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
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/mixing_glass.glb"))
    print(f"\n[build_mixing_glass] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
