# Known Issues — <project name>

> Known bugs, limitations, and gotchas, as a dependency graph (not a flat
> list). So they aren't rediscovered the hard way, and so a question blocked on
> an issue is visible. Compute the ready/blocked/superseded view with
> `python3 claude-harness/scripts/work_graph.py <this project>/memory`.

- **ID** — `I1`, `I2`, … (stable; referenced by other items' `blocked_by`).
- **blocked_by** — IDs (`Q…`/`I…`) that must close before this can be fixed;
  `—` if none.
- **supersedes** — the ID this replaces; set it on the replacement and close the
  old one (Status `superseded`).

| ID | Issue | Impact | Workaround | blocked_by | supersedes | Status |
|----|-------|--------|------------|------------|------------|--------|
| I1 | <issue> | <who/what it affects> | <if any> | — | — | open |
