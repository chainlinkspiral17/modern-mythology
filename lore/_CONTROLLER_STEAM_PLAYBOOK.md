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
  | riffrocker_melody_club | ✔ cursor | one drawn gui_input surface |
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

### 2026-11-09 · what cannot be reproduced is made impossible, and made to speak

- **What happened:** with the pick fixed the user sent a fullscreen
  3440x1440 screenshot — the chapter still in a 16:9 frame: "ultrawide still
  isn't rendering. I'm getting sick of this. It was clearly working
  earlier." / "give me a copy paste that opens a game that works." The same
  chapter fills here on Godot 4.6 AND 4.7.2 (downloaded from the SourceForge
  mirror — GitHub is blocked), under a real window manager (openbox installs
  with apt), fullscreen granted. Not reproduced.
- **Rules:**
  - **Test like the user's desktop.** `xvfb-run` alone has no window
    manager: maximise and fullscreen are never granted. Start openbox first
    (`openbox & sleep 1.5; godot …`). The user's Godot is NEWER than the
    project's (4.7 rewrites `config/features` — the reason project.godot
    changes on every open): test a screen fix on both.
  - **An option that draws the complaint is removed, not explained.**
    PILLARBOX is gone; `Settings.wide_screens` is always "fill".
  - **State that decides the picture is watched, not trusted to a signal.**
    ScreenMgr compares the root's aspect with what it should be twice a
    second and puts it right.
  - **The failure names itself on screen.** A chapter up in a wide window
    that is not filling shows one yellow line with every deciding fact
    (window, canvas, aspect, scale mode, wide surfaces, Godot version) —
    HUD, F4 hides it. The user's next screenshot is the evidence; no one
    has to be asked to open a page and copy a line.
  - **The launcher carries its own settings.** `bash godot/tools/play.sh`
    opens fullscreen through `-- --screen fullscreen` (Settings reads it),
    finds Godot from the running editor's process, and depends on nothing
    saved. The menu keeps a 16:9 frame (only chapters are wide-ready) — SAY
    SO first, or the menu's bars read as the bug.

### 2026-11-09 · THE CAUSE: a lambda cannot write a captured local (the APPLY that always applied 720p)

- **What happened:** the user, fourth message: "everytime I hit apply in
  the options menu, the window resizes down to 720." SettingsOverlay's
  SCREEN SIZE kept the pick in a local (`var pending := Settings.window_mode`),
  wrote it in the buttons' lambda (`func(v): pending = v`) and read it in
  APPLY's lambda. GDScript lambdas capture locals BY VALUE: the write stayed
  in the first lambda's copy, APPLY applied the size saved when the page
  opened — 720p, every time. No pick of ULTRAWIDE or FULLSCREEN ever reached
  Settings, from the day the row was written. The embed fix, the root-Window
  fix and the fill fix were each real, and none was the reason.
- **Rule:** a lambda never assigns a local of the enclosing function. Share
  a value through a member, a one-element Array / Dictionary, or (best) do
  the work in the lambda that receives it. `tools/lambda_capture_check.py`
  flags every such write (292 scripts: 0 today; it flags the old page);
  run_changed_audits.sh runs it on every change and per changed script.
- **Rule:** drive a settings control by PRESSING it in a test
  (`button.pressed.emit()` on the real overlay, then read Settings and the
  window) — the probes set `Settings.window_mode` directly and walked past
  the broken button three times.

### 2026-11-09 · a screen complaint needs the SCREEN'S OWN WORDS before a third fix

- **What happened:** after the root-Window fix the user: "still not
  working", with a screenshot — the debug window maximised on the wide
  monitor, the chapter in a 16:9 frame with black bars. Not the bug just
  fixed (that one drew the picture unscaled in a corner). The same chapter
  filled the width here with default settings: the picture is what
  WIDE SCREENS = PILLARBOX looks like, or a lost wide request. Three rounds
  were spent fixing what could be reproduced instead of reading what the
  user's machine was doing.
