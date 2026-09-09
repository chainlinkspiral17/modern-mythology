#!/usr/bin/env python3
"""assign_chapter_beds.py — which bed plays in which chapter (2026-09-11).

GameEngine._apply_chapter_music_context() collects every catalog entry
whose `chapters` list names the scene and hands them to
AudioMgr.set_chapter(). When that list comes back EMPTY, AudioMgr falls
through to "the unlocked playlist" — whatever the player has heard —
so the chapter is scored by accident.

234 of 312 scenes had no entry naming them: all of vol6 (107) and vol7
(89) except a dozen, the whole Louisiana arcana run (ch6-ch21), and the
vol1 link hub. They played vol5's four beds wherever they were.

THE RULE, two tiers, and it is the same rule the assigned scenes were
already following:

  1. PLACE. A scene whose backgrounds are mostly one locale gets that
     locale's bed — the Kwik Stop's fluorescents in the Kwik Stop,
     Per's signal bell in Per's shop, the woodstove in the cabin. The
     locale→bed tables below are authored, not learned: a scene visits
     several places and learning from the existing assignments smeared
     Kestrel's wind over the accretion basement.
  2. VOLUME FLOOR. Everything else gets `vol<N>_ambient`, which is what
     that entry has always been for (vol1 = the diner at the
     crossroads, vol6 = Harmony Creek Estates, vol7 = Smolvud).

A place is allowed to cross volumes when it is the SAME PLACE: the
Foxhole is the Foxhole in vol1 and vol6, the cathedral is the cathedral
in vol5 and vol7's interlude.

Only beds with a file on disk are assigned — an entry pointing at
nothing is the failure this whole pass exists to fix.

    python3 godot/tools/audio/assign_chapter_beds.py --dry
    python3 godot/tools/audio/assign_chapter_beds.py

Idempotent: a scene already named by any entry is left alone.
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GODOT = os.path.join(ROOT, "godot")
CATALOG = os.path.join(GODOT, "resources", "music_catalog.json")
SCENES = os.path.join(GODOT, "resources", "scenes")

# ── locale → bed, per volume ───────────────────────────────────────
PLACES = {
    1: {
        "missing_link_interior": "vol1_diner_ambient",
        "missing_link_exterior": "vol1_diner_ambient",
        "shuttle_bench": "vol1_diner_ambient",
        "faust_bedroom": "vol1_dream_drone",
        "faust_apartment_day": "vol1_painting",
        "new_orleans_bar": "vol1_club_thump",
        "foxhole_bar": "vol1_club_thump",
        "foxhole_stage": "vol1_club_thump",
        "foxhole_dressing_room": "vol1_club_thump",
        "pharmacy_floor": "vol1_pharmacy",
        "pharmacy_office": "vol1_pharmacy",
        "small_wood_road_night": "vol1_drive_night",
        "bar_exterior_night": "vol1_drive_night",
    },
    2: {
        "briar_falls_rest_stop": "vol2_rest_stop_wind",
        "briar_falls_overlook": "vol2_rest_stop_wind",
        "briar_falls_picnic": "vol2_rest_stop_wind",
        "briar_falls_trail": "vol2_rest_stop_wind",
        "briar_falls_building": "vol2_rest_stop_wind",
        "cliffside_circus": "vol2_seagash_drone",
        "sapo_falls": "vol2_seagash_drone",
        "grunion_beach": "vol2_seagash_drone",
        "beach_night": "vol2_seagash_drone",
        "centro_dock": "vol2_seagash_drone",
        "parish_cemetery": "vol2_graveyard_solo",
    },
    5: {
        "cathedral_interior": "vol5_cathedral_drone",
        "diner_interior": "vol5_diner_roomtone",
        "dambrosios_formal": "vol5_diner_roomtone",
        "cafe_olimpico": "vol5_cafe_ambient",
        "montreal_apartment": "vol5_cafe_ambient",
        "new_orleans_bar": "vol5_venue_ambient",
        "new_orleans_room": "vol5_venue_ambient",
        "riverboat_interior": "vol5_venue_ambient",
        "le_roulant_casino": "vol5_venue_ambient",
        "centro_grocery_aisle": "vol5_store_ambient",
        "pharmacy_floor": "vol5_store_ambient",
        "christian_ice_co": "vol5_store_ambient",
        "natalie_apartment": "vol5_domestic_roomtone",
        "new_orleans_apartment": "vol5_domestic_roomtone",
        "elicia_apartment": "vol5_domestic_roomtone",
        "roberts_kitchen": "vol5_domestic_roomtone",
        "graustark_cottage": "vol5_domestic_roomtone",
        "bungalow_interior": "vol5_domestic_roomtone",
        "hospice_room": "vol5_domestic_roomtone",
        "safehouse_bedroom": "vol5_domestic_roomtone",
        "graustark_chalk_wall": "vol5_cicadas_dusk",
        "graustark_wreck": "vol5_cicadas_dusk",
        "graustark_ruins": "vol5_cicadas_dusk",
        "riverfront_park": "vol5_cicadas_dusk",
        "chapel_exterior": "vol5_cicadas_dusk",
        "riverfront_exterior": "vol5_cicadas_dusk",
        "new_orleans_office": "vol5_cicadas_dusk",
    },
    6: {
        "kwik_stop_interior": "vol6_kwik_stop_interior",
        "centro_grocery_aisle": "vol6_kwik_stop_interior",
        "centro_break_room": "vol6_kwik_stop_interior",
        "centro_stockroom": "vol6_kwik_stop_interior",
        "pit_stop_interior": "vol6_kwik_stop_interior",
        "pit_stop_kitchen": "vol6_kwik_stop_interior",
        "pit_stop_office": "vol6_kwik_stop_interior",
        "pit_stop_back_booth": "vol6_kwik_stop_interior",
        "cosmic_comics_interior": "vol6_cosmic_comics_interior",
        "cosmic_comics_back_office": "vol6_cosmic_comics_interior",
        "bindery": "vol6_cosmic_comics_interior",
        "nexcorp_gas_go": "vol6_gas_and_go_interior",
        "nexcorp_fueling_station": "vol6_gas_and_go_interior",
        "el_rancho_taqueria": "vol6_el_rancho_interior",
        "school_field_evening": "vol6_live_oak_field",
        "gym_weight_room": "vol6_live_oak_field",
        "equipment_shed": "vol6_live_oak_field",
        "caldwell_radio_room_night": "vol6_substation_nine",
        "henderson_garage": "vol6_substation_nine",
        "nightmare_cell": "vol6_corporate_hum",
        "meadowlark_circle": "vol6_ambient",
        "meadowlark_circle_night": "vol6_ambient",
        "meadowlark_circle_henderson": "vol6_ambient",
        "miller_kitchen": "vol6_new_auburn_kitchen",
        "miller_back_porch": "vol6_new_auburn_kitchen",
        "miller_office": "vol6_new_auburn_kitchen",
        "miller_garage": "vol6_new_auburn_kitchen",
        "henderson_kitchen": "vol6_new_auburn_kitchen",
        "henderson_porch_front": "vol6_new_auburn_kitchen",
        "kowalski_kitchen": "vol6_new_auburn_kitchen",
        "kowalski_backyard": "vol6_new_auburn_kitchen",
        "caldwell_kitchen_night": "vol6_new_auburn_kitchen",
        "caldwell_porch_night": "vol6_new_auburn_kitchen",
        "bianca_kitchen_morning": "vol6_new_auburn_kitchen",
        "ramos_kitchen_morning": "vol6_new_auburn_kitchen",
        "grandmother_kitchen_morning": "vol6_new_auburn_kitchen",
        "roberts_kitchen": "vol6_new_auburn_kitchen",
        "sam_bedroom": "vol6_new_auburn_kitchen",
        "maya_bedroom": "vol6_new_auburn_kitchen",
        "jesse_bedroom": "vol6_new_auburn_kitchen",
        "diego_bedroom": "vol6_new_auburn_kitchen",
        "graciela_bedroom": "vol6_new_auburn_kitchen",
        "ben_bedroom": "vol6_new_auburn_kitchen",
        "coach_k_bedroom": "vol6_new_auburn_kitchen",
        "safehouse_bedroom": "vol6_new_auburn_kitchen",
        "cypress_motel": "vol6_new_auburn_kitchen",
        "vehicle_cab": "vol6_two_lane",
        "vehicle_cab_side": "vol6_two_lane",
        "vehicle_cab_rear": "vol6_two_lane",
        "new_auburn_two_lane": "vol6_two_lane",
        "new_auburn_bypass": "vol6_two_lane",
        "new_auburn_cedar_route": "vol6_two_lane",
        "new_auburn_lot": "vol6_two_lane",
        "new_auburn_strip_mall": "vol6_two_lane",
        "louisiana_road": "vol6_two_lane",
        "foxhole_bar": "vol1_club_thump",
        "foxhole_stage": "vol1_club_thump",
        "foxhole_dressing_room": "vol1_club_thump",
    },
    7: {
        "cabin_interior": "vol7_cabin_woodstove",
        "cabin_interior_bed": "vol7_cabin_woodstove",
        "cabin_road": "vol7_cabin_woodstove",
        "miller_back_porch": "vol7_cabin_woodstove",
        "lena_apartment": "vol7_apartment_rain",
        "salty_tome_alley": "vol7_painting_room",
        "salty_tome_interior": "vol7_shop_signal_bell",
        "salty_tome_kitchenette": "vol7_shop_signal_bell",
        "board_lords_interior": "vol7_shop_signal_bell",
        "hans_bakery_back_kitchen": "vol7_bread_table",
        "kestrel_mountain": "vol7_kestrel_circle",
        "kestrel_mountain_square": "vol7_kestrel_circle",
        "accretion_basement": "vol7_kestrel_circle",
        "accretion_corridor": "vol7_kestrel_circle",
        "cathedral_interior": "vol5_cathedral_drone",
        "missing_link_interior": "vol1_diner_ambient",
    },
}

# Scenes whose TITLE is about a place the backgrounds visit only in
# passing. The dominant-locale rule gets these wrong on purpose.
OVERRIDES = {
    "vol6_ch20_bridge": "vol6_substation_nine",     # "Substation Nine"
    "vol6_ch5_garage": "vol6_substation_nine",      # garage-band catharsis
    "vol6_ch0_prelude": "vol6_ambient",             # "Harmony Creek Estates"
    "vol6_ch2_coda": "vol6_corporate_hum",          # "The Hum, Everywhere"
    "vol6_ch22_foxhole": "vol1_club_thump",         # "The Foxhole"
    "vol7_ch18_pool": "vol7_kestrel_circle",        # the tide pools
    "vol1_title": "vol1_title",
    "vol1_end": "vol1_milestone_choice",
}


def scenes():
    out = []
    for vol in sorted(os.listdir(SCENES)):
        vd = os.path.join(SCENES, vol)
        if not os.path.isdir(vd):
            continue
        for fn in sorted(os.listdir(vd)):
            if not fn.endswith(".json") or fn == "index.json":
                continue
            j = json.load(open(os.path.join(vd, fn), encoding="utf-8"))
            sid = j.get("id", fn[:-5])
            bgs = [str(nd.get("src") or "") for nd in j.get("nodes", [])
                   if nd.get("t") == "bg"]
            locs = [b[3:] for b in bgs if b.startswith("3d:")]
            out.append((vol, sid, locs, len(j.get("nodes", []))))
    return out


def main():
    dry = "--dry" in sys.argv
    cat = json.loads(open(CATALOG, encoding="utf-8").read())
    by_id = {e["id"]: e for e in cat}
    named = set()
    for e in cat:
        named |= set(e.get("chapters", []))
        if e.get("chapter_id"):
            named.add(e["chapter_id"])

    def playable(tid):
        e = by_id.get(tid)
        return bool(e) and os.path.exists(os.path.join(GODOT, e.get("src", "")))

    placed, floored, residue = 0, 0, []
    for vol, sid, locs, n in scenes():
        if sid in named or sid.endswith("_stub"):
            continue
        vnum = int(vol[3:]) if vol.startswith("vol") and vol[3:].isdigit() else 0
        table = PLACES.get(vnum, {})
        pick = OVERRIDES.get(sid, "")
        kind = "override"
        if not pick and locs:
            for loc, _c in Counter(locs).most_common():
                if loc in table:
                    pick, kind = table[loc], "place"
                    break
        if not pick:
            pick, kind = "vol%d_ambient" % vnum, "floor"
        if not playable(pick):
            residue.append((vol, sid, n, pick))
            continue
        by_id[pick].setdefault("chapters", []).append(sid)
        named.add(sid)
        if kind == "floor":
            floored += 1
        else:
            placed += 1
        print("%-34s %-28s %s" % (sid, pick, kind))

    for e in cat:
        if "chapters" in e:
            e["chapters"] = sorted(set(e["chapters"]))
    print("\n%d by place · %d on the volume floor · %d unscored"
          % (placed, floored, len(residue)))
    for vol, sid, n, want in residue:
        print("   UNSCORED %-30s %4d node(s) · wanted %s" % (sid, n, want))
    if not dry:
        with open(CATALOG, "w", encoding="utf-8") as f:
            f.write(json.dumps(cat, indent=1, ensure_ascii=False) + "\n")
        print("\nwrote %s" % os.path.relpath(CATALOG, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
