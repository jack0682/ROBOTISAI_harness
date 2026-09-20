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

"""Claim-expiry logic — shared by validate_harness.py and the stop_gate hook.

A *claim* is a memory item with `scope: claim` (it lives in `memory/claims/`).
This module makes the falsifiability commitment load-bearing instead of
decorative: a claim may only be marked `settled` if it carries

  - `threshold:` — the measurable bar that would *refute* it,
  - `evidence:`  — the result that actually met that threshold, and
  - `review_at:` — a date by which a settled claim must be re-checked (its
    expiry clock; reused from the existing memory frontmatter field).

A `settled` claim whose `review_at` is in the past is **stale**: time has
passed without re-verification, so it may no longer be cited as settled until
renewed (bump `review_at` after re-checking) or retired (flip to `open` /
archive). This is Haft's "reopen-on-decay", made manual — a human re-confirms.

A claim may also be **contradicted**: `contradicted_by:` names the claim(s) or
artifact(s) that conflict with it. `settled` + a standing contradiction is an
error, not a state — recording that something refutes a claim and leaving it
certified is the exact failure this module exists to prevent. Edges (both
`supersedes` and `contradicted_by`) must name a claim that exists, the same
rule the work graph already enforces on its own typed edges.

Stdlib only and defensive: callers include a fail-open hook, so nothing here
may raise on malformed input. `memory/claims/README.md` documents the schema.
"""

from __future__ import annotations

import os
import re
from datetime import date

ALLOWED_STATUS = ("open", "settled", "stale")
ALLOWED_IMPORTANCE = ("high", "medium", "low")
# Values that count as "not filled in" for a required claim field.
_EMPTY = {"", "none", "~", "tbd", "todo", "n/a", "na", "..."}


def parse_frontmatter(text):
    """Return the frontmatter as a dict, or None if there is no closed block.

    Minimal `key: value` reader (the claim frontmatter is flat scalars); strips
    one layer of surrounding quotes. Tolerant: unparseable lines are skipped.
    """
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fm = {}
    for line in parts[1].splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        fm[key.strip()] = val
    return fm


def is_claim(fm):
    return bool(fm) and (fm.get("scope") or "").strip().lower() == "claim"


def _empty(v):
    return v is None or v.strip().lower() in _EMPTY


def parse_date(s):
    if not s:
        return None
    try:
        return date.fromisoformat(s.strip())
    except Exception:
        return None


def check_claim(fm, rel):
    """Structural errors for one claim item (independent of the calendar).

    `settled` is the earned state: it must state what would refute it, the
    evidence that met that bar, and when it expires.
    """
    errs = []
    status = (fm.get("status") or "").strip().lower()
    if not status:
        errs.append(f"claim {rel}: missing 'status' (open|settled|stale)")
        return errs
    if status not in ALLOWED_STATUS:
        errs.append(f"claim {rel}: status '{status}' not in "
                    f"{'|'.join(ALLOWED_STATUS)}")
    importance = (fm.get("importance") or "").strip().lower()
    if importance and importance not in ALLOWED_IMPORTANCE:
        errs.append(f"claim {rel}: importance '{importance}' not in "
                    f"{'|'.join(ALLOWED_IMPORTANCE)}")
    if status == "settled":
        if _empty(fm.get("threshold")):
            errs.append(f"claim {rel}: status=settled but 'threshold' is empty "
                        "— a settled claim must state what would refute it")
        if _empty(fm.get("evidence")):
            errs.append(f"claim {rel}: status=settled but 'evidence' is empty "
                        "— a settled claim must cite the result that met its "
                        "threshold")
        if parse_date(fm.get("review_at")) is None:
            errs.append(f"claim {rel}: status=settled but 'review_at' is not a "
                        "date — a settled claim must declare its expiry")
        if contradictions(fm):
            errs.append(
                f"claim {rel}: status=settled but 'contradicted_by' names "
                f"{', '.join(contradictions(fm))} — a recorded contradiction "
                "must be resolved or the claim reopened, not carried as settled")
    return errs


