---
description: The way in. Works out where you are — fresh clone, first setup, returning session, or something broken — and does the right thing. Type this when you do not know what to type.
argument-hint: [what you want to do, in plain words — or "check" to diagnose]
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

The user typed `/harness`. They may know nothing about this harness, or they
may have used it for weeks. **Work out which, then act — do not hand them a
menu of commands.**

What they said, if anything: $ARGUMENTS

---

## Step 0 — detect the situation. Check, never ask.

```sh
pwd; ls
git remote -v 2>/dev/null
git config --local --get user.email 2>/dev/null
ls claude-harness/.bootstrap-pending 2>/dev/null
ls claude-harness/sessions/active/*.md 2>/dev/null | wc -l
grep -c 'status: active' claude-harness/registry/projects.yaml 2>/dev/null
python3 claude-harness/scripts/validate_harness.py 2>&1 | tail -1
```

| what you see | situation | go to |
|---|---|---|
| `$ARGUMENTS` says check / broken / 확인 / 점검 | diagnose | **D** |
| `validate_harness` failed | broken install | **D** first, then re-detect |
| remote is the harness's own repo, no other project here | inside the template clone | **A** |
| `.bootstrap-pending` exists, or no active project | installed, not yet initialised | **B** |
| active project, no session files | set up, never worked in | **C**, skipping the recap |
| active project, session files exist | returning session | **C** |

Announce the situation in one line before acting, so they can correct you if
the detection is wrong.

---

## A — They are inside a clone of the harness template

This is the common mistake. The harness is **not used from inside its own
clone**; it is dropped into the workspace where their real work lives.

Say that in one sentence, then ask the one thing you cannot determine:

> Which directory holds the work you want the harness to govern?

Take the path and run it:

```sh
./bootstrap.sh <their-workspace> --fresh
```

Then tell them to open Claude Code **in that workspace** and type `/harness`
again. Do not try to continue from the clone — the bridge lives in the
workspace, not here.

---

## B — Installed, needs setting up

Do all three yourself, in this order, reporting as you go.

### B1. Signing identity — first, because it blocks everything

Commits here are blocked until a repository-local identity exists. Discovering
that at the end of a day's work is the failure this ordering prevents.

Report the current state before changing it:

```sh
git config --local --get user.name
git config --local --get user.email
git config --local --get user.signingkey
git config --global --get user.email   # to show, never to adopt silently
```

If all are set, verify and move on. Otherwise:

- **Name and email.** Ask. Do not guess and do not silently inherit the global
  value — show it and ask whether it is right for this repository. It becomes
  every commit's `Signed-off-by:` and every new file's `Author:` line.
- **GPG key.** `gpg --list-secret-keys --keyid-format=long`. If keys exist,
  show each one's id, uid and date and let them choose — picking for them
  produces commits GitHub marks `Unverified`, discovered much later. If none
  exists, offer `gpg --full-generate-key` (RSA 4096, their work email) and say
  plainly it needs a passphrase they must remember.

```sh
git config --local user.name       "<Name>"
git config --local user.email      "<email>"
git config --local user.signingkey <KEY_ID>
git config --local commit.gpgsign  true
git config --local tag.gpgsign     true
```

Then prove it, rather than asserting it:

```sh
echo probe | gpg --local-user <KEY_ID> --sign --output /dev/null && echo "signing OK"
.githooks/pre-commit && echo "gate passes"
```

Tell them the public key still has to be added to GitHub — you cannot do it:
`gpg --armor --export <KEY_ID>` → Settings → SSH and GPG keys.

**If they give you a passphrase**, use it only to unlock the key into
`gpg-agent`: a mode-600 temp file, `--pinentry-mode loopback
--passphrase-file`, then delete it. Never echo it, never leave it in a file
that could be committed.

### B2. Read the workspace — run `/harness-init`

It reads the workspace as a whole (what it is, build and test entry points,
languages, existing conventions), fills the project overlay, and clears
`.bootstrap-pending`. Do it; do not instruct them to.

### B3. Capture what they actually want

`/harness-init` establishes what the code **is**. Only they can say what it is
**for**. Ask **at most four questions in one message**, with your best reading
offered as the default so they confirm rather than compose:

- **Goal** — what has to be true when this is finished, in one sentence.
- **Scope** — what is in this piece of work, and what is explicitly *not*.
- **Done** — what will be run or looked at to decide it worked: a test, a
  measurement, a review. If they cannot name one, say so; that is itself the
  finding (`modes/verify.md`).
- **Hard constraints** — hardware, deadline, platform, an interface that must
  not break, data that may not be touched.

Never ask what you can read: language, build system, layout, test framework.

