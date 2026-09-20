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

"""Scaffold a new project harness from projects/_project_template/.

Usage:
    python3 scripts/new_project.py <project-name> [--description "..."]

Copies the template, fills the project name/description into PROJECT.md and
project.config.yaml, and registers the project in registry/projects.yaml.
"""

from __future__ import annotations

import argparse
import os
import sys

import _common as C


def main(argv=None):
    ap = argparse.ArgumentParser(description="Create a new project harness.")
    ap.add_argument("name", help="Project name (slugified for the directory).")
    ap.add_argument("--description", default="", help="One-line description.")
    args = ap.parse_args(argv)

    slug = C.slugify(args.name)
    if not slug:
        print("error: name produced an empty slug", file=sys.stderr)
        return 2

    src = C.rpath("projects", "_project_template")
    dst = C.rpath("projects", slug)
    try:
        C.copy_template(src, dst)
    except FileExistsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    # Fill the obvious placeholders.
    C.replace_in_file(os.path.join(dst, "PROJECT.md"), {"<name>": slug})
    cfg = os.path.join(dst, "project.config.yaml")
    data = C.load_yaml(cfg)
    data.setdefault("project", {})["name"] = slug
    if args.description:
        data["project"]["description"] = args.description
    C.dump_yaml(cfg, data)

    added = C.registry_add(
        "projects",
        "projects",
        {"name": slug, "path": f"projects/{slug}", "status": "active", "skills": []},
    )

    print(f"Created project '{slug}' at projects/{slug}")
    print("Registered in registry/projects.yaml" if added else
          "Note: registry already had an entry with this name (left as-is).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
