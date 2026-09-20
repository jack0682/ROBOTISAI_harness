# Protocol · Debugging

> Layer 1 — universal per-task procedure. No project specifics.

## Steps
1. **Reproduce.** Get the failure to happen reliably before theorizing. If you
   can't reproduce it, say so — you're diagnosing a report, not a bug.
2. **Capture the evidence.** Exact error, stack trace, inputs, environment. Read
   them; don't skim.
3. **Harvest what the system says about itself.** Before forming a single
   hypothesis about someone else's code, read its own record: `TODO` / `FIXME` /
   `XXX` / `HACK` comments near the failing path, `REGRESSION` and `KNOWN ISSUE`
   notes, config comments, `CHANGELOG`, and `git log` / `git blame` on the crux
   files. **A developer's documented failure is primary evidence, not
   background** (`modes/verify.md` → primary-source gate). On the testbed that
   produced this rule, the single most valuable artifact was a dated REGRESSION
   comment in the repo's own yaml that named the failure outright; an hour of
   hypothesis-forming would have re-derived it badly. Cite what you found with
   `path:line`, or state that you looked and the code says nothing.
4. **Isolate.** Narrow to the smallest input/code path that still fails. Bisect by
   change, time, or component.
5. **Form competing hypotheses.** List the plausible causes; note evidence for and
   against each. Don't anchor on the first.
6. **Find root cause vs. workaround.** Decide explicitly which you're delivering and
   say why. A workaround is labeled as one.
7. **Fix and verify.** Apply the fix; confirm the original reproduction now passes
   and you didn't break adjacent behavior.

## Output
- State: the root cause, the fix, and the evidence the fix works.
- If unresolved: best current hypothesis, what's been ruled out, next probe.

## Don'ts
- Don't claim a cause you haven't shown.
- Don't fix by coincidence — understand *why* the change works.
- Don't suppress a symptom and call the bug fixed.
