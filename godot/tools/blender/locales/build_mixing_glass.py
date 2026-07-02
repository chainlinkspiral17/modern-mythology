"""XIV · TEMPERANCE — The Mixing Glass. Narrow second-storey
cocktail lounge: backbar wall of bottles, U-shaped bar of brushed
copper, four leather booths along the W wall, a single neon
'OPEN' in the back. No windows on the street face — the side-alley
entrance only. Frank's Tuesday observation post.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_faded_poster, make_floor_plant
from _props.safety import make_smoke_detector, make_sprinkler

PAL = {"wall": (0.18, 0.14, 0.16, 1.0), "baseboard": (0.32, 0.22, 0.16, 1.0)}
COL_FLOOR = (0.22, 0.18, 0.16, 1.0); COL_SEAM = (0.14, 0.10, 0.08, 1.0)
COL_BAR_COPPER = (0.78, 0.46, 0.26, 1.0); COL_BAR_WOOD = (0.32, 0.20, 0.14, 1.0)
COL_BOOTH_LEATHER = (0.46, 0.18, 0.16, 1.0); COL_BACK_WOOD = (0.28, 0.18, 0.12, 1.0)
COL_BOTTLE_AMBER = (0.78, 0.42, 0.20, 1.0); COL_BOTTLE_CLEAR = (0.78, 0.84, 0.86, 0.55)
COL_BOTTLE_GREEN = (0.20, 0.42, 0.30, 1.0); COL_NEON_OPEN = (0.96, 0.32, 0.42, 1.0)
COL_LAMP = (0.96, 0.74, 0.42, 1.0)

ROOM_W = 5.0; ROOM_D = 8.5; CEIL = 2.90


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-1.80, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL)
    make_wall("Wall_S_E", (+1.80, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),
                                    ("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),
                                    ("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_BAR_COPPER})


def build_u_bar():
    # U-shaped bar — N end of room, opening toward S
    # E side: long arm
    make_box("Bar_E_Top",  (+1.50, 6.00, 1.06), (0.50, 3.20, 0.04), COL_BAR_COPPER)
    make_box("Bar_E_Body", (+1.50, 6.00, 0.50), (0.50, 3.20, 1.00), COL_BAR_WOOD)
    # W side: long arm
    make_box("Bar_W_Top",  (-1.50, 6.00, 1.06), (0.50, 3.20, 0.04), COL_BAR_COPPER)
    make_box("Bar_W_Body", (-1.50, 6.00, 0.50), (0.50, 3.20, 1.00), COL_BAR_WOOD)
    # N cap connecting them
    make_box("Bar_N_Top",  (0.0, 7.40, 1.06), (3.50, 0.50, 0.04), COL_BAR_COPPER)
    make_box("Bar_N_Body", (0.0, 7.40, 0.50), (3.50, 0.50, 1.00), COL_BAR_WOOD)
    # 6 bar stools around the perimeter (3 per side, S-facing arms)
    for si, (sx, sy) in enumerate([(+1.05, 4.60), (+1.05, 5.60), (+1.05, 6.60),
                                    (-1.05, 4.60), (-1.05, 5.60), (-1.05, 6.60)]):
        make_cyl(f"Stool_{si}_Post", (sx, sy, 0.40), 0.04, 0.80, P.METAL_BLACK)
        make_cyl(f"Stool_{si}_Seat", (sx, sy, 0.82), 0.18, 0.05, COL_BOOTH_LEATHER)
        make_cyl(f"Stool_{si}_Base", (sx, sy, 0.05), 0.20, 0.04, P.METAL_BLACK)


def build_backbar():
    # Mirrored backbar wall N of bar with bottle racks
    make_box("Backbar_Mirror", (0.0, ROOM_D-0.08, 1.80), (3.20, 0.04, 1.40), (0.74, 0.78, 0.82, 0.55))
    make_box("Backbar_Counter", (0.0, ROOM_D-0.30, 1.10), (3.20, 0.40, 0.06), COL_BACK_WOOD)
    # Three shelves of bottles
    for si in range(3):
        sz = 1.30 + si * 0.40
        make_box(f"Backbar_Shelf_{si}", (0.0, ROOM_D-0.30, sz), (3.00, 0.30, 0.02), COL_BACK_WOOD)
        for bi in range(15):
            bx = -1.40 + bi * 0.20
            cycle = bi % 3
            bc = [COL_BOTTLE_AMBER, COL_BOTTLE_CLEAR, COL_BOTTLE_GREEN][cycle]
            make_cyl(f"Bottle_{si}_{bi}", (bx, ROOM_D-0.30, sz + 0.16), 0.04, 0.30, bc, segments=8)


def build_booths():
    # Four leather booths along the W wall, each a banquette + table.
    for bi in range(4):
        by = 1.20 + bi * 1.80
        # Banquette against W wall
        make_box(f"Booth_{bi}_Bench", (-ROOM_W/2.0 + 0.40, by, 0.46),
                 (0.50, 1.50, 0.10), COL_BOOTH_LEATHER)
        make_box(f"Booth_{bi}_Back",  (-ROOM_W/2.0 + 0.20, by, 0.84),
                 (0.10, 1.50, 0.70), COL_BOOTH_LEATHER)
        # Small round table
        make_cyl(f"Booth_{bi}_Table", (-ROOM_W/2.0 + 1.00, by, 0.74), 0.30, 0.04, COL_BAR_COPPER)
        make_cyl(f"Booth_{bi}_TablePost", (-ROOM_W/2.0 + 1.00, by, 0.37), 0.025, 0.74, P.METAL_BLACK)
        # Small flickering candle on each table
        make_cyl(f"Booth_{bi}_Candle", (-ROOM_W/2.0 + 1.00, by, 0.80), 0.025, 0.08, COL_LAMP)


def build_neon_open():
    # Single neon sign in N corner, low and warm
    make_box("Neon_Open_BG", (-1.40, ROOM_D-0.10, 2.50), (0.80, 0.04, 0.30), COL_NEON_OPEN)
    make_box("Neon_Open_Letters", (-1.40, ROOM_D-0.12, 2.50), (0.005, 0.60, 0.18), P.PAPER)


def build_ceiling_infra():
    # Three brass-tube pendants over the bar runline
    for pi, px in enumerate([-0.80, 0.0, +0.80]):
        make_cyl(f"Pendant_Cord_{pi}", (px, 6.20, CEIL-0.30), 0.012, 0.60, P.METAL_BLACK)
        make_cyl(f"Pendant_Bulb_{pi}", (px, 6.20, CEIL-0.66), 0.10, 0.18, COL_LAMP)
    make_smoke_detector("Smoke", (0.0, 4.0, CEIL))
    make_sprinkler("Spr_N", (0.0, 6.5, CEIL))
    make_sprinkler("Spr_S", (0.0, 2.0, CEIL))


def build_decor():
    make_wall_clock("Clock", (+ROOM_W/2.0-0.05, 5.0, 2.20), frozen_hour=4, frozen_min=15)
    make_faded_poster("Poster_S", (+ROOM_W/2.0-0.05, 2.0, 1.40))
    make_floor_plant("Plant", (+ROOM_W/2.0-0.40, 0.40, 0.0), palette={"leaf": (0.40, 0.46, 0.30, 1.0)})


def build_temperance_dressing():
    """Scene-description specifics from setup_the_off_pour.json:
      · Frank's middle stool at the bar's mid-section · the canon
        watching-spot · with a small notebook on the bar in front
        of it (Frank takes notes sometimes)
      · "Off pour" tonight · a highball glass on the back-bar with
        an obviously-wrong liquid level (the canonical tell)
      · Maddie's clean-pour station · a row of three perfectly-
        cleaned glasses + a clean white pour rail (set against
        the off-pour visually)
    """
    # U-shaped bar mid-section approx at (0.0, -1.0); back-bar at +Y
    mid_x = 0.0
    mid_y = -1.0
    bar_top_z = 1.05

    # Frank's stool (middle position)
    make_cyl("FrankStool_Seat",
             (mid_x, mid_y - 0.50, 0.74),
             0.18, 0.06,
             (0.42, 0.20, 0.16, 1.0),
             segments=10, axis='Z')
    make_cyl("FrankStool_Post",
             (mid_x, mid_y - 0.50, 0.36),
             0.024, 0.72,
             (0.62, 0.62, 0.60, 1.0), segments=6, axis='Z')

    # Frank's notebook on the bar in front of the stool
    make_box("FranksNotebook_Cover",
             (mid_x, mid_y, bar_top_z + 0.014),
             (0.14, 0.20, 0.014),
             (0.20, 0.16, 0.12, 1.0))
    # Open to a page (cream paper)
    make_box("FranksNotebook_Page",
             (mid_x + 0.06, mid_y, bar_top_z + 0.022),
             (0.13, 0.18, 0.001),
             (0.94, 0.90, 0.80, 1.0))
    # 5 thin dark text lines on the page (his Tuesday tally)
    for li in range(5):
        make_box("FranksNotebook_Line_%d" % li,
                 (mid_x + 0.06, mid_y - 0.02 + li * 0.025, bar_top_z + 0.023),
                 (0.10, 0.012, 0.0005),
                 (0.18, 0.16, 0.10, 1.0))
    # Pen alongside
    make_cyl("FranksPen",
             (mid_x - 0.10, mid_y + 0.16, bar_top_z + 0.014),
             0.004, 0.12,
             (0.18, 0.14, 0.10, 1.0),
             segments=4, axis='Y')

    # The OFF POUR · a highball with an obvious-wrong liquid level
    # On the back-bar, slightly off to one side from Maddie's
    # canonical station
    bb_x = +0.80
    bb_y = +0.20
    bb_top_z = 1.20
    # Glass body (taller than usual)
    make_cyl("OffPour_Glass",
             (bb_x, bb_y, bb_top_z + 0.07),
             0.030, 0.14,
             (0.86, 0.86, 0.88, 0.55),
             segments=10, axis='Z')
    # Liquid (way too tall · the canonical "off" tell)
    make_cyl("OffPour_Liquid",
             (bb_x, bb_y, bb_top_z + 0.06),
             0.026, 0.115,
             (0.62, 0.36, 0.16, 1.0),
             segments=10, axis='Z')

    # Maddie's clean-pour station · 3 spotless glasses + a clean
    # white pour rail (a flat strip behind the bar)
    for gi in range(3):
        gx = -0.80 + gi * 0.18
        make_cyl("MaddiePour_CleanGlass_%d" % gi,
                 (gx, +0.20, bb_top_z + 0.055),
                 0.026, 0.11,
                 (0.92, 0.92, 0.94, 0.55),
                 segments=10, axis='Z')
    # White pour rail along the back-bar edge
    make_box("MaddiePour_Rail",
             (-0.60, +0.10, bb_top_z + 0.005),
             (0.60, 0.04, 0.01),
             (0.94, 0.92, 0.88, 1.0))


def build_temperance_wave2_props():
    """Named props from setup_pre_shift_setup.json and
    setup_last_call_friday.json. Additive to the canonical dressing;
    everything here supports the new bookend scenarios.

    Pre-shift (4:48 PM Tuesday):
      · Alley door area with Reggie's Tuesday delivery boxes
      · Citrus tray in prep on the back bar (lemon supremes on a
        white board, paring knife in the wooden apron holster)
      · Tape deck with the Tuesday playlist queued (a single
        cassette + a play-button-labelled boombox on the back bar)
      · The speed-rack inventory ledger on the back bar (paper on a
        clipboard · Trini's Sunday closeout in her handwriting)

    Last-call Friday (1:38 AM):
      · Bar stool C · the E-arm middle stool where the bachelor
        party lands · with an empty highball tipped on its side
      · Ice well · a rectangular chest sunk into the U-bar's N-cap
        top, currently at half capacity with visible dark bottom
      · Tickets rail · a horizontal spring-clip rail behind the bar
        with 3 drink tickets pinned to it (loose paper, canonical
        yellow-carbon look)
      · Back walk-in ice chest · a 40-pound blue cooler on the
        floor at the alley door (heavy, Frank has to carry it in)
    """
    # ── Pre-shift props ─────────────────────────────────────────

    # Alley door area · south-west corner where Wall_S_W meets Wall_W
    ax_door = -ROOM_W/2.0 + 0.20   # near the west wall
    ay_door = 0.50                  # just inside the alley door

    # Reggie's produce delivery · two stacked cardboard boxes
    make_box("PreShift_ProduceBox_Lo",
             (ax_door + 0.40, ay_door, 0.14),
             (0.28, 0.36, 0.28),
             (0.60, 0.48, 0.32, 1.0))
    make_box("PreShift_ProduceBox_Hi",
             (ax_door + 0.40, ay_door, 0.42),
             (0.28, 0.36, 0.24),
             (0.62, 0.50, 0.34, 1.0))
    # A bright-green stem sticking out of the top box (mint)
    make_cyl("PreShift_MintSprig",
             (ax_door + 0.40, ay_door + 0.02, 0.56),
             0.02, 0.10,
             (0.44, 0.68, 0.36, 1.0), segments=5)

    # Citrus prep tray on the back bar (west end)
    prep_x = -1.10
    prep_y = ROOM_D - 0.30
    prep_z = 1.22
    make_box("PreShift_CuttingBoard",
             (prep_x, prep_y, prep_z + 0.008),
             (0.32, 0.28, 0.016),
             (0.94, 0.88, 0.72, 1.0))
    # Three lemon supremes on the board
    for li, dx in enumerate([-0.08, 0.0, +0.08]):
        make_cyl("PreShift_LemonSupreme_%d" % li,
                 (prep_x + dx, prep_y, prep_z + 0.028),
                 0.035, 0.014,
                 (0.94, 0.86, 0.34, 1.0), segments=8)
    # Paring knife on the far side of the board
    make_box("PreShift_ParingKnife_Blade",
             (prep_x + 0.14, prep_y - 0.10, prep_z + 0.02),
             (0.008, 0.10, 0.012),
             (0.88, 0.90, 0.92, 1.0))
    make_box("PreShift_ParingKnife_Handle",
             (prep_x + 0.14, prep_y + 0.02, prep_z + 0.02),
             (0.018, 0.08, 0.018),
             (0.22, 0.14, 0.10, 1.0))

    # Boombox with Tuesday playlist cassette · east side of back bar
    tape_x = +0.90
    tape_y = ROOM_D - 0.35
    tape_z = 1.22
    make_box("PreShift_Boombox_Body",
             (tape_x, tape_y, tape_z + 0.08),
             (0.36, 0.14, 0.16),
             (0.14, 0.14, 0.16, 1.0))
    # Two speaker grilles
    for si, dx in enumerate([-0.11, +0.11]):
        make_cyl("PreShift_Boombox_Speaker_%d" % si,
                 (tape_x + dx, tape_y - 0.07, tape_z + 0.08),
                 0.05, 0.008,
                 (0.10, 0.10, 0.10, 1.0), segments=10, axis='Y')
    # Cassette door in the middle
    make_box("PreShift_Boombox_TapeDoor",
             (tape_x, tape_y - 0.07, tape_z + 0.08),
             (0.10, 0.008, 0.06),
             (0.28, 0.28, 0.30, 0.60))
    # Green "playing" LED
    make_cyl("PreShift_Boombox_LED",
             (tape_x - 0.15, tape_y - 0.07, tape_z + 0.14),
             0.006, 0.008,
             (0.42, 0.90, 0.50, 1.0), segments=6, axis='Y')

    # Speed-rack inventory ledger clipboard · on the back-bar counter
    lg_x = -0.20
    lg_y = ROOM_D - 0.40
    lg_z = 1.13
    make_box("PreShift_Ledger_Clip",
             (lg_x, lg_y, lg_z + 0.006),
             (0.20, 0.28, 0.010),
             (0.28, 0.24, 0.18, 1.0))
    make_box("PreShift_Ledger_Paper",
             (lg_x, lg_y, lg_z + 0.012),
             (0.18, 0.26, 0.001),
             (0.92, 0.88, 0.78, 1.0))
    # Trini's Sunday closeout · faint ruled lines
    for li in range(8):
        make_box("PreShift_Ledger_Line_%d" % li,
                 (lg_x, lg_y - 0.11 + li * 0.028, lg_z + 0.013),
                 (0.14, 0.001, 0.0005),
                 (0.32, 0.28, 0.22, 1.0))

    # ── Last-call Friday props ─────────────────────────────────

    # Bar stool C · E-arm middle stool (the bachelor party's landing)
    # Existing stools are at (+1.05, 4.60), (+1.05, 5.60), (+1.05, 6.60)
    # Stool C is the middle one at (+1.05, 5.60) · add a tipped
    # highball glass on the bar in front of it
    c_x = +1.05
    c_y = 5.60
    # Tipped highball on the bar top (bar top at z=1.06)
    make_cyl("LastCall_TippedHighball_Body",
             (+0.75, c_y, 1.09),
             0.028, 0.13,
             (0.86, 0.86, 0.88, 0.55),
             segments=10, axis='Y')     # laid on its side
    # A small puddle stain
    make_box("LastCall_HighballPuddle",
             (+0.65, c_y, 1.062),
             (0.06, 0.10, 0.002),
             (0.62, 0.36, 0.16, 0.70))

    # Ice well · sunken into the N-cap of the U-bar (0, 7.40, 1.06)
    # Rectangular chest cutout, currently at half capacity
    make_box("LastCall_IceWell_Frame",
             (0.0, 7.20, 1.05),
             (0.90, 0.36, 0.04),
             (0.62, 0.62, 0.64, 1.0))
    # Ice pile (half-full)
    make_box("LastCall_IceWell_Ice",
             (0.0, 7.20, 1.03),
             (0.86, 0.32, 0.10),
             (0.86, 0.92, 0.96, 0.80))
    # Small metal scoop resting on the ice
    make_cyl("LastCall_IceScoop_Handle",
             (+0.30, 7.30, 1.14),
             0.008, 0.16,
             (0.78, 0.80, 0.82, 1.0), segments=6, axis='Y')
    make_box("LastCall_IceScoop_Cup",
             (+0.20, 7.30, 1.10),
             (0.06, 0.08, 0.05),
             (0.78, 0.80, 0.82, 1.0))

    # Tickets rail · behind the bar's east arm, above the back bar
    rail_x = +1.50
    rail_y = ROOM_D - 0.30
    rail_z = 1.60
    make_box("LastCall_TicketsRail",
             (rail_x, rail_y, rail_z),
             (0.02, 0.60, 0.01),
             (0.62, 0.62, 0.62, 1.0))
    # Three tickets pinned to it (yellow-carbon look)
    for ti, dy in enumerate([-0.20, 0.0, +0.20]):
        make_box("LastCall_Ticket_%d" % ti,
                 (rail_x + 0.02, rail_y + dy, rail_z - 0.05),
                 (0.001, 0.10, 0.14),
                 (0.94, 0.86, 0.42, 1.0))
        # A small tear-off perforation line at the top
        make_box("LastCall_Ticket_%d_Perf" % ti,
                 (rail_x + 0.021, rail_y + dy, rail_z - 0.008),
                 (0.001, 0.09, 0.001),
                 (0.72, 0.66, 0.32, 1.0))

    # Back walk-in second ice chest · 40-pound blue cooler on the
    # floor near the alley door (Frank's job to haul in)
    make_box("LastCall_BackupIceChest_Body",
             (ax_door + 0.20, ay_door + 0.90, 0.24),
             (0.36, 0.30, 0.24),
             (0.30, 0.52, 0.78, 1.0))
    # Chest lid
    make_box("LastCall_BackupIceChest_Lid",
             (ax_door + 0.20, ay_door + 0.90, 0.38),
             (0.36, 0.30, 0.03),
             (0.28, 0.50, 0.76, 1.0))
    # Handle recess (a darker line on top)
    make_box("LastCall_BackupIceChest_HandleLine",
             (ax_door + 0.20, ay_door + 0.90, 0.40),
             (0.24, 0.02, 0.006),
             (0.18, 0.34, 0.58, 1.0))


def main():
    clear_scene()
    build_shell()
    build_u_bar()
    build_backbar()
    build_booths()
    build_neon_open()
    build_ceiling_infra()
    build_decor()
    build_temperance_dressing()
    build_temperance_wave2_props()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/mixing_glass.glb"))
    print(f"\n[build_mixing_glass] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
