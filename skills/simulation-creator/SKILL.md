---
name: simulation-creator
description: skill to create new simulation scenarios or debug existing ones
---

- dont assume something works a certain way in INET, check the ned and the source code
- dont assume the parameter names of modules, check the ned file
- dont assume some module is available, check the ned files
- pcap capture is a debugging aid, not part of the model. Only commit pcap config if the showcase/tutorial text actually refers to it (e.g. OSPF tutorial Step 25). Otherwise add it to capture/inspect, then remove it — don't commit it.
- to capture, use the per-node built-in recorder (no NED edits needed): `*.<node>.numPcapRecorders = 1` and `*.<node>.pcapRecorder[0].pcapFile = "${resultdir}/${configname}.pcap"`. The recorder sits inside the host, so its default moduleNamePatterns (`eth[*] ppp[*] wlan[*]`) already match that host's interfaces. this needs checksumMode and fcsMode set to computed.
- gotcha: a top-level PcapRecorder submodule whose moduleNamePatterns starts with `.` (e.g. `.^`) is NOT a silencer — the leading dot subscribes it to its parent (the whole network), so it captures everything. To actually disable such a recorder, set moduleNamePatterns to "" or remove the submodule.
- a routingtablerecorder can likewise be added ad-hoc to watch routing-table changes.
- use analog-model agnostic radio/radiomedium, and set analog model from ini
if available for the specific technology; use analog-model specific one if possible instead of configuring RadioMedium from scratch.
- use network node types appropriate for the simulation, e.g. wireless or adhoc hosts if there is wireless, etc.
- when using ethernet, set the bitrate in the ini
- make sure to import all needed ned modules
- make sure to position nodes on the canvas so that they dont have the same
position
- dont use automatic positioning such as ring in the display string,
but position the nodes manually
- never write behavioral claims based on assumptions about protocol standards — check the actual INET implementation in the .cc files (e.g. INET may use INIT-REBOOT instead of full DORA after a DHCP client restart, which differs from what you might assume from the RFC)
- you can check if the simulation works by running it and checking for errors. how to run a simulation is described in the omnetpp skill.