---
name: omnetpp-dev
description: Skills useful for OMNeT++ developers
---
# Updating ChangeLogs

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

## IDE (ui/ChangeLog):

- Only user-facing changes should remain: bugfixes, and improvements or changes noticeable for the user.
- It must be written in terms that the user understands, so class names, source file names etc should NOT be in there.
- Entries should be prefixed with the name of the IDE component, such as "Analysis Tool:", "NED Editor:", "C++ Build:", "Simulation Launcher:", etc.
- The affected file names are there only to help interpreting the log msg, they should be removed.
- Adjacent entries that are part of the same change over a short period (a few days) should be merged
- If a log entry contains multiple distinct/unrelated items, it should be split into separate bullet items within the log entry
- Include entries about Eclipse platform updates (Eclipse, CDT, PyDev, etc version)
- When unsure, ask!!!

## Qtenv (src/qtenv/ChangeLog):

Similar rules as for the IDE. Refinements:

- Component names: "Graphics", "Generic Object Inspector", "Module Log View", etc.
- Include notes on Qt compatibility

## Test (test/ChangeLog):

- Prefix entries with the name of the test subdir: "core:", "fingerprint:", "anim/displaystring:", etc.
- Keep entries short
- Expect strong commit message "interference" (when the text of the log entry is
  not very relevant, because changes in several folders were committed together).

## Simkernel API (include/omnetpp/ChangeLog):

- This is the public C++ API of the simulation kernel, so keep everything except minor technical changes.
- Entries often start with "<classname>:"

## Simkernel Src (src/sim/ChangeLog):

- This is the implementation of the headers in include/omnetpp.
- Many (most?) entries should read are something like "Follow (or implement) change (or feature) described
  in include/omnetpp/ChangeLog". (Many "Added..." entries should be changed to "Implemented...")

## Envir (src/envir/ChangeLog):

- This is the simulation runtime environment: configuration handling, result file
  managers (scalar/vector/eventlog), debugger support, command-line options, etc.
- Envir-specific changes (result file handling, config options, debugger support,
  eventlog management) should be described fully.
- Many entries are "follow" changes where envir call sites are updated due to API
  changes in sim/ or common/. These should be brief, like "Follow cException changes
  described in src/sim/ChangeLog" or "Updated call sites for cPar::unparse() change".
- Drop entries where envir files were only incidentally touched (e.g., a header
  reorganization, an include change, or a formatting change).
- Expect strong commit message "interference" (changes in several folders committed
  together, with the log msg describing the main change, not the envir part).

## NED/MSG tools (src/nedxml/ChangeLog):

- Entries are about the NED compiler, message compiler (opp_msgtool/opp_msgc), NED type
  infrastructure, and built-in NED declarations.
- Prefix with component: "opp_msgtool:", "Message compiler:", "NED:", "Built-in NED
  declarations:", "NedTypeInfo:", etc.
- Mostly self-contained -- few "follow" entries from other modules.
- Include both user-visible changes (new NED syntax, msgc features) and internal fixes.

## Cmdenv (src/cmdenv/ChangeLog):

- Entries are about the command-line simulation environment: config options (cmdenv-*),
  output formatting, event banners, progress updates, fake GUI.
- Mostly self-contained, with occasional "follow" entries for sim/envir API changes
  (use "Follow..." phrasing, e.g. "Follow sim library change: ...").
- Keep all entries — this is a small changelog.

## Scave (src/scave/ChangeLog):

- Entries are about the result analysis library: result file loading/writing, sorting,
  exporting, Python bindings (nanobind), and opp_scavetool.
- Prefix with component where helpful: "OmnetppResultFileLoader:", "opp_scavetool:",
  "CSV export:", "python:", etc.
- Include nanobind/build changes as they affect the Python analysis workflow.

# API Changes (doc/API-changes.txt):

- Prerequisite: include/omnetpp/ChangeLog must be up to date.

- Lists backward-compatibility-affecting changes to the public C++ API (include/omnetpp/).

- Primary input: `git diff <last-release-tag> HEAD -- include/omnetpp/` for the actual
  header changes (turn off the pager!). Use `include/omnetpp/ChangeLog` for context and narrative.
- Each entry is tagged with an impact marker:
  - `(+)` new feature (new class, method, etc.)
  - `(!!!)` major incompatible change (old code will not compile or work)
  - `(!)` minor incompatible change (affects rarely used features)
  - `(-)` deprecated (possibly with a replacement)
  - `(x)` removed a previously deprecated item
  - `(i)` information

- Only include changes that affect compiling and running models. Internal/implementation
  changes do not belong here.

- Entries should be indented with 8 spaces after the marker tag.

- Entries often start with the class name, e.g. "(+)     cFoo: Added bar() method."

- Related entries may be grouped (e.g. "This change is part of the X API.").

- Do NOT mention header file names. The full OMNeT++ API is accessed by users
  via the omnetpp.h umbrella header.

- Be specific, and avoid handwavy statements like "foo() and similar functions...".
  ChangeLogs are written in a more casual style, so they are often not sufficiently
  precise to serve as input for the API-Changes file. You need to look at the git
  diff.

- When writing an entry for a "redesign" or "overhaul", decompose it into separate
  entries for each distinct compatibility concern: removed items, changed behavior,
  new additions. Do NOT write a single narrative entry describing how something
  was reimplemented internally.

- "X was reimplemented using Y" is NOT an API change. Only the observable differences
  matter: what was removed, what signatures changed, what behavior changed.

- Never use "etc." or "and similar" when listing removed or changed items.
  Look at the git diff and list every name explicitly.

- When listing removed classes or functions, use the exact names from the diff.
  Do not infer or approximate names from context or commit messages.

- Macros that still exist but now behave differently (e.g. became no-ops or aliases,
  or changed capture semantics) ARE API changes and must be documented, even though
  they still compile.

- Classes marked @ingroup Internals are still public API if they are SIM_API-annotated.
  Their removal is a (!) incompatible change.

  
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
