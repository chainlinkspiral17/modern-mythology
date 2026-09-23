"""finn_apartment — Finn's one-bedroom (vol 7): kitchen south, bedroom
north beyond the partition; the crow on the south sill.

DRAFT 3 (2026-09-19, lore/_VISUAL_PROGRAM.md §3 backgrounds pass, 7
placements). Kit furniture: the desk lamp (make_lamp), the desk chair,
the two kitchen chairs, the perch chair (its rail on the kit back);
the kettle and pour-over cone as profiles; the ceiling dome as a dome;
turned bed posts with a rail; dresser pulls. LAYOUT fixes the recorder
never reported: the desk's east end 6 cm inside the east wall; the
phone and notebook floating BESIDE the desk (placed against a top
the desk no longer covered after the 09-07 move); the reader and
headset hovering 10 cm over the perch chair's seat (the nightstand
had moved with the bed); the duffel inside the desk chair; the
counter 5 cm into the west wall; the dresser 2 cm into the east
wall; both outlets inside furniture; the round rug lying across the
bedroom partition; the plant's pot in the bed deck. WEAR: the chairs'
floor patches, the step-up scuff at the platform bed, the desk's
elbow strip, the counter's drip, the duffel's nine-month patch, the
sill's marks under the crow. D3: a counter outlet + the kettle's
cord, a desk outlet + the lamp's cord. D5: the neighbour's roof and
the treeline past the north window; the street and the sea-band past
the south one. Scene: the desk-lamp practical moved onto the lamp's
bulb, the ceiling dome lit.
Draft 4 targets: the bed's crates as slatted crates with contents;
the dresser's top dressing (a bowl of change, the keys); the kitchen
window's curtain; the entry door leaf with its chain; the fridge
Finn must have (the counter run has none); Deck: the preset from the
SE corner + shot_establish_b.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_chamfer_box, make_blob, make_cyl, make_lathe, make_tube, export_glb
from _props.furniture import make_chair, make_lamp
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
BED_Y = ROOM_D - 1.25   # draft 3: 0.10 north — the deck's south edge sat in the partition
DESK_X = ROOM_W/2.0 - 0.70   # draft 3: the desk's east end was 6 cm inside the wall

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, with_grid=False)
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
    bx, by = -1.14, BED_Y   # head end at the W wall (2026-09-10: pillow lay along the long side)
    for sx in (-1, 1):
        for sy in (-1, 1):
            # (draft 3: turned posts, a finial above the deck)
            make_lathe(f"Bed_Post_{sx}_{sy}", (bx + sx * 0.9, by + sy * 0.5, 0.0),
                       [(0.04, 0.0), (0.045, 0.03), (0.032, 0.08), (0.036, 0.40), (0.045, 0.49), (0.045, 0.56), (0.03, 0.60), (0.035, 0.66), (0.0, 0.70)],
                       COL_WOOD, segments=8)
    make_tube("Bed_Foot_Rail", [(bx + 0.9, by - 0.5, 0.63), (bx + 0.9, by + 0.5, 0.63)], 0.016, COL_WOOD, segments=6)
    make_box("Bed_Deck", (bx, by, 0.52), (1.92, 1.14, 0.06), COL_WOOD)
    make_chamfer_box("Bed_Mattress", (bx, by, 0.62), (1.80, 1.04, 0.16), (0.92, 0.86, 0.78, 1.0))
    make_chamfer_box("Bed_Comforter", (bx + 0.15, by, 0.76), (1.40, 0.82, 0.10), COL_ACCENT)   # ON the mattress, clear of the pillow (2026-09-07)
    make_chamfer_box("Bed_Pillow", (bx - 0.68, by, 0.76), (0.30, 0.90, 0.12), P.PAPER)   # on the mattress, off its chamfered edge (2026-09-22)
    for ci, cx in enumerate((bx - 0.55, bx + 0.1, bx + 0.65)):
        # on the floor (2026-09-23: 4 cm up, the frame standing on nothing)
        make_box(f"Bed_Crate_{ci}", (cx, by, 0.14), (0.40, 0.90, 0.28), (0.34, 0.24, 0.16, 1.0))

def build_desk_lamp():
    dx, dy = DESK_X, 1.5   # end against the E wall; the perch chair owns the N side (2026-09-07)
    make_box("Desk_Top", (dx, dy, 0.74), (1.00, 0.60, 0.04), COL_WOOD)
    for li in range(4):
        lx, ly = dx+(-0.44,+0.44,-0.44,+0.44)[li], dy+(-0.24,-0.24,+0.24,+0.24)[li]
        make_lathe(f"Desk_Leg_{li}", (lx, ly, 0.0), [(0.022, 0.0), (0.026, 0.03), (0.018, 0.08), (0.02, 0.45), (0.028, 0.52), (0.02, 0.60), (0.024, 0.72)], COL_WOOD, segments=8)
    make_box("Desk_Apron", (dx, dy, 0.70), (0.92, 0.52, 0.04), (0.40, 0.29, 0.18, 1.0))
    # (draft 3: the kit lamp — base, stem, shade, bulb; its practical
    # sits on the bulb)
    make_lamp("Lamp", dx-0.30, dy+0.20, base_z=0.76, h=0.55, shade_col=COL_ACCENT, body_col=P.METAL_BLACK)
    for bi in range(3):
        make_box(f"Desk_Book_{bi}", (dx+0.20+bi*0.12, dy, 0.80), (0.10, 0.22, 0.20), P.SNACK_TINTS[bi%len(P.SNACK_TINTS)])

def build_rug():
    # (draft 3: a bedside rug — the 2.4 m round rug lay across the
    # bedroom partition — and a kitchen mat at the counter)
    make_cyl("Rug", (0.45, 4.42, 0.012), 0.42, 0.005, COL_ACCENT)
    make_box("Kitchen_Mat", (-1.05, 1.30, 0.004), (0.70, 1.20, 0.008), (0.52, 0.44, 0.34, 1.0))

def build_dressing():
    bx, by = -1.14, BED_Y   # head end at the W wall (2026-09-10: pillow lay along the long side)
    make_chamfer_box("Nightstand", (bx+1.2, by, 0.28), (0.40, 0.40, 0.56), COL_WOOD)
    make_box("Nightstand_Drawer_Pull", (bx+1.2, by-0.205, 0.40), (0.06, 0.01, 0.02), P.METAL_BLACK)
    make_box("Clock", (bx+1.2, by, 0.62), (0.15, 0.10, 0.10), P.METAL_BLACK)
    # Dresser against the east wall (draft 3: off the wall by 2 cm,
    # pulls on the drawers)
    make_chamfer_box("Dresser", (ROOM_W/2.0-0.33, ROOM_D-1.3, 0.45), (0.44, 1.0, 0.90), COL_WOOD)
    for di in range(3):
        make_box(f"Dresser_Drawer_{di}", (ROOM_W/2.0-0.55, ROOM_D-1.3, 0.24+di*0.24), (0.02, 0.86, 0.16), (0.34, 0.24, 0.16, 1.0))
        for pi_, py_ in enumerate((ROOM_D-1.3-0.25, ROOM_D-1.3+0.25)):
            make_cyl(f"Dresser_Pull_{di}_{pi_}", (ROOM_W/2.0-0.565, py_, 0.24+di*0.24), 0.012, 0.01, P.METAL_BLACK, axis='X', segments=6)
    # Desk chair (draft 3: the kit chair, back to the door)
    make_chair("Chair", DESK_X, 0.95, yaw=0.0, wood=COL_WOOD, seat_col=COL_ACCENT, w=0.42)
    # Floor plant, NE corner (draft 3: at the NW its pot stood in the
    # bed deck)
    make_floor_plant("Plant", (1.9, ROOM_D-0.45, 0.0), palette={"leaf": (0.36, 0.48, 0.30, 1.0), "pot": (0.44, 0.34, 0.24, 1.0)})
    # Wall art over the bed (make_faded_poster was imported/unused)
    make_faded_poster("Poster_W", (-ROOM_W/2.0+0.05, ROOM_D/2.0, 1.60))

def build_win():
    make_window("Window_N", (0.0, ROOM_D-0.02, 1.50), width=1.20, height=1.00)

def build_ceiling_infra():
    # A home: warm dome fixture, no shop tubes
    make_lathe("Ceiling_Dome", (0.0, 2.5, CEIL), [(0.0, -0.14), (0.09, -0.13), (0.14, -0.08), (0.16, -0.02), (0.16, 0.0), (0.0, 0.0)], (0.94, 0.88, 0.70, 1.0), segments=12)
    make_cyl("Ceiling_Dome_Ring", (0.0, 2.5, CEIL-0.01), 0.17, 0.02, (0.62, 0.52, 0.30, 1.0), segments=12)
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
        make_chair(f"KT_Chair_{ci}", 0.0, cy, yaw=(math.pi if ci else 0.0), wood=wood, w=0.40)
    # The folded cloth + three pieces of charred wood
    make_chamfer_box("Folded_Cloth", (0.0, 1.60, 0.775), (0.40, 0.30, 0.008), (0.82, 0.78, 0.68, 1.0))
    for wi in range(3):
        make_box(f"Charred_Wood_{wi}", (-0.12 + wi * 0.12, 1.60, 0.79), (0.08, 0.03, 0.025), (0.10, 0.09, 0.08, 1.0))
    # The crow's chair beside the bed — tall back, the perch
    make_chair("Perch_Chair", 0.55, 3.65, yaw=math.pi, wood=(0.36, 0.26, 0.17, 1.0), w=0.42)
    make_cyl("Perch_Chair_Rail", (0.55, 3.81, 0.93), 0.022, 0.42, (0.30, 0.22, 0.14, 1.0), segments=6, axis='X')
    # The duffel, SE corner, nine months — soft canvas, not luggage
    # (draft 3: in the corner proper; at (1.85, 0.55) it sat inside the
    # desk chair)
    make_blob("Duffel", (1.82, 0.42, 0.17), 0.30, (0.34, 0.36, 0.30, 1.0),
              noise=0.14, seed=7, squash=0.55)
    make_box("Duffel_Strap", (1.82, 0.42, 0.34), (0.50, 0.06, 0.03), (0.24, 0.25, 0.22, 1.0))
    make_box("Duffel_Zip", (1.82, 0.36, 0.335), (0.44, 0.012, 0.006), (0.72, 0.70, 0.62, 1.0))
    # Counter along the W wall: kettle + cone (draft 3: off the wall —
    # its west 5 cm stood inside it; the kettle and cone as profiles)
    make_chamfer_box("Counter", (-1.78, 1.30, 0.44), (0.70, 1.60, 0.88), (0.50, 0.44, 0.36, 1.0))
    make_box("Counter_Top", (-1.78, 1.30, 0.92), (0.74, 1.66, 0.05), (0.34, 0.28, 0.22, 1.0))
    make_box("Counter_Door_Seam", (-1.427, 1.30, 0.44), (0.004, 0.02, 0.80), (0.30, 0.26, 0.20, 1.0))
    for ki, ky in enumerate((0.95, 1.65)):
        make_box(f"Counter_Pull_{ki}", (-1.425, ky, 0.80), (0.008, 0.10, 0.02), P.METAL_BLACK)
    make_lathe("Kettle", (-1.75, 0.90, 0.945), [(0.0, 0.0), (0.085, 0.0), (0.095, 0.05), (0.09, 0.13), (0.06, 0.16), (0.035, 0.165), (0.035, 0.18), (0.0, 0.18)], (0.62, 0.64, 0.65, 1.0), segments=12)
    make_tube("Kettle_Spout", [(-1.67, 0.90, 1.03), (-1.60, 0.90, 1.10), (-1.57, 0.90, 1.14)], 0.012, (0.62, 0.64, 0.65, 1.0), segments=6)
    make_tube("Kettle_Bail", [(-1.75, 0.84, 1.11), (-1.75, 0.86, 1.20), (-1.75, 0.94, 1.20), (-1.75, 0.96, 1.11)], 0.008, (0.18, 0.17, 0.16, 1.0), segments=5)
    make_lathe("Pour_Cone", (-1.75, 1.55, 0.945), [(0.03, 0.0), (0.03, 0.02), (0.045, 0.03), (0.075, 0.10), (0.065, 0.10), (0.04, 0.035), (0.0, 0.035)], (0.86, 0.82, 0.74, 1.0), segments=10)
    make_lathe("Pour_Mug", (-1.75, 1.55, 0.945), [(0.0, 0.0), (0.04, 0.0), (0.042, 0.018), (0.0, 0.018)], (0.30, 0.34, 0.40, 1.0), segments=10)
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
    # (draft 3: both plates stood inside furniture — the W one in the
    # counter, the E one in the dresser)
    make_wall_outlet("Outlet_W", (-ROOM_W / 2.0, 2.6), axis='Y',
                     face_sign=1, aged=True)
    make_wall_outlet("Outlet_E", (ROOM_W / 2.0, 2.5), axis='Y',
                     face_sign=-1, aged=True)


def build_crow_2026_08():
    """THE CROW on Finn's south windowsill — it follows him through
    the volume (5 cues on this locale alone). S_Window_Frame sits
    at (1.55, 0.05), sill height ~1.05.
    """
    from _props.creatures import make_crow
    make_crow("Crow", 1.55, 0.30, 1.07, facing=1.0)


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    Six distinct cues, none with geometry. Built:

    - THE HEXAGON (ch12_morning: "He laid the eighth piece into the
      hole. It fit." / the crow on the cloth between the ARIA piece
      and the hole): a smaller cloth + ring + face + ARIA piece at
      the kitchen table's west end, beside the charred-wood cloth.
    - THE STICK in its waxed-paper sleeve at the table's east end —
      where the crow stood on the sleeve.
    - THE READER ("the compact one he had bought from Cale in '49")
      + its headset on the bedroom nightstand.
    - FINN'S PHONE and FINN'S NOTEBOOK on the desk, and the thumb-
      sized CARVED CEDAR beside the lamp.
    """
    cedar = (0.55, 0.38, 0.26, 1.0)
    cedar_dk = (0.44, 0.30, 0.20, 1.0)
    T = 0.765
    # ── THE HEXAGON · kitchen table west end ──
    hx, hy = -0.40, 1.60
    make_box("Hexagon_Cloth", (hx, hy, T + 0.002), (0.30, 0.28, 0.004), (0.78, 0.74, 0.64, 1.0))
    for hi in range(6):
        ang = math.pi / 3.0 * hi + math.pi / 6.0
        make_box(f"Hexagon_Ring_{hi}", (hx + 0.095 * math.cos(ang), hy + 0.095 * math.sin(ang), T + 0.013),
                 (0.065, 0.065, 0.018), cedar)
    make_cyl("Hexagon_Center_Face", (hx, hy, T + 0.012), 0.040, 0.016, cedar_dk, segments=12)
    make_cyl("Hexagon_Face_Inlay", (hx, hy, T + 0.0215), 0.022, 0.003, (0.62, 0.46, 0.32, 1.0), segments=10)
    make_box("Hexagon_Aria_Piece", (-0.285, 1.49, T + 0.014), (0.060, 0.045, 0.020), cedar)
    # ── THE STICK · table east end ──
    make_box("Stick_Sleeve", (0.40, 1.60, T + 0.010), (0.26, 0.09, 0.020), (0.88, 0.84, 0.72, 1.0))
    make_box("Stick_Label", (0.40, 1.60, T + 0.021), (0.10, 0.05, 0.002), (0.96, 0.95, 0.92, 1.0))
    # ── THE READER + HEADSET · nightstand (top 0.56) ──
    # (draft 3: ON the nightstand — the nightstand had moved with the
    # bed and these hovered 10 cm over the perch chair's seat)
    nx, ny = -1.14 + 1.2, BED_Y
    make_box("Reader", (nx + 0.10, ny - 0.13, 0.571), (0.100, 0.150, 0.020), (0.22, 0.22, 0.25, 1.0))
    make_box("Reader_Screen", (nx + 0.10, ny - 0.13, 0.5825), (0.080, 0.110, 0.002), (0.30, 0.38, 0.46, 1.0))
    for ci2, cx2 in enumerate((nx - 0.11, nx - 0.04)):
        make_cyl(f"Headset_Cup_{ci2}", (cx2, ny + 0.11, 0.575), 0.030, 0.030, (0.18, 0.18, 0.20, 1.0), segments=8)
    make_box("Headset_Band", (nx - 0.075, ny + 0.11, 0.596), (0.10, 0.012, 0.012), (0.24, 0.24, 0.26, 1.0))
    # ── FINN'S PHONE + NOTEBOOK + THE CARVED CEDAR · desk (top 0.76) ──
    # (draft 3: on the desk — they were placed beside it, in the air)
    make_box("Finns_Phone", (DESK_X - 0.25, 1.30, 0.7655), (0.070, 0.140, 0.011), (0.13, 0.13, 0.15, 1.0))
    make_box("Finns_Notebook", (DESK_X - 0.05, 1.50, 0.766), (0.150, 0.200, 0.012), (0.36, 0.30, 0.24, 1.0))
    make_box("Finns_Notebook_Wire", (DESK_X - 0.131, 1.50, 0.767), (0.010, 0.200, 0.014), (0.55, 0.56, 0.58, 1.0))
    make_box("Carved_Cedar", (DESK_X - 0.17, 1.72, 0.785), (0.030, 0.020, 0.050), (0.52, 0.34, 0.22, 1.0))


