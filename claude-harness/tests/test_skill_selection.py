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

"""What predicts a bad skill selection, checked without any run data.

`skill_triggers.py` was argued from the wrong cost. It set out to shrink
descriptions because they are the largest part of the always-on surface — but
that surface is byte-stable between sessions and therefore sits in the cached
prefix, and when library size was measured against accuracy, selection failure
accounted for most of the degradation while context overhead was statistically
indistinguishable from zero. Bytes were never the binding constraint.

These tests pin the two checks that replaced it as the headline, both computable
offline: a model-invocable skill must be anchored by at least one literal
phrase, and two descriptions that read the same must be visible as a pair.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "claude-harness"
sys.path.insert(0, str(HARNESS / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "skill_triggers", HARNESS / "evaluation" / "skill_triggers.py")
assert SPEC and SPEC.loader
T = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(T)


def _entry(description, user_only=False):
    return {"description": description, "user_only": user_only,
            "triggers": sorted(T.triggers(description)),
            "bytes": len(description.encode("utf-8"))}


class UserInvokedOnlyTests(unittest.TestCase):
    def _skill(self, frontmatter):
        temp = tempfile.mkdtemp()
        path = Path(temp) / "SKILL.md"
        path.write_text(f"---\n{frontmatter}\n---\n\nbody\n", encoding="utf-8")
        return str(path)

    def test_it_reads_the_opt_out(self):
        path = self._skill("name: x\ndisable-model-invocation: true")
        self.assertTrue(T.user_invoked_only(path))

    def test_absent_means_model_invocable(self):
        self.assertFalse(T.user_invoked_only(self._skill("name: x")))

    def test_false_means_model_invocable(self):
        path = self._skill("name: x\ndisable-model-invocation: false")
        self.assertFalse(T.user_invoked_only(path))


class SignatureTests(unittest.TestCase):
    def test_trigger_phrases_are_excluded(self):
        """Two skills should be free to invite a request the same way. What
        must not collide is the claim about what they do."""
        sig = T._signature('Render a diagram. Use when user says "draw this".')
        self.assertIn("diagram", sig)
        self.assertNotIn("draw", sig)

    def test_frame_words_are_dropped(self):
        self.assertEqual(set(), T._signature("Use when the user says it is."))


class RedundancyTests(unittest.TestCase):
    def test_two_identical_claims_are_paired(self):
        current = {"a": _entry("Rent and manage cloud GPU instances."),
                   "b": _entry("Manage and rent cloud GPU instances.")}
        pairs = T.redundant_pairs(current)
        self.assertEqual(1, len(pairs), pairs)
        self.assertEqual(("a", "b"), pairs[0][1:])

    def test_unrelated_claims_are_not_paired(self):
        current = {"a": _entry("Rent and manage cloud GPU instances."),
                   "b": _entry("Write rigorous proofs for theorems.")}
        self.assertEqual([], T.redundant_pairs(current))

    def test_a_user_invoked_skill_cannot_be_half_of_a_pair(self):
        """It never enters the candidate set, so it shadows nothing."""
        current = {"a": _entry("Rent and manage cloud GPU instances."),
                   "b": _entry("Manage and rent cloud GPU instances.",
                               user_only=True)}
        self.assertEqual([], T.redundant_pairs(current))

    def test_the_threshold_is_the_calibrated_one(self):
        self.assertEqual(0.35, T.REDUNDANCY_THRESHOLD)


class ShippedLibraryTests(unittest.TestCase):
    def test_every_model_invocable_skill_is_anchored(self):
        current = T.collect()
        gaps = sorted(n for n, v in current.items()
                      if not v["triggers"] and not v["user_only"])
        self.assertEqual([], gaps)

    def test_the_opt_outs_are_the_two_that_mutate_things(self):
        current = T.collect()
        opted = sorted(n for n, v in current.items() if v["user_only"])
        self.assertEqual(["file-organizer", "skill-creator"], opted)

    def test_redundancy_stays_at_or_below_what_was_accepted(self):
        """`serverless-modal` ~ `vast-gpu` is a known sibling pair, reported and
        accepted. A second pair appearing means a description drifted."""
        pairs = T.redundant_pairs(T.collect())
        self.assertLessEqual(len(pairs), 1, pairs)


if __name__ == "__main__":
    unittest.main()
