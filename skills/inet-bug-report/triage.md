# Triage: phases 1 to 5

Detective work. Reach one of these verdicts before a single line of source is changed: *not
reproducible*, *not a bug*, *already fixed on master*, *introduced by the reporter's branch*,
*already fixed on a topic branch*, *already being fixed by a pull request*, or *real, unreported,
and mine to fix*.

## Phase 1 — read the report, fill its gaps

Read the whole report before running anything, and separate what the reporter **saw** from what the
reporter **inferred**. A stated cause is a hypothesis; only the observed failure is evidence.

**When the report is thin** — a sentence from the user, or one missing an item SKILL.md lists —
close the gaps in this order, and only then start phase 2:

1. **Locate it in the source.** Grep for the identifier, class, parameter or message text the
   description mentions. Read the code and form a concrete expectation of what should fail.
2. **Find the shortest existing scenario that exercises it.** Search `tests/module`,
   `tests/fingerprint`, `examples/` and `showcases/` for a configuration that already reaches the
   code path. Reproducing inside an existing test is far better than writing a new one, because the
   fix can then be verified by that test.
3. **Fix the commit.** Use the hash the report gives. With none, use the current `HEAD` of the
   user's checkout, record its SHA, and say which you used.
4. **Ask the user only for what neither the code nor the repository can tell you** — which reading
   of "wrong" they mean, which configuration they ran, what they saw on screen. Ask once, in one
   message, listing everything you need.

## Phase 2 — worktree A: build at the reported hash and verify the bug there

    cd /home/user/inet
    git fetch --prune origin
    git worktree add --detach ../inet-bug-<slug>-reported <hash>
    # build there

Build before you change anything, so a build failure is never mistaken for the bug.

### Reproduce

Run the exact command from phase 1. **If it does not fail**, vary these three, one at a time, in
this order — they are what reports most often omit:

- **Build mode.** `ASSERT` is compiled out in release. A defect that aborts cleanly in debug can
  corrupt memory in release, and one guarded by an assertion can be invisible in debug.
- **User interface.** Qtenv animated, Qtenv express and Cmdenv exercise different code. Anything
  reached from `refreshDisplay()`, `pausePoint()` or a visualizer runs only under Qtenv.
- **Configuration, run number and seed.** State which run of how many reproduces it.

Also rebuild from clean once if the failure is a startup or setup crash; a stale partial build
produces crashes that are not bugs in the source.

If it still does not fail, **stop**. Report the hash you used, each factor you varied, and what you
saw instead. Do not go on to master, and do not write a fix. An unverified report is a question for
the reporter, not a defect.

When it does fail, record the reproduction as a command a reader can paste, and keep worktree A
built — phase 3 compares against it.

### Prove the behaviour is wrong

A reproduction shows behaviour. It does not show the behaviour is wrong. Find the authority that
says so, and quote it with its clause number:

- the standard: IEEE 802.x, IETF RFC, 3GPP, IEC or OPEN Alliance;
- the module contract: the NED comment, the Doxygen comment, the parameter documentation;
- an invariant the code states about itself, including an `ASSERT` that a release build drops;
- OMNeT++ API semantics, for example that `refreshDisplay()` must tolerate mid-event state;
- a reference implementation or a published measurement, when nothing normative applies.

Quote the source; do not paraphrase from memory. This citation becomes the *What the standard says*
section of the issue, so finding it now costs nothing later — and it is what stops an agent from
"fixing" a deliberate model abstraction. INET abstracts on purpose in many places: ask what the code
is trying to do, and whether the documentation states the simplification somewhere else.

If no authority exists, present that to the user and stop. An expectation nobody can source is a
question, not a bug.

## Phase 3 — worktree B: master, the baseline, and the same verification

    git worktree add ../inet-bug-<slug>-master -b topic/gy/<slug> origin/master
    # build there

### Baseline the tests first, while B is still pristine

Before you verify anything and long before you fix anything, run the suites that cover the area and
**save the output**. This is the only honest way to call a later failure pre-existing, and here it
costs one test run on a tree that is already built. Reconstructing this baseline after the fix
exists means another build.

    cd tests/fingerprint && ./fingerprinttest -d -m <area>   | tee <scratch>/baseline-fingerprint.txt
    cd tests/module      && inet_run_module_tests -f <Area>  | tee <scratch>/baseline-module.txt

Name in your report every test that already fails here. Those are out of scope, permanently.

### Verify the bug in master

