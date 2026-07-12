"""sam_bedroom — vol5-7 locale (auto-generated placement script)."""
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

ROOM_W = 4.0; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall":(0.96,0.86,0.78,1.0),"baseboard":(0.62,0.46,0.30,1.0)}
COL_FLOOR = (0.74,0.58,0.38,1.0); COL_SEAM = (0.42,0.30,0.18,1.0); COL_WOOD = (0.46,0.34,0.22,1.0)
COL_ACCENT = (0.86,0.62,0.62,1.0)

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

def build_bed():
    bx, by = -ROOM_W/4.0, ROOM_D/2.0
    make_box("Bed_Frame", (bx, by, 0.20), (1.20, 1.80, 0.20), (0.42, 0.30, 0.20, 1.0))
    make_box("Bed_Mattress", (bx, by, 0.40), (1.10, 1.70, 0.16), (0.92, 0.86, 0.78, 1.0))
    # Headboard, pillow, and a rumpled comforter (a kid's bed, made lazily)
    make_box("Bed_Headboard", (bx, by+0.88, 0.62), (1.20, 0.08, 0.60), (0.40, 0.28, 0.18, 1.0))
    make_box("Bed_Pillow", (bx, by+0.58, 0.52), (0.96, 0.36, 0.12), (0.94, 0.92, 0.86, 1.0))
    make_box("Bed_Comforter", (bx, by-0.24, 0.50), (1.14, 1.14, 0.12), (0.30, 0.46, 0.62, 1.0))

def build_desk_lamp():
    dx, dy = +ROOM_W/4.0, 1.5
    make_box("Desk_Top", (dx, dy, 0.74), (1.00, 0.60, 0.04), COL_WOOD)
    for i, (lx, ly) in enumerate([(-0.44, -0.26), (0.44, -0.26), (-0.44, 0.26), (0.44, 0.26)]):
        make_box(f"Desk_Leg_{i}", (dx+lx, dy+ly, 0.37), (0.06, 0.06, 0.72), COL_WOOD)
    # Clip lamp: base, column, head (the lit fixture)
    make_cyl("Lamp_Base", (dx-0.34, dy+0.18, 0.78), 0.07, 0.03, P.METAL_BLACK)
    make_cyl("Lamp_Col", (dx-0.34, dy+0.18, 0.98), 0.02, 0.40, P.METAL_BLACK)
    make_cyl("Lamp_Head", (dx-0.24, dy+0.20, 1.16), 0.06, 0.10, COL_ACCENT)
    # Chunky CRT monitor + keyboard — a kid's computer corner
    make_box("Monitor_Body", (dx+0.10, dy+0.14, 0.98), (0.42, 0.40, 0.38), (0.24, 0.24, 0.26, 1.0))
    make_box("Monitor_Screen", (dx+0.10, dy-0.06, 0.98), (0.34, 0.02, 0.28), (0.12, 0.16, 0.22, 1.0))
    make_box("Keyboard", (dx+0.10, dy-0.20, 0.77), (0.40, 0.16, 0.03), (0.32, 0.32, 0.34, 1.0))
    # Stubby game console + controller on the desk edge
    make_box("Console", (dx-0.30, dy-0.16, 0.79), (0.26, 0.20, 0.06), P.METAL_BLACK)
    make_box("Controller", (dx+0.02, dy-0.22, 0.77), (0.14, 0.09, 0.03), (0.42, 0.20, 0.46, 1.0))
    # Desk chair
    make_box("Chair_Seat", (dx, dy-0.55, 0.46), (0.42, 0.42, 0.05), COL_WOOD)
    make_box("Chair_Back", (dx, dy-0.74, 0.74), (0.42, 0.05, 0.46), (0.30, 0.46, 0.62, 1.0))
    for i, (lx, ly) in enumerate([(-0.16, -0.16), (0.16, -0.16), (-0.16, 0.16), (0.16, 0.16)]):
        make_box(f"Chair_Leg_{i}", (dx+lx, dy-0.55+ly, 0.23), (0.05, 0.05, 0.44), P.METAL_BLACK)

def build_posters():
    for pi in range(3):
        px = -ROOM_W/2.0+0.05; py = 1.0 + pi*1.5
        make_faded_poster(f"Poster_W_{pi}", (px, py, 1.50))

def build_rug():
    make_cyl("Rug", (0.0, ROOM_D/2.0, 0.012), 1.20, 0.005, COL_ACCENT)

def build_win():
    make_window("Window_N", (0.0, ROOM_D-0.02, 1.50), width=1.20, height=1.00)

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def build_dressing():
    """Teen-boy clutter: a nightstand + clock, a low toy/game shelf, a
    beanbag, a globe, a skateboard against the wall, and a laundry pile
    on the floor. make_floor_plant was imported but never used."""
    bx, by = -ROOM_W/4.0, ROOM_D/2.0
    TINTS = P.SNACK_TINTS
    # Nightstand + alarm clock by the bed
    nsx = bx + 0.95
    make_box("Nightstand", (nsx, by+0.7, 0.28), (0.40, 0.40, 0.56), COL_WOOD)
    make_box("Clock", (nsx, by+0.7, 0.62), (0.16, 0.10, 0.10), P.METAL_BLACK)
    # Low toy/game shelf on the east wall, colour-blocked spines + boxes
    shx = ROOM_W/2.0 - 0.18
    make_box("Shelf_Body", (shx, ROOM_D-1.4, 0.70), (0.28, 1.10, 1.40), COL_WOOD)
    for r in range(3):
        for c in range(6):
            make_box(f"Shelf_Item_{r}_{c}", (shx-0.03, ROOM_D-1.9+c*0.18, 0.35+r*0.42),
                     (0.20, 0.13, 0.26), TINTS[(r+c) % len(TINTS)])
    # Beanbag chair (squashed stack of discs)
    for di in range(3):
        make_cyl(f"Beanbag_{di}", (0.3, 1.1, 0.14+di*0.10), 0.42-di*0.08, 0.12, (0.72, 0.28, 0.30, 1.0), segments=14)
    # Globe on the nightstand
    make_cyl("Globe_Ball", (nsx, by+0.7, 0.74), 0.09, 0.16, (0.30, 0.52, 0.66, 1.0), segments=12)
    make_cyl("Globe_Stand", (nsx, by+0.7, 0.64), 0.02, 0.06, P.METAL_BLACK)
    # Skateboard leaning against the south wall
    make_box("Skateboard", (0.9, 0.15, 0.42), (0.20, 0.06, 0.80), (0.36, 0.22, 0.44, 1.0))
    for wi, wz in enumerate([0.10, 0.74]):
        make_cyl(f"Skate_Wheel_{wi}", (0.9, 0.10, wz), 0.05, 0.10, (0.86, 0.82, 0.30, 1.0), axis='X', segments=8)
    # Laundry pile in the corner
    for li, (lc, lz) in enumerate([((0.42, 0.46, 0.62, 1.0), 0.06), ((0.66, 0.52, 0.34, 1.0), 0.14), ((0.54, 0.30, 0.32, 1.0), 0.20)]):
        make_cyl(f"Laundry_{li}", (-ROOM_W/2.0+0.5, 0.6, lz), 0.24-li*0.04, 0.10, lc, segments=10)

def main():
    clear_scene()
    build_shell()
    build_bed()
    build_desk_lamp()
    build_posters()
    build_rug()
    build_win()
    build_ceiling_infra()
    build_dressing()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/sam_bedroom.glb"))
    print(f"\n[build_sam_bedroom] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
