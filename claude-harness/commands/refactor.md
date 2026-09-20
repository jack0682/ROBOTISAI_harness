---
description: Refactor code without changing behavior — improve clarity/structure, verify behavior is preserved.
argument-hint: <what to refactor>
allowed-tools: [Read, Grep, Glob, Edit, Bash]
---

Follow `claude-harness/protocols/coding.md` and `claude-harness/styles/code.md`,
with a behavior-preservation focus.

Target: $ARGUMENTS

Establish current behavior (and its tests) first. Make structural changes only;
no behavior change. Verify the same tests pass before and after (per
`claude-harness/protocols/validation.md`). Keep the diff focused — no
opportunistic unrelated edits.
