"""VOL 5 · Café Olimpico — Saint-Viateur, Mile End, Montreal.

Hero set for XIX The Sun ("Pattern Recognition in Dust Motes",
vol5_ch19_sun.json) and XIV Temperance — John Frank's café, a
Tuesday morning in late May, six years of Tuesdays into a
fifty-year-old Italian espresso institution (est. 1970 register:
blue-and-white, soccer on the wall, stand-up bar culture). This is
The Sun after The Moon — the set is built FOR morning light:
big front openings, a corner window over John's table, warm cream
and azzurro, circles everywhere (round tables, globe pendants,
the clock, the brass finial on the machine). Canon baked in:

  · "the small round metal table in the back corner, under the
    window" + "a shaft of late-morning sunlight fell across the
    table ... and the dust motes ... performed their intricate
    silent ballet in the shaft" (scene line 46) — NW corner table
    under the west window, with the dust motes modeled as tiny
    sun-lit specks in the shaft (the chapter subtitle is literal).
  · "they made him the single espresso ... and set it down beside
    the small water glass he had not asked for" (line 42) — the
    water-glass ritual: glass on John's table, tumbler stacks +
    carafe by the register.
  · "the bell over the café door chimed" (lines 174, 186) — brass
    bell over the door. Clock frozen at 10:23, the minute the
    blue-dreadlocked woman walks into the pattern (line 174).
  · "a small table by the front window" + the cardboard tube the
    man "did not, at any point, open" (lines 174/178) — SE window
    two-top with two coffees and a CLOSED kraft tube.
  · "Sub-pattern: secondary clustering around the new arrival at
    the window table" (line 182) — a second, smaller mote cluster
    over the window table.
  · croissants (lines 309-334, 392): pastry case holds them; on
    John's table the paper bag, one whole croissant, and one
    broken in half (Elicia hands him the larger piece).
  · "The chair is terrible" (line 90) — thin worn bistro chairs.
  · "the menu she had already memorized" (line 305) — card menus.
  · Outside (lines 271, 400): Saint-Viateur in late-May full
    green — street tree, dry sidewalk, THE DOG tied to the bike
    rack, the bagel shop across the street starting lunch rush.
  · Marco the barista (line 190) works the stand-up bar: brass
    foot rail, no table service clutter behind it.

CANON-NEGATIVES (as important as the props): it is NOT raining
(line 174 — "though it was not, today, raining"): no umbrellas, no
puddles, no rain hooks. No drip-coffee pots, no donut case, no PNW
mug wall — this is a single-espresso institution, not the Daily
Grind. No fluorescent tube grid — a 1970 café runs on globe
pendants and one ceiling fan. The cardboard tube stays CLOSED.

Playbook compliance: windows are REAL OPENINGS (frame + mullions,
zero glass slabs); the front door is propped open for late May so
the Background3D camera at the threshold sees straight to the bar;
cylinders/spheres for everything at eye level; fully deterministic
(no random module — seed arithmetic only). Sign lettering
(Facade_SignPanel, MenuBoard_0/1, BagelShop_SignBand) is
scene-side Label3D per the playbook.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_wall, make_ceiling, make_crown_molding, make_door_hinges
from _props.store_fixtures import make_register, make_credit_card_terminal
from _props.decor import make_wall_clock, make_payphone
from _props.safety import make_smoke_detector, make_ceiling_speaker, make_hvac_vent

# ── Shell footprint kept from the scaffold (tscn lights + the
#    Background3D "cafe_olimpico" camera at the door, x 0) ────────
ROOM_W = 8.0; ROOM_D = 6.0; CEIL = 3.00

# ── Olimpico palette — blue-and-white Italian institution, warmed
#    by fifty years of espresso and morning sun. Muted per house rule.
PAL_WALL      = {"wall": (0.91, 0.89, 0.83, 1.0), "baseboard": (0.30, 0.22, 0.15, 1.0)}
COL_AZZURRO   = (0.24, 0.38, 0.58, 1.0)   # Olimpico blue (trim, awning, bunting)
COL_AZZURRO_LT= (0.44, 0.56, 0.72, 1.0)
COL_TILE_CREAM= (0.88, 0.86, 0.79, 1.0)   # checker floor, worn by decades
COL_TILE_BLUE = (0.36, 0.46, 0.58, 1.0)
COL_TILE_WORN = (0.76, 0.73, 0.65, 1.0)   # the Tuesdays path
COL_TILE_BLUE_WORN = (0.46, 0.53, 0.62, 1.0)
COL_GROUT     = (0.55, 0.52, 0.46, 1.0)
COL_WOOD      = (0.45, 0.32, 0.20, 1.0)   # old walnut trim
COL_WOOD_DARK = (0.27, 0.20, 0.14, 1.0)
COL_MARBLE    = (0.89, 0.88, 0.84, 1.0)   # bar top
COL_MARBLE_VEIN = (0.64, 0.64, 0.61, 1.0)
COL_CHROME    = (0.74, 0.76, 0.78, 1.0)   # the machine
COL_BRASS     = (0.72, 0.58, 0.30, 1.0)
COL_CREAM     = (0.93, 0.91, 0.86, 1.0)   # demitasse ceramic
COL_ESPRESSO  = (0.24, 0.15, 0.10, 1.0)
COL_GLASSISH  = (0.74, 0.79, 0.80, 1.0)   # opaque stand-in for tumblers
COL_WHITE_PANEL = (0.87, 0.86, 0.82, 1.0) # bar-front panels
COL_SLATE     = (0.16, 0.17, 0.16, 1.0)
COL_CHALK     = (0.88, 0.88, 0.82, 1.0)
COL_CROISSANT = (0.79, 0.60, 0.33, 1.0)
COL_CRUST     = (0.64, 0.44, 0.22, 1.0)
COL_KRAFT     = (0.70, 0.56, 0.38, 1.0)   # the cardboard tube / paper bag
COL_GAZZETTA  = (0.87, 0.72, 0.68, 1.0)   # pink Italian sports paper
COL_SEPIA     = (0.70, 0.60, 0.46, 1.0)
COL_SEPIA_INK = (0.38, 0.30, 0.22, 1.0)
COL_PITCH     = (0.30, 0.46, 0.30, 1.0)   # soccer on the corner TV
COL_SUNGLOW   = (0.99, 0.93, 0.78, 1.0)   # dust motes / bulb glow
COL_METAL_TABLE = (0.60, 0.62, 0.63, 1.0) # John's small round metal table
COL_CHAIR_BLUE = (0.32, 0.42, 0.55, 1.0)  # worn painted bistro chairs
COL_CONCRETE  = (0.58, 0.57, 0.53, 1.0)   # dry (NOT rain-dark) sidewalk
COL_ASPHALT   = (0.20, 0.20, 0.21, 1.0)
COL_BRICK     = (0.55, 0.35, 0.27, 1.0)
COL_LEAF      = (0.38, 0.53, 0.29, 1.0)   # late-May full green (line 271)
COL_TRUNK     = (0.36, 0.28, 0.20, 1.0)
COL_DOG       = (0.66, 0.50, 0.31, 1.0)   # the dog at the bike rack (line 400)
COL_ORANGE    = (0.82, 0.52, 0.22, 1.0)   # aranciata / aperitivo poster disc
COL_TIN_RED   = (0.68, 0.24, 0.20, 1.0)

BAR_TOP = 1.10        # stand-up espresso-bar height (taller than a diner counter)
BACKBAR_TOP = 0.97

_DIRS = {'N': (0.0, 1.0), 'S': (0.0, -1.0), 'E': (1.0, 0.0), 'W': (-1.0, 0.0)}


# ═════════════════════════════════════════════════════════════════
# Local furniture helpers (deterministic, cylinder-first at eye level)
# ═════════════════════════════════════════════════════════════════
def _metal_table(prefix, cx, cy, r=0.30, tint=COL_METAL_TABLE):
    """Small round metal café table — 'the small round metal table
    in the back corner' (scene line 46). Pedestal + round base."""
    make_cyl(f"{prefix}_Top", (cx, cy, 0.725), r, 0.03, tint, segments=12)
    make_cyl(f"{prefix}_Rim", (cx, cy, 0.705), r * 0.97, 0.012, P.METAL_BLACK, segments=12)
    make_cyl(f"{prefix}_Column", (cx, cy, 0.36), 0.032, 0.70, P.METAL_BLACK)
    make_cyl(f"{prefix}_Base", (cx, cy, 0.02), r * 0.62, 0.04, P.METAL_BLACK, segments=12)

