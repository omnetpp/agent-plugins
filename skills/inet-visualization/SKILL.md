---
name: inet-visualization
description: How to configure visualization in INET simulations. Covers all visualizer types, which to use for wired vs wireless, multi-visualizer setup, packet filters, and common pitfalls.
---

# INET Visualization Configuration

## Integrated Visualizer Setup

By default, networks extending `WiredNetworkBase` or `WirelessNetworkBase` include an `IntegratedCanvasVisualizer` (single instance of each visualizer submodule).

To use **multiple instances** of the same visualizer type (e.g., color-coded arrows for different traffic types), switch to `IntegratedMultiCanvasVisualizer`:

```ini
**.visualizer.typename = "IntegratedMultiCanvasVisualizer"
**.visualizer.numChannelVisualizers = 3
```

## Link Activity Visualizers — Which One to Use

### DataLinkVisualizer (wired and wireless — PREFERRED for wired)
- Tracks MAC-to-MAC activity using chunk IDs
- Works for both wired and wireless
- Standard choice for showing link-level activity in wired networks
- **PITFALL: Multicast/broadcast causes cross-links** — the visualizer stores one "last sender" per chunk ID, so when multiple routers forward the same multicast data, the last sender overwrites earlier ones, producing incorrect arrows
- Parameter: `displayLinks = true`

```ini
**.visualizer.dataLinkVisualizer[0].displayLinks = true
**.visualizer.dataLinkVisualizer[0].packetFilter = "UdpBasicAppData*"
**.visualizer.dataLinkVisualizer[0].lineColor = "blue"
```

### ChannelVisualizer (wired networks — alternative)
- Subscribes to the `messageSent` signal emitted by OMNeT++ **channels**
- Shows correct per-hop arrows because it resolves source/destination from the channel's gates
- **No multicast cross-link problem** — each channel event maps to exactly one physical hop
- Useful alternative when DataLinkVisualizer produces incorrect arrows (multicast scenarios)
- Parameter: `displayChannelActivity = true`

