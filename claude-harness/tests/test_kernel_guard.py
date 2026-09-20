# Copyright 2026 ROBOTIS AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Jaehong Oh <jaehongoh1554@gmail.com>

"""kernel_guard had no tests, and `_hooklib.safe()` fails open.

Those two facts compound: a crash in the guard is swallowed and the tool call is
permitted, so a broken guard is indistinguishable from a permissive one. This
was not hypothetical — an edit in this session left `_distilling()` called and
never defined, and the only symptom was that nothing was ever denied.

These drive the hook as a subprocess, the way Claude Code does, so a NameError
shows up as a failing test instead of as silence.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
_AUDIT_LOG = str(Path(tempfile.gettempdir()) /
                  f"harness-test-audit-{os.getpid()}.log")
GUARD = ROOT / "claude-harness" / "scripts" / "hooks" / "kernel_guard.py"

_SPEC = importlib.util.spec_from_file_location("kernel_guard", GUARD)
assert _SPEC and _SPEC.loader
KG = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(KG)


def run_guard(tool_input, tool="Write", env=None):
    payload = json.dumps({
        "hook_event_name": "PreToolUse",
        "tool_name": tool,
        "tool_input": tool_input,
        "cwd": str(ROOT),
        "session_id": "test",
    })
    result = subprocess.run(
        [sys.executable, str(GUARD)], input=payload, capture_output=True, text=True,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(ROOT),
             "HARNESS_AUDIT_LOG": _AUDIT_LOG, **(env or {})},
    )
    decision = ""
    if result.stdout.strip():
        try:
            body = json.loads(result.stdout)
            decision = (body.get("hookSpecificOutput") or {}).get(
                "permissionDecision", "")
        except ValueError:
            decision = ""
    return decision, result


class DeletionDetectorTests(unittest.TestCase):
    """The gate asks before a destructive command; it missed ten of twelve shapes.

    A single anchored pattern (`(?:^|[;&|]\\s*|sudo )(rm|rmdir|unlink|shred)\\s`)
    could not see a leading space, a newline, a loop body, `find -delete`,
    `xargs rm`, `git clean`, or a Python one-liner. Neither the leading space nor
    the newline is exotic.

    This is a confirmation gate, not a security boundary. Anything reaching a
    shell can still delete anything the user can; the point is that the ordinary
    shapes stop being silent.
    """

    DESTRUCTIVE = [
        "rm -rf /important",
        "cd /x && rm -rf y",
        "  rm -rf /important",                       # leading whitespace
        "echo hi\nrm -rf /important",                # newline, no re.M before
        "for f in *; do rm $f; done",                # hidden behind `do`
        "find . -name '*.md' -delete",
        "find . -exec rm {} +",
        "ls | xargs rm -rf",
        "git clean -fdx",
        'python3 -c "import shutil; shutil.rmtree(\'/x\')"',
        "truncate -s 0 important.md",
        "mv important.md /dev/null",
        "sudo rm -rf /x",
        "FOO=1 rm -rf /x",                           # env-var prefix
        "nohup rm -rf /x",
    ]

    BENIGN = [
        "ls -la",
        "git status",
        "echo 'rm -rf is dangerous'",                # the word, not the command
        "grep -r rm .",
        "python3 -m pytest",
        "cat firmware.md",
        "npm run build",
        "git log --oneline",
        "mkdir -p build",
        "cp a.md b.md",
        "git clean --dry-run",                       # -n only: shows, removes nothing
    ]

    def test_destructive_shapes_are_caught(self):
        for command in self.DESTRUCTIVE:
            with self.subTest(command=command):
                self.assertTrue(KG._is_destructive(command))

    def test_ordinary_commands_do_not_fire(self):
        """A gate that asks about `ls` is a gate people learn to click through."""
        for command in self.BENIGN:
            with self.subTest(command=command):
                self.assertFalse(KG._is_destructive(command))

    def test_deleting_under_tmp_is_not_flagged(self):
        self.assertFalse(KG._deletion_outside_tmp("rm -rf /tmp/scratch"))
        self.assertTrue(KG._deletion_outside_tmp("rm -rf /tmp/../etc"))


class VerificationCeilingTests(unittest.TestCase):
    """An environment that cannot run the thing being judged.

    The verification machinery assumed execution was always possible, leaving a
    false binary: demand evidence that cannot exist, or let unverified work pass
    as fine. In practice it collapsed to the second
    (`claude-harness/docs/testbed_findings.md`, finding F1).
    """

    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "stop_gate", ROOT / "claude-harness" / "scripts" / "hooks" / "stop_gate.py")
        self.sg = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.sg)

    def _worklog(self, body):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        path = Path(self._tmp.name) / "worklog.md"
        path.write_text(body, encoding="utf-8")
        self.sg.H.latest_session_file = lambda: str(path)
        return path

    def test_a_checkpoint_stating_its_ceiling_satisfies_the_gate(self):
        self._worklog("## Checkpoint\nVerification ceiling: static read plus a "
                      "closed-loop argument; not hardware-validated.\n")
        self.assertTrue(self.sg._states_verification_ceiling([], 0, "claude-harness"))

    def test_a_checkpoint_that_claims_completion_does_not(self):
        """"All done" in an environment that cannot run anything is the exact
        failure this replaces."""
        self._worklog("## Checkpoint\nAll done, everything works.\n")
        self.assertFalse(self.sg._states_verification_ceiling([], 0, "claude-harness"))

    def test_no_worklog_at_all_does_not(self):
        self.sg.H.latest_session_file = lambda: None
        self.assertFalse(self.sg._states_verification_ceiling([], 0, "claude-harness"))

    def test_every_marker_is_recognised(self):
        for marker in self.sg._CEILING_MARKERS:
            with self.subTest(marker=marker):
                self._worklog(f"## Checkpoint\nThe {marker} is as follows.\n")
                self.assertTrue(
                    self.sg._states_verification_ceiling([], 0, "claude-harness"))


class DistillSandboxTests(unittest.TestCase):
    def test_a_write_outside_the_sandbox_is_denied(self):
        for var in ("HARNESS_DISTILL", "CLAUDE_HARNESS_DISTILL"):
            with self.subTest(variable=var):
                decision, _ = run_guard(
                    {"file_path": "claude-harness/KERNEL.md"}, env={var: "1"})
                self.assertEqual("deny", decision)

    def test_a_write_inside_the_sandbox_is_allowed(self):
        decision, _ = run_guard({"file_path": "claude-harness/memory/note.md"},
                                env={"HARNESS_DISTILL": "1"})
        self.assertNotEqual("deny", decision)

    def test_an_unresolvable_target_is_denied_not_waved_through(self):
        """Fail-closed on ambiguity: an edit that cannot be proven inside the
        allowed surface must not slip through it."""
        decision, _ = run_guard({}, env={"HARNESS_DISTILL": "1"})
        self.assertEqual("deny", decision)

    def test_the_sandbox_is_off_when_not_distilling(self):
        decision, _ = run_guard({"file_path": "claude-harness/KERNEL.md"})
        self.assertNotEqual("deny", decision)

    def test_the_guard_does_not_crash(self):
        """`safe()` turns a crash into an allow, so a broken guard reads exactly
        like a permissive one. Assert on stderr, which the wrapper cannot hide."""
        for env in ({}, {"HARNESS_DISTILL": "1"}):
            with self.subTest(env=env or "no distill"):
                _, result = run_guard({"file_path": "x.md"}, env=env)
                self.assertNotIn("Traceback", result.stderr)
                self.assertNotIn("NameError", result.stderr)


if __name__ == "__main__":
    unittest.main()