def _bistro_chair(prefix, cx, cy, facing, tint=COL_CHAIR_BLUE):
    """Thin worn painted-metal bistro chair — 'The chair is
    terrible' (line 90). `facing` = direction the sitter faces."""
    dx, dy = _DIRS[facing]
    make_cyl(f"{prefix}_Seat", (cx, cy, 0.455), 0.17, 0.025, tint, segments=12)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"{prefix}_Leg_{li}", (cx + sx * 0.125, cy + sy * 0.125, 0.22),
                 0.013, 0.44, P.METAL_BLACK)
    bx, by = cx - dx * 0.155, cy - dy * 0.155
    for pi, sgn in enumerate((-1, +1)):
        px = bx + (sgn * 0.115 if dx == 0 else 0.0)
        py = by + (sgn * 0.115 if dy == 0 else 0.0)
        make_cyl(f"{prefix}_BackPost_{pi}", (px, py, 0.665), 0.011, 0.40, tint)
    rail_axis = 'X' if dx == 0 else 'Y'
    make_cyl(f"{prefix}_BackRail", (bx, by, 0.875), 0.013, 0.26, tint, axis=rail_axis)
    slat_sz = (0.24, 0.02, 0.07) if dx == 0 else (0.02, 0.24, 0.07)
    make_box(f"{prefix}_BackSlat", (bx, by, 0.70), slat_sz, tint)

def _stool(prefix, cx, cy):
    make_cyl(f"{prefix}_Seat", (cx, cy, 0.72), 0.16, 0.04, COL_WOOD, segments=12)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"{prefix}_Leg_{li}", (cx + sx * 0.095, cy + sy * 0.095, 0.35),
                 0.015, 0.70, P.METAL_BLACK)
    for ri, (rx, ry, rsz) in enumerate([
            (0.0, -0.095, (0.19, 0.018, 0.018)), (0.0, +0.095, (0.19, 0.018, 0.018)),
            (-0.095, 0.0, (0.018, 0.19, 0.018)), (+0.095, 0.0, (0.018, 0.19, 0.018))]):
        make_box(f"{prefix}_Rung_{ri}", (cx + rx, cy + ry, 0.24), rsz, P.METAL_BLACK)

def _globe_pendant(prefix, cx, cy, drop=0.78):
    """White globe pendant — round warm light, the 1970 fixture
    vocabulary (Sun-card circle motif; no fluorescent tubes here)."""
    make_cyl(f"{prefix}_Canopy", (cx, cy, CEIL - 0.02), 0.045, 0.035, COL_BRASS)
    make_cyl(f"{prefix}_Cord", (cx, cy, CEIL - drop / 2.0), 0.007, drop, P.METAL_BLACK)
    make_cyl(f"{prefix}_Collar", (cx, cy, CEIL - drop - 0.01), 0.05, 0.03, COL_BRASS)
    make_cyl(f"{prefix}_Globe", (cx, cy, CEIL - drop - 0.115), 0.105, 0.16,
             COL_SUNGLOW, segments=12)

def _espresso_setting(prefix, cx, cy, bz, *, drunk=False):
    """Single espresso, demitasse on saucer — the six-year order."""
    make_cyl(f"{prefix}_Saucer", (cx, cy, bz + 0.006), 0.056, 0.012, COL_CREAM, segments=12)
    make_cyl(f"{prefix}_Cup", (cx, cy, bz + 0.040), 0.032, 0.055, COL_CREAM)
    if not drunk:
        make_cyl(f"{prefix}_Coffee", (cx, cy, bz + 0.062), 0.026, 0.008, COL_ESPRESSO)
    make_box(f"{prefix}_Handle", (cx + 0.040, cy, bz + 0.040), (0.013, 0.011, 0.036), COL_CREAM)
    make_cyl(f"{prefix}_Spoon", (cx - 0.02, cy + 0.048, bz + 0.014), 0.0045, 0.09,
             COL_CHROME, axis='X')

def _water_glass(prefix, cx, cy, bz):
    """The small water glass he had not asked for (line 42)."""
    make_cyl(f"{prefix}", (cx, cy, bz + 0.042), 0.028, 0.078, COL_GLASSISH)
    make_cyl(f"{prefix}_Water", (cx, cy, bz + 0.056), 0.024, 0.036, (0.66, 0.74, 0.78, 1.0))

def _croissant(prefix, cx, cy, bz):
    """Stepped-box crescent, golden with darker crust ends."""
    make_box(f"{prefix}_Mid", (cx, cy, bz + 0.017), (0.095, 0.052, 0.034), COL_CROISSANT)
    make_box(f"{prefix}_EndW", (cx - 0.062, cy + 0.020, bz + 0.014),
             (0.048, 0.040, 0.027), COL_CRUST)
    make_box(f"{prefix}_EndE", (cx + 0.062, cy + 0.020, bz + 0.014),
             (0.048, 0.040, 0.027), COL_CRUST)

def _croissant_half(prefix, cx, cy, bz, big=True):
    w = 0.070 if big else 0.048
    make_box(f"{prefix}_Body", (cx, cy, bz + 0.015), (w, 0.048, 0.030), COL_CROISSANT)
    make_box(f"{prefix}_End", (cx + w / 2.0, cy + 0.016, bz + 0.013),
             (0.036, 0.036, 0.024), COL_CRUST)


# ═════════════════════════════════════════════════════════════════
# SHELL — checkerboard tile floor worn by fifty years of feet,
# cream walls, west corner window over John's table (the shaft
# comes through here), full-height plate walls elsewhere.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    # Grout-tone slab, then a deterministic cream/blue checker on top.
    make_box("Floor_Slab", (0.0, 3.0, -0.05), (ROOM_W + 0.4, ROOM_D + 0.4, 0.10), COL_GROUT)
    for i in range(10):
        for j in range(7):
            cx = -3.6 + i * 0.8
            cy = 0.6 + j * 0.8
            base = COL_TILE_CREAM if (i + j) % 2 == 0 else COL_TILE_BLUE
            # Worn tiles cluster near the door→bar aisle (six years
            # of Tuesdays; fifty of everyone else) + seed scatter.
            seed = (i * 7 + j * 13) % 13
            worn = seed < 2 or (abs(cx) < 1.3 and cy < 4.0 and seed < 5)
            if worn:
                base = COL_TILE_WORN if (i + j) % 2 == 0 else COL_TILE_BLUE_WORN
            make_box(f"FloorTile_{i}_{j}", (cx, cy, 0.006), (0.74, 0.74, 0.012), base)
    # East wall — solid (memorabilia + ledge + payphone live here)
    make_wall("Wall_E", (ROOM_W / 2.0, 3.0, 0), length=ROOM_D + 0.4, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    # West wall — corner-window opening y 3.9..5.5 (sill 0.85, head
    # 2.35) over the back-corner table (scene line 46)
    make_wall("Wall_W_S", (-ROOM_W / 2.0, 1.85, 0), length=4.10, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_W_N", (-ROOM_W / 2.0, 5.85, 0), length=0.70, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_W_Sill", (-4.0, 4.7, 0.425), (0.20, 1.60, 0.85), PAL_WALL["wall"])
    make_box("Wall_W_SillBase", (-3.94, 4.7, 0.08), (0.06, 1.60, 0.16), PAL_WALL["baseboard"])
    make_box("Wall_W_Header", (-4.0, 4.7, 2.675), (0.20, 1.60, 0.65), PAL_WALL["wall"])
    # North wall — solid behind the backbar
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    # South (Saint-Viateur) wall — door opening x −1.05..+1.05 and
    # two BIG window openings x ±1.45..±3.45 (sill 0.55, head 2.55).
    for nm, px, pw in [("Wall_S_PierSW", -3.825, 0.75), ("Wall_S_PierWD", -1.25, 0.40),
                       ("Wall_S_PierED", +1.25, 0.40), ("Wall_S_PierSE", +3.825, 0.75)]:
        make_box(nm, (px, 0.0, CEIL / 2.0), (pw, 0.20, CEIL), PAL_WALL["wall"])
    for tag, wx in [("W", -2.45), ("E", +2.45)]:
        make_box(f"Wall_S_{tag}_Sill", (wx, 0.0, 0.275), (2.00, 0.20, 0.55), PAL_WALL["wall"])
        make_box(f"Wall_S_{tag}_SillBase", (wx, 0.13, 0.08), (2.00, 0.06, 0.16),
                 PAL_WALL["baseboard"])
        make_box(f"Wall_S_{tag}_Header", (wx, 0.0, 2.775), (2.00, 0.20, 0.45), PAL_WALL["wall"])
    make_box("Wall_S_AboveDoor", (0.0, 0.0, 2.675), (2.10, 0.20, 0.65), PAL_WALL["wall"])
    # Painted plaster ceiling (a 1970 café — NOT a drop-tile grid)
    make_ceiling("Ceil", (0.0, 3.0, CEIL), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
                 palette={"tile": (0.90, 0.88, 0.82, 1.0)},
                 with_grid=False, with_stains=False)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W / 2.0 + 0.10, 3.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W / 2.0 - 0.10, 3.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D - 0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_WOOD})


