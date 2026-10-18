---
name: simu5g
description: >
  Entry point for developing Simu5G in this repository: makes sure the shared AI skills
  are installed, then hands over to the simu5g-dev skill, which holds all Simu5G rules.
  Use at the start of any Simu5G development task (coding, testing, refactoring,
  rebasing) before reaching for individual skills.
---

# Simu5G — entry point

<!-- Master copy lives in the shared skills repo under project-stubs/simu5g/;
     install into the Simu5G repo as .claude/skills/simu5g/SKILL.md. -->

## Get the shared skills

The detailed skills live in the shared skills repo (**TODO: final URL**). If
`~/.claude/skills/simu5g-dev` does not exist, clone the repo and run its
`./install.sh`, then continue.

## Then load `simu5g-dev`

All Simu5G rules live in the `simu5g-dev` skill: which `inet-*`,
`omnetpp-model-*` and `dev-*` skills apply and how Simu5G overrides them, the commit-subject
format specifics, the architecture red lines and rules, code/NED style, build/run and
testing rules, and the working rules. Load it before starting any task.
