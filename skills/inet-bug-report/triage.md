# Triage: phases 0 to 4

Detective work. The aim is to reach one of five verdicts before a single line of source is changed:
*not reproducible*, *not a bug*, *already fixed on master*, *already being fixed by a pull request*,
or *real, unreported, and mine to fix*.

## Phase 0 — read the input, fill its gaps, set up the worktree

Read the whole report before running anything, and separate what the reporter **saw** from what the
reporter **inferred**. A stated cause is a hypothesis; only the observed failure is evidence.

**When the input is thin** — a sentence from the user, or a report missing the four items SKILL.md
lists — close the gaps in this order, and only then start phase 1:

1. **Locate it in the source.** Grep for the identifier, class, parameter or message text the
   description mentions. Read the code and form a concrete expectation of what should fail.
2. **Find the shortest existing scenario that exercises it.** Search `tests/module`,
   `tests/fingerprint`, `examples/` and `showcases/` for a configuration that already reaches the
   code path. Reproducing inside an existing test is far better than writing a new one, because the
   fix can then be verified by that test.
3. **Fix the commit.** Use the commit the report names. With no commit named, use the current
   `HEAD` of the user's checkout, record its SHA, and say which you used.
4. **Ask the user only for what neither the code nor the repository can tell you** — which of two
   readings of "wrong" they mean, which configuration they ran, what they saw on screen. Ask once,
   in one message, listing everything you need.

**The worktree.** The user's main checkout is dirty and must stay untouched.

    cd /home/user/inet
    git fetch --prune origin          # always --prune, see phase 3
    git worktree add ../inet-bug-<slug> -b topic/gy/<slug> origin/master

Note the exact commit you branched from. Build there before you start changing anything, so that a
build failure is never mistaken for the bug.

## Phase 1 — reproduce

Reproduce on **the commit fixed in phase 0**, not on master. Master may have moved, and phase 3 is
where that gets tested. If that commit is not in the repository, say so and reproduce on the closest
ancestor you can find.

Run the exact command line from phase 0. If it does not fail, vary one factor at a time in this
order, because these are what agents most often omit from a report:

- **Build mode.** `ASSERT` is compiled out in release. A defect that aborts cleanly in debug can
  corrupt memory in release, and one guarded by an assertion can be invisible in debug.
- **User interface.** Qtenv animated, Qtenv express and Cmdenv exercise different code. Anything
  reached from `refreshDisplay()`, `pausePoint()` or a visualizer only runs under Qtenv.
- **Configuration, run number and seed.** State which run of how many reproduces it.
- **Clean build.** A stale partial build produces crashes that are not bugs in the source. If the
  failure is a startup or setup crash, rebuild from clean before you believe it.

Record the reproduction as a command a reader can paste. If after all of this it does not fail,
**stop**. Report what you tried and what you saw instead. Do not write a fix.

## Phase 2 — prove the behaviour is wrong

A reproduction shows behaviour. It does not show that the behaviour is wrong. Find the authority
that says so, and quote it with its clause number:

- the standard: IEEE 802.x, IETF RFC, 3GPP, IEC or OPEN Alliance;
- the module contract: the NED comment, the Doxygen comment, the parameter documentation;
- an invariant the code states about itself, including an `ASSERT` that a release build drops;
- OMNeT++ API semantics, for example that `refreshDisplay()` must tolerate mid-event state;
- a reference implementation or a published measurement, when nothing normative applies.

Quote the source. Do not paraphrase from memory. If the report wrote `NO AUTHORITY FOUND` and you
cannot find one either, present that to the user and stop — an expectation nobody can source is a
question, not a bug.

Then check the opposite reading. Ask what the code is trying to do and whether the "bug" is a
deliberate simplification the model documents elsewhere. Many INET models abstract deliberately.

## Phase 3 — is it still on master, and is a fix already sitting somewhere?

Two questions. The first is answered by running the code, the second only by searching history.
Both read `origin/*` refs, so **fetch immediately before this phase**, even if phase 0 already
fetched. This phase produces stop verdicts, and a stop verdict computed from stale refs is wrong in
the expensive direction: you tell the user "still broken on master" about a commit that was fixed
this morning, or "a fix exists on branch X" about a branch that was deleted after being merged.

