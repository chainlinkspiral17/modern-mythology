#!/usr/bin/env python3
"""hero_art_placement_audit.py — is every hero picture laid where it belongs?

The user (2026-11-08): "texture art badly placed all over. still needs to be
fixed." — a beach picture laid on a brick wall with a sign band crossing in
front of it. HeroArt.gd lays each roster art row (meshy_roster.json, kind
"art": locale, center [blender x y z], size [w h], facing, hide) as a quad and
hides the stand-in boxes the row names. Nothing checked the rows against the
set. For every row this reads the set's boxes (the recorded builder,
vantage_obstruction_audit.boxes_for) and reports:

  NO-STANDIN  the row hides parts, and no part of the set has that name
  OFF-FACE    the quad is not on the stand-in's face (> 4 cm in front of or
              behind it) — the picture floats, or sinks into its object
  MISFIT      the quad is not the stand-in's size or place on that face
              (centre off by > 15 % of its size, or size outside 0.6x..1.6x)
  FLOATING    no hide row and no surface right behind the quad covering it
  COVERED     another part of the set stands in front of the picture over
              more than 8 % of it, within 40 cm (a sign, a band, a shelf)

A report, not yet a gate: each finding is read and fixed in the roster
(the stand-in's own geometry is the truth) or the builder.

    python3 tools/audit/hero_art_placement_audit.py            # every locale
    python3 tools/audit/hero_art_placement_audit.py cabin_interior
"""
import collections
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GODOT = os.path.normpath(os.path.join(HERE, "..", ".."))
ROSTER = os.path.join(GODOT, "tools", "meshy_roster.json")
sys.path.insert(0, HERE)
import vantage_obstruction_audit as VO  # noqa: E402

FACE_TOL = 0.04
COVER_DEPTH = 0.40
COVER_FRAC = 0.08
NONSOLID = re.compile(r"glow|light|beam\b|shaft|spray|mist|steam|smoke|dust|fog|haze|halo|wear_|stain|"
                      r"^view_|sky|cloud|_ray|ray_", re.I)
GLASSY = re.compile(r"glass|pane|window|_win\b|_win_|screen|curtain|sheer", re.I)
WIRY = re.compile(r"wire|cable|cord|string|chain|rod\b|_rod_", re.I)
SLOPED = re.compile(r"roof|rafter|plank|purlin|eave", re.I)
AXES = {"+x": (0, 1), "-x": (0, -1), "+y": (1, 1), "-y": (1, -1), "up": (2, 1), "+z": (2, 1)}


def _plane_axes(n):
    """the two in-plane axes (width, height) for a normal axis"""
    return {0: (1, 2), 1: (0, 2), 2: (0, 1)}[n]


def _overlap_1d(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))


def on_host(c, w, h, n, sg, wa, ha, boxes, skip, stand_face):
    """the picture lies on the front face of a solid that wholly backs it and
    reaches back past the stand-in's face — the stand-in is buried in that
    solid (a sign board inside a building body) and the picture rightly sits
    on the solid's face"""
    q0 = (c[wa] - w / 2.0, c[wa] + w / 2.0)
    q1 = (c[ha] - h / 2.0, c[ha] + h / 2.0)
    for b in boxes:
        if b[0] in skip:
            continue
        bc, bh = b[1], b[2]
        if abs(bc[n] + sg * bh[n] - c[n]) > FACE_TOL:
            continue
        if (bc[n] - sg * bh[n] - stand_face) * sg > 0.01:
            continue
        cov = _overlap_1d(q0[0], q0[1], bc[wa] - bh[wa], bc[wa] + bh[wa]) * \
              _overlap_1d(q1[0], q1[1], bc[ha] - bh[ha], bc[ha] + bh[ha])
        if cov >= 0.9 * w * h:
            return True
    return False


def on_post(c, w, h, n, sg, wa, ha, boxes):
    """the picture is mounted on the front of a post or pole (the sign
    stand-in was centred ON its post, so the post ran up through the
    picture: hero_art_fix moves it to the post's face, 2026-11-08)"""
    for b in boxes:
        if not re.search(r"post|pole", b[0], re.I):
            continue
        bc, bh = b[1], b[2]
        front = bc[n] + sg * bh[n]
        if abs(c[n] - front) > 0.012:
            continue
        if _overlap_1d(c[wa] - w / 2, c[wa] + w / 2, bc[wa] - bh[wa], bc[wa] + bh[wa]) > 0 and \
                _overlap_1d(c[ha] - h / 2, c[ha] + h / 2, bc[ha] - bh[ha], bc[ha] + bh[ha]) > 0:
            return True
    return False


