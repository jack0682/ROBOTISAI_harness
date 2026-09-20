---
name: harness-activate
description: Activate the layered Claude Harness. Use when the user asks to "use the harness", "load the harness", work under the harness, or load a project's harness context.
---

# Harness activation

This repository is governed by a layered Claude Harness rooted at `claude-harness/`.

When this skill triggers:

1. Read `claude-harness/HARNESS.md` for the layering contract and load order.
2. The kernel (`claude-harness/kernel/*.md`) is the constitution and is already imported via
   the repo `CLAUDE.md` — follow it first.
3. To work a specific project, run `/harness-load <project> [task_type]`, which
   assembles kernel → protocol → styles → skills → project context → latest session.
4. Respect the active project's `constraints.md` gates and any explicit
   `overrides/`. The kernel always wins unless a project marks an explicit override.

Preview what would load for a project/task:
`python3 claude-harness/scripts/collect_context.py <project> <task_type>`
