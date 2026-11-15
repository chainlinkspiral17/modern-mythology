#!/usr/bin/env python3
"""rig_twin_audit.py — a view of a set that lost the set's light rig
(2026-11-15, pass 399).

A light in a locale .tscn named `<Name>__<view>[__<view>…]` (or a VIEW_GROUPS
group) is kept only in the views it names; Background3D strips it from every
other view of that scene (_strip_other_preset_lights). When a pass copies a
view to carry chapter state — pass 397's `finn_apartment_stick` and
`finn_apartment_night_stick`, made from `finn_apartment` and
`finn_apartment_night` so ch18's table could have the stick on it — the copy
is a new view id, and every light tagged to the original was stripped from
it: Finn's ch18 afternoon and night ran with no key, fill, back or moon.
Pass 168's two vol 3 ch8 Chau house views (Steven's desk, Mrs. Chau's room)
kept no light at all: the house's rig named the six views before them.

A view is UNLIT when it keeps no light at all while a sibling view of the
same scene keeps one, or when it keeps no DirectionalLight3D while its TWIN —
a sibling with the same camera_origin, the view it was copied from — keeps a
tagged DirectionalLight3D of its own. (A view at its own camera with only
its practicals — a dark room, a set lit by a television — is a choice.) Fix
it by naming the twin in the light's tag, or with a VIEW_GROUPS group the
twins share.

    python3 godot/tools/audit/rig_twin_audit.py
Gate: zero.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GODOT = os.path.normpath(os.path.join(HERE, "..", ".."))
B3D = os.path.join(GODOT, "scripts", "vn", "Background3D.gd")
LIGHT = re.compile(r'\[node name="([^"]+)" type="(DirectionalLight3D|OmniLight3D|SpotLight3D)"')


def presets_and_groups():
    src = open(B3D, encoding="utf-8").read()
    pres, cams = {}, {}
    for m in re.finditer(r'^\t"([a-z0-9_]+)": \{\n(.*?)^\t\},', src, re.M | re.S):
        s = re.search(r'"scene": "res://([^"]+)"', m.group(2))
        if s:
            pres[m.group(1)] = s.group(1)
            c = re.search(r'"camera_origin": Vector3\(([^)]*)\)', m.group(2))
            cams[m.group(1)] = tuple(round(float(x), 2) for x in c.group(1).split(",")) if c else None
    groups = {}
    g = re.search(r'\nconst VIEW_GROUPS := \{(.*?)\n\}', src, re.S)
    if g:
        for m in re.finditer(r'"([a-z0-9_]+)": \[([^\]]*)\]', g.group(1)):
            groups[m.group(1)] = re.findall(r'"([a-z0-9_]+)"', m.group(2))
    return pres, groups, cams


def main():
    pres, groups, cams = presets_and_groups()
    byscene = {}
    for p, s in pres.items():
        byscene.setdefault(s, []).append(p)

    def owners(name):
        out = []
        for part in name.split("__")[1:]:
            if part in pres:
                out.append(part)
            elif part in groups:
                out += groups[part]
        return out

    bad, read = 0, 0
    for scene, views in sorted(byscene.items()):
        path = os.path.join(GODOT, scene)
        if len(views) < 2 or not os.path.exists(path):
            continue
        lights = LIGHT.findall(open(path, encoding="utf-8").read())
        if not any(owners(n) for n, _t in lights):
            continue
        read += 1
        keep = {v: [(n, t) for n, t in lights if not owners(n) or v in owners(n)] for v in views}
        own_dir = {v: any(t == "DirectionalLight3D" and owners(n) for n, t in keep[v]) for v in views}
        for v in sorted(views):
            dirs = sum(1 for _n, t in keep[v] if t == "DirectionalLight3D")
            sib_dir = [q for q in views if q != v and own_dir[q] and cams.get(q) is not None and cams.get(q) == cams.get(v)]
            sib_any = [q for q in views if q != v and keep[q]]
            if (dirs == 0 and sib_dir) or (not keep[v] and sib_any):
                bad += 1
                print("UNLIT  %-34s %-30s keeps %d light(s), no directional; %s keep a rig of their own"
                      % (os.path.basename(scene), v, len(keep[v]), ", ".join(sorted(sib_dir or sib_any)[:4])))
    print("rig_twin_audit · %d set(s) with view-tagged lights · %d view(s) that lost the set's rig" % (read, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
