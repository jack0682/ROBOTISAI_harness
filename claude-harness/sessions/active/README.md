# sessions/active

Worklogs for sessions that are still open. `scripts/new_session.py` writes here,
and the `session_start` hook resumes the most recent one that is not older than a
fortnight — it used to resume the most recent one full stop, which meant every
session for two months opened with a July checkpoint reading "Next action: commit
+ push", because `git checkout` rewrites mtimes and a finished worklog reads as
minutes old on a fresh clone.

Finished worklogs move to `../archived/`, which the hook deliberately does not
scan. The contents of this directory are deployment state and are not tracked.
