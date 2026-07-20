---
name: generic-protocol-test-authoring
description: Writing Protocol Conformance Test Plans — Briefing for an External Planner
---

# Writing Protocol Conformance Test Plans — Briefing for an External Planner

You are given a protocol specification (an RFC or equivalent standard). Your job is to
produce a **conformance test plan**: a list of focused test cases, each written in
**structured English** against a fixed template, that an engineer can translate
**one-to-one** into an executable test.

You do **not** know the simulator or its codebase, and you never write code. You reason
from the specification about *observable behavior*, and you express each expectation in the
vocabulary this document defines. An engineer (the "grounder") who does know the
implementation converts each of your cases mechanically into a runnable test.

**The contract:** if a case fills every field of the template unambiguously, the grounder
can translate it without guessing. *Detail and fidelity to the spec are your job; syntax is
theirs.* Refer to every message and every field **exactly as the specification names them**
— the grounder maps those names onto the implementation.

---

## 1. How the system observes a running protocol (the mental model)

The protocol runs in a small simulated network of **nodes** connected by **links**. A silent
observer watches the entire run as an ordered **timeline of events** and checks your
expectations against it, in order, each within a time deadline.

Exactly two things are observable:

- **(a) Frames on the wire.** Every packet a node **transmits** or **receives** at its
  network interface. This is the **primary, preferred** evidence: it is precisely what
  really crossed the link, with *all* layers present at once (link + network + transport +
  payload), and every field is readable in either direction.
- **(b) A node's internal protocol state.** An FSM state, a cache entry, a counter, a flag —
  observed directly (the grounder can reach it). Use this when the behavior does **not** show
  up on the wire, or as corroboration.

**Prefer (a).** On-wire behavior is implementation-independent evidence — it is what the
standard actually constrains. Reach into internal state only when a requirement has no packet
manifestation (e.g. a state transition that emits nothing), or to corroborate.

The **direction vocabulary is just two verbs**: at its interface a node **transmits** a frame
or **receives** a frame. That is the whole of it.

**Time is relative.** Each expectation is bounded by *when* it must be satisfied relative to
the previous one (a deadline: "within …", or "not before …"). You give timing
**qualitatively** ("within a few seconds", "after the retransmission timeout"); the engineer
tunes the exact numbers.

---

## 2. The observability boundary (what you may and may not assert)

**Every expectation must be one of exactly two shapes:**

1. *"Node N, at its interface, **transmits / receives** a frame such that <field conditions>."*
2. *"Node N's **internal state** <reaches / equals / contains> <value>."*

You may qualify either with a **count** (how many times), an **order**, a **timing deadline**,
and **correlations** to values seen earlier.

**You may NOT** assert anything with no observable manifestation — *"the node parsed the option
correctly"*, *"the checksum was verified"*, *"the algorithm ran"* — unless it surfaces as a
later frame or an internal-state fact. Re-express such requirements as their **observable
consequence**. For example, "the node MUST process option X" is only testable through the
*response* it produces or the *state* it leaves.

**Golden rule:** if you cannot phrase an expectation as a frame at an interface or an
internal-state fact, it is not testable here. Do not invent an assertion — record it as a
**coverage gap** in the case's NOTES instead.

---

## 3. The assertion vocabulary (the primitives you compose)

Every case is built from these primitives. Phrase them in spec terms; the grounder maps each
onto the engine.

| Primitive | Meaning | Typical spec phrasing it captures |
|---|---|---|
| **must happen (once)** | one matching event is required | "the node MUST send an X" |
| **exactly N times** | precisely N matching events | "MUST send exactly three retransmissions" |
| **at least N / at most N** | a bounded count | "MUST send at least one"; "no more than N" |
| **must NOT happen** (within a window) | a matching event fails the case | "MUST NOT send X after Y"; "MUST NOT forward" |
| **within / after a deadline** | timing relative to the previous step | "within RETRANS_TIMER"; "not before the DAD delay" |
| **correlation (capture & reuse)** | a field value from an earlier frame must reappear in a later one | "the Reply MUST echo the Request's Identifier"; "the ACK number MUST be the sequence number + 1" |
| **any-order group** | a set of frames, all required, in any order | "the node MUST send both a HoTI and a CoTI (order unspecified)" |
| **one of several alternatives** | the first of N acceptable frames satisfies the step | "the node MAY answer with either A or B" |
| **end-to-end delivery** | a frame transmitted by one node is received *as the same packet* by another | "the datagram MUST be delivered to the destination" |
| **inject a crafted frame** | the test itself sends a hand-built frame as stimulus (you can *play a peer* that the real node responds to) | "on receipt of a valid X, the node MUST reply with Y" — when no real peer sends X |
| **fault: drop / delay / corrupt** | a selected in-flight frame is dropped, held, or corrupted | "if the response is lost, the client MUST retransmit"; "a corrupted frame MUST be discarded" |

