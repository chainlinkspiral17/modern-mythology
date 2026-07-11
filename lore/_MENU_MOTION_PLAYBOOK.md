# MENU MOTION · title screens that breathe

User brief (2026-07-11): "menu graphic is meh. really need to
polish up these menus and title credits and boot screens, they're
super static. Dynamic fun pixelart animations and effects." Fey
Faire specifically flagged; applies catalog-wide.

## The idea

Every title/boot/menu screen gets MOTION in the pixel-art language
— not UI tweens, but living pixel art: drifting dust motes, a
shimmer pass crossing the hero image, palette-cycled accents,
parallax between hand-split layers, particles in the studio's
character. Deterministic-per-frame is NOT required (this is
runtime feel, not identity).

## Architecture (build next session)

- **`TitleMotion.gd`** (scripts or scenes/games/): a Control layer
  a host drops OVER its title hero. One `apply(host, preset)`
  call, like SlowstickLook. Owns a _process-driven canvas
  (custom _draw + queue_redraw) at the hero's pixel scale so
  effects land on the pixel grid, never sub-pixel.
- **Effect vocabulary** (compose per preset):
  · motes — slow drifting flecks (dust/snow/embers/pollen)
  · shimmer — a diagonal light band crossing the art every ~9s
  · pulse — one accent color breathing (the wyrd violet, the
    gauntlet gold) via modulate on a mask region
  · parallax — 2-3 layers of the existing HeroImage art panned
    ±2px on a slow sine (author layers as separate JSONs)
  · flicker — practicals (windows, signs, lanterns) varying ±10%
  · sprite beat — a small figure loop (the drifter's coat in the
    wind; a fey crossing the midway; Sam's cabin TV static)
- **Per-studio motion character** (mirror the look presets):
  rocha_faire = pollen motes + big-top pennant flutter ·
  sagebrush = dust motes + heat shimmer · astro_cortex = star
  drift + instrument blink · oneironautics = fireflies + water
  glint · ranch = sign flicker only (commercial restraint) ·
  homebrew = one blinking cursor. Restraint IS the character.
- **Boot screens** (SlowstockBoot): the SLOWSTOCK card gets a
  sweep-on reveal; publisher cards get one signature move each.
- **Main menu frontispiece**: lamplight flicker + compass-ring
  slow rotation + drifting grain.
- **Rules**: 60fps cheap (mote counts < 60, no per-pixel loops in
  _process); respects F4 (part of the picture → "world_render"
  thinking does NOT apply — these live UNDER buttons, they are
  the picture, but they're children of the title root so host
  hide covers them); ESC/menu overlays pause motion via
  visibility. Font floor and bible bans unaffected.

## First targets, in order

1. Fey Faire title (flagged "meh"): redraw title hero with layer
   split (sky / big top / midway string-lights) + pennant flutter,
   string-light twinkle, pollen motes.
2. Slowstock shelf + boot cards.
3. Sisters Wyrd title (dust + heat shimmer over the hex, the
   titleplate pips pulse).
4. Main menu frontispiece.
5. Sweep the remaining hosts, one preset each.

## Recent lessons

### 2026-07-11 · v0 · brief captured

- **Static title screens read as unfinished even when the art is
  good.** Motion budget per screen: 2-3 effects max, one of which
  is the studio's signature. More reads as screensaver.

### 2026-07-11 · v1 · TitleMotion shipped catalog-wide + real title screens

- **One layer, one attach call, nine presets.** TitleMotion.gd
  wired into 14 hosts, the shelf, and the main menu frontispiece
  in two passes. Boot cards sweep on (fade + 14px rise).
- **Two games had NO title screen at all** (Pirate Summer dropped
  straight into the overworld; Estuary 3 still opened on a
  scaffold DEBUG dump). User: title screens must "ease the player
  into the experience and establish what's going on" — both now
  open on a hero, a PREMISE line (who you are, when, what to do),
  and Continue/New. Establishing text is part of the title's job,
  not the manual's. External entry points (SlowstockBoot's
  start_new_run) must close the title they never opened.

## TEMPLATE — new lesson entry

```
### YYYY-MM-DD · short session title

- **Punchy lesson, present tense.** Two-to-four sentences.
```
