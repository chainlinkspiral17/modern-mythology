#!/usr/bin/env python3
"""Contact sheets of every HeroImage asset, one sheet per stick/group."""
import json, os, sys, glob
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from preview_hero import render

ROOT = "/home/user/modern-mythology/godot/resources"
OUTDIR = os.path.dirname(os.path.abspath(__file__))

groups = {}
for path in glob.glob(ROOT + "/**/*.json", recursive=True):
    try:
        doc = json.load(open(path))
    except Exception:
        continue
    if not (isinstance(doc, dict) and "layers" in doc and "palette" in doc and "w" in doc):
        continue
    rel = os.path.relpath(path, ROOT)
    parts = rel.split(os.sep)
    # group key: the stick dir (games/vol7/<stick>) or games/<other>
    if len(parts) >= 3 and parts[0] == "games" and parts[1] == "vol7":
        key = parts[2]
    elif len(parts) >= 2 and parts[0] == "games":
        key = parts[1]
    else:
        key = parts[0]
    groups.setdefault(key, []).append((rel, doc))

made = []
for key, items in sorted(groups.items()):
    items.sort()
    tiles = []
    for rel, doc in items:
        try:
            w, h, pal, px = render(doc)
        except Exception as e:
            continue
        scale = max(1, min(3, 480 // max(w, 1)))
        img = Image.new("RGB", (w, h))
        for y in range(h):
            for x in range(w):
                img.putpixel((x, y), pal[px[y * w + x]][:3])
        img = img.resize((w * scale, h * scale), Image.NEAREST)
        # cap tile width
        if img.width > 480:
            img = img.resize((480, int(img.height * 480 / img.width)), Image.NEAREST)
        tiles.append((os.path.basename(rel)[:-5], img))
    if not tiles:
        continue
    cols = 4
    cw = max(t.width for _, t in tiles) + 10
    ch = max(t.height for _, t in tiles) + 26
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cw + 10, rows * ch + 34), (18, 15, 20))
    d = ImageDraw.Draw(sheet)
    d.text((10, 8), "%s · %d assets" % (key.upper(), len(tiles)), fill=(235, 225, 200))
    for i, (name, t) in enumerate(tiles):
        gx = 10 + (i % cols) * cw
        gy = 30 + (i // cols) * ch
        sheet.paste(t, (gx, gy))
        d.text((gx, gy + t.height + 2), name[:34], fill=(200, 190, 175))
    out = os.path.join(OUTDIR, "sheet_%s.png" % key)
    sheet.save(out)
    made.append((out, len(tiles)))
    print("wrote", out, len(tiles), "assets")
print("TOTAL sheets:", len(made))
