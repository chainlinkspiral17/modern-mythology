#!/usr/bin/env python3
"""empty_frame_audit.py — frames, posters and screens with no picture (2026-11-09).

The user: "lots of frames still showing as empty, not sure if that's where
art is going or not, seems like it should be." A builder hangs a frame as a
thin coloured slab; the picture comes from a roster art row (meshy_roster.json,
kind "art", an `apply` row: locale, center, size, facing, hide). A frame no
row covers stays a flat rectangle of colour for good.

For every set: the PICTURE SURFACES — thin slabs (under 4 cm through) whose
name says frame / poster / picture / painting / photo / print / canvas / flyer
/ diploma / calendar / map / chart / mural / screen / monitor — and, of those,
the ones no art row covers (hidden by a row's `hide` list, or under a row's
quad over half their face). A procedural picture's parts (its frame, field,
figure, title) are grouped into ONE picture; shelf stock, glazing bars and
seat-back monitors are left out.

    python3 tools/audit/empty_frame_audit.py                 # every set, a count per set
    python3 tools/audit/empty_frame_audit.py caltech_dabney  # the parts, with place and size
    python3 tools/audit/empty_frame_audit.py --json out.json # machine-readable, every set

A report for writing roster rows from (the user generates the pictures;
this lists what is missing). Not a gate.
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vantage_obstruction_audit as VO  # noqa: E402
import hero_art_placement_audit as HA  # noqa: E402

SURFACE = re.compile(r"frame|poster|picture|painting|photo|print(?!er)|canvas|flyer|flier|diploma|certificate|"
                     r"calendar|(?<![a-z])map(?![a-z])|chart|mural|artwork|_art(?![a-z])|screen|monitor|"
                     r"album|record_sleeve|postcard|polaroid|drawing|sketch", re.I)
NOT = re.compile(r"window|door|bed_?frame|frame_(top|bot|bottom|left|right|l|r|n|s|e|w|[0-9]+)$|_frame_(top|bot|bottom|left|right)|"
                 r"screen_door|porch_screen|windscreen|sunscreen|fire_?screen|smoke|privacy|_glow|_glint|_stand|_foot|_bezel|"
                 r"_body|_back$|_leg|_cable|_cord|_bracket|_mount|_shelf|_post|_pole|scaffold|truss|chassis|"
                 r"wear_|stain|shadow|fluor|troffer|light|lamp|vent|grille|ceil|skylight|"
                 r"fridge|cooler|freezer|oven|microwave|washer|dryer|display_case|case_|aquarium|"
                 r"camera|projector|speaker|radio|phone|laptop_base|keyboard", re.I)
MIN_SIDE = 0.12
MAX_THICK = 0.04
# not pictures: stock on shelves, the glazing bars of a window, a seat-back
# monitor, an appliance's frame
NOISE = re.compile(r"winframe|_stock_|stock_|hvac|elevator|cabseat|magrack|emptyslot|photo_book|bldg_win|"
                   r"pinned_dummy|chartpocket|score_screen", re.I)
# the parts ONE picture is built from (a procedural poster: its frame, its
# field, a figure's head and shoulders, a title bar): one picture, one row
PART = re.compile(r"_(frame|field|figure|title|print|mat|pic|picture|paper|image|face|head|shoulders|band|grid|"
                  r"stripe|line|text|caption|glass|border|bg|ground|sky|sun|body|label)(_?[0-9]+)*$", re.I)


def stem_of(name):
    prev = None
    while prev != name:
        prev = name
        name = PART.sub("", name)
    return name


def pictures(parts):
    """group a set's empty surfaces into pictures: {stem: [parts]} with the
    group's largest face as its size"""
    groups = collections.OrderedDict()
    for p in parts:
        if NOISE.search(p[0]):
            continue
        groups.setdefault(stem_of(p[0]), []).append(p)
    return groups


