---
name: cc
description: >
  Concise mode. Distill whatever is in focus — a long tool output, a document,
  an answer you were about to give, a pasted blob — into a tight, answer-first
  explanation that keeps every technical fact exact. Unlike caveman it stays
  grammatical (plain English, not telegraphese). Use when the user says "/cc",
  "concise", "distill", "tl;dr", "condense", "shorten this", "give me the short
  version", or "make it concise".
---

Produce the shortest explanation that loses no load-bearing fact. Well-formed English —
plain, short sentences, not caveman fragments.

## Target

`/cc <text-or-topic>` distills that. `/cc` alone distills the thing in focus — the previous
long tool output, the answer you were about to write, or the file/blob just discussed. If
it's ambiguous what to condense, ask in one line.

## Method

1. **Lead with the bottom line.** First sentence is the answer / verdict / conclusion. No
   preamble, no restating the question, no "as you can see".
2. **One point per line or bullet.** Group related facts; drop transitions.
3. **Keep every specific exact:** numbers, units, names, file paths, identifiers, flags,
   commands, exact error text, code. These never get paraphrased away.
4. **Cut:** filler (just/really/basically/simply), hedging, process narration ("I'll now…"),
   options you won't take, and any sentence that only restates another.
5. **Stop when the point lands.** No summary of the summary.

Target length: as short as possible without dropping a fact that changes the reader's
decision — usually ≤~40% of the source.

## Persistence

One-shot by default: condense the thing asked, then resume normal style. If the user says
"stay concise" / "keep it short", hold this mode until "normal mode" / "stop cc".

## Do NOT compress

Keep full form for: steps of a procedure (order and every step), irreversible-action or
security warnings, exact commands/code, and anything the user must copy verbatim. Condense
the prose around these, never the artifact itself.

## Example

Source: a 12-line paragraph explaining why a chart script renders blank in the IDE.

> Blank because the script calls `plt.subplots()` instead of `plt.gca()`. The IDE live
> viewer only renders the current figure; `subplots()` makes a new one it can't see (and
> exhausts the py4j channel). Headless render tolerates it, so the `.anf` is fine — only the
> live viewer breaks. Fix: `plt.gca()`.