def fitting_part(c, w, h, n, sg, wa, ha, hidden):
    """the hidden part (or the whole stand-in) the picture fits — its face
    rect within 0.6x..1.6x of the picture and the picture's centre within
    15 % of it; the largest such. None when nothing fits."""
    cands = []
    if hidden:
        lo = [min(b[1][i] - b[2][i] for b in hidden) for i in range(3)]
        hi = [max(b[1][i] + b[2][i] for b in hidden) for i in range(3)]
        cands.append(("(all)", lo, hi))
        for b in hidden:
            cands.append((b[0], [b[1][i] - b[2][i] for i in range(3)], [b[1][i] + b[2][i] for i in range(3)]))
    best = None
    faces = []
    for name, lo, hi in cands:
        sw, sh = hi[wa] - lo[wa], hi[ha] - lo[ha]
        cx, cz = (hi[wa] + lo[wa]) / 2.0, (hi[ha] + lo[ha]) / 2.0
        off = max(abs(c[wa] - cx) / max(sw, 0.05), abs(c[ha] - cz) / max(sh, 0.05))
        rw, rh = w / max(sw, 0.01), h / max(sh, 0.01)
        if off <= 0.15 and 0.6 <= rw <= 1.6 and 0.6 <= rh <= 1.6:
            face = hi[n] if sg > 0 else lo[n]
            faces.append(face)
            err = abs(math.log(rw)) + abs(math.log(rh)) + off     # the CLOSEST fit
            if best is None or err < best[1]:
                best = (name, err, face, faces)
    return best


def hidden_by(row, boxes):
    """the parts HeroArt._hide really hides for this row — the same rule as
    the runtime (2026-11-08: the audit matched every bare prefix room-wide,
    so 'Poster_1' took Poster_10 across the room and 'Bypass_Sign' the
    Bypass_Signal_ lamps): an exact name or a `Name_` prefix hides its
    matches under the picture (all of them when none is under it); a bare
    prefix's longer names (Donut_Sign's Donut_SignText) hide only under it"""
    hide = [str(p) for p in (row.get("hide") or [])]
    if not hide:
        return []
    fc = str(row.get("facing", "")).lower()
    if fc not in AXES:
        return []
    n, _sg = AXES[fc]
    wa, ha = _plane_axes(n)
    c = [float(v) for v in row["center"]]
    hw, hh = float(row["size"][0]) / 2.0 + 0.15, float(row["size"][1]) / 2.0 + 0.15

    def _near(b):
        bc = b[1]
        return abs(bc[wa] - c[wa]) <= hw and abs(bc[ha] - c[ha]) <= hh and abs(bc[n] - c[n]) <= 0.30

    exact, parts = [], []
    for b in boxes:
        nm = b[0]
        for h in hide:
            if nm == h or (h.endswith("_") and nm.startswith(h)):
                exact.append(b)
                break
            if nm.startswith(h):
                parts.append(b)
                break
    near = [b for b in exact if _near(b)]
    return (near or exact) + [b for b in parts if _near(b)]


def labelled(row, boxes, hidden):
    """the parts the row's label names ("Fool_Notebook_L + Fool_Notebook_R",
    "Class_Chalkboard") — the stand-in the picture is laid ON when the hide
    list names only its detail (the notebook's ruled lines, the chalk words)"""
    toks = set(t.strip() for t in re.split(r"\s*\+\s*|\(", str(row.get("label", ""))) if t.strip())
    have = {b[0] for b in hidden}
    return [b for b in boxes if b[0] in toks and b[0] not in have]


