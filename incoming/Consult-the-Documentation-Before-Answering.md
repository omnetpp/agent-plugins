
---
type: concept
created: 2026-07-15
updated: 2026-07-15
tags: [agent-behavior, documentation, anti-inference, methodology, ground-truth]
---

# Consult the Documentation Before Answering

When a user asks a technical question about a library, framework, protocol,
tool, API, or any system with authoritative documentation, **always consult
the documentation first.** Never answer from "circumstantial evidence"
(inference from naming patterns, prior memory, contextual clues) when
documentation is available.

## The rule

Documentation is ground truth for factual questions about external systems,
the same way running code is ground truth for claims about your own work.
If there is a doc, you read it before you answer. Not your second move —
your first.

## The anti-pattern: circumstantial evidence

Answering from any of these is a guess, not knowledge:

- **Naming inference:** "It's named `proxyArpInterfaces`, so it probably
  controls which interfaces do proxy ARP." (Read the NED to confirm
  semantics, defaults, wildcard syntax.)
- **Prior-memory inference:** "I remember that `Ipv4NetworkConfigurator`
  uses CIDR in `destination`." (Wrong — it uses `L3AddressResolver` syntax.
  Memory is stale and approximate.)
- **Contextual inference:** "Other examples use `Eth100M`, so this probably
  does too." (Check what's actually available.)
- **Pattern-matching:** "This looks like a standard TCP socket API, so
  `connect()` probably blocks." (Read the framework's own docs.)

Each is a guess. A guess that happens to be right teaches the wrong habit.
A guess that is wrong, acted upon, and discovered later destroys trust.

## The documentation hierarchy

Consult sources in this order. Stop at the first that authoritatively
answers the question:

1. **Local project docs** — NED files, headers, source, `.md` files,
   `doc/` directories, INI comments. The most accurate doc for *this
   version* is right there.
2. **Knowledge base (opp_brain)** — team-curated knowledge.
3. **Official web docs** — `webfetch` the official manual / API reference
   / RFC / man page.
4. **Source code** — NED for parameters, `.h`/`.cc` for C++ behavior,
   `.msg` for message fields. The code *is* the spec.
5. **Only then: inference, clearly labeled.** "I could not find this in
   the documentation. Based on [X], I infer [Y], but this is unverified."

## The confidence ladder for factual questions

> I vaguely recall ▸ I infer from naming ▸ I read a secondary source ▸ I
> read the official documentation ▸ I read the source code ▸ I ran it and
> observed the behavior

You may only report the rung you actually reached. "I vaguely recall" is
rung zero. Do not present it as knowledge.

## How to cite

When answering from docs, say where you got it:

- "According to `Arp.ned` (line 42), `retryCount` defaults to 3."
- "RFC 826 §4.2 specifies that..."
- "The `opp_run -h config` output shows..."

When answering from inference (no doc found), label it:

- "I could not find this in the docs. Based on the source at `Arp.cc:204`,
  this is my reading of the code, not a documented behavior."

## Relationship to the ground-truth method

The ground-truth skill (§3) says *"Read the actual thing; do not reason about
what it probably says"* — focused on reading source code, error messages, and
logs for claims about your own work. This concept extends that principle to
**external documentation**: when the question is about a system's documented
behavior, the documentation *is* the reality you must touch.

The ground-truth ladder runs from "it plausibly should work" to "I read the
source and confirmed it." This adds a parallel ladder for factual questions
about external systems, with documentation as the primary rung.

## The concrete case

An agent was asked a technical question and answered from "circumstantial
evidence" — inference from context — rather than consulting the available
documentation. The answer was plausible, detailed, and wrong. The user caught
it. This is the same failure mode as the ground-truth "plausible-answer
reflex" (§7), but applied to factual questions about external systems rather
than claims about one's own code. The antidote is the same: touch reality
directly. For factual questions about documented systems, the documentation
*is* the reality.

Source: implemented as the `consult-the-docs` skill (`~/.claude/skills/consult-the-docs/SKILL.md`).
