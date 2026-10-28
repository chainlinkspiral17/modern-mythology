#!/usr/bin/env python3
"""text_focus_pass.py — the camera goes where the sentence looks (2026-10-27).

The Deck: "shots aren't focusing on what the text is describing ... direction
pass, camera placement pass." shot_seed.py cuts by spacing and only to markers
a set already has; a line naming "the microwave clock" or "the spiral
notebook" in a set with no such marker held the wide. This pass reads each
narrated line, finds the first thing it NAMES that the set really has in view
(the builder's part names, through marker_aim_audit.matches_for), makes sure a
marker frames it — authoring one from the current view's side when there is
none (`shot_insert_<word>__<preset>` on a set that serves several views; the
marker tools' own candidate search, occlusion and empty-frame tests) — and
cues it: `[shot:insert <word>]`. The director's INSERT_HOLD brings the room
back two lines later.

Rules: an authored [shot:] is never touched (nor a line that opens with any
directive but trip/mood/beat); ≥ 3 nodes since the last cue; the same insert
not within 10 nodes; seeded cues ≤ nodes / 5; structure, bodies, people and
time are never subjects; a part too generic (≥ 25 matches) or too big (> 2.4 m)
is not an insert.

    python3 godot/tools/audit/text_focus_pass.py --dry <vol>…        # measure
    python3 godot/tools/audit/text_focus_pass.py <vol>…              # author markers + cue the lines
    python3 godot/tools/audit/text_focus_pass.py --dry --chapter vol7_ch2_x
"""
import glob
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vantage_obstruction_audit as VO
import marker_aim_audit as M
import marker_reframe as R
import shot_seed as SS

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GODOT = os.path.join(ROOT, "godot")
SCENES = os.path.join(GODOT, "resources", "scenes")
TSCN = os.path.join(GODOT, "scenes", "locales")
BG3D = os.path.join(GODOT, "scripts", "vn", "Background3D.gd")
PLACES = os.path.join(GODOT, "resources", "vn", "bg_places.json")

MIN_GAP, REUSE, BUDGET_DIV = 3, 10, 5
GENERIC_MAX, SIZE_MAX = 25, 2.4
WORD_RX = re.compile(r"[A-Za-z][A-Za-z'-]+")
DIRECT_RX = re.compile(r"^\[(\w+):([^\]\r\n]+)\]\s*")
BB_RX = re.compile(r"\[/?[a-z_]+[^\]]*\]")

NEVER = set("""
wall walls floor floors ceiling room rooms house home building place inside outside front back side sides top bottom
middle edge edges corner corners half part parts piece pieces light lights air sky ground world street road way
hand hands face faces eye eyes head heads hair arm arms leg legs foot feet finger fingers mouth lips shoulder shoulders
chest body skin voice breath throat neck knee knees back nose ear ears cheek cheeks tooth teeth
girl girls woman women man men kid kids boy boys people person someone everyone nobody anybody somebody family
mother father mom dad sister brother friend friends
thing things time times morning night nights day days evening afternoon minute minutes hour hours week weeks year
years moment moments second seconds today tonight tomorrow yesterday summer winter spring autumn fall
word words name names line lines look looks sound sounds rest moment idea question answer story stories something
nothing anything everything other others first last next again still just there here then than what that this
they them their theirs with from into onto over under about around after before down through each every some more
most very only also even much many like does have been were will would could should which while where when said says
says tell tells told know knows knew think thinks thought want wants wanted need needs needed make makes made take
takes took come comes came goes going gone open opens opened close closes closed turn turns turned hold holds held
keep keeps kept stand stands stood walk walks walked sits sit sat looks looked feel feels felt seem seems seemed
small large little long short big good same different whole kind sort fine right left
kitchen kitchens bathroom bedroom bedrooms hallway hall stairs stairwell stairway roof loft attic basement office
store shop lobby landing yard clearing alley town city block
rain mist fog snow cloud clouds wind weather water sunlight daylight moonlight dark darkness shadow shadows
cabin bakery bookstore diner apartment studio tower building buildings house houses room
across above below behind beside between beyond inside outside toward towards flat hers his white warm cold work
center centre space miles drop stop rises bend entrance submission titles tokens template layers pulls repairs drivers
path trail creek stream river beach shore ocean sea tide horizon headland bluff mountain mountains overlook garden
asphalt sidewalk curb pavement gravel forest woods trees tree cedars spruce field hill hills ridge
wear shops foundation storage submissions submission cedar
band break song songs verse chorus dance dream dreams ghosts witness text title titles team groups readings deck
figure figures flame purifiers twenty five seven eight nine blue black empty worn spare lower rear west east north
south iced indie novelty interior heat dust well weight yards tips strip grid smear marks sorts dates base backs
skip fill fills leave gets plays works stage lake motes mote
ones highs manager managers squat towers rings registers clerk owner customer customers
banks bank drugstore frozen four pink high broken wakes runs pull main players player parents teacher torso jobs job
business service expense images forms surrounds border coast island cave farm dune surf sand grass moss sidelines
recess overhang copy carbon seams seam
puddle puddles stain stains spill spills mark scuff scuffs crack cracks
brow brows forehead eyebrow eyebrows wrist wrists elbow elbows thumb thumbs palm palms jaw chin lap hip hips belly
""".split())
# furniture every room has: one cue a chapter, not a refrain
COMMON = {"table", "tables", "door", "doors", "counter", "counters", "couch", "chair", "chairs", "bench", "desk", "shelf",
          "window", "steps", "step", "coffee", "cedar", "floor"}
