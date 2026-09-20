# Contributing

This repository is the ROBOTIS AI team's harness. Two things are enforced by
tooling rather than by review: **how code is written** and **how it is
committed**. Both fail closed.

---

## First-time setup — do this before your first commit

```sh
git config --local user.name       "Your Name"
git config --local user.email      "you@robotis.com"
git config --local user.signingkey <YOUR_GPG_KEY_ID>
git config --local commit.gpgsign  true
```

`--local`, not `--global`. A global identity in `~/.gitconfig` is your personal
one and git will stamp it on a team commit without telling you. Setting it on
the repository is what makes team attribution correct.

Find your key id:

```sh
gpg --list-secret-keys --keyid-format=long
```

No key yet:

```sh
gpg --full-generate-key                       # RSA 4096, your @robotis.com address
gpg --armor --export <KEY_ID>                 # paste into GitHub → SSH and GPG keys
```

`core.hooksPath` is already set to `.githooks`, so the gates are active as soon
as you clone. Nothing else to install.

---

## Commit policy

Full rule: `claude-harness/protocols/commit_policy.md`.

Every commit must carry, without exception:

1. **A DCO sign-off** — `git commit -s`, producing
   `Signed-off-by: Your Name <you@robotis.com>`, matching your configured
   identity exactly.
2. **A GPG signature** — automatic once `commit.gpgsign` is true.
3. **A capitalised imperative subject** — `CHANGELOG.rst` is generated from
   commit subjects at release time (ROBOTIS ROS Style Guide §4.6).

```
Added zero-copy path to the diff-drive controller
Fixed odometry drift when the encoder wraps
Removed the deprecated buzzer parameter
```

The sign-off and the signature are not interchangeable: the **signature** proves
who committed, the **sign-off** attests you have the right to submit the work.

### No AI co-authors

A commit must **never** credit an AI assistant — no `Co-authored-by:` naming
Claude, Anthropic, Copilot, ChatGPT, Gemini, Codex, Cursor, Devin or Aider, and
no `Generated with <tool>` footer.

An agent is a tool, not an author. Authorship and the DCO attestation belong to
the person who signed off. **This rule overrides the harness and any coding
assistant's own attribution default.** Human co-authors are welcome as usual.

### `--no-verify` is a policy violation

It bypasses every gate above. If a hook is wrong, fix the hook.

---

## Code style

**The ROBOTIS Programming Style Guide is mandatory** for C, C++, Python,
JavaScript/TypeScript, HTML/CSS and ROS 2 package files.

- Skill: `claude-harness/skills/robotis-style/SKILL.md`
- Per language: `references/{cpp,c,python,ros,javascript}.md`

The four that are wrong most often:

| | C / C++ | Python | JS / TS |
|---|---:|---:|---|
| indent | **2** spaces | **4** spaces | **2** spaces |
| line limit | **100** | **99** | **100** |
| quotes | `"` double | `'` single | `'` single |

Plus: never a tab; comments in English; every file ends with a blank line.

Third-party code keeps **its own** style — do not impose ours on a vendored
project.

### Licence header — every source file

All code here is **Apache License 2.0**. Every source file opens with the header
in `references/license-header.md`, ending in an `Author:` line naming **you**,
taken from your local git identity.

```sh
python3 claude-harness/scripts/check_license_header.py         # report
python3 claude-harness/scripts/check_license_header.py --fix   # insert
```

`pre-commit` runs this over your staged files, so a missing header blocks the
commit.

ROS `.msg`, `.srv`, `.action` and `.launch.py` files carry no header.

---

## What the gates will tell you

Every refusal names the exact command that fixes it. Read it rather than
working around it — a bypassed gate makes the next commit's provenance
unverifiable, which is what all of this exists to prevent.

| gate | when |
|---|---|
| `.githooks/pre-commit` | identity / signing key unset, missing licence header |
| `.githooks/commit-msg` | no sign-off, mismatched sign-off, AI co-author, empty subject |
| `commit_guard.py` | an agent trying to commit without identity, with `--no-verify`, or with an AI co-author |
