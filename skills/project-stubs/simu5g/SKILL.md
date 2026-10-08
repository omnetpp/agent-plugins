---
name: simu5g
description: >
  Entry point for developing Simu5G in this repository: which AI skills apply here, Simu5G
  architecture red lines, and local build/run specifics. Use at the start of any Simu5G
  development task (coding, testing, refactoring, rebasing) before reaching for individual
  skills.
---

# Simu5G — skill routing and project rules

<!-- Master copy lives in the shared skills repo under project-stubs/simu5g/;
     install into the Simu5G repo as .claude/skills/simu5g/SKILL.md. -->

## Get the shared skills

The detailed skills live in the shared skills repo (**TODO: final URL**). If
`~/.claude/skills/omnetpp-fingerprint-testing` does not exist, clone the repo
and run its `./install.sh`, then continue.

## Which skills apply here

- `omnetpp-*` — platform mechanics and shared workflows (fingerprint
  concepts, coding conventions, refactoring, git workflow, debugging).
- `simu5g-*` — Simu5G specifics; these AUGMENT the corresponding `inet-*`
  and `omnetpp-*` skills and WIN on any conflict.
- `inet-*` — the baseline for conventions and idioms Simu5G does not regulate
  itself; INET's repo mechanics (runner flags, INET_ROOT, baseline paths) do
  not carry over literally. Precedence and the per-skill mapping are in
  `simu5g-dev`.

Key pairs: fingerprints → `omnetpp-fingerprint-testing` +
`simu5g-fingerprint-testing`; refactoring → `omnetpp-model-refactoring`
(+ per-step fingerprint gate); git → `omnetpp-git-workflow`.

## Architecture red lines (3GPP-mandated Control/Data Plane separation)

- **Control Plane** = RRC and its submodules (e.g. `BearerManagement`) in the
  NIC. It CONFIGURES the Data Plane (entity setup/teardown). Processing data
  packets in Control Plane code is STRICTLY FORBIDDEN. Control Plane entities
  communicate via C++ method calls, NOT packets — adding gates to
  `BearerManagement` is a strict no.
- **Data Plane** = everything else in the NIC outside RRC. It processes data
  packets SOLELY; configuration-changing code (e.g. `deleteEntities()`) does
  not belong there — that is Control Plane (likely BearerManagement) work.

## Local build/run specifics

- Build: `make MODE=debug -j12` (debug builds with parallelism).
- Run: `simu5g_dbg` is in `$PATH` (don't search for it); ini file is a
  positional argument; `-c <ConfigName>`, `-u Cmdenv`. Set the working
  directory via the tool's cwd parameter rather than `cd` in the command.
  Example: `simu5g_dbg -u Cmdenv -c VoIP-DL-MultiQfi omnetpp_drb.ini`
- Multi-step refactoring gate (per step): compile debug → commit → run
  fingerprint suite → do NOT proceed until green; never update fingerprint
  baselines without explicit user consent.
