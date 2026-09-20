# evaluation/ — does the harness actually work?

Two kinds of check live here:

**1. Quality rubrics** (the `*.md` files) — exit gates applied to *work product*:
`answer_quality.md`, `code_quality.md`, `research_quality.md`,
`hallucination_check.md`, `final_acceptance.md`. Each emits a verdict, never a
silent skip (`final_acceptance.md`). These are referenced by `modes/audit.md` and
the protocols.

**2. Behavioral tests** (the subdirectories) — do the harness's own routing and
skills *fire when they should and stay quiet when they shouldn't*? Adapted from a
meta-factory reference's should-trigger / should-NOT-trigger discipline:

- `trigger_tests/` — prompts that **should** route to a given mode/scope/skill.
  A miss means the description/routing is too weak.
- `near_miss_tests/` — prompts that look related but should **not** trigger a
  given mode/scope/skill. A false fire means the trigger is too greedy.

These are specification cases, run by reading: take the prompt, decide what
`ROUTING.md` + the relevant `description` frontmatter would select, and compare to
the expected routing. They are intentionally lightweight — the goal is to catch
drift (a mode that stops triggering, a skill that grabs unrelated work), not to
build an automated test rig. Structural integrity of the harness itself is
checked separately by `scripts/validate_harness.py`, and the golden set's own
references (every `expect_*` / `should_not` names a real, *active* mode/scope/skill,
never an archived one) by `evaluation/check_routing_tests.py` — so archiving a skill
turns a stale expectation into a loud, fixable failure.

Add cases as real routing mistakes are found — that is the highest-signal source.
