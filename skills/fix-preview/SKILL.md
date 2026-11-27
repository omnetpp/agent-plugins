---
name: fix-preview
description: |
  Show a small fix to an INET showcase or tutorial doc page as one PNG: the page BEFORE on the left
  and AFTER on the right, exactly as the real Sphinx build renders it, with the changed text
  highlighted (red before, green after) and the affected figures/charts in view, opened in eog.
  Use after a wording, number, deleted-note, ini-line or replaced-figure fix to a showcase/tutorial
  page when the user says "show me before and after", "side-by-side preview", "preview the page
  edit", or "as usual" after a doc fix. Not for sharing a page as a link (preview-artifact) and not
  for per-commit history (showcase-previewer).
---

# Before/after preview of a doc page fix

The output is a PNG of the real rendered pages side by side. Do NOT make a Claude artifact or a
hand-designed HTML comparison page; the user rejected both.

Scripts are in `scripts/`; run them with `PY=~/.cache/inet-docreview/venv/bin/python`
(has `websocket-client` and PIL). `W` = the INET worktree, `M` = the media repo/worktree.

## Steps

1. **Pick the media for each side.** AFTER uses the current media (plus any new figure copied
   into the media worktree, uncommitted). When the fix is about text that no longer matches a
   re-rendered chart, BEFORE must show the figures as they were when the old text was written:
   find the commit with `git -C $M log -- showcases/<area>/<name>/doc/<figure>.png`, then
   `git -C $M worktree add ~/media-verify-old <sha>` and build BEFORE with that media.
2. **Build both sides** (podman, incremental, ~7 s after the first build; `export UCX_VFS_ENABLE=n`
   is harmless). If the edits are uncommitted, never `git stash` (the stash is shared by all
   worktrees). Instead:
   ```
   cp <edited files> $SCRATCH/ && git -C $W checkout -- <edited files>
   doc/src/build --only showcases --media <old-or-current media> --out doc/site-before --quiet
   cp $SCRATCH/<edited files> back into place
   doc/src/build --only showcases --media $M --out doc/site-after --quiet
   ```
   Pages land at `<out>/docs/showcases/<area>/<name>/doc/index.html` (tutorials analogously).
3. **Serve each site** in the background and keep the PIDs:
   ```
   python3 -m http.server 8811 -d doc/site-before >/dev/null 2>&1 & B=$!
   python3 -m http.server 8812 -d doc/site-after  >/dev/null 2>&1 & A=$!
   ```
4. **Screenshot each side** (same START/END anchors on both, so the crops line up):
   ```
   $PY scripts/shot.py URL "PHRASE1|PHRASE2" "#fbc4c0" before.png "START_TEXT" "END_TEXT" [BLOCK_SELECTOR]
   $PY scripts/shot.py URL "PHRASE1|PHRASE2" "#bfe8c8" after.png  "START_TEXT" "END_TEXT" [BLOCK_SELECTOR]
   ```
   The crop runs from the first paragraph/heading/list item containing START_TEXT to the first one
   after it containing END_TEXT (1440 px viewport, 24 px padding). Choose anchors so the crop
   includes the changed figure. BLOCK_SELECTOR outlines and fills whole blocks, e.g.
   `.admonition.note` for a deleted note, `img[src*="elog2"]` for a replaced figure.
   Then `kill $B $A`.
5. **Compose:**
   ```
   $PY scripts/compose.py before.png after.png <W>/<page>-fix-before-after.png \
     "BEFORE: master 22df607673, chart media b63ee34 (2026-06-22)" "AFTER: <branch>, chart media cd94c73"
   ```
   Labels name the INET commit/branch and the media commit of each side. Save the PNG in the INET
   worktree root (untracked), not inside `doc/`.
6. **Check, then show.** Read the PNG yourself: are the highlights on the changed text, is the
   changed figure inside the crop? Then open it:
   `pkill -x eog; (eog FILE >/dev/null 2>&1 &)` — without the `pkill -x eog`, an old eog window
   keeps showing a stale image.

## Gotchas

- A phrase must lie within ONE DOM text node. Inline roles (`:ned:`, `:par:` become `<a><code>` /
  `<code>`) split text, so mark the pieces separately (e.g. `XMac|LMac|lowest| values up until 120ms`).
- Spaces in a phrase match any whitespace (source line breaks survive in the HTML).
- On "phrase not found", fix the phrase; do not drop it. An empty PHRASES (`""`) is fine for a
  side whose only change is a block (deleted note).
- Sphinx renames images on name clashes (`throughput1.png`), so match images by substring.
- Never `pkill -f <pattern>` when the pattern also matches the invoking shell's command line (it
  killed the shell, exit 144). Start servers in the background and `kill $PID`.
- Numbers in a wording fix come only from data the text already shows; keep fixes minimal.
- Commit only when the user says so; no Co-Authored-By trailers.
- A new sequence-chart figure comes from the OMNeT++ IDE MCP server (`omnetpp-ide-mcp` skill);
  that is out of scope here.
