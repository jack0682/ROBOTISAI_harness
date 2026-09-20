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

"""Work-state as a dependency graph — shared by validate, session_start, CLI.

Adapted from Beads: long-horizon work (open questions, known issues) is not a
flat list but a graph with typed edges. Flat lists hide two things that matter
across many sessions — which open item is *blocked* on another still-open item,
and which items have been *superseded* but never retired. This module reads the
project's `open_questions.md` (IDs `Q1…`) and `known_issues.md` (IDs `I1…`)
pipe-tables and computes:

  - ready          — open items with zero open blockers (what to work on now)
  - blocked        — open items waiting on a still-open blocker (and on which)
  - superseded_open — items something else supersedes that are still open (retire)
  - dangling       — blocked_by/supersedes edges pointing at an unknown ID
  - cycles         — blocked_by deadlocks (A waits on B waits on A)

Stdlib only and defensive (a fail-open hook imports it): malformed input yields
empty results, never an exception. Took Beads' data model (typed edges +
ready-set + supersedes), not its Dolt/SQL storage — the source of truth stays
markdown tables a human reads and edits.
"""

from __future__ import annotations

import os
import re

_ID_RE = re.compile(r"^[QI]\d+$")
# A status that means the item is no longer open work.
_CLOSED = {"answered", "fixed", "done", "resolved", "closed", "superseded",
           "dropped", "wontfix", "won't fix"}
# Cells that mean "no edge".
_NONE_CELLS = {"", "-", "—", "–", "none", "n/a", "na"}


def _split_rows(text):
    """Yield the data rows of every pipe-table in `text` as lists of cells.

    A data row is `| a | b | ... |`; the header and the `|---|` separator are
    skipped, as are rows whose first content cell is a `<placeholder>`.
    """
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells:
            continue
        joined = "".join(cells)
        if set(joined) <= set("-: "):          # separator row
            continue
        if cells[0].lower() in ("id", "#", "date"):  # header row
            continue
        yield cells


def _edges(cell):
    out = []
    for tok in (cell or "").replace(";", ",").split(","):
        tok = tok.strip()
        if _ID_RE.match(tok):
            out.append(tok)
    return out


def _one_edge(cell):
    tok = (cell or "").strip()
    return tok if _ID_RE.match(tok) else None


def _parse_file(path, kind_prefix, columns):
    """Parse one work table. `columns` maps logical field -> header label we
    expect; we locate fields by position via a tolerant column order instead,
    so this just needs the file to follow its template's column order."""
    items = {}
    if not os.path.isfile(path):
        return items
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except Exception:
        return items
    for cells in _split_rows(text):
        idc = cells[0]
        if not idc.startswith(kind_prefix) or not _ID_RE.match(idc):
            continue
        row = dict(zip(columns, cells + [""] * (len(columns) - len(cells))))
        text_cell = row.get("text", "")
        if text_cell.startswith("<") and text_cell.endswith(">"):
            continue  # untouched template placeholder
        status = (row.get("status", "") or "").strip().lower()
        items[idc] = {
            "id": idc,
            "kind": "question" if kind_prefix == "Q" else "issue",
            "text": text_cell,
            "blocked_by": _edges(row.get("blocked_by", "")),
            "supersedes": _one_edge(row.get("supersedes", "")),
            "status": status,
            "open": status not in _CLOSED,
        }
    return items


def load_items(memory_dir):
    """Build the item map for a project memory dir. Column orders match the
    templates in projects/_project_template/memory/."""
    items = {}
    items.update(_parse_file(
        os.path.join(memory_dir, "open_questions.md"), "Q",
        ["id", "text", "blocked_by", "supersedes", "status"]))
    items.update(_parse_file(
        os.path.join(memory_dir, "known_issues.md"), "I",
        ["id", "text", "impact", "workaround", "blocked_by", "supersedes",
         "status"]))
    return items


def analyze(items):
    ready, blocked, superseded_open, dangling, cycles = [], {}, [], [], []
    ids = set(items)

    for it in items.values():
        for dep in it["blocked_by"]:
            if dep not in ids:
                dangling.append((it["id"], "blocked_by", dep))
        if it["supersedes"] and it["supersedes"] not in ids:
            dangling.append((it["id"], "supersedes", it["supersedes"]))

    # An item that something else supersedes should be retired, not left open.
    superseders = {it["supersedes"]: it["id"]
                   for it in items.values() if it["supersedes"]}
    for sid, by in superseders.items():
        tgt = items.get(sid)
        if tgt and tgt["open"]:
            superseded_open.append((sid, by))

    for it in items.values():
        if not it["open"]:
            continue
        has_dangling = any(d not in items for d in it["blocked_by"])
        open_blockers = [d for d in it["blocked_by"]
                         if d in items and items[d]["open"]]
        if open_blockers:
            blocked[it["id"]] = open_blockers
        elif has_dangling:
            # Points at an unknown blocker — an error state, not "ready". It is
            # reported under `dangling`; do not advertise it as workable.
            continue
        else:
            ready.append(it["id"])

    cycles = _find_cycles(items)
    return {
        "ready": sorted(ready),
        "blocked": blocked,
        "superseded_open": superseded_open,
        "dangling": dangling,
        "cycles": cycles,
    }


def _find_cycles(items):
    """Return blocked_by cycles among open items (each cycle as a list of ids)."""
    WHITE, GREY, BLACK = 0, 1, 2
    color = {i: WHITE for i in items}
    found = []

    def visit(node, stack):
        color[node] = GREY
        stack.append(node)
        for dep in items[node]["blocked_by"]:
            if dep not in items or not items[dep]["open"]:
                continue
            if color[dep] == GREY:
                found.append(stack[stack.index(dep):] + [dep])
            elif color[dep] == WHITE:
                visit(dep, stack)
        stack.pop()
        color[node] = BLACK

    for i, it in items.items():
        if it["open"] and color[i] == WHITE:
            visit(i, [])
    return found


def integrity_problems(items):
    """Errors (dangling edge, cycle) and warnings (superseded-but-open) for a
    work graph — consumed by validate_harness.py. Returns (errors, warnings)."""
    a = analyze(items)
    errs, warns = [], []
    for src, kind, dep in a["dangling"]:
        errs.append(f"{src} {kind} -> {dep}: no such work item")
    for cyc in a["cycles"]:
        errs.append("blocked_by cycle: " + " -> ".join(cyc))
    for sid, by in a["superseded_open"]:
        warns.append(f"{sid} is superseded by {by} but still open — close/retire it")
    return errs, warns


def _cli(argv):
    import sys
    memory_dir = argv[1] if len(argv) > 1 else "."
    items = load_items(memory_dir)
    a = analyze(items)
    if not items:
        print(f"no work items found under {memory_dir}")
        return 0
    print(f"READY ({len(a['ready'])}): " + (", ".join(a["ready"]) or "—"))
    if a["blocked"]:
        print("BLOCKED:")
        for i, deps in sorted(a["blocked"].items()):
            print(f"  {i} waits on {', '.join(deps)}")
    for sid, by in a["superseded_open"]:
        print(f"SUPERSEDED-OPEN: {sid} (by {by}) — retire it")
    for src, kind, dep in a["dangling"]:
        print(f"DANGLING: {src} {kind} -> {dep}")
    for cyc in a["cycles"]:
        print("CYCLE: " + " -> ".join(cyc))
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(_cli(sys.argv))
