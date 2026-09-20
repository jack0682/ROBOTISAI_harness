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

"""Guard the phrases that make a skill selectable.

A skill is chosen by its `description`, and nothing in this harness ever checked
that a description still does its job.

**This file used to be argued from the wrong cost.** It was written to shrink
descriptions because they are the largest part of the always-on context. That
reasoning does not survive two facts. Prompt caching is prefix-matched over
`tools → system → messages`, and this harness's always-on surface is
byte-stable between sessions, so it sits in the cached prefix and is cheap.
And when a library's size was measured against its accuracy, selection failure
accounted for most of the degradation while context overhead was statistically
indistinguishable from zero. Bytes were never the binding constraint;
**selection** is.

So the byte budget stays, demoted: it is hygiene that keeps a description from
turning back into prose, not the headline. What this file now reports first are
the two things that actually predict a bad selection, both computable without
any run data:

  - **trigger gaps** — a description with no quoted phrase gives the router
    nothing literal to match, and is the shape most easily hidden by a
    near-duplicate. (A skill with `disable-model-invocation: true` is exempt: it
    is invisible to the router until the user names it, so it can neither
    shadow nor be shadowed.)
  - **redundancy** — two descriptions that read the same compete for the same
    request, and the router picks between them by coin-flip. This is what
    shadowing looks like before it costs anything.

The part that must survive every edit is the trigger phrases: the quoted strings
a user would actually say. The narrative around them ("uses a fresh cross-model
reviewer with web/DBLP/arXiv lookup to catch hallucinated authors...") describes
the mechanism, which belongs in the body — it does not help decide whether the
skill is relevant now.

    python3 evaluation/skill_triggers.py --snapshot   # record the baseline
    python3 evaluation/skill_triggers.py              # check against it

Exit 1 if a recorded trigger has disappeared, a model-invocable skill has no
trigger at all, or a description exceeds the budget.
"""

from __future__ import annotations

import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

SKILLS_DIR = os.path.join(_ROOT, "skills")
BASELINE = os.path.join(_HERE, "skill_triggers.json")

# A flat cap would punish a skill for having many ways to be asked for, which is
# the one part of a description that has to stay. The budget is therefore the
# fixed cost of a description -- one clause saying what the skill does, plus the
# "Use when the user says" frame -- on top of whatever its triggers cost.
DESCRIPTION_FRAME = 200
TOTAL_MAX = 18_000


def budget(trigger_bytes):
    return DESCRIPTION_FRAME + trigger_bytes


def trigger_bytes(trigger_set):
    """What the triggers themselves cost, quoted and comma-separated."""
    return sum(len(t.encode("utf-8")) + 4 for t in trigger_set)

_QUOTED = re.compile(r'[\\"“”]([^\\"“”\n]{2,60})[\\"“”]|[\'‘’]([^\'‘’\n]{2,60})[\'‘’]')


def _description(path):
    """The raw description value, whatever quoting style the file uses."""
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    match = re.search(r"^description:\s*(.*?)(?=\n[a-z-]+:|\n---)", text,
                      re.M | re.S)
    if not match:
        return ""
    value = " ".join(match.group(1).split())
    if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value


def triggers(description):
    """Quoted phrases a user would say. Order-independent, case-folded."""
    found = set()
    for a, b in _QUOTED.findall(description):
        phrase = (a or b).strip().lower()
        if phrase and not phrase.startswith("--"):
            found.add(phrase)
    return found


def user_invoked_only(path):
    """True when a skill opts out of model invocation.

    Such a skill never enters the router's candidate set, so it can neither
    shadow another nor be shadowed, and needs no trigger phrase.
    """
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError:
        return False
    if not text.startswith("---") or text.count("---") < 2:
        return False
    for line in text.split("---", 2)[1].splitlines():
        key, _, value = line.partition(":")
        if key.strip().lower() == "disable-model-invocation":
            return value.strip().lower() in ("true", "yes", "1")
    return False


# Words that carry no discriminating power between skills in this library -- a
# description made only of these is not describing what makes it different.
_STOPWORDS = frozenset("""
a an and are as at be by for from in into is it its of on or that the this to
use used user says when with your you skill claude 사용 할 때 하는 것 그
""".split())


def _signature(description):
    """The content words of a description, minus its trigger phrases.

    Triggers are removed first: two skills *should* share some phrasing in how
    they invite a request. What must not collide is the claim about what the
    skill does.
    """
    body = _QUOTED.sub(" ", description).lower()
    words = re.findall(r"[a-z]{3,}|[぀-ヿ一-鿿가-힯]{2,}",
                       body)
    return {w for w in words if w not in _STOPWORDS}


