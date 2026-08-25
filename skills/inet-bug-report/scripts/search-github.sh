#!/usr/bin/env bash
# Search a repository's issues and pull requests, open and closed, for every term given.
# Usage:  search-github.sh <term> [<term> ...]        (run inside the git checkout)
set -u
[ $# -ge 1 ] || { echo "usage: $0 <term> [<term> ...]" >&2; exit 2; }
# gh and git both resolve the repository from the cwd: run this INSIDE the checkout under
# investigation, not inside the skill directory.
git rev-parse --verify -q origin/master >/dev/null || {
    echo "no origin/master in $(pwd) -- run this inside the project you are investigating." >&2
    exit 1; }

for term in "$@"; do
    echo "=============================================================="
    echo "TERM: $term"
    echo "-------- issues (open and closed) --------"
    gh issue list --state all --search "$term" --limit 15 \
        --json number,state,title,updatedAt \
        --template '{{range .}}{{.number}}  {{.state}}  {{.title}}  ({{timeago .updatedAt}}){{"\n"}}{{end}}' \
        2>&1 | grep -v '^GraphQL: Projects' || true
    echo "-------- pull requests (open and closed) --------"
    gh pr list --state all --search "$term" --limit 15 \
        --json number,state,title,updatedAt \
        --template '{{range .}}{{.number}}  {{.state}}  {{.title}}  ({{timeago .updatedAt}}){{"\n"}}{{end}}' \
        2>&1 | grep -v '^GraphQL: Projects' || true
    echo "-------- commits on master --------"
    git log --oneline --grep "$term" -i origin/master 2>/dev/null | head -10
    echo
done
