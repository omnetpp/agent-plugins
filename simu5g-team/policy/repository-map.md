# The repository map

Four repositories sit side by side in one workspace:

| Repository | Role | Written by the team? |
|---|---|---|
| `simu5g` | the 5G/LTE simulator — the work repository | yes |
| `inet` | dependency: the INET Framework | no — read-only |
| `omnetpp` | dependency: the simulation platform | no — read-only |
| `ai-logs` | plans and records | yes |

The dependency direction is `simu5g` → `inet` → `omnetpp`. It never reverses,
and the team never patches a dependency. A bug found in `inet` or `omnetpp` is
reproduced, documented, and reported upstream — gate 8 of
`policy/hitl-gates.md`. Reading dependency source to understand behavior is
always allowed and often necessary.

## Where a work product goes

| Product | Place |
|---|---|
| A plan, not yet done | `ai-logs/pending/simu5g-YYYY-MM-DD_<title>.md` |
| A finished plan | moved to `ai-logs/done/`, same name |
| The spend record | `ai-logs/simu5g-spend.md` |
| Code | its owning folder under `simu5g/src/` |
| A simulation or example config | `simu5g/simulations/` |
| The fingerprint baseline | `simu5g/tests/fingerprint/simulations.csv` |
| A guide | `simu5g/doc/` |
| Role descriptions and team policy | this repository — and no work |

A plan carries its design decisions and discoveries back into itself as the
work proceeds: a plan says why, a commit says what.

The internal layout of `simu5g/src/` belongs to the lead and is not restated
here. The knowledge curator checks this map against the actual checkout and
corrects it.
