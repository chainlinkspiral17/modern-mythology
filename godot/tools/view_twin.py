#!/usr/bin/env python3
"""view_twin.py — make a TWIN of a view: the same camera, lights and frames,
for chapters whose dressing differs (2026-11-15, pass 400).

Passes 396-399 staged chapter state on shared sets by giving the state its
own view (henderson_kitchen_supper, finn_apartment_stick, _hexagon) and
tagging the state's parts to it. Each copy was made by hand, and each hand
copy lost something: pass 397's twins lost the room's light rig (tagged to
the original view; rig_twin_audit now gates it), and a copy spliced onto the
preceding preset's closing line hid it from every line-based audit. This
does the copy the same way every time:

  1. Background3D.CAMERA_PRESETS: FROM's block copied as TO (with --note),
     on its own lines, right after FROM's.
  2. locale_ambient.json and wide_views.json: FROM's entries copied.
  3. The set's .tscn: every node that is not a shot marker and is tagged
     FROM (`Name__FROM`, alone or among other tags) gains `__TO` — the rig,
     the practicals, any tscn-authored dressing (parent= paths follow).
  4. Shot markers `shot_*__FROM`: the establishing frames and face frames
     are copied as `__TO` (the director reaches for them unasked); an insert
     frame is copied only when a moved segment cues it (an uncued copy would
     be an orphan frame).
  5. The bg nodes named by --scenes (`file.json:node`) point at TO.
  6. Builder parts tagged FROM are LISTED, not changed (a GLB part's name is
     the builder's): tag them by hand or with a VIEW_GROUPS group.
  7. The hero-art roster: a picture that skips FROM (`not_presets`) skips TO
     too — a day twin showed the night window pictures beside the day ones
     until pass 400 (hero_art_placement_audit DUPLICATE). Byte-exact.
  8. A copied frame already judged by render (half_hidden_baseline.json
     `judged`) is judged in TO too: it is the same frame.

    python3 godot/tools/view_twin.py FROM TO --scenes vol7/vol7_ch13_marina.json:0 \
        [--note "why this view exists"] [--dry]
"""
import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GODOT = os.path.normpath(os.path.join(HERE, ".."))
B3D = os.path.join(GODOT, "scripts", "vn", "Background3D.gd")
AMBIENT = os.path.join(GODOT, "resources", "audio", "locale_ambient.json")
WIDE = os.path.join(GODOT, "resources", "vn", "wide_views.json")
SCENES = os.path.join(GODOT, "resources", "scenes")
LOCALES = os.path.join(GODOT, "tools", "blender", "locales")
CUE = re.compile(r"\[shot:(\w+)(?: (\w+))?~?\]")


def preset_block(src, view):
    m = re.search(r'^\t"%s": \{\n.*?^\t\},\n' % re.escape(view), src, re.M | re.S)
    return m


def loc_of(scene):
    return os.path.splitext(os.path.basename(scene))[0]


