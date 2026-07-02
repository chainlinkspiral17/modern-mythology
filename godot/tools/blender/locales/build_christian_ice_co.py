"""XVII · STAR — Christian Ice Co. Interior of the 1950s ice
plant. Front retail counter with a glass-fronted ice-block freezer
(stacked blocks behind frosted glass), a row of bagged-ice
chest freezers along the W wall, mid-floor refrigeration
machinery (compressors + brine tank), the loading dock door at
the back. "ICE" letters cast a cold backlight through the
storefront. Glass Skin / Christian Ice beat — quietly luminous.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_calendar, make_faded_poster
from _props.safety import (make_smoke_detector, make_sprinkler,
                            make_fluorescent_tube_fixture, make_security_camera)

PAL = {"wall": (0.78, 0.82, 0.86, 1.0), "baseboard": (0.42, 0.46, 0.52, 1.0)}
COL_FLOOR_CONCRETE = (0.62, 0.66, 0.70, 1.0); COL_SEAM = (0.42, 0.46, 0.50, 1.0)
COL_COUNTER = (0.78, 0.82, 0.86, 1.0); COL_COUNTER_TOP = (0.62, 0.74, 0.82, 1.0)
COL_FREEZER_BODY = (0.86, 0.90, 0.94, 1.0); COL_FROST_GLASS = (0.86, 0.94, 0.96, 0.65)
COL_ICE_BLOCK = (0.78, 0.92, 0.96, 0.75); COL_COMPRESSOR = (0.32, 0.32, 0.34, 1.0)
COL_BRINE_TANK = (0.42, 0.52, 0.58, 1.0); COL_PIPE = (0.62, 0.62, 0.60, 1.0)
COL_PIPE_RED = (0.86, 0.34, 0.20, 1.0); COL_NEON_ICE = (0.78, 0.92, 0.96, 1.0)
COL_DOCK_DOOR = (0.42, 0.46, 0.52, 1.0); COL_BAGS = (0.86, 0.84, 0.78, 1.0)

ROOM_W = 9.0; ROOM_D = 11.0; CEIL = 3.80


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR_CONCRETE, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL, baseboard_face_sign=bb)
    # N wall: loading dock door + small walls
    make_wall("Wall_N_W", (-3.0, ROOM_D, 0), length=3.0, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (+3.0, ROOM_D, 0), length=3.0, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=-1)
    # Roll-up dock door (closed) centered N
    make_box("DockDoor", (0.0, ROOM_D-0.04, 1.50), (3.20, 0.08, 3.00), COL_DOCK_DOOR)
    for di in range(8):
        make_box(f"DockDoor_Rib_{di}", (0.0, ROOM_D-0.02, 0.20 + di*0.36),
                 (3.20, 0.04, 0.06), (0.32, 0.36, 0.42, 1.0))
    # S wall (storefront) — glass front with central door
    make_wall("Wall_S_W", (-3.50, 0.0, 0), length=2.0, height=0.80, axis='X', palette=PAL)
    make_wall("Wall_S_E", (+3.50, 0.0, 0), length=2.0, height=0.80, axis='X', palette=PAL)
    # Glass storefront panels above the low wall
    make_box("Storefront_W_Glass", (-3.20, 0.04, 2.20), (1.40, 0.04, 2.80), COL_FROST_GLASS)
    make_box("Storefront_E_Glass", (+3.20, 0.04, 2.20), (1.40, 0.04, 2.80), COL_FROST_GLASS)
    # Frame mullions
    for mx in [-3.20, -2.50, +2.50, +3.20]:
        make_box(f"Mullion_{mx:+.0f}", (mx, 0.02, 2.20),
                 (0.04, 0.06, 2.80), COL_FREEZER_BODY)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),
                                    ("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_BRINE_TANK})


def build_ice_letters_outside():
    # The iconic "ICE" letters on the parapet, visible THROUGH the
    # storefront from inside. Modeled as three big square panels.
    for li, (lx, label) in enumerate([(-1.40, "I"), (0.0, "C"), (+1.40, "E")]):
        make_box(f"ICE_Letter_BG_{label}", (lx, -1.40, 4.50),
                 (1.00, 0.20, 1.20), COL_NEON_ICE)
        # Strokes carved out — abstracted with darker boxes inside
        make_box(f"ICE_Letter_Stroke_{label}", (lx, -1.50, 4.50),
                 (0.60, 0.05, 0.80), (0.32, 0.42, 0.52, 1.0))
    # Pole sign also far back
    make_cyl("PoleSign_Pole", (-3.0, -3.0, 3.0), 0.10, 6.0, COL_BRINE_TANK)
    make_box("PoleSign_BG", (-3.0, -3.0, 5.80), (1.20, 0.10, 0.80), COL_NEON_ICE)


def build_retail_counter():
    # Counter parallel to the storefront, S of the freezer
    ry = 2.40
    make_box("Counter_Top",  (0.0, ry, 1.00), (3.40, 0.60, 0.04), COL_COUNTER_TOP)
    make_box("Counter_Body", (0.0, ry, 0.50), (3.40, 0.60, 1.00), COL_COUNTER)
    # Cash register
    make_box("Register_Body", (-1.20, ry, 1.20), (0.40, 0.40, 0.30), COL_BRINE_TANK)
    make_box("Register_Drawer", (-1.20, ry, 0.94), (0.40, 0.40, 0.08), COL_BRINE_TANK)
    # Bell + receipt spike + price-card display
    make_cyl("CounterBell", (+0.80, ry, 1.10), 0.06, 0.04, (0.74, 0.56, 0.28, 1.0))
    make_box("PriceCard", (+1.20, ry, 1.20), (0.30, 0.04, 0.20), P.PAPER)


def build_ice_block_freezer():
    # Glass-fronted upright freezer behind the counter
    fx, fy = 0.0, 3.80
    make_box("BlockFreezer_Body", (fx, fy, 1.20), (3.20, 0.80, 2.40), COL_FREEZER_BODY)
    make_box("BlockFreezer_Glass", (fx, fy-0.40, 1.40), (3.00, 0.005, 2.00), COL_FROST_GLASS)
    # Stacked ice blocks behind the glass (5x3 grid)
    for col in range(5):
        for row in range(3):
            ix = -1.20 + col * 0.60
            iz = 0.50 + row * 0.50
            make_box(f"IceBlock_{col}_{row}", (fx + ix - 1.0, fy, iz),
                     (0.50, 0.40, 0.40), COL_ICE_BLOCK)
    # Frost coil pipe visible at the top
    make_cyl("FrostCoil", (fx, fy-0.30, 2.30), 0.05, 3.00, COL_PIPE, axis='X')


def build_chest_freezers():
    # Row of bagged-ice chest freezers along the W wall
    for fi in range(3):
        fx = -ROOM_W/2.0 + 0.60
        fy = 4.50 + fi * 1.80
        make_box(f"Chest_{fi}_Body", (fx, fy, 0.50), (0.80, 1.40, 1.00), COL_FREEZER_BODY)
        make_box(f"Chest_{fi}_Lid", (fx, fy, 1.04), (0.80, 1.40, 0.08), COL_FROST_GLASS)
        # Stacked bags visible (3 per chest)
        for bi in range(3):
            by = fy - 0.40 + bi * 0.40
            make_box(f"Chest_{fi}_Bag_{bi}", (fx, by, 1.10),
                     (0.40, 0.30, 0.20), COL_BAGS)


def build_machinery():
    # Mid-floor refrigeration: 2 compressors + a brine tank
    # Compressor 1
    cx1, cy1 = +1.80, 6.50
    make_box("Comp1_Base", (cx1, cy1, 0.30), (1.00, 0.80, 0.60), COL_COMPRESSOR)
    make_cyl("Comp1_Drum", (cx1, cy1, 0.90), 0.30, 0.40, COL_COMPRESSOR, segments=12)
    make_cyl("Comp1_Pipe_Top", (cx1, cy1, 1.30), 0.04, 0.40, COL_PIPE)
    # Compressor 2
    cx2, cy2 = +3.00, 6.50
    make_box("Comp2_Base", (cx2, cy2, 0.30), (0.80, 0.80, 0.60), COL_COMPRESSOR)
    make_cyl("Comp2_Drum", (cx2, cy2, 0.90), 0.24, 0.40, COL_COMPRESSOR, segments=12)
    # Brine tank
    bx, by = +1.80, 8.50
    make_cyl("BrineTank", (bx, by, 0.90), 0.70, 1.80, COL_BRINE_TANK, segments=14)
    make_cyl("BrineTank_Top", (bx, by, 1.84), 0.72, 0.08, COL_PIPE, segments=14)
    # Connecting pipes (red = hot gas, plain = brine)
    make_box("Pipe_Hot_1", (cx1, cy1, 1.60), (0.04, 0.04, 0.50), COL_PIPE_RED)
    make_box("Pipe_Hot_2", ((cx1+bx)/2.0, (cy1+by)/2.0, 1.84),
             (abs(cx1-bx), 0.04, 0.04), COL_PIPE_RED)
    make_box("Pipe_Brine", ((cx2+bx)/2.0, (cy2+by)/2.0, 1.50),
             (abs(cx2-bx), 0.04, 0.04), COL_PIPE)
    # Pressure gauges
    for gi, (gx, gy) in enumerate([(cx1+0.20, cy1-0.40), (cx2-0.20, cy2-0.40), (bx, by-0.70)]):
        make_cyl(f"Gauge_{gi}", (gx, gy, 1.20), 0.06, 0.02, P.PAPER, axis='Y', segments=10)


def build_ceiling_infra():
    for j, ypos in enumerate([2.0, 5.5, 9.0]):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL),
                                       length=2.20, width=0.32,
                                       palette={"diffuser": (0.92, 0.96, 1.0, 1.0)})
    make_smoke_detector("Smoke", (0.0, 5.5, CEIL))
    make_sprinkler("Spr_W", (-2.5, 5.5, CEIL))
    make_sprinkler("Spr_E", (+2.5, 5.5, CEIL))
    make_security_camera("Cam", (+ROOM_W/2.0-0.10, 1.5, CEIL-0.10))


def build_decor():
    make_wall_clock("Clock", (-ROOM_W/2.0+0.05, 1.5, 2.40), frozen_hour=4, frozen_min=15)
    make_calendar("Calendar", (-ROOM_W/2.0+0.05, 9.5, 2.30))
    make_faded_poster("Notice", (+ROOM_W/2.0-0.05, 9.5, 1.80))


def build_star_dressing():
    """Scene-description specifics from setup_eleven_days_left.json:
      · The fogged block-freezer glass · the canon "wipe-it-once
        it-fogs-again" tell with a recent wiped streak
      · Mr Couvillon's customer ledger on the retail counter · a
        large ledger book turned to his page (the canon "Wednesday
        since the year she was born" tally)
      · The morning wiping cloth on the freezer top · damp blue
        canvas
      · The notice that hasn't been published yet · a typed
        announcement on the counter near the till, face down
    """
    # Block-freezer approx at (-1.5, +2.0); retail counter at (+2.0, 0)
    bf_x = -1.5
    bf_y = +2.0
    bf_glass_z = 1.30
    # Fog overlay on the freezer glass (a pale frosted rectangle)
    make_box("BlockFreezer_FogOverlay",
             (bf_x, bf_y - 0.42, bf_glass_z),
             (0.80, 0.005, 0.50),
             (0.86, 0.90, 0.94, 0.65))
    # A wiped clean-streak diagonal across the fog (where Delphine
    # just wiped it)
    make_box("BlockFreezer_WipedStreak",
             (bf_x, bf_y - 0.421, bf_glass_z + 0.04),
             (0.50, 0.005, 0.08),
             (0.62, 0.74, 0.86, 0.5))
    # The wiping cloth on the freezer top (damp blue canvas)
    make_box("BlockFreezer_WipingCloth",
             (bf_x + 0.20, bf_y, bf_glass_z + 0.32),
             (0.22, 0.14, 0.018),
             (0.42, 0.52, 0.62, 1.0))

    # Mr Couvillon's customer ledger on the retail counter
    rc_x = +2.0
    rc_y = 0.0
    counter_z = 1.05
    make_box("CouvillonLedger_Cover",
             (rc_x, rc_y, counter_z + 0.020),
             (0.32, 0.40, 0.040),
             (0.42, 0.22, 0.16, 1.0))
    # Open page
    make_box("CouvillonLedger_LeftPage",
             (rc_x - 0.14, rc_y, counter_z + 0.042),
             (0.18, 0.38, 0.002),
             (0.94, 0.90, 0.80, 1.0))
    make_box("CouvillonLedger_RightPage",
             (rc_x + 0.14, rc_y, counter_z + 0.042),
             (0.18, 0.38, 0.002),
             (0.94, 0.90, 0.80, 1.0))
    # Many narrow tally lines on Couvillon's page (one block per Wednesday)
    for li in range(20):
        make_box("CouvillonLedger_TallyLine_%d" % li,
                 (rc_x + 0.14, rc_y + 0.16 - li * 0.018, counter_z + 0.043),
                 (0.16, 0.006, 0.0005),
                 (0.20, 0.16, 0.12, 1.0))

    # The closing-notice typed page, face down on the counter
    make_box("ClosingNotice_Paper",
             (rc_x - 0.36, rc_y - 0.20, counter_z + 0.014),
             (0.18, 0.24, 0.0008),
             (0.94, 0.90, 0.80, 1.0))
    # Edge of the paper showing the official letterhead stamp
    # (a small darker block, face-down so just a hint visible)
    make_box("ClosingNotice_Stamp",
             (rc_x - 0.36, rc_y - 0.20, counter_z + 0.0145),
             (0.06, 0.06, 0.0005),
             (0.42, 0.20, 0.16, 1.0))


def build_star_wave2_props():
    """Named props from setup_the_notice_in_the_picayune.json and
    setup_the_last_sunday.json.

    the_notice_in_the_picayune (6:48 AM Wednesday · the notice ran):
      · Mrs Aucoin's Picayune folded to A-14 on the counter
      · The framed grandfather photograph over the register with a
        catch-light (1949 opening day · Emile at the dock)
      · Wilfred Theriot's envelope on the counter (contains the
        1978 compressor-day photograph)
      · The Gambit reporter's small notepad + pencil (Marcy Nguyễn)

    the_last_sunday (3:14 PM · the ceremony that arrived on its own):
      · Mrs Aucoin's shrimp étouffée in a foil pan on the counter
      · The photograph enlargement of Emile on an easel in the
        parking lot (via the storefront window frame)
      · The magnolia sapling in burlap by the parking-lot planter
      · Mr Theriot's 1949 brass shovel leaning on the wagon
      · The Bunn tab of a hundred paper cups (a tall stack)
    """
    rc_x = 0.0
    rc_y = -1.20
    counter_z = 0.90

    # ── the_notice_in_the_picayune ──────────────────────────────

    # Mrs Aucoin's Picayune folded to A-14 on the counter
    pic_x = rc_x + 0.40
    pic_y = rc_y - 0.10
    make_box("MrsAucoin_Picayune_Fold",
             (pic_x, pic_y, counter_z + 0.010),
             (0.24, 0.16, 0.008),
             (0.88, 0.86, 0.80, 1.0))
    # A-14 headline block (a darker stripe at the top of the fold)
    make_box("MrsAucoin_Picayune_Headline",
             (pic_x, pic_y + 0.05, counter_z + 0.015),
             (0.20, 0.020, 0.0005),
             (0.20, 0.16, 0.12, 1.0))
    # Column body of the notice (thinner stripes)
    for li in range(6):
        make_box("MrsAucoin_Picayune_Line_%d" % li,
                 (pic_x, pic_y + 0.02 - li * 0.010, counter_z + 0.015),
                 (0.20, 0.005, 0.0005),
                 (0.28, 0.24, 0.20, 1.0))

    # The framed grandfather photograph over the register
    # (register is at the counter · frame goes up on the wall behind)
    frame_x = rc_x
    frame_y = rc_y + 0.60
    make_box("Emile_Frame_Body",
             (frame_x, frame_y - 0.02, 2.20),
             (0.30, 0.02, 0.24),
             (0.62, 0.46, 0.24, 1.0))
    # Photograph inside
    make_box("Emile_Frame_Photo",
             (frame_x, frame_y - 0.03, 2.20),
             (0.26, 0.001, 0.20),
             (0.72, 0.68, 0.58, 1.0))
    # Emile silhouette (a dark figure in a white shirt at the dock)
    make_box("Emile_Photo_Figure",
             (frame_x, frame_y - 0.032, 2.16),
             (0.06, 0.001, 0.08),
             (0.28, 0.24, 0.20, 1.0))
    # White-shirt patch on the figure
    make_box("Emile_Photo_Shirt",
             (frame_x, frame_y - 0.033, 2.18),
             (0.04, 0.001, 0.04),
             (0.94, 0.92, 0.86, 1.0))
    # A small brass plaque under the frame
    make_box("Emile_Frame_Plaque",
             (frame_x, frame_y - 0.02, 2.02),
             (0.20, 0.005, 0.03),
             (0.78, 0.62, 0.30, 1.0))

    # Wilfred Theriot's envelope on the counter
    make_box("Wilfred_Envelope",
             (rc_x - 0.30, rc_y + 0.14, counter_z + 0.010),
             (0.16, 0.11, 0.006),
             (0.94, 0.88, 0.76, 1.0))
    # 1978 photograph corner peeking out of the envelope
    make_box("Wilfred_Envelope_PhotoEdge",
             (rc_x - 0.26, rc_y + 0.18, counter_z + 0.014),
             (0.06, 0.02, 0.001),
             (0.62, 0.56, 0.42, 1.0))

    # Marcy Nguyễn's small reporter notepad + pencil
    make_box("Marcy_Notepad",
             (rc_x + 0.50, rc_y + 0.14, counter_z + 0.008),
             (0.10, 0.14, 0.010),
             (0.94, 0.92, 0.86, 1.0))
    # Wire spiral binding (top edge)
    make_box("Marcy_Notepad_Spiral",
             (rc_x + 0.50, rc_y + 0.21, counter_z + 0.014),
             (0.10, 0.005, 0.003),
             (0.62, 0.62, 0.64, 1.0))
    make_cyl("Marcy_Pencil",
             (rc_x + 0.62, rc_y + 0.14, counter_z + 0.010),
             0.005, 0.14,
             (0.94, 0.86, 0.32, 1.0), segments=6, axis='Y')

    # ── the_last_sunday ────────────────────────────────────────

    # Mrs Aucoin's shrimp étouffée in a foil pan
    make_box("MrsAucoin_Etouffee_Pan",
             (rc_x - 0.10, rc_y, counter_z + 0.03),
             (0.28, 0.20, 0.06),
             (0.86, 0.86, 0.88, 1.0))    # foil silver
    # Étouffée surface (dark rust-red)
    make_box("MrsAucoin_Etouffee_Surface",
             (rc_x - 0.10, rc_y, counter_z + 0.062),
             (0.24, 0.16, 0.004),
             (0.62, 0.28, 0.14, 1.0))
    # A few shrimp shapes visible (small pink curls)
    for shi in range(3):
        make_cyl("MrsAucoin_Etouffee_Shrimp_%d" % shi,
                 (rc_x - 0.10 + shi * 0.03 - 0.04, rc_y + shi * 0.02 - 0.02, counter_z + 0.065),
                 0.010, 0.03,
                 (0.94, 0.62, 0.48, 1.0), segments=6, axis='Z')

    # Photograph enlargement of Emile on an easel in the parking lot
    # (visible through the storefront window · we put it at +Y, outside)
    easel_x = -3.50
    easel_y = -6.00
    # Tripod legs
    for li, (dx, dy) in enumerate([(-0.20, -0.10), (+0.20, -0.10), (0.0, +0.14)]):
        make_cyl("Easel_TripodLeg_%d" % li,
                 (easel_x + dx, easel_y + dy, 0.80),
                 0.014, 1.60,
                 (0.42, 0.30, 0.22, 1.0), segments=6, axis='Z')
    # Frame (bigger than the interior photograph)
    make_box("Easel_PhotoFrame",
             (easel_x, easel_y, 1.60),
             (0.90, 0.03, 0.68),
             (0.62, 0.46, 0.24, 1.0))
    # Photograph itself (Emile enlarged)
    make_box("Easel_PhotoInside",
             (easel_x, easel_y - 0.02, 1.60),
             (0.80, 0.001, 0.58),
             (0.72, 0.68, 0.58, 1.0))

    # Magnolia sapling in burlap by the parking-lot planter
    mag_x = -3.20
    mag_y = -5.20
    # Burlap-wrapped root ball
    make_cyl("Magnolia_RootBall",
             (mag_x, mag_y, 0.24),
             0.18, 0.36,
             (0.72, 0.60, 0.34, 1.0), segments=8, axis='Z')
    # Trunk
    make_cyl("Magnolia_Trunk",
             (mag_x, mag_y, 1.10),
             0.022, 1.60,
             (0.42, 0.30, 0.22, 1.0), segments=6, axis='Z')
    # Foliage cluster (three offset spheres approximated as cylinders)
    for fi, (dx, dz) in enumerate([(-0.10, 1.70), (+0.10, 1.80), (0.0, 1.94)]):
        make_cyl("Magnolia_Foliage_%d" % fi,
                 (mag_x + dx, mag_y, dz),
                 0.16, 0.20,
                 (0.34, 0.46, 0.30, 1.0), segments=10, axis='Z')

    # Mr Theriot's 1949 brass shovel leaning on the wagon
    # (wagon is offscreen · we place the shovel against the west wall)
    shovel_x = -2.20
    shovel_y = -3.00
    make_cyl("Theriot_Shovel_Handle",
             (shovel_x, shovel_y, 0.80),
             0.014, 1.40,
             (0.62, 0.42, 0.26, 1.0), segments=6, axis='Z')
    # Brass D-grip at the top
    make_cyl("Theriot_Shovel_DGrip",
             (shovel_x, shovel_y, 1.52),
             0.06, 0.02,
             (0.78, 0.62, 0.30, 1.0), segments=10, axis='X')
    # Blade at the bottom
    make_box("Theriot_Shovel_Blade",
             (shovel_x, shovel_y, 0.14),
             (0.14, 0.04, 0.20),
             (0.78, 0.62, 0.30, 1.0))

    # The Bunn tab of a hundred paper cups (a tall stack)
    stack_x = +0.60
    stack_y = rc_y + 0.20
    for pi in range(25):
        make_cyl("BunnPaperCup_%d" % pi,
                 (stack_x, stack_y, counter_z + 0.04 + pi * 0.02),
                 0.036, 0.020,
                 (0.94, 0.92, 0.90, 1.0), segments=10, axis='Z')


def main():
    clear_scene()
    build_shell()
    build_ice_letters_outside()
    build_retail_counter()
    build_ice_block_freezer()
    build_chest_freezers()
    build_machinery()
    build_ceiling_infra()
    build_decor()
    build_star_dressing()
    build_star_wave2_props()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/christian_ice_co.glb"))
    print(f"\n[build_christian_ice_co] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
