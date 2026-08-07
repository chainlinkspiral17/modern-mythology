"""The crumpled barn — vol2 ch1's history montage. A gray barn that
lost its back half years ago: the gable end still stands, the roof
lies where it fell.

Hero features: the standing weathered gable wall with its dark
doorway and hay-door, the collapsed roof planes lying low behind it
on a rubble bed, exposed frame posts still upright inside the
footprint, scattered siding boards, a remnant fence line, a rusted
water trough, tall weeds working through everything, and a flat
overcast sky.

Coordinate frame: Blender Z-up. y=0 is the field's south edge (the
camera side); +Y runs north to the gable face at y≈8. glTF export
remaps to Godot (x, z, -y).

Vantages wired in Background3D.CAMERA_PRESETS:
  crumpled_barn_ext — in the field looking N at the standing gable
  with the fallen roof behind.
  crumpled_barn_int — inside the standing half: the marionette
  cabinet (Jiggles the Juggler, head resting on his shoulder,
  glass fourth wall broken) facing the carved wooden sign of the
  mermaid — "Come Visit Today. A Twisted Beauty and a Beast. Only
  at The Cliffside Circus Attraction." The hero props of the whole
  Delores thread.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

COL_FIELD = (0.42, 0.42, 0.28, 1.0)      # dry pasture
COL_DIRT = (0.40, 0.34, 0.26, 1.0)
COL_BARN = (0.42, 0.40, 0.38, 1.0)       # weathered gray board
COL_BARN_DK = (0.32, 0.30, 0.29, 1.0)
COL_DOOR = (0.14, 0.13, 0.12, 1.0)
COL_ROOF = (0.36, 0.33, 0.30, 1.0)       # fallen shingle planes
COL_ROOF_DK = (0.28, 0.26, 0.24, 1.0)
COL_FRAME = (0.30, 0.25, 0.19, 1.0)      # old fir posts
COL_RUBBLE = (0.38, 0.35, 0.31, 1.0)
COL_WEED = (0.34, 0.38, 0.22, 1.0)
COL_WEED_DRY = (0.48, 0.44, 0.28, 1.0)
COL_FENCE = (0.34, 0.28, 0.20, 1.0)
COL_TROUGH = (0.36, 0.30, 0.26, 1.0)     # rust
COL_TREE = (0.20, 0.26, 0.18, 1.0)
COL_SKY = (0.62, 0.63, 0.64, 1.0)        # flat overcast


def build_field():
    make_box("Field", (0.0, 7.0, 0.0), (34.0, 20.0, 0.05), COL_FIELD)
    make_box("Yard_Dirt", (0.0, 8.5, 0.01), (10.0, 6.0, 0.05), COL_DIRT)


def build_gable():
    """The standing end wall, face at y=8: wide base narrowing in
    three steps to the peak, doorway and hay door punched dark."""
    make_box("Gable_Base", (-0.5, 8.4, 1.6), (6.4, 0.35, 3.2), COL_BARN)
    make_box("Gable_Mid", (-0.5, 8.4, 3.85), (4.6, 0.33, 1.3), COL_BARN)
    make_box("Gable_Peak", (-0.5, 8.4, 4.95), (2.4, 0.30, 0.9), COL_BARN_DK)
    # Board seams: darker vertical strips
    for i in range(7):
        make_box(f"Gable_Seam_{i}", (-3.2 + i * 0.95, 8.22, 1.6), (0.06, 0.02, 3.15),
                 COL_BARN_DK)
    # The doorway (door long gone) + hay door above
    make_box("Doorway", (-1.2, 8.30, 1.25), (1.7, 0.45, 2.5), COL_DOOR)
    make_box("Hay_Door", (-0.5, 8.28, 4.05), (1.0, 0.40, 1.0), COL_DOOR)
    # One leaning siding board by the doorway
    make_box("Lean_Board", (0.4, 8.05, 1.15), (0.28, 0.10, 2.3), COL_BARN_DK)


def build_collapse():
    """The fallen roof: two big shingle planes lying low on rubble at
    slightly different heights, plus surviving frame posts."""
    # The planes slid off the BACK half as they fell — the front bay
    # behind the gable survives as a sheltered pocket (the interior
    # vantage stands there)
    make_box("Roof_Plane_W", (-2.6, 12.4, 0.75), (4.4, 4.2, 0.30), COL_ROOF)
    make_box("Roof_Plane_E", (1.9, 12.8, 1.15), (4.0, 3.8, 0.30), COL_ROOF_DK)
    make_box("Roof_Ridge_Piece", (-0.3, 13.6, 1.55), (3.2, 0.7, 0.35), COL_ROOF_DK)
    # Rubble bed under and around the planes
    rubble = [(-3.8, 9.6, 0.5), (-1.0, 10.2, 0.7), (2.8, 9.8, 0.45), (0.6, 12.8, 0.55),
              (-4.4, 11.8, 0.4), (4.0, 11.6, 0.6), (2.0, 13.4, 0.35)]
    for i, (rx, ry, rh) in enumerate(rubble):
        make_box(f"Rubble_{i}", (rx, ry, rh / 2.0), (1.3 + 0.3 * (i % 3), 1.0, rh),
                 COL_RUBBLE)
    # Frame posts still standing inside the footprint, varied heights
    posts = [(-2.8, 10.4, 3.4), (1.6, 10.8, 2.6), (-0.4, 12.2, 3.0), (3.0, 12.6, 1.8)]
    for i, (px, py, ph) in enumerate(posts):
        make_box(f"Post_{i}", (px, py, ph / 2.0), (0.24, 0.24, ph), COL_FRAME)
    make_box("Beam_Fallen", (-1.0, 11.2, 0.35), (0.22, 3.8, 0.22), COL_FRAME)
    # Scattered siding boards in the yard
    boards = [(-3.5, 6.8, 0.0), (-1.2, 6.2, 0.4), (1.8, 6.9, -0.2), (3.2, 7.6, 0.3)]
    for i, (bx, by, rot_hint) in enumerate(boards):
        make_box(f"Board_{i}", (bx, by, 0.06), (1.9 + 0.4 * (i % 2), 0.26, 0.06),
                 COL_BARN_DK)


def build_yard():
    # Remnant fence line, posts missing rails in places
    for i in range(7):
        fx = -9.0 + i * 3.0
        if i == 3:
            continue  # the gap where the gate was
        make_box(f"Fence_Post_{i}", (fx, 3.4, 0.5), (0.14, 0.14, 1.0), COL_FENCE)
    make_cyl("Fence_Rail_W", (-6.0, 3.4, 0.78), 0.05, 5.8, COL_FENCE, segments=6, axis='X')
    make_cyl("Fence_Rail_E", (6.0, 3.4, 0.72), 0.05, 5.6, COL_FENCE, segments=6, axis='X')
    # Rusted water trough
    make_box("Trough", (4.6, 5.4, 0.30), (1.6, 0.7, 0.60), COL_TROUGH,
             open_faces={"+Z"})
    # Weeds: clumps through the yard, taller at the walls
    clumps = [(-4.8, 5.0), (-2.0, 4.4), (0.8, 5.6), (3.6, 4.2), (-3.4, 7.6),
              (1.6, 7.9), (-5.6, 9.0), (5.0, 8.8), (0.0, 3.2), (-7.5, 6.0)]
    for ci, (cx, cy) in enumerate(clumps):
        for b in range(4):
            bx = cx + 0.14 * ((b * 5 + ci * 3) % 5 - 2)
            h = 0.4 + 0.16 * ((b + ci) % 3) + (0.3 if cy > 7.0 else 0.0)
            col = COL_WEED if (b + ci) % 2 == 0 else COL_WEED_DRY
            make_box(f"Weed_{ci}_{b}", (bx, cy + 0.08 * (b % 2), h / 2.0),
                     (0.05, 0.05, h), col)


def build_interior():
    """Inside the standing half, y ∈ [8.6, 13]: the cabinet with the
    broken marionette, and the carved sign half-hanging opposite."""
    # A patch of old plank floor under the props (the surviving bay)
    make_box("Int_Floor", (-0.6, 9.6, 0.03), (5.0, 1.8, 0.06), (0.34, 0.28, 0.22, 1.0))
    # The cabinet — against the gable's inner face beside the sign,
    # glass fourth wall facing north into the bay
    cbx, cby = -1.8, 8.95
    make_box("Cab_Body", (cbx, cby, 0.95), (0.7, 0.9, 1.9), (0.30, 0.22, 0.16, 1.0))
    make_box("Cab_Stage", (cbx + 0.1, cby, 0.75), (0.45, 0.7, 0.06), (0.44, 0.34, 0.22, 1.0))
    # Glass fourth wall (north face), broken: partial pane + shard
    make_box("Cab_Glass", (cbx - 0.12, cby + 0.44, 1.30), (0.55, 0.02, 0.75),
             (0.55, 0.62, 0.66, 0.35))
    make_box("Cab_Glass_Shard", (cbx + 0.24, cby + 0.42, 0.82), (0.20, 0.02, 0.16),
             (0.55, 0.62, 0.66, 0.5))
    # Jiggles the Juggler — sagging at the hip, head against shoulder
    make_box("Jiggles_Torso", (cbx + 0.08, cby, 1.10), (0.14, 0.18, 0.30),
             (0.56, 0.44, 0.30, 1.0))
    make_box("Jiggles_Hip_Sag", (cbx + 0.06, cby + 0.06, 0.90), (0.13, 0.16, 0.14),
             (0.48, 0.36, 0.26, 1.0))
    make_cyl("Jiggles_Head", (cbx + 0.14, cby - 0.09, 1.30), 0.07, 0.12,
             (0.78, 0.68, 0.55, 1.0), segments=8)
    make_box("Jiggles_Arm_L", (cbx + 0.04, cby - 0.16, 1.02), (0.05, 0.05, 0.26),
             (0.56, 0.44, 0.30, 1.0))
    make_box("Jiggles_Arm_R", (cbx + 0.04, cby + 0.17, 1.12), (0.05, 0.05, 0.22),
             (0.56, 0.44, 0.30, 1.0))
    # His name in red paint on the cabinet base (north face)
    make_box("Jiggles_Name", (cbx, cby + 0.46, 0.62), (0.5, 0.02, 0.08),
             (0.58, 0.16, 0.12, 1.0))
    # Marionette strings up into the case head
    for i, sy in enumerate((cby - 0.1, cby, cby + 0.1)):
        make_box(f"Jiggles_String_{i}", (cbx + 0.08, sy, 1.60), (0.008, 0.008, 0.45),
                 (0.62, 0.60, 0.55, 1.0))
    # The carved wooden sign, half-hanging on the gable's inner face:
    # one corner up, one dropped (two offset panels read as a tilt)
    make_box("Sign_Panel_Hi", (1.2, 8.62, 1.75), (0.9, 0.06, 0.65), (0.46, 0.34, 0.20, 1.0))
    make_box("Sign_Panel_Lo", (0.55, 8.60, 1.45), (0.75, 0.06, 0.60), (0.42, 0.30, 0.18, 1.0))
    # The mermaid relief: rock, seated figure, the fall of dark hair
    make_box("Sign_Rock", (0.85, 8.55, 1.35), (0.34, 0.04, 0.22), (0.36, 0.30, 0.24, 1.0))
    make_box("Sign_Figure", (0.88, 8.52, 1.62), (0.16, 0.04, 0.36), (0.62, 0.50, 0.38, 1.0))
    make_box("Sign_Hair", (0.94, 8.50, 1.58), (0.10, 0.03, 0.42), (0.22, 0.16, 0.12, 1.0))
    # The old-script line below, a lighter incised band
    make_box("Sign_Script", (0.85, 8.53, 1.16), (0.80, 0.03, 0.10), (0.58, 0.48, 0.34, 1.0))
    # A shaft of daylight through the broken roof: pale dust plane
    make_box("Light_Shaft", (-0.6, 9.8, 1.6), (1.1, 0.9, 3.0), (0.72, 0.70, 0.62, 0.18))


def build_backdrop():
    # 2026-08-04 · this was a hedgerow and then a 104m-wide "Sky"
    # slab standing 11m past it with NOTHING behind it — the
    # louisiana_road failure exactly: the field stopped at a painted
    # wall. The horizon is the environment's job (fog + sky in the
    # .tscn). Geometry's job is to keep receding until fog eats it.
    for i in range(6):
        tx = -14.0 + i * 5.5
        make_box(f"Hedge_{i}", (tx, 17.0, 1.6), (4.8, 1.6, 3.2), COL_TREE)
    # Receding hedgerows and windbreaks out across the section, each
    # band dimmer and lower so aerial perspective has steps to grade.
    for i, (by, bw, bh, shade) in enumerate([
            (60.0, 60.0, 5.0, 0.88), (130.0, 110.0, 6.0, 0.74),
            (260.0, 190.0, 7.5, 0.60), (460.0, 300.0, 9.0, 0.48),
            (760.0, 440.0, 11.0, 0.38)]):
        c = (COL_TREE[0] * shade, COL_TREE[1] * shade,
             COL_TREE[2] * shade, 1.0)
        make_box(f"FarWindbreak_{i}", (0.0, by, bh * 0.5),
                 (bw, 5.0, bh), c)
        # a farm building or two out on the section line
        if i in (1, 3):
            make_box(f"FarBarn_{i}", (bw * 0.35, by - 8.0, 3.0),
                     (7.0, 5.0, 6.0), c)


def main():
    clear_scene()
    build_field()
    build_gable()
    build_collapse()
    build_interior()
    build_yard()
    build_backdrop()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/crumpled_barn.glb"))
    print(f"\n[build_crumpled_barn] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
