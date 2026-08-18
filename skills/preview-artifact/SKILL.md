---
name: preview-artifact
description: Publish a locally-built INET/Sphinx documentation page (showcase or tutorial) as a self-contained, shareable Claude artifact that keeps INET's real Material Design theme - inlining every stylesheet, script, font, figure and video. Use when asked to preview, share, or publish a showcase/tutorial page as a link or artifact, to show a built doc page to a reviewer or collaborator, or to get a rendered showcase in front of someone without them building the docs.
---

# INET doc page → artifact preview

Publishes the *actual built page*, not a re-creation: same app bar, drawer,
outline and typography a local `make html` produces.

## Quick start

```bash
# 1. build the page (make html, NOT bare sphinx-build - see traps)
cd <worktree>/doc/src && DOC_BUILD_TARGET=showcases make html \
    SPHINXBUILD="<docvenv>/bin/python -m sphinx"

# 2. inline everything into one file
python3 ~/.claude/skills/preview-artifact/scripts/inline_page.py \
    <worktree>/doc/src/_build/html/showcases/<path>/doc/index.html \
    <scratchpad>/<name>.html

# 3. publish with the Artifact tool (file_path = the output, plus favicon +
#    description). Republishing the same path keeps the same URL.
```

The script prints what it embedded and any warnings. Read them — they flag
placeholder alt text and re-encoded videos.

## Workflow

1. Build with `make html`. If the venv is missing, see the
   `reference-inet-docs-sphinx-build` memory for the recipe.
2. Run the inliner. It fails loudly on a missing asset rather than shipping a
   broken page.
3. Sanity-check the render before publishing — cheap and catches theme
   surprises:
   ```bash
   google-chrome --headless --disable-gpu --no-sandbox --hide-scrollbars \
       --window-size=1400,1100 --virtual-time-budget=8000 \
       --screenshot=shot.png <output>.html
   ```
   Wrap the file in `<html><head>…</head><body>…</body></html>` first; the
   Artifact host supplies that wrapper, a local Chrome does not.
4. Publish. Keep the favicon stable across redeploys of the same page.

## Traps this script already handles

Do not "simplify" these away — each one was a real failure:

- **Blank white page.** `page_transitions.css` sets `html { opacity: 0 }` and
  waits for a `<head>` script to add `.page-ready`. Extract only `<body>` and
  you ship a perfectly correct page that renders as nothing, with no error
  anywhere. The script carries the head scripts across *and* adds a backstop.
- **Deploy rejected: "invalid or unpaired escape sequences".** jQuery contains
  a literal U+FFFD in its `CSS.escape` NUL mapping. Escaped to `�`.
- **289 KB of dead CSS.** `fonts.css` is mostly `fonts.gstatic.com` CJK slices
  the artifact CSP blocks. Those `@font-face` blocks are stripped.
- **Empty icon boxes.** FontAwesome's `all.css` asks for `../webfonts/`, but
  the build ships the fonts beside the stylesheet. Resolution falls back to the
  sibling directory (so the artifact beats the local build here).
- **Dead links.** Every relative href is absolutized to
  `https://inet.omnetpp.org/docs/…` so the drawer and breadcrumb navigate.
- **Inert download links.** Artifact viewers are never granted download
  permission, so `:download:` targets are repointed at GitHub and `download=`
  is dropped. Leaving them trips a publish warning.
- **Figure zoom links must be removed, not repointed.** A scaled figure is
  wrapped in a link to the full-size image, which lightbox2 binds to. Neither
  target works: left pointing at the docs site the fetch is CSP-blocked, so
  clicking gives a spinner that never resolves; pointed at the embedded `data:`
  URI the viewer refuses the link (a `data:` href is a phishing vector) and
  replaces the whole figure — the image with it, since the `<img>` is inside the
  anchor — with a "This content is blocked" box. The wrapper is dropped, so the
  figure renders and clicking it does nothing.

## Provenance stamp

Every page gets a colophon at the end of the article naming the commits it was
built from — the INET checkout (branch, short hash, worktree, plus a warning if
tracked files were modified) and the separate `inet-framework/media` repository,
which is where showcase videos and many figures actually live. A preview
outlives the branch it came from, so a reader must be able to tell what they are
looking at.

It must be inserted after the article's last `</section>`. Putting it before the
`side-doc-outline` div instead drops it into the narrow right-hand column, where
it is clipped and pushes the Table Of Contents out of view.

## Videos

`.. video::` renders to a plain `<video src="media/x.mp4">`, so it embeds
exactly like an image. Three things to know:

- **`make html` is required.** Videos are copied by the Makefile's
  `copy-media` target; a bare `sphinx-build` silently omits them and the
  script will abort on the missing file.
- **Budget.** 16 MB page limit, base64 costs +33%. Across INET's ~196 clips the
  median is 0.32 MB and the 90th percentile 1.75 MB, so a typical page is fine.
  Only `emulation/babel/doc/babel.mp4` (10.4 MB) cannot fit alongside figures.
- **Automatic re-encode.** Over budget, the script gives each clip a
  proportional share and walks a scale/CRF ladder with ffmpeg until it fits.
  Screencasts tolerate this well. `--no-shrink` fails instead; if even the
  ladder is not enough, replace the clip with a poster frame linking to the
  docs site.

The theme emits `autoplay` without `muted`, which browsers refuse to honour —
the script adds `muted` so clips actually play.

## Charts render on a light plate

INET chart PNGs are exported with `savefig.transparent: True`, so their black
axis text disappears on any dark ground. The INET theme is light, so this is
safe here — but it matters for any *custom-styled* page: give every figure an
explicit light background rather than inheriting the page's.
