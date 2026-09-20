# Protocol · Validation

> Layer 1 — universal per-task procedure. No project specifics.

Use after any change — code, docs, configuration, or the harness itself.
Validation is what separates "it works" from "it should work"
(`kernel/operating_principles.md` §4).

## Mandatory after edits
1. **Existence & syntax.** Every file you created/modified exists and parses
   (loads, compiles, or lints clean for its format).
2. **References resolve.** Paths, links, imports, and names mentioned in the
   changed files point at things that exist.
3. **No new contradictions.** The change doesn't contradict rules, docs, or
   code still in force; if it must, update or explicitly override them.
4. **Run what the repo provides.** If the repository has tests, run the ones
   covering the change; if it has linters/formatters, run them. If it has
   neither, do the structural checks above and **state that no automated
   checks exist** — never imply a green suite you didn't run.

## Recommended when applicable
- Exercise the change end-to-end (run the command, render the doc, load the
  config), not just its parts.
- Check formatting/style consistency with the surrounding material.
- For behavior changes, add or extend a test rather than only hand-checking.

## When the change is to this harness
- Run `python3 scripts/validate_harness.py` (structure, registries, frontmatter,
  kernel-leakage guard) — it must pass.
- Preview inheritance with `python3 scripts/collect_context.py <project> <task>`
  and confirm the load order picks up the change.
- If the bridge inputs changed (`harness.config.yaml`, bridge generators),
  re-run `python3 scripts/install_bridge.py` and confirm idempotence.
- If you archived, added, or renamed a skill / mode / scope, run
  `python3 evaluation/check_routing_tests.py` so the routing golden set cannot
  reference a dead target.

## Reporting
- Say exactly what was validated and how; list what was *not* validated and why.
- A failed check is reported with its output, not smoothed over.
- Before declaring a whole task complete, apply the
  `evaluation/final_acceptance.md` gate (which composes the other rubrics in
  `evaluation/`).

## Don'ts
- Don't claim validation you didn't perform.
- Don't validate only the happy path of a risky change.
- Don't treat "the edit applied" as "the edit works".
