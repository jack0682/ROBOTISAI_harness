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

"""Attaching to an external repo must not disarm the project it is not.

There was nothing between "no harness" and "full project registration + bridge +
hooks", so diagnosing someone else's repo for an afternoon either got the whole
deployment or — in practice — got nothing, and the work happened with no work
graph and no claim discipline.

The trap in adding the small end is `_hooklib.active_project()`: it resolves a
project only when exactly **one** row is `status: active`, and a second active
row silently switches off the deletion guard, the plan-before-edit reminder and
the validation-evidence check on the real project. An analysis target is
therefore registered `status: analysis`. These tests pin that, and pin that
nothing is written into the target repository.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "claude-harness"
SCRIPTS = HARNESS / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "hooks"))

SPEC = importlib.util.spec_from_file_location(
    "new_analysis", SCRIPTS / "new_analysis.py")
assert SPEC and SPEC.loader
A = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)

HSPEC = importlib.util.spec_from_file_location(
    "_hooklib", SCRIPTS / "hooks" / "_hooklib.py")
assert HSPEC and HSPEC.loader
H = importlib.util.module_from_spec(HSPEC)
HSPEC.loader.exec_module(H)


class StatusTests(unittest.TestCase):
    def test_an_analysis_target_is_not_active(self):
        """The whole reason the status exists."""
        self.assertEqual("analysis", A.STATUS)
        self.assertNotEqual("active", A.STATUS)

    def test_the_hook_layer_only_resolves_active_rows(self):
        source = (SCRIPTS / "hooks" / "_hooklib.py").read_text(encoding="utf-8")
        self.assertIn('p.get("status") == "active"', source)

    def test_the_live_registry_still_resolves_one_project(self):
        """Registering analysis targets must never make this ambiguous.

        The invariant is *unambiguous* resolution, not *non-empty*: a fresh
        deployment ships no project at all, and the gates correctly resolve to
        None there. What must never happen is analysis rows leaking into the
        active set, or two actives existing at once.
        """
        registry = (HARNESS / "registry" / "projects.yaml").read_text(
            encoding="utf-8")
        actives = [line for line in registry.splitlines()
                   if line.strip() == "status: active"]
        self.assertLessEqual(len(actives), 1,
                             f"more than one active project row: {actives}")
        project = H.active_project()
        if actives:
            self.assertIsNotNone(project, "an active row resolves to nothing")
        else:
            self.assertIsNone(
                project, f"no active row, yet the gates resolved {project}")


class ScaffoldTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.mkdtemp()
        self.target = os.path.join(self.temp, "someone-elses-repo")
        os.makedirs(os.path.join(self.target, "src"))
        Path(self.target, "src", "a.py").write_text("x = 1\n", encoding="utf-8")
        self.harness = os.path.join(self.temp, "harness")
        os.makedirs(os.path.join(self.harness, "registry"))
        Path(self.harness, "registry", "projects.yaml").write_text(
            "projects:\n- name: real\n  path: projects/real\n"
            "  status: active\n  skills: []\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.temp, ignore_errors=True)

    def _run(self, *args):
        def rpath(*parts):
            return os.path.join(self.harness, *parts)
        with mock.patch.object(A.C, "rpath", side_effect=rpath):
            return A.main(list(args))

    def test_it_writes_nothing_into_the_target_repository(self):
        before = sorted(os.listdir(self.target))
        self.assertEqual(0, self._run(self.target))
        self.assertEqual(before, sorted(os.listdir(self.target)))
        for junk in ("CLAUDE.md", ".claude", ".claude-plugin"):
            self.assertFalse(os.path.exists(os.path.join(self.target, junk)),
                             junk)

    def test_it_scaffolds_a_work_graph_and_a_claims_area(self):
        self._run(self.target, "probe")
        base = os.path.join(self.harness, "analysis", "probe")
        for rel in ("README.md", "memory/open_questions.md",
                    "memory/known_issues.md", "claims"):
            with self.subTest(rel=rel):
                self.assertTrue(os.path.exists(os.path.join(base, *rel.split("/"))))

    def test_it_registers_the_target_as_analysis_not_active(self):
        self._run(self.target, "probe")
        text = Path(self.harness, "registry", "projects.yaml").read_text(
            encoding="utf-8")
        self.assertIn("probe", text)
        self.assertIn("analysis", text)
        self.assertEqual(1, text.count("status: active"),
                         "a second active row disarms the real project's gates")

    def test_it_refuses_a_path_that_is_not_a_directory(self):
        self.assertEqual(1, self._run(os.path.join(self.temp, "nope")))

    def test_it_refuses_to_clobber_an_existing_target(self):
        self._run(self.target, "probe")
        self.assertEqual(1, self._run(self.target, "probe"))

    def test_the_work_graph_parses_what_it_writes(self):
        self._run(self.target, "probe")
        spec = importlib.util.spec_from_file_location(
            "work_graph", SCRIPTS / "work_graph.py")
        wg = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(wg)
        items = wg.load_items(
            os.path.join(self.harness, "analysis", "probe", "memory"))
        # The template rows are placeholders and are skipped by design; what
        # matters is that parsing the scaffold does not error.
        self.assertIsInstance(items, dict)


class CommandTests(unittest.TestCase):
    def test_the_command_exists_and_is_registered(self):
        path = HARNESS / "commands" / "harness-analyze.md"
        self.assertTrue(path.is_file())
        registry = (HARNESS / "registry" / "commands.yaml").read_text(
            encoding="utf-8")
        self.assertIn("harness-analyze", registry)

    def test_the_command_names_both_brownfield_rules(self):
        """F6 is the mode F4 and F5 were found in; the command that opens it
        should carry them, or they are documented where nobody is standing."""
        text = (HARNESS / "commands" / "harness-analyze.md").read_text(
            encoding="utf-8")
        self.assertIn("protocols/debugging.md", text)
        self.assertIn("modes/verify.md", text)


if __name__ == "__main__":
    unittest.main()
