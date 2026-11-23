---
name: omnetpp-tooling
description: >
  How to query and check OMNeT++ NED, MSG and INI files with the omnetpp MCP tools and the
  opp_lint command-line linter, instead of grepping. Use when reading, editing, renaming or
  reviewing .ned, .msg or .ini files in an OMNeT++ project: finding a NED type, its
  parameters, gates, subtypes or usages; resolving effective INI parameter values;
  looking up configuration options; checking files for errors after an edit; fixing
  "unresolved type" errors; or inspecting a recorded .elog eventlog.
---

# OMNeT++ NED/MSG/INI tooling

The `omnetpp` MCP server indexes every NED, MSG and INI file of the project and of the
projects on its NED path. Its answers are semantic (they follow `extends`, imports,
packages and `typename` assignments), so prefer them to text search for these files.
Depending on the agent, the tools may appear with a prefix such as `mcp__omnetpp__`. If no
such tools are available, see "Without the MCP tools" below.

## Which tool to use

| Question | Tool |
| --- | --- |
| Which NED types exist (filter by kind/package/name)? | `list_ned_types` |
| Parameters, gates, submodules, properties of a type | `get_ned_type` |
| Base types / derived types | `get_inheritance`, `find_subtypes` |
| Who uses a type, what breaks if it changes | `find_type_usages`, `impact_of`, `neighbors` |
| Connections inside a compound module | `get_connections` |
| Where a parameter gets its value | `find_param_assignments` |
| Effective parameter values of an INI config | `list_ini_configs`, `resolve_ini_params` |
| Meaning of an INI option such as `sim-time-limit` | `lookup_config_option`, `list_config_options` |
| MSG classes, fields, and where they are used | `list_msg_types`, `get_msg_type`, `find_msg_usages`, `find_member_accesses` |
| C++ class behind a `@class` | `resolve_class` |
| Unused networks or message types (hint only) | `find_unused` |
| Errors and warnings of one file | `get_diagnostics` |
| Recorded eventlog (`.elog`) contents | `elog_*` tools (standalone `opp_ide_mcp` only, not the VS Code live bridge) |

`rename_ned_type`, `rename_member` and `organize_imports` return edits and **do not write
files**. Apply the returned edits yourself, then check the touched files again.

## Checking files

- After you edit a `.ned`, `.msg` or `.ini` file, check it. With the omnetpp plugin's lint
  hook, the diagnostics of the edited file come back automatically after each edit.
  Otherwise call `get_diagnostics` or run the linter.
- Run the linter from the project root:
  `opp_lint` (whole project), `opp_lint path/to/file.ned`, `opp_lint --format=json`.
  Exit code 0 means no errors, 1 means diagnostics at or above `--fail-on` (default
  `error`), 2 means a usage or runtime error.
- If `opp_lint` is not on PATH, or it exits with 127 (a stale shim of the VS Code
  extension), run it as `npx --yes -p @omnetpp/opp-tools opp_lint …` (needs Node.js 18 or
  newer).
- Suppress a single diagnostic only when it is a false positive, and say why in the
  suppression comment.

## NED path

Projects that use other OMNeT++ projects (for example INET) need those projects on the NED
path, or type lookups fail with "unresolved type" errors. The tools read the NED path from
`omnetpp.nedPath` in the project's `.vscode/settings.json` (entries separated by `;`,
relative to the project root), or from `--ned-path` / `OMNETPP_NED_PATH`. If many types
are unresolved, check this setting before you change any code. Prefer relative entries in
the committed settings file, so they work for teammates too.

## Without the MCP tools

The plugin provides the MCP server in Claude Code and Cursor. Codex needs it registered once
(`codex mcp add omnetpp -- opp_ide_mcp`); some agents have none. Without it:

- Find a type by its declaration (`simple`, `module`, `network`, `channel`, `moduleinterface`,
  `channelinterface` followed by the name) and check the `package` line of its file and the
  `import` lines of the file that uses it: the same simple name can exist in several packages.
- Follow `extends` and `like` by hand to the base type or interface before concluding that a
  parameter or gate is missing.
- For effective INI values, read the config's section and every section it `extends` (and
  `[General]`); the first matching pattern line wins.
- Check every edit with `opp_lint` (above): it resolves types the same way as the MCP server.

## Limits

- The tools read files from disk. Save a file before you query it.
- They do not compile or run anything. Use the build (`make MODE=debug`) and a simulation
  run to verify C++ and runtime behavior.
