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

---

## Deep read of the mesh (2026-06-16, from .gltf+.bin)

Parsed 5,250 verts × 3,592 tris of the male mesh directly
from `scene.bin`. Findings beyond the metadata:

### What the silhouette actually looks like

Front-view ASCII silhouette (32 columns × 40 rows, derived
from rasterising the actual mesh vertices). The `·` markers
are the 8-head ideal Y-lines.

```
              #######             ← head crown
              #######
             #########            ← skull mid
             #########
  ·           #######            ·  1H = chin
           #############          ← neck/shoulder transition
        #### ######### ####       ← clavicle peak
       #####################      ← arms hanging
      #######################
  ·   #######################    ·  2H = nipple line
       #####################      ← chest
      #####  ### # ###  #####     ← arms-to-torso gap visible
     ##### ############# #####
    #####  ##### # #####  #####
  ·#####    ## # # # ##    ##### ·  3H = navel / waist
   ###### ##   # # #   ## ######
   ###    ###### # ######    ###  ← hand at hip (widest pt)
   ##     ####  ###  ####     ##
  ###     # #### # #### #     ###·  4H = crotch (midpoint)
  ####    ## ######### ##    #####
  #####   ### ####### ###   #####
  ##      ### ####### ###      ##
   ##     ##  #######  ##     ##
  ·        ## ####### ##         ·  5H = mid-thigh
           #############
            ###########
            ###########
           ###### ######
  ·        ####     ####         ·  6H = knee
           #### ### ####
            ##### #####
            #         #
            ##### #####
  ·            #   #             ·  7H = mid-shin
             ## # # ##
             #########
             #### ####
           ###### ######
             #       #            ← ankle / foot
```

### Real-data measurements

- **Total height**: 3.609 units. Head height (1/8): 0.451.
- **Width at hip level** (widest point): 1.33 units —
  this is fingertip-to-fingertip with arms hanging,
  NOT shoulder width. Easy to confuse.
- **Shoulder width** (peak at y≈2.93, before arms hang
  below): 0.81 units = **1.8 head-widths**. That's
  narrower than the male athletic ideal (2.5-3 head-widths),
  suggesting this base mesh is gender-neutral and meant to
  be sculpt-pushed for masculine shoulders per character.
- **Female silhouette** (mesh 2): same height 3.61, width
  1.25 (slightly narrower). Visible wasp-waist at 3H, hip
  flare at 4H. Same topology, displaced.
- **Body depth** (Z): 0.58 units. Depth/height ratio 0.16,
  matches real human ~0.18.

### Edge loops at joints (3-loop rule)

Knee region (Y 0.82-1.05, ~23cm vertical band): 14 distinct
Y-levels of vertices.

Elbow region (Y 2.16-2.35): 13 distinct Y-levels.

Both far exceed the 3-loop minimum. The mesh is
deformation-ready out of the box.

### Side view (planar nose / hanging arms)

```
         #  #   #   #         ← skull
       ##  # ## # ### ##
        # #  ###### ######   ← face plane + nose protrudes (+Z)
        ###################
          ###############
         #### # ###           ← neck slope
      ####  ########          ← shoulder
     ### #  #  ### ###
    #### #  # # #########     ← arm hanging in front-and-side
     #####  # #### #######
      ## #  ## ###  ## ###    ← elbow
      ## #  # ##  #      #
       ####### ##    #  ##    ← waist
       ###### ###    #  ##
        #### ####    #  #
         ### ## ##      #
        ## ### ###  ### #     ← hip / gluteus
       #  #   ##### ## #
      ##      ###   ## #      ← thigh
      #    #   ## #####
      ### #  #########        ← knee
       ####   #########
      ###    ##########       ← shin
       #    #  #  #####
       # ##  #  ####          ← ankle
       #### ### ####
       ## # ## ###
       ### ## ###
     ####### ####             ← foot
   #  #  #   # #
    #   # ### #
   ## #  # ###
       #
    ####### #
           #
     ### ##                   ← toes pointing FORWARD (+Z)
       #  ##
    #######   #  #
   ## ## ## # ############
```

The nose pushes forward into +Z — that's the planar face
front plane catching the light. The foot extends forward
(toes at +Z) — note this is the "Z-up axes ARE LIES"
problem in reverse: in Blender Y is up here, foot points +Z.

### Concrete takeaways for OUR pipeline

1. **Width-at-hip is NOT shoulder width**. If we ever
   auto-place humans against props (chairs, doorways),
   measure the bone-derived shoulder width, not the bbox.
   The bbox includes arms hanging.

