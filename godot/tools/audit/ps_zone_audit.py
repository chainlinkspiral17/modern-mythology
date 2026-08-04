#!/usr/bin/env python3
"""Pirate Summer zone integrity audit.

Catches the bug classes the 2026-08 production passes turned up, so
they can't come back silently:

  1. EXITS WITH NO ART — a walkable exit whose tile kind has no entry
     in CampOverworld._TILE_SPRITE_FOR_KIND renders as a flat
     ColorRect. This is what "can't leave the cabin" actually was.
  2. Dangling exits — an exit naming a zone that doesn't exist, or a
     spawn key the destination zone doesn't declare.
  3. Unwalkable spawns — a spawn point sitting on a wall or a prop.
  4. Stranded NPCs — a scheduled bunk_pos / seat / activity position
     that isn't the tile kind it claims to be, or is out of bounds.
  5. Ragged grids — a row whose length disagrees with size[0].
  6. Undeclared tiles — a character in tiles[] with no tileset entry.
  7. Invisible props — a SOLID tile drawn with the same sprite as
     the ground it stands on. This is how the mess hall's three
     long tables and their benches rendered as floor: 'table' and
     'bench' both pointed at wood_floor.

Exit code is nonzero if anything is found. Run before committing zone
or camper JSON:

    python3 godot/tools/audit/ps_zone_audit.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PS = os.path.join(ROOT, "resources", "games", "vol7", "pirate_summer")
ZONES = os.path.join(PS, "zones")
OVERWORLD = os.path.join(ROOT, "scenes", "games", "pirate_summer",
                         "CampOverworld.gd")
TILE_DIR = os.path.join(PS, "sprites", "tiles")

# Distant scenery drawn as multi-tile silhouettes in flat color. These
# are deliberate — a 16x16 sprite would break the shape they spell.
SILHOUETTE_KINDS = {
    "heron", "captain", "fed_boat", "old_man", "old_man_end",
    "watched_island",
}


def load_mapped_kinds():
    src = open(OVERWORLD).read()
    m = re.search(r"_TILE_SPRITE_FOR_KIND := \{(.*?)\n\}", src, re.S)
    if not m:
        return None, None, None
    pairs = re.findall(r'"([a-z_0-9]+)":\s*"([a-z_0-9]+)"', m.group(1))
    return {k for k, _ in pairs}, {v for _, v in pairs}, dict(pairs)


def main():
    mapped, targets, sprite_of = load_mapped_kinds()
    problems = []
    if mapped is None:
        print("could not parse _TILE_SPRITE_FOR_KIND")
        return 1

    have_sprites = {f[:-5] for f in os.listdir(TILE_DIR) if f.endswith(".json")}
    for t in sorted(targets - have_sprites):
        problems.append("sprite map points at missing tile art: %s.json" % t)

    zones = {}
    for f in sorted(os.listdir(ZONES)):
        if f.endswith(".json"):
            zones[f[:-5]] = json.load(open(os.path.join(ZONES, f)))

    campers = json.load(open(os.path.join(PS, "campers.json")))["campers"]

    for zid, z in zones.items():
        rows = z.get("tiles", [])
        ts = z.get("tileset", {})
        size = z.get("size", [0, 0])
        w, h = int(size[0]), int(size[1])

        if len(rows) != h:
            problems.append("%s: %d rows, size says %d" % (zid, len(rows), h))
        for i, r in enumerate(rows):
            if len(r) != w:
                problems.append("%s: row %d is %d wide, size says %d"
                                % (zid, i, len(r), w))

        used = {ch for r in rows for ch in r}
        for ch in sorted(used):
            if ch not in ts:
                problems.append("%s: tile %r used but not declared" % (zid, ch))

        walkable = {ch for ch, d in ts.items() if d.get("walkable")}

        for ch, d in ts.items():
            if ch not in used:
                continue
            kind = d.get("kind", "")
            ex = d.get("exit")
            if ex:
                dest = ex.get("zone", "")
                spawn = ex.get("spawn", "")
                if dest not in zones:
                    problems.append("%s: exit %r -> unknown zone %r"
                                    % (zid, ch, dest))
                elif spawn not in zones[dest].get("spawns", {}):
                    problems.append("%s: exit %r -> %s has no spawn %r"
                                    % (zid, ch, dest, spawn))
                if not d.get("walkable"):
                    problems.append("%s: exit %r is not walkable" % (zid, ch))
                if kind not in mapped:
                    problems.append("%s: EXIT %r (kind %s) has no tile art — "
                                    "renders as a flat rect" % (zid, ch, kind))
            elif kind not in mapped and kind not in SILHOUETTE_KINDS:
                problems.append("%s: tile %r (kind %s) has no tile art"
                                % (zid, ch, kind))

        # A solid prop drawn with the same sprite as the ground it
        # stands on is invisible. This is how the mess hall's three
        # long tables and their benches rendered as floor for months:
        # "table" and "bench" both pointed at wood_floor.
        base_kind = ""
        for ch in (".", ","):
            if ch in ts and ts[ch].get("walkable"):
                base_kind = ts[ch].get("kind", "")
                break
        base_sprite = sprite_of.get(base_kind, "")
        if base_sprite:
            for ch, d in ts.items():
                if ch not in used or d.get("walkable"):
                    continue
                k = d.get("kind", "")
                if k in SILHOUETTE_KINDS:
                    continue
                if sprite_of.get(k, "") == base_sprite:
                    problems.append("%s: solid tile %r (kind %s) draws with "
                                    "the ground sprite %r — invisible"
                                    % (zid, ch, k, base_sprite))

        for name, pos in z.get("spawns", {}).items():
            if len(pos) < 2:
                problems.append("%s: spawn %s malformed" % (zid, name))
                continue
            x, y = int(pos[0]), int(pos[1])
            if not (0 <= y < len(rows) and 0 <= x < len(rows[y])):
                problems.append("%s: spawn %s at %s is out of bounds"
                                % (zid, name, pos))
            elif rows[y][x] not in walkable:
                problems.append("%s: spawn %s at %s sits on %r (not walkable)"
                                % (zid, name, pos, rows[y][x]))

        for n in z.get("npcs", []):
            pos = n.get("pos", [])
            if len(pos) < 2:
                continue
            x, y = int(pos[0]), int(pos[1])
            if not (0 <= y < len(rows) and 0 <= x < len(rows[y])):
                problems.append("%s: static npc %s out of bounds at %s"
                                % (zid, n.get("camper"), pos))

    # scheduled positions · bunks, seats, activities, free time
    for c in campers:
        cid = c.get("id", "?")
        cabin = c.get("cabin", "")
        bunk = c.get("bunk_pos")
        if cabin and bunk:
            zid = "cabin_" + cabin
            z = zones.get(zid)
            if z is None:
                problems.append("%s: cabin %s has no zone" % (cid, cabin))
            else:
                rows = z["tiles"]
                x, y = int(bunk[0]), int(bunk[1])
                if not (0 <= y < len(rows) and 0 <= x < len(rows[y])):
                    problems.append("%s: bunk_pos %s out of bounds in %s"
                                    % (cid, bunk, zid))
                else:
                    ch = rows[y][x]
                    kind = z["tileset"].get(ch, {}).get("kind", "")
                    if kind not in ("bunk", "sams_bunk"):
                        problems.append("%s: bunk_pos %s in %s is %r (kind %s)"
                                        " — not a bunk"
                                        % (cid, bunk, zid, ch, kind))
        sched = c.get("schedule", {})
        checks = []
        seat = sched.get("mess_hall_seat")
        if seat:
            checks.append(("mess_hall", seat, "mess_hall_seat"))
        ftz = sched.get("free_time_zone")
        ftp = sched.get("free_time_pos")
        if ftz and ftp:
            checks.append((ftz, ftp, "free_time_pos"))
        cfr = sched.get("campfire_ring_position")
        if cfr:
            checks.append(("campfire_ring", cfr, "campfire_ring_position"))
        cpp = sched.get("camp_path_position")
        if cpp:
            checks.append(("camp_path", cpp, "camp_path_position"))
        for zname, pos in (sched.get("activity_positions", {}) or {}).items():
            checks.append((zname, pos, "activity_positions[%s]" % zname))
        for zname, pos, label in checks:
            z = zones.get(zname)
            if z is None:
                problems.append("%s: %s names unknown zone %s"
                                % (cid, label, zname))
                continue
            if len(pos) < 2:
                continue
            rows = z["tiles"]
            x, y = int(pos[0]), int(pos[1])
            if not (0 <= y < len(rows) and 0 <= x < len(rows[y])):
                problems.append("%s: %s %s out of bounds in %s"
                                % (cid, label, pos, zname))

    if problems:
        print("ps_zone_audit: %d problem(s)\n" % len(problems))
        for p in problems:
            print("  ·", p)
        return 1
    print("ps_zone_audit: 0 problems · %d zones · %d campers"
          % (len(zones), len(campers)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
