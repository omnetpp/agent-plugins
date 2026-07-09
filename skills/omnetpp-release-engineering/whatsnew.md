# Writing WHATSNEW.md

## Prerequisites

All ChangeLog files must be cleaned up (see rules above) before writing WHATSNEW.
doc/API-changes.txt should also be up to date.

## Primary sources

- ChangeLog files in every major directory (include/omnetpp/, src/sim/, src/envir/,
  src/cmdenv/, src/qtenv/, src/nedxml/, src/scave/, src/eventlog/, src/common/,
  src/utils/, ui/, python/, test/, doc/, samples/)
- `git log --oneline <last-release-tag>..HEAD` for additional context when ChangeLog
  entries are unclear or sparse.

## Header and structure

- Release header: `OMNeT++ X.Y (Month Year)` followed by a line of dashes.
- Opening paragraph: A brief (3–5 sentence) high-level summary of the release's
  focus and highlights. Mention the most impactful changes to set expectations.
- Body: Organized into sections by component/area. Each section has a heading
  (plain text ending with colon), followed by a blank line, then bullet items
  indented with 2 spaces (`  - `).
- Footer: `See ChangeLogs in individual folders for details.` and a
  `Bugs fixed: https://github.com/omnetpp/omnetpp/issues?q=...+milestone%3AX.Y` link.

## Typical sections (include only those with changes, in roughly this order)

- Simulation kernel
- MSG files, opp_msgc (or opp_msgtool)
- Result Recording
- Cmdenv
- Qtenv
- Fingerprints
- Command-line Tools (opp_makemake, opp_scavetool, opp_neddoc, opp_test, etc.)
- Python library (or Python libraries)
- Analysis Tool
- NED editor
- Simulation Launcher/debugging
- Other IDE Components (or IDE Misc)
- User Guide / Install Guide
- Tests
- Build

## Mapping ChangeLogs to WHATSNEW sections

- `include/omnetpp/ChangeLog` + `src/sim/ChangeLog` → Simulation kernel
- `src/nedxml/ChangeLog` → MSG files / opp_msgc
- `src/envir/ChangeLog` → Simulation kernel (result recording, config options) or its own section
- `src/cmdenv/ChangeLog` → Cmdenv
- `src/qtenv/ChangeLog` → Qtenv
- `src/scave/ChangeLog` → Command-line Tools (opp_scavetool) + Analysis Tool (lib) + Python library
- `ui/ChangeLog` → Analysis Tool, NED editor, Simulation Launcher, Other IDE Components, etc.
- `python/ChangeLog` → Python library
- `test/ChangeLog` → Tests
- A single WHATSNEW section may draw from multiple ChangeLogs (e.g. Analysis Tool
  draws from ui/ChangeLog and src/scave/ChangeLog and python/ changes).

## Writing style

- User-facing, narrative prose. Explain what changed and *why it matters*, not
  just what was done technically. Target audience: simulation model developers.
- Use backticks for code identifiers: `cPar`, `opp_run`, `parsimPack()`, etc.
- Reference GitHub issues as `(#NNNN)` or `(fix #NNNN)` when relevant.
- Each bullet should be self-contained: one change = one bullet (unless tightly
  related changes are best explained together).
- Keep bullets concise but informative — typically 1–4 sentences each.
- Minor or numerous small fixes can be summarized as "Several bug fixes and
  minor improvements." or "Further bug fixes."
- Order bullets within a section roughly by importance (most significant first).
- Do NOT include raw commit hashes or file names that are meaningless to the user.
- Internal refactorings, code cleanups, and build system tweaks are generally
  omitted unless they have user-visible consequences.
