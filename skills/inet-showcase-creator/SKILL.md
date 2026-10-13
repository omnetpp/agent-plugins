---
name: inet-showcase-creator
description: |
  Plan and create new INET Framework showcases under the inet/showcases/ directory, or
  rework an existing draft showcase page that is not good enough. Use when asked to add a
  new showcase simulation study and its Sphinx documentation page, or to improve, rework,
  restructure or finish a work-in-progress showcase. Always start with discovery and
  planning; do not create files until user confirms.
---

> The `inet-showcase-team` skill is an **alternative** pipeline for the same job: a coordinator,
> two producers and four blind reviewers at five gates. It uses this file as its build reference.
> Pick one skill per showcase; do not run both on the same page.

# What a showcase is

A showcase is a runnable INET simulation and a short page that tell one story: a networking
problem, the mechanism that resolves it, and evidence that it does. The reader arrives with the
problem and leaves able to explain it in plain words, to watch it happen in the simulation, and
to reuse the configuration that resolves it.

The page keeps a fixed order, and every decision in this skill serves it:

1. **Goals** states the problem and the resolution in plain English, then what the page shows.
2. **About X** explains the problem and the mechanism without INET.
3. **X in INET** says how INET expresses the mechanism.
4. **The Model** shows the network and, where the topic allows, a configuration in which the
   problem is visible and one in which the mechanism is on.
5. **Results** walks the reader through what happens when the simulation runs: which node
   sends which message to whom and why, what state changes, and where the non-obvious moment
   is. The problem happens before the resolution. The walkthrough proves the claim as a side
   effect of showing it; a figure that only proves a point, with no one explaining what
   happens in it, does not teach.

For a tool or visualizer showcase the problem is something the reader needs to see or measure,
and the resolution is the INET feature; the same order holds. The compressed forms in the
exemplar table are legitimate: `wireless/txop` states the problem in one clause, the visualizer
tours have no baseline. The problem may shrink and the baseline may be absent, but the order
never inverts.

A showcase succeeds when a reader who skips every figure still follows the story, and a reader
who reads only the figures still sees the problem before the fix.

# Attention points

The workflow alternates between segments that need the user and segments that run unattended.
Every question is collected into one of three attention points, and each point arrives with an
artifact the user can decide on. Between the points, do not ask: proceed on a stated assumption,
record it, and raise it at the next point.

| Point | When | The user decides on |
|---|---|---|
| **A — design** | Phases 0–1, then the placeholder draft (2.3) | claim and scope, the Phase 0.5 verdict, the storyboard, and the rendered placeholder page: structure, narrative, evidence plan |
| **B — page** | after Phase 3 | the finished page with real evidence |
| **C — ship** | end | remaining minor items, reviewer disagreements, commit |

Phases 2.4–2.8 and Phase 3 are unattended. The one legitimate interrupt is a Phase 2.7 verdict of
*Claim must change* or *Something is wrong in the model*; hand it back as soon as it is issued.

Point A is where the expensive reversals are prevented. On the three showcases measured before
this rule existed, the first-ready page took 1–4 hours, and the changes made after the user saw
it — evidence type, page structure, narrative, prose — took 1 to 19 days.

# Rework entry: an existing draft showcase

When the showcase already exists as a work-in-progress page, enter here instead of at Phase 0.
The expensive decisions — evidence type, structure, narrative — were made without a storyboard;
the rework supplies the storyboard after the fact and rebuilds the page into it.

1. **Reverse-storyboard the existing page.** Extract what it actually delivers: the claim, the
   takeaways a reader leaves with, the section list, and every figure or video with the
   takeaway it serves. Artifacts serving no takeaway, and takeaways with no artifact, are the
   first findings. So is a Results section that states outcomes but never walks through
   what happens in the run.
2. **Write the target storyboard** (Phase 1 shape) against the exemplar of the right kind, after
   reading `references/exemplars.md`. Map every existing artifact to **keep**, **re-capture**
   (same slot, different window, crop, pacing or type) or **cut**. Keep the existing observables
   and literature anchor if the plan had them; write them now if it did not.
3. **Attention point A.** Show the user both storyboards side by side and the artifact map. That
   is the one decision the rework needs; batch the Phase 0.5 questions into it only if the
   audit was never done.
4. **Rewrite the whole page into the target storyboard.** Not a diff of the old prose — the
   old structure survives a patch. Kept artifacts go into their slots as they are; re-capture
   slots get placeholders (2.3). Style pass (2.3b), build, one rendered review.
