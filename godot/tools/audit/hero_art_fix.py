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
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GODOT = os.path.normpath(os.path.join(HERE, "..", ".."))
ROSTER = os.path.join(GODOT, "tools", "meshy_roster.json")
sys.path.insert(0, HERE)
import hero_art_placement_audit as H  # noqa: E402
import vantage_obstruction_audit as VO  # noqa: E402


FLIP = {"+x": "-x", "-x": "+x", "+y": "-y", "-y": "+y"}
_CAMS = {}


def cameras(locale):
    """every viewpoint on a set, in BLENDER coordinates: the camera_origin of
    each preset that loads it and each shot marker in its scene"""
    if locale in _CAMS:
        return _CAMS[locale]
    import shot_marker_audit as SM
    pts = []
    p2s = SM.preset_to_scene()
    bg = open(os.path.join(GODOT, "scripts", "vn", "Background3D.gd"), encoding="utf-8").read()
    for preset, scene in p2s.items():
        if os.path.basename(scene)[:-5] != locale:
            continue
        m = re.search(r'\n\t"%s": \{(.*?)\n\t\}' % re.escape(preset), bg, re.S)
        if m:
            o = re.search(r'"camera_origin": Vector3\(([-\d.]+),\s*([-\d.]+),\s*([-\d.]+)\)', m.group(1))
            if o:
                gx, gy, gz = (float(v) for v in o.groups())
                pts.append((gx, -gz, gy))
        tscn = os.path.join(GODOT, scene)
        if os.path.exists(tscn):
            src = open(tscn, encoding="utf-8").read()
            for mm in re.finditer(r'\[node name="shot_[^"]*"[^\n]*\n(?:transform = Transform3D\([^)]*?([-\d.]+), ([-\d.]+), ([-\d.]+)\)\n|position = Vector3\(([-\d.]+), ([-\d.]+), ([-\d.]+)\))', src):
                g = [x for x in mm.groups() if x is not None]
                if len(g) == 3:
                    gx, gy, gz = (float(v) for v in g)
                    pts.append((gx, -gz, gy))
    _CAMS[locale] = pts
    return pts


def viewers_behind(locale, c, n, sg, rect):
    """cameras within 25 m that look at the picture's plane from in front of it
    vs from behind it (in-plane within the picture's rect grown by 8 m)"""
    wa, ha = H._plane_axes(n)
    front = back = 0
    for p in cameras(locale):
        d = (p[n] - c[n]) * sg
        if abs(d) < 0.05 or abs(d) > 25.0:
            continue
        if not (rect[0][0] - 8.0 <= p[wa] <= rect[0][1] + 8.0):
            continue
        if d > 0:
            front += 1
        else:
            back += 1
    return front, back


def _blocked(face_c, n, sg, rect, boxes, skip):
    """how much of a stand-in face's rect a solid in front of it (within
    0.40 m, starting at or behind the face) covers"""
    wa, ha = H._plane_axes(n)
    (a0, a1), (b0, b1) = rect
    area = max((a1 - a0) * (b1 - b0), 1e-6)
    worst = 0.0
    for b in boxes:
        if b[0] in skip or H.NONSOLID.search(b[0]) or re.search(r"glass|curtain|blind", b[0], re.I):
            continue
        bc, bh = b[1], b[2]
        ahead = (bc[n] + sg * bh[n] - face_c) * sg
        starts = (bc[n] - sg * bh[n] - face_c) * sg
        if not (0.005 < ahead <= 0.40) or starts > 0.05:
            continue
        cov = H._overlap_1d(a0, a1, bc[wa] - bh[wa], bc[wa] + bh[wa]) * \
              H._overlap_1d(b0, b1, bc[ha] - bh[ha], bc[ha] + bh[ha])
        worst = max(worst, cov / area)
    return worst


