---
name: inet
description: >
  Entry point for developing the INET Framework in this repository: which AI skills apply
  here, how to install them, always-on basics, and the plans workflow. Use at the start of any
  INET development task (coding, testing, refactoring, preparing a branch or PR) before
  reaching for individual skills.
---

# INET Framework — skill routing

<!-- Master copy lives in the shared skills repo under project-stubs/inet/;
     install into the INET repo as .claude/skills/inet/SKILL.md. -->

## Get the plugins

The detailed skills come from the OMNeT++ agent plugins (marketplace `omnetpp`,
github.com/omnetpp/ai-config). If the `inet-fingerprint-testing` skill is not available,
they are not installed. Tell the user to install them (Claude Code):

```bash
claude plugin marketplace add omnetpp/ai-config
claude plugin install inet@omnetpp
```

`inet` brings `omnetpp` and `omnetpp-dev` along. Other agents: see the README of
that repository.

## Which skills apply here

`dev-*` (universal rules), `omnetpp-model-*` and `omnetpp-tooling` (simulation-model
mechanics and shared workflows) and `inet-*` (INET specifics — these AUGMENT the
corresponding `omnetpp-model-*` skill and WIN on conflict). `simu5g-*` does not apply.
By task:

| Task | Skills |
|---|---|
| Environment, building, worktrees | inet-dev-environment |
| Fingerprint tests | omnetpp-model-fingerprint-testing + inet-fingerprint-testing |
| Module / unit / protocol tests | inet-test-suites |
| Statistical baselines | inet-statistical-tests |
| Writing/porting module code | omnetpp-model-coding-conventions + inet-module-development |
| Refactoring | omnetpp-model-refactoring |
| Designing a feature, writing a plan | dev-design |
| Git, commits, rebases, PRs | dev-git-workflow + dev-commit-messages + omnetpp-model-git-workflow |
| Branch cleanup / big rebase | inet-branch-cleanup (CLI) or omnetpp-model-branch-cleanup / omnetpp-model-branch-rebase (opp_repl) |
| Debugging a sim | omnetpp-model-debugging (+ omnetpp-model-development for flags) |
| Cosmetic code cleanup | inet-cosmetic-cleanup |
| Querying or checking NED/MSG/INI files | omnetpp-tooling |
| NED documentation (neddoc) | omnetpp-model-doc-generation |
| Release notes / showcases | inet-release-notes, inet-showcase-creator |

## Always-on basics

- Build from the **toplevel** project directory, never `src/`; build debug
  only, `make MODE=debug -j$(nproc)`, after C++ changes, and test in debug
  mode only (see inet-dev-environment; CI tests release).
- Start every shell command block with `source ./setenv -q` from the project
  root and verify `$INET_ROOT` points at THIS checkout.
- Develop on a topic branch in the main checkout, not in tool-managed
  worktrees.
- Commit subjects follow dev-commit-messages. Apply them as a final
  message-only pass when history is otherwise final.
- Run simulations via `inet` / `inet_dbg`, never `opp_run` directly.

## Plans workflow

Keep design/implementation plans as Markdown files in a plans repo outside the INET
checkout; its location comes from the user's own instructions (ask if none names it).
Status by folder: new plans in `plans/pending/`, completed ones moved to `plans/done/`.
Name plans `YYYY-MM-DD_short-title.md`. While implementing: work incrementally, commit
per completed step, mark progress in the plan, and record actual design decisions and
discoveries back into it.
