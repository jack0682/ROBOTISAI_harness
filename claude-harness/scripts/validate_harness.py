#!/usr/bin/env python3
# Copyright 2026 ROBOTIS AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Jaehong Oh <jaehongoh1554@gmail.com>

"""Structural lint for the claude-harness.

Checks that every layer's files exist, the registry points at real paths, command
files have valid frontmatter, and no project-specific terms leaked into the
universal layers (kernel/protocols/styles). Exits non-zero on any failure.

Usage:
    python3 scripts/validate_harness.py
"""

from __future__ import annotations

import json
import os
import re
import sys

import _claims
import _common as C
import work_graph

# Files that must exist in each universal layer.
STYLE_FILES = ["code", "naming", "citation"]
TEMPLATE_FILES = [
    "task_brief", "plan", "answer", "implementation_report",
    "research_report", "review_report", "checkpoint", "handoff",
]
EVALUATION_FILES = [
    "answer_quality", "code_quality", "research_quality",
    "hallucination_check", "final_acceptance",
]
TOP_FILES = ["README.md", "HARNESS.md", "harness.config.yaml",
             "KERNEL.md", "ROUTING.md"]
HOOK_SCRIPTS = ["_hooklib.py", "session_start.py", "post_edit.py",
                "stop_gate.py", "kernel_guard.py", "pre_compact.py",
                # route_hint runs on every user prompt and was absent from this
                # list: deleting it left the lint green while settings.json went
                # on invoking a file that was not there.
                "route_hint.py"]
# The hooks settings.json must actually register, and the event each belongs to.
WIRED_HOOKS = {
    "session_start.py": "SessionStart",
    "kernel_guard.py": "PreToolUse",
    "post_edit.py": "PostToolUse",
    "stop_gate.py": "Stop",
    "pre_compact.py": "PreCompact",
    "route_hint.py": "UserPromptSubmit",
}

# Modes (cognitive operations) and scopes (domain governance) — the spine routes
# into these. Each scope owns an AGENTS.md.
MODE_FILES = ["README", "think", "define", "math_lock", "verify", "counter",
              "execute", "research", "paper", "prompt", "memory", "audit", "layer"]
SCOPE_DIRS = ["research", "math", "writing", "coding", "experiments",
              "prompts", "control"]

# Universal layers that must stay project-agnostic.
AGNOSTIC_DIRS = ["kernel", "protocols", "styles", "modes", "scopes"]

# Where backtick `.md` cross-references are checked (sessions/ and projects/
# are excluded: worklogs are historical, templates use placeholders).
MD_REF_DIRS = ["kernel", "protocols", "styles", "templates", "evaluation",
               "commands", "modes"]
MD_REF_TOP = ["README.md", "HARNESS.md", "KERNEL.md", "ROUTING.md"]
_MD_REF_RE = re.compile(r"`([^`\s]+\.md)`")

# Every file in these layers must be referenced (by filename) from somewhere in
# the live harness — an unreferenced file is decoration drifting out of force.
ORPHAN_DIRS = ["templates", "evaluation", "skills/shared-references"]
# `skills` is in the corpus but not in ORPHAN_DIRS: a skill is reached by its
# description, not by being named from another file, so an unreferenced skill is
# not dead. Its *shared references* are the opposite — they exist only to be
# pointed at, and two of them sat at zero referrers because this list excluded
# the one directory that cites them.
ORPHAN_CORPUS_DIRS = ["kernel", "protocols", "styles", "commands",
                      "templates", "evaluation", "skills"]
ORPHAN_CORPUS_TOP = ["README.md", "HARNESS.md"]


