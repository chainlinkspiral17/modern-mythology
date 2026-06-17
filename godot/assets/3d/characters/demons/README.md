# Demon character GLBs

Drop demon-character meshes in this folder. Up to 8 canonical demon
slots; only **`the_demon`** ships in chapter 1 (the man at the empty
stool at the cathedral's DEVIL station).

## How demon portraits render

Demon GLBs share the hero `Portrait3D.tscn` scene but the
`SubViewportContainer` carries a material override running
`portrait_demon_static.gdshader`. When `CharLayer._make_portrait`
resolves a GLB inside `demons/` it calls
`Portrait3D.set_demon_mode(true)`, which:

1. Pushes the digital-static shader strength to 1 — RGB chromatic
   aberration, horizontal scanline tears, TIME-quantized static
   noise, and signal-drop bands all light up.
2. Pins the camera/lighting to the **`demon_chaos`** mood preset
   (sickly cathode green key, red signal-burn fill, 28 Hz jitter,
   quick lurch + yaw drift). Any incoming expression (`happy`,
   `angry`, etc.) is collapsed to `demon_chaos` — demons don't
   perform moods, they leak.

The art-direction brief: **digital static and high-energy chaos.**
Hero portraits = subtle camera + lighting; demon portraits =
broken VHS tape fed through a possessed camera.

## File-naming convention

| Visitor ID (visitors.json) | Expected file | Notes |
|----------------------------|---------------|-------|
| `the_demon`               | `the_demon.glb`        | ch1 only — Magician scenarios |
| `the_drifter`             | `the_drifter.glb`      | future |
| `the_birdwatcher`         | `the_birdwatcher.glb`  | future |
| `the_critic`              | `the_critic.glb`       | future |
| `the_superfan`            | `the_superfan.glb`     | future |
| `the_twins`               | `the_twins.glb`        | future (single mesh, twin figures) |
| `drunk_uncle`             | `drunk_uncle.glb`      | future |
| `mackenzie_remote`        | `mackenzie_remote.glb` | future (the call-in demon) |

The registry table is in `godot/scenes/game/CharLayer.gd` under
`PORTRAIT_3D_DEMON_KEY_TO_GLB`. Implicit `<key>.glb` lookup also
works, so dropping `the_drifter.glb` into this folder is enough to
make that demon portrait resolve once the visitor appears in a
scene JSON. The static-shader gating is automatic — anything under
`demons/` is treated as a demon.

## Authoring tips

- Demon meshes should stand at roughly the same scale as heroes
  (~1.8 m tall). The portrait framing in `Portrait3D.tscn` is
  tuned for head-and-shoulders; very short or very tall figures
  will read wrong.
- Vertex colors are fine; PBR textures also work since the shader
  layers ON TOP of the rendered viewport.
- The camera shake at `demon_chaos` is violent enough that intricate
  facial detail will smear. Lean into silhouette + bold features
  (the chaos shader does the rest).
