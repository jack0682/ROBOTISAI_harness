# scope · experiments — design, data analysis, results → claims

**Read first.** `modes/execute.md`, `modes/counter.md`, `modes/verify.md`,
`modes/audit.md`, `protocols/validation.md`.

**Purpose.** Design experiments that can actually test the claim in question, run
them honestly, and convert results into claims no stronger than the data supports.

**Contract.**
- Before running: state *which claim* this experiment tests and *how a result
  would confirm or refute it*. If it can't, don't run it as if it could
  (`modes/counter.md`).
- Separate observed from latent; name the controlled and the measured variables
  (ties to `modes/math_lock.md`).
- Convert results to claims through `modes/verify.md` — strength capped by the
  data.

**Local invariants.**
- The experiment and the claim meet: no "this run can't test that claim" gap.
- Confounds and alternative explanations are enumerated before concluding.
- Scope of a result is the scope actually exercised — a happy-path run is not
  "fully tested"; two cases are not "comprehensive".
- Real numbers trace to a real run/artifact (`kernel/verification_authority.md`).
- **Construct independence.** The metric is independent of what the method
  *enforces by construction*. A method that guarantees a property cannot cite
  the measure of that property as evidence it is *better* — only that the
  guarantee holds. A perfect, zero-variance score across all conditions is the
  signature of a metric measuring the thing the method already enforces; treat
  it as a flag to find a companion metric the method does not optimize, not as a
  headline result. (A single sample reported as "± 0.000" is not a statistic.)
- **Identifiability — can the quantity of interest actually be recovered from
  what was observed?** Before a result is read as evidence for a mechanism, ask
  whether the measurement can separate that mechanism from the others acting at
  the same time. This is `modes/math_lock.md` item 7 applied to a measurement
  rather than a formalism, and it is the same lens `scopes/control/` runs on a
  signal that mixes several contributions. Both testbeds this harness was run
  against failed here first: a metric that measured what the method enforced,
  and an external torque that was not separable from tracking error during
  motion. If the answer is no, the run does not become evidence by being
  repeated — the observable has to change.

**Guardrails.**
- Never present expected/mock output as an actual run
  (`kernel/anti_patterns.md`).
- A negative experimental result is data, not failure — record it; don't bury it.
- Don't persist an environment-specific run failure as a durable rule
  (`modes/memory.md`).

**Verification.** Pre-registration of the confirm/refute condition; ablations to
test the assumptions surfaced in `math_lock`; an independent vantage on
surprising results before they become claims.

**Anti-patterns.** ❌ Running an experiment that can't test the claim. ❌ Ignoring
confounds. ❌ Over-scoping a result. ❌ Result→claim with no strength cap.
❌ **Circular metric:** scoring a method on the very quantity it enforces by
construction, getting a near-tautological "perfect" number, and reading it as
superiority over methods that don't enforce it. The ablation (with vs without
the mechanism) is the valid comparison; the cross-method comparison on the
enforced quantity is not independent.

**Routes to.** modes: `execute`, `counter`, `verify`, `audit`, `math_lock`.
skills: `experiment-plan`, `experiment-queue`, `ablation-planner`,
`experiment-audit`, `result-to-claim`, `experiment-bridge`, `vast-gpu`,
`serverless-modal`.
