# Code quality rules

These rules hold in the `simu5g` repository. The language conventions —
explicit error handling, `cRuntimeError` and `ASSERT`, `check_and_cast` over
`dynamic_cast`, the MSG-file pitfalls, plain-ASCII text — live in the
`omnetpp-coding-conventions` skill and are not restated here.

## Why code degrades

An agent adds freely — an addition is safe and local. It rarely changes
existing code, because a change needs the whole picture. So the public
surface grows, duplicates appear, and every individual diff still passes
review. These rules push back.

## The rules

1. A name says what the thing is, not when it arrived. No `New`, no `2`, no
   `Old`, no `Tmp`, no `Fixed`.
2. Search for an existing function before you write a new one, and widen it
   before you add a sibling. The code reviewer checks this on every diff.
3. A comment never carries history. No "was changed to", no "previously",
   no "now we". What a thing was belongs in `ai-logs/done/`.
4. Every public name is a promise: a new method in a header, a new NED
   parameter, a new module gate, a new signal — each needs a stated reason
   in the commit message.
5. Do not add a parameter that no caller sets.
6. One file, one job. A header declares; a `.cc` defines; a `.ned` describes
   the same module the C++ implements, under the same name.
7. Two code paths that do one thing are one bug waiting. Merge them.
8. Prefer one base-class method behind a flag over a zoo of subclass
   overrides that differ by two lines — the `flatten-virtual-methods`
   procedure of the `omnetpp-model-refactoring` skill is the way there.
9. A module that implements a 3GPP entity is named and shaped after the
   specification. Code that visibly deviates from the standard is flagged,
   never assumed correct.
10. Generated files (`*_m.h`, `*_m.cc`) are never hand-edited.

## Budgets

The steward measures the tree before proposing a budget (line width, function
length, file length). A budget enters this file through gate 7: the steward
proposes with measurements, the human accepts. None is accepted yet.

## When the steward runs

A quality audit runs when a plan moves to `ai-logs/done/`, and reads the
files that plan touched — including the untouched code around them, because
drift hides in what a diff does not show. A sweep that fixes findings is
gate 7.
