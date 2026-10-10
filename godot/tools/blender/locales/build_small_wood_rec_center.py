"""small_wood_rec_center — vol2's second interlude, Small Wood, Oregon
(2026-10-10).

"My parents wanted a night together so they dropped my sister and I off
at Small Wood Rec Center — a small, deteriorating one-room building on
the main drag of town. Unfortunately, that night was a dance instead of
the usual casual come-as-you-are games of foosball, pool, and scattered
cartridges popped into an old Nintendo system. A portly kid was the
deejay and there were eight kids making an effort to shuffle in place
uncomfortably ... We were standing at the entrance horrified ... Janess
and I made for the back, where we arranged fold-up chairs in sitting
positions and looked around for out-dated but readily available reading
material." (vol2_ch2_interlude_two)

It played on Harmony Creek High's weight room (a Texas school basement).
This is the rec hall: one worn room on the main drag, 12 x 9 m under a
water-stained drop ceiling with two tubes dead; the glass entry doors
to the street at night; the dance pushed into the middle — the
deejay's folding table at the far wall with the decks, the mixer, the
speakers on their stands, a coloured party light, streamers taped up;
the everyday room shoved to its edges — the pool table and the foosball
against the W wall, the TV on its cart with the Nintendo and the
cartridges scattered; at the back the stack of fold-up chairs and the
two pulled out by the magazine rack; the bulletin board, the drinking
fountain, the restroom doors, the snack window with its shutter down.

Coordinates: Blender Z-up, the entrance on the S wall at y 0, x -6..6,
y 0..9. glTF export -> Godot (x, z, -y).

Draft 2 targets: the eight kids and the two shuffling as figures; the
main drag through the doors at insert scale; the middle school gym (the
pick-up game) as its own preset.
"""
import os, sys, math, random
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_chamfer_box, make_lathe, make_tube, make_rot_box, export_glb
from _props.structure import make_floor, make_wall, make_wall_with_openings, make_ceiling
from _props.safety import make_fluorescent_tube_fixture
from _props.detail import make_traffic_wear, make_floor_stain, make_wall_outlet

ROOM_W = 12.0; ROOM_D = 9.0; CEIL = 3.0
XW, XE, YS, YN = -ROOM_W / 2.0, ROOM_W / 2.0, 0.0, ROOM_D
FW, FE, FS, FN = XW + 0.10, XE - 0.10, YS + 0.10, YN - 0.10
DOOR_X, DOOR_W, DOOR_H = -2.0, 1.8, 2.2
WIN_XS = (-4.6, 2.6, 4.6)
PAL = {"wall": (0.72, 0.68, 0.56, 1.0), "baseboard": (0.30, 0.26, 0.22, 1.0)}
PANEL = (0.46, 0.34, 0.24, 1.0)
WOOD = (0.42, 0.30, 0.20, 1.0); STEEL = (0.64, 0.66, 0.68, 1.0); BLACK = (0.10, 0.10, 0.11, 1.0)
FELT = (0.20, 0.42, 0.28, 1.0)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": (0.62, 0.58, 0.50, 1.0), "seam": (0.48, 0.44, 0.38, 1.0)})
    make_wall("Wall_W", (XW, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_E", (XE, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_N", (0.0, YN, 0), length=ROOM_W + 0.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_S", (0.0, YS, 0), length=ROOM_W + 0.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=+1,
                            openings=[(DOOR_X, DOOR_H / 2.0, DOOR_W, DOOR_H)] + [(x, 1.55, 1.40, 1.10) for x in WIN_XS])
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
                 palette={"tile": (0.82, 0.80, 0.74, 1.0), "grid": (0.62, 0.60, 0.56, 1.0), "stain": (0.66, 0.58, 0.44, 1.0)})
    # wood paneling to 1.2 m round the room, worn
    for tag, ax, line, a0, a1, sign in (("W", 'Y', FW, 0.1, ROOM_D - 0.1, 1), ("E", 'Y', FE, 0.1, ROOM_D - 0.1, -1), ("N", 'X', FN, XW + 0.1, XE - 0.1, -1)):
        mid, ln = (a0 + a1) / 2.0, a1 - a0
        c = (line + sign * 0.01, mid, 0.68) if ax == 'Y' else (mid, line + sign * 0.01, 0.68)
        s = (0.02, ln, 1.04) if ax == 'Y' else (ln, 0.02, 1.04)
        make_box(f"Paneling_{tag}", c, s, PANEL)
    # the glass entry doors (a pair), the windows to the main drag
    for i, s in enumerate((-1, 1)):
        make_box(f"Entry_Door_{i}", (DOOR_X + s * DOOR_W / 4.0, YS, 1.10), (DOOR_W / 2.0 - 0.04, 0.04, 2.18), (0.40, 0.42, 0.44, 1.0))
        make_box(f"Entry_Door_{i}_Glass", (DOOR_X + s * DOOR_W / 4.0, YS + 0.025, 1.25), (DOOR_W / 2.0 - 0.20, 0.01, 1.60), (0.66, 0.74, 0.80, 0.35))
        make_box(f"Entry_Door_{i}_Bar", (DOOR_X + s * DOOR_W / 4.0, YS + 0.035, 1.05), (DOOR_W / 2.0 - 0.20, 0.03, 0.04), STEEL)
    for i, x in enumerate(WIN_XS):
        make_box(f"Window_{i}_Glass", (x, YS, 1.55), (1.40, 0.01, 1.10), (0.62, 0.70, 0.76, 0.30))
        make_box(f"Window_{i}_Sill", (x, FS + 0.05, 0.98), (1.50, 0.12, 0.04), (0.80, 0.78, 0.72, 1.0))
    # the ceiling: six troffers, two of them dead
    for i, (x, y) in enumerate(((-3.6, 2.4), (0.0, 2.4), (3.6, 2.4), (-3.6, 6.4), (0.0, 6.4), (3.6, 6.4))):
        make_fluorescent_tube_fixture(f"Troffer_{i}", (x, y, CEIL), length=1.20, width=0.60)


