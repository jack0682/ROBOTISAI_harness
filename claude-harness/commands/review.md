---
description: Review code or written work — correctness, regressions, tests, maintainability, with severity ratings.
argument-hint: <target to review, e.g. a diff or file>
allowed-tools: [Read, Grep, Glob, Bash]
---

Follow `claude-harness/protocols/review.md`. Report using
`claude-harness/templates/review_report.md`.

Target: $ARGUMENTS

Understand the intent first. Check correctness → regressions → tests →
maintainability → style, in that order. Rate severity; lead with blocking issues.
Verify each finding is real before reporting it.
