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

"""SessionStart hook (matcher: startup|resume|compact).

stdout on exit 0 is injected into the session context by the runtime, so the
latest worklog's Next Step and most recent checkpoint reach the model
mechanically — no reliance on the model remembering to read sessions/. It also
re-injects the *unsettled* claims (open / stale) from memory/claims/, so a
fresh or post-compaction context cannot silently treat a not-yet-earned or
expired claim as established. On `compact`, also restates the checkpoint
obligation that compaction would otherwise erode. Every run logs a
self-instrumentation event so a silently failed injection (no worklog,
unparseable checkpoint) shows up in the data.
"""

from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _hooklib as H

sys.path.insert(0, os.path.join(H.harness_root(), "scripts"))
import _claims
import work_graph

MAX_SECTION_LINES = 30


def _trim(text):
    lines = text.splitlines()
    if len(lines) > MAX_SECTION_LINES:
        lines = lines[:MAX_SECTION_LINES] + ["[... trimmed]"]
    return "\n".join(lines)


def _unsettled_claims():
    """Surface the claims that are NOT established — open (under construction)
    and stale (settled but past their review_at expiry) — so a fresh session or
    a post-compaction context does not silently treat them as fact
    (memory/claims/README.md). Returns "" when nothing is unsettled."""
    base = os.path.join(H.harness_root(), "memory", "claims")
    if not os.path.isdir(base):
        return ""
    open_c, stale_c, contra_c = [], [], []
    for fn in sorted(os.listdir(base)):
        if (not fn.endswith(".md") or fn.startswith("_")
                or fn in ("README.md", "MEMORY.md")):
            continue
        try:
            with open(os.path.join(base, fn), "r", encoding="utf-8") as fh:
                fm = _claims.parse_frontmatter(fh.read())
        except Exception:
            continue
        if not _claims.is_claim(fm):
            continue
        name = fm.get("name") or fn[:-3]
        # A contradiction outranks the other two: staleness says "this may have
        # decayed", a contradiction says "something on record disputes this".
        if _claims.is_contradicted(fm):
            contra_c.append(f"{name} (by {', '.join(_claims.contradictions(fm))})")
        elif _claims.is_stale(fm):
            stale_c.append(name)
        elif (fm.get("status") or "").strip().lower() == "open":
            open_c.append(name)
    parts = []
    if contra_c:
        parts.append("  CONTRADICTED (something on record disputes these — "
                     "resolve before citing): " + "; ".join(contra_c[:10]))
    if stale_c:
        parts.append("  STALE (settled but expired — re-verify before relying "
                     "on these): " + ", ".join(stale_c[:10]))
    if open_c:
        parts.append("  OPEN (not yet earned — still under construction): "
                     + ", ".join(open_c[:10]))
    if not parts:
        return ""
    return (f"[{H.hdir_name()}] Unsettled claims in memory/claims/ — do NOT "
            "treat as established:\n" + "\n".join(parts))


def _project_work():
    """For the active project, surface the work-state dependency graph: what is
    ready (no open blockers), what is blocked, and any graph problems — so a
    fresh session starts on a workable item instead of re-deriving the queue
    (scripts/work_graph.py). Returns "" when there is no active project / no
    items."""
    pdir = H.active_project_dir()
    if not pdir:
        return ""
    items = work_graph.load_items(os.path.join(pdir, "memory"))
    if not items:
        return ""
    a = work_graph.analyze(items)
    lines = []
    if a["ready"]:
        lines.append("  READY (no open blockers): " + ", ".join(a["ready"][:15]))
    if a["blocked"]:
        b = "; ".join(f"{i}←{','.join(d)}"
                      for i, d in list(a["blocked"].items())[:10])
        lines.append("  BLOCKED: " + b)
    probs = [f"{s} superseded by {by} (retire)" for s, by in a["superseded_open"]]
    probs += [f"{src} {kind}→{dep} missing" for src, kind, dep in a["dangling"]]
    probs += ["cycle " + "→".join(c) for c in a["cycles"]]
    if probs:
        lines.append("  ⚠ graph: " + "; ".join(probs[:8]))
    if not lines:
        return ""
    return (f"[{H.hdir_name()}] Project work graph "
            "(open_questions/known_issues):\n" + "\n".join(lines))