Notes:
- A **correlation** is how you test "echoes", "matching identifiers", "sequence + 1", "same
  token", etc. Name the value in the earlier step and reference it (`{name}`) in the later one.
- **Inject** and **fault** turn a passive check into an active probe. Use *inject* to supply a
  stimulus the network wouldn't otherwise produce (be the correspondent, be the attacker,
  be the lost-and-retrying peer). Use *fault* to create the loss/corruption/delay a
  requirement is written against.

---

## 4. Constructing scenarios (eliciting the behavior)

A behavior only appears if the scenario **forces** it. Designing the minimal situation that
triggers the requirement is part of each case. Reason from the spec:

- to observe a **redirect**, the destination must be reachable via a *better next hop on the
  same link*;
- to observe **fragmentation**, a datagram must exceed the *link MTU*;
- to observe a **duplicate-address defense**, *two nodes must claim the same address*;
- to observe a **retransmission**, the response must be **lost** (a fault injection);
- to observe a **response to message X**, and no node naturally sends X, **inject** X.

**Reuse vs. design.** If the protocol already has a standard test network, say *"reuse <that
network>"* and only add the per-case stimulus/knobs. If it does not (a new or not-yet-modeled
protocol), **design the minimal topology**: list the nodes and their roles, the links between
them, and the few key parameters (addresses, MTU, timers) that matter. **Keep topologies as
small as the requirement allows** — two nodes on one link is the common case; add a router or
a second link only when the behavior needs it.

---

## 5. Verdict stance (do not predict the implementation)

Always write each expectation as the **standard** requires. **Never** soften an assertion to
match what you guess the implementation does — you don't know, and guessing corrupts the
suite. If the implementation happens to lack the feature, the engineer records the case as a
**known/expected gap** when running it; your assertion stays faithful to the standard. *A test
that fails because the implementation is incomplete is a finding, not a plan error.*

Cover **Required** behaviors first; include **Optional** ones too, each tagged `Optional`.

---

## 6. Granularity — one behavior per case

Split compound requirements into **focused, single-purpose cases**. "The RA carries a prefix
option" and "the RA's managed/other-config flags are clear under stateless configuration" are
**two** cases, not one. Small cases translate cleanly, localize failures, and read as a
conformance matrix. A case that asserts five unrelated things is a smell — split it.

---

## 7. The test-case template

A case is a short header plus an ordered `EXPECT` list. **Write only what deviates from the
defaults** — a normal step is a plain one-line sentence.

**Defaults, so you can leave them unwritten:** each step **must happen once**, **at the acting
node's interface** (transmit or receive, per the verb), **in sequence** after the previous
step, within a sensible window the engineer picks. Annotate a step only when it *breaks* one
of these.

```
ID:          short_snake_name
TITLE:       one line
SPEC:        <Standard> §<section> · Required | Optional
REQUIREMENT: the MUST / SHOULD / MAY sentence, ~verbatim (for traceability)
SCENARIO:    reuse <network>   OR   new: <nodes & roles; links; key parameters>
STIMULUS:    what triggers the behavior (a node boots | an app sends traffic | a link/timer event)
FAULT:       drop | delay | corrupt <frame>, or inject <crafted message>, and when   (only if used)
EXPECT:
   1. <node> transmits <message> [with <field conditions>].       [capture <field>→{name}]
   2. <node> receives <message> with <conditions, may use {name}>.
   ...
NOTES:       grounding hints or recorded coverage gaps   (only if needed)
```

**Qualifiers — add to a step only when it breaks a default:**

| Add to the step … | when the spec says … |
|---|---|
| `must NEVER …` / `exactly N …` / `at least N …` / `at most N …` | anything other than "once" |
| `in any order:` a; b; c | a set of frames whose order is unspecified |
| `one of:` a; b | either of several acceptable frames |
| a deadline — "within <t>", "after <t>", "not before <t>" | timing the standard actually pins |
| `internal state:` <node>'s <fact> | the behavior is a state change, not a frame (§2) |

Every field maps one-to-one to the executable test: **ID/TITLE** name it; **SPEC/REQUIREMENT**
become its description and matrix row; **SCENARIO** picks or builds the network; **STIMULUS**
becomes traffic (or an injected frame); each **EXPECT** step becomes one ordered check; an
inline **capture** becomes a correlation binding; **FAULT** becomes an interception/injection.
The verdict is always "the spec behavior occurs", so you never state it (see §5).

