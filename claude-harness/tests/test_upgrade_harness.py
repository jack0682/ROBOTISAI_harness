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

"""`upgrade_harness.py` is the only tool that moves improvements out to a
deployment, and it had no tests and no callers.

Measured against a real three-month-stale deployment, the version it shipped as
synced 17 files and never touched KERNEL.md, ROUTING.md, modes/ or scopes/ — it
upgraded a harness while leaving its constitution behind — and deleted one local
file without being asked. These pin both halves of the fix.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "claude-harness" / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location(
    "upgrade_harness", SCRIPTS / "upgrade_harness.py")
assert SPEC and SPEC.loader
U = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(U)

CONFIG = """harness:
  name: "test-harness"
distribution:
  synced_dirs:
    - kernel
    - modes
  synced_files:
    - KERNEL.md
"""


def _harness(base, files):
    base.mkdir(parents=True, exist_ok=True)
    for rel, body in files.items():
        path = base / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return base


class DistributionContractTests(unittest.TestCase):
    def test_the_contract_comes_from_the_config(self):
        with tempfile.TemporaryDirectory() as temp:
            root = _harness(Path(temp) / "h", {"harness.config.yaml": CONFIG})
            dirs, files = U._distribution(str(root))
        self.assertEqual(["kernel", "modes"], dirs)
        self.assertEqual(["KERNEL.md"], files)

    def test_a_missing_or_broken_config_falls_back(self):
        for name, body in {"missing": None, "garbage": "%%%not yaml%%%",
                           "wrong shape": "distribution: 5\n"}.items():
            with self.subTest(case=name):
                with tempfile.TemporaryDirectory() as temp:
                    root = Path(temp) / "h"
                    root.mkdir()
                    if body is not None:
                        (root / "harness.config.yaml").write_text(body, encoding="utf-8")
                    dirs, files = U._distribution(str(root))
                # The layers whose absence was the bug must be in the fallback.
                self.assertIn("modes", dirs)
                self.assertIn("scopes", dirs)
                self.assertIn("KERNEL.md", files)
                self.assertIn("ROUTING.md", files)

    def test_the_shipped_config_syncs_the_spine_and_the_routed_layers(self):
        """The regression that mattered: an upgrade that leaves KERNEL.md stale."""
        dirs, files = U._distribution(str(ROOT / "claude-harness"))
        for layer in ("kernel", "modes", "scopes", "protocols", "scripts", "tests"):
            self.assertIn(layer, dirs)
        for spine in ("KERNEL.md", "ROUTING.md"):
            self.assertIn(spine, files)

    def test_sync_targets_walks_the_declared_layers(self):
        with tempfile.TemporaryDirectory() as temp:
            root = _harness(Path(temp) / "h", {
                "harness.config.yaml": CONFIG,
                "KERNEL.md": "spine",
                "kernel/identity.md": "k",
                "modes/think.md": "m",
                "projects/onn/PROJECT.md": "local, must not be synced",
                "kernel/__pycache__/x.pyc": "junk",
            })
            targets = set(U._sync_targets(str(root)))
        self.assertEqual({"KERNEL.md", "kernel/identity.md", "modes/think.md"}, targets)


class VersionReportTests(unittest.TestCase):
    def test_the_version_is_read_from_the_config(self):
        with tempfile.TemporaryDirectory() as temp:
            root = _harness(Path(temp) / "h", {
                "harness.config.yaml": 'harness:\n  name: "x"\n  version: "0.3.0"\n'})
            self.assertEqual("0.3.0", U._harness_version(str(root)))

    def test_a_config_without_a_version_is_not_an_error(self):
        for name, body in {"no harness key": "distribution: {}\n",
                           "harness not a mapping": "harness: 5\n",
                           "no file": None}.items():
            with self.subTest(case=name):
                with tempfile.TemporaryDirectory() as temp:
                    root = Path(temp) / "h"
                    root.mkdir()
                    if body is not None:
                        (root / "harness.config.yaml").write_text(body, encoding="utf-8")
                    self.assertEqual("", U._harness_version(str(root)))

    def test_the_shipped_config_carries_a_version(self):
        self.assertTrue(U._harness_version(str(ROOT / "claude-harness")))


class PruneTests(unittest.TestCase):
    def _run(self, argv, local):
        with mock.patch.object(U.C, "harness_root", return_value=str(local)):
            with mock.patch("builtins.print"):
                return U.main(argv)

    def _pair(self, temp):
        upstream = _harness(Path(temp) / "up", {
            "harness.config.yaml": CONFIG,
            "HARNESS.md": "upstream",   # main() checks the root looks like a harness
            "KERNEL.md": "new spine",
            "kernel/identity.md": "new",
        })
        local = _harness(Path(temp) / "local", {
            "harness.config.yaml": CONFIG,
            "KERNEL.md": "old spine",
            "kernel/identity.md": "old",
            "kernel/local_only.md": "written by this deployment",
        })
        return upstream, local

    def test_apply_without_prune_keeps_local_files(self):
        with tempfile.TemporaryDirectory() as temp:
            upstream, local = self._pair(temp)
            self.assertEqual(0, self._run([str(upstream), "--apply"], local))

            self.assertEqual("new spine", (local / "KERNEL.md").read_text(encoding="utf-8"))
            # The old default mirrored exactly, so an upgrade could silently
            # delete a script a deployment had added.
            self.assertTrue((local / "kernel" / "local_only.md").exists())

    def test_prune_is_available_when_asked_for(self):
        with tempfile.TemporaryDirectory() as temp:
            upstream, local = self._pair(temp)
            self.assertEqual(0, self._run([str(upstream), "--apply", "--prune"], local))
            self.assertFalse((local / "kernel" / "local_only.md").exists())

    def test_a_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as temp:
            upstream, local = self._pair(temp)
            self.assertEqual(0, self._run([str(upstream)], local))
            self.assertEqual("old spine", (local / "KERNEL.md").read_text(encoding="utf-8"))
            self.assertTrue((local / "kernel" / "local_only.md").exists())

    def test_the_upstream_contract_wins(self):
        """A deployment whose config predates a new layer must still learn to
        sync it, so the contract is read from the side that knows."""
        with tempfile.TemporaryDirectory() as temp:
            upstream = _harness(Path(temp) / "up", {
                "harness.config.yaml": CONFIG.replace(
                    "    - modes\n", "    - modes\n    - scopes\n"),
                "HARNESS.md": "upstream",
                "KERNEL.md": "spine",
                "kernel/identity.md": "k",
                "scopes/math/AGENTS.md": "new layer",
            })
            local = _harness(Path(temp) / "local", {
                "harness.config.yaml": CONFIG,   # older: no scopes
                "KERNEL.md": "spine",
            })
            self.assertEqual(0, self._run([str(upstream), "--apply"], local))
            self.assertTrue((local / "scopes" / "math" / "AGENTS.md").exists())


if __name__ == "__main__":
    unittest.main()
