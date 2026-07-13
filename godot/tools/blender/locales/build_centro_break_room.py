"""Centro Grocery — break room — vol6 placement script."""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots, make_donut_display
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture, make_ceiling_speaker

ROOM_W = 5.0; ROOM_D = 4.0; CEIL = 2.6
PAL_WALL = {"wall": (0.74, 0.74, 0.70, 1.0), "baseboard": (0.32, 0.30, 0.28, 1.0)}
COL_FLOOR = (0.62, 0.58, 0.52, 1.0); COL_SEAM = (0.32, 0.30, 0.28, 1.0); COL_WOOD = (0.42, 0.32, 0.22, 1.0)
COL_ACCENT = (0.86, 0.62, 0.28, 1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})

def build_table():
    tx, ty = 0.0, ROOM_D/2.0
    make_cyl("Table_Top", (tx, ty, 0.74), 0.40, 0.04, COL_WOOD)
    make_cyl("Table_Pedestal", (tx, ty, 0.37), 0.06, 0.70, COL_WOOD)
    for ci in range(4):
        import math
        ang = ci * 1.57
        cx, cy = tx + math.cos(ang)*0.85, ty + math.sin(ang)*0.85
        make_box(f"Chair_{ci}_Seat", (cx, cy, 0.44), (0.38, 0.38, 0.04), COL_WOOD)
        make_box(f"Chair_{ci}_Back", (cx + math.cos(ang)*0.16, cy + math.sin(ang)*0.16, 0.72), (0.38, 0.04, 0.56), COL_WOOD)
        for lx in (-0.15, 0.15):
            for ly in (-0.15, 0.15):
                make_box(f"Chair_{ci}_Leg_{lx}_{ly}", (cx+lx, cy+ly, 0.22), (0.03, 0.03, 0.44), P.METAL_BLACK)

def build_vending():
    vx, vy = +ROOM_W/2.0-0.30, ROOM_D-1.0
    make_box("Vending_Body", (vx, vy, 1.00), (0.50, 0.70, 2.00), COL_ACCENT)
    make_box("Vending_Glass", (vx-0.26, vy, 1.20), (0.04, 0.66, 1.20), (0.78, 0.84, 0.86, 0.50))
    for r in range(4):
        for c in range(5):
            make_box(f"Vending_Snack_{r}_{c}", (vx-0.22, vy-0.28+c*0.14, 0.70+r*0.30), (0.04, 0.10, 0.18), P.SNACK_TINTS[(r+c)%len(P.SNACK_TINTS)])

def build_kitchenette():
    """Galley counter along the W wall: sink + faucet, a compound
    microwave, a drip coffee station, and upper cabinets."""
    cx = -ROOM_W/2.0 + 0.28
    cy0 = ROOM_D/2.0
    # Counter carcass + top
    make_box("Counter_Body", (cx, cy0, 0.45), (0.52, 2.60, 0.90), COL_WOOD)
    make_box("Counter_Top", (cx, cy0, 0.92), (0.56, 2.64, 0.05), P.METAL_STEEL)
    make_box("Counter_Kick", (cx, cy0, 0.05), (0.44, 2.56, 0.10), (0.20, 0.16, 0.12, 1.0))
    # Cabinet doors under the counter
    for di, dy in enumerate([cy0-0.85, cy0-0.28, cy0+0.30, cy0+0.88]):
        make_box(f"Counter_Door_{di}", (cx-0.24, dy, 0.46), (0.02, 0.50, 0.72), (0.36, 0.28, 0.18, 1.0))
        make_box(f"Counter_Pull_{di}", (cx-0.26, dy+0.20, 0.46), (0.02, 0.03, 0.12), P.METAL_BLACK)
    # Sink basin (recessed dark box + rim) at the S third
    sy = cy0 - 0.80
    make_box("Sink_Rim", (cx, sy, 0.93), (0.42, 0.44, 0.03), P.METAL_STEEL)
    make_box("Sink_Basin", (cx, sy, 0.86), (0.34, 0.36, 0.14), (0.30, 0.32, 0.34, 1.0))
    # Faucet (riser + gooseneck spout)
    make_cyl("Faucet_Riser", (cx+0.10, sy+0.16, 1.02), 0.02, 0.18, P.METAL_STEEL, segments=8, axis='Z')
    make_cyl("Faucet_Spout", (cx, sy+0.10, 1.12), 0.018, 0.24, P.METAL_STEEL, segments=8, axis='Y')
    make_box("Faucet_Handle", (cx+0.14, sy+0.16, 1.04), (0.04, 0.10, 0.03), P.METAL_STEEL)
    # Compound microwave at the N third of the counter
    my = cy0 + 0.85
    make_box("Microwave_Body", (cx, my, 1.10), (0.48, 0.44, 0.30), (0.30, 0.30, 0.32, 1.0))
    make_box("Microwave_Door", (cx+0.10, my-0.23, 1.10), (0.30, 0.02, 0.26), (0.18, 0.18, 0.20, 1.0))
    make_box("Microwave_Window", (cx+0.08, my-0.24, 1.10), (0.20, 0.01, 0.18), (0.10, 0.14, 0.12, 0.7))
    make_box("Microwave_Panel", (cx-0.16, my-0.23, 1.10), (0.10, 0.02, 0.24), (0.14, 0.14, 0.16, 1.0))
    make_box("Microwave_Handle", (cx+0.24, my-0.23, 1.10), (0.02, 0.04, 0.22), P.METAL_STEEL)
    # Drip coffee station (make_coffee_pots was imported/unused)
    make_coffee_pots("Coffee", (cx, cy0+0.10, 0.94), pots=2)
    # Upper cabinets above the counter
    make_box("UpperCab_Body", (cx+0.02, cy0, 1.95), (0.44, 2.40, 0.60), (0.36, 0.28, 0.18, 1.0))
    for ui, uy in enumerate([cy0-0.60, cy0+0.60]):
        make_box(f"UpperCab_Door_{ui}", (cx-0.20, uy, 1.95), (0.02, 1.10, 0.56), (0.42, 0.32, 0.20, 1.0))
        make_box(f"UpperCab_Pull_{ui}", (cx-0.22, uy+0.45, 1.80), (0.02, 0.03, 0.12), P.METAL_BLACK)

