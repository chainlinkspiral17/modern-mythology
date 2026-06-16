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
