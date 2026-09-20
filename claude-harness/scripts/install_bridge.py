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

"""Generate the native Claude Code bridge for the harness.

Claude Code does not auto-load an arbitrary directory of markdown. This writes a
thin bridge in the repo root so the harness actually loads:

  <root>/CLAUDE.md                              auto-loaded; @-imports the kernel
  <root>/.claude/commands/harness-load.md       /harness-load <project> [task_type]
  <root>/.claude/commands/harness-checkpoint.md /harness-checkpoint
  <root>/.claude/skills -> ../<hdir>/skills      symlink: every registered skill
                                                 (incl. harness-activate) is served
                                                 from the harness skills/ layer — no copy
  <root>/.claude/settings.json                  hook layer (merged, not clobbered)

The hook layer wires the runtime to the kernel's obligations: session-start
context injection, post-edit audit + validation reminder, a stop gate that
demands a checkpoint, and a confirmation guard on kernel edits. Hook scripts
live in scripts/hooks/ (stdlib only).

Re-running is safe. The bridge body is fully generated and replaced;
settings.json is merged (harness-managed hook entries are replaced, anything
user-defined is preserved); and a leading `<!-- NAME:BEGIN -->...<!-- NAME:END -->`
region installed by another tool is carried across rather than truncated.

Usage:
    python3 scripts/install_bridge.py
"""

from __future__ import annotations

import os
import re

import _common as C


def main(argv=None):
    config = C.load_config()
    bridge = config.get("bridge", {})
    harness_dir = os.path.basename(C.harness_root())  # e.g. "claude-harness"
    root = os.path.abspath(C.rpath(bridge.get("root_relative", "..")))

    written = []
    written.append(_write_claude_md(root, harness_dir, config))
    written.append(_write_harness_load(root, harness_dir))
    written.append(_write_harness_checkpoint(root, harness_dir))
    written.append(_write_harness_init(root, harness_dir))
    written.append(_write_activate_skill(root, harness_dir))
    written.append(_write_settings(root, harness_dir))
    written.append(_ensure_gitignore(root, harness_dir))
    written.extend(_link_skills(root))
    written.extend(_write_scope_rules(root, harness_dir))

    print(f"Bridge installed under {root}")
    for w in written:
        if w:
            print(f"  - {os.path.relpath(w, root)}")
    return 0


def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)


# A leading `<!-- NAME:BEGIN --> ... <!-- NAME:END -->` region belongs to whoever
# installed it. The harness does not need to know what NAME means -- only that
# regenerating its own bridge must not delete someone else's.
_FOREIGN_REGION_RE = re.compile(
    r"\A(\s*<!--\s*([A-Za-z0-9_-]+):BEGIN\s*-->.*?<!--\s*\2:END\s*-->\s*)",
    re.DOTALL,
)


