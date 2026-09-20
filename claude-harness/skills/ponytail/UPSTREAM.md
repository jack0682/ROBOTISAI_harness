# ponytail — vendored from upstream

**Source:** <https://github.com/DietrichGebert/ponytail> · MIT License ·
Copyright (c) 2026 DietrichGebert · vendored 2026-09-20 at upstream
`2026-09-14`.

The full MIT notice is in `LICENSE` beside this file, as the licence requires.

**The bodies are upstream's text**, with exactly one addition: `ponytail`
carries a trailing section headed *"ROBOTIS AI amendment — local, not
upstream"*, below a `---` rule. Everything above that rule is untouched, so a
diff against a future upstream version stays readable. The other three bodies
are unmodified.

The amendment does not soften the skill — the ladder stays mandatory. It fixes
what "lazy" may cost: brevity is a tiebreaker among *correct* options and never
a trade against correctness; the reasoning that precedes the ladder is not on
the budget; and going over length is allowed where it buys edge-case
correctness, error handling, safety, or readability. It also resolves a real
conflict: upstream says to delete an explanation longer than the code, which
would eat the harness's reporting duty (`kernel/output_protocol.md`), so the
amendment carves that out.

Do not edit upstream's text to fit local taste — raise it upstream, or extend
the amendment.

**The `description:` frontmatter was rewritten**, and that is the one
deliberate divergence. Every skill description is injected into *every*
session, so the library carries a measured ceiling
(`tests/test_context_budget.py`) and a per-skill budget derived from how many
trigger phrases a description actually needs
(`evaluation/skill_triggers.py`). Upstream's four descriptions came to 2,345 B
and pushed the always-on surface over its ceiling.

They were rewritten to fit the budget the same way the rest of this library
was: **mechanism moved into the body, every trigger phrase kept.** `ponytail`
still answers to "be lazy", "yagni", "shortest path" and the rest; nothing that
made a skill reachable was dropped. `evaluation/skill_triggers.py` passes, and
it is what would catch a trigger going missing.

If you re-vendor from upstream, expect a frontmatter conflict and resolve it
the same way.

## What was taken, and what was not

| upstream | here | why |
|---|---|---|
| `ponytail` | ✅ | the core skill — the ladder, YAGNI, minimum working change |
| `ponytail-review` | ✅ | over-engineering review of a **diff** |
| `ponytail-audit` | ✅ | over-engineering audit of the **whole repo** |
| `ponytail-debt` | ✅ | harvests the `ponytail:` shortcut comments the core skill writes — without it that convention is write-only |
| `ponytail-gain` | ❌ | renders **upstream's own published benchmark medians** ("lines of code ▼ 80–94%") as a scoreboard. Those numbers were not measured here, and shipping a skill that prints them as fact is exactly what `kernel/verification_authority.md` forbids. If the team wants the figure, measure it on this codebase. |
| `ponytail-help` | ❌ | a reference card for `/ponytail`, `/ponytail-review` … slash commands. Those commands are **not** installed here — this deployment installs `/harness`, `/harness-checkpoint`, `/harness-init`, `/harness-load` — so the card would point at things that do not exist. `skills/INDEX.md` is the catalogue instead. |
| `hooks/*.js`, `commands/*.toml`, `.claude-plugin/` | ❌ | upstream's own activation machinery. This harness already has a seven-hook layer wired through `install_bridge.py`; adding a second one that also decides when a mode is active would leave two things fighting over the same job. Third-party executable code in a team repository is a separate decision, not a side effect of adding a skill. |

## How it sits next to the harness

They are close enough to be worth stating explicitly.

`scopes/coding/AGENTS.md` already says *"smallest correct change; reuse before
adding"*. Ponytail is a sharper, more insistent version of the same instinct,
with an explicit ladder. They agree; ponytail is the louder one.

The division of labour is real, though:

- **The harness governs whether a claim is earned** — was it run, is it
  verified, does the evidence hold.