# -ing words that ARE things (the rest are verbs: "folding", "turning")
ING_THINGS = {"railing", "awning", "carving", "carvings", "bedding", "wiring", "siding", "stuffing", "frosting", "piping",
              "railings", "awnings", "clothing", "decking"}
# a material or room word before another word is a modifier, not the subject
# ("wool socks", "kitchen table", "cedar box"): the head noun after it is
MODIFIER = set("""
wool woolen cedar glass paper wood wooden metal plastic brass steel iron tin leather cotton canvas flannel linen
kitchen bathroom bedroom living dining front back side coffee tea water card ceramic stone brick concrete copper
""".split())


# HeroArt.OBJECT_WORDS: a line naming a picture is the director's NOTICING shot
ART_WORDS = re.compile(r"\b(" + "|".join(re.findall(r'"(\w+)"', re.search(
    r"const OBJECT_WORDS[^=]*= \[(.*?)\]", open(os.path.join(GODOT, "scripts", "vn", "HeroArt.gd")).read(), re.S).group(1)))
    + r")s?\b", re.I)


def presets():
    src = open(BG3D).read()
    out = {}
    for m in re.finditer(r'^\t"(\w+)": \{\n\t\t"scene": "res://scenes/locales/(\w+)\.tscn"(.*?)\n\t\},', src, re.M | re.S):
        pid, scene, body = m.group(1), m.group(2), m.group(3)
        cm = VO.PV.ORIGIN.search("\t\t" + body) if hasattr(VO, "PV") else None
        out[pid] = (scene, body)
    return out


def preset_camera(body):
    om = re.search(r'"camera_origin":\s*Vector3\(([^)]*)\)', body)
    rm = re.search(r'"camera_rotation":\s*Vector3\(((?:[^()]|\([^()]*\))+)\)', body)
    if not om:
        return None, None
    pos = tuple(float(eval(v, {"deg_to_rad": math.radians})) for v in om.group(1).split(","))
    rot = (0.0, 0.0, 0.0)
    if rm:
        rot = tuple(float(eval(v, {"deg_to_rad": math.radians})) for v in re.split(r",(?![^(]*\))", rm.group(1)))
    return pos, rot


_BOX = {}


def boxes(scene):
    if scene in _BOX:
        return _BOX[scene]
    path = os.path.join(TSCN, scene + ".tscn")
    src = open(path).read() if os.path.exists(path) else ""
    gm = re.search(r'path="res://assets/3d/locales/(\w+)\.glb"', src)
    _BOX[scene] = VO.boxes_for(gm.group(1) if gm else scene) or []
    return _BOX[scene]


