"""nate_garage — Nate's parents' two-car garage, the rear half converted
into the band's practice room (vol6 ch14 Substation Nine, pass 64,
2026-10-11).

"Nate's garage is bigger than Jesse's. Nate's parents had, in 2018,
converted the rear half of their two-car garage into a small finished
room with sound dampening on the walls and a separate window AC that
does not, technically, count as part of the house's HVAC envelope. The
conversion had been Nate's father's project." Walt — commercial
insurance, bass in a wedding band three times a year — "had decided
that his son was going to have, in their house, the room he himself had
not had at fifteen." The Wednesday practice at seven: Carl at the kit,
Nate plugged in, Em at the mic running the practice; the set order
written on the back of the flyer in Nate's handwriting; practice ends at
nine forty-six, Carl carries his snare to his mother's car at the curb,
Em and Jesse in the driveway.

DRAFT 1: the FRONT BAY (y 0..3.8) with the roll-up door UP (the August
rule), Walt's road cases, the shelving, the mower and the bikes; the
PARTITION with its door standing open; the FINISHED ROOM (y 3.8..7.6)
carpeted, foam panels in rows on three walls, the window AC in the east
window, two flush ceiling fixtures, the loveseat, the mini fridge, Walt's
wedding-band poster, the box fan by the door (Carl's song), the band gear
borrowed from Jesse's garage builder and moved into the room (the kit
faces the partition door, the mic at the room's front); OUTSIDE the
two-car driveway with Jesse's Civic, the street with Carl's mother's car
at the curb, the house attached on the east with the side door Jesse
comes in by and the kitchen window lit (Walt making a sandwich), a porch
light, the lawn, a live oak, the neighbours across the street.
Draft 2 targets: Em's soft mic case on the loveseat; the flyer taped to
Amp_0 with the set order; a music stand; Walt's own bass in a gig bag in
the corner; the house's front porch; a mailbox at the curb; the
street's far houses as more than slabs; the kitchen seen through its
window (Walt at the counter).

Coordinate frame: Blender Z-up. y=0 is the open door plane (south, to
the driveway); +Y into the garage; x=±3.6. glTF export remaps to Godot
(x, z, -y).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
_LOC = os.path.dirname(os.path.abspath(__file__))
if _LOC not in sys.path: sys.path.insert(0, _LOC)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_chamfer_box, make_lathe, make_blob, make_taper_cyl, make_rot_box, export_glb
from _props.structure import make_floor, make_wall, make_wall_with_openings, make_ceiling, make_frame_ring
from _props.vehicles import make_car
import build_henderson_garage as HG

ROOM_W = 7.2      # x in [-3.6, 3.6]
ROOM_D = 7.6      # y in [0, 7.6]: the bay 0..3.8, the finished room 3.8..7.6
PART_Y = 3.8
CEIL = 2.7
COL_WALL = (0.62, 0.60, 0.55, 1.0)
COL_BASE = (0.40, 0.38, 0.34, 1.0)
COL_ROOM_WALL = (0.56, 0.54, 0.50, 1.0)   # the finished room, painted a warm grey
COL_FLOOR = (0.44, 0.44, 0.46, 1.0)
COL_SEAM = (0.36, 0.36, 0.38, 1.0)
COL_CARPET = (0.30, 0.28, 0.30, 1.0)
COL_FOAM = (0.16, 0.16, 0.17, 1.0)
COL_DOOR = (0.82, 0.81, 0.78, 1.0)
COL_TRACK = (0.30, 0.31, 0.34, 1.0)
COL_STEEL = (0.34, 0.35, 0.38, 1.0)
COL_STEEL_DK = (0.18, 0.18, 0.20, 1.0)
COL_WOOD = (0.46, 0.34, 0.22, 1.0)
COL_DRIVE = (0.50, 0.49, 0.50, 1.0)
COL_ASPHALT = (0.26, 0.26, 0.28, 1.0)
COL_LAWN = (0.22, 0.30, 0.16, 1.0)
COL_HOUSE = (0.70, 0.64, 0.56, 1.0)       # the house's brick-tan
COL_TRIM = (0.86, 0.85, 0.80, 1.0)
COL_ROOF = (0.32, 0.30, 0.30, 1.0)
COL_GLOW = (1.00, 0.88, 0.62, 1.0)
COL_GLASS_WARM = (1.00, 0.84, 0.56, 1.0)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y', palette=pal, baseboard_face_sign=+1)
    # the E wall carries the finished room's window (the window AC sits in it)
    make_wall_with_openings("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y', palette=pal,
                            baseboard_face_sign=-1, openings=[(5.80, 1.45, 0.90, 0.80)])
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL, axis='X', palette=pal, baseboard_face_sign=-1)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4, with_grid=False, with_stains=False)
    # the partition: a stud wall with the door at x -1.0, the leaf standing open into the bay
    make_wall_with_openings("Partition", (0.0, PART_Y, 0), length=ROOM_W, height=CEIL, axis='X', palette={"wall": COL_ROOM_WALL, "baseboard": COL_BASE},
                            baseboard_face_sign=+1, openings=[(-1.0, 1.025, 0.90, 2.05)])
    make_box("Partition_Door_Frame_Head", (-1.0, PART_Y, 2.08), (1.02, 0.24, 0.06), COL_TRIM)
    for e in (-1, 1):
        make_box(f"Partition_Door_Jamb_{'W' if e < 0 else 'E'}", (-1.0 + e * 0.48, PART_Y, 1.025), (0.06, 0.24, 2.05), COL_TRIM)
    make_rot_box("Partition_Door", (-1.0 - 0.45 + 0.30, PART_Y - 0.10 - 0.36, 1.02), (0.86, 0.04, 2.02), COL_DOOR, yaw=-1.10)
    # the roll-up door UP: the rolled sections under the ceiling, the tracks, the opener
    make_box("Door_Header", (0.0, 0.0, CEIL - 0.15), (ROOM_W + 0.4, 0.22, 0.30), COL_WALL)
    for sgn in (-1, 1):
        make_box(f"Door_Jamb_{sgn:+d}", (sgn * (ROOM_W / 2.0 - 0.10), 0.0, CEIL / 2.0), (0.20, 0.22, CEIL), COL_WALL)
    for k in range(4):
        make_box(f"Door_Panel_{k}", (0.0, 0.55 + k * 0.42, CEIL - 0.10), (ROOM_W - 0.7, 0.40, 0.05), COL_DOOR)
    for sgn in (-1, 1):
        make_box(f"Door_Track_{sgn:+d}", (sgn * (ROOM_W / 2.0 - 0.32), 1.2, CEIL - 0.16), (0.05, 2.4, 0.05), COL_TRACK)
        make_box(f"Door_Track_V_{sgn:+d}", (sgn * (ROOM_W / 2.0 - 0.32), 0.10, CEIL - 0.75), (0.05, 0.05, 1.3), COL_TRACK)
    make_box("Opener_Rail", (0.0, 1.9, CEIL - 0.20), (0.06, 3.0, 0.06), COL_TRACK)
    make_box("Opener_Motor", (0.0, 3.3, CEIL - 0.28), (0.34, 0.44, 0.22), COL_STEEL_DK)
    make_box("Opener_Hanger", (0.0, 3.3, CEIL - 0.085), (0.04, 0.30, 0.17), COL_STEEL_DK)
    # the bay's one fluorescent tube
    make_box("Bay_Tube", (0.0, 2.0, CEIL - 0.06), (1.20, 0.10, 0.08), (0.92, 0.92, 0.85, 1.0))


def build_finished_room():
    """Walt's project: carpet, foam on three walls, the window AC, two
    flush fixtures, the loveseat, the fridge, the poster, the box fan."""
    y0, y1 = PART_Y + 0.10, ROOM_D - 0.10
    make_box("Carpet", (0.0, (y0 + y1) / 2.0, 0.012), (ROOM_W - 0.2, y1 - y0, 0.024), COL_CARPET)
    # foam panels: three rows on the N wall, two on each side wall, in a checker
    for r, z in enumerate((0.75, 1.45, 2.15)):
        for c, x in enumerate([-3.0 + 0.75 * i for i in range(9)]):
            if (r + c) % 2:
                continue
            make_chamfer_box(f"Foam_N_{r}_{c}", (x, ROOM_D - 0.10 - 0.03, z), (0.60, 0.05, 0.60), COL_FOAM, chamfer=0.02)
    for r, z in enumerate((0.95, 1.85)):
        for c, y in enumerate([y0 + 0.45 + 0.75 * i for i in range(5)]):
            if (r + c) % 2:
                continue
            make_chamfer_box(f"Foam_W_{r}_{c}", (-ROOM_W / 2.0 + 0.10 + 0.03, y, z), (0.05, 0.60, 0.60), COL_FOAM, chamfer=0.02)
            if abs(y - 5.80) > 0.75:   # the E wall's window and its AC
                make_chamfer_box(f"Foam_E_{r}_{c}", (ROOM_W / 2.0 - 0.10 - 0.03, y, z), (0.05, 0.60, 0.60), COL_FOAM, chamfer=0.02)
    # the window AC in the E window (opening y 5.35..6.25, z 1.05..1.85)
    make_frame_ring("East_Window_Frame", (ROOM_W / 2.0 - 0.12, 5.80, 1.45), (0.04, 1.00, 0.90), COL_TRIM)
    make_box("East_Window_Glass_Top", (ROOM_W / 2.0 - 0.14, 5.80, 1.68), (0.02, 0.86, 0.30), (0.42, 0.52, 0.55, 0.6))
    make_box("Window_AC", (ROOM_W / 2.0 - 0.05, 5.80, 1.28), (0.70, 0.60, 0.42), (0.80, 0.80, 0.78, 1.0))
    for gi in range(5):
        make_box(f"Window_AC_Vane_{gi}", (ROOM_W / 2.0 - 0.41, 5.80, 1.14 + gi * 0.06), (0.012, 0.52, 0.02), (0.62, 0.62, 0.60, 1.0))
    make_box("Window_AC_Panel", (ROOM_W / 2.0 - 0.41, 5.80, 1.42), (0.012, 0.52, 0.10), (0.30, 0.30, 0.32, 1.0))
    # two flush ceiling fixtures (their practicals in the .tscn)
    for i, x in enumerate((-1.3, 1.3)):
        make_cyl(f"Room_Light_{i}", (x, 5.7, CEIL - 0.05), 0.18, 0.10, (0.94, 0.94, 0.90, 1.0), segments=14)
    # the loveseat on the W wall, Em's end
    make_chamfer_box("Loveseat_Base", (-2.95, 6.2, 0.22), (0.80, 1.40, 0.44), (0.36, 0.30, 0.34, 1.0), chamfer=0.03)
    make_chamfer_box("Loveseat_Back", (-3.25, 6.2, 0.62), (0.20, 1.40, 0.44), (0.36, 0.30, 0.34, 1.0), chamfer=0.03)
    for e in (-1, 1):
        make_chamfer_box(f"Loveseat_Arm_{'S' if e < 0 else 'N'}", (-2.95, 6.2 + e * 0.64, 0.56), (0.80, 0.12, 0.24), (0.36, 0.30, 0.34, 1.0), chamfer=0.03)
    for e in (-1, 1):
        make_chamfer_box(f"Loveseat_Cushion_{'S' if e < 0 else 'N'}", (-2.85, 6.2 + e * 0.32, 0.50), (0.60, 0.60, 0.12), (0.42, 0.36, 0.40, 1.0), chamfer=0.03)
    # the mini fridge in the NE corner, a case of water on it
    make_box("Mini_Fridge", (3.24, 7.1, 0.42), (0.50, 0.50, 0.84), (0.80, 0.80, 0.78, 1.0))
    make_box("Mini_Fridge_Handle", (2.98, 7.26, 0.55), (0.02, 0.03, 0.30), COL_STEEL)
    make_box("Water_Case", (3.24, 7.1, 0.95), (0.40, 0.28, 0.22), (0.30, 0.46, 0.70, 0.7))
    # Walt's wedding-band poster, framed, on the N wall between the foam
    make_box("Wedding_Band_Poster_Frame", (2.25, ROOM_D - 0.10 - 0.015, 1.80), (0.46, 0.03, 0.62), (0.20, 0.18, 0.16, 1.0))
    make_box("Wedding_Band_Poster", (2.25, ROOM_D - 0.10 - 0.032, 1.80), (0.40, 0.004, 0.56), (0.86, 0.82, 0.70, 1.0))
    make_box("Wedding_Band_Poster_Band", (2.25, ROOM_D - 0.10 - 0.036, 1.70), (0.30, 0.004, 0.22), (0.24, 0.26, 0.40, 1.0))
    # the box fan by the door (Carl's song: "just about a box fan, that's it")
    make_box("Box_Fan", (-0.25, 4.25, 0.26), (0.52, 0.12, 0.52), (0.84, 0.84, 0.82, 1.0))
    make_cyl("Box_Fan_Grille", (-0.25, 4.185, 0.26), 0.22, 0.01, (0.30, 0.30, 0.32, 1.0), segments=16, axis='Y')
    make_box("Box_Fan_Foot_W", (-0.45, 4.25, 0.015), (0.06, 0.22, 0.03), (0.60, 0.60, 0.58, 1.0))
    make_box("Box_Fan_Foot_E", (-0.05, 4.25, 0.015), (0.06, 0.22, 0.03), (0.60, 0.60, 0.58, 1.0))
    # the Foxhole flyer, the set order on its back in Nate's hand, taped to Amp_0's grille
    make_box("Flyer", (-2.05, 5.835, 0.30), (0.22, 0.004, 0.28), (0.90, 0.88, 0.80, 1.0))
    make_box("Flyer_Tape", (-2.05, 5.832, 0.45), (0.06, 0.003, 0.03), (0.86, 0.84, 0.70, 0.8))
    # the power strip and the cable run along the N wall's base
    make_box("Power_Strip", (0.6, ROOM_D - 0.10 - 0.05, 0.03), (0.34, 0.06, 0.05), (0.86, 0.86, 0.84, 1.0))


def build_band_gear_from_jesses():
    """Jesse's garage builder's kit, amps, Tele, bass and mic, moved
    2.4 m deeper so the kit sits at the finished room's back facing the
    partition door; the mic stand is moved on its own to the room's
    front (it would have stood in the partition)."""
    DY = 2.4
    def shifted(fn):
        def w(name, center, *a, **k):
            cx, cy, cz = center
            dy = DY + (1.1 if name.startswith("Mic") else 0.0)
            return fn(name, (cx, cy + dy, cz), *a, **k)
        return w
    orig_box, orig_cyl = HG.make_box, HG.make_cyl
    HG.make_box, HG.make_cyl = shifted(orig_box), shifted(orig_cyl)
    try:
        HG.build_band_gear()
    finally:
        HG.make_box, HG.make_cyl = orig_box, orig_cyl


def build_bay():
    """The front half: what a two-car garage keeps when the cars live in
    the driveway — Walt's road cases, the shelving, the mower, the bikes."""
    # Walt's road cases stacked on the W side (the wedding band's)
    for i, (x, y, z, sz) in enumerate(((-2.9, 2.6, 0.30, (0.90, 0.60, 0.60)), (-2.9, 2.6, 0.80, (0.80, 0.56, 0.40)), (-2.9, 1.7, 0.26, (0.60, 0.50, 0.52)))):
        make_chamfer_box(f"Road_Case_{i}", (x, y, z), sz, (0.14, 0.14, 0.15, 1.0), chamfer=0.02)
        make_box(f"Road_Case_{i}_Latch", (x + sz[0] / 2.0 + 0.004, y, z), (0.008, 0.10, 0.08), COL_STEEL)
    # steel shelving on the E side with bins and paint cans
    sx, sy = 3.1, 2.2
    for zi, z in enumerate((0.05, 0.75, 1.45, 2.05)):
        make_box(f"Shelf_{zi}", (sx, sy, z), (0.80, 1.60, 0.04), COL_STEEL)
    for pi, (px, py) in enumerate(((2.75, 1.5), (3.45, 1.5), (2.75, 2.9), (3.45, 2.9))):
        make_box(f"Shelf_Post_{pi}", (px, py, 1.05), (0.04, 0.04, 2.10), COL_STEEL_DK)
    for bi, (by, col) in enumerate(((1.75, (0.30, 0.40, 0.62, 1.0)), (2.35, (0.62, 0.30, 0.26, 1.0)), (2.95, (0.30, 0.40, 0.62, 1.0)))):
        make_box(f"Shelf_Bin_{bi}", (sx, by, 0.95), (0.60, 0.50, 0.36), col)
    for ci, cy in enumerate((1.7, 2.1, 2.5)):
        make_cyl(f"Paint_Can_{ci}", (sx + 0.1, cy, 1.57), 0.09, 0.20, (0.70, 0.68, 0.62, 1.0), segments=10)
    # the mower under the shelving's end, the bikes on hooks on the W wall
    make_box("Mower_Deck", (2.4, 0.9, 0.16), (0.56, 0.90, 0.20), (0.62, 0.14, 0.12, 1.0))
    for wi, (wx, wy) in enumerate(((2.16, 0.55), (2.64, 0.55), (2.16, 1.25), (2.64, 1.25))):
        make_cyl(f"Mower_Wheel_{wi}", (wx, wy, 0.10), 0.10, 0.06, COL_STEEL_DK, segments=10, axis='X')
    for hi, hx in enumerate((2.2, 2.6)):
        make_box(f"Mower_Handle_Bar_{hi}", (hx, 1.33, 0.62), (0.025, 0.025, 0.72), COL_STEEL)   # up from the deck's rear edge
    make_box("Mower_Handle", (2.4, 1.33, 1.0), (0.46, 0.04, 0.04), COL_STEEL)   # on the bars
    for bi, by in enumerate((0.8, 1.9)):
        make_cyl(f"Bike_{bi}_Wheel_F", (-3.3, by - 0.35, 1.55), 0.33, 0.03, COL_STEEL_DK, segments=16, axis='X')
        make_cyl(f"Bike_{bi}_Wheel_R", (-3.3, by + 0.35, 1.55), 0.33, 0.03, COL_STEEL_DK, segments=16, axis='X')
        make_rot_box(f"Bike_{bi}_Frame", (-3.3, by, 1.62), (0.03, 0.56, 0.03), (0.30, 0.46, 0.62, 1.0) if bi == 0 else (0.62, 0.30, 0.26, 1.0))
        make_box(f"Bike_{bi}_Hook", (-3.45, by, 1.95), (0.14, 0.03, 0.03), COL_STEEL)


