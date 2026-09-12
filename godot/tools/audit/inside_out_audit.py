#!/usr/bin/env python3
"""inside_out_audit.py — the prose says where the camera is (2026-09-11).

A Deck read of the Magician's opening: two paragraphs of the warehouse
seen from the road — "The warehouse did not stand. The warehouse
slumped — a great rusting beast at the industrial edge of Graustark ...
Outside, kudzu vines thick as wrists throttled the chain-link fence" —
played over the INTERIOR, and then the prose turned inside on its own
one line later ("Inside, the air was thick and still"). The fix was a
cut to a new exterior vantage and a `bg` back on the word "Inside".

This finds the rest of that class, the way mood_clock_audit finds a
night mood under a noon clock: every narrate line is read for a
STRONG place assertion — a paragraph that opens by putting the reader
outside a building or inside a room — and compared with the active
background's kind. Only strong openers count; "outside, the rain kept
on" narrated from a kitchen table is a view through a window, not a
camera claim, so bare "Outside," is evidence only when the chapter
has not yet gone inside.

Every preset is classified by NAME first (`*_interior`, `kitchen`,
`road`, `porch` …) and by GEOMETRY as the tie-break (a roof-sized box
over the camera = interior). Presets that satisfy neither are unknown
and never flagged.

    python3 godot/tools/audit/inside_out_audit.py
    python3 godot/tools/audit/inside_out_audit.py --all

Gate at zero once the current list is worked; DELIBERATE holds the
ones read and kept.
"""
import glob
import io
import json
import os
import re
import sys
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GODOT = os.path.join(ROOT, "godot")
SCENES = os.path.join(GODOT, "resources", "scenes")

import preset_vantage_audit as PV

INT_NAME = re.compile(
    r"(_interior|_int$|_cab|garage|kitchen|bedroom|_room|room$|office|apartment|"
    r"_bar$|^bar_|shop|store|studio|cell|ward|stockroom|break_room|aisle|"
    r"dressing|stage|lobby|portal|quarters|bakery|bindery|darkroom|chamber|"
    r"booth|kitchenette|hospice|hospital|basement|corridor|pharmacy|casino|"
    r"roadhouse|comics|taqueria|newspaper|shed|tower_floors|cathedral_interior|"
    r"motel_room|diner$|diner_)", re.I)
EXT_NAME = re.compile(
    r"(_exterior|_ext$|road|street|field|beach|park|_lot|porch|yard|dock|"
    r"overlook|trail|falls|mountain|circle|highway|bypass|route|cemetery|"
    r"garden|alley|drive_in|lighthouse|square|terrain|ruins|wreck|chalk_wall|"
    r"cottage$|godseye|skatepark|carnival|circus|strip_mall|fueling|"
    r"missing_link_exterior|tideline|lake|survey|riverfront|estuary)", re.I)
ROOF = re.compile(r"(roof|ceiling|ceil|rafter|joist|canopy|awning|overhead|beam)", re.I)

DIRECT = re.compile(r"^(\[[a-z]+:[^\]]*\]\s*)+")

# STRONG openers. A paragraph that starts this way is placing the
# reader, not describing a view.
EXT_ASSERT = re.compile(
    r"^(?:"
    r"From the (?:road|street|sidewalk|driveway|parking lot|lot|highway|shoulder|curb|yard|lawn|gate)\b"
    r"|Out (?:on|in) the (?:street|lot|parking lot|road|yard|driveway|field|porch|dark|open|cold|rain|heat)\b"
    r"|On the (?:sidewalk|street|road|highway|shoulder|curb|lawn|porch steps|dock|beach|sand|gravel)\b"
    r"|Across the (?:street|road|lot|parking lot|field)\b"
    r"|The (?:warehouse|house|building|cabin|diner|store|church|bungalow|motel|barn|shed|garage|tower|"
    r"apartment building|strip mall|station|school|courthouse|hospital|chapel|bar|shop|casino|roadhouse|lighthouse)"
    r" (?:did not stand|stood|slumped|sat|rose|loomed|squatted|hunched|leaned|waited|crouched|sprawled)\b"
    r")", re.I)
# "Outside," alone: evidence only while the chapter is still outside.
EXT_SOFT = re.compile(r"^Outside\b")
INT_ASSERT = re.compile(
    r"^(?:Inside,|Inside the (?:house|cabin|room|apartment|kitchen|office|store|shop|bar|"
    r"church|building|warehouse|car|truck|cab|booth|bungalow|cottage|garage|shed|tent)\b|Indoors\b"
    r"|In the (?:kitchen|bedroom|hall|hallway|living room|front room|back room|office|booth|"
    r"bathroom|garage|basement|attic|cabin|studio|bar|stockroom|break room|ward|cell|lobby|"
    r"corridor|dark of the|quiet of the)\b"
    r"|Back inside\b|Once inside\b)", re.I)

