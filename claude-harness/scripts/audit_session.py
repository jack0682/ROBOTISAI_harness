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

"""Compliance instrumentation: cross-check the hook audit log against sessions/.

The hook layer appends three kinds of JSONL entries to sessions/.audit.log:
file edits, Bash commands, and hook self-instrumentation events. This report
groups them by session and applies the same evidence rules as the stop gate
(audit-log only — no filesystem-mtime heuristics):

  checkpoint   — the session wrote/updated a sessions/*.md at/after its first
                 non-sessions/ edit
  validation   — when the active project declares `validation.commands`, a
                 matching audited Bash command ran at/after the first edit

It also surfaces what the hook layer itself did: stop-gate blocks, guard
asks, and session-start injections that found no checkpoint to inject.

`--library` reports on the skill library instead: which skills actually fire,
what the gate said about the sessions they were used in, and how often any skill
fires at all.

Usage:
    python3 scripts/audit_session.py
    python3 scripts/audit_session.py --library
"""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "hooks"))
import _hooklib as H

SLACK_SECONDS = 60

# Outcome-driven retirement waits for evidence. Acting on a thin sample is not a
# smaller version of curation, it is a different and worse thing: in the study
# this threshold comes from, retiring at n=20 with a zero tolerance made the
# library *worse* than leaving it alone and collapsed it to two skills. Below
# N_MIN this report prints the sample size and withholds the verdict.
N_MIN = 100
# Fraction of evaluated sessions in which any skill fires. A healthy library sits
# around 0.70–0.80; a drifted one was measured at 0.19.
ENGAGEMENT_FLOOR = 0.70


def library_stats(entries=None):
    """Per-skill trials and contribution, plus router engagement.

    A *trial* is a session the stop gate actually evaluated: it had edits
    outside sessions/, so there was a real result to judge. Sessions with no
    such edits produce no outcome and are not counted either way — treating
    them as passes would inflate every skill that happened to be loaded.
    """
    entries = H.read_audit() if entries is None else entries
    outcomes = [e for e in entries if e.get("event") == "session_outcome"]
    per_skill = {}
    engaged = 0
    for e in outcomes:
        detail = e.get("detail") or {}
        skills = [s for s in (detail.get("skills") or []) if s]
        if skills:
            engaged += 1
        passed = detail.get("verdict") == "pass"
        for name in skills:
            row = per_skill.setdefault(name, {"trials": 0, "pass": 0, "blocked": 0})
            row["trials"] += 1
            row["pass" if passed else "blocked"] += 1
    for row in per_skill.values():
        row["contribution"] = (
            (row["pass"] - row["blocked"]) / row["trials"] if row["trials"] else 0.0)
        row["sufficient"] = row["trials"] >= N_MIN
    return {
        "evaluated": len(outcomes),
        "engaged": engaged,
        "engagement": (engaged / len(outcomes)) if outcomes else None,
        "skills": per_skill,
    }


def _user_invoked_only(name):
    """True when a skill opts out of model invocation entirely.

    Such a skill is invisible to the router until the user types its name, so it
    needs no trigger phrase and cannot shadow anything. Counting it as a gap
    would penalise the very fix for over-triggering.
    """
    path = os.path.join(H.harness_root(), "skills", name, "SKILL.md")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except Exception:
        return False
    if not text.startswith("---"):
        return False
    block = text.split("---", 2)[1] if text.count("---") >= 2 else ""
    for line in block.splitlines():
        key, _, value = line.partition(":")
        if key.strip().lower() == "disable-model-invocation":
            return value.strip().lower() in ("true", "yes", "1")
    return False


def _untriggered_skills():
    """Model-invocable skills with no recorded trigger phrase.

    `skill_triggers.py` guards the quoted phrases inside each description
    against regression — for a skill with none, it is guarding nothing. A
    description with no trigger is also the shape most likely to be selected by
    accident, or passed over, when it sits next to a near-duplicate.
    """
    path = os.path.join(H.harness_root(), "evaluation", "skill_triggers.json")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception:
        return None
    return sorted(name for name, triggers in data.items()
                  if not triggers and not _user_invoked_only(name))


