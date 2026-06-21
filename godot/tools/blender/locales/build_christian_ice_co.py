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
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/christian_ice_co.glb"))
    print(f"\n[build_christian_ice_co] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
