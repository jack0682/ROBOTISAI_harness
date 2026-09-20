# mode · research — map a field, don't summarize it

**Trigger.** "이 분야 어떻게 돼 있어", a literature question, novelty check, prior-art
search, deciding whether an idea is worth building.

**Input.** The topic/idea, and access to sources (skills: `arxiv`, `semantic-scholar`,
`exa-search`, `novelty-check`, `research-lit`;
live facts via `protocols/web_search.md`).

**Operations.** Produce a *terrain*, not a reading list:
1. **Map & lineage.** The major lines of work, who descends from whom, how the
   problem has been framed over time.
2. **Clusters.** Group approaches by their actual idea, not by keyword. Name each
   cluster's core assumption.
3. **Gaps.** Where the map is empty — and whether it's empty because it's hard,
   uninteresting, or genuinely unexplored.
4. **Existing terms.** What the user's idea would already be *called* in the
   literature. Surface naming collisions early.
5. **Differentiation.** Against the closest existing work, what is actually
   different here — mechanism, not marketing.
6. **Risky claims.** Flag field claims that are weakly supported, contested, or
   widely-cited-but-thin.
7. **The three questions.** "Does this already exist?" / "Is it the same thing
   under a different name?" / "Is it actually worth building?" — answer each, with
   sources.

**Output.** A field map (clusters + lineage), a gap list, the existing-name
mapping, a differentiation statement, a risky-claims list, and a verdict on the
three questions — each claim traceable to a real source (`styles/citation.md`;
never cite an unread source).

**Guardrails.** Don't launder a summary as a map. Distinguish what the literature
*shows* from what it *asserts*. Mark recency-sensitive findings and verify them
live.

**Anti-patterns.** ❌ A bullet list of paper abstracts. ❌ Claiming novelty
without checking existing names. ❌ Citing what you didn't read.

**Loop position.** Feeds *Claim* and *Definition* — research sharpens what's worth
claiming and reveals the real definitions in use.
