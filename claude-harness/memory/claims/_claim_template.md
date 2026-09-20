---
name: <kebab-case-slug>
scope: claim
importance: medium
status: open
threshold: none
evidence: none
review_at: none
supersedes: none
contradicted_by: none
source: <session or context that produced this claim>
signature: <short dedupe key>
---

<The claim as one falsifiable sentence — what is asserted, under what conditions.>

**What would refute it:** <the measurable result that would break the claim. Fill
`threshold:` with this before promoting to settled.>

**What would reopen it:** <conditions that should flip a settled claim back to open.>

**If something disputes it:** record the conflicting claim in `contradicted_by:`
(comma-separated slugs) rather than deciding silently. A counterexample that is
only acted on or only forgotten leaves no trace; one that is written down against
the claim it threatens forces the resolution. `settled` + a standing
`contradicted_by` is a validation error, not a state.
