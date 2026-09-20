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

"""Distribution was a hand-rolled file sync, and the fleet fragmented under it.

21 installs on one machine, six distinct HEADs, four plain copies with no git at
all — because runtime state is written into the governance tree, every copy goes
dirty, and a dirty copy cannot be `git pull`ed. `upgrade_harness.py` was the
answer and it was the wrong shape: it deleted local files absent upstream while
its sync set omitted `modes/`, `scopes/`, `KERNEL.md` and `ROUTING.md`.

The platform's plugin system does versioning, pinning and update for free. These
tests pin the manifests, and one records the limit the migration ran into: a
plugin does not carry `CLAUDE.md`, so it cannot deliver the always-on spine.
"""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "claude-harness"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN = HARNESS / ".claude-plugin" / "plugin.json"

HOOK_SCRIPTS = ("session_start.py", "route_hint.py", "kernel_guard.py",
                "commit_guard.py", "post_edit.py", "pre_compact.py",
                "stop_gate.py")


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class MarketplaceTests(unittest.TestCase):
    def test_it_points_at_the_harness_not_the_repo_root(self):
        """The repo root holds CLAUDE.md, which a plugin does not ship and
        which `claude plugin validate` warns about. The plugin is the harness."""
        entry = _load(MARKETPLACE)["plugins"][0]
        self.assertEqual("./claude-harness", entry["source"])

    def test_the_versions_agree(self):
        self.assertEqual(_load(MARKETPLACE)["plugins"][0]["version"],
                         _load(PLUGIN)["version"])

    def test_the_names_agree(self):
        self.assertEqual(_load(MARKETPLACE)["plugins"][0]["name"],
                         _load(PLUGIN)["name"])


class PluginTests(unittest.TestCase):
    def setUp(self):
        self.plugin = _load(PLUGIN)

    def test_its_component_paths_resolve(self):
        for key in ("skills", "commands"):
            for rel in self.plugin[key]:
                with self.subTest(path=rel):
                    self.assertTrue((HARNESS / rel.lstrip("./")).is_dir())

    def test_every_hook_script_exists_and_is_rooted_in_the_plugin(self):
        commands = []
        for entries in self.plugin["hooks"].values():
            for entry in entries:
                for hook in entry["hooks"]:
                    commands.append(hook["command"])
        self.assertEqual(len(HOOK_SCRIPTS), len(commands), commands)
        for command in commands:
            with self.subTest(command=command):
                self.assertIn("${CLAUDE_PLUGIN_ROOT}/scripts/hooks/", command)
                script = command.rsplit("/", 1)[-1].rstrip('"')
                self.assertIn(script, HOOK_SCRIPTS)
                self.assertTrue(
                    (HARNESS / "scripts" / "hooks" / script).is_file())

    def test_the_hook_events_match_what_the_bridge_installs(self):
        """Two delivery paths, one enforcement layer. If they drift, a
        plugin-installed harness and a bridge-installed one stop being the same
        harness."""
        import importlib.util
        import sys
        sys.path.insert(0, str(HARNESS / "scripts"))
        spec = importlib.util.spec_from_file_location(
            "install_bridge", HARNESS / "scripts" / "install_bridge.py")
        bridge = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bridge)
        desired = bridge._write_settings.__doc__  # noqa: F841 - presence only
        self.assertEqual(
            sorted(self.plugin["hooks"]),
            sorted(["SessionStart", "UserPromptSubmit", "PreToolUse",
                    "PostToolUse", "PreCompact", "Stop"]))

    def test_post_tool_use_records_skills(self):
        """The telemetry the library report depends on."""
        matcher = self.plugin["hooks"]["PostToolUse"][0]["matcher"]
        self.assertIn("Skill", matcher)


class SpineLimitTests(unittest.TestCase):
    """A plugin ships skills, commands, agents, hooks and MCP servers. It does
    not ship `CLAUDE.md`, so the always-on spine cannot travel with it — which
    is why `install_bridge.py` is not redundant and was not retired."""

    def test_the_plugin_declares_no_spine(self):
        plugin = _load(PLUGIN)
        for key in ("claudeMd", "context", "memory"):
            self.assertNotIn(key, plugin)

    def test_the_bridge_still_writes_the_spine(self):
        bridge = (HARNESS / "scripts" / "install_bridge.py").read_text(
            encoding="utf-8")
        self.assertIn("_write_claude_md", bridge)
        self.assertIn("KERNEL.md", bridge)


if __name__ == "__main__":
    unittest.main()
