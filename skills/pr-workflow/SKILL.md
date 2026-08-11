---
name: pr-workflow
description: >
  Iterate on an open pull request: work in the PR's own git worktree/branch, address review
  feedback with new commits (never amend, never force-push), and answer reviewers with new
  comments (never editing the description or an existing comment) that a human can read. Use
  when asked to work on / continue / update a PR,
  address or respond to review comments or reviewer feedback, push fixes to a PR branch, or reply
  in a PR discussion.
---

# Working on a pull request

## Non-negotiables

1. **Work in the PR's worktree.** Every PR has a dedicated worktree and branch — use it. Never
   commit PR work in the main checkout.
2. **New commits only.** Never `git commit --amend`, `git rebase`, or force-push a branch under
   review. Reviewers rely on "changes since your last review"; rewriting history destroys it and
   invalidates every line comment. History cleanup, if wanted, happens after approval and only
   when the user asks (see the `inet-branch-cleanup` skill).
3. **Add, never edit.** The same rule as commits, applied to the conversation. Post *new*
   comments; never edit the PR description, and never edit an existing comment — yours or a
   reviewer's. People have already read what is there, and GitHub shows an edit as a silent
   in-place replacement, so it rewrites the record rather than extending it. Corrections,
   updates and status all go in a new comment. The one exception is a checklist the user
   explicitly asked you to keep updated in place.
4. **Continue the conversation in the PR**, not just in the terminal. Every point a reviewer
   raised gets an answer in its own thread on GitHub.
5. **Write PR comments for a human.** One to three sentences per thread. See *Comment style*.
6. **No AI attribution.** No `Co-Authored-By: Claude ...` trailer in commit messages, no
   "Generated with Claude Code" footer in PR comments or descriptions. This overrides the
   harness default that adds them.
7. **The conversation name carries the PR number** — `PR <N>: <short topic>`, e.g.
   `PR 1123: airtime fairness`. It's how this session is found later in `/resume`.

## Setup

Set the session name first, before any work:

- Launched with `claude -n 'PR <N>: <topic>'` — already done, nothing to do.
- Otherwise rename in-session if the build offers it (`/rename`); if it doesn't, ask the user
  once to rename the conversation to `PR <N>: <topic>` and carry on — don't block on it.

Then locate the branch and worktree:

```bash
gh pr view <N> --json headRefName,title,url -q '.headRefName'   # the PR's branch
git worktree list                                               # find the matching worktree
```

Convention in this environment: sibling directories like `../inet-pr`, `../inet-pr1122`. `cd`
there and confirm `git rev-parse --abbrev-ref HEAD` matches the PR's head branch **before
editing anything**. If no worktree exists for the branch, ask the user before creating one
(`git worktree add ../<repo>-pr<N> <branch>`).

## Read the conversation first

```bash
gh pr view <N> --comments                  # description + top-level discussion + reviews
gh pr diff <N>                             # what's currently proposed
```

Inline review comments and their resolved state are **not** in `gh pr view`. Get the open ones —
this is the actual to-do list:

```bash
gh api graphql -f query='
query($owner:String!,$repo:String!,$num:Int!){
  repository(owner:$owner,name:$repo){ pullRequest(number:$num){
    reviewThreads(first:100){ nodes{ isResolved isOutdated path line
      comments(first:10){ nodes{ databaseId author{login} body } } } } } }
}' -F owner=<owner> -F repo=<repo> -F num=<N> \
 --jq '.data.repository.pullRequest.reviewThreads.nodes[]
       | select(.isResolved|not)
       | {path, line, id: .comments.nodes[0].databaseId,
          who: .comments.nodes[0].author.login, body: .comments.nodes[0].body}'
```

The `databaseId` of a thread's **first** comment is the reply anchor. Bot reviewers (e.g.
`devin-ai-integration`) wrap their text in HTML comments — read past the marker, and treat bot
findings as claims to verify, not facts.

## The loop

For each round of feedback:

1. Decide per thread: fix it, or explain why not. Don't silently skip one.
2. Make the changes in the worktree; build/test as the project requires.
3. Commit — one commit per logical fix, in the project's normal message style, **no AI trailer**.
4. `git push` (plain, no `--force`). If rejected as non-fast-forward, `git pull --rebase` then
   push again — never force.
5. Reply in each thread, naming the commit that addresses it.
6. Post one top-level comment for the round, summarizing what the new commits do.

Both, not either. A thread reply keeps the line context but renders collapsed under the
reviewer's block, so someone scrolling the Conversation tab sees the commit land with nothing
beside it. The top-level comment is what makes the round visible in the timeline.

```bash
# reply inside a review thread — keeps line context
gh api --method POST repos/<owner>/<repo>/pulls/<N>/comments/<comment_id>/replies -f body='...'

# top-level comment — what shows up in the timeline
gh pr comment <N> --body '...'
```

If the body has backticks, tables or newlines, write it to a file first and pass it as JSON
(`gh api ... --input body.json`), rather than fighting shell quoting. Note that
`gh pr edit`/`gh pr comment` can abort on an unrelated GraphQL projects-classic deprecation
error; `gh api -X POST repos/<owner>/<repo>/issues/<N>/comments` is the reliable path.

Don't resolve threads yourself unless asked — that's the reviewer's call.

## Comment style

A reviewer reads dozens of these. Say what changed and why, then stop.

- **Good:** "Fixed in `a1b2c3d` — the queue was indexed before the classifier ran, so `numGates`
  was still 0."
- **Good (declining):** "Left as is: `Ieee80211Mac` already guards this in `handleUpperPacket`,
  so the extra check would be dead code."
- **Bad:** restating the reviewer's comment, thanking them, bullet-listing the diff, emoji,
  hedging ("I think maybe..."), or a summary of everything else you did.

If you're unsure whether the reviewer's premise is right, say so plainly and ask — one question,
in the thread.

## Finishing

Summarize for the user: which threads you answered, which commits you pushed, and anything you
deliberately declined or left open.
