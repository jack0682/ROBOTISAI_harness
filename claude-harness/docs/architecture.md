# Architecture

## One sentence

A small always-on **spine** (`KERNEL.md` + `ROUTING.md`) that dispatches each
request onto two axes — **modes** (cognitive operations) × **scopes** (domain
governance) — and loads everything deeper on demand, all in service of one
closed loop that tests whether a thought survives.

## The central loop

```
Thought → Claim → Definition → Mathematical Formulation → Consistency Check
   → Counterexample → Execution / Experiment / Implementation → Data / Result
   → Revision → Artifact → Memory / Skill Distillation
```

This is not a script to perform on every reply; it is the **map of where a thought
can fail**, so failure is found early. Each stage has a mode that executes it.

## Two axes

**modes/** — *what cognitive operation*, domain-independent. Each mode file is
`Trigger · Input · Operations · Output · Guardrails · Anti-patterns · Loop
position`. The output is the *fixed artifact* the stage must leave behind — this
is how the loop makes progress (`KERNEL.md` principle 5).

**scopes/** — *what domain* (math, research, writing, coding, experiments,
prompts). Each scope's `AGENTS.md` (ref5-style) is `Read first · Purpose ·
Contract · Local invariants · Guardrails · Verification · Anti-patterns` and
routes into the modes, protocols, and skills its domain prefers.

A task = one scope + a short chain of modes. Example (new theory):
`think → define → math_lock → counter → execute → audit → memory`.

## Layer stack (load order vs authority)

```
Spine        KERNEL.md, ROUTING.md         always on
Scopes       scopes/<domain>/AGENTS.md      on routing
Modes        modes/<op>.md                  on routing
Principles   kernel/*.md                    on demand (depth)
Procedure    protocols/*.md                 on demand
Styles       styles/*.md                    on demand
Skills       skills/<name>/SKILL.md         metadata first, body on demand
Memory       memory/                        durable knowledge
Project      projects/<name>/               overlay + explicit overrides
Session      sessions/active/               working memory
```

Loading is recency-based (spine first); **authority** is the reverse (spine wins).
Conflicts surface to the user. Full contract: `HARNESS.md`.

## Why "small kernel"

The always-on context the harness controls is the spine; the measured total is
~45 KB once the bridge, the session_start injection and 67 skill frontmatters
are counted (2026-09-10). Keeping the spine small (a) leaves attention
budget for the actual work, (b) makes the routing explicit rather than implicit in
a wall of always-loaded rules, and (c) means depth is paid for only when a task
needs it. The full constitutional texts still exist in `kernel/`; `KERNEL.md`
condenses them and points to them.

## Enforcement is mechanical, not just advisory

The markdown states obligations; the **hook layer** (`scripts/hooks/`, wired via
`.claude/settings.json`) enforces the checkable ones at runtime — session-start
context injection, an audit log of every edit and command, and a stop gate that
blocks ending after unlogged edits until a checkpoint exists. The harness also
verifies *itself*: `scripts/validate_harness.py` checks structure, registries,
cross-references, project-term leakage, and orphans. See `docs/design_principles.md`
for why this matters to this user, and `docs/ref_analysis.md` for what was borrowed.
