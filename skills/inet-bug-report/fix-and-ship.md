# Fix and ship: phases 6 to 11

## Writing for a human reviewer

This applies to every commit message, the issue and the pull request text. A maintainer reads
them between other work. Each sentence must give that reader a fact they need: what is wrong,
why, how to see it, what changed, what was checked. Delete any sentence whose removal loses nothing.

Cut these on sight:

- **Narration of your work**: "I investigated", "after careful analysis", "this PR aims to",
  "let's". State the finding, not the journey. A dead end stays only when it explains why the
  obvious fix does not work.
- **Restating the diff**: "adds a check for X" over a diff that adds a check for X. Give the reason
  instead.
- **Filler and inflated words**: comprehensive, robust, seamless, critical, crucial, ensures,
  enhances, leverages, significantly, properly, correctly handles, "it is important to note".
- **Unearned absolutes and reflexive hedges**: "never", "always", "guarantees" without a rule, the
  arithmetic or a run behind it; "may potentially", "should help to".
- **Decoration**: emoji, bold in every paragraph, a heading over one sentence, a one-item list, a
  table for two facts, a closing summary that repeats the opening.
- **Empty template sections**: drop *Relationship to*, *Why both commits are needed* or
  *Not addressed here* when there is nothing to say. Never write "N/A".
- **Process residue**: audit rounds, subagent names, "generated with", checkbox test plans. These
  go to the gate, not to GitHub.

Prefer short sentences, a file and line over a description of where the code is, and one real
number over an adjective. Spell out every abbreviation on first use. Before the audit, read each
text once as the maintainer would and cut what that reader would skim past.

## Phase 6 — write the fix in worktree B, build, test, commit, draft the pull request text

Worktree B is already at `origin/master`, on branch `topic/<initials>/<slug>`, built, and its test
baseline is recorded. Work there. The pull request targets master, so the fix is cut from master,
never from the reported hash.

### Writing it

- **Fix the cause, not the symptom.** If the report's candidate fix only suppresses the crash, say
  so and decide deliberately. A defensive guard is right when the caller is allowed to see transient
  state; it is wrong when the state should never have been transient.
- **One commit per independent defect.** If two defects must land together to change anything
  observable, that is fine — two commits, one pull request, and the pull request explains why
  neither works alone.
- **Keep the diff minimal.** No drive-by refactoring, reformatting or renaming. Anything you noticed
  but did not fix belongs in *Not addressed here*, or in its own issue.
- **Match the surrounding code.** Follow the [inet](../inet/SKILL.md) skill for naming, Doxygen
  comments and display strings.
- Commit messages follow `doc/project/rule/classification.md` and `doc/project/rule/pull-request.md`:
  - subject `[<scope>: ]<kind>: <what the commit does>`, and for a fix the kind is `fix:`, for
    example `mipv6: fix: use hasActiveBinding() to detect a first home registration`
    (`CR-TAG-SUBJECT`, `PR-MSG-SUBJECT`: aim for 72 characters, fail above 80);
  - a body that gives the reason and says how to reproduce the defect (`PR-MSG-WHY`,
    `PR-MSG-REPRODUCE`) — the phase-2 reproduction command is exactly that;
  - a `Change:` trailer as the last line, for example
    `Change: src.<position> | behavior.change.fix | fingerprint` — name the baselines that move,
    `-` for none, never a guess (`CR-TAG-TRAILER`, `CR-TAG-FORM`, `CR-OBL-BASELINE`).

  The `Change:` line is a classification, not attribution. Never add Co-Authored-By or any other
  attribution trailer (`PR-MSG-FACTS`).

### Testing it

Rebuild, then rerun exactly the suites you baselined in phase 3 and **diff against the saved
output**:

    cd tests/fingerprint && ./fingerprinttest -d -m <area>   | tee <scratch>/after-fingerprint.txt
    cd tests/module      && inet_run_module_tests -f <Area>  | tee <scratch>/after-module.txt
    diff <scratch>/baseline-fingerprint.txt <scratch>/after-fingerprint.txt
    diff <scratch>/baseline-module.txt      <scratch>/after-module.txt

Every difference is caused by your change until you show otherwise; every failure present in the
baseline is pre-existing and out of scope. That is what the baseline buys you: the pull request
sentence *"fails identically on unmodified master, so it is pre-existing and out of scope"* is now
backed by a diff, and you never have to rebuild master to write it.

