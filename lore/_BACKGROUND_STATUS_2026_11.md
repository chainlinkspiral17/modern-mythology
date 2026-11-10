# Background sets — where each one stands (2026-11-10)

The user: *"Background models still need a lot of work."* This is the measured state of every 3D set the
visual novel plays on, in order of how many lines the reader spends there. It is a work queue for THE
DRAFTING PROGRAM (`_IMPROVEMENT_ROADMAP.md`), not a report of anything finished.

**116 sets carry 19240 lines. Half of all lines play in the top 15 sets.** The model chapters — the sets that
have absorbed many passes — have 2,000–6,500 parts (the Kwik Stop 6,469, the diner 3,118, the cabin 2,126).
Most of the sets the reader spends the most time in have 350–900.

Columns: **lines** played there · **views** (camera presets) · **marks** (shot markers) · **lights** ·
**parts** (builder objects — a proxy for how much has been modelled) · **held** (views whose set stops at the
16:9 frame: `wide_frame_audit` could not clear them for a wider screen — an EDGES measure) · **empty** (frames,
posters, screens with no picture: `empty_frame_audit`).

| set | lines | views | marks | lights | parts | held | empty |
|---|---:|---:|---:|---:|---:|---:|---:|
| `cabin_interior` | 2144 | 6 | 108 | 31 | 2126 | 6 | 2 |
| `lena_apartment` | 941 | 2 | 40 | 10 | 645 | 2 | 2 |
| `salty_tome_interior` | 844 | 8 | 44 | 12 | 2042 | 8 | 2 |
| `miller_kitchen` | 800 | 2 | 29 | 13 | 719 | 0 | 6 |
| `hans_bakery_back_kitchen` | 695 | 2 | 37 | 10 | 870 | 2 | 2 |
| `cosmic_comics_interior` | 660 | 2 | 46 | 12 | 1132 | 2 | 7 |
| `board_lords_interior` | 598 | 3 | 27 | 11 | 848 | 3 | 2 |
| `kwik_stop` | 537 | 5 | 25 | 13 | 6469 | 5 | 5 |
| `graustark` | 460 | 10 | 40 | 23 | 11073 | 8 | 8 |
| `vehicle_cab` | 441 | 10 | 47 | 39 | 1061 | 10 | 1 |
| `centro_grocery_aisle` | 428 | 1 | 19 | 14 | 20580 | 0 | 0 |
| `school_field_evening` | 385 | 2 | 30 | 18 | 1457 | 2 | 0 |
| `pit_stop_interior` | 336 | 4 | 30 | 17 | 1183 | 4 | 2 |
| `henderson_kitchen` | 322 | 1 | 22 | 5 | 636 | 0 | 1 |
| `finn_apartment` | 303 | 3 | 26 | 11 | 614 | 1 | 1 |
| `kowalski_kitchen` | 294 | 2 | 20 | 9 | 791 | 2 | 1 |
| `natalie_apartment` | 292 | 2 | 21 | 11 | 692 | 1 | 3 |
| `chillwave_interior` | 267 | 2 | 19 | 8 | 601 | 1 | 0 |
| `bianca_kitchen_morning` | 259 | 2 | 19 | 13 | 718 | 0 | 6 |
| `caldwell_porch_night` | 257 | 2 | 25 | 6 | 500 | 2 | 0 |
| `miller_back_porch` | 253 | 2 | 18 | 7 | 367 | 2 | 4 |
| `houston_office` | 240 | 1 | 8 | 9 | 577 | 1 | 1 |
| `centro_break_room` | 234 | 1 | 12 | 8 | 432 | 0 | 1 |
| `diner` | 225 | 3 | 23 | 37 | 3118 | 1 | 9 |
| `foxhole_bar` | 214 | 2 | 13 | 19 | 659 | 0 | 1 |
| `new_orleans_bar` | 204 | 1 | 11 | 21 | 1069 | 1 | 2 |
| `new_orleans_office` | 198 | 1 | 8 | 6 | 474 | 1 | 1 |
| `henderson_garage` | 179 | 2 | 11 | 6 | 353 | 2 | 0 |
| `new_auburn_courtroom` | 177 | 1 | 13 | 10 | 480 | 1 | 0 |
| `hospital_room` | 175 | 2 | 11 | 10 | 490 | 2 | 1 |
| `cabin_road` | 172 | 2 | 18 | 5 | 828 | 2 | 1 |
| `maya_bedroom` | 171 | 2 | 17 | 11 | 533 | 2 | 0 |
| `cedar_tower` | 165 | 5 | 21 | 18 | 1286 | 5 | 24 |
| `centro_stockroom` | 164 | 2 | 11 | 6 | 558 | 2 | 0 |
| `cafe_olimpico` | 163 | 1 | 9 | 5 | 601 | 1 | 1 |
| `new_orleans_apartment` | 162 | 1 | 8 | 4 | 600 | 0 | 2 |
| `daily_grind_interior` | 155 | 1 | 15 | 13 | 1442 | 1 | 0 |
| `missing_link_interior` | 154 | 2 | 15 | 12 | 678 | 2 | 1 |
| `elicia_apartment` | 149 | 1 | 9 | 5 | 558 | 1 | 5 |
| `new_auburn_road` | 146 | 7 | 17 | 32 | 7037 | 7 | 0 |
| `roberts_kitchen` | 144 | 1 | 15 | 10 | 1142 | 1 | 12 |
| `tideline_survey` | 133 | 2 | 5 | 3 | 200 | 2 | 0 |
| `el_rancho_taqueria` | 133 | 2 | 11 | 12 | 454 | 1 | 0 |
| `sam_bedroom` | 133 | 1 | 15 | 6 | 369 | 0 | 0 |
| `nightmare_cell` | 133 | 1 | 10 | 4 | 141 | 0 | 0 |
| `hospice_room` | 131 | 2 | 7 | 8 | 248 | 2 | 3 |
| `club_sharp` | 131 | 4 | 4 | 25 | 1241 | 0 | 24 |
| `accretion_basement` | 128 | 2 | 6 | 10 | 396 | 0 | 0 |
| `grandmother_kitchen_morning` | 128 | 1 | 12 | 8 | 1054 | 1 | 1 |
| `jesse_bedroom` | 125 | 2 | 10 | 7 | 362 | 0 | 1 |
| `diego_bedroom` | 125 | 2 | 20 | 6 | 372 | 0 | 0 |
| `montreal_apartment` | 123 | 1 | 10 | 5 | 660 | 1 | 6 |
| `lake_palestine` | 122 | 2 | 8 | 4 | 841 | 2 | 0 |
| `riverboat_interior` | 112 | 1 | 7 | 18 | 1495 | 0 | 0 |
| `estuary_7_template` | 103 | 1 | 15 | 4 | 216 | 1 | 0 |
| `cathedral_interior` | 103 | 1 | 0 | 0 | 1264 | 0 | 0 |
| `faust_apartment` | 102 | 2 | 16 | 11 | 945 | 1 | 13 |
| `meadowlark_circle` | 102 | 4 | 14 | 17 | 1527 | 4 | 0 |
| `bungalow` | 100 | 1 | 12 | 13 | 681 | 0 | 0 |
| `nate_garage` | 96 | 2 | 14 | 8 | 346 | 1 | 0 |
| `kestrel_mountain` | 92 | 2 | 5 | 8 | 286 | 2 | 0 |
| `equipment_shed` | 88 | 1 | 8 | 4 | 141 | 1 | 0 |
| `ramos_kitchen_morning` | 79 | 1 | 8 | 8 | 1001 | 1 | 1 |
| `safehouse_bedroom` | 78 | 2 | 16 | 6 | 403 | 0 | 0 |
| `houston_design_studio` | 73 | 1 | 7 | 6 | 325 | 1 | 1 |
| `kowalski_backyard` | 72 | 2 | 8 | 6 | 215 | 2 | 1 |
| `briar_falls` | 68 | 5 | 18 | 5 | 1441 | 5 | 0 |
| `nexcorp_fueling_station` | 64 | 5 | 18 | 23 | 4674 | 5 | 0 |
| `small_wood_farmhouse` | 56 | 9 | 12 | 25 | 1648 | 1 | 1 |
| `miriam_subaru` | 54 | 2 | 8 | 8 | 1308 | 2 | 0 |
| `smolvud_jetty` | 51 | 2 | 10 | 4 | 703 | 2 | 0 |
| `gym_weight_room` | 47 | 1 | 9 | 5 | 277 | 0 | 0 |
| `new_orleans_room` | 46 | 2 | 5 | 7 | 264 | 0 | 1 |
| `cape_perpetua_overlook` | 45 | 1 | 9 | 2 | 385 | 1 | 0 |
| `small_wood_road` | 45 | 3 | 11 | 7 | 1268 | 3 | 0 |
| `caldwell_radio_room_night` | 45 | 1 | 5 | 6 | 403 | 0 | 1 |
| `grunion_beach` | 43 | 4 | 4 | 8 | 639 | 4 | 0 |
| `lake_house` | 42 | 7 | 8 | 12 | 1073 | 4 | 11 |
| `foxhole_dressing_room` | 42 | 1 | 7 | 4 | 133 | 0 | 0 |
| `nexcorp_gas_go` | 42 | 1 | 7 | 6 | 1618 | 1 | 0 |
| `highway_101` | 41 | 3 | 7 | 6 | 2307 | 3 | 0 |
| `bindery` | 41 | 1 | 6 | 5 | 1342 | 1 | 0 |
| `pharmacy` | 39 | 3 | 18 | 25 | 12086 | 1 | 6 |
| `missing_link_exterior` | 38 | 3 | 12 | 12 | 1422 | 2 | 0 |
| `cliffside_circus` | 37 | 2 | 6 | 10 | 376 | 1 | 0 |
| `miller_office` | 34 | 3 | 13 | 13 | 552 | 0 | 4 |
| `oregon_lighthouse` | 31 | 2 | 2 | 14 | 630 | 1 | 0 |
| `pit_stop_office` | 30 | 1 | 6 | 7 | 229 | 0 | 1 |
| `editing_suite` | 29 | 4 | 6 | 12 | 560 | 1 | 1 |
| `henderson_porch_front` | 29 | 1 | 7 | 4 | 82 | 1 | 0 |
| `school_newspaper` | 28 | 1 | 8 | 11 | 920 | 0 | 1 |
| `county_line_station` | 28 | 1 | 6 | 3 | 222 | 1 | 0 |
| `bar_exterior` | 27 | 1 | 3 | 7 | 130 | 1 | 0 |
| `houston_bayou` | 27 | 3 | 13 | 28 | 1327 | 3 | 0 |
| `coach_k_bedroom` | 23 | 1 | 7 | 5 | 162 | 1 | 0 |
| `smolvud_coop` | 22 | 1 | 5 | 8 | 778 | 0 | 0 |
| `small_wood_rec_center` | 20 | 1 | 4 | 8 | 247 | 1 | 0 |
| `lena_studio` | 19 | 1 | 7 | 4 | 161 | 0 | 0 |
| `ben_bedroom` | 18 | 1 | 5 | 5 | 216 | 0 | 2 |
| `kai_apartment` | 14 | 1 | 9 | 4 | 245 | 1 | 3 |
| `skatepark` | 14 | 1 | 7 | 3 | 710 | 1 | 0 |
| `crumpled_barn` | 11 | 2 | 6 | 5 | 1564 | 2 | 0 |
| `carrie_city` | 10 | 9 | 5 | 29 | 1486 | 0 | 16 |
| `wagner_home` | 10 | 4 | 12 | 7 | 1048 | 3 | 1 |
| `graustark_post_office` | 9 | 1 | 5 | 3 | 402 | 1 | 0 |
| `chau_house` | 9 | 11 | 5 | 24 | 2411 | 1 | 17 |
| `darkroom` | 9 | 1 | 4 | 3 | 145 | 0 | 2 |
| `gallatin_water_tower` | 9 | 1 | 2 | 1 | 170 | 1 | 2 |
| `miller_garage` | 8 | 1 | 6 | 5 | 143 | 0 | 0 |
| `sapo_falls` | 7 | 2 | 2 | 4 | 416 | 2 | 0 |
| `graciela_bedroom` | 7 | 1 | 6 | 5 | 309 | 1 | 5 |
| `small_wood_field` | 6 | 3 | 7 | 23 | 7273 | 1 | 0 |
| `nick_house` | 5 | 6 | 5 | 17 | 699 | 1 | 15 |
| `caldwell_kitchen_night` | 5 | 1 | 7 | 4 | 487 | 0 | 1 |
| `vol4_story_rooms` | 2 | 8 | 4 | 35 | 5036 | 2 | 4 |
| `riverfront` | 2 | 2 | 5 | 18 | 5375 | 2 | 8 |

