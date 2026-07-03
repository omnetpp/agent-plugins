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

After every mismatch is verified as an expected consequence of the change
(and NEVER while errors exist, and never without user consent):

```
cp tests/fingerprint/simulations.csv.UPDATED tests/fingerprint/simulations.csv
```

Then spot-check a few affected simulations with `-m` rather than re-running
the full suite.
