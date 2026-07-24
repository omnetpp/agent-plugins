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
2. **Read the entire document** and resolve every directive to its source (see
   "Resolving RST directives" below) — config files, NED files, scripts, scenario files,
   included code fragments, and figures/charts.
3. **Locate the implementation.** Find and read the relevant source code files that
   implement the behavior the document describes. This is essential — never evaluate
   claims from memory or general knowledge alone.
4. **Identify the reference standard** (RFC, IEEE spec, textbook definition) if applicable.

### Resolving RST directives

The document is `.rst` source, so figures and code appear as directives, not rendered
output. Resolve each one before judging it:

- **`.. figure::` / `.. image::`** — the target (e.g. `media/x.png`) is relative to the
  `.rst` file's directory. **Open and view the image.** For a diagram, check it matches the
  topology/prose; for a chart, check the plotted values and trend match the claimed
  behavior. A chart that contradicts the text is a factual error, not a cosmetic one.
- **`.. literalinclude::`** — the path is relative to the `.rst` file. Read the source
  file, then clip to the slice the reader actually sees: `:start-at:`/`:end-at:`,
  `:start-after:`/`:end-before:`, or `:lines:`. Verify the shown fragment against the prose
  (parameter names, values, types) and confirm it is still current with the file it
  includes from — a stale slice is a real error.
- **`.. video::`** — cannot be watched. **Only if** it (or a figure) is immediately
  followed by a `..` comment holding a **VIDEO RECIPE / FIGURE RECIPE** (`config:`, `seed:`,
  `shows:`, `anchors:`): re-run that config (via the `omnetpp-mcp-sim` / `video-recording`
  skills), express-run to the recipe's `window:`, and confirm the **anchors** still hold in
  the message log — each anchor is a *mechanism* plus a *last-observed sim time*, so it
  doubles as the oracle for "does the clip still depict what `shows:` and the prose claim";
  an anchor that moved or prose the replay contradicts is a factual error. **No recipe
  (older showcases have none) → don't replay the sim for the video;** just review the
  surrounding prose on its own terms.

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

### Check applicability, not just truth
A claim can be individually **true** yet not apply to the scenario the document actually
demonstrates — the most common way a "fix"/"solution"/"cause" claim goes wrong, and one a
naive fact-check waves through because every word is correct. For every claim that a
mechanism *solves*, *fixes*, *mitigates*, *prevents*, or *causes* the demonstrated effect:
- **Reconstruct the mechanism, don't just look it up.** Trace how the claimed fix/cause
  would actually operate *in this scenario*, step by step, as if you had to reimplement or
  reproduce it — name exactly what it acts on and follow it against this topology, traffic,
  and roles. Verifying a claim is merely *true* tolerates vagueness; reconstructing *how it
  would work here* forces the precision that exposes a mismatch. If the reconstruction needs
  a fact the scenario contradicts, that gap is the error. (This is the step that surfaces
  these; the checks below are what it turns up.)
- **Cross-reference the claim against the configured scenario** — topology, traffic
  direction (who transmits to whom), and node roles — not just against the code/standard in
  the abstract. A correct statement about a *different* configuration (e.g. a downlink /
  AP-side fix cited for an uplink demo) is an error even though it is factually accurate.
- **Pin down exactly what the mechanism acts on**, then confirm that thing is present and
  dominant in the scenario as run. Ask literally: *"would this change the demonstrated
  result?"* If the mechanism operates on traffic, a node, or a layer the scenario doesn't
  exercise, it is misapplied — flag it.
- **External-system claims sit outside the code/spec surface.** A claim about a system *not*
  in the implementation or the standard (a different stack, a real-world product, another
  OS's behavior) cannot be checked by reading the source. Verify it against domain knowledge
  of *that* system's mechanism, and scrutinize applicability hardest here — true-but-
  inapplicable claims hide in exactly these "in the real world, X handles this" asides.

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
- **True is not the same as applicable.** Verify every fix/solution/causation claim actually
  applies to the scenario *as configured* (topology, traffic direction, node roles), not
  merely that it is true in general — true-but-inapplicable claims are the ones a naive
  fact-check misses (see "Check applicability, not just truth").
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
