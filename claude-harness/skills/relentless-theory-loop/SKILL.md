---
name: relentless-theory-loop
description: Sustained recursive inquiry for theory-building: objections, rival hypotheses, append-only lab notes across sessions. Triggers on \"keep digging\", \"continue the thread\", \"challenge assumptions\".
---

# Relentless Theory Loop

## Scope And Non-Scope
Use this skill for ongoing brainstorming and theory formalization, not for final book prose.

In scope:
- long-horizon conceptual research
- recursive question generation
- self-objection and falsification attempts
- rival hypothesis generation
- uncertainty-preserving logging
- continuation planning across sessions

Out of scope:
- polished publication chapters
- rhetorical style optimization for public audiences
- premature final conclusions that suppress unresolved tensions

If a user asks for polished prose while core theory questions remain open, finish the current research cycle first, preserve open problems in the log, then explicitly ask whether to switch modes.

## Core Behavioral Contract
For every reasoning cycle, produce all of the following:
- at least one deeper question
- at least one objection to the provisional answer
- at least one rival formulation/hypothesis
- at least one explicit next-step trigger question

Never treat a provisional answer as final truth.
Always keep failed paths, unresolved tensions, and contradictions visible.
Prefer rigorous structure over convenience, and prefer long-horizon continuity over neat one-shot completion.

## Required Operating Mode
Stay in theory-lab mode:
- analyze assumptions
- tighten definitions
- pressure-test causal claims
- identify what evidence would discriminate among rivals
- preserve epistemic uncertainty

Do not drift into book prose, narrative smoothing, or certainty theater.

## Log File Policy (Append-Only)
Use an append-only Markdown file for the research log.

Rules:
- never rewrite prior cycles to make them look cleaner
- never delete failed paths
- if a correction is needed, append a new cycle that explicitly references the older claim
- treat resolved vs unresolved status as an evolving state recorded across appended cycles

Default log path if user does not specify one:
- `research_log.md` in the current working directory

## Required Cycle Structure
When appending a cycle, use this structure in this order:

1. Current Problem
2. Why It Matters
3. Question
4. Provisional Answer
5. Objection
6. Rival View
7. Revision
8. Open Problems
9. Next Trigger Questions
10. Auto-Selected Next Question

Each cycle must preserve at least one unresolved element unless there is strong evidence that all tensions are actually resolved.

## Script Workflow
This skill uses `scripts/brainstorm_loop.py` for deterministic logging and continuity support.

### 1) Initialize Log (first use)
Run:
```bash
python scripts/brainstorm_loop.py init --log research_log.md --project "Foundational Research"
```

### 2) Append A Research Cycle
After each analysis pass, append one structured cycle:
```bash
python scripts/brainstorm_loop.py append-cycle \
  --log research_log.md \
  --current-problem "..." \
  --why-matters "..." \
  --question "..." \
  --provisional-answer "..." \
  --objection "..." \
  --rival-view "..." \
  --revision "..." \
  --open-problem "..." \
  --next-trigger "..."
```

Notes:
- pass `--objection`, `--rival-view`, `--open-problem`, and `--next-trigger` multiple times when needed
- if `--auto-selected-next` is omitted, the script selects one from trigger questions

### 3) Inspect Unresolved State
Before stopping or switching context:
```bash
python scripts/brainstorm_loop.py status --log research_log.md
```
This reports unresolved open problems, unresolved trigger questions, and a candidate next question.

### 4) Prepare Continuation Handoff
When ending a session, append a continuity block:
```bash
python scripts/brainstorm_loop.py continue-loop --log research_log.md --append-handoff
```
This extracts unresolved state, selects the strongest next trigger question, appends a handoff block, and prints a ready-to-use next-cycle prompt.

## Anti-Premature-Stopping Rule
Do not end with "done" if unresolved questions remain.
Instead:
- append the current cycle
- run `status`
- run `continue-loop --append-handoff`
- present the auto-selected next question and a concrete continuation trigger

Only stop without continuation when the user explicitly asks to stop.

## Interaction Guidance
When responding during this skill:
- maintain concise, technical language
- separate claims from confidence levels
- explicitly mark objections and rival hypotheses
- treat missing evidence as first-class research output

If uncertainty is high, increase structural rigor (clearer assumptions, cleaner rival decomposition, tighter trigger questions) rather than writing smoother prose.
