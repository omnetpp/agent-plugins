---
name: inet-bug-report
description: >
  Take a bug report for INET, OMNeT++ or a derived simulation project — a Markdown file or a plain
  description — and act on it end to end: reproduce the bug, prove the behaviour is actually wrong,
  check whether current master already fixes it, search GitHub for an existing issue or pull
  request, write and test a fix, then stop for the user's confirmation before filing the issue and
  opening the pull request. Use when handed a bug report, a bug .md file, or a description of a
  defect, and asked to verify, triage, investigate, fix, file, or "run the whole pipeline on" it.
---

# INET bug report: verify, triage, fix, file

The input is a bug report written by someone else — an agent that hit the defect during other work,
or the user in a sentence. It may be wrong, stale, or thin. Your job is the pipeline below, and
four of its phases can legitimately end it without a fix.

## Hard rules

1. **Never trust the report.** Reproduce the failure yourself before you touch anything else.
2. **No reproduction means stop.** Report what you tried and what you saw instead. Never write a fix
   for a defect you have not seen fail.
3. **Wrong behaviour must be proved wrong**, against a standard, an RFC, a NED or Doxygen contract,
   or a stated invariant. "This looks odd" is not a bug.
4. **Stop at the gate.** When the fix is written and tested, stop and wait for the user to confirm
   before you file anything. That is phase 7. You may not skip it, even when the user asked for the
   whole pipeline up front.
5. **Ask again before each outward-facing command.** Show the exact text and the exact branch name
   for `git push`, `gh issue create` and `gh pr create`.
6. **One issue per independent defect.** Two defects that must land together are still two issues;
   one pull request closes both.
7. **Prove a failing test is pre-existing** by reproducing it on pristine master. Never call a
   failure unrelated without that comparison.
8. **Work in a dedicated git worktree** off `origin/master`. The user's main checkout is dirty and
   must stay untouched.

## The pipeline

Report the verdict of each phase as you finish it.

| # | Phase | Ends the pipeline when |
| - | ----- | ---------------------- |
| 0 | Read the input, fill its gaps, set up the worktree | — |
| 1 | Reproduce the bug | it does not reproduce → report and stop |
| 2 | Prove the behaviour is wrong | the behaviour is correct → report "not a bug" and stop |
| 3 | Check `origin/master`; sweep all branches by text; scan recent branches by area | already fixed on master → report the commit and stop; fixed on a topic branch → report the branch and stop |
| 4 | Search GitHub for an existing issue or pull request | an open pull request fixes it → report it and stop |
| 5 | Write the fix | — |
| 6 | Test it; separate regressions from pre-existing failures | — |
| **7** | **GATE — present everything, wait for the user** | **the user says no → stop, branch stays local** |
| 8 | Create the issue | — |
| 9 | Push the branch, open the pull request | — |
| 10 | Record the verdict | — |

Phases 0–4 are detective work: [triage.md](triage.md).
Phases 5–10 are the fix, the test discipline and the GitHub conventions:
[fix-and-ship.md](fix-and-ship.md).

An existing *issue* with no fix does not end the pipeline: skip phase 8 and cite that issue from the
pull request instead.

## What the input has to yield

Before phase 1 you need all of these. Derive what you can from the repository; ask the user for the
rest. Do not guess a reproduction and then report that the bug is not reproducible.

- **Repository and commit** — from `git remote -v` and the report. Never take the repository from
  the report alone.
- **The exact command line**, with directory, configuration name, build mode and user interface.
- **The observed failure** — the exception text, the wrong value, the backtrace, the hang.
- **The expected behaviour and its authority** — the clause, the RFC section, the NED comment. If
  the report has none, phase 2 has to find one.

A one-sentence description from the user is a valid input. Turn it into the four items above, then
proceed; see phase 0 in [triage.md](triage.md).

## Phase 7 in full

Post to the user: the diff of the fix, the before/after evidence that it works, the test results
with every pre-existing failure named, the proposed issue title or titles, and the proposed pull
request title and branch name. Then ask whether to file the issue and open the pull request, or to
stop. Wait for the answer. Nothing reaches GitHub until it comes.

## Projects other than INET

The pipeline is unchanged for OMNeT++ and derived projects. Read the repository from
`git remote -v`. Build commands, test suites and issue conventions differ per project — establish
them from the repository before phase 6, and tell the user which suites you treat as green.