def _foreign_prefix(path):
    """Any marked region another installer owns at the top of an existing file.

    `_write` truncates, which is correct for a fully generated file and was
    silently wrong for this one: the live CLAUDE.md carries 68 lines of co-work
    governance above the bridge, installed by a different tool, and every
    regeneration deleted it. The co-work installer re-applied it afterwards, so
    the coupling held only as long as someone remembered the order.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            existing = fh.read()
    except OSError:
        return ""
    match = _FOREIGN_REGION_RE.match(existing)
    return match.group(1) if match else ""


def _write(path, content, keep_foreign_regions=False):
    _ensure_dir(os.path.dirname(path))
    if keep_foreign_regions:
        prefix = _foreign_prefix(path)
        if prefix and not _FOREIGN_REGION_RE.match(content):
            content = prefix + content.lstrip("\n")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return path


def _write_claude_md(root, hdir, config):
    # The bridge imports only the always-on spine: KERNEL.md (the condensed
    # constitution + central loop + non-negotiable principles) and ROUTING.md
    # (request → scope × mode × skill dispatcher). Everything deeper — kernel/
    # (full principle texts), modes/, scopes/, protocols/, skills/, memory/ —
    # is loaded on demand via ROUTING.md. Small always-on surface by design.
    ws = config.get("bridge", {}).get("workspace_relative", "..")
    lines = [
        "# Project memory — claude-harness bridge",
        "",
        "> Auto-generated by `claude-harness/scripts/install_bridge.py`. Do not edit",
        "> by hand — edit the harness and regenerate.",
        "",
        "This repository operates under a layered Claude Harness — the ROBOTIS",
        "AI team's shared research operating system. The always-on spine is",
        "imported below; it states who the harness is, the loop it runs, the",
        "non-negotiable principles, and then routes to the depth on demand.",
        "",
        "## Spine (always active)",
        "",
        f"@{hdir}/KERNEL.md",
        f"@{hdir}/ROUTING.md",
        "",
        "## How loading works",
        "",
        f"`KERNEL.md` is the constitution; `ROUTING.md` dispatches each request to",
        "the right depth on two axes:",
        "",
        f"- **scope** = the work's domain → `{hdir}/scopes/<domain>/AGENTS.md`",
        "  (local invariants, guardrails, verification).",
        f"- **mode** = the cognitive operation → `{hdir}/modes/<op>.md` (think,",
        "  define, math_lock, verify, counter, execute, research, paper, prompt,",
        "  memory, audit, layer).",
        "",
        f"Deeper layers load only when needed: full principle texts in",
        f"`{hdir}/kernel/`, procedure in `{hdir}/protocols/`, capabilities in",
        f"`{hdir}/skills/`, durable knowledge in `{hdir}/memory/`.",
        "",
        "## Workspace topology",
        "",
        "Claude runs inside this repo. Harness state (modes, scopes, memory,",
        f"sessions, overrides) lives in `{hdir}/`. If a project governs an external",
        f"working tree, its `project.config.yaml` `workspace:` section records the",
        "exact root and key paths (default: this repo is self-contained).",
        "",
        "## Jurisdiction",
        "",
        "The harness governs **methodology and output standards** — how work is",
        "done, verified, checkpointed, and reported. The platform and any installed",
        "plugins govern **tool behavior**. When an external instruction (plugin,",
        "platform default) conflicts with a harness rule, apply the stricter rule",
        "and surface the conflict to the user instead of silently picking a side.",
        "",
        "## Committing — team standing rules, above the harness",
        "",
        "These outrank the harness, the platform defaults, and any assistant's",
        "own attribution behaviour. Enforced by `.githooks/` and by",
        f"`{hdir}/scripts/hooks/commit_guard.py`; full text in",
        f"`{hdir}/protocols/commit_policy.md`.",
        "",
        "- **Never credit an AI as a co-author.** No `Co-authored-by:` naming",
        "  Claude, Anthropic, Copilot, ChatGPT, Gemini, Codex, Cursor, Devin or",
        "  Aider, and no `Generated with <tool>` footer. An agent is a tool, not",
        "  an author. Human co-authors are fine.",
        "- **Every commit carries a DCO `Signed-off-by:` and a GPG signature.**",
        "  The signing identity is set `--local`, never inherited from a global",
        "  git config.",
        "- **Ask the user for the signing name, email and GPG key** before the",
        "  first commit. Never guess them, never substitute a global identity.",
        "- `--no-verify` is a policy violation, not a shortcut.",
        "",
        "## Loading more of the harness",
        "",
        f"- Entry point and full load order: `{hdir}/HARNESS.md`",
        "- To work a specific project + task, run `/harness-load <project> [task_type]`.",
        "- To checkpoint long work, run `/harness-checkpoint`.",
        "",
        "Project-specific harnesses may add constraints and context, but must not",
        "silently override the kernel — only explicit, marked overrides under a",
        f"project's `overrides/` are allowed (`{hdir}/HARNESS.md`).",
        "",
    ]
    return _write(os.path.join(root, "CLAUDE.md"), "\n".join(lines),
                  keep_foreign_regions=True)


def _write_harness_load(root, hdir):
    content = f"""---
description: Load the layered harness for a project and task — assembles kernel, protocol, skills, project context, and the latest session in load order.
argument-hint: <project> [task_type]
allowed-tools: [Read, Bash, Glob]
---

Load the harness context for the requested project and task, in this order (read
each file that exists):

1. `{hdir}/HARNESS.md`
2. `{hdir}/kernel/*.md` (the constitution)
3. `{hdir}/protocols/<task_type>.md` (omitted → the project's `protocols.default`,
   else the harness `defaults.protocols`), plus the project's `protocols.additional`
4. the project's default `{hdir}/styles/*.md`
5. required `{hdir}/skills/<skill>/SKILL.md` from the project config
6. `{hdir}/projects/<project>/PROJECT.md`, `context.md`, `constraints.md`, `local_rules.md`
7. `{hdir}/projects/<project>/overrides/*.md`
8. the latest file in `{hdir}/sessions/`

Arguments: $ARGUMENTS

