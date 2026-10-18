---
name: inet-cosmetic-cleanup
description: >
  Cosmetic cleanup of INET (OMNeT++) C++ source files: fix all-caps abbreviation casing in
  identifiers (TCPSendBuffer -> TcpSendbuffer), strip graphical noise from EV log statements,
  delete leftover commented-out code, and make error/exception messages specific and contextual.
  Behavior-preserving, verified by byte-identical fingerprints. Use when asked to clean up, tidy,
  beautify, or do cosmetic / style improvement of an INET .cc/.h source file (e.g. Mipv6.cc), or to
  fix naming / log-noise / dead-comment / error-message smells.
---

# INET cosmetic cleanup

Polish an INET source file by removing cosmetic "smells" **without changing behavior**.

**The governing invariant:** a cosmetic change is behavior-preserving, so **every fingerprint
stays byte-identical**. That is both the goal and the safety net — if a fingerprint moves, the
change was not cosmetic; revert and investigate. It also tells you which renames are safe to
automate (see *Scope tiers*).

## The smells

1. **All-caps abbreviations in identifiers** — capitalize only the first letter of each
   multi-letter abbreviation, so chains of acronyms stay readable.
   - `TCPSendBuffer` -> `TcpSendbuffer`, `IPv6Address` -> `Ipv6Address`, `CNAddress` -> `cnAddress`,
     `BULEntry` -> `bulEntry`, `getHTTPURL()` -> `getHttpUrl()`.
   - **2-letter abbreviations are the exception** — fine to keep both caps (`sendRA()`); leave them
     unless the surrounding code clearly prefers mixed case.
   - **NOT smells, leave alone:** ALL_CAPS constants / macros / enum values
     (`BRR_RETRIES`, `MAX_RR_BINDING_LIFETIME`), preprocessor lines, include guards, and the
     `I`-prefix interface convention (`IInterfaceTable`).
   - Preserve RFC-canonical mixed forms (`HoA`, `CoA`) — don't "normalize" them to `Hoa`/`Coa`.

2. **Graphical noise in log statements** — strip decoration like
   `<<<<<<`, `>>>>>>`, `======`, `######`, `******`, and leading/trailing `\n` art.
   - Keep the *informative* content: `EV << "\n<<==== HoT MESSAGE FORMED; APPENDING CONTROL INFO ====>>\n";`
     -> `EV_INFO << "HoT message formed, appending control info\n";`
   - Pure "entered function X" / "this is where Y happens" traces are low value — **delete them**
     rather than reformat.
   - Downgrade shouty ALL-CAPS prose to normal sentence case; use plain ASCII (no em-dash / Unicode art).

3. **Commented-out code** — delete leftover commented statements, debug `EV`/`bubble`/`printf`
   lines, and dead blocks from old debug sessions. Keep genuine explanatory comments.
   Don't delete a commented line that documents an intentional decision (`// no IKE/IPsec...`).

4. **Uninformative or sloppy error/exception messages** — make every `throw cRuntimeError(...)`
   (and error log) specific and contextual.
   - **No trailing punctuation** — don't end a message with `!` or `.`; fix typos while you're there.
   - **Include the offending value and context** — state *what* was wrong (the concrete value),
     *what* it is / where it came from, and *what operation* was underway. Use cRuntimeError's
     printf-style args to interpolate the actual values.
   - No need to name the enclosing class/module — OMNeT++ prefixes the failing module's path and
     type to the error automatically.
   - Example: `throw cRuntimeError("Unkown value for tokenType!");`
     -> `throw cRuntimeError("Unknown token type %d while handling RR token expiry", (int)tokenType);`

5. **Angry / emotional comments** — debugging-session rants
   (`// WAS SCHEDULED FOR EXPIRY, NOT 2 SECONDS BEFORE!?!?!?`). Delete them; or, if one captures a
   real fact, rewrite it as a neutral factual note.

6. **Tautological / redundant comments** — comments that merely restate what the code plainly does
   (`delete pk; // free up memory`, `i++; // increment i`). Delete them: a comment should explain
   *why*, not narrate the obvious.

## Scope tiers (what is safe to auto-rename)

Renaming is the risky smell because identifiers can be bound outside C++. Triage every rename:

- **Tier 1 — local variables & parameters:** auto-fix; single file, zero external impact.
- **Tier 2 — file-private (static functions, private members/methods, types used only within this
  module's .cc/.h):** rename, then update *all* references (`grep -rn` across the repo) and rebuild.
  C++-only, so no fingerprint impact.
- **Tier 3 — externally-bound names: DO NOT auto-rename.** Propose to the user with the full
  reference list; do them only as a deliberate, fully-coordinated rename. These include:
  - registered class/module names (`Define_Module`, `Register_Class`, `Register_Abstract_Class`)
    tied to NED `@class` / type names;
  - name *strings* for NED params / gates / signals / submodules (`par("x")`, `registerSignal("x")`,
    `getSubmodule("x")`) and anything read from generated `.msg` / `.ned` code;
  - public API used widely across modules.

## Workflow

1. `scripts/find-smells.sh <file>` to list candidates (heuristic — review each, don't apply blindly).
2. Triage: classify every naming candidate by scope tier; separate live vs. commented-out logs.
3. Apply Tier-1/2 renames; strip/delete noisy logs; delete commented-out code. Collect Tier-3 proposals.
4. Build from the **toplevel** project dir (regenerates makefiles): `make MODE=debug -j` (and release).
   See inet-dev-environment for the build rules and the setenv/INET_ROOT check.
5. Run the relevant fingerprint suite and confirm **zero** changes, e.g.
   `cd tests/fingerprint && ./fingerprinttest -d -m <area>` (drop graphical noise with `-F tyf`;
   runner details: inet-fingerprint-testing).
   Any moved fingerprint = a non-cosmetic change leaked in -> investigate.
6. Present Tier-3 rename proposals to the user; apply approved ones with full reference updates,
   then rebuild + re-verify fingerprints.
7. Commit per area: `Area: cosmetics: <what>`, or `Area: cleanup: <what>` when the commit
   mainly removes dead or commented-out code (e.g.
   `Mipv6: cosmetics: tidy log messages, fix abbreviation casing`; markers: dev-commit-messages).

## Why fingerprints can't move

Log edits, comment deletions, and error-message wording are never recorded in fingerprints
(error text only surfaces when the error fires, which is off the tested datapath); Tier-1/2 renames
don't change runtime behavior. The only way a "cosmetic" pass perturbs a fingerprint is by touching a
Tier-3 externally-bound name — which is exactly why those are gated behind explicit approval.
