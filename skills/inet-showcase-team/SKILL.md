---
name: inet-showcase-team
description: |
  Coordinate a five-role expert team to create a new INET Framework showcase: an INET
  implementation expert, a standards/domain expert, a university reader, an industry
  practitioner, and you as coordinator. Use when asked to create a showcase with the team,
  the panel, or multiple agents — or whenever a new showcase is worth more scrutiny than a
  single pass. The build mechanics live in the inet-showcase-creator skill; this skill
  governs who is consulted, when, and how disagreements end.
---

# INET Showcase Team — coordinator charter

Loading this skill makes **you** the coordinator. You do the discovery, the writing, the
running, the merging, and every conversation with the user. Four panelists advise you at five
gates; they never write anything but their own reports.

> **The build reference is `inet-showcase-creator`.** Directory layout, ini/NED conventions,
> the `doc/index.rst` structure, the two-reading-layers rules, the writing principles, the
> figure and evidence guidance — all of it stays there, single-sourced. Load it alongside this
> skill and follow it for *how* to build. This file only adds *who reviews what, when, and how
> conflicts end*. Where the two overlap, the creator skill's phase machinery wins; this file
> tells you who to convene inside it.

Work in a dedicated worktree off `inet-master`, not in the main checkout.

## Roster

| Agent | `subagent_type` | Trusted about |
|---|---|---|
| INET expert | `inet-expert` | What the INET code actually does; whether a scenario is expressible; whether an observable is recordable |
| Domain expert | `domain-expert` | What the standard requires; what the literature predicts, with computed magnitudes |
| University expert | `university-expert` | Whether an MSc student or PhD researcher gets to the claim, and can reuse the result |
| Industry expert | `industry-expert` | Whether a practitioner can map the scenario to a real deployment and lift something out |
| Coordinator | (you) | Merging, conflict resolution, all writing, all user escalation |

### Invoking them

- Spawn all panelists for a gate **in a single message** so they run concurrently.
- **Never pass a `model` override.** The agent definitions omit `model:` so each inherits the
  main conversation's model. Every report opens with a model self-report — if one comes back on
  a weaker model than you are running on, discard it and re-spawn. A downgraded reviewer gives
  false confidence.
- Wait for all four before merging. Do not merge partial results, and never guess what a
  pending panelist will say.
- Re-review after revisions spawns a **fresh** agent (a blind re-read is more honest than a
  reviewer anchored on its own findings). Cross-examination instead **continues the same agent**
  via `SendMessage`, because it must be able to hold or withdraw its own position.

## Workspace

Everything the panel produces lives outside the INET source tree, under the (untracked) plan
folder:

```
inet-master/plan/pending/showcase-<name>/
  brief.md                  G1 output — the approved topic brief
  plan.md                   the showcase plan (claim, scenarios, observables, anchor, outline)
  decisions.md              running decision log: escalations, user rulings, dial settings
  panel/
    g1-topic/round1/{inet,domain,university,industry}.md
    g1-topic/merge.md
    g2-feasibility/...
    g3-plan/...
    g4-behavior/...
    g5-doc/...
```

`decisions.md` is not optional. Every escalation, every user ruling, every rejected finding with
its reason goes there. A panel with no paper trail cannot be audited, and you will be asked in
round 3 why something was dropped in round 1.

## Convening protocol

Each panelist gets, in its prompt:

1. **The artifact path** — plan, ini/NED, page, or run outputs. Paths, not pasted content, so it
   resolves directives itself.
2. **The gate** (G1…G5) and the per-gate brief from the gate map below.
3. **Its report path** — `panel/<gate>/round<N>/<role>.md`. It writes that file and nothing else.
4. **The claim** — the one-sentence answer to "what will a reader see this showcase prove?"
5. **The detail dials** — the three 0–10 settings from Phase 1 (standards detail, INET
   configuration detail, implementation detail), because they bound what anyone may ask for.
6. **Persona parameters** where the role takes them: which academic persona, which industry segment.

They must **not** get: the authoring rationale, your reasoning, prior conversation, or — in
round 1 — any other panelist's report. The blindness is what makes the reports worth reading;
a reviewer that knows what you meant reviews your intent instead of your artifact.

## Report contract

Every panelist writes this structure. Keep it stable — merging four reports depends on it.

```markdown
# <role> — <gate> — round <N>

Model: <the model I am running on>
Artifact: <path> (<git rev or mtime>)

## Verdict
BLOCK | REVISE | ENDORSE — one sentence.

## Coverage
What I examined. **What I deliberately did not examine**, so silence is readable.
Role-specific: documents+revisions consulted (domain) / persona worn (university) /
segment spoken for (industry) / code paths read and runs performed (INET).

## Findings
### F1 — <one-line claim>  [blocker|major|minor] [confidence: high|medium|low]
- **Where**: file:line or section
- **Lens**: why this matters from my seat
- **Evidence**: src/…:NNN | RFC NNNN §x | IEEE 802.1Q-2022 cl. 8.6.8 | measured value | run output
- **Proposed change**: what must become true (not finished prose)
- **Cost**: words / figures / configs / sim time

## Contributions
Things to ADD that nobody asked for and the showcase is worse without. Same fields.

## Cut
At least one thing to remove, with what is lost by removing it.

## Out of scope
Noticed, not my seat, recorded so it is not lost.
```