def surfaces(boxes):
    out = []
    for n, c, h in boxes:
        if not SURFACE.search(n) or NOT.search(n):
            continue
        ext = sorted(((2.0 * h[i], i) for i in range(3)))
        thick, axis = ext[0]
        if thick > MAX_THICK or ext[1][0] < MIN_SIDE:
            continue
        out.append((n, c, h, axis))
    # a frame and its picture ("Frame_Small_0" + "Frame_Small_0_Pic") are one
    # surface: keep the picture
    names = {p[0] for p in out}
    return [p for p in out if not any(o != p[0] and o.startswith(p[0] + "_") and
                                      re.search(r"_(pic|picture|image|photo|art|print|paper|canvas|screen|face)$", o, re.I)
                                      for o in names)]


def covered_names(loc, rows, boxes):
    names = set()
    for _slug, r in rows:
        for b in HA.hidden_by(r, boxes):
            names.add(b[0])
    return names


def under_quad(part, rows):
    n, c, h, axis = part
    wa, ha = HA._plane_axes(axis)
    area = (2 * h[wa]) * (2 * h[ha])
    for _slug, r in rows:
        fc = str(r.get("facing", "")).lower()
        if fc not in HA.AXES or HA.AXES[fc][0] != axis:
            continue
        rc = [float(v) for v in r["center"]]
        if abs(rc[axis] - c[axis]) > 0.20:
            continue
        rw, rh = float(r["size"][0]) / 2.0, float(r["size"][1]) / 2.0
        ow = HA._overlap_1d(c[wa] - h[wa], c[wa] + h[wa], rc[wa] - rw, rc[wa] + rw)
        oh = HA._overlap_1d(c[ha] - h[ha], c[ha] + h[ha], rc[ha] - rh, rc[ha] + rh)
        if area > 0 and ow * oh >= 0.5 * area:
            return True
    return False


def main():
    want = [a for a in sys.argv[1:] if not a.startswith("--") and not a.endswith(".json")]
    out_json = None
    if "--json" in sys.argv:
        out_json = sys.argv[sys.argv.index("--json") + 1]
    roster = json.load(open(HA.ROSTER, encoding="utf-8"))
    rows = collections.defaultdict(list)
    for e in roster.get("entries", []):
        if e.get("kind") != "art":
            continue
        for r in e.get("apply", []) or []:
            if isinstance(r, dict) and r.get("locale") and r.get("center") and r.get("size"):
                rows[r["locale"]].append((e.get("slug", "?"), r))
    locs = want or sorted({f[6:-3] for f in os.listdir(os.path.join(HERE, "..", "blender", "locales"))
                           if f.startswith("build_") and f.endswith(".py")})
    total = sets = 0
    report = {}
    for loc in locs:
        try:
            boxes = VO.boxes_for(loc)
        except Exception:
            continue
        if not boxes:
            continue
        surf = surfaces(boxes)
        if not surf:
            continue
        hid = covered_names(loc, rows[loc], boxes)
        empty = [p for p in surf if p[0] not in hid and not under_quad(p, rows[loc])]
        if not empty:
            continue
        groups = pictures(empty)
        if not groups:
            continue
        sets += 1
        total += len(groups)
        report[loc] = []
        for stem, parts in groups.items():
            n, c, h, ax = max(parts, key=lambda q: q[2][HA._plane_axes(q[3])[0]] * q[2][HA._plane_axes(q[3])[1]])
            wa, ha = HA._plane_axes(ax)
            report[loc].append({"picture": stem, "parts": [q[0] for q in parts], "center": [round(v, 3) for v in c],
                                "size": [round(2 * h[wa], 3), round(2 * h[ha], 3)], "normal_axis": "xyz"[ax]})
        if want:
            print("== %s · %d picture(s) with no art row" % (loc, len(groups)))
            for r in report[loc]:
                print("   EMPTY  %-34s %.2f x %.2f m  at (%.2f, %.2f, %.2f)  · %d part(s)" % (
                    r["picture"], r["size"][0], r["size"][1], *r["center"], len(r["parts"])))
        else:
            print("%-30s %3d empty picture(s)" % (loc, len(groups)))
    print("empty_frame_audit · %d set(s) · %d picture(s) with no art row" % (sets, total))
    if out_json:
        json.dump(report, open(out_json, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
