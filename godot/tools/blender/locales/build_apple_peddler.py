"""apple_peddler — vol 2's Apple Peddler, the 24-hour diner in d.dean's
story (draft 1, 2026-10-18).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
The diner exists in the page the narrator finds in the copy shop's
wastebasket: "right off the main drag through town, next door to the
Greyhound Station", open twenty-four hours.
  the "stall" Bernard sits in             → the booths under the front glass
  the cigarette machine and the periodicals machine
                                          → Vending_* by the door
  the tide tables stacked on the floor by the door      → Tide_Tables
  the one-page laminated menu, the apple pie, the pots of coffee, the
   register, the ashtrays (smoking at the table)
  the rain outside                        → the front glass dark and
                                             streaked, the wet main drag,
                                             the Greyhound depot next door
  the kitchen behind the pass: the grill and the fryer (the grill view
   also plays vol 2's "local diner", which the text never names, and the
   evening diner of ch5 plays a booth — reuses, noted in bg_places).
The text gives no time of day for the Apple Peddler itself.

Blender: x east, y north, z up; Godot (x, z, -y). The front faces south
onto the main drag; the depot stands east.

DRAFT 2 targets: the depot as more than a box (its own doors and bays);
the waitresses' station; the pie case's pies as more than discs; a dawn
light state for the grill (vol 2's "open up"); Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_lathe,
                             join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings
from _props.furniture import make_chair
from _props.safety import make_fluorescent_tube_fixture
from _props.vehicles import make_car

X0, X1, D, H, T = -7.0, 7.0, 9.0, 3.0, 0.20
WALL = (0.84, 0.78, 0.62, 1.0); BASE = (0.40, 0.30, 0.22, 1.0)
PAL = {"wall": WALL, "baseboard": BASE}
TILE_A = (0.86, 0.84, 0.78, 1.0); TILE_B = (0.30, 0.30, 0.32, 1.0)
VINYL_RED = (0.62, 0.16, 0.14, 1.0); CHROME = (0.80, 0.80, 0.80, 1.0)
FORMICA = (0.86, 0.82, 0.70, 1.0)
STEEL = (0.66, 0.68, 0.70, 1.0)
NIGHT_GLASS = (0.06, 0.07, 0.10, 0.45)   # (2026-10-29) was opaque: the wet drag never showed
KX0, KD = 2.0, 3.0          # the kitchen: x 2..7 behind the counter, y 6..9


def build_room():
    cx, cy = (X0 + X1) / 2.0, D / 2.0
    make_floor("AP_Floor", (cx, cy, 0.0), size_x=X1 - X0 + 0.4, size_y=D + 0.4, palette={"vinyl": TILE_A, "seam": TILE_B})
    for i in range(14):
        for j in range(9):
            if (i + j) % 2 == 0:
                make_box(f"AP_Check_Stock_{i}_{j}", (X0 + 0.5 + i, 0.5 + j, 0.003), (1.0, 1.0, 0.004), TILE_B)
    make_box("AP_Ceil", (cx, cy, H + 0.04), (X1 - X0 + 0.4, D + 0.4, 0.08), (0.90, 0.88, 0.82, 1.0))
    make_wall("AP_Wall_N", (cx, D, 0), length=X1 - X0 + 0.4, height=H, thickness=T, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall("AP_Wall_W", (X0, cy, 0), length=D + 0.4, height=H, thickness=T, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall_with_openings("AP_Wall_E", (X1, cy, 0), length=D + 0.4, height=H, thickness=T, axis='Y', palette=PAL,
                            baseboard_face_sign=-1, openings=[(8.3, 1.0, 0.86, 2.0)])
    make_box("AP_Back_Door", (X1, 8.3, 1.0), (0.05, 0.88, 2.0), (0.50, 0.50, 0.52, 1.0))
    # the front: a long band of glass onto the main drag, the door at its E end
    make_wall_with_openings("AP_Wall_S", (cx, 0.0, 0), length=X1 - X0 + 0.4, height=H, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=+1, openings=[(-2.5, 1.55, 8.4, 1.5), (4.9, 1.05, 1.0, 2.1)])
    make_box("AP_Front_Glass", (-2.5, 0.0, 1.55), (8.4, 0.02, 1.5), NIGHT_GLASS)
    for k in range(5):
        make_box(f"AP_Front_Mullion_{k}", (-6.7 + k * 2.1, 0.0, 1.55), (0.06, 0.08, 1.5), CHROME)
    for k in range(40):        # the rain on the glass
        x = -6.5 + (k * 37 % 840) / 100.0
        z = 0.95 + (k * 53 % 120) / 100.0
        make_box(f"AP_Rain_Stock_{k}", (x, 0.012, z), (0.006, 0.004, 0.10 + (k % 4) * 0.05), (0.40, 0.46, 0.54, 1.0))
    make_box("AP_Front_Door", (4.9, 0.0, 1.05), (0.98, 0.05, 2.08), CHROME)
    make_box("AP_Front_Door_Glass", (4.9, 0.0, 1.20), (0.70, 0.06, 1.50), NIGHT_GLASS)
    for k in range(3):
        make_fluorescent_tube_fixture(f"AP_Fluor_{k}", (-4.5 + k * 4.5, 4.0, H), length=1.20, width=0.30)
    # the booths ("stall") under the glass: red vinyl, a formica table each,
    # the ashtray, the sugar, the laminated menu
    for k in range(4):
        bx = -5.8 + k * 2.1
        for s in (-1, 1):
            make_box(f"Booth_{k}_Seat_{s:+d}", (bx + s * 0.62, 0.70, 0.24), (0.50, 1.10, 0.48), VINYL_RED)
            make_box(f"Booth_{k}_Back_{s:+d}", (bx + s * 0.86, 0.70, 0.78), (0.14, 1.10, 0.64), VINYL_RED)
        make_box(f"Booth_{k}_Table", (bx, 0.66, 0.74), (0.70, 0.96, 0.04), FORMICA)
        make_box(f"Booth_{k}_Table_Edge", (bx, 0.66, 0.715), (0.72, 0.98, 0.02), CHROME)
        make_cyl(f"Booth_{k}_Post", (bx, 0.66, 0.36), 0.04, 0.72, CHROME, segments=8)
        make_cyl(f"Booth_{k}_Ashtray", (bx - 0.18, 0.40, 0.77), 0.06, 0.02, (0.30, 0.30, 0.32, 1.0), segments=12)
        make_cyl(f"Booth_{k}_Sugar", (bx + 0.20, 0.30, 0.82), 0.04, 0.12, (0.90, 0.90, 0.88, 1.0), segments=10)
        make_box(f"Booth_{k}_Menu", (bx + 0.05, 0.80, 0.765), (0.24, 0.34, 0.006), (0.94, 0.90, 0.76, 1.0))
    # Bernard's booth (the W end): his coffee, his pie, the smoke
    make_cyl("Bernard_Coffee", (-5.75, 0.80, 0.81), 0.04, 0.10, (0.94, 0.94, 0.92, 1.0), segments=10)
    make_cyl("Bernard_Pie_Plate", (-5.95, 0.62, 0.765), 0.10, 0.01, (0.94, 0.94, 0.92, 1.0), segments=14)
    make_rot_box("Bernard_Pie_Slice", (-5.95, 0.62, 0.79), (0.10, 0.08, 0.04), (0.84, 0.62, 0.34, 1.0), yaw=0.4)
    make_rot_box("Bernard_Cigarette", (-6.0, 0.40, 0.785), (0.06, 0.008, 0.008), (0.96, 0.96, 0.94, 1.0), yaw=0.3)
    # the counter and its stools, the register, the pie case, the coffee
    make_box("Counter", (-0.5, 5.6, 0.52), (9.0, 0.70, 1.04), (0.62, 0.20, 0.16, 1.0))
    make_box("Counter_Top", (-0.5, 5.6, 1.055), (9.1, 0.80, 0.03), FORMICA)
    make_box("Counter_Kick", (-0.5, 5.24, 0.06), (9.0, 0.04, 0.12), CHROME)
    for k in range(8):
        x = -4.5 + k * 1.1
        make_cyl(f"Stool_{k}_Post", (x, 4.85, 0.36), 0.04, 0.72, CHROME, segments=8)
        make_cyl(f"Stool_{k}_Seat", (x, 4.85, 0.76), 0.20, 0.08, VINYL_RED, segments=14)
        make_cyl(f"Stool_{k}_Foot", (x, 4.85, 0.02), 0.16, 0.04, CHROME, segments=12)
    make_box("Register", (3.4, 5.6, 1.17), (0.40, 0.36, 0.20), (0.40, 0.40, 0.42, 1.0))
    make_box("Register_Drawer", (3.4, 5.40, 1.10), (0.36, 0.04, 0.06), (0.40, 0.40, 0.42, 1.0))
    make_box("Pie_Case", (-3.2, 5.6, 1.30), (0.80, 0.50, 0.46), (0.82, 0.86, 0.88, 1.0))
    for k in range(3):
        make_cyl(f"Pie_{k}", (-3.2, 5.6, 1.14 + k * 0.14), 0.20, 0.05, (0.86, 0.64, 0.34, 1.0), segments=14)
    for k in range(3):
        make_box(f"Pie_Shelf_{k}", (-3.2, 5.6, 1.11 + k * 0.14), (0.76, 0.46, 0.006), (0.80, 0.84, 0.86, 1.0))
    # the back bar: the coffee station, the pots, the cups
    make_box("Back_Bar", (-2.5, D - 0.10 - 0.32, 0.46), (5.0, 0.64, 0.92), (0.62, 0.20, 0.16, 1.0))
    make_box("Back_Bar_Top", (-2.5, D - 0.10 - 0.33, 0.935), (5.1, 0.66, 0.03), FORMICA)
    make_box("Coffee_Maker", (-1.6, D - 0.10 - 0.30, 1.20), (0.70, 0.40, 0.50), STEEL)
    for k in range(3):
        make_cyl(f"Coffee_Pot_{k}", (-1.85 + k * 0.25, D - 0.10 - 0.48, 1.03), 0.08, 0.16, (0.30, 0.20, 0.14, 1.0), segments=12)
    for k in range(10):
        make_cyl(f"Cup_Stack_{k}", (-4.4 + (k % 5) * 0.12, D - 0.10 - 0.30, 0.99 + (k // 5) * 0.10), 0.04, 0.10,
                 (0.94, 0.94, 0.92, 1.0), segments=10)
    make_box("Menu_Board", (-2.5, D - 0.11, 2.15), (3.0, 0.02, 0.70), (0.16, 0.16, 0.18, 1.0))
    for k in range(6):
        make_box(f"Menu_Board_Line_{k}", (-2.5, D - 0.122, 2.40 - k * 0.10), (2.4 - (k % 3) * 0.4, 0.004, 0.03), (0.92, 0.90, 0.80, 1.0))
    # by the door: the cigarette machine, the periodicals machine, the tide tables
    make_box("Vending_Cigarette", (6.4, 1.8, 0.90), (0.70, 0.60, 1.80), (0.70, 0.18, 0.16, 1.0))
    make_box("Vending_Cigarette_Face", (6.04, 1.8, 1.20), (0.02, 0.50, 0.80), (0.86, 0.84, 0.76, 1.0))
    for k in range(5):
        make_box(f"Vending_Cigarette_Pull_{k}", (6.03, 1.6 + (k % 5) * 0.10, 0.70), (0.04, 0.06, 0.04), CHROME)
    make_box("Vending_Periodicals", (6.5, 3.0, 0.55), (0.56, 0.50, 1.10), (0.20, 0.34, 0.56, 1.0))
    make_box("Vending_Periodicals_Window", (6.21, 3.0, 0.85), (0.02, 0.40, 0.30), (0.70, 0.74, 0.76, 1.0))
    for k in range(5):
        make_box(f"Tide_Tables_{k}", (5.7 + (k % 2) * 0.03, 0.50, 0.02 + k * 0.03), (0.30, 0.20, 0.03), (0.92, 0.90, 0.80, 1.0))
    make_box("Doormat", (4.9, 0.70, 0.008), (1.2, 0.8, 0.016), (0.20, 0.18, 0.16, 1.0))


def build_kitchen():
    """Behind the counter and the pass: the grill, the fryer, the hood, the
    reach-in; the line's light."""
    kx0, ky0 = KX0, D - KD
    # the pass between the dining room and the line
    make_box("Pass_Wall_W", (KX0 - 0.10, ky0 + KD / 2.0, H / 2.0), (0.2, KD, H), WALL)
    make_wall_with_openings("Pass_Wall_S", ((KX0 + X1) / 2.0, ky0, 0), length=X1 - KX0, height=H, thickness=0.14, axis='X',
                            palette=PAL, baseboard_face_sign=+1, openings=[(3.6, 1.45, 2.6, 0.70), (6.2, 1.0, 0.80, 2.0)])
    make_box("Pass_Shelf", (3.6, ky0, 1.10), (2.6, 0.40, 0.03), STEEL)
    make_box("Pass_Heat_Lamp", (3.6, ky0 + 0.10, 1.76), (2.4, 0.20, 0.08), (0.30, 0.30, 0.32, 1.0))
    make_box("Pass_Ticket_Rail", (3.6, ky0 - 0.03, 1.785), (2.4, 0.02, 0.03), STEEL)
    for k in range(3):
        make_box(f"Pass_Ticket_{k}", (2.8 + k * 0.6, ky0 - 0.03, 1.70), (0.08, 0.004, 0.14), (0.96, 0.96, 0.92, 1.0))
    make_box("Kitchen_Floor", ((KX0 + X1) / 2.0, ky0 + KD / 2.0, 0.006), (X1 - KX0, KD, 0.012), (0.56, 0.54, 0.50, 1.0))
    # the line against the N wall: the flat-top grill, the fryer, the hood over them
    gy = D - 0.10 - 0.40
    make_box("Grill_Body", (3.85, gy, 0.44), (1.40, 0.80, 0.88), STEEL)
    make_box("Grill_Top", (3.85, gy, 0.895), (1.40, 0.76, 0.03), (0.20, 0.20, 0.20, 1.0))
    make_box("Grill_Backsplash", (3.85, gy + 0.36, 1.10), (1.40, 0.04, 0.38), STEEL)
    for k in range(4):
        make_cyl(f"Grill_Pancake_{k}", (3.45 + k * 0.25, gy - 0.10, 0.915), 0.07, 0.01, (0.86, 0.66, 0.36, 1.0), segments=12)
    make_box("Grill_Spatula", (4.45, gy - 0.32, 0.92), (0.30, 0.08, 0.01), STEEL)
    make_box("Fryer_Body", (4.95, gy, 0.44), (0.60, 0.80, 0.88), STEEL)
    for s in (-1, 1):
        make_box(f"Fryer_Basket_{s:+d}", (4.95 + s * 0.14, gy - 0.05, 0.95), (0.22, 0.34, 0.12), (0.70, 0.70, 0.72, 1.0))
    make_box("Hood", (4.3, D - 0.10 - 0.40, 2.30), (2.80, 0.80, 0.50), STEEL)
    make_box("Hood_Duct", (4.3, gy + 0.20, 2.70), (0.60, 0.40, 0.30), STEEL)
    make_box("Reach_In", (2.6, gy + 0.05, 1.0), (0.80, 0.70, 2.0), STEEL)
    make_box("Prep_Table", (6.3, 6.9, 0.45), (0.70, 1.20, 0.90), STEEL)
    make_box("Prep_Table_Top", (6.3, 6.9, 0.905), (0.72, 1.22, 0.02), STEEL)