def flip_row(row, boxes):
    """a picture whose stand-in face on its facing side is buried in a solid
    while the opposite face is open faces the wrong way (the Kowalski window
    faced into the house; the New Orleans laundromat sign into its own box):
    turn it to the open side, on that face"""
    fc = str(row.get("facing", "")).lower()
    hide = [str(p) for p in (row.get("hide") or [])]
    if fc not in FLIP or not hide:
        return None
    hidden = H.hidden_by(row, boxes)
    if not hidden:
        return None
    n, sg = H.AXES[fc]
    wa, ha = H._plane_axes(n)
    lo = [min(b[1][i] - b[2][i] for b in hidden) for i in range(3)]
    hi = [max(b[1][i] + b[2][i] for b in hidden) for i in range(3)]
    rect = ((lo[wa], hi[wa]), (lo[ha], hi[ha]))
    skip = {b[0] for b in hidden}
    face_here = hi[n] if sg > 0 else lo[n]
    face_there = lo[n] if sg > 0 else hi[n]
    if _blocked(face_here, n, sg, rect, boxes, skip) >= 0.9 and _blocked(face_there, n, -sg, rect, boxes, skip) < 0.3:
        # … and only when the cameras that see it are on the other side
        front, back = viewers_behind(row["locale"], [float(v) for v in row["center"]], n, sg, rect)
        if back <= front:
            return None
        c = [float(v) for v in row["center"]]
        c[n] = face_there
        c[wa], c[ha] = (lo[wa] + hi[wa]) / 2.0, (lo[ha] + hi[ha]) / 2.0
        return FLIP[fc], [round(v, 4) for v in c]
    return None