## Passes since this table was measured

- **lena_apartment** — draft 8 (2026-11-10, pass 324): 645 → 789 parts; the bathroom door, the kitchen's
  fronts, the closet, the radiator, her five studies, the alley.
- **miller_kitchen / bianca_kitchen_morning** — draft 3 (2026-11-10, pass 325): 719 → 862 parts; the mudroom
  and the attached garage, the stair to the floor above, the hall closet, the drying rack, the back porch.
- Next: hans_bakery_back_kitchen → board_lords_interior → henderson_kitchen → finn_apartment.

## Brief for the next pass: hans_bakery_back_kitchen (read 2026-11-10, not yet built)

695 lines play on the preset `hans_bakery_back_kitchen`, and the scenes are not in a back kitchen. From the
text (vol7 ch15_loft 111–116, ch17_roy 8–19, ch17_aria 171, ch17_bakery 7 / 39 / 95, ch10_cabin 9 / 24):

- **Two rooms.** "The bakery's MAIN ROOM ... had three long tables: the worktable, the cooling rack table, and
  the dining table Hans had moved in in 2046". "Per is at the BACK KITCHEN ... on the bench in the back kitchen
  with a coffee." The table scenes are in the main room; the back kitchen is next door.
- **The front is in the same room.** "At six twelve the bell rang at the front of the bakery ... She walked to
  the front of the room. Greta came out from behind the front counter ... went to the door. She opened it. ...
  He stood at the door for a count. He looked across the room at the ten at the table." The builder has a
  south wall with a pass window and the front of house beyond it.
