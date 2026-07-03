---
name: inet-branch-cleanup
description: >
  Clean up / reorganize an INET (OMNeT++) topic branch into a reviewable, "green at every
  commit" history: reorder/fold/squash commits while keeping the relevant test suites passing at
  every commit, and justify every fingerprint change per-ingredient. Use when asked to tidy,
  clean up, reorganize, rebase, or prepare-for-review/PR an INET branch; to make every commit
  pass tests; or to walk a branch commit-by-commit fixing breakages and fingerprint drift.
---

# INET branch cleanup

Turn a messy INET topic branch (developed exploratorily, with broken intermediate commits and
under-documented fingerprint drift) into a clean linear history where **every commit passes the
relevant test suites**, **every fingerprint change is explained per-ingredient**, and **each
logical change lands once, in final form** (minimal churn/zigzags). This is the CLI-based
INET playbook; for the opp_repl-driven variant (dependency-scoped tests, coverage ledger)
see omnetpp-branch-cleanup.

## Confirm with the user before starting

These change the whole approach — ask, don't assume:

1. **End goal** — upstream PR / internal merge / split into PRs / just tidy (no merge yet).
2. **Test scope** — which suites and filters define "green". Get the *exact* commands, e.g.
   `cd tests/fingerprint && ./fingerprinttest -d -m <area>` and
   `cd tests/module && inet_run_module_tests -f <Area>`. Confirm which other suites to ignore.
3. **Granularity** — keep ~1:1 commits / squash into thematic units / hybrid (squash noise &
   fix-ups, keep substantive standalone changes).
4. **Fix / churn handling** — when later commits patch, adjust, or extend code an earlier commit
   introduced (a "zigzag", see *Minimize zigzags* below), the default is to **fold them into the
   introducing commit** so it's right the first time. Keep a fix as its own commit only when it has
   *standalone value* (a real bug worth showing or cherry-picking) — then reorder it
   green-before-breakage instead of folding. Confirm: fold-by-default vs. preferring visible fixes.
5. **`tyf` policy** — graphical fingerprints are unreliable (`fingerprinttest` itself suggests
   `-F tyf`). Usually exclude them and enforce only behavioral ingredients.
6. Warn that **leftover bugs with no fix on the branch may need new bugfix commits**, and that
   **the branch tip itself may not be green** — verify, don't assume.

## The contract (per commit, walked master → HEAD)

1. `src` builds. 2. Fingerprint suite ends `OK` — zero errors, zero failures unless the commit
legitimately changes fingerprints. 3. Module suite passes. 4. Any commit that changes recorded
fingerprints **explains per-ingredient WHY** in its message (tie the moved ingredient to the
code change). 5. Feature-introducing commits produce zero failures/errors.

## Minimize zigzags (each change lands once)

A third objective, alongside greenness and fingerprint justification: the cleaned history's
per-commit diffs should **partition** the net `master..HEAD` diff. Every line of the final state is
authored by exactly one commit; no commit introduces code that a later branch commit rewrites or
deletes. A **zigzag** (churn) is a violation — code added in A, then patched/adjusted/extended by
later commits B, C, D. A reviewer reading A sees code already obsolete at HEAD.

**Fold rule.** When B…D exist *only because A wasn't right or complete yet* — they bugfix it, tweak
it, or bolt a minor bit onto it — fold them back into A so A is correct the first time. This is
strictly better than reordering: folding removes the churn **and** the broken/incomplete
intermediate state in one move, so green-at-every-commit comes for free (no fix to slot ahead of a
breakage). Zigzag-minimization and the green contract are mostly the *same* operation; they diverge
only at the exceptions below.

**Keep separate (principled exceptions):**
- **Dependency** — B depends on commits *between* A and B; it can't move back without dragging them.
  Leave it, or fold the whole cluster if it's one unit.
- **Standalone value** — B fixes a *real* bug worth showing on its own (pre-existing, cherry-pickable,
  or a breakage worth documenting). Reorder it green-before-breakage but keep it as its own commit.
- **Coherent feature** — B tells its own story and merely happens to touch A's code; that's legitimate
  layering, not churn. Test: *does B stand alone, or is it just "oops, A also needed this"?* — only
  the latter folds. Don't fold a coherent feature just to shrink the commit count; gate "minor
  feature" folds on the granularity choice (§3) — fold only additions too small to review standalone.

## Procedure

