"""finn_apartment — vol5-7 locale (auto-generated placement script)."""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_chamfer_box, make_blob, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture
from _props.detail import (make_traffic_wear, make_floor_stain,
                           make_wall_tint_band, make_threshold,
                           make_wall_outlet, make_light_switch)

ROOM_W = 4.5; ROOM_D = 5.0; CEIL = 2.6
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
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})

def build_bed():
    # Re-arranged (2026-07-15): a RAISED platform bed on posts, long axis
    # E–W, set toward the N wall with visible under-bed storage crates —
    # a tall silhouette, deliberately NOT the shared W-wall twin so it no
    # longer reads as Kai's room (was a byte-for-byte clone).
    bx, by = -0.5, ROOM_D - 1.35
    for sx in (-1, 1):
        for sy in (-1, 1):
            make_box(f"Bed_Post_{sx}_{sy}", (bx + sx * 0.9, by + sy * 0.5, 0.25),
                     (0.08, 0.08, 0.50), COL_WOOD)
    make_box("Bed_Deck", (bx, by, 0.52), (1.92, 1.14, 0.06), COL_WOOD)
    make_chamfer_box("Bed_Mattress", (bx, by, 0.62), (1.80, 1.04, 0.16), (0.92, 0.86, 0.78, 1.0))
    make_chamfer_box("Bed_Comforter", (bx, by - 0.04, 0.72), (1.82, 1.02, 0.10), COL_ACCENT)
    make_chamfer_box("Bed_Pillow", (bx, by + 0.40, 0.74), (1.40, 0.30, 0.12), P.PAPER)
    for ci, cx in enumerate((bx - 0.55, bx + 0.1, bx + 0.65)):
        make_box(f"Bed_Crate_{ci}", (cx, by, 0.18), (0.40, 0.90, 0.28), (0.34, 0.24, 0.16, 1.0))

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

def build_rug():
    make_cyl("Rug", (0.0, ROOM_D/2.0, 0.012), 1.20, 0.005, COL_ACCENT)

def build_dressing():
    bx, by = -0.5, ROOM_D - 1.35
    make_chamfer_box("Nightstand", (bx+1.2, by, 0.28), (0.40, 0.40, 0.56), COL_WOOD)
    make_box("Clock", (bx+1.2, by, 0.62), (0.15, 0.10, 0.10), P.METAL_BLACK)
    # Dresser against the east wall
    make_chamfer_box("Dresser", (ROOM_W/2.0-0.30, ROOM_D-1.3, 0.45), (0.44, 1.0, 0.90), COL_WOOD)
    for di in range(3):
        make_box(f"Dresser_Drawer_{di}", (ROOM_W/2.0-0.52, ROOM_D-1.3, 0.24+di*0.24), (0.02, 0.86, 0.16), (0.34, 0.24, 0.16, 1.0))
    # Desk chair
    dx, dy = +ROOM_W/4.0, 1.5
    make_box("Chair_Seat", (dx, dy-0.55, 0.46), (0.42, 0.42, 0.05), COL_WOOD)
    make_box("Chair_Back", (dx, dy-0.74, 0.74), (0.42, 0.05, 0.46), COL_ACCENT)
    for i, (lx, ly) in enumerate([(-0.16, -0.16), (0.16, -0.16), (-0.16, 0.16), (0.16, 0.16)]):
        make_box(f"Chair_Leg_{i}", (dx+lx, dy-0.55+ly, 0.23), (0.05, 0.05, 0.44), P.METAL_BLACK)
    # Floor plant, NW corner (make_floor_plant was imported/unused)
    make_floor_plant("Plant", (-ROOM_W/2.0+0.5, ROOM_D-0.6, 0.0), palette={"leaf": (0.36, 0.48, 0.30, 1.0), "pot": (0.44, 0.34, 0.24, 1.0)})
    # Wall art over the bed (make_faded_poster was imported/unused)
    make_faded_poster("Poster_W", (-ROOM_W/2.0+0.05, ROOM_D/2.0, 1.60))

def build_win():
    make_window("Window_N", (0.0, ROOM_D-0.02, 1.50), width=1.20, height=1.00)

def build_ceiling_infra():
    # A home: warm dome fixture, no shop tubes
    make_cyl("Ceiling_Dome", (0.0, 2.5, CEIL-0.10), 0.15, 0.14, (0.94, 0.88, 0.70, 1.0), segments=12)
    make_smoke_detector("Smoke", (0.9, 2.5, CEIL))


