---
name: inet-test-suites
description: >
  Running and authoring INET's module, unit, and protocol-conformance test suites: runner
  flags (-f is the filter, -m is build mode!), the debug-lib requirement, timeout wrapping,
  reading test.err vs test.out, .test-file authoring idioms, and the tests/protocol black-box
  framework. Use when running or writing INET module/unit/protocol tests or triaging their
  failures. Fingerprint tests: see inet-fingerprint-testing; statistical tests: see
  inet-statistical-tests.
---

# INET test suites

The suites and their skills:

| Suite | Location | Runner / skill |
|---|---|---|
| Fingerprint | tests/fingerprint | `fingerprinttest` — see inet-fingerprint-testing |
| Module | tests/module | `inet_run_module_tests` (below) |
| Unit | tests/unit | `inet_run_unit_tests` (below) |
| Protocol conformance | tests/protocol | `run-tests.sh` — see [protocol-tests.md](protocol-tests.md) |
| Statistical | statistics/ repo | opp_repl — see inet-statistical-tests |

Authoring `.test` files (opp_test idioms, log hygiene):
see [authoring-tests.md](authoring-tests.md).

## Running module tests

```
cd <inet-root> && source ./setenv -q
cd tests/module && rm -rf work && timeout 600 inet_run_module_tests -f '<regex>'
```

- **`-f <regex>` is the test-name filter** (`--filter`). `-m` is the BUILD
  MODE (`debug`/`release`) — `-m 'IPv6_'` fails with "invalid choice". (If a
  document shows `-m` as a filter, it is wrong.) Same semantics for
  `inet_run_unit_tests`. Other flags: `-w` working dir, `--no-build` to skip
  the build step.
- **Always wrap in `timeout`** — a buggy change can create an infinite packet
  loop that hangs forever. The full suite is on the order of a minute; a few
  minutes of timeout is safe. A multi-GB `work/<Test>/test.out` means a loop —
  delete it (disk!).
- Module tests run the **DEBUG** library. Build both modes first (see
  inet-dev-environment) or you test stale code.
- Module tests run with `--check-signals=false` — they CANNOT catch missing
  `@signal` declarations; only the debug fingerprint suite validates those.

## Triaging a failing test

- **Read `work/<Test>/test.err` FIRST.** The simulation's abort message
  (ASSERT failure, cRuntimeError, "Error: ..." line) goes to stderr =
  `test.err`; `test.out` holds only the stdout EV log. Grepping only test.out
  makes a hard crash look like "the sim just stopped / a packet vanished".
- PASS/FAIL is decided by the simulation's **exit code**, independent of the
  `.test` file's `%contains` assertions — commenting out an assertion cannot
  mask a crash.
- "undisposed object" lines are warnings, not the failure cause; with a
  nonzero exit and only "undisposed object" visible in test.out, the real
  error is in test.err (the orphaned object is usually a casualty of the
  aborted event).
- Reproduce interactively: `cd tests/module/work/<Test> && inet_dbg -u Qtenv
  omnetpp.ini` (see omnetpp-sim-debugging for gdb/eventlog techniques).
