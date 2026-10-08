---
name: simu5g-dev
description: Rules for working with Simu5G, incl. which INET/OMNeT++ skills apply and the commit-subject format (change-type markers)
---

# INET and OMNeT++ skills

Simu5G is built on INET and follows INET's architecture and conventions. Rules
apply in this order of precedence:

1. `simu5g-*` skills and the rules in this file -- they WIN on any conflict.
2. `inet-*` skills -- the baseline for everything Simu5G does not regulate
   itself: coding and documentation conventions, NED/C++ idioms, module design,
   test authoring, cosmetic cleanup, branch cleanup.
3. `omnetpp-*` skills -- platform mechanics and generic workflows. Skip the ones
   about developing OMNeT++ itself (e.g. `omnetpp-release-engineering`).

An INET rule stays in force here unless a Simu5G rule overrides it. Silence in
the Simu5G skills means "INET's rule applies", not "no rule".

INET skills also describe INET's own repo mechanics: test runner commands and
flags, `INET_ROOT`/setenv, baseline file locations, the WHATSNEW workflow.
These do NOT carry over literally. Use the Simu5G counterpart where one exists,
and check it in the Simu5G tool's source, because commands and flags differ
(e.g. INET runs `./fingerprinttest`; Simu5G runs the `./fingerprints` wrapper,
which takes the binary and the directory from `SIMU5G_ROOT` -- a stale or
foreign `SIMU5G_ROOT` silently tests another worktree):

| INET skill                | In Simu5G                                         |
|---------------------------|---------------------------------------------------|
| inet-fingerprint-testing  | simu5g-fingerprint-testing (concepts carry over)  |
| inet-dev-environment      | same traps, with SIMU5G_ROOT for INET_ROOT        |
| inet-statistical-tests    | workflow applies; Simu5G's own statistics/ repo   |
| inet-test-suites          | authoring idioms apply to Simu5G's tests/module   |
| inet-release-notes        | does not apply (WHATSNEW only on request)         |

When the work changes INET itself (an INET fix proposed for a Simu5G need), the
`inet-*` skills apply in full, without Simu5G overrides.

# Commit subject format

Commit subjects carry a change-type marker after the module/subsystem prefix:

```
<module/subsystem>: <type>: <topic>
```

e.g. `binder: fix: out-of-bounds read in getServingNode()`. Multi-subsystem
commits list the modules comma-separated (`mac,phy: ...`). A change that
touches one KIND of thing across the whole tree names that kind instead of
listing directories: `NED cosmetics: <topic>`, not
`src,simulations,emulation: cosmetics: <topic>`.

Related commits are grouped VISUALLY in the log by a GROUP PREFIX in front of
the module list:

```
<group>: <module/subsystem>: <type>: <topic>
```

A group is a series of commits that serve ONE goal that can be stated in one
sentence: a plan, a feature, a refactoring, a tree-wide sweep. The group name
names that goal, so in `git log --oneline` the series reads as one block. For
a plan executed on a topic branch, the name is the branch name without
`topic/` (`teid:`, `cplane:`, `ipv6-sessions:`); otherwise a short name for
the goal (`layout:`, `watches:`).

The goal decides membership, not when or where a commit was made. A commit
belongs to the group if it is a step toward the goal. That includes the tests
written for the goal and the `fix:` commits that the work exposed or depends
on. A commit made alongside the work for an unrelated reason does not belong
to it: it gets no group prefix, or its own group.

e.g. `teid: gtp,ip2nic: refactor: ...`, `layout: statsCollector: cosmetics: ...`,
`watches: apps: state members are WATCHed`.

The subsystem prefix for the Sphinx website under `doc/src/` is `website:`,
not `doc:` -- e.g. `website: added Releases item to the main menu` or
`website: docs: README describes how the website is deployed`. Older `doc:`
subjects on `doc/src/` predate this and are not a counter-example.

Markers: `fix:`, `refactor:`, `cosmetics:`, `cleanup:`, `docs:`, `test:`
(`test:` = the commit only adds or changes tests or fingerprint baselines).
Pick the marker by what the commit actually does, not by which files it
touches. Variants seen in older history -- `rename:`, `refactoring:`,
`fixes:`, `bugfix:`, `feature:` -- are drift; do not use them or copy them
as precedent.

