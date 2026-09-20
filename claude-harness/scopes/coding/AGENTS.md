# scope · coding — implementation, refactor, debugging

**Read first.** `modes/execute.md`, `modes/audit.md`, `protocols/coding.md`,
`protocols/validation.md`, `protocols/debugging.md`, `styles/code.md`.

**Purpose.** Turn a decided design into the smallest correct working change, and
prove it works — not assert it.

**Contract.**
- **The ROBOTIS Programming Style Guide is mandatory** for any file in C, C++,
  Python, JavaScript/TypeScript, HTML/CSS, or any ROS 2 package file. Load
  `skills/robotis-style/SKILL.md` and its language reference *before* writing —
  not after, as a cleanup pass. Third-party code keeps its own style.
- Read the target before editing it; never edit blind.
- Smallest correct change; reuse before adding; match the surrounding code.
- After any edit, run the repo's tests/linters/formatters; if none exist, say so
  and validate structurally (`protocols/validation.md`).
- A behavior claim is *run*, not asserted (`kernel/tooling_protocol.md`).

**Local invariants.**
- **Read what the code says about itself, first.** In someone else's codebase
  the `TODO` / `FIXME` / `REGRESSION` / `KNOWN ISSUE` notes, the config
  comments, the `CHANGELOG` and `git log`/`blame` on the crux files are
  **primary evidence, not background** — a developer who already hit this
  failure and wrote it down outranks any hypothesis you can form in an hour.
  Harvest before theorizing (`protocols/debugging.md` step 3), and cite what you
  found with `path:line` or say the code is silent.
- **Evidence map before changing:** changed surface, entry point, owner boundary,
  caller, callee, sibling, tests. Know what you're touching.
- **One canonical path.** Prefer fixing the real path over adding a compatibility
  shim or a parallel code path.
- **No silent growth.** After edits, check `git diff --numstat`; if non-test size
  grew, justify it or trim it.
- New abstractions, dependencies, or files must earn their place with a stated
  reason (`kernel/operating_principles.md`).

**Guardrails.**
- "It should work" is not "it works." Only claim what you ran
  (`kernel/anti_patterns.md`).
- Don't refactor unrelated code while doing a narrow task.
- Guard irreversible/outward actions; confirm before destructive ops.

**Verification.** The repo's own checks first; then reconcile against the request
(`modes/audit.md`). Best fix, not merely a plausible one. Quality verdicts that
matter get an independent vantage (a test that can fail, a fresh review), not
self-review. **Style compliance is the linter's output** (`ament_cpplint`,
`ament_flake8`, `ESLint`), never an assertion that the guide was followed.

**Committing.** Every commit carries a DCO `Signed-off-by:` trailer *and* a GPG
signature, and the signing identity is set `--local` so a personal global
identity is never inherited. `protocols/commit_policy.md` is the rule; the
`.githooks/` gate enforces it. `--no-verify` is a policy violation.

**Anti-patterns.** ❌ Editing before reading. ❌ Claiming tests pass without
running them. ❌ Scope creep / speculative generality. ❌ Compatibility cruft where
one clean path would do.

**Routes to.** modes: `execute`, `audit`, `layer`. protocols: `coding`,
`validation`, `debugging`, `file_management`. skills: `mcp-builder`,
`agent-browser`, and language/tool-specific skills as needed.
