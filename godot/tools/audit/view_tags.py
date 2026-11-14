#!/usr/bin/env python3
"""view_tags.py — which VIEWS a part of a set is in (pass 374, 2026-11-14).

One .tscn serves several views (Background3D.CAMERA_PRESETS), and a part can
belong to some of them only:

  `<Name>__<view>[__<view>…]`   the part is in the views its name tags
  `<Name>__<group>`             … or in every view of a VIEW GROUP
                                (Background3D.VIEW_GROUPS: a short tag that
                                stands for a list of views — a part of three
                                views overran Blender's 63-character names)
  a view's `strip` prefixes     leave that view, tagged or not

Every gate that asks "is this part there?" asks here, so the engine's rule
and the audits' are one rule:

    import view_tags as VT
    VT.owners("Vg_Roy_Torso__st_gva")      -> {"salty_tome_gather", ...} | None (untagged: every view)
    VT.in_view(name, view)                 -> tags, groups and the view's strips
    VT.never_together(n1, n2)              -> no view shows both (so they cannot clip)

    python3 godot/tools/audit/view_tags.py            # the groups, and any tag that names nothing
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GD = os.path.normpath(os.path.join(HERE, "..", "..", "scripts", "vn", "Background3D.gd"))
_STATE = None


def _load():
    global _STATE
    if _STATE is None:
        src = open(GD, encoding="utf-8").read()
        ids, strips, scene = set(), {}, {}
        for m in re.finditer(r'\n\t"(\w+)": \{(.*?)\n\t\},', src, re.S):
            pid, body = m.group(1), m.group(2)
            if '"scene"' not in body:
                continue
            ids.add(pid)
            sm = re.search(r'"scene":\s*"res://scenes/locales/(\w+)\.tscn"', body)
            if sm:
                scene[pid] = sm.group(1)
            st = re.search(r'"strip":\s*\[([^\]]*)\]', body)
            if st:
                strips[pid] = [t.strip().strip('"') for t in st.group(1).split(",") if t.strip()]
        groups = {}
        gm = re.search(r'\nconst VIEW_GROUPS := \{(.*?)\n\}', src, re.S)
        if gm:
            for m in re.finditer(r'"(\w+)":\s*\[([^\]]*)\]', gm.group(1)):
                groups[m.group(1)] = [t.strip().strip('"') for t in m.group(2).split(",") if t.strip()]
        _STATE = (ids, strips, groups, scene)
    return _STATE


def preset_ids():
    return _load()[0]


def groups():
    return _load()[2]


def strips(view):
    return _load()[1].get(view, ())


def scenes():
    """{view id: the set (.tscn name) it shows}"""
    return _load()[3]


def owners(name):
    """The views `name` is tagged for (groups expanded), or None when it
    carries no view tag (it is in every view of its set)."""
    ids, _strips, grp, _scene = _load()
    out = set()
    for part in name.split("__")[1:]:
        if part in ids:
            out.add(part)
        elif part in grp:
            out.update(grp[part])
    return out or None


def in_view(name, view):
    own = owners(name)
    if own is not None and view not in own:
        return False
    return not any(name.startswith(pf) for pf in strips(view))


def never_together(n1, n2):
    """True when no view can show both parts: their tagged views are
    disjoint, or one is tagged and every view it is in strips the other."""
    o1, o2 = owners(n1), owners(n2)
    if o1 is None and o2 is None:
        return False
    if o1 is not None and o2 is not None:
        return not (o1 & o2)
    tagged, other = (o1, n2) if o1 is not None else (o2, n1)
    return all(any(other.startswith(pf) for pf in strips(v)) for v in tagged)


def main():
    ids, _s, grp, _sc = _load()
    bad = 0
    for g, views in sorted(grp.items()):
        miss = [v for v in views if v not in ids]
        if g in ids:
            print("CLASH   group %s is also a view's id" % g)
            bad += 1
        if miss:
            print("UNKNOWN group %s names no such view: %s" % (g, ", ".join(miss)))
            bad += 1
        print("%-14s %s" % (g, " ".join(views)))
    print("\nview_tags · %d view(s) · %d group(s) · %d problem(s)" % (len(ids), len(grp), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
