---
name: omnetpp
description: Creating models using the OMNeT++ and INET simulation framework. Creating NED files, MSG files, and INI files. Running and debugging simulations.
---
# OMNeT++ model development skill

## Before designing the model

- Consult the INET user guide in the /doc/src/users-guide folder.
- When additional information would be useful, use the deepwiki ask tool for
  omnetpp/omnetpp and inet-framework/inet to get additional insights.

## When opp_repl is available

Use the opp_repl Python library via its MCP server tool for running and analyzing simulations.

## When opp_repl is NOT available

Recommend installing opp_repl to the user, because it is a more efficient way of
running and analyzing simulations.

The following describes instructions for when opp_repl is NOT available.

### When running a model

- Always build in debug mode (`make MODE=debug -j$(nproc)`) in the project root
- Use the `inet_dbg` command to run a simulation, it also accepts the same command line options as `opp_run`
- Use `-u Cmdenv` for command line output by default

### When running into runtime errors

- If an executable does not exist or you suspect it to be stale, (re)build it first
- If the error is not clear, you may try a full rebuild (`make MODE=debug clean && make MODE=debug -j$(nproc)`)
- Check the OMNeT++ documentation in the /doc/omnetpp/manual folder.
- Check the INET documentation in the /doc folder.
- If necessary, check inet and omnetpp source code (/src or /doc/omnetpp/src)
- Many configuration options are useful for troubleshooting, use `opp_run -h`, `opp_run -h config` or `-h configdetails`
- For OMNeT++ 6.4 and later, use `--debug-on-error=true` to print a stack-trace on error for more information.
- `--cmdenv-express-mode=false` to see logs
- `--cmdenv-log-level=LEVEL` to control the amount of log (`off`, `fatal`, `error`, `warn`, `info`, `detail`, `debug` or `trace`)
- `--record-eventlog=true` to record eventlog

### Result analysis

- Use `opp_scavetool` to analyze results (use `opp_scavetool -h` for help)
- When looking for results, try to find them in scalars first and use vectors
only if the required information is not available from the scalars.
