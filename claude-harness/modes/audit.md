# mode · audit — check work is really done, not just claimed

**Trigger.** Before declaring a task complete; after a long execution; a
checkpoint; "다 된거지?"; any handoff.

**Input.** The original request and the produced work.

**Operations.**
1. **Reconcile against the original.** Put the *original* requirement next to the
   result and check coverage item by item — not the result against your own plan
   (`kernel/reasoning_protocol.md`).
2. **Detect the gap between claimed and done.** Hunt specifically for "looks done
   but isn't": a stub presented as finished, a test referenced but not run, a
   claim of validation with no command behind it (the audit log doesn't lie),
   scope quietly shrunk.
3. **Apply the evidence-map / best-fix lens.** Was the right thing changed
   (entry point, owner boundary, callers/callees, tests)? Is this the best fix or
   the first plausible one? Did non-test size grow without justification?
4. **State the ledger** — in whatever form fits: **Done** (and how verified) /
   **Not Done** / **Unverified** (couldn't check, and why it matters) / **Risk**
   (what could invalidate it) / **Next** (the concrete next action).
5. **Closeout.** Trigger the distillation review (`modes/memory.md`).

**Completion bar.** "Done" is not "I did something." It is **"a verifiable
artifact now exists that addresses the user's original problem."** Until then the
task is open, and the audit names the next action.

**Output.** The reconciliation result + the ledger. Keep it honest and only as
long as it needs to be — this is the one place the Done/Not-Done/Unverified/Risk/
Next form earns its keep; elsewhere it's optional (`KERNEL.md` → Output).

**Guardrails.** Effort and rigor are different axes: a low-effort run does *less*,
it never *lowers the verification bar* (`kernel/execution_protocol.md`).
Report failures with their output; never paper over a skipped step.

**Anti-patterns.** ❌ "Should work" as "works". ❌ Checking the result against the
plan instead of the request. ❌ A green self-report with no independent or
mechanical check behind a quality claim.

**Loop position.** *Revision* — the gate that sends work back to fix or forward to
artifact/distillation.
