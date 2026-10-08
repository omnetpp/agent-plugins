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
  breaks `dlopen` while `make` stays green).

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