# ═════════════════════════════════════════════════════════════════
# STOREFRONT — real openings (frame + mullions, NO glass slabs per
# playbook), the door PROPPED OPEN for late May (the camera at the
# threshold sees straight to the machine; The Sun's door stands
# open where The Moon's would be shut), the canon brass bell.
# ═════════════════════════════════════════════════════════════════
def _window_frame_south(tag, wx):
    """Blue-painted wood frame in a south opening centered at wx.
    Opening: 2.0 wide, z 0.55..2.55, transom at 2.12."""
    make_box(f"WinS_{tag}_SillCap", (wx, 0.0, 0.575), (2.12, 0.24, 0.05), COL_AZZURRO)
    make_box(f"WinS_{tag}_Ledge", (wx, 0.15, 0.61), (1.90, 0.14, 0.03), COL_WOOD)
    make_box(f"WinS_{tag}_Head", (wx, 0.0, 2.525), (2.12, 0.24, 0.05), COL_AZZURRO)
    for sgn in (-1, +1):
        make_box(f"WinS_{tag}_Jamb_{sgn:+d}", (wx + sgn * 0.985, 0.0, 1.55),
                 (0.06, 0.22, 1.95), COL_AZZURRO)
        make_box(f"WinS_{tag}_MullV_{sgn:+d}", (wx + sgn * 0.50, 0.0, 1.53),
                 (0.05, 0.14, 1.90), COL_AZZURRO)
    make_box(f"WinS_{tag}_Transom", (wx, 0.0, 2.12), (1.96, 0.14, 0.05), COL_AZZURRO)

def build_storefront():
    _window_frame_south("W", -2.45)
    _window_frame_south("E", +2.45)
    # West corner window (John's shaft) — same treatment, Y-run wall
    make_box("WinW_SillCap", (-4.0, 4.7, 0.87), (0.24, 1.72, 0.05), COL_AZZURRO)
    make_box("WinW_Ledge", (-3.86, 4.7, 0.905), (0.14, 1.60, 0.03), COL_WOOD)
    make_box("WinW_Head", (-4.0, 4.7, 2.325), (0.24, 1.72, 0.05), COL_AZZURRO)
    for sgn in (-1, +1):
        make_box(f"WinW_Jamb_{sgn:+d}", (-4.0, 4.7 + sgn * 0.775, 1.60),
                 (0.22, 0.05, 1.50), COL_AZZURRO)
    make_box("WinW_MullV", (-4.0, 4.7, 1.60), (0.14, 0.05, 1.44), COL_AZZURRO)
    make_box("WinW_Transom", (-4.0, 4.7, 1.98), (0.14, 1.56, 0.05), COL_AZZURRO)
    # Door surround — opening x −1.05..1.05 to z 2.35
    for sgn in (-1, +1):
        make_box(f"DoorPost_{sgn:+d}", (sgn * 1.02, 0.0, 1.175), (0.07, 0.16, 2.35), COL_AZZURRO)
    make_box("DoorHead", (0.0, 0.0, 2.325), (2.10, 0.16, 0.06), COL_AZZURRO)
    # The door leaf, swung fully INWARD against the west pier and
    # wedged — propped open for the one warm bright Tuesday.
    make_box("Door_Leaf", (-1.02, 0.57, 1.14), (0.05, 0.90, 2.24), COL_WOOD_DARK)
    for pi in range(2):
        make_box(f"Door_Panel_{pi}", (-0.988, 0.57, 0.66 + pi * 0.95),
                 (0.008, 0.64, 0.70), COL_WOOD)
    make_box("Door_KickPlate", (-0.986, 0.57, 0.16), (0.012, 0.84, 0.26), COL_BRASS)
    make_cyl("Door_PushBar", (-0.975, 0.60, 1.02), 0.018, 0.56, COL_BRASS, axis='Y')
    make_box("Door_Wedge", (-0.99, 1.06, 0.028), (0.06, 0.10, 0.056), COL_WOOD)
    make_door_hinges("Door_Hinge", edge_x=-1.045, edge_y=0.10,
                     edge_z_centers=[0.40, 1.15, 1.90], axis='Z')
    # THE BELL over the door — it chimes at 10:23 and again for
    # Elicia (scene lines 174, 186). Brass, bracket-mounted, offset
    # east so the threshold camera line stays clear.
    make_box("DoorBell_Mount", (0.55, 0.14, 2.30), (0.06, 0.09, 0.06), P.METAL_BLACK)
    make_cyl("DoorBell_Arm", (0.55, 0.23, 2.30), 0.011, 0.14, COL_BRASS, axis='Y')
    make_cyl("DoorBell_Body", (0.55, 0.31, 2.26), 0.048, 0.06, COL_BRASS)
    make_cyl("DoorBell_Flare", (0.55, 0.31, 2.215), 0.062, 0.022, COL_BRASS)
    make_cyl("DoorBell_Clapper", (0.55, 0.31, 2.18), 0.011, 0.045, P.METAL_BLACK)
    # Entry mats — dry ones; no umbrella stand today (line 174:
    # "though it was not, today, raining")
    make_box("EntryMat", (0.0, 0.72, 0.016), (1.80, 0.95, 0.010), (0.20, 0.24, 0.32, 1.0))
    make_box("EntryMat_Border", (0.0, 0.72, 0.014), (1.92, 1.07, 0.006), (0.14, 0.14, 0.15, 1.0))
    # Hours card on the east door post (lettering scene-side)
    make_box("HoursCard", (1.02, -0.09, 1.55), (0.14, 0.010, 0.20), P.PAPER)


