#!/usr/bin/env python3
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

"""Gemini independent-review MCP server (stdlib-only, stdio JSON-RPC).

Exposes Google Gemini (a non-Claude model family) as an independent reviewer that
the Claude executor can call to cross-check its own work — proofs, derivations,
code, claims. This is the third reviewer family alongside the Claude executor and
the GPT reviewers (codex / oracle), giving the harness genuine cross-family
verification for `kernel/verification_authority.md` ("quality verdicts need a
check independent of what produced the work").

Independence is the CALLER's responsibility: pass the raw artifacts (file paths)
and the review objective, never a Claude-side summary or recommendation
(`skills/shared-references/reviewer-independence.md`). This server forwards the
material to Gemini verbatim and returns Gemini's verdict unaltered.

Transport: newline-delimited JSON-RPC 2.0 over stdio (the MCP stdio transport).
No third-party dependencies — runs under the system python3, offline-safe, no
launch-time package resolution. Backed by the `gemini` CLI (non-interactive
`-p` mode), which must be installed and authenticated.

Register:
    claude mcp add gemini-review -s user -- python3 \
        <harness>/claude-harness/mcp-servers/gemini-review/server.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

SERVER_NAME = "gemini-review"
SERVER_VERSION = "0.1.0"
DEFAULT_PROTOCOL = "2025-06-18"

# Guards so a runaway artifact can't blow up the prompt or hang the call.
MAX_FILE_BYTES = 500_000
MAX_TOTAL_BYTES = 1_500_000
GEMINI_TIMEOUT_S = 300

TOOL = {
    "name": "review",
    "description": (
        "Get an independent review from Google Gemini (a non-Claude model "
        "family) — for cross-checking a proof, derivation, code, or claim "
        "without contaminating the reviewer with Claude's own framing. Pass the "
        "review objective/rubric as `prompt` and the artifacts to review as "
        "absolute file paths in `files`; the server reads them and submits the "
        "raw content to Gemini. Keep `prompt` to the role + objective + the "
        "output you want; do NOT pre-digest, summarize, or hint at your own "
        "conclusion (that re-imports the blind spot independence exists to "
        "escape)."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "The review objective / role / rubric / desired "
                               "output. Raw and un-leading; no Claude-side "
                               "summary or recommendation.",
            },
            "files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Absolute paths of the artifacts to review. Their "
                               "raw contents are passed to Gemini verbatim.",
            },
            "model": {
                "type": "string",
                "description": "Optional Gemini model id (e.g. 'gemini-2.5-pro'). "
                               "Omit to use the gemini CLI default.",
            },
        },
        "required": ["prompt"],
    },
}


def _read_files(paths):
    """Return (blocks, notes). Each block is a delimited raw file dump."""
    blocks, notes, total = [], [], 0
    for p in paths or []:
        if not os.path.isabs(p):
            notes.append(f"[skipped non-absolute path: {p}]")
            continue
        if not os.path.isfile(p):
            notes.append(f"[missing file: {p}]")
            continue
        try:
            data = open(p, "r", encoding="utf-8", errors="replace").read()
        except OSError as exc:
            notes.append(f"[unreadable: {p} ({exc})]")
            continue
        if len(data.encode("utf-8", "replace")) > MAX_FILE_BYTES:
            data = data[:MAX_FILE_BYTES] + "\n[...truncated...]"
            notes.append(f"[truncated to {MAX_FILE_BYTES} bytes: {p}]")
        total += len(data)
        if total > MAX_TOTAL_BYTES:
            notes.append(f"[total content cap reached; later files dropped at {p}]")
            break
        blocks.append(f"===== FILE: {p} =====\n{data}\n===== END {p} =====")
    return blocks, notes


def _run_review(args):
    prompt = (args or {}).get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        return True, "error: 'prompt' is required and must be a non-empty string."
    files = (args or {}).get("files") or []
    model = (args or {}).get("model")

    blocks, notes = _read_files(files)
    payload = prompt.strip()
    if blocks:
        payload += "\n\n" + "\n\n".join(blocks)

    cmd = ["gemini", "-o", "text"]
    if isinstance(model, str) and model.strip():
        cmd += ["-m", model.strip()]
    cmd += ["-p", "Provide your independent review based strictly on the material "
                  "above. Do not assume facts not present in it; flag anything you "
                  "cannot verify."]
    try:
        r = subprocess.run(cmd, input=payload, capture_output=True, text=True,
                           timeout=GEMINI_TIMEOUT_S)
    except FileNotFoundError:
        return True, ("error: `gemini` CLI not found on PATH. Install it and "
                      "authenticate (`gemini` once interactively).")
    except subprocess.TimeoutExpired:
        return True, f"error: gemini review timed out after {GEMINI_TIMEOUT_S}s."

    out = (r.stdout or "").strip()
    if r.returncode != 0 and not out:
        tail = (r.stderr or "").strip().splitlines()[-5:]
        return True, "error: gemini exited %d.\n%s" % (r.returncode, "\n".join(tail))

    header = "[Independent review — Google Gemini%s]" % (
        f" ({model})" if model else "")
    note_str = ("\n[notes: " + "; ".join(notes) + "]") if notes else ""
    return False, f"{header}{note_str}\n\n{out}"


# --- JSON-RPC plumbing ------------------------------------------------------

def _send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def _result(req_id, result):
    _send({"jsonrpc": "2.0", "id": req_id, "result": result})


def _error(req_id, code, message):
    _send({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}})


def _handle(msg):
    method = msg.get("method")
    req_id = msg.get("id")
    is_request = req_id is not None

    if method == "initialize":
        params = msg.get("params") or {}
        proto = params.get("protocolVersion") or DEFAULT_PROTOCOL
        _result(req_id, {
            "protocolVersion": proto,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        })
    elif method == "tools/list":
        _result(req_id, {"tools": [TOOL]})
    elif method == "tools/call":
        params = msg.get("params") or {}
        if params.get("name") != TOOL["name"]:
            _error(req_id, -32602, f"unknown tool: {params.get('name')}")
            return
        is_err, text = _run_review(params.get("arguments") or {})
        _result(req_id, {"content": [{"type": "text", "text": text}],
                         "isError": is_err})
    elif method == "ping":
        _result(req_id, {})
    elif method and method.startswith("notifications/"):
        pass  # notifications get no response
    elif is_request:
        _error(req_id, -32601, f"method not found: {method}")
    # else: a notification we don't handle — ignore silently


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        try:
            _handle(msg)
        except Exception as exc:  # never die on one bad message
            rid = msg.get("id") if isinstance(msg, dict) else None
            if rid is not None:
                _error(rid, -32603, f"internal error: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
