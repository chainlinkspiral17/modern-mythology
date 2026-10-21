#!/usr/bin/env python3
"""room_crowding_audit.py — which rooms are cramped? (2026-10-21) A report.

The Deck: "Certain interiors look poorly arranged and cramped." The store
gate (walkway_audit) measures lanes between shop fixtures; nothing measured
a living room, a bedroom or an office. This does, for every set with a
floor at z 0:

  floor     the room's floor area (the Floor boxes at grade), m²
  filled    the share of that floor taken by anything standing in a
            person's body height (from 0.12 m to 1.2 m above the floor:
            furniture, counters, table tops, walls' own thickness inside
            the floor's outline)
  walk      the share of the floor a person can actually move through —
            the free floor shrunk by a body's half-width (0.28 m), every
            piece of it a person can stand in (>= 0.25 m² once shrunk),
            grown back. A room you cannot cross
            without brushing furniture scores low here even when `filled`
            looks modest: the furniture is spread so the lanes between
            it are all narrower than a body.
  pinch     pairs of floor-standing pieces 0.10-0.55 m apart (a gap you
            turn sideways through, or can't): the squeezes.

Rooms are ranked by story lines played × crowding, most-played and
tightest first. No gate: it is the drafting program's queue for the
re-plan pass (CLAUDE.md, BUILD BIG: enlarge the room before shaving the
furniture).

    python3 godot/tools/audit/room_crowding_audit.py               # all
    python3 godot/tools/audit/room_crowding_audit.py lena_apartment
    python3 godot/tools/audit/room_crowding_audit.py --json out.json
"""
import glob
import json
import os
import re
import sys
from collections import deque

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
GODOT = os.path.abspath(os.path.join(HERE, "..", ".."))
BUILDERS = os.path.join(GODOT, "tools", "blender", "locales")

CELL = 0.05          # m · grid
BODY_R = 0.28        # m · half a person's shoulder width
BAND = (0.12, 1.20)  # m above the floor · the body's height band
FLOOR_RE = re.compile(r"(^|_)(floor|slab|deck|carpet|vinyl|linoleum|tile_?floor)($|_)", re.I)
NOT_FLOOR_RE = re.compile(r"(floor_?(lamp|plant|safe|tom|board|vent|drain|stain|mat)|seam|joint|grid|crack|stain|wear|rug|runner|mat\b)", re.I)
SKIP_RE = re.compile(r"(rug|runner|mat$|_mat_|wear|stain|threshold|cord|cable|shadow|glow|light_pool|pool|decal|"
                     r"seam|grid|joint|crack|sheen|scuff|spill|puddle|dust|chalk|hair|paper|sheet_\d|tape|"
                     r"view_|thru_|ground|lawn|street|walk_|sidewalk|curb|far|band|sky|backdrop|"
                     r"air_|shimmer|beam_light|god_?ray|fog|steam|smoke|mist)", re.I)
PINCH = (0.10, 0.55)


def _floor_boxes(boxes):
    out = []
    for n, c, h in boxes:
        if not FLOOR_RE.search(n) or NOT_FLOOR_RE.search(n):
            continue
        top = c[2] + h[2]
        if -0.08 <= top <= 0.12 and (2 * h[0]) * (2 * h[1]) >= 1.5 and h[2] <= 0.25:
            out.append((n, c, h))
    return out


