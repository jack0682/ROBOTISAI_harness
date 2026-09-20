---
description: Summarize content faithfully — capture the load-bearing points without distortion or invention.
argument-hint: <what to summarize>
allowed-tools: [Read, Grep, Glob]
---

Follow `claude-harness/protocols/writing.md` and
`claude-harness/kernel/output_protocol.md`.

Target: $ARGUMENTS

Lead with the single most important takeaway. Preserve meaning; don't inflate,
soften, or invent. Keep it proportional to the content's actual importance. Flag
anything ambiguous in the source rather than resolving it silently.
