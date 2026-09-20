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

"""The skill library cannot be curated without knowing which skill fired.

The measured failure mode of a growing skill library is *selection* -- a
near-duplicate description hiding the right skill -- and it accounts for most of
the degradation, while the context cost of the extra descriptions does not.
Selection is invisible in this harness today: `sessions/.audit.log` records file
edits and Bash commands, and nothing at all about skills. These tests pin the
instrumentation that closes that gap, and the rule that keeps it honest -- a
session the gate never evaluated contributes no outcome either way.
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
HOOKS = ROOT / "claude-harness" / "scripts" / "hooks"

sys.path.insert(0, str(HOOKS))
_SPEC = importlib.util.spec_from_file_location("_hooklib", HOOKS / "_hooklib.py")
assert _SPEC and _SPEC.loader
H = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(H)


def _run(hook, payload, audit_log):
    return subprocess.run(
        [sys.executable, str(HOOKS / hook)],
        input=json.dumps(payload), capture_output=True, text=True,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(ROOT),
             "HARNESS_AUDIT_LOG": audit_log},
    )


def _entries(audit_log):
    if not os.path.isfile(audit_log):
        return []
    with open(audit_log, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


class SkillNameTests(unittest.TestCase):
    """The Skill tool's input shape is not documented, so the reader is
    deliberately tolerant -- and returns "" rather than a guess."""

    def test_it_reads_the_documented_shape(self):
        self.assertEqual("proof-checker",
                         H.skill_name({"skill": "proof-checker", "args": "x"}))

    def test_it_accepts_the_other_plausible_keys(self):
        for key in ("skill_name", "name", "skillName"):
            with self.subTest(key=key):
                self.assertEqual("arxiv", H.skill_name({key: "arxiv"}))

    def test_an_unrecognised_shape_yields_empty_not_a_guess(self):
        for value in ({}, None, {"unrelated": "x"}, {"skill": "  "}, "a string"):
            with self.subTest(value=value):
                self.assertEqual("", H.skill_name(value))

    def test_a_skill_entry_is_not_a_file_edit(self):
        entry = {"tool": "Skill", "skill": "arxiv"}
        self.assertTrue(H.is_skill_use(entry))
        self.assertFalse(H.is_file_edit(entry))

    def test_an_unnamed_skill_use_is_not_counted(self):
        """Logged so the gap is visible, but not counted as an invocation."""
        self.assertFalse(H.is_skill_use({"tool": "Skill", "skill": ""}))


class SkillRecordingTests(unittest.TestCase):
    def test_post_edit_records_the_skill_that_ran(self):
        with tempfile.TemporaryDirectory() as temp:
            log = os.path.join(temp, "audit.log")
            _run("post_edit.py", {
                "session_id": "t", "tool_name": "Skill",
                "tool_input": {"skill": "kill-argument", "args": ""},
            }, log)
            rows = [e for e in _entries(log) if H.is_skill_use(e)]
            self.assertEqual(1, len(rows), _entries(log))
            self.assertEqual("kill-argument", rows[0]["skill"])

    def test_a_skill_call_writes_no_file_edit_row(self):
        with tempfile.TemporaryDirectory() as temp:
            log = os.path.join(temp, "audit.log")
            _run("post_edit.py", {
                "session_id": "t", "tool_name": "Skill",
                "tool_input": {"skill": "arxiv"},
            }, log)
            self.assertEqual([], [e for e in _entries(log) if H.is_file_edit(e)])


class SessionOutcomeTests(unittest.TestCase):
    """`ĉ(s) = (successes − failures) / trials` is only as good as what counts
    as a trial."""

    def _session(self, temp, log, edit_outside_sessions):
        artifact = os.path.join(temp, "artifact.md")
        Path(artifact).write_text("x", encoding="utf-8")
        _run("post_edit.py", {
            "session_id": "t", "tool_name": "Skill",
            "tool_input": {"skill": "proof-checker"},
        }, log)
        if edit_outside_sessions:
            _run("post_edit.py", {
                "session_id": "t", "tool_name": "Edit",
                "tool_input": {"file_path": artifact},
            }, log)
        _run("stop_gate.py", {"session_id": "t", "stop_hook_active": False}, log)
        return [e for e in _entries(log)
                if e.get("event") == "session_outcome"]

    def test_an_evaluated_session_attributes_its_verdict_to_the_skills(self):
        with tempfile.TemporaryDirectory() as temp:
            log = os.path.join(temp, "audit.log")
            outcomes = self._session(temp, log, edit_outside_sessions=True)
            self.assertEqual(1, len(outcomes), outcomes)
            detail = outcomes[0]["detail"]
            self.assertEqual(["proof-checker"], detail["skills"])
            self.assertIn(detail["verdict"], ("pass", "blocked"))

    def test_a_session_the_gate_never_evaluated_records_no_outcome(self):
        """No edits outside sessions/ means no verifiable result. Counting it as
        a pass would inflate every skill that happened to be open."""
        with tempfile.TemporaryDirectory() as temp:
            log = os.path.join(temp, "audit.log")
            self.assertEqual([], self._session(temp, log,
                                               edit_outside_sessions=False))


if __name__ == "__main__":
    unittest.main()
