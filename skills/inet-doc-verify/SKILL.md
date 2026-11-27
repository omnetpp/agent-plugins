---
name: inet-doc-verify
description: |
  Verify that INET showcase and tutorial pages (showcases/*/doc/index.rst, tutorials/*/doc/index.rst)
  are still correct for a given INET commit or release, and move their "Verified with INET version"
  stamp. Runs local deterministic checks (NED type and parameter names in :ned:/:par: roles and ini
  files, literalinclude anchors and snippet drift, figure/video/download files, 0-second network
  setup of every config), then a diff-driven text review limited to the commits that touched what
  the page depends on since it was last verified. Use when asked to verify, re-verify, check, or
  re-stamp showcases or tutorials for a release or master commit, to find pages invalidated by
  recent changes, or to update the "verified with" line. Does NOT run fingerprint, statistical or
  chart tests (CI does) and does NOT judge visuals.
---

# INET doc page verification

A page is "verified at commit X" when (1) every name and file it references resolves at X,
(2) every config sets up at X, and (3) no commit between the previous verified commit and X
changed what the page's prose claims. Steps 1-2 are scripts. Step 3 is a reading task that
the scripts narrow down to the relevant commits. The stamp moves only after the user has seen
the report.

Scripts live in `scripts/` (Python 3, no dependencies; run from inside the INET repo or pass
`--inet-root`). `PAGE_DIR` is the directory holding the simulation and `doc/index.rst` (the other `doc/*.rst` files, e.g. tutorial steps, are checked as part of the page; the stamp lives in `index.rst` only)
(e.g. `showcases/wireless/hiddennode`, `tutorials/bgp`).

## Step 0: scope and base commit

1. List the pages: `grep -rl "Verified with INET version" showcases tutorials --include=index.rst`
   gives the stamped ones. Pages without a stamp line are not verified yet (treat as "verify from
   scratch" and say so).
2. Target commit = what the user names (release tag, sha, or current HEAD). Check out or
   `git worktree add` that commit if the working tree is not already at it; the scripts read the
   working tree, not git objects.
3. Base commit per page: the `.. verified-commit: <sha>` comment under the stamp line. If absent,
   the scripts fall back to the latest tag of the stamped version (`4.6` -> `v4.6.x`). Say in the
   report which base was used; a tag base is looser than a sha base.

## Step 1: deterministic checks (all pages, seconds)

```
scripts/check_page.py PAGE_DIR... --quiet            # names, anchors, files, snippet drift
OMNETPP_ROOT=~/omnetpp-dev scripts/check_page.py PAGE_DIR... --quiet --run   # + 0-second setup per config
```

- `--run` needs the OMNeT++ root (or run after `. setenv`) and a built INET; it sets up every
  non-abstract config with `--sim-time-limit=0s`, so NED/ini errors, bad typenames and parameter
  type errors surface. Budget a few seconds per config; big networks take longer (`--timeout`).
- `--since REV` overrides the snippet-drift base for literalinclude slices.
- `--literals` adds INFO lines for ``camelCase`` literals that are not parameters (noisy; use when
  a page is suspected of naming parameters without the `:par:` role).
- `--json` for machine-readable output. Exit code 1 means at least one ERROR.

Reading the output:
- **ERROR** = the page is wrong at this commit (missing type/parameter/file, broken anchor,
  config that does not set up). Must be fixed or explicitly waived before stamping.
- **WARN** = needs a human: a snippet that changed since the base (the diff is printed; decide
  whether the prose around it still matches), a name not declared in NED but present in src/
  (figure attribute, result-filter parameter, JSON key: usually fine), a `:par:` holding an
  expression, a page with no `verified-commit` comment.
- `:ned:` on a parameter name and `:par:` on a type name are reported with a hint; they are role
  misuse, fix the role.
- Videos and figures live in the separate `media/` tree (`doc/media` is a symlink), so a missing
  video means the media checkout lacks it, not that git lost it.

See [references/checks.md](references/checks.md) for what each check does and does not prove.

## Step 2: what changed since the base (all pages, seconds)

```
scripts/page_deps.py PAGE_DIR...            # Markdown; --json for machine-readable
```

Per page it prints the base..target range and four commit lists:
1. commits touching the page directory (someone edited the showcase itself);
2. commits that changed this page's rows in `tests/fingerprint/store.json` (the `*.csv` files on
   releases before the store), each with the ingredient sets that moved and the configs: behavior
   changed and the baseline was re-recorded (apply the ingredient rule of Step 3);
