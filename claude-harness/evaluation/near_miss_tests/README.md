# near_miss_tests/ — prompts that should NOT trigger a given target

Each case: a prompt that *looks* related to a mode/scope/skill but should **not**
select it, plus what it should do instead. A false fire = the trigger is too
greedy; tighten the `description`/routing. Run by reading (`evaluation/README.md`).

**The full golden set lives in [`cases.yaml`](cases.yaml)**; `should_not` targets are
integrity-checked by `evaluation/check_routing_tests.py`.

## Seed cases

```
- prompt: "이 함수 이름 좀 더 명확하게 바꿔줘"
  should_not: math_lock        # mentions "함수" but is a naming task
  expect_instead: coding (styles/naming.md)

- prompt: "이 수식 LaTeX으로 예쁘게 렌더만 해줘"
  should_not: math_lock        # math present, but no claim to verify
  expect_instead: writing (formatting)

- prompt: "오늘 한 거 그냥 한 줄로 요약만 해줘"
  should_not: memory           # a summary, not a distillation-to-persist
  expect_instead: a plain summary; persist nothing

- prompt: "이 에러 로그 무슨 뜻이야?"
  should_not: prompt           # "prompt"-adjacent words, but it's debugging
  expect_instead: coding/debugging

- prompt: "이 논문 뭐에 대한 건지 한 문단으로 알려줘"
  should_not: paper            # not a critique; just an explainer
  expect_instead: a brief explanation (research-lite)
```

The most valuable near-miss cases are the ones found in the wild — when a mode or
skill fired on something it shouldn't have, record it here so it can't drift back.
