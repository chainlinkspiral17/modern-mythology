# Blender Pipeline · Modern Mythology · COMMUNITY PLANNED

Procedural Blender scripts that build the low-poly Gouraud-shaded
3D assets for the COMMUNITY PLANNED gallery game. The aesthetic
lock: ~mid-90s low-poly, per-vertex Lambertian shading, restrained
lighting, painted-2D textures applied to the 3D geometry. Runs on
a decade-old laptop. Looks striking.

## the pipeline

```
  blender script (this directory)       →  GLB file       →  Godot scene
  blender --background --python build_<asset>.py     godot/assets/3d/cathedral/
                                                     godot/scenes/cathedral.tscn
```

Each script is self-contained and deterministic. Run it; get the
same mesh every time. Edit the constants at the top of a script,
re-run, get the new mesh. No DCC tool surface needed — Blender
becomes a build target, not an authoring environment.

## requirements

- **Blender 3.6+** installed locally. (4.x is fine too.)
- Blender on PATH, or known absolute path.
- The scripts run via `blender --background --python <script>.py`.
- No external Python dependencies beyond bpy (built-in to Blender).

## the assets

Built incrementally as the prototype matures:

| script | what it builds | status |
|---|---|---|
| `build_cathedral_interior.py` | the warehouse box · floor · ceiling · walls · workbench · BBS desk · river window with iron struts · two strategic-map diorama bases | **starter shipped** |
| `build_workbench_props.py` | the soldering iron, the notebook, the cassette deck, the model boat fragment, the moth-lamp revision 3 | reserved |
| `build_diorama_graustark.py` | the Graustark region as a tabletop diorama — boat-ghost site, diner, restaurant, bungalow, cathedral, river | reserved |
| `build_diorama_hce.py` | the HCE region diorama — Lot 47 model home, HOA office, Phase III trailer, cul-de-sacs | reserved |
| `build_diorama_smallwood.py` | the Small Wood region — Wagner's Hardware, the road, the tower (the unreachable one), God's Thumb | reserved |
| `build_agent_figurines.py` | the small painted demon icons that sit on the wall shelf and the dioramas (vagrant, cicada, moth, steamboat, weir, filly, starling, husk) | reserved |
| `build_phone.py` | the workbench phone | reserved |
| `build_bbs_terminal.py` | the phosphor-green CRT, the keyboard, the modem stack | reserved |

## aesthetic rules (locked)

- **Polygon budget:** ~5-10k triangles for the full warehouse interior. Individual props 50-500 triangles each. The full scene loads in 50ms on integrated graphics.
- **Vertex colors carry the Gouraud lighting.** No baked lightmaps required (though optional). The custom Godot shader reads per-vertex color as Lambertian intensity from a fixed light direction.
- **Materials are simple.** Diffuse-only base + the painted 2D textures (visitor portraits, item plates, card art, the BBS CRT phosphor screen) as image textures on specific faces.
- **Lighting is restrained.** 1-3 lights per room. Frasier's workbench lamp + the river-window directional + (optionally) a small fill from the BBS terminal's phosphor glow.
- **Palette ties to the project canon:** warm bg `#0e0a06`, warm mid `#1a120a`, paper `#d9c69b`, rust `#c66e3a`, phosphor green `#8fcf6e`, blue accent `#6a8fc6`. Consistent with the prototype HTML's CSS variables.

## the visual reference

Mid-90s first-person 3D, modern restraint:

- *Quake* (1996) — sector lighting, warm/cool contrast
- *Thief: The Dark Project* (1998) — torch-lit interiors, deep blacks
- *LSD: Dream Emulator* (1998) — surreal low-poly
- *Mouthwashing* (2024) — modern PS1-aesthetic horror
- *Signalis* (2022) — pixel-modern hybrid
- *Anatomy* by Kitty Horrorshow — first-person low-poly minimalism
- *Cruelty Squad* — aggressively striking with low fidelity

## running the scripts

```bash
# from project root
cd godot/tools/blender

# build the warehouse interior
blender --background --python build_cathedral_interior.py

# the GLB lands at:
#   godot/assets/3d/cathedral/cathedral_interior.glb

# import it in Godot:
#   File → Import → cathedral_interior.glb
#   it'll appear in the FileSystem dock; drag into a scene
```

## from blender to godot

The GLB files import natively in Godot 4. Vertex colors come in
as a `COLOR_0` mesh attribute. A custom shader reads that
attribute as the Gouraud lighting term. The shader lives at:

```
godot/assets/shaders/gouraud_lambert.gdshader
```

(reserved; will land alongside the first 3D scene assembly.)

## what to author by hand vs. procedurally

This pipeline procedurally generates **architectural geometry** —
the warehouse box, the workbench shape, the dioramas' base
platforms, the BBS desk. These are blocky, deterministic, easy
to vary by editing constants.

What does NOT belong in the procedural pipeline:
- Character models (none needed; first-person)
- Organic shapes that need an artist's hand
- Painted 2D textures (those live in `godot/assets/gallery/`
  and are authored via the Gauntlet Studio pipeline)
- Animation rigs (none needed for static props; first-person
  hand animations would be authored by hand)

The procedural scripts let me (Claude) generate buildable assets
without needing to do art in a DCC tool. The painted look comes
from the 2D textures wrapped onto the 3D geometry — the existing
Gauntlet Studio painted style projects onto the low-poly meshes.

## status

Starter script `build_cathedral_interior.py` shipped. Run it
locally to generate the GLB. Future scripts will be added as the
build progresses.