You can preview the exact ordered file list with:
`python3 {hdir}/scripts/collect_context.py <project> <task_type>`
(add `--show` to dump contents). Honor the project's `constraints.md` gates. The
kernel always wins over project rules unless a project marks an explicit override.
For work spanning many steps or sessions, also read `{hdir}/protocols/long_task.md`;
before claiming completion, apply `{hdir}/protocols/validation.md`.
"""
    return _write(os.path.join(root, ".claude", "commands", "harness-load.md"), content)


def _write_harness_checkpoint(root, hdir):
    content = f"""---
description: Write a control-flow checkpoint of the current long task into the harness sessions/ so work continues or resumes deliberately.
argument-hint: [task label]
allowed-tools: [Read, Write, Bash]
---

Follow `{hdir}/protocols/long_task.md` and the checkpoint rules in
`{hdir}/kernel/execution_protocol.md`. Fill `{hdir}/templates/checkpoint.md` and
write it into `{hdir}/sessions/<date>_<slug>.md` (or create the session via
`python3 {hdir}/scripts/new_session.py --task "..."`).

Task label (optional): $ARGUMENTS

A checkpoint is control flow, not a summary: record the trigger, current state
(done-and-verified / in-progress / pending), evidence, plan status,
decisions/assumptions, remaining unknowns, risks, the single next action, and
`Continue or stop` — which defaults to **continue**; stop only if the objective
is complete or a hard external blocker exists. Write so a fresh session could
continue from the checkpoint alone, then take the next action.
"""
    return _write(
        os.path.join(root, ".claude", "commands", "harness-checkpoint.md"), content)


def _ensure_gitignore(root, hdir):
    """Make sure local agent/tool state never gets committed."""
    path = os.path.join(root, ".gitignore")
    lines = [".omc/", f"{hdir}/sessions/.audit.log", ".loop_heartbeat"]
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
        present = {l.strip() for l in content.splitlines()}
        missing = [l for l in lines if l not in present]
        if not missing:
            return None  # already covered
        return _write(path, content.rstrip("\n") + "\n" + "\n".join(missing) + "\n")
    return _write(path, "# Local agent/tool state — never commit.\n"
                  + "\n".join(lines) + "\n")


# Hook entries written into .claude/settings.json. Entries are recognized as
# harness-managed by this marker in their command string, so re-running the
# installer replaces them without touching user-defined hooks.
_HOOK_MARKER = "/scripts/hooks/"
_HOOK_SCRIPTS = (
    "session_start.py", "kernel_guard.py", "commit_guard.py", "post_edit.py",
    "pre_compact.py", "stop_gate.py", "route_hint.py",
)


def _is_ours(entry, root, hdir):
    """Is this settings.json hook entry one this harness installs?

    The old test was the bare substring `/scripts/hooks/`, which also matches a
    sibling harness -- `codex-harness/scripts/hooks/...` would have been deleted
    by a claude-harness install. It is harmless today only because the Codex
    bridge writes AGENTS.md and never touches settings.json.

    So: ours if it points into this harness, or into a harness directory that no
    longer exists (a rename left it behind, and a hook pointing at a missing file
    fails silently on every tool call). A sibling package that is present on disk
    is somebody else's and stays.
    """
    import json as _json

    text = _json.dumps(entry)
    if f"{hdir}{_HOOK_MARKER}" in text:
        return True
    for script in _HOOK_SCRIPTS:
        marker = f"{_HOOK_MARKER}{script}"
        index = text.find(marker)
        if index < 0:
            continue
        # `text[:index]` already ends immediately before `/scripts/hooks/`, so
        # the harness directory is its last path segment.
        prefix = text[:index].rsplit("/", 1)[-1]
        if prefix and not os.path.isdir(os.path.join(root, prefix)):
            return True
    return False


def _merge_hook_entries(existing, desired, root, hdir):
    """Replace our entries where they already sit; append only what is new.

    Appending unconditionally made every regeneration reorder the file --
    harness hooks to the end, foreign hooks to the front -- so running the
    installer and running the co-work installer each flipped it back. A file
    that oscillates is a file every deployment shows as dirty, and a dirty
    deployment cannot be updated by `git pull`.
    """
    remaining = list(desired)
    merged = []
    for entry in existing:
        if not _is_ours(entry, root, hdir):
            merged.append(entry)
            continue
        matcher = entry.get("matcher")
        replacement = next(
            (d for d in remaining if d.get("matcher") == matcher), None)
        if replacement is not None:
            remaining.remove(replacement)
            merged.append(replacement)
        # An entry of ours with no counterpart in `desired` is retired; drop it.
    return merged + remaining


def _hook_cmd(hdir, script):
    return f'python3 "$CLAUDE_PROJECT_DIR/{hdir}/scripts/hooks/{script}"'


def _write_settings(root, hdir):
    """Merge the harness hook layer into .claude/settings.json (idempotent).

    Project-scope hooks apply automatically and are committable, which is what
    turns the kernel's declared obligations (checkpoints, validation, session
    continuity) into runtime-enforced behavior. Existing non-harness settings
    and hooks are preserved.
    """
    import json

    path = os.path.join(root, ".claude", "settings.json")
    settings = {}
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                settings = json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"  ! skipping {path}: cannot parse existing file ({exc})")
            return None

    desired = {
        "SessionStart": [{
            "matcher": "startup|resume|compact",
            "hooks": [{"type": "command",
                       "command": _hook_cmd(hdir, "session_start.py")}],
        }],
        "PreToolUse": [{
            "matcher": "Edit|Write|MultiEdit|NotebookEdit|Bash",
            "hooks": [{"type": "command",
                       "command": _hook_cmd(hdir, "kernel_guard.py")}],
        }, {
            # Bash only: this one reads `git commit` off the command line.
            # It is separate from kernel_guard because the matchers differ and
            # because losing it silently -- which a reinstall did, once -- takes
            # the commit policy offline with no error anywhere.
            "matcher": "Bash",
            "hooks": [{"type": "command",
                       "command": _hook_cmd(hdir, "commit_guard.py")}],
        }],
        "PostToolUse": [{
            # Skill is here and not on PreToolUse: the record is of what ran,
            # and the kernel guard has nothing to decide about a skill call.
            "matcher": "Edit|Write|MultiEdit|NotebookEdit|Bash|Skill",
            "hooks": [{"type": "command",
                       "command": _hook_cmd(hdir, "post_edit.py")}],
        }],
        "PreCompact": [{
            "hooks": [{"type": "command",
                       "command": _hook_cmd(hdir, "pre_compact.py")}],
        }],
        "Stop": [{
            "hooks": [{"type": "command",
                       "command": _hook_cmd(hdir, "stop_gate.py")}],
        }],
        "UserPromptSubmit": [{
            "hooks": [{"type": "command",
                       "command": _hook_cmd(hdir, "route_hint.py")}],
        }],
    }
    hooks = settings.setdefault("hooks", {})
    for event, entries in desired.items():
        hooks[event] = _merge_hook_entries(
            hooks.get(event, []), entries, root, hdir)

    return _write(path, json.dumps(settings, indent=2, ensure_ascii=False) + "\n")


# Scopes whose work is identifiable from the file being touched. These get a
# path-scoped rule, which the platform fires on the file rather than on how the
# request happened to be worded -- the failure `route_hint` cannot cover, since a
# regex over the prompt never sees which file is open.
#
# math / research / writing / prompts are deliberately absent: their work is not
# tied to a path, a rule with no `paths:` loads unconditionally, and putting them
# here would grow the always-on surface to cover requests a rule cannot identify.
# They stay with ROUTING.md Step 2 and route_hint.
_SCOPE_RULES = {
    "coding": [
        "**/*.{py,ts,tsx,js,jsx,go,rs,c,h,cc,cpp,hpp,java,rb,sh}",
    ],
    "control": [
        "**/controllers/**", "**/control/**",
        "**/*controller*.{py,cpp,hpp,c,h}", "**/*.launch.py",
        "**/config/*.{yaml,yml}",
    ],
    "experiments": [
        "**/experiments/**", "**/*.ipynb", "**/train*.py", "**/eval*.py",
        "**/results/**",
    ],
}


# Mandatory team standards that fire on the file the same way a scope does, but
# are not scopes -- they are a house style every language file is held to. Kept
# separate from _SCOPE_RULES so that `scope-*.md` stays a 1:1 map onto scopes/.
_STANDARD_RULES = {
    "robotis-style": [
        "**/*.{c,h,cc,cpp,hpp,cxx,hxx,py,js,jsx,ts,tsx,css,scss,html}",
        "**/package.xml", "**/CMakeLists.txt", "**/setup.py", "**/setup.cfg",
        "**/plugin.xml", "**/CHANGELOG.rst",
        "**/*.{msg,srv,action}", "**/*.launch.py",
    ],
}


def _write_scope_rules(root, hdir):
    """Path-scoped reminders that the file in hand belongs to a scope.

    These do not restate the scope -- they name it. An `@` import would be
    expanded at launch, which would put the whole scope into the always-on
    surface and defeat the point of scoping it to a path.

    `_STANDARD_RULES` rides along: same mechanism, but it names a mandatory
    house standard (the ROBOTIS style guide) rather than a scope. Its body is
    hand-written and richer than a generated one, so a missing file is
    regenerated as a pointer and an existing file is never overwritten.
    """
    out = []
    base = os.path.join(root, ".claude", "rules")
    _ensure_dir(base)
    for name, globs in sorted(_STANDARD_RULES.items()):
        path = os.path.join(base, f"{name}.md")
        if os.path.isfile(path):
            out.append(None)
            continue
        paths = "\n".join(f'  - "{g}"' for g in globs)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(f"---\npaths:\n{paths}\n---\n\n"
                     f"# This file is governed by the `{name}` standard\n\n"
                     f"Load `{hdir}/skills/{name}/SKILL.md` before writing, "
                     "editing or reviewing this file, and the matching "
                     "`references/` document for its language. This is a team "
                     "standard, not a preference.\n")
        out.append(path)
    for scope, globs in sorted(_SCOPE_RULES.items()):
        path = os.path.join(base, f"scope-{scope}.md")
        if os.path.isfile(path):
            # Hand-edited rules are the author's, not the installer's.
            out.append(None)
            continue
        paths = "\n".join(f'  - "{g}"' for g in globs)
        body = (f"---\npaths:\n{paths}\n---\n\n"
                f"# This file belongs to the `{scope}` scope\n\n"
                f"Read `{hdir}/scopes/{scope}/AGENTS.md` before non-trivial "
                "work here — it owns the local invariants, the guardrails and "
                "the verification this scope owes.\n\n"
                "> This rule fires on the file, not on how the request was "
                f"worded. `{hdir}/ROUTING.md` Step 2 remains the authority on "
                "what to load.\n")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body)
        out.append(path)
    return out


def _link_skills(root):
    """Serve the harness skills/ layer at <root>/.claude/skills via a relative
    symlink, so every registered skill — with its full payload (scripts/,
    references/, ...) — auto-activates with no copy or mirror.

    Idempotent. If a real directory already sits at the link path, refuse and
    surface it rather than clobber user content (kernel rule 5)."""
    link = os.path.join(root, ".claude", "skills")
    hdir = os.path.basename(C.harness_root())
    target = os.path.join("..", hdir, "skills")  # relative to <root>/.claude/
    _ensure_dir(os.path.dirname(link))

    if os.path.islink(link):
        if os.readlink(link) == target:
            return [link]
        os.unlink(link)
    elif os.path.exists(link):
        raise SystemExit(
            f"error: {link} is a real directory, not the harness skills "
            f"symlink. Move its contents into {hdir}/skills/ and remove it, "
            "then re-run install_bridge.py.")
    os.symlink(target, link)
    return [link]


def _write_harness_init(root, hdir):
    # Mirrors the canonical commands/init.md, with paths bound to this harness dir.
    canonical = os.path.join(C.harness_root(), "commands", "init.md")
    with open(canonical, "r", encoding="utf-8") as fh:
        content = fh.read().replace("claude-harness/", f"{hdir}/")
    return _write(
        os.path.join(root, ".claude", "commands", "harness-init.md"), content)


def _write_activate_skill(root, hdir):
    content = f"""---
name: harness-activate
description: Activate the layered Claude Harness. Use when the user asks to "use the harness", "load the harness", work under the harness, or load a project's harness context.
---

# Harness activation

This repository is governed by a layered Claude Harness rooted at `{hdir}/`.

When this skill triggers:

1. Read `{hdir}/HARNESS.md` for the layering contract and load order.
2. The kernel (`{hdir}/kernel/*.md`) is the constitution and is already imported via
   the repo `CLAUDE.md` — follow it first.
3. To work a specific project, run `/harness-load <project> [task_type]`, which
   assembles kernel → protocol → styles → skills → project context → latest session.
4. Respect the active project's `constraints.md` gates and any explicit
   `overrides/`. The kernel always wins unless a project marks an explicit override.

Preview what would load for a project/task:
`python3 {hdir}/scripts/collect_context.py <project> <task_type>`
"""
    # harness-activate is a first-class harness skill: written into the source
    # skills/ layer, then served (with all others) through the .claude/skills
    # symlink created by _link_skills. `root` is unused but kept for signature
    # symmetry with the other _write_* bridge functions.
    return _write(
        C.rpath("skills", "harness-activate", "SKILL.md"),
        content,
    )


if __name__ == "__main__":
    raise SystemExit(main())
