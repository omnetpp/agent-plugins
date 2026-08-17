# Routing

The program manager classifies every task with three questions, in order:

1. **Does the task change code?** If not, it is a Question, a Standards
   question, an Investigation, or a Bug report intake — answered in prose,
   never with a diff.
2. **Does it change module structure, a public interface, the NED parameter
   surface, or anything near the Control/Data-plane boundary?** If yes, it is
   at least an Architecture refactoring.
3. **Is the change meant to change simulation results?** If yes, gate 4 will
   be reached, and the plan names which fingerprints move and why. If not,
   every fingerprint stays byte-identical — a moved fingerprint is a defect,
   not a baseline update.

## The table

Use less when you can; never more without the resource manager's agreement.

| Class | Default team | Target |
|---|---|---|
| Question | program-manager, or the one named expert | 10k |
| Standards question | 3gpp-standards-expert | 20k |
| Investigation | one expert, prose only | 50k |
| Bug report intake | triage-agent | 50k |
| Fingerprint drift triage | fingerprint-analyst | 50k |
| Trivial change | simu5g-lead, code-expert | 30k |
| Bug fix | simu5g-lead, code-expert, test-expert, fingerprint-analyst | 100k |
| Feature | software-architect, simu5g-lead, code-expert, test-expert, fingerprint-analyst, code-reviewer | 400k |
| Architecture refactoring | software-architect, architecture-auditor, simu5g-lead, refactor-expert, fingerprint-analyst, code-reviewer | 600k |
| Wide sweep or rename | simu5g-lead, refactor-expert, fingerprint-analyst | 400k |
| Quality audit | code-quality-steward | 150k |

Performance work has no expert yet: classify it as an Investigation (measure)
followed by a Feature (change), and say so to the human. A release, a result
study, and a licence question likewise wait for their deferred roles; until
then the program manager takes them to the human at gate 1.

## Escalation

A role asks for one more role, or a stronger model, with a one-sentence
reason. De-escalation is always welcome: a grep over a full read, one
fingerprint config over the suite, the lead answering over a fan-out.
