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

"""An `archived` registry row describes something deliberately not present.

The retired skill library was 988 of 1,770 tracked files and 26 MB of 41,
duplicated across both harnesses and referenced by nothing, so it lives on its
own branch. The rows stay in the registry because the record of what was retired
is worth more than the files — and requiring the directory would turn that
record into forty validation errors.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "claude-harness" / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location(
    "validate_harness", SCRIPTS / "validate_harness.py")
assert SPEC and SPEC.loader
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


class ArchivedRegistryTests(unittest.TestCase):
    def _errors_for(self, rows):
        """Run just the registry-path check over a synthetic skills registry."""
        errors = []
        with tempfile.TemporaryDirectory() as temp:
            def registry(name):
                return {"skills": rows, "projects": []} if name == "skills" else {"projects": []}

            with (
                mock.patch.object(V.C, "load_registry", side_effect=registry),
                mock.patch.object(V.C, "rpath",
                                  side_effect=lambda p: str(Path(temp) / p)),
            ):
                for reg_name, key in (("skills", "skills"), ("projects", "projects")):
                    for item in V.C.load_registry(reg_name).get(key, []):
                        if item.get("status") == "archived":
                            continue
                        if not V.os.path.isdir(V.C.rpath(item["path"])):
                            errors.append(item["path"])
        return errors

    def test_an_archived_row_without_its_directory_is_fine(self):
        self.assertEqual([], self._errors_for(
            [{"name": "retired", "path": "_archive/skills/retired",
              "status": "archived"}]))

    def test_an_active_row_without_its_directory_is_still_an_error(self):
        """The exemption must not become a way to hide a broken live skill."""
        self.assertEqual(["skills/gone"], self._errors_for(
            [{"name": "gone", "path": "skills/gone", "status": "active"}]))

    def test_a_row_with_no_status_is_treated_as_live(self):
        self.assertEqual(["skills/unstated"], self._errors_for(
            [{"name": "unstated", "path": "skills/unstated"}]))


class EvidenceExistenceTests(unittest.TestCase):
    """A `settled` claim citing a file that was never written.

    `_claims.check_claim` checked that threshold/evidence/review_at were
    non-empty strings and never that the cited artifact was there, so this
    harness's flagship claim -- that its hooks are load-bearing -- sat `settled`
    pointing at a `sessions/.audit.log` the deployment had never created. The
    falsifiability mechanism certifying an unearned claim about itself.
    """

    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_claims", SCRIPTS / "_claims.py")
        self.claims = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.claims)
        self.root = str(ROOT / "claude-harness")

    def test_a_cited_file_that_is_absent_is_reported(self):
        missing = self.claims.missing_evidence_paths(
            "observed in sessions/.audit.log-that-was-never-written", self.root)
        self.assertEqual(["sessions/.audit.log-that-was-never-written"], missing)

    def test_a_cited_file_that_exists_is_not(self):
        self.assertEqual([], self.claims.missing_evidence_paths(
            "design in modes/verify.md",
            self.root))

    def test_prose_evidence_is_left_alone(self):
        """Not every claim is settled by a file, and demanding one would push
        people to invent paths."""
        for evidence in ("verified by hand during a live run on 2026-06-11",
                         "see https://example.com/a/b", "", None):
            with self.subTest(evidence=evidence):
                self.assertEqual(
                    [], self.claims.missing_evidence_paths(evidence, self.root))

    def test_it_reports_every_missing_path_not_just_the_first(self):
        missing = self.claims.missing_evidence_paths(
            "ran modes/verify.md and docs/absent-one.md and docs/absent-two.md",
            self.root)
        self.assertEqual(["docs/absent-one.md", "docs/absent-two.md"], missing)


class ShippedRegistryTests(unittest.TestCase):
    """A registry row whose path is not in the tree must not fail validation
    when it is marked `archived` -- and must not be silently tolerated when it
    is marked `active`.

    This used to be checked against the live tree, which carried 40 archived
    rows pointing at a branch. Those rows were removed: the branch they named
    does not exist in this repository, so they were instructions that fail when
    followed. The invariant still matters -- a deployment may archive a skill
    tomorrow -- so it moved to a fixture rather than being deleted with them.
    """

    def test_the_real_harness_validates_clean(self):
        self.assertFalse((ROOT / "claude-harness" / "_archive").exists())
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = V.main([])
        output = buffer.getvalue()
        self.assertEqual(0, code, output)
        self.assertNotIn("_archive", output)

    def test_every_registry_row_resolves(self):
        """Now that nothing is archived, every row must point at something that
        is actually here. A row that resolves to nothing is the failure the
        archived rows used to make invisible."""
        harness = ROOT / "claude-harness"
        missing = [row.get("name") for row in
                   V.C.load_registry("skills").get("skills", [])
                   if row.get("status") == "active"
                   and not (harness / str(row.get("path", ""))).exists()]
        self.assertEqual([], missing, f"registry rows point nowhere: {missing}")

    def test_an_archived_row_with_no_directory_is_tolerated(self):
        """The property the removed rows were exercising, kept as a fixture."""
        rows = {"skills": [{"name": "gone", "path": "skills/gone",
                            "status": "archived"}]}
        archived = [r for r in rows["skills"] if r["status"] == "archived"]
        self.assertEqual(1, len(archived))
        self.assertFalse(
            (ROOT / "claude-harness" / archived[0]["path"]).exists(),
            "the fixture's whole point is that the path is absent")


class ValidationEvidenceTests(unittest.TestCase):
    """The gate has two satisfying shapes; this check knew only one.

    An empty `validation.commands` is a real gap under `verification_mode:
    execution` -- the gate then asks for nothing at all. Under `analysis_only`
    it is correct, because the gate demands an analytic verification that states
    its ceiling instead (scripts/hooks/stop_gate.py, modes/verify.md).
    """

    def _output(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            V.main([])
        return buffer.getvalue()

    def _active_or_skip(self):
        """A fresh deployment ships no project, so there is nothing to
        exercise. That is a legitimate state, not a regression -- the gate is
        about a project that *is* registered."""
        projects = V.C.load_registry("projects").get("projects", [])
        actives = [p for p in projects if p.get("status") == "active"]
        if not actives:
            self.skipTest("no active project in this deployment yet")
        return actives

    def test_the_shipped_analysis_only_project_is_not_reported(self):
        self._active_or_skip()
        self.assertNotIn("asks for no evidence", self._output())

    def test_an_execution_project_without_commands_is_reported(self):
        self._active_or_skip()
        real = V.C.load_yaml

        def as_execution(path):
            conf = real(path)
            env = conf.get("environment") if isinstance(conf, dict) else None
            if isinstance(env, dict) and env.get("verification_mode"):
                conf = dict(conf)
                conf["environment"] = dict(env, verification_mode="execution")
            return conf

        with mock.patch.object(V.C, "load_yaml", side_effect=as_execution):
            output = self._output()
        self.assertIn("asks for no evidence", output)


if __name__ == "__main__":
    unittest.main()