If fingerprints move, justify each change **per ingredient**, tying the moved ingredient to the code
change. Graphical (`tyf`) fingerprints are unreliable and often already stale; when a re-recording
absorbs a stale value, say so. The [inet-branch-cleanup](../inet-branch-cleanup/SKILL.md) skill has
the full fingerprint discipline.

Also produce the **before/after evidence** that the fix works: the run that used to crash and now
does not, the measurement that changed, the log excerpt. Worktree A still holds the failing build if
you need the "before" again. This evidence is what the pull request is built around.

### Committing it

Commit on the topic branch — one commit per independent defect — and write the pull request text,
the body phase 10 will post, to a local file now: `<scratch>/pull-request.md`. Nothing is pushed
here and no pull request is opened; the commits and that file are what the audit reads.

Run the two mechanical gates yourself before the audit, so the audit does not spend a round on what
a script finds:

    doc/project/enforcement/check-commits.sh        origin/master..HEAD
    doc/project/enforcement/check-classification.sh origin/master..HEAD

## Phase 7 — the audit, repeated until it passes

A fresh subagent, opus, started with none of your context. That is the whole point: it reads the
commits and the pull request text the way a maintainer will — cold, without your reasoning about
why the fix is right to anchor it.

**Its scope is the commits and the pull request text, not whether the code is correct.** Phases 2,
3 and 6 established correctness against an authority and against the test baseline; an agent that
never saw the bug cannot improve on that, and asking it to try produces noise.

The procedure is the **pull request audit** of `doc/project/audit/README.md`, carried out by
`doc/project/guide/review-a-pull-request.md`. Give the subagent these, and nothing else — the
documents live in worktree B, so pass absolute paths:

- the commit series, messages and diffs: `git log --reverse -p origin/master..HEAD`, with
  `origin/master` as the merge base (no pull request number exists yet, so skip the guide's step 1
  fetch);
- the pull request text file;
- the procedure, `guide/review-a-pull-request.md`: steps 2 to 5 and 8;
- the rules it judges against: `rule/pull-request.md` — every `PR-*` rule and its *Quick reference*
  table — and `rule/classification.md`, every `CR-*` rule;
- for `PR-REQ-STORY`, steps 6 and 8 of `guide/contribute-a-change.md`;
- the *Writing for a human reviewer* section at the top of this file, copied in, reported as its
  own row `STYLE` with each sentence to cut or rewrite quoted;
- for `PR-REQ-ARCH` only, the two ledgers `audit/architecture-exceptions.md` and
  `audit/naming-exceptions.md` — and `rule/sealing.md` with `audit/seal-list.md` when the fix
  touches a sealed path.

The guide's steps 6 and 7 — per-commit and integrated code correctness through
`guide/review-a-code-change.md` and the `enforcement/checklist/` files — are *not* part of this
audit. They are the scope you just excluded. Tell the subagent to mark them `not verified — covered
by the bug report pipeline`, not to skip them silently.

Ask for the report in the guide's step-8 form: one row per rule, `PASS`, `FLAG`, `PARTIAL` or
`not verified`, with evidence, the `CR-*` rows beside the `PR-*` rows they mirror; then one numbered
finding per problem, with the commit or the place in the pull request text, the rule, and the repair.
Keep it at `audit/pull-request/<slug>.md` in worktree B — that folder is ignored by git, so it never
enters a commit.

Then act on it, before the gate, never after:

- **Fix every `FLAG`.** A commit-division finding is fixed by rebasing the series, not by adding a
  correction commit on top (`PR-SERIES-ORDER`).
- **Settle every `PARTIAL`**, and decide every question the report raises. The ones you reject go
  to the gate with your reason. Silently dropping one is how a real finding disappears.
- **Turn `not verified` into evidence where you can.** For a series of one or two commits, build and
  test each commit, so `PR-SERIES-BUILDS` can pass rather than stay open.
- **If the commits changed, rebuild, rerun the suites and re-diff against the phase-3 baseline.** A
  rebase that splits or reorders commits invalidates the phase-6 test run, and `PR-SERIES-BUILDS`
  asks for every commit in the series to be green, not just the tip. Rerun the two mechanical gates.

### Audit again, until it passes

After acting on a report, start a **new** fresh subagent on the corrected commits and pull request
text. Do not resume the previous one: it has seen your first version, and it would judge the diff
between versions instead of the result. Repeat until every row is `PASS`, or `not verified` for the
excluded correctness steps only, and no finding is open.

Stop the loop and take it to the gate instead when a round repeats a finding you already rejected
with a reason, when two rounds contradict each other, or after three rounds that still leave
findings. Those are decisions for the user, not for another round.

