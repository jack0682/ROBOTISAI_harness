# Evaluation · Code Quality

> A self-review gate. Run before claiming a code change is done.

## Checklist
- [ ] **Correct** — does what's required; edge cases and error paths handled.
- [ ] **Minimal** — smallest change that solves it; no unrelated edits.
- [ ] **Reuses** — uses existing utilities/patterns rather than re-inventing.
- [ ] **Fits in** — matches surrounding naming, style, and idioms.
- [ ] **No regressions** — adjacent behavior and contracts intact.
- [ ] **Tested** — new behavior is covered; tests would catch a regression.
- [ ] **Verified for real** — actually ran/tested; output reported truthfully.
- [ ] **Runnable** — the command to run/verify is provided.
- [ ] **Clean** — no dead code, debug prints, commented-out blocks, unused imports.

## Fail conditions (any one = not done)
- "Should work" without having run it.
- New dependency or abstraction with no stated justification.
- Tests claimed to pass without being run.
