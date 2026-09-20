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

"""Shared utilities for the claude-harness scripts.

Locates the harness root, loads config/registry, and provides small helpers for
copying templates and slugifying names. Uses PyYAML when available and falls back
to a minimal stdlib reader/writer for the simple YAML subset the harness ships
with (nested mappings, lists, lists of mappings, plain scalars), so the scripts
run without extra installs. The fallback does not preserve comments on write —
neither does PyYAML's safe_dump from parsed data.
"""

from __future__ import annotations

import os
import re
import shutil

# --- YAML backend (PyYAML if present, else minimal stdlib fallback) ---------

try:
    import yaml  # type: ignore

    def load_yaml(path):
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}

    def dump_yaml(path, data):
        with open(path, "w", encoding="utf-8") as fh:
            yaml.safe_dump(data, fh, sort_keys=False, allow_unicode=True)

    HAVE_PYYAML = True
except Exception:  # pragma: no cover - exercised only without PyYAML
    HAVE_PYYAML = False

    def load_yaml(path):
        with open(path, "r", encoding="utf-8") as fh:
            return _fallback_parse(fh.read())

    def dump_yaml(path, data):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(_fallback_dump(data)) + "\n")


# --- Fallback YAML reader/writer (stdlib only) -------------------------------
# Supports the subset the harness uses: nested mappings, lists, lists of
# mappings ("- key: value" + continuation keys), quoted/plain scalars, ints,
# floats, booleans, null, [] and {}. Full-line and trailing comments handled.

def _strip_comment(line):
    out = []
    quote = None
    for ch in line:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            out.append(ch)
        elif ch == "#":
            break
        else:
            out.append(ch)
    return "".join(out).rstrip()


def _parse_scalar(s):
    s = s.strip()
    if s in ("", "null", "~"):
        return None
    if s in ("true", "True"):
        return True
    if s in ("false", "False"):
        return False
    if s == "[]":
        return []
    if s == "{}":
        return {}
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    for cast in (int, float):
        try:
            return cast(s)
        except ValueError:
            pass
    return s


def _split_key(content):
    """Split 'key: rest' on the first ':' outside quotes; None if not a pair."""
    quote = None
    for i, ch in enumerate(content):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == ":":
            if i == len(content) - 1 or content[i + 1] in " \t":
                key = content[:i].strip()
                if len(key) >= 2 and key[0] == key[-1] and key[0] in "\"'":
                    key = key[1:-1]
                return key, content[i + 1:].strip()
    return None


def _fallback_parse(text):
    lines = []
    for raw in text.splitlines():
        if raw.lstrip().startswith("#"):
            continue
        stripped = _strip_comment(raw)
        if not stripped.strip():
            continue
        lines.append((len(stripped) - len(stripped.lstrip(" ")), stripped.strip()))
    if not lines:
        return {}
    value, _ = _parse_block(lines, 0)
    return value if value is not None else {}


def _parse_block(lines, idx):
    indent = lines[idx][0]
    if lines[idx][1] == "-" or lines[idx][1].startswith("- "):
        return _parse_list(lines, idx, indent)
    return _parse_map(lines, idx, indent)


def _collect_span(lines, idx, indent):
    span = []
    while idx < len(lines) and lines[idx][0] > indent:
        span.append(lines[idx])
        idx += 1
    return span, idx


def _parse_list(lines, idx, indent):
    items = []
    while (idx < len(lines) and lines[idx][0] == indent
           and (lines[idx][1] == "-" or lines[idx][1].startswith("- "))):
        rest = lines[idx][1][1:].strip()
        idx += 1
        span, idx = _collect_span(lines, idx, indent)
        if rest:
            span.insert(0, (indent + 2, rest))
        if not span:
            items.append(None)
        elif len(span) == 1 and _split_key(span[0][1]) is None:
            items.append(_parse_scalar(span[0][1]))
        else:
            value, _ = _parse_block(span, 0)
            items.append(value)
    return items, idx


