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

"""The stop gate has two ways to be satisfied, and only one of them is a command.

A project once shipped as `verification_mode: execution` with an empty
`validation.commands`. That combination asks for nothing at all: the command
branch needs patterns to match against, and there were none. The project is pure
theory -- no build, no test, every required skill analytic -- so the honest
setting is `analysis_only`, where the gate demands an analytic verification that
states its own ceiling instead. These tests pin that branch, because the failure
mode it replaced was silence.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
HOOKS = ROOT / "claude-harness" / "scripts" / "hooks"
SPEC = importlib.util.spec_from_file_location("stop_gate", HOOKS / "stop_gate.py")
assert SPEC and SPEC.loader
G = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)


def _project(mode, commands=()):
    return ("example-theory-project", {
        "validation": {"commands": list(commands)},
        "environment": {"verification_mode": mode},
    })


class AnalysisOnlyEvidenceTests(unittest.TestCase):
    """An edit outside sessions/ plus a worklog: reason one is already settled,
    so whatever the gate says next is the evidence branch talking."""

    def _run(self, project, worklog_text):
        edit = {"ts": 1000.0, "session_id": "t", "tool": "Edit",
                "file_path": str(ROOT / "artifact.md")}
        worklog = {"ts": 1001.0, "session_id": "t", "tool": "Write",
                   "file_path": str(ROOT / "claude-harness" / "sessions" /
                                    "active" / "w.md")}
        with tempfile.TemporaryDirectory() as temp:
            note = Path(temp) / "w.md"
            note.write_text(worklog_text, encoding="utf-8")
            buffer = io.StringIO()
            with (
                mock.patch.object(G.H, "read_input",
                                  return_value={"session_id": "t"}),
                mock.patch.object(G.H, "read_audit",
                                  return_value=[edit, worklog]),
                mock.patch.object(G.H, "under_sessions",
                                  side_effect=lambda p: "sessions" in p),
                mock.patch.object(G.H, "active_project", return_value=project),
                mock.patch.object(G.H, "latest_session_file",
                                  return_value=str(note)),
                mock.patch.object(G.H, "log_event"),
                contextlib.redirect_stdout(buffer),
            ):
                G.main()
            out = buffer.getvalue().strip()
        return json.loads(out)["reason"] if out else None

    def test_analysis_only_without_a_ceiling_is_blocked(self):
        reason = self._run(_project("analysis_only"), "# worklog\nDid the thing.")
        self.assertIsNotNone(reason, "the gate stayed silent")
        self.assertIn("analysis-only", reason)
        self.assertIn("verification ceiling", reason)

    def test_analysis_only_with_a_ceiling_passes(self):
        reason = self._run(
            _project("analysis_only"),
            "# worklog\nProved the bound.\n\nVerification ceiling: not run — "
            "no executable artifact exists for this proof.")
        self.assertIsNone(reason, f"unexpected block: {reason}")

    def test_execution_with_no_commands_asks_for_nothing(self):
        """The shipped-and-dead configuration, pinned so the regression is
        recognisable if it comes back: a live gate must not look like this."""
        reason = self._run(_project("execution"), "# worklog\nDid the thing.")
        self.assertIsNone(reason)


if __name__ == "__main__":
    unittest.main()
