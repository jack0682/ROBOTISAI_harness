# modes/ — the cognitive operations

A **mode** is one operation the harness runs on a thought. Modes are
domain-independent (a `scope` supplies the domain). Each mode file is short and
shaped the same way, loosely:

- **Trigger** — when to enter this mode.
- **Input** — what it consumes.
- **Operations** — what it actually does.
- **Output** — the fixed artifact it must leave behind (this is how the loop
  makes progress — see `KERNEL.md` principle 5).
- **Guardrails / Anti-patterns** — how the mode fails, and the line it must hold.
- **Loop position** — where it sits in the central loop.

You rarely run one mode in isolation. Real work chains them. The chain *is* the
central loop: `Thought → Claim → Definition → Math → Consistency → Counterexample
→ Execution → Data → Revision → Artifact → Distillation`.

| mode | one line | loop stage |
|---|---|---|
| `think` | decompose the request, compress the thought to a thesis | Thought |
| `define` | force concepts into testable definitions | Definition |
| `math_lock` | check the formalism actually holds and supports the claim | Math / Consistency |
| `verify` | separate claim from evidence; cap claim strength to evidence | Claim |
| `counter` | attack the idea from a reviewer/experimenter's seat | Counterexample |
| `execute` | turn thought into the next concrete unit of work | Execution / Artifact |
| `research` | map a field: lineage, clusters, gaps, novelty | (feeds Claim/Definition) |
| `paper` | critique a document the way a hostile reviewer would | (Artifact critique) |
| `prompt` | write a behavior-contract directive for another agent | (Execution handoff) |
| `memory` | distill a session into reusable memory/skill | Distillation |
| `audit` | check work is really done, not just claimed | Revision |
| `layer` | move deliberately between abstraction levels | (cross-cutting) |

These are tools, not a script to perform. Output format stays flexible
(`KERNEL.md` → Output). Naming the mode you are in is for *your* clarity and the
user's, not a header you must print.
