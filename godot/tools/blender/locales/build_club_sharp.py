"""club_sharp — vol1 ch4's dream club (2026-10-10).

"They get in, tear around town, and wind up at a club in the heart of
nowhere, beating with life — people overflowing from its seams. Club
Sharp has a # for a logo. Dickens Dean seems to have the run of the
place. There is a gigantic arcade downstairs, several dance floors, and
a bowling alley. Music and movement seem to flow from one area to the
next." ... "you need a shot of absinthe to clear away cobwebs."

It played on the Foxhole (vol6's 12 x 16 m Texas punk black box). This
is the club the chapter describes, built big because it is a dream
that keeps opening: the main floor (24 x 18 m, 6 m to the deck above)
with two dance floors of lit tiles; the long bar on the E wall, its
back bar of green absinthe and its fountain; Dickens Dean's booth up
three steps on the N dais under the # in neon; on the W side the floor
opens over a railed atrium onto THE ARCADE DOWNSTAIRS — rows of
cabinets glowing four metres below, a stair down; on the S side,
behind a glass wall, THE BOWLING ALLEY — six lanes running away
under their pin-deck lights, the ball returns, the scoring screens.

Coordinates: Blender Z-up, the main floor at z 0, x -12..12, y 0..18
(the S glass at y 0). The arcade floor is z -4 under x -12..-4. glTF
export -> Godot (x, z, -y).

Draft 2 targets: the crowd "overflowing from its seams" as figures;
the arcade at insert scale; the car outside ("a beautiful car
waiting outside").
"""
import os, sys, math, random
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_chamfer_box, make_lathe, make_tube, make_rot_box, export_glb
from _props.objects import make_liquor_bottle

W, D, H = 24.0, 18.0, 6.0
XW, XE, YS, YN = -W / 2.0, W / 2.0, 0.0, D
ATRIUM_X1 = -4.0            # the floor opens W of this over the arcade
LOW_Z = -4.0
BLACK = (0.06, 0.06, 0.08, 1.0); WALL = (0.14, 0.12, 0.18, 1.0); STEEL = (0.62, 0.64, 0.68, 1.0)
CHROME = (0.80, 0.82, 0.86, 1.0); GLASS = (0.60, 0.70, 0.86, 0.18)
NEON_PINK = (0.98, 0.30, 0.66, 1.0); NEON_CYAN = (0.30, 0.90, 0.98, 1.0); NEON_GREEN = (0.50, 0.98, 0.40, 1.0)
ABSINTHE = (0.44, 0.82, 0.30, 0.8)
VELVET = (0.40, 0.08, 0.16, 1.0)


