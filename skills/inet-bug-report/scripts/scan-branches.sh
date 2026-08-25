#!/usr/bin/env bash
# List recently active branches that change a given path, relative to origin/master.
# Catches an unfiled fix that the -S pickaxe misses because the fix reworded or moved the code.
#
# Usage:  scan-branches.sh [--no-fetch] <path> [<since-date>]
#   e.g.  scan-branches.sh src/inet/linklayer/ieee80211 2026-02-01
# Default window: 6 months. Fetches with --prune first, so that a branch deleted upstream is not
# reported as live; pass --no-fetch when offline or when you fetched a moment ago.
set -u
do_fetch=yes
[ "${1:-}" = "--no-fetch" ] && { do_fetch=no; shift; }
[ $# -ge 1 ] || { echo "usage: $0 [--no-fetch] <path> [<since-date, YYYY-MM-DD>]" >&2; exit 2; }
path="$1"
since="${2:-$(date -d '6 months ago' +%F 2>/dev/null || date -v-6m +%F)}"

# Run this INSIDE the checkout being investigated: every command below is relative to the cwd.
git rev-parse --git-dir >/dev/null 2>&1 || { echo "not inside a git checkout: $(pwd)" >&2; exit 1; }
git rev-parse --verify -q origin/master >/dev/null || {
    echo "no origin/master in $(git rev-parse --show-toplevel) -- run this inside the project you are" >&2
    echo "investigating, not inside the skill directory." >&2; exit 1; }

if [ "$do_fetch" = yes ]; then
    if ! timeout 120 git fetch --prune origin >/dev/null 2>&1; then
        echo "WARNING: git fetch --prune failed. Results may be stale, and a branch deleted"
        echo "         upstream may still be listed below. Say so in your report." >&2
    fi
fi

echo "branches touching '$path', active since $since, versus origin/master"
echo

scan() {  # $1 = refs glob, $2 = label
    git for-each-ref --sort=-committerdate "$1" \
        --format='%(committerdate:short) %(refname:short) %(authorname)' |
    awk -v s="$since" '$1>=s' |
    while read -r date ref author; do
        [ "$ref" = "origin/master" ] || [ "$ref" = "master" ] && continue
        n=$(git rev-list --count "origin/master..$ref" -- "$path" 2>/dev/null) || continue
        [ "${n:-0}" -gt 0 ] || continue
        printf '%s  %-55s %2s commit(s)  %s\n' "$date" "$ref" "$n" "$author"
        git log --oneline "origin/master..$ref" -- "$path" | head -5 | sed 's/^/        /'
        echo
    done
}

echo "########## remote topic branches ##########"
scan 'refs/remotes/origin/topic' 
echo "########## local branches (not visible to anyone else) ##########"
scan 'refs/heads'
echo "Inspect a candidate:  git diff origin/master...<branch> -- $path"
