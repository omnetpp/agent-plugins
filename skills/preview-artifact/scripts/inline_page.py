#!/usr/bin/env python3
"""Turn a locally-built INET/Sphinx documentation page into a single self-contained
HTML file that can be published as a Claude artifact.

The artifact sandbox blocks every external host, so all twelve stylesheets, nine
scripts, the fonts, the figures and any videos have to travel inside the file.
The theme is preserved exactly - this is the built page, not a re-creation.

    python3 inline_page.py <built-index.html> <output.html> [--title "Name"]

Videos are embedded as data URIs. If the page would exceed the artifact size
limit, the videos are re-encoded (smallest first) until it fits; pass
--no-shrink to fail instead of re-encoding.

See ../SKILL.md for the traps this script already handles.
"""

import argparse
import base64
import datetime
import os
import re
import shutil
import subprocess
import sys
import tempfile

DOCS = "https://inet.omnetpp.org/docs/"
GH = "https://github.com/inet-framework/inet/blob/master/"

MIME = {
    ".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf",
    ".eot": "application/vnd.ms-fontobject", ".otf": "font/otf",
    ".svg": "image/svg+xml", ".png": "image/png", ".gif": "image/gif",
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".ico": "image/x-icon",
    ".mp4": "video/mp4", ".webm": "video/webm",
}

CAP = 16 * 1024 * 1024        # hard artifact limit
TARGET = 14 * 1024 * 1024     # aim here, so the result is not borderline
B64 = 4.0 / 3.0               # base64 expansion

# tried in order until the clip fits its share of the budget
LADDER = [(1280, 28), (1280, 32), (960, 32), (960, 36), (720, 38), (640, 42)]

stats = {"css": 0, "js": 0, "fonts": 0, "imgs": 0, "videos": 0,
         "dropped": 0, "links": 0}
notes = []


def datauri_bytes(data, ext):
    return "data:%s;base64,%s" % (MIME.get(ext, "application/octet-stream"),
                                  base64.b64encode(data).decode("ascii"))


_uri_cache = {}


def datauri(path):
    """Cached: an image is often referenced twice (inline, and by its lightbox
    link), and re-encoding the same bytes twice is pure waste."""
    if path not in _uri_cache:
        with open(path, "rb") as fh:
            _uri_cache[path] = datauri_bytes(fh.read(),
                                             os.path.splitext(path)[1].lower())
    return _uri_cache[path]


def strip_query(u):
    return u.split("?")[0].split("#")[0]


def find_html_root(page_html):
    """Walk up from the page to the build root (the directory holding _static)."""
    d = os.path.dirname(os.path.abspath(page_html))
    while d != "/":
        if os.path.isdir(os.path.join(d, "_static")):
            return d
        d = os.path.dirname(d)
    sys.exit("error: no _static/ above %s - is this a built page?" % page_html)


def resolve_asset(base, url):
    clean = strip_query(url)
    cand = os.path.normpath(os.path.join(base, clean))
    if os.path.isfile(cand):
        return cand
    # FontAwesome's all.css asks for ../webfonts/, but the build ships the font
    # files beside the stylesheet; prefer that over leaving empty icon boxes
    alt = os.path.normpath(os.path.join(base, os.path.basename(clean)))
    return alt if os.path.isfile(alt) else None


def inline_css(page_dir, rel):
    path = os.path.normpath(os.path.join(page_dir, strip_query(rel)))
    cssdir = os.path.dirname(path)
    css = open(path, encoding="utf-8").read()

    # the CJK slices point at fonts.gstatic.com, which the CSP blocks; dropping
    # them removes most of a 289 KB stylesheet that could never load anyway
    css = re.sub(r"@font-face\s*\{[^}]*gstatic[^}]*\}", "", css)

    def fix(m):
        quote, url = m.group(1), m.group(2)
        if url.startswith(("data:", "about:", "http:", "https:", "//")):
            return m.group(0)
        target = resolve_asset(cssdir, url)
        if target is None:
            stats["dropped"] += 1
            return "url(about:blank)"
        if os.path.splitext(target)[1].lower() in (".woff", ".woff2", ".ttf", ".otf"):
            stats["fonts"] += 1
        return "url(%s%s%s)" % (quote, datauri(target), quote)

    stats["css"] += 1
    return re.sub(r"url\(\s*(['\"]?)([^'\")]+)\1\s*\)", fix, css)


def inline_js(page_dir, rel):
    path = os.path.normpath(os.path.join(page_dir, strip_query(rel.strip())))
    stats["js"] += 1
    js = open(path, encoding="utf-8").read()
    # jQuery carries a literal U+FFFD in its CSS.escape NUL mapping; the deploy
    # validator rejects that codepoint. The escape is identical inside a string.
    return js.replace("�", "\\uFFFD")


