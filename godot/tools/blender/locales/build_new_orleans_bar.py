"""VOL 5 · New Orleans Bar — cameo. Long mahogany bar, brass rail,
bottle wall, pendant lamps, jukebox in corner.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb, make_tube, make_dome, make_taper_cyl
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window, make_wall_with_openings
from _props.store_fixtures import make_counter, make_counter_bullnose
from _props.decor import make_wall_clock
from _props.safety import make_fluorescent_tube_fixture, make_smoke_detector, make_ceiling_speaker
from _props.objects import make_liquor_bottle, make_bowl

PAL = {"wall": (0.42, 0.30, 0.22, 1.0), "baseboard": (0.18, 0.12, 0.10, 1.0)}
COL_FLOOR = (0.32, 0.22, 0.16, 1.0); COL_SEAM = (0.18, 0.12, 0.10, 1.0)
COL_BAR = (0.42, 0.28, 0.18, 1.0); COL_TOP = (0.22, 0.14, 0.10, 1.0); COL_BRASS = (0.86, 0.62, 0.28, 1.0)
COL_BOTTLE_AMBER = (0.78, 0.42, 0.16, 1.0); COL_BOTTLE_CLEAR = (0.78, 0.84, 0.86, 0.55); COL_BOTTLE_GREEN = (0.32, 0.42, 0.20, 1.0)
ROOM_W = 9.0; ROOM_D = 6.0; CEIL = 3.20

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1)
    # (2026-10-03: CUT round the street windows — solid behind the panes before)
    make_wall_with_openings("Wall_S_W", (-3.0, 0.0, 0), length=2.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=+1,
                            openings=[(-3.0, 1.60, 1.00, 1.20)])
    make_wall_with_openings("Wall_S_E", (+3.0, 0.0, 0), length=2.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=+1,
                            openings=[(3.0, 1.60, 1.00, 1.20)])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"tile": (0.30, 0.22, 0.14, 1.0), "grid": (0.18, 0.12, 0.10, 1.0)})
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10),("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_BRASS})
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    make_window("Window_SW", (-3.0, 0.10, 1.60), width=1.00, height=1.20, room_dir=+1)
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    make_window("Window_SE", (+3.0, 0.10, 1.60), width=1.00, height=1.20, room_dir=+1)

def build_bar():
# make_counter's `depth` is the X extent and `length` is Y —
    # so length=7.0/depth=1.20 built this bar ROTATED 90 DEGREES:
    # a 7m counter running north-south, 1.65m of it through the
    # north wall, with all five stools embedded in its flank.
    # (Found 2026-08-12, once shared-module geometry recorded.)
    top_z = make_counter("Bar", (0.0, 4.15, 0.0), length=1.20, depth=7.0, height=1.10, palette={"formica": COL_BAR, "top": COL_TOP, "kick": (0.18, 0.10, 0.06, 1.0)})
    make_counter_bullnose("Bar", (0.0, 3.55, top_z), length=7.0,
                          palette={"top": COL_TOP}, axis='X')
    # Brass foot rail (cylinder along south face)
    make_cyl("Bar_FootRail", (0.0, 3.52, 0.18), 0.025, 7.0, COL_BRASS, axis='X', segments=8)
    # 5 bar stools (south side)
    for si, sx in enumerate([-2.4, -1.2, 0.0, +1.2, +2.4]):
        make_cyl(f"Stool_{si}_Seat", (sx, 3.20, 0.78), 0.18, 0.06, COL_BAR)
        make_cyl(f"Stool_{si}_Pillar", (sx, 3.20, 0.40), 0.04, 0.74, COL_BRASS)
        make_cyl(f"Stool_{si}_Foot", (sx, 3.20, 0.02), 0.16, 0.04, COL_BRASS)   # on the floor (2026-09-22: 2 cm up)
    # Bottle wall north of bar (mounted shelves)
    for shf in range(3):
        sz = top_z + 0.30 + shf*0.40
        # mounted ON the mirror's face, short of the TV (2026-09-22: 40 cm off the wall)
        make_box(f"Bottle_Shelf_{shf}", (-0.65, 5.78, sz), (5.1, 0.20, 0.02), COL_TOP)
        for bi in range(16):
            bx = -3.0 + bi*0.32
            tint = [COL_BOTTLE_AMBER, COL_BOTTLE_CLEAR, COL_BOTTLE_GREEN][(shf+bi)%3]
            make_liquor_bottle(f"Bottle_{shf}_{bi}", bx, 5.78, sz + 0.01,
                               tint, h=0.24 + ((shf + bi) % 3) * 0.035,
                               r=0.033)
    # Back mirror (long horizontal — bartender's reflection canon)
    make_box("Bar_Mirror", (-0.65, 5.89, top_z+0.85), (5.1, 0.02, 1.50), (0.78, 0.84, 0.86, 0.85))   # on the wall; ends where the TV hangs

def build_jukebox():
    # Wurlitzer-style jukebox SE corner
    jx, jy = +3.80, 1.20
    make_box("Jukebox_Body", (jx, jy, 0.75), (0.80, 0.60, 1.50), (0.78, 0.42, 0.16, 1.0))
    make_box("Jukebox_TopArch", (jx, jy, 1.70), (0.80, 0.60, 0.40), (0.62, 0.32, 0.14, 1.0))
    make_box("Jukebox_Glass", (jx, jy-0.31, 1.10), (0.70, 0.04, 0.50), (0.32, 0.22, 0.18, 0.55))
    make_box("Jukebox_LightBar", (jx, jy-0.32, 1.50), (0.70, 0.02, 0.10), (0.96, 0.78, 0.42, 1.0))

def build_decor():
    make_wall_clock("Clock", (0.0, 5.900, 2.60), frozen_hour=11, frozen_min=47, facing='-Y')
    # Pendant lamps over bar
    for pi, px in enumerate([-2.0, 0.0, +2.0]):
        make_cyl(f"Pendant_{pi}_Cord", (px, 4.5, CEIL-0.25), 0.005, 0.50, P.METAL_BLACK)   # ceiling to shade (2026-09-22: 10 cm short of both)
        make_box(f"Pendant_{pi}_Shade", (px, 4.5, CEIL-0.65), (0.30, 0.30, 0.30), (0.92, 0.74, 0.32, 1.0))

def build_ceiling_fan():
    # Slow-turning ceiling fan with a warm light kit (jazz-club canon).
    fx, fy, fz = 0.0, 3.0, CEIL - 0.15
    make_cyl("Fan_Downrod", (fx, fy, fz), 0.02, 0.30, P.METAL_BLACK)   # to the ceiling (2026-09-22: 2 cm short)
    make_cyl("Fan_Motor", (fx, fy, fz - 0.23), 0.12, 0.14, COL_BRASS, segments=12)
    blades = [(0.46, fy, 0.66, 0.16), (-0.46, fy, 0.66, 0.16),
              (fx, fy+0.46, 0.16, 0.66), (fx, fy-0.46, 0.16, 0.66)]
    for bi, (bx, by, sw, sd) in enumerate(blades):
        make_box(f"Fan_Blade_{bi}", (bx, by, fz - 0.30), (sw, sd, 0.02), (0.36, 0.24, 0.14, 1.0))
    make_cyl("Fan_LightKit", (fx, fy, fz - 0.36), 0.09, 0.12, (0.96, 0.84, 0.62, 1.0), segments=12)   # on the motor

def build_ceiling_infra():
    # A grimy dive lights by neon, TV glow and low pendants — no
    # shop tubes
    for pi, (px, py) in enumerate(((-2.0, 2.2), (2.0, 2.2))):
        # (2026-09-22: these shared the bar pendants' names — Lamp_ now; shade on the cord, bulb in the shade)
        make_cyl(f"Lamp_{pi}_Cord", (px, py, CEIL-0.16), 0.008, 0.32, P.METAL_BLACK)
        make_cyl(f"Lamp_{pi}_Shade", (px, py, CEIL-0.39), 0.15, 0.14, (0.30, 0.24, 0.18, 1.0), segments=12)
        make_cyl(f"Lamp_{pi}_Bulb", (px, py, CEIL-0.47), 0.05, 0.06, (1.0, 0.80, 0.45, 1.0), segments=8)


def build_hero_props():
    """2026-08-03 hero-prop pass: the muted bar TV (Strength's
    refrain), the cheap-vinyl corner booth + saltshaker + folded
    twenty + empties, three neon beer signs (two dead brands), the
    CHALK TABLE (vol1's pool table) + cue rack, the pinball machine
    + the Missile Command cabinet, and a six-top for the vol1
    party."""
    vinyl = (0.36, 0.20, 0.18, 1.0)
    wood = (0.35, 0.24, 0.15, 1.0)
    felt = (0.16, 0.36, 0.24, 1.0)
    # The bar TV, muted, over the back bar
    make_box("Bar_TV", (2.6, 5.86, 2.30), (1.10, 0.08, 0.62), (0.10, 0.10, 0.12, 1.0))   # on the wall (2026-09-22: 6 cm off it)
    make_box("Bar_TV_Screen", (2.6, 5.81, 2.30), (0.98, 0.02, 0.52), (0.32, 0.40, 0.36, 1.0))
    # Corner booth SW: L-benches + table + the props on it
    make_box("Booth_Bench_W", (-4.15, 1.6, 0.30), (0.55, 1.9, 0.46), vinyl)
    make_box("Booth_Back_W", (-4.38, 1.6, 0.80), (0.10, 1.9, 0.70), vinyl)
    make_box("Booth_Bench_S", (-3.1, 0.55, 0.30), (1.6, 0.55, 0.46), vinyl)
    make_box("Booth_Back_S", (-3.1, 0.32, 0.80), (1.6, 0.10, 0.70), vinyl)
    make_box("Booth_Table", (-3.4, 1.35, 0.74), (1.10, 0.75, 0.05), wood)
    make_box("Booth_Table_Leg", (-3.4, 1.35, 0.37), (0.10, 0.10, 0.72), (0.20, 0.19, 0.20, 1.0))
    # The booth's own light (2026-10-05): a wall sconce over the table on
    # the west wall — Doug's corner had only the room's pendants.
    make_box("Booth_Sconce_Plate", (-4.39, 1.35, 1.78), (0.02, 0.14, 0.22), (0.30, 0.24, 0.16, 1.0))
    make_box("Booth_Sconce_Arm", (-4.32, 1.35, 1.80), (0.12, 0.02, 0.02), (0.30, 0.24, 0.16, 1.0))
    make_taper_cyl("Booth_Sconce_Shade", (-4.20, 1.35, 1.80), 0.09, 0.05, 0.14, (0.86, 0.56, 0.28, 1.0), segments=10)
    make_cyl("Saltshaker", (-3.25, 1.30, 0.80), 0.022, 0.08, (0.88, 0.88, 0.84, 0.9), segments=8)
    make_box("Folded_Twenty", (-3.25, 1.30, 0.8286), (0.05, 0.035, 0.006), (0.55, 0.62, 0.50, 1.0))
    for bi, (bx, by) in enumerate(((-3.6, 1.5), (-3.15, 1.55))):
        make_cyl(f"Empty_Bottle_{bi}", (bx, by, 0.86), 0.03, 0.20, (0.36, 0.26, 0.14, 0.8), segments=8)
    # Three neon beer signs on the W wall — two dead brands, one live
    for ni, (ny, col) in enumerate(((1.4, (0.86, 0.32, 0.34, 1.0)), (2.8, (0.30, 0.72, 0.62, 1.0)),
                                    (4.2, (0.90, 0.70, 0.28, 1.0)))):
        make_box(f"BeerNeon_{ni}_Box", (-4.42, ny, 2.05), (0.06, 0.85, 0.45), (0.14, 0.12, 0.14, 1.0))
        make_box(f"BeerNeon_{ni}_Tube", (-4.38, ny, 2.05), (0.03, 0.65, 0.28), col)
    # THE CHALK TABLE — vol1's pool table + the cue rack
    make_box("Chalk_Table_Body", (-2.2, 1.9, 0.62), (2.24, 1.24, 0.36), wood)
    make_box("Chalk_Table_Felt", (-2.2, 1.9, 0.805), (2.02, 1.02, 0.02), felt)
    make_box("Chalk_Table_Rail", (-2.2, 1.9, 0.80), (2.24, 1.24, 0.05), (0.28, 0.19, 0.12, 1.0))
    for lx, ly in ((-3.15, 1.4), (-1.25, 1.4), (-3.15, 2.4), (-1.25, 2.4)):
        make_box(f"Chalk_Leg_{lx:.2f}_{ly:.1f}", (lx, ly, 0.30), (0.14, 0.14, 0.60), wood)
    for bi in range(3):
        make_cyl(f"Pool_Ball_{bi}", (-2.4 + bi * 0.22, 1.85 + 0.1 * (bi % 2), 0.845), 0.028, 0.056,
                 [(0.86, 0.82, 0.74, 1.0), (0.72, 0.22, 0.18, 1.0), (0.14, 0.14, 0.16, 1.0)][bi], segments=8)
    make_box("Cue_Rack", (-4.42, 0.9, 1.35), (0.06, 0.60, 1.10), wood)
    for ci in range(4):
        make_cyl(f"Cue_{ci}", (-4.38, 0.72 + ci * 0.12, 1.35), 0.012, 1.00, (0.66, 0.52, 0.34, 1.0), segments=5)
    # Pinball + Missile Command along the E wall
    make_box("Pinball_Body", (4.05, 3.1, 0.72), (0.72, 1.35, 0.35), (0.62, 0.26, 0.30, 1.0))
    make_box("Pinball_Glass", (4.05, 3.1, 0.92), (0.66, 1.25, 0.03), (0.55, 0.62, 0.66, 0.4))
    make_box("Pinball_Backbox", (4.05, 3.72, 1.50), (0.70, 0.16, 0.70), (0.70, 0.32, 0.36, 1.0))
    for li in range(4):
        make_box(f"Pinball_Leg_{li}", (3.80 + 0.5 * (li % 2), 2.55 + 1.1 * (li // 2), 0.28),
                 (0.05, 0.05, 0.56), (0.55, 0.57, 0.58, 1.0))
    make_box("MissileCmd_Cab", (4.10, 4.5, 0.88), (0.70, 0.80, 1.75), (0.16, 0.16, 0.20, 1.0))
    make_box("MissileCmd_Screen", (3.78, 4.5, 1.25), (0.05, 0.55, 0.42), (0.14, 0.30, 0.22, 1.0))
    make_box("MissileCmd_Marquee", (3.80, 4.5, 1.68), (0.05, 0.62, 0.18), (0.80, 0.30, 0.24, 1.0))
    make_box("MissileCmd_Panel", (3.72, 4.5, 0.90), (0.16, 0.60, 0.06), (0.24, 0.24, 0.28, 1.0))
    # A six-top for the vol1 party
    make_cyl("Group_Table", (0.6, 1.75, 0.725), 0.65, 0.05, wood, segments=14)
    make_cyl("Group_Table_Post", (0.6, 1.75, 0.35), 0.07, 0.70, (0.20, 0.19, 0.20, 1.0), segments=8)   # floor to top (2026-09-22: 2 cm up)
    import math as _m
    for ci in range(6):
        ang = ci * (2.0 * _m.pi / 6.0) + 0.3
        cx, cy = 0.6 + _m.cos(ang) * 1.0, 1.9 + _m.sin(ang) * 1.0
        make_box(f"Group_Chair_{ci}_Seat", (cx, cy, 0.44), (0.38, 0.38, 0.04), wood)
        # legs (2026-09-08)
        for lx_ in (-1, 1):
            for ly_ in (-1, 1):
                make_box(f"Group_Chair_{ci}_Leg_{lx_:+d}_{ly_:+d}",
                         (cx + lx_ * 0.15, cy + ly_ * 0.15, 0.22),
                         (0.035, 0.035, 0.44), wood)
        make_box(f"Group_Chair_{ci}_Back", (0.6 + _m.cos(ang) * 1.17, 1.9 + _m.sin(ang) * 1.17, 0.70),
                 (0.38, 0.05, 0.48), wood)


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    Three distinct cues. Built:

    - THE BAR TV already existed in the 2026-08 hero pass — the
      cue missed it because "tv" is under the matcher's 3-char
      stem floor. Fixed with a SYNONYMS entry (tv -> bar_tv,
      television), no new geometry.
    - THE HANDS ("His hands rested on the sticky tabletop"):
      residue grammar — two faint sticky sheen patches on the
      corner booth's table where hands keep resting.

    The tattoo cue (the ouroboros on Douglas's forearm) is ON A
    PERSON — no honest anchor exists in the room; it stays
    deliberately blind and VnDirector holds the wide (the
    closeup_douglas precedent).
    """
    make_box("Hands_Sticky_Patch_A", (-3.30, 1.25, 0.7664), (0.14, 0.11, 0.0015),
             (0.38, 0.30, 0.22, 1.0))
    make_box("Hands_Sticky_Patch_B", (-3.52, 1.42, 0.7664), (0.11, 0.13, 0.0015),
             (0.36, 0.28, 0.21, 1.0))


def build_dive_2026_10():
    """CHARACTER PASS (2026-10-03). The chapter: "the bar TV … Muted …
    under the buzzing neon of three different beer signs, two of which
    had … His hands rested on the sticky tabletop … the cheap vinyl …
    the saltshaker … a tired-looking woman behind the bar … deliveries
    coming through the back door." A Marigny dive: the taps and the
    bar's clutter, a COLD BEER neon over the mirror, string lights,
    Mardi Gras beads on the mirror and the TV, a dartboard and its
    chalk scores, the gator on the wall, the specials board, the back
    door with its RESTROOM sign, and the street at night outside the
    windows."""
    wood = (0.35, 0.24, 0.15, 1.0)
    brass = COL_BRASS
    top = 1.16
    # ── on the bar: the taps, the mat, the tip jar, napkins, ashtrays, peanuts, the register
    make_box("Tap_Tower", (-0.70, 4.30, top + 0.14), (0.42, 0.10, 0.28), (0.72, 0.72, 0.74, 1.0))
    for i, tx in enumerate((-0.84, -0.70, -0.56)):
        make_cyl(f"Tap_{i}_Spout", (tx, 4.22, top + 0.16), 0.012, 0.08, brass, segments=6, axis='Y')
        make_cyl(f"Tap_{i}_Handle", (tx, 4.30, top + 0.36), 0.018, 0.16, [(0.86, 0.20, 0.18, 1.0), (0.14, 0.14, 0.16, 1.0), (0.92, 0.84, 0.40, 1.0)][i], segments=6)
    make_box("Bar_Mat", (-0.70, 3.95, top + 0.006), (0.60, 0.28, 0.012), (0.12, 0.12, 0.14, 1.0))
    make_cyl("Tip_Jar", (0.30, 4.35, top + 0.08), 0.06, 0.16, (0.78, 0.84, 0.86, 0.5), segments=10)
    make_box("Tip_Jar_Bills", (0.30, 4.35, top + 0.05), (0.07, 0.05, 0.08), (0.56, 0.62, 0.50, 1.0))
    for i, nx in enumerate((-2.0, 1.4)):
        make_box(f"Napkin_Dispenser_{i}", (nx, 4.40, top + 0.07), (0.14, 0.09, 0.14), (0.62, 0.62, 0.64, 1.0))
        make_box(f"Napkin_{i}", (nx, 4.345, top + 0.07), (0.10, 0.004, 0.09), (0.94, 0.94, 0.90, 1.0))
    for i, ax in enumerate((-1.5, 0.9)):
        make_cyl(f"Bar_Ashtray_{i}", (ax, 3.90, top + 0.015), 0.055, 0.03, (0.30, 0.30, 0.32, 1.0), segments=10)
    make_bowl("Peanut_Bowl", 2.2, 3.95, top, (0.46, 0.40, 0.32, 1.0), r=0.09, h=0.05)
    make_box("Register", (2.0, 4.50, top + 0.14), (0.40, 0.36, 0.28), (0.62, 0.62, 0.60, 1.0))
    make_box("Register_Keys", (2.0, 4.33, top + 0.19), (0.30, 0.02, 0.10), (0.30, 0.30, 0.32, 1.0))
    make_box("Register_Drawer", (2.0, 4.31, top + 0.05), (0.36, 0.02, 0.08), (0.50, 0.50, 0.48, 1.0))
    # ── the glass rack over the bar
    make_box("Glass_Rack", (0.0, 4.15, 2.30), (3.0, 0.40, 0.03), wood)
    for i in range(4):
        make_cyl(f"Glass_Rack_Rail_{i}", (0.0, 4.00 + i * 0.10, 2.27), 0.008, 3.0, brass, segments=6, axis='X')
    for i in range(14):
        make_cyl(f"Hung_Glass_{i}", (-1.3 + i * 0.2, 4.05 + (i % 3) * 0.10, 2.18), 0.035, 0.14, (0.80, 0.86, 0.88, 0.5), segments=8)
    for i, cx in enumerate((-1.3, 1.3)):
        make_cyl(f"Glass_Rack_Chain_{i}", (cx, 4.15, 2.76), 0.006, 0.88, (0.30, 0.30, 0.32, 1.0), segments=5)
    # ── neon: COLD BEER over the mirror; the string lights along the north wall
    make_box("ColdBeer_Box", (-0.65, 5.92, 3.0), (1.40, 0.06, 0.36), (0.14, 0.12, 0.14, 1.0))
    make_box("ColdBeer_Tube", (-0.65, 5.88, 3.0), (1.10, 0.02, 0.16), (0.30, 0.78, 0.96, 1.0))
    make_tube("String_Lights", [(-4.3, 5.86, 2.95), (-2.5, 5.86, 2.80), (-0.7, 5.86, 2.95), (1.1, 5.86, 2.80), (2.9, 5.86, 2.95), (4.3, 5.86, 2.82)], 0.005, (0.16, 0.16, 0.18, 1.0), segments=4)
    for i in range(14):
        sx = -4.1 + i * 0.6
        sz = 2.95 - 0.15 * abs(((sx + 4.3) % 3.6) / 1.8 - 1.0) * 1.0
        make_cyl(f"String_Bulb_{i}", (sx, 5.86, sz - 0.05), 0.02, 0.05, [(0.96, 0.82, 0.40, 1.0), (0.90, 0.40, 0.44, 1.0), (0.44, 0.86, 0.60, 1.0)][i % 3], segments=6)
    # ── Mardi Gras beads on the mirror and the TV
    for i, (x0, x1, z, col) in enumerate(((-2.8, -1.6, 2.55, (0.60, 0.26, 0.74, 1.0)), (-1.4, -0.2, 2.50, (0.26, 0.70, 0.36, 1.0)), (0.2, 1.4, 2.55, (0.92, 0.78, 0.22, 1.0)), (2.1, 3.1, 2.76, (0.60, 0.26, 0.74, 1.0)))):   # the last over the TV's top edge
        make_tube(f"Beads_{i}", [(x0, 5.86, z + 0.18), ((x0 + x1) / 2.0, 5.84, z - 0.12), (x1, 5.86, z + 0.18)], 0.012, col, segments=6)
    # ── dartboard and the chalk scores on the east wall; the specials board on the north
    make_cyl("Dartboard", (ROOM_W / 2.0 - 0.125, 2.0, 1.73), 0.23, 0.04, (0.20, 0.18, 0.16, 1.0), segments=16, axis='X')
    make_cyl("Dartboard_Bull", (ROOM_W / 2.0 - 0.148, 2.0, 1.73), 0.03, 0.006, (0.80, 0.20, 0.18, 1.0), segments=10, axis='X')
    for i in range(6):
        make_box(f"Dartboard_Wedge_{i}", (ROOM_W / 2.0 - 0.147, 2.0 + 0.14 * (1 if i % 2 else -1) * (0.5 + 0.5 * (i // 2)) * 0.4, 1.73 + 0.12 * ((i // 2) - 1)), (0.004, 0.05, 0.05), (0.86, 0.82, 0.70, 1.0) if i % 2 else (0.20, 0.48, 0.30, 1.0))
    make_box("Score_Board", (ROOM_W / 2.0 - 0.112, 1.30, 1.70), (0.012, 0.40, 0.50), (0.12, 0.14, 0.12, 1.0))
    for i in range(5):
        make_box(f"Score_Line_{i}", (ROOM_W / 2.0 - 0.118, 1.30 - 0.12 + (i % 2) * 0.22, 1.88 - i * 0.07), (0.002, 0.10, 0.012), (0.88, 0.88, 0.84, 1.0))
    make_box("Specials_Board", (3.9, 5.885, 2.05), (0.60, 0.012, 0.80), (0.12, 0.14, 0.12, 1.0))
    make_box("Specials_Board_Frame", (3.9, 5.895, 2.05), (0.66, 0.008, 0.86), wood)
    for i in range(5):
        make_box(f"Specials_Line_{i}", (3.9 + (0.03 if i % 2 else -0.03), 5.878, 2.33 - i * 0.14), (0.38 - (i % 3) * 0.06, 0.002, 0.03), [(0.92, 0.88, 0.70, 1.0), (0.96, 0.60, 0.60, 1.0), (0.70, 0.90, 0.96, 1.0)][i % 3])
    # ── the gator on the wall over the bottle shelves' west end
    make_box("Gator_Head", (-3.75, 5.80, 2.65), (0.52, 0.20, 0.16), (0.30, 0.34, 0.22, 1.0))
    make_box("Gator_Snout", (-4.08, 5.80, 2.62), (0.20, 0.14, 0.10), (0.30, 0.34, 0.22, 1.0))
    make_box("Gator_Jaw", (-3.95, 5.80, 2.56), (0.36, 0.16, 0.04), (0.42, 0.40, 0.28, 1.0))
    for i in range(6):
        make_box(f"Gator_Tooth_{i}", (-4.12 + i * 0.07, 5.72 + (i % 2) * 0.16, 2.585), (0.015, 0.012, 0.025), (0.92, 0.90, 0.82, 1.0))
    for i, oy in enumerate((5.72, 5.88)):
        make_dome(f"Gator_Eye_{i}", (-3.62, oy, 2.73), 0.025, (0.86, 0.70, 0.20, 1.0), rings=3, segments=8)
    # ── the back door on the east wall's north end, the RESTROOM sign
    make_box("Back_Door", (ROOM_W / 2.0 - 0.125, 5.40, 1.05), (0.05, 0.90, 2.10), (0.30, 0.22, 0.14, 1.0))
    make_cyl("Back_Door_Knob", (ROOM_W / 2.0 - 0.17, 5.05, 1.02), 0.03, 0.04, brass, segments=8, axis='X')
    make_box("Back_Door_Sign", (ROOM_W / 2.0 - 0.112, 5.40, 2.35), (0.012, 0.44, 0.14), (0.92, 0.90, 0.84, 1.0))
    make_box("Back_Door_Sign_Text", (ROOM_W / 2.0 - 0.118, 5.40, 2.35), (0.002, 0.34, 0.05), (0.16, 0.16, 0.18, 1.0))
    # ── the street at night outside the south windows
    make_box("Ground_Sidewalk", (0.0, -2.0, -0.03), (24.0, 4.0, 0.06), (0.52, 0.50, 0.46, 1.0))
    make_box("Curb", (0.0, -4.05, -0.06), (24.0, 0.14, 0.14), (0.60, 0.58, 0.54, 1.0))
    make_box("Ground_Street", (0.0, -9.5, -0.14), (24.0, 11.0, 0.06), (0.24, 0.24, 0.26, 1.0))
    make_box("Out_Facade", (0.0, -15.5, 4.0), (26.0, 0.6, 8.0), (0.40, 0.32, 0.26, 1.0))
    for c in range(8):
        make_box(f"Out_Facade_Win_{c}", (-9.0 + c * 2.6, -15.19, 4.5), (1.0, 0.02, 1.4), [(0.92, 0.78, 0.40, 1.0), (0.16, 0.18, 0.22, 1.0), (0.80, 0.60, 0.44, 1.0)][c % 3])
    make_cyl("Street_Lamp_Pole", (-3.0, -3.7, 2.0), 0.05, 4.0, (0.20, 0.22, 0.24, 1.0), segments=8)
    make_box("Street_Lamp_Head", (-3.0, -4.1, 3.9), (0.28, 0.46, 0.14), (0.96, 0.88, 0.60, 1.0))
    from _props.vehicles import make_car
    make_car("Parked_Car", 2.8, -6.0, 4.4, (0.26, 0.26, 0.30, 1.0), along="X", z0=-0.11)


def main():
    clear_scene(); build_shell(); build_bar(); build_jukebox(); build_decor(); build_ceiling_fan(); build_ceiling_infra()
    build_hero_props()
    build_hero_props_2026_09()
    build_dive_2026_10()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/new_orleans_bar.glb"))
    print(f"\n[build_new_orleans_bar] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
