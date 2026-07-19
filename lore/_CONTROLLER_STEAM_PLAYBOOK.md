# CONTROLLER + STEAM MACHINE PLAYBOOK

Full-package controller support and the Steam Machine build.
Read this before touching input handling, adding a new UI surface,
authoring haptics, or cutting a build.

Baseline device: the **2026 Steam Controller**. Steam Input
presents it as a standard SDL gamepad; its HD haptic motors render
SDL rumble, so one rumble path covers Steam Controller, Steam
Deck, and ordinary XInput pads. Its trackpads give us a guaranteed
mouse fallback at the Steam Input layer — but the native goal is
that nobody needs it.

## Core rules

1. **One path per input, never two.** The package's ~60 surfaces
   read raw keycodes (`KEY_ESCAPE`, arrows, E/J) and mouse clicks.
   `GamepadMgr` (autoload) translates pad input into those same
   events instead of adding parallel handlers. The moment an input
   can arrive twice (a joypad binding on an action AND a
   synthesized key that triggers the same action), something
   double-fires. That is why:
   - `menu_back`'s direct joypad-B binding was REMOVED from
     project.godot — B becomes a synthesized ESC (one path).
   - Button synthesis happens in `_unhandled_input`, so a Control
     that consumed the button (AcceptDialog closing on ui_cancel's
     built-in B) suppresses the synth.
   - Arrow synthesis stands down while any Control has UI focus —
     Godot's default `ui_*` joypad bindings already move focus,
     and synthesizing arrows (also bound to `ui_*`) would
     double-move it.
2. **Pad == keyboard, exactly.** Synthesized keys mimic real
   keyboard behavior including echo repeats (initial press, 0.28s
   delay, 0.12s echo repeats, release). If a surface behaves
   differently on pad vs keyboard, the synthesis is wrong, not the
   surface.
3. **Synthesized events carry `device == 97`** (`SYNTH_DEVICE`).
   Any code that must distinguish real from synthetic input checks
   that sentinel. GamepadMgr itself ignores device-97 events so it
   never reacts to its own output.
4. **The virtual cursor is the universal fallback, not the primary
   path.** Right stick moves it, RB/R3 click. It makes every
   mouse-only surface pad-playable with zero per-surface work —
   but W2/W3 work should keep ADDING native focus/hotkey paths so
   the common flows never need it. It hides after 3s idle and the
   instant a real mouse moves.
5. **Haptics ride the sound grammar.** `SFXBank.RUMBLE_MAP` keys
   rumble by SFX preset — any surface that plays a preset gets
   matched rumble for free, scaled by the preset's volume_ratio
   and by `Settings.haptics` (0–1, persisted). Explicit beats use
   `SFXBank.rumble(weak, strong, duration)`. Rules of thumb:
   - UI ticks: weak motor only, ≤0.16, ≤0.09s.
   - Rewards: weak-led, a little strong, 0.15–0.45s.
   - Impacts/losses: strong-led (loss_thud is 0/0.85/0.4 — the
     heaviest thing in the game, keep it that way).
   - Ambient beds, hover ticks, radio static: NO rumble. Mapping
     them is a bug; rumble spam is worse than none.
6. **New HUD/UI surfaces**: follow the F4 rule (CLAUDE.md) as
   always, and if the surface is mouse-only, it is automatically
   cursor-covered — but note it in the W3 inventory below so a
   native path can be added.

## The mapping (2026 Steam Controller reference)

