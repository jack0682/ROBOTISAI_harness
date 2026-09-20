# mode · paper — critique a document as a hostile reviewer

**Trigger.** A paper, report, proposal, or section is up for critique; "이거 좀
봐줘" on written work; before submission/sharing.

**Input.** The document (or section) plus its intended venue/audience.

**Operations.** Don't polish sentences first — interrogate the spine:
1. **Decompose.** Pull the document into: *thesis*, *claims*, *definitions*,
   *math*, *evidence*, *experiments*, *contribution*, *limitations*. Check each
   exists and is sound (route to `define`, `math_lock`, `verify`, `counter`).
2. **Claimed vs proven.** Separate what the paper *actually establishes* from
   what it *says it establishes*. This gap is what reviewers attack first.
3. **Take the reviewer's seat.** Find the rejection reason, the weakest
   assumption, the experiment that doesn't support its claim, the
   over-generalized abstract.
4. **Deflate.** Mark overstated language; rewrite to the provable version
   ("we show" → "we provide evidence that, under conditions C"). Match the
   contribution claim to what's demonstrated.
5. **Contribution & limits.** Is the stated contribution real and properly
   bounded? Are limitations honestly stated or buried?
6. *Only then* prose: clarity, structure, figures (skills: `paper-write`,
   `paper-plan`, `paper-figure`, `paper-claim-audit`, `citation-audit`,
   `rebuttal`).

**Output.** A structured critique: per-element verdict (thesis…limitations), the
claimed-vs-proven gap, the reviewer's likely attacks, specific deflation edits,
and a prioritized fix list (what would change a reject to an accept).

**Guardrails.** Critique to strengthen, not to perform rigor (`modes/counter.md`).
A real limitation honestly stated is a strength, not a confession.

**Anti-patterns.** ❌ Line-editing prose while the thesis is undefined. ❌ Letting
an abstract claim more than the results. ❌ Softening a fatal flaw into a "minor".

**Loop position.** *Artifact* critique — the quality gate before a document
leaves. Reuses `verify`, `math_lock`, `counter` on written claims.
