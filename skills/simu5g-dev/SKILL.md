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

Markers in use: `fix:`, `refactor:`, `cosmetics:`, `cleanup:`, `docs:`.
Features get NO marker -- they keep the plain `<module>: <topic>` form.
Pick the marker by what the commit actually does, not by which files it
touches.

A fix of a LATENT bug -- one that no current configuration reaches -- is still
`fix:`, never `refactor:`. `refactor:` is reserved for changes whose behavior
is identical in EVERY state, reachable or not; "no config reaches the
difference" does not make a change a refactoring. A preparatory change that
removes a trap for the next commit is a fix, too. Write "latent" and
"fingerprint-inert" in the body, in the "Fault: ... Fix: ..." form below.

The markers separate the risk classes: a `fix:` commit is where behavior
(and thus fingerprints) may legitimately change; `refactor:`, `cosmetics:`,
`cleanup:` and `docs:` commits are expected to be fingerprint-inert. The
markers also make each class of change mechanically greppable when
assembling release notes or auditing what moved between releases.

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