---

## 8. Worked example A — an existing behavior (round-trip reference)

*Requirement:* an ICMPv6 Echo Reply must return the Identifier and Sequence Number of the
Echo Request that prompted it, so the sender can correlate replies to requests.

```
ID:          icmpv6_echo_identifier_echo
TITLE:       Echo Reply echoes the Request's Identifier and Sequence Number
SPEC:        RFC 4443 §4.2 · Required
REQUIREMENT: "The Identifier and Sequence Number ... are returned unchanged in the Echo Reply."
SCENARIO:    reuse a one-link network with two hosts (host A, host B) on the same subnet.
STIMULUS:    host A pings host B (Echo Requests, once a second for a few seconds).
EXPECT:
   1. host A transmits an Echo Request.     [capture Identifier→{id}, Sequence Number→{seq}]
   2. host A receives an Echo Reply with Identifier={id} and Sequence Number={seq}.
```

*Reference only — you never write this; it is what the engineer produces from the case above,
shown so you can calibrate how much detail a translatable case needs:*

```
.once(on("host1.eth[0].mac").signal("packetSentToLower")
          .packet("Icmpv6EchoRequestMsg.code == 0")
          .capture("id", "Icmpv6EchoRequestMsg.identifier")
          .capture("seq", "Icmpv6EchoRequestMsg.seqNumber").within(6.0))
.once(on("host1.eth[0].mac").signal("packetReceivedFromLower")
          .packet("Icmpv6EchoReplyMsg.identifier == {id} && Icmpv6EchoReplyMsg.seqNumber == {seq}")
          .within(2.0));
```

Notice: your two ordered steps became two ordered checks; "host A transmits / receives" became
the interface observation points; the capture/reuse became the `{id}`/`{seq}` binding; the
implicit "once" and the engineer's chosen window filled the rest. Nothing was left to a guess.

---

## 9. Worked example B — a new protocol needing a new scenario and a fault

*Requirement (a hypothetical reliable request/response protocol "FooProto"):* "If the client
does not receive a Response within the retransmission timeout, it MUST retransmit the Request
with the same Request-ID. Once a matching Response is received, the client MUST NOT retransmit."

This behavior can only be elicited by **losing** the first Response — so the case designs a
minimal two-node network and injects a **drop** fault. It also shows a **negative** assertion.

```
ID:          fooproto_retransmit_on_lost_response
TITLE:       Client retransmits its Request when the Response is lost, and stops once answered
SPEC:        FooProto spec §5.3 · Required
REQUIREMENT: "If the client does not receive a Response within the retransmission timeout it
             MUST retransmit the Request with the same Request-ID. Once a matching Response is
             received, the client MUST NOT retransmit."
SCENARIO:    new — client node and server node on one link (client + server roles);
             retransmission timeout set to a small, known value.
STIMULUS:    the client sends a Request to the server at the start of the run.
FAULT:       drop the first Response the server transmits (so the client's timer fires).
EXPECT:
   1. client transmits a Request.                                   [capture Request-ID→{rid}]
   2. client transmits a Request with Request-ID={rid} (the same Request, retransmitted),
      after the retransmission timeout.
   3. client receives a Response with Request-ID={rid}.
   4. client must NEVER transmit a Request with Request-ID={rid}, for at least one
      retransmission interval after step 3.
NOTES:       step 4 is the negative half of the MUST NOT — its window must span at least one
             retransmission interval so a wrongful retransmit is caught.
```

This one case exercises new-topology design, a stimulus, a fault, a correlation, a positive
sequence, and a negative bound — the full vocabulary, all in structured English.

---

## 10. Checklist before you emit a case

- [ ] Every expectation is a **frame at an interface** or an **internal-state fact** (§2).
- [ ] Messages and fields are named **exactly as the specification names them**.
- [ ] The **scenario forces** the behavior; topology is **minimal**; reuse noted where possible.
- [ ] Any step that isn't "once" (**never** / exactly-N / at-least / at-most) is **marked** as such.
- [ ] **Correlations** (echoed / matching / +1 values) are named as captures and reused.
- [ ] **Timing** is given qualitatively where it matters.
- [ ] **Verdict** is faithful to the spec; **Optional** behaviors are tagged.
- [ ] **One behavior per case**; compound requirements are split.
- [ ] Anything the standard requires but that has **no observable manifestation** is recorded
      as a coverage gap in NOTES, not turned into a fabricated assertion.

Produce the plan as an ordered list of cases in the §7 template, grouped by spec area, with a
short header per group naming the standard and section range it covers.
