<div align="center">

# ROBOTIS AI Harness

**A Claude Code governance layer for the ROBOTIS AI team**

Coding style, commit policy and working method — *enforced*, not suggested.

[![License](https://img.shields.io/badge/License-Apache_2.0-D22128.svg?style=flat-square)](LICENSE)
[![Team](https://img.shields.io/badge/ROBOTIS-AI_Team-0B5FFF.svg?style=flat-square)](https://www.robotis.com)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-D97757.svg?style=flat-square)](https://claude.com/claude-code)
[![Style Guide](https://img.shields.io/badge/style-ROBOTIS_C%2B%2B_%7C_C_%7C_Python_%7C_ROS_%7C_JS-2C8EBB.svg?style=flat-square)](claude-harness/skills/robotis-style/)

[![Skills](https://img.shields.io/badge/skills-72-6E56CF.svg?style=flat-square)](claude-harness/skills/INDEX.md)
[![Hooks](https://img.shields.io/badge/hooks-7_enforcing-1A7F37.svg?style=flat-square)](claude-harness/scripts/hooks/)
[![Tests](https://img.shields.io/badge/tests-156_passing-1A7F37.svg?style=flat-square)](claude-harness/tests/)
[![Commits](https://img.shields.io/badge/commits-GPG_%2B_DCO_required-1A7F37.svg?style=flat-square)](claude-harness/protocols/commit_policy.md)
[![ROS 2](https://img.shields.io/badge/ROS_2-compliant-22314E.svg?style=flat-square)](claude-harness/skills/robotis-style/references/ros.md)

**English** · [한국어](README.ko.md)

[Get started](#2-get-started-in-five-minutes) ·
[Skills](#5-what-skills-are-available) ·
[What is enforced](#6-what-is-enforced) ·
[Troubleshooting](#8-when-you-get-stuck)

</div>

---

Drop it into your working directory once, and the rules apply every time you
open Claude Code there. **There is one command to remember: `/harness`.**

---

## 1. Why — what this changes over plain Claude Code

Claude Code is already good. The problems start when there is **more than one
of you**. Everyone writes different prompts, the style guide has to be pasted
in every session, and a rule you forget is a rule that does not exist.

| | Plain Claude Code | With this harness |
|---|---|---|
| **Style guide** | pasted in each session, or silently ignored | loaded **the moment a source file is opened** |
| **Rule violations** | caught later, at review | **blocked** at write and commit time |
| **"Tests pass"** | can be said without running them | only what was actually run can be claimed |
| **Session ends** | next session starts from scratch | the worklog is picked up automatically |
| **Long work interrupted** | nothing survives | **a session cannot end without a checkpoint** |
| **Commit quality** | varies per person | sign-off + GPG + header + subject, all checked |
| **AI co-author trailers** | tools add them by default | **blocked** — a tool is not an author |
| **Repeated work** | new prompt every time | **72 skills** selected automatically |
| **Team consistency** | everyone does it their own way | one set of rules for everyone |

### Concretely

**① You stop having to remember the style.**
Open `laser_distance_sensor.cpp` and the C++ rules load — 2-space indent,
100 columns, double quotes, brace placement, the trailing underscore on member
variables. Nobody has to ask for it.

**② "Looks right" and "is right" stop being the same thing.**
The harness's first principle is *agreement is not verification*. A test that
was not run cannot be reported as passing, and an unsupported claim is marked
as unsupported.

**③ You cannot skip a rule by accident.**
Seven hooks actually block. Unsigned commits, AI co-authors, missing licence
headers, long work with no checkpoint — all refused, and `--no-verify` is
refused too.

**④ Today's session continues yesterday's.**
Type `/harness` again and it reports where the last session stopped, what is
uncommitted, and what it recorded as the next step.

> Honestly: **this is overkill for a one-off.** If you are writing a throwaway
> script, just use Claude Code. This is for *work that spans sessions* and
> *code that several people touch*.

---

## 2. Get started in five minutes

### Step 1 — Get it

Clone it somewhere temporary, **not** into your working directory. It is an
installer that copies itself into your project, not something you work inside.

```sh
git clone git@github.com:jack0682/ROBOTISAI_harness.git /tmp/harness
```

### Step 2 — Install it into your working directory

Replace `~/my_project` with the directory that holds **your actual work**.

```sh
/tmp/harness/bootstrap.sh ~/my_project --fresh
```

That one line:

- copies the harness layer into your project
- generates `CLAUDE.md` and `.claude/`, which Claude reads automatically
- installs the commit gates
- **removes the template's git remote** — a copy can never push upstream, so
  leaving it only invites an attempt that wastes time and fails
- validates the installation and prints the result

> ⚠️ Use `--fresh` **only on a first install.** On an update it resets the work
> history that has accumulated.

### Step 3 — Open Claude and type `/harness`

```sh
cd ~/my_project
claude
```

Then just type:

```
/harness
```

That is it. It takes over from there.

---

## 3. What `/harness` actually does

**It works out the situation itself.** The same command does different things
the first time and the tenth time.

### First time — right after install

**① Signing identity.** First, because without it **commits are blocked
entirely** — and discovering that at the end of a day's work is exactly what
this ordering prevents. It asks for your name, email and GPG key, and walks you
through creating a key if you do not have one.

**② Reads your working directory.** What the project is, which languages, how
it builds and tests, what conventions already exist. It reads the code rather
than asking you.

**③ Asks what you actually want.** Reading code tells you what something *is*,
never what it is *for*. So it asks four questions, and only four:

- **Goal** — what has to be true when this is finished
- **Scope** — what is in this piece of work, and what is explicitly **not**
- **Done** — what you will run or look at to decide it worked
- **Constraints** — hardware you cannot get, a deadline, an interface that must
  not break

The answers go into the project files, and every later session reads them.

### Next day — continuing

**It does not repeat the setup.** Instead it gives you this and gets back to
work:

- where the last session stopped
- uncommitted changes, unpushed commits
- what is ready to work on and what is blocked
- the next step the last session wrote down

### When something feels wrong

```
/harness check
```

Checks whether the installation actually works. **Not "the file exists" but
"does the gate actually block"** — an installation that looks fine and enforces
nothing is the dangerous state.

---

## 4. Two commands to know

| Command | When |
|---|---|
| **`/harness`** | first install · starting a session · something feels wrong (`/harness check`) |
| **`/harness-checkpoint`** | mid-way through long work, so the next session can continue |

The other two (`/harness-init`, `/harness-load`) are what `/harness` calls
internally. You will rarely type them.

Otherwise, **just say what you want in plain language** — Korean or English.
"Find the bug in this function", "refactor this part". The harness routes it to
the right rules and skills.

---

## 5. What skills are available

**72 skills** are installed. You do not call them directly — the right one is
pulled in based on what you ask. But **you can only ask for what you know
exists**, so here they are.

Full list: [`claude-harness/skills/INDEX.md`](claude-harness/skills/INDEX.md)
· ▶ marks an **orchestrator** that chains other skills.

### 🪶 Coding — simplicity

Vendored from [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)
(MIT). What was taken and what was deliberately left behind:
[`skills/ponytail/UPSTREAM.md`](claude-harness/skills/ponytail/UPSTREAM.md).

| Skill | What it does |
|---|---|
| `ponytail` | The laziest solution that actually works — YAGNI → reuse → stdlib → native → one line → minimum. Levels `lite` / `full` / `ultra` |
| `ponytail-review` | Reviews a **diff** for over-engineering: what to delete |
| `ponytail-audit` | The same over the **whole repo**, ranked |
| `ponytail-debt` | Harvests the `ponytail:` shortcut comments into a debt ledger |

> It complements the harness rather than repeating it: **the harness decides
> whether a claim is earned, ponytail decides whether the code should exist.**

### 🔧 Coding — mandatory

| Skill | What it does |
|---|---|
| **`robotis-style`** | **The ROBOTIS Programming Style Guide.** C++ (Rev 35) · C (Rev 18) · Python (Rev 18) · ROS (Rev 10) · JavaScript (Rev 9), plus the Apache licence header. **Loads automatically when a source file is opened.** |

> This one is not optional. Everything below is pulled in only when needed.

### 🤖 Agents and tooling

| Skill | What it does |
|---|---|
| `mcp-builder` | Build MCP servers (Python FastMCP / Node TypeScript) — expose an external API as LLM tools |
| `agent-browser` | Browser automation — navigate, fill forms, screenshot, scrape, test web apps |
| `skill-creator` | Create, improve and benchmark skills |
| `meta-optimize` ▶ / `meta-apply` | Analyse usage logs to improve the skills themselves (cross-model jury + human approval before anything lands) |
| `file-organizer` | File organisation |

### 🧪 Experiments — from plan to claim

| Skill | What it does |
|---|---|
| `experiment-plan` | Proposal → claim-driven roadmap (ablation matrix, evaluation protocol, compute budget) |
| `experiment-bridge` ▶ | Turn the plan into running code — implement, deploy to GPU, collect first results |
| `experiment-queue` | SSH job queue for multi-seed / multi-config runs, with OOM-aware retry |
| `run-experiment` ▶ | Front door — picks the target and hands off to the provider skill |
| `monitor-experiment` | Check progress, collect results |
| `training-check` | Watch WandB metrics for NaN, loss divergence, idle GPUs — **before a broken run burns GPU hours** |
| `analyze-results` | Statistics, comparison tables, interpretation |
| `csv-data-summarizer` | CSV summary stats and quick plots |
| `system-profile` | Profile a script, process, GPU, memory or interconnect; report bottlenecks |
| `experiment-audit` | **Integrity audit** — fake ground truth, score normalisation, phantom results, insufficient scope |
| `ablation-planner` | Design ablations from a reviewer's perspective |
| `result-to-claim` | Judge what a result **actually supports** and what it does not |

**Compute back-ends:** `vast-gpu` (rent GPUs) · `serverless-modal` (Modal) ·
`qzcli` (启智) · `hugging-face-cli` · `hugging-face-datasets`

### 📐 Theory and mathematics

| Skill | What it does |
|---|---|
| `proof-writer` | Write rigorous ML/AI proofs — theorems, lemmas, missing steps |
| `proof-checker` | Verify a proof, find its gaps via cross-model review, fix and re-review |
| `formula-derivation` | Turn scattered equations into a paper-ready derivation |
| `kill-argument` | **Adversarial review** — write the strongest rejection, then defend it, then surface what is still unresolved |
| `relentless-theory-loop` ▶ | Sustained theory-building across sessions (objections, rival hypotheses, append-only notes) |

### 📚 Research and literature

| Skill | What it does |
|---|---|
| `research-lit` | Search and analyse papers, map related work |
| `novelty-check` | Verify an idea's novelty against recent literature |
| `idea-creator` / `idea-discovery` ▶ | Generate and rank ideas / the full discovery pipeline |
| `idea-discovery-robot` ▶ | Robotics and embodied AI — benchmark-grounded, simulation-first |
| `research-refine` | Vague direction → problem-anchored, implementable plan |
| `research-review` | Critical review from an external reviewer back-end |
| `research-wiki` / `wiki-enrich` | Knowledge base accumulating papers, ideas, experiments, claims |
| `find-skills` | "Is there a skill that does X?" |

**Retrieval back-ends:** `arxiv` (preprints) · `semantic-scholar`
(published / citations) · `exa-search` (general web) · `notebooklm` /
`notebooklm-browser`

### ✍️ Papers and documents

| Skill | What it does |
|---|---|
| `paper-writing` ▶ | **Full pipeline** — report → outline → figures → LaTeX → PDF |
| `paper-plan` / `paper-write` / `paper-compile` | Outline / LaTeX draft / compile and fix errors |
| `paper-figure` / `paper-illustration` ▶ | Result figures and tables / AI illustrations and architecture diagrams |
| `figure-spec` | **Deterministic** SVG architecture diagrams (JSON spec → editable vector) |
| `mermaid-diagram` | Flowcharts, sequence, ER, Gantt |
| `citation-audit` | Whether every citation is real, correctly attributed, and **actually supports the claim** |
| `paper-claim-audit` | Check every number and comparison **against the raw result files** |
| `auto-review-loop` ▶ | Multi-round automated review (selectable `REVIEWER_BACKEND`) |
| `rebuttal` ▶ / `resubmit-pipeline` ▶ | Reviewer responses / porting a paper to another venue |
| `writing-systems-papers` | Structural blueprint for systems papers (OSDI/SOSP style) |
| `overleaf-sync` | Two-way sync with Overleaf via its Git bridge |
| `doc-coauthoring` | Co-author specs, proposals, decision documents |
| `grant-proposal` | Grant proposals (KAKENHI / NSF / NSFC / ERC and others) |
| `pdf` | Anything PDF — read, extract tables, merge, split, fill forms, OCR |
| `render-html` | Markdown/JSON → a readable single-file HTML view |

### 🔗 Pipelines (chaining several skills)

`research-pipeline` ▶ (idea discovery → experiments → review → paper) ·
`research-refine-pipeline` ▶ · `auto-paper-improvement-loop` ▶

### 📣 Other

`feishu-notify` — the notification side-channel other skills use to report status

---

## 6. What is enforced

### Coding style — the ROBOTIS Programming Style Guide

Applies to C, C++, Python, JavaScript/TypeScript, HTML/CSS and ROS 2 package
files. **It loads the moment a source file is opened**, so nobody has to
remember to ask for it.

The four that are wrong most often:

| | C / C++ | Python | JS / TS |
|---|---:|---:|---|
| Indent | **2 spaces** | **4 spaces** | **2 spaces** |
| Line limit | **100** | **99** | **100** |
| Quotes | `"` double | `'` single | `'` single |

Plus: **never a tab**, comments in English, no Korean in source, every file
ends with a blank line, and an Apache 2.0 header at the top of every source
file.

Per language:
[`claude-harness/skills/robotis-style/references/`](claude-harness/skills/robotis-style/references/)

> **When modifying third-party open source, follow that project's style.** Do
> not impose ours on it.

### Licence header

All code here is **Apache License 2.0**. Every new source file starts like
this:

```python
# Copyright 2026 ROBOTIS AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# ... (elided)
# limitations under the License.
#
# Author: Your Name <you@example.com>
```

`Author:` is filled from your git config. Leaving it out blocks the commit.

```sh
python3 claude-harness/scripts/check_license_header.py        # check
python3 claude-harness/scripts/check_license_header.py --fix  # insert
```

> ROS interface files (`.msg`, `.srv`, `.action`) and `.launch.py` carry no
> header.

### Commit policy

Every commit needs a **DCO sign-off (`Signed-off-by:`)** and a **GPG
signature**.

```sh
git commit -s -m "Added zero-copy path to the diff-drive controller"
```

- `-s` adds the sign-off. The GPG signature is automatic.
- Subjects are **capitalised imperative verbs** — `CHANGELOG.rst` is generated
  from commit subjects at release time (`Added ...`, `Fixed ...`,
  `Removed ...`).

**Crediting an AI as a co-author is forbidden.** No `Co-authored-by:` naming
Claude, Copilot, ChatGPT or similar, and no `Generated with ...` footer. A tool
is not an author; copyright and the DCO attestation belong to the person who
signed off. **This rule outranks the harness and any assistant's own
attribution default.** Human co-authors are of course fine.

Bypassing with `--no-verify` is a policy violation. If a gate is wrong, fix the
gate.

#### Three independent layers

| Gate | Catches |
|---|---|
| `.githooks/pre-commit` | identity unset, no GPG key, missing licence header |
| `.githooks/commit-msg` | no sign-off, mismatched sign-off, AI co-author, empty subject |
| `commit_guard.py` | an agent committing without identity, `--no-verify`, AI co-author |

Bypass one and the others still hold.

### Working method

`KERNEL.md` and `ROUTING.md` load every session. They route each request to the
right **scope** (7 domain rule sets) and **mode** (13 cognitive operations);
everything deeper loads on demand.

Seven hooks make that enforced rather than advisory:

| Hook | What it does |
|---|---|
| `session_start` | injects the last worklog, checkpoint and unsettled claims |
| `route_hint` | surfaces the scope/mode a request calls for |
| `kernel_guard` | requires confirmation to edit the kernel |
| `commit_guard` | blocks unsigned commits, AI co-authors, `--no-verify` |
| `post_edit` | records edits, restates the verification owed |
| `pre_compact` | preserves state before context compaction |
| `stop_gate` | **will not let long work end without a checkpoint** |

---

## 7. Updates do not arrive by themselves

This repository is the **single upstream**, and it changes only when its author
changes it.

A workspace copy is **detached on purpose**. `bootstrap.sh` copies the harness
in rather than leaving a clone that tracks this origin, so your project's git is
entirely your own and a `git pull` will never drop harness changes on top of
your work. The trade is that upstream improvements do **not** reach you
automatically.

To update, re-clone and re-run:

```sh
rm -rf /tmp/harness
git clone git@github.com:jack0682/ROBOTISAI_harness.git /tmp/harness
/tmp/harness/bootstrap.sh ~/my_project      # no --fresh!
```

Without `--fresh`, `projects/`, `sessions/`, `memory/` and `registry/` — **your
accumulated work history** — are left untouched.

> Fixed something in the harness, or found an improvement? **Send it upstream.**
> Kept in one workspace, it disappears at the next update.

---

## 8. When you get stuck

<details>
<summary><b>"My commits are blocked"</b></summary>

Because there is no signing identity. That is intended. `/harness` will set it
up. Manually:

```sh
git config --local user.name       "Your Name"
git config --local user.email      "you@example.com"
git config --local user.signingkey <GPG_KEY_ID>
```

**`--local`**, not `--global`. A global identity gets stamped onto team commits
without telling you.
</details>

<details>
<summary><b>"GitHub does not show Verified"</b></summary>

The public key has to be on your account:

```sh
gpg --armor --export <GPG_KEY_ID>
```

→ GitHub Settings → SSH and GPG keys → New GPG key.
</details>

<details>
<summary><b>"I do not have a GPG key"</b></summary>

`/harness` will walk you through creating one. Manually:

```sh
gpg --full-generate-key     # RSA 4096, your work email
```
</details>

<details>
<summary><b>"The harness does not seem to be working"</b></summary>

`/harness check` runs every check and repairs what is safely repairable. It
verifies that gates **actually block**, not merely that files exist.
</details>

<details>
<summary><b>"I opened Claude inside the cloned folder"</b></summary>

That is not where it is used. Type `/harness` — it will explain and, once you
give it your project path, install it there.
</details>

<details>
<summary><b>"The style rules are not firing"</b></summary>

Path-scoped rules fire on the **`Read`/`Edit` tools, not on `cat` in a shell.**
Reading a file through the shell silently costs you the rule. This is
documented behaviour; `/harness check` verifies the rule files are present.
</details>

---

## 9. Layout

```
your-project/
├── CLAUDE.md          ← generated. Claude reads this every session
├── .claude/           ← generated. Hooks, skills symlink, path-scoped rules
├── .githooks/         ← the commit gates
├── CONTRIBUTING.md    ← the rules, in detail, for humans
├── LICENSE            ← Apache 2.0
├── claude-harness/    ← the harness itself
└── ...your actual work
```

Worth knowing inside `claude-harness/`:

| Path | What |
|---|---|
| `KERNEL.md`, `ROUTING.md` | the always-on spine |
| `skills/INDEX.md` | **all 72 skills** |
| `skills/robotis-style/` | the ROBOTIS style guide, per language |
| `protocols/commit_policy.md` | the commit policy in full |
| `scopes/` | 7 domain rule sets |
| `modes/` | 13 cognitive operations |
| `projects/` | your project — goal, constraints, glossary |
| `sessions/` | work history. The next session resumes from here |
| `scripts/hooks/` | the 7 enforcing hooks |
| `tests/` | 156 tests |

---

## 10. Checking an installation yourself

```sh
python3 claude-harness/scripts/validate_harness.py               # structure
python3 claude-harness/scripts/check_license_header.py           # licence headers
cd claude-harness && python3 -m unittest discover -s tests -q    # its own tests
```

`/harness check` runs all of these and interprets the output, which is usually
easier.

---

## Contributing

Fixed something in the harness, or found an improvement? Send it upstream. The
rules are in [`CONTRIBUTING.md`](CONTRIBUTING.md) — signing setup, commit
policy, and where the style guide applies.

## Licence

[Apache License 2.0](LICENSE) — Copyright 2026 ROBOTIS AI
