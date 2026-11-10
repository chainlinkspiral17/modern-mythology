#!/usr/bin/env python3
"""window_size_audit.py — are the windows too small? (2026-11-10)

The user: "Look at windows, if they are too small." Most rooms were cut
from one kitchen template with a 0.9 x 1.05 m window; a real double-hung
is about 0.9 x 1.5, a living-room picture window 1.5 - 2.4 m wide, and a
head at 2.0 - 2.1 m. A small pane high in a big wall is half of why a room
reads as a box.

For every built set this groups the parts of each window (by name: the
prefix before _Frame / _Glass / _Casing / _Mull ...), measures its frame —
width, height, sill and head — and the wall it is in, and reports the
ones under a house window's size:

    SMALL   width < 1.00 m, or height < 1.10 m   (a room window; not a door lite)
    LOW     head under 1.90 m                    (the top of the glass below eye-line-plus)

    python3 tools/audit/window_size_audit.py                 # every set, worst first
    python3 tools/audit/window_size_audit.py finn_apartment  # one set, every window
    python3 tools/audit/window_size_audit.py --csv           # the table

A report, not a gate: a basement's "small high window", a cabin porthole
and a bathroom slit are small on purpose (the text decides).
"""
import contextlib, io, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vantage_obstruction_audit as VO   # noqa: E402

WIN = re.compile(r"(^|_)(window|win|sash|skylight|porthole)(_|$|[0-9])", re.I)
MEMBER = re.compile(r"_(Frame|FrameT|FrameB|FrameSide|Frame_Head|Frame_Sill|Frame_Jamb[AB]?|Glass|Warm|Pane|Mull[HV]?|Mullion|Glint)(_|$)", re.I)
NOT_WIN = re.compile(r"curtain|blind|rod|bracket|stool|apron|casing|sill$|_sill_|shade|valance|box|plant|mark|wear|drip|view|out_|practical|decal|sticker|sign|card|display", re.I)
VEHICLE = re.compile(r"cab|car|truck|van|bus|boat|train|plane|civic|subaru|vehicle|ferry|trailer", re.I)
SMALL_W, SMALL_H, LOW_HEAD = 1.00, 1.10, 1.90