- **Ponytail governs whether the code should exist** — is this abstraction
  needed, can the stdlib do it, can it be one line.

Neither substitutes for the other. A one-line solution asserted to work without
being run still fails the harness. A well-verified factory-for-one-product
still fails ponytail.

## One thing to decide

Upstream's description ends with *"Use on ANY coding task"*, and the skill
declares itself **persistent** — "ACTIVE EVERY RESPONSE ... Default: full".
Left as it is, it will tend to engage on most coding work rather than only when
asked for by name.

That may be exactly what the team wants. If it is not, the lever is
`disable-model-invocation` in the skill frontmatter (the harness already uses
it for `skill-creator` and `file-organizer`), which keeps `/ponytail` working
while stopping it from selecting itself. **Left as upstream ships it**, because
narrowing a vendored skill's trigger silently is how a library stops behaving
the way its documentation says it does.

---

## Was the amendment worth it? — measured over three tasks, 2026-09-20

Asserting that a prompt amendment helps is the kind of claim this harness
refuses on faith, so it was measured. Two fresh agents per task, same model,
given **only** the doctrine text: one upstream, one upstream + amendment. Every
implementation was then executed against edge cases rather than read.

| task | upstream | amended | the real difference |
|---|---|---|---|
| **encoder unwrap** (16-bit wrap) | correct one-liner | correct, 8 lines | on 3 of 4 malformed readings upstream returns a **plausible number** (`-4364` ticks that never happened); amended raises |
| **leap year** (deliberately trivial) | `calendar.isleap` | `calendar.isleap` | **+2 lines** — a type hint and a `__main__` guard. Identical behaviour on 11 years |
| **heading error** (unnormalised radians) | `atan2(sin d, cos d)` — correct | **same algorithm** | upstream's self-check contained `assert ... or True`; amended ran its check and flagged `nan`/`inf` as unverified |

### The hypothesis lost, 3 for 3

The amendment was written on the belief that **short code is wrong code**. It
is not. Under upstream's doctrine alone the model climbed to `calendar.isleap`
and to `atan2(sin d, cos d)` — the correct idiom every time, including on
unnormalised input and both wrap directions. Brevity never cost correctness in
any of the three.

Keeping a justification the evidence does not support would be the exact
failure this harness exists to catch, so clause 1 now says so in the skill
itself.

### What did earn its place

**Guarding input the function did not produce.** The encoder case is the one
that matters: a short unwrap is mathematically right and still integrates
`-4364` phantom ticks into odometry when the driver hands it a bad register
read. No test of well-formed input shows this.

**The ledger — the clearest result of the study.** The amended heading answer
ended with *"unverified: behaviour on nan/inf"*. Running it: `nan` propagates,
and `inf` does **not** behave as guessed — `math.sin(inf)` raises `ValueError`.
**The guess was wrong, and writing it down as unverified is what kept it from
becoming a false claim.** Upstream's answer made no such statement.

**A new clause, forced by the data.** Upstream's rule *"lazy code without its
check is unfinished"* produced, on the heading task,
`assert isclose(...) or True` — an assertion that passes for `return 12345.0`,
confirmed by substituting exactly that. Clause 3 now requires breaking the
function on purpose and watching the check go red.

### The amendment's own failure mode

On the encoder it validated `counts_per_rev`, which does not enter the
arithmetic. Both agents noticed the parameter is unused; upstream proposed
deleting it, the amendment kept and guarded it. That is padding, and clause 3's
"not permission to pad" is the line holding it back. Worth watching — it is the
cost side of this change.

The feared cost did **not** otherwise appear: on a deliberately trivial task
the amendment added two lines and no abstraction.

### Scope of this evidence

Three tasks, one sample per arm, one model, all in Python. It shows the
mechanism is real, names what it buys, and refuted its own original
justification. It does **not** measure how often any of it pays. Reproduce
before treating the effect size as known.
