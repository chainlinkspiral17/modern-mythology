#!/usr/bin/env python3
"""hero_art_candidates.py — what else can be a picture (2026-10-12). A report.

The user: "Do an audit to find what more can be given a hero art pass. Flat
backdrops for skies, backlots, windows, posters, monitors, TV screens,
paintings." Hero art (pass 97, scripts/vn/HeroArt.gd) lays a generated
picture on a surface and hides the box stand-in. This finds the surfaces
that are worth it, in every locale builder, and ranks them:

  PICTURE   posters, paintings, photos, prints, maps, calendars, menus,
            flyers, murals, album/comic covers, corkboards
  SCREEN    TVs, monitors, laptop / phone / drive-in screens, displays
  SIGN      signs, billboards, banners, marquees, plaques
  WINDOW    windows whose outside is empty or thin (no make_view world
            past them) — a painted view card behind the glass
  BACKLOT   the far bands at a set's edge (treelines, ridges, skylines,
            facades) — a painted panorama card instead of colour slabs
  SKY       exterior presets whose sky is the procedural gradient

Each row: the locale, the object family (its instances collapsed), its size
and the axis it faces along, the lines the locale plays (how much the
picture is seen), and how many of those lines mention the thing (the prose
calling it out). Families already covered by an art entry are marked.

    python3 godot/tools/audit/hero_art_candidates.py                # text report
    python3 godot/tools/audit/hero_art_candidates.py --json out.json
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GODOT = os.path.join(ROOT, "godot")
BUILDERS = os.path.join(GODOT, "tools", "blender", "locales")
SCENES = os.path.join(GODOT, "resources", "scenes")
BG3D = os.path.join(GODOT, "scripts", "vn", "Background3D.gd")
ROSTER = os.path.join(GODOT, "tools", "meshy_roster.json")

# whole-word vocabularies (a name splits on "_" and CamelCase: MenuBoard → menu, board)
CATS = {
    "SCREEN": {"screen", "monitor", "tv", "television", "crt", "display", "tablet", "jumbotron"},
    "PICTURE": {"poster", "painting", "portrait", "print", "prints", "photo", "photos", "photograph", "picture", "pictures",
                "mural", "canvas", "artwork", "map", "chart", "calendar", "diploma", "certificate", "menu", "flyer",
                "postcard", "drawing", "sketch", "album", "cover", "covers", "corkboard", "bulletin", "collage", "comic", "comics"},
    "SIGN": {"sign", "signs", "billboard", "banner", "marquee", "placard", "plaque", "logo", "neon", "decal"},
}
# a part word that says the piece is the hardware, not the picture
HARDWARE = {"glass", "frame", "casing", "trim", "bracket", "post", "pole", "leg", "legs", "rail", "hinge", "knob", "seam",
            "mullion", "muntin", "light", "lamp", "bulb", "stand", "base", "mount", "wire", "cord", "cable", "tray", "edge",
            "kick", "door", "case", "shelf", "rack", "cabinet", "belt", "lid", "vent", "drain", "outlet", "switch", "chain",
            "bolt", "arm", "pin", "tack", "nail", "hook", "clip", "printer", "sill", "head", "foot"}
# mention words in the prose per keyword (stems; the keyword itself is always used)
MENTION = {"tv": r"tv|television|screen|broadcast|channel", "television": r"tv|television|screen|broadcast",
           "screen": r"screen|tv|television|monitor", "monitor": r"monitor|screen", "crt": r"screen|monitor|crt",
           "display": r"display|screen", "menu": r"menu|board", "comic": r"comic|cover", "comics": r"comic|cover",
           "cover": r"cover|comic", "covers": r"cover|comic", "print": r"print|photo", "prints": r"print|photo",
           "neon": r"neon|sign", "logo": r"logo|sign"}
BACKLOT = {"far", "backdrop", "horizon", "treeline", "skyline", "ridge", "bluff", "hill", "hills", "mountain",
           "mountains", "band", "bg", "distant", "beyond", "facade", "facades", "skyline"}
WINDOW_PARTS = ({"window", "win", "windows"}, {"glass", "pane", "glasspane", "glasspanel"})
SPLIT = re.compile(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])|\d+")


def words(name):
    return [w.lower() for w in SPLIT.findall(name)]


def presets():
    src = open(BG3D).read()
    out = {}
    for m in re.finditer(r'\t"([a-z0-9_]+)": \{\n((?:\t\t[^\n]*\n)*?)\t\},', src):
        body = m.group(2)
        sc = re.search(r'"scene": "res://scenes/locales/([a-z0-9_]+)\.tscn"', body)
        if sc:
            cam = re.search(r'"camera_origin": Vector3\(([-\d.]+), ([-\d.]+), ([-\d.]+)\)', body)
            cb = (float(cam.group(1)), -float(cam.group(3)), float(cam.group(2))) if cam else None   # godot → blender
            out[m.group(1)] = {"locale": sc.group(1), "sky": '"sky_top"' in body, "cam": cb}
    return out


def lines_by_locale(pre):
    """narrate/say lines per locale, and the lines themselves (for mentions)."""
    by = defaultdict(list)
    for f in glob.glob(os.path.join(SCENES, "vol*", "*.json")):
        try:
            d = json.load(open(f))
        except (OSError, ValueError):
            continue
        nodes = d.get("nodes") if isinstance(d, dict) else d
        if not isinstance(nodes, list):
            continue
        cur = None
        for n in nodes:
            if not isinstance(n, dict):
                continue
            if n.get("t") == "bg":
                s = str(n.get("src", ""))
                cur = pre.get(s[3:], {}).get("locale") if s.startswith("3d:") else None
                continue
            if cur and n.get("text") and n.get("t") in ("narrate", "say", "think"):
                by[cur].append(re.sub(r"\[[^\]]*\]", "", n["text"]).lower())
    return by


def art_covered():
    try:
        r = json.load(open(ROSTER))
    except (OSError, ValueError):
        return set()
    out = set()
    for e in r.get("entries", []):
        if e.get("kind") == "art":
            for row in e.get("apply", []):
                for h in row.get("hide", []) or []:
                    out.add((row.get("locale"), h.rstrip("_")))
    return out


def root(name, key):
    """The object a piece belongs to: its name up to and including the
    keyword word (Sanderling_Mural_Sky → Sanderling_Mural)."""
    parts = [p for p in re.sub(r"\{[^}]*\}", "", name).split("_") if p]
    for i, p in enumerate(parts):
        if key in words(p):
            keep = [q for q in parts[:i + 1] if not re.fullmatch(r"[+\-]?\d+(\.\d+)?|[A-Z]?\d+|x[+\-]\d+", q)]
            return "_".join(keep)
    return re.sub(r"(_[+\-]?\d+(\.\d+)?)+$", "", name)


def scan():
    import prop_overlap_audit as P
    pre = presets()
    lines = lines_by_locale(pre)
    covered = art_covered()
    rows = []
    views = defaultdict(int)
    sky_locales = defaultdict(int)
    for p, v in pre.items():
        if v["sky"]:
            sky_locales[v["locale"]] += 1
    for b in sorted(glob.glob(os.path.join(BUILDERS, "build_*.py"))):
        loc = os.path.basename(b)[6:-3]
        devnull = open(os.devnull, "w")
        old = sys.stdout
        sys.stdout = devnull
        try:
            P.record_builder(b)
        finally:
            sys.stdout = old
            devnull.close()
        groups = defaultdict(list)       # (cat, key, root) → pieces
        for bx in P.A.BOXES:
            name, c, sz = bx[0], bx[1], bx[2]
            if re.match(r"(View|Thru|Out|Beyond|Yard|Lot|Hemlock|Street|Across|Forest|Far)_|.*_View_", name):
                views[loc] += 1
            ws = set(words(name))
            dims = sorted(sz)
            hit = None
            for cat, vocab in CATS.items():
                k = next((w for w in words(name) if w in vocab), None)
                if k in ("screen",) and ws & {"knee", "porch", "mesh", "insect", "fly", "privacy", "fire"}:
                    k = None      # a porch's insect screen, not a display
                if k and not (ws & HARDWARE) and dims[0] <= 0.10 and dims[1] * dims[2] >= 0.004:
                    hit = (cat, k)
                    break
            if hit is None and (ws & WINDOW_PARTS[0]) and (ws & WINDOW_PARTS[1]) and dims[0] <= 0.06 and dims[1] * dims[2] >= 0.25:
                hit = ("WINDOW", "window")
            if hit is None:
                k = next((w for w in words(name) if w in BACKLOT), None)
                if (k and dims[2] >= 4.0 and sz[2] >= 1.5
                        and not ws & {"roof", "hull", "saloon", "wear", "trim", "stripe", "red", "ground", "floor", "sidewalk", "road", "curb"}):
                    hit = ("BACKLOT", k)
            if hit:
                groups[(hit[0], hit[1], root(name, hit[1]))].append((name, c, sz))
        # PAINTED: a picture FAKED from flat coloured boxes on one plane (the
        # alley face's bands, the Starfish Nebula's arms) — named for its
        # subject, so no keyword finds it. Pieces sharing a first name word,
        # all thin along the same axis, all in one plane: the box stand-in of
        # a picture, and the most direct hero-art replacement.
        by_prefix = defaultdict(list)
        for bx in P.A.BOXES:
            name, c, sz = bx[0], bx[1], bx[2]
            ws = words(name)
            if not ws or set(ws) & {"seam", "stripe", "line", "dash", "tile", "wear", "stain", "grime", "shadow", "zebra",
                                      "crosswalk", "lane", "rug", "mat", "floor", "ceil", "wall", "base", "trim", "glass",
                                      "frame", "shelf", "board", "plank", "step", "puddle", "edge", "curb", "sidewalk"}:
                continue
            dims = sorted(sz)
            if dims[0] <= 0.03 and dims[1] * dims[2] >= 0.01:
                by_prefix[name.split("_")[0]].append((name, c, sz))
        STRUCTURE = {"counter", "store", "alley", "aisle", "fluor", "fluortube", "road", "ceiling", "ground", "drive", "turf",
                     "hash", "ditch", "sewergrate", "diffuserglow", "checkout", "meat", "booth", "out", "back", "num",
                     "door", "cab", "car", "truck", "roof", "porch", "deck", "fence", "bldg", "house", "lot", "street",
                     "window", "win", "case", "cooler", "fridge", "freezer", "shelf", "rack", "pallet", "box", "crate"}
        for pref, inst in by_prefix.items():
            if len(inst) < 4 or pref.lower() in STRUCTURE or any(g[2] == pref for g in groups):
                continue
            axes = defaultdict(list)
            for name, c, sz in inst:
                axes[list(sz).index(min(sz))].append((name, c, sz))
            ax, members = max(axes.items(), key=lambda kv: len(kv[1]))
            if ax == 2:
                continue        # flat on the ground or the ceiling: markings, not a picture
            planes = [m[1][ax] for m in members]
            if len(members) < 4 or max(planes) - min(planes) > 0.06:
                continue
            area = sum(sorted(m[2])[1] * sorted(m[2])[2] for m in members)
            if area < 0.3 or len({re.sub(r"(_[+\-]?\d+)+$", "", m[0]) for m in members}) < 3:
                continue
            groups[("PAINTED", pref.lower(), pref + "_*")] = members
        loc_lines = lines.get(loc, [])
        for (cat, key, rt), inst in groups.items():
            surfs = surfaces(inst)
            sf = max(surfs, key=lambda t: sorted(t["dims"])[1] * sorted(t["dims"])[2])
            c, sz = sf["center"], sf["dims"]
            dims = sorted(sz)
            pat = r"\b(" + MENTION.get(key, re.escape(key.rstrip("s"))) + r")\w*"
            if cat == "WINDOW":
                pat = r"\bwindow"
            if cat == "PAINTED":
                pat = r"\b(" + re.escape(key) + r"|mural|painting|painted)\w*"
            if cat == "BACKLOT":
                pat = r"\b(forest|woods|trees|treeline|ridge|hills?|mountains?|skyline|across the street|buildings|bluff|horizon|the sea|ocean)\b"
            hits_txt = [t for t in loc_lines if re.search(pat, t)]
            ment = len(hits_txt)
            quote = ""
            if hits_txt:
                # prefer the line that names THIS object (the family's own words), then the shortest
                own = [w for w in words(rt) if len(w) > 3 and w not in (key, "wall", "board", "left", "right")]
                best = min(hits_txt, key=lambda t: (-sum(1 for w in own if w in t), len(t)))
                quote = best.strip()[:220]
            total_area = sum(sorted(t[2])[1] * sorted(t[2])[2] for t in inst)
            rows.append({"cat": cat, "locale": loc, "family": rt, "key": key, "count": len(inst), "area": round(total_area, 3),
                         "pieces": sorted({n for n, _, _ in inst})[:6],
                         "size": [round(dims[2], 2), round(dims[1], 2)], "thin_axis": "xyz"[list(sz).index(dims[0])],
                         "dims": [round(v, 3) for v in sz],
                         "surfaces": surfs,
                         "center": [round(v, 2) for v in c], "lines": len(loc_lines), "mentions": ment, "quote": quote,
                         "covered": any(l == loc and (rt.rstrip("*").rstrip("_").startswith(h) or h.startswith(rt.rstrip("*").rstrip("_"))) for (l, h) in covered),
                         "has_view": False})
        for r in rows:
            if r["locale"] == loc:
                r["has_view"] = views[loc] > 0
    for loc, n in sky_locales.items():
        rows.append({"cat": "SKY", "locale": loc, "area": 0.0, "family": "(procedural sky)", "count": n, "size": [0, 0],
                     "thin_axis": "-", "center": [0, 0, 0], "lines": len(lines.get(loc, [])),
                     "mentions": sum(1 for t in lines.get(loc, []) if re.search(r"\b(sky|clouds?|sunset|sunrise|dawn|dusk|stars)\b", t)),
                     "covered": False, "has_view": True})
    # a draft `apply` row per candidate: facing toward the locale's preset camera
    cams = defaultdict(list)
    for v in pre.values():
        if v.get("cam"):
            cams[v["locale"]].append(v["cam"])
    for r in rows:
        if r["cat"] == "SKY" or not cams.get(r["locale"]):
            continue
        cam = cams[r["locale"]][0]
        c = r["center"]
        ax = r["thin_axis"]
        if r["cat"] == "BACKLOT" or ax == "z" and r["size"][1] > 3.0:
            # a backdrop stands up: face it along the horizontal axis toward the camera
            dx, dy = cam[0] - c[0], cam[1] - c[1]
            facing = ("+x" if dx >= 0 else "-x") if abs(dx) >= abs(dy) else ("+y" if dy >= 0 else "-y")
        elif ax == "z":
            facing = "up"
        else:
            i = "xy".index(ax)
            facing = ("+" if cam[i] >= c[i] else "-") + ax
        r["apply"] = {"locale": r["locale"], "label": r["family"], "center": c, "size": wh(r, facing), "facing": facing,
                      "hide": [r["family"].rstrip("*")]}
        # one row per surface (2026-10-13): each its own centre and true size
        rows_all = []
        for sf in r.get("surfaces") or []:
            sub = dict(r, dims=sf["dims"])
            sc = sf["center"]
            f = facing
            if r["cat"] == "BACKLOT" or ax == "z" and r["size"][1] > 3.0:
                # each band of a backdrop turns to the camera on its own
                dx, dy = cam[0] - sc[0], cam[1] - sc[1]
                f = ("+x" if dx >= 0 else "-x") if abs(dx) >= abs(dy) else ("+y" if dy >= 0 else "-y")
            elif ax in "xy":
                i = "xy".index(ax)
                f = ("+" if cam[i] >= sc[i] else "-") + ax
            # hide exactly this surface's pieces (a window's glass, not its
            # frame); a surface of many pieces hides by the family name
            fam = r["family"].rstrip("*").rstrip("_")
            hide = sf["pieces"] if len(sf["pieces"]) <= 24 else [fam, fam + "_"]
            rows_all.append({"locale": r["locale"], "label": r["family"], "center": sc, "size": wh(sub, f),
                             "facing": f, "hide": hide, "pieces": sf["pieces"][:8]})
        r["apply_all"] = rows_all
    return rows


def surfaces(inst, gap=0.05, plane=0.06):
    """Pieces → the separate surfaces they make (2026-10-13). A family name
    (Poster_*, Window_*) gathers every instance in a room; pieces that touch
    (within `gap`) on one plane (thin along the same axis, within `plane`) are
    one picture. Each surface: its bounding-box centre and extents, Blender
    frame, and its piece names."""
    n = len(inst)
    par = list(range(n))

    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i
    boxes = []
    for name, c, sz in inst:
        ax = list(sz).index(min(sz))
        boxes.append((ax, [c[k] - sz[k] / 2 for k in range(3)], [c[k] + sz[k] / 2 for k in range(3)]))
    for i in range(n):
        for j in range(i + 1, n):
            ai, lo_i, hi_i = boxes[i]
            aj, lo_j, hi_j = boxes[j]
            if ai != aj or abs((lo_i[ai] + hi_i[ai]) - (lo_j[ai] + hi_j[ai])) / 2 > plane:
                continue
            if all(lo_i[k] - gap <= hi_j[k] and lo_j[k] - gap <= hi_i[k] for k in range(3)):
                par[find(i)] = find(j)
    clusters = defaultdict(list)
    for i in range(n):
        clusters[find(i)].append(i)
    out = []
    for idx in clusters.values():
        lo = [min(boxes[i][1][k] for i in idx) for k in range(3)]
        hi = [max(boxes[i][2][k] for i in idx) for k in range(3)]
        out.append({"center": [round((lo[k] + hi[k]) / 2, 3) for k in range(3)],
                    "dims": [round(hi[k] - lo[k], 3) for k in range(3)],
                    "pieces": sorted(inst[i][0] for i in idx)})
    out.sort(key=lambda t: -(sorted(t["dims"])[1] * sorted(t["dims"])[2]))
    return out


def wh(r, facing):
    """The picture's [width, height] as the viewer sees it (2026-10-13). The
    row's `size` is largest-first and lost which side is up — a tall poster
    read as landscape, and the hero tool generated it the wrong shape. A
    picture facing ±x spans y by z; facing ±y, x by z; facing up, x by y."""
    d = r.get("dims") or [r["size"][0], r["size"][1], r["size"][1]]
    if facing in ("+x", "-x"):
        w, h = d[1], d[2]
    elif facing in ("+y", "-y"):
        w, h = d[0], d[2]
    else:
        w, h = d[0], d[1]
    if r["cat"] == "BACKLOT" and facing != "up":
        # a backdrop card stands up across the band's long side
        w, h = max(d[0], d[1]), d[2]
    return [round(w, 2), round(h, 2)]


def score(r):
    # seen x called out x big enough to read: a wall of comic covers outranks one print
    vis = 1.0 if r["cat"] == "SKY" else min(1.0, (r.get("area", 0.0) ** 0.5) / 0.8)
    if r["cat"] == "WINDOW" and r.get("has_view"):
        vis *= 0.4        # something is already built past it
    return r["lines"] * (1.0 + min(r["mentions"], 20) / 4.0) * vis


def main():
    rows = scan()
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        json.dump(rows, open(out, "w"), indent=1)
    by = defaultdict(list)
    for r in rows:
        by[r["cat"]].append(r)
    for cat in ("PAINTED", "PICTURE", "SCREEN", "SIGN", "WINDOW", "BACKLOT", "SKY"):
        rr = sorted(by.get(cat, []), key=score, reverse=True)
        print("== %s · %d candidate(s)" % (cat, len(rr)))
        for r in rr[:30]:
            print("   %-28s %-34s x%-3d %5.2f x %-5.2f m  lines %-4d mentions %-3d%s%s" % (
                r["locale"], r["family"][:34], r["count"], r["size"][0], r["size"][1],
                r["lines"], r["mentions"], "  (art entry)" if r["covered"] else "",
                "  (view built)" if r["cat"] == "WINDOW" and r.get("has_view") else ""))
    print("hero_art_candidates · %d surface(s) across %d locale(s)" % (len(rows), len({r['locale'] for r in rows})))


if __name__ == "__main__":
    main()
