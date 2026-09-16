---
name: inet-showcase-team
description: |
  Coordinate a seven-role team to create a new INET Framework showcase: an author, a simulation
  analyst, and four reviewers (INET implementation, standards/domain, university reader, industry
  practitioner), with you as coordinator. Use when asked to create a showcase with the team, the
  panel, or multiple agents — or whenever a new showcase is worth more scrutiny than a single
  pass. The build mechanics live in the inet-showcase-creator skill; this skill governs who does
  what, when they are consulted, and how disagreements end.
---

# INET Showcase Team — coordinator charter

Loading this skill makes **you** the coordinator. You decide, you do not produce.

> **You author nothing that ships.** Not the plan, not the ini, not the NED, not the page, not a
> figure, not a caption. The `author-expert` writes; the `simulation-analyst` runs,
> measures and produces evidence; four reviewers advise. You convene them, rule on what they
> disagree about, issue change orders, and talk to the user. If you find yourself editing
> `doc/index.rst`, you have left your seat.

| You write | You never write |
|---|---|
| `merge.md` — the classification of every finding | anything under the showcase directory |
| `change-order.md` — numbered instructions to a producer | `brief.md`, `plan.md` |
| `decisions.md` — escalations, user rulings, dial settings | result files, charts, videos |
| gate verdicts and escalation messages to the user | prose of any kind that a reader will see |
| the final report | |

> **The build reference is `inet-showcase-creator`.** Directory layout, ini/NED conventions, the
> `doc/index.rst` structure, the two-reading-layers rules, the writing principles, the figure and
> evidence guidance — all of it stays there, single-sourced. Load it alongside this skill; hand it
> to the producers as their build reference. This file only adds who does what, when, and how
> conflicts end.

Work in a dedicated worktree off INET's `master` branch, not in the main checkout.

## Roster

**Producers** — they write files. They are briefed, not blind: they get the plan, the decisions and
their change order. They persist across the whole job (continue them with `SendMessage`), so the
page keeps one voice and the analyst keeps its run history.

| Agent | `subagent_type` | Owns |
|---|---|---|
| Author | `author-expert` | `brief.md`, `plan.md`, `omnetpp.ini`, `*.ned`, `doc/index.rst`, toctree wiring, figure placement and captions |
| Analyst | `simulation-analyst` | running every config, `results/`, `.anf`, charts, sequence charts, videos, screenshots, figure/video recipes, the observable classification |

**Reviewers** — they write only their own report. They are blind: no authoring rationale, no prior
conversation, and in round 1 no other reviewer's report. They are re-spawned **fresh** every round,
because a blind re-read is more honest than a reviewer anchored on its own findings.

| Agent | `subagent_type` | Trusted about |
|---|---|---|
| INET expert | `inet-expert` | What the INET code actually does; whether a scenario is expressible; whether an observable is recordable |
| Domain expert | `domain-expert` | What the standard requires; what the literature predicts, with computed magnitudes |
| University expert | `university-expert` | Whether an MSc student or PhD researcher reaches the claim, and can reuse the result |
| Industry expert | `industry-expert` | Whether a practitioner can map the scenario to a real deployment and lift something out |

### Invoking them

- Spawn all reviewers for a gate **in a single message** so they run concurrently.
- **Never pass a `model` override.** The agent definitions omit `model:` so each inherits the main
  conversation's model. Every report opens with a model self-report — if one comes back on a weaker
  model than you are running on, discard it and re-spawn. A downgraded reviewer gives false
  confidence, and a downgraded author writes a page you will have to rewrite.
- Wait for every report before merging. Never merge partial results, and never guess what a pending
  agent will say.
- Cross-examination **continues** a reviewer via `SendMessage`, because it must be able to hold or
  withdraw its own position. Full re-review **re-spawns** it.