def build_outside():
    """The main drag in the rain, the Greyhound depot next door (E)."""
    make_box("Drag_Walk", (0.0, -2.0, 0.06), (40.0, 3.6, 0.12), (0.46, 0.46, 0.46, 1.0))
    make_box("Drag_Road", (0.0, -8.0, -0.01), (60.0, 8.4, 0.02), (0.18, 0.18, 0.20, 1.0))
    for k in range(8):
        make_box(f"Drag_Line_{k}", (-24.0 + k * 7.0, -8.0, 0.002), (3.0, 0.12, 0.004), (0.80, 0.76, 0.40, 1.0))
    for k in range(6):
        make_cyl(f"Drag_Puddle_{k}", (-12.0 + k * 5.0, -6.5 - (k % 2) * 2.0, 0.003), 0.8, 0.004, (0.30, 0.34, 0.40, 1.0), segments=14)
    make_box("Depot_Mass", (14.0, 4.0, 2.8), (12.0, 10.0, 5.6), (0.70, 0.70, 0.68, 1.0))
    make_box("Depot_Canopy", (14.0, -1.0, 3.2), (12.0, 2.6, 0.20), (0.50, 0.52, 0.56, 1.0))
    for k in range(4):
        make_cyl(f"Depot_Canopy_Post_{k}", (9.0 + k * 3.4, -2.1, 1.55), 0.08, 3.10, (0.50, 0.52, 0.56, 1.0), segments=8)
    make_box("Depot_Sign", (14.0, -1.0, 3.80), (5.0, 0.20, 0.80), (0.20, 0.36, 0.66, 1.0))
    make_box("Depot_Doors", (14.0, -1.02 + 0.10 - 0.01, 1.2), (3.0, 0.04, 2.4), (0.30, 0.34, 0.40, 1.0))
    for k in range(3):
        make_box(f"Across_Bldg_{k}", (-14.0 + k * 13.0, -18.0, 3.5), (11.0, 6.0, 7.0), ((0.56, 0.50, 0.44, 1.0), (0.46, 0.44, 0.42, 1.0))[k % 2])
    make_car("Drag_Car_0", -6.0, -4.9, 4.4, (0.30, 0.30, 0.34, 1.0), along="X")
    # (2026-10-29) the drag's sodium lamps, and the lit windows of the
    # buildings across it — what shows through the rain on the glass
    for k, sx in enumerate((-7.0, 5.0)):
        make_cyl(f"Drag_Lamp_{k}_Pole", (sx, -3.4, 2.6), 0.07, 5.2, (0.30, 0.30, 0.32, 1.0), segments=8)
        make_box(f"Drag_Lamp_{k}_Arm", (sx, -4.0, 5.1), (0.08, 1.2, 0.08), (0.30, 0.30, 0.32, 1.0))
        make_box(f"Drag_Lamp_{k}_Head", (sx, -4.6, 5.0), (0.30, 0.50, 0.14), (1.0, 0.70, 0.36, 1.0))
    for k in range(3):
        for j in range(2):
            for w in range(3):
                lit = (k + j + w) % 3 == 0
                make_box(f"Across_Window_{k}_{j}_{w}", (-14.0 + k * 13.0 - 3.0 + w * 3.0, -14.98, 1.6 + j * 2.6), (1.6, 0.02, 1.3),
                         (1.0, 0.80, 0.50, 1.0) if lit else (0.12, 0.13, 0.16, 1.0))
    # the sign over the front glass, on the wall's outside face
    make_box("AP_Sign_Board", (-1.5, -0.16, 2.66), (6.0, 0.12, 0.56), (0.90, 0.86, 0.70, 1.0))
    make_box("AP_Sign_Apple", (-4.2, -0.24, 2.66), (0.46, 0.04, 0.46), (0.80, 0.16, 0.14, 1.0))


def main():
    clear_scene()
    build_room()
    build_kitchen()
    build_outside()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/apple_peddler.glb"))
    print(f"\n[build_apple_peddler] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
