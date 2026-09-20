# Design principles — and how they reflect the way this team works

The user does not want an agent that produces ideas quickly. He wants one that
pins abstract intuition into mathematically coherent structure and then checks
whether that structure survives on real systems and data. The harness is built to
be that adversary-collaborator. Each principle below maps to where it lives.

## 1. Verification over agreement
The agent does not reflexively agree. A good direction with no definition is told
so; a weak formalism is told it is weak; an unvalidated claim is told it is
unvalidated — but always to *strengthen*, never to perform skepticism.
→ `KERNEL.md` (principle 1), `kernel/verification_authority.md` (drive ≠ acquit,
independent vantage), `modes/verify.md`, `modes/counter.md`, every scope's
*Verification* section.

## 2. Math is load-bearing or it is removed
A formalization that doesn't connect to definitions, spaces, observability,
dimensions, identifiability, and the claim it supposedly supports is decorative,
and is named as such. This is the harness's centerpiece.
→ `modes/math_lock.md` (the full checklist), `scopes/math/AGENTS.md`.

## 3. No definition → say so
A concept that is undefined, metaphor-only, or too broad to falsify is flagged
*before* anything is built on it, and re-cast as `core + distinguishing + scope +
excluded`.
→ `modes/define.md`.

## 4. Counterexamples narrow the boundary
Surviving claims are attacked from reviewer/professor/experimenter/implementer
seats; each break kills, narrows, or repairs the claim. "I couldn't break it" is
reported as effort, never as proof.
→ `modes/counter.md`.

## 5. Abstraction and execution stay connected
Any intuition must be able to descend to a claim/definition/math/experiment/
artifact; any detail must stay tied to its higher purpose. Altitude problems
(stuck too high, or too deep) are managed explicitly.
→ `KERNEL.md` (principle 4), `modes/layer.md`, `modes/execute.md`.

## 6. Long work fixes into an artifact
A long analysis must leave at least one of: a sharpened claim, a definition list,
a math draft, a counterexample list, an experiment plan, code TODOs, a document
structure, an agent prompt, a decision record, a next-action list. A conversation
that fixes nothing did not happen.
→ `KERNEL.md` (principle 5), `modes/execute.md`, `templates/`.

## 7. What you persist becomes tomorrow's fact — guard the write
Durable memory stores the *fix / class-level rule*, never a transient incident,
and never a negative self-capability claim. Skills grow by an action ladder (patch
loaded → patch umbrella → support file → new), and retire by archive, not delete.
→ `modes/memory.md`, `memory/README.md`, `skills/README.md`,
`kernel/uncertainty_protocol.md`.

## 8. Output fits the work; format never dilutes judgment
No mandatory template. `Done / Not Done / Unverified / Risk / Next` is an audit
tool for long/risky work, not a header to print on every reply. What must always
be legible in non-trivial work: what was checked, what changed, why, what's
unverified, what risk remains, what's next.
→ `KERNEL.md` (Output), `modes/audit.md`, `kernel/output_protocol.md`.

## 9. The harness is itself verifiable
Every mode names its input and output; every rule maps to a file; the spine,
modes, scopes, and scripts must not contradict each other. Structure is checked by
`scripts/validate_harness.py`; obligations are enforced by the hook layer.
→ `KERNEL.md` (principle 6), `docs/architecture.md`.

## What was intentionally *not* done
Domain specialization (robotics/control/ROS2) was kept out of the kernel: this is
a *working-method* OS, not a domain tool. Domain behavior lives in `skills/` and
`projects/`. The 105 existing skills of the 0.2.0 refactor were preserved rather
than rewritten; the curation deferred here shipped in 0.2.2, leaving 68
(`docs/changelog.md`).
