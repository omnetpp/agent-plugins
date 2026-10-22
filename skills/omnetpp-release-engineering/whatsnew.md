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
  focus and highlights, in this order:
  - the character of the release (e.g. "This is primarily a bugfix release.");
  - the main new features (2–4), each with what it is good for, not just what it is
    (e.g. unused-entry reporting is "useful e.g. when porting models");
  - the main bugfix areas, as a short list of areas (not individual fixes).
  Do not present fixes as features here, and keep it consistent with the body: if a
  bullet presents something as a fix, the intro must not call it new support.
- Body: Organized into sections by component/area. Each section has a heading
  (plain text ending with colon), followed by a blank line, then bullet items
  indented with 2 spaces (`  - `).
- Footer: `See ChangeLogs in individual folders for details.` and a
  `Bugs fixed: https://github.com/omnetpp/omnetpp/issues?q=...+milestone%3AX.Y` link.

## Typical sections (include only those with changes, in roughly this order)

- Simulation kernel
- Configuration (if there are notable config option changes)
- NED
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
  related changes are best explained together, see grouping below).
- Keep bullets concise but informative — typically 1–4 sentences each.
- A bullet about a change that fixes an existing problem must make it clear that it
  is a fix, e.g. "Fixed X doing Y", "Fixed X not doing Y", or a "Fix:" prefix. This
  also applies to filling a gap in the implementation (e.g. support for a previously
  unsupported figure type, display string tag or config option). Do not present a fix
  as a new feature ("X now does Y"). The ChangeLog entries are already marked this way
  (see changelogs.md); keep the marking when turning them into WHATSNEW bullets.
- When a bullet combines new features and fixes, list the new features first, then the
  fixes in a separate sentence ("Fixed ...").
- Minor or numerous small fixes can be summarized as "Several bug fixes and
  minor improvements." or "Further bug fixes."
- Order bullets within a section roughly by importance (most significant first).
- Do NOT include raw commit hashes or file names that are meaningless to the user.
- Internal refactorings, code cleanups, and build system tweaks are generally
  omitted unless they have user-visible consequences.
- Wrap bullets at 80 columns, and do not split a backtick code span across lines.

## Brevity

WHATSNEW should not be longer than necessary; it is not the ChangeLog.

- Leave out reference details (lists of option values, lists of covered entry
  types), usage tips that the manual covers, and illustrative examples (e.g.
  "multiplied a packet count by 8").
- Describe a fix by its user-visible symptom, in 1–2 lines, not by its mechanism.
- Group related small fixes in the same component into one bullet, e.g. "Fixed
  several gaps and differences from Qtenv in the rendering of the graphical editor,
  such as ...", or "Fixed several `WATCH()` problems: ...".
- For features, state the effect, not the design rationale ("checking at the end
  also covers dynamically created modules", not "the primary motivation for the
  `end` option was ...").
- Say each thing once; avoid repetition within a bullet.
- Minor fixes (e.g. shadowed duplicate keys in a result file header) get 1–2 lines,
  or are left to the ChangeLog.

## Accuracy

- Do not inflate when summarizing: name the actual problems ("a compile error for
  `std::vector<bool>`", "a crash when displaying a null pointer ..."), not "compile
  errors and crashes". Check vague words such as "crashes" against the commits.
- When condensing, check what gets dropped: significant fixes, especially crash
  fixes and those with an issue number, must not disappear.

## Structure

- Do not describe the same change in two sections (e.g. `opp_neddoc` options and
  the NED Documentation Generator); describe it once and cross-reference it
  ("see below").
- A fix in a shared library should mention all affected front-ends (e.g. field
  scalar units: Python library and Analysis Tool).
- Fixes to features that are themselves new in this release (e.g. the picking of
  clipped figures in Qtenv) are part of the feature, not separate fixes.
