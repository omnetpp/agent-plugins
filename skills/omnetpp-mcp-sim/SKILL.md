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
| `run_simulation` | Advance sim by time/event limit, optional run mode (normal/fast/express); under Qtenv the result carries a `status` (`stopped`/`finished`/`error`) + `message` (see below) | | |
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

**Dialogs** — normally empty during MCP work. While an MCP request is processed, Qtenv routes `confirm()` / `displayException()` (errors, end-of-sim notices) to the log buffer instead of a blocking `QMessageBox`. Use these for the rare dialog that bypasses that path. Note: a runtime **error** during `run_simulation` is reported via that tool's `status`/`message` result (see "Reading run outcome & errors" below), so you rarely need `list_dialogs` for errors — it's mainly for dialogs raised outside a request (e.g. at startup / network setup).

| Tool | What it does | Qtenv? | Clang? |
|---|---|---|---|
| `list_dialogs` | List visible top-level modal dialogs (index, title, text, buttons, kind) | Y | |
| `dismiss_dialog` | Click a button on a visible dialog (default: accept / OK on topmost) | Y | |

**State queries**

| Tool | What it does | Qtenv? | Clang? |
|---|---|---|---|
| `get_simulation_state` | Current sim time, event number, state, next-event info; under Qtenv also an `animation` object mirroring the Animation Parameters dialog (active profile, model-driven animation_speed, and both `normal`/`fast` profiles' playback speed + min/max animation clamps) | | |
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
| `get_canvas_image` | Render a module's graphics to a PNG (base64-encoded) — the "Export to Image..." context menu item | Y | |
| `open_inspector` | Open a Qtenv inspector window for any cObject by full path | Y | |
| `get_inspector_screenshot` | Capture the inspector widget as a PNG (with optional resize) | Y | |
| `expand_inspector_tree` | Expand tree nodes in object / object-tree inspectors before screenshotting | Y | |

**Video recording (Qtenv)**

| Tool | What it does | Qtenv? | Clang? |
|---|---|---|---|
| `start_video_recording` | Begin frame-by-frame PNG capture of the main window | Y | |
| `stop_video_recording` | Stop capture and return a ready-to-run ffmpeg command | Y | |
| `record_video` | One-shot wrapper: start + run_simulation + stop | Y | |
| `set_animation_parameters` | Set a profile's playback-speed slider and/or min/max animation-speed clamps (mirrors the Animation Parameters dialog) | Y | |

See the `video-recording` skill for the recommended workflow. `set_animation_parameters` mirrors
Qtenv's "Animation Parameters" dialog: pick a `profile` (`normal`/`fast`) and set any of
`playback_speed` (clipped to 0.01–100 in normal mode), `min_animation_speed`, `max_animation_speed`
(0 clears a clamp). Read the current values back from the `animation` object in
`get_simulation_state`. During recording, sim-time-per-frame = `(1/fps) × animation_speed ×
playback_speed`, so a lower playback speed captures more frames (slow-motion / finer detail) and a
higher one captures fewer (coarser / faster coverage).

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

## Network / topology screenshots

`get_canvas_image` is the programmatic equivalent of Qtenv's right-click
**"Export to Image..."**: it renders the module's *live* graphical inspector, so the
current zoom, icon scale, label settings and every canvas figure — INET visualizer
annotations included — come out exactly as shown on screen, but with no window
chrome, toolbar, scrollbars or zoom overlay. **Prefer it over
`get_inspector_screenshot` for network/topology figures** — nothing has to be
cropped afterwards.

Parameters:

- `area`: `module_rectangle` (the module's background rectangle, i.e. the playground;
  default, and what "Export to Image" defaults to), `all_elements` (bounding box of all
  graphics — crops tighter when the playground has empty regions), `viewport` (exactly
  what the inspector currently shows)
- `margin`: pixels around the captured area (default 5)
- `output_file`: also save the PNG there (relative paths resolve against the
  simulation's working directory). The image comes back either way — this just saves
  decoding the base64 yourself
- Response carries a metadata block alongside the image: `width`, `height`,
  `zoom_factor`, `area`, `margin`, and `file` if saved
- Requires **Qtenv**, and requires an **open graphical inspector** for the module. For
  the network one always exists; for a submodule, `set_canvas_view` or `open_inspector`
  opens it. Otherwise you get an error — deliberately, because the alternative
  (rendering offscreen at zoom 1) silently produces garbage.
- Images are downscaled so neither side exceeds 2048 px

### The zoom loop

**Zoom is a composition choice, not a resolution knob.** Icons have a fixed pixel size
regardless of zoom, while the layout and the canvas figures scale with it. So zooming
out doesn't just shrink the picture — it crowds submodules, their name labels, and
visualizer annotations into each other, and clips figures. Zooming in spreads them out
but wastes space and may not fit. You cannot render small and upscale.

There is no formula for the right zoom. Capture, **look at the image**, and judge it
the way a person would:

- do the visualizer annotations overlap each other, or the node icons?
- is there a large empty region? (try `area: all_elements`, or zoom in)
- is anything clipped at the edges?
- is the text legible at the size this will appear in the docs?

Then adjust and re-capture:

```
set_canvas_view {module_path: "<root>", fit: true}     → rough framing
get_canvas_image {module_path: "<root>"}               → look at it, judge
set_canvas_view {module_path: "<root>", zoom_by: 1.3}  → adjust
get_canvas_image {module_path: "<root>"}               → look again
...
get_canvas_image {module_path: "<root>", output_file: "doc/media/Topology.png"}
```

**Record the final `zoom` in the FIGURE RECIPE.** Qtenv persists per-network zoom in
`~/.qtenvrc` as `type2-embedded-<NetworkName>-zoomfactor`, so on the machine where the
figure was first made the framing looks right "for free" — and on a fresh checkout or
CI it silently falls back to zoom 1. A recipe that names an explicit
`set_canvas_view {zoom: N}` replays anywhere in one shot; the judge-loop above is only
needed when creating or re-tuning a figure.

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
   capture:  set_canvas_view zoom=1.69 → get_canvas_image area=module_rectangle
             margin=5; was 728×478
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
- **capture** — for canvas: the **explicit `set_canvas_view` zoom** (not "fit" — the
  zoom that the judge-loop settled on, so a replay needs no loop), plus `area` and
  `margin`; for inspector: the `open_inspector`/crop steps. Either way end with the
  last dims as a resolution hint.

## Qtenv vs Cmdenv for MCP

- **Qtenv**: sim starts paused, use `run_simulation` to advance; requires a display (`DISPLAY` or `WAYLAND_DISPLAY`). Required for any tool marked **Qtenv? Y** in the table above — broadly: canvas / inspector screenshots, video recording, log retrieval from the Qtenv buffer, and config / run lifecycle (`setup_config`, `rebuild_network`).
- **Cmdenv**: no display needed, auto-runs to completion. Qtenv-only tools return "not available". Good for querying state/objects/results mid-run via stop conditions, or for batch automation that doesn't need visuals.

## run_simulation behavior

- `run_simulation` with `time_limit` runs until that sim-time **or** the INI `sim-time-limit`, whichever comes first
- After the sim-time-limit is reached the simulation is finished; further `run_simulation` calls won't advance it

### Reading run outcome & errors (Qtenv)

Under Qtenv, `run_simulation` catches simulation exceptions internally (a human would
normally see them in a modal `QMessageBox`, which an agent cannot read). The outcome is
surfaced in the tool result instead — **always check the `status` field**:

| `status` | Meaning | `message` |
|---|---|---|
| `stopped` | A run/event limit or stop condition was reached; more events may remain | — |
| `finished` | The simulation ended normally (e.g. sim-time-limit hit, or a module called `endSimulation()`) | termination reason |
| `error` | A **runtime error** stopped the run — the run did NOT complete as intended | full error text (module path + cRuntimeError message) |

The same error text is also available afterwards as the `lastError` field of
`get_simulation_state` (present only while the last run's state is error). `Cmdenv` does
not wrap errors this way — there a runtime error propagates out as a normal MCP tool error.

## Requirements

- OMNeT++ must be built from the **`aipre` branch** (contains `mcpserver.cc`)
- On this machine: `~/omnetpp-dev` is the aipre build (`6.4.0aipre2`), NOT `~/omnetpp-aipre-GUI/`
- INET at `~/inet` is already built against `~/omnetpp-dev`
