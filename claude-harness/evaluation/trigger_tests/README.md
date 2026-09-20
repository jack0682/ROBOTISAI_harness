# trigger_tests/ — prompts that SHOULD route a certain way

Each case: a user prompt + the mode/scope/skill it **should** select. Run by
reading (`evaluation/README.md`). A miss = the routing or a `description` is too
weak; fix the trigger, not the test.

**The full golden set lives in [`cases.yaml`](cases.yaml)** (this file documents the
format; the block below is illustrative). Reference integrity — every `expect_*`
names a real, *active* mode/scope/skill, not an archived one — is enforced by
`evaluation/check_routing_tests.py`.

Format (one case per list item; keep them terse):

```
- prompt: "이 정리가 정의역에서 잘 정의되는지 확인해줘"
  expect_mode: math_lock
  expect_scope: math
  why: explicit request to check a formalism holds
```

## Seed cases

```
- prompt: "이 긴 메모에서 핵심 문제만 한 문장으로 뽑아줘"
  expect_mode: think
  why: compression / problem extraction

- prompt: "이 수식이 진짜 그 주장을 뒷받침하는지 봐줘"
  expect_mode: math_lock
  expect_scope: math
  why: claim↔math correspondence check

- prompt: "이 결과를 다른 걸로도 설명할 수 있지 않아?"
  expect_mode: counter
  why: alternative-explanation / attack

- prompt: "이 논문 리뷰어 입장에서 까줘"
  expect_mode: paper
  expect_scope: writing
  why: hostile-reviewer critique

- prompt: "이 작업을 다른 에이전트한테 시킬 프롬프트로 만들어줘"
  expect_mode: prompt
  expect_scope: prompts
  why: behavior-contract authoring

- prompt: "이 분야 이미 있는 건지, 이름만 다른 건지 정리해줘"
  expect_mode: research
  expect_scope: research
  why: novelty / prior-art terrain
```
