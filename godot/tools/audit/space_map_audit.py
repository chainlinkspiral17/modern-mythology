#!/usr/bin/env python3
"""space_map_audit.py — the gauntlet's three copies of every board
(2026-09-11).

A gauntlet space lives in three places and nothing checked that they
agreed:

  1. `resources/games/locations/<id>.json` — the board: which spaces
     exist, which are liminal. The scenario reads this.
  2. `scripts/<Place>GauntletHost.gd` SPACE_MAP — world positions,
     used whenever the host scene is loaded.
  3. `TarotGauntletGame.gd _STANDALONE_SPACE_VANTAGES` — a hand-copied
     mirror of (2), used when the board runs with no host. Its own
     comment says "when you update a host's SPACE_MAP, copy the change
     here too", which is exactly the kind of instruction that rots.

It had rotted: the Magician's last five arcana stations (star, moon,
sun, judgement, world) never reached the mirror, so a standalone
Magician board had no vantage for them; D'Ambrosio's booth_1 and
booth_6 were swapped against build_diner.py's south→north numbering,
walking the player to the wrong end of the alcove row; the hostess
stand kept a pre-playtest position; and precipice_door — a THRESHOLD
liminal station — was missing entirely.

Hosts are paired to locations by key overlap, not by name (the diner's
host is DinerGauntletHost but its location id is "dambrosios").
Symbolic floor constants in a host (LOWER_FLOOR_Z…) are resolved from
that host before comparing.

    python3 godot/tools/audit/space_map_audit.py
    python3 godot/tools/audit/space_map_audit.py --all   # pairings too

A suite gate at zero.
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GODOT = os.path.join(ROOT, "godot")
HOSTS = os.path.join(GODOT, "scripts")
GAUNTLET = os.path.join(GODOT, "scenes", "games", "TarotGauntletGame.gd")
LOCATIONS = os.path.join(GODOT, "resources", "games", "locations")

# Locations whose host SPACE_MAP describes a DIFFERENT board from the one
# the JSON and the mirror share. The game tries the host first and falls
# back to the mirror, so these run on the mirror; the host's table is a
# leftover from an earlier staging of the same place. Read 2026-09-11 —
# not drift to fix here, and changing a host's map would move whatever
# still uses it.
KNOWN_DIVERGENT = {
    "ember_ash_office",        # host: the finished office · JSON: the renovation
    "roberts_house",           # host: the 2026-05 walk · JSON: the loom/tapestry/garden walk
    "the_hierophant_circuit",  # host: the bandstand + church plaza · JSON: the circuit
}


def brace_block(src, start):
    """The {...} body beginning at or after `start`."""
    i = src.index("{", start)
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return src[i + 1:j]
    return None


def entries(body, consts=None):
    """'"id": [a, b, c]' pairs → {id: [floats]}, resolving named consts."""
    out = {}
    for m in re.finditer(r'"([\w]+)"\s*:\s*\[([^\]]*)\]', body):
        vals = []
        for v in m.group(2).split(","):
            v = re.sub(r"#.*", "", v).strip()
            if not v:
                continue
            if consts and v in consts:
                vals.append(round(consts[v], 3))
                continue
            try:
                vals.append(round(float(v), 3))
            except ValueError:
                vals.append(v)
        out[m.group(1)] = vals
    return out


def host_maps():
    out = {}
    for f in sorted(glob.glob(os.path.join(HOSTS, "*GauntletHost.gd"))):
        src = open(f).read()
        m = re.search(r"const SPACE_MAP\s*:?=", src)
        if not m:
            continue
        consts = {c: float(v) for c, v in
                  re.findall(r"const (\w+)\s*:\s*float\s*=\s*([-0-9.]+)", src)}
        body = brace_block(src, m.start())
        if body:
            out[os.path.basename(f)[:-3]] = entries(body, consts)
    return out


def mirror_maps():
    src = open(GAUNTLET).read()
    m = re.search(r"\nconst _STANDALONE_SPACE_VANTAGES\s*:?=", src)
    body = brace_block(src, m.start())
    out = {}
    for mm in re.finditer(r'\n\t"(\w+)":\s*\{', body):
        inner = brace_block(body, mm.end() - 1)
        if inner:
            out[mm.group(1)] = entries(inner)
    return out


def json_spaces():
    out = {}
    for f in sorted(glob.glob(os.path.join(LOCATIONS, "*.json"))):
        try:
            j = json.load(open(f))
        except Exception:
            continue
        ids = {s.get("id") for s in j.get("spaces", []) if s.get("id")}
        out[os.path.basename(f)[:-5]] = ids
    return out


def pair(mirror, hosts):
    """Location → host, by key overlap, best match first."""
    cands = []
    for loc, me in mirror.items():
        for h, he in hosts.items():
            inter = len(set(me) & set(he))
            union = len(set(me) | set(he)) or 1
            cands.append((inter / union, loc, h))
    cands.sort(reverse=True)
    got, free_l, free_h = {}, set(mirror), set(hosts)
    for s, loc, h in cands:
        if loc in free_l and h in free_h:
            got[loc] = (h, s)
            free_l.discard(loc)
            free_h.discard(h)
    return got, sorted(free_l), sorted(free_h)


def main():
    show_all = "--all" in sys.argv
    mirror, hosts, jsons = mirror_maps(), host_maps(), json_spaces()
    paired, loose_loc, loose_host = pair(mirror, hosts)
    problems = 0
    for loc in sorted(paired):
        h, score = paired[loc]
        me, he = mirror[loc], hosts[h]
        js = jsons.get(loc, set())
        if loc in KNOWN_DIVERGENT:
            if show_all:
                print("ok(known) %-24s %-30s host serves another board" % (loc, h))
            # the mirror still has to cover the board the JSON describes
            gaps = sorted(js - set(me))
            if gaps:
                problems += len(gaps)
                print("SPACE   %-24s standalone has no vantage for: %s"
                      % (loc, ", ".join(gaps)))
            continue
        only_h = sorted(set(he) - set(me))
        only_m = sorted(set(me) - set(he))
        diff = sorted(k for k in set(me) & set(he) if me[k] != he[k])
        gaps = sorted(js - set(me)) if js else []
        n = len(only_h) + len(only_m) + len(diff) + len(gaps)
        problems += n
        if not n:
            if show_all:
                print("ok        %-24s %-30s %3.0f%%" % (loc, h, score * 100))
            continue
        print("== %-24s %-30s %.0f%% match" % (loc, h, score * 100))
        for k in only_h:
            print("   SPACE   host has %-22s the standalone mirror does not" % k)
        for k in only_m:
            print("   SPACE   mirror has %-20s the host does not" % k)
        for k in diff:
            print("   SPACE   %-22s host %s | mirror %s" % (k, he[k], me[k]))
        for k in gaps:
            print("   SPACE   %-22s is in the location JSON but neither table" % k)
    for loc in loose_loc:
        problems += 1
        print("SPACE   %-24s mirrors no host SPACE_MAP" % loc)
    for h in loose_host:
        problems += 1
        print("SPACE   %-24s has a SPACE_MAP no location mirrors" % h)
    print("\nspace_map_audit · %d location(s) checked · %d disagreement(s)"
          % (len(paired), problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