def windows_of(boxes):
    groups = {}
    for n, c, h in boxes:
        if not WIN.search(n) or NOT_WIN.search(n):
            continue
        m = MEMBER.search(n)
        if not m:
            continue
        groups.setdefault(n[:m.start()], []).append((n, c, h))
    out = []
    for pre, parts in groups.items():
        lo = [min(c[i] - h[i] for _, c, h in parts) for i in range(3)]
        hi = [max(c[i] + h[i] for _, c, h in parts) for i in range(3)]
        w = max(hi[0] - lo[0], hi[1] - lo[1])
        t = min(hi[0] - lo[0], hi[1] - lo[1])
        ht = hi[2] - lo[2]
        if w < 0.25 or ht < 0.25 or t > 0.6:
            continue
        out.append((pre, w, ht, lo[2], hi[2], ((lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0)))
    return out


STRUCT = re.compile(r"^(wall|floor|ceil|crown|view|out_)|baseboard|_base$|outlet|switch|wear|stain|scuff|tint|rug|mat$|traffic|cord|practical", re.I)
TARGET_W, TARGET_HEAD, TARGET_SILL = 1.60, 2.20, 0.72


def plan_for(boxes, win):
    """What a window could grow to: (sill, head, a0, a1, why[]). Looks under
    the sill (furniture against the wall holds the sill up) and to both
    sides (wall-hung things and furniture taller than the sill, the wall's
    ends). `--plan` prints it; the builder is edited by hand from it."""
    pre, w, ht, sill, head, at = win
    parts = [(n, c, h) for n, c, h in boxes if n.startswith(pre + "_") or n == pre]
    lo = [min(c[i] - h[i] for _, c, h in parts) for i in range(3)]
    hi = [max(c[i] + h[i] for _, c, h in parts) for i in range(3)]
    ax = 0 if hi[0] - lo[0] >= hi[1] - lo[1] else 1          # the axis the window runs along
    nx = 1 - ax
    line = (lo[nx] + hi[nx]) / 2.0
    floors = [(c, h) for n, c, h in boxes if re.match(r"floor", n, re.I) and h[2] < 0.2]
    if not floors:
        return None
    fc, fh = max(floors, key=lambda f: f[1][0] * f[1][1])
    sign = 1.0 if fc[nx] > line else -1.0
    a0, a1 = lo[ax], hi[ax]
    why = []
    under = 0.0
    lim0, lim1 = fc[ax] - fh[ax] + 0.35, fc[ax] + fh[ax] - 0.35
    for n, c, h in boxes:
        if n.startswith(pre + "_") or n == pre or STRUCT.search(n):
            continue
        d = (c[nx] - line) * sign                 # into the room
        if d - h[nx] > 0.75 or d + h[nx] < -0.15:
            continue
        b0, b1, z0, z1 = c[ax] - h[ax], c[ax] + h[ax], c[2] - h[2], c[2] + h[2]
        if b1 > a0 + 0.02 and b0 < a1 - 0.02:
            if z1 <= sill + 0.06 and z1 > 0.25 and z1 > under:
                under = z1
                why.append("under: %s top %.2f" % (n, z1))
            continue
        if z1 < TARGET_SILL + 0.1 or z0 > TARGET_HEAD:
            continue
        if d - h[nx] > 0.22 and z1 < sill:
            continue                               # low furniture off the wall beside the window
        if b1 <= a0 + 0.02 and b1 + 0.12 > lim0:
            lim0 = b1 + 0.12
            why.append("left: %s to %.2f" % (n, b1))
        if b0 >= a1 - 0.02 and b0 - 0.12 < lim1:
            lim1 = b0 - 0.12
            why.append("right: %s from %.2f" % (n, b0))
    new_sill = min(sill, max(TARGET_SILL, under + 0.08)) if under else min(sill, TARGET_SILL)
    new_head = max(head, TARGET_HEAD)
    cen = (a0 + a1) / 2.0
    half = min(max(TARGET_W, a1 - a0) / 2.0, cen - lim0, lim1 - cen)
    half = max(half, (a1 - a0) / 2.0)
    return ("XY"[ax], line, new_sill, new_head, cen - half, cen + half, why[-6:])


def main():
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    csv = "--csv" in sys.argv
    if "--plan" in sys.argv:
        for loc in want:
            with contextlib.redirect_stdout(io.StringIO()):
                boxes = VO.boxes_for(loc)
            print("== %s" % loc)
            for win in sorted(windows_of(boxes)):
                pl = plan_for(boxes, win)
                pre, w, ht, sill, head, at = win
                if not pl:
                    continue
                ax, line, ns, nh, n0, n1, why = pl
                print("   %-22s frame %.2f x %.2f  sill %.2f head %.2f  ->  %.2f x %.2f  sill %.2f head %.2f  centre %s=%.2f z=%.3f" % (
                    pre, w, ht, sill, head, n1 - n0, nh - ns, ns, nh, ax.lower(), (n0 + n1) / 2.0, (ns + nh) / 2.0))
                for y in why:
                    print("        %s" % y)
        return 0
    rows = []
    seen = set()
    for pid, loc, og, rot, fov in VO.presets():
        if loc in seen or (want and loc not in want and pid not in want):
            continue
        seen.add(loc)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                boxes = VO.boxes_for(loc)
        except Exception:
            boxes = None
        if not boxes:
            continue
        floor_z = 0.0
        for pre, w, ht, sill, head, at in windows_of(boxes):
            flags = []
            if w < SMALL_W or ht < SMALL_H:
                flags.append("SMALL")
            if head - floor_z < LOW_HEAD and sill - floor_z > 0.3:
                flags.append("LOW")
            rows.append((loc, pre, w, ht, sill, head, flags, bool(VEHICLE.search(loc))))
    if csv:
        print("set,window,width,height,sill,head,flags")
        for loc, pre, w, ht, sill, head, flags, veh in rows:
            print("%s,%s,%.2f,%.2f,%.2f,%.2f,%s" % (loc, pre, w, ht, sill, head, "+".join(flags)))
        return 0
    bad = [r for r in rows if r[6] and not r[7]]
    by = {}
    for r in (rows if want else bad):
        by.setdefault(r[0], []).append(r)
    for loc in sorted(by, key=lambda k: (-len([r for r in by[k] if r[6]]), k)):
        print("== %s" % loc)
        for _, pre, w, ht, sill, head, flags, veh in sorted(by[loc], key=lambda r: r[2] * r[3]):
            print("   %-12s %-34s %.2f x %.2f m   sill %.2f  head %.2f" % ("+".join(flags) or "ok", pre, w, ht, sill, head))
    sets = len({r[0] for r in rows if not r[7]})
    print("\nwindow_size_audit · %d window(s) in %d set(s) · %d under a house window's size in %d set(s)" % (
        len([r for r in rows if not r[7]]), sets, len(bad), len({r[0] for r in bad})))
    return 0


if __name__ == "__main__":
    sys.exit(main())
