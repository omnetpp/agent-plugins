---
name: omnetpp
description: >
  Entry point for developing OMNeT++ itself in this repository (simulation kernel, envir,
  nedxml, user interfaces, IDE, tools, documentation): which AI skills apply here and how
  to obtain them. Use at the start of any OMNeT++ development task (designing, planning,
  implementing, testing, committing, preparing a branch or a release) before reaching for
  individual skills.
---

# OMNeT++ — skill routing

<!-- Master copy lives in the shared skills repo under project-stubs/omnetpp/;
     install into the OMNeT++ repo as .claude/skills/omnetpp/SKILL.md. -->

## Get the shared skills

The detailed skills live in the shared skills repo (**TODO: final URL**). If
`~/.claude/skills/dev-design` does not exist, they are not installed — clone the repo and
run its `./install.sh`, then continue.

## Which skills apply here

`dev-*` (universal rules) and the `omnetpp-*` skills about developing OMNeT++ itself.
The `omnetpp-model-*`, `inet-*` and `simu5g-*` skills are for simulation models and do not
apply to the OMNeT++ code base. By task:

| Task | Skills |
|---|---|
| Designing a feature, writing or implementing a plan | dev-design |
| Git, commits, rebases, PRs | dev-git-workflow |
| Branch cleanup / big rebase | dev-branch-cleanup / dev-branch-rebase |
| ChangeLogs, API-changes.txt, WHATSNEW | omnetpp-release-engineering |
