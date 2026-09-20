# Copyright 2026 ROBOTIS AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Jaehong Oh <jaehongoh1554@gmail.com>

"""Shared helpers for the harness hook scripts.

Hooks are run by the Claude Code runtime (not the model) with the hook event
JSON on stdin. Everything here is stdlib-only and must never raise out of a
hook: a crashed hook degrades the session. Callers wrap main() in `safe()`.

The audit log (sessions/.audit.log) holds JSONL entries of three kinds,
classified by key:
  {"tool": <Edit|Write|...>, "file_path": ...}   — a file modification
  {"tool": "Bash", "command": ...}               — a command execution
  {"event": <name>, "detail": {...}}             — hook self-instrumentation
All carry "ts" and "session_id".
"""

from __future__ import annotations

import json
import os
import re
import sys
import time


def safe(main):
    """Run a hook main(); on any internal error, exit 0 but RECORD the crash.

    Exit code 2 blocks tools/stop in Claude Code, so an unexpected crash must
    never propagate as a non-zero exit — a buggy hook must not brick the
    session (fail-open on infrastructure failure is deliberate). But a hook
    that fails open *silently* is a gate that has quietly stopped enforcing,
    which is exactly the "incomplete gate = silent pass" failure a governance
    layer must avoid. So the crash is logged as a `hook_crash` event: the gate
    still yields, but its failure is now visible in sessions/.audit.log instead
    of vanishing. A chronically-crashing guard shows up in the data.
    """
    try:
        return main() or 0
    except Exception as exc:  # noqa: BLE001 - deliberate: hooks fail open, but loudly
        try:
            script = os.path.basename(sys.argv[0]) if sys.argv else "?"
            log_event("", "hook_crash", script=script,
                      error=f"{type(exc).__name__}: {exc}"[:200])
        except Exception:
            pass
        return 0


