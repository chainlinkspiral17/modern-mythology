# Sound-effects audit

Full inventory of every audio slot the project's current systems
need, keyed by game / act / moment. Each row lists either:

- **preset:** a name that already exists in `slowstick_synth.py`'s
  `SFX_PRESETS`, ready to render immediately
- **compose:** a JSON composition slot (BGM loop)
- **new:** an SFX not yet authored · a preset needs to be added
  to `slowstick_synth.py`
- **defer:** authorial intent captured but no wire-up yet

Notation: `[status]` `slot-path` — description. The `slot-path`
is where the WAV would live under `godot/assets/audio/` when the
tool renders it.

---

## ESTUARY 3 · Vol 7 gallery slowstick

### Act 1 · The Shift (Kwik Stop, twelve nights)

- [preset]  `sfx/e3/act1/register_ding.wav` — Register operate. Uses `register_ding`.
- [preset]  `sfx/e3/act1/cooler_whoosh.wav` — Cooler open. Uses `cooler_whoosh`.
- [preset]  `sfx/e3/act1/broom_sweep.wav` — Broom sweep. Uses `broom_sweep`.
- [preset]  `sfx/e3/act1/phone_ring.wav` — Phone rings on scheduled turns. Uses `phone_ring`.
- [preset]  `sfx/e3/act1/door_open.wav` — Backroom door (night 12 turn 14). Uses `door_open`.
- [preset]  `sfx/e3/act1/fluorescent_start.wav` — Night 1 boot ambience. Uses `fluorescent_start`.
- [preset]  `sfx/e3/act1/verb_select.wav` — SCUMM verb button click. A soft blip.
- [preset]  `sfx/e3/act1/turn_tick.wav` — Every 40s turn advance. A low woody click.
- [preset]  `sfx/e3/act1/customer_bell.wav` — Store door bell on customer arrival. Small ding.
- [preset]  `sfx/e3/act1/radio_static.wav` — Static burst when tuning between stations.
- [preset]  `sfx/e3/act1/radio_889_bed.wav` — 88.9 NPR voice-under bed loop. Per-station audio.
- [preset]  `sfx/e3/act1/radio_1150_bed.wav` — 1150 AM fishing-report loop.
- [preset]  `sfx/e3/act1/radio_1600_static_voice_night_5.wav` — The night-5 static voice.
- [preset]  `sfx/e3/act1/radio_1600_static_voice_night_12_sam.wav` — Night 12 "sam." · the game's most authored radio beat.
- [rendered] `bgm/e3/act1/kwik_stop_hum.wav` — 59Hz fluorescent underscore. Authored: `estuary_3_kwik_stop_hum.json`.
- [rendered] `bgm/e3/act1/night_12_still.wav` — Ambient variant for night 12 (the fluorescent stops flickering).
- [preset]  `sfx/e3/act1/2am_customer_stands_up.wav` — Chair scrape + footsteps on night 12 turn 14. The transition sound.

### Act 2 · The Estuary (four seasons + second spring)

- [preset]  `sfx/e2/act2/control_click.wav` — Any tide-gate / buffer / species button click.
- [preset]  `sfx/e2/act2/season_settle.wav` — SETTLE THE SEASON button. A soft resolve chord.
- [preset]  `sfx/e2/act2/season_success.wav` — Season success narration reveal. A gentle chime.
- [preset]  `sfx/e2/act2/season_failure.wav` — Season failure narration reveal. A slightly bent low tone.
- [preset]  `sfx/e2/act2/tide_gate_toggle.wav` — Wet-metal ratchet sound when the tide gate shifts.
- [preset]  `sfx/e2/act2/tide_pool_splash.wav` — Weather beat (e.g. algal bloom). Uses `tide_pool_splash`.
- [preset]  `sfx/e2/act2/wave_break.wav` — Season-transition foam.
- [preset]  `sfx/e2/act2/gull_cry.wav` — Occasional overlay during spring/summer seasons.
- [preset]  `sfx/e2/act2/heron_wingbeat.wav` — When the heron icon selected.
- [rendered] `bgm/e3/act2/estuary_spring.wav` — Spring underscore. Warm pad + light arp.
- [rendered] `bgm/e3/act2/estuary_summer.wav` — Summer underscore. More activity.
- [rendered] `bgm/e3/act2/estuary_fall.wav` — Fall underscore. Windier, hollower.
- [rendered] `bgm/e3/act2/estuary_winter.wav` — Winter underscore. Sparse.
- [rendered] `bgm/e3/act2/estuary_second_spring.wav` — The reprise. Brighter than spring 1.

### Act 3 · The Town (Labor Day walkabout)

