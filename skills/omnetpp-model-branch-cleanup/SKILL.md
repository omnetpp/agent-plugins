---
name: omnetpp-model-branch-cleanup
description: >
  Clean up a topic branch of an OMNeT++-based simulation project into a reviewable history
  using opp_repl-driven regression testing (fingerprint + statistical tests, dependency-scoped):
  recompose the total diff into typed commits (refactor/fix/feature), validate each against the
  test oracle, and prove nothing was lost via a coverage ledger. Use when asked to clean up,
  reorganize, or validate a feature/topic branch and opp_repl is available. For rebasing onto a
  moved main branch use omnetpp-model-branch-rebase; for the INET CLI-based playbook see
  inet-branch-cleanup.
---

# Branch cleanup (opp_repl-based)

Two procedures, by rigor:

- [interactive-walkthrough.md](interactive-walkthrough.md) — the lighter, interactive
  per-patch procedure: cherry-pick each commit, run dependency-scoped fingerprint +
  statistical tests, confirm each step with the user. Start here for ordinary branches.
- [framework.md](framework.md) — the full framework with free hunk-level recomposition,
  typed output commits (a refactor MUST leave fingerprints identical; a fix/feature may
  change them only with an in-commit baseline update and explanation), a coverage ledger
  proving the recomposition is lossless, and a resumable state file. Use for large or
  messy branches where commit boundaries must be redrawn.

Both assume opp_repl (fingerprint/statistical test stores, dependency store for scoping).
The final state of the cleaned branch must be byte-identical to the original topic branch
(modulo explained baseline updates); the original branch is never rewritten.
