# 3D models — drop your .glb files here

This is `res://assets/models/`. Put exported `.glb` / `.gltf` here (the binaries
are git-ignored — they live locally, sourced from Drive `one model nation
finale/3D model/`).

Easiest way to get them in (from the repo root):
```bash
bash scripts/import-assets.sh "/path/to/your/3D model"
```
That copies every model + texture in here and runs a headless Godot import.

## Special filenames (auto-loaded — no config needed)
| File | Used as |
|------|---------|
| `barn hanger.glb` | the venue (replaces the procedural blockout) |
| `helicopter.glb` | the disaster helicopter |

`Hangar.gd` / `Helicopter.gd` also accept a couple of alternate paths — see their
`MODEL_CANDIDATES`.

## Characters
Point a character at its model in `scenes/previz/data/characters.json`:
```json
{ "id": "nono", "name": "NoNo Von Deutschland", "band": "Nana Avatar",
  "color": "d05a9a", "zone": "stage", "model": "res://assets/models/nono.glb" }
```
No `model` → the coloured capsule stand-in is used, so you can drop models in one
at a time.

## Scale / origin
Models import at their authored scale and origin. After the real `barn hanger.glb`
is in, `STAGE_X`, the crowd grid and camera defaults will likely need a nudge to
match it — that's a known tuning task. Prefer real-world metres and origin at the
floor where possible.
