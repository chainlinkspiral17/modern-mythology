"""Maya's Bedroom — vol6 — vol6 placement script."""
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

ROOM_W = 4.0; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall": (0.96, 0.86, 0.78, 1.0), "baseboard": (0.62, 0.46, 0.30, 1.0)}
COL_FLOOR = (0.74, 0.58, 0.38, 1.0); COL_SEAM = (0.42, 0.30, 0.18, 1.0); COL_WOOD = (0.46, 0.34, 0.22, 1.0)
COL_ACCENT = (0.86, 0.62, 0.62, 1.0)

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

def build_bed():
    bx, by = -ROOM_W/4.0, ROOM_D/2.0
    make_box("Bed_Frame", (bx, by, 0.20), (1.20, 1.80, 0.20), (0.42, 0.30, 0.20, 1.0))
    make_box("Bed_Mattress", (bx, by, 0.40), (1.10, 1.70, 0.16), (0.92, 0.86, 0.78, 1.0))
    make_box("Bed_Pillow", (bx, by+0.62, 0.50), (1.00, 0.36, 0.10), P.PAPER)
    make_box("Bed_Throw", (bx, by-0.50, 0.50), (1.00, 0.40, 0.06), COL_ACCENT)
    make_box("Bed_Headboard", (bx, by+0.88, 0.62), (1.20, 0.08, 0.60), (0.40, 0.28, 0.18, 1.0))
    make_box("Bed_Comforter", (bx, by-0.10, 0.50), (1.14, 1.02, 0.10), (0.74, 0.52, 0.62, 1.0))
    # A couple of plush toys against the pillow
    make_cyl("Plush_A", (bx-0.30, by+0.60, 0.62), 0.10, 0.20, (0.86, 0.62, 0.42, 1.0), segments=10)
    make_cyl("Plush_B", (bx+0.28, by+0.58, 0.60), 0.09, 0.18, (0.62, 0.52, 0.78, 1.0), segments=10)

def build_desk_lamp():
    dx, dy = +ROOM_W/4.0, 1.5
    make_box("Desk_Top", (dx, dy, 0.74), (1.00, 0.60, 0.04), COL_WOOD)
    for li in range(4):
        lx, ly = dx+(-0.44,+0.44,-0.44,+0.44)[li], dy+(-0.24,-0.24,+0.24,+0.24)[li]
        make_box(f"Desk_Leg_{li}", (lx, ly, 0.36), (0.04, 0.04, 0.72), COL_WOOD)
    make_box("Lamp_Base", (dx-0.30, dy+0.20, 0.78), (0.10, 0.10, 0.04), P.METAL_BLACK)
    make_cyl("Lamp_Arm", (dx-0.30, dy+0.20, 0.96), 0.012, 0.30, P.METAL_BLACK)
    make_cyl("Lamp_Head", (dx-0.20, dy+0.20, 1.16), 0.06, 0.08, COL_ACCENT)
    # Books on desk
    for bi in range(3):
        make_box(f"Desk_Book_{bi}", (dx+0.20+bi*0.12, dy, 0.80), (0.10, 0.22, 0.20), P.SNACK_TINTS[bi%len(P.SNACK_TINTS)])

def build_posters():
    for pi in range(3):
        px = -ROOM_W/2.0+0.05
        py = 1.0 + pi*1.5
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
    make_hvac_vent("HVAC", (-ROOM_W/4.0, ROOM_D-0.5, CEIL), width=0.80, depth=0.40)

def build_dressing():
    """Teen-girl room dressing: a vanity dresser with mirror + drawers,
    a nightstand + clock, a floor plant (make_floor_plant was imported
    but unused), and warm fairy lights strung along the north wall."""
    bx, by = -ROOM_W/4.0, ROOM_D/2.0
    # Nightstand + alarm clock beside the bed
    nsx = bx + 0.95
    make_box("Nightstand", (nsx, by+0.7, 0.28), (0.40, 0.40, 0.56), COL_WOOD)
    make_box("Clock", (nsx, by+0.7, 0.62), (0.15, 0.10, 0.10), P.METAL_BLACK)
    # Vanity dresser against the east wall: body, three drawers, a mirror
    vx = ROOM_W/2.0 - 0.30
    make_box("Vanity_Body", (vx, ROOM_D-1.2, 0.42), (0.50, 0.90, 0.84), COL_WOOD)
    for di in range(3):
        make_box(f"Vanity_Drawer_{di}", (vx-0.26, ROOM_D-1.2, 0.24+di*0.24), (0.02, 0.80, 0.18), (0.34, 0.24, 0.16, 1.0))
    make_box("Vanity_Mirror", (vx-0.02, ROOM_D-1.2, 1.30), (0.03, 0.66, 0.80), (0.78, 0.84, 0.90, 0.6))
    make_box("Vanity_MirrorFrame", (vx, ROOM_D-1.2, 1.30), (0.05, 0.72, 0.86), COL_ACCENT)
    # Perfume/trinket bottles on the vanity top
    for ti, tc in enumerate([(0.86, 0.62, 0.72, 1.0), (0.62, 0.78, 0.86, 1.0), (0.92, 0.82, 0.42, 1.0)]):
        make_cyl(f"Trinket_{ti}", (vx-0.1, ROOM_D-1.5+ti*0.2, 0.90), 0.03, 0.10, tc, segments=8)
    # Floor plant, SE corner
    make_floor_plant("Plant", (ROOM_W/2.0-0.5, 0.7, 0.0), palette={"leaf": (0.40, 0.52, 0.36, 1.0), "pot": (0.72, 0.48, 0.56, 1.0)})
    # Fairy lights along the north wall
    for i in range(8):
        make_cyl(f"Fairy_{i}", (-1.4+i*0.4, ROOM_D-0.08, 2.05), 0.028, 0.028, (1.0, 0.84, 0.6, 1.0), segments=6)

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
        "../../../assets/3d/locales/maya_bedroom.glb"))
    print(f"\n[build_maya_bedroom] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
