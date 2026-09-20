# projects/ — Layer 4 (project harnesses)

A **project harness** layers project-local context, constraints, and rules on top
of the universal harness. This is the part that **changes** per project; the kernel
is the part that **doesn't**.

> Kernel = what does not change. Project = what changes. Session = what's happening
> right now.

## Contract
- One directory per project: `projects/<project-name>/`, structured like
  `_project_template/`.
- A project may **add** context/constraints and **override** universal rules — but
  overrides must be explicit, living in `overrides/`. A project never silently
  weakens a kernel rule.
- Register every project in `registry/projects.yaml`.

## Template contents
| File | Purpose |
|------|---------|
| `PROJECT.md` | Entry point — read first when working this project. |
| `project.config.yaml` | Metadata: required skills, default protocols/styles, gates. |
| `context.md` | Background, current state, goals. |
| `constraints.md` | Technical/environment limits and never-break conditions. |
| `glossary.md` | Project-specific terms. |
| `workflows.md` | Recurring project procedures. |
| `local_rules.md` | Project-only rules. |
| `memory/` | decisions, open_questions, known_issues, checkpoints. |
| `overrides/` | explicit adjustments to protocols/styles/commands. |

## Creating a project
```bash
python3 scripts/new_project.py my-project
```

No concrete projects ship yet — only the template.
