---
name: inet-showcase-creator
description: |
  Plan and create new INET Framework showcases under the inet/showcases/ directory.
  Use when asked to add a new showcase simulation study and its Sphinx documentation page.
  Always start with discovery and planning; do not create files until user confirms.
---

> Reworking an EXISTING showcase page for readability (wall-of-text fixes,
> ranking pages by readability metrics) is the separate
> `showcase-readability-rework` skill — use that, not this one.

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

Raise all doubts, discuss every important aspect with the user. Infer defaults from existing model and template showcase.

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
- The **expected observables**: for each config/scenario, concrete *falsifiable*
  statements of what the run will show when it works — checked later in Phase 2.7.
  Tie them to time and place, not just existence (e.g. "the client's IP goes
  0.0.0.0 → a leased address around t≈2 s in `host[0]`"; "queue length at
  `router.eth[0]` exceeds N at some point"; "node B's RSSI crosses the threshold
  and it reassociates around t≈10 s"). Write at least one per claim.
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
[What is demonstrated and why — short; the box and hero figure below carry the punchline]

| Verified with INET version: ``X.Y``
| Source files location: `inet/showcases/... <GitHub URL>`__

.. admonition:: In one minute

   [3–5 bullets: the effect (with its headline numbers), the cause, the fix(es),
    and a one-line roadmap of the page. Written LAST, once Results exist.]

[Hero artifact: the strongest Results figure, placed here so it lands on the first
 screen — before any protocol background — followed by its one-sentence bold
 takeaway. Reusing the same image file as the Results section is fine.]

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

- **Evidence before theory:** the "In one minute" box and the hero artifact put the page's claim, proven, on the first screen. The About section then explains what the reader has already seen — which also permits writing it tighter. (Full rules: *Two reading layers* under Documentation Writing Principles.)
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
- **Eventlog excerpts or sequence charts** — best for protocol handshakes or message exchanges where the exact ordering matters. Use the `omnetpp-ide-mcp` skill to drive the IDE's Sequence Chart tool: it can open an `.elog`, search for the relevant exchange by message-name pattern, configure axes/zoom/timeline, and return a PNG — all without manual clicking. Particularly useful when you want a tight frame around a specific protocol exchange (e.g. a DORA handshake) on a chosen subset of axes.
- **Network screenshots with visualizer overlays** — annotated snapshots at key moments (e.g., "after prune" vs "after graft"). Useful when a video would be overkill but a static image captures the state well.

Think about which moments or artifacts are most surprising, educational, or confirming for the reader. The Results section should provide evidence that the described behavior actually happens — not just restate the config section's predictions. Capture these artifacts only after Phase 2.7 confirms the run actually demonstrates the claim; capturing earlier risks recording the wrong behavior.

### 2.4 Wire into toctree

Add entry to appropriate `index.rst`:
- Simple category: `showcases/<category>/index.rst` → add `<name>/doc/index`
- Nested (TSN): `showcases/tsn/<subcategory>/index.rst` → add `<name>/doc/index`
- New subcategory: may require creating intermediate `index.rst` and wiring to parent

### 2.5 Static checks

- NED `package` matches folder path
- All `:download:` links reference existing files
- No broken `:doc:` or `:ned:` references
- ``literalinclude`` markers actually slice what you expect. `:start-at:` + `:end-before:` are order-sensitive: if the ini's section order doesn't match the doc's subsection order, the slice silently extends past the intended config, or worse, swallows the next one too. Default rule: **keep ini section order matching doc subsection order** (helps direct ini readers too). Verify by rendering or by reading the rendered output.

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
- Add a PCAP recorder (per-node `numPcapRecorders`) with `checksumMode = "computed"` and
  `fcsMode = "computed"` to inspect traffic with tcpdump. Only commit it if the page text
  refers to it; otherwise capture ad-hoc and don't commit. (See the `simulation-creator` skill.)
- Use `--debug-on-error=true` for stack traces
- Use `--cmdenv-express-mode=false --cmdenv-log-level=detail` for verbose logs

### 2.7 Critically review the simulation's behavior (gate before capturing results)

Phase 2.6 confirms the simulation *runs* — clean exit, result files produced, stated
numbers match output. It cannot tell you whether the run actually *exhibits the
phenomenon the showcase is about*. A simulation can pass 2.6 while the interesting thing
never happens, or happens so trivially that no reader would notice. This step is the
behavioral gate that 2.6 is not.

The risk this catches: the showcase's prose describes the *intended* story, an artifact
gets captured, and nobody confirms the artifact shows that story rather than a flat line.
A lease-expiration showcase whose `sim-time-limit` is shorter than the lease never expires
a lease; a handover showcase whose tx power keeps the node inside one cell never hands
over — both run green.

Run these steps in order. **Do not capture any Results artifact (video, chart, packet
screenshot, eventlog) until this step issues a clean verdict** — capturing first means
recording the wrong behavior and noticing later.

#### Step 1: Retrieve the predicted observables

Pull the expected-observables list registered in Phase 1. If none exists yet, write it
**now, before observing the run**, so the check can't drift into rationalizing whatever
happened. Each observable must be falsifiable and tied to a time/place, not just existence.

#### Step 2: Observe the actual run against each prediction

For each predicted observable, find the evidence in the actual run:
- module logs, recorded statistics (`opp_scavetool`), the eventlog
- live inspection via the `omnetpp-mcp-sim` skill — pause at the predicted time and look at
  module state, watches, and the FES; this is where you actually *watch what's happening*
- for a time-located prediction, confirm *when* it happens, not just *that* it happens

#### Step 3: Classify each observable

Mark each one:
- **Observed and legible** — happens, at the right magnitude and time, and would be visible
  to a reader
- **Absent** — the predicted phenomenon never occurs in this run
- **Degenerate / trivial** — technically occurs but in a way no reader would learn from:
  the event of interest fires at t=0 before the scenario is set up, a metric that flatlines
  or is a single data point, a counter that ticks once and never again, saturation so total
  that nothing varies (0% or 100% throughout), or a transient that is over before the
  simulation warms up
- **Present but uncaptured** — it happens, but no statistic / visualizer / log surfaces it,
  so there is nothing to show

Independently of the predictions, sanity-check magnitudes: throughput near link capacity?
latencies physically plausible? counts the right order of magnitude? Implausible numbers
mean a misconfiguration that "runs fine."

#### Step 4: Verdict

Pick one:
- **Demonstrates the claim cleanly** — every observable is *observed and legible* and
  magnitudes are plausible. **Only this verdict unlocks Results artifact capture.**
- **Needs tuning** — the phenomenon is absent or degenerate because of parameters (load,
  power, positions, durations, `sim-time-limit`). Adjust **within realistic, representative
  ranges**, re-run, repeat from Step 2. Tuning that only makes the phenomenon appear by
  pushing parameters to contrived values is itself a failure — a showcase must demonstrate
  its claim under parameters a reader would accept as representative, not under values
  reverse-engineered to force the result.
- **Claim must change** — the run is correct but shows something narrower or different than
  the doc claims. This is a scope change: **present it to the user and let them decide**
  (narrow the claim, re-scope, or abandon), the same way Phase 0.5 hands its verdict back.
  Do not silently rewrite the claim. If narrowed, revisit the prediction list.
- **Something is wrong in the model** — implausible magnitudes or impossible behavior point
  at a config or model bug. **Surface it to the user** before continuing; if it traces to
  the implementation, it may reopen the Phase 0.5 assessment.

"Capture it anyway and describe what we hoped to see" is **not** a verdict. The Results
section must show evidence the behavior happened — a caption describing intent over an
artifact that shows nothing is the exact failure this step exists to prevent.

**Bound the loop.** Loop Steps 2–4 only while the verdict stays *Needs tuning* and the
tuning stays within representative ranges. If two or three rounds of honest tuning don't
produce a clean run — or if you find yourself reaching for contrived values to force it —
stop and surface the situation to the user rather than spin or fake it. A *Claim must
change* or *Something is wrong in the model* verdict also exits the loop to the user.

Only a *Demonstrates the claim cleanly* verdict lets you proceed to capture Results
artifacts (the evidence types in §2.3) and finalize the Results section.

## Phase 3: Review and revise (after Results are captured)

Once `doc/index.rst` and its Results artifacts are complete (Phase 2.7 passed), put the
finished document through an independent review before declaring done.

### Subagents required — do not review inline

This phase depends on *isolated* review: a reviewer that has not seen the authoring
conversation. `review-as-user` in particular simulates a first-time reader, which is
meaningless run in the same context that just wrote the doc — it already knows every intent.

- **If you can spawn subagents:** run the review (below).
- **If you cannot spawn subagents:** do **not** attempt the review inline — a same-context
  review is contaminated and gives false confidence. Instead, tell the user the showcase is
  complete and recommend they run `review-as-user` and `review-as-pro` on `doc/index.rst`
  themselves, then stop. Skipping the automated review here is acceptable; faking it inline
  is not.

### Running the review (subagent path)

Each round, spawn **two fresh subagents in parallel, both on the Opus model** (not Sonnet):

- one loads the `review-as-user` skill, the other `review-as-pro`.
- give each subagent only the path to `doc/index.rst` plus the target persona / domain —
  **not** the authoring rationale or this conversation. The blindness is the whole point.
- re-spawn fresh each round (don't reuse a subagent): a blind re-read of the revised doc is
  more honest than a reviewer anchored on its own prior findings.

### Iterate — capped at 3 rounds

1. Collect both reports and triage by their severity grades:
   - **review-as-user:** High / Medium / Low
   - **review-as-pro:** Error / Missing / Minor
2. Fix every **High**, **Error**, and **Missing** finding. Collect Medium / Low / Minor but
   do **not** loop on them — apply them once at the end or hand them to the user.
3. Re-run the review on the revised doc.
4. **Stop when** a round surfaces no High / Error / Missing findings, **or** after **3
   rounds**, whichever comes first.
5. **On recurrence** — a reviewer re-flags something you already addressed — stop the loop
   and surface it to the user. That's author-vs-reviewer disagreement, a human call, not
   something to churn on (same hand-back as the Phase 0.5 / 2.7 verdicts).

Report which rounds ran, what was fixed each round, and any unresolved Medium/Low items or
disagreements left for the user.

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

### Two reading layers (the anti-wall-of-text rules)

A showcase page is written in two layers, so a skimming reader gets the whole story
and a careful reader loses nothing. The failure mode these rules prevent: 3,000+
words of uniform paragraphs where core claims, derivations, tuning rationale, and
caveats all look identical, the best evidence sits 1,000 words deep, and nothing
marks the fine print as skippable.

**Layer 1 — the main flow:**

- **Open with an "In one minute" admonition** (after Goals, before everything else):
  the effect with its headline numbers, the cause, the fix(es), and a one-line
  roadmap of the page. Write it last, once Results exist — it summarizes evidence,
  it doesn't predict it.
- **Lead with evidence.** The strongest Results artifact appears within the first
  screen — right after the one-minute box, before protocol background. Theory
  explains what the reader has already seen.
- **Paragraph budget: ≤ ~70 words.** A longer paragraph gets split, bulleted, or
  its depth moved to a Layer-2 box. The main flow must read end-to-end *without
  opening any box* and still tell the complete story.
- **Figure cadence.** No figure is preceded by more than ~2 paragraphs of new prose
  since the last visual element. If prose accumulates past that, either a figure is
  missing or the prose is fine print that belongs in a box.
- **Every figure gets a takeaway.** Immediately after each figure, one bolded
  sentence stating what it proves (e.g. "**One station at 6 Mbps pulls four 54 Mbps
  stations down to ~2.5 Mbps each.**"). Figure + takeaway must stand alone — a
  reader who sees only those two things learns the result.

**Layer 2 — the fine print:**

- **Box the depth, don't cut it.** Derivations (e.g. airtime arithmetic), parameter
  tuning rationale (e.g. why sensitivity/noise floor were adjusted), and caveats /
  known limitations go into titled admonitions at their point of use:

  ```rst
  .. admonition:: Details — why a 6 Mbps frame costs ~6× the airtime

     [the derivation, as bullets]

  .. admonition:: Fine print — per-station fairness under saturation

     [the caveat, stated plainly]
  ```

- **Titles are descriptive, not generic.** "Details — why X" / "Fine print — Y",
  never a bare "Note". Box titles collectively form a scannable index of the page's
  fine print.
- **Don't over-box.** If a section grows more boxes than flow, the scope is wrong —
  cut or restructure instead. The boxes exist to protect the main flow, not to
  absorb unlimited depth.

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
