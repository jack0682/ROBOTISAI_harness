# mode · counter — attack the idea to find its boundary

> Criticism here is *constructive by destruction*: the goal is not to win an
> argument but to find where the idea actually breaks, so the surviving version is
> stronger and its boundary is known.

**Trigger.** A claim, model, or result has survived `verify`/`math_lock` and is
about to be trusted, written up, or built on. Also any "이거 맞는 것 같은데" that
hasn't been attacked yet.

**Input.** The current best version of the claim/model/result.

**Operations.**
1. **Take the hostile seats.** Argue as: a *reviewer* hunting for the rejection
   reason; a *professor* probing the weakest assumption; a *peer* who half-buys
   it; an *experimenter* asking what could confound it; an *implementer* asking
   what breaks in practice.
2. **Construct counterexamples.** Find an instance — even contrived — where the
   claim fails or the definition admits something it shouldn't. One real
   counterexample beats ten reassurances.
3. **Alternative explanations.** "This result is also explained by X" — list the
   confounds and rival hypotheses the evidence doesn't rule out.
4. **Verification mismatch.** "This experiment cannot actually test that claim
   because…" — find where the evidence and the claim don't meet.
5. **Reject the false positive — what does NOT count as evidence.** Before
   crediting support, see through the patterns that masquerade as it:
   - *math:* "I tried and couldn't find a problem" read as a proof; an
     unfalsifiable lemma; notation that performs rigor without carrying a claim.
   - *experiments:* a circular metric (a perfect score on the very quantity the
     method enforces by construction); a happy-path run called "comprehensive";
     mock/expected output shown as a real run; a single sample dressed as "±0".
   - *research:* novelty asserted with no prior-art search actually run.
   - *coding:* "tests pass / CI green" taken as "correct" when the test never
     exercises the claimed path.
   A claim resting only on one of these is not yet supported — say so.
6. **Use the breaks.** Each surviving attack does one of: kills the claim,
   *narrows* it (adds a condition / shrinks scope), or sends it back to
   `define`/`math_lock` for repair. Record which.

**Output.** A list of attack points; concrete counterexamples (or "none found
after trying A,B,C" — stated as effort, not as proof of safety); confounds; the
*narrowed* claim and its now-explicit boundary; what each attack forces.

**Guardrails.** Attack the strongest version of the idea, not a strawman. Trying
and failing to break it is evidence *toward* it — but report it as "attacked along
these axes, held", never as "proven".

**Anti-patterns.** ❌ Performing skepticism without producing a concrete break.
❌ Stopping at the first easy objection. ❌ Treating "I couldn't break it" as
"it's correct".

**Loop position.** *Counterexample* — the stress test between formalization and
execution. Skill: `kill-argument`.
