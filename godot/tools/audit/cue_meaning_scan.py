#!/usr/bin/env python3
"""cue_meaning_scan.py — insert cues whose line names ANOTHER framed object
and not their own (pass 409, after ch16's "[shot:insert ring]" cut to a
clothes rounder on "The bell rang when he unlocked it").

For every [shot:insert X] on a line, in the 3D view current at that line:
the line (tags stripped) names some other object Y that has its own insert
frame in that view, and names neither X nor X's synonyms (from
shot_marker_audit.SYNONYMS). Such a cue may mean Y, or it may set up the
next line, or X may be named by a word the synonyms lack. Read each row
and decide:
  KEEP      the object is what the line (or the next, in one breath) is about
  RETARGET  to a frame the view has, that the line is about
  MOVE      the tag to the nearby line (same bg) that names X
  DROP      a person, a hand, a gesture, an action: cast never appear in
            object close-ups
Rows read and kept go in JUDGED below, so a diff shows each judgement. The report lists only
the unread rows. Report only (not a gate).

    python3 cue_meaning_scan.py [--all]
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bg_resolve  # noqa: E402
from shot_marker_audit import preset_to_scene, markers_in, SYNONYMS, SCENES  # noqa: E402

CUE = re.compile(r"\[shot:insert\s+([a-z0-9_]+)~?\]")
TAG = re.compile(r"\[[^\]]*\]")

# file:node -> why it stands. Pass 409: 82 rows read by a node-cited reader
# and spot-checked; 45 stand (37 kept as cued, 8 after a retarget).
JUDGED = {
    "vol1_ch2_painting:9": "\"Faust paints.\": the table he paints at (pass 409)",
    "vol1_ch7_ink:37": "KEEP (pass 409 reader, node-cited)",
    "vol1_link_jukebox:1": "KEEP (pass 409 reader, node-cited)",
    "vol2_ch1_history_one:40": "KEEP (pass 409 reader, node-cited)",
    "vol2_ch2_interlude_three:8": "KEEP (pass 409 reader, node-cited)",
    "vol2_ch4_night_lights:6": "house: the night-lights chapter (\"that celebration\"); the barn frame sat in the roadside view's area (pass 409)",
    "vol3_ch4_the_coast:15": "KEEP (pass 409 reader, node-cited)",
    "vol3_ch6_game_room:18": "KEEP (pass 409 reader, node-cited)",
    "vol5_ch0_booth6:22": "booth six is the line's subject (pass 409)",
    "vol5_ch17_star:109": "KEEP (pass 409 reader, node-cited)",
    "vol5_ch20_judgement:77": "KEEP (pass 409 reader, node-cited)",
    "vol5_ch4_emperor:70": "KEEP (pass 409 reader, node-cited)",
    "vol5_ch7_chariot:14": "KEEP (pass 409 reader, node-cited)",
    "vol5_ch7_chariot:79": "KEEP (pass 409 reader, node-cited)",
    "vol5_ch9_hermit:52": "KEEP (pass 409 reader, node-cited)",
    "vol5_ch9_hermit:61": "KEEP (pass 409 reader, node-cited)",
    "vol6_ch10_home:75": "KEEP (pass 409 reader, node-cited)",
    "vol6_ch10_night_shift:95": "KEEP (pass 409 reader, node-cited)",
    "vol6_ch12_cosmic:178": "KEEP (pass 409 reader, node-cited)",
    "vol6_ch15_kwik_stop:102": "KEEP (pass 409 reader, node-cited)",
    "vol6_ch18_letter:36": "KEEP (pass 409 reader, node-cited)",
    "vol6_ch20_bridge:108": "KEEP (pass 409 reader, node-cited)",
    "vol6_ch20_prints:58": "KEEP (pass 409 reader, node-cited)",
    "vol6_ch21_cosmic:103": "KEEP (pass 409 reader, node-cited)",
    "vol6_ch21_cosmic:16": "KEEP (pass 409 reader, node-cited)",
    "vol6_ch21_cosmic:58": "KEEP (pass 409 reader, node-cited)",
    "vol6_ch22_foxhole:214": "KEEP (pass 409 reader, node-cited)",
    "vol6_ch23_sunday:100": "KEEP (pass 409 reader, node-cited)",
    "vol6_ch2_cosmic:28": "KEEP (pass 409 reader, node-cited)",
    "vol6_ch2_dumpster:75": "KEEP (pass 409 reader, node-cited)",
    "vol6_ch3_jesse_bedroom:25": "KEEP (pass 409 reader, node-cited)",
    "vol6_ch3_sam_bedroom:16": "the door she hears it through (pass 409)",
    "vol6_ch6_safehouse:21": "KEEP (pass 409 reader, node-cited)",
    "vol6_ch9_room:88": "KEEP (pass 409 reader, node-cited)",
    "vol7_ch11_bowl:23": "substrate_bowl: \"the size of his palm\" (pass 408)",
    "vol7_ch11_bowl:48": "substrate_bowl (pass 408)",
    "vol7_ch11_bowl:53": "substrate_bowl: \"the ferret on the substrate's bowl\" (pass 408)",
    "vol7_ch11_bowl:55": "substrate_bowl (pass 408)",
    "vol7_ch11_per:119": "KEEP (pass 409 reader, node-cited)",
    "vol7_ch14_figure:80": "KEEP (pass 409 reader, node-cited)",
    "vol7_ch14_painting:104": "face: she paints the jaw and the neck (pass 409)",
    "vol7_ch19_roy:46": "KEEP (pass 409 reader, node-cited)",
    "vol7_ch20_wall:123": "KEEP (pass 409 reader, node-cited)",
    "vol7_ch21_cabin:27": "KEEP (pass 409 reader, node-cited)",
    "vol7_ch22_portal:68": "KEEP (pass 409 reader, node-cited)",
    "vol7_ch6_sunday:7": "KEEP (pass 409 reader, node-cited)",
}


def words_for(i):
    return {w for w in SYNONYMS.get(i, []) + [i] if len(w) >= 3}


def has(text, ws):
    return any(re.search(r"\b%s(s|es)?\b" % re.escape(w).replace("_", r"[-\s]?"), text) for w in ws)


def main():
    show_all = "--all" in sys.argv
    p2s = preset_to_scene()
    rows = []
    for dp, _, fs in os.walk(SCENES):
        for fn in sorted(fs):
            if not fn.endswith(".json"):
                continue
            try:
                j = json.load(open(os.path.join(dp, fn)))
            except Exception:
                continue
            nodes = j.get("nodes", []) if isinstance(j, dict) else j
            sid = j.get("id", fn[:-5]) if isinstance(j, dict) else fn[:-5]
            cur = ""
            for k, n in enumerate(nodes):
                if not isinstance(n, dict):
                    continue
                if n.get("t") == "bg":
                    cur = bg_resolve.preset_of(n.get("src"), sid) or ""
                t = n.get("text")
                if not cur or not isinstance(t, str):
                    continue
                m = CUE.search(t)
                if not m:
                    continue
                x = m.group(1)
                ids = set()
                for h in markers_in(p2s.get(cur, "")) or set():
                    mm = re.match(r"shot_insert_([a-z0-9_]+?)(?:__([a-z0-9_]+))?$", h)
                    if mm and mm.group(2) in (None, cur):
                        ids.add(mm.group(1))
                plain = TAG.sub("", t).lower()
                if has(plain, words_for(x)):
                    continue
                alts = sorted(y for y in ids if y != x and has(plain, words_for(y))
                              and not (words_for(y) & words_for(x)))
                if not alts:
                    continue
                key = "%s:%d" % (fn[:-5], k)
                if key in JUDGED and not show_all:
                    continue
                rows.append((key, cur, x, alts, " ".join(plain[:140].split())))
    for key, cur, x, alts, txt in rows:
        print("  %s [%s] insert %s · line names %s · %s%s" % (
            key, cur, x, ",".join(alts), txt, ("   (judged: %s)" % JUDGED[key]) if key in JUDGED else ""))
    unread = len([r for r in rows if r[0] not in JUDGED])
    print("cue_meaning_scan · %d unread cue(s) whose line names another framed object (%d judged)"
          % (unread, len(JUDGED)))


if __name__ == "__main__":
    main()