- **Also named:** the back door (the dining table's end "nearest the back door"); the kettle, Greta at it,
  "Hans's wedding-photo on the wall behind her"; the kitchenette sink; the peg the canvas coat hangs on and
  "the bench by the door" with the wooden box; Greta's cloth "folded in a particular drawer"; the bell "that
  had been at the door of the house since the house was built" — the bakery is in a house; the loft.
- **So:** the next pass is a PLAN pass, not a detail pass — one main room with the front counter and belled
  door at one end, the three long tables, the kettle wall with the wedding photograph, the back door; a
  doorway to the back kitchen (ovens, the bench). Check `hans_bakery_back_door` (10 lines) against it.

## Reading it

- **Thin and heavily used** (the first targets): `lena_apartment` (941 lines, 645 parts), `miller_kitchen`
  (800 / 719), `hans_bakery_back_kitchen` (695 / 870), `board_lords_interior` (598 / 848), `henderson_kitchen`
  (322 / 636, 5 lights), `finn_apartment` (303 / 614), `kowalski_kitchen`, `natalie_apartment`,
  `chillwave_interior`, `caldwell_porch_night` (257 / 500), `miller_back_porch` (253 / 367), `houston_office`,
  `centro_break_room`, `henderson_garage` (179 / 353).
- **Edges stop at the frame:** every view of `cabin_interior`, `salty_tome_interior`, `kwik_stop`,
  `vehicle_cab`, `pit_stop_interior`, `board_lords_interior` is HELD — the set does not run past a wider
  frame. SCALE + EDGES work clears them (and gives the panorama on a wide screen).
- **33 sets have under 400 parts** and carry 2,322 lines between them: first-generation builds.
- This counts parts, not quality. A set can have 2,000 parts and still read as a set; the Deck read decides.

## Method for each set (the model-chapter bar)

1. Read every scene that plays there; list what the text names and where the camera needs to be.
2. SCALE: size the room from what happens in it, then err larger (CLAUDE.md rule 5).
3. EDGES: run the geometry past the frame; what is outside the windows and doors; no world edge.
4. The detail pass (`_SET_DETAIL_PLAYBOOK.md` D2–D6): surface breakup, infrastructure, use states, depth
   bands, coverage and light.
5. Pictures on the walls (`_EMPTY_FRAMES_2026_11.md`).
6. Contact sheet of every view and marker; the full suite; the Deck read.

