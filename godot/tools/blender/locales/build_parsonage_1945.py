"""parsonage_1945 — vol 3's 1945 house in Pasadena: Ron's room upstairs and
the hall outside it (draft 1, 2026-10-18).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
"The Parsonage" is only the stem's name: the text calls the place "the
mansion", "the house". Upstairs ("up there in his room"; "Downstairs was a
ruckus unholy"; "Ron catches me on the stairs").
RON'S ROOM:
  "Books on the floor in drifts, dust in the lamplight, nowhere to stand"
   — but "the one patch of floor not drowned in books"   → Books_Stock_*,
                                         the clear patch by the desk
  a bed with springs; books slide off "the far side of the bed"
                                       → the iron bed, its far side open
  the desk, Ron "half turned away", "The typewriter is black and big as an
   engine block", the fresh sheet with a carbon behind it, the pages laid
   face down                           → Desk_*, Typewriter_*, Pages_*
  the lamp ("dust in the lamplight")   → Lamp_Desk
  the window on the street: at dawn the street "always empty at this hour",
   "A streetlamp still burns at the corner"; in ch19 the window open, "the
   air comes in heavy with oranges"   → the window over the street; the
                                         sash raised in the ch19 view only
  the door onto the hall with a gap beneath it          → Door_Ron
THE HALL — wide enough for "a meeting or something", people "pressed up
  intimate" around Jack: the stair head, the other rooms' doors.
What the window shows is per view: a sky card for dawn, day or night.

Blender: x east, y north, z up; Godot (x, z, -y). The upstairs floor is at
z 0 (the wall helpers build from z 0); the street runs a storey below, at
z -3.4, past the S wall.

DRAFT 2 targets: the house's exterior (the text gives none); the downstairs
and the table "at the table" tonight; the orange trees behind the street;
Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_blob, make_taper_cyl,
                             join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings
from _props.furniture import make_chair, make_lamp

F = 0.0                                     # the upstairs floor (our walls rise from z 0)
G = -3.4                                    # the street, a storey below
X0, X1, D, H, T = -2.6, 2.6, 4.6, 2.9, 0.20
WALL = (0.80, 0.74, 0.62, 1.0); BASE = (0.40, 0.30, 0.22, 1.0)
PAL = {"wall": WALL, "baseboard": BASE}
OAK = (0.50, 0.36, 0.24, 1.0); OAK_DARK = (0.34, 0.24, 0.16, 1.0)
WIN_X, WIN_Z, WIN_W, WIN_H = 0.9, F + 1.55, 1.10, 1.50
DAWN, DAY = "__ron_dawn", "__ron_day"
NIGHT = "__ron_night_floor__ron_night_bed"
BOOK_COLS = [(0.36, 0.20, 0.16), (0.20, 0.26, 0.36), (0.30, 0.34, 0.24), (0.62, 0.54, 0.40), (0.16, 0.16, 0.18), (0.50, 0.30, 0.20),
             (0.70, 0.64, 0.50)]


def build_house():
    """The upstairs as a floor on the house's mass; the room and the hall."""
    # the house below, cut round the stair going down (x 4.3..5.95)
    make_box("House_Mass_Below", (-1.35, 5.0, (G - 0.12) / 2.0), (11.3, 12.0, -G - 0.12), (0.84, 0.80, 0.70, 1.0))
    make_box("House_Mass_Below_E", (6.475, 5.0, (G - 0.12) / 2.0), (1.05, 12.0, -G - 0.12), (0.84, 0.80, 0.70, 1.0))
    make_floor("Ron_Floor", (0.0, D / 2.0, F), size_x=X1 - X0 + 0.4, size_y=D + 0.4,
               palette={"vinyl": (0.52, 0.38, 0.26, 1.0), "seam": (0.42, 0.30, 0.20, 1.0)})
    make_box("Ron_Ceil", (0.0, D / 2.0, F + H + 0.04), (X1 - X0 + 0.4, D + 0.4, 0.08), (0.88, 0.84, 0.76, 1.0))
    make_wall("Ron_Wall_W", (X0, D / 2.0, F), length=D + 0.4, height=H, thickness=T, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall("Ron_Wall_E", (X1, D / 2.0, F), length=D + 0.4, height=H, thickness=T, axis='Y', palette=PAL, baseboard_face_sign=-1)
    make_wall_with_openings("Ron_Wall_S", (0.0, 0.0, F), length=X1 - X0 + 0.4, height=H, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=+1, openings=[(WIN_X, WIN_Z, WIN_W, WIN_H)])
    make_wall_with_openings("Ron_Wall_N", (0.0, D, F), length=X1 - X0 + 0.4, height=H, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=-1, openings=[(-1.6, F + 1.0, 0.86, 2.0)])
    # the window: frame, the two sashes; the lower sash raised in ch19 only
    make_box("Window_Frame_Head", (WIN_X, 0.0, WIN_Z + WIN_H / 2.0 + 0.04), (WIN_W + 0.16, 0.24, 0.08), (0.92, 0.90, 0.84, 1.0))
    make_box("Window_Sill", (WIN_X, 0.06, WIN_Z - WIN_H / 2.0 - 0.03), (WIN_W + 0.20, 0.30, 0.05), (0.92, 0.90, 0.84, 1.0))
    make_box("Window_Upper_Sash", (WIN_X, 0.04, WIN_Z + WIN_H / 4.0), (WIN_W, 0.04, WIN_H / 2.0), (0.92, 0.90, 0.84, 1.0))
    make_box("Window_Upper_Bar", (WIN_X, 0.04, WIN_Z + WIN_H / 4.0), (0.03, 0.05, WIN_H / 2.0 - 0.06), (0.92, 0.90, 0.84, 1.0))
    make_box("Window_Lower_Sash__ron_dawn__ron_day__ron_night_floor", (WIN_X, -0.01, WIN_Z - WIN_H / 4.0), (WIN_W, 0.04, WIN_H / 2.0),
             (0.92, 0.90, 0.84, 1.0))
    make_box("Window_Lower_Sash_Raised__ron_night_bed", (WIN_X, -0.01, WIN_Z + WIN_H / 4.0), (WIN_W, 0.04, WIN_H / 2.0),
             (0.92, 0.90, 0.84, 1.0))
    make_box("Window_Shade", (WIN_X, 0.12, WIN_Z + WIN_H / 2.0 - 0.10), (WIN_W, 0.02, 0.16), (0.90, 0.86, 0.70, 1.0))
    # the hall north of the room: wide, the stair head at its E end
    hy0, hy1 = D + 0.10, D + 3.70
    hcy = (hy0 + hy1) / 2.0
    make_floor("Hall_Floor", (0.0, hcy, F), size_x=12.0, size_y=hy1 - hy0, palette={"vinyl": (0.50, 0.36, 0.24, 1.0), "seam": (0.40, 0.28, 0.20, 1.0)})
    make_box("Hall_Ceil", (0.0, hcy, F + H + 0.04), (12.0, hy1 - hy0, 0.08), (0.88, 0.84, 0.76, 1.0))
    make_wall_with_openings("Hall_Wall_N", (0.0, hy1, F), length=12.0, height=H, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=-1, openings=[(-3.6, F + 1.0, 0.86, 2.0), (0.4, F + 1.0, 0.86, 2.0)])
    make_wall("Hall_Wall_W", (-6.0, hcy, F), length=hy1 - hy0 + 0.2, height=H, thickness=T, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall("Hall_Wall_S_West", (-4.3, hy0 - 0.05, F), length=3.4, height=H, thickness=0.10, axis='X', palette=PAL, baseboard_face_sign=+1)
    make_wall("Hall_Wall_S_East", (4.3, hy0 - 0.05, F), length=3.4, height=H, thickness=0.10, axis='X', palette=PAL, baseboard_face_sign=+1)
    for k, x in enumerate((-3.6, 0.4)):
        make_box(f"Hall_Door_{k}", (x, hy1, F + 1.0), (0.84, 0.05, 2.0), (0.50, 0.36, 0.24, 1.0))
    # the stair head: the banister, the newel, the first treads going down
    sx = 5.0
    make_box("Stair_Well_Floor", (sx, hcy, F - 1.0), (1.6, 3.0, 0.1), (0.40, 0.30, 0.22, 1.0))
    for k in range(5):
        make_box(f"Stair_Tread_{k}", (sx, hy0 + 0.3 + k * 0.28, F - 0.19 - k * 0.19), (1.0, 0.30, 0.04), OAK)
    make_box("Banister_Rail", (sx - 0.60, hcy, F + 0.91), (0.06, 3.0, 0.06), OAK_DARK)
    for k in range(10):
        make_box(f"Banister_Spindle_{k}", (sx - 0.60, hy0 + 0.2 + k * 0.32, F + 0.44), (0.03, 0.03, 0.88), OAK_DARK)
    make_box("Newel_Post", (sx - 0.60, hy0 + 0.05, F + 0.55), (0.12, 0.12, 1.10), OAK_DARK)
    make_box("Stair_Well_Wall", (sx + 0.85, hcy, F), (0.10, 3.4, H + 2.0), WALL)
    for k in range(3):
        make_box(f"Hall_Sconce_{k}", (-4.5 + k * 3.5, hy1 - 0.12, F + 2.0), (0.14, 0.12, 0.20), (0.96, 0.86, 0.60, 1.0))
    make_box("Hall_Runner", (-0.5, hcy, F + 0.006), (10.0, 1.2, 0.01), (0.46, 0.20, 0.18, 1.0))


def build_room():
    # the iron bed against the E wall, its foot to the S; the far side (W) open
    bx, by = X1 - 0.10 - 0.50, 2.6
    for e in (-1, 1):
        make_box(f"Bed_Frame_End_{e:+d}", (bx, by + e * 0.98, F + 0.50), (1.00, 0.04, 1.00 if e > 0 else 0.70), (0.20, 0.20, 0.22, 1.0))
    make_box("Bed_Springs", (bx, by, F + 0.42), (0.96, 1.92, 0.08), (0.42, 0.42, 0.44, 1.0))
    make_box("Bed_Mattress", (bx, by, F + 0.54), (0.94, 1.90, 0.16), (0.86, 0.84, 0.76, 1.0))
    make_box("Bed_Blanket", (bx, by - 0.20, F + 0.63), (0.96, 1.30, 0.03), (0.40, 0.36, 0.30, 1.0))
    for s in (-1, 1):
        for e in (-1, 1):
            make_box(f"Bed_Leg_{s:+d}_{e:+d}", (bx + s * 0.46, by + e * 0.96, F + 0.19), (0.04, 0.04, 0.38), (0.20, 0.20, 0.22, 1.0))
    for k in range(6):       # books on the bed too
        make_rot_box(f"Bed_Book_{k}", (bx - 0.25 + (k % 3) * 0.18, by + 0.5 - (k // 3) * 0.3, F + 0.66 + (k % 2) * 0.03),
                     (0.16, 0.24, 0.03), (*BOOK_COLS[k % len(BOOK_COLS)], 1.0), yaw=k * 0.5)
    # the desk on the W wall, Ron's chair half turned toward the room
    dx, dy = X0 + 0.10 + 0.36, 2.3
    make_box("Desk_Top", (dx, dy, F + 0.74), (0.72, 1.30, 0.04), OAK)
    for s in (-1, 1):
        make_box(f"Desk_Pedestal_{s:+d}", (dx, dy + s * 0.48, F + 0.36), (0.68, 0.34, 0.72), OAK_DARK)
    make_chair("Desk_Chair", dx + 0.60, dy - 0.10, yaw=-math.pi / 2.0 - 0.6, wood=OAK_DARK)
    # the typewriter: black, big as an engine block; the sheet and carbon in it
    tx, ty, tz = dx + 0.05, dy, F + 0.76
    make_chamfer_box("Typewriter_Body", (tx, ty, tz + 0.10), (0.42, 0.48, 0.20), (0.08, 0.08, 0.09, 1.0), chamfer=0.04)
    make_cyl("Typewriter_Platen", (tx - 0.10, ty, tz + 0.22), 0.04, 0.50, (0.12, 0.12, 0.12, 1.0), axis='Y', segments=12)
    make_box("Typewriter_Sheet", (tx - 0.12, ty, tz + 0.34), (0.004, 0.22, 0.24), (0.96, 0.96, 0.92, 1.0))
    make_box("Typewriter_Carbon", (tx - 0.11, ty, tz + 0.33), (0.002, 0.22, 0.22), (0.10, 0.10, 0.14, 1.0))
    make_box("Typewriter_Keys", (tx + 0.14, ty, tz + 0.07), (0.16, 0.42, 0.06), (0.16, 0.16, 0.16, 1.0))
    make_box("Typewriter_Lever", (tx - 0.10, ty + 0.28, tz + 0.26), (0.03, 0.10, 0.02), (0.70, 0.70, 0.72, 1.0))
    make_box("Pages_Face_Down", (dx + 0.06, dy - 0.48, F + 0.78), (0.22, 0.28, 0.04), (0.92, 0.90, 0.82, 1.0))
    make_box("Carbon_Box", (dx - 0.10, dy + 0.48, F + 0.78), (0.22, 0.30, 0.04), (0.20, 0.20, 0.26, 1.0))
    make_lamp("Lamp_Desk", dx - 0.10, dy - 0.15 + 0.62, base_z=F + 0.76, h=0.46)
    # the books in drifts over the floor, leaving the one patch by the desk
    k = 0
    for i in range(10):
        for j in range(9):
            x = X0 + 0.35 + i * 0.47
            y = 0.30 + j * 0.47
            if (abs(x - (dx + 1.0)) < 0.55 and abs(y - 2.0) < 0.80) or (x > bx - 0.55 and 1.5 < y < 3.7) or (x < X0 + 0.85 and 1.5 < y < 3.1):
                continue        # the clear patch, the bed, the desk
            if -2.3 < x < -0.8 and y > 3.2:
                continue        # the door's swing
            n = 1 + ((i * 7 + j * 3) % 4)
            for m in range(n):
                make_rot_box(f"Books_Stock_{k}", (x + (m % 2) * 0.05, y, F + 0.025 + m * 0.05), (0.18 + (m % 3) * 0.03, 0.26, 0.05),
                             (*BOOK_COLS[(k * 3) % len(BOOK_COLS)], 1.0), yaw=((i + j + m) % 5) * 0.35)
                k += 1
    # the door onto the hall, shut, the gap under it
    make_box("Door_Ron", (-1.6, D, F + 1.0), (0.84, 0.05, 2.0), (0.50, 0.36, 0.24, 1.0))
    make_cyl("Door_Ron_Knob", (-1.26, D - 0.045, F + 0.98), 0.026, 0.04, (0.70, 0.62, 0.40, 1.0), axis='Y', segments=10)
    make_box("Ceiling_Fixture", (0.0, 2.3, F + H - 0.05), (0.30, 0.30, 0.10), (0.94, 0.90, 0.78, 1.0))


def build_street():
    """Below the window: the street at dawn empty, the streetlamp at the
    corner, the houses across; the sky card per view."""
    make_box("Street_Road", (0.0, -10.0, G - 0.01), (60.0, 9.0, 0.02), (0.32, 0.32, 0.32, 1.0))
    for s in (-1, 1):
        make_box(f"Street_Walk_{s:+d}", (0.0, -10.0 + s * 6.0, G + 0.06), (60.0, 3.0, 0.12), (0.70, 0.68, 0.62, 1.0))
    make_box("Front_Yard", (0.0, -2.5, G), (20.0, 5.0, 0.02), (0.40, 0.50, 0.28, 1.0))
    make_cyl("Streetlamp_Post", (-9.0, -4.6, G + 2.2), 0.08, 4.4, (0.20, 0.22, 0.24, 1.0), segments=8)
    make_box("Streetlamp_Arm", (-8.6, -4.6, G + 4.36), (0.80, 0.06, 0.06), (0.20, 0.22, 0.24, 1.0))
    make_blob("Streetlamp_Globe", (-8.2, -4.6, G + 4.20), 0.18, (1.0, 0.92, 0.70, 1.0), noise=0.0, seed=1)
    for k in range(5):
        make_box(f"Across_House_{k}", (-16.0 + k * 8.0, -22.0, G + 3.0), (6.4, 7.0, 6.0),
                 ((0.86, 0.82, 0.72, 1.0), (0.78, 0.70, 0.58, 1.0), (0.90, 0.88, 0.80, 1.0))[k % 3])
        make_box(f"Across_Roof_{k}", (-16.0 + k * 8.0, -22.0, G + 6.2), (6.8, 7.4, 0.40), (0.56, 0.30, 0.22, 1.0))
    for k in range(6):
        x = -18.0 + k * 7.2
        make_cyl(f"Street_Tree_{k}_Trunk", (x, -16.4, G + 1.2), 0.14, 2.4, (0.36, 0.28, 0.20, 1.0), segments=8)
        make_blob(f"Street_Tree_{k}_Crown", (x, -16.4, G + 3.4), 1.6, (0.24, 0.40, 0.22, 1.0), noise=0.25, seed=k)
    # the sky beyond, a card per light
    make_box("Sky_Card" + DAWN, (0.0, -45.0, G + 15.0), (120.0, 0.2, 30.0), (0.78, 0.74, 0.76, 1.0))
    make_box("Sky_Card" + DAY, (0.0, -45.0, G + 15.0), (120.0, 0.2, 30.0), (0.62, 0.76, 0.92, 1.0))
    make_box("Sky_Card__ron_night_floor__ron_night_bed__parsonage_hall", (0.0, -45.0, G + 15.0), (120.0, 0.2, 30.0), (0.04, 0.05, 0.10, 1.0))


def main():
    clear_scene()
    build_house()
    build_room()
    build_street()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/parsonage_1945.glb"))
    print(f"\n[build_parsonage_1945] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
