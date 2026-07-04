"""The Daily Grind — front room — vol7 hero locale (Smolvud, OR).

Lena Vargas's morning workplace, corner of Cedar and Hemlock
(vol7_epilogue_gallery). Soren's shop; he roasts the dark French
Petra drinks (vol7_ch8_monday). PNW 2025 register — warm wood,
mismatched furniture, rain gear by the door — NOT the diner's 90s
operator-noir. Canon sources baked in:

  · vol7_ch2_morning: Lena unlocks the BACK DOOR first — it wakes
    the heat-pump compressor that runs the hot-water lines for the
    espresso bar; she fills the CERAMIC MILK PITCHERS from the
    cooler and sets them on the bar in the order the regulars like
    their drinks pulled; the BELL over the door rings at six-eleven;
    WREN'S CORNER TABLE (hot chocolate, the hand-cut marshmallow
    from the slab Hans the baker sells the Grind); the cortado man.
  · vol7_ch2_afternoon: Tem + Kai + Finn at the corner table —
    Finn "sat in the fourth chair" (the corner table seats four);
    "Soren was in the back"; slate-gray rain-light through the
    front window.
  · vol7_ch8_monday + music_catalog vol7_daily_grind: "the bell at
    eleven fifty-fifty-eight, rain-light at the counter" — the wall
    clock is frozen at 11:58.
  · lore/milk_and_honey/static_truths.md: "contact: the small box
    at the daily grind by the front register. mark it for l.v." —
    the contact box + a stack of Static Truths issues live beside
    the register; "the crow that sits on the railing of the Daily
    Grind every morning when I open" — the railing outside the
    storefront, crow included; the Issue #1 cover image (a coffee
    cup on a saucer on a small porch table, railing behind) is the
    porch two-top outside the west end of the storefront.
  · lore/_VOL6_VOL7_LOCALES_MANIFEST.md: Mrs. Gable's morning seat,
    Per's regular table, back-room office, counter + 4-5 small
    tables.
  · lore/_VOL7_WIKI.md: Lena is a painter (Tide Pool Geometries /
    octopus studies — two of her pieces hang on the west wall);
    Smolvud runs on tokens (the tip jar holds them).

Big storefront windows are REAL OPENINGS with wood frames +
mullions, no glass (playbook no-transparency rule) — rain-light is
the whole mood, so a sidewalk apron, the railing, the crow, and a
wet street live outside the openings. The back-room door in the
north wall is the seam to Soren's back room / Lena's studio
(separate space, closed wood door).

Text on menu boards / zine covers / signs is scene-side Label3D
per the playbook; this script bakes named vertex-colored panels:
  MenuBoard_{0..2}, Zine_StaticTruths, StaticTruths_ContactBox,
  OpenSign_Board, BackDoor_Sign, AFrame_Board, TipJar_Label.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import (make_floor, make_wall, make_ceiling,
                              make_crown_molding, make_door_hinges)
from _props.store_fixtures import make_register, make_credit_card_terminal
from _props.food_service import make_sugar_creamer_caddy, make_paper_cup_stack
from _props.decor import make_wall_clock, make_floor_plant, make_fire_extinguisher
from _props.safety import make_smoke_detector, make_hvac_vent, make_ceiling_speaker
from _props.signage import make_paper_notices_wall
from _props.cleaning import make_trash_can

# ── Shell (footprint kept from the scaffold — the .tscn camera and
#    lights are tuned to this 7 × 6 room, door gap x −1..+1) ──────
ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 2.8
PAL_WALL = {"wall": (0.82, 0.79, 0.72, 1.0), "baseboard": (0.30, 0.24, 0.18, 1.0)}
COL_FLOOR = (0.55, 0.42, 0.30, 1.0)      # fir floorboards
COL_SEAM  = (0.33, 0.25, 0.18, 1.0)

# ── Coffee-shop palette (PNW 2025, warm-sunset saturation) ───────
COL_WOOD      = (0.48, 0.35, 0.22, 1.0)   # walnut fixtures
COL_WOOD_DARK = (0.28, 0.21, 0.15, 1.0)
COL_WOOD_LT   = (0.66, 0.52, 0.34, 1.0)   # lighter plank alternate
COL_BUTCHER   = (0.72, 0.58, 0.38, 1.0)   # bar top
COL_SAGE      = (0.46, 0.53, 0.44, 1.0)   # espresso machine enamel
COL_BRASS     = (0.70, 0.57, 0.30, 1.0)
COL_CREAM     = (0.90, 0.87, 0.80, 1.0)   # ceramic
COL_SLATE     = (0.15, 0.16, 0.15, 1.0)   # menu chalkboards
COL_CHALK     = (0.88, 0.88, 0.82, 1.0)
COL_GLASSISH  = (0.72, 0.78, 0.78, 1.0)   # opaque stand-in for jar glass
COL_AMBER     = (0.62, 0.42, 0.22, 1.0)   # carafe coffee
COL_BEAN      = (0.22, 0.13, 0.08, 1.0)
COL_COCOA     = (0.36, 0.22, 0.14, 1.0)
COL_BURLAP    = (0.62, 0.50, 0.34, 1.0)
COL_CORK      = (0.60, 0.45, 0.30, 1.0)
COL_PLANT     = (0.36, 0.47, 0.32, 1.0)
COL_POT       = (0.58, 0.38, 0.26, 1.0)   # terracotta
COL_RAINCOAT  = (0.38, 0.36, 0.26, 1.0)   # wax canvas (Roy-adjacent town uniform)
COL_CROW      = (0.10, 0.10, 0.13, 1.0)
COL_CONCRETE  = (0.55, 0.54, 0.51, 1.0)
COL_ASPHALT   = (0.15, 0.15, 0.16, 1.0)   # rain-dark street
COL_PUDDLE    = (0.30, 0.33, 0.36, 1.0)
COL_UPHOLSTER = (0.55, 0.32, 0.22, 1.0)   # rust wool armchair
# Mismatched mugs / chairs — muted per house warm-sunset rule
MUG_TINTS = [
    (0.72, 0.30, 0.22, 1.0),   # rust red
    (0.34, 0.48, 0.46, 1.0),   # teal
    (0.82, 0.64, 0.28, 1.0),   # mustard
    (0.38, 0.44, 0.56, 1.0),   # dusty blue
    (0.46, 0.53, 0.44, 1.0),   # sage
    (0.90, 0.87, 0.80, 1.0),   # cream
]
CHAIR_TINTS = [COL_WOOD, (0.34, 0.48, 0.46, 1.0), COL_WOOD_DARK, (0.62, 0.34, 0.22, 1.0)]

BAR_TOP = 0.98        # bar counter top surface z
BACKBAR_TOP = 0.94    # backbar cabinet top surface z


# ═════════════════════════════════════════════════════════════════
# Local furniture helpers (deterministic, axis-aligned)
# ═════════════════════════════════════════════════════════════════
_DIRS = {'N': (0.0, 1.0), 'S': (0.0, -1.0), 'E': (1.0, 0.0), 'W': (-1.0, 0.0)}

def _chair(prefix, cx, cy, facing, tint):
    """Cafe chair. `facing` is the direction the sitter faces; the
    backrest goes on the opposite edge of the seat."""
    dx, dy = _DIRS[facing]
    make_box(f"{prefix}_Seat", (cx, cy, 0.45), (0.40, 0.40, 0.04), tint)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"{prefix}_Leg_{li}", (cx + sx * 0.16, cy + sy * 0.16, 0.225),
                 0.018, 0.45, COL_WOOD_DARK)
    bx, by = cx - dx * 0.19, cy - dy * 0.19
    for pi, sgn in enumerate((-1, +1)):
        px = bx + (sgn * 0.16 if dx == 0 else 0.0)
        py = by + (sgn * 0.16 if dy == 0 else 0.0)
        make_cyl(f"{prefix}_BackPost_{pi}", (px, py, 0.675), 0.016, 0.45, tint)
    slat_sz = (0.36, 0.03, 0.09) if dx == 0 else (0.03, 0.36, 0.09)
    for si, sz_z in enumerate((0.72, 0.86)):
        make_box(f"{prefix}_Slat_{si}", (bx, by, sz_z), slat_sz, tint)

def _stool(prefix, cx, cy):
    make_cyl(f"{prefix}_Seat", (cx, cy, 0.70), 0.17, 0.045, COL_WOOD, segments=12)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"{prefix}_Leg_{li}", (cx + sx * 0.10, cy + sy * 0.10, 0.34),
                 0.016, 0.68, P.METAL_BLACK)
    for ri, (rx, ry, rsz) in enumerate([
            (0.0, -0.10, (0.20, 0.02, 0.02)), (0.0, +0.10, (0.20, 0.02, 0.02)),
            (-0.10, 0.0, (0.02, 0.20, 0.02)), (+0.10, 0.0, (0.02, 0.20, 0.02))]):
        make_box(f"{prefix}_Rung_{ri}", (cx + rx, cy + ry, 0.22), rsz, P.METAL_BLACK)

def _round_table(prefix, cx, cy, r, tint):
    make_cyl(f"{prefix}_Top", (cx, cy, 0.74), r, 0.04, tint, segments=12)
    make_cyl(f"{prefix}_Column", (cx, cy, 0.38), 0.045, 0.68, COL_WOOD_DARK)
    make_cyl(f"{prefix}_Base", (cx, cy, 0.025), r * 0.55, 0.05, COL_WOOD_DARK, segments=12)

def _square_table(prefix, cx, cy, w, tint):
    make_box(f"{prefix}_Top", (cx, cy, 0.74), (w, w, 0.04), tint)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"{prefix}_Leg_{li}", (cx + sx * (w / 2 - 0.06), cy + sy * (w / 2 - 0.06),
                 0.36), 0.022, 0.72, COL_WOOD_DARK)

def _pendant(prefix, cx, cy, drop=0.62, shade=COL_SAGE):
    """Cylinder-shade pendant — round geometry at eye level per playbook."""
    make_cyl(f"{prefix}_Canopy", (cx, cy, CEIL - 0.02), 0.05, 0.04, P.METAL_BLACK)
    make_cyl(f"{prefix}_Cord", (cx, cy, CEIL - drop / 2.0), 0.008, drop, P.METAL_BLACK)
    make_cyl(f"{prefix}_Shade", (cx, cy, CEIL - drop - 0.065), 0.15, 0.13, shade, segments=12)
    make_cyl(f"{prefix}_Bulb", (cx, cy, CEIL - drop - 0.135), 0.05, 0.04,
             (0.98, 0.88, 0.62, 1.0))

def _mug(prefix, cx, cy, bz, tint):
    make_cyl(f"{prefix}_Body", (cx, cy, bz + 0.048), 0.038, 0.095, tint)
    make_box(f"{prefix}_Handle", (cx + 0.048, cy, bz + 0.050), (0.016, 0.014, 0.05), tint)

def _cup_saucer(prefix, cx, cy, bz, tint):
    make_cyl(f"{prefix}_Saucer", (cx, cy, bz + 0.006), 0.062, 0.012, COL_CREAM, segments=12)
    make_cyl(f"{prefix}_Cup", (cx, cy, bz + 0.045), 0.036, 0.065, tint)
    make_box(f"{prefix}_Handle", (cx + 0.045, cy, bz + 0.045), (0.014, 0.012, 0.04), tint)


# ═════════════════════════════════════════════════════════════════
# SHELL — walls with the storefront + corner-window openings carved
# out of the same wall planes the scaffold used (camera-safe), the
# back-room door gap in the north wall, fir floor, plank ceiling.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # East wall — solid (hooks / corkboard / retail shelf live here)
    make_wall("Wall_E", (ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    # West wall — window opening y 0.9..2.7 (sill 0.75, head 2.30)
    make_wall("Wall_W_S", (-ROOM_W / 2.0, 0.35, 0), length=1.10, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_W_N", (-ROOM_W / 2.0, 4.45, 0), length=3.50, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_W_Sill", (-ROOM_W / 2.0, 1.8, 0.375), (0.20, 1.80, 0.75), PAL_WALL["wall"])
    make_box("Wall_W_SillBase", (-ROOM_W / 2.0 + 0.06, 1.8, 0.08), (0.06, 1.80, 0.16),
             PAL_WALL["baseboard"])
    make_box("Wall_W_Header", (-ROOM_W / 2.0, 1.8, 2.55), (0.20, 1.80, 0.50), PAL_WALL["wall"])
    # North wall — back-room door gap x −2.9..−1.9
    make_wall("Wall_N_W", (-3.3, ROOM_D, 0), length=0.80, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (0.9, ROOM_D, 0), length=5.60, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_N_AboveDoor", (-2.4, ROOM_D, 2.50), (1.0, 0.20, 0.60), PAL_WALL["wall"])
    # South (storefront) wall — door gap x −1..+1, window openings
    # x −3.1..−1.3 and +1.3..+3.1 (sill 0.75, head 2.30)
    for nm, px, pw in [("Wall_S_PierSW", -3.30, 0.40), ("Wall_S_PierWD", -1.15, 0.30),
                       ("Wall_S_PierED", +1.15, 0.30), ("Wall_S_PierSE", +3.30, 0.40)]:
        make_box(nm, (px, 0.0, CEIL / 2.0), (pw, 0.20, CEIL), PAL_WALL["wall"])
    for tag, wx in [("W", -2.2), ("E", +2.2)]:
        make_box(f"Wall_S_{tag}_Sill", (wx, 0.0, 0.375), (1.80, 0.20, 0.75), PAL_WALL["wall"])
        make_box(f"Wall_S_{tag}_SillBase", (wx, 0.06, 0.08), (1.80, 0.06, 0.16),
                 PAL_WALL["baseboard"])
        make_box(f"Wall_S_{tag}_Header", (wx, 0.0, 2.55), (1.80, 0.20, 0.50), PAL_WALL["wall"])
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.28), (2.0, 0.20, 0.56), PAL_WALL["wall"])
    # Ceiling — painted planks with wood battens (2025 shop, no drop grid)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
                 palette={"tile": (0.80, 0.75, 0.66, 1.0), "grid": (0.46, 0.35, 0.24, 1.0)},
                 with_stains=False)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W / 2.0 + 0.10, ROOM_D / 2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W / 2.0 - 0.10, ROOM_D / 2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D - 0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_WOOD})


# ═════════════════════════════════════════════════════════════════
# STOREFRONT — wood frames + mullions in the empty openings (no
# glass per playbook), the front door, the canon bell over it, the
# hanging OPEN sign, entry mat, umbrella stand, window succulents.
# ═════════════════════════════════════════════════════════════════
def _window_frame_south(tag, wx):
    """Frame + mullion grid for a south-wall opening centered at wx.
    Opening: 1.8 wide, z 0.75..2.30, transom bar at 1.95."""
    make_box(f"WinS_{tag}_Sill", (wx, 0.0, 0.735), (1.92, 0.22, 0.07), COL_WOOD)
    make_box(f"WinS_{tag}_Ledge", (wx, 0.14, 0.775), (1.80, 0.14, 0.03), COL_WOOD)
    make_box(f"WinS_{tag}_Head", (wx, 0.0, 2.315), (1.92, 0.22, 0.07), COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"WinS_{tag}_Jamb_{sgn:+d}", (wx + sgn * 0.93, 0.0, 1.525),
                 (0.06, 0.22, 1.65), COL_WOOD)
    for mi, mx in enumerate((-0.6, +0.6)):
        make_box(f"WinS_{tag}_MullV_{mi}", (wx + mx, 0.0, 1.525), (0.05, 0.14, 1.55), COL_WOOD)
    make_box(f"WinS_{tag}_Transom", (wx, 0.0, 1.95), (1.80, 0.14, 0.05), COL_WOOD)

def build_storefront():
    _window_frame_south("W", -2.2)
    _window_frame_south("E", +2.2)
    # West (Cedar-side) corner window — same treatment, Y-axis wall
    make_box("WinW_Sill", (-3.5, 1.8, 0.735), (0.22, 1.92, 0.07), COL_WOOD)
    make_box("WinW_Ledge", (-3.36, 1.8, 0.775), (0.14, 1.80, 0.03), COL_WOOD)
    make_box("WinW_Head", (-3.5, 1.8, 2.315), (0.22, 1.92, 0.07), COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"WinW_Jamb_{sgn:+d}", (-3.5, 1.8 + sgn * 0.93, 1.525),
                 (0.22, 0.06, 1.65), COL_WOOD)
    for mi, my in enumerate((1.2, 2.4)):
        make_box(f"WinW_MullV_{mi}", (-3.5, my, 1.525), (0.14, 0.05, 1.55), COL_WOOD)
    make_box("WinW_Transom", (-3.5, 1.8, 1.95), (0.14, 1.80, 0.05), COL_WOOD)
    # Succulents on the west sill ledge (PNW shop greenery)
    for si, sy in enumerate((1.45, 2.15)):
        make_cyl(f"SillSucculent_{si}_Pot", (-3.36, sy, 0.815), 0.035, 0.05, COL_POT)
        make_cyl(f"SillSucculent_{si}_Leaf", (-3.36, sy, 0.865), 0.028, 0.05, COL_PLANT)
    # Door surround + wood-framed door leaf (west half), no glass
    for sgn in (-1, +1):
        make_box(f"DoorPost_{sgn:+d}", (sgn * 0.96, 0.0, 1.10), (0.08, 0.16, 2.20), COL_WOOD)
    make_box("DoorTransom", (0.0, 0.0, 2.24), (2.00, 0.16, 0.08), COL_WOOD)
    make_box("Door_Stile_W", (-0.88, 0.0, 1.08), (0.07, 0.05, 2.10), COL_WOOD_DARK)
    make_box("Door_Stile_E", (-0.12, 0.0, 1.08), (0.07, 0.05, 2.10), COL_WOOD_DARK)
    make_box("Door_Rail_Top", (-0.50, 0.0, 2.08), (0.83, 0.05, 0.09), COL_WOOD_DARK)
    make_box("Door_Rail_Mid", (-0.50, 0.0, 0.92), (0.83, 0.05, 0.07), COL_WOOD_DARK)
    make_box("Door_KickPlate", (-0.50, 0.0, 0.15), (0.83, 0.05, 0.26), P.METAL_STEEL)
    make_cyl("Door_PushBar", (-0.50, 0.07, 1.00), 0.020, 0.62, COL_BRASS, axis='X')
    make_door_hinges("Door_Hinge", edge_x=-0.92, edge_y=0.0,
                     edge_z_centers=[0.35, 1.05, 1.80], axis='X')
    # East sidelite — frame only, opening left empty
    make_box("SideLite_Stile_W", (0.12, 0.0, 1.10), (0.06, 0.05, 2.16), COL_WOOD_DARK)
    make_box("SideLite_Stile_E", (0.88, 0.0, 1.10), (0.06, 0.05, 2.16), COL_WOOD_DARK)
    make_box("SideLite_Sill", (0.50, 0.0, 0.30), (0.80, 0.05, 0.06), COL_WOOD_DARK)
    make_box("SideLite_Mull", (0.50, 0.0, 1.52), (0.80, 0.05, 0.05), COL_WOOD_DARK)
    # THE BELL over the door — rings at six-eleven for Wren, at
    # eleven fifty-eight for the gray-Monday music cue (vol7_ch2 /
    # music_catalog vol7_daily_grind). Brass, bracket-mounted.
    make_box("DoorBell_Mount", (0.55, 0.13, 2.32), (0.06, 0.10, 0.06), P.METAL_BLACK)
    make_cyl("DoorBell_Arm", (0.55, 0.24, 2.32), 0.012, 0.16, COL_BRASS, axis='Y')
    make_cyl("DoorBell_Body", (0.55, 0.32, 2.27), 0.050, 0.07, COL_BRASS)
    make_cyl("DoorBell_Flare", (0.55, 0.32, 2.22), 0.068, 0.025, COL_BRASS)
    make_cyl("DoorBell_Clapper", (0.55, 0.32, 2.18), 0.012, 0.05, P.METAL_BLACK)
    # OPEN/CLOSED sign hanging inside the east storefront window —
    # "The Daily Grind had now flipped its CLOSED to OPEN"
    # (vol7_ch15_bread). Lettering scene-side.
    make_cyl("OpenSign_Cord", (2.2, 0.05, 2.10), 0.004, 0.30, P.TWINE, axis='Z')
    make_box("OpenSign_Board", (2.2, 0.05, 1.85), (0.36, 0.02, 0.20), COL_CREAM)
    make_box("OpenSign_TextBand", (2.2, 0.038, 1.85), (0.28, 0.006, 0.09),
             (0.72, 0.30, 0.22, 1.0))
    # Hours plaque on the east door pier
    make_box("HoursPlaque", (1.15, 0.105, 1.50), (0.16, 0.010, 0.22), P.PAPER)
    # Entry mat + umbrella stand (rain register)
    make_box("EntryMat_Under", (0.0, 0.85, 0.004), (1.90, 1.10, 0.006), (0.14, 0.13, 0.13, 1.0))
    make_box("EntryMat", (0.0, 0.85, 0.011), (1.76, 0.96, 0.008), P.RUBBER_MAT)
    make_cyl("UmbrellaStand", (-1.30, 0.40, 0.28), 0.11, 0.56, P.METAL_BLACK,
             segments=12)
    for ui, (ux, uy, utint) in enumerate([(-1.26, 0.36, (0.24, 0.28, 0.38, 1.0)),
                                          (-1.34, 0.45, (0.42, 0.22, 0.20, 1.0))]):
        make_cyl(f"Umbrella_{ui}_Shaft", (ux, uy, 0.62), 0.012, 0.75, P.METAL_BLACK)
        make_cyl(f"Umbrella_{ui}_Canopy", (ux, uy, 0.78), 0.045, 0.34, utint)
        make_cyl(f"Umbrella_{ui}_Tip", (ux, uy, 1.02), 0.006, 0.10, P.METAL_STEEL)


# ═════════════════════════════════════════════════════════════════
# EXTERIOR — what the rain-light comes through: sidewalk apron, the
# canon railing with THE CROW (static_truths.md: "the crow that
# sits on the railing of the Daily Grind every morning when I
# open"), the porch two-top from the Issue #1 cover (coffee cup on
# a saucer, railing behind), planter, A-frame board, wet street.
# ═════════════════════════════════════════════════════════════════
def build_exterior():
    make_box("Ext_Sidewalk_S", (0.0, -1.25, -0.03), (9.4, 2.50, 0.06), COL_CONCRETE)
    make_box("Ext_Sidewalk_W", (-4.55, 3.0, -0.03), (2.10, 8.60, 0.06), COL_CONCRETE)
    for si in range(4):
        make_box(f"Ext_SidewalkSeam_{si}", (-3.1 + si * 2.0, -1.25, 0.001),
                 (0.02, 2.50, 0.002), (0.40, 0.39, 0.37, 1.0))
    make_box("Ext_Curb", (0.0, -2.55, -0.02), (9.4, 0.16, 0.12), (0.46, 0.45, 0.43, 1.0))
    make_box("Ext_Street", (0.0, -3.70, -0.05), (9.4, 2.20, 0.04), COL_ASPHALT)
    make_box("Ext_Puddle", (1.4, -3.30, -0.028), (1.30, 0.60, 0.002), COL_PUDDLE)
    # Railing along the front (break at the door path x −1..+1)
    for seg, (x0, x1) in enumerate([(-3.4, -1.2), (1.2, 3.4)]):
        n_posts = 4
        for pi in range(n_posts):
            px = x0 + (x1 - x0) * pi / (n_posts - 1)
            make_cyl(f"Rail_{seg}_Post_{pi}", (px, -1.05, 0.46), 0.025, 0.92, P.METAL_BLACK)
        make_box(f"Rail_{seg}_Top", ((x0 + x1) / 2.0, -1.05, 0.94),
                 (x1 - x0 + 0.08, 0.07, 0.05), COL_WOOD)
        make_box(f"Rail_{seg}_Mid", ((x0 + x1) / 2.0, -1.05, 0.52),
                 (x1 - x0, 0.04, 0.04), P.METAL_BLACK)
        for ki in range(9):
            kx = x0 + 0.18 + (x1 - x0 - 0.36) * ki / 8.0
            make_box(f"Rail_{seg}_Picket_{ki}", (kx, -1.05, 0.70),
                     (0.02, 0.02, 0.44), P.METAL_BLACK)
    # THE CROW — perched on the west railing run, facing the door.
    # Same crow Mrs. Gable sees at the lighthouse (VOL7 wiki).
    make_cyl("Crow_Body", (-2.7, -1.05, 1.015), 0.045, 0.13, COL_CROW, axis='X', segments=12)
    make_cyl("Crow_Head", (-2.615, -1.05, 1.05), 0.032, 0.06, COL_CROW, axis='X')
    make_box("Crow_Beak", (-2.565, -1.05, 1.045), (0.035, 0.014, 0.014),
             (0.24, 0.22, 0.20, 1.0))
    make_box("Crow_Tail", (-2.79, -1.05, 1.035), (0.09, 0.035, 0.012), COL_CROW)
    for li, ly in enumerate((-0.02, +0.02)):
        make_cyl(f"Crow_Leg_{li}", (-2.68, -1.05 + ly, 0.975), 0.004, 0.05,
                 (0.24, 0.22, 0.20, 1.0))
    # Porch two-top — the Static Truths Issue #1 cover image: a
    # coffee cup on a saucer on a small porch table, railing behind.
    _round_table("PorchTable", -2.2, -0.60, 0.30, COL_WOOD)
    _cup_saucer("PorchTable_Cup", -2.28, -0.62, 0.76, COL_CREAM)
    _chair("PorchChair", -1.62, -0.60, 'W', COL_WOOD_DARK)
    # Planter box east of the door
    make_box("Planter_Box", (2.3, -0.58, 0.20), (0.85, 0.34, 0.40), COL_WOOD)
    make_box("Planter_Soil", (2.3, -0.58, 0.385), (0.77, 0.26, 0.03), (0.20, 0.15, 0.11, 1.0))
    for bi, (bx, bh) in enumerate([(2.02, 0.30), (2.30, 0.42), (2.58, 0.26)]):
        make_cyl(f"Planter_Shrub_{bi}", (bx, -0.58, 0.40 + bh / 2.0), 0.10, bh, COL_PLANT)
    # A-frame chalk board on the sidewalk ("today's roast" scene-side)
    for si, sy in enumerate((-0.52, -0.68)):
        make_box(f"AFrame_Leg_{si}", (1.5, sy, 0.42), (0.5, 0.03, 0.84), COL_WOOD_DARK)
    make_box("AFrame_Board", (1.5, -0.505, 0.46), (0.42, 0.02, 0.58), COL_SLATE)
    for ci in range(3):
        make_box(f"AFrame_Chalk_{ci}", (1.5, -0.49, 0.62 - ci * 0.13),
                 (0.30 - ci * 0.05, 0.005, 0.035), COL_CHALK)


# ═════════════════════════════════════════════════════════════════
# ESPRESSO BAR — the counter Lena works behind. Plank-faced bar,
# butcher-block top, brass foot rail; pastry case (frame + open
# front, NO glass) with Hans's marshmallow slab; two-group espresso
# machine (cylinder group heads / portafilters at eye level);
# ceramic milk pitchers in regulars' order (vol7_ch2_morning);
# register + tip jar of tokens + THE STATIC TRUTHS CONTACT BOX
# ("the small box at the daily grind by the front register. mark
# it for l.v.") + a stack of Issue #1.
# ═════════════════════════════════════════════════════════════════
def build_bar():
    # Bar body: x −1.1..2.9, customer face y 3.75, back face y 4.35
    make_box("Bar_Body", (0.9, 4.05, 0.46), (4.0, 0.60, 0.92), COL_WOOD)
    make_box("Bar_Top", (0.9, 4.05, 0.95), (4.16, 0.72, 0.06), COL_BUTCHER)
    make_box("Bar_Kick", (0.9, 3.74, 0.10), (4.0, 0.02, 0.20), COL_WOOD_DARK)
    for pi in range(10):
        px = -1.08 + 0.22 + pi * 0.395
        tint = COL_WOOD_LT if pi % 2 == 0 else COL_WOOD
        make_box(f"Bar_Plank_{pi}", (px, 3.745, 0.50), (0.34, 0.012, 0.80), tint)
    for si in range(8):
        sx = -1.18 + 0.26 + si * 0.52
        make_cyl(f"Bar_Bullnose_{si}", (sx, 3.70, 0.945), 0.025, 0.52, COL_BUTCHER, axis='X')
    make_cyl("Bar_FootRail", (0.9, 3.62, 0.22), 0.020, 3.9, COL_BRASS, axis='X')
    for bi, bx in enumerate((-0.7, 0.9, 2.5)):
        make_box(f"Bar_FootRailBracket_{bi}", (bx, 3.68, 0.20), (0.03, 0.12, 0.03), COL_BRASS)
    # ── Pastry case (west end, frame + open customer front) ─────
    make_box("PastryCase_Tray", (-0.55, 4.08, 0.995), (0.92, 0.52, 0.03), P.METAL_STEEL)
    for ci, (cx, cy) in enumerate([(-0.98, 3.85), (-0.12, 3.85), (-0.98, 4.31), (-0.12, 4.31)]):
        make_box(f"PastryCase_Post_{ci}", (cx, cy, 1.26), (0.05, 0.05, 0.50), COL_WOOD)
    make_box("PastryCase_Roof", (-0.55, 4.08, 1.53), (0.98, 0.58, 0.04), COL_WOOD)
    make_box("PastryCase_Back", (-0.55, 4.32, 1.26), (0.88, 0.03, 0.46), COL_WOOD)
    make_box("PastryCase_Shelf", (-0.55, 4.10, 1.26), (0.86, 0.44, 0.02), COL_GLASSISH)
    # Hans's marshmallow slab — hand-cut, one per hot chocolate,
    # traded for tokens + Tuesday bread (vol7_ch2_morning)
    make_box("Hans_MarshmallowTray", (-0.80, 4.02, 1.025), (0.26, 0.20, 0.015), P.PAPER)
    make_box("Hans_MarshmallowSlab", (-0.82, 4.02, 1.06), (0.18, 0.13, 0.05), COL_CREAM)
    for mi in range(3):
        make_box(f"Hans_MarshmallowCube_{mi}", (-0.70 + mi * 0.045, 3.95, 1.048),
                 (0.03, 0.03, 0.03), COL_CREAM)
    for si in range(3):
        make_box(f"Pastry_Scone_{si}", (-0.48 + si * 0.11, 4.05, 1.055),
                 (0.085, 0.085, 0.045), (0.80, 0.62, 0.38, 1.0))
    for mi in range(4):
        mx = -0.86 + mi * 0.19
        make_cyl(f"Pastry_Muffin_{mi}_Base", (mx, 4.08, 1.30), 0.038, 0.055,
                 (0.62, 0.44, 0.24, 1.0))
        make_cyl(f"Pastry_Muffin_{mi}_Dome", (mx, 4.08, 1.345), 0.046, 0.025,
                 (0.52, 0.34, 0.18, 1.0))
    make_box("Pastry_PriceCard", (-0.30, 3.87, 1.045), (0.09, 0.008, 0.06), P.PAPER)
    # ── Ceramic milk pitchers, regulars' order (canon) ──────────
    for pi in range(4):
        px = 0.02 + pi * 0.15
        tint = COL_CREAM if pi % 2 == 0 else P.METAL_STEEL
        make_cyl(f"MilkPitcher_{pi}_Body", (px, 4.26, 1.035), 0.045, 0.11, tint)
        make_box(f"MilkPitcher_{pi}_Handle", (px + 0.055, 4.26, 1.04),
                 (0.018, 0.014, 0.06), tint)
    # ── Two-group espresso machine (Linea-class proportions) ────
    make_box("Espresso_Body", (1.05, 4.10, 1.19), (0.85, 0.44, 0.42), P.METAL_STEEL)
    make_box("Espresso_PanelS", (1.05, 3.875, 1.19), (0.79, 0.012, 0.36), COL_SAGE)
    make_box("Espresso_PanelN", (1.05, 4.325, 1.28), (0.79, 0.012, 0.20), COL_SAGE)
    make_box("Espresso_TopTray", (1.05, 4.10, 1.415), (0.87, 0.46, 0.03), P.METAL_STEEL)
    for gi, gx in enumerate((0.86, 1.24)):
        make_cyl(f"Espresso_Group_{gi}", (gx, 4.27, 1.06), 0.045, 0.10, P.METAL_STEEL)
        make_cyl(f"Espresso_Portafilter_{gi}", (gx, 4.27, 1.005), 0.050, 0.03, P.METAL_BLACK)
        make_cyl(f"Espresso_PFHandle_{gi}", (gx, 4.40, 1.005), 0.015, 0.16,
                 P.METAL_BLACK, axis='Y')
    make_box("Espresso_DripTray", (1.05, 4.30, 0.99), (0.70, 0.14, 0.02), P.METAL_STEEL)
    for di in range(6):
        make_box(f"Espresso_DripSlat_{di}", (0.79 + di * 0.105, 4.30, 1.001),
                 (0.02, 0.13, 0.003), P.METAL_BLACK)
    for wi, wx in enumerate((0.585, 1.515)):
        make_cyl(f"Espresso_SteamWand_{wi}", (wx, 4.18, 1.07), 0.008, 0.20, P.METAL_STEEL)
        make_cyl(f"Espresso_SteamKnob_{wi}", (wx, 4.18, 1.20), 0.028, 0.035, COL_WOOD_DARK,
                 axis='X')
    make_cyl("Espresso_Gauge", (0.82, 3.868, 1.28), 0.040, 0.014, COL_CREAM, axis='Y')
    make_cyl("Espresso_GaugeRim", (0.82, 3.872, 1.28), 0.046, 0.006, P.METAL_BLACK, axis='Y')
    make_box("Espresso_BrandPlate", (1.18, 3.868, 1.30), (0.26, 0.006, 0.06), COL_BRASS)
    for r in range(2):
        for c in range(5):
            make_cyl(f"Espresso_WarmCup_{r}_{c}", (0.73 + c * 0.16, 3.98 + r * 0.22, 1.455),
                     0.028, 0.05, MUG_TINTS[(r * 5 + c) % len(MUG_TINTS)])
    # ── Register zone ────────────────────────────────────────────
    make_register("RegisterMachine", (2.1, 4.05, BAR_TOP),
                  palette={"body": (0.30, 0.29, 0.28, 1.0)})
    make_credit_card_terminal("CardTerminal", (1.72, 3.86, BAR_TOP))
    # Tip jar — Smolvud runs on tokens (vol7_ch2_morning: Jameson's
    # forty tokens; ch8: Edgar pays in tokens)
    make_cyl("TipJar_Body", (2.45, 3.86, 1.05), 0.055, 0.14, COL_GLASSISH)
    for ti in range(3):
        make_cyl(f"TipJar_Token_{ti}", (2.44 + (ti % 2) * 0.02, 3.86, 1.00 + ti * 0.012),
                 0.032, 0.008, COL_WOOD_LT)
    make_box("TipJar_Label", (2.45, 3.80, 1.06), (0.07, 0.006, 0.05), P.PAPER)
    # THE CONTACT BOX — "the small box at the daily grind by the
    # front register. mark it for l.v." (static_truths.md back cover)
    make_box("StaticTruths_ContactBox", (2.66, 3.95, 1.035), (0.17, 0.13, 0.11), COL_WOOD)
    make_box("StaticTruths_ContactSlot", (2.66, 3.95, 1.092), (0.10, 0.02, 0.008),
             P.METAL_BLACK)
    make_box("StaticTruths_ContactLabel", (2.66, 3.88, 1.045), (0.10, 0.006, 0.05), P.PAPER)
    # A short stack of Issue #1 beside it (photocopied, half-letter)
    for zi in range(3):
        make_box(f"StaticTruths_Stack_{zi}", (2.66 + (zi % 2) * 0.008, 4.20, 0.985 + zi * 0.008),
                 (0.15, 0.21, 0.006), P.PAPER if zi % 2 == 0 else P.NEWSPRINT)
    make_box("StaticTruths_Stack_Masthead", (2.66, 4.14, 1.013), (0.11, 0.06, 0.004),
             P.METAL_BLACK)


# ═════════════════════════════════════════════════════════════════
# BACKBAR + NORTH WALL — cabinet with the milk cooler (Lena fills
# the pitchers from it), sink, kettle + pour-over cones (Petra's
# cone, Soren's dark French), grinders with bean hoppers, knock
# box, takeaway cups, bean jars; the heat-pump compressor the back
# door wakes at six oh-four; menu boards; mismatched mug shelves;
# the clock frozen at 11:58; the back-room door (Soren in the back,
# Lena's studio beyond).
# ═════════════════════════════════════════════════════════════════
def build_backbar():
    # Cabinet run x −0.5..3.3
    make_box("Backbar_Body", (1.4, 5.625, 0.45), (3.8, 0.55, 0.90), COL_WOOD)
    make_box("Backbar_Top", (1.4, 5.625, 0.92), (3.9, 0.60, 0.04), COL_BUTCHER)
    make_box("Backbar_Kick", (1.4, 5.34, 0.08), (3.8, 0.02, 0.16), COL_WOOD_DARK)
    # Under-counter milk cooler — two steel doors (vol7_ch2_morning)
    for di, dx in enumerate((0.55, 1.25)):
        make_box(f"Cooler_Door_{di}", (dx, 5.335, 0.47), (0.62, 0.015, 0.74), P.METAL_STEEL)
        make_box(f"Cooler_Handle_{di}", (dx - 0.22, 5.32, 0.62), (0.03, 0.015, 0.26),
                 P.METAL_BLACK)
        make_box(f"Cooler_Vent_{di}", (dx, 5.328, 0.16), (0.50, 0.008, 0.08), P.METAL_BLACK)
    # Sink (west end) — inset basin + gooseneck faucet
    make_box("Sink_Basin", (-0.15, 5.60, 0.885), (0.42, 0.36, 0.10),
             P.METAL_STEEL, open_faces={'+Z'})
    make_box("Sink_BasinFloor", (-0.15, 5.60, 0.845), (0.40, 0.34, 0.01),
             (0.42, 0.44, 0.46, 1.0))
    make_cyl("Sink_FaucetRiser", (-0.15, 5.78, 1.06), 0.014, 0.24, P.METAL_STEEL)
    make_cyl("Sink_FaucetSpout", (-0.15, 5.68, 1.17), 0.012, 0.20, P.METAL_STEEL, axis='Y')
    for hi, hx in enumerate((-0.25, -0.05)):
        make_box(f"Sink_Handle_{hi}", (hx, 5.78, 0.965), (0.05, 0.02, 0.02), P.METAL_STEEL)
    # Kettle + pour-over stand (the cone canon, vol7_ch8_monday)
    make_cyl("Kettle_Body", (0.35, 5.62, 1.02), 0.080, 0.15, P.METAL_STEEL, segments=12)
    make_cyl("Kettle_Lid", (0.35, 5.62, 1.105), 0.055, 0.02, P.METAL_STEEL)
    make_cyl("Kettle_Knob", (0.35, 5.62, 1.125), 0.014, 0.02, COL_WOOD_DARK)
    make_box("Kettle_Spout_A", (0.44, 5.62, 1.00), (0.07, 0.018, 0.018), P.METAL_STEEL)
    make_box("Kettle_Spout_B", (0.485, 5.62, 1.035), (0.04, 0.015, 0.015), P.METAL_STEEL)
    make_box("Kettle_Handle", (0.26, 5.62, 1.11), (0.03, 0.02, 0.09), COL_WOOD_DARK)
    make_box("PourOver_Base", (0.90, 5.60, 0.955), (0.44, 0.24, 0.03), COL_WOOD)
    for ui, ux in enumerate((0.70, 1.10)):
        make_box(f"PourOver_Upright_{ui}", (ux, 5.60, 1.10), (0.03, 0.03, 0.26), COL_WOOD)
    make_box("PourOver_TopRail", (0.90, 5.60, 1.245), (0.44, 0.10, 0.03), COL_WOOD)
    for ci, cx in enumerate((0.80, 1.00)):
        make_cyl(f"PourOver_Cone_{ci}_Upper", (cx, 5.60, 1.30), 0.062, 0.06, COL_CREAM)
        make_cyl(f"PourOver_Cone_{ci}_Lower", (cx, 5.60, 1.265), 0.038, 0.03, COL_CREAM)
        make_cyl(f"PourOver_Carafe_{ci}", (cx, 5.60, 1.03), 0.052, 0.12, COL_AMBER)
    # Cocoa tins — Wren's hot chocolate (vol7_ch2_morning)
    for ti in range(2):
        make_cyl(f"CocoaTin_{ti}", (1.28, 5.55 + ti * 0.14, 1.005), 0.045, 0.13, COL_COCOA)
        make_box(f"CocoaTin_{ti}_Label", (1.235, 5.55 + ti * 0.14, 1.01),
                 (0.006, 0.06, 0.07), P.PAPER_AGED)
    # Grinders — body + bean hopper cylinders (eye-level round rule)
    for gi, gx in enumerate((1.60, 2.02)):
        make_box(f"Grinder_{gi}_Body", (gx, 5.62, 1.13), (0.20, 0.26, 0.38), P.METAL_BLACK)
        make_cyl(f"Grinder_{gi}_Hopper", (gx, 5.62, 1.43), 0.085, 0.22, COL_GLASSISH, segments=12)
        make_cyl(f"Grinder_{gi}_Beans", (gx, 5.62, 1.38), 0.070, 0.10, COL_BEAN, segments=12)
        make_cyl(f"Grinder_{gi}_Lid", (gx, 5.62, 1.55), 0.090, 0.02, P.METAL_BLACK)
        make_box(f"Grinder_{gi}_Spout", (gx, 5.48, 1.05), (0.05, 0.06, 0.07), P.METAL_BLACK)
        make_box(f"Grinder_{gi}_Tray", (gx, 5.46, 0.945), (0.14, 0.10, 0.01), P.METAL_STEEL)
    # Knock box
    make_box("KnockBox", (2.35, 5.62, 1.00), (0.18, 0.18, 0.12), P.METAL_BLACK,
             open_faces={'+Z'})
    make_cyl("KnockBox_Bar", (2.35, 5.62, 1.055), 0.014, 0.16, P.METAL_STEEL, axis='X')
    # Takeaway cups + lids + sleeves (ch14/ch16 takeaway canon)
    make_paper_cup_stack("TakeawayCups_A", (2.62, 5.56, 0.94), count=14)
    make_paper_cup_stack("TakeawayCups_B", (2.62, 5.72, 0.94),
                         count=10, palette={"col": P.PAPER_AGED})
    for li in range(5):
        make_cyl(f"TakeawayLid_{li}", (2.80, 5.64, 0.95 + li * 0.012), 0.050, 0.010,
                 (0.24, 0.23, 0.22, 1.0))
    make_box("TakeawaySleeves", (2.95, 5.62, 0.975), (0.10, 0.14, 0.07), COL_BURLAP)
    # Bean jars — Soren's roasts, labeled (dark French front)
    for ji, (jx, jy) in enumerate([(3.10, 5.52), (3.10, 5.72), (3.26, 5.62)]):
        make_cyl(f"BeanJar_{ji}_Glass", (jx, jy, 1.03), 0.055, 0.18, COL_GLASSISH, segments=12)
        make_cyl(f"BeanJar_{ji}_Fill", (jx, jy, 0.99), 0.046, 0.09, COL_BEAN, segments=12)
        make_cyl(f"BeanJar_{ji}_Lid", (jx, jy, 1.13), 0.058, 0.02, COL_WOOD)
        make_box(f"BeanJar_{ji}_Label", (jx, jy - 0.058, 1.03), (0.05, 0.006, 0.05), P.PAPER)
    # Burlap bean sacks by the back door — Soren roasts (ch8_monday)
    make_box("BeanSack_0", (-1.45, 5.62, 0.26), (0.42, 0.40, 0.52), COL_BURLAP)
    make_box("BeanSack_0_Roll", (-1.45, 5.62, 0.545), (0.46, 0.44, 0.05), COL_BURLAP)
    make_box("BeanSack_0_Stencil", (-1.45, 5.41, 0.30), (0.24, 0.006, 0.14), COL_WOOD_DARK)
    make_box("BeanSack_1", (-1.05, 5.68, 0.20), (0.36, 0.34, 0.40), (0.56, 0.44, 0.30, 1.0))
    # Heat-pump compressor + hot-water lines — the thing the back
    # door wakes at six oh-four (vol7_ch2_morning). Twenty minutes
    # to temperature; the window for morning prep.
    make_box("HeatPump_Body", (-0.62, 5.72, 0.29), (0.46, 0.32, 0.54), P.METAL_STEEL)
    for vi in range(3):
        make_box(f"HeatPump_Vent_{vi}", (-0.62, 5.555, 0.16 + vi * 0.15),
                 (0.36, 0.008, 0.05), P.METAL_BLACK)
    make_cyl("HeatPump_Riser", (-0.42, 5.84, 0.62), 0.016, 0.55, (0.55, 0.36, 0.24, 1.0))
    make_cyl("HeatPump_Line", (0.3, 5.84, 0.88), 0.014, 1.5, (0.55, 0.36, 0.24, 1.0), axis='X')

def build_north_wall():
    wall_face = ROOM_D - 0.10   # 5.90
    # Menu boards — three framed chalk panels (text scene-side)
    for bi in range(3):
        bx = 0.15 + bi * 1.0
        make_box(f"MenuBoard_{bi}_Frame", (bx, wall_face - 0.02, 2.05), (0.90, 0.03, 0.74),
                 COL_WOOD)
        make_box(f"MenuBoard_{bi}", (bx, wall_face - 0.045, 2.05), (0.82, 0.02, 0.66),
                 COL_SLATE)
        make_box(f"MenuBoard_{bi}_Header", (bx, wall_face - 0.06, 2.28),
                 (0.52, 0.005, 0.09), COL_CHALK)
        for ri in range(4):
            make_box(f"MenuBoard_{bi}_Row_{ri}", (bx - 0.06, wall_face - 0.06, 2.14 - ri * 0.10),
                     (0.58, 0.005, 0.035), COL_CHALK)
            make_box(f"MenuBoard_{bi}_Price_{ri}", (bx + 0.32, wall_face - 0.06, 2.14 - ri * 0.10),
                     (0.10, 0.005, 0.035), COL_CHALK)
    # Clock frozen at 11:58 — the bell at eleven fifty-eight
    # (vol7_ch8_monday / music_catalog vol7_daily_grind)
    make_wall_clock("Clock", (-1.35, wall_face - 0.03, 2.30), frozen_hour=11, frozen_min=58)
    # Mismatched mug shelves (east of the menu boards)
    for si, sz in enumerate((1.50, 1.86)):
        make_box(f"MugShelf_{si}", (3.0, wall_face - 0.09, sz), (0.80, 0.18, 0.03), COL_WOOD)
        for ki, sgn in enumerate((-1, +1)):
            make_box(f"MugShelf_{si}_Bracket_{ki}", (3.0 + sgn * 0.34, wall_face - 0.045, sz - 0.06),
                     (0.03, 0.09, 0.10), P.METAL_BLACK)
        for mi in range(5):
            _mug(f"ShelfMug_{si}_{mi}", 2.70 + mi * 0.15, wall_face - 0.09, sz + 0.015,
                 MUG_TINTS[(si * 3 + mi) % len(MUG_TINTS)])
    # Back-room door — the seam to Soren's back room + Lena's
    # studio (vol7_ch3_studio); the back door beyond it is the one
    # Lena unlocks first. Closed solid-wood leaf, brass knob.
    for sgn in (-1, +1):
        make_box(f"BackDoor_Post_{sgn:+d}", (-2.4 + sgn * 0.54, ROOM_D - 0.05, 1.10),
                 (0.08, 0.14, 2.20), COL_WOOD)
    make_box("BackDoor_Header", (-2.4, ROOM_D - 0.06, 2.26), (1.20, 0.10, 0.12), COL_WOOD)
    make_box("BackDoor_Leaf", (-2.4, ROOM_D + 0.02, 1.08), (0.96, 0.06, 2.12), COL_WOOD_DARK)
    for pi in range(2):
        make_box(f"BackDoor_Panel_{pi}", (-2.4, ROOM_D - 0.012, 0.70 + pi * 0.85),
                 (0.68, 0.008, 0.62), COL_WOOD)
    make_cyl("BackDoor_Knob", (-2.05, ROOM_D - 0.05, 1.02), 0.028, 0.05, COL_BRASS, axis='Y')
    make_door_hinges("BackDoor_Hinge", edge_x=-2.86, edge_y=ROOM_D - 0.02,
                     edge_z_centers=[0.35, 1.05, 1.80], axis='X')
    make_box("BackDoor_Sign", (-2.4, ROOM_D - 0.115, 1.62), (0.26, 0.012, 0.10), P.PAPER_AGED)


# ═════════════════════════════════════════════════════════════════
# SEATING — the CORNER TABLE with its four chairs (Finn "sat in the
# fourth chair", vol7_ch2_afternoon; Wren's Friday hot chocolate;
# Marina + Roy sightings), Mrs. Gable's morning two-top by the east
# window, Per's regular table, the window bar with stools, and the
# NW armchair nook. Mismatched on purpose.
# ═════════════════════════════════════════════════════════════════
def build_seating():
    # THE CORNER TABLE — SW corner where the two windows meet
    _round_table("CornerTable", -2.5, 1.2, 0.45, COL_WOOD_LT)
    _chair("CornerChair_0", -2.5, 1.90, 'S', CHAIR_TINTS[0])
    _chair("CornerChair_1", -1.80, 1.2, 'W', CHAIR_TINTS[1])
    _chair("CornerChair_2", -2.5, 0.55, 'N', CHAIR_TINTS[2])
    _chair("CornerChair_3", -3.08, 1.2, 'E', CHAIR_TINTS[3])
    # Wren's hot chocolate, left mid-table (the marshmallow in it)
    _cup_saucer("CornerTable_Cocoa", -2.38, 1.30, 0.76, MUG_TINTS[3])
    # Mrs. Gable's morning seat — two-top by the east window
    # (_VOL6_VOL7_LOCALES_MANIFEST); her coffee is on the table
    _square_table("MrsGableTable", 2.45, 1.70, 0.62, COL_WOOD)
    _chair("MrsGableChair_0", 1.88, 1.70, 'E', CHAIR_TINTS[2])
    _chair("MrsGableChair_1", 3.02, 1.70, 'W', CHAIR_TINTS[0])
    _cup_saucer("MrsGable_Coffee", 2.32, 1.78, 0.76, COL_CREAM)
    make_box("MrsGable_Newspaper", (2.58, 1.58, 0.765), (0.24, 0.17, 0.01), P.NEWSPRINT)
    # Per's regular table (manifest) — two-top mid-east
    _square_table("PerTable", 2.60, 3.35, 0.60, COL_WOOD_LT)
    _chair("PerChair_0", 2.00, 3.35, 'E', CHAIR_TINTS[1])
    _chair("PerChair_1", 2.60, 2.78, 'N', CHAIR_TINTS[3])
    # Window bar along the east storefront window + two stools
    make_box("WindowBar_Top", (2.25, 0.34, 0.98), (1.60, 0.30, 0.05), COL_BUTCHER)
    for wi, wx in enumerate((1.60, 2.25, 2.90)):
        make_box(f"WindowBar_Bracket_{wi}", (wx, 0.22, 0.86), (0.05, 0.14, 0.20), P.METAL_BLACK)
    _stool("WindowStool_0", 1.90, 0.62)
    _stool("WindowStool_1", 2.65, 0.62)
    # NW armchair nook — rust wool armchair, side table, floor lamp
    make_box("Armchair_Base", (-3.0, 4.85, 0.22), (0.62, 0.62, 0.30), COL_UPHOLSTER)
    make_box("Armchair_Cushion", (-2.95, 4.85, 0.42), (0.50, 0.52, 0.12), COL_UPHOLSTER)
    make_box("Armchair_Back", (-3.24, 4.85, 0.62), (0.16, 0.62, 0.60), COL_UPHOLSTER)
    for ai, sgn in enumerate((-1, +1)):
        make_box(f"Armchair_Arm_{ai}", (-3.0, 4.85 + sgn * 0.30, 0.50),
                 (0.58, 0.12, 0.26), COL_UPHOLSTER)
    for fi, (fx, fy) in enumerate([(-3.24, 4.62), (-2.76, 4.62), (-3.24, 5.08), (-2.76, 5.08)]):
        make_cyl(f"Armchair_Foot_{fi}", (fx, fy, 0.035), 0.022, 0.07, COL_WOOD_DARK)
    _round_table("SideTable", -2.5, 4.38, 0.22, COL_WOOD_DARK)
    _mug("SideTable_Mug", -2.52, 4.40, 0.76, MUG_TINTS[0])
    make_cyl("FloorLamp_Base", (-3.05, 5.45, 0.02), 0.14, 0.04, P.METAL_BLACK, segments=12)
    make_cyl("FloorLamp_Pole", (-3.05, 5.45, 0.78), 0.014, 1.48, COL_BRASS)
    make_cyl("FloorLamp_Shade", (-3.05, 5.45, 1.60), 0.14, 0.18, COL_CREAM, segments=12)
    make_cyl("FloorLamp_Glow", (-3.05, 5.45, 1.50), 0.06, 0.03, (0.98, 0.88, 0.62, 1.0))


# ═════════════════════════════════════════════════════════════════
# CONDIMENT STATION — sugar caddy, napkins, water carafe + cups,
# cinnamon shakers, cup-return trash. Mid-east floor, off the
# door-to-counter aisle.
# ═════════════════════════════════════════════════════════════════
def build_condiment_station():
    make_box("Condiment_Cabinet", (1.70, 2.60, 0.425), (0.55, 0.42, 0.85), COL_WOOD)
    make_box("Condiment_Top", (1.70, 2.60, 0.87), (0.60, 0.47, 0.04), COL_BUTCHER)
    make_box("Condiment_ShelfNook", (1.70, 2.39, 0.55), (0.45, 0.02, 0.30), COL_WOOD_DARK)
    make_sugar_creamer_caddy("Condiment_Caddy", (1.62, 2.66, 0.93))
    make_box("Condiment_Napkins", (1.88, 2.50, 0.945), (0.14, 0.14, 0.11), P.PAPER)
    make_box("Condiment_NapkinWeight", (1.88, 2.50, 1.005), (0.05, 0.05, 0.012), COL_WOOD_DARK)
    make_cyl("Condiment_Carafe", (1.52, 2.46, 0.99), 0.050, 0.20, P.METAL_STEEL, segments=12)
    make_cyl("Condiment_CarafeSpigot", (1.52, 2.40, 0.93), 0.010, 0.05, P.METAL_BLACK, axis='Y')
    for ci in range(4):
        make_cyl(f"Condiment_WaterCup_{ci}", (1.86, 2.70, 0.905 + ci * 0.012), 0.032, 0.012,
                 COL_GLASSISH)
    for si in range(2):
        make_cyl(f"Condiment_Shaker_{si}", (1.60 + si * 0.09, 2.44, 0.945), 0.020, 0.09,
                 COL_GLASSISH)
    make_trash_can("CupReturn", (3.08, 2.55, 0.0), branded=False)
    make_box("CupReturn_Sign", (3.08, 2.34, 0.72), (0.16, 0.008, 0.08), P.PAPER)


# ═════════════════════════════════════════════════════════════════
# EAST WALL — rain-gear hooks with a wax-canvas coat + drip mat
# (everyone in this town owns one), the community corkboard with
# STATIC TRUTHS pinned center (Lena's zine), Soren's retail bean
# bags, fire extinguisher by the bar pass.
# ═════════════════════════════════════════════════════════════════
def build_east_wall():
    wall_face = ROOM_W / 2.0 - 0.10   # 3.40
    # Rain-gear hooks (south end, by the door)
    make_box("RainHooks_Rail", (wall_face + 0.02, 1.10, 1.66), (0.03, 1.20, 0.08), COL_WOOD)
    for hi, hy in enumerate((0.62, 0.94, 1.26, 1.58)):
        make_cyl(f"RainHooks_Peg_{hi}", (wall_face - 0.03, hy, 1.64), 0.014, 0.10,
                 COL_BRASS, axis='X')
    # A wax canvas coat on the second peg + drip mat below
    make_box("RainCoat_Body", (wall_face - 0.07, 0.94, 1.24), (0.06, 0.34, 0.76), COL_RAINCOAT)
    make_box("RainCoat_Hood", (wall_face - 0.07, 0.94, 1.66), (0.07, 0.22, 0.12), COL_RAINCOAT)
    make_box("RainCoat_Flap", (wall_face - 0.105, 0.94, 1.20), (0.012, 0.10, 0.60),
             (0.32, 0.30, 0.22, 1.0))
    make_box("RainHooks_DripMat", (wall_face - 0.28, 1.05, 0.006), (0.50, 1.10, 0.01),
             P.RUBBER_MAT)
    # Community corkboard — flyers + STATIC TRUTHS front and center
    # (Lena's zine, static_truths.md; masthead Label3D scene-side)
    make_box("CorkBoard", (wall_face + 0.02, 2.80, 1.60), (0.03, 1.40, 0.95), COL_CORK)
    make_box("CorkBoard_FrameT", (wall_face + 0.005, 2.80, 2.09), (0.04, 1.46, 0.05), COL_WOOD)
    make_box("CorkBoard_FrameB", (wall_face + 0.005, 2.80, 1.11), (0.04, 1.46, 0.05), COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"CorkBoard_FrameSide_{sgn:+d}", (wall_face + 0.005, 2.80 + sgn * 0.72, 1.60),
                 (0.04, 0.05, 1.02), COL_WOOD)
    make_paper_notices_wall("CorkNotice", wall_x=wall_face, wall_face_sign=-1,
                            run_center_y=2.80, base_z=0.0, notices=[
        # (dy, dz, w, h, tint) — tide chart / co-op hours / band
        # flyer / lost cat / yoga at the grange / bus schedule
        (-0.52, 1.86, 0.24, 0.30, P.PAPER),
        (-0.20, 1.90, 0.20, 0.26, (0.42, 0.52, 0.62, 1.0)),
        (+0.22, 1.88, 0.26, 0.32, P.PAPER_AGED),
        (+0.54, 1.84, 0.18, 0.22, (0.86, 0.66, 0.34, 1.0)),
        (-0.50, 1.36, 0.22, 0.26, P.NEWSPRINT),
        (+0.50, 1.38, 0.24, 0.28, P.PAPER),
    ])
    # STATIC TRUTHS Issue #1 — pinned dead center. Cover: masthead
    # + the porch-cup drawing; back cover octopus is on the copies
    # by the register.
    make_box("Zine_StaticTruths", (wall_face - 0.025, 2.80, 1.60), (0.02, 0.24, 0.34), P.PAPER)
    make_box("Zine_StaticTruths_Masthead", (wall_face - 0.038, 2.80, 1.72),
             (0.006, 0.19, 0.06), P.METAL_BLACK)
    make_box("Zine_StaticTruths_CoverArt", (wall_face - 0.038, 2.80, 1.55),
             (0.006, 0.15, 0.14), (0.55, 0.52, 0.48, 1.0))
    for pi, py in enumerate((2.70, 2.90)):
        make_cyl(f"Zine_StaticTruths_Pin_{pi}", (wall_face - 0.045, py, 1.755), 0.012, 0.015,
                 (0.72, 0.30, 0.22, 1.0), axis='X')
    # Soren's retail bean bags — the dark French Petra drinks
    make_box("RetailShelf", (wall_face - 0.09, 4.75, 1.32), (0.22, 1.00, 0.03), COL_WOOD)
    for ki, sgn in enumerate((-1, +1)):
        make_box(f"RetailShelf_Bracket_{ki}", (wall_face - 0.04, 4.75 + sgn * 0.42, 1.24),
                 (0.10, 0.03, 0.13), P.METAL_BLACK)
    for bi in range(5):
        by = 4.37 + bi * 0.19
        tint = (0.34, 0.22, 0.14, 1.0) if bi % 2 == 0 else (0.48, 0.32, 0.18, 1.0)
        make_box(f"RetailBag_{bi}", (wall_face - 0.12, by, 1.435), (0.11, 0.07, 0.20), tint)
        make_box(f"RetailBag_{bi}_Fold", (wall_face - 0.12, by, 1.545), (0.12, 0.08, 0.02), tint)
        make_box(f"RetailBag_{bi}_Label", (wall_face - 0.18, by, 1.43),
                 (0.005, 0.05, 0.07), P.PAPER)
    make_box("RetailShelf_PriceCard", (wall_face - 0.05, 4.75, 1.36), (0.01, 0.12, 0.06),
             P.PAPER)
    # Fire extinguisher near the bar pass
    make_fire_extinguisher("FireExt", (wall_face + 0.04, 5.55, 0.30))


# ═════════════════════════════════════════════════════════════════
# WEST WALL — Lena's paintings (she is the only person on this
# coast making work like this — vol7_ch2_morning via her Board
# Lords decks; Tide Pool Geometries + an octopus study), the low
# bookcase, the hanging plant over the corner window.
# ═════════════════════════════════════════════════════════════════
def build_west_wall():
    wall_face = -ROOM_W / 2.0 + 0.10   # −3.40
    # Tide Pool Geometries — long dark kelp-lines on deep gray
    make_box("LenaPainting_TidePool_Frame", (wall_face + 0.015, 3.60, 1.75),
             (0.03, 0.74, 0.54), COL_WOOD_DARK)
    make_box("LenaPainting_TidePool_Canvas", (wall_face + 0.035, 3.60, 1.75),
             (0.02, 0.66, 0.46), (0.30, 0.32, 0.33, 1.0))
    for ki, (ky, kh, kz) in enumerate([(3.38, 0.34, 1.70), (3.52, 0.42, 1.78),
                                       (3.68, 0.30, 1.66), (3.82, 0.40, 1.80)]):
        make_box(f"LenaPainting_TidePool_Kelp_{ki}", (wall_face + 0.047, ky, kz),
                 (0.004, 0.020, kh), (0.10, 0.11, 0.12, 1.0))
    make_box("LenaPainting_TidePool_Sig", (wall_face + 0.047, 3.86, 1.56),
             (0.004, 0.07, 0.02), (0.10, 0.11, 0.12, 1.0))
    # Octopus study — indigo ground, warm octopus, star flecks
    make_box("LenaPainting_Octopus_Frame", (wall_face + 0.015, 4.55, 1.72),
             (0.03, 0.50, 0.42), COL_WOOD_DARK)
    make_box("LenaPainting_Octopus_Canvas", (wall_face + 0.035, 4.55, 1.72),
             (0.02, 0.42, 0.34), (0.16, 0.13, 0.26, 1.0))
    make_cyl("LenaPainting_Octopus_Head", (wall_face + 0.048, 4.55, 1.80), 0.062, 0.008,
             (0.82, 0.52, 0.30, 1.0), axis='X', segments=12)
    for ai in range(4):
        make_box(f"LenaPainting_Octopus_Arm_{ai}", (wall_face + 0.046, 4.43 + ai * 0.08, 1.68),
                 (0.004, 0.018, 0.10 + (ai % 2) * 0.04), (0.82, 0.52, 0.30, 1.0))
    for si in range(4):
        make_box(f"LenaPainting_Octopus_Star_{si}",
                 (wall_face + 0.046, 4.40 + ((si * 3) % 4) * 0.09, 1.84 - (si % 2) * 0.05),
                 (0.004, 0.014, 0.014), (0.90, 0.86, 0.94, 1.0))
    # Low bookcase under the paintings — leave-one-take-one
    make_box("Bookcase_Shell", (-3.33, 3.75, 0.50), (0.30, 1.00, 1.00), COL_WOOD,
             open_faces={'+X'})
    make_box("Bookcase_Shelf", (-3.33, 3.75, 0.48), (0.26, 0.94, 0.025), COL_WOOD_DARK)
    for ri, rz in enumerate((0.16, 0.62)):
        for ci in range(7):
            cyy = 3.36 + ci * 0.13
            bh = (0.24, 0.28, 0.22, 0.26)[(ri * 3 + ci) % 4]
            tint = P.SNACK_TINTS[(ri * 5 + ci * 2) % len(P.SNACK_TINTS)]
            make_box(f"Bookcase_Book_{ri}_{ci}", (-3.30, cyy, rz + bh / 2.0),
                     (0.20, 0.035, bh), tint)
    make_box("Bookcase_GameBox_0", (-3.33, 3.60, 1.035), (0.24, 0.32, 0.06),
             (0.34, 0.48, 0.46, 1.0))
    make_box("Bookcase_GameBox_1", (-3.33, 3.62, 1.095), (0.22, 0.28, 0.05),
             (0.72, 0.30, 0.22, 1.0))
    # Hanging plant over the corner window's north edge
    make_cyl("HangPlant_Hook", (-3.0, 2.55, CEIL - 0.02), 0.03, 0.04, P.METAL_BLACK)
    for ci in range(3):
        make_box(f"HangPlant_Cord_{ci}", (-3.0 + (ci - 1) * 0.05, 2.55 + (ci % 2) * 0.05 - 0.025,
                 CEIL - 0.28), (0.006, 0.006, 0.52), P.TWINE)
    make_cyl("HangPlant_Pot", (-3.0, 2.55, CEIL - 0.60), 0.10, 0.12, COL_POT, segments=12)
    for li in range(6):
        ang_x = (-1, 0, 1, -1, 0, 1)[li] * 0.09
        ang_y = (-1, -1, -1, 1, 1, 1)[li] * 0.07
        make_cyl(f"HangPlant_Leaf_{li}", (-3.0 + ang_x, 2.55 + ang_y, CEIL - 0.50),
                 0.035, 0.07, COL_PLANT)
    for vi in range(3):
        make_box(f"HangPlant_Vine_{vi}", (-3.0 + (vi - 1) * 0.10, 2.55 + (vi % 2) * 0.08 - 0.04,
                 CEIL - 0.76), (0.02, 0.02, 0.26), COL_PLANT)
    # Floor plant in the NW corner behind the armchair
    make_floor_plant("FloorPlant_NW", (-3.05, 5.72, 0.0))


# ═════════════════════════════════════════════════════════════════
# CEILING — warm pendants (2025 PNW, not fluorescent-tube 90s):
# three over the bar, one over each table. Smoke detector, HVAC
# vent, one ceiling speaker.
# ═════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    pendants = [
        ("Pendant_Bar_0", 0.0, 4.0), ("Pendant_Bar_1", 1.2, 4.0), ("Pendant_Bar_2", 2.4, 4.0),
        ("Pendant_Corner", -2.5, 1.2), ("Pendant_MrsGable", 2.45, 1.7),
        ("Pendant_Per", 2.6, 3.35),
    ]
    for nm, px, py in pendants:
        _pendant(nm, px, py)
    make_smoke_detector("Smoke", (0.2, 3.0, CEIL))
    make_hvac_vent("HVAC", (-1.8, 4.6, CEIL), width=0.80, depth=0.40)
    make_ceiling_speaker("Speaker", (0.8, 1.6, CEIL))


def main():
    clear_scene()
    build_shell()
    build_storefront()
    build_exterior()
    build_bar()
    build_backbar()
    build_north_wall()
    build_seating()
    build_condiment_station()
    build_east_wall()
    build_west_wall()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/daily_grind_interior.glb"))
    print(f"\n[build_daily_grind_interior] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
