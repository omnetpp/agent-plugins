# Cross-cutting INET gotchas

## Configurator wiring

- **`Ipv6NodeConfigurator.networkConfiguratorModule` defaults to `""`**
  (unlike the IPv4 one, which defaults to `"configurator"`) — intentional,
  because MIPv6 needs plain SLAAC. Consequence: any setup expecting
  Ipv6NetworkConfigurator-computed addresses/routes to be APPLIED must set
  `**.ipv6.configurator.networkConfiguratorModule = "configurator"`, or
  interfaces silently stay link-local-only ("off-link" errors, hosts without
  global addresses). This is the single most recurring IPv6 example trap.
- **Ipv6NetworkConfigurator won't drive SLAAC across an EthernetSwitch**: on
  a switched LAN it installs no AdvPrefix on the router interface, so RAs
  carry no Prefix Information option and hosts never get a global address.
  Direct host↔router links work. Workaround: set the advertised prefix via
  the router's per-node `routes` XML
  (`<interface AdvSendAdvertisements='on'><AdvPrefix ...>`).
- **`<interface towards='...'>` fails across an L2 switch** — use
  `names='ethN'` on switched LANs.
- IPv6 `<route>` uses `gateway=`, not `nextHop=`. Host default routes:
  `<route destination='0.0.0.0' netmask='0.0.0.0'>`. With
  `addRemoteRoutes=false`, IPv6 hosts are better served defaults via RA than
  manual `<route>` entries.
- **Ipv4NetworkConfigurator refuses /32 host addresses on a shared wireless
  link** ("Failed to find address prefix"), and a /24 makes all nodes
  on-link — multi-hop MANET addressing needs the routing protocol to
  advertise /32 host routes itself.

## IPv6 asymmetries vs IPv4

- **Ipv6RoutingTable has NO global connected routes** (only fe80::/10) —
  protocols needing connected prefixes must derive them from
  `Ipv6InterfaceData` (advPrefixes / global addresses), not the routing
  table.
- IPv6 global addresses appear only after DAD completes (~0.5 s of sim time)
  and only if the node configurator is wired (see above) — don't read them
  at init.
- INET (correctly) refuses to forward packets with link-local destinations —
  multi-hop IPv6 over an ad-hoc network requires global addresses.
- IPv6 fires ICMPv6 Redirects when forwarding out the arrival interface
  (RFC 4861); on a single-prefix wireless/MANET link this creates a redirect
  storm — set the `Ipv6` module's `sendRedirects=false` there (IPv4 sends no
  redirects at all).

## Module/node wiring

- `Router` defaults `hasUdp=false` — set it for UDP-based routing protocols.
- `Router`'s `*.routingTableModule` wildcard points at the IPv4 table; an
  IPv6-only protocol module must override per-instance
  (`routingTableModule=""` + `routingTableModule6="^.ipv6.routingTable"`).
- Prefer `findProtocolData<X>()` + null check over `getProtocolData<X>()`
  when an interface may legitimately lack that data (e.g. tunnel
  interfaces); `getProtocolData` throws.
- **Packets arriving on an UNNUMBERED interface get local-delivered** (the
  address-match logic treats an unspecified interface address as a match) —
  a TUN interface used for capture/re-injection MUST have an address.

## Naming and files

- **`network` is a reserved NED keyword** — a directory named `network`
  breaks its package declaration; pick another name.
- Generated `*_m.{h,cc}` files are never hand-edited (and are excluded from
  cosmetic cleanups).
