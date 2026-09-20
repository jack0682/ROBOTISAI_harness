# Style · Naming

> Layer 2 — universal presentation convention. No project specifics.

For naming code symbols, files, and harness artifacts.

## Principles
- **Descriptive over clever.** A name should reveal intent without a comment.
- **Consistent over correct-in-isolation.** Follow the existing convention of the
  file/codebase even if you'd personally pick differently.
- **Right length for scope.** Short names for short-lived locals; fuller names for
  things used far from their definition.

## Conventions
- Match the host language/ecosystem (snake_case, camelCase, PascalCase, kebab-case)
  — don't impose a foreign convention.
- Booleans read as predicates: `is_ready`, `has_children`.
- Functions are verbs/verb-phrases; values/objects are nouns.
- Avoid abbreviations unless they're standard in the domain.

## Harness artifacts
- Skills, projects, sessions: `kebab-case` or `snake_case` slugs, lowercase.
- Session files: `<date>_<short_slug>.md`.

## Don'ts
- Don't encode type into the name when the language already carries it.
- Don't reuse a name for a different meaning nearby.
