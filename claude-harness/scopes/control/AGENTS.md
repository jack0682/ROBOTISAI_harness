# scope · control — dynamics, feedback, timing

**Read first.** `KERNEL.md` (principles 1–4), `modes/math_lock.md` (including the
closed-loop axis), `modes/verify.md`, `scopes/coding/AGENTS.md` when the artifact
is a running controller.

**Why this scope exists.** A stability failure in a feedback system is part
implementation, part mathematics, and part experiment, and without a scope that
owns it the reasoning gets spread across all three and nobody checks the loop.
The other scopes reason about objects that hold still. This one is for systems
that evolve in time and feed their own output back into their input — which is
where a component that is correct on its own becomes a system that oscillates.

This scope is finding **F2** in [`docs/testbed_findings.md`](../../docs/testbed_findings.md),
written after running the harness on a real bilateral-teleoperation stability
bug and watching the reasoning get spread across coding, math and experiments
with nobody owning the loop. `modes/math_lock.md` items 10–12 are F3 and F8 from
the same run. That file records what is still open.

**Purpose.** Decide whether the loop is stable, whether it exchanges energy
safely with whatever is on the other end, what it can actually observe, and what
the timing is rather than what the block diagram implies.

**Contract (what this scope owes).**
- The loop is drawn before it is discussed: every block, every signal, every
  point where a sample is taken or a value is held, every delay.
- Stability is argued about the *closed* loop, never a block in isolation.
- Every estimated quantity is checked for identifiability in the regime it is
  used in, not only in the regime where it is easy.
- Timing is stated in numbers — rates, latencies, jitter — and reconciled against
  the analysis that assumed them.

**Local invariants.**
- **Closed-loop, not open-loop.** Two components that are each well-behaved can
  be unstable together. A stability claim about a controller says nothing until
  the plant, the sensing and the delay are in it.
- **Energy has to balance.** Where the loop couples to a person or an
  environment, the interconnection is passive or a reason is given why it need
  not be. Rendering a restoring force from a signal that already contains that
  force's own effect is a positive feedback path, however well it is tuned.
- **Causality.** No block consumes a value it cannot have yet. A derivative of a
  measured signal is a noise amplifier with a bandwidth, not free information.
- **Identifiability in the regime of use.** A quantity estimated by subtracting a
  *static* baseline from a composite measurement is not identifiable while the
  system is moving — the measurement is a sum of several effects and exactly one
  of them is wanted. Being right at rest is not evidence about motion.
- **Sampling is part of the plant.** A discrete controller on a continuous plant
  carries a hold, a rate and a phase lag that no continuous-time argument
  contains. Debounce counts, ramp times and inter-process hops are latency.
- **Model fidelity is stated, not assumed.** Which dynamics are modelled, which
  are neglected, and the regime in which neglecting them is valid.

**Guardrails.**
- A limit cycle is evidence of a loop, not of a bad gain. Retuning until an
  oscillation disappears, without changing the interconnection, is a workaround
  and says so out loud.
- "It works on the bench" is a claim about one trajectory. Name the regime.
- Where the system cannot be run, say so and mark the verification ceiling
  (`modes/verify.md`). An unrunnable system must not quietly become a verified
  one.
- The implementation's own regression notes, tuning comments and disabled flags
  are primary sources about what actually broke, and are usually more reliable
  than any prose description of the architecture. Read them before trusting a
  description (`modes/verify.md`).

**Verification.** The closed-loop argument first — passivity, small-gain, or an
explicit margin — then the numbers that argument assumed, then, where it can be
run, the experiment. Where it cannot be run, the analysis is the deliverable and
its ceiling is part of it.

**Routes to.** `modes/math_lock.md` (closed-loop axis) · `modes/counter.md` ·
`protocols/debugging.md` · `protocols/validation.md` ·
`scopes/experiments/AGENTS.md` when a run exists · `scopes/coding/AGENTS.md` for
the implementation.

**Anti-patterns.** ❌ Proving a block stable and calling the loop stable.
❌ An estimator validated only in the regime where it is easy. ❌ Continuous-time
analysis of a sampled loop. ❌ Treating a delay as a constant when it is a
distribution. ❌ Tuning until the symptom stops and calling that the cause.