Every marker is a claim a reviewer can check: `refactor:`, `cosmetics:`,
`cleanup:`, `docs:` and `test:` claim that the model's behavior does not
change; `fix:` claims a correction. NO marker means an INTENDED change of
behavior or interface: a feature, a deliberate behavior change, a
restructuring, a removal, a dependency upgrade. These are the commits to read
carefully, and the candidates for WHATSNEW. There is deliberately no
`feature:` marker: the markers are useful because they are exhaustive, and an
optional one would make both `grep` and the absence of a marker meaningless.
To flag an unmarked commit whose effect matters, end the subject with
`(behavior change)` or `(fingerprint change: <what moved>)`.

A fix of a LATENT bug -- one that no current configuration reaches -- is still
`fix:`, never `refactor:`. `refactor:` is reserved for changes whose behavior
is identical in EVERY state, reachable or not; "no config reaches the
difference" does not make a change a refactoring. A preparatory change that
removes a trap for the next commit is a fix, too. Write "latent" and
"fingerprint-inert" in the body, in the "Fault: ... Fix: ..." form below.

So the markers separate the risk classes: `fix:` and unmarked commits are
where behavior (and thus fingerprints) may legitimately change; `refactor:`,
`cosmetics:`, `cleanup:`, `docs:` and `test:` commits are expected to be
fingerprint-inert. They also make each class of change mechanically greppable
when assembling release notes or auditing what moved between releases.

A fix is normally its OWN commit. When a fix exceptionally rides inside a
larger feature commit, the message body must explicitly call out the fault
and the fix, including the literal word "Fix:" -- the established pattern is
"Fault, exposed by ...: <what was wrong and how it failed>" followed by
"Fix: <what changed>". Deliberate exclusions from a change's scope (e.g.
"the DC networks DELIBERATELY stay SDAP-less") also belong in the message of
the commit that defines the change, so a log reader cannot mistake them for
omissions.

# Tests that found bugs go first

When a new test suite exposes defects, and the tests are refined while the
defects are fixed, the tests go FIRST in history, in their FINAL form, as one
commit; the code fixes follow it. Do not let test edits ride inside the fix
commits, and do not add a later "fold the checks back in" commit. The suite
is red from the test commit until the last fix lands -- accepted, because the
history then demonstrates each defect before the commit that fixes it. Every
commit must still COMPILE, and the test commit's message says plainly that
the suite reports failures until the following fixes land, so a bisecting
reader is not ambushed.

# Architecture rules

- **No dynamic creation of infrastructure modules, ever.** Singleton and
  infrastructure modules (binders, configurators, ...) are declared in NED and
  reached through a module-path parameter (`inet::ModuleRefByPar`, like
  `binderModule`) -- never find-or-create, never `createScheduleInit` on first
  use. A network shared by configs with and without a feature gets a switch
  named like the node switch, so one line enables everything:
  `bool hasD2D = default(false)` + `d2dBinder: D2dBinder if hasD2D`.
  Entities created by events (per-bearer RLC/PDCP entities, MEC app
  instances, session ports) are a different, accepted category.
- **A signal is never a request.** Signals are notifications only. Test for
  every `emit()`: would the emitter, and everything its caller does next,
  behave correctly with ZERO listeners? If not -- a listener leaves a result,
  directly or in some third module, that the emitting side reads after
  `emit()` returns -- it is a call in disguise and is forbidden. Make an
  honest call through an interface instead. A direct call that looks
  architecturally wrong is still better than the disguise: keep it until the
  real restructuring moves it.
- **Configuration is pushed through C++ setters.** Runtime configuration
  reaches a module through an `Enter_Method` setter (`configureDrb()`,
  `setLegSelection()` style) that validates the value at delivery time --
  never `module->par(...).parse(...)` on an already-built module. Needing
  `@mutable` for a config push is the sign the mechanism is wrong. (Setting a
  dynamically created module's OWN parameters before `finalizeParameters()`
  is fine.)
- **RRC state is push-only inside a node.** Consumers (splitter, Ip2Nic,
  packet holder, ...) keep small RRC-pushed mirrors with named variables and
  `Enter_Method` setters; RRC fans out on every change and initializes
  dynamically created consumers at creation. No pull calls into RRC on the
  data path, no `bearerManagementModule`-style refs in consumers.
  Communication between nodes follows the 3GPP interfaces (the gNB RRC
  initiates handover over Xn and N2), not a direction rule.
