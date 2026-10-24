"""Wagner's home — vol1 ch2, after the skatepark.

DRAFT 2 (2026-10-10). Draft 1 was a 6 x 5 m "lived-in family front room"
— a beige sofa, a TV, framed pictures — with the record player tucked in
a corner. The prose:

  "INT. WAGNER'S HOME — DAY. Wagner puts up his skateboard, goes to the
  record player, and starts some metal. — This here is the shit. — What
  is this I'm hearing? — Burzum. Norwegian Black Metal ... — We need to
  get a good crew. Take the longboat out tonight ... They make haste to
  their ride of choice — JD, a beat-up piece of shit."

So it is a skater-metalhead's rented bungalow, the front room built around
the stereo, 7.2 x 6.0 m under a 2.6 m ceiling, opening onto the kitchen
and the hall:
  · THE STEREO WALL (W): the turntable on its credenza with the receiver,
    the floor speakers either side, the milk crates of LPs, a black
    sleeve leaning out, the posters over it.
  · BY THE DOOR: the wall rack where he "puts up" his skateboard (two on
    the hooks, his leaning under them), the shoes on the mat.
  · The thrift-store sofa on the E wall, the coffee table (cans, a skate
    magazine, the remote), the rug; the TV on its low stand; a guitar on
    its stand beside a practice amp; the floor lamp.
  · Through the cased opening, the kitchen: the counter with a pizza box,
    the fridge, the sink under its window. Through the other, the short
    hall to his door.
  · Out the front window: the yard, the driveway — and JD on it, the
    beat-up sedan, faded maroon — and the street of small houses.

Coordinate frame: Blender Z-up; y=0 is the front (S) wall, +Y runs back to
the kitchen; walls x=+-3.6, back wall y=6.0, the kitchen to y=9.4.
glTF export remaps to Godot (x, z, -y).

DRAFT 3 (2026-10-18): THE FRONT. vol 1 ch5 sees the house from outside
twice on one day: "Wagner is sitting on the porch, reading and smoking."
(the morning) and "The three approach the steps." / "Through the open door,
the album on the turn-table plays on to an empty room." (that afternoon).
So the house has its outside now: lap siding, a gable roof, a porch across
the front W of the window with a seat, a crate, the book and the ashtray,
two steps down to the walk; the front door is SHUT in the room's own view
and the morning, and OPEN for the proposition (`__wagner_house_steps`), so
the walk looks through it to the stereo. Jacob's house ("Jacob is waiting
for them outside, smoking") is its own lot on another block (x 80), plain:
ch2 calls it an apartment, ch5 a house (the author's call).

Draft 4 targets: the band posters' imagery (the prose names Burzum —
the posters should read as black-metal logos without copying any); the
afternoon going to evening for "Take the longboat out tonight"; the
street's other side as built lots, not the view kit; Jacob's house past
plain once the apartment/house knot is answered.
"""
import math
import os
import random
import sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_lathe, make_rot_box, make_gable, make_blob, make_chamfer_box, export_glb
from _props.structure import make_floor, make_wall, make_wall_with_openings, make_ceiling, make_window
from _props.views import make_view
from _props.vehicles import make_car

X0, X1 = -3.6, 3.6
Y0, Y1 = 0.0, 6.0
CEIL = 2.6
KY1 = 9.4                       # the kitchen's back wall
KX0 = 0.2                       # the kitchen's W wall
HALL_X = -2.4                   # the hall opening's centre

COL_WALL = (0.70, 0.68, 0.60, 1.0)      # landlord off-white, gone grey
COL_BASE = (0.40, 0.34, 0.26, 1.0)
COL_FLOOR = (0.52, 0.38, 0.26, 1.0)     # worn oak
COL_SEAM = (0.38, 0.27, 0.18, 1.0)
COL_TRIM = (0.82, 0.80, 0.74, 1.0)
COL_DARK = (0.10, 0.10, 0.11, 1.0)
COL_WOOD = (0.52, 0.36, 0.22, 1.0)
COL_SOFA = (0.26, 0.24, 0.22, 1.0)      # a dark thrift-store sofa
COL_SOFA_CUSH = (0.32, 0.30, 0.27, 1.0)
COL_POSTER = (0.06, 0.06, 0.07, 1.0)
COL_PAPER = (0.92, 0.90, 0.84, 1.0)
COL_GLASS = (0.78, 0.84, 0.86, 0.25)


