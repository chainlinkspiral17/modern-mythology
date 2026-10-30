#!/usr/bin/env python3
"""vn_insert_node — insert a node into a VN scene JSON without breaking its jumps.

Scene nodes are addressed BY INDEX: a choice's `"goto": 25` jumps to node 25,
and the music cue sheets in resources/music/direction.json key their beats to
node indices (`{"at": 25, ...}`). Inserting a node (a `bg` cut to a new
vantage, a `music` directive) shifts every later node by one, so each of those
references has to move with it. This does that, and keeps the file's own
indentation and escaping so the diff is the insert and the renumbered jumps.

    python3 godot/tools/vn_insert_node.py <scene.json> <index> '<node json>'
    python3 godot/tools/vn_insert_node.py resources/scenes/vol4/vol4_story_map_of_the_city.json 25 \\
        '{"t": "bg", "src": "3d:dead_store_roof"}'
    ... --dry-run   print what would change, write nothing

The new node lands AT <index> (the old node <index> becomes <index>+1).
- a goto pointing PAST <index> is bumped by one, so it still reaches its line;
- a goto pointing AT <index> is left alone: it now lands on the new node, which
  plays first and falls through to the old line ("climb." cuts to the roof,
  then reads its line);
- a music beat at <index> or later is bumped: a beat belongs to its LINE.
(2026-10-30: written for vol 4's dead store roof, where node 22's choice jumps
to 23 and 25 by index. The first version bumped a goto AT the index too, so
"climb." jumped past the new cut — thread B caught it.)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GODOT = os.path.normpath(os.path.join(HERE, ".."))
DIRECTION = os.path.join(GODOT, "resources", "music", "direction.json")


def _indent_of(raw):
    m = re.search(r'^\{\s*\n( +)"', raw)
    return len(m.group(1)) if m else 2


def _bump_gotos(obj, at):
    n = 0
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "goto" and isinstance(v, int) and v > at:
                obj[k] = v + 1
                n += 1
            else:
                n += _bump_gotos(v, at)
    elif isinstance(obj, list):
        for v in obj:
            n += _bump_gotos(v, at)
    return n


def _dump(obj, raw):
    out = json.dumps(obj, indent=_indent_of(raw), ensure_ascii=("\\u" in raw))
    return out + ("\n" if raw.endswith("\n") else "")


def main(argv):
    dry = "--dry-run" in argv
    args = [a for a in argv if a != "--dry-run"]
    if len(args) != 3:
        sys.exit(__doc__)
    path, at, node_src = args[0], int(args[1]), args[2]
    node = json.loads(node_src)
    raw = open(path).read()
    scene = json.loads(raw)
    nodes = scene["nodes"]
    if not (0 <= at <= len(nodes)):
        sys.exit("index %d outside 0..%d" % (at, len(nodes)))
    bumped = _bump_gotos(nodes, at)
    nodes.insert(at, node)
    out = _dump(scene, raw)
    json.loads(out)
    # the music cue sheet for this scene, if one is authored
    beats_bumped = 0
    draw = None
    if os.path.exists(DIRECTION):
        draw = open(DIRECTION).read()
        direction = json.loads(draw)
        sheet = direction.get("scenes", {}).get(scene.get("id", ""), None)
        if isinstance(sheet, dict):
            for b in sheet.get("beats", []):
                if isinstance(b.get("at"), int) and b["at"] >= at:
                    b["at"] += 1
                    beats_bumped += 1
    print("%s: node inserted at %d (%d nodes now); %d goto(s) bumped; %d music beat(s) bumped"
          % (os.path.basename(path), at, len(nodes), bumped, beats_bumped))
    if dry:
        return
    open(path, "w").write(out)
    if beats_bumped:
        open(DIRECTION, "w").write(_dump(direction, draw))


if __name__ == "__main__":
    main(sys.argv[1:])
