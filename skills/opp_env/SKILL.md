---
name: opp_env
description: Maintaining the opp_env project database, especially adding new OMNeT++ versions
---

# opp_env Maintenance Skill

## Project location

The opp_env source is at `/home/andras/projects/opp_env`. The database lives in
`opp_env/database/` and contains:
- `omnetpp.py` – OMNeT++ versions
- `inet.py` – INET versions
- `simu5g.py` – Simu5G versions
- `veins.py` – Veins versions
- `simulte.py` – SimuLTE versions
- `external.py` – all other third-party projects (flora, inetgpl, openflow, plexe, inbaversim, …)

Tests live in `tests/`. The two main smoke tests are:
- `tests/smoketest_list_and_info` – tests `opp_env list` and `opp_env info` output (takes under 1 minute, no installation)
- `tests/smoketest_install_and_run` – tests actual install/run/shell mechanics with a dummy project (takes a few minutes)

## Reading the database

Use the `opp_env` CLI to read and query the database. Do **not** parse Python source directly.

```bash
opp_env list                        # all projects, grouped (one line per project)
opp_env list --flat                 # one line per project+version
opp_env list --names                # project names only
opp_env list --descriptions         # names + descriptions
opp_env list --aliases              # version aliases (e.g. inet-latest -> inet-4.6.0)
opp_env list --matching simu5g veins   # version combos where both can coexist
opp_env list --expand               # default (latest-patchlevel) combos with all deps resolved
opp_env list --expand simu5g        # expand only simu5g
opp_env list --expand simu5g veins  # expand only where simu5g and veins are used together
opp_env list --expand-all simu5g    # ALL combos (not just latest patchlevel per major) for simu5g
opp_env info simu5g                 # human-readable info on all simu5g versions
opp_env info simu5g-1.1             # info on one version
opp_env info --raw inet-4.6.0       # full JSON description (download URL, commands, etc.)
```

Key concepts:
- `--expand` picks the **latest patchlevel** per minor series (e.g. `omnetpp-6.0.3` not `6.0.2`).
- `--expand-all` lists every single version combination.
- `required_projects` in a database entry uses glob patterns like `"6.4.*"`, `"6.3.*"`, etc.

## Adding a new OMNeT++ version (e.g. 6.5.0)

### Step 1 – Add the version to `omnetpp.py`

In `opp_env/database/omnetpp.py`, find the `released_versions` list in `get_project_descriptions()`
and prepend the new version (with `*` for modernized builds):

```python
released_versions = [
    "6.5.0*",   # <-- add here
    "6.4.0*",
    "6.3.0*",
    ...
]
```

A `*` suffix means the version is "modernized" (builds with a modern compiler/tools and has a
compatible setenv script). Almost all 6.x versions, and all new ones should be `*`.

Verify it appeared:
```bash
opp_env list --flat | grep omnetpp-6.5
```

### Step 2 – Update dependent projects

**Rule:** if a project supported the previous version (e.g. `6.4.*`), it is likely to also support
the new version (e.g. `6.5.*`) — but this must be verified by actually building and smoke-testing.
If it did NOT support the previous version, leave it alone.

For each database file, find entries whose `omnetpp` key in `required_projects` contains `"6.4.*"`
and prepend `"6.5.*"` to the list. Work through each file:

**`inet.py`** – `make_inet_project_description()` calls: update the `omnetpp_versions` list for
entries that already include `"6.4.*"`. Example pattern:

```python
["4.6.0", ["6.5.*", "6.4.*", "6.3.*", "6.2.*", "aipre"]],
```
Note: some inet versions may be explicitly *incompatible* with a newer omnetpp due to Nix library
changes (e.g. `inet-4.5.4` is incompatible with `omnetpp-6.4` due to ffmpeg). Check the comments
in `inet.py` carefully and leave those entries unchanged.

**`simu5g.py`** – uses a helper `get_simu5g_project_description()`. The version table at the bottom
lists `[simu5g_version, inet_versions, omnetpp_versions]`. Add `"6.5.*"` to each entry that already
has `"6.4.*"`:

```python
["1.4.3", ["4.6.*", "4.5.*"], ["6.5.*", "6.4.*", "6.3.*", "6.2.*"]],
```

**`veins.py`** – similar table at the bottom. Add `"6.5.*"` to entries with `"6.4.*"`.

**`external.py`** – search for `"6.4.*"` and prepend `"6.5.*"` in each matching `required_projects`
dict. Projects currently updated this way: `flora-1.2.0`, `inetgpl-4.6.0`, `inetgpl-1.0`,
`openflow`, `plexe-3.2`, `inbaversim-0.3.0`, `inbaversim-0.1.0`, `inbaversim-git`.

