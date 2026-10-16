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
| 3 | andy_family_house (vol 3, Texas) | 12 | kitchen evening, living room night, bathroom, Andy's room day/night, the blanket fort, the Dallas closet | standin: Kowalski kitchen, Jesse's room; bathrooms show nothing |
| 4 | caltech_dabney (vol 3–4) | 11 | the bare room, the game room, Dabney courtyard, campus, the steam tunnels, Spencer's room, the 1945 hallway, the basement | standin: Ben's room, Cosmic Comics office, Main Street, accretion corridor |
| 5 | dean_house_1994 (vol 2, Small Wood) | 8 | D.N. Dean's bedroom, the window at night, the reading lamp, the basement, the second house | standin: Ben's room, Henderson garage |
| 6 | little_league (vol 3, "acceptable losses") | 7 | dugout in August, the mound, first base, home plate, the concession stand | standin: school field (day) |
| 7 | dean_office | 6 | Dickens Dean's office (vol 1 Act Two), the club office, the tutorial lobby, his office at night (vol 4) | standin: New Orleans office |
| 8 | chau_house (vol 3, "passengers") | 6 | the house, living room, game room, steam bathroom, hot tub | standin |
| 9 | airport | 6 | LAX terminal at night, plane cabin day/night | standin: hospital waiting; cabins show nothing |
| 10 | copy_shop | 5 | the copier at night (vol 2), the office copier (vol 4, the meld seams) | standin |
| 11 | sleep_lab | 5 | Jane's sleep study, the four-screen room | standin: hospital room |
| 12 | pasadena_1945 | 5 | Pasadena street and park, Hollywood street, the 1945 clinic | standin: Main Street (period wrong) |
| 13 | editing_suite | 4 | the Fool's editing suite (vol 1), the meld suites (vols 2–3) | standin: Cedar Tower studio |
| 14 | apple_peddler (vol 2) | 4 | the diner: grill at dawn, at night | standin: Pit Stop |
| 15 | parsonage_1945 | 4 | the Parsonage: Ron's room night/dawn/day, the hallway | standin: the cabin |
| 16 | bus_station (vol 4) | 4 | the station by day, on the bus | standin |
| 17 | sea_cave (vol 2) | 3 | | standin: Grunion beach |
| 18 | city_night_street, faust3_houses, lighthouse | 1–3 each | | lighthouse: `bayou_lighthouse.tscn` exists — give it a VN preset |

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
