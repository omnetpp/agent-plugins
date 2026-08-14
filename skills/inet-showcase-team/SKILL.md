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
> figure, not a takeaway sentence. The `author-expert` writes; the `simulation-analyst` runs,
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

Work in a dedicated worktree off `inet-master`, not in the main checkout.

## Roster

**Producers** — they write files. They are briefed, not blind: they get the plan, the decisions and
their change order. They persist across the whole job (continue them with `SendMessage`), so the
page keeps one voice and the analyst keeps its run history.

| Agent | `subagent_type` | Owns |
|---|---|---|
| Author | `author-expert` | `brief.md`, `plan.md`, `omnetpp.ini`, `*.ned`, `doc/index.rst`, toctree wiring, figure placement and takeaway sentences |
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

## Workspace

Everything lives outside the INET source tree, under the (untracked) plan folder:

```
inet-master/plan/pending/showcase-<name>/
  brief.md                  G1 output — the approved topic brief          (author)
  plan.md                   claim, scenarios, observables, anchor, outline (author)
  decisions.md              escalations, user rulings, dial settings       (coordinator)
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

## The gate loop

Every gate has the same shape. Do not skip steps or reorder them.

1. **Produce** — the author (or analyst) creates or revises the artifact.
2. **Convene** — spawn the gate's reviewers in parallel, blind.
3. **Merge** — classify every finding; write `merge.md`.
4. **Resolve** — apply the conflict ladder; cross-examine contested items; escalate what is left.
5. **Order** — write `change-order.md` and hand it to the producer.
6. **Verify** — read the diff. Confirm each ordered item landed and nothing else moved. Record
   refusals in `decisions.md`.

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

You merge, then order the author to write `brief.md`: claim candidate, target audience, why this
topic now, top three risks, nearest existing art. **The user picks.** Do not proceed on a topic the
user has not chosen.

### G2 — Feasibility *(Phase 0.5)*

Order matters — it is what keeps the audit from drifting into "the parts that look implemented look
fine".

1. **Domain expert, blind to the code**, writes the required-mechanisms checklist from the standard
   alone, with normative force per item.
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

### G3 — Plan review *(Phase 1 / 1.5)*

The gate this team exists for. The author writes `plan.md`: the claim, the scenario and config
matrix, the **expected observables** (falsifiable, tied to a time and place), the literature anchor,
the evidence types, the doc outline, and the detail dials.

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

Merge, resolve, escalate, order the author to revise `plan.md`, then take it to the user for the
Phase 1 confirmation. If the panel introduced a new mechanism or capability dependency, reopen G2 for
those items before summarizing.

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

**You issue the verdict.** Only *demonstrates the claim cleanly* unlocks artifact capture. *Needs
tuning* authorizes the analyst for a bounded loop — parameter values only, representative ranges only,
two or three rounds — then it comes back. *Claim must change* and *something is wrong in the model*
both exit to the user.

### G5 — Final doc review *(Phase 3)*

On the finished `doc/index.rst` with its Results artifacts.

- **University expert** runs the `review-as-user` method in full, wearing the named persona.
- **INET and domain experts** split `review-as-pro`: INET verifies the prose against the code, domain
  against the standard. Two reviewers, two authorities, nothing to argue about between them.
- **Industry expert** reviews applicability: liftability, overclaiming, unstated limitations that would
  bite in a real deployment.
- **Analyst** runs the claim-to-evidence traceability audit: every quantitative statement and every
  behavioral assertion traced to a result file or artifact, every figure's bold takeaway checked
  against what the figure actually plots, every config re-run after the final edits, and the shipped
  `results/` confirmed to match the shipped page.

Order every `blocker` and `major`; collect `minor` and order them once at the end. Re-review the
revised doc. Stop when a round surfaces no blockers or majors, or after **3 rounds**. **On recurrence**
— a reviewer re-flags something already addressed — stop and hand it to the user; that is
author-versus-reviewer disagreement, a human call, not something to churn on.

## Merge protocol

1. **Read every report in full** before deciding anything.
2. **Deduplicate** by (location, claim). Count how many independent lenses raised it — cross-lens
   agreement is the strongest signal you have, and it outranks any single reviewer's severity.
3. **Check each finding against its role's blocker definition.** Demote what misses the bar, and
   record the demotion.
4. **Classify** every finding: **accept**, **relocate** (accepted, but the depth goes into a Layer-2
   admonition rather than the main flow), **reject** (with a reason), **contest** (two lenses
   disagree), **escalate** (the user must rule).
5. **Write `merge.md`**: the classification of every finding, the running cost total against the
   plan's budget, and the list going to cross-examination.
6. **Write `change-order.md`** — never prose, only instructions.

### Change order format

```markdown
# Change order — <gate> round <N> — to: author-expert

## C1 — <what must become true>
- Source: F3 (domain), F7 (university) — two lenses
- Placement: main flow, section "The Model" | Layer-2 box titled "Details — …"
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
4. **Layer discipline decides placement.** Accepted depth goes into a titled `Details — why …` or
   `Fine print — …` admonition. Layer 1's ≤70-word paragraph budget, figure cadence, and
   one-bold-takeaway-per-figure rule are hard constraints. Most "add more" findings are
   accept-with-relocation.
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

## Output

When the showcase is done, report: final path, created and modified files, the run command, the
verification status of every config, which gates convened and in how many rounds, what each round
changed, unresolved `minor` items, and every disagreement left for the user. Move the showcase plan to
`plan/done/` once the page ships.
