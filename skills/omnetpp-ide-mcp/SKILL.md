---
name: omnetpp-ide-mcp
description: Drive the OMNeT++ IDE's Sequence Chart and Analysis (Scave) tools programmatically via the in-IDE MCP server. Use when asked to screenshot a protocol exchange (DORA, TCP handshake, etc.) from a .elog file, OR to render/screenshot a result chart from a .anf analysis file, drive these tools from outside the workbench, or operate the IDE without manual clicking. Server listens on http://127.0.0.1:5077/mcp (loopback, JSON-RPC over HTTP POST).
---

# OMNeT++ IDE MCP Server

A custom MCP server lives inside the OMNeT++ IDE as plugin `org.omnetpp.mcp`. When the IDE is running, the server exposes 23 JSON-RPC tools across two IDE tools: the **Sequence Chart** (open eventlogs, search events, configure axes/zoom/timeline, filter what gets drawn, take PNG screenshots) and the **Analysis / Scave editor** (open `.anf` files, list charts, render result charts to PNG — both headless and WYSIWYG).

> This skill is about **operating** charts that already exist. For **authoring** result charts (creating the `.anf`, defining charts, writing/editing chart scripts, using templates so they render in the IDE and headless via `opp_charttool`), that is a separate concern.

## When to use

The user is asking to:
- Screenshot a specific protocol exchange in a `.elog` file (DHCP DORA, TCP handshake, etc.)
- Drive the OMNeT++ Sequence Chart from a script or from another agent
- Programmatically inspect events, modules, or axes in a simulation eventlog
- Repeat a sequence-chart configuration across many runs

- Render a result chart from an existing `.anf` analysis to a PNG (`open_analysis` → `list_charts` → `render_chart`/`screenshot_chart`)

If the user is just opening an `.elog` or `.anf` interactively and using it by hand, this skill isn't needed.

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
5. set_display_mode NETWORK_COMMUNICATION           → required when axes are network nodes
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

## Recipe comments for showcase sequence charts

Every sequence-chart `.. figure::` in a showcase should be immediately followed by a
**FIGURE RECIPE** comment, so the chart can be regenerated after a config or
visualization change. The recipe records only the deltas specific to that chart; the
redo procedure itself is the canonical recipe above. The anchor / self-check
philosophy — why a redo is usually a cheap deterministic replay, and how the anchor
lets the AI decide whether to replay or re-tune — is written once in the
`video-recording` skill and applies identically here.

Format (RST comment — `..` on its own line, content never parsed as RST):

```
.. figure:: media/client_crash.png
..
   FIGURE RECIPE (redo via the "omnetpp-ide-mcp" skill)
   type:     seqchart
   config:   ClientCrash               # ../omnetpp.ini, record-eventlog=true
   seed:     default
   shows:    the INIT-REBOOT exchange — client[0]'s broadcast DHCPREQUEST
             reaching dhcpServer via switch, answered by a DHCPACK
   source:   results/ClientCrash-*.elog (produced by record-eventlog=true)
   axes:     client[0] · switch · dhcpServer        (this top-to-bottom order)
   anchor:   REQUEST→ACK at t≈60s (client crashes t=30s, restarts t=60s).
             If the exchange moves off ~60s, the scenario/timing changed →
             re-capture and rewrite this recipe.
   capture:  Sequence Chart screenshot, NONLINEAR timeline, cropped to the
             exchange; was 963×578
   stamp:    captured 2026-06, INET 4.6
```

Fields specific to sequence charts:
- **source** — the `.elog` the chart is drawn from, plus how to produce it
  (`record-eventlog=true` on that config). On redo the AI re-runs the config to
  regenerate the eventlog, then `open_eventlog`s it.
- **axes** — the module set + top-to-bottom order for `set_open_axis_modules` /
  `set_manual_axis_order`. Always include physical transit modules (switch/router)
  or the arrows vanish (see Pitfalls).
- **anchor** — the protocol exchange and its sim time. On redo, `find_events` for
  the message pattern and confirm it still lands near that time before
  screenshotting; if it moved, re-derive and rewrite.
- **capture** — timeline mode (usually NONLINEAR) and the last screenshot dims (a
  resolution hint, not a hard crop).

## Pitfalls (read before debugging an empty chart)

1. **NETWORK_COMMUNICATION mode needs physical transit modules visible.** A DHCP packet physically traverses the switch even though logically it goes "client to server". If you remove the switch from the open axis set, the arrows disappear because the chart can't draw an arrow whose physical path leaves the visible axes. Keep switches/routers/wire junctions in the axis set.

2. **`use_network_node_axes` is the safest starting point** when you don't know the topology — it opens every `@networkNode` and `@wireJunction` module AND sets NETWORK_COMMUNICATION mode in one call. From there, narrow with `set_open_axis_modules`, then re-call `set_display_mode NETWORK_COMMUNICATION` if you've changed display mode in between.

3. **Eventlog files don't auto-refresh.** If the user just ran the simulation from CLI, the IDE's workspace cache may still think the file is absent. `open_eventlog` does a `refreshLocal` on the parent folder, so passing the workspace path (e.g. `/inet/showcases/.../foo.elog`) always works. Absolute paths under the workspace root also work.