### Severity vocabulary

| Severity | Meaning | Equivalent grades |
|---|---|---|
| `blocker` | The gate cannot pass until this is resolved | Phase 0.5 blocker-by-definition · `review-as-pro` Error · `review-as-user` High |
| `major` | Fix before shipping; you apply it unless it conflicts | Missing · Medium |
| `minor` | Collect, apply once at the end, never loop on | Minor · Low |

Each role's charter defines what a blocker means **from its seat** — a university-expert blocker
is a broken prerequisite chain, not a wish for more detail; an industry-expert blocker is a claim
that would misinform a real decision, not a preference about scale. Hold them to their own
definitions; a finding that does not meet its role's blocker bar gets demoted on merge, with the
reason recorded.

## Gate map

### G1 — Topic brief *(feeds `inet-showcase-creator` Phase 0)*

Input: a candidate topic, or "pick one" — in which case source candidates from
`plan/pending/showcase-topic-catalog.md` and `existing-showcase-review.md`, which record the
uncovered topics and the state of the existing 84 showcases.

Each panelist scores the candidate 0–5 on its own axis with justification: implementation
readiness (INET), standards/literature substance (domain), teaching value (university),
practitioner relevance (industry). Each names the top risk from its seat.

You produce `brief.md`: claim candidate, target audience, why this topic now, top three risks,
nearest existing art. **The user picks.** Do not proceed on a topic the user has not chosen.

### G2 — Feasibility *(Phase 0.5)*

Order matters — it is what keeps the audit from drifting into "the parts that look implemented
look fine".

1. **Domain expert, blind to the code**, writes the required-mechanisms checklist from the
   standard alone, with normative force per item.
2. **University expert** adds the mechanisms every textbook shows, and **industry expert** adds
   the capabilities every real product has. These two lists exist because the standard's MUST
   list systematically misses what everyone takes for granted — the per-client rate adaptation
   that made a planned downlink scenario inexpressible is the canonical case.
3. **INET expert** derives the scenario-required capability list from the draft scenarios and
   grades *every item of all three lists* against the C++: implemented / partial-simplified /
   missing-stubbed, each with a file:line.
4. **You** build the gap table with two independent axes — *blocker by definition* and *impacts
   current scope* — and never collapse them into one severity. Then issue a verdict from the
   Phase 0.5 menu (*suitable as-is* / *suitable with claim narrowed to X* / *not suitable —
   implementation needs work first*) and hand it to the user. "Document the limitations openly"
   is not a verdict.

### G3 — Plan review *(Phase 1 / 1.5)*

The gate this team exists for. Artifact: `plan.md`, containing the claim, the scenario and config
matrix, the **expected observables** (falsifiable, tied to a time and place), the literature
anchor, the evidence types, the doc outline, and the detail dials.

All four, blind, in parallel. Per-seat questions:

- **INET** — are the configs expressible as written? Is every observable actually recordable, at
  the claimed resolution? Will each config reach its phenomenon before `sim-time-limit`?
- **Domain** — is the claim true under the standard? Is the anchor right and computed for *these*
  parameters? Are the values representative? Does the scenario exercise the mechanism it names?
- **University** — does the outline build without forward references? Is the claim legible and
  falsifiable to the persona? Where would they stall? Is the evidence type the one that teaches?
- **Industry** — is each scenario mappable to a deployment? Is the regime one practitioners
  operate in? What comparison is missing? What is liftable?

Everyone proposes at least one concrete contribution with its cost, and **everyone names a cut**.
The cut requirement is structural: four lenses grow a page monotonically otherwise, and
wall-of-text is the dominant defect across the existing corpus.

Merge, resolve, escalate what is left, then update `plan.md` and take it to the user for the
Phase 1 confirmation. If the panel introduced a new mechanism or capability dependency, reopen G2
for those items before summarizing.

### G4 — Behavioral gate *(Phase 2.7)*

Convene **after the run, before any Results artifact is captured**. Capturing first means
recording the wrong behavior and noticing later.

- **INET** — verify each predicted observable in the actual run (logs, `opp_scavetool` scalars,
  eventlog, live paused inspection). Confirm *when*, not only *that*. Sanity-check magnitudes.
- **Domain** — compare the measured magnitude against the literature anchor; rule on whether the
  tuning stayed within representative ranges.
- **University** — legibility: would the persona *see* the effect in the planned artifact, or is
  it present-but-invisible? Flag degenerate cases (flatline, single tick, t=0 firing, total
  saturation, transient over before warm-up).
- **Industry** — second opinion on representativeness after tuning.

You issue the Phase 2.7 verdict. Only *demonstrates the claim cleanly* unlocks artifact capture.
*Needs tuning* loops Steps 2–4 at most two or three honest rounds; *claim must change* and
*something is wrong in the model* both exit to the user.

