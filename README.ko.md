<div align="center">

# ROBOTIS AI Harness

**로보티즈 AI 팀 전용 Claude Code 거버넌스 레이어**

코딩 스타일 · 커밋 규칙 · 작업 방법론을 *권장*이 아니라 *강제*로 만듭니다.

[![License](https://img.shields.io/badge/license-Apache_2.0-D22128?logo=apache&logoColor=white)](LICENSE)
[![ROBOTIS AI](https://img.shields.io/badge/ROBOTIS-AI_Team-0B5FFF?logo=probot&logoColor=white)](https://www.robotis.com)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-D97757?logo=claude&logoColor=white)](https://claude.com/claude-code)
[![ROS 2](https://img.shields.io/badge/ROS_2-compliant-22314E?logo=ros&logoColor=white)](claude-harness/skills/robotis-style/references/ros.md)

[![C++](https://img.shields.io/badge/C%2B%2B-Rev_35-00599C?logo=cplusplus&logoColor=white)](claude-harness/skills/robotis-style/references/cpp.md)
[![C](https://img.shields.io/badge/C-Rev_18-A8B9CC?logo=c&logoColor=white)](claude-harness/skills/robotis-style/references/c.md)
[![Python](https://img.shields.io/badge/Python-Rev_18-3776AB?logo=python&logoColor=white)](claude-harness/skills/robotis-style/references/python.md)
[![JS / TS](https://img.shields.io/badge/JS_%2F_TS-Rev_9-F7DF1E?logo=javascript&logoColor=black)](claude-harness/skills/robotis-style/references/javascript.md)

[![Skills](https://img.shields.io/badge/skills-72-6E56CF?logo=claude&logoColor=white)](claude-harness/skills/INDEX.md)
[![Hooks](https://img.shields.io/badge/hooks-7_enforcing-1A7F37?logo=githubactions&logoColor=white)](claude-harness/scripts/hooks/)
[![Tests](https://img.shields.io/badge/tests-156_passing-1A7F37?logo=pytest&logoColor=white)](claude-harness/tests/)
[![Commits](https://img.shields.io/badge/commits-GPG_%2B_DCO-1A7F37?logo=gnuprivacyguard&logoColor=white)](claude-harness/protocols/commit_policy.md)

[English](README.md) · **한국어**

[시작하기](#2-5분-안에-시작하기) ·
[스킬 목록](#5-쓸-수-있는-스킬들) ·
[강제되는 규칙](#6-무엇이-강제되나요) ·
[문제 해결](#8-자주-막히는-것들)

</div>

---

각자의 작업 폴더에 한 번 넣어두면, 그 폴더에서 Claude를 열 때마다 규칙이 자동으로
적용됩니다. **외울 명령어는 `/harness` 하나**입니다.

---

## 1. 왜 쓰나 — 그냥 Claude Code 쓰는 것과 뭐가 다른가

Claude Code는 이미 충분히 좋습니다. 문제는 **팀이 여럿일 때** 생깁니다. 사람마다
프롬프트가 다르고, 스타일 가이드는 매번 붙여넣어야 하고, 규칙은 잊으면 그만입니다.

| | 그냥 Claude Code | 이 하네스 |
|---|---|---|
| **스타일 가이드** | 매 세션 직접 붙여넣거나, 안 붙이면 무시됨 | 소스 파일을 **여는 순간** 자동 로드 |
| **규칙 위반** | 리뷰에서 뒤늦게 지적 | 파일 저장·커밋 시점에 **차단** |
| **"테스트 통과했습니다"** | 안 돌려보고 말할 수 있음 | 돌린 것만 주장 가능 — 안 돌리면 stop gate가 막음 |
| **세션이 끊기면** | 다음 세션에 처음부터 다시 설명 | 워크로그를 자동으로 이어받음 |
| **긴 작업 중단** | 아무것도 안 남고 끝남 | 체크포인트 없이 **세션을 끝낼 수 없음** |
| **커밋 품질** | 사람마다 제각각 | Sign-off + GPG + 헤더 + 제목 규칙 자동 검사 |
| **AI 공동저자 표기** | 도구가 자동으로 붙임 | **차단됨** (도구는 저자가 아님) |
| **반복 작업** | 매번 프롬프트 새로 작성 | 상황에 맞는 **스킬 72개**가 자동 선택 |
| **팀 일관성** | 각자 다른 방식 | 전원 동일한 규칙 |

### 구체적으로 뭐가 달라지나

**① 스타일을 "기억"할 필요가 없습니다**
`laser_distance_sensor.cpp` 를 여는 순간 C++ 규칙(들여쓰기 2칸, 100자, 큰따옴표,
중괄호 위치, 멤버 변수 뒤 밑줄…)이 로드됩니다. 물어보지 않아도 적용됩니다.

**② "된 것 같다"와 "됐다"를 구분합니다**
하네스의 첫 번째 원칙은 *동의는 검증이 아니다* 입니다. 안 돌려본 테스트를
"통과했다"고 말할 수 없고, 근거 없는 주장은 근거 없다고 표시됩니다.

**③ 실수로 규칙을 빠뜨릴 수 없습니다**
훅 7개가 실제로 차단합니다. 서명 없는 커밋, AI 공동저자, 라이선스 헤더 누락,
체크포인트 없는 긴 작업 — 전부 막힙니다. 우회(`--no-verify`)도 막힙니다.

**④ 어제 하던 일을 오늘 이어받습니다**
`/harness` 를 다시 치면 지난 세션이 어디까지 했는지, 뭐가 커밋 안 됐는지, 다음 할
일이 뭐라고 적혀 있는지 정리해서 보여줍니다.

> 정직하게: **작은 일회성 작업에는 과합니다.** 스크립트 하나 뚝딱 만들 거면 그냥
> Claude Code 쓰세요. 이건 *여러 세션에 걸친 작업*과 *여러 사람이 만지는 코드*를
> 위한 것입니다.

---

## 2. 5분 안에 시작하기

### 1단계 — 받기

작업 폴더가 아니라 **아무 임시 위치**에 받습니다. 여기서 바로 쓰는 게 아니라, 내
작업 폴더로 넣어주는 설치 도구이기 때문입니다.

```sh
git clone git@github.com:jack0682/ROBOTISAI_harness.git /tmp/harness
```

### 2단계 — 내 작업 폴더에 넣기

`~/my_project` 자리에 **실제 작업이 들어있는 폴더** 경로를 씁니다.

```sh
/tmp/harness/bootstrap.sh ~/my_project --fresh
```

이 한 줄이 하는 일:

- 하네스를 작업 폴더에 복사
- Claude가 자동으로 읽는 `CLAUDE.md` 와 `.claude/` 생성
- 커밋 검사 장치 설치
- **템플릿 저장소와의 git 연결 끊기** — 사본은 어차피 업스트림에 푸시할 수 없으니,
  남겨두면 시도했다가 실패하는 데 시간만 씁니다
- 설치가 제대로 됐는지 검사하고 결과 출력

> ⚠️ `--fresh` 는 **처음 설치할 때만** 씁니다. 나중에 업데이트할 때 붙이면 그동안
> 쌓인 작업 기록이 초기화됩니다.

### 3단계 — Claude 열고 `/harness`

```sh
cd ~/my_project
claude
```

그리고 그냥 이렇게 칩니다:

```
/harness
```

끝입니다. 이후는 `/harness` 가 알아서 묻고 진행합니다.

---

## 3. `/harness` 가 실제로 하는 일

**상황을 스스로 판단합니다.** 같은 명령어인데 처음 칠 때와 나중에 칠 때 하는 일이
다릅니다.

### 처음 칠 때 — 설치 직후

**① 서명 정보 설정** — 이게 제일 먼저인 이유는, 이게 없으면 **커밋이 아예 안 되기
때문**입니다. 하루 종일 작업하고 마지막에 막히는 걸 막으려고 맨 앞에 둡니다.
이름·이메일·GPG 키를 물어봅니다. GPG 키가 없으면 만드는 것부터 같이 합니다.

**② 작업 폴더 분석** — 이게 무슨 프로젝트인지, 어떤 언어를 쓰는지, 빌드와 테스트는
어떻게 돌리는지, 기존 규칙이 뭔지를 직접 읽습니다. 사람에게 묻지 않고 코드를 봅니다.

**③ 뭘 하고 싶은지 묻기** — 코드를 읽으면 "이게 무엇인지" 는 알 수 있지만 "무엇을
위한 것인지" 는 알 수 없습니다. 네 가지만 묻습니다.

- **목표** — 끝났을 때 무엇이 참이어야 하나요
- **범위** — 이번 작업에 뭐가 들어가고, 뭐가 **안** 들어가나요
- **완료 기준** — 뭘 돌려보거나 확인해서 됐다고 판단하나요
- **제약** — 못 구하는 장비, 마감, 건드리면 안 되는 인터페이스

답은 프로젝트 문서에 기록되고, 이후 모든 세션이 그걸 읽습니다.

### 다음 날 다시 칠 때 — 이어서 작업

**설치 과정을 반복하지 않습니다.** 대신 이걸 정리해서 보여주고 바로 이어갑니다.

- 지난 세션이 어디까지 했는지
- 커밋 안 된 변경, 푸시 안 된 커밋이 있는지
- 지금 할 수 있는 작업과 막혀 있는 작업
- 지난 세션이 적어둔 "다음 할 일"

### 뭔가 이상할 때

```
/harness check
```

설치가 실제로 작동하는지 전부 점검합니다. **"파일이 있다" 가 아니라 "검사가 실제로
막는가" 까지 확인합니다** — 겉보기엔 멀쩡한데 아무것도 막지 않는 상태가 제일
위험하기 때문입니다.

---

## 4. 알아야 할 명령어는 두 개

| 명령어 | 언제 |
|---|---|
| **`/harness`** | 처음 설치할 때 · 새 세션 시작할 때 · 뭔가 이상할 때 (`/harness check`) |
| **`/harness-checkpoint`** | 작업이 길어질 때 중간 저장. 세션이 끊겨도 다음에 이어서 |

나머지 두 개(`/harness-init`, `/harness-load`)는 `/harness` 가 내부적으로 부르는
것들이라 직접 칠 일은 거의 없습니다.

그 외에는 **그냥 평소처럼 말하면 됩니다** — 한국어든 영어든. "이 함수 버그 좀
찾아줘", "이 부분 리팩터링 해줘". 하네스가 알아서 맞는 규칙과 스킬을 불러옵니다.

---

## 5. 쓸 수 있는 스킬들

**스킬 72개**가 들어있습니다. 직접 부를 필요는 없습니다 — 요청 내용을 보고 맞는 걸
자동으로 가져옵니다. 다만 **뭐가 가능한지 알아야 시킬 수 있으므로** 정리합니다.

전체 목록: [`claude-harness/skills/INDEX.md`](claude-harness/skills/INDEX.md)
· ▶ 표시는 다른 스킬들을 엮어서 돌리는 **오케스트레이터**입니다.

### 🪶 코딩 — 단순함

[DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) 에서
가져왔습니다(MIT). 뭘 가져오고 뭘 일부러 뺐는지:
[`skills/ponytail/UPSTREAM.md`](claude-harness/skills/ponytail/UPSTREAM.md).

| 스킬 | 하는 일 |
|---|---|
| `ponytail` | 실제로 작동하는 가장 게으른 해법 — YAGNI → 재사용 → 표준 라이브러리 → 네이티브 → 한 줄 → 최소. `lite` / `full` / `ultra` 단계 |
| `ponytail-review` | **diff**를 과설계 관점으로만 리뷰 — 뭘 지울지 |
| `ponytail-audit` | 같은 걸 **저장소 전체**에 대해, 순위를 매겨서 |
| `ponytail-debt` | 코드에 남은 `ponytail:` 단축 주석을 부채 장부로 수확 |

> 하네스와 겹치지 않고 보완합니다: **하네스는 주장이 입증됐는지를, ponytail은
> 그 코드가 존재해야 하는지를 판단합니다.**

### 🔧 코딩 — 필수 적용

| 스킬 | 하는 일 |
|---|---|
| **`robotis-style`** | **ROBOTIS 프로그래밍 스타일 가이드.** C++(Rev 35) · C(Rev 18) · Python(Rev 18) · ROS(Rev 10) · JavaScript(Rev 9) + Apache 라이선스 헤더. **소스 파일을 열면 자동 로드** |

> 이것만은 선택이 아닙니다. 나머지 스킬은 필요할 때만 불립니다.

### 🤖 에이전트 · 도구 만들기

| 스킬 | 하는 일 |
|---|---|
| `mcp-builder` | MCP 서버 제작 (Python FastMCP / Node TypeScript). 외부 API를 LLM 도구로 노출 |
| `agent-browser` | 브라우저 자동화 — 페이지 열기, 폼 입력, 스크린샷, 데이터 추출, 웹앱 테스트 |
| `skill-creator` | 새 스킬 제작·개선, 성능 측정 |
| `meta-optimize` ▶ / `meta-apply` | 사용 기록을 분석해 스킬 자체를 개선 (교차 모델 심사 + 사람 승인 후 반영) |
| `file-organizer` | 파일 정리 |

### 🧪 실험 — 계획부터 주장까지

| 스킬 | 하는 일 |
|---|---|
| `experiment-plan` | 연구 제안 → 청구 기반 실험 로드맵 (ablation 행렬, 평가 프로토콜, 컴퓨트 예산) |
| `experiment-bridge` ▶ | 계획을 실제 코드로 — 구현, GPU 배포, 첫 결과 수집 |
| `experiment-queue` | 다중 시드·다중 설정 SSH 작업 큐 (OOM 재시도 포함) |
| `run-experiment` ▶ | 실험 실행 진입점 — 대상 선택 후 제공자 스킬로 전달 |
| `monitor-experiment` | 진행 상황 확인, 결과 수집 |
| `training-check` | WandB 지표 감시 — NaN, loss 발산, 유휴 GPU. **망가진 학습이 GPU 시간을 태우기 전에** |
| `analyze-results` | 통계 계산, 비교 표, 해석 |
| `csv-data-summarizer` | CSV 기술통계 + 빠른 시각화 |
| `system-profile` | 스크립트·프로세스·GPU·메모리·인터커넥트 프로파일링, 병목 보고 |
| `experiment-audit` | **실험 무결성 감사** — 가짜 ground truth, 점수 정규화, 유령 결과, 불충분한 범위 |
| `ablation-planner` | 리뷰어 관점에서 ablation 설계 |
| `result-to-claim` | 이 결과가 **실제로 뒷받침하는 것**과 아닌 것을 판정 |

**컴퓨트 백엔드:** `vast-gpu`(GPU 임대) · `serverless-modal`(Modal) · `qzcli`(启智) ·
`hugging-face-cli` · `hugging-face-datasets`

### 📐 이론 · 수학

| 스킬 | 하는 일 |
|---|---|
| `proof-writer` | ML/AI 이론 증명 작성 — 정리·보조정리, 빠진 단계 보완 |
| `proof-checker` | 증명 검증, 교차 모델로 허점 찾기, 수정 후 재검토 |
| `formula-derivation` | 흩어진 수식을 논문용 유도 과정으로 정리 |
| `kill-argument` | **적대적 리뷰** — 가장 강한 반박문을 쓰고, 다시 방어하고, 남은 쟁점을 드러냄 |
| `relentless-theory-loop` ▶ | 세션을 넘나드는 지속적 이론 구축 (반론, 경쟁 가설, 추가 전용 노트) |

### 📚 연구 · 문헌

| 스킬 | 하는 일 |
|---|---|
| `research-lit` | 논문 검색·분석, 관련 연구 정리 |
| `novelty-check` | **查新** — 최근 문헌 대조로 아이디어 신규성 검증 |
| `idea-creator` / `idea-discovery` ▶ | 연구 방향 → 아이디어 생성·순위 / 전체 발굴 파이프라인 |
| `idea-discovery-robot` ▶ | 로보틱스·임베디드 AI 특화 (벤치마크 기반, 시뮬레이션 우선) |
| `research-refine` | 모호한 방향 → 문제 고정된 실행 가능 계획 |
| `research-review` | 외부 리뷰어 백엔드로 비판적 리뷰 받기 |
| `research-wiki` / `wiki-enrich` | 논문·아이디어·실험·주장 누적 지식베이스 |
| `find-skills` | "이런 거 하는 스킬 있나?" |

**검색 백엔드:** `arxiv`(프리프린트) · `semantic-scholar`(게재본·인용수) ·
`exa-search`(일반 웹) · `notebooklm` / `notebooklm-browser`

### ✍️ 논문 · 문서

| 스킬 | 하는 일 |
|---|---|
| `paper-writing` ▶ | **전체 파이프라인** — 보고서 → 개요 → 그림 → LaTeX → PDF |
| `paper-plan` / `paper-write` / `paper-compile` | 개요 / LaTeX 초고 / 컴파일·오류 수정 |
| `paper-figure` / `paper-illustration` ▶ | 결과 그림·표 / AI 일러스트·아키텍처 도식 |
| `figure-spec` | **결정론적** SVG 아키텍처 도식 (JSON 명세 → 편집 가능한 벡터) |
| `mermaid-diagram` | 플로차트·시퀀스·ER·간트 |
| `citation-audit` | 인용이 실재하고, 제대로 귀속되고, **주장을 실제로 뒷받침하는지** |
| `paper-claim-audit` | 논문의 모든 수치·비교를 **원시 결과 파일과 대조** |
| `auto-review-loop` ▶ | 다중 라운드 자동 리뷰 (`REVIEWER_BACKEND` 선택) |
| `rebuttal` ▶ / `resubmit-pipeline` ▶ | 리뷰 대응문 / 다른 학회로 이전 |
| `writing-systems-papers` | 시스템 논문 구조 설계 (OSDI/SOSP 류) |
| `overleaf-sync` | Overleaf Git 브리지 양방향 동기화 |
| `doc-coauthoring` | 스펙·제안서·결정 문서 공동 작성 |
| `grant-proposal` | 연구비 제안서 (KAKENHI/NSF/NSFC/ERC 등) |
| `pdf` | PDF 전반 — 읽기, 표 추출, 병합·분할, 폼 채우기, OCR |
| `render-html` | Markdown/JSON → 읽기 좋은 단일 HTML |

### 🔗 파이프라인 (여러 스킬을 엮어 돌림)

`research-pipeline` ▶ (아이디어 발굴 → 실험 → 리뷰 → 논문 전 과정) ·
`research-refine-pipeline` ▶ · `auto-paper-improvement-loop` ▶

### 📣 기타

`feishu-notify` — 다른 스킬이 상태를 보고할 때 쓰는 알림 채널

---

## 6. 무엇이 강제되나요

### 코딩 스타일 — ROBOTIS 프로그래밍 스타일 가이드

C, C++, Python, JavaScript/TypeScript, HTML/CSS, ROS 2 패키지 파일에 적용됩니다.
**소스 파일을 여는 순간 자동으로 로드**되므로 따로 부를 필요가 없습니다.

자주 틀리는 네 가지:

| | C / C++ | Python | JS / TS |
|---|---:|---:|---|
| 들여쓰기 | **2칸** | **4칸** | **2칸** |
| 줄 길이 | **100자** | **99자** | **100자** |
| 따옴표 | `"` 큰따옴표 | `'` 작은따옴표 | `'` 작은따옴표 |

그리고: **탭 문자 절대 금지**, 주석은 영어로, 소스에 한글 금지, 모든 파일은 빈 줄로
끝나기, 모든 소스 파일 맨 위에 Apache 2.0 헤더.

언어별 전체 내용:
[`claude-harness/skills/robotis-style/references/`](claude-harness/skills/robotis-style/references/)

> **외부 오픈소스를 수정할 때는 그 프로젝트의 스타일을 따릅니다.** 우리 스타일을
> 밀어넣지 않습니다.

### 라이선스 헤더

모든 코드는 **Apache License 2.0** 입니다. 새로 만드는 모든 소스 파일은 이렇게
시작합니다:

```python
# Copyright 2026 ROBOTIS AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# ... (중략)
# limitations under the License.
#
# Author: 내 이름 <내 이메일>
```

`Author:` 는 git 설정에서 자동으로 채워집니다. 빠뜨리면 커밋이 막힙니다.

```sh
python3 claude-harness/scripts/check_license_header.py        # 검사
python3 claude-harness/scripts/check_license_header.py --fix  # 자동 삽입
```

> ROS 인터페이스 파일(`.msg`, `.srv`, `.action`)과 `.launch.py` 는 헤더를 넣지
> 않습니다.

### 커밋 규칙

모든 커밋에 **DCO 서명(`Signed-off-by:`)** 과 **GPG 서명**이 필요합니다.

```sh
git commit -s -m "Added zero-copy path to the diff-drive controller"
```

- `-s` 가 `Signed-off-by:` 를 붙입니다. GPG 서명은 자동입니다.
- 제목은 **대문자로 시작하는 명령형 동사**로 씁니다 — 릴리스 때
  `CHANGELOG.rst` 가 커밋 제목에서 자동 생성되기 때문입니다.
  (`Added ...`, `Fixed ...`, `Removed ...`)

**AI를 공동 작성자로 넣는 것은 금지됩니다.** `Co-authored-by:` 에 Claude, Copilot,
ChatGPT 등을 쓰거나 `Generated with ...` 푸터를 붙일 수 없습니다. 도구는 저자가
아니고, 저작권과 DCO 서명은 서명한 사람의 것입니다. **이 규칙은 하네스보다
우선하며, 어떤 AI 도구의 기본 동작보다도 우선합니다.** 사람 공동 작성자는 당연히
괜찮습니다.

`--no-verify` 로 우회하는 것은 정책 위반입니다. 검사가 잘못됐으면 검사를 고칩니다.

#### 세 겹으로 막힙니다

| 검사 | 잡는 것 |
|---|---|
| `.githooks/pre-commit` | 서명 정보 미설정, GPG 키 없음, 라이선스 헤더 누락 |
| `.githooks/commit-msg` | sign-off 없음/불일치, AI 공동저자, 너무 짧은 제목 |
| `commit_guard.py` | Claude가 서명 없이 커밋하려 할 때, `--no-verify`, AI 공동저자 |

하나를 우회해도 나머지가 막습니다.

### 작업 방법론

`KERNEL.md` 와 `ROUTING.md` 가 매 세션 자동 로드됩니다. 요청을 읽고 맞는
**scope**(도메인 규칙 7개)와 **mode**(사고 방식 13개)로 라우팅하며, 나머지는 필요할
때만 읽습니다.

일곱 개 훅이 이걸 "권장" 이 아니라 "강제" 로 만듭니다:

| 훅 | 하는 일 |
|---|---|
| `session_start` | 지난 워크로그·체크포인트·미해결 주장을 세션 시작 시 주입 |
| `route_hint` | 요청에 맞는 scope/mode 제시 |
| `kernel_guard` | 커널(헌법) 수정 시 확인 요구 |
| `commit_guard` | 서명·AI 공동저자·`--no-verify` 차단 |
| `post_edit` | 편집 기록, 검증 의무 상기 |
| `pre_compact` | 컨텍스트 압축 전 상태 보존 |
| `stop_gate` | **체크포인트 없이 긴 작업을 끝낼 수 없게** |

---

## 7. 업데이트는 자동으로 되지 않습니다

이 저장소가 **유일한 원본**이고, 작성자가 직접 고칠 때만 바뀝니다.

작업 폴더에 들어간 사본은 **일부러 원본과 끊어져 있습니다.** `bootstrap.sh` 는
복사를 하지 클론을 남기지 않으므로, 작업 폴더의 git은 온전히 그 폴더 것입니다.
`git pull` 이 하네스 변경을 내 작업 위로 덮어쓰는 일이 없습니다. 대신 **업스트림
개선이 자동으로 반영되지도 않습니다.**

업데이트하려면 다시 받아서 다시 실행합니다:

```sh
rm -rf /tmp/harness
git clone git@github.com:jack0682/ROBOTISAI_harness.git /tmp/harness
/tmp/harness/bootstrap.sh ~/my_project      # --fresh 없이!
```

`--fresh` 를 빼면 `projects/`, `sessions/`, `memory/`, `registry/` — 즉 **그동안
쌓인 내 작업 기록**은 그대로 보존됩니다.

> 하네스 자체를 고쳤거나 개선점을 찾았다면 **업스트림에 보내주세요.** 한 작업
> 폴더에만 두면 다음 업데이트 때 사라집니다.

---

## 8. 자주 막히는 것들

<details>
<summary><b>"커밋이 안 돼요"</b></summary>

서명 정보가 없어서입니다. 의도된 동작입니다. `/harness` 를 치면 설정해줍니다.
수동으로 하려면:

```sh
git config --local user.name       "내 이름"
git config --local user.email      "내 이메일"
git config --local user.signingkey <GPG_키_ID>
```

`--global` 이 아니라 **`--local`** 입니다. 전역 설정을 쓰면 개인 명의가 팀 커밋에
조용히 찍힙니다.
</details>

<details>
<summary><b>"GitHub에서 Verified가 안 떠요"</b></summary>

공개키를 계정에 등록해야 합니다:

```sh
gpg --armor --export <GPG_키_ID>
```

→ GitHub Settings → SSH and GPG keys → New GPG key 에 붙여넣기.
</details>

<details>
<summary><b>"GPG 키가 없어요"</b></summary>

`/harness` 가 만드는 것부터 같이 해줍니다. 직접 하려면:

```sh
gpg --full-generate-key     # RSA 4096, 회사 이메일
```
</details>

<details>
<summary><b>"하네스가 작동 안 하는 것 같아요"</b></summary>

`/harness check` 를 치면 전부 점검하고 고칠 수 있는 건 고칩니다. 파일 존재 여부가
아니라 **검사가 실제로 막는지**까지 확인합니다.
</details>

<details>
<summary><b>"클론한 폴더 안에서 Claude를 열었어요"</b></summary>

여기서 쓰는 게 아닙니다. `/harness` 를 치면 알아서 안내하고, 작업 폴더 경로만
알려주면 설치해줍니다.
</details>

<details>
<summary><b>"스타일 규칙이 안 걸려요"</b></summary>

경로 기반 규칙은 **`Read`/`Edit` 도구에서만 발동하고 셸의 `cat` 에서는 발동하지
않습니다.** 파일을 셸로 읽으면 규칙이 조용히 빠집니다. 이건 문서화된 동작이고,
`/harness check` 가 규칙 파일 존재 여부를 확인해줍니다.
</details>

---

## 9. 폴더 구조

```
내-작업-폴더/
├── CLAUDE.md          ← 자동 생성. Claude가 매번 읽음
├── .claude/           ← 자동 생성. 훅, 스킬 링크, 파일별 규칙
├── .githooks/         ← 커밋 검사 장치
├── CONTRIBUTING.md    ← 규칙 (사람용 상세 문서)
├── LICENSE            ← Apache 2.0
├── claude-harness/    ← 하네스 본체
└── ...내 실제 작업 파일들
```

`claude-harness/` 안에서 알아둘 만한 곳:

| 경로 | 내용 |
|---|---|
| `KERNEL.md`, `ROUTING.md` | 항상 로드되는 핵심 |
| `skills/INDEX.md` | **스킬 72개 전체 목록** |
| `skills/robotis-style/` | ROBOTIS 스타일 가이드 (언어별) |
| `protocols/commit_policy.md` | 커밋 규칙 전문 |
| `scopes/` | 도메인별 규칙 7개 |
| `modes/` | 사고 방식 13개 |
| `projects/` | 내 프로젝트 정보 — 목표, 제약, 용어 |
| `sessions/` | 작업 기록. 다음 세션이 여기서 이어받음 |
| `scripts/hooks/` | 강제 담당 훅 7개 |
| `tests/` | 자체 테스트 156개 |

---

## 10. 설치 상태 직접 확인하기

```sh
python3 claude-harness/scripts/validate_harness.py               # 구조 검사
python3 claude-harness/scripts/check_license_header.py           # 라이선스 헤더
cd claude-harness && python3 -m unittest discover -s tests -q    # 자체 테스트
```

`/harness check` 가 이걸 전부 돌리고 결과를 해석해주므로, 보통은 그쪽이 편합니다.

---

## 기여

하네스 자체를 고쳤거나 개선점을 찾았다면 업스트림으로 보내주세요. 규칙은
[`CONTRIBUTING.md`](CONTRIBUTING.md) 에 있습니다 — 서명 설정, 커밋 규칙, 스타일
가이드 적용 범위.

## 라이선스

[Apache License 2.0](LICENSE) — Copyright 2026 ROBOTIS AI
