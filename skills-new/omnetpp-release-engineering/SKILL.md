---
name: omnetpp-release-engineering
description: >
  OMNeT++ core release documentation workflow: updating per-component ChangeLog files from git
  history, maintaining doc/API-changes.txt with impact markers, and writing the WHATSNEW.md
  release entry. Use when preparing an OMNeT++ (core) release, updating ChangeLogs, documenting
  API changes, or drafting the OMNeT++ WHATSNEW entry. For INET release notes use
  inet-release-notes instead.
---
# OMNeT++ release engineering

The release process for OMNeT++ includes updating the ChangeLog files (every major folder contains one),
and writing an entry in the top WHATSNEW.md. ChangeLog files serve as a main input for writing the WHATSNEW entry.

Updating ChangeLogs is a 2-step process:

1. Raw ChangeLogs. The update_changelogs Python script uses `git log` to add raw
   entries from commits since the last release (named in the script!) at the top
   of each ChangeLog file. New entries are separated from old ones with a
   "----------- lines above this marker have been added from git log -----------"
   marker line.

2. Cleanup: Editing the ChangeLogs to delete irrelevant entries, re-wording for
   clarity, etc.

3. Removal of the marker line, as it is no longer needed.

Different ChangeLog files have different conventions.

Per-component ChangeLog conventions: see [changelogs.md](changelogs.md). API-changes.txt rules: see [api-changes.md](api-changes.md). WHATSNEW.md structure and style: see [whatsnew.md](whatsnew.md).
