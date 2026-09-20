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

"""The audit log had a reader that nothing read.

`audit_session.py` was written as the compliance report and then wired to
nothing — not a hook, not a command. The cost of that showed up on 2026-09-20:
the log had been 86/150 test noise with zero `stop_block` entries, and the
harness's only settled claim was citing it. A report no one runs is the same as
no report.

These tests pin the library half of it, and specifically the two places where it
is supposed to *refuse* to answer: per-skill contribution below the evidence bar,
and router engagement on a sample too thin to mean anything.
"""

from __future__ import annotations

import importlib.util
import io
import contextlib
from pathlib import Path
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "claude-harness" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "hooks"))
SPEC = importlib.util.spec_from_file_location(
    "audit_session", SCRIPTS / "audit_session.py")
assert SPEC and SPEC.loader
A = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)

VSPEC = importlib.util.spec_from_file_location(
    "validate_harness", SCRIPTS / "validate_harness.py")
assert VSPEC and VSPEC.loader
V = importlib.util.module_from_spec(VSPEC)
VSPEC.loader.exec_module(V)


def _outcome(skills, verdict):
    return {"ts": 1.0, "session_id": "s", "event": "session_outcome",
            "detail": {"skills": list(skills), "verdict": verdict}}


class LibraryStatsTests(unittest.TestCase):
    def test_trials_and_contribution_are_counted_per_skill(self):
        entries = [_outcome(["a"], "pass"), _outcome(["a"], "pass"),
                   _outcome(["a", "b"], "blocked")]
        stats = A.library_stats(entries)
        self.assertEqual(3, stats["skills"]["a"]["trials"])
        self.assertEqual(2, stats["skills"]["a"]["pass"])
        self.assertEqual(1, stats["skills"]["a"]["blocked"])
        self.assertAlmostEqual(1 / 3, stats["skills"]["a"]["contribution"])
        self.assertAlmostEqual(-1.0, stats["skills"]["b"]["contribution"])

    def test_engagement_counts_sessions_where_no_skill_fired(self):
        """The denominator is evaluated sessions, not sessions that used a
        skill — otherwise a library nobody reaches for scores 100%."""
        entries = [_outcome(["a"], "pass"), _outcome([], "pass"),
                   _outcome([], "blocked"), _outcome(["a"], "pass")]
        stats = A.library_stats(entries)
        self.assertEqual(4, stats["evaluated"])
        self.assertEqual(2, stats["engaged"])
        self.assertAlmostEqual(0.5, stats["engagement"])

    def test_no_outcomes_means_no_engagement_number(self):
        stats = A.library_stats([])
        self.assertIsNone(stats["engagement"])
        self.assertEqual({}, stats["skills"])

    def test_a_thin_sample_is_marked_insufficient(self):
        stats = A.library_stats([_outcome(["a"], "pass")])
        self.assertFalse(stats["skills"]["a"]["sufficient"])

    def test_the_bar_is_the_measured_one(self):
        entries = [_outcome(["a"], "pass") for _ in range(A.N_MIN)]
        self.assertTrue(A.library_stats(entries)["skills"]["a"]["sufficient"])


class LibraryReportTests(unittest.TestCase):
    def _report(self, entries):
        buffer = io.StringIO()
        with (mock.patch.object(A.H, "read_audit", return_value=entries),
              contextlib.redirect_stdout(buffer)):
            A.library_report()
        return buffer.getvalue()

    def test_it_withholds_the_verdict_below_the_bar(self):
        out = self._report([_outcome(["a"], "pass")])
        self.assertIn("no verdict", out)
        self.assertIn(str(A.N_MIN), out)

    def test_it_prints_a_verdict_once_the_bar_is_met(self):
        out = self._report([_outcome(["a"], "pass") for _ in range(A.N_MIN)])
        self.assertIn("+1.00", out)

    def test_it_says_so_when_there_is_no_data(self):
        out = self._report([])
        self.assertIn("No session outcomes recorded yet", out)

    def test_it_lists_skills_with_no_trigger(self):
        """The live library: this is a structural finding, available now."""
        out = self._report([])
        self.assertTrue(
            "no recorded trigger" in out or "at least one recorded trigger" in out,
            out)


class UserInvokedOnlyTests(unittest.TestCase):
    """A skill that opts out of model invocation needs no trigger phrase.

    It is invisible to the router until the user types its name, so it cannot
    shadow anything — flagging it as a trigger gap would penalise the very fix
    for over-triggering. `skill-creator` is the live case: a near-miss test
    records it firing on "just list the skills", which is not authoring one.
    """

    def test_it_detects_the_opt_out(self):
        self.assertTrue(A._user_invoked_only("skill-creator"))
        self.assertTrue(A._user_invoked_only("file-organizer"))

    def test_an_ordinary_skill_is_not_opted_out(self):
        self.assertFalse(A._user_invoked_only("arxiv"))

    def test_a_missing_skill_is_not_opted_out(self):
        self.assertFalse(A._user_invoked_only("no-such-skill"))

    def test_the_live_library_has_no_trigger_gaps(self):
        """The whole point of the 2026-09-20 pass, checked against the real
        library rather than a fixture."""
        self.assertEqual([], A._untriggered_skills())


class EngagementWarningTests(unittest.TestCase):
    """Silence on a thin sample is the point, not an oversight."""

    def _warnings(self, entries):
        with mock.patch.object(A.H, "read_audit", return_value=entries), \
             mock.patch.dict(sys.modules, {"audit_session": A}):
            return V._check_router_engagement()

    def test_it_stays_silent_with_no_data(self):
        self.assertEqual([], self._warnings([]))

    def test_it_stays_silent_on_a_sample_too_small_to_mean_anything(self):
        entries = [_outcome([], "pass") for _ in range(5)]
        self.assertEqual([], self._warnings(entries))

    def test_it_warns_when_engagement_is_low_over_enough_sessions(self):
        entries = ([_outcome([], "pass") for _ in range(25)]
                   + [_outcome(["a"], "pass") for _ in range(5)])
        warnings = self._warnings(entries)
        self.assertEqual(1, len(warnings), warnings)
        self.assertIn("router engagement", warnings[0])

    def test_a_healthy_library_produces_no_warning(self):
        entries = ([_outcome(["a"], "pass") for _ in range(25)]
                   + [_outcome([], "pass") for _ in range(5)])
        self.assertEqual([], self._warnings(entries))


if __name__ == "__main__":
    unittest.main()
