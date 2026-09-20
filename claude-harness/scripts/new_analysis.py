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

"""Attach the harness to an external repository for read-only analysis.

There was nothing between "no harness" and "full project registration + bridge
+ hooks". Deploying the whole thing to diagnose someone else's repo for an
afternoon is disproportionate, so in practice it did not get deployed at all and
the work happened with no work graph and no claim discipline.

This is the small end. It registers an **analysis target**: a work graph and a
claims area scoped to an external path, and nothing else. Specifically it does
**not**:

  - write a bridge into the external repo (no CLAUDE.md, no .claude/)
  - install hooks there
  - mark itself `active`

That last one is load-bearing. `_hooklib.active_project()` resolves a project
only when exactly one is `status: active`; a second active row silently switches
off the deletion guard, the plan-before-edit reminder and the validation-evidence
check. An analysis target is registered `status: analysis` so it is invisible to
the hook layer and cannot disarm the gates that govern the real project.

    python3 scripts/new_analysis.py <path-to-repo> [name]
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C

STATUS = "analysis"

_OPEN_QUESTIONS = """# Open questions — {name}

Analysis target: `{root}` (read-only; the harness is attached, not deployed).

`id` is `Q<n>`. `blocked_by` accepts a comma-separated list of `Q`/`I` ids;
`supersedes` takes one. Run `python3 scripts/work_graph.py {rel}/memory` to see
what is ready, blocked, or dangling.

| id | question | blocked_by | supersedes | status |
|----|----------|-----------|-----------|--------|
| Q1 | <question> | — | — | open |
"""

_KNOWN_ISSUES = """# Known issues — {name}

Analysis target: `{root}` (read-only).

| id | issue | impact | workaround | blocked_by | supersedes | status |
|----|-------|--------|-----------|-----------|-----------|--------|
| I1 | <issue> | <impact> | <workaround> | — | — | open |
"""

_README = """# {name} — analysis target

`{root}`

The harness is **attached** to this repository, not deployed into it: no
`CLAUDE.md`, no `.claude/`, no hooks were written there, and this target is
registered `status: analysis` so the hook layer does not resolve it as the
active project.

What it gives you:

- **`memory/open_questions.md` / `memory/known_issues.md`** — a typed work graph
  over the analysis, so a question blocked on another is visible as blocked
  rather than forgotten (`scripts/work_graph.py`).
- **`claims/`** — findings about this repository, under the same discipline as
  any other claim: `settled` needs a `threshold`, the `evidence` that met it, and
  a `review_at` (`memory/claims/README.md`). A diagnosis of someone else's system
  is exactly the kind of claim that ages badly.

Before forming a hypothesis about this code, harvest what it says about itself —
`TODO`/`FIXME`/`REGRESSION` notes, `CHANGELOG`, `git log`/`blame` on the crux
files (`protocols/debugging.md` step 3). And if someone described how this system
works, reconcile the description against the code before reasoning on it
(`modes/verify.md` operation 8). Both rules exist because this mode of work is
where they were first needed.

When the analysis ends, either promote it to a real project
(`scripts/new_project.py`) or flip this row to `status: archived` — leaving it
registered as `analysis` forever is how the registry starts lying.
"""


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print(__doc__)
        return 2

    root = os.path.abspath(os.path.expanduser(args[0]))
    if not os.path.isdir(root):
        print(f"not a directory: {root}")
        return 1
    name = C.slugify(args[1]) if len(args) > 1 else C.slugify(
        os.path.basename(root.rstrip(os.sep)))
    if not name:
        print("could not derive a name; pass one explicitly")
        return 1

    rel = f"analysis/{name}"
    dest = C.rpath(rel)
    if os.path.exists(dest):
        print(f"already registered: {rel}")
        return 1

    os.makedirs(os.path.join(dest, "memory"), exist_ok=True)
    os.makedirs(os.path.join(dest, "claims"), exist_ok=True)
    fields = {"name": name, "root": root, "rel": rel}
    for filename, body in (
            ("README.md", _README),
            (os.path.join("memory", "open_questions.md"), _OPEN_QUESTIONS),
            (os.path.join("memory", "known_issues.md"), _KNOWN_ISSUES)):
        with open(os.path.join(dest, filename), "w", encoding="utf-8") as fh:
            fh.write(body.format(**fields))

    reg_path = C.rpath("registry", "projects.yaml")
    reg = C.load_yaml(reg_path) or {}
    rows = reg.setdefault("projects", [])
    rows.append({"name": name, "path": rel, "status": STATUS, "skills": []})
    C.dump_yaml(reg_path, reg)

    print(f"analysis target registered: {rel}")
    print(f"  target repository : {root}")
    print(f"  work graph        : {rel}/memory/")
    print(f"  claims            : {rel}/claims/")
    print(f"  status            : {STATUS} (not active — the hook layer "
          "ignores it, and the real project keeps its gates)")
    print("  nothing was written into the target repository.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
