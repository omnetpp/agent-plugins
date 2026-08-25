# Conformance report — template

One file per family or slice, at `doc/protocols/<family>/conformance-review.md`. It is a living
document. A fix commit updates it in the same commit.

Copy the structure below. Keep the section order. Keep the column order.

---

```markdown
# <Family> — conformance review

- **Family:** <name>
- **Directories:** `src/inet/<dir>`, `src/inet/<dir>`
- **Specs:** see [spec-manifest.md](spec-manifest.md)
- **Reviewed at:** `<commit>` (<date>)
- **Workflow:** v<n> (<date>)
- **Method:** <N> matrix rows from <M> spec documents. <K> findings. <R> refuted at P7 and
  dropped. <P> errors reproduced. <S> rows spot-checked by <who>, <W> wrong.

## 1. Scope statement

What this family intends to model, and at what fidelity. What it deliberately leaves out.

Cite `doc/src/developers-guide/ch-<name>.rst` for anything the guide already states. Do not
repeat it.

This section decides what counts as a gap. The user approved it at the P2 checkpoint.

## 2. Summary

Three to six sentences. What is solid, what is the largest gap, and what a maintainer should do
first. Name finding IDs.

**Lead with root causes, not with the row count.** One defect commonly spans several requirements,
so counting rows makes the code look worse than it is. "9 root causes" is the honest headline; the
requirement count belongs in the coverage table below. The reader is a maintainer planning work, and
work is planned per root cause.

### Verification coverage

What was checked, and what was not. A reader cannot judge how far to trust a report that does not
say what it left unchecked.

| Status | Rows | Verified | By what | Unverified |
|---|---|---|---|---|
| `Incorrect` | 12 | 12 | reproduced in a simulation (P6) | 0 |
| `Missing`, `Partial` | 65 | 65 | adversarial refutation (P7) | 0 |
| `Full` | 125 | 53 | blind duplication (P7b), two-obligation rows | 72 |
| `Non-gap` | 16 | 16 | blind duplication (P7b) | 0 |

Also state what the completeness critic found: how many requirements P3 had missed. That number is
what says whether the enumeration itself was any good.

Counts by status and impact:

| | `results` | `scope` | `cosmetic` |
|---|---|---|---|
| `Incorrect` | | | |
| `Missing` | | | |
| `Partial` | | | |
| `Suspect` | | | |

## 3. Coverage matrix

One row per spec feature. `Full` rows carry no ID. Every other row carries one.

| ID | Feature | Spec clause | Level | Status | Impact | Confidence | Evidence |
|---|---|---|---|---|---|---|---|
| — | Header checksum | [RFC 791 §3.1](https://www.rfc-editor.org/rfc/rfc791#section-3.1) | MUST | `Full` | — | high | [Ipv4Header.cc:120](../../../src/inet/networklayer/ipv4/Ipv4Header.cc#L120) |
| <a id="ipv4-001"></a>[IPV4-001](#f1) | Reassembly timeout | [RFC 791 §3.2](https://www.rfc-editor.org/rfc/rfc791#section-3.2) | MUST | `Partial` | results | high | [Ipv4.cc:812](../../../src/inet/networklayer/ipv4/Ipv4.cc#L812) |

Group rows under subheadings that follow the spec's own structure, for example
`### 3a. Header format`, `### 3b. Fragmentation`, `### 3c. Options`.

## 4. Findings

One entry per non-`Full` row, in ID order.

### <a id="f1"></a>F1 — Reassembly timeout ignores the TTL bound

