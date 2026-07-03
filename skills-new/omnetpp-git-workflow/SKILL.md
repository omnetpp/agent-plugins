---
name: omnetpp-git-workflow
description: >
  Git conventions and discipline for OMNeT++-family simulation projects: safe staging (never
  git add -A), green-at-every-commit for multi-step work, backup tags before history rewrites,
  incremental rebase tactics, intent-preserving conflict resolution, and integrating
  third-party PRs with RFC review plus dynamic proof. Use for any commit, rebase,
  cherry-pick, branch reorganization, or PR-integration work in these projects. Commit-subject
  formats are project-specific — see the project's entry-point skill.
---

# Git workflow

## Hard rules

- **NEVER perform destructive git operations** (reset, rebase, force push,
  history rewrites) without explicit user consent.
- **NEVER use `git add -A` or `git commit -a`** — repos contain unrelated
  untracked files. Stage with `git add -u` (tracked, changed files) plus
  `git add <file>` for files YOU created, then commit.
- Disable pagers/editors in scripted use: `GIT_PAGER=cat`, `GIT_EDITOR=true`.
- Before any history rewrite, tag the original tip
  (`git tag <branch>-orig`) so the pre-rewrite state stays reachable.
- Use `git mv` for renames (preserves history); update `#include`s and header
  guards, and grep for references first.

## Green at every commit

For multi-step work (refactorings, ports, feature branches meant for review),
each commit must: build cleanly (all relevant build modes) and pass the
relevant test suites — for behavior-preserving steps, with byte-identical
fingerprints. Commit after each completed step; don't batch. Any commit that
legitimately changes recorded test baselines updates them *in the same commit*
and explains the change in the message (per-ingredient, for fingerprints).
Commit-subject conventions differ per project (e.g. INET's
`Area: category: description`) — apply them as a final message-only rewrite
pass when the history is otherwise final, so intermediate rebases don't
invalidate the wording.

## Rebase tactics

- **Try the rebase before assuming conflicts** — even a large branch over a
  much-moved base rebases clean when the touched regions are disjoint.
- When a rebase hits many hard conflicts, do NOT fight through to the top of
  the base branch in one jump: perform multiple smaller rebases, each
  advancing over a few base commits, until reaching the top. When facing
  difficulties mid-rebase, STOP and recommend this to the user.
- Cherry-picking is weaker than rebase (it doesn't track file renames/moves).
  When a cherry-pick conflicts, try rebase instead — it may succeed without
  manual resolution.
- Conflict-resolution mindset: understand the INTENT of the original commit
  and re-apply that intent on the current code — preserve what the commit
  meant, not its exact text.
- For heavyweight jobs there are dedicated skills: omnetpp-branch-cleanup
  (reshape a branch's history in place) and omnetpp-branch-rebase
  (cross a large upstream gap in validated stages).

## Integrating third-party PRs

- Rebase the PR onto current master first.
- Evaluate every reviewer comment explicitly (valid bug / design critique /
  audit request) and fix the real ones as small, behavior-preserving commits.
  A fix commit may be folded into the contributor's commit if a squashed
  history is preferred.
- Review protocol code against the standard: a static read citing RFC/spec
  section numbers, marking deliberate simplifications as such — PLUS a
  **dynamic proof**: run the scenario and confirm the claimed mechanism in
  the log (e.g. the expected routing-table change at the expected time).
- Add a targeted example or test for any code path that fired zero times in
  existing scenarios, and verify regression guards actually fail without the
  fix.
- Run the full relevant test suites before declaring the integration done.
