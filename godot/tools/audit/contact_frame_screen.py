#!/usr/bin/env python3
"""contact_frame_screen — screen a contact sheet for frames that show
nothing: near-black (a lens outside the lights, a mood that quantises a
dim scene to zero) and near-uniform (a lens pressed against one wall).

The geometry gates judge boxes; this judges the PIXELS the Deck rendered.
2026-09-24's first sheet: 25 near-black frames — whole night beaches
among them (their moon key pointed at the sky) — and a dozen single-
colour inserts the marker audits had passed.

    python3 godot/tools/audit/contact_frame_screen.py [contact_dir]
(default godot/qa/contact). Needs Pillow. Report only — not a gate:
some dark frames are the scene's truth.
"""
import glob, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    try:
        from PIL import Image, ImageStat
    except ImportError:
        print("contact_frame_screen: needs Pillow (pip install pillow)")
        return 2
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.normpath(os.path.join(HERE, "..", "..", "qa", "contact"))
    rows = []
    for f in sorted(glob.glob(os.path.join(root, "*", "*.jpg")) + glob.glob(os.path.join(root, "*", "*.png"))):
        if os.path.basename(os.path.dirname(f)).startswith("_"):
            continue
        im = Image.open(f).convert("L").resize((160, 90))
        st = ImageStat.Stat(im)
        px = list(im.getdata())
        med = sorted(px)[len(px) // 2]
        flat = sum(1 for p in px if abs(p - med) <= 10) / len(px)
        rows.append((os.path.relpath(f, root), st.mean[0], st.stddev[0], flat))
    black = [r for r in rows if r[1] < 6 and r[2] < 6]
    flat = [r for r in rows if r not in black and r[3] >= 0.97 and r[2] < 4]
    print("── NEAR-BLACK (%d) ──" % len(black))
    for r in black:
        print("  %-72s mean %4.1f" % (r[0], r[1]))
    print("── ONE FLAT COLOUR (%d) ──" % len(flat))
    for r in flat:
        print("  %-72s mean %4.1f sd %4.1f" % (r[0], r[1], r[2]))
    print("contact_frame_screen · %d frame(s) · %d near-black · %d flat" % (len(rows), len(black), len(flat)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