def _autonomy_mandate():
    """Inject the standing autonomy mandate every session so it is enforced
    mechanically, not by relying on the model to read kernel/autonomy_mandate.md.
    Extracts the compact block between the INJECT markers. Fail-open: returns ""
    if the file or its markers are absent."""
    path = os.path.join(H.harness_root(), "kernel", "autonomy_mandate.md")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except Exception:
        return ""
    m = re.search(r"<!-- INJECT:START -->(.*?)<!-- INJECT:END -->", text, re.S)
    if not m:
        return ""
    body = m.group(1).strip()
    return f"[{H.hdir_name()}] {body}" if body else ""


def _first_run_notice(hdir):
    """The harness was just dropped into this workspace and nothing knows it yet.

    `bootstrap.sh` leaves `.bootstrap-pending`. Until `/harness-init` clears it,
    every session opens by saying what has not happened: the workspace has not
    been read, and no project overlay governs it. Without this the first session
    starts work against a harness that is technically in force and factually
    ignorant of the repository around it.

    It also states the git posture once, so no session spends tokens finding out
    the hard way that the template remote is gone on purpose.
    """
    marker = os.path.join(H.harness_root(), ".bootstrap-pending")
    if not os.path.isfile(marker):
        return ""
    return (
        f"[{hdir}] FIRST RUN — this workspace has not been analyzed yet.\n"
        "Before any other work, run `/harness-init`: read the workspace as a "
        "whole (what it is, its build/test entry points, its languages, its "
        "existing conventions), register the project overlay, and record what "
        "you found. Work done before that is work done blind.\n"
        "The harness's own upstream remote was removed by bootstrap on purpose "
        "— this copy is standalone and cannot push there, so do not try. Send "
        "harness improvements to the upstream repository directly.\n"
        f"Clear this notice by deleting `{hdir}/.bootstrap-pending` once "
        "`/harness-init` has completed.")


def main():
    data = H.read_input()
    source = data.get("source", "startup")
    session_id = data.get("session_id", "")
    hdir = H.hdir_name()
    out = []

    mandate = _autonomy_mandate()
    if mandate:
        out.append(mandate)

    bootstrap = _first_run_notice(hdir)
    if bootstrap:
        out.append(bootstrap)

    if source == "compact":
        out.append(
            f"[{hdir}] Context was just compacted. The kernel rules imported via "
            "CLAUDE.md remain fully in force. Re-verify your current state against "
            "the latest checkpoint below before continuing, and write a fresh "
            f"checkpoint to {hdir}/sessions/ before further risky edits "
            "(kernel/execution_protocol.md).")

    latest = H.latest_session_file()
    next_step = checkpoint = None
    if latest:
        with open(latest, "r", encoding="utf-8") as fh:
            text = fh.read()
        rel = os.path.relpath(latest, data.get("cwd") or os.getcwd())
        out.append(f"[{hdir}] Latest session worklog: {rel}")
        # A mission/loop worklog carries a compact STATE block that is the
        # durable context memory — reload it in full so a fresh session resumes
        # without re-exploring (protocols/long_loop.md).
        state = H.extract_section(text, "## STATE")
        if state:
            out.append("Mission STATE (durable context memory — resume from this):\n"
                       + _trim(state))
        next_step = H.extract_section(text, "## Next Step")
        if next_step:
            out.append("Next Step (from the worklog):\n" + _trim(next_step))
        checkpoint = H.last_checkpoint(text)
        unresolved = checkpoint and "continue or stop: stop" not in checkpoint.lower()
        if checkpoint and (unresolved or source == "compact"):
            out.append("Latest checkpoint:\n" + _trim(checkpoint))

    claims_note = _unsettled_claims()
    if claims_note:
        out.append(claims_note)

    work_note = _project_work()
    if work_note:
        out.append(work_note)

    H.log_event(session_id, "session_start_inject", source=source,
                autonomy=bool(mandate), worklog=bool(latest),
                next_step=bool(next_step), checkpoint=bool(checkpoint),
                unsettled_claims=bool(claims_note), work_graph=bool(work_note))
    if out:
        print("\n\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(H.safe(main))
