# memory/ — durable, reusable knowledge

> Not a conversation log. This is the small set of things that should outlive a
> session: decisions and why, working patterns, project state, sharpened claims
> and definitions, live constraints. Sessions (`sessions/`) are the worklog;
> memory is the distillate (`modes/memory.md`).

## Layout

- `MEMORY.md` — the **index**: one line per item, loaded for orientation. Never
  put item bodies here.
- `decisions/` — a decision + why, alternatives rejected, what would reopen it.
- `project_states/` — current state of an ongoing line of work.
- `patterns/` — a reusable way of working (when it's not general enough to be a
  skill yet).
- `claims/` — load-bearing claims with an enforced lifecycle (open → settled →
  stale) and an expiry clock. A `settled` claim must carry its refutation
  threshold, the evidence that met it, and a dated `review_at`; this is checked,
  not assumed (`claims/README.md`, `scripts/_claims.py`).
- `archived/` — superseded items, kept (not deleted) for history.

## Item format

Each item is one markdown file with frontmatter:

```markdown
---
name: <kebab-case-slug>            # unique; matches the filename
scope: <decision|project|pattern|claim|definition|constraint>
importance: <high|medium|low>
review_at: <YYYY-MM-DD | none>     # when to re-check this is still true (or none)
supersedes: <slug | none>          # the item this replaces
source: <session file or context that produced it>
signature: <short content hash/dedupe key>
---

<The fact, decision, or pattern — stated as durably true. For a decision, follow
with **Why:** and **What would reopen it:**. Link related items with [[slug]].>
```

After writing an item, add its one-line pointer to `MEMORY.md`.

For `scope: claim` items the schema is **extended and enforced** — `status`,
`threshold`, `evidence`, and an expiry `review_at` — see `claims/README.md`.
Here `review_at` stops being advisory: a settled claim with no expiry, no
refutation threshold, or no evidence is a gate failure.

## Write discipline (the guard)

What you persist becomes tomorrow's "fact" — so guard the write
(`modes/memory.md`, `kernel/uncertainty_protocol.md`):

- Persist the **fix / config / class-level rule**, never the transient incident.
- **Never** persist a negative self-capability claim ("X can't do Y"). Record the
  specific error + condition instead.
- Mark each item's real epistemic status (verified vs one observation) so a later
  reader inherits its true confidence.
- Prefer **supersede / archive over delete.** To retire an item: move it to
  `archived/`, and set the new item's `supersedes:`.
- Before adding, check `MEMORY.md` for an item this updates — update it rather
  than duplicating. `signature` is the dedupe key.

## Relationship to skills

memory = *who the user is and the current state*. skills = *how to do a class of
task*. A repeated correction about **how to work** belongs in the governing skill
(via the action ladder, `skills/README.md`), not only in a memory note.
