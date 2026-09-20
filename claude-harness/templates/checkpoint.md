# Checkpoint <id>: <task> — <date>

Time: <ISO 8601, e.g. 2026-06-10T15:05+09:00 — lets tooling order checkpoints
regardless of their position in the file>

> A checkpoint is control flow, not a summary: it decides whether and how work
> continues. `Continue or stop` defaults to **continue** — stop only when the
> objective is genuinely complete or a hard external blocker exists. Triggers
> live in `kernel/execution_protocol.md`.

## Trigger
<Which checkpoint trigger fired (e.g. plan revised, before core edit, tempted
to stop early).>

## Active project
<project name, or none>

## Goal
<What this task is trying to achieve.>

## Current state
- **Done & verified:** <unit completed and how it was verified>
- **In progress:** <what's mid-flight, and its current state>
- **Pending:** <not yet started>

## Evidence gathered
<Key facts read/ran/measured since the last checkpoint, with sources.>

## Current hypothesis
<The working theory of how the goal will be reached, if not already settled.>

## Plan status
<on plan / revised (what changed, why, what evidence forced it) / blocked>

## Decisions & assumptions made
- <decision> — <reason>
- <assumption> — <verified? / to confirm>

## Remaining unknowns
<What is still unverified or undecided, and why it matters.>

## Risks
<What could invalidate the work or needs guarding.>

## Next action
<The single concrete next action. Mandatory unless the task is complete.>

## Continue or stop
continue <(default) — or: stop, because <objective complete | hard external
blocker: name it>>

## Resume notes
<Anything a fresh session needs: files to re-read, flags/APIs to re-verify.>