def humanise(name):
    return os.path.splitext(os.path.basename(name))[0].replace("-", " ").replace("_", " ")


# ----------------------------------------------------------------- provenance

def git(path, *args):
    try:
        out = subprocess.run(["git", "-C", path] + list(args),
                             capture_output=True, text=True, timeout=15)
        return out.stdout.strip() if out.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def describe(path):
    """(branch, short-hash, dirty) for a checkout, or None if it is not one."""
    sha = git(path, "rev-parse", "--short", "HEAD")
    if not sha:
        return None
    branch = git(path, "rev-parse", "--abbrev-ref", "HEAD") or "HEAD"
    dirty = bool(git(path, "status", "--porcelain", "--untracked-files=no"))
    return branch, sha, dirty


def find_worktree(page_dir):
    """Walk up from the built page to the checkout that produced it."""
    d = page_dir
    while d != "/":
        if os.path.exists(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    return None


def provenance(page_dir, rel_dir):
    """A colophon naming the exact commits the page was built from.

    A preview that outlives the branch it came from is a liability, so both the
    INET checkout and the separate media repo are stamped.
    """
    root = find_worktree(page_dir)
    if root is None:
        return ""

    rows = []
    inet = describe(root)
    if inet:
        rows.append(("INET", os.path.basename(root), inet))
    # showcase videos and many figures live in the separate media repository,
    # checked out (or symlinked) at <worktree>/media
    media = os.path.realpath(os.path.join(root, "media"))
    if os.path.isdir(media):
        info = describe(media)
        if info and os.path.realpath(media) != os.path.realpath(root):
            rows.append(("media", "inet-framework/media", info))
    if not rows:
        return ""

    def row(label, where, info):
        branch, sha, dirty = info
        flag = ' <span class="ap-dirty">+ uncommitted changes</span>' if dirty else ""
        return ("<div><span class='ap-k'>%s</span> <code>%s</code> @ "
                "<code>%s</code> <span class='ap-w'>(%s)</span>%s</div>"
                % (label, branch, sha, where, flag))

    built = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return (
        "<style>"
        ".artifact-provenance{margin:2.5rem 0 1rem;padding:1rem 0 0;"
        "border-top:1px solid rgba(0,0,0,.12);font:13px/1.7 Roboto,sans-serif;"
        "color:rgba(0,0,0,.54)}"
        ".artifact-provenance code{font-family:monospace;font-size:12px;"
        "background:rgba(0,0,0,.05);padding:1px 5px;border-radius:3px}"
        ".artifact-provenance .ap-k{display:inline-block;min-width:52px;"
        "font-weight:500;color:rgba(0,0,0,.68)}"
        ".artifact-provenance .ap-w{color:rgba(0,0,0,.4)}"
        ".artifact-provenance .ap-dirty{color:#b26500}"
        "</style>"
        '<div class="artifact-provenance">'
        "<div style='margin-bottom:.5rem'>Built from <code>%s</code> on %s</div>"
        "%s</div>" % (rel_dir, built, "".join(row(*r) for r in rows))
    )


# --------------------------------------------------------------- video shrink

def reencode(src, width, crf, out):
    """One ffmpeg pass. Screencasts survive aggressive CRF far better than film."""
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error", "-i", src,
        "-vf", "scale='min(%d,iw)':-2" % width,
        "-c:v", "libx264", "-crf", str(crf), "-preset", "medium",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "48k",
        out,
    ]
    subprocess.run(cmd, check=True)
    return os.path.getsize(out)


def shrink(src, budget, tmpdir):
    """Return bytes of src re-encoded to fit `budget`, or the smallest achievable."""
    best = None
    for i, (width, crf) in enumerate(LADDER):
        out = os.path.join(tmpdir, "%s.%d.mp4" % (os.path.basename(src), i))
        try:
            size = reencode(src, width, crf, out)
        except subprocess.CalledProcessError:
            continue
        if best is None or size < best[0]:
            best = (size, out)
        if size <= budget:
            notes.append("%s re-encoded to %dpx/crf%d (%.1f -> %.1f MB)"
                         % (os.path.basename(src), width, crf,
                            os.path.getsize(src) / 1048576.0, size / 1048576.0))
            return open(out, "rb").read()
    if best is None:
        sys.exit("error: ffmpeg could not re-encode %s" % src)
    notes.append("%s re-encoded as far as the ladder goes (%.1f MB, still over its "
                 "%.1f MB share)" % (os.path.basename(src), best[0] / 1048576.0,
                                     budget / 1048576.0))
    return open(best[1], "rb").read()


