#!/usr/bin/env python3
"""trip_direction.py — direct THE TRIP for every scene, from its writing (2026-11-08).

The user: "direct the psychedelic effect for each scene." Before this,
every scene opened at the same trip level and 105 of the corpus's 106
`[trip:]` cues were one mechanical `[trip:1.2]`.

resources/vn/trip_direction.json (GameEngine._trip_scene_start reads it):

    {"scenes": {"<scene_id>": {
        "level": 1.2,                 # the scene_scale it opens at (0..1.5)
        "register": "domestic",       # optional: a TripSync register for the scene
        "beats": [{"node": 41, "trip": 1.45, "hold": 3, "why": "…"}],
        "why": "…",                   # the reading behind the level
        "locked": true                # hand-directed: never regenerated
    }}}

The level comes from the scene's own words: how much of it is vision,
dream, music, the uncanny (the trip swells) against how much is grief,
hospitals, courts, money, the working day (the trip steps back so the
weight lands plain). Levels are spread over the whole corpus by rank, so
"dreamlike" means dreamlike relative to the rest of the book. A morning
kitchen with no uncanny in it takes the `domestic` register. Beats: a
line that turns visionary in a grounded scene swells for three lines; a
death or a hospital in a dreamlike scene drops it.

    python3 tools/trip_direction.py            # (re)build, keeping locked entries
    python3 tools/trip_direction.py --show ID  # one scene's direction and why
"""
import collections
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GODOT = os.path.normpath(os.path.join(HERE, ".."))
SCENES = os.path.join(GODOT, "resources", "scenes")
OUT = os.path.join(GODOT, "resources", "vn", "trip_direction.json")

HIGH = [
    "dream", "vision", "hallucinat", "tripping", "acid", "lsd", "mushroom", "shroom", "peyote",
    "trance", "psychedel", "kaleidoscop", "glow", "shimmer", "neon", "nebula", "galax", "cosmos",
    "cosmic", "void", "float", "melt", "swirl", "spiral", "pulse", "riff", "guitar", "synth",
    "chord", "danc", "concert", "=rave", "magic", "ghost", "spirit", "demon",
    "angel", "portal", "substrate", "rainbow", "sparkl", "haze", "=stars", "moonlight",
    "music", "song", "=sing", "=singing", "=sang", "flame",
]
LOW = [
    "hospital", "funeral", "=grave", "grief", "griev", "=died", "cancer", "sick", "doctor",
    "nurse", "court", "lawyer", "judge", "police", "officer", "arrest", "interrog", "contract",
    "paperwork", "invoice", "=rent", "money", "=bank", "debt", "homework", "boss", "meeting",
    "spreadsheet", "email", "=shift", "clocked", "taxes", "insurance", "=bill", "=bills",
]
DOMESTIC = ["kitchen", "breakfast", "dishes", "coffee", "morning", "toast", "eggs", "=sink"]
MORNING = ["morning", "breakfast"]
VISION_LINE = ["dream", "vision", "hallucinat", "trance", "melt", "glow", "kaleidoscop", "swirl",
               "spiral", "float", "void", "portal", "substrate", "shimmer"]
GROUND_LINE = [r"\bdied\b", r"\bis dead\b", r"\bwas dead\b", r"\bfuneral", r"\bhospital", r"\bcancer\b",
               r"\bgunshot", r"\bkilled\b"]

TOK = re.compile(r"[a-z']+")
CUE = re.compile(r"\[[^\]]*\]")
# (score per 1000 words, minimum hits) → level. Absolute, not by rank: a
# scene with little signal either way keeps the volume's own level (a single
# "judge" in a short scene is not plainness; "death" is often the Tarot card
# or a myth in this book, so only died / funeral / hospital count)
def _level_for(score, hi_n, lo_n):
    if score >= 10.0 and hi_n >= 6:
        return 1.40, "dreamlike"
    if score >= 4.0 and hi_n >= 3:
        return 1.20, "leans uncanny"
    if score <= -6.0 and lo_n >= 4:
        return 0.50, "plain: the weight lands without the trip"
    if score <= -2.0 and lo_n >= 2:
        return 0.75, "grounded"
    return 1.00, "the volume's own"


def _count(words, stems):
    c = collections.Counter()
    for w in words:
        for st in stems:
            if (w == st[1:]) if st.startswith("=") else w.startswith(st):
                c[st.lstrip("=")] += 1
                break
    return c


def _phrase_hits(text, phrases):
    return [re.sub(r"\\b", "", p) for p in phrases if re.search(p, text)]


