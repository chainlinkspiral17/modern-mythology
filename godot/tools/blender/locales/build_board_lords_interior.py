"""Board Lords — Kai's skate shop, Main St, Smolvud OR — vol7 locale.

The building's century of retail is fixed canon (lore/_VOL7_WIKI.md):
Wagner's Hardware 1962-2011, general store 2014-2031, nothing
2031-2034, Board Lords 2034-present. The hardware past must stay
legible in the geometry — original fir plank floor with the ghost
footprints of the old gondola aisles, the tall 1962 hardware
shelving reused for skate inventory, the parts-drawer cabinet
behind the counter, the rolling-ladder rail, and the faded painted
WAGNER'S HARDWARE ghost sign across the upper back wall (Kai's new
BOARD LORDS panel hangs over its east end).

Canon sources for the dressing:
  · godot/resources/scenes/vol7/vol7_ch5_roy.json — the bell over
    the door; the CLOSED/OPEN flip sign; "the small fluorescent
    over the repair counter in the back"; the kettle; "Woke the
    lathe"; the glass on the deck wall (rendered as an open-front
    heritage case per the no-transparency rule); the counter Roy
    puts a hand on; Kai's phone on the counter; the board a kid
    left for a tune-up.
  · vol7_ch9_tuesday.json — the small electric burner (gas cut
    2049); the chipped Tidewater mug; the bench against the front
    window "for parents waiting on repairs"; the back bench + work
    lamp; palette knife / glue syringe / clamps / the maple kept
    since 2049 for repairs; the stool behind the counter; Roy on
    the sidewalk past the laundromat across Main.
  · vol7_ch12_kai.json — the back office (Devon's old desk, a
    chair, two cardboard boxes of bearings on the floor); the kid
    on the bench by the front window.
  · vol7_ch16_shop.json — the small drawer under the register
    where the door notes live; deck wax; bearings sold to a
    vacation renter; the sanderling mural across Main with the
    substrate patch (painted by Janet Halfmoon in '46).
  · lore/_VOL6_VOL7_LOCALES_MANIFEST.md — "Skate gear + zine wall
    + Kai's permanent perch on the counter."

No transparency: storefront windows are OPENINGS with fir frames +
mullions (diner-window rule); the heritage case is frame + open
front; the door is stiles + rails, no glass slab. Text lettering is
scene-side Label3D per the playbook — this script bakes named
vertex-colored panels only (Ghost_LetterBand, BoardLords_SignPanel,
Zine_StaticTruths, ShoeWall_SignBand, ...).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import (make_wall, make_ceiling, make_crown_molding,
                              make_door_hinges)
from _props.store_fixtures import make_register, make_credit_card_terminal
from _props.decor import make_wall_clock, make_floor_plant
from _props.safety import (make_smoke_detector, make_hvac_vent,
                           make_fluorescent_tube_fixture,
                           make_ceiling_speaker)

# ── Shell (kept from the original scaffold — .tscn camera + lights
#    are tuned to this footprint) ─────────────────────────────────
ROOM_W = 9.0; ROOM_D = 7.0; CEIL = 2.8
PAL_WALL = {"wall": (0.42, 0.32, 0.46, 1.0), "baseboard": (0.18, 0.12, 0.20, 1.0)}
COL_WOOD = (0.42, 0.30, 0.52, 1.0)           # purple-stained trim (house style)

# ── 1962 building bones ──────────────────────────────────────────
COL_FIR_FLOOR   = (0.55, 0.42, 0.28, 1.0)    # original fir planks, 90 yrs of finish
COL_FIR_SEAM    = (0.38, 0.28, 0.18, 1.0)
COL_FIR_WORN    = (0.63, 0.51, 0.36, 1.0)    # traffic lane, finish walked off
COL_FIR_SHADOW  = (0.44, 0.32, 0.20, 1.0)    # unfaded floor under the old aisles
COL_OLD_FIR     = (0.34, 0.25, 0.17, 1.0)    # 1962 shelving / storefront frames
COL_OLD_FIR_LT  = (0.48, 0.37, 0.25, 1.0)    # worn edges on the old wood
COL_BRASS       = (0.72, 0.58, 0.28, 1.0)
COL_GHOST_FIELD = (0.72, 0.63, 0.49, 1.0)    # aged sign-paint field
COL_GHOST_INK   = (0.50, 0.27, 0.21, 1.0)    # oxblood letter paint, faded
COL_GHOST_SUB   = (0.42, 0.35, 0.30, 1.0)    # smaller sub-line paint
COL_PAINT_SPILL = (0.44, 0.50, 0.56, 1.0)    # Wagner's paint-dept spill, faded

# ── Board Lords palette (PNW coastal, muted per house rule) ──────
COL_BL_TEAL     = (0.30, 0.52, 0.46, 1.0)    # shop brand
COL_BL_CREAM    = (0.92, 0.88, 0.76, 1.0)
COL_GRIP        = (0.14, 0.13, 0.14, 1.0)
COL_DECK_WOOD   = (0.72, 0.58, 0.40, 1.0)    # natural maple deck
COL_SLAT        = (0.30, 0.26, 0.24, 1.0)    # deck-wall slatwall
COL_SLAT_GROOVE = (0.20, 0.17, 0.16, 1.0)
COL_KRAFT       = (0.74, 0.56, 0.34, 1.0)
COL_STEEL_WORN  = (0.52, 0.52, 0.54, 1.0)
COL_GUM_SOLE    = (0.62, 0.48, 0.32, 1.0)
COL_TIDEWATER   = (0.62, 0.72, 0.76, 1.0)    # the chipped Tidewater mug
COL_CRT_SHELL   = (0.28, 0.27, 0.26, 1.0)
COL_CRT_SCREEN  = (0.16, 0.22, 0.30, 1.0)
COL_CRT_STATIC  = (0.62, 0.68, 0.72, 1.0)

# Deck-art / apparel tints — muted warm-sunset + PNW cool accents
DECK_TINTS = [
    (0.30, 0.52, 0.46, 1.0),   # teal
    (0.78, 0.42, 0.22, 1.0),   # rust
    (0.94, 0.82, 0.52, 1.0),   # cream wheat
    (0.34, 0.42, 0.54, 1.0),   # dusty blue
    (0.32, 0.44, 0.30, 1.0),   # forest
    (0.52, 0.24, 0.20, 1.0),   # oxblood
    (0.24, 0.22, 0.24, 1.0),   # charcoal
    (0.92, 0.62, 0.28, 1.0),   # warm amber
]


# ═════════════════════════════════════════════════════════════════
# SHELL — floor slab is replaced by the wood-floor history pass
# below; walls keep the scaffold footprint. South wall becomes a
# real storefront (openings, not solid wall) in build_storefront.
# North wall splits around the back-office doorway (ch12 canon).
# ═════════════════════════════════════════════════════════════════
def build_shell():
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL,
                  axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    # North wall split around the office doorway (gap x 2.45..3.35)
    make_wall("Wall_N_W", (-1.125, ROOM_D, 0), length=7.15, height=CEIL,
              axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (+4.025, ROOM_D, 0), length=1.35, height=CEIL,
              axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_N_AboveOfficeDoor", (2.90, ROOM_D, CEIL-0.30),
             (0.90, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_WOOD})


# ═════════════════════════════════════════════════════════════════
# FLOOR HISTORY — the original 1962 fir plank floor. Wear lane from
# the door to the counter, two darker "ghost aisle" footprints where
# Wagner's gondola shelving stood for five decades (the floor under
# them never sun-faded), bolt holes at the old rack feet, a faded
# blue-gray paint spill from the hardware store's paint department,
# and the brass WAGNER'S threshold plate still set in the doorway.
# ═════════════════════════════════════════════════════════════════
def build_floor_history():
    # Slab
    make_box("Floor_Slab", (0.0, ROOM_D/2.0, -0.05),
             (ROOM_W+0.4, ROOM_D+0.4, 0.10), COL_FIR_FLOOR)
    # Plank seams — planks run N-S, seams every 0.30 m
    n_seams = 29
    for i in range(n_seams):
        sx = -4.2 + i * 0.30
        make_box(f"Floor_PlankSeam_{i}", (sx, ROOM_D/2.0, 0.0025),
                 (0.014, ROOM_D+0.4, 0.0015), COL_FIR_SEAM)
    # Deterministic butt joints (short cross seams between planks)
    for j in range(12):
        bx = -4.05 + (j * 7 % n_seams) * 0.30
        by = 0.6 + ((j * 5 + 2) % 11) * 0.55
        make_box(f"Floor_ButtJoint_{j}", (bx + 0.15, by, 0.0025),
                 (0.30, 0.012, 0.0015), COL_FIR_SEAM)
    # Wear lane — door to counter, finish walked off since 1962
    make_box("Floor_WearLane_Main", (0.0, 2.6, 0.005),
             (1.30, 4.40, 0.003), COL_FIR_WORN)
    make_box("Floor_WearLane_DeckWall", (-2.10, 3.55, 0.005),
             (2.90, 0.90, 0.003), COL_FIR_WORN)
    make_box("Floor_WearLane_Counter", (1.60, 4.55, 0.005),
             (1.10, 0.90, 0.003), COL_FIR_WORN)
    # Ghost aisle footprints — richer, unfaded floor where the
    # hardware gondolas sat (Wagner's Hardware 1962-2011)
    make_box("Floor_GhostAisle_W", (-2.40, 3.40, 0.0035),
             (0.90, 3.20, 0.002), COL_FIR_SHADOW)
    make_box("Floor_GhostAisle_E", (2.20, 2.20, 0.0035),
             (0.90, 3.00, 0.002), COL_FIR_SHADOW)
    # Bolt holes at the old rack feet — corners + midpoints
    hole_pts = [(-2.80, 1.85), (-2.00, 1.85), (-2.80, 3.40), (-2.00, 3.40),
                (-2.80, 4.95), (-2.00, 4.95),
                (1.80, 0.75), (2.60, 0.75), (1.80, 2.20), (2.60, 2.20),
                (1.80, 3.65), (2.60, 3.65)]
    for hi, (hx, hy) in enumerate(hole_pts):
        make_cyl(f"Floor_BoltHole_{hi}", (hx, hy, 0.004), 0.014, 0.006,
                 (0.12, 0.09, 0.07, 1.0), segments=6)
    # Paint spill — the paint department was along the east wall;
    # a dusty blue-gray splotch soaked into the grain, faded now
    make_box("Floor_PaintSpill_A", (3.45, 1.15, 0.0045),
             (0.42, 0.30, 0.002), COL_PAINT_SPILL)
    make_box("Floor_PaintSpill_B", (3.30, 1.32, 0.0055),
             (0.22, 0.18, 0.001), COL_PAINT_SPILL)
    # Brass threshold plate — "WAGNER'S HDW. CO." cast into the
    # doorway sill in 1962; Kai never took it out
    make_box("Floor_WagnerThreshold", (0.0, 0.28, 0.010),
             (1.70, 0.30, 0.016), COL_BRASS)
    make_box("Floor_WagnerThreshold_Letters", (0.0, 0.28, 0.019),
             (1.10, 0.12, 0.002), (0.48, 0.38, 0.20, 1.0))
    # Entry mat north of the plate
    make_box("EntryMat_Under", (0.0, 1.05, 0.006), (1.90, 1.05, 0.006),
             (0.14, 0.13, 0.13, 1.0))
    make_box("EntryMat", (0.0, 1.05, 0.013), (1.76, 0.92, 0.008), P.RUBBER_MAT)
    make_box("EntryMat_Grit", (0.0, 0.62, 0.017), (1.20, 0.10, 0.002),
             (0.50, 0.44, 0.36, 1.0))


# ═════════════════════════════════════════════════════════════════
# STOREFRONT — real window OPENINGS (diner-window rule: no glass
# slab, frame + mullions only) in the original 1962 fir surrounds.
# Door with stiles/rails, the brass bell (ch5/ch9/ch16: "the bell
# over the door rang"), the CLOSED/OPEN flip sign Kai turns every
# morning at ten, and the bench inside the east window "for parents
# waiting on repairs" (ch9).
# ═════════════════════════════════════════════════════════════════
def build_storefront():
    # Wall pieces around the two window openings + door gap x -1..1
    for tag, sgn in (("W", -1), ("E", +1)):
        make_box(f"Storefront_Bulkhead_{tag}", (sgn * 2.75, 0.0, 0.275),
                 (3.50, 0.20, 0.55), PAL_WALL["wall"])
        make_box(f"Storefront_Bulkhead_{tag}_Base", (sgn * 2.75, 0.13, 0.08),
                 (3.50, 0.06, 0.16), PAL_WALL["baseboard"])
        make_box(f"Storefront_CornerPier_{tag}", (sgn * 4.25, 0.0, 1.45),
                 (0.50, 0.20, 1.80), PAL_WALL["wall"])
        make_box(f"Storefront_DoorPier_{tag}", (sgn * 1.20, 0.0, 1.45),
                 (0.40, 0.20, 1.80), PAL_WALL["wall"])
        make_box(f"Storefront_Header_{tag}", (sgn * 2.75, 0.0, 2.575),
                 (3.50, 0.20, 0.45), PAL_WALL["wall"])
    make_box("Storefront_AboveDoor", (0.0, 0.0, 2.50), (2.00, 0.20, 0.60),
             PAL_WALL["wall"])
    # Window frames — original old-growth fir, dark with age
    for tag, sgn in (("W", -1), ("E", +1)):
        wx = sgn * 2.70
        make_box(f"Window_{tag}_Sill", (wx, 0.0, 0.585), (2.72, 0.16, 0.07), COL_OLD_FIR)
        make_box(f"Window_{tag}_Head", (wx, 0.0, 2.315), (2.72, 0.16, 0.07), COL_OLD_FIR)
        for jsgn in (-1, +1):
            make_box(f"Window_{tag}_Jamb_{jsgn:+d}", (wx + jsgn * 1.325, 0.0, 1.45),
                     (0.07, 0.16, 1.80), COL_OLD_FIR)
        make_box(f"Window_{tag}_Transom", (wx, 0.0, 1.95), (2.60, 0.10, 0.05), COL_OLD_FIR)
        for msgn in (-1, +1):
            make_box(f"Window_{tag}_MullV_{msgn:+d}", (wx + msgn * 0.65, 0.0, 1.45),
                     (0.05, 0.10, 1.73), COL_OLD_FIR)
        # Worn interior stool cap — elbows and shop dogs since 1962
        make_box(f"Window_{tag}_StoolCap", (wx, 0.14, 0.605), (2.60, 0.12, 0.03),
                 COL_OLD_FIR_LT)
    # Door surround + west-hinged leaf (frame + rails, NO glass)
    for sgn in (-1, +1):
        make_box(f"Door_Post_{sgn:+d}", (sgn * 0.96, 0.0, 1.10),
                 (0.08, 0.16, 2.20), COL_OLD_FIR)
    make_box("Door_Transom", (0.0, 0.0, 2.24), (2.00, 0.16, 0.08), COL_OLD_FIR)
    make_box("Door_Stile_W", (-0.88, 0.0, 1.08), (0.07, 0.05, 2.10), COL_OLD_FIR)
    make_box("Door_Stile_E", (-0.12, 0.0, 1.08), (0.07, 0.05, 2.10), COL_OLD_FIR)
    make_box("Door_Rail_Top", (-0.50, 0.0, 2.08), (0.83, 0.05, 0.09), COL_OLD_FIR)
    make_box("Door_Rail_Mid", (-0.50, 0.0, 0.92), (0.83, 0.05, 0.07), COL_OLD_FIR)
    make_box("Door_KickPlate", (-0.50, 0.0, 0.15), (0.83, 0.05, 0.26), P.METAL_STEEL)
    make_cyl("Door_PushBar", (-0.50, 0.07, 1.00), 0.020, 0.62, COL_BRASS, axis='X')
    make_door_hinges("Door_Hinge", edge_x=-0.92, edge_y=0.0,
                     edge_z_centers=[0.35, 1.05, 1.80], axis='X')
    # The CLOSED/OPEN flip sign on a cord (ch5: "He flipped the
    # CLOSED to OPEN") — teal board, cream text band, both faces
    make_cyl("Door_FlipSign_Cord", (-0.50, 0.045, 1.86), 0.004, 0.30, P.TWINE, axis='Z')
    make_box("Door_FlipSign_Board", (-0.50, 0.045, 1.60), (0.36, 0.020, 0.22), COL_BL_TEAL)
    make_box("Door_FlipSign_Text_In", (-0.50, 0.058, 1.60), (0.28, 0.006, 0.09), COL_BL_CREAM)
    make_box("Door_FlipSign_Text_Out", (-0.50, 0.032, 1.60), (0.28, 0.006, 0.09), COL_BL_CREAM)
    # Brass bell above the door — every arrival in ch5/ch9/ch16
    make_box("Bell_Mount", (0.55, 0.13, 2.32), (0.06, 0.10, 0.06), P.METAL_BLACK)
    make_cyl("Bell_Arm", (0.55, 0.24, 2.32), 0.012, 0.16, COL_BRASS, axis='Y')
    make_cyl("Bell_Body", (0.55, 0.32, 2.27), 0.050, 0.07, COL_BRASS)
    make_cyl("Bell_Flare", (0.55, 0.32, 2.22), 0.068, 0.025, COL_BRASS)
    make_cyl("Bell_Clapper", (0.55, 0.32, 2.18), 0.012, 0.05, P.METAL_BLACK)
    # Waiting bench inside the east window (ch9: "the small bench
    # against the front window that Kai kept for parents waiting on
    # repairs"; ch12: the kid with the board across his lap)
    make_box("Bench_Seat", (2.45, 0.42, 0.45), (1.70, 0.38, 0.05), COL_OLD_FIR_LT)
    for lsgn in (-1, +1):
        make_box(f"Bench_Leg_{lsgn:+d}", (2.45 + lsgn * 0.72, 0.42, 0.21),
                 (0.06, 0.34, 0.42), COL_OLD_FIR)
    make_box("Bench_Stretcher", (2.45, 0.42, 0.12), (1.40, 0.05, 0.04), COL_OLD_FIR)
    make_box("Bench_Backpack", (2.95, 0.42, 0.60), (0.26, 0.22, 0.26),
             (0.40, 0.46, 0.34, 1.0))
    make_box("Bench_Backpack_Pocket", (2.95, 0.30, 0.53), (0.18, 0.03, 0.12),
             (0.32, 0.38, 0.28, 1.0))
    make_cyl("Bench_Helmet", (1.95, 0.42, 0.51), 0.11, 0.08, DECK_TINTS[6])
    make_cyl("Bench_Helmet_Crown", (1.95, 0.42, 0.565), 0.08, 0.04, DECK_TINTS[6])
    # Window display platform inside the west window — two decks on
    # stands, a shoe, a fanned sticker pack
    make_box("WinDisp_Platform", (-2.70, 0.50, 0.11), (2.30, 0.70, 0.22), COL_SLAT)
    for di, dx in enumerate((-3.30, -2.35)):
        tint = DECK_TINTS[(di * 3 + 1) % len(DECK_TINTS)]
        make_box(f"WinDisp_Deck_{di}", (dx, 0.50, 0.61), (0.026, 0.205, 0.78), tint)
        make_box(f"WinDisp_Deck_{di}_Art", (dx - 0.015, 0.50, 0.61),
                 (0.004, 0.16, 0.30), DECK_TINTS[(di * 3 + 4) % len(DECK_TINTS)])
        for psgn in (-1, +1):
            make_cyl(f"WinDisp_Stand_{di}_{psgn:+d}", (dx + 0.05, 0.50 + psgn * 0.09, 0.36),
                     0.012, 0.28, P.METAL_BLACK)
    make_box("WinDisp_Shoe_Sole", (-1.75, 0.45, 0.24), (0.28, 0.11, 0.035), COL_GUM_SOLE)
    make_box("WinDisp_Shoe_Upper", (-1.77, 0.45, 0.28), (0.23, 0.10, 0.08), DECK_TINTS[3])
    make_box("WinDisp_PriceCard", (-2.05, 0.38, 0.255), (0.10, 0.014, 0.07), P.PAPER)
    make_box("WinDisp_StickerFan_A", (-3.05, 0.32, 0.225), (0.10, 0.07, 0.004), DECK_TINTS[0])
    make_box("WinDisp_StickerFan_B", (-2.98, 0.36, 0.228), (0.10, 0.07, 0.004), DECK_TINTS[5])
    make_floor_plant("FloorPlant", (3.95, 0.80, 0.0))


# ═════════════════════════════════════════════════════════════════
# MAIN STREET THROUGH THE WINDOWS — the laundromat directly across
# Main with Janet Halfmoon's sanderling mural ('46) and the gray
# substrate patch eating its lower corner (ch5/ch9: "the patch on
# the sanderling mural across from Board Lords"), the downspout the
# drone fixed in ch9, sidewalks, the road, one streetlight on the
# buffer strip (public right-of-way rule).
# ═════════════════════════════════════════════════════════════════
def build_exterior_main_street():
    make_box("Ext_Sidewalk_Near", (0.0, -1.35, -0.06), (16.0, 2.50, 0.12),
             (0.58, 0.56, 0.52, 1.0))
    for si in range(5):
        make_box(f"Ext_Sidewalk_Near_Seam_{si}", (-6.0 + si * 3.0, -1.35, 0.001),
                 (0.03, 2.40, 0.002), (0.42, 0.40, 0.37, 1.0))
    make_box("Ext_Road", (0.0, -4.85, -0.10), (16.0, 4.50, 0.08),
             (0.30, 0.29, 0.30, 1.0))
    for di in range(4):
        make_box(f"Ext_Road_CenterDash_{di}", (-5.4 + di * 3.6, -4.85, -0.058),
                 (1.40, 0.12, 0.004), (0.82, 0.72, 0.36, 1.0))
    make_box("Ext_Road_Patch", (2.6, -3.9, -0.058), (1.60, 0.90, 0.004),
             (0.24, 0.23, 0.24, 1.0))
    make_box("Ext_Sidewalk_Far", (0.0, -7.75, -0.06), (16.0, 1.30, 0.12),
             (0.58, 0.56, 0.52, 1.0))
    # Streetlight at the road edge on the far buffer strip
    make_cyl("Ext_Streetlight_Pole", (-4.5, -7.35, 2.3), 0.06, 4.6,
             (0.24, 0.26, 0.28, 1.0))
    make_box("Ext_Streetlight_Arm", (-4.15, -7.35, 4.55), (0.80, 0.08, 0.06),
             (0.24, 0.26, 0.28, 1.0))
    make_box("Ext_Streetlight_Lens", (-3.85, -7.35, 4.47), (0.30, 0.16, 0.08),
             (0.96, 0.88, 0.62, 1.0))
    # Laundromat — brick, parapet, storefront band
    make_box("Ext_Laundromat_Facade", (0.0, -8.75, 2.2), (16.0, 0.50, 4.4),
             (0.52, 0.38, 0.31, 1.0))
    make_box("Ext_Laundromat_Parapet", (0.0, -8.75, 4.46), (16.2, 0.60, 0.14),
             (0.40, 0.30, 0.25, 1.0))
    make_box("Ext_Laundromat_Band", (0.0, -8.48, 0.30), (16.0, 0.04, 0.60),
             (0.36, 0.32, 0.30, 1.0))
    # Laundromat door + windows (dark openings-with-frames, distant)
    make_box("Ext_Laundromat_Door", (4.1, -8.46, 1.05), (0.95, 0.04, 2.10),
             (0.12, 0.11, 0.12, 1.0))
    make_box("Ext_Laundromat_DoorFrame", (4.1, -8.45, 2.16), (1.10, 0.04, 0.10),
             (0.70, 0.68, 0.62, 1.0))
    for wi, wx in enumerate((5.6, 2.5)):
        make_box(f"Ext_Laundromat_Win_{wi}", (wx, -8.46, 1.45), (1.10, 0.04, 1.30),
                 (0.14, 0.14, 0.16, 1.0))
        make_box(f"Ext_Laundromat_WinFrame_{wi}", (wx, -8.45, 2.14), (1.22, 0.04, 0.08),
                 (0.70, 0.68, 0.62, 1.0))
    # The sanderling mural — small shorebird, wet-sand band, painted
    # by Janet Halfmoon in '46 on the wall Kai checks every morning
    make_box("Ext_Mural_Sky", (-1.6, -8.46, 2.35), (4.20, 0.04, 1.90),
             (0.55, 0.62, 0.64, 1.0))
    make_box("Ext_Mural_SandBand", (-1.6, -8.44, 1.62), (4.20, 0.04, 0.44),
             (0.70, 0.62, 0.50, 1.0))
    make_box("Ext_Mural_Sanderling_Body", (-1.35, -8.42, 2.30), (0.90, 0.03, 0.48),
             (0.88, 0.86, 0.80, 1.0))
    make_box("Ext_Mural_Sanderling_Head", (-0.80, -8.42, 2.62), (0.34, 0.03, 0.30),
             (0.88, 0.86, 0.80, 1.0))
    make_box("Ext_Mural_Sanderling_Beak", (-0.52, -8.42, 2.60), (0.28, 0.03, 0.06),
             (0.20, 0.18, 0.16, 1.0))
    make_box("Ext_Mural_Sanderling_Eye", (-0.76, -8.41, 2.66), (0.05, 0.02, 0.05),
             (0.20, 0.18, 0.16, 1.0))
    make_box("Ext_Mural_Sanderling_Wing", (-1.45, -8.41, 2.32), (0.55, 0.02, 0.26),
             (0.68, 0.64, 0.58, 1.0))
    for li, lx in enumerate((-1.55, -1.15)):
        make_box(f"Ext_Mural_Sanderling_Leg_{li}", (lx, -8.42, 1.95),
                 (0.05, 0.03, 0.26), (0.20, 0.18, 0.16, 1.0))
    # The substrate patch — flat gray-brown, eating the lower-west
    # corner of the mural, "bigger today, maybe" (ch5)
    make_box("Ext_Mural_Patch_A", (-3.05, -8.40, 1.85), (1.30, 0.03, 1.00),
             (0.42, 0.40, 0.38, 1.0))
    make_box("Ext_Mural_Patch_B", (-2.45, -8.39, 1.58), (0.90, 0.03, 0.55),
             (0.45, 0.43, 0.41, 1.0))
    make_box("Ext_Mural_Patch_C", (-3.30, -8.39, 2.45), (0.55, 0.03, 0.45),
             (0.40, 0.38, 0.36, 1.0))
    # The downspout the drone re-hung in ch9
    make_cyl("Ext_Laundromat_Downspout", (6.9, -8.44, 2.1), 0.05, 4.0,
             (0.55, 0.53, 0.50, 1.0))
    for bi in range(3):
        make_box(f"Ext_Downspout_Bracket_{bi}", (6.9, -8.48, 0.8 + bi * 1.5),
                 (0.14, 0.06, 0.05), (0.42, 0.40, 0.38, 1.0))


# ═════════════════════════════════════════════════════════════════
# THE GHOST SIGN — WAGNER'S HARDWARE, painted on the upper back wall
# in 1962, uncovered when the general store's paneling came down.
# Aged paint field, oxblood letter band (Label3D scene-side),
# PAINT · TOOLS · GLASS sub-line, chipped patches where the plaster
# shows through. Kai's BOARD LORDS panel hangs over its east end —
# the new sign literally mounted on the old one.
# ═════════════════════════════════════════════════════════════════
def build_ghost_sign():
    wall_face = ROOM_D - 0.10   # 6.90
    make_box("Ghost_Field", (-0.70, wall_face - 0.015, 2.30),
             (6.40, 0.03, 0.70), COL_GHOST_FIELD)
    make_box("Ghost_LetterBand", (-0.70, wall_face - 0.032, 2.42),
             (5.60, 0.006, 0.30), COL_GHOST_INK)
    make_box("Ghost_SubBand", (-0.70, wall_face - 0.032, 2.10),
             (4.20, 0.006, 0.14), COL_GHOST_SUB)
    # Chips — wall paint showing through the sign field
    chips = [(-3.45, 2.52, 0.40, 0.18), (-2.20, 2.06, 0.30, 0.14),
             (-0.15, 2.58, 0.55, 0.12), (1.30, 2.14, 0.26, 0.20),
             (-1.30, 2.36, 0.18, 0.10)]
    for ci, (cx, cz, w, h) in enumerate(chips):
        make_box(f"Ghost_Chip_{ci}", (cx, wall_face - 0.038, cz),
                 (w, 0.004, h), PAL_WALL["wall"])
    # Water-stain drip down from the crown, across the sign's west end
    make_box("Ghost_WaterStain", (-3.70, wall_face - 0.036, 2.35),
             (0.22, 0.004, 0.72), (0.60, 0.52, 0.40, 1.0))
    # Kai's BOARD LORDS panel — hung 2034, overlapping the ghost
    # sign's east end. Teal field, cream letter band, two brackets.
    make_box("BoardLords_SignPanel", (2.75, wall_face - 0.075, 2.32),
             (2.30, 0.05, 0.52), COL_BL_TEAL)
    make_box("BoardLords_SignLetters", (2.75, wall_face - 0.105, 2.36),
             (1.90, 0.006, 0.24), COL_BL_CREAM)
    make_box("BoardLords_SignRule", (2.75, wall_face - 0.105, 2.16),
             (1.30, 0.006, 0.03), COL_BL_CREAM)
    for bsgn in (-1, +1):
        make_box(f"BoardLords_SignBracket_{bsgn:+d}",
                 (2.75 + bsgn * 0.95, wall_face - 0.045, 2.62),
                 (0.05, 0.09, 0.14), P.METAL_BLACK)


# ═════════════════════════════════════════════════════════════════
# THE DECK WALL — west wall. Slatwall with three rows of six
# face-out decks, varied deck-art blocks (position-seeded pattern
# variety), mounting pegs, price tags. The signature fixture of the
# shop (ch5: Kai cleans it during the first empty hour).
# ═════════════════════════════════════════════════════════════════
def _deck_art(prefix, ax, ay, az, k, tint_b, tint_c):
    """Art blocks proud of a face-out deck at (ax, ay, az). Five
    pattern families keyed by k."""
    if k == 0:      # three horizontal stripes
        for si, dz in enumerate((-0.18, 0.0, +0.18)):
            make_box(f"{prefix}_Stripe_{si}", (ax, ay, az + dz),
                     (0.004, 0.185, 0.07), tint_b)
    elif k == 1:    # split two-tone lower half
        make_box(f"{prefix}_Split", (ax, ay, az - 0.19),
                 (0.004, 0.185, 0.36), tint_b)
        make_box(f"{prefix}_SplitRule", (ax - 0.002, ay, az - 0.005),
                 (0.004, 0.185, 0.025), tint_c)
    elif k == 2:    # center dot
        make_box(f"{prefix}_Dot", (ax, ay, az), (0.004, 0.11, 0.11), tint_b)
        make_box(f"{prefix}_DotCore", (ax - 0.002, ay, az),
                 (0.004, 0.055, 0.055), tint_c)
    elif k == 3:    # border ring
        for bi, (dy, dz, w, h) in enumerate([
                (0.0, +0.34, 0.17, 0.03), (0.0, -0.34, 0.17, 0.03),
                (+0.082, 0.0, 0.025, 0.70), (-0.082, 0.0, 0.025, 0.70)]):
            make_box(f"{prefix}_Border_{bi}", (ax, ay + dy, az + dz),
                     (0.004, w, h), tint_b)
    else:           # nose band + tail band
        make_box(f"{prefix}_NoseBand", (ax, ay, az + 0.28),
                 (0.004, 0.185, 0.12), tint_b)
        make_box(f"{prefix}_TailBand", (ax, ay, az - 0.28),
                 (0.004, 0.185, 0.12), tint_c)

def build_deck_wall():
    wall_face = -ROOM_W / 2.0 + 0.10   # -4.40
    make_box("Deck_Slatwall", (-4.36, 4.70, 1.41), (0.07, 3.60, 2.62), COL_SLAT)
    for gi in range(8):
        gz = 0.35 + gi * 0.30
        make_box(f"Deck_SlatGroove_{gi}", (-4.322, 4.70, gz),
                 (0.006, 3.55, 0.02), COL_SLAT_GROOVE)
    rows_z = (0.72, 1.50, 2.28)
    for col in range(6):
        cy = 3.15 + col * 0.62
        for row, rz in enumerate(rows_z):
            idx = col * 3 + row
            base = DECK_TINTS[idx % len(DECK_TINTS)]
            if idx % 7 == 3:
                base = COL_DECK_WOOD   # a few natural-maple decks
            make_box(f"Deck_{col}_{row}", (-4.300, cy, rz),
                     (0.026, 0.205, 0.78), base)
            _deck_art(f"DeckArt_{col}_{row}", -4.285, cy, rz, idx % 5,
                      DECK_TINTS[(idx * 3 + 2) % len(DECK_TINTS)],
                      DECK_TINTS[(idx * 5 + 5) % len(DECK_TINTS)])
            for psgn in (-1, +1):
                make_cyl(f"Deck_Peg_{col}_{row}_{psgn:+d}",
                         (-4.335, cy + psgn * 0.06, rz - 0.30),
                         0.006, 0.06, P.METAL_STEEL, axis='X', segments=6)
            if idx % 4 == 1:
                make_box(f"Deck_PriceTag_{col}_{row}", (-4.315, cy, rz - 0.46),
                         (0.008, 0.09, 0.05), P.PAPER)


# ═════════════════════════════════════════════════════════════════
# HERITAGE CASE + VIDEO CORNER — "the glass on the deck wall" (ch5)
# rendered as an open-front display cabinet per the no-glass rule.
# Wagner's relics inside (the shop yardstick, a hand-crank drill)
# next to the first Board Lords deck from 2034. On top: the CRT +
# tape deck running skate videos all day, screen facing the room.
# ═════════════════════════════════════════════════════════════════
def build_heritage_case():
    cx, cy = -4.15, 2.20
    make_box("Heritage_Cabinet", (cx, cy, 0.55), (0.50, 1.00, 1.10),
             COL_OLD_FIR, open_faces={'+X'})
    make_box("Heritage_Shelf_Mid", (cx + 0.02, cy, 0.58), (0.44, 0.92, 0.03),
             COL_OLD_FIR_LT)
    make_box("Heritage_Shelf_Low", (cx + 0.02, cy, 0.22), (0.44, 0.92, 0.03),
             COL_OLD_FIR_LT)
    for rsgn in (-1, +1):
        make_box(f"Heritage_Rim_{rsgn:+d}", (cx + 0.24, cy + rsgn * 0.48, 0.55),
                 (0.04, 0.04, 1.10), COL_OLD_FIR)
    make_box("Heritage_Rim_Top", (cx + 0.24, cy, 1.08), (0.04, 1.00, 0.04),
             COL_OLD_FIR)
    # Relics: Wagner's wooden yardstick, the hand-crank drill, and
    # the first Board Lords deck (2034), worn at the tail
    make_box("Heritage_Yardstick", (cx + 0.10, cy, 0.63), (0.05, 0.88, 0.015),
             P.PAPER_AGED)
    make_box("Heritage_Drill_Body", (cx + 0.06, cy - 0.28, 0.68),
             (0.06, 0.22, 0.05), (0.30, 0.28, 0.30, 1.0))
    make_cyl("Heritage_Drill_Wheel", (cx + 0.06, cy - 0.32, 0.72), 0.045, 0.02,
             (0.44, 0.20, 0.16, 1.0), axis='Y')
    make_cyl("Heritage_Drill_Handle", (cx + 0.06, cy - 0.16, 0.70), 0.012, 0.08,
             COL_OLD_FIR_LT, axis='Y', segments=6)
    make_box("Heritage_FirstDeck", (cx + 0.14, cy + 0.22, 0.28),
             (0.026, 0.205, 0.50), DECK_TINTS[5])
    make_box("Heritage_FirstDeck_Wear", (cx + 0.155, cy + 0.22, 0.08),
             (0.004, 0.16, 0.08), COL_DECK_WOOD)
    make_box("Heritage_Card", (cx + 0.20, cy - 0.10, 0.28), (0.008, 0.14, 0.09),
             P.PAPER)
    # CRT + tape deck on top — skate tapes on loop, screen faces east
    make_box("CRT_Body", (cx + 0.02, cy - 0.12, 1.335), (0.44, 0.46, 0.42),
             COL_CRT_SHELL)
    make_box("CRT_Screen", (cx + 0.245, cy - 0.12, 1.36), (0.012, 0.35, 0.28),
             COL_CRT_SCREEN)
    make_box("CRT_Screen_Static", (cx + 0.253, cy - 0.12, 1.44), (0.006, 0.32, 0.03),
             COL_CRT_STATIC)
    make_box("CRT_Screen_Skater", (cx + 0.253, cy - 0.20, 1.33), (0.006, 0.05, 0.09),
             COL_CRT_STATIC)
    make_box("CRT_Screen_RampLine", (cx + 0.253, cy - 0.04, 1.29), (0.006, 0.16, 0.02),
             (0.48, 0.54, 0.58, 1.0))
    make_cyl("CRT_Knob", (cx + 0.245, cy + 0.13, 1.24), 0.020, 0.02,
             P.METAL_BLACK, axis='X', segments=6)
    make_box("CRT_TapeDeck", (cx + 0.02, cy + 0.32, 1.155), (0.40, 0.28, 0.09),
             (0.20, 0.19, 0.20, 1.0))
    make_box("CRT_TapeDeck_Slot", (cx + 0.225, cy + 0.32, 1.16), (0.005, 0.18, 0.03),
             (0.08, 0.08, 0.09, 1.0))
    for vi in range(3):
        make_box(f"CRT_Tape_{vi}", (cx + 0.02, cy + 0.44 - vi * 0.0, 1.24 + vi * 0.045),
                 (0.19, 0.11, 0.038),
                 (0.20, 0.18, 0.22, 1.0) if vi % 2 == 0 else (0.26, 0.20, 0.30, 1.0))
    make_box("CRT_Cable", (cx + 0.02, cy + 0.18, 1.14), (0.012, 0.16, 0.012),
             P.METAL_BLACK)


# ═════════════════════════════════════════════════════════════════
# ZINE WALL — pocket rack by the window end of the west wall
# (locales manifest: "zine wall"). Local photocopied stock; Lena's
# STATIC TRUTHS face-out on the top rail (Label3D scene-side).
# ═════════════════════════════════════════════════════════════════
def build_zine_wall():
    wall_face = -ROOM_W / 2.0 + 0.10
    make_box("Zine_Back", (wall_face + 0.02, 0.90, 1.15), (0.04, 0.85, 1.10),
             COL_OLD_FIR)
    for r in range(3):
        rz = 0.78 + r * 0.36
        make_box(f"Zine_Rail_{r}", (wall_face + 0.10, 0.90, rz - 0.12),
                 (0.05, 0.85, 0.04), COL_OLD_FIR_LT)
        for c in range(2):
            zy = 0.70 + c * 0.40
            tint = (P.NEWSPRINT, P.PAPER, P.PAPER_AGED)[(r * 2 + c) % 3]
            make_box(f"Zine_{r}_{c}", (wall_face + 0.08, zy, rz),
                     (0.012, 0.22, 0.30), tint)
            make_box(f"Zine_{r}_{c}_Print", (wall_face + 0.088, zy, rz + 0.05),
                     (0.006, 0.16, 0.09), P.METAL_BLACK)
    make_box("Zine_StaticTruths", (wall_face + 0.08, 0.90, 1.62),
             (0.014, 0.24, 0.34), P.PAPER)
    make_box("Zine_StaticTruths_Print", (wall_face + 0.09, 0.90, 1.69),
             (0.006, 0.18, 0.11), P.METAL_BLACK)


# ═════════════════════════════════════════════════════════════════
# REPAIR ZONE — north wall, west side. The back bench with the work
# lamp (ch9), the lathe Kai "wakes" every morning (ch5), the vise,
# the deck mid-repair under two C-clamps, glue bottle + syringe +
# palette knife (the ch9 Tess Mariana repair kit), the maple blank
# kept since 2049, the pegboard with painted tool silhouettes
# (hardware-store discipline that never left the building), and the
# repair-queue rack holding the board a kid left for a tune-up (ch5).
# ═════════════════════════════════════════════════════════════════
def build_repair_zone():
    wall_face = ROOM_D - 0.10   # 6.90
    bx, by = -2.80, 6.60
    # Bench — heavy fir top on old frame legs, lower shelf
    make_box("Repair_BenchTop", (bx, by, 0.95), (2.80, 0.62, 0.06), COL_OLD_FIR_LT)
    make_box("Repair_BenchApron", (bx, by - 0.26, 0.86), (2.70, 0.05, 0.10), COL_OLD_FIR)
    for li, (lx, ly) in enumerate([(-4.05, 6.38), (-1.55, 6.38),
                                   (-4.05, 6.82), (-1.55, 6.82)]):
        make_box(f"Repair_BenchLeg_{li}", (lx, ly, 0.46), (0.08, 0.08, 0.92), COL_OLD_FIR)
    make_box("Repair_BenchShelf", (bx, by, 0.26), (2.60, 0.54, 0.04), COL_OLD_FIR)
    # Lower shelf stock: the maple kept since 2049, clamp bin, grip sheets
    make_box("Repair_MapleBlank", (-3.60, by, 0.32), (0.60, 0.18, 0.08), COL_DECK_WOOD)
    make_box("Repair_MapleBlank_Label", (-3.60, by - 0.095, 0.32), (0.10, 0.008, 0.05),
             P.PAPER_AGED)
    make_box("Repair_ClampBin", (-2.75, by, 0.36), (0.44, 0.34, 0.16), COL_KRAFT,
             open_faces={'+Z'})
    for ci in range(3):
        make_box(f"Repair_BinClamp_{ci}", (-2.88 + ci * 0.14, by, 0.42),
                 (0.05, 0.26, 0.05), COL_STEEL_WORN)
    make_box("Repair_GripSheets", (-2.05, by, 0.31), (0.55, 0.24, 0.05), COL_GRIP)
    # Vise at the west end
    make_box("Repair_Vise_Base", (-3.90, by - 0.10, 1.01), (0.16, 0.20, 0.06),
             COL_STEEL_WORN)
    make_box("Repair_Vise_Jaws", (-3.90, by - 0.14, 1.10), (0.14, 0.16, 0.12),
             (0.38, 0.38, 0.42, 1.0))
    make_cyl("Repair_Vise_Handle", (-3.90, by - 0.26, 1.06), 0.010, 0.18,
             COL_STEEL_WORN, axis='X', segments=6)
    # The lathe (ch5: "Woke the lathe") — benchtop unit, east end
    make_box("Lathe_Bed", (-1.75, by, 1.005), (0.62, 0.16, 0.05), COL_STEEL_WORN)
    make_box("Lathe_Headstock", (-2.00, by, 1.11), (0.12, 0.16, 0.16),
             (0.34, 0.36, 0.40, 1.0))
    make_cyl("Lathe_Spindle", (-1.88, by, 1.14), 0.020, 0.14, COL_STEEL_WORN,
             axis='X')
    make_box("Lathe_Tailstock", (-1.52, by, 1.09), (0.09, 0.14, 0.12),
             (0.34, 0.36, 0.40, 1.0))
    make_box("Lathe_ToolRest", (-1.76, by - 0.11, 1.09), (0.22, 0.03, 0.03),
             COL_STEEL_WORN)
    make_box("Lathe_Motor", (-2.02, by + 0.14, 1.05), (0.14, 0.10, 0.10),
             P.METAL_BLACK)
    make_box("Lathe_Sawdust", (-1.75, by - 0.16, 0.985), (0.50, 0.16, 0.008),
             (0.80, 0.68, 0.48, 1.0))
    make_box("Lathe_Sawdust_Floor", (-1.75, 6.20, 0.006), (0.40, 0.30, 0.004),
             (0.80, 0.68, 0.48, 1.0))
    # Deck mid-repair, clamped (the ch9 pattern: glue, clamp, wait)
    make_box("Repair_Deck", (-3.05, by - 0.02, 0.99), (0.78, 0.205, 0.02),
             COL_DECK_WOOD)
    make_box("Repair_Deck_CrackLine", (-2.95, by - 0.02, 1.001), (0.30, 0.012, 0.002),
             (0.30, 0.22, 0.14, 1.0))
    for csgn in (-1, +1):
        ccx = -3.05 + csgn * 0.26
        make_box(f"Repair_CClamp_Spine_{csgn:+d}", (ccx, by - 0.02, 1.03),
                 (0.03, 0.05, 0.14), COL_STEEL_WORN)
        make_box(f"Repair_CClamp_TopJaw_{csgn:+d}", (ccx + 0.03, by - 0.02, 1.085),
                 (0.09, 0.05, 0.03), COL_STEEL_WORN)
        make_box(f"Repair_CClamp_BotJaw_{csgn:+d}", (ccx + 0.03, by - 0.02, 0.965),
                 (0.09, 0.05, 0.03), COL_STEEL_WORN)
        make_cyl(f"Repair_CClamp_Screw_{csgn:+d}", (ccx + 0.06, by - 0.02, 0.93),
                 0.008, 0.07, P.METAL_BLACK, segments=6)
    # Glue bottle, syringe, palette knife, rag
    make_cyl("Repair_GlueBottle", (-2.55, by + 0.12, 1.05), 0.035, 0.14,
             (0.86, 0.78, 0.52, 1.0))
    make_cyl("Repair_GlueCap", (-2.55, by + 0.12, 1.135), 0.014, 0.03,
             (0.78, 0.42, 0.22, 1.0), segments=6)
    make_cyl("Repair_Syringe", (-2.38, by + 0.10, 0.995), 0.008, 0.14,
             (0.82, 0.84, 0.86, 1.0), axis='X', segments=6)
    make_box("Repair_PaletteKnife_Blade", (-2.22, by + 0.16, 0.99),
             (0.12, 0.03, 0.004), COL_STEEL_WORN)
    make_box("Repair_PaletteKnife_Handle", (-2.13, by + 0.16, 0.995),
             (0.06, 0.025, 0.02), COL_OLD_FIR)
    make_box("Repair_Rag", (-3.55, by + 0.14, 0.99), (0.20, 0.16, 0.025),
             (0.56, 0.50, 0.44, 1.0))
    # Work lamp (ch9: "turned on the work lamp") — post + arm + shade
    make_cyl("Repair_Lamp_Post", (-3.35, by + 0.22, 1.20), 0.014, 0.44,
             P.METAL_BLACK, segments=6)
    make_box("Repair_Lamp_Arm", (-3.22, by + 0.22, 1.42), (0.28, 0.03, 0.03),
             P.METAL_BLACK)
    make_cyl("Repair_Lamp_Shade", (-3.08, by + 0.22, 1.37), 0.085, 0.11,
             (0.24, 0.30, 0.28, 1.0))
    make_cyl("Repair_Lamp_Bulb", (-3.08, by + 0.22, 1.315), 0.055, 0.015,
             (1.0, 0.94, 0.78, 1.0))
    # Pegboard with painted tool silhouettes (Wagner's habit)
    make_box("Peg_Board", (bx, wall_face - 0.015, 1.85), (2.60, 0.03, 1.10),
             (0.52, 0.44, 0.34, 1.0))
    make_box("Peg_Board_Frame_T", (bx, wall_face - 0.02, 2.42), (2.66, 0.03, 0.05),
             COL_OLD_FIR)
    make_box("Peg_Board_Frame_B", (bx, wall_face - 0.02, 1.28), (2.66, 0.03, 0.05),
             COL_OLD_FIR)
    # Screwdrivers ×3 — shaft + handle, hanging vertical
    for si in range(3):
        sx = -3.85 + si * 0.22
        make_box(f"Peg_Shadow_SD_{si}", (sx, wall_face - 0.032, 1.95),
                 (0.05, 0.004, 0.30), (0.40, 0.33, 0.25, 1.0))
        make_cyl(f"Peg_SD_Shaft_{si}", (sx, wall_face - 0.05, 1.88), 0.006, 0.16,
                 COL_STEEL_WORN, segments=6)
        make_cyl(f"Peg_SD_Handle_{si}", (sx, wall_face - 0.05, 2.02), 0.016, 0.09,
                 DECK_TINTS[(si * 2 + 1) % len(DECK_TINTS)], segments=6)
    # Wrenches ×2
    for wi in range(2):
        wx2 = -3.10 + wi * 0.20
        make_box(f"Peg_Shadow_WR_{wi}", (wx2, wall_face - 0.032, 1.90),
                 (0.06, 0.004, 0.36), (0.40, 0.33, 0.25, 1.0))
        make_box(f"Peg_WR_Bar_{wi}", (wx2, wall_face - 0.05, 1.88),
                 (0.03, 0.015, 0.28), COL_STEEL_WORN)
        make_box(f"Peg_WR_Head_{wi}", (wx2, wall_face - 0.05, 2.045),
                 (0.055, 0.015, 0.05), COL_STEEL_WORN)
    # Skate T-tool
    make_box("Peg_Shadow_TT", (-2.55, wall_face - 0.032, 1.92),
             (0.16, 0.004, 0.22), (0.40, 0.33, 0.25, 1.0))
    make_box("Peg_TT_Bar", (-2.55, wall_face - 0.05, 2.00), (0.14, 0.02, 0.03),
             DECK_TINTS[0])
    make_box("Peg_TT_Stem", (-2.55, wall_face - 0.05, 1.90), (0.03, 0.02, 0.17),
             DECK_TINTS[0])
    # Hammer
    make_box("Peg_Shadow_HM", (-2.20, wall_face - 0.032, 1.92),
             (0.10, 0.004, 0.34), (0.40, 0.33, 0.25, 1.0))
    make_box("Peg_HM_Handle", (-2.20, wall_face - 0.05, 1.88), (0.03, 0.02, 0.28),
             COL_OLD_FIR_LT)
    make_box("Peg_HM_Head", (-2.20, wall_face - 0.05, 2.045), (0.10, 0.035, 0.05),
             COL_STEEL_WORN)
    # Hand saw
    make_box("Peg_Shadow_SAW", (-1.80, wall_face - 0.032, 1.90),
             (0.14, 0.004, 0.42), (0.40, 0.33, 0.25, 1.0))
    make_box("Peg_SAW_Blade", (-1.80, wall_face - 0.05, 1.84), (0.07, 0.006, 0.34),
             COL_STEEL_WORN)
    make_box("Peg_SAW_Handle", (-1.80, wall_face - 0.05, 2.08), (0.09, 0.025, 0.10),
             COL_OLD_FIR)
    # Blue painter's tape + bearing grease tin on the low rail
    make_cyl("Peg_TapeRoll", (-3.55, wall_face - 0.07, 1.42), 0.05, 0.045,
             (0.34, 0.42, 0.54, 1.0), axis='Y')
    make_cyl("Peg_GreaseTin", (-2.05, wall_face - 0.08, 1.40), 0.045, 0.06,
             (0.44, 0.46, 0.42, 1.0), axis='Y')
    # Repair-queue rack, NW corner of the west wall — the tune-up
    # board from ch5 + one more, kraft claim tags
    make_box("Queue_Rail", (-4.34, 6.45, 1.55), (0.06, 0.70, 0.05), COL_OLD_FIR)
    for qi, qy in enumerate((6.25, 6.62)):
        make_box(f"Queue_Deck_{qi}", (-4.30, qy, 1.10), (0.026, 0.205, 0.78),
                 DECK_TINTS[(qi * 4 + 3) % len(DECK_TINTS)])
        make_box(f"Queue_Tag_{qi}", (-4.28, qy + 0.05, 1.44), (0.010, 0.07, 0.09),
                 COL_KRAFT)
    # Grip-tape roll rack on the wall east of the pegboard — rods
    # face the room so the rolls read as circles at eye level
    make_box("Grip_Backplate", (-0.95, wall_face - 0.015, 1.50), (0.95, 0.03, 0.55),
             COL_SLAT)
    for gi in range(3):
        gx = -1.23 + gi * 0.28
        make_cyl(f"Grip_Rod_{gi}", (gx, wall_face - 0.18, 1.50), 0.010, 0.32,
                 P.METAL_STEEL, axis='Y', segments=6)
        make_cyl(f"Grip_Roll_{gi}", (gx, wall_face - 0.24, 1.50),
                 0.13 if gi != 1 else 0.115, 0.10, COL_GRIP, axis='Y')
        make_cyl(f"Grip_Core_{gi}", (gx, wall_face - 0.295, 1.50), 0.045, 0.012,
                 COL_KRAFT, axis='Y', segments=6)


# ═════════════════════════════════════════════════════════════════
# COUNTER ZONE — the counter Roy put a hand on (ch5). Register with
# the note drawer under it (ch16: the folded pieces of paper taken
# off the door over the years), Kai's phone, the token terminal,
# deck-wax crate, sticker jar, Kai's permanent perch cushion
# (locales manifest), the stool (ch9), and behind it the side table
# with the electric burner (gas cut 2049), the kettle, and the
# chipped Tidewater mug Devon left.
# ═════════════════════════════════════════════════════════════════
def build_counter_zone():
    cx, cy = 2.35, 5.40
    make_box("Counter_Body", (cx, cy, 0.475), (1.50, 0.80, 0.95), COL_OLD_FIR)
    make_box("Counter_Top", (cx, cy, 0.98), (1.66, 0.92, 0.06), COL_OLD_FIR_LT)
    make_box("Counter_Kick", (cx, cy - 0.41, 0.10), (1.50, 0.02, 0.20),
             P.COUNTER_DARK)
    make_cyl("Counter_Bullnose", (cx, cy - 0.46, 0.96), 0.025, 1.60,
             COL_OLD_FIR_LT, axis='X')
    top_z = 1.01
    make_register("RegisterMachine", (2.00, cy - 0.05, top_z),
                  palette={"body": (0.30, 0.29, 0.30, 1.0)})
    make_credit_card_terminal("TokenTerminal", (2.55, cy - 0.25, top_z))
    # The note drawer under the register — slightly open, clerk
    # side, folded paper slips inside (ch16 canon)
    make_box("Counter_NoteDrawer", (2.00, cy + 0.44, 0.70), (0.32, 0.10, 0.16),
             COL_OLD_FIR_LT, open_faces={'+Z'})
    make_cyl("Counter_NoteDrawer_Knob", (2.00, cy + 0.50, 0.70), 0.012, 0.03,
             COL_BRASS, axis='Y', segments=6)
    for ni in range(3):
        make_box(f"Counter_NoteSlip_{ni}", (1.93 + ni * 0.07, cy + 0.44, 0.775),
                 (0.05, 0.07, 0.012), P.PAPER_AGED if ni % 2 else P.PAPER)
    # Kai's phone, face-up by the register (ch5: "picked up his
    # phone from the counter")
    make_box("Counter_Phone", (2.85, cy - 0.20, top_z + 0.006),
             (0.075, 0.155, 0.012), P.METAL_BLACK)
    make_box("Counter_Phone_Screen", (2.85, cy - 0.20, top_z + 0.013),
             (0.065, 0.135, 0.002), (0.12, 0.14, 0.18, 1.0))
    # Deck-wax crate + pucks (ch16: the Saturday rush bought wax)
    make_box("Counter_WaxCrate", (1.78, cy - 0.28, top_z + 0.045),
             (0.22, 0.22, 0.09), COL_KRAFT, open_faces={'+Z'})
    for wi in range(4):
        make_cyl(f"Counter_WaxPuck_{wi}", (1.72 + (wi % 2) * 0.11,
                 cy - 0.33 + (wi // 2) * 0.10, top_z + 0.075), 0.038, 0.035,
                 DECK_TINTS[(wi * 3 + 2) % len(DECK_TINTS)], segments=6)
    # Sticker tin — open tin of slaps by the terminal
    make_cyl("Counter_StickerTin", (2.28, cy - 0.30, top_z + 0.055), 0.065, 0.11,
             (0.58, 0.60, 0.62, 1.0))
    for si2 in range(3):
        make_box(f"Counter_TinSticker_{si2}", (2.24 + si2 * 0.04, cy - 0.30,
                 top_z + 0.12 + si2 * 0.008), (0.06, 0.045, 0.004),
                 DECK_TINTS[(si2 * 2 + 1) % len(DECK_TINTS)])
    # Kai's perch — the flattened cushion on the counter's east end
    make_box("Counter_KaiPerch_Cushion", (2.98, cy + 0.18, top_z + 0.016),
             (0.36, 0.36, 0.032), (0.30, 0.28, 0.30, 1.0))
    make_box("Counter_KaiPerch_Dent", (2.98, cy + 0.18, top_z + 0.034),
             (0.24, 0.24, 0.004), (0.24, 0.22, 0.24, 1.0))
    # Stool behind the counter (ch9: "sat down on the stool")
    make_cyl("Counter_Stool_Seat", (2.00, 6.10, 0.72), 0.17, 0.05,
             (0.36, 0.28, 0.24, 1.0))
    for li2, (lx2, ly2) in enumerate([(-0.10, -0.10), (0.10, -0.10),
                                      (-0.10, 0.10), (0.10, 0.10)]):
        make_cyl(f"Counter_Stool_Leg_{li2}", (2.00 + lx2, 6.10 + ly2, 0.35),
                 0.014, 0.70, P.METAL_BLACK, segments=6)
    make_box("Counter_Stool_Ring", (2.00, 6.10, 0.22), (0.26, 0.26, 0.02),
             P.METAL_BLACK, open_faces={'+Z', '-Z'})
    # Back table — burner + kettle + the chipped Tidewater mug
    make_box("BackTable_Top", (1.00, 6.60, 0.78), (0.70, 0.50, 0.04), COL_OLD_FIR_LT)
    for bli, (blx, bly) in enumerate([(0.72, 6.42), (1.28, 6.42),
                                      (0.72, 6.78), (1.28, 6.78)]):
        make_box(f"BackTable_Leg_{bli}", (blx, bly, 0.39), (0.05, 0.05, 0.78),
                 COL_OLD_FIR)
    make_cyl("BackTable_Burner", (0.88, 6.60, 0.825), 0.11, 0.05,
             (0.22, 0.21, 0.22, 1.0))
    make_cyl("BackTable_Burner_Coil", (0.88, 6.60, 0.853), 0.08, 0.008,
             (0.34, 0.30, 0.30, 1.0))
    make_cyl("Kettle_Body", (0.88, 6.60, 0.94), 0.10, 0.16,
             (0.62, 0.64, 0.66, 1.0), segments=10)
    make_cyl("Kettle_Lid", (0.88, 6.60, 1.03), 0.045, 0.03,
             (0.52, 0.54, 0.56, 1.0), segments=8)
    make_box("Kettle_Spout", (1.00, 6.60, 0.99), (0.09, 0.03, 0.03),
             (0.62, 0.64, 0.66, 1.0))
    make_box("Kettle_Handle_A", (0.80, 6.60, 1.06), (0.03, 0.02, 0.05),
             P.METAL_BLACK)
    make_box("Kettle_Handle_B", (0.865, 6.60, 1.085), (0.16, 0.02, 0.02),
             P.METAL_BLACK)
    # The chipped Tidewater mug (ch9) — chip = bare ceramic at the rim
    make_cyl("Mug_Tidewater", (1.22, 6.55, 0.845), 0.042, 0.09, COL_TIDEWATER)
    make_box("Mug_Tidewater_Band", (1.22, 6.508, 0.85), (0.05, 0.006, 0.03),
             COL_BL_CREAM)
    make_box("Mug_Tidewater_Chip", (1.255, 6.55, 0.885), (0.014, 0.02, 0.014),
             (0.90, 0.88, 0.84, 1.0))
    make_box("Mug_Tidewater_Handle", (1.28, 6.55, 0.845), (0.02, 0.014, 0.055),
             COL_TIDEWATER)


# ═════════════════════════════════════════════════════════════════
# BACK OFFICE DOORWAY — ch12: Devon's old desk against the wall,
# the chair Devon also left, two cardboard boxes of bearings on the
# floor. Door standing open against the recess wall; the bearings
# boxes sit just inside where the doorway sightline catches them.
# ═════════════════════════════════════════════════════════════════
def build_office_door():
    dx = 2.90
    for psgn in (-1, +1):
        make_box(f"Office_Post_{psgn:+d}", (dx + psgn * 0.49, ROOM_D - 0.05, 1.10),
                 (0.08, 0.14, 2.20), COL_OLD_FIR)
    make_box("Office_Header", (dx, ROOM_D - 0.06, 2.26), (1.10, 0.10, 0.12),
             COL_OLD_FIR)
    make_box("Office_Recess", (dx, ROOM_D + 0.55, 1.10), (0.94, 0.90, 2.20),
             (0.07, 0.06, 0.09, 1.0))
    # Door leaf standing open, flat against the recess's east side
    make_box("Office_DoorLeaf", (3.32, ROOM_D + 0.42, 1.08), (0.04, 0.72, 2.10),
             COL_WOOD)
    make_cyl("Office_DoorKnob", (3.29, ROOM_D + 0.68, 1.02), 0.022, 0.04,
             COL_BRASS, axis='X', segments=6)
    # Devon's desk edge + the two bearings boxes (ch12), catching
    # the light just inside the doorway
    make_box("Office_DeskEdge", (2.62, ROOM_D + 0.35, 0.37), (0.42, 0.30, 0.05),
             (0.24, 0.19, 0.15, 1.0))
    make_box("Office_DeskLeg", (2.46, ROOM_D + 0.30, 0.17), (0.05, 0.05, 0.34),
             (0.20, 0.16, 0.13, 1.0))
    make_box("Office_BearingsBox_0", (2.72, ROOM_D + 0.16, 0.11),
             (0.30, 0.26, 0.22), COL_KRAFT)
    make_box("Office_BearingsBox_1", (2.72, ROOM_D + 0.16, 0.27),
             (0.26, 0.22, 0.10), (0.66, 0.48, 0.28, 1.0))


# ═════════════════════════════════════════════════════════════════
# TRUCKS / WHEELS CASE — open-front display case west of the
# counter (frame + rims, no glass). Trucks on the top shelf, wheel
# four-packs and bearings tins below, paper price cards.
# ═════════════════════════════════════════════════════════════════
def build_wheels_case():
    cx, cy = 0.70, 5.375
    make_box("Wheels_Base", (cx, cy, 0.14), (1.20, 0.55, 0.28), P.COUNTER_DARK)
    for pi, (px, py) in enumerate([(0.13, 5.13), (1.27, 5.13),
                                   (0.13, 5.62), (1.27, 5.62)]):
        make_box(f"Wheels_Post_{pi}", (px, py, 0.61), (0.05, 0.05, 0.66),
                 COL_OLD_FIR)
    make_box("Wheels_Rim_F", (cx, 5.13, 0.955), (1.19, 0.04, 0.04), COL_OLD_FIR)
    make_box("Wheels_Rim_B", (cx, 5.62, 0.955), (1.19, 0.04, 0.04), COL_OLD_FIR)
    for rsgn in (-1, +1):
        make_box(f"Wheels_Rim_Side_{rsgn:+d}", (cx + rsgn * 0.57, cy, 0.955),
                 (0.04, 0.53, 0.04), COL_OLD_FIR)
    make_box("Wheels_BackPanel", (cx, 5.635, 0.60), (1.14, 0.03, 0.63), COL_SLAT)
    make_box("Wheels_Shelf_Low", (cx, cy, 0.50), (1.10, 0.48, 0.03),
             COL_OLD_FIR_LT)
    make_box("Wheels_Shelf_Top", (cx, cy, 0.84), (1.10, 0.48, 0.03),
             COL_OLD_FIR_LT)
    # Trucks ×4 on the top shelf — baseplate + hanger + axle + kingpin
    for ti in range(4):
        tx = 0.28 + ti * 0.28
        make_box(f"Truck_Base_{ti}", (tx, cy, 0.87), (0.10, 0.07, 0.02),
                 COL_STEEL_WORN)
        make_box(f"Truck_Hanger_{ti}", (tx, cy - 0.02, 0.905), (0.13, 0.035, 0.035),
                 (0.60, 0.62, 0.66, 1.0))
        make_cyl(f"Truck_Axle_{ti}", (tx, cy - 0.02, 0.905), 0.007, 0.20,
                 P.METAL_STEEL, axis='X', segments=6)
        make_cyl(f"Truck_Kingpin_{ti}", (tx, cy + 0.015, 0.90), 0.008, 0.05,
                 P.METAL_BLACK, segments=6)
    # Wheel four-packs ×5 on the lower shelf — faces toward the room
    for wi in range(5):
        wx = 0.22 + wi * 0.24
        tint = DECK_TINTS[(wi * 3 + 2) % len(DECK_TINTS)]
        for wj in range(4):
            make_cyl(f"Wheel_{wi}_{wj}", (wx - 0.054 + wj * 0.036, cy - 0.10, 0.545),
                     0.028, 0.032, tint, axis='Y')
        make_box(f"Wheel_Band_{wi}", (wx, cy - 0.10, 0.575), (0.15, 0.07, 0.014),
                 P.PAPER)
    # Bearings tins ×3 at the back of the lower shelf
    for bi in range(3):
        make_cyl(f"Bearings_Tin_{bi}", (0.35 + bi * 0.35, cy + 0.14, 0.535),
                 0.035, 0.035, COL_STEEL_WORN, segments=8)
        make_box(f"Bearings_Label_{bi}", (0.35 + bi * 0.35, cy + 0.10, 0.535),
                 (0.05, 0.006, 0.03), P.PAPER_AGED)
    make_box("Wheels_PriceCard_A", (0.24, 5.115, 0.99), (0.09, 0.012, 0.06), P.PAPER)
    make_box("Wheels_PriceCard_B", (1.10, 5.115, 0.99), (0.09, 0.012, 0.06), P.PAPER)


# ═════════════════════════════════════════════════════════════════
# CENTER ISLAND — the oak display table left over from Wagner's
# Hardware, now carrying folded tees, beanies, and the odd-wheels
# basket. Worn edges where seventy years of hands have been.
# ═════════════════════════════════════════════════════════════════
def build_center_island():
    ix, iy = 0.0, 3.0
    make_box("Island_Top", (ix, iy, 0.75), (2.40, 1.00, 0.05), COL_OLD_FIR)
    make_box("Island_TopWear", (ix, iy - 0.47, 0.777), (2.30, 0.05, 0.004),
             COL_OLD_FIR_LT)
    make_box("Island_Apron", (ix, iy, 0.68), (2.28, 0.90, 0.06), COL_OLD_FIR)
    for li, (lx, ly) in enumerate([(-1.08, 2.62), (1.08, 2.62),
                                   (-1.08, 3.38), (1.08, 3.38)]):
        make_box(f"Island_Leg_{li}", (lx, ly, 0.36), (0.09, 0.09, 0.72), COL_OLD_FIR)
    make_box("Island_LowShelf", (ix, iy, 0.18), (2.20, 0.84, 0.04), COL_OLD_FIR_LT)
    # Folded tee stacks ×4
    for si in range(4):
        sx = -0.85 + si * 0.56
        for layer in range(3):
            tint = DECK_TINTS[(si * 3 + layer * 2 + 1) % len(DECK_TINTS)]
            make_box(f"Island_TeeStack_{si}_{layer}",
                     (sx, iy - 0.22, 0.80 + layer * 0.05),
                     (0.34, 0.28, 0.045), tint)
    # Beanie stack
    for bi in range(3):
        make_cyl(f"Island_Beanie_{bi}", (0.95, iy + 0.26, 0.80 + bi * 0.055),
                 0.085, 0.05, DECK_TINTS[(bi * 2 + 4) % len(DECK_TINTS)])
    # Odd-wheels basket — "2 FOR 1" card scene-side
    make_box("Island_WheelBasket", (-0.78, iy + 0.24, 0.84), (0.44, 0.36, 0.17),
             COL_KRAFT, open_faces={'+Z'})
    for wi in range(6):
        wx = -0.92 + (wi % 3) * 0.14
        wy = iy + 0.17 + (wi // 3) * 0.14
        make_cyl(f"Island_OddWheel_{wi}", (wx, wy, 0.895 + (wi % 2) * 0.02),
                 0.028, 0.032, DECK_TINTS[(wi * 5 + 2) % len(DECK_TINTS)],
                 axis='Y' if wi % 2 == 0 else 'X')
    make_box("Island_SaleCard", (-0.78, iy + 0.05, 0.945), (0.14, 0.012, 0.09),
             P.PAPER)
    # Overstock kraft box on the low shelf
    make_box("Island_Overstock", (0.55, iy, 0.32), (0.60, 0.44, 0.24), COL_KRAFT)


# ═════════════════════════════════════════════════════════════════
# APPAREL RACK — single rail, west-center floor. Tees and two
# hoodies on hangers, PNW-muted tints, chest prints on a few.
# ═════════════════════════════════════════════════════════════════
def build_apparel_rack():
    ry, rz = 4.70, 1.48
    for psgn, px in ((-1, -2.65), (+1, -0.75)):
        make_cyl(f"Rack_Post_{psgn:+d}", (px, ry, 0.74), 0.020, 1.48,
                 P.METAL_BLACK, segments=6)
        make_box(f"Rack_Foot_{psgn:+d}", (px, ry, 0.02), (0.10, 0.55, 0.04),
                 P.METAL_BLACK)
    make_cyl("Rack_Rail", (-1.70, ry, rz), 0.016, 1.90, P.METAL_STEEL, axis='X')
    for gi in range(8):
        gx = -2.44 + gi * 0.21
        tint = DECK_TINTS[(gi * 3 + 2) % len(DECK_TINTS)]
        make_cyl(f"Rack_Hanger_{gi}", (gx, ry, rz - 0.03), 0.006, 0.06,
                 P.METAL_STEEL, segments=6)
        make_box(f"Rack_Shoulders_{gi}", (gx, ry, rz - 0.09), (0.03, 0.38, 0.05),
                 tint)
        make_box(f"Rack_GarmentBody_{gi}", (gx, ry, rz - 0.40), (0.028, 0.34, 0.56),
                 tint)
        if gi in (2, 6):   # hoodies get a hood bump
            make_box(f"Rack_Hood_{gi}", (gx, ry + 0.05, rz - 0.02),
                     (0.032, 0.16, 0.10), tint)
        if gi in (1, 4, 7):    # chest print
            make_box(f"Rack_Print_{gi}", (gx + 0.016, ry, rz - 0.28),
                     (0.004, 0.14, 0.10), COL_BL_CREAM)
    make_box("Rack_SizeCard", (-1.70, ry, rz + 0.10), (0.16, 0.012, 0.08), P.PAPER)


# ═════════════════════════════════════════════════════════════════
# SHOE WALL — east wall, south section. Flat fir shelves with nine
# display shoes, shoebox stacks below, teal SHOES band (Label3D
# scene-side).
# ═════════════════════════════════════════════════════════════════
def build_shoe_wall():
    wall_face = ROOM_W / 2.0 - 0.10   # 4.40
    make_box("Shoe_BackPanel", (wall_face - 0.015, 1.50, 1.30), (0.03, 1.60, 1.60),
             COL_SLAT)
    make_box("ShoeWall_SignBand", (wall_face - 0.035, 1.50, 2.02),
             (0.006, 1.10, 0.16), COL_BL_TEAL)
    for sh in range(3):
        shz = 0.68 + sh * 0.46
        make_box(f"Shoe_Shelf_{sh}", (wall_face - 0.16, 1.50, shz),
                 (0.32, 1.55, 0.03), COL_OLD_FIR_LT)
        for c in range(3):
            sy = 1.05 + c * 0.45
            tint = DECK_TINTS[(sh * 3 + c * 2 + 1) % len(DECK_TINTS)]
            make_box(f"Shoe_Sole_{sh}_{c}", (wall_face - 0.17, sy, shz + 0.033),
                     (0.28, 0.115, 0.035), COL_GUM_SOLE)
            make_box(f"Shoe_Upper_{sh}_{c}", (wall_face - 0.155, sy, shz + 0.09),
                     (0.235, 0.10, 0.08), tint)
            make_box(f"Shoe_Toe_{sh}_{c}", (wall_face - 0.27, sy, shz + 0.075),
                     (0.06, 0.095, 0.05), (0.86, 0.82, 0.74, 1.0))
            make_box(f"Shoe_Laces_{sh}_{c}", (wall_face - 0.20, sy, shz + 0.128),
                     (0.10, 0.08, 0.008), (0.90, 0.88, 0.82, 1.0))
            if (sh + c) % 3 == 0:
                make_box(f"Shoe_PriceCard_{sh}_{c}", (wall_face - 0.31, sy, shz + 0.02),
                         (0.012, 0.07, 0.045), P.PAPER)
    # Shoebox stacks under the bottom shelf
    for bi in range(3):
        bx2 = 1.05 + bi * 0.45
        make_box(f"Shoe_BoxStack_A_{bi}", (wall_face - 0.18, bx2, 0.12),
                 (0.30, 0.34, 0.12), COL_KRAFT)
        make_box(f"Shoe_BoxStack_B_{bi}", (wall_face - 0.18, bx2, 0.25),
                 (0.30, 0.32, 0.11), DECK_TINTS[(bi * 3 + 6) % len(DECK_TINTS)])
        make_box(f"Shoe_BoxLabel_{bi}", (wall_face - 0.34, bx2, 0.19),
                 (0.012, 0.10, 0.05), P.PAPER)


# ═════════════════════════════════════════════════════════════════
# WAGNER'S HARDWARE SHELVING — the original 1962 tall fir shelving
# unit, east wall, reused for skate inventory. Worn shelf edges,
# steel label holders with aged paper, a stencilled AISLE 3 still
# on the upright, two leftover paint cans on the top shelf, and the
# rolling-ladder rail with the ladder stowed at its north end.
# ═════════════════════════════════════════════════════════════════
def build_hardware_shelving():
    wall_face = ROOM_W / 2.0 - 0.10   # 4.40
    ux = 4.19                          # unit centerline x
    for ui, uy in enumerate((2.75, 4.00, 5.25)):
        make_box(f"HW_Upright_{ui}", (ux, uy, 1.275), (0.42, 0.06, 2.55),
                 COL_OLD_FIR)
    make_box("HW_TopCap", (ux, 4.00, 2.565), (0.44, 2.56, 0.05), COL_OLD_FIR)
    make_box("HW_Kick", (ux - 0.19, 4.00, 0.07), (0.03, 2.45, 0.14),
             (0.22, 0.16, 0.11, 1.0))
    # Stencil on the south upright — AISLE 3 in worn paint
    make_box("HW_AisleStencil", (ux - 0.215, 2.75, 1.80), (0.006, 0.05, 0.30),
             COL_GHOST_INK)
    shelf_zs = (0.30, 0.90, 1.50, 2.10)
    for si, shz in enumerate(shelf_zs):
        make_box(f"HW_Shelf_{si}", (ux, 4.00, shz), (0.40, 2.42, 0.04),
                 COL_OLD_FIR)
        make_box(f"HW_ShelfWearEdge_{si}", (ux - 0.195, 4.00, shz + 0.012),
                 (0.012, 2.36, 0.016), COL_OLD_FIR_LT)
        make_box(f"HW_LabelHolder_{si}", (ux - 0.205, 4.00, shz - 0.035),
                 (0.006, 2.30, 0.035), COL_STEEL_WORN)
        for lj in range(3):
            make_box(f"HW_Label_{si}_{lj}", (ux - 0.210, 3.05 + lj * 0.95,
                     shz - 0.035), (0.004, 0.18, 0.028), P.PAPER_AGED)
    # Shelf 0 (z 0.30): flat deck stack + kraft cartons
    for di in range(6):
        make_box(f"HW_DeckStack_{di}", (ux - 0.02, 3.35 + (di % 2) * 0.02,
                 0.335 + di * 0.017), (0.21, 0.79, 0.014),
                 DECK_TINTS[(di * 3 + 1) % len(DECK_TINTS)])
    make_box("HW_Carton_0", (ux - 0.01, 4.65, 0.46), (0.34, 0.55, 0.28), COL_KRAFT)
    # Shelf 1 (z 0.90): shoeboxes + bearings cartons + a jar of odd bolts
    for bi2 in range(3):
        make_box(f"HW_ShoeBox_{bi2}", (ux - 0.01, 3.10 + bi2 * 0.40, 0.985),
                 (0.32, 0.34, 0.125), DECK_TINTS[(bi2 * 2 + 3) % len(DECK_TINTS)])
    make_box("HW_BearingsCarton_0", (ux - 0.01, 4.55, 0.98), (0.28, 0.24, 0.12),
             COL_KRAFT)
    make_box("HW_BearingsCarton_1", (ux - 0.01, 4.85, 0.98), (0.28, 0.24, 0.12),
             (0.66, 0.48, 0.28, 1.0))
    make_cyl("HW_BoltJar", (ux - 0.05, 3.55, 1.00), 0.055, 0.14,
             (0.55, 0.50, 0.42, 1.0), segments=8)
    # Shelf 2 (z 1.50): wheel boxes + spray cans
    for wi2 in range(4):
        make_box(f"HW_WheelBox_{wi2}", (ux - 0.01, 3.05 + wi2 * 0.32, 1.585),
                 (0.26, 0.26, 0.13), P.PAPER if wi2 % 2 == 0 else COL_KRAFT)
        make_box(f"HW_WheelBoxBand_{wi2}", (ux - 0.145, 3.05 + wi2 * 0.32, 1.585),
                 (0.006, 0.20, 0.06), DECK_TINTS[(wi2 * 5 + 2) % len(DECK_TINTS)])
    for ci2 in range(4):
        make_cyl(f"HW_SprayCan_{ci2}", (ux - 0.05, 4.45 + ci2 * 0.15, 1.60),
                 0.030, 0.16, DECK_TINTS[(ci2 * 3 + 4) % len(DECK_TINTS)],
                 segments=8)
        make_cyl(f"HW_SprayCap_{ci2}", (ux - 0.05, 4.45 + ci2 * 0.15, 1.70),
                 0.020, 0.03, (0.80, 0.80, 0.78, 1.0), segments=6)
    # Shelf 3 (z 2.10): overstock + the two Wagner's paint cans
    make_box("HW_Overstock_0", (ux - 0.01, 3.30, 2.25), (0.34, 0.60, 0.26),
             COL_KRAFT)
    make_box("HW_Overstock_1", (ux - 0.01, 4.10, 2.22), (0.32, 0.50, 0.20),
             (0.68, 0.50, 0.30, 1.0))
    for pi2 in range(2):
        pcy = 4.70 + pi2 * 0.22
        make_cyl(f"HW_PaintCan_{pi2}", (ux - 0.03, pcy, 2.21), 0.075, 0.17,
                 COL_STEEL_WORN, segments=8)
        make_box(f"HW_PaintCan_Label_{pi2}", (ux - 0.11, pcy, 2.21),
                 (0.006, 0.10, 0.10), P.PAPER_AGED)
        make_box(f"HW_PaintCan_Drip_{pi2}", (ux - 0.108, pcy + 0.03, 2.15),
                 (0.004, 0.03, 0.05), COL_PAINT_SPILL)
    # Rolling-ladder rail + stowed ladder (hardware bones)
    make_cyl("HW_LadderRail", (ux - 0.26, 4.00, 2.46), 0.018, 2.40, COL_BRASS,
             axis='Y')
    for bi3, byy in enumerate((2.90, 4.00, 5.10)):
        make_box(f"HW_RailBracket_{bi3}", (ux - 0.14, byy, 2.46),
                 (0.22, 0.04, 0.04), P.METAL_BLACK)
    for ssgn, sy2 in ((-1, 4.83), (+1, 5.07)):
        make_box(f"HW_Ladder_Stile_{ssgn:+d}", (ux - 0.30, sy2, 1.38),
                 (0.035, 0.05, 1.90), COL_OLD_FIR_LT)
    for ri in range(6):
        make_cyl(f"HW_Ladder_Rung_{ri}", (ux - 0.30, 4.95, 0.60 + ri * 0.32),
                 0.013, 0.20, COL_OLD_FIR_LT, axis='Y', segments=6)
    for hsgn, hy in ((-1, 4.83), (+1, 5.07)):
        make_box(f"HW_Ladder_Hook_{hsgn:+d}", (ux - 0.28, hy, 2.38),
                 (0.05, 0.04, 0.10), P.METAL_BLACK)


# ═════════════════════════════════════════════════════════════════
# PARTS-DRAWER CABINET — Wagner's small-parts cabinet behind the
# counter, 24 drawers relabelled for bearings / bolts / bushings /
# kingpins. One drawer open with bearings inside. The old counter
# scale still sits on top.
# ═════════════════════════════════════════════════════════════════
def build_parts_cabinet():
    wall_face = ROOM_W / 2.0 - 0.10
    px, py = 4.22, 6.15
    make_box("Parts_Body", (px, py, 0.75), (0.35, 1.10, 1.50), COL_OLD_FIR)
    make_box("Parts_TopCap", (px, py, 1.515), (0.38, 1.14, 0.03), COL_OLD_FIR_LT)
    for r in range(6):
        for c in range(4):
            dy = py - 0.405 + c * 0.27
            dz = 0.22 + r * 0.22
            tone = COL_OLD_FIR_LT if (r + c) % 2 == 0 else (0.42, 0.32, 0.22, 1.0)
            make_box(f"Parts_Drawer_{r}_{c}", (px - 0.185, dy, dz),
                     (0.02, 0.24, 0.19), tone)
            make_cyl(f"Parts_Knob_{r}_{c}", (px - 0.20, dy, dz), 0.010, 0.02,
                     COL_BRASS, axis='X', segments=6)
            make_box(f"Parts_LabelFrame_{r}_{c}", (px - 0.197, dy, dz + 0.055),
                     (0.004, 0.09, 0.035), P.PAPER_AGED)
    # One drawer pulled open — bearings visible
    make_box("Parts_OpenDrawer", (px - 0.32, py + 0.135, 1.10), (0.24, 0.24, 0.17),
             (0.42, 0.32, 0.22, 1.0), open_faces={'+Z'})
    for bi in range(3):
        make_cyl(f"Parts_OpenBearing_{bi}", (px - 0.38 + bi * 0.06, py + 0.135, 1.185),
                 0.016, 0.008, COL_STEEL_WORN, segments=8)
    # The old counter scale on top — base, column, pan, dial face
    make_box("Scale_Base", (px - 0.02, py - 0.25, 1.565), (0.24, 0.30, 0.07),
             (0.44, 0.20, 0.16, 1.0))
    make_cyl("Scale_Column", (px - 0.02, py - 0.14, 1.70), 0.022, 0.20,
             (0.44, 0.20, 0.16, 1.0), segments=8)
    make_cyl("Scale_Pan", (px - 0.02, py - 0.34, 1.635), 0.10, 0.02,
             COL_STEEL_WORN, segments=10)
    make_cyl("Scale_Dial", (px - 0.02, py - 0.135, 1.82), 0.075, 0.03,
             (0.90, 0.88, 0.80, 1.0), axis='Y')
    make_box("Scale_Needle", (px - 0.02, py - 0.155, 1.84), (0.008, 0.006, 0.05),
             P.METAL_BLACK)


# ═════════════════════════════════════════════════════════════════
# WALL DRESSING — the shop clock frozen at 10:00 (Kai opens at ten,
# every day, ch5/ch9), a skate poster, the framed black-and-white
# photo of the building as Wagner's Hardware (1975), and the
# opening-day Polaroid from 2034 beside it.
# ═════════════════════════════════════════════════════════════════
def build_wall_dressing():
    wall_face = ROOM_D - 0.10
    make_wall_clock("Clock", (4.00, wall_face - 0.03, 2.45),
                    frozen_hour=10, frozen_min=0)
    # Skate poster — sky band, ramp, rider (baked blocks)
    make_box("Poster_Skate_Body", (0.35, wall_face - 0.02, 1.50),
             (0.50, 0.010, 0.70), (0.24, 0.28, 0.34, 1.0))
    make_box("Poster_Skate_Sky", (0.35, wall_face - 0.028, 1.68),
             (0.44, 0.006, 0.28), (0.55, 0.62, 0.64, 1.0))
    make_box("Poster_Skate_Ramp", (0.42, wall_face - 0.028, 1.36),
             (0.28, 0.006, 0.18), (0.42, 0.40, 0.38, 1.0))
    make_box("Poster_Skate_Rider", (0.28, wall_face - 0.034, 1.62),
             (0.06, 0.004, 0.10), COL_BL_CREAM)
    make_box("Poster_Skate_Title", (0.35, wall_face - 0.034, 1.22),
             (0.36, 0.004, 0.08), COL_BL_TEAL)
    # The building as Wagner's Hardware, 1975 — B&W print, fir frame
    make_box("Photo_Wagner1975_Frame", (1.75, wall_face - 0.015, 1.55),
             (0.42, 0.012, 0.34), COL_OLD_FIR)
    make_box("Photo_Wagner1975_Print", (1.75, wall_face - 0.025, 1.55),
             (0.36, 0.006, 0.28), (0.78, 0.76, 0.72, 1.0))
    make_box("Photo_Wagner1975_Building", (1.73, wall_face - 0.030, 1.51),
             (0.24, 0.004, 0.14), (0.38, 0.37, 0.36, 1.0))
    make_box("Photo_Wagner1975_Awning", (1.73, wall_face - 0.033, 1.575),
             (0.26, 0.003, 0.03), (0.52, 0.50, 0.48, 1.0))
    # Opening-day Polaroid, 2034
    make_box("Photo_Opening2034_Frame", (2.12, wall_face - 0.015, 1.44),
             (0.11, 0.010, 0.13), P.PAPER)
    make_box("Photo_Opening2034_Print", (2.12, wall_face - 0.022, 1.455),
             (0.09, 0.004, 0.09), (0.40, 0.44, 0.42, 1.0))


# ═════════════════════════════════════════════════════════════════
# STICKERS EVERYWHERE — slaps on the door leaf, the window piers,
# the counter face, the wheels case, the island apron, the bench
# apron, the parts cabinet and the CRT. Position-seeded sizes and
# tints; a third get a contrast core block.
# ═════════════════════════════════════════════════════════════════
def build_stickers():
    # (x, y, z, plane) — plane is the axis the sticker faces along
    spots = [
        # door leaf, interior face (below the mid rail)
        (-0.72, 0.030, 0.62, 'Y'), (-0.50, 0.030, 0.48, 'Y'),
        (-0.30, 0.030, 0.70, 'Y'), (-0.58, 0.030, 0.30, 'Y'),
        # door piers, interior faces
        (-1.20, 0.105, 1.10, 'Y'), (-1.20, 0.105, 1.60, 'Y'),
        (+1.20, 0.105, 1.25, 'Y'), (+1.20, 0.105, 1.78, 'Y'),
        # counter customer face
        (1.85, 4.995, 0.72, 'Y'), (2.10, 4.995, 0.50, 'Y'),
        (2.38, 4.995, 0.80, 'Y'), (2.62, 4.995, 0.38, 'Y'),
        (2.90, 4.995, 0.66, 'Y'), (2.25, 4.995, 0.26, 'Y'),
        # wheels case base front
        (0.42, 5.095, 0.20, 'Y'), (0.78, 5.095, 0.12, 'Y'),
        (1.05, 5.095, 0.22, 'Y'),
        # island apron, south face
        (-0.55, 2.545, 0.68, 'Y'), (0.62, 2.545, 0.66, 'Y'),
        # repair bench apron
        (-3.35, 6.315, 0.86, 'Y'), (-2.30, 6.315, 0.86, 'Y'),
        # parts cabinet south side
        (4.22, 5.595, 1.05, 'Y'), (4.22, 5.595, 0.72, 'Y'),
        # CRT south side + shoe shelf edge (faces west)
        (-4.13, 1.905, 1.30, 'Y'), (4.075, 1.85, 0.665, 'X'),
    ]
    for i, (sx, sy, sz, plane) in enumerate(spots):
        w = 0.07 + (i * 3 % 5) * 0.012
        h = 0.05 + (i * 7 % 4) * 0.014
        tint = DECK_TINTS[(i * 5 + 1) % len(DECK_TINTS)]
        core = DECK_TINTS[(i * 3 + 4) % len(DECK_TINTS)]
        if plane == 'Y':
            face_sgn = -1.0 if sy > 3.0 else +1.0
            make_box(f"Sticker_{i}", (sx, sy + face_sgn * 0.004, sz),
                     (w, 0.006, h), tint)
            if i % 3 == 0:
                make_box(f"Sticker_{i}_Core", (sx, sy + face_sgn * 0.008, sz),
                         (w * 0.5, 0.004, h * 0.5), core)
        else:
            make_box(f"Sticker_{i}", (sx - 0.004, sy, sz), (0.006, w, h), tint)
            if i % 3 == 0:
                make_box(f"Sticker_{i}_Core", (sx - 0.008, sy, sz),
                         (0.004, w * 0.5, h * 0.5), core)


# ═════════════════════════════════════════════════════════════════
# CEILING INFRASTRUCTURE — four tube banks for the floor, plus the
# small fluorescent over the repair counter that Kai turns on first
# thing every morning (ch5/ch16: "turned on the back light over the
# repair bench"). Smoke detector, HVAC, the speaker that plays
# whatever tape is in the deck.
# ═════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    for j, (fx, fy) in enumerate([(-2.4, 2.4), (+2.4, 2.4),
                                  (-2.4, 4.9), (+2.4, 4.9)]):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (fx, fy, CEIL),
                                      length=1.40, width=0.34)
    make_fluorescent_tube_fixture("Fluor_RepairBench", (-2.8, 6.55, CEIL),
                                  length=1.10, width=0.26)
    make_smoke_detector("Smoke", (0.0, 3.5, CEIL))
    make_hvac_vent("HVAC", (-3.85, 6.30, CEIL), width=0.80, depth=0.40)
    make_ceiling_speaker("Speaker", (3.0, 3.2, CEIL))


def main():
    clear_scene()
    build_shell()
    build_floor_history()
    build_storefront()
    build_exterior_main_street()
    build_ghost_sign()
    build_deck_wall()
    build_heritage_case()
    build_zine_wall()
    build_repair_zone()
    build_counter_zone()
    build_office_door()
    build_wheels_case()
    build_center_island()
    build_apparel_rack()
    build_shoe_wall()
    build_hardware_shelving()
    build_parts_cabinet()
    build_wall_dressing()
    build_stickers()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/board_lords_interior.glb"))
    print(f"\n[build_board_lords_interior] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
