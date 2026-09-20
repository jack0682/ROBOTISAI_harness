---
description: Adopt the harness for the surrounding workspace — clean source leftovers, install the bridge, create the project overlay, absorb the workspace context, validate.
argument-hint: [project-name]
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

Initialize the harness for the **workspace this repo sits in**. Topology: Claude
runs inside this harness repo; the materials to analyze and work on live in the
parent workspace (`../` from the root `CLAUDE.md`, unless configured otherwise
in `claude-harness/harness.config.yaml` `bridge.workspace_relative`). The
harness repo itself is never the analysis target.

This is execution, not analysis — follow
`claude-harness/kernel/execution_protocol.md` and finish the whole sequence.
Project name: $ARGUMENTS (default: the **workspace** directory name, lowercased,
as a kebab/snake slug — not this harness repo's name).

1. **Detect state.** If a project other than `_project_template` is already
   registered in `claude-harness/registry/projects.yaml`, switch to refresh
   mode: re-run the bridge, re-validate, reconcile the project's recorded
   workspace state with reality, report — skip steps 2 and 4.
2. **Clean adoption leftovers** (each is destructive — confirm with the user
   first, and look before deleting): this repo's `.git/` if the user wants it
   detached, `.omc/` and `claude-harness/.omc/`, and `claude-harness/sessions/`
   logs that came from the source harness repo (keep `_session_template.md`,
   `README.md`).
3. **Install the bridge:** `python3 claude-harness/scripts/install_bridge.py`
   → regenerates the root `CLAUDE.md` (including the workspace topology
   section) and `.claude/`.
4. **Create the project overlay:**
   `python3 claude-harness/scripts/new_project.py <name>`.
5. **Absorb the workspace.** Inspect the workspace (`../`) — its README,
   manifests, build/test/lint config, data, directory layout, existing agent
   instructions — and fill `claude-harness/projects/<name>/`: `PROJECT.md`
   (one-liner, status, goal, workspace path), `context.md` (stack, layout,
   current state, key resource paths *relative to the workspace*),
   `constraints.md` (gates, technical/environment limits, MCP/external tools,
   never-break), `glossary.md` (domain terms). Record the workspace root and
   key paths in `project.config.yaml` `workspace:`. Only record what you
   verified by reading — no guessed commands or paths.
6. **Guard the kernel.** Add the project's domain terms to
   `claude-harness/harness.config.yaml` `kernel_leakage_blocklist`.
7. **Validate:** `python3 claude-harness/scripts/validate_harness.py` must
   pass; preview the load order with
   `python3 claude-harness/scripts/collect_context.py <name> <task>`.
8. **Start the worklog.** Create the first session file
   (`claude-harness/sessions/<date>_init_<name>.md`) recording what was
   created/filled, then report — including what still needs a human answer
   (unknown constraints, missing MCP servers, unconfirmed commands).
9. **Clear the first-run notice.** Delete `claude-harness/.bootstrap-pending`
   if it exists. That file is what makes every session open by announcing the
   workspace has not been read; leaving it in place after the analysis is done
   turns a real warning into noise that gets ignored.