def build_hero_props():
    """2026-08-03 tail pass: the kitchen table the charred wood is
    laid out on, the crow's perch-chair beside the bed, the
    nine-month duffel, the kettle + counter + cone, the SOUTH
    kitchen window (Cape Perpetua's direction), the bedroom
    partition of the one-bedroom."""
    wood = (0.44, 0.32, 0.20, 1.0)
    # Kitchen table + two facing chairs
    make_chamfer_box("Kitchen_Table", (0.0, 1.60, 0.74), (1.10, 0.80, 0.05), wood)
    for lx, ly in ((-0.48, 1.28), (0.48, 1.28), (-0.48, 1.92), (0.48, 1.92)):
        make_box(f"KT_Leg_{lx:+.2f}_{ly:.2f}", (lx, ly, 0.37), (0.05, 0.05, 0.72), wood)
    for ci, cy in enumerate((0.95, 2.25)):
        make_box(f"KT_Chair_{ci}_Seat", (0.0, cy, 0.44), (0.40, 0.40, 0.05), wood)
        make_box(f"KT_Chair_{ci}_Back", (0.0, cy + (0.18 if ci else -0.18), 0.72), (0.40, 0.05, 0.52), wood)
    # The folded cloth + three pieces of charred wood
    make_chamfer_box("Folded_Cloth", (0.0, 1.60, 0.775), (0.40, 0.30, 0.008), (0.82, 0.78, 0.68, 1.0))
    for wi in range(3):
        make_box(f"Charred_Wood_{wi}", (-0.12 + wi * 0.12, 1.60, 0.79), (0.08, 0.03, 0.025), (0.10, 0.09, 0.08, 1.0))
    # The crow's chair beside the bed — tall back, the perch
    make_box("Perch_Chair_Seat", (0.55, 3.65, 0.45), (0.42, 0.42, 0.05), (0.36, 0.26, 0.17, 1.0))
    make_box("Perch_Chair_Back", (0.55, 3.86, 0.70), (0.42, 0.05, 0.52), (0.36, 0.26, 0.17, 1.0))
    make_cyl("Perch_Chair_Rail", (0.55, 3.86, 0.97), 0.022, 0.42, (0.30, 0.22, 0.14, 1.0), segments=6, axis='X')
    # The duffel, SE corner, nine months — soft canvas, not luggage
    make_blob("Duffel", (1.85, 0.55, 0.18), 0.34, (0.34, 0.36, 0.30, 1.0),
              noise=0.14, seed=7, squash=0.55)
    make_box("Duffel_Strap", (1.85, 0.55, 0.37), (0.55, 0.06, 0.03), (0.24, 0.25, 0.22, 1.0))
    # Counter along the W wall: kettle + cone
    make_chamfer_box("Counter", (-1.85, 1.30, 0.44), (0.70, 1.60, 0.88), (0.50, 0.44, 0.36, 1.0))
    make_box("Counter_Top", (-1.85, 1.30, 0.92), (0.74, 1.66, 0.05), (0.34, 0.28, 0.22, 1.0))
    make_cyl("Kettle", (-1.80, 0.90, 1.03), 0.09, 0.16, (0.62, 0.64, 0.65, 1.0), segments=10)
    make_cyl("Pour_Cone", (-1.80, 1.55, 1.02), 0.06, 0.09, (0.86, 0.82, 0.74, 1.0), segments=8)
    # The SOUTH kitchen window (toward Cape Perpetua) — S wall east
    # segment, above the entry level
    make_box("S_Window_Frame", (1.55, 0.05, 1.55), (0.90, 0.08, 1.00), (0.34, 0.28, 0.22, 1.0))
    make_box("S_Window_Glass", (1.55, 0.03, 1.55), (0.76, 0.05, 0.86), (0.45, 0.52, 0.60, 0.5))
    # Bedroom partition (the crow flies low through this doorway)
    make_box("Bedroom_Part", (-0.55, 3.05, 1.3), (1.9, 0.14, 2.6), (0.62, 0.55, 0.46, 1.0))
    make_box("Bedroom_Part_Header", (0.75, 3.05, 2.35), (0.7, 0.14, 0.5), (0.62, 0.55, 0.46, 1.0))



def build_detail_pass_2026_08():
    """D2 surface breakup + first D3 (generic template pass per
    lore/_SET_DETAIL_PLAYBOOK.md): the entry walk-line, a work-zone
    stain, ceiling gather on the long walls, a threshold, and the
    switch/outlet pair every room earns. Per-locale wear
    PERSONALITY (whose feet, whose spills) is the next pass."""
    wear = (COL_FLOOR[0] * 0.88, COL_FLOOR[1] * 0.88, COL_FLOOR[2] * 0.88, 1.0)
    stain = (COL_FLOOR[0] * 0.82, COL_FLOOR[1] * 0.82, COL_FLOOR[2] * 0.82, 1.0)
    pw = PAL_WALL["wall"]
    band = (pw[0] * 0.90, pw[1] * 0.90, pw[2] * 0.88, 1.0)
    make_traffic_wear("Wear_Entry", [(0.0, 0.6), (0.0, ROOM_D * 0.55)],
                      width=0.75, tint=wear)
    make_floor_stain("Stain_WorkZone", (ROOM_W * 0.22, ROOM_D * 0.62),
                     radius=0.24, tint=stain)
    make_wall_tint_band("Band_W", (-ROOM_W / 2.0 + 0.105, ROOM_D / 2.0, 0.0),
                        length=ROOM_D - 0.4, axis='Y', band_z=CEIL - 0.16, tint=band)
    make_wall_tint_band("Band_E", (ROOM_W / 2.0 - 0.105, ROOM_D / 2.0, 0.0),
                        length=ROOM_D - 0.4, axis='Y', band_z=CEIL - 0.16, tint=band)
    make_threshold("Threshold_Entry", (0.0, 0.10), width=1.9, axis='X')
    make_light_switch("Switch_Entry", (1.15, 0.0), axis='X', face_sign=1, aged=True)
    make_wall_outlet("Outlet_W", (-ROOM_W / 2.0, ROOM_D * 0.35), axis='Y',
                     face_sign=1, aged=True)
    make_wall_outlet("Outlet_E", (ROOM_W / 2.0, ROOM_D * 0.70), axis='Y',
                     face_sign=-1, aged=True)


def main():
    clear_scene()
    build_shell()
    build_bed()
    build_desk_lamp()
    build_rug()
    build_dressing()
    build_win()
    build_ceiling_infra()
    build_hero_props()
    build_detail_pass_2026_08()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/finn_apartment.glb"))
    print(f"\n[build_finn_apartment] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
