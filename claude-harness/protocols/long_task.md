# Protocol · Long Task

> Layer 1 — universal per-task procedure. No project specifics.
> The governing rules — long-horizon assumptions, checkpoint triggers,
> continue-by-default — are kernel law: `kernel/execution_protocol.md`. This
> file is the procedure that implements them in this harness.

Use for work that spans many steps or may outlast a single session. For *forced,
unattended, multi-hour* autonomous runs, see `long_loop.md` (mission file +
driver + the three rails).

## Steps
1. **Decompose into checkpointable units.** Each unit should end in a verifiable,
   resumable state.
2. **Track state explicitly.** Keep a running list of done / in-progress / pending.
   Update it as you go, not at the end.
3. **Keep a worklog in `sessions/`.** One session file per working unit (from
   `sessions/_session_template.md`). Record as you go: files inspected, commands
   run, external references (source + URL), decisions, plan revisions, edits,
   tests/validation, unresolved risks.
4. **Checkpoint on the kernel triggers** (`kernel/execution_protocol.md`), not
   just at milestones. Fill `templates/checkpoint.md` and append it to the
   session file. The checkpoint must name the next action and defaults to
   continue.
5. **Verify incrementally.** Don't defer all verification to the end — confirm each
   unit before building on it (see `protocols/validation.md`).
6. **Handoff-ready.** Write so that someone (or a future session) with no memory of
   this one could pick it up from the checkpoint alone. Use `templates/handoff.md`.

## On resuming
- Read the latest checkpoint/session first. Re-verify any named files/flags/APIs
  still exist before relying on them.
- Reconcile the recorded state with reality before continuing.

## Don'ts
- Don't run a long task with no externalized state — context can be summarized away.
- Don't claim cumulative completion you didn't verify step by step.
- Don't end a checkpoint without a concrete next action while work remains.
