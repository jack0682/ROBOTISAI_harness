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

"""Scaffold a new skill module from skills/_skill_template/.

Usage:
    python3 scripts/new_skill.py <skill-name> [--description "..."]

Copies the template, fills the name/description into SKILL.md frontmatter, and
registers the skill in registry/skills.yaml.
"""

from __future__ import annotations

import argparse
import os
import sys

import _common as C


def main(argv=None):
    ap = argparse.ArgumentParser(description="Create a new skill module.")
    ap.add_argument("name", help="Skill name (slugified for the directory).")
    ap.add_argument("--description", default="", help="One-line trigger description.")
    args = ap.parse_args(argv)

    slug = C.slugify(args.name)
    if not slug:
        print("error: name produced an empty slug", file=sys.stderr)
        return 2

    src = C.rpath("skills", "_skill_template")
    dst = C.rpath("skills", slug)
    try:
        C.copy_template(src, dst)
    except FileExistsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    # The template ships as SKILL.md.template so the live skills/ directory
    # (served via the .claude/skills symlink) never exposes the template as an
    # activatable skill. Materialize it as SKILL.md in the new skill.
    skill_md = os.path.join(dst, "SKILL.md")
    os.rename(os.path.join(dst, "SKILL.md.template"), skill_md)
    repl = {"_skill_template": slug, "<name>": slug}
    if args.description:
        repl["TEMPLATE — replace with a one-line trigger description. State what "
             "the skill does and the intent/phrases that should activate it."] = (
            args.description
        )
    C.replace_in_file(skill_md, repl)

    added = C.registry_add(
        "skills",
        "skills",
        {"name": slug, "path": f"skills/{slug}", "status": "active"},
    )

    print(f"Created skill '{slug}' at skills/{slug}")
    print("Registered in registry/skills.yaml" if added else
          "Note: registry already had an entry with this name (left as-is).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