3. **direct** commits: files implementing the NED types the page names in any `doc/*.rst`
   (tutorial steps included) or sets parameters of by ini key, with the files touched;
4. **indirect** commits: directories of every type reachable through submodules (large; scan
   subjects only, open one when its subject names something the page explains).

"NOTHING CHANGED in the dependency set" means step 1 alone decides the page.

## Step 3: diff-driven text review (only pages with commits in lists 1-3)

For each such page, read the page once and the listed commits once, then answer one question
per commit: *does this change contradict a sentence, number, parameter name, default value,
figure caption or included snippet on the page?* Use `git show <sha>` on the direct commits
and `git show <sha> -- <page dir>` on the page-directory commits. Many pages fit one agent;
spread the pages over parallel subagents when there are more than about ten, one page set per
agent, each returning findings in the format below.

Rules for this step:
- Evidence or nothing: every finding quotes the page sentence and names the commit. A finding
  without both is dropped.
- Report, do not edit. The user decides what to fix and what to waive.
- Decide which side is wrong before calling a contradiction a page error. If the page describes
  behavior a user would expect (an icon goes away on close, a statistic covers all packets) and
  the code does not deliver it, suspect the code first: look for the missing half (a signal that
  is emitted but not subscribed to, a removal function that nothing calls, a parameter that is
  read but ignored). If it is there, report the item as **SRC-BUG**, not FIX: the page sentence
  stays as it is, and the defect goes to the `inet-bug-report` pipeline. Never propose rewording
  a page so that it describes a defect as intended behavior.
- Every proposed page edit is checked in context: read the whole paragraph (and the section
  heading) with the new wording in place, and make sure no other sentence still says the
  opposite. Example of the failure: "displays icons above the endpoints of an active
  connection" two lines above a new "the icons are not removed when it is closed".
- Do not invent numbers. If a commit changed a result (list 2 or a direct change to a traffic
  parameter), say that the stated numbers must be re-measured; do not estimate new ones.
- A re-recorded fingerprint row is not automatically "results moved". Compare the ingredients of
  the old and new row (`git show SHA -- tests/fingerprint/`): if the `tplx` value is identical the
  event timeline, module paths and frame lengths did not change and numbers/narratives on the page
  stand; a `tyf`-only change is display strings; a `~tND`-only change is serialized packet bytes
  and matters only where the page shows bytes (Wireshark or hex screenshots, FCS, sequence
  numbers). Only a changed `tplx` (or `~tNl`) makes the page's results a HUMAN item.
- Indirect commits are a scan, not a review: open one only if its subject touches something the
  page explains (a protocol the page is about, a visualizer the page shows).
- Do not propose `review-as-pro` here: it is for work-in-progress showcases, not for finished
  pages. When the base is too old to give a useful commit list (e.g. a `3.6` stamp), pass a
  narrower base with `--since` (both scripts): the last commit that edited the page's own prose (skip bulk mechanical edits
  such as an all-showcases version bump), or ask the user which release the page was checked at.

## Step 4: report

One table, one row per page, then details only for rows that are not PASS:

| page | base | errors | warnings | commits (page/fp/direct) | verdict |

Verdicts: **PASS** (no ERROR, no unresolved WARN, no contradicting commit), **FIX** (ERRORs or
confirmed contradictions where the page is the wrong side, each listed with file:line and the
commit), **SRC-BUG** (the page states intended behavior and the code fails it: name the source
file:line and the missing piece; the page is not edited and not stamped until the source fix
lands), **HUMAN** (snippet drift
or a commit whose effect on the prose could not be settled from the text; list the open items).
Give the report before touching any page.

## Step 5: stamp (after the user accepts PASS rows)

```
scripts/stamp.py PAGE_DIR... --commit <target sha> [--version master]
```

Writes `.. verified-commit: <full sha>` after the stamp line block (replaces an existing one)
and, with `--version`, rewrites the visible version text. Stamp only pages the user accepted;
a FIX page gets stamped after its fix, in the same commit as the fix.

## Caveats the scripts cannot cover

- Name checks are existence checks across all NED files: a parameter that exists on *some*
  module passes even if the page attaches it to the wrong module. Step 3 and `review-as-pro`
  cover that.
- `--run` sets up the network only; it does not run the simulation. Behavior changes are the
  job of fingerprint and statistical tests on CI, and of list 2 in step 2.
- Visual regressions (what a video or screenshot shows) are out of scope.
