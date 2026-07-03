# Simulation Project Branch Cleanup Guide

Step-by-step procedure for cleaning up a feature branch in a simulation project (e.g. INET), producing a validated, rebased branch with clear commit history.

## Inputs

- A **`.opp` file** defining the simulation project
- A **baseline branch** name (e.g. `master`)
- A **feature branch** name (e.g. `topic/infrastructure`) with N commits to clean up

## Prerequisites

- **opp_repl**
- An **omnetpp version** compatible with both baseline and feature branch

## Phase 1: Preparation

### 1.1 Create a separate `.opp` file for the clean branch

Copy the original `.opp` file and modify the test store paths to avoid merge conflicts when rebasing later:

- `fingerprint_store="tests/fingerprint/<feature>-clean.json"`
- `statistics_folder="tests/statistical/<feature>-clean"`

```python
clean_project = SimulationProject(...)  # load from the modified .opp file
```

### 1.2 Check out and build the baseline branch

```bash
git checkout <baseline>
```

Build the simulation project (release mode).

### 1.3 Build the dependency store

Run all simulations on the baseline to build the dependency database:

```python
update_simulation_task_dependencies(simulation_project=clean_project)
```

This maps modified files → NED packages → features → simulation configs.

### 1.4 Create baseline fingerprint and statistical stores

Run all simulations on the baseline to populate the separate test result stores:

```python
update_fingerprint_test_results(simulation_project=clean_project)
update_statistical_test_results(simulation_project=clean_project)
```

These serve as the reference for validating each patch.

### 1.5 Create a clean branch

```bash
git checkout -b <feature>-clean
```

## Phase 2: Branch Review

Before processing individual patches, review the entire feature branch to understand the full scope of changes:

1. Read through all commits (`git log <baseline>..<feature>`)
2. Review the overall diff (`git diff <baseline>..<feature>`)
3. Categorize commits by area/purpose
4. Identify dependencies between commits
5. Plan the ordering: which commits to cherry-pick as-is, which to split, merge, or reorder
6. Document the plan (e.g. in the project-specific plan file)

This upfront review is essential for out-of-order cherry-picking and merging related commits.

## Phase 3: Per-Patch Processing

This is an **interactive** process. Each step requires user confirmation before proceeding.

For each patch (cherry-picked, split, merged, or reordered as determined in Phase 2):

### 3.1 Propose the next step ⏸️ ASK USER

Before touching any code, present to the user:
- **Which commit(s)** from the feature branch will be processed next
- **What the commit does**: summarize the diff, the intent, and the affected areas
- **How it will be applied**: cherry-pick as-is, split, merge with other commits, or reorder
- **Why this ordering**: explain dependencies or rationale for processing it now
- **Expected test outcome**: whether results should be identical or are expected to diverge

**Wait for user confirmation before proceeding.**

### 3.2 Apply the patch

```bash
git cherry-pick <commit>
```

Or apply manually if splitting/merging.

### 3.3 Rewrite the commit message

Make it accurate, detailed, and self-contained:
- Describe *what* the patch does and *why*
- Name affected modules/protocols
- Note expected behavioral changes (if any)

### 3.4 Build

Ensure compilation succeeds. If the build fails:

1. Search other commits on the feature branch for fixes (e.g. later commits that add missing includes, fix typos, or resolve compilation errors introduced by this patch)
2. **⏸️ ASK USER**: explain the build error, identify the fix (with the source commit if found), and ask for explicit permission before making any new code changes
3. If approved, apply the minimal fix and note it in the commit message

### 3.5 Run tests (scoped to affected configs)

```python
run_fingerprint_tests(simulation_project=clean_project, affected_by_modification_filter="<commit>")
run_statistical_tests(simulation_project=clean_project, affected_by_modification_filter="<commit>")
```

The `affected_by_modification_filter` uses the dependency store to test only simulation configs affected by the modified files.

### 3.6 Evaluate results

- **PASS**: proceed to commit
- **FAIL but explainable**: roll test results forward and include updated stores in the commit:
  ```python
  update_fingerprint_test_results(simulation_project=clean_project, affected_by_modification_filter="<commit>")
  update_statistical_test_results(simulation_project=clean_project, affected_by_modification_filter="<commit>")
  ```
  Document the explanation in the commit message.
- **RUNTIME ERROR**: search other commits on the feature branch for fixes (e.g. missing initializations, wrong parameters). **⏸️ ASK USER**: explain the error, identify the fix (with the source commit if found), and ask for explicit permission before making any new code changes
- **FAIL and unexplainable**: STOP — investigate before proceeding

### 3.7 Amend commit

Include validation result in the commit message. If test results were rolled forward, include the updated store files in the commit.

#### Commit message format (PASS)

```
<clear summary line>

<detailed description>

Validation:
  <repr() of fingerprint test results>
  <repr() of statistical test results>
```

#### Commit message format (explained FAIL)

```
<clear summary line>

<detailed description>

Validation:
  <repr() of fingerprint test results>
  <repr() of statistical test results>

  Explanation: <why the differences are expected, e.g. event reordering
  due to synchronous send replacing async at same simulation time>
```

### 3.8 Present the result ⏸️ ASK USER

After the commit is created, present to the user:
- **What was done**: summary of the applied patch and any modifications made
- **Commit message**: the full proposed commit message
- **Test results**: pass/fail summary
- **Updated stores**: if test results were rolled forward, note which files changed
- **Next step preview**: briefly mention what comes next

**Wait for user confirmation before continuing to the next patch.**

## Phase 4: Final Validation

After all patches are applied:

1. **Full fingerprint test run**: `run_fingerprint_tests(simulation_project=clean_project)` over all configs
2. **Full statistical test run**: `run_statistical_tests(simulation_project=clean_project)` over all configs
3. **Summary report**: list of all patches with their verification status (pass / explained-fail)

## Notes

- Use opp_repl through the MCP server when possible for running simulations, querying the dependency store, and running tests
- Patches touching core/common code (directories not belonging to any feature) will conservatively trigger testing of all configs
- The separate store files can be merged back into the standard stores after the branch is finalized
