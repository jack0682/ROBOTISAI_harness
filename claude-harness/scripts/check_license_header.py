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

"""Check -- and optionally insert -- the mandatory ROBOTIS AI licence header.

All code in this organisation is Apache License 2.0 and every source file opens
with the header defined in
`skills/robotis-style/references/license-header.md`.

There are two forms, and the difference is a factual one:

* **A file this team writes** carries `Author: <name> <email>`, taken from the
  repository-local git identity -- the same identity that signs the commit.
  Never hardcoded, never guessed: with no local identity configured `--fix`
  refuses to run rather than write a wrong name into every file it touches.
* **An inherited file** -- code the team did not write but now owns -- carries
  the copyright and the Apache grant with **no** author line, inserted with
  `--no-author`. Naming the current user as the author of somebody else's file
  would be a false claim, and a licence header is not the place to make one.

`--staged` therefore enforces the header on every staged file and the `Author:`
line only on files the commit *adds*.

    python3 claude-harness/scripts/check_license_header.py              # report
    python3 claude-harness/scripts/check_license_header.py --fix        # insert
    python3 claude-harness/scripts/check_license_header.py --fix \
        --no-author                                                    # backfill
    python3 claude-harness/scripts/check_license_header.py --staged     # pre-commit

Exit status is 1 when any file is missing its header, so this is usable as a
gate.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

HOLDER = "ROBOTIS AI"

BODY = """Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""

# suffix -> line-comment marker
HASH = "#"
SLASH = "//"
COMMENT = {
    ".py": HASH, ".sh": HASH, ".bash": HASH, ".zsh": HASH,
    ".yaml": HASH, ".yml": HASH, ".cmake": HASH,
    ".c": SLASH, ".h": SLASH, ".cc": SLASH, ".cpp": SLASH, ".cxx": SLASH,
    ".hpp": SLASH, ".hxx": SLASH,
    ".js": SLASH, ".jsx": SLASH, ".ts": SLASH, ".tsx": SLASH,
}

# Per ROBOTIS ROS Style Guide 3-2: ROS interface files and launch files carry
# no licence header. `CMakeLists.txt` has no suffix, so it is named explicitly.
NAMED = {"CMakeLists.txt": HASH}
SKIP_SUFFIX = {".msg", ".srv", ".action"}
SKIP_NAME_ENDS = (".launch.py",)
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".pytest_cache", "build",
             "install", "log", "_archive", ".githooks"}


def marker_for(path):
    name = os.path.basename(path)
    if name in NAMED:
        return NAMED[name]
    if any(name.endswith(s) for s in SKIP_NAME_ENDS):
        return None
    suffix = os.path.splitext(name)[1]
    if suffix in SKIP_SUFFIX:
        return None
    return COMMENT.get(suffix)


def header_text(marker, year, author_name, author_email):
    """The header. `Author:` is omitted when no author is supplied.

    Inherited files -- code this team did not write -- carry the copyright and
    the Apache grant but no author line, because naming the current user as the
    author of somebody else's file is a false claim. New files carry all three.
    """
    lines = [f"Copyright {year} {HOLDER}", ""]
    lines += BODY.split("\n")
    if author_name and author_email:
        lines += ["", f"Author: {author_name} <{author_email}>"]
    out = []
    for line in lines:
        out.append(marker if not line else f"{marker} {line}")
    return "\n".join(out) + "\n"


def has_author(text):
    """Is there an `Author:` line in the opening block?"""
    head = "\n".join(text.split("\n")[:25])
    return "Author:" in head


