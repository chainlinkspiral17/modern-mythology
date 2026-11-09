#!/usr/bin/env python3
"""ceiling_grid_audit.py — ceiling lights sit ON the tile grid (2026-11-09).

The user: "the lights on the roof need to be arranged properly with the
tiles on the roof, not haphazard." A drop ceiling (make_ceiling's GridX /
GridY T-bars, a builder's own Ceiling_Grid / Tin_Rib bars) is a grid of
tiles; a troffer, a flush light, a pendant's canopy, a smoke detector or a
speaker hung from it belongs IN a tile (centred) or, when it is longer than
a tile, centred on the bar between the tiles it spans. One placed by eye
straddles the bars at random — the haphazard ceiling.

For each set: the grid lines (the bars' positions along X and Y, with the
grid's pitch), and every ceiling-mounted fixture (its top within 0.12 m of
the grid's height, its name a light / fixture word). Along each axis a
fixture is ON the grid when its centre is within TOL of a tile centre, or —
when it spans more than one tile on that axis — within TOL of a bar.

    python3 tools/audit/ceiling_grid_audit.py            # every builder
    python3 tools/audit/ceiling_grid_audit.py kwik_stop  # some
    python3 tools/audit/ceiling_grid_audit.py --gate     # nonzero exit on OFF
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vantage_obstruction_audit as VO  # noqa: E402

BAR_X = re.compile(r"(?:Grid_?X|Rib_X)_?-?\d*", re.I)
BAR_Y = re.compile(r"(?:Grid_?Y|Rib_Y)_?-?\d*", re.I)
BAR = re.compile(r"(Ceiling|Ceil).*(Grid|Rib)|_Grid[XY]_|Grid_[XY]_", re.I)
FIX = re.compile(r"troffer|fluor|ceiling_?light|ceil_?light|flush|canopy|light_?panel|lightpanel|"
                 r"smoke|ceiling_?speaker|speaker|sprinkler|downlight|can_?light|recessed|fixture", re.I)
NOT = re.compile(r"_led\b|_led$|_slat|_glow|_tube$|_tube_|_bulb|_cord|_socket|_shade|_cage|_chain|_stem|_wire|_lens|_glint|"
                 r"wall|sconce|desk|floor|table_lamp|stain", re.I)
TOL = 0.06


def grid_of(boxes):
    """{'x': [bar positions], 'y': [...], 'z': height} for the drop-ceiling
    bars: thin (< 6 cm across), long, horizontal, at one height."""
    xs, ys, zs = [], [], []
    for n, c, h in boxes:
        if not BAR.search(n):
            continue
        if h[2] > 0.03:
            continue
        if h[0] < 0.04 and h[1] > 0.4:        # a bar running along Y: its X is a grid line
            xs.append(round(c[0], 3))
            zs.append(c[2])
        elif h[1] < 0.04 and h[0] > 0.4:      # along X: its Y is a grid line
            ys.append(round(c[1], 3))
            zs.append(c[2])
    if len(xs) < 2 or len(ys) < 2:
        return None
    return {"x": sorted(set(xs)), "y": sorted(set(ys)), "z": max(zs)}


def _pitch(lines):
    d = sorted(round(b - a, 3) for a, b in zip(lines, lines[1:]) if b - a > 0.2)
    return d[len(d) // 2] if d else None


def _on_axis(c, half, lines, pitch):
    """None when on the grid, else how far off (m)."""
    if pitch is None:
        return None
    # the bars around the centre
    near = min(lines, key=lambda g: abs(g - c))
    if 2.0 * half > pitch * 1.05:
        # spans tiles: centred on a bar, or centred in a run of whole tiles
        best = abs(c - near)
        k = round((2.0 * half) / pitch)
        if k % 2 == 1:                          # an odd number of tiles: centred in a tile
            best = min(best, abs(abs(c - near) - pitch / 2.0))
        return None if best <= TOL else best
    # inside one tile: its centre on the tile's centre
    off = abs(abs(c - near) - pitch / 2.0)
    return None if off <= TOL else off


def check(boxes):
    g = grid_of(boxes)
    if g is None:
        return None, []
    px, py = _pitch(g["x"]), _pitch(g["y"])
    lo_x, hi_x, lo_y, hi_y = g["x"][0], g["x"][-1], g["y"][0], g["y"][-1]
    out = []
    for n, c, h in boxes:
        if not FIX.search(n) or NOT.search(n) or BAR.search(n):
            continue
        top = c[2] + h[2]
        if abs(top - g["z"]) > 0.12:
            continue
        if not (lo_x - 0.2 <= c[0] <= hi_x + 0.2 and lo_y - 0.2 <= c[1] <= hi_y + 0.2):
            continue                            # under another ceiling
        ox = _on_axis(c[0], h[0], g["x"], px)
        oy = _on_axis(c[1], h[1], g["y"], py)
        if ox is not None or oy is not None:
            out.append((n, c, h, ox, oy))
    return (g, px, py), out


def main():
    want = [a for a in sys.argv[1:] if not a.startswith("-")]
    gate = "--gate" in sys.argv
    locs = want or sorted({f[6:-3] for f in os.listdir(os.path.join(HERE, "..", "blender", "locales"))
                           if f.startswith("build_") and f.endswith(".py")})
    bad = sets = 0
    for loc in locs:
        try:
            boxes = VO.boxes_for(loc)
        except Exception:
            continue
        info, off = check(boxes or [])
        if info is None:
            continue
        sets += 1
        for n, c, h, ox, oy in off:
            print("OFF   %-26s %-40s (%.2f, %.2f)  off by %s%s" % (
                loc, n, c[0], c[1], ("x %.2f " % ox) if ox is not None else "", ("y %.2f" % oy) if oy is not None else ""))
        bad += len(off)
    print("ceiling_grid_audit · %d set(s) with a tile grid · %d fixture(s) off the grid" % (sets, bad))
    return 1 if (gate and bad) else 0


if __name__ == "__main__":
    sys.exit(main())
