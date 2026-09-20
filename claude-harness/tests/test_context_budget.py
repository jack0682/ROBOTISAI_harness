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

"""The always-on surface, measured rather than asserted.

Four documents budgeted it at the spine alone — `KERNEL.md` + `ROUTING.md`,
13 KB — while the real figure was four times that, and the largest component (69
skill frontmatters, pushed in by the `.claude/skills` symlink rather than pulled
on demand) was counted nowhere. A number nobody measures drifts until it is
decoration.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "claude-harness"

# Ceilings, not targets. They exist so a large addition to the always-on surface
# is a decision someone makes, rather than something that happens.
SPINE_MAX = 24_000
# Lowered when the descriptions were tightened: 33,484B of frontmatter became
# 24,293B by moving mechanism out of the always-on surface and into the bodies,
# with every trigger phrase preserved (evaluation/skill_triggers.py). Leaving the
# old ceiling would have let it grow straight back.
SKILL_FRONTMATTER_MAX = 28_000
TOTAL_MAX = 52_000


def _frontmatter_bytes(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return 0
    end = text.find("\n---", 3)
    return len(text[: end + 4].encode("utf-8")) if end > 0 else 0


class AlwaysOnSurfaceTests(unittest.TestCase):
    def spine_bytes(self):
        total = 0
        for path in (ROOT / "CLAUDE.md", HARNESS / "KERNEL.md", HARNESS / "ROUTING.md"):
            if path.exists():
                total += len(path.read_bytes())
        return total

    def skill_bytes(self):
        return sum(_frontmatter_bytes(p)
                   for p in (HARNESS / "skills").glob("*/SKILL.md"))

    def test_the_spine_stays_a_router(self):
        self.assertLess(self.spine_bytes(), SPINE_MAX)

    def test_skill_descriptions_stay_bounded(self):
        """They are 61% of what the model sees every session, and nothing else
        in the repository was watching them."""
        self.assertLess(self.skill_bytes(), SKILL_FRONTMATTER_MAX)

    def test_the_total_is_bounded(self):
        self.assertLess(self.spine_bytes() + self.skill_bytes(), TOTAL_MAX)

    def test_the_documented_figure_matches_the_measured_one(self):
        """`KERNEL.md` used to say the spine was the whole of it. If that claim
        comes back, this fails."""
        kernel = (HARNESS / "KERNEL.md").read_text(encoding="utf-8")
        self.assertNotIn(
            "are the only documents loaded into every session", kernel)
        self.assertIn("skill", kernel.lower().split("## identity")[0])

    def test_the_docs_quote_no_hardcoded_size(self):
        """Three files once gave three different sizes for the same surface —
        24 KB, 33 KB, and a measured 12.9 KB — which is principle 6 failing on
        the harness's own headline number. A figure copied into prose cannot
        stay true; the fix is that prose points at the measurement instead of
        repeating it."""
        pattern = re.compile(r"\d[\d,.]*\s*KB", re.I)
        for rel in ("KERNEL.md", "evaluation/skill_triggers.py"):
            text = (HARNESS / rel).read_text(encoding="utf-8")
            with self.subTest(file=rel):
                self.assertEqual([], pattern.findall(text))


def measure():
    case = AlwaysOnSurfaceTests("test_the_total_is_bounded")
    spine, skills = case.spine_bytes(), case.skill_bytes()
    print(f"always-on surface (measured now)\n"
          f"  spine   {spine:>7,}B  (ceiling {SPINE_MAX:,})\n"
          f"  skills  {skills:>7,}B  (ceiling {SKILL_FRONTMATTER_MAX:,})\n"
          f"  total   {spine + skills:>7,}B  (ceiling {TOTAL_MAX:,})"
          f"  ≈ {(spine + skills) // 4:,} tokens")
    return 0


if __name__ == "__main__":
    if "--measure" in sys.argv:
        raise SystemExit(measure())
    unittest.main()
