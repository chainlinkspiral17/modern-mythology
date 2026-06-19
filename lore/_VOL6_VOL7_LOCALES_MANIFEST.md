# Vol 6 + Vol 7 · 3D Locales Manifest

What needs to be built (Blender → GLB → Godot scene) for vol 6
(Planned Community / HCE) and vol 7 (Land of Milk and Honey /
Smolvud) per the locale pipeline established by vol 5.

The asset pipeline per locale is:
  · `godot/tools/blender/locales/build_<name>.py` — Blender Python
    builder that emits `<name>.glb` to `godot/assets/3d/locales/`
  · `godot/scenes/locales/<name>.tscn` — Godot scene that wraps
    the GLB with the standard PostProcess stack + practicals +
    hidden hero
  · `Background3D.CAMERA_PRESETS[<id>]` entry — establishing-shot
    camera for VN bg use via `"src": "3d:<id>"`
  · (optional) `godot/scripts/<Name>GauntletHost.gd` — gauntlet
    space-map → 3D position routing if the locale carries a board

Status legend: 🟢 done · 🟡 in progress · 🔴 not started · ⚪ stretch

---

## VOL 6 · PLANNED COMMUNITY (Harmony Creek Estates)

The volume's centre of gravity is the Harmony Creek
intersection: Kwik Stop ↔ NexCorp Gas & Go ↔ Cosmic Comics
clustered around the Phase I/II border. Plus the engineered
community itself.

### Adjacent infrastructure (high priority)

| Locale | Bg preset id | Status | Notes |
|---|---|---|---|
| **Kwik Stop interior** | `kwik_stop_interior` | 🟢 | Sam's register. Hot Pockets, wire basket, back-cooler infinite-reflection motif. Counter NE, beer cooler N, snack aisles middle, coffee/slurpee W, magazines + ATM near south entrance |
| **NexCorp Gas & Go interior** | `gas_go_interior` | 🔴 | Skip's shift. Locker #4 (combo is Skip's ex-wife's birthday backward). Across the intersection from Kwik Stop |
| **Cosmic Comics interior** | `cosmic_comics_interior` | 🔴 | Rick's shop. Phone ledger, photocopier (where Maya's *NEWS FROM HARMONY CREEK* runs), DO NOT SORT YET pile, Henderson Donation boxes (surviving *Glitch Report* issues) |
| **HCE intersection exterior** | `hce_intersection` | 🔴 | Establishing wide shot — Kwik Stop one corner, NexCorp Gas & Go opposite, the Phase I roofline behind. Streetlight + truck-cab silhouettes |

### Harmony Creek Estates (the engineered community)

| Locale | Bg preset id | Status | Notes |
|---|---|---|---|
| **HCE Phase I street** | `hce_phase1_street` | 🔴 | The 1991 lots. Connie Daigle (Lot 7), Mrs. Pimentel (Lot 14). Bermuda lawns, the welcome arch |
| **HCE Phase II buildout** | `hce_phase2_street` | 🔴 | New homes under occupancy. Carl Reno's welcome breakfasts at Lot 28. Same materials as Phase I but slightly off |
| **HCE Phase III dirt** | `hce_phase3_dirt` | 🔴 | Surveying flags, Norman Lott's modular trailer, the "historic significance" stake markers. Pre-construction |
| **Model home interior · Lot 47** | `hce_lot47_model_interior` | 🔴 | The fake basil pot in the kitchen. Staged everything. Carla Vega lives three doors down |
| **892 Ashberry Drive** | `ashberry_892_interior` | 🔴 | Empty house Maya's been watching for a year. Holding-company owned, maintained, unoccupied. *zine #19* documents it |
| **HOA welcome office + community pool** | `hce_hoa_office` | 🔴 | Mrs. Pimentel's welcome table. Pool nearby. The Carl Reno breakfast happens here Sunday morning |

### Cross-volume locations (vol 5 reused, mostly aged forward)

| Locale | Status | Notes |
|---|---|---|
| **Cathedral of Rust & Code** (vol 5) | 🟢 | Already built. By vol 6 has begun inverting from warehouse-cathedral to cathedral-warehouse. Same tscn, may want a vol6_aged variant |
| **D'Ambrosio's** (vol 5) | 🟢 | Diner still there. John's column corner. Maya's letters to F.T. drop here |
| **Halsey Studios** | 🔴 | Regional recording studio. Gallatin Band records there. Live-room + control-booth + the master-tape archive shelves |

---

## VOL 7 · LAND OF MILK AND HONEY (Smolvud, Oregon coast)

Smolvud is a town. The scope is bigger than vol 6's HCE
intersection — it's a whole settlement with interconnected
shops + the lighthouse + the cannery + the road out.

### The Cypress Street corridor (Lena's daily geometry)

