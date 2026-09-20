---
description: Implement a change — read first, smallest correct edit, reuse existing patterns, verify for real.
argument-hint: <what to implement>
allowed-tools: [Read, Grep, Glob, Edit, Write, Bash]
---

Follow `claude-harness/protocols/coding.md` and `claude-harness/styles/code.md`.
Report using `claude-harness/templates/implementation_report.md`.

Task: $ARGUMENTS

Read the target files and surrounding code before editing. Make the minimal change.
Run/verify it and report the real result — validate per
`claude-harness/protocols/validation.md` before reporting. Respect the active
project's `constraints.md` gates.
