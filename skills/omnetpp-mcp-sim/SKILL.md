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

| Tool | What it does |
|---|---|
| `get_network_topology` | Module tree and connections |
| `get_module_hierarchy` | Full module hierarchy |
| `get_module_info` | Info on a specific module |
| `get_module_connections` | Gate connections of a module |
| `get_simulation_state` | Current sim time, event number, state |
| `get_module_parameters` | Parameter values of a module |
| `get_module_watches` | Watch variables |
| `run_simulation` | Advance sim by time/event limit |
| `stop_simulation` | Stop the running simulation |
| `get_module_log` | Log output of a module |
| `get_module_message_log` | Message log of a module |
| `execute_cpp` | Execute C++ expression in the live sim |
| `find_modules` | Search modules by pattern |
| `find_objects` | Search cObject tree |
| `get_object_children` | Children of a cObject |
| `get_object_details` | Details of a cObject |
| `set_stop_condition` | Set a stop condition |
| `set_debugger_break_condition` | Set a debugger break condition |
| `get_config` | Current INI config |
| `get_canvas_image` | Screenshot of a module canvas (base64 PNG) |
| `get_fes` | Future Event Set contents |
| `get_channel_parameters` | Channel parameters |
| `read_pcap` | Read PCAP capture file |
| `list_result_files` | List result files |

### Available simulation MCP resources

| URI | Content |
|---|---|
| `omnetpp://network-topology` | Network topology as text |
| `omnetpp://ned-source` | NED source of network |
| `omnetpp://config-ini` | Active INI configuration |
| `omnetpp://module/{path}/parameters` | Module parameters |
| `omnetpp://module/{path}/statistics` | Module statistics |
| `omnetpp://result-scalars` | Scalar results |

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

## Qtenv vs Cmdenv for MCP

- **Qtenv**: needed for `get_canvas_image`; sim starts paused, use `run_simulation` to advance; requires a display (`DISPLAY` or `WAYLAND_DISPLAY`)
- **Cmdenv**: no display needed, auto-runs to completion; `get_canvas_image` not available; good for querying state/logs mid-run via stop conditions

## run_simulation behavior

- `run_simulation` with `time_limit` runs until that sim-time **or** the INI `sim-time-limit`, whichever comes first
- After the sim-time-limit is reached the simulation is finished; further `run_simulation` calls won't advance it

## Requirements

- OMNeT++ must be built from the **`aipre` branch** (contains `mcpserver.cc`)
- On this machine: `~/omnetpp-dev` is the aipre build (`6.4.0aipre2`), NOT `~/omnetpp-aipre-GUI/`
- INET at `~/inet` is already built against `~/omnetpp-dev`
