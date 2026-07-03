#!/usr/bin/env bash
# Symlink every skill in this repo into the agent's skills directory
# (default: ~/.claude/skills) so skill descriptions are auto-loaded.
set -eu

REPO_DIR=$(cd "$(dirname "$0")" && pwd)
TARGET=${1:-"$HOME/.claude/skills"}
mkdir -p "$TARGET"

for dir in "$REPO_DIR"/*/; do
    name=$(basename "$dir")
    [ "$name" = "project-stubs" ] && continue   # masters for per-repo skills, not installed here
    [ -f "$dir/SKILL.md" ] || continue
    if [ -e "$TARGET/$name" ] && [ ! -L "$TARGET/$name" ]; then
        echo "SKIP $name: $TARGET/$name exists and is not a symlink (remove it manually to adopt the repo version)" >&2
        continue
    fi
    ln -sfn "${dir%/}" "$TARGET/$name"
    echo "linked $name"
done
