# mode · verify — separate claim from evidence, cap strength

**Trigger.** A claim is being made or relied on; results are being interpreted;
"so this shows that…"; before anything gets written down as established.

**Input.** The claim(s) and whatever is offered as support.

**Operations.**
1. **Separate claim from evidence.** State the claim in one line; list, beside
   it, exactly what supports it.
2. **Sort the support.** What is *proven* / *measured*, what is *inferred*, what
   is *believed because it's wanted*. The third pile is the dangerous one — name
   it (`kernel/uncertainty_protocol.md`).
3. **Judge claim strength.** Rate the claim: established / supported / suggestive
   / speculative. The strength is **capped by the kind of evidence** under it
   (`kernel/verification_authority.md`) — a two-case check is not
   "comprehensive"; a proxy is not the target.
4. **Weaken to survive.** If the claim outruns the evidence, rewrite it as the
   strongest *defensible* version. A smaller true claim beats a larger unprovable
   one.
5. **Mark the not-yet-sayable.** Explicitly flag claims that *must not be stated
   yet* — what evidence would unlock each.
6. **Independence check for quality verdicts.** "It looks right to me, who wrote
   it" is the weakest check. For correctness verdicts, demand an independent
   vantage; don't hand a reviewer your pre-digested framing.
7. **Primary-source gate — no direct check, no verdict.** A verdict on a
   dependency's behavior, a cited result, a source, or a number requires that
   *you* read or ran the thing. A subagent's summary, an abstract, "the doc
   says", "the paper proves", or a memory note does **not** satisfy it — cite the
   file/line, the run, or the passage you actually checked, or mark the verdict
   not-yet-issuable. Most confident-but-wrong verdicts are claims-by-proxy.
8. **Reconcile the description against the artifact.** The primary-source gate
   applies to *the user's own account of their system*, not only to external
   sources. When a request describes how something works — "the follower runs
   sensorless torque control", "this service retries on 5xx", "the loader
   already validates that" — check the description against the code **before
   reasoning on top of it**, and surface any divergence first. On the testbed
   that produced this rule, the follower was described as sensorless
   *torque/current* control and the code was *position-mode* admittance using
   current only as a proxy; every conclusion built on the description would have
   been about a system that does not exist. This is not doubting the user — they
   are usually describing intent, or an older revision, and the gap is itself
   the finding.
9. **Proof hierarchy — grade the evidence by kind.** Separate *primary* proof
   (the real path reproduced, the actual output observed, the derivation done)
   from *supplemental* (a unit test, CI green, a snapshot, a lint/type pass, a
   plausible-looking number). Supplemental *supports* a primary check; it never
   *substitutes* for one. CI green is not "it works"; a passing test is not "the
   claim holds" unless the test exercises the claimed path.

**Verification ceiling.** Every verdict carries the highest level of evidence
that was *available*, not only the level reached. Some environments cannot run
the thing being judged — a target that builds only on other hardware, a system
you can read but not execute — and the honest verdict there is not "unverified"
and certainly not "verified", but a statement of the ceiling: what was
established by reading the primary sources and reasoning from them, and what
remains open because it could not be run.

Write it as a line, not a feeling: *"static read + closed-loop argument; not
hardware-validated."* A project whose `environment.verification_mode` is
`analysis_only` (`projects/<name>/project.config.yaml`) owes this in its
checkpoint, and the stop gate asks for it in place of the execution evidence it
cannot have. Without it the choice collapses to demanding evidence that cannot
exist, or letting unverified work pass as fine — and in practice it collapses to
the second.

**Output.** A claim/evidence table; a strength rating per claim; rewritten
claims where they were too strong; a "not yet sayable — needs X" list. Where a
verdict rests on something not directly checked, say so explicitly.

**Guardrails.** This is the harness's "agreement is not verification" principle in
action. Being convinced is not evidence. Liking the conclusion is not evidence.

**Anti-patterns.** ❌ Promoting a hope to a fact. ❌ "Comprehensive / fully tested
/ proven" beyond what was exercised. ❌ Accepting a claim because rejecting it
would be inconvenient. ❌ A verdict on a source/result you never opened. ❌ Citing
CI/tests/a snapshot as if it were the primary check it only supports.

**Loop position.** *Claim* — pairs tightly with `math_lock` (for formal claims)
and `counter` (which stress-tests survivors).