def main(argv=None):
    errors = []
    warnings = []
    config = C.load_config()

    # --- top-level files ---
    for f in TOP_FILES:
        if not os.path.isfile(C.rpath(f)):
            errors.append(f"missing top-level file: {f}")

    # --- kernel (deep principles, from config) ---
    for name in config.get("kernel", []):
        if not os.path.isfile(C.rpath("kernel", f"{name}.md")):
            errors.append(f"missing kernel file: kernel/{name}.md")

    # --- modes (cognitive operations) ---
    for name in MODE_FILES:
        if not os.path.isfile(C.rpath("modes", f"{name}.md")):
            errors.append(f"missing mode file: modes/{name}.md")

    # --- scopes (domain governance: one AGENTS.md each) ---
    for d in SCOPE_DIRS:
        if not os.path.isfile(C.rpath("scopes", d, "AGENTS.md")):
            errors.append(f"missing scope governance: scopes/{d}/AGENTS.md")

    # --- memory layer ---
    for f in ("README.md", "MEMORY.md"):
        if not os.path.isfile(C.rpath("memory", f)):
            errors.append(f"missing memory file: memory/{f}")
    mem_errs, mem_warns = _check_memory_items()
    errors.extend(mem_errs)
    warnings.extend(mem_warns)

    wg_errs, wg_warns = _check_work_graphs()
    errors.extend(wg_errs)
    warnings.extend(wg_warns)

    # --- protocols (from registry) ---
    for item in C.load_registry("protocols").get("protocols", []):
        if not os.path.isfile(C.rpath(item["path"])):
            errors.append(f"protocols registry points at missing file: {item['path']}")

    # --- styles / templates / evaluation (fixed sets) ---
    for n in STYLE_FILES:
        if not os.path.isfile(C.rpath("styles", f"{n}.md")):
            errors.append(f"missing style file: styles/{n}.md")
    for n in TEMPLATE_FILES:
        if not os.path.isfile(C.rpath("templates", f"{n}.md")):
            errors.append(f"missing template: templates/{n}.md")
    for n in EVALUATION_FILES:
        if not os.path.isfile(C.rpath("evaluation", f"{n}.md")):
            errors.append(f"missing evaluation rubric: evaluation/{n}.md")

    # --- commands: exist + valid frontmatter ---
    for item in C.load_registry("commands").get("commands", []):
        p = C.rpath(item["path"])
        if not os.path.isfile(p):
            errors.append(f"commands registry points at missing file: {item['path']}")
            continue
        errors.extend(_check_frontmatter(p, item["path"]))

    # --- skills / projects registry paths exist ---
    # An `archived` entry describes something deliberately not present: the
    # archive lives on its own branch so a clone does not carry 26 MB of retired
    # skills. The registry keeps the row so the record of what was retired, and
    # what superseded it, survives. Requiring the directory would make that
    # record itself the error.
    for reg_name, key in (("skills", "skills"), ("projects", "projects")):
        for item in C.load_registry(reg_name).get(key, []):
            if item.get("status") == "archived":
                continue
            if not os.path.isdir(C.rpath(item["path"])):
                errors.append(
                    f"{reg_name} registry points at missing dir: {item['path']}")

    # --- leakage guard: no project terms in universal layers ---
    blocklist = config.get("kernel_leakage_blocklist", [])
    if blocklist:
        for d in AGNOSTIC_DIRS:
            errors.extend(_scan_leakage(d, blocklist))

    # --- markdown cross-references resolve ---
    errors.extend(_check_md_refs())

    # --- no orphaned templates/rubrics ---
    errors.extend(_check_orphans())
    errors.extend(_check_skills())

    # --- hook layer: scripts must exist; settings.json wiring is warn-only ---
    for n in HOOK_SCRIPTS:
        if not os.path.isfile(C.rpath("scripts", "hooks", n)):
            errors.append(f"missing hook script: scripts/hooks/{n}")

    # --- bridge presence (warn only; generated by install_bridge.py) ---
    root = C.rpath(config.get("bridge", {}).get("root_relative", ".."))
    if not os.path.isfile(os.path.join(root, "CLAUDE.md")):
        warnings.append("bridge not installed: ../CLAUDE.md missing "
                        "(run scripts/install_bridge.py)")
    settings_path = os.path.join(root, ".claude", "settings.json")
    if not os.path.isfile(settings_path):
        warnings.append("hook layer not installed: .claude/settings.json "
                        "missing (run scripts/install_bridge.py)")
    else:
        # The old check was "does the string /scripts/hooks/ appear anywhere",
        # which one surviving entry out of six satisfied. Check each hook is
        # registered, and registered on the event it belongs to.
        try:
            with open(settings_path, "r", encoding="utf-8") as fh:
                settings = json.load(fh)
        except (ValueError, OSError) as exc:
            warnings.append(f"cannot read .claude/settings.json: {exc}")
        else:
            events = settings.get("hooks") or {}
            for script, event in sorted(WIRED_HOOKS.items()):
                serialised = json.dumps(events.get(event) or [])
                if f"/scripts/hooks/{script}" not in serialised:
                    warnings.append(
                        f"hook not wired: {script} is not registered on "
                        f"{event} in .claude/settings.json "
                        "(run scripts/install_bridge.py)")

    # --- gates that switch themselves off ---
    # `_hooklib.active_project()` returns None unless exactly one project is
    # active, and three enforcement paths key off it: the deletion guard, the
    # plan-before-edit reminder, and the validation-evidence check. Registering a
    # second active project therefore disables all three, silently. So does an
    # empty `validation.commands` on the one that is active. Neither is an error
    # -- both are legitimate states -- but neither should be invisible.
    try:
        actives = [pr for pr in C.load_registry("projects").get("projects", [])
                   if pr.get("status") == "active"]
    except Exception:
        actives = []
    if len(actives) > 1:
        names = ", ".join(sorted(pr.get("name", "?") for pr in actives))
        warnings.append(
            f"{len(actives)} projects are active ({names}); the hooks resolve a "
            "project only when exactly one is, so the deletion guard, the "
            "plan-before-edit reminder and the validation-evidence check are all "
            "inactive")
    for project in actives:
        try:
            pconf = C.load_yaml(C.rpath(project["path"], "project.config.yaml")) or {}
        except Exception:
            continue
        commands = ((pconf.get("validation") or {}).get("commands")
                    if isinstance(pconf.get("validation"), dict) else None)
        env = pconf.get("environment")
        mode = (str(env.get("verification_mode") or "").strip().lower()
                if isinstance(env, dict) else "")
        # The gate has two satisfying shapes and this check knew only one. An
        # analysis_only project owes an analytic verification that states its
        # ceiling instead of a command that ran (stop_gate, modes/verify.md), so
        # an empty validation.commands is correct there rather than a gap.
        if not commands and mode != "analysis_only":
            warnings.append(
                f"project '{project.get('name', '?')}' declares no "
                "validation.commands and is not verification_mode: "
                "analysis_only, so the stop gate asks for no evidence that "
                "anything was run")

    warnings.extend(_check_router_engagement())

    # --- report ---
    for w in warnings:
        print(f"WARN  {w}")
    if errors:
        for e in errors:
            print(f"FAIL  {e}")
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s). FAILED.")
        return 1

    print(f"OK    harness structure valid "
          f"({len(warnings)} warning(s)).")
    return 0