def build_dance():
    """The deejay's table at the far wall, the speakers, the party light,
    streamers; the dead zone of the floor in the middle."""
    tx, ty = 0.6, FN - 0.55
    make_box("DJ_Table_Top", (tx, ty, 0.74), (1.80, 0.76, 0.04), (0.86, 0.84, 0.80, 1.0))
    for i, (lx, ly) in enumerate(((-0.84, -0.32), (0.84, -0.32), (-0.84, 0.32), (0.84, 0.32))):
        make_box(f"DJ_Table_Leg_{i}", (tx + lx, ty + ly, 0.36), (0.03, 0.03, 0.72), STEEL)
    make_box("DJ_Table_Skirt", (tx, ty - 0.39, 0.55), (1.80, 0.01, 0.38), BLACK)
    for i, dx in enumerate((-0.48, 0.48)):
        make_box(f"DJ_Deck_{i}", (tx + dx, ty, 0.79), (0.40, 0.34, 0.06), (0.20, 0.20, 0.22, 1.0))
        make_cyl(f"DJ_Deck_{i}_Platter", (tx + dx, ty + 0.02, 0.825), 0.13, 0.01, (0.36, 0.36, 0.38, 1.0), segments=14)
    make_box("DJ_Mixer", (tx, ty, 0.80), (0.30, 0.34, 0.08), BLACK)
    for i in range(4):
        make_box(f"DJ_Mixer_Fader_{i}", (tx - 0.09 + i * 0.06, ty - 0.06, 0.845), (0.012, 0.06, 0.01), (0.86, 0.86, 0.84, 1.0))
    make_box("DJ_CD_Case_Stack", (tx + 0.80, ty + 0.20, 0.80), (0.14, 0.13, 0.08), (0.30, 0.40, 0.60, 1.0))
    make_tube("DJ_Cable", [(tx + 0.10, ty + 0.18, 0.76), (tx + 0.20, ty + 0.40, 0.40), (tx + 0.10, ty + 0.38, 0.02)], 0.006, BLACK, segments=4)
    for i, x in enumerate((tx - 1.6, tx + 1.6)):
        make_box(f"Speaker_Stand_Base_{i}", (x, ty, 0.02), (0.60, 0.60, 0.04), BLACK)
        make_cyl(f"Speaker_Stand_Pole_{i}", (x, ty, 0.74), 0.025, 1.40, BLACK, segments=6)
        make_chamfer_box(f"Speaker_{i}", (x, ty, 1.72), (0.42, 0.36, 0.62), BLACK, chamfer=0.03)
        make_cyl(f"Speaker_{i}_Cone", (x, ty - 0.185, 1.64), 0.14, 0.01, (0.24, 0.24, 0.26, 1.0), axis='Y', segments=14)
    # the party light on its tripod, its coloured heads
    lx, ly = tx + 2.6, ty - 0.2
    for i in range(3):
        a = i * 2.0 * math.pi / 3.0
        make_rot_box(f"Party_Light_Leg_{i}", (lx + 0.18 * math.cos(a), ly + 0.18 * math.sin(a), 0.70), (0.025, 0.025, 1.42), BLACK,
                     yaw=a, roll=0.0, pitch=0.0)
    make_box("Party_Light_Bar", (lx, ly, 1.42), (0.80, 0.06, 0.06), BLACK)
    for i, (dx, col) in enumerate(((-0.30, (0.96, 0.30, 0.40, 1.0)), (0.0, (0.40, 0.60, 0.98, 1.0)), (0.30, (0.40, 0.96, 0.50, 1.0)))):
        make_cyl(f"Party_Light_Head_{i}", (lx + dx, ly - 0.06, 1.50), 0.07, 0.12, col, axis='Y', segments=10)
    # streamers taped across the ceiling from the N wall, a few balloons
    cols = [(0.86, 0.30, 0.36, 1.0), (0.30, 0.50, 0.86, 1.0), (0.92, 0.82, 0.30, 1.0)]
    for i in range(5):
        x0 = -4.0 + i * 2.0
        make_tube(f"Streamer_{i}", [(x0, FN, 2.80), (x0 + 0.5, 6.0, 2.60), (x0 + 0.8, 4.0, 2.85)], 0.012, cols[i % 3], segments=4)
    for i, (x, y) in enumerate(((-1.2, FN - 0.15), (-0.9, FN - 0.12), (2.2, FN - 0.15))):
        make_lathe(f"Balloon_{i}", (x, y, 1.80), [(0.0, 0.0), (0.10, 0.06), (0.14, 0.18), (0.12, 0.28), (0.0, 0.32)], cols[i % 3], segments=10)
        make_tube(f"Balloon_{i}_String", [(x, y, 1.80), (x, y + 0.03, 1.20)], 0.002, (0.86, 0.86, 0.84, 1.0), segments=3)
    make_traffic_wear("Dance_Floor_Scuff", [(-1.0, 3.6), (1.5, 4.4)], width=2.4, tint=(0.50, 0.47, 0.42, 1.0))


