---
name: inet-showcase-creator
description: |
  Plan and create new INET Framework showcases under the inet/showcases/ directory.
  Use when asked to add a new showcase simulation study and its Sphinx documentation page.
  Always start with discovery and planning; do not create files until user confirms.
---

# Workflow

## Phase 0: Discover existing patterns (before asking questions)

1. Use `inet-framework/inet` deepwiki MCP for INET-specific documentation if needed.
2. Check the destination directory for existing simulation model. Explore and
    analyze it. Use it as a template or starting point.
3. Find the best matching existing showcase as template:
   - `grep_search` or `find_by_name` in `showcases/` for similar features
   - Read its `doc/index.rst`, `omnetpp.ini`, and `.ned` files
4. Check the relevant category `index.rst` for toctree structure.
5. Analyze the `results/` directory for existing results. Check what kind of data is available. Possibly ask the user later to provide them if it is needed for better end-result. 

## Phase 0.5: Assess implementation vs. the showcase's claim

Before committing to build a showcase, check whether the INET implementation actually
supports the specific claim the showcase will make. The risk this catches: writing a
showcase that *names* a protocol while skipping mechanisms a knowledgeable reader
would immediately ask about (the DHCP showcase nearly shipped without lease
expiration).

Run these steps in order. Don't skip ahead — the order is what prevents
"read the code and judge reasonableness" creep.

### Step 1: Pin down the claim

The claim is the one-sentence answer to "what will a reader see this showcase prove?"
— usually inferable from the user's initial request, or from the template showcase.
If unclear, ask one focused question before continuing.

### Step 2: Enumerate the protocol's required mechanisms as a checklist (before reading code)

Write down what the RFC / standard *requires* the protocol to do, as a flat checklist,
**before** opening any C++. For DHCP this would include: DORA, retransmission with
backoff, lease expiration at server, T1/T2 renewal/rebind at client, INIT-REBOOT,
DECLINE, RELEASE, INFORM, relay support, …

This list comes from the standard, not from intuition or from what looks easy to
demo. The point is to have a mechanical reference the audit grades against, so the
assessment can't drift into "the parts that look implemented look fine."

For trivial / well-trodden cases (e.g. a basic Ethernet topology demo) the checklist
may be one or two items — that's fine, the discipline is the same.

### Step 3: Grade each checklist item against the C++

For each item in the Step 2 checklist, check the actual code:
- Read the relevant `.cc`/`.h`, not just `.ned`
- Grep for `TODO`, `FIXME`, "not implemented", "ignored", "simplified", "for now"
- Check that NED parameters the mechanism relies on are actually read in the C++
- Mark each item: **implemented**, **partial/simplified**, or **missing/stubbed**

### Step 4: Classify each gap on two independent axes

For every item that isn't fully implemented, record **both**:

- **Blocker by definition (Y/N):** Is this mechanism something a knowledgeable reader
  of a showcase on this protocol would expect to be modeled? (Lease expiration in a
  DHCP showcase: Y. Obscure DHCP option handling: typically N.)
- **Impacts current scope (Y/N):** Does the showcase's current claim/scenarios
  actually exercise this mechanism?

**Do not collapse these into a single severity.** A gap can be a blocker-by-definition
even if the current narrow scope dodges it — that's exactly the case that gets
embarrassing later, and merging the axes hides it.

### Step 5: Report findings, then issue a verdict (constrained by the gap table)

Present the user with:
- The claim (Step 1)
- The required-mechanisms checklist with each item's status (Steps 2–3)
- A gap table with two columns: *blocker by definition* and *impacts current scope*
- A verdict from the menu in Step 6

### Step 6: Verdict menu — gated by the gap table

Pick one:

- **Suitable as-is** — available **only if no gap in the table has _blocker by
  definition = Y_**. Otherwise this verdict is off the menu, regardless of whether
  the current scope happens to dodge the gap.
- **Suitable with claim narrowed to X** — describe the narrower claim explicitly,
  and confirm that under it no remaining gap has _blocker by definition = Y_.
  Narrowing the claim changes what a reader of *this showcase* will expect, which
  can dissolve a blocker; it does not retroactively reclassify gaps.