def _parse_map(lines, idx, indent):
    out = {}
    while (idx < len(lines) and lines[idx][0] == indent
           and not lines[idx][1].startswith("- ") and lines[idx][1] != "-"):
        pair = _split_key(lines[idx][1])
        if pair is None:
            raise ValueError(f"fallback YAML reader: not a 'key: value' line: "
                             f"{lines[idx][1]!r}")
        key, rest = pair
        idx += 1
        if rest:
            out[key] = _parse_scalar(rest)
        else:
            if (idx < len(lines) and lines[idx][0] == indent
                    and (lines[idx][1] == "-" or lines[idx][1].startswith("- "))):
                out[key], idx = _parse_block(lines, idx)
            else:
                span, idx = _collect_span(lines, idx, indent)
                out[key] = _parse_block(span, 0)[0] if span else None
    return out, idx


def _fmt_scalar(v):
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    needs_quotes = (s == "" or s != s.strip()
                    or any(c in s for c in ":#\"'{}[]")
                    or s.lower() in ("null", "true", "false", "yes", "no", "~"))
    if needs_quotes:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def _fallback_dump(data, indent=0):
    pad = "  " * indent
    lines = []
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{pad}{k}:")
                lines.extend(_fallback_dump(v, indent + 1))
            else:
                lines.append(f"{pad}{k}: {_fmt_value(v)}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item:
                first = True
                for k, v in item.items():
                    prefix = f"{pad}- " if first else f"{pad}  "
                    first = False
                    if isinstance(v, (dict, list)) and v:
                        lines.append(f"{prefix}{k}:")
                        lines.extend(_fallback_dump(v, indent + 2))
                    else:
                        lines.append(f"{prefix}{k}: {_fmt_value(v)}")
            else:
                lines.append(f"{pad}- {_fmt_scalar(item)}")
    else:
        lines.append(f"{pad}{_fmt_scalar(data)}")
    return lines


def _fmt_value(v):
    """Format a leaf value, including empty containers."""
    if isinstance(v, dict):
        return "{}"
    if isinstance(v, list):
        return "[]"
    return _fmt_scalar(v)


# --- Paths ------------------------------------------------------------------

def harness_root():
    """Return the absolute path to the harness root (the dir containing scripts/)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rpath(*parts):
    """Join parts under the harness root."""
    return os.path.join(harness_root(), *parts)


def load_config():
    return load_yaml(rpath("harness.config.yaml"))


# --- Registry ---------------------------------------------------------------

def registry_path(name):
    return rpath("registry", f"{name}.yaml")


def load_registry(name):
    return load_yaml(registry_path(name))


def save_registry(name, data):
    """Rewrite a registry file, preserving its leading comment header.

    Neither PyYAML's safe_dump nor the fallback writer keeps comments, and a
    registry rewrite was observed stripping the header in the field — so the
    header lines are captured before dumping and re-prepended after.
    """
    path = registry_path(name)
    header = []
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("#"):
                    header.append(line)
                else:
                    break
    dump_yaml(path, data)
    if header:
        with open(path, "r", encoding="utf-8") as fh:
            body = fh.read()
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("".join(header) + body)


def registry_add(name, key, entry):
    """Append `entry` to the list under `key` in registry `name`, deduped by name.

    Returns True if added, False if an entry with the same `name` already existed.
    """
    reg = load_registry(name)
    items = reg.setdefault(key, [])
    for it in items:
        if isinstance(it, dict) and it.get("name") == entry.get("name"):
            return False
    items.append(entry)
    save_registry(name, reg)
    return True


# --- Helpers ----------------------------------------------------------------

def slugify(text):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", str(text).strip().lower())
    return s.strip("-")


def copy_template(src_dir, dst_dir):
    """Copy a template directory tree to a new location. Refuses to overwrite."""
    if os.path.exists(dst_dir):
        raise FileExistsError(f"Target already exists: {dst_dir}")
    shutil.copytree(src_dir, dst_dir)


def replace_in_file(path, replacements):
    """Apply (old -> new) string replacements to a single file in place."""
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()
    for old, new in replacements.items():
        content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
