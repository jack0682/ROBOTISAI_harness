# sessions/distilled

Where a distillation run writes what it proposes: memory items, patterns, and
skill patches, as text for a person to approve.

This is the only place besides `../../memory/` that the distillation sandbox
permits writes to (`scripts/hooks/kernel_guard.py`). A distiller proposes skill
changes here; it never edits `skills/` directly.

The contents are deployment state and are not tracked.
