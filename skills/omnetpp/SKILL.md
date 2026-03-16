---
name: omnetpp
description: Creating models using the OMNeT++ and INET simulation framework. Creating NED files, MSG files, and INI files. Running and debugging simulations.
---
# OMNeT++ model development skill

## Before designing the model

- consult the INET user guide in the /doc/src/users-guide folder.
- when additional information would be useful, use the deepwiki ask tool for omnetpp/omnetpp and inet-framework/inet to get additional insigths.

## when running a model

- always build in debug mode (`make MODE=debug -j$(nproc)`) in the project root
- use the `inet_dbg` command to run a simulation, it also accepts the same command line options as `opp_run`
- use `-u Cmdenv` for command line output by default

## when running into runtime errors

- if an executable does not exist or you suspect it to be stale, (re)build it first
- if the error is not clear, you may try a full rebuild (`make MODE=debug clean && make MODE=debug -j$(nproc)`)
- Check the OMNeT++ documentation in the /doc/omnetpp/manual folder.
- Check the INET documentation in the /doc folder.
- if necessary, check inet and omnetpp source code (/src or /doc/omnetpp/src)
- many configuration options are useful for troubleshoothing, use `opp_run -h`, `opp_run -h config` or `-h configdetails`
- for omnetpp 6.4 and later, use `--debug-on-error=true` to print a stack-trace on error for more information.
- `--cmdenv-express-mode=false` to see logs
- `--cmdenv-log-level=LEVEL` to control the amount of log (`off`, `fatal`, `error`, `warn`, `info`, `detail`, `debug` or `trace`)
- `--record-eventlog=true` to record eventlog

## result analysis

- use `opp_scavetool` to analyze results (use `opp_scavetool -h` for help)
- when looking for results, try to find them in scalars first and use vectors
only if the required information is not available from the scalars.
