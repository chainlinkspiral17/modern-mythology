#!/usr/bin/env python3
"""scene_insert_node.py — insert a node into a chapter JSON and move every
node-index target that points at or past it (pass 411).

A chapter's choices and jumps aim at nodes BY INDEX: `opts[].goto`, a
jump's `goto`, a check's `pass` / `fail`. Inserting a node without moving
them sends the story to the wrong line. Pass 411's first ch10_cabin edit
left "Per's box" looping on itself, which vn_target_audit caught.

The file is edited as TEXT, so its own layout survives: hand-compacted
choice options, its indent and its escapes. The new node is written in
the neighbor's indent.

    python3 godot/tools/scene_insert_node.py SCENE.json INDEX '{"t": "bg", "src": "3d:x"}' [--dry]
    python3 godot/tools/scene_insert_node.py SCENE.json INDEX --shift-only [--dry]
        (a node was already inserted at INDEX: move the targets only)

Never insert into a VOICED chapter: its voice files are keyed by node index.
The tool refuses a chapter with any "voice" field. After it runs, also move
by hand any record keyed by node index for that chapter:
resources/vn/trip_direction.json beats, cue_meaning_scan.py JUDGED keys,
and music cue sheets. The tool lists the trip beats it finds.
"""
import json
import os
import re
import sys

GODOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TARGET = re.compile(r'("(?:goto|pass|fail)"\s*:\s*)(\d+)')


def node_spans(raw):
    """[(start, end)] of each element of the top-level "nodes" array."""
    m = re.search(r'"nodes"\s*:\s*\[', raw)
    if m:
        pos = m.end()
    else:                                   # a bare list
        pos = raw.index("[") + 1
    dec = json.JSONDecoder()
    spans = []
    while True:
        while raw[pos] in " \t\r\n,":
            pos += 1
        if raw[pos] == "]":
            return spans, pos
        _obj, end = dec.raw_decode(raw, pos)
        spans.append((pos, end))
        pos = end


def shift_targets(raw, region, idx):
    a, b = region
    seg = raw[a:b]
    moved = []

    def rep(mm):
        v = int(mm.group(2))
        if v >= idx:
            moved.append((v, v + 1))
            return mm.group(1) + str(v + 1)
        return mm.group(0)
    seg = TARGET.sub(rep, seg)
    return raw[:a] + seg + raw[b:], moved


def main():
    args = [a for a in sys.argv[1:] if a != "--dry"]
    dry = "--dry" in sys.argv
    if len(args) < 3:
        sys.exit(__doc__)
    path = args[0] if os.path.isabs(args[0]) else os.path.join(GODOT, "resources", "scenes", args[0])
    if not os.path.exists(path):
        path = args[0]
    idx = int(args[1])
    raw = open(path, encoding="utf-8").read()
    data = json.loads(raw)
    nodes = data.get("nodes", []) if isinstance(data, dict) else data
    if any(isinstance(n, dict) and n.get("voice") for n in nodes):
        sys.exit("refused: %s is voiced (voice files are keyed by node index)" % os.path.basename(path))
    spans, close = node_spans(raw)
    assert len(spans) == len(nodes), (len(spans), len(nodes))
    if args[2] == "--shift-only":
        out, moved = shift_targets(raw, (spans[0][0], close), idx)
    else:
        new = json.loads(args[2])
        if idx > len(nodes):
            sys.exit("index past the end")
        # the neighbor's indent and layout
        ref = spans[min(idx, len(spans) - 1)]
        line_start = raw.rfind("\n", 0, ref[0]) + 1
        ind = raw[line_start:ref[0]]
        body = json.dumps(new, indent=2, ensure_ascii=False)
        body = ("\n" + ind).join(body.split("\n"))
        # move targets first (over every node), then insert the new one
        out, moved = shift_targets(raw, (spans[0][0], close), idx)
        spans2, _ = node_spans(out)
        at = spans2[idx][0] if idx < len(spans2) else None
        if at is None:          # append after the last node
            last_end = spans2[-1][1]
            out = out[:last_end] + ",\n" + ind + body + out[last_end:]
        else:
            out = out[:at] + body + ",\n" + ind + out[at:]
    json.loads(out)
    sid = os.path.basename(path)[:-5]
    print("%s: %s at %d · %d target(s) moved %s" % (
        sid, "shift only" if args[2] == "--shift-only" else "inserted", idx, len(moved), moved))
    td = os.path.join(GODOT, "resources", "vn", "trip_direction.json")
    if os.path.exists(td):
        t = json.load(open(td))
        scenes = t.get("scenes", t) if isinstance(t, dict) else {}
        e = scenes.get(sid) if isinstance(scenes, dict) else None
        if isinstance(e, dict):
            later = [b.get("node") for b in e.get("beats", []) if isinstance(b.get("node"), int) and b["node"] >= idx]
            if later:
                print("   trip_direction beats at/after %d to move by hand: %s" % (idx, later))
    if not dry:
        open(path, "w", encoding="utf-8").write(out)


if __name__ == "__main__":
    main()
