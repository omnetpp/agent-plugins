---
name: omnetpp-review-brief
description: >
  Write a dense reviewer's brief for a pull request, topic branch or commit range
  of an OMNeT++-based model library (INET, Simu5G, ...): a ranked list of verified
  findings that tells a human reviewer where to spend review time -- user-visible
  NED interface changes (a bundled script cross-checks large NED diffs), shifts of
  responsibility, key data-structure changes, changes in how modules communicate,
  commit claims checked against the diff, the quality of added tests, verification
  state and PR shape. Use when asked to summarize, brief, or prepare the review of
  a PR, branch or commit range for a human reviewer, or to list what changed
  architecturally between two revisions. Not a bug hunt (use /code-review) and not
  release notes (use the release-notes skills).
---

# Reviewer's brief for a branch or PR

The reader is a human reviewer who knows the codebase. They will read the
commits themselves. The brief tells them what they would NOT get from reading
the commits in order, ranked by what they have to do about it:

- net effects that are spread over several commits;
- commit claims (markers, "inert", counts, "nothing calls this") checked
  against the diff -- confirmed or contradicted;
- what no commit mentions: interface breaks, ownership and lifetime changes,
  a verification gap, a stale message, a mismatched test description;
- patterns across commits: mixed goals, test history, marker misuse;
- where the reviewer's judgment is needed.

It is a fact sheet with evidence, not a verdict: it does not approve or reject,
and it does not hunt for bugs. Conflicts with the project's stated rules are
findings like any other, ranked high.

The skeleton is in [TEMPLATE.md](TEMPLATE.md). Read it before writing.

## Density rules

The value of a brief is insight per word. These rules override any habit of
filling a template.

- **Each fact appears exactly once.** There is no TL;DR that sections then
  restate, and no question list that restates findings. The top of the ranked
  list IS the summary. A question belongs to the finding that raises it, as
  its last sentence ("Ask: ...").
- **No empty sections.** A check that found nothing gets one entry in the
  single "Checked, nothing found" paragraph at the end (a comma-separated list,
  with a few words of method each where the method matters). Never write a
  heading followed by "none found".
- **Verified is the default.** Do not write "I verified this". Mark only the
  exceptions, in parentheses: "(from the commit message)", "(from the
  logbook)", "(not checked)", "(inferred from names)".
- **Do not restate commit messages.** If a commit message explains a change
  well, the brief cites the commit and adds only what the message does not
  say. Rationale the author already wrote is not a finding.
- **One finding, one bullet, one ask.** A bold title that states the finding
  as a short sentence, then only what the title does not say: what it was
  before if that is not obvious, who is affected, the evidence. If the title
  says everything, the body is just the evidence. A finding carries at most
  one "Ask:"; two issues or two asks are two findings. Keep the body under
  about 80 words; a finding that needs more is usually several.
- **Wrap lines at about 80 columns.** The brief is read in its Markdown source
  and in diffs; a finding on one physical line is unreadable there.
- **Evidence is compact**: `file:line` at the tip (at the base for removed
  things) and the commit as hash plus an abbreviated subject of two to five
  words, e.g. `710fecdf5` ("CbrSender: cbrGeneratedBytes unit"). Every commit
  citation carries the abbreviated subject, because branches are rebased and
  bare hashes stop resolving; full subjects are not needed.
- **Prose, but short.** Full sentences, no fragment chains joined by colons,
  semicolons or arrows; write the verb ("renamed to", "now calls"), not an
  arrow. No invented abbreviations. No tables. Nested bullets only for a real
  list inside a finding.
- **Budget.** Aim for one screen of header plus findings for a typical branch,
  and stay under about 150 lines even for a large one. A finding that needs no
  reviewer action is one line in "Minor". The method note is at most three
  lines. When over budget, demote the lowest-ranked findings to one-liners;
  never pad.

## Ranking

Rank by what the reviewer has to do, then by reach within a level:

1. **Decide before merge**: a rule conflict; a claim of inertness or of a
   count that the evidence does not support or that was never verified; a
   change that breaks user configs, NED or analysis scripts, or silently
   changes results; a dropped duty with no new owner; a branch that should be
   split.
2. **Check closely**: design changes a reviewer must judge -- a responsibility
   moved, a communication mechanism changed, ownership or lifetime of key state
   changed, a new interface or extension point, tests whose oracle or
   robustness is doubtful.
3. **Cheap fixes**: wrong or stale commit messages, misleading comments or test
   descriptions, marker misuse, leftover merge text.
4. **Minor**: one line each.

Reach means who actually hits it. A removed result that nothing in the repo
reads ranks below a removed parameter that every example sets. Say who is
affected.

## Step 0 -- fix the range

