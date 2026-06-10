---
name: omnetpp-ide-mcp
description: Drive the OMNeT++ IDE's Sequence Chart programmatically via the in-IDE MCP server. Use when asked to take a screenshot of a protocol exchange (DORA, TCP handshake, etc.) from a .elog file, drive the Sequence Chart from outside the workbench, or operate the IDE without manual clicking. Server listens on http://127.0.0.1:5077/mcp (loopback, JSON-RPC over HTTP POST).
---

# OMNeT++ IDE MCP Server

A custom MCP server lives inside the OMNeT++ IDE as plugin `org.omnetpp.mcp`. When the IDE is running, the server exposes 17 JSON-RPC tools for driving the Sequence Chart programmatically — open eventlogs, search events, configure axes/zoom/timeline, take PNG screenshots.

## When to use

The user is asking to:
- Screenshot a specific protocol exchange in a `.elog` file (DHCP DORA, TCP handshake, etc.)
- Drive the OMNeT++ Sequence Chart from a script or from another agent
- Programmatically inspect events, modules, or axes in a simulation eventlog
- Repeat a sequence-chart configuration across many runs

If the user is just opening an `.elog` interactively and using the chart by hand, this skill isn't needed.

## Check the server is up

```bash
curl -sS --max-time 1 -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5077/mcp/health
# 200 = ready; 000 = IDE not running or server disabled
```

If `000`, the IDE isn't running. Ask the user to start it (they likely have an `ide` alias or know their launcher). The server boots automatically with the IDE. It can be disabled with `OPP_MCP_DISABLED=1` or moved to a different port with `OPP_MCP_PORT=N`.

## JSON-RPC transport

Plain HTTP POST against `/mcp`. Each request is a JSON-RPC 2.0 object:

```bash
curl -sS -X POST -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' \
  http://127.0.0.1:5077/mcp
```

Tool invocation:

```bash
curl -sS -X POST -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"open_eventlog","arguments":{"path":"/project/results/foo.elog"}}}' \
  http://127.0.0.1:5077/mcp
```

Tool results come back as MCP content blocks: text (JSON string for structured data) and image (base64 PNG for screenshots).

Always call `tools/list` first to see the current tool surface and read the full descriptions — they include workflow guidance.

## Canonical recipe — "screenshot exchange X in eventlog Y"

This is the recipe the agent should follow for any "show me protocol X in eventlog Y" prompt. It's also documented in the `open_eventlog` tool description.

```
1. open_eventlog                                    → handle (workspace path)
2. find_events {message_name_pattern: "<protocol pattern>"}
                                                    → event numbers + sim times + modules
3. set_open_axis_modules                            → relevant network nodes
                                                      INCLUDING physical transit modules
                                                      (switches, routers, wire junctions)
4. set_manual_axis_order                            → top-to-bottom order
5. set_display_mode NETWORK_COMMUNICATION           → MUST come AFTER set_open_axis_modules
                                                      (axis changes reset display-mode flags)
6. zoom_to_simulation_time_range                    → exchange bounds
7. set_timeline_mode NONLINEAR                      → readable arrow spacing for dense exchanges
8. screenshot                                       → PNG content block
```

Worked example, DHCP DORA in `inet/showcases/general/dhcp/results/BasicDHCP-#0.elog`:

```jsonc
// find_events for "^DHCP(DISCOVER|OFFER|REQUEST|ACK)$" → bounds 1.0976270..1.0978383
// pick axes: client[0] (origin), switch (transit — required!), dhcpServer (target)

set_open_axis_modules    {module_paths: ["DhcpShowcase.client[0]", "DhcpShowcase.switch", "DhcpShowcase.dhcpServer"]}
set_manual_axis_order    {module_paths: ["DhcpShowcase.client[0]", "DhcpShowcase.switch", "DhcpShowcase.dhcpServer"]}
set_display_mode         {mode: "NETWORK_COMMUNICATION"}
zoom_to_simulation_time_range {from_simulation_time: "1.0976270", to_simulation_time: "1.0978383"}
set_timeline_mode        {mode: "NONLINEAR"}
screenshot               {}
```

