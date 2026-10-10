"""The drugstore — vol1 ch2's workplace ("The Drugstore": vol1_ch2_pharmacy
and vol1_ch2_pharmacy_mirror).

DRAFT 2 (2026-10-10) — rebuilt from the prose. Draft 1 was an 8 x 6 m box
with two gondolas, a gray "annex" behind a partition and the mirror bolted
to the sales floor. The chapter says otherwise:

  "Faust heads to his office, sits down at the computer ... grabs a
  handful of pills ... swallows them with coffee and glances about his
  office. The fluorescents hum like a slow apology." · "Faust stands up
  and inspects himself in the mirror." (still IN the office) · "Faust
  exits the office, emerges into the drugstore proper, looks out at the
  slow medicated trickle of society." · "From my whitewalled fortress of
  solitude I emerge and bask upon my kingdom — of cheap fluorescents and
  impulse buys." · "Deborah is helping a customer at the front table.
  Faust saunters up." · "Faust checks the bottle and hands it over to
  her." · "Eric enters ... Eric puts down lunch. I smell me some
  Vietnamese. Deborah is already digging into hers. Six eggrolls between
  the three of us."

So this is a CHAIN drugstore ("dime-this corporate skrill"), 26 x 22 m
under a 3.6 m drop ceiling of fluorescent troffers:
  · FRONT (S): the glass storefront and sliding doors, the parking lot and
    the street past it, two register stands with their impulse racks,
    the basket stack, the security pedestals, a promo table, the photo
    kiosk, the magazine rack.
  · THE AISLES: seven gondola runs, 7 m long, 2.1 m lanes — candy and
    snacks, household, hair, cosmetics, vitamins, pain and cold, first
    aid — each with its hanging aisle sign and a south endcap; wall bays
    down both side walls; the cooler doors in the NW corner.
  · THE PHARMACY (N, centre): raised 45 cm on its platform, so the
    pharmacist looks out over the shelf tops at his kingdom — the
    PHARMACY soffit, DROP OFF / PICK UP / CONSULTATION stations along
    the counter (the counter is "the front table" — waist height from
    his side), the will-call rack of white bags, the work island with
    its counting trays and screens, and on its end THE LUNCH: the
    takeout bag, three foam clamshells, one open on six eggrolls, the
    chopsticks and the sauce cups. The back wall of stock bottles.
  · THE OFFICE (NE of the pharmacy, behind it): white walls, one 2x4
    troffer, the desk on the N wall with the computer, the coffee, the
    open stock bottle and three tablets beside it, the chair; the
    full-length MIRROR on the E wall; the reference shelf, the diploma,
    the drug-rep sample boxes on the file cabinet, the calendar. Its
    door opens S onto the pharmacy; the half-gate and two steps lead
    down to the floor.
  · EAST of the pharmacy: the waiting chairs, the blood-pressure kiosk,
    the restroom and EMPLOYEES ONLY doors.

Coordinate frame: Blender Z-up. y=0 is the storefront (S) wall; +Y runs
back to the pharmacy. Walls x=+-13, back wall y=22, ceiling 3.6.
glTF export remaps to Godot (x, z, -y).

Vantages (Background3D.CAMERA_PRESETS):
  pharmacy_floor  — from the pharmacy platform behind PICK UP, over the
                    shelf tops down the lane to the storefront glass.
  pharmacy_office — the office's SW corner by the door: the desk on the
                    N wall, the mirror on the E wall.

Draft 3 targets: customers in the lanes are the VN's job, but the store
wants its trickle — a cart left in a lane, a basket on the floor at the
pickup, the queue line stanchions at the registers; endcap promotions
specific to the season the chapter is set in; the pharmacy's privacy
glass; restroom corridor depth past its door.
"""
import math
import os
import sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_rot_box, export_glb
from _props.structure import make_floor, make_wall, make_wall_with_openings, make_ceiling
from _props.safety import make_fluorescent_tube_fixture
from _props.merch import stock_gondola
from _props.coolers_drinks import make_cooler_door
from _props.furniture import make_chair
from _props.objects import make_mug
from _props.decor import make_calendar, make_wall_clock
from _props.views import make_view
from _props.vehicles import make_car

X0, X1 = -13.0, 13.0
Y0, Y1 = 0.0, 22.0
CEIL = 3.6
PLAT = 0.45                     # the pharmacy platform's floor height

# pharmacy and office
RX_X0, RX_X1 = -6.1, 6.1        # partition centre lines
RX_Y = 15.8                     # platform front edge (the counter stands just S of it)
OF_X0 = 1.7                     # office W wall centre line (E wall = RX_X1)
OF_Y = 18.5                     # office S wall centre line (N = the store's N wall)

COL_WALL = (0.84, 0.85, 0.83, 1.0)
COL_WHITE = (0.94, 0.94, 0.92, 1.0)        # the office: "whitewalled"
COL_BASE = (0.30, 0.31, 0.32, 1.0)
COL_FLOOR = (0.80, 0.79, 0.74, 1.0)        # speckled VCT
COL_SEAM = (0.70, 0.69, 0.64, 1.0)
COL_CEIL = (0.90, 0.90, 0.88, 1.0)
COL_STEEL = (0.70, 0.71, 0.72, 1.0)
COL_DARK = (0.22, 0.23, 0.25, 1.0)
COL_LAM = (0.86, 0.85, 0.82, 1.0)          # counter laminate
COL_LAM_DK = (0.42, 0.44, 0.48, 1.0)
COL_RED = (0.78, 0.14, 0.14, 1.0)          # the chain's red
COL_GREEN = (0.16, 0.46, 0.32, 1.0)
COL_GLINT = (0.84, 0.88, 0.92, 1.0)        # the pipeline has no alpha: glass is drawn as glints on an open frame
COL_PAPER = (0.95, 0.95, 0.92, 1.0)
COL_ASPHALT = (0.24, 0.24, 0.25, 1.0)
COL_CONCRETE = (0.66, 0.65, 0.62, 1.0)
COL_STRIPE = (0.92, 0.92, 0.86, 1.0)

BRAND = [(0.80, 0.18, 0.14, 1.0), (0.16, 0.30, 0.62, 1.0), (0.94, 0.74, 0.16, 1.0),
         (0.24, 0.50, 0.26, 1.0), (0.44, 0.20, 0.46, 1.0), (0.90, 0.46, 0.14, 1.0),
         (0.86, 0.84, 0.80, 1.0), (0.20, 0.56, 0.70, 1.0)]

LEVELS = (0.25, 0.62, 0.99, 1.36)           # gondola shelf plates; top 1.74
RUN_Y0, RUN_Y1 = 6.0, 13.0                  # the aisle runs
RUN_XS = (-9.0, -6.0, -3.0, 0.0, 3.0, 6.0, 9.0)
RUN_DEPTH = 0.90
AISLES = (                                   # (sign, plan for the W face, plan for the E face)
    ("CANDY & SNACKS", None, None),
    ("HOUSEHOLD", "tissue", "jug"),
    ("HAIR CARE", "shampoo", "shampoo"),
    ("COSMETICS", "cosmetics", "cosmetics"),
    ("VITAMINS", "vitamins", "vitamins"),
    ("PAIN & COLD", "meds", "meds"),
    ("FIRST AID", "meds", "tubes"),
)


# ── merchandise for a drugstore: one facing of one product along a shelf
def _P(axis, front, sgn, u, d, z):
    """u along the run, d metres back from the shelf's front edge."""
    if axis == 'Y':
        return (front - sgn * d, u, z)
    return (u, front - sgn * d, z)


def _S(axis, along, depth, h):
    return (depth, along, h) if axis == 'Y' else (along, depth, h)


def _sbox(name, center, size, color):
    """Packages stay sharp-edged (merch.py: the auto-chamfer tripled a stocked store's vertices)."""
    return make_box(name, center, size, color, chamfer=0.0)


def _scyl(name, center, radius, height, color, segments=8, axis='Z'):
    return make_cyl(name, center, radius, height, color, segments=min(segments, 8), axis=axis)