Write the answers into the active project's overlay —
`projects/<name>/PROJECT.md`, `context.md`, `constraints.md`, `glossary.md` —
and put everything unresolved into
`projects/<name>/memory/open_questions.md`, one item each. Set
`verification_mode` and `validation.commands` in `project.config.yaml` honestly — name only commands you have actually run, or
declare the project `analysis_only`. **A gate configured to check nothing is
worse than no gate, because it reports success.**

Then go to **C** and start working.

---

## C — Working: a returning session, or the first one

### C1. Reconstruct the state — read, do not re-derive

The `session_start` hook already injected the latest worklog's `STATE`, its
`Next Step`, the most recent checkpoint, unsettled claims and the work graph.
**Use that.** Then fill only the gaps it cannot cover:

```sh
git status -sb
git log --oneline -5
git log --oneline @{u}.. 2>/dev/null     # committed but never pushed
ls -t claude-harness/sessions/active/*.md 2>/dev/null | head -3
```

Read the most recent worklog in full. Its `Next Step` is the single most
load-bearing line here — the previous session wrote it so this one would not
have to guess.

Report anything that decayed while they were away, **before** proposing work:
uncommitted changes the worklog does not mention; commits never pushed; a
`settled` claim past its `review_at` (it is not established any more); a
validator that passes no longer.

### C2. Recap, short — skip entirely if there is no history

> **Where it stands.** <two or three lines from the last STATE>
> **In flight.** <uncommitted / unpushed, or "clean">
> **Open.** <ready items, blocked ones and why>
> **Next step on record.** <the previous session's Next Step, verbatim>

If `$ARGUMENTS` points somewhere else, take that as the new direction — and say
plainly that it diverges from what was recorded, so the worklog gets corrected
rather than silently contradicted.

### C3. Do the work

Load the scope and mode the task calls for (`ROUTING.md`). Open files with
`Read`/`Edit`, not `cat` — the path-scoped rules, including the ROBOTIS style
guide, fire on the tool, not on the shell.

Before the session ends, write or update the worklog with
`/harness-checkpoint`: current state, what was verified and how, the next
action.

---

## D — Diagnose

Run all of it; do not stop at the first failure.

```sh
python3 claude-harness/scripts/validate_harness.py
( cd claude-harness && python3 -m unittest discover -s tests -q 2>&1 | tail -3 )
ls CLAUDE.md .claude/settings.json .claude/skills .claude/rules/ 2>&1
for h in $(grep -o 'hooks/[a-z_]*\.py' .claude/settings.json | sort -u); do
  test -f "claude-harness/$h" && echo "ok   $h" || echo "MISSING $h"
done
git config --local core.hooksPath; git config --local commit.gpgsign
test -x .githooks/pre-commit && test -x .githooks/commit-msg \
  && echo "githooks executable" || echo "GITHOOKS NOT EXECUTABLE"
git config --local --get user.signingkey
python3 claude-harness/scripts/check_license_header.py 2>&1 | tail -2
grep -c 'status: active' claude-harness/registry/projects.yaml
```

| symptom | meaning | fix |
|---|---|---|
| hook file missing | wired to nothing, fails silently every call | `install_bridge.py` |
| fewer than 7 hooks | a regeneration dropped one — the commit guard is the usual casualty | regenerate, re-check |
| `robotis-style.md` rule absent | the style guide no longer fires on the file | regenerate |
| `core.hooksPath` unset, or hooks not executable | commit gates inert; unsigned commits pass | `git config --local core.hooksPath .githooks`; `chmod +x .githooks/*` |
| local identity unset | commits blocked — correct | **B1** |
| headers missing | new files lack the licence header | `check_license_header.py --fix` |
| more than one `status: active` | the gates resolve nothing and silently disarm | leave exactly one |

Then prove a gate still bites, because structure passing is not enforcement
working:

```sh
printf 'Added something real\n' > /tmp/probe.msg
.githooks/commit-msg /tmp/probe.msg; echo "exit=$? (non-zero is correct)"
rm -f /tmp/probe.msg
```

Repair the mechanical failures yourself. **Do not** invent a signing identity,
pick a GPG key, or choose which project is active — those are the user's.

Lead the report with anything meaning **the harness is not actually enforcing
something**: a broken gate is worse than an absent one, because it looks fine.

---

## Rules for this command

- **Never list every command.** They need two: `/harness` and
  `/harness-checkpoint`. Mention a third only if it is the immediate next step.
- **Run things instead of instructing.** The only things you must ask for are
  the workspace path, the signing identity, and the four requirement questions.
- **Do not lecture about the methodology.** They meet it through the work.
- Do not stop having only explained. End by doing the next thing, or by asking
  the one question that unblocks it.
- Explain in the language the user wrote in.
