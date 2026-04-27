# Backgrounds

Place full-scene background images here.

## Naming convention
`{scene_id}.jpg` or `{scene_id}.png` or `{scene_id}.webp`

## Examples
```
small_wood_day.jpg          ← Small Wood Volumes, daytime exterior
small_wood_night.jpg
diner_exterior_night.jpg
station_omega_dome.jpg
underpass_night.jpg
briar_falls_cemetery.jpg
```

## Specs
- Recommended: 1920×1080px (16:9), JPEG for photos, PNG for illustration
- WebP supported for smaller file sizes
- Engine scales to fill the 1280×720 game canvas automatically

## In scenes
Reference by filename in a `bg` node:
```json
{ "t": "bg", "src": "assets/backgrounds/small_wood_day.jpg" }
```
