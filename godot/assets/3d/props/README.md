# Hero prop GLBs

Story-critical objects (the tarot deck, the SCUMM Machine, Sam's
license-plate notebook, the steamboat model …) as textured GLBs,
one per roster entry with `kind: "prop"` in `godot/tools/meshy_roster.json`.

They are produced by the image → Meshy pipeline:

```bash
cd /home/deck/Downloads/modern-mythology && python3 godot/tools/meshy_pipeline.py list --kind prop
cd /home/deck/Downloads/modern-mythology && python3 godot/tools/meshy_pipeline.py run scumm_machine --provider google --texture
```

or from the browser via `python3 godot/tools/meshy_pipeline.py serve`.

## Using them

- **Locale builds (Blender):** import with `bpy.ops.import_scene.gltf`
  the same way `build_graustark.py` instances hero GLBs
  (`_instance_hero_glb`) — measure the bbox, fix the up-axis (Meshy
  tags Y-up but often exports Z-up), scale to the canon size, and drop
  it at the spawn point. Prop scale is NOT normalised to 1.80 m like
  heroes; set the size per object (a matchbook is 5 cm, the SCUMM
  Machine is 1.5 m).
- **VN close-ups / CG:** load through a `Portrait3D`-style
  SubViewport if a prop needs a rotating hero shot; the portrait
  framing is tuned for heads, so add a per-prop camera distance.

## Conventions

- Filenames are the roster `file` field; do not rename by hand.
- Meshy GLBs carry PBR textures (base colour + normal + metallic/
  roughness); that is allowed for props (the "no texture assets" rule
  in CLAUDE.md is about locale geometry, which stays vertex-coloured).
- Keep each GLB under ~15 MB. Use `--model-type smart-topology
  --polycount 8000` for background-scale props.
