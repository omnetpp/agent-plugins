# OMNeT++ agent plugins

Agent plugins for developing [OMNeT++](https://omnetpp.org) simulation models, the INET
Framework, and INET-based model libraries such as Simu5G. They give AI coding agents (Claude
Code, Codex and others) OMNeT++ skills. They also connect the agents to the OMNeT++
command-line tools: a NED/MSG/INI linter that runs after every edit, a language server, and an
MCP server that answers questions about the model.

The repository is one plugin marketplace, `omnetpp`, with four plugins:

| Plugin | For | Contents |
|---|---|---|
| `omnetpp` | Everyone who writes OMNeT++ models | Skills for model development, coding conventions, debugging, documentation generation (`opp_docgen`) and the NED/MSG/INI tools. The lint hook, the language server and the `omnetpp` MCP server. |
| `omnetpp-dev` | Maintainers of a model library | Working rules, fingerprint testing, behavior-preserving refactoring, git workflow, branch cleanup and rebase, review briefs, and the generic `dev-*` procedures they build on. |
| `inet` | INET contributors | INET build environment, test suites, protocol conformance test planning, fingerprint and statistical tests, module development, release notes, showcases. |
| `simu5g` | Simu5G contributors | Simu5G development rules and its fingerprint tests. |

`omnetpp-dev` needs `omnetpp`; `inet` needs both; `simu5g` needs `inet`. Claude Code
installs the dependencies on its own. In other agents, install every plugin in your row
below.

## Install

Pick the row for your role.

| Role | Plugins |
|---|---|
| Model developer | `omnetpp` |
| Model library maintainer | `omnetpp`, `omnetpp-dev` |
| INET contributor | `omnetpp`, `omnetpp-dev`, `inet` |
| Simu5G contributor | `omnetpp`, `omnetpp-dev`, `inet`, `simu5g` |

### Claude Code

```bash
claude plugin marketplace add omnetpp/ai-config
```

```bash
claude plugin install omnetpp@omnetpp
```

Install the other plugins of your row the same way, e.g. `claude plugin install inet@omnetpp`.

### Codex CLI

```bash
codex plugin marketplace add omnetpp/ai-config
```

```bash
codex plugin add omnetpp@omnetpp
```

Codex starts a plugin's MCP server in the plugin directory, not in your project, so the
`omnetpp` MCP server is registered separately (it needs the tools on `PATH`, see below):

```bash
codex mcp add omnetpp -- opp_ide_mcp
```

### Other agents

The plugins also have manifests for Copilot CLI, Cursor and Antigravity. These are untested.
They carry the skills, plus the language server (Copilot CLI) and the MCP server (Cursor).

## Requirements

- **Node.js 18 or newer**, for the command-line tools from the
  [`@omnetpp/opp-tools`](https://www.npmjs.com/package/@omnetpp/opp-tools) npm package
  (`opp_lint`, `opp_lsp`, `opp_ide_mcp`, `opp_docgen`). The plugin uses them from `PATH`.
  If they are not there, it fetches a pinned version with `npx`. The first fetch is
  slow, so installing them once is better:

  ```bash
  npm install -g @omnetpp/opp-tools
  ```

  The OMNeT++ VS Code extension can also put them on `PATH` ("OMNeT++: Install Command-Line
  Tools").
- **Library NED folders** (e.g. INET, for a model built on it) come from `omnetpp.nedPath` in
  the project's `.vscode/settings.json`, or from the `OMNETPP_NED_PATH` environment variable.
- **opp_repl** (`pip install opp_repl`, [github.com/omnetpp/opp_repl](https://github.com/omnetpp/opp_repl))
  for the opp_repl-driven skills in `omnetpp-dev` and `inet`: branch cleanup and
  rebase, and statistical-test maintenance. The plugins do not install it.

## Project setup

A project repository (INET, Simu5G, OMNeT++) can carry a short entry-point skill and agent
settings that point teammates' agents to the right plugins. `project-stubs/` holds the
master copies.

## License

The plugin contents (skills, manifests, scripts) are under the [MIT License](LICENSE).

The `@omnetpp/opp-tools` command-line tools are not part of this repository and have their own
license. They are free for noncommercial use (teaching, academic research, personal
non-profit use) on the same terms as the OMNeT++ Academic Public License; commercial use
requires an [OMNEST](https://omnest.com) license.

## Contributing

See [AGENTS.md](AGENTS.md) for the skill layout, naming and layering rules.
