# Vol7 — art manifest

*The list of background images and CG cards vol7 scenes
now reference. Generated from a sweep of vol7 scene JSONs
after splitting locations out of the generic cabin/road bgs
and adding CG nodes at canonical narrative beats.*

---

## New background locations

These paths are referenced by `bg` directives in vol7 scenes but
don't have art yet. Each row: target path · scenes that use it ·
prose hook (what the location looks like in the writing).

### The Tower at Old-Yachats (ch21–22)

| path | scenes | hook |
|---|---|---|
| `assets/backgrounds/vol7_101_to_yachats.jpg` | `vol7_ch22_drive` | The drive up 101 from Smolvud to old-Yachats — forty-three miles. Coastal stretch Tem hasn't driven in her adult life. |
| `assets/backgrounds/vol7_old_yachats_arrival.jpg` | `vol7_ch21_tower`, `vol7_ch22_drive` | Arrival at old-Yachats. Tower seen from outside. |
| `assets/backgrounds/vol7_tower_lobby.jpg` | `vol7_ch22_floors` | The lobby. Polished cedar floor. Cedar paneling walls. Twelve-foot ceiling. Reception desk. |
| `assets/backgrounds/vol7_tower_stairs.jpg` | `vol7_ch22_portal` | Stairs up through the Tower's floors. Cedar throughout. |
| `assets/backgrounds/vol7_tower_portal_room.jpg` | `vol7_ch22_portal` | The fourth floor, the portal room. Unmarked cedar door. Window at chest height, six inches by six. |

### The slow-stick excursion (ch18)

| path | scenes | hook |
|---|---|---|
| `assets/backgrounds/vol7_bakery_back_alley.jpg` | `vol7_ch18_stick` | Eight-twelve at the back door of Hans's bakery. The Sunday-afternoon cast dispersing. |
| `assets/backgrounds/vol7_cale_truck_back_alley.jpg` | `vol7_ch18_stick` | Cale's truck parked in the back alley behind the bakery. The stick-handover moment. |

### Estuary 7 (epilogue)

| path | scenes | hook |
|---|---|---|
| `assets/backgrounds/vol7_estuary_7_planner_view.jpg` | `vol7_epilogue_gallery`, `vol7_epilogue_submission` | Estuary 7 at planner's-view. The river coming down from the cedars. The bar of sand at the mouth. The flats. The bluff. The forested ridge. The substrate held it for fifty-five years. |

---

## New CG cards

CG nodes inserted at canonical big moments in vol7. Each card is a
full-screen image with a caption. The engine fires a CG card when
the scene hits a `{"t":"cg","src":...,"caption":...}` directive —
they're punctuation marks in the prose, not ambient bgs.

| path | scene | beat |
|---|---|---|
| `assets/cg/vol7_box_of_three_sticks.png` | `vol7_ch6_the_stick` | Three sticks in the wooden box. Third labeled in Cale's careful hand: **ESTUARY 7 — INES ROCHA 2046**. Named for the first time. |
| `assets/cg/vol7_smolvud_alley_night.png` | `vol7_ch16_eight` | Hemlock at night. The bookstore. The alley. Smolvud, Saturday. The procession to the back-room party. |
| `assets/cg/vol7_four_bowls_cedar.png` | `vol7_ch17_aria` | The cedar bowl. Spiral on the outside. The size of two cupped hands. Tem hands it to Aria. |
| `assets/cg/vol7_olafs_bell.png` | `vol7_ch19_cedar` | Olaf's bell. Cedar. Carved with the spiral his son will later set in the bowl. |
| `assets/cg/vol7_cabin_door_302am.png` | `vol7_ch20_door` | The cabin door at 3:02 AM. A figure on the porch in the rain. The second knock. |
| `assets/cg/vol7_the_form.png` | `vol7_ch20_each` | The form the figure resolves to. Each of them sees something different. |
| `assets/cg/vol7_the_wall_milk_crate.png` | `vol7_ch20_wall` | The wall. Lena's milk crate at its foot. September 1, six-thirty AM. |
| `assets/cg/vol7_floured_hand_on_face.png` | `vol7_ch21_cabin` | Hans's floured baker's hand on Tem's face. Sunday morning, every Sunday morning. |
| `assets/cg/vol7_tower_portal_door.png` | `vol7_ch22_portal` | The portal-room door. Cedar. Window at chest height, six inches by six. |
| `assets/cg/vol7_estuary_7_opening.png` | `vol7_epilogue_gallery` | Estuary 7 at planner's-view. The river coming down from the cedars. |
| `assets/cg/vol7_blank_template.png` | `vol7_epilogue_submission` | The blank template. The river. The bar of sand. The flats. The bluff. The forested ridge. |
| `assets/cg/vol7_freq_interlude_ii.png` | `vol7_interlude_ii` | Frequency interlude II. The minute Finn's radio goes quiet. |

---

## What's still missing

Locations the prose names that don't yet have their own bg path
(currently still using the generic cabin / road bgs):

- **The Daily Grind** — Lena's workplace, named throughout vol7. Currently using `vol8_daily_grind.jpg`. Once that file exists it's fine; only the naming convention (vol7 vs vol8) needs reconciling.
- **The Salty Tome** — Petra's bookstore. Currently using `vol8_bookstore.jpg`. Same naming reconciliation.
- **ChillWave** — Cale's shop. Currently using `vol8_chillwave.jpg`. Same.
- **Hans's bakery interior** (front, not the back alley) — Currently using `vol8_hans_bakery.jpg`. Same.
- **The cabin loft** — the mattress, Eddvard's '79-onward bed (ch15_loft). Currently reusing `vol8_cabin_interior.jpg`. Probably warrants its own loft-specific view.
- **The Missing Link** — Finn's drinking hole (ch16_aud, ch9_evening). Currently using `vol8_missing_link.jpg`. Naming reconciliation.
- **Board Lords** — Kai's skate shop (ch5_roy, ch9_tuesday, ch10_per, ch12_kai, ch16_shop). Currently using `vol8_board_lords.jpg`. Naming reconciliation.
- **Cape Perpetua** — drive vista (ch12_morning). Currently using `vol8_cape_perpetua.jpg`. Naming reconciliation.

The "vol8_" prefix on these existing references is a leftover from
when this volume was being numbered differently. Recommend a future
pass to rename `vol8_*` to `vol7_*` and update the scene JSONs in
lockstep — the new bgs added by this manifest already use `vol7_`.

---

## CG nodes the prose suggests but I didn't add yet

These are also strong CG-worthy moments; flagged for a second pass:

- **The hexagon completing** (ch12_lena) — "The hexagon was complete. The crow was speaking. The figure had been on the stack." Could be a single CG card showing all three in a tight composition.
- **The drones at the bluff** (ch2_morning) — "The drones came in off the bluff in the last hour before dawn." Opening image of Land of Milk & Honey, deserves a CG.
- **The painting** (ch14_painting) — Petra's canvas. The cedar from the milk crate. Named object.
- **Aria — Three twenty-two** (ch18_home) — the shirt pocket, the thing inside. Held back; the exact reveal isn't on-page yet.
- **Brandon T. on the second floor** (ch22_floors) — the Tower's named occupant. Could be a CG when he's revealed.

---

*To author each asset, generate the image at standard scene-bg
dimensions (recommend 1920×1080 for bgs, same or larger for CGs
since they're full-screen). Drop the resulting files at the target
paths listed above. Godot reimports on next launch.*