- Topic branch: `base = git merge-base <target> <tip>`, normally against the
  branch it will merge into.
- PR: `gh pr view <N> --json baseRefName,headRefOid,title,body,commits`
  (read-only), then `git fetch origin pull/<N>/head:refs/review/pr-<N>`.
- Commit range: as given. Check that base is an ancestor of tip
  (`git merge-base --is-ancestor`); if not, say so and use the merge base.
- Push state: compare the tip with its remote counterparts
  (`git branch -a --contains <tip>`, `git rev-parse`).

## Step 1 -- orient and shape the brief

- `git log --reverse --format='%h %s' base..tip`, then read every commit
  message in full (`git log --reverse --stat --format='=== %h %s%n%n%b'`).
  The messages are claims to check, and the stated goal comes from them, the PR
  description or a plan document.
- `git diff --stat=200 --dirstat=files,3 base tip`: where the weight is.
- **Classify the weight**: model code, refactoring, tests, configuration,
  baselines. The classification decides where the effort goes. A branch that is
  mostly tests is reviewed mostly through its tests (step 7); a branch that
  changes the NED interface mostly through step 2. Do not spend effort on an
  architecture section that the branch gives no material for.
- **Group the commits by goal.** One goal is one sentence. The groups go into
  the brief as one line each: the goal and its commits as a range (first and
  last hash with abbreviated subjects, plus the count), listing single hashes
  only for a goal of one or two commits or a non-contiguous group. If the
  branch serves more than one goal that could be reviewed and merged
  separately, propose a split as a level-1 finding.
- Look for the execution record, if the project keeps one (logbook, CI run,
  PR comments): what was run on which commit, and what was not run on the tip.
  The verification state goes into the header.

## Step 2 -- external interface (NED)

When the NED diff is small, read the changed NED files at both revisions. For
larger diffs, or as a cross-check, run the bundled script:

```
python3 <this-skill-dir>/ned_interface_diff.py <base> <tip> \
    --repo <repo> --external <dependency NED roots...> > <scratch>/ned-diff.md
```