# A line like "He stood at the window and looked out" within the four
# narrate pages before an exterior opener makes it a VIEW — the camera
# stays in the room and the director's `[shot:insert window~]` is the
# right call. The Chariot's "Across the street, an older man ... was
# leaning against a streetlight" is exactly that.
VIEW = re.compile(r"(window|looked out|looking out|through the glass|from the porch|"
                  r"from the doorway|in the doorway|the screen door)", re.I)

# (scene id, node index) pairs read on the Deck or in the prose and kept.
DELIBERATE = set()


_GEO = {}


def _boxes(glb):
    """The locale's boxes through the audit recorder — only for the
    presets whose NAME says nothing, so the builders that run here are
    few. Stdout swallowed: builders narrate."""
    if glb not in _GEO:
        import prop_overlap_audit as P
        import vantage_obstruction_audit as VO
        P.A.install_stubs()
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                _GEO[glb] = VO.boxes_for(glb)
            except Exception:
                _GEO[glb] = []
    return _GEO[glb]


def preset_kinds():
    """{preset_id: 'interior'|'exterior'|'?'}"""
    src = open(PV.GD).read()
    out = {}
    for m in PV.BLOCK.finditer(src):
        pid, body = m.group(1), m.group(2)
        kind = "?"
        if INT_NAME.search(pid):
            kind = "interior"
        elif EXT_NAME.search(pid):
            kind = "exterior"
        else:
            om, gm = PV.ORIGIN.search(body), PV.GLB.search(body)
            if om and gm:
                boxes = _boxes(gm.group(1))
                if boxes:
                    gx, gy, gz = (PV._ev(om.group(i)) for i in (1, 2, 3))
                    bx, by, bz = gx, -gz, gy
                    over = [n for n, c, h in boxes
                            if abs(c[0] - bx) <= h[0] and abs(c[1] - by) <= h[1]
                            and c[2] - h[2] > bz + 0.3 and min(h[0], h[1]) * 2 >= 2.0]
                    kind = "interior" if over else "exterior"
        out[pid] = kind
    return out


def main():
    show_all = "--all" in sys.argv
    kinds = preset_kinds()
    problems, checked = [], 0
    for f in sorted(glob.glob(os.path.join(SCENES, "**", "*.json"), recursive=True)):
        if os.path.basename(f) == "index.json":
            continue
        j = json.load(open(f, encoding="utf-8"))
        sid = j.get("id", os.path.basename(f)[:-5])
        kind, pid = "?", ""
        gone_inside = False
        recent = []   # the last two narrate lines, for the window test
        for i, n in enumerate(j.get("nodes", [])):
            t = n.get("t")
            if t == "bg":
                src = str(n.get("src") or "")
                if src.startswith("3d:"):
                    pid = src[3:]
                    kind = kinds.get(pid, "?")
                else:
                    pid, kind = src, "?"
                gone_inside = kind == "interior"
                continue
            if t != "narrate":
                continue
            text = DIRECT.sub("", str(n.get("text") or "")).strip()
            if not text or kind == "?":
                continue
            checked += 1
            claim = ""
            if INT_ASSERT.match(text):
                claim = "interior"
            elif EXT_ASSERT.match(text):
                claim = "exterior"
            elif EXT_SOFT.match(text) and not gone_inside:
                claim = "exterior"
            if claim == "interior":
                gone_inside = True
            viewed = claim == "exterior" and any(VIEW.search(r) for r in recent + [text])
            # four pages, not two: the page split turned "He stood at the
            # window" into a page of its own, three pages before the
            # "Across the street" it explains (2026-09-12)
            recent = (recent + [text])[-4:]
            if not claim or claim == kind or viewed:
                continue
            if (sid, i) in DELIBERATE:
                if show_all:
                    print("ok(kept)  %-30s #%-4d %s" % (sid, i, text[:60]))
                continue
            problems.append((sid, i, claim, pid, text))
    for sid, i, claim, pid, text in problems:
        print("PLACE   %-30s #%-4d prose is %-8s · bg %s (%s)\n        %s"
              % (sid, i, claim.upper(), pid, kinds.get(pid, "?"), text[:110]))
    print("\ninside_out_audit · %d narrated line(s) under a known vantage · "
          "%d contradicted" % (checked, len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
