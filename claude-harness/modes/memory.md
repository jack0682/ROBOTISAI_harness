# mode · memory — distill a session into reusable knowledge

> The self-improvement loop. Adapted from a strong self-improving-agent reference:
> after work, a *separate* review decides what — if anything — should outlive this
> session, with a strict guard on what must **not** be persisted.

**Trigger.** End of a substantive session; a checkpoint; a decision worth keeping;
"이거 기억해둬"; a pattern you've now done more than once. The closeout step of any
long task (`KERNEL.md` → self-audit).

**Input.** What this session actually did — decisions, dead-ends, patterns,
corrections the user made, project state.

**Operations — the distillation review.** Ask, in order:
1. **Did a reusable pattern appear?** A way of working that would help next time.
2. **Is it worth persisting as memory?** A decision + its why, a project state, a
   sharpened claim/definition, a live constraint.
3. **Should an existing skill be patched?** (Most sessions that change *how* you
   work patch an existing skill, not create one.)
4. **Is it general enough to be a new skill?** Rarely — only when no existing
   skill or umbrella covers it.
5. **Would persisting it be harmful?** Apply the guard below *before* writing.

**The persistence guard — what NOT to write as a durable rule.**
- ❌ An environment-specific or transient failure ("the build broke today").
- ❌ A one-off error or an accidental workaround.
- ❌ An over-narrow single incident dressed as a general rule.
- ❌ **A negative self-capability claim** ("X can't do Y", "tool Z doesn't work")
  — the most dangerous capture; it silently forecloses the option forever.
  Record the *specific error and condition*, never a blanket verdict.
Persist the **fix**, the **missing config**, or the **class-level rule** instead.

**The action ladder (prevents skill sprawl).** When something *is* worth keeping:
1. patch the already-loaded skill →
2. patch the umbrella skill that owns this area →
3. add a support file (`examples/`, `failure_modes.md`) to an existing skill →
4. only then create a new skill.

**Claims have an enforced lifecycle.** A claim worth persisting goes to
`memory/claims/` as `scope: claim` with a `status` (open → settled → stale). It
may only be `settled` when it carries the `threshold` that would refute it, the
`evidence` that met it, and a dated `review_at` expiry — `validate_harness.py`
and the stop gate block an unearned or expired "settled" (`memory/claims/
README.md`, `scripts/_claims.py`). This is where "verification over agreement"
becomes a checked invariant, not a posture. A claim under construction stays
`open`; settle it only after `math_lock`/`counter`/experiment actually earn it.

**Memory vs skill — the split.**
- **memory/** = *who the user is and what the current state is* — decisions,
  project state, preferences, live claims. → `memory/{decisions,project_states,
  patterns,claims}/`.
- **skills/** = *how to do this class of task* — reusable procedure. A repeated
  user *correction* about how to work belongs in the governing skill, not just a
  memory note.

**Write mechanics.** Each memory item is a file with frontmatter
(`scope / importance / review_at / supersedes / source / signature`) and a
one-line entry in `memory/MEMORY.md` (the index). Prefer **supersede / archive
over delete** (move to `memory/archived/`, set `supersedes`). A mid-session write
goes to disk immediately but the *loaded* context refreshes at the next session
boundary — write-through, snapshot-stable.

**Output.** Zero or more memory items written + indexed; zero or more skill
patches (per the ladder); a one-line distillation note in the session file. "Nothing
worth persisting" is a valid, common result — say it rather than inventing an entry.

**Tooling.** `scripts/distill_session.py` scaffolds this review against the audit
log; `memory/README.md` holds the schema.

**Loop position.** *Distillation* — the loop's return arrow. What it writes
becomes the next session's loaded context, so the guard above is load-bearing.
