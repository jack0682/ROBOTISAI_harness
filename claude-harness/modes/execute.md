# mode · execute — descend thought into the next concrete unit

> A long discussion that produces no next action did not happen
> (`KERNEL.md` principle 5). This mode is the descent from thinking to doing.

**Trigger.** A line of thought has matured enough to act on; the end of any long
analysis; "좋아 그럼 이제 뭘 하지"; execution was requested.

**Input.** The current claims, definitions, and decisions.

**Operations.**
1. **Pick the conversion target.** Turn the thought into one or more of: a
   *research question*, an *experiment plan*, *code TODOs*, a *data-analysis
   plan*, a *document structure*, a *talk flow*, or an *agent prompt*
   (→ `modes/prompt.md`).
2. **Descend to an actionable unit.** Name something that can be *started now* —
   small, concrete, with a clear done-condition. Not "improve the model" but
   "run ablation X to test assumption A from the math_lock checklist".
3. **Keep the thread up.** Every unit links back to the higher claim it serves,
   so execution doesn't drift from purpose (`modes/layer.md`).
4. **Carry the procedure.** For domain work, route into the scope and its
   protocol (coding → `scopes/coding/AGENTS.md` + `protocols/coding.md`,
   `protocols/validation.md`; experiments → `scopes/experiments/AGENTS.md`).
5. **Fix the artifact.** When the output *is* the deliverable, produce it in a
   form the next session can pick up (`modes/memory.md`, `templates/`).

**Output.** A concrete next-action (or a short ordered list), each with a
done-condition and the claim it serves. Where applicable, the actual artifact
(plan / TODOs / structure / prompt).

**Guardrails.** When execution was asked for, stopping at "analysis only" is a
failure, not a deliverable (`kernel/execution_protocol.md`). Assume no
artificial limit; split large work into checkpointed units, don't skim it.

**Anti-patterns.** ❌ Ending a long thread with no next step. ❌ A "next action"
too vague to start. ❌ Executing while losing the why.

**Loop position.** *Execution / Experiment / Implementation → Artifact*. Hands
off to `audit` (did it actually get done) and `memory` (distill it).
