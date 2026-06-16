# Character Modeling Notes — Reference

## Frasier — canonical concept (2026-06-16)

The user provided two reference images that overturned my notes:

- **Young Black man** (late 20s/early 30s, not "middle-aged
  creaky" — that quote from `_VOL6_WIKI.md` is about vol6-era
  Frasier; vol5 Frasier is young)
- **Locs / dreadlocks** — twisted strands going up + back. NOT
  an afro. (My earlier hair_style='unkempt_afro' was wrong.)
- **Athletic build** — male_avg proportions, not male_tall lean
- **Olive bomber jacket worn OPEN** — two side panels visible,
  dark t-shirt visible in the chest gap
- **"GEARING CORP" tee** — dark t-shirt with a cream/grey gear
  logo on the chest centerline (the printed band-tee / dev-shop
  vibe)
- **Dark jeans** + dark shoes

Pose canon: at his workbench in the Cathedral, holding a
soldering iron in one hand, working on a circuit board with
the other. Lean-forward posture, focused face.

Code spec updated (commit pending). 'locs' hair style added,
'open_jacket' clothing helper added with shirt + logo + side
panels.

---

## Procedural human attempts — WITHDRAWN (2026-06-16)

After iterating procedural figures (cross-section lofts with
asymmetric Z, intermediate rings, split legs, outboard arms)
the user concluded: **"go back to using the reference. you
fundamentally do not understand."**

Decision: **the planar reference IS the figure.** No more
procedural attempts. `human_midtier.py` stays in tree as a
documented dead end (the v1.1 version got brief moderate
approval before later iterations regressed). All character
work going forward instances the reference mesh via the
`_import_planar_sources` / `_instance_planar_npc` pipeline
in `build_graustark.py`.

Failure trajectory recorded for the record:

> "that looks like the first human sculpt you've done I'm
>  moderately happy with. congrats and record for posterity."
> — v1.1 (commit 0e4a521)

> "your models are broken. this is what I was expecting"
> — v1.1 vs reference comparison

> "go back to using the reference. you fundamentally do not
>  understand."
> — final call (commit pending)

File: `godot/tools/blender/locales/human_midtier.py`