| Locale | Bg preset id | Status | Notes |
|---|---|---|---|
| **Daily Grind interior** | `daily_grind_interior` | 🔴 | Lena's morning coffee shop job. Mrs. Gable's morning seat. Per's regular table. Probably has a back-room office + counter + 4-5 small tables |
| **Salty Tome bookstore** | `salty_tome_interior` | 🔴 | Petra's shop. Tide charts, local zines, John Frank's *Frequency Beneath*. Lena's apartment is upstairs |
| **Lena's apartment (above Salty Tome)** | `lena_apartment` | 🔴 | The writing desk where *Static Truths* gets laid out. Window over Cypress St. The SUN charcoal mark won't wash off |
| **Board Lords skate shop** | `board_lords_interior` | 🔴 | Kai's shop. Was Wagner's Hardware once, was nothing for 3 years, is now Board Lords. Skate gear + zine wall + Kai's permanent perch on the counter |
| **Pizza Pirate** | `pizza_pirate_interior` | 🔴 | Sal Carratura's place since 1991. The SCUMM Machine in the back hallway (custodian since '07). Cabinet + dim hallway lights + the booth seating |
| **Cypress Street exterior** | `cypress_street_exterior` | 🔴 | Establishing daytime + nighttime variants. Salty Tome + Pizza Pirate + Board Lords all on one block |

### Beyond the town

| Locale | Bg preset id | Status | Notes |
|---|---|---|---|
| **Smolvud lighthouse** | `lighthouse_exterior` | 🔴 | The crow Mrs. Gable sees every morning for 9 years. May or may not be Aria's. Lighthouse cliff + path + the crow's perch |
| **Smolvud library back room** | `library_archive` | 🔴 | Mrs. Gable's anomalous-frequency archive. Out-of-circulation. Boxes of Glitch Report issues. The vol6 *NEWS FROM HARMONY CREEK* zines live here too |
| **Alsea Bay Cannery basement** | `cannery_basement` | 🔴 | The servers Finn inspects at low tide. Pilings + the substrate's most direct vol7 contact point. Cold, damp, lit by the off-band radio |
| **The lighthouse interior** ⚪ | `lighthouse_interior` | ⚪ | Stretch — if/when Lena goes up |

### Cross-volume locations

| Locale | Status | Notes |
|---|---|---|
| **Cathedral of Rust & Code** (very aged) | 🟢 | Already built. By vol 7 Frasier is near end-of-life; the inversion is complete. May want a vol7_dust variant — same geometry, different lighting + mood-strata curation |
| **HCE remains** ⚪ | ⚪ | Stretch — the Phase III dirt may still exist as a ghost zone in vol 7 |

---

## Pipeline — adding a new locale

The pattern, after building one, is replicable in ~600-800 lines
of Blender Python per locale plus ~250 lines of `.tscn`:

1. **Builder** — `godot/tools/blender/locales/build_<name>.py`.
   Copy the bungalow or kwik_stop builder as a template:
     · `clear_scene()`, `make_box`, `make_cyl` helpers
     · One function per zone (e.g. `build_counter`, `build_aisles`)
     · `build_shell()` for the floor / walls / ceiling
     · `export_glb()` at the end pointing at
       `godot/assets/3d/locales/<name>.glb`
   Run via `./run_cathedral.sh build_<name>.py`.

2. **Scene** — `godot/scenes/locales/<name>.tscn`. Copy the
   `kwik_stop.tscn` as a template (cleanest reference):
     · Full PostProcess shader stack
     · Three-light foundation + practicals
     · WorldEnvironment with locale-appropriate fog + glow
     · Hidden hero GLB if locale has a canonical occupant POV
     · Floor collider sized to the locale's footprint
     · Optional `default_style_pack` on the PostProcess node

3. **Bg preset** — add an entry to `Background3D.CAMERA_PRESETS`
   in `godot/scripts/vn/Background3D.gd`:
     · `scene` — path to the .tscn
     · `requires_glb` — path to the .glb (for graceful fallback)
     · `camera_origin`, `camera_rotation`, `fov` — establishing
       shot vantage
     · `suppress_input: true` — strip Player + CanvasLayers so
       the bg is non-interactive

4. **(Optional) Gauntlet host** — if the locale carries a board,
   add `godot/scripts/<Name>GauntletHost.gd` mirroring
   `DinerGauntletHost.gd`. Map each `<location>.json` space to
   Blender XY + facing-yaw.

## Asset costs (rough estimates)

Each locale:
- Builder: 1-2 hours to draft, 30 min to iterate
- GLB build: 10-30 seconds Blender runtime
- Scene wiring: 30 min copy + retune
- Bg preset: 5 min
- Gauntlet host (optional): 30 min

So a fully wired locale is 2-4 hours of work + the per-character
hero GLBs they reference.

## What's needed NEXT

To unblock the Sam-at-Kwik-Stop test:
- ✅ Kwik Stop builder + .tscn + bg preset (this commit)
- ✅ Sam Miller registry entry in CharLayer + uploader (prior commit)
- ⏳ `sam_miller.glb` model authored + dropped into
  `godot/assets/3d/characters/heroes/`
- ⏳ Run `./run_cathedral.sh build_kwik_stop.py` on the Deck to
  materialise the locale GLB

Once those land, `vol6_ch15_kwik_stop` (or any new VN scene with
`"src": "3d:kwik_stop_interior"`) will render the 3D Kwik Stop
with Sam's portrait wired through the standard pipeline.

After Kwik Stop verifies the end-to-end, the next high-value
build targets are: **NexCorp Gas & Go** (Skip), **Cosmic Comics**
(Rick + Maya's photocopier), and **Daily Grind** (Lena's morning
job — vol 7 anchor).
