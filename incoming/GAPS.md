# Gaps — skill coverage vs. available knowledge

*Compiled 2026-07-03 by cross-checking the session-memory extraction (the theme files
in this directory) against an inventory of the existing skills in `~/.claude/skills/`
(inet, omnetpp, omnetpp-dev, inet-branch-cleanup, inet-cosmetic-cleanup,
inet-release-notes, inet-showcase-creator, inet-statistical-tests, simu5g, oppenv-dev,
rst-editing).*

## 1. Covered by NO existing skill — material now staged in this directory

| Topic | Staged file | Notes |
|---|---|---|
| Environment setup: `setenv`, `INET_ROOT`, wrong-worktree trap, worktree auto-removal | environment-worktrees.md | Highest-value gap — the wrong-worktree trap already cost real debugging time; two dedicated memory notes existed, no skill mentions `setenv`/`INET_ROOT` at all |
| Module-test mechanics | module-tests.md | Only fragments exist (in inet-branch-cleanup: `-f` flag, `timeout`, log path). Missing everywhere: test.err-vs-test.out rule, `.test` authoring idioms (`%#` comments, first-match-wins config, `%postrun-command`), log-size hygiene, `--no-build`/`-m debug` runner flags |
| Unit tests | protocol-unit-tests.md | `inet_run_unit_tests`, standalone opp_test harness recipe, round-trip-test-per-serializer rule — in no skill |
| Protocol conformance tests (`tests/protocol/`) | protocol-unit-tests.md | Framework + authoring gotchas (`%expected-failure`, wire-level observation, `.within()` semantics, lambda filters) — in no skill |
| Debugging techniques | debugging.md | Vanishing-packet checklist, gdb-on-real-binary, pcap-diff for ~tND non-determinism, log attribution — in no skill |
| Recipes (add a signal, Qtenv status label, configurator switches) | recipes.md | In no skill |
| Design patterns: additive/fingerprint-inert integration, dual-stack, porting workflow | porting-workflow.md | In no skill |
| Cross-cutting INET gotchas (networkConfiguratorModule default, Igmpv3/Mldv2 lockstep, reserved `network` keyword, chunkLength=serializer rule, msg struct-vs-class, …) | inet-architecture-gotchas.md | In no skill; file also contains deep protocol internals (BGP/OSPFv3/MIPv6/IPsec) that may belong in code docs instead — to be triaged when organizing |

## 2. Fragmented / duplicated across existing skills

- **Fingerprint knowledge lives in 3 places and none is complete for INET.**
  The best ingredient glossary is in `simu5g/fingerprints.md` — but for Simu5G's own
  `./fingerprints -d` runner, not INET's `fingerprinttest`. The cause→ingredient drift
  mapping is in `inet-branch-cleanup`. The byte-identical gate is in
  `inet-cosmetic-cleanup`. Nowhere documented for INET: `-s` (release exe) vs default
  debug, `-f` (ingredient filter) vs `-m` (line-filter regex), the stale-`.UPDATED`
  purge rule, the new-example recording flow (placeholder hashes), the
  protocol-registry `~tNlb` gotcha, the signal-check debug/release asymmetry
  (all staged in fingerprint-testing.md).
- **Build-from-toplevel** is stated in 3 skills (inet-branch-cleanup,
  inet-cosmetic-cleanup, inet-statistical-tests) but absent from the generic
  `omnetpp` skill (which has only a bare `make MODE=debug`), and the
  release+debug dual-build requirement is stated only as a statistical-tests
  precondition, not as the general rule it is (staged in building.md).
- **Commit-message convention** (`Area: category: description`) appears in
  inet-branch-cleanup and inet-cosmetic-cleanup; inet-release-notes warns it is
  historically inconsistent. One canonical statement needed (staged in git-workflow.md).
- **The `inet` skill is thin** relative to its "Developing INET modules" description:
  plans workflow + display strings + doxygen comments only. It is the natural hub for
  most of the staged material.
- **Statistical tests**: `inet-statistical-tests` is canonical for the opp_repl-MCP
  workflow, but the reliable CLI fallback (`inet_run_statistical_tests -m debug
  --no-build`, standalone `update_statistical_results`, the default-project gotcha,
  opp_repl crashing on the full ~913-config run) exists only in memory
  (staged in statistical-tests.md).

## 3. Blank spots — no material in memory OR skills, but needed for the stated audiences

- **Fresh-contributor quickstart**: clone → toolchain → (opp_env or manual) →
  `setenv` → first build → run an example. All existing material assumes a
  working setup.
- **Pre-PR checklist**: which suites must pass for which kind of change
  (C++ change vs NED change vs new example vs new protocol). Distillable from
  branch-cleanup + the staged testing files, but doesn't exist as a checklist.
- **INET C++/NED/msg coding conventions**: cosmetic-cleanup covers 6 smells;
  `simu5g/coding_guidelines.md` has good general rules (explicit errors,
  `check_and_cast`, no statics, INI syntax gotchas) but is Simu5G-scoped —
  INET has no equivalent.
- **CI**: what GitHub Actions run on an INET PR, what a contributor must expect/fix.
- **Documentation workflow**: building users-guide/developers-guide, NED
  documentation comments (showcase docs are covered by inet-showcase-creator;
  release notes by inet-release-notes; RST formatting by rst-editing).
- **Simu5G↔INET pairing**: which INET version/branch Simu5G builds against, how to
  set up the combined dev environment.
- **OMNeT++ core development** (planned for later): `omnetpp-dev` covers only
  ChangeLog/WHATSNEW release engineering — nothing on building omnetpp, its test
  suites, or kernel-dev practices.

## 4. Distribution gap

All skills currently live in the personal `~/.claude/skills` (sourced from
`ai-config/skills/`). Nothing reaches Simu5G developers or external contributors.
To decide when organizing: per-project `.claude/skills/` in each repo (auto-discovered
on checkout, needs machine-specific paths genericized) vs. a shared dev-skills repo
(single source of truth, extra install step) — plus how INET/Simu5G-common knowledge
(fingerprint ingredients, opp_test authoring, OMNeT++ tooling) is shared between the two.
