#!/usr/bin/env python3
"""shot_seed.py — cut the comic at its prose anchors (2026-09-09).

The Deck's verdict on the latter half of Major Arcana: "real bad shot
direction all throughout". The density scan said why: 8–12 cues over
100–137 nodes, holds of fifteen and twenty lines on one frame. The
locales already carry the vocabulary (shot_insert_*, shot_closeup_*,
shot_establish[_b/_c]); the chapters just don't use it.

This seeds cuts by the playbook's grammar, using ONLY markers that
exist in the chapter's locale:

  · a `say` by a character with a shot_closeup_<char> marker, when the
    speaker changes and ≥ 3 nodes have passed since the last cue →
    [shot:closeup <char>]
  · a `narrate` that names an insert's object (the marker id's words or
    shot_marker_audit's SYNONYMS), ≥ 4 nodes since the last cue, the
    insert not used in the last 12 nodes → [shot:insert <id>]
  · ≥ 6 nodes held on a closeup/insert → [shot:establish] (rotating
    through establish_b / establish_c when the locale has them, so a
    long chapter is not one wide frame)
  · budget: cues never exceed nodes / 4; a node that already carries a
    [shot:] is the author's and is never touched; other leading
    directives ([trip:], [mood:], [beat:]) are kept — the shot goes
    in front of them.

Edits are RAW TEXT SPLICES (the node's encoded "text" string gets the
cue prefixed) — the file is never re-serialized, so indentation,
key order and unicode escapes survive.

Usage:
    python3 godot/tools/audit/shot_seed.py --dry <chapter.json>…
    python3 godot/tools/audit/shot_seed.py <chapter.json>…
    python3 godot/tools/audit/shot_seed.py --light <chapter.json>…   # authored chapters: fewer, wider cuts
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import shot_marker_audit as SM

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DIRECT_RX = re.compile(r"^\[(shot|panel|stage|mood|beat|trip):([^\]\r\n]+)\]\s*")
SHOT_RX = re.compile(r"\[shot:([^\]~]+)~?\]")

MIN_GAP_CLOSEUP = 3
MIN_GAP_INSERT = 4
HOLD_MAX = 6
INSERT_REUSE = 12
BUDGET_DIV = 4
MIN_INDEX = 8           # no seeded cut before the eighth node
STOP_WORDS = {"the", "a", "an", "of", "and", "her", "his", "its", "on", "in", "up", "off", "b", "c", "d", "e"}


def locale_markers(src):
    """'3d:<preset>' → (locale basename, [marker names])."""
    if not src.startswith("3d:"):
        return None, []
    preset = src[3:]
    p2s = SM.preset_to_scene()
    scene = p2s.get(preset)
    if not scene:
        return None, []
    return os.path.basename(scene)[:-5], SM.markers_in(scene)


def words_for(cue_id):
    ws = set(w for w in re.split(r"[_\s]+", cue_id.lower()) if w and w not in STOP_WORDS)
    for s in SM.SYNONYMS.get(cue_id, []):
        for w in re.split(r"[_\s]+", s.lower()):
            # a synonym anchors prose only when it is a real word for the
            # thing (≥ 5 letters): "note" is not a notebook, "hull" not
            # the steamship
            if w and w not in STOP_WORDS and len(w) >= 5:
                ws.add(w)
    return ws


def mentions(text, words):
    low = text.lower()
    for w in words:
        if len(w) < 3:
            continue
        if re.search(r"\b" + re.escape(w) + r"s?\b", low):
            return True
    return False


def strip_directives(text):
    while True:
        m = DIRECT_RX.match(text)
        if not m:
            return text
        text = text[m.end():]


def plan(path):
    d = json.load(open(path))
    nodes = d.get("nodes", [])
    bgs = [n for n in nodes if n.get("t") == "bg"]
    src = str(bgs[0].get("src", "")) if bgs else ""
    locale, markers = locale_markers(src)
    if not markers:
        return locale, [], nodes, "no markers"

    def vocabulary(markers, loc_name):
        establishes = [m[len("shot_"):] for m in markers if m.startswith("shot_establish")]
        if "establish" not in establishes:
            establishes.append("establish")      # the preset camera is always a wide
        establishes.sort()
        closeups = {m[len("shot_closeup_"):]: m for m in markers if m.startswith("shot_closeup_")}
        # an insert is usable only when the locale's builder HAS the
        # object (shot_marker_audit's blind-cue test) — a marker that
        # frames nothing named is not a shot to seed
        inserts = {m[len("shot_insert_"):]: m for m in markers if m.startswith("shot_insert_")
                   and SM.object_exists(loc_name, m[len("shot_insert_"):]) is not False}
        # the room's GENERIC closeup pair (marker_author --closeup / -b):
        # a bust frame of the conversation spot and its reverse. A room
        # with no marker for this character still has a face to cut to.
        generic = [c for c in ("person", "person_b") if c in closeups]
        return establishes, closeups, inserts, {k: words_for(k) for k in inserts}, generic

    establishes, closeups, inserts, insert_words, generic = vocabulary(markers, locale)

    edits = []                       # (node index, cue string)
    existing = 0
    last_cue = -99
    current = "establish"
    last_closeup = None
    last_insert_at = {}
    est_i = 0
    # each speaker OWNS a side of the room for the length of a scene (the
    # film rule — don't cross the line): the first speaker takes the
    # generic frame, the second its reverse, and they alternate from there
    speaker_side = {}
    for i, nd in enumerate(nodes):
        t = nd.get("t")
        text = nd.get("text") if isinstance(nd.get("text"), str) else None
        if t == "bg" and i > 0:
            # a mid-chapter locale change: the vocabulary is the NEW
            # locale's markers from here on (ch11 moves office → studio)
            _loc, mk = locale_markers(str(nd.get("src", "")))
            # ALWAYS swap — a locale with no markers has an empty
            # vocabulary (only the preset wide), never the last one's
            establishes, closeups, inserts, insert_words, generic = vocabulary(mk or [], _loc or "")
            last_insert_at = {}
            speaker_side = {}
            est_i = 0
            current = "establish"
            last_cue = i
            last_closeup = None
            continue
        if i < MIN_INDEX and not (text and SHOT_RX.search(text[:80]) and DIRECT_RX.match(text)):
            continue                          # the chapter's opening card and first breath are the author's
        if text is not None:
            m = SHOT_RX.search(text[:80])
            if m and DIRECT_RX.match(text):
                existing += 1
                last_cue = i
                cue = m.group(1).strip()
                current = cue.split()[0]
                if current == "closeup":
                    last_closeup = cue.split()[1] if len(cue.split()) > 1 else None
                elif current == "insert" and len(cue.split()) > 1:
                    last_insert_at[cue.split()[1]] = i
                continue
        if t == "say" and text is not None:
            ch = str(nd.get("char", "")).lower()
            if ch in closeups and ch != last_closeup and i - last_cue >= MIN_GAP_CLOSEUP:
                edits.append((i, "[shot:closeup %s]" % ch))
                last_cue = i
                current = "closeup"
                last_closeup = ch
                continue
            if generic and ch and ch != last_closeup and i - last_cue >= MIN_GAP_CLOSEUP:
                side = speaker_side.get(ch)
                if side is None:
                    side = generic[len(speaker_side) % len(generic)]
                    speaker_side[ch] = side
                # a cut to the frame we are already on is not a cut
                if side != speaker_side.get(last_closeup, None):
                    edits.append((i, "[shot:closeup %s]" % side))
                    last_cue = i
                    current = "closeup"
                    last_closeup = ch
                    continue
        if t == "narrate" and text is not None:
            body = strip_directives(text)
            hit = None
            for k, ws in insert_words.items():
                if i - last_insert_at.get(k, -99) < INSERT_REUSE:
                    continue
                if mentions(body, ws):
                    hit = k
                    break
            if hit and i - last_cue >= MIN_GAP_INSERT:
                edits.append((i, "[shot:insert %s]" % hit))
                last_cue = i
                current = "insert"
                last_insert_at[hit] = i
                last_closeup = None
                continue
            if current != "establish" and i - last_cue >= HOLD_MAX:
                est = establishes[est_i % len(establishes)] if establishes else "establish"
                est_i += 1
                edits.append((i, "[shot:%s]" % est))
                last_cue = i
                current = "establish"
                last_closeup = None
                continue
    budget = max(0, len(nodes) // BUDGET_DIV - existing)
    if len(edits) > budget:
        # keep the earliest cuts — the reader meets the grammar first
        edits = edits[:budget]
    return locale, edits, nodes, "ok:%d" % existing


def splice(path, nodes, edits):
    raw = open(path, encoding="utf-8").read()
    pos = 0
    out = raw
    offset = 0
    # walk nodes in order, locating each node's encoded text in the raw
    # file so the prefix lands on the right occurrence
    edit_at = dict(edits)
    for i, nd in enumerate(nodes):
        text = nd.get("text")
        if not isinstance(text, str):
            continue
        cands = [json.dumps(text, ensure_ascii=False), json.dumps(text, ensure_ascii=True)]
        found = -1
        enc = None
        for c in cands:
            k = raw.find('"text": ' + c, pos)
            if k < 0:
                k = raw.find('"text":' + c, pos)
            if k >= 0 and (found < 0 or k < found):
                found, enc = k, c
        if found < 0:
            raise RuntimeError("node %d text not found in raw file: %r" % (i, text[:40]))
        if i in edit_at:
            q = raw.find(enc, found)           # start of the encoded string (the opening quote)
            ins = q + 1 + offset
            out = out[:ins] + edit_at[i] + out[ins:]
            offset += len(edit_at[i])
        pos = found + len(enc)
    open(path, "w", encoding="utf-8").write(out)


def main():
    global MIN_GAP_CLOSEUP, MIN_GAP_INSERT, HOLD_MAX, BUDGET_DIV
    dry = "--dry" in sys.argv
    if "--light" in sys.argv:
        # chapters that already carry authored grammar: wider gaps,
        # longer holds, a smaller budget — seed only the obvious cuts
        MIN_GAP_CLOSEUP, MIN_GAP_INSERT, HOLD_MAX, BUDGET_DIV = 5, 7, 9, 6
    paths = [a for a in sys.argv[1:] if not a.startswith("--")]
    total = 0
    for p in paths:
        locale, edits, nodes, why = plan(p)
        name = os.path.basename(p)[:-5]
        if not why.startswith("ok"):
            print("%-28s %s (%s)" % (name, why, locale))
            continue
        existing = int(why.split(":")[1])
        print("%-28s %-24s nodes %3d  has %2d  +%d cues" % (name, locale, len(nodes), existing, len(edits)))
        for i, cue in edits:
            body = strip_directives(str(nodes[i].get("text", "")))[:56].replace("\n", " ")
            print("    %3d %-26s %s" % (i, cue, body))
        total += len(edits)
        if not dry and edits:
            splice(p, nodes, edits)
            json.load(open(p))          # the splice must leave valid JSON
    print("\n%d cue(s) %s" % (total, "planned" if dry else "written"))


if __name__ == "__main__":
    main()