Always `--prune`. Without it a deleted remote branch keeps its remote-tracking ref forever, and
`for-each-ref` reports it as live — which is exactly how the branch scan below invents a fix that no
longer exists anywhere.

    git fetch --prune origin
    git -C <worktree> log --oneline origin/master -5
    # rebuild and rerun the reproduction on origin/master

If it no longer reproduces, find the commit that fixed it before you claim it is fixed:

    git log -S '<the exact broken expression>' --oneline -- <path>
    git log -L <start>,<end>:<path>          # line-level history of the broken lines
    git log --oneline <reported-commit>..origin/master -- <path>

Report the fixing commit and stop. If it still reproduces on master, keep the master reproduction —
the issue must cite master, not the reporter's branch.

Watch for the reverse case: the report came from a topic branch and the defect exists **only**
there. Then it is not an upstream bug. Say so and hand it back.

### Then sweep every branch, not just master

Development happens on topic branches, and a branch carries no pull request until someone opens
one, so phase 4 cannot see it. INET has hundreds of live topic branches. You cannot check out and
rebuild them, and you do not have to: the pickaxe over `--all` searches every local and remote
branch at once.

    git fetch --prune origin
    git log --all --oneline -S '<the exact broken expression>' -- <path>
    git log --all --oneline -G '<regex for the broken line>'   -- <path>
    git log --all --oneline --grep '<identifier>'
    git log --all --oneline -- <path> | head -20    # who is touching this file at all

For every candidate commit, find where it lives and whether master has it:

    git branch -a --contains <sha>
    git merge-base --is-ancestor <sha> origin/master && echo "already on master" || echo "NOT on master"

Ignore hits on `attic/*` branches; those are abandoned. Treat a hit on a live `topic/*` branch as a
real finding.

### Then scan recent branches by area

The pickaxe is anchored to text you already know. It misses a fix that reworded the line, moved the
code, or repaired the *caller* instead. So also ask the complementary question — **which branches
are people currently working in, near this code?**

    scripts/scan-branches.sh <path> [<since-date>]      # default window: 6 months

It lists every remote `topic/*` branch and every local branch that has commits against `<path>`
which `origin/master` does not, newest first, with the commit subjects. Start `<path>` broad (the
subsystem directory) and narrow it if the list is long. The scan is cheap — tens of branches per
second — so run it before concluding that nobody has touched this.

Read the subjects, then inspect anything plausible:

    git log origin/master..<branch> -- <path>
    git diff origin/master...<branch> -- <path>       # three dots: changes on the branch only

Pay particular attention to branches named `fixes`, `minifixes`, `misc` or similar. They are where
small unfiled bugfixes accumulate, and they rarely have an issue or a pull request.

Local-only hits deserve a separate line in your report: they are invisible to everyone else, and
they may be the user's own unfinished work on this very bug.

| Found | Do |
| ----- | -- |
| A fix on a live topic branch, not on master | Report the branch and commit, and stop. Ask the user whether to test it, rebase it, or open a pull request for it — do not write a competing fix |
| A branch reworking the same area, no fix in it | Not a stop. Name it at the gate: your fix may conflict, or belong on that branch instead |
| A partial or abandoned attempt on an old branch | Read it before writing your own. It often records why the obvious fix does not work |
| A commit that *introduced* the defect | Name it in the issue. It tells the reviewer the age and the intent, and may reveal that the change was deliberate |
| Nothing outside master | Continue |

## Phase 4 — does GitHub already know?

Search open **and** closed issues, and open **and** closed pull requests. A closed issue often holds
the maintainers' reasoning, which changes what you should do next.

Search on three axes, because each finds what the others miss:

- the symptom, in the user's words: `segfault refreshDisplay`;
- the identifier: the class, the method, the NED parameter, the constant;
- the file path.

`scripts/search-github.sh <term> [<term>...]` runs all of these against the repository the current
directory belongs to. Read the hits; a title match is not a duplicate until you have read the body.

Decide from what you find:

| Found | Do |
| ----- | -- |
| Open pull request that fixes it | Report it, link it, stop |
| Open issue, no fix | Skip phase 8. Write the fix and reference the existing issue from the pull request |
| Closed as "Not a bug" or "Postponed" | Read the reasoning, present it to the user, stop unless they say otherwise |
| Closed as fixed, but it still reproduces | The fix was incomplete. File a new issue that cites the old one |
| Nothing | Continue to phase 5 |

Also search the commit log, since not everything reaches an issue:

    git log --oneline --grep '<identifier>' origin/master | head
