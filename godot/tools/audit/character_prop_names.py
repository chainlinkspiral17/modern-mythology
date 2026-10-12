#!/usr/bin/env python3
"""Props named for a character — a report, not a gate (2026-10-12).

The marker-aim audit resolves `shot_closeup_<name>` to geometry whose
name carries <name>; a phone, a notebook, a truck or a cup named for a
character therefore ANSWERS that character's closeup cue, and the frame
is judged against the prop instead of the person (passes 81, 86, 87:
Bens_Truck, Hands_Print_Marit, Sams_Phone, Rick_Shelf, Ricks_Notebook —
one per pass, found by the gate after the marker was placed).

Run this BEFORE adding a named closeup to a locale, for that locale:

    python3 godot/tools/audit/character_prop_names.py hans_bakery_back_kitchen
    python3 godot/tools/audit/character_prop_names.py            # every builder

Names that are the character's own place (Roys_Chair, Gracie_Chair,
Bianca_Desk) are fine as long as the frame shows that piece; names on
small things away from the person (phones, cups, trucks, photos) are the
ones to rename by what/where (Island_Phone, Toyota_Truck, Desk_Notebook).
"""
import glob
import os
import re
import sys
from collections import defaultdict

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
SCENES = os.path.join(REPO, "godot", "resources", "scenes")
BUILDERS = [os.path.join(REPO, "godot", "tools", "blender", "locales"),
            os.path.join(REPO, "godot", "tools", "blender", "_props")]
# words that are cues but not people (a sign's figure, a dollar bill)
NOT_PEOPLE = {"figure", "figures", "bill", "bills", "child", "frog", "reporter", "man", "woman", "person"}


def cue_names():
    cues = set()
    for f in glob.glob(os.path.join(SCENES, "vol*", "*.json")):
        with open(f) as fh:
            for m in re.finditer(r"\[shot:closeup ([a-z_]+)\]", fh.read()):
                cues.add(m.group(1))
    cues -= {"person", "person_b"} | NOT_PEOPLE
    names = set()
    for c in cues:
        names.update({c, c.rstrip("s"), c + "s"})
    return {n for n in names if len(n) >= 3}


def scan(only=None):
    names = cue_names()
    hits = defaultdict(set)
    for d in BUILDERS:
        for f in glob.glob(os.path.join(d, "*.py")):
            stem = os.path.basename(f)[:-3]
            if only and only not in stem:
                continue
            with open(f) as fh:
                src = fh.read()
            for m in re.finditer(r'make_\w+\(\s*f?"([A-Za-z0-9_{}]+)"', src):
                nm = m.group(1)
                parts = [p.lower() for p in re.sub(r"\{[^}]*\}", "", nm).split("_") if p]
                for p in parts:
                    if p in names:
                        hits[stem].add((nm, p))
                        break
    return hits


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    hits = scan(only)
    total = 0
    for stem in sorted(hits):
        print("== %s" % stem)
        for nm, who in sorted(hits[stem]):
            print("   %-40s ← %s" % (nm, who))
            total += 1
    print("%d prop name(s) carry a character's name across %d builder(s)" % (total, len(hits)))


if __name__ == "__main__":
    main()