def build_shell():
    # the main floor (E of the atrium), the arcade floor below, the walls and the deck above
    make_box("Floor_Main", ((ATRIUM_X1 + XE) / 2.0, D / 2.0, -0.10), (XE - ATRIUM_X1, D, 0.20), (0.10, 0.10, 0.12, 1.0))
    make_box("Floor_Arcade", ((XW + ATRIUM_X1) / 2.0, D / 2.0, LOW_Z - 0.10), (ATRIUM_X1 - XW, D, 0.20), (0.12, 0.10, 0.16, 1.0))
    make_box("Atrium_Edge", (ATRIUM_X1 - 0.10, D / 2.0, (LOW_Z - 0.2) / 2.0), (0.20, D, -LOW_Z), (0.12, 0.12, 0.14, 1.0))
    for nm, c, s in (("Wall_W", (XW - 0.10, D / 2.0, (LOW_Z + H) / 2.0), (0.20, D + 0.4, H - LOW_Z)),
                     ("Wall_E", (XE + 0.10, D / 2.0, H / 2.0), (0.20, D + 0.4, H)),
                     ("Wall_N", (0.0, YN + 0.10, (LOW_Z + H) / 2.0), (W + 0.4, 0.20, H - LOW_Z))):
        make_box(nm, c, s, WALL)
    make_box("Deck_Ceiling", (0.0, D / 2.0, H + 0.10), (W + 0.4, D + 0.4, 0.20), (0.08, 0.08, 0.10, 1.0))
    # light trusses under the deck
    for i, y in enumerate((4.0, 9.0, 14.0)):
        make_box(f"Truss_{i}", (4.0, y, H - 0.15), (15.0, 0.30, 0.30), STEEL)
        for j in range(6):
            make_cyl(f"Truss_{i}_Can_{j}", (-2.5 + j * 2.6, y, H - 0.44), 0.10, 0.28, BLACK, segments=10)
    # the S wall is the bowling alley's glass, E of the atrium; the arcade's S wall below
    make_box("Wall_S_Arcade", ((XW + ATRIUM_X1) / 2.0, YS - 0.10, (LOW_Z + 0.0) / 2.0), (ATRIUM_X1 - XW, 0.20, -LOW_Z), WALL)
    make_box("Wall_S_Upper_W", ((XW + ATRIUM_X1) / 2.0, YS - 0.10, H / 2.0), (ATRIUM_X1 - XW, 0.20, H), WALL)
    make_box("Glass_Bowling", ((ATRIUM_X1 + XE) / 2.0, YS, 1.8), (XE - ATRIUM_X1, 0.03, 3.6), GLASS)
    make_box("Glass_Bowling_Head", ((ATRIUM_X1 + XE) / 2.0, YS, (3.6 + H) / 2.0), (XE - ATRIUM_X1, 0.20, H - 3.6), WALL)
    for i in range(6):
        make_box(f"Glass_Bowling_Mullion_{i}", (ATRIUM_X1 + 0.2 + i * 3.2, YS, 1.8), (0.08, 0.10, 3.6), BLACK)


def build_dance_floors():
    """Two dance floors of lit tiles; the # in neon over the dais."""
    cols = [NEON_PINK, NEON_CYAN, (0.86, 0.80, 0.30, 1.0), NEON_GREEN, (0.60, 0.40, 0.98, 1.0)]
    rnd = random.Random(3)
    for f, (cx, cy, n) in enumerate(((2.0, 8.5, 8), (8.5, 4.8, 5))):
        s = 0.9
        for i in range(n):
            for j in range(n):
                x = cx - (n - 1) * s / 2.0 + i * s
                y = cy - (n - 1) * s / 2.0 + j * s
                lit = rnd.random() < 0.45
                make_box(f"Dance_{f}_Tile_{i}_{j}", (x, y, 0.005), (s - 0.04, s - 0.04, 0.01), cols[rnd.randrange(len(cols))] if lit else (0.16, 0.14, 0.20, 1.0))
    # the dais at the N wall with Dickens Dean's booth, three steps up
    make_box("Dais", (2.0, YN - 2.2, 0.27), (9.0, 4.4, 0.54), (0.10, 0.08, 0.12, 1.0))
    for i in range(3):
        make_box(f"Dais_Step_{i}", (2.0, YN - 4.4 - 0.17 - i * 0.34, 0.09 * (3 - i)), (6.0, 0.34, 0.18 * (3 - i)), (0.12, 0.10, 0.14, 1.0))
    bx, by, bz = 2.0, YN - 1.6, 0.54
    make_chamfer_box("Booth_Seat_Back", (bx, YN - 0.55, bz + 0.65), (5.0, 0.30, 0.90), VELVET, chamfer=0.06)
    make_chamfer_box("Booth_Seat", (bx, YN - 0.95, bz + 0.22), (5.0, 0.60, 0.44), VELVET, chamfer=0.05)
    for i, x in enumerate((bx - 2.6, bx + 2.6)):
        make_chamfer_box(f"Booth_Arm_{i}", (x, YN - 1.40, bz + 0.40), (0.30, 1.50, 0.80), VELVET, chamfer=0.05)
    make_chamfer_box("Booth_Table", (bx, by - 0.30, bz + 0.72), (2.6, 0.90, 0.06), BLACK, chamfer=0.02)
    make_cyl("Booth_Table_Pedestal", (bx, by - 0.30, bz + 0.35), 0.10, 0.70, CHROME, segments=10)
    for i, dx in enumerate((-0.7, -0.2, 0.4)):
        make_lathe(f"Absinthe_Glass_{i}", (bx + dx, by - 0.30, bz + 0.75), [(0.0, 0.0), (0.03, 0.0), (0.008, 0.02), (0.008, 0.08), (0.04, 0.12), (0.045, 0.18), (0.0, 0.18)], (0.70, 0.90, 0.60, 0.6), segments=10)
    make_box("Absinthe_Spoon", (bx - 0.2, by - 0.30, bz + 0.94), (0.14, 0.03, 0.004), CHROME)
    # the # in neon over the booth: two verticals, two horizontals, slanted
    hx, hz, hy = 2.0, 4.0, YN - 0.055
    for i, dx in enumerate((-0.5, 0.5)):
        make_rot_box(f"Hash_Neon_V_{i}", (hx + dx, hy, hz), (0.12, 0.05, 2.4), NEON_PINK, pitch=0.18)
    for i, dz in enumerate((-0.45, 0.45)):
        make_box(f"Hash_Neon_H_{i}", (hx, hy, hz + dz), (2.0, 0.05, 0.12), NEON_PINK)
    make_box("Hash_Neon_Backing", (hx, YN - 0.015, hz), (2.8, 0.03, 3.0), BLACK)


