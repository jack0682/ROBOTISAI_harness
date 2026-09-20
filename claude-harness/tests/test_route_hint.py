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

"""`route_hint` runs on every user prompt and had no tests.

Six regexes, fired before anything else the harness does, deciding which scope
gets surfaced. A scope added to `scopes/`, `registry/scopes.yaml`, `ROUTING.md`
and the golden set can still be invisible here — which is exactly what happened
to `control`: everything documented it and the hook could never surface it.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
_AUDIT_LOG = str(Path(tempfile.gettempdir()) /
                  f"harness-test-audit-{os.getpid()}.log")
HARNESS = ROOT / "claude-harness"
HOOK = HARNESS / "scripts" / "hooks" / "route_hint.py"

sys.path.insert(0, str(HARNESS / "scripts"))
import _common as C  # noqa: E402

_SPEC = importlib.util.spec_from_file_location("route_hint", HOOK)
RH = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(RH)


def run_hook(prompt):
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps({"hook_event_name": "UserPromptSubmit",
                          "prompt": prompt, "session_id": "test"}),
        capture_output=True, text=True,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(ROOT),
             "HARNESS_AUDIT_LOG": _AUDIT_LOG},
    )
    return result


class RouteTableTests(unittest.TestCase):
    def test_every_route_names_a_registered_scope(self):
        registered = {s["name"] for s in C.load_registry("scopes").get("scopes", [])}
        for scope, _, _, _ in RH.ROUTES:
            with self.subTest(scope=scope):
                self.assertIn(scope, registered)

    def test_every_registered_scope_is_reachable(self):
        """A scope the hook cannot surface is documented, not routed."""
        registered = {s["name"] for s in C.load_registry("scopes").get("scopes", [])}
        routed = {scope for scope, _, _, _ in RH.ROUTES}
        self.assertEqual(set(), registered - routed)

    def test_every_pattern_compiles(self):
        for scope, pattern, _, _ in RH.ROUTES:
            with self.subTest(scope=scope):
                re.compile(pattern)

    def test_every_route_names_modes_that_exist(self):
        modes = {m["name"] for m in C.load_registry("modes").get("modes", [])}
        for scope, _, mode_list, _ in RH.ROUTES:
            for mode in [m.strip() for m in mode_list.split(",")]:
                with self.subTest(scope=scope, mode=mode):
                    self.assertIn(mode, modes)


class HookBehaviourTests(unittest.TestCase):
    def test_an_empty_prompt_produces_no_hint(self):
        for prompt in ("", "   ", "\n"):
            with self.subTest(prompt=repr(prompt)):
                self.assertEqual("", run_hook(prompt).stdout.strip())

    def test_a_prompt_matching_nothing_produces_no_hint(self):
        """Noise on every prompt is how a hint gets ignored."""
        self.assertEqual("", run_hook("오늘 날씨 어때").stdout.strip())

    def test_a_matching_prompt_names_its_scope_and_file(self):
        out = run_hook("이 증명에서 식별성이 성립하는지 봐줘").stdout
        self.assertIn("math", out)
        self.assertIn("scopes/math/AGENTS.md", out)

    def test_at_most_two_scopes_are_surfaced(self):
        """More than two matches is noise, not a signal."""
        crowded = ("이 코드의 버그를 고치고 실험 결과를 분석해서 논문 초록을 쓰고 "
                   "증명도 확인하고 선행연구도 찾아줘")
        self.assertGreater(len(RH.ROUTES), 2)
        hinted = [line for line in run_hook(crowded).stdout.splitlines()
                  if line.strip().startswith("·")]
        self.assertLessEqual(len(hinted), 2)

    def test_the_hook_does_not_crash(self):
        """`safe()` turns a crash into silence, and silence is also what a
        no-match looks like."""
        for prompt in ("", "증명", "x" * 5000, "```\n{}\n```", "🙂"):
            with self.subTest(prompt=prompt[:20]):
                result = run_hook(prompt)
                self.assertEqual(0, result.returncode)
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
