---
name: omnetpp-branch-rebase
description: >
  Rebase a topic branch of an OMNeT++-based simulation project onto a moved main branch,
  regression-free, using opp_repl tests: partition commits into groups, walk them across
  intermediate stages of main, validate each (group, stage) with scoped fingerprint and
  statistical tests, preserve every attempt as a forensic branch, and keep resumable state in
  a logbook. Use when asked to rebase a long-lived topic branch across a large upstream gap
  and opp_repl is available. For history cleanup without moving the base, use
  omnetpp-branch-cleanup.
---

# Branch rebase (opp_repl-based)

The full procedure is in [framework.md](framework.md): groups-times-stages incremental
rebase with safe points, four-baseline failure diagnosis, a never-rewrite/fix-commit-only
policy, and a state file that makes the process resumable from disk alone.

Related: omnetpp-branch-cleanup (reshaping history in place, base fixed), and the simpler
conflict tactics in omnetpp-git-workflow (incremental multi-step rebase,
intent-preserving conflict resolution).
