---
name: inet-module-development
description: >
  Developing protocol modules and models inside the INET Framework: coding/documentation
  conventions (display strings, Doxygen), how-to recipes (new signals, configurator
  facilities), integration patterns (fingerprint-inert node integration, dual-stack design,
  porting protocols from older codebases), and cross-cutting INET gotchas. Use when writing,
  extending, porting, or reviewing INET C++/NED/MSG module code. Generic model-code rules:
  see omnetpp-model-coding-conventions.
---

# INET module development

Applies on top of omnetpp-model-coding-conventions. Reference files:

- [conventions.md](conventions.md) — display strings (`displayStringTextFormat`),
  Doxygen documentation rules.
- [recipes.md](recipes.md) — add a new signal (3 coordinated steps),
  network-configurator facilities worth knowing.
- [integration-patterns.md](integration-patterns.md) — adding a protocol to
  node types without disturbing anything (fingerprint-inert), dual-stack
  (IPv4+IPv6) design, message/serializer rules, porting from older
  INET-based codebases (ANSA etc.).
- [gotchas.md](gotchas.md) — cross-cutting INET traps (configurator wiring,
  IPv6 asymmetries, reserved names).

## Working principles

- **A working example RUN is the verification gate for each development
  phase — compile-green is insufficient.** Each phase's example must actually
  form adjacencies / install routes / deliver pings before the phase is
  committed.
- **Widen scenario coverage to flush latent bugs.** A single-topology example
  hides bugs that multi-node, multi-session, TCP-under-mobility, repeated-
  handover, and return-to-start scenarios expose. Prefer several small
  configs over one demo.
- **Keep mirrored modules in lockstep.** Some INET modules are deliberate
  line-for-line mirrors across address families (e.g. `Igmpv3` ↔ `Mldv2`,
  RFC 3376 ↔ RFC 3810: state machines, fields, and method names align 1:1).
  Any behavioral change to one MUST be mirrored to the other in the same
  session, as paired commits. (Older-version peers like `Igmpv2`/`Mldv1` are
  separate interop modules — do NOT fold them in.)
- **Fix latent upstream bugs as you encounter them** (uninitialized fields,
  dangling pointers) and note them — porting and refactoring regularly
  surface real pre-existing bugs.
- **Green at every commit**: every commit builds (debug) and its own tests
  pass; module tests and the full fingerprint suite run at the branch tip
  (see omnetpp-model-git-workflow). Unrelated fingerprints stay
  byte-identical.
