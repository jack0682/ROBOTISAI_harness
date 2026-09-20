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

"""Which worklog counts as "the session to resume".

`session_start` injects the latest one into the top of every session. For two
months it injected a worklog from 2026-07-11 whose closing line was
"Next action: commit (main) + push" — finished work presented as pending, in
every session, because the selection ranked by mtime and `git checkout` rewrites
mtimes. On a fresh clone a July file reads as minutes old.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
HOOKS = ROOT / "claude-harness" / "scripts" / "hooks"
SPEC = importlib.util.spec_from_file_location("_hooklib", HOOKS / "_hooklib.py")
assert SPEC and SPEC.loader
H = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(H)

DAY = 86400.0


class SessionAgeTests(unittest.TestCase):
    def test_the_filename_date_beats_a_rewritten_mtime(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "2026-07-11_harness-upgrade.md"
            path.write_text("x", encoding="utf-8")
            os.utime(path, None)  # fresh mtime, exactly as a checkout leaves it
            age = H.session_age_days(path=str(path),
                                     today=time.mktime((2026, 9, 10, 12, 0, 0, 0, 1, -1)))
        self.assertGreater(age, 55)

    def test_a_worklog_without_a_date_falls_back_to_mtime(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "CHECKPOINT-agents.md"
            path.write_text("x", encoding="utf-8")
            now = time.time()
            os.utime(path, (now - 3 * DAY, now - 3 * DAY))
            age = H.session_age_days(str(path), today=now)
        self.assertAlmostEqual(3.0, age, places=1)

    def test_a_malformed_date_does_not_raise(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "2026-99-99_broken.md"
            path.write_text("x", encoding="utf-8")
            self.assertIsInstance(H.session_age_days(str(path)), float)


class LatestSessionTests(unittest.TestCase):
    def _sessions(self, temp, names):
        active = Path(temp) / "sessions"
        active.mkdir(parents=True, exist_ok=True)
        for name in names:
            (active / name).write_text("x", encoding="utf-8")
        return active

    def _latest(self, temp, names, max_age="14"):
        active = self._sessions(temp, names)
        with (
            mock.patch.object(H, "sessions_dir", return_value=str(active)),
            mock.patch.dict(os.environ,
                            {"CLAUDE_HARNESS_SESSION_MAX_AGE_DAYS": max_age}),
        ):
            result = H.latest_session_file()
        return os.path.basename(result) if result else None

    def test_an_old_worklog_is_not_a_resume_target(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertIsNone(self._latest(temp, ["2026-07-11_finished.md"]))

    def test_a_recent_worklog_still_is(self):
        today = time.strftime("%Y-%m-%d")
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(f"{today}_current.md",
                             self._latest(temp, [f"{today}_current.md"]))

    def test_a_recent_one_wins_over_an_old_one(self):
        today = time.strftime("%Y-%m-%d")
        with tempfile.TemporaryDirectory() as temp:
            latest = self._latest(temp, ["2026-07-11_finished.md",
                                         f"{today}_current.md"])
        self.assertEqual(f"{today}_current.md", latest)

    def test_the_bound_can_be_lifted(self):
        """Someone resuming genuinely old work must be able to say so."""
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(
                "2026-07-11_finished.md",
                self._latest(temp, ["2026-07-11_finished.md"], max_age="0"))

    def test_scaffolding_is_never_a_resume_target(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertIsNone(
                self._latest(temp, ["README.md", "_session_template.md"]))


class PluginInstallTests(unittest.TestCase):
    """Two defects that only installing the plugin could surface.

    A plugin unpacks to `<cache>/<marketplace>/<plugin>/<version>/`, so the
    harness root's basename is a version string. Every gate message then named
    `0.4.0` as if it were a directory — "write a checkpoint in 0.4.0/sessions/"
    — and, worse, the writable state landed inside a directory that the next
    version replaces. The audit log is the store a settled claim cites and the
    input to per-skill contribution, which needs n ≥ 100 trials: resetting it on
    every update means it never reaches its own evidence bar.
    """

    def _as_plugin(self, root):
        return mock.patch.object(H, "harness_root", return_value=root)

    CACHE = ("/Users/x/.claude/plugins/cache/robotisai/robotisai-harness/0.4.2")

    def test_a_clone_is_not_a_plugin_install(self):
        with self._as_plugin("/Users/x/work/robotisai_harness/claude-harness"):
            self.assertIsNone(H._plugin_install())
            self.assertEqual("claude-harness", H.hdir_name())

    def test_a_clone_keeps_state_where_it_always_was(self):
        root = "/Users/x/work/robotisai_harness/claude-harness"
        with self._as_plugin(root), mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("HARNESS_STATE_DIR", None)
            self.assertEqual(root, H.state_root())

    def test_a_plugin_install_is_named_not_versioned(self):
        with self._as_plugin(self.CACHE):
            self.assertEqual("robotisai-harness", H.hdir_name())

    def test_plugin_state_escapes_the_version_directory(self):
        with self._as_plugin(self.CACHE), mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("HARNESS_STATE_DIR", None)
            state = H.state_root()
            self.assertNotIn("0.4.2", state)
            self.assertNotIn("/plugins/cache/", state)
            self.assertTrue(state.endswith("harness-state/robotisai/"
                                           "robotisai-harness"), state)

    def test_two_versions_of_one_plugin_share_state(self):
        """The property that makes telemetry accumulate at all."""
        base = "/Users/x/.claude/plugins/cache/m/p/"
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("HARNESS_STATE_DIR", None)
            with self._as_plugin(base + "0.4.2"):
                first = H.state_root()
            with self._as_plugin(base + "9.9.9"):
                second = H.state_root()
        self.assertEqual(first, second)

    def test_the_env_override_still_wins(self):
        with self._as_plugin(self.CACHE), \
             mock.patch.dict(os.environ, {"HARNESS_STATE_DIR": "/tmp/elsewhere"}):
            self.assertEqual("/tmp/elsewhere", H.state_root())


class AuditLogPathTests(unittest.TestCase):
    """The hooks run as subprocesses, so a test that drives one cannot mock the
    log path. Without the override the suite wrote its synthetic events into the
    real `sessions/.audit.log` -- the store claims are settled against, which on
    2026-09-10 was 86/150 test noise."""

    def test_it_defaults_to_the_harness_sessions_dir(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("HARNESS_AUDIT_LOG", None)
            self.assertEqual(os.path.join(H.sessions_dir(), ".audit.log"),
                             H.audit_log_path())

    def test_the_env_var_redirects_it(self):
        with tempfile.TemporaryDirectory() as temp:
            target = os.path.join(temp, "audit.log")
            with mock.patch.dict(os.environ, {"HARNESS_AUDIT_LOG": target}):
                self.assertEqual(target, H.audit_log_path())

    def test_a_redirected_write_does_not_touch_the_real_log(self):
        real = H.audit_log_path()
        before = os.path.getsize(real) if os.path.isfile(real) else 0
        with tempfile.TemporaryDirectory() as temp:
            target = os.path.join(temp, "audit.log")
            with mock.patch.dict(os.environ, {"HARNESS_AUDIT_LOG": target}):
                H.log_event("unit-test", "probe")
                self.assertTrue(os.path.isfile(target))
        after = os.path.getsize(real) if os.path.isfile(real) else 0
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
