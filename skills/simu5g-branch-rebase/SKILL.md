---
name: simu5g-branch-rebase
description: Rules and methods for rebasing a topic branch to a newer base in the Simu5G project
---

# Project Rules

- For performing a rebase of a topic branch to a newer base,
  read `rebase-procedure.md`. This is the main set of instructions.
- To learn more about what fingerprint tests are, read `fingerprints.md`

# Working with git

- **NEVER** delete or overwrite any branches you didn't create yourself.

- Certain git operations utilize a pager (`less`) or an editor (`vi`). Make sure
  you disable them with setting GIT_EDITOR=true or GIT_PAGER=cat.

- Always take care NOT to stage any merge conflict markers into git commits.

- Never care about any potential .orig or .rej files in the working copy.

- Never "add all files in working copy" to any git commit - there are
  miscellanous untracked files in the repo, leave them untracked.