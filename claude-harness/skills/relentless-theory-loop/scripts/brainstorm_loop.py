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

"""
brainstorm_loop.py

Append-only research workflow helper for long-horizon theory brainstorming.

This script does not call a model API. It manages Markdown logging structure,
extracts unresolved problems/questions, and prepares continuation handoffs.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import textwrap
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

CYCLE_HEADING_RE = re.compile(r"^## Cycle\s+(\d+)", re.MULTILINE)
SECTION_RE = re.compile(
    r"^### (?P<name>[^\n]+)\n(?P<body>.*?)(?=^### |\Z)", re.MULTILINE | re.DOTALL
)
CHECKBOX_RE = re.compile(r"^\s*[-*]\s*\[(?P<mark>[ xX])\]\s*(?P<text>.+?)\s*$")
BULLET_RE = re.compile(r"^\s*[-*]\s*(?P<text>.+?)\s*$")

KEYWORD_WEIGHTS = {
    "falsif": 4.0,
    "counterexample": 3.5,
    "mechanism": 3.0,
    "causal": 2.5,
    "prediction": 2.5,
    "predict": 2.5,
    "boundary": 2.3,
    "failure mode": 2.2,
    "assumption": 2.0,
    "rival": 2.0,
    "alternative": 1.8,
    "evidence": 1.8,
    "trade-off": 1.6,
    "tradeoff": 1.6,
    "why": 1.2,
}

CYCLE_TEMPLATE_ORDER = [
    "Current Problem",
    "Why It Matters",
    "Question",
    "Provisional Answer",
    "Objection",
    "Rival View",
    "Revision",
    "Open Problems",
    "Next Trigger Questions",
    "Auto-Selected Next Question",
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def canonicalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def append_text(path: Path, block: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        if path.stat().st_size > 0 and not block.startswith("\n"):
            f.write("\n")
        f.write(block)
        if not block.endswith("\n"):
            f.write("\n")


def resolve_value(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("@"):
        file_path = Path(raw[1:])
        if not file_path.exists():
            raise FileNotFoundError(f"Referenced file does not exist: {file_path}")
        return file_path.read_text(encoding="utf-8").strip()
    return raw


def resolve_values(values: Sequence[str]) -> List[str]:
    return [resolve_value(v) for v in values]


def next_cycle_number(markdown: str) -> int:
    matches = [int(m.group(1)) for m in CYCLE_HEADING_RE.finditer(markdown)]
    if not matches:
        return 1
    return max(matches) + 1


def format_text_or_list(items: Sequence[str]) -> str:
    cleaned = [i.strip() for i in items if i.strip()]
    if not cleaned:
        return "- [ ] TODO"
    if len(cleaned) == 1:
        return cleaned[0]
    return "\n".join(f"- {item}" for item in cleaned)


def format_checklist(items: Sequence[str]) -> str:
    cleaned = [i.strip() for i in items if i.strip()]
    if not cleaned:
        return "- [ ] TODO"
    return "\n".join(f"- [ ] {item}" for item in cleaned)


def iter_sections(markdown: str) -> Iterable[Tuple[str, str]]:
    for m in SECTION_RE.finditer(markdown):
        yield m.group("name").strip(), m.group("body").strip()


def parse_list_items(body: str) -> List[Tuple[str, bool]]:
    """
    Parse bullets/checklists from a markdown section body.

    Returns list of tuples: (text, is_open)
    - [ ] item -> open
    - [x] item -> closed
    - bullet item -> open by default
    """
    parsed: List[Tuple[str, bool]] = []
    for line in body.splitlines():
        line = line.rstrip()
        if not line:
            continue

        checkbox = CHECKBOX_RE.match(line)
        if checkbox:
            mark = checkbox.group("mark").lower()
            text = checkbox.group("text").strip()
            parsed.append((text, mark != "x"))
            continue

        bullet = BULLET_RE.match(line)
        if bullet:
            text = bullet.group("text").strip()
            parsed.append((text, True))

    # If no bullets were found, treat non-empty body as one open item.
    if not parsed and body.strip():
        parsed.append((body.strip(), True))

    return parsed


def extract_state(markdown: str) -> Dict[str, List[str]]:
    """
    Extract unresolved open problems and unresolved trigger questions using
    last-write-wins semantics by canonical text.
    """
    open_map: Dict[str, Tuple[str, bool]] = {}
    trigger_map: Dict[str, Tuple[str, bool]] = {}

    for name, body in iter_sections(markdown):
        normalized_name = canonicalize(name)
        entries = parse_list_items(body)

        if normalized_name == canonicalize("Open Problems"):
            for text, is_open in entries:
                key = canonicalize(text)
                open_map[key] = (text, is_open)

        if normalized_name == canonicalize("Next Trigger Questions"):
            for text, is_open in entries:
                key = canonicalize(text)
                trigger_map[key] = (text, is_open)

    unresolved_open = [v[0] for v in open_map.values() if v[1]]
    unresolved_triggers = [v[0] for v in trigger_map.values() if v[1]]

    return {
        "unresolved_open_problems": unresolved_open,
        "unresolved_trigger_questions": unresolved_triggers,
    }


def score_question(question: str) -> float:
    q = question.strip().lower()
    if not q:
        return -1.0

    score = 0.0

    # Slight preference for concrete, medium-length questions.
    length = len(q)
    if 35 <= length <= 220:
        score += 1.2
    elif length < 20:
        score -= 0.8

    if "?" in q:
        score += 0.8
    if q.startswith("what if"):
        score += 1.1
    if q.startswith("under what"):
        score += 0.7

    for token, weight in KEYWORD_WEIGHTS.items():
        if token in q:
            score += weight

    # Encourage discriminatory/testable framing.
    if "would" in q and "if" in q:
        score += 0.8
    if "versus" in q or "vs" in q:
        score += 0.9

    return score


def choose_strongest_question(questions: Sequence[str]) -> Tuple[str, float]:
    cleaned = [q.strip() for q in questions if q and q.strip()]
    if not cleaned:
        return "", -1.0

    ranked = sorted(((q, score_question(q)) for q in cleaned), key=lambda x: x[1], reverse=True)
    return ranked[0]


def render_init_block(project: str) -> str:
    created = utc_now()
    return textwrap.dedent(
        f"""\
        # Research Brainstorm Log

        ## Session Metadata
        - Created (UTC): {created}
        - Project: {project}
        - Mode: Theory-Lab (not publication prose)

        ## Process Rules
        - This file is append-only. Do not delete prior cycles.
        - Preserve failed paths and unresolved tensions.
        - Every cycle must include objection, rival view, revision, and deeper trigger questions.
        - Prefer long-horizon continuity over neat one-shot closure.

        ## Required Cycle Sections
        {"\n".join(f"- {name}" for name in CYCLE_TEMPLATE_ORDER)}
        """
    ).strip()


def cmd_init(args: argparse.Namespace) -> int:
    log_path = Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if not log_path.exists() or not read_text(log_path).strip():
        log_path.write_text(render_init_block(args.project), encoding="utf-8")
        print(f"Initialized log: {log_path}")
        return 0

    # Existing file: append a re-entry marker instead of overwriting.
    block = textwrap.dedent(
        f"""\
        ## Session Re-Entry ({utc_now()})
        - Project: {args.project}
        - Note: Continuing in append-only mode.
        """
    ).strip()
    append_text(log_path, block)
    print(f"Appended session re-entry marker: {log_path}")
    return 0


def cmd_append_cycle(args: argparse.Namespace) -> int:
    log_path = Path(args.log)
    existing = read_text(log_path)
    cycle_no = next_cycle_number(existing)

    objections = resolve_values(args.objection)
    rivals = resolve_values(args.rival_view)
    open_problems = resolve_values(args.open_problem)
    next_triggers = resolve_values(args.next_trigger)

    auto_selected = resolve_value(args.auto_selected_next) if args.auto_selected_next else ""
    if not auto_selected:
        auto_selected, _ = choose_strongest_question(next_triggers)
        if not auto_selected:
            auto_selected = "What is the deepest unresolved assumption in the current revision?"

    block = textwrap.dedent(
        f"""\
        ## Cycle {cycle_no:04d} ({utc_now()})

        ### Current Problem
        {resolve_value(args.current_problem)}

        ### Why It Matters
        {resolve_value(args.why_matters)}

        ### Question
        {resolve_value(args.question)}

        ### Provisional Answer
        {resolve_value(args.provisional_answer)}

        ### Objection
        {format_text_or_list(objections)}

        ### Rival View
        {format_text_or_list(rivals)}

        ### Revision
        {resolve_value(args.revision)}

        ### Open Problems
        {format_checklist(open_problems)}

        ### Next Trigger Questions
        {format_checklist(next_triggers)}

        ### Auto-Selected Next Question
        {auto_selected}
        """
    ).strip()

    append_text(log_path, block)

    result = {
        "log": str(log_path),
        "cycle": cycle_no,
        "auto_selected_next_question": auto_selected,
        "open_problems_added": len(open_problems),
        "trigger_questions_added": len(next_triggers),
    }
    print(json.dumps(result, indent=2))
    return 0


def build_status(log_path: Path) -> Dict[str, object]:
    markdown = read_text(log_path)
    if not markdown.strip():
        return {
            "log": str(log_path),
            "cycles": 0,
            "unresolved_open_problems": [],
            "unresolved_trigger_questions": [],
            "recommended_next_question": "",
            "recommended_score": -1.0,
        }

    cycles = [int(m.group(1)) for m in CYCLE_HEADING_RE.finditer(markdown)]
    state = extract_state(markdown)

    candidate_pool = state["unresolved_trigger_questions"]
    if not candidate_pool:
        # Fallback: convert open problems into prompts.
        candidate_pool = [f"How can we resolve: {p}?" for p in state["unresolved_open_problems"]]

    next_q, score = choose_strongest_question(candidate_pool)

    return {
        "log": str(log_path),
        "cycles": max(cycles) if cycles else 0,
        "unresolved_open_problems": state["unresolved_open_problems"],
        "unresolved_trigger_questions": state["unresolved_trigger_questions"],
        "recommended_next_question": next_q,
        "recommended_score": round(score, 3),
    }


def cmd_status(args: argparse.Namespace) -> int:
    log_path = Path(args.log)
    summary = build_status(log_path)

    if args.json:
        print(json.dumps(summary, indent=2))
        return 0

    print(f"Log: {summary['log']}")
    print(f"Cycles: {summary['cycles']}")
    print("\nUnresolved Open Problems:")
    for item in summary["unresolved_open_problems"]:
        print(f"- [ ] {item}")

    print("\nUnresolved Trigger Questions:")
    for item in summary["unresolved_trigger_questions"]:
        print(f"- [ ] {item}")

    print("\nRecommended Next Question:")
    if summary["recommended_next_question"]:
        print(f"{summary['recommended_next_question']} (score={summary['recommended_score']})")
    else:
        print("None found")

    return 0


def render_handoff_block(summary: Dict[str, object]) -> str:
    open_items = summary["unresolved_open_problems"]
    trigger_items = summary["unresolved_trigger_questions"]
    next_q = summary["recommended_next_question"]

    open_md = format_checklist(open_items if open_items else ["No unresolved open problems captured."])
    trigger_md = format_checklist(
        trigger_items if trigger_items else ["No trigger questions captured. Generate a new discriminating question."]
    )

    next_prompt = textwrap.dedent(
        f"""\
        Continue the research loop using this question:
        {next_q or 'What assumption is currently least justified, and what rival model best challenges it?'}

        In the next cycle, include at minimum:
        - one objection
        - one rival view
        - one revision
        - one newly added open problem
        - one newly added trigger question
        """
    ).strip()

    return textwrap.dedent(
        f"""\
        ## Continuation Handoff ({utc_now()})

        ### Open Problems Snapshot
        {open_md}

        ### Next Trigger Questions Snapshot
        {trigger_md}

        ### Auto-Selected Next Question
        {next_q or 'What assumption is currently least justified, and what rival model best challenges it?'}

        ### Suggested Next Cycle Prompt
        {next_prompt}
        """
    ).strip()


def cmd_select_next(args: argparse.Namespace) -> int:
    log_path = Path(args.log)
    summary = build_status(log_path)

    if args.append_handoff:
        append_text(log_path, render_handoff_block(summary))

    print(json.dumps(
        {
            "recommended_next_question": summary["recommended_next_question"],
            "recommended_score": summary["recommended_score"],
            "appended_handoff": bool(args.append_handoff),
            "log": str(log_path),
        },
        indent=2,
    ))
    return 0


def cmd_continue_loop(args: argparse.Namespace) -> int:
    log_path = Path(args.log)
    summary = build_status(log_path)

    if args.append_handoff:
        append_text(log_path, render_handoff_block(summary))

    next_question = summary["recommended_next_question"] or (
        "What assumption is currently least justified, and what rival hypothesis most strongly challenges it?"
    )

    ready_prompt = textwrap.dedent(
        f"""\
        NEXT CYCLE TRIGGER
        Question: {next_question}

        Required outputs for the next cycle:
        1) Provisional answer
        2) Objection
        3) Rival view
        4) Revision
        5) At least one open problem
        6) At least one deeper trigger question
        """
    ).strip()

    if args.json:
        print(
            json.dumps(
                {
                    "recommended_next_question": next_question,
                    "unresolved_open_problems": summary["unresolved_open_problems"],
                    "unresolved_trigger_questions": summary["unresolved_trigger_questions"],
                    "ready_prompt": ready_prompt,
                    "appended_handoff": bool(args.append_handoff),
                    "log": str(log_path),
                },
                indent=2,
            )
        )
    else:
        print(ready_prompt)

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Append-only brainstorming loop helper for long-horizon theory research."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize or re-enter a research Markdown log")
    p_init.add_argument("--log", required=True, help="Path to Markdown log file")
    p_init.add_argument("--project", default="Foundational Research", help="Project label")
    p_init.set_defaults(func=cmd_init)

    p_append = sub.add_parser("append-cycle", help="Append one structured research cycle")
    p_append.add_argument("--log", required=True, help="Path to Markdown log file")
    p_append.add_argument("--current-problem", required=True)
    p_append.add_argument("--why-matters", required=True)
    p_append.add_argument("--question", required=True)
    p_append.add_argument("--provisional-answer", required=True)
    p_append.add_argument("--objection", action="append", required=True, help="Repeat for multiple objections")
    p_append.add_argument("--rival-view", action="append", required=True, help="Repeat for multiple rivals")
    p_append.add_argument("--revision", required=True)
    p_append.add_argument("--open-problem", action="append", required=True, help="Repeat for multiple open problems")
    p_append.add_argument("--next-trigger", action="append", required=True, help="Repeat for multiple trigger questions")
    p_append.add_argument(
        "--auto-selected-next",
        help="Optional explicit next question; if omitted, script auto-selects from trigger questions",
    )
    p_append.set_defaults(func=cmd_append_cycle)

    p_status = sub.add_parser("status", help="Show unresolved state and recommended next question")
    p_status.add_argument("--log", required=True, help="Path to Markdown log file")
    p_status.add_argument("--json", action="store_true", help="Return JSON output")
    p_status.set_defaults(func=cmd_status)

    p_select = sub.add_parser(
        "select-next",
        help="Choose strongest next question from unresolved state, optionally appending handoff",
    )
    p_select.add_argument("--log", required=True, help="Path to Markdown log file")
    p_select.add_argument("--append-handoff", action="store_true", help="Append continuity handoff block")
    p_select.set_defaults(func=cmd_select_next)

    p_continue = sub.add_parser(
        "continue-loop",
        help="Generate continuation prompt and optionally append handoff block",
    )
    p_continue.add_argument("--log", required=True, help="Path to Markdown log file")
    p_continue.add_argument("--append-handoff", action="store_true", help="Append continuity handoff block")
    p_continue.add_argument("--json", action="store_true", help="Return JSON output")
    p_continue.set_defaults(func=cmd_continue_loop)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.func(args)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive fallback
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