def check_row(slug, row, boxes, others_hidden=frozenset()):
    """others_hidden: parts the locale's OTHER rows hide (not drawn when the
    pictures are in: they cover nothing)"""
    out = []
    fc = str(row.get("facing", "")).lower()
    if fc not in AXES:
        return ["BADROW     %s: facing %r" % (slug, fc)]
    n, sg = AXES[fc]
    wa, ha = _plane_axes(n)
    c = [float(v) for v in row["center"]]
    w, h = float(row["size"][0]), float(row["size"][1])
    q0 = (c[wa] - w / 2.0, c[wa] + w / 2.0)
    q1 = (c[ha] - h / 2.0, c[ha] + h / 2.0)
    area = max(w * h, 1e-6)
    hide = [str(p) for p in (row.get("hide") or [])]
    hidden = hidden_by(row, boxes)
    if hidden and fitting_part(c, w, h, n, sg, wa, ha, hidden) is None:
        # nothing hidden is the picture's size: the label's part may be (the
        # hide names only a notebook's ruled lines; the picture is its page)
        more = hidden + labelled(row, boxes, hidden)
        if fitting_part(c, w, h, n, sg, wa, ha, more) is not None:
            hidden = more
    support = []
    if hide and not hidden:
        out.append("NO-STANDIN %s: hides %s — no such part in %s" % (slug, ",".join(hide), row["locale"]))
    if hidden:
        lo = [min(b[1][i] - b[2][i] for b in hidden) for i in range(3)]
        hi = [max(b[1][i] + b[2][i] for b in hidden) for i in range(3)]
        face = hi[n] if sg > 0 else lo[n]
        fp = fitting_part(c, w, h, n, sg, wa, ha, hidden)
        if fp is not None:
            face = fp[2]           # the face of the part the picture IS on
            # … or of any part it fits (a facade picture on the wall with its
            # hidden galleries in front: on the wall is right)
            near_f = min(fp[3], key=lambda f: abs(c[n] - f))
            if abs(c[n] - near_f) <= FACE_TOL:
                face = near_f
        if abs(c[n] - face) > FACE_TOL and not on_host(c, w, h, n, sg, wa, ha, boxes,
                                                       {x[0] for x in hidden}, face) \
                and not ((c[n] - face) * sg > 0 and on_post(c, w, h, n, sg, wa, ha, boxes)):
            out.append("OFF-FACE   %s: %.2f m %s the stand-in's face (%s)" % (
                slug, abs(c[n] - face), "off" if (c[n] - face) * sg > 0 else "inside", ",".join(hide)))
        # the picture against the hidden part it best matches (a sign hides its
        # panel AND its post; a monitor its body AND its screen) and against
        # the whole stand-in: a fit to either is a fit
        def _fit(lo_, hi_):
            sw_, sh_ = hi_[wa] - lo_[wa], hi_[ha] - lo_[ha]
            cx_, cz_ = (hi_[wa] + lo_[wa]) / 2.0, (hi_[ha] + lo_[ha]) / 2.0
            off_ = max(abs(c[wa] - cx_) / max(sw_, 0.05), abs(c[ha] - cz_) / max(sh_, 0.05))
            rw_, rh_ = w / max(sw_, 0.01), h / max(sh_, 0.01)
            ok_ = off_ <= 0.15 and 0.6 <= rw_ <= 1.6 and 0.6 <= rh_ <= 1.6
            return ok_, sw_, sh_, off_
        fits = [_fit(lo, hi)]
        for b in hidden:
            fits.append(_fit([b[1][i] - b[2][i] for i in range(3)], [b[1][i] + b[2][i] for i in range(3)]))
        if not any(f[0] for f in fits):
            _ok, sw, sh, off = fits[0]
            out.append("MISFIT     %s: picture %.2fx%.2f vs stand-in %.2fx%.2f, centre off %.0f%%" % (
                slug, w, h, sw, sh, off * 100))
    else:
        # the surface it hangs on: a part whose facing side is at the quad
        # plane and covers most of the picture
        for b in boxes:
            bc, bh = b[1], b[2]
            face = bc[n] + sg * bh[n]
            if abs(face - c[n]) > FACE_TOL:
                continue
            cov = _overlap_1d(q0[0], q0[1], bc[wa] - bh[wa], bc[wa] + bh[wa]) * \
                  _overlap_1d(q1[0], q1[1], bc[ha] - bh[ha], bc[ha] + bh[ha])
            if cov >= 0.5 * area:
                support.append(b[0])
        # a window's view fills an OPENING: nothing behind it is the point
        is_view = row.get("_cat") == "WINDOW" or \
            re.search(r"window|_win\b|_win_|view|sky|horizon|glass", "%s %s" % (slug, row.get("label", "")), re.I)
        if not support and not hide and not is_view:
            out.append("FLOATING   %s: no surface behind the picture at %s" % (
                slug, ", ".join("%.2f" % v for v in c)))
    # anything standing in front of the picture
    skip = {b[0] for b in hidden} | set(support) | set(others_hidden)
    covers = collections.Counter()
    for b in boxes:
        if b[0] in skip or NONSOLID.search(b[0]):
            continue
        bc, bh = b[1], b[2]
        front0 = c[n] + sg * 0.01
        front1 = c[n] + sg * COVER_DEPTH
        lo_n, hi_n = min(front0, front1), max(front0, front1)
        if _overlap_1d(lo_n, hi_n, bc[n] - bh[n], bc[n] + bh[n]) <= 0.0:
            continue
        ov = _overlap_1d(q0[0], q0[1], bc[wa] - bh[wa], bc[wa] + bh[wa]) * \
             _overlap_1d(q1[0], q1[1], bc[ha] - bh[ha], bc[ha] + bh[ha])
        if ov / area >= COVER_FRAC:
            covers[b[0]] = ov / area
    # (2026-11-08) the picture faces INTO a solid: a body starts at its plane
    # (or the picture is inside it) and runs on in front over all of it —
    # pump screens on a pump's far side facing in, storefront signs turned
    # to the shop's own wall, a brand panel inside its wall. Seen from
    # anywhere the picture is the back of a quad, or behind the wall.
    # (2026-11-09) the solids in front are SUMMED (the grocery's entrance
    # sign faced its own wall across a lintel and two piers, none of them
    # 60 % alone) and looked for 10 cm out (the crumpled barn's sign faced
    # the gable wall 7.5 cm in front of it)
    fin = []
    for b in boxes:
        if b[0] in skip or NONSOLID.search(b[0]) or GLASSY.search(b[0]):
            continue
        bc, bh = b[1], b[2]
        near = (bc[n] - sg * bh[n] - c[n]) * sg
        far = (bc[n] + sg * bh[n] - c[n]) * sg
        # (a picture 50 m "inside" a ridge is inside its bounding box, not
        # the ridge; a sloped roof plank's box spans the gable window under
        # it; a spinner's wires are wires)
        if near > 0.10 or far < 0.04 or near < -0.30 or WIRY.search(b[0]) or \
                (row.get("_cat") == "WINDOW" and SLOPED.search(b[0])):
            continue
        ov = _overlap_1d(q0[0], q0[1], bc[wa] - bh[wa], bc[wa] + bh[wa]) * \
             _overlap_1d(q1[0], q1[1], bc[ha] - bh[ha], bc[ha] + bh[ha])
        if ov > 0:
            fin.append((ov / area, b[0], near))
    if fin and min(1.0, sum(f[0] for f in fin)) >= 0.6:
        fin.sort(reverse=True)
        out.append("FACES-IN   %s: faces into %s (%.0f%% of it, %s %.2f m)" % (
            slug, fin[0][1], min(1.0, sum(f[0] for f in fin)) * 100,
            "from" if fin[0][2] >= 0 else "buried", abs(fin[0][2])))
    # … and a stand-in's own sibling left standing in front of it (the KWIK
    # STOP letters the hide list skipped): any overlap shows
    stems = {re.sub(r"[_\d+-]+$", "", p) for p in hide}
    stems = {s_ for s_ in stems if len(s_) >= 4}
    for b in boxes:
        if b[0] in skip or not any(b[0].startswith(s_) for s_ in stems):
            continue
        bc, bh = b[1], b[2]
        near = (bc[n] - sg * bh[n] - c[n]) * sg
        far = (bc[n] + sg * bh[n] - c[n]) * sg
        # (a far hill in front of the next far hill is another object)
        if far <= 0.0005 or near > 0.10 or bh[n] * 2.0 > 0.5:
            continue
        ov = _overlap_1d(q0[0], q0[1], bc[wa] - bh[wa], bc[wa] + bh[wa]) * \
             _overlap_1d(q1[0], q1[1], bc[ha] - bh[ha], bc[ha] + bh[ha])
        if ov / area >= 0.01:
            out.append("LEFTOVER   %s: %s (the stand-in's own) stands %.3f m in front of the picture" % (
                slug, b[0], far))
    if covers:
        worst = ", ".join("%s %.0f%%" % (k, v * 100) for k, v in covers.most_common(3))
        out.append("COVERED    %s: %s" % (slug, worst))
    return out


