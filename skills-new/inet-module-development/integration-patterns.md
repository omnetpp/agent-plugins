# Integration patterns

## Adding a protocol to nodes — additive, fingerprint-inert

New functionality enters node types WITHOUT perturbing existing simulations,
proven by byte-identical fingerprints of the whole suite. Mechanisms, by
preference:

- a default-off boolean switch + conditional submodule in the node NED
  (`hasBabel`, `hasMipv6`, `hasIpsec`, ...);
- activating an existing dormant `like`-interface slot (e.g.
  `LinkLayerNodeBase`'s `llc` slot via `llc.typename=...`);
- implementing the protocol `like IApp` so it slots into `app[]` with no
  node-NED surgery;
- a new node type extending `Router`/`StandardHost`, leaving the base NED
  untouched.

## Protocol module structure

- **One module + per-packet tags beats per-interface sockets**: a single
  `UdpSocket` with `InterfaceReq`/`L3AddressReq` tags per send; one LLC
  socket opened on the local SAP receives from ALL interfaces.
- **Do ALL protocol setup (interface config, socket bind, activation) in
  `handleStartOperation()`, not spread across `initialize()` stages** —
  `RoutingProtocolBase::initialize` triggers `handleStartOperation` BEFORE
  later init stages run, so stage-based setup comes too late.
- **Gateway-module + gateless-submodule pattern** for multi-instance
  protocols (e.g. one `Vrrp` module owning the IP gates, demuxing to
  dynamically created per-instance submodules driven by C++ calls via
  `Enter_Method`) — keeps per-instance statistics and timers without gate
  plumbing.
- Parse protocol config XML inline with `cXMLElement` rather than a separate
  configurator module.

## Messages and serializers

- Messages are **typed `FieldsChunk` classes, not raw TLV byte arrays**:
  TLVs become named fields/record arrays; near-identical message variants
  collapse into one class with a type field.
- **Serializer byte count MUST equal the chunk's `chunkLength`.** Keep every
  builder's length formula in sync with the serializer (count bytes
  included); for variable-length messages, add wire-length helper functions
  called via `setChunkLength()` before insertion. Guard `setChunkLength`
  with `isMutable()` when re-sending reused chunks. Mismatch symptom:
  debug-only crashes, or uninitialized-byte padding → non-deterministic
  `~tND` fingerprints.
- `B(x).get()` returns BYTES, not bits.
- Every new serializer gets a round-trip unit test (see
  inet-test-suites/protocol-tests.md — nothing else exercises deserialize).

## Dual-stack (IPv4 + IPv6) design

- Gate per-AF logic on routing-table presence (`rt4`/`rt6` refs, e.g.
  `ModuleRefByPar`); install `Ipv4Route`/`Ipv6Route` per AF; run per-AF
  hello/adjacency in the neighbor's own family; IPv6-only nodes must work
  unaffected.
- Derive connected prefixes per family: IPv4 from interface addr+netmask;
  IPv6 from `Ipv6InterfaceData` advPrefixes/global addresses — the IPv6
  routing table has NO global connected routes (see gotchas.md).
- Admin distances come from the shared `RouteAdminDist` enum.
- **Adjacency source ≠ route next-hop**: protocol adjacency traffic may use
  link-local sources (per spec), but installed IPv6 route next-hops should be
  the neighbor's GLOBAL address (link-local next-hops forward poorly in
  INET). In SPF-style route propagation, propagate BOTH families' next hops —
  a v4-only propagation branch gives multi-hop IPv6 routes an unspecified
  next hop (routing loop) while IPv4 works.
- **Flooding protocols need explicit DB sync on adjacency-up** (flood the
  LSDB to a new neighbor) — fire-and-forget flooding misses LSPs received
  before the adjacency formed.
- **Wireless shared media need batching + jitter**: one packet per protocol
  event at the same instant triggers "another transmission already started";
  batch per-(destination, interface) and jitter flush timers
  (`*= uniform(0.5, 1.0)`).

## Porting from older INET-based codebases (ANSA and similar)

- **Build an API-translation cookbook first**: find code that exists in BOTH
  the old codebase and current INET (e.g. EIGRP made the ANSA→INET 4.x trip)
  and diff it for a concrete rewrite map (`cPacket`→`Chunk`,
  control-info→tags, `InterfaceEntry`→`NetworkInterface`,
  `getModuleFromPar`→`ModuleRefByPar`, `info()`→`str()`, ...).
- **Phase the port**, green at every commit: (1) constants/value types +
  module shell + feature entry; (2) .msg messages + serializer + round-trip
  test; (3) tables/adjacency; (4) first runnable example; (5)
  flooding/route exchange; (6) route install + end-to-end ping example;
  (7) fingerprints + branch cleanup.
- **Reuse mainline code instead of re-porting** (check whether support
  classes already migrated); skip dead substrate (hollow relay shims,
  commented-out datapaths); drop non-protocol fields (display-string fields
  in messages).
- Deferring serializers to a late phase is acceptable precedent (some
  mainline protocols still have none) — but then `~tND` fingerprints are
  unavailable for those examples.
- **Data-plane capture/re-injection**: the clean mechanism is a TUN
  interface + `TunSocket` (route captured prefixes to the tun iface;
  decapsulate and re-inject via the socket); alternative: `INetfilter` hooks
  returning STOLEN. The tun interface must have an address (see gotchas).
