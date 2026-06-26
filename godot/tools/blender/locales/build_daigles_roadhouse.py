"""XV · DEVIL — Daigle's Roadhouse. One-storey cinderblock bar at
the south HWY 90 strip. Pool table mid-room, juke against the W
wall, neon Schlitz behind the bar, mounted gator head over the
liquor shelves, sticky-floor honky-tonk fluorescents. Gumbo Limbo's
counterpart.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_faded_poster
from _props.safety import (make_smoke_detector, make_sprinkler,
                            make_fluorescent_tube_fixture, make_bug_zapper)

PAL = {"wall": (0.42, 0.36, 0.28, 1.0), "baseboard": (0.22, 0.18, 0.16, 1.0)}
COL_FLOOR = (0.32, 0.22, 0.16, 1.0); COL_SEAM = (0.18, 0.14, 0.12, 1.0)
COL_BAR = (0.32, 0.20, 0.14, 1.0); COL_BAR_TOP = (0.22, 0.14, 0.10, 1.0)
COL_POOL_FELT = (0.20, 0.42, 0.28, 1.0); COL_POOL_RAIL = (0.18, 0.12, 0.08, 1.0)
COL_JUKE_RED = (0.74, 0.22, 0.20, 1.0); COL_JUKE_CHROME = (0.78, 0.80, 0.82, 1.0)
COL_NEON_SCHLITZ = (0.86, 0.34, 0.20, 1.0); COL_GATOR = (0.32, 0.42, 0.28, 1.0)
COL_BEER_AMBER = (0.78, 0.42, 0.20, 1.0); COL_BEER_CLEAR = (0.86, 0.92, 0.86, 0.6)

ROOM_W = 9.0; ROOM_D = 7.5; CEIL = 2.70


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-3.0, 0.0, 0), length=3.0, height=CEIL, axis='X', palette=PAL)
    make_wall("Wall_S_E", (+3.0, 0.0, 0), length=3.0, height=CEIL, axis='X', palette=PAL)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),
                                    ("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),
                                    ("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_BAR})


def build_bar():
    # Bar runs along the N wall — 6m long.
    make_box("Bar_Top",  (0.0, ROOM_D-0.40, 1.10), (5.50, 0.50, 0.06), COL_BAR_TOP)
    make_box("Bar_Body", (0.0, ROOM_D-0.40, 0.55), (5.50, 0.50, 1.10), COL_BAR)
    # Back-bar shelves
    make_box("Backbar_Counter", (0.0, ROOM_D-0.10, 1.04), (5.20, 0.30, 0.04), COL_BAR)
    for si in range(3):
        sz = 1.30 + si * 0.36
        make_box(f"Backbar_Shelf_{si}", (0.0, ROOM_D-0.10, sz), (5.00, 0.24, 0.02), COL_BAR)
        for bi in range(20):
            bx = -2.30 + bi * 0.25
            bc = COL_BEER_AMBER if bi % 2 == 0 else COL_BEER_CLEAR
            make_cyl(f"Bottle_{si}_{bi}", (bx, ROOM_D-0.10, sz + 0.14), 0.035, 0.26, bc, segments=8)
    # Beer tap row at bar front
    for ti in range(4):
        tx = -1.20 + ti * 0.80
        make_cyl(f"Tap_{ti}_Stem", (tx, ROOM_D-0.50, 1.30), 0.025, 0.30, COL_JUKE_CHROME)
        make_box(f"Tap_{ti}_Handle", (tx, ROOM_D-0.50, 1.50), (0.06, 0.06, 0.20),
                 (0.42, 0.20, 0.16, 1.0))
    # 5 bar stools facing the bar (S side)
    for si in range(5):
        sx = -2.00 + si * 1.00
        sy = ROOM_D - 1.40
        make_cyl(f"Stool_{si}_Post", (sx, sy, 0.42), 0.04, 0.84, P.METAL_BLACK)
        make_cyl(f"Stool_{si}_Seat", (sx, sy, 0.86), 0.18, 0.06, (0.42, 0.20, 0.16, 1.0))
        make_cyl(f"Stool_{si}_Base", (sx, sy, 0.05), 0.20, 0.04, P.METAL_BLACK)


def build_pool_table():
    px, py = +1.50, 3.20
    # Pool table — felt + rails + 4 legs
    make_box("Pool_Felt", (px, py, 0.80), (1.40, 2.50, 0.04), COL_POOL_FELT)
    make_box("Pool_Rail_N", (px, py+1.30, 0.84), (1.60, 0.10, 0.10), COL_POOL_RAIL)
    make_box("Pool_Rail_S", (px, py-1.30, 0.84), (1.60, 0.10, 0.10), COL_POOL_RAIL)
    make_box("Pool_Rail_W", (px-0.75, py, 0.84), (0.10, 2.50, 0.10), COL_POOL_RAIL)
    make_box("Pool_Rail_E", (px+0.75, py, 0.84), (0.10, 2.50, 0.10), COL_POOL_RAIL)
    for sgn_x in (-1, +1):
        for sgn_y in (-1, +1):
            make_box(f"Pool_Leg_{sgn_x:+d}_{sgn_y:+d}", (px+sgn_x*0.62, py+sgn_y*1.10, 0.40),
                     (0.10, 0.10, 0.80), COL_POOL_RAIL)
    # Cue ball + a few coloured balls
    for bi, (bx, by, bc) in enumerate([(px, py+0.30, P.PAPER), (px+0.20, py+0.30, (0.96, 0.74, 0.20, 1.0)),
                                        (px-0.20, py-0.20, (0.74, 0.22, 0.20, 1.0)),
                                        (px+0.10, py-0.40, (0.18, 0.34, 0.62, 1.0))]):
        make_cyl(f"Pool_Ball_{bi}", (bx, by, 0.84), 0.05, 0.10, bc, axis='Y', segments=8)
    # Cue stick leaning on the side
    make_box("Pool_Cue", (px+0.80, py-0.80, 1.20), (0.025, 0.025, 1.40), (0.62, 0.46, 0.26, 1.0))


def build_jukebox():
    # Old-school jukebox against the W wall
    jx, jy = -ROOM_W/2.0 + 0.40, 4.20
    make_box("Juke_Body", (jx, jy, 0.80, ), (0.50, 0.60, 1.60), COL_JUKE_RED)
    make_box("Juke_Top", (jx, jy, 1.70), (0.50, 0.60, 0.20), COL_JUKE_CHROME)
    # Arched dome
    for ai in range(4):
        make_cyl(f"Juke_Arch_{ai}", (jx, jy - 0.20 + ai*0.15, 1.84), 0.18, 0.04,
                 COL_JUKE_CHROME, axis='X', segments=8)
    # Speaker grilles
    for gi in range(3):
        make_box(f"Juke_Grille_{gi}", (jx+0.26, jy, 0.50 + gi*0.30),
                 (0.005, 0.40, 0.20), (0.20, 0.16, 0.14, 1.0))
    # Selection panel
    make_box("Juke_Panel", (jx+0.26, jy, 1.30), (0.005, 0.46, 0.20), (0.86, 0.78, 0.42, 1.0))


def build_neon_schlitz():
    # Iconic neon over the bar centerline
    make_box("Neon_Schlitz_BG", (0.0, ROOM_D-0.06, 2.20), (1.40, 0.04, 0.40), COL_NEON_SCHLITZ)
    make_box("Neon_Schlitz_Letters", (0.0, ROOM_D-0.08, 2.20), (0.005, 1.20, 0.24), P.PAPER)
    # Smaller "BEER" neon next to it
    make_box("Neon_Beer_BG", (-2.20, ROOM_D-0.06, 2.20), (0.80, 0.04, 0.30), (0.96, 0.72, 0.20, 1.0))
    make_box("Neon_Beer_Letters", (-2.20, ROOM_D-0.08, 2.20), (0.005, 0.64, 0.18), P.PAPER)


def build_gator_head():
    # Mounted gator head on a plaque, above the backbar (S-facing)
    gx, gy = +2.30, ROOM_D - 0.12
    make_box("Gator_Plaque", (gx, gy, 2.50), (0.50, 0.04, 0.30), (0.32, 0.20, 0.14, 1.0))
    # Skull-like elongated form
    make_box("Gator_Snout", (gx, gy-0.30, 2.50), (0.20, 0.60, 0.15), COL_GATOR)
    make_box("Gator_Jaw", (gx, gy-0.30, 2.42), (0.20, 0.50, 0.06), COL_GATOR)
    # Teeth row (top)
    for ti in range(6):
        tx = gx - 0.08 + ti * 0.032
        make_box(f"Gator_Tooth_{ti}", (tx, gy-0.50, 2.46), (0.018, 0.04, 0.04), P.PAPER)


def build_ceiling_infra():
    for j, ypos in enumerate([2.0, 4.5]):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL),
                                       length=1.80, width=0.32,
                                       palette={"diffuser": (0.96, 0.86, 0.62, 1.0)})
    make_bug_zapper("BugZap", (-ROOM_W/2.0+0.20, 6.50, 2.30))
    make_smoke_detector("Smoke", (0.0, 3.5, CEIL))
    make_sprinkler("Spr_N", (-1.5, 6.0, CEIL))
    make_sprinkler("Spr_S", (+1.5, 2.0, CEIL))


def build_decor():
    make_wall_clock("Clock", (-ROOM_W/2.0+0.05, 5.5, 2.20), frozen_hour=4, frozen_min=15)
    make_faded_poster("Poster_S", (+ROOM_W/2.0-0.05, 5.0, 1.50))
    # Cardboard corkboard with stapled notices near the front (E wall)
    make_box("Corkboard", (+ROOM_W/2.0-0.04, 1.7, 1.50), (0.04, 0.80, 0.60), (0.62, 0.46, 0.32, 1.0))
    for ni in range(4):
        nx = +ROOM_W/2.0 - 0.06
        ny = 1.40 + (ni % 2) * 0.30
        nz = 1.30 + (ni // 2) * 0.30
        make_box(f"Notice_{ni}", (nx, ny, nz), (0.005, 0.18, 0.14), (0.92, 0.86, 0.74, 1.0))


def build_devil_dressing():
    """Scene-description specifics from setup_one_more_round.json:
      · "Lou polishing a glass that was already clean" · a glass
        and a folded white bar towel on the bar in front of Lou's
        canonical station
      · "Your tab is on the brass clip nearest the register" · a
        paper tab on a brass clip, near the cash register
      · "The pool table is set up but unplayed since 11" · already
        built — augment with racked balls + a cue resting on the
        rail
      · Your stool · the one you've been on every Tuesday for a
        year · with a soft circular wear on the seat
      · A door-counter sign on the front door · "6 STEPS" (the
        canonical line: "six steps from your stool")
    """
    # Bar approx along Y = -3.5; Lou's station at around (-1.5, -3.5)
    bar_cy = -3.5
    bar_top_z = 1.05

    # Lou's polished glass + bar towel
    lou_x = -1.5
    # Highball glass (squeaky clean)
    make_cyl("LouGlass_Body",
             (lou_x, bar_cy + 0.10, bar_top_z + 0.06),
             0.030, 0.13,
             (0.86, 0.86, 0.88, 0.55),
             segments=8, axis='Z')
    # Folded bar towel
    make_box("LouTowel_Folded",
             (lou_x + 0.20, bar_cy + 0.10, bar_top_z + 0.012),
             (0.18, 0.10, 0.020),
             (0.92, 0.88, 0.78, 1.0))

    # Brass tab clip near the register · paper tab hanging from it
    # Register approx at (+2.0, bar_cy)
    reg_x = +2.0
    # Wall-mounted clip strip just behind the bar (north side of bar)
    make_box("TabClip_Strip",
             (reg_x - 0.40, bar_cy + 0.50, bar_top_z + 0.22),
             (0.40, 0.04, 0.04),
             (0.42, 0.32, 0.20, 1.0))
    # 4 brass clips on the strip
    for ci, cx_off in enumerate([-0.16, -0.05, +0.05, +0.16]):
        make_box("TabClip_%d" % ci,
                 (reg_x - 0.40 + cx_off, bar_cy + 0.48, bar_top_z + 0.22),
                 (0.04, 0.005, 0.04),
                 (0.78, 0.62, 0.30, 1.0))
    # The tab paper hanging from the clip nearest the register (rightmost)
    tab_x = reg_x - 0.40 + 0.16
    make_box("MyTab_Paper",
             (tab_x, bar_cy + 0.481, bar_top_z + 0.10),
             (0.08, 0.001, 0.20),
             (0.94, 0.90, 0.80, 1.0))
    # Tally marks on the tab — 6 darker hashes (one for each round you remember + 1)
    for hi in range(6):
        make_box("MyTab_Hash_%d" % hi,
                 (tab_x - 0.025 + (hi % 3) * 0.025,
                  bar_cy + 0.4815,
                  bar_top_z + 0.12 - (hi // 3) * 0.04),
                 (0.005, 0.0005, 0.020),
                 (0.20, 0.16, 0.12, 1.0))

    # Pool table augmentation — racked balls + a cue on the rail
    # Pool table approx at (+2.0, +1.0)
    pt_cx = +2.0
    pt_cy = +1.0
    pt_top_z = 0.78
    # Triangular rack at the foot end
    rack_x = pt_cx
    rack_y = pt_cy - 0.50
    # 15 balls + 1 cue ball stacked in a triangle (5+4+3+2+1)
    bi = 0
    for row in range(5):
        for col in range(5 - row):
            bx = rack_x - 0.06 * (5 - row - 1) / 2.0 + col * 0.06
            by = rack_y - row * 0.052
            # Alternate colors so the rack reads as racked-up
            ball_colors = [
                (0.96, 0.82, 0.20, 1.0),   # 1 yellow
                (0.20, 0.36, 0.82, 1.0),   # 2 blue
                (0.86, 0.16, 0.14, 1.0),   # 3 red
                (0.42, 0.20, 0.62, 1.0),   # 4 purple
                (0.96, 0.52, 0.20, 1.0),   # 5 orange
                (0.20, 0.46, 0.22, 1.0),   # 6 green
                (0.62, 0.20, 0.18, 1.0),   # 7 dark red
                (0.10, 0.08, 0.08, 1.0),   # 8 black
            ]
            color = ball_colors[bi % 8]
            make_cyl("PoolBall_%d" % bi,
                     (bx, by, pt_top_z + 0.028),
                     0.028, 0.056,
                     color, segments=8, axis='Z')
            bi += 1
    # Cue ball at the head end
    make_cyl("PoolBall_Cue",
             (pt_cx, pt_cy + 0.60, pt_top_z + 0.028),
             0.028, 0.056,
             (0.94, 0.92, 0.88, 1.0), segments=8, axis='Z')
    # Cue resting on the side rail (along the east rail)
    make_cyl("PoolCue_Shaft",
             (pt_cx + 0.50, pt_cy, pt_top_z + 0.06),
             0.012, 1.40,
             (0.74, 0.62, 0.42, 1.0), segments=6, axis='Y')
    # Cue tip
    make_cyl("PoolCue_Tip",
             (pt_cx + 0.50, pt_cy + 0.70, pt_top_z + 0.06),
             0.014, 0.04,
             (0.42, 0.28, 0.16, 1.0), segments=6, axis='Y')

    # "Your stool" with the worn seat ring
    # Stool approx at (0.0, -2.6) — across the bar from Lou
    stool_x = 0.0
    stool_y = bar_cy + 0.80
    # Stool seat (round disc, oxblood leather)
    make_cyl("YourStool_Seat",
             (stool_x, stool_y, 0.74),
             0.18, 0.06,
             (0.42, 0.20, 0.16, 1.0),
             segments=10, axis='Z')
    # A darker wear-ring on the seat (the canon weekly groove)
    make_cyl("YourStool_WearRing",
             (stool_x, stool_y, 0.77),
             0.14, 0.002,
             (0.32, 0.16, 0.12, 1.0),
             segments=10, axis='Z')
    # 4 chrome legs
    for sgn_x, sgn_y in [(-1, -1), (+1, -1), (-1, +1), (+1, +1)]:
        make_cyl("YourStool_Leg_%+d_%+d" % (sgn_x, sgn_y),
                 (stool_x + sgn_x * 0.14, stool_y + sgn_y * 0.14, 0.36),
                 0.014, 0.72,
                 (0.62, 0.62, 0.60, 1.0),
                 segments=6, axis='Z')

    # "6 STEPS" sign on the front door
    # Front door approx at (0.0, +5.4, south interior of front wall)
    door_x = 0.0
    door_y = +5.40
    make_box("SixSteps_Sign_Backing",
             (door_x, door_y - 0.012, 1.60),
             (0.20, 0.005, 0.10),
             (0.92, 0.88, 0.78, 1.0))
    # Six small dark hash marks above the larger "6 STEPS" line
    for ci in range(6):
        make_box("SixSteps_Hash_%d" % ci,
                 (door_x - 0.08 + ci * 0.032, door_y - 0.013, 1.62),
                 (0.014, 0.0005, 0.010),
                 (0.18, 0.16, 0.10, 1.0))
    # Bigger text line "STEPS" below
    make_box("SixSteps_TextLine",
             (door_x, door_y - 0.013, 1.58),
             (0.16, 0.0005, 0.020),
             (0.18, 0.16, 0.10, 1.0))


def main():
    clear_scene()
    build_shell()
    build_bar()
    build_pool_table()
    build_jukebox()
    build_neon_schlitz()
    build_gator_head()
    build_ceiling_infra()
    build_decor()
    build_devil_dressing()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/daigles_roadhouse.glb"))
    print(f"\n[build_daigles_roadhouse] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
