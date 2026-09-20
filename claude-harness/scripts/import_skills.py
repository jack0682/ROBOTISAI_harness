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

"""One-shot: import external skill directories into the harness and register them.

Usage:
    python3 scripts/import_skills.py [--from DIR]

Copies every immediate subdirectory of --from (default ~/skills)
into the harness `skills/` layer verbatim — preserving each skill's own payload
(`scripts/`, `references/`, `templates/`, lock files, etc.). Then registers every
copied skill that carries a top-level `SKILL.md` as an `active` entry in
`registry/skills.yaml`.

Faithful + idempotent:
  - ALL subdirectories are copied (including shared-asset / review-bundle dirs
    that have no SKILL.md of their own), so nothing the skills reference is lost.
  - Only dirs with a top-level `SKILL.md` (and not starting with `_`) are
    registered as activatable skills.
  - A skill dir that already exists in the harness is left untouched; a registry
    entry that already exists (by name) is left as-is.

The skills become active because `.claude/skills` is a symlink to this `skills/`
directory (see install_bridge.py::_link_skills) — there is no copy/mirror step.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys

import _common as C

DEFAULT_SOURCE = "~/skills"


def _subdirs(source):
    """Immediate subdirectories of `source`, excluding dot-dirs, sorted."""
    for name in sorted(os.listdir(source)):
        if name.startswith("."):
            continue
        src = os.path.join(source, name)
        if os.path.isdir(src):
            yield name, src


def _is_skill(path):
    return os.path.isfile(os.path.join(path, "SKILL.md"))


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Import external skills into the harness skills/ layer.")
    ap.add_argument("--from", dest="source", default=DEFAULT_SOURCE,
                    help=f"Source skills directory (default: {DEFAULT_SOURCE}).")
    args = ap.parse_args(argv)

    source = os.path.abspath(os.path.expanduser(args.source))
    if not os.path.isdir(source):
        print(f"error: source not found: {source}", file=sys.stderr)
        return 2

    skills_root = C.rpath("skills")
    os.makedirs(skills_root, exist_ok=True)

    copied, already = [], []
    for name, src in _subdirs(source):
        dst = os.path.join(skills_root, name)
        if os.path.exists(dst):
            already.append(name)
            continue
        shutil.copytree(src, dst, symlinks=True)
        copied.append(name)

    # Best-effort provenance: keep the source lock file alongside the skills.
    lock = os.path.join(source, ".skill-lock.json")
    if os.path.isfile(lock):
        shutil.copy2(lock, os.path.join(skills_root, ".skill-lock.json"))

    # Register every skill dir (top-level SKILL.md, not a template) as active.
    # Batched: load once, append new entries, save once.
    reg = C.load_registry("skills")
    items = reg.setdefault("skills", [])
    have = {it.get("name") for it in items if isinstance(it, dict)}
    registered, no_skill_md = [], []
    for name, _src in _subdirs(source):
        dst = os.path.join(skills_root, name)
        if not _is_skill(dst):
            no_skill_md.append(name)
            continue
        if name.startswith("_") or name in have:
            continue
        items.append({"name": name, "path": f"skills/{name}", "status": "active"})
        have.add(name)
        registered.append(name)
    if registered:
        C.save_registry("skills", reg)

    n = len(registered)
    print(f"copied dirs:   {len(copied)} new, {len(already)} already present")
    print(f"registered:    {n} new active skill{'' if n == 1 else 's'}")
    if no_skill_md:
        print(f"no SKILL.md (copied, not registered): {', '.join(no_skill_md)}")
    if copied:
        head = ", ".join(copied[:8]) + (" ..." if len(copied) > 8 else "")
        print(f"  + {head}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
