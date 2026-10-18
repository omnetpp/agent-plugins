---
name: dev-commit-messages
description: >
  Commit subject format for any software project: area prefix, change-type
  markers (fix:, refactor:, cosmetics:, cleanup:, docs:, test:,
  chore:/build:/ci:; no marker for intended behavior changes), what each
  marker claims, latent-bug fixes, the Fault/Fix message pattern, and group
  prefixes for commit series. Use when writing or rewording commit messages,
  and when reviewing what commits claim.
---

# Commit messages

```
[<group>: ]<area>: [<marker>: ]<topic>
```

`<area>` is the module or subsystem the commit changes, named as the project
names it (`envir:`, `binder:`, `IPv6:`). Several areas are listed
comma-separated (`mac,phy:`). A commit that touches one KIND of thing across
the whole tree names that kind instead of listing directories
(`NED cosmetics: <topic>`).

## Markers

`fix:`, `refactor:`, `cosmetics:`, `cleanup:`, `docs:`, `test:`, `chore:`
(`test:` = the commit only adds or changes tests or test baselines;
`chore:` = build system, CI, developer tooling or repository housekeeping,
e.g. helper scripts, `.gitignore`, IDE project files, version bumps). For
build-system and CI changes, the more specific `build:` and `ci:` may be used
instead of `chore:`; they make the same claim. Pick the marker by what the
commit actually does, not by which files it touches. Variants such as
`refactoring:`, `fixes:`, `bugfix:`, `rename:` and `feature:` are drift; do
not use them, and do not copy them from older history as precedent.

`chore:`, `build:` and `ci:` are only for changes that cannot change the
software's behavior. A build or dependency change that CAN change it
(compiler or optimization flags, a dependency upgrade) gets no marker.

Every marker is a claim a reviewer can check: `refactor:`, `cosmetics:`,
`cleanup:`, `docs:`, `test:`, `chore:`, `build:` and `ci:` claim that the
behavior does not change; `fix:` claims a correction. NO marker means an
INTENDED change of behavior or interface: a feature, a deliberate behavior
change, a restructuring, a removal, a dependency upgrade. These are the
commits to read carefully, and the candidates for release notes. There is
deliberately no `feature:` marker:
the markers are useful because they are exhaustive, and an optional one would
make both `grep` and the absence of a marker meaningless. To flag an unmarked
commit whose effect matters, end the subject with `(behavior change)` or
`(baseline change: <what moved>)`.

A fix of a LATENT bug (one that no current input or configuration reaches) is
still `fix:`, never `refactor:`. `refactor:` is reserved for changes whose
behavior is identical in EVERY state, reachable or not; "nothing reaches the
difference" does not make a change a refactoring. A preparatory change that
removes a trap for the next commit is a fix, too. Say "latent" and
"regression results unchanged" in the body, in the "Fault: ... Fix: ..." form
below.

So the markers separate the risk classes: `fix:` and unmarked commits are
where behavior (and thus regression baselines) may legitimately change;
`refactor:`, `cosmetics:`, `cleanup:`, `docs:`, `test:`, `chore:`, `build:`
and `ci:` commits must leave the regression results unchanged. They also
make each class of change mechanically greppable when assembling release
notes or auditing what moved between releases.

## Fixes inside larger commits

A fix is normally its OWN commit. When a fix exceptionally rides inside a
larger commit, the body must call out the fault and the fix, including the
literal word "Fix:": "Fault, exposed by ...: <what was wrong and how it
failed>" followed by "Fix: <what changed>". Deliberate exclusions from a
change's scope also belong in the message of the commit that defines the
change, so a reader cannot mistake them for omissions.

## Group prefix

A series of commits serving ONE goal that can be stated in one sentence (a
plan, a feature, a refactoring, a tree-wide sweep) gets a group prefix naming
that goal, so it reads as one block in `git log --oneline`. For a plan
executed on a topic branch, the name is the branch name without `topic/`;
otherwise a short name for the goal. The goal decides membership, not when or
where a commit was made: the tests written for the goal and the `fix:`
commits the work exposed or depends on belong to it; a commit made alongside
it for an unrelated reason does not.

## Older history

Older history of a project may not follow this format. It is not a
counter-example.