`--external` lists the NED source roots of the libraries the project builds on
(for an INET-based project, INET's `src`); they only resolve base types. The
script needs `opp_nedtool` on `PATH` and reads `.nedfolders`/`.nedexclusions`
at each revision. It reports, per NED type with inheritance flattened: types
added, removed, moved or renamed (candidates); base types and interfaces;
parameters (added without default, removed, renamed, type, value, default vs
FIXED, unit, volatile, `@mutable`, declaring type); deep assignments; gates;
submodules; `@class`, `@signal`, `@statistic`; connections; doc-comment
changes; and module-tree path changes (the ini keys that move), each in the
type that introduces it.

Then the judgment work:

1. Classify each change for a user upgrading from base: *breaks* configs, NED
   or analysis scripts; *silently changes results* (a default, an effective
   value, a statistic's source, unit or record mode); or *additive*. Additive
   changes are one line in "Minor" unless they matter to the review.
2. Confirm rename candidates from `git diff -M`, migrated ini lines and the
   commit message.
3. For everything that breaks, write one imperative migration line.
4. C++ side of parameters: a removed parameter still read with `par("...")`,
   or a new `par()` read without a NED declaration.
5. Names C++ builds or looks up as strings (`create(`, `registerSignal(`,
   `recordScalar`, `getSubmodule(`, `findSubmodule(`, `getModuleByPath(`,
   `hasPar(`, `gate(`). List the identifier-like literals on changed lines:

   ```
   git diff -U0 base tip -- '*.cc' '*.h' | grep -E '^[-+][^-+]' \
     | grep -v -E 'EV|cRuntimeError|throw|//' \
     | grep -o -E '"[A-Za-z][A-Za-z0-9_.^-]*"' | sort | uniq -c | sort -rn
   ```

   Trace each one that names a module, signal, parameter or prefix. For each
   NED name renamed or removed, `git grep` the tip for the old name in string
   literals.
6. Read flagged doc-comment changes: report a change of meaning of an
   unchanged declaration.
7. Blind spots of the script for this range (non-literal `like` expressions,
   undiffed external libraries, a dependency upgrade inside the range) go into
   the method note only if they apply.

Secondary interfaces, when touched: the C++ API for users who subclass (public
or virtual methods removed or retyped, pure virtuals added or removed), `.msg`
fields used by applications, XML/config file formats, result names recorded
outside `@statistic`.

## Step 3 -- responsibilities

For each module whose code changed beyond cosmetics, compare its duties at
base and tip: the messages, gates and timers it handles, its `Enter_Method`
entry points, the state it owns, the signals it emits or subscribes to. Use
`git diff --color-moved=zebra --color-moved-ws=allow-indentation-change` and
`git diff -M` to find moved code. Report only modules whose SET of duties
changed: transferred, gained, dropped, split, merged, new, removed. A dropped
duty without a new owner is level 1. Flag accumulation: a module gaining a
duty from another layer, plane or domain. Internal restructuring with unchanged
duties is not a finding.

## Step 4 -- key data structures

A structure is key if it crosses a module boundary (packet, chunk, tag,
control info, a struct in a method signature, a signal payload), is a shared
registry in an infrastructure module, is the primary state of a module, or is
serialized. Report fields added, removed or retyped; key and cardinality
changes (highlight these); ownership and lifetime (raw vs smart vs value
pointer, who deletes); the sets of writers and readers; enum values; serialized
sizes. Method: `git diff -- '*.msg'`, member and container declarations in
`.h` diffs, `git grep` for writers and readers at both revisions.

## Step 5 -- communication between modules

For the touched modules, compare the interaction edges (from, to, mechanism,
what flows) at base and tip. Grep markers: `send(`, `sendDirect(`,
`check_and_cast<`, `getModuleByPath`, `ModuleRefByPar`, `getParentModule()->`,
`Enter_Method`, `emit(`, `subscribe(`, `receiveSignal`, `->par(`,
`par(...).parse(`, `addTag`/`getTag`/`findTag`, infrastructure setters and
getters, `initialize(int stage)`, `static`. Report new and removed edges,
mechanism changes ("A now notifies B with signal S instead of calling M"),
direction changes (pull to push), new coupling to infrastructure.

Check every new or changed edge against the generic rules in
`omnetpp-coding-conventions` and the project's red lines from its entry-point
skill (e.g. `simu5g-dev`): a signal used as a request, a cross-module call
without `Enter_Method`, another module's parameter read, configuration pushed
with `par().parse()`, an initialization-order dependency without a stage that
guarantees it.

## Step 6 -- claims against reality

Check every commit message claim that can be checked cheaply, and report
contradictions and unverified claims:

- markers: a `refactor:`/`cosmetics:`/`cleanup:`/`docs:`/`test:` commit that
  changes the NED interface, a default, examples or baselines; a `fix:` that
  also adds features;
- numbers: re-recorded row counts, moved ingredients, test pass counts --
  recount them from the diff (e.g. `git diff -U0 c~1 c -- <baselines> | grep
  -c '^-[^-]'`), and compute the net move over the range keyed by test
  identity;
- "nothing calls this", "no subclass redefines it", "only error paths change":
  grep for it;
- stale text: counts or names from a previous base, leftover merge-conflict
  blocks, references a reader cannot resolve (bare hashes of other branches,
  plan item ids).

A confirmed claim is not a finding; it goes into the method note as a count
("12 claims checked, all confirmed except those listed").

## Step 7 -- tests

When the range adds or changes tests, review the tests themselves; read their
bodies, not only their commit messages. Per test file, or per group of similar
ones:

- what it claims, and whether the checks actually assert that;
- where the expected values come from: a transcription of a spec, a closed
  form, an invariance, or the model's own output (a change detector only);
- tolerance: justified by the case, or loose enough to hide the error it
  exists to catch;
- robustness: does it reach into internals (protected members, generator
  state, module paths, RNG draw order) that an unrelated change would break?
- expected failures: does each describe a real, named defect, and does its
  one-line reason match its description?
- cost and wiring: runtime, the runner and make target, CI, environment
  dependencies (e.g. a Python package);
- project rules for tests (e.g. a spec-oracle rule, "tests that found bugs go
  first").

Also: baselines re-recorded (which, why, with what stated reason), tests
removed, disabled or made more lenient, examples changed. A test that is good
is not a finding; a doubtful one is.

## Step 8 -- write the brief

Fill in [TEMPLATE.md](TEMPLATE.md) by the density rules and the ranking. Before
saving, reread the draft once and cut: every sentence that repeats another,
every sentence that only says a check found nothing (move it to the closing
paragraph), every restated commit rationale, every "I verified". Split every
finding that carries two issues or runs past about 80 words, and check that
no line is longer than about 80 columns.

Write the brief to the location the project skill names (default: the
scratchpad). In chat, give the top findings in a few lines and the path.

## Scale and delegation

- Small range (under ~30 changed files): do everything inline.
- Larger: always run the NED script yourself. Delegate grep-and-list evidence
  gathering (steps 4-5) and the reading of large test sets (step 7) to
  cheaper-model subagents, one per subsystem or test group, each returning
  structured lists with `file:line`. Do the ranking and synthesis yourself.
  Spot-check at least three items of every subagent report against the code;
  mention the spot-checks in the method note.
