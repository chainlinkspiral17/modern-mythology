"""caltech_dabney — vol 3's Caltech: Dabney House and the tunnels under
campus, in 2003 and in 1945 (draft 1, 2026-10-17).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
Five areas in one GLB. Props that belong to one year carry the presets that
show them (`<Name>__<preset>…`; Background3D strips them elsewhere), so the
1945 courtyard is the 2003 courtyard from the same camera with 2003 taken out.

THE COURTYARD (origin) — 2003, mid-afternoon of Andy's arrival; and 1945.
  "courtyard archways"                  → the S wing's arcade
  "music from somewhere high up" / the inner windows' small speakers
                                       → Speaker_* on the upper sills (2003)
  "The Birth of God": "an old man in a striped shirt and overalls"
                                       → Mural_* on the W wing, the bench
                                         under it (2003)
  palms "with dead fronds fallen at the base"             → Palm_*
  "scraggly kittens"                    → Kitten_* (2003)
  Andy in 1945: no basketball hoop, no speakers in the windows, no umbrella
  table, the paintings and writing on the walls all different
                                       → Hoop_*, Umbrella_*, Speaker_*,
                                         Paint_* are 2003-only
THE SIDE YARD (x 16..30) — the couchmobile under its tarp, "a couch lifted
  on two large sets of wheels", the engine, the handlebar steering; the
  "overgrown ivy wall" between campus and Pasadena, the city beyond.
THE GAME ROOM (x 60..72, the basement) — "black leather couches" in a U
  facing the wall of TVs and monitors ("Cathode rays, LCD"), "miles of black
  rubber twine", the shelf of game boxes and jewel cases under the screens,
  the refrigerators "big and industrial" down one wall, the beige PC with
  its floppy drive in one corner, the sit-down arcade cabinet in another,
  the couch leather cut all over (vol 4: "GAY FOR C3PO"), the sprite murals.
SPENCER'S ROOM (x 80..84.6, upstairs) — Spencer on the floor in a blanket
  with the laptop, clothes heaped in the corners, magazines and textbooks,
  the frames on the wall: the long Contra sketch on blue grid paper.
THE TUNNELS (x 100..103.2, running north) — 2003: graffiti on everything,
  the rail to grind, doors with radiation signs, the checkpoint, the clean
  room behind reinforced glass, the racquetball room lit by red and blue
  Chinese lanterns. 1945: the same corridor bare under fluorescent tubes.
  Off it, the bare room: "Not very big at all", cement, one door, one bulb.

Blender: x east, y north, z up; Godot (x, z, -y).

KNOTS (flagged in the brief, not fixed): ch2 has Jack alone find Andy in
his basement office, ch9 has Ron and Jack together; the 2003 sleep lab is in
"the new building, Moore" while 1945 Andy wakes where "There was a whole
office here". The set does not decide either.

DRAFT 2 targets: the arcade with real arch soffits (the spandrels are
prisms); the windows looked up at (ch6_dabney's "Look up at the windows");
the couchmobile uncovered (Andy sits on it); pinball tables and sprite
murals only if the poem is kept as set dressing; the tunnel's riders and
lab coats; the bare room's dark-to-light as a mid-scene bg switch; the
clinic (its own stem); Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_lathe, make_rot_box, make_blob,
                             make_tube, make_prism, make_taper_cyl, catenary, join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings
from _props.furniture import make_bed, make_chair
from _props.safety import make_fluorescent_tube_fixture
from _props.detail import make_wall_outlet

try:
    import bpy
except ImportError:
    bpy = None

Y2003 = "__dabney_courtyard__dabney_side_yard"
TUN2003 = "__caltech_tunnels"

STUCCO = (0.86, 0.80, 0.68, 1.0); STUCCO_DARK = (0.70, 0.64, 0.54, 1.0)
TILE_ROOF = (0.62, 0.34, 0.24, 1.0)
PAVER = (0.70, 0.66, 0.58, 1.0); PAVER_SEAM = (0.56, 0.52, 0.46, 1.0)
GLASS_DARK = (0.16, 0.20, 0.24, 1.0)
DIRT = (0.40, 0.32, 0.24, 1.0)
PALM_TRUNK = (0.56, 0.48, 0.38, 1.0); FROND = (0.30, 0.46, 0.22, 1.0); FROND_DEAD = (0.56, 0.44, 0.26, 1.0)
LEATHER = (0.17, 0.16, 0.17, 1.0); LEATHER_CUT = (0.40, 0.40, 0.40, 1.0)   # black leather, lifted so it reads by screen light
CARPET = (0.30, 0.24, 0.26, 1.0)
BEIGE = (0.80, 0.76, 0.66, 1.0)
CEMENT = (0.58, 0.57, 0.54, 1.0)

CX0, CX1, CY0, CY1, BH = -12.0, 12.0, 0.0, 18.0, 8.0     # courtyard, building height
ARC_Y = 0.0                                               # the arcade's line (the S wing)


def join_named(prefix, out_name):
    """Join meshes whose names start with `prefix` into one named `out_name`
    — join_stock's idea for a per-preset group (its key would lose the
    `__<preset>` suffix Background3D reads)."""
    if bpy is None:
        return
    objs = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith(prefix)]
    if len(objs) < 2:
        return
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    objs[0].name = out_name
    bpy.ops.object.select_all(action='DESELECT')


# ── the courtyard ─────────────────────────────────────────────────────
def palm(prefix, x, y, h, seed=0, z0=0.0):
    make_taper_cyl(f"{prefix}_Trunk", (x, y, z0 + h / 2.0), 0.26, 0.17, h, PALM_TRUNK, segments=10)
    h += z0
    make_cyl(f"{prefix}_Boot", (x, y, h - 0.25), 0.30, 0.5, (0.46, 0.38, 0.28, 1.0), segments=10)
    for k in range(11):
        a = k * (2.0 * math.pi / 11.0) + seed * 0.3
        droop = 0.35 + (k % 3) * 0.15
        L = 2.6
        cx = x + math.cos(a) * L * 0.45
        cy = y + math.sin(a) * L * 0.45
        make_rot_box(f"{prefix}_Frond_{k}", (cx, cy, h + 0.10 - droop * 0.6), (L, 0.42, 0.04),
                     FROND if k % 4 else (0.36, 0.50, 0.26, 1.0), yaw=a, pitch=droop)
    # the dead fronds hanging under the crown and fallen at the base
    for k in range(4):
        a = k * 1.6 + seed
        make_rot_box(f"{prefix}_Dead_Hang_{k}", (x + math.cos(a) * 0.22, y + math.sin(a) * 0.22, h - 1.1), (0.10, 0.36, 1.6),
                     FROND_DEAD, yaw=a, roll=0.25)
    for k in range(3):
        a = k * 2.1 + seed * 0.7
        make_rot_box(f"{prefix}_Dead_Fallen_{k}", (x + math.cos(a) * 1.1, y + math.sin(a) * 1.1, z0 + 0.03), (2.2, 0.38, 0.04),
                     FROND_DEAD, yaw=a + 0.4)


def facade_windows(prefix, along, line, start, end, floors=(1.3, 5.0), step=3.0, w=1.2, h=1.6, sign=1, speakers=False):
    """Dark window recesses with sills on a facade. along 'X' (N/S facades)
    or 'Y' (E/W facades); `sign` is the side the courtyard lies on."""
    k = 0
    p = start
    while p <= end + 1e-6:
        for fz in floors:
            z = fz + h / 2.0
            if along == 'X':
                make_box(f"{prefix}_Win_{k}", (p, line + sign * 0.02, z), (w, 0.04, h), GLASS_DARK)
                make_box(f"{prefix}_Win_{k}_Mull", (p, line + sign * 0.05, z), (0.05, 0.03, h), STUCCO_DARK)
                make_box(f"{prefix}_Win_{k}_Sill", (p, line + sign * 0.10, fz - 0.03), (w + 0.16, 0.20, 0.06), STUCCO_DARK)
                if speakers and fz > 3 and k % 2 == 0:
                    make_box(f"Speaker_{prefix}_{k}" + Y2003, (p + 0.30, line + sign * 0.12, fz + 0.11), (0.18, 0.16, 0.22),
                             (0.12, 0.12, 0.12, 1.0))
            else:
                make_box(f"{prefix}_Win_{k}", (line + sign * 0.02, p, z), (0.04, w, h), GLASS_DARK)
                make_box(f"{prefix}_Win_{k}_Mull", (line + sign * 0.05, p, z), (0.03, 0.05, h), STUCCO_DARK)
                make_box(f"{prefix}_Win_{k}_Sill", (line + sign * 0.10, p, fz - 0.03), (0.20, w + 0.16, 0.06), STUCCO_DARK)
                if speakers and fz > 3 and k % 2 == 0:
                    make_box(f"Speaker_{prefix}_{k}" + Y2003, (line + sign * 0.12, p + 0.30, fz + 0.11), (0.16, 0.18, 0.22),
                             (0.12, 0.12, 0.12, 1.0))
            k += 1
        p += step


def build_courtyard():
    cx, cy = (CX0 + CX1) / 2.0, (CY0 + CY1) / 2.0
    make_floor("Court_Floor", (cx, cy, 0.0), size_x=(CX1 - CX0) + 0.4, size_y=(CY1 - CY0) + 0.4,
               palette={"vinyl": PAVER, "seam": PAVER_SEAM})
    # the wings as masses: the courtyard sees their faces
    make_box("Wing_N", (cx, CY1 + 4.0, BH / 2.0), ((CX1 - CX0) + 16.0, 8.0, BH), STUCCO)
    make_box("Wing_W", (CX0 - 4.0, (CY1 - 3.0) / 2.0, BH / 2.0), (8.0, (CY1 - CY0) + 3.0, BH), STUCCO)
    make_box("Wing_E_N", (CX1 + 2.0, 13.75, BH / 2.0), (4.0, 8.5, BH), STUCCO)
    make_box("Wing_E_S", (CX1 + 2.0, 1.75, BH / 2.0), (4.0, 9.5, BH), STUCCO)
    make_box("Wing_E_Over", (CX1 + 2.0, 8.0, (BH + 3.4) / 2.0), (4.0, 3.0, BH - 3.4), STUCCO)   # over the passage
    make_box("Wing_S_Back", (cx, ARC_Y - 3.0 - 4.0, BH / 2.0), ((CX1 - CX0) + 16.0, 8.0, BH), STUCCO)
    make_box("Wing_S_Upper", (cx, ARC_Y - 1.5, (4.4 + BH) / 2.0), ((CX1 - CX0), 3.0, BH - 4.4), STUCCO)
    for nm, (bx, by, bw, bd) in {"N": (cx, CY1 + 4.0, (CX1 - CX0) + 16.6, 8.6), "W": (CX0 - 4.0, cy, 8.6, (CY1 - CY0)),
                                 "S": (cx, ARC_Y - 5.5, (CX1 - CX0) + 16.6, 11.6), "E": (CX1 + 2.0, cy, 4.6, (CY1 - CY0))}.items():
        make_box(f"Roof_Eave_{nm}", (bx, by, BH + 0.12), (bw, bd, 0.24), TILE_ROOF)
    # the S wing's ground floor is the arcade: piers on the courtyard line,
    # arches between them, the covered walk behind with its doors
    make_box("Arcade_Walk", (cx, ARC_Y - 1.5, 0.01), ((CX1 - CX0), 3.0, 0.02), PAVER_SEAM)
    make_box("Arcade_Ceil", (cx, ARC_Y - 1.5, 4.36), ((CX1 - CX0), 3.0, 0.08), STUCCO_DARK)
    bay, pier, spring, top = 3.0, 0.50, 2.7, 4.4
    n = int((CX1 - CX0) / bay)
    for k in range(n + 1):
        x = CX0 + k * bay
        w = pier
        if k in (0, n):        # the end piers are half piers against the wings
            w = pier / 2.0
            x += (w / 2.0) * (1 if k == 0 else -1)
        make_box(f"Arcade_Pier_{k}", (x, ARC_Y - 0.25, spring / 2.0), (w, 0.5, spring), STUCCO)
    r = (bay - pier) / 2.0
    for k in range(n):
        x0 = CX0 + k * bay + pier / 2.0
        x1 = x0 + 2.0 * r
        xm = (x0 + x1) / 2.0
        for side in (-1, 1):
            # the spandrel: from the top corner, down the pier face, up the arc to the crown
            pts = [(x0 if side < 0 else x1, top), (x0 if side < 0 else x1, spring)]
            for j in range(1, 8):
                t = j / 8.0 * (math.pi / 2.0)
                pts.append((xm + side * r * math.cos(t), spring + r * math.sin(t)))
            pts.append((xm, top))
            poly = [(u - xm, v - (top + spring) / 2.0) for (u, v) in pts]
            if side > 0:
                poly = list(reversed(poly))
            make_prism(f"Arcade_Spandrel_{k}_{side:+d}", (xm, ARC_Y - 0.25, (top + spring) / 2.0), poly, 0.5, STUCCO, axis="Y")
        if k % 2 == 0:
            make_box(f"Arcade_Door_{k}", (xm, ARC_Y - 2.98, 1.1), (1.0, 0.04, 2.2), (0.40, 0.28, 0.18, 1.0))
    facade_windows("Fac_S", 'X', ARC_Y, CX0 + 1.5, CX1 - 1.5, floors=(5.2,), step=3.0, sign=1, speakers=True)
    facade_windows("Fac_N", 'X', CY1, CX0 + 2.0, CX1 - 2.0, step=4.0, sign=-1, speakers=True)
    facade_windows("Fac_E", 'Y', CX1, 2.0, 16.0, floors=(5.0,), step=3.5, sign=-1, speakers=True)
    facade_windows("Fac_W_Up", 'Y', CX0, 2.0, 16.0, floors=(5.0,), step=3.5, sign=1, speakers=True)
    # the W wing's ground floor: the mural wall. "The Birth of God": an old
    # man in a striped shirt and overalls, on a painted ground (2003)
    mx, my = CX0 + 0.03, 9.0
    make_box("Mural_Ground" + Y2003, (mx, my, 2.4), (0.02, 6.0, 3.8), (0.40, 0.56, 0.70, 1.0))
    make_box("Mural_Sun" + Y2003, (mx + 0.01, my + 1.6, 3.5), (0.02, 1.6, 1.4), (0.92, 0.74, 0.30, 1.0))
    make_box("Mural_Earth" + Y2003, (mx + 0.01, my, 0.9), (0.02, 6.0, 0.8), (0.50, 0.40, 0.26, 1.0))
    for k in range(6):
        make_box(f"Mural_Shirt_Stripe_{k}" + Y2003, (mx + 0.02, my - 0.4, 2.55 + k * 0.12), (0.02, 1.0, 0.06),
                 ((0.86, 0.84, 0.80, 1.0), (0.66, 0.20, 0.18, 1.0))[k % 2])
    make_box("Mural_Overalls" + Y2003, (mx + 0.025, my - 0.4, 2.0), (0.02, 1.06, 1.4), (0.24, 0.34, 0.56, 1.0))
    make_box("Mural_Overall_Bib" + Y2003, (mx + 0.03, my - 0.4, 2.85), (0.02, 0.56, 0.50), (0.24, 0.34, 0.56, 1.0))
    make_box("Mural_Head" + Y2003, (mx + 0.025, my - 0.4, 3.55), (0.02, 0.56, 0.62), (0.86, 0.68, 0.54, 1.0))
    make_box("Mural_Beard" + Y2003, (mx + 0.03, my - 0.4, 3.32), (0.02, 0.50, 0.30), (0.92, 0.92, 0.90, 1.0))
    for s in (-1, 1):
        make_box(f"Mural_Arm_{s:+d}" + Y2003, (mx + 0.025, my - 0.4 + s * 0.75, 2.9), (0.02, 0.50, 0.18), (0.86, 0.68, 0.54, 1.0))
    make_box("Mural_Title" + Y2003, (mx + 0.02, my + 1.6, 1.55), (0.02, 2.2, 0.20), (0.94, 0.92, 0.86, 1.0))
    # the bench under it (both years: Andy sits down there in 1945 too)
    make_box("Bench_Mural_Seat", (CX0 + 0.55, my, 0.45), (0.50, 3.2, 0.08), (0.46, 0.34, 0.22, 1.0))
    for s in (-1, 0, 1):
        make_box(f"Bench_Mural_Leg_{s:+d}", (CX0 + 0.55, my + s * 1.4, 0.205), (0.44, 0.10, 0.41), STUCCO_DARK)
    # the walls' other paintings and writing (2003)
    for k, (x, z, w, h, col) in enumerate(((-7.5, 2.2, 2.6, 1.4, (0.70, 0.30, 0.36, 1.0)), (3.8, 1.8, 1.8, 1.0, (0.30, 0.56, 0.42, 1.0)),
                                           (7.8, 2.6, 2.2, 0.6, (0.20, 0.20, 0.24, 1.0)))):
        make_box(f"Paint_N_{k}" + Y2003, (x, CY1 - 0.02, z), (w, 0.02, h), col)
    make_box("Paint_E_0" + Y2003, (CX1 - 0.02, 4.0, 2.0), (0.02, 1.6, 1.2), (0.80, 0.56, 0.20, 1.0))
    # the planting beds and the palms
    for k, (x, y, h) in enumerate(((-6.0, 13.0, 11.0), (6.5, 13.5, 12.5), (-6.5, 4.5, 10.0), (7.0, 5.0, 11.5))):
        make_box(f"Bed_Curb_{k}", (x, y, 0.08), (3.0, 3.0, 0.16), STUCCO_DARK)
        make_box(f"Bed_Dirt_{k}", (x, y, 0.17), (2.7, 2.7, 0.02), DIRT)
        palm(f"Palm_{k}", x, y, h, seed=k, z0=0.18)
    # the hoop on its pole by the E wing (2003)
    make_cyl("Hoop_Pole" + Y2003, (9.6, 16.4, 1.6), 0.06, 3.2, (0.30, 0.32, 0.36, 1.0), segments=8)
    make_box("Hoop_Arm" + Y2003, (9.6, 16.0, 3.15), (0.06, 0.80, 0.06), (0.30, 0.32, 0.36, 1.0))
    make_box("Hoop_Board" + Y2003, (9.6, 15.6, 3.30), (1.8, 0.04, 1.05), (0.92, 0.92, 0.90, 1.0))
    make_lathe("Hoop_Rim" + Y2003, (9.6, 15.32, 3.05), [(0.23, 0.0), (0.24, 0.01), (0.23, 0.02)], (0.86, 0.36, 0.16, 1.0),
               segments=16, loop=True)
    make_box("Hoop_Rim_Bracket" + Y2003, (9.6, 15.53, 3.05), (0.12, 0.10, 0.03), (0.86, 0.36, 0.16, 1.0))
    # the umbrella table and its chairs (2003), the trash can
    ux, uy = 3.0, 12.5
    make_cyl("Umbrella_Table_Top" + Y2003, (ux, uy, 0.74), 0.55, 0.03, (0.88, 0.88, 0.86, 1.0), segments=16)
    make_cyl("Umbrella_Table_Stem" + Y2003, (ux, uy, 0.36), 0.04, 0.72, (0.40, 0.40, 0.42, 1.0), segments=8)
    make_cyl("Umbrella_Pole" + Y2003, (ux, uy, 1.48), 0.02, 1.44, (0.40, 0.40, 0.42, 1.0), segments=6)
    make_lathe("Umbrella_Canopy" + Y2003, (ux, uy, 2.10), [(0.0, 0.40), (0.6, 0.24), (1.15, 0.0), (1.15, -0.02), (0.0, 0.38)],
               (0.20, 0.42, 0.40, 1.0), segments=8)
    for k in range(4):
        a = k * math.pi / 2.0 + 0.3
        make_chair(f"Umbrella_Chair_{k}" + Y2003, ux + math.cos(a) * 0.95, uy + math.sin(a) * 0.95, yaw=a + math.pi / 2.0,
                   wood=(0.86, 0.86, 0.84, 1.0))
    make_cyl("Trash_Can" + Y2003, (CX0 + 0.5, 3.2, 0.45), 0.28, 0.90, (0.30, 0.34, 0.30, 1.0), segments=12)
    # the kittens by the bench (2003)
    for k, (x, y) in enumerate(((CX0 + 1.6, 7.2), (CX0 + 2.2, 7.6), (CX0 + 1.3, 11.4))):
        make_blob(f"Kitten_{k}_Body" + Y2003, (x, y, 0.09), 0.10, ((0.58, 0.42, 0.26, 1.0), (0.30, 0.28, 0.26, 1.0))[k % 2],
                  noise=0.05, seed=k)
        make_blob(f"Kitten_{k}_Head" + Y2003, (x + 0.11, y + 0.02, 0.17), 0.055, ((0.58, 0.42, 0.26, 1.0), (0.30, 0.28, 0.26, 1.0))[k % 2],
                  noise=0.0, seed=k + 9)
    # through the E passage: the side yard (the passage floor)
    make_box("Passage_Floor", (CX1 + 2.0, 8.0, 0.01), (4.0, 3.0, 0.02), PAVER_SEAM)


def build_side_yard():
    """East of the E wing: lawn and a path, the couchmobile under its tarp
    against the wing, the overgrown ivy wall, Pasadena beyond."""
    x0, x1 = CX1 + 4.0, 30.0
    make_box("Yard_Lawn", ((x0 + x1) / 2.0, 8.0, -0.01), (x1 - x0, 40.0, 0.02), (0.36, 0.50, 0.26, 1.0))
    make_box("Yard_Path", ((x0 + x1) / 2.0, 8.0, 0.005), (x1 - x0, 1.6, 0.01), PAVER)
    # the couchmobile: a couch on two big sets of wheels, the engine, the
    # handlebar — a tarp over most of it, roped
    kx, ky = x0 + 1.6, 3.4
    for s in (-1, 1):
        for e in (-1, 1):
            make_cyl(f"Couchmobile_Wheel_{s:+d}_{e:+d}", (kx + s * 0.70, ky + e * 0.95, 0.38), 0.38, 0.22, (0.10, 0.10, 0.10, 1.0),
                     axis='X', segments=14)
    make_box("Couchmobile_Frame", (kx, ky, 0.48), (1.10, 2.10, 0.10), (0.36, 0.36, 0.38, 1.0))
    make_box("Couchmobile_Engine", (kx, ky - 1.20, 0.62), (0.46, 0.40, 0.36), (0.30, 0.30, 0.30, 1.0))
    make_tube("Couchmobile_Handlebar", [(kx - 0.20, ky + 0.70, 0.96), (kx - 0.40, ky + 1.05, 1.10), (kx + 0.40, ky + 1.05, 1.10),
                                       (kx + 0.20, ky + 0.70, 0.96)], 0.02, (0.56, 0.56, 0.58, 1.0))
    make_chamfer_box("Couchmobile_Tarp", (kx, ky - 0.10, 0.92), (1.30, 2.10, 0.84), (0.26, 0.38, 0.56, 1.0), chamfer=0.14)
    make_box("Couchmobile_Tarp_Skirt", (kx, ky - 0.10, 0.56), (1.34, 2.14, 0.12), (0.24, 0.36, 0.54, 1.0))
    for k in range(3):
        make_box(f"Couchmobile_Rope_{k}", (kx, ky - 0.80 + k * 0.70, 0.93), (1.36, 0.02, 0.86), (0.82, 0.76, 0.56, 1.0))
    # the overgrown ivy wall: block wall under lumps of ivy
    make_box("Ivy_Wall", (x1, 8.0, 1.5), (0.40, 40.0, 3.0), (0.56, 0.54, 0.50, 1.0))
    for k in range(26):
        y = -11.0 + k * 1.55
        make_blob(f"Ivy_{k}", (x1 - 0.10, y, 1.5 + (k % 3) * 0.4), 1.0 + (k % 4) * 0.15, (0.20, 0.38, 0.18, 1.0),
                  noise=0.28, seed=k)
    for k, (y, h) in enumerate(((-2.0, 10.0), (15.0, 12.0))):
        palm(f"Yard_Palm_{k}", x1 - 3.5, y, h, seed=k + 5)
    # Pasadena beyond: low buildings, street trees, the mountains
    for k in range(7):
        y = -18.0 + k * 7.0
        h = 5.0 + (k % 3) * 3.0
        make_box(f"City_Bldg_{k}", (x1 + 16.0 + (k % 2) * 6.0, y, h / 2.0), (8.0, 5.5, h),
                 ((0.82, 0.78, 0.70, 1.0), (0.74, 0.70, 0.66, 1.0), (0.86, 0.82, 0.76, 1.0))[k % 3])
    for k in range(8):
        make_blob(f"City_Tree_{k}", (x1 + 7.0, -16.0 + k * 6.0, 3.6), 2.2, (0.28, 0.42, 0.24, 1.0), noise=0.3, seed=k + 30)
        make_cyl(f"City_Tree_{k}_Trunk", (x1 + 7.0, -16.0 + k * 6.0, 1.2), 0.18, 2.4, PALM_TRUNK, segments=8)
    make_prism("Mountains", (x1 + 120.0, 8.0, 0.0), [(-140.0, 0.0), (-80.0, 34.0), (-30.0, 22.0), (10.0, 46.0), (60.0, 28.0),
                                                     (140.0, 38.0), (140.0, 0.0)][::-1], 4.0, (0.50, 0.56, 0.66, 1.0), axis="X")


# ── the game room (basement) ──────────────────────────────────────────
GX0, GX1, GY0, GY1, GH = 60.0, 72.0, 0.0, 10.0, 2.8


def couch(prefix, cx, cy, length, face, carved=False):
    """A black leather couch; `face` is the direction its sitters look."""
    yaw = {"+Y": 0.0, "-Y": math.pi, "+X": -math.pi / 2.0, "-X": math.pi / 2.0}[face]
    c, s = math.cos(yaw), math.sin(yaw)

    def at(u, v):       # u along the couch, v toward its front
        return (cx + u * c - v * s, cy + u * s + v * c)
    make_rot_box(f"{prefix}_Base", (*at(0.0, 0.0), 0.20), (length, 0.92, 0.40), LEATHER, yaw=yaw)
    make_rot_box(f"{prefix}_Back", (*at(0.0, -0.36), 0.66), (length, 0.22, 0.56), LEATHER, yaw=yaw)
    for e in (-1, 1):
        make_rot_box(f"{prefix}_Arm_{e:+d}", (*at(e * (length / 2.0 - 0.11), 0.0), 0.52), (0.22, 0.92, 0.26), LEATHER, yaw=yaw)
    n = max(2, int(length / 0.75))
    w = (length - 0.44) / n
    for k in range(n):
        u = -length / 2.0 + 0.22 + w * (k + 0.5)
        make_rot_box(f"{prefix}_Cush_{k}", (*at(u, 0.06), 0.47), (w - 0.02, 0.66, 0.14), (0.20, 0.19, 0.20, 1.0), yaw=yaw)
    if carved:
        # the cuts gone grey in their grooves: initials, dates, jokes, a name
        # scratched through to the stuffing (vol 4: "GAY FOR C3PO")
        for k in range(9):
            u = -length / 2.0 + 0.40 + k * (length - 0.8) / 8.0
            make_rot_box(f"{prefix}_Cut_{k}", (*at(u, -0.24), 0.70 + (k % 3) * 0.09), (0.16 + (k % 2) * 0.10, 0.004, 0.012),
                         LEATHER_CUT, yaw=yaw)
        make_rot_box(f"{prefix}_Cut_Stuffing", (*at(length * 0.18, -0.24), 0.60), (0.22, 0.004, 0.035), (0.86, 0.82, 0.70, 1.0),
                     yaw=yaw)
        make_rot_box(f"{prefix}_Cut_C3PO", (*at(-length * 0.20, -0.24), 0.82), (0.40, 0.004, 0.022), (0.40, 0.40, 0.40, 1.0), yaw=yaw)


def tv(prefix, x, y, z, w, kind, glow):
    """A screen on the wall of screens: 'crt' (deep box) or 'lcd' (thin)."""
    if kind == "crt":
        make_chamfer_box(f"{prefix}_Body", (x, y - 0.24, z + w * 0.38), (w, 0.48, w * 0.76), (0.12, 0.12, 0.13, 1.0), chamfer=0.03)
        make_box(f"{prefix}_Screen", (x, y - 0.485, z + w * 0.40), (w * 0.82, 0.006, w * 0.60), glow)
    else:
        make_box(f"{prefix}_Body", (x, y - 0.04, z + w * 0.30), (w, 0.06, w * 0.58), (0.10, 0.10, 0.11, 1.0))
        make_box(f"{prefix}_Screen", (x, y - 0.072, z + w * 0.30), (w * 0.94, 0.004, w * 0.52), glow)
        make_box(f"{prefix}_Foot", (x, y - 0.10, z + 0.01), (w * 0.30, 0.16, 0.02), (0.10, 0.10, 0.11, 1.0))


def build_game_room():
    cx, cy = (GX0 + GX1) / 2.0, (GY0 + GY1) / 2.0
    make_floor("Game_Floor", (cx, cy, 0.0), size_x=GX1 - GX0 + 0.4, size_y=GY1 - GY0 + 0.4,
               palette={"vinyl": CARPET, "seam": (0.26, 0.20, 0.22, 1.0)})
    make_box("Game_Ceil", (cx, cy, GH + 0.04), (GX1 - GX0 + 0.4, GY1 - GY0 + 0.4, 0.08), (0.56, 0.54, 0.50, 1.0))
    pal = {"wall": (0.66, 0.64, 0.60, 1.0), "baseboard": (0.24, 0.22, 0.22, 1.0)}
    make_wall("Game_Wall_N", (cx, GY1, 0), length=GX1 - GX0 + 0.4, height=GH, thickness=0.2, axis='X', palette=pal, baseboard_face_sign=-1)
    make_wall("Game_Wall_E", (GX1, cy, 0), length=GY1 - GY0 + 0.4, height=GH, thickness=0.2, axis='Y', palette=pal, baseboard_face_sign=-1)
    make_wall_with_openings("Game_Wall_S", (cx, GY0, 0), length=GX1 - GX0 + 0.4, height=GH, thickness=0.2, axis='X', palette=pal,
                            baseboard_face_sign=+1, openings=[(GX0 + 1.4, 1.0, 0.90, 2.0)])
    make_wall("Game_Wall_W", (GX0, cy, 0), length=GY1 - GY0 + 0.4, height=GH, thickness=0.2, axis='Y', palette=pal, baseboard_face_sign=+1)
    make_box("Game_Stair_Dark", (GX0 + 1.4, GY0 - 0.16, 1.0), (0.90, 0.10, 2.0), (0.06, 0.06, 0.07, 1.0))   # the stairwell up
    for k in range(3):
        make_fluorescent_tube_fixture(f"Fluor_Game_{k}", (GX0 + 3.0 + k * 3.0, 3.0, GH), length=1.20, width=0.30)
    # the wall of screens on the N wall: the long low shelf of game boxes,
    # the decks and consoles on it, CRTs and LCDs on it and on the wall above
    sy = GY1 - 0.10
    sx0, sx1 = GX0 + 2.0, GX1 - 2.6
    make_box("Media_Shelf_Top", ((sx0 + sx1) / 2.0, sy - 0.30, 0.62), (sx1 - sx0, 0.60, 0.04), (0.16, 0.14, 0.14, 1.0))
    make_box("Media_Shelf_Mid", ((sx0 + sx1) / 2.0, sy - 0.30, 0.30), (sx1 - sx0, 0.60, 0.03), (0.16, 0.14, 0.14, 1.0))
    for k in range(6):
        x = sx0 + k * (sx1 - sx0) / 5.0
        make_box(f"Media_Shelf_Upright_{k}", (min(max(x, sx0 + 0.02), sx1 - 0.02), sy - 0.30, 0.31), (0.04, 0.60, 0.62),
                 (0.16, 0.14, 0.14, 1.0))
    # under the screens: soft-cornered boxes, cracked jewel cases, burned discs
    boxcols = [(0.86, 0.80, 0.70), (0.30, 0.36, 0.56), (0.70, 0.22, 0.20), (0.20, 0.20, 0.22), (0.88, 0.86, 0.80), (0.36, 0.52, 0.30)]
    x = sx0 + 0.06
    k = 0
    while x < sx1 - 0.10:
        t = 0.03 if k % 3 else 0.012
        hh = 0.21 if k % 3 else 0.14
        make_box(f"Media_Stock_Box_{k}", (x, sy - 0.24, 0.035 + hh / 2.0 + 0.0), (t, 0.20, hh), (*boxcols[k % len(boxcols)], 1.0))
        make_box(f"Media_Stock_Box2_{k}", (x, sy - 0.24, 0.315 + hh / 2.0), (t, 0.20, hh), (*boxcols[(k + 2) % len(boxcols)], 1.0))
        x += t + 0.006
        k += 1
    make_box("Media_Floor_Plinth", ((sx0 + sx1) / 2.0, sy - 0.30, 0.0175), (sx1 - sx0, 0.60, 0.035), (0.16, 0.14, 0.14, 1.0))
    make_box("Floppy_Unlabeled", (sx0 + 1.20, sy - 0.48, 0.3165), (0.09, 0.09, 0.003), (0.16, 0.16, 0.18, 1.0))
    # the decks and consoles on top, the screens on them and the wall above
    decks = [(0.42, 0.30, 0.09, (0.18, 0.18, 0.20)), (0.36, 0.28, 0.08, (0.62, 0.62, 0.64)), (0.43, 0.30, 0.10, (0.14, 0.14, 0.16)),
             (0.26, 0.22, 0.08, (0.56, 0.56, 0.60)), (0.32, 0.26, 0.09, (0.20, 0.30, 0.20))]
    glows = [(0.40, 0.56, 0.84, 1.0), (0.80, 0.50, 0.70, 1.0), (0.44, 0.80, 0.56, 1.0), (0.86, 0.76, 0.44, 1.0), (0.56, 0.62, 0.90, 1.0)]
    n = 5
    for k in range(n):
        x = sx0 + 0.50 + k * (sx1 - sx0 - 1.0) / (n - 1)
        dw, dd, dh, dc = decks[k]
        make_box(f"Deck_{k}", (x, sy - 0.16, 0.64 + dh / 2.0), (dw, dd, dh), (*dc, 1.0))
        tv(f"TV_Low_{k}", x, sy, 0.64 + dh, 0.70 if k % 2 == 0 else 0.86, "crt" if k % 2 == 0 else "lcd", glows[k])
    for k in range(4):
        x = sx0 + 0.95 + k * (sx1 - sx0 - 1.9) / 3.0
        make_box(f"TV_Shelf_{k}", (x, sy - 0.26, 1.58), (1.04, 0.52, 0.04), (0.16, 0.14, 0.14, 1.0))
        for s in (-1, 1):
            make_box(f"TV_Shelf_{k}_Bracket_{s:+d}", (x + s * 0.40, sy - 0.26, 1.46), (0.04, 0.50, 0.20), (0.16, 0.14, 0.14, 1.0))
        tv(f"TV_High_{k}", x, sy, 1.60, 0.56 if k % 2 else 0.90, "lcd" if k % 2 == 0 else "crt", glows[(k + 2) % 5])
    # the miles of black rubber twine: cables looping down and along
    for k in range(7):
        x = sx0 + 0.3 + k * (sx1 - sx0 - 0.6) / 6.0
        make_tube(f"Cable_Stock_{k}", catenary((x, sy - 0.04, 1.58), (x + 0.6, sy - 0.04, 0.66), 0.25 + (k % 3) * 0.10),
                  0.012, (0.04, 0.04, 0.04, 1.0))
    for k in range(4):
        x = sx0 + 0.6 + k * 1.4
        make_tube(f"Cable_Stock_Floor_{k}", catenary((x, sy - 0.62, 0.64), (x + 0.5, sy - 1.10, 0.012), 0.10), 0.012,
                  (0.04, 0.04, 0.04, 1.0))
    # the U of couches, the back one carved
    couch("Couch_Back", cx - 0.40, 3.80, 3.2, "+Y", carved=True)
    couch("Couch_Left", GX0 + 2.30, 6.20, 2.6, "+X")
    couch("Couch_Right", GX1 - 3.10, 6.20, 2.6, "-X")
    for k, (x, y, yaw) in enumerate(((cx - 1.0, 6.4, 0.4), (cx + 0.8, 7.0, -0.9), (cx + 0.2, 5.6, 2.1))):
        make_rot_box(f"Controller_{k}", (x, y, 0.016), (0.15, 0.10, 0.03), (0.20, 0.20, 0.22, 1.0), yaw=yaw)
    make_rot_box("Controller_Couch", (cx - 1.1, 3.90, 0.555), (0.15, 0.10, 0.03), (0.30, 0.30, 0.34, 1.0), yaw=0.3)
    make_box("Andy_Notebook", (cx + 0.6, 3.92, 0.555), (0.18, 0.24, 0.03), (0.16, 0.20, 0.30, 1.0))
    # the refrigerators down the E wall: big, industrial, glass doors, drinks
    fx = GX1 - 0.10 - 0.40
    for k in range(5):
        y = 1.0 + k * 0.96
        make_box(f"Fridge_{k}_Body", (fx, y, 1.05), (0.80, 0.92, 2.10), (0.70, 0.72, 0.74, 1.0))
        make_box(f"Fridge_{k}_Glass", (fx - 0.402, y, 1.10), (0.004, 0.74, 1.70), (0.42, 0.52, 0.58, 1.0))
        make_box(f"Fridge_{k}_Handle", (fx - 0.42, y + 0.32, 1.10), (0.03, 0.03, 0.60), (0.80, 0.80, 0.82, 1.0))
        make_box(f"Fridge_{k}_Grille", (fx - 0.402, y, 0.12), (0.004, 0.80, 0.16), (0.20, 0.20, 0.22, 1.0))
        for j in range(4):
            for m in range(5):
                make_box(f"Fridge_Stock_{k}_{j}_{m}", (fx - 0.36, y - 0.28 + m * 0.14, 0.42 + j * 0.40), (0.06, 0.06, 0.20),
                         ((0.76, 0.84, 0.30, 1.0), (0.80, 0.30, 0.20, 1.0), (0.30, 0.50, 0.80, 1.0), (0.90, 0.60, 0.20, 1.0))[(k + j + m) % 4])
    # NW corner: the beige PC with its floppy drive on a small desk
    px, py = GX0 + 0.10 + 0.40, GY1 - 0.10 - 1.2
    make_box("PC_Desk_Top", (px, py, 0.72), (0.80, 1.00, 0.04), (0.50, 0.40, 0.30, 1.0))
    for s in (-1, 1):
        make_box(f"PC_Desk_Panel_{s:+d}", (px, py + s * 0.48, 0.35), (0.76, 0.04, 0.70), (0.44, 0.34, 0.26, 1.0))
    # (the desk is on the W wall: whoever sits here faces west)
    make_box("PC_Case", (px - 0.08, py - 0.10, 0.82), (0.42, 0.44, 0.16), BEIGE)
    make_box("PC_Floppy", (px + 0.132, py - 0.02, 0.84), (0.004, 0.12, 0.02), (0.20, 0.20, 0.20, 1.0))
    make_chamfer_box("PC_CRT", (px - 0.08, py - 0.10, 1.07), (0.38, 0.38, 0.34), BEIGE, chamfer=0.03)
    make_box("PC_CRT_Screen", (px + 0.112, py - 0.10, 1.08), (0.004, 0.28, 0.22), (0.30, 0.50, 0.46, 1.0))
    make_box("PC_Keyboard", (px + 0.26, py - 0.10, 0.745), (0.16, 0.44, 0.025), BEIGE)
    make_chair("PC_Chair", px + 0.66, py - 0.10, yaw=math.pi / 2.0, wood=(0.30, 0.30, 0.32, 1.0))
    # SW corner: the sit-down arcade cabinet, its attract mode on
    ax, ay = GX0 + 0.10 + 0.70, 2.70
    make_box("Arcade_Base", (ax, ay, 0.35), (1.30, 0.90, 0.70), (0.14, 0.12, 0.20, 1.0))
    make_box("Arcade_Seat", (ax + 0.30, ay, 0.62), (0.44, 0.56, 0.14), (0.60, 0.12, 0.12, 1.0))
    make_box("Arcade_SeatBack", (ax + 0.56, ay, 0.98), (0.10, 0.56, 0.60), (0.60, 0.12, 0.12, 1.0))
    make_box("Arcade_Hood", (ax - 0.36, ay, 1.20), (0.56, 0.90, 1.00), (0.14, 0.12, 0.20, 1.0))
    make_box("Arcade_Screen", (ax - 0.078, ay, 1.18), (0.004, 0.64, 0.48), (0.70, 0.40, 0.84, 1.0))
    make_box("Arcade_Marquee", (ax - 0.36, ay, 1.78), (0.58, 0.92, 0.18), (0.94, 0.80, 0.30, 1.0))
    make_box("Arcade_Panel", (ax - 0.02, ay, 0.76), (0.22, 0.70, 0.06), (0.20, 0.20, 0.26, 1.0))
    # the sprite murals (the poem's: kept to the W wall, low-key)
    for k in range(8):
        make_box(f"Sprite_Mural_{k}", (GX0 + 0.11, 5.0 + (k % 4) * 0.90, 1.55 + (k // 4) * 0.55), (0.006, 0.40, 0.36),
                 ((0.80, 0.30, 0.24, 1.0), (0.30, 0.60, 0.86, 1.0), (0.94, 0.80, 0.30, 1.0), (0.40, 0.76, 0.40, 1.0))[k % 4])
    make_wall_outlet("Outlet_Media", (GX0 + 3.5, GY1), axis='X', face_sign=-1)


# ── Spencer's room (upstairs) ─────────────────────────────────────────
SX0, SX1, SY0, SY1, SH = 80.0, 84.6, 0.0, 4.2, 2.6


def build_spencer_room():
    cx, cy = (SX0 + SX1) / 2.0, (SY0 + SY1) / 2.0
    make_floor("Sp_Floor", (cx, cy, 0.0), size_x=SX1 - SX0 + 0.4, size_y=SY1 - SY0 + 0.4,
               palette={"vinyl": (0.50, 0.42, 0.34, 1.0), "seam": (0.42, 0.34, 0.28, 1.0)})
    make_box("Sp_Ceil", (cx, cy, SH + 0.04), (SX1 - SX0 + 0.4, SY1 - SY0 + 0.4, 0.08), (0.88, 0.86, 0.80, 1.0))
    pal = {"wall": (0.84, 0.80, 0.70, 1.0), "baseboard": (0.40, 0.34, 0.28, 1.0)}
    make_wall_with_openings("Sp_Wall_E", (SX1, cy, 0), length=SY1 - SY0 + 0.4, height=SH, thickness=0.2, axis='Y', palette=pal,
                            baseboard_face_sign=-1, openings=[(2.4, 1.5, 1.2, 1.3)])
    make_box("Sp_Window_Glass", (SX1, 2.4, 1.5), (0.02, 1.2, 1.3), (0.70, 0.82, 0.92, 1.0))
    make_wall("Sp_Wall_N", (cx, SY1, 0), length=SX1 - SX0 + 0.4, height=SH, thickness=0.2, axis='X', palette=pal, baseboard_face_sign=-1)
    make_wall("Sp_Wall_W", (SX0, cy, 0), length=SY1 - SY0 + 0.4, height=SH, thickness=0.2, axis='Y', palette=pal, baseboard_face_sign=+1)
    make_wall_with_openings("Sp_Wall_S", (cx, SY0, 0), length=SX1 - SX0 + 0.4, height=SH, thickness=0.2, axis='X', palette=pal,
                            baseboard_face_sign=+1, openings=[(SX0 + 0.8, 1.0, 0.86, 2.0)])
    make_box("Sp_Door", (SX0 + 0.37, 0.10 + 0.43, 1.0), (0.04, 0.84, 2.0), (0.56, 0.44, 0.32, 1.0))
    # a plain bed against the N wall, unmade; a plain desk under the window
    make_bed("Sp_Bed", SX1 - 0.10 - 1.00, SY1 - 0.10 - 0.48, head="-X", w=0.95, d=1.95, made=False,
             blanket_col=(0.40, 0.42, 0.36, 1.0))
    # Spencer's spot on the floor: the blanket, the laptop open on it
    fx, fy = cx - 0.50, 1.90
    make_chamfer_box("Sp_Blanket", (fx, fy, 0.04), (1.20, 1.00, 0.08), (0.46, 0.30, 0.30, 1.0), chamfer=0.03)
    make_box("Sp_Laptop_Base", (fx + 0.10, fy - 0.10, 0.092), (0.30, 0.22, 0.024), (0.24, 0.24, 0.26, 1.0))
    make_rot_box("Sp_Laptop_Lid", (fx + 0.10, fy + 0.005, 0.20), (0.30, 0.012, 0.22), (0.24, 0.24, 0.26, 1.0), roll=-0.20)
    make_rot_box("Sp_Laptop_Screen", (fx + 0.10, fy - 0.002, 0.20), (0.27, 0.004, 0.19), (0.40, 0.56, 0.74, 1.0), roll=-0.20)
    # the clothes heaped over the corners
    for k, (x, y, r) in enumerate(((SX0 + 0.40, SY1 - 0.40, 0.50), (SX0 + 0.30, 0.70, 0.40), (SX1 - 0.45, 2.20, 0.36))):
        make_blob(f"Sp_Clothes_{k}", (x, y, r * 0.35), r, ((0.30, 0.34, 0.44, 1.0), (0.60, 0.56, 0.48, 1.0), (0.24, 0.24, 0.26, 1.0))[k],
                  noise=0.35, seed=k + 3, squash=0.45)
    # magazines and textbooks on the floor by the wall
    for k in range(6):
        make_rot_box(f"Sp_Mag_{k}", (SX0 + 1.10 + (k % 3) * 0.32, 3.40 + (k // 3) * 0.10, 0.012 + (k // 3) * 0.024),
                     (0.22, 0.28, 0.02 if k % 2 else 0.04), ((0.80, 0.30, 0.24, 1.0), (0.30, 0.40, 0.60, 1.0), (0.86, 0.84, 0.74, 1.0))[k % 3],
                     yaw=(k * 0.37) % 0.6 - 0.3)
    # the frames on the W wall: the long Contra sketch on blue grid paper,
    # Japanese characters down its margin, and smaller frames round it
    wx = SX0 + 0.11
    make_box("Frame_Contra", (wx, 2.0, 1.60), (0.03, 1.60, 0.46), (0.12, 0.12, 0.12, 1.0))
    make_box("Frame_Contra_Paper", (wx + 0.017, 2.0, 1.60), (0.004, 1.50, 0.38), (0.70, 0.80, 0.92, 1.0))
    for k in range(9):
        make_box(f"Frame_Contra_Grid_{k}", (wx + 0.020, 1.32 + k * 0.17, 1.60), (0.002, 0.004, 0.36), (0.50, 0.62, 0.86, 1.0))
    for k in range(5):
        make_box(f"Frame_Contra_Stage_{k}", (wx + 0.021, 1.40 + k * 0.28, 1.50 + (k % 2) * 0.10), (0.002, 0.20, 0.03), (0.22, 0.26, 0.40, 1.0))
    for k in range(4):
        make_box(f"Frame_Contra_Kana_{k}", (wx + 0.021, 2.66, 1.74 - k * 0.07), (0.002, 0.05, 0.04), (0.22, 0.26, 0.40, 1.0))
    for k, (y, z) in enumerate(((3.65, 1.75), (3.10, 1.70), (3.20, 1.25))):
        make_box(f"Frame_Small_{k}", (wx, y, z), (0.03, 0.36, 0.44), (0.20, 0.16, 0.12, 1.0))
        make_box(f"Frame_Small_{k}_Pic", (wx + 0.017, y, z), (0.004, 0.30, 0.38),
                 ((0.70, 0.50, 0.60, 1.0), (0.40, 0.50, 0.40, 1.0), (0.60, 0.60, 0.70, 1.0))[k])
    # the photo of Jessie and Janessa propped on the desk
    make_box("Sp_Desk_Top", (SX1 - 0.10 - 0.30, 0.90, 0.74), (0.58, 1.10, 0.03), (0.50, 0.40, 0.30, 1.0))
    for s in (-1, 1):
        make_box(f"Sp_Desk_Leg_{s:+d}", (SX1 - 0.10 - 0.30, 0.90 + s * 0.52, 0.365), (0.54, 0.03, 0.73), (0.44, 0.34, 0.26, 1.0))
    make_rot_box("Sp_Photo", (SX1 - 0.10 - 0.30, 1.20, 0.835), (0.10, 0.015, 0.15), (0.90, 0.56, 0.70, 1.0), pitch=0.0, roll=-0.15)


# ── the tunnels, 2003 and 1945, and the bare room ─────────────────────
TX0, TX1, TL, TH = 100.0, 103.2, 60.0, 2.8
BR_Y0, BR_Y1, BR_X1 = 6.0, 9.2, 106.4         # the bare room off the E side
BR_DOOR_Y = 7.6
RB_Y0, RB_Y1 = 16.0, 26.0                     # the racquetball room off the W side


def build_tunnels():
    cx = (TX0 + TX1) / 2.0
    make_floor("Tun_Floor", (cx, TL / 2.0, 0.0), size_x=TX1 - TX0 + 0.4, size_y=TL, palette={"vinyl": CEMENT, "seam": (0.50, 0.49, 0.46, 1.0)})
    make_box("Tun_Ceil", (cx, TL / 2.0, TH + 0.04), (TX1 - TX0 + 0.4, TL, 0.08), (0.54, 0.54, 0.52, 1.0))
    pal = {"wall": (0.70, 0.70, 0.66, 1.0), "baseboard": (0.44, 0.44, 0.42, 1.0)}
    make_wall_with_openings("Tun_Wall_W", (TX0, TL / 2.0, 0), length=TL, height=TH, thickness=0.2, axis='Y', palette=pal,
                            baseboard_face_sign=+1, openings=[(21.0, 1.1, 1.8, 2.2), (34.0, 1.5, 3.0, 1.2)])
    make_wall_with_openings("Tun_Wall_E", (TX1, TL / 2.0, 0), length=TL, height=TH, thickness=0.2, axis='Y', palette=pal,
                            baseboard_face_sign=-1, openings=[(BR_DOOR_Y, 1.0, 0.86, 2.0)])
    make_box("Tun_End_N", (cx, TL + 0.1, TH / 2.0), (TX1 - TX0 + 0.4, 0.2, TH), (0.30, 0.30, 0.30, 1.0))
    make_box("Tun_End_S", (cx, -0.1, TH / 2.0), (TX1 - TX0 + 0.4, 0.2, TH), (0.30, 0.30, 0.30, 1.0))
    # the steam pipes along the ceiling (both years) and the tubes
    for k, (x, r) in enumerate(((TX0 + 0.40, 0.08), (TX0 + 0.66, 0.05), (TX1 - 0.40, 0.07))):
        make_cyl(f"Tun_Pipe_{k}", (x, TL / 2.0, TH - 0.22 - k * 0.04), r, TL, (0.46, 0.44, 0.40, 1.0), axis='Y', segments=10)
    for k in range(10):
        make_fluorescent_tube_fixture(f"Fluor_Tun_{k}", (cx, 3.0 + k * 6.0, TH), length=1.20, width=0.30)
    # doors on the E side (one is the bare room's; the others radiation doors in 2003)
    for k, y in enumerate((14.0, 27.0, 41.0)):
        make_box(f"Tun_Door_E_{k}", (TX1 - 0.12, y, 1.0), (0.04, 0.90, 2.0), (0.46, 0.50, 0.52, 1.0))
        make_box(f"Rad_Sign_{k}" + TUN2003, (TX1 - 0.145, y, 1.55), (0.006, 0.30, 0.30), (0.96, 0.84, 0.20, 1.0))
        make_box(f"Rad_Sign_{k}_Trefoil" + TUN2003, (TX1 - 0.149, y, 1.55), (0.004, 0.14, 0.14), (0.12, 0.10, 0.12, 1.0))
    # the clean room behind reinforced glass (W side, y 32.5..35.5)
    make_box("Clean_Glass", (TX0, 34.0, 1.5), (0.04, 3.0, 1.2), (0.70, 0.80, 0.84, 1.0))
    for s in (-1, 1):
        make_box(f"Clean_Room_Side_{s:+d}", (TX0 - 1.5, 34.0 + s * 2.0, 1.4), (3.0, 0.2, 2.8), (0.92, 0.94, 0.94, 1.0))
    make_box("Clean_Room_Ceil", (TX0 - 1.5, 34.0, 2.84), (3.0, 4.0, 0.08), (0.94, 0.94, 0.94, 1.0))
    make_box("Clean_Room_Back", (TX0 - 3.0, 34.0, 1.4), (0.2, 4.0, 2.8), (0.92, 0.94, 0.94, 1.0))
    make_box("Clean_Room_Floor", (TX0 - 1.5, 34.0, 0.0), (3.0, 4.0, 0.02), (0.92, 0.92, 0.92, 1.0))
    make_box("Clean_Room_Bench", (TX0 - 2.4, 34.0, 0.45), (0.8, 2.6, 0.90), (0.84, 0.86, 0.88, 1.0))
    # the racquetball room through its doorway (W side): white court, red and
    # blue lanterns hung across (2003)
    rx0, rx1 = TX0 - 9.8, TX0
    rcx, rcy = (rx0 + rx1) / 2.0, (RB_Y0 + RB_Y1) / 2.0
    make_box("Racquet_Floor", (rcx, rcy, 0.0), (rx1 - rx0, RB_Y1 - RB_Y0, 0.02), (0.82, 0.70, 0.52, 1.0))
    make_box("Racquet_Wall_W", (rx0, rcy, 3.0), (0.2, RB_Y1 - RB_Y0, 6.0), (0.92, 0.92, 0.90, 1.0))
    make_box("Racquet_Wall_N", (rcx, RB_Y1, 3.0), (rx1 - rx0, 0.2, 6.0), (0.92, 0.92, 0.90, 1.0))
    make_box("Racquet_Wall_S", (rcx, RB_Y0, 3.0), (rx1 - rx0, 0.2, 6.0), (0.92, 0.92, 0.90, 1.0))
    make_box("Racquet_Ceil", (rcx, rcy, 6.05), (rx1 - rx0, RB_Y1 - RB_Y0, 0.1), (0.40, 0.40, 0.40, 1.0))
    make_box("Racquet_Line", (rcx, rcy, 0.012), (0.08, RB_Y1 - RB_Y0, 0.004), (0.80, 0.20, 0.18, 1.0))
    for k in range(10):
        x = rx0 + 1.0 + (k % 5) * 1.9
        y = RB_Y0 + 2.5 + (k // 5) * 4.5
        col = (0.92, 0.22, 0.20, 1.0) if k % 2 == 0 else (0.24, 0.36, 0.92, 1.0)
        make_cyl(f"Lantern_Hang_{k}_Cord" + TUN2003, (x, y, 5.45), 0.005, 1.10, (0.10, 0.10, 0.10, 1.0), segments=4)
        make_blob(f"Lantern_Hang_{k}" + TUN2003, (x, y, 4.75), 0.26, col, noise=0.0, seed=k, squash=0.9)
    # the rail to grind: a pipe handrail on posts along the E wall
    make_cyl("Grind_Rail", (TX1 - 0.40, 20.5, 0.62), 0.03, 11.0, (0.62, 0.62, 0.60, 1.0), axis='Y', segments=8)
    for k in range(6):
        make_cyl(f"Grind_Rail_Post_{k}", (TX1 - 0.40, 15.5 + k * 2.0, 0.30), 0.025, 0.60, (0.50, 0.50, 0.48, 1.0), segments=6)
    # the checkpoint (2003): a booth and a gate arm
    make_box("Checkpoint_Booth" + TUN2003, (TX0 + 0.50, 46.0, 0.60), (0.80, 1.20, 1.20), (0.40, 0.42, 0.46, 1.0))
    make_box("Checkpoint_Window" + TUN2003, (TX0 + 0.91, 46.0, 1.00), (0.01, 0.80, 0.30), (0.50, 0.62, 0.70, 1.0))
    make_box("Checkpoint_Arm" + TUN2003, (TX0 + 1.70, 46.4, 1.00), (1.60, 0.06, 0.06), (0.90, 0.80, 0.20, 1.0))
    # graffiti on everything (2003): tags, throw-ups and years of layers
    gcols = [(0.86, 0.26, 0.40), (0.24, 0.62, 0.86), (0.96, 0.82, 0.24), (0.36, 0.80, 0.40), (0.62, 0.36, 0.86), (0.12, 0.12, 0.14),
             (0.94, 0.94, 0.92), (0.94, 0.52, 0.20)]
    k = 0
    for side, x in (("W", TX0 + 0.105), ("E", TX1 - 0.105)):
        y = 1.0
        while y < TL - 1.0:
            # leave the doors, the glass and the doorway readable
            if side == "E" and (abs(y - BR_DOOR_Y) < 0.8 or any(abs(y - d) < 0.7 for d in (14.0, 27.0, 41.0))):
                y += 0.9
                continue
            if side == "W" and (19.9 < y < 22.1 or 32.3 < y < 35.7):
                y += 0.9
                continue
            w = 0.6 + (k * 7 % 5) * 0.25
            h = 0.3 + (k * 3 % 4) * 0.18
            z = 0.6 + (k * 5 % 6) * 0.22
            dx = 0.002 * (k % 3)
            off = -dx if side == "E" else dx
            make_box(f"Graffiti_{k}" + TUN2003, (x + off, y, z), (0.004, w, h), (*gcols[k % len(gcols)], 1.0))
            y += w * 0.7 + 0.15
            k += 1


def build_bare_room():
    """1945: "Not very big at all." Cement, bare walls, one door, one bulb."""
    x0, x1, y0, y1, h = TX1, BR_X1, BR_Y0, BR_Y1, 2.6
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    make_box("Bare_Floor", (cx, cy, 0.0), (x1 - x0, y1 - y0, 0.02), CEMENT)
    make_box("Bare_Ceil", (cx, cy, h + 0.04), (x1 - x0, y1 - y0, 0.08), (0.64, 0.64, 0.62, 1.0))
    pal = {"wall": (0.68, 0.67, 0.64, 1.0), "baseboard": (0.60, 0.59, 0.56, 1.0)}
    make_wall("Bare_Wall_E", (x1, cy, 0), length=y1 - y0 + 0.4, height=h, thickness=0.2, axis='Y', palette=pal, baseboard_face_sign=-1)
    make_wall("Bare_Wall_N", (cx, y1, 0), length=x1 - x0, height=h, thickness=0.2, axis='X', palette=pal, baseboard_face_sign=-1)
    make_wall("Bare_Wall_S", (cx, y0, 0), length=x1 - x0, height=h, thickness=0.2, axis='X', palette=pal, baseboard_face_sign=+1)
    # the one door: propped open (lit), shut with the light under it (dark)
    make_box("Bare_Door_Open__caltech_bare_room__caltech_tunnels__caltech_hallway_1945", (TX1 + 0.10 + 0.42, BR_DOOR_Y - 0.41, 1.0),
             (0.84, 0.04, 2.0), (0.44, 0.40, 0.34, 1.0))
    make_box("Bare_Door_Shut__caltech_bare_room_dark", (TX1, BR_DOOR_Y, 1.0), (0.05, 0.84, 2.0), (0.44, 0.40, 0.34, 1.0))
    make_box("Bare_Bulb_Cord", (cx, cy, h - 0.15), (0.01, 0.01, 0.30), (0.12, 0.12, 0.12, 1.0))
    make_blob("Bare_Bulb", (cx, cy, h - 0.34), 0.05, (0.98, 0.94, 0.80, 1.0), noise=0.0, seed=1)


def main():
    clear_scene()
    build_courtyard()
    build_side_yard()
    build_game_room()
    build_spencer_room()
    build_tunnels()
    build_bare_room()
    try:
        join_stock()
        join_named("Graffiti_", "Graffiti" + TUN2003)
    except Exception as _e:
        print("[join] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/caltech_dabney.glb"))
    print(f"\n[build_caltech_dabney] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
