#!/usr/bin/env python3
"""window_backing_audit.py — is there anything BEHIND the glass? (2026-10-07)

The claustrophobia pass found twenty-five rooms whose windows were a
pane laid on a solid wall: glass, frame and mullions on the room face,
the wall unbroken behind them, nothing outside. LocaleGlass makes the
glass transparent at load (2026-10-02) — and through it the player
saw plaster. Every room read sealed. No gate asked.

Every pane (a thin, upright part named *_Glass / *_Pane / *_Warm, or a
make_window see-through glint) is tested against the room's walls: a
full-height wall part in the pane's plane (within PLANE m) that covers
the pane's centre is a SOLID BACKING — the window looks into the wall.
Cut it with make_wall_with_openings and give it an outside
(_props/views.py make_view, or the builder's own D5 band).

    python3 godot/tools/audit/window_backing_audit.py             # every builder
    python3 godot/tools/audit/window_backing_audit.py lena_apartment
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prop_overlap_audit as P  # noqa: E402

PLANE = 0.35        # m · a pane sits on the wall's room face, inset ≤ 0.2
PANE = re.compile(r"(^|_)(glass|pane|warm|glint_\d)$", re.I)
WALL = re.compile(r"^(wall|walls)(_|$)", re.I)
# panes that are MEANT to sit on a wall (a mirror, a framed print's
# glazing, a cabinet's glass door against its own back) are not windows
NOT_WINDOW = re.compile(r"(mirror|frame_glass|print|photo|picture|poster|cabinet|case|cooler|freezer|fridge|"
                        r"door_glass|clock|lamp|bulb|jar|bottle|tank|aquarium|monitor|screen|tv|crt|"
                        r"vitrine|hutch|curio|display|sign|menu|board|meter|gauge|dial|vape|kiosk)", re.I)
# windows that stay solid ON PURPOSE (the liminal threshold the story
# opens when the man in the charcoal suit arrives — a liminal-JSON call)
DELIBERATE = {
    ("ember_ash_office", "CornerAcross"),
    # no camera reaches this house (no preset, no [shot:] marker) —
    # roberts_kitchen is the set the story shoots
    ("roberts_house", "FrontPicWindow"),
    ("roberts_house", "KitchenWin"),
}


def panes_and_walls(loc):
    P.record_builder(os.path.join(P.A.LOCALES, "build_%s.py" % loc))
    panes, walls = [], []
    for n, c, h in P.A.BOXES:
        if WALL.search(n) and 2 * h[2] > 1.5:
            walls.append((n, c, h))
            continue
        if not PANE.search(n) or NOT_WINDOW.search(n):
            continue
        thin = min(h[0], h[1])
        if thin > 0.03 or 2 * h[2] < 0.35 or 2 * max(h[0], h[1]) < 0.0:
            continue
        panes.append((n, c, h))
    return panes, walls


def audit(loc):
    panes, walls = panes_and_walls(loc)
    out, seen = [], set()
    for n, c, h in panes:
        stem = re.sub(PANE, "", n).rstrip("_")
        if (loc, stem) in DELIBERATE or stem in seen:
            continue
        along_x = h[0] >= h[1]            # the pane spans X → it lies in an N/S wall
        for wn, wc, wh in walls:
            w_along_x = wh[0] >= wh[1]
            if w_along_x != along_x:
                continue
            if along_x:
                in_plane = abs(wc[1] - c[1]) <= PLANE + wh[1]
                covers = wc[0] - wh[0] < c[0] < wc[0] + wh[0]
            else:
                in_plane = abs(wc[0] - c[0]) <= PLANE + wh[0]
                covers = wc[1] - wh[1] < c[1] < wc[1] + wh[1]
            covers = covers and wc[2] - wh[2] < c[2] < wc[2] + wh[2]
            if in_plane and covers:
                seen.add(stem)
                out.append((stem, wn, c))
                break
    return out


def main(argv):
    locs = argv[1:] or sorted(os.path.basename(p)[6:-3] for p in glob.glob(os.path.join(P.A.LOCALES, "build_*.py")))
    total = 0
    for loc in locs:
        try:
            bad = audit(loc)
        except Exception as e:  # a builder the recorder can't run is not a window defect
            print("  · %-28s (skipped: %s)" % (loc, type(e).__name__))
            continue
        for stem, wall, c in bad:
            total += 1
            print("  ✗ %-28s %-26s on solid %s at (%.2f, %.2f, %.2f)" % (loc, stem, wall, c[0], c[1], c[2]))
    print("window_backing_audit · %d locale(s) · %d pane(s) on a solid wall" % (len(locs), total))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
