# Performing Git Rebase

- When rebase encounters a lots of conflicts that are hard to resolve, a viable
  alternative is this: Do NOT to resolve to the top of master at once, but
  instead do multiple rebase operations, each skipping just a small number of
  commits on the master at once until reaching the top of master.
  When facing difficulties during rebase, ALWAYS STOP AND RECOMMEND THE ABOVE
  SOLUTION to the user.

- Cherry-picking is significantly weaker than rebase (e.g. it does not track file
  renames/moves). When cherry-picking faces conflicts, try rebase instead -- it
  may well succeed without manual conflict resolution.

- The right mindset for conflict resolution: understand the INTENT of the
  original commit, and try to do the same kind of change on the local branch.
  I.e. preserve the intent of the topic branch commits, not their exact text.