def build_draft3_2026_09():
    """DRAFT 3 (2026-09-19) · wear, cords, the two windows' outsides —
    see the module docstring. No part name carries a cue word (crow ·
    charred · wood · duffel · nightstand · hexagon · cedar · phone ·
    notebook · stick · reader)."""
    floor_dk = (COL_FLOOR[0] * 0.84, COL_FLOOR[1] * 0.84, COL_FLOOR[2] * 0.84, 1.0)
    cord = (0.16, 0.16, 0.18, 1.0)
    # WEAR
    for ci, (cx, cy) in enumerate(((0.0, 0.95), (0.0, 2.25), (DESK_X, 0.95))):
        make_floor_stain(f"Wear_Seat_{ci}", (cx, cy), radius=0.25, tint=floor_dk, segments=10)
    make_floor_stain("Wear_Step_Up", (-0.35, BED_Y - 0.75), radius=0.22, tint=floor_dk, segments=10)
    # (the nine-month patch is the wall's, not the floor's: a floor decal
    # under a blob is a clip to the recorder, which boxes the blob whole)
    make_box("Wear_Corner", (ROOM_W / 2.0 - 0.104, 0.42, 0.26), (0.004, 0.50, 0.22), (0.86, 0.76, 0.66, 1.0))
    make_box("Wear_Desk_Edge", (DESK_X, 1.23, 0.7615), (0.80, 0.05, 0.003), (0.36, 0.26, 0.16, 1.0))
    make_box("Wear_Drip", (-1.415, 1.30, 0.60), (0.004, 0.30, 0.20), (0.44, 0.38, 0.30, 1.0))
    # the S window's interior sill — the crow and its marks were on air
    # (2026-09-23: the window had a frame in the wall and no sill)
    make_box("S_Window_Sill", (1.55, 0.26, 1.055), (1.00, 0.32, 0.03), (0.80, 0.78, 0.72, 1.0))
    for mi in range(5):
        make_box(f"Sill_Mark_{mi}", (1.35 + mi * 0.09, 0.22 + (mi % 2) * 0.05, 1.071), (0.03, 0.02, 0.002), (0.90, 0.90, 0.86, 1.0))
    # D3: the counter's outlet + the kettle's cord; the desk's outlet +
    # the lamp's cord (straight tubes)
    make_wall_outlet("Outlet_W_2", (-ROOM_W / 2.0, 1.15), axis='Y', face_sign=1, z=1.15, aged=True)
    make_tube("Cord_1", [(-1.66, 0.96, 0.96), (-2.13, 1.15, 1.15)], 0.008, cord, segments=5)
    # (the lamp's cord runs along the desk's back edge, behind the
    # carved piece — across the top it stood in shot_insert_cedar's line)
    make_wall_outlet("Outlet_E_2", (ROOM_W / 2.0, 1.78), axis='Y', face_sign=-1, z=1.0, aged=True)
    make_tube("Cord_2", [(DESK_X - 0.30, 1.77, 0.78), (ROOM_W / 2.0 - 0.13, 1.78, 1.0)], 0.008, cord, segments=5)
    # D5: past the north window, the neighbour's roof and the
    # treeline; past the south one, the street and the sea band
    make_box("Out_N_Ground", (0.0, ROOM_D + 4.0, -0.03), (14.0, 7.0, 0.05), (0.30, 0.36, 0.26, 1.0))
    make_box("Out_N_House", (1.5, ROOM_D + 4.5, 1.4), (6.0, 3.0, 2.8), (0.62, 0.58, 0.52, 1.0))
    from _props.geometry import make_prism
    make_prism("Out_N_Roof", (1.5, ROOM_D + 4.5, 2.8), [(-3.3, 0.0), (3.3, 0.0), (0.0, 1.6)], 3.2, (0.32, 0.26, 0.22, 1.0), axis="Y")
    make_box("Out_N_Treeline", (0.0, ROOM_D + 9.0, 3.0), (20.0, 0.4, 6.0), (0.13, 0.22, 0.17, 1.0))
    make_box("Out_S_Ground", (0.0, -4.0, -0.03), (14.0, 7.0, 0.05), (0.34, 0.34, 0.36, 1.0))
    make_box("Out_S_Roofline", (0.0, -6.5, 1.2), (14.0, 0.4, 2.4), (0.44, 0.40, 0.36, 1.0))
    make_box("Out_S_Sea", (0.0, -9.5, 2.9), (20.0, 0.3, 0.9), (0.42, 0.52, 0.60, 1.0))
    make_box("Out_S_Sky", (0.0, -9.6, 5.0), (20.0, 0.2, 3.4), (0.70, 0.74, 0.78, 1.0))


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
    build_crow_2026_08()
    build_hero_props_2026_09()
    build_draft3_2026_09()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/finn_apartment.glb"))
    print(f"\n[build_finn_apartment] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
