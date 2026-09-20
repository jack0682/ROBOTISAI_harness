# protocol · commit_policy — what a commit in this repository must carry

**Authority note.** The no-AI-co-author rule below is a **team standing rule and
it outranks the harness**, this assistant's platform defaults, and any tool's
attribution behaviour. Where they disagree, this file wins. The rest of this
protocol sits at normal protocol authority (`KERNEL.md` → Authority order).

Enforced in three independent places, so that no single bypass is enough:

| layer | file | what it catches |
|---|---|---|
| agent | `scripts/hooks/commit_guard.py` (PreToolUse: Bash) | the agent running `git commit` without identity, with `--no-verify`, or with an AI co-author |
| git | `.githooks/pre-commit` | identity and signing key not configured |
| git | `.githooks/commit-msg` | missing/mismatched sign-off, AI co-author, empty subject |

`core.hooksPath` is set to `.githooks`, so the hooks are versioned with the
repository rather than living in an un-shareable `.git/hooks`.

---

## 1. Signing identity is repository-local

```sh
git config --local user.name       "<Name>"
git config --local user.email      "<name>@robotis.com"
git config --local user.signingkey <GPG_KEY_ID>
git config --local commit.gpgsign  true
```

**`--local`, not `--global`.** A global identity in `~/.gitconfig` is a personal
one, and git will silently stamp it on a team commit if the repository does not
override it. That is the exact failure this guards: the repository this one was
derived from carried 34 commits under a personal identity inherited that way.

**Until these are set, no commit happens.** An agent working in this repository
must *ask the user* for the name, email and key — never guess, never fall back
to the global identity, never invent a placeholder.

## 2. Every commit is GPG-signed

`commit.gpgsign = true` and `tag.gpgsign = true`. `pre-commit` verifies the
configured key actually exists in the local keyring, so a commit cannot fail
halfway through signing.

## 3. Every commit carries a DCO sign-off

```
Signed-off-by: <Name> <<name>@robotis.com>
```

Added by `git commit -s`. It must match `user.name` / `user.email` **exactly**.

The sign-off and the signature are not interchangeable:
- the **signature** proves *who committed*;
- the **sign-off** attests *that they have the right to submit the work*.

Both are required.

## 4. No AI co-authors — overrides everything else

An agent is a tool, not an author. A commit must not carry:

- `Co-authored-by:` naming Claude, Anthropic, Copilot, ChatGPT/OpenAI, Gemini,
  Codex, Cursor, Devin, Aider, or any `noreply@` address of such a service;
- a `Generated with <tool>` footer.

Authorship and the DCO attestation belong to the person who signed off. Crediting
a model as co-author misstates who certified the work. **Human co-authors remain
welcome** — the rule targets AI attribution only.

This rule explicitly overrides the attribution default that Claude Code (and any
comparable assistant) would otherwise apply.

## 5. Subject lines are capitalised imperative verbs

`CHANGELOG.rst` is generated from commit subjects at release time
(ROBOTIS ROS Style Guide §4.6), so the subject must read as a changelog entry:

```
Added zero-copy path to the diff-drive controller
Fixed odometry drift when the encoder wraps
Removed the deprecated buzzer parameter
```

`.gitmessage` is installed as `commit.template` and carries this reminder.

## 6. `--no-verify` is a policy violation

It bypasses every gate above. It is denied by `commit_guard`, and using it
outside a genuine tooling emergency is a violation to report, not a shortcut to
take. If a hook is wrong, fix the hook.

---

## When the gate blocks you

Read what it printed. Every failure names the exact command that fixes it. Do
not work around a gate — a bypassed gate makes the next commit's provenance
unverifiable, which is the thing all of this exists to prevent
(`kernel/verification_authority.md`).
