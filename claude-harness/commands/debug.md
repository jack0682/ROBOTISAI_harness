---
description: Debug a failure — reproduce, isolate, weigh competing hypotheses, root-cause, fix, verify.
argument-hint: <bug or failure description>
allowed-tools: [Read, Grep, Glob, Edit, Bash]
---

Follow `claude-harness/protocols/debugging.md`.

Problem: $ARGUMENTS

Reproduce before theorizing. Hold competing hypotheses with evidence for/against.
State root cause vs. workaround explicitly. Verify the fix against the original
reproduction and check for regressions (per
`claude-harness/protocols/validation.md`).
