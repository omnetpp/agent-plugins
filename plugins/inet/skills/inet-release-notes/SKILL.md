---
name: inet-release-notes
description: |
  Write the WHATSNEW.md release-notes entry for a new INET Framework (OMNeT++) release.
  Discovers what changed from git history since the previous release, sorts changes into
  backward-incompatible and backward-compatible items, drafts them in INET's house style,
  and (after review) prepends the finished entry to WHATSNEW.md.
  Use when asked to write or draft the WHATSNEW entry, release notes, or "what's new"
  section for a new INET version/release.
---

# Writing an INET WHATSNEW.md release entry

The goal is a new top-of-file entry in `WHATSNEW.md` that matches the existing entries
in structure, ordering, and tone. The most recent entry (currently INET-4.6) is the
canonical example — open it and the previous one and mirror them. The full annotated
skeleton, ordering rules, house-style rules, and standard boilerplate sentences live in
[TEMPLATE.md](TEMPLATE.md); read it before drafting.

## ⚠️ The #1 rule: baseline against the PREVIOUS RELEASE

**This is the single most common and most important mistake — internalize it before drafting
anything.** A release entry describes how the codebase differs from **the previous release**
(the `vX.Y.0` tag), NOT how it differs from the start of this development cycle. The commit
range contains the whole cycle's churn — features added and later refined, even added and
later removed — and **none of that intra-cycle churn is a "change"** for someone upgrading
from the previous release.

Before you write that anything was **renamed, removed, had its default changed, or was
extended**, verify it existed and behaved differently at the previous tag:

```
git show <prev>:<path>            # e.g. git show v4.6.0:src/.../Foo.ned
git grep <symbol> <prev> -- src   # was this identifier present at the previous release?
```

Two failure shapes to reject outright:
- **Introduced-and-refined this cycle** → describe ONLY the net end-state, and list it as a
  backward-COMPATIBLE addition, not a backward-incompatible change. Example: a new parameter
  that "now defaults to true" is not a change if the parameter didn't exist last release — it
  simply ships that way.
- **Introduced-and-removed this cycle** → a non-event; do NOT mention it at all. Example: an
  enum added and then replaced within the same cycle never shipped, so "X was replaced" means
  nothing to a user of the previous release.

When in doubt, check the tag. Every backward-incompatible claim must survive this test.

## Workflow

### 1. Establish the release header facts

Ask the user (or infer, then confirm) only what git can't tell you:
- **Version** and **release type** (feature / stable / development).
- **Month + year** of the release.
- **Minimum OMNeT++ version** required.

### 2. Discover what changed (from git history)

Releases are tagged `vX.Y.0` (`git tag | grep '^v'`). The previous release tag is the
lower bound of the range.

```
PREV=v4.6.0          # the previous release tag
git log $PREV..HEAD --no-merges --format='%s'      # subjects, for clustering
git log $PREV..HEAD --no-merges --format='%an' | sort | uniq -c | sort -rn   # authors
```

**Expect scale and noise.** A feature release spans **thousands** of commits (the
v4.5.4..v4.6.0 range had ~2300). You cannot read them all — aggregate. A large fraction is
**not release-note material** and must be excluded: Python dev-tooling churn, test/fingerprint
infrastructure, build/CI/.github/prod/releng. In the 4.6 range these alone were ~450 commits.

**Cluster by meaning, not by prefix.** Many subjects start with an area-ish word
(`mrp`, `QUIC`, `EthernetPlca`, `checksum`, `ClockBase`, `All:`) — a useful clustering hint —
but the `Area: category: description` convention is **inconsistent** across a real range
(mixed case and style), so don't try to parse it as a strict format. Group commits into
themes by what they touch (clock, gPTP, QUIC, MRP, 10BASE-T1S, checksum/FCS, wireless PHY,
TCP read mode, queueing, visualizers, serializers, tutorials, showcases, docs, …). Renames,
removed defaults, and semantic/result-changing reworks are candidates for the
backward-incompatible bucket; new opt-in modules/protocols/features, stats, tutorials,
showcases, docs, and fixes are backward-compatible.

**Attribution is NOT reliably derivable from git — treat git as a weak hint only.** In
practice `git log --grep='contributed by'` finds nothing; the git author *handle* often
differs from the credited name (e.g. MRP authored by "DJtime" but credited to "Daniel
Zeitler"); some contributions are deliberately anonymized ("a generous industry partner");
and a contributor's commits may even fall outside this range. Use the author list only to
spot non-core-team names worth asking about, and **confirm every attribution explicitly with
the user** in step 5. Never invent a credit from a git author handle.

### 3. Group and categorize

- Fold many commits into a few coherent **themed items** — one theme = one numbered item.
  Never enumerate raw commits; write a narrative of what changed and why it matters.
- Split items into two buckets, **backward-incompatible** and **backward-compatible**, and
  order each bucket per the rules in [TEMPLATE.md](TEMPLATE.md) (major protocols/refactors
  first; tutorials → showcases → documentation near the end; "Notable bug fixes and other
  changes" is always the **last** item of the backward-compatible bucket).
- **Baseline every change against the previous release tag** — see the #1 rule at the top of
  this file. Confirm each renamed/removed/changed-default/extended claim with
  `git show <prev>:<path>` or `git grep <symbol> <prev> -- src` before writing it. This is the
  most common error by far; do not skip it.
- Decide which themes are major (own numbered item) vs minor (one paragraph folded into
  "Notable bug fixes and other changes").
- These are **candidates, not final**. The maintainer curates: some git-visible
  "backward-incompatible" themes get deliberately downplayed rather than elevated — e.g. in
  4.6 the SCTP→SimpleModule conversion and the SimpleModule/Module base-class rename were
  folded into "Notable bug fixes and other changes" / the intro instead of getting their own
  numbered backward-incompatible item, and the OMNeT++ version bump lives in the intro
  paragraph. Surface your proposed elevation/fold decisions for the user to adjust.

### 4. Draft the entry

Follow the skeleton and style rules in [TEMPLATE.md](TEMPLATE.md). Key points:
- Intro paragraph naming the 3–6 biggest highlights + the OMNeT++ requirement.
- The standard ChangeLog-pointer sentence.
- Each **backward-incompatible** item ends with an explicit impact statement (either
  "requires modification of models …" or "doesn't require model changes but may change
  statistical results …").
- Externally-contributed protocols/models get a closing attribution line.
- Neutral, professional, technical prose; real identifier names verbatim (plain text — no
  backticks/markdown); hard-wrap at ~78 columns.

### 5. Review, then prepend

Present the draft to the user for review (this is a curated document, not a changelog
dump — expect edits). After approval, prepend the entry above the previous one in
`WHATSNEW.md`, with the setext header underline matching the title length and a blank
line separating it from the entry below.

## Verify before finishing

- [ ] Header underline length matches the title (em-dash counts as one character).
- [ ] Intro paragraph + ChangeLog-pointer sentence present; OMNeT++ requirement stated.
- [ ] Two buckets present and correctly ordered; bug-fixes item is last.
- [ ] Every backward-incompatible item ends with an impact statement.
- [ ] Every "renamed / removed / changed-default / extended" claim verified against the
      PREVIOUS RELEASE TAG (not a mid-range state); items introduced-and-changed within the
      range describe only the net end-state, and introduced-and-removed items are dropped.
- [ ] Contributor attributions included and confirmed with the user.
- [ ] Lines wrapped at ~78 cols; plain-text style (no markdown bold/code/links).
- [ ] Entry prepended above the previous one; nothing below it disturbed.
