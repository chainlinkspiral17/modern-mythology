"""CHILLWAVE VIDEO — Cale's slow-stick shop, Main St, Smolvud OR —
vol7 hero locale.

WHAT THE PLACE IS (per the binding scenes — grep "3d:chillwave_interior"
→ vol7_ch3_studio, vol7_ch6_cale, vol7_ch6_chillwave; the other nine
ch6 scenes continue in the back room without re-binding): Cale's
record/video shop that actually deals in SLOW STICKS — designer-made
memory media sold in waxed-paper foundation sleeves and disc-cases.
Front retail floor + the back room where the inventory lives. The
back room hosts the whole ch6 spine (music catalog id
vol7_chillwave_back_room covers all eleven ch6 scenes), so it is a
real modeled room behind the north doorway, not a recess glimpse.

Canon sources baked in:
  · vol7_ch3_studio: "ChillWave Video at four-twelve was quiet";
    the bell rings as she comes in; "Cale was at the counter with a
    paperback"; the store smell — "wax-paper sleeves, the cedar
    shelves Cale had built himself in 2046"; Estuary 7 "is not on
    the floor... It's in the back" (so the floor stock exists AND
    the hero stick is NOT out front).
  · vol7_ch6_cale / vol7_ch6_chillwave: "walked around the counter
    and through the doorway to the back" (counter guards the back
    doorway); "The back was where the inventory lived. Cedar
    shelves alphabetized by designer, a wooden crate by the door
    for new arrivals, a workbench in the corner with a soldering
    iron and the small precision tools Cale used on the older
    readers"; "He unplugged the soldering iron from the strip on
    the wall, moved a few small parts off the bench into a tray,
    pulled a second chair over from the corner"; "The transformer
    on the wall hummed faintly even with the iron unplugged";
    "Bench behind you, third slot in the wooden box" — three sticks,
    the third Estuary 7, Ines Rocha 2046 on a white label; she
    exits through the front, "the bell rang twice".
  · vol7_ch6_why_lena: Lena's chair is "a folding metal one Cale
    had probably grabbed out of the closet" — so a folding metal
    chair near the bench AND a closet door in the back room.
  · vol7_ch21_leaving: "the case Cale had put on the inventory
    shelf behind his register on the seventeenth of August" — ch3 &
    ch6 both post-date that, so Estuary 7's empty disc-case sits on
    the shelf behind the register while the stick itself waits in
    the wooden box in the back.
  · vol7_ch13_cale: "his afternoon cigarette at two-forty-five on
    the back porch at ChillWave" → back door + small porch off the
    back room (coffee-can butt tin outside; NO smoking props
    inside). Also the CLOSED sign / register-paper note is a ch13
    one-off — not baked, shop reads open.
  · vol7_ch12_morning: "Cale's truck was outside ChillWave Video"
    (his F-150, ch16_eight) → slab-tier pickup at the Main St curb.
  · milk_and_honey/_ART_MANIFEST.md: "Counter at front, register,
    the bell. Lights low. Inventory crates by the door." Lights-low
    → warm pendants, no fluorescent banks (scene lights are tscn-
    side). The manifest's crate placement is conflated; the binding
    prose puts the new-arrivals crate by the BACK-room door, which
    wins (playbook wave-8 rule).

Canon-negatives honored: no café table (scaffold's removed), no
customers' seating, no ashtray/tobacco inside (back porch only), no
apartment storey above (Cale lives over the laundromat — ch13), the
Estuary 7 stick itself never on the floor, no in-world neon — the
"chillwave" look is the screen-space mood, not baked geometry.

No transparency: storefront windows are OPENINGS with cedar frames
+ mullions; the door is stiles + rails with an empty upper panel.
Text is scene-side Label3D per the playbook; this script bakes named
vertex-colored panels only: ChillWave_SignPanel/_SignLetters,
FlipSign_Board, HoursCard, *_Tab_* (alphabet-by-designer dividers),
Island*_Card, InvShelf_Estuary7_Label, StickBox_Estuary7_Label.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import (make_floor, make_wall, make_ceiling,
                              make_crown_molding, make_door_hinges)
from _props.store_fixtures import make_register
from _props.decor import make_fire_extinguisher
from _props.safety import make_smoke_detector, make_hvac_vent

# ── Shell (footprint kept from the scaffold — the .tscn camera at
#    Godot (0, 2.30, +0.5) looks north from the front door across
#    this 7 × 6 front room; door gap x −1..+1) ────────────────────
ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 2.8
PAL_WALL = {"wall": (0.42, 0.32, 0.46, 1.0),      # plum (Main St house style,
            "baseboard": (0.18, 0.12, 0.20, 1.0)}  #  kept from the scaffold)

# Back room (the inventory room, ch6) — x −3.5..+1.5 behind the
# north wall; the side yard x 1.6..3.5 is the gravel strip + porch.
BACK_Y0 = 6.0            # shared wall centerline
BACK_Y1 = 9.2            # back-room north wall centerline
BACK_XE = 1.5            # back-room east wall centerline

# ── ChillWave palette (cedar shop Cale built in 2046, PNW muted) ─
COL_FIR_FLOOR = (0.52, 0.40, 0.28, 1.0)   # worn fir planks
COL_FIR_SEAM  = (0.35, 0.26, 0.18, 1.0)
COL_FIR_WORN  = (0.61, 0.49, 0.34, 1.0)   # traffic lane, finish walked off
COL_CEDAR     = (0.58, 0.38, 0.28, 1.0)   # the 2046 cedar shelving
COL_CEDAR_LT  = (0.68, 0.48, 0.35, 1.0)
COL_CEDAR_DK  = (0.38, 0.24, 0.18, 1.0)
COL_BRASS     = (0.70, 0.57, 0.30, 1.0)
COL_CREAM     = (0.90, 0.87, 0.80, 1.0)
COL_BRAND     = (0.30, 0.46, 0.56, 1.0)   # ChillWave sign teal-blue
COL_STEEL     = P.METAL_STEEL
COL_STEEL_WORN= (0.52, 0.52, 0.54, 1.0)
COL_CAST_IRON = (0.13, 0.13, 0.14, 1.0)
COL_KRAFT     = (0.74, 0.56, 0.34, 1.0)
COL_CONCRETE  = (0.55, 0.54, 0.51, 1.0)
COL_ASPHALT   = (0.30, 0.29, 0.30, 1.0)
COL_PUDDLE    = (0.30, 0.33, 0.36, 1.0)
COL_GRAVEL    = (0.48, 0.45, 0.40, 1.0)
COL_TRUCK     = (0.28, 0.36, 0.30, 1.0)   # Cale's F-150, faded forest
COL_TRUCK_DK  = (0.20, 0.26, 0.22, 1.0)
COL_GLASS_DK  = (0.12, 0.13, 0.15, 1.0)   # dark opaque "glass" (distant)
COL_LAMPGREEN = (0.24, 0.40, 0.30, 1.0)
COL_GLOW_WARM = (0.98, 0.88, 0.62, 1.0)

# Waxed-paper foundation sleeves — "the wax yellowed at the edges"
# (vol7_ch16_eight; the foundation has packaged sticks in these
# since the '30s)
SLEEVE_TINTS = [P.PAPER_AGED, (0.90, 0.86, 0.74, 1.0),
                (0.84, 0.76, 0.60, 1.0), (0.92, 0.90, 0.80, 1.0),
                (0.80, 0.72, 0.55, 1.0)]
# Disc-cases (the case Estuary 7 was sold to Tem in) — muted plastic
CASE_TINTS = [(0.16, 0.15, 0.17, 1.0), (0.30, 0.38, 0.46, 1.0),
              (0.44, 0.22, 0.19, 1.0), (0.26, 0.36, 0.28, 1.0),
              (0.72, 0.54, 0.26, 1.0), (0.82, 0.78, 0.68, 1.0)]

COUNTER_TOP = 0.985       # counter top surface z


# ═════════════════════════════════════════════════════════════════
# Local helpers (deterministic — index-cycled variation, no random)
# ═════════════════════════════════════════════════════════════════
_SLEEVE_W = (0.016, 0.015, 0.018, 0.014, 0.017, 0.015, 0.019, 0.016)

def _media_row(prefix, a0, a1, cross, shelf_z, seed=0, axis='X'):
    """A filed run of slow-stick media along `axis` from a0..a1 at
    perpendicular coordinate `cross`, standing on shelf_z. Mixes
    waxed-paper sleeves, disc-cases, pulled gaps, flat piles, and
    proud cream alphabet tabs ("alphabetized by designer" — tab
    lettering is scene-side Label3D on the *_Tab_* panels)."""
    def _put(name, run_c, w, depth, h, tint, z_lift=0.0):
        z = shelf_z + z_lift + h / 2.0
        if axis == 'X':
            make_box(name, (run_c, cross, z), (w, depth, h), tint)
        else:
            make_box(name, (cross, run_c, z), (depth, w, h), tint)
    cursor = a0 + 0.02
    i = 0
    while cursor < a1 - 0.05:
        k = seed + i
        if k % 12 == 7:                       # pulled-media gap
            cursor += 0.050
            i += 1
            continue
        if k % 17 == 13:                      # flat overstock pile
            for pi in range(2):
                _put(f"{prefix}_Flat_{i}_{pi}", cursor + 0.072,
                     0.140, 0.130, 0.016,
                     SLEEVE_TINTS[(k + pi * 2) % len(SLEEVE_TINTS)],
                     z_lift=pi * 0.017)
            cursor += 0.155
            i += 1
            continue
        if k % 9 == 5:                        # designer alphabet tab
            _put(f"{prefix}_Tab_{i}", cursor + 0.006,
                 0.012, 0.150, 0.225, COL_CREAM)
            cursor += 0.020
            i += 1
            continue
        if k % 5 == 4:                        # disc-case, spine out
            _put(f"{prefix}_Case_{i}", cursor + 0.013,
                 0.026, 0.125, 0.155, CASE_TINTS[(k * 3 + 1) % len(CASE_TINTS)])
            cursor += 0.030
            i += 1
            continue
        w = _SLEEVE_W[k % len(_SLEEVE_W)]     # sleeved stick on edge
        _put(f"{prefix}_Slv_{i}", cursor + w / 2.0,
             w, 0.135, 0.185 + (k % 3) * 0.006,
             SLEEVE_TINTS[(k * 2 + 3) % len(SLEEVE_TINTS)])
        cursor += w + (0.003 if k % 4 else 0.010)
        i += 1

def _case_pile(prefix, cx, cy, bz, count, seed=0):
    """A small flat pile of disc-cases / sleeves."""
    for pi in range(count):
        k = seed + pi
        tint = CASE_TINTS[(k * 2 + 1) % len(CASE_TINTS)] if k % 2 \
            else SLEEVE_TINTS[(k * 3 + 2) % len(SLEEVE_TINTS)]
        make_box(f"{prefix}_{pi}",
                 (cx + (k % 3 - 1) * 0.008, cy + (k % 2) * 0.007,
                  bz + 0.011 + pi * 0.023),
                 (0.125 - (k % 2) * 0.008, 0.140 - (k % 3) * 0.010, 0.021),
                 tint)

def _wood_chair(prefix, cx, cy, facing, tint):
    """Plain wood chair; `facing` = direction the sitter faces."""
    dx, dy = {'N': (0, 1), 'S': (0, -1), 'E': (1, 0), 'W': (-1, 0)}[facing]
    make_box(f"{prefix}_Seat", (cx, cy, 0.45), (0.40, 0.40, 0.04), tint)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"{prefix}_Leg_{li}", (cx + sx * 0.16, cy + sy * 0.16, 0.225),
                 0.018, 0.45, COL_CEDAR_DK)
    bx, by = cx - dx * 0.19, cy - dy * 0.19
    for pi, sgn in enumerate((-1, +1)):
        px = bx + (sgn * 0.16 if dx == 0 else 0.0)
        py = by + (sgn * 0.16 if dy == 0 else 0.0)
        make_cyl(f"{prefix}_BackPost_{pi}", (px, py, 0.675), 0.016, 0.45, tint)
    slat_sz = (0.36, 0.03, 0.09) if dx == 0 else (0.03, 0.36, 0.09)
    for si, sz_z in enumerate((0.72, 0.86)):
        make_box(f"{prefix}_Slat_{si}", (bx, by, sz_z), slat_sz, tint)

def _pendant(prefix, cx, cy, drop=0.62, shade=COL_CREAM):
    """Cylinder-shade pendant — round geometry at eye level; warm
    'lights low' vocabulary (no fluorescent banks in this shop)."""
    make_cyl(f"{prefix}_Canopy", (cx, cy, CEIL - 0.02), 0.05, 0.04, P.METAL_BLACK)
    make_cyl(f"{prefix}_Cord", (cx, cy, CEIL - drop / 2.0), 0.008, drop, P.METAL_BLACK)
    make_cyl(f"{prefix}_Shade", (cx, cy, CEIL - drop - 0.065), 0.15, 0.13, shade,
             segments=12)
    make_cyl(f"{prefix}_Bulb", (cx, cy, CEIL - drop - 0.135), 0.05, 0.04, COL_GLOW_WARM)

def _bare_bulb(prefix, cx, cy):
    """Back-room bare bulb on a cord, with pull chain."""
    make_cyl(f"{prefix}_Canopy", (cx, cy, CEIL - 0.015), 0.05, 0.03, P.METAL_BLACK)
    make_cyl(f"{prefix}_Cord", (cx, cy, CEIL - 0.14), 0.007, 0.22, COL_CAST_IRON)
    make_cyl(f"{prefix}_Bulb", (cx, cy, CEIL - 0.29), 0.032, 0.08, COL_GLOW_WARM)
    make_cyl(f"{prefix}_PullChain", (cx + 0.05, cy, CEIL - 0.20), 0.003, 0.14,
             COL_STEEL_WORN)


# ═════════════════════════════════════════════════════════════════
# SHELL — front room keeps the scaffold's 7 × 6 footprint; the south
# wall becomes a real storefront (openings + piers, diner-window
# rule), the north wall splits around the doorway to the back
# (x −0.55..+0.35 — she comes in at x 0, walks north past the
# counter's west end, through this doorway: ch6). The back room is
# a full second volume, y 6.1..9.1 × x −3.5..+1.5.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    # Floors — worn fir planks (the building predates Cale's 2046
    # cedar refit; the shelving is cedar, the floor is older)
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_FIR_FLOOR, "seam": COL_FIR_SEAM})
    make_floor("BackFloor", (-1.0, 7.6, 0.0), size_x=5.4, size_y=3.4,
               palette={"vinyl": COL_FIR_FLOOR, "seam": COL_FIR_SEAM})
    # Wear lane — door → counter → back doorway (finish walked off)
    make_box("Floor_WearLane", (-0.10, 3.0, 0.006), (0.75, 5.6, 0.004), COL_FIR_WORN)
    make_box("Floor_WearSpur", (0.75, 3.65, 0.007), (1.40, 0.62, 0.004), COL_FIR_WORN)
    # Side walls, front room
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    # North (shared) wall — doorway gap x −0.55..+0.35
    make_wall("Wall_N_W", (-2.125, BACK_Y0, 0), length=3.15, height=CEIL,
              axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (+2.025, BACK_Y0, 0), length=3.35, height=CEIL,
              axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_N_AboveDoorway", (-0.10, BACK_Y0, 2.52), (0.90, 0.20, 0.56),
             PAL_WALL["wall"])
    # South storefront — piers + sills + headers; window openings
    # x −3.0..−1.3 and +1.3..+3.0 (sill 0.75, head 2.30), door −1..+1
    for nm, px, pw in [("Wall_S_PierSW", -3.35, 0.70), ("Wall_S_PierWD", -1.15, 0.30),
                       ("Wall_S_PierED", +1.15, 0.30), ("Wall_S_PierSE", +3.35, 0.70)]:
        make_box(nm, (px, 0.0, CEIL / 2.0), (pw, 0.20, CEIL), PAL_WALL["wall"])
    for tag, wx in [("W", -2.15), ("E", +2.15)]:
        make_box(f"Wall_S_{tag}_Sill", (wx, 0.0, 0.375), (1.70, 0.20, 0.75),
                 PAL_WALL["wall"])
        make_box(f"Wall_S_{tag}_SillBase", (wx, 0.06, 0.08), (1.70, 0.06, 0.16),
                 PAL_WALL["baseboard"])
        make_box(f"Wall_S_{tag}_Header", (wx, 0.0, 2.55), (1.70, 0.20, 0.50),
                 PAL_WALL["wall"])
    make_box("Wall_S_AboveDoor", (0.0, 0.0, 2.52), (2.0, 0.20, 0.56), PAL_WALL["wall"])
    # Back-room walls
    make_wall("Wall_Back_W", (-ROOM_W / 2.0, 7.65, 0), length=3.3, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_Back_E", (BACK_XE, 7.65, 0), length=3.3, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_Back_N", (-1.0, BACK_Y1, 0), length=5.4, height=CEIL,
              axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    # Ceilings — painted plank (pre-war Main St building), mauve-gray
    ceil_pal = {"tile": (0.70, 0.64, 0.70, 1.0), "grid": (0.36, 0.28, 0.38, 1.0)}
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, palette=ceil_pal, with_stains=False)
    make_ceiling("BackCeil", (-1.0, 7.6, CEIL), size_x=5.4, size_y=3.4,
                 palette=ceil_pal, with_stains=False)
    # Crown molding, front room only (retail face; the back is bare)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W / 2.0 + 0.10, ROOM_D / 2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W / 2.0 - 0.10, ROOM_D / 2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D - 0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_CEDAR})
    # Doorway trim to the back — "she paused with her hand on the
    # frame" (ch6_cale): a real cedar frame, no leaf (open doorway)
    for sgn, px in [(-1, -0.59), (+1, +0.39)]:
        make_box(f"BackDoorway_Post_{sgn:+d}", (px, BACK_Y0, 1.10),
                 (0.08, 0.26, 2.20), COL_CEDAR)
    make_box("BackDoorway_Header", (-0.10, BACK_Y0, 2.26), (1.06, 0.26, 0.12),
             COL_CEDAR)


# ═════════════════════════════════════════════════════════════════
# STOREFRONT — cedar frames + mullions in the two openings (no
# glass), the front door (stiles + rails, EMPTY upper panel — no
# transparency), THE BELL over it (ch3: "The bell rang as she came
# in"; ch6: "The bell rang twice" on her way out), the OPEN/CLOSED
# flip sign in the east sidelite, entry mat (rain-town register).
# ═════════════════════════════════════════════════════════════════
def _window_frame_south(tag, wx):
    """Frame + mullions for a south opening centered at wx.
    Opening 1.7 wide, z 0.75..2.30, transom bar at 1.95."""
    make_box(f"WinS_{tag}_Sill", (wx, 0.0, 0.735), (1.82, 0.22, 0.07), COL_CEDAR)
    make_box(f"WinS_{tag}_Ledge", (wx, 0.14, 0.775), (1.70, 0.14, 0.03), COL_CEDAR_LT)
    make_box(f"WinS_{tag}_Head", (wx, 0.0, 2.315), (1.82, 0.22, 0.07), COL_CEDAR)
    for sgn in (-1, +1):
        make_box(f"WinS_{tag}_Jamb_{sgn:+d}", (wx + sgn * 0.88, 0.0, 1.525),
                 (0.06, 0.22, 1.65), COL_CEDAR)
    for mi, mx in enumerate((-0.55, +0.55)):
        make_box(f"WinS_{tag}_MullV_{mi}", (wx + mx, 0.0, 1.525),
                 (0.05, 0.14, 1.55), COL_CEDAR)
    make_box(f"WinS_{tag}_Transom", (wx, 0.0, 1.95), (1.70, 0.14, 0.05), COL_CEDAR)

def build_storefront():
    _window_frame_south("W", -2.15)
    _window_frame_south("E", +2.15)
    # Door surround — leaf west (x −0.95..−0.05), sidelite east
    for sgn in (-1, +1):
        make_box(f"Door_Post_{sgn:+d}", (sgn * 0.96, 0.0, 1.10), (0.08, 0.16, 2.20),
                 COL_CEDAR)
    make_box("Door_MidPost", (0.0, 0.0, 1.10), (0.08, 0.16, 2.20), COL_CEDAR)
    make_box("Door_Transom", (0.0, 0.0, 2.24), (2.00, 0.16, 0.08), COL_CEDAR)
    # Door leaf — stiles + rails, lower panel solid, upper OPEN
    for si, sx in enumerate((-0.90, -0.10)):
        make_box(f"Door_Stile_{si}", (sx, 0.02, 1.08), (0.09, 0.05, 2.10), COL_CEDAR_DK)
    make_box("Door_Rail_Bottom", (-0.50, 0.02, 0.14), (0.71, 0.05, 0.22), COL_CEDAR_DK)
    make_box("Door_Rail_Lock", (-0.50, 0.02, 1.02), (0.71, 0.05, 0.14), COL_CEDAR_DK)
    make_box("Door_Rail_Top", (-0.50, 0.02, 2.09), (0.71, 0.05, 0.08), COL_CEDAR_DK)
    make_box("Door_LowerPanel", (-0.50, 0.02, 0.60), (0.71, 0.03, 0.70), COL_CEDAR)
    make_cyl("Door_Knob", (-0.14, -0.06, 1.02), 0.028, 0.05, COL_BRASS, axis='Y')
    make_box("Door_Deadbolt", (-0.14, -0.045, 1.18), (0.05, 0.02, 0.08), COL_BRASS)
    make_box("Door_KickPlate", (-0.50, -0.005, 0.15), (0.71, 0.02, 0.24), COL_BRASS)
    make_door_hinges("Door_Hinge", edge_x=-0.92, edge_y=0.0,
                     edge_z_centers=[0.35, 1.05, 1.80], axis='X')
    # THE BELL over the door (brass, bracket-mounted; it rings)
    make_box("DoorBell_Mount", (-0.50, 0.13, 2.32), (0.06, 0.10, 0.06), P.METAL_BLACK)
    make_cyl("DoorBell_Arm", (-0.50, 0.24, 2.32), 0.012, 0.16, COL_BRASS, axis='Y')
    make_cyl("DoorBell_Body", (-0.50, 0.32, 2.27), 0.050, 0.07, COL_BRASS)
    make_cyl("DoorBell_Flare", (-0.50, 0.32, 2.22), 0.068, 0.025, COL_BRASS)
    make_cyl("DoorBell_Clapper", (-0.50, 0.32, 2.18), 0.012, 0.05, P.METAL_BLACK)
    # OPEN/CLOSED flip sign on a cord in the east sidelite (ch12:
    # "the OPEN sign was on the door"; lettering scene-side)
    make_cyl("FlipSign_Cord", (0.48, 0.05, 1.98), 0.004, 0.28, P.TWINE)
    make_box("FlipSign_Board", (0.48, 0.05, 1.74), (0.36, 0.02, 0.20), COL_CREAM)
    make_box("FlipSign_Text_In", (0.48, 0.063, 1.74), (0.28, 0.006, 0.09), COL_BRAND)
    make_box("FlipSign_Text_Out", (0.48, 0.037, 1.74), (0.28, 0.006, 0.09), COL_BRAND)
    make_box("HoursCard", (1.15, 0.105, 1.50), (0.16, 0.010, 0.22), P.PAPER)
    # Entry mat — it is always raining in Smolvud
    make_box("EntryMat_Under", (-0.30, 0.75, 0.009), (1.60, 0.95, 0.006),
             (0.14, 0.13, 0.13, 1.0))
    make_box("EntryMat", (-0.30, 0.75, 0.016), (1.46, 0.82, 0.008), P.RUBBER_MAT)


# ═════════════════════════════════════════════════════════════════
# EXTERIOR · MAIN STREET (south) — sidewalk, curb, wet road, the
# far sidewalk, a streetlamp on the buffer strip (public right-of-
# way rule), rain puddles, Cale's F-150 at the curb (ch12/ch16),
# and the shop facade: single-storey parapet (Cale does NOT live
# above the shop — his apartment is over the laundromat, ch13) with
# the CHILLWAVE VIDEO sign panel (lettering scene-side).
# ═════════════════════════════════════════════════════════════════
def build_exterior_main_street():
    make_box("Ext_Sidewalk", (0.0, -1.35, -0.06), (8.6, 2.50, 0.12), COL_CONCRETE)
    for si in range(3):
        make_box(f"Ext_Sidewalk_Seam_{si}", (-2.6 + si * 2.6, -1.35, 0.001),
                 (0.03, 2.40, 0.002), (0.42, 0.40, 0.37, 1.0))
    make_box("Ext_Curb", (0.0, -2.66, -0.04), (8.6, 0.16, 0.12),
             (0.46, 0.45, 0.43, 1.0))
    make_box("Ext_Road", (0.0, -4.80, -0.10), (8.6, 4.10, 0.08), COL_ASPHALT)
    for di in range(3):
        make_box(f"Ext_Road_Dash_{di}", (-2.9 + di * 2.9, -4.85, -0.058),
                 (1.30, 0.12, 0.004), (0.82, 0.72, 0.36, 1.0))
    make_box("Ext_Sidewalk_Far", (0.0, -7.35, -0.06), (8.6, 1.10, 0.12), COL_CONCRETE)
    make_box("Ext_Puddle_0", (-1.8, -1.10, 0.002), (0.90, 0.45, 0.002), COL_PUDDLE)
    make_box("Ext_Puddle_1", (1.5, -3.55, -0.056), (1.20, 0.55, 0.002), COL_PUDDLE)
    # Streetlamp at the sidewalk's outer edge (buffer strip)
    make_cyl("Streetlamp_Pole", (3.0, -2.38, 2.10), 0.045, 4.20, P.METAL_BLACK,
             segments=12)
    make_cyl("Streetlamp_Arm", (2.85, -2.38, 4.05), 0.025, 0.40, P.METAL_BLACK,
             axis='X')
    make_cyl("Streetlamp_Head", (2.62, -2.38, 3.98), 0.09, 0.14, P.METAL_BLACK,
             segments=12)
    make_cyl("Streetlamp_Glow", (2.62, -2.38, 3.89), 0.065, 0.05, COL_GLOW_WARM,
             segments=12)
    # Facade above the storefront — painted band + cornice parapet
    make_box("Facade_Band", (0.0, -0.02, 3.45), (7.40, 0.24, 1.30),
             (0.30, 0.26, 0.34, 1.0))
    make_box("Facade_Cornice", (0.0, -0.10, 4.16), (7.70, 0.44, 0.18),
             (0.24, 0.26, 0.28, 1.0))
    # CHILLWAVE VIDEO sign panel — teal field, cream letter band,
    # brackets; lettering scene-side on ChillWave_SignLetters
    make_box("ChillWave_SignPanel", (0.0, -0.20, 3.44), (2.90, 0.08, 0.62), COL_BRAND)
    make_box("ChillWave_SignLetters", (0.0, -0.245, 3.50), (2.40, 0.006, 0.28),
             COL_CREAM)
    make_box("ChillWave_SignRule", (0.0, -0.245, 3.24), (1.70, 0.006, 0.04), COL_CREAM)
    for bsgn in (-1, +1):
        make_box(f"ChillWave_SignBracket_{bsgn:+d}", (bsgn * 1.20, -0.13, 3.80),
                 (0.05, 0.10, 0.14), P.METAL_BLACK)
    # Cale's F-150 at the curb (slab-tier box body per playbook)
    tx, ty = -2.55, -3.75          # near lane, wheels clear of the curb
    for wi, (wx, wy) in enumerate([(-4.05, ty - 0.80), (-1.05, ty - 0.80),
                                   (-4.05, ty + 0.80), (-1.05, ty + 0.80)]):
        make_cyl(f"CaleTruck_Wheel_{wi}", (wx, wy, 0.36), 0.36, 0.26,
                 (0.10, 0.10, 0.11, 1.0), axis='Y', segments=12)
    make_box("CaleTruck_Chassis", (tx, ty, 0.70), (4.90, 1.78, 0.42), COL_TRUCK)
    make_box("CaleTruck_Hood", (-4.35, ty, 1.02), (1.30, 1.68, 0.24), COL_TRUCK)
    make_box("CaleTruck_Cab", (-3.05, ty, 1.25), (1.45, 1.62, 0.68), COL_TRUCK)
    make_box("CaleTruck_Windshield", (-3.80, ty, 1.33), (0.04, 1.30, 0.38), COL_GLASS_DK)
    for ssgn in (-1, +1):
        make_box(f"CaleTruck_SideGlass_{ssgn:+d}", (-3.02, ty + ssgn * 0.82, 1.33),
                 (0.95, 0.03, 0.34), COL_GLASS_DK)
    make_box("CaleTruck_Bed", (-1.20, ty, 1.05), (2.20, 1.68, 0.52), COL_TRUCK_DK,
             open_faces={'+Z'})
    make_box("CaleTruck_BedFloor", (-1.20, ty, 0.82), (2.10, 1.58, 0.04), COL_TRUCK_DK)
    make_box("CaleTruck_BumperF", (-5.02, ty, 0.55), (0.10, 1.70, 0.16), COL_STEEL_WORN)
    make_box("CaleTruck_BumperR", (-0.08, ty, 0.55), (0.10, 1.70, 0.16), COL_STEEL_WORN)
    make_box("CaleTruck_Mirror", (-3.72, ty + 0.90, 1.42), (0.06, 0.08, 0.12),
             COL_TRUCK_DK)


# ═════════════════════════════════════════════════════════════════
# COUNTER ZONE — the counter guards the doorway to the back ("she
# walked around the counter and through the doorway", ch6). Cedar
# plank face, register, Cale's paperback (ch3), a short stack of
# sleeves, his stool, and the INVENTORY SHELF behind the register
# with Estuary 7's empty disc-case on it (on that shelf since the
# seventeenth of August, ch21 — the stick itself is in the back).
# ═════════════════════════════════════════════════════════════════
def build_counter_zone():
    # Body x 0.4..2.6, customer face y 3.94, top z COUNTER_TOP
    make_box("Counter_Body", (1.5, 4.25, 0.46), (2.20, 0.62, 0.92), COL_CEDAR)
    make_box("Counter_Top", (1.5, 4.25, 0.955), (2.36, 0.74, 0.06), COL_CEDAR_DK)
    make_box("Counter_Kick", (1.5, 3.93, 0.10), (2.20, 0.02, 0.20), COL_CEDAR_DK)
    for pi in range(5):
        px = 0.66 + pi * 0.42
        make_box(f"Counter_Plank_{pi}", (px, 3.935, 0.52), (0.36, 0.012, 0.78),
                 COL_CEDAR_LT if pi % 2 == 0 else COL_CEDAR)
    # Register (the slow-shop till; Cale sells for nineteen dollars
    # and says "we'll settle later")
    make_register("Register", (2.05, 4.32, COUNTER_TOP),
                  palette={"body": (0.30, 0.29, 0.28, 1.0)})
    # Cale's paperback, face down mid-counter (ch3)
    make_box("Paperback_Block", (1.15, 4.16, COUNTER_TOP + 0.014),
             (0.115, 0.175, 0.026), (0.44, 0.22, 0.19, 1.0))
    make_box("Paperback_Pages", (1.15, 4.16, COUNTER_TOP + 0.013),
             (0.100, 0.160, 0.020), P.PAPER)
    # A short stack of empty waxed sleeves + a wax-pencil
    _case_pile("Counter_SleeveStack", 0.70, 4.30, COUNTER_TOP, 3, seed=4)
    make_cyl("Counter_WaxPencil", (0.70, 4.08, COUNTER_TOP + 0.008), 0.006, 0.14,
             (0.82, 0.64, 0.28, 1.0), axis='X')
    # Cale's stool, behind the counter
    make_cyl("CaleStool_Seat", (1.5, 5.05, 0.60), 0.16, 0.045, COL_CEDAR, segments=12)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"CaleStool_Leg_{li}", (1.5 + sx * 0.10, 5.05 + sy * 0.10, 0.29),
                 0.016, 0.58, COL_CEDAR_DK)
    # INVENTORY SHELF behind the register (north wall, y face 5.90)
    for bi, bz in enumerate((1.30, 1.72)):
        make_box(f"InvShelf_Board_{bi}", (1.5, 5.82, bz), (1.30, 0.20, 0.03), COL_CEDAR)
        for ki, kx in enumerate((0.95, 2.05)):
            make_box(f"InvShelf_Bracket_{bi}_{ki}", (kx, 5.86, bz - 0.07),
                     (0.03, 0.10, 0.11), P.METAL_BLACK)
    # Estuary 7's empty disc-case, face out, white label (label
    # lettering scene-side on InvShelf_Estuary7_Label)
    make_box("InvShelf_Estuary7_Case", (1.12, 5.77, 1.3925), (0.125, 0.024, 0.155),
             CASE_TINTS[0])
    make_box("InvShelf_Estuary7_Label", (1.12, 5.756, 1.40), (0.075, 0.005, 0.045),
             (0.96, 0.95, 0.92, 1.0))
    _media_row("InvShelf_Row", 1.30, 2.10, 5.82, 1.735, seed=61, axis='X')
    _case_pile("InvShelf_Pile", 1.75, 5.82, 1.315, 2, seed=9)
    # Kraft carton of fresh foundation sleeves under the counter
    make_box("Counter_UnderShelf", (1.5, 4.42, 0.50), (1.90, 0.34, 0.025), COL_CEDAR_DK)
    make_box("Counter_SleeveCarton", (1.05, 4.42, 0.60), (0.34, 0.26, 0.17), COL_KRAFT)


# ═════════════════════════════════════════════════════════════════
# THE FLOOR — the stock that IS on the floor (ch3: "It's not on the
# floor" — implying the floor stock the sentence measures against).
# Two double-sided cedar browser islands west of the center aisle,
# one east; cedar wall runs on both side walls. All of it filed
# and tabbed by designer, all of it Cale's 2046 cedar.
# ═════════════════════════════════════════════════════════════════
def _browser_island(idx, cx, cy):
    x0, x1 = cx - 1.0, cx + 1.0
    make_box(f"Island{idx}_Plinth", (cx, cy, 0.05), (2.0, 0.64, 0.10), COL_CEDAR_DK)
    for si, sx in enumerate((x0 + 0.025, x1 - 0.025)):
        make_box(f"Island{idx}_End_{si}", (sx, cy, 0.51), (0.05, 0.64, 1.02), COL_CEDAR)
    make_box(f"Island{idx}_Divider", (cx, cy, 0.575), (1.90, 0.05, 0.95), COL_CEDAR)
    make_box(f"Island{idx}_LowShelf", (cx, cy, 0.30), (1.90, 0.56, 0.03), COL_CEDAR_LT)
    for face, fsgn in (("S", -1), ("N", +1)):
        make_box(f"Island{idx}_{face}_BinFloor", (cx, cy + fsgn * 0.17, 0.735),
                 (1.90, 0.28, 0.03), COL_CEDAR_LT)
        make_box(f"Island{idx}_{face}_Lip", (cx, cy + fsgn * 0.305, 0.79),
                 (1.90, 0.03, 0.07), COL_CEDAR_DK)
        _media_row(f"Island{idx}_{face}_Row", x0 + 0.10, x1 - 0.10,
                   cy + fsgn * 0.17, 0.75,
                   seed=idx * 29 + (0 if face == "S" else 43), axis='X')
    _case_pile(f"Island{idx}_Under_A", x0 + 0.45, cy - 0.12, 0.315, 3, seed=idx * 5 + 1)
    _case_pile(f"Island{idx}_Under_B", x1 - 0.50, cy + 0.10, 0.315, 2, seed=idx * 5 + 3)
    # Section card on the aisle-facing east end (scene-side letters)
    make_box(f"Island{idx}_Card", (x1 + 0.006, cy, 0.85), (0.012, 0.24, 0.14), P.PAPER)

def _wall_media_run(prefix, wall_x, dir_sign, y0, y1, shelf_zs, seed0):
    """Cedar wall shelving; dir_sign = +1 shelves face east (west
    wall), −1 face west (east wall). Media rows run along Y."""
    cyy = (y0 + y1) / 2.0
    back_x = wall_x + dir_sign * 0.02
    make_box(f"{prefix}_Back", (back_x, cyy, 1.12), (0.04, y1 - y0, 2.24), COL_CEDAR)
    up_x = wall_x + dir_sign * 0.15
    for ui, uy in enumerate((y0, cyy, y1)):
        make_box(f"{prefix}_Upright_{ui}", (up_x, uy, 1.12), (0.26, 0.05, 2.24),
                 COL_CEDAR)
    make_box(f"{prefix}_Cap", (up_x, cyy, 2.265), (0.30, y1 - y0 + 0.08, 0.05),
             COL_CEDAR)
    for si, sz in enumerate(shelf_zs):
        make_box(f"{prefix}_Board_{si}", (up_x, cyy, sz), (0.26, y1 - y0 - 0.10, 0.03),
                 COL_CEDAR_LT)
        _media_row(f"{prefix}_S{si}", y0 + 0.08, y1 - 0.08,
                   wall_x + dir_sign * 0.145, sz + 0.015,
                   seed=seed0 + si * 13, axis='Y')

def build_floor_stock():
    _browser_island(0, -1.6, 2.05)
    _browser_island(1, -1.6, 3.55)
    _browser_island(2, +1.7, 2.05)
    _wall_media_run("WestRun", -3.40, +1, 0.9, 5.3, (0.30, 0.82, 1.34, 1.86), 7)
    _wall_media_run("EastRun", +3.40, -1, 0.8, 3.4, (0.30, 0.82, 1.34, 1.86), 71)
    # Two framed designer one-sheets on the east wall's open north
    # section, proud of the wall face at x 3.40 (video-shop
    # register; abstract blocks, no invented lettering)
    for fi, (fy, art) in enumerate([(4.0, (0.30, 0.38, 0.46, 1.0)),
                                    (5.0, (0.44, 0.22, 0.19, 1.0))]):
        make_box(f"Poster_{fi}_Frame", (3.385, fy, 1.70), (0.03, 0.50, 0.66),
                 COL_CEDAR_DK)
        make_box(f"Poster_{fi}_Sheet", (3.365, fy, 1.70), (0.02, 0.42, 0.58), P.PAPER_AGED)
        make_box(f"Poster_{fi}_Art", (3.352, fy, 1.78), (0.006, 0.34, 0.28), art)
        make_box(f"Poster_{fi}_TitleBand", (3.352, fy, 1.44), (0.006, 0.30, 0.06),
                 COL_CAST_IRON)


# ═════════════════════════════════════════════════════════════════
# THE BACK ROOM — "the back was where the inventory lived" (ch6).
# Cedar shelves alphabetized by designer (west wall + north wall),
# the new-arrivals crate by the door, the workbench in the NW
# corner with the soldering iron / precision tools / parts tray /
# the older reader under repair, the wall strip + the humming wall
# transformer, the wooden box with three sticks (third slot:
# Estuary 7, white label), the folding metal chair, the chair in
# the corner, and the closet the folding chair came out of.
# ═════════════════════════════════════════════════════════════════
def build_back_room():
    wall_n_face = BACK_Y1 - 0.10          # 9.10
    wall_e_face = BACK_XE - 0.10          # 1.40
    # ── Cedar inventory shelves — west wall (rows along Y; stops
    # at y 8.2 so the run clears the workbench in the NW corner) ──
    _wall_media_run("BackRunW", -3.40, +1, 6.5, 8.2,
                    (0.30, 0.82, 1.34, 1.86), 101)
    # ── Cedar inventory shelves — north wall (rows along X; the
    # slice x −0.75..+0.5 of this unit is what the establishing
    # camera sees through the doorway) ───────────────────────────
    bx0, bx1 = -1.40, 0.90
    bcx = (bx0 + bx1) / 2.0
    make_box("BackRunN_Back", (bcx, wall_n_face - 0.02, 1.12),
             (bx1 - bx0, 0.04, 2.24), COL_CEDAR)
    for ui, ux in enumerate((bx0, bcx, bx1)):
        make_box(f"BackRunN_Upright_{ui}", (ux, wall_n_face - 0.15, 1.12),
                 (0.05, 0.26, 2.24), COL_CEDAR)
    make_box("BackRunN_Cap", (bcx, wall_n_face - 0.15, 2.265),
             (bx1 - bx0 + 0.08, 0.30, 0.05), COL_CEDAR)
    for si, sz in enumerate((0.30, 0.82, 1.34, 1.86)):
        make_box(f"BackRunN_Board_{si}", (bcx, wall_n_face - 0.15, sz),
                 (bx1 - bx0 - 0.10, 0.26, 0.03), COL_CEDAR_LT)
        _media_row(f"BackRunN_S{si}", bx0 + 0.08, bx1 - 0.08,
                   wall_n_face - 0.145, sz + 0.015, seed=151 + si * 13, axis='X')
    # ── New-arrivals crate by the door (ch6) ─────────────────────
    make_box("Crate_Body", (-0.95, 6.55, 0.19), (0.52, 0.52, 0.34), COL_CEDAR_DK,
             open_faces={'+Z'})
    for ci, cz in enumerate((0.10, 0.24)):
        make_box(f"Crate_Slat_W_{ci}", (-1.215, 6.55, cz), (0.015, 0.50, 0.07),
                 COL_CEDAR_LT)
        make_box(f"Crate_Slat_S_{ci}", (-0.95, 6.285, cz), (0.50, 0.015, 0.07),
                 COL_CEDAR_LT)
    _case_pile("Crate_Pile_A", -1.06, 6.48, 0.05, 4, seed=31)
    _case_pile("Crate_Pile_B", -0.84, 6.64, 0.05, 3, seed=37)
    make_box("Crate_FaceUpSleeve", (-0.90, 6.44, 0.155), (0.135, 0.150, 0.014),
             SLEEVE_TINTS[1])
    # ── THE WORKBENCH — NW corner, along the north wall ──────────
    bench_cx, bench_cy = -2.6, 8.72       # top spans x −3.4..−1.8
    make_box("Bench_Top", (bench_cx, bench_cy, 0.90), (1.60, 0.70, 0.05), COL_CEDAR)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"Bench_Leg_{li}", (bench_cx + sx * 0.72, bench_cy + sy * 0.28, 0.44),
                 0.030, 0.88, COL_CEDAR_DK)
    make_box("Bench_LowShelf", (bench_cx, bench_cy, 0.26), (1.50, 0.60, 0.03),
             COL_CEDAR_LT)
    make_box("Bench_KraftBox_0", (-3.05, 8.72, 0.40), (0.34, 0.30, 0.24), COL_KRAFT)
    make_box("Bench_KraftBox_1", (-2.55, 8.72, 0.37), (0.30, 0.26, 0.18), COL_KRAFT)
    bt = 0.925                            # bench top surface
    # Work lamp, west end — vertical pole + horizontal arm (no
    # diagonals), green shade, warm bulb
    make_cyl("BenchLamp_Base", (-3.26, 8.85, bt + 0.012), 0.070, 0.024, COL_CAST_IRON,
             segments=12)
    make_cyl("BenchLamp_Pole", (-3.26, 8.85, bt + 0.30), 0.012, 0.56, COL_CAST_IRON)
    make_cyl("BenchLamp_Arm", (-3.08, 8.85, bt + 0.56), 0.010, 0.36, COL_CAST_IRON,
             axis='X')
    make_cyl("BenchLamp_Shade", (-2.90, 8.85, bt + 0.50), 0.070, 0.10, COL_LAMPGREEN,
             segments=12)
    make_cyl("BenchLamp_Glow", (-2.90, 8.85, bt + 0.435), 0.040, 0.025, COL_GLOW_WARM)
    # The older reader under repair — "the small thing he had been
    # working on" (ch6): shell open, lid off flat, board exposed
    make_box("Reader_Base", (-2.95, 8.62, bt + 0.018), (0.165, 0.115, 0.036),
             CASE_TINTS[5])
    make_box("Reader_Board", (-2.95, 8.62, bt + 0.042), (0.120, 0.080, 0.010),
             (0.22, 0.36, 0.24, 1.0))
    for chi in range(2):
        make_box(f"Reader_Chip_{chi}", (-2.985 + chi * 0.07, 8.62, bt + 0.054),
                 (0.030, 0.030, 0.012), COL_CAST_IRON)
    make_box("Reader_Lid", (-2.95, 8.44, bt + 0.005), (0.165, 0.115, 0.010),
             CASE_TINTS[5])
    make_box("Reader_SlotBar", (-2.875, 8.62, bt + 0.052), (0.012, 0.070, 0.008),
             COL_STEEL)
    # Soldering iron on its stand, UNPLUGGED and cooling (ch6 + the
    # music-catalog desc) — coiled cord + free plug on the bench
    make_box("Iron_StandBase", (-2.60, 8.85, bt + 0.010), (0.10, 0.07, 0.020),
             COL_STEEL_WORN)
    for pi, py in enumerate((8.82, 8.88)):
        make_cyl(f"Iron_StandPost_{pi}", (-2.60, py, bt + 0.045), 0.006, 0.05,
                 COL_STEEL_WORN)
    make_cyl("Iron_Barrel", (-2.60, 8.85, bt + 0.075), 0.008, 0.16, COL_STEEL, axis='X')
    make_cyl("Iron_Handle", (-2.48, 8.85, bt + 0.075), 0.014, 0.09, COL_CAST_IRON,
             axis='X')
    make_cyl("Iron_Tip", (-2.70, 8.85, bt + 0.075), 0.004, 0.05, COL_STEEL_WORN,
             axis='X')
    make_cyl("Iron_CordCoil", (-2.44, 8.66, bt + 0.010), 0.045, 0.018, COL_CAST_IRON,
             segments=12)
    make_box("Iron_Plug_Free", (-2.40, 8.58, bt + 0.008), (0.026, 0.018, 0.014),
             COL_CAST_IRON)
    # The parts tray — "moved a few small parts off the bench into
    # a tray" (ch6)
    make_box("PartsTray", (-2.15, 8.85, bt + 0.026), (0.22, 0.16, 0.05), COL_STEEL_WORN,
             open_faces={'+Z'})
    make_box("PartsTray_Floor", (-2.15, 8.85, bt + 0.006), (0.20, 0.14, 0.008),
             (0.40, 0.40, 0.42, 1.0))
    for pti in range(3):
        make_box(f"PartsTray_Part_{pti}", (-2.21 + pti * 0.055, 8.83 + (pti % 2) * 0.04,
                 bt + 0.018), (0.022, 0.016, 0.012),
                 [COL_CAST_IRON, COL_BRASS, COL_STEEL][pti])
    # Small precision tools, front edge of the bench
    for ti in range(3):
        tx = -2.90 + ti * 0.12
        make_cyl(f"Tool_Driver_{ti}_Shaft", (tx, 8.47, bt + 0.008), 0.005, 0.12,
                 COL_STEEL, axis='Y')
        make_cyl(f"Tool_Driver_{ti}_Handle", (tx, 8.56, bt + 0.010), 0.012, 0.05,
                 [CASE_TINTS[2], CASE_TINTS[1], CASE_TINTS[3]][ti], axis='Y')
    for wi, wx in enumerate((-2.52, -2.512)):
        make_box(f"Tool_Tweezer_{wi}", (wx, 8.47, bt + 0.005), (0.004, 0.090, 0.006),
                 COL_STEEL)
    make_cyl("Tool_Loupe", (-2.36, 8.48, bt + 0.012), 0.028, 0.024, COL_CAST_IRON)
    # Screw jars + tins on the shelf above the bench
    make_box("BenchShelf", (bench_cx, wall_n_face - 0.10, 1.62), (1.40, 0.16, 0.03),
             COL_CEDAR)
    for ki, kx in enumerate((-3.15, -2.05)):
        make_box(f"BenchShelf_Bracket_{ki}", (kx, wall_n_face - 0.06, 1.55),
                 (0.03, 0.09, 0.11), P.METAL_BLACK)
    for ji in range(3):
        make_cyl(f"BenchShelf_Jar_{ji}", (-3.05 + ji * 0.16, wall_n_face - 0.10, 1.685),
                 0.035, 0.100, (0.82, 0.78, 0.68, 1.0))
        make_cyl(f"BenchShelf_JarLid_{ji}", (-3.05 + ji * 0.16, wall_n_face - 0.10,
                 1.745), 0.037, 0.016, COL_STEEL_WORN)
    for ni in range(2):
        make_cyl(f"BenchShelf_Tin_{ni}", (-2.40 + ni * 0.14, wall_n_face - 0.10, 1.665),
                 0.040, 0.060, COL_STEEL_WORN)
    # THE WALL STRIP + THE TRANSFORMER — "the transformer on the
    # wall hummed faintly even with the iron unplugged" (ch6)
    make_box("PowerStrip_Body", (-2.85, wall_n_face - 0.035, 1.24), (0.42, 0.05, 0.09),
             (0.82, 0.80, 0.74, 1.0))
    for oi in range(3):
        make_box(f"PowerStrip_Outlet_{oi}", (-2.99 + oi * 0.11, wall_n_face - 0.063,
                 1.24), (0.045, 0.006, 0.045), COL_CAST_IRON)
    make_box("PowerStrip_CordDown", (-2.68, wall_n_face - 0.03, 0.60),
             (0.018, 0.018, 1.16), COL_CAST_IRON)
    make_box("WallTransformer_Body", (-2.66, wall_n_face - 0.10, 1.26),
             (0.095, 0.085, 0.135), COL_CAST_IRON)
    make_box("WallTransformer_LED", (-2.66, wall_n_face - 0.145, 1.30),
             (0.014, 0.006, 0.014), (0.94, 0.62, 0.30, 1.0))
    make_box("WallTransformer_CordDown", (-2.66, wall_n_face - 0.05, 1.02),
             (0.016, 0.016, 0.34), COL_CAST_IRON)
    # THE WOODEN BOX — three sticks, "third slot in the wooden box"
    # = Estuary 7, Ines Rocha 2046, white label in his small
    # careful hand (label lettering scene-side)
    make_box("StickBox_Body", (-1.95, 8.58, bt + 0.048), (0.30, 0.13, 0.095),
             COL_CEDAR_DK, open_faces={'+Z'})
    make_box("StickBox_Floor", (-1.95, 8.58, bt + 0.010), (0.28, 0.11, 0.010),
             COL_CEDAR)
    for di, dx in enumerate((-0.050, +0.050)):
        make_box(f"StickBox_Divider_{di}", (-1.95 + dx, 8.58, bt + 0.048),
                 (0.006, 0.11, 0.075), COL_CEDAR)
    make_box("StickBox_Stick_0", (-2.045, 8.58, bt + 0.058), (0.020, 0.016, 0.088),
             CASE_TINTS[0])
    make_box("StickBox_Stick_1", (-1.950, 8.58, bt + 0.058), (0.020, 0.016, 0.088),
             CASE_TINTS[3])
    make_box("StickBox_Estuary7", (-1.855, 8.58, bt + 0.062), (0.026, 0.022, 0.096),
             SLEEVE_TINTS[2])
    make_box("StickBox_Estuary7_Label", (-1.855, 8.567, bt + 0.070),
             (0.020, 0.004, 0.030), (0.96, 0.95, 0.92, 1.0))
    # ── Seats: Cale's stool at the bench; the FOLDING METAL chair
    # (the one Lena sits on, ch6_why_lena); the wood chair waiting
    # in the corner (the "second chair" he pulls over) ───────────
    make_cyl("BenchStool_Seat", (-2.60, 8.10, 0.60), 0.16, 0.045, COL_CEDAR,
             segments=12)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"BenchStool_Leg_{li}", (-2.60 + sx * 0.10, 8.10 + sy * 0.10, 0.29),
                 0.016, 0.58, COL_CEDAR_DK)
    fx, fy = -1.95, 7.55
    make_box("FoldChair_Seat", (fx, fy, 0.44), (0.40, 0.38, 0.025), COL_STEEL_WORN)
    make_box("FoldChair_Back", (fx, fy + 0.20, 0.78), (0.38, 0.025, 0.30),
             COL_STEEL_WORN)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"FoldChair_Leg_{li}", (fx + sx * 0.17, fy + sy * 0.16, 0.215),
                 0.011, 0.43, COL_CAST_IRON)
    for ci, csgn in enumerate((-1, +1)):
        make_cyl(f"FoldChair_BackPost_{ci}", (fx + csgn * 0.17, fy + 0.20, 0.665),
                 0.011, 0.45, COL_CAST_IRON)
    make_cyl("FoldChair_CrossBar", (fx, fy - 0.16, 0.10), 0.009, 0.34, COL_CAST_IRON,
             axis='X')
    _wood_chair("CornerChair", -2.90, 6.50, 'E', COL_CEDAR)
    # ── The closet (the folding chair's home) — east wall, closed
    # surface-mounted leaf ───────────────────────────────────────
    for pi, py in enumerate((7.92, 8.68)):
        make_box(f"Closet_Post_{pi}", (wall_e_face - 0.03, py, 1.10),
                 (0.06, 0.08, 2.20), COL_CEDAR)
    make_box("Closet_Header", (wall_e_face - 0.03, 8.30, 2.24), (0.06, 0.84, 0.10),
             COL_CEDAR)
    make_box("Closet_Leaf", (wall_e_face - 0.025, 8.30, 1.08), (0.05, 0.70, 2.12),
             COL_CEDAR_DK)
    make_cyl("Closet_Knob", (wall_e_face - 0.07, 8.02, 1.02), 0.022, 0.04, COL_BRASS,
             axis='X')
    # ── The back door → the porch where Cale smokes (ch13) ───────
    for pi, py in enumerate((6.52, 7.38)):
        make_box(f"BackDoor_Post_{pi}", (wall_e_face - 0.03, py, 1.10),
                 (0.06, 0.08, 2.20), COL_CEDAR)
    make_box("BackDoor_Header", (wall_e_face - 0.03, 6.95, 2.24), (0.06, 0.94, 0.10),
             COL_CEDAR)
    make_box("BackDoor_Leaf", (wall_e_face - 0.025, 6.95, 1.08), (0.05, 0.78, 2.12),
             COL_CEDAR_DK)
    make_cyl("BackDoor_Knob", (wall_e_face - 0.07, 7.26, 1.02), 0.022, 0.04, COL_BRASS,
             axis='X')
    make_box("BackDoor_Deadbolt", (wall_e_face - 0.065, 7.26, 1.18),
             (0.02, 0.05, 0.08), COL_BRASS)
    make_box("BackDoor_Mat", (1.05, 6.95, 0.006), (0.50, 0.80, 0.010), P.RUBBER_MAT)
    # Fire extinguisher on the east wall between the two doors
    # (retail code; anchor keeps its YZ sign panel proud of the
    # wall face at x 1.40, not buried in the wall thickness)
    make_fire_extinguisher("FireExt", (1.41, 7.62, 0.30))


# ═════════════════════════════════════════════════════════════════
# EXTERIOR · THE BACK PORCH + SIDE STRIP — "his afternoon cigarette
# at two-forty-five on the back porch at ChillWave" (ch13). Small
# plank deck off the back door, two posts, a flat lid roof, the
# coffee-can butt tin (smoking lives OUT here — none inside), and
# the gravel strip ("the lot", ch13 — empty; the truck is out front
# on Main today).
# ═════════════════════════════════════════════════════════════════
def build_back_porch():
    make_box("Ext_SideLot_Gravel", (2.65, 7.8, -0.02), (2.10, 3.20, 0.04), COL_GRAVEL)
    make_box("Ext_SideLot_Puddle", (3.05, 8.6, 0.001), (0.70, 0.42, 0.002), COL_PUDDLE)
    make_box("Porch_Deck", (2.15, 7.0, 0.07), (1.10, 1.40, 0.10), COL_CEDAR)
    for si in range(2):
        make_box(f"Porch_DeckSeam_{si}", (2.15, 6.70 + si * 0.60, 0.121),
                 (1.06, 0.015, 0.002), COL_CEDAR_DK)
    for pi, py in enumerate((6.42, 7.58)):
        make_box(f"Porch_Post_{pi}", (2.60, py, 1.27), (0.09, 0.09, 2.30), COL_CEDAR_DK)
    make_box("Porch_Roof", (2.22, 7.0, 2.46), (1.35, 1.60, 0.07), COL_CEDAR_DK)
    make_cyl("Porch_CoffeeCan", (2.44, 6.52, 0.19), 0.055, 0.14, COL_STEEL_WORN,
             segments=12)
    make_box("Porch_Step", (2.15, 7.82, 0.03), (0.80, 0.28, 0.06), COL_CEDAR_DK)


# ═════════════════════════════════════════════════════════════════
# CEILING INFRASTRUCTURE — warm cylinder pendants out front ("Lights
# low", _ART_MANIFEST — no fluorescent banks; the scaffold's tube
# fixtures were the wrong vocabulary), two green shades over the
# counter, bare bulbs on cords in the back room, smoke detectors,
# one HVAC vent.
# ═════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    _pendant("Pendant_AisleW_A", -1.6, 2.05)
    _pendant("Pendant_AisleW_B", -1.6, 3.55)
    _pendant("Pendant_AisleE", 1.7, 2.05)
    _pendant("Pendant_Entry", 0.0, 0.95)
    _pendant("Pendant_Counter_W", 0.9, 4.25, drop=0.70, shade=COL_LAMPGREEN)
    _pendant("Pendant_Counter_E", 2.1, 4.25, drop=0.70, shade=COL_LAMPGREEN)
    make_smoke_detector("Smoke", (-0.4, 3.2, CEIL))
    make_hvac_vent("HVAC", (-1.0, 5.2, CEIL), width=0.80, depth=0.40)
    _bare_bulb("BackBulb_A", -0.6, 7.0)
    _bare_bulb("BackBulb_B", -2.6, 8.35)
    make_smoke_detector("BackSmoke", (-1.6, 7.4, CEIL))


def main():
    clear_scene()
    build_shell()
    build_storefront()
    build_exterior_main_street()
    build_counter_zone()
    build_floor_stock()
    build_back_room()
    build_back_porch()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/chillwave_interior.glb"))
    print(f"\n[build_chillwave_interior] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
