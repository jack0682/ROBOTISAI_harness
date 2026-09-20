# mode · prompt — write a behavior contract for another agent

> This team frequently hands work to other agents. A prompt here is **not a polite
> request** — it is a behavior contract the agent operates under.

**Trigger.** "이걸 다른 에이전트한테 시킬 프롬프트 짜줘"; delegating a task; building a
reusable directive or sub-agent spec.

**Input.** The task to delegate, the authority the agent should have, and the
acceptance bar.

**Operations.** Build the contract with these parts (include what's load-bearing;
omit what's noise):
1. **Goal** — the objective in one line, and the done-condition.
2. **Authority & boundaries** — what the agent may and may not do; what's
   irreversible/outward-facing and needs confirmation.
3. **Input** — exactly what it receives and where.
4. **Output** — the exact shape of the deliverable.
5. **Verification rules** — how it must check its own work, and what it may *not*
   self-certify (independent vantage for quality verdicts).
6. **Checkpoints** — when to stop and report vs. continue.
7. **Failure behavior** — what to do when blocked: what to try, what to surface,
   what never to fake.
8. **Completion report** — the form of the final hand-back.

**Plan-ownership switch.** If the user says "don't plan it for them — make the
agent plan itself", do **not** embed a step list. Instead write the contract so
the agent is *required to produce and follow its own plan*: give it the goal,
constraints, acceptance bar, and a mandate to plan, checkpoint, and self-verify —
and withhold the procedure.

**Output.** A ready-to-paste directive (the contract above), plus a one-line note
on which mode it puts the receiving agent in.

**Guardrails.** Don't hand the agent a pre-digested conclusion when its value is
an independent vantage (`kernel/verification_authority.md`). Make refusal-on-
fabrication and faithful reporting explicit — an external agent doesn't inherit
this kernel.

**Anti-patterns.** ❌ A vague "please do X well". ❌ A contract with no verification
or failure clause. ❌ Over-specifying steps when self-planning was requested.

**Loop position.** *Execution* handoff. Skills: `mcp-builder`.
