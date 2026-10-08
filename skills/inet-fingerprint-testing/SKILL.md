---
name: inet-fingerprint-testing
description: >
  INET Framework specifics for fingerprint testing: the tests/fingerprint/fingerprinttest
  runner and its flags, baseline CSV layout, the re-recording workflow, and INET-specific
  gotchas (INET_ROOT/setenv trap, protocol-registry insertions, signal-check asymmetry).
  Use when running, triaging, or re-recording fingerprint tests in the INET repo. Builds on
  the generic omnetpp-fingerprint-testing skill — read that first for concepts, ingredient
  semantics, drift interpretation, and the acceptance discipline.
---

# INET fingerprint testing

First read [../omnetpp-fingerprint-testing/SKILL.md](../omnetpp-fingerprint-testing/SKILL.md)
(concepts, workflow, discipline). Everything below is INET-specific.

## Runner

```
cd <inet-root> && source ./setenv -q
cd tests/fingerprint && rm -f *.UPDATED *.ERROR *.FAILED
./fingerprinttest -s -F tyf -m <regex> 2>&1 | tee /tmp/fp.log
```

Flags (NOTE: `-m` and `-f` do not mean what they mean in other INET test runners):

- `-s` — run the **release** binary (`opp_run_release`); `-d` — run the
  **debug** binary (`opp_run_dbg`). With neither flag the plain `opp_run` runs,
  which is the release build — so a "debug run" needs `-d` explicitly. Debug
  is much slower but is the only mode where the signal validator runs (see
  gotchas).
- `-m <regex>` — **line filter**: regex matched against the whole CSV line
  (directory, ini file, config name all match). This is NOT a build-mode flag.
- `-f <ingredient>` — run only rows with that ingredient (e.g. `-f tplx`).
- `-F <ingredient>` — skip an ingredient; `-F tyf` (graphical, unreliable) is
  recommended by the tool itself.
- CSV file(s) as positional args; default is the full standard set.

Baselines: `tests/fingerprint/*.csv`. The main table is `examples.csv`
(4-ingredient rows: `tplx;~tNl;~tND;tyf`); topic CSVs (e.g.
`mipv6-refactoring.csv` with `~tNlb` rows) cover specific areas. A CSV header
comment may declare the file an invariant ("must NOT change") — treat those
rows as a hard byte-identical gate.

## The INET_ROOT trap (do this every time)

The `fingerprinttest` wrapper executes `$INET_ROOT/bin/inet_fingerprinttest
--directory $INET_ROOT` — if the shell's `INET_ROOT`/`PATH` point at a
*different checkout or worktree* (a fresh shell may inherit one), the suite
runs THAT tree's library against THIS tree's CSVs. The result looks exactly
like a stale build or mysterious mismatches, and rebuilding changes nothing.
Since shell state does not persist between agent tool calls, start **every**
command block with:

```
cd <inet-root> && source ./setenv -q -r 2>/dev/null; source ./setenv -q 2>/dev/null
```

and verify `echo $INET_ROOT` prints this checkout. Only the run step is
affected; builds are cwd-relative.

## Re-recording

- Purge stale artifacts first (see generic skill; command above).
- Run from where the CSV's working-directory column resolves (use the
  project root for `bin/inet_fingerprinttest <csv>` invocations — the CSV
  working dirs are cwd-relative).
- Failing rows produce `<name>.csv.UPDATED`; after verifying and justifying
  every change per-ingredient, `cp` it over the CSV and re-run the affected
  rows to confirm PASS.
- **New example**: add a row with placeholder hashes
  (`0000-0000/tplx;0000-0000/~tNl;...`), run the test to generate `.UPDATED`,
  copy it over, re-run to confirm. The CSV row's sim-time-limit MUST match the
  ini file's, or the recorded hash is for a different run length.
- The opp_repl/python equivalents (`run_fingerprint_tests`,
  `update_fingerprint_test_results`) default to **debug** mode.

## INET-specific gotchas

- **Adding a `Protocol` registry entry** (in `Protocol.cc`) renumbers the ids
  of all later-defined protocols; expect deterministic `~tNlb` re-records for
  PPP-framed examples (Ethernet-framed ones are immune, ids sort early). See
  the generic drift guide; this is not a regression.
- **Signal-check asymmetry**: module tests run with `--check-signals=false`;
  the fingerprint suite in *debug* mode is the ONLY harness that validates
  `@signal` declarations. After adding signals, run the debug fingerprint
  suite — an undeclared signal aborts every affected sim at init (shows up as
  errors=N, not as fingerprint drift).
- **`~tND` needs serializers + computed checksums**: rows with `~tND` require
  every chunk to have a serializer and force computed checksum/CRC/FCS modes;
  a missing serializer aborts the run. `~tNl` rows never serialize — passing
  `~tNl` proves nothing about serializers.
- The chunk-length-vs-serializer consistency check is **debug-only**: release
  runs silently emit malformed packets where debug would throw. Suspicious
  `~tND` behavior? Re-run in debug (drop `-s`).
