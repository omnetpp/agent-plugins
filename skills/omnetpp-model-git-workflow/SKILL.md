---
name: omnetpp-model-git-workflow
description: >
  Git workflow additions for OMNeT++-based simulation-model projects (INET,
  Simu5G, user models): fingerprint-identical commits for behavior-preserving
  steps, per-ingredient justification of baseline changes, the dedicated skills
  for heavyweight branch cleanup and rebases, and reviewing third-party protocol
  code against the standard with a dynamic proof. Use together with
  dev-git-workflow for commit, rebase, branch-reorganization or PR-integration
  work in simulation-model projects.
---

# Git workflow for simulation models

Applies on top of dev-git-workflow; read that first. This skill only adds what
is specific to simulation models.

## Green at every commit

- Behavior-preserving steps keep the fingerprints byte-identical (see
  omnetpp-model-fingerprint-testing).
- A commit that legitimately changes fingerprint baselines explains the change
  per ingredient in its message.

## Heavyweight history work

- omnetpp-model-branch-cleanup: reshape a branch's history in place.
- omnetpp-model-branch-rebase: cross a large upstream gap in validated stages.

## Integrating third-party PRs of protocol models

- Review protocol code against the standard: a static read citing RFC/spec
  section numbers, marking deliberate simplifications as such — PLUS a
  **dynamic proof**: run the scenario and confirm the claimed mechanism in
  the log (e.g. the expected routing-table change at the expected time).
