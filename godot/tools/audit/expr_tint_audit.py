#!/usr/bin/env python3
"""expr_tint_audit.py — the expression tint table exists twice
(2026-09-11).

`CharLayer.gd`'s EXPR_TINTS is what the running game multiplies a mono
substrate portrait by. `tools/raster_substrate.py`'s EXPRESSION_TINTS
is what the offline rasterizer bakes into a PNG. They have to agree,
and nothing checked: the baker held six of the game's thirty-one, so
`--all-expressions` emitted six files and every other expression baked
FLAT — the lookup's default is no tint at all, which fails silently and
looks like a portrait that just didn't come out.

    python3 godot/tools/audit/expr_tint_audit.py

A suite gate at zero.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GD = os.path.join(ROOT, "godot", "scenes", "game", "CharLayer.gd")
PY = os.path.join(ROOT, "godot", "tools", "raster_substrate.py")


def gd_table():
    src = open(GD).read()
    i = src.index("const EXPR_TINTS")
    body = src[src.index("{", i):src.index("}", src.index("{", i))]
    return {m.group(1): tuple(round(float(x), 3) for x in m.group(2).split(",")[:3])
            for m in re.finditer(r'"(\w+)":\s*Color\(([^)]*)\)', body)}


def py_table():
    src = open(PY).read()
    m = re.search(r"EXPRESSION_TINTS\s*=\s*\{", src)
    body = src[m.end() - 1:src.index("}", m.end())]
    return {mm.group(1): tuple(round(float(x), 3) for x in mm.group(2).split(",")[:3])
            for mm in re.finditer(r'"(\w+)":\s*\(([^)]*)\)', body)}


def main():
    g, p = gd_table(), py_table()
    bad = 0
    for k in sorted(set(g) - set(p)):
        bad += 1
        print("TINT    %-14s the game tints it, the rasterizer bakes it FLAT" % k)
    for k in sorted(set(p) - set(g)):
        bad += 1
        print("TINT    %-14s the rasterizer bakes it, the game does not tint it" % k)
    for k in sorted(set(g) & set(p)):
        if g[k] != p[k]:
            bad += 1
            print("TINT    %-14s game %s | rasterizer %s" % (k, g[k], p[k]))
    print("\nexpr_tint_audit · %d expression(s) · %d disagreement(s)" % (len(g), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
