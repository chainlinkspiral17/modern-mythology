"""Pit Stop Diner — the back office — vol6 hero pass.

The room where Ben's legal pad lives. Same venue as
build_pit_stop_interior.py (one venue, two GLBs — the PITSTOP_*
palette block below is byte-identical in both files).

Binding scenes (grep "3d:pit_stop_office" — 2 VN scenes):
  · vol6_ch0_prelude L63-74 ("Pit Stop Diner · Back Office · 06:17")
    — "the desk that used to be Rick's father's desk, in the chair
    that has been reupholstered twice, looking at a legal pad."
    Careful block letters, pen down / pen up. (Binding adjudication:
    this beat used to be served by the cosmic_comics_back_office
    GLB — see that build's docstring, "ch0 Pit Stop office" — but
    ch0 now binds 3d:pit_stop_office directly; this room owns it.)
  · vol6_ch3_pit_stop_office (Tue 15:48) — "Ben is at the small
    desk in the back office"; the seven-item list; "He puts the
    list in the bottom drawer of the desk, beneath the folded
    apron. He closes the drawer." Off-scene regulars: Brenda the
    morning manager works in here (ch6), so the room also carries
    the manager clutter — punch clock, time cards, safe, schedule
    corkboard.

Reading the canon into geometry:
  · The desk: an old double-pedestal OAK desk (it "used to be
    Rick's father's desk" — decades-old oak, same species as the
    Cosmic Comics register wood), brass pulls, an old inkwell ring
    stain on the top. Desk_Drawer_Bottom_E is the named bottom
    drawer — CLOSED, list + folded apron canon-occluded inside.
  · The chair: "reupholstered twice" — wooden swivel chair whose
    seat and back cushions are two DIFFERENT fabrics (rust vinyl
    seat, mustard back), neither matching the wood.
  · The legal pad (LegalPad_Page — block lettering is scene-side
    Label3D) + pen, dead center of the desk. No computer, no
    monitor: both ch0 and ch3 are pen-on-paper scenes and nothing
    ever names a machine — the scaffold's floating Monitor is
    removed, not reseated.
  · Wall clock frozen at 6:17 — ch0's "the only hour in the day
    that belongs entirely to the diner."

Canon-negatives:
  · NO window — never named; a strip-mall back office off the
    kitchen (the scaffold had none either; kept deliberate).
  · NO computer / monitor (see above).
  · ONE door (to the kitchen), one desk, one filing cabinet.

Scaffold audit (playbook 2026-07-02 — openings/intersections first):
  · Both filing cabinets sat 15 cm EMBEDDED in the west wall
    (centers x -1.7/-1.2, faces to -1.95 vs. wall face -1.9) —
    replaced with ONE cabinet, proud of the wall.
  · Monitor floated 14 cm above the desk slab (same bug class the
    cosmic back office had) — removed entirely (canon-negative).
  · Desk was a 4 cm slab with no pedestals, no drawers — the ch3
    bottom drawer physically didn't exist. Rebuilt.
  · No chair in a room whose scenes are all about sitting at the
    desk — built.
  · Door gap had no frame, no leaf — framed, leaf parked open
    against the south wall (camera shoots through the gap).
  · make_ceiling default stains land OUTSIDE a 4 m-wide room
    (x=+3) — stains disabled, one placed by hand.

Shell footprint kept from the scaffold (4 x 5 x 2.6) — the .tscn
camera preset (Background3D.gd "pit_stop_office": south-doorway
establishing shot at 2.30 m, fov 60) is tuned to it; the north wall
(desk wall) is the backdrop and the south gap stays clear.

Text is scene-side Label3D; named panels baked here: LegalPad_Page,
TimeCard_{0..7}, Corkboard_Sheet_{0..5}, HealthCert_Paper,
BreakerPanel_Label, Office_DoorSign.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import (make_floor, make_wall, make_ceiling,
                              make_door_hinges)
from _props.decor import make_wall_clock, make_calendar
from _props.safety import (make_smoke_detector, make_hvac_vent,
                           make_fluorescent_tube_fixture)

# ── Shell (kept from the scaffold — camera + lights tuned to it) ──
ROOM_W = 4.0; ROOM_D = 5.0; CEIL = 2.6

# ═════════════════════════════════════════════════════════════════
# PITSTOP_* — Pit Stop Diner venue palette. KEEP IN SYNC: this block
# is byte-identical in build_pit_stop_interior.py and
# build_pit_stop_office.py (one venue, two GLBs — md5-verify after
# any edit, per the Miller-house / Foxhole multi-room rule).
# ═════════════════════════════════════════════════════════════════
PITSTOP_CREAM      = (0.93, 0.88, 0.76, 1.0)   # painted walls
PITSTOP_CREAM_AGED = (0.85, 0.78, 0.64, 1.0)   # grease-adjacent wall tone
PITSTOP_RED        = (0.62, 0.18, 0.16, 1.0)   # booth vinyl / brand oxblood
PITSTOP_RED_WORN   = (0.70, 0.34, 0.26, 1.0)   # sun-worn vinyl / table edging
PITSTOP_FORMICA    = (0.76, 0.66, 0.46, 1.0)   # counter + table tops
PITSTOP_TOP_DARK   = (0.20, 0.15, 0.13, 1.0)   # counter top laminate
PITSTOP_WOOD       = (0.52, 0.36, 0.22, 1.0)   # oak trim / the office desk
PITSTOP_WOOD_DARK  = (0.33, 0.22, 0.14, 1.0)
PITSTOP_STAINLESS  = (0.70, 0.71, 0.72, 1.0)   # kitchen line steel
PITSTOP_STEEL_DK   = (0.44, 0.45, 0.47, 1.0)
PITSTOP_FLOOR      = (0.82, 0.76, 0.62, 1.0)   # tan linoleum
PITSTOP_FLOOR_SEAM = (0.58, 0.51, 0.40, 1.0)
PITSTOP_CHECKER    = (0.48, 0.16, 0.14, 1.0)   # dark-red checker tiles
PITSTOP_MINT       = (0.62, 0.76, 0.68, 1.0)   # 50s mint accent trim
PITSTOP_LEGAL_PAD  = (0.94, 0.86, 0.44, 1.0)   # Ben's legal pad (ch0/ch3)
PITSTOP_APRON      = (0.90, 0.88, 0.82, 1.0)   # bib aprons
PITSTOP_BRASS      = (0.78, 0.62, 0.30, 1.0)   # door bell + pass bell
PITSTOP_DAY_SKY    = (0.98, 0.92, 0.72, 1.0)   # Texas summer daylight outside
PITSTOP_ASPHALT    = (0.30, 0.30, 0.32, 1.0)   # strip-mall lot
PITSTOP_STRIPE     = (0.88, 0.86, 0.78, 1.0)   # lot striping
PITSTOP_PICKUP_BLK = (0.10, 0.10, 0.11, 1.0)   # the Louisiana pickup (ch2/ch3)
PITSTOP_COINWASH   = (0.70, 0.78, 0.82, 1.0)   # Coin Wash facade next door (ch7)
PITSTOP_GREASE     = (0.34, 0.28, 0.20, 1.0)   # grill patina / dumpster grime
# ═══════════════════════ end shared block ════════════════════════

PAL_WALL = {"wall": PITSTOP_CREAM_AGED, "baseboard": PITSTOP_WOOD_DARK}

# Locals (this room only)
COL_MUSTARD_FAB = (0.72, 0.56, 0.24, 1.0)   # 2nd reupholstery fabric
COL_RUST_FAB    = (0.66, 0.34, 0.22, 1.0)   # 1st reupholstery fabric
COL_CORK        = (0.72, 0.58, 0.38, 1.0)
COL_KRAFT       = (0.72, 0.55, 0.34, 1.0)
COL_BINDERS     = [(0.34, 0.42, 0.54, 1.0), (0.56, 0.58, 0.42, 1.0),
                   (0.68, 0.32, 0.20, 1.0), (0.52, 0.40, 0.26, 1.0)]


# ═════════════════════════════════════════════════════════════════
# SHELL — floor (older, scuffed), walls with 70s wood-panel
# wainscot, ceiling. South door gap x -1..+1 stays clear.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0),
               size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": PITSTOP_FLOOR, "seam": PITSTOP_FLOOR_SEAM})
    for i, (sx, sy) in enumerate([(0.0, 1.0), (0.3, 2.2), (-0.2, 3.0),
                                  (0.1, 3.6)]):
        make_box(f"Floor_Scuff_{i}", (sx, sy, 0.008), (0.30, 0.20, 0.001),
                 P.FLOOR_SCUFF)
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1),
                      ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
                  axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W / 4.0 + 0.5), 0.0, 0),
              length=ROOM_W / 2.0 - 1.0, height=CEIL, axis='X',
              palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W / 4.0 + 0.5), 0.0, 0),
              length=ROOM_W / 2.0 - 1.0, height=CEIL, axis='X',
              palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.30), (2.0, 0.20, 0.60),
             PITSTOP_CREAM_AGED)
    # 70s wood-panel wainscot on W / N / E (the office cave)
    make_box("Wainscot_W", (-1.88, 2.5, 0.50), (0.03, 5.0, 1.00),
             PITSTOP_WOOD)
    make_box("Wainscot_E", (+1.88, 2.5, 0.50), (0.03, 5.0, 1.00),
             PITSTOP_WOOD)
    make_box("Wainscot_N", (0.0, 4.88, 0.50), (3.8, 0.03, 1.00),
             PITSTOP_WOOD)
    for i in range(9):
        wy = 0.30 + i * 0.55
        make_box(f"Wainscot_W_Batten_{i}", (-1.865, wy, 0.50),
                 (0.035, 0.04, 1.00), PITSTOP_WOOD_DARK)
        make_box(f"Wainscot_E_Batten_{i}", (+1.865, wy, 0.50),
                 (0.035, 0.04, 1.00), PITSTOP_WOOD_DARK)
    for i in range(7):
        wx = -1.65 + i * 0.55
        make_box(f"Wainscot_N_Batten_{i}", (wx, 4.865, 0.50),
                 (0.04, 0.035, 1.00), PITSTOP_WOOD_DARK)
    make_box("Wainscot_W_Rail", (-1.86, 2.5, 1.02), (0.045, 5.0, 0.05),
             PITSTOP_WOOD_DARK)
    make_box("Wainscot_E_Rail", (+1.86, 2.5, 1.02), (0.045, 5.0, 0.05),
             PITSTOP_WOOD_DARK)
    make_box("Wainscot_N_Rail", (0.0, 4.86, 1.02), (3.8, 0.045, 0.05),
             PITSTOP_WOOD_DARK)
    # Stains land outside a 4 m room with the helper defaults —
    # place the one water stain by hand instead
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL),
                 size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4, with_stains=False)
    make_box("Ceil_Stain_0", (-1.1, 3.8, CEIL + 0.025), (0.70, 0.70, 0.003),
             P.CEILING_STAIN)


# ═════════════════════════════════════════════════════════════════
# THE DESK — Rick's father's old oak double-pedestal desk (ch0),
# against the north wall (the camera backdrop). Bottom-east drawer
# is THE drawer (ch3: the list, beneath the folded apron — closed,
# canon-occluded). Legal pad + pen dead center.
# ═════════════════════════════════════════════════════════════════
def build_desk():
    dx, dy = 0.0, 4.35
    make_box("Desk_Top", (dx, dy, 0.76), (1.70, 0.80, 0.05), PITSTOP_WOOD)
    make_box("Desk_TopEdge", (dx, dy - 0.415, 0.745), (1.70, 0.03, 0.04),
             PITSTOP_WOOD_DARK)
    for sgn, tag in [(-1, 'W'), (+1, 'E')]:
        px = dx + sgn * 0.60
        make_box(f"Desk_Pedestal_{tag}", (px, dy, 0.37), (0.45, 0.70, 0.72),
                 PITSTOP_WOOD)
        for di, dz in enumerate([0.62, 0.40]):
            make_box(f"Desk_DrawerFace_{tag}_{di}", (px, dy - 0.365, dz),
                     (0.39, 0.02, 0.16), PITSTOP_WOOD_DARK)
            make_cyl(f"Desk_DrawerPull_{tag}_{di}", (px, dy - 0.385, dz),
                     0.012, 0.05, PITSTOP_BRASS, axis='X')
    # THE bottom drawer (ch3) — deeper face, named
    make_box("Desk_Drawer_Bottom_E", (dx + 0.60, dy - 0.365, 0.16),
             (0.39, 0.02, 0.24), PITSTOP_WOOD_DARK)
    make_cyl("Desk_Drawer_Bottom_E_Pull", (dx + 0.60, dy - 0.385, 0.16),
             0.012, 0.05, PITSTOP_BRASS, axis='X')
    make_box("Desk_Drawer_Bottom_W", (dx - 0.60, dy - 0.365, 0.16),
             (0.39, 0.02, 0.24), PITSTOP_WOOD_DARK)
    make_cyl("Desk_Drawer_Bottom_W_Pull", (dx - 0.60, dy - 0.385, 0.16),
             0.012, 0.05, PITSTOP_BRASS, axis='X')
    make_box("Desk_Modesty", (dx, dy + 0.30, 0.42), (0.90, 0.03, 0.60),
             PITSTOP_WOOD)
    # Desktop: the legal pad (block letters are scene-side Label3D)
    make_box("LegalPad", (dx - 0.10, dy - 0.10, 0.795), (0.22, 0.30, 0.015),
             PITSTOP_LEGAL_PAD)
    make_box("LegalPad_Page", (dx - 0.10, dy - 0.10, 0.805),
             (0.20, 0.27, 0.004), PITSTOP_LEGAL_PAD)
    make_cyl("Desk_Pen", (dx + 0.10, dy - 0.14, 0.79), 0.006, 0.14,
             P.METAL_BLACK, axis='Y')
    # Rick's father's decades: inkwell ring stain in the oak
    make_cyl("DeskTop_RingStain", (dx + 0.55, dy + 0.18, 0.786), 0.045,
             0.002, PITSTOP_WOOD_DARK, segments=12)
    # Corded phone (the diner line)
    make_box("Desk_Phone_Body", (dx - 0.55, dy + 0.10, 0.82),
             (0.22, 0.16, 0.08), (0.26, 0.24, 0.24, 1.0))
    make_box("Desk_Phone_Handset", (dx - 0.55, dy + 0.10, 0.885),
             (0.24, 0.06, 0.05), (0.20, 0.18, 0.18, 1.0))
    for i in range(3):
        make_cyl(f"Desk_Phone_Cord_{i}", (dx - 0.42 + i * 0.03,
                 dy + 0.19, 0.80 - i * 0.01), 0.010, 0.02,
                 (0.20, 0.18, 0.18, 1.0), axis='Y')
    # Banker's lamp
    make_cyl("Desk_Lamp_Base", (dx + 0.55, dy + 0.12, 0.795), 0.07, 0.02,
             PITSTOP_BRASS)
    make_cyl("Desk_Lamp_Stem", (dx + 0.55, dy + 0.12, 0.90), 0.012, 0.20,
             PITSTOP_BRASS)
    make_cyl("Desk_Lamp_Shade", (dx + 0.52, dy + 0.10, 1.00), 0.065, 0.24,
             (0.24, 0.42, 0.30, 1.0), axis='X', segments=10)
    # Coffee mug + spike + ledgers
    make_cyl("Desk_Mug", (dx + 0.30, dy - 0.22, 0.805), 0.040, 0.09,
             (0.92, 0.90, 0.84, 1.0), segments=10)
    make_cyl("Desk_Spike_Base", (dx - 0.70, dy - 0.20, 0.795), 0.045, 0.02,
             PITSTOP_STEEL_DK)
    make_cyl("Desk_Spike_Needle", (dx - 0.70, dy - 0.20, 0.88), 0.006, 0.15,
             PITSTOP_STAINLESS)
    make_box("Desk_Spike_Invoices", (dx - 0.70, dy - 0.20, 0.83),
             (0.09, 0.09, 0.02), P.PAPER)
    for i, lz in enumerate([0.80, 0.835]):
        make_box(f"Desk_Ledger_{i}", (dx + 0.62, dy - 0.18, lz),
                 (0.26, 0.34, 0.035), COL_BINDERS[i])
    # The chair, reupholstered twice (ch0): rust seat, mustard back
    chx, chy = 0.0, 3.45
    make_cyl("ReuphChair_Post", (chx, chy, 0.30), 0.030, 0.40,
             PITSTOP_STEEL_DK)
    for i, (lx, ly) in enumerate([(+0.22, 0.0), (-0.22, 0.0),
                                  (0.0, +0.22), (0.0, -0.22)]):
        make_box(f"ReuphChair_Leg_{i}", (chx + lx / 2.0, chy + ly / 2.0,
                 0.06), (0.44 if ly == 0 else 0.06,
                         0.44 if lx == 0 else 0.06, 0.05),
                 PITSTOP_WOOD_DARK)
    make_box("ReuphChair_Seat", (chx, chy, 0.53), (0.46, 0.44, 0.09),
             COL_RUST_FAB)
    make_box("ReuphChair_Back", (chx, chy + 0.24, 0.92), (0.44, 0.07, 0.42),
             COL_MUSTARD_FAB)
    for sgn in (-1, +1):
        make_box(f"ReuphChair_Arm_{sgn:+d}", (chx + sgn * 0.25, chy, 0.71),
                 (0.05, 0.40, 0.05), PITSTOP_WOOD)
        make_box(f"ReuphChair_ArmPost_{sgn:+d}",
                 (chx + sgn * 0.25, chy - 0.14, 0.62), (0.04, 0.04, 0.14),
                 PITSTOP_WOOD)
    # Caster-wear ring in the linoleum under the chair
    make_cyl("Floor_CasterWear", (chx, chy, 0.006), 0.42, 0.002,
             P.FLOOR_SCUFF, segments=14)


# ═════════════════════════════════════════════════════════════════
# MANAGER WALLS — safe, single filing cabinet (proud of the wall),
# punch clock + time cards, corkboard + calendar, breaker panel,
# apron hooks, health certificate, supply cartons.
# ═════════════════════════════════════════════════════════════════
def build_manager_dressing():
    # Floor safe beside the desk (NE corner)
    make_box("Safe_Body", (1.40, 4.50, 0.36), (0.55, 0.55, 0.72),
             PITSTOP_STEEL_DK)
    make_cyl("Safe_Dial", (1.40, 4.21, 0.42), 0.06, 0.05, PITSTOP_STAINLESS,
             axis='Y', segments=10)
    make_box("Safe_Handle", (1.24, 4.215, 0.30), (0.04, 0.03, 0.14),
             PITSTOP_STAINLESS)
    make_box("Safe_PaperStack", (1.40, 4.50, 0.76), (0.30, 0.36, 0.08),
             P.PAPER_AGED)
    # ONE filing cabinet, west wall, fully inside the room
    make_box("Filing_Body", (-1.55, 3.60, 0.66), (0.50, 0.60, 1.32),
             (0.62, 0.62, 0.58, 1.0))
    for di, dz in enumerate([1.14, 0.82, 0.50, 0.18]):
        make_box(f"Filing_DrawerFace_{di}", (-1.55, 3.295, dz),
                 (0.44, 0.02, 0.24), (0.55, 0.55, 0.51, 1.0))
        make_box(f"Filing_Handle_{di}", (-1.55, 3.28, dz + 0.06),
                 (0.14, 0.015, 0.025), P.METAL_BLACK)
    # Desk fan on the cabinet (Texas summer; the AC is for customers)
    make_cyl("Fan_Base", (-1.55, 3.60, 1.345), 0.09, 0.03, PITSTOP_STEEL_DK)
    make_cyl("Fan_Stem", (-1.55, 3.60, 1.42), 0.015, 0.14, PITSTOP_STEEL_DK)
    make_cyl("Fan_Cage", (-1.55, 3.62, 1.54), 0.14, 0.08, PITSTOP_STAINLESS,
             axis='Y', segments=12)
    # Punch clock + time-card rack, east wall (Brenda / Lydia / the
    # kids' doubles all clock through here)
    make_box("PunchClock_Body", (1.84, 1.55, 1.45), (0.12, 0.30, 0.42),
             PITSTOP_STEEL_DK)
    make_cyl("PunchClock_Face", (1.775, 1.55, 1.53), 0.09, 0.02,
             (0.94, 0.92, 0.86, 1.0), axis='X', segments=12)
    make_box("PunchClock_Slot", (1.77, 1.55, 1.30), (0.02, 0.12, 0.015),
             P.METAL_BLACK)
    make_box("TimeCardRack_Back", (1.885, 2.30, 1.50), (0.03, 0.55, 0.65),
             PITSTOP_WOOD)
    for i in range(8):
        col = i % 2
        row = i // 2
        make_box(f"TimeCard_{i}", (1.86, 2.16 + col * 0.28,
                 1.72 - row * 0.15), (0.02, 0.10, 0.15), P.PAPER)
    # Corkboard above the filing cabinet: the schedule + notes
    make_box("Corkboard_Panel", (-1.89, 3.60, 1.75), (0.02, 0.95, 0.65),
             COL_CORK)
    for i, fz in enumerate([1.41, 2.09]):
        make_box(f"Corkboard_FrameH_{i}", (-1.87, 3.60, fz),
                 (0.03, 1.00, 0.04), PITSTOP_WOOD)
    for i, (dy, dz, w, h) in enumerate([
            (-0.30, 1.85, 0.24, 0.30), (0.02, 1.90, 0.28, 0.22),
            (0.32, 1.82, 0.18, 0.24), (-0.16, 1.56, 0.20, 0.16),
            (0.14, 1.58, 0.16, 0.20), (0.36, 1.55, 0.12, 0.12)]):
        make_box(f"Corkboard_Sheet_{i}", (-1.876, 3.60 + dy, dz),
                 (0.01, w, h), P.PAPER if i % 2 else P.PAPER_AGED)
        make_box(f"Corkboard_Pin_{i}", (-1.869, 3.60 + dy, dz + h / 2.0 -
                 0.02), (0.008, 0.015, 0.015), PITSTOP_RED)
    make_calendar("Calendar", (-1.895, 1.60, 1.65))
    # Breaker panel, west wall north end
    make_box("BreakerPanel_Box", (-1.87, 4.45, 1.70), (0.06, 0.40, 0.60),
             PITSTOP_STEEL_DK)
    make_box("BreakerPanel_Door", (-1.835, 4.45, 1.70), (0.01, 0.36, 0.56),
             PITSTOP_STAINLESS)
    make_box("BreakerPanel_Label", (-1.827, 4.45, 1.94), (0.005, 0.20, 0.08),
             P.PAPER_AGED)
    # Apron hooks by the door (the FOLDED apron is inside the bottom
    # drawer, ch3 — this is the spare on the wall)
    make_box("ApronHook_Rail", (1.885, 0.75, 1.62), (0.03, 0.45, 0.06),
             PITSTOP_WOOD)
    for i, hy in enumerate([0.60, 0.90]):
        make_cyl(f"ApronHook_{i}", (1.84, hy, 1.59), 0.012, 0.08,
                 PITSTOP_BRASS, axis='X')
    make_box("Apron_Hanging_Bib", (1.80, 0.90, 1.32), (0.02, 0.28, 0.42),
             PITSTOP_APRON)
    make_box("Apron_Hanging_Skirt", (1.80, 0.90, 0.95), (0.02, 0.36, 0.34),
             PITSTOP_APRON)
    make_box("Apron_Hanging_Strap", (1.82, 0.90, 1.56), (0.01, 0.16, 0.06),
             PITSTOP_APRON)
    # Framed health certificate by the door
    make_box("HealthCert_Frame", (1.89, 1.10, 1.95), (0.02, 0.30, 0.38),
             PITSTOP_WOOD_DARK)
    make_box("HealthCert_Paper", (1.877, 1.10, 1.95), (0.01, 0.24, 0.32),
             P.PAPER)
    # Supply cartons, SW corner (napkins / to-go / the Sysco stack)
    make_box("Carton_0", (-1.45, 0.85, 0.22), (0.55, 0.45, 0.44), COL_KRAFT)
    make_box("Carton_1", (-1.42, 1.38, 0.20), (0.50, 0.42, 0.40), COL_KRAFT)
    make_box("Carton_2", (-1.48, 1.05, 0.62), (0.48, 0.40, 0.36), COL_KRAFT)
    make_box("Carton_TapeSeam", (-1.48, 1.05, 0.805), (0.48, 0.06, 0.005),
             P.PAPER_AGED)
    make_box("NapkinBale", (-1.45, 1.90, 0.15), (0.40, 0.30, 0.30),
             PITSTOP_APRON)
    # Small trash bin beside the desk
    make_cyl("Desk_Bin", (0.62, 3.95, 0.16), 0.13, 0.32, PITSTOP_STEEL_DK,
             segments=10)
    # Wall clock frozen at 6:17 — ch0: the hour that belongs to the
    # diner. North wall, above the desk, facing the camera.
    make_wall_clock("OfficeClock", (0.85, 4.88, 2.15),
                    frozen_hour=6, frozen_min=17)
    # Shelf above the desk: binders, envelope box, first-aid kit
    make_box("DeskShelf", (-0.60, 4.80, 1.90), (1.20, 0.28, 0.04),
             PITSTOP_WOOD)
    for i, sx in enumerate([-1.05, -0.60]):
        make_box(f"DeskShelf_Bracket_{i}", (sx, 4.86, 1.82),
                 (0.04, 0.12, 0.12), PITSTOP_WOOD_DARK)
    for i in range(4):
        make_box(f"DeskShelf_Binder_{i}", (-1.02 + i * 0.10, 4.80, 2.07),
                 (0.07, 0.24, 0.30), COL_BINDERS[i])
    make_box("DeskShelf_EnvelopeBox", (-0.42, 4.80, 1.99),
             (0.26, 0.20, 0.14), COL_KRAFT)
    make_box("DeskShelf_FirstAid", (-0.12, 4.80, 1.99), (0.22, 0.16, 0.14),
             PITSTOP_APRON)
    make_box("DeskShelf_FirstAid_CrossV", (-0.12, 4.71, 1.99),
             (0.03, 0.005, 0.10), PITSTOP_RED)
    make_box("DeskShelf_FirstAid_CrossH", (-0.12, 4.71, 1.99),
             (0.10, 0.005, 0.03), PITSTOP_RED)


# ═════════════════════════════════════════════════════════════════
# DOOR — frame + transom on the south gap; leaf parked OPEN against
# the south wall east segment (the camera shoots through the gap).
# ═════════════════════════════════════════════════════════════════
def build_door():
    for sgn in (-1, +1):
        make_box(f"DoorPost_{sgn:+d}", (sgn * 0.96, 0.0, 1.08),
                 (0.08, 0.24, 2.16), PITSTOP_WOOD)
    make_box("DoorTransom", (0.0, 0.0, 2.20), (2.0, 0.24, 0.08),
             PITSTOP_WOOD)
    make_box("Door_Leaf_Open", (1.45, 0.14, 1.04), (0.82, 0.05, 2.08),
             PITSTOP_WOOD)
    make_cyl("Door_Knob", (1.78, 0.19, 1.02), 0.022, 0.05, PITSTOP_BRASS,
             axis='Y')
    make_door_hinges("Door_Hinge", edge_x=1.02, edge_y=0.12,
                     edge_z_centers=[0.35, 1.05, 1.78], axis='Y')
    make_box("Office_DoorSign", (1.45, 0.17, 1.62), (0.16, 0.008, 0.10),
             P.PAPER_AGED)
    # Threshold wear strip where the kitchen meets the office
    make_box("Door_Threshold", (0.0, 0.0, 0.012), (1.90, 0.20, 0.02),
             PITSTOP_WOOD_DARK)


# ═════════════════════════════════════════════════════════════════
# CEILING INFRA — ONE fluorescent (small room, no canon for more),
# smoke detector, HVAC.
# ═════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    make_fluorescent_tube_fixture("Fluor_0", (0.0, 2.40, CEIL),
                                  length=1.20, width=0.32)
    make_smoke_detector("Smoke", (-0.9, 1.4, CEIL))
    make_hvac_vent("HVAC", (1.0, 4.30, CEIL), width=0.70, depth=0.35)


def main():
    clear_scene()
    build_shell()
    build_desk()
    build_manager_dressing()
    build_door()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/pit_stop_office.glb"))
    print(f"\n[build_pit_stop_office] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