def build_shell():
    make_floor("Floor", (0.0, (Y0 + Y1) / 2.0, 0.0), size_x=X1 - X0 + 0.4, size_y=Y1 - Y0 + 0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM}, style="plank")
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    make_wall("Wall_W", (X0, (Y0 + Y1) / 2.0, 0), length=Y1 - Y0 + 0.4, height=CEIL, axis='Y', palette=pal, baseboard_face_sign=+1)
    make_wall("Wall_E", (X1, (Y0 + KY1) / 2.0, 0), length=KY1 - Y0 + 0.4, height=CEIL, axis='Y', palette=pal, baseboard_face_sign=-1)
    # S: the front door and the front window on the driveway
    make_wall_with_openings("Wall_S", (0.0, Y0, 0), length=X1 - X0 + 0.4, height=CEIL, axis='X', palette=pal,
                            baseboard_face_sign=+1, openings=[(-2.5, 1.025, 0.95, 2.05), (1.2, 1.45, 2.2, 1.40)])
    # N: the hall opening and the kitchen's cased opening
    make_wall_with_openings("Wall_N", (0.0, Y1, 0), length=X1 - X0 + 0.4, height=CEIL, axis='X', palette=pal,
                            baseboard_face_sign=-1, openings=[(HALL_X, 1.025, 0.90, 2.05), (1.7, 1.05, 1.60, 2.10)])
    make_ceiling("Ceil", (0.0, (Y0 + KY1) / 2.0, CEIL), size_x=X1 - X0 + 0.4, size_y=KY1 - Y0 + 0.4,
                 with_grid=False, with_stains=True, palette={"tile": (0.86, 0.85, 0.80, 1.0)})
    # the front window: frame, glass, the curtains pushed open
    make_window("Win_S", (1.2, Y0 + 0.10, 1.45), width=2.2, height=1.40, room_dir=+1, see_through=True,
                palette={"frame": COL_TRIM}, cross_mullion=True)
    make_box("Win_S_Glass", (1.2, Y0 + 0.02, 1.45), (2.2, 0.01, 1.40), COL_GLASS)
    make_box("Win_S_Sill", (1.2, Y0 + 0.17, 0.74), (2.4, 0.14, 0.03), COL_TRIM)
    make_cyl("Curtain_Rod", (1.2, Y0 + 0.16, 2.30), 0.015, 2.80, COL_DARK, segments=6, axis='X')
    for k, bx in enumerate((-0.15, 2.55)):
        make_box(f"Curtain_Rod_Bracket_{k}", (bx, Y0 + 0.135, 2.30), (0.03, 0.07, 0.03), COL_DARK)   # rod to the wall face
    for k, (cx, w) in enumerate(((-0.10, 0.36), (2.50, 0.36))):
        make_box(f"Curtain_{k}", (cx, Y0 + 0.19, 1.47), (w, 0.08, 1.64), (0.20, 0.16, 0.22, 1.0))
        make_box(f"Curtain_{k}_Rod_Ring", (cx, Y0 + 0.16, 2.29), (0.06, 0.04, 0.04), COL_DARK)
    # the front door, shut, and its deadbolt; the hall and kitchen casings
    # shut in the room's view and the morning; open for the proposition
    SHUT = "__wagner_home__wagner_porch_morning"
    make_box("Front_Door" + SHUT, (-2.5, Y0, 1.02), (0.92, 0.05, 2.04), (0.40, 0.18, 0.14, 1.0))
    make_cyl("Front_Door_Knob" + SHUT, (-2.15, Y0 + 0.06, 1.00), 0.028, 0.05, (0.72, 0.64, 0.40, 1.0), segments=8, axis='Y')
    make_box("Front_Door_Deadbolt" + SHUT, (-2.15, Y0 + 0.04, 1.18), (0.05, 0.02, 0.05), (0.72, 0.64, 0.40, 1.0))
    make_box("Front_Door_Open__wagner_house_steps", (-2.5 + 0.44, Y0 + 0.10 + 0.44, 1.02), (0.05, 0.88, 2.04), (0.40, 0.18, 0.14, 1.0))
    for nm, cx, w in (("Hall", HALL_X, 0.90), ("Kitchen", 1.7, 1.60)):
        make_box(f"{nm}_Casing_Head", (cx, Y1 - 0.11, 2.12), (w + 0.16, 0.02, 0.10), COL_TRIM)
        for s in (-1, 1):
            make_box(f"{nm}_Casing_{s:+d}", (cx + s * (w / 2.0 + 0.04), Y1 - 0.11, 1.03), (0.08, 0.02, 2.06), COL_TRIM)
    make_cyl("Ceiling_Dome", (0.3, 3.0, CEIL - 0.04), 0.18, 0.08, (0.94, 0.92, 0.84, 1.0), segments=14)


