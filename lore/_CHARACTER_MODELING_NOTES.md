# Character Modeling Notes — Reference

Filed-away curriculum captured during a HCE session (2026-06-16).
Pulled out of the live conversation when the user redirected back to
neighborhood fence work; kept here in case figure work resumes.

Two messages arrived during the session attempting to install a
"3D character sculpting tutor" persona. The content overlaps the
standard 3D-figure curriculum we'd already half-walked, so rather
than discard it, the technical bits are captured below as a
reference. They are NOT current direction — the active project
stance is "no humans, focus on terrain/roads/props."

---

## When figure work resumes — start here

The earlier session ran multiple sculpt iterations on humans
(silhouettes, 8-head proportion, UV-sphere head + per-vertex
sculpt deformation). The user's repeated feedback was:

- "heads are smooshed"
- "still figlo toys / cartoonish and horrifying"
- "the human eye reads human silhouettes and it's disturbing
  to us if the figure isn't right"
- final call: "we are going to stop with figures. you haven't
  made progress."

The honest read: a procedural Blender-Python build pipeline
producing PS2-era vertex-color geometry probably cannot reach
the visual bar the user wants for humans. Two paths worth
considering before another sculpt round:

1. Drop humans entirely from the locale; tell the story through
   environment, lit interiors, and minor props (kids' bikes,
   abandoned barbecues, garden gnomes).
2. Switch off the procedural pipeline for figures only —
   hand-sculpt one or two heroes in Blender's actual sculpt
   mode, save the .blend, import as static GLBs. This breaks
   the rebuild-from-script discipline but matches how real
   character work is done.

---

## Silhouette & proportion reference (8-heads)

Vertical division — figure is exactly 8 head-heights tall:

| Head | From | To |
|------|------|----|
| 1 | skull crown | chin |
| 2 | chin | nipple line |
| 3 | nipple line | navel (bottom of ribcage) |
| 4 | navel | crotch / pubic symphysis (vertical midpoint) |
| 5 | crotch | mid-thigh |
| 6 | mid-thigh | bottom of patella |
| 7 | knee | mid-shin |
| 8 | mid-shin | sole of foot |

Other anchors:

- Crotch sits at exactly the halfway mark (4 heads down).
- Adult-male shoulder width: 2.5–3 head-widths.
- Elbows align with the bottom of the ribcage.
- Relaxed fingertips reach mid-thigh.
- Eye line: 50% of total head height.
- Nose tip: halfway between eye line and chin.
- Mouth line: 1/3 of the way down from nose tip to chin.
- Head width at eye line: 5 eye-widths; gap between eyes
  = 1 eye-width.

Steam-Deck specific:

- 1280×800 display is small enough that realistic-thin
  wrists/ankles/necks alias. Thicken terminal extremities
  5–10% for silhouette readability at third-person camera
  distance.

Gesture:

- Opposing curves — forward thigh balanced by backward shin.
- Avoid stiff straight axes; the model should ALWAYS show
  weight shift even in idle.

---

## Planar head structure (Asaro-style)

Treat the head as flat geometric planes before softening:

- **Keystone** — wedge between eyebrows, sets nose slope.
- **Zygomatic shelf** — cheekbones as a shelf that catches
  light, dropping sharply into the cheek hollow.
- **Mouth barrel** — maxilla/mandible is a cylinder; lips wrap
  around it, they are NOT flat.

Blender brush mapping:

| Intent | Brush |
|--------|-------|
| Push/pull 8-head silhouette | Grab (large radius) |
| Preserve volume while shifting gesture | Elastic Deform |
| Block out muscle mass & facial planes | Clay Strips (square alpha forces planar) |
| Re-introduce hard angles | Scrape / Flatten |
| Define deep occlusion (armpits, eyelid creases, mouth corners) | Crease + pinch |

---

## Topology budgets (Steam-Deck target)

- Traversal mesh: 3,000–8,000 tris.
- Cutscene / close-up LOD: up to ~25,000 tris.
- 3-loop rule: every bending joint (knee, elbow, shoulder,
  neck, jaw) needs ≥ 3 clean edge loops to distribute weights
  and prevent volume collapse during deformation.
- High-frequency detail (pores, micro-wrinkles, fabric threads)
  goes on a baked normal map, NEVER into base geometry.

---

## Why this is filed, not active

Active mandate (verbatim, from session 2026-06-16):

> "we are going to stop with figures. you haven't made progress.
>  go back to polishing the neighborhood."

> "don't add more props until the landscape terrain and roads
>  and placement of terrain objects is good. the only exception
>  for now are road and terrain props or fixes."

Don't re-open this without an explicit "restart figure work"
request from the user. If they do, point them here first so
they can review proportions/topology budget before another
round.

---

## Reference asset on file (2026-06-16)

User uploaded `424cb8fa-planar_human_base_rigs.glb` —
"PLANAR HUMAN BASE RIGS" by dacancino on Sketchfab,
CC-BY-4.0. Source:
https://sketchfab.com/3d-models/planar-human-base-rigs-15a1d670d29b4195a10c23dca0d13da9