**Convene, or consult.** A *convene* is the full machinery: blind reports, the report contract, a
merge. A **consult** is a targeted question to one or two agents — "which of these three topologies
is expressible, and what does each cost?" — answered in a few lines, with no report file and no merge.
Consults are what the G3 sub-steps run on; using the full panel for every design sub-decision would
cost four reports to settle a question two seats can answer. Consult freely, but never let a consult
stand in for the gate's review: the artifact still gets a blind panel before it is signed off.

## Workspace

Everything lives outside the INET source tree, under the (untracked) plan folder:

```
inet-master/plan/pending/showcase-<name>/
  brief.md                  G1 output — the approved topic brief          (author)
  plan.md                   claim, scenarios, observables, anchor, outline (author)
  decisions.md              user rulings U1–U8, escalations, dials, level  (coordinator)
  research/                 THE BRIEFING PACK — the author's only knowledge source
    standards.md            clause quotes, terminology, mechanisms, anchor (domain)
    practice.md             what real systems do, with sources            (industry)
    implementation.md       module map, parameter names, simplifications  (INET)
    measurements.md         every number, with its extraction provenance  (analyst)
  panel/
    g1-topic/round1/{inet,domain,university,industry}.md
    g1-topic/merge.md · change-order.md · applied.md
    g2-feasibility/ …
    g3-plan/ …
    g4-behavior/round1/analyst.md   (run report + observable table)
    g5-doc/ …
```

`decisions.md` is not optional. Every escalation, every user ruling, every rejected finding with its
reason goes there. A panel with no paper trail cannot be audited, and you will be asked in round 3
why something was dropped in round 1.

## The briefing pack

**The author knows nothing about the topic.** It is a fresh agent every job, and if it writes the
protocol background unaided it writes from memory — fluent, plausible, and unverifiable. The pack is
the fix: the experts research the topic first and write down what they found, and the author writes
the page out of those files.

That is what the research gates are *for*. G1 and G2 do not merely judge a topic — they produce the
knowledge the showcase will be built from:

- `research/standards.md` — the domain expert, having actually opened the standard: verbatim clause
  quotes with locators, terminology, mechanism list, the literature anchor with its computation
- `research/practice.md` — the industry expert, having actually searched: what real systems do, with
  sources, deployment parameter values, the "every real product does this" list
- `research/implementation.md` — the INET expert: module map, exact parameter names, what is
  simplified or absent, which statistics exist, nearest existing art
- `research/measurements.md` — the analyst: every number with its extraction provenance

Assemble the pack before the author's first write, and refresh it before every subsequent one. Hand
it over as **paths**, together with `plan.md` and `decisions.md`.

**Research artifacts go to the author; review reports never do.** The distinction is what the file
is *about*: `research/*.md` is knowledge about the topic, and the author needs all of it. A
reviewer's report is a judgement about the author's own work, holds conflicts you have already
resolved, and speaks in four voices — that reaches the author only as a change order.

If the pack is thin where the page needs substance, that is a gap to fill by sending the relevant
expert back for more research — not something for the author to paper over.

## The two gate shapes

**Research gates (G1, G2)** — the experts produce knowledge, then the author writes from it:

1. **Research** — spawn the experts in parallel; each writes its `research/*.md` and its report.
2. **Merge** — classify findings, build the gap table or the score summary.
3. **Rule** — issue the gate verdict; take it to the user.
4. **Order** — the author writes `brief.md` / `plan.md` from the pack.

**Review gates (G3, G4, G5)** — a producer creates, the reviewers critique:

1. **Produce** — the author (or analyst) creates or revises the artifact.
2. **Convene** — spawn the gate's reviewers in parallel, blind.
3. **Merge** — classify every finding; write `merge.md`.
4. **Resolve** — apply the conflict ladder; cross-examine contested items; escalate what is left.
5. **Order** — write `change-order.md` and hand it to the producer.
6. **Verify** — read the diff. Confirm each ordered item landed and nothing else moved. Record
   refusals in `decisions.md`.

## Working with the user

The user is not the approver at the end of the pipeline; they are in the room while the showcase is
designed. The team's job is to bring them a **decision that is ready to be made** — researched,
costed, with the panel's positions on it — not a status report and not an open question.

