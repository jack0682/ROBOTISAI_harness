#!/usr/bin/env python3
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

"""PostToolUse hook (matcher: Edit|Write|MultiEdit|NotebookEdit|Bash|Skill).

File modifications, Bash commands and skill invocations are appended to
sessions/.audit.log — the evidence stream the stop gate and audit_session.py
read. Bash commands are what later proves (or disproves) that validation
actually ran.

Skill invocations are recorded because the library cannot be curated without
them. The measured failure mode of a growing skill library is *selection*
(a near-duplicate description hiding the right skill), not context size, and
selection can only be seen in which skill actually fired for which task.

Context injection stays low-noise: one reminder on the first file edit of a
session, plus one when the first edit *outside the harness repo* happens in
a project whose config gates edits behind a plan.
"""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _hooklib as H

MAX_COMMAND_CHARS = 2000


def _succeeded(data):
    """True / False / None for the Bash call this hook is reporting on.

    None means the runtime told us nothing we can read. It is deliberately not
    False: a gate that blocks on every unrecognised response shape is a gate
    that gets switched off. A *known* failure is what stops counting as evidence.
    """
    response = data.get("tool_response")
    if not isinstance(response, dict):
        return None
    if response.get("interrupted") is True:
        return False
    for key in ("is_error", "isError", "error"):
        if key in response:
            return not bool(response[key])
    for key in ("exit_code", "exitCode", "returncode"):
        value = response.get(key)
        if isinstance(value, int):
            return value == 0
    return None


def main():
    data = H.read_input()
    session_id = data.get("session_id", "")
    tool = data.get("tool_name", "")

    if tool == "Bash":
        command = (data.get("tool_input") or {}).get("command", "")
        H.append_audit({"ts": time.time(), "session_id": session_id,
                        "tool": "Bash", "command": command[:MAX_COMMAND_CHARS],
                        # Whether it worked, not just that it ran. Without this
                        # the stop gate accepted a failing test suite as proof
                        # the change was validated.
                        "ok": _succeeded(data)})
        return 0

    if tool == "Skill":
        name = H.skill_name(data.get("tool_input"))
        # An unreadable input shape is logged with skill "" on purpose: a gap in
        # the telemetry must show up as a gap, not vanish.
        H.append_audit({"ts": time.time(), "session_id": session_id,
                        "tool": "Skill", "skill": name})
        return 0

    path = H.edited_path(data.get("tool_input"))
    prior = [e for e in H.read_audit(session_id) if H.is_file_edit(e)]
    H.append_audit({"ts": time.time(), "session_id": session_id,
                    "tool": tool, "file_path": path})

    hdir = H.hdir_name()
    notes = []
    if not prior:
        notes.append(
            f"[{hdir}] First file modification of this session recorded "
            f"(audit: {hdir}/sessions/.audit.log). After each change apply "
            f"{hdir}/protocols/validation.md; before ending the session, "
            f"write or update a checkpoint in {hdir}/sessions/ "
            "(kernel/execution_protocol.md) — the stop gate checks for it.")

    if path and not H.under_harness(path):
        first_ws = not any(not H.under_harness(e["file_path"]) for e in prior)
        if first_ws:
            proj = H.active_project()
            if proj and (proj[1].get("constraints") or {}).get(
                    "require_plan_before_edit"):
                notes.append(
                    f"[{hdir}] First workspace edit. Project '{proj[0]}' gate: "
                    "require_plan_before_edit — an approved plan "
                    "(protocols/planning.md) must exist before workspace "
                    "changes. If none does, stop and plan first.")

    if notes:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": "\n".join(notes)}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(H.safe(main))
