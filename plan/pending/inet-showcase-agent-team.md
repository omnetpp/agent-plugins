# INET Showcase Agent Team

A seven-role multi-agent team for creating new INET showcases in `inet-master`, replacing the
solo run of `skills/inet-showcase-creator`.

## Goal

The current `inet-showcase-creator` skill is a good linear pipeline with human gates, but one
context does all the judging: the same agent that writes the claim also decides whether the
code supports it, whether the standard is respected, whether a student could follow it, and
whether a practitioner would care. Those are four different competencies and the failure modes
they catch are documented in the skill itself (the DHCP lease-expiration near-miss, the
rate-anomaly per-client rate-adaptation gap).

This plan splits those competencies into four blind reviewers and two producers, coordinated by a
decision-only coordinator, and defines *when they convene*, *what they must produce*, and *how
disagreements end*.

## Decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | Agents live in `ai-config/agents/*.md` as first-class Claude Code subagent definitions; installed by symlinking `~/.claude/agents -> ai-config/agents` | Version-controlled with the rest of the AI config; available in every repo; invoked as `subagent_type: inet-expert` |
| D2 | The panel convenes at **five gates**, mapped onto phases that already exist in `inet-showcase-creator` | The seams are already there; adding a gate structure on top costs nothing and reuses the existing verdict machinery |
| D3 | New skill `inet-showcase-team` is the **coordinator charter**; `inet-showcase-creator` stays the authoritative build reference and is not duplicated | The creator skill's 585 lines of conventions and writing principles remain single-sourced |
| D4 | **The coordinator is the main session**, not a subagent | It must interact with the user at every verdict gate, spawn the others, and hold the decision log across the whole job — all things a subagent cannot do well. The `inet-showcase-team` skill is what turns the main session into the coordinator. |
| D5 | **The coordinator produces nothing that ships.** It writes only `merge.md`, `change-order.md`, `decisions.md`, gate verdicts and user escalations | Judging and producing in one seat is what the team exists to break up. The coordinator that drafts a paragraph then rules on the panel's objection to it is reviewing itself. |
| D5a | **Two producers.** `author-expert` owns every artifact that ships or describes what will ship (`brief.md`, `plan.md`, `omnetpp.ini`, `*.ned`, `doc/index.rst`, toctree, figure placement and takeaway sentences). `simulation-analyst` owns running, `results/`, evidence artifacts, recipes, and the observable classification | A clean seam: words and model on one side, runs and evidence on the other. Both are reviewed by the four; neither reviews itself |
| D5b | **Reviewers are report-only**: each writes exactly one file, its own report | No concurrent-edit conflicts; blindness stays intact |
| D5c | Producers are **briefed and persistent** (continued via `SendMessage`); reviewers are **blind and re-spawned fresh** each round | The page keeps one voice and the analyst keeps its run history, while a blind re-read stays honest |
| D5d | Producers receive a **change order**, never the raw review reports | The conflicts are already resolved; four raw voices pull the page apart and re-litigate settled rulings |
| D6a | **The briefing pack.** G1/G2 produce `research/{standards,practice,implementation,measurements}.md`; the author writes the page out of those files and nothing else | Otherwise the author — a fresh agent with no topic knowledge — writes the protocol background from memory, which is fluent, plausible and unverifiable. Research artifacts go to the author; review reports never do |
| D6b | The domain expert **opens the actual standard** (local `~/Documents/ieee802` cache, `pdftotext` extract-then-grep), and flags every item `verified: <doc> cl. <n>` or `UNVERIFIED — from memory`; an UNVERIFIED item may not be a blocker | A confident recollection is indistinguishable from a read clause in a written report, and it can otherwise stop a showcase |
| D6c | The industry expert **searches before it opines**, every gate, with URLs per claim | The field moves; recollection describes the industry of some years ago and is confidently wrong about who ships what |
| D5e | The analyst has **bounded tuning authority**: parameter values in existing configs, inside an authorized loop, within representative ranges, every change logged | Otherwise every *needs tuning* round trips through author + coordinator for a value change, and the loop the creator skill caps at 2–3 rounds never converges |
| D6 | Panelist agent frontmatter **omits `model:`** so each inherits the main conversation's model | The existing Phase 3 rule — reviewers never run on a weaker model than the author — enforced structurally instead of by instruction |
| D7 | Panel artifacts live under `inet-master/plan/pending/showcase-<name>/panel/` | `plan/` is already untracked in `inet-master`, so the paper trail never pollutes the INET repo |
| D8 | Every panelist must name **at least one thing to cut** in every report | A four-lens panel monotonically grows a page unless forced not to; wall-of-text is the single most common defect in the existing 84 showcases |

Not done in a worktree (contrary to the global rule) because the deliverable *is* the installed
config: `~/.claude/agents` must symlink into the main `ai-config` checkout for the team to be
usable at all. Changes are committed with targeted `git add`.

## Roster

