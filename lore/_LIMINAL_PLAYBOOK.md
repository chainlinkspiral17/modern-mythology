# Liminal Spaces Playbook

How **"the walls are thin here"** is rendered across all gauntlet
locations, and the single discipline that keeps it consistent as
new spaces are added.

## What counts as liminal

Three subtypes, each with its own visual cue:

| `liminal_type` | What it means | Examples |
|---|---|---|
| `show` | Part of someone's broadcast / blog / art. The space is wired into a fiction that bleeds out of it. | `card_wall` (John's Graustark blog), `the_studio`, `the_editing_desk`, `the_storage_closet` (dead-show graveyard) |
| `imagination` | Imagined-but-not-visited place. Has tactile presence without lived experience. | All cathedral `kind:"wip"` plinths (Briar Falls, Harmony Creek, Montreal, Sharp's Club) |
| `threshold` | Wall-thin point between realities. The proportions are wrong; the door has no sign; you can see somewhere else from here. | `precipice_door` (impossible door), `the_back_room` (no signage), `table_17` (Paul's projected court), `the_bookshelf` (the mirror shard) |

## Core rule — JSON is the single source of truth

**Liminal status lives in `godot/resources/games/locations/<id>.json`,
nowhere else.** Each station may carry an optional
`"liminal_type"` field with one of the three values above.

```jsonc
{
  "id": "card_wall",
  "label": "CARD WALL",
  "kind": "search",
  "pos_xy": [600, 720],
  "search_pile": "card_wall",
  "liminal_type": "show"   // ← the tag
}
```

**Inference rule**: stations with `"kind": "wip"` are
auto-treated as `imagination` even without the tag — so future
WIP plinths inherit the treatment by virtue of being WIPs.

## Runtime — how the cue fires

`scripts/LiminalProximityController.gd` runs in every locale
scene. On `_ready()` it:

1. Loads the location JSON (path passed via the
   `location_json` `@export`).
2. Cross-references each tagged station against the gauntlet
   host's `SPACE_MAP` to resolve world positions.
3. **Drift-checks both directions** — every JSON station id must
   exist in the host's SPACE_MAP; every SPACE_MAP key must exist
   in the JSON. Mismatches `push_warning` loudly at scene-open
   so the next person who runs the scene sees the drift.

On `_process()` it measures the player's xz-plane distance to
the nearest liminal station and writes:

- `strength`  — 1.0 within `inner_metres`, fades to 0 across
  `falloff_metres` past that
- `tint_color` — picked from `TINT_BY_TYPE` based on the active
  station's subtype (warm sodium for `show`, cool desat for
  `imagination`, wrong-room blue for `threshold`)

The shader (`assets/shaders/liminal_proximity.gdshader`) sits at
the END of the post-process stack and applies three stacked
effects gated by `strength`:

- Radial chromatic aberration, vignette-shaped (zero at center,
  full at corners)
- Slow UV wobble (~1 px on 1280×720)
- Tint shift via luminance × `tint_color`, vignette-shaped

The cue is intentionally subtle — much softer than the
demon-static treatment (which is a louder cousin of the same
idea). The viewer should feel uneasy, not glitched.

## To add a new liminal station

1. **Tag it in the JSON.** Pick the subtype.
2. **Make sure it exists in the host's SPACE_MAP.** This is
   already a hard requirement for gauntlet-board → 3D-position
   mapping, so it's almost always already done.
3. **Don't edit anything else.** No code changes; no shader
   tweaks; no per-locale overrides.

The drift checker will catch you if you put it in one place but
not the other.

## To add a new locale that should have liminal cues

1. **Tag liminal stations in the location JSON.**
2. **Wire the scene** by adding the same three things every
   existing locale has:
   - `liminal_proximity.gdshader` ext_resource
   - `Mat_Liminal` ShaderMaterial sub_resource
   - `LiminalQuad` ColorRect at the END of the PostProcess
     CanvasLayer (after OldFilmQuad), preceded by
     `BB_Before_LiminalQuad`
   - `LiminalProximityController` Node3D with the four required
     `@export` paths (host, player, post_process, location_json)
3. **Don't fork the shader, the controller, or the tint table.**
   If you find yourself wanting to, that means a new subtype is
   warranted — add it to `TINT_BY_TYPE` once, and propagate the
   string to the playbook + the JSONs.

## Anti-patterns to avoid

- ❌ **Hardcoding liminal lists in GauntletHost scripts.** The
  host knows positions, the JSON knows liminal status. Keep
  them separate.
- ❌ **Per-locale shader forks.** One shader, parameterised by
  type-tint. Adding a fork means adding a fifth subtype-tint
  entry, not a second shader file.
- ❌ **Tagging every threshold.** Literal doors (`kind: "threshold"`)
  that just lead outside (`front_door`, `gangway`, `staff_exit`)
  are NOT liminal — they're plumbing. Only tag the
  metaphysically-thin ones.
- ❌ **Silent treatment changes.** If the inference rule
  (`kind:"wip"` → imagination) ever expands, document it here
  AND mention it in the commit message.

## Current liminal roster (as of 2026-06)

| Locale | Spaces | Subtypes |
|---|---|---|
| Diner (Fool) | `card_wall`, `precipice_door` | show, threshold |
| Cathedral (Magician) | `lovers`, `wheel`, `hanged_man`, `tower` (auto via `kind:"wip"`) | imagination ×4 |
| Bungalow (Priestess) | `the_studio`, `the_editing_desk`, `the_storage_closet`, `the_bookshelf` | show ×3, threshold |
| Riverboat (Empress/Emperor/Hierophant) | `table_17`, `the_back_room` | threshold ×2 |

When adding a new station, update this table at the same time
you tag the JSON. If the table goes stale, the playbook is
lying.
