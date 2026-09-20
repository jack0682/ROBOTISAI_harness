# sessions/ — short-term working memory

A **session** captures the here-and-now of a single working unit. Projects hold
long-term context; sessions hold what's happening right now and let work resume
after a break or a context reset.

> Kernel = what doesn't change. Project = what changes. Session = what's happening
> right now.

## Layout
- `active/` — worklogs for in-flight work. The hook layer reads these (latest
  worklog → injected at session start; the stop gate checks one was written).
- `archived/` — retired worklogs, kept for history (not resume targets).
- `distilled/` — distillation outputs: what a session taught, before it's promoted
  to `memory/` or a skill (`modes/memory.md`).
- `_session_template.md`, `README.md` stay at the top level.

## Contract
- One file per session: `active/<date>_<short-slug>.md`
  (e.g. `active/2026-06-05_harness_design.md`).
- Built from `_session_template.md`.
- For long tasks, a session accumulates checkpoints (`templates/checkpoint.md`).
- At close, run the **distillation review** (the template's last section,
  `modes/memory.md`): decide what — if anything — becomes memory or a skill patch.
  "Nothing worth persisting" is a valid, common result.

## Creating a session
```bash
python3 scripts/new_session.py --project my-project --task coding --date 2026-06-05
```

## On resuming
Read the latest active worklog first. Reconcile its recorded state with reality,
and re-verify any named files/flags/APIs before relying on them.

## Retiring / distilling
- Done with a worklog → `git mv active/<f> archived/`.
- Captured a reusable lesson → write it to `distilled/`, then promote it to
  `memory/` or a skill via the action ladder (`skills/README.md`).
