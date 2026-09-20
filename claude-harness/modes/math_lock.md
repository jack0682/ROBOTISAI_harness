# mode · math_lock — make the formalism load-bearing

> The center of this harness. This harness does not accept equations as decoration. A
> formalization either *carries* a claim under stated conditions, or it is
> removed. This mode is the gate between "looks rigorous" and "is rigorous".

**Trigger.** Any math is written or invoked: a model, an objective, a bound, a
derivation, a "we can show that…". Also when a claim *should* be formalized but
isn't yet.

**Input.** The formal content + the claim it is meant to support + the concepts
it rests on (run `define` first if they're shaky).

**Operations — the consistency checklist.** Separate and check each; report which
pass, which fail, which are unknown:

1. **Objects & spaces.** Every variable: what is it, and in *what space* does it
   live? Inputs, outputs, parameters, latent variables, observed quantities,
   constraints — listed and separated.
2. **Observed vs latent.** Which quantities are actually observable/measurable,
   which are latent? A claim that depends on a latent variable as if observed is
   a red flag.
3. **Domain / codomain.** Each operation/function: domain and codomain stated;
   is it well-defined everywhere it's applied? Partial functions, division by
   possibly-zero, log of possibly-negative, etc.
4. **Operation meaning.** Does each operation *mean* what the prose says it does?
   Expectation over which distribution? Norm in which space? Limit in what sense?
5. **Dimensions / units.** Dimensional and unit consistency across every
   equation. A unit mismatch is a definite bug, cheap to catch.
6. **Hidden assumptions.** Surface what's silently assumed: independence,
   stationarity, smoothness, convexity, full rank, i.i.d., a regime where the
   approximation holds. Mark each verified / assumed / unjustified.
7. **Identifiability.** Can the quantities of interest actually be recovered from
   what's observed? Watch for **underdetermination** (more free parameters than
   constraints), non-identifiability, and observationally-equivalent models.
8. **Degrees of freedom.** Too much freedom (a model that can fit anything
   predicts nothing); circularity (a definition that assumes its conclusion).
9. **Claim ↔ math correspondence.** The decisive check: does the math actually
   *establish the claim made in words*, under the conditions stated — or a weaker
   / different / vacuous statement? Name the gap if there is one.

### When the object evolves in time (items 10–12)

The nine items above verify a *static* formalism. Both of the real systems this
harness has been run against were dynamic and under feedback, and the failure in
each was in the loop rather than in any equation. Run these as well whenever
there is a plant, a controller, a filter, an estimator, or anything else whose
output re-enters its own input (`scopes/control/AGENTS.md`).

10. **Closed-loop stability.** Is the stability claim about the *loop*, or about a
    block? Two individually well-behaved components can be unstable together.
    State the argument — passivity, small-gain, a Lyapunov function, an explicit
    margin — and the conditions it needs. "Each part is fine" is not one.
11. **Energy and passivity.** Where the system couples to a person or an
    environment, does the interconnection store or create energy? A restoring
    force computed from a signal that already contains that force's own effect is
    positive feedback wearing the notation of a spring. Check the sign of the
    power flow, not the plausibility of the formula.
12. **Delay, sampling, and bandwidth.** What is the sample rate, the hold, the
    transport delay, the jitter? A continuous-time argument applied to a sampled
    loop has silently assumed all of them away. Derivatives of measured signals
    have a bandwidth and a noise gain; name both. Where a delay is a
    distribution, do not carry it as a constant.

**Output.** A checklist verdict (pass / fail / unknown per item), the explicit
list of conditions under which the formalism holds, the surfaced assumptions, and
a one-line judgment: *does this math support its claim, and if not, what's the
smallest repair* (tighten a definition, add a condition, weaken the claim, or
design an experiment to test an assumption).

**Guardrails.** "I can't see a problem" ≠ "there is no problem" — say which
(`kernel/reasoning_protocol.md`). When stakes are high, hand the raw
formalism and claim to an independent vantage (a fresh check, a different method,
the `proof-checker` skill), never your own summary
(`kernel/verification_authority.md`).

**Anti-patterns.** ❌ Nodding at notation without checking spaces/units.
❌ Treating a suggestive equation as a proof. ❌ Accepting an identifiability-free
model. ❌ Letting a formalism *look* like it supports a stronger claim than it
does.

**Loop position.** *Mathematical Formulation → Consistency Check*. Routinely
loops with `counter` (a failed check often *is* a counterexample) and `define`.
Relevant skills: `proof-checker`, `proof-writer`, `formula-derivation`,
`kill-argument`.
