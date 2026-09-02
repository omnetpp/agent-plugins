# Fix and ship: phases 6 to 11

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
- Commit subjects use the repository's own form: `<area>: <verb phrase>`, area lowercase, for
  example `mipv6: use hasActiveBinding() to detect a first home registration`. Never add
  Co-Authored-By or any other attribution trailer.

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

## Phase 7 — the audit

A fresh subagent, opus, started with none of your context. That is the whole point: it reads the
commits and the pull request text the way a maintainer will — cold, without your reasoning about
why the fix is right to anchor it.

**Its scope is the commits and the pull request text, not whether the code is correct.** Phases 2,
3 and 6 established correctness against an authority and against the test baseline; an agent that
never saw the bug cannot improve on that, and asking it to try produces noise.

Give it these, and nothing else — the rule documents live in worktree B, so pass absolute paths:

- the commit series, messages and diffs: `git log --reverse -p origin/master..HEAD`;
- the pull request text file;
- the rules it judges against: `doc/architecture/pull-requests.md` — every `PR-SPLIT-*`,
  `PR-SERIES-*`, `PR-MSG-*` and `PR-REQ-*` rule, plus its *Quick reference* table;
- for `PR-REQ-STORY`, the *Contributor workflow* in
  `doc/architecture/architectural-requirements.md`, steps 6 and 8;
- for `PR-REQ-ARCH` only, the two ledgers `doc/architecture/architecture-exceptions.md` and
  `doc/architecture/naming-exceptions.md` — and `doc/architecture/sealing.md` when the fix touches
  a sealed path.

`doc/architecture/enforcement/agent-review-checklist.md` is *not* part of this audit. It judges a
code diff against the architectural requirements, which is the scope you just excluded.

Ask for the verdict in the form that checklist already uses — one line per finding, each carrying
the rule it comes from:

    PASS
    FLAG     — <commit or pull request text>:<where> — <rule id> — <one-line reason>
    QUESTION — <commit or pull request text>:<where> — <rule id> — <what to check>

Then act on it, before the gate, never after:

- **Fix every `FLAG`.** A commit-division finding is fixed by rebasing the series, not by adding a
  correction commit on top (`PR-SERIES-ORDER`).
- **Decide every `QUESTION`.** The ones you reject go to the gate with your reason. Silently
  dropping one is how a real finding disappears.
- **If the commits changed, rebuild, rerun the suites and re-diff against the phase-3 baseline.** A
  rebase that splits or reorders commits invalidates the phase-6 test run, and `PR-SERIES-BUILDS`
  asks for every commit in the series to be green, not just the tip.

## Phase 8 — the gate

Stop here. Post to the user:

1. the diff of the fix;
2. the before/after evidence;
3. the test diff against the baseline, with every pre-existing failure named;
4. the audit report: what you fixed from it, and every `QUESTION` you rejected, with the reason;
5. the proposed issue title or titles — or the existing issue number you will cite instead;
6. the proposed pull request title and branch name.

Then ask whether to file the issue and open the pull request, or to stop. Wait for the answer.
Nothing reaches GitHub until it comes. If the user declines, leave the branch local and say so.

## Phase 9 — the issue

**Skip this phase if phase 5 found an open issue with no fix.** Cite that number in the pull request
instead of filing a duplicate.

House style, taken from inet-framework/inet issues #1132 and #1133.

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
found. Its shape:

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

## Verification

The reproduction that now passes. Fingerprints re-recorded and why. Test results diffed against the
master baseline, with every pre-existing failure named.

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
