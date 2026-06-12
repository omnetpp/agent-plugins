---
name: omnetpp-mcp-sim
description: Run OMNeT++/INET simulations and interact with them live via the built-in MCP server. Use when the user wants an AI to observe, query, or control a running OMNeT++ simulation, connect to a live simulation via MCP, use --mcp-server-address, run simulations through opp_repl MCP, or asks how an AI can interact with a simulation at runtime.
---

# OMNeT++ AI-Interactive Simulations via MCP

## Architecture

There are two independent MCP layers:

```
Windsurf/AI
    │  MCP: execute_python(...)         ← opp_repl layer (optional)
    ▼
opp_repl REPL (port 9966)
    │  launches subprocess
    ▼
OMNeT++ simulation binary (omnetpp-aipre build)
    │  listens on
    ▼
simulation MCP server (port 8765)       ← simulation layer (core)
    ↑
Windsurf/AI also connects here directly
```

## Layer 1 — Simulation-side MCP (built into OMNeT++ `aipre` branch)

The MCP server is compiled into the OMNeT++ `envir` library (`src/envir/mcpserver.cc`).
It is activated by the `mcp-server-address` config option (INI or command line).

**Starting directly** (no opp_repl needed):
```bash
./INET -u Qtenv -f omnetpp.ini -c MyConfig --mcp-server-address localhost:8765
# or Cmdenv:
./INET -u Cmdenv -f omnetpp.ini -c MyConfig --mcp-server-address localhost:8765
```

**Starting via opp_repl** (when you also want workflow automation):
```python
run_simulations(filter="MyConfig", mode="debug", user_interface="Qtenv",
                append_args=["--mcp-server-address", "localhost:8765"])
```

**Windsurf MCP client config** (`~/.codeium/windsurf/mcp_config.json`):
```json
{
  "mcpServers": {
    "omnetpp-sim": {
      "url": "http://localhost:8765/mcp"
    }
  }
}
```
No auth token needed — the simulation MCP server is unauthenticated.

### Available simulation MCP tools

`Qtenv?` column: **Y** = the tool requires Qtenv and returns "not available" under Cmdenv.
`Clang?` column: **Y** = the tool requires the JIT C++ interpreter (only available when OMNeT++ was built with `WITH_CLANG_INTERPRETER=yes`; can be disabled at runtime).

**Simulation control**

| Tool | What it does | Qtenv? | Clang? |
|---|---|---|---|
| `run_simulation` | Advance sim by time/event limit, optional run mode (normal/fast/express) | | |
| `request_stop_simulation` | Stop the currently running simulation after the current event | | |
| `set_stop_condition` | Set a C++ lambda stop condition (persists across `run_simulation` calls) | | Y |
| `clear_stop_condition` | Clear the C++ stop condition | | |
| `set_debugger_break_condition` | Trap into gdb/lldb when a C++ condition fires | | Y |
| `clear_debugger_break_condition` | Clear the C++ debugger-break condition | | |
| `request_debugger_break` | Force a debugger break on the next event | | |

**Configuration & lifecycle**

| Tool | What it does | Qtenv? | Clang? |
|---|---|---|---|
| `get_config` | Active INI config (full snapshot or single option value) | | |
| `list_configs` | List configs declared in the .ini file with run counts | | |
| `setup_config` | Switch to a different config / run number (tears down + sets up fresh network) | Y | |
| `rebuild_network` | Restart current config from event #0 (reseeds RNGs, resets stats) | Y | |

**Dialogs** — normally empty during MCP work. While an MCP request is processed, Qtenv routes `confirm()` / `displayException()` (errors, end-of-sim notices) to the log buffer instead of a blocking `QMessageBox`. Use these for the rare dialog that bypasses that path.

| Tool | What it does | Qtenv? | Clang? |
|---|---|---|---|
| `list_dialogs` | List visible top-level modal dialogs (index, title, text, buttons, kind) | Y | |
| `dismiss_dialog` | Click a button on a visible dialog (default: accept / OK on topmost) | Y | |

**State queries**

| Tool | What it does | Qtenv? | Clang? |
|---|---|---|---|
| `get_simulation_state` | Current sim time, event number, state, next-event info | | |
| `get_fes` | Future Event Set contents | | |
| `get_statistics` | Live values of `@statistic` recorders for a module | | |
| `list_result_files` | List files in the result directory (.sca / .vec / .elog / .pcap) | | |

**Module & object queries**

| Tool | What it does | Qtenv? | Clang? |
|---|---|---|---|
| `find_modules` | Search modules by name / NED type pattern | | |
| `find_objects` | Search cObject tree by class name / path pattern | | |
| `get_network_topology` | Whole network topology as a nested JSON tree | | |
| `get_module_hierarchy` | Submodule list + parent info for a module | | |
| `get_module_info` | Module type, NED type, info string | | |
| `get_module_connections` | Gate connections of a module with peer paths | | |
| `get_module_parameters` | Current parameter values of a module | | |
| `get_module_watches` | `WATCH()` variables and their current values | | |
| `get_module_log` | `EV <<` log output for a module (from Qtenv log buffer) | Y | |
| `get_module_message_log` | Message / packet traffic log for a module (text view) | Y | |
| `list_logged_packets` | Structured packet list from Qtenv's log buffer with `path: logged:<tree_id>` handles | Y | |
| `get_channel_parameters` | Channel properties for a module's connections | | |
| `get_object_children` | Direct child objects of any cObject | | |
| `get_object_details` | Full reflection details for a cObject | | |

