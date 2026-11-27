"""Put a BEFORE and an AFTER screenshot side by side with coloured, labelled header bands.

Usage: compose.py BEFORE.png AFTER.png OUT.png "BEFORE LABEL" "AFTER LABEL"
Labels should name the commit and the media commit, e.g.
"BEFORE: master 22df607673, chart media b63ee34 (2026-06-22)" / "AFTER: <branch>, chart media cd94c73".
"""
import sys
from PIL import Image, ImageDraw, ImageFont

if len(sys.argv) != 6:
    sys.exit(__doc__)
bpath, apath, out, lb, la = sys.argv[1:6]
RED, GREEN, GUTTER, BAND, BORDER = '#fbc4c0', '#bfe8c8', 16, 44, '#999999'
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 17)
shots = [Image.open(bpath).convert('RGB'), Image.open(apath).convert('RGB')]
colw = [s.width + 2 for s in shots]
h = BAND + max(s.height for s in shots) + 2
canvas = Image.new('RGB', (GUTTER + colw[0] + GUTTER + colw[1] + GUTTER, h + 2 * GUTTER), 'white')
d = ImageDraw.Draw(canvas)
x = GUTTER
for shot, w, colour, label in zip(shots, colw, (RED, GREEN), (lb, la)):
    y = GUTTER
    d.rectangle([x, y, x + w - 1, y + BAND - 1], fill=colour)
    d.text((x + 12, y + BAND // 2), label, fill='black', font=font, anchor='lm')
    y += BAND
    d.rectangle([x, y, x + w - 1, y + shot.height + 1], outline=BORDER)
    canvas.paste(shot, (x + 1, y + 1))
    x += w + GUTTER
canvas.save(out)
print(out, canvas.size)
