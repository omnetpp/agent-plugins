# Review brief: <branch or PR title>

<!--
Format rules for the whole brief:
- No tables. Markdown tables are unreadable in the source, which is where
  the brief is read. Use bullet lists instead: one bullet per item, a
  paragraph that starts with a few words in bold (the title or topic),
  then the facts, the evidence and the commit.
- Keep each bullet self-contained: what changed, before -> after,
  `file:line`, commit (hash + subject), and V (verified) or I (inferred).
- Nested bullets only for a list inside an item (e.g. several affected
  subtypes); never more than two levels.
-->

- **Range**: base `<hash>` ("<subject>") .. tip `<hash>` ("<subject>"), <N> commits
- **Stated goal**: <one sentence, from the PR description / plan / group prefix>
- **Weight**: <dirstat in one line, e.g. "60% src/stack/rrc, 25% NED, 15% tests">
- **Written**: <date>, from the tip above; re-check if the branch was rebased
- **Method**: <script run or NED read by hand; C++ read in full or by
  subsystem; V = verified, I = inferred>

## TL;DR

<5-10 numbered items, ranked by blast radius (see SKILL.md step 7). Each
item starts with the section letter and a bold title, then one or two
sentences.>

1. [A] **Breaks configs silently.** `<old>` is now `<new>`; ini lines with
   the old name match nothing, and nothing reports it.
2. [A] **Silent result change.** The default of `<Type>.<param>` changed
   from `<old>` to `<new>`.
3. [B] **Duty dropped.** `<Module>` no longer does `<duty>`; no new owner
   found.
4. [D] **Mechanism change.** `<A>` -> `<B>` was a method call, is now
   signal `<name>` (rule conflict, see D).

## A. External interface (NED)

### Breaks existing configurations

- **<What, e.g. "UE parameter rename">.** `<old>` is now `<new>`.
  <Confirmed / candidate, and by what: ini lines migrated, guard, commit
  message.> `<file:line>`; `<hash>` ("<subject>"). V

### Silently changes results

- **<What>.** <before -> after, and why it is silent.> `<file:line>`;
  `<hash>` ("<subject>"). V/I

### Additive

- **<What>.** <one line each>

### Migration

- `<old ini key / NED name>` -> `<new>`
- ...

### Meaning changed without a declaration change

- **<Name>.** <what it meant before, what it means now; evidence>. V/I

### Secondary surfaces

- **C++ API for extenders.** <removed/renamed virtuals, members>
- **Names built in C++.** <run-time module names, signal names, lookups>

## B. Responsibilities

- **<Module>: <transferred to Y / gained / dropped / split / merged>.**
  <The duty.> Before: <...>. After: <...>. `<file:line>`; `<hash>`
  ("<subject>"). V/I
- **Accumulation.** <modules that gained a duty from another layer, plane
  or domain; or "none found">
- **Internal restructuring, duties unchanged.** <one line listing modules>

## C. Key data structures

- **<Structure> (<why key>).** <The change.> Writers: <before -> after>.
  Readers: <before -> after>. `<file:line>`; `<hash>` ("<subject>"). V/I
- **Cardinality and key changes.** <highlight separately, even if listed
  above; or "none found" and how searched>

## D. Communication between modules

- **<A> -> <B>: <old mechanism> -> <new mechanism>.** <What flows.>
  `<file:line>`; `<hash>` ("<subject>"). V/I

### Rule conflicts

- **<Rule> (<skill name>).** <The edge and the evidence.> Or: "None
  found", followed by what was checked.

## E. Other facts

- **Claims vs reality.** <...>
- **Behavior evidence.** <baselines re-recorded: which, where, stated why>
- **Tests.** <...>
- **Examples and configs.** <...>
- **Documentation.** <...>
- **Unchecked areas.** <...>

## Questions for the reviewer

1. **<Topic>.** <The question, with the facts it rests on.>

## Coverage and method

- **NED.** <read N files by hand / script run with --external ...; blind
  spots>
- **C++.** <which modules or diffs were read; greps used>
- **Subagents.** <which sections, which spot-checks>
- **Not examined.** <...>
