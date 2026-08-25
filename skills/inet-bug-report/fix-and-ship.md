# Fix and ship: phases 5 to 10

## Phase 5 — write the fix

- **Fix the cause, not the symptom.** If the report's *Candidate fix* only suppresses the crash,
  say so and decide deliberately. A defensive guard is legitimate when the caller is allowed to see
  transient state; it is wrong when the state should never have been transient.
- **One commit per independent defect.** If two defects have to land together to change anything
  observable, that is fine — two commits, one pull request, and the pull request explains why
  neither works alone.
- **Keep the diff minimal.** No drive-by refactoring, no reformatting, no renaming. Anything you
  noticed but did not fix belongs in *Not addressed here*, or in its own issue.
- **Match the surrounding code.** Follow the conventions in the [inet](../inet/SKILL.md) skill for
  naming, Doxygen comments and display strings.
- Commit subjects use the repository's own form: `<area>: <verb phrase>`, area lowercase, for
  example `mipv6: use hasActiveBinding() to detect a first home registration`. Never add
  Co-Authored-By or any other attribution trailer.

## Phase 6 — test, and separate regressions from pre-existing failures

Build first, then run the suites that cover the area you touched. Ask the user for the exact scope
if it is not obvious; the usual pair is:

    cd tests/fingerprint && ./fingerprinttest -d -m <area>
    cd tests/module     && inet_run_module_tests -f <Area>

**The rule that matters most:** a failing test is a regression until you have proved otherwise, and
the only proof is reproducing the same failure on pristine master. Build unmodified `origin/master`
in a second worktree, run the same test, and compare. State the result explicitly in the pull
request: "fails identically on unmodified master, therefore pre-existing and out of scope". Never
write that sentence without having run it.

If fingerprints change, justify each change **per ingredient**, tying the moved ingredient to the
code change. Graphical (`tyf`) fingerprints are unreliable and often already stale; when your
re-recording absorbs a stale value, say so. The [inet-branch-cleanup](../inet-branch-cleanup/SKILL.md)
skill has the full fingerprint discipline.

Also produce the **before/after evidence** that the fix works: the measurement, the log excerpt or
the run that used to crash and now does not. This is what the pull request is built around.

## Phase 7 — the gate

Stop here. Post to the user:

1. the diff of the fix;
2. the before/after evidence;
3. the test results, with any pre-existing failure named and its master comparison;
4. the proposed issue title or titles;
5. the proposed pull request title and branch name.

Then ask whether to file the issue and open the pull request, or to stop. Wait for the answer.
Nothing reaches GitHub until it comes. If the user declines, leave the branch local and record that
in the report file.

## Phase 8 — the issue

House style, taken from inet-framework/inet issues #1132 and #1133.

- **Title**: `<area>: <the precise claim>`. Lowercase area prefix. The title states the defect, not
  the symptom: `mipv6: MIPv6_INITIAL_BINDACK_TIMEOUT_FIRST is 1 s, RFC 6275 specifies 1.5 s`.
- **One issue per independent defect.** Cross-reference them, and explain the dependency: "fixing
  this alone changes nothing observable, because #1132 makes the branch that reads it unreachable".
- Spell out every abbreviation on first use and repeat it well past the first use:
  "Binding Update (BU)", "Duplicate Address Detection (DAD)".
- Labels are optional; the maintainers triage. Do not invent labels.

```markdown
## Summary

What is wrong, with `src/inet/.../File.cc:123` and the few lines of code quoted.

## What the standard says

The quoted clause, as a block quote, with its number. Or the NED/Doxygen contract it breaks.

## Why it matters

The consequence for a user, with the measurement that shows it.

## Relationship to #<other>

Only when there is one. Say which fix is load-bearing and which is not.
```

Create it, then note the number:

    gh issue create --title "<title>" --body-file <file>

## Phase 9 — the pull request

Branch name `topic/<initials>/<slug>`, matching the repository's existing branches.

    git push -u origin topic/gy/<slug>
    gh pr create --title "<title>" --body-file <file>

- **Title** states the outcome, not the mechanism:
  `mipv6: complete a first home registration in a single Binding Update`.
- Put `Closes #N` for every issue the pull request fixes near the top.

```markdown
One paragraph: what the pull request achieves, and the constraint a reviewer needs up front
(for example, that two defects had to be fixed together).

Closes #<n>
Closes #<m>

## The problem

The mechanism, with a measured table of the failing behaviour: event, time, value.

## The defect(s)

One subsection per defect, each naming its issue number, what the code did, and what it does now.

## Why both commits are needed

Only for multi-defect fixes. A table showing each partial fix changing nothing.

## Verification

The reproduction that now passes. Fingerprints re-recorded and why. Module tests, with every
pre-existing failure named and shown to fail identically on unmodified master.

## Not addressed here

What you deliberately left, and the issue that records it.
```

## Phase 10 — record

- Report the verdict, the issue number and the pull request number to the user. The verdict is one
  of: `fixed, PR #<n>` / `already fixed by <sha>` / `duplicate of #<n>` / `not reproducible` /
  `not a bug` / `fix ready, not filed`.
- **If the input was a file**, append the verdict to it, in place, together with what you learned
  that the reporter did not know — the real reproduction, the authority you found, the trigger
  condition, the pre-existing test failures. Leave the file where it was.
- Save a memory when the investigation produced knowledge that outlives the fix: a diagnostic that
  proved a branch was dead, a set of pre-existing failures that future agents should not
  re-diagnose, a trigger condition nobody would guess.