def chapter_presets(nodes, sid, places, pre):
    """node index -> the preset loaded there (None: a 2D or unresolved bg)."""
    cur, out = None, {}
    for i, n in enumerate(nodes):
        if n.get("t") == "bg":
            s = str(n.get("src") or "")
            if s.startswith("3d:"):
                cur = s[3:]
            else:
                stem = os.path.splitext(os.path.basename(s))[0]
                e = places.get(stem) or {}
                to = (e.get("by_scene") or {}).get(sid) or e.get("to") or ""
                cur = to[3:] if str(to).startswith("3d:") else None
            if cur not in pre:
                cur = None
        out[i] = cur
    return out


LOWER = set()     # every word the scenes ever write in lower case


def cast_words():
    words = set()
    for f in glob.glob(os.path.join(SCENES, "*", "*.json")):
        try:
            j = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        for n in j.get("nodes", []):
            for w in WORD_RX.findall(str(n.get("text") or "")):
                if w[0].islower():
                    LOWER.add(w.lower())
            c = str(n.get("char") or "")
            for w in WORD_RX.findall(c):
                words.add(w.lower())
    return words


CARVING = re.compile(r"\b(carv\w*|rim|spiral|figures?|totems?)\b", re.I)
# a thing is named with an article or an owner before it ("the kettle", "his
# notebook", "Lena's grinder"): "Sam rings him up" names no rings
DETERMINER = set("the a an his her their my your our its this that these those some two three four each every".split())
PRONOUN = set("he she it they i we you".split())
FUNCTION = set("in on at of and or to with from was were had has is are the a an by for as but that this its it".split())


# a word that names a different thing inside a compound part name:
# "the truck comes at five fifty-eight" is the delivery truck, not the
# HandTruck on the dock floor (2026-10-28)
COMPOUND_NOT = {"truck": {"hand"}, "dock": {"coil", "track", "edgeguard", "face", "bumper", "plate", "leveler"}}


def word_hits(word, geo):
    hits = M.matches_for(word, geo)
    bad = COMPOUND_NOT.get(word)
    if bad:
        hits = [h for h in hits if not (set(CAMEL.sub("_", h[0]).lower().split("_")) & bad)]
    return hits


def subject_for(text, geo, cast, marked=()):
    """(word, hits) for the thing the line names that the set has in view, or
    None. Every candidate is gathered; one the set already has an insert
    marker for wins (the story's established objects: the bowls, the
    kettle), else the first named."""
    toks = [(m.group(0), m.start()) for m in WORD_RX.finditer(text)]
    found = []
    for ti, (w, at) in enumerate(toks):
        # a possessive points past itself ("Marit's bowl", "Lena's room")
        if w.lower().endswith("'s") or w.endswith("'"):
            continue
        wl = w.lower().strip("'-")
        if len(wl) < 4 or wl in NEVER or wl in cast:
            continue
        # a capital is a name unless it opens the sentence as a common word
        if w[0].isupper():
            opens = at == 0 or text[:at].rstrip()[-1:] in ".!?\"\u201c\u2014:"
            if not opens or wl not in LOWER:
                continue
        if len(wl) >= 6 and wl.endswith("ed"):
            continue
        if len(wl) >= 6 and wl.endswith("ing") and wl not in ING_THINGS:
            continue
        # a material or room word straight before a noun modifies it ("the
        # cedar roof", "wool socks"); before a function word it is the noun
        # ("the cedar in Finn's hand")
        prev = [t[0].lower() for t in toks[max(0, ti - 3):ti]]
        if not any(p in DETERMINER or p.endswith("'s") for p in prev):
            continue
        if prev and (prev[-1] in PRONOUN or (toks[ti - 1][0][0].isupper() and not prev[-1] in DETERMINER)):
            continue
        nxt = toks[ti + 1][0].lower() if ti + 1 < len(toks) else ""
        if wl in MODIFIER and nxt and nxt not in FUNCTION and len(nxt) >= 3 and \
                text.find(w + " " + toks[ti + 1][0]) >= 0:
            continue
        for cand in (wl, wl[:-1] if wl.endswith("s") and not wl.endswith("ss") else None):
            if not cand or len(cand) < 4 or cand in NEVER:
                continue
            hits = word_hits(cand, geo)
            if not hits or len(hits) >= GENERIC_MAX:
                continue
            found.append((cand, hits))
            break
    if not found:
        return None
    # vol 7's carvings: "the young woman in the hooded coat", "a crow at the
    # rim" describe the figures ON a bowl or a piece, not a coat in the room
    if CARVING.search(text):
        bowls = [f for f in found if f[0].startswith("bowl")]
        if bowls:
            return bowls[0]
        found = [f for f in found if f[0] not in ("coat", "hood")]
        if not found:
            return None
    for cand, hits in found:
        if cand in marked:
            return cand, hits
    return found[0]


