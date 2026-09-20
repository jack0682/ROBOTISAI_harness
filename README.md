# ROBOTIS AI Harness

A drop-in governance layer for Claude Code. Clone it into a workspace and that
workspace gets the team's coding standard, its commit policy, and a research
methodology that is enforced by hooks rather than by remembering.

Built to be **copied per workspace**, not installed once globally: each
workspace carries its own copy, its own project overlay, and its own session
history.

---

## Use it in a workspace

```sh
cd ~/where/your/work/lives                  # the workspace, not a new folder
git clone git@github.com:jack0682/ROBOTISAI_harness.git /tmp/harness
/tmp/harness/bootstrap.sh . --fresh
```

That copies the harness layer in, generates the Claude Code bridge at the
workspace root, wires the commit gates, and validates. Afterwards the workspace
looks like this:

```
your-workspace/
├── CLAUDE.md          ← generated: Claude auto-loads this
├── .claude/           ← generated: hooks, skills symlink, path-scoped rules
├── .githooks/         ← commit gates (DCO sign-off, GPG, no AI co-authors)
├── CONTRIBUTING.md    ← the rules, for humans
├── LICENSE            ← Apache 2.0
├── claude-harness/    ← the harness itself
└── ...your actual work
```

### What happens on first use

Bootstrap does two things a team member should not have to remember:

- **It removes the template's git remote from the workspace.** A workspace copy
  can never push here, so leaving the remote in place only invites an attempt
  that costs tokens and ends in a permission error. The workspace's git becomes
  entirely its own.
- **It leaves a first-run marker.** Until `/harness-init` clears it, every
  session opens by stating that the workspace has not been read yet and that no
  project overlay governs it.

So the first thing to do in that workspace is run **`/harness-init`**. It reads
the workspace as a whole — what it is, its build and test entry points, its
languages, its existing conventions — registers the project overlay, records
what it found, and then clears the marker. Work done before that is work done
blind.

Re-running `bootstrap.sh` is safe — it regenerates the bridge, keeps
hand-edited rules, and leaves existing sessions, memory and projects alone.
`--fresh` is only for a workspace starting clean.

### How updates travel — they do not, by themselves

This repository is the **single upstream**, maintained by its author. Nothing
here changes unless it is changed here.

A workspace copy is **detached on purpose**: `bootstrap.sh` copies the harness
in rather than leaving a clone that tracks this origin, so the workspace's git
is entirely its own and a `git pull` in the workspace will never pull harness
changes over your work. The trade is that a workspace does **not** pick up
upstream improvements automatically.

To bring a workspace up to date, re-clone and re-run:

```sh
rm -rf /tmp/harness && git clone git@github.com:jack0682/ROBOTISAI_harness.git /tmp/harness
/tmp/harness/bootstrap.sh .          # no --fresh: keeps your sessions, memory, projects
```

`claude-harness/scripts/upgrade_harness.py` does the same thing file by file
when you want to see the diff first. What is never overwritten either way is
the deployment-local state — `projects/`, `sessions/`, `memory/`, `registry/`,
`analysis/` — which is what makes a workspace's harness *that workspace's*.

Found a fix or an improvement? Send it upstream here rather than keeping it in
one workspace, or it will be lost the next time that workspace is refreshed.

### Set your signing identity before your first commit

```sh
git config --local user.name       "Your Name"
git config --local user.email      "you@robotis.com"
git config --local user.signingkey <YOUR_GPG_KEY_ID>
```

`--local`, deliberately: a global identity from `~/.gitconfig` would otherwise
be stamped onto team commits without anyone noticing. **Until these are set,
every commit is blocked.**

---

## What it enforces

### Code style — the ROBOTIS Programming Style Guide

Mandatory for C, C++, Python, JavaScript/TypeScript, HTML/CSS and ROS 2 package
files. Third-party code keeps its own style.

| | C / C++ | Python | JS / TS |
|---|---:|---:|---|
| indent | **2** spaces | **4** spaces | **2** spaces |
| line limit | **100** | **99** | **100** |
| quotes | `"` double | `'` single | `'` single |

Never a tab. Comments in English. Every file ends with a blank line. Every
source file opens with the Apache 2.0 / ROBOTIS AI header.

The full guide ships as a skill — `claude-harness/skills/robotis-style/` — with
a reference per language, and `.claude/rules/robotis-style.md` surfaces it
automatically whenever a matching file is opened.

### Commit policy

Every commit carries a **DCO `Signed-off-by:`** and a **GPG signature**, and
**never credits an AI as a co-author**. That last rule outranks the harness and
any assistant's own attribution default.

Enforced in three independent places, so no single bypass is enough:

| gate | catches |
|---|---|
| `.githooks/pre-commit` | identity or signing key unset, missing licence header |
| `.githooks/commit-msg` | no sign-off, mismatched sign-off, AI co-author, empty subject |
| `claude-harness/scripts/hooks/commit_guard.py` | an agent committing without identity, with `--no-verify`, or with an AI co-author |

Full text: `claude-harness/protocols/commit_policy.md` · human version:
`CONTRIBUTING.md`.

### Methodology

`claude-harness/KERNEL.md` and `ROUTING.md` load in every session — a small
always-on spine that routes each request to the right depth: a **scope**
(`scopes/<domain>/AGENTS.md`) for domain invariants, a **mode**
(`modes/<op>.md`) for the cognitive operation. Everything deeper loads on
demand.

Seven hooks make it load-bearing rather than advisory: session context
injection, a routing hint, a kernel-edit guard, the commit guard, a post-edit
audit record, a pre-compact capture, and a stop gate that will not let long work
end without a checkpoint.

---

## Layout

| path | what |
|---|---|
| `claude-harness/KERNEL.md`, `ROUTING.md` | the always-on spine |
| `claude-harness/kernel/` | full principle texts |
| `claude-harness/scopes/` | domain governance (7) |
| `claude-harness/modes/` | cognitive operations (13) |
| `claude-harness/protocols/` | procedure, incl. `commit_policy.md` |
| `claude-harness/skills/` | 68 skills, incl. `robotis-style` |
| `claude-harness/scripts/` | bridge installer, validator, header checker |
| `claude-harness/scripts/hooks/` | the seven enforcement hooks |
| `claude-harness/tests/` | 156 tests |
| `claude-harness/{projects,sessions,memory,registry,analysis}/` | per-deployment state — never synced between workspaces |

## Checking a deployment

```sh
python3 claude-harness/scripts/validate_harness.py        # structure
python3 claude-harness/scripts/check_license_header.py    # licence headers
cd claude-harness && python3 -m unittest discover -s tests -q
```

## Licence

Apache License 2.0 — see `LICENSE`.
