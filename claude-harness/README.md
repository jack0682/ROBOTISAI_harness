# claude-harness — the ROBOTIS AI team's research operating system

Not a tool for producing ideas fast. A harness that **tests whether a thought
survives** theory, math, counterexample, experiment, code, and data — and fixes
what survives into an artifact. It defaults to **verification over agreement**:
no definition is told it has none, a decorative equation is told it is decorative,
an unvalidated claim is told it is unvalidated.

> The job is not to think for the user. It is to test whether the thought holds.

## The central loop

```
Thought → Claim → Definition → Mathematical Formulation → Consistency Check
   → Counterexample → Execution / Experiment / Implementation → Data / Result
   → Revision → Artifact → Memory / Skill Distillation
```

Full statement: `KERNEL.md`. Dispatch: `ROUTING.md`.

## Architecture (two axes)

The harness's own always-on surface is small — the **spine** (`KERNEL.md` +
`ROUTING.md`, 20 KB). What the model actually sees every session is larger:
~45 KB (~11k tokens) once the bridge, the autonomy-mandate injection and 67
skill frontmatters are counted. The skill frontmatters are 54% of it and are
pushed in by the `.claude/skills` symlink, not pulled on demand — which is why
their size is capped and checked (`evaluation/skill_triggers.py`).
`ROUTING.md` dispatches each request on two axes, loading depth on demand:

- **modes** (`modes/`) — *cognitive operations*, domain-independent: `think`,
  `define`, `math_lock`, `verify`, `counter`, `execute`, `research`, `paper`,
  `prompt`, `memory`, `audit`, `layer`. Each is input → operation → fixed output.
- **scopes** (`scopes/`) — *domain governance* (math, research, writing, coding,
  experiments, prompts): local invariants, guardrails, and the verification each
  domain owes. One `AGENTS.md` per scope.

`math_lock` is the centerpiece: a formalization either carries its claim under
stated conditions, or it is cut.

## Quick start

```bash
# Validate harness structure (primary health check)
python3 scripts/validate_harness.py

# (Re)generate the native Claude Code bridge (root CLAUDE.md + .claude/)
python3 scripts/install_bridge.py

# Start a session worklog (lands in sessions/active/)
python3 scripts/new_session.py --task "derive identifiability bound" --date 2026-06-11

# End-of-session distillation review (what becomes memory/skill?)
python3 scripts/distill_session.py

# Create a project overlay / skill slot
python3 scripts/new_project.py my_project
python3 scripts/new_skill.py my_skill
```

## Layout

| Path | What lives here |
|------|-----------------|
| `KERNEL.md`   | the always-on constitution: identity, central loop, 6 non-negotiable principles |
| `ROUTING.md`  | request → scope × mode × skill dispatcher |
| `modes/`      | cognitive operations (think … math_lock … audit) |
| `scopes/`     | domain governance (`<domain>/AGENTS.md`) |
| `kernel/`     | full principle texts, loaded for depth |
| `protocols/`  | per-task procedure (planning, coding, validation, …) |
| `styles/`     | output/presentation conventions |
| `skills/`     | capability modules (metadata-first, on demand) |
| `memory/`     | durable, reusable knowledge (`MEMORY.md` index + items) |
| `sessions/`   | working memory: `active/`, `archived/`, `distilled/` |
| `evaluation/` | quality rubrics + trigger / near-miss routing tests |
| `templates/`  | fill-in artifact skeletons |
| `commands/`   | canonical command defs (native Claude Code format) |
| `projects/`   | project-local overlays (slots) |
| `registry/`   | machine-readable index that drives the scripts |
| `scripts/`    | working Python automation + the hook enforcement layer |

The hook layer (`scripts/hooks/`, wired via `.claude/settings.json`) is what turns
the kernel's obligations into runtime-enforced behavior: it injects the latest
worklog at session start, audit-logs edits and commands, and blocks a stop after
unlogged edits until a checkpoint exists. See `HARNESS.md` for the layering
contract, conflict resolution, and load order.

## Adopting in a project

Self-contained by default. To govern an external working tree, run
`/harness-init <project>` (`commands/init.md`): it inspects the workspace, fills
`projects/<name>/`, registers domain terms in `kernel_leakage_blocklist`, and
validates. Project-shaped rules live in `projects/<name>/` (explicit overrides in
`overrides/`); only truly universal lessons are promoted into `kernel/` or a mode.
The kernel's safety, verification, and checkpoint rules are not overridable.

### Cloning as a template into a new workspace

This harness is a **Claude-only template**: clone it into a workspace, sever the
template's git so the clone stops tracking the origin, and use it as that
workspace's convention layer.

```sh
# From the repository root, install into the workspace that holds your work:
./bootstrap.sh ~/my_project --fresh
```

`bootstrap.sh` is the documented path: it copies the harness in, generates the
bridge, wires the commit gates, severs the template remote and validates. See
the root `README.md`.

`scripts/detach_for_workspace.py` remains for the other topology — when the
template was cloned *directly into* the workspace rather than installed from
outside — and severs that clone's `.git` in place. Dry-run is the default.

`detach_for_workspace.py` removes the clone's `.git` (killing the dependency on
the template origin), regenerates the bridge, and validates. Run it **in the
clone, not in the source template.** Dry-run is the default; `--apply` performs the
destructive steps.

### Keeping a deployment current

A deployment drifts as the source improves, and for a long time nothing carried
improvements out to one: `upgrade_harness.py` had no callers, and what it synced
omitted `KERNEL.md`, `ROUTING.md`, `modes/` and `scopes/` — it upgraded a harness
while leaving its constitution stale. Measured against a three-month-old
deployment it moved 17 files where 30 had changed, and deleted a local file
without being asked.

What is synced and what belongs to the deployment is now declared once, in
`harness.config.yaml` under `distribution:`, and read from the **upstream** side —
so a deployment whose config predates a new layer still learns to sync it.

```bash
# from inside the deployment; dry-run is the default and prints every change
python3 claude-harness/scripts/upgrade_harness.py /path/to/upstream/claude-harness
python3 claude-harness/scripts/upgrade_harness.py /path/to/upstream/claude-harness --apply
```

Local files upstream does not ship are reported, never deleted, unless you add
`--prune`. `projects/`, `sessions/`, `memory/`, `registry/` and `_archive/` are
never touched — that is what makes a deployment a deployment. Afterwards run
`scripts/install_bridge.py` and `scripts/validate_harness.py`, or `check.py` at
the repository root, which runs both plus the test suites.

Every session in a workspace where the harness is in force runs under the
**standing autonomy mandate** (`kernel/autonomy_mandate.md`): maximum work depth
and persistence by default, injected mechanically by the `session_start` hook.

## Design lineage

The refactor toward this structure drew, deliberately and selectively, on several
public harnesses — scope-based `AGENTS.md` governance and self-audit discipline,
a self-improving agent's distillation loop and persistence guard, an agent
runtime's skill/memory format, and a meta-factory's evaluation discipline. What
was borrowed and why: `docs/ref_analysis.md`. Architecture and rationale:
`docs/architecture.md`, `docs/design_principles.md`.
