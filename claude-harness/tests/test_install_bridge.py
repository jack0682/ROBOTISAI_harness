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

"""The bridge installer had no tests, and two of its bugs were silent.

It truncated CLAUDE.md, deleting 68 lines of co-work governance another tool
owns, while its docstring called re-running idempotent. And it appended its hook
entries, so every run reordered .claude/settings.json and the co-work installer
reordered it back -- a file that oscillates is a file every deployment reports
as dirty, and a dirty deployment cannot be updated by `git pull`.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "claude-harness" / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location(
    "install_bridge", SCRIPTS / "install_bridge.py")
assert SPEC and SPEC.loader
B = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(B)


def _hook(path):
    return {"matcher": "Edit|Bash",
            "hooks": [{"type": "command",
                       "command": f'python3 "$CLAUDE_PROJECT_DIR/{path}"'}]}


class ForeignRegionTests(unittest.TestCase):
    def test_a_marked_region_survives_regeneration(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "CLAUDE.md"
            path.write_text(
                "<!-- COWORK:BEGIN -->\n# CO-WORK\nrules\n<!-- COWORK:END -->\n\n"
                "# old bridge body\n",
                encoding="utf-8",
            )
            B._write(str(path), "# new bridge body\n", keep_foreign_regions=True)
            text = path.read_text(encoding="utf-8")

        self.assertIn("<!-- COWORK:BEGIN -->", text)
        self.assertIn("rules", text)
        self.assertIn("# new bridge body", text)
        self.assertNotIn("# old bridge body", text)
        self.assertTrue(text.startswith("<!-- COWORK:BEGIN -->"))

    def test_regeneration_without_a_region_is_a_plain_write(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "CLAUDE.md"
            path.write_text("# old\n", encoding="utf-8")
            B._write(str(path), "# new\n", keep_foreign_regions=True)
            self.assertEqual("# new\n", path.read_text(encoding="utf-8"))

    def test_a_region_is_not_duplicated_when_content_already_carries_one(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "CLAUDE.md"
            path.write_text("<!-- X:BEGIN -->\na\n<!-- X:END -->\nold\n",
                            encoding="utf-8")
            B._write(str(path), "<!-- X:BEGIN -->\nb\n<!-- X:END -->\nnew\n",
                     keep_foreign_regions=True)
            text = path.read_text(encoding="utf-8")
        self.assertEqual(1, text.count("<!-- X:BEGIN -->"))
        self.assertIn("b", text)


class HookMergeTests(unittest.TestCase):
    def setUp(self):
        self.root = str(ROOT)

    def test_our_entry_is_replaced_where_it_already_sits(self):
        existing = [
            _hook("claude-harness/scripts/hooks/kernel_guard.py"),
            _hook("cowork/hooks/cowork_guard.py"),
        ]
        desired = [_hook("claude-harness/scripts/hooks/kernel_guard.py")]

        merged = B._merge_hook_entries(existing, desired, self.root,
                                       "claude-harness")

        self.assertEqual(2, len(merged))
        # Position, not just presence: appending is what made the file oscillate.
        self.assertIn("kernel_guard.py", json.dumps(merged[0]))
        self.assertIn("cowork_guard.py", json.dumps(merged[1]))

    def test_a_new_entry_is_appended(self):
        existing = [_hook("cowork/hooks/cowork_guard.py")]
        desired = [_hook("claude-harness/scripts/hooks/kernel_guard.py")]

        merged = B._merge_hook_entries(existing, desired, self.root,
                                       "claude-harness")

        self.assertIn("cowork_guard.py", json.dumps(merged[0]))
        self.assertIn("kernel_guard.py", json.dumps(merged[1]))

    def test_a_sibling_harness_keeps_its_hooks(self):
        """The old test was the bare substring `/scripts/hooks/`, which a
        claude-harness install would have used to delete a sibling harness's.

        The sibling is built here instead of assumed in the repo. This harness
        ships standalone, and the invariant -- a package that is present on
        disk is somebody else's -- does not depend on which one it is.
        """
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "sibling-harness" / "scripts" / "hooks").mkdir(
                parents=True)
            sibling = _hook("sibling-harness/scripts/hooks/kernel_guard.py")
            merged = B._merge_hook_entries([sibling], [], tmp, "claude-harness")
            self.assertEqual([sibling], merged)

    def test_an_entry_pointing_at_a_vanished_harness_is_dropped(self):
        stale = _hook("renamed-harness/scripts/hooks/stop_gate.py")
        self.assertFalse((ROOT / "renamed-harness").exists())
        merged = B._merge_hook_entries([stale], [], self.root, "claude-harness")
        self.assertEqual([], merged)

    def test_merging_is_stable_under_repetition(self):
        existing = [
            _hook("claude-harness/scripts/hooks/kernel_guard.py"),
            _hook("cowork/hooks/cowork_guard.py"),
        ]
        desired = [_hook("claude-harness/scripts/hooks/kernel_guard.py")]

        once = B._merge_hook_entries(existing, desired, self.root, "claude-harness")
        twice = B._merge_hook_entries(once, desired, self.root, "claude-harness")

        self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()