[`IPV4-001`](#ipv4-001) · **Status:** `Partial` · **Impact:** `results` · **Confidence:** high · **Level:** MUST
- **Spec:** [RFC 791 §3.2](https://www.rfc-editor.org/rfc/rfc791#section-3.2), "the timer ... SHOULD be at least the TTL of the arriving fragment"
- **Observable:** the node transmits an ICMP Time Exceeded, or the reassembly buffer entry expires
- **Implementation:** [Ipv4.cc:812](../../../src/inet/networklayer/ipv4/Ipv4.cc#L812) uses a fixed `fragmentTimeout` parameter
- **What is missing:** <one or two sentences>
- **Consequence:** <what a simulation gets wrong because of this>
- **P7 verdict:** CONFIRMED — <one line>

Keep each entry short. The matrix carries the census. An entry explains only what the row cannot.

## 5. Defaults and configuration

Parameters whose default disables a spec-mandated or widely deployed behavior. The code here is
conformant. Only the default is questionable, so these stay out of the matrix.

| ID | Parameter | Default | Spec / practice | Consequence |
|---|---|---|---|---|
| IPV4-040 | `Tcp.windowScalingSupport` | `false` | RFC 7323, on by default in Linux | Every default simulation caps the window at 64 KiB. |

## 6. Observations

Implementation defects with no spec content, found while reading. One line each. Not investigated.

- `Ipv4.cc:455` — the loop index may pass the array bound when the option list is empty. Not
  chased. Route to `/code-review`.

## 7. Closed

Findings that a later commit fixed. Never delete a finding. Move it here with its commit.

| ID | Feature | Closed by | Date |
|---|---|---|---|
| IPV4-003 | Broadcast address check | `a1b2c3d4` | 2026-09-01 |

## 8. Accepted omissions

See [accepted-omissions.md](accepted-omissions.md). Rows there are not reported again.
```

---

## Cross-references — everything is a link

A report that makes the reader search is a report nobody checks. Three link kinds, all mandatory.

### 1. Identifiers

Each matrix row carries an anchor in its ID cell, and links on to the finding that explains it:

    | <a id="ipv4-002"></a>[IPV4-002](#f2) | ... |

Each finding heading carries its own explicit anchor, so the link survives a reworded heading:

    ### <a id="f2"></a>F2 — Three legal packets abort the simulation

Every mention of an identifier anywhere in the prose links back to its matrix row:

    [`IPV4-002`](#ipv4-002)

Anchors are lower case. Verify before you commit: every `](#ipv4-nnn)` must have a matching
`<a id="ipv4-nnn">`, exactly one of each.

### 2. Spec clauses

One uniform rule:

    [RFC 1122 §3.2.1.2](https://www.rfc-editor.org/rfc/rfc1122#section-3.2.1.2)

The anchor is `#section-<clause>` with the clause verbatim. Modern RFCs rendered by xml2rfc carry
deep anchors, so `#section-2.1.1` lands exactly. Older text RFCs carry only top-level anchors, and
an unmatched fragment lands at the top of the document — harmless, so do not special-case it. A
clause with no number, as in RFC 792, links to the document with no fragment. An errata reference
links to `https://www.rfc-editor.org/errata/eid<N>`.

For a document that is not an RFC, link to wherever the review can actually reach it, and never to a
paywalled page that returns nothing without a login.

### 3. Evidence

A `file:line` links to the file at that line, relative to the report:

    [Ipv4.cc:282](../../../src/inet/networklayer/ipv4/Ipv4.cc#L282)

The prefix is `../../../` from `doc/protocols/<family>/`. Use the first line of a range for the
anchor. Keep the display text short — the path tail and the line — and put the full path only in
the link target.

### Before you commit

Check all four, and fix what fails:

- every `](#ipv4-nnn)` has exactly one matching anchor,
- every `](#fN)` has exactly one matching anchor,
- every relative file path exists on disk,
- no anchor is defined twice.

A dangling link is worse than no link, because it teaches the reader to stop clicking.

## Writing rules for the report

1. **The matrix is the census.** Every spec feature appears, including the ones INET gets right.
   A report that lists only problems cannot show coverage, and cannot be diffed usefully.
2. **Evidence, not assertion.** A `file:line` or a test name. "Appears to be implemented" is not
   evidence.
3. **Quote the spec only where the wording carries the finding.** A short fragment. Never a
   clause in full, and never a spec PDF's text in bulk.
4. **State the consequence.** A maintainer prioritizes by what a simulation gets wrong, not by
   the clause number.
5. **Keep the method line honest.** It says how many findings were refuted and dropped. That
   number is what makes the surviving ones credible.
