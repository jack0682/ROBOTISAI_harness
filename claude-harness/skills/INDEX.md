# skills/ — curated index (by scope)

> The active skill library (72 skills) organized under the harness's scopes
> (`scopes/<domain>/AGENTS.md`) so routing actually reaches the right skill, and
> flags consolidation candidates per the action ladder (`skills/README.md`).
> `registry/skills.yaml` is the machine index; this is the human/routing map.
> Prefer an existing skill over a new one; prefer patching an umbrella over
> adding a sibling.

Legend: **▶ orchestrator** (chains other skills) · ⚑ consolidation candidate.

## coding — house standards  → `scopes/coding/`  **(MANDATORY)**
- `robotis-style` — **the ROBOTIS Programming Style Guide.** Not optional and
  not a lookup of last resort: load it *before* writing or reviewing any
  `.c/.h/.cpp/.hpp/.py/.js/.ts/.css/.html` file or ROS 2 package file. Also
  fires on the file via `.claude/rules/robotis-style.md`. References cover C++
  (Rev 35), C (Rev 18), Python (Rev 18), ROS (Rev 10), JavaScript (Rev 9).

## coding — simplicity  → `scopes/coding/`
Vendored from [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)
(MIT), unmodified. Provenance and what was deliberately left behind:
`skills/ponytail/UPSTREAM.md`.
- `ponytail` — the laziest solution that actually works: YAGNI → reuse → stdlib
  → native → one line → minimum. Levels `lite` / `full` / `ultra`.
- `ponytail-review` — over-engineering review of a **diff**: what to delete.
- `ponytail-audit` — the same over the **whole repo**, ranked.
- `ponytail-debt` — harvests the `ponytail:` shortcut comments the core skill
  leaves behind into a debt ledger.

> Complements rather than duplicates the harness: the harness decides whether a
> claim is **earned**, ponytail decides whether the code should **exist**.

## math — theory, proof, formalization  → `scopes/math/`
- `proof-checker` — verify/fix a LaTeX proof, find gaps.
- `proof-writer` — write rigorous ML/AI proofs.
- `formula-derivation` — derive/structure a theory line, build a formula.
- `kill-argument` — adversarial: construct the strongest rejection of a claim.
- `relentless-theory-loop` ▶ — foundational theory-building loop.

## research — literature, novelty, ideas  → `scopes/research/`
**Discovery & novelty:** `idea-creator`, `idea-discovery` ▶, `idea-discovery-robot` ▶,
`research-refine`, `research-refine-pipeline` ▶, `research-pipeline` ▶, `novelty-check`,
`research-lit`, `research-review`, `research-wiki`, `wiki-enrich`, `find-skills`.
**Retrieval back-ends** (pick by source): `arxiv` (preprints), `semantic-scholar`
(published/citations), `exa-search` (general web), `notebooklm`, `notebooklm-browser`.

## writing — papers, documents, critique  → `scopes/writing/`
**Paper authoring (the `paper-*` umbrella family):** `paper-plan`, `paper-write`,
`paper-writing` ▶, `paper-figure`, `paper-compile`, `paper-illustration` ▶ (umbrella —
`IMAGE_BACKEND`: gemini / codex-image2; the former `-image2` skill merged in and
archived), `figure-spec`, `mermaid-diagram`, `overleaf-sync`, `writing-systems-papers`,
`render-html`.
**Claim/citation audit:** `citation-audit`, `paper-claim-audit`.
**Review & resubmit loops:** `auto-review-loop` ▶ (umbrella — selectable
`REVIEWER_BACKEND`: codex / manual / llm / minimax; the former `-llm` and
`-minimax` variants are merged into it),
`auto-paper-improvement-loop` ▶, `rebuttal` ▶, `resubmit-pipeline` ▶.
**Docs:** `pdf`, `doc-coauthoring`, `grant-proposal`.

## experiments — design, runs, data → claims  → `scopes/experiments/`
**Plan → run → audit → claim:** `experiment-plan`, `experiment-bridge` ▶,
`experiment-queue`, `experiment-audit`, `ablation-planner`, `result-to-claim`,
`analyze-results`, `run-experiment`, `monitor-experiment`, `training-check`,
`system-profile`, `csv-data-summarizer`.
**Compute back-ends:** `vast-gpu`, `serverless-modal`, `qzcli`, `hugging-face-cli`,
`hugging-face-datasets`.

## prompts / agent-tooling / harness  → `scopes/prompts/`, `scopes/coding/`
`mcp-builder`, `agent-browser`, `skill-creator`, `meta-optimize` ▶, `meta-apply`,
`harness-activate`, `file-organizer`.

## utility (no scope)
`feishu-notify` — notification side-channel used by other skills (platform: Feishu/Lark).

---

## Adding a skill

Prefer an existing skill over a new one; prefer patching an umbrella over
adding a sibling (`skills/README.md`). The ▶ orchestrators are umbrellas —
new work extends them.

Every description is injected into **every** session, so a new skill costs
context on every run whether or not it fires. `tests/test_context_budget.py`
holds the ceiling and `evaluation/skill_triggers.py` sets the per-skill
description budget from its trigger count. Run both before adding one.