- **No reading other modules' parameters.** A cross-module `par()` read
  hides a dependency that belongs in the NED wiring. Declare a LOCAL
  parameter and let the enclosing compound set it (explicit assignment or a
  lenient `*.`/`**.` pattern).
- **Module paths are passed down with `absPath`.** The compound keeps the
  path natural to itself and converts it before propagating, so each
  submodule resolves it in its own frame:

  ```ned
  string macModule = default("^.mac");
  *.macModule = default(absPath(this.macModule));
  ```

  Never write submodule-frame paths (`^.^.mac`) on a compound parameter.
  `*.` is lenient: submodules without the parameter are skipped.
- **No boolean arguments that select a mode.** `getStackServingNode(false)`
  says nothing at the call site. Use SEPARATE named functions
  (`setServingNodeId()` / `setNrServingNodeId()`); an enum argument was
  considered and rejected. Likewise two named variables over a 2-element array
  indexed by a bool. Applies to new code; the legacy `bool isNr` arguments
  are cleanup material.
- **Radio medium vs node, as in INET.** The medium models propagation up to
  the antenna -- geometry, path loss, LOS state, shadowing, fading,
  interference -- and computes the SINR. The antenna (gain, pattern,
  orientation) and everything after it belong to the node: noise figure,
  error model (BLER from SINR + MCS), HARQ combining, the reception decision,
  CQI/feedback. The medium returns per-RB SINR/RSRP for a (transmission,
  receiver) pair; it never decides a reception.
- **Which methods are virtual.** Stack classes are meant to be overridable:
  make methods virtual EXCEPT trivial one-line accessors/mutators, value and
  state structs, packet and chunk classes, generated `_m.h` code,
  constructors, and helper classes held BY VALUE (a vptr buys nothing
  there). Prove such a change inert with
  `CFLAGS_EXTRA="-Wsuggest-override -Woverloaded-virtual"` (zero hits before
  and after) and `nm -D --undefined-only <lib> | c++filt | grep simu5g::`
  (must print nothing: a declared-but-undefined member that becomes virtual
  breaks `dlopen` while `make` stays green). Run the same `nm` check after
  any scripted code move: a class whose KEY FUNCTION (first non-inline
  virtual member, often the destructor) lost its definition gives an
  undefined `_ZTV...` vtable symbol -- e.g. a function-map regex like
  `Class::[A-Za-z_]*(` misses `Class::~Class`, and the destructor moves out
  with its neighbors. Include `~` in such regexes.
- **Error handling in emulation.** The base rule -- abort on an invalid state
  or input, never recover and continue -- is in `omnetpp-coding-conventions`.
  It rests on a closed world: every input comes from the experiment
  definition, so an invalid one is a bug. Real packets entering through an
  ext interface (LLDP, IPv6 ND, mDNS from the host) break that premise.
  - Who owns the violated expectation decides: ABORT when it is owned by the
    experiment definition (code, NED, ini, replayed trace files -- a malformed
    pcap still aborts); DISCARD and continue only for input from the
    uncontrolled environment (live traffic).
  - The tolerance lives at the INGRESS BOUNDARY only: the ext-interface seam
    reduces the open world to what the model handles. Interior code keeps
    asserting -- an unknown packet deep in the stack is still a bug (the
    ingress filter let it through). Never spread defensive guards through the
    stack for emulation's sake.
  - The discard is LOUD: an EV line plus a drop counter per reason, else the
    results silently exclude offered load.
  - A strictness switch at the boundary (drop-unknown vs abort-on-unknown) is
    legitimate; strict mode makes the ingress a testbed sanity check.
  - Example: a packet no bearer/QoS flow covers throws, and stays so;
    emulation configs add an explicit catch-all filter row (real UEs have a
    default QoS rule, too).

# Code and NED style

- **Parameter and gate comments are one-liners**: capital first letter
  (unless the first word is an identifier or a proper spelling: `rlcMode`,
  `eNodeB`, `dBm`), no closing full stop on a single-sentence comment
  (multi-sentence prose keeps its punctuation), no ASCII-art noise (`-->`,
  `// --- SECTION --- //`, dangling empty `//`). Examples, shapes and
  rationale go into the module's main doc comment; the parameter gets a
  one-liner such as `// per-leg descriptors (see module comment)`.
  Trap for sweeps: some NED types declare parameters with NO `parameters:`
  label, directly in the module body -- find parameters by brace depth, not
  by the section label.
