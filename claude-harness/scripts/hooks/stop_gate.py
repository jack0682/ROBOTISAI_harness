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

"""Stop hook — co-work continuation + checkpoint/evidence enforcement (v3).

Evidence comes from the audit log only, per session — no filesystem-mtime
heuristics (those were cross-satisfiable by concurrent sessions). Ordinary
checkpoint/evidence failures block at most once. An active co-work task armed
with ``continuation.mode=until_verified`` is different: while it is Claude's
turn the gate blocks every stop attempt, including ``stop_hook_active`` retries,
until Claude hands off or reaches a valid terminal state. A pending durable
``멈추지마`` control event also blocks until reconciliation.

Checks (only when this session made file edits outside sessions/):
  1. Checkpoint — this session wrote/updated a sessions/*.md at/after the
     edits began.
  2. Validation evidence — only when the active project's config declares
     `validation.commands` patterns: at least one audited Bash command
     matching a pattern ran at/after the edits began.
"""

from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _hooklib as H

sys.path.insert(0, os.path.join(H.harness_root(), "scripts"))
import _claims

# A worklog write up to this many seconds before the first edit still counts
# (covers "checkpoint written, edit follows immediately" races).
SLACK_SECONDS = 60


# Phrases that mark a claim's verification ceiling. Deliberately a small,
# literal set: the point is that the ceiling was written down, and a gate that
# tries to judge the quality of the prose judges nothing reliably.
_CEILING_MARKERS = (
    "verification ceiling", "not hardware-validated", "not run",
    "analysis only", "analysis-only", "unverified:", "could not be run",
)


def _states_verification_ceiling(entries, first_ts, hdir):
    """Did this session write down what it could not verify?

    Reads the checkpoint the gate already requires, rather than adding a second
    artifact: an analysis-only project owes the same worklog, with its limits in
    it.
    """
    path = H.latest_session_file()
    if not path:
        return False
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read().lower()
    except OSError:
        return False
    return any(marker in text for marker in _CEILING_MARKERS)


def _matches_validation(command, patterns):
    """Does this command actually run one of the declared validations?

    Substring matching over the raw command line meant `echo "pytest"` satisfied
    a pytest requirement. Match against the words of each shell segment instead,
    so the pattern has to appear as something being executed rather than as text
    being printed.
    """
    if not command:
        return False
    for segment in re.split(r"\|\||&&|[;&|\n()`]", command):
        # Remove quoted spans before splitting, not after: `echo "colcon test"`
        # splits into two unquoted-looking words otherwise, and a pattern that
        # spans them matches text the shell only ever printed.
        spoken = " ".join(re.sub(r"[\"'][^\"']*[\"']", " ", segment).split())
        if spoken and any(pattern in spoken for pattern in patterns):
            return True
    return False


def _emit_block(session_id, reason, *, persistent, edits=0, reasons=1):
    # Logging is observability, not authority. A full/unavailable audit log must
    # never turn a required persistent block into a silent pass.
    try:
        H.log_event(
            session_id,
            "stop_block",
            reasons=reasons,
            edits=edits,
            persistent=persistent,
        )
    except Exception:
        pass
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


def _log_outcome(session_id, entries, blocked):
    """Record which skills were in play and whether the gate let the session go.

    `verdict` is the gate's own judgement, not a claim about the work's quality:
    `pass` means the evidence the project asked for was present, `blocked` means
    it was not. That is the strongest outcome signal available without a human,
    and it is the one the stop gate already computes.
    """
    skills = sorted({e["skill"] for e in entries if H.is_skill_use(e)})
    try:
        H.log_event(session_id, "session_outcome",
                    skills=skills,
                    verdict="blocked" if blocked else "pass")
    except Exception:
        # Observability must never turn into a second failure mode for the gate.
        pass


