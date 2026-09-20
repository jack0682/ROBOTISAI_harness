# Reference analysis — what was borrowed, and what was not

Seven public "harness" repositories were studied before this refactor. They are
**not** of one kind: the word "harness" spans a governance layer over a coding
agent, an execution runtime, a curated map, and a name collision. What follows is
what each contributed (or didn't) to this harness. Nothing was copied; structure
and discipline were absorbed.

## ref5 · openclaw — **primary governance reference**
A multi-channel assistant whose *own* repo governance is the lesson: a terse root
that **routes** rather than contains, plus scoped `AGENTS.md` files each owning
local invariants and a Verification section; skills as versioned methodology
units; and self-audit discipline (evidence-map before changing, "best fix not
plausible fix", no silent LOC growth, one canonical path, an autoreview closeout).
**Absorbed:** the scope axis (`scopes/<domain>/AGENTS.md` with Read first /
Contract / Local invariants / Guardrails / Verification / Anti-patterns); the
router-style spine (`KERNEL.md` + `ROUTING.md`); the self-audit lens in
`modes/audit.md` and `KERNEL.md` → Self-audit discipline.

## ref6 · hermes-agent — **primary self-improvement reference**
A self-improving agent whose headline is a learning loop: after a session, a
*separate* review decides what to persist, with a **narrow write surface**
(memory + skills only), a **persistence guard** on what must NOT be saved
(transient failures, accidental workarounds, narrow incidents, and especially
negative self-capability claims), an **action ladder** (patch loaded → patch
umbrella → support file → new skill), a memory/skill split, and archive-over-
delete with a curator lifecycle. **Absorbed:** `modes/memory.md`,
`scripts/distill_session.py`, the session template's Distillation review, the
guard and ladder in `KERNEL.md` and `skills/README.md`.

## ref4 · OpenHarness (oh/ohmo) — skill & memory format
A lightweight agent runtime. **Absorbed:** skills as `SKILL.md` + frontmatter,
advertised metadata-first and loaded on demand (already the harness's format —
confirmed and kept); memory as frontmatter-tagged items (`scope / importance /
review_at / supersedes / source / signature`) over a `MEMORY.md` index, with
signature-dedupe and supersede semantics → `memory/README.md`, `memory/MEMORY.md`.

## ref2 · revfactory/harness — lifecycle & evaluation
A "team-architecture factory": one meta-skill that *generates* agent teams from a
sentence. Opposite of a governance constitution, so not adopted structurally.
**Absorbed only:** the Phase-0-audit → Phase-7-evolution lifecycle framing and the
should-trigger / should-NOT-trigger evaluation discipline →
`evaluation/{trigger_tests,near_miss_tests}/`, `modes/audit.md` closeout.

## ref7 · OpenManus — loop skeleton (light)
A classic ReAct execution agent (think → act → observe, stuck detection,
`max_steps`, persona `SYSTEM_PROMPT` + `NEXT_STEP_PROMPT`). Maintenance was
slowing, so dependence was kept light. **Absorbed:** the shape of a mode file
(trigger/input/operation/output, a stance per operation) and the discipline of a
bounded loop with an explicit stuck/altitude check (`modes/layer.md`).

## ref3 · awesome-agent-harness — the map, kept as an index
A curated catalog (288 entries, 9 categories) defining a harness as "the
reliability layer around a model." Not a single implementation to absorb. **Kept
as** a discovery index — its governance, context/state, and reference-harness
categories are where to look for the next idea (e.g. `agent-governance-toolkit`,
`Haft`, `sd0x-dev-flow`).

## ref1 · harness/harness — excluded (name collision)
A Go DevOps platform (Drone CI's successor: code hosting, CI/CD, Gitspaces). No
LLM-agent framework; the only contact is plumbing to *install* Claude Code inside
a cloud dev container. Search noise — not absorbed.

## Net mapping

| Source | Lands in |
|---|---|
| ref5 governance | `ROUTING.md`, `scopes/*/AGENTS.md`, `modes/audit.md`, `KERNEL.md` self-audit |
| ref6 self-improvement | `modes/memory.md`, `scripts/distill_session.py`, session template, `skills/README.md` |
| ref4 skill/memory | `memory/`, `skills/README.md` (confirmed format) |
| ref2 lifecycle/eval | `evaluation/{trigger,near_miss}_tests/` |
| ref7 loop | `modes/*` file shape, `modes/layer.md` |
| ref3 map | this file (discovery index) |
| ref1 | — (excluded) |

## Second-pass absorption (2026-06-12) — mining the catalog's external repos

The first pass took one idea per local ref. A second pass mined ref3's catalog
for *external* repos closest to the "escape-proof, not plausible" thesis, and
re-checked what the local refs still had unabsorbed. Findings, ranked:

**ADOPTED — Haft → claim-expiry clock.** Haft (catalog: Guardrails/Governance)
stores decisions as *falsifiable contracts*: claim + threshold + evidence +
valid-until, and **reopens on decay** when evidence ages or a prediction fails.
This is the harness's own "math is load-bearing or removed", made time-aware.
The harness already had `review_at` / `supersedes` frontmatter but **nothing
enforced them** — a decorative field, exactly the failure mode the harness
exists to catch. Built into `memory/claims/` (`scope: claim`, `status`
open→settled→stale), `scripts/_claims.py` (shared logic), `validate_harness.py`
(settled ⇒ threshold+evidence+dated review_at, else error; stale ⇒ warning),
and `stop_gate.py` (block a session that leaves a claim unearned-settled or
settled-but-stale). `review_at` reused as the expiry clock — no new field. Took
the DecisionRecord + manual reopen; left Haft's `haft run`/WorkCommission
*execution-runtime* half (does not belong in a markdown methodology spine).

**ADOPTED — sd0x-dev-flow → fail-closed hooks + compaction-survival (2026-06-12).**
sd0x's stop-guard treats an unresolved gate as *blocked* ("incomplete gate =
blocked"); the harness fails OPEN. Reconciled the tension: infrastructure
crashes still fail open (a buggy hook must not brick the session), but (1)
`_hooklib.safe()` now logs a `hook_crash` event so a silently-failing gate is
visible in the audit data instead of vanishing; (2) `kernel_guard` is
fail-closed on *ambiguity* — an edit-tool call whose target cannot be resolved
is asked (or, in the distill sandbox, denied) rather than silently allowed; and
(3) `session_start` re-injects the unsettled claims (open / stale) from
memory/claims/, so a fresh or post-compaction context cannot silently treat a
not-yet-earned or expired claim as fact. Took the *fail-closed-on-ambiguity*
and *compaction re-injection* ideas; left sd0x's dual-reviewer dispatch (a
code-review runtime concern, not methodology). All paths tested live.

**ADOPTED — Beads → typed-edge work graph (2026-06-12).** Beads models
long-horizon work as a graph (typed edges, `ready` = zero open blockers,
`supersedes` auto-retire) over a Dolt SQL backend. Flat `open_questions`/
`known_issues` tables hid which open item was *blocked* on another and let
*superseded* items linger. Rebuilt the two project-memory tables with stable
IDs (`Q…`/`I…`) and `blocked_by` / `supersedes` columns; `scripts/work_graph.py`
parses them and computes ready / blocked / superseded-but-open / dangling-edge /
cycle. `validate_harness.py` treats a dangling edge or a blocked_by cycle as an
error and a superseded-but-open item as a warning (the graph may not lie);
`session_start` injects the active project's ready-set so a session opens on a
workable item. Took Beads' data model, **left Dolt** — source of truth stays
markdown tables a human reads (and Beads' own "no MEMORY.md" stance conflicts
with this harness's memory layer anyway).

**ADOPTED — openclaw (2nd-pass) → sharper verify/counter (2026-06-12).** Three
gates added: (1) `modes/verify.md` **primary-source gate** — "no direct check,
no verdict": a verdict on a dependency/source/result requires you read or ran
it; a subagent summary, abstract, or memory note does not satisfy it; (2)
`modes/verify.md` **proof hierarchy** — primary proof (real path reproduced,
actual output observed) vs supplemental (CI/tests/snapshot/lint), which supports
but never substitutes; (3) `modes/counter.md` + scopes **"what does NOT count as
evidence"** false-positive list. The first concrete instance came from the live
ONN testbed: ONN reports CSR = 1.0 ± 0.0, which the paper itself admits is "by
construction" for a constraint-enforcing method — a **circular metric**. That
case is now a named anti-pattern in `scopes/experiments/AGENTS.md`
(construct-independence invariant + circular-metric anti-pattern) and in the
counter-mode false-positive list. (openclaw's evidence-map and best-fix were
already in `KERNEL.md` self-audit — not re-absorbed.)

**REVIEWED, PENDING (recorded so the review is a fixed artifact, not lost):**
- **Acontext → merge-not-append distillation.** On distill, route
  update-existing-skill vs create-new so artifacts don't accrete near-dupes.
- **SkillSpector / Snyk agent-scan → one-time hygiene.** SARIF scan the
  imported skills for trigger-shadowing / tool-poisoning. Tooling, not design.

**REJECTED — Hermes (ref6) 2nd pass.** Compression-locks, WAL/NFS fallback,
read-only multi-profile DB, iteration-budget, jittered backoff, turn-retry
state machine: all solve a *parallel/networked execution-runtime*'s problems.
This harness is a single-user markdown layer + a few scripts; adopting them is
over-engineering for problems it does not have.
