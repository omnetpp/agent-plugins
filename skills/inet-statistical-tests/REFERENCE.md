# Reference — INET statistical-test maintenance

Deeper detail for the workflow in [SKILL.md](SKILL.md). Everything here runs through the opp_repl
MCP `execute_python` session. When in doubt about an API, read the canonical docs first:
`opp-repl://guide/statistical_tests`, `opp-repl://function/run_statistical_tests`,
`opp-repl://function/update_statistical_test_results`, `opp-repl://guide/comparing_simulations`.

## Preparing the build (preconditions)

Record baselines against an **all-features, debug** build, regenerated from the toplevel.

- Enable all features + regenerate makefiles: in INET this is the release-test convention
  ("enable all except `SelfDoc`"). Use `opp_featuretool` (`.oppfeatures` at the project root) or
  the opp_repl feature API, then rebuild. See `opp-repl://guide/feature_tests`.
- Build INET (and OMNeT++) in **debug**, from the project root, not `src/`, so makefiles pick up
  new files. opp_repl's `update_*` defaults to `mode="debug"`; the build must match.
- Confirm `statistics/` is clean and pulled: `git -C statistics status -sb && git -C statistics pull`.

## Triage details

```python
r = run_statistical_tests(simulation_project=inet_project)
r.is_all_results_pass()
fails  = r.get_fail_results().results       # result changed vs baseline
# ERRORs surface as non-PASS with an error_message; inspect:
for tr in r.results:
    if tr.result == "ERROR":
        print(tr.task.simulation_task.get_parameters_string()); print(tr.error_message)
```

`reason` of a `FAIL` is the comma-joined counter summary ending in the worst offender, e.g.
`40 compared, 2 different, largest difference: module = ..., value_stored = ..., value_current = ...`.

### Classifying ERRORs (not result changes — fix the cause)

- **NED type not found / module missing** → an optional feature is disabled. Enable all features +
  regenerate makefiles, rebuild, re-triage.
- **crash / ASSERT / sim aborts** → a real bug or a broken example; fix before recording.
- **build failure** → stale or wrong-mode build; rebuild debug from toplevel.

## Verifying a deviation is legitimate (Phase 2)

The worst offender is in `reason`. For the full set of differing scalars, open the `.csv` written
next to the baseline:

```python
import pandas as pd
tr  = r.get_fail_results().results[0]
cfg = tr.task.simulation_task.simulation_config
proj = cfg.simulation_project
csv = proj.get_full_path(proj.statistics_folder + "/" + cfg.working_directory + "/" +
                         tr.task.get_result_file_name("csv"))
df = pd.read_csv(csv)
print(df.sort_values("relative_error", key=abs, ascending=False).head(20))
```

Re-filter **without re-running** to separate signal from noise:

```python
tr2 = tr.recheck(unbounded_relative_error_threshold=1e-6)   # tolerate float noise
tr3 = tr.recheck(exclude_name_filter="jitter")              # drop a known-noisy scalar
print(tr2.result, tr2.reason)
```

`recheck()` / the `comparison.refilter(...)` and `comparison.only_stored` / `only_current` frames
let you line up renamed modules/scalars and inspect only-side rows. See the statistical_tests guide.

To compare against another INET commit (was this change intended?):

```python
res = compare_statistics_between_commits(inet_project, "HEAD~1", "HEAD",
        working_directory_filter="examples/<area>", config_filter="<config>", run_number=0)
res.results[0].print_different_statistical_results(include_relative_errors=True)
```

Decision rule: every differing scalar must trace to an intended INET change. If any does not, it is
a **regression** — stop, do not update, report it.

## Updating (Phase 3)

```python
# one area at a time as you sign off:
update_statistical_test_results(simulation_project=inet_project,
    working_directory_filter="examples/<area>")
# verdict per config:
for u in _.results:
    print(u.task.get_parameters_string(), '|', u.result)   # INSERT / UPDATE / KEEP
```

`run_protected` copies the new `.sca` into `statistics/` only on `INSERT`/`UPDATE`, then always
deletes the temporary `<working_dir>/results/*.sca`. `KEEP` writes nothing.

## Commit hygiene (Phase 4)

The statistics repo tracks `.sca` only. `.diff` (written on `UPDATE`) and `.csv` (written by the
compare path) land inside the repo tree — keep them out:

```bash
STATS=/home/andras/projects/inet/statistics
# one-time: ensure ignore rules
printf '*.diff\n*.csv\n' >> "$STATS/.gitignore"   # then dedupe/sort as needed
# clean strays + untrack any mistakenly committed
find "$STATS" \( -name '*.diff' -o -name '*.csv' \) -delete
git -C "$STATS" ls-files '*.csv' '*.diff' | xargs -r git -C "$STATS" rm --cached
# stage baselines only
git -C "$STATS" add '*.sca' .gitignore
```

Commit message: short area-prefixed subject + the INET HEAD description in the body (see SKILL.md
Phase 4). House-style examples from the repo history:

- `update mipv6/mipv6roaming results after fixing MIPv6 Home Address option length`
- `eigrp, mpls: follow number format change (printf %.17 to round-trip precision)`
- `follow example/pim/ reorganization, added new examples pim/*_ipv6`

Then `git -C "$STATS" show --stat`, present it, and **wait for explicit OK before `git push`.**
