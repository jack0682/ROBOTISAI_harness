---
paths:
  - "**/controllers/**"
  - "**/control/**"
  - "**/*controller*.{py,cpp,hpp,c,h}"
  - "**/*.launch.py"
  - "**/config/*.{yaml,yml}"
---

# You are in a feedback system — load the control scope

Read `claude-harness/scopes/control/AGENTS.md` before reasoning about behavior
here, and run items 10–12 of `claude-harness/modes/math_lock.md` on any claim
about stability: closed-loop stability, energy/passivity, and
delay/sampling/bandwidth.

The failure this scope exists for: two components that are each correct on their
own, unstable together. "Being right at rest is not evidence about motion", and
a limit cycle is evidence about the loop, not about one gain.

> This rule fires on the file. It is finding F2 in
> `claude-harness/docs/testbed_findings.md`, made to fire at the moment it
> applies rather than only when the prompt happens to say "oscillates".
