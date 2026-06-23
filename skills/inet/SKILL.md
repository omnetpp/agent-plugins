---
name: inet
description: Developing INET modules
---

# Plans

Always keep design/implementation plans as Markdown files in a `plan/` folder, 
creating it (`plan/pending/`) if the project has none yet. Follow this 
status-by-folder convention:

- Save a **new plan** in `plan/pending/`.
- When a plan has been **executed to completion**, move it to `plan/done/`
  (e.g. `git mv plan/pending/<name>.md plan/done/<name>.md`).

When implementing a plan, work through it incrementally:

- Ask whether to do the implementation work in a dedicated git worktree or in the main checkout.
- Mark each part done in the plan as you implement it.
- Create a git commit as you complete each step of the plan.
- Update the plan as you go with the actual design decisions and facts discovered during implementation.
- Move the plan to plan/done/ once it is fully implemented.

# Coding guidelines

## Display strings

Every module should display about 2 lines of text above its icon that reflects
its internal state. This string should tell the user a hint on the overall state or activity
of that module: what state it is in, how active it has been, info on what it is currently
doing (if it is relevant), and so on.

It should be based on the displayStringTextFormat NED parameter, whose definition and
handling is inherited from an INET base class (ModuleMixin). The parameter is able to display the values
of watched variables (see WATCH() in C++). The {expr} syntax resolves WATCH variables and
named child objects; dotted submodule paths like {submodule.varName} are also supported.
Example: "sent {numSent} pks\nrcvd {numReceived} pks".
One-letter '%' directives can also be used, but should be treated as legacy for new modules.
The parameter is declared @mutable, so it can be changed at runtime.
Each module type should assign a default format string appropriate for that module type.
If the module does not inherit from ModuleMixin, refreshDisplay() must be overridden manually
to call StringFormat::formatString() and update the display string tag "t".

When figuring out displayStringTextFormat:
- figure out what the module does and what variables would be useful to display
- look at existing WATCHes -- if the needed variables exist as WATCHes, use them
- for missing variables: if the variable can be computed from other variables,
  use WATCH_EXPR() or WATCH_LAMBDA(). If it cannot be computed, consider implementing it
  (add as state variable + WATCH + maintenance code) -- ALWAYS MAKE THE USER EXPLICITLY
  CONFIRM if a new variable is added.

Ideas of what to display for different types of modules:
- apps: send/received number of packets or bytes; number of sessions; connection state;
  other state (like TALK/SILENCE)
- table modules: number of entries (maybe per item type if appropriate)
- routing protocols: number of routing protocol msgs sent/rcvd; number of route changes applied
- generic elements: number of pks send/received (sent up/sent down etc); queue size; etc.
- queue-like elements: queue size (pks/bytes); drop count; etc
- displaying the count of remaining packets/requests etc is usually not enough, because
  it does not tell how many were already done -- both are needed for a good picture


  ## Code documentation

Use Javadoc-style (`/** ... */`) Doxygen comments for:
- **Every major class** — describe what it represents, its role in the architecture, and key
  design aspects.
- **Every method in interface (abstract) classes** — briefly describe important aspects;
  that may include the intended operation, parameters, preconditions, and postconditions.

Implementation class methods generally do NOT need Doxygen comments unless non-obvious.

### Class-level comments

Every class that represents a significant concept (protocol module, data structure,
interface) must have a Doxygen comment immediately before the class declaration.
The comment should state what the class represents and give a brief overview of how
it works. For module classes, include a reference to the NED documentation:
"See the corresponding NED file for more details."

Example (protocol module):
```cpp
/**
 * Implements the TCP protocol. Usage and compliance with various RFCs are
 * discussed in the corresponding NED documentation.
 *
 * **Communication with clients**
 *
 * This section describes the interface between the Tcp module and its clients...
 */
class INET_API Tcp : public TransportProtocolBase
{
  ...
};
```

Related methods in a class can be grouped using the `@name` tag and `//@{ ... //@}`:

```cpp
/** @name Routing functions (query the route table) */
//@{
/**
 * The routing function. Performs longest prefix match...
 */
virtual IRoute *findBestMatchingRoute(const L3Address& dest) const = 0;
...
//@}
```