def added_files(repo):
    """Staged files that are *new*. Only these must carry an `Author:` line."""
    try:
        r = subprocess.run(["git", "diff", "--cached", "--name-only",
                            "--diff-filter=A"],
                           cwd=repo, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return set()
    return {os.path.join(repo, p) for p in r.stdout.split("\n") if p.strip()}


def has_header(text):
    """A header is present if the Apache grant and the holder both appear in the
    opening block. Deliberately not an exact-match test: an existing file may
    carry a different year or author, and neither is a defect."""
    head = "\n".join(text.split("\n")[:25])
    return ("Licensed under the Apache License" in head
            and HOLDER in head)


def git_identity(repo):
    def cfg(key):
        try:
            r = subprocess.run(["git", "config", "--local", "--get", key],
                               cwd=repo, capture_output=True, text=True,
                               timeout=5)
        except (OSError, subprocess.SubprocessError):
            return ""
        return r.stdout.strip() if r.returncode == 0 else ""
    return cfg("user.name"), cfg("user.email")


def staged_files(repo):
    try:
        r = subprocess.run(["git", "diff", "--cached", "--name-only",
                            "--diff-filter=ACM"],
                           cwd=repo, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return []
    return [os.path.join(repo, p) for p in r.stdout.split("\n") if p.strip()]


def walk(root):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            yield os.path.join(base, name)


def insert(path, marker, year, name, email):
    """Write the header above the existing content, below any shebang."""
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    lines = text.split("\n")
    prefix = []
    # A shebang, and an XML/encoding declaration, stay above the header.
    if lines and lines[0].startswith("#!"):
        prefix.append(lines.pop(0))
    header = header_text(marker, year, name, email)
    body = "\n".join(lines).lstrip("\n")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(("\n".join(prefix) + "\n" if prefix else "")
                 + header + "\n" + body)
    return True


def _add_author(repo, candidates, args):
    """Stamp `Author:` onto files that already carry a header without one.

    Used when a file's authorship is established after the header was written
    -- the inherited-vs-authored question answered the other way. It only ever
    *adds* a line; a file that already names an author is left alone.
    """
    name, email = git_identity(repo)
    if not name or not email:
        print("license-header: --author-only needs a local git identity.\n"
              "  git config --local user.name  \"<Name>\"\n"
              "  git config --local user.email \"<name>@robotis.com\"",
              file=sys.stderr)
        return 2
    touched = 0
    for path in candidates:
        if not os.path.isfile(path):
            continue
        if any(part in SKIP_DIRS for part in path.split(os.sep)):
            continue
        marker = marker_for(path)
        if marker is None:
            continue
        try:
            with open(path, "r", encoding="utf-8") as fh:
                text = fh.read()
        except (UnicodeDecodeError, OSError):
            continue
        if not has_header(text) or has_author(text):
            continue
        lines = text.split("\n")
        # The header ends at the last consecutive comment line of the block;
        # append the author two lines below "limitations under the License."
        end = None
        for i, line in enumerate(lines[:25]):
            if "limitations under the License." in line:
                end = i
                break
        if end is None:
            continue
        lines.insert(end + 1, marker)
        lines.insert(end + 2, f"{marker} Author: {name} <{email}>")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        touched += 1
        print(f"  ~ {os.path.relpath(path, repo)}")
    print(f"\nlicense-header: added Author to {touched} file(s) "
          f"as {name} <{email}>.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fix", action="store_true",
                    help="insert the header where it is missing")
    ap.add_argument("--staged", action="store_true",
                    help="check only files staged for commit")
    ap.add_argument("--author-only", action="store_true",
                    help="add the Author: line to files that already carry a "
                         "header but no author -- used once, when the author "
                         "of existing files is established")
    ap.add_argument("--no-author", action="store_true",
                    help="omit the Author: line -- for backfilling inherited "
                         "files this team did not write")
    ap.add_argument("--year", default=None,
                    help="copyright year for inserted headers "
                         "(default: current year; never bump an existing one)")
    ap.add_argument("paths", nargs="*", help="files or directories to check")
    args = ap.parse_args()

    repo = os.getcwd()
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=repo,
                           capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            repo = r.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass

    if args.staged:
        candidates = staged_files(repo)
    elif args.paths:
        candidates = []
        for p in args.paths:
            candidates.extend(walk(p) if os.path.isdir(p) else [p])
    else:
        candidates = list(walk(repo))

    if args.author_only:
        return _add_author(repo, candidates, args)

    added = added_files(repo) if args.staged else set()
    missing = []
    authorless = []
    for path in candidates:
        if not os.path.isfile(path):
            continue
        if any(part in SKIP_DIRS for part in path.split(os.sep)):
            continue
        marker = marker_for(path)
        if marker is None:
            continue
        try:
            with open(path, "r", encoding="utf-8") as fh:
                text = fh.read()
        except (UnicodeDecodeError, OSError):
            continue
        if not has_header(text):
            missing.append((path, marker))
        elif path in added and not has_author(text):
            # A file this commit introduces is authored by the committer, and
            # the Author line is the only place that is recorded.
            authorless.append(path)

    if not missing and not authorless:
        print("license-header: OK — every checked file carries the header.")
        return 0

    if authorless and not args.fix:
        print(f"license-header: {len(authorless)} new file(s) carry the "
              f"header but no `Author:` line. A file you are adding must name "
              f"its author:\n")
        for path in authorless:
            print(f"  {os.path.relpath(path, repo)}")
        if not missing:
            return 1
        print()

    if not args.fix:
        print(f"license-header: {len(missing)} file(s) missing the "
              f"Apache 2.0 / {HOLDER} header:\n")
        for path, _ in missing:
            print(f"  {os.path.relpath(path, repo)}")
        print("\nInsert with:  python3 claude-harness/scripts/"
              "check_license_header.py --fix")
        return 1

    if args.no_author:
        name, email = "", ""
    else:
        name, email = git_identity(repo)
    if not args.no_author and (not name or not email):
        print("license-header: refusing to --fix. The repository has no local "
              "git identity, and `Author:` must name the actual author.\n"
              "  git config --local user.name  \"<Name>\"\n"
              "  git config --local user.email \"<name>@robotis.com\"",
              file=sys.stderr)
        return 2

    year = args.year or __import__("datetime").date.today().year
    for path, marker in missing:
        insert(path, marker, year, name, email)
        print(f"  + {os.path.relpath(path, repo)}")
    who = f"as {name} <{email}>" if name else "with no Author line"
    print(f"\nlicense-header: inserted {len(missing)} header(s) "
          f"{who}, © {year} {HOLDER}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