**Producers** — write files, briefed, persistent across the job.

| Agent | Owns |
|---|---|
| `author-expert` | `brief.md`, `plan.md`, `omnetpp.ini`, `*.ned`, `doc/index.rst`, toctree wiring, figure placement and takeaway sentences. Writes simple technical English for an international audience; may refuse a change-order item once, citing the rule it breaks |
| `simulation-analyst` | Running every config, `results/`, `.anf`, charts, sequence charts, videos, screenshots, figure/video recipes, the observable classification, and the proposed behavioral verdict |

**Reviewers** — write only their own report, blind, re-spawned fresh each round.

| Agent | Authority — what it is trusted about | Blocker definition (its own lens) |
|---|---|---|
| `inet-expert` | What the INET code *actually does*. Every claim cites `src/inet/...:line` or a NED declaration. | The plan/page asserts behavior the code does not have, or needs a modeling capability INET lacks |
| `domain-expert` | What the **standard** requires (IEEE/IETF/3GPP) and what the **literature** predicts, with clause/RFC citations and computed magnitudes | The plan/page contradicts a MUST/SHALL, or names a protocol while omitting a mechanism a knowledgeable reader expects |
| `university-expert` | Whether the target reader (MSc student / PhD researcher) can follow the story to the claim, and whether the result is reusable in a thesis or paper | A load-bearing prerequisite is missing or out of order, so the persona cannot reach the claim — *not* "I would like more detail" |
| `industry-expert` | Whether a practitioner can map the scenario to a real deployment and lift something out of it | The scenario is unmappable to any real system, or the headline claim would mislead someone making a real engineering decision |
| coordinator (main session) | Merging, conflict resolution, change orders, all user escalation — **and nothing that ships** | — |

## The two gate shapes

**Research gates (G1, G2)** — the experts produce knowledge into `research/*.md`, the coordinator
merges and rules, then the author writes `brief.md` / `plan.md` **out of the pack**.

**Review gates (G3, G4, G5)** — **produce** (author or analyst) → **convene** (reviewers, blind,
parallel) → **merge** (classify every finding) → **resolve** (ladder, cross-examination, escalation)
→ **order** (`change-order.md` to the producer) → **verify** (read the diff; confirm each item landed
and nothing else moved).

The research gates exist as much to build the author's knowledge base as to judge the topic. That is
the answer to "how does the author write about a topic it does not know": it does not write from
memory, it writes from `research/standards.md` (verbatim clause quotes), `research/practice.md`
(sourced deployment facts), `research/implementation.md` (module map and exact parameter names) and
`research/measurements.md` (every number with its provenance). Anything the pack does not support is
a marked gap and a request back to the relevant expert — never a smoothed-over sentence.

## Gate map

| Gate | `inet-showcase-creator` phase | Producer | Reviewers | Coordinator's job |
|---|---|---|---|---|
| **G1 topic brief** | (new — feeds Phase 0) | author writes `brief.md` | all four score the candidate; analyst does a cheap build/runtime check | Merge, order the brief, take it to the user. **The user picks.** |
| **G2 feasibility** | Phase 0.5 | — | domain writes the standard checklist **blind to the code**; university adds "what every textbook shows"; industry adds "what every real product does"; INET derives the capability list and grades all three against the C++ | Build the two-axis gap table, issue the verdict menu, hand back to user |
| **G3 plan review** | Phase 1 / 1.5 | author writes `plan.md` | all four, blind, parallel + analyst on measurement feasibility | Merge, resolve, escalate, order the revision; user confirms |
| **G4 behavioral gate** | Phase 2.7 | analyst runs and classifies | domain checks the anchor and polices honest tuning; university judges legibility; industry judges representativeness; INET called in on absent observables and implausible magnitudes | Issue the 2.7 verdict; only *demonstrates the claim cleanly* unlocks artifact capture; authorize bounded tuning |
| **G5 final doc review** | Phase 3 | author revises the page | university runs `review-as-user`; INET and domain split `review-as-pro` (code-truth vs standard-truth); industry reviews applicability; analyst runs the claim-to-evidence traceability audit | Triage, order, re-review; cap 3 rounds; stop on recurrence |

Three structural improvements fall out of the split rather than being bolted on:

- **G2** — the checklist author never sees the code, which is what prevents the audit drifting into
  "the parts that look implemented look fine". Giving industry the "every real product does this"
  list is aimed squarely at the documented rate-anomaly miss: the standard assumed per-client rate
  adaptation, so no mechanism checklist would ever have surfaced it, but a practitioner names it
  immediately.
- **G4** — the agent that *runs* the simulation is not the agent that *wrote the claim*, so
  "capture it anyway and describe what we hoped to see" has no seat to come from.
- **G5** — the analyst's claim-to-evidence traceability audit is new: every quantitative statement
  in the finished page is traced back to a result file, and every figure's bold takeaway is checked
  against what the figure actually plots. The existing skill only spot-checks.