| Pad                  | Becomes            | Where defined |
|----------------------|--------------------|---------------|
| A                    | advance / accept   | `advance` + `menu_select` actions (project.godot) + default `ui_accept` focus activation |
| B                    | ESC (synth)        | GamepadMgr → every `KEY_ESCAPE` handler + `menu_back` action via its ESC key binding |
| X                    | E (synth)          | interact — Pirate Summer et al |
| Y                    | J (synth)          | journal — Pirate Summer |
| View (back)          | F4 (synth)         | clean-screenshot HUD master toggle |
| Start                | skip               | `skip` action (rebound from LB to Start) |
| D-pad / left stick   | arrows (synth, focus-gated) | overworld movement, log scrolling; focus nav when a Control is focused |
| Right stick          | virtual cursor     | GamepadMgr CanvasLayer 120 |
| LB                   | TAB (synth)        | roster (PS), map (Basilica), VN skip |
| RB / R3              | left click while the cursor is active; otherwise RB → I (synth: PS duffel, Basilica tune-down) | GamepadMgr |
| Trackpads            | Steam Input mouse  | guaranteed fallback, no code |
| Gyro / grips / triggers | unbound — deliberate | triggers→Q/E rejected: Q hangs up the CP BBS + yaws the VN camera (graze hazard) |

## Steam Machine build

- Export preset: **SteamMachine** (`godot/export_presets.cfg`
  preset.5) — Linux/X11 x86_64, single binary, PCK embedded, no
  console wrapper, reference/voice junk excluded. Output:
  `<repo>/builds/steam_machine/ModernMythology.x86_64`
  (`builds/` is gitignored).
- Build:

  ```bash
  cd /home/deck/Downloads/modern-mythology && ./godot/tools/build_steam_machine.sh
  ```

  (Needs a Godot 4.6 binary — `GODOT_BIN=...` overrides discovery
  — and export templates installed once in the editor.)
- On the Steam Machine: Steam → **Add a Non-Steam Game** → browse
  to the binary. SteamOS applies the default gamepad template;
  everything above works with it. No per-game Steam Input config
  is required, but "Right Trackpad as Mouse" is the recommended
  extra.
- First run of an EXPORTED build with no settings.cfg defaults to
  **fullscreen** (Settings.gd checks `OS.has_feature("template")`).
  Editor/source runs keep the windowed dev default, so the Deck
  workflow is unchanged.
- Renderer is already `gl_compatibility` (Deck-first since day
  one) — the same build runs on the Machine's RDNA GPU with
  headroom to spare; there is no separate "optimized" renderer to
  maintain. Performance sweeps happen on the Deck, the weaker
  target.
- HD haptics beyond SDL rumble (the Steam Controller's per-event
  waveform API) require the Steam Input API via GodotSteam — a
  future upgrade, deliberately out of scope; the SDL rumble
  grammar is the baseline and works everywhere.

## Wave roadmap (arc status)

- **W1 — DONE 2026-07-19.** GamepadMgr autoload (synthesis + focus
  gate + virtual cursor), input-map fixes (skip→Start, menu_back
  joy stripped), SFXBank rumble grammar (~60 presets mapped),
  `Settings.haptics`, this playbook.
- **W2 — DONE 2026-07-19 (code side).** Initial focus lands
  automatically via `GamepadMgr.focus_first()` on: MainMenu,
  GalleryOverlay.open, ScenarioPicker, all four SpreadHost views,
  the CP slot picker, and the SlowstockShelf. VN ChoiceMenu
  already grabbed focus (audit finding — pad-native from day
  one). Stuck-focus auto-heal added to GamepadMgr: a
  mouse-clicked button that keeps focus would gate arrow synth
  off forever (killing overworld stick movement); holding a
  direction 0.6s with no focus movement now releases the orphan
  and movement resumes. DELIBERATE deferrals: the gauntlet board
  and GalleryOverlay's chapter-picker rows use FOCUS_NONE flat
  buttons — the virtual cursor covers them; native focus there
  is W3-adjacent polish, not a blocker. Needs ON-PAD
  verification (first real Steam Controller session).