### G5 — Final doc review *(Phase 3)*

On the finished `doc/index.rst` with its Results artifacts.

- **University expert** runs the `review-as-user` method in full, wearing the named persona.
- **INET and domain experts** split `review-as-pro`: INET verifies the prose against the code,
  domain against the standard. Two reviewers, two authorities, no overlap to argue about.
- **Industry expert** reviews applicability: liftability, overclaiming, unstated limitations that
  would bite in a real deployment.

Fix every `blocker` and `major`; collect `minor` and apply once at the end. Re-run on the revised
doc. Stop when a round surfaces no blockers or majors, or after **3 rounds**. **On recurrence** —
a panelist re-flags something you already addressed — stop and hand it to the user; that is
author-versus-reviewer disagreement, a human call, not something to churn on.

## Merge protocol

1. **Read all four reports in full** before deciding anything.
2. **Deduplicate** by (location, claim). Count how many independent lenses raised it — cross-lens
   agreement is the strongest signal you have, and it outranks any single panelist's severity.
3. **Check each finding against its role's blocker definition.** Demote what does not meet the bar,
   and record the demotion.
4. **Classify** every finding: **accept** (you will apply it), **relocate** (accepted, but the depth
   goes into a Layer-2 admonition rather than the main flow), **reject** (with a reason), **contest**
   (two lenses disagree), **escalate** (the user must rule).
5. **Write `merge.md`** for the gate: the classification of every finding, the running cost total
   against the plan's budget, and the list going to cross-examination.
6. **Apply accepted changes yourself, in your own voice.** Never paste a panelist's wording into the
   page. Four voices in one document produce exactly the uneven, over-long page these reviews exist
   to prevent.

## Conflict resolution ladder

Apply in order. Stop at the first rung that settles it.

1. **Truth first.** The INET expert on what the code does and the domain expert on what the standard
   says both outrank pedagogy and marketability. Code-versus-standard is *not* a conflict: report
   both plainly ("INET does X; the standard requires Y") and route it through the Phase 0.5
   machinery — documented limitation, narrowed claim, or implementation bug to surface.
2. **Feasibility is not negotiable.** A missing-capability finding removes a scenario from scope. It
   is never argued down; the only counter is "implement it first", which is the user's call.
3. **The dials arbitrate volume.** Every "more detail" dispute between university, industry and
   domain is settled by the three 0–10 dials the user set. A request above the dial is relocated or
   dropped, with the reason recorded. A panelist contesting a dial is an escalation, not a finding —
   the dials belong to the user.
4. **Layer discipline decides placement.** Accepted depth goes into a titled `Details — why …` or
   `Fine print — …` admonition. Layer 1's ≤70-word paragraph budget, figure cadence, and
   one-bold-takeaway-per-figure rule are hard constraints, not preferences. Most "add more" findings
   are accept-with-relocation.
5. **Cost budget.** When accepted contributions exceed the plan's declared budget (configs, figures,
   target length), rank by severity, then by cross-lens agreement, and drop the tail **explicitly** in
   `merge.md`. A silently dropped finding reads later as one that was never raised.
6. **Escalate to the user** when two blockers are mutually exclusive, a dial is contested, a scenario
   needs implementation work, or the claim itself must change.

### Escalation format

One paragraph per position, stated in the panelist's own strongest terms — not your paraphrase of
why it is wrong — then your recommendation with reasoning, then a menu of choices. Same shape as the
Phase 0.5 and 2.7 verdict hand-backs. Record the user's ruling in `decisions.md`.

### Cross-examination (round 2, contested items only)

Not a re-review. For each contested finding, continue the panelist via `SendMessage` and give it:
its own finding, the opposing position stated **neutrally** (do not signal who you agree with), and
one instruction — hold with new evidence, or withdraw. A panelist that holds without new evidence has
withdrawn in practice; treat it as such and say so in `merge.md`.

## Coordinator anti-patterns

- **Splitting the difference silently.** Half-implementing a contested finding satisfies nobody and
  hides the disagreement from the user.
- **Dropping a blocker because it is inconvenient.** A blocker-by-definition is by construction
  something a knowledgeable reader expects; a footnote does not change that expectation.
- **Letting panelist prose reach the page.** You write. They advise.
- **Reviewing inline instead of convening.** A same-context review is contaminated: it already knows
  every intent, which is exactly what the reader will not know. If you cannot spawn subagents, say so,
  tell the user which gates went unreviewed, and stop — do not fake a panel.
- **Convening on nothing.** A panel on a plan without expected observables, or on a page without
  Results, produces speculation. Have the artifact ready first.
- **Running the panel past its cap.** Three rounds, then the user decides.
- **Losing the trail.** Every rejection needs a recorded reason.

## Output

When the showcase is done, report: final path, created and modified files, the run command, the
verification status of every config, which gates convened and in how many rounds, what each round
changed, unresolved `minor` items, and every disagreement left for the user. Move the showcase plan
to `plan/done/` once the page ships.
