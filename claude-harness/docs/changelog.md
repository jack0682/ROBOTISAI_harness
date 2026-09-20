# Changelog

## 0.3.0 — the loop stops instead of spinning; deployments can be updated (2026-09-10)


### co-work runtime
- **A state for "waiting on a person."** A pane holding a confirmation dialog
  fell through to a generic `TmuxError`, so the loop treated the one condition
  retrying cannot resolve as the one thing retrying is for. 6,178 of the 6,226
  ERROR lines in a two-week supervisor log were that, retried at the raw
  2-second poll, with no notification raised. `BlockedOnHuman` is reported once,
  marked on the heartbeat with its reason and start time, and waited on. It is
  deliberately neither an error nor progress, so real failures stay visible and
  nothing reads the stall as health.
- **`healthy` cannot be true while blocked**, and `cowork validate` fails a
  heartbeat that claims otherwise — the contradiction that let this run unseen.
- **A time bound on silence.** `InputNotReady` is swallowed because a busy agent
  frees itself in seconds; that reasoning expires when a TUI redesign makes every
  pane look permanently busy. `StalledNotReady` surfaces it.
- **The readiness contract is data.** `cowork/tmux/readiness.json`, versioned,
  with the previous in-code values as the fallback every malformed shape lands on.
- **Delivery outcomes are facts on disk** (`shared/.delivery-log`), one row per
  change of outcome, so "never attempted" and "attempted and failed, for this
  reason" survive state.json dropping its history.
- **Overflowed history is kept** (`shared/.history-archive`) instead of leaving
  `history_dropped` as a count of things nobody can look at. A live state
  reported 88 discarded task records.
- **Reads stop committing revisions.** `status`, `whose-turn`, `readiness` and
  `watch` no longer reconcile; neither do the supervisor-internal helpers whose
  pass already did, which removed several redundant inbox scans per poll.
- **A dead supervisor's artifacts are reaped**, except lock files (`flock`
  targets whose presence means nothing) and the pane map (the only record of the
  previous generation).

### distribution
- **`upgrade_harness.py` works and is safe.** It synced 17 files where 30 had
  changed on a three-month-stale deployment, and touched neither `KERNEL.md` nor
  `ROUTING.md` nor `modes/` nor `scopes/` — it upgraded a harness while leaving
  its constitution behind. What is universal is now declared once as
  `distribution:` in `harness.config.yaml` and read from the upstream side.
  Deleting local files is opt-in behind `--prune`.
- **A harness in use no longer dirties its own tree.** 123 dirty entries in the
  live deployment become 2. A dirty copy cannot be updated by `git pull`, which
  is how one repository became 35 divergent installs.
- **`fleet_survey.py`** — read-only census of every install, and which of its
  commits are absent from canonical.
- **The bridge installers stop deleting work they do not own.** Both truncated
  their bridge file, removing the co-work block another tool installs; running
  the Codex one removed 62 lines from `AGENTS.md`. A leading
  `<!-- NAME:BEGIN -->…<!-- NAME:END -->` region is now carried across.
  Hook entries are replaced in place rather than appended, so `settings.json`
  stops oscillating between the two installers.

### enforcement
- **`check.py`** runs every check in one command — both structure validators, the
  routing golden set, bridge drift, both test suites — and a GitHub workflow runs
  the same command. There had been 213 passing tests and nothing that ran them.
- **Stale worklogs are no longer injected.** Selection ranked by mtime, and `git
  checkout` rewrites mtimes, so for two months every session opened with a
  2026-07-11 checkpoint reading "Next action: commit (main) + push". Age now comes
  from the date in the filename.

### tests
197 → 252. New modules for `install_bridge`, `upgrade_harness` and worklog
freshness, none of which had any.

### versions
`harness.config.yaml` said 0.2.0, the changelog said 0.2.1, and both project
configs said 0.1.0. All now 0.3.0.

## 0.2.2 — skill right-sizing, autonomy mandate, routing obligation (2026-07-11)

Recorded here on 2026-09-10: this release shipped and was never written down,
which is why the entry below is reconstructed from git rather than from notes.
Session log: `sessions/archived/2026-07-11_harness-upgrade-p1-skill-prune.md`.

- **Skill library 105 → 68.** Variants archived to `_archive/skills/`; `INDEX.md`
  rewritten against the new mode/scope routing.
- **`kernel/autonomy_mandate.md`** — the standing authorization to work at full
  depth, added to `harness.config.yaml`'s `kernel:` list and injected every
  session by the `session_start` hook.
- **`scripts/hooks/route_hint.py`** — a `UserPromptSubmit` hook surfacing the
  likely scope and mode, closing the on-demand-loading gap where non-trivial
  domain work was answered from the spine alone.
- **`ROUTING.md` Step 2 became an obligation** rather than a suggestion.
- **`evaluation/{trigger,near_miss}_tests/cases.yaml`** — 30 golden routing cases,
  plus `check_routing_tests.py` to keep their targets live.
- **`scripts/detach_for_workspace.py`** — clone-as-template adoption.
- **`projects/nn-ai-theory/`** — the first real registered project.

## 0.2.1 — loop intelligence + distillation automation (2026-06-11)

Design: `docs/loop_and_distillation_design.md`. All extensions of existing scripts;
`validate_harness.py` stays 0/0.