def build_edges():
    """The everyday room shoved to the walls."""
    # the pool table against the W wall
    px, py = FW + 1.35, 5.4
    make_box("Pool_Table_Body", (px, py, 0.62), (1.24, 2.24, 0.36), WOOD)
    make_box("Pool_Table_Felt", (px, py, 0.805), (1.02, 2.02, 0.02), FELT)
    for i, (lx, ly) in enumerate(((-0.52, -1.02), (0.52, -1.02), (-0.52, 1.02), (0.52, 1.02))):
        make_box(f"Pool_Table_Leg_{i}", (px + lx, py + ly, 0.22), (0.14, 0.14, 0.44), WOOD)
    make_rot_box("Pool_Cue_Leaned", (FW + 0.08, py + 1.3, 0.72), (0.02, 0.02, 1.44), (0.66, 0.52, 0.34, 1.0), roll=0.06)
    # the foosball table south of it
    fx, fy = FW + 0.85, 2.4
    make_box("Foosball_Body", (fx, fy, 0.75), (0.76, 1.30, 0.26), (0.18, 0.34, 0.60, 1.0))
    make_box("Foosball_Field", (fx, fy, 0.865), (0.66, 1.20, 0.01), FELT)
    for i, (lx, ly) in enumerate(((-0.33, -0.60), (0.33, -0.60), (-0.33, 0.60), (0.33, 0.60))):
        make_box(f"Foosball_Leg_{i}", (fx + lx, fy + ly, 0.31), (0.07, 0.07, 0.62), (0.16, 0.16, 0.18, 1.0))
    for r in range(6):
        make_cyl(f"Foosball_Rod_{r}", (fx, fy - 0.50 + r * 0.20, 0.90), 0.008, 1.20, STEEL, axis='X', segments=5)
    # the TV on its cart with the Nintendo and the cartridges, E side
    cx, cy = FE - 0.55, 3.6
    make_box("TV_Cart_Shelf_Top", (cx, cy, 0.78), (0.80, 0.56, 0.03), (0.20, 0.20, 0.22, 1.0))
    make_box("TV_Cart_Shelf_Low", (cx, cy, 0.18), (0.80, 0.56, 0.03), (0.20, 0.20, 0.22, 1.0))
    for i, (lx, ly) in enumerate(((-0.38, -0.26), (0.38, -0.26), (-0.38, 0.26), (0.38, 0.26))):
        make_box(f"TV_Cart_Post_{i}", (cx + lx, cy + ly, 0.41), (0.03, 0.03, 0.80), STEEL)
    make_chamfer_box("TV_Set", (cx, cy, 1.08), (0.62, 0.50, 0.56), (0.16, 0.16, 0.18, 1.0), chamfer=0.04)
    make_box("TV_Set_Screen", (cx - 0.315, cy, 1.10), (0.004, 0.44, 0.38), (0.22, 0.26, 0.30, 1.0))
    make_box("Nintendo_Console", (cx, cy, 0.235), (0.26, 0.20, 0.08), (0.62, 0.62, 0.62, 1.0))
    make_box("Nintendo_Pad_0", (cx - 0.30, cy - 0.10, 0.205), (0.12, 0.05, 0.02), (0.26, 0.26, 0.28, 1.0))
    rnd = random.Random(9)
    for i in range(6):
        make_rot_box(f"Cartridge_{i}", (cx - 0.70 + rnd.uniform(-0.25, 0.25), cy + rnd.uniform(-0.6, 0.6), 0.012), (0.12, 0.13, 0.024),
                     (0.44, 0.44, 0.46, 1.0), yaw=rnd.uniform(0, 3.0))
    # the back: the stack of fold-up chairs, the two pulled out by the magazine rack
    for i in range(6):
        make_box(f"Chair_Stack_{i}", (FE - 0.40, FN - 0.40, 0.45 + i * 0.03), (0.44, 0.44, 0.03), (0.52, 0.48, 0.42, 1.0))
    make_box("Chair_Stack_Legs", (FE - 0.40, FN - 0.40, 0.22), (0.40, 0.40, 0.44), (0.40, 0.40, 0.42, 1.0))
    for i, (x, yaw) in enumerate(((FE - 1.40, 0.4), (FE - 2.00, -0.2))):
        y = FN - 1.20
        make_rot_box(f"Fold_Chair_{i}_Seat", (x, y, 0.45), (0.42, 0.40, 0.03), (0.52, 0.48, 0.42, 1.0), yaw=yaw)
        make_rot_box(f"Fold_Chair_{i}_Back", (x - 0.19 * math.sin(-yaw), y - 0.19 * math.cos(yaw), 0.66), (0.42, 0.03, 0.38), (0.52, 0.48, 0.42, 1.0), yaw=yaw)
        for lx in (-0.17, 0.17):
            for ly in (-0.16, 0.16):
                rx = lx * math.cos(yaw) - ly * math.sin(yaw)
                ry = lx * math.sin(yaw) + ly * math.cos(yaw)
                make_box(f"Fold_Chair_{i}_Leg_{lx:+.2f}_{ly:+.2f}", (x + rx, y + ry, 0.215), (0.02, 0.02, 0.43), STEEL)
    mx = FE - 0.05
    make_box("Magazine_Rack", (mx, FN - 1.95, 1.05), (0.10, 0.70, 0.90), WOOD)
    for i in range(3):
        make_box(f"Magazine_{i}", (mx - 0.07, FN - 2.15 + i * 0.20, 1.20 - (i % 2) * 0.30), (0.02, 0.18, 0.26), [(0.80, 0.30, 0.26, 1.0), (0.30, 0.50, 0.66, 1.0), (0.86, 0.80, 0.40, 1.0)][i])
    # the bulletin board, the drinking fountain, the restroom doors, the snack window
    make_box("Bulletin_Board", (FW + 0.02, 7.8, 1.55), (0.03, 1.20, 0.80), (0.62, 0.48, 0.32, 1.0))
    for i in range(5):
        make_box(f"Bulletin_Flyer_{i}", (FW + 0.04, 7.35 + i * 0.22, 1.50 + (i % 2) * 0.18), (0.004, 0.18, 0.24), [(0.94, 0.92, 0.86, 1.0), (0.96, 0.86, 0.40, 1.0)][i % 2])
    make_box("Fountain_Body", (FE - 0.18, 6.4, 0.80), (0.32, 0.40, 0.30), STEEL)
    make_box("Fountain_Bracket", (FE - 0.11, 6.4, 0.55), (0.10, 0.20, 0.40), STEEL)
    for i, x in enumerate((-4.6, -3.4)):
        make_box(f"Restroom_Door_{i}", (x, FN - 0.03, 1.02), (0.86, 0.05, 2.04), (0.46, 0.40, 0.34, 1.0))
        make_box(f"Restroom_Sign_{i}", (x, FN - 0.065, 1.62), (0.18, 0.01, 0.18), (0.30, 0.40, 0.66, 1.0))
    make_box("Snack_Window_Shutter", (-1.6, FN - 0.03, 1.40), (1.40, 0.04, 0.90), (0.62, 0.62, 0.60, 1.0))
    make_box("Snack_Window_Sill", (-1.6, FN - 0.15, 0.94), (1.50, 0.24, 0.04), (0.80, 0.78, 0.72, 1.0))
    make_wall_outlet("Outlet_N", (1.4, YN), axis='X', face_sign=-1)
    make_floor_stain("Floor_Stain_0", (3.0, 1.8), radius=0.30)
    make_floor_stain("Floor_Stain_1", (-3.5, 6.8), radius=0.22)


