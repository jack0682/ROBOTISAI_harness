# Protocol · Review

> Layer 1 — universal per-task procedure. No project specifics.

Use when reviewing code or written work (yours or someone else's).

## Steps
1. **Know the intent.** Understand what the change is supposed to do before judging
   how it does it. Review against the goal, not your preferences.
2. **Read the actual diff/work,** not a summary of it.
3. **Check in priority order:**
   - **Correctness** — does it do the right thing? Edge cases, error paths, off-by-ones.
   - **Regressions** — does it break adjacent behavior or contracts?
   - **Tests** — is the new behavior actually covered? Would the tests catch a regression?
   - **Maintainability** — clarity, naming, duplication, complexity that doesn't earn itself.
   - **Style** — last, and least.
4. **Rate severity.** Separate blocking defects from nits. Don't drown a real bug in
   style comments.
5. **Verify your own findings.** Before reporting a bug, confirm it's real — trace it,
   don't assume. Mark uncertain findings as uncertain.

## Output
- Use `templates/review_report.md`. Each finding: location, severity, why it matters,
  suggested fix.
- Lead with blocking issues.

## Don'ts
- Don't invent problems to seem thorough.
- Don't rewrite to taste; respect working code that differs from your style.
