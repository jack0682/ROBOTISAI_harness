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

"""Detach a cloned harness from its template git, and wire it into the workspace.

Run this ONCE, right after cloning this harness as a template into a new
workspace. It severs the dependency on the template's git origin so the cloned
harness becomes a plain in-tree convention layer for THIS workspace, then
regenerates the native Claude Code bridge so the harness is in force here.

Topology (see harness.config.yaml `bridge`):
  <bridge_root>/                 <- the repo/workspace root the bridge auto-loads
    CLAUDE.md                    <- generated bridge (imports the spine)
    .claude/                     <- generated bridge (skills symlink, hooks, ...)
    claude-harness/  (== harness_root)   <- this harness
      KERNEL.md, ROUTING.md, kernel/, modes/, scopes/, scripts/, ...

The template git lives at <bridge_root>/.git (a `git clone` of the template) or,
if the harness was cloned standalone, at <harness_root>/.git. This tool removes
that ONE .git so the clone no longer tracks the template origin. It never removes
a .git that is not the template clone's, and it prints the remote first so you
can see what you are severing.

Usage:
    python3 scripts/detach_for_workspace.py            # dry-run: report the plan
    python3 scripts/detach_for_workspace.py --apply    # do it (destructive)
    python3 scripts/detach_for_workspace.py --apply --clean-sessions --git-init

Steps (dry-run prints them; --apply performs them):
  1. Remove the template clone's .git/  (kill the git dependency).
  2. Regenerate the bridge (install_bridge.py) into <bridge_root>.
  3. --clean-sessions: drop template session worklogs (keep README/_template).
  4. --git-init: initialize a fresh, empty git repo at <bridge_root>.
  5. Validate (validate_harness.py).
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C


def _git_remote(root):
    try:
        r = subprocess.run(["git", "-C", root, "remote", "-v"],
                           capture_output=True, text=True)
        return (r.stdout or r.stderr or "").strip() or "(no remotes / not a git repo)"
    except FileNotFoundError:
        return "(git not installed)"


def _find_template_git(bridge_root, harness_root):
    """The template clone's .git: prefer bridge_root/.git, else harness_root/.git.
    Returns the abspath of the .git dir, or None."""
    for root in (bridge_root, harness_root):
        g = os.path.join(root, ".git")
        if os.path.isdir(g):
            return g, root
    return None, None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true",
                    help="Perform the destructive steps (default: dry-run report).")
    ap.add_argument("--clean-sessions", action="store_true",
                    help="Also delete template session worklogs (keep README/_template).")
    ap.add_argument("--git-init", action="store_true",
                    help="Initialize a fresh empty git repo at the bridge root after detaching.")
    args = ap.parse_args(argv)

    config = C.load_config()
    harness_root = os.path.abspath(C.harness_root())
    bridge_root = os.path.abspath(C.rpath(config.get("bridge", {})
                                          .get("root_relative", "..")))
    git_dir, git_root = _find_template_git(bridge_root, harness_root)

    mode = "APPLY" if args.apply else "DRY-RUN (nothing will change; pass --apply to execute)"
    print(f"=== detach_for_workspace [{mode}] ===")
    print(f"harness_root : {harness_root}")
    print(f"bridge_root  : {bridge_root}")
    if git_dir:
        print(f"template .git: {git_dir}")
        print("  remote(s):")
        for line in _git_remote(git_root).splitlines():
            print(f"    {line}")
    else:
        print("template .git: (none found — already detached, or not a git clone)")
    print()

    # --- Step 1: remove template .git ---
    if git_dir:
        if args.apply:
            shutil.rmtree(git_dir)
            print(f"[1] removed {git_dir}  (git dependency severed)")
        else:
            print(f"[1] would remove {git_dir}")
    else:
        print("[1] skip — no template .git to remove")

    # --- Step 2: regenerate the bridge ---
    install = os.path.join(harness_root, "scripts", "install_bridge.py")
    if args.apply:
        r = subprocess.run([sys.executable, install], capture_output=True, text=True)
        print(f"[2] install_bridge.py -> exit {r.returncode}")
        for line in (r.stdout or "").strip().splitlines()[-6:]:
            print(f"    {line}")
        if r.returncode != 0:
            print("    STDERR:", (r.stderr or "").strip()[:300])
    else:
        print(f"[2] would run: python3 {os.path.relpath(install, bridge_root)}")

    # --- Step 3: clean template sessions ---
    sessions = os.path.join(harness_root, "sessions")
    keep = {"README.md", "_session_template.md"}
    worklogs = []
    for d in (sessions, os.path.join(sessions, "active")):
        if os.path.isdir(d):
            worklogs += [os.path.join(d, f) for f in os.listdir(d)
                         if f.endswith(".md") and f not in keep]
    if args.clean_sessions:
        if args.apply:
            for f in worklogs:
                os.remove(f)
            print(f"[3] removed {len(worklogs)} template session worklog(s)")
        else:
            print(f"[3] would remove {len(worklogs)} template session worklog(s)")
    else:
        print(f"[3] skip session cleanup ({len(worklogs)} worklog(s) kept; "
              "pass --clean-sessions to drop them)")

    # --- Step 4: fresh git ---
    if args.git_init:
        if args.apply:
            r = subprocess.run(["git", "-C", bridge_root, "init"],
                               capture_output=True, text=True)
            print(f"[4] git init at {bridge_root} -> exit {r.returncode}")
        else:
            print(f"[4] would run: git init at {bridge_root}")
    else:
        print("[4] skip git-init (workspace stays git-less unless you init your own)")

    # --- Step 5: validate ---
    validate = os.path.join(harness_root, "scripts", "validate_harness.py")
    if args.apply:
        r = subprocess.run([sys.executable, validate], capture_output=True, text=True)
        print(f"[5] validate_harness.py -> exit {r.returncode}: "
              f"{(r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr).strip() else ''}")
    else:
        print(f"[5] would run: python3 {os.path.relpath(validate, bridge_root)}")

    print()
    if args.apply:
        print("Done. The harness now governs this workspace with no dependency on "
              "the template origin.")
        print("Next: run  /harness-init  to fill the project overlay for this workspace.")
    else:
        print("Dry-run only. Re-run with --apply to execute.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
