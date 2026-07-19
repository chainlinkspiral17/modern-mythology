"""Henderson house front porch + driveway — vol6 placement script.

Canon: ch7 "The First Part Is Done" — Ben walks Jesse to the front
porch at night, they sit on the steps. ch14 "Live Oak" — Jesse pulls
into the driveway at 10:48 PM, the house mostly dark, THE KITCHEN
LIGHT LEFT ON for him (his mother's practice-night ritual — the one
lit window is the emotional center of the shot). ch19 — the same
arrival, later.

Hero features: the front of the house with the ONE LIT WINDOW
(kitchen, warm) among dark ones, the concrete porch with steps the
boys sit on, porch posts + a porch light (off — the kitchen glow and
the street carry it), the driveway with Jesse's parked Civic-class
sedan, the front lawn, mailbox at the curb, the cul-de-sac street
edge.

Coordinate frame: Blender Z-up. y=0 is the house FRONT WALL; +Y runs
toward the street; the curb is at y=YARD_D. glTF export remaps to
Godot (x, z, -y).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

YARD_W = 12.0     # x ∈ [-6, 6]
YARD_D = 8.5      # y ∈ [0, 8.5] house→curb
HOUSE_H = 3.2

COL_SIDING = (0.40, 0.42, 0.46, 1.0)    # blue-grey siding, night-dim
COL_SIDING_DK = (0.32, 0.34, 0.38, 1.0)
COL_TRIM = (0.55, 0.55, 0.52, 1.0)
COL_ROOF = (0.20, 0.20, 0.22, 1.0)
COL_DARKGLASS = (0.10, 0.12, 0.16, 1.0) # unlit windows
COL_LITGLASS = (1.00, 0.82, 0.48, 1.0)  # THE kitchen window — blooms
COL_PORCH = (0.48, 0.47, 0.45, 1.0)
COL_STEP = (0.42, 0.41, 0.39, 1.0)
COL_POST = (0.50, 0.50, 0.47, 1.0)
COL_DOOR = (0.26, 0.16, 0.12, 1.0)
COL_LAWN = (0.16, 0.22, 0.12, 1.0)      # night lawn
COL_DRIVE = (0.34, 0.34, 0.36, 1.0)
COL_STREET = (0.22, 0.22, 0.24, 1.0)
COL_CURB = (0.40, 0.40, 0.40, 1.0)
COL_CAR = (0.30, 0.32, 0.36, 1.0)       # the Civic, night grey-blue
COL_CAR_DK = (0.18, 0.19, 0.22, 1.0)
COL_GLASS = (0.14, 0.16, 0.20, 1.0)
COL_MAILBOX = (0.24, 0.26, 0.28, 1.0)
COL_TREE = (0.30, 0.24, 0.16, 1.0)
COL_CANOPY = (0.14, 0.20, 0.11, 1.0)


def build_ground():
    make_box("Lawn", (0.0, YARD_D / 2.0, -0.02), (YARD_W, YARD_D, 0.04), COL_LAWN)
    # Driveway on the EAST side, house to street
    make_box("Driveway", (3.4, YARD_D / 2.0, 0.0), (3.0, YARD_D, 0.05), COL_DRIVE)
    for k in range(3):
        make_box(f"Drive_Joint_{k}", (3.4, 1.6 + k * 2.4, 0.03), (3.0, 0.03, 0.01),
                 (0.28, 0.28, 0.30, 1.0))
    # Front walk from porch to street, west of the driveway
    make_box("Walk", (0.0, YARD_D / 2.0 + 0.6, 0.0), (0.9, YARD_D - 1.2, 0.045), COL_PORCH)
    # Street + curb along the far edge
    make_box("Street", (0.0, YARD_D + 1.6, -0.06), (YARD_W + 4.0, 3.2, 0.04), COL_STREET)
    make_box("Curb", (0.0, YARD_D + 0.08, -0.01), (YARD_W + 4.0, 0.16, 0.10), COL_CURB)


def build_house():
    """Front elevation: mostly dark. One warm window."""
    make_box("House_Wall", (0.0, -0.15, HOUSE_H / 2.0), (YARD_W - 1.0, 0.3, HOUSE_H), COL_SIDING)
    for k in range(6):
        make_box(f"Siding_Line_{k}", (0.0, 0.02, 0.4 + k * 0.5), (YARD_W - 1.2, 0.02, 0.03),
                 COL_SIDING_DK)
    # Roof suggestion — eave slab + a shallow gable face
    make_box("Eave", (0.0, 0.2, HOUSE_H + 0.06), (YARD_W - 0.6, 0.8, 0.12), COL_ROOF)
    make_box("Gable", (0.0, -0.1, HOUSE_H + 0.55), (5.0, 0.25, 0.9), COL_SIDING_DK)
    make_box("Gable_Peak", (0.0, -0.1, HOUSE_H + 1.1), (2.4, 0.24, 0.35), COL_SIDING_DK)
    # Front door at center behind the porch
    make_box("Front_Door", (0.0, 0.02, 1.05), (0.95, 0.10, 2.1), COL_DOOR)
    make_cyl("Door_Knob", (0.35, 0.09, 1.0), 0.03, 0.04, COL_TRIM, segments=8, axis='Y')
    # Windows: living room (dark, W), bedroom above (dark), and THE
    # KITCHEN WINDOW east of the door — LIT (the mother's ritual)
    make_box("Win_Living_Frame", (-3.2, 0.04, 1.5), (1.7, 0.10, 1.2), COL_TRIM)
    make_box("Win_Living", (-3.2, 0.07, 1.5), (1.55, 0.02, 1.05), COL_DARKGLASS)
    make_box("Win_Living_Mull", (-3.2, 0.08, 1.5), (0.04, 0.02, 1.05), COL_TRIM)
    make_box("Win_Up_Frame", (-1.6, 0.02, HOUSE_H - 0.42), (1.1, 0.08, 0.75), COL_TRIM)
    make_box("Win_Up", (-1.6, 0.05, HOUSE_H - 0.42), (0.98, 0.02, 0.62), COL_DARKGLASS)
    # THE lit window
    make_box("Win_Kitchen_Frame", (2.55, 0.04, 1.55), (1.4, 0.10, 1.05), COL_TRIM)
    make_box("Win_Kitchen_LIT", (2.55, 0.07, 1.55), (1.26, 0.02, 0.92), COL_LITGLASS)
    make_box("Win_Kitchen_Mull", (2.55, 0.085, 1.55), (0.04, 0.02, 0.92), COL_TRIM)
    make_box("Win_Kitchen_Sill", (2.55, 0.10, 1.0), (1.5, 0.14, 0.05), COL_TRIM)


def build_porch():
    """Concrete porch + THE STEPS (ch7: they sit here) + posts."""
    make_box("Porch_Slab", (0.0, 0.75, 0.18), (3.2, 1.5, 0.36), COL_PORCH)
    # Three steps down toward the walk
    for s in range(3):
        make_box(f"Porch_Step_{s}", (0.0, 1.5 + 0.18 + s * 0.30, 0.12 - s * 0.06),
                 (1.7, 0.32, 0.12), COL_STEP)
    # Posts + simple rail
    for sgn in (-1, 1):
        make_box(f"Porch_Post_{sgn:+d}", (sgn * 1.45, 1.35, 1.35), (0.12, 0.12, 2.35), COL_POST)
        make_box(f"Porch_Rail_{sgn:+d}", (sgn * 1.45, 0.65, 0.85), (0.08, 1.3, 0.08), COL_POST)
    make_box("Porch_Header", (0.0, 1.35, 2.55), (3.1, 0.14, 0.14), COL_POST)
    # Porch light by the door — OFF (dark glass), the kitchen carries
    make_box("Porch_Lamp", (-0.65, 0.06, 2.0), (0.12, 0.10, 0.20), COL_MAILBOX)
    # A forgotten glass of iced tea on the top step (they sat a while)
    make_cyl("Tea_Glass", (0.55, 1.55, 0.42), 0.04, 0.12, (0.45, 0.35, 0.22, 0.8), segments=8)


def build_car_and_curb():
    """Jesse's sedan nose-in on the driveway; mailbox; the live oak
    the street is named for, dark overhead at the curb."""
    cx, cy = 3.4, 3.4
    make_box("Car_Body", (cx, cy, 0.52), (1.75, 4.2, 0.55), COL_CAR)
    make_box("Car_Cabin", (cx, cy + 0.1, 0.98), (1.55, 2.2, 0.42), COL_CAR_DK)
    make_box("Car_Windshield", (cx, cy - 1.0, 0.95), (1.45, 0.06, 0.38), COL_GLASS)
    make_box("Car_Rear_Glass", (cx, cy + 1.2, 0.95), (1.45, 0.06, 0.36), COL_GLASS)
    for sy in (-1.4, 1.4):
        for sx in (-0.85, 0.85):
            make_cyl(f"Car_Wheel_{sx:+.1f}_{sy:+.1f}", (cx + sx, cy + sy, 0.30),
                     0.30, 0.16, (0.10, 0.10, 0.11, 1.0), segments=12, axis='X')
    make_box("Car_Bumper_F", (cx, cy - 2.12, 0.42), (1.7, 0.10, 0.22), COL_CAR_DK)
    make_box("Car_Plate", (cx, cy - 2.17, 0.55), (0.32, 0.02, 0.16), (0.6, 0.6, 0.58, 1.0))
    # Mailbox at the curb on a post
    make_box("Mailbox_Post", (-1.2, YARD_D - 0.3, 0.55), (0.08, 0.08, 1.1), COL_TREE)
    make_box("Mailbox", (-1.2, YARD_D - 0.3, 1.18), (0.24, 0.5, 0.24), COL_MAILBOX)
    # The live oak at the curb — big dark canopy over the street edge
    tx, ty = -4.6, YARD_D - 0.8
    make_cyl("Oak_Trunk", (tx, ty, 1.5), 0.34, 3.0, COL_TREE, segments=10)
    make_cyl("Oak_Canopy_A", (tx, ty, 3.6), 2.4, 1.6, COL_CANOPY, segments=12)
    make_cyl("Oak_Canopy_B", (tx + 1.2, ty - 0.6, 3.2), 1.5, 1.2, COL_CANOPY, segments=10)
    make_cyl("Oak_Canopy_C", (tx - 1.1, ty + 0.5, 3.3), 1.4, 1.1, COL_CANOPY, segments=10)
    # Streetlamp far east — a cool pool on the asphalt edge
    make_cyl("StreetLamp_Pole", (5.6, YARD_D + 0.4, 2.4), 0.07, 4.8, COL_MAILBOX, segments=8)
    make_box("StreetLamp_Arm", (5.25, YARD_D + 0.4, 4.7), (0.7, 0.07, 0.07), COL_MAILBOX)
    make_box("StreetLamp_Head", (4.95, YARD_D + 0.4, 4.62), (0.35, 0.18, 0.10),
             (0.80, 0.78, 0.62, 1.0))


def main():
    clear_scene()
    build_ground()
    build_house()
    build_porch()
    build_car_and_curb()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/henderson_porch_front.glb"))
    print(f"\n[build_henderson_porch_front] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
