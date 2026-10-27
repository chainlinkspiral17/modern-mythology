# Vols 1–4: sets and cast (backgrounds + models program)

**2026-10-16, draft 1.** The user: *"Let's move back to background and model
work for all the new vol 1-4 stuff."*

The vols 1–4 story lives on `claude/vol1-4-source-text` (another session):
448 scenes, ~145k words. Its scenes name **279 flat background pictures**
(`assets/backgrounds/<stem>.jpg`) that were never made, and ~70 speaking
characters, most of them without models. This doc is the plan for both.

## How a vols 1–4 scene finds its set

`godot/resources/vn/bg_places.json` maps every stem to a set, and
`GameEngine.resolve_bg()` plays that 3D preset in place of the picture, so
the other branch's scene JSON never needs editing (no merge fights). Each
stem has a `fit`:

| fit | meaning | stems | scene uses |
|---|---|---|---|
| exact | the place itself (incl. the August vol 1–2 migration pairs) | 38 → 53 | 70 → ~115 |
| reuse | an existing set that IS this kind of place (a hospital room, LAX → no) | 81 | 98 |
| standin | the nearest set until its own **build** group exists | 114 → 99 | 179 → ~134 |
| 2d | stays a picture (game screens, inserts, montages, the pulp visions); `to: null` until painted | 46 | 55 |

When a build group lands: point its stems at the new presets, set `fit:
exact` and `built`, render it with `tools/PresetShot.gd`, record its
perf baseline (`perf_gate.py --update <room>`).

## Build queue (new sets, by scene uses)