def build_outside():
    """The driveway two cars wide, the Civic, the street with Carl's
    mother's car at the curb, the house on the east with its side door and
    the lit kitchen window, the lawn, a live oak, the neighbours."""
    make_box("Driveway", (0.0, -4.0, -0.02), (ROOM_W - 0.4, 8.0, 0.04), COL_DRIVE)
    for k in range(4):
        make_box(f"Driveway_Joint_{k}", (0.0, -1.5 - k * 1.8, 0.001), (ROOM_W - 0.4, 0.03, 0.006), COL_SEAM)
    make_box("Driveway_Joint_Mid", (0.0, -4.0, 0.001), (0.03, 8.0, 0.006), COL_SEAM)
    make_box("Lawn_W", (-7.0, -4.0, -0.03), (6.6, 8.0, 0.03), COL_LAWN)
    make_box("Lawn_E", (7.5, -4.0, -0.03), (7.0, 8.0, 0.03), COL_LAWN)
    make_box("Sidewalk", (0.0, -8.6, -0.02), (28.0, 1.2, 0.04), (0.60, 0.59, 0.58, 1.0))
    make_box("Curb", (0.0, -9.3, -0.03), (28.0, 0.2, 0.10), (0.58, 0.57, 0.55, 1.0))
    make_box("Street", (0.0, -13.0, -0.06), (28.0, 7.2, 0.04), COL_ASPHALT)
    make_box("Street_Centerline", (0.0, -13.0, -0.038), (28.0, 0.10, 0.004), (0.84, 0.78, 0.30, 1.0))
    make_box("Lawn_Far", (0.0, -19.5, -0.03), (28.0, 6.0, 0.03), COL_LAWN)
    # Jesse's Civic in the driveway, nose to the bay; Carl's mother's car at the curb
    make_car("Civic", -1.6, -3.4, 4.3, (0.52, 0.56, 0.60, 1.0), along="Y", hatch=True)
    make_car("Carls_Mothers_Car", 5.2, -10.2, 4.6, (0.26, 0.28, 0.34, 1.0), along="X")
    # the house, attached on the east: a brick-tan box with its roof, the side door, the kitchen window
    make_box("House", (8.2, 3.8, 1.45), (8.0, 8.0, 2.9), COL_HOUSE)
    make_box("House_Roof", (8.2, 3.8, 3.15), (8.6, 8.6, 0.50), COL_ROOF)
    make_box("Garage_Roof", (0.0, ROOM_D / 2.0, CEIL + 0.25), (ROOM_W + 0.8, ROOM_D + 0.8, 0.50), COL_ROOF)
    make_box("House_Side_Door", (5.6, -0.22, 1.02), (0.90, 0.05, 2.04), (0.30, 0.22, 0.18, 1.0))
    make_frame_ring("House_Side_Door_Frame", (5.6, -0.20, 1.02), (1.04, 0.04, 2.12), COL_TRIM)
    make_box("House_Side_Step", (5.6, -0.60, 0.06), (1.20, 0.70, 0.12), (0.60, 0.59, 0.58, 1.0))
    make_box("Porch_Light", (6.3, -0.24, 2.30), (0.12, 0.08, 0.20), COL_GLOW)
    make_frame_ring("Kitchen_Window_Frame", (8.4, -0.20, 1.50), (1.30, 0.04, 1.00), COL_TRIM)
    make_box("Kitchen_Window", (8.4, -0.19, 1.50), (1.16, 0.01, 0.86), COL_GLASS_WARM)
    make_box("Kitchen_Window_Muntin", (8.4, -0.215, 1.50), (0.03, 0.01, 0.86), COL_TRIM)
    # the live oak on the west lawn, the neighbours across the street
    make_taper_cyl("Live_Oak_Trunk", (-6.5, -4.5, 1.6), 0.30, 0.20, 3.2, (0.36, 0.28, 0.22, 1.0), segments=9)
    make_blob("Live_Oak_Crown", (-6.5, -4.5, 5.0), 3.0, (0.20, 0.30, 0.14, 1.0), noise=0.22, seed=7, squash=0.7)
    for hi, hx in enumerate((-8.0, 0.0, 8.0)):
        make_box(f"Neighbour_{hi}", (hx, -22.0, 1.6), (7.0, 7.0, 3.2), (0.56, 0.52, 0.48, 1.0) if hi != 1 else (0.64, 0.60, 0.52, 1.0))
        make_box(f"Neighbour_{hi}_Roof", (hx, -22.0, 3.45), (7.6, 7.6, 0.50), COL_ROOF)
        make_box(f"Neighbour_{hi}_Window", (hx - 1.5, -18.48, 1.5), (1.2, 0.02, 0.9), COL_GLASS_WARM if hi == 1 else (0.20, 0.22, 0.26, 1.0))
    make_box("Street_Lamp_Post", (-4.2, -8.9, 2.4), (0.14, 0.14, 4.8), COL_STEEL_DK)
    make_box("Street_Lamp_Head", (-4.2, -9.3, 4.85), (0.30, 0.70, 0.18), COL_STEEL_DK)
    make_box("Street_Lamp_Lens", (-4.2, -9.45, 4.74), (0.24, 0.36, 0.03), COL_GLOW)


def main():
    clear_scene()
    build_shell()
    build_finished_room()
    build_band_gear_from_jesses()
    build_bay()
    build_outside()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/nate_garage.glb"))
    print(f"\n[build_nate_garage] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
