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

"""Scope loading was a prose obligation that nothing could enforce.

`ROUTING.md` Step 2 calls answering domain work from the spine alone the
harness's main failure mode, and the only mechanism behind it was `route_hint` —
six regexes over the *prompt*. A regex over the prompt never sees which file is
open, which is how the `control` scope came to exist in the directory, the
registry, `ROUTING.md` and the golden set while the hook could not surface it.

A path-scoped rule fires on the file instead. These tests pin the three rules
that exist, the four scopes that deliberately have none, and the two properties
that keep the mechanism from backfiring.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "claude-harness"
RULES = ROOT / ".claude" / "rules"
SCRIPTS = HARNESS / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location(
    "install_bridge", SCRIPTS / "install_bridge.py")
assert SPEC and SPEC.loader
B = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(B)

PATH_SCOPED = ("coding", "control", "experiments")
PROMPT_ONLY = ("math", "research", "writing", "prompts")


class RuleSetTests(unittest.TestCase):
    def test_only_the_path_identifiable_scopes_have_rules(self):
        self.assertEqual(sorted(PATH_SCOPED), sorted(B._SCOPE_RULES))

    def test_the_other_scopes_are_left_to_the_router(self):
        """A rule with no `paths:` loads unconditionally. Giving these one would
        grow the always-on surface to cover requests a path cannot identify."""
        for scope in PROMPT_ONLY:
            with self.subTest(scope=scope):
                self.assertNotIn(scope, B._SCOPE_RULES)
                self.assertFalse((RULES / f"scope-{scope}.md").exists())

    def test_every_rule_names_a_real_scope(self):
        for scope in B._SCOPE_RULES:
            with self.subTest(scope=scope):
                self.assertTrue(
                    (HARNESS / "scopes" / scope / "AGENTS.md").is_file())


class ShippedRuleTests(unittest.TestCase):
    def _rule(self, scope):
        return (RULES / f"scope-{scope}.md").read_text(encoding="utf-8")

    def test_each_rule_is_scoped_to_paths(self):
        for scope in PATH_SCOPED:
            with self.subTest(scope=scope):
                text = self._rule(scope)
                self.assertTrue(text.startswith("---"))
                self.assertIn("paths:", text.split("---")[1])

    def test_no_rule_imports_the_scope(self):
        """An `@` import is expanded at launch, which would put the whole scope
        into the always-on surface — the opposite of scoping it to a path."""
        for scope in PATH_SCOPED:
            with self.subTest(scope=scope):
                body = self._rule(scope).split("---", 2)[2]
                self.assertEqual(
                    [], re.findall(r"(?<![\w`])@[\w./-]+", body))

    def test_each_rule_points_at_its_scope_file(self):
        for scope in PATH_SCOPED:
            with self.subTest(scope=scope):
                self.assertIn(f"scopes/{scope}/AGENTS.md", self._rule(scope))

    def test_rules_stay_small(self):
        """They name a scope; they do not restate it."""
        for scope in PATH_SCOPED:
            with self.subTest(scope=scope):
                self.assertLess(len(self._rule(scope).encode("utf-8")), 2_000)


class GeneratorTests(unittest.TestCase):
    def test_it_writes_a_rule_per_scope(self):
        """One rule per scope, plus one per mandatory house standard.

        The two kinds ride the same mechanism but point at different things: a
        scope rule names `scopes/<name>/AGENTS.md`, a standard rule names
        `skills/<name>/SKILL.md`. Asserting a single body shape for both was
        what made this test wrong when the first standard was added.
        """
        with tempfile.TemporaryDirectory() as temp:
            written = [p for p in B._write_scope_rules(temp, "claude-harness")
                       if p]
            self.assertEqual(len(B._SCOPE_RULES) + len(B._STANDARD_RULES),
                             len(written))
            by_name = {Path(p).stem: Path(p).read_text(encoding="utf-8")
                       for p in written}
            for scope in B._SCOPE_RULES:
                text = by_name[f"scope-{scope}"]
                self.assertIn("paths:", text)
                self.assertIn("claude-harness/scopes/", text)
            for standard in B._STANDARD_RULES:
                text = by_name[standard]
                self.assertIn("paths:", text)
                self.assertIn(f"claude-harness/skills/{standard}/", text)

    def test_it_does_not_clobber_a_hand_edited_rule(self):
        """The shipped rules say more than the generated ones. Regenerating the
        bridge must not silently flatten them."""
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp) / ".claude" / "rules"
            base.mkdir(parents=True)
            mine = base / "scope-coding.md"
            mine.write_text("---\npaths:\n  - \"x\"\n---\nmine\n",
                            encoding="utf-8")
            B._write_scope_rules(temp, "claude-harness")
            self.assertIn("mine", mine.read_text(encoding="utf-8"))


class RoutingDocTests(unittest.TestCase):
    def test_routing_records_the_read_tool_precondition(self):
        """Measured 2026-09-20: a path-scoped rule fires on `Read` and not on
        `cat` through Bash. Three of seven scopes route that way, so reading
        through a shell command costs the scope with no visible sign. If that
        caveat is ever dropped from the file that claims to be the authority,
        the mechanism becomes silently conditional again."""
        text = (HARNESS / "ROUTING.md").read_text(encoding="utf-8")
        self.assertIn("`Read` tool", text)
        self.assertIn("Bash", text)

    def test_routing_documents_the_split(self):
        """`control` was documented everywhere and unreachable by the hook. The
        cure for that is not another mechanism — it is saying which mechanism
        covers which scope, in the file that claims to be the authority."""
        text = (HARNESS / "ROUTING.md").read_text(encoding="utf-8")
        self.assertIn(".claude/rules/", text)
        for scope in PATH_SCOPED:
            with self.subTest(scope=scope):
                self.assertIn(scope, text)


if __name__ == "__main__":
    unittest.main()
