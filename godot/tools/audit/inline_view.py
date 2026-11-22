#!/usr/bin/env python3
"""inline_view.py — a line that changes the room itself (pass 447, 2026-11-21).

`[view:preset]` FIRST in the text of a narrate / say / think / interlude is a
bg node without a node: GameEngine plays the cut (with its transition), then
the line. It exists for the voiced chapters, where a node cannot go in without
moving every index after it (voice lines, saves, trip beats).

Every tool that asks "which room is this line in?" walks the nodes through
here, so the engine's rule and the gates' are one rule:

    import inline_view as IV
    for i, n in IV.walk(nodes):      # enumerate(nodes), plus a bg node (same
        if n.get("t") == "bg": ...   #   index) before each line that cuts
    for n in IV.nodes(nodes): ...    # the same, without the index
    IV.of(node)                      # the preset a line cuts to, or None

The node walk() adds is {"t": "bg", "src": "3d:<preset>", "inline_view": True}:
a tool that WRITES bg nodes back must skip it (it is not in the file).

    python3 godot/tools/audit/inline_view.py     # every inline view; a tag
                                                 # that is not first, or names
                                                 # no preset, fails
"""
import glob
import json
import os
import re
import sys

TEXT = ("narrate", "say", "think", "interlude")
_FIRST = re.compile(r"^\[view:([^\]\r\n]+)\]")
_ANY = re.compile(r"\[view:([^\]\r\n]*)\]")


def of(node):
    """The preset this line cuts to before it shows, or None."""
    if not isinstance(node, dict) or node.get("t") not in TEXT:
        return None
    text = node.get("text")
    if not isinstance(text, str) or not text.startswith("[view:"):
        return None
    m = _FIRST.match(text)
    if not m:
        return None
    parts = m.group(1).split()
    return parts[0] if parts else None


def walk(nodes):
    """enumerate(nodes), with a bg node before every line that cuts."""
    for i, n in enumerate(nodes or []):
        v = of(n)
        if v:
            yield i, {"t": "bg", "src": "3d:" + v, "inline_view": True}
        yield i, n


def nodes(nodes_):
    for _i, n in walk(nodes_):
        yield n


def strip(text):
    """The text without its leading [view:] tag."""
    return _FIRST.sub("", text, count=1) if isinstance(text, str) else text


STYLES = ("cut", "fade", "dissolve", "flash")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    godot = os.path.normpath(os.path.join(here, "..", ".."))
    sys.path.insert(0, here)
    import view_tags as VT
    presets = set(VT.preset_ids())
    found, bad = [], []
    for f in sorted(glob.glob(os.path.join(godot, "resources", "scenes", "**", "*.json"), recursive=True)):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        ns = d.get("nodes") if isinstance(d, dict) else None
        if not isinstance(ns, list):
            continue
        rel = os.path.relpath(f, godot)
        for i, n in enumerate(ns):
            if not isinstance(n, dict):
                continue
            for key, val in n.items():
                if isinstance(val, str) and "[view:" in val and (key != "text" or n.get("t") not in TEXT):
                    bad.append("%s#%d  [view:] in a %s node's %r: only a line's text carries one"
                               % (rel, i, n.get("t"), key))
            text = n.get("text")
            if n.get("t") not in TEXT or not isinstance(text, str) or "[view:" not in text:
                continue
            tags = _ANY.findall(text)
            if len(tags) > 1:
                bad.append("%s#%d  %d [view:] tags on one line" % (rel, i, len(tags)))
            if not _FIRST.match(text):
                bad.append("%s#%d  [view:%s] is not FIRST in the text: the cut would play after "
                           "the line's other cues (a shot it then clears)" % (rel, i, tags[0]))
                continue
            parts = tags[0].split()
            if not parts or parts[0] not in presets:
                bad.append("%s#%d  [view:%s] names no camera preset" % (rel, i, tags[0]))
                continue
            if len(parts) > 2 or (len(parts) == 2 and parts[1] not in STYLES):
                bad.append("%s#%d  [view:%s]: after the preset comes one transition of %s"
                           % (rel, i, tags[0], "/".join(STYLES)))
                continue
            found.append((rel, i, tags[0]))
    print("inline_view · %d line(s) change the room themselves" % len(found))
    for rel, i, tag in found:
        print("  %s#%d  -> %s" % (rel, i, tag))
    for b in bad:
        print("  ✗ " + b)
    if bad:
        print("inline_view · %d fault(s)" % len(bad))
        return 1
    print("inline_view · clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
