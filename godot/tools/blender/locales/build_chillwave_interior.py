"""chillwave_interior — vol5-7 locale. A small second-floor
chillwave / synthwave cocktail lounge: a copper-topped bar with a
neon-underlit back-bar bottle wall, chrome stools, a low leather
lounge banquette with round cocktail tables, a DJ console with twin
turntables, a magenta "sunset grid" neon mural on the E wall, potted
palms, and warm pendant + cool cove accent lighting. Moody purple
palette — light to READ without flattening the neon contrast.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_floor_plant
from _props.safety import make_smoke_detector, make_hvac_vent

ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 2.8
PAL_WALL = {"wall": (0.42, 0.32, 0.46, 1.0), "baseboard": (0.18, 0.12, 0.20, 1.0)}
COL_FLOOR = (0.20, 0.16, 0.24, 1.0); COL_SEAM = (0.30, 0.20, 0.38, 1.0)
COL_WOOD = (0.30, 0.20, 0.34, 1.0)
COL_COPPER = (0.86, 0.52, 0.42, 1.0); COL_COPPER_DK = (0.52, 0.30, 0.28, 1.0)
COL_LEATHER = (0.34, 0.16, 0.32, 1.0); COL_CHROME = (0.72, 0.72, 0.78, 1.0)
COL_MAGENTA = (0.92, 0.28, 0.72, 1.0); COL_CYAN = (0.36, 0.86, 0.94, 1.0)
COL_HOTPINK = (0.96, 0.40, 0.62, 1.0); COL_ORANGE = (0.98, 0.56, 0.34, 1.0)
COL_PURPLE = (0.58, 0.34, 0.86, 1.0)
COL_BOTTLE_A = (0.86, 0.42, 0.66, 1.0); COL_BOTTLE_B = (0.42, 0.74, 0.86, 0.6)
COL_BOTTLE_C = (0.56, 0.42, 0.86, 1.0)
COL_LAMP = (0.98, 0.78, 0.52, 1.0); COL_BLACK = (0.10, 0.08, 0.12, 1.0)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL,
              axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL,
              axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
                                    ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_PURPLE})


def build_bar():
    # Copper-topped bar running E-W along the N wall, patrons to the S.
    by = ROOM_D - 0.60
    make_box("Bar_Body", (0.0, by, 0.53), (4.60, 0.72, 1.02), COL_WOOD)
    make_box("Bar_Front_Panel", (0.0, by - 0.37, 0.53), (4.60, 0.02, 1.00), COL_PURPLE)
    make_box("Bar_Top", (0.0, by, 1.08), (4.80, 0.84, 0.06), COL_COPPER)
    make_box("Bar_Kick", (0.0, by - 0.38, 0.10), (4.60, 0.04, 0.18), COL_BLACK)
    # Brass foot rail along the front
    make_cyl("Bar_FootRail", (0.0, by - 0.44, 0.18), 0.03, 4.40, COL_COPPER, axis='X', segments=8)
    for rp in (-2.0, 0.0, +2.0):
        make_cyl(f"Bar_RailPost_{rp:+.0f}", (rp, by - 0.44, 0.10), 0.02, 0.16, COL_COPPER)
    # A neon under-glow strip along the bar's front kick (cyan)
    make_box("Bar_UnderNeon", (0.0, by - 0.39, 0.24), (4.20, 0.01, 0.03), COL_CYAN)
    # Four chrome stools facing N
    for si, sx in enumerate([-1.8, -0.6, +0.6, +1.8]):
        sy = by - 0.95
        make_cyl(f"Stool_{si}_Base", (sx, sy, 0.04), 0.20, 0.04, COL_CHROME, segments=12)
        make_cyl(f"Stool_{si}_Post", (sx, sy, 0.40), 0.035, 0.72, COL_CHROME)
        make_cyl(f"Stool_{si}_FootRing", (sx, sy, 0.22), 0.14, 0.02, COL_CHROME, segments=12)
        make_cyl(f"Stool_{si}_Seat", (sx, sy, 0.80), 0.19, 0.06, COL_LEATHER, segments=12)


def build_backbar():
    # Mirrored back-bar with three neon-lit shelves of bottles on N wall.
    by = ROOM_D - 0.14
    make_box("Backbar_Mirror", (0.0, by, 1.80), (4.20, 0.03, 1.60), (0.30, 0.34, 0.42, 0.55))
    make_box("Backbar_Cabinet", (0.0, by - 0.10, 0.60), (4.40, 0.24, 1.10), COL_WOOD)
    for si in range(3):
        sz = 1.30 + si * 0.42
        make_box(f"Backbar_Shelf_{si}", (0.0, by - 0.14, sz), (4.00, 0.24, 0.03), COL_BLACK)
        # Neon light-line under each shelf
        make_box(f"Backbar_ShelfNeon_{si}", (0.0, by - 0.12, sz - 0.03),
                 (3.90, 0.01, 0.02), [COL_MAGENTA, COL_CYAN, COL_HOTPINK][si])
        for bi in range(17):
            bx = -1.90 + bi * 0.24
            bc = [COL_BOTTLE_A, COL_BOTTLE_B, COL_BOTTLE_C][bi % 3]
            make_cyl(f"Bottle_{si}_{bi}", (bx, by - 0.14, sz + 0.17), 0.035, 0.30, bc, segments=6)
    # A row of hanging stemware under the lowest shelf
    for gi in range(8):
        gx = -1.6 + gi * 0.46
        make_cyl(f"Stem_Bowl_{gi}", (gx, by - 0.30, 1.14), 0.05, 0.08, COL_BOTTLE_B, segments=8)
        make_cyl(f"Stem_Stem_{gi}", (gx, by - 0.30, 1.02), 0.008, 0.16, COL_CHROME)


def build_sunset_mural():
    # Magenta→orange "chillwave sunset" neon mural on the E wall
    # (thin panels on the wall face; sun of stacked slats + palms).
    wx = ROOM_W/2.0 - 0.06
    cy = 2.6; cz = 1.70
    # Sun disc built from horizontal slats, widening then a gap grid
    grad = [COL_ORANGE, COL_ORANGE, COL_HOTPINK, COL_HOTPINK, COL_MAGENTA, COL_MAGENTA]
    widths = [0.30, 0.70, 0.98, 1.10, 1.14, 1.10]
    for i, (w, col) in enumerate(zip(widths, grad)):
        make_box(f"Sunset_Slat_{i}", (wx, cy, cz + 0.62 - i * 0.16),
                 (0.03, w, 0.09), col)
    # Perspective grid floor below the sun (converging lines)
    for gi in range(5):
        make_box(f"Sunset_GridH_{gi}", (wx, cy, cz - 0.30 - gi * 0.12),
                 (0.02, 1.20 - gi * 0.12, 0.02), COL_CYAN)
    for gv in range(5):
        gvy = cy - 0.5 + gv * 0.25
        make_box(f"Sunset_GridV_{gv}", (wx, gvy, cz - 0.55),
                 (0.02, 0.02, 0.52), COL_CYAN)
    # Two palm silhouettes flanking the sun
    for sgn, tag in [(-1, "L"), (+1, "R")]:
        py = cy + sgn * 1.05
        make_box(f"Palm_{tag}_Trunk", (wx, py, cz), (0.02, 0.05, 0.90), COL_BLACK)
        for fr in range(5):
            ang = (fr - 2) * 0.5
            make_box(f"Palm_{tag}_Frond_{fr}", (wx, py + ang * 0.12, cz + 0.48 + abs(ang) * 0.02),
                     (0.02, 0.34, 0.03), COL_BLACK)


def build_lounge():
    # Low leather banquette along the W wall + two round cocktail tables.
    wx = -ROOM_W/2.0 + 0.45
    make_box("Banquette_Base", (wx, 3.0, 0.24), (0.70, 3.60, 0.44), COL_LEATHER)
    make_box("Banquette_Back", (wx - 0.28, 3.0, 0.78), (0.14, 3.60, 0.62), COL_LEATHER)
    for ci in range(3):
        make_box(f"Banquette_Tuft_{ci}", (wx - 0.20, 1.6 + ci * 1.4, 0.78),
                 (0.02, 0.04, 0.56), COL_PURPLE)
    for ti, ty in enumerate([2.0, 4.0]):
        tx = wx + 0.95
        make_cyl(f"Cocktail_{ti}_Base", (tx, ty, 0.03), 0.22, 0.06, COL_BLACK, segments=12)
        make_cyl(f"Cocktail_{ti}_Post", (tx, ty, 0.34), 0.03, 0.62, COL_CHROME)
        make_cyl(f"Cocktail_{ti}_Top", (tx, ty, 0.66), 0.30, 0.04, COL_COPPER, segments=16)
        # a cocktail glass + a small candle on each
        make_cyl(f"Cocktail_{ti}_Glass_Bowl", (tx - 0.08, ty, 0.76), 0.05, 0.08,
                 COL_BOTTLE_B, segments=8)
        make_cyl(f"Cocktail_{ti}_Glass_Stem", (tx - 0.08, ty, 0.69), 0.006, 0.10, COL_CHROME)
        make_cyl(f"Cocktail_{ti}_Candle", (tx + 0.10, ty, 0.72), 0.03, 0.06, COL_LAMP, segments=8)


def build_dj_console():
    # Twin-turntable DJ console in the SE corner facing the room.
    cx, cy = ROOM_W/2.0 - 0.85, 1.15
    make_box("DJ_Cabinet", (cx, cy, 0.50), (1.50, 0.60, 1.00), COL_BLACK)
    make_box("DJ_Top", (cx, cy, 1.02), (1.56, 0.66, 0.05), COL_WOOD)
    make_box("DJ_FrontNeon", (cx, cy - 0.31, 0.50), (1.30, 0.01, 0.04), COL_MAGENTA)
    for di, dx in enumerate([-0.42, +0.42]):
        make_box(f"DJ_Deck_{di}", (cx + dx, cy, 1.07), (0.44, 0.52, 0.05), (0.16, 0.14, 0.18, 1.0))
        make_cyl(f"DJ_Platter_{di}", (cx + dx, cy, 1.11), 0.18, 0.03, COL_CHROME, segments=16)
        make_cyl(f"DJ_Label_{di}", (cx + dx, cy, 1.13), 0.06, 0.005, COL_HOTPINK, segments=12)
        make_box(f"DJ_Tonearm_{di}", (cx + dx + 0.15, cy + 0.14, 1.12), (0.03, 0.20, 0.02), COL_CHROME)
    # Center mixer with knobs + faders + green level LEDs
    make_box("DJ_Mixer", (cx, cy, 1.08), (0.26, 0.50, 0.06), (0.20, 0.18, 0.22, 1.0))
    for ki in range(6):
        make_cyl(f"DJ_Knob_{ki}", (cx - 0.08 + (ki % 3) * 0.08, cy - 0.14 + (ki // 3) * 0.10, 1.13),
                 0.018, 0.03, COL_CYAN, segments=6)
    for li in range(5):
        make_box(f"DJ_LED_{li}", (cx, cy + 0.10 - li * 0.02, 1.12),
                 (0.10, 0.008, 0.008), (0.42, 0.94, 0.56, 1.0))
    # A laptop propped at the back of the console
    make_box("DJ_Laptop_Base", (cx, cy + 0.18, 1.06), (0.32, 0.22, 0.02), COL_CHROME)
    make_box("DJ_Laptop_Screen", (cx, cy + 0.29, 1.16), (0.32, 0.02, 0.20), COL_BLACK)
    make_box("DJ_Laptop_Glow", (cx, cy + 0.278, 1.16), (0.28, 0.005, 0.16), COL_CYAN)


def build_ceiling_infra():
    # Neon cove strips (magenta N/S, cyan E/W) + two warm pendants over the bar.
    make_box("Cove_N", (0.0, ROOM_D - 0.30, CEIL - 0.12), (5.6, 0.04, 0.04), COL_MAGENTA)
    make_box("Cove_S", (0.0, 0.40, CEIL - 0.12), (5.6, 0.04, 0.04), COL_MAGENTA)
    make_box("Cove_W", (-ROOM_W/2.0 + 0.30, ROOM_D/2.0, CEIL - 0.12), (0.04, 5.0, 0.04), COL_CYAN)
    make_box("Cove_E", (+ROOM_W/2.0 - 0.30, ROOM_D/2.0, CEIL - 0.12), (0.04, 5.0, 0.04), COL_CYAN)
    for pi, px in enumerate([-1.2, +1.2]):
        make_cyl(f"Pendant_Cord_{pi}", (px, ROOM_D - 0.90, CEIL - 0.25), 0.01, 0.50, COL_BLACK)
        make_cyl(f"Pendant_Shade_{pi}", (px, ROOM_D - 0.90, CEIL - 0.56), 0.12, 0.14, COL_COPPER, segments=10)
        make_cyl(f"Pendant_Bulb_{pi}", (px, ROOM_D - 0.90, CEIL - 0.66), 0.05, 0.06, COL_LAMP, segments=8)
    make_hvac_vent("Vent", (-1.5, 1.6, CEIL), width=1.00, depth=0.50, slats=5)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))


def build_decor():
    make_wall_clock("Clock", (-ROOM_W/2.0 + 0.05, 4.6, 2.30), frozen_hour=1, frozen_min=20,
                    palette={"face": (0.30, 0.24, 0.36, 1.0), "rim": COL_MAGENTA})
    make_floor_plant("Palm_SE", (ROOM_W/2.0 - 0.40, 2.4, 0.0),
                     palette={"leaf": (0.34, 0.52, 0.40, 1.0), "pot": COL_BLACK})
    make_floor_plant("Palm_SW", (-ROOM_W/2.0 + 0.45, 0.60, 0.0),
                     palette={"leaf": (0.34, 0.52, 0.40, 1.0), "pot": COL_BLACK})


def main():
    clear_scene()
    build_shell()
    build_bar()
    build_backbar()
    build_sunset_mural()
    build_lounge()
    build_dj_console()
    build_ceiling_infra()
    build_decor()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/chillwave_interior.glb"))
    print(f"\n[build_chillwave_interior] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
