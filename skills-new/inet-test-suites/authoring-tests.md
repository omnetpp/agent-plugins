# Authoring INET .test files (opp_test)

## Structural idioms

- Comments must be **`%#`**, not plain `#`. A plain-`#` line is CONTENT: it
  silently swallows the next directive, and a bare `#` after a `%contains`
  block appends to that block.
- `%contains: stdout` works well on module-attributed log lines; use
  `%subst: /omnetpp:://` to normalize namespaces.
- An "no undisposed objects" check = `%postrun-command` grep +
  `%not-contains`.
- Use **`%expected-failure:`** for spec behaviors INET doesn't model: write
  the test to assert the RFC-correct behavior, let it fail, and it is
  reported as EXPECTEDFAIL (yellow) instead of FAIL — honest, non-red, and it
  flips to PASS automatically if the feature is later implemented. Do not
  invert assertions to make unimplemented behavior "pass".
- Keep tests **independent of examples/**: copy needed networks into
  `tests/module/lib/` (flat topologies and manual configuration are fine
  there). Tests that assert literal lifecycle stage numbers
  (`Doing stage K/N`) break when a stage is inserted — avoid literal stage
  counts where possible.

## Config and logging

- Ini matching is **first-match-wins**: put specific per-module log enables
  BEFORE a `**.cmdenv-log-level=off` catch-all.
- For a `%not-contains` on a module's log line, that module must remain
  log-ENABLED — otherwise the check passes vacuously.
- Eventlog-based tests need `cmdenv-express-mode=false` AND log level on:
  express mode or log-level=off strips log messages from the eventlog too.
- Find which module emits an asserted line with
  `--cmdenv-log-prefix="%C@@ "` (the default prefix is empty, lines are bare).

## Log-size hygiene (test.out bloat)

- `record-vector-results = false` wherever vectors aren't consumed.
- Scalar-only tests: `cmdenv-express-mode = true` (overrides opp_test's
  generated default of false; observed 503 MB → 4 KB).
- Log-asserting tests: `**.cmdenv-log-level = off` + re-enable only the
  modules under test + `cmdenv-event-banners = false`.

## Config gotchas seen in tests

- Overriding an Ethernet interface's MTU needs the trailing wildcard:
  `**.<node>.eth[N].**.mtu = 1280B` — plain `**.<node>.eth[N].mtu` silently
  does not apply.
