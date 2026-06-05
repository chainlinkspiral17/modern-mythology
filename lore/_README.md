# Modern Mythology · Lore

The text-heavy half of the project. Worldbuilding, characters,
chapter pitches, full episode scripts, music + game subculture
documentation, character accumulations.

This directory is a sibling of `godot/`. The Godot project
consumes its own JSON hooks at `godot/resources/puzzle_hooks/`,
which still hold the machine-readable game data; everything in
`lore/` is reference material for writers and designers — long-
form prose, scripts, and reference docs that the engine doesn't
parse.

## directory map

### top-level reference docs

| file | what |
|---|---|
| `_COMPASS.md` | NARRATIVE STRUCTURE COMPASS — the in-fiction meta-system referenced across multiple cards |
| `_DAMBROSIO_FAMILY.md` | the D'Ambrosio family tree as worldbuilding constraint |
| `_DAMBROSIO_EMPLOYEES.md` | the employment register that reframes the deck's class layer |
| `_DEMONIC_DOMAIN.md` | the demonic electronic domain — recast of the card-game layer |
| `_PITCHES.md` | card-as-scene pitch index (per-card pitches live in `pitches/`) |
| `_POMEGRANATE_HOUR.md` | Elicia Duchane's web series — series-level doc (22 episode scripts in `pomegranate_hour/`) |
| `_SINKHOLE_NEXUS.md` | the Calamity — the deck's central trauma reframing |
| `_TAROT_LORE.md` | classical Major Arcana mapping onto Graustark / the deck |
| `_UNLOCK_WEB.md` | per-card outbound edges across the 22-card network |

### subdirectories

| dir | what |
|---|---|
| `pitches/` | per-card scene pitches (0 through 21, partial coverage) |
| `pomegranate_hour/` | Elicia's series — 22 episode scripts + `_INDEX.md` + `_HOST_FRAMES.md` + `_HOST_FRAMES_scenes.js` (dialogue-format export for HTML tools) |
| `planned_community/` | vol6 lore — character accumulations, Suburban Blight, Cosmic Comics, the Glitch Report, the music strata, the digital subculture |
| `milk_and_honey/` | vol7 lore — Static Truths, the SCUMM Machine, the Alsea Bay Cannery |

## what lives in `godot/resources/puzzle_hooks/` instead

The engine-side. JSON hook files the game's hotspot system reads:
the 22 card JSONs (`fool.json`, `magician.json`, etc.), the
portrait JSONs, `music_player.json`, `tarot_synth.json`, and
`fool_reference_blocks400.json`. Plus `_README.md` documenting
the hook schema.

The hooks reference lore docs in their `notes` fields by path
(e.g. *"See lore/_POMEGRANATE_HOUR.md for the full series doc"*),
but no code logic depends on `lore/` — moving or renaming files
here will only break prose cross-references in JSON notes, not
the engine.

## conventions

- top-level reference docs are prefixed `_` and uppercase-named
  for sorting and instant recognition
- per-volume subdirectories are lowercase named after the volume's
  setting (`planned_community/`, `milk_and_honey/`)
- per-character / per-artifact files inside subdirectories are
  lowercase snake_case (`suburban_blight.md`, `cosmic_comics.md`,
  `static_truths.md`)
- all dates in prose are in the form *"late summer 2025"* unless
  a chapter requires the exact date
- all in-fiction quotes are in italics or formatted as blockquotes;
  the writer's own commentary is in normal prose
- when a fact is reserved (deliberately not committed by the deck),
  the doc says so explicitly: *"the deck reserves whether..."*

## also adjacent (still in `godot/`)

- `godot/resources/scenes/` — the game's actual VN scene JSONs
  (vol1-7 chapters, the engine-consumed scripts)
- `godot/scenes/menu/` — Godot GDScript scene controllers (the
  dioramas, music player, gallery)
- `godot/tools/` — Python + HTML tooling (runway_render.py,
  resolve_bridge.py, voice_studio.html, etc.)

— the chapter is held in both places.
