---
name: simulation-creator
description: skill to create new simulation scenarios or debug existing ones
---

- dont assume something works a certain way in INET, check the ned and the source code
- dont assume the parameter names of modules, check the ned file
- dont assume some module is available, check the ned files
- its ok to add a PCAP recorder/routingtablerecorder to the simulation if you need it to understand whats happening with tcpdump
- use analog-model agnostic radio/radiomedium, and set analog model from ini
if available for the specific technology; use analog-model specific one if possible instead of configuring RadioMedium from scratch.
- use network node types appropriate for the simulation, e.g. wireless or adhoc hosts if there is wireless, etc.
- when using ethernet, set the bitrate in the ini
- make sure to import all needed ned modules
- make sure to position nodes on the canvas so that they dont have the same
position
- dont use automatic positioning such as ring in the display string,
but position the nodes manually
- you can check if the simulation works by running it and checking for errors. how to run a simulation is described in running.md.