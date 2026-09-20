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

"""Integrity check for evaluation/{trigger_tests,near_miss_tests}/cases.yaml.

The routing DECISION is model-evaluated (the cases are "run by reading", per
evaluation/README.md); this script does NOT judge whether routing is correct. It
checks that the golden set cannot silently rot: every mode / scope / skill a case
names must be REAL and ACTIVE (not archived). It is the guard that turns "a skill
was archived" into a loud, fixable test failure instead of a stale expectation no
one notices.

Usage:  python3 evaluation/check_routing_tests.py
Exit 0 if every reference resolves; 1 otherwise (prints each dangling reference).
"""

from __future__ import annotations

import os
import sys

HROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HROOT, "scripts"))
import _common as C


def _active(reg_name, key):
    """Names of active entries in a registry (status == 'active')."""
    out = set()
    for item in (C.load_registry(reg_name) or {}).get(key, []):
        if isinstance(item, dict) and item.get("status") == "active" and item.get("name"):
            out.add(item["name"])
    return out


def _load_cases(rel):
    path = os.path.join(HROOT, rel)
    if not os.path.isfile(path):
        return None
    data = C.load_yaml(path) or {}
    cases = data.get("cases", [])
    return cases if isinstance(cases, list) else []


def _as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def main():
    modes = _active("modes", "modes")
    scopes = _active("scopes", "scopes")
    skills = _active("skills", "skills")
    anyref = modes | scopes | skills

    errors, warns, n = [], [], 0

    trig = _load_cases("evaluation/trigger_tests/cases.yaml")
    if trig is None:
        warns.append("trigger_tests/cases.yaml not found")
        trig = []
    for c in trig:
        n += 1
        p = (c.get("prompt") or "?")[:48]
        m = c.get("expect_mode")
        if m and m not in modes:
            errors.append(f"[trigger] {p!r}: expect_mode '{m}' is not an active mode")
        s = c.get("expect_scope")
        if s and s not in scopes:
            errors.append(f"[trigger] {p!r}: expect_scope '{s}' is not an active scope")
        for sk in _as_list(c.get("expect_skill")):
            if sk not in skills:
                errors.append(f"[trigger] {p!r}: expect_skill '{sk}' is not an active skill")

    near = _load_cases("evaluation/near_miss_tests/cases.yaml")
    if near is None:
        warns.append("near_miss_tests/cases.yaml not found")
        near = []
    for c in near:
        n += 1
        p = (c.get("prompt") or "?")[:48]
        sn = c.get("should_not")
        if sn and sn not in anyref:
            errors.append(f"[near-miss] {p!r}: should_not '{sn}' names no active mode/scope/skill")
        for sk in _as_list(c.get("expect_skill")):
            if sk not in skills:
                errors.append(f"[near-miss] {p!r}: expect_skill '{sk}' is not an active skill")

    print(f"routing tests: {n} case(s) checked ({len(trig)} trigger + {len(near)} "
          f"near-miss) | active refs: {len(modes)} modes, {len(scopes)} scopes, "
          f"{len(skills)} skills")
    for w in warns:
        print("  warn: " + w)
    if errors:
        print(f"FAIL — {len(errors)} dangling reference(s):")
        for e in errors:
            print("  - " + e)
        return 1
    print("OK — every referenced mode/scope/skill is real and active.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
