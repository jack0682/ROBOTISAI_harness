# Deployment — how this harness reaches a workspace

## The problem this replaces

`scripts/fleet_survey.py`, 2026-09-20:

```
24 installs · 2 hold unique commits · 7 are plain copies (unrecoverable by git)
```

Distribution was a hand-rolled file sync. Every copy goes dirty — runtime state
(`sessions/`, `shared/`, `.tmux-panes.bak.*`) is written into the governance
tree and is not gitignored — and a dirty copy cannot be `git pull`ed. So copies
were made by hand, and seven of them now have no git at all.

`scripts/upgrade_harness.py` was the answer and it was the wrong shape: it
deleted local files absent upstream, while its sync set omitted `modes/`,
`scopes/`, `KERNEL.md` and `ROUTING.md` — the always-on spine. It has since been
rewritten and tested, but it is still a bespoke updater for a problem the
platform solves.

## Two parts, because one of them cannot be a plugin

A workspace governed by this harness needs two things, and they arrive by
different routes.

### 1. The plugin — capabilities and enforcement

`.claude-plugin/marketplace.json` (repo root) publishes the plugin at
`./claude-harness`; `claude-harness/.claude-plugin/plugin.json` declares it.

```bash
/plugin marketplace add jack0682/ROBOTISAI_harness
/plugin install robotisai-harness@robotisai
```

It carries the **skills**, the **commands**, and all six **hooks** (rooted at
`${CLAUDE_PLUGIN_ROOT}`). Versioning, pinning and update come from the platform:
bump `version` in both manifests and installs update themselves. This is what
replaces the hand sync.

Validate before release:

```bash
claude plugin validate .              # the marketplace
claude plugin validate ./claude-harness   # the plugin
```

### 2. The bridge — the always-on spine

**A plugin does not ship `CLAUDE.md`.** `claude plugin validate` says so
directly: *"CLAUDE.md at the plugin root is not loaded as project context."*
Skills, commands, agents, hooks and MCP servers travel; project context does
not.

The spine — `CLAUDE.md` importing `KERNEL.md` and `ROUTING.md` — is precisely
project context, and it is the part that must be *always on*. Shipping it as a
skill would make it on-demand, which is the one thing it cannot be: a kernel
that loads only when someone thinks to ask for it is not a kernel.

So `scripts/install_bridge.py` stays, and it is not redundant with the plugin.
It writes the spine, the `harness-*` slash commands, the `.claude/skills`
symlink, and the path-scoped scope rules under `.claude/rules/`.

```bash
python3 claude-harness/scripts/install_bridge.py
```

### What this means for `upgrade_harness.py`

It is **not retired yet**, deliberately. The plugin updates the plugin's half;
nothing yet updates a clone's spine except this script. Retiring it now would
strand every clone deployment — including the seven plain copies, which are the
ones least able to recover. It goes when a workspace can get its spine from the
plugin-installed harness rather than from a clone of it.

## Where a plugin install keeps its state

A plugin unpacks to `<config>/plugins/cache/<marketplace>/<plugin>/<version>/`,
so the harness root's basename is a version string. Installing it for the first
time on 2026-09-20 surfaced two defects that no amount of manifest validation
would have:

- Every gate message named the version as if it were a directory — *"write a
  checkpoint in `0.4.0/sessions/`"*. `hdir_name()` now returns the plugin's name
  when it detects a plugin install.
- Writable state (`sessions/`, the audit log, `memory/`) resolved **inside the
  version directory**, which the next version replaces. The audit log is the
  store a settled claim cites and the input to per-skill contribution, which
  needs `n ≥ 100` trials — resetting it on every update means it can never reach
  its own bar. `state_root()` now places it at
  `<config>/harness-state/<marketplace>/<plugin>/`, beside `plugins` rather than
  under it (a directory named `cache` is one somebody eventually clears).
  `HARNESS_STATE_DIR` overrides; a clone is unchanged.

Verified by bumping 0.4.2 → 0.4.3 with a record written by 0.4.2 and confirming
it was still there afterwards.

## Consistency between the two paths

Both paths install the same six hooks on the same six events. If they drift, a
plugin-installed harness and a bridge-installed one stop being the same harness
while both look healthy. `tests/test_plugin_manifest.py` pins the event set and
the `PostToolUse` matcher (which must include `Skill`, or the library report
loses its input).
