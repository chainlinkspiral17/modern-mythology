"""Cosmic Comics — front room — vol6 placement script.

Rick's shop, Linden Strip Mall, wedged between the Sally Beauty and
the Great Clips. Canon sources:
  · lore/planned_community/cosmic_comics.md ("the layout"): long,
    narrow; painted Galactus on the front window throwing purple
    bars across the floor; THREE rows of long-box racks down the
    center (Marvel / DC / Indie); single tall back wall of
    new-arrival comics behind the counter; the counter itself is a
    display case of Funko Pops plus a small revolving TPB rack;
    Sharp UP-700 register (1998); YA section back-left with Maya's
    eight mood index cards.
  · lore/planned_community/rick_cosmic.md: the beige 1989 AT&T
    two-line desk phone at the back counter; THE PHONE LEDGER in a
    fireproof box bolted to the floor under the back counter;
    Dean's hand-painted OPEN/CLOSED sign (tiny ceramic frog,
    lower-right of the CLOSED face); the Pomegranate Hour VHS shelf
    + Polaroid; the framed grid of nineteen tour posters; the
    manila-envelope drop shelf; Henderson Donation boxes.
  · godot/resources/scenes/vol6/vol6_ch1_cosmic_comics.json /
    vol6_ch12_cosmic.json: brass bell above the door (1994 estate
    sale); the DO NOT SORT YET pile; subscriptions binder under the
    register; bag-and-board waste bin; manga wall; indie rack;
    shelf where Rick keeps his Sentinel.

The back room / back office is a SEPARATE GLB
(build_cosmic_comics_back_office.py — out of scope here). The seam
is the curtained EMPLOYEES-ONLY doorway cut into the north wall at
x = -1.6; a dark recess box behind it hides the void. The three-lock
service door, zine archive, couch and photocopier all live on the
other side of that curtain.

Text on signs/covers is handled scene-side (Label3D per the
playbook) — this script only bakes named vertex-colored panels:
  Window_E_ShopNameBand, NewArrivals_Header, BackRoom_Sign,
  DoNotSortYet_Sign, MangaWall_Sign, Zine_NewsFromHarmonyCreek,
  TourPoster_PhilipRetirement_*, YA_MoodCard_{0..7},
  RowSign_{Marvel,DC,Indie}_* .

No transparency: the Galactus mural is opaque painted glass (canon —
it blocks the window), the display case and key-issue case are
frame + open front per the no-glass rule, doors are frame + mullions
with the opening left empty.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import (make_floor, make_wall, make_ceiling,
                              make_crown_molding, make_door_hinges)
from _props.store_fixtures import make_register, make_credit_card_terminal
from _props.shelving import make_magazine_rack
from _props.signage import make_hanging_banner, make_paper_notices_wall
from _props.decor import make_wall_clock, make_floor_plant
from _props.safety import (make_smoke_detector, make_hvac_vent,
                           make_fluorescent_tube_fixture,
                           make_ceiling_speaker, make_security_camera)

# ── Shell (kept from the original scaffold — .tscn camera + lights
#    are tuned to this footprint) ─────────────────────────────────
ROOM_W = 10.0; ROOM_D = 8.0; CEIL = 2.8
PAL_WALL = {"wall": (0.42, 0.32, 0.46, 1.0), "baseboard": (0.18, 0.12, 0.20, 1.0)}
COL_FLOOR = (0.32, 0.28, 0.32, 1.0); COL_SEAM = (0.18, 0.16, 0.20, 1.0)
COL_WOOD = (0.42, 0.30, 0.52, 1.0)          # purple-stained trim (house style)
COL_ACCENT = (0.78, 0.42, 0.86, 1.0)

# ── Comic-shop palette ───────────────────────────────────────────
COL_SHELF_WOOD = (0.40, 0.29, 0.20, 1.0)     # decades-old oak fixtures
COL_SHELF_DARK = (0.26, 0.18, 0.14, 1.0)
COL_LONGBOX    = (0.90, 0.87, 0.80, 1.0)     # white corrugate
COL_LONGBOX_IN = (0.32, 0.28, 0.24, 1.0)
COL_KRAFT      = (0.74, 0.56, 0.34, 1.0)     # cardboard
COL_DIVIDER    = (0.94, 0.92, 0.86, 1.0)     # white divider tab
COL_BRASS      = (0.72, 0.58, 0.28, 1.0)
COL_PHONE      = (0.80, 0.75, 0.62, 1.0)     # 1989 AT&T beige
COL_FIREBOX    = (0.30, 0.30, 0.33, 1.0)     # fireproof steel
COL_LEDGER     = (0.10, 0.10, 0.11, 1.0)     # black hardcover
COL_ETAPE      = (0.16, 0.16, 0.19, 1.0)     # electrical-tape spine
COL_VELVET_A   = (0.24, 0.14, 0.30, 1.0)     # back-room curtain
COL_VELVET_B   = (0.19, 0.11, 0.25, 1.0)
COL_CORK       = (0.60, 0.45, 0.30, 1.0)
COL_FELT       = (0.16, 0.10, 0.20, 1.0)     # key-issue case lining
COL_SLAB       = (0.88, 0.90, 0.90, 1.0)     # CGC slab shell
COL_SKIN       = (0.85, 0.72, 0.58, 1.0)     # Funko vinyl skin

# Four-color-print cover tints — muted per house "warm sunset" rule
COMIC_TINTS = [
    (0.72, 0.24, 0.20, 1.0),   # Marvel red
    (0.24, 0.36, 0.62, 1.0),   # DC blue
    (0.86, 0.70, 0.28, 1.0),   # golden-age yellow
    (0.46, 0.28, 0.54, 1.0),   # indie purple
    (0.30, 0.52, 0.46, 1.0),   # teal
    (0.80, 0.48, 0.24, 1.0),   # orange
    (0.88, 0.84, 0.74, 1.0),   # newsprint white
    (0.22, 0.20, 0.24, 1.0),   # black cover
]
COL_COVER_BAND = (0.92, 0.90, 0.84, 1.0)

# Galactus mural — laid down by Rick's then-girlfriend in 1996
COL_GAL_BG      = (0.13, 0.09, 0.22, 1.0)    # deep space
COL_GAL_PURPLE  = (0.38, 0.22, 0.54, 1.0)    # armor
COL_GAL_HELM    = (0.48, 0.30, 0.64, 1.0)    # helmet
COL_GAL_MAGENTA = (0.70, 0.34, 0.64, 1.0)    # chest panel / planet
COL_GAL_SKIN    = (0.55, 0.48, 0.66, 1.0)    # face
COL_STAR        = (0.90, 0.86, 0.94, 1.0)
COL_FLOORLIGHT  = (0.40, 0.28, 0.50, 1.0)    # the purple bars on the floor


# ═════════════════════════════════════════════════════════════════
# SHELL — walls / floor / ceiling / crown. Same as every interior
# locale, EXCEPT the north wall gains a doorway to the back room.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    # North wall split around the back-room doorway (gap x -2.1..-1.1)
    make_wall("Wall_N_W", (-3.65, ROOM_D, 0), length=3.10, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (+2.05, ROOM_D, 0), length=6.30, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_N_AboveDoor", (-1.6, ROOM_D, CEIL-0.30), (1.0, 0.20, 0.60), PAL_WALL["wall"])
    # South (storefront) wall — door gap x -1..+1
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


# ═════════════════════════════════════════════════════════════════
# STOREFRONT — Galactus windows, front door (frame only, no glass),
# Dean's OPEN/CLOSED sign, the 1994 brass bell, entry mat, and the
# purple light bars the mural lays across the floor.
# ═════════════════════════════════════════════════════════════════
def _build_galactus_window(tag, wx):
    """One storefront window, interior face. tag 'W' gets the
    Galactus figure; tag 'E' gets the cosmos + shop-name band."""
    face = 0.11   # interior face of the south wall (thickness 0.20)
    # Frame
    make_box(f"Window_{tag}_Sill",  (wx, face, 0.55), (3.60, 0.10, 0.08), COL_SHELF_WOOD)
    make_box(f"Window_{tag}_Head",  (wx, face, 2.38), (3.60, 0.10, 0.08), COL_SHELF_WOOD)
    for sgn in (-1, +1):
        make_box(f"Window_{tag}_Jamb_{sgn:+d}",
                 (wx + sgn * 1.76, face, 1.46), (0.08, 0.10, 1.90), COL_SHELF_WOOD)
    # Painted glass — opaque by canon (the mural covers the pane)
    make_box(f"Window_{tag}_MuralBG", (wx, 0.13, 1.46), (3.40, 0.012, 1.74), COL_GAL_BG)
    # Star field (deterministic scatter)
    for si in range(7):
        sx = wx - 1.45 + ((si * 5 + 2) % 7) * 0.46
        sz = 0.75 + ((si * 3 + 1) % 5) * 0.32
        make_box(f"Window_{tag}_Star_{si}", (sx, 0.138, sz), (0.035, 0.004, 0.035), COL_STAR)
    if tag == 'W':
        # Blocky Galactus — helmet prongs, head, face, torso, arms
        for sgn in (-1, +1):
            make_box(f"Window_W_HelmProng_{sgn:+d}",
                     (wx + sgn * 0.44, 0.142, 1.98), (0.18, 0.010, 0.60), COL_GAL_HELM)
        make_box("Window_W_GalHead", (wx, 0.142, 1.86), (0.52, 0.010, 0.44), COL_GAL_HELM)
        make_box("Window_W_Face",  (wx, 0.150, 1.82), (0.30, 0.008, 0.28), COL_GAL_SKIN)
        for sgn in (-1, +1):
            make_box(f"Window_W_Eye_{sgn:+d}",
                     (wx + sgn * 0.08, 0.156, 1.86), (0.06, 0.004, 0.05), COL_GAL_BG)
        make_box("Window_W_Torso", (wx, 0.142, 1.16), (0.92, 0.010, 0.66), COL_GAL_PURPLE)
        make_box("Window_W_Chest", (wx, 0.150, 1.18), (0.50, 0.008, 0.42), COL_GAL_MAGENTA)
        for sgn in (-1, +1):
            make_box(f"Window_W_Arm_{sgn:+d}",
                     (wx + sgn * 0.78, 0.142, 1.20), (0.22, 0.010, 0.52), COL_GAL_PURPLE)
    else:
        # Cosmos side — ringed planet + shop-name band (Label3D
        # scene-side supplies the "COSMIC COMICS" lettering)
        make_cyl("Window_E_PlanetRing", (wx + 0.25, 0.138, 1.22), 0.58, 0.010,
                 COL_GAL_HELM, axis='Y', segments=12)
        make_cyl("Window_E_Planet", (wx + 0.25, 0.146, 1.22), 0.40, 0.010,
                 COL_GAL_MAGENTA, axis='Y', segments=12)
        make_box("Window_E_ShopNameBand", (wx - 0.10, 0.150, 1.94),
                 (2.30, 0.006, 0.34), COL_COVER_BAND)

def build_storefront():
    _build_galactus_window('W', -3.0)
    _build_galactus_window('E', +3.0)
    # Purple bars the mural lays across the floor (ch12 canon)
    for wsgn in (-1, +1):
        for k in range(3):
            bx = 3.0 * wsgn - 0.55 + k * 0.55
            make_box(f"Mural_FloorBar_{'W' if wsgn < 0 else 'E'}_{k}",
                     (bx, 2.05, 0.008), (0.34, 2.20, 0.002), COL_FLOORLIGHT)
    # Door surround inside the 2 m gap
    for sgn in (-1, +1):
        make_box(f"DoorPost_{sgn:+d}", (sgn * 0.96, 0.0, 1.10), (0.08, 0.16, 2.20), COL_SHELF_WOOD)
    make_box("DoorTransom", (0.0, 0.0, 2.24), (2.00, 0.16, 0.08), COL_SHELF_WOOD)
    # Door leaf (west half) — frame + mullions, NO glass slab
    make_box("Door_Stile_W", (-0.88, 0.0, 1.08), (0.07, 0.05, 2.10), COL_SHELF_DARK)
    make_box("Door_Stile_E", (-0.12, 0.0, 1.08), (0.07, 0.05, 2.10), COL_SHELF_DARK)
    make_box("Door_Rail_Top", (-0.50, 0.0, 2.08), (0.83, 0.05, 0.09), COL_SHELF_DARK)
    make_box("Door_Rail_Mid", (-0.50, 0.0, 0.92), (0.83, 0.05, 0.07), COL_SHELF_DARK)
    make_box("Door_KickPlate", (-0.50, 0.0, 0.15), (0.83, 0.05, 0.26), P.METAL_STEEL)
    make_cyl("Door_PushBar", (-0.50, 0.07, 1.00), 0.020, 0.62, COL_BRASS, axis='X')
    make_door_hinges("Door_Hinge", edge_x=-0.92, edge_y=0.0,
                     edge_z_centers=[0.35, 1.05, 1.80], axis='X')
    # East sidelite — frame only, opening left empty
    make_box("SideLite_Stile_W", (0.12, 0.0, 1.10), (0.06, 0.05, 2.16), COL_SHELF_DARK)
    make_box("SideLite_Stile_E", (0.88, 0.0, 1.10), (0.06, 0.05, 2.16), COL_SHELF_DARK)
    make_box("SideLite_Sill", (0.50, 0.0, 0.30), (0.80, 0.05, 0.06), COL_SHELF_DARK)
    make_box("SideLite_Mull", (0.50, 0.0, 1.52), (0.80, 0.05, 0.05), COL_SHELF_DARK)
    # Dean's hand-painted OPEN/CLOSED sign (1992) hanging on the
    # door — tiny ceramic frog glued to the lower-right of the
    # CLOSED face (rick_cosmic.md item V). Frog faces the interior.
    make_cyl("DoorSign_Cord", (-0.50, 0.045, 1.88), 0.004, 0.32, P.TWINE, axis='Z')
    make_box("DoorSign_Board", (-0.50, 0.045, 1.62), (0.34, 0.020, 0.24), (0.88, 0.82, 0.66, 1.0))
    make_box("DoorSign_TextBand", (-0.50, 0.058, 1.62), (0.26, 0.006, 0.10), (0.72, 0.24, 0.20, 1.0))
    make_box("DoorSign_Frog", (-0.37, 0.060, 1.53), (0.030, 0.012, 0.026), (0.36, 0.56, 0.34, 1.0))
    # Hours plaque on the east door post
    make_box("HoursPlaque", (1.06, 0.085, 1.45), (0.16, 0.010, 0.22), P.PAPER_AGED)
    # Brass bell above the door — 1994 estate sale (ch12 canon)
    make_box("BrassBell_Mount", (0.55, 0.13, 2.32), (0.06, 0.10, 0.06), P.METAL_BLACK)
    make_cyl("BrassBell_Arm", (0.55, 0.24, 2.32), 0.012, 0.16, COL_BRASS, axis='Y')
    make_cyl("BrassBell_Body", (0.55, 0.32, 2.27), 0.050, 0.07, COL_BRASS)
    make_cyl("BrassBell_Flare", (0.55, 0.32, 2.22), 0.068, 0.025, COL_BRASS)
    make_cyl("BrassBell_Clapper", (0.55, 0.32, 2.18), 0.012, 0.05, P.METAL_BLACK)
    # Entry mat
    make_box("EntryMat_Under", (0.0, 0.85, 0.004), (1.90, 1.10, 0.006), (0.14, 0.13, 0.13, 1.0))
    make_box("EntryMat", (0.0, 0.85, 0.011), (1.76, 0.96, 0.008), P.RUBBER_MAT)


# ═════════════════════════════════════════════════════════════════
# LONG-BOX ROWS — three rows down the center: Marvel / DC / Indie.
# Wood browsing tables, white long boxes with comics + divider tabs
# poking above the rims, spare closed boxes on the lower shelf,
# hanging row signs (Label3D scene-side).
# ═════════════════════════════════════════════════════════════════
def build_longbox_rows():
    rows = [
        ("Marvel", 2.35, COMIC_TINTS[0]),
        ("DC",     3.80, COMIC_TINTS[1]),
        ("Indie",  5.25, COMIC_TINTS[3]),
    ]
    for ri, (name, ry, sign_col) in enumerate(rows):
        # Table — 4.8 m browsing run, 0.60 m deep, top at 0.625
        make_box(f"LBTable_{name}_Top", (0.0, ry, 0.60), (4.80, 0.60, 0.05), COL_SHELF_WOOD)
        for sgn in (-1, +1):
            make_box(f"LBTable_{name}_End_{sgn:+d}",
                     (sgn * 2.35, ry, 0.30), (0.06, 0.58, 0.60), COL_SHELF_DARK)
        make_box(f"LBTable_{name}_Spine", (0.0, ry, 0.30), (4.60, 0.05, 0.56), COL_SHELF_DARK)
        make_box(f"LBTable_{name}_LowShelf", (0.0, ry, 0.16), (4.60, 0.52, 0.04), COL_SHELF_WOOD)
        # Spare sealed long boxes on the lower shelf
        for si in range(3):
            sx = -1.5 + si * 1.5
            make_box(f"LBTable_{name}_Spare_{si}", (sx, ry, 0.31), (0.70, 0.30, 0.24), COL_LONGBOX)
            make_box(f"LBTable_{name}_SpareLid_{si}", (sx, ry, 0.435), (0.74, 0.34, 0.03), COL_LONGBOX)
        # Six open long boxes on the tabletop, comics face E-W
        for bi in range(6):
            bx = -1.80 + bi * 0.72
            make_box(f"LongBox_{name}_{bi}_Shell", (bx, ry, 0.775),
                     (0.62, 0.30, 0.30), COL_LONGBOX, open_faces={'+Z'})
            make_box(f"LongBox_{name}_{bi}_Inner", (bx, ry, 0.66),
                     (0.58, 0.26, 0.02), COL_LONGBOX_IN)
            for ci in range(7):
                cx = bx - 0.24 + ci * 0.075
                tint = COMIC_TINTS[(ri * 5 + bi * 3 + ci) % len(COMIC_TINTS)]
                make_box(f"LongBox_{name}_{bi}_Comic_{ci}",
                         (cx, ry, 0.82), (0.020, 0.26, 0.26), tint)
            for ti, tx_off in enumerate((-0.13, +0.17)):
                make_box(f"LongBox_{name}_{bi}_Tab_{ti}",
                         (bx + tx_off, ry, 0.86), (0.010, 0.27, 0.30), COL_DIVIDER)
        # Hanging row sign — MARVEL / DC / INDIE lettering scene-side
        make_hanging_banner(f"RowSign_{name}", (0.0, ry, CEIL),
                            width=1.30, height=0.32,
                            bg_color=sign_col, text_color=P.PAPER)


# ═════════════════════════════════════════════════════════════════
# COUNTER ZONE — the counter IS a display case (Funko Pops behind an
# open front, per the no-glass rule), register section with the
# Sharp UP-700, the beige 1989 AT&T phone, THE PHONE LEDGER in its
# floor-bolted fireproof box, card terminal, waste bin, employee
# cubby, and the revolving markdown-TPB rack beside it.
# ═════════════════════════════════════════════════════════════════
def build_counter_zone():
    cy = 6.85   # counter centerline; customer face 6.50, clerk aisle 7.20..8.0
    # Display-case section (x 0.4..2.0): frame + shelf, front open
    make_box("Case_Base", (1.20, cy, 0.14), (1.60, 0.70, 0.28), COL_SHELF_DARK)
    for pi, (px, py) in enumerate([(0.44, 6.54), (1.96, 6.54), (0.44, 7.16), (1.96, 7.16)]):
        make_box(f"Case_Post_{pi}", (px, py, 0.61), (0.06, 0.06, 0.66), COL_SHELF_WOOD)
    make_box("Case_Rim_F", (1.20, 6.54, 0.95), (1.62, 0.05, 0.05), COL_SHELF_WOOD)
    make_box("Case_Rim_B", (1.20, 7.16, 0.95), (1.62, 0.05, 0.05), COL_SHELF_WOOD)
    for sgn in (-1, +1):
        make_box(f"Case_Rim_Side_{sgn:+d}", (1.20 + sgn * 0.78, cy, 0.95),
                 (0.05, 0.62, 0.05), COL_SHELF_WOOD)
    make_box("Case_BackPanel", (1.20, 7.17, 0.60), (1.60, 0.04, 0.68), COL_SHELF_WOOD)
    make_box("Case_Shelf", (1.20, cy, 0.55), (1.50, 0.58, 0.03), (0.72, 0.74, 0.76, 1.0))
    # Funko Pops — cylinder body + oversized cylinder head (round
    # geometry at eye level per playbook); sell ~one every two months
    for fi in range(6):
        fx = 0.55 + fi * 0.26
        tint = COMIC_TINTS[(fi * 3 + 1) % len(COMIC_TINTS)]
        make_cyl(f"FunkoPop_{fi}_Body", (fx, cy, 0.62), 0.040, 0.10, tint)
        make_cyl(f"FunkoPop_{fi}_Head", (fx, cy, 0.71), 0.056, 0.07, COL_SKIN)
    # Register section (x 2.0..3.0) — solid cabinet + dark top
    make_box("Counter_Body", (2.50, cy, 0.46), (1.00, 0.70, 0.92),
             (0.42, 0.30, 0.52, 1.0))
    make_box("Counter_Top", (2.50, cy, 0.95), (1.10, 0.80, 0.06), P.COUNTER_TOP)
    make_box("Counter_Kick", (2.50, 6.49, 0.10), (1.00, 0.02, 0.20), P.COUNTER_DARK)
    make_cyl("Counter_Bullnose", (2.50, 6.44, 0.93), 0.025, 1.05, P.COUNTER_TOP, axis='X')
    # Sharp UP-700 (1998) — refused replacement three times
    make_register("RegisterMachine", (2.50, 6.95, 0.98),
                  palette={"body": (0.62, 0.60, 0.55, 1.0)})
    make_credit_card_terminal("CardTerminal", (2.15, 6.62, 0.98))
    # THE PHONE — beige 1989 AT&T two-line desk unit. The line the
    # call from Beaumont has come in on since 2002.
    make_box("Phone_Base", (2.88, 7.08, 1.01), (0.24, 0.20, 0.06), COL_PHONE)
    make_box("Phone_Keypad", (2.90, 7.04, 1.045), (0.10, 0.08, 0.012), (0.30, 0.28, 0.26, 1.0))
    for ki in range(2):
        make_box(f"Phone_LineKey_{ki}", (2.80, 7.02 + ki * 0.04, 1.045),
                 (0.03, 0.02, 0.010), (0.90, 0.90, 0.84, 1.0))
    make_box("Phone_Handset_Bar", (2.88, 7.13, 1.075), (0.05, 0.14, 0.03), COL_PHONE)
    for sgn in (-1, +1):
        make_cyl(f"Phone_Handset_Cup_{sgn:+d}", (2.88, 7.13 + sgn * 0.085, 1.065),
                 0.030, 0.045, COL_PHONE)
    for wi in range(3):
        make_cyl(f"Phone_Cord_{wi}", (2.99, 7.14, 0.94 - wi * 0.05),
                 0.007, 0.035, COL_PHONE, axis='Y')
    # THE PHONE LEDGER — "PHONE NOTES · DO NOT DISCUSS". Fireproof
    # box bolted to the floor under the back counter; black
    # hardcover, spine taped with electrical tape (rick_cosmic.md IV)
    make_box("PhoneLedger_Flange", (2.75, 7.36, 0.012), (0.42, 0.36, 0.024), COL_FIREBOX)
    for bi, (bx, by) in enumerate([(2.56, 7.20), (2.94, 7.20), (2.56, 7.52), (2.94, 7.52)]):
        make_cyl(f"PhoneLedger_Bolt_{bi}", (bx, by, 0.030), 0.012, 0.014, P.METAL_BLACK)
    make_box("PhoneLedger_Firebox", (2.75, 7.36, 0.17), (0.34, 0.28, 0.29), COL_FIREBOX)
    make_box("PhoneLedger_Handle", (2.75, 7.21, 0.24), (0.10, 0.015, 0.02), P.METAL_STEEL)
    make_box("PhoneLedger_Book", (2.75, 7.36, 0.34), (0.26, 0.20, 0.05), COL_LEDGER)
    make_box("PhoneLedger_TapeSpine", (2.63, 7.36, 0.34), (0.035, 0.21, 0.056), COL_ETAPE)
    # Bag-and-board waste bin under the register (ch12 closing canon)
    make_box("WasteBin", (1.70, 7.40, 0.19), (0.30, 0.30, 0.38), COL_SHELF_DARK,
             open_faces={'+Z'})
    make_box("WasteBin_Scrap_0", (1.66, 7.38, 0.36), (0.16, 0.14, 0.03), P.PAPER)
    make_box("WasteBin_Scrap_1", (1.75, 7.44, 0.39), (0.12, 0.10, 0.02), P.NEWSPRINT)
    # Employee cubby — where Wren drops her bag (ch12)
    make_box("EmployeeCubby", (0.55, 7.42, 0.32), (0.52, 0.40, 0.64),
             COL_SHELF_WOOD, open_faces={'+Y'})
    make_box("EmployeeCubby_Bag", (0.55, 7.42, 0.16), (0.32, 0.24, 0.24),
             (0.48, 0.50, 0.36, 1.0))
    # Revolving markdown-TPB rack beside the counter (canon)
    make_cyl("TPBSpinner_Base", (3.55, 6.10, 0.02), 0.24, 0.04, P.METAL_BLACK, segments=12)
    make_cyl("TPBSpinner_Pole", (3.55, 6.10, 0.78), 0.028, 1.52, P.METAL_STEEL)
    for tz_i, tz in enumerate((0.50, 0.90, 1.30)):
        make_cyl(f"TPBSpinner_Disc_{tz_i}", (3.55, 6.10, tz - 0.18), 0.19, 0.015,
                 P.METAL_STEEL, segments=12)
        for si in range(4):
            tint = COMIC_TINTS[(tz_i * 3 + si * 2) % len(COMIC_TINTS)]
            if si % 2 == 0:
                sgn = -1 if si == 0 else +1
                make_box(f"TPB_{tz_i}_{si}", (3.55 + sgn * 0.15, 6.10, tz),
                         (0.05, 0.26, 0.34), tint)
            else:
                sgn = -1 if si == 1 else +1
                make_box(f"TPB_{tz_i}_{si}", (3.55, 6.10 + sgn * 0.15, tz),
                         (0.26, 0.05, 0.34), tint)
    make_box("TPBSpinner_SaleSign_A", (3.55, 6.10, 1.60), (0.30, 0.015, 0.14), P.LOTTERY_RED)
    make_box("TPBSpinner_SaleSign_B", (3.55, 6.10, 1.60), (0.015, 0.30, 0.14), P.LOTTERY_RED)


# ═════════════════════════════════════════════════════════════════
# BACK WALL — the single tall wall of new-arrival comics behind the
# counter, the back-counter shelf (manila envelope / Sentinel /
# subscriptions binder), the Pomegranate Hour VHS shelf + Polaroid,
# and the wall clock frozen at 15:22 (ch1 interlude time).
# ═════════════════════════════════════════════════════════════════
def build_back_wall():
    wall_face = ROOM_D - 0.10   # 7.90
    # Slatwall panel + four face-out rows of current issues
    make_box("NewArrivals_Slat", (1.70, wall_face, 2.00), (2.60, 0.05, 1.50), COL_SHELF_DARK)
    for r in range(4):
        rz = 1.45 + r * 0.37
        make_box(f"NewArrivals_Rail_{r}", (1.70, wall_face - 0.04, rz - 0.13),
                 (2.60, 0.03, 0.03), P.METAL_STEEL)
        for c in range(8):
            cx = 0.65 + c * 0.30
            tint = COMIC_TINTS[(r * 3 + c) % len(COMIC_TINTS)]
            make_box(f"NewArrivals_{r}_{c}_Cover", (cx, wall_face - 0.05, rz),
                     (0.17, 0.012, 0.26), tint)
            make_box(f"NewArrivals_{r}_{c}_Band", (cx, wall_face - 0.062, rz + 0.09),
                     (0.13, 0.005, 0.05), COL_COVER_BAND)
    make_box("NewArrivals_Header", (1.70, wall_face - 0.03, 2.62),
             (2.00, 0.02, 0.20), COL_ACCENT)   # "NEW ARRIVALS" scene-side
    # Back-counter shelf — the manila-envelope drop (Rick checks
    # daily; Sam's twin lives behind the Kwik Stop slushie machine),
    # the subscriptions binder from Rick's notebook list, and the
    # small shelf where Rick keeps his Sentinel.
    make_box("BackCounter_Shelf", (1.50, wall_face, 1.05), (2.20, 0.24, 0.03), COL_SHELF_WOOD)
    for sgn in (-1, +1):
        make_box(f"BackCounter_Bracket_{sgn:+d}", (1.50 + sgn * 0.95, wall_face + 0.02, 0.97),
                 (0.04, 0.16, 0.14), P.METAL_BLACK)
    make_box("ManilaEnvelope", (0.85, wall_face - 0.02, 1.22), (0.24, 0.012, 0.30), COL_KRAFT)
    make_box("Sentinel_Stack", (1.55, wall_face - 0.02, 1.10), (0.30, 0.20, 0.06), P.NEWSPRINT)
    make_box("Binder_Subscriptions", (2.30, wall_face - 0.02, 1.22),
             (0.06, 0.26, 0.30), (0.22, 0.30, 0.46, 1.0))
    # Pomegranate Hour shelf — all 22 episodes on VHS + the Polaroid
    # of Elicia in the front window (2019)
    make_box("PomHour_Shelf", (4.15, wall_face, 1.82), (0.90, 0.20, 0.03), COL_SHELF_WOOD)
    for vi in range(22):
        vx = 3.76 + vi * 0.033
        vtint = (0.20, 0.18, 0.22, 1.0) if vi % 2 == 0 else (0.26, 0.20, 0.30, 1.0)
        make_box(f"VHS_{vi}", (vx, wall_face - 0.02, 1.975), (0.026, 0.16, 0.27), vtint)
    make_box("Polaroid_Frame", (4.63, wall_face - 0.01, 1.95), (0.10, 0.008, 0.12), P.PAPER)
    make_box("Polaroid_Photo", (4.63, wall_face - 0.016, 1.965), (0.08, 0.004, 0.08),
             (0.34, 0.28, 0.40, 1.0))
    # Wall clock — frozen at 15:22, the ch1 interlude timestamp
    make_wall_clock("Clock", (-0.55, wall_face - 0.03, 2.45),
                    frozen_hour=15, frozen_min=22)


# ═════════════════════════════════════════════════════════════════
# BACK-ROOM DOORWAY — the seam to build_cosmic_comics_back_office.
# Curtained (canon: the back room is "behind the curtain"), with a
# dark recess so the opening doesn't read as void, the DO NOT SORT
# YET pile, and the Henderson Donation boxes staged beside it.
# ═════════════════════════════════════════════════════════════════
def build_backroom_door():
    dx = -1.6
    # Frame + header + EMPLOYEES ONLY sign (Label3D scene-side)
    for sgn in (-1, +1):
        make_box(f"BackRoom_Post_{sgn:+d}", (dx + sgn * 0.54, ROOM_D - 0.05, 1.10),
                 (0.08, 0.14, 2.20), COL_SHELF_WOOD)
    make_box("BackRoom_Header", (dx, ROOM_D - 0.06, 2.28), (1.20, 0.10, 0.14), COL_SHELF_WOOD)
    make_box("BackRoom_Sign", (dx, ROOM_D - 0.115, 2.28), (0.90, 0.012, 0.12), P.PAPER_AGED)
    # Dark recess behind the doorway (the back room is another GLB)
    make_box("BackRoom_Recess", (dx, ROOM_D + 0.55, 1.10), (1.04, 0.90, 2.20),
             (0.06, 0.05, 0.08, 1.0))
    # Velvet curtain — rod + five strips, alternating depth/color
    make_cyl("BackRoom_CurtainRod", (dx, ROOM_D - 0.02, 2.18), 0.015, 1.00,
             COL_BRASS, axis='X')
    for k in range(5):
        kx = dx - 0.38 + k * 0.19
        col = COL_VELVET_A if k % 2 == 0 else COL_VELVET_B
        ky = ROOM_D - 0.01 + (0.03 if k % 2 else 0.0)
        make_box(f"BackRoom_Curtain_{k}", (kx, ky, 1.13), (0.165, 0.025, 2.00), col)
    # The DO NOT SORT YET pile (ch1 — Maya's patient-indifference task)
    for pi, (px, ph) in enumerate([(-0.95, 0.18), (-0.62, 0.30), (-0.32, 0.24)]):
        make_box(f"DoNotSort_Stack_{pi}", (px, 7.60, ph / 2.0), (0.30, 0.34, ph),
                 COMIC_TINTS[6] if pi % 2 == 0 else P.NEWSPRINT)
        make_box(f"DoNotSort_StackTop_{pi}", (px, 7.60, ph + 0.015), (0.28, 0.32, 0.03),
                 COMIC_TINTS[(pi * 5 + 2) % len(COMIC_TINTS)])
    make_box("DoNotSortYet_Sign", (-0.62, 7.41, 0.42), (0.26, 0.012, 0.18), P.PAPER)
    # Henderson Donation boxes — surviving Glitch Report issues
    # circulate out of these (VOL6 wiki)
    make_box("HendersonBox_0", (-2.85, 7.62, 0.20), (0.55, 0.45, 0.40), COL_KRAFT)
    make_box("HendersonBox_0_Lid", (-2.85, 7.62, 0.415), (0.59, 0.49, 0.04), COL_KRAFT)
    make_box("HendersonBox_1", (-2.85, 7.62, 0.61), (0.52, 0.42, 0.34),
             (0.68, 0.50, 0.30, 1.0))
    make_box("HendersonBox_2", (-3.60, 7.50, 0.20), (0.55, 0.45, 0.40), COL_KRAFT)
    make_box("HendersonBox_Label_0", (-2.85, 7.40, 0.61), (0.22, 0.010, 0.14), P.PAPER)
    make_box("HendersonBox_Label_1", (-3.60, 7.27, 0.20), (0.22, 0.010, 0.14), P.PAPER)


# ═════════════════════════════════════════════════════════════════
# WEST WALL — band-flyer cork board by the window, the manga wall
# (ch12: "one at the manga wall"), and the YA corner back-left with
# Maya's eight mood index cards.
# ═════════════════════════════════════════════════════════════════
def build_west_wall():
    wall_face = -ROOM_W / 2.0 + 0.10   # -4.90
    # Cork board of local-scene flyers (zine releases, Gallatin Band)
    make_box("FlyerBoard", (wall_face + 0.02, 1.35, 1.65), (0.03, 1.50, 1.05), COL_CORK)
    make_paper_notices_wall("Flyer", wall_x=wall_face + 0.04, wall_face_sign=+1,
                            run_center_y=1.35, base_z=0.0, notices=[
        (-0.55, 1.95, 0.22, 0.30, P.PAPER),
        (-0.18, 1.98, 0.26, 0.34, (0.86, 0.46, 0.22, 1.0)),
        (+0.22, 1.92, 0.20, 0.26, P.PAPER_AGED),
        (+0.55, 1.96, 0.24, 0.30, P.PAPER),
        (-0.40, 1.52, 0.24, 0.32, (0.46, 0.28, 0.54, 1.0)),
        (+0.05, 1.48, 0.20, 0.28, P.PAPER),
        (+0.45, 1.50, 0.22, 0.26, (0.30, 0.52, 0.46, 1.0)),
    ])
    # Manga wall — tall shelving, spines face east into the room
    make_box("MangaWall_Kick", (wall_face + 0.14, 4.00, 0.08), (0.28, 3.50, 0.16), COL_SHELF_DARK)
    make_box("MangaWall_Crown", (wall_face + 0.14, 4.00, 2.36), (0.28, 3.50, 0.06), COL_SHELF_WOOD)
    for ui in range(4):
        uy = 2.30 + ui * 1.1333
        make_box(f"MangaWall_Upright_{ui}", (wall_face + 0.14, uy, 1.22),
                 (0.28, 0.05, 2.28), COL_SHELF_WOOD)
    for sh in range(5):
        shz = 0.35 + sh * 0.45
        make_box(f"MangaWall_Shelf_{sh}", (wall_face + 0.14, 4.00, shz),
                 (0.28, 3.40, 0.035), COL_SHELF_WOOD)
        for k in range(14):
            ky = 2.42 + k * 0.229
            h = (0.28, 0.33, 0.26, 0.31)[(sh * 5 + k) % 4]
            tint = COMIC_TINTS[(sh * 7 + k * 3) % len(COMIC_TINTS)]
            make_box(f"MangaWall_Spines_{sh}_{k}", (wall_face + 0.16, ky, shz + h / 2.0 + 0.02),
                     (0.20, 0.20, h), tint)
        # Curtis's Tuesday-rotation shelf-talkers
        if sh in (1, 3):
            make_box(f"MangaWall_ShelfTalker_{sh}", (wall_face + 0.29, 3.10 + sh * 0.5, shz + 0.01),
                     (0.015, 0.14, 0.06), P.PAPER)
    make_box("MangaWall_Sign", (wall_face + 0.03, 4.00, 2.55), (0.02, 1.60, 0.22), COL_ACCENT)
    # YA corner (back-left, NW) — re-shelved by Maya in May into
    # eight mood categories, index cards taped to the shelf edges
    make_box("YA_W_Frame", (wall_face + 0.13, 6.80, 0.66), (0.26, 1.60, 1.32), COL_SHELF_WOOD)
    for sh in range(2):
        shz = 0.42 + sh * 0.44
        make_box(f"YA_W_Shelf_{sh}", (wall_face + 0.15, 6.80, shz), (0.26, 1.50, 0.03),
                 COL_SHELF_DARK)
    for fi in range(5):
        fy = 6.24 + fi * 0.29
        tint = ((0.86, 0.70, 0.28, 1.0), (0.30, 0.52, 0.46, 1.0), (0.70, 0.34, 0.64, 1.0),
                (0.24, 0.36, 0.62, 1.0), (0.80, 0.48, 0.24, 1.0))[fi]
        make_box(f"YA_W_FaceOut_{fi}", (wall_face + 0.29, fy, 1.02), (0.012, 0.20, 0.26), tint)
    make_box("YA_N_Frame", (-4.05, ROOM_D - 0.13, 0.66), (1.60, 0.26, 1.32), COL_SHELF_WOOD)
    for sh in range(2):
        shz = 0.42 + sh * 0.44
        make_box(f"YA_N_Shelf_{sh}", (-4.05, ROOM_D - 0.15, shz), (1.50, 0.26, 0.03),
                 COL_SHELF_DARK)
    for fi in range(5):
        fx = -4.63 + fi * 0.29
        tint = COMIC_TINTS[(fi * 3 + 4) % len(COMIC_TINTS)]
        make_box(f"YA_N_FaceOut_{fi}", (fx, ROOM_D - 0.29, 1.02), (0.20, 0.012, 0.26), tint)
    # Eight mood cards — FOR WHEN YOU NEED TO BE BRAVE, etc. —
    # Label3D scene-side; four on each unit's shelf edges
    for mi in range(8):
        if mi < 4:
            make_box(f"YA_MoodCard_{mi}", (wall_face + 0.29, 6.15 + (mi % 4) * 0.42,
                     0.44 + (mi // 2) * 0.44), (0.012, 0.13, 0.075), P.PAPER)
        else:
            make_box(f"YA_MoodCard_{mi}", (-4.70 + (mi % 4) * 0.42, ROOM_D - 0.29,
                     0.44 + ((mi - 4) // 2) * 0.44), (0.13, 0.012, 0.075), P.PAPER)


# ═════════════════════════════════════════════════════════════════
# EAST WALL — the zine rack (regional paper-stock signature, NEWS
# FROM HARMONY CREEK front and center), price-guide magazine
# shelving, the key-issue display case (frame + open front, slabbed
# books), the framed grid of nineteen tour posters behind the
# counter, and a floor plant by the window.
# ═════════════════════════════════════════════════════════════════
def build_east_wall():
    wall_face = ROOM_W / 2.0 - 0.10   # 4.90
    make_floor_plant("FloorPlant", (4.42, 0.85, 0.0))
    # Zine rack — wooden pocket rack, sold-by-hand photocopied stock
    make_box("ZineRack_Back", (wall_face - 0.04, 1.90, 1.15), (0.04, 1.30, 1.50), COL_SHELF_WOOD)
    for r in range(3):
        rz = 0.62 + r * 0.45
        make_box(f"ZineRack_Rail_{r}", (wall_face - 0.14, 1.90, rz - 0.14),
                 (0.05, 1.30, 0.04), COL_SHELF_DARK)
        for c in range(4):
            cyy = 1.42 + c * 0.32
            tint = (P.NEWSPRINT, P.PAPER, P.PAPER_AGED)[(r * 2 + c) % 3]
            make_box(f"Zine_{r}_{c}", (wall_face - 0.11, cyy, rz), (0.012, 0.24, 0.32), tint)
            make_box(f"Zine_{r}_{c}_Print", (wall_face - 0.12, cyy, rz + 0.05),
                     (0.006, 0.18, 0.10), P.METAL_BLACK)
    # Maya's zine, front and center on top — Label3D scene-side
    make_box("Zine_NewsFromHarmonyCreek", (wall_face - 0.11, 1.90, 2.02),
             (0.014, 0.26, 0.36), P.PAPER)
    make_box("Zine_NewsFromHarmonyCreek_Print", (wall_face - 0.12, 1.90, 2.09),
             (0.006, 0.20, 0.12), P.METAL_BLACK)
    # Price-guide / magazine shelving (shared prop)
    make_magazine_rack("MagRack", (wall_face - 0.18, 3.50, 0.0), count=6)
    # Key-issue display case — frame + felt back + open front
    # (no-glass rule); three slabbed books
    make_box("KeyIssueCase_Frame", (wall_face - 0.06, 5.30, 1.55), (0.12, 1.10, 0.75),
             COL_SHELF_DARK, open_faces={'-X'})
    make_box("KeyIssueCase_Felt", (wall_face - 0.01, 5.30, 1.55), (0.02, 1.00, 0.65), COL_FELT)
    for ki, ktint in enumerate([COMIC_TINTS[2], COMIC_TINTS[0], COMIC_TINTS[4]]):
        kyy = 5.00 + ki * 0.30
        make_box(f"KeyIssue_{ki}_Slab", (wall_face - 0.055, kyy, 1.55),
                 (0.030, 0.24, 0.34), COL_SLAB)
        make_box(f"KeyIssue_{ki}_Cover", (wall_face - 0.088, kyy, 1.54),
                 (0.012, 0.19, 0.28), ktint)
        make_box(f"KeyIssue_{ki}_Tag", (wall_face - 0.088, kyy, 1.32),
                 (0.010, 0.10, 0.05), P.PAPER)
    # The framed grid of nineteen tour posters (rick_cosmic.md V) —
    # last cell is the Philip Daigle retirement-party poster, drawn
    # in her father's hand ("BYO HOPE")
    idx = 0
    for kz in range(4):
        for jy in range(5):
            if idx >= 19:
                break
            py = 6.05 + jy * 0.32
            pz = 1.05 + kz * 0.40
            body = COMIC_TINTS[(idx * 5 + 3) % len(COMIC_TINTS)]
            name = "TourPoster_PhilipRetirement" if idx == 18 else f"TourPoster_{idx}"
            make_box(f"{name}_Frame", (wall_face - 0.015, py, pz), (0.02, 0.26, 0.34),
                     COL_SHELF_DARK)
            make_box(f"{name}_Body", (wall_face - 0.030, py, pz),
                     (0.012, 0.22, 0.30), COL_KRAFT if idx == 18 else body)
            make_box(f"{name}_Print", (wall_face - 0.041, py, pz - 0.08),
                     (0.005, 0.17, 0.08), P.METAL_BLACK)
            idx += 1


# ═════════════════════════════════════════════════════════════════
# SPINNER RACKS — two classic wire spinners flanking the entrance.
# Round pole + tier discs + wire verticals (cylinders at eye level
# per playbook), four face-out comics per tier, crossed topper sign.
# ═════════════════════════════════════════════════════════════════
def build_spinner_racks():
    for p, px in enumerate((-3.05, +3.05)):
        py = 1.55
        make_box(f"Spinner_{p}_Foot_A", (px, py, 0.03), (0.72, 0.08, 0.05), P.METAL_BLACK)
        make_box(f"Spinner_{p}_Foot_B", (px, py, 0.03), (0.08, 0.72, 0.05), P.METAL_BLACK)
        make_cyl(f"Spinner_{p}_Pole", (px, py, 0.90), 0.025, 1.70, P.METAL_STEEL)
        for w, (wx, wy) in enumerate([(0.20, 0.0), (-0.20, 0.0), (0.0, 0.20), (0.0, -0.20)]):
            make_cyl(f"Spinner_{p}_Wire_{w}", (px + wx, py + wy, 0.95),
                     0.004, 1.30, P.METAL_STEEL)
        for t in range(4):
            tz = 0.48 + t * 0.33
            make_cyl(f"Spinner_{p}_Disc_{t}", (px, py, tz - 0.16), 0.20, 0.012,
                     P.METAL_STEEL, segments=12)
            for si in range(4):
                tint = COMIC_TINTS[(p * 3 + t * 2 + si * 5) % len(COMIC_TINTS)]
                if si % 2 == 0:
                    sgn = -1 if si == 0 else +1
                    make_box(f"Spinner_{p}_Comic_{t}_{si}", (px + sgn * 0.17, py, tz),
                             (0.012, 0.20, 0.28), tint)
                else:
                    sgn = -1 if si == 1 else +1
                    make_box(f"Spinner_{p}_Comic_{t}_{si}", (px, py + sgn * 0.17, tz),
                             (0.20, 0.012, 0.28), tint)
        make_cyl(f"Spinner_{p}_Cap", (px, py, 1.77), 0.04, 0.03, P.METAL_STEEL)
        make_box(f"Spinner_{p}_Topper_A", (px, py, 1.90), (0.30, 0.02, 0.14), P.LOTTERY_RED)
        make_box(f"Spinner_{p}_Topper_B", (px, py, 1.90), (0.02, 0.30, 0.14), P.LOTTERY_RED)


# ═════════════════════════════════════════════════════════════════
# CEILING INFRASTRUCTURE — fluorescent banks (the ones Maya turns
# off in sections at close), smoke detector, HVAC (the standard
# clunk), Muzak dome, security camera over the register.
# ═════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    for j in range(4):
        fx = -2.4 if j % 2 == 0 else +2.4
        fy = 2.7 if j < 2 else 5.3
        make_fluorescent_tube_fixture(f"Fluor_{j}", (fx, fy, CEIL), length=1.50, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))
    make_hvac_vent("HVAC", (-3.3, ROOM_D-0.7, CEIL), width=0.80, depth=0.40)
    make_security_camera("SecCam", (0.9, 6.2, CEIL))
    make_ceiling_speaker("Speaker", (-2.4, 4.2, CEIL))


def main():
    clear_scene()
    build_shell()
    build_storefront()
    build_longbox_rows()
    build_counter_zone()
    build_back_wall()
    build_backroom_door()
    build_west_wall()
    build_east_wall()
    build_spinner_racks()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/cosmic_comics_interior.glb"))
    print(f"\n[build_cosmic_comics_interior] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
