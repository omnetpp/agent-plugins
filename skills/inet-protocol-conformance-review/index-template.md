# Protocol review index — template

One file, at `doc/protocols/index.md`. It is the index of reports and the work queue.

---

```markdown
# INET protocol conformance reviews

Each row is one protocol family, or one slice of a large family. A report reviews the family
against its standards and lists what is missing, partial, or incorrect. The workflow is the
`inet-protocol-conformance-review` skill.

Status values:

| Status | Meaning |
|---|---|
| `not-started` | The family is in the queue. Nothing has been done. |
| `spec-pack` | The spec set is approved. The documents are being collected. |
| `spec-blocked` | A required document cannot be obtained. See the report for what is missing. |
| `in-review` | The scope statement is approved. Enumeration and mapping are running. |
| `reviewed` | The report is complete and signed off. |
| `stale` | The code moved under the report. |
| `method-stale` | The workflow gained a pass this report never had. |
| `spec-stale` | A cited document was obsoleted or updated. |

| Family | Directories under `src/inet/` | Specs | Status | Workflow | Reviewed at | Report |
|---|---|---|---|---|---|---|
| IPv4 | `networklayer/ipv4`, `networklayer/arp` | RFC 791, 792, 826, 1122, 1812, 6864 | `in-review` | — | [ipv4](ipv4/conformance-review.md) |
| MPLS | `networklayer/mpls`, `ldp`, `rsvpte`, `ted`, `pcep` | RFC 3031, 5036, 3209 | `not-started` | — | — |
```

---

## Three kinds of staleness

They demand different work, and that is the useful part. A report does not need re-running from
scratch just because something changed.

| Status | What moved | What to re-run |
|---|---|---|
| `stale` | the code | re-map the affected rows. The enumeration still holds — the specification did not move. |
| `method-stale` | the workflow | only the phases that are new. The enumeration and the mapping still hold. |
| `spec-stale` | a cited document | a real re-run. An obsoleted or updated RFC invalidates the enumeration itself. |

`Reviewed at` holds the commit the review was made against, and `Directories` the exact path list it
covered. Together they let a later check detect code drift. `Workflow` holds the version of the
review process, so method drift is a comparison rather than an archaeology exercise. Do not write
the checks yet — record the data now so they are possible later.

## Ordering the queue

1. User impact first.
2. Spec availability second. A blocked family waits.
3. Implementation age third. Old, rarely touched code hides more.
