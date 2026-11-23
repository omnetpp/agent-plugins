# Working on the OMNeT++ agent plugins

This repository is a plugin marketplace. Each plugin is a self-contained folder,
`plugins/<plugin>/`, and its skills are in `plugins/<plugin>/skills/<skill>/SKILL.md`. An agent
installs a plugin by copying its folder, so nothing in a plugin may refer to a file outside
that folder.

## Which plugin a skill belongs to

| Prefix | Applies to | Plugin |
|---|---|---|
| `omnetpp-model-*` | OMNeT++-based simulation models: INET, Simu5G, user models | `omnetpp` (everyday model work) or `omnetpp-dev` (regression testing, refactoring, history work) |
| `omnetpp-tooling`, `omnetpp-model-doc-*` | the OMNeT++ command-line tools | `omnetpp` |
| `dev-*` | any software project | `omnetpp-dev` (only the ones its skills build on) |
| `inet-*` | INET and INET-based libraries | `inet` |
| `simu5g-*` | Simu5G only | `simu5g` |

Dependencies point one way: `simu5g` → `inet` → `omnetpp-dev` → `omnetpp`. A skill
may refer to any skill in its own plugin or in a plugin it depends on. A skill may mention a
skill in a plugin that depends on it only as an optional pointer, e.g. "for INET, see
`inet-fingerprint-testing` if installed".

## Rules for skills

- **Refer to other skills by name**, never by a relative path such as
  `../omnetpp-model-fingerprint-testing/SKILL.md`: after installation, the plugins are in
  separate folders.
- **Generic skills have no commands.** A concrete invocation belongs in a project skill.
- **Project skills have no duplicated content.** They hold only differences, exceptions and
  local workflows. They start by pointing to the generic skill, and they win when the two
  conflict. Example: `omnetpp-model-fingerprint-testing` (concepts) plus
  `inet-fingerprint-testing` (the INET runner).
- **Every description says what the skill does and when to use it** ("Use when ..."). The
  description is all an agent sees before it decides to load the skill.
- **Nothing private.** No home directories, personal plan repos, user names or internal
  notes. Use variables (`$INET_ROOT`) or describe the location by its role.
- Commit subjects follow the `dev-commit-messages` skill.
