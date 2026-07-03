# Migration map — old skills/, plans/, incoming/ → skills-new/

*Working document for the 2026-07-03 restructuring — **all rows migrated**;
delete this file once the migration is accepted.*

## Generic skills (omnetpp-*)

| Target | Sources | Notes |
|---|---|---|
| omnetpp-fingerprint-testing | incoming/fingerprint-testing.md, simu5g/fingerprints.md, inet-branch-cleanup | D (exemplar, built earlier) |
| omnetpp-model-development | skills/omnetpp, incoming/omnetpp-tooling.md | running/debugging flags, config discovery, result analysis, opp_repl preference |
| omnetpp-coding-conventions | simu5g/coding_guidelines.md (generic parts) | explicit errors, ASSERT/exception, check_and_cast, no statics, msg/NED gotchas, INI syntax, "be critical"; Simu5G-only bits → simu5g stub |
| omnetpp-model-refactoring | simu5g/refactoring.md, move-code-refactoring.md, flatten-virtual-methods.md | genericized (test commands → project fingerprint skill; `.cascade/` refs fixed; Simu5G examples kept, labeled) |
| omnetpp-git-workflow | simu5g/SKILL.md (git), simu5g/rebase.md, incoming/git-workflow.md | staging discipline, destructive-op consent, incremental rebase, intent-preserving conflicts, green-at-every-commit, backup tags, PR-integration discipline |
| omnetpp-sim-debugging | incoming/debugging.md | vanishing-packet checklist, gdb-on-real-binary, Qtenv repro, log attribution, pcap-diff |
| omnetpp-branch-cleanup | plans/git-branch-cleanup.md, plans/simulation-project-branch-cleanup.md | SKILL.md wrapper + both docs as reference files (verbatim); opp_repl-based |
| omnetpp-branch-rebase | plans/git-branch-rebase.md | SKILL.md wrapper + doc verbatim; opp_repl-based |
| omnetpp-release-engineering | skills/omnetpp-dev | renamed; split into SKILL.md + changelogs.md + api-changes.md + whatsnew.md (content verbatim) |

## INET skills (inet-*)

| Target | Sources | Notes |
|---|---|---|
| inet-fingerprint-testing | (exemplar) | D |
| inet-dev-environment | incoming/building.md, incoming/environment-worktrees.md | toplevel make, dual-mode builds, setenv/INET_ROOT trap, worktree rules, stale-lib diagnosis |
| inet-test-suites | incoming/module-tests.md, incoming/protocol-unit-tests.md | SKILL.md (suite map + module tests) + authoring-tests.md + protocol-tests.md |
| inet-module-development | incoming/recipes.md, incoming/porting-workflow.md, incoming/inet-architecture-gotchas.md (cross-cutting only), skills/inet (display strings + doxygen) | SKILL.md + conventions.md + recipes.md + integration-patterns.md + gotchas.md |
| inet-branch-cleanup | skills/inet-branch-cleanup (+scripts.md) | moved; fingerprint section slimmed to reference the fingerprint skills; stale personal plan path removed; cross-ref omnetpp-branch-cleanup |
| inet-cosmetic-cleanup | skills/inet-cosmetic-cleanup (+find-smells.sh) | moved; build/fingerprint boilerplate → references |
| inet-release-notes | skills/inet-release-notes (+TEMPLATE.md) | moved verbatim |
| inet-showcase-creator | skills/inet-showcase-creator | moved; tool-specific names (grep_search) genericized |
| inet-statistical-tests | skills/inet-statistical-tests (+REFERENCE.md), incoming/statistical-tests.md | moved + new "CLI fallback" section in REFERENCE.md |

## Simu5G

| Target | Sources | Notes |
|---|---|---|
| simu5g-fingerprint-testing | simu5g/fingerprints.md (runner-specific parts) | ./fingerprints -d, -m = SUBSTRING, fp_stdout.log protocol, simulations.csv.UPDATED |
| project-stubs/simu5g | simu5g/SKILL.md, simu5g_arch.md, coding_guidelines.md (Simu5G-only bits) | routing + architecture red lines + build/run specifics |

## Other

| Target | Sources | Notes |
|---|---|---|
| oppenv-dev | skills/oppenv-dev | moved verbatim (own scope prefix `oppenv-`) |
| rst-editing | skills/rst-editing | moved verbatim (generic docs skill, unprefixed) |
| project-stubs/inet | (exemplar) + skills/inet (plans workflow, corrected) | plans workflow: develop in main checkout (worktree question dropped — worktrees get auto-removed) |

## Dissolved / not migrated

- **skills/omnetpp, omnetpp-dev, simu5g, inet** — dissolved into the targets
  above; retire the old directories once the new repo is installed (several
  names collide: install.sh will SKIP any existing non-symlink dir).
- **skills/caveman, grill-me, handoff, write-a-skill** — personal/meta skills,
  not project knowledge; stay in ai-config/skills.
- **incoming/inet-architecture-gotchas.md — deep protocol internals**
  (BGP/OSPFv3/MIPv6/IPsec/PIM architecture write-ups): NOT migrated to skills;
  candidate material for source-code docs. Kept in incoming/.
- **incoming/GAPS.md** — working notes; §3 blank spots (contributor
  quickstart, pre-PR checklist, CI docs) remain open TODOs.
- **inet-gsd-abandoned** (memory): personal workflow history, not migrated.
