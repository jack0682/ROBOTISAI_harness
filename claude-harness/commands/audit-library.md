---
description: Report on the skill library's health — which skills actually fire, what the gate said about those sessions, and which descriptions carry no trigger.
argument-hint: (none)
allowed-tools: [Bash, Read]
---

Run `python3 claude-harness/scripts/audit_session.py --library` and read the
result against `claude-harness/skills/README.md` (the action ladder and the
archive-over-delete lifecycle).

The report answers three questions and refuses to answer a fourth:

- **Does any skill fire at all?** Router engagement — the share of gate-evaluated
  sessions in which some skill was used. A healthy library sits near 70–80%; a
  drifted one was measured at 19%. A low number is a routing or description
  problem, not evidence that the skills are bad.
- **Which skills are in play, and how did those sessions end?** Per-skill trials
  and the gate's verdict on each. `verdict` is the stop gate's judgement that the
  evidence the project asked for was present — not a claim about the work's
  quality.
- **Which descriptions carry no trigger phrase?** `evaluation/skill_triggers.py`
  guards quoted trigger phrases against regression; for a skill with none it is
  guarding nothing, and a description with no trigger is the shape most easily
  hidden by a near-duplicate.

**What it will not tell you: which skill to retire.** Contribution
`ĉ(s) = (pass − blocked) / trials` is withheld until `n ≥ 100`. This is not
caution for its own sake — retiring on a thin sample was measured to make a
library *worse* than leaving it alone, collapsing it to two skills. Until the
bar is met, act only on what is structurally visible: duplicate coverage, stale
references to archived skills, and missing triggers.

Report what the numbers support and name what they do not.