- **`scripts/run_loop.py`** — mode-routed iterations; producer–reviewer cadence
  (`--review-every`, `--reviewer-model` — runs the ACCEPTANCE gate from a fresh
  vantage); completeness critic (`--critic-every`); stall detection → replan
  directive → `needs-input` stop; transient retry/backoff (rate-limit blips retry
  the same iteration); adaptive per-iteration timeout from a STATE `EST:` hint;
  `<mission_dir>/.loop_heartbeat`; `--distill-on-done`.
- **`templates/mission.md`** — STATE gains `MODE:` and `EST:`; `needs-input`
  status; 2h/30-iter default caps.
- **`scripts/distill_session.py`** — `--auto` spawns a sandboxed `claude -p`
  reviewer (launched at the bridge root so hooks fire); `--apply` lands memory
  items, default is proposal-only to `sessions/distilled/`; skill patches always
  proposals.
- **`scripts/hooks/kernel_guard.py`** — distillation sandbox: under
  `CLAUDE_HARNESS_DISTILL=1`, edits are **denied** outside `memory/` and
  `sessions/distilled/` (verified live: 2 escape attempts denied).
- **`scripts/validate_harness.py`** — memory items must carry `name:`/`scope:`
  frontmatter. **`install_bridge.py`** — `.loop_heartbeat` gitignored.
- **`protocols/long_loop.md`** — documents the new driver behavior + run command.

## 0.2.0 — research-OS refactor (2026-06-11)

Refactor of the harness from a task-routed governance framework into a
personal research operating system, centered on the loop *Thought → Claim →
Definition → Math → Consistency → Counterexample → Execution → Data → Revision →
Artifact → Distillation*.

### Added
- **Spine:** `KERNEL.md` (condensed constitution: identity, central loop, 6
  non-negotiable principles, output flexibility, memory guard, self-audit) and
  `ROUTING.md` (request → scope × mode × skill dispatcher). These are now the
  only always-on documents.
- **modes/** — 12 cognitive operations + README: `think, define, math_lock,
  verify, counter, execute, research, paper, prompt, memory, audit, layer`.
  `math_lock` carries the full consistency checklist (the centerpiece).
- **scopes/** — 6 domain-governance `AGENTS.md` (ref5 style): `math, research,
  writing, coding, experiments, prompts`.
- **memory/** — durable knowledge layer: `MEMORY.md` index + `decisions/`,
  `patterns/`, `project_states/`, `archived/`, with a frontmatter schema and the
  persistence guard (`memory/README.md`).
- **Distillation loop** — `modes/memory.md`, `scripts/distill_session.py`
  (evidence-grounded review scaffold), and a Distillation review section in the
  session template (ref6).
- **sessions/** split into `active/`, `archived/`, `distilled/`.
- **evaluation/** — `README.md` + `trigger_tests/` and `near_miss_tests/` with
  seed cases (ref2 should-trigger / should-NOT-trigger).
- **registry/** — `modes.yaml`, `scopes.yaml`.
- **docs/** — `architecture.md`, `design_principles.md`, `ref_analysis.md`, this
  changelog.

### Changed
- `kernel/` is renamed in role (not on disk): it now holds the **full principle
  texts loaded on demand**, condensed and pointed to by `KERNEL.md`. The bridge
  `CLAUDE.md` @-imports only the spine, not the 9 kernel files (small always-on
  surface).
- `harness.config.yaml` — version 0.2.0; layer list rewritten around the spine.
- `scripts/validate_harness.py` — now also checks `KERNEL.md`, `ROUTING.md`,
  the 12 modes, the 6 scope `AGENTS.md`, and the memory layer; leakage guard and
  md-ref checks extended to `modes/` and `scopes/`.
- `scripts/install_bridge.py` — bridge `CLAUDE.md` rewritten to import the spine
  and describe the two-axis routing.
- `scripts/new_session.py` and `scripts/hooks/_hooklib.py` — sessions now live in
  `sessions/active/` (top level still read for back-compat).
- `skills/README.md` — added the action-ladder growth governance and distillation
  anti-patterns (ref6).
- `HARNESS.md`, `README.md` — rewritten for the new architecture.

### Preserved (deliberately not changed)
- The hook enforcement layer (`scripts/hooks/`) and audit log — extended in path
  handling only; its checkpoint/validation gates are intact.
- The 105 skills of the time and the `codex-skills/` packages — format already matched the
  target; mass curation into umbrellas is deferred.
- `protocols/`, `styles/`, `templates/`, `projects/`, `commands/` — kept; scopes
  and modes route *into* them.

### Next (not done this pass)

Annotated 2026-09-10 — all four have since shipped, and reading this list as
outstanding work was misleading for two months.

- ~~Curate the skill library into umbrella skills; reconcile skill descriptions
  against the new mode/scope routing.~~ Done in 0.2.2 (105 → 68).
- ~~Automate the distillation review (currently protocol + scaffold).~~ Done in
  0.2.1, above — `distill_session.py --auto`.
- ~~Populate `evaluation/{trigger,near_miss}_tests/` from real routing
  mistakes.~~ Done in 0.2.2 (30 golden cases).
- ~~Register a first real project under `projects/`.~~ Done in 0.2.2
  (`nn-ai-theory`).

### Archived
- `sessions/2026-06-10_*.md` → `sessions/archived/`.
- Pre-refactor structure is recoverable via git history on `main`.