# ═════════════════════════════════════════════════════════════════
# EXTERIOR — Saint-Viateur doing its Tuesday work (line 400): dry
# late-May sidewalk, street tree in full green (line 271), the
# terrasse two-top, the bike rack with THE DOG tied to it watching
# every pedestrian, the bagel shop across the street starting its
# lunch rush. Facade band + blue awning + sign panel above.
# ═════════════════════════════════════════════════════════════════
def build_exterior():
    # Our facade above the storefront + the blue awning
    make_box("Facade_Band", (0.0, -0.10, 3.65), (8.40, 0.20, 1.30), (0.84, 0.80, 0.72, 1.0))
    make_box("Facade_Cornice", (0.0, -0.14, 4.36), (8.60, 0.30, 0.12), (0.70, 0.66, 0.58, 1.0))
    make_box("Facade_SignPanel", (0.0, -0.225, 3.62), (5.20, 0.06, 0.62), COL_AZZURRO)
    make_box("Awning_Canopy", (0.0, -0.68, 2.72), (7.60, 1.15, 0.05), COL_AZZURRO)
    make_box("Awning_Valance", (0.0, -1.245, 2.60), (7.60, 0.04, 0.22), COL_AZZURRO)
    for si in range(4):
        make_box(f"Awning_Stripe_{si}", (-2.85 + si * 1.9, -1.248, 2.60),
                 (0.55, 0.045, 0.22), (0.88, 0.87, 0.83, 1.0))
    # Dry sidewalk (canon-negative: no puddles), curb, street
    make_box("Ext_Sidewalk", (0.0, -1.60, -0.03), (13.0, 2.90, 0.06), COL_CONCRETE)
    for si in range(5):
        make_box(f"Ext_SidewalkSeam_{si}", (-4.4 + si * 2.2, -1.60, 0.002),
                 (0.02, 2.90, 0.002), (0.46, 0.45, 0.42, 1.0))
    make_box("Ext_Curb", (0.0, -3.13, -0.01), (13.0, 0.16, 0.12), (0.50, 0.49, 0.46, 1.0))
    make_box("Ext_Street", (0.0, -5.65, -0.05), (13.0, 4.90, 0.04), COL_ASPHALT)
    for di in range(5):
        make_box(f"Ext_LaneDash_{di}", (-5.2 + di * 2.6, -5.65, -0.028),
                 (0.90, 0.10, 0.003), (0.72, 0.62, 0.30, 1.0))
    make_box("Ext_FarCurb", (0.0, -8.18, -0.01), (13.0, 0.16, 0.12), (0.50, 0.49, 0.46, 1.0))
    make_box("Ext_FarSidewalk", (0.0, -8.95, -0.03), (13.0, 1.50, 0.06), COL_CONCRETE)
    # The bagel shop across the street (line 400) — brick facade,
    # warm oven glow in the window, lunch-rush door open
    make_box("BagelShop_Facade", (0.0, -9.90, 2.20), (12.50, 0.30, 4.40), COL_BRICK)
    make_box("BagelShop_Window", (-1.7, -9.72, 1.55), (4.60, 0.06, 1.50), (0.16, 0.15, 0.14, 1.0))
    make_box("BagelShop_OvenGlow", (-1.7, -9.68, 1.50), (4.20, 0.02, 1.20), (0.92, 0.70, 0.40, 1.0))
    make_box("BagelShop_Door", (2.3, -9.72, 1.15), (1.00, 0.06, 2.30), (0.30, 0.22, 0.15, 1.0))
    make_box("BagelShop_SignBand", (0.0, -9.72, 3.05), (6.40, 0.06, 0.62), (0.86, 0.82, 0.72, 1.0))
    make_box("BagelShop_Cornice", (0.0, -9.90, 4.44), (12.70, 0.36, 0.10), (0.68, 0.62, 0.54, 1.0))
    for ci in range(3):
        make_box(f"BagelShop_FlourSack_{ci}", (2.95 + (ci % 2) * 0.32, -9.55, 0.16 + (ci // 2) * 0.30),
                 (0.30, 0.24, 0.32), P.PAPER_AGED)
    # Street tree in full late-May green (line 271) — cyl-tier canopy
    make_box("Tree_Pit", (-4.4, -2.40, 0.004), (0.90, 0.90, 0.010), (0.26, 0.20, 0.14, 1.0))
    make_cyl("Tree_Trunk", (-4.4, -2.40, 1.20), 0.10, 2.40, COL_TRUNK, segments=10)
    make_cyl("Tree_Canopy_0", (-4.4, -2.40, 3.05), 1.10, 0.70, COL_LEAF, segments=12)
    make_cyl("Tree_Canopy_1", (-4.4, -2.40, 3.65), 0.85, 0.55, (0.33, 0.47, 0.25, 1.0), segments=12)
    make_cyl("Tree_Canopy_2", (-4.4, -2.40, 4.12), 0.52, 0.42, COL_LEAF, segments=10)
    # Terrasse two-top west of the door (Mile End sidewalk ritual)
    _metal_table("TerrasseTable", -2.45, -1.15, r=0.28)
    _bistro_chair("TerrasseChair_0", -3.05, -1.15, 'E')
    _bistro_chair("TerrasseChair_1", -1.85, -1.15, 'W')
    _espresso_setting("TerrasseCup", -2.52, -1.10, 0.74, drunk=True)
    # Bike rack + THE DOG (line 400: "A dog, tied to a bike rack,
    # looked at every pedestrian with the bright unjudging attention
    # dogs reserved for their favorite hour of the day.")
    for pi, px in enumerate((2.55, 3.25)):
        make_cyl(f"BikeRack_Post_{pi}", (px, -1.70, 0.375), 0.025, 0.75, P.METAL_BLACK)
    make_cyl("BikeRack_Rail", (2.90, -1.70, 0.765), 0.025, 0.72, P.METAL_BLACK, axis='X')
    make_box("Dog_Haunch", (3.60, -1.15, 0.16), (0.22, 0.26, 0.26), COL_DOG)
    make_box("Dog_Chest", (3.47, -1.15, 0.27), (0.16, 0.20, 0.30), COL_DOG)
    make_box("Dog_Head", (3.42, -1.15, 0.53), (0.15, 0.17, 0.15), COL_DOG)
    make_box("Dog_Snout", (3.33, -1.15, 0.49), (0.08, 0.10, 0.07), (0.52, 0.38, 0.24, 1.0))
    for ei, sgn in enumerate((-1, +1)):
        make_box(f"Dog_Ear_{ei}", (3.44, -1.15 + sgn * 0.062, 0.63),
                 (0.03, 0.04, 0.09), (0.52, 0.38, 0.24, 1.0))
    for li, sgn in enumerate((-1, +1)):
        make_cyl(f"Dog_ForeLeg_{li}", (3.44, -1.15 + sgn * 0.06, 0.15), 0.018, 0.30, COL_DOG)
    make_cyl("Dog_Tail", (3.76, -1.15, 0.30), 0.015, 0.14, COL_DOG, axis='X')
    make_box("Dog_Collar", (3.42, -1.15, 0.445), (0.13, 0.155, 0.03), (0.62, 0.22, 0.18, 1.0))
    make_cyl("Dog_Leash_Drop", (3.25, -1.70, 0.60), 0.006, 0.30, (0.62, 0.22, 0.18, 1.0))
    make_cyl("Dog_Leash_RunY", (3.25, -1.44, 0.46), 0.006, 0.52, (0.62, 0.22, 0.18, 1.0), axis='Y')
    make_cyl("Dog_Leash_RunX", (3.34, -1.17, 0.46), 0.006, 0.18, (0.62, 0.22, 0.18, 1.0), axis='X')


# ═════════════════════════════════════════════════════════════════
# THE BAR — the institution's altar. Marble top at stand-up height,
# white panel fronts with azzurro band, brass foot rail (no stools:
# you stand at an Olimpico bar), and the chrome machine wearing a
# brass sun-crown finial. Pastry case of croissants + cannoli west;
# register, card terminal, and the water-glass ritual east.
# ═════════════════════════════════════════════════════════════════
def build_bar():
    # Body x −0.7..3.5, customer face y 4.0, back y 4.7
    make_box("Bar_Body", (1.4, 4.35, 0.52), (4.20, 0.70, 1.04), COL_WOOD)
    make_box("Bar_Top", (1.4, 4.35, 1.07), (4.36, 0.86, 0.06), COL_MARBLE)
    for vi, (vx, vy, vl) in enumerate([(0.2, 4.18, 0.9), (2.3, 4.5, 1.2), (3.1, 4.22, 0.6)]):
        make_box(f"Bar_TopVein_{vi}", (vx, vy, 1.101), (vl, 0.012, 0.002), COL_MARBLE_VEIN)
    make_box("Bar_Kick", (1.4, 3.99, 0.09), (4.20, 0.03, 0.18), COL_WOOD_DARK)
    make_box("Bar_TrimBand", (1.4, 3.985, 0.97), (4.20, 0.025, 0.10), COL_AZZURRO)
    for pi in range(5):
        px = -0.28 + pi * 0.84
        make_box(f"Bar_FrontPanel_{pi}", (px, 3.985, 0.55), (0.70, 0.020, 0.66), COL_WHITE_PANEL)
    make_box("Bar_EndCap_W", (-0.715, 4.35, 0.55), (0.020, 0.66, 0.86), COL_WHITE_PANEL)
    # Brass foot rail — the stand-up espresso-bar culture
    make_cyl("Bar_FootRail", (1.4, 3.86, 0.185), 0.020, 4.05, COL_BRASS, axis='X')
    for bi, bx in enumerate((-0.4, 1.4, 3.2)):
        make_box(f"Bar_FootRailBracket_{bi}", (bx, 3.92, 0.17), (0.03, 0.12, 0.03), COL_BRASS)
    # ── THE MACHINE — chrome horizontal-boiler 3-group, brass ball
    #    finial on top like a small sun (altar of the institution) ──
    make_box("Espresso_Base", (0.85, 4.38, 1.15), (1.44, 0.56, 0.10), P.METAL_BLACK)
    make_cyl("Espresso_Body", (0.85, 4.38, 1.46), 0.26, 1.40, COL_CHROME, axis='X', segments=14)
    for ci, sgn in enumerate((-1, +1)):
        make_cyl(f"Espresso_EndCap_{ci}", (0.85 + sgn * 0.72, 4.38, 1.46), 0.27, 0.04,
                 COL_BRASS, axis='X', segments=14)
    make_box("Espresso_BrandPlate", (0.85, 4.108, 1.44), (0.44, 0.012, 0.09), COL_BRASS)
    for gi, gx in enumerate((0.45, 1.25)):
        make_cyl(f"Espresso_Gauge_{gi}", (gx, 4.105, 1.52), 0.035, 0.014, COL_CREAM, axis='Y')
        make_cyl(f"Espresso_GaugeRim_{gi}", (gx, 4.10, 1.52), 0.041, 0.008, P.METAL_BLACK, axis='Y')
    make_box("Espresso_TopTray", (0.85, 4.38, 1.735), (1.46, 0.50, 0.025), COL_CHROME)
    # Warming demitasse rows flanking the finial
    cup_i = 0
    for r in range(2):
        for cxx in (0.25, 0.45, 0.65, 1.05, 1.25, 1.45):
            make_cyl(f"Espresso_WarmCup_{cup_i}", (cxx, 4.28 + r * 0.20, 1.772),
                     0.027, 0.048, COL_CREAM)
            cup_i += 1
    make_cyl("Espresso_FinialBase", (0.85, 4.38, 1.757), 0.050, 0.020, COL_BRASS)
    make_cyl("Espresso_FinialStem", (0.85, 4.38, 1.80), 0.018, 0.07, COL_BRASS)
    make_cyl("Espresso_FinialBall", (0.85, 4.38, 1.885), 0.055, 0.09, COL_BRASS, segments=12)
    make_cyl("Espresso_FinialTip", (0.85, 4.38, 1.955), 0.012, 0.05, COL_BRASS)
    # Groups + portafilters on the barista (north) side
    make_box("Espresso_DripTray", (0.85, 4.60, 1.11), (1.20, 0.18, 0.02), COL_CHROME)
    for gi, gx in enumerate((0.45, 0.85, 1.25)):
        make_cyl(f"Espresso_Group_{gi}", (gx, 4.60, 1.29), 0.050, 0.10, COL_CHROME)
        make_cyl(f"Espresso_Portafilter_{gi}", (gx, 4.60, 1.225), 0.052, 0.025, P.METAL_BLACK)
        make_cyl(f"Espresso_PFHandle_{gi}", (gx, 4.72, 1.225), 0.013, 0.16,
                 P.METAL_BLACK, axis='Y')
        make_cyl(f"Espresso_GroupCup_{gi}", (gx, 4.60, 1.145), 0.027, 0.048, COL_CREAM)
    for wi, wx in enumerate((0.12, 1.58)):
        make_cyl(f"Espresso_SteamWand_{wi}", (wx, 4.52, 1.30), 0.008, 0.20, COL_CHROME)
        make_cyl(f"Espresso_SteamKnob_{wi}", (wx, 4.52, 1.43), 0.024, 0.03, COL_WOOD_DARK, axis='X')
    # ── Pastry case (west end): croissants below (lines 309/392),
    #    cannoli + biscotti above. Frame + open front, NO glass. ──
    make_box("PastryCase_Tray", (-0.30, 4.32, 1.115), (0.85, 0.50, 0.03), COL_CHROME)
    for ci, (cxx, cyy) in enumerate([(-0.68, 4.11), (0.08, 4.11), (-0.68, 4.53), (0.08, 4.53)]):
        make_box(f"PastryCase_Post_{ci}", (cxx, cyy, 1.37), (0.045, 0.045, 0.48), COL_WOOD)
    make_box("PastryCase_Roof", (-0.30, 4.32, 1.625), (0.92, 0.56, 0.035), COL_WOOD)
    make_box("PastryCase_Back", (-0.30, 4.545, 1.37), (0.82, 0.025, 0.42), COL_WOOD)
    make_box("PastryCase_Shelf", (-0.30, 4.32, 1.38), (0.80, 0.42, 0.018), COL_GLASSISH)
    for ki in range(4):
        _croissant(f"Pastry_Croissant_{ki}", -0.52 + (ki % 2) * 0.24,
                   4.22 + (ki // 2) * 0.20, 1.13)
    for ni in range(3):
        make_cyl(f"Pastry_Cannolo_{ni}", (-0.52 + ni * 0.20, 4.28, 1.415),
                 0.021, 0.11, (0.82, 0.70, 0.50, 1.0), axis='X')
        make_cyl(f"Pastry_CannoloCream_{ni}", (-0.52 + ni * 0.20, 4.28, 1.415),
                 0.016, 0.124, COL_CREAM, axis='X')
    for bi in range(3):
        make_box(f"Pastry_Biscotti_{bi}", (0.18, 4.24 + bi * 0.05, 1.40 + bi * 0.022),
                 (0.13, 0.045, 0.022), COL_CRUST)
    make_box("Pastry_PriceCard", (-0.30, 4.09, 1.16), (0.09, 0.008, 0.06), P.PAPER)
    # ── Register zone (east) + the water-glass ritual (line 42) ──
    make_register("RegisterMachine", (2.95, 4.38, BAR_TOP),
                  palette={"body": (0.26, 0.25, 0.24, 1.0)})
    make_credit_card_terminal("CardTerminal", (2.52, 4.06, BAR_TOP))
    for col in range(2):
        for k in range(4):
            make_cyl(f"WaterGlass_Stack_{col}_{k}", (2.30 + col * 0.075, 4.45, 1.137 + k * 0.055),
                     0.030, 0.052, COL_GLASSISH)
    make_cyl("WaterCarafe_Body", (2.12, 4.52, 1.20), 0.052, 0.20, COL_CHROME, segments=12)
    make_box("WaterCarafe_Handle", (2.18, 4.52, 1.22), (0.016, 0.014, 0.09), COL_CHROME)
    for si in range(2):
        make_cyl(f"SugarDispenser_{si}", (1.70 + si * 0.10, 4.08, 1.155), 0.024, 0.11, COL_GLASSISH)
        make_cyl(f"SugarDispenser_{si}_Cap", (1.70 + si * 0.10, 4.08, 1.218), 0.019, 0.018, COL_CHROME)
    # A regular's stand-up setting left mid-bar — Marco's climate
    _espresso_setting("BarCup_Regular", 2.05, 4.14, BAR_TOP, drunk=True)
    _water_glass("BarGlass_Regular", 2.16, 4.20, BAR_TOP)
    make_cyl("TipBowl", (2.70, 4.10, 1.12), 0.048, 0.035, COL_BRASS, segments=12)
    # Card menus in a holder — "the menu she had already memorized"
    # (line 305). Lettering scene-side.
    make_box("MenuCard_Holder", (1.95, 4.42, 1.13), (0.05, 0.10, 0.06), COL_WOOD)
    make_box("MenuCard_Stack", (1.95, 4.42, 1.20), (0.012, 0.09, 0.13), P.PAPER)


# ═════════════════════════════════════════════════════════════════
# BACKBAR + NORTH WALL — grinders, knock box, moka pots, saucer
# stacks, espresso-tin pyramid, aranciata crate, sink; above: cup
# shelves, the clock frozen at 10:23 (the bell, line 174), two
# menu boards, fifty years of soccer — team photos, scudetto
# pennant, corner TV with the match on.
# ═════════════════════════════════════════════════════════════════
def build_backbar():
    make_box("Backbar_Body", (1.4, 5.65, 0.46), (4.20, 0.55, 0.92), COL_WOOD)
    make_box("Backbar_Top", (1.4, 5.65, 0.945), (4.30, 0.60, 0.05), COL_WOOD_DARK)
    make_box("Backbar_Kick", (1.4, 5.365, 0.08), (4.20, 0.02, 0.16), COL_WOOD_DARK)
    for di in range(5):
        dx = -0.28 + di * 0.84
        make_box(f"Backbar_Door_{di}", (dx, 5.362, 0.50), (0.70, 0.015, 0.68), COL_WHITE_PANEL)
        make_cyl(f"Backbar_Knob_{di}", (dx + 0.26, 5.352, 0.52), 0.014, 0.02, COL_BRASS, axis='Y')
    # Grinders — chrome bodies, bean hoppers (eye-level rounds)
    for gi, gx in enumerate((-0.25, 0.25)):
        make_box(f"Grinder_{gi}_Body", (gx, 5.62, 1.155), (0.20, 0.24, 0.37), COL_CHROME)
        make_cyl(f"Grinder_{gi}_Hopper", (gx, 5.62, 1.44), 0.078, 0.20, COL_GLASSISH, segments=12)
        make_cyl(f"Grinder_{gi}_Beans", (gx, 5.62, 1.40), 0.064, 0.10,
                 (0.22, 0.13, 0.08, 1.0), segments=12)
        make_cyl(f"Grinder_{gi}_Lid", (gx, 5.62, 1.55), 0.084, 0.02, P.METAL_BLACK)
        make_box(f"Grinder_{gi}_Doser", (gx, 5.48, 1.08), (0.05, 0.06, 0.08), P.METAL_BLACK)
    # Trophy — a small brass cup from some 1980s league Sunday
    make_box("Trophy_Plinth", (0.62, 5.68, 1.00), (0.09, 0.09, 0.06), COL_WOOD_DARK)
    make_cyl("Trophy_Stem", (0.62, 5.68, 1.07), 0.012, 0.08, COL_BRASS)
    make_cyl("Trophy_Bowl", (0.62, 5.68, 1.15), 0.045, 0.08, COL_BRASS, segments=12)
    for hi, sgn in enumerate((-1, +1)):
        make_box(f"Trophy_Handle_{hi}", (0.62 + sgn * 0.055, 5.68, 1.16),
                 (0.014, 0.012, 0.05), COL_BRASS)
    make_box("KnockBox", (0.95, 5.62, 1.03), (0.17, 0.17, 0.11), P.METAL_BLACK,
             open_faces={'+Z'})
    make_cyl("KnockBox_Bar", (0.95, 5.62, 1.082), 0.013, 0.15, COL_CHROME, axis='X')
    # Moka pots — decorative elders of the house
    for mi, mx in enumerate((1.22, 1.40)):
        make_cyl(f"MokaPot_{mi}_Base", (mx, 5.66, 1.015), 0.038, 0.09, COL_CHROME)
        make_cyl(f"MokaPot_{mi}_Waist", (mx, 5.66, 1.07), 0.026, 0.02, P.METAL_BLACK)
        make_cyl(f"MokaPot_{mi}_Top", (mx, 5.66, 1.125), 0.034, 0.09, COL_CHROME)
        make_box(f"MokaPot_{mi}_Handle", (mx + 0.045, 5.66, 1.12), (0.014, 0.012, 0.06),
                 P.METAL_BLACK)
    for si in range(6):
        make_cyl(f"SaucerStack_{si}", (1.68, 5.60, 0.978 + si * 0.011), 0.055, 0.010, COL_CREAM)
    # Espresso-tin pyramid (fifty years of the same brand)
    for ti, tx in enumerate((1.86, 1.96, 2.06)):
        make_cyl(f"EspressoTin_{ti}", (tx, 5.66, 1.033), 0.042, 0.125,
                 COL_TIN_RED if ti % 2 == 0 else COL_AZZURRO)
    for ti, tx in enumerate((1.91, 2.01)):
        make_cyl(f"EspressoTin_Top_{ti}", (tx, 5.66, 1.158), 0.042, 0.125,
                 COL_AZZURRO if ti % 2 == 0 else COL_TIN_RED)
    # Aranciata crate — orange cans in a wood crate
    make_box("AranciataCrate", (2.50, 5.64, 1.028), (0.40, 0.30, 0.115), COL_WOOD,
             open_faces={'+Z'})
    for ci in range(8):
        make_cyl(f"AranciataCan_{ci}", (2.36 + (ci % 4) * 0.094, 5.575 + (ci // 4) * 0.13, 1.045),
                 0.028, 0.088, COL_ORANGE)
    # Sink east end + folded rag
    make_box("Sink_Basin", (3.15, 5.63, 0.93), (0.40, 0.34, 0.09), COL_CHROME,
             open_faces={'+Z'})
    make_box("Sink_BasinFloor", (3.15, 5.63, 0.895), (0.38, 0.32, 0.008), (0.44, 0.46, 0.48, 1.0))
    make_cyl("Sink_FaucetRiser", (3.15, 5.80, 1.08), 0.013, 0.22, COL_CHROME)
    make_cyl("Sink_FaucetSpout", (3.15, 5.71, 1.18), 0.011, 0.18, COL_CHROME, axis='Y')
    make_box("Sink_Rag", (3.40, 5.60, 0.985), (0.14, 0.12, 0.025), (0.80, 0.78, 0.72, 1.0))
    # ── North wall (face y ≈ 5.86) ───────────────────────────────
    # THE CLOCK — frozen at 10:23, the minute the bell chimed and
    # the blue-dreadlocked woman entered the pattern (line 174).
    make_wall_clock("Clock", (-0.35, 5.86, 2.42), frozen_hour=10, frozen_min=23)
    # Cup shelves under the clock — demitasse ranks, one house style
    # (single-espresso institution: no mismatched-mug wall here)
    for si, sz in enumerate((1.55, 1.88)):
        make_box(f"CupShelf_{si}", (-0.30, 5.82, sz), (0.80, 0.16, 0.025), COL_WOOD)
        for ki, sgn in enumerate((-1, +1)):
            make_box(f"CupShelf_{si}_Bracket_{ki}", (-0.30 + sgn * 0.34, 5.865, sz - 0.05),
                     (0.03, 0.08, 0.09), P.METAL_BLACK)
        for mi in range(5):
            make_cyl(f"ShelfCup_{si}_{mi}", (-0.60 + mi * 0.15, 5.82, sz + 0.038),
                     0.030, 0.05, COL_CREAM)
    # Menu boards over the machine (lettering scene-side)
    for bi in range(2):
        bx = 0.55 + bi * 1.0
        make_box(f"MenuBoard_{bi}_Frame", (bx, 5.86, 2.42), (0.92, 0.03, 0.62), COL_WOOD)
        make_box(f"MenuBoard_{bi}", (bx, 5.845, 2.42), (0.84, 0.02, 0.54), COL_SLATE)
        make_box(f"MenuBoard_{bi}_Header", (bx, 5.83, 2.61), (0.50, 0.006, 0.07), COL_CHALK)
        for ri in range(3):
            make_box(f"MenuBoard_{bi}_Row_{ri}", (bx - 0.07, 5.83, 2.50 - ri * 0.11),
                     (0.54, 0.006, 0.035), COL_CHALK)
            make_box(f"MenuBoard_{bi}_Price_{ri}", (bx + 0.30, 5.83, 2.50 - ri * 0.11),
                     (0.09, 0.006, 0.035), COL_CHALK)
    # Scudetto pennant + framed team photos (sepia decades)
    make_box("Scudetto_Body", (2.10, 5.87, 2.50), (0.16, 0.02, 0.18), COL_AZZURRO)
    make_box("Scudetto_Tip", (2.10, 5.87, 2.375), (0.08, 0.02, 0.07), COL_AZZURRO)
    make_box("Scudetto_Crest", (2.10, 5.855, 2.52), (0.07, 0.01, 0.08), COL_BRASS)
    for fi, (fx, fz) in enumerate([(2.45, 2.32), (2.80, 2.56), (2.80, 2.24)]):
        make_box(f"SoccerPhoto_{fi}_Frame", (fx, 5.87, fz), (0.30, 0.025, 0.24), COL_WOOD_DARK)
        make_box(f"SoccerPhoto_{fi}_Print", (fx, 5.855, fz), (0.25, 0.012, 0.19), COL_SEPIA)
        make_box(f"SoccerPhoto_{fi}_TeamRow", (fx, 5.845, fz - 0.03), (0.21, 0.006, 0.05),
                 COL_SEPIA_INK)
    # Corner TV, the match on with the sound off (NE, up high)
    make_box("TV_Bracket", (3.45, 5.92, 2.42), (0.08, 0.10, 0.08), P.METAL_BLACK)
    make_box("TV_Body", (3.45, 5.80, 2.56), (0.72, 0.06, 0.44), P.METAL_BLACK)
    make_box("TV_Screen", (3.45, 5.765, 2.56), (0.64, 0.012, 0.36), COL_PITCH)
    make_box("TV_ScoreBand", (3.28, 5.757, 2.70), (0.22, 0.006, 0.045), (0.88, 0.88, 0.84, 1.0))
    for pi in range(4):
        make_box(f"TV_Player_{pi}", (3.28 + pi * 0.11, 5.757, 2.49 + (pi % 2) * 0.06),
                 (0.018, 0.006, 0.032), (0.90, 0.90, 0.88, 1.0) if pi % 2 == 0 else COL_AZZURRO_LT)
    # Azzurro-and-white bunting strung across the room over the bar
    make_cyl("Bunting_Cord", (0.0, 4.90, 2.72), 0.006, 7.20, P.TWINE, axis='X')
    for pi in range(9):
        px = -3.2 + pi * 0.8
        tint = COL_AZZURRO if pi % 2 == 0 else (0.90, 0.89, 0.85, 1.0)
        if pi % 4 == 3:
            tint = COL_TIN_RED
        make_box(f"Bunting_Flag_{pi}", (px, 4.90, 2.615), (0.15, 0.012, 0.19), tint)
        make_box(f"Bunting_FlagTip_{pi}", (px, 4.90, 2.475), (0.075, 0.012, 0.09), tint)


# ═════════════════════════════════════════════════════════════════
# SEATING — John's back-corner table under the west window (the
# whole chapter happens here), the SE front-window two-top where
# the blue-dreadlocked woman meets the man with the cardboard tube,
# a mid-floor two-top with the Gazzetta, the west window ledge with
# stools, an east standing ledge. Terrible chairs throughout.
# ═════════════════════════════════════════════════════════════════
def build_seating():
    # ── JOHN'S TABLE (line 46) — NW back corner, under the window.
    _metal_table("JohnTable", -3.05, 4.70, r=0.30)
    _bistro_chair("JohnChair", -3.05, 5.38, 'S')       # John, back to the light
    _bistro_chair("EliciaChair", -3.05, 4.02, 'N')     # Elicia, across
    # His single espresso (mostly drunk — line 408) + the water glass
    _espresso_setting("JohnCup", -3.14, 4.82, 0.74, drunk=True)
    _water_glass("JohnWaterGlass", -2.99, 4.88, 0.74)
    _espresso_setting("EliciaCup", -3.16, 4.58, 0.74)
    # The notebook, open — six years of dust-mote notes (line 182)
    make_box("JohnNotebook_Cover", (-2.90, 4.66, 0.742), (0.315, 0.225, 0.006), COL_WOOD_DARK)
    make_box("JohnNotebook_PageL", (-2.975, 4.66, 0.747), (0.145, 0.205, 0.004), P.PAPER)
    make_box("JohnNotebook_PageR", (-2.825, 4.66, 0.747), (0.145, 0.205, 0.004), P.PAPER)
    for ni in range(4):
        make_box(f"JohnNotebook_InkLine_{ni}", (-2.975, 4.725 - ni * 0.038, 0.7495),
                 (0.105, 0.005, 0.0012), COL_SEPIA_INK)
    make_cyl("JohnPen", (-2.86, 4.535, 0.752), 0.005, 0.13, P.METAL_BLACK, axis='X')
    # The croissants (lines 309–334, 392): kraft bag, one whole, one
    # broken — the larger half handed to John, the smaller Elicia's.
    make_box("CroissantBag", (-2.95, 4.93, 0.775), (0.15, 0.115, 0.095), COL_KRAFT)
    make_box("CroissantBag_Fold", (-2.95, 4.93, 0.828), (0.16, 0.125, 0.014), (0.62, 0.48, 0.32, 1.0))
    make_cyl("CroissantPlate", (-3.05, 4.44, 0.746), 0.062, 0.012, COL_CREAM, segments=12)
    _croissant_half("CroissantHalf_John", -3.09, 4.45, 0.752, big=True)
    _croissant_half("CroissantHalf_Elicia", -3.00, 4.42, 0.752, big=False)
    _croissant("CroissantWhole", -2.88, 4.94, 0.834)
    # ── THE WINDOW TABLE (lines 174/178) — SE front window: the
    # blue-dreadlocked woman + the man; two coffees; the tube CLOSED.
    _metal_table("WindowTable", 2.60, 1.00, r=0.30)
    _bistro_chair("WindowChair_0", 1.95, 1.00, 'E')
    _bistro_chair("WindowChair_1", 3.25, 1.00, 'W')
    _espresso_setting("WindowCup_0", 2.48, 1.12, 0.74)
    _espresso_setting("WindowCup_1", 2.72, 0.88, 0.74)
    make_cyl("CardboardTube", (2.60, 0.98, 0.785), 0.045, 0.62, COL_KRAFT, axis='X')
    for ei, sgn in enumerate((-1, +1)):
        make_cyl(f"CardboardTube_Cap_{ei}", (2.60 + sgn * 0.315, 0.98, 0.785), 0.047, 0.018,
                 (0.50, 0.38, 0.26, 1.0), axis='X')
    # ── Mid-floor two-top — pink Gazzetta left by the morning shift
    _metal_table("MidTable", -1.70, 2.50, r=0.30)
    _bistro_chair("MidChair_0", -2.35, 2.50, 'E')
    _bistro_chair("MidChair_1", -1.70, 3.15, 'S')
    make_box("Gazzetta", (-1.62, 2.42, 0.746), (0.24, 0.17, 0.008), COL_GAZZETTA)
    make_box("Gazzetta_Headline", (-1.62, 2.475, 0.751), (0.20, 0.045, 0.002), COL_SEPIA_INK)
    _espresso_setting("MidCup", -1.82, 2.60, 0.74, drunk=True)
    # ── West front-window ledge + stools (window-watching seats)
    make_box("WindowLedge_W_Top", (-2.45, 0.33, 1.045), (1.90, 0.28, 0.045), COL_WOOD)
    for bi, bx in enumerate((-3.15, -2.45, -1.75)):
        make_box(f"WindowLedge_W_Bracket_{bi}", (bx, 0.26, 0.81), (0.05, 0.14, 0.42), COL_WOOD_DARK)
    _stool("WindowStool_0", -2.85, 0.78)
    _stool("WindowStool_1", -2.05, 0.78)
    _espresso_setting("LedgeCup", -2.75, 0.34, 1.0675, drunk=True)
    # ── East wall standing ledge — more stand-up culture
    make_box("StandLedge_E_Top", (3.76, 2.75, 1.05), (0.28, 1.50, 0.045), COL_WOOD)
    for bi, by in enumerate((2.15, 2.75, 3.35)):
        make_box(f"StandLedge_E_Bracket_{bi}", (3.84, by, 0.82), (0.12, 0.05, 0.42), COL_WOOD_DARK)
    _stool("StandStool_E", 3.42, 2.42)
    _water_glass("StandLedge_Glass", 3.76, 3.05, 1.0725)


# ═════════════════════════════════════════════════════════════════
# WALL DRESSING — decades that read as loved, not tired: sepia
# photos of the café itself on the west wall, the framed azzurro
# jersey + aperitivo poster (big warm disc — the Sun hides in the
# advertising) + payphone + coat pegs east, radiator under John's
# window, tomato-can basil on the east window ledge.
# ═════════════════════════════════════════════════════════════════
def build_walls_decor():
    wf_w = -3.90   # west wall inner face
    wf_e = +3.90   # east wall inner face
    # Fifty years of the same room — three sepia house photos
    for fi, (fy, fz) in enumerate([(1.50, 1.85), (2.10, 2.02), (2.70, 1.85)]):
        make_box(f"HistoryPhoto_{fi}_Frame", (wf_w + 0.012, fy, fz), (0.03, 0.32, 0.26), COL_WOOD_DARK)
        make_box(f"HistoryPhoto_{fi}_Print", (wf_w + 0.030, fy, fz), (0.012, 0.26, 0.20), COL_SEPIA)
        make_box(f"HistoryPhoto_{fi}_Figure", (wf_w + 0.038, fy - 0.03, fz - 0.02),
                 (0.006, 0.09, 0.12), COL_SEPIA_INK)
    # Cast-iron radiator under John's window (Montreal interior tell)
    for ri in range(8):
        make_cyl(f"Radiator_Fin_{ri}", (-3.80, 4.365 + ri * 0.096, 0.38), 0.032, 0.52,
                 (0.62, 0.60, 0.56, 1.0))
    make_cyl("Radiator_TopPipe", (-3.80, 4.70, 0.66), 0.020, 0.76, (0.62, 0.60, 0.56, 1.0), axis='Y')
    make_cyl("Radiator_Valve", (-3.80, 4.30, 0.20), 0.028, 0.05, COL_BRASS, axis='Y')
    # East wall: framed Azzurri jersey over the standing ledge
    make_box("Jersey_Frame", (wf_e - 0.012, 2.75, 1.95), (0.03, 0.62, 0.74), COL_WOOD_DARK)
    make_box("Jersey_Mat", (wf_e - 0.030, 2.75, 1.95), (0.012, 0.54, 0.66), (0.88, 0.87, 0.83, 1.0))
    make_box("Jersey_Torso", (wf_e - 0.042, 2.75, 1.90), (0.012, 0.34, 0.42), COL_AZZURRO)
    for si, sgn in enumerate((-1, +1)):
        make_box(f"Jersey_Sleeve_{si}", (wf_e - 0.042, 2.75 + sgn * 0.235, 2.04),
                 (0.012, 0.13, 0.20), COL_AZZURRO)
    make_box("Jersey_Collar", (wf_e - 0.048, 2.75, 2.115), (0.006, 0.10, 0.035),
             (0.90, 0.89, 0.85, 1.0))
    make_box("Jersey_Number", (wf_e - 0.050, 2.75, 1.90), (0.006, 0.11, 0.15),
             (0.90, 0.89, 0.85, 1.0))
    # Aperitivo poster — a big warm disc over vintage lettering (the
    # Sun card hiding in a 1960s ad), hand-built ON the wall face
    # (make_faded_poster buries its panel inside our wall thickness)
    make_box("Poster_Aperitivo_Body", (wf_e - 0.010, 1.15, 1.85), (0.014, 0.56, 0.78), P.PAPER_AGED)
    make_cyl("Poster_Aperitivo_Disc", (wf_e - 0.020, 1.15, 2.00), 0.19, 0.008, COL_ORANGE, axis='X',
             segments=14)
    make_box("Poster_Aperitivo_Title", (wf_e - 0.020, 1.15, 1.58), (0.006, 0.44, 0.09), COL_SEPIA_INK)
    # Payphone — the institution never took it down
    make_payphone("Payphone", (wf_e + 0.04, 3.85, 1.35))
    # Coat pegs by the door — ONE light spring jacket (dry late May;
    # canon-negative: no rain slickers on the wall, Tem wears hers)
    make_box("CoatPegs_Rail", (wf_e - 0.015, 0.62, 1.66), (0.03, 0.66, 0.07), COL_WOOD)
    for hi, hy in enumerate((0.42, 0.62, 0.82)):
        make_cyl(f"CoatPegs_Peg_{hi}", (wf_e - 0.055, hy, 1.64), 0.013, 0.09, COL_BRASS, axis='X')
    make_box("SpringJacket_Body", (wf_e - 0.10, 0.42, 1.32), (0.06, 0.30, 0.56),
             (0.42, 0.46, 0.54, 1.0))
    make_box("SpringJacket_Collar", (wf_e - 0.10, 0.42, 1.62), (0.07, 0.20, 0.08),
             (0.34, 0.38, 0.46, 1.0))
    # East window ledge — basil in a tomato can (Italian kitchen tell)
    make_cyl("BasilCan", (2.20, 0.16, 0.665), 0.042, 0.11, COL_TIN_RED)
    make_box("BasilCan_Label", (2.20, 0.115, 0.665), (0.06, 0.006, 0.07), P.PAPER)
    for li in range(4):
        make_cyl(f"BasilLeaf_{li}", (2.20 + ((li * 7) % 3 - 1) * 0.025,
                 0.16 + ((li * 5) % 3 - 1) * 0.02, 0.745 + (li % 2) * 0.03),
                 0.024, 0.045, COL_LEAF)


# ═════════════════════════════════════════════════════════════════
# THE DUST MOTES — the chapter is subtitled "Pattern Recognition in
# Dust Motes" (line 46: "the dust motes were part of what you paid
# for"). Primary cluster: the shaft slanting from the west window
# down across John's table. Secondary cluster over the window table
# — "secondary clustering around the new arrival" (line 182).
# Deterministic seed arithmetic; tiny sun-bright specks the glow
# pass can catch.
# ═════════════════════════════════════════════════════════════════
def build_dust_motes():
    # Primary shaft: from the window plane (x −3.9, z 2.25) down to
    # just above the tabletop (x −2.7, z 0.85)
    for i in range(22):
        t = i / 21.0
        mx = -3.85 + 1.15 * t + (((i * 5) % 7) / 7.0 - 0.5) * 0.24
        mz = 2.22 - 1.34 * t + (((i * 11) % 9) / 9.0 - 0.5) * 0.20
        my = 4.16 + ((i * 7) % 12) / 12.0 * 1.10
        s = 0.012 + ((i * 3) % 4) * 0.004
        make_box(f"DustMote_{i}", (mx, my, mz), (s, s, s), COL_SUNGLOW)
    # Four low motes doing their ballet right over the notebook
    for i in range(4):
        make_box(f"DustMote_Low_{i}", (-3.02 + ((i * 5) % 4) * 0.06,
                 4.52 + ((i * 7) % 5) * 0.07, 0.82 + ((i * 3) % 3) * 0.09),
                 (0.012, 0.012, 0.012), COL_SUNGLOW)
    # Secondary cluster — around the new arrival at the window table
    for i in range(8):
        make_box(f"DustMote_Window_{i}", (2.36 + ((i * 7) % 6) * 0.09,
                 0.70 + ((i * 5) % 5) * 0.12, 1.28 + ((i * 11) % 7) * 0.11),
                 (0.011, 0.011, 0.011), COL_SUNGLOW)


# ═════════════════════════════════════════════════════════════════
# CEILING — globe pendants (circles of warm light: the Sun motif),
# one old ceiling fan on a medallion to keep the motes moving,
# smoke detector, speaker, one discreet vent. NO fluorescent grid.
# ═════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    for nm, px, py, drop in [
            ("Pendant_Bar_0", -0.50, 3.80, 0.75), ("Pendant_Bar_1", 1.40, 3.80, 0.75),
            ("Pendant_Bar_2", 3.00, 3.80, 0.75),
            ("Pendant_John", -3.05, 4.70, 0.90), ("Pendant_Mid", -1.70, 2.50, 0.90),
            ("Pendant_Window", 2.60, 1.00, 0.90)]:
        _globe_pendant(nm, px, py, drop=drop)
    # Ceiling fan — off the camera axis, over the mid floor
    make_cyl("Fan_Medallion", (-0.90, 2.90, CEIL - 0.012), 0.16, 0.024, COL_CREAM, segments=14)
    make_cyl("Fan_Downrod", (-0.90, 2.90, CEIL - 0.15), 0.012, 0.28, P.METAL_BLACK)
    make_cyl("Fan_Motor", (-0.90, 2.90, CEIL - 0.30), 0.09, 0.14, COL_BRASS, segments=12)
    for bi, (bx, by, bsz) in enumerate([
            (+0.31, 0.0, (0.50, 0.11, 0.012)), (-0.31, 0.0, (0.50, 0.11, 0.012)),
            (0.0, +0.31, (0.11, 0.50, 0.012)), (0.0, -0.31, (0.11, 0.50, 0.012))]):
        make_box(f"Fan_Blade_{bi}", (-0.90 + bx, 2.90 + by, CEIL - 0.345), bsz, COL_WOOD_DARK)
    make_cyl("Fan_Globe", (-0.90, 2.90, CEIL - 0.43), 0.065, 0.10, COL_SUNGLOW, segments=12)
    make_smoke_detector("Smoke", (0.8, 1.8, CEIL))
    make_ceiling_speaker("Speaker", (-2.0, 1.4, CEIL))
    make_hvac_vent("HVAC", (2.2, 3.4, CEIL), width=0.70, depth=0.36)


def main():
    clear_scene()
    build_shell()
    build_storefront()
    build_exterior()
    build_bar()
    build_backbar()
    build_seating()
    build_walls_decor()
    build_dust_motes()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/cafe_olimpico.glb"))
    print(f"\n[build_cafe_olimpico] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
