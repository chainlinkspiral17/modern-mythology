#!/usr/bin/env python3
"""Rebuild Pirate Summer's four camper cabins · production pass 2.

The problem (user, 2026-08-03): "scale down the cabin to not be a
giant empty warehouse with a few cots in it and no detail." All four
cabins were 18x10 rooms holding ~120 open floor tiles and 7-11 props,
with fewer bunks than campers assigned to them and bunk_pos values in
campers.json that pointed at open floor.

This rebuilds each cabin to the size its roster actually needs, with
ONE REAL BUNK PER CAMPER, a footlocker at the foot of each, and the
dressing a lived-in cabin has: a cubby of folded things, wet suits on
a line, the one oil lamp, the rug, the window that looks at a named
place, and each cabin's story prop. It then rewrites campers.json so
every bunk_pos lands on that camper's actual bunk tile, and validates
the whole thing.

Run:  python3 godot/tools/sprites/build_ps_cabins.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ZONES = os.path.join(ROOT, "resources", "games", "vol7", "pirate_summer", "zones")
CAMPERS = os.path.join(ROOT, "resources", "games", "vol7", "pirate_summer",
                       "campers.json")

# Shared tile vocabulary. Per-cabin extras merge on top.
BASE_TILES = {
    ".": {"kind": "floor", "color": "#5c4432", "walkable": True},
    "#": {"kind": "wall", "color": "#2a1e14", "walkable": False},
    "B": {"kind": "bunk", "color": "#6a4e30", "walkable": False,
          "label": "a bunk"},
    "F": {"kind": "footlocker", "color": "#6a4e30", "walkable": False,
          "label": "a camp trunk · somebody's name inked on the lid"},
    "C": {"kind": "cubby", "color": "#5a4028", "walkable": False,
          "label": "the cubby · folded towels, a rolled sleeping bag"},
    "L": {"kind": "clothesline", "color": "#6a5a3e", "walkable": False,
          "label": "swimsuits on a line · still damp from this afternoon"},
    "N": {"kind": "oil_lamp", "color": "#e8c060", "walkable": False,
          "label": "the cabin's one lamp · lit after lights-out, briefly"},
    "R": {"kind": "rug", "color": "#8c5c34", "walkable": True},
}


def door(dest_spawn):
    return {"kind": "door", "color": "#8c6a3e", "walkable": True,
            "exit": {"zone": "camp_path", "spawn": dest_spawn},
            "label": "the screen door · out to the path"}


def window(view):
    return {"kind": "window", "color": "#8ea6b0", "walkable": False,
            "label": "the window · " + view}


CABINS = {
    # ── Sam's cabin · six sleepers (Sam + five) ──────────────────
    "cabin_sturgeon": {
        "display_name": "Cabin Sturgeon · interior",
        "rows": [
            "##############",
            "#B..B..B...S.#",
            "#F..F..F...T.#",
            "#...........N#",
            "#...RRRR.....W",
            "#...RRRR.....W",
            "#B..B........#",
            "#F..F...P....#",
            "#C..........L#",
            "######DD######",
        ],
        "extra": {
            "S": {"kind": "sams_bunk", "color": "#7a5a3a", "walkable": False,
                  "label": "Sam's bunk · press space to sleep · advances the day"},
            "T": {"kind": "duffel", "color": "#6a5a3e", "walkable": False,
                  "label": "Sam's duffel bag · a slowstick inside"},
            "P": {"kind": "pickup", "color": "#c8b070", "walkable": False,
                  "label": "a pencil with a good point on the floor by the rug"},
            "W": window("you can see the mess hall porch from here"),
            "D": door("from_sturgeon"),
        },
        "spawns": {"start": [10, 2], "from_camp_path": [6, 8]},
        "bunks": ["bea_hallowell", "wu_kai", "elias_wren",
                  "ford_mears", "xavier_lund"],
    },
    # ── Beaver · four sleepers ───────────────────────────────────
    "cabin_beaver": {
        "display_name": "Cabin Beaver · interior",
        "rows": [
            "#############",
            "#B..B..B..B.#",
            "#F..F..F..F.#",
            "#..........M#",
            "#...RRRR....W",
            "#...RRRR....W",
            "#..........N#",
            "#C.........L#",
            "#...........#",
            "#####DD######",
        ],
        "extra": {
            "M": {"kind": "map", "color": "#c8a842", "walkable": False,
                  "label": "a hand-drawn map of the camp taped to the wall · Tessa's handiwork"},
            "W": window("you can see the archery range from here"),
            "D": door("from_beaver"),
        },
        "spawns": {"start": [6, 6], "from_camp_path": [5, 8]},
        "bunks": ["tessa_ansen", "marisol_cortez", "danny_broz",
                  "reggie_vandermeer"],
    },
    # ── Osprey · three sleepers ──────────────────────────────────
    "cabin_osprey": {
        "display_name": "Cabin Osprey · interior",
        "rows": [
            "############",
            "#B..B..B...#",
            "#F..F..F...#",
            "#.........P#",
            "#..RRRR....W",
            "#..RRRR....W",
            "#.........A#",
            "#C........N#",
            "#L.........#",
            "#####DD#####",
        ],
        "extra": {
            "P": {"kind": "poster", "color": "#6a8ab0", "walkable": False,
                  "label": "a poster of a great blue heron · Sylvie's"},
            "A": {"kind": "cassette", "color": "#8a7a54", "walkable": False,
                  "label": "a stack of cassette tapes · Nika's · one is labeled 'Portland 7/93'"},
            "W": window("you can see the north bluff from here"),
            "D": door("from_osprey"),
        },
        "spawns": {"start": [5, 7], "from_camp_path": [5, 8]},
        "bunks": ["sylvie_nakagawa", "ollie_fisk", "nika_voss"],
    },
    # ── Kestrel · two sleepers · the smallest cabin ──────────────
    "cabin_kestrel": {
        "display_name": "Cabin Kestrel · interior",
        "rows": [
            "###########",
            "#B..B.....#",
            "#F..F.....#",
            "#........K#",
            "#..RRR....W",
            "#..RRR....W",
            "#C.......N#",
            "#L........#",
            "####DD#####",
        ],
        "extra": {
            "K": {"kind": "postcard", "color": "#d8cfae", "walkable": False,
                  "label": "a small cream postcard of Coimbra's library, older than either of Amelie's parents"},
            "W": window("you can see the mess hall porch from here"),
            "D": door("from_kestrel"),
        },
        "spawns": {"start": [5, 6], "from_camp_path": [4, 7]},
        # campers.json order: amelie at the first bunk, priya at the second
        "bunks": ["amelie_rocha", "priya_sundar"],
    },
}


def bunk_positions(rows):
    """Every 'B' tile, reading order — the canonical bunk list."""
    out = []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "B":
                out.append([x, y])
    return out


def build():
    campers_doc = json.load(open(CAMPERS))
    by_id = {c["id"]: c for c in campers_doc["campers"]}
    errors = []

    for zid, spec in CABINS.items():
        rows = spec["rows"]
        w = len(rows[0])
        h = len(rows)
        for i, r in enumerate(rows):
            if len(r) != w:
                errors.append("%s row %d is %d wide, expected %d"
                              % (zid, i, len(r), w))

        tileset = dict(BASE_TILES)
        tileset.update(spec["extra"])

        # every char used must be declared
        used = {ch for row in rows for ch in row}
        for ch in sorted(used):
            if ch not in tileset:
                errors.append("%s uses undeclared tile %r" % (zid, ch))
        for ch in sorted(set(tileset) - used):
            del tileset[ch]   # don't ship dead tileset entries

        # bunks must match the roster exactly
        bunks = bunk_positions(rows)
        roster = spec["bunks"]
        if len(bunks) != len(roster):
            errors.append("%s has %d bunks for %d campers"
                          % (zid, len(bunks), len(roster)))
        for cid, pos in zip(roster, bunks):
            if cid not in by_id:
                errors.append("%s: unknown camper %s" % (zid, cid))
                continue
            by_id[cid]["bunk_pos"] = pos      # the alignment fix

        # spawns must be walkable
        walkable = {ch for ch, d in tileset.items() if d.get("walkable")}
        for name, pos in spec["spawns"].items():
            x, y = pos
            ch = rows[y][x]
            if ch not in walkable:
                errors.append("%s spawn %s at %s is %r (not walkable)"
                              % (zid, name, pos, ch))

        # exactly one exit, at least two door tiles wide
        doors = sum(row.count("D") for row in rows)
        if doors < 2:
            errors.append("%s has %d door tiles (want a 2-wide doorway)"
                          % (zid, doors))

        doc = {
            "id": zid,
            "display_name": spec["display_name"],
            "size": [w, h],
            "tileset": tileset,
            "tiles": rows,
            "spawns": spec["spawns"],
            "npcs": [],   # scheduled placement owns the cabins now
        }
        path = os.path.join(ZONES, zid + ".json")
        with open(path, "w") as fh:
            json.dump(doc, fh, indent=1)
            fh.write("\n")
        open_tiles = sum(row.count(".") + row.count("R") for row in rows)
        props = sum(1 for row in rows for ch in row
                    if ch not in ".#RD")
        print("%-16s %2dx%-2d open=%-3d props=%-2d bunks=%d/%d"
              % (zid, w, h, open_tiles, props, len(bunks), len(roster)))

    with open(CAMPERS, "w") as fh:
        json.dump(campers_doc, fh, indent=1)
        fh.write("\n")

    # final pass · every camper's bunk_pos lands on a bunk tile
    for zid, spec in CABINS.items():
        rows = json.load(open(os.path.join(ZONES, zid + ".json")))["tiles"]
        for cid in spec["bunks"]:
            x, y = by_id[cid]["bunk_pos"]
            if rows[y][x] != "B":
                errors.append("%s: %s bunk_pos %s is %r, not a bunk"
                              % (zid, cid, [x, y], rows[y][x]))

    if errors:
        print("\nFAILED:")
        for e in errors:
            print("  ·", e)
        raise SystemExit(1)
    print("\nall cabins valid · bunk_pos aligned for %d campers"
          % sum(len(s["bunks"]) for s in CABINS.values()))


if __name__ == "__main__":
    build()
