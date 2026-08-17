# The human gates

An agent that reaches a gate states the choice, states its recommendation, and
waits. It never proceeds on an assumption.

1. **The goal.** A new goal, a priority conflict, or invented work.
2. **The plan.** The architect writes the plan to
   `ai-logs/pending/simu5g-YYYY-MM-DD_<title>.md`. No code before the human
   approves the plan.
3. **Structure and red lines.** A new module, a new gate, a new public
   interface, a new dependency — and every crossing of the Control/Data-plane
   boundary. The architecture auditor reports first; only the human waives a
   red line.
4. **The fingerprint baseline.** Any re-record of
   `simu5g/tests/fingerprint/simulations.csv`, and any statistical baseline.
   The fingerprint analyst explains the change per ingredient first; only the
   human consents.
5. **A commit.** Explicit paths, one step per commit. The human works in the
   same checkout.
6. **A merge to `master`.** Only the human merges.
7. **A large cleanup.** The code quality steward proposes; the human accepts
   the rule into `policy/code-quality-rules.md` before any sweep.
8. **An outward action.** A push, a tag, a release, an upstream bug report to
   the `inet` or `omnetpp` projects — anything that leaves the machine.

The rule of thumb: do not stop for what the code, the plan, or a sensible
default answers. State the assumption and continue. Stop where a wrong guess
is expensive to undo.
