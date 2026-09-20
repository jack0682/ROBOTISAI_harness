---
description: Attach the harness to an external repository for read-only analysis — a work graph and claims scoped to it, with no bridge, no hooks, and no second active project.
argument-hint: <path-to-repo> [name]
allowed-tools: [Bash, Read, Glob, Grep]
---

Attach, do not deploy. Run:

```
python3 claude-harness/scripts/new_analysis.py $ARGUMENTS
```

It registers an **analysis target** — a work graph
(`analysis/<name>/memory/open_questions.md`, `known_issues.md`) and a claims
area (`analysis/<name>/claims/`) — and writes **nothing into the target
repository**: no `CLAUDE.md`, no `.claude/`, no hooks. The row is registered
`status: analysis`, not `active`, because the hook layer resolves a project only
when exactly one is active and a second active row would silently switch off the
deletion guard, the plan-before-edit reminder and the validation-evidence check
on the *real* project.

Then work the analysis under two rules this mode exists for:

1. **Harvest what the code says about itself before forming a hypothesis** —
   `TODO` / `FIXME` / `REGRESSION` / `KNOWN ISSUE` notes near the failing path,
   config comments, `CHANGELOG`, `git log` and `git blame` on the crux files. A
   developer's documented failure is primary evidence, not background
   (`claude-harness/protocols/debugging.md` step 3).
2. **Reconcile any description of the system against the code before reasoning
   on it.** If the request says how the thing works, check that against the
   artifact and surface the divergence first — a description is usually intent
   or an older revision (`claude-harness/modes/verify.md` operation 8).

Record what you find as you go: open questions with their `blocked_by` edges so
a blocked line of enquiry stays visible, and findings as claims with a
`threshold` that would refute them. A diagnosis of someone else's system is
exactly the kind of claim that ages badly, which is what `review_at` is for.

When the analysis ends, either promote it (`scripts/new_project.py`) or flip the
registry row to `status: archived`. A target left registered as `analysis`
forever is how the registry starts lying.

**Where the notes live, and what travels.** The target lands at
`claude-harness/analysis/<name>/`, inside the harness tree — so your *notes*
about the external repo are carried by a plugin install of this harness, while
the analyzed repository's contents never are (nothing is copied out of it).
`harness.config.yaml` lists `analysis` under `distribution.local_dirs`, so the
clone-sync path never pushes one workspace's analysis into another. If a target
holds anything that must not leave this machine, archive the row and delete the
directory when you are done rather than leaving it to ship.