def build_bar():
    """The long bar on the E wall, the back bar of absinthe and the
    fountain, the stools."""
    bx = XE - 3.2
    make_box("Bar_Body", (bx, 9.0, 0.55), (0.80, 10.0, 1.10), BLACK)
    make_box("Bar_Top", (bx - 0.05, 9.0, 1.13), (0.95, 10.1, 0.06), CHROME)
    make_box("Bar_LED_Strip", (bx - 0.41, 9.0, 0.95), (0.01, 10.0, 0.03), NEON_CYAN)
    for i in range(9):
        make_cyl(f"Bar_Stool_{i}_Seat", (bx - 0.85, 4.6 + i * 1.1, 0.78), 0.19, 0.06, (0.80, 0.10, 0.30, 1.0), segments=12)
        make_cyl(f"Bar_Stool_{i}_Post", (bx - 0.85, 4.6 + i * 1.1, 0.38), 0.03, 0.72, CHROME, segments=8)
        make_cyl(f"Bar_Stool_{i}_Foot", (bx - 0.85, 4.6 + i * 1.1, 0.015), 0.20, 0.03, CHROME, segments=12)
    make_box("BackBar_Counter", (XE - 0.40, 9.0, 0.50), (0.60, 10.0, 1.00), BLACK)
    for s, z in enumerate((1.50, 2.10, 2.70)):
        make_box(f"BackBar_Shelf_{s}", (XE - 0.15, 9.0, z), (0.30, 10.0, 0.03), (0.70, 0.86, 0.96, 0.5))
        for k in range(24):
            col = ABSINTHE if (k + s) % 3 == 0 else [(0.80, 0.84, 0.86, 0.5), (0.72, 0.42, 0.16, 0.9)][(k + s) % 2]
            make_liquor_bottle(f"BackBar_Bottle_{s}_{k}", XE - 0.20, 4.4 + k * 0.40, z + 0.015, col, h=0.30, r=0.035)
    make_box("BackBar_Glow", (XE - 0.04, 9.0, 2.10), (0.02, 10.0, 1.60), (0.20, 0.50, 0.30, 1.0))
    # the absinthe fountain on the bar
    fx, fy = bx - 0.05, 8.2
    make_lathe("Absinthe_Fountain", (fx, fy, 1.16), [(0.0, 0.0), (0.12, 0.0), (0.05, 0.05), (0.04, 0.28), (0.14, 0.32), (0.14, 0.56), (0.0, 0.60)], (0.80, 0.86, 0.90, 0.6), segments=14)
    for i in range(4):
        a = i * math.pi / 2.0
        make_cyl(f"Absinthe_Fountain_Tap_{i}", (fx + 0.16 * math.cos(a), fy + 0.16 * math.sin(a), 1.46), 0.01, 0.06, CHROME, segments=6)