_PLACED = {}
COVER_MIN = 0.03       # of the visible frame the subject must own (report / keep)
COVER_NEW = 0.06       # a NEW lens asks more: the thermos behind the register owned 5 % and read as nothing
INSERT_CENTER = 0.36   # VnDirector.INSERT_CENTER: the director's lift
TEXT_BAND = 0.31       # the reading box's share of the screen, from the bottom


def coverage(pos_b, rx, ry, fov, boxes, subj, rows=11, cols=17):
    """The share of the picture ABOVE the reading box whose first hit is the
    subject, with the director's insert lift applied (2026-10-28: frames
    that passed the empty and occlusion tests showed a wall where a thermos,
    a dock and the puddles were meant to be)."""
    vf = math.radians(fov)
    hf = 2.0 * math.atan(math.tan(vf / 2.0) * VO.ASPECT)
    lift = math.atan(math.tan(vf / 2.0) * (1.0 - 2.0 * INSERT_CENTER))
    pitch = rx - lift
    own = n = 0
    for r in range(rows):
        fy = r / (rows - 1.0)                     # 0 top .. 1 bottom
        if fy > 1.0 - TEXT_BAND:
            continue
        dv = math.atan((1.0 - 2.0 * fy) * math.tan(vf / 2.0))
        for c in range(cols):
            fx = c / (cols - 1.0)
            dh = math.atan((2.0 * fx - 1.0) * math.tan(hf / 2.0))
            t, who = VO.cast(pos_b, VO.ray_dir(pitch, ry, dh, dv), boxes, ignore=re.compile(r"^$"))
            n += 1
            if who in subj:
                own += 1
    return own / float(max(1, n))
# what divides one room from another (and a room from outside): a lens on
# the far side of one of these is in another room, or looking in through a
# window from the porch (2026-10-27: the first blanket insert did exactly that)
STRUCT = re.compile(r"(^|_)(wall|walls|glass|pane|warm|window|windows|win|door|doors|partition|part|shutter|siding|"
                    r"gable|roof|glint|frameside|framet|frameb|mull|mullh|mullv|exterior|ext)(_|$|\d)", re.I)
CAMEL = re.compile(r"(?<=[a-z])(?=[A-Z])")


def same_room(a_b, b_b, boxes):
    """True when nothing structural stands between two points (blender frame)."""
    d = [b_b[i] - a_b[i] for i in range(3)]
    for name, c, h in boxes:
        if not STRUCT.search(CAMEL.sub("_", name)):
            continue
        t0, t1 = 0.0, 1.0
        ok = True
        for i in range(3):
            lo_, hi_ = c[i] - h[i], c[i] + h[i]
            if abs(d[i]) < 1e-9:
                if not (lo_ <= a_b[i] <= hi_):
                    ok = False
                    break
                continue
            u, v = (lo_ - a_b[i]) / d[i], (hi_ - a_b[i]) / d[i]
            if u > v:
                u, v = v, u
            t0, t1 = max(t0, u), min(t1, v)
            if t0 > t1:
                ok = False
                break
        if ok and 0.0 < t0 < 1.0:
            return False
    return True