Quick check after edits:

```bash
opp_env list --expand simu5g        # simu5g-git/latest should now point to omnetpp-6.5.0
opp_env list --expand simu5g veins  # veins-git+simu5g-git should point to omnetpp-6.5.0
opp_env list --expand-all simu5g | wc -l   # count should grow
```

### Step 3 – Update `smoketest_list_and_info`

Run the smoke test to see which assertions break:

```bash
cd /home/andras/projects/opp_env/tests
./smoketest_list_and_info
cat testcase.out   # shows the output of the last failed command
```

The test lives in `tests/smoketest_list_and_info`. Typical things to fix after a new version:

1. **`--expand` assertions that name a specific omnetpp version** – e.g.
   `assert_contains_line 'simu5g-git inet-4.6.0 omnetpp-6.4.0'` becomes `omnetpp-6.5.0` because
   `--expand` always picks the highest compatible version.

2. **`--expand-all` line count assertions** – `assert_num_lines 129 150` must be updated to allow
   the larger count produced by new combinations. Run `opp_env list --expand-all simu5g | wc -l`
   to find the new value and widen the range slightly (±15 lines is typical).

3. **`--grouped` / `--flat` omnetpp version list** – if the test has a literal list of all omnetpp
   versions in an `assert_contains_line`, the new version must be prepended.

Pattern for updating a line count assertion:

```bash
opp_env list --expand-all simu5g | wc -l      # e.g. prints 143
opp_env list --expand-all simu5g veins-5 | wc -l
# then update assert_num_lines <min> <max> so that the real count falls inside
```

### Step 4 – Test new project combinations

For every project combo that now includes the new OMNeT++ version, do a full install + smoke test
in a fresh workspace. The pattern is:

```bash
WORKSPACE=$(mktemp -d /tmp/opp_env_test_XXXXXX)
opp_env install -w $WORKSPACE --init <project-combo> --smoke-test
# e.g.:
opp_env install -w $WORKSPACE --init inet-4.6.0 omnetpp-6.5.0 --smoke-test
opp_env install -w $WORKSPACE --init simu5g-git --smoke-test
opp_env install -w $WORKSPACE --init simu5g-1.4.3 --smoke-test
opp_env install -w $WORKSPACE --init veins-git --smoke-test
```

The `--smoke-test` flag runs the project's own `make smoketest` target after building.
You can also run the smoke test on an already-installed workspace:

```bash
opp_env run -w $WORKSPACE --smoke-test
```

To find exactly which new combos were added, compare before/after:

```bash
opp_env list --expand-all | grep "omnetpp-6.5" | sort > /tmp/new_combos.txt
```

Then test one representative combination per project family (the git/latest version with the new
omnetpp).

**Record every result in the testing log** (see "Testing log" section below).

### Step 4a – Handling build failures

If `opp_env install ... --smoke-test` fails, the build output ends with a compiler/linker error.
Read it carefully and decide whether it is a trivial fix.

**Diagnosing the error:**

```bash
# Re-run without smoke-test to get a cleaner build log:
opp_env install -w $WORKSPACE --init <project> 2>&1 | tail -50

# Or enter the environment interactively to try things:
opp_env shell -w $WORKSPACE <project>
# Inside the shell: try 'make' and read the error
```

**Trivial fix — add a `sed` patch command:**
A trivial fix is one or a few `sed -i` substitutions that reliably handle the problem across all
affected files — typically renamed symbols, C++ syntax tightening, or simple API renames.
Add it to `patch_commands` of the project's database entry, guarded by a version condition.
Examples from `inet.py`:

```python
# renamed symbol (omnetpp API change)
"sed -i 's|cResultFilterDescriptor|cResultFilterType|' src/inet/common/figures/DelegateSignalConfigurator.cc" if inet_version == "3.4.0" else "",

# compiler C++ conformance fix, applied across all matching files
"for f in $(grep -Rls 'defined(linux)'); do sed -i 's|defined(linux)|defined(__linux__)|' $f; done",

# fix flexible array member in union
"sed -i 's|info\\[\\]|info[0]|' src/inet/common/serializer/sctp/headers/sctphdr.h" if inet_version.startswith("3.") else "",
```

Always put an explanatory comment directly above the `sed` command:
```python
# fix "error: flexible array member in union" in sctphdr.h — C11 tightened the rule
"sed -i 's|info\\[\\]|info[0]|' src/inet/common/serializer/sctp/headers/sctphdr.h" if ...,
```

