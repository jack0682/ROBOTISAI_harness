# scope · math — theory, formalization, proof, identifiability

**Read first.** `KERNEL.md` (principles 1–3), `modes/define.md`,
`modes/math_lock.md`, `modes/counter.md`. This scope is where the harness's
central commitment — *math is load-bearing or it is removed* — is enforced.

**Purpose.** Turn intuitions into formal objects that survive scrutiny, and check
that the formalism actually carries the claim under stated conditions.

**Contract (what this scope owes).**
- No formalization without its concepts defined first (`modes/define.md`).
- Every formal claim runs the `math_lock` checklist before it's trusted.
- Every surviving claim is attacked at least once (`modes/counter.md`) and its
  boundary recorded.
- The output states the *conditions* under which the result holds, not just the
  result.

**Local invariants.**
- Variables, spaces, domains/codomains, observed vs latent quantities, and
  constraints are always separated and named.
- Dimensional/unit consistency holds across every equation.
- Identifiability is checked: the quantities of interest are recoverable from
  what's observed; no hidden underdetermination or circularity.
- The claim and the math correspond — the math proves *that* claim, not a weaker
  or different one.

**Guardrails.**
- "I can't find a problem" ≠ "there is no problem" — say which.
- An equation that doesn't support its claim is named decorative and cut or
  repaired; it is never left in to look rigorous.
- For high-stakes results, get an independent vantage (`proof-checker` skill, a
  fresh derivation, a different method) — never self-acquit
  (`kernel/verification_authority.md`).

**Verification.** Run the `math_lock` checklist to a per-item verdict. Where a
proof is involved, `proof-checker` / `proof-writer`. Where a claim is empirical,
hand off to `scopes/experiments/`. State the holding conditions explicitly.

**Anti-patterns.** ❌ Notation theatre. ❌ A model that can fit anything. ❌ Latent
treated as observed. ❌ Strengthening a claim past what the math gives.

**Routes to.** modes: `define`, `math_lock`, `counter`, `verify`, `layer`.
skills: `proof-checker`, `proof-writer`, `formula-derivation`, `kill-argument`.
