# MISSION — <slug>

> Durable loop state and context memory. The driver (`scripts/run_loop.py`) and
> every iteration read this file. It survives context compaction and new
> sessions **because it lives on disk, not in the context window** — keep the
> STATE block small and CURRENT (overwrite in place), and append one line per
> iteration to the LEDGER. A fresh iteration should be able to continue the work
> from this file alone (`protocols/long_loop.md`).

## Control
- STATUS: active        <!-- active | done | aborted | needs-input ; the driver stops on anything but active. needs-input = a human should look before continuing. -->
- GOAL: <the one objective the loop is driving to>
- TERMINATION: <the concrete, checkable condition that means GOAL is met, and how it is verified — e.g. "an independent cross-model reviewer confirms the proof closes with no remaining gaps">
- CAPS: max_hours=2 max_iters=30      <!-- hard safety caps; the driver stops at whichever comes first. ~2h at 3-5 min/iter ≈ 30 iters. -->
- ACCEPTANCE: <who/what may mark a phase ACCEPTED — a cross-model reviewer (codex/gemini), a passing test, a deterministic check. The executor marks DONE, never ACCEPTED (kernel/verification_authority.md). The driver's --review-every iterations run this gate automatically.>

## STATE  (compact — reloaded every iteration; keep it small, overwrite in place)
- DONE: <verified results so far, one line each>
- ACCEPTED: <phases an independent check accepted, with the verdict source>
- OPEN: <current blockers / open questions; the loop pulls NEXT from here. If empty but GOAL unmet, decompose the GOAL into new items.>
- FILE-MAP: <key path → role, so a fresh iteration need not re-explore>
- MODE: <optional: the mode this NEXT should run under — think|define|math_lock|verify|counter|execute|research|paper|prompt|audit. Omit to let the iteration route via ROUTING.md.>
- EST: <optional: rough minutes the NEXT action needs; the driver scales the per-iteration timeout from this (bounded to 30 min).>
- NEXT: <the single next action this iteration takes>

## LEDGER  (append one line per iteration; never rewritten)
- <iso-ts> iter 0: mission created.
