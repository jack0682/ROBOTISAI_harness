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

"""Run the routing golden set against the mechanical router — do not just read it.

The 33 cases in trigger_tests/ and near_miss_tests/ were specified as "run by
reading": take the prompt, decide what ROUTING.md would select, compare. That is
the right way to check the *table*, which only a reader applies. But there is
also a machine in this harness that routes — `scripts/hooks/route_hint.py`, six
regexes fired on every user prompt — and nothing ever ran the golden set against
it. Its patterns had no tests at all.

The distinction this enforces: `route_hint` routes to a **scope**. It names that
scope's typical modes as a convenience, and does not decide them. So scope-level
expectations are asserted here, and mode-level ones are reported and left to the
reader, because asserting them would be testing the regexes for a judgement they
do not make.

    python3 evaluation/run_routing_tests.py [-v]

Exit 1 if any scope-level expectation fails.
"""

from __future__ import annotations

import importlib.util
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
import _common as C  # noqa: E402

_SPEC = importlib.util.spec_from_file_location(
    "route_hint", os.path.join(_ROOT, "scripts", "hooks", "route_hint.py"))
_ROUTE_HINT = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_ROUTE_HINT)


def routed_scopes(prompt):
    """Exactly what the hook would surface for this prompt."""
    return [scope for scope, pattern, _, _ in _ROUTE_HINT.ROUTES
            if re.search(pattern, prompt, re.I)]


def _cases(name):
    path = os.path.join(_HERE, name, "cases.yaml")
    return (C.load_yaml(path) or {}).get("cases", []) or []


def _known_scopes():
    return {s["name"] for s in C.load_registry("scopes").get("scopes", [])}


def main(argv=None):
    verbose = "-v" in (argv if argv is not None else sys.argv[1:])
    scopes = _known_scopes()
    failures, checked, deferred = [], 0, 0

    for case in _cases("trigger_tests"):
        want = case.get("expect_scope")
        if not want:
            deferred += 1
            continue
        if want not in scopes:
            failures.append(f"unknown scope '{want}' in: {case['prompt'][:60]}")
            continue
        checked += 1
        got = routed_scopes(case["prompt"])
        if want not in got:
            failures.append(
                f"trigger MISS  want={want:<12} got={got or '[]'}  "
                f"{case['prompt'][:56]}")
        elif verbose:
            print(f"ok    {want:<12} {case['prompt'][:56]}")

    for case in _cases("near_miss_tests"):
        avoid = case.get("should_not")
        if avoid not in scopes:
            # A mode-level near-miss. The router does not decide modes.
            deferred += 1
            continue
        checked += 1
        got = routed_scopes(case["prompt"])
        if avoid in got:
            failures.append(
                f"near-miss HIT want-no={avoid:<10} got={got}  "
                f"{case['prompt'][:56]}")
        elif verbose:
            print(f"ok    not-{avoid:<8} {case['prompt'][:56]}")

    # A scope nobody can reach mechanically is a scope the hook will never
    # surface, however well ROUTING.md describes it.
    unreachable = sorted(scopes - {r[0] for r in _ROUTE_HINT.ROUTES})
    for scope in unreachable:
        failures.append(f"scope '{scope}' has no route_hint pattern — the hook "
                        "can never surface it")

    print(f"routing: {checked} scope-level expectation(s) checked, "
          f"{deferred} mode-level left to the reader")
    if failures:
        for line in failures:
            print(f"FAIL  {line}")
        print(f"\n{len(failures)} routing failure(s).")
        return 1
    print("OK — the router agrees with every scope-level golden case.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
