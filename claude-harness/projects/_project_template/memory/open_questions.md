# Open Questions — <project name>

> Unresolved questions that affect the project, as a dependency graph (not a
> flat list). Move to `decisions.md` once answered, and set Status to
> `answered`. Compute what is actually workable now with
> `python3 claude-harness/scripts/work_graph.py <this project>/memory`.

- **ID** — `Q1`, `Q2`, … (stable; referenced by other items' `blocked_by`).
- **blocked_by** — IDs (`Q…`/`I…`) that must close before this is workable; `—`
  if none. An open question with no open blocker is *ready*.
- **supersedes** — the ID this question replaces; set it on the replacement and
  close the old one (Status `superseded`).

| ID | Question | blocked_by | supersedes | Status |
|----|----------|------------|------------|--------|
| Q1 | <question> | — | — | open |