**Packet inspection (Wireshark-style)** — `list_logged_packets` returns a `path` field of the form `logged:<tree_id>` for each entry. Pass that path to `open_inspector`, `expand_inspector_tree`, and `get_inspector_screenshot` to drill into a packet's nested chunk structure (INET Packet → SequenceChunk / IPv4Header / TcpHeader etc.) and screenshot the result.

**Pcap analysis**

| Tool | What it does | Qtenv? | Clang? |
|---|---|---|---|
| `read_pcap` | Analyze a PCAP/PCAPNG file via tshark (filters, fields, decode hints) | | |

**Visualization (Qtenv canvas + inspectors)**

| Tool | What it does | Qtenv? | Clang? |
|---|---|---|---|
| `get_canvas_image` | Render a module's `cCanvas` to a PNG (base64-encoded) | Y | |
| `open_inspector` | Open a Qtenv inspector window for any cObject by full path | Y | |
| `get_inspector_screenshot` | Capture the inspector widget as a PNG (with optional resize) | Y | |
| `expand_inspector_tree` | Expand tree nodes in object / object-tree inspectors before screenshotting | Y | |

**Video recording (Qtenv)**

| Tool | What it does | Qtenv? | Clang? |
|---|---|---|---|
| `start_video_recording` | Begin frame-by-frame PNG capture of the main window | Y | |
| `stop_video_recording` | Stop capture and return a ready-to-run ffmpeg command | Y | |
| `record_video` | One-shot wrapper: start + run_simulation + stop | Y | |

See the `video-recording` skill for the recommended workflow.

**Arbitrary code execution**

| Tool | What it does | Qtenv? | Clang? |
|---|---|---|---|
| `execute_cpp` | JIT-compile and run a C++ snippet inside the live simulation process | | Y |

### Available simulation MCP resources

The server exposes a few read-only resources for static context that doesn't change during a run. Note the URI scheme is `simulation://`, not `omnetpp://`.

| URI | Content |
|---|---|
| `simulation://config/run` | Run identity: OMNeT++ version, run ID, config name, run number, network, experiment, seed set, result dir, iteration variables, timestamps |
| `simulation://config/ini` | Active INI configuration: config name, run number, all key-value entries (text/plain) |
| `simulation://types/modules` | All registered NED module types in the current network (fully qualified name, C++ class, simple/compound) |
| `simulation://types/channels` | All registered NED channel types |
| `simulation://ned/{typeName}` | NED source code for a specific type (e.g. `inet.node.inet.StandardHost`) |
| `simulation://modules/{path}/parameters` | Parameter *metadata* for a module (name, type, volatile). For current values use `get_module_parameters`. |
| `simulation://modules/{path}/statistics` | Registered `@statistic` declarations and recorders. For live values use `get_statistics`. |

## Layer 2 — opp_repl MCP (optional, for workflow automation)

`opp_repl` is a separate Python REPL that exposes its own MCP server for the AI.
Use it when you also need: building projects, running batches, fingerprint tests,
comparing results, or controlling which simulations to launch.

**Start opp_repl with MCP enabled:**
```bash
TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
HASH=$(echo -n "$TOKEN" | sha256sum | cut -d' ' -f1)
opp_repl --load @opp --mcp-port 9966 --mcp-token-hash "$HASH"
```

**Windsurf config entry:**
```json
"opp_repl": {
  "headers": { "Authorization": "Bearer <TOKEN>" },
  "url": "http://localhost:9966/mcp"
}
```

The AI calls `execute_python(code)` to run any opp_repl function.
The `filter` parameter in `run_simulations()` is a regex matched against the
config section name (e.g. `filter="DS_IDLE"` matches `[Config DS_IDLE]`).

## When to use which

| Goal | Use |
|---|---|
| Observe/query a running simulation | Simulation MCP only |
| Step through events, inspect state | Simulation MCP only |
| Launch + interact with one simulation | Simulation MCP only |
| Build project, run batch, run tests | opp_repl MCP |
| AI controls full workflow end-to-end | Both layers |

## Launching the simulation (INET on this machine)

Use `~/omnetpp-dev` (version `6.4.0aipre2`) with `~/inet`. Source both setenvs:

```bash
. ~/omnetpp-dev/setenv && . ~/inet/setenv
cd ~/inet/showcases/general/dhcp
inet -u Qtenv -c BasicDHCP --mcp-server-address localhost:8765 --qtenv-default-run=0 > /tmp/sim.log 2>&1 &
```

