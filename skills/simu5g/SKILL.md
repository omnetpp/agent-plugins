---
name: simu5g
description: Rules for working on the Simu5G project
---

# Project Rules

- When asked to refactor, first read `refactoring.md`
- When running tests or debugging, read `fingerprints.md`
- For coding style and error handling, read `coding_guidelines.md`

# Working with git

- **NEVER** make destructive git operations (reset, rebase, force push, etc.)
  without explicit user consent

- Certain git operations utilize a pager (`less`) or an editor (`vi`). Make sure
  you disable them with setting GIT_EDITOR=true or GIT_PAGER=cat.

- When doing rebase, consult `rebase.md`.

# Refactoring:

- When doing multi-step refactorings, read all .md files for instructions.
  Then, for **EACH** step:

    0. Consult the .cascade/*.md files for instructions
    1. Compile in **DEBUG MODE** (`make MODE=debug`)
    2. Commit the changes
    3. Run fingerprint tests (`cd tests/fingerprint && ./fingerprints -d`)
    4. **DO NOT PROCEED** to the next step until all tests pass
    5. Never update the fingerprint results without explicit user consent
