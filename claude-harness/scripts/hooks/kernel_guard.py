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

"""PreToolUse hook (matcher: Edit|Write|MultiEdit|NotebookEdit|Bash).

Guards that escalate to permissionDecision "ask" interactively (the user stays
the authority) — except the distillation sandbox, which "deny"s because a
headless run cannot answer an ask:

1. Kernel guard — edits to the harness constitution (kernel/*.md) bind every
   future session and must never slip through on auto-accept. Fail-closed: an
   edit-tool call whose target cannot be resolved is asked, not allowed.
2. Deletion guard — when the single active project's config sets
   `constraints.allow_file_deletion: false`, destructive-looking Bash
   commands (rm/rmdir/unlink/shred) outside /tmp get a confirmation.
3. Distillation sandbox — under HARNESS_DISTILL=1 the write surface is
   memory/ + sessions/distilled/ only; anything else (or an unresolvable
   target) is denied.

Asks and denies are self-logged as events.
"""

from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _hooklib as H

# Shell commands that remove things, checked as the first word of a segment
# rather than by substring, so `rm` inside a filename or a comment does not fire
# and a leading space or a newline does not hide one.
_DESTRUCTIVE_COMMANDS = frozenset({"rm", "rmdir", "unlink", "shred", "srm"})

# Shapes that delete without `rm` being the command word.
_DESTRUCTIVE_PHRASES = (
    re.compile(r"\bfind\b.*?(?:-delete\b|-exec\s+(?:rm|shred|unlink)\b)", re.S),
    # `-(?!-)` so `git clean --dry-run` -- which removes nothing -- does not fire
    # on the `d` in `dry`. A gate that asks about safe commands gets clicked
    # through, which costs more than the case it was guarding.
    re.compile(r"\bgit\s+clean\b(?:\s+\S+)*?\s-(?!-)[a-zA-Z]*[fxd]", re.S),
    re.compile(r"\bxargs\b(?:\s+-\S+)*\s+(?:rm|rmdir|unlink|shred)\b"),
    re.compile(r"\btruncate\s+(?:-\S+\s+)*-s\s*0\b"),
    re.compile(r"\b(?:shutil\.rmtree|os\.removedirs|os\.unlink|os\.remove)\s*\("),
    re.compile(r"\.unlink\s*\(\s*\)"),
    re.compile(r"\bmv\b[^;&|]*\s/dev/null\b"),
)

# Where one shell command ends and the next begins, including the keywords that
# open a loop or conditional body. `for f in *; do rm $f; done` hid behind the
# `do` for as long as this was a single anchored pattern.
_SEGMENT_SPLIT = re.compile(r"\|\||&&|[;&|\n()`]|\bdo\b|\bthen\b|\belse\b|\{|\}")


def _segments(command):
    for part in _SEGMENT_SPLIT.split(command or ""):
        part = part.strip()
        if part:
            yield part


def _first_word(segment):
    """The command word, skipping the wrappers that would otherwise hide it."""
    words = segment.split()
    index = 0
    while index < len(words):
        word = words[index].strip("\"'")
        if word in ("sudo", "command", "time", "nohup", "env", "exec", "xargs"):
            index += 1
            continue
        if "=" in word and not word.startswith("-"):   # VAR=value prefix
            index += 1
            continue
        return os.path.basename(word)
    return ""


def _is_destructive(command):
    """Does this shell command look like it removes something?

    Deliberately a confirmation gate, not a security boundary: a shell has
    unbounded ways to delete a file and no regex closes them all. It exists to
    catch the shapes that actually turn up, and the honest statement of its limit
    is that anything reaching a shell can still delete anything the user can.
    """
    if not command:
        return False
    if any(pattern.search(command) for pattern in _DESTRUCTIVE_PHRASES):
        return True
    return any(_first_word(segment) in _DESTRUCTIVE_COMMANDS
               for segment in _segments(command))


def _ask(reason, session_id, event):
    H.log_event(session_id, event, reason=reason[:160])
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": reason,
    }}))


def _deny(reason, session_id, event):
    H.log_event(session_id, event, reason=reason[:160])
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))


_EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")
# Both names are honoured. The neutral one is what the distiller sets now; the
# agent-named one kept a run already in flight from losing its sandbox, and was
# the only name this file ever read while the Codex distiller set a third.
_DISTILL_VARS = ("HARNESS_DISTILL", "CLAUDE_HARNESS_DISTILL")


def _distilling():
    return any(os.environ.get(name) == "1" for name in _DISTILL_VARS)