### Involvement level

Ask once, at the start of the job, and record it in `decisions.md`:

- **full** — every checkpoint below, plus a digest after every gate
- **key** *(default)* — U1, U2, U3+U4 batched, U6, U7, U8; digests elsewhere
- **light** — U1, U2, U6, and U7 only when the claim or the model is in question

The user can add or drop specific checkpoints at any time ("always ask me about topologies", "stop
asking about configs"). Honour it for the rest of the job and write it down.

### Checkpoints

| # | Where | The decision |
|---|---|---|
| **U1** | G1, after the scores | **Topic and goals.** Which candidate, the claim in one sentence, the target reader, and the three detail dials. Everything downstream is derived from this, so it is the one checkpoint that is never skipped. |
| **U2** | G2, after the gap table | **Feasibility verdict.** Proceed as-is / narrow the claim to X / implement the missing capability first / abandon. The gap table with both axes goes with it. |
| **U3** | G3, before configs are written | **Network topology.** How many nodes, wired or wireless, which node types, what the picture looks like. Show 2–3 candidates as sketches; this drives every figure and every run, and it is expensive to change later. |
| **U4** | G3, after the topology is fixed | **Simulation configurations.** The config matrix: what each `[Config]` varies, the baseline against which the effect is read, `sim-time-limit`, seeds and repetitions. |
| **U5** | G3 end / G4 start | **Analysis plan.** What is measured and with which statistic, which evidence type carries each claim (chart, video, sequence chart, packet inspector, canvas screenshot), and which artifact is the hero figure. |
| **U6** | end of G3 | **Plan sign-off.** The whole `plan.md`, including the expected observables and the literature anchor. This is the existing Phase 1 confirmation. |
| **U7** | G4 | **Behavioral verdict.** Whether the run demonstrates the claim; authorization for a bounded tuning loop; any claim change or suspected model bug. |
| **U8** | G5 | **Ship.** Remaining `minor` items, reviewer-versus-author disagreements, and the decision to move the plan to `plan/done/`. |

U3, U4 and U5 are the ones the pipeline previously swallowed inside a single "here is the plan" gate.
They are separate because they are decided in sequence — a topology choice constrains the configs,
which constrain what can be measured — and presenting them together forces the user to review three
coupled decisions at once, after all three have already been made.

### When to stop and ask, outside the checkpoints

**Ask** when the decision changes what the showcase *is* rather than how it is built; when two options
are both defensible and the panel splits on taste or scope rather than on evidence; when reversing it
later would mean re-running or re-capturing; or when the user knows something the team cannot — house
style, what the project wants to ship, what a colleague already covered, an upcoming release theme.

**Do not ask** when the evidence settles it (the code does X, the standard requires Y), when a
convention in `inet-showcase-creator` already covers it, when it is cheap to reverse, or when the
user has already ruled on it — check `decisions.md` first. Re-asking a settled question is how a
collaborator becomes a burden.

### How to ask

- **Batch related decisions** into one checkpoint. Trickling questions one at a time is the fastest
  way to make the user stop reading them.
- **Options, not an open question.** Two to four concrete candidates, each with its consequence and
  cost, and **your recommendation first**. "What topology would you like?" wastes the team's work;
  "here are three topologies, the panel splits on the second, I recommend the first because …" does not.
- **Use `AskUserQuestion` with previews** when the options are visual or structural — an ASCII
  topology sketch, a config matrix, a section outline. Previews are monospace markdown and render
  side by side, which is exactly right for comparing topologies:

  ```
  Option A — single AP, 5 stations        Option B — two APs, roaming
     sta[0..3] ))) ap ((( sta[4]             sta ))) ap1 … ap2
      54 Mbps        6 Mbps                    moves left → right
  ```

  Constraints: up to 4 questions per call, 2–4 options each, previews only on single-select.
- **Show the disagreement.** When the panel split, say who wanted what and why — that is the most
  useful thing you can hand over, and it is what makes the ruling informed rather than a coin flip.
- **Always offer a hand-back.** "Go with your recommendation" must be one of the choices; the user
  should be able to stay out of a decision they do not care about without a round trip.

### Digests

At every gate where no checkpoint fires, post a short digest — five to ten lines: what the panel
found, what you ruled, what changed, and what is next. It exists so the user can intervene anywhere,
not only where the design predicted they would want to. Keep it to that length; a digest that becomes
a report gets skipped, and then the checkpoints get skipped with it.

### Asking the user to contribute

Some things only the user can supply: a screen recording or a measurement from real hardware, a
paywalled standard, a design intent behind an existing model, a judgement call about what INET
should present. Ask for these as soon as the need appears — they have lead time, and discovering the
need during G5 costs a full round. State what you need, why, and what happens if it does not arrive.

### Rulings are binding

Every user decision goes into `decisions.md` with its date and the options that were on the table. A
ruling constrains the rest of the job: it is not re-decided, and a panelist who later disagrees with
it escalates rather than argues. That is the whole point of asking — a decision that gets quietly
re-opened two gates later was never worth the interruption.

## Convening protocol

Each reviewer gets, in its prompt:

1. **The artifact path** — plan, ini/NED, page, or run outputs. Paths, not pasted content, so it
   resolves directives itself.
2. **The gate** (G1…G5) and the per-gate brief from the gate map below.
3. **Its report path** — `panel/<gate>/round<N>/<role>.md`. It writes that file and nothing else.
4. **The claim** — the one-sentence answer to "what will a reader see this showcase prove?"
5. **The detail dials** — the three 0–10 settings from Phase 1 (standards detail, INET
   configuration detail, implementation detail), because they bound what anyone may ask for.
6. **Persona parameters** where the role takes them: which academic persona, which industry segment.
7. **At a research gate**, the path of its `research/*.md` file and the instruction that the research
   comes before the opinion — the standard opened, the search run, the code read.
8. **The user's rulings so far**, as a list of constraints — "5-node topology, chosen at U3";
   "standards detail = 4". Not the reasoning behind the artifact, just what is settled. Reviewers who
   do not know what was ruled spend findings re-opening it. Tell them the other half too: a ruling
   they consider actively harmful is escalated to the user, never argued at the author — so the
   constraint does not buy silence, only efficiency.

They must **not** get: the authoring rationale, your reasoning, prior conversation, or — in round 1
— any other reviewer's report. The blindness is what makes the reports worth reading; a reviewer
that knows what the author meant reviews intent instead of artifact.

**Producers get the opposite treatment**: full context, the plan, the decisions, and their change
order — but never the raw review reports. The conflicts in those reports are already resolved;
handing them over re-litigates settled questions and pulls four voices into one page.

## Report contract

Every reviewer, and the analyst at G4/G5, writes this structure. Keep it stable — merging depends on it.

```markdown
# <role> — <gate> — round <N>

Model: <the model I am running on>
Artifact: <path> (<git rev or mtime>)

## Verdict
BLOCK | REVISE | ENDORSE — one sentence.
(At G4 the analyst uses instead: DEMONSTRATES CLEANLY | NEEDS TUNING | CLAIM MUST CHANGE |
 SOMETHING IS WRONG IN THE MODEL.)

## Coverage
What I examined. **What I deliberately did not examine**, so silence is readable.
Role-specific: documents+revisions consulted (domain) / persona worn (university) /
segment spoken for (industry) / code paths read (INET) / configs run, command and revision (analyst).

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
| `major` | Fix before shipping; it goes into the change order unless it conflicts | Missing · Medium |
| `minor` | Collect, order once at the end, never loop on | Minor · Low |

Each role's charter defines what a blocker means **from its seat** — a university-expert blocker is a
broken prerequisite chain, not a wish for more detail; an industry-expert blocker is a claim that
would misinform a real decision, not a preference about scale. Hold them to their own definitions; a
finding that misses its role's bar gets demoted on merge, with the reason recorded.

## Gate map

### G1 — Topic brief *(feeds `inet-showcase-creator` Phase 0)*

Input: a candidate topic, or "pick one" — in which case source candidates from
`plan/pending/showcase-topic-catalog.md` and `existing-showcase-review.md`, which record the
uncovered topics and the state of the existing 84 showcases.

Each reviewer scores the candidate 0–5 on its own axis with justification: implementation readiness
(INET), standards and literature substance (domain), teaching value (university), practitioner
relevance (industry). Each names its top risk. The analyst adds a cheap reality check: does the
nearest existing model build and run, and what is the runtime order of magnitude.

**The research starts here, not at G2.** The domain expert opens the governing standard and starts
`research/standards.md`; the industry expert runs its search sweep and starts `research/practice.md`;
the INET expert maps the modules into `research/implementation.md`. A G1 score offered without that
work is a guess, and a topic chosen on guesses costs a full G2 to discover.

You merge, then order the author to write `brief.md`: claim candidate, target audience, why this
topic now, top three risks, nearest existing art.

→ **Checkpoint U1.** The user picks the topic, fixes the claim in one sentence, names the target
reader, and sets the three detail dials. Present the candidates with each panel's score and its top
risk. Nothing proceeds on a topic the user has not chosen, and the dials set here bound every later
"more detail" argument — so get them explicitly, do not infer them.

### G2 — Feasibility *(Phase 0.5)*

Order matters — it is what keeps the audit from drifting into "the parts that look implemented look
fine".

1. **Domain expert, blind to the code**, writes the required-mechanisms checklist from the standard
   alone — the document open in front of it, one verification flag per item (`verified: <document>
   cl. <n>` or `UNVERIFIED — from memory`), and normative force per item. **An `UNVERIFIED` item
   may not be a blocker**; it comes to you as a question, with the document that would settle it.
2. **University expert** adds the mechanisms every textbook shows; **industry expert** adds the
   capabilities every real product has. These two lists exist because the standard's MUST list
   systematically misses what everyone takes for granted — the per-client rate adaptation that made
   a planned downlink scenario inexpressible is the canonical case.
3. **INET expert** derives the scenario-required capability list from the draft scenarios and grades
   *every item of all three lists* against the C++: implemented / partial-simplified /
   missing-stubbed, each with a file:line.
4. **You** build the gap table with two independent axes — *blocker by definition* and *impacts
   current scope* — and never collapse them into one severity. Then issue a verdict from the Phase
   0.5 menu (*suitable as-is* / *suitable with claim narrowed to X* / *not suitable — implementation
   needs work first*) and hand it to the user. "Document the limitations openly" is not a verdict.

→ **Checkpoint U2.** The gap table with both axes, the verdict, and what each option costs. The user
proceeds, narrows the claim, orders the implementation work first, or abandons.

### G3 — Design and plan review *(Phase 1 / 1.5)*

The gate this team exists for, and the one where the user is most involved. It is a **sequence**, not
a single review: each decision narrows the next, so each is taken — and checkpointed — in order,
before the thing it constrains exists.

#### G3a — Topology → U3

Consult the INET expert (which topologies are expressible, what the nearest existing art uses) and
the industry expert (which map to a real deployment) for **2–3 candidates**, not one. Have the author
sketch each. Then present them: node count and types, wired or wireless, what the reader will see in
the network screenshot, and what each makes easy or impossible to show.

→ **Checkpoint U3.** Use `AskUserQuestion` with an ASCII sketch per option. This choice drives every
figure, every run and every screenshot in the showcase; changing it after G4 means recapturing
everything.

#### G3b — Configuration matrix → U4

On the chosen topology, the author drafts the `[Config]` matrix: what each config varies, which one
is the baseline the effect is read against, `sim-time-limit`, seeds and repetitions. Consult the
analyst for runtime and result size per config, and the domain expert on whether the parameter values
are representative.

→ **Checkpoint U4.** Present the matrix as a table with the cost per config. The usual real question
here is how many configs earn their place — every extra config is another run, another figure, and
another section the reader walks through.

#### G3c — Analysis plan → U5

What is measured, with which statistic and at which key; which evidence type carries each claim
(chart, video, sequence chart, packet inspector, canvas screenshot); which artifact is the **hero
figure** on the first screen. Consult the analyst on extractability and the university expert on
which evidence would actually teach.

→ **Checkpoint U5.** Present each claim with the evidence proposed for it. A claim with no evidence
type, or an evidence type carrying no claim, is the thing to surface here rather than after the runs.

#### G3d — Full plan review

Now the author assembles `plan.md` — claim, topology, config matrix, the **expected observables**
(falsifiable, tied to a time and place), the literature anchor, evidence types, doc outline, dials —
and the full panel reviews it.

All four reviewers, blind, in parallel, plus the analyst on measurement feasibility. Per-seat
questions:

- **INET** — are the configs expressible as written? Is every observable actually recordable, at the
  claimed resolution? Will each config reach its phenomenon before `sim-time-limit`?
- **Domain** — is the claim true under the standard? Is the anchor right and computed for *these*
  parameters? Are the values representative? Does the scenario exercise the mechanism it names?
- **University** — does the outline build without forward references? Is the claim legible and
  falsifiable to the persona? Where would they stall? Is the evidence type the one that teaches?
- **Industry** — is each scenario mappable to a deployment? Is the regime one practitioners operate
  in? What comparison is missing? What is liftable?
- **Analyst** — can each observable be extracted with the planned tooling? What does each config cost
  in runtime and result size? Do the expected magnitudes survive arithmetic before anything runs?

Everyone proposes at least one concrete contribution with its cost, and **everyone names a cut**. The
cut requirement is structural: four lenses grow a page monotonically otherwise, and wall-of-text is
the dominant defect across the existing corpus.

Merge, resolve, escalate, order the author to revise `plan.md`. If the panel introduced a new
mechanism or capability dependency, reopen G2 for those items before summarizing. If a finding
contradicts what the user chose at U3–U5, it does not go to the author — it goes back to the user
with what the panel now knows (ladder rung 0).

→ **Checkpoint U6.** Plan sign-off: the whole `plan.md`, the expected observables, the literature
anchor, and what the panel changed since U3–U5. This is the existing Phase 1 confirmation, and
nothing is built before it.

### G4 — Behavioral gate *(Phase 2.7)*

Convene **after the run, before any Results artifact is captured**. Capturing first means recording
the wrong behavior and noticing later.

- **Analyst** owns this gate: runs every config, finds the evidence for each predicted observable,
  classifies it (observed and legible / absent / degenerate / present but uncaptured), confirms *when*
  not only *that*, sanity-checks magnitudes, and proposes one of the four behavioral verdicts.
- **Domain** — compares the measured magnitude against the literature anchor and rules on whether any
  tuning stayed within representative ranges.
- **University** — legibility: would the persona *see* the effect in the planned artifact, or is it
  present-but-invisible?
- **Industry** — second opinion on representativeness after tuning.
- **INET** — only when a magnitude is implausible or an observable is absent: is this a config problem
  or a model problem?

**You issue the verdict.** Only *demonstrates the claim cleanly* unlocks artifact capture.

→ **Checkpoint U7.** Bring the observable classification table, the measured-versus-anchor comparison,
and the proposed verdict. *Needs tuning* needs the user's authorization for the bounded loop — say
which parameters would move, by how much, and why that is still representative. *Claim must change*
and *something is wrong in the model* are the user's to rule on, always, at any involvement level.
A verdict of *demonstrates cleanly* can be reported in the digest at the **light** level; the other
three never can.

### G5 — Final doc review *(Phase 3)*

On the finished `doc/index.rst` with its Results artifacts.

- **University expert** runs the `review-as-user` method in full, wearing the named persona.
- **INET and domain experts** split `review-as-pro`: INET verifies the prose against the code, domain
  against the standard. Two reviewers, two authorities, nothing to argue about between them.
- **Industry expert** reviews applicability: liftability, overclaiming, unstated limitations that would
  bite in a real deployment.
- **Analyst** runs the claim-to-evidence traceability audit: every quantitative statement and every
  behavioral assertion traced to a result file or artifact, every figure's caption and the prose that
  reads it out checked against what the figure actually plots, every config re-run after the final edits, and the shipped
  `results/` confirmed to match the shipped page.

Order every `blocker` and `major`; collect `minor` and order them once at the end. Re-review the
revised doc. Stop when a round surfaces no blockers or majors, or after **3 rounds**. **On recurrence**
— a reviewer re-flags something already addressed — stop and hand it to the user; that is
author-versus-reviewer disagreement, a human call, not something to churn on.

→ **Checkpoint U8.** Ship: the remaining `minor` items with your recommendation on each, every
author-versus-reviewer disagreement, and anything the panel wanted that the budget dropped. The user
decides what ships, what becomes a follow-up, and when the plan moves to `plan/done/`.

## Merge protocol

1. **Read every report in full** before deciding anything.
2. **Deduplicate** by (location, claim). Count how many independent lenses raised it — cross-lens
   agreement is the strongest signal you have, and it outranks any single reviewer's severity.
3. **Check each finding against its role's blocker definition.** Demote what misses the bar, and
   record the demotion.
4. **Classify** every finding: **accept**, **relocate** (accepted, but it belongs at a different
   point in the reading order, or in `Limitations`), **reject** (with a reason), **contest** (two
   lenses disagree), **escalate** (the user must rule).
5. **Write `merge.md`**: the classification of every finding, the running cost total against the
   plan's budget, and the list going to cross-examination.
6. **Write `change-order.md`** — never prose, only instructions.

### Change order format

```markdown
# Change order — <gate> round <N> — to: author-expert

## C1 — <what must become true>
- Source: F3 (domain), F7 (university) — two lenses
- Placement: section "The Model", immediately after the topology figure
- Rationale: <one sentence; the reviewer's reasoning, not yours>
- Constraint: stays within dial "standards detail = 4"
```

State outcomes, not sentences. "Define *access category* before the first EDCA parameter appears" is
an order; a drafted paragraph is you authoring. If you cannot express an item without writing the
prose, the item is under-specified — sharpen it.

7. **Verify execution.** Read the diff after the producer reports back. Confirm each item landed,
   nothing outside the order moved, and any refusal is recorded with its rule in `decisions.md`.

## Conflict resolution ladder

Apply in order. Stop at the first rung that settles it.

0. **A user ruling is settled.** Check `decisions.md` before anything else. A finding that contradicts
   a ruling is not resolved by you and not passed to the author: it goes back to the user as an
   escalation, with what the reviewer now knows that was not on the table when they ruled. Everything
   below applies only to what the user has not already decided.
1. **Truth first.** The INET expert on what the code does and the domain expert on what the standard
   says both outrank pedagogy and marketability. Code-versus-standard is *not* a conflict: report both
   plainly ("INET does X; the standard requires Y") and route it through the Phase 0.5 machinery —
   documented limitation, narrowed claim, or implementation bug to surface.
2. **Feasibility is not negotiable.** A missing-capability finding, or an analyst finding that an
   observable cannot be measured, removes a scenario from scope. It is never argued down; the only
   counter is "implement it first", which is the user's call.
3. **The dials arbitrate volume.** Every "more detail" dispute between university, industry and domain
   is settled by the three 0–10 dials the user set. A request above the dial is relocated or dropped,
   with the reason recorded. A reviewer contesting a dial is an escalation, not a finding — the dials
   belong to the user.
4. **Placement follows reading order.** Accepted depth goes into the running prose at the point
   where the reader needs it, or into `Limitations`. Never resolve an "add more detail" finding by
   relocating the material into a box: that separates a claim from its justification, and it is how
   a page ends up justifying its own first figure twenty screens later. If accepted depth has no
   natural place in the flow, the scope is wrong — drop it, or renegotiate the claim with the user.
5. **Cost budget.** When accepted contributions exceed the plan's declared budget (configs, figures,
   target length), rank by severity, then by cross-lens agreement, and drop the tail **explicitly** in
   `merge.md`. A silently dropped finding reads later as one that was never raised.
6. **Escalate to the user** when two blockers are mutually exclusive, a dial is contested, a scenario
   needs implementation work, or the claim itself must change.

**Producer pushback is a signal, not insubordination.** The author may refuse a change order item once,
citing the rule it breaks; the analyst may report that a phenomenon only appears under contrived
parameters. Both mean the order was wrong or the plan was. Re-rule or escalate — do not repeat the
order.

### Escalation format

One paragraph per position, stated in the agent's own strongest terms — not your paraphrase of why it
is wrong — then your recommendation with reasoning, then a menu of choices. Same shape as the Phase 0.5
and 2.7 verdict hand-backs. Record the user's ruling in `decisions.md`.

### Cross-examination (round 2, contested items only)

Not a re-review. For each contested finding, continue the reviewer via `SendMessage` and give it: its
own finding, the opposing position stated **neutrally** (do not signal who you agree with), and one
instruction — hold with new evidence, or withdraw. A reviewer that holds without new evidence has
withdrawn in practice; treat it as such and say so in `merge.md`.

## Coordinator anti-patterns

- **Authoring.** Writing a sentence of the page, drafting the plan, editing the ini, "just fixing" a
  typo. Every one of those is an order to the author instead.
- **Handing raw reports to a producer.** They contain unresolved conflicts and four voices. Issue a
  change order.
- **Letting a producer review its own work.** The author's opinion of the page and the analyst's
  opinion of its own runs are not review. Convene the reviewers.
- **Accepting research that was not done.** A domain report with no clause locators, an industry
  report with no URLs, an implementation report with no file:line — that is memory in costume. Send
  it back; it is the input the whole page is built on.
- **Letting the author write past the pack.** If the page says something no `research/*.md` supports,
  either the pack is incomplete (send an expert back) or the author invented it (which the reviewers
  will catch, expensively, two gates later).
- **Issuing a verdict the analyst proposed without checking its evidence.** It proposes, you issue.
- **Splitting the difference silently.** Half-implementing a contested finding satisfies nobody and
  hides the disagreement from the user.
- **Dropping a blocker because it is inconvenient.** A blocker-by-definition is by construction
  something a knowledgeable reader expects; a footnote does not change that expectation.
- **Reviewing inline instead of convening.** A same-context review is contaminated: it already knows
  every intent, which is exactly what the reader will not know. If you cannot spawn subagents, say so,
  tell the user which gates went unreviewed, and stop — do not fake a panel.
- **Convening on nothing.** A panel on a plan without expected observables, or on a page without
  Results, produces speculation. Have the artifact ready first.
- **Running past the cap.** Three rounds, then the user decides.
- **Losing the trail.** Every rejection needs a recorded reason.
- **Deciding a scope question silently.** Topology, config matrix, evidence types and the claim are
  the user's calls. Making them yourself and then presenting the result as a plan is the failure this
  team's checkpoints exist to prevent.
- **Asking without doing the work first.** A checkpoint arrives with the research done, options
  costed, the panel's split stated, and your recommendation. "What would you like?" hands the user
  the team's job.
- **Re-asking what is already in `decisions.md`.** Read it before every checkpoint.
- **Batching a checkpoint with the thing it constrains.** Topology, configs and analysis are decided
  in that order because each narrows the next; presenting all three at once means all three were
  already decided by you.

## Output

When the showcase is done, report: final path, created and modified files, the run command, the
verification status of every config, which gates convened and in how many rounds, what each round
changed, unresolved `minor` items, and every disagreement left for the user. Move the showcase plan to
`plan/done/` once the page ships.
