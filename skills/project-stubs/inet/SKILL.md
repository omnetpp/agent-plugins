---
name: inet
description: >
  Entry point for developing the INET Framework in this repository: which AI skills apply
  here, how to obtain them, always-on basics, and the plans workflow. Use at the start of any
  INET development task (coding, testing, refactoring, preparing a branch or PR) before
  reaching for individual skills.
---

# INET Framework — skill routing

<!-- Master copy lives in the shared skills repo under project-stubs/inet/;
     install into the INET repo as .claude/skills/inet/SKILL.md. -->

## Get the shared skills

The detailed skills live in the shared skills repo (**TODO: final URL**, e.g.
`github.com/omnetpp/ai-skills`). If
`~/.claude/skills/omnetpp-fingerprint-testing` does not exist, they are not
installed — clone the repo and run its `./install.sh`, then continue.

## Which skills apply here

`omnetpp-*` (platform + shared workflows) and `inet-*` (INET specifics —
these AUGMENT the corresponding `omnetpp-*` skill and WIN on conflict).
`simu5g-*` does not apply. By task:

| Task | Skills |
|---|---|
| Environment, building, worktrees | inet-dev-environment |
| Fingerprint tests | omnetpp-fingerprint-testing + inet-fingerprint-testing |
| Module / unit / protocol tests | inet-test-suites |
| Statistical baselines | inet-statistical-tests |
| Writing/porting module code | omnetpp-coding-conventions + inet-module-development |
| Refactoring | omnetpp-model-refactoring |
| Git, commits, rebases, PRs | omnetpp-git-workflow |
| Branch cleanup / big rebase | inet-branch-cleanup (CLI) or omnetpp-branch-cleanup / omnetpp-branch-rebase (opp_repl) |
| Debugging a sim | omnetpp-sim-debugging (+ omnetpp-model-development for flags) |
| Cosmetic code cleanup | inet-cosmetic-cleanup |
| Release notes / showcases / RST | inet-release-notes, inet-showcase-creator, rst-editing |

## Always-on basics

- Build from the **toplevel** project directory, never `src/`; build BOTH
  `make -j$(nproc)` (release) and `make MODE=debug -j$(nproc)` after C++
  changes (see inet-dev-environment for why).
- Start every shell command block with `source ./setenv -q` from the project
  root and verify `$INET_ROOT` points at THIS checkout.
- Develop on a topic branch in the main checkout, not in tool-managed
  worktrees.
- Commit subjects: `Area: category: description` (categories: fix / refactor /
  feature / test; omit when obvious from the wording). Apply as a final
  message-only pass when history is otherwise final.
- Run simulations via `inet` / `inet_dbg`, never `opp_run` directly.

## Plans workflow

Keep design/implementation plans as Markdown files in the `plans` folder of
the `ai-logs` repo (git@github.com:omnetpp/ai-logs.git, normally checked out
as a sibling of `inet/`), status-by-folder: new plans in `plan/pending/`,
completed ones moved to `plan/done/`. Name plans
`YYYY-MM-DD_short-title.md`. While implementing: work incrementally, commit
per completed step, mark progress in the plan, and record actual design
decisions and discoveries back into it.