4. **Screenshot reflects the visible widget.** To change resolution, call `resize_window` to grow the IDE window before screenshotting. The chart widget is one part of the window, so the screenshot is smaller than the requested window size.

5. **Filenames with `#` are workspace-legal.** OMNeT++ generates filenames like `BasicDHCP-#0.elog`. JSON handles `#` fine; no URL-encoding needed.

## Trimming a busy chart with `set_event_filter`

In wireless traces, the chart fills with infrastructure traffic (Beacons, 802.11 ACKs) that obscures the protocol exchange you actually want to show. `set_event_filter` is the headless equivalent of the IDE's "Filter Eventlog" button.

Discovery first: `list_message_names {handle}` returns the distinct set of message names found in this eventlog — the same data the dialog's "by name" tab shows as checkboxes. Look at what's there, then write the filter.

**Inclusion (preferred when possible):** list the message families you want to keep. Anything not in any of these patterns is dropped.

```jsonc
set_event_filter {
  handle: "...",
  message_names: ["DHCP*", "Beacon", "Auth*", "Assoc*", "Probe*"]
}
```

This is cleaner than exclusion and matches naturally with the chart's OR'd filter dimensions.

**Exclusion via match expression:** when the noise pattern is small and the keep-set is open-ended, use `message_expression` with OMNeT++ match-expression syntax (NOT Lucene/Elasticsearch). The grammar:

```
WlanAck                     literal — matches default field (message name)
NOT WlanAck                 negation
WlanAck*                    glob
field(value)                explicit field selector
NOT (A AND B)               combinators
```

So to hide every 802.11 ACK: `message_expression: "NOT WlanAck"`.

**Other dimensions:** `module_paths` / `module_ned_types` for module filtering; `from_event_number` / `to_event_number` / `from_simulation_time` / `to_simulation_time` for slicing.

**Clear:** `set_event_filter {handle, clear: true}` removes the filter.

Filter dimensions are OR'd internally (any matching field includes the event), so for AND-of-conditions use a single `message_expression` with `AND` operators rather than mixing fields.

## Tool surface (current as of session memory)

Open the chart and navigate:
- `open_eventlog` → handle
- `goto_event` (scroll + select an event by number)
- `zoom_to_simulation_time_range`

Inspect:
- `list_modules` (full module tree, optionally network-nodes only)
- `list_axes` (currently visible axes in display order)
- `list_message_names` (distinct message names — or `kind:"class"` for class names — that appear in the eventlog; the same data the IDE Filter dialog's checkbox lists show)
- `find_events` (paginated; filter by message name regex, module path regex, time range, event range)
- `get_event` (single event with cause + consequences)
- `get_view_state` (zoom, time bounds, timeline mode, axis ordering, widget size)

Configure the view:
- `set_open_axis_modules`
- `set_manual_axis_order`
- `set_axis_ordering_mode` (MODULE_ID / MODULE_FULL_PATH / MINIMIZE_CROSSINGS / MANUAL)
- `set_timeline_mode` (SIMULATION_TIME / EVENT_NUMBER / STEP / NONLINEAR)
- `set_display_mode` (ALL / DEFAULT / NETWORK_COMMUNICATION)
- `set_event_filter` (filter which events/messages get drawn — by name, class, module, event/time range, or free-form match expression; same machinery as the IDE's Filter Eventlog dialog)
- `use_network_node_axes` (preset: all network nodes + wire junctions, NETWORK_COMMUNICATION on)

Output:
- `screenshot` (PNG, base64, current viewport)

Analysis / Scave editor (drive the `.anf` result-chart editor):
- `open_analysis` → handle (loads the analysis' input `.sca`/`.vec`, so charts have data)
- `list_charts` (id, name, type ∈ {LINE, BAR, HISTOGRAM, MATPLOTLIB}, folder)
- `render_chart` (headless PNG via the IDE's Export-Charts machinery; deterministic, works for native + matplotlib, no visible page needed; identify the chart by id or name, optional `dpi`)
- `screenshot_chart` (WYSIWYG PNG of the on-screen chart viewer)

Use `render_chart` to regenerate a showcase figure deterministically; use `screenshot_chart` only when you specifically want what the on-screen viewer shows. Both need the IDE's Python bridge (py4j, hardcoded port 3724), so only one IDE instance per machine can render charts.

Misc:
- `resize_window` (resize the IDE main window)
- `ping` (smoke test)

`tools/list` is the source of truth — every tool's description carries the up-to-date contract.

## Plugin source and side-load workflow

Source: `~/omnetpp-dev/ui/org.omnetpp.mcp/`. Side-loaded JAR lives at `~/omnetpp-aipre-GUI/ide/plugins/org.omnetpp.mcp_<version>.jar` and is registered in `configuration/org.eclipse.equinox.simpleconfigurator/bundles.info`. The dev cycle is: edit Java → `javac` against the IDE's bundled jars → `jar cfm` into a numbered version → drop in `plugins/` + update `bundles.info` → restart IDE. (Auto-refresh / dropins is disabled in this install by `org.eclipse.update.reconcile=false`.)

The plugin's design notes, build status, and the BasicDHCP DORA event waypoints live in user memory: `~/.claude/projects/-home-user-inet/memory/project_omnetpp_ide_mcp.md`.
