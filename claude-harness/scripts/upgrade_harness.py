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

"""Sync the universal layers of this harness from an upstream checkout.

Deployed harnesses (a clone adopted into some workspace via /harness-init)
drift from the source repo as the source improves. This script closes that
gap: it mirrors the UNIVERSAL layers from an upstream harness directory into
this one, and never touches the local-state layers.

  synced   : kernel/ protocols/ styles/ templates/ evaluation/ commands/
             scripts/ + HARNESS.md README.md
  preserved: projects/ sessions/ registry/ harness.config.yaml
             (plus anything outside the harness dir — bridge, workspace)

Mirroring is exact for the synced layers: upstream additions and changes are
copied in, and local files upstream no longer ships are deleted (reported
first). __pycache__/dotfiles are ignored. If the upstream config's `kernel:`
list differs from the local one, a warning explains what to reconcile by
hand (the local config is preserved, so a renamed kernel file needs a manual
config edit).

Dry-run by default — prints the full change list. Apply with --apply, then:
  python3 scripts/install_bridge.py   (regenerate bridge + hooks wiring)
  python3 scripts/validate_harness.py (must pass)

Usage:
    python3 scripts/upgrade_harness.py /path/to/upstream/claude-harness [--apply]
"""

from __future__ import annotations

import filecmp
import fnmatch
import os
import shutil
import sys

import _common as C

# Fallback only. The real contract is `distribution:` in harness.config.yaml,
# so this list and the one the validator enforces cannot drift apart again.
# They had: modes/ and scopes/ were missing here while being declared universal
# everywhere else, and KERNEL.md and ROUTING.md -- the only two files the bridge
# imports -- were never synced at all, so an upgrade left the spine stale.
_FALLBACK_DIRS = ["kernel", "protocols", "styles", "modes", "scopes",
                  "templates", "evaluation", "commands", "scripts", "tests",
                  "skills"]
_FALLBACK_TOP = ["KERNEL.md", "ROUTING.md", "HARNESS.md", "README.md"]
SKIP_NAMES = {"__pycache__"}


def _distribution(root):
    """The synced layers, from the config that declares them."""
    try:
        config = C.load_yaml(os.path.join(root, "harness.config.yaml")) or {}
        contract = config.get("distribution")
        # `distribution: 5` must fall back, not raise. Every other shape of
        # malformed config already did.
        if not isinstance(contract, dict):
            contract = {}
    except Exception:
        contract = {}
    dirs = contract.get("synced_dirs")
    files = contract.get("synced_files")
    return (
        list(dirs) if isinstance(dirs, list) and dirs else list(_FALLBACK_DIRS),
        list(files) if isinstance(files, list) and files else list(_FALLBACK_TOP),
    )


def _agent_specific(root):
    """Paths this harness owns outright, as fnmatch patterns.

    Read from the LOCAL config, unlike the synced set: which of its files are
    genuinely a different program is a fact about this harness, and upstream has
    no standing to overwrite the answer.
    """
    try:
        config = C.load_yaml(os.path.join(root, "harness.config.yaml")) or {}
        contract = config.get("distribution")
        if not isinstance(contract, dict):
            return []
        patterns = contract.get("agent_specific")
        return [str(item) for item in patterns] if isinstance(patterns, list) else []
    except Exception:
        return []