- `--qtenv-default-run=0` — auto-loads run 0 in Qtenv so the network is set up immediately and the MCP server starts without any GUI interaction
- The MCP server only starts **after the network is set up** — with Qtenv+`--qtenv-default-run=0` this is automatic; without it you must manually click "Set up network" in the GUI first
- Verify MCP is listening: `ss -tlnp | grep 8765`
- The Windsurf MCP config on this machine uses server name `omnetppX` (not `omnetpp-sim`)

## Saving the canvas image to a file

`get_canvas_image` returns base64 PNG via MCP but does not save to disk. Use this to save it:

```python
import base64, json, urllib.request

req = urllib.request.Request(
    'http://localhost:8765/mcp',
    data=json.dumps({
        'jsonrpc':'2.0','id':1,'method':'tools/call',
        'params':{'name':'get_canvas_image','arguments':{'module_path':'NetworkName','area':'all_elements','margin':5}}
    }).encode(),
    headers={'Content-Type':'application/json','Accept':'application/json'}
)
resp = json.loads(urllib.request.urlopen(req).read())
for item in resp.get('result',{}).get('content',[]):
    if item.get('type') == 'image':
        with open('/path/to/output.png','wb') as f:
            f.write(base64.b64decode(item['data']))
```

- `get_canvas_image` requires **Qtenv** — it returns "not available" under Cmdenv
- `area` options: `all_elements` (bounding box of all graphics), `module_rectangle`, `viewport`

## Recipe comments for showcase figures (canvas & inspector)

Every canvas/topology or module-inspector `.. figure::` in a showcase should be
immediately followed by a **FIGURE RECIPE** comment, so the image can be regenerated
after a config or visualization change. The recipe records only the deltas specific
to that figure; the capture procedure is the `get_canvas_image` /
`open_inspector` + `get_inspector_screenshot` flow above. The anchor / self-check
philosophy — why a visualization-only change is a cheap deterministic replay, and
how the anchor lets the AI decide replay-vs-re-tune — is written once in the
`video-recording` skill and applies identically here.

Format (RST comment — `..` on its own line, content never parsed as RST):

```
.. figure:: media/network.png            ← canvas / topology
..
   FIGURE RECIPE (redo via the "omnetpp-mcp-sim" skill)
   type:     canvas
   config:   BasicDHCP   # ../omnetpp.ini
   seed:     default
   shows:    network topology — dhcpServer, switch, client[0..2] on 100 Mbps Ethernet
   anchor:   initial state (t=0, before run). No timing — the self-check is
             structural: if the module set/links differ, the NED changed.
   capture:  get_canvas_image, area=all_elements; was 728×478
   stamp:    captured 2026-06, INET 4.6

.. figure:: media/lease_table.png        ← module inspector
..
   FIGURE RECIPE (redo via the "omnetpp-mcp-sim" skill)
   type:     inspector
   config:   BasicDHCP   # ../omnetpp.ini
   seed:     default
   shows:    server's `leased` map — three IP→client-MAC bindings (.10/.11/.12)
   target:   dhcpServer → module inspector → `leased` field
   anchor:   after all 3 clients BOUND (~t=2–3s; same anchor as basicdhcp.mp4).
             Fewer/more bindings ⇒ client count or timing changed.
   capture:  open_inspector(dhcpServer) → get_inspector_screenshot, cropped; was 720×170
   stamp:    captured 2026-06, INET 4.6
```

Fields:
- **type** — `canvas` (a `get_canvas_image` render of a module's cCanvas) or
  `inspector` (a `get_inspector_screenshot` of an inspector window).
- **anchor** — for a timed shot (inspector state, or a canvas overlay after an
  event) the sim time to advance to before capturing, re-checkable via the message
  log / `get_simulation_state`. For a pure topology shot there is no timing — the
  anchor is "initial/structural" and the self-check is whether the NED topology
  still matches.
- **target** (inspector only) — which module and which inspector/field to
  `open_inspector` (plus `expand_inspector_tree` if the field is a nested object).
- **capture** — `area` for canvas (`all_elements` etc.) and the last screenshot dims
  as a resolution hint.

## Qtenv vs Cmdenv for MCP

- **Qtenv**: sim starts paused, use `run_simulation` to advance; requires a display (`DISPLAY` or `WAYLAND_DISPLAY`). Required for any tool marked **Qtenv? Y** in the table above — broadly: canvas / inspector screenshots, video recording, log retrieval from the Qtenv buffer, and config / run lifecycle (`setup_config`, `rebuild_network`).
- **Cmdenv**: no display needed, auto-runs to completion. Qtenv-only tools return "not available". Good for querying state/objects/results mid-run via stop conditions, or for batch automation that doesn't need visuals.

## run_simulation behavior

- `run_simulation` with `time_limit` runs until that sim-time **or** the INI `sim-time-limit`, whichever comes first
- After the sim-time-limit is reached the simulation is finished; further `run_simulation` calls won't advance it

## Requirements

- OMNeT++ must be built from the **`aipre` branch** (contains `mcpserver.cc`)
- On this machine: `~/omnetpp-dev` is the aipre build (`6.4.0aipre2`), NOT `~/omnetpp-aipre-GUI/`
- INET at `~/inet` is already built against `~/omnetpp-dev`
