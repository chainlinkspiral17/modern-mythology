"""lena_apartment — vol5-7 locale (auto-generated placement script)."""
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

ROOM_W = 5.0; ROOM_D = 5.0; CEIL = 2.6
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
    # Re-arranged (2026-07-15): a proper QUEEN (1.5 wide) with a footboard,
    # centered against the N wall with the headboard N — a bigger, adult
    # footprint that no longer matches the shared twin at -ROOM_W/4.
    bx, by = 0.0, ROOM_D - 1.15
    make_box("Bed_Frame", (bx, by, 0.20), (1.50, 1.94, 0.22), (0.42, 0.30, 0.20, 1.0))
    make_box("Bed_Mattress", (bx, by, 0.42), (1.40, 1.84, 0.16), (0.92, 0.86, 0.78, 1.0))
    # Tall headboard (N end) + a low footboard (S end)
    make_box("Bed_Headboard", (bx, by+1.00, 0.66), (1.54, 0.08, 0.66), (0.40, 0.28, 0.18, 1.0))
    make_box("Bed_Footboard", (bx, by-0.98, 0.42), (1.54, 0.08, 0.34), (0.40, 0.28, 0.18, 1.0))
    make_box("Bed_Pillow_L", (bx-0.36, by+0.68, 0.54), (0.62, 0.36, 0.12), (0.98, 0.94, 0.90, 1.0))
    make_box("Bed_Pillow_R", (bx+0.36, by+0.68, 0.54), (0.62, 0.36, 0.12), (0.98, 0.94, 0.90, 1.0))
    make_box("Bed_Duvet", (bx, by-0.24, 0.52), (1.44, 1.18, 0.10), (0.72, 0.46, 0.52, 1.0))

def build_desk_lamp():
    dx, dy = +ROOM_W/4.0, 1.5
    make_box("Desk_Top", (dx, dy, 0.74), (1.00, 0.60, 0.04), COL_WOOD)
    for i, (lx, ly) in enumerate([(-0.44, -0.26), (0.44, -0.26), (-0.44, 0.26), (0.44, 0.26)]):
        make_box(f"Desk_Leg_{i}", (dx+lx, dy+ly, 0.37), (0.06, 0.06, 0.72), COL_WOOD)
    # Gooseneck lamp: base disc, column, head (the head is the lit fixture)
    make_cyl("Lamp_Base", (dx-0.30, dy+0.18, 0.78), 0.08, 0.03, P.METAL_BLACK)
    make_cyl("Lamp_Col", (dx-0.30, dy+0.18, 0.98), 0.02, 0.40, P.METAL_BLACK)
    make_cyl("Lamp_Head", (dx-0.20, dy+0.20, 1.16), 0.06, 0.10, COL_ACCENT)
    # Laptop (base + raised screen), a stacked book pile, and a mug
    make_box("Laptop_Base", (dx+0.12, dy, 0.77), (0.34, 0.24, 0.02), P.METAL_BLACK)
    make_box("Laptop_Screen", (dx+0.12, dy+0.11, 0.90), (0.34, 0.02, 0.24), (0.10, 0.12, 0.16, 1.0))
    for bi, (bz, bc) in enumerate([(0.79, (0.62, 0.24, 0.24, 1.0)), (0.83, (0.24, 0.42, 0.52, 1.0)), (0.87, (0.72, 0.62, 0.30, 1.0))]):
        make_box(f"Desk_Book_{bi}", (dx+0.36, dy-0.16, bz), (0.20, 0.28, 0.035), bc)
    make_cyl("Desk_Mug", (dx-0.02, dy-0.18, 0.82), 0.04, 0.09, COL_ACCENT, segments=12)
    # Desk chair (seat, back, four legs)
    make_box("Chair_Seat", (dx, dy-0.55, 0.46), (0.42, 0.42, 0.05), COL_WOOD)
    make_box("Chair_Back", (dx, dy-0.74, 0.72), (0.42, 0.05, 0.44), COL_WOOD)
    for i, (lx, ly) in enumerate([(-0.16, -0.16), (0.16, -0.16), (-0.16, 0.16), (0.16, 0.16)]):
        make_box(f"Chair_Leg_{i}", (dx+lx, dy-0.55+ly, 0.23), (0.05, 0.05, 0.44), COL_WOOD)

def build_posters():
    for pi in range(3):
        px = -ROOM_W/2.0+0.05; py = 1.0 + pi*1.5
        make_faded_poster(f"Poster_W_{pi}", (px, py, 1.50))

def build_rug():
    make_cyl("Rug", (0.0, ROOM_D/2.0, 0.012), 1.20, 0.005, COL_ACCENT)

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def build_dressing():
    """Lived-in apartment dressing: nightstand + clock beside the bed,
    a filled bookshelf, a floor plant, and warm string lights along
    the north wall — so the room reads as someone's home, not a cell."""
    bx, by = 0.0, ROOM_D - 1.15
    COL_TERRA = (0.66, 0.40, 0.26, 1.0)
    BOOK_COLS = [(0.62, 0.24, 0.24, 1.0), (0.24, 0.42, 0.52, 1.0),
                 (0.72, 0.62, 0.30, 1.0), (0.30, 0.46, 0.34, 1.0)]
    # Nightstand beside the bed (toward room centre) + alarm clock
    nsx = bx + 0.95
    make_box("Nightstand", (nsx, by+0.7, 0.30), (0.42, 0.42, 0.60), COL_WOOD)
    make_box("Nightstand_Drawer", (nsx, by+0.7-0.22, 0.42), (0.36, 0.02, 0.16), (0.34, 0.24, 0.16, 1.0))
    make_box("Clock", (nsx, by+0.7, 0.66), (0.16, 0.10, 0.10), P.METAL_BLACK)
    # Bookshelf against the east wall, packed with colour-banded books
    shx = ROOM_W/2.0 - 0.20
    make_box("Shelf_Body", (shx, ROOM_D-1.2, 0.90), (0.30, 1.00, 1.80), COL_WOOD)
    for r in range(4):
        for c in range(6):
            make_box(f"Shelf_Book_{r}_{c}", (shx-0.03, ROOM_D-1.7+c*0.16, 0.35+r*0.42),
                     (0.22, 0.12, 0.26), BOOK_COLS[(r+c) % 4])
    # Floor plant, NW corner
    make_floor_plant("Plant", (-ROOM_W/2.0+0.5, ROOM_D-0.6, 0.0),
                     palette={"leaf": (0.36, 0.48, 0.30, 1.0), "pot": COL_TERRA})
    # Warm string lights strung along the north wall
    for i in range(9):
        make_cyl(f"Fairy_{i}", (-1.6+i*0.4, ROOM_D-0.08, 2.10), 0.03, 0.03, (1.0, 0.82, 0.5, 1.0), segments=6)

def main():
    clear_scene()
    build_shell()
    build_bed()
    build_desk_lamp()
    build_posters()
    build_rug()
    build_ceiling_infra()
    build_dressing()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/lena_apartment.glb"))
    print(f"\n[build_lena_apartment] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
