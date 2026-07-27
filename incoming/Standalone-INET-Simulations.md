
---
type: concept
created: 2026-07-15
updated: 2026-07-15
tags: [inet, standalone-simulation, ned-path, opp_run, configurator, gotcha]
---

# Running Standalone INET Simulations Outside the INET Tree

How to create and run a self-contained INET simulation project in its own
directory, without modifying or building inside the INET source tree.

## NED path assembly

INET's `.nedfolders` file lists the NED source directories relative to
`$INET_ROOT`. To include both your project and all of INET's NED files, assemble
the `-n` argument:

```sh
INET_NED=$(cat "$INET_ROOT/.nedfolders" | sed "s|^|$INET_ROOT/|" | tr '\n' ':')
opp_run_release -n ".:$INET_NED" ...
```

If your NED file declares `package myproject;`, it must live in a directory
named `myproject/` — OMNeT++ enforces that the package name matches the
directory path relative to the NED root.

## Loading the INET shared library

Use the full path to the `.dylib`/`.so` (not the `-l` short form, which
prepends `lib`):

```sh
opp_run_release -l "$INET_ROOT/out/clang-release/src/libINET.dylib" ...
```

Or use the `inet` wrapper script (`$INET_ROOT/bin/inet`), which handles the
library path and NED folders automatically — but it requires both OMNeT++
and INET `setenv` scripts to have been sourced.

## Debug/release library mismatch

INET's `libINET.dylib` is linked against a specific OMNeT++ installation
(check with `otool -L libINET.dylib | grep oppsim`). You **must** use
`opp_run_release` (or `opp_run_dbg`) from the same OMNeT++ installation that
INET was built against, otherwise you get:

```
Error: Attempt to load the oppsim shared library more than once.
```

This happens silently when multiple OMNeT++ checkouts exist (e.g.
`omnetpp-dev` and `omnetpp-6.4.0aipre2`) — always verify the `otool -L`
link path.

## Ipv4NetworkConfigurator: `<route>` destination syntax

The `<route>` element's `@destination` attribute uses `L3AddressResolver`
syntax, **not CIDR**. `destination="10.0.1.0/24"` causes a parse error.
Use `destination="*"` with `netmask="255.255.255.0"`, or use host/module
name patterns like `destination="subnet.server[*]"`.

## Ipv4NodeConfigurator + Router: interfaces not configured

When a `Router` node is used with `Ipv4NetworkConfigurator`, the router's
network interfaces may silently fail to get IP addresses. Symptom: the
router's ARP module logs "IPv4 address X not recognized, dropping ARP
packet" for its own IP, and all traffic through the router fails with
100% packet loss.

Root cause: `Ipv4NodeConfigurator`'s `networkConfiguratorModule` parameter
defaults to `"configurator"`. `findModuleFromPar` resolves this relative
path from the node configurator module (`<node>.ipv4.configurator`), and
`findModuleByPath("configurator")` finds the node's **own** per-node
configurator instead of the network-level `Ipv4NetworkConfigurator`. As a
result, `networkConfigurator` is null (or wrong), and
`configureAllInterfaces()` is never called for the router's interfaces.

**Workaround**: put all hosts on the same subnet (no router needed), or
explicitly set the `networkConfiguratorModule` parameter on the router's
node configurator to the absolute path of the network configurator
(e.g. `*.router.ipv4.configurator.networkConfiguratorModule = "configurator"`
resolved from the network level, or use an absolute path like
`ArpDemo.configurator`).

## ARP statistics recording gotcha

The `Arp` module's `@statistic` declarations for `arpRequestSent` and
`arpReplySent` record `sum(packetBytes)` and `vector(packetBytes)`, but the
signal emits `inet::Packet*`. Recording these as vectors causes a runtime
error: "Cannot convert cObject* to double". Use `result-recording-modes =
+count` (scalar only) to avoid this.