- **W3 — DONE 2026-07-19 (code audit + fixes; on-pad verify
  pending).** Every stick's input handling audited for keys the
  synth doesn't cover, echo semantics, FOCUS_NONE buttons, and
  mouse-only surfaces. Fixes: LB→TAB and idle-RB→I added to
  GamepadMgr; NH heard-log and PMG ledger normalized to also
  accept J (the Y button); Basilica gains KEY_I as tune-down so
  the radio is tunable both ways on pad (X=up, RB=down).
  Deliberately NOT mapped: triggers→Q/E (Q hangs up the CP BBS
  and yaws the VN camera — graze hazard) and Wyrd's Z/C hex
  diagonals (the four orthogonal steps generate the whole hex
  lattice; diagonals are shortcuts).

  | Stick | Status | Notes |
  |-------|--------|-------|
  | pirate_summer | ✔ full | stick/d-pad walk (echo hold-to-walk matches keyboard), X interact, Y journal, LB roster, RB duffel, B closes |
  | estuary_1 | ✔ full | 1/2/3 gate hotkeys ALSO clickable levers → cursor; A advances week |
  | estuary_2 | ✔ full | pure buttons · focus nav |
  | estuary_3 (4 acts + manager) | ✔ cursor | Planner/KwikStop/Walkabout use FOCUS_NONE buttons + drawn surfaces by design → virtual cursor; shelf has initial focus |
  | northwind_harbor | ✔ full | Y (J) toggles the heard log (normalized from H-only) |
  | basilica_of_wires | ✔ full | arrows turn/step (echo-filtered steps = press-per-step, matches keyboard), LB map, X/RB tune ±25; A/D fine-tune stays keyboard-only |
  | sweetgum | ✔ cursor | one drawn gui_input surface |
  | riffmaster_melody_club | ✔ cursor | one drawn gui_input surface |
  | hane_no_niwa | ✔ cursor | one drawn gui_input surface |
  | patient_mister_glass | ✔ full | Y (J) toggles the ledger (normalized from L-only) |
  | fey_faire | ✔ full | buttons + focus; KP_ENTER alt-accept harmless |
  | earthman_chronicles | ✔ full | buttons + focus; KP_ENTER alt-accept harmless |
  | kwik_stop_manager | ✔ full | pure buttons + checkboxes · focus nav |
  | sams_summer_shifts | ✔ full | pure buttons · focus nav |
  | sisters_wyrd | ✔ full | d-pad hex steps (press-per-step); Q/E/Z/C diagonals keyboard-only by design |

- **W4 — DONE 2026-07-19.** SteamMachine export preset + build
  script + fullscreen first-run default.

## Recent lessons

### 2026-07-19 · the translation-layer decision

- **Translate at the edge, don't rewrite the middle.** Sixty
  surfaces of keycode+mouse handling would take weeks to port to
  actions. One autoload that synthesizes the keys and clicks they
  already understand made the whole package pad-playable in a
  day, and new surfaces inherit support by writing ordinary
  keyboard/mouse code.
- **Double-fire is the whole game.** Every controller bug in
  design review was some input arriving twice (action binding +
  synth, ui_cancel + ESC synth, ui_* focus + arrow synth). The
  three guards — strip duplicate bindings, synthesize from
  _unhandled_input, gate arrows on focus — exist to keep one
  path per input. Check all three before adding any binding.

### 2026-07-19 · the W3 sweep · normalize sticks, don't grow the pad map

- **When a stick has an odd hotkey, teach the stick the shared
  vocabulary — don't teach the pad the odd key.** NH's H and
  PMG's L both became "also accepts J" one-liners; the pad map
  stayed at seven buttons. Every button added to the global map
  is a collision surface across ~60 scenes (triggers→Q/E died in
  audit because Q hangs up the BBS and yaws the VN camera).
- **Grep the whole repo for a keycode before mapping it.** The
  audit loop was: list each stick's nonstandard keys, then grep
  that key EVERYWHERE before deciding. Two of five candidate
  mappings died on collisions found outside the stick that
  wanted them.
- **"Unreachable on pad" is sometimes fine.** Wyrd's hex
  diagonals and Basilica's fine-tune stay keyboard-only: the
  orthogonal steps generate the hex lattice, and coarse tune
  covers the radio. Match capability, not keys — a pad path per
  FUNCTION, not per binding.

## TEMPLATE — new lesson entry

```
### YYYY-MM-DD · short session title

- **Punchy lesson, present tense.** Two-to-four sentences.
```
