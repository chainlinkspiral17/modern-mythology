#!/usr/bin/env python3
"""partition_window_audit.py — an inside wall that runs into a window (pass 438).

Elicia's bungalow: the bathroom partition (x -2.5) ran from the front wall
through the middle of the living-room window — half the window lit the bath,
and the "wallpaper peel" a line cued sat on the partition's end. No gate saw
it: the window was not blocked by furniture, and the partition touched only
walls.

A window here is a thin, glass-named pane at least half a metre wide and 0.4 m
tall, above the floor; a partition is a wall-named slab at most 0.3 m thick
and 1.8 m+ tall. A partition fails when its thickness lies INSIDE the window's
span (8 cm clear of either edge), its end reaches the window's plane (within
0.25 m) and its height overlaps the glass. Uses the box cache. Nonzero exits
on any finding; JUDGED lists the ones that stand, with the reason.

    python3 godot/tools/audit/partition_window_audit.py
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vantage_obstruction_audit as V  # noqa: E402

LOC = os.path.normpath(os.path.join(HERE, "..", "blender", "locales"))
# "locale:partition:window" -> why it stands
JUDGED = {}
WIN = re.compile(r"(^|_)win(dow)?(_|$|\d)|glass|pane", re.I)
NOTWIN = re.compile(r"frame|sill|mullion|muntin|trim|head|casing|curtain|blind|shade|rod|sash_?bar|stool|apron|ledge|reflect|frost|sticker|decal|sign|door|car|truck|van|bus|cab|wind(shield|screen)|bottle|cup|mug|jar|case|cooler|display|counter|shelf|table|aquarium|tank|lamp|bulb|screen|monitor|tv|clock", re.I)
WALL = re.compile(r"wall|partition|divider|pier", re.I)
NOTWALL = re.compile(r"base|trim|tile|paint|art|picture|poster|shelf|sconce|clock|outlet|switch|grime|stain|band|mural|sign|light|lamp|cabinet|cap|chair|rail|paper|peel|plaster|crack|panel_|board", re.I)
out = []
for f in sorted(glob.glob(os.path.join(LOC, "build_*.py"))):
    loc = os.path.basename(f)[6:-3]
    try:
        boxes = V.boxes_for(loc)
    except Exception:
        continue
    if not boxes:
        continue
    wins, walls = [], []
    for n, c, h in boxes:
        if WIN.search(n) and not NOTWIN.search(n):
            t = sorted(range(3), key=lambda i: h[i])
            if t[0] in (0, 1) and h[t[0]] < 0.06 and h[2] > 0.2 and h[1 - t[0]] > 0.25 and c[2] > 0.6:
                wins.append((n, c, h, t[0]))
        if WALL.search(n) and not NOTWALL.search(n) and h[2] >= 0.9:
            t0 = 0 if h[0] < h[1] else 1
            if h[t0] <= 0.15 and h[1 - t0] >= 0.4:
                walls.append((n, c, h, t0))
    for wn, wc, wh, wn_ax in wins:          # wn_ax: the window's normal axis
        span = 1 - wn_ax                    # the axis the window spans along
        for pn, pc, ph, pt in walls:
            if pt != span:                  # partition thin along the window's span = runs along the normal
                continue
            # the partition's thin interval sits inside the window's span (not at its edge)
            p0, p1 = pc[span] - ph[span], pc[span] + ph[span]
            w0, w1 = wc[span] - wh[span], wc[span] + wh[span]
            if not (p0 > w0 + 0.08 and p1 < w1 - 0.08):
                continue
            # its end reaches the window plane
            e0, e1 = pc[wn_ax] - ph[wn_ax], pc[wn_ax] + ph[wn_ax]
            if not (e0 - 0.25 <= wc[wn_ax] <= e1 + 0.25):
                continue
            # heights overlap the glass
            if pc[2] + ph[2] < wc[2] - wh[2] + 0.1 or pc[2] - ph[2] > wc[2] + wh[2] - 0.1:
                continue
            if "%s:%s:%s" % (loc, pn, wn) in JUDGED:
                continue
            out.append("%-28s %-36s through %s" % (loc, pn, wn))
if out:
    print("\n".join(out))
print("partition_window_audit · %d partition(s) through a window" % len(out))
sys.exit(1 if out else 0)
