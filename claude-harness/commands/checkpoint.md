---
description: Write a control-flow checkpoint of the current long task into sessions/ so work continues or resumes deliberately.
argument-hint: [task label]
allowed-tools: [Read, Write, Bash]
---

Follow `claude-harness/protocols/long_task.md` and the checkpoint rules in
`claude-harness/kernel/execution_protocol.md`. Fill
`claude-harness/templates/checkpoint.md` and write it into
`claude-harness/sessions/<date>_<slug>.md`.

Task label (optional): $ARGUMENTS

A checkpoint is control flow, not a summary: record the trigger, current state
(done-and-verified / in-progress / pending), evidence, plan status,
decisions/assumptions, remaining unknowns, risks, the single next action, and
`Continue or stop` — which defaults to **continue**; stop only if the objective
is complete or a hard external blocker exists. Write so a fresh session could
continue from the checkpoint alone, then take the next action.
