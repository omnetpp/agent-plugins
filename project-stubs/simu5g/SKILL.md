---
name: simu5g
description: >
  Entry point for developing Simu5G in this repository: makes sure the OMNeT++ agent
  plugins are installed, then hands over to the simu5g-dev skill, which holds all Simu5G rules.
  Use at the start of any Simu5G development task (coding, testing, refactoring,
  rebasing) before reaching for individual skills.
---

# Simu5G — entry point

<!-- Master copy lives in the shared skills repo under project-stubs/simu5g/;
     install into the Simu5G repo as .claude/skills/simu5g/SKILL.md. -->

## Get the plugins

The detailed skills come from the OMNeT++ agent plugins (marketplace `omnetpp`,
github.com/omnetpp/agent-plugins). If the `simu5g-dev` skill is not available, they are not
installed. Tell the user to install them (Claude Code):

```bash
claude plugin marketplace add omnetpp/agent-plugins
claude plugin install simu5g@omnetpp
```

`simu5g` brings `inet`, `omnetpp-dev` and `omnetpp` along. Other agents: see the
README of that repository.

## Then load `simu5g-dev`

All Simu5G rules live in the `simu5g-dev` skill: which `inet-*`,
`omnetpp-model-*` and `dev-*` skills apply and how Simu5G overrides them, the commit-subject
format specifics, the architecture red lines and rules, code/NED style, build/run and
testing rules, and the working rules. Load it before starting any task.