- [preset]  `sfx/e3/act3/tile_hover.wav` — Hover on a location tile.
- [preset]  `sfx/e3/act3/tile_enter.wav` — Click a location tile. Small transition.
- [preset]  `sfx/e3/act3/hotspot_look.wav` — LOOK verb reveal.
- [preset]  `sfx/e3/act3/hotspot_talk.wav` — TALK verb reveal.
- [preset]  `sfx/e3/act3/hotspot_use.wav` — USE verb reveal.
- [preset]  `sfx/e3/act3/key_in_lock.wav` — Bookstore key. Consider new preset — for now `door_open` fits.
- [preset]  `sfx/e3/act3/clock_tick.wav` — Optional 15-min clock advance.
- [preset]  `sfx/e3/act3/return_to_shop.wav` — The bell over the Kwik Stop's door on return.
- [rendered] `bgm/e3/act3/town_morning.wav` — Morning walkabout underscore. Slightly warmer than Act 2's landscape.
- [rendered] `bgm/e3/act3/town_dusk.wav` — Return-to-Kwik-Stop underscore (clock >= 18:00).

### Act 4 · The Fifth Season (rhythm-drawing on the beach)

- [rendered] `bgm/e3/act4/beach_loop.wav` — Marc Ostrom's 8-bar 72 BPM ambient. Authored: `estuary_3_act4_beach_loop.json`.
- [preset]  `sfx/e3/act4/stick_scratch.wav` — Every rhythm press. Uses `stick_scratch`.
- [preset]  `sfx/e3/act4/press_hit.wav` — On-beat press acknowledgment. Soft warm click.
- [preset]  `sfx/e3/act4/press_miss.wav` — Out-of-window press. Small negative tick.
- [preset]  `sfx/e3/act4/tide_pool_splash.wav` — When line crosses a tide pool. Uses `tide_pool_splash`.
- [preset]  `sfx/e3/act4/creature_arrival_heron.wav` — Heron appears.
- [preset]  `sfx/e3/act4/creature_arrival_otter.wav` — Otter appears.
- [preset]  `sfx/e3/act4/creature_arrival_crab.wav` — Crab appears.
- [preset]  `sfx/e3/act4/creature_arrival_fry.wav` — Cutthroat fry appear.
- [preset]  `sfx/e3/act4/creature_arrival_2am_customer.wav` — Wind on the dune ridge at bar 32.
- [preset]  `sfx/e3/act4/creature_arrival_kid_on_bike.wav` — Bike gear-shift at bar 48.
- [preset]  `sfx/e3/act4/tide_swallow.wav` — Slow whoosh as the tide reaches the line. One-shot at end.
- [preset]  `sfx/e3/act4/signing.wav` — Sam signs the drawing. A soft final scratch.

### Ending

- [rendered] `bgm/e3/ending/quiet.wav` — Credits underscore. Very sparse.
- [preset]  `sfx/e3/ending/page_turn.wav` — Between epilogue / credits / quiet views.

---

## SLOWSTOCK SHELF · library UI

- [preset]  `sfx/shelf/cartridge_hover.wav` — Hover on a cartridge.
- [preset]  `sfx/shelf/cartridge_click.wav` — Click a locked cartridge (soft denial) OR unlocked (crisp positive).
- [preset]  `sfx/shelf/boot.wav` — BOOT button pressed. A cartridge-being-inserted click.
- [preset]  `sfx/shelf/back_to_shelf.wav` — Return from a stick. Could use `door_open` or a new preset.
- [preset]  `sfx/shelf/unlock_chime.wav` — When a new wave unlocks. A short bright chord.
- [rendered] `bgm/shelf/cabin_ambient.wav` — The cabin's living-room ambience when the shelf is open. Very quiet.

---

## COMMUNITY PLANNED · Vol 6

The CP audio pass shipped earlier this arc (`43. completed · Audio
pass · CP BGM + Wave-2 gauntlet BGM`). Confirming what's in place:

- [existing] `bgm/cp/regular_days.ogg` — the day-loop BGM
- [existing] `bgm/cp/vol5_warehouse_drone.ogg` — W13-W14 storm-window override

New CP audio the demon-depth arc calls for:

- [preset]  `sfx/cp/tier_crossing_hungry.wav` — When a demon crosses steady → hungry.
- [preset]  `sfx/cp/tier_crossing_restless.wav` — Hungry → restless.
- [preset]  `sfx/cp/tier_crossing_close.wav` — Restless → close_to_turning.
- [preset]  `sfx/cp/tier_crossing_turned.wav` — Close → turned. The most dramatic of the four.
- [preset]  `sfx/cp/basement_rite.wav` — When THE_BASEMENT visit reduces corruption. A soft resolve.
- [preset]  `sfx/cp/pair_warm.wav` — Warm demon-pair or human-pair interaction fires.
- [preset]  `sfx/cp/pair_loud.wav` — Loud pair (moth + starling, cicada + starling, JF + Mackenzie).
- [preset]  `sfx/cp/pair_cold.wav` — Cold pair (Husk + others, Jules driving to HC).
- [preset]  `sfx/cp/marker_set.wav` — When a consequence marker is set on a stage choice.
- [preset]  `sfx/cp/marker_expire.wav` — When a marker expires (softer).
- [preset]  `sfx/cp/quiet_week.wav` — When a human's home-streak triggers obligation −1.
- [preset]  `sfx/cp/roster_loud.wav` — The three-hungry-demons interlude fires.
- [preset]  `sfx/cp/interlude_earned.wav` — When an interlude lands on the shelf.
- [preset]  `sfx/cp/labor_day_arrival.wav` — Day 100 chime.