def build_atrium_and_arcade():
    """The railed opening over the arcade downstairs: the rail, the stair
    down, the cabinets glowing four metres below."""
    rx = ATRIUM_X1 + 0.15
    make_box("Atrium_Rail", (rx, D / 2.0 + 1.0, 1.05), (0.06, D - 3.0, 0.06), CHROME)
    make_box("Atrium_Rail_Glass", (rx, D / 2.0 + 1.0, 0.55), (0.02, D - 3.0, 0.90), GLASS)
    for i in range(9):
        make_box(f"Atrium_Rail_Post_{i}", (rx, 2.5 + i * 1.9, 0.52), (0.05, 0.05, 1.04), CHROME)
    # the stair down at the S end of the opening
    steps = 20
    for k in range(steps):
        z = -0.20 * (k + 1)
        x = ATRIUM_X1 - 0.30 - k * 0.28
        make_box(f"Arcade_Stair_{k}", (x, 1.10, z), (0.28, 1.40, 0.04), BLACK)
    make_box("Arcade_Stair_Stringer", (ATRIUM_X1 - 0.30 - (steps - 1) * 0.14, 0.38, -2.0), ((steps) * 0.28, 0.06, 0.20), CHROME)
    # the cabinets in rows, their screens lit, marquees glowing
    rnd = random.Random(7)
    scr = [(0.30, 0.86, 0.96, 1.0), (0.96, 0.40, 0.70, 1.0), (0.60, 0.96, 0.40, 1.0), (0.96, 0.86, 0.30, 1.0)]
    k = 0
    for row in range(3):
        y = 4.5 + row * 4.2
        for c in range(4):
            x = XW + 1.4 + c * 1.6
            for side, sgn in ((0, -1), (1, 1)):
                cy = y + sgn * 0.55
                make_box(f"Cabinet_{k}", (x, cy, LOW_Z + 0.88), (0.70, 0.80, 1.76), (0.12, 0.10, 0.16, 1.0))
                make_box(f"Cabinet_{k}_Screen", (x, cy + sgn * 0.402, LOW_Z + 1.24), (0.54, 0.004, 0.44), scr[rnd.randrange(4)])
                make_box(f"Cabinet_{k}_Marquee", (x, cy + sgn * 0.402, LOW_Z + 1.64), (0.60, 0.004, 0.16), scr[rnd.randrange(4)])
                make_box(f"Cabinet_{k}_Panel", (x, cy + sgn * 0.47, LOW_Z + 0.96), (0.60, 0.14, 0.06), (0.20, 0.20, 0.24, 1.0))
                k += 1
    make_box("Arcade_Carpet", ((XW + ATRIUM_X1) / 2.0 - 0.3, D / 2.0, LOW_Z + 0.004), (ATRIUM_X1 - XW - 1.2, D - 1.0, 0.008), (0.16, 0.10, 0.30, 1.0))
    for i in range(40):
        make_box(f"Arcade_Carpet_Star_{i}", (rnd.uniform(XW + 0.8, ATRIUM_X1 - 1.0), rnd.uniform(1.0, D - 1.0), LOW_Z + 0.0095), (0.10, 0.10, 0.002), scr[i % 4])


