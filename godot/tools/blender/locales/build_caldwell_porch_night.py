"""caldwell_porch_night — vol5-7 locale (auto-generated placement script)."""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture

ROOM_W = 6.0; ROOM_D = 4.0; CEIL = 2.8
PAL_WALL = {"wall":(0.62,0.46,0.32,1.0),"baseboard":(0.32,0.22,0.14,1.0)}
COL_FLOOR = (0.42,0.30,0.20,1.0); COL_SEAM = (0.22,0.14,0.10,1.0); COL_WOOD = (0.42,0.30,0.18,1.0)
COL_ACCENT = (0.96,0.62,0.32,1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)

def build_railing():
    make_box("Rail_Top", (0.0, 0.10, 1.00), (ROOM_W-1.0, 0.06, 0.06), COL_WOOD)
    for vi in range(10):
        vx = -(ROOM_W-1.0)/2.0+vi*0.6
        make_box(f"Rail_Bal_{vi}", (vx, 0.10, 0.50), (0.04, 0.04, 0.90), COL_WOOD)

def _make_rocker(prefix, cx, cy):
    """Compound rocking chair — seat faces south (toward the railing),
    back at +Y with spindles, armrests, four legs, two curved runners."""
    make_box(f"{prefix}_Seat", (cx, cy, 0.46), (0.50, 0.46, 0.05), COL_WOOD)
    make_box(f"{prefix}_Back", (cx, cy+0.22, 0.76), (0.48, 0.04, 0.56), COL_WOOD)
    for si in range(4):
        sx = cx - 0.18 + si*0.12
        make_box(f"{prefix}_Spindle_{si}", (sx, cy+0.22, 0.74), (0.02, 0.03, 0.50), COL_ACCENT)
    for ai, ax in enumerate((cx-0.26, cx+0.26)):
        make_box(f"{prefix}_Arm_{ai}", (ax, cy-0.02, 0.64), (0.05, 0.44, 0.04), COL_WOOD)
        make_box(f"{prefix}_ArmPost_{ai}", (ax, cy-0.20, 0.55), (0.04, 0.04, 0.18), COL_WOOD)
    for k,(ox,oy) in enumerate([(-0.22,-0.20),(0.22,-0.20),(-0.22,0.20),(0.22,0.20)]):
        make_box(f"{prefix}_Leg_{k}", (cx+ox, cy+oy, 0.23), (0.05,0.05,0.46), COL_WOOD)
    for ri, rx in enumerate((cx-0.22, cx+0.22)):
        make_box(f"{prefix}_Runner_{ri}", (rx, cy, 0.03), (0.05, 0.72, 0.06), COL_WOOD)

def build_chairs():
    for ci, cx in enumerate([-1.5, +1.5]):
        _make_rocker(f"Rocker_{ci}", cx, ROOM_D/2.0)

def build_door():
    make_box("ScreenDoor_Frame", (0.0, 0.0, 1.05), (1.00, 0.04, 2.10), COL_WOOD)
    make_box("ScreenDoor_Screen", (0.0, 0.03, 1.05), (0.80, 0.01, 1.90), (0.28,0.30,0.26,1.0))

def build_porchlamp():
    # Wall-mounted carriage lamp: bracket, glass housing, warm bulb.
    make_box("PorchLamp_Bracket", (-1.5, 0.16, CEIL-0.66), (0.05, 0.20, 0.05), P.METAL_BLACK)
    make_box("PorchLamp_Housing", (-1.5, 0.30, CEIL-0.66), (0.18, 0.18, 0.30), P.METAL_BLACK)
    make_box("PorchLamp_Glass", (-1.5, 0.30, CEIL-0.66), (0.13, 0.13, 0.24), P.GLASS_WARM)
    make_cyl("PorchLamp_Bulb", (-1.5, 0.30, CEIL-0.66), 0.05, 0.12, COL_ACCENT)

def build_dressing():
    # Side table between the rockers, with a mug and a folded paper.
    tx, ty = 0.0, ROOM_D/2.0
    make_box("SideTable_Top", (tx, ty, 0.52), (0.44, 0.44, 0.04), COL_WOOD)
    for k,(ox,oy) in enumerate([(-0.18,-0.18),(0.18,-0.18),(-0.18,0.18),(0.18,0.18)]):
        make_box(f"SideTable_Leg_{k}", (tx+ox, ty+oy, 0.26), (0.04,0.04,0.50), COL_WOOD)
    make_cyl("Mug_Body", (tx-0.08, ty, 0.60), 0.05, 0.10, (0.86,0.82,0.74,1.0))
    make_cyl("Mug_Handle", (tx-0.14, ty, 0.60), 0.02, 0.05, (0.86,0.82,0.74,1.0), axis='Y', segments=6)
    make_box("Paper", (tx+0.10, ty, 0.55), (0.20, 0.14, 0.03), P.NEWSPRINT)
    # Doormat at the door.
    make_box("Doormat", (0.0, 0.55, 0.02), (0.90, 0.55, 0.03), P.RUBBER_MAT)
    make_box("Doormat_Trim", (0.0, 0.55, 0.03), (0.78, 0.44, 0.02), (0.36,0.30,0.22,1.0))
    # Cordwood stack in the NW corner (logs along X, pyramid rows).
    lx0, ly0 = -ROOM_W/2.0+0.45, ROOM_D-0.7
    for r, n in enumerate((4,3,2)):
        for c in range(n):
            col = (0.52,0.38,0.26,1.0) if (r+c)%2 else (0.42,0.30,0.20,1.0)
            make_cyl(f"Log_{r}_{c}", (lx0, ly0 - 0.16*(n-1)/2.0 + c*0.16, 0.12+r*0.15),
                     0.07, 0.52, col, axis='X', segments=8)
    # Potted plant in the NE corner (wire the imported helper).
    make_floor_plant("PorchPlant", (ROOM_W/2.0-0.5, ROOM_D-0.6, 0.0),
                     palette={"leaf":(0.34,0.46,0.30,1.0),"pot":(0.56,0.36,0.24,1.0)})
    # Hanging planter over the railing on the east side.
    hx, hy = 1.5, 0.62
    make_cyl("HangWire", (hx, hy, CEIL-0.35), 0.005, 0.68, P.METAL_BLACK)
    make_cyl("HangPot", (hx, hy, CEIL-0.80), 0.14, 0.16, (0.56,0.36,0.24,1.0))
    for i,(dx,dy) in enumerate([(0.14,0.0),(0.07,0.121),(-0.07,0.121),(-0.14,0.0),(-0.07,-0.121),(0.07,-0.121)]):
        make_cyl(f"HangLeaf_{i}", (hx+dx, hy+dy, CEIL-0.94), 0.03, 0.16, (0.36,0.48,0.32,1.0))

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def main():
    clear_scene()
    build_shell()
    build_railing()
    build_chairs()
    build_door()
    build_porchlamp()
    build_dressing()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/caldwell_porch_night.glb"))
    print(f"\n[build_caldwell_porch_night] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