---

## TAROT GAUNTLET · Vol 5

The Wave-2 gauntlet BGM pass earlier this arc covered the primary
locale loops. Follow-up audio the current systems need:

- [preset]  `sfx/gauntlet/card_flip.wav` — Any card reveal.
- [preset]  `sfx/gauntlet/card_place.wav` — Placing a card on a locale hotspot.
- [preset]  `sfx/gauntlet/hand_deal.wav` — Dealing a new hand.
- [preset]  `sfx/gauntlet/threshold_cross.wav` — Named-threshold crossing (per Wave-2 hand JSONs).
- [preset]  `sfx/gauntlet/visitor_arrive.wav` — Named visitor enters the locale.
- [preset]  `sfx/gauntlet/lore_token_reveal.wav` — Lore token added to the scrapbook.
- [preset]  `sfx/gauntlet/scrapbook_open.wav` — Opening the scrapbook.
- [preset]  `sfx/gauntlet/scenario_unlock.wav` — When CP → Gauntlet crossover fires.
- [preset]  `sfx/gauntlet/scenario_picker.wav` — Ctrl+F8 overlay open.
- [preset]  `sfx/gauntlet/win_chord.wav` — Scenario win.
- [preset]  `sfx/gauntlet/loss_thud.wav` — Named-loss condition.

---

## SHARED · engine + menu

- [preset]  `sfx/ui/menu_open.wav` — Any modal open.
- [preset]  `sfx/ui/menu_close.wav` — Any modal close.
- [preset]  `sfx/ui/button_hover.wav` — Universal hover chirp.
- [preset]  `sfx/ui/button_click.wav` — Universal click.
- [preset]  `sfx/ui/save_confirm.wav` — Save-slot save confirm.
- [preset]  `sfx/ui/load_start.wav` — Save-slot load start.
- [preset]  `sfx/ui/notification.wav` — Any non-critical notification (interlude earned, achievement, etc.).

---

## Totals

By status:

| status  | count |
|---------|-------|
| existing (already in repo) | 2 |
| preset (render now)        | 8 |
| compose (BGM to author)    | 15 |
| new (SFX preset to add)    | 63 |
| defer                       | 8 |
| **TOTAL slots**            | **96** |

## Development order

Suggested waves to unblock the most gameplay per commit:

1. **Wave A (shelf + Estuary 3 core loop).** Render every existing
   preset to `godot/assets/audio/`. Author the missing UI SFX
   (`verb_select`, `turn_tick`, `customer_bell`, `control_click`,
   `season_settle`, `tile_hover`, `tile_enter`, `press_hit`,
   `press_miss`, `cartridge_hover`, `cartridge_click`, `boot`).
   Ten new presets. Render + wire into the existing controllers.
   → Estuary 3 becomes audibly complete.

2. **Wave B (Act 2/3 BGM).** Compose the four estuary-seasonal
   loops + second-spring reprise + town-morning + town-dusk. Seven
   JSON compositions. Render + wire.
   → Estuary 3 has a full musical bed.

3. **Wave C (CP demon-depth SFX).** The fourteen CP-specific SFX
   from the demon-depth arc. Adds audio texture to the invisible
   corruption economy the player is asked to read.

4. **Wave D (Gauntlet + shared UI).** Card-flip, card-place, hand-
   deal, menu-open/close, etc. Cross-cuts every mode.

5. **Wave E (radio beds + creature arrivals).** The deferred
   authored-per-line moments · Act 1 radio programs, Act 4
   creature-specific sounds.

## Adding a new preset

1. Write a function `sfx_<name>(sr)` in `slowstick_synth.py`
   that returns a float sample list.
2. Register it in `SFX_PRESETS`.
3. Run `python3 slowstick_synth.py sfx <name> godot/assets/audio/...`
4. Reference the WAV from a Godot `AudioStreamPlayer`.

## Adding a new composition

1. Copy an existing JSON in `compositions/` as a template.
2. Author bars/beats/pitches.
3. Run `python3 slowstick_synth.py compose <path>`.
4. Reference the WAV.

## Rendering everything at once

```bash
# All SFX presets
python3 godot/tools/audio/slowstick_synth.py sfx all godot/assets/audio/sfx/

# All authored compositions (loop over the directory)
for f in godot/tools/audio/compositions/*.json; do
  python3 godot/tools/audio/slowstick_synth.py compose "$f"
done
```