def build_hall_and_kitchen():
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    # the hall: a stub to his door
    make_box("Hall_Floor", (HALL_X, Y1 + 0.9, -0.05), (1.4, 1.8, 0.10), COL_FLOOR)
    for s in (-1, 1):
        make_wall(f"Hall_Wall_{s:+d}", (HALL_X + s * 0.65, Y1 + 0.95, 0), length=1.70, height=CEIL, axis='Y', palette=pal,
                  baseboard_face_sign=-s)
    make_wall("Hall_Wall_End", (HALL_X, Y1 + 1.85, 0), length=1.50, height=CEIL, axis='X', palette=pal, baseboard_face_sign=-1)
    make_box("Bedroom_Door", (HALL_X, Y1 + 1.73, 1.02), (0.80, 0.04, 2.04), (0.62, 0.54, 0.42, 1.0))
    make_box("Bedroom_Door_Sticker", (HALL_X + 0.10, Y1 + 1.708, 1.45), (0.18, 0.002, 0.24), COL_POSTER)
    make_cyl("Bedroom_Door_Knob", (HALL_X + 0.30, Y1 + 1.69, 0.98), 0.025, 0.05, (0.72, 0.64, 0.40, 1.0), segments=8, axis='Y')
    # the kitchen through the cased opening
    make_box("Kitchen_Floor", ((KX0 + X1) / 2.0, (Y1 + KY1) / 2.0, -0.05), (X1 - KX0 + 0.2, KY1 - Y1 + 0.2, 0.10), (0.66, 0.62, 0.52, 1.0))
    make_wall("Kitchen_Wall_W", (KX0, (Y1 + KY1) / 2.0, 0), length=KY1 - Y1 + 0.2, height=CEIL, axis='Y', palette=pal, baseboard_face_sign=+1)
    make_wall_with_openings("Kitchen_Wall_N", ((KX0 + X1) / 2.0, KY1, 0), length=X1 - KX0 + 0.4, height=CEIL, axis='X', palette=pal,
                            baseboard_face_sign=-1, openings=[(1.6, 1.55, 1.0, 0.90)])
    face = KY1 - 0.10
    make_box("Kitchen_Counter", (1.30, face - 0.30, 0.44), (2.00, 0.60, 0.88), (0.56, 0.46, 0.34, 1.0))
    make_box("Kitchen_Counter_Top", (1.30, face - 0.31, 0.90), (2.04, 0.64, 0.04), (0.72, 0.70, 0.64, 1.0))
    make_box("Kitchen_Sink", (1.60, face - 0.31, 0.915), (0.60, 0.42, 0.01), (0.66, 0.68, 0.70, 1.0))
    make_cyl("Kitchen_Faucet", (1.60, face - 0.08, 1.05), 0.012, 0.26, (0.70, 0.72, 0.74, 1.0), segments=6)
    make_window("Kitchen_Win", (1.6, face, 1.55), width=1.0, height=0.90, room_dir=-1, see_through=True, palette={"frame": COL_TRIM})
    make_box("Kitchen_Win_Glass", (1.6, KY1 - 0.02, 1.55), (1.0, 0.01, 0.90), COL_GLASS)
    make_box("Pizza_Box", (0.70, face - 0.32, 0.945), (0.42, 0.42, 0.05), (0.80, 0.70, 0.52, 1.0))
    for k in range(3):
        make_cyl(f"Kitchen_Can_{k}", (2.05 + k * 0.09, face - 0.40, 0.98), 0.033, 0.12, (0.70, 0.12, 0.10, 1.0), segments=8)
    make_box("Fridge", (X1 - 0.10 - 0.38, face - 0.40, 0.88), (0.74, 0.78, 1.76), (0.88, 0.88, 0.84, 1.0))
    make_box("Fridge_Handle", (X1 - 0.10 - 0.70, face - 0.80, 1.20), (0.03, 0.03, 0.40), (0.60, 0.60, 0.60, 1.0))
    make_box("Fridge_Flyer", (X1 - 0.10 - 0.40, face - 0.795, 1.40), (0.20, 0.002, 0.26), COL_PAPER)
    make_cyl("Kitchen_Dome", (1.9, 7.8, CEIL - 0.04), 0.15, 0.08, (0.94, 0.92, 0.84, 1.0), segments=12)


