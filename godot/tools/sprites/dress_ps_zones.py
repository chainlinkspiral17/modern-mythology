#!/usr/bin/env python3
"""Dress the three zones the player sees most · production pass 3.

camp_path is the hub, the mess hall is visited three times a day, the
campfire ring every evening. All three were carrying the same two
problems as the cabins:

  · The mess hall's tables AND benches both mapped to `wood_floor` —
    the room the player eats in rendered as an empty box with
    invisible furniture.
  · The camp path's four cabins and the mess hall were flat blocks of
    one wall tile each: four identical rectangles with no roof, no
    window, no sign. A building you cannot tell from another building
    is not a building.

This gives every structure a roof course, a face with a lit window,
and a name board by its door — and the mess hall real tables, real
benches, and a serving line. Layout, walkability and every exit are
preserved exactly; only non-walkable interior fill changes.

Run: python3 godot/tools/sprites/dress_ps_zones.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ZONES = os.path.join(ROOT, "resources", "games", "vol7", "pirate_summer",
                     "zones")


def load(zid):
    return json.load(open(os.path.join(ZONES, zid + ".json")))


def save(zid, doc):
    with open(os.path.join(ZONES, zid + ".json"), "w") as fh:
        json.dump(doc, fh, indent=1)
        fh.write("\n")


def walkable_set(ts):
    return {ch for ch, d in ts.items() if d.get("walkable")}


def snapshot(doc):
    """(walkable-mask, exit-map) — must be identical after dressing."""
    ts = doc["tileset"]
    walk = walkable_set(ts)
    mask = ["".join("1" if ch in walk else "0" for ch in row)
            for row in doc["tiles"]]
    exits = {}
    for y, row in enumerate(doc["tiles"]):
        for x, ch in enumerate(row):
            ex = ts.get(ch, {}).get("exit")
            if ex:
                exits[(x, y)] = (ex.get("zone"), ex.get("spawn"))
    return mask, exits


# ── camp_path · give the five buildings architecture ─────────────

def dress_camp_path():
    z = load("camp_path")

    # ── Layout repair, BEFORE the dressing snapshot ──────────────
    # Cabin Beaver was UNREACHABLE. Its door tile sat only on the
    # structure's upper row, with a tree above it and solid wall
    # below — so no walkable tile touched it and Tessa's cabin could
    # never be entered. Sturgeon and Osprey have a two-tall door
    # column reaching down to the path; Beaver gets the same, which
    # is also what makes the roof/wall composition legible.
    rows0 = [list(r) for r in z["tiles"]]
    if rows0[13][18] == "V" and rows0[13 - 1][18] not in (".", ","):
        rows0[14][18] = "v"
        z["tiles"] = ["".join(r) for r in rows0]

    before = snapshot(z)
    rows = [list(r) for r in z["tiles"]]
    ts = z["tileset"]

    # Each structure: the fill char, its door char, and its name.
    STRUCTS = [
        ("C", "s", "Cabin Sturgeon · your cabin"),
        ("V", "v", "Cabin Beaver · Tessa's cabin"),
        ("O", "o", "Cabin Osprey · Sylvie and Nika's cabin"),
        ("K", "k", "Cabin Kestrel · Amelie and Priya's cabin"),
        ("M", "m", "the mess hall"),
    ]
    # y=roof slope · Y=ridge course · w=window wall · W=plain front
    # wall · g=name board · Q=doorway recess under the roof
    ROOF, RIDGE, FACE, FRONT, SIGN = "y", "Y", "w", "W", "g"
    # One recess char PER STRUCTURE. A single shared one would have
    # given all four cabins Sturgeon's exit — the walkability/exit
    # snapshot assert caught it, which is exactly what it is for.
    RECESS_CHARS = ["Q", "Z", "X", "J", "q"]

    ts[RIDGE] = {"kind": "cabin_roof_ridge", "color": "#5a4836",
                 "walkable": False,
                 "label": "the ridge · cedar shingles, mossy on the north slope"}
    ts[ROOF] = {"kind": "cabin_roof", "color": "#4a3a2c", "walkable": False,
                "label": "cedar shingles, and the eave over the door"}
    ts[FACE] = {"kind": "cabin_face", "color": "#5c4a34", "walkable": False,
                "label": "a lit window"}
    ts[FRONT] = {"kind": "cabin_front", "color": "#4a3826", "walkable": False,
                 "label": "board-and-batten, under the eave"}
    ts[SIGN] = {"kind": "cabin_sign", "color": "#8a7048", "walkable": False,
                "label": "the cabin's name board · repainted every June"}

    for s_i, (fill_ch, door_ch, name) in enumerate(STRUCTS):
        occupied = sorted(y for y, r in enumerate(rows) if fill_ch in r)
        if not occupied:
            continue
        # THE FACE IS THE ROW NEAREST THE APPROACH — always the
        # structure's LOWEST row. Roof above, wall below, door and
        # windows only ever in the wall. Taking the FIRST door row
        # instead put the openings in the upper band and the shingles
        # under them: "doors and windows placed in roofs."
        face_row = occupied[-1]
        roof_rows = [y for y in occupied if y != face_row]
        for y in occupied:
            xs = [x for x, ch in enumerate(rows[y]) if ch == fill_ch]
            if y == face_row:
                door_x = rows[y].index(door_ch) if door_ch in rows[y] else None
                for x in xs:
                    if door_x is None:
                        rows[y][x] = FACE if x % 2 == 0 else FRONT
                    else:
                        dist = abs(x - door_x)
                        rows[y][x] = FACE if (dist >= 2 and dist % 2 == 0) \
                            else FRONT
                if door_x is not None:
                    for cand in (door_x - 1, door_x + 1):
                        if cand in xs:
                            rows[y][cand] = SIGN
                            break
            else:
                # roof: the topmost course is the ridge, the rest slope
                band = RIDGE if y == roof_rows[0] else ROOF
                for x in xs:
                    rows[y][x] = band
        # A door tile sitting in a ROOF row is the threshold seen
        # under the eave — the recess behind the door, not a hole in
        # the shingles. Same walkability, same exit, its own art.
        door_def = ts.get(door_ch)
        recess_ch = RECESS_CHARS[s_i]
        if door_def is not None:
            for y in roof_rows:
                if door_ch not in rows[y]:
                    continue
                if recess_ch not in ts:
                    rec = dict(door_def)
                    rec["kind"] = "cabin_doorway"
                    rec["label"] = "the doorway · dark past the screen"
                    ts[recess_ch] = rec
                for x, ch in enumerate(rows[y]):
                    if ch == door_ch:
                        rows[y][x] = recess_ch
        ts[fill_ch]["label"] = name

    z["tiles"] = ["".join(r) for r in rows]
    # drop tileset entries no structure uses any more
    live = {ch for r in rows for ch in r}
    for ch in [c for c in ts if c not in live]:
        del ts[ch]
    after = snapshot(z)
    assert before[0] == after[0], "camp_path walkability changed"
    assert before[1] == after[1], "camp_path exits changed"
    save("camp_path", z)
    print("camp_path   · 5 structures given roof / lit face / name board")


# ── mess_hall · furniture that is visible, and a serving line ────

def dress_mess_hall():
    z = load("mess_hall")
    before = snapshot(z)
    ts = z["tileset"]
    # T and b were both rendering as the floor. Give them their own
    # kinds; keep walkability exactly as it was (benches walkable so
    # you can sit; tables not).
    ts["T"]["kind"] = "table_long"
    ts["T"]["label"] = "a long wooden table · forty summers of initials"
    ts["b"]["kind"] = "bench_wood"
    ts["b"]["label"] = "a bench along the table · press space to sit and eat"
    # The serving line, on the open floor beside the kitchen.
    ts["S"] = {"kind": "serving_counter", "color": "#9aa2a6",
               "walkable": False,
               "label": "the serving line · trays at the near end, "
                        "Bear's soup at the far"}
    ts["u"] = {"kind": "oil_lamp", "color": "#e8c060", "walkable": False,
               "label": "a hanging lamp over the long tables"}
    rows = [list(r) for r in z["tiles"]]
    # kitchen block is rows 9-11, x 3-8 · put the line on its lip
    for x in range(3, 9):
        if rows[9][x] == "K":
            continue
    for x in range(3, 9):
        if rows[8][x] == ".":
            rows[8][x] = "S"
    # two hanging lamps over the table bays
    for (lx, ly) in ((7, 5), (14, 5)):
        if rows[ly][lx] == ".":
            rows[ly][lx] = "u"
    z["tiles"] = ["".join(r) for r in rows]
    after = snapshot(z)
    assert before[1] == after[1], "mess_hall exits changed"
    save("mess_hall", z)
    print("mess_hall   · tables + benches now render; serving line + lamps")


# ── campfire_ring · the things a used firepit accumulates ────────

def dress_campfire_ring():
    z = load("campfire_ring")
    before = snapshot(z)
    ts = z["tileset"]
    ts["W"] = {"kind": "woodpile", "color": "#7a6244", "walkable": False,
               "label": "split rounds under a tarp · Bear splits them Sundays"}
    ts["u"] = {"kind": "stump", "color": "#8a7050", "walkable": False,
               "label": "a cut stump · the counselor's chair, by custom"}
    ts["l"] = {"kind": "oil_lamp", "color": "#e8c060", "walkable": False,
               "label": "a lantern on a shepherd's hook · lit before dusk"}
    rows = [list(r) for r in z["tiles"]]
    placements = [
        (3, 4, "W"), (3, 5, "W"),      # the woodpile, west, under the trees
        (19, 7, "u"),                  # the counselor's stump, east of the ring
        (5, 10, "l"), (18, 4, "l"),    # two lanterns on the approach
    ]
    for x, y, ch in placements:
        if rows[y][x] == ".":
            rows[y][x] = ch
    z["tiles"] = ["".join(r) for r in rows]
    after = snapshot(z)
    assert before[1] == after[1], "campfire_ring exits changed"
    save("campfire_ring", z)
    print("campfire_ring · woodpile, counselor's stump, two lanterns")


if __name__ == "__main__":
    dress_camp_path()
    dress_mess_hall()
    dress_campfire_ring()
