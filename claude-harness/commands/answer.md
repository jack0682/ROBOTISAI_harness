---
description: Answer a question directly and grounded — bottom line first, calibrated, sourced.
argument-hint: <question>
allowed-tools: [Read, Grep, Glob, WebSearch, WebFetch]
---

Follow `claude-harness/protocols/answering.md`. For non-trivial answers use
`claude-harness/templates/answer.md`.

Question: $ARGUMENTS

Lead with the answer, ground claims in checkable sources, and distinguish verified
from inferred. If you don't know, say so.