| # | group | uses | the views it needs | status |
|---|---|---|---|---|
| 1 | **writers_desk** (vol 4's scrapbook desk) | 33 | desk night, corkboard, room from the door, desk at dawn | **draft 1 built 2026-10-16** — `build_writers_desk.py`, presets `writers_desk`, `_board`, `_room`, `_dawn`; 108 draw calls |
| 2 | **small_wood_high** (+ vol 4's classrooms) | 12 | the gym (the school-board hearing), hallway, locker room, art room; Todd's 7th-grade class, computer lab | **draft 1 built 2026-10-16** — `build_small_wood_high.py`, presets `small_wood_high_gym`, `_hall`, `_locker`, `_class`, `_art`, `_lab`; 236 draw calls |
| 3 | **link_house** (vol 3, Texas; was andy_family_house) | 9 | kitchen evening, living room night, bathroom day/night, Andy's room day/night/lamp | **draft 1 built 2026-10-17** — `build_link_house.py`, presets `andy_house_kitchen`, `_living`, `_bath`, `_bath_night`, `_bedroom`, `_bedroom_night`, `_bedroom_lamp`; 268 draw calls. The blanket fort moved to amanda_house (first chau_house; the text puts it at Amanda's, 2026-10-17), the Dallas closet to june_dallas |
| 4 | **caltech_dabney** (vol 3–4) | 11 | the bare room, the game room, Dabney courtyard, campus, the steam tunnels, Spencer's room, the 1945 hallway, the basement | **draft 1 built 2026-10-17** — `build_caltech_dabney.py`, presets `dabney_courtyard`, `_courtyard_1945` (same camera, 2003 props stripped), `_side_yard`, `_game_room`, `_couch`, `_couch_carving`, `spencer_room`, `caltech_tunnels`, `caltech_hallway_1945`, `caltech_bare_room`, `_dark`; 150 draw calls |
| 5 | **small_wood_ranch** (vol 2, the narrator's family ranch) — **UNIFIED 2026-10-27 into small_wood_farmhouse, THE LINK HOME** (Andy: the points-of-impact family lives in the Link home after they move out): his room is upstairs NW, the second house in the field SE; the ranch presets load the farmhouse | 5 | his room at night, the reading lamp, "the room" up the hill (Dean rebuilds this room), the second house | **draft 1 built 2026-10-17** — `build_small_wood_ranch.py`, presets `ranch_bedroom_night`, `_lamp`, `_day`, `ranch_second_house`; 102 draw calls |
| 5b | **dean_house_1994** (vol 2, Small Wood) | 2 | teenage D.N. Dean's bedroom (3:50 a.m., the furnace under the floor) and the basement (graph paper, the monitor off) | **draft 2 built 2026-10-18** — `build_dean_house_1994.py`, presets `dean_bedroom_1994`, `dean_basement_1994`. The bedroom is the narrator's room from `_props/small_wood_house.py` (the user: "the same layout, just dressed different"; the two houses overlap in the dreams); 100 draw calls |
| 5c | **small_wood_farmhouse** (vol 2) | 2 | the renters' living room at the picture windows, the porch on a cold night (a spare kitchen-window view) | **draft 1 built 2026-10-18** — `build_small_wood_farmhouse.py`, presets `farm_living_night`, `farm_porch_night` (by_scene, loose_pages), `farm_kitchen_window`; 70 draw calls |
| 5d | **small_wood_town** (vol 2) | 2 | the radio drama's studio (December 1992), Chuck's video store counter (February 2013) | **draft 1 built 2026-10-18** — `build_small_wood_town.py`, presets `radio_studio`, `video_store_counter`; 62 draw calls |
| 5e | **small_wood_field** (vol 2, Small Wood High's football field) | 3 | Friday night under the lights (points of impact, rewind), two-a-days at dusk (interlude one) | **draft 2 built 2026-10-27** (Andy: green and white; a running track round the field; the home stand covered under an elevated slanted roof) — `build_small_wood_field.py`, presets `small_wood_field_night`, `_dusk`. Was vol 6's Texas field (the Deck: "football field and stadium is still nonsense"). The covered wooden home stand, wooden light poles, the firs, the church across the street — PROPOSED, the text gives the lights, the bleachers, the scoreboard, the church |
| 6 | **little_league** (vol 3, "acceptable losses"; the text says only "our league") | 7 | dugout in August, on third base, the mound, first base, home plate, the convenience stand | **draft 1 built 2026-10-17** — `build_little_league.py`, presets `ballfield_dugout`, `_third_base`, `_mound`, `_first_base`, `_home_plate`, `_stand`; 74 draw calls |
| 7 | **dean_offices** | 6 | the trio's Office (vol 1 Act Two; theirs, not Dean's), the club office, the tutorial lobby, his monitor room and his office building at night (vol 4) | **draft 1 built 2026-10-17** — `build_dean_offices.py`, presets `onei_office`, `_desk`, `_door`, `tutorial_lobby`, `club_office`, `_after`, `dean_monitor_room`, `dean_tower_corridor`; 116 draw calls |
| 8 | **chau_house** (vol 3, "passengers") | 4 | the hall at noon and the entry in the morning, the living room, the game room on Sunday morning, the steam bathroom | **draft 1 built 2026-10-17** — `build_chau_house.py`, presets `chau_hall_noon`, `chau_entry_morning` (by_scene, part c), `chau_living`, `chau_bath`, `chau_game_room`, `chau_steven_room` (vol 4's "the wasted sentiment"); 98 draw calls |
| 8b | **amanda_house** (vol 3, "passengers") | 2 | the hot tub at 10 p.m. Saturday, the blanket fort (pushed-together couches, the fan's sheet) | **draft 1 built 2026-10-17** — a sub-area of `build_chau_house.py` (x 40..56), presets `amanda_hot_tub`, `amanda_fort`, `amanda_fort_close` (by_scene, part c) |
| 9 | **airport_cabin** | 6 | LAX terminal at night, plane cabin day/night, vol 4's November cabin | **draft 1 built 2026-10-17** — `build_airport_cabin.py`, presets `lax_gate`, `lax_store`, `lax_seat_close`, `plane_night`, `plane_day`, `plane_vol4`; 222 draw calls |
| 10 | **copy_shop** | 5 | the copier at night (vol 2), the melds' copier at 4 a.m., vol 4's office after hours (paper cuts) | **draft 1 built 2026-10-17** — `build_copy_shop.py`, presets `copy_shop_floor`, `_wastebasket` (by_scene, apple_peddler), `_copier`, `office_after_hours` (its own picture, `vol4_office_after_hours`); 100 draw calls |
| 11 | **sleep_lab** | 5 | Jane's sleep study, the four-screen room | **draft 1 built 2026-10-17** — `build_sleep_lab.py`, presets `sleep_lab_entry`, `_desk`, `_night`, `four_screens_wide`, `_show`, `_beam`; 348 draw calls |
| 12 | **pasadena_1945** | 5 | Pasadena street (clear; the meld's rain), the park, a Hollywood street, the 1945 clinic | **draft 1 built 2026-10-17** — `build_pasadena_1945.py`, presets `street_day`, `street_rain` (by_scene, meld_seam_2_3), `park_chess`, `hollywood_shoot`, `clinic_1945`; 134 draw calls |
| 13 | **editing_suite** | 4 | the four's suite at Aud's (vol 1; the vol 2 and vol 4 melds), vol 3 ch4's night edit station | **draft 1 built 2026-10-18** — `build_editing_suite.py`, presets `suite_wide`, `suite_tide`, `suite_4am` (by_scene, meld_kaleidoscope_c), `edit_station`; 64 draw calls |
| 14 | **apple_peddler** (vol 2) | 4 | the Apple Peddler of d.dean's story (booth, line); ch8's unnamed local diner and ch5's evening diner as reuses; the meld's dawn block plays the existing Missing Link | **draft 1 built 2026-10-18** — `build_apple_peddler.py`, presets `apple_peddler_booth`, `_grill`, `_night`; 88 draw calls. Timeline Knot 12 (Aud's Missing Link in vol 2) is the author's |
| 15 | **parsonage_1945** | 4 | Ron's room upstairs at dawn / day / night (two views), the hall | **draft 1 built 2026-10-18** — `build_parsonage_1945.py`, presets `ron_dawn`, `ron_day`, `ron_night_floor`, `ron_night_bed` (by_scene, ch19), `parsonage_hall`; 78 draw calls |
| 16 | **bus_station** (vol 4) | 4 | under the bus overhang (Ext. · Day), on the bus (two views) | **draft 1 built 2026-10-18** — `build_bus_station.py`, presets `bus_station`, `bus_two_shot`, `bus_aisle` (by_scene, cc_2); 80 draw calls |
| 17 | **sea_cave** (vol 2, ch9) | 4 | Julie's cave at dawn, at low tide, with the tide in; Charles's riverbed sand | **draft 1 built 2026-10-18** — `build_sea_cave.py`, presets `cave_dawn`, `cave_low_tide` (by_scene, art class), `cave_tide_in` (by_scene, the truck), `riverbed_sand`; 102 draw calls |
| 17b | **oregon_lighthouse** (vol 2) | 1 | the lighthouse 1.5 hours from Small Wood, December night (not the bayou lighthouse) | **draft 1 built 2026-10-18** — `build_oregon_lighthouse.py`, presets `lighthouse_base_up`, `lighthouse_gate`; 68 draw calls |
| 17c | **nick_house** (vol 3, "uncle nick") | 5 | the dark front on Halloween, the garage (Mark's workshop; the print shop years later), Nick's room, the drafting table | **draft 1 built 2026-10-18** — `build_nick_house.py`, presets `nick_house_front`, `nick_garage_halloween`, `nick_print_shop`, `nick_room`, `nick_drafting` (by_scene, uncle_nick_b); 82 draw calls |
| 17d | **lake_house** (vol 3, "acceptable losses") | 6 | Terry's front, the dock by day, sunrise from the kitchen table, Chris's room day and night, the bathroom before dawn | **draft 1 built 2026-10-18** — `build_lake_house.py`, presets `lake_house_day`, `lake_dock_day`, `lake_dock_dawn`, `chris_room_day`, `chris_room_night`, `lake_bath_night`; 140 draw calls |
| 17e | **tulsa_house** (vol 3, "safari") | 2 | Marty's slide show, the patio and the fort under the moon (mid-eighties) | **draft 1 built 2026-10-18** — `build_tulsa_house.py`, presets `tulsa_slideshow`, `tulsa_patio`; 74 draw calls |
| 17f | **carrie_city** (vol 4, Sister Carrie) | 5 | Charlie's flat (bedroom night, day; living room night, and the morning after), the after party (wide, the two stools), the sister's house (yard, inside) | **draft 1 built 2026-10-18** — `build_carrie_city.py`, presets `charlie_bedroom_night`, `charlie_apartment_day`, `charlie_living_night` / `_day` (by_scene, cc_5), `afterparty_room`, `afterparty_stools` (by_scene, cc_5), `sister_house_yard`, `sister_house_inside`; 88 draw calls |
| 17g | **vol4_story_rooms** (vol 4) | 7 | the honeydew garage, the dead clothing store, the mirror, Aaron's room (and its blue dream), Steven's room, the Deans' house late, the Shanghai room | **draft 1 built 2026-10-18** — `build_vol4_story_rooms.py`, presets `garage_level`, `dead_store`, `mirror_room`, `aaron_bedroom`, `aaron_bedroom_blue`, `dean_house_late`, `shanghai_window_night`. Steven's room moved to chau_house (`chau_steven_room`; the user: Steven lives at the Chau house); 132 draw calls |
| 18 | **wagner_home** (draft 3: the front) + Jacob's | 3 | Wagner's porch in the morning, the steps and the open door in the afternoon, Jacob's house on another block | **draft 3 built 2026-10-18** — `build_wagner_home.py`, presets `wagner_porch_morning`, `wagner_house_steps`, `jacob_house_front`; 116 draw calls |
| 18b | **club_street** (vol 1) | 4 | the street outside Club #: out the door (ch8), the curb and JD (ch9), the meld's neon, 4 a.m. (ch16, new stem `vol1_club_street_dawn`) | **draft 1 built 2026-10-18** — `build_club_street.py`, presets `club_street_door`, `club_street_curb`, `club_street_neon_wide`, `club_street_dawn`; 110 draw calls |
| 18c | **vol3_rooms** (vol 3) | 11 | June's closet, the Oregon home (day, night; also ch4's "back home"), the coast studio and bathroom, the condo demo unit, the Korean barbecue, the pizza party room, the club, the hospital catwalk (two views) | **draft 1 built 2026-10-18** — `build_vol3_rooms.py`, presets `june_closet`, `oregon_home_day`, `_night`, `coast_studio`, `coast_bathroom`, `condo_demo_unit`, `korean_bbq_table`, `pizza_party_window`, `warehouse_floor`, `catwalk_rail_night`, `catwalk_walk` (by_scene, yellow card); 200 draw calls |

## The eras (Andy, 2026-10-27) and WAVE 4: the borrowed sets

- **vol 1** — 2010s Houston, "weird and fantastical".
- **vol 2** — "Oregon in the late 1990s look" (Small Wood; Smolvud is the 2050s Small Wood).
- **vol 3** — "all over the map, but early 2000s".

A sweep on 2026-10-27 found 36 vol 1–4 uses of sets built for vols 5–7 (`bg_places` reuse/stand-in rows and direct `3d:` bgs). Ranked by how wrong they read:

| priority | scene(s) | plays on | needs | status |
|---|---|---|---|---|
| 1 | vol3 ch7 emulsion / red dust (Utah desert, gas station, motel) | vol 6 Texas hwy 9, NexCorp, Cypress Motel | its own desert road, early 2000s | **built 2026-10-27** — `desert_route` (six presets) |
| 1 | vol2 ch2/ch3 football | vol 6 Texas stadium | Small Wood's field | **built 2026-10-27** — `small_wood_field` |
| 2 | vol1 exteriors (the park, the river) | vol 5 Graustark riverfront | 2010s Houston, weird | **built 2026-10-27** — `houston_bayou`: `houston_park_day` (Buffalo Bayou), `jd_river`, `jd_river_turn` (the dream river). The interiors stay (Andy: "Houston and New Orleans interiors can be similar"). Judgement Day's driving-day cab (vehicle_cab) still to look at |
| 2 | vol3 ch6 arcadeum (Honolulu high-rise lobby, game store) | 2052 cedar tower, 2026 Cosmic Comics | Honolulu, early 2000s | to plan |
| 2 | vol2 ch6 mayhune (summer backyard party) | vol 6 Texas Kowalski backyard | a late-90s Oregon backyard | to plan |
| 2 | vol2 bookstores (The Cat's Pause, the Blue Heron) | vol 7 Salty Tome (2052) | the 1990s bookstores | to plan |
| 2 | vol3/vol4 gas stations, restroom (NexCorp) | vol 6 NexCorp (2026 brand) | an unbranded early-2000s station | to plan |
| 3 | vol2 docks, Hwy 101 (Small Wood 1997) | vol 7 Smolvud jetty, Hwy 101 (2052) | the same places in their 1997 state (era presets) | to plan |
| 3 | vol3 ch4 city street; vol4 apartments | vol 7 main street, Finn's 2052 apartment | era-right streets and rooms | to plan |
| ok | MD Anderson hospital, Dean's tower, dream cells, Cape Perpetua | — | — | kept |


**Stand-ins carry a cost:** a 1945 Pasadena street played by Main Street is
the wrong decade. They exist so no scene goes black; they are not the look.

## 2D (46 stems)

These are pictures by design, painted through Hero Studio:
- the chapter vii graphic-adventure screens (`vol2_scumm_*`), in a modern
  look and never era cosplay;
- the Earthman pulp visions (`vol3_pulp_*`, the ruined city, the time pod);
- inserts: the scrapbook, the Usenet post, Sister Carrie notes, the
  letters, the arcade cabinet;
- montages and abstracts (the hall of ratifications, the mandala, the pink
  void);
- vol 4's beach-daycare colour series;
- the battle painting.

Until one is painted, a scene showing it has no background. Draft 2: a
Hero Studio `scene2d` kind, so these generate and install like hero art.

## Cast

Already modelled for vols 1–4: Faust, Jacob, Dickens Dean, Wagner, Joan,
Deborah, Emily, Helen, Margaret (as `margaret_coop`), Eric, the Stranger,
Aud, David Jarvis, Hans, Chess, Philip (Roberts).

**51 new roster entries (2026-10-16)** — 48 characters and 3 looks, prompts
anchored in the manuscript and the other branch's `voice_map.json`, every
canon quote checked word for word:
- vol 1: Olivia, Aunt Grace, the Fool, the corpse-painted boy, the pharmacy's
  old woman, the bar group's Margaret, the four author facets (the Writer,
  the Director, the Artist, the Human Being — one man, four models), and
  Air, Fire and Water, who step off the shirts;
- vol 2: Bernard, Joe K-U, Becca, Pastor Tim, Charles, Jay Rose (portly, the
  DJ) and Arthur Finch (lean, the strip), Katrina, Shannon, Delores;
- vol 3: Andy (2003, and a 1945 look), Ron (as the text draws him, not a
  photo likeness), Betty, Jack Parsons, Jack Perkins, Janessa, June Okimoto,
  Jane, Aunt Terry, Niles, Marty, Kathy, Steven Chau, Aaron Cauther, Chris,
  Uncle Nick, the shopkeeper, the businesswoman, April;
- vol 4: Charlie Drouet, Caroline, Esther, Hurstwood, Caroline's sister,
  Norm Todd, Chess young (a look), the young Dickens Dean (a look).

Generate them in Hero Studio; `slim` brings each to ~5 MB. Where canon is
silent the entry's notes say "proposal" — edit before spending credits.

Open from the cast pass (the author's calls):
- Dickens Dean is young in vols 1 and 4 ("this young person — tall,
  attractive"); the roster's Dean is silver-haired: extend the young look
  to vol 1?
- Is vol 4's Chess (early 20s) vol 6's Chess (about thirty)?
- The speaking Terry in vol 3 is Aunt Terry (a woman); the other branch's
  voice_map casts "terry" as Coach Terry, who has no lines.
- `faust`, `jacob`, `wagner`, `aud` and `hans` lack the meld scenes' volumes
  (2, 4) in their `vol` lists, so those scenes fall back to 2D for them.

Canon to keep straight: **Arthur Finch draws DriftWood; Jay Rose is the DJ**
— a split character, and the names blur on purpose (see the roadmap).

## Ages: a look and a voice for each era (2026-10-16)

The user: *"characters need new looks and voices as they age."*

**The ledger is `godot/tools/ages.json`.** It has the timeline (with sources) and,
for 28 recurring characters, every era: volumes, scenes, year, age, the roster
look for that age, and a voice key with a casting note.

The timeline:
- vol 1: spring 2009;
- vol 2: 1993–94;
- vol 3: 2003, plus 1945 and 1991;
- vol 4: 2006, plus "daddy" running about 2010 into the 2030s;
- vol 5: spring 2025 (the age-7 flashback is about 2015; Montreal is about 2039);
- vol 6: summer 2025;
- vol 7: 2052.

**Looks.** The roster carries one entry per age. A look entry has `base` (the
character) and `look.vols` / `look.scenes` (where it shows), and `CharLayer`
picks it. The pass added six looks: `aud_1994`, `hans_1994`,
`john_frank_montreal`, `elicia_temple_montreal`, `aria_dean_sighting` and
`aria_dean_teen`. It also rewired these:
- **Dickens Dean** has three ages:
  - `nate_kestrel`, the teenage Nate Dean of 1993–94 (vol 2's dream journal,
    vol 7's memories);
  - `dickens_dean_daddy`, early 30s (vols 1 and 4, per the user's ruling);
  - the base model at about 50 (vols 5–6).
- **Chess:** `chess_vol4` (early 20s), then the base at about 30 (vol 6).
- **Maya:** `maya_daigle_age7` is fenced to vol5_ch5_hierophant. It used to
  take every vol 5 Maya, including the 16-year-old.
- **Natalie** is mid-40s, not late 20s, by the text.

**Voices.** `elevenlabs_render.py` asks `voice_ages.era_voice_key(char,
scene)` first. When that era's key has a `voice_id` in `voice_map.json`, the
line is spoken at that age. Otherwise the character's own voice is used,
so nothing goes silent while ages are uncast. `python3
godot/tools/voice_ages.py` lists them: **9 new voices to cast**:
- teen Dean, 1994;
- Aud at 73 and Hans at 40;
- Montreal John and Elicia, about 2039;
- Maya at 7 and at 16;
- Lena and Cale, 2052.

33 eras keep a voice that already exists. `ages_audit.py` keeps the ledger
and the roster in step (run by the scoped suite).

**Held for the author** (in the ledger's `edits`, marked HELD):
1. **Vol 7's two calendars.** Its dated events are 2052, but its stated ages
   (Aud 73, Hans 68, "N years since") count from about 2022–24. Under 2052,
   Aud and Hans were 15 and 10 in 1994, and their 1994 looks would be dreams
   of their older selves. Cale would be 77, but the roster says 40s.
2. Vols 5 and 6 are the same year by the text; the lore's "twenty years of
   evolution" belongs to an older timeline.
3. Vol 4 daddy_b/c set Dean 10–20 years after daddy_a. Should those use the
   older base?
4. `miriam_2025` rests on a nine-year gap the text doesn't support. Retire
   it?
5. Keys that route to two people: `wren`, `sammy`, `margaret`, `brandon`;
   vol 6's bassist `nate`.

## Accounting: every speaker, prop, picture and cue (2026-10-17, draft 1)

The user: *"we'll need all the heroes and hero props and assets for vol 1-4
accounted for as well."*

```bash
git fetch origin claude/vol1-4-source-text && D=$(mktemp -d) && git archive origin/claude/vol1-4-source-text godot/resources/scenes | tar -x -C $D && python3 godot/tools/vol_assets.py --scenes $D/godot/resources/scenes
```

`vol_assets.py` resolves each speaker the way CharLayer does, including the
volume filter. It counts a file as present when either branch has it. Against
dbabab4a:

| | total | covered | open |
|---|---|---|---|
| speakers | 112 | 101 roster entries · 11 voice only | 0 |
| CG | 66 | 13 on the vols 1–4 branch · 53 `scene2d` drafts | 0 |
| backgrounds | 291 | 232 3D sets · 53 `scene2d` drafts | 6 wait on a build (airport, andy_family_house, chau_house) |
| music cues | 38 | 1 | **37** |

- **Voice only, by the text:** the voices in Jacob's and Wagner's earbuds,
  Habes's message, the frame ("Wood"), the voice-over, a Player, the
  three-at-once line, the passing stranger, the starship's Sentries, and Dean's
  daughter in vol4_goggles ("We don't see her yet"). The "Man" of
  vol1_ch4_dream_bar is Dickens Dean before he gives his name, and the scene
  shows his model. The list lives in `VOICE_ONLY` in the tool.
- **24 new heroes:**
  - vol 1: the dreamgirl and the clerk with no face;
  - vol 2: the beach-party cast (Not Chuck, the DJ in the tent, Guitar Gal,
    Star Gal, the woman who clings, the Out of Towner, Tourista) and the four
    House of Glass actors;
  - vol 3: Melody, Jules, Verse, the Core and the inoculation nurse;
  - vol 4: the brother-in-law, All Smiles, the workshop girl, the video-test
    woman and her I.F., and Alex.
- **16 hero props:** Joan's dagger, the cracked DJ headphones, the black
  guitar pick, D. Dean's journal, the heron feather, the derby crab number 0,
  the key with no teeth, the small yellow raincoat, the 1969 Mercedes, Ron's
  typewriter, the IRIS binder, the toy soldier, the red string, the cardboard
  kaleidoscope, the star key and the copy of Sister Carrie.
- **107 pictures** are the new Hero Studio kind `scene2d`. Each installs as a
  1920-wide JPEG at the exact path its scene names. `scene2d_draft.py` drafted
  them from the narration around each picture. **Read them before spending
  credits.**
- The other branch now names the vol 2 deejay "Arthur Finch" and has Arthur
  disappear first. Per the ruling, `jay_rose` stays the DJ's look and the
  blur stays in the text.