def build_bowling():
    """Behind the S glass: six lanes running away south under their
    pin-deck lights, the ball returns, the scoring screens."""
    lx0, lx1 = ATRIUM_X1 + 0.8, XE - 0.8
    make_box("Bowling_Floor", ((lx0 + lx1) / 2.0 - 0.0, -14.0, -0.10), (lx1 - lx0 + 1.6, 28.0, 0.20), (0.10, 0.10, 0.12, 1.0))
    make_box("Bowling_Ceiling", ((lx0 + lx1) / 2.0, -14.0, 3.9), (lx1 - lx0 + 1.6, 28.0, 0.20), (0.06, 0.06, 0.08, 1.0))
    make_box("Bowling_Wall_W", (lx0 - 0.9, -14.0, 1.9), (0.20, 28.0, 3.8), WALL)
    make_box("Bowling_Wall_E", (lx1 + 0.9, -14.0, 1.9), (0.20, 28.0, 3.8), WALL)
    make_box("Bowling_Wall_S", ((lx0 + lx1) / 2.0, -28.0, 1.9), (lx1 - lx0 + 1.8, 0.20, 3.8), (0.10, 0.10, 0.14, 1.0))
    n = 6
    lw = (lx1 - lx0) / n
    for i in range(n):
        x = lx0 + lw * (i + 0.5)
        make_box(f"Lane_{i}", (x, -15.0, 0.012), (lw * 0.62, 24.0, 0.024), (0.80, 0.62, 0.40, 1.0))
        for s in (-1, 1):
            make_box(f"Lane_{i}_Gutter_{s:+d}", (x + s * lw * 0.38, -15.0, 0.004), (lw * 0.12, 24.0, 0.008), (0.30, 0.30, 0.34, 1.0))
        make_box(f"Lane_{i}_Foul_Line", (x, -3.0, 0.025), (lw * 0.62, 0.04, 0.002), BLACK)
        for r, row in enumerate(((0,), (-1, 1), (-2, 0, 2), (-3, -1, 1, 3))):
            for pc in row:
                make_lathe(f"Lane_{i}_Pin_{r}_{pc}", (x + pc * 0.08, -26.4 - r * 0.20, 0.024), [(0.0, 0.0), (0.03, 0.0), (0.045, 0.10), (0.02, 0.24), (0.03, 0.32), (0.0, 0.38)], (0.96, 0.96, 0.94, 1.0), segments=8)
        make_box(f"Lane_{i}_Pin_Light", (x, -26.0, 3.70), (lw * 0.70, 0.30, 0.20), NEON_CYAN if i % 2 else NEON_PINK)
        make_box(f"Lane_{i}_Score_Screen", (x, -2.0, 2.6), (lw * 0.70, 0.06, 0.50), (0.14, 0.20, 0.34, 1.0))
        make_box(f"Lane_{i}_Score_Screen_Face", (x, -1.965, 2.6), (lw * 0.62, 0.004, 0.40), (0.30, 0.70, 0.96, 1.0))
        make_cyl(f"Lane_{i}_Score_Screen_Hanger", (x, -2.0, 3.35), 0.02, 1.0, STEEL, segments=5)
    for i in range(n // 2):
        x = lx0 + lw * (2 * i + 1)
        make_box(f"Ball_Return_{i}", (x, -1.6, 0.35), (0.50, 1.20, 0.70), (0.20, 0.20, 0.26, 1.0))
        for b in range(3):
            make_lathe(f"Ball_Return_{i}_Ball_{b}", (x, -1.95 + b * 0.24, 0.70), [(0.0, 0.0), (0.10, 0.03), (0.11, 0.11), (0.08, 0.19), (0.0, 0.22)], [NEON_PINK, NEON_CYAN, NEON_GREEN][b], segments=10)


def build_outside():
    make_box("Ground_Far", (0.0, 0.0, LOW_Z - 0.4), (300.0, 300.0, 0.2), (0.04, 0.04, 0.06, 1.0))


def main():
    clear_scene()
    build_shell(); build_dance_floors(); build_bar(); build_atrium_and_arcade(); build_bowling(); build_outside()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/club_sharp.glb"))
    print(f"\n[build_club_sharp] exporting to {out}")
    export_glb(out)


if __name__ == "__main__": main()
