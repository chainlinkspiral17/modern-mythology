"""el_rancho_taqueria — vol5-7 locale (auto-generated placement script)."""
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

ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 2.8
PAL_WALL = {"wall":(0.96,0.84,0.62,1.0),"baseboard":(0.62,0.42,0.22,1.0)}
COL_FLOOR = (0.62,0.46,0.30,1.0); COL_SEAM = (0.32,0.22,0.14,1.0); COL_WOOD = (0.42,0.30,0.18,1.0)
COL_ACCENT = (0.78,0.42,0.22,1.0)

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

def build_register_counter():
    top_z = make_counter("Register", (ROOM_W/4.0, ROOM_D-1.5, 0.0), length=2.40, depth=1.00, height=0.95,
                         palette={"formica": COL_WOOD, "top": (0.18, 0.12, 0.20, 1.0), "kick": (0.18, 0.12, 0.20, 1.0)})
    make_register("RegisterMachine", (ROOM_W/4.0, ROOM_D-1.5-0.30, top_z))
    # Chip warmer on the counter — metal case, warm lamp, tortilla chips.
    cx, cy = ROOM_W/4.0-0.85, ROOM_D-1.5
    make_box("ChipWarmer_Body", (cx, cy, top_z+0.22), (0.46,0.46,0.40), P.METAL_STEEL)
    make_box("ChipWarmer_Glass", (cx-0.24, cy, top_z+0.24), (0.02,0.42,0.34), P.GLASS_WARM)
    make_box("ChipWarmer_Lamp", (cx, cy, top_z+0.42), (0.44,0.44,0.03), (1.0,0.78,0.32,1.0))
    for i in range(3):
        make_box(f"Chips_{i}", (cx-0.12+i*0.12, cy, top_z+0.10), (0.08,0.32,0.14), (0.92,0.78,0.42,1.0))

def build_menu_board():
    mx, my, mz = ROOM_W/4.0, ROOM_D-0.06, 2.05
    make_box("MenuBoard_Frame", (mx, my+0.01, mz), (2.34, 0.02, 1.02), P.METAL_STEEL)
    make_box("MenuBoard", (mx, my, mz), (2.24, 0.04, 0.92), (0.14,0.13,0.12,1.0))
    row_cols = [(0.98,0.86,0.44,1.0),(0.92,0.62,0.28,1.0),(0.86,0.44,0.30,1.0),(0.72,0.82,0.60,1.0)]
    for col_i in range(2):
        for row in range(4):
            make_box(f"Menu_{col_i}_{row}", (mx-0.55+col_i*1.10, my-0.03, mz+0.28-row*0.18),
                     (0.80, 0.005, 0.05), row_cols[row])

def build_salsa_station():
    sx, sy = -ROOM_W/2.0+0.8, ROOM_D-1.2
    make_box("Salsa_Table", (sx, sy, 0.45), (1.10, 0.62, 0.06), COL_WOOD)
    for k,(ox,oy) in enumerate([(-0.46,-0.24),(0.46,-0.24),(-0.46,0.24),(0.46,0.24)]):
        make_box(f"Salsa_Leg_{k}", (sx+ox, sy+oy, 0.24), (0.05,0.05,0.42), COL_WOOD)
    salsa_cols = [(0.72,0.20,0.16,1.0),(0.36,0.52,0.24,1.0),(0.86,0.62,0.24,1.0)]
    for i in range(3):
        px = sx-0.34+i*0.34
        make_box(f"SalsaPan_{i}", (px, sy-0.05, 0.51), (0.26,0.32,0.10), P.METAL_STEEL)
        make_box(f"Salsa_{i}", (px, sy-0.05, 0.56), (0.22,0.28,0.03), salsa_cols[i])
    for i,col in enumerate([(0.86,0.22,0.16,1.0),(0.86,0.72,0.20,1.0),(0.36,0.46,0.24,1.0)]):
        make_cyl(f"Bottle_{i}", (sx+0.40, sy-0.20+i*0.18, 0.58), 0.03, 0.16, col)
    make_box("Napkins", (sx-0.40, sy+0.22, 0.54), (0.16,0.10,0.12), P.METAL_STEEL)