def read_scenes():
    out = []
    for dirpath, _dirs, files in os.walk(SCENES):
        for fn in sorted(files):
            if not fn.endswith(".json"):
                continue
            try:
                j = json.load(open(os.path.join(dirpath, fn), encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(j, dict) or not isinstance(j.get("nodes"), list):
                continue
            sid = j.get("id") or fn[:-5]
            lines = []
            for i, n in enumerate(j["nodes"]):
                t = n.get("text") if isinstance(n, dict) else None
                if isinstance(t, str) and t.strip():
                    lines.append((i, CUE.sub("", t).lower()))
            if lines:
                out.append((sid, lines))
    return out


def direct(scenes):
    rows = []
    for sid, lines in scenes:
        words = [w for _i, t in lines for w in TOK.findall(t)]
        n = max(len(words), 1)
        hi = _count(words, HIGH)
        lo = _count(words, LOW)
        do = _count(words, DOMESTIC)
        k = 1000.0 / n
        score = sum(hi.values()) * k - 1.4 * sum(lo.values()) * k
        rows.append((score, sid, lines, hi, lo, do, n, words))
    plan = {}
    for score, sid, lines, hi, lo, do, n, words in rows:
        level, label = _level_for(score, sum(hi.values()), sum(lo.values()))
        top_hi = ", ".join("%s ×%d" % kv for kv in hi.most_common(4))
        top_lo = ", ".join("%s ×%d" % kv for kv in lo.most_common(4))
        why = "%s — %s" % (label, top_hi or "no uncanny words") if level >= 1.0 else \
              "%s — %s" % (label, top_lo or "an everyday room, little of the uncanny")
        entry = {"level": level, "why": why}
        # a morning kitchen with none of the uncanny: the domestic register
        # (a kitchen at night is not this: the register is a morning's warmth)
        mo = _count(words, MORNING)
        # … and a real kitchen or breakfast table: a morning in a truck cab
        # or at the pit stop keeps its volume's register (vol 6's zines)
        kit = sum(v for k, v in do.items() if k in ("kitchen", "breakfast", "dishes", "toast", "eggs"))
        if kit >= 5 and sum(do.values()) * 1000.0 / n >= 6.0 and sum(mo.values()) >= 2 and level <= 1.0 \
                and sum(hi.values()) * 1000.0 / n < 6.0:
            entry["register"] = "domestic"
            entry["why"] += "; a kitchen-and-morning room (%s): domestic register" % \
                ", ".join("%s ×%d" % kv for kv in do.most_common(3))
        beats = []
        last = -99
        for i, t in lines:
            if len(beats) >= 6 or i - last < 12:
                continue
            vis = _count(TOK.findall(t), VISION_LINE)
            if level <= 1.2 and sum(vis.values()) >= 2:
                beats.append({"node": i, "trip": round(min(1.5, level + 0.35), 2), "hold": 3,
                              "why": "the line turns visionary (%s)" % ", ".join(vis)})
                last = i
                continue
            g = _phrase_hits(t, GROUND_LINE)
            if level >= 1.0 and g:
                beats.append({"node": i, "trip": 0.45, "hold": 3,
                              "why": "a weight the trip steps back from (%s)" % ", ".join(g)})
                last = i
        if beats:
            entry["beats"] = beats
        plan[sid] = entry
    return plan


def main():
    if "--show" in sys.argv:
        sid = sys.argv[sys.argv.index("--show") + 1]
        data = json.load(open(OUT, encoding="utf-8"))
        print(json.dumps(data["scenes"].get(sid, {}), indent=2, ensure_ascii=False))
        return 0
    old = {}
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT, encoding="utf-8")).get("scenes", {})
        except Exception:
            old = {}
    plan = direct(read_scenes())
    kept = 0
    for sid, e in old.items():
        if isinstance(e, dict) and e.get("locked"):
            plan[sid] = e
            kept += 1
    doc = {
        "_doc": "THE TRIP, directed per scene (2026-11-08). Built by tools/trip_direction.py from each "
                "scene's writing; GameEngine._trip_scene_start reads it. level = the scene_scale the "
                "scene opens at (0..1.5); register = an optional TripSync register; beats = a node where "
                "the trip swells or drops for `hold` lines. Hand-directed entries carry \"locked\": true "
                "and survive a rebuild. An inline [trip:] / [register:] cue on a line still wins there.",
        "scenes": dict(sorted(plan.items())),
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")
    lv = collections.Counter(e["level"] for e in plan.values())
    nb = sum(len(e.get("beats", [])) for e in plan.values())
    nd = sum(1 for e in plan.values() if e.get("register") == "domestic")
    print("trip_direction · %d scene(s) · levels %s · %d beat(s) · %d domestic · %d locked kept"
          % (len(plan), dict(sorted(lv.items())), nb, nd, kept))
    return 0


if __name__ == "__main__":
    sys.exit(main())