5. Continue as for a new page: 2.6 run if configs changed, 2.7 gate for every re-capture slot,
   2.8 capture, Phase 3 review, attention points B and C.

Skipped in a rework: Phase 0.5 when the implementation audit already exists in the plan or the
decisions log; the placeholder draft for slots whose artifact is kept. Never skipped: the
storyboard, the style pass, and the blind Phase 3 review.

# Exemplar showcases

The house style is defined by shipped, human-written pages, not by rules. The table lists the
pages the maintainer rates as really good, tagged by kind. **All eleven inform every showcase**:
their shared conventions — section skeleton, how a figure is introduced, how ini excerpts are
cut, how results are ordered — and each page's distinctive presenting techniques are distilled
in `references/exemplars.md`, which the author reads before writing and the style pass (2.3b)
and Phase 3 reviewers check against. On top of that, Phase 0 picks the one page closest in
**kind** to the new showcase — not the page closest in topic — and the author reads it in full
and mimics its section order, its figures per section, and its words per figure.

| Kind | Path (under `showcases/`) | What it exemplifies | Size: words / figures / videos |
|---|---|---|---|
| Protocol mechanism, short | `wireless/txop` | The minimal complete page: Goals → About → X in INET → The Model → Results. One sequence-chart figure carries the result. | 1200 / 3 / 0 |
| Packet-level protocol demo | `wireless/blockack` | An Experiments section lists the configs; each per-config section walks the Qtenv packet traffic view and packet inspector frame by frame, one sentence before each figure. | 2100 / 14 / 0 |
| Chart-driven parameter study | `wireless/aggregation` | Results split by reader question (received packets and throughput, end-to-end delay), one chart each. | 2100 / 7 / 0 |
| Chart-driven parameter study | `wireless/fragmentation` | Same skeleton as aggregation, plus a Further Analysis section for the secondary result. | 2100 / 7 / 0 |
| Cross-technology performance study | `wireless/coexistence` | Goals → The Model → Configuration → Results; performance charts next to spectrum figures and one sequence chart; one video. | 3200 / 8 / 1 |
| Mechanism demo + performance comparison | `tsn/framepreemption` | A mechanism section (Transmission on the Wire) before Results. Results show the behavior first (video, packet log, sequence chart, Wireshark, packet inspector) and the delay charts after. | 3400 / 15 / 1 |
| Progressive multi-config study | `tsn/timesynchronization/clockdrift` | A chain of "Example:" sections, each one config and one chart, adding one element of complexity per step. No video. | 4200 / 23 / 0 |
| Video-driven visualizer demo | `visualizer/canvas/radiomediumactivity` | Scenarios grow simple → multiple nodes → interference; each has a video and an annotated still. No ini excerpts at all. | 2500 / 7 / 3 |
| Feature tour of one module | `visualizer/canvas/spectrum` | One section per feature (probe, spectrum figure, spectrogram, power density map), each with its own config and its own figure or video. | 2800 / 5 / 3 |
| Concept taxonomy | `wireless/analogmodel` | Parallel structure per variant: Overview, then Example. Videos and 3D figures where a still cannot show the idea. | 3100 / 8 / 3 |
| Tool / feature how-to | `general/pcaprecording` | The model → The configuration → Results; external-tool (Wireshark) screenshots, one per interface type; one video. | 1800 / 10 / 1 |

Word counts are of the raw `index.rst` and are for calibrating density, not targets to hit.

A topic-near page or example is still the right source for the *model* (ini and NED); that is a
separate choice, made in Phase 0 step 4.

# Workflow

## Phase 0: Discover existing patterns (before asking questions)

1. Use `inet-framework/inet` deepwiki MCP for INET-specific documentation if needed.
2. Check the destination directory for existing simulation model. Explore and
    analyze it. Use it as a template or starting point.
