# Modern Mythology · Blender prop library

Shared, vertex-coloured prop builders used by every locale's
Blender script. Keeps locale builders short ("placement scripts")
and lets the same fixtures appear across vol 5-7 chapters without
copy-paste drift.

## Layout

```
godot/tools/blender/
├── _props/
│   ├── __init__.py        — package marker + library overview
│   ├── geometry.py        — make_box, make_cyl, clear_scene, export_glb
│   ├── palette.py         — neutral + brand colour constants, SNACK_TINTS
│   ├── structure.py       — floor, walls, ceiling, crown molding,
│   │                        windows, door hinges
│   ├── store_fixtures.py  — counter, register, cig rack, lottery,
│   │                        credit-card terminal
│   ├── coolers_drinks.py  — cooler doors, slurpee fountain, ice
│   │                        machine, soda bottle pyramids
│   ├── decor.py           — wall clock, calendar, payphone, faded
│   │                        poster, air freshener tree, floor plant
│   └── safety.py          — security cameras, smoke detectors,
│                            sprinklers, HVAC vents, conduit, bug
│                            zapper, fluorescent tube fixtures
└── locales/
    ├── build_kwik_stop.py     — placement script
    ├── build_cosmic_comics.py
    ├── build_gas_and_go.py
    └── …
```

## Function contract

Every builder follows the same signature shape:

```python
def make_<fixture>(prefix, anchor, *, …palette_kwargs, …count_kwargs):
    """anchor = Blender-frame (x, y, z) anchor point.
    prefix is a string baked into every Blender object name so two
    instances don't collide ('KwikStop_Counter' vs 'ElRancho_Counter').
    palette = optional dict of color overrides; defaults are from
    palette.py."""
```

- **prefix** — every spawned object name starts with it
- **anchor** — Blender (x, y, z) tuple; the meaning is documented
  per-function (some are centres, some are wall-mount points)
- **palette** — optional dict of color overrides. Use this when a
  locale wants the SAME fixture in a different colour key (warm
  for kwik stop, cool for gas & go)

## Adding a new prop

1. Find the file it belongs in (or create a new category if it
   doesn't fit one of the existing seven).
2. Extract the function from whichever locale builder authored
   it. Generalise the anchor / palette so it's not kwik-stop
   specific.
3. Replace the locale builder's inline version with the import +
   call. The locale script gets shorter — that's the point.
4. When ≥ 2 locales need the same prop, document the override
   knobs in the function docstring.

## Coordinate convention

Blender world frame, matching every existing locale:
- **X** = east (positive) / west (negative)
- **Y** = north (positive) / south (negative); doors typically at Y=0
- **Z** = up
- Godot importer swaps Y/Z, so Blender north (Y+) → Godot -Z

Camera-frame conversions live in `Background3D.gd` —
`Vector3(blender_x, blender_z, -blender_y)`.

## Palette discipline

`palette.py` neutrals are warm-sunset 1990s vernacular — the
default Kwik Stop look. Different locales should override via
`palette={}` kwargs rather than editing the module-level
constants. Brand colours (KWIK STOP red, HCE navy, NexCorp
amber) are canon and shared.

`SNACK_TINTS` is the product cycle used for chip bags / soda
cans / six-packs / cig packs. Warm-amber dominant with three
muted cool accents (teal / dusty blue / sage / olive). DO NOT
re-rainbow this list — it's the visual-cohesion guarantee
across every store/diner/cooler in the franchise.
