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

"""The local amendment to a vendored skill has to survive re-vendoring.

`skills/ponytail/` is upstream's text with one section appended. The obvious
failure is a future `git checkout` of a newer upstream silently dropping that
section -- the skill would still load, still work, and quietly stop saying that
brevity may not be traded against correctness. Nothing would report it.

These pin the amendment's load-bearing clauses and the boundary that keeps it
diffable. They are deliberately about *presence*, not wording: a test that
pinned exact sentences would fail on every edit and get deleted.
"""

from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "claude-harness"
SKILL = HARNESS / "skills" / "ponytail" / "SKILL.md"
MARKER = "# ROBOTIS AI amendment"


class AmendmentPresenceTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SKILL.is_file(), f"{SKILL} is missing")
        self.text = SKILL.read_text(encoding="utf-8")

    def test_the_amendment_is_present_and_marked_local(self):
        self.assertIn(MARKER, self.text)
        head = self.text[self.text.index(MARKER):self.text.index(MARKER) + 200]
        self.assertIn("local", head.lower(),
                      "the amendment must announce that it is not upstream")

    def test_it_sits_below_a_rule_so_upstream_stays_diffable(self):
        """Everything above the `---` is upstream's, unchanged. That is what
        makes a diff against a newer upstream readable instead of a mess."""
        before = self.text[: self.text.index(MARKER)]
        self.assertTrue(before.rstrip().endswith("---"),
                        "the amendment must be separated by a horizontal rule")

    def test_it_does_not_weaken_the_ladder(self):
        """The amendment relaxes what 'lazy' may cost, never whether the ladder
        runs. If it ever reads as 'the ladder is optional', that is a different
        skill wearing this one's name."""
        body = self.text[self.text.index(MARKER):].lower()
        self.assertIn("mandatory", body)

    def test_the_four_clauses_survive(self):
        """Each clause exists because dropping it reintroduces a failure that
        was actually observed. Presence, not phrasing."""
        body = self.text[self.text.index(MARKER):].lower()
        for needle, why in (
                ("tiebreaker", "brevity must stay a tiebreaker among correct options"),
                ("budget", "the reasoning that precedes the ladder is not budgeted"),
                ("safety", "a safety path may never be deleted to save lines"),
                ("unverified", "the harness's report is not prose to trim"),
        ):
            with self.subTest(clause=needle):
                self.assertIn(needle, body, why)

    def test_it_forbids_padding(self):
        """The allowance is for correctness, safety and clarity. Without this
        line it reads as permission to write more code, which is the opposite
        of the skill it is amending."""
        body = self.text[self.text.index(MARKER):].lower()
        self.assertIn("pad", body)


class ScopeBindingTests(unittest.TestCase):
    """The amendment has to hold whether or not the skill happens to load."""

    def test_the_coding_scope_names_it(self):
        text = (HARNESS / "scopes" / "coding" / "AGENTS.md").read_text(
            encoding="utf-8")
        self.assertIn("ponytail", text)
        self.assertIn("amendment", text.lower())

    def test_provenance_is_recorded(self):
        text = (HARNESS / "skills" / "ponytail" / "UPSTREAM.md").read_text(
            encoding="utf-8")
        self.assertIn("amendment", text.lower())
        self.assertIn("MIT", text)


class LicenceTests(unittest.TestCase):
    def test_the_mit_notice_travels_with_the_vendored_skill(self):
        licence = HARNESS / "skills" / "ponytail" / "LICENSE"
        self.assertTrue(licence.is_file(), "MIT requires the notice be kept")
        text = licence.read_text(encoding="utf-8")
        self.assertIn("MIT License", text)
        self.assertIn("Copyright", text)


if __name__ == "__main__":
    unittest.main()
