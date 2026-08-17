# simu5g-team

This repository is the team definition for Simu5G development and
architectural refactoring. It holds no work. It describes the roles, the
routing, and the policies of an agent team that changes the `simu5g`
repository. Work products go where `policy/repository-map.md` sends them.

## The workspace

Four repositories sit side by side in one workspace:

- `simu5g` — the 5G/LTE network simulator. This is the only repository
  that the team changes.
- `inet` — the INET Framework. This is a dependency. The team does not
  change it.
- `omnetpp` — the simulation platform. This is a dependency. The team does
  not change it.
- `ai-logs` — plans and records. The `pending/` directory holds plans that
  are not yet done. The `done/` directory holds plans that are finished.

The dependency direction is `simu5g` → `inet` → `omnetpp`. It never
reverses. The team never patches a dependency. If the team finds a bug in
`inet` or `omnetpp`, the team writes an upstream report (gate 8 of
`policy/hitl-gates.md`).

## Two rules above all others

1. The team answers a question in prose. A question is never a reason to
   change code.
2. An agent never re-records a fingerprint baseline. An agent never merges
   to `master`. Only the human does these two actions.

## Where the procedures live

This repository does not restate how to run the fingerprint suite, how to
move a method between modules, or how to stage a commit. The procedures
live in the shared skills under `~/.claude/skills/`. The master copies are
in the `ai-config` repository. The skill groups are:

- `omnetpp-*` — platform mechanics: fingerprint concepts and drift
  interpretation, coding conventions for C++, NED, and MSG,
  behavior-preserving refactoring procedures, the git workflow, and
  simulation debugging.
- `simu5g-*` — Simu5G specifics. Each skill extends the matching
  `omnetpp-*` skill. If the two conflict, the `simu5g-*` skill wins.
- `inet-*` — background only. Simu5G follows the INET architecture and
  conventions, so the INET skills explain the idiom. The INET tooling
  (INET's build environment, INET's fingerprint runner) does not apply
  here.

A role file names the skills that it needs in its `Read first` section.
The role file refers to a skill. It never copies one.

## The tiers

- **Tier 0 — the human.** The human is the product owner. The human sets
  the goals and approves every gate. Only the human re-records a baseline
  or merges to `master`.
- **Tier 1 — control.** The program manager wants the work done. The
  resource manager wants the work cheap. They check each other.
- **Tier 2 — the lead.** The simu5g lead owns the repository: its idiom,
  its fingerprint baseline, its commits, its red lines.
- **Tier 3 — specialists.** The lead calls each specialist for one task.

Each tier calls the tier below it.

## The roster

| Tier | Role | Model | In one line |
|---|---|---|---|
| 1 | program-manager | opus | Classifies the task, picks the team, names the gates, routes to the lead. |
| 1 | resource-manager | sonnet | Guards tokens and time. Only this role can refuse an oversized team. |
| 2 | simu5g-lead | opus | Owns the `simu5g` repository: idiom, fingerprint baseline, commits, red lines. |
| 3 design | software-architect | opus | Designs how to make a change. Writes the plan as fingerprint-gated steps. |
| 3 design | 3gpp-standards-expert | opus | Says what the model must do, citing the 3GPP specification. |
| 3 design | architecture-auditor | opus | Audits a plan or a diff against the architecture red lines. |
| 3 design | code-quality-steward | opus | Guards long-term readability against cumulative drift. |
| 3 build | code-expert | sonnet | Implements one step of an approved plan. |
| 3 build | refactor-expert | sonnet | Runs behavior-preserving refactoring steps and wide sweeps. |
| 3 check | fingerprint-analyst | sonnet | Runs and triages the fingerprint suite. Reads drift by ingredient. |
| 3 check | test-expert | sonnet | Picks and runs the narrowest run that proves a change works. |
| 3 check | code-reviewer | opus | Reviews one diff for correctness and local cleanliness. |
| 3 support | build-environment-engineer | sonnet | Makes the code build and run on the machine. |
| 3 support | triage-agent | sonnet | Converts a bug report into a minimal reproduction and a task class. |
| 3 support | documentation-writer | sonnet | Writes guides that describe what the code is today. |
| 3 support | knowledge-curator | sonnet | Keeps plans, documents and role files consistent and true. |

Four roles are deferred until the work demands them: performance-expert,
result-analysis-expert, release-manager, license-compliance-officer. The
routing says what to do when these roles are absent.

## The role file

Every file in `role/` is both the role's documentation and its runtime
subagent definition. There is one source of truth. The frontmatter carries
exactly `name`, `description`, and `model`. It has no `tools:` line, for
two reasons. Every role inherits the session's tools. The role file states
the read-only discipline in prose.

The body has these sections, in this order:

1. `Mandate` — always.
2. `Read first` — always.
3. `You own`, `What you must know`, `What you do`, `Rules`, `Stop and
   ask` — as needed.
4. `What you return` — always, with a hard line cap.

## The `Read first` section

A session loads only the `CLAUDE.md` of the repository in which it starts.
Therefore the `Read first` section names the two to five documents and
skills that a role must open before it acts. Each entry gives the reason
that the item matters. The section refers to a document. It never copies
one. The knowledge curator makes sure that every `Read first` section
refers to real, current files.

## Installation

Link the roles into the work repository so Claude Code finds them:

    ln -s ../../simu5g-team/role simu5g/.claude/agents

Many roles first read `simu5g/.claude/skills/simu5g/SKILL.md`. This file
is the repository's own entry point. The master copy is
`project-stubs/simu5g/` in the `ai-config` repository. Install it into the
checkout before the team runs. The `install.sh` script of the same
repository installs the shared `omnetpp-*` and `simu5g-*` skills.

## The trigger

The team has one trigger: `/simu5g-team`. The file
`skill/simu5g-team/SKILL.md` defines it. The trigger classifies the task,
states the routing in five lines, and gives the work to the lead.
