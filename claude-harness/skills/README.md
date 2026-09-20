# skills/ — Layer 3 (capability modules)

A **skill** is an optional, pluggable capability module for a specific domain or
recurring kind of work (e.g. a framework, a writing format, a control discipline).

> The point of this layer is the **slot**, not the content. Skills plug in per need
> and are loaded only when relevant — they never sit in the kernel.

## Contract
- One directory per skill: `skills/<skill-name>/`.
- **Required:** `SKILL.md` — what the skill is, when to use it, how to apply it.
  Frontmatter `name` + `description` (the `description` drives auto-activation).
  A skill may carry whatever payload it needs in its own directory (`scripts/`,
  `references/`, `templates/`, assets, lock files, …); it ships verbatim and is
  served as-is.
- **Recommended** (the `_skill_template/` layout, for skills authored in-harness):
  `checklist.md` (do-this-every-time steps), `examples.md` (worked examples),
  `failure_modes.md` (known traps). Optional — imported third-party skills
  commonly have only `SKILL.md` plus their own payload, and that is valid.
- Register every skill in `registry/skills.yaml`. Support payloads that are not
  skills (no `SKILL.md`, referenced by skills — e.g. `shared-references/`) are
  registered with `status: support`; frontmatter `name` must equal the
  directory name, and `name` must be unique across all active skills.
- `_skill_template/` keeps its skill file as `SKILL.md.template` so the live
  symlink never serves the template as an activatable skill; `new_skill.py`
  materializes it as `SKILL.md` when scaffolding.

## How skills become active
The harness skills/ layer is served directly to Claude Code: the bridge makes
`<root>/.claude/skills` a **relative symlink to this directory**
(`../<harness>/skills`), created by `_link_skills` in
`scripts/install_bridge.py`. There is **no copy and no mirror** — the single
committed copy under `skills/` *is* what activates. Adding a skill here (and
registering it) makes it live on the next session; nothing to re-sync.

## Creating a skill
```bash
python3 scripts/new_skill.py my-skill        # scaffold from _skill_template/
```

## Importing existing skills
```bash
python3 scripts/import_skills.py --from /path/to/skills   # copy verbatim + register
```
Copies every skill directory in verbatim (payload included) and registers each
one carrying a top-level `SKILL.md` as `active`. Idempotent.

## Rules
- A skill **adds** capability; it must not weaken a kernel rule. Domain-specific
  deviations from a universal style/protocol belong here or in a project override,
  never in `kernel/`, `protocols/`, or `styles/`.
- Keep skills self-contained: a skill should make sense loaded on its own.

## Growth governance — the action ladder (prevents sprawl)
Skills rot when every session spawns a new narrow one. When the distillation
review (`modes/memory.md`) decides something about *how to work* is worth keeping,
climb the ladder and stop at the first rung that fits:

1. **Patch the already-loaded skill** — the one in play this session.
2. **Patch the umbrella skill** that owns this area (prefer one rich skill over
   many thin ones).
3. **Add a support file** to an existing skill (`examples.md`, `failure_modes.md`).
4. **Create a new skill** — only when no existing skill or umbrella covers it.

Anti-patterns when distilling into skills (from a self-improving-agent reference):
- ❌ Capturing an environment-specific or transient failure as a durable how-to.
- ❌ Hardening a one-off workaround or a single narrow incident into a rule.
- ❌ Writing a **negative self-capability claim** ("tool X can't do Y") into a
  skill — it forecloses the option in every future session. Record the specific
  error and condition instead.
- ❌ A new skill that duplicates an umbrella skill's territory.

**Lifecycle:** prefer **archive over delete**. A stale or superseded skill is
moved aside (and marked in `registry/skills.yaml`), not removed — history is
cheap and a deletion is hard to reverse (`kernel/operating_principles.md` §5).
memory vs skill split: see `memory/README.md` and `modes/memory.md`.

## Relationship to the kernel — defer, don't restate
The kernel (`kernel/`) owns the **universal** disciplines and is always active
under the harness. A skill (and the `shared-references/` layer) must **defer to**
them, not re-state them: carry only the domain-specific *target* of a rule (e.g.
"the BibTeX you emit", "the result file you cite"), never a fresh copy of the
universal rule itself. The kernel homes are:

- never invent / report faithfully / guard irreversible & outward actions, incl.
  automated rewriting of human-authored files → `kernel/operating_principles.md`
- verified vs. inferred vs. guessed; durable-memory write guard →
  `kernel/uncertainty_protocol.md`
- drive-vs-acquit, independent quality verdicts, claim-ceiling →
  `kernel/verification_authority.md`
- untrusted-content / injection hygiene → `kernel/tooling_protocol.md`
- effort-vs-rigor axes → `kernel/execution_protocol.md`

Several `shared-references/` docs predate the harness and still carry a universal
principle inline; those now open with a pointer to the kernel section that owns
it. New skills reference the kernel, they do not re-inline it.

This harness ships a working skill library (see `registry/skills.yaml`), served
live through the `.claude/skills` symlink. Add more with `new_skill.py` or
`import_skills.py`.

**Curated map:** `skills/INDEX.md` organizes the whole library by scope
(`scopes/<domain>/`), marks orchestrators (▶) and consolidation candidates (⚑),
and is the routing entry point referenced from `ROUTING.md`. Keep it in sync when
adding, archiving, or merging skills.
