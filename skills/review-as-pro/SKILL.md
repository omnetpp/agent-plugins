---
name: review-as-pro
description: |
  Review a technical document as a domain expert, verifying factual correctness against
  implementation code and protocol standards. Finds errors, misleading claims, and missing
  behaviors. Use when asked to review a document for technical accuracy, verify claims
  against source code, or check whether a showcase/tutorial correctly describes protocol
  or system behavior.
---

# Review-as-Pro

Review a technical document by adopting the mindset of a domain expert who knows both the
subject matter (protocol, algorithm, system) and the actual implementation. The goal is to
catch factual errors, code/prose mismatches, and significant omissions that undermine the
document's credibility or educational value.

## Phase 0: Preparation

1. **Identify the domain.** Determine the protocol, algorithm, or system the document
   describes (e.g., DHCP, OSPF, TCP congestion control, a scheduling algorithm).
2. **Read the entire document** and all referenced/inlined files (config files, NED files,
   scripts, scenario files).
3. **Locate the implementation.** Find and read the relevant source code files that
   implement the behavior the document describes. This is essential — never evaluate
   claims from memory or general knowledge alone.
4. **Identify the reference standard** (RFC, IEEE spec, textbook definition) if applicable.

## Phase 1: Claim Verification

Walk through the document and extract every verifiable technical claim. For each claim:

### Check against implementation
- Read the actual source code that implements the described behavior.
- Verify parameter names, default values, address ranges, state names, message types.
- Verify behavioral descriptions: which messages are sent, unicast vs broadcast,
  state transitions, timer values, pool calculations.
- Flag any claim where the prose says X but the code does Y.

### Check against the standard/protocol spec
- Is the described protocol behavior consistent with the relevant RFC or specification?
- If the implementation deviates from the standard, note whether the document
  acknowledges this or silently presents implementation-specific behavior as standard.

### Check numerical/logical consistency
- Verify arithmetic (address ranges, timer calculations, pool sizes).
- Check boundary conditions (off-by-one in ranges, edge cases in state machines).
- Verify that configuration values in the document match the actual config files.

## Phase 2: Completeness Check

Assess what the document *omits* that a domain expert would expect to see:

- **Missing protocol behaviors** — Important message types, state transitions, or
  mechanisms not mentioned (e.g., NAK responses, RELEASE messages, DECLINE).
- **Missing failure/edge cases** — What happens when things go wrong? Timeouts,
  rejected requests, expired leases, unreachable servers.
- **Model limitations** — Simplifications in the implementation vs. real-world behavior
  that the reader should be aware of (e.g., server doesn't expire leases, no ARP probe).
- **Missing options/parameters** — Common protocol options (DNS, NTP) provided by the
  implementation but not mentioned in the document.

Only flag omissions that are **relevant to the document's scope and audience**. A brief
showcase need not cover every RFC edge case.

## Phase 3: Report

Structure the output as:

### Technically Incorrect
Numbered list of factual errors. Each entry:
- One-sentence summary of the error
- What the document says (with line reference)
- What the code/standard actually does (with file and line reference)

### Missing Behaviors
Numbered list of significant omissions. Each entry:
- What is missing and why it matters
- Where in the implementation it exists (file/line reference if applicable)

### Minor Issues
Brief list of ambiguities, misleading phrasing, or stylistic concerns that don't
rise to the level of factual error.

### Summary Table
Concise table with columns: #, Issue, Severity (Error / Missing / Minor).

## Guidelines

- **Never evaluate claims from memory alone.** Always read the actual implementation
  source code. Protocols in simulation frameworks often differ from textbook descriptions.
- **Distinguish document errors from implementation bugs.** If the code behaves
  differently from the RFC, note it, but the primary question is whether the document
  accurately describes what the code *actually does*.
- **Be precise with numbers.** When flagging an off-by-one or wrong range, show the
  exact computation from the code.
- **Quote the code.** Use file:line citations when referencing implementation details.
- **Don't prescribe rewrites** unless asked. The report should identify *what is wrong*,
  not propose new text.
- **Calibrate omission severity.** A missing DHCPRELEASE mention in a brief getting-started
  guide is minor; in a comprehensive protocol tutorial, it's significant.
