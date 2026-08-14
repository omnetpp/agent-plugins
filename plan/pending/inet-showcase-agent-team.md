# INET Showcase Agent Team

A five-role multi-agent team for creating new INET showcases in `inet-master`, replacing the
solo run of `skills/inet-showcase-creator`.

## Goal

The current `inet-showcase-creator` skill is a good linear pipeline with human gates, but one
context does all the judging: the same agent that writes the claim also decides whether the
code supports it, whether the standard is respected, whether a student could follow it, and
whether a practitioner would care. Those are four different competencies and the failure modes
they catch are documented in the skill itself (the DHCP lease-expiration near-miss, the
rate-anomaly per-client rate-adaptation gap).

This plan splits those competencies into four blind panelists plus a coordinator, and defines
*when they convene*, *what they must produce*, and *how disagreements end*.

## Decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | Agents live in `ai-config/agents/*.md` as first-class Claude Code subagent definitions; installed by symlinking `~/.claude/agents -> ai-config/agents` | Version-controlled with the rest of the AI config; available in every repo; invoked as `subagent_type: inet-expert` |
| D2 | The panel convenes at **five gates**, mapped onto phases that already exist in `inet-showcase-creator` | The seams are already there; adding a gate structure on top costs nothing and reuses the existing verdict machinery |
| D3 | New skill `inet-showcase-team` is the **coordinator charter**; `inet-showcase-creator` stays the authoritative build reference and is not duplicated | The creator skill's 585 lines of conventions and writing principles remain single-sourced |
| D4 | **The coordinator is the main session**, not a subagent | It must interact with the user at every verdict gate, spawn the panelists, and hold the decision log across the whole job — all things a subagent cannot do well. The `inet-showcase-team` skill is what turns the main session into the coordinator. |
| D5 | Panelists are **report-only**: each writes exactly one file (its own report) and never touches the plan, the ini, the NED, or the page | One author voice on the page; no concurrent-edit conflicts; the coordinator applies every accepted change in its own words |
| D6 | Panelist agent frontmatter **omits `model:`** so each inherits the main conversation's model | The existing Phase 3 rule — reviewers never run on a weaker model than the author — enforced structurally instead of by instruction |
| D7 | Panel artifacts live under `inet-master/plan/pending/showcase-<name>/panel/` | `plan/` is already untracked in `inet-master`, so the paper trail never pollutes the INET repo |
| D8 | Every panelist must name **at least one thing to cut** in every report | A four-lens panel monotonically grows a page unless forced not to; wall-of-text is the single most common defect in the existing 84 showcases |

Not done in a worktree (contrary to the global rule) because the deliverable *is* the installed
config: `~/.claude/agents` must symlink into the main `ai-config` checkout for the team to be
usable at all. Changes are committed with targeted `git add`.

## Roster

| Agent | Authority — what it is trusted about | Blocker definition (its own lens) |
|---|---|---|
| `inet-expert` | What the INET code *actually does*. Every claim cites `src/inet/...:line` or a NED declaration. | The plan/page asserts behavior the code does not have, or needs a modeling capability INET lacks |
| `domain-expert` | What the **standard** requires (IEEE/IETF/3GPP) and what the **literature** predicts, with clause/RFC citations and computed magnitudes | The plan/page contradicts a MUST/SHALL, or names a protocol while omitting a mechanism a knowledgeable reader expects |
| `university-expert` | Whether the target reader (MSc student / PhD researcher) can follow the story to the claim, and whether the result is reusable in a thesis or paper | A load-bearing prerequisite is missing or out of order, so the persona cannot reach the claim — *not* "I would like more detail" |
| `industry-expert` | Whether a practitioner can map the scenario to a real deployment and lift something out of it | The scenario is unmappable to any real system, or the headline claim would mislead someone making a real engineering decision |
| coordinator (main session) | Merging, conflict resolution, all writing, all user escalation | — |

## Gate map

| Gate | `inet-showcase-creator` phase | Who | Coordinator's job |
|---|---|---|---|
| **G1 topic brief** | (new — feeds Phase 0) | all four score the candidate | Produce a one-page brief: claim candidate, audience, why now, top risks. User picks. |
| **G2 feasibility** | Phase 0.5 | domain writes the standard checklist **blind to the code**; INET writes the capability list and grades both against C++; university adds "what every textbook shows"; industry adds "what every real product does" | Build the two-axis gap table, issue the existing verdict menu, hand back to user |
| **G3 plan review** | Phase 1 / 1.5 | all four, blind, parallel | Merge, resolve, escalate; finalize claim, scenarios, expected observables, literature anchor, outline |
| **G4 behavioral gate** | Phase 2.7 | INET verifies each observable in the run; domain compares against the literature anchor and polices honest tuning; university judges legibility; industry judges representativeness of parameters | Issue the existing 2.7 verdict; only *demonstrates the claim cleanly* unlocks artifact capture |
| **G5 final doc review** | Phase 3 | university runs `review-as-user`; INET and domain split `review-as-pro` (code-truth vs standard-truth); industry reviews applicability | Triage, fix, re-run; cap 3 rounds; stop on recurrence |

G2's split is the main structural improvement: the checklist author never sees the code, which is
what prevents the audit drifting into "the parts that look implemented look fine". Giving industry
the "every real product does this" list is aimed squarely at the documented rate-anomaly miss —
the standard assumed per-client rate adaptation, so no mechanism checklist would ever have
surfaced it, but a practitioner names it immediately.

## Report contract

One markdown file per panelist per gate per round, at a coordinator-assigned path. Fixed
sections: model self-report, verdict (`BLOCK` / `REVISE` / `ENDORSE`), coverage (what was examined
*and what was deliberately not*, so silence is readable), findings, contributions, one cut, out of
scope. Every finding carries: severity, confidence, location, lens rationale, **evidence**, proposed
change, and cost in words/figures/configs/sim-time.

Shared severity vocabulary, so four reports merge mechanically:

| Severity | Meaning | Maps to |
|---|---|---|
| `blocker` | Gate cannot pass until resolved | Phase 0.5 blocker-by-definition, `review-as-pro` Error, `review-as-user` High |
| `major` | Fix before shipping; coordinator applies unless it conflicts | Missing / Medium |
| `minor` | Collect, apply once at the end, never loop on | Minor / Low |

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

Rounds: round 1 blind and parallel; round 2 is **cross-examination of contested items only**
(the panelist is continued via `SendMessage`, shown the opposing position neutrally, and asked to hold
with new evidence or withdraw); round 3 only re-verifies fixed blockers. Cap 3, stop on recurrence.

## Files

- [x] `ai-config/agents/inet-expert.md`
- [x] `ai-config/agents/domain-expert.md`
- [x] `ai-config/agents/university-expert.md`
- [x] `ai-config/agents/industry-expert.md`
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
  `university-expert` and `industry-expert` are generic enough that the model might reach for them
  outside showcase work; their `description` frontmatter scopes them to panel duty. Rename with a
  `showcase-` prefix if that proves insufficient.
- G1 is only as good as its input: it expects `plan/pending/showcase-topic-catalog.md` and
  `existing-showcase-review.md`, both already present in `inet-master/plan/pending/`.
- First real use should be a topic with a known-good outcome so the panel's calibration can be
  judged against a page whose quality is already known.
