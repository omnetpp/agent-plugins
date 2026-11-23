# WHATSNEW.md entry — annotated skeleton & style guide

This file documents the structure, ordering, and house style of an INET `WHATSNEW.md`
release entry, distilled from the existing entries. When in doubt, open the most recent
real entry in `WHATSNEW.md` and copy its shape.

## Annotated skeleton

```
INET-X.Y (Month Year) — feature release       ← title; release type: "feature release",
-----------------------------------------          or historically "Stable" / "Development".
                                                   Underline = hyphens, same visible length
                                                   as the title (the em-dash counts as 1).

<Intro paragraph.> One paragraph. Opens "This is a new feature release in the INET 4.x
branch." Names the 3–6 biggest highlights in a sentence or two ("Highlights include new
protocol implementations for …, major refinements to …, and …"). States the ongoing focus
("improving correctness, accuracy, modularity, and long-term maintainability"). Ends with
"Requires OMNeT++ X.Y or later."

For the full list of additions, removals, and changes (features, modules, packet
chunks/tags, signals, statistics, and C++ classes), see ChangeLog in the src
folder.

<Optional extra pointers, e.g. a line about the AI wiki / deepwiki, if applicable.>

Notable backward-incompatible changes include the following:

1. <Short title — a noun phrase, e.g. "Clock model refinement">

   <1–4 paragraphs of narrative.>

   <Closing impact statement — REQUIRED for every backward-incompatible item. One of:
    "This change requires the modification of simulation models that …", or
    "This change doesn't require the modification of simulation models, but it may
    significantly change the statistical results of simulations that …", or
    "These changes are backward incompatible for simulations that explicitly …">

2. <…>

Notable backward compatible changes are the following:

1. <Short title>

   <1–3 paragraphs.>

   <Optional: "The <X> protocol implementation was contributed by <Name>." — for
    externally contributed protocols/models only.>

…

N. Notable bug fixes and other changes        ← ALWAYS the last item of this bucket.

   <A series of short, standalone paragraphs — one per fix or minor change. Each is a
    self-contained statement ("Fixed …", "Added …", "Removed …", "Improved …").>

   Several additional issues reported on GitHub have also been fixed.
```

Separate the new entry from the one below it with a blank line (entries in the file are
separated by one or two blank lines).

## Ordering rules

**Two buckets, in this order:** backward-incompatible first, then backward-compatible.

Inside **backward-incompatible**: lead with the changes most likely to surprise an existing
user — model/semantic reworks that change results (clock, gPTP), then renames and removed
defaults, then refactorings.

Inside **backward-compatible**, roughly:
1. Major new protocols / models (e.g. 10BASE-T1S, QUIC, IPsec, MRP).
2. Extensions to existing protocols/features (e.g. TCP auto-read, AODV gateway, GPSR).
3. Cross-cutting infrastructure (queueing model, protocol support, visualizers, serializers).
4. Tutorials.
5. New showcases.
6. Documentation refinements.
7. **Notable bug fixes and other changes** — always last.

Use a single "Notable bug fixes and other changes" item to absorb everything too small to
deserve its own numbered entry.

## House style

- **Baseline against the previous release (SKILL.md's #1 rule).** Describe only how the code
  differs from the previous release tag — never present an intra-cycle add-then-refine as a
  change, and never mention an add-then-remove at all.
- **Tone:** neutral, professional, technical. No marketing language, no superlatives, no
  hype. (The INET docs were deliberately revised toward "neutral, professional language" —
  match that.)
- **Voice/tense:** past tense and present-perfect passive — "was added", "has been
  extended", "were renamed", "now uses". Describe the end state and its effect.
- **One theme per item.** Synthesize many commits into one coherent story; explain what
  changed and why it matters to a user. Do not list commits or PR numbers.
- **Identifiers verbatim, as plain text.** Module, class, parameter, and signal names are
  written exactly (EthernetMacPhy, autoRead, fcsMode, packetLifeTime) with NO backticks or
  markdown — this file is plain text with setext headers, not Markdown rendering.
- **Backward-incompatible items must state the impact** on existing simulations: either
  models must be edited, or they need not be edited but statistical results may change.
- **Attribute external contributions** with a closing "… was contributed by <Name>." line.
  Confirm names with the user; derive candidates from git authorship and commit-body
  "contributed by" mentions.
- **Line width:** hard-wrap at ~78 columns (80 max). Numbered titles flush-left ("1. Title");
  body text indented 3 spaces. Bare URLs are fine; no markdown links.
- **No time-bound promises** ("coming soon"); describe what this release contains.

## Worked micro-example (one backward-incompatible item)

```
3. Ethernet module renames

   Existing Ethernet MAC modules were renamed to use the MacPhy suffix (e.g.
   EthernetMacPhy, EthernetCsmaMacPhy) to reflect that they combine MAC and PHY
   functionality in a single module. This resolves naming conflicts introduced
   by the new dedicated EthernetCsmaMac and EthernetCsmaPhy modules, which
   provide a modern, state-machine-based implementation of the individual layers
   and are primarily used by the new Ethernet 10BASE-T1S model.

   These changes are backward incompatible for simulations that directly
   reference the old module names.
```

Note the shape: title → what changed and why → who/what it affects → explicit
backward-incompatibility statement to close.
