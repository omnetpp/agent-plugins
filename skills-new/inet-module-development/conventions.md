# INET module conventions

## Display strings (status text above module icons)

Every module should display ~2 lines of text above its icon reflecting its
internal state: what state it is in, how active it has been, what it is
currently doing.

Mechanics:

- Base it on the `displayStringTextFormat` NED parameter, inherited from the
  INET base class (`ModuleMixin`); it is `@mutable`, so it can be changed at
  runtime (even from the ini per instance). Each module type should assign a
  default format string appropriate for that type.
- `{expr}` resolves WATCH'd variables and named child objects; dotted
  submodule paths like `{submodule.varName}` are supported. Example:
  `"sent {numSent} pks\nrcvd {numReceived} pks"`.
- **Leading-dot gotcha (OMNeT++ 6):** module-relative paths need a LEADING
  DOT — `{.wlan[0].mib.ssid}`; a bare `{wlan[0].mib.ssid}` resolves relative
  to the top-level network and fails with "Module not found".
- One-letter `%` directives (`%n` name, `%p` path, `%t` text tag, `%s` str())
  exist but are legacy for new modules.
- If the module does not inherit from ModuleMixin, override `refreshDisplay()`
  manually (`StringFormat::formatString()` + display-string tag `t`).
- **Display-only**: `refreshDisplay()` runs under Qtenv, not Cmdenv — a bad
  path won't error in Cmdenv, so verify visually in Qtenv. Never affects
  behavior or fingerprints.

Choosing what to display:

- Look at existing `WATCH()`es first; for computable values add
  `WATCH_EXPR()`/`WATCH_LAMBDA()` in `initialize()`. If a needed value cannot
  be computed from existing state, adding a new state variable requires
  EXPLICIT user confirmation.
- Ideas per module kind — apps: packets/bytes sent+received, sessions,
  connection state; tables: entry counts; routing protocols: protocol
  messages sent/received, route changes applied; queues: length + drop count.
  Show done AND remaining counts — remaining alone gives no sense of
  progress.

## Code documentation (Doxygen)

- Javadoc-style (`/** ... */`) comments for **every major class** (what it
  represents, role in the architecture, key design aspects) and **every
  method of interface/abstract classes** (intended operation, parameters,
  pre/postconditions as relevant).
- Implementation-class methods need comments only when non-obvious.
- Class comments for module classes should end with a pointer to the NED
  documentation: "See the corresponding NED file for more details."
- Group related methods with `/** @name ... */` and `//@{ ... //@}`.
