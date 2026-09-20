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

"""PreToolUse hook (matcher: Bash). The commit policy, enforced on the agent.

`.githooks/` already gates the human's commits. This gates the *agent's*, one
layer earlier, because a hook that runs inside `git commit` cannot stop a
`--no-verify` and cannot explain itself in a way the model will act on.

Three denials, all fail-closed:

1. **No signing identity.** `user.name` / `user.email` / `user.signingkey` must
   be set with `--local`. A repository-local identity is the point: ~/.gitconfig
   carries a personal identity that would otherwise be stamped, silently, onto
   a team commit.
2. **`--no-verify`.** Skipping the DCO and signature gate is a policy
   violation, not a convenience, so it is denied outright rather than asked.
3. **`commit.gpgsign` not true.** Every commit in this repository is signed.

These are denies, not asks: the standing instruction is that no commit happens
until the signing identity has been supplied by the user. An "ask" would let a
click through it, and a headless run cannot answer one at all.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _hooklib as H

# Same segmentation idea as kernel_guard: find the command word per segment so
# that `git` inside a filename, a comment, or a here-doc does not fire.
_SEGMENT_SPLIT = re.compile(r"\|\||&&|[;&|\n()`]|\bdo\b|\bthen\b|\belse\b|\{|\}")

_WRAPPERS = ("sudo", "command", "time", "nohup", "env", "exec")

# `git commit`, allowing global options in between: `git -C path commit`.
_GIT_COMMIT = re.compile(r"^git\b(?:\s+-[cC]\s+\S+|\s+--\S+(?:=\S+)?)*\s+commit\b")

_NO_VERIFY = re.compile(r"(?:^|\s)(?:--no-verify|-n)(?:\s|$)")

# An agent is a tool, not an author. This repository forbids crediting a model
# as a co-author, and the rule outranks the harness and this assistant's own
# attribution default -- so it is checked here, on the command the agent is
# about to run, as well as in .githooks/commit-msg.
_AI_COAUTHOR = re.compile(
    r"Co-authored-by:[^\n]*"
    r"(claude|anthropic|copilot|chatgpt|openai|gpt-\d|gemini|codex|cursor"
    r"|devin|aider|noreply@)", re.I)
_AI_FOOTER = re.compile(
    r"Generated with[^\n]*(Claude|Copilot|ChatGPT|Gemini)", re.I)


def _segments(command):
    for part in _SEGMENT_SPLIT.split(command or ""):
        part = part.strip()
        if part:
            yield part


def _strip_wrappers(segment):
    words = segment.split()
    index = 0
    while index < len(words):
        word = words[index].strip("\"'")
        if word in _WRAPPERS:
            index += 1
            continue
        if "=" in word and not word.startswith("-"):   # VAR=value prefix
            index += 1
            continue
        break
    return " ".join(words[index:])


def _commit_segments(command):
    """Every segment of this command line that runs `git commit`."""
    return [s for s in (_strip_wrappers(seg) for seg in _segments(command))
            if _GIT_COMMIT.match(s)]


def _git_config_local(key, cwd):
    try:
        out = subprocess.run(
            ["git", "config", "--local", "--get", key],
            cwd=cwd, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def _deny(reason, session_id, event):
    H.log_event(session_id, event, reason=reason[:160])
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))


_ASK_THE_USER = (
    "Ask the user for the signing identity and configure it before retrying:\n"
    "  git config --local user.name       \"<Name>\"\n"
    "  git config --local user.email      \"<name>@robotis.com\"\n"
    "  git config --local user.signingkey <GPG_KEY_ID>\n"
    "Do not guess these values and do not fall back to the global git identity."
)


def main():
    data = H.read_input()
    session_id = data.get("session_id", "")
    if data.get("tool_name") != "Bash":
        return 0

    command = (data.get("tool_input") or {}).get("command", "")
    commits = _commit_segments(command)
    if not commits:
        return 0

    cwd = data.get("cwd") or os.getcwd()

    if _AI_COAUTHOR.search(command) or _AI_FOOTER.search(command):
        _deny(("Commit blocked: the message credits an AI assistant as a "
               "co-author, or carries a tool's generated-with footer. An agent "
               "is a tool, not an author — authorship and the DCO attestation "
               "belong to the person who signed off.\n\n"
               "Remove the `Co-authored-by:` / `Generated with` line. **This "
               "rule overrides the harness and this assistant's own attribution "
               "default**; it is not negotiable and .githooks/commit-msg "
               "enforces it independently. Human co-authors are fine."),
              session_id, "commit_guard_ai_coauthor_deny")
        return 0

    for segment in commits:
        if _NO_VERIFY.search(segment):
            _deny(("Commit policy: `--no-verify` bypasses the DCO sign-off and "
                   "GPG signature gate in .githooks/, which this repository "
                   "requires on every commit. That is a policy violation, not a "
                   "shortcut. Remove the flag and fix what the hook reports.\n"
                   "See CONTRIBUTING.md and "
                   f"{H.hdir_name()}/protocols/commit_policy.md."),
                  session_id, "commit_guard_no_verify_deny")
            return 0

    name = _git_config_local("user.name", cwd)
    email = _git_config_local("user.email", cwd)
    key = _git_config_local("user.signingkey", cwd)
    sign = _git_config_local("commit.gpgsign", cwd)

    missing = [label for label, value in
               (("user.name", name), ("user.email", email),
                ("user.signingkey", key)) if not value]
    if missing:
        _deny(("Commit blocked: this repository has no local signing identity "
               f"({', '.join(missing)} unset). Every commit here carries a DCO "
               "`Signed-off-by:` trailer and a GPG signature, and the identity "
               "must be set with --local so that a personal global git identity "
               "is never inherited onto a team commit.\n\n" + _ASK_THE_USER),
              session_id, "commit_guard_identity_deny")
        return 0

    if sign != "true":
        _deny(("Commit blocked: `commit.gpgsign` is not true in this "
               "repository, so the commit would be unsigned.\n"
               "  git config --local commit.gpgsign true"),
              session_id, "commit_guard_gpgsign_deny")
        return 0

    # Identity is present; the .githooks gate owns the rest (sign-off trailer
    # matching, key availability, subject shape). Remind rather than block, so
    # the sign-off is not forgotten and then rejected at commit-msg time.
    if " -s" not in f" {command} " and "--signoff" not in command:
        H.log_event(session_id, "commit_guard_signoff_reminder")
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": (
                "Commit policy: this repository requires a DCO sign-off. Use "
                f"`git commit -s` — the trailer must read exactly "
                f"`Signed-off-by: {name} <{email}>` or .githooks/commit-msg "
                "will reject it."),
        }}))
    return 0


if __name__ == "__main__":
    raise SystemExit(H.safe(main))
