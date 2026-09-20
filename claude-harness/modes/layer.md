# mode · layer — move deliberately between abstraction levels

> Cross-cutting. This team's work spans philosophy → concept → math → system → code →
> experiment → data → document → strategy. Most stalls are *altitude* problems:
> stuck too high to act, or too deep to remember why. This mode manages the climb
> and the descent.

**Trigger.** The discussion is too abstract to produce an action; or too buried
in implementation to recall the goal; or it's unclear which level a claim even
lives at; "우리가 지금 무슨 얘기를 하고 있는 거지".

**Input.** The current thread and where it sits.

**Operations.**
1. **Locate the level.** Name the current altitude: philosophical intuition /
   concept / mathematics / system / code / experiment / data / document /
   strategy. State it plainly.
2. **Diagnose the drift.** Too abstract (no testable consequence) → **descend**.
   Too deep (lost the purpose) → **ascend** and restore the higher claim.
3. **Build the ladder.** Show the *path* between levels for this specific idea:
   how the intuition becomes a concept, the concept a definition, the definition
   math, the math an experiment, the experiment code, the result a document.
   A claim that can't be connected downward to a test, or upward to a purpose, is
   a flag — name the break.
4. **Hand off.** Once relocated, route to the mode for that level (`define`,
   `math_lock`, `execute`, `paper`…).

**Output.** A one-line "we are at level X"; the direction to move and why; the
concrete ladder between levels for *this* idea; the handoff to the next mode.

**Guardrails.** Abstraction and execution must stay connected (`KERNEL.md`
principle 4) — this mode is its enforcement. Don't resolve an altitude problem by
just adding more abstraction.

**Anti-patterns.** ❌ Spinning at the philosophical level with no descent path.
❌ Optimizing an implementation detail no higher claim needs. ❌ Mixing levels in
one argument without noticing.

**Loop position.** Cross-cutting — invoked whenever the loop stalls on altitude
rather than content.
