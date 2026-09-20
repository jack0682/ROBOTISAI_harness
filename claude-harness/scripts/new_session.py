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

"""Start a new session log from sessions/_session_template.md.

Usage:
    python3 scripts/new_session.py [--project P] [--task T] [--date YYYY-MM-DD] [--slug S]

Creates sessions/<date>_<slug>.md with the Date / Active Project / Task fields
pre-filled. --date defaults to today; pass it explicitly for reproducible runs.
"""

from __future__ import annotations

import argparse
import datetime
import os
import sys

import _common as C


def main(argv=None):
    ap = argparse.ArgumentParser(description="Create a new session log.")
    ap.add_argument("--project", default="", help="Active project name.")
    ap.add_argument("--task", default="", help="Short task description.")
    ap.add_argument("--date", default="", help="YYYY-MM-DD (defaults to today).")
    ap.add_argument("--slug", default="", help="Filename slug (defaults from task).")
    args = ap.parse_args(argv)

    date = args.date or datetime.date.today().isoformat()
    slug = C.slugify(args.slug or args.task or "session")
    fname = f"{date}_{slug}.md"
    # Active worklogs live in sessions/active/; archived/ and distilled/ hold
    # retired logs and distillation outputs (sessions/README.md).
    os.makedirs(C.rpath("sessions", "active"), exist_ok=True)
    dst = C.rpath("sessions", "active", fname)
    if os.path.exists(dst):
        print(f"error: session already exists: sessions/active/{fname}",
              file=sys.stderr)
        return 1

    with open(C.rpath("sessions", "_session_template.md"), "r", encoding="utf-8") as fh:
        content = fh.read()

    content = content.replace("<YYYY-MM-DD>", date)
    if args.project:
        content = content.replace("<project name, or none>", args.project)
    if args.task:
        content = content.replace("<What this session is working on.>", args.task)

    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(content)

    print(f"Created session sessions/active/{fname}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
