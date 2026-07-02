# Skyboxes — drop equirectangular sky images here

`res://assets/sky/`. A mood uses a real sky if a file named after its id exists,
otherwise it falls back to the procedural gradient. Supported: `.hdr` `.exr`
`.png` `.jpg` (equirectangular / panorama).

| File | Used for |
|------|----------|
| `dusk.hdr` (or .png/.jpg) | the open-air clear-evening opening (NoNo) |
| `night.hdr` | the cloudy/overcast night finale (Zonk) |
| `disaster.hdr` | the dusty disaster sky (optional) |

Equirect 2:1 images work best. HDR/EXR give proper sky lighting; PNG/JPG are
fine for look. After adding one, run `bash scripts/import-assets.sh` (or open the
editor once) so Godot imports it.