### PhysicalLinkVisualizer (wireless ONLY)
- Checks `dynamic_cast<IRadio*>(module)` — only matches wireless radio modules
- Does NOT work with wired interfaces (Ethernet MACs/PHYs don't implement IRadio)
- Parameter: `displayLinks = true`

### NetworkRouteVisualizer (end-to-end, network layer)
- Shows the full path a packet takes through the network at the IP layer
- Good for visualizing routing paths
- Works for both wired and wireless
- Parameter: `displayRoutes = true`

### TransportRouteVisualizer (end-to-end, transport layer)
- Shows transport-layer (TCP/UDP) connection paths
- Parameter: `displayRoutes = true`

## Summary: Choosing a Link Visualizer

| Network Type | Best Choice | Why |
|---|---|---|
| Wired unicast | `ChannelVisualizer` or `DataLinkVisualizer` | Both work correctly |
| Wired multicast | `ChannelVisualizer` | DataLinkVisualizer has cross-link bug |
| Wireless | `PhysicalLinkVisualizer` or `DataLinkVisualizer` | PhysicalLink shows radio-to-radio hops |
| End-to-end path | `NetworkRouteVisualizer` | Shows full IP-level route |

## Common Parameters (shared by link visualizers)

```ini
**.visualizer.dataLinkVisualizer[0].displayLinks = true
**.visualizer.dataLinkVisualizer[0].nodeFilter = "R* or receiver*"
**.visualizer.dataLinkVisualizer[0].interfaceFilter = "eth0"
**.visualizer.dataLinkVisualizer[0].packetFilter = "UdpBasicAppData*"
**.visualizer.dataLinkVisualizer[0].lineColor = "blue"
**.visualizer.dataLinkVisualizer[0].lineStyle = "solid"  # solid, dashed, dotted
**.visualizer.dataLinkVisualizer[0].lineWidth = 3
**.visualizer.dataLinkVisualizer[0].labelFormat = "%n"   # %n=name, %c=class
**.visualizer.dataLinkVisualizer[0].fadeOutMode = "simulationTime"
**.visualizer.dataLinkVisualizer[0].fadeOutTime = 2s
```

## Other Visualizers Quick Reference

### InterfaceTableVisualizer
Shows interface info (IP addresses, state) as labels on nodes.
```ini
**.visualizer.interfaceTableVisualizer[0].displayInterfaceTables = true
**.visualizer.interfaceTableVisualizer[0].nodeFilter = "R*"
```

### RoutingTableVisualizer
Shows routing table entries as arrows indicating next hops.
```ini
**.visualizer.routingTableVisualizer[0].displayRoutingTables = true
**.visualizer.routingTableVisualizer[0].destinationFilter = "receiver1"
```

### StatisticVisualizer
Displays a statistic value (signal) as a label near nodes.
```ini
**.visualizer.statisticVisualizer[0].displayStatistics = true
**.visualizer.statisticVisualizer[0].signalName = "packetReceived"
**.visualizer.statisticVisualizer[0].statisticExpression = "count"
```

### PacketDropVisualizer
Shows where and why packets are dropped.
```ini
**.visualizer.packetDropVisualizer[0].displayPacketDrops = true
**.visualizer.packetDropVisualizer[0].nodeFilter = "*"
**.visualizer.packetDropVisualizer[0].labelFormat = "%n (%r)"  # %r=reason
```

### MediumVisualizer (wireless only)
Shows radio signal propagation, transmission/reception ranges.
```ini
**.visualizer.mediumVisualizer[0].displaySignals = true
**.visualizer.mediumVisualizer[0].displayCommunicationRanges = true
**.visualizer.mediumVisualizer[0].displayInterferenceRanges = true
```

### RadioVisualizer (wireless only)
Shows radio state (idle, transmitting, receiving, switching).
```ini
**.visualizer.radioVisualizer[0].displayRadios = true
**.visualizer.radioVisualizer[0].radioFilter = "**"
```

### MobilityVisualizer
Shows movement trail and velocity vectors.
```ini
**.visualizer.mobilityVisualizer[0].displayMobility = true
**.visualizer.mobilityVisualizer[0].displayMovementTrails = true
**.visualizer.mobilityVisualizer[0].displayVelocities = true
```

### Ieee80211Visualizer
Shows 802.11 association info (SSID, connected AP).
```ini
**.visualizer.ieee80211Visualizer[0].displayAssociations = true
```

### QueueVisualizer
Shows queue fill levels.
```ini
**.visualizer.queueVisualizer[0].displayQueues = true
**.visualizer.queueVisualizer[0].queueFilter = "**.queue"
```

### GateScheduleVisualizer (TSN)
Shows time-aware shaper gate schedules.
```ini
**.visualizer.gateScheduleVisualizer[0].displayGateSchedules = true
```

### LinkBreakVisualizer (wireless)
Shows link breaks (useful for MANET routing).
```ini
**.visualizer.linkBreakVisualizer[0].displayLinkBreaks = true
```

### TransportConnectionVisualizer
Shows TCP connection endpoints with icons.
```ini
**.visualizer.transportConnectionVisualizer[0].displayTransportConnections = true
```

### InfoVisualizer
Shows submodule info (display string `t=` tag content).
```ini
**.visualizer.infoVisualizer[0].displayInfos = true
**.visualizer.infoVisualizer[0].modules = "*.R*.pim"
```

## Color-Coded Multi-Visualizer Pattern

A common pattern for showing different traffic types with different colors:

```ini
**.visualizer.typename = "IntegratedMultiCanvasVisualizer"
**.visualizer.numChannelVisualizers = 3

# UDP data traffic (blue)
**.visualizer.channelVisualizer[0].displayChannelActivity = true
**.visualizer.channelVisualizer[0].packetFilter = "UdpBasicAppData*"
**.visualizer.channelVisualizer[0].lineColor = "blue"
**.visualizer.channelVisualizer[0].labelColor = "blue"

# Control traffic (red)
**.visualizer.channelVisualizer[1].displayChannelActivity = true
**.visualizer.channelVisualizer[1].packetFilter = "Pim* or PIM*"
**.visualizer.channelVisualizer[1].lineColor = "red"
**.visualizer.channelVisualizer[1].labelColor = "red"

# Everything else (gray)
**.visualizer.channelVisualizer[2].displayChannelActivity = true
**.visualizer.channelVisualizer[2].packetFilter = "not UdpBasicAppData* and not Pim* and not PIM*"
**.visualizer.channelVisualizer[2].lineColor = "gray"
**.visualizer.channelVisualizer[2].labelColor = "gray"
```

## Common Pitfalls

1. **PhysicalLinkVisualizer in wired networks**: Does nothing — it only works with IRadio (wireless). Use ChannelVisualizer or DataLinkVisualizer instead.

2. **DataLinkVisualizer with multicast**: Produces incorrect cross-link arrows because it uses a single `lastModule` map per chunk ID. When multiple routers forward the same multicast data, the last sender overwrites. Use ChannelVisualizer for wired multicast.

3. **IntegratedCanvasVisualizer vs IntegratedMultiCanvasVisualizer**: The default `IntegratedCanvasVisualizer` has exactly one instance of each visualizer submodule. You MUST switch to `IntegratedMultiCanvasVisualizer` to use `numXxxVisualizers` parameters.

4. **Forgetting displayLinks/displayChannelActivity**: All visualizers are disabled by default. You must explicitly set `displayLinks = true` or `displayChannelActivity = true`.

5. **packetFilter format**: Uses `cMatchExpression` on packet name by default. For protocol-based filtering use `expr(has(udp))` syntax or name glob patterns like `"UdpBasicAppData*"`.