def fit_videos(html, paths, allow_shrink):
    """Substitute video placeholders, re-encoding if the page would be too big."""
    if not paths:
        return html

    base = len(html.encode("utf-8"))
    raw = [os.path.getsize(p) for p in paths]
    projected = base + sum(r * B64 for r in raw)

    budgets = None
    if projected > TARGET:
        room = TARGET - base
        if room <= 0:
            sys.exit("error: the page exceeds the limit before any video is added")
        if not allow_shrink:
            sys.exit("error: page would be %.1f MB; re-encoding is disabled"
                     % (projected / 1048576.0))
        if not shutil.which("ffmpeg"):
            sys.exit("error: page would be %.1f MB and ffmpeg is not installed - "
                     "install it, or replace the largest clip with a poster frame "
                     "linking to the docs site" % (projected / 1048576.0))
        allowed = room / B64
        total = float(sum(raw))
        budgets = [allowed * (r / total) for r in raw]
        print("  videos: %.1f MB raw exceeds the %.1f MB available - re-encoding"
              % (sum(raw) / 1048576.0, allowed / 1048576.0))

    tmpdir = tempfile.mkdtemp(prefix="preview-artifact-")
    try:
        for i, path in enumerate(paths):
            if budgets is not None and raw[i] > budgets[i]:
                data = shrink(path, budgets[i], tmpdir)
            else:
                data = open(path, "rb").read()
            html = html.replace("@@VIDEO%d@@" % i,
                                datauri_bytes(data, os.path.splitext(path)[1].lower()))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    return html


# --------------------------------------------------------------------- build