## Report contract

One markdown file per reviewer per gate per round (and one from the analyst at G4/G5), at a
coordinator-assigned path. Fixed sections: model self-report, verdict (`BLOCK` / `REVISE` /
`ENDORSE`, or the four-way behavioral menu for the analyst at G4), coverage (what was examined
*and what was deliberately not*, so silence is readable), findings, contributions, one cut, out of
scope. Every finding carries: severity, confidence, location, lens rationale, **evidence**, proposed
change, and cost in words/figures/configs/sim-time.

Shared severity vocabulary, so four reports merge mechanically:

| Severity | Meaning | Maps to |
|---|---|---|
| `blocker` | Gate cannot pass until resolved | Phase 0.5 blocker-by-definition, `review-as-pro` Error, `review-as-user` High |
| `major` | Fix before shipping; goes into the change order unless it conflicts | Missing / Medium |
| `minor` | Collect, order once at the end, never loop on | Minor / Low |

## Conflict resolution ladder

1. **Truth first.** INET expert on what the code does, domain expert on what the standard says,
   both beat pedagogy and marketability. Code-vs-standard is *not* a conflict — report both and
   route it through the existing Phase 0.5 machinery.
2. **Feasibility is not negotiable.** A missing capability removes a scenario; the only counter is
   "implement it first", which is a user decision.
3. **The detail dials arbitrate volume.** The three 0–10 dials the user sets in Phase 1 settle every
   university-vs-industry-vs-domain "more detail" dispute. A request above the dial is downgraded or
   dropped, with the reason recorded. Contesting a dial is an escalation, not a finding.
4. **Layer discipline decides placement.** Accepted depth goes into a titled `Details —` /
   `Fine print —` admonition rather than into Layer 1, whose ≤70-word paragraph budget and figure
   cadence are hard constraints. Most "add more" findings are accepted-with-relocation.
5. **Cost budget.** Over budget, rank by severity, then by how many independent lenses asked for the
   same thing; drop the tail explicitly rather than silently.
6. **Escalate** mutually exclusive blockers, contested dials, implementation work, and claim changes —
   one paragraph per position plus a coordinator recommendation, same shape as the existing verdict
   hand-backs.

**Producer pushback is a rung of its own.** The author may refuse a change-order item once, citing
the rule it breaks; the analyst may report that the phenomenon only appears under contrived
parameters. Either means the order was wrong or the plan was — re-rule or escalate, never repeat the
order.

Rounds: round 1 blind and parallel; round 2 is **cross-examination of contested items only**
(the panelist is continued via `SendMessage`, shown the opposing position neutrally, and asked to hold
with new evidence or withdraw); round 3 only re-verifies fixed blockers. Cap 3, stop on recurrence.

## Files

- [x] `ai-config/agents/inet-expert.md`
- [x] `ai-config/agents/domain-expert.md`
- [x] `ai-config/agents/university-expert.md`
- [x] `ai-config/agents/industry-expert.md`
- [x] `ai-config/agents/author-expert.md`
- [x] `ai-config/agents/simulation-analyst.md`
- [x] `ai-config/skills/inet-showcase-team/SKILL.md`
- [x] `ai-config/plan/pending/inet-showcase-agent-team.md` (this file)

## Deployment

```bash
ln -s /home/levy/workspace/ai-config/agents /home/levy/.claude/agents
ln -s /home/levy/workspace/ai-config/skills/inet-showcase-team /home/levy/.claude/skills/inet-showcase-team
```

`~/.claude/skills` currently holds only `codebase-memory`, `graphify`, `grill-me` — the other
`ai-config` skills are not installed there, so the second symlink is the pattern that makes
`inet-showcase-team` (and, if wanted, `inet-showcase-creator`, `review-as-pro`, `review-as-user`)
loadable by name.

## Follow-ups

- The agent names are global once symlinked into `~/.claude/agents`. `domain-expert`,
  `university-expert`, `industry-expert` and `author-expert` are generic enough that the model might
  reach for them outside showcase work; their `description` frontmatter scopes them to panel duty.
  Rename with a `showcase-` prefix if that proves insufficient.
- **Model ownership is the one genuinely arguable seam.** `omnetpp.ini` and `*.ned` are assigned to
  the author on the reading that "the showcase" is the model plus the page, with the INET expert
  reviewing the model and the analyst holding bounded authority over parameter values during tuning.
  The alternative — give the model to the analyst, leave the author purely on prose — is cleaner for
  the tuning loop and worse for coherence between the ini and the text that walks through it. Revisit
  after the first real run if the tuning loop turns out to thrash.
- G1 is only as good as its input: it expects `plan/pending/showcase-topic-catalog.md` and
  `existing-showcase-review.md`, both already present in `inet-master/plan/pending/`.
- First real use should be a topic with a known-good outcome so the panel's calibration can be
  judged against a page whose quality is already known.
