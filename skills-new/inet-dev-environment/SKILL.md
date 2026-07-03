---
name: inet-dev-environment
description: >
  INET Framework development environment: building correctly (toplevel make, release AND
  debug), the setenv/INET_ROOT wrong-worktree trap, diagnosing stale libraries, and
  worktree/checkout rules. Use before building INET, when a build seems stale ("class not
  found", ghost test failures), when tests appear to run the wrong code, or when setting up
  to work on an INET checkout or branch.
---

# INET development environment

## Building

- Always run `make` from the **toplevel project directory**, never from
  `src/`. Toplevel make regenerates makefiles so newly added/removed source
  files are picked up; building in `src/` can produce a stale library
  (symptom: `Class "inet::Foo" not found -- perhaps its code was not linked
  in`). This matters especially when switching commits or branches.
- Plain `make` builds **release only**. After every C++ change build BOTH
  modes — `make -j$(nproc)` and `make MODE=debug -j$(nproc)` — because
  different harnesses load different libs: module tests run the **debug** lib
  (`libINET_dbg.so`); the `inet` command and fingerprint runs with `-s` use
  **release**. Editing C++, running only `make`, then running module tests
  executes STALE debug code (ghost failures that contradict a clean release
  build).
- Confirm/deny a stale-lib suspicion directly:
  `strings out/clang-debug/src/libINET_dbg.so | grep <symbol>`.
- Run simulations via the `inet` / `inet_dbg` wrappers, never `opp_run`
  directly.

## The INET_ROOT / setenv trap

A fresh shell may inherit `INET_ROOT`/`PATH` pointing at a **different INET
checkout or worktree** (check: `which inet`). Test wrappers dereference
`$INET_ROOT` — e.g. `tests/fingerprint/fingerprinttest` runs
`$INET_ROOT/bin/inet_fingerprinttest --directory $INET_ROOT` — so the suite
silently runs the OTHER tree's library against THIS tree's baselines. The
symptoms (mismatches, missing serializers, pre-change behavior) look exactly
like a stale or broken build, and rebuilding fixes nothing because the local
lib is never loaded.

Rule: shell state does not persist between agent tool calls, so start
**every** command block with

```
cd <inet-root> && source ./setenv -q
```

and, when anything smells wrong, verify `echo $INET_ROOT` prints this
checkout. Only the *run* step is affected — builds are cwd-relative.

## Worktrees and checkouts

- **Develop in the main checkout, on a topic branch**
  (`git checkout -b topic/X master`) — not in a git worktree under a
  tool-managed directory (e.g. `.claude/worktrees/`): such worktrees can be
  auto-removed between sessions. Committed work survives in the shared
  `.git` object store (`git reflog --all`, branch refs), but the working tree
  and uncommitted changes are gone.
- Commit often, so nothing depends on the working tree surviving.