def library_report():
    stats = library_stats()
    skills = stats["skills"]
    print(f"Skill library — {stats['evaluated']} evaluated session(s) in the "
          "audit log.\n")

    if not stats["evaluated"]:
        print("  No session outcomes recorded yet. Per-skill contribution needs\n"
              "  gate verdicts to attribute; until sessions accumulate, this\n"
              "  report can only show the structural checks below.")
    else:
        engagement = stats["engagement"]
        flag = "" if engagement >= ENGAGEMENT_FLOOR else "  ← below floor"
        print(f"  Router engagement: {stats['engaged']}/{stats['evaluated']} "
              f"({engagement:.0%}), floor {ENGAGEMENT_FLOOR:.0%}{flag}")
        if skills:
            print(f"\n  {'skill':<34}{'n':>5}{'pass':>6}{'blk':>5}   contribution")
            for name, row in sorted(skills.items(),
                                    key=lambda kv: (-kv[1]["trials"], kv[0])):
                verdict = (f"{row['contribution']:+.2f}" if row["sufficient"]
                           else f"(n<{N_MIN}, no verdict)")
                print(f"  {name:<34}{row['trials']:>5}{row['pass']:>6}"
                      f"{row['blocked']:>5}   {verdict}")
            ready = [n for n, r in skills.items() if r["sufficient"]]
            print(f"\n  {len(ready)} of {len(skills)} skill(s) have n ≥ {N_MIN}. "
                  "Retirement decisions wait for that bar —\n"
                  "  acting on a thinner sample measured worse than leaving the "
                  "library alone.")

    untriggered = _untriggered_skills()
    if untriggered is None:
        print("\n  ! evaluation/skill_triggers.json is unreadable — trigger "
              "coverage unknown.")
    elif untriggered:
        print(f"\n  Skills with no recorded trigger ({len(untriggered)}) — the "
              "trigger guard protects nothing\n  for these, and a description "
              "with no trigger is the shape most easily shadowed:")
        for name in untriggered:
            print(f"    {name}")
    else:
        print("\n  Every active skill has at least one recorded trigger.")
    return 0


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if "--library" in args:
        return library_report()

    entries = H.read_audit()
    if not entries:
        print(f"No audit log at {H.audit_log_path()} — the hook layer has not "
              "recorded anything yet.")
        return 0

    proj = H.active_project()
    patterns = []
    if proj:
        patterns = [p for p in ((proj[1].get("validation") or {})
                                .get("commands") or []) if p]

    by_session = {}
    for e in entries:
        by_session.setdefault(e.get("session_id", "?"), []).append(e)

    compliant = 0
    blocks = asks = failed_injects = 0
    print(f"{len(by_session)} session(s) in the audit log"
          + (f" — validation patterns: {', '.join(patterns)}" if patterns
             else " — no validation patterns configured") + "\n")

    for sid, ents in sorted(by_session.items(),
                            key=lambda kv: min(e.get("ts", 0) for e in kv[1])):
        file_edits = [e for e in ents if H.is_file_edit(e)]
        real = [e for e in file_edits if not H.under_sessions(e["file_path"])]
        worklog = [e for e in file_edits if H.under_sessions(e["file_path"])
                   and e["file_path"].endswith(".md")]
        bash = [e for e in ents if H.is_bash(e)]
        events = [e for e in ents if H.is_event(e)]
        blocks += sum(1 for e in events if e.get("event") == "stop_block")
        asks += sum(1 for e in events if e.get("event", "").endswith("_ask"))
        failed_injects += sum(
            1 for e in events if e.get("event") == "session_start_inject"
            and e.get("detail", {}).get("worklog")
            and not e.get("detail", {}).get("checkpoint"))

        if not real:
            status, ok = "OK (no checkpoint-worthy edits)", True
        else:
            first_ts = min(e.get("ts", 0) for e in real)
            has_cp = any(e.get("ts", 0) >= first_ts - SLACK_SECONDS
                         for e in worklog)
            has_val = (not patterns) or any(
                e.get("ts", 0) >= first_ts - SLACK_SECONDS
                and any(p in e.get("command", "") for p in patterns)
                for e in bash)
            ok = has_cp and has_val
            misses = ([] if has_cp else ["checkpoint"]) + \
                     ([] if has_val else ["validation"])
            status = "OK" if ok else "MISS (" + ", ".join(misses) + ")"
        if ok:
            compliant += 1

        first = min((e.get("ts", 0) for e in ents), default=0)
        last = max((e.get("ts", 0) for e in ents), default=0)
        span = time.strftime("%Y-%m-%d %H:%M", time.localtime(first))
        if last - first >= 60:
            span += time.strftime("–%H:%M", time.localtime(last))
        files = sorted({e.get("file_path", "") for e in real})
        print(f"  {sid[:8]:<8}  {span}  {len(real):>3} edit(s) "
              f"{len(files):>2} file(s)  {len(worklog):>2} worklog "
              f"{len(bash):>3} bash  {status}")

    rate = 100.0 * compliant / len(by_session)
    print(f"\nCompliance: {compliant}/{len(by_session)} session(s) "
          f"({rate:.0f}%).")
    print(f"Hook layer: {blocks} stop-gate block(s), {asks} guard ask(s), "
          f"{failed_injects} session-start injection(s) that found a worklog "
          "but no parseable checkpoint.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
