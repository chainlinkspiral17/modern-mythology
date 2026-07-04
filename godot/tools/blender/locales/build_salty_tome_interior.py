"""THE SALTY TOME — Petra's used bookshop — vol7 hero locale (Smolvud, OR).

Ground floor of Petra's building on Hemlock (Lena's apartment is
directly upstairs — build_lena_apartment.py models this same facade
from above, brick + cornice + the hanging spruce-blue sign; keep
those treatments in sync). Petra bought the building in '11 and has
lived above the bookstore since '15 (vol7_ch14_petra). PNW 2025
register — tall fir stacks, sea-junk ephemera, rain outside, warm
inside. NOT a corporate bookstore: Petra buys the slow electronics
on purpose. Canon sources baked in:

  · vol7_ch8_monday: the front door on Hemlock + THE BELL over it;
    the CLOSED/OPEN flip sign; the till with the cash float; "the
    small terminal Petra kept on the counter" that hums slowly
    (Petra "did not like fast electronics and bought the slow ones
    on purpose"); the hold ledger; the NEW-ARRIVALS shelf Edgar
    buys from without asking; the children's section with the
    clean carpet + the picture book the girl had to leave behind;
    the small kitchenette in the back (Petra's kettle, the
    pour-over cone, the dark French Soren roasts, the small clay
    mug from Margit's 2009, the sandwich fridge); the desk outside
    the office door; the coat hook by the office door; Petra came
    out at seven-twenty (the wall clock); the back door off the
    alley; tokens for payment.
  · vol7_ch8_aria: the small brass bell ON the counter (Lena turns
    it over in her hand); the small stool Lena uses when she is
    alone in the shop; Tem's cup of cold coffee on the counter;
    the small table by the window display (Roy's coat, Petra's
    tote); THE CAT on the small wool pillow in the front-window
    display "where she always was".
  · vol7_ch14_petra: the kitchenette table the four of them sit
    at (Petra set out four mugs); the chair beside the radiator
    with the cat's wool pillow; the couch in the back office
    (behind the closed office door — not modeled, door is shut);
    "the bookstore opens onto the front and the alley both"; rain
    on the back window; the dumpster in the alley; the mural on
    the wall outside the back door (the Starfish Nebula Lena
    painted in '50 — the ARIA FACE from ch14 is deliberately NOT
    baked: this bg also serves ch8, pre-face).
  · lore/_VOL7_WIKI.md + milk_and_honey/static_truths.md: sells
    everything from tide charts to local zines; STATIC TRUTHS is
    photocopied on Petra's back-room copier ($2 the first run,
    free after) — the copier stands in the back-west corner with
    a fresh half-letter run in its output tray.
  · milk_and_honey/_ART_MANIFEST.md: "front counter, the wall
    where her paintings hang, the front door on Hemlock" — two
    framed sea paintings on the east wall; the kitchenette at the
    back with the cat's pillow + the alley back door.

FACADE CONSISTENCY (with build_lena_apartment.py): brick street
face (0.44,0.28,0.22), gray-green cornice (0.30,0.34,0.32), the
hanging sign = spruce-blue board (0.16,0.24,0.30) with brass rules
on a black iron arm, warm shop-window glow at grade. Lena's dark
front window sits above the shopfront here, sign hung beneath it.

No transparency: windows are REAL OPENINGS with fir frames +
mullions; the exterior (Hemlock sidewalk, streetlamp, dollar cart)
and the alley (mural wall, dumpster) live outside the openings.
Text is scene-side Label3D per the playbook; this script bakes
named vertex-colored panels:
  SaltyTome_SignBoard, FlipSign_Board, HoursPlaque, NewArrivals_Card,
  StackSign_0/1, EndcapCard_0/1, WestShelf_Card_0/1, Kids_Card,
  Zine_StaticTruths, TideChart_Sheet, OfficeDoor_Sign, HoldLedger_*,
  Copier_Output_StaticTruths, Cart_Card.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import (make_floor, make_wall, make_ceiling,
                              make_crown_molding, make_door_hinges)
from _props.store_fixtures import make_register
from _props.decor import make_wall_clock, make_floor_plant, make_fire_extinguisher
from _props.safety import make_smoke_detector, make_hvac_vent

# ── Shell (footprint kept from the scaffold — the .tscn camera at
#    Godot (0, 2.30, +0.5) looks north from the front door across
#    this 8 × 6 room; door gap x −1..+1) ──────────────────────────
ROOM_W = 8.0; ROOM_D = 6.0; CEIL = 2.8
PAL_WALL = {"wall": (0.79, 0.74, 0.64, 1.0),     # aged warm plaster
            "baseboard": (0.30, 0.24, 0.18, 1.0)}
COL_FLOOR = (0.55, 0.42, 0.30, 1.0)              # fir floorboards
COL_SEAM  = (0.33, 0.25, 0.18, 1.0)

# ── Bookshop palette (2025 PNW coastal, warm + salt-weathered) ───
COL_WOOD      = (0.48, 0.35, 0.22, 1.0)   # old oak shelving
COL_WOOD_DARK = (0.28, 0.21, 0.15, 1.0)
COL_WOOD_LT   = (0.66, 0.52, 0.34, 1.0)
COL_BUTCHER   = (0.72, 0.58, 0.38, 1.0)   # counter top ("hands flat
                                          #  on the wood", ch8_aria)
COL_BRASS     = (0.70, 0.57, 0.30, 1.0)
COL_CREAM     = (0.90, 0.87, 0.80, 1.0)
COL_SPRUCE    = (0.16, 0.24, 0.30, 1.0)   # hanging-sign board — SAME
                                          # tint as build_lena_apartment
COL_CLAY      = (0.62, 0.40, 0.28, 1.0)   # Margit's mug (2009)
COL_BEIGE_TECH= (0.82, 0.78, 0.68, 1.0)   # slow terminal housing
COL_UPHOLSTER = (0.55, 0.32, 0.22, 1.0)   # rust wool reading chair
COL_WOOL      = (0.78, 0.72, 0.62, 1.0)   # the cat's pillow
COL_CAT       = (0.42, 0.40, 0.38, 1.0)   # Petra's old gray cat
COL_CAT_DK    = (0.30, 0.28, 0.27, 1.0)
COL_RUG_A     = (0.34, 0.44, 0.44, 1.0)   # children's carpet ground
COL_RUG_B     = (0.62, 0.34, 0.24, 1.0)   # carpet border band
COL_RAINCOAT  = (0.38, 0.36, 0.26, 1.0)   # wax canvas (town uniform)
COL_RADIATOR  = (0.68, 0.66, 0.60, 1.0)   # many-coats-of-paint iron
COL_CAST_IRON = (0.13, 0.13, 0.14, 1.0)
COL_PLANT     = (0.36, 0.47, 0.32, 1.0)
COL_POT       = (0.58, 0.38, 0.26, 1.0)
COL_FLOAT     = (0.32, 0.52, 0.50, 1.0)   # glass fishing float (opaque)
COL_BRICK     = (0.44, 0.28, 0.22, 1.0)   # facade — matches lena bld
COL_BRICK_DK  = (0.32, 0.20, 0.16, 1.0)
COL_CORNICE   = (0.30, 0.34, 0.32, 1.0)
COL_CONCRETE  = (0.55, 0.54, 0.51, 1.0)
COL_ASPHALT   = (0.15, 0.15, 0.16, 1.0)
COL_PUDDLE    = (0.30, 0.33, 0.36, 1.0)
COL_XEROX     = (0.86, 0.86, 0.88, 1.0)   # copier beige (matches the
COL_XEROX_TOP = (0.32, 0.32, 0.32, 1.0)   #  harmony copy-shop machine)
COL_XEROX_PNL = (0.18, 0.18, 0.22, 1.0)
COL_STEEL     = P.METAL_STEEL
# Starfish Nebula mural fragment (alley) — SAME tints as
# build_lena_apartment.py's full mural (Lena painted it in '50)
COL_MURAL_GROUND = (0.14, 0.12, 0.26, 1.0)
COL_MURAL_OCTO   = (0.82, 0.52, 0.30, 1.0)
COL_MURAL_STAR   = (0.90, 0.82, 0.52, 1.0)
COL_MURAL_POOL   = (0.24, 0.48, 0.48, 1.0)

# Used-book spines — lena-apartment BOOK_TINTS + two coastal tones
BOOK_TINTS = [(0.48, 0.30, 0.24, 1.0), (0.28, 0.36, 0.42, 1.0),
              (0.62, 0.54, 0.34, 1.0), (0.36, 0.30, 0.38, 1.0),
              (0.70, 0.64, 0.52, 1.0), (0.30, 0.44, 0.42, 1.0),
              (0.55, 0.42, 0.28, 1.0)]
CHAIR_TINTS = [COL_WOOD, (0.34, 0.48, 0.46, 1.0), COL_WOOD_DARK,
               (0.62, 0.34, 0.22, 1.0)]

COUNTER_TOP = 0.99          # shop counter top surface z


# ═════════════════════════════════════════════════════════════════
# Local helpers (deterministic — index-cycled variation, no random)
# ═════════════════════════════════════════════════════════════════
_SPINE_W = (0.055, 0.040, 0.070, 0.045, 0.060, 0.035, 0.050, 0.065)
_SPINE_H = (0.215, 0.185, 0.240, 0.200, 0.225, 0.175, 0.230, 0.195)

def _spine_row(prefix, x0, x1, y_face, shelf_z, seed=0):
    """A run of used-book spines along X, backs at y_face, standing
    on shelf_z. Deterministic gaps + flat piles break the rhythm."""
    cursor = x0 + 0.03
    i = 0
    while cursor < x1 - 0.06:
        k = seed + i
        if k % 11 == 9:                      # pulled-book gap
            cursor += 0.055
            i += 1
            continue
        if k % 13 == 11:                     # short flat pile
            for pi in range(2):
                make_box(f"{prefix}_Flat_{i}_{pi}",
                         (cursor + 0.075, y_face, shelf_z + 0.023 + pi * 0.042),
                         (0.145, 0.20, 0.040 - pi * 0.004),
                         BOOK_TINTS[(k + pi * 3) % len(BOOK_TINTS)])
            cursor += 0.165
            i += 1
            continue
        w = _SPINE_W[k % len(_SPINE_W)]
        h = _SPINE_H[(k * 5 + 2) % len(_SPINE_H)]
        make_box(f"{prefix}_{i}", (cursor + w / 2.0, y_face, shelf_z + h / 2.0),
                 (w, 0.165, h), BOOK_TINTS[(k * 3 + 1) % len(BOOK_TINTS)])
        cursor += w + (0.004 if k % 5 else 0.014)
        i += 1

def _book_pile(prefix, cx, cy, bz, count, seed=0):
    for bi in range(count):
        k = seed + bi
        make_box(f"{prefix}_{bi}",
                 (cx + (k % 3 - 1) * 0.012, cy + (k % 2) * 0.010,
                  bz + 0.021 + bi * 0.042),
                 (0.155 - (k % 2) * 0.012, 0.215 - (k % 3) * 0.014, 0.040),
                 BOOK_TINTS[(k * 2 + 3) % len(BOOK_TINTS)])

def _chair(prefix, cx, cy, facing, tint):
    """Mismatched wood chair; `facing` = direction the sitter faces."""
    dx, dy = {'N': (0, 1), 'S': (0, -1), 'E': (1, 0), 'W': (-1, 0)}[facing]
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

def _pendant(prefix, cx, cy, drop=0.62, shade=COL_CREAM):
    """Cylinder-shade pendant — round geometry at eye level."""
    make_cyl(f"{prefix}_Canopy", (cx, cy, CEIL - 0.02), 0.05, 0.04, P.METAL_BLACK)
    make_cyl(f"{prefix}_Cord", (cx, cy, CEIL - drop / 2.0), 0.008, drop, P.METAL_BLACK)
    make_cyl(f"{prefix}_Shade", (cx, cy, CEIL - drop - 0.065), 0.15, 0.13, shade,
             segments=12)
    make_cyl(f"{prefix}_Bulb", (cx, cy, CEIL - drop - 0.135), 0.05, 0.04,
             (0.98, 0.88, 0.62, 1.0))

def _cup_saucer(prefix, cx, cy, bz, tint):
    make_cyl(f"{prefix}_Saucer", (cx, cy, bz + 0.006), 0.062, 0.012, COL_CREAM,
             segments=12)
    make_cyl(f"{prefix}_Cup", (cx, cy, bz + 0.045), 0.036, 0.065, tint)
    make_box(f"{prefix}_Handle", (cx + 0.045, cy, bz + 0.045), (0.014, 0.012, 0.04), tint)

def _mug(prefix, cx, cy, bz, tint):
    make_cyl(f"{prefix}_Body", (cx, cy, bz + 0.048), 0.038, 0.095, tint)
    make_box(f"{prefix}_Handle", (cx + 0.048, cy, bz + 0.050), (0.016, 0.014, 0.05), tint)


# ═════════════════════════════════════════════════════════════════
# SHELL — same 8 × 6 footprint as the scaffold, but the south wall
# gets REAL window openings (frames later, no glass) and the north
# wall gets the office door, the alley back door ("the bookstore
# opens onto the front and the alley both", ch14_petra) and the
# kitchenette window. Fir floor, plank ceiling, crown molding.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # Side walls — solid
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    # North wall — office door gap x −3.0..−2.1, back door gap
    # x −0.3..+0.6, kitchenette window x 2.0..3.4 (sill 1.05 head 2.25)
    make_wall("Wall_N_W", (-3.6, ROOM_D, 0), length=1.20, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_C", (-1.2, ROOM_D, 0), length=1.80, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_E1", (1.3, ROOM_D, 0), length=1.40, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_E2", (3.8, ROOM_D, 0), length=0.80, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_N_AboveOffice", (-2.55, ROOM_D, 2.50), (0.90, 0.20, 0.60), PAL_WALL["wall"])
    make_box("Wall_N_AboveBack", (0.15, ROOM_D, 2.50), (0.90, 0.20, 0.60), PAL_WALL["wall"])
    make_box("Wall_N_KitchSill", (2.7, ROOM_D, 0.525), (1.40, 0.20, 1.05), PAL_WALL["wall"])
    make_box("Wall_N_KitchHeader", (2.7, ROOM_D, 2.525), (1.40, 0.20, 0.55), PAL_WALL["wall"])
    # South (Hemlock storefront) wall — door gap x −1..+1, window
    # openings x −3.1..−1.3 and +1.3..+3.1 (sill 0.75, head 2.30)
    for nm, px, pw in [("Wall_S_PierSW", -3.65, 1.10), ("Wall_S_PierWD", -1.15, 0.30),
                       ("Wall_S_PierED", +1.15, 0.30), ("Wall_S_PierSE", +3.65, 1.10)]:
        make_box(nm, (px, 0.0, CEIL / 2.0), (pw, 0.20, CEIL), PAL_WALL["wall"])
    for tag, wx in [("W", -2.2), ("E", +2.2)]:
        make_box(f"Wall_S_{tag}_Sill", (wx, 0.0, 0.375), (1.80, 0.20, 0.75), PAL_WALL["wall"])
        make_box(f"Wall_S_{tag}_SillBase", (wx, 0.06, 0.08), (1.80, 0.06, 0.16),
                 PAL_WALL["baseboard"])
        make_box(f"Wall_S_{tag}_Header", (wx, 0.0, 2.55), (1.80, 0.20, 0.50), PAL_WALL["wall"])
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.28), (2.0, 0.20, 0.56), PAL_WALL["wall"])
    # Ceiling — painted planks with battens (pre-war building)
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
# STOREFRONT — fir frames + mullions in the openings (no glass),
# the front door on Hemlock, THE BELL over it (ch8_monday: it rings
# at eleven fifty-eight when Roy comes in; ch8_aria: "She looked at
# the bell over the door for a long count"), the CLOSED/OPEN flip
# sign ("She turned the CLOSED sign"), the window displays — cat on
# her wool pillow east, sea-junk + tide charts west — and the small
# table by the window display (Roy's coat / Petra's tote land here).
# ═════════════════════════════════════════════════════════════════
def _window_frame_south(tag, wx):
    """Frame + mullions for a south opening centered at wx.
    Opening 1.8 wide, z 0.75..2.30, transom bar at 1.95."""
    make_box(f"WinS_{tag}_Sill", (wx, 0.0, 0.735), (1.92, 0.22, 0.07), COL_WOOD)
    make_box(f"WinS_{tag}_Ledge", (wx, 0.14, 0.775), (1.80, 0.14, 0.03), COL_WOOD_LT)
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
    # Front door — solid fir leaf, west-hinged, brass knob (a shop
    # you can lock from the inside, ch8_aria: Tem's instruction)
    for sgn in (-1, +1):
        make_box(f"Door_Post_{sgn:+d}", (sgn * 0.96, 0.0, 1.10), (0.08, 0.16, 2.20), COL_WOOD)
    make_box("Door_Transom", (0.0, 0.0, 2.24), (2.00, 0.16, 0.08), COL_WOOD)
    make_box("Door_Leaf", (-0.50, 0.02, 1.08), (0.90, 0.05, 2.10), COL_WOOD_DARK)
    for pi in range(2):
        make_box(f"Door_Panel_{pi}", (-0.50, -0.012, 0.62 + pi * 0.95),
                 (0.62, 0.008, 0.72), COL_WOOD)
    make_cyl("Door_Knob", (-0.14, -0.06, 1.02), 0.028, 0.05, COL_BRASS, axis='Y')
    make_box("Door_Deadbolt", (-0.14, -0.045, 1.18), (0.05, 0.02, 0.08), COL_BRASS)
    make_box("Door_KickPlate", (-0.50, -0.015, 0.15), (0.80, 0.02, 0.26), COL_BRASS)
    make_door_hinges("Door_Hinge", edge_x=-0.92, edge_y=0.0,
                     edge_z_centers=[0.35, 1.05, 1.80], axis='X')
    # THE BELL over the door (brass, bracket-mounted)
    make_box("DoorBell_Mount", (0.55, 0.13, 2.32), (0.06, 0.10, 0.06), P.METAL_BLACK)
    make_cyl("DoorBell_Arm", (0.55, 0.24, 2.32), 0.012, 0.16, COL_BRASS, axis='Y')
    make_cyl("DoorBell_Body", (0.55, 0.32, 2.27), 0.050, 0.07, COL_BRASS)
    make_cyl("DoorBell_Flare", (0.55, 0.32, 2.22), 0.068, 0.025, COL_BRASS)
    make_cyl("DoorBell_Clapper", (0.55, 0.32, 2.18), 0.012, 0.05, P.METAL_BLACK)
    # CLOSED/OPEN flip sign on a cord in the east sidelite position
    make_cyl("FlipSign_Cord", (0.45, 0.05, 1.98), 0.004, 0.28, P.TWINE, axis='Z')
    make_box("FlipSign_Board", (0.45, 0.05, 1.74), (0.36, 0.02, 0.20), COL_CREAM)
    make_box("FlipSign_Text_In", (0.45, 0.063, 1.74), (0.28, 0.006, 0.09), COL_SPRUCE)
    make_box("FlipSign_Text_Out", (0.45, 0.037, 1.74), (0.28, 0.006, 0.09), COL_SPRUCE)
    make_box("HoursPlaque", (1.15, 0.105, 1.50), (0.16, 0.010, 0.22), P.PAPER)
    # Entry mat + umbrella stand (rain register)
    make_box("EntryMat_Under", (0.0, 0.80, 0.004), (1.90, 1.00, 0.006), (0.14, 0.13, 0.13, 1.0))
    make_box("EntryMat", (0.0, 0.80, 0.011), (1.76, 0.88, 0.008), P.RUBBER_MAT)
    make_cyl("UmbrellaStand", (-1.35, 0.45, 0.28), 0.11, 0.56, P.METAL_BLACK, segments=12)
    make_cyl("Umbrella_Shaft", (-1.31, 0.41, 0.62), 0.012, 0.75, P.METAL_BLACK)
    make_cyl("Umbrella_Canopy", (-1.31, 0.41, 0.78), 0.045, 0.34, (0.24, 0.28, 0.38, 1.0))
    make_cyl("Umbrella_Tip", (-1.31, 0.41, 1.02), 0.006, 0.10, COL_STEEL)
    # ── EAST window display — THE CAT (ch8_monday: "on the small
    # wool pillow in the front-window display where she always
    # was"; asleep — she opens one eye scene-side, not here)
    make_box("WinDispE_Platform", (2.2, 0.42, 0.12), (1.70, 0.55, 0.24), COL_WOOD)
    make_cyl("Cat_Pillow", (2.62, 0.42, 0.265), 0.17, 0.055, COL_WOOL, segments=12)
    make_cyl("Cat_Body", (2.62, 0.44, 0.375), 0.085, 0.26, COL_CAT, axis='Y', segments=12)
    make_cyl("Cat_Head", (2.62, 0.28, 0.405), 0.055, 0.09, COL_CAT, axis='Y', segments=12)
    for ei, ex in enumerate((2.585, 2.655)):
        make_box(f"Cat_Ear_{ei}", (ex, 0.27, 0.465), (0.020, 0.020, 0.028), COL_CAT_DK)
    make_box("Cat_Muzzle", (2.62, 0.235, 0.385), (0.035, 0.02, 0.025), COL_CREAM)
    for si in range(3):
        make_box(f"Cat_Stripe_{si}", (2.62, 0.36 + si * 0.07, 0.462),
                 (0.10, 0.022, 0.012), COL_CAT_DK)
    make_cyl("Cat_Tail", (2.54, 0.55, 0.30), 0.020, 0.18, COL_CAT_DK, axis='X')
    # Display books west of the cat (spines to the street too)
    _book_pile("WinDispE_Pile", 1.65, 0.42, 0.24, 4, seed=2)
    for fi in range(2):
        make_box(f"WinDispE_FaceOut_{fi}", (1.95 + fi * 0.24, 0.30, 0.395),
                 (0.16, 0.035, 0.23), BOOK_TINTS[(fi * 4 + 1) % len(BOOK_TINTS)])
        make_box(f"WinDispE_Stand_{fi}", (1.95 + fi * 0.24, 0.34, 0.30),
                 (0.10, 0.06, 0.12), COL_WOOD_DARK)
    make_box("WinDispE_PriceCard", (1.65, 0.24, 0.29), (0.09, 0.008, 0.06), P.PAPER)
    # ── WEST window display — sea junk + tide charts (wiki: "sells
    # everything from tide charts to local zines")
    make_box("WinDispW_Platform", (-2.2, 0.42, 0.12), (1.70, 0.55, 0.24), COL_WOOD)
    make_box("TideChart_Crate", (-2.75, 0.42, 0.35), (0.34, 0.34, 0.22), COL_WOOD_DARK,
             open_faces={'+Z'})
    for ri in range(4):
        make_cyl(f"TideChart_Roll_{ri}", (-2.85 + (ri % 2) * 0.11, 0.36 + (ri // 2) * 0.13,
                 0.42 + (ri % 3) * 0.012), 0.028, 0.30, P.PAPER_AGED)
    for gi, (gx, gr) in enumerate([(-2.25, 0.075), (-2.05, 0.055)]):
        make_cyl(f"GlassFloat_{gi}", (gx, 0.40, 0.24 + gr), gr, gr * 1.7, COL_FLOAT,
                 segments=12)
        make_box(f"GlassFloat_{gi}_NetA", (gx, 0.40, 0.24 + gr), (gr * 2.1, 0.012, 0.012),
                 P.TWINE)
        make_box(f"GlassFloat_{gi}_NetB", (gx, 0.40, 0.24 + gr), (0.012, gr * 2.1, 0.012),
                 P.TWINE)
    make_box("Driftwood", (-1.62, 0.44, 0.29), (0.42, 0.14, 0.10), (0.58, 0.52, 0.44, 1.0))
    _book_pile("WinDispW_Pile", -1.60, 0.30, 0.24, 3, seed=9)
    # The small table by the window display (ch8_monday: Roy sets
    # the wax canvas coat on it; ch8_aria: Petra's tote bag)
    make_cyl("WinTable_Top", (2.85, 1.10, 0.74), 0.30, 0.04, COL_WOOD_LT, segments=12)
    make_cyl("WinTable_Column", (2.85, 1.10, 0.38), 0.045, 0.68, COL_WOOD_DARK)
    make_cyl("WinTable_Base", (2.85, 1.10, 0.025), 0.17, 0.05, COL_WOOD_DARK, segments=12)
    _book_pile("WinTable_Pile", 2.85, 1.10, 0.76, 3, seed=5)


# ═════════════════════════════════════════════════════════════════
# EXTERIOR · HEMLOCK (south) — sidewalk, curb, wet street, brick
# facade + cornice + Lena's dark window above the shop (SAME brick
# / cornice / sign treatment as build_lena_apartment.py, which
# models this facade from her window), the hanging spruce-blue
# SALTY TOME sign, a streetlamp, and the dollar cart.
# ═════════════════════════════════════════════════════════════════
def build_exterior_street():
    make_box("Ext_Sidewalk", (0.0, -1.25, -0.03), (9.6, 2.50, 0.06), COL_CONCRETE)
    for si in range(4):
        make_box(f"Ext_SidewalkSeam_{si}", (-3.1 + si * 2.0, -1.25, 0.001),
                 (0.02, 2.50, 0.002), (0.40, 0.39, 0.37, 1.0))
    make_box("Ext_Curb", (0.0, -2.55, -0.02), (9.6, 0.16, 0.12), (0.46, 0.45, 0.43, 1.0))
    make_box("Ext_Street", (0.0, -3.70, -0.05), (9.6, 2.20, 0.04), COL_ASPHALT)
    make_box("Ext_Puddle_0", (1.6, -3.30, -0.028), (1.30, 0.60, 0.002), COL_PUDDLE)
    make_box("Ext_Puddle_1", (-2.4, -1.05, 0.002), (0.80, 0.42, 0.002), COL_PUDDLE)
    # Brick facade — pilasters, upper storey band, cornice (brick +
    # cornice tints match build_lena_apartment's street face)
    for pi, px in enumerate((-4.05, +4.05)):
        make_box(f"Facade_Pilaster_{pi}", (px, -0.02, 2.15), (0.30, 0.24, 4.30), COL_BRICK)
    make_box("Facade_UpperBand", (0.0, -0.02, 3.56), (8.40, 0.24, 1.52), COL_BRICK)
    make_box("Facade_BrickCourse", (0.0, -0.10, 2.84), (8.40, 0.10, 0.08), COL_BRICK_DK)
    make_box("Facade_Cornice", (0.0, -0.14, 4.40), (8.70, 0.50, 0.20), COL_CORNICE)
    # Lena's front window over the shopfront (the window she looks
    # down at Hemlock from) + the stairwell window — both dark
    for wi, wx in enumerate((-1.5, +1.7)):
        make_box(f"Upstairs_Win_{wi}_Recess", (wx, -0.10, 3.55), (0.86, 0.06, 1.10),
                 (0.10, 0.10, 0.12, 1.0))
        make_box(f"Upstairs_Win_{wi}_SillExt", (wx, -0.16, 2.96), (0.98, 0.14, 0.07), COL_WOOD)
        make_box(f"Upstairs_Win_{wi}_Head", (wx, -0.16, 4.14), (0.98, 0.14, 0.07), COL_WOOD)
        for sgn in (-1, +1):
            make_box(f"Upstairs_Win_{wi}_Jamb_{sgn:+d}", (wx + sgn * 0.46, -0.16, 3.55),
                     (0.06, 0.14, 1.25), COL_WOOD)
        make_box(f"Upstairs_Win_{wi}_Mull", (wx, -0.16, 3.55), (0.86, 0.10, 0.05), COL_WOOD)
    # THE HANGING SIGN under Lena's window — iron arm, chain links,
    # spruce-blue board + brass rules; lettering scene-side Label3D
    # (mirror of build_lena_apartment's SaltyTome_Sign* from street)
    make_box("SaltyTome_SignMount", (-1.5, -0.14, 2.66), (0.10, 0.06, 0.16), P.METAL_BLACK)
    make_box("SaltyTome_SignArm", (-1.5, -0.42, 2.70), (0.04, 0.52, 0.04), P.METAL_BLACK)
    for hi, hy in enumerate((-0.28, -0.56)):
        make_cyl(f"SaltyTome_SignLink_{hi}", (-1.5, hy, 2.62), 0.008, 0.14, P.METAL_BLACK)
    make_box("SaltyTome_SignBoard", (-1.5, -0.42, 2.36), (0.05, 0.44, 0.40), COL_SPRUCE)
    for ri, sgn in enumerate((-1, +1)):
        make_box(f"SaltyTome_SignRule_{ri}", (-1.5 + sgn * 0.028, -0.42, 2.50),
                 (0.006, 0.36, 0.04), COL_BRASS)
    # Streetlamp on the curb-side buffer (public right-of-way rule)
    make_cyl("Streetlamp_Pole", (-3.7, -2.30, 2.10), 0.045, 4.20, P.METAL_BLACK, segments=12)
    make_cyl("Streetlamp_Arm", (-3.55, -2.30, 4.05), 0.025, 0.40, P.METAL_BLACK, axis='X')
    make_cyl("Streetlamp_Head", (-3.32, -2.30, 3.98), 0.09, 0.14, P.METAL_BLACK, segments=12)
    make_cyl("Streetlamp_Glow", (-3.32, -2.30, 3.89), 0.065, 0.05, (0.98, 0.84, 0.56, 1.0),
             segments=12)
    # The dollar cart under the east window (used-bookshop register;
    # card lettering scene-side on Cart_Card)
    make_box("Cart_Body", (2.3, -0.55, 0.52), (0.96, 0.42, 0.50), COL_WOOD, open_faces={'+Z'})
    make_box("Cart_LowerShelf", (2.3, -0.55, 0.30), (0.90, 0.36, 0.03), COL_WOOD_DARK)
    for ci, (cx2, cy2) in enumerate([(1.92, -0.71), (2.68, -0.71), (1.92, -0.39),
                                     (2.68, -0.39)]):
        make_cyl(f"Cart_Caster_{ci}", (cx2, cy2, 0.06), 0.05, 0.04, P.METAL_BLACK, axis='Y')
    _spine_row("Cart_RowA", 1.90, 2.70, -0.64, 0.77, seed=31)
    _spine_row("Cart_RowB", 1.90, 2.70, -0.46, 0.77, seed=47)
    make_box("Cart_Card", (2.3, -0.78, 0.88), (0.22, 0.010, 0.12), P.PAPER_AGED)
    make_floor_plant("Ext_Planter", (-2.6, -0.55, 0.0))


# ═════════════════════════════════════════════════════════════════
# EXTERIOR · ALLEY (north) — what the kitchenette window shows:
# the opposite building with the STARFISH NEBULA mural fragment
# (Lena painted it in '50; ch14_petra: "the mural on the wall
# outside my back door" — the ARIA FACE is ch14-morning-only and
# deliberately NOT baked, this bg serves ch8 too), the dumpster
# Petra reads at, a caged safety light over the back door, rain
# puddles.
# ═════════════════════════════════════════════════════════════════
def build_exterior_alley():
    make_box("Alley_Ground", (0.6, 7.25, -0.03), (10.0, 2.90, 0.06), COL_ASPHALT)
    make_box("Alley_Puddle_0", (2.4, 7.0, 0.002), (1.20, 0.55, 0.002), COL_PUDDLE)
    make_box("Alley_Puddle_1", (0.2, 7.6, 0.002), (0.70, 0.40, 0.002), COL_PUDDLE)
    # Opposite building — dark brick, mural fragment facing us
    make_box("Alley_OppositeWall", (1.4, 8.75, 2.20), (7.60, 0.15, 4.40), COL_BRICK_DK)
    make_box("Mural_Ground", (2.7, 8.66, 1.85), (2.60, 0.02, 2.50), COL_MURAL_GROUND)
    make_cyl("Mural_Octo_Head", (2.1, 8.64, 2.35), 0.42, 0.012, COL_MURAL_OCTO,
             axis='Y', segments=12)
    for ai, (ax, alen) in enumerate([(1.75, 1.10), (2.05, 1.40), (2.40, 0.95)]):
        make_box(f"Mural_Octo_Arm_{ai}", (ax, 8.645, 1.95 - alen / 2.0 + 0.60),
                 (0.13, 0.012, alen), COL_MURAL_OCTO)
    make_box("Mural_Starfish", (3.45, 8.645, 2.65), (0.44, 0.012, 0.44), COL_MURAL_STAR)
    make_box("Mural_PoolBand", (2.7, 8.645, 0.85), (2.40, 0.012, 0.38), COL_MURAL_POOL)
    # The dumpster (ch14_petra: "by my reading at the dumpster")
    make_box("Dumpster_Body", (1.3, 7.7, 0.55), (1.50, 0.85, 1.00), (0.20, 0.30, 0.24, 1.0))
    make_box("Dumpster_Lid", (1.3, 7.62, 1.08), (1.54, 0.72, 0.06), (0.16, 0.24, 0.19, 1.0))
    make_box("Dumpster_Skid_0", (0.7, 7.7, 0.06), (0.14, 0.80, 0.12), COL_CAST_IRON)
    make_box("Dumpster_Skid_1", (1.9, 7.7, 0.06), (0.14, 0.80, 0.12), COL_CAST_IRON)
    # Caged safety light over the back door (exterior north face)
    make_box("AlleyLight_Base", (0.15, 6.14, 2.45), (0.16, 0.06, 0.16), P.METAL_BLACK)
    make_cyl("AlleyLight_Glow", (0.15, 6.20, 2.45), 0.055, 0.09, (0.98, 0.84, 0.56, 1.0),
             axis='Y')
    for gi in range(3):
        make_box(f"AlleyLight_Cage_{gi}", (0.07 + gi * 0.08, 6.24, 2.45),
                 (0.012, 0.10, 0.16), P.METAL_BLACK)


# ═════════════════════════════════════════════════════════════════
# COUNTER — Petra's counter, plank-faced, wood top ("hands flat on
# the wood between them", ch8_aria). On it, west→east: the hold
# ledger + pencil (ch8_monday), the small brass bell (ch8_aria),
# Tem's cup of cold coffee (ch8_aria), the token dish (Edgar and
# Mr. Marsden pay in tokens), the SLOW TERMINAL ("Petra did not
# like fast electronics and bought the slow ones on purpose"), and
# the till ("The till is unlocked. The float is one-twenty").
# Lena's stool behind (ch8_aria: Tem pulls it around).
# ═════════════════════════════════════════════════════════════════
def build_counter():
    # Body x −0.15..2.15, customer face y 3.54, top z COUNTER_TOP
    make_box("Counter_Body", (1.0, 3.85, 0.46), (2.30, 0.62, 0.92), COL_WOOD)
    make_box("Counter_Top", (1.0, 3.85, 0.96), (2.46, 0.74, 0.06), COL_BUTCHER)
    make_box("Counter_Kick", (1.0, 3.53, 0.10), (2.30, 0.02, 0.20), COL_WOOD_DARK)
    for pi in range(6):
        px = -0.02 + pi * 0.41
        make_box(f"Counter_Plank_{pi}", (px, 3.535, 0.52), (0.34, 0.012, 0.78),
                 COL_WOOD_LT if pi % 2 == 0 else COL_WOOD)
    make_box("Counter_Notice", (0.45, 3.528, 0.70), (0.16, 0.008, 0.22), P.PAPER_AGED)
    # Hold ledger, open, with pencil (ch8_monday: "wrote the name
    # down in the hold ledger as Petra had taught her to do")
    for li, sgn in enumerate((-1, +1)):
        make_box(f"HoldLedger_Page_{li}", (0.35 + sgn * 0.105, 3.72, COUNTER_TOP + 0.008),
                 (0.20, 0.28, 0.016), P.PAPER)
    make_box("HoldLedger_Spine", (0.35, 3.72, COUNTER_TOP + 0.006), (0.03, 0.28, 0.020),
             COL_WOOD_DARK)
    make_cyl("HoldLedger_Pencil", (0.35, 3.90, COUNTER_TOP + 0.008), 0.006, 0.16,
             (0.82, 0.64, 0.28, 1.0), axis='X')
    # The small brass bell (ch8_aria — Lena turns it over in her hand)
    make_cyl("CounterBell_Base", (0.02, 3.70, COUNTER_TOP + 0.006), 0.045, 0.012,
             COL_WOOD_DARK)
    make_cyl("CounterBell_Dome", (0.02, 3.70, COUNTER_TOP + 0.030), 0.038, 0.036, COL_BRASS)
    make_cyl("CounterBell_Button", (0.02, 3.70, COUNTER_TOP + 0.054), 0.008, 0.014,
             P.METAL_BLACK)
    # Tem's coffee, gone cold at the counter's west end (ch8_aria)
    _cup_saucer("TemCoffee", -0.05, 3.95, COUNTER_TOP, COL_CREAM)
    # Token dish — Smolvud runs on tokens (ch8_monday: Edgar +
    # Mr. Marsden both pay in tokens)
    make_cyl("TokenDish", (0.68, 3.70, COUNTER_TOP + 0.010), 0.055, 0.020, COL_WOOD)
    for ti in range(4):
        make_cyl(f"Token_{ti}", (0.67 + (ti % 2) * 0.022, 3.70 + (ti % 3) * 0.014,
                 COUNTER_TOP + 0.022 + (ti // 2) * 0.007), 0.026, 0.006, COL_WOOD_LT)
    # The slow terminal — beige CRT, humming carefully (ch8_monday)
    make_box("Terminal_Base", (1.15, 3.95, COUNTER_TOP + 0.035), (0.34, 0.32, 0.07),
             COL_BEIGE_TECH)
    make_box("Terminal_CRT", (1.15, 3.98, COUNTER_TOP + 0.21), (0.30, 0.28, 0.28),
             COL_BEIGE_TECH)
    make_box("Terminal_Screen", (1.15, 3.825, COUNTER_TOP + 0.22), (0.22, 0.012, 0.17),
             (0.08, 0.14, 0.10, 1.0))
    make_box("Terminal_ScreenLine", (1.15, 3.818, COUNTER_TOP + 0.27), (0.16, 0.004, 0.014),
             (0.36, 0.62, 0.40, 1.0))
    make_box("Terminal_Keyboard", (1.15, 3.70, COUNTER_TOP + 0.020), (0.30, 0.13, 0.030),
             (0.72, 0.68, 0.58, 1.0))
    for vi in range(3):
        make_box(f"Terminal_Vent_{vi}", (1.325, 3.98, COUNTER_TOP + 0.13 + vi * 0.05),
                 (0.006, 0.22, 0.014), (0.62, 0.58, 0.50, 1.0))
    # The till (make_register's 90s POS reads right for a shopkeeper
    # who buys the slow ones on purpose)
    make_register("Till", (1.80, 3.92, COUNTER_TOP), palette={"body": (0.30, 0.29, 0.28, 1.0)})
    # Lena's stool, behind the counter (ch8_aria)
    make_cyl("LenaStool_Seat", (1.0, 4.42, 0.60), 0.16, 0.045, COL_WOOD, segments=12)
    for li2, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"LenaStool_Leg_{li2}", (1.0 + sx * 0.10, 4.42 + sy * 0.10, 0.29),
                 0.016, 0.58, COL_WOOD_DARK)
    # Kraft-wrapped hold parcels on the back shelf (Petra tapes the
    # torn dust jackets, ch8_monday)
    make_box("Counter_BackShelf", (0.5, 4.05, 0.55), (1.10, 0.30, 0.025), COL_WOOD_DARK)
    for pi2 in range(2):
        make_box(f"HoldParcel_{pi2}", (0.25 + pi2 * 0.45, 4.05, 0.615),
                 (0.26, 0.20, 0.09), P.PAPER_AGED)
        make_box(f"HoldParcel_{pi2}_Twine", (0.25 + pi2 * 0.45, 4.05, 0.663),
                 (0.28, 0.02, 0.012), P.TWINE)


# ═════════════════════════════════════════════════════════════════
# THE STACKS — two tall double-sided runs west of the center aisle,
# 2.2 m of used spines (the register's "tall stacks"), endcaps
# facing the aisle, top piles. Section lettering scene-side on
# StackSign_0/1 + EndcapCard_0/1.
# ═════════════════════════════════════════════════════════════════
def _stack_run(idx, cy):
    x0, x1 = -3.0, -0.7
    cx = (x0 + x1) / 2.0
    length = x1 - x0
    h = 2.20
    make_box(f"Stack_{idx}_Plinth", (cx, cy, 0.06), (length, 0.56, 0.12), COL_WOOD_DARK)
    make_box(f"Stack_{idx}_Divider", (cx, cy, h / 2.0), (length, 0.05, h), COL_WOOD)
    for si, sx in enumerate((x0, x1)):
        make_box(f"Stack_{idx}_Side_{si}", (sx + (0.025 if si == 0 else -0.025), cy, h / 2.0),
                 (0.05, 0.56, h), COL_WOOD)
    make_box(f"Stack_{idx}_Cap", (cx, cy, h + 0.025), (length + 0.06, 0.60, 0.05), COL_WOOD)
    make_box(f"StackSign_{idx}", (cx, cy, h + 0.14), (0.90, 0.04, 0.18), COL_SPRUCE)
    for face, fsgn in (("S", -1), ("N", +1)):
        for shelf_i, sz in enumerate((0.14, 0.66, 1.18, 1.70)):
            make_box(f"Stack_{idx}_{face}_Shelf_{shelf_i}",
                     (cx, cy + fsgn * 0.145, sz), (length - 0.10, 0.24, 0.035), COL_WOOD_DARK)
            _spine_row(f"Stack_{idx}_{face}_Books_{shelf_i}", x0 + 0.06, x1 - 0.06,
                       cy + fsgn * 0.155, sz + 0.018,
                       seed=idx * 17 + shelf_i * 5 + (0 if face == "S" else 51))
    _book_pile(f"Stack_{idx}_TopPile_A", x0 + 0.45, cy, h + 0.05, 3, seed=idx * 7 + 1)
    _book_pile(f"Stack_{idx}_TopPile_B", x1 - 0.50, cy, h + 0.05, 2, seed=idx * 7 + 4)
    # Endcap facing the center aisle — face-out staff picks
    make_box(f"Endcap_{idx}_Panel", (x1 + 0.02, cy, 1.10), (0.04, 0.50, 2.20), COL_WOOD)
    for fi, fz in enumerate((0.55, 1.15, 1.75)):
        make_box(f"Endcap_{idx}_Ledge_{fi}", (x1 + 0.08, cy, fz - 0.14),
                 (0.10, 0.44, 0.025), COL_WOOD_DARK)
        make_box(f"Endcap_{idx}_Book_{fi}", (x1 + 0.075, cy - 0.02, fz),
                 (0.035, 0.165, 0.24), BOOK_TINTS[(idx * 5 + fi * 2) % len(BOOK_TINTS)])
    make_box(f"EndcapCard_{idx}", (x1 + 0.045, cy, 1.98), (0.012, 0.26, 0.12), P.PAPER)

def build_stacks():
    _stack_run(0, 2.50)
    _stack_run(1, 3.80)


# ═════════════════════════════════════════════════════════════════
# WEST WALL — full-height wall shelving with the ROLLING LADDER
# (2.35 m shelves warrant it), and the CHILDREN'S SECTION at the
# front: low case, picture books face-out (the one the girl had to
# leave behind goes back face-out, ch8_monday), the clean carpet
# ("take your time, the carpet's clean"), a floor cushion.
# ═════════════════════════════════════════════════════════════════
def build_west_wall():
    wall_face = -ROOM_W / 2.0 + 0.10          # −3.90
    # Wall shelving y 2.2..4.9, 2.35 high, spines face east
    y0, y1 = 2.2, 4.9
    cyy = (y0 + y1) / 2.0
    make_box("WestShelf_Back", (wall_face + 0.02, cyy, 1.175), (0.04, y1 - y0, 2.35), COL_WOOD)
    for si, sy in enumerate((y0, cyy, y1)):
        make_box(f"WestShelf_Upright_{si}", (wall_face + 0.14, sy, 1.175),
                 (0.24, 0.05, 2.35), COL_WOOD)
    make_box("WestShelf_Cap", (wall_face + 0.14, cyy, 2.375), (0.28, y1 - y0 + 0.10, 0.05),
             COL_WOOD)
    for shelf_i, sz in enumerate((0.14, 0.60, 1.06, 1.52, 1.98)):
        make_box(f"WestShelf_Board_{shelf_i}", (wall_face + 0.14, cyy, sz),
                 (0.24, y1 - y0 - 0.10, 0.035), COL_WOOD_DARK)
        # Books run along Y here — reuse _spine_row by mapping X→Y
        # via a thin local loop (deterministic like _spine_row)
        cursor = y0 + 0.09
        bi = 0
        while cursor < y1 - 0.12:
            k = shelf_i * 23 + bi
            if k % 11 == 9:
                cursor += 0.055
                bi += 1
                continue
            w = _SPINE_W[k % len(_SPINE_W)]
            h2 = _SPINE_H[(k * 5 + 2) % len(_SPINE_H)]
            make_box(f"WestShelf_Book_{shelf_i}_{bi}",
                     (wall_face + 0.16, cursor + w / 2.0, sz + 0.018 + h2 / 2.0),
                     (0.165, w, h2), BOOK_TINTS[(k * 3 + 2) % len(BOOK_TINTS)])
            cursor += w + (0.004 if k % 5 else 0.014)
            bi += 1
    for ci2, cz2 in enumerate((0.90, 1.82)):
        make_box(f"WestShelf_Card_{ci2}", (wall_face + 0.27, y0 + 0.5 + ci2 * 1.4, cz2),
                 (0.012, 0.24, 0.10), P.PAPER)
    # ROLLING LADDER — brass rail along the shelf face, near-vertical
    # ladder hooked on (axis-aligned per the no-diagonal rule)
    make_cyl("Ladder_Rail", (wall_face + 0.30, cyy, 2.30), 0.016, y1 - y0 - 0.10, COL_BRASS,
             axis='Y')
    for bi2, byy in enumerate((y0 + 0.15, cyy, y1 - 0.15)):
        make_box(f"Ladder_RailBracket_{bi2}", (wall_face + 0.245, byy, 2.30),
                 (0.10, 0.03, 0.03), P.METAL_BLACK)
    for si2, syy in enumerate((2.88, 3.32)):
        make_cyl(f"Ladder_Stile_{si2}", (wall_face + 0.34, syy, 1.13), 0.022, 2.26, COL_WOOD)
        make_box(f"Ladder_Hook_{si2}", (wall_face + 0.32, syy, 2.29), (0.06, 0.04, 0.07),
                 COL_BRASS)
        make_cyl(f"Ladder_Wheel_{si2}", (wall_face + 0.36, syy, 0.035), 0.035, 0.03,
                 P.METAL_BLACK, axis='Y')
    for ri2 in range(6):
        make_cyl(f"Ladder_Rung_{ri2}", (wall_face + 0.34, 3.10, 0.30 + ri2 * 0.32),
                 0.016, 0.40, COL_WOOD_DARK, axis='Y')
    # ── CHILDREN'S SECTION (SW front corner) ─────────────────────
    make_box("Kids_Rug", (-3.0, 1.25, 0.008), (1.55, 1.30, 0.012), COL_RUG_A)
    make_box("Kids_Rug_Border", (-3.0, 1.25, 0.014), (1.25, 1.00, 0.004), COL_RUG_B)
    make_box("Kids_Rug_Center", (-3.0, 1.25, 0.018), (0.95, 0.70, 0.004), COL_RUG_A)
    # Low case against the west wall
    make_box("Kids_Case_Back", (wall_face + 0.02, 1.25, 0.46), (0.04, 1.50, 0.92), COL_WOOD)
    for ki, kyy in enumerate((0.50, 1.25, 2.00)):
        make_box(f"Kids_Case_Upright_{ki}", (wall_face + 0.13, kyy, 0.46),
                 (0.22, 0.04, 0.92), COL_WOOD)
    make_box("Kids_Case_Cap", (wall_face + 0.13, 1.25, 0.935), (0.26, 1.58, 0.03), COL_WOOD)
    for shelf_i2, kz in enumerate((0.10, 0.50)):
        make_box(f"Kids_Case_Board_{shelf_i2}", (wall_face + 0.13, 1.25, kz),
                 (0.22, 1.44, 0.03), COL_WOOD_DARK)
        cursor = 0.58
        bi3 = 0
        while cursor < 1.88:
            k = shelf_i2 * 31 + bi3 + 7
            w = 0.05 + (k % 4) * 0.012
            make_box(f"Kids_Book_{shelf_i2}_{bi3}",
                     (wall_face + 0.15, cursor + w / 2.0, kz + 0.016 + 0.10),
                     (0.15, w, 0.20 - (k % 3) * 0.02),
                     BOOK_TINTS[(k * 2 + 5) % len(BOOK_TINTS)])
            cursor += w + 0.008
            bi3 += 1
    # The picture book the girl left behind — face-out on top
    # (ch8_monday: "they would come back on Saturday for the third")
    make_box("Kids_FaceOut_Stand", (wall_face + 0.16, 1.05, 0.99), (0.10, 0.08, 0.10),
             COL_WOOD_DARK)
    make_box("Kids_FaceOut_Book", (wall_face + 0.18, 1.05, 1.09), (0.035, 0.22, 0.24),
             (0.82, 0.64, 0.28, 1.0))
    _book_pile("Kids_TopPile", -3.72, 1.55, 0.95, 2, seed=13)
    make_box("Kids_Card", (wall_face + 0.26, 1.25, 0.80), (0.012, 0.22, 0.10), P.PAPER)
    # Floor cushion where the girl sat with all three books open
    make_cyl("Kids_Cushion", (-2.75, 1.15, 0.055), 0.20, 0.11, COL_RUG_B, segments=12)
    make_box("Kids_OpenBook_PageL", (-3.10, 1.45, 0.026), (0.15, 0.20, 0.012), P.PAPER)
    make_box("Kids_OpenBook_PageR", (-2.95, 1.45, 0.026), (0.15, 0.20, 0.012), P.PAPER)
    make_box("Kids_OpenBook_Spine", (-3.025, 1.45, 0.022), (0.02, 0.20, 0.016),
             BOOK_TINTS[5])


# ═════════════════════════════════════════════════════════════════
# EAST WALL — the local-zine rack (STATIC TRUTHS face-out among
# them, static_truths.md), the reading nook (rust wool armchair +
# side table + floor lamp), "the wall where her paintings hang"
# (_ART_MANIFEST) — two sea paintings — a framed tide chart by the
# counter, and the radiator with the cat's OTHER wool cushion on
# the chair beside it (ch14_petra).
# ═════════════════════════════════════════════════════════════════
def build_east_wall():
    wall_face = ROOM_W / 2.0 - 0.10           # +3.90
    # ── Zine rack (front, y 0.5..1.5) — local zines, face-out ────
    make_box("ZineRack_Back", (wall_face + 0.02, 1.0, 1.25), (0.04, 1.00, 1.10), COL_WOOD)
    for zi, zz in enumerate((0.90, 1.30, 1.70)):
        make_box(f"ZineRack_Rail_{zi}", (wall_face - 0.055, 1.0, zz - 0.11),
                 (0.10, 0.96, 0.025), COL_WOOD_DARK)
        make_box(f"ZineRack_Lip_{zi}", (wall_face - 0.105, 1.0, zz - 0.085),
                 (0.012, 0.96, 0.05), COL_WOOD_DARK)
    zine_tints = [P.PAPER, (0.42, 0.52, 0.62, 1.0), P.PAPER_AGED,
                  (0.86, 0.66, 0.34, 1.0), P.NEWSPRINT, P.PAPER]
    zslots = [(0.70, 0.90), (1.00, 0.90), (1.30, 0.90),
              (0.70, 1.30), (1.30, 1.30), (0.85, 1.70), (1.15, 1.70)]
    for qi, (qy, qz) in enumerate(zslots):
        make_box(f"ZineRack_Zine_{qi}", (wall_face - 0.07, qy, qz),
                 (0.016, 0.15, 0.215), zine_tints[qi % len(zine_tints)])
    # STATIC TRUTHS Issue stack, front + center slot (photocopied
    # half-letter, single-fold — masthead Label3D scene-side)
    make_box("Zine_StaticTruths", (wall_face - 0.075, 1.0, 1.30), (0.020, 0.145, 0.215),
             P.PAPER)
    make_box("Zine_StaticTruths_Masthead", (wall_face - 0.088, 1.0, 1.375),
             (0.006, 0.115, 0.045), P.METAL_BLACK)
    make_box("Zine_StaticTruths_Cover", (wall_face - 0.088, 1.0, 1.27),
             (0.006, 0.09, 0.10), (0.55, 0.52, 0.48, 1.0))
    # ── Reading nook (mid-east) ──────────────────────────────────
    make_box("Nook_Rug", (3.15, 2.35, 0.008), (1.15, 1.15, 0.012), (0.40, 0.36, 0.30, 1.0))
    make_box("Armchair_Base", (3.38, 2.45, 0.22), (0.62, 0.62, 0.30), COL_UPHOLSTER)
    make_box("Armchair_Cushion", (3.33, 2.45, 0.42), (0.50, 0.52, 0.12), COL_UPHOLSTER)
    make_box("Armchair_Back", (3.62, 2.45, 0.62), (0.16, 0.62, 0.60), COL_UPHOLSTER)
    for ai2, sgn in enumerate((-1, +1)):
        make_box(f"Armchair_Arm_{ai2}", (3.38, 2.45 + sgn * 0.30, 0.50),
                 (0.58, 0.12, 0.26), COL_UPHOLSTER)
    for fi2, (fx, fy) in enumerate([(3.14, 2.22), (3.62, 2.22), (3.14, 2.68), (3.62, 2.68)]):
        make_cyl(f"Armchair_Foot_{fi2}", (fx, fy, 0.035), 0.022, 0.07, COL_WOOD_DARK)
    # A book left splayed on the chair arm (used-bookshop register)
    make_box("Armchair_Book", (3.38, 2.72, 0.585), (0.16, 0.11, 0.03), BOOK_TINTS[1])
    make_cyl("Nook_SideTable_Top", (2.90, 1.92, 0.55), 0.22, 0.04, COL_WOOD_DARK, segments=12)
    make_cyl("Nook_SideTable_Column", (2.90, 1.92, 0.27), 0.035, 0.52, COL_WOOD_DARK)
    make_cyl("Nook_SideTable_Base", (2.90, 1.92, 0.02), 0.13, 0.04, COL_WOOD_DARK, segments=12)
    _book_pile("Nook_TablePile", 2.90, 1.92, 0.57, 2, seed=21)
    make_cyl("Nook_Lamp_Base", (3.62, 2.95, 0.02), 0.13, 0.04, P.METAL_BLACK, segments=12)
    make_cyl("Nook_Lamp_Pole", (3.62, 2.95, 0.76), 0.013, 1.44, COL_BRASS)
    make_cyl("Nook_Lamp_Shade", (3.62, 2.95, 1.56), 0.13, 0.17, COL_CREAM, segments=12)
    make_cyl("Nook_Lamp_Glow", (3.62, 2.95, 1.47), 0.055, 0.03, (0.98, 0.88, 0.62, 1.0))
    # ── Petra's paintings (above the nook, _ART_MANIFEST) ────────
    # A: gray-green seascape — sky band, sea band, dark headland
    make_box("Painting_A_Frame", (wall_face + 0.015, 2.15, 1.80), (0.03, 0.70, 0.52),
             COL_WOOD_DARK)
    make_box("Painting_A_Canvas", (wall_face - 0.005, 2.15, 1.80), (0.02, 0.62, 0.44),
             (0.72, 0.72, 0.68, 1.0))
    make_box("Painting_A_Sea", (wall_face - 0.018, 2.15, 1.68), (0.006, 0.62, 0.20),
             (0.30, 0.40, 0.42, 1.0))
    make_box("Painting_A_Headland", (wall_face - 0.022, 2.38, 1.75), (0.006, 0.16, 0.10),
             (0.20, 0.22, 0.20, 1.0))
    # B: small harbor study — boat hull + mast on slate water
    make_box("Painting_B_Frame", (wall_face + 0.015, 2.95, 1.78), (0.03, 0.46, 0.38),
             COL_WOOD_DARK)
    make_box("Painting_B_Canvas", (wall_face - 0.005, 2.95, 1.78), (0.02, 0.38, 0.30),
             (0.36, 0.42, 0.46, 1.0))
    make_box("Painting_B_Hull", (wall_face - 0.018, 2.95, 1.72), (0.006, 0.18, 0.05),
             (0.55, 0.32, 0.22, 1.0))
    make_cyl("Painting_B_Mast", (wall_face - 0.018, 2.95, 1.82), 0.005, 0.14, COL_WOOD_DARK)
    # ── Framed tide chart by the counter (wiki: sells tide charts) ─
    make_box("TideChart_Frame", (wall_face + 0.015, 3.60, 1.70), (0.03, 0.42, 0.56),
             COL_WOOD)
    make_box("TideChart_Sheet", (wall_face - 0.005, 3.60, 1.70), (0.02, 0.36, 0.50), P.PAPER)
    for gi2 in range(4):
        make_box(f"TideChart_Row_{gi2}", (wall_face - 0.018, 3.60, 1.86 - gi2 * 0.11),
                 (0.004, 0.30, 0.020), (0.42, 0.52, 0.62, 1.0))
    for mi2 in range(3):
        make_cyl(f"TideChart_Moon_{mi2}", (wall_face - 0.018, 3.48 + mi2 * 0.12, 1.92),
                 0.014, 0.006, COL_SPRUCE, axis='X')
    # ── Radiator + the chair beside it (ch14_petra: the cat's wool
    # pillow lives on this chair when the kitchenette is in use) ──
    for fi3 in range(7):
        make_box(f"Radiator_Fin_{fi3}", (3.82, 4.56 + fi3 * 0.075, 0.36),
                 (0.16, 0.045, 0.56), COL_RADIATOR)
    make_box("Radiator_TopRail", (3.82, 4.79, 0.655), (0.17, 0.56, 0.03), COL_RADIATOR)
    for li3, ly in enumerate((4.60, 4.98)):
        make_cyl(f"Radiator_Foot_{li3}", (3.82, ly, 0.04), 0.025, 0.08, COL_CAST_IRON)
    make_cyl("Radiator_Pipe", (3.84, 5.06, 1.05), 0.022, 2.10, COL_RADIATOR)
    make_cyl("Radiator_Valve", (3.84, 5.06, 0.24), 0.040, 0.05, COL_BRASS)
    _chair("RadiatorChair", 3.50, 4.78, 'W', CHAIR_TINTS[1])
    make_cyl("RadiatorChair_Cushion", (3.50, 4.78, 0.50), 0.16, 0.05, COL_WOOL, segments=12)
    # Fire extinguisher between nook and radiator (retail code)
    make_fire_extinguisher("FireExt", (wall_face + 0.04, 3.98, 0.30))
    make_floor_plant("FloorPlant_SE", (3.55, 0.45, 0.0))


# ═════════════════════════════════════════════════════════════════
# NORTH ZONE — the office door (closed; the couch is behind it,
# ch14_petra), the coat hooks BY the office door (ch8_monday:
# Petra's wax canvas; ch8_aria: Tem hangs hers on the same hook),
# the desk outside the office door with Petra's clay mug (Margit's,
# 2009), the wall clock at SEVEN-TWENTY (when Petra came out,
# ch8_monday), THE COPIER (static_truths.md: Static Truths is run
# on this machine — a fresh half-letter run sits in the output
# tray), and the alley back door with boots + mat.
# ═════════════════════════════════════════════════════════════════
def build_north_zone():
    wall_y = ROOM_D
    # ── Office door (x −3.0..−2.1), closed solid leaf ────────────
    for sgn in (-1, +1):
        make_box(f"OfficeDoor_Post_{sgn:+d}", (-2.55 + sgn * 0.49, wall_y - 0.05, 1.10),
                 (0.08, 0.14, 2.20), COL_WOOD)
    make_box("OfficeDoor_Header", (-2.55, wall_y - 0.06, 2.26), (1.06, 0.10, 0.12), COL_WOOD)
    make_box("OfficeDoor_Leaf", (-2.55, wall_y + 0.02, 1.08), (0.86, 0.06, 2.12),
             COL_WOOD_DARK)
    for pi in range(2):
        make_box(f"OfficeDoor_Panel_{pi}", (-2.55, wall_y - 0.012, 0.70 + pi * 0.85),
                 (0.58, 0.008, 0.62), COL_WOOD)
    make_cyl("OfficeDoor_Knob", (-2.24, wall_y - 0.05, 1.02), 0.028, 0.05, COL_BRASS,
             axis='Y')
    make_door_hinges("OfficeDoor_Hinge", edge_x=-2.96, edge_y=wall_y - 0.02,
                     edge_z_centers=[0.35, 1.05, 1.80], axis='X')
    make_box("OfficeDoor_Sign", (-2.55, wall_y - 0.115, 1.62), (0.24, 0.012, 0.10),
             P.PAPER_AGED)
    # ── Coat hooks by the office door (west side) ────────────────
    make_box("CoatHooks_Rail", (-3.45, wall_y - 0.115, 1.70), (0.50, 0.03, 0.08), COL_WOOD)
    for hi, hx in enumerate((-3.62, -3.45, -3.28)):
        make_cyl(f"CoatHooks_Peg_{hi}", (hx, wall_y - 0.16, 1.68), 0.014, 0.10, COL_BRASS,
                 axis='Y')
    # Petra's wax canvas on the middle peg (the town uniform)
    make_box("PetraCoat_Body", (-3.45, wall_y - 0.22, 1.28), (0.34, 0.07, 0.76), COL_RAINCOAT)
    make_box("PetraCoat_Hood", (-3.45, wall_y - 0.22, 1.70), (0.22, 0.08, 0.12), COL_RAINCOAT)
    make_box("PetraCoat_Flap", (-3.45, wall_y - 0.262, 1.24), (0.10, 0.012, 0.60),
             (0.32, 0.30, 0.22, 1.0))
    # ── The desk outside the office door ─────────────────────────
    make_box("Desk_Top", (-1.2, 5.62, 0.76), (1.25, 0.55, 0.04), COL_WOOD)
    for li4, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"Desk_Leg_{li4}", (-1.2 + sx * 0.55, 5.62 + sy * 0.21, 0.37),
                 0.022, 0.74, COL_WOOD_DARK)
    make_box("Desk_Drawer", (-1.2, 5.42, 0.66), (1.10, 0.03, 0.12), COL_WOOD_DARK)
    make_cyl("Desk_DrawerKnob", (-1.2, 5.40, 0.66), 0.014, 0.02, COL_BRASS, axis='Y')
    # Petra's clay mug from Margit's, 2009 (ch8_monday — Lena sets
    # the coffee here when the office door is closed)
    _mug("MargitMug", -1.55, 5.60, 0.78, COL_CLAY)
    for si3 in range(3):
        make_box(f"Desk_Papers_{si3}", (-1.05, 5.62, 0.79 + si3 * 0.012),
                 (0.24, 0.32, 0.010), P.PAPER if si3 % 2 == 0 else P.PAPER_AGED)
    make_box("Desk_HoldSlips", (-0.78, 5.55, 0.795), (0.10, 0.14, 0.03), P.NEWSPRINT)
    make_cyl("Desk_Lamp_Base", (-1.68, 5.72, 0.79), 0.06, 0.02, COL_CAST_IRON, segments=12)
    make_cyl("Desk_Lamp_Pole", (-1.68, 5.72, 0.94), 0.010, 0.28, COL_BRASS)
    make_cyl("Desk_Lamp_Shade", (-1.63, 5.68, 1.09), 0.075, 0.06, (0.24, 0.40, 0.30, 1.0),
             segments=12)
    # Wall clock over the desk — 7:20, the minute Petra came out of
    # the office (ch8_monday)
    make_wall_clock("Clock", (-1.2, wall_y - 0.13, 2.30), frozen_hour=7, frozen_min=20)
    # ── THE COPIER — back-west corner (static_truths.md: "printed
    # on the Salty Tome's back-room copier"; first run $2, then
    # "the copier is the copier. I'm not in the way.") ────────────
    make_box("Copier_Body", (-3.50, 5.30, 0.50), (0.66, 0.58, 0.88), COL_XEROX)
    make_box("Copier_Top", (-3.50, 5.30, 0.955), (0.68, 0.60, 0.035), COL_XEROX_TOP)
    make_box("Copier_Lid", (-3.50, 5.34, 0.99), (0.60, 0.48, 0.035), COL_XEROX)
    make_box("Copier_LidHandle", (-3.50, 5.06, 0.995), (0.18, 0.03, 0.025), COL_XEROX_TOP)
    make_box("Copier_Panel", (-3.28, 5.02, 0.90), (0.20, 0.03, 0.10), COL_XEROX_PNL)
    for bi4 in range(4):
        make_cyl(f"Copier_Button_{bi4}", (-3.34 + bi4 * 0.045, 5.005, 0.90), 0.011, 0.012,
                 (0.66, 0.64, 0.60, 1.0) if bi4 else (0.30, 0.62, 0.34, 1.0), axis='Y')
    for di2 in range(2):
        make_box(f"Copier_Drawer_{di2}", (-3.50, 5.005, 0.30 + di2 * 0.20),
                 (0.56, 0.02, 0.14), (0.78, 0.78, 0.80, 1.0))
        make_box(f"Copier_DrawerHandle_{di2}", (-3.50, 4.99, 0.355 + di2 * 0.20),
                 (0.30, 0.012, 0.02), COL_XEROX_TOP)
    make_box("Copier_OutTray", (-3.06, 5.30, 0.72), (0.26, 0.34, 0.02), COL_XEROX_TOP)
    # Fresh Static Truths run in the tray — half-letter, single-fold
    for zi2 in range(4):
        make_box(f"Copier_Output_Sheet_{zi2}", (-3.06, 5.30, 0.735 + zi2 * 0.006),
                 (0.145, 0.215, 0.005), P.PAPER)
    make_box("Copier_Output_StaticTruths", (-3.06, 5.24, 0.762), (0.11, 0.05, 0.004),
             P.METAL_BLACK)
    make_box("Copier_ReamStack_0", (-3.78, 4.86, 0.03), (0.23, 0.30, 0.06), P.PAPER)
    make_box("Copier_ReamStack_1", (-3.78, 4.86, 0.09), (0.23, 0.30, 0.06), P.PAPER_AGED)
    make_box("Copier_Cord", (-3.72, 5.62, 0.015), (0.03, 0.45, 0.02), COL_CAST_IRON)
    # ── The alley back door (x −0.3..+0.6) — Lena's morning door ─
    for sgn in (-1, +1):
        make_box(f"BackDoor_Post_{sgn:+d}", (0.15 + sgn * 0.49, wall_y - 0.05, 1.10),
                 (0.08, 0.14, 2.20), COL_WOOD)
    make_box("BackDoor_Header", (0.15, wall_y - 0.06, 2.26), (1.06, 0.10, 0.12), COL_WOOD)
    make_box("BackDoor_Leaf", (0.15, wall_y + 0.02, 1.08), (0.86, 0.06, 2.12), COL_WOOD_DARK)
    for pi3 in range(2):
        make_box(f"BackDoor_Panel_{pi3}", (0.15, wall_y - 0.012, 0.70 + pi3 * 0.85),
                 (0.58, 0.008, 0.62), COL_WOOD)
    make_cyl("BackDoor_Knob", (0.46, wall_y - 0.05, 1.02), 0.028, 0.05, COL_BRASS, axis='Y')
    make_box("BackDoor_Deadbolt", (0.46, wall_y - 0.055, 1.18), (0.05, 0.02, 0.08), COL_BRASS)
    make_door_hinges("BackDoor_Hinge", edge_x=-0.26, edge_y=wall_y - 0.02,
                     edge_z_centers=[0.35, 1.05, 1.80], axis='X')
    make_box("BackDoor_Mat", (0.15, 5.55, 0.006), (0.90, 0.55, 0.010), P.RUBBER_MAT)
    for bi5, bx2 in enumerate((-0.52, -0.38)):
        make_cyl(f"Boot_{bi5}_Shaft", (bx2, 5.70, 0.14), 0.05, 0.24, COL_RAINCOAT)
        make_box(f"Boot_{bi5}_Foot", (bx2, 5.62, 0.035), (0.09, 0.22, 0.07),
                 (0.24, 0.22, 0.18, 1.0))


# ═════════════════════════════════════════════════════════════════
# NEW ARRIVALS — the table between the door and the counter
# (ch8_monday: Edgar "bought a book from the new-arrivals shelf
# without asking what it was"; Roy walks it picking books up and
# putting them down). Card lettering scene-side on NewArrivals_Card.
# ═════════════════════════════════════════════════════════════════
def build_new_arrivals():
    make_box("NewArrivals_Top", (1.55, 1.85, 0.76), (1.15, 0.68, 0.05), COL_WOOD_LT)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"NewArrivals_Leg_{li}", (1.55 + sx * 0.50, 1.85 + sy * 0.27, 0.37),
                 0.022, 0.74, COL_WOOD_DARK)
    make_box("NewArrivals_Shelf", (1.55, 1.85, 0.30), (1.00, 0.55, 0.03), COL_WOOD_DARK)
    _book_pile("NewArrivals_PileA", 1.20, 1.70, 0.785, 4, seed=3)
    _book_pile("NewArrivals_PileB", 1.55, 2.02, 0.785, 3, seed=11)
    _book_pile("NewArrivals_PileC", 1.90, 1.72, 0.785, 5, seed=17)
    for fi, (fx, fy) in enumerate([(1.32, 2.02), (1.80, 2.05)]):
        make_box(f"NewArrivals_FaceUp_{fi}", (fx, fy, 0.795), (0.155, 0.215, 0.020),
                 BOOK_TINTS[(fi * 3 + 2) % len(BOOK_TINTS)])
    _book_pile("NewArrivals_Under", 1.45, 1.85, 0.315, 3, seed=23)
    make_box("NewArrivals_CardStand", (2.02, 1.95, 0.815), (0.06, 0.04, 0.06), COL_WOOD_DARK)
    make_box("NewArrivals_Card", (2.02, 1.95, 0.90), (0.16, 0.012, 0.11), P.PAPER)


# ═════════════════════════════════════════════════════════════════
# KITCHENETTE (NE, ch8_monday + ch14_petra) — counter with Petra's
# kettle + the pour-over cone (the dark French Soren roasts; the
# cone fight is Petra's pleasure), the small sandwich fridge, the
# four mugs on the shelf (Petra set out four, ch14), the sink, the
# back window with the alley beyond, and the table the four of
# them sit at.
# ═════════════════════════════════════════════════════════════════
def build_kitchenette():
    # Window frame (opening x 2.0..3.4, z 1.05..2.25) — rain-side
    make_box("KitchWin_Sill", (2.7, ROOM_D, 1.035), (1.52, 0.22, 0.07), COL_WOOD)
    make_box("KitchWin_Head", (2.7, ROOM_D, 2.265), (1.52, 0.22, 0.07), COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"KitchWin_Jamb_{sgn:+d}", (2.7 + sgn * 0.73, ROOM_D, 1.65),
                 (0.06, 0.22, 1.30), COL_WOOD)
    make_box("KitchWin_MullV", (2.7, ROOM_D, 1.65), (0.05, 0.14, 1.22), COL_WOOD)
    make_box("KitchWin_MullH", (2.7, ROOM_D, 1.65), (1.40, 0.14, 0.05), COL_WOOD)
    # Counter run along the north wall x 0.95..3.05
    make_box("Kitch_Cabinet", (2.0, 5.70, 0.44), (2.10, 0.52, 0.88), COL_WOOD)
    make_box("Kitch_Top", (2.0, 5.70, 0.90), (2.20, 0.58, 0.04), COL_BUTCHER)
    make_box("Kitch_Kick", (2.0, 5.43, 0.08), (2.10, 0.02, 0.16), COL_WOOD_DARK)
    for di3, dx2 in enumerate((1.45, 2.55)):
        make_box(f"Kitch_CabDoor_{di3}", (dx2, 5.435, 0.48), (0.72, 0.015, 0.66), COL_WOOD_LT)
        make_cyl(f"Kitch_CabKnob_{di3}", (dx2 + 0.28, 5.42, 0.60), 0.014, 0.02, COL_BRASS,
                 axis='Y')
    # Kettle (Petra's, ch8_monday)
    make_cyl("Kettle_Body", (1.30, 5.70, 0.995), 0.080, 0.15, COL_STEEL, segments=12)
    make_cyl("Kettle_Lid", (1.30, 5.70, 1.08), 0.055, 0.02, COL_STEEL)
    make_cyl("Kettle_Knob", (1.30, 5.70, 1.10), 0.014, 0.02, COL_WOOD_DARK)
    make_box("Kettle_Spout", (1.39, 5.70, 0.975), (0.07, 0.018, 0.018), COL_STEEL)
    make_box("Kettle_Handle", (1.21, 5.70, 1.085), (0.03, 0.02, 0.09), COL_WOOD_DARK)
    # THE CONE + carafe (the coffee is made the way Petra wants it
    # made, and she still complains — ch8_monday)
    make_box("PourOver_Base", (1.78, 5.68, 0.925), (0.30, 0.22, 0.03), COL_WOOD)
    for ui, ux in enumerate((1.66, 1.90)):
        make_box(f"PourOver_Upright_{ui}", (ux, 5.68, 1.06), (0.03, 0.03, 0.24), COL_WOOD)
    make_box("PourOver_TopRail", (1.78, 5.68, 1.195), (0.30, 0.10, 0.03), COL_WOOD)
    make_cyl("PourOver_Cone_Upper", (1.78, 5.68, 1.245), 0.062, 0.06, COL_CREAM)
    make_cyl("PourOver_Cone_Lower", (1.78, 5.68, 1.21), 0.038, 0.03, COL_CREAM)
    make_cyl("PourOver_Carafe", (1.78, 5.68, 0.99), 0.052, 0.11, (0.62, 0.42, 0.22, 1.0))
    # Soren's dark French, in a labeled tin
    make_cyl("CoffeeTin", (2.10, 5.74, 1.00), 0.045, 0.13, (0.22, 0.13, 0.08, 1.0))
    make_box("CoffeeTin_Label", (2.055, 5.74, 1.00), (0.006, 0.06, 0.07), P.PAPER_AGED)
    # Sink under the window + gooseneck faucet
    make_box("Kitch_Sink_Basin", (2.70, 5.72, 0.865), (0.38, 0.32, 0.09), COL_STEEL,
             open_faces={'+Z'})
    make_box("Kitch_Sink_Floor", (2.70, 5.72, 0.828), (0.36, 0.30, 0.01),
             (0.42, 0.44, 0.46, 1.0))
    make_cyl("Kitch_Faucet_Riser", (2.70, 5.86, 1.02), 0.013, 0.22, COL_STEEL)
    make_cyl("Kitch_Faucet_Spout", (2.70, 5.78, 1.12), 0.011, 0.18, COL_STEEL, axis='Y')
    # Dish rack with the second cup (Lena's own, ch8_monday)
    make_box("Kitch_DishRack", (3.00, 5.70, 0.925), (0.26, 0.30, 0.03), COL_WOOD_DARK)
    _mug("Kitch_SecondCup", 3.00, 5.70, 0.94, CHAIR_TINTS[1])
    # The small sandwich fridge ("There is a sandwich in the small
    # fridge if you do not eat. Eat it." — ch8_monday)
    make_box("Kitch_Fridge", (3.50, 5.66, 0.42), (0.56, 0.56, 0.84), COL_CREAM)
    make_box("Kitch_Fridge_Door", (3.50, 5.365, 0.42), (0.52, 0.02, 0.78), (0.84, 0.82, 0.76, 1.0))
    make_box("Kitch_Fridge_Handle", (3.28, 5.35, 0.52), (0.03, 0.015, 0.26), COL_STEEL)
    make_box("Kitch_Fridge_Note", (3.55, 5.352, 0.60), (0.10, 0.006, 0.08), P.PAPER)
    # Mug shelf west of the window — the FOUR mugs Petra set out
    # (ch14_petra)
    make_box("Kitch_MugShelf", (1.30, 5.81, 1.60), (0.80, 0.18, 0.03), COL_WOOD)
    for ki2, sgn in enumerate((-1, +1)):
        make_box(f"Kitch_MugShelf_Bracket_{ki2}", (1.30 + sgn * 0.34, 5.855, 1.54),
                 (0.03, 0.09, 0.10), P.METAL_BLACK)
    for mi3 in range(4):
        _mug(f"Kitch_ShelfMug_{mi3}", 1.02 + mi3 * 0.19, 5.81, 1.615,
             [COL_CREAM, COL_CLAY, CHAIR_TINTS[1], (0.62, 0.34, 0.22, 1.0)][mi3])
    # ── The kitchenette table (ch14: Lena, Cale across, Petra at
    # the end; Kai stood by the door — three chairs + the radiator
    # chair make the four seats) ─────────────────────────────────
    make_box("KitchTable_Top", (2.85, 4.62, 0.74), (0.85, 0.85, 0.04), COL_WOOD_LT)
    for li5, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"KitchTable_Leg_{li5}", (2.85 + sx * 0.36, 4.62 + sy * 0.36, 0.36),
                 0.022, 0.72, COL_WOOD_DARK)
    _chair("KitchChair_S", 2.85, 4.02, 'N', CHAIR_TINTS[0])
    _chair("KitchChair_W", 2.24, 4.62, 'E', CHAIR_TINTS[2])
    _chair("KitchChair_N", 2.85, 5.20, 'S', CHAIR_TINTS[3])
    # Two of the four cups on the table (the hour of sitting, ch14)
    _mug("KitchTable_Cup_A", 2.68, 4.50, 0.76, COL_CLAY)
    _mug("KitchTable_Cup_B", 3.02, 4.74, 0.76, COL_CREAM)


# ═════════════════════════════════════════════════════════════════
# CEILING — warm pendants (bookshop, not fluorescent-tube retail:
# the scaffold's tube fixtures were the wrong vocabulary, per the
# Cosmic Comics scaffold lesson), green library shades over the
# counter, smoke detector, one HVAC vent.
# ═════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    _pendant("Pendant_Aisle", 0.0, 2.7)
    _pendant("Pendant_Kids", -2.85, 1.25)
    _pendant("Pendant_Nook", 3.15, 2.40)
    _pendant("Pendant_Kitch", 2.85, 4.70)
    _pendant("Pendant_Counter_W", 0.35, 3.85, drop=0.70, shade=(0.24, 0.40, 0.30, 1.0))
    _pendant("Pendant_Counter_E", 1.65, 3.85, drop=0.70, shade=(0.24, 0.40, 0.30, 1.0))
    make_smoke_detector("Smoke", (-0.6, 3.4, CEIL))
    make_hvac_vent("HVAC", (0.9, 5.0, CEIL), width=0.80, depth=0.40)


def main():
    clear_scene()
    build_shell()
    build_storefront()
    build_exterior_street()
    build_exterior_alley()
    build_counter()
    build_stacks()
    build_west_wall()
    build_east_wall()
    build_north_zone()
    build_new_arrivals()
    build_kitchenette()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/salty_tome_interior.glb"))
    print(f"\n[build_salty_tome_interior] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
