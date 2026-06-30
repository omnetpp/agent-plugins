#!/usr/bin/env bash
# find-smells.sh — first-pass detector of cosmetic smells in INET C++ source files.
# Usage: find-smells.sh <file.cc|file.h> [more files...]
#
# Output is a list of CANDIDATES for human review, not an authoritative fix list.
# Triage each by scope tier (see SKILL.md) before changing anything.
set -u

[ "$#" -ge 1 ] || { echo "usage: $0 <file> [file...]" >&2; exit 2; }

for f in "$@"; do
    [ -f "$f" ] || { echo "skip (not a file): $f" >&2; continue; }
    echo "================================================================"
    echo "FILE: $f"
    echo "================================================================"

    echo
    echo "--- [1] NAMING: identifiers with a 3+ uppercase run + a lowercase letter ---"
    echo "    (e.g. TCPSendBuffer, CNAddress, IPv6Address; ALL_CAPS constants are excluded."
    echo "     'count  identifier' — review each and classify by scope tier.)"
    grep -oE '\b[A-Za-z_][A-Za-z0-9_]*\b' "$f" \
        | grep -E '[A-Z]{3,}' \
        | grep -E '[a-z]' \
        | sort | uniq -c | sort -rn \
        | head -80

    echo
    echo "--- [2] LOG NOISE: decoration in EV/ev log statements (<<< >>> === ### *** ~~~ +++ ___) ---"
    grep -nE '(EV[_A-Z]*|ev)[[:space:]]*<<.*(<<<|>>>|===|###|\*\*\*|~~~|\+\+\+|___)' "$f" | head -60

    echo
    echo "--- [3a] COMMENTED-OUT CODE: // followed by a statement ending in ; { or } ---"
    grep -nE '^[[:space:]]*//[[:space:]]*[A-Za-z_].*[;{}][[:space:]]*$' "$f" | head -80

    echo
    echo "--- [3b] COMMENTED-OUT LOG / DEBUG lines (// or /* ... */) ---"
    grep -nE '(^[[:space:]]*//|/\*)[[:space:]]*(EV[_A-Z]*|ev|bubble|printf|cout|std::cout|WATCH)\b' "$f" | head -40

    echo
    echo "--- [3c] BLOCK-COMMENT dead code: single-line /* ... ; ... */ (likely commented statement) ---"
    grep -nE '/\*([^*]|\*[^/])*;([^*]|\*[^/])*\*/' "$f" | head -40

    echo
    echo "--- [4a] ERROR MESSAGES ending in ! or . (drop trailing punctuation; fix typos) ---"
    grep -nE '(throw|cRuntimeError|cException|opp_error|ASSERT)\b.*[!.]"' "$f" | head -40

    echo
    echo "--- [4b] CONTEXT-FREE cRuntimeError (bare literal, no interpolated value) ---"
    echo "    (add the offending value + what operation was underway via printf-style args)"
    grep -nE 'cRuntimeError\("[^"%]*"[[:space:]]*\)' "$f" | head -40

    echo
    echo "--- [5] ANGRY / emotional comments (!?!? runs, or long SHOUTING in a comment) ---"
    grep -nE '//.*([!?]{2,}|[!?][[:space:]]*[!?])' "$f" | head -30
    grep -nE '//[[:space:]]*[A-Z][A-Z ]{10,}' "$f" | head -20

    echo
    echo "--- [6] TAUTOLOGICAL trailing comments (heuristic — judge each; delete the obvious ones) ---"
    grep -nE ';[[:space:]]*//[[:space:]]*(free|frees|freeing|delete|deletes|deleting|return|returns|increment|decrement|loop|set|get|create|creates|add|adds|remove|removes|clear|clears|init|initialize)\b' "$f" | head -30

    echo
    echo "(MANUAL scan still needed for: multi-line /* ... */ commented-out code blocks — distinguish"
    echo " these from genuine RFC/standard excerpts and explanatory comments, which are KEPT; and for"
    echo " logs whose whole content is decoration / 'entered function X' tracing — those are deletions,"
    echo " not reformats.)"
    echo
done