## Phase 8 — the gate

Stop here. Post to the user:

1. the diff of the fix;
2. the before/after evidence;
3. the test diff against the baseline, with every pre-existing failure named;
4. the final audit report and the number of rounds: what you fixed, every finding you rejected with
   the reason, and why the loop stopped if it ended before a clean pass;
5. the proposed issue title or titles — or the existing issue number you will cite instead;
6. the proposed pull request title and branch name.

Then ask whether to file the issue and open the pull request, or to stop. Wait for the answer.
Nothing reaches GitHub until it comes. If the user declines, leave the branch local and say so.

## Phase 9 — the issue

**Skip this phase if phase 5 found an open issue with no fix.** Cite that number in the pull request
instead of filing a duplicate.

House style, taken from inet-framework/inet issues #1132 and #1133. Write it as
[Writing for a human reviewer](#writing-for-a-human-reviewer) says.

- **Title**: `<area>: <the precise claim>`, area lowercase. It states the defect, not the symptom:
  `mipv6: MIPv6_INITIAL_BINDACK_TIMEOUT_FIRST is 1 s, RFC 6275 specifies 1.5 s`.
- **One issue per independent defect.** Cross-reference them and explain the dependency: "fixing
  this alone changes nothing observable, because #1132 makes the branch that reads it unreachable".
- Spell out every abbreviation on first use and keep repeating it well past the first use:
  "Binding Update (BU)", "Duplicate Address Detection (DAD)".
- Labels are optional; the maintainers triage. Do not invent labels.

```markdown
## Summary

What is wrong, with `src/inet/.../File.cc:123` and the few lines of code quoted.

## What the standard says

The authority from phase 2, quoted as a block quote with its clause number. Or the NED/Doxygen
contract it breaks.

## Why it matters

The consequence for a user, with the measurement that shows it.

## Relationship to #<other>

Only when there is one. Say which fix is load-bearing and which is not.
```

    gh issue create --title "<title>" --body-file <file>

If the bug is latent on master — the defect is there but the trigger arrived on a topic branch —
say so plainly in *Why it matters*, and name the branch and the configuration that expose it.

## Phase 10 — the pull request

Branch name `topic/<initials>/<slug>`, matching the repository's existing branches.

    git fetch --prune origin      # master may have moved while you worked
    git push -u origin topic/gy/<slug>
    gh pr create --title "<title>" --body-file <scratch>/pull-request.md

- **Title** states the outcome, not the mechanism:
  `mipv6: complete a first home registration in a single Binding Update`.
- Put `Closes #N` for every issue it fixes near the top — including an issue you did not file.

The body is the file you wrote in phase 6 and audited in phase 7, corrected for what the audit
found. Its shape — drop any section with nothing to say:

```markdown
One paragraph: what the pull request achieves, and the constraint a reviewer needs up front
(for example, that two defects had to be fixed together).

Closes #<n>

## The problem

The mechanism, with a measured table of the failing behaviour: event, time, value.

## The defect(s)

One subsection per defect, each naming its issue number, what the code did, and what it does now.

## Why both commits are needed

Only for multi-defect fixes. A table showing each partial fix changing nothing.

## Architectural surface

The contracts, packet content, configuration surface and feature descriptors the fix touches, or
"none" (PR-REQ-ARCH). Any new `AV-*` or `NV-*` ledger row, and the permission for a sealed path.

## Verification

The reproduction that now passes. Every test command run, exactly as typed, with its resulting
status (PR-REQ-STORY). Fingerprints re-recorded and why. Test results diffed against the master
baseline, with every pre-existing failure named.

## Not addressed here

What you deliberately left, and the issue that records it.
```

## Phase 11 — record

- Report the verdict, the issue number and the pull request number to the user. The verdict is one
  of: `fixed, PR #<n>` / `already fixed by <sha>` / `already fixed on branch <b>` /
  `duplicate of #<n>` / `not reproducible` / `not a bug` / `introduced by the reporter's branch` /
  `fix ready, not filed`.
- **If the report was a file**, append the verdict to it in place, with what you learned that the
  reporter did not know: the real reproduction, the authority, the trigger conditions, the
  pre-existing test failures. Leave the file where it was.
- Remove the worktrees once the user is done with them: `git worktree remove <path>`. Ask first —
  they are expensive to rebuild.
- Save a memory when the investigation produced knowledge that outlives the fix: a diagnostic that
  proved a branch was dead, pre-existing failures future agents should not re-diagnose, a trigger
  condition nobody would guess.
