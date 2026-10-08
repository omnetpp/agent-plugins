---
name: simu5g-dev
description: Rules for working with Simu5G, incl. which INET/OMNeT++ skills apply and the commit-subject format (change-type markers)
---

# Using INET and OMNeT++ skills

Simu5G is an INET-based project which follows the same architecture and conventions
as INET, so INET-related skills are highly relevant! Make use of INET-related skills
(unless overridden by Simu5G-specific rules). 

Simu5G and INET are written for OMNeT++, so OMNeT++ skills related to model development
are relevant, too. However, ignore skills that are about developing OMNeT++ **itself**.

# Commit subject format

Commit subjects carry a change-type marker after the module/subsystem prefix:

```
<module/subsystem>: <type>: <topic>
```

e.g. `binder: fix: out-of-bounds read in getServingNode()`. Multi-subsystem
commits list the modules comma-separated (`mac,phy: ...`).

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
