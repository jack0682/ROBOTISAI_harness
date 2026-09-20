# ROBOTIS AI Harness

로보티즈 AI 팀이 Claude Code를 쓸 때 **코딩 스타일·커밋 규칙·작업 방법론을 자동으로
강제**하는 레이어입니다. 각자의 작업 폴더에 한 번 넣어두면, 그 폴더에서 Claude를 열
때마다 규칙이 자동으로 적용됩니다.

외울 명령어는 **`/harness` 하나**입니다. 나머지는 이 문서가 설명합니다.

---

## 1. 5분 안에 시작하기

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
- 템플릿 저장소와의 git 연결 끊기 (어차피 푸시 못 하는데 시도하면 시간 낭비라서)
- 설치가 제대로 됐는지 검사하고 결과 출력

> `--fresh` 는 **처음 설치할 때만** 씁니다. 나중에 업데이트할 때 붙이면 그동안 쌓인
> 작업 기록이 초기화됩니다.

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

## 2. `/harness` 가 실제로 하는 일

**상황을 스스로 판단합니다.** 같은 명령어인데 처음 칠 때와 나중에 칠 때 하는 일이
다릅니다.

### 처음 칠 때 — 설치 직후

세 가지를 순서대로 처리합니다.

**① 서명 정보 설정** — 이게 제일 먼저인 이유는, 이게 없으면 **커밋이 아예 안 되기
때문**입니다. 하루 종일 작업하고 마지막에 막히는 걸 막으려고 맨 앞에 둡니다.

이름·이메일·GPG 키를 물어봅니다. GPG 키가 없으면 만드는 것부터 같이 합니다.

**② 작업 폴더 분석** — 이게 무슨 프로젝트인지, 어떤 언어를 쓰는지, 빌드와 테스트는
어떻게 돌리는지, 기존 규칙이 뭔지를 직접 읽습니다. 사람에게 묻지 않고 코드를 봅니다.

**③ 뭘 하고 싶은지 묻기** — 코드를 읽으면 "이게 무엇인지" 는 알 수 있지만 "무엇을
위한 것인지" 는 알 수 없습니다. 그래서 네 가지만 묻습니다.

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

## 3. 알아야 할 명령어는 두 개

| 명령어 | 언제 |
|---|---|
| **`/harness`** | 처음 설치할 때 · 새 세션 시작할 때 · 뭔가 이상할 때 (`/harness check`) |
| **`/harness-checkpoint`** | 작업이 길어질 때 중간 저장. 세션이 끊겨도 다음에 이어서 할 수 있게 |

나머지 두 개(`/harness-init`, `/harness-load`)는 `/harness` 가 내부적으로 부르는
것들이라 직접 칠 일은 거의 없습니다.

그 외에는 **그냥 평소처럼 한국어로 말하면 됩니다.** "이 함수 버그 좀 찾아줘",
"이 부분 리팩터링 해줘" — 하네스가 알아서 맞는 규칙을 불러옵니다.

---

## 4. 무엇이 강제되나요

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

언어별 전체 내용은 `claude-harness/skills/robotis-style/references/` 에 있습니다 —
C++(Rev 35), C(Rev 18), Python(Rev 18), ROS(Rev 10), JavaScript(Rev 9).

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

### 이 규칙들은 세 겹으로 막힙니다

| 검사 | 잡는 것 |
|---|---|
| `.githooks/pre-commit` | 서명 정보 미설정, GPG 키 없음, 라이선스 헤더 누락 |
| `.githooks/commit-msg` | sign-off 없음/불일치, AI 공동저자, 너무 짧은 제목 |
| `commit_guard.py` | Claude가 서명 없이 커밋하려 할 때, `--no-verify`, AI 공동저자 |

하나를 우회해도 나머지가 막습니다.

### 작업 방법론

`KERNEL.md` 와 `ROUTING.md` 가 매 세션 자동으로 로드됩니다. 요청을 읽고 맞는
**scope**(도메인 규칙)와 **mode**(사고 방식)로 라우팅하며, 나머지는 필요할 때만
읽습니다.

일곱 개 훅이 이걸 "권장" 이 아니라 "강제" 로 만듭니다 — 세션 시작 컨텍스트 주입,
라우팅 힌트, 커널 수정 확인, 커밋 가드, 편집 기록, 압축 전 저장, 그리고 **긴 작업을
체크포인트 없이 끝내지 못하게 하는 stop gate**.

---

## 5. 업데이트는 자동으로 되지 않습니다

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

## 6. 자주 막히는 것들

**"커밋이 안 돼요"**
서명 정보가 없어서입니다. 의도된 동작입니다. `/harness` 를 치면 설정해줍니다.
수동으로 하려면:

```sh
git config --local user.name       "내 이름"
git config --local user.email      "내 이메일"
git config --local user.signingkey <GPG_키_ID>
```

`--global` 이 아니라 **`--local`** 입니다. 전역 설정을 쓰면 개인 명의가 팀 커밋에
조용히 찍힙니다.

**"GitHub에서 Verified가 안 떠요"**
공개키를 계정에 등록해야 합니다:

```sh
gpg --armor --export <GPG_키_ID>
```

→ GitHub Settings → SSH and GPG keys → New GPG key 에 붙여넣기.

**"하네스가 작동 안 하는 것 같아요"**
`/harness check` 를 치면 전부 점검하고 고칠 수 있는 건 고칩니다.

**"클론한 폴더 안에서 Claude를 열었어요"**
여기서 쓰는 게 아닙니다. `/harness` 를 치면 알아서 안내하고, 작업 폴더 경로만
알려주면 설치해줍니다.

**"GPG 키가 없어요"**
`/harness` 가 만드는 것부터 같이 해줍니다. 직접 하려면:

```sh
gpg --full-generate-key     # RSA 4096, 회사 이메일
```

---

## 7. 폴더 구조

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
| `skills/robotis-style/` | ROBOTIS 스타일 가이드 (언어별) |
| `protocols/commit_policy.md` | 커밋 규칙 전문 |
| `projects/` | 내 프로젝트 정보 — 목표, 제약, 용어 |
| `sessions/` | 작업 기록. 다음 세션이 여기서 이어받음 |
| `scripts/` | 설치기, 검사기 |

---

## 8. 설치 상태 직접 확인하기

```sh
python3 claude-harness/scripts/validate_harness.py               # 구조 검사
python3 claude-harness/scripts/check_license_header.py           # 라이선스 헤더
cd claude-harness && python3 -m unittest discover -s tests -q    # 자체 테스트
```

`/harness check` 가 이걸 전부 돌리고 결과를 해석해주므로, 보통은 그쪽이 편합니다.

## 라이선스

Apache License 2.0 — `LICENSE` 참조.
