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

"""Scaffold the end-of-session distillation review (modes/memory.md).

This does NOT decide what to persist — that judgment is the model's, run under
the persistence guard in modes/memory.md. What it does is assemble the *evidence*
(what this session actually touched, from the audit log) and print the review
questions against it, so the distillation is grounded in what happened rather
than in what the model remembers happening.

Self-improvement-loop design (adapted from a self-improving-agent reference):
the review has a deliberately narrow write surface — it may only produce memory
items (memory/) and skill patches (skills/), via the action ladder — and a hard
guard on what must NOT be persisted.

Usage:
    python3 scripts/distill_session.py [--session-id ID] [--latest]

With no args it summarizes the most recent session's audit entries. Output is a
prompt for the model to act on, plus the raw evidence.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "hooks"))
import _hooklib as H  # noqa: E402

REVIEW = """\
## Distillation review — modes/memory.md

Run the review against the evidence below. Write to disk only via the two
allowed surfaces (memory/ items, skills/ patches), and only after the guard
passes. "Nothing worth persisting" is a valid, common outcome — say it.

1. Did a REUSABLE PATTERN appear this session (a way of working worth repeating)?
2. Is something worth persisting as MEMORY (a decision + why, project state, a
   sharpened claim/definition, a live constraint)?  → memory/{decisions,
   project_states,patterns}/ + index in memory/MEMORY.md.
3. Should an EXISTING SKILL be patched? (Most "how I work" changes patch a skill,
   not create one.)
4. Is it general enough to be a NEW SKILL? (Rare.)

Action ladder (prevents sprawl): patch loaded skill → patch umbrella skill →
add a support file → only then create a new skill.

PERSISTENCE GUARD — do NOT write as a durable rule:
  - an environment-specific or transient failure;
  - a one-off error or accidental workaround;
  - an over-narrow single incident dressed as a general rule;
  - a NEGATIVE SELF-CAPABILITY claim ("X can't do Y") — most dangerous; record
    the specific error + condition, never a blanket verdict.
Persist the fix / missing config / class-level rule instead. Prefer
supersede/archive over delete. Mark each item's true epistemic status.
"""


def _summarize(entries):
    edits, bash, events = [], [], []
    for e in entries:
        if H.is_file_edit(e):
            edits.append(e.get("file_path", ""))
        elif H.is_bash(e):
            bash.append(e.get("command", ""))
        elif H.is_event(e):
            events.append(e.get("event", ""))
    return edits, bash, events


def _evidence(session_id, edits, bash, latest):
    lines = ["## Evidence (audit log)", "",
             f"session_id: {session_id or '(none found)'}"]
    if latest:
        lines.append(f"latest worklog: {os.path.relpath(latest, H.harness_root())}")
    uniq = sorted(set(p for p in edits if p))
    lines.append(f"\nfiles modified ({len(uniq)}):")
    for p in uniq:
        try:
            lines.append(f"  - {os.path.relpath(p, H.harness_root())}")
        except ValueError:
            lines.append(f"  - {p}")
    lines.append(f"\ncommands run ({len(bash)}):")
    lines += [f"  - {c}" for c in bash[-20:]]
    return "\n".join(lines)


def _auto_prompt(evidence, proposal_abs, memory_abs, apply, work_cwd):
    where = (
        f"APPLY MODE: you MAY create/update memory items under `{memory_abs}/` "
        f"(frontmatter per its README) and update `{memory_abs}/MEMORY.md`. Propose "
        f"any SKILL changes as text in `{proposal_abs}` — never edit skills/ "
        "directly."
        if apply else
        f"PROPOSAL MODE (default, dry-run): write ALL conclusions — proposed memory "
        f"items AND proposed skill patches — as text into `{proposal_abs}` ONLY. Do "
        "not modify memory/ or skills/."
    )
    return (
        REVIEW + "\n\n" + evidence + "\n\n## Your task\n"
        f"Work happened in: {work_cwd}\n"
        f"{where}\n"
        "A sandbox is enforced: you may only write under memory/ and "
        "sessions/distilled/ (edits elsewhere are denied). Apply the persistence "
        "guard and the action ladder strictly. If nothing is worth persisting, "
        f"write a one-line 'nothing to persist' note to `{proposal_abs}` and stop. "
        "End by stating exactly what you wrote."
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description="Distillation review (scaffold or auto).")
    ap.add_argument("--session-id", default="", help="Audit session id to review.")
    ap.add_argument("--latest", action="store_true",
                    help="Review the most recent session id in the audit log.")
    ap.add_argument("--auto", action="store_true",
                    help="Spawn a sandboxed `claude -p` to run the review and write "
                         "results, instead of just printing the prompt.")
    ap.add_argument("--apply", action="store_true",
                    help="With --auto: allow landing memory items in memory/ "
                         "(skill patches stay proposals). Default: proposal-only.")
    ap.add_argument("--cwd", default=None, help="Where the reviewed work happened "
                    "(context only).")
    ap.add_argument("--date", default=None, help="Proposal date stamp YYYY-MM-DD "
                    "(defaults to today).")
    args = ap.parse_args(argv)

    session_id = args.session_id or None
    if not session_id:
        ids = [e.get("session_id") for e in H.read_audit() if e.get("session_id")]
        session_id = ids[-1] if ids else None

    entries = H.read_audit(session_id)
    edits, bash, _ = _summarize(entries)
    latest = H.latest_session_file()
    evidence = _evidence(session_id, edits, bash, latest)

    if not args.auto:
        print(REVIEW + "\n\n" + evidence)
        if not entries:
            print("\n(no audit entries — nothing to distill from this session)")
        return 0

    # --auto: spawn a sandboxed reviewer.
    import datetime
    date = args.date or datetime.date.today().isoformat()
    distilled = os.path.join(H.harness_root(), "sessions", "distilled")
    os.makedirs(distilled, exist_ok=True)
    proposal = os.path.join(distilled, f"{date}_distill.md")
    memory_abs = os.path.join(H.harness_root(), "memory")
    # The bridge (CLAUDE.md + .claude/settings.json wiring the hooks) lives at the
    # harness's parent — launch there so the distill sandbox hook actually fires.
    bridge_root = os.path.abspath(os.path.join(H.harness_root(), ".."))
    prompt = _auto_prompt(evidence, proposal, memory_abs, args.apply,
                          args.cwd or "(unspecified)")

    env = dict(os.environ, HARNESS_DISTILL="1")
    cmd = ["claude", "-p", prompt, "--permission-mode", "acceptEdits"]
    mode = "APPLY (memory writes allowed)" if args.apply else "PROPOSAL (dry-run)"
    print(f"[distill] auto review — {mode}; sandbox=memory/+sessions/distilled/")
    print(f"[distill] proposal/output: {os.path.relpath(proposal, H.harness_root())}")
    try:
        r = subprocess.run(cmd, cwd=bridge_root, env=env, timeout=1800,
                           capture_output=True, text=True)
    except subprocess.TimeoutExpired:
        print("[distill] timed out.")
        return 1
    except FileNotFoundError:
        print("[distill] `claude` CLI not found; cannot run --auto.")
        return 1
    out = (r.stdout or r.stderr or "").strip()
    print(out[-1500:] if out else "[distill] (no output)")
    print(f"[distill] exit={r.returncode}. Review {os.path.relpath(proposal, H.harness_root())}"
          + ("" if args.apply else " and approve before applying (run with --apply, "
             "or land the memory items by hand)."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
