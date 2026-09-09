# Writing rules for INET showcase pages

This file is the checklist the style pass (`SKILL.md` §2.3b) applies to every draft before the
user reads it. It is not loaded at authoring time; the author writes from the exemplar page and
the six essentials in `SKILL.md`.

**Adding a rule.** A new lesson enters this file only as a *check*: a pattern to grep for, or a
question to ask of a sentence. The story behind it goes in the commit message, not here. The
anecdotes below predate that rule and are kept until each is reduced to its check.


- Goals should answer "why does this feature exist?" before "what does it do?" — structure as: problem → solution → what we demonstrate
- Separate domain knowledge (the protocol/standard) from tool knowledge (INET configuration) — use an "About X" section for protocol background before The Model, and an "X in INET" subsection inside The Model for module/parameter overview
- Never reference a concept before defining it — follow dependency order (e.g. define "lease" before describing the DORA exchange that grants one)
- Explain the *why* behind each mechanism, not just the *what* (e.g. why Renewing uses unicast but Rebinding uses broadcast)
- When a parameter appears in multiple places, the mechanism must be described the same way, not just the outcome (e.g. don't describe `numReservedAddresses` differently in the module overview vs the results section)
- Abstract models (state machines, protocol layers) need explicit grounding in previously described concrete steps
- For each config/scenario, identify the primary reader question and answer it explicitly in the Results section (e.g. "does the client get the same IP after reboot?")

### Simple technical English

The audience is international, and most of it reads English as a second or third language. Write so that a competent engineer who is tired and not a native speaker gets each sentence on the first pass.

- **One idea per sentence.** Aim under 25 words. If a sentence needs a comma-spliced clause to survive, it is two sentences.
- **Active voice, present tense.** "The switch drops the frame", not "the frame will have been dropped by the switch".
- **Plain verbs.** Use, send, drop, wait, grow, shrink — not utilize, transmit-a-message-to, experience-a-loss-of.
- **No noun stacks.** Three nouns in a row is the limit: "queue length threshold" is fine, "downlink transmission opportunity duration limit" is not — rewrite it with a preposition.
- **One term per concept, fixed at first use.** Never vary a term for elegance. Variety is the enemy of comprehension: if it is a "stream" in section 2, it is not a "flow" in section 5.

### Clarity and precision

- **Qualify ambiguous nouns on first use**: "group" → "multicast group", "entry" → "entry in the router's forwarding table". Every noun needs enough context to be unambiguous at its first appearance.
- **Replace vague qualifiers with concrete consequences**: Don't say "expensive" or "costly" — name the actual effect (e.g. extra header overhead, processing bottleneck, wasted bandwidth).
- **Explain what named protocol messages do**: When introducing a protocol message type, state its action as a verb — "Register message" → "*registers* the source with the RP"; "Join message" → "asks routers to create a forwarding entry."
- **Unaware participants**: When an entity (e.g. the source host) is unaware of the protocol being described, say so explicitly — "the source sends a normal multicast packet — it has no knowledge of PIM."
- **No C++ function/method/type names in user-facing prose.** `recordLease`, `bindLease`, `getLeaseByMac`, `handleStopOperation`, `Ieee80211MgmtSta` — none of these belong. State names, protocol message names, NED parameter names are fine and routinely cited; *implementation symbol names are not.*
- **Implementation flavor leaks even without identifiers.** Phrases like "expiry timer", "stop handler", "lifecycle teardown", "in-memory lease" don't name C++ symbols but still frame the prose around how INET implements the protocol rather than what the protocol does. Heuristic: read the sentence as if INET didn't exist — if it only makes sense inside INET, rephrase. Example: *"the server's expiry timer reclaims the address"* → *"the server reclaims the address once the lease expires."*
- **No implementation-history parentheticals.** "(introduced for RFC 2131 compliance)", "(added in 4.6)" tells the reader nothing actionable and implies the rest is non-compliant or otherwise different. Just describe current behavior.
- **No `§4.4.x`-style RFC section citations inline.** Readers don't go look them up; the surrounding prose carries the meaning. Keep one high-level "RFC NNNN" pointer per protocol if useful; drop section numbers.
- **No ad-hoc "this is current" assertions.** Lines like "all figures still current", "captured with the default seed", "verified for this commit" go stale silently and get believed; a stale assertion is worse than no assertion. The standard `| Verified with INET version: X.Y` boilerplate is an exception — it's a template convention with a defined update protocol (bump on re-verification). Invented current-state lines on top of that don't have a convention behind them; they're just hopes. Per-figure or per-config TODOs go inline at the point of use (e.g. a `.. TODO:` comment next to the figure that needs re-capturing), where a maintainer editing that thing will see them — not in a top-of-file list nobody reads.
- **Do not explain what the audience already knows.** The reader of an INET showcase knows what `omnetpp.ini` is, that it sets module parameters, what `[General]` and `[Config ...]` sections are, that `extends` inherits, and what the `configurator` and `visualizer` modules are for. Explaining any of that is scaffolding the page carries for nobody. The line: explain what is specific to *this* showcase (that the routes come from a configurator XML file, that a tunnel interface has no address), not what is common to every showcase. Watch for this after acting on a reviewer finding — a reviewer briefed as "has never used INET" will ask for exactly this material, and the real audience does not want it.

- **Say the positive thing, not the negation.** "In INET a tunnel is *not* a protocol module" only lands for a reader who expected one; anyone else cannot see the contrast being drawn and learns nothing. Write what it *is*: "a tunnel is a virtual network interface". Same for "unlike most router operating systems, this needs no address" — the comparison is only useful if the reader already knows the other system, and it usually smuggles in an unearned absolute (see below) about what those systems require.

- **Give the introduction the same scrutiny as the body — it needs more.** Vague nouns cluster at the top of a page, because nothing has been defined yet and abstraction is the path of least resistance: *"a network"*, *"every link"*, *"the sender"*, *"that one message"*, *"the whole scheme"*, *"the quiet case"*, *"what the tunnel is for"*. That is exactly where a reader can least afford them, having no context to resolve them against. Go through the Goals section noun by noun and ask what each one refers to; if the answer is not on the page yet, name it.

- **Check every example against the mechanism it is illustrating.** An example that contradicts the failure being described is worse than none. A draft of a Path MTU Discovery black hole offered *"a ping still succeeds"* as the sign that small packets get through — but ping is ICMP, and ICMP is precisely what the firewall in that scenario is discarding. A name lookup and a partially-loaded web page work as examples because they are UDP and TCP.

- **Naming a cause earns you a consequence.** Stating *why* something happens often makes a second, more useful sentence derivable rather than asserted. Once the page said that some networks filter ICMP deliberately while others drop it only under load, *"the fault is hardest to find when the network is busiest"* followed from it. Without the cause that sentence would have been an unsupported claim about the world.

- **Be specific where specificity is free.** "A network can only forward a packet if it has a route" → *an IPv6 router*, *its routing table*. "Each interface is labelled with the address it holds" → *the IPv6 address*. "A tunnel puts one packet inside another" → *an IPv6-in-IPv6 tunnel carries a complete IPv6 datagram as the payload of another*. None of these cost a word worth saving, and each one removes a question.

- **No idioms or phrasal verbs where a plain verb exists.** An idiom is the one part of a sentence a non-native reader cannot look up: "the queue fills up in no time", "the link goes down for good", "throughput takes a hit". Write "the queue fills within 2 ms", "the link stays down", "throughput drops to 2.5 Mbps". Phrasal verbs have the same problem whenever a single verb says it — "set up" is *configure*, "carry out" is *perform*, "put off" is *delay*.

- **No unearned absolutes.** Write "never", "always", "cannot", "no X will ever", "the clearest/simplest/only" **only when the underlying fact is genuinely absolute**. The test is one question: *can you name the exception?* If you can, the sentence has to admit it. Three failing kinds, all of which shipped on a first draft and were caught in review:

  - **Policy written as impossibility.** "IPv6 Unique Local Addresses cannot be in the global routing table" — they stay out because providers filter them by default, and RFC 4193 explicitly permits routing them between co-operating sites. Write "providers filter them at their borders by default".
  - **Convention written as prohibition.** "Routers never look at the inner packet of a tunnel" — nothing stops them, the packet is not encrypted, and deep packet inspection does exactly that. They forward on the outer header because that is all a forwarding decision needs. Write what the router *does*, not what it supposedly may not do.
  - **Superlatives and rankings you would have to defend.** "The clearest example", "that mechanism in its simplest form", "the whole trick", "the premise the whole showcase rests on". These tell the reader how to feel instead of giving them a fact; cut them and the fact usually stands better alone.

  Absolutes that are *correct* and should be kept: protocol rules ("a router may not fragment a packet it is forwarding" — RFC 8200), arithmetic ("the 40-byte outer header always pushes a full-size packet over the limit"), things verified in the code or a run ("a learned path MTU is never raised by an incoming message, only lowered"), and direct quotes of a standard. Precision is the goal, not hedging — do not weaken a true absolute into "usually".

  Watch for the same claim appearing twice at different strengths. A page that asserts an absolute in Goals and correctly qualifies it 200 lines later destroys the reader's trust in both statements.

  **Most absolutes are not the word "never".** They hide in bare plurals and in "every": *"networks discard ICMP traffic"*, *"the network carries **every** small packet and discards **every** large one"*, *"a file transfer stops partway **and never finishes**"*. Each reads as a universal law and each is false as stated. The fix is usually not to hedge but to **quantify**: *"many networks discard ICMP traffic"* says strictly more than *"networks may discard"* — it asserts that it is common, which is the fact the reader needs — while the plain plural *"carries small packets and discards large ones"* is both true and shorter.

  **Correcting one sentence can falsify an absolute somewhere else.** *"The sender never learns"* was defensible until the paragraph above it was corrected to say the loss is intermittent — after which a retransmission might well get through, and the "never" became wrong. Whenever you weaken or qualify a claim, re-read the sentences that depended on the stronger version.

  When a wider-context or aside-shaped remark is worth keeping but is not part of the argument, a `.. note::` is the right home — 17 showcases on master use them. (That is *not* the "Details"/"Fine-print" admonition pattern, which is a separate readability-rework artifact and is not house style.)

### Consistency across the page

- **Never state a claim strongly early and qualify it correctly later.** A page that asserts "no router on the public Internet will ever hold a route for these addresses" in Goals and then explains 200 lines down that it is a matter of policy has now told the reader two different things, and damaged both. Whenever you soften a claim after review, grep the whole page for the other places you made it.

- **Say each thing once.** The commonest duplication comes from editing in passes: a point made in the paragraph that introduces a figure and again in the paragraph after it; the same aside inserted in two sections weeks apart; a sentence you add that repeats the one already following it. After any insertion, re-read the surrounding paragraphs — not just the inserted text.

- **Name a standard once, then call it "the standard".** RFC 4193 four times in one section is noise. This works only while one standard owns the passage: on a page that interleaves several (RFC 8201 for the mechanism, 2473 for tunnels, 4890 for filtering, 8200 for a constant), keep naming them, because "the standard" would not say which.

- **Check the convention on master before inventing one.** Figure captions: 0 of 231 figures on master use them, and the house style says to describe the image in prose before or after it. Code-block `:caption:` options: 0 of 44 pages. A quick `grep -rc` over `showcases/*/*/doc/index.rst` settles these in seconds and outranks a reviewer's suggestion.

### Structure and notation

- **Standard notation gets its own paragraph**: If the protocol has standard notation (e.g. `(S,G)`, `(*,G)` in PIM), define it in a dedicated paragraph *before* first use, not inline mid-sentence.
- **Two-context terms need both contexts stated**: When a term appears in two roles (e.g. `(S,G)` as a forwarding table entry AND as a Join message type), explain both explicitly. Don't assume the reader will infer the second meaning.
- **Label temporary vs. steady-state**: When a mechanism has phases (e.g. bootstrap → normal operation), explicitly label what is temporary and what is the final state. Don't let the reader mistake the bootstrap for the normal mode.
- **Define acronyms, state names, and protocol-message names on first use** unless they're obviously well-known to the showcase's expected audience. ACK is everywhere; NAK isn't. DORA is jargon outside DHCP-aware readers. The bar is *"would I gloss this in a hallway conversation with the target reader?"*. A short parenthetical (`DHCPNAK — "negative acknowledgement"`) usually does it.
- **Avoid forward references by default.** "(explained below)" isn't a substitute for explaining — the reader feels they're missing something even if they're not. Exceptions are fine when the inline gloss carries enough context that the forward pointer is *informational* rather than load-bearing: e.g. *"a server identifier — described under DHCP in INET — that the client uses to direct its REQUEST"* tells you what a server identifier is without making you go look first. If you can't write the term cleanly in place, reorder the doc instead of pointing forward.

### Readability

- **Dense paragraphs → bullet lists**: When a paragraph contains more than two sequential steps or more than three distinct concepts, break it into a bulleted or numbered list.
- **Problem→solution at every level**: Not just in the Goals section — each new mechanism should motivate *why it's needed* before explaining *what it does* (e.g. "receivers don't know the source → that's why we need an RP").
- **State machines and similar reference material aren't narrative.** Dense state-machine prose walkthroughs, ASCII transition diagrams, formal grammar dumps, decision-tree tables — anything that reads like a reference-manual page belongs in the protocol's RFC/textbook (or, if needed, in INET's per-module reference doc). The showcase's job is "watch this specific scenario unfold", not "here is the whole spec." Introduce only the states/transitions/notation the per-config sections actually demonstrate.
- **Bullet-list parameter dumps.** When introducing a module, listing its parameters as a comma-separated, parenthetical-laden paragraph is unscannable. One bullet per parameter, short description per bullet. The cost is a handful of extra lines; the gain is something a reader can actually skim.

### Figures and screenshots

- **Every visible element on a figure should be explainable from the caption or surrounding text** — especially the elements that would prompt "wait, what's that?" from a first-time reader. Sequence charts and canvas screenshots routinely show things that surprise readers but are protocol-correct: 802.11 broadcast echoes, link-layer ACKs, ARP exchanges before any unicast, retransmits that cross each other on the wire, the same packet appearing on multiple axes as it traverses internal modules. Anticipate the question and answer it before the reader asks.

  Corollary: the deciding question is *"is this element relevant to what the figure is showing?"* — not *"can I explain it?"*. If it's not relevant, strip it via axis filter, event filter, or tighter time range; explaining noise costs the reader attention for nothing. If it is relevant, explain it — and don't ship the figure without that explanation.

- **Silence is a feature.** A network node whose lifeline stays empty across the frame of a sequence chart tells the reader "this node is not involved in the path being shown." The Roaming chart in the DHCP showcase uses this: `dhcpServer1`'s empty lifeline below the active path makes it visually obvious that the roam DORA does not touch the old subnet. Use that on purpose.

- **Default to noise removal, not noise tolerance.** When the protocol of interest produces ten arrows and the link-layer / management chatter produces a hundred, the chart's reader can't see the ten. Filter aggressively. The result should be: the reader's eye lands on the protocol arrows immediately, not after a manual subtraction pass.
