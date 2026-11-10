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
- **hans_bakery_back_kitchen — draft 6 (pass 328, 2026-11-10): a plan pass.** One main room from the belled
  street door and front counter to the kitchenette wall, three long tables, and a real back kitchen through a
  doorway (new preset `hans_bakery_ovens`). 870 → 1,140 parts. Draft 7 targets in the roadmap.
- **board_lords_interior — draft 5 (pass 329, 2026-11-10).** Daylight (it was dusk at ten in the morning), a
  glazed front door with Main through it, the back office as a real room with the hexagon on Devon's desk, and
  five shots that looked at nothing re-aimed. 862 → 1,002 parts.
- **henderson_kitchen — draft 5 (pass 330, 2026-11-10): the house around the kitchen.** The front wall had a
  2 m open hole onto the lawn; it is closed (one wider window, an oak sideboard under the long wall). The
  kitchen doorway is a cased opening in the W wall onto a front hall (front door, a full stair up into a dark
  well, a back door) and, across the hall, the dining room nobody dines in: carpet, a chandelier with no table
  under it, the small table that holds the lamp, lit. 636 → 918 parts. Draft 6 targets in the roadmap.
- **finn_apartment — draft 5 (pass 331, 2026-11-10).** A crow on the kitchen chair for the day and dusk views
  (every kitchen crow line cut to the bed), the radio on its console behind the table, the bedroom closet with
  the wax canvas coat on its hook, the town / bluff / tower past the S window, four lines directed. The
  compass knot (one kitchen window in the text, two in the set) is left: both windows carry roster pictures.
  614 → 729 parts. Draft 6 targets in the roadmap (first: a pre-dawn twin for ch12_morning's crow).
- **kowalski_kitchen — draft 6 (pass 332, 2026-11-10).** The stair hall (flight up, the basement door ajar
  on a real flight down, the bedroom door) behind a 1.8 m cased opening; stair / basement / door shots and
  five lines directed. 791 → 899 parts. Draft 7 targets in the roadmap.
- **WINDOWS (pass 333, 2026-11-10; the user: "Look at windows, if they are too small").** Ten sets' windows
  enlarged (bedrooms, Finn's apartment, the Henderson garage, the Pit Stop office); `window_size_audit.py`
  measures every set (84 still under a house window's size in 26 sets — the cabin first).
- The queue of 2026-11-10 is through its first pass. Next six, by lines over parts: kowalski_kitchen →
  natalie_apartment → chillwave_interior → caldwell_porch_night → miller_back_porch → houston_office (briefs
  for the first two are below, read but not built).

## Brief for hans_bakery_back_kitchen (read 2026-11-10; BUILT the same day, pass 328)

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

## Brief for board_lords_interior (read 2026-11-10; BUILT the same day, pass 329 — the render found more than the brief)

598 lines on `board_lords_interior` (ch9_tuesday 131, ch16_shop 76, ch16_aud 65, ch5_roy 63, ch10_per 58,
ch2_morning 26) and 66 on `board_lords_office` (ch12_kai). Unlike the bakery, the PLAN agrees with the text
(rebuilt 2026-08 as the skate shop it is): the front door and its sign, the front window onto Main and the
sanderling mural, the parents' bench against that window, the counter with the register and its small drawer and
the stool behind it, the repair counter "in the back" under "the small fluorescent", the lathe, the back office
(Devon's desk, his chair, two boxes of bearings), the alley and the truck. So this one is a DETAIL pass:

- **Named and missing:** the BELL ("The bell had not rung. The shop was the two of them" — ch5_roy 50; a bell on
  a spring over the door has been a draft target since September); the note "taped to the inside of the door
  above the sign" and the CLOSED/OPEN sign as a part that can be read (no lettering: a card with two faces).
- **A knot for the user, not for a builder to settle:** the kettle. ch5_roy 12 / 50 have "the kettle in the back
  room"; ch16 (the builder's docstring quotes it) has him pull "the kettle out from under the counter" onto "the
  small electric burner". The set has the second. Flag it; do not move it.
- **Check by render before building:** `shot_establish_b` and the `main_street` preset for the street's depth
  (a draft-4 target that was never read); the deck wall's glass; the three kids on the bench by the window
  (ch16_shop 70) against the bench's length.
- **Then the method:** D2 wall pass (the deck wall is one colour field), D4 use states (a board on the repair
  bench with its trucks off — ch9's cracked board "from the bus rack"), D5 the alley past the office door.

## Brief for finn_apartment (read 2026-11-10)

307 lines across three views (`finn_apartment_night` 156: ch18_home 82, ch12_morning 74; `finn_apartment_day`
96: ch5_cabin 80, ch12_kai 12, ch12_morning 4; `finn_apartment` 55: ch9_evening 28, ch18_stick 27). What the
text fixes:

- "a one-bedroom above the kayak shop"; "at the corner of Hemlock and the alley that ran behind the bakery".
- THE KITCHEN WINDOW: "He stood at the kitchen window looking down at the alley" (ch12_morning) AND "The
  kitchen window faced south. South was the direction of Cape Perpetua ... The face was looking out at the
  town" (ch12_kai). One window: south, over the alley. The builder has it on the W wall ("the W wall is over
  the alley") with a second S window "toward the street and the sea" — the plan disagrees with the text.
- The kitchen: "the small kitchen table" with the folded cloth, the charred wood, later the hexagon; "the
  chair across from him" (the crow's, in the kitchen); "the chair by the table"; "the space heater in the
  corner"; "the duffel in the corner"; "the counter" (the cone and the kettle); "the kitchen light"; the radio
  ("He could hear the radio going faintly through the door", ch5); the door Kai knocks at, never locked by
  day; boots and coat pulled on at the door (ch5).
- The bedroom, through "the doorway" the crow flies low through: the bed, the wool blanket; "the chair beside
  the bed" (his grandmother's, 2046) with the crow on its back; the side table with a drawer, the reader on
  it; "the bedroom's ceiling light"; "the dresser" (handkerchiefs); "the closet" with "the hook" his wax
  canvas coat hangs on (ch18_home) — the builder has no closet.
- Shots in use: closeup person 18, insert crow 10, closeup finn 8, closeup person_b 8, insert table 6,
  establish 5, insert duffel 3, insert hexagon 3, insert charred_wood 3, insert phone / reader / door 2,
  heater, kettle, coffee, cloth, cedar, notebook, stick, sleeve, blanket, closeup kai.
- To read by render before any change: which chair the crow shots hold (kitchen vs bedroom — the text moves
  the crow between them by line), what `insert door` shows, and the night view's window.

Built the same day as pass 331. The plan's COMPASS item was dropped on reading the roster: both windows
already carry pictures (pass 203), so the set keeps its two windows.

## Brief for kowalski_kitchen (read 2026-11-10; not built)

296 lines (`kowalski_kitchen` 248: ch19_chains 95, ch13_home 57, ch8 44, ch19_depthchart 29, ch23_sleep 23;
`kowalski_kitchen_night` 48: ch7_hospital). What the text fixes:

- "He goes in through the garage" (ch13) — the door from the garage is how the family comes in; "Ben goes to
  the door. At the door he pauses." The driveway, the open garage, Bill's truck on the street on Fridays.
- The kitchen table: Bill "with the Sentinel" (the crossword: `insert crossword` x5), Anita with coffee, in
  scrubs at night ("dark except for the kitchen light. Ben's mother is at the table"); Daisy the dog under it.
- The counter (Ben makes a sandwich with his back to the table; Gracie eats cereal at it), the stove (Bill
  cooking eggs), "the cabinet to the left of the stove" (hot sauce), "the small under-cabinet light" (ch19
  night), the kitchen window (Bill "yelling about the weeds" through it).
- Stairs DOWN to the basement bedroom ("Maya goes downstairs"; "Bathroom is at the bottom of the ...") and
  UP ("He goes upstairs to bed"); a hallway from which the parents' bedroom door is seen ("by the angle of the
  bedroom door from the hallway"); the living room with the TV (the noon news; `insert couch` x3).
- Shots in use: closeup person 17, establish 11, closeup person_b 10, insert crossword 5, closeup bill /
  anita 4, closeup ben 4, closeup gracie 3, insert phone 3, insert couch 3, insert table 3, establish_b 2,
  insert eggs 2, insert garage, establish_c.
- To read by render before any change: what stands in the garage door's place, whether the stairs and hall
  exist past the kitchen, what `insert couch` and `insert garage` show, the night view's one light.
- The builder (draft 5, 10.0 x 6.4) already has the family room, the garage door and the hall opening. Its
  note "nothing in the prose climbs a stair here" is wrong: "Maya goes downstairs" / "She goes upstairs. The
  kitchen is full." (basement, ch7-8) and "He goes upstairs to bed" / "He kisses her cheek. He goes upstairs"
  (ch7, ch19). The stairs are the first target, in the hall.

## Brief for natalie_apartment (read 2026-11-10; not built)

294 lines (`natalie_apartment_night` 268: ch12_hanged 146, ch18_moon 122; `natalie_apartment` 26: ch18_moon
13, ch20_judgement 13). A studio in LA, read at night. What the text fixes:

- The door with its deadbolt ("closed the door behind her with her hip. The deadbolt clunked"), shoes off and
  a duffel "just inside the door"; `insert door` x6.
- "A nest": discarded dance shoes, "stacks of books leaning at precarious Borgesian angles", chipped
  porcelain, the bookshelf with "the small step-stool" by it; the Borges open on the floor.
- "moonlight slanting through the blinds" / "a stray beam of streetlight" / the streetlight that flickers
  outside her window; THE WINDOWSILL where the Hanged Man is set face-up and watches (`insert card` x9).
- The record player — "a Dual 1219 ... bought at a yard sale in 2014", the Nina Simone LP, the tonearm that
  lifts itself (`insert tonearm` x3, `record_player` x3, `platter`); "the ancient refrigerator" that cycles;
  the kitchen counter (her phone rings on it), the stove and kettle, "the under-cabinet light".
- THE FUTON with "a quilt woven with threads the color of twilight"; "the small low table she used for
  readings", the lamp under its scarf, the rug she sits cross-legged on; the bathroom door with the uniform
  on its back.
- To read by render before any change: the window and its blinds at night (streetlight outside, the sill
  with the card), whether the nest reads (books, shoes) or the room is bare, what `insert door` shows.

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

