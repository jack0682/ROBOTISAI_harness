# skills/ — curated index (by scope)

> The active skill library (68 skills) organized under the harness's scopes
> (`scopes/<domain>/AGENTS.md`) so routing actually reaches the right skill, and
> flags consolidation candidates per the action ladder (`skills/README.md`).
> `registry/skills.yaml` is the machine index; this is the human/routing map.
> Prefer an existing skill over a new one; prefer patching an umbrella over
> adding a sibling. Retired skills live in `_archive/skills/` (out of force).

Legend: **▶ orchestrator** (chains other skills) · ⚑ consolidation candidate.

## coding — house standards  → `scopes/coding/`  **(MANDATORY)**
- `robotis-style` — **the ROBOTIS Programming Style Guide.** Not optional and
  not a lookup of last resort: load it *before* writing or reviewing any
  `.c/.h/.cpp/.hpp/.py/.js/.ts/.css/.html` file or ROS 2 package file. Also
  fires on the file via `.claude/rules/robotis-style.md`. References cover C++
  (Rev 35), C (Rev 18), Python (Rev 18), ROS (Rev 10), JavaScript (Rev 9).

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
`-minimax` skills are merged into it and archived to `_archive/skills/`),
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

## Archived families (2026-07-11 — moved to `_archive/skills/`, out of injection)
Retired to shrink the per-session skill list to what this team's work actually uses
(theory/robotics/research/experiments/writing). Reversible: move a dir back under
`skills/` and set its registry entry to `active`.

- **Patent pipeline (10):** `patent-pipeline` ▶ + `invention-structuring`,
  `claims-drafting`, `embodiment-description`, `figure-description`,
  `specification-writing`, `jurisdiction-format`, `patent-novelty-check`,
  `prior-art-search`, `patent-review`. *(out of scope: no patent work.)*
- **Art/design/office (11):** `algorithmic-art`, `brand-guidelines`, `canvas-design`,
  `pixel-art`, `frontend-design`, `web-artifacts-builder`, `theme-factory`,
  `slack-gif-creator`, `docx`, `pptx`, `xlsx`.
- **Talk/poster/slides (4):** `paper-talk` ▶, `paper-slides`, `slides-polish`,
  `paper-poster`.
- **Retrieval duplicates (5):** `alphaxiv`, `deepxiv`, `openalex`, `gemini-search`,
  `comm-lit-review` (kept front-line: `arxiv`, `semantic-scholar`, `exa-search`).
- **Foreign/misc (7):** `interview-cheatsheet`, `dse-loop` ▶, `ralph`, `prd`,
  `internal-comms`, `agents-sdk`, `webapp-testing`.

Also archived: the orphaned `codex-skills/` mirror tree (Codex/Gemini CLI skill
packs, not wired into the CC bridge) → `_archive/codex-skills/`.

## Consolidation candidates (action ladder)
1. ✅ **DONE (2026-06-11)** — `auto-review-loop` × {base, -llm, -minimax} merged into
   the `auto-review-loop` umbrella via a `REVIEWER_BACKEND` switch; the two variants
   archived (`superseded_by: auto-review-loop`).
2. ✅ **DONE (2026-06-11)** — `paper-illustration` + `paper-illustration-image2`
   merged into the `paper-illustration` umbrella via an `IMAGE_BACKEND` switch.
3. ✅ **DONE (2026-07-11)** — retrieval family consolidated to `arxiv` /
   `semantic-scholar` / `exa-search`; `alphaxiv`/`deepxiv`/`openalex`/`gemini-search`/
   `comm-lit-review` archived. `research-lit` remains the front-door.
4. ✅ **DONE (2026-07-11)** — patent-specific docs (`patent-format-*`,
   `patent-writing-principles`, `prior-art-databases`) archived to
   `_archive/skills/shared-references-patent/`. *Still P2-pending:* clean stale
   skill mentions (archived retrieval / `dse-loop` / `codex-skills`) in
   `external-cadence.md` / `wiki-helper-resolution.md` / `integration-contract.md`.
5. The remaining **▶ orchestrators** (`research-pipeline`, `paper-writing`, …) are
   umbrellas — new work extends them, not adds siblings.