_PRESETS = None


def presets_of(locale):
    """the Background3D presets that load this locale (a row's not_presets
    names some of them)"""
    global _PRESETS
    if _PRESETS is None:
        _PRESETS = collections.defaultdict(set)
        try:
            for pr in VO.presets():
                _PRESETS[os.path.splitext(os.path.basename(pr[1]))[0]].add(pr[0])
        except Exception:
            pass
    return _PRESETS.get(locale, set())


def shows_in(slug, row):
    """the views of the set this row's picture shows in: its slug's
    `__<preset>` suffixes (HeroArt.apply, 2026-11-08) less its not_presets"""
    pres = presets_of(row["locale"])
    own = [p for p in slug.split("__")[1:] if p in pres]
    base = set(own) if own else set(pres)
    return base - set(row.get("not_presets") or [])


def co_present(r1, r2, s1="", s2=""):
    """two rows that show in at least one view of the set together (a day
    window and its night twin never do)"""
    if not presets_of(r1["locale"]):
        return True
    return bool(shows_in(s1, r1) & shows_in(s2, r2))


def overlaps(k, rows):
    """(2026-11-08) two pictures laid on ONE plane over each other — they
    z-fight in the game (the new-arrivals comics fanned 4 cm over each
    other; two papers taped in one shop window)"""
    slug, r = rows[k]
    fc = str(r.get("facing", "")).lower()
    if fc not in AXES:
        return []
    n, _sg = AXES[fc]
    wa, ha = _plane_axes(n)
    c = [float(v) for v in r["center"]]
    w, h = float(r["size"][0]), float(r["size"][1])
    out = []
    for j, (slug2, r2) in enumerate(rows):
        if j <= k or str(r2.get("facing", "")).lower() != fc or not co_present(r, r2, slug, slug2):
            continue
        c2 = [float(v) for v in r2["center"]]
        if abs(c2[n] - c[n]) > 0.004:
            continue
        w2, h2 = float(r2["size"][0]), float(r2["size"][1])
        ov = _overlap_1d(c[wa] - w / 2, c[wa] + w / 2, c2[wa] - w2 / 2, c2[wa] + w2 / 2) * \
            _overlap_1d(c[ha] - h / 2, c[ha] + h / 2, c2[ha] - h2 / 2, c2[ha] + h2 / 2)
        # HeroArt stacks a smaller picture over a larger one on one plane
        # (HeroArt._stack): a partial overlap is a layer (the text strip on
        # its sign panel). Two of one size on one place is two pictures for
        # ONE surface: only the later shows
        if ov >= 0.95 * max(w * h, w2 * h2):
            out.append("DUPLICATE  %s: and %s are two pictures for one surface (only %s shows)" % (
                slug, slug2, slug2))
    return out


