# Review brief: <branch or PR title>

<!--
Density rules (SKILL.md): each fact once; no empty sections; verified is the
default, mark only exceptions; do not restate commit messages; one finding per
bullet with a bold sentence title and only what the title does not say;
at most one "Ask:" and about 80 words per finding; commits as hash +
abbreviated subject; questions inside their finding; no tables; lines
wrapped at ~80 columns; about one screen, under ~150 lines. Delete every
comment and every optional section that would be empty.
-->

- **Range**: base `<hash>` ("<abbrev. subject>"), tip `<hash>` ("<abbrev.
  subject>"), <N> commits; <push state, e.g. "tip equals origin/<b>">.
- **Goal**: <one sentence, with its source>.
- **Weight**: <one or two sentences: where the lines are, by kind -- model,
  refactoring, tests, configs, baselines>.
- **Verification**: <what was run on the tip and on which commits, and what
  was not; source: logbook / CI / commit messages>.

## Commits by goal

<!-- One line per goal: the goal as a phrase, then its commits as a range;
single hashes only for one or two commits or a non-contiguous group. -->

- <Goal>, <n> commits: `<first>` ("<abbrev>") to `<last>` ("<abbrev>").
- <Goal>: `<hash>` ("<abbrev>").

## Decide before merge

1. **<Finding as a short sentence.>** <What the title does not say: before,
   who is affected, why it matters.> `<file:line>`, `<hash>` ("<abbrev>").
   Ask: <question, if the finding raises one>.

## Check closely

1. **<Finding.>** <...>

## Cheap fixes

- **<Finding.>** <...>

## Minor

- <One line each.>

## Migration

<!-- Only if something breaks users. One imperative line each. -->

- Replace `<old>` with `<new>`.

## Checked, nothing found

<One paragraph, comma-separated: e.g. "NED meaning changes (doc comments
diffed), names built in C++ (literal grep), key/cardinality changes, new
communication edges, red-line conflicts (signals, cross-module par(), parse(),
gates on RRC), emulation/ (untouched).">

## Method

<At most three lines: what was run and read; what was not examined;
subagents and spot-checks.>