## Pitfalls (read before debugging an empty chart)

1. **`set_open_axis_modules` resets display-mode flags as a side effect.** If you set display mode first then change axes, the display mode reverts. Always: axes → manual order → `set_display_mode` → zoom → screenshot.

2. **NETWORK_COMMUNICATION mode needs physical transit modules visible.** A DHCP packet physically traverses the switch even though logically it goes "client to server". If you remove the switch from the open axis set, the arrows disappear because the chart can't draw an arrow whose physical path leaves the visible axes. Keep switches/routers/wire junctions in the axis set.

3. **`use_network_node_axes` is the safest starting point** when you don't know the topology — it opens every `@networkNode` and `@wireJunction` module AND sets NETWORK_COMMUNICATION mode in one call. From there, you can narrow with `set_open_axis_modules` (and re-apply `set_display_mode`).

4. **Eventlog files don't auto-refresh.** If the user just ran the simulation from CLI, the IDE's workspace cache may still think the file is absent. `open_eventlog` does a `refreshLocal` on the parent folder, so passing the workspace path (e.g. `/inet/showcases/.../foo.elog`) always works. Absolute paths under the workspace root also work.

5. **Screenshot reflects the visible widget.** To change resolution, call `resize_window` to grow the IDE window before screenshotting. The chart widget is one part of the window, so the screenshot is smaller than the requested window size.

6. **Filenames with `#` are workspace-legal.** OMNeT++ generates filenames like `BasicDHCP-#0.elog`. JSON handles `#` fine; no URL-encoding needed.

## Tool surface (current as of session memory)

Open the chart and navigate:
- `open_eventlog` → handle
- `goto_event` (scroll + select an event by number)
- `zoom_to_simulation_time_range`

Inspect:
- `list_modules` (full module tree, optionally network-nodes only)
- `list_axes` (currently visible axes in display order)
- `find_events` (paginated; filter by message name regex, module path regex, time range, event range)
- `get_event` (single event with cause + consequences)
- `get_view_state` (zoom, time bounds, timeline mode, axis ordering, widget size)

Configure the view:
- `set_open_axis_modules`
- `set_manual_axis_order`
- `set_axis_ordering_mode` (MODULE_ID / MODULE_FULL_PATH / MINIMIZE_CROSSINGS / MANUAL)
- `set_timeline_mode` (SIMULATION_TIME / EVENT_NUMBER / STEP / NONLINEAR)
- `set_display_mode` (ALL / DEFAULT / NETWORK_COMMUNICATION)
- `use_network_node_axes` (preset: all network nodes + wire junctions, NETWORK_COMMUNICATION on)

Output:
- `screenshot` (PNG, base64, current viewport)

Misc:
- `resize_window` (resize the IDE main window)
- `ping` (smoke test)

`tools/list` is the source of truth — every tool's description carries the up-to-date contract.

## Plugin source and side-load workflow

Source: `~/omnetpp-dev/ui/org.omnetpp.mcp/`. Side-loaded JAR lives at `~/omnetpp-aipre-GUI/ide/plugins/org.omnetpp.mcp_<version>.jar` and is registered in `configuration/org.eclipse.equinox.simpleconfigurator/bundles.info`. The dev cycle is: edit Java → `javac` against the IDE's bundled jars → `jar cfm` into a numbered version → drop in `plugins/` + update `bundles.info` → restart IDE. (Auto-refresh / dropins is disabled in this install by `org.eclipse.update.reconcile=false`.)

The plugin's design notes, build status, and the BasicDHCP DORA event waypoints live in user memory: `~/.claude/projects/-home-user-inet/memory/project_omnetpp_ide_mcp.md`.