def facing(tag, kind, a0, width, front, sgn, z0, k, axis='Y'):
    def fit(pitch):
        n = max(1, int((width + 0.001) / pitch))
        return n, a0 + (width - n * pitch) / 2.0 + pitch / 2.0
    body = BRAND[k % len(BRAND)]
    band = BRAND[(k + 3) % len(BRAND)]
    if kind == "meds":                     # cartons with a white front panel
        n, s = fit(0.10)
        for i in range(n):
            u = s + i * 0.10
            h = 0.15 + 0.03 * ((i + k) % 2)
            c = BRAND[(k + i // 3) % len(BRAND)]
            _sbox(f"{tag}_Med_{i}", _P(axis, front, sgn, u, 0.06, z0 + h / 2.0), _S(axis, 0.09, 0.11, h), c)
            _sbox(f"{tag}_Med_{i}_Panel", _P(axis, front, sgn, u, 0.003, z0 + h * 0.55), _S(axis, 0.07, 0.004, h * 0.35), COL_PAPER)
    elif kind == "vitamins":               # white bottles with coloured caps and labels
        n, s = fit(0.09)
        for i in range(n):
            u = s + i * 0.09
            c = BRAND[(k + i // 4) % len(BRAND)]
            _scyl(f"{tag}_Vit_{i}", _P(axis, front, sgn, u, 0.05, z0 + 0.07), 0.038, 0.14, COL_PAPER if i % 2 else c, segments=8)
            _scyl(f"{tag}_Vit_{i}_Cap", _P(axis, front, sgn, u, 0.05, z0 + 0.1525), 0.030, 0.025, c if i % 2 else COL_PAPER, segments=8)
    elif kind == "shampoo":                # tall flat bottles with flip caps
        n, s = fit(0.09)
        for i in range(n):
            u = s + i * 0.09
            c = BRAND[(k + i // 3) % len(BRAND)]
            _sbox(f"{tag}_Sham_{i}", _P(axis, front, sgn, u, 0.04, z0 + 0.12), _S(axis, 0.08, 0.05, 0.24), c)
            _scyl(f"{tag}_Sham_{i}_Cap", _P(axis, front, sgn, u, 0.04, z0 + 0.26), 0.022, 0.04, COL_PAPER, segments=6)
    elif kind == "tissue":                 # tissue boxes and paper-towel packs
        n, s = fit(0.25)
        for i in range(n):
            u = s + i * 0.25
            for st in range(2):
                _sbox(f"{tag}_Tis_{i}_{st}", _P(axis, front, sgn, u, 0.07, z0 + 0.065 + st * 0.13),
                         _S(axis, 0.24, 0.12, 0.125), BRAND[(k + i + st) % len(BRAND)])
            _sbox(f"{tag}_Tis_{i}_Slot", _P(axis, front, sgn, u, 0.07, z0 + 0.258), _S(axis, 0.10, 0.04, 0.004), COL_PAPER)
    elif kind == "jug":                    # detergent jugs
        n, s = fit(0.22)
        for i in range(n):
            u = s + i * 0.22
            c = ((0.94, 0.52, 0.12, 1.0), (0.20, 0.40, 0.80, 1.0), (0.30, 0.66, 0.36, 1.0))[(k + i // 2) % 3]
            _sbox(f"{tag}_Jug_{i}", _P(axis, front, sgn, u, 0.09, z0 + 0.14), _S(axis, 0.18, 0.14, 0.28), c)
            _scyl(f"{tag}_Jug_{i}_Cap", _P(axis, front, sgn, u + 0.05, 0.09, z0 + 0.295), 0.03, 0.03, COL_PAPER, segments=6)
    elif kind == "cosmetics":              # one tall blister card per column, the item in its bubble
        n, s = fit(0.09)
        for i in range(n):
            u = s + i * 0.09
            c = ((0.84, 0.30, 0.42, 1.0), (0.62, 0.20, 0.24, 1.0), (0.92, 0.72, 0.62, 1.0), (0.30, 0.20, 0.18, 1.0))[(k + i) % 4]
            _sbox(f"{tag}_Cos_{i}", _P(axis, front, sgn, u, 0.03, z0 + 0.12), _S(axis, 0.075, 0.03, 0.24), COL_PAPER)
            _sbox(f"{tag}_Cos_{i}_Item", _P(axis, front, sgn, u, 0.0, z0 + 0.10), _S(axis, 0.035, 0.012, 0.12), c)
    elif kind == "tubes":                  # ointment tubes and bandage boxes
        n, s = fit(0.12)
        for i in range(n):
            u = s + i * 0.12
            _sbox(f"{tag}_Band_{i}", _P(axis, front, sgn, u, 0.05, z0 + 0.06), _S(axis, 0.11, 0.08, 0.12),
                     (0.92, 0.88, 0.80, 1.0) if (i + k) % 2 else (0.20, 0.42, 0.72, 1.0))
            _sbox(f"{tag}_Band_{i}_Stripe", _P(axis, front, sgn, u, 0.008, z0 + 0.09), _S(axis, 0.11, 0.004, 0.025), COL_RED)
    elif kind == "stockbottle":            # the pharmacy's stock: white HDPE and amber bottles
        n, s = fit(0.075)
        for i in range(n):
            u = s + i * 0.075
            amber = (i + k) % 5 == 2
            h = 0.11 + 0.03 * ((i * 3 + k) % 3)
            _scyl(f"{tag}_Rx_{i}", _P(axis, front, sgn, u, 0.045, z0 + h / 2.0), 0.032, h,
                     (0.62, 0.36, 0.12, 1.0) if amber else COL_PAPER, segments=8)
            _scyl(f"{tag}_Rx_{i}_Cap", _P(axis, front, sgn, u, 0.045, z0 + h + 0.01), 0.030, 0.02, COL_PAPER if amber else BRAND[(k + i) % len(BRAND)], segments=8)


def gondola(prefix, cx, y0, y1, plans, *, sides=(-1, 1), levels=LEVELS, depth=RUN_DEPTH, seed=0, wall=False):
    """A run along Y. sides: -1 faces W, +1 faces E. plans: {side: kind}."""
    length = y1 - y0
    cy = (y0 + y1) / 2.0
    half = depth / 2.0
    top = max(levels) + 0.38
    if wall:   # single-sided against a wall: the base and spine at the back
        make_box(f"{prefix}_Base", (cx, cy, 0.10), (half, length, 0.20), COL_DARK)
        make_box(f"{prefix}_Back", (cx - sides[0] * (half / 2.0 - 0.02), cy, top / 2.0), (0.04, length, top), COL_STEEL)
    else:
        make_box(f"{prefix}_Base", (cx, cy, 0.10), (depth, length, 0.20), COL_DARK)
        make_box(f"{prefix}_Shelving_Spine", (cx, cy, (0.20 + top) / 2.0), (0.06, length, top - 0.20), COL_STEEL)
    nsec = max(1, int(round(length / 0.50)))
    w = length / nsec
    for sh, z in enumerate(levels):
        for sgn in sides:
            if wall:
                back = cx - sgn * (half / 2.0 - 0.04)
                front = cx + sgn * (half / 2.0)
                mid = (back + front) / 2.0
                make_box(f"{prefix}_Shelf_{sh}_x{sgn:+d}", (mid, cy, z), (abs(front - back), length, 0.03), COL_STEEL)
            else:
                front = cx + sgn * half
                make_box(f"{prefix}_Shelf_{sh}_x{sgn:+d}", (cx + sgn * (half + 0.03) / 2.0, cy, z), (half - 0.03, length, 0.03), COL_STEEL)
            make_box(f"{prefix}_PriceStrip_{sh}_x{sgn:+d}", (front + sgn * 0.003, cy, z), (0.006, length, 0.04), COL_PAPER)
            kind = plans[sgn]
            for p in range(nsec):
                a0 = y0 + p * w
                facing(f"{prefix}_Stock_{sh}_x{sgn:+d}_{p}", kind, a0 + 0.01, w - 0.02, front, sgn, z + 0.015,
                       seed * 13 + sh * 7 + p + (3 if sgn > 0 else 0), axis='Y')
    if not wall:
        for e in (-1, 1):
            make_box(f"{prefix}_End_Panel_{e:+d}", (cx, cy + e * (length / 2.0 + 0.02), top / 2.0), (depth, 0.04, top), COL_STEEL)
    return top


def endcap(prefix, cx, y_back, kind, seed):
    """An endcap facing S against a run's S end panel (y_back = the panel's S face)."""
    d = 0.45
    cy = y_back - d / 2.0
    make_box(f"{prefix}_Base", (cx, cy, 0.10), (RUN_DEPTH, d, 0.20), COL_DARK)
    for sh, z in enumerate(LEVELS[:3]):
        make_box(f"{prefix}_Shelf_{sh}", (cx, cy, z), (RUN_DEPTH, d, 0.03), COL_STEEL)
        make_box(f"{prefix}_PriceStrip_{sh}", (cx, y_back - d - 0.003, z), (RUN_DEPTH, 0.006, 0.04), COL_PAPER)
        facing(f"{prefix}_Stock_{sh}", kind, cx - RUN_DEPTH / 2.0 + 0.02, RUN_DEPTH - 0.04, y_back - d, -1, z + 0.015,
               seed + sh, axis='X')
    for e in (-1, 1):
        make_box(f"{prefix}_Side_{e:+d}", (cx + e * (RUN_DEPTH / 2.0 + 0.015), cy, 0.80), (0.03, d, 1.60), COL_STEEL)
    make_box(f"{prefix}_Header", (cx, y_back - d + 0.02, 1.70), (RUN_DEPTH + 0.06, 0.03, 0.22), COL_RED)
    make_box(f"{prefix}_Header_Sale", (cx, y_back - d + 0.004, 1.70), (0.50, 0.004, 0.10), COL_PAPER)


def _hanging_sign(prefix, cx, cy, w, h, z, col, along='X', text_col=COL_PAPER):
    size = (w, 0.03, h) if along == 'X' else (0.03, w, h)
    make_box(prefix, (cx, cy, z), size, col)
    tsize = (w * 0.7, 0.034, h * 0.30) if along == 'X' else (0.034, w * 0.7, h * 0.30)
    make_box(f"{prefix}_Text", (cx, cy, z), tsize, text_col)
    for s in (-1, 1):
        off = (s * w * 0.4, 0.0) if along == 'X' else (0.0, s * w * 0.4)
        make_cyl(f"{prefix}_Wire_{s:+d}", (cx + off[0], cy + off[1], (z + h / 2.0 + CEIL) / 2.0), 0.004,
                 CEIL - (z + h / 2.0), COL_STEEL, segments=4)


# ═══════════════════════════════════════════════════════════════ the shell
def build_shell():
    make_floor("Floor", (0.0, (Y0 + Y1) / 2.0, 0.0), size_x=X1 - X0 + 0.4, size_y=Y1 - Y0 + 0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    make_wall("Wall_W", (X0, (Y0 + Y1) / 2.0, 0), length=Y1 - Y0 + 0.4, height=CEIL, axis='Y', palette=pal, baseboard_face_sign=+1)
    make_wall("Wall_E", (X1, (Y0 + Y1) / 2.0, 0), length=Y1 - Y0 + 0.4, height=CEIL, axis='Y', palette=pal, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_N", (0.0, Y1, 0), length=X1 - X0 + 0.4, height=CEIL, axis='X', palette=pal,
                            baseboard_face_sign=-1, openings=[(9.0, 1.05, 0.95, 2.10), (11.6, 1.05, 0.95, 2.10)])
    # the storefront: the entry (sliding doors) and two long bands of glass
    make_wall_with_openings("Wall_S", (0.0, Y0, 0), length=X1 - X0 + 0.4, height=CEIL, axis='X', palette=pal,
                            baseboard_face_sign=+1,
                            openings=[(-9.0, 1.25, 2.40, 2.50), (-3.4, 1.60, 6.4, 2.40), (6.4, 1.60, 9.6, 2.40)])
    make_ceiling("Ceil", (0.0, (Y0 + Y1) / 2.0, CEIL), size_x=X1 - X0 + 0.4, size_y=Y1 - Y0 + 0.4,
                 with_grid=True, with_stains=False, palette={"tile": COL_CEIL})
    # storefront glass and mullions, set in the cuts
    for k, (cx, w) in enumerate(((-3.4, 6.4), (6.4, 9.6))):
        for gi, (go, gw) in enumerate(((-0.18, 0.03), (-0.12, 0.012))):
            make_box(f"Front_Glass_{k}_Glint_{gi}", (cx + go * w, Y0 + 0.045, 1.60), (gw, 0.004, 2.38), COL_GLINT)
        n = int(round(w / 1.6))
        for m in range(n + 1):
            make_box(f"Front_Mullion_{k}_{m}", (cx - w / 2.0 + m * w / n, Y0, 1.60), (0.06, 0.10, 2.40), COL_DARK)
        make_box(f"Front_Sill_{k}", (cx, Y0 + 0.06, 0.41), (w, 0.14, 0.02), COL_DARK)
    # the automatic doors, both leaves slid half open, in their frame
    make_box("Entry_Header", (-9.0, Y0, 2.55), (2.60, 0.24, 0.12), COL_DARK)
    make_box("Entry_Operator", (-9.0, Y0 + 0.16, 2.70), (2.60, 0.16, 0.20), COL_STEEL)
    for s in (-1, 1):
        make_box(f"Entry_Jamb_{s:+d}", (-9.0 + s * 1.23, Y0, 1.25), (0.06, 0.20, 2.50), COL_DARK)
        sx = -9.0 + s * 0.85
        for e in (-1, 1):   # stiles and rails round the pane (a solid board behind glass reads as a wall)
            make_box(f"Entry_Slider_{s:+d}_Stile_{e:+d}", (sx + e * 0.30, Y0 + 0.06, 1.24), (0.06, 0.05, 2.46), COL_DARK)
        make_box(f"Entry_Slider_{s:+d}_Rail_Top", (sx, Y0 + 0.06, 2.43), (0.54, 0.05, 0.08), COL_DARK)
        make_box(f"Entry_Slider_{s:+d}_Rail_Bottom", (sx, Y0 + 0.06, 0.07), (0.54, 0.05, 0.14), COL_DARK)
        make_box(f"Entry_Slider_{s:+d}_Glint", (sx - 0.12, Y0 + 0.06, 1.25), (0.02, 0.004, 2.22), COL_GLINT)
    make_box("Entry_Mat", (-9.0, 1.10, 0.005), (2.40, 1.80, 0.01), (0.20, 0.22, 0.24, 1.0))
    # the outside: the walk, the lot, the street past it
    make_box("Out_Walk", (0.0, -1.5, -0.03), (X1 - X0 + 8.0, 3.0, 0.06), COL_CONCRETE)
    make_box("Out_Curb", (0.0, -3.05, 0.02), (X1 - X0 + 8.0, 0.15, 0.14), (0.60, 0.59, 0.56, 1.0))
    make_box("Out_Lot", (0.0, -14.5, -0.04), (X1 - X0 + 20.0, 23.0, 0.06), COL_ASPHALT)
    for k in range(13):
        sx = -12.0 + k * 2.75
        make_box(f"Out_Stall_{k}", (sx, -6.6, -0.005), (0.10, 5.0, 0.01), COL_STRIPE)
        make_box(f"Out_Stall_B_{k}", (sx, -16.4, -0.005), (0.10, 5.0, 0.01), COL_STRIPE)
    make_box("Out_Fire_Lane", (0.0, -3.6, -0.006), (X1 - X0 + 8.0, 0.12, 0.01), (0.92, 0.80, 0.20, 1.0))
    make_car("Out_Car_0", -7.9, -6.4, 4.6, (0.66, 0.68, 0.70, 1.0), along="Y")
    make_car("Out_Car_1", 3.1, -6.6, 4.5, (0.58, 0.12, 0.12, 1.0), along="Y", hatch=True)
    make_car("Out_Car_2", 11.35, -16.2, 5.2, (0.16, 0.20, 0.30, 1.0), along="Y", pickup=True)
    make_car("Out_Car_3", -2.4, -16.4, 4.6, (0.86, 0.86, 0.84, 1.0), along="Y")
    for k, lx in enumerate((-8.0, 8.0)):
        make_cyl(f"Out_Lot_Light_{k}_Pole", (lx, -11.5, 0.0 + 3.5), 0.10, 7.0, (0.46, 0.46, 0.48, 1.0), segments=6)
        make_box(f"Out_Lot_Light_{k}_Head", (lx, -11.5, 7.05), (0.80, 0.40, 0.14), (0.40, 0.40, 0.42, 1.0))
        make_box(f"Out_Lot_Light_{k}_Base", (lx, -11.5, 0.30), (0.50, 0.50, 0.60), COL_CONCRETE)
    # the cart corral out in the lot
    for s in (-1, 1):
        make_box(f"Out_Corral_Rail_{s:+d}", (6.0 + s * 0.55, -11.5, 0.95), (0.05, 3.0, 0.05), COL_STEEL)
        for k in range(3):
            make_cyl(f"Out_Corral_Post_{s:+d}_{k}", (6.0 + s * 0.55, -12.9 + k * 1.4, 0.475), 0.025, 0.95, COL_STEEL, segments=6)
    make_view("View_S", "S", -26.0, 0.0, kind="street", ground_z=0.0, seed=26)


def build_lights():
    """2x4 troffers in rows over the floor; the practicals sit on a subset."""
    for i, fx in enumerate((-10.5, -6.0, -1.5, 3.0, 7.5, 11.0)):
        for j, fy in enumerate((2.5, 6.8, 10.4, 13.8)):
            make_fluorescent_tube_fixture(f"Fluor_{i}_{j}", (fx, fy, CEIL), length=1.20, width=0.60)
    for j, fy in enumerate((17.0, 20.2)):
        for i, fx in enumerate((-4.0, -0.5)):
            make_fluorescent_tube_fixture(f"Fluor_Rx_{i}_{j}", (fx, fy, CEIL), length=1.20, width=0.60)
    make_fluorescent_tube_fixture("Fluor_Rx_Gate", (4.0, 17.0, CEIL), length=1.20, width=0.60)
    make_fluorescent_tube_fixture("Fluor_Office", (3.9, 20.2, CEIL), length=1.20, width=0.60)
    for i, fx in enumerate((-9.5, 9.5)):
        make_fluorescent_tube_fixture(f"Fluor_Back_{i}", (fx, 18.5, CEIL), length=1.20, width=0.60)


# ═══════════════════════════════════════════════════════════ the floor
def build_aisles():
    for k, gx in enumerate(RUN_XS):
        sign, pw, pe = AISLES[k]
        if pw is None:
            stock_gondola(f"Aisle_{k}", (gx, (RUN_Y0 + RUN_Y1) / 2.0, 0.0), length=RUN_Y1 - RUN_Y0, levels=LEVELS,
                          plan="candy", seed=k * 5, axis='Y', depth=RUN_DEPTH, base_col=COL_DARK, metal=COL_STEEL,
                          tag_col=COL_PAPER, lean=True)
        else:
            gondola(f"Aisle_{k}", gx, RUN_Y0, RUN_Y1, {-1: pw, +1: pe}, seed=k * 5)
        endcap(f"Endcap_{k}", gx, RUN_Y0 - 0.04, ("meds", "tissue", "shampoo", "vitamins", "vitamins", "meds", "tubes")[k], k * 3)
    # the hanging aisle signs, one over each lane between runs
    for k in range(len(RUN_XS) - 1):
        lx = (RUN_XS[k] + RUN_XS[k + 1]) / 2.0
        _hanging_sign(f"Aisle_Sign_{k}", lx, 9.5, 1.30, 0.40, 2.85, COL_RED, along='X')
    # wall bays, both side walls, S of the coolers
    gondola("WallBay_W", X0 + 0.10 + 0.30, 1.8, 13.4, {+1: "meds"}, sides=(+1,), depth=1.20, seed=40, wall=True)
    gondola("WallBay_E", X1 - 0.10 - 0.30, 3.4, 13.4, {-1: "cosmetics"}, sides=(-1,), depth=1.20, seed=44, wall=True)
    make_box("WallBay_W_Header", (X0 + 0.11, 7.6, 2.30), (0.02, 11.6, 0.30), COL_RED)
    make_box("WallBay_E_Header", (X1 - 0.11, 8.4, 2.30), (0.02, 10.0, 0.30), COL_RED)
    # the coolers, NW: five doors in the N wall W of the pharmacy
    wall_y = Y1 - 0.10 - 0.50
    for i, cx in enumerate((-12.2, -10.9, -9.6, -8.3, -7.0)):
        make_cooler_door(f"Cooler_{i}", (cx, wall_y, 1.30), stock=("dairy" if i < 2 else "beverage"), seed=i)
    make_box("Cooler_Header", (-9.6, wall_y - 0.02, 2.60), (6.5, 0.04, 0.24), COL_RED)
    make_box("Cooler_Soffit", (-9.6, wall_y + 0.25, (2.72 + CEIL) / 2.0), (6.6, 0.70, CEIL - 2.72), COL_WALL)


def build_front():
    """The registers, the impulse racks, the baskets, the promo table."""
    for k, rx in enumerate((-5.6, -2.6)):
        # the register stand: a counter running N-S, cashier on the E side
        make_box(f"Register_{k}_Counter", (rx, 2.6, 0.48), (0.70, 2.40, 0.96), COL_LAM_DK)
        make_box(f"Register_{k}_Counter_Top", (rx, 2.6, 0.98), (0.80, 2.50, 0.04), COL_LAM)
        make_box(f"Register_{k}_Kick", (rx, 2.6, 0.05), (0.72, 2.42, 0.10), COL_DARK)
        make_box(f"Register_{k}_Till", (rx + 0.12, 3.1, 1.06), (0.36, 0.40, 0.12), COL_DARK)
        make_rot_box(f"Register_{k}_Screen", (rx + 0.20, 3.1, 1.30), (0.04, 0.34, 0.26), COL_DARK, pitch=0.0, roll=-0.25)
        make_cyl(f"Register_{k}_Screen_Post", (rx + 0.20, 3.1, 1.14), 0.02, 0.16, COL_STEEL, segments=6)
        make_box(f"Register_{k}_Terminal", (rx - 0.25, 2.8, 1.06), (0.10, 0.16, 0.12), COL_DARK)
        make_box(f"Register_{k}_Bags", (rx + 0.08, 1.65, 1.10), (0.40, 0.30, 0.20), COL_PAPER)
        make_box(f"Register_{k}_Lane_Number", (rx, 2.6, 2.50), (0.30, 0.04, 0.30), COL_RED)
        make_cyl(f"Register_{k}_Lane_Number_Post", (rx, 2.6, 1.70), 0.02, 1.40, COL_STEEL, segments=6)
        # the impulse rack on the customer (W) side of each stand
        make_box(f"Impulse_{k}_Base", (rx - 0.62, 2.6, 0.10), (0.40, 1.60, 0.20), COL_DARK)
        make_box(f"Impulse_{k}_Back", (rx - 0.44, 2.6, 0.75), (0.04, 1.60, 1.30), COL_STEEL)
        for sh, z in enumerate((0.40, 0.75, 1.10)):
            make_box(f"Impulse_{k}_Shelf_{sh}", (rx - 0.62, 2.6, z), (0.36, 1.60, 0.03), COL_STEEL)
            facing(f"Impulse_{k}_Stock_{sh}", ("cosmetics", "tubes", "vitamins")[sh], 1.82, 1.56, rx - 0.80, -1,
                   z + 0.015, k * 5 + sh, axis='Y')
    # the basket stack and the security pedestals at the entry
    make_box("Basket_Stand", (-11.6, 1.2, 0.10), (0.50, 0.40, 0.20), COL_DARK)
    for b in range(6):
        make_box(f"Basket_{b}", (-11.6, 1.2, 0.23 + b * 0.06), (0.46, 0.34, 0.06), COL_RED)
    for s in (-1, 1):
        make_box(f"Entry_Sensor_{s:+d}", (-9.0 + s * 1.30, 1.6, 0.80), (0.08, 0.50, 1.60), (0.86, 0.86, 0.84, 1.0))
        make_box(f"Entry_Sensor_{s:+d}_Foot", (-9.0 + s * 1.30, 1.6, 0.02), (0.20, 0.60, 0.04), COL_DARK)
    # the promo table between the registers and the aisles
    make_box("Promo_Table_Top", (1.5, 3.6, 0.76), (1.60, 0.80, 0.04), (0.74, 0.62, 0.44, 1.0))
    for i, (lx, ly) in enumerate(((-0.72, -0.32), (0.72, -0.32), (-0.72, 0.32), (0.72, 0.32))):
        make_box(f"Promo_Table_Leg_{i}", (1.5 + lx, 3.6 + ly, 0.37), (0.05, 0.05, 0.74), (0.60, 0.50, 0.36, 1.0))
    for i in range(5):
        for st in range(3 - i % 2):
            make_box(f"Promo_Box_{i}_{st}", (0.95 + i * 0.28, 3.6 + 0.12 * ((i % 2) - 0.5), 0.84 + st * 0.12),
                     (0.24, 0.24, 0.12), BRAND[(i + st) % len(BRAND)])
    make_box("Promo_Sign", (1.5, 3.93, 0.96), (0.60, 0.02, 0.36), COL_RED)
    make_box("Promo_Sign_Text", (1.5, 3.918, 0.98), (0.44, 0.004, 0.12), COL_PAPER)
    # the magazine rack under the front glass, the photo kiosk on the E
    make_box("Magazine_Rack_Base", (5.6, 0.55, 0.15), (2.40, 0.50, 0.30), COL_DARK)
    make_box("Magazine_Rack_Back", (5.6, 0.82, 0.80), (2.40, 0.04, 1.00), COL_STEEL)
    for t in range(3):
        z = 0.50 + t * 0.28
        make_box(f"Magazine_Rack_Tier_{t}", (5.6, 0.69, z), (2.40, 0.22, 0.02), COL_STEEL)
        for m in range(8):
            make_rot_box(f"Magazine_Rack_Stock_{t}_{m}", (4.6 + m * 0.285, 0.74, z + 0.15),
                         (0.21, 0.01, 0.28), BRAND[(m + t * 3) % len(BRAND)], roll=0.0)
    make_box("Photo_Kiosk_Body", (11.6, 1.6, 0.55), (0.70, 0.60, 1.10), COL_DARK)
    make_rot_box("Photo_Kiosk_Screen", (11.6, 1.31, 1.30), (0.56, 0.04, 0.40), (0.30, 0.46, 0.66, 1.0), pitch=0.0, roll=0.0)
    make_box("Photo_Kiosk_Sign", (11.6, 1.6, 2.35), (0.90, 0.04, 0.30), (0.20, 0.42, 0.72, 1.0))
    make_cyl("Photo_Kiosk_Sign_Post", (11.6, 1.6, 1.65), 0.02, 1.10, COL_STEEL, segments=6)


# ═════════════════════════════════════════════════════════ the pharmacy
def build_pharmacy():
    pal_w = {"wall": COL_WHITE, "baseboard": COL_BASE}
    # the platform and its two steps up at the gate
    make_box("RX_Platform", (0.0, (RX_Y + Y1 - 0.10) / 2.0, PLAT / 2.0), (RX_X1 - RX_X0, Y1 - 0.10 - RX_Y, PLAT), (0.72, 0.71, 0.67, 1.0))
    make_box("RX_Step_0", (5.30, RX_Y - 0.45, 0.075), (0.90, 0.30, 0.15), (0.72, 0.71, 0.67, 1.0))
    make_box("RX_Step_1", (5.30, RX_Y - 0.15, 0.15), (0.90, 0.30, 0.30), (0.72, 0.71, 0.67, 1.0))
    # the side partitions
    make_wall("RX_Wall_W", (RX_X0, (RX_Y + Y1) / 2.0, 0), length=Y1 - RX_Y, height=CEIL, axis='Y', palette=pal_w, baseboard_face_sign=+1)
    make_wall("RX_Wall_E", (RX_X1, (RX_Y + Y1) / 2.0, 0), length=Y1 - RX_Y, height=CEIL, axis='Y', palette=pal_w, baseboard_face_sign=-1)
    # the counter: "the front table" — on the main floor, waist height from the platform
    cx0, cx1 = RX_X0 + 0.10, 4.75
    ccx = (cx0 + cx1) / 2.0
    make_box("RX_Counter", (ccx, RX_Y - 0.32, 0.535), (cx1 - cx0, 0.60, 1.07), COL_LAM_DK)
    make_box("RX_Counter_Top", (ccx, RX_Y - 0.25, 1.09), (cx1 - cx0, 0.78, 0.04), COL_LAM)
    make_box("RX_Counter_Kick", (ccx, RX_Y - 0.64, 0.05), (cx1 - cx0, 0.04, 0.10), COL_DARK)
    # the gate in the gap E of the counter
    make_box("RX_Gate", (5.30, RX_Y + 0.02, PLAT + 0.50), (0.86, 0.04, 1.00), COL_LAM_DK)
    make_box("RX_Gate_Post", (5.78, RX_Y + 0.02, PLAT + 0.50), (0.06, 0.06, 1.00), COL_STEEL)
    # the soffit and its fascia over the counter
    make_box("RX_Soffit", (0.0, RX_Y - 0.30, (2.90 + CEIL) / 2.0), (RX_X1 - RX_X0 + 0.20, 0.80, CEIL - 2.90), COL_WHITE)
    make_box("RX_Fascia_Band", (0.0, RX_Y - 0.71, 3.22), (RX_X1 - RX_X0 + 0.20, 0.02, 0.44), COL_RED)
    for i in range(8):                                   # P H A R M A C Y
        make_box(f"RX_Fascia_Letter_{i}", (-1.75 + i * 0.50, RX_Y - 0.725, 3.22), (0.30, 0.01, 0.30), COL_PAPER)
    make_box("RX_Fascia_Cross_V", (-3.0, RX_Y - 0.725, 3.22), (0.10, 0.01, 0.32), COL_PAPER)
    make_box("RX_Fascia_Cross_H", (-3.0, RX_Y - 0.725, 3.22), (0.32, 0.01, 0.10), COL_PAPER)
    # the three stations, each with its hanging sign
    for name, sx in (("DropOff", -3.6), ("PickUp", 1.0), ("Consult", 3.7)):
        make_box(f"RX_Sign_{name}", (sx, RX_Y - 0.50, 2.62), (1.10, 0.03, 0.30), COL_GREEN)
        make_box(f"RX_Sign_{name}_Text", (sx, RX_Y - 0.517, 2.62), (0.76, 0.004, 0.10), COL_PAPER)
        make_box(f"RX_Sign_{name}_Bracket", (sx, RX_Y - 0.50, 2.835), (0.80, 0.02, 0.13), COL_STEEL)
    top = 1.11
    # DROP OFF: the tray, the clipboard, the pen
    make_box("RX_DropOff_Tray", (-3.6, RX_Y - 0.30, top + 0.03), (0.34, 0.26, 0.06), COL_DARK)
    make_box("RX_DropOff_Clipboard", (-3.15, RX_Y - 0.42, top + 0.006), (0.23, 0.32, 0.012), (0.56, 0.42, 0.26, 1.0))
    make_box("RX_DropOff_Form", (-3.15, RX_Y - 0.42, top + 0.014), (0.21, 0.28, 0.004), COL_PAPER)
    # PICK UP: the register on the pharmacist's side, the card reader on the customer's, a bag waiting
    make_box("RX_PickUp_Till", (1.0, RX_Y - 0.06, top + 0.06), (0.36, 0.34, 0.12), COL_DARK)
    make_rot_box("RX_PickUp_Screen", (1.0, RX_Y + 0.02, top + 0.32), (0.34, 0.04, 0.26), COL_DARK, pitch=0.0, roll=0.0)
    make_cyl("RX_PickUp_Screen_Post", (1.0, RX_Y + 0.02, top + 0.15), 0.02, 0.06, COL_STEEL, segments=6)
    make_box("RX_PickUp_Terminal", (0.55, RX_Y - 0.50, top + 0.06), (0.10, 0.16, 0.12), COL_DARK)
    make_box("RX_PickUp_Bag", (1.45, RX_Y - 0.38, top + 0.13), (0.22, 0.14, 0.26), COL_PAPER)
    make_box("RX_PickUp_Bag_Label", (1.45, RX_Y - 0.452, top + 0.16), (0.12, 0.004, 0.06), (0.86, 0.86, 0.50, 1.0))
    make_cyl("RX_PickUp_Pen_Cup", (0.30, RX_Y - 0.35, top + 0.05), 0.04, 0.10, COL_DARK, segments=8)
    # CONSULTATION: the two frosted panels that make it private
    for s in (-1, 1):
        make_box(f"RX_Consult_Panel_{s:+d}", (3.7 + s * 0.55, RX_Y - 0.25, top + 0.36), (0.03, 0.70, 0.70), (0.80, 0.86, 0.88, 0.55))
    # the customer-side lip of the counter: cough drops and lip balm
    make_box("RX_Lip_Shelf", (-1.3, RX_Y - 0.70, 0.95), (3.00, 0.16, 0.03), COL_STEEL)
    facing("RX_Lip_Shelf_Stock", "tubes", -2.75, 2.90, RX_Y - 0.78, -1, 0.965, 17, axis='X')
    # the will-call rack behind PICK UP: rows of white bags on rods
    wy = 17.15
    for p in (-2.4, 0.2):
        make_box(f"WillCall_Post_{p:+.1f}", (p, wy, PLAT + 0.95), (0.05, 0.05, 1.90), COL_STEEL)
    for r in range(4):
        z = PLAT + 0.60 + r * 0.40
        make_cyl(f"WillCall_Rod_{r}", (-1.1, wy, z), 0.012, 2.60, COL_STEEL, segments=6, axis='X')
        for b in range(16):
            if (b * 7 + r * 3) % 11 == 4:
                continue
            _sbox(f"WillCall_Stock_{r}_{b}", (-2.25 + b * 0.155, wy, z - 0.16), (0.13, 0.08, 0.30),
                     COL_PAPER if (b + r) % 5 else (0.90, 0.88, 0.70, 1.0))
    # the work island: counting trays, screens, the label printer — and the lunch
    ix0, ix1, iy = -4.6, 0.8, 19.2
    icx = (ix0 + ix1) / 2.0
    make_box("RX_Island", (icx, iy, PLAT + 0.45), (ix1 - ix0, 0.76, 0.90), COL_LAM_DK)
    make_box("RX_Island_Top", (icx, iy, PLAT + 0.92), (ix1 - ix0 + 0.06, 0.84, 0.04), COL_LAM)
    it = PLAT + 0.94
    for k, tx in enumerate((-4.1, -2.6)):
        make_box(f"RX_Tray_{k}", (tx, iy - 0.18, it + 0.01), (0.26, 0.18, 0.02), (0.34, 0.56, 0.74, 1.0))
        make_box(f"RX_Tray_{k}_Spatula", (tx + 0.05, iy - 0.18, it + 0.025), (0.18, 0.025, 0.006), COL_STEEL)
        make_box(f"RX_Monitor_{k}", (tx, iy + 0.22, it + 0.30), (0.52, 0.03, 0.32), COL_DARK)
        make_box(f"RX_Monitor_{k}_Screen", (tx, iy + 0.204, it + 0.30), (0.48, 0.004, 0.28), (0.36, 0.52, 0.66, 1.0))
        make_box(f"RX_Monitor_{k}_Stand", (tx, iy + 0.26, it + 0.07), (0.20, 0.16, 0.14), COL_DARK)
        make_box(f"RX_Keyboard_{k}", (tx, iy - 0.02, it + 0.012), (0.42, 0.14, 0.024), COL_DARK)
    make_box("RX_Label_Printer", (-3.35, iy + 0.18, it + 0.09), (0.22, 0.26, 0.18), (0.86, 0.86, 0.84, 1.0))
    make_box("RX_Vial_Bin", (-1.75, iy + 0.10, it + 0.06), (0.36, 0.24, 0.12), (0.62, 0.36, 0.12, 1.0))
    for v in range(5):
        make_cyl(f"RX_Vial_Bin_Stock_{v}", (-1.90 + v * 0.07, iy + 0.10, it + 0.15), 0.025, 0.06, (0.70, 0.42, 0.14, 1.0), segments=8)
    # THE LUNCH at the island's E end: "Six eggrolls between the three of us"
    lx = 0.15
    make_box("Lunch_Bag", (lx + 0.30, iy + 0.22, it + 0.16), (0.28, 0.18, 0.32), (0.96, 0.96, 0.94, 1.0))
    make_box("Lunch_Bag_Print", (lx + 0.30, iy + 0.129, it + 0.20), (0.14, 0.004, 0.10), COL_RED)
    for k, (cx, cy) in enumerate(((lx - 0.30, iy - 0.10), (lx + 0.05, iy - 0.20), (lx + 0.36, iy - 0.14))):
        make_box(f"Lunch_Clamshell_{k}", (cx, cy, it + 0.03), (0.22, 0.22, 0.06), (0.97, 0.97, 0.95, 1.0))
        if k == 0:   # Deborah's, open: the lid stood up behind it, the eggrolls in it
            make_rot_box("Lunch_Clamshell_0_Lid", (cx, cy + 0.12, it + 0.15), (0.22, 0.02, 0.18), (0.97, 0.97, 0.95, 1.0), pitch=0.0, roll=0.0)
            for e in range(2):
                make_cyl(f"Eggroll_{e}", (cx - 0.04 + e * 0.07, cy - 0.01, it + 0.085), 0.026, 0.14, (0.78, 0.54, 0.24, 1.0), segments=8, axis='Y')
            make_cyl("Lunch_Chopstick_0", (cx + 0.02, cy - 0.04, it + 0.112), 0.004, 0.22, (0.86, 0.76, 0.56, 1.0), segments=4, axis='X')
            make_cyl("Lunch_Chopstick_1", (cx + 0.02, cy - 0.06, it + 0.112), 0.004, 0.22, (0.86, 0.76, 0.56, 1.0), segments=4, axis='X')
        else:
            make_box(f"Lunch_Clamshell_{k}_Seam", (cx, cy, it + 0.062), (0.22, 0.22, 0.004), (0.88, 0.88, 0.86, 1.0))
    for k in range(3):
        make_cyl(f"Lunch_Sauce_{k}", (lx - 0.05 + k * 0.08, iy + 0.05, it + 0.02), 0.025, 0.04, (0.94, 0.94, 0.90, 1.0), segments=8)
        make_cyl(f"Lunch_Sauce_{k}_Fill", (lx - 0.05 + k * 0.08, iy + 0.05, it + 0.0405), 0.022, 0.003, (0.78, 0.40, 0.18, 1.0), segments=8)
    # the back wall of stock: five shelves of bottles, W of the office
    bx0, bx1 = RX_X0 + 0.20, OF_X0 - 0.20
    bcx = (bx0 + bx1) / 2.0
    face = Y1 - 0.10
    sd = 0.36
    make_box("RxStock_Bay_Back", (bcx, face - 0.02, PLAT + 1.10), (bx1 - bx0, 0.04, 2.20), COL_STEEL)
    for e, ex in enumerate((bx0, bx1)):
        make_box(f"RxStock_Bay_Side_{e}", (ex, face - sd / 2.0, PLAT + 1.10), (0.03, sd, 2.20), COL_STEEL)
    for sh in range(6):
        z = PLAT + 0.12 + sh * 0.38
        make_box(f"RxStock_Bay_Shelf_{sh}", (bcx, face - sd / 2.0, z), (bx1 - bx0 - 0.03, sd - 0.04, 0.025), COL_STEEL)
        nsec = int((bx1 - bx0) / 0.6)
        w = (bx1 - bx0) / nsec
        for p in range(nsec):
            facing(f"RxStock_Stock_{sh}_{p}", "stockbottle", bx0 + p * w + 0.02, w - 0.04, face - sd + 0.02, -1,
                   z + 0.0125, sh * 5 + p, axis='X')
    # the vaccine fridge under the W end of the island's lane, the phone and the fax on the W partition
    make_box("RX_Vaccine_Fridge", (RX_X0 + 0.45, 17.4, PLAT + 0.42), (0.60, 0.60, 0.84), (0.90, 0.90, 0.88, 1.0))
    make_box("RX_Vaccine_Fridge_Door", (RX_X0 + 0.76, 17.4, PLAT + 0.42), (0.02, 0.54, 0.78), (0.80, 0.86, 0.88, 1.0))
    make_box("RX_Wall_Phone", (RX_X0 + 0.13, 18.4, PLAT + 1.40), (0.06, 0.20, 0.24), COL_DARK)
    make_wall_clock("RX_Clock", (RX_X0 + 0.10, 19.6, PLAT + 2.30), frozen_hour=12, frozen_min=10, facing='+X')


# ═══════════════════════════════════════════════════════════ the office
def build_office():
    """Faust's office: "my whitewalled fortress of solitude"."""
    pal_w = {"wall": COL_WHITE, "baseboard": (0.86, 0.86, 0.84, 1.0)}
    ox0, ox1 = OF_X0 + 0.10, RX_X1 - 0.10          # interior faces
    oy0, oy1 = OF_Y + 0.10, Y1 - 0.10
    ocx = (ox0 + ox1) / 2.0
    # the office walls stand ON the platform (a wall from the slab would sit inside it)
    wh = CEIL - PLAT
    bb = pal_w["baseboard"]
    make_box("Office_Wall_W", (OF_X0, (OF_Y + Y1) / 2.0, PLAT + wh / 2.0), (0.20, Y1 - OF_Y, wh), COL_WHITE)
    make_box("Office_Wall_W_Base", (OF_X0 + 0.106, (OF_Y + Y1) / 2.0 + 0.05, PLAT + 0.08), (0.012, Y1 - OF_Y - 0.30, 0.16), bb)
    d0, d1 = 2.55 - 0.475, 2.55 + 0.475            # the door opening
    for name, a, b in (("W", OF_X0 - 0.10, d0), ("E", d1, RX_X1 + 0.10)):
        make_box(f"Office_Wall_S_Pier_{name}", ((a + b) / 2.0, OF_Y, PLAT + wh / 2.0), (b - a, 0.20, wh), COL_WHITE)
        ra, rb = max(a, OF_X0 + 0.10), min(b, RX_X1 - 0.10)      # the room side, between the walls
        make_box(f"Office_Wall_S_Pier_{name}_Base", ((ra + rb) / 2.0, OF_Y + 0.106, PLAT + 0.08), (rb - ra, 0.012, 0.16), bb)
    make_box("Office_Wall_S_Lintel", (2.55, OF_Y, PLAT + 2.10 + (wh - 2.10) / 2.0), (d1 - d0, 0.20, wh - 2.10), COL_WHITE)
    # the door, swung open into the office against the W wall
    make_box("Office_Door", (OF_X0 + 0.13, OF_Y + 0.58, PLAT + 1.03), (0.04, 0.90, 2.04), (0.82, 0.80, 0.76, 1.0))
    make_cyl("Office_Door_Knob", (OF_X0 + 0.17, OF_Y + 0.95, PLAT + 0.98), 0.025, 0.06, COL_STEEL, segments=8, axis='X')
    make_box("Office_Door_Frame_Head", (2.55, OF_Y - 0.11, PLAT + 2.13), (1.05, 0.03, 0.06), (0.86, 0.86, 0.84, 1.0))
    # the white paint the office walls carry on their room faces (the partitions are white both sides)
    # the desk on the N wall
    dx, dy = 3.55, oy1 - 0.36
    dt = PLAT + 0.74
    make_box("Office_Desk_Top", (dx, dy, dt), (1.60, 0.72, 0.03), (0.66, 0.60, 0.52, 1.0))
    make_box("Office_Desk_Pedestal", (dx + 0.56, dy, PLAT + 0.36), (0.42, 0.66, 0.72), (0.60, 0.55, 0.48, 1.0))
    for d in range(3):
        make_box(f"Office_Desk_Drawer_{d}", (dx + 0.56, dy - 0.335, PLAT + 0.14 + d * 0.22), (0.38, 0.01, 0.18), (0.66, 0.60, 0.52, 1.0))
    for i, (lx, ly) in enumerate(((-0.76, -0.32), (-0.76, 0.32))):
        make_box(f"Office_Desk_Leg_{i}", (dx + lx, dy + ly, PLAT + 0.36), (0.04, 0.04, 0.72), (0.40, 0.40, 0.42, 1.0))
    make_box("Office_Desk_Modesty", (dx - 0.10, dy + 0.33, PLAT + 0.50), (1.30, 0.02, 0.40), (0.60, 0.55, 0.48, 1.0))
    t = dt + 0.015
    # "sits down at the computer"
    make_box("Office_Monitor_Panel", (dx - 0.05, dy + 0.18, t + 0.33), (0.58, 0.03, 0.35), COL_DARK)
    make_box("Office_Monitor_Screen", (dx - 0.05, dy + 0.164, t + 0.33), (0.54, 0.004, 0.31), (0.40, 0.56, 0.70, 1.0))
    make_box("Office_Monitor_Neck", (dx - 0.05, dy + 0.21, t + 0.10), (0.05, 0.03, 0.20), COL_DARK)
    make_box("Office_Monitor_Foot", (dx - 0.05, dy + 0.17, t + 0.006), (0.22, 0.16, 0.012), COL_DARK)
    make_box("Office_Keyboard", (dx - 0.05, dy - 0.10, t + 0.012), (0.44, 0.15, 0.024), COL_DARK)
    make_box("Office_Mouse", (dx + 0.30, dy - 0.10, t + 0.015), (0.06, 0.10, 0.03), COL_DARK)
    make_box("Office_Desk_Phone", (dx + 0.58, dy + 0.12, t + 0.04), (0.20, 0.22, 0.08), COL_DARK)
    # the coffee, the stock bottle with its cap off, the tablets: "Think I'll try three ... Two will do."
    make_mug("Office_Coffee", dx - 0.55, dy - 0.12, t, (0.86, 0.20, 0.18, 1.0))
    make_cyl("Pill_Bottle", (dx + 0.18, dy + 0.02, t + 0.065), 0.034, 0.13, COL_PAPER, segments=10)
    make_cyl("Pill_Bottle_Label", (dx + 0.18, dy + 0.02, t + 0.06), 0.0345, 0.07, (0.30, 0.46, 0.72, 1.0), segments=10)
    make_cyl("Pill_Bottle_Cap", (dx + 0.34, dy + 0.06, t + 0.01), 0.033, 0.02, COL_PAPER, segments=10)
    for k, (px, py) in enumerate(((0.15, -0.24), (0.19, -0.27), (0.11, -0.28))):
        make_cyl(f"Pill_{k}", (dx + px, dy + py, t + 0.003), 0.006, 0.006, (0.98, 0.98, 0.96, 1.0), segments=8)
    make_box("Office_Papers", (dx - 0.50, dy + 0.14, t + 0.01), (0.22, 0.30, 0.02), COL_PAPER)
    make_box("Office_Sticky_Pad", (dx + 0.40, dy - 0.24, t + 0.008), (0.08, 0.08, 0.016), (0.96, 0.90, 0.40, 1.0))
    make_cyl("Office_Pen_Cup", (dx - 0.66, dy + 0.18, t + 0.05), 0.035, 0.10, (0.20, 0.42, 0.72, 1.0), segments=8)
    for k in range(3):
        make_cyl(f"Office_Pen_{k}", (dx - 0.66 + (k - 1) * 0.012, dy + 0.18, t + 0.12), 0.004, 0.14, BRAND[k], segments=4)
    # the chair, pushed back from the desk where he stood up
    cx, cy = dx - 0.10, dy - 0.85
    make_cyl("Office_Chair_Base", (cx, cy, PLAT + 0.03), 0.30, 0.04, COL_DARK, segments=10)
    make_cyl("Office_Chair_Post", (cx, cy, PLAT + 0.25), 0.03, 0.40, COL_STEEL, segments=8)
    make_box("Office_Chair_Seat", (cx, cy, PLAT + 0.48), (0.48, 0.46, 0.07), COL_DARK)
    make_box("Office_Chair_Back", (cx, cy - 0.21, PLAT + 0.82), (0.44, 0.05, 0.56), COL_DARK)
    make_box("Office_Chair_Spine", (cx, cy - 0.22, PLAT + 0.55), (0.06, 0.04, 0.10), COL_STEEL)
    # the two-drawer file cabinet in the NE corner and the drug-rep samples on it
    fx, fy = ox1 - 0.25, oy1 - 0.32
    make_box("Office_File", (fx, fy, PLAT + 0.36), (0.44, 0.60, 0.72), (0.60, 0.62, 0.64, 1.0))
    for d in range(2):
        make_box(f"Office_File_Drawer_{d}", (fx, fy - 0.305, PLAT + 0.18 + d * 0.36), (0.40, 0.01, 0.32), (0.56, 0.58, 0.60, 1.0))
    for k in range(4):
        make_box(f"Sample_Box_{k}", (fx + 0.04 * ((k % 2) - 0.5), fy + 0.02, PLAT + 0.72 + 0.045 + k * 0.09), (0.30, 0.20, 0.09),
                 ((0.42, 0.20, 0.56, 1.0), (0.94, 0.94, 0.92, 1.0), (0.18, 0.52, 0.62, 1.0), (0.94, 0.94, 0.92, 1.0))[k])
    make_box("Sample_Box_3_Logo", (fx, fy - 0.082, PLAT + 0.72 + 0.045 + 3 * 0.09), (0.16, 0.004, 0.04), (0.42, 0.20, 0.56, 1.0))
    # THE MIRROR: full length, on the E wall, S of the cabinet
    my = oy0 + 0.80
    make_box("Office_Mirror_Frame", (ox1 - 0.015, my, PLAT + 1.05), (0.03, 0.56, 1.56), (0.24, 0.22, 0.20, 1.0))
    make_box("Office_Mirror_Glass", (ox1 - 0.032, my, PLAT + 1.05), (0.006, 0.48, 1.48), (0.72, 0.78, 0.82, 1.0))
    # the W wall: the reference shelf (a carcass, so the books stand IN it), the calendar
    bx, by = ox0 + 0.16, oy1 - 1.10
    bw, bh = 0.90, 1.80
    for s in (-1, 1):
        make_box(f"Office_Bookshelf_Side_{s:+d}", (bx, by + s * (bw / 2.0 - 0.01), PLAT + bh / 2.0), (0.30, 0.02, bh), (0.86, 0.85, 0.82, 1.0))
    make_box("Office_Bookshelf_Back", (bx - 0.14, by, PLAT + bh / 2.0), (0.02, bw, bh), (0.86, 0.85, 0.82, 1.0))
    for sh in range(4):
        z = PLAT + 0.04 + sh * 0.45
        make_box(f"Office_Bookshelf_Shelf_{sh}", (bx, by, z), (0.28, bw - 0.04, 0.02), (0.86, 0.85, 0.82, 1.0))
        for b in range(9 - sh):
            h = 0.24 + 0.03 * ((b + sh) % 3)
            make_box(f"Office_Book_{sh}_{b}", (bx - 0.02, by - bw / 2.0 + 0.08 + b * 0.085, z + 0.01 + h / 2.0), (0.22, 0.06, h),
                     ((0.20, 0.30, 0.52, 1.0), (0.62, 0.16, 0.14, 1.0), (0.86, 0.80, 0.62, 1.0), (0.18, 0.40, 0.30, 1.0))[(b + sh) % 4])
    make_box("Office_Bookshelf_Top", (bx, by, PLAT + bh + 0.01), (0.30, bw, 0.02), (0.86, 0.85, 0.82, 1.0))
    make_calendar("Office_Calendar", (5.10, oy1 - 0.003, PLAT + 1.62), axis='X')
    # the N wall over the desk: the diploma and the license
    for k, (wx, w, h) in enumerate(((3.25, 0.50, 0.40), (3.95, 0.36, 0.28))):
        make_box(f"Office_Diploma_{k}_Frame", (wx, oy1 - 0.012, PLAT + 1.75), (w, 0.024, h), (0.20, 0.16, 0.12, 1.0))
        make_box(f"Office_Diploma_{k}_Mat", (wx, oy1 - 0.026, PLAT + 1.75), (w - 0.08, 0.004, h - 0.08), (0.94, 0.92, 0.84, 1.0))
    # the S wall inside the door: the corkboard with the schedule, the hook with his jacket
    make_box("Office_Corkboard", (4.4, oy0 + 0.012, PLAT + 1.45), (0.90, 0.024, 0.60), (0.70, 0.56, 0.38, 1.0))
    for k in range(5):
        make_box(f"Office_Corkboard_Note_{k}", (4.10 + k * 0.15, oy0 + 0.026, PLAT + 1.42 + 0.10 * (k % 2)), (0.12, 0.004, 0.16), COL_PAPER)
    make_box("Office_Coat_Hook", (5.35, oy0 + 0.03, PLAT + 1.70), (0.04, 0.06, 0.04), COL_STEEL)
    make_box("Office_Jacket", (5.35, oy0 + 0.08, PLAT + 1.30), (0.44, 0.08, 0.76), (0.30, 0.32, 0.36, 1.0))
    make_cyl("Office_Wastebasket", (dx - 0.85, dy - 0.05, PLAT + 0.16), 0.13, 0.32, (0.40, 0.40, 0.42, 1.0), segments=10)


# ═══════════════════════════════════════════════════ east of the pharmacy
def build_waiting():
    for k in range(4):
        make_chair(f"Wait_Chair_{k}", RX_X1 + 0.62, 16.6 + k * 0.62, yaw=-math.pi / 2.0,
                   wood=(0.34, 0.34, 0.36, 1.0), seat_col=(0.20, 0.36, 0.56, 1.0), w=0.48)
    # the blood-pressure kiosk
    make_box("BP_Kiosk_Base", (RX_X1 + 0.70, 20.0, 0.25), (0.70, 0.70, 0.50), (0.86, 0.86, 0.84, 1.0))
    make_box("BP_Kiosk_Seat", (RX_X1 + 0.70, 20.0, 0.52), (0.56, 0.50, 0.04), (0.20, 0.36, 0.56, 1.0))
    make_box("BP_Kiosk_Tower", (RX_X1 + 0.70, 20.40, 1.05), (0.60, 0.20, 1.10), (0.86, 0.86, 0.84, 1.0))
    make_rot_box("BP_Kiosk_Screen", (RX_X1 + 0.70, 20.29, 1.30), (0.40, 0.02, 0.30), (0.30, 0.46, 0.66, 1.0), pitch=0.0, roll=0.0)
    # the flu shot sign on its A-frame by the counter's end
    make_box("Flu_Sign_Foot", (RX_X1 + 0.80, 14.70, 0.015), (0.60, 0.40, 0.03), COL_DARK)
    make_box("Flu_Sign_Board", (RX_X1 + 0.80, 14.60, 0.48), (0.60, 0.04, 0.90), COL_PAPER)
    make_box("Flu_Sign_Band", (RX_X1 + 0.80, 14.578, 0.75), (0.56, 0.004, 0.16), (0.20, 0.42, 0.72, 1.0))
    # the doors in the N wall: restrooms, employees only
    for k, (nx, col) in enumerate(((9.0, (0.70, 0.66, 0.60, 1.0)), (11.6, (0.70, 0.66, 0.60, 1.0)))):
        make_box(f"Back_Door_{k}", (nx, Y1 - 0.08, 1.04), (0.90, 0.04, 2.06), col)
        make_box(f"Back_Door_{k}_Push", (nx - 0.25, Y1 - 0.11, 1.05), (0.25, 0.02, 0.08), COL_STEEL)
        make_box(f"Back_Door_{k}_Sign", (nx, Y1 - 0.105, 1.60), (0.30, 0.01, 0.20), (0.20, 0.42, 0.72, 1.0) if k == 0 else COL_RED)
    make_box("Water_Fountain", (10.3, Y1 - 0.28, 0.85), (0.44, 0.36, 0.30), COL_STEEL)
    make_box("Water_Fountain_Pedestal", (10.3, Y1 - 0.15, 0.35), (0.20, 0.10, 0.70), COL_STEEL)


def main():
    clear_scene()
    build_shell()
    build_lights()
    build_aisles()
    build_front()
    build_pharmacy()
    build_office()
    build_waiting()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/pharmacy.glb"))
    print(f"\n[build_pharmacy] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