**Phase 0 — Safety + baselines.** Tag the original tip (`git tag <branch>-orig`). Work on a copy
branch. Move untracked scratch files out of the repo. Establish the **master baseline** AND the
**HEAD baseline** (build + both suites at each) — note exactly which sims/tests run and the pass
state. The tip is often *not* green; that's expected.

**Phase 1 — Map the branch.** List commits (`git rev-list --reverse master..HEAD`). Identify:
(a) thematic groups; (b) **fingerprint change points** = commits touching `tests/fingerprint/*.csv`;
(c) **fix→breakage pairs** from commit messages ("fix ...", "tests exposing ...", "infinite
loop"); (c′) **churn chains (zigzags)** = the same file/function/hunk re-touched across commits
(scan `git log -p`, per-hunk blame) where the later touch only fixes or finishes the earlier one —
these fold into their origin (same *file* alone isn't a chain; it must be the same *logical unit*
re-edited to correct it); (d) stray/non-scope commits (raise with the user, default keep). Note
which `.csv` files are "invariants" (a header may say *"must NOT change"*) vs ones that legitimately drift.

**Phase 2 — Construct the corrected history.** Drive a scripted rebase (interactive `-i` is often
unavailable in the harness, so use `GIT_SEQUENCE_EDITOR=<script> GIT_EDITOR=true git rebase -i
master`): **`fixup`/`squash` each churn chain back into the commit that introduced its code** so
the code appears once, in final form (this often dissolves a fix→breakage pair outright — the
breakage never exists — so prefer it over reordering unless the fix has standalone value); reorder
the fix→breakage pairs you *do* keep; `fixup` standalone "update fingerprints" commits into their
code commit; `edit`-stop where you must fold a new fix or re-record fingerprints. At each
re-record/edit stop: **purge stale `*.UPDATED`**, build, run the suite, accept the new csv, and
write the per-ingredient justification into the commit message. Expect **forward-ripple
conflicts**: an early fingerprint re-record makes later fingerprint commits' csv diffs conflict —
resolve each by re-recording at that commit.

**Phase 3 — Verify (efficiently).** A full per-commit walk is usually overkill. Instead:
- **Bracket each fingerprint change point**: test the changing commit *and its parent* (parent
  green with old csv, change point green with new csv) → the change is correctly localized.
- **Module tests at key commits**: the reordered fix→test pairs, hang-risk commits (lifecycle /
  restart / loop fixes), and the tip. The unchanged commits between change points inherit and
  stay green.
- Run the suite **twice** at any commit where determinism is in doubt.

**Phase 4 — Reword.** Rewrite every subject to `Area: category: description`
(`fix`/`refactor`/`feature`/`test`; omit category when the verb makes it obvious — "Implement…",
"Add … test"). Message-only, bodies preserved: `git filter-branch --msg-filter`. Verify trees are
identical before/after (`git diff <pre> <post>` empty).

**Phase 5 — Finalize.** Per the user: replace the original branch (`git branch -f`) keeping the
`-orig` tag, or keep both. Remove temp tags/scratch.

## Fingerprint discipline

- Ingredient semantics and the cause→ingredient map for writing per-commit justifications live
  in omnetpp-fingerprint-testing (`ingredients.md`, `interpreting-drift.md`); INET runner flags
  and gotchas in inet-fingerprint-testing. The rule that matters here: a change point's
  justification ties **each moved ingredient to a cause** — if you can't explain an ingredient
  move, it's a red flag: investigate, don't just re-record.

## Pitfalls / hard-won lessons

- **Stale `*.UPDATED` lies.** `fingerprinttest` leaves `*.UPDATED/*.ERROR/*.FAILED` behind;
  reading a stale one (from a run at another commit) makes a deterministic sim look
  non-deterministic and sends you chasing ghosts. Always `rm -f tests/fingerprint/*.UPDATED
  *.ERROR *.FAILED` before reading results; trust the `FAILED (should be PASS)` *log* lines.
- **Wrap module tests in `timeout`** (~60s suite; >2× = infinite packet loop). The per-test
  output is `tests/module/work/<testname>/test.out`; a multi-GB file = a loop — delete it (disk!).
- **Build from the toplevel project dir**, not `src/` (regenerates makefiles for new files; vital
  when checking out different commits).
- **Verify the tip is green first** — a "refactoring" branch can still hide real behavior changes
  and leftover bugs.
- **`-F tyf`** to drop graphical-fingerprint noise.
- See `scripts.md` (next to this file) for ready-to-adapt walk / sequence-editor / reword scripts.