def _check_router_engagement():
    """Warn when skills have stopped firing.

    A library degrades silently: descriptions drift, near-duplicates crowd each
    other out, and the router ends up picking nothing. The end-task metric moves
    last; engagement moves first, which is what makes it worth checking here.

    Two things this deliberately does *not* do. It stays silent with no data —
    a fresh log is not a finding. And it never names a skill to cut: engagement
    is a property of the library as a whole, and the per-skill verdict needs a
    sample this check has no way to know it has.
    """
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import audit_session
        stats = audit_session.library_stats()
    except Exception:
        return []
    engagement = stats.get("engagement")
    if engagement is None or stats.get("evaluated", 0) < 20:
        return []
    if engagement >= audit_session.ENGAGEMENT_FLOOR:
        return []
    return [f"router engagement is {engagement:.0%} over "
            f"{stats['evaluated']} evaluated session(s) — a skill fires in "
            "fewer than "
            f"{audit_session.ENGAGEMENT_FLOOR:.0%} of them. Run "
            "`scripts/audit_session.py --library`; this is a routing or "
            "description problem before it is a skill-quality one"]


def _check_frontmatter(path, rel):
    errs = []
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    if not text.startswith("---"):
        errs.append(f"command missing frontmatter: {rel}")
        return errs
    parts = text.split("---", 2)
    if len(parts) < 3:
        errs.append(f"command frontmatter not closed: {rel}")
        return errs
    if "description:" not in parts[1]:
        errs.append(f"command frontmatter missing 'description': {rel}")
    return errs


