# Protocol · Coding

> Layer 1 — universal per-task procedure. No project specifics. (No "framework X
> nodes look like Y" here — that belongs in a skill or project.)

## Steps
1. **Read first.** Open the files you're about to touch and the code around them.
   Understand the existing patterns, naming, and idioms before writing.
2. **Reuse before adding.** Look for an existing function/utility/pattern that does
   the job. Prefer extending it over introducing a parallel one.
3. **Smallest correct change.** Make the minimal edit that fully solves the problem.
   Don't refactor unrelated code in passing.
4. **Match the surroundings.** New code should read like the code next to it —
   same comment density, naming, and style.
5. **Justify new dependencies.** Adding an external dependency requires a stated
   reason and a check that it isn't already solved in-tree.
6. **Leave it runnable.** Provide the exact command(s) to run and verify the change.

## Verification
- Run it / test it before claiming it works. Report real output.
- If you couldn't run it, say so and say what you'd run.

## Don'ts
- Don't write speculative generality for a concrete need.
- Don't leave the change unverified and call it done.
- Don't invent APIs — check the real signature.
