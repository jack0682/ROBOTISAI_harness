#!/bin/sh
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

# Drop this harness into a workspace and put it in force there.
#
#   ./bootstrap.sh /path/to/your/workspace
#
# Copies the harness layer into the workspace, generates the Claude Code bridge
# (CLAUDE.md + .claude/) at the workspace root, installs the commit gates, and
# validates. The workspace keeps its own git; this clone's git is never touched.
#
# Re-running is safe: the bridge is regenerated, hand-edited rules are kept, and
# existing harness state (sessions/, memory/, projects/) is left alone unless
# --fresh is given.

set -eu

SRC="$(cd "$(dirname "$0")" && pwd)"
FRESH=0
TARGET=""

usage() {
  cat >&2 <<EOF
usage: ./bootstrap.sh <workspace-dir> [--fresh]

  <workspace-dir>  where the harness should take effect. Gets CLAUDE.md,
                   .claude/ and claude-harness/.
  --fresh          also reset sessions/, memory/ and projects/ in the target,
                   for a workspace starting clean. Refuses to run unprompted
                   over an existing deployment's state.
EOF
  exit 2
}

while [ $# -gt 0 ]; do
  case "$1" in
    --fresh) FRESH=1 ;;
    -h|--help) usage ;;
    -*) echo "unknown option: $1" >&2; usage ;;
    *) [ -z "$TARGET" ] || usage; TARGET="$1" ;;
  esac
  shift
done

[ -n "$TARGET" ] || usage
[ -d "$TARGET" ] || { echo "not a directory: $TARGET" >&2; exit 1; }

TARGET="$(cd "$TARGET" && pwd)"
[ "$TARGET" != "$SRC" ] || {
  echo "refusing to bootstrap the template into itself." >&2; exit 1; }

command -v python3 >/dev/null 2>&1 || {
  echo "python3 is required and was not found." >&2; exit 1; }

echo "harness  : $SRC"
echo "workspace: $TARGET"
echo

# 1. The harness layer, plus the files the commit gates need.
echo "→ copying the harness layer"
mkdir -p "$TARGET/claude-harness"
tar -C "$SRC" -cf - \
    --exclude='.git' --exclude='__pycache__' --exclude='.pytest_cache' \
    claude-harness .githooks .gitmessage LICENSE CONTRIBUTING.md \
  | tar -C "$TARGET" -xf -

if [ "$FRESH" -eq 1 ]; then
  echo "→ resetting deployment-local state (--fresh)"
  rm -rf "$TARGET/claude-harness/analysis"
  find "$TARGET/claude-harness/sessions" -name '*.md' \
       ! -name 'README.md' ! -name '_session_template.md' -delete 2>/dev/null || true
  rm -f "$TARGET/claude-harness/sessions/.audit.log"
  find "$TARGET/claude-harness/memory/claims" -name '*.md' \
       ! -name 'README.md' ! -name '_claim_template.md' -delete 2>/dev/null || true
  find "$TARGET/claude-harness/projects" -mindepth 1 -maxdepth 1 -type d \
       ! -name '_project_template' -exec rm -rf {} + 2>/dev/null || true
  printf 'projects:\n- name: _project_template\n  path: projects/_project_template\n  status: template\n  skills: []\n' \
    > "$TARGET/claude-harness/registry/projects.yaml"
fi

# 1b. Sever any dependency on the template's git.
#
# A workspace copy can never push here -- it is somebody else's repository --
# so leaving the remote in place only invites an attempt that costs tokens and
# ends in a permission error. If the target was produced by cloning the
# template rather than by copying into an existing project, its origin is this
# template; that is removed. A workspace with its own origin is left alone.
TEMPLATE_URL_FRAGMENT="ROBOTISAI_harness"
if [ -d "$TARGET/.git" ]; then
  ORIGIN="$(cd "$TARGET" && git remote get-url origin 2>/dev/null || true)"
  case "$ORIGIN" in
    *"$TEMPLATE_URL_FRAGMENT"*)
      echo "→ severing the template remote ($ORIGIN)"
      ( cd "$TARGET" && git remote remove origin )
      echo "  this workspace is now standalone; it cannot and should not push upstream."
      ;;
  esac
fi

# 1c. First-run marker: the session hook reads this and asks for a full
#     workspace analysis before any other work. Removed by /harness-init.
printf '%s\n' \
  "Bootstrapped $(date -u +%Y-%m-%dT%H:%M:%SZ). The workspace has not been" \
  "analyzed yet and no project overlay is registered. Run /harness-init." \
  > "$TARGET/claude-harness/.bootstrap-pending"

# 2. The bridge: CLAUDE.md + .claude/ at the workspace root.
echo "→ generating the Claude Code bridge"
( cd "$TARGET" && python3 claude-harness/scripts/install_bridge.py )

# 3. Commit gates, when the workspace is a git repo.
echo
if [ -d "$TARGET/.git" ] || ( cd "$TARGET" && git rev-parse --git-dir >/dev/null 2>&1 ); then
  ( cd "$TARGET" \
    && git config --local core.hooksPath .githooks \
    && git config --local commit.gpgsign true \
    && git config --local tag.gpgsign true \
    && git config --local commit.template .gitmessage )
  chmod +x "$TARGET/.githooks/"* 2>/dev/null || true
  echo "→ commit gates installed (core.hooksPath=.githooks, gpgsign=true)"
  if ! ( cd "$TARGET" && git config --local --get user.email >/dev/null 2>&1 ); then
    cat <<'EOF'

  ⚠  This workspace has no repository-local signing identity yet, so commits
     are blocked until you set one. A global identity is deliberately not
     inherited. Set yours:

       git config --local user.name       "Your Name"
       git config --local user.email      "you@robotis.com"
       git config --local user.signingkey <YOUR_GPG_KEY_ID>

     See CONTRIBUTING.md.
EOF
  fi
else
  echo "→ workspace is not a git repository; commit gates copied but not wired."
  echo "  After 'git init', run:  git config --local core.hooksPath .githooks"
fi

# 4. Prove it.
echo
echo "→ validating"
( cd "$TARGET" && python3 claude-harness/scripts/validate_harness.py )

cat <<EOF

Done. The harness is in force in $TARGET.

  Next:  open Claude Code in that workspace and run  /harness-init
         to register the project overlay for it.
EOF
