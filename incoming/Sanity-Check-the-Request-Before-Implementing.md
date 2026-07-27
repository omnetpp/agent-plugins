
---
type: concept
created: 2026-07-15
updated: 2026-07-15
tags: [agent-behavior, clarification, push-back, sanity-check, methodology, gotcha]
---

# Sanity-Check the Request Before Implementing

A discipline for AI agents (and human engineers): **before you start building,
verify that the request itself makes sense.** If it doesn't, push back gently,
find out what the user actually meant, and work *with* them toward a better
result. Blindly implementing a conceptually confused request produces work
that is technically "done" but wrong — and wastes everyone's time.

## The principle

A request is a pointer to a goal, not the goal itself (this is also stated in
the ground-truth method, §1). But there is a checkpoint *before* decomposing
the request: **does the request's literal content even make sense in the
domain?** If the user asks for something that conflates two different concepts,
the right move is not to pick the closest valid interpretation and proceed
silently — it is to surface the mismatch and clarify.

This is not about questioning the user's authority. The user knows their goal.
It is about catching slips of the tongue, terminology mix-ups, and conceptual
conflations that, if implemented literally, would produce a result nobody
wanted.

## The concrete case: "ARP routing protocol"

In this project, the user asked to "create a demo simulation that shows how
the ARP routing protocol works." **ARP is not a routing protocol.** ARP is an
address resolution protocol — it maps IP addresses to MAC addresses on a local
link. It does not compute routes, maintain routing tables, or make forwarding
decisions. Routing protocols are OSPF, RIP, BGP, AODV, EIGRP, etc.

The agent should have recognised this immediately and responded with something
like:

> Quick sanity check before I start: ARP (Address Resolution Protocol) isn't
> a routing protocol — it resolves IP addresses to MAC addresses on a local
> link. Did you mean:
>
> a) A demo of **ARP** (address resolution) — how hosts learn each other's
>    MAC addresses? This is what I can build with the current topology.
> b) A demo of a **routing protocol** like OSPF, AODV, or RIP — how routers
>    build and maintain routing tables?
>
> If you meant (a), I'll proceed. If you meant (b), tell me which protocol
> and I'll design the topology around it.

Instead, the agent silently built an ARP demo (the closest valid interpretation)
without ever flagging the mismatch. The result was technically correct — ARP
was demonstrated — but the user's actual intent was never confirmed, and a
routing-protocol demo (which might have been what they wanted) was never
offered.

## Why this matters

- **Slips of the tongue are common.** People say "ARP routing" the way they
  say "DNS routing" — a mental shortcut that conflates a network protocol
  with routing. The expert's job is to catch this, not exploit it.
- **Silent interpretation is not the same as understanding.** Picking the
  "closest valid" interpretation and proceeding looks helpful but bypasses
  the user's actual intent. The user may not even know their request was
  ambiguous.
- **Working *with* the user beats working *for* them.** A good agent is a
  collaborator, not an order-taker. Surfacing a conceptual mismatch early —
  with a concrete, framed question — is more useful than a polished deliverable
  that misses the point.
- **It saves time.** The ARP demo took significant effort to build and debug
  (including a Router+configurator pitfall that consumed debugging time).
  If the user actually wanted OSPF, all of that was wasted.

## When to push back vs. when to proceed

| Situation | Action |
|---|---|
| Request contains a conceptual error (wrong term, conflation) | **Push back.** Flag the mismatch, offer likely alternatives, ask. |
| Request is ambiguous but all interpretations are valid | **Proceed with the most likely one**, state the assumption, offer to adjust. |
| Request is unusual but not wrong | **Proceed.** Unusual is not incorrect. |
| Request is impossible as stated | **Push back.** Explain why, offer the closest feasible alternative. |
| User explicitly confirms after push-back | **Proceed without further question.** Don't nag. |

## How to push back well

1. **Be specific about the mismatch.** Don't say "that doesn't make sense" —
   say *why*: "ARP is an address resolution protocol, not a routing protocol.
   Routing protocols compute paths; ARP resolves next-hop IP addresses to MAC
   addresses."
2. **Offer concrete alternatives.** Give the user a menu of what they might
   have meant, with enough context to choose.
3. **Make it easy to confirm.** "If you meant (a), I'll proceed right now" —
   one word from the user and you're moving.
4. **Don't lecture.** One or two sentences of context, then the question. The
   user is an expert who made a slip, not a student who needs a tutorial.
5. **Recommend a default.** If you have a best guess, say so and offer to
   proceed unless they correct you.

## Relationship to existing skills

This is the **pre-work companion** to the ground-truth method. Ground-truth
§1 says "a request is a pointer to a goal, not the goal itself — resolve the
pointer." This concept adds: **before resolving the pointer, check that it
points to something real in the domain.** If the user says "show me how the
steering wheel routes the car," the ground-truth move is to figure out what
they actually want to see; the sanity-check move is to first say "steering
wheels don't route — they steer. Did you mean the navigation system?"