def main():
    want = set(a for a in sys.argv[1:] if not a.startswith("--"))
    roster = json.load(open(ROSTER, encoding="utf-8"))
    rows = collections.defaultdict(list)
    for e in roster.get("entries", []):
        if e.get("kind") != "art":
            continue
        for r in e.get("apply", []) or []:
            if isinstance(r, dict) and r.get("locale") and r.get("center") and r.get("size"):
                rows[r["locale"]].append((e.get("slug", "?"), dict(r, _cat=e.get("art_cat", ""))))
    total = bad = 0
    by_kind = collections.Counter()
    for loc in sorted(rows):
        if want and loc not in want:
            continue
        boxes = VO.boxes_for(loc)
        if not boxes:
            continue
        found = []
        hid_by = [{b[0] for b in hidden_by(r, boxes)} for _s, r in rows[loc]]
        for k, (slug, r) in enumerate(rows[loc]):
            total += 1
            others = set().union(*[h for j, h in enumerate(hid_by) if j != k]) if len(hid_by) > 1 else set()
            f = check_row(slug, r, boxes, others - hid_by[k])
            f += overlaps(k, rows[loc])
            if f:
                bad += 1
                found.extend(f)
                for x in f:
                    by_kind[x.split()[0]] += 1
        if found:
            print("== %s (%d of %d)" % (loc, len({x.split()[1] for x in found}), len(rows[loc])))
            for x in found:
                print("   " + x)
    print("\nhero_art_placement_audit · %d placement(s) read · %d with a finding · %s"
          % (total, bad, dict(by_kind)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
