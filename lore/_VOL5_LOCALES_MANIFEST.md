# Vol 5 — locale 3D upgrade manifest

## ⚠️ HARD RULE — debug feature parity in every chapter / gauntlet

User has stated multiple times: **every chapter, every gauntlet,
every VN scene MUST have the full debug feature surface available**
going forward. The hard rule:

A locale `.tscn` is NOT considered complete unless its scene tree
contains all of:

1. **WorldEnvironment** with locale-appropriate Environment sub-resource
2. **Three-light foundation** — at minimum Key/Fill/Back DirectionalLight3D
3. **GLB instance** (`assets/3d/locales/<name>.glb`)
4. **PostProcess CanvasLayer** with MoodCycler script + the canonical
   9-shader stack (Neon, DirAscii, Ascii, Starscape, Motion, Blur,
   Quad, OldFilm, Liminal) — each preceded by a BackBufferCopy
5. **`mood_strata` array** — locale-appropriate mood IDs that F3
   cycles through during play
6. **LiminalProximityController** Node3D
7. **PDPRiffmaster** Node
8. **HUD CanvasLayer** (`groups=["ui"]`, layer 100) with DebugHUD
   Label + DebugMenu VBoxContainer

ALL existing fully-wired locales (kwik_stop, diner, bungalow,
riverboat_interior, riverfront, harmony_*) follow this contract.
ALL new locales (P1 cathedral/graustark wave + every P2 locale)
MUST follow this contract from initial commit.

The VN `Background3D` strips most of these (PostProcess, HUD) when
loading the locale as a bg, but they need to be PRESENT so that:
- Debug overlay's LOCALE BG-3D section has a MoodCycler to drive
- Walkable-mode of the same locale works without further additions
- The gauntlet's standalone-3D path can promote them when ready

Tracking the priority-ordered upgrade of vol5 visual-novel
backgrounds from 2D PNG sources to 3D Background3D presets.
Going forward, every locale built MUST integrate with the
same VN toolchain features as existing 3D scenes:

- `Background3D.CAMERA_PRESETS` entry (scene path + glb path +
  camera vantage)
- locale `.tscn` wrapper with PostProcess CanvasLayer +
  MoodCycler + three-light foundation (per `_LIGHTING_PLAYBOOK.md`)
- `VnDebugState` registry support (works automatically — locale
  state persists)
- portrait debug overlay (Shift+F12) works in every scene
- character backdrop swap support (per the `set_portrait_backdrop`
  path that already lives in CharLayer)
- Mood/shader/style/blend controls (existing MoodCycler)

## Priority order

### P1 — wire existing builders as Background3D presets
These have BUILDERS and .tscns already. Need only a preset entry +
scene JSON src-swap.

| # | Locale | Builder | .tscn | Status |
|---|--------|---------|-------|--------|
| 1 | bungalow_dusk (Priestess) | build_bungalow.py | bungalow.tscn | NEEDS PRESET |
| 2 | graustark_ruins (cameos + Lovers) | build_graustark.py | NO .tscn yet | NEEDS .tscn + PRESET |
| 3 | riverboat_interior (Empress/Emperor) | build_riverboat_interior.py | riverboat_interior.tscn | NEEDS PRESET |
| 4 | cathedral_interior (Magician) | build_cathedral_interior.py | NO .tscn yet | NEEDS .tscn + PRESET |

### P2 — build new locales with the asset library
| # | Locale | Used in | New build script |
|---|--------|---------|------------------|
| 5 | roberts_kitchen (Lovers ch6) | vol5_roberts_kitchen.jpg | build_roberts_kitchen.py |
| 6 | natalie_apartment (Empress, 3 uses) | vol5_natalie_apartment.jpg | build_natalie_apartment.py |
| 7 | elicia_apartment (Lovers cameos) | vol5_elicia_apartment.jpg | build_elicia_apartment.py |
| 8 | houston_office (Emperor) | vol5_houston_office.jpg | build_houston_office.py |
| 9 | houston_design_studio (Emperor) | vol5_houston_design_studio.jpg | build_houston_design_studio.py |
| 10 | montreal_apartment (cameo) | vol5_montreal_apartment.jpg | build_montreal_apartment.py |
| 11 | cafe_olimpico (Montreal) | vol5_cafe_olimpico.jpg | build_cafe_olimpico.py |
| 12 | new_orleans_bar | vol5_new_orleans_bar.jpg | build_new_orleans_bar.py |
| 13 | new_orleans_office | vol5_new_orleans_office.jpg | build_new_orleans_office.py |
| 14 | new_orleans_apartment | vol5_new_orleans_apartment.jpg | build_new_orleans_apartment.py |
| 15 | new_orleans_room | vol5_new_orleans_room.jpg | build_new_orleans_room.py |
| 16 | hospice_room (late chapter) | vol5_hospice_room.jpg | build_hospice_room.py |
| 17 | louisiana_road (outdoor) | vol5_louisiana_road.jpg | build_louisiana_road.py |

## Per-locale "feature parity" checklist

Every new locale builder MUST produce a scene that includes:

- [ ] **PostProcess CanvasLayer** with the canonical 9-shader stack
  (NeonQuad / DirAsciiQuad / AsciiQuad / StarscapeQuad /
  MotionQuad / BlurQuad / Quad / OldFilmQuad / LiminalQuad).
  Copy the block from kwik_stop.tscn — wire MoodCycler script
  with the right mood_strata list.
- [ ] **Three-light foundation** + practicals per
  `_LIGHTING_PLAYBOOK.md` (one DirectionalLight3D for window/sun
  spill + one warm Fill + one cool BackRim, plus per-fixture
  OmniLight3D where lamps are visible in the geometry).
- [ ] **WorldEnvironment** with locale-appropriate ambient +
  fog + glow tuned for the mood.
- [ ] **Background3D.CAMERA_PRESETS** entry with at minimum the
  canonical opening vantage (per chapter brief in `_VOL5_WIKI.md`)
  and a `requires_glb` field pointing at the built .glb.
- [ ] **Scene JSON updated**: change `"src": "assets/backgrounds/<name>.jpg"`
  to `"src": "3d:<preset_id>"` in every vol5 scene that referenced
  the old 2D bg.
- [ ] **Style packs**: add per-locale style packs to MoodCycler's
  `STYLE_PACKS` array so F12 in the scene cycles
  visually-appropriate combinations (e.g. `natalie_evening`,
  `roberts_kitchen_morning`, `houston_office_fluorescent`).

## Snapshot

P1 is 4 locales of wire-up work (no new geometry needed beyond
the existing builders). Should ship in a single commit.
P2 is 13 new builders + .tscns. Plan: one commit per locale so
they can be reviewed/built/QA'd individually. Library-driven
(per the `_props/*` modules) — each should land in ~150-300
lines of placement script.
