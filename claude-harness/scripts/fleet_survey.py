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

"""Survey every harness installation on this machine — read-only.

The harness has no install/update path, so copies of it have accumulated and
drifted independently. Before any of them can be consolidated, we need to know
which ones hold work that exists nowhere else. This walks the filesystem, finds
every harness install, and reports for each: whether it is a git repo at all,
which upstream it points at, and — the part that matters — which of its commits
are absent from the canonical repo.

Read-only: runs only `git` query commands, writes nothing, fetches nothing.

    python3 fleet_survey.py [--root ~] [--canonical PATH] [--all] [--json]

Reports every harness install found under a root, and how each one relates
to the canonical checkout.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

MARKER = "claude-harness"          # a directory that identifies a harness install
SKIP = {".Trash", "node_modules", ".git", ".venv", "venv", "__pycache__"}
DEFAULT_CANONICAL = os.path.expanduser("~/harness_ws/ROBOTISAI_harness")

# Copies also accumulate outside the working tree. They are not all the same kind
# of thing, and lumping them together either hides real copies or drowns the list
# in noise, so classify instead of filtering.
CLASSES = (
    ("cache", "/Library/Caches/"),          # bytecode shadow trees; not installs
    ("worktree", "/.codex/worktrees/"),     # derivative checkouts of another repo
    ("cloud", "/Library/CloudStorage/"),    # real copies, synced off-machine
)


def classify(path):
    for name, needle in CLASSES:
        if needle in path:
            return name
    return "working"


def git(repo, *args, timeout=20):
    """Run a git query in `repo`. Returns stripped stdout, or None on any failure."""
    try:
        out = subprocess.run(
            ["git", "-C", repo, *args],
            capture_output=True, text=True, timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def find_installs(root, max_depth=10):
    """Every directory containing a `claude-harness/` child, i.e. a harness install."""
    root = os.path.abspath(os.path.expanduser(root))
    found = []
    base_depth = root.rstrip(os.sep).count(os.sep)
    for dirpath, dirnames, _ in os.walk(root):
        if dirpath.count(os.sep) - base_depth >= max_depth:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP and (not d.startswith(".") or d == ".codex")]
        if MARKER in dirnames:
            found.append(dirpath)
            # Installs DO nest here (~/co-work holds one and contains more), so
            # keep descending -- but never into the harness package itself.
            dirnames.remove(MARKER)
    return sorted(found)


def survey_one(path, canonical):
    """Everything we need to decide this copy's fate, without changing it."""
    rec = {"path": path, "is_git": os.path.isdir(os.path.join(path, ".git"))}
    if not rec["is_git"]:
        # A plain copy can never be updated by git and can never be pushed from.
        # Anything unique in it is unrecoverable except by hand.
        rec["verdict"] = "plain-copy"
        return rec

    rec["remote"] = git(path, "remote", "get-url", "origin") or "(none)"
    rec["branch"] = git(path, "rev-parse", "--abbrev-ref", "HEAD") or "(detached)"
    rec["head"] = git(path, "rev-parse", "--short", "HEAD") or "(none)"
    status = git(path, "status", "--porcelain")
    rec["dirty"] = len(status.splitlines()) if status else 0

    # Commits this copy has that canonical does not. This is the only question
    # that blocks consolidation: everything else can be re-derived.
    unique = []
    if canonical and path != canonical:
        revs = git(path, "rev-list", "--all", "--max-count=400")
        for sha in (revs.splitlines() if revs else []):
            if git(canonical, "cat-file", "-e", f"{sha}^{{commit}}") is None:
                subject = git(path, "log", "--oneline", "-1", sha)
                unique.append(subject or sha[:9])
    rec["unique_commits"] = unique

    if unique:
        rec["verdict"] = "HOLDS UNIQUE WORK"
    elif rec["dirty"]:
        rec["verdict"] = "dirty-only"
    else:
        rec["verdict"] = "clean-derivative"
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="~", help="where to search (default: ~)")
    ap.add_argument("--canonical", default=DEFAULT_CANONICAL,
                    help=f"repo to compare against (default: {DEFAULT_CANONICAL})")
    ap.add_argument("--all", action="store_true",
                    help="also survey cloud-synced copies and codex worktrees")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    canonical = os.path.abspath(os.path.expanduser(args.canonical))
    if not os.path.isdir(os.path.join(canonical, ".git")):
        print(f"canonical is not a git repo: {canonical}", file=sys.stderr)
        return 2

    all_installs = find_installs(args.root)
    grouped = {}
    for path in all_installs:
        grouped.setdefault(classify(path), []).append(path)
    installs = grouped.get("working", [])
    if args.all:
        installs = [p for p in all_installs if classify(p) != "cache"]
    records = [survey_one(p, canonical) for p in installs]

    if args.json:
        print(json.dumps({"canonical": canonical, "installs": records}, indent=2))
        return 0

    home = os.path.expanduser("~")
    print(f"canonical: {canonical} @ {git(canonical, 'rev-parse', '--short', 'HEAD')}")
    print(f"installs found: {len(records)}\n")
    rows = sorted(records, key=lambda r: (r["verdict"] != "HOLDS UNIQUE WORK",
                                          r.get("path", "")))
    for r in rows:
        short = r["path"].replace(home, "~")
        if not r["is_git"]:
            print(f"  {'plain-copy':<18}  {short}")
            continue
        n = len(r["unique_commits"])
        flag = f"unique={n}" if n else "unique=0"
        print(f"  {r['verdict']:<18}  {short}")
        print(f"  {'':<18}  {r['branch']}@{r['head']}  dirty={r['dirty']}  {flag}"
              f"  {r['remote'].split('/')[-1]}")
        for line in r["unique_commits"][:6]:
            print(f"  {'':<18}    · {line}")
        if n > 6:
            print(f"  {'':<18}    · … and {n - 6} more")
        print()

    holds = [r for r in records if r.get("verdict") == "HOLDS UNIQUE WORK"]
    plain = [r for r in records if not r["is_git"]]
    print(f"summary: {len(records)} installs · {len(holds)} hold unique commits · "
          f"{len(plain)} are plain copies (unrecoverable by git)")
    for name, _ in CLASSES:
        extra = grouped.get(name, [])
        if extra and not args.all:
            note = {"cache": "python bytecode shadows, not real installs",
                    "worktree": "codex worktrees",
                    "cloud": "cloud-synced copies — real, and off this machine"}[name]
            print(f"  not surveyed: {len(extra):>2} {name} ({note}); --all includes them")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
