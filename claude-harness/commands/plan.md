---
description: Plan a task before acting — frame the goal, gather context, surface decisions, sequence verifiable steps.
argument-hint: <what to plan>
allowed-tools: [Read, Grep, Glob, Agent]
---

Follow `claude-harness/protocols/planning.md`. Produce the plan using
`claude-harness/templates/plan.md`.

Task to plan: $ARGUMENTS

Read relevant material first, reuse existing patterns, recommend a single approach,
and end with an end-to-end verification section. Ask the user only about decisions
genuinely theirs to make.
