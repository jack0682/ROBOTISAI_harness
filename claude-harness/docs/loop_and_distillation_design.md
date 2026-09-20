# Loop intelligence, continuity, and distillation automation

Design for making the autonomous loop (`scripts/run_loop.py`) smarter and able to
run meaningfully for 1–2+ hours uninterrupted, plus automating the distillation
stage of the central loop. Builds on the existing design (`protocols/long_loop.md`):
many short fresh `claude -p` iterations over a durable on-disk MISSION file, with
three rails (TERMINATION, CAP, independent ACCEPTANCE). Nothing here removes a
rail; it adds intelligence and robustness on top.

## A. Smarter iterations
- **Progress/stall detection.** The driver hashes the mission `## STATE` block and
  counts DONE/ACCEPTED lines each iteration. No change for K iterations = a
  *stall* (an iteration can exit 0 yet make zero real progress — the failure the
  caps alone don't catch). On stall the driver switches the next iteration to a
  **stall directive** (change strategy / decompose NEXT / mark blocked); persistent
  stall stops the loop with `needs-input` rather than spinning.
- **Mode-routed iterations.** Each iteration first routes its NEXT through
  `ROUTING.md` (or an explicit `MODE:` hint in STATE) and executes under that
  mode's discipline (`modes/<mode>.md`) — `math_lock` for a consistency check,
  `counter` for an attack, etc. — instead of a generic "do the next thing".
- **Producer–reviewer cadence.** Most iterations are EXECUTOR. Every `review-every`
  iterations a **REVIEWER** iteration runs with a fresh context and (optionally) a
  different model (`--reviewer-model`), given only the primary artifacts + the
  claim, never the executor's framing (`kernel/verification_authority.md`). It
  promotes DONE→ACCEPTED or rejects to OPEN. The ACCEPTANCE gate thus lives in the
  loop's rhythm, not as an afterthought, and the loop cannot self-acquit.
- **Completeness critic.** Every `critic-every` iterations, a CRITIC iteration asks
  "what is missing / unverified / unattempted?" and appends findings to OPEN.

## B. Uninterrupted, meaningful, 1–2h+
- **Transient retry/backoff.** Rate-limit / overload / transient API errors retry
  the *same* iteration with exponential backoff (do not count toward the
  consecutive-error abort); only real errors count. A short outage no longer kills
  an hour-long run.
- **Heartbeat + detached run.** The driver writes `<mission_dir>/.loop_heartbeat`
  each iteration (ts, iter, status, elapsed) so liveness is externally visible.
  Run detached (`nohup`/`tmux`/launchd). State is on disk, so a killed driver
  resumes from the mission file unchanged.
- **Stall → replan, don't die.** When OPEN empties before GOAL is met, or progress
  stalls, the loop injects a decompose/replan directive instead of terminating;
  it stops only on a hard blocker, a cap, or `needs-input`.
- **Adaptive per-iteration timeout** from an `EST:` minutes hint in STATE (bounded
  by the 30-min hard ceiling).

## C. Distillation automation (`scripts/distill_session.py --auto`)
Adapted from a self-improving-agent reference: a forked reviewer with a **narrow
write surface** decides what to persist.
- `--auto` spawns a fresh `claude -p` with the review prompt + audit evidence.
- **Write surface is enforced**, not just advised: `CLAUDE_HARNESS_DISTILL=1` makes
  `scripts/hooks/kernel_guard.py` **deny** any edit outside `memory/` and
  `sessions/distilled/`. `skills/` is excluded on purpose — skill patches are
  proposed as text into `sessions/distilled/` for human approval, never written
  directly. (Headless can't answer an "ask", so distillation gets a hard sandbox.)
- **Default is dry-run (proposal):** writes proposals to
  `sessions/distilled/<date>_distill.md`. `--apply` lets it land memory items
  (frontmatter + `MEMORY.md` index). **Skill patches are always proposals** — skills
  are higher-stakes than memory notes; a human approves them. Never delete
  (supersede/archive only).
- The persistence guard (no transient/env-specific/negative-capability captures)
  and the action ladder (`modes/memory.md`, `skills/README.md`) bind the reviewer.
- **Triggers:** `run_loop.py --distill-on-done` runs it (proposal mode) when a
  mission completes; otherwise run it manually after a session. Hooks never
  auto-spawn `claude` (too heavy).

## Phasing (all implemented)
P1 robustness (retry/backoff, heartbeat, stall→replan) · P2 mode-routing + stall
escalation + `MODE`/`EST` in STATE · P3 producer–reviewer cadence · P4
`distill --auto` (sandboxed, dry-run default) + memory validation · P5
`--distill-on-done` + completeness critic + adaptive timeout.

All are extensions of `run_loop.py`, `templates/mission.md`, and
`distill_session.py` — gated each step by `scripts/validate_harness.py`.
