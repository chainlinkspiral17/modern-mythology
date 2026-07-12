"""Cosmic Comics — back-issue floor — vol6 placement script."""
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

ROOM_W = 10.0; ROOM_D = 8.0; CEIL = 2.8
PAL_WALL = {"wall": (0.42, 0.32, 0.46, 1.0), "baseboard": (0.18, 0.12, 0.20, 1.0)}
COL_FLOOR = (0.32, 0.28, 0.32, 1.0); COL_SEAM = (0.18, 0.16, 0.20, 1.0); COL_WOOD = (0.42, 0.30, 0.52, 1.0)
COL_ACCENT = (0.78, 0.42, 0.86, 1.0)

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

def build_bins():
    for ji in range(2):
        ay = ROOM_D * (0.35 + ji * 0.30)
        make_box(f"Bin_{ji}_Base", (0.0, ay, 0.30), (5.0, 0.50, 0.60), (0.30, 0.22, 0.14, 1.0))
        for di in range(11):
            make_box(f"Bin_{ji}_Div_{di}", (-2.5+di*0.5, ay, 0.66), (0.02, 0.50, 0.12), P.METAL_STEEL)
        for ci in range(15):
            cx_pos = -2.4 + (ci%10)*0.45
            cy_off = -0.20 + (ci//10)*0.40
            tint = P.SNACK_TINTS[(ji+ci)%len(P.SNACK_TINTS)]
            make_box(f"Bin_{ji}_Comic_{ci}", (cx_pos, ay+cy_off, 0.70), (0.40, 0.04, 0.20), tint)

def build_register_counter():
    top_z = make_counter("Register", (ROOM_W/4.0, ROOM_D-1.5, 0.0), length=2.40, depth=1.00, height=0.95,
                         palette={"formica": (0.42, 0.30, 0.52, 1.0), "top": (0.18, 0.12, 0.20, 1.0), "kick": (0.18, 0.12, 0.20, 1.0)})
    make_register("RegisterMachine", (ROOM_W/4.0, ROOM_D-1.5-0.30, top_z))

def build_rack():
    # Iconic revolving comic spinner instead of a flat wall slab: a
    # weighted base, a steel pole, and three tiers of radiating wire
    # pockets, each holding a colour-coded comic.
    rx, ry = -ROOM_W/2.0 + 1.1, ROOM_D - 1.3
    make_cyl("Spinner_Base", (rx, ry, 0.06), 0.46, 0.12, P.METAL_BLACK, segments=16)
    make_cyl("Spinner_Pole", (rx, ry, 0.98), 0.045, 1.84, P.METAL_STEEL, segments=8)
    for tier, tz in enumerate([0.66, 1.16, 1.66]):
        for pk in range(6):
            ang = pk * (2.0 * math.pi / 6.0) + tier * 0.4
            ox, oy = math.cos(ang) * 0.34, math.sin(ang) * 0.34
            make_box(f"Spinner_Wire_{tier}_{pk}", (rx+ox*0.6, ry+oy*0.6, tz), (0.02, 0.02, 0.30), P.METAL_STEEL)
            tint = P.SNACK_TINTS[(tier + pk) % len(P.SNACK_TINTS)]
            make_box(f"Spinner_Comic_{tier}_{pk}", (rx+ox, ry+oy, tz+0.02), (0.22, 0.03, 0.30), tint)

def build_posters():
    for pi in range(3):
        py = 1.0 + pi*2.0
        make_faded_poster(f"Poster_W_{pi}", (-ROOM_W/2.0+0.05, py, 1.70), palette={"body": COL_ACCENT})

def build_drop():
    pass  # ceiling already added in build_shell

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))
    make_hvac_vent("HVAC", (-ROOM_W/4.0, ROOM_D-0.5, CEIL), width=0.80, depth=0.40)

def build_dressing():
    """Comic-shop flavour: a glass display case of graded slabs beside
    the register, an action-figure pegwall on the east wall, a cardboard
    standee, and a stool behind the counter."""
    # Glass display case beside the register
    dx, dy = ROOM_W/4.0 - 1.7, ROOM_D - 1.5
    make_box("Case_Body", (dx, dy, 0.45), (1.20, 0.60, 0.90), COL_WOOD)
    make_box("Case_Glass", (dx, dy, 1.06), (1.16, 0.56, 0.32), (0.70, 0.80, 0.92, 0.35))
    for gi in range(5):
        make_box(f"Case_Slab_{gi}", (dx-0.48+gi*0.24, dy, 0.96), (0.16, 0.30, 0.02),
                 P.SNACK_TINTS[gi % len(P.SNACK_TINTS)])
    # Action-figure pegwall, east wall (blister cards + figure bodies)
    for r in range(3):
        for c in range(4):
            px = ROOM_W/2.0 - 0.10; py = 2.0 + c * 0.55; pz = 1.2 + r * 0.5
            make_box(f"Peg_{r}_{c}_Card", (px, py, pz), (0.02, 0.22, 0.30), (0.86, 0.78, 0.42, 1.0))
            make_cyl(f"Peg_{r}_{c}_Fig", (px-0.08, py, pz), 0.05, 0.20,
                     P.SNACK_TINTS[(r + c) % len(P.SNACK_TINTS)], axis='X', segments=8)
    # Cardboard standee near the front SE corner
    make_box("Standee_Board", (ROOM_W/2.0 - 1.3, 1.0, 0.98), (0.55, 0.05, 1.92), COL_ACCENT)
    make_box("Standee_Foot", (ROOM_W/2.0 - 1.3, 1.15, 0.03), (0.55, 0.30, 0.03), (0.30, 0.22, 0.14, 1.0))
    # Stool behind the register
    make_cyl("Stool_Seat", (ROOM_W/4.0 - 0.7, ROOM_D - 2.6, 0.56), 0.18, 0.06, P.METAL_BLACK, segments=12)
    make_cyl("Stool_Post", (ROOM_W/4.0 - 0.7, ROOM_D - 2.6, 0.28), 0.03, 0.54, P.METAL_STEEL, segments=8)

def main():
    clear_scene()
    build_shell()
    build_bins()
    build_register_counter()
    build_rack()
    build_posters()
    build_drop()
    build_ceiling_infra()
    build_dressing()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/cosmic_comics_interior.glb"))
    print(f"\n[build_cosmic_comics_interior] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
