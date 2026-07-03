# AI Skills for OMNeT++ / INET / Simu5G Development

A shared, public repository of AI agent skills for developing OMNeT++, the INET
Framework, and INET-based model libraries such as Simu5G. Written for Claude
Code, but the skills are plain markdown and usable from any AI coding tool.

## Install

```
./install.sh
```

This symlinks each skill directory into `~/.claude/skills/`, where Claude Code
auto-discovers it. Re-run after pulling new skills. Pass a different target
directory as the first argument if your tool reads skills from elsewhere.

Each supported project repo carries a brief entry-point skill in its own
`.claude/skills/` directory that lists which skills from this repo apply to it
(see `project-stubs/` for the masters).

## Naming scheme

Skills are named `<scope>-<workflow-or-convention>`. The scope prefix states
where a skill is valid — not necessarily a repository name:

| Prefix | Applies to |
|---|---|
| `omnetpp-*` | OMNeT++ platform mechanics: NED/MSG, kernel, build system, fingerprints |
| `inet-*` | The INET Framework repo only |
| `simu5g-*` | Simu5G only |
| `netsim-*` | Network-simulation methodology in general, not tied to OMNeT++ |

## Layering: generic skill + project augmentation

Shared knowledge lives in a generic skill; each project adds a thin skill with
only its deltas (exact commands, file locations, local exceptions). The project
skill starts by directing the reader to the generic skill, then augments it.
Exemplar: `omnetpp-fingerprint-testing` (concepts, ingredient semantics, drift
interpretation, discipline) + `inet-fingerprint-testing` (the INET runner, its
flags, INET-specific gotchas).

Rules that keep the layering honest:

- **Generic skills are command-free.** A concrete invocation in a generic skill
  is a smell — it belongs in a project skill.
- **Project skills are duplication-free.** They contain only differences,
  exceptions, and local workflows; concepts stay in the generic skill.
- **Project rules win** when they conflict with a generic skill.
- Every skill description states what it does AND when to use it ("Use
  when ..."), because the description is the only part an agent sees before
  deciding to load the skill.

## Layout

```
# Generic (omnetpp-*)
omnetpp-fingerprint-testing/   fingerprint concepts, ingredients, drift interpretation
omnetpp-model-development/     NED/MSG/INI, running sims, config discovery, result analysis
omnetpp-coding-conventions/    C++/MSG/NED conventions for model code
omnetpp-model-refactoring/     behavior-preserving refactoring recipes (move code, flatten)
omnetpp-git-workflow/          staging/commit/rebase discipline, PR integration
omnetpp-sim-debugging/         vanishing packets, gdb, pcap diffing, log attribution
omnetpp-branch-cleanup/        opp_repl-driven branch cleanup (framework + walkthrough)
omnetpp-branch-rebase/         opp_repl-driven staged rebase framework
omnetpp-release-engineering/   OMNeT++ core ChangeLogs, API-changes.txt, WHATSNEW

# INET (inet-*)
inet-dev-environment/          toplevel build, dual-mode, setenv/INET_ROOT trap, worktrees
inet-fingerprint-testing/      INET fingerprint runner + gotchas
inet-test-suites/              module/unit/protocol suites, .test authoring
inet-statistical-tests/        statistical baseline maintenance (opp_repl + CLI fallback)
inet-module-development/       conventions, recipes, integration patterns, gotchas
inet-branch-cleanup/           CLI-based INET branch-cleanup playbook
inet-cosmetic-cleanup/         cosmetic C++ cleanup, fingerprint-verified
inet-release-notes/            WHATSNEW entry for INET releases
inet-showcase-creator/         new showcases + Sphinx docs

# Simu5G (simu5g-*)
simu5g-fingerprint-testing/    Simu5G fingerprint runner specifics

# Other
oppenv-dev/                    opp_env database maintenance
rst-editing/                   RST formatting rules
project-stubs/                 masters for the per-repo entry-point skills (inet, simu5g)
install.sh                     symlink skills into ~/.claude/skills
```