- **Rules:**
  - **The game says what the screen is doing.** `ScreenMgr.describe()` —
    "Window 3440×1390, maximised, on a 3440×1440 screen · wide (2.47:1). The
    story fills the width." — is shown under SCREEN SIZE in Settings and
    printed to the log on every change. A reason is always named
    (PILLARBOX is on / the window is 16:9 / this page keeps a 16:9 frame /
    inside the editor's Game tab). Ask for that line, not for a description.
  - **A wide-ready surface is a GROUP member** (`wide_ready`), read fresh on
    every refresh — not a list entry dropped by a one-shot signal.
  - **A setting that can silently produce the complaint is reset once.** The
    fill option moved to a new key (`wide_fill`); an old saved PILLARBOX is
    not read.
  - **A pick applies at once.** SCREEN SIZE waited for a separate APPLY
    press; every other row on the page applied on the press.
  - A screenshot from the user is worth more than a probe: when the first
    fix "doesn't work", ask what the screen shows before writing a second.

### 2026-11-09 · the window changes through the root Window — and a screen fix is tested on a SCREEN

- **What happened:** after the embed fix the user came back twice:
  "Ultrawide setting isn't taking, still." / "In scenes are back to their
  old resolution." Settings sized the window with
  `DisplayServer.window_set_size`. The OS window grew to 3440x1440; the root
  Window node stayed 1280x720 (the DisplayServer records the size it was
  asked for, so its "window changed" callback never fires) — the game drew
  at its OLD resolution in a corner of the new window, menu and scenes both,
  and at boot from the saved setting too. Two sessions "fixed" the screen
  size without once running the game on a screen of that size.
- **Rule:** a size / mode / position change of the game's window goes
  through `get_tree().root` (`.size`, `.mode`, `.position`): the Window's
  setters call the DisplayServer AND resize the viewport. Never
  `DisplayServer.window_set_size|mode|position` (gate:
  `window_api_audit.py`, in run_changed_audits.sh on every change).
  Settings then checks for a second that root.size == the real window
  (`_sync_root_window`) and corrects it.
- **A size that IS the screen is fullscreen.** ULTRAWIDE on a 3440x1440
  monitor "did not fit" (title bar + taskbar) and fell to MAXIMISED — never
  the resolution asked for. Now it is that screen's fullscreen. Where
  fullscreen is not granted (no window manager, a compositor that ignores
  it), 45 frames later the window becomes a borderless one of the screen's
  size.
- **Test:** `tools/ScreenProbe.tscn` — the real Main scene, the mode set as
  the overlay sets it, a chapter started as the menu starts it; prints the
  window, root.size, the canvas and the 3D set's render size at each step
  and captures the SCREEN (the X root, not the game's viewport — a lost
  window only shows there). Run it under `xvfb-run -s "-screen 0
  3440x1440x24"` AND a larger screen (3840x2160: the windowed path) before
  saying a screen-size fix works. Good: `root.size (3440, 1440) · canvas
  (1720, 720)` in a scene, Background3D viewport (3440, 1440).

### 2026-11-09 · the user plays from the EDITOR: debug runs must not be embedded

- **What happened:** the user asked, more than once, for the ultrawide / max
  resolution "in debug". Godot 4.4+ plays an editor run (F5) EMBEDDED in its
  Game tab, where a game cannot change its window, so SCREEN SIZE did
  nothing; sessions answered with `tools/play.sh` (a terminal launch), which
  is not how the user plays. ("I keep repeating things.")
- **Rule:** debug runs open in their own window — `python3
  godot/tools/no_embed.py` (with Godot CLOSED) sets the project's
  `[game_view] embed_on_play=false` in `.godot/editor/project_metadata.cfg`
  (local, not in git). After that, F5 opens a real window and the saved
  SCREEN SIZE applies (FULLSCREEN = the screen's own maximum; ULTRAWIDE =
  3440×1440). Never answer a screen-size question with play.sh alone.

### 2026-09-03 · the fence ate the pad; Cabin Beaver's door had a pine in it

"movement in pirate summer is completely broken" (Deck).

- **Autoloads get unhandled input LAST.** Godot walks the
  unhandled-input group from the deepest node back to the root's
  first child. The InputBlocker fence under every slowstick called
  set_input_as_handled() on EVERY event, so it ran before the
  GamepadMgr autoload and swallowed the raw JoypadButton events —
  B/X/Y/LB/RB never became ESC/E/J/Tab/I inside the television. The
  d-pad walk is polled in _process and was fine; but Pirate Summer's
  day-intro modal needs ESC or SPACE to begin the day, so on pad Sam
  stood behind a modal forever. The fence now lets joypad events
  through; the synthesized KEY event comes back through it and is
  fenced from the menu underneath as before. The 07-19 pad audit
  predated the TV wrap (07-10 fence, TV wrap later) — RE-AUDIT THE
  PAD after any change to the wrap, the fence, or the autoload
  order.
- **Give every modal's button focus.** The day-intro modal had no
  focus owner, so A (ui_accept, on the real input map) did nothing.
  GamepadMgr.focus_first.call_deferred(panel) on open; the panel is
  freed on close so focus releases itself.
- **A zone's exits are testable without Godot.** A BFS from each
  zone's start spawn over `walkable` tiles to every exit tile and
  spawn found the doorway of Cabin Beaver walled in by a "smaller
  pine" at (18,12) — unreachable from the path, and a dead spawn
  from inside. Run it after any zone edit:
  see the commit 89a7a724 script (17 zones, 0 problems).

### 2026-08-03 · the TV was eating the bottom of every stick

**User report:** "still can't play" + a screenshot of Northwind
Harbor with NO walk signs, NO pockets, NO HEARD, and a two-pixel
dog.

**Root cause 1 — the cabin TV clipped the design space.** Sticks
lay out in an absolute 1280x720 coordinate space. The TV
container's screen panel is FULL_RECT minus bezel insets (30 px
sides, 72 px total vertical) with clip_contents on — so on a
720-tall window the glass is 648 tall and the BOTTOM 72 PIXELS OF
EVERY SLOWSTICK rendered into the void. Any control living near
y=720 (Northwind's nav row, any stick's bottom status bar) was
invisible AND unclickable. Fix: the FitFrame — a fixed 1280x720
Control letterboxed into the glass (uniform min-scale, centered;
Control.scale transforms input too). **Rule: a stick's design
space is 1280x720 and whatever mounts a stick must letterbox that
space, never hand the stick a smaller rect.**

