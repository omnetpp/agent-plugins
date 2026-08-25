#!/usr/bin/env bash
# Search a repository's issues and pull requests, open and closed, for every term given.
# Usage:  search-github.sh <term> [<term> ...]        (run inside the git checkout)
set -u
[ $# -ge 1 ] || { echo "usage: $0 <term> [<term> ...]" >&2; exit 2; }

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
