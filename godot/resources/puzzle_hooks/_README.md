# Puzzle Hook Seeds

Each art asset can register "hooks" — small machine-readable bits of
information embedded alongside the art that future puzzle mechanics can
read. The hooks themselves don't need any engine code today; they're
JSON sidecars next to the assets that any future puzzle/cipher system
can introspect.

> **Note:** as of mid-2025, long-form lore — chapter pitches, episode
> scripts, character accumulations, worldbuilding reference docs — lives
> at the repo-root `lore/` directory, not here. This directory holds only
> the engine-consumed JSON hooks plus this README. Hook `notes` fields
> may reference paths like `lore/_POMEGRANATE_HOUR.md`; those are prose
> cross-references, not code paths, and exist only to point a reader to
> the canonical writeup of a concept the hook surfaces.

## Schema

```json
{
  "asset": "assets/gallery/emperor.png",
  "scene_id": "vol5_ch4_emperor",
  "character": "dante",
  "arcana": "IV - THE EMPEROR",

  "ciphers": [
    {
      "id": "emp_throne_inscription",
      "kind": "latin_motto",
      "text": "AVTORITAS POTESTAS IMPERIVM",
      "anchor_norm": [0.45, 0.68],
      "reveals": "vol5_ch21_world::keystone_1"
    }
  ],

  "hotspots": [
    {
      "id": "emp_ankh",
      "shape": "rect_norm",
      "rect": [0.34, 0.32, 0.40, 0.55],
      "interact": "emperor.ankh.touched",
      "unlocks": "music:vol5_emperor_theme"
    }
  ],

  "easter_eggs": [
    "rotated mirror reflections at the floor encode the river's name backwards"
  ]
}
```

## Conventions

- `ciphers` — hidden text or motto baked into the art. `anchor_norm`
  is [x, y] in 0..1 of the image. `reveals` is a future puzzle ID
  that this cipher unlocks once solved.
- `hotspots` — interactable rects (normalized coords). `interact` is
  the event name the engine fires when clicked. `unlocks` chains
  forward to gallery unlocks, music tracks, or scene flags.
- `easter_eggs` — prose notes for the author. The engine ignores
  these but they're a journal of what's hidden where.
- `reveals` and `unlocks` IDs reference future systems that don't
  exist yet — that's the point. We seed forward.

## File layout

```
godot/resources/puzzle_hooks/
  emperor.json              ← hooks for the Emperor arcana
  empress.json
  portrait_dante.json
  portrait_nicola.json
  ...
```

A future engine pass will load these alongside the gallery overlay,
register the hotspots/ciphers, and wire `reveals`/`unlocks` IDs to
real puzzle state.