def _erode(m, r_cells):
    """Binary erosion by a disc, with plain numpy shifts."""
    out = m.copy()
    H, W = m.shape
    for dy in range(-r_cells, r_cells + 1):
        for dx in range(-r_cells, r_cells + 1):
            if dx * dx + dy * dy > r_cells * r_cells:
                continue
            sh = np.zeros_like(m)
            ys0, ys1 = max(0, dy), H + min(0, dy)
            xs0, xs1 = max(0, dx), W + min(0, dx)
            sh[ys0:ys1, xs0:xs1] = m[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
            out &= sh
    return out


def _dilate(m, r_cells):
    return ~_erode(~m, r_cells)


def _components(m, min_cells):
    """Every 4-connected piece of m with at least min_cells cells (a set
    with several rooms behind closed doors has one piece per room)."""
    H, W = m.shape
    seen = np.zeros_like(m)
    out = np.zeros_like(m)
    ys, xs = np.nonzero(m)
    for y0, x0 in zip(ys, xs):
        if seen[y0, x0]:
            continue
        q = deque([(y0, x0)])
        seen[y0, x0] = True
        cells = []
        while q:
            y, x = q.popleft()
            cells.append((y, x))
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    q.append((yy, xx))
        if len(cells) >= min_cells:
            yy, xx = zip(*cells)
            out[list(yy), list(xx)] = True
    return out


def measure(boxes):
    floors = _floor_boxes(boxes)
    if not floors:
        return None
    x0 = min(c[0] - h[0] for _, c, h in floors)
    x1 = max(c[0] + h[0] for _, c, h in floors)
    y0 = min(c[1] - h[1] for _, c, h in floors)
    y1 = max(c[1] + h[1] for _, c, h in floors)
    if (x1 - x0) * (y1 - y0) > 900.0:          # a street, a lot, a field — not a room
        return None
    W, H = int(np.ceil((x1 - x0) / CELL)), int(np.ceil((y1 - y0) / CELL))

    def span(c, h):
        a = int(np.floor((c[0] - h[0] - x0) / CELL)); b = int(np.ceil((c[0] + h[0] - x0) / CELL))
        d = int(np.floor((c[1] - h[1] - y0) / CELL)); e = int(np.ceil((c[1] + h[1] - y0) / CELL))
        return max(0, d), min(H, e), max(0, a), min(W, b)

    floor = np.zeros((H, W), bool)
    for _, c, h in floors:
        d, e, a, b = span(c, h)
        floor[d:e, a:b] = True
    ftop = max(c[2] + h[2] for _, c, h in floors)
    obst = np.zeros((H, W), bool)
    pieces = []
    for n, c, h in boxes:
        if SKIP_RE.search(n) or FLOOR_RE.search(n) and not NOT_FLOOR_RE.search(n):
            continue
        lo, hi = c[2] - h[2] - ftop, c[2] + h[2] - ftop
        if hi < BAND[0] or lo > BAND[1] or 2 * h[2] < 0.03:
            continue
        if c[0] + h[0] < x0 or c[0] - h[0] > x1 or c[1] + h[1] < y0 or c[1] - h[1] > y1:
            continue
        d, e, a, b = span(c, h)
        if d >= e or a >= b:
            continue
        obst[d:e, a:b] = True
        if lo <= 0.30 and 2 * h[0] < 4.0 and 2 * h[1] < 4.0 and not re.search(r"wall|pier|spandrel|lintel|jamb|header|partition|column|post_?wall", n, re.I):
            pieces.append((n, c, h))
    free = floor & ~obst
    r = int(round(BODY_R / CELL))
    core = _components(_erode(free, r), int(0.25 / (CELL * CELL)))
    walk = _dilate(core, r) & free
    fa = float(floor.sum())
    # pinches: pairs of floor pieces (grouped by assembly token) 0.10-0.55 apart
    groups = {}
    for n, c, h in pieces:
        k = n.split("_")[0]
        g = groups.setdefault(k, [c[0] - h[0], c[1] - h[1], c[0] + h[0], c[1] + h[1]])
        g[0] = min(g[0], c[0] - h[0]); g[1] = min(g[1], c[1] - h[1])
        g[2] = max(g[2], c[0] + h[0]); g[3] = max(g[3], c[1] + h[1])
    keys = [k for k, g in groups.items() if (g[2] - g[0]) * (g[3] - g[1]) >= 0.04]
    pinches = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = groups[keys[i]], groups[keys[j]]
            gx = max(0.0, max(a[0], b[0]) - min(a[2], b[2]))
            gy = max(0.0, max(a[1], b[1]) - min(a[3], b[3]))
            gap = (gx * gx + gy * gy) ** 0.5
            if PINCH[0] <= gap <= PINCH[1]:
                pinches.append((round(gap, 2), keys[i], keys[j]))
    return {"floor": round(fa * CELL * CELL, 1),
            "filled": round(float((obst & floor).sum()) / fa, 3),
            "walk": round(float(walk.sum()) / fa, 3),
            "pinches": sorted(pinches)}


def main():
    import prop_overlap_audit as P
    import window_count_audit as Wc
    P.A.install_stubs()
    want = [a for a in sys.argv[1:] if not a.startswith("--") and not a.endswith(".json")]
    lines = Wc.lines_by_locale()
    rows = []
    for b in sorted(glob.glob(os.path.join(BUILDERS, "build_*.py"))):
        loc = os.path.basename(b)[6:-3]
        if want and loc not in want:
            continue
        old = sys.stdout
        sys.stdout = open(os.devnull, "w")
        try:
            boxes, _ = P.record_builder(b)
        except Exception:
            boxes = None
        finally:
            sys.stdout = old
        if not boxes:
            continue
        m = measure(boxes)
        if not m:
            continue
        m.update(locale=loc, lines=lines.get(loc, 0))
        # crowding: what is NOT walkable, weighted by how much it is played
        m["score"] = round((1.0 - m["walk"]) * (1 + len(m["pinches"]) * 0.1) * (m["lines"] ** 0.5), 2)
        rows.append(m)
    rows.sort(key=lambda r: -r["score"])
    if "--json" in sys.argv:
        json.dump(rows, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
    print("%-28s %6s %7s %6s %6s %6s" % ("locale", "lines", "floor", "filled", "walk", "pinch"))
    for r in rows:
        if not want and r["lines"] == 0:
            continue
        print("%-28s %6d %7.1f %6.2f %6.2f %6d" % (r["locale"], r["lines"], r["floor"], r["filled"], r["walk"], len(r["pinches"])))
        if want:
            for p in r["pinches"][:12]:
                print("      pinch %.2f m  %s · %s" % p)
    print("room_crowding_audit · %d room set(s)" % len(rows))


if __name__ == "__main__":
    main()