def build_fridge():
    # Fridge in the NW corner
    fx, fy = -ROOM_W/2.0 + 0.42, ROOM_D - 0.55
    make_box("Fridge_Body", (fx, fy, 0.95), (0.72, 0.72, 1.90), (0.82, 0.82, 0.80, 1.0))
    make_box("Fridge_DoorUpper", (fx-0.35, fy, 1.35), (0.03, 0.66, 1.02), (0.86, 0.86, 0.84, 1.0))
    make_box("Fridge_DoorLower", (fx-0.35, fy, 0.55), (0.03, 0.66, 0.66), (0.86, 0.86, 0.84, 1.0))
    make_box("Fridge_HandleU", (fx-0.38, fy+0.28, 1.35), (0.03, 0.04, 0.40), P.METAL_STEEL)
    make_box("Fridge_HandleL", (fx-0.38, fy+0.28, 0.55), (0.03, 0.04, 0.30), P.METAL_STEEL)
    make_box("Fridge_Kick", (fx, fy, 0.05), (0.68, 0.68, 0.10), (0.30, 0.30, 0.30, 1.0))
    # Magnets / a note on the door
    make_box("Fridge_Note", (fx-0.37, fy-0.10, 1.45), (0.005, 0.16, 0.20), P.PAPER)

def build_board():
    make_box("BulletinBoard", (0.0, ROOM_D-0.06, 1.50), (1.60, 0.04, 0.90), (0.62, 0.42, 0.28, 1.0))
    for pi in range(8):
        px = -0.60 + (pi%4)*0.40; pz = 1.20 + (pi//4)*0.50
        make_box(f"Notice_{pi}", (px, ROOM_D-0.04, pz), (0.20, 0.005, 0.16), P.PAPER)

def build_break_decor():
    # Wall clock on the N wall beside the bulletin board
    make_wall_clock("Clock", (1.70, ROOM_D-0.05, 2.10), frozen_hour=12, frozen_min=30)
    # Wall calendar on the E wall (make_calendar was imported/unused)
    make_calendar("Calendar", (ROOM_W/2.0-0.06, 1.20, 1.60))
    # Corner floor plant (make_floor_plant was imported/unused)
    make_floor_plant("Plant", (ROOM_W/2.0-0.55, 0.60, 0.0))
    # Swing-lid trash bin by the counter
    tx, ty = -ROOM_W/2.0+0.70, 0.70
    make_cyl("Trash_Body", (tx, ty, 0.34), 0.20, 0.68, (0.34, 0.36, 0.34, 1.0), segments=12, axis='Z')
    make_cyl("Trash_Rim", (tx, ty, 0.68), 0.21, 0.03, (0.24, 0.26, 0.24, 1.0), segments=12, axis='Z')
    make_box("Trash_SwingLid", (tx, ty, 0.71), (0.30, 0.30, 0.04), (0.28, 0.30, 0.28, 1.0))

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))
    make_hvac_vent("HVAC", (-ROOM_W/4.0, ROOM_D-0.5, CEIL), width=0.80, depth=0.40)

def main():
    clear_scene()
    build_shell()
    build_table()
    build_vending()
    build_kitchenette()
    build_fridge()
    build_board()
    build_break_decor()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/centro_break_room.glb"))
    print(f"\n[build_centro_break_room] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