def _is_agent_specific(rel, patterns):
    return any(fnmatch.fnmatch(rel, pattern) for pattern in patterns)


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    apply_mode = "--apply" in args
    prune = "--prune" in args
    # For CI: report drift as a failure instead of as a dry-run summary.
    exit_on_drift = "--exit-on-drift" in args
    args = [a for a in args if a not in ("--apply", "--prune", "--exit-on-drift")]
    if len(args) != 1:
        print(__doc__)
        return 2
    upstream = os.path.abspath(args[0])
    local = C.harness_root()

    if not (os.path.isfile(os.path.join(upstream, "HARNESS.md"))
            and os.path.isdir(os.path.join(upstream, "kernel"))):
        print(f"FAIL  {upstream} does not look like a harness root "
              "(needs HARNESS.md + kernel/).")
        return 1
    if os.path.realpath(upstream) == os.path.realpath(local):
        print("FAIL  upstream and local are the same directory.")
        return 1

    # Read the contract from upstream: it is the side that knows what the new
    # shape is, and a deployment whose config predates a new layer would
    # otherwise never learn to sync it.
    sync_dirs, sync_top = _distribution(upstream)
    owned = _agent_specific(local)

    _report_versions(upstream, local)

    added, changed, removed = [], [], []
    for rel in _sync_targets(upstream, sync_dirs, sync_top):
        if _is_agent_specific(rel, owned):
            continue
        up, lo = os.path.join(upstream, rel), os.path.join(local, rel)
        if not os.path.isfile(lo):
            added.append(rel)
        elif not filecmp.cmp(up, lo, shallow=False):
            changed.append(rel)
    for rel in _sync_targets(local, sync_dirs, sync_top):
        if _is_agent_specific(rel, owned):
            continue
        if not os.path.isfile(os.path.join(upstream, rel)):
            removed.append(rel)

    if not (added or changed or removed):
        print("OK    already in sync with upstream — nothing to do.")
        return 0
    if exit_on_drift and (added or changed):
        for rel in added + changed:
            print(f"DRIFT   {rel}")
        print(f"\nFAIL  {len(added) + len(changed)} file(s) have drifted from "
              "upstream. Sync them, or declare them agent-specific in "
              "harness.config.yaml.")
        return 1

    for rel in added:
        print(f"ADD     {rel}")
    for rel in changed:
        print(f"UPDATE  {rel}")
    if prune:
        for rel in removed:
            print(f"REMOVE  {rel}  (upstream no longer ships it)")
    elif removed:
        # Listing every one buries the two lines that matter. A deployment that
        # skipped the skill prune has hundreds of these and none of them is news.
        shown = removed[:10]
        for rel in shown:
            print(f"EXTRA   {rel}  (local only)")
        if len(removed) > len(shown):
            print(f"EXTRA   … and {len(removed) - len(shown)} more local-only "
                  "files; --prune would delete them")

    _warn_kernel_list(upstream, local)

    if not apply_mode:
        tail = f"{len(removed)} remove" if prune else f"{len(removed)} local-only"
        print(f"\nDry run: {len(added)} add, {len(changed)} update, {tail}. "
              "Re-run with --apply to write.")
        return 0

    for rel in added + changed:
        dst = os.path.join(local, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(upstream, rel), dst)
    # Deleting is opt-in. Mirroring exactly meant an upgrade could silently
    # remove a script a deployment had added, and the default for a tool nobody
    # had ever run should not be the destructive one.
    for rel in (removed if prune else []):
        os.remove(os.path.join(local, rel))

    print(f"\nApplied: {len(added)} added, {len(changed)} updated, "
          f"{len(removed) if prune else 0} removed.")
    print("Now run:  python3 scripts/install_bridge.py  "
          "&&  python3 scripts/validate_harness.py")
    return 0


def _sync_targets(root, sync_dirs=None, sync_top=None):
    """Relative paths of all files in the synced layers under `root`."""
    if sync_dirs is None or sync_top is None:
        sync_dirs, sync_top = _distribution(root)
    rels = [t for t in sync_top if os.path.isfile(os.path.join(root, t))]
    for d in sync_dirs:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [n for n in dirnames
                           if n not in SKIP_NAMES and not n.startswith(".")]
            for fn in sorted(filenames):
                if fn.startswith(".") or fn.endswith((".pyc", ".pyo")):
                    continue
                rels.append(os.path.relpath(os.path.join(dirpath, fn), root))
    return rels


def _harness_version(root):
    try:
        config = C.load_yaml(os.path.join(root, "harness.config.yaml")) or {}
        harness = config.get("harness")
        return str((harness or {}).get("version") or "") if isinstance(harness, dict) else ""
    except Exception:
        return ""


def _report_versions(upstream, local):
    """Lead with the version delta. Knowing an upgrade exists is the part a
    deployment cannot work out for itself."""
    up, lo = _harness_version(upstream), _harness_version(local)
    if not (up or lo):
        return
    if up and lo and up == lo:
        print(f"version : {lo} (same as upstream)\n")
    else:
        print(f"version : {lo or '(unknown)'}  ->  upstream {up or '(unknown)'}\n")


def _warn_kernel_list(upstream, local):
    try:
        up = C.load_yaml(os.path.join(upstream, "harness.config.yaml"))
        lo = C.load_yaml(os.path.join(local, "harness.config.yaml"))
    except Exception:
        return
    up_k, lo_k = up.get("kernel", []), lo.get("kernel", [])
    if up_k != lo_k:
        print(f"\nWARN  upstream kernel list differs from local "
              f"harness.config.yaml (local config is preserved):")
        print(f"      upstream: {up_k}")
        print(f"      local   : {lo_k}")
        print("      Reconcile the local `kernel:` list by hand, then "
              "regenerate the bridge.")


if __name__ == "__main__":
    raise SystemExit(main())
