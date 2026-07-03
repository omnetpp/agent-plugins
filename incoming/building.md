# Building

*Extracted 2026-07-03 from Claude session memory (`~/.claude/projects/-home-andras-projects-inet/memory/`). Raw material for future INET dev skills — unedited: may contain machine-specific paths and session-specific observations. Source memory file cited per bullet.*

- Always run `make` from the **toplevel INET project directory**, never from `src/`. Toplevel `make` regenerates makefiles to pick up newly-added source files; running `make` in `src/` can produce a stale `libINET_dbg.so` (symptom: `Class "inet::Foo" not found -- perhaps its code was not linked in`). Command: `cd <inet-root> && make -j$(nproc) MODE=debug`. Matters especially when switching commits/branches where files appear/disappear. (inet-build-from-toplevel.md)
- Plain `make` only builds the **release** build. After every source change build BOTH: `make -j$(nproc)` (release) AND `make MODE=debug -j$(nproc)` (debug) — module tests run the debug lib (see Module tests). (inet-module-tests-use-debug-lib.md, mipv6-tunneling-refactor-plan.md)
- Confirm a stale lib isn't the culprit with `strings out/clang-debug/src/libINET_dbg.so | grep <symbol>`. (inet-module-tests-use-debug-lib.md)
- Run simulations only via the `inet` / `inet_dbg` wrapper commands, **never `opp_run` directly** (explicit user preference, repeated across notes). (inet-module-tests-use-debug-lib.md, mipv6-tunneling-refactor-plan.md)
