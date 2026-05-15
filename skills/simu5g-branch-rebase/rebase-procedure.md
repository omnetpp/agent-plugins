# Rebasing a Simu5G Topic Branch onto a New Base

Procedure for rebasing a topic branch from one upstream release to another
(e.g., from v1.4.1 to v1.4.2). Produces a validated, buildable branch with
periodically updated fingerprint test results at specific commits.

## Inputs

- **repo_path**: Path to the Simu5G repository
- **topic_branch**: The branch to rebase (e.g., `rebase-auto`)
- **old_base**: The current base of the topic branch (e.g., `v1.4.1`)
- **new_base**: The target base to rebase onto (e.g., `v1.4.2`)

## Prerequisites

- OMNeT++ built and on PATH (`opp_run` or `opp_run_dbg` accessible)
- `INET_ROOT` set, INET built (debug mode)
- `SIMU5G_ROOT` set to the repository path
- INET version compatible with the new base

## Phase 1: Pre-Analysis

Before starting the rebase, analyze the upstream gap and the topic branch to
predict conflicts and plan the approach.

### 1.1 Upstream gap analysis

```bash
git log --oneline <old_base>..<new_base>
git diff --stat <old_base>..<new_base>
```

Identify:
- **API changes**: Renamed/removed/changed function signatures
- **File renames/moves**: Track with `git diff --diff-filter=R <old_base>..<new_base>`
- **Deleted code**: Functions or files removed that the topic may depend on
- **Semantic changes**: Behavioral changes in shared code

### 1.2 Topic branch analysis

```bash
git log --oneline <old_base>..<topic_branch>
git diff --stat <old_base>..<topic_branch>
```

Categorize topic commits:
- **Additive** (new files only): Unlikely to conflict
- **Modifying** (changes existing files): Check against upstream changes
- **Fingerprint-update** commits: Will need regeneration at specific commits

### 1.3 Conflict prediction

Compute the file intersection: files modified in both the upstream gap and
the topic branch. For each overlapping file, examine the nature of changes:
- Mechanical API renames → easy to resolve
- Structural refactoring → may need incremental approach
- Both sides made semantic changes → highest risk

### 1.4 Strategy decision

- If conflict prediction shows mostly mechanical/additive changes → **straight rebase**
- If conflict prediction shows heavy overlap with semantic changes → **incremental rebase**
  (advance through upstream commits in small batches)

Default: attempt straight rebase first, fall back to incremental if confidence
drops during conflict resolution.

## Phase 2: Execute Rebase

### 2.1 Create working branch

```bash
git checkout <topic_branch>
git checkout -b <topic_branch>-on-<new_base>
```

Never mutate the source branch. Always work on a new branch.

### 2.2 Start the rebase

```bash
GIT_EDITOR=true git rebase --empty=keep --onto <new_base> <old_base>
```

The `--empty=keep` flag is critical: it preserves commits that become empty
after conflict resolution. Without it, fingerprint-update commits whose CSV
changes are subsumed by an earlier regeneration will be silently dropped.

### 2.3 Conflict resolution

When a conflict occurs, resolve autonomously using these strategies
(in order of preference):

1. **Mechanical adaptation**: The topic uses an API that was renamed/changed
   upstream. Apply the same transformation to the topic's code.
   Example: `binder_->getRlcByNodeId(id, AM)` → `getRlcByMacNodeId(binder_, id, AM)`

2. **Context shift**: Surrounding code changed (new parameters, moved lines).
   Re-apply the topic commit's intent in the new context.

3. **Semantic merge**: Both upstream and topic made meaningful changes to the
   same code. Understand both intents and combine them.

Never drop commits, leave at least an empty marker commit in place with
a commit message that explains what got dropped and why.
For commits that only update fingerprint test results, resolve the conflict
by taking the version from the commit being rebased (`--theirs` in rebase
terminology). Do NOT resolve by taking `--ours` (the already-applied side),
because that makes the commit empty. Even with `--empty=keep`, an empty
fingerprint commit is confusing — it's better to keep a meaningful diff so
that Phase 4 regeneration can amend it with the correct values.

Take care not to drop any new test cases that might have been added between
the old and new base. Also, don't pointlessly reintroduce test cases that
were dropped between the old and new base.

**Confidence-based fallback**: If a conflict cannot be resolved with high
confidence (e.g., the correct resolution is ambiguous, or multiple semantic
changes interleave), fall back to incremental rebase:

```bash
git rebase --abort
# Find an intermediate commit in the upstream gap before the problematic change
git rebase --onto <intermediate_commit> <old_base>
# Then rebase the result onto the remaining upstream commits
git rebase --onto <new_base> <intermediate_commit>
```

