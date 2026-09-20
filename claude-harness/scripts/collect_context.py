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

"""Assemble and print the harness load order for a project + task type.

Prints the exact files, in load order, that the harness would feed Claude for the
given project and task. Use --show to also print their contents (the full context
blob).

Usage:
    python3 scripts/collect_context.py <project> [task_type] [--show]
"""

from __future__ import annotations

import argparse
import os
import sys

import _common as C


def main(argv=None):
    ap = argparse.ArgumentParser(description="Preview the harness load order.")
    ap.add_argument("project", help="Project name (under projects/).")
    ap.add_argument("task_type", nargs="?", default="",
                    help="Task type / protocol name (e.g. coding). Omitted → the "
                         "project's protocols.default, else harness defaults.")
    ap.add_argument("--show", action="store_true", help="Print file contents too.")
    args = ap.parse_args(argv)

    config = C.load_config()
    order = []  # list of (label, relpath)

    # 1. Entry point
    order.append(("entry", "HARNESS.md"))

    # 2. Kernel, in configured order
    for name in config.get("kernel", []):
        order.append(("kernel", f"kernel/{name}.md"))

    # Project config drives protocols, styles, skills, and overrides.
    proj_dir = f"projects/{args.project}"
    proj_cfg_path = C.rpath(proj_dir, "project.config.yaml")
    if not os.path.isfile(proj_cfg_path):
        print(f"error: project '{args.project}' not found "
              f"({proj_dir}/project.config.yaml missing)", file=sys.stderr)
        return 1
    proj_cfg = C.load_yaml(proj_cfg_path)

    # 3. Protocols: the explicit task type (or the project's defaults, else the
    #    harness defaults), plus the project's additional protocols.
    proto_cfg = proj_cfg.get("protocols", {}) or {}
    names = [args.task_type] if args.task_type else list(
        proto_cfg.get("default")
        or config.get("defaults", {}).get("protocols", []))
    names += proto_cfg.get("additional") or []
    seen = set()
    for n in names:
        if n in seen:
            continue
        seen.add(n)
        proto = f"protocols/{n}.md"
        if os.path.isfile(C.rpath(proto)):
            order.append(("protocol", proto))
        else:
            print(f"warning: no protocol '{n}' ({proto} not found)",
                  file=sys.stderr)

    # 4. Styles (project defaults, else global defaults)
    styles = (proj_cfg.get("styles", {}) or {}).get("default") \
        or config.get("defaults", {}).get("styles", [])
    for s in styles:
        order.append(("style", f"styles/{s}.md"))

    # 5. Required skills
    for sk in (proj_cfg.get("skills", {}) or {}).get("required", []):
        order.append(("skill", f"skills/{sk}/SKILL.md"))

    # 6. Project files, then overrides
    for f in ("PROJECT.md", "context.md", "constraints.md", "local_rules.md"):
        order.append(("project", f"{proj_dir}/{f}"))
    for ov in (proj_cfg.get("overrides", {}) or {}).get("files", []):
        order.append(("override", f"{proj_dir}/{ov}"))

    # 7. Latest session
    latest = _latest_session()
    if latest:
        order.append(("session", latest))

    # Print
    print(f"# Load order for project='{args.project}' task='{args.task_type}'\n")
    for i, (label, rel) in enumerate(order, 1):
        exists = os.path.isfile(C.rpath(rel))
        mark = "" if exists else "   [MISSING]"
        print(f"{i:2d}. [{label}] {rel}{mark}")

    if args.show:
        print("\n" + "=" * 72)
        for label, rel in order:
            p = C.rpath(rel)
            print(f"\n##### [{label}] {rel} #####\n")
            if os.path.isfile(p):
                with open(p, "r", encoding="utf-8") as fh:
                    print(fh.read())
            else:
                print("(missing)")
    return 0


def _latest_session():
    sess_dir = C.rpath("sessions")
    if not os.path.isdir(sess_dir):
        return None
    files = sorted(
        f for f in os.listdir(sess_dir)
        if f.endswith(".md") and not f.startswith("_") and f != "README.md"
    )
    return f"sessions/{files[-1]}" if files else None


if __name__ == "__main__":
    raise SystemExit(main())
