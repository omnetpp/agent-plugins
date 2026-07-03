# Per-component ChangeLog conventions

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