def read_input():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def harness_root():
    """scripts/hooks/_hooklib.py -> the harness root two levels up."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _plugin_install():
    """(cache_root, plugin_name) when this copy is a plugin install, else None.

    A plugin is unpacked to `<cache>/<marketplace>/<plugin>/<version>/`, so the
    harness root's basename is a version string. Two things break on that and
    both were found by actually installing it: every gate message named `0.4.0`
    as if it were a directory, and the writable state landed inside a directory
    that a version bump replaces.
    """
    root = harness_root()
    parent = os.path.dirname(root)
    if os.sep + "plugins" + os.sep + "cache" + os.sep not in root + os.sep:
        return None
    name = os.path.basename(parent)
    return (parent, name) if name else None


def hdir_name():
    """What to call this harness in a message shown to a person.

    In a clone that is the directory it lives in. In a plugin install the
    directory is a version number, which is useless in a sentence like "write a
    checkpoint in 0.4.0/sessions/" — so the plugin's name is used instead.
    """
    install = _plugin_install()
    if install:
        return install[1]
    return os.path.basename(harness_root())


def state_root():
    """Where this harness's *writable* state lives.

    `harness.config.yaml` already separates the shipped layers from the local
    ones (`distribution.local_dirs`: projects, sessions, memory, registry). In a
    clone they sit together and that is fine. In a plugin install they must not:
    the plugin unpacks under a version directory, so writing state there means a
    version bump silently leaves behind the audit log, the claims and every
    worklog. The telemetry that per-skill contribution needs would reset on
    every update and never reach its evidence bar.

    `HARNESS_STATE_DIR` overrides. Otherwise a plugin install keeps state beside
    the cache under the plugin's name, and a clone is unchanged.
    """
    override = os.environ.get("HARNESS_STATE_DIR")
    if override:
        return override
    install = _plugin_install()
    if install:
        cache_root, name = install
        # `<config>/plugins/cache/<marketplace>/<plugin>` -> keep state beside
        # `plugins`, not under it: a directory named `cache` is one somebody
        # eventually clears, and this is the store a settled claim cites.
        marker = os.sep + "plugins" + os.sep + "cache" + os.sep
        config_dir, _, rest = cache_root.partition(marker)
        return os.path.join(config_dir, "harness-state",
                            os.path.dirname(rest) or "local", name)
    return harness_root()


def sessions_dir():
    return os.path.join(state_root(), "sessions")


def audit_log_path():
    """Where the hook layer records what it did.

    `HARNESS_AUDIT_LOG` redirects it. The hooks run as subprocesses, so a test
    that exercises them cannot mock this -- and without the override the suite
    wrote its synthetic events into the real log. That log is the evidence store
    claims are settled against (memory/claims/), and it was once 86/150 test
    noise, which is why a claim about the hooks could not be checked against it.
    """
    path = (os.environ.get("HARNESS_AUDIT_LOG")
            or os.path.join(sessions_dir(), ".audit.log"))
    # In a plugin install this directory does not exist until something writes.
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except OSError:
        pass
    return path


def session_files():
    """Real session worklogs (README and the template excluded).

    Active worklogs live in sessions/active/; the sessions/ top level is still
    scanned for backward compatibility with worklogs written before the
    active/ split. archived/ and distilled/ are intentionally excluded — a
    retired or distilled log is not a resume target.
    """
    out = []
    for d in (os.path.join(sessions_dir(), "active"), sessions_dir()):
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if fn.endswith(".md") and fn not in ("README.md", "_session_template.md"):
                out.append(os.path.join(d, fn))
    return sorted(out)


_SESSION_DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


def session_age_days(path, today=None):
    """Age of a worklog in days, from the date in its filename.

    Mtime cannot answer this. `new_session.py` names every worklog
    `<YYYY-MM-DD>_<slug>.md`, but a `git checkout` rewrites mtimes, so a worklog
    written in July reads as minutes old on a fresh clone — which is how a
    two-month-old "Next action: commit + push" was injected into the top of
    every session for two months. A worklog with no date in its name falls back
    to mtime, which is the best available answer for it.
    """
    match = _SESSION_DATE_RE.search(os.path.basename(path))
    today = today or time.time()
    if match:
        try:
            stamp = time.mktime((int(match.group(1)), int(match.group(2)),
                                 int(match.group(3)), 12, 0, 0, 0, 1, -1))
            return max(0.0, (today - stamp) / 86400.0)
        except (ValueError, OverflowError):
            pass
    try:
        return max(0.0, (today - os.path.getmtime(path)) / 86400.0)
    except OSError:
        return 0.0


def session_max_age_days():
    try:
        value = float(os.environ.get("CLAUDE_HARNESS_SESSION_MAX_AGE_DAYS", "14"))
    except ValueError:
        return 14.0
    return value if value > 0 else float("inf")


def latest_session_file():
    """The most recent worklog worth resuming, or None.

    Old worklogs are not resume targets. Injecting one is worse than injecting
    nothing: it presents finished work as the session's pending next action.
    """
    limit = session_max_age_days()
    files = [f for f in session_files() if session_age_days(f) <= limit]
    return max(files, key=os.path.getmtime) if files else None


# --- Audit log -----------------------------------------------------------

def read_audit(session_id=None):
    entries = []
    path = audit_log_path()
    if not os.path.isfile(path):
        return entries
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except Exception:
                continue
            if session_id is None or entry.get("session_id") == session_id:
                entries.append(entry)
    return entries


def append_audit(entry):
    with open(audit_log_path(), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def log_event(session_id, event, **detail):
    """Self-instrumentation: record what the hook layer itself did, so silent
    failures (a lost injection, a gate block) are visible in the data."""
    entry = {"ts": time.time(), "session_id": session_id, "event": event}
    if detail:
        entry["detail"] = detail
    append_audit(entry)


_SKILL_NAME_KEYS = ("skill", "skill_name", "name", "skillName")


def skill_name(tool_input):
    """The skill a `Skill` tool call names, or "".

    The Skill tool's input shape is not documented, so this reads the plausible
    keys rather than asserting one. Getting "" back is the honest answer for an
    unrecognised shape -- the library report then shows zero invocations, which
    is visible, instead of a confident wrong name.
    """
    ti = tool_input or {}
    if not isinstance(ti, dict):
        return ""
    for key in _SKILL_NAME_KEYS:
        value = ti.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def is_file_edit(entry):
    return ("tool" in entry and entry.get("tool") not in ("Bash", "Skill")
            and bool(entry.get("file_path")))


def is_skill_use(entry):
    return entry.get("tool") == "Skill" and bool(entry.get("skill"))


def is_bash(entry):
    return entry.get("tool") == "Bash"


def is_event(entry):
    return "event" in entry


def under_sessions(path):
    return os.path.realpath(path).startswith(
        os.path.realpath(sessions_dir()) + os.sep)


def under_harness(path):
    return os.path.realpath(path).startswith(
        os.path.realpath(harness_root()) + os.sep)


# --- Worklog extraction ----------------------------------------------------

_HEADING_RE = re.compile(r"^#{1,6} ")


def extract_section(text, header):
    """Return the body of a markdown section. Any heading level ends the
    section (a `# Plan:` h1 after `## Next Step` must not leak in)."""
    out, active = [], False
    for line in text.splitlines():
        if _HEADING_RE.match(line):
            active = line.strip() == header
            continue
        if active:
            out.append(line)
    return "\n".join(out).strip()


# Fences may carry a language tag (```text) — kernel/execution_protocol.md
# documents the checkpoint format with one, so the extractor must accept it.
_CHECKPOINT_BLOCK_RE = re.compile(r"```[a-zA-Z]*[ \t]*\n(CHECKPOINT\b.*?)```", re.S)
_TIME_RE = re.compile(r"^Time:\s*(\S.*)$", re.M)


def _parse_time(s):
    from datetime import datetime
    try:
        return datetime.fromisoformat(s.strip()).timestamp()
    except Exception:
        return None


def last_checkpoint(text):
    """Return the most recent fenced CHECKPOINT block.

    Worklogs order checkpoint blocks inconsistently (append-order and
    newest-first both occur in the field), so prefer the block with the
    latest parseable `Time:` line; fall back to the last block in the file.
    """
    blocks = [b.strip() for b in _CHECKPOINT_BLOCK_RE.findall(text)]
    if not blocks:
        return None
    timed = []
    for b in blocks:
        m = _TIME_RE.search(b)
        t = _parse_time(m.group(1)) if m else None
        if t is not None:
            timed.append((t, b))
    if timed:
        return max(timed, key=lambda x: x[0])[1]
    return blocks[-1]


def edited_path(tool_input):
    ti = tool_input or {}
    return ti.get("file_path") or ti.get("notebook_path") or ""


# --- Active project ---------------------------------------------------------

def active_project():
    """Return (name, config dict) when exactly one registered project is
    active; otherwise None. Fail-open: any parse problem returns None."""
    try:
        scripts = os.path.join(harness_root(), "scripts")
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        import _common as C
        reg = C.load_yaml(os.path.join(harness_root(), "registry",
                                       "projects.yaml")) or {}
        actives = [p for p in reg.get("projects", [])
                   if isinstance(p, dict) and p.get("status") == "active"]
        if len(actives) != 1:
            return None
        cfg_path = os.path.join(harness_root(), actives[0]["path"],
                                "project.config.yaml")
        if not os.path.isfile(cfg_path):
            return None
        return actives[0].get("name", "?"), (C.load_yaml(cfg_path) or {})
    except Exception:
        return None


def active_project_dir():
    """Absolute path to the single active project's directory, or None.
    Fail-open: any registry parse problem returns None."""
    try:
        scripts = os.path.join(harness_root(), "scripts")
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        import _common as C
        reg = C.load_yaml(os.path.join(harness_root(), "registry",
                                       "projects.yaml")) or {}
        actives = [p for p in reg.get("projects", [])
                   if isinstance(p, dict) and p.get("status") == "active"]
        if len(actives) != 1:
            return None
        return os.path.join(harness_root(), actives[0]["path"])
    except Exception:
        return None
