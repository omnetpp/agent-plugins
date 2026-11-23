# Project stubs

Master copies of the files that a project repository (INET, Simu5G, OMNeT++) carries so
that its contributors' agents use the right plugins. Each folder holds three files:

| File | Install as | Purpose |
|---|---|---|
| `SKILL.md` | `.claude/skills/<project>/SKILL.md` | Entry-point skill: which skills apply to which task, the project's always-on basics. It tells the user how to install the plugins when they are missing. |
| `settings.json` | `.claude/settings.json` (merge the two keys into an existing file) | Claude Code: registers the `omnetpp` marketplace and enables the project's plugins. |
| `AGENTS.md` | one line in the project's `AGENTS.md` | For other agents: which plugins to install. |

With `settings.json` committed, Claude Code registers the marketplace once a teammate trusts
the folder. Each teammate still installs the plugins once, e.g.
`claude plugin install inet@omnetpp`; until then, `/plugin` shows them as not installed.

Edit the masters here and copy them into the project repositories; keep the project copies
identical to the masters.
