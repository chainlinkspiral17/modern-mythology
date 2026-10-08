"""Centro Foods — the sales floor — vol 6 (Diego's night shift, inventory).

DRAFT 6 · AT SUPERMARKET SCALE (2026-10-07). The user: "Don't be afraid
to make spaces and floorplans bigger. Backgrounds always felt small and
claustrophobic." Drafts 1-5 put a supermarket — "she covers all twelve
aisles and the produce wet wall and the dairy case and the meat counter
and the back stockroom and the dock and the manager's office and the
break room" — in a 10 x 8 m box with two gondolas, and every pass since
had been shaving fixtures to make it walkable. This draft builds the
floor a Centro Foods on the edge of a New Auburn industrial corridor
actually has: 30 x 22 m under a 5.4 m open-structure ceiling (bar joists,
the main duct, fluorescent strips hung on wires over the lanes).

  · FRONT (south, the storefront): the entrance with its sliding doors
    and mats, the cart corral, two runs of storefront glass onto the lot;
    four checkout lanes with their lane lights (the five on lane 1's belt,
    Diego's backpack in the cubby behind it), the customer service desk.
  · PRODUCE (west front): "the produce wet wall" along the west wall —
    sloped misted racks of greens — and three produce islands, the
    hanging scale over the first; the wet-floor cone at the wet wall.
  · THE AISLES: six 9 m gondolas running front-to-back make Aisles 5-9
    (1.9 m lanes; Aisle Seven, canned vegetables, the centre lane), end
    caps on the south ends, a blade sign over every lane's mouth.
    "Diego parks the hand truck. He starts pulling cases of stewed
    tomatoes off the pallet and onto the lower shelf" — the pallet in
    Aisle Seven against the shelf, Russell's clipboard and Diego's phone
    and the chain-issued scanner on its load, the dented can leaking.
  · THE BACK (north): "the dairy case" — twelve reach-in doors, one
    "propped open with a milk crate because the lock has been sticking
    since July", Russell's thermometer on its inner face; the double flap
    doors to RECEIVING ("the corner from receiving into Aisle Seven") and
    the cardboard bale beside them; the meat counter's service case.
  · THE EAST SIDE: the deli (where Marisol works) and the bakery, the
    frozen bank of glass doors.
  · Outside the glass: the lot, the walk and curb, a parked car, the
    cart corral, a lamp post, the strip across.

Lanes are 1.9 m between gondolas, 1.8 m in the action alley in front of
the end caps, 2-4 m everywhere else; walkway_audit and case_access_audit
are floors, not targets. Draft 7 targets: the reach-in coolers' contents
by the merchandise grammar (still blocks); price-check signs and shelf
talkers; the manager's office window over the front; wear and D3 at the
new scale; aisles 1-4 and 10-12 implied past the frame edges.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path:
    sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import (clear_scene, make_box, make_chamfer_box, make_cyl, make_lathe,
                             make_tube, make_rot_box, make_blob, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings, make_ceiling, make_frame_ring
from _props.store_fixtures import make_counter, make_register, make_credit_card_terminal
from _props.shelving import make_endcap
from _props.food_service import make_coffee_pots, make_donut_display
from _props.coolers_drinks import make_cooler_row
from _props.decor import make_wall_clock, make_calendar
from _props.merch import stock_gondola, merch_section

X0, X1, Y0, Y1 = -15.0, 15.0, 0.0, 22.0       # wall centre lines
XW, XE, YS, YN = -14.9, 14.9, 0.1, 21.9       # wall room faces
CEIL = 5.4
STRIP_Z = 3.9                                 # the fluorescent strips hang here
PAL_WALL = {"wall": (0.86, 0.86, 0.82, 1.0), "baseboard": (0.30, 0.30, 0.30, 1.0)}
COL_FLOOR = (0.80, 0.79, 0.74, 1.0); COL_SEAM = (0.56, 0.56, 0.52, 1.0)
COL_ACCENT = (0.24, 0.52, 0.34, 1.0)          # Centro green
STEEL = (0.62, 0.63, 0.64, 1.0)
DARK = (0.20, 0.20, 0.22, 1.0)
PAPER = (0.94, 0.93, 0.88, 1.0)

GONDOLA_XS = (-3.40, -0.80, 1.80, 4.40, 7.00, 9.60)
G_Y0, G_Y1 = 7.50, 16.50                      # front-to-back runs
G_LEVELS = [0.34 + k * 0.40 for k in range(5)]
LANE_XS = [(a + b) / 2.0 for a, b in zip(GONDOLA_XS, GONDOLA_XS[1:])]   # aisles 5..9
AISLE_7_X = LANE_XS[2]
COOLER_WALL_Y = 21.40                         # the reach-in doors' face
DAIRY_DOORS = [X0 + 2.0 + 0.66 + k * 1.32 for k in range(12)]
PROPPED = 10                                  # the door with the milk crate
CHECK_XS = (3.0, 5.4, 7.8, 10.2)
CHECK_Y = 3.6


# ── the shell ──────────────────────────────────────────────────────
def build_shell():
    make_floor("Floor", (0.0, (Y0 + Y1) / 2.0, 0.0), size_x=X1 - X0 + 0.4, size_y=Y1 - Y0 + 0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for j in range(1, int(Y1 - Y0)):
        make_box(f"Floor_Tile_Seam_{j}", (0.0, Y0 + j, 0.0015), (X1 - X0, 0.015, 0.002), COL_SEAM)
    make_wall("Wall_W", (X0, (Y0 + Y1) / 2.0, 0), length=Y1 - Y0 + 0.4, height=CEIL, axis='Y',
              palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_E", (X1, (Y0 + Y1) / 2.0, 0), length=Y1 - Y0 + 0.4, height=CEIL, axis='Y',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_N", (0.0, Y1, 0), length=X1 - X0 + 0.4, height=CEIL, axis='X', palette=PAL_WALL,
                            baseboard_face_sign=-1, openings=[(5.0, 1.20, 1.80, 2.40)])
    make_wall_with_openings("Wall_S", (0.0, Y0, 0), length=X1 - X0 + 0.4, height=CEIL, axis='X',
                            palette={"wall": (0.24, 0.50, 0.34, 1.0), "baseboard": DARK}, baseboard_face_sign=+1,
                            openings=[(-8.5, 1.90, 9.0, 1.80), (0.0, 1.30, 2.60, 2.60), (8.0, 1.90, 6.0, 1.80)])
    make_ceiling("Ceil", (0.0, (Y0 + Y1) / 2.0, CEIL), size_x=X1 - X0 + 0.4, size_y=Y1 - Y0 + 0.4, with_grid=False,
                 palette={"tile": (0.34, 0.35, 0.36, 1.0)})
    # the open structure: bar joists, the main duct, a sprinkler main
    for k in range(13):
        x = X0 + 1.5 + k * 2.25
        make_box(f"Ceiling_Joist_{k}", (x, (Y0 + Y1) / 2.0, CEIL - 0.20), (0.08, Y1 - Y0, 0.40), (0.28, 0.29, 0.30, 1.0))
    make_cyl("Ceiling_Duct_Main", (0.0, 11.0, CEIL - 0.85), 0.38, X1 - X0 - 1.0, (0.62, 0.64, 0.66, 1.0), axis='X', segments=12)
    for k, x in enumerate((-9.0, -1.0, 7.0)):
        make_cyl(f"Ceiling_Duct_Drop_{k}", (x, 11.0, CEIL - 0.335), 0.20, 0.67, (0.62, 0.64, 0.66, 1.0), segments=10)
    make_cyl("Ceiling_Sprinkler_Main", (0.0, 6.0, CEIL - 0.45), 0.05, X1 - X0 - 1.0, (0.70, 0.18, 0.16, 1.0), axis='X', segments=6)
    # the storefront: glass in the two runs, mullions, the sliding doors
    for nm, cx, w in (("W", -8.5, 9.0), ("E", 8.0, 6.0)):
        make_box(f"Storefront_{nm}_Glass", (cx, Y0, 1.90), (w, 0.012, 1.80), (0.70, 0.80, 0.84, 0.22))
        n = int(w / 1.5)
        for k in range(n + 1):
            make_box(f"Storefront_{nm}_Mullion_{k}", (cx - w / 2.0 + k * w / n, Y0, 1.90), (0.06, 0.12, 1.80), STEEL)
        for k, z in enumerate((1.0, 2.8)):
            make_box(f"Storefront_{nm}_Rail_{k}", (cx, Y0, z), (w, 0.12, 0.06), STEEL)
        make_box(f"Storefront_{nm}_Decal", (cx - w / 4.0, Y0 + 0.012, 2.30), (1.40, 0.003, 0.50), (0.94, 0.86, 0.30, 1.0))
    for sgn, nm in ((-1, "W"), (1, "E")):
        make_box(f"Entrance_Door_{nm}", (sgn * 0.95, Y0 - 0.06, 1.25), (1.0, 0.04, 2.40), (0.70, 0.80, 0.84, 0.30))
        make_box(f"Entrance_Door_{nm}_Frame", (sgn * 0.95, Y0 - 0.06, 2.47), (1.0, 0.06, 0.06), STEEL)
    make_box("Exit_Sign", (0.0, YS + 0.20, 2.95), (0.40, 0.06, 0.20), (0.94, 0.94, 0.90, 1.0))
    make_box("Exit_Sign_Letters", (0.0, YS + 0.168, 2.95), (0.28, 0.004, 0.10), (0.90, 0.16, 0.14, 1.0))
    make_cyl("Exit_Sign_Conduit", (0.0, YS + 0.20, (3.05 + CEIL) / 2.0), 0.008, CEIL - 3.05, (0.62, 0.62, 0.60, 1.0), segments=5)
    make_box("Entrance_Mat_Out", (0.0, -0.80, 0.008), (2.6, 1.20, 0.016), DARK)
    make_box("Entrance_Mat_In", (0.0, 0.90, 0.008), (2.6, 1.40, 0.016), DARK)
    make_box("Entrance_Sign", (0.0, -0.15, 3.60), (6.0, 0.08, 1.20), (0.94, 0.94, 0.90, 1.0))
    make_box("Entrance_Sign_Letters", (0.0, -0.195, 3.60), (4.6, 0.01, 0.62), COL_ACCENT)


# ── the front: checkouts, service desk, carts ─────────────────────
def _lane_light(prefix, x, y, n):
    make_cyl(f"{prefix}_Pole", (x, y, 1.10), 0.03, 2.20, STEEL, segments=8)
    make_box(f"{prefix}_Box", (x, y, 2.38), (0.30, 0.30, 0.36), (0.94, 0.94, 0.90, 1.0))
    make_box(f"{prefix}_Number", (x, y - 0.152, 2.38), (0.14, 0.004, 0.20), (0.18, 0.18, 0.20, 1.0))
    make_box(f"{prefix}_Number_Ink", (x + (0.03 if n % 2 else -0.03), y - 0.155, 2.38), (0.03, 0.002, 0.16), (0.94, 0.94, 0.90, 1.0))


def build_front():
    for k, cx in enumerate(CHECK_XS):
        top_z = make_counter(f"Checkout_{k}", (cx, CHECK_Y, 0.0), length=2.60, depth=0.90, height=0.90,
                             palette={"formica": (0.60, 0.64, 0.66, 1.0), "top": (0.24, 0.26, 0.28, 1.0),
                                      "kick": (0.24, 0.26, 0.28, 1.0)})
        make_box(f"Checkout_{k}_Belt", (cx - 0.05, CHECK_Y - 0.25, top_z + 0.015), (0.46, 1.80, 0.03), (0.12, 0.12, 0.14, 1.0))
        for gi in range(6):
            make_box(f"Checkout_{k}_Belt_Rib_{gi}", (cx - 0.05, CHECK_Y - 1.05 + gi * 0.32, top_z + 0.0305), (0.46, 0.02, 0.002),
                     (0.24, 0.24, 0.26, 1.0))
        make_register(f"Checkout_{k}_Register", (cx + 0.12, CHECK_Y + 0.95, top_z))
        make_credit_card_terminal(f"Checkout_{k}_CardTerm", (cx - 0.38, CHECK_Y + 0.75, top_z))
        make_box(f"Checkout_{k}_Scanner_Glass", (cx - 0.05, CHECK_Y + 0.62, top_z + 0.004), (0.30, 0.22, 0.006), (0.24, 0.36, 0.30, 1.0))
        # the bag carousel at the belt's end, the candy rack on the lane face
        make_cyl(f"Checkout_{k}_Bagger_Post", (cx + 0.10, CHECK_Y + 1.62, 0.50), 0.03, 1.00, STEEL, segments=8)
        make_cyl(f"Checkout_{k}_Bagger_Top", (cx + 0.10, CHECK_Y + 1.62, 1.02), 0.28, 0.03, STEEL, segments=12)
        for b in range(3):
            ang = b * 2.094
            make_box(f"Checkout_{k}_Bagger_Bag_{b}", (cx + 0.10 + 0.20 * math.cos(ang), CHECK_Y + 1.62 + 0.20 * math.sin(ang), 0.86),
                     (0.18, 0.18, 0.28), (0.94, 0.94, 0.92, 1.0))
        make_box(f"Checkout_{k}_Candy_Rack", (cx - 0.47, CHECK_Y - 0.60, 0.55), (0.04, 1.10, 1.10), DARK)
        for sh in range(4):
            make_box(f"Checkout_{k}_Candy_Rack_Shelf_{sh}", (cx - 0.55, CHECK_Y - 0.60, 0.14 + sh * 0.27), (0.12, 1.10, 0.02), STEEL)
            # the impulse stock by the merch grammar (2026-10-07: solid toy
            # blocks) — gum tubes, jerky, nuts, faced to the lane (-X),
            # authored along X and turned onto the rack's Y run
            from _props import merch as M
            px, py = cx - 0.55, CHECK_Y - 0.60
            M._ROT, M._LEAN = (px, py), True
            try:
                for si, kind in enumerate((("tubes", "jerky"), ("jerky", "nuts"), ("tubes", "tubes"), ("nuts", "jerky"))[sh]):
                    M.merch_section(f"Checkout_{k}_Candy_Rack_Stock_{sh}_{si}", kind, px - 0.55 + si * 0.55, py + 0.06, +1,
                                    0.14 + sh * 0.27 + 0.01, k * 7 + sh * 3 + si, width=0.55)
            finally:
                M._ROT, M._LEAN = None, False
        _lane_light(f"Checkout_{k}_Lane_Light", cx + 0.40, CHECK_Y - 1.45, k + 1)   # at the lane's entry, off the counter
    # THE FIVE on lane 1's belt; DIEGO'S BACKPACK in the cubby behind lane 1
    cx = CHECK_XS[0]
    make_box("Five_Dollar_Bill", (cx - 0.05, CHECK_Y - 0.40, 0.90 + 0.032 + 0.0008), (0.156, 0.066, 0.0015), (0.62, 0.68, 0.56, 1.0))
    make_chamfer_box("Register_Cubby", (cx + 0.63, CHECK_Y + 0.30, 0.45), (0.36, 1.20, 0.90), (0.46, 0.42, 0.36, 1.0))
    make_chamfer_box("Register_Cubby_Backpack", (cx + 0.63, CHECK_Y + 0.10, 1.11), (0.30, 0.32, 0.42), (0.30, 0.36, 0.30, 1.0))
    # the customer service desk, east wall front
    make_counter("Service_Desk", (13.30, 2.70, 0.0), length=3.20, depth=0.80, height=1.05,
                 palette={"formica": COL_ACCENT, "top": (0.24, 0.26, 0.28, 1.0), "kick": DARK})
    make_box("Service_Desk_Sign", (13.30, 3.75, 3.30), (0.06, 2.40, 0.50), (0.94, 0.94, 0.90, 1.0))
    for e in (-1, 1):
        make_cyl(f"Service_Desk_Sign_Wire_{e:+d}", (13.30, 3.75 + e * 1.0, (3.55 + CEIL) / 2.0), 0.006, CEIL - 3.55, STEEL, segments=4)
    make_box("Service_Desk_Sign_Letters", (13.26, 3.75, 3.30), (0.01, 1.80, 0.22), COL_ACCENT)
    # the cart corral just inside the entrance, west
    for k in range(5):
        _cart(f"Cart_Corral_{k}", -3.40 + k * 0.20, 1.40)
    for b in range(5):
        make_box(f"Basket_Stack_{b}", (-1.95, 0.55, 0.05 + b * 0.10), (0.34, 0.24, 0.10), (0.62, 0.30, 0.24, 1.0))


def _cart(prefix, cx, cy):
    """A wire cart facing north (nested carts share the frame)."""
    wire = (0.72, 0.74, 0.78, 1.0)
    for zi, bz in enumerate((0.46, 0.60, 0.74)):
        w, d = 0.22 + zi * 0.02, 0.32 + zi * 0.02
        make_tube(f"{prefix}_Rail_{zi}", [(cx - w, cy - d, bz), (cx + w, cy - d, bz), (cx + w, cy + d, bz),
                                          (cx - w, cy + d, bz), (cx - w, cy - d, bz)], 0.006, wire, segments=5)
    for ci, (u, v) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        make_tube(f"{prefix}_Upright_{ci}", [(cx + u * 0.22, cy + v * 0.32, 0.44), (cx + u * 0.26, cy + v * 0.36, 0.80)], 0.007, wire, segments=5)
    make_box(f"{prefix}_Floor", (cx, cy, 0.45), (0.44, 0.62, 0.012), wire)
    for u in (-1, 1):
        make_tube(f"{prefix}_Leg_{u:+d}", [(cx + u * 0.20, cy - 0.28, 0.10), (cx + u * 0.20, cy - 0.28, 0.44),
                                           (cx + u * 0.20, cy + 0.28, 0.44), (cx + u * 0.20, cy + 0.28, 0.10)], 0.01, STEEL, segments=5)
    make_tube(f"{prefix}_Handle", [(cx - 0.26, cy - 0.36, 0.80), (cx - 0.26, cy - 0.42, 0.92), (cx + 0.26, cy - 0.42, 0.92),
                                   (cx + 0.26, cy - 0.36, 0.80)], 0.012, STEEL, segments=6)
    make_cyl(f"{prefix}_Grip", (cx, cy - 0.42, 0.92), 0.018, 0.30, (0.72, 0.20, 0.18, 1.0), axis='X', segments=8)
    for wi, (u, v) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        make_lathe(f"{prefix}_Caster_{wi}", (cx + u * 0.20, cy + v * 0.28, 0.0),
                   [(0.0, 0.0), (0.04, 0.005), (0.045, 0.06), (0.03, 0.09), (0.0, 0.10)], P.METAL_BLACK, segments=8)


# ── produce ────────────────────────────────────────────────────────
PRODUCE_COLS = [(0.82, 0.24, 0.20, 1.0), (0.92, 0.58, 0.20, 1.0), (0.86, 0.82, 0.32, 1.0),
                (0.36, 0.54, 0.28, 1.0), (0.62, 0.30, 0.42, 1.0), (0.94, 0.86, 0.40, 1.0)]


def _produce_island(prefix, cx, cy, seed):
    make_chamfer_box(f"{prefix}_Base", (cx, cy, 0.315), (2.40, 1.40, 0.63), (0.42, 0.30, 0.20, 1.0))
    make_box(f"{prefix}_Tier1", (cx, cy - 0.10, 0.66), (2.40, 1.20, 0.06), (0.52, 0.38, 0.26, 1.0))
    make_box(f"{prefix}_Tier2_Riser", (cx, cy + 0.30, 0.79), (2.40, 0.60, 0.20), (0.42, 0.30, 0.20, 1.0))
    make_box(f"{prefix}_Tier2", (cx, cy + 0.30, 0.92), (2.40, 0.60, 0.06), (0.52, 0.38, 0.26, 1.0))
    for gi in range(8):
        gx = cx - 1.05 + gi * 0.30
        col = PRODUCE_COLS[(gi + seed) % len(PRODUCE_COLS)]
        for kk in range(6):
            make_lathe(f"{prefix}_Fruit_{gi}_{kk}", (gx + (kk % 3) * 0.08 - 0.08, cy - 0.40 + (kk // 3) * 0.10, 0.69),
                       [(0.0, 0.0), (0.035, 0.008), (0.05, 0.035), (0.048, 0.065), (0.03, 0.085), (0.0, 0.09)], col, segments=6)
    for li in range(7):
        make_box(f"{prefix}_Greens_{li}", (cx - 0.95 + li * 0.32, cy + 0.30, 1.01), (0.22, 0.20, 0.12),
                 ((0.34, 0.50, 0.26, 1.0), (0.46, 0.60, 0.30, 1.0))[li % 2])
    make_box(f"{prefix}_Price_Card", (cx, cy - 0.705, 0.55), (0.30, 0.004, 0.14), PAPER)


def build_produce():
    # THE PRODUCE WET WALL — sloped misted racks along the west wall
    wx0 = XW
    make_box("Wet_Wall_Back", (wx0 + 0.05, 6.75, 1.40), (0.10, 9.5, 2.80), (0.20, 0.30, 0.24, 1.0))
    make_box("Wet_Wall_Base", (wx0 + 0.50, 6.75, 0.35), (0.90, 9.5, 0.70), (0.30, 0.32, 0.30, 1.0))
    for t, (depth, z) in enumerate(((0.90, 0.82), (0.62, 1.18), (0.36, 1.54))):
        make_box(f"Wet_Wall_Tier_{t}", (wx0 + 0.05 + depth / 2.0, 6.75, z), (depth, 9.4, 0.04), STEEL)
        gx = wx0 + 0.05 + depth - 0.17
        for k in range(30):
            make_box(f"Wet_Wall_Tier_{t}_Greens_{k}", (gx, 2.20 + k * 0.31, z + 0.07), (0.30, 0.26, 0.10),
                     ((0.30, 0.50, 0.26, 1.0), (0.42, 0.60, 0.30, 1.0), (0.56, 0.30, 0.42, 1.0), (0.36, 0.54, 0.22, 1.0))[(k + t) % 4])
    make_cyl("Wet_Wall_Mist_Bar", (wx0 + 0.30, 6.75, 2.68), 0.02, 9.4, STEEL, axis='Y', segments=6)
    make_box("Wet_Wall_Canopy", (wx0 + 0.45, 6.75, 2.75), (0.90, 9.5, 0.10), COL_ACCENT)
    make_box("Wet_Wall_Canopy_Lamp", (wx0 + 0.70, 6.75, 2.695), (0.10, 9.2, 0.02), (0.98, 0.96, 0.86, 1.0))
    # three islands, the hanging scale over the first
    for k, (cx, cy) in enumerate(((-11.0, 4.5), (-11.0, 8.6), (-7.6, 6.5))):
        _produce_island(f"Produce_Island_{k}", cx, cy, k * 3)
    sx, sy = -10.2, 4.5
    make_lathe("Produce_Scale_Body", (sx, sy, 1.47), [(0.12, 0.0), (0.13, 0.02), (0.13, 0.14), (0.10, 0.16), (0.0, 0.16)], STEEL, segments=12)
    make_cyl("Produce_Scale_Dial", (sx, sy - 0.132, 1.55), 0.09, 0.006, (0.92, 0.92, 0.88, 1.0), axis='Y', segments=14)
    make_tube("Produce_Scale_Rod", [(sx, sy, 1.63), (sx, sy, CEIL)], 0.008, STEEL, segments=5)
    make_lathe("Produce_Scale_Pan", (sx, sy, 1.30), [(0.0, 0.0), (0.16, 0.0), (0.18, 0.03), (0.16, 0.04), (0.0, 0.035)],
               (0.72, 0.74, 0.78, 1.0), segments=14)
    for ci2 in range(3):
        ang2 = ci2 * 2.094
        make_tube(f"Produce_Scale_Chain_{ci2}", [(sx + 0.15 * math.cos(ang2), sy + 0.15 * math.sin(ang2), 1.34), (sx, sy, 1.47)],
                  0.003, STEEL, segments=4)
    # bins of onions and potatoes under the storefront glass
    for k in range(4):
        bx = -13.2 + k * 1.02      # one row of bins, butted
        make_box(f"Produce_Bin_{k}", (bx, 0.46, 0.35), (1.0, 0.70, 0.70), (0.52, 0.38, 0.24, 1.0))
        make_blob(f"Produce_Bin_{k}_Pile", (bx, 0.46, 0.72), 0.36, ((0.80, 0.62, 0.40, 1.0), (0.62, 0.46, 0.30, 1.0))[k % 2],
                  noise=0.15, seed=k, squash=0.45)
    # the wet-floor cone at the wet wall's misted edge
    make_chamfer_box("Cone_Base", (-12.9, 10.4, 0.02), (0.30, 0.30, 0.04), (0.96, 0.72, 0.20, 1.0), chamfer=0.01)
    make_lathe("Cone_Body", (-12.9, 10.4, 0.04), [(0.13, 0.0), (0.12, 0.05), (0.03, 0.62), (0.0, 0.64)], (0.96, 0.72, 0.20, 1.0), segments=12)
    make_box("Cone_Sign", (-12.9, 10.322, 0.36), (0.12, 0.002, 0.10), (0.16, 0.16, 0.18, 1.0))


# ── the aisles ─────────────────────────────────────────────────────
def _digit(prefix, x, y, z, n, h=0.30, col=(0.96, 0.96, 0.92, 1.0)):
    """A seven-segment numeral on a north/south-facing board (y = its face)."""
    segs = {0: "abcdef", 1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc", 5: "afgcd", 6: "afgedc", 7: "abc", 8: "abcdefg", 9: "abcfgd"}[n]
    w, t = h * 0.55, h * 0.12
    pos = {"a": (0, h / 2, True), "g": (0, 0, True), "d": (0, -h / 2, True),
           "f": (-w / 2, h / 4, False), "b": (w / 2, h / 4, False), "e": (-w / 2, -h / 4, False), "c": (w / 2, -h / 4, False)}
    for sgm in segs:
        dx, dz, horiz = pos[sgm]
        make_box(f"{prefix}_Seg_{sgm}", (x + dx, y, z + dz), (w, 0.004, t) if horiz else (t, 0.004, h / 2), col)


def build_aisles():
    plans = ("grocery", "grocery", "grocery", "grocery", "grocery", "grocery")
    for k, gx in enumerate(GONDOLA_XS):
        stock_gondola(f"Aisle_{k}", (gx, (G_Y0 + G_Y1) / 2.0, 0.0), length=G_Y1 - G_Y0, levels=G_LEVELS,
                      plan=plans[k], seed=k * 5, axis='Y', base_col=DARK, metal=STEEL, tag_col=PAPER, lean=True)
        # the end cap on the south end, faced to the action alley
        make_endcap(f"EndCap_{k}", (gx, G_Y0 - 0.42, 0.0), palette={"header": COL_ACCENT})
        # SHELF TALKERS (2026-10-07): the flags that stick out of the price
        # strips into the lane, read face-on by someone walking it — SALE
        # yellow, NEW red, Centro-value green — five a side, at eye level
        talkers = (((0.98, 0.86, 0.22, 1.0), (0.82, 0.16, 0.14, 1.0)), ((0.86, 0.20, 0.16, 1.0), (0.98, 0.98, 0.96, 1.0)),
                   ((0.96, 0.96, 0.92, 1.0), COL_ACCENT))
        for s_ in (-1, 1):
            for j in range(5):
                ty = G_Y0 + 1.1 + j * 1.75 + (0.45 if s_ > 0 else 0.0)
                lvl = G_LEVELS[2 + (j + k) % 2]
                fx = gx + s_ * 0.356                       # the price strip's face
                col, band = talkers[(j + k + (1 if s_ > 0 else 0)) % 3]
                make_box(f"Talker_{k}_{s_:+d}_{j}", (fx + s_ * 0.06, ty, lvl - 0.0625), (0.12, 0.004, 0.075), col)
                make_box(f"Talker_{k}_{s_:+d}_{j}_Band", (fx + s_ * 0.06, ty, lvl - 0.0125), (0.12, 0.004, 0.025), band)
    # a blade over every lane's mouth: the aisle number, a category strip
    for k, lx in enumerate(LANE_XS):
        n = 5 + k
        y = G_Y0 + 0.30
        make_box(f"Aisle_Blade_{n}", (lx, y, 3.30), (1.30, 0.05, 0.90), COL_ACCENT)
        for e in (-1, 1):
            make_cyl(f"Aisle_Blade_{n}_Wire_{e:+d}", (lx + e * 0.55, y, (3.75 + CEIL) / 2.0), 0.006, CEIL - 3.75, STEEL, segments=4)
        _digit(f"Aisle_Blade_{n}_Digit_S", lx - (0.12 if n >= 10 else 0.0), y - 0.027, 3.48, n % 10)
        _digit(f"Aisle_Blade_{n}_Digit_N", lx, y + 0.027, 3.48, n % 10)
        for r in range(3):
            make_box(f"Aisle_Blade_{n}_Category_{r}", (lx, y - 0.027, 3.15 - r * 0.14), (1.10, 0.004, 0.08), PAPER)
    # the fluorescent strips over the lanes, hung on wires
    for k, lx in enumerate(LANE_XS + [GONDOLA_XS[0] - 1.3, GONDOLA_XS[-1] + 1.3]):
        make_box(f"Fluor_Strip_{k}", (lx, (G_Y0 + G_Y1) / 2.0, STRIP_Z), (0.16, G_Y1 - G_Y0 - 0.4, 0.08), (0.94, 0.94, 0.90, 1.0))
        make_box(f"Fluor_Strip_{k}_Lens", (lx, (G_Y0 + G_Y1) / 2.0, STRIP_Z - 0.045), (0.12, G_Y1 - G_Y0 - 0.5, 0.01), (0.99, 0.98, 0.92, 1.0))
        for e in (-1, 1):
            make_cyl(f"Fluor_Strip_{k}_Wire_{e:+d}", (lx, (G_Y0 + G_Y1) / 2.0 + e * 3.8, (STRIP_Z + 0.04 + CEIL) / 2.0), 0.005,
                     CEIL - STRIP_Z - 0.04, STEEL, segments=4)
    for k, (x, y, ln) in enumerate(((-8.0, 3.2, 10.0), (6.6, 5.4, 9.0), (-6.0, 19.0, 14.0), (8.5, 18.6, 10.0), (-11.0, 13.5, 6.0))):
        make_box(f"Fluor_Run_{k}", (x, y, STRIP_Z), (ln, 0.16, 0.08), (0.94, 0.94, 0.90, 1.0))
        make_box(f"Fluor_Run_{k}_Lens", (x, y, STRIP_Z - 0.045), (ln - 0.1, 0.12, 0.01), (0.99, 0.98, 0.92, 1.0))
        for e in (-1, 1):
            make_cyl(f"Fluor_Run_{k}_Wire_{e:+d}", (x + e * (ln / 2.0 - 0.5), y, (STRIP_Z + 0.04 + CEIL) / 2.0), 0.005,
                     CEIL - STRIP_Z - 0.04, STEEL, segments=4)
    # THE PALLET in Aisle Seven, against the west gondola's face, the hand
    # truck parked behind it; the dented can leaking under 4F
    gx_w = GONDOLA_XS[2] + 0.35                  # Aisle Seven's west shelf face
    plx, ply = gx_w + 0.52, 11.60
    make_box("Pallet", (plx, ply, 0.08), (1.00, 1.20, 0.16), (0.62, 0.48, 0.30, 1.0))
    make_chamfer_box("Pallet_Load", (plx, ply, 0.46), (0.90, 1.05, 0.60), (0.68, 0.56, 0.38, 1.0))
    for k in range(3):
        make_box(f"Pallet_Load_Case_Label_{k}", (plx - 0.451, ply - 0.35 + k * 0.35, 0.50), (0.003, 0.20, 0.12), (0.80, 0.20, 0.16, 1.0))
    hx, hy = gx_w + 0.40, ply - 1.10
    make_rot_box("HandTruck_Frame", (hx, hy, 0.60), (0.40, 0.08, 1.20), (0.62, 0.28, 0.24, 1.0), roll=0.0)
    make_box("HandTruck_Toe", (hx, hy + 0.04, 0.04), (0.44, 0.30, 0.03), STEEL)
    for wi3, wx3 in enumerate((hx - 0.22, hx + 0.22)):
        make_lathe(f"HandTruck_Wheel_{wi3}", (wx3, hy - 0.05, 0.0), [(0.0, 0.0), (0.12, 0.0), (0.12, 0.05), (0.0, 0.05)],
                   P.METAL_BLACK, segments=10)
    top = 0.76
    make_box("Russell_Clipboard", (plx, ply - 0.15, top + 0.006), (0.240, 0.320, 0.012), (0.55, 0.42, 0.28, 1.0))
    make_box("Clipboard_Sheet", (plx, ply - 0.14, top + 0.0135), (0.210, 0.280, 0.002), (0.94, 0.93, 0.88, 1.0))
    make_box("Clipboard_Clip", (plx, ply - 0.295, top + 0.022), (0.060, 0.030, 0.020), STEEL)
    make_cyl("Russell_Pen", (plx + 0.06, ply - 0.08, top + 0.0195), 0.005, 0.130, (0.24, 0.28, 0.52, 1.0), axis='Y', segments=6)
    make_box("Diegos_Phone", (plx + 0.25, ply + 0.20, top + 0.0055), (0.070, 0.140, 0.011), (0.13, 0.13, 0.15, 1.0))
    make_box("Chain_Scanner", (plx - 0.20, ply + 0.30, top + 0.0225), (0.060, 0.150, 0.045), (0.22, 0.22, 0.25, 1.0))
    make_box("Scanner_Window", (plx - 0.20, ply + 0.2214, top + 0.0225), (0.036, 0.006, 0.020), (0.70, 0.24, 0.20, 1.0))
    make_cyl("Dented_Can", (GONDOLA_XS[3] - 0.55, 9.40, 0.055), 0.05, 0.11, (0.84, 0.80, 0.70, 1.0), axis='X', segments=10)
    make_cyl("Can_Puddle", (GONDOLA_XS[3] - 0.62, 9.38, 0.006), 0.09, 0.005, (0.72, 0.68, 0.56, 1.0), segments=10)
    make_box("Wear_Lane_Seven", (AISLE_7_X, (G_Y0 + G_Y1) / 2.0, 0.0018), (0.70, G_Y1 - G_Y0, 0.002), (0.72, 0.71, 0.66, 1.0))


def _meat_tray(tag, tx, ty, z0, kind, k):
    """One steel tray (0.46 x 0.60) and its cut, a price tag on a pick at
    the tray's front. z0 = the case bed's top."""
    make_box(tag, (tx, ty, z0 + 0.01), (0.46, 0.60, 0.02), (0.74, 0.76, 0.78, 1.0))
    top = z0 + 0.02
    red, red_dk, fat = (0.70, 0.18, 0.16, 1.0), (0.56, 0.14, 0.12, 1.0), (0.94, 0.88, 0.80, 1.0)
    if kind == "steaks":
        for i in range(3):
            y = ty - 0.18 + i * 0.18
            make_chamfer_box(f"{tag}_Steak_{i}_Fat", (tx, y, top + 0.010), (0.30, 0.15, 0.020), fat, chamfer=0.008)
            make_chamfer_box(f"{tag}_Steak_{i}", (tx - 0.01, y, top + 0.026), (0.27, 0.13, 0.012), red if i % 2 else red_dk, chamfer=0.005)
    elif kind == "ground":
        for i in range(2):
            make_blob(f"{tag}_Ground_{i}", (tx, ty - 0.13 + i * 0.27, top + 0.03), 0.12, (0.78, 0.30, 0.30, 1.0),
                      noise=0.30, seed=40 + k + i, squash=0.30)
    elif kind == "chops":
        for i in range(4):
            y = ty - 0.21 + i * 0.14
            make_chamfer_box(f"{tag}_Chop_{i}", (tx + 0.02, y, top + 0.012), (0.24, 0.11, 0.024), (0.86, 0.56, 0.52, 1.0), chamfer=0.006)
            make_box(f"{tag}_Chop_{i}_Bone", (tx - 0.12, y, top + 0.014), (0.06, 0.03, 0.028), fat)
    elif kind == "chicken":
        for i in range(6):
            make_blob(f"{tag}_Chicken_{i}", (tx - 0.10 + (i % 2) * 0.20, ty - 0.18 + (i // 2) * 0.18, top + 0.03), 0.07,
                      (0.94, 0.80, 0.70, 1.0), noise=0.25, seed=60 + k + i, squash=0.50)
    elif kind == "links":
        for i in range(7):
            y = ty - 0.24 + i * 0.08
            for j in range(2):
                make_cyl(f"{tag}_Link_{i}_{j}", (tx - 0.09 + j * 0.18, y, top + 0.024), 0.024, 0.16,
                         (0.66, 0.36, 0.28, 1.0), axis='X', segments=8)
    elif kind == "roast":
        make_blob(f"{tag}_Roast", (tx, ty, top + 0.07), 0.14, red_dk, noise=0.18, seed=80 + k, squash=0.65)
        for i in range(3):
            make_box(f"{tag}_Roast_Twine_{i}", (tx - 0.08 + i * 0.08, ty, top + 0.07), (0.008, 0.26, 0.15), fat)
    # the price tag on its pick, at the tray's front
    make_cyl(f"{tag}_Tag_Pick", (tx + 0.15, ty - 0.27, top + 0.04), 0.003, 0.08, (0.92, 0.92, 0.90, 1.0), segments=4)
    make_box(f"{tag}_Tag", (tx + 0.15, ty - 0.275, top + 0.085), (0.08, 0.004, 0.05), (0.98, 0.98, 0.96, 1.0))
    make_box(f"{tag}_Tag_Price", (tx + 0.15, ty - 0.278, top + 0.08), (0.05, 0.002, 0.015), (0.80, 0.16, 0.14, 1.0))


# ── the back: dairy, receiving, meat ──────────────────────────────
def build_back():
    # the DAIRY case holds dairy (2026-10-07: it held beer six-packs and soda
    # cans) — gallons low, half-gallons, eggs and butter, yogurt and cheese
    make_cooler_row("Cooler", COOLER_WALL_Y, DAIRY_DOORS, cz=1.25, shelves=5, stock="dairy")
    make_box("Dairy_Sign", (DAIRY_DOORS[5], YN - 0.03, 3.20), (6.0, 0.06, 0.60), COL_ACCENT)
    make_box("Dairy_Sign_Letters", (DAIRY_DOORS[5], YN - 0.065, 3.20), (3.4, 0.01, 0.30), PAPER)
    # the propped door, its crate, Russell's thermometer on its inner face
    dx = DAIRY_DOORS[PROPPED]
    # hinged at the frame's west edge, swung 45 degrees into the aisle; the
    # crate at its free edge holds it there
    hx, hy = dx - 0.62, COOLER_WALL_Y + 0.04
    lx, ly = hx + 0.60 * 0.7071, hy - 0.60 * 0.7071
    make_rot_box("Cooler_Door_Leaf", (lx, ly, 1.25), (0.05, 1.20, 2.04), (0.82, 0.84, 0.86, 1.0), yaw=0.7854)
    make_box("Cooler_Door_Handle", (hx + 1.05 * 0.7071 - 0.03, hy - 1.05 * 0.7071 - 0.03, 1.25), (0.03, 0.03, 0.30), STEEL)
    make_box("Cooler_Door_Milk_Crate_Prop", (hx + 1.20 * 0.7071 + 0.10, hy - 1.20 * 0.7071 - 0.08, 0.14), (0.32, 0.32, 0.28),
             (0.30, 0.44, 0.62, 1.0))
    make_box("Cooler_Thermometer", (lx + 0.04, ly + 0.04, 1.70), (0.05, 0.05, 0.14), (0.90, 0.89, 0.86, 1.0))
    make_box("Cooler_Thermometer_Needle", (lx + 0.07, ly + 0.07, 1.68), (0.01, 0.01, 0.03), (0.80, 0.22, 0.18, 1.0))
    make_lathe("Floor_Drain", (dx - 0.3, COOLER_WALL_Y - 1.20, 0.0), [(0.0, 0.0), (0.08, 0.0), (0.09, 0.006), (0.0, 0.008)],
               (0.36, 0.36, 0.38, 1.0), segments=12)
    # RECEIVING: the double flap doors, the sign, the bale beside them
    for sgn, nm in ((-1, "W"), (1, "E")):
        make_box(f"Receiving_Door_{nm}", (5.0 + sgn * 0.45, Y1, 1.15), (0.88, 0.04, 2.30), (0.20, 0.20, 0.22, 1.0))
        make_box(f"Receiving_Door_{nm}_Window", (5.0 + sgn * 0.45, Y1 - 0.025, 1.65), (0.30, 0.006, 0.40), (0.52, 0.60, 0.64, 1.0))
        make_box(f"Receiving_Door_{nm}_Kick", (5.0 + sgn * 0.45, Y1 - 0.025, 0.25), (0.80, 0.006, 0.40), STEEL)
    make_box("Receiving_Sign", (5.0, YN - 0.01, 2.70), (1.40, 0.02, 0.26), (0.94, 0.94, 0.90, 1.0))
    make_box("Receiving_Sign_Letters", (5.0, YN - 0.022, 2.70), (1.10, 0.004, 0.12), (0.80, 0.16, 0.14, 1.0))
    make_chamfer_box("Card_Bale", (3.30, YN - 0.34, 0.70), (0.90, 0.64, 1.40), (0.44, 0.48, 0.52, 1.0))
    make_box("Card_Bale_Lid", (3.30, YN - 0.34, 1.42), (0.86, 0.60, 0.05), STEEL)
    make_box("Card_Bale_Stack", (3.30, YN - 0.36, 0.90), (0.70, 0.50, 0.30), (0.66, 0.54, 0.36, 1.0))
    # THE MEAT COUNTER: the service case along the north wall's east run
    mx0, mx1, my = 6.6, 13.2, 20.00
    make_chamfer_box("Meat_Case_Body", ((mx0 + mx1) / 2.0, my, 0.55), (mx1 - mx0, 1.10, 1.10), (0.86, 0.86, 0.84, 1.0))
    for e in range(5):
        make_box(f"Meat_Case_Glass_Post_{e}", (mx0 + 0.1 + e * (mx1 - mx0 - 0.2) / 4.0, my - 0.53, 1.36), (0.04, 0.04, 0.52), STEEL)
    make_box("Meat_Case_Glass_Rail", ((mx0 + mx1) / 2.0, my - 0.53, 1.635), (mx1 - mx0 - 0.1, 0.04, 0.03), STEEL)
    for gi, (gx, gw) in enumerate(((-2.5, 0.03), (-2.4, 0.012), (1.0, 0.02), (2.9, 0.03))):
        make_box(f"Meat_Case_Glint_{gi}", ((mx0 + mx1) / 2.0 + gx, my - 0.53, 1.36), (gw, 0.004, 0.52), (0.86, 0.90, 0.92, 1.0))
    # the case's white bed, and on it twelve steel trays of CUTS (2026-10-07:
    # they were twelve flat red slabs) — a tray reads by what is on it
    make_box("Meat_Case_Bed", ((mx0 + mx1) / 2.0, my, 1.105), (mx1 - mx0 - 0.08, 0.86, 0.01), (0.94, 0.94, 0.92, 1.0))
    kinds = ("steaks", "ground", "chops", "chicken", "links", "roast")
    for mi in range(12):
        tx = mx0 + 0.40 + mi * 0.53
        _meat_tray(f"Meat_Tray_{mi}", tx, my, 1.11, kinds[mi % len(kinds)], mi)
        if mi < 11:   # the parsley line between trays
            make_box(f"Meat_Parsley_{mi}", (tx + 0.265, my, 1.125), (0.05, 0.58, 0.03), (0.28, 0.52, 0.22, 1.0))
    make_box("Meat_Back_Counter", ((mx0 + mx1) / 2.0, YN - 0.30, 0.46), (mx1 - mx0, 0.55, 0.92), (0.72, 0.74, 0.76, 1.0))
    make_box("Meat_Sign", ((mx0 + mx1) / 2.0, YN - 0.03, 3.20), (4.0, 0.06, 0.60), (0.62, 0.18, 0.16, 1.0))
    make_box("Meat_Sign_Letters", ((mx0 + mx1) / 2.0, YN - 0.065, 3.20), (2.2, 0.01, 0.30), PAPER)
    make_wall_clock("Clock", (-2.0, YN, 3.10), frozen_hour=3, frozen_min=14, facing='-Y')


# ── the east side: deli, bakery, frozen ───────────────────────────
def build_east():
    # THE DELI: a service case faced west, the slicer counter behind it
    dx, dy0, dy1 = 12.95, 7.6, 11.6
    make_chamfer_box("Deli_Case_Body", (dx, (dy0 + dy1) / 2.0, 0.55), (0.95, dy1 - dy0, 1.10), (0.86, 0.86, 0.84, 1.0))
    make_box("Deli_Case_Glass", (dx - 0.45, (dy0 + dy1) / 2.0, 1.30), (0.04, dy1 - dy0 - 0.1, 0.50), (0.55, 0.62, 0.66, 0.4))
    for k in range(8):
        make_box(f"Deli_Case_Tray_{k}", (dx, dy0 + 0.30 + k * 0.50, 1.13), (0.60, 0.42, 0.06),
                 ((0.90, 0.72, 0.62, 1.0), (0.94, 0.86, 0.56, 1.0), (0.72, 0.36, 0.30, 1.0))[k % 3])
    make_box("Deli_Back_Counter", (XE - 0.32, (dy0 + dy1) / 2.0, 0.46), (0.60, dy1 - dy0, 0.92), (0.72, 0.74, 0.76, 1.0))
    make_box("Deli_Slicer", (XE - 0.32, dy0 + 1.0, 1.05), (0.40, 0.50, 0.26), STEEL)
    make_cyl("Deli_Slicer_Blade", (XE - 0.48, dy0 + 1.0, 1.10), 0.15, 0.02, (0.84, 0.86, 0.88, 1.0), axis='X', segments=14)
    make_box("Deli_Scale", (XE - 0.32, dy0 + 2.4, 0.97), (0.34, 0.30, 0.10), (0.88, 0.88, 0.86, 1.0))
    make_box("Deli_Sign", (XE - 0.03, (dy0 + dy1) / 2.0, 3.20), (0.06, 3.6, 0.60), (0.80, 0.52, 0.20, 1.0))
    make_box("Deli_Sign_Letters", (XE - 0.065, (dy0 + dy1) / 2.0, 3.20), (0.01, 2.0, 0.30), PAPER)
    # the bakery: a pastry case, the bread racks and the coffee pots
    by0, by1 = 12.6, 15.0
    top_z = make_counter("Bakery_Counter", (13.0, (by0 + by1) / 2.0, 0.0), length=by1 - by0, depth=0.90, height=0.95,
                         palette={"formica": (0.74, 0.62, 0.42, 1.0), "top": (0.32, 0.22, 0.14, 1.0), "kick": (0.32, 0.22, 0.14, 1.0)})
    make_donut_display("Bakery_Donuts", (12.95, by0 + 0.80, top_z), tiers=3)
    make_coffee_pots("Bakery_Coffee", (12.95, by1 - 0.70, top_z), pots=3)
    make_box("Bakery_Sign", (XE - 0.03, (by0 + by1) / 2.0, 3.20), (0.06, 2.6, 0.60), (0.86, 0.62, 0.30, 1.0))
    # THE FROZEN BANK: glass doors along the east wall's north run, faced west
    fy0, fy1 = 16.0, 19.0
    make_chamfer_box("Frozen_Bank", (XE - 0.30, (fy0 + fy1) / 2.0, 1.10), (0.60, fy1 - fy0, 2.20), (0.80, 0.84, 0.88, 1.0))
    n = int((fy1 - fy0) / 0.75)
    for fi in range(n):
        fy = fy0 + 0.40 + fi * 0.75
        make_box(f"Frozen_Door_{fi}", (XE - 0.615, fy, 1.15), (0.03, 0.70, 1.80), (0.55, 0.62, 0.66, 0.4))
        make_box(f"Frozen_Door_{fi}_Handle", (XE - 0.645, fy + 0.28, 1.15), (0.03, 0.03, 0.40), STEEL)
        for r in range(4):
            make_box(f"Frozen_Door_{fi}_Boxes_{r}", (XE - 0.50, fy, 0.50 + r * 0.42), (0.18, 0.62, 0.22),
                     ((0.18, 0.30, 0.62, 1.0), (0.80, 0.18, 0.14, 1.0), (0.94, 0.74, 0.16, 1.0))[(fi + r) % 3])
    make_box("Frozen_Sign", (XE - 0.03, (fy0 + fy1) / 2.0, 3.20), (0.06, 3.0, 0.60), (0.24, 0.42, 0.70, 1.0))
    # the bread racks along the west wall's north run
    stock_gondola("Bread_Rack", (XW + 0.36, 16.5, 0.0), length=7.0, levels=G_LEVELS[:4], plan="bread", sides=(-1,),
                  axis='Y', seed=2, base_col=DARK, metal=STEEL, tag_col=PAPER, end_panels=True, lean=True)
    make_box("Bread_Sign", (XW + 0.03, 16.5, 3.20), (0.06, 3.0, 0.60), (0.80, 0.56, 0.30, 1.0))
    make_box("Produce_Sign", (-10.0, 6.5, 3.40), (4.0, 0.06, 0.70), COL_ACCENT)
    for e in (-1, 1):
        make_cyl(f"Produce_Sign_Wire_{e:+d}", (-10.0 + e * 1.8, 6.5, (3.75 + CEIL) / 2.0), 0.006, CEIL - 3.75, STEEL, segments=4)
    make_box("Produce_Sign_Letters", (-10.0, 6.465, 3.40), (2.6, 0.01, 0.34), PAPER)
    # the staff calendar on the east wall's face, faced into the store (-X)
    make_box("Calendar_Body", (XE - 0.003, 5.4, 1.70), (0.005, 0.40, 0.50), (0.78, 0.62, 0.46, 1.0))
    make_box("Calendar_Grid", (XE - 0.006, 5.4, 1.55), (0.001, 0.34, 0.20), PAPER)


# ── outside the glass ──────────────────────────────────────────────
def build_lot():
    from _props.detail import make_far_bands
    from _props.vehicles import make_car
    make_box("Lot_Asphalt", (0.0, -9.0, -0.06), (60.0, 17.0, 0.10), (0.26, 0.26, 0.27, 1.0))
    make_box("Lot_Walk", (0.0, -1.2, -0.03), (40.0, 2.2, 0.06), (0.62, 0.60, 0.56, 1.0))
    make_box("Lot_Curb", (0.0, -2.35, -0.05), (40.0, 0.12, 0.14), (0.55, 0.53, 0.50, 1.0))
    for si in range(14):
        make_box(f"Lot_Stripe_{si}", (-17.0 + si * 2.7, -5.6, -0.008), (0.10, 5.0, 0.006), (0.86, 0.84, 0.72, 1.0))
    make_car("Lot_Car", -6.4, -5.8, 4.5, (0.60, 0.60, 0.62, 1.0), along="Y", z0=-0.01)
    make_car("Lot_Car_2", 9.8, -5.6, 4.6, (0.30, 0.32, 0.40, 1.0), along="Y", z0=-0.01)
    for ci, cx2 in enumerate((4.2, 6.4)):
        make_tube(f"Corral_Rail_{ci}", [(cx2, -4.0, 0.02), (cx2, -4.0, 0.95), (cx2, -7.0, 0.95), (cx2, -7.0, 0.02)], 0.02, STEEL, segments=6)
    make_box("Corral_Sign", (5.3, -7.05, 1.12), (2.24, 0.04, 0.30), COL_ACCENT)
    for k, lx in enumerate((-12.0, 12.0)):
        make_lathe(f"Lot_Lamp_Post_{k}", (lx, -9.0, 0.0), [(0.16, 0.0), (0.10, 0.10), (0.07, 7.8), (0.08, 8.0), (0.0, 8.0)],
                   (0.30, 0.30, 0.32, 1.0), segments=8)
        make_box(f"Lot_Lamp_Head_{k}", (lx, -9.0, 8.05), (0.70, 0.30, 0.16), (0.30, 0.30, 0.32, 1.0))
    make_far_bands("Far", (0.46, 0.44, 0.42, 1.0), [(22.0, 34.0, 5.0, 0.85), (32.0, 40.0, 7.0, 0.7)], sides="S", cy=0.0, profile="roofline")


# ── the manager's office over the front (2026-10-07) ─────────────
OF_X0, OF_Y1, OF_Z = 11.4, 2.30, 3.00        # office west edge, front face, floor top
HATCH_X1, HATCH_Y1 = 13.9, 1.00              # the stair's hole in the slab


def build_office():
    """THE MANAGER'S OFFICE — "she covers ... the manager's office and the
    break room" — a mezzanine over the front's south-east corner, above
    the service desk: a slab on a column, its front wall cut for a window
    over the sales floor (the blinds half down, a lamp lit behind), and a
    steel ship's stair under the slab along the south wall, clear of the
    storefront glass and the desk's clerk side."""
    slab = (0.52, 0.53, 0.54, 1.0)
    office_wall = (0.84, 0.83, 0.78, 1.0)
    # the slab, with the hatch over the stair's top
    make_box("Office_Slab_N", ((OF_X0 + XE) / 2.0, (HATCH_Y1 + OF_Y1) / 2.0, OF_Z - 0.075), (XE - OF_X0, OF_Y1 - HATCH_Y1, 0.15), slab)
    make_box("Office_Slab_SE", ((HATCH_X1 + XE) / 2.0, (YS + HATCH_Y1) / 2.0, OF_Z - 0.075), (XE - HATCH_X1, HATCH_Y1 - YS, 0.15), slab)
    make_box("Office_Slab_Fascia", ((OF_X0 + XE) / 2.0, OF_Y1 + 0.02, OF_Z - 0.20), (XE - OF_X0, 0.04, 0.40), COL_ACCENT)
    make_box("Office_Column", (OF_X0 + 0.10, OF_Y1 - 0.10, (OF_Z - 0.15) / 2.0), (0.14, 0.14, OF_Z - 0.15), STEEL)
    make_box("Office_Column_Foot", (OF_X0 + 0.10, OF_Y1 - 0.10, 0.01), (0.24, 0.24, 0.02), STEEL)
    # the front wall: piers, the spandrel and the lintel round the window
    wx0, wx1, wz0, wz1 = OF_X0 + 0.50, XE - 0.50, OF_Z + 0.55, OF_Z + 1.75
    wy = OF_Y1 - 0.06
    for nm, a, b, z0, z1 in (("Pier_W", OF_X0, wx0, OF_Z, CEIL), ("Pier_E", wx1, XE, OF_Z, CEIL),
                             ("Spandrel", wx0, wx1, OF_Z, wz0), ("Lintel", wx0, wx1, wz1, CEIL)):
        make_box(f"Office_Wall_{nm}", ((a + b) / 2.0, wy, (z0 + z1) / 2.0), (b - a, 0.12, z1 - z0), office_wall)
    make_box("Office_Wall_W", (OF_X0 + 0.06, (YS + OF_Y1 - 0.12) / 2.0, (OF_Z + CEIL) / 2.0), (0.12, OF_Y1 - 0.12 - YS, CEIL - OF_Z), office_wall)
    # the window: a frame ring, the glass, the blinds half down
    make_frame_ring("Office_Window_Frame", ((wx0 + wx1) / 2.0, wy, (wz0 + wz1) / 2.0), (wx1 - wx0, 0.12, wz1 - wz0), STEEL, bar=0.05)
    make_box("Office_Window_Glass", ((wx0 + wx1) / 2.0, wy, (wz0 + wz1) / 2.0), (wx1 - wx0 - 0.10, 0.01, wz1 - wz0 - 0.10), (0.72, 0.80, 0.84, 0.25))
    make_box("Office_Blind_Head", ((wx0 + wx1) / 2.0, wy - 0.09, wz1 - 0.08), (wx1 - wx0 - 0.10, 0.06, 0.06), (0.90, 0.90, 0.86, 1.0))
    for k in range(9):
        make_box(f"Office_Blind_Slat_{k}", ((wx0 + wx1) / 2.0, wy - 0.09, wz1 - 0.14 - k * 0.055), (wx1 - wx0 - 0.12, 0.05, 0.008),
                 (0.92, 0.92, 0.88, 1.0))
    for e in (-1, 1):
        make_box(f"Office_Blind_Cord_{e:+d}", ((wx0 + wx1) / 2.0 + e * 0.9, wy - 0.09, wz1 - 0.36), (0.006, 0.006, 0.50), (0.92, 0.92, 0.88, 1.0))
    # inside: the desk, its chair, the monitor, the lamp, a file cabinet,
    # the corkboard of schedules on the back wall
    dx, dy = 13.2, 0.95
    make_box("Office_Desk", (dx, dy, OF_Z + 0.375), (1.60, 0.70, 0.75), (0.46, 0.36, 0.26, 1.0))
    make_box("Office_Monitor", (dx - 0.30, dy - 0.15, OF_Z + 0.75 + 0.20), (0.50, 0.04, 0.32), (0.14, 0.14, 0.16, 1.0))
    make_box("Office_Monitor_Stand", (dx - 0.30, dy - 0.10, OF_Z + 0.75 + 0.03), (0.16, 0.12, 0.06), (0.14, 0.14, 0.16, 1.0))
    make_box("Office_Monitor_Screen", (dx - 0.30, dy - 0.172, OF_Z + 0.75 + 0.20), (0.46, 0.004, 0.28), (0.40, 0.56, 0.64, 1.0))
    make_cyl("Office_Lamp_Base", (dx + 0.55, dy + 0.10, OF_Z + 0.76), 0.07, 0.02, (0.20, 0.20, 0.22, 1.0), segments=8)
    make_cyl("Office_Lamp_Post", (dx + 0.55, dy + 0.10, OF_Z + 0.97), 0.012, 0.40, (0.20, 0.20, 0.22, 1.0), segments=6)
    make_cyl("Office_Lamp_Shade", (dx + 0.55, dy + 0.10, OF_Z + 1.20), 0.12, 0.12, (0.96, 0.86, 0.60, 1.0), segments=10)
    make_box("Office_Chair_Seat", (dx, dy + 0.62, OF_Z + 0.46), (0.48, 0.46, 0.08), (0.18, 0.18, 0.20, 1.0))
    make_box("Office_Chair_Base", (dx, dy + 0.62, OF_Z + 0.21), (0.08, 0.08, 0.42), (0.18, 0.18, 0.20, 1.0))
    make_box("Office_Chair_Back", (dx, dy + 0.86, OF_Z + 0.78), (0.46, 0.06, 0.56), (0.18, 0.18, 0.20, 1.0))
    make_box("Office_File_Cabinet", (XE - 0.28, 1.70, OF_Z + 0.66), (0.46, 0.60, 1.32), (0.56, 0.58, 0.58, 1.0))
    make_box("Office_Corkboard", ((dx + XE) / 2.0 - 0.2, YS + 0.015, OF_Z + 1.45), (1.20, 0.03, 0.80), (0.64, 0.48, 0.32, 1.0))
    for k in range(5):
        make_box(f"Office_Corkboard_Sheet_{k}", ((dx + XE) / 2.0 - 0.65 + k * 0.22, YS + 0.032, OF_Z + 1.45 + (0.12 if k % 2 else -0.10)),
                 (0.18, 0.004, 0.24), PAPER)
    # the hatch's guard rail on the office floor (open at the stair's head)
    for k, x in enumerate((12.30, 13.10, HATCH_X1 - 0.03)):
        make_box(f"Office_Rail_Post_{k}", (x, HATCH_Y1 + 0.03, OF_Z + 0.50), (0.04, 0.04, 1.00), STEEL)
    make_box("Office_Rail_Top", ((12.28 + HATCH_X1) / 2.0, HATCH_Y1 + 0.03, OF_Z + 1.00), (HATCH_X1 - 12.28, 0.05, 0.04), STEEL)
    make_box("Office_Rail_Mid", ((12.28 + HATCH_X1) / 2.0, HATCH_Y1 + 0.03, OF_Z + 0.50), (HATCH_X1 - 12.28, 0.03, 0.03), STEEL)
    make_box("Office_Rail_E", (HATCH_X1 + 0.03, (YS + HATCH_Y1) / 2.0, OF_Z + 0.50), (0.04, HATCH_Y1 - YS, 1.00), STEEL)
    # the ship's stair: solid steps rising west along the south wall
    n = 17
    sx0, sx1 = 14.70, 11.62                  # the first riser's face, the top step's far edge
    run = (sx0 - sx1) / n
    for i in range(n):
        h = OF_Z * (i + 1) / n
        x = sx0 - run * (i + 0.5)
        make_box(f"Office_Stair_Step_{i}", (x, (YS + HATCH_Y1 - 0.10) / 2.0, h / 2.0), (run, HATCH_Y1 - 0.10 - YS, h), (0.40, 0.41, 0.42, 1.0))
        make_box(f"Office_Stair_Nosing_{i}", (x + run / 2.0 - 0.015, (YS + HATCH_Y1 - 0.10) / 2.0, h - 0.005), (0.03, HATCH_Y1 - 0.10 - YS, 0.01),
                 (0.86, 0.74, 0.20, 1.0))
    ry = HATCH_Y1 - 0.10 - 0.02
    for k in range(3):                       # posts off the 1st, 9th and 16th steps
        i = (0, 8, 15)[k]
        x = sx0 - run * (i + 0.5)
        make_box(f"Office_Stair_Post_{k}", (x, ry, OF_Z * (i + 1) / n + 0.45), (0.04, 0.04, 0.90), STEEL)
    make_tube("Office_Stair_Rail", [(sx0 - run * 0.5, ry, OF_Z * 1 / n + 0.90), (sx0 - run * 15.5, ry, OF_Z * 16 / n + 0.90)], 0.02, STEEL)
    make_box("Office_Door_Sign", (XE - 0.70, wy + 0.065, OF_Z + 2.05), (0.60, 0.006, 0.18), PAPER)


def main():
    clear_scene()
    build_shell()
    build_front()
    build_produce()
    build_aisles()
    build_back()
    build_east()
    build_lot()
    build_office()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/centro_grocery_aisle.glb"))
    print(f"\n[build_centro_grocery_aisle] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