def contradictions(fm):
    """What this claim's frontmatter records as contradicting it.

    The provenance relations this harness could already express were Support
    (threshold/evidence), Invalidate (supersedes) and Depend-on (the work
    graph's blocked_by). `Contradict` had no home: there was nowhere to write
    down that a result conflicts with a standing claim. In a harness whose
    central operation is attacking its own conclusions (`modes/counter.md`),
    that absence meant a counterexample could only be acted on or forgotten,
    never *recorded against* the claim it threatens.
    """
    raw = (fm.get("contradicted_by") or "").strip()
    if not raw or raw.lower() in _EMPTY:
        return []
    items = [t.strip().strip("[]\"'") for t in raw.replace(";", ",").split(",")]
    return [t for t in items if t and t.lower() not in _EMPTY]


def dangling_refs(fm, claims_dir):
    """Slugs this claim points at that do not exist.

    The work graph treats a dangling edge as an error ("the graph may not lie");
    claims carried the same supersede-over-delete semantics with no check at
    all. A pointer at a claim that was never written, or was renamed, is the
    same defect in both places.
    """
    names = list(contradictions(fm))
    sup = (fm.get("supersedes") or "").strip()
    if sup and sup.lower() not in _EMPTY:
        names.append(sup.strip("[]\"'"))
    missing = []
    for name in names:
        slug = os.path.basename(name)
        if slug.endswith(".md"):
            slug = slug[:-3]
        if not slug:
            continue
        if not os.path.isfile(os.path.join(claims_dir, slug + ".md")):
            missing.append(slug)
    return missing


# A path-shaped token: has a separator and a plausible extension or known suffix.
_PATH_RE = re.compile(r"[A-Za-z0-9_.\-]*(?:/[A-Za-z0-9_.\-]+)+")


def missing_evidence_paths(evidence, root=None):
    """Artifacts the evidence names that are not on disk.

    Prose evidence is allowed and returns nothing: not every claim is settled by
    a file. But when the evidence points at one, the file has to be there. The
    flagship claim of this harness was `settled` citing observations in
    `sessions/.audit.log`, a file that had never been written — the falsifiability
    mechanism certifying an unearned claim about itself.
    """
    if _empty(evidence):
        return []
    base = root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    missing = []
    for token in _PATH_RE.findall(str(evidence)):
        token = token.strip(".,;:)'\"")
        # Only judge tokens that look like they name something in this harness.
        if not token or token.startswith(("http", "//")) or " " in token:
            continue
        if not token.split("/", 1)[0] in _EVIDENCE_ROOTS:
            continue
        if not os.path.exists(os.path.join(base, token)):
            missing.append(token)
    return missing


# Top-level directories a claim can point at. Anything else in an evidence string
# is prose or an external reference, and not this checker's business.
_EVIDENCE_ROOTS = frozenset({
    "sessions", "memory", "projects", "evaluation", "docs", "scripts",
    "modes", "scopes", "kernel", "protocols", "templates", "skills", "tests",
})


def is_stale(fm, today=None):
    """True when a `settled` claim's review_at expiry has passed."""
    if (fm.get("status") or "").strip().lower() != "settled":
        return False
    d = parse_date(fm.get("review_at"))
    return d is not None and d < (today or date.today())


def check_file(path):
    """Return (errors, is_claim, stale) for a memory item file. Fail-soft:
    any read/parse problem yields ([], False, False) so a hook never crashes."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except Exception:
        return [], False, False
    fm = parse_frontmatter(text)
    if not is_claim(fm):
        return [], False, False
    rel = os.path.basename(path)
    errs = check_claim(fm, rel)
    for slug in dangling_refs(fm, os.path.dirname(os.path.abspath(path))):
        errs.append(f"claim {rel}: points at '{slug}', which is not a claim in "
                    "memory/claims/ — a supersede or contradiction edge may not "
                    "name something that does not exist")
    return errs, True, is_stale(fm)


def is_contradicted(fm):
    """True when a claim records a standing contradiction, whatever its status."""
    return bool(contradictions(fm))
