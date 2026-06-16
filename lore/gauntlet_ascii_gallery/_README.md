# Gauntlet ASCII Gallery

Full-screen ASCII maps for use as the Tarot Gauntlet's **map view**
(the screen the player can pop open mid-run to see board layout,
zones, and visitor positions).

Each map in this folder is:

- Pure monospace ASCII — designed to render in a fixed-width font.
- Sized for a typical terminal/full-screen view (~90 cols × 50 rows
  max). Designed to look right at any size you scale to as long as
  the font is mono.
- Lore-canonical for its scenario: compass directions, zone names,
  and search/visitor/threshold markers match what `build_*.py` and
  the gauntlet rules use.
- Wrapped in a fenced block (` ``` `) so a Markdown viewer
  renders it verbatim.

The gallery exists because the user asked: "lovely ASCII though,
file it away in an ascii gallery for the gauntlet, maybe as the
full screen map."

## Files

- `dambrosios_diner.md` — D'Ambrosio's diner + surrounding zones
  (river / bayou / parking lot / gangway / paddle wheel), with
  Gauntlet zone markers for the canonical scenario
  "D'Ambrosio's · Fool reversed" (THE LEAP).

## Adding a new map

1. Sketch the room/locale layout to scale (1 character ≈ 0.3m
   horizontally, 1 row ≈ 0.5m vertically).
2. Mark gauntlet zones with the canonical glyphs:
   - `S` — Search pile
   - `V` — Visitor station
   - `T` — Threshold (3 AP movement cost)
   - `◯` — Faith starting position
3. Wrap in a fenced block. Add a brief lore note and zone index
   below the map.
4. Add the new map filename to the "Files" list above.

## Conventions

- North is UP in every map (matches Blender Y convention used in
  the build scripts).
- Box-drawing characters (`─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼`) for walls.
- `═ ║ ╔ ╗ ╚ ╝` for double-line emphasis (counters, bars).
- `▒` for thresholds, glow zones, water.
- `░` for kitchen tile / staff zones.
- `▓` for feature props (jukebox / Table 17 / BBS).
- `◆` for freestanding tables, `◇` for booth tables.
- `●` for fixed light fixtures, `○` for stools.
