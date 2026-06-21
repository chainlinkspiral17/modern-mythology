"""board_lords_interior — vol5-7 locale (auto-generated placement script)."""
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

ROOM_W = 9.0; ROOM_D = 7.0; CEIL = 2.8
PAL_WALL = {"wall":(0.42,0.32,0.46,1.0),"baseboard":(0.18,0.12,0.20,1.0)}
COL_FLOOR = (0.32,0.28,0.32,1.0); COL_SEAM = (0.18,0.16,0.20,1.0); COL_WOOD = (0.42,0.30,0.52,1.0)
COL_ACCENT = (0.78,0.42,0.86,1.0)

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

def build_bins():
    for ji in range(2):
        ay = ROOM_D * (0.35 + ji * 0.30)
        make_box(f"Bin_{ji}_Base", (0.0, ay, 0.30), (5.0, 0.50, 0.60), (0.30, 0.22, 0.14, 1.0))

def build_register_counter():
    top_z = make_counter("Register", (ROOM_W/4.0, ROOM_D-1.5, 0.0), length=2.40, depth=1.00, height=0.95,
                         palette={"formica": COL_WOOD, "top": (0.18, 0.12, 0.20, 1.0), "kick": (0.18, 0.12, 0.20, 1.0)})
    make_register("RegisterMachine", (ROOM_W/4.0, ROOM_D-1.5-0.30, top_z))

def build_posters():
    for pi in range(3):
        px = -ROOM_W/2.0+0.05; py = 1.0 + pi*1.5
        make_faded_poster(f"Poster_W_{pi}", (px, py, 1.50))

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def main():
    clear_scene()
    build_shell()
    build_bins()
    build_register_counter()
    build_posters()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/board_lords_interior.glb"))
    print(f"\n[build_board_lords_interior] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
