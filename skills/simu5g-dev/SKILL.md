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
and check it, because the same flag can mean something different (e.g.
fingerprint `-m`: a regex in INET, a substring in Simu5G):

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
commits list the modules comma-separated (`mac,phy: ...`).

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
