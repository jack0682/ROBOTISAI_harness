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

## Was the amendment worth it? — measured, 2026-09-20

An A/B, because asserting that a prompt amendment helps is exactly the kind of
claim this harness refuses to take on faith. Two fresh agents, same model, same
task, given **only** the doctrine text: one upstream, one upstream + amendment.

Task: `wheel_delta(prev_ticks, curr_ticks, counts_per_rev)` for a 16-bit
wrapping robot encoder — a case where the short answer is tempting.

**Upstream produced a correct one-liner.**

```python
return (curr_ticks - prev_ticks + 32768) % 65536 - 32768
```

**The amendment produced eight lines**: the same unwrap, plus range checks on
both readings and on `counts_per_rev`, a docstring naming the half-revolution
assumption, and a closing statement of what was *not* verified.

| | upstream | amended |
|---|---|---|
| 7 well-formed cases (forward, reverse, both wrap directions, zero, ±32767) | **all correct** | **all correct** |
| negative tick from a driver bug | returns `101` | raises `ValueError` |
| tick above the register (70000) | returns `-4364` | raises `ValueError` |
| `counts_per_rev = 0` | returns `100` | raises `ValueError` |
| body length | 1 line | 8 lines |

**The result does not say what was expected, and that is the finding.** The
hypothesis behind the amendment — *short code is wrong code* — was **not
supported**: upstream's one-liner is correct on every well-formed input, including
both wrap directions. Brevity did not cost correctness here.

What it did cost is behaviour on garbage. On three of four malformed readings
upstream returns a **plausible number** — `-4364` ticks of movement that never
happened — and odometry integrates it without noticing. The amended version
stops. For a wheel encoder that difference is the whole point, and it is not
visible in any test of well-formed input.

One honest caveat on the other side: the amended version validates
`counts_per_rev`, which does not enter the arithmetic. **Both** agents noticed
the parameter is unused; upstream proposed deleting it, the amendment kept and
guarded it. That is the amendment's failure mode — spending lines on a
parameter that should arguably not exist — and clause 3's "not permission to
pad" is the line holding it back.

A third difference neither doctrine decides: at a movement of exactly half the
register (32768) the two disagree in sign (`-32768` vs `+32768`). The input is
genuinely direction-ambiguous, so neither is wrong. Worth knowing before either
one integrates into a position estimate.

**Scope of this evidence.** One task, one sample per arm, one model. It shows
the mechanism is real and names what it buys; it is not a measurement of how
often it pays. Reproduce with `wheel_delta` or a task of your own before
treating the effect size as known.

