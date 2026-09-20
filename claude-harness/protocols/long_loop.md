# Protocol · Long Loop

> Layer 1 — universal per-task procedure. No project specifics.
> Specializes `long_task.md` for *forced, unattended, multi-hour* autonomous
> work. The governing kernel law is `execution_protocol.md` (continue-by-default,
> checkpoints as control flow) and `verification_authority.md` (drive ≠ acquit).

Use when work must run continuously for hours with little or no supervision.

## The architecture: many short fresh iterations, not one long session
A single session run for hours degrades — compaction summarizes its context and
load-bearing detail is lost. So the loop does the opposite: **many short, fresh
iterations over a durable on-disk state file**, driven by `scripts/run_loop.py`.
Each iteration reloads the compact state, does ONE next action, writes the result
back to disk, and exits. No single iteration holds more than minutes of context,
so compaction and session restarts cannot lose the work.

## The mission file is the memory
Create one from `templates/mission.md` (e.g. via the loop driver). It is the
context memory and the loop control in one file:
- **Control** — STATUS (active/done/aborted), GOAL, TERMINATION, CAPS, ACCEPTANCE.
- **STATE** — a *compact, overwritten-in-place* snapshot: DONE, ACCEPTED, OPEN,
  FILE-MAP, NEXT. Keep it small; it is reloaded every iteration.
- **LEDGER** — append-only, one line per iteration; never rewritten.

Externalize continuously, not at the end: a fresh iteration must be able to
resume from this file alone. The `PreCompact` hook is the backstop — when it
fires, flush the STATE block before the context is summarized.

## Three rails every forced loop must have
A loop with none of these is an archive generator, not progress:
1. **A concrete TERMINATION criterion** — a checkable condition that means the
   GOAL is met (and how it is verified). Without it the loop never stops.
2. **A hard CAP** — max_hours and max_iters in the mission `CAPS:` line; the
   driver stops at whichever comes first. The kill-switch is `STATUS: aborted`.
3. **An independent ACCEPTANCE gate** — the executor may mark a phase DONE, but
   may not mark it ACCEPTED. Quality verdicts come from an independent check (a
   cross-model reviewer, a passing test, a deterministic verifier), per
   `verification_authority.md`. ACCEPTED records the verdict source.

## What the driver adds (intelligence + continuity)
The driver is more than a `while` loop (`docs/loop_and_distillation_design.md`):
- **Mode-routed iterations** — each iteration routes its NEXT through `ROUTING.md`
  (or a STATE `MODE:` hint) and works under that mode's discipline.
- **Producer–reviewer cadence** — every `--review-every` iterations a fresh-context
  REVIEWER (optionally `--reviewer-model`) runs the ACCEPTANCE gate: it checks
  DONE→ACCEPTED against the primary artifacts, never the executor's framing. The
  loop cannot self-acquit.
- **Completeness critic** — every `--critic-every` iterations, "what's missing /
  unverified?" → appended to OPEN.
- **Stall → replan, not spin** — no STATE progress for K iters injects a
  strategy-change directive; persistent stall stops with `needs-input`.
- **Transient retry/backoff** — a rate-limit/overload blip retries the same
  iteration; only real errors count toward the abort.
- **Adaptive timeout** from a STATE `EST:` hint; **heartbeat** at
  `<mission_dir>/.loop_heartbeat`; **`--distill-on-done`** runs the distillation
  review when the mission completes.

## Running it
```bash
python3 scripts/run_loop.py --mission <sessions/active/..._mission.md> \
    --cwd <work dir> --hours 2 --max-iters 30 \
    --review-every 5 --reviewer-model <other-model> --distill-on-done
```
Run it detached for a long unattended session (`nohup`/`tmux`/launchd); the
`.loop_heartbeat` file shows liveness. The driver re-reads the mission each
iteration, so editing STATUS or NEXT steers or stops the loop live. State lives on
disk, so a killed driver resumes from the mission file unchanged — on resume, read
the mission STATE first and reconcile it with reality before continuing
(`long_task.md`).

## Don'ts
- Don't run a forced loop without a termination criterion and a cap.
- Don't let an iteration self-acquit its own quality and advance on that.
- Don't keep state only in context — if it is not in the mission file, a
  compaction or a restart will lose it.