- **NED doc comments:** a network's doc comment describes its TOPOLOGY only
  (nodes, core network, links); what the simulation does belongs in the ini
  file. A doc comment does not open with the type's own name (neddoc already
  prints it as the heading).
- **Comments describe the current code, never its history.** No
  `// changed to X because ...`, `// was Y`, `// fix for Z`, `// NEW:`. The
  change and its rationale go into the commit message.
- **ASCII-only punctuation** in all source comments (`--`, `->`, `<-`), as
  in `omnetpp-coding-conventions`.
- **`WATCH` runtime state only**: counters, windows, tables, current ids,
  identity learned from the network. Members that merely cache a NED
  parameter (`x_ = par("x")`, never changed) get no WATCH -- the parameter is
  already visible in Qtenv; existing ones may be removed. A member
  initialized from a parameter but modified at runtime is state.
- **Name gates after what they carry** (`userDataIn/userDataOut`); a
  readable, slightly vague name beats a precise 3GPP acronym. No
  `upperLayer*`/`lowerLayer*` where there is no real layer relation.
  Discuss gate and module names with the user BEFORE implementing. Never
  name the gates of a module that is not a network layer `ifIn`/`ifOut`:
  INET's `InterfaceTable` takes any module with those gate names next to a
  NIC for a network layer and calls `getIndex()` on them (throws for scalar
  gates).