3. Read `references/exemplars.md` (the conventions shared by all eleven exemplar pages and
   each page's distinctive techniques). Then pick the **exemplar** page closest in kind from
   the Exemplar showcases table (chart-driven study, video-driven mechanism demo, protocol
   handshake, …), read its `doc/index.rst` in full, and note its section order, figures per
   section, and words per figure; the draft is measured against these. Open any other page
   in the table whose technique the storyboard borrows (a packet-inspector walk, a chain of
   "Example:" sections, a video-only results section).
4. Separately, find the topic-nearest showcase or example as the source of the **model**:
   grep `showcases/` and `examples/` for the same modules; read its `omnetpp.ini` and `.ned`.
5. Check the relevant category `index.rst` for toctree structure.
6. Analyze the `results/` directory for existing results. Check what kind of data is available. Possibly ask the user later to provide them if it is needed for better end-result. 

## Phase 0.5: Assess implementation vs. the showcase's claim

Before committing to build a showcase, check whether the INET implementation actually
supports the specific claim the showcase will make. Two distinct risks this catches:
writing a showcase that *names* a protocol while skipping mechanisms a knowledgeable
reader would immediately ask about (the DHCP showcase nearly shipped without lease
expiration), and building a scenario on a modeling *capability* the code doesn't have
(the rate-anomaly showcase's downlink scenario assumed an AP transmits to each client
at that client's rate; INET's rate control kept one state machine per interface, and
per-receiver adaptation had to be implemented before the scenario was possible).

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

**Second list — scenario-required capabilities.** The standard-derived checklist
catches missing protocol *mechanisms*, but a showcase can also silently depend on a
modeling *capability* that no mechanism list will ever contain — precisely because
the standard takes it for granted. Derive this list from the planned scenarios: for
each config, ask "what must the model be able to represent or configure for this
scenario to be expressible at all?" — per-node or per-link parameter heterogeneity,
per-destination or per-flow state, a queue/scheduler discipline, a statistic that
must be recordable per the right key. The real miss this list exists for: the
rate-anomaly showcase's downlink scenario needed the AP to rate-adapt *per client*.
Every real AP does this and the standard assumes it — which is exactly why the
mechanism checklist never surfaced it — but INET's rate control kept a single state
machine per interface, and per-receiver adaptation had to be implemented first. A
human caught that gap; this checklist is how the audit catches the next one.

For trivial / well-trodden cases (e.g. a basic Ethernet topology demo) the checklists
may be one or two items — that's fine, the discipline is the same.

### Step 3: Grade each checklist item against the C++

For each item in the two Step 2 checklists (mechanisms and capabilities), check the
actual code:
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
- The required-mechanisms and scenario-capability checklists with each item's status
  (Steps 2–3)
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
- if scoping introduces a dependency the Phase 0.5 checklists didn't cover — a new
  mechanism, or a scenario-required capability (per-station state, a scheduling
  discipline, a heterogeneous parameter) — extend the Phase 0.5 audit to those items
  now, before summarizing. Phase 0.5 ran before the scope was final; a capability gap
  discovered mid-implementation is the expensive kind.

**Summarize before proceeding:**
- The general scope and the planned outline and claims of the showcase
- The **expected observables**: for each config/scenario, concrete *falsifiable*
  statements of what the run will show when it works — checked later in Phase 2.7.
  Tie them to time and place, not just existence (e.g. "the client's IP goes
  0.0.0.0 → a leased address around t≈2 s in `host[0]`"; "queue length at
  `router.eth[0]` exceeds N at some point"; "node B's RSSI crosses the threshold
  and it reassociates around t≈10 s"). Write at least one per claim.
- The **literature anchor**, when the showcase demonstrates a known effect or anomaly
  that has a published magnitude or analytical model (the Heusse et al. airtime
  formula for the 802.11 rate anomaly, Li et al.'s 1/4–1/7 multi-hop chain capacity,
  near-total flow-in-the-middle starvation): compute the predicted value for the
  planned scenario's parameters and register it, with its source, as one more
  expected observable. Phase 2.7 Step 2 compares the run against it.
- The **storyboard** — the page in miniature, approved before anything is built:
  - the problem in one sentence and the resolution in one sentence, in plain English
  - the claim in one sentence, and the two to four takeaways a reader should leave with
  - the section list in the exemplar's order, one sentence per section
  - the **run walkthrough outline** for Results: the run as a numbered sequence of steps in
    time order, one line each. Every step names the time (or event), the nodes involved,
    the messages exchanged (by protocol name, with the fields that matter), the state that
    changes, and what the reader should notice. Mark the step where the problem shows and
    the step where the mechanism resolves it. Write this from the protocol and the
    configuration first; Phase 2.7 checks it against the real run
  - for every walkthrough step and every takeaway, the evidence artifact that shows it: its
    type (sequence chart, packet inspector, video, table or canvas screenshot, chart — see
    the evidence types in 2.3), what it shows (which nodes, which time window, which axes or
    which visualizer), and the sentence that will stand under it. One artifact can cover
    several steps. One hero artifact per claim. Every further artifact names the step or
    takeaway it serves, or it is cut
- Final path: `showcases/<category>/<showcaseName>/`
- Which `index.rst` to update
- Files to create
- Which configs to run for verification

Wait for explicit user confirmation. This is the first half of attention point A; the
second half is the rendered placeholder draft in 2.3, which the user reviews before any
simulation is run or any evidence is captured.

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

### 2.3 Draft the page with placeholders (second half of attention point A)

Write the **complete** `doc/index.rst` now, before any run and before any capture, with a
placeholder in every figure and video slot the storyboard defined. The user reviews this page
rendered. Structure, narrative and evidence type are cheap to change here and cost days after
capture.

- A placeholder is a grey PNG at the intended display size, carrying the artifact's type and
  the storyboard description of what it shows. The sentence that will stand under the real
  artifact is already in the prose. Generate it with:

  ```bash
  python3 -c "
  from PIL import Image, ImageDraw
  im = Image.new('RGB', (800, 450), (220, 220, 220)); d = ImageDraw.Draw(im)
  d.multiline_text((20, 20), 'PLACEHOLDER\n<type>: <what it shows>', fill=(60, 60, 60))
  im.save('doc/media/placeholder-<name>.png')"
  ```

- Wire the toctree (2.4), run the style pass (2.3b), build the Sphinx HTML, and hand the user
  the rendered page (snapshot it into the Showcase Previewer with `sp add`, see
  §"Showcase Previewer"; the `preview-artifact` skill publishes it as a shareable link). Ask for one
  review of structure, narrative and evidence plan. Apply the answers before 2.6.

Create `doc/index.rst` following this structure:

```rst
Title
=====

Goals
-----
[The problem, the resolution, then what the page shows — in that order]

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
[Walk through the run in time order, following the storyboard's walkthrough outline:
 what happens, which messages are exchanged, what the reader sees in each figure.
 Performance charts, if any, after the walkthrough]

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

**Results section guidance:** Results is a guided walk through the run, not a list of verdicts. Its job is that the reader understands how the protocol works in this scenario; the claim is proved along the way. Write it from the storyboard's walkthrough outline:

- **Narrate in time order.** "At 1.2 s the mobile node leaves the home link. Its access router notices the new attachment and sends a Proxy Binding Update to the home agent..." Each paragraph covers one step: who acts, what message goes where, why, and what changes as a result.
- **Name the messages and the fields that matter.** Say which message it is, who sends it, who receives it, and the one or two fields that drive the behavior (a flag, a lifetime, a sequence number, an address). Give each message's action as a verb (see references/writing.md). Show the packet inspector or a sequence chart where the field is visible.
- **Read every figure out loud.** Before or after each sequence chart, screenshot or video, the prose tells the reader where to look and what they see: which arrow is which message, which table row changed, which node turns red. A figure without that reading is a puzzle, not evidence.
- **Point out the non-obvious.** A retransmission, a message that is absent, a timer that fires, a race, a surprising order, a state that lasts longer than expected. These are why the reader opens the page; say why they happen.
- **Problem before resolution.** Where the page has a baseline, walk the problem run first, then the run with the mechanism, and name the step where the two diverge.
- **A "why" the model cannot answer is a finding.** Explaining each message against the eventlog also checks the model: on the Proxy Mobile IPv6 page it exposed three INET defects (a stale destination cache, a routing loop, a duplicate Router Discovery entry) and a behaviour that breaks RFC 4862, all hidden by the outcome-only page. Do not write around such a gap; hand it to the user as a 2.7 finding.
- **Numbers and charts follow the walkthrough.** A performance chart confirms at scale what the walkthrough showed for single messages. It does not replace the walkthrough.

A reader who finishes Results should be able to retell the exchange message by message and say why each message was sent. The evidence type for each walkthrough step and takeaway is chosen in the storyboard (Phase 1), from this list:

- **Videos/animations** — best for time-dependent behavior (protocol state changes, tree building, failover, handover). Show the simulation running with appropriate visualizers. Most showcases benefit from at least one video. Use the `video-recording` skill for the recording workflow.
- **Qtenv packet inspector screenshots** — best for showcases where packet structure matters (encapsulation, protocol headers, nested packets, tagged frames). Preferred over PCAP/Wireshark screenshots because they show structured protocol layers in a readable tree without introducing an external tool.
- **Charts/plots** — best for performance-oriented showcases (throughput, latency, packet loss, queue lengths). Use the OMNeT++ Analysis Tool or export to generate clean plots. When the x axis is time, label it **"Simulation time [s]"** (or the unit used), not "Time" or "time [s]": the reader must not take it for wall-clock time. Use the same wording in the caption and the prose ("at 2.5 s simulation time").
- **Routing/forwarding table screenshots** — best for routing protocol showcases. Show how tables change over time or differ between nodes.
- **Eventlog excerpts or sequence charts** — best for protocol handshakes or message exchanges where the exact ordering matters. Use the `omnetpp-ide-mcp` skill to drive the IDE's Sequence Chart tool: it can open an `.elog`, search for the relevant exchange by message-name pattern, configure axes/zoom/timeline, and return a PNG — all without manual clicking. Particularly useful when you want a tight frame around a specific protocol exchange (e.g. a DORA handshake) on a chosen subset of axes.
- **Network screenshots with visualizer overlays** — annotated snapshots at key moments (e.g., "after prune" vs "after graft"). Useful when a video would be overkill but a static image captures the state well.

Think about which moments are most surprising or educational for the reader, and give them the most space. The Results section shows the described behavior happening, step by step, in the real run — not a restatement of the config section's predictions, and not bare proof with no explanation of what happens. Capture these artifacts only after Phase 2.7 confirms the run actually demonstrates the claim; capturing earlier risks recording the wrong behavior.

### 2.3b Style pass (unattended, before the user sees any draft)

Spawn one fresh subagent with four paths and nothing else: the draft `doc/index.rst`, the
closest exemplar's `doc/index.rst`, and `references/exemplars.md` and `references/writing.md`
from this skill. It returns a list of violations, each with the line, the convention or rule it
breaks (with the exemplar count or the rule name), and a proposed replacement. Apply them. Run the pass on every draft the user will read — the placeholder
draft and the final page — so the user's review is spent on narrative and evidence, not on
idioms, unearned absolutes and section order.

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
- for an observable carrying a literature anchor (Phase 1), compare the measured
  magnitude against the anchor's predicted value. Landing near the published /
  analytical number is the strongest evidence the parameters are representative —
  the positive counterpart of Step 4's ban on contrived tuning. A large unexplained
  deviation is a *Needs tuning* or *Something is wrong in the model* signal to
  resolve, not a discrepancy to narrate around.
- walk the storyboard's run walkthrough outline against the eventlog, step by step: the
  messages, their order, their senders and receivers, the fields that matter, the times.
  Correct the outline to the real run: add the messages the outline missed, drop the ones
  that do not occur, and flag every surprise. A surprise the model explains is material for
  Results (the non-obvious moment); one it does not explain is a *Something is wrong in the
  model* signal

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

### 2.8 Capture the evidence into the approved slots (unattended)

Replace each placeholder with the artifact the storyboard specified, at the same position and
size, following the evidence guidance in 2.3 and the capture skills (`video-recording`,
`inet-showcase-charts`, `omnetpp-ide-mcp`, `omnetpp-mcp-sim`). Do not add slots, change an
artifact's type, or restructure the page here. If the run shows that a planned artifact cannot
carry its takeaway, that is a 2.7 finding: hand it to the user with the options, do not
substitute silently. Add a FIGURE RECIPE or VIDEO RECIPE comment after every artifact so it
can be redone from the comment alone.

- **Capture at the width the reader sees.** The page column is about 834 px at a 1440 px
  viewport. Qtenv and the IDE do not scale label fonts with window size or zoom, so a capture
  far wider than the column is shrunk on the page and its labels with it: sequence charts
  captured 2088-2160 px wide rendered their labels at about 6 px, and every review passed them.
  Capture close to the rendered width (about 1000 px for a full-width figure), split a chart
  that does not fit legibly, and measure label height on the built page, not in the image
  file. Look for an axis or element that reads as a border or disappears at page size.
- **Question inherited `known:` notes.** A recipe's `known:` limitation is not settled because
  an earlier pass wrote it. If it touches the showcase's main subject (the node, message or
  state the page is about), treat it as a defect to raise with the user: fix it in INET, work
  around it with another visualizer or filter, or state it on the page by the user's choice.
  A route visualizer that never reached the mobile node was carried through a whole rework as
  "known" until the user pointed at it.

## Phase 3: Review and revise (after Results are captured, unattended)

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

Each round, spawn **two fresh subagents in parallel**, both on the **same model the main
conversation is running on** — never a weaker one:

- one loads the `review-as-user` skill, the other `review-as-pro`.
- instruct each subagent to state, at the very start of its report, which model it is
  running on — so a silent downgrade is visible.
- give each subagent only the path to `doc/index.rst`, the closest exemplar's path and
  `references/exemplars.md` for comparison, and the target persona / domain — **not** the authoring rationale or this conversation.
  The blindness is the whole point.
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

### Treat reviewer findings as hypotheses, not instructions

Reviewers are reliable on **errors** — a mislabelled phenomenon, a wrong number, a claim
the code contradicts. Fix those. They are much less reliable on **Missing**, and their
findings there almost all push in one direction: *add more text*. A reader persona
briefed as "has never used INET" will ask you to explain the ini file format; a
completeness-minded technical reviewer will ask you to mention the module's other two
parameters. Acting on both uncritically produces a padded page that a human editor then
strips back out.

Before acting on a "Missing" finding, ask:

- **Would the page's real audience ask this?** The persona's gaps are not always the
  audience's gaps.
- **Does the fix answer the question or just raise it?** "The module declares two more
  parameters" satisfies a completeness objection and leaves the reader wondering which
  two — worse than the original sentence.
- **Was the original sentence actually wrong, or was it read as a stronger claim than it
  made?** "Three parameters describe the tunnel" is not a claim that the module has
  exactly three parameters, and needs no parenthetical.

Fix every Error. Weigh every Missing. Say in your report which Missing findings you
declined and why.

### Verify anything checkable before you write it

Every claim about behaviour that was *reasoned* rather than *run* during one recent
showcase turned out wrong or incomplete, and each check cost under a minute:

- "Both ends of a tunnel need an interface" — running it with the far end's interface
  removed showed only the *sending* end needs one, because decapsulation needs no
  configured state. The tested fact was more interesting than the assumed one.
- "Traffic starts at 2 s so Neighbor Discovery has finished" — the log showed address
  resolution happening at 2.000 s and Router Discovery at 2.6 s. What had finished was
  Duplicate Address Detection.
- "16 packets are sent" — the application had no `stopTime` and sent 17.
- "Four control packets per link" — it was 4 or 5 depending on the configuration, and
  the arithmetic in the results table did not close.

The rule: if a sentence asserts what the model does, run the model. Reading the C++ is
the second-best check; remembering what it does is not a check at all.

## Attention points B and C

After Phase 3, run the style pass (2.3b) once more, build the HTML, and give the user the
rendered finished page together with the Phase 3 report. This is attention point B; batch every
question that was deferred during the unattended phases into it. Apply the answers, then
present the ship decision (attention point C): remaining minor items, reviewer disagreements,
and the commit.

# Showcase Previewer: snapshot every commit

After every commit that touches the showcase directory, snapshot the page into the Showcase
Previewer: `sp add <worktree> <showcase-dir> --agent <name>`. A placeholder draft (2.3) is worth
a snapshot too. When you hand the user a rendered page (2.3, attention points B and C), give the
previewer link. The `showcase-previewer` skill has the details: backfill, locks, flags.

# Output

Provide:
- Final showcase path
- List of created/modified files
- Run command: `inet` (or `inet -c ConfigName` if multiple configs)
- Verification status: confirm that all configs ran successfully

Do not modify files outside the new showcase except required `index.rst` wiring.

# Documentation writing rules

The full rules live in `references/writing.md` and are applied by the style pass (2.3b), not
read while authoring. When writing, work from `references/exemplars.md`, the closest exemplar
page, and these seven essentials:

- Problem → resolution → what we show, at page level and inside each mechanism: motivate before
  explaining, and show the problem happening before showing the fix (§"What a showcase is").
- One idea per sentence, under about 25 words; active voice, present tense, plain verbs.
- One term per concept, fixed at first use; define acronyms and protocol message names once.
- No C++ symbol names in prose, and no phrasing that only makes sense inside INET.
- Do not explain what every INET reader knows (what `omnetpp.ini` is, what `extends` does).
- No unearned absolutes: "never", "always", "cannot", "the simplest" only when you cannot name
  the exception.
- Say each thing once, at the place the reader needs it; mechanism before results, as on master.

A new lesson goes into `references/writing.md` only as a check — a pattern to grep for or a
question to ask of a sentence — never as an anecdote.