Specs that worked:
- ~2,350 tris per figure (65% of the planar reference's ~3,600;
  12× the primitive HCE `human_figure`'s ~200)
- 24 verts per body ring
- Asymmetric cross-sections — separate radii for front/side/back
  in X AND for front/back in Z. Chest bulges forward, spine pulls
  back, butt back, belly forward. This single change is what
  pushed past the previous "stacked barrels" failure.
- 8H proportions exact (1.80 m total, head 0.225 m)
- Intermediate rings at every angular transition:
  - skull_apex between crown and hairline (replaces a bad ring
    that used absolute widths instead of HEAD_X multipliers —
    that ring was the "head spike" failure mode)
  - nose_upper, lower_lip, jaw_under in the face
  - trap_a_mid + trap_b_mid in the shoulder slope
  - above_knee + below_knee in the leg taper

Failure modes ruled out by user feedback during this session:
- v0 procedural blockout: "stacks of barrels" — symmetric ellipse
  cross-sections, no Z asymmetry
- v2 reactionary widening: "worse by every metric" — bumping all
  dimensions 20% to fix "emaciated" overshot. Reverted.
- Intermediate v1: "emaciated and spiky" — dimensions were OK,
  but the head's bad skull_top ring, sharp trap-slope steps, and
  pinched knee read as angular
- v1.1: just fix the angular transitions with intermediate rings;
  leave dimensions alone. WORKED.

Lesson for future iteration: when user says "emaciated AND spiky,"
the two complaints are independent. Spiky = angular transitions =
add intermediate rings. Emaciated = dimensions = bump radii.
Address them separately, not together.

The body-type variants (male_avg / male_tall / male_heavy /
female_avg / female_slim / teen / child / elderly) all share the
same edge-loop topology and intermediate-ring layout; only the
shoulder/hip/waist/depth radii vary by profile.

---

## Direction (decided 2026-06-16, end of session)

After visual A/B comparison between the procedural blockout
(`build_planar_human.py` + cross-section lofting) and dacancino's
reference, the procedural approach was retired and the reference
was adopted as the canonical character base.

**Active pipeline:**

1. `lore/refs/humans/planar_human_base_rigs/` — reference assets
   in repo, CC-BY-4.0 attributed via `lore/refs/CREDITS.md`.
2. `godot/tools/blender/characters/import_planar_human_base.py`
   — imports the reference, splits male + female meshes, renames
   to project-consistent identifiers, exports to
   `godot/assets/3d/characters/human_{male,female}_base.glb`,
   saves a `human_base_workspace.blend` for sculpt iteration.
3. Sculpt variants ride on top of the base. Each variant is a
   shape-key driven displacement of the same topology, exported
   as a separate GLB by a future `build_human_variants.py`.

**Why this beats the procedural blockout:**

- Reference is ~3,600 tris per figure with sculpted topology that
  reads as human at planar / Asaro shading. Our procedural was
  ~1,470 tris of symmetric-ellipse cross-sections that read as
  stacked barrels.
- Skeleton matches: the reference uses the exact 34-bone
  hierarchy with twist intermediates + foot IK chain that we'd
  designed for our pipeline. Zero retargeting needed.
- One topology, sculpt-displaced for body variants → matches the
  "one base mesh, multiple displaced variants" pattern we'd
  identified as the right pipeline.

**`build_planar_human.py` is now reference-only** — kept in tree
because it documents the lessons (proportions, neck-band split,
face carving math) and the proportional jig is useful for QA
overlay against sculpt variants, but it is NOT the build path.

**Baselines confirmed by user (2026-06-16):** the male + female
GLBs produced by `import_planar_human_base.py` are THE base
models. Don't make new ones from scratch. All future character
work (NPC variants, body types, hair/clothes) sculpts ON TOP of
these two baselines.

---

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

### Face close-up read (2026-06-16)

Cropped Y=3.10-3.65 (head only, ~55cm tall) and re-rasterised
the front view at 1.5cm/row, this time with a depth ramp
` .:-=+*#%@` where the brightness = how far forward in +Z
the front-most vertex sits at each (X,Y) cell. Now the
sculpted features actually read:

```
                           =                       ← crown (Y=3.61)
                   :   *   *   *   :               ← hairline ridge
              =    .#  #   #   #  #.    =          ← brow ridge
             :  +                     +  :         ← orbit rim
                 *                   *
              :                         :
              =                         =
             -.+                       +.-           brow valley
                                                   ← (Y=3.43)
                   #     % % %     #                  brow→eye transition
            = =* #                   # *= =
            -=:. *   #   #%%%#   #   * .:=-          ← eye line (Y=3.38)
           - =+          #%%%#          += -          (eye sockets = %%%, deep recess)
             =+* #     # #%%%# #     # *+=
           --=+ *     # %%%%%%% #     * +=--
             =+.  #     %%%%%%%     #  .+=            cheekbone shelf
             ==+*      #%%%%%%%#      *+==
              =+=   #  #% %%% %#  #   =+=
               +=  #.   % %%% %   .#  =+           ← nose tip (Y=3.27) — protrudes
                +* *  ##%%%%%%%##  * *+              max-Z=+0.227, FRONT-MOST point
                +*:  ## %% % %% ##  :*+            ← mouth line (Y=3.23)
                =+  #.  ## % ##  .#  +=               philtrum + upper lip
                -     # #% % %# #     -              chin/jaw curve
                  :* +#         #+ *:
                       *#% % %#*
                 = =    +  *  +    = =             ← chin (1H) (Y=3.16)
               :    .      .      .    :
```

**What I can SEE in the sculpt that I missed before:**

- **Eye sockets are deep recesses** — they show as `%%%` (one ramp
  step from the back, ~4cm behind the eye-line surface).
  Measured depth: **4cm of recess** from nose-bridge to eye-socket
  floor.
- **Cheekbones form a shelf** under the eye sockets. The
  `#%%%%%%%#` band at Y≈3.22 is the cheekbone catching light:
  bright `#` on the outside, deep `%` toward the eye socket.
- **Nose has structure**: bridge from brow down to tip,
  flares slightly at the nostrils (visible `## %% % %% ##`
  at Y=3.27). The Keystone wedge between the eyebrows is
  faintly visible.
- **Lips wrap a barrel**, not flat — the mouth ASCII shows
  `+*: ## %% % %% ## :*+` with the philtrum (`%` between
  the lips) recessed and the lip edges (`*`) catching light.
- **Chin is rounded** but separate from the jaw line — the
  bottom `*#% % %#*` shows the chin's own depth peak.

**Measured Z protrusion down the centerline:**

```
Y=3.60  crown     Z=+0.114  (recedes back from face plane)
Y=3.55  hairline  Z=-0.157  (BACK of head, hair sweep)
Y=3.38  eye line  Z=+0.211
Y=3.27  nose tip  Z=+0.227   ← front-most point of face
Y=3.23  mouth     Z=+0.218
Y=3.17  chin      Z=+0.205
```

The nose tip is **16mm forward of the eye-line plane** —
modest, not a stylised pinocchio, planar-sculpt scale.

**Eye-line slice (top-down, Y=3.38):**

```
                         #####               ← back of head
                #   #             #   #      ← skull side
             #                           #
           ##                             ##
          ####                           ####  ← cheekbone shelves
            #                             #
             #                           #
                  #        #        #       ← face front
                                                center & sides
```

The XZ cross-section is a **rounded triangle with corners
pulled OUT for cheekbones** and the front centerline (nose
bridge) pulled forward. NOT a circle, NOT an oval. This is
the Asaro planar approach: hard normals at the cheek
shelves.

### Rule of thirds — measured, NOT idealised

The face vertical thirds (hairline → brow → nose → chin)
are NOT equal in this mesh:

```
hairline → brow      0.120  (31%)
brow → nose base     0.160  (41%)   ← oversized middle
nose base → chin     0.110  (28%)
ideal third          0.130  (33%)
```

The middle third (brow→nose) is **41%** of face length —
8% over ideal. The bottom third is 5% under. This is a
common real-face deviation (most real faces have a longer
middle third than the "rule" claims), and the mesh keeps
it honest rather than forcing a 33/33/33 grid.

Lesson: don't force perfect thirds in our sculpts. The
range 30-40% per third reads as "human face." A perfect
33% feels uncanny because no real face has it.

### Head width / 5-eyes rule — measured

- Head width at eye line: **0.326**
- One-eye-width = 0.326 / 5 = **0.065**
- Implies eye-to-eye gap (one eye-width): **6.5cm at this scale**

Spot-check the front-view ASCII: the eye-socket centers
sit at ~X=±0.06, gap ~0.065 → matches the 5-eyes rule
cleanly.

### What I'd carry into our sculpts

1. **Sculpt depth, not just outline.** The face front-view
   reads because the depth ramp shows planar shifts. A
   flat-Z face (everything at the same Z) would look like
   a mask, not a head. Each ASCII row has a +/-2cm Z
   gradient ACROSS X. Recreate that gradient.
2. **Eye sockets must be RECESSED**, not painted on. 4cm
   of recess at our character scale.
3. **Cheekbones are SHELVES** catching the side-light;
   not bumps, not curves. Hard normal shift.
4. **Nose protrudes 16mm.** Subtle. A stylised "long nose"
   would be 30-40mm. We've over-shot in earlier attempts.
5. **Don't force exact thirds** in face proportions. 30-40%
   per third reads better than perfect 33s.
6. **Hairline is on the BACK of the head, not the front.**
   The Z=-0.157 hairline value caught me; it's the volume
   sweep that goes BEHIND the brow ridge, not a forehead
   line.

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