- **Node layouts follow INET's node-base grid.** Module rows at y=75/225/375
  (app, transport, network); dispatchers at x=750 (y=150/300/450, cb 600,
  bl 750, li 900); interfaces around y=975. Aux column x=125 in 80-unit
  slots: status 80, mobility 160, interfaceTable 240, clock 320, energy*
  400-560, measurer 640, pcapRecorder 720, environment 800. INET's optional
  slots stay reserved; Simu5G-only aux modules go below 800. Aux modules get
  `is=s`. Keep structural placeholders even when functionally unused (e.g. a
  UE's unconnected link-layer dispatchers): an empty box with its
  dispatchers reads as structure, without them as a layout error. In Qtenv,
  INET's `NodeBase` re-lays out gateless aux modules at INITSTAGE_LAST
  (y in 100-unit steps, in submodule order).
- **Layout groups (`g=`) may be used**: Qtenv supports them, and neddoc is
  built with an OMNeT++ version that does too (the released 6.4 IDE editor
  may still draw group members on top of each other). Moving node aux
  columns to `g=aux` starts in INET, then follows here.
- **Moving modules one level deeper into a compound** -- check before the
  move:
  - `getParentModule()->par(...)` / `->hasPar(...)` / `->getFullName()` now
    hit the compound and silently change meaning (often no error). Grep the
    moved modules for `getParentModule`; fix with local parameters set by
    the enclosing NED, and `getContainingNode()` for the node name.
  - `gate(x)->isConnected()` is always true inside a compound, and
    `isPathOK()` alone is true for an UNCONNECTED gate; the right test is
    `isConnected() && isPathOK()`.
  - Keep the inner submodule order as the nodes had it (initialization
    order). Expect `tplx`/`tilx` to move with `~tNl` and `sz` identical.

# Testing

- **Test with debug builds only** (`make MODE=debug`, `bin/simu5g_dbg`,
  fingerprint runner `-d`). Release builds compile every `ASSERT` out, so a
  scenario can run green in release while violating assertions; they bring
  almost no extra benefit at double the runtime, and CI runs the fingerprint
  suite in both modes anyway. Rebuild debug after every source change and,
  when a run exists to exercise an assertion, check the library is fresh:
  `[ out/clang-debug/src/libsimu5g_dbg.so -nt src/<edited file> ]`.
- **Example simulations must all run to completion.** A configuration that
  must be REJECTED is a module test in `tests/module` (INET-style
  `opp_test`, `make moduletests`) with `%exitcode: 1` and `%contains: stderr`
  of the intended message -- never an example config with an expected-ERROR
  fingerprint row (the fingerprint runner does not check the message).
  Traps: `opp_test -p` needs an absolute program path; `opp_run_dbg` appends
  `_dbg` to `-l` itself; include `../../lib/defaults.ini` at the END of
  `[General]`.
- **A spec oracle is a verbatim transcription of the spec**, regardless of
  what the model does -- including constants that look like sloppy rounding
  (3GPP's `c = 3.0e8`). No accommodation toward the implementation, however
  small. Where the model disagrees, that is the finding: move the affected
  checks into their own `.test` file with `%expected-failure` and a
  `%description` of the deviation, instead of adjusting expected values or
  loosening tolerances.
- **Compiling is enough** for WATCH-only commits and for layout-only
  (display string) changes, see `simu5g-fingerprint-testing` for what counts
  as inert. Write no fingerprint claims ("byte-identical, N/N") into their
  commit messages unless the suite actually ran. During layout sessions, do
  not start the fingerprint suite even for small structural side changes:
  note what needs a fingerprint check, and remind the user instead.
- **The fingerprint suite has ZERO emulation coverage.** Whenever a module
  is renamed or a package moved, grep `emulation/` explicitly -- the suite
  will not tell you.

# Working rules

- **Never write to GitHub** -- no `git push`, release assets, tags, issues,
  PRs, comments or release-note edits -- unless the user asked for it AND you
  have asked "ARE YOU SURE?" twice, in separate turns. Never force-push, not
  even then: report the local and remote hashes and leave it to the user.
  Prepare artifacts locally and say where they are.
- **A question is not a change request.** A question about a design detail
  asks for information: answer it on its merits (facts, trade-offs,
  consequences) and keep the design. If the answer reveals a real problem,
  report it as a finding ("this suggests X; do you want to change it?")
  without switching. Never write "so the plan becomes ...". Keep track of
  which points the user decided and which are your open proposals.
- **Push back on anything questionable**, including the user's own
  suggestions and instructions. Split a suggestion into its parts -- one part
  can be right while another is wrong -- and flag the wrong part before
  acting. Silent wholesale compliance is the failure mode. Hold a position
  until given a reason, in both directions.
- **Verify negative capability claims.** Before saying "X cannot do Y" --
  especially when it decides a design -- check the underlying mechanism
  (OMNeT++ modules and gates can be created at run time, signals propagate to
  ancestors), then search for existing uses of it. A subagent's "not found"
  is unverified until you have checked it yourself.
- **Surface decisions adopted by default.** When a plan or design rests on a
  choice nobody explicitly made, name it and ask, instead of letting it
  become the design silently.
- **Never edit WHATSNEW.md** unless the user asks for an entry -- not in the
  implementing commit, not in a follow-up commit. If a change is
  user-visible, say so in the report and offer draft text in chat.
- **Plans, logbooks, designs and reports** live in the separate repo
  `~/projects/ai-plans` (`executions/`, `designs/`, `plans/`, `reports/`;
  `~/projects/ai-logs` is a symlink to it). Write to absolute paths there: a
  relative `ai-logs/` path creates a stray directory in the Simu5G checkout.
  Commit to ai-plans only when asked.
- **Cite commits by hash AND abbreviated subject**, everywhere -- chat,
  commit bodies, plans, notes: `a6707eb81 ("a UE attaches by requesting an
  RRC connection")`. Branches are rebased often and old hashes stop
  resolving; the subject finds the new commit. Branch tips likewise: the
  branch name plus the tip's subject, not just "@ <hash>".
- **Pushed topic branches of the Simu5G development fork may be rewritten**
  (amended, reordered): nobody else follows them. "Already pushed" is no
  argument against a rewrite, "not pushed yet" no reason for urgency. Check
  push state with git (`git rev-parse <b> origin/<b>`), never from notes. The
  push itself still follows the GitHub rule above.
- **D2D is a legacy research prototype**: keep it working, add no features.
  When a cross-cutting change touches D2D, extend D2D only where that comes
  free or cheap; otherwise skip it, make the limitation explicit, and say
  which D2D parts were skipped.
- **INET changes are on the table.** When a Simu5G design hits an INET
  limitation, propose a general INET fix or extension instead of only
  designing around it. State what Simu5G does without it, and the release
  constraint: Simu5G builds against an INET release, so an INET change is
  usable only after the next INET release or a base move -- sequence the
  Simu5G work so it does not block on that. Record new INET gaps in
  `~/projects/ai-plans/reports/inet-*.md`, in the report whose kind fits.
