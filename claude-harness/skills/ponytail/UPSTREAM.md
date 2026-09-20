# ponytail — vendored from upstream

**Source:** <https://github.com/DietrichGebert/ponytail> · MIT License ·
Copyright (c) 2026 DietrichGebert · vendored 2026-09-20 at upstream
`2026-09-14`.

The full MIT notice is in `LICENSE` beside this file, as the licence requires.

**The bodies are upstream's text, unmodified.** Do not edit them to fit local
taste — raise it upstream, or wrap it here.

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
