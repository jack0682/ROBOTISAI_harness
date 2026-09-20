# scope · prompts — agent prompts as behavior contracts

**Read first.** `modes/prompt.md`, `kernel/verification_authority.md`,
`kernel/anti_patterns.md`.

**Purpose.** Produce directives for other agents that are *behavior contracts*,
not polite requests — because an external agent does not inherit this kernel.

**Contract.**
- A delegated prompt specifies: goal + done-condition, authority & boundaries,
  input, output shape, verification rules, checkpoints, failure behavior,
  completion report.
- It makes refusal-on-fabrication and faithful reporting explicit.
- It withholds your pre-digested conclusion when the agent's value is an
  independent vantage.

**Local invariants.**
- Every contract has a verification clause and a failure clause — never omit
  these two.
- Irreversible/outward-facing actions in the contract require a confirmation gate.
- The plan-ownership switch is honored: if the user wants the agent to self-plan,
  the contract *mandates planning* and withholds the step list; if not, it
  supplies the procedure.

**Guardrails.**
- Don't import this harness's blind spots into a reviewer agent by feeding it your
  framing instead of the primary artifacts.
- Don't over-specify steps when self-planning was requested.

**Verification.** Dry-read the contract as the receiving agent: is the goal
unambiguous? can it tell done from not-done? does it know what never to fake? If
any answer is no, the contract is incomplete.

**Anti-patterns.** ❌ "Please do X well." ❌ No verification/failure clause.
❌ Over-scripting a self-planning mandate. ❌ Handing a conclusion where a vantage
was needed.

**Routes to.** modes: `prompt`, `execute`. skills: `mcp-builder`.
