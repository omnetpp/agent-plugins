# The resource policy

Most control is static: the routing table names the default team, and this
file names the model tier and the token target. The resource manager audits
rarely; it does not sit in the loop.

## Model tiers

| Tier | Use it for |
|---|---|
| opus | Architecture, design, review, audits, standards questions, non-trivial debugging, synthesis |
| sonnet | Builds, searches, log scans, sweeps, repetitive edits, test and fingerprint runs, plots |

A role's default tier is in its frontmatter. Escalation takes one stated
sentence of reason; de-escalation needs none.

## Token targets

The targets stand in the routing table (`routing.md`), one per task class,
from 10k for a Question to 600k for an Architecture refactoring. A target is
a signal, not a wall: past the target, the lead tells the program manager,
and the program manager decides — finish, narrow, or stop — and records the
overrun in `ai-logs/simu5g-spend.md`.

## Context hygiene

1. Grep before read; read the section, not the file.
2. Run the narrowest thing that proves the step. The full fingerprint suite
   runs when the plan says so, not by habit; narrow it with the runner's
   `-m` filter — which matches substrings, not regexes.
3. Every long run gets a timeout and writes to a file inside the repository;
   the return quotes counts and the first real error, never the log.
4. Build output goes to a file. A green build returns one line.
5. Never one process per config when one process can sweep.
6. Background runs use absolute paths.
7. Never re-derive a fact the conversation already states.