def build_street():
    """The main drag at night past the doors and windows."""
    make_box("Out_Sidewalk", (0.0, -2.0, -0.03), (40.0, 4.0, 0.06), (0.50, 0.48, 0.44, 1.0))
    make_box("Out_Street", (0.0, -9.0, -0.12), (40.0, 10.0, 0.06), (0.24, 0.24, 0.26, 1.0))
    for i in range(4):
        make_box(f"Out_Shopfront_{i}", (-12.0 + i * 8.0, -16.0, 2.5), (7.0, 0.6, 5.0), [(0.46, 0.40, 0.34, 1.0), (0.52, 0.50, 0.46, 1.0)][i % 2])
        make_box(f"Out_Shopfront_{i}_Window", (-12.0 + i * 8.0, -15.69, 1.6), (4.0, 0.02, 1.6), (0.86, 0.72, 0.44, 1.0) if i in (1, 3) else (0.16, 0.18, 0.22, 1.0))
    make_box("Out_Sidewalk_Far", (0.0, -16.0, -0.03), (40.0, 3.0, 0.06), (0.50, 0.48, 0.44, 1.0))
    make_cyl("Out_Street_Lamp_Pole", (1.5, -3.6, 2.2), 0.06, 4.4, (0.24, 0.24, 0.26, 1.0), segments=8)
    make_box("Out_Street_Lamp_Head", (1.5, -4.0, 4.3), (0.26, 0.60, 0.14), (0.96, 0.86, 0.58, 1.0))


def main():
    clear_scene()
    build_shell(); build_dance(); build_edges(); build_street()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/small_wood_rec_center.glb"))
    print(f"\n[build_small_wood_rec_center] exporting to {out}")
    export_glb(out)


if __name__ == "__main__": main()