def place_marker(scene, preset, word, hits, cam, boxes_all, dry):
    """Author shot_insert_<word>[__<preset>] framing the hits from cam's side
    (once per set, view and word: a dry run counts it as placed after that)."""
    key = (scene, preset, word)
    if key in _PLACED:
        return _PLACED[key]
    _PLACED[key] = _place(scene, preset, word, hits, cam, boxes_all, dry)
    return _PLACED[key]


def _place(scene, preset, word, hits, cam, boxes_all, dry):
    """The first clear lens on the subject, searched outward from the side the
    view's own camera stands on (the room the player knows), at the subject's
    natural distance first. Early exit: the full ring search of
    marker_reframe costs ~20 s a subject and the first pass that ran it on
    vol 7 would have taken hours."""
    path = os.path.join(TSCN, scene + ".tscn")
    lo, hi = R.locale_bounds(boxes_all)
    subj = {h[0] for h in hits}
    _an, tgt = M.subject_target(hits, cam)
    size = R.subject_size(hits)
    if size > SIZE_MAX:
        return None, "too big (%.1f m)" % size
    pose = _search(hits, cam, boxes_all)
    if pose is None:
        return None, "no clear position"
    npos, rx, ry = pose
    name = "shot_insert_%s__%s" % (word, preset)
    if not dry:
        blk = ["", "; authored by text_focus_pass.py (2026-10-27): the line names it, the camera goes to it",
               '[node name="%s" type="Marker3D" parent="." groups=["vn_shot"]]' % name,
               "position = Vector3(%.3f, %.3f, %.3f)" % npos,
               "rotation = Vector3(%.4f, %.4f, 0.0)" % (rx, ry),
               "metadata/fov = 35.0", ""]
        with open(path, "a") as f:
            f.write("\n".join(blk))
    return name, "ok"


def _search(hits, cam, boxes_all):
    """(pos, rx, ry) of the first clear, same-room, covered lens, or None."""
    lo, hi = R.locale_bounds(boxes_all)
    subj = {h[0] for h in hits}
    _an, tgt = M.subject_target(hits, cam)
    size = R.subject_size(hits)
    pref = R.preferred_dist(size)
    base = math.atan2(cam[2] - tgt[2], cam[0] - tgt[0])
    max_eye = max(R.MAX_EYE, tgt[1] - 1.0)
    for d in (pref, pref * 1.35, pref * 0.8, pref * 1.8):
        for dyaw in (0, 20, -20, 40, -40, 60, -60, 90, -90, 120, -120):
            a = base + math.radians(dyaw)
            for el in (15.0, 30.0, 5.0):
                e = math.radians(el)
                npos = (tgt[0] + math.cos(a) * d * math.cos(e), tgt[1] + d * math.sin(e),
                        tgt[2] + math.sin(a) * d * math.cos(e))
                if not (R.MIN_EYE <= npos[1] <= max_eye):
                    continue
                pb = R.to_b(npos)
                if not (lo[0] - 0.2 <= pb[0] <= hi[0] + 0.2 and lo[1] - 0.2 <= pb[1] <= hi[1] + 0.2):
                    continue
                if VO.inside_any(pb, boxes_all):
                    continue
                if not same_room(R.to_b(cam), pb, boxes_all):
                    continue
                _a2, tgt2 = M.subject_target(hits, npos)
                if VO._occlusion(pb, R.to_b(tgt2), boxes_all, subj):
                    continue
                rx, ry = R.aim(npos, tgt2)
                st = VO.frame_stats(pb, rx, ry, 35.0, boxes_all)
                if st["escape"] >= VO.EMPTY_FRAC:
                    continue
                if coverage(pb, rx, ry, 35.0, boxes_all, subj) < COVER_NEW:
                    continue
                return npos, rx, ry
    return None


_MW = {}


