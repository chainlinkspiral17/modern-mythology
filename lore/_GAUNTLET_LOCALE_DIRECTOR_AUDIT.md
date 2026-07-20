# GAUNTLET LOCALE DIRECTOR PASS · AUDIT + FINDINGS
### per-space first-person camera/background wiring · 2026-07-20

Verify pass over all 23 gauntlet locations: does every board space a
scenario can move you to resolve to a first-person vantage, or does it
fall back to the top-down map?

Reusable checker: `godot/tools/audit_gauntlet_locales.py` (exit 1 on
gaps, so it can gate CI). It cross-checks each location's board spaces
against the FP render's four tiers (see
`TarotGauntletGame._render_current_space`):
1. **HOST 3D** — `scripts/<Locale>GauntletHost.gd` `SPACE_MAP`
2. **STANDALONE 3D** — `TarotGauntletGame._STANDALONE_SPACE_VANTAGES`
   + a `_LOCATION_SCENE_PATHS` entry to load the locale `.tscn`
3. **painted PNG** — `assets/gallery/locations/<loc>_fp_<space>.png`
4. **top-down map** — the fallback we want to avoid

## RESULT · 20 of 23 fully wired

All twenty of these resolve every board space to an FP vantage (host
SPACE_MAP + standalone table both mirror the location board):

asylum_ward_c · bayou_lighthouse · carnival_lot · cathedral ·
christian_ice_co · courthouse_chamber · daigles_roadhouse ·
dambrosios · elicia_bungalow · frog_knows_best ·
lacombe_service_garage · le_roulant_casino · mixing_glass ·
parish_cemetery · riverboat_interior · roadside_chapel ·
simon_apartment · solenade_garden · static_drive_in ·
wgur_transmitter_shack

## THREE LOCATIONS DESYNCED · host built for an OLDER board

The root cause in all three: the location JSON's `spaces[]` were
**renamed / re-scoped** after the host's `SPACE_MAP` was authored, and
the host was never updated. The host still holds vantages for the
*old* space names (stale keys), so the *current* board spaces find no
camera and drop to top-down. This needs the 3D scene open to place
cameras meaningfully — an on-device director job, which is why this
pass was queued behind a playtest.

### ember_ash_office — 7/12 missing  (host houston_office.tscn ✓)
- MATCHED (4): desk, back_stair, cypress_beam, corner_across
- FIXED THIS PASS: `office_door` (host had it keyed `door` — same
  north office door; added an alias at the known-good coords).
- STILL MISSING (7): leaded_window, back_alley, warehouse_floor,
  kitchen_rough_in, salvage_piles, front_stair, sidewalk
- Stale host keys to retire/re-map: bourbon, chair, rotary_phone,
  voicemail, ac_window, crew_photo (desk props / décor, not board
  spaces).

### roberts_house — 9/12 missing  (host roberts_kitchen.tscn ✓)
- MATCHED (3): kitchen_table, front_hallway, front_door
- STILL MISSING (9): kitchen_faucet, kitchen_window, driveway,
  living_room, the_loom, back_hallway, the_tapestry, back_door, garden
- Stale host keys (13, an entirely older board): front_porch,
  living_couch, coffee_table, side_chair, kitchen_sink, casserole,
  back_porch, bedroom_door, front_yard, curb, back_yard_fence,
  hall_table, phone_niche. Some map cleanly (kitchen_sink≈
  kitchen_faucet, living_couch≈living_room) — confirm on-device.

### the_hierophant_circuit — 11/11 missing  (the biggest gap)
- MATCHED (0). The board became a **five-venue circuit** (church →
  the black car → D'Ambrosio's → park bandstand → old armory →
  riverfront); the host's 18 SPACE_MAP keys are an *old single-church*
  board (church_plaza, church_doors, bandstand_*, path_*, sidewalk_*).
- CURRENT board spaces needing vantages: church_interior,
  church_steps, the_black_car, dambrosios_curb, dambrosios_dining_room,
  table_17, dambrosios_kitchen, back_corridor, park_bandstand,
  old_armory, riverfront.
- FIXED THIS PASS (data/naming bugs, correct regardless of cameras):
  - `_LOCATION_SCENE_PATHS` gained `the_hierophant_circuit` →
    `hierophant_circuit.tscn` (was absent — runtime `_location_id` is
    `the_hierophant_circuit`, with the "the_"; standalone FP could
    never find the scene).
  - `_BGM_BY_LOCATION` key `hierophant_circuit` → `the_hierophant_circuit`
    (was a dead key; the circuit played no ambient).
- The 11 circuit vantages need bespoke authoring — its `pos_xy` board
  is a schematic spanning five venues, NOT a metric floor plan, so it
  can't be derived; place cameras with the scene open.

## WHY THE CAMERAS WEREN'T AUTO-FILLED

The locale `.tscn` files are single GLB interiors with no per-space
marker nodes, and the desynced boards' `pos_xy` don't linearly map to
the hand-tuned Blender vantages (ember's Y-fit is degenerate;
hierophant's board isn't metric). Fabricating coordinates blind risked
cameras clipping walls or facing the wrong way — worse than an honest
top-down fallback. The correct fix is to open each scene and place the
missing vantages, then mirror them into `_STANDALONE_SPACE_VANTAGES`.

## ADJACENT FINDING · two more dead BGM keys

`_BGM_BY_LOCATION` also has dead keys `riverboat` (should be
`riverboat_interior`) and `anya_bungalow` (should be `elicia_bungalow`)
— those two locations currently play no ambient. Left for
confirmation; not touched this pass.

## ON-DEVICE AUTHORING CHECKLIST (per desynced location)

1. Open the locale `.tscn`, walk to each missing board space.
2. Note the FP camera Blender X/Y + facing yaw (0=+X east, 90=+Y north).
3. Add `"space_id": [x, y, yaw],` to the host `SPACE_MAP`.
4. Mirror the same block into `_STANDALONE_SPACE_VANTAGES[loc_id]`.
5. Retire the stale keys listed above.
6. Re-run `python3 godot/tools/audit_gauntlet_locales.py` → expect
   "all N spaces FP-wired" for that location.
