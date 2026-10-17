"""small_wood_ranch — vol 2's family ranch in Small Wood (draft 1, 2026-10-17).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
The narrator's family's place on the Oregon coast, 1993-94: his bedroom in
the old ranch house (five scene uses: the window at night, the reading
lamp, and "the room" Dean rebuilds up the hill, which IS this room) and the
second house on the property, where he moves out to read by kerosene.

What the scenes say, and where it is here:
  "those wood plank blinds my grandmother hung, knocking at the frame"
                                       → Blind_N: wide wooden slats over the
                                         N window, a few hung crooked
  "I'd just look out my window at the moon on the night horizon, falling
   behind the many trees"              → View_N's firs and the Moon disc
  "On the nightstand where my clock radio used to sit there was a stick of
   grey plastic about as long as a pencil"
                                       → Nightstand; Clock_Radio in the night
                                         presets, Grey_Stick in "the room"
  "On the hook behind the door where I hung my jacket"
                                       → Door_Hook + Jacket (S wall)
  "The paperback's pages had gone soft at the corners, the house dark and
   quiet around the lamp"              → Lamp_Reading by the bed, the book
  "the second house on the property in my little room sleeping on old and
   dirty mattresses. I'd brought in a kerosene lamp to read by ... the walls
   shone through bare in places, stripped to the board"
                                       → the second house (x 30..34): bare
                                         studs and boards, two mattresses,
                                         Kerosene_Lamp
  "I'd painted what remained of the plaster on the walls with natural
   earthy colors and hidden shapes, shadow figures"
                                       → Plaster_Patch_* with Figure_*

Blender: x east, y north, z up; Godot (x, z, -y). The bedroom is x -1.9..1.9,
y 0..4.2, ceiling 2.45 (an old farmhouse room); the second house's room is
x 30..34, y 0..3.6, ceiling 2.3, alone in its own field.

DRAFT 2 targets: the field and the road between the two houses (vol2_room_
roof_dusk is "From the roof the field ran down to the road ... the second
house off to the left with its windows gone": a third preset on the roof);
the rest of the ranch house (the hall, the family below); Dean's own 1994
bedroom and basement are another set (dean_house_1994); the empty version
of "the room" ("white walls and a drain in the middle of the floor") as a
per-preset prop switch; Deck-verified framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_lathe, make_rot_box,
                             export_glb)
from _props.views import make_view
from _props.structure import make_floor, make_wall, make_ceiling, make_window, make_wall_with_openings
from _props.furniture import make_bed, make_chair, make_lamp
from _props.decor import make_faded_poster
from _props.detail import make_wall_outlet, make_light_switch, make_traffic_wear

W, D, CEIL, T = 3.8, 4.2, 2.45, 0.20
PAL = {"wall": (0.82, 0.80, 0.72, 1.0), "baseboard": (0.40, 0.32, 0.24, 1.0)}
FLOOR = (0.50, 0.38, 0.26, 1.0); FLOOR_SEAM = (0.38, 0.28, 0.18, 1.0)
PINE = (0.62, 0.48, 0.30, 1.0); PINE_DARK = (0.44, 0.32, 0.20, 1.0)
SLAT = (0.66, 0.52, 0.34, 1.0)
BOARD = (0.46, 0.38, 0.30, 1.0); BOARD_DARK = (0.32, 0.26, 0.20, 1.0)
PLASTER = (0.78, 0.74, 0.66, 1.0)
EARTH = [(0.56, 0.36, 0.22, 1.0), (0.42, 0.44, 0.26, 1.0), (0.62, 0.50, 0.30, 1.0), (0.34, 0.24, 0.20, 1.0)]
WIN_X, WIN_W, WIN_H, WIN_Z = 0.20, 1.30, 1.25, 1.45

# second house
HX0, HX1, HD, HCEIL = 30.0, 34.0, 3.6, 2.3


def build_bedroom():
    make_floor("Floor", (0.0, D / 2.0, 0.0), size_x=W + 0.4, size_y=D + 0.4, palette={"vinyl": FLOOR, "seam": FLOOR_SEAM})
    make_ceiling("Ceil", (0.0, D / 2.0, CEIL), size_x=W + 0.4, size_y=D + 0.4, with_grid=False, with_stains=True,
                 palette={"tile": (0.90, 0.88, 0.82, 1.0)})
    make_wall("Wall_W", (-W / 2.0, D / 2.0, 0), length=D + 0.4, height=CEIL, thickness=T, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_E", (W / 2.0, D / 2.0, 0), length=D + 0.4, height=CEIL, thickness=T, axis='Y', palette=PAL, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_N", (0.0, D, 0), length=W + 0.4, height=CEIL, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=-1, openings=[(WIN_X, WIN_Z, WIN_W, WIN_H)])
    door_x = 1.20
    make_wall_with_openings("Wall_S", (0.0, 0.0, 0), length=W + 0.4, height=CEIL, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=+1, openings=[(door_x, 1.0, 0.82, 2.0)])
    make_window("Window_N", (WIN_X, D - 0.10, WIN_Z), width=WIN_W, height=WIN_H, see_through=True)
    # the wood plank blinds: wide slats, the cords, two hanging out of true
    make_box("Blind_N_Head", (WIN_X, D - 0.17, WIN_Z + WIN_H / 2.0 + 0.04), (WIN_W + 0.08, 0.06, 0.05), PINE_DARK)
    for k in range(14):
        z = WIN_Z + WIN_H / 2.0 - 0.04 - k * 0.075
        tilt = 0.10 if k in (9, 10) else 0.0
        make_rot_box(f"Blind_N_Slat_{k}", (WIN_X + (0.02 if k == 10 else 0.0), D - 0.18, z), (WIN_W, 0.07, 0.008), SLAT,
                     roll=0.35 + tilt, yaw=(0.04 if k == 9 else 0.0))
    for s in (-1, 1):
        make_box(f"Blind_N_Cord_{s:+d}", (WIN_X + s * WIN_W * 0.3, D - 0.19, WIN_Z - 0.08), (0.006, 0.006, WIN_H + 0.10), (0.88, 0.84, 0.74, 1.0))
    make_box("Blind_N_Pull", (WIN_X + WIN_W / 2.0 - 0.06, D - 0.21, WIN_Z - 0.30), (0.008, 0.008, 0.60), (0.88, 0.84, 0.74, 1.0))
    # the door, open against the E wall, the hook behind it and the jacket on it
    make_box("Door", (door_x + 0.43, 0.10 + 0.40, 0.995), (0.04, 0.80, 1.99), PINE)
    make_cyl("Door_Knob", (door_x + 0.39, 0.82, 0.96), 0.028, 0.05, (0.62, 0.52, 0.28, 1.0), axis='X', segments=10)
    make_box("Door_Hook", (door_x + 0.40, 0.42, 1.78), (0.03, 0.03, 0.06), (0.24, 0.22, 0.20, 1.0))
    make_box("Jacket", (door_x + 0.38, 0.42, 1.38), (0.06, 0.46, 0.78), (0.20, 0.26, 0.34, 1.0))
    # the bed along the W wall, its head at the N end under the window's edge
    make_bed("Bed", -W / 2.0 + 0.10 + 0.50, D - 0.10 - 0.98, head="+Y", w=0.99, d=1.92,
             blanket_col=(0.40, 0.30, 0.26, 1.0), sheet_col=(0.86, 0.84, 0.76, 1.0))
    # the nightstand with the clock radio, the reading lamp and the paperback
    nx, ny = -W / 2.0 + 0.10 + 1.25, D - 0.10 - 0.24
    make_box("Nightstand", (nx, ny, 0.29), (0.42, 0.40, 0.58), PINE_DARK)
    # the clock radio is there at night; in "the room" Dean rebuilt (the day
    # preset) it is gone — "On the nightstand where my clock radio used to sit
    # there was a stick of grey plastic about as long as a pencil" — and the
    # stick lies there instead (Background3D strips `__<preset>` meshes)
    night = "__ranch_bedroom_night__ranch_bedroom_lamp"
    make_box("Clock_Radio" + night, (nx - 0.06, ny + 0.04, 0.635), (0.24, 0.12, 0.09), (0.16, 0.14, 0.13, 1.0))
    make_box("Clock_Radio_Face" + night, (nx - 0.06, ny - 0.022, 0.64), (0.14, 0.004, 0.04), (0.92, 0.28, 0.16, 1.0))
    make_cyl("Grey_Stick__ranch_bedroom_day", (nx - 0.10, ny - 0.12, 0.592), 0.009, 0.17, (0.58, 0.58, 0.60, 1.0),
             axis='X', segments=8)
    make_lamp("Lamp_Reading", nx + 0.10, ny + 0.06, base_z=0.58, h=0.46)
    make_box("Paperback", (nx + 0.02, ny - 0.10, 0.596), (0.11, 0.18, 0.025), (0.62, 0.24, 0.18, 1.0))
    make_box("Paperback_Pages", (nx + 0.02, ny - 0.10, 0.598), (0.10, 0.17, 0.02), (0.92, 0.88, 0.76, 1.0))
    # his desk on the E wall: a cassette deck, tapes, a stack of library books
    dx, dy = W / 2.0 - 0.10 - 0.30, 2.30
    make_box("Desk_Top", (dx, dy, 0.74), (0.58, 1.10, 0.03), PINE)
    for s in (-1, 1):
        make_box(f"Desk_Leg_{s:+d}", (dx, dy + s * 0.52, 0.365), (0.54, 0.03, 0.73), PINE)
    make_chair("Desk_Chair", dx - 0.62, dy, yaw=-math.pi / 2.0, wood=PINE)
    make_box("Tape_Deck", (dx + 0.05, dy + 0.32, 0.80), (0.30, 0.38, 0.10), (0.20, 0.20, 0.22, 1.0))
    for k in range(7):
        make_box(f"Tape_{k}", (dx + 0.10, dy - 0.10 + k * 0.03, 0.795), (0.11, 0.018, 0.07), (0.80 - k * 0.07, 0.70, 0.60, 1.0))
    for k in range(4):
        make_box(f"Library_Book_{k}", (dx, dy - 0.36, 0.77 + k * 0.035), (0.17, 0.25, 0.032),
                 ((0.30, 0.34, 0.46, 1.0), (0.48, 0.26, 0.20, 1.0), (0.36, 0.40, 0.30, 1.0), (0.60, 0.52, 0.36, 1.0))[k])
    # a dresser on the S wall, a poster and a pennant
    make_box("Dresser", (-0.70, 0.10 + 0.25, 0.48), (0.86, 0.48, 0.96), PINE_DARK)
    for k in range(3):
        make_box(f"Dresser_Drawer_{k}", (-0.70, 0.10 + 0.495, 0.20 + k * 0.29), (0.80, 0.012, 0.24), PINE)
    make_faded_poster("Poster_E", (W / 2.0 - 0.104, 3.30, 1.70), into_room=-1)
    make_box("Rug", (0.10, 2.10, 0.006), (1.40, 1.00, 0.012), (0.42, 0.40, 0.36, 1.0))
    make_box("Clothes_Floor", (0.30, 1.40, 0.04), (0.50, 0.36, 0.08), (0.34, 0.38, 0.30, 1.0))
    make_cyl("Ceiling_Fixture", (0.0, D / 2.0, CEIL - 0.06), 0.17, 0.10, (0.92, 0.88, 0.76, 1.0), segments=12)
    make_light_switch("Switch_Door", (door_x - 0.62, 0.0), axis='X', face_sign=1, aged=True)
    make_wall_outlet("Outlet_Bed", (-W / 2.0, 3.20), axis='Y', face_sign=1, aged=True)
    make_traffic_wear("Wear_Door_Bed", [(door_x, 0.4), (-0.6, 3.2)], width=0.6,
                      tint=(FLOOR[0] * 0.86, FLOOR[1] * 0.86, FLOOR[2] * 0.86, 1.0))
    # through the window: the firs, and the moon low over them (night presets light it)
    make_view("View_N", "N", D, 0.0, kind="back", ground_z=-0.4, seed=21)
    make_cyl("Moon", (-6.0, D + 60.0, 9.0), 1.6, 0.05, (0.96, 0.94, 0.86, 1.0), axis='Y', segments=24)
    for k in range(9):
        a = k * 0.7
        make_lathe(f"Fir_Far_{k}", (-20.0 + k * 5.0, D + 34.0 + (k % 3) * 4.0, -0.4),   # beyond the view's houses
                   [(1.6, 0.0), (1.2, 2.5), (0.9, 5.0), (0.5, 7.5), (0.0, 10.0 + (k % 4) * 1.5)],
                   (0.12, 0.20, 0.14, 1.0), segments=8)


def build_second_house():
    """The little room in the second house: stud walls stripped to the
    board, a last of the plaster painted with earthy shadow figures, two
    mattresses on the boards, the kerosene lamp."""
    cx, cy = (HX0 + HX1) / 2.0, HD / 2.0
    make_floor("SH_Floor", (cx, cy, 0.0), size_x=(HX1 - HX0) + 0.4, size_y=HD + 0.4,
               palette={"vinyl": BOARD, "seam": BOARD_DARK})
    make_box("SH_Ceil", (cx, cy, HCEIL + 0.03), ((HX1 - HX0) + 0.4, HD + 0.4, 0.06), BOARD_DARK)
    for k in range(5):
        make_box(f"SH_Joist_{k}", (HX0 + 0.4 + k * 0.80, cy, HCEIL - 0.06), (0.06, HD, 0.12), BOARD_DARK)
    pal = {"wall": BOARD, "baseboard": BOARD_DARK}
    make_wall("SH_Wall_W", (HX0, cy, 0), length=HD + 0.4, height=HCEIL, thickness=0.14, axis='Y', palette=pal, baseboard_face_sign=+1)
    make_wall_with_openings("SH_Wall_E", (HX1, cy, 0), length=HD + 0.4, height=HCEIL, thickness=0.14, axis='Y', palette=pal,
                            baseboard_face_sign=-1, openings=[(1.8, 1.4, 0.90, 1.0)])          # its window gone
    make_wall("SH_Wall_N", (cx, HD, 0), length=(HX1 - HX0) + 0.4, height=HCEIL, thickness=0.14, axis='X', palette=pal, baseboard_face_sign=-1)
    make_wall_with_openings("SH_Wall_S", (cx, 0.0, 0), length=(HX1 - HX0) + 0.4, height=HCEIL, thickness=0.14, axis='X', palette=pal,
                            baseboard_face_sign=+1, openings=[(HX0 + 1.0, 1.0, 0.80, 2.0)])
    # the studs showing where the plaster came off (inside faces)
    for k in range(8):
        x = HX0 + 0.35 + k * 0.48
        make_box(f"SH_Stud_N_{k}", (x, HD - 0.085, HCEIL / 2.0), (0.05, 0.03, HCEIL), BOARD_DARK)
    for k in range(6):
        y = 0.40 + k * 0.48
        make_box(f"SH_Stud_W_{k}", (HX0 + 0.085, y, HCEIL / 2.0), (0.03, 0.05, HCEIL), BOARD_DARK)
    # what remains of the plaster, painted: earthy grounds with shadow figures in them
    for k, (y, z, w, h) in enumerate(((0.9, 1.30, 1.20, 1.10), (2.4, 1.10, 0.90, 1.40))):
        make_box(f"SH_Plaster_Patch_W_{k}", (HX0 + 0.105, y, z), (0.012, w, h), PLASTER)
        make_box(f"SH_Paint_W_{k}", (HX0 + 0.113, y, z), (0.004, w * 0.92, h * 0.90), EARTH[k])
        make_box(f"SH_Figure_W_{k}", (HX0 + 0.117, y + 0.05, z - 0.05), (0.004, w * 0.22, h * 0.62), EARTH[3])
        make_lathe(f"SH_Figure_W_{k}_Head", (HX0 + 0.117, y + 0.05, z + h * 0.30), [(0.0, 0.0), (0.09, 0.05), (0.08, 0.14), (0.0, 0.18)],
                   EARTH[3], segments=8)
    make_box("SH_Plaster_Patch_N", (HX0 + 2.6, HD - 0.105, 1.25), (1.40, 0.012, 1.20), PLASTER)
    make_box("SH_Paint_N", (HX0 + 2.6, HD - 0.113, 1.25), (1.30, 0.004, 1.10), EARTH[1])
    for k in range(3):
        make_box(f"SH_Figure_N_{k}", (HX0 + 2.2 + k * 0.40, HD - 0.117, 1.10 + (k % 2) * 0.10), (0.16, 0.004, 0.70), EARTH[(k + 2) % 4])
    # two old mattresses on the boards, a blanket, the lamp, books
    make_chamfer_box("SH_Mattress_0", (HX0 + 1.10, 2.40, 0.10), (1.00, 1.90, 0.20), (0.74, 0.70, 0.60, 1.0), chamfer=0.04)
    make_chamfer_box("SH_Mattress_1", (HX0 + 1.18, 2.36, 0.27), (0.96, 1.86, 0.14), (0.70, 0.66, 0.56, 1.0), chamfer=0.04)
    for k in range(3):
        make_box(f"SH_Mattress_Stain_{k}", (HX0 + 0.9 + k * 0.22, 2.0 + k * 0.30, 0.342), (0.22, 0.18, 0.002), (0.58, 0.50, 0.38, 1.0))
    make_box("SH_Blanket", (HX0 + 1.20, 2.70, 0.35), (0.90, 1.00, 0.03), (0.28, 0.30, 0.36, 1.0))
    lx, ly = HX0 + 1.95, 1.70
    make_box("SH_Crate", (lx, ly, 0.17), (0.40, 0.30, 0.34), BOARD)
    make_lathe("Kerosene_Lamp", (lx, ly, 0.34), [(0.0, 0.0), (0.07, 0.0), (0.075, 0.04), (0.06, 0.08), (0.02, 0.10),
                                                (0.045, 0.13), (0.05, 0.22), (0.03, 0.27), (0.0, 0.28)], (0.82, 0.74, 0.52, 0.8), segments=12)
    make_box("Kerosene_Lamp_Handle", (lx, ly, 0.625), (0.10, 0.01, 0.02), (0.30, 0.28, 0.24, 1.0))
    for k in range(5):
        make_box(f"SH_Book_{k}", (HX0 + 2.6 + (k % 2) * 0.05, 1.20, 0.016 + k * 0.032), (0.16, 0.24, 0.032),
                 ((0.30, 0.30, 0.40, 1.0), (0.52, 0.30, 0.22, 1.0))[k % 2])
    make_box("SH_Paint_Cans", (HX1 - 0.40, 3.10, 0.10), (0.30, 0.20, 0.20), (0.50, 0.42, 0.30, 1.0))
    # outside the gone window: the trees in the dark
    make_view("SH_View_E", "E", HX1, 1.8, kind="back", ground_z=0.0, seed=33)


def main():
    clear_scene()
    build_bedroom()
    build_second_house()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/small_wood_ranch.glb"))
    print(f"\n[build_small_wood_ranch] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