def marked_words(scene, preset):
    """The insert subjects a set already frames for this view (re-read after
    each new marker: _MW is cleared when one is written)."""
    key = (scene, preset)
    if key not in _MW:
        src = open(os.path.join(TSCN, scene + ".tscn")).read()
        ws = set()
        for m in re.finditer(r'name="shot_insert_([a-z0-9_]+?)(?:__(\w+))?"', src):
            if m.group(2) in (None, preset) or m.group(2) not in VO.PRESET_IDS:
                ws.add(m.group(1))
        _MW[key] = ws
    return _MW[key]


def has_marker(scene, preset, word):
    src = open(os.path.join(TSCN, scene + ".tscn")).read()
    return ('name="shot_insert_%s__%s"' % (word, preset) in src) or ('name="shot_insert_%s"' % word in src)


def run_chapter(path, pre, places, cast, dry, stats):
    j = json.load(open(path, encoding="utf-8"))
    nodes = j.get("nodes", [])
    sid = j.get("id", os.path.basename(path)[:-5])
    at = chapter_presets(nodes, sid, places, pre)
    edits, last_cue, recent = [], -99, {}
    budget = max(1, len(nodes) // BUDGET_DIV)
    for i, n in enumerate(nodes):
        t = n.get("t")
        text = str(n.get("text") or "")
        if "[shot:" in text[:200]:
            last_cue = i
            continue
        if t not in ("narrate", "think") or not text:
            continue
        lead = DIRECT_RX.match(text)
        if lead and lead.group(1) not in ("trip", "mood", "beat"):
            continue
        preset = at.get(i)
        if preset is None:
            continue
        scene, body = pre[preset]
        cam, _rot = preset_camera(body)
        allb = boxes(scene)
        if not allb or cam is None:
            continue
        view = [b for b in allb if VO._in_view(b[0], preset)] if preset in VO.PRESET_IDS else allb
        geo = [(b[0], (b[1][0], b[1][2], -b[1][1])) for b in view]
        clean = BB_RX.sub("", text)
        if ART_WORDS.search(clean):
            continue
        # a tarot card read aloud ("THE STAR. The naked figure kneels at the
        # pool") describes the card, not the room
        if re.match(r"\s*(THE |[IVXL]+\. )?[A-Z]{3,}[A-Z ,']*[.:]", clean):
            continue
        found = subject_for(clean, geo, cast, marked_words(scene, preset))
        if not found:
            continue
        word, hits = found
        # the one the camera can mean: the nearest instance and its own parts
        # (two tables in a room are not one 3.7 m subject)
        _an, near = M.subject_target(hits, cam)
        hits = [h for h in hits if math.dist(h[1], near) <= 1.2] or hits
        stats["named"] += 1
        if i - last_cue < MIN_GAP or i - recent.get(word, -99) < REUSE or len(edits) >= budget or \
                (word in COMMON and word in recent):
            stats["spaced"] += 1
            continue
        if not has_marker(scene, preset, word):
            name, why = place_marker(scene, preset, word, hits, cam, view, dry)
            if name is None:
                stats["unplaceable"] += 1
                stats["why"].append("%s #%d %s: %s" % (sid, i, word, why))
                continue
            stats["markers"] += 1
            _MW.pop((scene, preset), None)
            if dry:
                _MW.setdefault((scene, preset), set(marked_words(scene, preset))).add(word)
        edits.append((i, "[shot:insert %s]" % word))
        last_cue, recent[word] = i, i
        stats["cued"] += 1
        stats["sample"].append("%s #%d → insert %s · %s" % (sid, i, word, clean[:80]))
    if edits and not dry:
        SS.splice(path, nodes, edits)
    return len(edits)


def coverage_report(only, drop):
    """Every insert marker's subject coverage (see coverage()); `--drop`
    deletes the ones this pass authored below COVER_MIN, and their cues."""
    low = []
    for fn in sorted(os.listdir(TSCN)):
        loc = fn[:-5]
        if not fn.endswith(".tscn") or (only and loc not in only):
            continue
        path = os.path.join(TSCN, fn)
        markers = [mk for mk in M.parse_markers(path) if mk[0].startswith("shot_insert_")]
        if not markers:
            continue
        gm = re.search(r'path="res://assets/3d/locales/(\w+)\.glb"', open(path).read())
        bx = VO.boxes_for(gm.group(1) if gm else loc) or []
        if not bx:
            continue
        src = open(path).read()
        for name, pos, rot in markers:
            if "--mine" in sys.argv and '; authored by text_focus_pass.py' not in src.split('name="%s"' % name)[0][-200:]:
                continue
            cue = name[len("shot_insert_"):]
            word, _, view = cue.partition("__")
            vb = [b for b in bx if VO._in_view(b[0], view)] if view in VO.PRESET_IDS else bx
            geo = [(b[0], (b[1][0], b[1][2], -b[1][1])) for b in vb]
            hits = M.matches_for(word, geo)
            if not hits:
                continue
            good = word_hits(word, geo)
            hits = [h for h in good if math.dist(h[1], pos) <= 30.0] or good
            if not hits:
                # it frames the wrong thing (the HandTruck for "the truck")
                mine = ('; authored by text_focus_pass.py' in src.split('name="%s"' % name)[0][-200:])
                low.append((loc, name, 0.0, mine, pos))
                continue
            subj = {h[0] for h in hits}
            mf = re.search(r'\[node name="%s"[^\n]*\n(?:[^\n\[]*\n)*?metadata/fov = ([\d.]+)' % re.escape(name), src)
            fov = float(mf.group(1)) if mf else 35.0
            cv = coverage(R.to_b(pos), rot[0], rot[1], fov, vb, subj)
            if cv < COVER_MIN:
                mine = ('; authored by text_focus_pass.py' in src.split('name="%s"' % name)[0][-200:])
                low.append((loc, name, cv, mine, pos))
    for loc, name, cv, mine, _p in low:
        print("  LOW %-28s %-46s %4.1f%%%s" % (loc, name, cv * 100, "  (text_focus)" if mine else ""))
    print("coverage · %d insert marker(s) below %.0f%% of the picture" % (len(low), COVER_MIN * 100))
    return low


def refit(low, pre, places):
    """Re-place each low-coverage insert with the coverage-checked search
    (same name, new pose). One that cannot be placed: this pass's own is
    deleted with its cues; an older hand marker is reported and kept."""
    by_scene = {}
    for pid, (scene, body) in pre.items():
        by_scene.setdefault(scene, []).append(pid)
    moved = dropped = kept = 0
    drop_cues = []                # (preset, word)
    for loc, name, cv, mine, mpos in low:
        if not mine:
            # a hand marker may frame a hero prop the builder's boxes do
            # not hold (the carved bowls score 0 % and read well): report it
            kept += 1
            continue
        path = os.path.join(TSCN, loc + ".tscn")
        cue = name[len("shot_insert_"):]
        word, _, view = cue.partition("__")
        # an unsuffixed marker belongs to the view whose camera is nearest it
        views = [view] if view in pre else sorted(
            by_scene.get(loc, []), key=lambda v: math.dist(preset_camera(pre[v][1])[0] or (0, 0, 0), mpos))
        if not views:
            kept += 1
            continue
        scene, body = pre[views[0]]
        cam, _r = preset_camera(body)
        allb = boxes(scene)
        if cam is None or not allb:
            kept += 1
            continue
        vb = [b for b in allb if VO._in_view(b[0], views[0])] if views[0] in VO.PRESET_IDS else allb
        geo = [(b[0], (b[1][0], b[1][2], -b[1][1])) for b in vb]
        hits = word_hits(word, geo)
        if hits:
            _an, near = M.subject_target(hits, cam)
            hits = [h for h in hits if math.dist(h[1], near) <= 1.2] or hits
        pose = _search(hits, cam, vb) if hits else None
        src = open(path).read()
        blk = re.search(r'\[node name="%s"[^\n]*\n((?:[^\n\[]*\n)*)' % re.escape(name), src)
        if pose and blk:
            npos, rx, ry = pose
            body_new = re.sub(r"(?m)^(transform|position|rotation) = .*\n", "", blk.group(1))
            body_new = "position = Vector3(%.3f, %.3f, %.3f)\nrotation = Vector3(%.4f, %.4f, 0.0)\n" % (npos + (rx, ry)) + body_new
            src = src[:blk.start(1)] + body_new + src[blk.end(1):]
            open(path, "w").write(src)
            moved += 1
            print("  moved   %-26s %s" % (loc, name))
        elif mine and blk:
            head = src.rfind("\n; authored by text_focus_pass.py", 0, blk.start())
            a = head if head != -1 and blk.start() - head < 200 else blk.start()
            src = src[:a] + "\n" + src[blk.end():]
            open(path, "w").write(src)
            drop_cues += [(v, word) for v in views]
            dropped += 1
            print("  dropped %-26s %s" % (loc, name))
        else:
            kept += 1
            print("  KEPT    %-26s %s (no clear frame found)" % (loc, name))
    if drop_cues:
        cue_rx = {}
        for v, w in drop_cues:
            cue_rx.setdefault(v, set()).add(w)
        for f in glob.glob(os.path.join(SCENES, "*", "*.json")):
            raw = open(f, encoding="utf-8").read()
            if "[shot:insert " not in raw:
                continue
            j = json.loads(raw)
            nodes = j.get("nodes", [])
            at = chapter_presets(nodes, j.get("id", ""), places, pre)
            changed = False
            for i, n in enumerate(nodes):
                t = str(n.get("text") or "")
                m = re.match(r"\[shot:insert (\w+)\]", t)
                if m and at.get(i) in cue_rx and m.group(1) in cue_rx[at.get(i)]:
                    old = json.dumps(t, ensure_ascii=False)[1:-1]
                    new = json.dumps(t[m.end():], ensure_ascii=False)[1:-1]
                    if old in raw:
                        raw = raw.replace(old, new, 1)
                        changed = True
            if changed:
                open(f, "w", encoding="utf-8").write(raw)
    print("refit · %d moved · %d dropped (with their cues) · %d hand marker(s) kept" % (moved, dropped, kept))


def main():
    if "--coverage" in sys.argv:
        VO.P.A.install_stubs()
        VO.PRESET_IDS.update(p[0] for p in VO.presets())
        low = coverage_report([a for a in sys.argv[1:] if not a.startswith("--")], "--drop" in sys.argv)
        if "--refit" in sys.argv:
            places = json.load(open(PLACES))["places"] if os.path.exists(PLACES) else {}
            refit(low, presets(), places)
        return
    dry = "--dry" in sys.argv
    VO.P.A.install_stubs()
    VO.PRESET_IDS.update(p[0] for p in VO.presets())
    pre = presets()
    places = json.load(open(PLACES))["places"] if os.path.exists(PLACES) else {}
    cast = cast_words()
    files = []
    if "--chapter" in sys.argv:
        cid = sys.argv[sys.argv.index("--chapter") + 1]
        files = glob.glob(os.path.join(SCENES, "*", cid + ".json"))
    else:
        for v in [a for a in sys.argv[1:] if not a.startswith("--")]:
            files += sorted(glob.glob(os.path.join(SCENES, "vol%s" % v, "*.json")))
    stats = {"named": 0, "spaced": 0, "cued": 0, "markers": 0, "unplaceable": 0, "why": [], "sample": []}
    for f in files:
        if os.path.basename(f) == "index.json":
            continue
        n = run_chapter(f, pre, places, cast, dry, stats)
        print("  %-40s %d cue(s)" % (os.path.basename(f)[:-5], n), flush=True)
    print("text_focus_pass%s · %d chapter(s) · %d line(s) name a thing in view · %d cued (%d new marker(s)) · %d held by spacing · %d unplaceable"
          % (" (dry)" if dry else "", len(files), stats["named"], stats["cued"], stats["markers"], stats["spaced"], stats["unplaceable"]))
    for s in stats["sample"][:None if "--all" in sys.argv else 40]:
        print("  ", s)
    for w in stats["why"][:None if "--all" in sys.argv else 20]:
        print("   ✗", w)


if __name__ == "__main__":
    main()
