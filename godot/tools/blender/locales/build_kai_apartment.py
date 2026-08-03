"""kai_apartment — vol5-7 locale (auto-generated placement script)."""
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

ROOM_W = 4.5; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall":(0.86,0.86,0.86,1.0),"baseboard":(0.32,0.32,0.32,1.0)}
COL_FLOOR = (0.62,0.52,0.42,1.0); COL_SEAM = (0.32,0.22,0.14,1.0); COL_WOOD = (0.42,0.30,0.18,1.0)
COL_ACCENT = (0.18,0.42,0.74,1.0)

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
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})

def build_bed():
    # Re-arranged (2026-07-15): a FLOOR futon mattress — no frame, lowest
    # possible silhouette — long axis E–W in the SW near the door. The
    # deliberate opposite of Finn's raised platform, so the ex-clone pair
    # now reads as two different people (was a byte-for-byte clone).
    bx, by = -0.65, 1.25
    make_box("Futon_Mat", (bx, by, 0.09), (1.86, 1.16, 0.14), (0.30, 0.34, 0.40, 1.0))
    make_box("Futon_Fold", (bx, by - 0.38, 0.16), (1.86, 0.46, 0.10), COL_ACCENT)
    make_box("Futon_Blanket", (bx, by + 0.10, 0.17), (1.70, 0.86, 0.06), COL_ACCENT)
    make_box("Futon_Pillow_L", (bx - 0.5, by + 0.40, 0.16), (0.54, 0.30, 0.10), P.PAPER)
    make_box("Futon_Pillow_R", (bx + 0.5, by + 0.40, 0.16), (0.54, 0.30, 0.10), P.PAPER)

def build_desk_lamp():
    dx, dy = +ROOM_W/4.0, 1.5
    make_box("Desk_Top", (dx, dy, 0.74), (1.00, 0.60, 0.04), COL_WOOD)
    for li in range(4):
        lx, ly = dx+(-0.44,+0.44,-0.44,+0.44)[li], dy+(-0.24,-0.24,+0.24,+0.24)[li]
        make_box(f"Desk_Leg_{li}", (lx, ly, 0.36), (0.04, 0.04, 0.72), COL_WOOD)
    make_box("Lamp_Base", (dx-0.30, dy+0.20, 0.78), (0.10, 0.10, 0.04), P.METAL_BLACK)
    make_cyl("Lamp_Arm", (dx-0.30, dy+0.20, 0.96), 0.012, 0.30, P.METAL_BLACK)
    make_cyl("Lamp_Head", (dx-0.20, dy+0.20, 1.16), 0.06, 0.08, COL_ACCENT)
    for bi in range(3):
        make_box(f"Desk_Book_{bi}", (dx+0.20+bi*0.12, dy, 0.80), (0.10, 0.22, 0.20), P.SNACK_TINTS[bi%len(P.SNACK_TINTS)])

def build_posters():
    for pi in range(3):
        px = -ROOM_W/2.0+0.05; py = 1.0 + pi*1.5
        make_faded_poster(f"Poster_W_{pi}", (px, py, 1.50))

def build_dressing():
    bx, by = -0.65, 1.25
    # low milk-crate "nightstand" for the floor futon, against the W wall
    make_box("Nightstand", (bx-1.15, by, 0.18), (0.36, 0.36, 0.36), COL_WOOD)
    make_box("Clock", (bx-1.15, by, 0.40), (0.15, 0.10, 0.10), P.METAL_BLACK)
    # Dresser against the east wall
    make_box("Dresser", (ROOM_W/2.0-0.30, ROOM_D-1.3, 0.45), (0.44, 1.0, 0.90), COL_WOOD)
    for di in range(3):
        make_box(f"Dresser_Drawer_{di}", (ROOM_W/2.0-0.52, ROOM_D-1.3, 0.24+di*0.24), (0.02, 0.86, 0.16), (0.34, 0.24, 0.16, 1.0))
    # Desk chair
    dx, dy = +ROOM_W/4.0, 1.5
    make_box("Chair_Seat", (dx, dy-0.55, 0.46), (0.42, 0.42, 0.05), COL_WOOD)
    make_box("Chair_Back", (dx, dy-0.74, 0.74), (0.42, 0.05, 0.46), COL_ACCENT)
    for i, (lx, ly) in enumerate([(-0.16, -0.16), (0.16, -0.16), (-0.16, 0.16), (0.16, 0.16)]):
        make_box(f"Chair_Leg_{i}", (dx+lx, dy-0.55+ly, 0.23), (0.05, 0.05, 0.44), P.METAL_BLACK)
    # Floor plant, NW corner (make_floor_plant was imported/unused)
    make_floor_plant("Plant", (-ROOM_W/2.0+0.5, ROOM_D-0.6, 0.0), palette={"leaf": (0.40, 0.50, 0.38, 1.0), "pot": (0.44, 0.34, 0.24, 1.0)})

def build_win():
    make_window("Window_N", (0.0, ROOM_D-0.02, 1.50), width=1.20, height=1.00)

def build_ceiling_infra():
    # A home: warm dome fixture, no shop tubes
    make_cyl("Ceiling_Dome", (0.0, 2.5, CEIL-0.10), 0.15, 0.14, (0.94, 0.88, 0.70, 1.0), segments=12)
    make_smoke_detector("Smoke", (0.9, 2.5, CEIL))


def build_hero_props():
    """2026-08-03 tail pass: the kitchen table, the wall clock at
    seven oh-eight, the bathroom door."""
    wood = (0.44, 0.32, 0.20, 1.0)
    make_box("Kitchen_Table", (0.6, 3.6, 0.74), (1.00, 0.75, 0.05), wood)
    for lx, ly in ((0.18, 3.28), (1.02, 3.28), (0.18, 3.92), (1.02, 3.92)):
        make_box(f"KT_Leg_{lx:.2f}_{ly:.2f}", (lx, ly, 0.37), (0.05, 0.05, 0.72), wood)
    make_box("KT_Chair_Seat", (0.6, 2.95, 0.44), (0.40, 0.40, 0.05), wood)
    make_box("KT_Chair_Back", (0.6, 2.77, 0.72), (0.40, 0.05, 0.52), wood)
    make_cyl("Water_Glass", (0.75, 3.55, 0.82), 0.035, 0.11, (0.55, 0.62, 0.66, 0.5), segments=8)
    make_wall_clock("Clock_Kitchen", (0.0, 4.95, 2.05), frozen_hour=7, frozen_min=8)
    # Bathroom door, E wall ("He showered.")
    make_box("Bathroom_Door", (2.20, 1.4, 1.03), (0.05, 0.80, 2.05), (0.50, 0.40, 0.28, 1.0))
    make_cyl("Bathroom_Knob", (2.14, 1.10, 1.00), 0.025, 0.03, (0.66, 0.52, 0.24, 1.0), axis='X', segments=8)


def main():
    clear_scene()
    build_shell()
    build_bed()
    build_desk_lamp()
    build_posters()
    build_dressing()
    build_win()
    build_ceiling_infra()
    build_hero_props()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/kai_apartment.glb"))
    print(f"\n[build_kai_apartment] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