REDUNDANCY_THRESHOLD = 0.35
"""Calibrated against this library, not chosen a priori.

At 0.45 nothing surfaces. At 0.25 it floods with sibling pairs that are supposed
to resemble each other (`paper-plan`/`paper-write`, `arxiv`/`research-lit`). At
0.35 exactly one pair surfaces — `serverless-modal` ~ `vast-gpu` at 42% — which
is the pair whose shadowing trigger had to be removed on 2026-09-20. A threshold
that finds the known defect and nothing else is the one worth keeping.
"""


def redundant_pairs(current, threshold=REDUNDANCY_THRESHOLD):
    """Description pairs that read the same, by Jaccard over content words.

    Not a semantic judgement and not a verdict -- a high overlap is a prompt to
    look, because two descriptions competing for one request is what shadowing
    looks like before it has cost anything measurable.
    """
    sigs = {n: _signature(v["description"]) for n, v in current.items()
            if not v["user_only"] and v["description"]}
    pairs = []
    names = sorted(sigs)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            sa, sb = sigs[a], sigs[b]
            if not sa or not sb:
                continue
            overlap = len(sa & sb) / len(sa | sb)
            if overlap >= threshold:
                pairs.append((overlap, a, b))
    return sorted(pairs, reverse=True)


def collect():
    out = {}
    for name in sorted(os.listdir(SKILLS_DIR)):
        path = os.path.join(SKILLS_DIR, name, "SKILL.md")
        if not os.path.isfile(path):
            continue
        description = _description(path)
        out[name] = {"bytes": len(description.encode("utf-8")),
                     "description": description,
                     "user_only": user_invoked_only(path),
                     "triggers": sorted(triggers(description))}
    return out


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    current = collect()

    if "--snapshot" in argv:
        with open(BASELINE, "w", encoding="utf-8") as handle:
            json.dump({k: v["triggers"] for k, v in current.items()},
                      handle, indent=1, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
        total = sum(v["bytes"] for v in current.values())
        print(f"snapshot: {len(current)} skills, "
              f"{sum(len(v['triggers']) for v in current.values())} triggers, "
              f"{total:,}B of description")
        return 0

    try:
        with open(BASELINE, encoding="utf-8") as handle:
            baseline = json.load(handle)
    except (OSError, ValueError):
        print("FAIL  no trigger baseline; run --snapshot first")
        return 1

    failures = []
    for name, recorded in sorted(baseline.items()):
        if name not in current:
            # Retiring a skill is a decision; losing one is not. The registry
            # records the first, so only say something when it did not.
            failures.append(f"skill '{name}' is gone from skills/")
            continue
        lost = sorted(set(recorded) - set(current[name]["triggers"]))
        if lost:
            failures.append(f"{name}: lost trigger(s) {lost}")

    over = []
    for name, value in current.items():
        allowed = budget(trigger_bytes(set(value["triggers"])))
        if value["bytes"] > allowed:
            over.append((name, value["bytes"], allowed))
    for name, size, allowed in sorted(over, key=lambda x: x[1] - x[2], reverse=True):
        failures.append(f"{name}: description is {size}B, budget {allowed}B "
                        f"({len(current[name]['triggers'])} triggers) — move the "
                        "mechanism into the body, keep the triggers")

    # A model-invocable skill with no quoted phrase gives the router nothing
    # literal to match on. This is the headline check, not the byte count.
    gaps = sorted(name for name, v in current.items()
                  if not v["triggers"] and not v["user_only"])
    for name in gaps:
        failures.append(f"{name}: no trigger phrase — the router has nothing "
                        "literal to match, and an unanchored description is "
                        "the shape a near-duplicate hides. Add phrases, or set "
                        "disable-model-invocation: true if it should only run "
                        "when asked for by name")

    total = sum(v["bytes"] for v in current.values())
    if total > TOTAL_MAX:
        failures.append(f"descriptions total {total:,}B > {TOTAL_MAX:,}B — "
                        "hygiene, not a context bill: the always-on surface is "
                        "byte-stable and therefore cached. Over this line a "
                        "description has usually turned back into prose")

    pairs = redundant_pairs(current)
    print(f"skill triggers: {len(current)} skills, "
          f"{sum(len(v['triggers']) for v in current.values())} triggers "
          f"preserved, {len(gaps)} trigger gap(s), {len(pairs)} redundant "
          f"pair(s); {total:,}B of description (cap {TOTAL_MAX:,}B)")
    for overlap, a, b in pairs[:10]:
        print(f"      redundant  {overlap:.0%}  {a} ~ {b}")
    if pairs:
        print("      (a prompt to look, not a verdict — two descriptions "
              "competing for one request)")
    if failures:
        for line in failures:
            print(f"FAIL  {line}")
        print(f"\n{len(failures)} failure(s).")
        return 1
    print("OK — every recorded trigger survives, every model-invocable skill "
          "is anchored, and the budget holds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
