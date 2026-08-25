# Accepted-omissions ledger — template

One ledger per family, at `doc/protocols/<family>/accepted-omissions.md`.

A row here silences that gap in every future review run. That is why **only the user writes this
file**. An agent proposes a row at the P8 checkpoint and waits.

The format mirrors `doc/architecture/architecture-exceptions.md`, which the enforcement pipeline
already uses.

---

```markdown
# <FAMILY> — accepted omissions

Gaps against the standard that INET does not intend to close. Each row is a decision, not an
oversight. A future conformance review reads this file and does not report these again.

Rules:
- Only a human adds a row. An agent may propose one, in the review report, and wait.
- A row keeps the finding ID it had in the report. IDs are never reused.
- Removing a row means the gap becomes reportable again. Say why in the commit message.

| ID | Spec clause | What is omitted | Why | Decided by | Date |
|---|---|---|---|---|---|
| IPV4-023 | RFC 791 §3.2 | Source routing options are parsed but not acted on. | Out of the declared modeling scope. No INET study needs them, and the routing model has no hook for them. | <name> | 2026-08-25 |
```

---

## What belongs here

A gap that is deliberate, and that stays deliberate.

## What does not belong here

- A gap nobody has decided about yet. That stays `Missing` or `Partial` in the report.
- A bug. Fix it, or record it as a finding.
- A gap that is merely inconvenient to close. Say that in the report, and let the roadmap decide.
