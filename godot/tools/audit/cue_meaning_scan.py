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

    python3 cue_meaning_scan.py [--generic] [--all]
      --generic: cues on a generic surface (table, door, window ...) whose line
      names a specific object with its own frame (pass 413)
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

# --generic: cues on a generic surface (table, door, window ...) whose line names a
# specific framed object. Pass 413: 98 rows read; 77 stand as cued.
JUDGED_GENERIC = {
    "meld_seam_1_2:20": "KEEP (pass 413 reader, node-cited)",
    "vol1_ch3_bar:6": "KEEP (pass 413 reader, node-cited)",
    "vol2_ch12_drift_wood_intro:16": "KEEP (pass 413 reader, node-cited)",
    "vol2_ch3_points_of_impact:34": "KEEP (pass 413 reader, node-cited)",
    "vol4_curtain_call:29": "KEEP (pass 413 reader, node-cited)",
    "vol5_ch10_wheel:11": "KEEP (pass 413 reader, node-cited)",
    "vol5_ch11_justice:48": "KEEP (pass 413 reader, node-cited)",
    "vol5_ch17_star:107": "KEEP (pass 413 reader, node-cited)",
    "vol5_ch17_star:109": "KEEP (pass 413 reader, node-cited)",
    "vol5_ch17_star:30": "KEEP (pass 413 reader, node-cited)",
    "vol5_ch17_star:60": "KEEP (pass 413 reader, node-cited)",
    "vol5_ch17_star:87": "KEEP (pass 413 reader, node-cited)",
    "vol5_ch18_moon:193": "KEEP (pass 413 reader, node-cited)",
    "vol5_ch20_judgement:87": "KEEP (pass 413 reader, node-cited)",
    "vol5_ch4_emperor:50": "KEEP (pass 413 reader, node-cited)",
    "vol5_ch7_chariot:155": "KEEP (pass 413 reader, node-cited)",
    "vol5_ch7_chariot:79": "KEEP (pass 413 reader, node-cited)",
    "vol5_ch9_hermit:77": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch0_prelude:76": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch10_home:75": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch11_eileen:134": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch12_cosmic:226": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch13_two_a_days:23": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch13_two_a_days:59": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch14_live_oak:107": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch14_live_oak:115": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch14_substation_nine:51": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch15_home:16": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch15_kwik_stop:290": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch17_porch:6": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch18_stockroom:92": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch1_bedroom:9": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch21_cosmic:132": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch21_cosmic:92": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch22_vinton:203": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch23_sunday:31": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch2_kwik_stop:33": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch3_jesse_bedroom:43": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch3_sam_bedroom:16": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch4_miller_office:4": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch4_sam_list:24": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch5_radio:24": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch6_kwik_stop_open:21": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch7_henderson_kitchen:20": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch7_henderson_kitchen:29": "KEEP (pass 413 reader, node-cited)",
    "vol6_ch8_kowalski_kitchen:23": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch12_lena:64": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch12_morning:126": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch15_bread:87": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch15_loft:15": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch16_aud:104": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch16_aud:160": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch17_aria:14": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch17_dawn:34": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch17_dawn:37": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch18_stick:76": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch19_ring:48": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch19_ring:64": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch1_finn:7": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch1_morning:10": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch1_morning:14": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch20_calls:39": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch20_door:10": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch21_cabin:38": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch21_tower:21": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch21_tower:44": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch22_portal:9": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch2_morning:133": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch3_apartment:14": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch3_studio:61": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch4_finn:134": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch5_roy:67": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch7_six_oclock:29": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch8_aria:66": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch8_monday:12": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch8_six_oclock:11": "KEEP (pass 413 reader, node-cited)",
    "vol7_ch9_evening:33": "KEEP (pass 413 reader, node-cited)",
}
GENERIC = {"table", "counter", "door", "window", "wall", "room", "desk", "shelf", "floor", "kitchen", "bench",
           "porch", "yard", "street", "road", "lot", "hall", "doorway", "booth", "bar", "shelves", "stove", "sink"}


def words_for(i):
    return {w for w in SYNONYMS.get(i, []) + [i] if len(w) >= 3}


def has(text, ws):
    return any(re.search(r"\b%s(s|es)?\b" % re.escape(w).replace("_", r"[-\s]?"), text) for w in ws)


def main():
    show_all = "--all" in sys.argv
    generic = "--generic" in sys.argv
    judged = JUDGED_GENERIC if generic else JUDGED
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
                key = "%s:%d" % (fn[:-5], k)
                if generic:
                    if x not in GENERIC:
                        continue
                    alts = sorted(y for y in ids if y != x and y not in GENERIC and has(plain, words_for(y))
                                  and not (words_for(y) & words_for(x)))
                    if alts and (show_all or key not in JUDGED_GENERIC):
                        rows.append((key, cur, x, alts, " ".join(plain[:140].split())))
                    continue
                if has(plain, words_for(x)):
                    continue
                alts = sorted(y for y in ids if y != x and has(plain, words_for(y))
                              and not (words_for(y) & words_for(x)))
                if not alts:
                    continue
                if key in JUDGED and not show_all:
                    continue
                rows.append((key, cur, x, alts, " ".join(plain[:140].split())))
    for key, cur, x, alts, txt in rows:
        print("  %s [%s] insert %s · line names %s · %s%s" % (
            key, cur, x, ",".join(alts), txt, ("   (judged: %s)" % judged[key]) if key in judged else ""))
    unread = len([r for r in rows if r[0] not in judged])
    print("cue_meaning_scan%s · %d unread cue(s) whose line names another framed object (%d judged)"
          % (" --generic" if generic else "", unread, len(judged)))


if __name__ == "__main__":
    main()
