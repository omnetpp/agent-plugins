# Protocol conformance tests (tests/protocol) and unit tests

## The protocol-test framework

`tests/protocol/` is a spec-driven, black-box conformance framework
(shared library in `tests/protocol/lib`; suites are siblings, e.g. `wifi`,
`ipv6`). Run a suite:

```
cd tests/protocol/<suite> && ../lib/build.sh && ./run-tests.sh
```

(`../lib/libprotocoltest.so` must be built first; opp tools on PATH.)

## Authoring principles

- **Observe at the interface (the wire), not internal modules.** RFCs specify
  packets on the wire; interface-level observation survives host-internal
  refactors. SEND = `on("X.eth[0].mac").signal("packetSentToLower")`, RECEIVE
  = `...packetReceivedFromLower`; at the MAC, the full frame (L2+L3+payload
  headers) is readable in BOTH directions. (Also pragmatic: e.g. the Ipv6
  core module does not emit `packetSentToLower` itself.)
- **Events with no positive packet** (e.g. DAD success = absence of a
  defending NA): assert on scalar signals (`startDad`, `dadCompleted`,
  `dadFailed`, with `.is(1)`), subscribed at the **host** level
  (`on("host1").signal("dadFailed")`), not on the protocol submodule.
- **PacketFilter cannot compare address fields to string literals**
  (`ipv6.destAddress == "ff02::2"` fails) — use a C++ lambda with
  support-header helpers (e.g. `Ipv6TestSupport.h`: `ipv6Dst`, `isDadProbe`,
  `nsTarget`, `raHasAutonomousPrefix`).
- **`.within(t)` is an ABSOLUTE deadline** measured from the step's anchor
  (simulation start for step 0) — NOT a duration after `.notBefore()`. Write
  `notBefore(3.9).within(6.0)`, never `within(2.0)` meaning "2s later".
- **Timing realism**: some behaviors only occur after the network settles
  (e.g. redirects after routing converges) — use wide windows. To provoke a
  Packet Too Big that comes back unfragmented, reduce only the FAR interface's
  MTU.
- Use `%expected-failure:` for RFC behaviors INET doesn't model (see
  authoring-tests.md).

## Unit tests

- Runner: `inet_run_unit_tests` — same flag semantics as module tests
  (`-f` filter, `-m` build mode).
- Standalone opp_test harness recipe (for a one-off unit test):
  ```
  mkdir tests/unit/work; opp_test gen -v X.test; cd work
  opp_makemake -f --deep -I$ROOT/src -L$ROOT/src -lINET_dbg -o work; make MODE=debug; cd ..
  LD_LIBRARY_PATH=$ROOT/out/clang-debug/src opp_test run -v X.test
  ```
  (debug lib, as for every test run; `rm -rf work` afterwards — it is generated).
- **Every new serializer gets a round-trip (serialize→deserialize) unit
  test.** It is the ONLY thing exercising the deserialize path: simulation
  receivers keep the C++ chunk object, so even `~tND` fingerprints exercise
  serialization only.