def build_stereo_wall():
    """W wall: the turntable, the receiver, the speakers, the crates of LPs, the posters."""
    face = X0 + 0.10
    cy = 3.0
    make_box("Stereo_Credenza", (face + 0.24, cy, 0.30), (0.48, 1.60, 0.60), COL_WOOD)
    make_box("Stereo_Credenza_Top", (face + 0.24, cy, 0.615), (0.50, 1.64, 0.03), COL_WOOD)
    t = 0.63
    make_box("Receiver", (face + 0.24, cy + 0.42, t + 0.07), (0.40, 0.44, 0.14), COL_DARK)
    make_box("Receiver_Dial", (face + 0.442, cy + 0.42, t + 0.08), (0.004, 0.30, 0.05), (0.86, 0.64, 0.28, 1.0))
    make_box("Turntable_Plinth", (face + 0.24, cy - 0.30, t + 0.05), (0.38, 0.46, 0.10), (0.72, 0.60, 0.44, 1.0))
    make_cyl("Turntable_Platter", (face + 0.24, cy - 0.33, t + 0.105), 0.15, 0.012, (0.74, 0.74, 0.76, 1.0), segments=20)
    make_cyl("Turntable_Record", (face + 0.24, cy - 0.33, t + 0.115), 0.148, 0.004, (0.04, 0.04, 0.05, 1.0), segments=20)
    make_cyl("Turntable_Record_Label", (face + 0.24, cy - 0.33, t + 0.1185), 0.045, 0.002, (0.90, 0.90, 0.88, 1.0), segments=12)
    make_rot_box("Turntable_Tonearm", (face + 0.30, cy - 0.20, t + 0.13), (0.03, 0.22, 0.012), (0.72, 0.72, 0.74, 1.0), yaw=0.35)
    make_cyl("Turntable_Tonearm_Post", (face + 0.38, cy - 0.12, t + 0.115), 0.015, 0.03, (0.72, 0.72, 0.74, 1.0), segments=8)
    # the sleeve he pulled it from, leaning on the credenza's front
    make_box("Record_Sleeve", (face + 0.486, cy - 0.10, 0.16), (0.012, 0.31, 0.31), COL_POSTER)   # standing on the floor against the credenza
    # the floor speakers either side
    for k, sy in enumerate((cy - 1.15, cy + 1.15)):
        make_box(f"Speaker_{k}", (face + 0.18, sy, 0.48), (0.34, 0.30, 0.96), COL_DARK)
        for d, (dz, r) in enumerate(((0.30, 0.10), (0.62, 0.06), (0.82, 0.03))):
            make_cyl(f"Speaker_{k}_Driver_{d}", (face + 0.352, sy, dz), r, 0.006, (0.24, 0.24, 0.26, 1.0), segments=12, axis='X')
    # the milk crates of LPs, two stacked
    for k in range(2):
        cz = 0.165 + k * 0.33
        make_box(f"Milk_Crate_{k}", (face + 0.20, 4.85, cz), (0.34, 0.34, 0.32), (0.12, 0.26, 0.56, 1.0))
        for r in range(9):
            make_box(f"Milk_Crate_{k}_LP_{r}", (face + 0.12 + r * 0.022, 4.85, cz + 0.06), (0.012, 0.31, 0.31),
                     (COL_POSTER, (0.40, 0.34, 0.30, 1.0), (0.60, 0.20, 0.16, 1.0))[(r + k) % 3])
    # the posters over the stereo: black sheets, white jagged logos
    rnd = random.Random(66)
    for k, (py, w, h) in enumerate(((1.75, 0.60, 0.88), (3.0, 0.90, 0.60), (4.25, 0.60, 0.88))):
        make_box(f"Poster_{k}", (X0 + 0.103, py, 1.75), (0.006, w, h), COL_POSTER)
        for m in range(6):
            make_box(f"Poster_{k}_Logo_{m}", (X0 + 0.107, py - w * 0.35 + m * w * 0.14, 1.75 + h * 0.28 + rnd.uniform(-0.04, 0.04)),
                     (0.002, w * 0.10, rnd.uniform(0.04, 0.12)), (0.88, 0.88, 0.86, 1.0))
        make_box(f"Poster_{k}_Image", (X0 + 0.107, py, 1.75 - h * 0.12), (0.002, w * 0.70, h * 0.40), (0.34, 0.34, 0.36, 1.0))