Run the same reproduction. **Before you conclude anything from the result, diff the defective lines
between the two worktrees.** Running tells you only whether the trigger fired; the diff tells you
whether the defect is present. These two facts are independent, and confusing them drops real bugs:

| Defect in master's code | Trigger reachable | Verdict |
| --- | --- | --- |
| yes | yes, and it fails | Real, present. Continue to phase 4 |
| yes | no — the trigger needs code that is not on master | **Real, latent. Continue to phase 4.** Try to build a master-only trigger from what master has; if none exists, say so and name the branch that exposes it |
| no — fixed since the reported hash | — | Find the fixing commit, report it, stop |
| no — never existed on master | — | The reported branch introduced it. Not an upstream bug: hand it back to the branch owner and stop |

To tell the last two apart:

    git log -S '<the exact broken expression>' --oneline <hash>..origin/master -- <path>
    git log -L <start>,<end>:<path>          # line-level history of the broken lines

The latent case is easy to get wrong and worth an example. A crash needs `AlternativesFs::getHistory()`
to index `elements[-1]` **and** a compound queue as the IEEE 802.11 `pendingQueue`. The broken
function is verbatim on master; only the compound queue arrived on a topic branch first. That is a
master bug, and reporting "not present in master" because the run was clean would lose it.

From here on the issue and the pull request cite **master**, not the reporter's branch.

## Phase 4 — is a fix already sitting on a branch?

Development happens on topic branches, and a branch carries no pull request until someone opens
one, so phase 5 cannot see it. INET has hundreds of live topic branches. You cannot check out and
rebuild them, and you do not have to.

**Sweep every branch by text.** The pickaxe over `--all` searches every local and remote branch at
once:

    git fetch --prune origin
    git log --all --oneline -S '<the exact broken expression>' -- <path>
    git log --all --oneline -G '<regex for the broken line>'   -- <path>
    git log --all --oneline --grep '<identifier>'

For each candidate, find where it lives and whether master has it:

    git branch -a --contains <sha>
    git merge-base --is-ancestor <sha> origin/master && echo "already on master" || echo "NOT on master"

**Then scan recent branches by area.** The pickaxe is anchored to text you already know, so it
misses a fix that reworded the line, moved the code, or repaired the *caller*. Ask the complementary
question — which branches are people working in, near this code?

    scripts/scan-branches.sh <path> [<since-date>]      # run inside the checkout; 6-month default

It lists every remote `topic/*` branch and every local branch with commits against `<path>` that
`origin/master` lacks, newest first, with subjects. Start broad and narrow if the list is long. Read
the subjects, then inspect anything plausible:

    git log  origin/master..<branch> -- <path>
    git diff origin/master...<branch> -- <path>       # three dots: changes on the branch only

Ignore `attic/*`; those are abandoned. Pay attention to branches named `fixes`, `minifixes` or
`misc` — small unfiled bugfixes accumulate there and rarely have an issue.

| Found | Do |
| ----- | -- |
| A fix on a live topic branch, not on master | Report the branch and commit, and stop. Ask the user whether to test it, rebase it, or open a pull request for it — do not write a competing fix |
| A branch reworking the same area, no fix in it | Not a stop. Name it at the gate: your fix may conflict, or belong on that branch |
| A partial or abandoned attempt on an old branch | Read it before writing your own. It often records why the obvious fix does not work |
| A commit that *introduced* the defect | Name it in the issue: it shows the age and the intent, and may reveal the change was deliberate |
| A local-only hit | Report it separately — it is invisible to everyone else, and may be the user's own unfinished work on this bug |
| Nothing | Continue |

## Phase 5 — does GitHub already know?

Search open **and** closed issues, and open **and** closed pull requests. A closed issue often holds
the maintainers' reasoning, which changes what you do next.

Search on three axes, because each finds what the others miss: the symptom in the user's words
(`segfault refreshDisplay`); the identifier (class, method, NED parameter, constant); the file path.

    scripts/search-github.sh <term> [<term>...]        # run inside the checkout

A title match is not a duplicate until you have read the body.

| Found | Do |
| ----- | -- |
| Open pull request that fixes it | Report it, link it, stop |
| **Open issue, no fix** | **Continue.** Skip phase 8 and cite that issue from the pull request |
| Closed as "Not a bug" or "Postponed" | Read the reasoning, present it to the user, stop unless they say otherwise |
| Closed as fixed, but it still reproduces | The fix was incomplete. File a new issue that cites the old one |
| Nothing | Continue to phase 6 |
