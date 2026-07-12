"""Miller Back Porch — vol6 placement script."""
import os, sys, math
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

ROOM_W = 6.0; ROOM_D = 4.0; CEIL = 2.8
PAL_WALL = {"wall": (0.62, 0.46, 0.32, 1.0), "baseboard": (0.32, 0.22, 0.14, 1.0)}
COL_FLOOR = (0.42, 0.30, 0.20, 1.0); COL_SEAM = (0.22, 0.14, 0.10, 1.0); COL_WOOD = (0.42, 0.30, 0.18, 1.0)
COL_ACCENT = (0.96, 0.62, 0.32, 1.0)

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

def build_railing():
    # Front railing
    make_box("Rail_Top", (0.0, 0.10, 1.00), (ROOM_W-1.0, 0.06, 0.06), COL_WOOD)
    for vi in range(10):
        vx = -(ROOM_W-1.0)/2.0+vi*0.6
        make_box(f"Rail_Bal_{vi}", (vx, 0.10, 0.50), (0.04, 0.04, 0.90), COL_WOOD)

def build_chairs():
    for ci, cx in enumerate([-1.5, +1.5]):
        cy = ROOM_D/2.0
        make_box(f"Rocker_{ci}_Seat", (cx, cy, 0.46), (0.50, 0.46, 0.04), COL_WOOD)
        make_box(f"Rocker_{ci}_Back", (cx, cy+0.20, 0.78), (0.50, 0.04, 0.66), COL_WOOD)
        # Back spindles — silhouette variety instead of a flat slab
        for si in range(4):
            sx = cx - 0.18 + si * 0.12
            make_cyl(f"Rocker_{ci}_Spindle_{si}", (sx, cy+0.20, 0.72), 0.015, 0.44, COL_WOOD, segments=6)
        # Armrests
        for ai, ax in enumerate([cx-0.24, cx+0.24]):
            make_box(f"Rocker_{ci}_Arm_{ai}", (ax, cy, 0.62), (0.04, 0.44, 0.04), COL_WOOD)
            make_cyl(f"Rocker_{ci}_ArmPost_{ai}", (ax, cy-0.18, 0.54), 0.02, 0.16, COL_WOOD, segments=6)
        for ri, ry in enumerate([cy-0.20, cy+0.20]):
            make_cyl(f"Rocker_{ci}_Rocker_{ri}", (cx, ry, 0.10), 0.04, 0.50, COL_WOOD, axis='X', segments=8)

def build_door():
    make_box("ScreenDoor_Frame", (0.0, 0.0, 1.05), (1.00, 0.04, 2.10), COL_WOOD)
    make_box("ScreenDoor_Mesh", (0.0, 0.0, 1.05), (0.96, 0.005, 2.00), (0.42, 0.42, 0.40, 0.45))

def build_porchlamp():
    make_cyl("PorchLamp_Cord", (-1.5, 0.30, CEIL-0.20), 0.005, 0.40, P.METAL_BLACK)
    make_cyl("PorchLamp_Bulb", (-1.5, 0.30, CEIL-0.66), 0.08, 0.16, COL_ACCENT)

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))
    make_hvac_vent("HVAC", (-ROOM_W/4.0, ROOM_D-0.5, CEIL), width=0.80, depth=0.40)

def build_dressing():
    """Set dressing so the porch reads lived-in, not a bare deck: a
    side table between the rockers (mug + folded paper on top), a
    doormat, a potted plant, a firewood stack, and a hanging planter.
    All compound silhouettes, not lone boxes."""
    cy = ROOM_D/2.0
    COL_TERRA = (0.66, 0.40, 0.26, 1.0); COL_LEAF = (0.36, 0.48, 0.30, 1.0)
    # Side table — round top on a turned column + three splayed legs
    make_cyl("SideTbl_Top", (0.0, cy, 0.44), 0.28, 0.04, COL_WOOD, segments=16)
    make_cyl("SideTbl_Col", (0.0, cy, 0.24), 0.05, 0.40, COL_WOOD, segments=8)
    for li in range(3):
        ang = li * (2.0 * math.pi / 3.0)
        make_box(f"SideTbl_Leg_{li}", (math.cos(ang) * 0.18, cy + math.sin(ang) * 0.18, 0.10),
                 (0.05, 0.05, 0.20), COL_WOOD)
    # Coffee mug (body + handle) and a folded newspaper on the table
    make_cyl("Mug_Body", (0.10, cy - 0.05, 0.52), 0.045, 0.09, (0.82, 0.36, 0.24, 1.0), segments=12)
    make_cyl("Mug_Handle", (0.16, cy - 0.05, 0.55), 0.02, 0.03, (0.82, 0.36, 0.24, 1.0), axis='X', segments=8)
    make_box("Newspaper", (-0.13, cy + 0.02, 0.475), (0.20, 0.14, 0.02), (0.80, 0.78, 0.72, 1.0))
    # Doormat at the screen door
    make_box("Doormat", (0.0, 0.55, 0.012), (0.90, 0.55, 0.02), (0.34, 0.26, 0.18, 1.0))
    # Potted plant, NE corner
    make_floor_plant("Plant", (ROOM_W/2.0 - 0.55, ROOM_D - 0.6, 0.0),
                     palette={"leaf": COL_LEAF, "pot": COL_TERRA})
    # Firewood stack against the east wall — cordwood rounds on end
    for row in range(3):
        for col in range(4):
            make_cyl(f"Firewood_{row}_{col}",
                     (ROOM_W/2.0 - 0.38, 0.7 + col * 0.16, 0.12 + row * 0.15),
                     0.072, 0.5, (0.40, 0.28, 0.18, 1.0), axis='X', segments=8)
    # Hanging planter near the SW corner ceiling
    make_cyl("Hanger_Cord", (1.5, cy - 0.5, CEIL - 0.35), 0.004, 0.70, P.METAL_BLACK)
    make_cyl("Hanger_Pot", (1.5, cy - 0.5, CEIL - 0.78), 0.14, 0.14, COL_TERRA, segments=12)
    for li in range(6):
        ang = li * (2.0 * math.pi / 6.0)
        make_cyl(f"Hanger_Leaf_{li}", (1.5 + math.cos(ang) * 0.17, cy - 0.5 + math.sin(ang) * 0.17, CEIL - 0.66),
                 0.03, 0.12, COL_LEAF)

def main():
    clear_scene()
    build_shell()
    build_railing()
    build_chairs()
    build_door()
    build_porchlamp()
    build_ceiling_infra()
    build_dressing()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/miller_back_porch.glb"))
    print(f"\n[build_miller_back_porch] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
