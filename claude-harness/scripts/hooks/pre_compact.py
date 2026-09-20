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

"""PreCompact hook — flush working memory before the context is summarized.

Compaction summarizes the context window: reasoning, decisions, and the file-map
held only in-context are lossy after it. This hook fires JUST BEFORE that and
injects a reminder to externalize the current working state to disk NOW — into
the active MISSION STATE block (or the latest session worklog) — so nothing
load-bearing is lost. It also logs a compaction-boundary event so a lost flush
is visible in the audit data. Deterministic backstop to the continuous-
externalization discipline (`protocols/long_loop.md`, `protocols/long_task.md`).
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _hooklib as H


def main():
    data = H.read_input()
    session_id = data.get("session_id", "")
    trigger = data.get("trigger", "auto")  # "auto" | "manual"
    hdir = H.hdir_name()

    latest = H.latest_session_file()
    target = None
    if latest:
        target = os.path.relpath(latest, data.get("cwd") or os.getcwd())

    H.log_event(session_id, "pre_compact_flush", trigger=trigger,
                worklog=bool(latest))

    msg = [f"[{hdir}] Context is about to be compacted ({trigger}). Before it is "
           "summarized away, write your current working state to disk NOW so it "
           "survives — this is the one moment in-context memory is lost."]
    if target:
        msg.append(
            f"Update the STATE block (DONE / ACCEPTED / OPEN / FILE-MAP / NEXT) "
            f"in {target}, keeping it compact, and append a LEDGER line. A fresh "
            "session must be able to resume from that file alone "
            "(protocols/long_loop.md).")
    else:
        msg.append(
            f"Write a session worklog under {hdir}/sessions/ capturing current "
            "state, decisions, the key file-map, and the single next action "
            "(protocols/long_task.md).")
    print("\n".join(msg))
    return 0


if __name__ == "__main__":
    raise SystemExit(H.safe(main))
