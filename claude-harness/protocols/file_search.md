# Protocol · File Search

> Layer 1 — universal per-task procedure. No project specifics.

Use when locating code/content across a codebase or filesystem.

## Steps
1. **Pick the right tool for the shape of the search.**
   - Known exact string/symbol → direct grep/search.
   - Known filename/glob → file find.
   - Broad/uncertain scope spanning many files → delegate to a search agent and
     keep the conclusion, not the file dumps.
2. **Start broad, then narrow.** Locate candidate regions, then read the precise
   spans that matter.
3. **Search by multiple angles** when one term might miss it: by symbol, by
   caller, by string literal, by config key.
4. **Confirm by reading.** Don't conclude from a filename or a match preview — open
   the spot and verify it's actually what you need.

## Output
- Report findings as `path:line` references.
- Distinguish "found it, here" from "likely here, unconfirmed."

## Don'ts
- Don't claim something doesn't exist after one narrow search — vary the query
  before concluding absence.
- Don't read whole large files when you know the span you need.