2. **One mesh, two figures**. Mesh 0/1 (male) and mesh 2
   (female) share IDENTICAL topology and edge loops —
   the same 3,592-tri base shape sculpt-displaced into a
   gendered silhouette. This is the procedural pattern we
   should adopt: one base mesh, multiple shape-key /
   displacement variants for body type.

3. **No textures, planar normals do the work**. The
   "sculpture" material is flat-shaded. The READ of the
   character comes from the silhouette + edge-discontinuity
   normals + lighting. This is exactly the locale
   constraint, transferred to characters.

4. **3-loop rule is over-satisfied here.** A modest
   character does NOT need a 24-spine articulation. The
   3-bone spine + 2-bone neck + IK-foot chain of this rig
   is enough for any open-world traversal animation.

5. **Hand = ONE box.** Stop modelling fingers. The pro
   reference confirms it.

6. **Twist bones matter MORE than fingers** for visual
   quality. The candy-wrapper deformation on rolled
   forearms is a silhouette-killer; fingers usually go
   unnoticed on 7-inch displays.

### Neck read (corrected — got compressed in the first pass)

The first 40-row silhouette was too coarse; the neck got
crushed into one row. Re-rasterised the upper body at
2.9 cm/row and pulled width-at-Y in 2 cm bins:

```
Y=3.30  w=0.295  ████████              ← head bone (jaw pivot)
Y=3.22  w=0.231  ██████                  jaw-to-neck transition
Y=3.20  w=0.233  ██████
Y=3.18  w=0.201  ██████                ← neck NARROWEST
Y=3.16  w=0.218  ██████                  1H mark (chin)
Y=3.14  w=0.247  ███████
Y=3.12  w=0.311  █████████
Y=3.10  w=0.280  ████████
Y=3.08  w=0.399  ███████████
Y=3.06  w=0.516  ███████████████
Y=3.04  w=0.529  ███████████████       ← neck1 bone (base of neck)
Y=3.02  w=0.632  ██████████████████
Y=3.00  w=0.737  ██████████████████████
Y=2.96  w=0.619  ██████████████████      clavicle build-up
Y=2.94  w=0.845  █████████████████████████ ← shoulder peak
```

Key dimensions:

- **Neck minimum width**: ~0.20 (at Y=3.18, just under the
  jaw line).
- **Neck height**: ~10-14 cm — from Y=3.20 (jaw base) down
  to Y=3.06 (collar peak).
- **Neck/head-width ratio**: 0.20 / 0.34 ≈ **0.59**. Neck
  is roughly 60% the width of the head. Real-anatomy
  reference is ~50-65%, so this matches.
- **Neck-to-shoulder rise**: width goes from 0.20 → 0.85
  in just 24 cm of Y, with the steepest climb between
  Y=3.10 and Y=2.94 (0.28 → 0.85 over 16 cm). That's the
  **trapezius slope** — the sharp diagonal from skull-base
  down to deltoid that distinguishes a real human neck
  from a tube.

Bone layout in this 14 cm band: `head` at Y=3.30 (jaw
pivot), `neck2` between, `neck1` at Y=3.04 (skull base).
**Two neck bones** — one for the head-tilt at the
skull-base, one for the upper-spine sway. This is what
enables looking-around animations without the chin
penetrating the chest.

Lesson for our sculpts: the neck silhouette is THREE Y-bands,
not one tube:

1. **Neck proper** (narrow column): ~10 cm tall, ~60% of
   head width.
2. **Trapezius slope** (rapid widening): ~6-8 cm, diagonal
   from neck base to clavicle peak.
3. **Clavicle / shoulder peak**: ~3-5 cm before arms hang.

Skipping the middle band — going straight from "narrow
neck" to "wide shoulders" — is the single most common
beginner read of the neck, and it's wrong. The traps
carry the visual weight.

### Open question for next session

The base mesh has narrow shoulders (1.8 head-widths). Real
adult male is 2.5-3. The reference is a gender-NEUTRAL
foundation. If we use this as a starting point, every male
character needs explicit shoulder-broadening sculpt.

Alternatively: re-target. Two base meshes —
`male_athletic_base` (3 head-widths shoulders) and
`female_base` (1.5 head-widths shoulders) — both built off
the same edge-loop layout but with the planar shifts
pre-sculpted.
2. Match the joint hierarchy exactly. Build the skeleton
   first, then sculpt to it.
3. Match the tri-count: target ~3,600 tris per figure for
   the LOD0 deformable mesh.
4. Use the planar `sculpture` material as the look reference
   — flat-shaded planes catching real Light3D nodes, not
   smooth Gouraud-shaded organic blobs.