def _make_table(prefix, cx, cy):
    make_cyl(f"{prefix}_Top", (cx, cy, 0.74), 0.42, 0.05, COL_WOOD, segments=12)
    make_cyl(f"{prefix}_Column", (cx, cy, 0.38), 0.06, 0.68, P.METAL_BLACK)
    make_cyl(f"{prefix}_Base", (cx, cy, 0.03), 0.30, 0.05, P.METAL_BLACK, segments=12)
    for ci, ox in enumerate((-0.66, 0.66)):
        chx, chy = cx+ox, cy
        make_box(f"{prefix}_Ch{ci}_Seat", (chx, chy, 0.45), (0.38,0.38,0.05), COL_ACCENT)
        bx = chx + (-0.17 if ox < 0 else 0.17)
        make_box(f"{prefix}_Ch{ci}_Back", (bx, chy, 0.68), (0.04,0.38,0.44), COL_ACCENT)
        for k,(lx,ly) in enumerate([(-0.15,-0.15),(0.15,-0.15),(-0.15,0.15),(0.15,0.15)]):
            make_box(f"{prefix}_Ch{ci}_Leg_{k}", (chx+lx, chy+ly, 0.22), (0.04,0.04,0.42), P.METAL_BLACK)

def build_tables():
    for ti,(tx,ty) in enumerate([(-1.7,2.0),(1.7,2.0),(0.0,3.5)]):
        _make_table(f"Table{ti}", tx, ty)

def build_neon_sign():
    sx = ROOM_W/2.0-0.06; sy = ROOM_D/2.0; sz = 2.0
    pink=(0.96,0.24,0.62,1.0); cyan=(0.30,0.82,0.92,1.0); amber=(1.0,0.72,0.28,1.0)
    make_box("Neon_Board", (sx+0.03, sy, sz), (0.03, 1.80, 0.92), (0.10,0.08,0.10,1.0))
    make_cyl("Neon_Top", (sx, sy, sz+0.38), 0.02, 1.70, pink, axis='Y')
    make_cyl("Neon_Bot", (sx, sy, sz-0.38), 0.02, 1.70, pink, axis='Y')
    make_cyl("Neon_L", (sx, sy-0.85, sz), 0.02, 0.76, pink, axis='Z')
    make_cyl("Neon_R", (sx, sy+0.85, sz), 0.02, 0.76, pink, axis='Z')
    for i in range(5):
        make_cyl(f"Neon_TxtA_{i}", (sx, sy-0.60+i*0.30, sz+0.12), 0.015, 0.22, cyan, axis='Z')
    for i in range(6):
        make_cyl(f"Neon_TxtB_{i}", (sx, sy-0.70+i*0.28, sz-0.14), 0.015, 0.18, amber, axis='Z')

def build_string_lights():
    for strand in range(2):
        sy = ROOM_D*(0.32+strand*0.34)
        make_box(f"Festoon_Wire_{strand}", (0.0, sy, CEIL-0.12), (ROOM_W-0.6, 0.01, 0.01), P.METAL_BLACK)
        span = ROOM_W-0.8
        for b in range(9):
            bx = -span/2.0 + b*(span/8.0)
            make_cyl(f"Festoon_Bulb_{strand}_{b}", (bx, sy, CEIL-0.20), 0.035, 0.08, (1.0,0.82,0.5,1.0))

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def main():
    clear_scene()
    build_shell()
    build_register_counter()
    build_menu_board()
    build_salsa_station()
    build_tables()
    build_neon_sign()
    build_string_lights()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/el_rancho_taqueria.glb"))
    print(f"\n[build_el_rancho_taqueria] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
