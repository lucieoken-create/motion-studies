#!/usr/bin/env python3
"""Trace a picture into flat-colored, outlined pieces for the still life study.

  python3 tools/trace.py photo.jpg still-life/mine.js --name mine

Needs:  pip install numpy pillow opencv-python-headless scikit-image

The steps: flatten the picture into patches of even color, split it into pieces along the color
edges, outline each piece, and write the result as a small JavaScript file the study can load.

Options worth knowing:
  --backdrop dark   the subject sits on a dark background: cut it out and leave the background empty
  --backdrop none   a full scene with no plain background: trace the whole frame (the default)
  --detail N        lower = more, smaller pieces. about 260 suits bold objects, 120 a soft scene
  --smallest N      pieces smaller than this many pixels are merged into a neighbor
  --smooth N        how much brushwork or noise to flatten first. lower keeps more edges
  --lift N          how much to brighten and saturate the colors. 0 = leave them as they are
  --groups FILE     a JSON list of hand-made groups, so parts of the picture break away as units

A group is {"name": "ship", "at": [x, y], "size": [half-width, half-height], "light": [min, max]}.
A piece joins the first group whose oval contains its middle and whose "light" range (0 = black,
1 = white, optional) contains its lightness. Pieces in no group are left loose.
"""
import argparse, json, sys
import numpy as np, cv2
from PIL import Image
from skimage.segmentation import felzenszwalb

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('picture'); ap.add_argument('out')
ap.add_argument('--name', default='mine', help='the name the study will know this picture by')
ap.add_argument('--credit', default='', help='where the picture comes from, written into the file as a comment')
ap.add_argument('--backdrop', choices=['none', 'dark'], default='none')
ap.add_argument('--detail', type=float, default=120); ap.add_argument('--smallest', type=int, default=90)
ap.add_argument('--smooth', type=int, default=14); ap.add_argument('--lift', type=float, default=1.0)
ap.add_argument('--groups', default='')
a = ap.parse_args()

img = cv2.cvtColor(np.array(Image.open(a.picture).convert('RGB')), cv2.COLOR_RGB2BGR)
H, W = img.shape[:2]
flat = cv2.pyrMeanShiftFiltering(img, 8, a.smooth)                      # flatten brushwork into patches of even color
rgb = cv2.cvtColor(flat, cv2.COLOR_BGR2RGB); hsv = cv2.cvtColor(flat, cv2.COLOR_BGR2HSV).astype(int)

keep = np.ones((H, W), np.uint8)                                        # which pixels belong to the subject
if a.backdrop == 'dark':
    green = (hsv[..., 0] > 30) & (hsv[..., 0] < 95)                     # leaves sit close to a dark backdrop, so greens get a gentler cut-off
    keep = ((hsv[..., 2] > 60) | ((hsv[..., 2] > 42) & (hsv[..., 1] > 90)) | (green & (hsv[..., 2] > 40) & (hsv[..., 1] > 60))).astype(np.uint8)
    keep = cv2.morphologyEx(cv2.morphologyEx(keep, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

groups = json.load(open(a.groups)) if a.groups else []
def group_of(cx, cy, light):
    for i, g in enumerate(groups):
        lo, hi = g.get('light', [0, 1])
        if ((cx - g['at'][0]) / g['size'][0]) ** 2 + ((cy - g['at'][1]) / g['size'][1]) ** 2 <= 1 and lo <= light <= hi: return i
    return -1

seg = felzenszwalb(rgb, scale=a.detail, sigma=0.6, min_size=a.smallest) + 1   # split along color edges
seg[keep == 0] = 0
pieces = []
for s in np.unique(seg):
    if s == 0: continue
    n, parts, stats, _ = cv2.connectedComponentsWithStats((seg == s).astype(np.uint8))
    for c in range(1, n):
        area = int(stats[c, cv2.CC_STAT_AREA])
        if area < max(30, a.smallest * .25): continue
        part = (parts == c).astype(np.uint8)
        color = np.median(rgb[part == 1], axis=0)
        light = (float(color.max()) + float(color.min())) / 510
        px = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_RGB2HSV)[0, 0].astype(float)
        px[1] = min(255, px[1] * (1 + .3 * a.lift)); px[2] = min(255, px[2] * (1 + .12 * a.lift) + 10 * a.lift)
        color = cv2.cvtColor(np.uint8([[px]]), cv2.COLOR_HSV2RGB)[0, 0]
        if a.backdrop == 'none': part = cv2.dilate(part, np.ones((3, 3), np.uint8))   # grow a pixel so neighbors meet with no gaps
        edges, _ = cv2.findContours(part, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        outline = cv2.approxPolyDP(max(edges, key=cv2.contourArea), 1.2, True)[:, 0, :]
        if len(outline) < 3: continue
        cx, cy = outline.mean(axis=0)
        pieces.append((area, group_of(cx, cy, light), '%02x%02x%02x' % tuple(int(v) for v in color), outline))
pieces.sort(key=lambda p: -p[0])

rows = ['[%d,"%s",%s]' % (g, col, ','.join(str(int(v)) for xy in pts for v in xy)) for _, g, col, pts in pieces]
with open(a.out, 'w') as f:
    f.write('// A picture for the still life study, as flat-colored pieces. Made with tools/trace.py.\n')
    if a.credit: f.write('// %s\n' % a.credit)
    f.write('// Each piece is [group, color, x, y, x, y, ...]. group is an index into groups, or -1 for a loose piece.\n')
    f.write('(window.STILL_LIFE = window.STILL_LIFE || {})[%s] = {\n  w: %d, h: %d, cutout: %s,\n  groups: %s,\n  pieces: [\n%s\n  ]\n};\n'
            % (json.dumps(a.name), W, H, 'true' if a.backdrop == 'dark' else 'false', json.dumps([g['name'] for g in groups]), ',\n'.join(rows)))

# a quick health check, so a bad trace is caught before anyone looks at it
total = W * H; biggest = pieces[0][0] / total; loose = sum(1 for p in pieces if p[1] < 0)
print(f'{a.out}: {len(pieces)} pieces, largest covers {biggest:.0%} of the picture' + (f', {loose} loose' if groups else ''))
if biggest > .25: print('  warning: one piece covers more than a quarter of the picture. try a lower --detail (about half).')
if len(pieces) > 900: print('  warning: over 900 pieces will be slow to draw. try a higher --detail or --smallest.')
if len(pieces) < 40: print('  warning: very few pieces. try a lower --detail, or --backdrop none if the subject was cut away.')