def main():
    data = H.read_input()
    session_id = data.get("session_id", "")

    if data.get("stop_hook_active"):
        return 0

    entries = H.read_audit(session_id)
    file_edits = [e for e in entries if H.is_file_edit(e)]
    real = [e for e in file_edits if not H.under_sessions(e["file_path"])]
    if not real:
        return 0
    first_ts = min(e.get("ts", 0) for e in real)

    hdir = H.hdir_name()
    reasons = []

    worklog_writes = [e for e in file_edits
                      if H.under_sessions(e["file_path"])
                      and e["file_path"].endswith(".md")]
    if not any(e.get("ts", 0) >= first_ts - SLACK_SECONDS
               for e in worklog_writes):
        files = sorted({e.get("file_path", "") for e in real})
        reasons.append(
            f"this session modified {len(files)} file(s) but wrote no "
            f"worklog/checkpoint in {hdir}/sessions/ since the edits began — "
            "write or update one now (e.g. /harness-checkpoint): current "
            "state, validation performed, next action")

    proj = H.active_project()
    patterns = []
    if proj:
        patterns = [p for p in ((proj[1].get("validation") or {})
                                .get("commands") or []) if p]
    environment = {}
    if proj and isinstance(proj[1].get("environment"), dict):
        environment = proj[1]["environment"]
    analysis_only = str(environment.get("verification_mode") or "").strip().lower(
        ) == "analysis_only"

    if proj and analysis_only:
        # Execution evidence cannot exist here, and demanding it would leave the
        # gate permanently unsatisfiable -- which in practice means switched off.
        # The substitute is an analytic verification that states its own ceiling,
        # so unverified work still cannot pass as verified.
        if not _states_verification_ceiling(entries, first_ts, hdir):
            reasons.append(
                f"project '{proj[0]}' runs in an analysis-only environment, so "
                "the checkpoint must carry a verification ceiling — what was "
                "established by reading and reasoning, and what remains "
                f"unverified because it could not be run ({hdir}/modes/verify.md)")
    elif patterns:
        bash = [e for e in entries if H.is_bash(e)]
        recent = [e for e in bash if e.get("ts", 0) >= first_ts - SLACK_SECONDS]
        matched = [e for e in recent
                   if _matches_validation(e.get("command", ""), patterns)]
        # A run that is known to have failed is not evidence of validation. An
        # unknown outcome still counts: see post_edit._succeeded.
        passed = [e for e in matched if e.get("ok") is not False]
        if not matched:
            reasons.append(
                f"project '{proj[0]}' declares validation commands "
                f"({', '.join(patterns)}) but none ran since the edits began — "
                "run the relevant ones and report the real result "
                f"({hdir}/protocols/validation.md)")
        elif not passed:
            reasons.append(
                f"project '{proj[0]}'s validation command ran and failed. A "
                "failing run is not evidence that the change is validated — fix "
                "it, or report the failure as the result "
                f"({hdir}/protocols/validation.md)")

    # Claim discipline: a claim (scope: claim) edited this session must not be
    # left `settled` without threshold/evidence/expiry, or settled-but-stale —
    # an unearned "settled" is exactly the decorative-rigor failure the harness
    # exists to block (scripts/_claims.py, memory/claims/README.md).
    claim_problems = []
    for path in sorted({e.get("file_path", "") for e in file_edits}):
        if not path or not os.path.isfile(path):
            continue
        cerrs, is_claim, stale = _claims.check_file(path)
        if cerrs:
            claim_problems.extend(cerrs)
        elif is_claim and stale:
            claim_problems.append(
                f"{os.path.basename(path)}: marked settled but its review_at "
                "has passed — re-verify and bump review_at, or set status open")
    if claim_problems:
        reasons.append(
            "a claim edited this session is not load-bearing — "
            + "; ".join(claim_problems))

    # Attribute this session's verdict to the skills it used, so the library can
    # later be curated on outcomes rather than on opinion. Only sessions the gate
    # actually evaluated are recorded: a session with no edits outside sessions/
    # produced no verifiable outcome, and counting it either way would put noise
    # into ĉ(s) = (successes − failures) / trials.
    _log_outcome(session_id, entries, blocked=bool(reasons))

    if not reasons:
        return 0

    _emit_block(
        session_id,
        f"[{hdir} stop gate] " + "; AND ".join(reasons) +
        ". If the work was genuinely trivial, state that explicitly to the "
        "user instead — either way you may finish after this; the ordinary "
        "checkpoint/evidence gate only fires once per session.",
        persistent=False,
        edits=len(real),
        reasons=len(reasons),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(H.safe(main))