def build_door_corner():
    """The skateboard rack by the door — 'Wagner puts up his skateboard' — and the shoes."""
    face = X0 + 0.10
    for k, z in enumerate((1.25, 1.62)):
        for h in (-1, 1):
            make_box(f"Skate_Rack_Hook_{k}_{h:+d}", (face + 0.05, 0.85 + h * 0.30, z - 0.04), (0.10, 0.03, 0.03), COL_DARK)
        make_box(f"Skateboard_{k}_Deck", (face + 0.10, 0.85, z), (0.02, 0.80, 0.20), ((0.10, 0.10, 0.12, 1.0), (0.60, 0.20, 0.16, 1.0))[k])
        for w in (-1, 1):
            make_cyl(f"Skateboard_{k}_Wheel_{w:+d}", (face + 0.135, 0.85 + w * 0.28, z), 0.027, 0.05, (0.92, 0.88, 0.72, 1.0), segments=8, axis='X')
    # his board, just put up — leaning under the rack, tail on the floor
    make_rot_box("Skateboard_His_Deck", (face + 0.12, 0.85, 0.40), (0.04, 0.20, 0.80), (0.30, 0.42, 0.24, 1.0), roll=0.12)
    make_box("Shoe_Mat", (-2.5, 0.55, 0.005), (0.90, 0.50, 0.01), (0.30, 0.26, 0.20, 1.0))
    for k, (sx, sy, yaw) in enumerate(((-2.75, 0.45, 0.2), (-2.55, 0.60, -0.3), (-2.30, 0.48, 0.1))):
        make_rot_box(f"Shoe_{k}", (sx, sy, 0.055), (0.11, 0.28, 0.09), ((0.10, 0.10, 0.12, 1.0), (0.80, 0.78, 0.74, 1.0), (0.12, 0.12, 0.14, 1.0))[k], yaw=yaw)
    make_box("Coat_Hook", (-1.85, Y0 + 0.13, 1.70), (0.04, 0.06, 0.04), COL_DARK)
    make_box("Coat_Hoodie", (-1.85, Y0 + 0.17, 1.33), (0.40, 0.06, 0.70), (0.14, 0.14, 0.16, 1.0))


def build_living():
    # the sofa on the E wall, facing the stereo
    sx, sy = X1 - 0.10 - 0.45, 2.80
    make_box("Sofa_Base", (sx, sy, 0.21), (0.90, 2.10, 0.42), COL_SOFA)
    make_box("Sofa_Back", (sx + 0.34, sy, 0.62), (0.22, 2.10, 0.42), COL_SOFA)
    for e in (-1, 1):
        make_box(f"Sofa_Arm_{e:+d}", (sx - 0.02, sy + e * 0.97, 0.55), (0.84, 0.16, 0.26), COL_SOFA)
    for k in range(3):
        make_box(f"Sofa_SeatCush_{k}", (sx - 0.05, sy - 0.59 + k * 0.59, 0.47), (0.62, 0.58, 0.10), COL_SOFA_CUSH)
    make_rot_box("Sofa_Blanket", (sx - 0.05, sy + 0.55, 0.53), (0.60, 0.40, 0.02), (0.46, 0.20, 0.16, 1.0), yaw=0.2)
    # the rug and the coffee table with what's on it
    make_box("Rug", (0.40, 2.80, 0.005), (2.60, 2.00, 0.01), (0.30, 0.26, 0.30, 1.0))
    tx, ty = 0.90, 2.80
    make_box("Coffee_Table_Top", (tx, ty, 0.42), (0.60, 1.10, 0.04), COL_WOOD)
    for i, (lx, ly) in enumerate(((-0.26, -0.50), (0.26, -0.50), (-0.26, 0.50), (0.26, 0.50))):
        make_box(f"Coffee_Table_Leg_{i}", (tx + lx, ty + ly, 0.20), (0.04, 0.04, 0.40), COL_WOOD)
    for k, (cx, cy) in enumerate(((-0.10, -0.30), (0.12, -0.20), (0.05, 0.30))):
        make_cyl(f"Coffee_Table_Can_{k}", (tx + cx, ty + cy, 0.50), 0.033, 0.12, ((0.70, 0.12, 0.10, 1.0), (0.20, 0.30, 0.60, 1.0), (0.70, 0.12, 0.10, 1.0))[k], segments=8)
    make_rot_box("Skate_Magazine", (tx - 0.05, ty + 0.05, 0.445), (0.22, 0.29, 0.006), (0.86, 0.50, 0.20, 1.0), yaw=0.3)
    make_box("TV_Remote", (tx + 0.18, ty + 0.12, 0.447), (0.05, 0.17, 0.014), COL_DARK)
    # the TV on its low stand against the N wall
    make_box("TV_Stand", (-0.40, Y1 - 0.10 - 0.22, 0.24), (1.40, 0.44, 0.48), COL_DARK)
    make_box("TV_Panel", (-0.40, Y1 - 0.10 - 0.16, 0.86), (1.10, 0.05, 0.66), COL_DARK)
    make_box("TV_Panel_Screen", (-0.40, Y1 - 0.10 - 0.186, 0.86), (1.04, 0.002, 0.60), (0.08, 0.09, 0.10, 1.0))
    make_box("TV_Panel_Foot", (-0.40, Y1 - 0.10 - 0.16, 0.50), (0.30, 0.18, 0.04), COL_DARK)
    make_box("Game_Console", (-0.80, Y1 - 0.10 - 0.25, 0.51), (0.30, 0.25, 0.06), COL_DARK)
    # the guitar on its stand and the practice amp, in the SE corner by the window
    make_box("Practice_Amp", (X1 - 0.10 - 0.22, 0.55, 0.22), (0.40, 0.26, 0.44), COL_DARK)
    make_box("Practice_Amp_Grille", (X1 - 0.10 - 0.22, 0.679, 0.24), (0.34, 0.004, 0.30), (0.30, 0.30, 0.30, 1.0))
    make_box("Guitar_Stand", (2.55, 0.62, 0.08), (0.30, 0.30, 0.16), COL_DARK)
    make_rot_box("Guitar_Body", (2.55, 0.62, 0.40), (0.36, 0.08, 0.46), (0.06, 0.06, 0.07, 1.0), roll=-0.10)
    make_rot_box("Guitar_Neck", (2.58, 0.66, 0.92), (0.05, 0.03, 0.62), (0.30, 0.20, 0.14, 1.0), roll=-0.10)
    make_rot_box("Guitar_Headstock", (2.62, 0.69, 1.27), (0.08, 0.03, 0.16), (0.06, 0.06, 0.07, 1.0), roll=-0.10)
    # the floor lamp at the sofa's N end
    make_cyl("Floor_Lamp_Base", (X1 - 0.35, 4.25, 0.02), 0.14, 0.04, COL_DARK, segments=12)
    make_cyl("Floor_Lamp_Pole", (X1 - 0.35, 4.25, 0.76), 0.014, 1.44, COL_DARK, segments=6)
    make_cyl("Floor_Lamp_Shade", (X1 - 0.35, 4.25, 1.56), 0.18, 0.24, (0.86, 0.76, 0.56, 1.0), segments=12)
    make_cyl("Floor_Lamp_Bulb", (X1 - 0.35, 4.25, 1.50), 0.035, 0.06, (0.98, 0.88, 0.62, 1.0), segments=8)


