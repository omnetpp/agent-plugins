# Finding classes, impact, and confidence

Three independent fields grade every matrix row. There is no combined score. A reviewer sorts by
impact, and skips everything below high confidence.

## Status

The conformance verdict for one spec feature.

| Status | Meaning | Requires |
|---|---|---|
| `Full` | INET implements the feature as the clause requires. | Evidence that points at the implementing code. No finding ID. |
| `Partial` | The feature exists, but a required element of it is absent. | The absent element named explicitly. |
| `Missing` | The feature is not modeled at all. | A search that shows it is absent, not just hard to find. |
| `Incorrect` | The behavior contradicts a normative statement. | **A reproduction.** See P6. |
| `Suspect` | The behavior probably contradicts a normative statement, and no reproduction exists. | A statement of what was tried and why it did not reproduce. |
| `Simplification` | A deliberate, accepted omission. | A row in `accepted-omissions.md`. **Only the user may assign this.** |
| `Non-gap` | The spec item is obsolete, deprecated, or outside INET's declared scope. | The clause or scope statement that makes it so. |

Rules:

- An agent **proposes** `Simplification`. It never assigns it. The row stays `Missing` or
  `Partial` until the user accepts it into the ledger.
- `Incorrect` without a reproduction is invalid. Downgrade to `Suspect`.
- `Non-gap` needs a source. "It feels outdated" is not a source.

## Impact

What the gap costs a simulation user.

| Impact | Meaning |
|---|---|
| `results` | The gap changes simulation results for a normal configuration. |
| `scope` | The gap blocks a whole class of study, but does not corrupt results the user can run today. |
| `cosmetic` | The gap affects neither results nor the range of possible studies. |

## Confidence

How well the evidence supports the row.

| Confidence | Meaning |
|---|---|
| `high` | The clause was read this run, the code was read, and P7 confirmed the finding. For `Incorrect`, a reproduction also exists. |
| `medium` | One leg is weak: the source is a draft, the code path is complex, or the search for the feature was not exhaustive. |
| `low` | The row rests on inference. Report it, and say what would settle it. |

Read [calibration.md](calibration.md) before you set confidence. It records how often each level
has been wrong.

## Requirement level

`level` comes from the spec text: `MUST`, `SHOULD`, or `MAY`. Keep it. A `MUST` violation outranks
a `SHOULD` violation, and the two must never merge into one severity number.

### Permissive clauses

A `MAY`, and anything from an Informational document, grants latitude rather than imposing an
obligation. It cannot be violated, so it cannot be `Missing`.

- The implementation exercises the permission, or does the thing another permitted way → **`Full`**.
- The implementation cannot exercise it because the surrounding capability is absent → **`Non-gap`**,
  and name the missing capability.

Do **not** reach for `Non-gap` merely because a clause imposes no obligation. `Non-gap` means
obsolete, deprecated, or outside the declared scope. The IPv4 pilot's spot check split on exactly
this point — one reviewer answered `Full` and another `Non-gap` for RFC 1071 §2, and both readings
were defensible. That is why this rule exists.

### Conditional clauses

A `MUST` whose antecedent is false in this model is **`Non-gap`**, not `Missing`. State the
antecedent and say why it does not hold. RFC 1812 §5.3.6 binds only where precedence-ordered queue
service is implemented and enabled. INET implements none, so the rule cannot be broken.

### Clauses with two halves

Many clauses impose two obligations in one sentence: send *this* message **and** discard *that*
datagram. Grade every half, and say in the note which halves you checked. A row is `Partial` when
one half holds and the other does not, however well the first half is implemented.

This produced the pilot's only confirmed wrong row. Watch for a summary containing "and", or naming
two actions.

## Finding identifiers

Format `<FAMILY>-<NNN>`, for example `IPV4-017`.

- Allocated once, in matrix order, at P4.
- Never reused. Never renumbered.
- A row's identity is its spec clause plus its feature name.
- A closed finding keeps its ID and moves to the report's `Closed` section.
