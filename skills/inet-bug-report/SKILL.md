---
name: inet-bug-report
description: >
  Take a bug report for INET, OMNeT++ or a derived simulation project — a Markdown file or a plain
  description — and act on it end to end: reproduce the bug at the commit the report names, verify
  it again on master, search recent topic branches and GitHub for an existing fix, write and test a
  fix, then stop for the user's confirmation before filing the issue and opening the pull request.
  Use when handed a bug report, a bug .md file, or a description of a defect, and asked to verify,
  triage, investigate, fix, file, or "run the whole pipeline on" it.
---

# INET bug report: verify, triage, fix, file

The input is a bug report written by someone else — an agent that hit the defect during other work,
or the user in a sentence. It may be wrong, stale, or thin. Your job is the flow below. Most of its
exits are legitimate and produce no fix at all.

## The flow

    read the report                     what it is, how to reproduce, the git hash
    worktree A at that hash, build
    verify the bug there                reproduce it, and prove the behaviour is wrong
        not reproducible  -> vary build mode, user interface, config/run/seed; then STOP
    worktree B at origin/master, build
    record the test baseline            while B is still pristine
    verify the bug in master
        absent -> fixed since?          find the commit, report it, STOP
               -> defect present, trigger absent?   real latent bug, continue
               -> defect absent too?    the reported branch introduced it, hand it back, STOP
    if present in master:
        search recent topic branches for a fix
            found -> report the branch, STOP
        search GitHub issues and pull requests
            open pull request -> report it, STOP
            open issue, no fix -> continue, skip phase 8, cite it in the pull request
        if nothing blocks:
            fix it, in worktree B       then build and test against the baseline
            GATE: ask the user          nothing reaches GitHub before the answer
            create the issue
            push the branch, open the pull request
            record the verdict

Phases 1–5 are the detective work: [triage.md](triage.md).
Phases 6–10 are the fix, the tests and the GitHub conventions: [fix-and-ship.md](fix-and-ship.md).

| # | Phase | Where |
| - | ----- | ----- |
| 1 | Read the report, fill its gaps | triage |
| 2 | Worktree A at the reported hash: build, reproduce, prove it is wrong | triage |
| 3 | Worktree B at master: build, baseline the tests, verify the bug there | triage |
| 4 | Search recent topic branches for an existing fix | triage |
| 5 | Search GitHub issues and pull requests | triage |
| 6 | Write the fix in worktree B, build, test against the baseline | fix-and-ship |
| 7 | **GATE — present everything, wait for the user** | fix-and-ship |
| 8 | Create the issue | fix-and-ship |
| 9 | Push the branch, open the pull request | fix-and-ship |
| 10 | Record the verdict | fix-and-ship |

## Hard rules

1. **Never trust the report.** Reproduce the failure yourself before you touch anything else.
2. **No reproduction means stop.** Vary the three factors in phase 2, then report what you tried and
   what you saw instead. Never proceed to master, and never write a fix, on an unverified report.
3. **Prove the behaviour is wrong before you edit code.** You need a citable authority: a standard
   clause, an RFC section, a NED or Doxygen contract, or an `ASSERT` the code makes about itself.
   That citation becomes the issue's *What the standard says* section, so it is not extra work.
4. **Running tells you the trigger fired; only a diff tells you the defect is there.** Before you
   conclude anything from a master run, diff the defective lines between the two worktrees.
5. **Two worktrees, never one that switches branches.** A switch forces a full rebuild each way, and
   you need both builds alive. The user's main checkout is dirty and must stay untouched.
6. **Baseline the tests while worktree B is still pristine.** That is the only honest way to call a
   later failure pre-existing, and it costs one test run at a moment when master is already built.
7. **Stop at the gate.** When the fix is written and tested, stop and wait for the user. That is
   phase 7, and you may not skip it even when the user asked for the whole pipeline up front.
8. **Ask again before each outward-facing command**: `git push`, `gh issue create`, `gh pr create`.
9. **One issue per independent defect.** Two defects that must land together are still two issues;
   one pull request closes both.
10. **`git fetch --prune origin` before every comparison against `origin/*`.** A stale ref turns a
    stop verdict into a wrong one, and without `--prune` a branch deleted upstream still looks alive.

## What the report has to give you

Derive what you can from the repository; ask the user for the rest. Do not guess a reproduction and
then report the bug as not reproducible.

- **What it is** — the observed failure: the exception text, the wrong value, the backtrace, the hang.
- **How to reproduce it** — the directory, the command, the configuration, the build mode, the user
  interface.
- **The git hash** — the commit it was seen on. With none given, use the current `HEAD` of the
  user's checkout, record the SHA, and say which you used.
- **Why it is wrong**, if the reporter knows. If not, phase 2 has to find the authority.

## Projects other than INET

The flow is unchanged for OMNeT++ and derived projects. Read the repository from `git remote -v`,
never from the report. Build commands, test suites and issue conventions differ per project —
establish them from the repository before phase 3, since that is where the baseline is recorded, and
tell the user which suites you treat as green.
