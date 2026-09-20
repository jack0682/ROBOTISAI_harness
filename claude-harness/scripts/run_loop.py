#!/usr/bin/env python3
# Copyright 2026 ROBOTIS AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Jaehong Oh <jaehongoh1554@gmail.com>

"""Forced long-running mission loop driver for the harness.

Runs autonomous work for hours by issuing MANY short, fresh `claude -p`
iterations against a durable on-disk MISSION file, instead of one long session
that compaction would degrade. Each iteration reloads the compact MISSION STATE
block (cheap), does the single NEXT action, updates the STATE in place, and
appends one LEDGER line. The loop survives compaction and session restarts
because no single iteration holds more than a few minutes of context — the
state lives on disk (`templates/mission.md`, `protocols/long_loop.md`).

Beyond the basic loop, the driver adds (see docs/loop_and_distillation_design.md):
  - transient retry/backoff      — a rate-limit/overload blip retries the SAME
                                   iteration; only real errors count toward abort.
  - stall detection → replan     — no STATE progress for K iters injects a
                                   strategy-change directive; persistent stall
                                   stops with `needs-input` instead of spinning.
  - mode-routed iterations       — each iteration routes NEXT through ROUTING.md
                                   (or a STATE `MODE:` hint) and works under it.
  - producer–reviewer cadence    — every --review-every iters a fresh-context
                                   REVIEWER (optionally a different model) checks
                                   DONE→ACCEPTED, never self-acquitting.
  - completeness critic          — every --critic-every iters, "what's missing?".
  - adaptive timeout             — from a STATE `EST:` minutes hint (bounded).
  - heartbeat                    — <mission_dir>/.loop_heartbeat for liveness.
  - --distill-on-done            — run the distillation review when STATUS=done.

Stops at the FIRST of: MISSION STATUS != active (done/aborted/needs-input), the
wall-clock cap, the iteration cap, persistent stall, or too many consecutive
non-transient errors. The caps are hard safety rails.

Usage:
    python3 scripts/run_loop.py --mission <path/to/MISSION.md> \
        [--cwd DIR] [--hours H] [--max-iters N] [--model M] \
        [--reviewer-model M] [--review-every K] [--critic-every C] \
        [--distill-on-done] [--dry-run]

The MISSION `CAPS:` line sets defaults; flags override. Kill-switch: set
`STATUS: aborted` in the MISSION file (re-read every iteration) or Ctrl-C.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
import time

ITER_TIMEOUT_S = 1800          # per-iteration hard ceiling (30 min)
MIN_TIMEOUT_S = 120            # adaptive-timeout floor
SLEEP_BETWEEN_S = 3            # brief gap so an aborted file is observed promptly
MAX_CONSEC_ERRORS = 3         # consecutive NON-transient errors → abort
TRANSIENT_RETRIES = 5         # per-iteration retries on a transient failure
TRANSIENT_BACKOFF_S = 10      # base backoff; doubles each retry (10, 20, 40, …)
STALL_WARN = 2               # no-progress iters before injecting a stall directive
STALL_STOP = 4               # no-progress iters (incl. warned) → stop, needs-input

# stderr/stdout signatures that mean "retry the same iteration", not "real error".
_TRANSIENT_RE = re.compile(
    r"rate.?limit|overloaded|429|503|502|500|timed out|timeout|temporarily|"
    r"connection (reset|refused|error)|ECONNRESET|ETIMEDOUT|EAI_AGAIN|"
    r"service unavailable|please try again", re.I)

EXEC_PROMPT = (
    "You are one iteration of a long-running autonomous mission loop.\n"
    "1. Read the mission file at: {mission}\n"
    "2. Read its `## Control` and `## STATE` blocks.\n"
    "3. ROUTE this iteration: take the single STATE `NEXT` action; classify it via "
    "ROUTING.md (or honor an explicit STATE `MODE:` hint) and work under that "
    "mode's discipline (modes/<mode>.md) — e.g. math_lock for a consistency/"
    "identifiability check, counter to attack a claim, define to pin a term, "
    "execute to produce an artifact. Do EXACTLY that one NEXT action — no more.\n"
    "4. UPDATE the mission file in place: refresh DONE / ACCEPTED / OPEN / "
    "FILE-MAP / MODE / EST / NEXT in the STATE block (keep it small), and APPEND "
    "one line to the LEDGER with what changed and the new NEXT.\n"
    "5. Mark a phase ACCEPTED only with an independent verdict (a cross-model "
    "reviewer or a passing check) — never self-acquit "
    "(kernel/verification_authority.md). You may mark DONE.\n"
    "6. If the TERMINATION condition is met, set `STATUS: done`. If irrecoverably "
    "blocked, set `STATUS: aborted` and say why in the LEDGER.\n"
    "Externalize everything into the mission file — do NOT rely on this session's "
    "context surviving. Work only on this iteration's NEXT action."
)

STALL_SUFFIX = (
    "\n\nSTALL NOTICE: the STATE block has not advanced for {n} iterations. Do not "
    "repeat the same NEXT. Either (a) change strategy, (b) DECOMPOSE NEXT into a "
    "smaller concrete first step and set that as NEXT, or (c) if genuinely blocked, "
    "move the item to OPEN with the blocker and pick a different NEXT. If OPEN is "
    "empty but the GOAL is unmet, generate the next sub-goals from the GOAL."
)

REVIEW_PROMPT = (
    "You are a REVIEWER iteration of an autonomous mission loop — an independent "
    "vantage, not the executor (kernel/verification_authority.md).\n"
    "1. Read the mission file at: {mission} — its `## Control` (GOAL, TERMINATION, "
    "ACCEPTANCE) and `## STATE`.\n"
    "2. For each item under DONE that is NOT yet under ACCEPTED, verify it "
    "INDEPENDENTLY against the PRIMARY ARTIFACTS (read the actual files/results), "
    "NOT against the LEDGER's claims or the executor's framing. Use the verify / "
    "math_lock / counter modes as fits.\n"
    "3. Update STATE in place: move each item that genuinely holds to ACCEPTED with "
    "its verdict source; send each that fails back to OPEN with the precise reason. "
    "Do not advance anything you could not independently confirm.\n"
    "4. APPEND one LEDGER line: 'reviewer: accepted X, rejected Y because …'.\n"
    "Change nothing else. Do not do executor work this iteration."
)

CRITIC_PROMPT = (
    "You are a COMPLETENESS-CRITIC iteration of an autonomous mission loop.\n"
    "1. Read the mission file at: {mission} (GOAL, TERMINATION, STATE).\n"
    "2. Ask, against the GOAL and TERMINATION: what is MISSING, UNVERIFIED, or "
    "UNATTEMPTED? A claim with no independent check, a definition still open, an "
    "experiment that wouldn't actually test the claim, a path not explored.\n"
    "3. Append the real gaps to OPEN in STATE (deduped, concrete), and one LEDGER "
    "line summarizing what you added. Add nothing speculative; change nothing else."
)


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def _status(text):
    m = re.search(r"^\s*-?\s*STATUS:\s*([\w-]+)", text, re.M | re.I)
    return (m.group(1).lower() if m else "active")


def _caps(text):
    h = re.search(r"max_hours\s*=\s*([0-9.]+)", text, re.I)
    n = re.search(r"max_iters\s*=\s*(\d+)", text, re.I)
    return (float(h.group(1)) if h else None, int(n.group(1)) if n else None)


def _section(text, header):
    """Body of a `## <header>` markdown section (until the next heading)."""
    out, active = [], False
    for line in text.splitlines():
        if line.startswith("#"):
            active = line.strip().lower().lstrip("# ").startswith(header.lower())
            continue
        if active:
            out.append(line)
    return "\n".join(out).strip()


def _state_sig(text):
    """A progress signature for the STATE block. Two STATE blocks with the same
    signature = no progress that iteration. The hash captures any textual change;
    the accepted-count makes a reviewer's DONE→ACCEPTED move register as progress
    even if it only moves a line within STATE."""
    state = _section(text, "STATE")
    accepted = state.lower().count("accepted")
    h = hashlib.sha1(state.encode("utf-8")).hexdigest()[:12]
    return (h, accepted)


def _est_minutes(text):
    m = re.search(r"EST:\s*([0-9.]+)", text, re.I)
    return float(m.group(1)) if m else None


def _iter_timeout(text):
    est = _est_minutes(text)
    if not est:
        return ITER_TIMEOUT_S
    return int(max(MIN_TIMEOUT_S, min(ITER_TIMEOUT_S, est * 60 * 2)))


def _is_transient(returncode, out, err):
    if returncode == 0:
        return False
    blob = (out or "") + "\n" + (err or "")
    return bool(_TRANSIENT_RE.search(blob))


def _heartbeat(mission, it, status, elapsed_h, note):
    path = os.path.join(os.path.dirname(mission), ".loop_heartbeat")
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(f"iter={it} status={status} elapsed_h={elapsed_h:.2f} "
                     f"note={note[:120]}\n")
    except OSError:
        pass


def _run_once(cmd_base, prompt, cwd, timeout):
    """Run one `claude -p`, retrying the SAME call on transient failures.

    Returns (ok, transient_exhausted, note).
    """
    delay = TRANSIENT_BACKOFF_S
    for attempt in range(TRANSIENT_RETRIES + 1):
        try:
            r = subprocess.run(cmd_base + [prompt], cwd=cwd, capture_output=True,
                               text=True, timeout=timeout)
            out, err, rc = r.stdout, r.stderr, r.returncode
        except subprocess.TimeoutExpired:
            out, err, rc = "", f"[iteration timed out >{timeout}s]", 124
        if rc == 0:
            tail = (out or err or "").strip().splitlines()
            return True, False, (tail[-1][:80] if tail else "(no output)")
        if _is_transient(rc, out, err) and attempt < TRANSIENT_RETRIES:
            print(f"[run_loop]   transient failure (attempt {attempt + 1}); "
                  f"backing off {delay}s")
            time.sleep(delay)
            delay *= 2
            continue
        tail = (err or out or "").strip().splitlines()
        return False, _is_transient(rc, out, err), (
            tail[-1][:80] if tail else f"[exit {rc}]")
    return False, True, "[transient retries exhausted]"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Forced long-running mission loop.")
    ap.add_argument("--mission", required=True, help="Path to the MISSION file.")
    ap.add_argument("--cwd", default=None, help="Working dir for each iteration.")
    ap.add_argument("--hours", type=float, default=None, help="Wall-clock cap.")
    ap.add_argument("--max-iters", type=int, default=None, help="Iteration cap.")
    ap.add_argument("--model", default=None, help="Model for executor iterations.")
    ap.add_argument("--reviewer-model", default=None,
                    help="Model for REVIEWER iterations (independence). "
                         "Defaults to --model.")
    ap.add_argument("--review-every", type=int, default=5,
                    help="Run a REVIEWER iteration every N iterations (0=off).")
    ap.add_argument("--critic-every", type=int, default=0,
                    help="Run a COMPLETENESS-CRITIC iteration every N (0=off).")
    ap.add_argument("--distill-on-done", action="store_true",
                    help="Run distill_session.py --auto when STATUS=done.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print the plan and the iteration prompts; run nothing.")
    args = ap.parse_args(argv)

    mission = os.path.abspath(args.mission)
    if not os.path.isfile(mission):
        print(f"error: mission file not found: {mission}", file=sys.stderr)
        return 2
    cwd = os.path.abspath(args.cwd) if args.cwd else os.path.dirname(mission)

    cap_h, cap_n = _caps(_read(mission))
    max_hours = args.hours if args.hours is not None else (cap_h or 6.0)
    max_iters = args.max_iters if args.max_iters is not None else (cap_n or 120)
    review_every = max(0, args.review_every)
    critic_every = max(0, args.critic_every)

    exec_base = ["claude", "-p"] + (["--model", args.model] if args.model else [])
    rev_model = args.reviewer_model or args.model
    rev_base = ["claude", "-p"] + (["--model", rev_model] if rev_model else [])

    print(f"[run_loop] mission={mission}")
    print(f"[run_loop] cwd={cwd}  caps: max_hours={max_hours} max_iters={max_iters}")
    print(f"[run_loop] review-every={review_every} (model={rev_model or 'same'})  "
          f"critic-every={critic_every}  distill-on-done={args.distill_on_done}")
    if args.dry_run:
        print("\n[EXEC_PROMPT]\n" + EXEC_PROMPT.format(mission=mission))
        print("\n[REVIEW_PROMPT]\n" + REVIEW_PROMPT.format(mission=mission))
        print("\n[CRITIC_PROMPT]\n" + CRITIC_PROMPT.format(mission=mission))
        return 0

    start = time.time()
    it = errors = stall = 0
    prev_sig = None
    while True:
        text = _read(mission)
        status = _status(text)
        if status != "active":
            print(f"[run_loop] STATUS={status} → stopping after {it} iters.")
            break
        elapsed_h = (time.time() - start) / 3600.0
        if elapsed_h >= max_hours:
            print(f"[run_loop] wall-clock cap {max_hours}h reached ({it} iters).")
            break
        if it >= max_iters:
            print(f"[run_loop] iteration cap {max_iters} reached.")
            break

        it += 1
        # choose iteration kind: reviewer / critic / executor (+stall directive)
        if review_every and it % review_every == 0:
            kind, base, prompt = "review", rev_base, REVIEW_PROMPT.format(mission=mission)
        elif critic_every and it % critic_every == 0:
            kind, base, prompt = "critic", exec_base, CRITIC_PROMPT.format(mission=mission)
        else:
            kind, base = "exec", exec_base
            prompt = EXEC_PROMPT.format(mission=mission)
            if stall >= STALL_WARN:
                prompt += STALL_SUFFIX.format(n=stall)

        timeout = _iter_timeout(text)
        t0 = time.time()
        ok, transient_dead, note = _run_once(base, prompt, cwd, timeout)
        dt = time.time() - t0

        # progress check (executor/critic advance STATE; reviewer advances ACCEPTED)
        new_sig = _state_sig(_read(mission))
        progressed = prev_sig is None or new_sig != prev_sig
        prev_sig = new_sig
        stall = 0 if (progressed and kind != "review") else (stall + (kind == "exec"))

        flag = "ok" if ok else ("ERR-transient" if transient_dead else "ERR")
        print(f"[run_loop] iter {it}/{max_iters} [{kind}] {elapsed_h:.2f}h {dt:.0f}s "
              f"{flag} stall={stall} | {note}")
        _heartbeat(mission, it, status, elapsed_h, note)

        errors = 0 if ok else errors + 1
        if errors >= MAX_CONSEC_ERRORS:
            print(f"[run_loop] {errors} consecutive errors — aborting "
                  "(check `claude` auth / the mission NEXT action).")
            break
        if stall >= STALL_STOP:
            print(f"[run_loop] no STATE progress for {stall} executor iters — "
                  "stopping (needs-input). Inspect the mission NEXT/OPEN, then "
                  "re-run to resume.")
            break
        time.sleep(SLEEP_BETWEEN_S)

    final = _status(_read(mission))
    total_h = (time.time() - start) / 3600.0
    _heartbeat(mission, it, final, total_h, "loop ended")  # terminal liveness state
    print(f"[run_loop] done. {it} iterations, {total_h:.2f}h. Final STATUS={final}. "
          f"Mission: {mission}")

    if args.distill_on_done and final == "done":
        print("[run_loop] STATUS=done → running distillation review (proposal mode).")
        here = os.path.dirname(os.path.abspath(__file__))
        try:
            subprocess.run([sys.executable, os.path.join(here, "distill_session.py"),
                            "--auto", "--cwd", cwd], timeout=ITER_TIMEOUT_S)
        except Exception as exc:  # noqa: BLE001 — distillation is best-effort
            print(f"[run_loop] distillation skipped: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
