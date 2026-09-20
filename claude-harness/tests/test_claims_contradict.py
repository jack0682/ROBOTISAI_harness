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

"""A counterexample had nowhere to be written down against the claim it threatens.

The provenance relations this harness could express were Support
(threshold/evidence), Invalidate (supersedes) and Depend-on (the work graph's
blocked_by). `Contradict` was missing, so a result that conflicts with a standing
claim could only be acted on or forgotten -- in a harness whose central operation
is attacking its own conclusions. These tests pin the edge and the two rules that
make it load-bearing: settled cannot survive a standing contradiction, and an
edge may not name a claim that does not exist.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "claude-harness" / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("_claims", SCRIPTS / "_claims.py")
assert SPEC and SPEC.loader
C = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C)

SETTLED = """---
name: {name}
scope: claim
importance: high
status: {status}
threshold: a measurable bar
evidence: prose evidence that met it
review_at: 2099-01-01
supersedes: {supersedes}
contradicted_by: {contradicted_by}
source: a session
signature: sig-v1
---

The claim.
"""


def _write(dirpath, name, *, status="settled", supersedes="none",
           contradicted_by="none"):
    path = Path(dirpath) / f"{name}.md"
    path.write_text(SETTLED.format(name=name, status=status,
                                   supersedes=supersedes,
                                   contradicted_by=contradicted_by),
                    encoding="utf-8")
    return str(path)


class ContradictionParsingTests(unittest.TestCase):
    def test_none_and_blank_read_as_no_contradiction(self):
        for value in ("none", "", "  ", "n/a", "~"):
            with self.subTest(value=value):
                self.assertEqual([], C.contradictions({"contradicted_by": value}))

    def test_it_reads_a_list(self):
        fm = {"contradicted_by": "alpha, beta; gamma"}
        self.assertEqual(["alpha", "beta", "gamma"], C.contradictions(fm))

    def test_is_contradicted_matches(self):
        self.assertTrue(C.is_contradicted({"contradicted_by": "alpha"}))
        self.assertFalse(C.is_contradicted({"contradicted_by": "none"}))


class SettledUnderContradictionTests(unittest.TestCase):
    def test_settled_with_a_standing_contradiction_is_an_error(self):
        with tempfile.TemporaryDirectory() as temp:
            _write(temp, "challenger")
            path = _write(temp, "disputed", contradicted_by="challenger")
            errs, is_claim, _ = C.check_file(path)
            self.assertTrue(is_claim)
            self.assertTrue(any("contradicted_by" in e for e in errs), errs)

    def test_reopening_the_claim_clears_the_error(self):
        """The resolution is to reopen it, not to delete the edge."""
        with tempfile.TemporaryDirectory() as temp:
            _write(temp, "challenger")
            path = _write(temp, "disputed", status="open",
                          contradicted_by="challenger")
            errs, _, _ = C.check_file(path)
            self.assertEqual([], errs)

    def test_an_uncontradicted_settled_claim_still_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            path = _write(temp, "fine")
            self.assertEqual([], C.check_file(path)[0])


class DanglingEdgeTests(unittest.TestCase):
    """The work graph calls a dangling edge an error; claims did not check at all."""

    def test_a_contradiction_naming_nothing_is_an_error(self):
        with tempfile.TemporaryDirectory() as temp:
            path = _write(temp, "disputed", status="open",
                          contradicted_by="never-written")
            errs, _, _ = C.check_file(path)
            self.assertTrue(any("never-written" in e for e in errs), errs)

    def test_a_supersedes_naming_nothing_is_an_error(self):
        with tempfile.TemporaryDirectory() as temp:
            path = _write(temp, "successor", supersedes="ghost")
            errs, _, _ = C.check_file(path)
            self.assertTrue(any("ghost" in e for e in errs), errs)

    def test_an_edge_that_resolves_is_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            _write(temp, "ancestor")
            path = _write(temp, "successor", supersedes="ancestor")
            self.assertEqual([], C.check_file(path)[0])

    def test_a_slug_written_as_a_filename_still_resolves(self):
        with tempfile.TemporaryDirectory() as temp:
            _write(temp, "ancestor")
            path = _write(temp, "successor", supersedes="ancestor.md")
            self.assertEqual([], C.check_file(path)[0])


class ImportanceTests(unittest.TestCase):
    def test_an_out_of_enum_importance_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "x.md"
            path.write_text(SETTLED.format(name="x", status="open",
                                           supersedes="none",
                                           contradicted_by="none")
                            .replace("importance: high", "importance: critical"),
                            encoding="utf-8")
            errs, _, _ = C.check_file(str(path))
            self.assertTrue(any("importance" in e for e in errs), errs)


class ShippedClaimTests(unittest.TestCase):
    def test_the_real_claims_bucket_still_validates(self):
        """Every shipped claim validates.

        A fresh deployment ships no claims -- claims are earned by a session,
        not distributed -- so an empty bucket is skipped rather than failed.
        The moment one exists, this guards it again.
        """
        base = ROOT / "claude-harness" / "memory" / "claims"
        checked = 0
        for path in sorted(base.glob("*.md")):
            if path.name.startswith("_") or path.name == "README.md":
                continue
            errs, is_claim, _ = C.check_file(str(path))
            if is_claim:
                checked += 1
                self.assertEqual([], errs, f"{path.name}: {errs}")
        if not checked:
            self.skipTest("no claims in this deployment yet")


if __name__ == "__main__":
    unittest.main()