After adding the patch, re-run the install from scratch:
```bash
rm -rf $WORKSPACE/<project-folder>
opp_env install -w $WORKSPACE <project> --smoke-test
```

**Non-trivial fix — drop support and document why:**
If the required changes span many files, require significant logic changes, or involve an
incompatible library ABI or deep API redesign, do NOT support the new omnetpp version for that
project. Revert the Step 2 edit for this entry and add an inline comment explaining the problem.
Examples from the database:

```python
# In inet.py — inline comment on the version table entry:
["4.5.4", ["6.3.*", "6.2.*", "6.1.*", "6.0.*"]],  # Incompatible with omnetpp-6.4 due to incompatible ffmpeg version in newer NixOS

["4.1.2", ["5.4.2", "5.4.1", "5.5.*"]], # with omnetpp-5.6.*, 5.7.*: error: Direct deletion of a module is illegal, use deleteModule() instead

# In veins.py — comment block above the table entry:
# removed omnetpp-5.5.0 from all versions due to segfault in smoke test
# removed inet-4.2.*/4.3.* due to subproject build errors:
#   VeinsInetTransparentMobility.h:69: error: virtual function 'getCurrentPosition' has different return type
```

### Step 4b – Handling smoke test failures

If the build succeeds but the smoke test fails:
```bash
# Run the smoke test command manually inside the environment:
opp_env shell -w $WORKSPACE <project>
# Inside: run the smoke_test_commands shown in opp_env info --raw <project>
```

- **Trivial config issue** (wrong path, missing flag) → fix in `smoke_test_commands` or `setenv_commands`.
- **Model crash or wrong output** → treat as a non-trivial failure: remove support for the new
  omnetpp version and document why (same pattern as build failures above).
- **Suspected fluke** (timing-sensitive, random seed) → re-run once to confirm before deciding.

### Step 4c – Testing log

Keep a log file at `tests/results/omnetpp-X.Y.Z.md` (create the `results/` dir if needed).
Record every combination tested, the outcome, any patches added, and any dropped support. Format:

```markdown
# Test results for omnetpp-6.5.0 support (YYYY-MM-DD)

## inet-4.6.0 + omnetpp-6.5.0
- **Result:** PASS (install + smoke test)

## simu5g-git + inet-4.6.0 + omnetpp-6.5.0
- **Result:** PASS

## simu5g-1.4.3 + inet-4.6.0 + omnetpp-6.5.0
- **Result:** FAIL (build error)
- **Error:** `error: 'cFoo' was not declared in this scope` in `src/stack/mac/LteMacEnbD2D.cc`
- **Assessment:** trivial — single symbol rename
- **Fix:** added to `simu5g.py` `patch_commands`:
  `sed -i 's|cFoo|cBar|' src/stack/mac/LteMacEnbD2D.cc`
- **Re-test:** PASS after patch

## veins-5.3.1 + inet-4.6.0 + omnetpp-6.5.0
- **Result:** FAIL (smoke test crash)
- **Error:** segfault inside `TraCI::connect()` — reproducible
- **Assessment:** non-trivial (SUMO API incompatibility, would require significant veins_inet changes)
- **Action:** removed `"6.5.*"` from veins-5.3.1 entry; added comment in `veins.py`:
  `# omnetpp-6.5 not supported: segfault in TraCI::connect() due to SUMO API incompatibility`
```

### Step 5 – Commit

Typical commit sequence used historically:

1. `omnetpp.py: added version X.Y.Z`
2. `inet: added omnetpp-X.Y support to inet-A.B`
3. `Add omnetpp-X.Y support to all projects that support omnetpp-X.(Y-1)` (simu5g, veins, external)
4. `tests: smoketest_list_and_info updated`

## Running the smoke tests

```bash
cd /home/andras/projects/opp_env/tests

# Fast test (no installation needed, just CLI queries):
./smoketest_list_and_info

# Full install/run test (slow, requires Nix):
./smoketest_install_and_run
```

Both scripts source `testlib.inc` which provides `run`, `assert_contains_line`, `assert_num_lines`,
`assert_not_contains`. On failure, the offending output is in `testcase.out`; the full log of all
commands is in `test.out`.

## Useful one-liners

```bash
# Show which omnetpp versions a project supports
opp_env info --raw inet-4.6.0 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['required_projects'])"

# List all project combos newly enabled by an omnetpp version
opp_env list --expand-all | grep "omnetpp-6.5"

# Check that a version alias resolves correctly
opp_env list --aliases | grep omnetpp-6

# Count total combinations
opp_env list --expand-all | wc -l
```