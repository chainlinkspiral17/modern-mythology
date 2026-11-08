#!/usr/bin/env python3
"""hero_art_fix.py — put every hero picture where its set says it goes (2026-11-08).

Fixes the mechanical findings of hero_art_placement_audit.py in
tools/meshy_roster.json, from the set's own geometry (the stand-in the row
hides is the truth: the builder put the sign board, the poster, the screen
there):

  OFF-FACE  → the picture moves onto the stand-in's front face (the side it
              faces), so it neither floats in front nor sinks inside.
  MISFIT    → the picture takes the stand-in face's centre and size, when
              the stand-in is about the picture's size (face area within
              0.25x..4x of the picture). A row that names a far bigger part
              (a whole wall) keeps its size and place on that face.
  FLOATING  → a row with no stand-in moves onto the nearest surface behind
              it (within 30 cm) that covers at least half the picture.

COVERED findings need a reading (a sign band across a mural is a bug; a
string across a corkboard is the corkboard) and are left to the audit.

The roster round-trips byte-for-byte (json indent 2, ensure_ascii False),
so the diff is only the rows that move.

    python3 tools/audit/hero_art_fix.py --dry      # what would move
    python3 tools/audit/hero_art_fix.py            # write the roster
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GODOT = os.path.normpath(os.path.join(HERE, "..", ".."))
ROSTER = os.path.join(GODOT, "tools", "meshy_roster.json")
sys.path.insert(0, HERE)
import hero_art_placement_audit as H  # noqa: E402
import vantage_obstruction_audit as VO  # noqa: E402


def fix_row(row, boxes):
    fc = str(row.get("facing", "")).lower()
    if fc not in H.AXES:
        return None
    n, sg = H.AXES[fc]
    wa, ha = H._plane_axes(n)
    c = [float(v) for v in row["center"]]
    w, h = float(row["size"][0]), float(row["size"][1])
    hide = [str(p) for p in (row.get("hide") or [])]
    hidden = [b for b in boxes if any(b[0].startswith(p) for p in hide)] if hide else []
    new_c, new_s = list(c), [w, h]
    why = []
    if hidden:
        lo = [min(b[1][i] - b[2][i] for b in hidden) for i in range(3)]
        hi = [max(b[1][i] + b[2][i] for b in hidden) for i in range(3)]
        face = hi[n] if sg > 0 else lo[n]
        if abs(c[n] - face) > H.FACE_TOL:
            new_c[n] = face
            why.append("onto the face (%.2f m)" % abs(c[n] - face))
        sw, sh = hi[wa] - lo[wa], hi[ha] - lo[ha]
        scx, scz = (hi[wa] + lo[wa]) / 2.0, (hi[ha] + lo[ha]) / 2.0
        off = max(abs(c[wa] - scx) / max(sw, 0.05), abs(c[ha] - scz) / max(sh, 0.05))
        rw, rh = w / max(sw, 0.01), h / max(sh, 0.01)
        ratio = (sw * sh) / max(w * h, 1e-6)
        misfit = off > 0.15 or not (0.6 <= rw <= 1.6) or not (0.6 <= rh <= 1.6)
        if misfit and 0.25 <= ratio <= 4.0 and sw > 0.02 and sh > 0.02:
            new_c[wa], new_c[ha] = scx, scz
            new_s = [sw, sh]
            why.append("the stand-in's size and place (%.2fx%.2f → %.2fx%.2f)" % (w, h, sw, sh))
    elif not hide:
        # the nearest surface behind, covering half the picture
        q0 = (c[wa] - w / 2.0, c[wa] + w / 2.0)
        q1 = (c[ha] - h / 2.0, c[ha] + h / 2.0)
        best = None
        for b in boxes:
            if H.NONSOLID.search(b[0]):
                continue
            bc, bh = b[1], b[2]
            face = bc[n] + sg * bh[n]
            behind = (c[n] - face) * sg          # > 0: the face is behind the picture
            if not (-H.FACE_TOL <= behind <= 0.30):
                continue
            cov = H._overlap_1d(q0[0], q0[1], bc[wa] - bh[wa], bc[wa] + bh[wa]) * \
                  H._overlap_1d(q1[0], q1[1], bc[ha] - bh[ha], bc[ha] + bh[ha])
            if cov < 0.5 * w * h:
                continue
            if best is None or abs(behind) < abs(best[0]):
                best = (behind, face, b[0])
        if best is not None and abs(best[0]) > H.FACE_TOL:
            new_c[n] = best[1]
            why.append("onto %s (%.2f m)" % (best[2], abs(best[0])))
    if not why:
        return None
    return [round(v, 4) for v in new_c], [round(v, 4) for v in new_s], "; ".join(why)


def main():
    dry = "--dry" in sys.argv
    want = set(a for a in sys.argv[1:] if not a.startswith("--"))
    src = open(ROSTER, encoding="utf-8").read()
    data = json.loads(src)
    moved = 0
    by_loc = {}
    for e in data.get("entries", []):
        if e.get("kind") != "art":
            continue
        for r in e.get("apply", []) or []:
            if not (isinstance(r, dict) and r.get("locale") and r.get("center") and r.get("size")):
                continue
            loc = r["locale"]
            if want and loc not in want:
                continue
            if loc not in by_loc:
                by_loc[loc] = VO.boxes_for(loc)
            boxes = by_loc[loc]
            if not boxes:
                continue
            f = fix_row(r, boxes)
            if f is None:
                continue
            moved += 1
            print("%-26s %-34s %s" % (loc, e.get("slug", "?"), f[2]))
            if not dry:
                r["center"], r["size"] = f[0], f[1]
    if not dry and moved:
        with open(ROSTER, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("\nhero_art_fix · %d row(s) %s" % (moved, "would move" if dry else "moved"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
