# Calibration

How often this workflow has been wrong, measured per family. Read this before you assign
confidence values. Update it after every family review.

## Why this file exists

The pilot family has no hand-made report to compare against. Without a measured error rate, a
confidence label is a guess. This file turns it into a record.

## Workflow versions

| Version | Date | What changed |
|---|---|---|
| v1 | 2026-08-25 | The original nine phases. Verified only its accusations: `Incorrect` by reproduction, `Missing` and `Partial` by refutation. |
| v2 | 2026-08-25 | Added P3b completeness critic, P4b catch-up mapping, P7b false-`Full` hunt by blind duplication, the per-obligation `checked:` field with mechanical enforcement, `level` as a separate audit verdict, and a published verification-coverage table. Budget 20 → 32 agents. Driven by the v1 pilot: 64% of rows were never adversarially checked, and the one confirmed error was in that 64%. |

A report records the version that produced it. A family whose report predates a pass is
`method-stale`, and needs only the phases that are new — not a fresh review.

## Method

After P8, the user spot-checks a random sample of matrix rows. For each sampled row they answer:
is the status right, is the clause citation right, is the evidence right?

Sample size: 10 rows for the pilot. For later families, 10 rows, or fewer once the rate is stable
across three families.

**Acceptance bar for the pilot:** 2 or fewer wrong rows out of 10. Above that, repair the
workflow before starting family two.

## Record

| Family | Date | Rows in matrix | Findings | Refuted at P7 | Sampled | Wrong | Notes |
|---|---|---|---|---|---|---|---|
| IPv4 with ARP and ICMP | 2026-08-25 | 287 | 147 | 3 refuted, 7 weakened, 2 miscited | 10 | 1 clear, 1 taxonomy | Self-check, not a human check — see the caveat below |

**Caveat on the pilot number.** The orchestrator that built this workflow also ran its spot check, so
this is a self-check. It is weaker evidence than a human check and the next family should not treat
it as settled. It was made as independent as the setup allows: three fresh agents received only the
requirement and the clause, with the status and the evidence withheld, and derived each answer from
scratch. Their verdicts were then compared with the report's.

**Result: 8 of 10 agreed. Of the two disagreements, one was a real error in the report and one was a
defect in this skill's taxonomy.**

- **A false `Full`.** "Parameter Problem trigger and discard" (RFC 792) was graded `Full` because
  both trigger sites were found and both discard correctly. The blind checker noticed that the
  clause's *other* half — discard on a bad header parameter — is not met: a bad version or short IHL
  is flagged at parse time and then falls through the same `&&` guard that finding F1 is about. The
  row became `Partial` (`IPV4-147`). The mapping agent graded the part of the clause it had gone
  looking for, and did not re-read the clause for the rest.
- **A taxonomy defect,** not a data error. See the permissive-clause rule below.

Both survived six enumeration agents, six mapping agents, a deep pass, and an adversarial refutation
pass. Ten sampled rows then found one. **Extrapolate with care: one error in ten sampled rows is not
one error in the report.** Treat the sample as a floor on the error rate, not a measurement of it.

## Prompt-writing rules learned during the pilot

**Never assert what a document says in an agent's prompt.** Name the topic to cover, and let the
agent read. During the IPv4 pilot the orchestrator's prompt told the ICMP agent that RFC 792
forbids generating errors about broadcast destinations, and asked for a row per prohibition. That
prohibition is in RFC 1122 and RFC 1812, not RFC 792. The agent checked and refused to write the
row. A weaker agent would have written it, and the false row would have carried a citation to a
clause that does not exist.

Write "cover the prohibitions on generating ICMP errors", not "RFC 792 forbids X, Y and Z".

**A stated fact in a prompt must be marked as unverified.** Where the orchestrator has already
looked at the code and wants the agent to start from that, phrase it as "a known starting fact,
which you must verify rather than trust". The pilot used this for the IP option classes, and it
kept the anchoring visible.

## Enumeration convergence — IPv4 pilot

| Pass | Enumerated before | Found missing | Coverage of what it saw |
|---|---|---|---|
| Critic 1 | 210 (of 221 — three documents were omitted from its input) | 193 | 52% |
| Critic 2 | 403 | ~26 real, 35 claimed | ~94% |

**Two rounds did not converge.** The second pass still found whole sections, not stragglers —
RFC 1812 5.3.9 and 5.3.12, and the RFC 1122 3.2.2.8 recipient duties. Plan for a third round on a
document set this size, or say in the report that the enumeration is still open.

The nine-row discrepancy in critic 2 is an orchestrator error, not an agent error: three of the
fifteen manifest documents were left out of the critics' input, so their existing rows were invisible
and the critic reported them as absent. Check the critics' input against the manifest.

## What a wrong row teaches

Record the cause, not just the count. Causes seen so far:

- **A clause with two halves, graded on one.** The IPv4 pilot's only clear error. The mapping agent
  found the behavior it was looking for, marked `Full`, and never re-read the clause for the rest of
  the obligation. Counter-measure: when a summary contains "and" or names two actions, check both,
  and say in the note which halves you checked.
- **A root cause hiding inside an unrelated row.** The same defect surfaced under a feature name
  that gives no hint of it. A per-row search cannot find that. This is what the deep pass and the
  spot check are for.

Typical causes to watch for:

- The agent searched for a feature under one name, and INET calls it another.
- The clause was read in an obsoleted RFC.
- The code path exists but is unreachable in any shipped configuration.
- A test exists that the mapping agent did not find, so a `Missing` should have been `Full`.
