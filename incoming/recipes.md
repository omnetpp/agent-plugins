# Recipes

*Extracted 2026-07-03 from Claude session memory (`~/.claude/projects/-home-andras-projects-inet/memory/`). Raw material for future INET dev skills — unedited: may contain machine-specific paths and session-specific observations. Source memory file cited per bullet.*

### Add a new INET signal with a cObject payload — 3 coordinated steps (inet-new-signal-three-steps.md)
1. Declare in `src/inet/common/Simsignals.{h,cc}`: add to the `extern INET_API simsignal_t` comma-list in the .h + a `registerSignal("name")` line in the .cc.
2. `Register_Abstract_Class(MyInfo);` in a .cc next to the payload class definition.
3. `@signal[name](type=inet::MyInfo);` in the **emitting module's** NED (e.g. `InterfaceTable.ned` for signals emitted via `ownerp->getInterfaceTable()->emit(...)`).
- Omitting (3) → fatal "Undeclared signal '...' emitted (@signal missing...)"; omitting (2) → "Wrong type '...' in the @signal property ... should be ... a registered class name". Both abort at network-init — but ONLY under the debug fingerprint harness (module tests run `--check-signals=false`). Mirror an existing signal (e.g. `ipv6MulticastGroupJoined`) as a template.
- LayeredProtocolBase-derived modules emit `packetReceivedFromUpper` etc. — a new NED for such a module must declare those `@signal`s or debug runs abort. (mipv6-tunneling-refactor-plan.md)

### Live status label above a node in Qtenv (inet-node-status-displaystring.md)
- Every INET node inherits `string displayStringTextFormat @mutable` from `inet.common.Module`/`ModuleMixin` (NodeBase extends Module); `refreshDisplay()` writes the `t` display tag — just set it in the ini, no NED change, no InfoVisualizer: `*.MN[*].displayStringTextFormat = "AP: {.wlan[0].mib.ssid}\n{.ipv6.mipv6.mobilityStatus}"`.
- `{expr}` resolves against WATCH'd variables / string params; `{a.b.name}` reaches into submodules (`internal::doResolveExpression` in `src/inet/common/ModuleMixin.cc` does `getModuleByPath(a.b)` then matches a child named `name`).
- **GOTCHA (OMNeT++ 6):** bare `getModuleByPath("wlan[0].mib")` resolves relative to the **top-level network**, not the module → "Module not found". Use a **LEADING DOT** for module-relative: `{.wlan[0].mib.ssid}`, `{.ipv6.mipv6.x}` (ccomponent.h: ".queue[2].srv" = relative to this module).
- For computed values add `WATCH_EXPR("name", <expr>)` in the submodule's `initialize()`. `%`-directives exist: `%n` name, `%p` path, `%t` text tag, `%s` str().
- **Display-only:** `refreshDisplay()` runs under Qtenv, NOT Cmdenv — can't verify from Cmdenv (a bad path won't error there); never affects behavior or fingerprints. Verify visually in Qtenv.

### Configurator features added (opt-in, fingerprint-neutral by default)
- IPv4+IPv6 configurator `<route>` accept combined CIDR in `destination` (`destination='2001:db8:2::/64'` / `'10.0.0.0/24'`), equivalent to the separate `prefixLength`/`netmask` attribute; both at once = error. Implemented by stripping trailing `/N` before `L3AddressResolver().resolve(...)` (which throws on embedded `/`). (inet-configurator-route-prefix-notation.md)
- `Ipv6NetworkConfigurator` `<interface>` accepts **`@address`** = full explicit IPv6 address (e.g. RFC 3956 `prefix::RIID`), overriding the EUI-64 token; must lie within the link prefix (validated → `cRuntimeError`); on a link with no `@prefix` template it also seeds the link's /64. Full address only — no IPv4-style `x`-wildcards. (inet-ipv6-explicit-address-todo.md)
- `addRemoteRoutes`/`addManualRoutes` params on both Ipv4/Ipv6 configurators (default `true` = no fingerprint movement). `addRemoteRoutes=false` drops gateway-set shortest-path routes so a routing protocol under test is the sole route source (was the BGP-over-IPv6 pain: precomputed remotes made decisionProcess discard learned routes). `addManualRoutes` gates the XML `<route>` entries, independent of `addStaticRoutes`. Known deferred inefficiency: with `addRemoteRoutes=false` the shortest-path calc still runs then discards. (inet-configurator-route-switches.md)
