---
name: inet-statistical-tests
description: >
  Maintain INET's statistical-test baselines — the separate `statistics/` git repo checked out
  under `inet/`. Drive opp_repl (live MCP session) to run the full statistical-test suite, triage
  result deviations, get per-area human sign-off, re-record the `.sca` baselines, commit them into
  the statistics repo with the INET HEAD commit description embedded, then stop before push. Use
  when asked to update/record/re-record statistical baselines or `.sca` results, refresh the
  statistics repo after an INET change, fix failing statistical tests, or commit new statistics.
---

# INET statistical-test maintenance

Statistical tests detect regressions by comparing each example simulation's scalar (`.sca`)
results against a stored baseline. The baselines live in a **separate git repo** checked out at
`inet/statistics` (remote `inet-framework/statistics`, branch `master`), gitignored by the INET
repo. `inet_project.statistics_folder == "statistics"` points there. Baseline path:
`statistics/<working_dir>/<ini>-<config>-#<run>.sca`.

This skill is driven through the **live opp_repl session via the MCP `execute_python` tool**. Do
not guess opp_repl APIs — read `opp-repl://guide/statistical_tests` and `opp-repl://function/...`
if unsure. Run the full suite in the **foreground and wait** (it is large; see below).

## Two entry points (know the difference)

- `run_statistical_tests(simulation_project=inet_project, ...)` — **compare only**. Returns
  `PASS`/`FAIL`/`ERROR`. Writes nothing to baselines. Use this to *triage*.
- `update_statistical_test_results(simulation_project=inet_project, ...)` — **records baselines**.
  Per config: `INSERT` (no baseline yet) / `UPDATE` (changed → also writes a `.diff`) / `KEEP`
  (byte-identical → **writes nothing**). Records in **debug mode** by default. Use this to *commit*
  validated changes only.

## Preconditions (verify before starting)

- [ ] opp_repl reachable via MCP `execute_python`; `inet_project` is loaded.
- [ ] OMNeT++ **and** INET built in **debug**, **from the toplevel** (so makefiles regenerate for
      new files). A stale/missing debug lib silently records wrong values.
- [ ] **All optional features enabled + makefiles regenerated.** Feature-gated example configs
      `ERROR` (NED type not found) or get recorded against the wrong build otherwise.
- [ ] `statistics/` repo on `master`, **clean** working tree, and freshly **`git pull`**'d.

## The suite

~913 configs over ~264 example dirs — every non-`abstract`, non-`emulation` config
(`get_simulation_tasks` default filter). The full run is long; run it foreground and wait.

## Workflow

### Phase 1 — Triage (read-only)

```python
r = run_statistical_tests(simulation_project=inet_project)
for tr in r.get_fail_results().results:
    print(tr.task.simulation_task.get_parameters_string(), '|', tr.result, '|', tr.reason)
```

- `ERROR` = build / feature / setup / crash problem, **not** a legitimate result change. Fix the
  cause (usually a feature not enabled or a stale build) and re-triage until only genuine `FAIL`s
  remain.
- Group the `FAIL`s by top-level area (`examples/<area>/...`) for review.

### Phase 2 — Per-area sign-off (mandatory)

For each failing area, decide **expected consequence of an INET change** vs **regression**:

- `tr.reason` names the worst-offending scalar. For the full table open the `.csv` next to the
  baseline, or use `tr.recheck(...)` to re-filter without re-running. See [REFERENCE.md](REFERENCE.md).
- Tie each deviation to a specific intended change in INET (check `git -C <inet> log`/`show`).
- **If a deviation is a regression → STOP. Do not re-baseline.** Report it for a code fix.
- Only the areas you have signed off as legitimate proceed to Phase 3.

### Phase 3 — Update signed-off areas

```python
update_statistical_test_results(simulation_project=inet_project,
    working_directory_filter="examples/<area>")   # omit filter only if the whole suite is signed off
```

`INSERT`/`UPDATE` copy the new `.sca` into `statistics/`; `KEEP` writes nothing (**not** a failure).

### Phase 4 — Hygiene + commit (stop before push)

1. **Hygiene** (the statistics repo has historically had stray `.csv`/`.diff` committed):
   - Ensure `statistics/.gitignore` exists and contains `*.diff` and `*.csv` (create if missing).
   - Delete stray artifacts: `find statistics -name '*.diff' -o -name '*.csv' -delete`.
   - Untrack any already-committed ones: `git -C statistics rm --cached <file>`.
2. **Stage baselines only** — never `git add -A`:
   ```bash
   git -C statistics add '*.sca' .gitignore
   ```
3. **Commit with the INET HEAD subject embedded.** Reference INET's HEAD by its short hash and
   *only its first line, in quotes* (not the full body) so the statistics commit records which INET
   change it follows:
   ```bash
   INET=/home/andras/projects/inet
   SUBJ=$(git -C "$INET" log -1 --format='%s')
   HASH=$(git -C "$INET" rev-parse --short HEAD)
   git -C "$INET/statistics" commit \
     -m "<areas>: update statistics after $SUBJ" \
     -m "Recorded against INET $HASH: \"$SUBJ\""
   ```
   (Match the statistics repo's house style — short area-prefixed subject describing *what* and
   *why*, e.g. "update mipv6 results after fixing Home Address option length".)
4. Show `git -C statistics show --stat`. **Then stop and ask for explicit OK before
   `git -C statistics push`.** Never push autonomously.

## Pitfalls

- **Features not enabled** → configs `ERROR` or baselines recorded against the wrong build. Enable
  all + regenerate makefiles first.
- **Stale/absent debug build** → wrong values recorded silently. Rebuild debug from the toplevel.
- **Forgot to pull `statistics/`** → conflicts / clobbering others' baselines.
- **Re-baselining to "go green"** → masks regressions. Every `FAIL` must be explained by an
  intended INET change; otherwise it's a bug to fix, not a result to record.
- **Committing `.diff`/`.csv`** → keep them out via `.gitignore` and stage only `*.sca`.
- **`KEEP` is not a failure** → baseline already matches; no file is written and the temp
  `results/*.sca` is deleted. See memory `opp-repl-statistical-keep-no-write`.
- **`abstract` and `emulation` configs are excluded by design** — don't try to force them in.
- **RNG non-determinism** → a config that varies run-to-run can't hold a stable baseline;
  investigate rather than re-recording it repeatedly.
