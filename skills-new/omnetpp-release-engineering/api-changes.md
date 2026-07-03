# API Changes (doc/API-changes.txt)

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