- **Not suitable — implementation needs work first** — always available.

"Document the limitations openly" is **not** a verdict. A blocker-by-definition is
by construction something a knowledgeable reader will expect to be modeled; a
footnote does not change that expectation. (Open-noted caveats remain appropriate
for *non*-blocker gaps inside an otherwise-suitable showcase — not as a way to ship
past a blocker.)

After issuing the verdict, ask the user how to proceed — they may accept it, push to
narrow further, fix the implementation first, or abandon. Do not proceed to Phase 1
until they have chosen.

## Phase 1: Clarify scope (do not create files yet)

Ask only what's essential. Infer defaults from existing model and template showcase.

**Core questions:**
- **Source**: What is the source of the showcase? If a base model is not present, what other example should it be based on?
- **Goal**: What feature is demonstrated? What claim should the showcase prove?
- **Category**: Where does it belong?
- **Detail**: 
  - How much the underlying network standards should be detailed (i.e. generic, non-INET specific info)? (on the level of 0-10)
  - How much detail should be given about how to actually configure this simulation scenario (i.e. INET specific configuration info)? (on the level of 0-10)
  - How much detail about the actual implementation in INET should be given (i.e. info from c++ files)? (on the level of 0-10)

**Ask only if unclear from context:**
- Network topology size/complexity (if not yet specified by the user)
- Expected outputs (plots, pcap, metrics)
- Linux-only requirements (namespaces, `RealTimeScheduler`, `CAP_SYS_ADMIN`)
- Multiple ini configs needed

**Iterate with the user until you are sure about the scope and the basic outline of the showcase.**
- ask the user to generate new result files if needed (like new diagrams, logs, pcap files, eventlogs, statistics, screenshots, screen video captures etc.)
- incorporate the new results into the plan

**Summarize before proceeding:**
- The general scope and the planned outline and claims of the showcase
- Final path: `showcases/<category>/<showcaseName>/`
- Which `index.rst` to update
- Files to create
- Which configs to run for verification

Wait for explicit user confirmation (until the user switches to code mode)

## Phase 1.5: Check existing examples for enrichment

After the showcase plan is established, search `examples/` and `showcases/` for
existing simulations that use the same modules or features. Check if they contain
anything worth incorporating:
- Interesting configurations or edge cases not yet in the plan
- Working parameter values that could serve as sanity checks
- Results or behaviors worth referencing or contrasting

This is not about copying — the showcase design comes first. This step is about
finding extras that make the showcase more complete or interesting. Update the plan
if you find something valuable, and mention it to the user.

## Phase 2: Implement (after confirmation)

### 2.1 Directory structure

Create `showcases/<category>/<showcaseName>/` and `doc/` subdirectory (if not yet present)

### 2.2 Simulation files

**Required:**
- `omnetpp.ini` with `sim-time-limit`, clear `[Config ...]` sections
- `.ned` file(s) with package `inet.showcases.<category>.<showcaseName>`
- you can modify existing files to achieve the goal of the showcase inside the new showcase directory (but do not delete or modify files that are not part of the showcase)

**Conventions:**
- Network name: `<Feature>Showcase` (e.g., `HandoverShowcase`)
- Use WiredNetworkBase/WirelessNetworkBase for the network
- Use `extends = ...` for config inheritance
- Add `description = "..."` to configs
- When literalincluding network files, only include the relevant parts (e.g. no license header or package and import statements))
- Don't use image captions but describe the image either before or after the image
- Include a network screenshot and briefly describe the network, including relevant node types. Don't literalinclude the network NED (unless specifically necessary)
- Network screenshot: use `area="module_rectangle"` and `margin=5`. Use the `omnetpp-mcp-sim` skill's `get_canvas_image` tool to capture screenshots.
- Most of the time we don't need :width: 100% for figures
- Add visualizers for understanding when relevant. You can use the inet-visualization skill for that. Not all showcases need
visualizers, e.g. in some showcases, the interesting behavior is in the charts, eventlogs, etc. For example, the wireless/qos showcase.

### 2.3 Documentation page

Create `doc/index.rst` following this structure:

