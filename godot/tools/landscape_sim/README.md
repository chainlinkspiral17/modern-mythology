# Estuary One — landscape simulation harness

> *In-fiction:* a prototype landscape simulator from the slowstick
> game studios of volume 7.
> *Out-of-fiction:* a parametric topography previewer the project
> uses before committing to a Blender / glTF build cycle.

## What it does

Given a parameter block (district bounds, elevation function, creek
control points, road grid, neighbourhood polygons), it renders a
top-down map preview as a PPM image: elevation contours, creek
path, road grid, land-use colours, neighbourhood centroid markers.
Stdlib only — no `pip install`.

## Why it exists

A full Blender → glTF → Godot iteration on a new locale takes
minutes and produces a 100 MB+ GLB. When the question is "is the
**shape** of this landscape right?", we don't need the GLB; we need
a map. Estuary One answers that question in under a second per
parameter sweep.

Workflow:

1. Open `estuary_one.py`. Edit the `*_PARAMS` block at the bottom
   (or add a new one for another locale).
2. `python3 estuary_one.py out.ppm`
3. View `out.ppm` (Krita, GIMP, ImageMagick, or `Pillow` → PNG).
4. Adjust parameters. Repeat until the topography reads correct.
5. Once locked, transcribe the parameters into the locale's
   `build_*.py` and start placing geometry.

## Current parametric locales

| Locale  | Function          | Status |
|---------|-------------------|--------|
| HCE     | `hce_elevation`   | Initial pass — country-club rise NW, creek meander NW→SE, low SE skate-park / woods |

## Extending

Each locale is a `LandscapeParams` instance: bounds, elevation
callable, `CreekPath`, `RoadGrid`, optional list of `Neighbourhood`
polygons with land-use codes. Add a new dataclass instance, swap
which one `__main__` renders, and re-run.

Elevation helpers shipped: `value_noise`, `fbm`, `hash2d` — Perlin-
style smoothing with deterministic seeds. Combine these with simple
gradients (tilts) and Gaussian rises/dips to compose terrain that
reads correctly at the district scale.