### 2.4 Intent preservation

The right mindset for conflict resolution: understand the INTENT of the
original commit, and do the same kind of change on the new base. Preserve
the intent of the topic branch commits, not their exact text.

Cherry-picking is significantly weaker than rebase (does not track file
renames/moves). Never fall back to cherry-pick.

## Phase 3: Build Verification (per commit)

After the rebase completes (or during an interactive rebase), verify each
commit builds:

```bash
git rebase -i --exec "make makefiles && make MODE=debug -j\$(nproc)" <new_base>
```

Or manually iterate:

```bash
git log --oneline <new_base>..<topic_branch>-on-<new_base>
# For each commit:
git checkout <commit>
make makefiles
make MODE=debug -j$(nproc)
```

### 3.1 Handling build failures

If a commit fails to build (e.g., it calls a function that was renamed
upstream but didn't produce a textual conflict):

1. Identify the cause (compare against pre-analysis API changes)
2. Create a **fixup commit** with the minimal fix:
   ```bash
   # fix the code
   # stage only the files changed by the fix to the commit
   git commit -m "fixup: adapt <description> to <new_base> API change

   <explanation of what changed and why>"
   ```

Do NOT amend the original commit. Use separate fixup commits with descriptive
messages.

### 3.2 Non-trivial build failures

If a build failure cannot be resolved mechanically (e.g., requires
understanding complex interactions), stop and report the issue to the user
with:
- The build error
- Which upstream change caused the incompatibility
- Proposed fix (if any)

## Phase 4: Fingerprint Validation (per fingerprint-update commit)

The topic branch contains commits that update `tests/fingerprint/simulations.csv`.
After rebasing onto the new base, these fingerprint values will be wrong
(they were computed on the old base). Each such commit needs regeneration.

### 4.1 Identify fingerprint-update commits

```bash
git log --oneline <new_base>..<topic_branch>-on-<new_base> -- tests/fingerprint/simulations.csv
```

### 4.2 For each fingerprint-update commit

1. Check out the commit
2. Build: `make makefiles && make MODE=debug -j$(nproc)`
3. Run all fingerprint tests:
   ```bash
   (cd tests/fingerprint && ./fingerprints -d) 2>&1 | tee fp_stdout.log
   ```
4. Check results:
   ```bash
   tail -10 fp_stdout.log
   ```
   - **errors** = runtime crashes → investigate and fix (add fixup commit)
   - **failures** = fingerprint mismatches → analyze and update

5. Analyze mismatches:
   - Compare which simulations/ingredients changed vs. the original commit
     on the old base (read the original commit message for expectations)
   - Verify the set of affected simulations is consistent with expectations
   - Note any extra or missing changes (due to new base interactions)

6. Update the CSV:
   ```bash
   cp tests/fingerprint/simulations.csv.UPDATED tests/fingerprint/simulations.csv
   ```

7. Amend the commit with updated CSV and enhanced message:
   ```bash
   git add tests/fingerprint/simulations.csv
   git commit --amend
   ```

   The commit message should include a summary of fingerprint changes:
   ```
   <original subject line>

   <original body if any>

   Fingerprint changes on <new_base> base:
     - Simulations affected: <list or count>
     - Ingredients changed: <e.g., "tplx and ~tNl" or "sz only">
     - Reason: <explanation, e.g., "statistics rename in v1.4.2 changes sz
       fingerprints for all simulations">
   ```

### 4.3 Checking fingerprint test results

See `fingerprints.md` for detailed instructions on interpreting results.
Key points:
- Use `fp_stdout.log` as the sole source of truth
- `grep 'ERROR (should be PASS)' fp_stdout.log` for runtime errors
- Errors are NEVER acceptable — fix before proceeding
- Failures (mismatches) are acceptable only if explained

## Phase 5: Final Report

After all commits are processed, produce a summary:

- Total commits rebased: N
- Conflicts resolved: list with brief description of each
- Fixup commits added: list with descriptions
- Fingerprint changes: summary per fingerprint-update commit
- Issues requiring follow-up (if any)

## Notes

- **Commit messages**: Keep original commit messages unchanged. Exceptions:
  fingerprint-update commits get enhanced messages with change analysis.
- **Fixup commits**: Always add as separate commits with descriptive messages.
  The user can squash them later with `git rebase -i --autosquash` if desired.
- **Never force-push** without explicit user consent.
- **GIT_EDITOR=true** and **GIT_PAGER=cat** should be set to prevent
  interactive editor/pager prompts during automated rebase operations.
