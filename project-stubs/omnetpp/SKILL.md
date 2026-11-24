---
name: omnetpp
description: >
  Entry point for developing OMNeT++ itself in this repository (simulation kernel, envir,
  nedxml, user interfaces, IDE, tools, documentation): which AI skills apply here and how
  to install them. Use at the start of any OMNeT++ development task (designing, planning,
  implementing, testing, committing, preparing a branch or a release) before reaching for
  individual skills.
---

# OMNeT++ — skill routing

<!-- Master copy lives in the shared skills repo under project-stubs/omnetpp/;
     install into the OMNeT++ repo as .claude/skills/omnetpp/SKILL.md. -->

## Get the plugins

The `dev-*` skills come from the `omnetpp-dev` plugin of the OMNeT++ agent plugins
(marketplace `omnetpp`, github.com/omnetpp/agent-plugins). If the `dev-design` skill is not
available, it is not installed. Tell the user to install it (Claude Code):

```bash
claude plugin marketplace add omnetpp/agent-plugins
claude plugin install omnetpp-dev@omnetpp
```

It brings the `omnetpp` plugin along, whose lint hook and language server also help with
the NED/MSG/INI files of the samples. Other agents: see the README of that repository.

## Which skills apply here

`dev-*` (universal rules) and the project skills of this repository about developing
OMNeT++ itself. The `omnetpp-model-*`, `inet-*` and `simu5g-*` skills are for simulation
models and do not apply to the OMNeT++ code base; `omnetpp-tooling` applies to the
NED/MSG/INI files of the samples. By task:

| Task | Skills |
|---|---|
| Designing a feature, writing or implementing a plan | dev-design |
| Git, commits, rebases, PRs | dev-git-workflow + dev-commit-messages |
| Branch cleanup / big rebase | dev-branch-cleanup / dev-branch-rebase |
| ChangeLogs, API-changes.txt, WHATSNEW | omnetpp-release-engineering (project skill of this repository) |