def build(page_html, out_path, title=None, allow_shrink=True):
    root = find_html_root(page_html)
    page_dir = os.path.dirname(os.path.abspath(page_html))
    rel_dir = os.path.relpath(page_dir, root).replace(os.sep, "/")
    repo_dir = rel_dir[:-4] if rel_dir.endswith("/doc") else rel_dir

    s = open(page_html, encoding="utf-8").read()

    styles = [inline_css(page_dir, h) for h in
              re.findall(r'<link rel="stylesheet"[^>]*href="([^"]+)"', s)]
    scripts = [inline_js(page_dir, h) for h in
               re.findall(r'<script[^>]*src="((?!https?:)[^"]+)"', s)]

    head = s[: s.index("<body>")]
    body = s[s.index("<body>") + len("<body>"): s.rindex("</body>")]

    # page_transitions.css starts the document at opacity 0 and depends on a
    # <head> script adding .page-ready. Without these the artifact is BLANK.
    head_inline = [m.group(1) for m in
                   re.finditer(r"<script(?![^>]*src)[^>]*>(.*?)</script>", head, re.S)
                   if "dataLayer" not in m.group(1)]

    body = re.sub(r'<script[^>]*googletagmanager[^>]*>\s*</script>', "", body)
    body = re.sub(r"<script>\s*window\.dataLayer.*?</script>", "", body, flags=re.S)
    body = re.sub(r'<script[^>]*src="[^"]*"[^>]*>\s*</script>', "", body)

    if title is None:
        m = re.search(r"<h1>(.*?)(?:<a class=\"headerlink\"|</h1>)", s, re.S)
        title = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else humanise(rel_dir)

    # Sphinx writes the image path into alt=""; give screen readers something real
    def fix_alt(m):
        notes.append("alt text is a placeholder for %s - improve it by hand"
                     % os.path.basename(m.group(1)))
        return '<img alt="%s"' % humanise(m.group(1))

    body = re.sub(r'<img alt="([^"]*/_images/[^"]+)"', fix_alt, body)

    def local(url, kind):
        path = os.path.normpath(os.path.join(page_dir, strip_query(url)))
        if not os.path.isfile(path):
            sys.exit("error: missing %s %s\n  for videos, the Makefile's copy-media "
                     "target must have run - a bare sphinx-build omits them"
                     % (kind, path))
        return path

    body = re.sub(r'(<img[^>]*\ssrc=")([^"]+)(")',
                  lambda m: "%s%s%s" % (m.group(1),
                                        datauri(local(m.group(2), "image")),
                                        m.group(3)),
                  body)
    stats["imgs"] = body.count("data:image/")

    # Scaled figures are wrapped in a link to the full-size image, and lightbox2
    # binds to it. Left pointing at the docs site that fetch is blocked by the
    # CSP, so the viewer gets a spinner that never resolves and a frozen page -
    # point the link at the embedded copy so zooming works offline.
    body = re.sub(r'(<a[^>]*\shref=")([^"]*_images/[^"]+)(")',
                  lambda m: "%s%s%s" % (m.group(1),
                                        datauri(local(m.group(2), "image")),
                                        m.group(3)),
                  body)

    # videos are deferred: their size decides whether re-encoding is needed
    video_paths = []

    def hold_video(m):
        video_paths.append(local(m.group(2), "video"))
        return "%s@@VIDEO%d@@%s" % (m.group(1), len(video_paths) - 1, m.group(3))

    body = re.sub(r'(<video[^>]*\ssrc=")([^"]+)(")', hold_video, body)
    stats["videos"] = len(video_paths)
    # the theme emits autoplay without muted, which browsers refuse to honour
    body = re.sub(r"<video(?![^>]*\smuted)", "<video muted", body)

    # a download= link does nothing for an artifact viewer; send those files to
    # the repository as ordinary links instead
    body = re.sub(r'href="[^"]*_downloads/[0-9a-f]+/([^"]+)"',
                  lambda m: 'href="%s%s/%s"' % (GH, repo_dir, m.group(1)), body)
    body = body.replace(' download=""', "")

    def absolutize(m):
        attr, url = m.group(1), m.group(2)
        if url.startswith(("http:", "https:", "#", "data:", "mailto:", "javascript:")):
            return m.group(0)
        stats["links"] += 1
        target = os.path.normpath(os.path.join(rel_dir, url)).replace(os.sep, "/")
        return '%s="%s%s"' % (attr, DOCS, target)

    body = re.sub(r'\b(href|action)="([^"]+)"', absolutize, body)

    # Nothing may still point at the local filesystem. Check for *relative* refs
    # rather than the substring "_images/": a click-for-full-size image link is
    # legitimately absolutized to https://inet.omnetpp.org/docs/_images/... and
    # still contains that substring.
    leftover = [u for u in re.findall(
        r'\b(?:src|href|action)="(?!https?:|#|data:|mailto:|javascript:)([^"]*)"', body)
        if not u.startswith("@@VIDEO")]   # video data URIs are substituted later
    assert not leftover, "unresolved local references survived: %s" % leftover[:5]
    assert "download=" not in body, "an inert download= link survived"

    # Stamp the commits this page was built from. It has to land after the last
    # </section> of the article: inserting it before the side-doc-outline div
    # instead drops it into the narrow right-hand column, where it is clipped and
    # shoves the Table Of Contents out of view.
    stamp = provenance(page_dir, rel_dir)
    if stamp:
        anchor = body.find('<div class="side-doc-outline')
        if anchor == -1:
            body += stamp
        else:
            end = body.rfind("</section>", 0, anchor)
            pos = anchor if end == -1 else end + len("</section>")
            body = body[:pos] + stamp + body[pos:]

    parts = ["<title>%s</title>" % title]
    parts += ["<style>\n%s\n</style>" % c for c in styles]
    parts += ["<script>\n%s\n</script>" % j for j in head_inline]
    parts += [
        "<style>\nhtml, body { margin: 0; padding: 0; background: #fff; }\n</style>",
        # backstop: never ship a page that can render invisible
        "<script>document.documentElement.classList.add('page-ready');</script>",
        body,
    ]
    parts += ["<script>\n%s\n</script>" % j for j in scripts]

    html = fit_videos("\n".join(parts), video_paths, allow_shrink)

    assert "@@VIDEO" not in html, "a video placeholder was not substituted"
    assert "�" not in html, "U+FFFD present - the deploy will reject it"
    open(out_path, "w", encoding="utf-8").write(html)

    size = len(html.encode("utf-8"))
    print("wrote %s  (%.2f MB)" % (out_path, size / 1048576.0))
    print("  title: %s" % title)
    print("  css %(css)d  js %(js)d  fonts %(fonts)d  images %(imgs)d  "
          "videos %(videos)d  links %(links)d  dropped-url %(dropped)d" % stats)
    for n in dict.fromkeys(notes):
        print("  note: %s" % n)
    if size > CAP:
        sys.exit("ERROR: still over the 16 MB artifact limit - replace the largest "
                 "clip with a poster frame linking to the docs site")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page", help="built index.html under doc/src/_build/html/...")
    ap.add_argument("out", help="self-contained HTML file to write")
    ap.add_argument("--title", help="artifact title (default: the page's <h1>)")
    ap.add_argument("--no-shrink", action="store_true",
                    help="fail instead of re-encoding oversized videos")
    a = ap.parse_args()
    build(a.page, a.out, a.title, allow_shrink=not a.no_shrink)