def segment_cues(path, node):
    data = json.load(open(path, encoding="utf-8"))
    nodes = data if isinstance(data, list) else data.get("nodes", [])
    cues = set()
    for n in nodes[node + 1:]:
        if not isinstance(n, dict):
            continue
        if n.get("t") == "bg":
            break
        for m in CUE.finditer(n.get("text") or ""):
            kind, name = m.group(1), m.group(2)
            cues.add("shot_%s_%s" % (kind, name) if name else "shot_%s" % kind)
    return nodes, cues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--scenes", default="", help="comma list of <scenes-relative json>:<bg node index>")
    ap.add_argument("--note", default="")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    FROM, TO = a.src, a.dst
    if not re.match(r"^[a-z0-9_]+$", TO):
        sys.exit("view id must be [a-z0-9_]+")
    b3d = open(B3D, encoding="utf-8").read()
    m = preset_block(b3d, FROM)
    if not m:
        sys.exit("no preset %s in CAMERA_PRESETS" % FROM)
    if preset_block(b3d, TO):
        sys.exit("preset %s exists already" % TO)
    blk = m.group(0)
    scene = re.search(r'"scene": "res://([^"]+)"', blk).group(1)
    note = "".join("\t\t# %s\n" % ln for ln in a.note.splitlines()) if a.note else ""
    twin = blk.replace('\t"%s": {\n' % FROM, '\t"%s": {\n%s' % (TO, note), 1)
    b3d = b3d[:m.end()] + twin + b3d[m.end():]
    log = ["preset %s → %s (%s)" % (FROM, TO, scene)]

    # the moved segments, and the inserts they cue
    moves, cued = [], set()
    for spec in [s for s in a.scenes.split(",") if s.strip()]:
        f, _, n = spec.strip().rpartition(":")
        path = os.path.join(SCENES, f)
        nodes, cues = segment_cues(path, int(n))
        src_ = str(nodes[int(n)].get("src", ""))
        if nodes[int(n)].get("t") != "bg" or src_ != "3d:" + FROM:
            sys.exit("%s node %s is not a bg on 3d:%s (%s)" % (f, n, FROM, src_))
        moves.append((path, int(n)))
        cued |= cues

    # the .tscn
    tpath = os.path.join(GODOT, scene)
    tscn = open(tpath, encoding="utf-8").read()
    renames = {}
    for mm in re.finditer(r'\[node name="([^"]+)" type="([A-Za-z0-9]+)"', tscn):
        name, typ = mm.group(1), mm.group(2)
        if FROM in name.split("__")[1:] and not (typ == "Marker3D" and name.startswith("shot_")):
            renames[name] = name + "__" + TO
    for old, new in renames.items():
        tscn = tscn.replace('[node name="%s" ' % old, '[node name="%s" ' % new)
        tscn = tscn.replace('parent="%s"' % old, 'parent="%s"' % new).replace('parent="%s/' % old, 'parent="%s/' % new)
    # the copies go in from the end of the file back, so no position moves
    # (the renames above are done first, on the text the matches came from
    # — so take the matches again from the renamed text)
    out, copies = [], []
    for mm in re.finditer(r'\[node name="(shot_[^"]+)" type="Marker3D"[^\n]*\]\n(?:[^\n\[;][^\n]*\n)*', tscn):
        name = mm.group(1)
        if name.split("__")[1:] != [FROM]:
            continue
        base = name.split("__")[0]
        if base.startswith("shot_insert_") and base not in cued:
            continue
        dup = mm.group(0).replace('[node name="%s"' % name, '[node name="%s__%s"' % (base, TO), 1)
        out.append((mm.end(), "\n; (view_twin) %s's frame in %s\n%s" % (FROM, TO, dup)))
        copies.append(base)
    for pos, text in sorted(out, key=lambda x: -x[0]):
        tscn = tscn[:pos] + text + tscn[pos:]
    log.append("tscn: %d node(s) tagged %s gain __%s; %d frame(s) copied" % (len(renames), FROM, TO, len(copies)))
    for o in sorted(renames):
        log.append("   + %s" % renames[o])
    for base in copies:
        log.append("   frame %s__%s" % (base, TO))

    # ambient + wide
    amb = open(AMBIENT, encoding="utf-8").read()
    am = re.search(r'\n    "%s": \{[^}]*\}' % re.escape(FROM), amb)
    if am:
        amb = amb[:am.end()] + "," + am.group(0).replace('"%s"' % FROM, '"%s"' % TO, 1) + amb[am.end():]
        json.loads(amb)
        log.append("locale_ambient: copied")
    wide = open(WIDE, encoding="utf-8").read()
    if re.search(r'\n  "%s",\n' % re.escape(FROM), wide):
        wide = wide.replace('\n  "%s",\n' % FROM, '\n  "%s",\n  "%s",\n' % (FROM, TO), 1)
        log.append("wide_views: expand")
    else:
        wm = re.search(r'\n  "%s": ("[^"]*"),?\n' % re.escape(FROM), wide)
        if wm:
            wide = wide[:wm.end()] + '  "%s": %s,\n' % (TO, wm.group(1)) + wide[wm.end():]
            log.append("wide_views: held, copied")
    json.loads(wide)

    # builder parts tagged FROM: listed
    loc = os.path.splitext(os.path.basename(scene))[0]
    bpath = os.path.join(LOCALES, "build_%s.py" % loc)
    if os.path.exists(bpath):
        for i, ln in enumerate(open(bpath, encoding="utf-8"), 1):
            # a tag ends at a quote, a brace, or the next tag: `__FROM_more` is another view
            if re.search(r'__%s(?=["\'{]|__)' % re.escape(FROM), ln) or ('"%s"' % FROM in ln and "make_" in ln):
                log.append("   BUILDER %s:%d tags %s — add %s by hand: %s" % (os.path.basename(bpath), i, FROM, TO, ln.strip()[:90]))

    # the roster's skip lists
    rpath = os.path.join(GODOT, "tools", "meshy_roster.json")
    rraw = open(rpath, encoding="utf-8").read()
    roster = json.loads(rraw)
    nskip = 0
    for e in roster.get("entries", []):
        for row in e.get("apply") or []:
            skip = row.get("not_presets")
            if isinstance(skip, list) and FROM in skip and TO not in skip:
                skip.append(TO)
                nskip += 1
                log.append("   roster %s skips %s too" % (e["slug"], TO))
    rout = json.dumps(roster, indent=2, ensure_ascii=False) + "\n"
    assert json.dumps(json.loads(rout), indent=2, ensure_ascii=False) + "\n" == rout

    # frames judged by render are judged in the twin
    hpath = os.path.join(GODOT, "tools", "audit", "half_hidden_baseline.json")
    hraw = open(hpath, encoding="utf-8").read()
    half = json.loads(hraw)
    nj = 0
    for base in copies:
        k_from, k_to = "%s:%s__%s" % (loc_of(scene), base, FROM), "%s:%s__%s" % (loc_of(scene), base, TO)
        if k_from in half.get("judged", {}) and k_to not in half["judged"]:
            half["judged"][k_to] = "(view_twin) %s's frame, as judged: %s" % (FROM, half["judged"][k_from])
            nj += 1
            log.append("   judged %s" % k_to)

    for path, n in moves:
        raw = open(path, encoding="utf-8").read()
        nodes = json.loads(raw)
        lst = nodes if isinstance(nodes, list) else nodes["nodes"]
        lst[n]["src"] = "3d:" + TO
        # rewrite only that node's src: find the n-th bg occurrence textually
        idx, count = -1, 0
        for k, nd in enumerate(lst):
            if isinstance(nd, dict) and nd.get("t") == "bg" and k < n and json.dumps(nd.get("src")) == '"3d:%s"' % FROM:
                count += 1
        pos = -1
        for _ in range(count + 1):
            pos = raw.index('"3d:%s"' % FROM, pos + 1)
        raw = raw[:pos] + '"3d:%s"' % TO + raw[pos + len('"3d:%s"' % FROM):]
        assert json.loads(raw)
        if not a.dry:
            open(path, "w", encoding="utf-8").write(raw)
        log.append("scene %s#%d → 3d:%s" % (os.path.relpath(path, SCENES), n, TO))

    if not a.dry:
        open(B3D, "w", encoding="utf-8").write(b3d)
        open(tpath, "w", encoding="utf-8").write(tscn)
        open(AMBIENT, "w", encoding="utf-8").write(amb)
        open(WIDE, "w", encoding="utf-8").write(wide)
        if nskip:
            open(rpath, "w", encoding="utf-8").write(rout)
        if nj:
            open(hpath, "w", encoding="utf-8").write(json.dumps(half, indent=1, ensure_ascii=False))
    print("\n".join(log))
    print("view_twin · %s%s → %s" % ("[DRY] " if a.dry else "", FROM, TO))


if __name__ == "__main__":
    main()