This is a vetted real-world example of exactly what we're
targeting: planar (Asaro-style) low-poly base meshes for
male + female figures, fully rigged.

### Topology budget (matches our target)

Per figure (the file contains a male + female pair):

| Mesh | Verts | Tris | Notes |
|------|------:|-----:|-------|
| body shell | ~5,372 | ~3,592 | UV-unwrapped, normals, flat-shaded "sculpture" material |
| skinned variant | ~5,250 | ~3,592 | + JOINTS_0 + WEIGHTS_0 |

So **~3,600 tris per figure** for the actual deformable mesh
— inside the 3,000-8,000 traversal target. This is concrete
evidence that the budget we picked is achievable, not
fantasy.

### Skeleton (34 joints per figure)

A bone-for-bone breakdown of how a production-ready game rig
condenses real anatomy:

```
root
└── pelvis_torsoControl
    ├── pelvis_independent
    │   ├── thigh.L → calf.L
    │   └── thigh.R → calf.R
    └── lumbar1 → lumbar2 → ribcage     ← spine = 3 bones, not 24
        ├── neck1 → neck2 → head        ← 2 neck bones, head separate
        ├── clavicle.L → upperArm.L
        │   → upperArm_rotate.L          ← TWIST bone (50% roll)
        │   → foreArm.L
        │   → foreArm_rotate.L           ← TWIST bone
        │   → hand.L                      ← single bone, no fingers
        └── clavicle.R → … (mirror)

footControl.L / footControl.R              ← IK leaf at root level
  ├── footToes.L/R
  └── footArch.L/R → footIK.L/R
```

Critical patterns to copy:

- **Twist bones** between upperArm/foreArm and between
  foreArm/hand. Without these, rolling the wrist 90° produces
  the classic "candy-wrapper" mesh collapse. The intermediate
  bone takes ~50% of the parent's roll.
- **Pelvis split**: `pelvis_torsoControl` carries the torso
  chain UP and `pelvis_independent` carries the legs DOWN.
  This lets the torso lean independently of the legs without
  the hip bones rotating into the thighs.
- **Spine = 3 bones**. lumbar1 + lumbar2 + ribcage is enough
  to read as a curving spine in animation; more is wasted
  rig overhead.
- **Hand = 1 bone**. No fingers in this rig. Fingers go on
  the close-up cinematic LOD, not on the open-world mesh.
- **Foot IK chain** at the root, not under the leg. The
  `footControl` is a separate sibling of the pelvis, which
  is how a Maya/Blender HumanIK chain expects to be driven.

### Proportions

- Mesh bbox height: **3.608 units**.
- Head height (1/8 of total): **0.451 units**.
- Bbox width at shoulders ≈ **1.33 units** → ~2.95 head-widths
  wide. Matches the 2.5-3 head-widths target for adult male.
- Two figures sit side by side at X≈0 and X≈3.0; widths
  match the male/female split.

### Materials

- Three materials total: `sculpture`, `sculpture.001`,
  `testLight`. Zero textures — `TEXCOORD_0` exists (UVs are
  laid out) but no image references. So the reference is
  rendered with flat shading + lighting only. This is a
  match for our locale pipeline (vertex colours / no
  texture assets).

User also uploaded the same model as a Sketchfab download zip
(`586dce8b-planar_human_base_rigs.zip`) containing
`scene.gltf` + `scene.bin` + `license.txt`. The split-file
glTF is friendlier for inspection (JSON header is plain text).
Same 83 nodes / 4 meshes / 2 skins as the GLB.

### Attribution requirement (CC-BY-4.0)

If we ever ship a derivative of this rig, the project must
include this credit verbatim:

> This work is based on "PLANAR HUMAN BASE RIGS"
> (https://sketchfab.com/3d-models/planar-human-base-rigs-15a1d670d29b4195a10c23dca0d13da9)
> by dacancino (https://sketchfab.com/dacancino) licensed
> under CC-BY-4.0
> (http://creativecommons.org/licenses/by/4.0/)

Commercial use IS allowed. The bar is just visible
attribution somewhere in the game (credits scene, README).

### If we ever resume figure work

1. The reference files live in the user's `~/.claude/uploads/`
   sandbox (not committed into the repo). If we restart,
   either:
   - re-download from Sketchfab, commit into
     `lore/refs/humans/` alongside a `CREDITS.md` that
     embeds the attribution block above; OR
   - open it in Blender on the Deck and use it purely as
     a sculpting reference for our own from-scratch mesh
     (no attribution needed if no part of the original is
     shipped).
2. Match the joint hierarchy exactly. Build the skeleton
   first, then sculpt to it.
3. Match the tri-count: target ~3,600 tris per figure for
   the LOD0 deformable mesh.
4. Use the planar `sculpture` material as the look reference
   — flat-shaded planes catching real Light3D nodes, not
   smooth Gouraud-shaded organic blobs.
