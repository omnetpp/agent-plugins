# Recipes

## Add a new INET signal with a cObject payload — 3 coordinated steps

1. Declare in `src/inet/common/Simsignals.{h,cc}`: add to the
   `extern INET_API simsignal_t` list in the .h and a `registerSignal("name")`
   line in the .cc.
2. `Register_Abstract_Class(MyInfo);` in a .cc next to the payload class
   definition.
3. `@signal[name](type=inet::MyInfo);` in the **emitting module's** NED file
   (the module whose `emit()` fires, even when called through a helper).

Omitting (3) → fatal "Undeclared signal ... emitted"; omitting (2) → "Wrong
type ... in the @signal property". Both abort at network init — but ONLY under
the **debug fingerprint harness** (module tests run `--check-signals=false`
and pass silently; release leaves the validator off). Mirror an existing
signal (e.g. `ipv6MulticastGroupJoined`) as a template.

Related: a new NED module derived from `LayeredProtocolBase`-style code must
declare the `@signal`s its base emits (`packetReceivedFromUpper`, ...) or
debug runs abort.

## Network-configurator facilities worth knowing (all opt-in, default-neutral)

- `<route destination='10.0.0.0/24'>` / `'2001:db8:2::/64'` — CIDR notation
  accepted in both IPv4 and IPv6 configurator route elements (alternative to
  `netmask`/`prefixLength` attributes; specifying both is an error).
- Ipv6NetworkConfigurator `<interface address='...'>` — assign a full
  explicit IPv6 address (e.g. an RFC 3956 `prefix::RIID`), overriding the
  EUI-64 interface id; must lie within the link prefix.
- `addRemoteRoutes=false` — drop the configurator's precomputed shortest-path
  routes so a routing protocol under test is the sole route source (without
  this, precomputed routes can shadow protocol-learned ones).
  `addManualRoutes` separately gates the XML `<route>` entries.
