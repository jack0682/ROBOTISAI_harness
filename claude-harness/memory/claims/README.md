# memory/claims/ — load-bearing claims with an expiry clock

> A claim is a memory item with `scope: claim`. This bucket is where the
> harness's central commitment — *verification over agreement; a claim is
> escape-proof or it is not settled* — is made durable and **enforced**, not
> just asserted. Adapted from Haft's decision records (claim + threshold +
> evidence + expiry, reopen-on-decay).

## Why this exists

`review_at` and `supersedes` already lived in the memory frontmatter but
nothing enforced them — a "settled" claim could carry no evidence and never
expire. That is exactly the decorative-rigor failure the harness exists to
prevent. Claims close that gap: a claim's epistemic state is a checked
invariant, not a label.

## Lifecycle

```
open ──(threshold measured, evidence meets it)──► settled ──(review_at passes)──► stale
  ▲                                                                                │
  └──────────────────── re-verify: bump review_at (renew) or archive ◄────────────┘
```

- **open** — a hypothesis under construction. No evidence requirement; this is
  where a claim lives while it is being attacked (`modes/counter.md`) and
  formalized (`modes/math_lock.md`).
- **settled** — *earned*. Must carry: `threshold` (what would refute it),
  `evidence` (the result that met that bar), and a dated `review_at` (when it
  must be re-checked). A `settled` claim missing any of these is a **gate
  failure** (`scripts/validate_harness.py` and the stop hook block it).
- **stale** — a `settled` claim whose `review_at` has passed. Time elapsed
  without re-verification, so it may no longer be cited as settled. Re-check,
  then either bump `review_at` (renew) or retire it to `archived/`.

## Item format

```markdown
---
name: <kebab-case-slug>            # unique; matches the filename
scope: claim
importance: <high|medium|low>
status: <open|settled|stale>       # epistemic state — enforced
threshold: <what measurable result would REFUTE this | none>   # required if settled
evidence: <the result that met the threshold + where to find it | none>  # required if settled
review_at: <YYYY-MM-DD>            # expiry: when a settled claim must be re-checked
supersedes: <slug | none>          # edge: must name a claim that exists
contradicted_by: <slug[, slug] | none>   # edge: what disputes this — blocks settled
source: <session/experiment that produced it>
signature: <short dedupe key>
---

<The claim, stated as one falsifiable sentence. Follow with
**What would reopen it:** and link evidence / related items with [[slug]].>
```

`_claim_template.md` is the copyable skeleton (underscore-prefixed files are
skipped by the validator). After writing a claim, add its line to `MEMORY.md`.

## The discipline (why each field is load-bearing)

- **No `settled` without a `threshold`.** A claim you can't state a refutation
  for is not falsifiable — it can't be settled, only *open*.
- **No `settled` without `evidence`.** A label is not a result. CI/unit-test
  green is supplemental, not the threshold result, unless the threshold *was*
  that test (`modes/verify.md` proof hierarchy).
- **Every `settled` claim expires.** `review_at` forces re-contact with reality
  on a clock; a claim that was true once is not assumed true forever.
- **A contradiction is recorded, not adjudicated silently.** `contradicted_by`
  names what disputes the claim. `settled` + a standing contradiction is an
  **error**: keeping the certification while the conflict sits on record is the
  precise failure this bucket exists to prevent. Resolve it (refute the
  challenger, or reopen the claim) — the edge is not a footnote.
- **An edge may not name something that does not exist.** Both `supersedes` and
  `contradicted_by` are checked against `memory/claims/`, the same rule the
  work graph already enforces on `blocked_by` / `supersedes`. A pointer at a
  renamed or never-written claim is a defect in either place.