SIDING = (0.62, 0.66, 0.62, 1.0); SIDING_LAP = (0.54, 0.58, 0.54, 1.0)
ROOF = (0.26, 0.24, 0.24, 1.0)
PORCH_WOOD = (0.50, 0.40, 0.30, 1.0)
OUT = "__wagner_porch_morning__wagner_house_steps__jacob_house_front"


def siding(prefix, along_axis, a0, a1, at, openings, top):
    """Lap siding strips that stop at every opening (along, cz, w, h)."""
    n, k = 13, 0
    for i in range(n):
        z0 = i * top / n
        z1 = z0 + top / n
        cuts = sorted((c - w / 2.0, c + w / 2.0) for c, cz, w, h in openings
                      if cz - h / 2.0 < z1 - 1e-3 and cz + h / 2.0 > z0 + 1e-3)
        spans, a = [], a0
        for ca, cb in cuts:
            if ca > a:
                spans.append((a, ca))
            a = max(a, cb)
        if a < a1:
            spans.append((a, a1))
        for u0, u1 in spans:
            if u1 - u0 < 0.02:
                continue
            col = (SIDING, SIDING_LAP)[i % 2]
            if along_axis == 'X':
                make_box(f"{prefix}_Stock_{k}", ((u0 + u1) / 2.0, at, (z0 + z1) / 2.0), (u1 - u0, 0.03, z1 - z0 - 0.006), col)
            else:
                make_box(f"{prefix}_Stock_{k}", (at, (u0 + u1) / 2.0, (z0 + z1) / 2.0), (0.03, u1 - u0, z1 - z0 - 0.006), col)
            k += 1


