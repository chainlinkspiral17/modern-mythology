"""VOL 5 · New Orleans Bar — cameo. Long mahogany bar, brass rail,
bottle wall, pendant lamps, jukebox in corner.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose
from _props.decor import make_wall_clock
from _props.safety import make_fluorescent_tube_fixture, make_smoke_detector, make_ceiling_speaker

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
    make_wall("Wall_S_W", (-3.0, 0.0, 0), length=2.4, height=CEIL, axis='X', palette=PAL)
    make_wall("Wall_S_E", (+3.0, 0.0, 0), length=2.4, height=CEIL, axis='X', palette=PAL)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"tile": (0.30, 0.22, 0.14, 1.0), "grid": (0.18, 0.12, 0.10, 1.0)})
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10),("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_BRASS})
    make_window("Window_SW", (-3.0, 0.0, 1.60), width=1.00, height=1.20)
    make_window("Window_SE", (+3.0, 0.0, 1.60), width=1.00, height=1.20)

def build_bar():
    top_z = make_counter("Bar", (0.0, 4.5, 0.0), length=7.0, depth=1.20, height=1.10, palette={"formica": COL_BAR, "top": COL_TOP, "kick": (0.18, 0.10, 0.06, 1.0)})
    make_counter_bullnose("Bar", (-0.60, 4.5, top_z), length=7.0, palette={"top": COL_TOP})
    # Brass foot rail (cylinder along south face)
    make_cyl("Bar_FootRail", (-0.62, 4.5, 0.18), 0.025, 7.0, COL_BRASS, axis='Y', segments=8)
    # 5 bar stools (south side)
    for si, sx in enumerate([-2.4, -1.2, 0.0, +1.2, +2.4]):
        make_cyl(f"Stool_{si}_Seat", (sx, 3.20, 0.78), 0.18, 0.06, COL_BAR)
        make_cyl(f"Stool_{si}_Pillar", (sx, 3.20, 0.40), 0.04, 0.74, COL_BRASS)
        make_cyl(f"Stool_{si}_Foot", (sx, 3.20, 0.04), 0.16, 0.04, COL_BRASS)
    # Bottle wall north of bar (mounted shelves)
    for shf in range(3):
        sz = top_z + 0.30 + shf*0.40
        make_box(f"Bottle_Shelf_{shf}", (0.0, 5.40, sz), (6.4, 0.20, 0.02), COL_TOP)
        for bi in range(20):
            bx = -3.0 + bi*0.32
            tint = [COL_BOTTLE_AMBER, COL_BOTTLE_CLEAR, COL_BOTTLE_GREEN][(shf+bi)%3]
            make_cyl(f"Bottle_{shf}_{bi}", (bx, 5.40, sz+0.16), 0.05, 0.30, tint)
    # Back mirror (long horizontal — bartender's reflection canon)
    make_box("Bar_Mirror", (0.0, 5.87, top_z+0.85), (6.4, 0.02, 1.50), (0.78, 0.84, 0.86, 0.85))

def build_jukebox():
    # Wurlitzer-style jukebox SE corner
    jx, jy = +3.80, 1.20
    make_box("Jukebox_Body", (jx, jy, 0.75), (0.80, 0.60, 1.50), (0.78, 0.42, 0.16, 1.0))
    make_box("Jukebox_TopArch", (jx, jy, 1.70), (0.80, 0.60, 0.40), (0.62, 0.32, 0.14, 1.0))
    make_box("Jukebox_Glass", (jx, jy-0.31, 1.10), (0.70, 0.04, 0.50), (0.32, 0.22, 0.18, 0.55))
    make_box("Jukebox_LightBar", (jx, jy-0.32, 1.50), (0.70, 0.02, 0.10), (0.96, 0.78, 0.42, 1.0))

def build_decor():
    make_wall_clock("Clock", (0.0, ROOM_D-0.05, 2.60), frozen_hour=11, frozen_min=47)
    # Pendant lamps over bar
    for pi, px in enumerate([-2.0, 0.0, +2.0]):
        make_cyl(f"Pendant_{pi}_Cord", (px, 4.5, CEIL-0.30), 0.005, 0.40, P.METAL_BLACK)
        make_box(f"Pendant_{pi}_Shade", (px, 4.5, CEIL-0.70), (0.30, 0.30, 0.30), (0.92, 0.74, 0.32, 1.0))

def build_ceiling_fan():
    # Slow-turning ceiling fan with a warm light kit (jazz-club canon).
    fx, fy, fz = 0.0, 3.0, CEIL - 0.15
    make_cyl("Fan_Downrod", (fx, fy, fz - 0.02), 0.02, 0.30, P.METAL_BLACK)
    make_cyl("Fan_Motor", (fx, fy, fz - 0.24), 0.12, 0.14, COL_BRASS, segments=12)
    blades = [(0.46, fy, 0.66, 0.16), (-0.46, fy, 0.66, 0.16),
              (fx, fy+0.46, 0.16, 0.66), (fx, fy-0.46, 0.16, 0.66)]
    for bi, (bx, by, sw, sd) in enumerate(blades):
        make_box(f"Fan_Blade_{bi}", (bx, by, fz - 0.30), (sw, sd, 0.02), (0.36, 0.24, 0.14, 1.0))
    make_cyl("Fan_LightKit", (fx, fy, fz - 0.40), 0.09, 0.12, (0.96, 0.84, 0.62, 1.0), segments=12)

def build_ceiling_infra():
    # A grimy dive lights by neon, TV glow and low pendants — no
    # shop tubes
    for pi, (px, py) in enumerate(((-2.0, 2.2), (2.0, 2.2))):
        make_cyl(f"Pendant_{pi}_Cord", (px, py, CEIL-0.16), 0.008, 0.32, P.METAL_BLACK)
        make_cyl(f"Pendant_{pi}_Shade", (px, py, CEIL-0.42), 0.15, 0.14, (0.30, 0.24, 0.18, 1.0), segments=12)
        make_cyl(f"Pendant_{pi}_Bulb", (px, py, CEIL-0.50), 0.05, 0.06, (1.0, 0.80, 0.45, 1.0), segments=8)


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
    make_box("Bar_TV", (2.6, 5.80, 2.30), (1.10, 0.08, 0.62), (0.10, 0.10, 0.12, 1.0))
    make_box("Bar_TV_Screen", (2.6, 5.74, 2.30), (0.98, 0.02, 0.52), (0.32, 0.40, 0.36, 1.0))
    # Corner booth SW: L-benches + table + the props on it
    make_box("Booth_Bench_W", (-4.15, 1.6, 0.30), (0.55, 1.9, 0.46), vinyl)
    make_box("Booth_Back_W", (-4.38, 1.6, 0.80), (0.10, 1.9, 0.70), vinyl)
    make_box("Booth_Bench_S", (-3.1, 0.55, 0.30), (1.6, 0.55, 0.46), vinyl)
    make_box("Booth_Back_S", (-3.1, 0.32, 0.80), (1.6, 0.10, 0.70), vinyl)
    make_box("Booth_Table", (-3.4, 1.35, 0.74), (1.10, 0.75, 0.05), wood)
    make_box("Booth_Table_Leg", (-3.4, 1.35, 0.37), (0.10, 0.10, 0.72), (0.20, 0.19, 0.20, 1.0))
    make_cyl("Saltshaker", (-3.25, 1.30, 0.80), 0.022, 0.08, (0.88, 0.88, 0.84, 0.9), segments=8)
    make_box("Folded_Twenty", (-3.25, 1.30, 0.765), (0.05, 0.035, 0.006), (0.55, 0.62, 0.50, 1.0))
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
    make_cyl("Group_Table", (1.2, 2.0, 0.74), 0.65, 0.05, wood, segments=14)
    make_cyl("Group_Table_Post", (1.2, 2.0, 0.37), 0.07, 0.70, (0.20, 0.19, 0.20, 1.0), segments=8)
    import math as _m
    for ci in range(6):
        ang = ci * (2.0 * _m.pi / 6.0) + 0.3
        cx, cy = 1.2 + _m.cos(ang) * 1.0, 2.0 + _m.sin(ang) * 1.0
        make_box(f"Group_Chair_{ci}_Seat", (cx, cy, 0.44), (0.38, 0.38, 0.04), wood)
        make_box(f"Group_Chair_{ci}_Back", (1.2 + _m.cos(ang) * 1.17, 2.0 + _m.sin(ang) * 1.17, 0.70),
                 (0.38, 0.05, 0.48), wood)


def main():
    clear_scene(); build_shell(); build_bar(); build_jukebox(); build_decor(); build_ceiling_fan(); build_ceiling_infra()
    build_hero_props()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/new_orleans_bar.glb"))
    print(f"\n[build_new_orleans_bar] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
