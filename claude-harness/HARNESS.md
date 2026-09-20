# HARNESS.md

This repository is **the ROBOTIS AI team's research operating system** — a shared
Claude Harness whose job is not to think for the team but to **test whether a
thought survives** theory, math, counterexample, experiment, code, and data, and
to fix what survives into an artifact. Full identity and the central loop:
`KERNEL.md`.

## Layers

```
Spine            (KERNEL.md, ROUTING.md)   ← always on: identity, central loop,
                                             non-negotiable principles, dispatch
        ↓ (ROUTING.md dispatches on two axes)
Scopes           (scopes/<domain>/AGENTS.md)  ← domain governance: invariants,
                                                 guardrails, the verification owed
Modes            (modes/<op>.md)            ← cognitive operations: input→op→output
        ↓ (scopes/modes route into the depth)
Principles       (kernel/*.md)              ← full constitutional texts, on demand
Procedure        (protocols/*.md)           ← per-task procedure
Styles           (styles/*.md)              ← output conventions
Skills           (skills/<name>/SKILL.md)   ← capability modules, metadata-first
Memory           (memory/)                  ← durable, reusable knowledge
Project          (projects/<name>/)         ← project-local context & overrides
Session          (sessions/active/)         ← the here-and-now working memory
```

The central loop the layers serve: `Thought → Claim → Definition → Math →
Consistency → Counterexample → Execution → Data → Revision → Artifact →
Distillation` (`KERNEL.md`).

## Two hard rules

1. **The kernel must never know about any specific project.** No domain names,
   repository names, filenames, or project jargon in `KERNEL.md`, `ROUTING.md`,
   `kernel/`, `modes/`, `scopes/`, `protocols/`, or `styles/` (enforced by the
   leakage guard in `scripts/validate_harness.py`).
2. **A project may add or constrain, but never silently override the kernel.**
   Any deviation lives in `projects/<name>/overrides/*.md`, explicitly marked
   with the base rule it overrides and a reason. A project may never weaken the
   kernel's safety, verification, calibration, checkpoint, or long-horizon rules.

## Conflict resolution (authority order)

1. spine + `kernel/` — always wins, except where an explicit project override is
   allowed;
2. explicit `projects/<name>/overrides/*.md` — for that project only;
3. `scopes/`, `modes/`, `protocols/`, `styles/`;
4. project context (`PROJECT.md`, `context.md`, `constraints.md`, `local_rules.md`);
5. `sessions/` — facts about current work, never new rules.

Loading order is recency-based (spine first, project/session last); **authority**
order is the reverse. An unresolvable conflict is surfaced, never silently picked.

## Default load order

1. spine: `KERNEL.md`, `ROUTING.md` (auto-loaded via the bridge `CLAUDE.md`)
2. `ROUTING.md` classifies → the matching `scopes/<domain>/AGENTS.md`
3. the modes the task needs: `modes/<op>.md`
4. depth as needed: `kernel/<principle>.md`, `protocols/<task>.md`,
   `styles/<style>.md`
5. relevant `skills/<name>/SKILL.md` (metadata first, body on demand)
6. `memory/MEMORY.md` (+ the items it indexes) for durable context
7. project overlay: `projects/<name>/{PROJECT,context,constraints,local_rules}.md`,
   `projects/<name>/overrides/*.md`
8. latest worklog: `sessions/active/<current>.md`

`/harness-load <project> [task_type]` assembles the project/task slice; preview
with `python3 scripts/collect_context.py <project> <task_type>`.

## Native integration

A thin bridge in the repository root makes the harness load in Claude Code; the
harness is the single source of truth and the bridge is fully generated
(idempotent). Topology: Claude launches in the harness repo so the bridge
auto-loads; the harness is self-contained by default, and may optionally govern an
external working tree (`bridge.workspace_relative` in `harness.config.yaml`).

- `../CLAUDE.md` — auto-loaded; `@`-imports the **spine** (`KERNEL.md` +
  `ROUTING.md`) into every session. Depth loads on demand.
- `../.claude/commands/harness-{init,load,checkpoint}.md` — slash commands.
- `../.claude/skills` — a **relative symlink to `skills/`**, so every registered
  skill (with its full payload) activates with no copy/mirror (`_link_skills` in
  `scripts/install_bridge.py`). Includes `harness-activate`.
- `../.claude/settings.json` — the **hook enforcement layer** (merged, never
  clobbered): the runtime, not the model, injects the latest worklog's Next
  Step/checkpoint at session start and after compaction; **surfaces a routing hint
  — the likely scope/mode to load — on each user prompt** (`route_hint.py`, closing
  the on-demand-loading gap); audit-logs every file modification **and Bash command** (`sessions/.audit.log`, gitignored); reminds
  on the first edit to apply `protocols/validation.md`; blocks the first stop
  after unlogged edits until a checkpoint is written (and, when the project
  declares `validation.commands`, until a matching command actually ran); and
  escalates kernel edits (plus destructive Bash when a project sets
  `allow_file_deletion: false`) to explicit confirmation. Hooks self-log their
  actions, so a silent failure shows in the data. Scripts: `scripts/hooks/`;
  compliance report: `python3 scripts/audit_session.py`.

Regenerate the bridge: `python3 scripts/install_bridge.py`. Validate structure:
`python3 scripts/validate_harness.py`. Distillation review at session close:
`python3 scripts/distill_session.py` (`modes/memory.md`).

**Template adoption.** This harness is a Claude-only template meant to be cloned
into a workspace. After cloning, run `python3 scripts/detach_for_workspace.py
--apply` to sever the template's git origin (removing the clone's `.git`),
regenerate the bridge into the workspace, and validate — the harness then governs
that workspace with no dependency on the template. Dry-run is the default; run it
in the clone, never in the source template.

**Standing autonomy mandate.** Whenever the harness is loaded, every session runs
under `kernel/autonomy_mandate.md` — a standing authorization to work at maximum
depth and persistence (unlimited tools/subagents/search/reasoning/budget; no early
stop; no shallow simplification). It raises the effort bar without waiving any
safety/verification/calibration gate, and is injected mechanically by the
`session_start` hook so it survives compaction and fresh sessions.