def fix_row(row, boxes):
    fc = str(row.get("facing", "")).lower()
    if fc not in H.AXES:
        return None
    n, sg = H.AXES[fc]
    wa, ha = H._plane_axes(n)
    c = [float(v) for v in row["center"]]
    w, h = float(row["size"][0]), float(row["size"][1])
    hide = [str(p) for p in (row.get("hide") or [])]
    hidden = H.hidden_by(row, boxes)
    new_c, new_s = list(c), [w, h]
    why = []
    if hidden:
        lo = [min(b[1][i] - b[2][i] for b in hidden) for i in range(3)]
        hi = [max(b[1][i] + b[2][i] for b in hidden) for i in range(3)]
        face = hi[n] if sg > 0 else lo[n]
        fp = H.fitting_part(c, w, h, n, sg, wa, ha, hidden)
        if fp is not None:
            face = fp[2]
        if H.FACE_TOL < abs(c[n] - face) <= 0.50 and not H.on_host(c, w, h, n, sg, wa, ha, boxes,
                                                                    {x[0] for x in hidden}, face) \
                and not ((c[n] - face) * sg > 0 and H.on_post(c, w, h, n, sg, wa, ha, boxes)) \
                and not H.camera_side(row, c, w, h, n, sg, wa, ha, hidden):
            new_c[n] = face
            why.append("onto the face (%.2f m)" % abs(c[n] - face))
        sw, sh = hi[wa] - lo[wa], hi[ha] - lo[ha]
        scx, scz = (hi[wa] + lo[wa]) / 2.0, (hi[ha] + lo[ha]) / 2.0
        off = max(abs(c[wa] - scx) / max(sw, 0.05), abs(c[ha] - scz) / max(sh, 0.05))
        rw, rh = w / max(sw, 0.01), h / max(sh, 0.01)
        ratio = (sw * sh) / max(w * h, 1e-6)
        misfit = fp is None
        # HALF-SIZE: the row's size is the part's half-extents (a sign 1.30 x
        # 0.40 m carried a 0.65 x 0.20 picture; monitors half their body):
        # the picture takes that part's full face — a screen part if the
        # thing has one (the picture is what is ON the monitor)
        half = None
        for b in hidden:
            bw, bhh = 2.0 * b[2][wa], 2.0 * b[2][ha]
            if 0.45 <= w / max(bw, 1e-6) <= 0.55 and 0.45 <= h / max(bhh, 1e-6) <= 0.55:
                half = b
                break
        if half is not None:
            scr = [b for b in hidden if re.search(r"screen|display|glass", b[0], re.I)]
            tgt = scr[0] if scr else half
            tc, th = tgt[1], tgt[2]
            new_c[n] = tc[n] + sg * th[n]
            new_c[wa], new_c[ha] = tc[wa], tc[ha]
            new_s = [2.0 * th[wa], 2.0 * th[ha]]
            why.append("half-size row: the full face of %s (%.2fx%.2f → %.2fx%.2f)" % (tgt[0], w, h, new_s[0], new_s[1]))
            misfit = False
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
    # BURIED: a solid wholly over the picture that starts at or behind it —
    # the picture is INSIDE that solid (a pump screen inside the pump body,
    # a sign inside its building, an OPEN sign behind its own door). It
    # moves out onto that solid's front face. A free-standing thing in front
    # (it starts > 5 cm in front of the picture) is not this, and stays a
    # COVERED finding for a reading.
    c2 = new_c
    w2, h2 = new_s
    q0 = (c2[wa] - w2 / 2.0, c2[wa] + w2 / 2.0)
    q1 = (c2[ha] - h2 / 2.0, c2[ha] + h2 / 2.0)
    skip = {b[0] for b in hidden}
    front = None
    for b in boxes:
        if b[0] in skip or H.NONSOLID.search(b[0]) or re.search(r"curtain|blind|drape|valance", b[0], re.I):
            continue
        bc, bh = b[1], b[2]
        b_front = bc[n] + sg * bh[n]
        b_back = bc[n] - sg * bh[n]
        ahead = (b_front - c2[n]) * sg          # how far its front face is in front of the picture
        starts = (b_back - c2[n]) * sg          # its back face, measured the same way
        # (2026-11-09) the picture must be INSIDE the solid (its back face at
        # or behind the picture): a solid that starts in front of a picture
        # facing it is FACES-IN, turned by turn_row — pushing the picture out
        # through it put Lena's canvas on the far side of the wall
        if not (0.01 < ahead <= 0.40) or starts > -0.005:
            continue
        cov = H._overlap_1d(q0[0], q0[1], bc[wa] - bh[wa], bc[wa] + bh[wa]) * \
              H._overlap_1d(q1[0], q1[1], bc[ha] - bh[ha], bc[ha] + bh[ha])
        if cov < 0.9 * w2 * h2:
            continue
        if front is None or (b_front - front[0]) * sg > 0:
            front = (b_front, b[0])
    if front is not None:
        new_c = list(new_c)
        new_c[n] = front[0]
        why.append("out of %s onto its face (%.2f m)" % (front[1], abs(front[0] - c2[n])))
    if not why:
        return None
    return [round(v, 4) for v in new_c], [round(v, 4) for v in new_s], "; ".join(why)


def turn_row(row, boxes):
    """(2026-11-08) a picture that FACES-IN — into the pump, the shop wall,
    the truck it is on — turns to face out of it, onto the stand-in's face
    on the open side (or the solid's own face when the row hides nothing).
    Kept only when the turned picture has no FACES-IN or OFF-FACE finding,
    so a door-glass sign (seen both ways, nothing solid in front) never
    turns. A picture buried > 20 cm (a far hill inside its hill) is read by
    hand."""
    slug = "?"
    found = H.check_row(slug, row, boxes)
    hit = [x for x in found if x.startswith("FACES-IN")]
    if not hit:
        return None
    fc = str(row.get("facing", "")).lower()
    if fc not in FLIP:
        return None
    m = re.search(r"faces into (\S+) .*(from|buried) ([\d.]+) m", hit[0])
    if not m or (m.group(2) == "buried" and float(m.group(3)) > 0.20):
        return None
    n, sg = H.AXES[fc]
    c = [float(v) for v in row["center"]]
    w, h = float(row["size"][0]), float(row["size"][1])
    wa, ha = H._plane_axes(n)
    hidden = H.hidden_by(row, boxes)
    if hidden:
        fp = H.fitting_part(c, w, h, n, -sg, wa, ha, hidden)
        if fp is not None:
            c[n] = fp[2]
        else:
            c[n] = (max(b[1][n] + b[2][n] for b in hidden) if -sg > 0 else
                    min(b[1][n] - b[2][n] for b in hidden))
    else:
        body = [b for b in boxes if b[0] == m.group(1)]
        if not body:
            return None
        c[n] = body[0][1][n] - sg * body[0][2][n]
    cand = dict(row, facing=FLIP[fc], center=[round(v, 4) for v in c])
    after = H.check_row(slug, cand, boxes)
    if any(x.startswith(("FACES-IN", "OFF-FACE")) for x in after):
        return None
    return FLIP[fc], cand["center"]


