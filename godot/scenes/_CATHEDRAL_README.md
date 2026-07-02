# cathedral.tscn · the playable warehouse

The Godot scene that assembles the COMMUNITY PLANNED 3D Cathedral
from the GLBs built by the Blender pipeline.

## quick start

1. **Build the GLBs first.** From a terminal:
   ```bash
   cd godot/tools/blender
   ./build_all.sh
   ```
   This runs all five Blender scripts (cathedral interior, workbench
   props, agent figurines, regional dioramas, atmosphere props) and
   writes the GLBs to `godot/assets/3d/`.

2. **Open the Godot project** (the `godot/` directory is the project
   root). Godot 4.x.

3. **Open `scenes/cathedral.tscn`.** The scene tree should show:
   - `WorldEnvironment` · ambient lighting + dark background
   - `Interior` · the warehouse shell (walls, floor, ceiling, river-window struts, workbench shell, BBS desk, diorama platforms, lights, camera marker)
   - `WorkbenchProps` · soldering iron, lamp, notebook, cassette deck, steamboat fragment, moth card, radio
   - `DemonFigurines` · the eight bound demons on the wall shelf
   - `Dioramas` · Graustark, HCE, and Small Wood tabletop miniatures
   - `Atmosphere` · Faith the dog, the phone, the back-room partition, the freight bay door, hanging bulb, storage crates
   - `Player` · CharacterBody3D with `FirstPersonController.gd` and a Camera3D at eye height

4. **Press F5** (or click the Play button). Walk the Cathedral.

## controls

- **WASD / arrow keys** · walk
- **mouse** · look around
- **shift** · careful (slower) walk
- **esc** · toggle mouse capture (lets you click in the editor while playing)

## the Gouraud shader

The vertex-color Gouraud lighting from the Blender bake is in each
GLB's mesh as the COLOR_0 attribute. Godot 4 imports this
automatically. The `gouraud_lambert.gdshader` reads that color as
the unshaded ALBEDO output, ignoring real-time lights entirely.

By default, Godot will use the default `StandardMaterial3D` from
the GLB import, which uses real-time lighting and may look slightly
different from the intended bake. **To switch a mesh to the Gouraud
shader:**

1. Select the mesh in the scene tree
2. In the Inspector → Material Override → New ShaderMaterial
3. ShaderMaterial → Shader → load `assets/shaders/gouraud_lambert.gdshader`
4. The mesh now uses the baked lighting only

The scene file pre-creates one `ShaderMaterial_1` resource you can
re-use for any mesh — just drag it into the Material Override slot.

## the player spawn

The Player node is positioned at `(9.5, 0.5, -7.0)` — roughly at the
freight bay door looking inward toward the workbench and BBS terminal.
Y=0.5 is half-character-height above the floor; the CharacterBody3D's
shape will need a capsule collision shape sized appropriately (the
scene file ships with an empty CollisionShape3D — add a CapsuleShape3D
of radius 0.3, height 1.8 to populate it).

## next steps for the scene

The scene is intentionally minimal — what's there is the visible
geometry. Things still to add:

- **CapsuleShape3D** on the Player's CollisionShape3D node
- **CollisionShape3D** static-body wrappers on the wall meshes so the
  player doesn't walk through them. (The simplest path: select the
  `Interior` instance, right-click → "Make Local," then add a
  `StaticBody3D` + auto-generated `CollisionShape3D` for each wall
  child. Godot has a one-click "Mesh → Create Trimesh Collision Sibling"
  in the Mesh menu.)
- **Interaction triggers** on the BBS terminal (sit → open BBS scene)
  and the workbench (sit → Cathedral Letters / craft).
- **Audio** — the ambient cathedral hum, the BBS modem dial-tone, the
  phone buzz. Drop AudioStreamPlayer3D nodes at the appropriate
  positions.
- **Animated lights** — the BBS phosphor glow should pulse subtly;
  the workbench bulb should be a touch warmer at evening hours.
- **Lightmap baking** — for the static interior, baking the GI once
  in Godot will significantly improve the look without runtime cost.

## the assets directory

```
godot/assets/3d/
├── cathedral/
│   └── cathedral_interior.glb       # warehouse shell
├── props/
│   └── workbench_props.glb          # workbench objects
├── agents/
│   └── demon_figurines.glb          # eight demons + wall shelf
├── dioramas/
│   └── regions.glb                  # graustark + hce + small wood
└── atmosphere/
    └── atmosphere.glb               # faith + phone + partition + door + bulb + crates
```

All built deterministically from the Blender Python scripts in
`godot/tools/blender/`. Edit the constants at the top of any
script to vary the geometry, re-run, the GLB updates.