def _check_md_refs():
    """Check that backtick `path/to/file.md` references point at real files.

    Only refs containing a '/' are checked (bare filenames are too ambiguous);
    placeholders (<>, {}, *, $), absolute/outside paths, and URLs are skipped.
    """
    errs = []
    hdir_prefix = os.path.basename(C.harness_root()) + "/"
    targets = list(MD_REF_TOP)
    for d in MD_REF_DIRS:
        base = C.rpath(d)
        if not os.path.isdir(base):
            continue
        for fn in sorted(os.listdir(base)):
            if fn.endswith(".md"):
                targets.append(f"{d}/{fn}")
    # scopes are nested (scopes/<domain>/AGENTS.md) — add their governance files.
    scopes_base = C.rpath("scopes")
    if os.path.isdir(scopes_base):
        for d in sorted(os.listdir(scopes_base)):
            f = f"scopes/{d}/AGENTS.md"
            if os.path.isfile(C.rpath(f)):
                targets.append(f)
    for rel in targets:
        fp = C.rpath(rel)
        if not os.path.isfile(fp):
            continue
        with open(fp, "r", encoding="utf-8") as fh:
            content = fh.read()
        for m in _MD_REF_RE.finditer(content):
            ref = m.group(1)
            if any(c in ref for c in "<>{}*$") or ref.startswith(("/", "../", "~", "http")):
                continue
            if "/" not in ref:
                continue
            r = ref[len(hdir_prefix):] if ref.startswith(hdir_prefix) else ref
            if os.path.isfile(C.rpath(r)):
                continue
            if os.path.isfile(os.path.join(os.path.dirname(fp), r)):
                continue
            errs.append(f"dangling .md reference '{ref}' in {rel}")
    return errs


def _check_skills():
    """The four contract rules in skills/README.md that nothing enforced.

    Validation checked only that a registry row's path exists. The README also
    requires each skill to *be* a skill: a SKILL.md, a frontmatter `name` equal
    to its directory, that name unique among active skills, and a description —
    the field the router selects on. A skill missing the last one is invisible;
    a duplicated name is two skills fighting over one identity. Both are the
    kind of silent defect this validator exists to make loud.
    """
    errs = []
    base = C.rpath("skills")
    if not os.path.isdir(base):
        return errs
    seen = {}
    for entry in sorted(os.listdir(base)):
        d = os.path.join(base, entry)
        if not os.path.isdir(d) or entry in ("shared-references", "__pycache__"):
            continue
        path = os.path.join(d, "SKILL.md")
        if not os.path.isfile(path):
            # A template ships SKILL.md.template so the live symlink never
            # serves it; that is deliberate, not a missing skill.
            if not os.path.isfile(path + ".template"):
                errs.append(f"skills/{entry}/: no SKILL.md")
            continue
        try:
            with open(path, "r", encoding="utf-8") as fh:
                fm = _claims.parse_frontmatter(fh.read()) or {}
        except Exception:
            errs.append(f"skills/{entry}/SKILL.md: unreadable frontmatter")
            continue
        name = (fm.get("name") or "").strip()
        if not name:
            errs.append(f"skills/{entry}/SKILL.md: frontmatter has no 'name'")
        elif name != entry:
            errs.append(f"skills/{entry}/SKILL.md: frontmatter name '{name}' "
                        "does not match its directory")
        if not (fm.get("description") or "").strip():
            errs.append(f"skills/{entry}/SKILL.md: no 'description' — the "
                        "router selects on this field, so the skill is "
                        "unreachable without it")
        if name:
            seen.setdefault(name, []).append(entry)
    for name, dirs in sorted(seen.items()):
        if len(dirs) > 1:
            errs.append(f"skill name '{name}' is claimed by {len(dirs)} "
                        f"directories: {', '.join(dirs)}")
    return errs


def _check_orphans():
    """Every templates/ and evaluation/ file must be referenced by filename from
    at least one other live harness file, else it is dead decoration."""
    errs = []
    corpus = []  # (relpath, content) pairs
    for rel in ORPHAN_CORPUS_TOP:
        fp = C.rpath(rel)
        if os.path.isfile(fp):
            with open(fp, "r", encoding="utf-8") as fh:
                corpus.append((rel, fh.read()))
    for d in ORPHAN_CORPUS_DIRS:
        base = C.rpath(d)
        if not os.path.isdir(base):
            continue
        # Walk, not listdir: skills/ holds its files one level down
        # (skills/<name>/SKILL.md), and a flat read finds none of them.
        for root, dirs, files in os.walk(base):
            dirs[:] = [x for x in dirs if x not in ("__pycache__", "_archive")]
            for fn in sorted(files):
                if not fn.endswith(".md"):
                    continue
                full = os.path.join(root, fn)
                rel = os.path.relpath(full, C.rpath("")).replace(os.sep, "/")
                with open(full, "r", encoding="utf-8") as fh:
                    corpus.append((rel, fh.read()))
    for d in ORPHAN_DIRS:
        base = C.rpath(d)
        if not os.path.isdir(base):
            continue
        for fn in sorted(os.listdir(base)):
            if not fn.endswith(".md"):
                continue
            rel = f"{d}/{fn}"
            if not any(fn in content for r, content in corpus if r != rel):
                errs.append(f"orphan file (referenced nowhere in the live "
                            f"harness): {rel}")
    return errs