_LOCALE_ROWS = {}


def leftover_row(row, boxes):
    """(2026-11-08) LEFTOVER: the stand-in's own piece left in front of its
    picture. A post or pole the sign was centred on → the picture moves just
    in front of it (the sign hangs on its post's face, not through it). A
    thin detail (a pinned paper, a menu row, a road line ≤ 3 cm deep) →
    the row hides it too, by its exact name."""
    others = set()
    for r2 in _LOCALE_ROWS.get(row["locale"], []):
        if r2 is not row:
            others |= {b[0] for b in H.hidden_by(r2, boxes)}
    found = [x for x in H.check_row("?", row, boxes, others) if x.startswith("LEFTOVER")]
    if not found:
        return None
    fc = str(row.get("facing", "")).lower()
    n, sg = H.AXES[fc]
    c = [float(v) for v in row["center"]]
    hide = list(row.get("hide") or [])
    why = []
    byname = {b[0]: b for b in boxes}
    for x in found:
        m = re.search(r"LEFTOVER\s+\S+: (\S+) ", x)
        if not m or m.group(1) not in byname:
            continue
        b = byname[m.group(1)]
        front = b[1][n] + sg * b[2][n]
        if re.search(r"post|pole", b[0], re.I):
            want = front + sg * 0.004
            if (want - c[n]) * sg > 0 and (want - c[n]) * sg <= 0.15:
                c[n] = want
                why.append("in front of %s (%.3f m)" % (b[0], abs(want - float(row["center"][n]))))
        elif b[2][n] * 2.0 <= 0.03 and b[0] not in hide:
            hide.append(b[0])
            why.append("hides %s too" % b[0])
    if not why:
        return None
    return [round(v, 4) for v in c], hide, "; ".join(why)


def main():
    dry = "--dry" in sys.argv
    want = set(a for a in sys.argv[1:] if not a.startswith("--"))
    src = open(ROSTER, encoding="utf-8").read()
    data = json.loads(src)
    moved = 0
    by_loc = {}
    for e in data.get("entries", []):
        if e.get("kind") == "art":
            for r in e.get("apply", []) or []:
                if isinstance(r, dict) and r.get("locale"):
                    _LOCALE_ROWS.setdefault(r["locale"], []).append(r)
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
            # (automatic turning stays OFF: a sign on door glass faces both
            # ways and a set's cameras are mostly on one side of it — the
            # wrong-facing rows are read and turned by hand)
            fl = turn_row(r, boxes)
            if fl is not None:
                print("%-26s %-34s faced into its object: turned %s → %s" % (loc, e.get("slug", "?"), r["facing"], fl[0]))
                moved += 1
                if not dry:
                    r["facing"], r["center"] = fl[0], fl[1]
                continue
            lf = leftover_row(r, boxes)
            if lf is not None:
                print("%-26s %-34s %s" % (loc, e.get("slug", "?"), lf[2]))
                moved += 1
                if not dry:
                    r["center"], r["hide"] = lf[0], lf[1]
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
