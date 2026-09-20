# Evaluation · Final Acceptance

> The last gate before declaring a task complete. Composes the other rubrics.

## Universal acceptance
- [ ] **Goal met** — the actual requested outcome is achieved, verified against the
      original request (not against the plan).
- [ ] **Verified, not assumed** — the relevant quality rubric
      (`answer_quality.md`, `code_quality.md`, or `research_quality.md`) and
      `hallucination_check.md` pass.
- [ ] **Reported faithfully** — what's done, what's not, and what failed are stated
      plainly. No overclaiming.
- [ ] **Scope honored** — delivered what was asked; adjacent issues noted, not
      silently folded in.
- [ ] **Constraints respected** — kernel rules and any active project constraints
      were not violated; overrides (if any) were explicit.
- [ ] **Reproducible** — how to run/verify is recorded; long work is checkpointed.

## Every gate emits a verdict — never a silent skip
- Each check above resolves to one explicit, recorded state — never left blank:
  - **pass** — ran, met the bar.
  - **fail** — ran, did not meet the bar; blocks completion.
  - **not applicable** — ran the judgment, nothing here to check. This is a
    *recorded verdict*, not an absence. "Not applicable" and "didn't check" are
    different things and must never look the same.
  - **blocked** — could not run (missing input or tool); name what's missing.
- A gate with no recorded verdict counts as not run, i.e. not done. Silently
  omitting a check reads as a pass it never earned — forbidden
  (`uncertainty_protocol.md`: a gap hidden is a liability).
- Record what each verdict rests on — what was checked, against what — so the
  user could re-run it. A verdict with no evidence behind it is itself a "should
  work," not a "verified."

## The honesty question
> Would this stand up if the user re-ran every check themselves? If any "done" rests
> on "should work" rather than "I verified it," it is not done — say so.

## Outcome
- ✅ Complete and verified — state it plainly.
- 🟡 Partial — say exactly what remains.
- 🔴 Blocked — say what blocked it and what's needed.
