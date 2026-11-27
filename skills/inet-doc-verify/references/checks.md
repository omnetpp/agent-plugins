# What each check proves

`check_page.py` categories, what they test, and what a clean result does not prove.

| category | test | passes even when |
|---|---|---|
| stamp | `\| Verified with INET version: ``x``` line exists; `.. verified-commit: sha` is a commit | the sha is old |
| source-link | the github URL in the `Source files location` line names this page's directory | the visible label is right but the URL is stale (checked separately: the URL is what the reader clicks) |
| ned-ref | `:ned:`X`` (or `:ned:`label <X>``) names a type declared in src/, showcases/ or tutorials/ | X is the wrong type for the sentence |
| par-ref | `:par:`x`` (last dotted component) is a parameter declared in some NED type; built-in channel parameters (delay, datarate, ber, per, disabled) count | x belongs to another module than the prose implies |
| cpp-ref | `:cpp:`X`` occurs as a whole word under src/ | X is a different symbol with the same name |
| download | `:download:` target exists relative to the page | - |
| figure/image/video/include | file exists (through the `doc/media` symlink) and a video is non-empty | the picture is stale |
| literalinclude | file exists, Sphinx start/end anchors resolve in Sphinx's order and semantics (start-at keeps the line, start-after drops it, end-at keeps it, end-before drops it and ignores a hit on the first line), `:lines:` in range, slice non-empty; with a base commit the same slice at the base is diffed | the slice is right but the prose around it is stale (the WARN diff is for the reviewer) |
| ini-include | `include x.ini` target exists | - |
| ini-typename | `...typename = "X"` names a declared NED type (package prefix stripped, `${}` skipped) | X is not a valid replacement for that submodule's interface (`--run` catches that) |
| ini-param | last dotted component of a dotted key without `-` is a declared parameter | the pattern matches no module (`--run` does not catch unused entries either; OMNeT++ has no such diagnostic) |
| run | every non-abstract `[Config]` sets up with `--sim-time-limit=0s -r 0` in Cmdenv, results to a temp dir | the simulation would fail later than t=0 |
| literal (opt-in) | ``camelCase`` literals that are neither parameters nor types | - |

WARN vs ERROR for unknown names: a name that still occurs anywhere under src/ (as a word) is a
WARN because it may be a JSON key, figure attribute or result-filter parameter; a name found
nowhere is an ERROR because it was most likely renamed or removed.

`page_deps.py` direct-type sources: `:ned:` roles, declarers of every `:par:` name, submodule
and channel types used by the page's own .ned files (including `<default("X")> like I` forms),
ini `typename` values, and ini parameter keys whose submodule segment names a type that declares
the parameter (`*.router*.rip.mode` → `Rip`: catches protocols switched on by a `has<X>` flag).
Roles are read from every `doc/*.rst` of the page, not only `index.rst`. Fingerprint commits come
from the parsed `store.json` of each commit and its first parent: a textual diff of the store has no
`working_directory` in its hunk context, so it cannot attribute rows to pages. A simple module or channel maps to its .ned plus the same-named
(or `@class`-named) .cc/.h/.msg beside it; a compound module maps to its .ned only, its
submodules are the indirect set.
