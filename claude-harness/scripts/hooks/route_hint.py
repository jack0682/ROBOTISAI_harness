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

"""UserPromptSubmit hook — routing hint (closes the on-demand-loading gap).

The harness's depth — scopes/<domain>/AGENTS.md and modes/<op>.md — only helps if
it actually gets loaded. ROUTING.md makes loading an obligation, but nothing
surfaces WHICH depth a given request needs, so the model can silently answer from
the spine alone and the careful scope/mode content stays dead. This hook does a
lightweight keyword classification of the user's prompt and injects a compact
pointer to the scope + modes to load — turning "the model might open the right
file" into "the pointer is already on the table."

It is a SOFT hint (says 'ignore if off-base'), never blocks, never decides the
route (the model still judges — see evaluation/{trigger,near_miss}_tests). It is
conservative by design: silent when there is no clear signal, because a false
silence (fall back to ROUTING.md) is cheaper than a noisy false fire. Fail-open and
self-logged, so its fire rate is visible in sessions/.audit.log.
"""

from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _hooklib as H

# (scope, keyword pattern, modes to load, key skills). Order = tie-break priority.
ROUTES = [
    ("math",
     r"증명|\bproof\b|\btheorem\b|\blemma\b|보조정리|정의역|부등식|수렴성?|식별[성가]"
     r"|identifiab|형식화|formaliz|정리를?\s*증명|수식이?.{0,15}(뒷받침|성립|검증|맞는|증명)",
     "define, math_lock, counter", "proof-checker / proof-writer / kill-argument"),
    ("research",
     r"선행\s*연구|관련\s*연구|related\s*work|prior[\s-]*art|문헌|literature|서베이|survey"
     r"|novelty|신규성|이\s*분야|이미\s*있는|논문.{0,6}찾|查新|査新",
     "research", "research-lit / novelty-check"),
    ("writing",
     r"리뷰어|초록|abstract|인용|참고문헌|citation|rebuttal|원고|manuscript"
     r"|논문.{0,10}(리뷰|써|작성|교정|검토|숫자|수치|맞는지|대조)",
     "paper, verify", "paper-claim-audit / citation-audit"),
    ("experiments",
     r"실험|experiment|ablation|어블레이션|벤치마크|benchmark|데이터\s*분석|training"
     r"|GPU|결과.{0,6}(분석|판정|해석|대조)|지표|\bmetric",
     "execute, counter, verify", "experiment-plan / result-to-claim"),
    ("coding",
     r"코드|코딩|구현|implement|버그|\bbug\b|디버그|debug|refactor|리팩터|스크립트"
     r"|컴파일|compile|에러\s*로그|함수.{0,6}(이름|추출|리팩)",
     "execute, audit", "protocols/coding + debugging"),
    ("control",
     r"진동|oscillat|불안정|instab|안정성|stability|폐루프|closed[\s-]*loop|피드백|feedback"
     r"|passiv|수동성|게인|\bgain\b|임피던스|impedance|제어기|controller|루프.{0,6}(안정|발산|튀)"
     r"|샘플링|sampling|지연.{0,6}(보상|영향)|latency|리밋\s*사이클|limit\s*cycle"
     r"|힘\s*추정|토크\s*추정|추정.{0,10}(튀|맞지|안\s*맞|드리프트)|force\s*estimat",
     "math_lock, counter", "protocols/debugging + scopes/control"),
    ("prompts",
     r"에이전트|\bagent\b|서브에이전트|subagent|프롬프트로|프롬프트\s*(써|만들|작성)"
     r"|위임|시킬\s*프롬프트",
     "prompt", "mcp-builder"),
]


def main():
    data = H.read_input()
    session_id = data.get("session_id", "")
    prompt = (data.get("prompt") or "")[:2000]
    if not prompt.strip():
        return 0

    hits = [(scope, modes, skills) for scope, pat, modes, skills in ROUTES
            if re.search(pat, prompt, re.I)]
    H.log_event(session_id, "route_hint",
                scopes=[h[0] for h in hits] or None)
    if not hits:
        return 0

    hits = hits[:2]  # cap: >2 matches is noise, not a signal
    out = [f"[{H.hdir_name()}] Routing hint (soft — ignore if off-base). Per "
           "ROUTING.md, load the depth before non-trivial work; don't operate "
           "from the spine alone:"]
    for scope, modes, skills in hits:
        out.append(f"  · {scope} → scopes/{scope}/AGENTS.md + modes/{{{modes}}}"
                   f"  (skills: {skills})")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(H.safe(main))
