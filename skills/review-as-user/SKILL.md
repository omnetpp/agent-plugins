---
name: review-as-user
description: |
  Review a document (tutorial, showcase, README, guide) from the perspective of its target reader.
  Simulates a sequential first-time reading, tracking mental model buildup, learning moments,
  and naturally arising questions. Produces a structured report of findings by severity.
  Use when asked to review documentation quality, find gaps, or assess reader experience.
---

# Review-as-User

Perform an empathetic, sequential review of a document by simulating a first-time reader
from the target audience. The goal is to find gaps, confusions, and unanswered questions
that the *author* can't see because they already know the material.

## Phase 0: Preparation

1. **Read the entire document** and all referenced/inlined files (literalinclude targets,
   linked source files, referenced images).
2. **Verify assets exist** — check that all referenced images, downloads, and links are
   actually present. Note any broken references immediately.
3. **Establish the persona.** Either the user specifies it or infer from context. Define:
   - **Knowledge level** — what they already know (e.g., "some networking, knows what
     OMNeT++/INET are, heard of DHCP")
   - **Goal** — why they're reading (e.g., "learn how to set up DHCP in INET")
   - **Reading style** — sequential, first time, moderately attentive

   If the persona is unclear, ask the user one short question to calibrate.

## Phase 1: Sequential Reading

Walk through the document **in reading order**, section by section (or paragraph by
paragraph for dense material). For each section, track three things:

### What the reader learns
- New concepts, facts, or configuration details introduced in this section.
- How their mental model updates (e.g., "DHCP = address rental with time limits").

### Questions that naturally arise
Categorize each question:
- **Resolved later** — the document answers it in a subsequent section. Note where.
- **Unresolved** — the document never answers it. Assess whether it *should*.
- **Out of scope** — a reasonable question but not the document's job to answer.

### Friction points
- Jargon used before it's explained
- Assumptions about knowledge the persona doesn't have
- Concepts mentioned but never connected (dangling threads)
- Ordering problems (explanation comes after it's needed)
- Contradictions or inconsistencies with code/config shown
- Math or parameter relationships the reader must work out themselves

## Phase 2: Cross-Checking

After the sequential pass:

1. **Code vs. prose consistency** — Do descriptions in the text match what the NED/ini/source
   files actually contain? Flag any mismatches.
2. **Figures and visuals** — Do referenced images exist? Do figure captions match what the
   image would show? Are there sections that *need* a visual but don't have one?
3. **Dangling references** — Broken links, placeholder URLs (e.g., `TODO`), non-existent
   download targets.
4. **Try-it-yourself path** — Could the reader actually follow the instructions to run this
   themselves? Are there missing steps?

## Phase 2b: Deep Verification (Optional, INET/OMNeT++ showcases)

When reviewing INET showcases or tutorials, these additional verification steps are
available and should be used when the document makes specific behavioral claims
(packet counts, state transitions, timing, routing decisions, etc.):

### Rendered HTML output

The Sphinx-built HTML lives at `doc/src/_build/html/` (relative to INET root).
Use it to verify:
- `.. literalinclude::` blocks render the correct ini/NED lines
- Figures and images display correctly
- Cross-references and links resolve

To rebuild (from `doc/src/`): `make html`
To launch a live-reload server: `make server` (serves on port 8000)

### Running the simulation (omnetpp-mcp-sim skill)

Use the `omnetpp-mcp-sim` skill to launch the showcase's simulation configs and
verify behavioral claims directly. This turns "this might be wrong" into
"this IS wrong" or "confirmed correct."

**What you can verify:**
- Claimed packet counts → check via `get_module_log`, result scalars
- State machine transitions → inspect logs for specific state changes
- Routing table contents → query module parameters/watches
- Timing claims → check simulation time vs. event sequence

Refer to the `omnetpp-mcp-sim` skill for launch instructions and available tools.

**When to use:** When the document asserts specific numeric results, claims about
protocol behavior ("no branches are pruned", "adjacency never reaches Full"), or
describes observable sequences that can be verified in logs.

## Phase 3: Report

Structure the output as:

### Mental Model Walkthrough
Section-by-section analysis from Phase 1. Use the document's own section headings.
Keep each entry concise: 2-3 bullet points for "learns", then questions/friction.

### Summary

#### Strengths
What the document does well — acknowledge good structure, clear explanations,
effective pedagogical choices.

#### Issues (grouped by severity)

- **High** — Blocks understanding or creates wrong mental models. Missing essential
  visuals, factual errors, code/prose contradictions.
- **Medium** — Natural questions left unanswered, unclear parameter semantics,
  unexplained prerequisites, ordering problems.
- **Low** — Minor ambiguities, style nits, missed opportunities for deeper explanation
  that are arguably out of scope.

Each issue: one sentence describing the problem, with a file/line reference if applicable.

## Guidelines

- **Be the reader, not the editor.** The primary lens is "what would I be confused about?"
  not "how would I rewrite this." The report should surface *reader experience problems*,
  not prescribe solutions (unless asked).
- **Don't nitpick prose style.** Focus on conceptual clarity, not grammar or word choice.
- **Distinguish "I'm confused" from "I'm curious."** A question the reader would Google
  is fine; a question that blocks them from continuing is not.
- **Calibrate to the persona.** A question that's trivial for an expert but blocking for a
  student is a real issue if the target audience is students.
- **Track resolution across sections.** If section 3 answers a question from section 1,
  note whether the gap between them is acceptable or too wide.
