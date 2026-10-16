#!/usr/bin/env python3
"""tscn_syntax_audit — what Godot's scene parser rejects, found here first.

2026-09-25: highway_101 and small_wood_road were skipped on every
contact sheet ("scene failed to load — GLB present"). The GLBs were
fine. Each scene carried `background_color = Color(0.62, 0.66, 0.72)`:
Godot's VariantParser wants exactly four arguments for Color, so the
whole .tscn failed to parse and `load()` returned null. Nothing in the
suite read .tscn files as SYNTAX. This does, for the constructors a
locale scene uses, plus the references a parse can fail on:

  · constructor arity — Color 4, Vector2 2, Vector3 3, Vector4 4,
    Quaternion 4, Plane 4, Rect2 4, AABB 6, Basis 9, Transform2D 6,
    Transform3D 12, Vector2i 2, Vector3i 3, Vector4i 4
  · every ExtResource("id") / SubResource("id") used is declared
  · every ext_resource path exists in the project (GLBs excepted —
    they are built on the Deck, not tracked)
  · `[node … parent="A/B"]` — A/B was declared earlier in the file,
    or its first segment is a node instanced from a PackedScene
    (children inside an instance cannot be checked here)

Usage:  python3 tscn_syntax_audit.py [--all]     (default: scenes/)
Prints one line per defect and `tscn_syntax · N defect(s)`; exit 1 on any.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GODOT = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOTS = [os.path.join(GODOT, "scenes")]
if "--all" in sys.argv:
    ROOTS = [GODOT]

ARITY = {
    "Color": 4, "Vector2": 2, "Vector3": 3, "Vector4": 4, "Quaternion": 4,
    "Plane": 4, "Rect2": 4, "AABB": 6, "Basis": 9, "Transform2D": 6,
    "Transform3D": 12, "Vector2i": 2, "Vector3i": 3, "Vector4i": 4,
}
CTOR = re.compile(r"\b(%s)\(\s*([^()]*?)\s*\)" % "|".join(ARITY))
HEADER = re.compile(r'^\[(ext_resource|sub_resource|node|gd_scene|resource|gd_resource|connection|editable)\b([^\]]*)\]')
ATTR = re.compile(r'(\w+)="([^"]*)"')
REF = re.compile(r'\b(ExtResource|SubResource)\(\s*"([^"]+)"\s*\)')
STRIP_STR = re.compile(r'"(?:[^"\\]|\\.)*"')


def audit_file(path):
    out = []
    rel = os.path.relpath(path, GODOT)
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().split("\n")
    declared = set()
    nodes = set()
    instanced = set()
    used = []
    for ln, line in enumerate(lines, 1):
        s = line.strip()
        if not s or s.startswith(";"):
            continue
        h = HEADER.match(s)
        if h:
            kind, rest = h.group(1), dict(ATTR.findall(h.group(2)))
            if kind in ("ext_resource", "sub_resource"):
                declared.add(rest.get("id", ""))
                if kind == "ext_resource":
                    p = rest.get("path", "")
                    if p.startswith("res://") and not p.endswith(".glb"):
                        fs = os.path.join(GODOT, p[len("res://"):])
                        if not os.path.exists(fs):
                            out.append("MISSING  %s:%d  %s" % (rel, ln, p))
            elif kind == "node":
                name, parent = rest.get("name", ""), rest.get("parent")
                if parent is None:
                    full = "."
                    nodes.add(".")
                    nodes.add(name)
                    full = name
                elif parent == ".":
                    full = name
                else:
                    full = parent + "/" + name
                    first = parent.split("/")[0]
                    if parent not in nodes and first not in instanced:
                        out.append("NOPARENT %s:%d  node %r parent %r not declared above" % (rel, ln, name, parent))
                nodes.add(full)
                if "instance" in rest or "instance=" in h.group(2):
                    instanced.add(full)
            # attributes on the header line may carry refs (instance=ExtResource("x"))
            for kind2, rid in REF.findall(h.group(2)):
                used.append((ln, rid))
            continue
        for kind2, rid in REF.findall(s):
            used.append((ln, rid))
        # constructor arity, strings blanked so a Color inside text is ignored
        bare = STRIP_STR.sub('""', s)
        for m in CTOR.finditer(bare):
            name, args = m.group(1), m.group(2)
            n = 0 if not args.strip() else len([a for a in args.split(",")])
            if n != ARITY[name]:
                out.append("ARITY    %s:%d  %s(...) has %d argument(s), Godot wants %d" % (rel, ln, name, n, ARITY[name]))
    for ln, rid in used:
        if rid not in declared:
            out.append("UNDECL   %s:%d  resource id %r never declared" % (rel, ln, rid))
    return out


def main():
    defects = []
    n_files = 0
    for root in ROOTS:
        for dp, _, fns in os.walk(root):
            if "/.godot" in dp or "/addons" in dp:
                continue
            for fn in sorted(fns):
                if fn.endswith((".tscn", ".tres")):
                    n_files += 1
                    defects += audit_file(os.path.join(dp, fn))
    for d in defects:
        print(d)
    print("tscn_syntax · %d file(s) · %d defect(s)" % (n_files, len(defects)))
    sys.exit(1 if defects else 0)


if __name__ == "__main__":
    main()