```rst
Title
=====

Goals
-----
[What is demonstrated and why]

| Verified with INET version: ``X.Y``
| Source files location: `inet/showcases/... <GitHub URL>`__

About [Protocol/Feature]
------------------------
[Protocol/feature background — pure domain knowledge, no INET specifics.
 Explain the problem being solved, the protocol's approach, key terminology,
 and relevant RFCs. Write as if INET didn't exist.]

[Protocol/Feature] in INET
---------------------------
[How the protocol/feature maps to INET modules and parameters:
 - Key node types (explain before first use in network descriptions)
 - Module structure (include module interior screenshot if helpful)
 - Configuration parameters with rationale (explain once here, not per-config)
 - Implementation-specific behavior and limitations]

The Model
---------
[Network topologies and scenario descriptions only.
 Should be clean and focused — INET mechanics already covered above.]

[Config Name] Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[Use .. literalinclude:: ../omnetpp.ini blocks.
 Focus on scenario walkthrough and expected behavior, not re-explaining parameters.]

Results
-------
[Choose evidence types based on what makes the showcase's behavior visible and interesting]

Sources: :download:`omnetpp.ini <../omnetpp.ini>`, :download:`*.ned <../*.ned>`

Try It Yourself
---------------
[Standard opp_env instructions - copy from template]

Discussion
----------
Use `this page <GitHub issue URL>`__ in the GitHub issue tracker for commenting on this showcase.
```

**Document structure guidance:**

- **Three-layer separation for protocol showcases:** protocol background → INET implementation → specific scenarios. This prevents INET details from being scattered across config sections. Simpler showcases (e.g., a feature demo with no protocol background) can merge or skip layers.
- **Explain key node types before first use:** If the network uses a specialized node type (e.g., MulticastRouter, TsnDevice), explain what it is and what it adds before describing the network topology.
- **Module interior screenshots:** For showcases where the internal module structure matters (e.g., protocol implementations, QoS queues), include a screenshot of the relevant compound module's interior in the INET section. Use `get_canvas_image` with the submodule path.
- **Configuration parameters explained once:** Explain parameters (with rationale for non-obvious choices) in the INET section. Per-config sections should just show the literalinclude and walk through the scenario behavior.
- **Implementation notes/limitations:** Place near the implementation description in the INET section, not at the end or scattered in config sections.

**Results section guidance:** Think about what makes the showcase's behavior visible and interesting. Choose from these evidence types based on the showcase's focus:

- **Videos/animations** — best for time-dependent behavior (protocol state changes, tree building, failover, handover). Show the simulation running with appropriate visualizers. Most showcases benefit from at least one video. Use the `video-recording` skill for the recording workflow.
- **Qtenv packet inspector screenshots** — best for showcases where packet structure matters (encapsulation, protocol headers, nested packets, tagged frames). Preferred over PCAP/Wireshark screenshots because they show structured protocol layers in a readable tree without introducing an external tool.
- **Charts/plots** — best for performance-oriented showcases (throughput, latency, packet loss, queue lengths). Use the OMNeT++ Analysis Tool or export to generate clean plots.
- **Routing/forwarding table screenshots** — best for routing protocol showcases. Show how tables change over time or differ between nodes.
- **Eventlog excerpts or sequence charts** — best for protocol handshakes or message exchanges where the exact ordering matters.
- **Network screenshots with visualizer overlays** — annotated snapshots at key moments (e.g., "after prune" vs "after graft"). Useful when a video would be overkill but a static image captures the state well.

Think about which moments or artifacts are most surprising, educational, or confirming for the reader. The Results section should provide evidence that the described behavior actually happens — not just restate the config section's predictions.

### 2.4 Wire into toctree

Add entry to appropriate `index.rst`:
- Simple category: `showcases/<category>/index.rst` → add `<name>/doc/index`
- Nested (TSN): `showcases/tsn/<subcategory>/index.rst` → add `<name>/doc/index`
- New subcategory: may require creating intermediate `index.rst` and wiring to parent

### 2.5 Static checks

- NED `package` matches folder path
- All `:download:` links reference existing files
- No broken `:doc:` or `:ned:` references

### 2.6 Run and verify

Run every config in the showcase to confirm it works. Use opp_repl MCP if available,
otherwise fall back to command-line execution (see the `omnetpp` skill for details).

**Steps:**
1. Build if needed: `make MODE=debug -j$(nproc)` in the INET root
2. For each `[Config ...]` section in `omnetpp.ini`:
   - Run: `inet -u Cmdenv -c <ConfigName>`
   - Check exit code and output for errors
   - If it fails: fix the issue and re-run (do not skip)
3. Verify that expected result files are produced (e.g. `.sca`, `.vec`, `.pcap`)
4. If the showcase documentation makes claims about specific results (e.g. "host A
   receives 100 packets"), spot-check them against actual output using `opp_scavetool`

**If a simulation fails to run, do not proceed to the output phase.** Fix the root
cause first. Common issues:
- Missing NED imports
- Wrong parameter names (always check the NED source, never guess)
- Missing module types
- Incorrect network topology connections

**Debugging tips** (from the `simulation-creator` skill):
- Add a PCAP recorder with `checksumMode = "computed"` and `fcsMode = "computed"` to
  inspect traffic with tcpdump
- Use `--debug-on-error=true` for stack traces
- Use `--cmdenv-express-mode=false --cmdenv-log-level=detail` for verbose logs

# Output

Provide:
- Final showcase path
- List of created/modified files
- Run command: `inet` (or `inet -c ConfigName` if multiple configs)
- Verification status: confirm that all configs ran successfully

Do not modify files outside the new showcase except required `index.rst` wiring.

# Documentation Writing Principles

- Goals should answer "why does this feature exist?" before "what does it do?" — structure as: problem → solution → what we demonstrate
- Separate domain knowledge (the protocol/standard) from tool knowledge (INET configuration) — use an "About X" section for protocol background before The Model, and an "X in INET" subsection inside The Model for module/parameter overview
- Never reference a concept before defining it — follow dependency order (e.g. define "lease" before describing the DORA exchange that grants one)
- Explain the *why* behind each mechanism, not just the *what* (e.g. why Renewing uses unicast but Rebinding uses broadcast)
- When a parameter appears in multiple places, the mechanism must be described the same way, not just the outcome (e.g. don't describe `numReservedAddresses` differently in the module overview vs the results section)
- Abstract models (state machines, protocol layers) need explicit grounding in previously described concrete steps
- For each config/scenario, identify the primary reader question and answer it explicitly in the Results section (e.g. "does the client get the same IP after reboot?")

### Clarity and precision

- **Qualify ambiguous nouns on first use**: "group" → "multicast group", "entry" → "entry in the router's forwarding table". Every noun needs enough context to be unambiguous at its first appearance.
- **Replace vague qualifiers with concrete consequences**: Don't say "expensive" or "costly" — name the actual effect (e.g. extra header overhead, processing bottleneck, wasted bandwidth).
- **Explain what named protocol messages do**: When introducing a protocol message type, state its action as a verb — "Register message" → "*registers* the source with the RP"; "Join message" → "asks routers to create a forwarding entry."
- **Unaware participants**: When an entity (e.g. the source host) is unaware of the protocol being described, say so explicitly — "the source sends a normal multicast packet — it has no knowledge of PIM."

### Structure and notation

- **Standard notation gets its own paragraph**: If the protocol has standard notation (e.g. `(S,G)`, `(*,G)` in PIM), define it in a dedicated paragraph *before* first use, not inline mid-sentence.
- **Two-context terms need both contexts stated**: When a term appears in two roles (e.g. `(S,G)` as a forwarding table entry AND as a Join message type), explain both explicitly. Don't assume the reader will infer the second meaning.
- **Label temporary vs. steady-state**: When a mechanism has phases (e.g. bootstrap → normal operation), explicitly label what is temporary and what is the final state. Don't let the reader mistake the bootstrap for the normal mode.

### Readability

- **Dense paragraphs → bullet lists**: When a paragraph contains more than two sequential steps or more than three distinct concepts, break it into a bulleted or numbered list.
- **Problem→solution at every level**: Not just in the Goals section — each new mechanism should motivate *why it's needed* before explaining *what it does* (e.g. "receivers don't know the source → that's why we need an RP").
