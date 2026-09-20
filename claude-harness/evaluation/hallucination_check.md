# Evaluation · Hallucination Check

> A focused gate against fabrication. Run on anything with factual or code claims.

## Check every claim against its source
- [ ] **APIs / functions / flags** — each one actually exists (checked, not recalled).
- [ ] **File paths** — each referenced path is real.
- [ ] **Citations** — each source was actually consulted; titles/URLs are real.
- [ ] **Numbers** — each figure came from a check, not an estimate dressed as fact.
- [ ] **Outputs** — any shown output is a real run, not an expected/mock one.
- [ ] **Quotes** — exact and in-context.

## The core question
> For each factual statement: *can I point to where I verified this?* If the answer
> is "I'm fairly sure" — that's not verified. Mark it as inferred, or go verify it.

## Fail conditions (any one = fix before delivering)
- An invented identifier, path, or citation.
- A guess written in the grammar of a fact.
- Mock/expected output presented as actual.
