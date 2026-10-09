#!/usr/bin/env python3
"""buried_decor_audit.py — is the wall dressing IN FRONT of the wall? (2026-10-09)

The overnight run found Diego's jerseys, scarf and flag, Jesse's acoustic
foam and lyric sheets, Maya's corkboard, the Miller office's commendations,
Lena's thermostat, a run of pegboards, mirrors, menu boards and neon
backings — 4 to 8 cm INSIDE their walls: placed from the wall's CENTRE
line (`ROOM_W/2 - 0.06` on a 20 cm wall whose face is at ROOM_W/2 - 0.10)
instead of its face. Every gate passed them: a part buried in a wall
touches the wall (support is happy) and clips nothing it is not part of.
No camera can ever see them.

Every DECOR part (a poster, board, sign, mirror, clock, calendar, pennant,
foam, frame…) whose box lies ENTIRELY inside a wall part's box fails.
Hidden-by-design backs (a shelf's back panel, a cooler's interior back)
are not decor and are not judged.

    python3 godot/tools/audit/buried_decor_audit.py            # every builder
    python3 godot/tools/audit/buried_decor_audit.py diego_bedroom
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prop_overlap_audit as P  # noqa: E402

WALL = re.compile(r"(^|_)(wall|walls)(_|$)|^Wall", re.I)
DECOR = re.compile(r"(foam|lyric|cork|(^|_)pin(_|$)|fairy|cert|map_|calendar|clock|mirror|menu|neon|pegboard|(^|_)peg_|"
                   r"pennant|setlist|thermostat|poster|photo|frame_art|(^|_)sign(_|$)|plaque|moodboard|services_board|"
                   r"jersey|scarf|flag|banner|notice|workorder|pinned|lure)", re.I)
NOT = re.compile(r"(ceil_grid|ceiling_grid|baseboard|(^|_)base(_|$)|_back$|_back_|interior_back)", re.I)


def audit(loc):
    P.record_builder(os.path.join(P.A.LOCALES, "build_%s.py" % loc))
    boxes = list(P.A.BOXES)
    walls = [(n, c, h) for n, c, h in boxes if WALL.search(n) and 2 * h[2] > 1.0 and min(h[0], h[1]) <= 0.16]
    out = []
    for n, c, h in boxes:
        if WALL.search(n) or NOT.search(n) or not DECOR.search(n) or c[2] < 0.3:
            continue
        for wn, wc, wh in walls:
            if all(wc[i] - wh[i] - 1e-4 <= c[i] - h[i] and c[i] + h[i] <= wc[i] + wh[i] + 1e-4 for i in range(3)):
                out.append((n, wn))
                break
    return out


def main(argv):
    P.A.install_stubs()
    locs = argv[1:] or sorted(os.path.basename(p)[6:-3] for p in glob.glob(os.path.join(P.A.LOCALES, "build_*.py")))
    total = 0
    for loc in locs:
        try:
            bad = audit(loc)
        except Exception as e:  # a builder the recorder cannot run is not a buried-decor defect
            print("  · %-28s (skipped: %s)" % (loc, type(e).__name__))
            continue
        for n, wn in bad:
            total += 1
            print("  ✗ %-26s %-34s buried in %s" % (loc, n, wn))
    print("buried_decor_audit · %d locale(s) · %d decor part(s) inside a wall" % (len(locs), total))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