MEMORY_ITEM_DIRS = ["decisions", "patterns", "project_states", "claims",
                    "archived"]
_REQUIRED_MEM_KEYS = ("name:", "scope:")


def _check_memory_items():
    """Each memory item (a .md under memory/<bucket>/) must carry frontmatter with
    at least name: and scope: — an item written by the distiller or by hand that
    lacks it would read back with no provenance (memory/README.md).

    Claims (scope: claim) additionally run the falsifiability invariant: a
    settled claim must carry threshold + evidence + a dated review_at
    (`scripts/_claims.py`, `memory/claims/README.md`). A settled claim past its
    review_at is reported as a staleness warning, not a hard failure — time
    passing is not a structural defect, but it must be visible.

    Returns (errors, warnings). Underscore-prefixed files (templates) are
    skipped, matching the README/MEMORY.md exclusions.
    """
    errs, warns = [], []
    for d in MEMORY_ITEM_DIRS:
        base = C.rpath("memory", d)
        if not os.path.isdir(base):
            continue
        for fn in sorted(os.listdir(base)):
            if (not fn.endswith(".md") or fn.startswith("_")
                    or fn in ("README.md", "MEMORY.md")):
                continue
            rel = f"memory/{d}/{fn}"
            with open(os.path.join(base, fn), "r", encoding="utf-8") as fh:
                text = fh.read()
            if not text.startswith("---"):
                errs.append(f"memory item missing frontmatter: {rel}")
                continue
            fm = text.split("---", 2)[1] if text.count("---") >= 2 else ""
            missing = [k for k in _REQUIRED_MEM_KEYS if k not in fm]
            if missing:
                errs.append(f"memory item {rel} frontmatter missing: "
                            f"{', '.join(missing)}")
            parsed = _claims.parse_frontmatter(text)
            if _claims.is_claim(parsed):
                errs.extend(_claims.check_claim(parsed, rel))
                # A warning, not an error: some evidence is a runtime artifact
                # that legitimately does not travel with a clone. Saying so is
                # still worth more than the silence that let this harness's own
                # flagship claim sit `settled` citing a file never written.
                for gone in _claims.missing_evidence_paths(parsed.get("evidence")):
                    warns.append(f"claim {rel}: evidence cites '{gone}', which "
                                 "is not present here")
                if _claims.is_stale(parsed):
                    warns.append(f"stale claim (settled but review_at "
                                 f"{parsed.get('review_at')} has passed — "
                                 f"re-verify, then bump review_at or archive): "
                                 f"{rel}")
    return errs, warns


def _check_work_graphs():
    """The work-state dependency graph (open_questions.md / known_issues.md) must
    not lie: a dangling blocked_by/supersedes edge or a blocked_by cycle is a
    hard error; an item superseded but still open is a warning (it should be
    retired). Checked for the project template and every registered project
    (`scripts/work_graph.py`). Returns (errors, warnings)."""
    errs, warns = [], []
    # The template plus every registered project (the template is itself a
    # registry entry, so dedupe by resolved path to avoid checking it twice).
    targets = [("_project_template",
                C.rpath("projects", "_project_template", "memory"))]
    for item in C.load_registry("projects").get("projects", []):
        p = item.get("path")
        if p:
            targets.append((item.get("name", "?"), C.rpath(p, "memory")))
    seen = set()
    for name, md in targets:
        key = os.path.realpath(md)
        if key in seen or not os.path.isdir(md):
            continue
        seen.add(key)
        items = work_graph.load_items(md)
        e, w = work_graph.integrity_problems(items)
        errs.extend(f"work graph [{name}]: {x}" for x in e)
        warns.extend(f"work graph [{name}]: {x}" for x in w)
    return errs, warns


def _scan_leakage(reldir, blocklist):
    errs = []
    base = C.rpath(reldir)
    if not os.path.isdir(base):
        return errs
    for root, _dirs, files in os.walk(base):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            fp = os.path.join(root, fn)
            with open(fp, "r", encoding="utf-8") as fh:
                content = fh.read()
            for term in blocklist:
                if term in content:
                    rel = os.path.relpath(fp, C.harness_root())
                    errs.append(f"project term '{term}' leaked into {rel}")
    return errs


if __name__ == "__main__":
    raise SystemExit(main())
