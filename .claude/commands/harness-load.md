---
description: Load the layered harness for a project and task — assembles kernel, protocol, skills, project context, and the latest session in load order.
argument-hint: <project> [task_type]
allowed-tools: [Read, Bash, Glob]
---

Load the harness context for the requested project and task, in this order (read
each file that exists):

1. `claude-harness/HARNESS.md`
2. `claude-harness/kernel/*.md` (the constitution)
3. `claude-harness/protocols/<task_type>.md` (omitted → the project's `protocols.default`,
   else the harness `defaults.protocols`), plus the project's `protocols.additional`
4. the project's default `claude-harness/styles/*.md`
5. required `claude-harness/skills/<skill>/SKILL.md` from the project config
6. `claude-harness/projects/<project>/PROJECT.md`, `context.md`, `constraints.md`, `local_rules.md`
7. `claude-harness/projects/<project>/overrides/*.md`
8. the latest file in `claude-harness/sessions/`

Arguments: $ARGUMENTS

You can preview the exact ordered file list with:
`python3 claude-harness/scripts/collect_context.py <project> <task_type>`
(add `--show` to dump contents). Honor the project's `constraints.md` gates. The
kernel always wins over project rules unless a project marks an explicit override.
For work spanning many steps or sessions, also read `claude-harness/protocols/long_task.md`;
before claiming completion, apply `claude-harness/protocols/validation.md`.