**Root cause 2 — STRETCH_KEEP on a 16x12 sprite.** Bosun's
TextureRect had a 96x72 size but stretch_mode KEEP, which draws
the texture at native sprite size — a speck. STRETCH_SCALE +
NEAREST is the pattern for SlowstockSprite display rects.

**Meta-lesson:** the "nothing happens" bug had THREE layers
(affordance, clipping, sprite scale) and the first fix pass only
addressed the first because it was reasoned from code, not from a
screenshot. A player screenshot beats a code read. Ask for one
early.


### 2026-08-03 · shelf click-to-boot regression · focus fires before gui_input

**User report:** "can't click on manual — it only clicks once and
plays," plus the mouse cursor disappearing.

**Root cause 1 (the click):** the W2 pad-nav wiring gave shelf
cartridge panels `focus_mode = FOCUS_ALL` with
`focus_entered -> _select_cart` ("pad focus selects, exactly like a
click"). But in Godot 4 a MOUSE click on a focusable Control grants
focus BEFORE the press reaches `gui_input` — so the same click ran
_select_cart via focus_entered, then gui_input saw
`_selected_id == sid` and took the "second click on the same cart =
boot" branch. One click booted the stick; MANUAL / SCRAPBOOK were
unreachable. This is the one-path-per-input rule failing in a new
shape: the two paths were different SIGNALS of the same event, not
two devices. Fix: `_select_cart` stamps `_selected_at_ms`; the
gui_input boot branch requires the selection to be >300ms old.
**Rule: any "second activation = confirm" surface with pad focus
must debounce against the focus-grant of the first activation.**

**Root cause 2 (the cursor):** GameEngine's reading-comfort
idle-hide (3.5s) kept running while the shelf overlay was open, and
the wake handler only listened for `InputEventMouseMotion` —
clicking without moving, and Deck touchscreen taps (which emit no
motion events), never brought the pointer back. Fix: no idle-hide
while a `vn_input_blocker` overlay is open (pointer-driven surface,
hiding reads as a bug), and wake on `InputEventMouseButton` too.


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