def build_front():
    """The house from outside: siding, the gable roof, the porch with its
    seat, the steps, the walk; the sky for the outside views."""
    # the siding stands just proud of the walls' ends (they run 0.2 past
    # the corners)
    siding("Siding_S", 'X', X0 - 0.23, X1 + 0.23, Y0 - 0.215, [(-2.5, 1.025, 0.95, 2.05), (1.2, 1.45, 2.2, 1.40)], CEIL)
    siding("Siding_W", 'Y', Y0 - 0.23, Y1 + 0.2, X0 - 0.215, [], CEIL)
    siding("Siding_E", 'Y', Y0 - 0.23, KY1 + 0.2, X1 + 0.215, [], CEIL)
    make_gable("House_Roof", (0.0, (Y0 + KY1) / 2.0, CEIL + 0.12 + 1.0), (X1 - X0 + 1.0, KY1 - Y0 + 1.0, 2.0), ROOF, ridge_axis='Y')
    # the porch across the front W of the window: deck, posts, its roof,
    # the rail at the W end, two steps down at the door
    px0, px1, py0, py1 = X0 - 0.15, 0.25, -2.5, Y0 - 0.23
    make_box("Porch_Slab_Deck", ((px0 + px1) / 2.0, (py0 + py1) / 2.0, 0.18), (px1 - px0, py1 - py0, 0.36), PORCH_WOOD)
    for k in range(9):
        make_box(f"Porch_Board_Seam_Stock_{k}", (px0 + 0.45 + k * 0.45, (py0 + py1) / 2.0, 0.362), (0.02, py1 - py0, 0.004),
                 (0.40, 0.32, 0.24, 1.0))
    for k, x in enumerate((px0 + 0.08, -1.55, px1 - 0.08)):
        make_box(f"Porch_Post_{k}", (x, py0 + 0.08, 0.36 + 1.12), (0.12, 0.12, 2.24), (0.84, 0.82, 0.76, 1.0))
    make_rot_box("Porch_Roof", ((px0 + px1) / 2.0, (py0 + py1) / 2.0 - 0.1, 2.66), (px1 - px0 + 0.3, py1 - py0 + 0.5, 0.10), ROOF, roll=-0.10)
    make_box("Porch_Rail_W", (px0 + 0.08, (py0 + py1) / 2.0, 0.36 + 0.86), (0.06, py1 - py0 - 0.2, 0.06), (0.84, 0.82, 0.76, 1.0))
    make_box("Porch_Rail_S_W", ((px0 + (-2.98)) / 2.0, py0 + 0.08, 0.36 + 0.86), (-2.98 - px0, 0.06, 0.06), (0.84, 0.82, 0.76, 1.0))
    make_box("Porch_Rail_S_E", ((-2.02 + px1) / 2.0, py0 + 0.08, 0.36 + 0.86), (px1 + 2.02, 0.06, 0.06), (0.84, 0.82, 0.76, 1.0))
    for k, (t, ty) in enumerate(((0.24, py0 - 0.20), (0.12, py0 - 0.60))):
        make_box(f"Porch_Step_{k}", (-2.5, ty, t / 2.0), (1.10, 0.40, t), PORCH_WOOD)
    # his seat: an old armchair on the porch, the crate beside it with the
    # ashtray and a mug; the book face down on the arm
    sx, sy = -3.0, -1.6                    # clear of the door's swing
    make_box("Porch_Armchair_Base", (sx, sy, 0.36 + 0.22), (0.80, 0.80, 0.44), (0.36, 0.30, 0.26, 1.0))
    make_box("Porch_Armchair_Back", (sx - 0.32, sy, 0.36 + 0.70), (0.16, 0.80, 0.56), (0.36, 0.30, 0.26, 1.0))
    for s_ in (-1, 1):
        make_box(f"Porch_Armchair_Arm_{s_:+d}", (sx, sy + s_ * 0.34, 0.36 + 0.54), (0.80, 0.12, 0.20), (0.36, 0.30, 0.26, 1.0))
    make_rot_box("Porch_Book_Face_Down", (sx + 0.1, sy + 0.34, 0.36 + 0.66), (0.20, 0.14, 0.03), (0.60, 0.20, 0.16, 1.0), yaw=0.3)
    make_box("Porch_Crate", (sx + 0.75, sy - 0.30, 0.36 + 0.18), (0.40, 0.32, 0.36), (0.62, 0.50, 0.32, 1.0))
    make_cyl("Porch_Ashtray", (sx + 0.70, sy - 0.32, 0.36 + 0.375), 0.07, 0.03, (0.40, 0.42, 0.44, 1.0), segments=10)
    make_cyl("Porch_Mug", (sx + 0.85, sy - 0.24, 0.36 + 0.41), 0.04, 0.10, (0.20, 0.30, 0.50, 1.0), segments=10)
    for k in range(3):
        make_blob(f"Cigarette_Smoke_Cloud_{k}__wagner_porch_morning", (sx + 0.68 + k * 0.05, sy - 0.30, 0.36 + 0.55 + k * 0.22),
                  0.05 + k * 0.03, (0.84, 0.84, 0.84, 1.0), noise=0.3, seed=60 + k)
    # the walk from the steps to the sidewalk, the path to the drive
    make_box("Front_Walk", (-2.5, -6.0, -0.001), (1.0, 5.4, 0.008), (0.62, 0.60, 0.56, 1.0))
    make_box("Walk_To_Drive", (-0.95, -3.5, -0.001), (2.1, 0.8, 0.008), (0.62, 0.60, 0.56, 1.0))
    # the sky for the outside views (the room's own env is warm and dark)
    for tag, col in (("__wagner_porch_morning", (0.76, 0.82, 0.90, 1.0)), ("__wagner_house_steps", (0.70, 0.78, 0.88, 1.0)),
                     ("__jacob_house_front", (0.72, 0.80, 0.90, 1.0))):
        make_box("Sky_S" + tag, (0.0, -150.0, 40.0), (400.0, 0.2, 160.0), col)
        make_box("Sky_W" + tag, (-150.0, 0.0, 40.0), (0.2, 400.0, 160.0), col)
        make_box("Sky_E" + tag, (150.0, 0.0, 40.0), (0.2, 400.0, 160.0), col)
        make_box("Sky_N" + tag, (0.0, 150.0, 40.0), (400.0, 0.2, 160.0), col)


