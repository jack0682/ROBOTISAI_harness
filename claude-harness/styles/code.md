# Style · Code

> Layer 2 — universal presentation convention. No project specifics.
> Language- or project-specific conventions go in a skill or a project override.

## Match the surroundings first
- The strongest style rule: write code that reads like the code already in the
  file — its naming, comment density, spacing, and idioms. Local consistency beats
  any global preference.

## Clarity
- Clear names over short names. The name should say what the thing is/does.
- Small, single-purpose functions. Avoid deep nesting; prefer early returns.
- Don't comment *what* the code does (it says that itself); comment *why* when the
  reason isn't obvious.

## Robustness
- Handle the error paths and edge cases, don't just the happy path.
- Fail loudly and informatively rather than silently.

## Restraint
- No speculative generality. Solve the present need.
- No dead code, no commented-out blocks left behind, no unused imports.

## Don'ts
- Don't reformat unrelated code in a focused change.
- Don't introduce a new style into a file that has an established one.
