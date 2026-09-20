---
paths:
  - "**/*.{py,ts,tsx,js,jsx,go,rs,c,h,cc,cpp,hpp,java,rb,sh}"
---

# You are editing code — load the coding scope

Before non-trivial work here, read `claude-harness/scopes/coding/AGENTS.md`
(and the modes it routes to). It owns the local invariants, the guardrails, and
the verification this scope owes.

Two of its rules are the ones most often skipped: a behavior claim is **run**,
not asserted; and a quality verdict needs a test that can fail, not self-review
(`claude-harness/kernel/verification_authority.md`).

> This rule fires on the file, not on how the request was worded. `ROUTING.md`
> Step 2 remains the authority on what to load; `route_hint` still covers the
> requests that never touch a file.