def _distill_guard(data, session_id, tool):
    """During an automated distillation run (HARNESS_DISTILL=1), the write
    surface is a hard sandbox: edits are allowed only under memory/ and
    sessions/distilled/. skills/ is intentionally excluded — a distiller proposes
    skill patches into sessions/distilled/ for human approval, never edits skills
    directly (modes/memory.md, docs/loop_and_distillation_design.md). Headless
    cannot answer an "ask", so this denies rather than escalates. Returns True if
    it emitted a decision."""
    # Neutral name, because this file is shared verbatim between the harnesses.
    # The old agent-named variable is still honoured so a distillation already in
    # flight does not lose its sandbox mid-run.
    if not _distilling() or tool not in _EDIT_TOOLS:
        return False
    path = H.edited_path(data.get("tool_input"))
    if not path:
        # Fail-closed in the hard sandbox: an unresolvable edit target cannot be
        # proven inside the allowed surface, so it must not slip through.
        _deny(("Distillation sandbox: could not resolve the edit target, so it "
               "cannot be confirmed within memory/ or sessions/distilled/. "
               "Write through an explicit path under one of those directories."),
              session_id, "distill_guard_ambiguous_deny")
        return True
    if not os.path.isabs(path):
        path = os.path.join(data.get("cwd") or os.getcwd(), path)
    target = os.path.realpath(path)
    root = os.path.realpath(H.harness_root())
    allowed = [os.path.join(root, "memory"),
               os.path.join(root, "sessions", "distilled")]
    if any(target == d or target.startswith(d + os.sep) for d in allowed):
        return False
    _deny(("Distillation runs in a sandbox: it may write only under memory/ and "
           "sessions/distilled/. Propose skill patches and anything else as text "
           "in sessions/distilled/ for human approval; do not edit it directly."),
          session_id, "distill_guard_deny")
    return True


def _deletion_outside_tmp(command):
    if not _is_destructive(command):
        return False
    paths = [t for t in command.split() if "/" in t and not t.startswith("-")]
    # Normalise before the prefix test: `/tmp/../etc` starts with "/tmp/" and is
    # not in /tmp. The check was a string comparison against an attacker-shaped
    # input, which is the whole family of bug this belongs to.
    if paths and all(_under_tmp(t) for t in paths):
        return False
    return True


def _under_tmp(token):
    path = os.path.normpath(token.strip("\"'"))
    return path == "/tmp" or path.startswith("/tmp/")


def main():
    data = H.read_input()
    session_id = data.get("session_id", "")
    tool = data.get("tool_name", "")

    # Distillation sandbox takes precedence — a hard write-surface boundary.
    if _distill_guard(data, session_id, tool):
        return 0

    if tool == "Bash":
        command = (data.get("tool_input") or {}).get("command", "")
        if _deletion_outside_tmp(command):
            proj = H.active_project()
            if proj and (proj[1].get("constraints") or {}).get(
                    "allow_file_deletion") is False:
                _ask((f"Project '{proj[0]}' sets allow_file_deletion: false "
                      "and this command looks destructive. Confirm it is "
                      "intended (and reversible, or explicitly authorized)."),
                     session_id, "deletion_guard_ask")
        return 0

    path = H.edited_path(data.get("tool_input"))
    if not path:
        # Fail-closed on ambiguity: an edit tool whose target we cannot read
        # cannot be cleared as "not a kernel edit". Normal Edit/Write always
        # carry a path, so this fires only on genuinely malformed input — ask
        # rather than silently allow a possible constitution edit.
        if tool in _EDIT_TOOLS:
            _ask(("Could not determine this edit's target, so it cannot be "
                  "cleared against the kernel-edit guard. Confirm it is not "
                  f"modifying the harness constitution ({H.hdir_name()}/kernel/)."),
                 session_id, "kernel_guard_ambiguous_ask")
        return 0
    if not os.path.isabs(path):
        path = os.path.join(data.get("cwd") or os.getcwd(), path)
    kernel_dir = os.path.realpath(os.path.join(H.harness_root(), "kernel"))
    target = os.path.realpath(path)
    if target.startswith(kernel_dir + os.sep) and target.endswith(".md"):
        rel = os.path.relpath(target, H.harness_root())
        _ask((f"This modifies the harness constitution "
              f"({H.hdir_name()}/{rel}). Kernel rules bind every future "
              "session — confirm deliberately."),
             session_id, "kernel_guard_ask")
    return 0


if __name__ == "__main__":
    raise SystemExit(H.safe(main))
