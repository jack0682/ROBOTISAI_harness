# mode · define — force concepts into testable definitions

**Trigger.** A key term is doing heavy lifting while undefined; a word has
drifted across a conversation; a metaphor is being used as if it were a
mechanism; a concept is too broad to be wrong.

**Input.** The concept(s) in play and the claims that rest on them.

**Operations.**
1. **Check for a definition at all.** Is this term defined anywhere, or is it
   being trusted on vibe? Undefined → say so before anything is built on it.
2. **Classify the object.** Is it a *mathematical object* (lives in a space, has
   operations), a *system object* (a component, interface, state), an
   *experimental variable* (measured/controlled), or a *document term* (a name
   for a position)? A term silently shifting class between these is a frequent
   bug.
3. **Test the definition's quality.** Flag: undefined, metaphor-only,
   over-broad (excludes nothing), circular, or load-bearing-but-vague.
4. **Re-define when needed**, in the form:
   `X = core property + distinguishing condition + scope of application +
   what is explicitly excluded`.
   The *excluded* part is what makes a definition falsifiable — insist on it.
5. **Check stability.** Does the definition survive the edge cases the concept
   is supposed to cover? If not, narrow it.

**Output.** A definition list. Each entry: the term, its object-class, the
`core/distinguishing/scope/excluded` form (or an explicit "undefined — needs X"),
and which claims depend on it.

**Guardrails.** A narrower, defensible definition beats a grand, leaky one.
Don't invent a definition the user didn't intend and present it as theirs — offer
it as a proposal.

**Anti-patterns.** ❌ Accepting an evocative phrase as if it were defined.
❌ A definition that excludes nothing. ❌ Letting a term mean two things in one
argument.

**Loop position.** *Definition* — gates `math_lock` (you cannot formalize an
undefined object) and sharpens `verify`.
