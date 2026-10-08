---
name: simu5g-fingerprint-testing
description: >
  Simu5G specifics for fingerprint testing: the tests/fingerprint/fingerprints runner (NOTE:
  -m is a substring filter here, unlike INET), the fp_stdout.log-only triage protocol, and
  updating simulations.csv. Use when running, triaging, or re-recording fingerprint tests in
  the Simu5G repo. Builds on the generic omnetpp-fingerprint-testing skill — read that first
  for concepts, ingredient semantics, drift interpretation, and the acceptance discipline.
---

# Simu5G fingerprint testing

First read [../omnetpp-fingerprint-testing/SKILL.md](../omnetpp-fingerprint-testing/SKILL.md).
Everything below is Simu5G-specific.

## Runner

```
(cd tests/fingerprint/ && ./fingerprints -d) 2>&1 | tee fp_stdout.log
```

- Runs all simulations (examples/, showcases/, ...) against the baselines in
  `tests/fingerprint/simulations.csv`. Full suite ≈ a few minutes.
- `-d` = debug binary.
- **`-m <substring>`** — filter to simulations whose config name/directory
  contains any of the given substrings. This is a plain SUBSTRING match
  (unlike INET's `fingerprinttest`, where `-m` takes a regex). Partial runs
  are for intermediate steps only — finish with the full suite.

## Triage protocol

`fp_stdout.log` is the ONLY output to look at — do NOT read the `.ERROR` /
`.FAILED` artifact files.

1. `tail -10 fp_stdout.log` — the summary must be `OK` or
   `FAILED (failures=N)` with **zero errors** (see the generic skill for the
   errors-vs-failures rule).
2. For errors: `grep 'ERROR (should be PASS)' fp_stdout.log` — each match
   carries the simulation directory, args, and full error message; re-run
   manually for a stack trace.

## Re-recording

This section replaces the generic skill's "never update baselines without
consent" for Simu5G.

Re-record and commit WITHOUT asking when (a) the run has zero errors and
(b) every ingredient that moved is explained with evidence, one of:

- `tilx` only (`tplx`, `~tNl`, `sz` identical): module ids shifted by a new or
  moved module or channel.
- `sz` moves, and an A/B of the two builds on the affected config shows the
  recorded values identical as SETS (scalars as (module, name, value),
  statistic fields as (module, name, field, value)): only the recording order
  changed.
- `tplx`/`tilx` move with `~tNl` AND `sz` identical: events at the same
  instant inside a node were reordered; nothing was scheduled or cancelled,
  wire traffic and results are unchanged. Name the reordered events.

State the explanation and the evidence in the commit message (e.g.
"fingerprint change: tilx only, module ids shifted by ...") and in the report.

ASK first when any row moves on `~tNl`, when recorded values differ, when
`tplx` moves without identical `~tNl` and `sz`, or when a mover cannot be
explained. That is a behavior change: present the evidence and let the user
decide. NEVER re-record while errors exist.

The runner writes a full `<name>.csv.UPDATED` next to each CSV that had
mismatches (`simulations.csv`, `simulations_d2d.csv`):

```
cp tests/fingerprint/simulations.csv.UPDATED tests/fingerprint/simulations.csv
```

When merging several `-m` runs, take only the rows that differ from the
original CSV -- each `.UPDATED` is a full CSV, so a later one would overwrite
earlier updates with stale rows.

Then spot-check a few affected simulations with `-m` rather than re-running
the full suite.

## When the suite can be skipped

Skip the fingerprint run after changes that obviously cannot affect behavior:

- comments (C++, NED, MSG, ini), documentation, WHATSNEW;
- display string details that nothing reads: icons, colors, labels, submodule
  positions inside node and NIC compounds;
- WATCH-only changes.

Still build, and make sure the NED files still load.

Two display string changes are NOT inert:

- **Positions of wireless nodes** (UEs, base stations, ...) in a network.
  INET's mobility modules (StationaryMobility, LinearMobility, ...) default to
  `initFromDisplayString = true`, so the icon position IS the simulated
  position unless the ini sets the initial coordinates. Moving such a node
  changes the simulated reality: re-run the affected simulations, and expect
  real value changes (= ask before re-recording).
- **Connection display strings with routing hints** (`m=...`): they need a
  channel, so an IdealChannel is created, which shifts module ids -> `tilx`
  moves. Run the suite; `tilx`-only drift is re-recordable without asking.