def build_jacob_house():
    """Jacob's: another block (x 80), a plain small house, a walk and a
    stoop; Jacob waits outside (he is the sprite)."""
    jx = 80.0
    make_view("Jacob_View_S", "S", 0.0, jx, kind="front", ground_z=0.0, seed=11)
    make_box("Jacob_House_Body", (jx, 4.0, 1.4), (8.0, 8.0, 2.8), (0.76, 0.70, 0.60, 1.0))
    make_gable("Jacob_House_Roof", (jx, 4.0, 2.8 + 0.9), (8.8, 8.8, 1.8), ROOF, ridge_axis='X')
    make_box("Jacob_Front_Door", (jx - 1.2, -0.02, 1.0), (0.90, 0.04, 2.0), (0.30, 0.34, 0.40, 1.0))
    for k, x in enumerate((jx + 1.4, jx - 3.0)):
        make_box(f"Jacob_Window_Pane_{k}", (x, -0.02, 1.5), (1.2, 0.03, 1.1), (0.30, 0.34, 0.38, 1.0))
        for s_ in (-1, 1):
            make_box(f"Jacob_Window_Frame_Jamb_{k}_{s_:+d}", (x + s_ * 0.63, -0.03, 1.5), (0.06, 0.05, 1.2), (0.88, 0.86, 0.80, 1.0))
    make_box("Jacob_Porch_Slab_Stoop", (jx - 1.2, -0.6, 0.09), (1.4, 1.2, 0.18), (0.60, 0.58, 0.54, 1.0))
    make_box("Jacob_Lot_Ground", (jx, 4.0, -0.025), (10.0, 8.6, 0.05), (0.30, 0.36, 0.22, 1.0))
    make_box("Jacob_Walk", (jx - 1.2, -5.0, -0.001), (1.0, 7.6, 0.008), (0.62, 0.60, 0.56, 1.0))
    make_box("Jacob_Trash_Can", (jx + 3.4, -0.6, 0.45), (0.56, 0.56, 0.90), (0.30, 0.34, 0.30, 1.0))


def build_outside():
    """The yard, the driveway and JD on it; the street of small houses."""
    make_view("View_S", "S", Y0, 0.0, kind="front", ground_z=0.0, seed=27)
    make_box("Driveway", (1.5, -4.5, -0.001), (2.8, 9.0, 0.008), (0.62, 0.60, 0.56, 1.0))
    build_front()
    build_jacob_house()
    # JD: "a beat-up piece of shit" — a faded maroon sedan, nose to the house
    make_car("JD", 1.5, -4.6, 4.70, (0.40, 0.18, 0.16, 1.0), along="Y")
    make_box("JD_Primer_Patch", (1.5 - 0.885, -4.0, 0.62), (0.006, 0.80, 0.30), (0.56, 0.56, 0.54, 1.0))


def main():
    clear_scene()
    build_shell()
    build_hall_and_kitchen()
    build_stereo_wall()
    build_door_corner()
    build_living()
    build_outside()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/wagner_home.glb"))
    print(f"\n[build_wagner_home] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
