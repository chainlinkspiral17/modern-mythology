"""Faust's studio apartment — vol1's most-played interior (the 4am
act-one waking, the lullaby, the dream-states, the painting day).

One room, two wired vantages. Canon: a painter's studio flat — the
bed where the lucid dreams happen, the easel with a working canvas,
a wall clock (it is always almost 4am somewhere), books, a
kitchenette he barely uses.

Hero features: bed with deep-red blanket in the NW corner under the
headboard wall, nightstand + shaded lamp, the E-wall window with
half-drawn curtains, the easel + canvas + paint table mid-room SE,
a W-wall bookcase with hand-shelved spines, writing desk + chair,
kitchenette in the SW corner, center rug, bare ceiling bulb, wall
clock on the N wall.

Coordinate frame: Blender Z-up. y=0 is the door (south) wall; +Y
runs back into the room; walls at x=±3.0, back wall y=5.0, ceiling
2.7. glTF export remaps to Godot (x, z, -y).

Vantages wired in Background3D.CAMERA_PRESETS:
  faust_bedroom       — mid-room looking NW at the bed corner.
  faust_apartment_day — inside the door, the whole studio in one
                        wide: bed far left, window right, easel
                        frame-right.
"""
import math
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling

ROOM_W = 6.0      # x ∈ [-3, 3]
ROOM_D = 5.0      # y ∈ [0, 5]
CEIL = 2.7

COL_WALL = (0.50, 0.48, 0.42, 1.0)      # warm gray-green plaster
COL_BASE = (0.28, 0.24, 0.18, 1.0)
COL_FLOOR = (0.36, 0.26, 0.16, 1.0)
COL_SEAM = (0.26, 0.18, 0.11, 1.0)
COL_CEIL = (0.46, 0.44, 0.40, 1.0)
COL_BEDFRAME = (0.28, 0.20, 0.14, 1.0)
COL_MATTRESS = (0.72, 0.68, 0.58, 1.0)
COL_BLANKET = (0.42, 0.18, 0.16, 1.0)   # deep red
COL_PILLOW = (0.80, 0.76, 0.66, 1.0)
COL_WOOD = (0.32, 0.23, 0.15, 1.0)
COL_WOOD_LT = (0.40, 0.30, 0.19, 1.0)
COL_LAMP = (1.00, 0.86, 0.55, 1.0)      # warm bulb — blooms via glow
COL_SHADE = (0.62, 0.48, 0.30, 1.0)
COL_GLASS = (0.40, 0.48, 0.58, 0.6)
COL_FRAME = (0.20, 0.18, 0.15, 1.0)
COL_CURTAIN = (0.55, 0.45, 0.30, 1.0)
COL_CANVAS = (0.84, 0.80, 0.70, 1.0)
COL_RUG = (0.30, 0.26, 0.34, 1.0)
COL_RUG_EDGE = (0.20, 0.17, 0.24, 1.0)
COL_CLOCK = (0.86, 0.82, 0.72, 1.0)
COL_STEEL = (0.55, 0.57, 0.58, 1.0)
COL_COUNTER = (0.44, 0.42, 0.38, 1.0)

SPINES = [
    (0.48, 0.20, 0.16, 1.0), (0.22, 0.30, 0.24, 1.0), (0.60, 0.52, 0.36, 1.0),
    (0.24, 0.22, 0.34, 1.0), (0.55, 0.38, 0.20, 1.0), (0.42, 0.44, 0.46, 1.0),
    (0.30, 0.14, 0.12, 1.0), (0.18, 0.24, 0.30, 1.0),
]


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=pal, baseboard_face_sign=+1)
    make_wall("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=pal, baseboard_face_sign=-1)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=pal, baseboard_face_sign=-1)
    make_wall("Wall_S", (0.0, 0.0, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=pal, baseboard_face_sign=+1)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, with_grid=False, with_stains=False,
                 palette={"tile": COL_CEIL})
    # Door in the S wall, east side, ajar
    make_box("Door", (2.2, 0.10, 1.05), (0.90, 0.06, 2.10), COL_WOOD)
    make_cyl("Door_Knob", (1.85, 0.15, 1.02), 0.035, 0.04, COL_STEEL, segments=8, axis='Y')
    # Center rug
    make_box("Rug", (0.1, 2.5, 0.008), (2.6, 2.2, 0.012), COL_RUG)
    make_box("Rug_Edge_S", (0.1, 1.45, 0.012), (2.6, 0.10, 0.008), COL_RUG_EDGE)
    make_box("Rug_Edge_N", (0.1, 3.55, 0.012), (2.6, 0.10, 0.008), COL_RUG_EDGE)


def build_bed():
    """NW corner: x ∈ [-2.6, -1.2], y ∈ [3.4, 5.0], headboard on N."""
    make_box("Bed_Frame", (-1.9, 4.2, 0.22), (1.5, 1.7, 0.28), COL_BEDFRAME)
    make_box("Bed_Headboard", (-1.9, 4.93, 0.75), (1.5, 0.08, 0.9), COL_BEDFRAME)
    make_box("Bed_Mattress", (-1.9, 4.2, 0.44), (1.4, 1.6, 0.18), COL_MATTRESS)
    # Blanket over the lower two-thirds, thrown back at one corner
    make_box("Bed_Blanket", (-1.9, 3.95, 0.55), (1.44, 1.05, 0.08), COL_BLANKET)
    make_box("Bed_Blanket_Fold", (-1.45, 3.5, 0.60), (0.5, 0.35, 0.06), COL_MATTRESS)
    make_box("Bed_Pillow", (-1.9, 4.72, 0.58), (1.0, 0.42, 0.12), COL_PILLOW)
    # Nightstand + shaded lamp, east of the bed
    make_box("Nightstand", (-0.85, 4.65, 0.30), (0.5, 0.45, 0.60), COL_WOOD)
    make_cyl("NLamp_Post", (-0.85, 4.65, 0.78), 0.02, 0.32, COL_STEEL, segments=6)
    make_cyl("NLamp_Shade", (-0.85, 4.65, 0.98), 0.13, 0.16, COL_SHADE, segments=10)
    make_cyl("NLamp_Bulb", (-0.85, 4.65, 0.90), 0.05, 0.06, COL_LAMP, segments=8)
    # A dream journal, the alarm clock ("wakes at four a.m. with the
    # sound of an alarm"), and the glass of water ("a tug of water")
    make_box("Journal", (-0.72, 4.52, 0.63), (0.20, 0.15, 0.035), (0.24, 0.22, 0.34, 1.0))
    make_box("Alarm_Clock", (-0.98, 4.74, 0.68), (0.16, 0.10, 0.14), (0.20, 0.18, 0.16, 1.0))
    make_box("Alarm_Face", (-0.98, 4.68, 0.68), (0.12, 0.02, 0.09), (0.72, 0.24, 0.20, 1.0))
    make_cyl("Water_Glass", (-0.70, 4.74, 0.66), 0.035, 0.11, COL_GLASS, segments=8)


def build_window():
    """E wall, centered y=2.4: frame + cool glass + half-drawn
    curtains on a rod."""
    wx = ROOM_W / 2.0 - 0.06
    make_box("Win_Frame", (wx, 2.4, 1.65), (0.08, 1.75, 1.65), COL_FRAME)
    make_box("Win_Glass", (wx - 0.01, 2.4, 1.65), (0.05, 1.55, 1.45), COL_GLASS)
    make_box("Win_Mullion_V", (wx - 0.03, 2.4, 1.65), (0.05, 0.06, 1.45), COL_FRAME)
    make_box("Win_Mullion_H", (wx - 0.03, 2.4, 1.65), (0.05, 1.55, 0.06), COL_FRAME)
    make_box("Win_Sill", (wx - 0.10, 2.4, 0.80), (0.22, 1.95, 0.06), COL_FRAME)
    make_cyl("Curtain_Rod", (wx - 0.14, 2.4, 2.56), 0.02, 2.2, COL_STEEL,
             segments=6, axis='Y')
    # Curtains bunched at both ends (half-drawn)
    make_box("Curtain_S", (wx - 0.16, 1.62, 1.62), (0.14, 0.42, 1.85), COL_CURTAIN)
    make_box("Curtain_N", (wx - 0.16, 3.18, 1.62), (0.14, 0.42, 1.85), COL_CURTAIN)


def build_easel():
    """Mid-room SE: easel legs, ledge, working canvas with paint
    passes; paint table beside it with tubes and a jar."""
    ex, ey = 1.4, 2.2
    for i, (lx, ly) in enumerate(((ex - 0.32, ey - 0.05), (ex + 0.32, ey - 0.05),
                                  (ex, ey + 0.38))):
        make_cyl(f"Easel_Leg_{i}", (lx, ly, 0.78), 0.025, 1.56, COL_WOOD_LT, segments=6)
    make_box("Easel_Ledge", (ex, ey - 0.10, 0.78), (0.72, 0.09, 0.06), COL_WOOD_LT)
    make_box("Easel_Canvas", (ex, ey - 0.06, 1.32), (0.66, 0.03, 0.92), COL_CANVAS)
    # The painting in progress — canon: "three elementals — water on
    # the left, fire on the right, air in the middle"
    make_box("Canvas_Water", (ex - 0.20, ey - 0.075, 1.32), (0.15, 0.012, 0.60), (0.28, 0.40, 0.56, 1.0))
    make_box("Canvas_Air", (ex, ey - 0.075, 1.38), (0.14, 0.012, 0.66), (0.80, 0.80, 0.74, 1.0))
    make_box("Canvas_Fire", (ex + 0.20, ey - 0.075, 1.30), (0.15, 0.012, 0.58), (0.72, 0.30, 0.16, 1.0))
    # Paint table
    tx, ty = 2.3, 1.4
    make_box("PaintTable_Top", (tx, ty, 0.66), (0.7, 0.5, 0.05), COL_WOOD)
    for lx, ly in ((tx - 0.28, ty - 0.18), (tx + 0.28, ty - 0.18),
                   (tx - 0.28, ty + 0.18), (tx + 0.28, ty + 0.18)):
        make_box(f"PaintTable_Leg_{lx:.2f}_{ly:.2f}", (lx, ly, 0.32), (0.05, 0.05, 0.64), COL_WOOD)
    for i, tube_col in enumerate(((0.62, 0.20, 0.16, 1.0), (0.24, 0.32, 0.50, 1.0),
                                  (0.60, 0.52, 0.24, 1.0), (0.86, 0.84, 0.78, 1.0))):
        make_box(f"Paint_Tube_{i}", (tx - 0.24 + i * 0.14, ty + 0.10, 0.71),
                 (0.10, 0.04, 0.04), tube_col)
    make_cyl("Brush_Jar", (tx + 0.22, ty - 0.12, 0.75), 0.055, 0.14, COL_GLASS, segments=8)


def build_bookcase_desk():
    """W wall: a two-bay case with hand-shelved spines; writing desk
    + chair south of it."""
    wx = -ROOM_W / 2.0 + 0.20
    make_box("Case_Back", (wx + 0.08, 2.8, 1.05), (0.04, 1.9, 2.1), COL_WOOD)
    for yy in (1.85, 2.8, 3.75):
        make_box(f"Case_V_{yy:.2f}", (wx, yy, 1.05), (0.30, 0.05, 2.1), COL_WOOD)
    make_box("Case_Top", (wx, 2.8, 2.12), (0.32, 1.95, 0.05), COL_WOOD)
    for zi, z in enumerate((0.25, 0.75, 1.25, 1.75)):
        make_box(f"Case_S{zi}", (wx, 2.8, z), (0.28, 1.85, 0.035), COL_WOOD_LT)
        n = 14
        for i in range(n):
            if (i + zi) % 6 == 4:
                continue
            k = (i * 5 + zi * 3) % len(SPINES)
            h = 0.20 + 0.05 * ((i * 3 + zi) % 4)
            make_box(f"Book_{zi}_{i}", (wx, 1.92 + i * 0.125, z + 0.02 + h / 2.0),
                     (0.16, 0.10, h), SPINES[k])
    # Writing desk + chair — EAST wall, north of the window. It was
    # on the W wall at y 0.85, which is the same stretch as the
    # kitchenette: the desk stood INSIDE the kitchen counter.
    dx, dy = 2.55, 4.15
    make_box("Desk_Top", (dx, dy, 0.74), (0.55, 1.0, 0.05), COL_WOOD_LT)
    for ly in (dy - 0.43, dy + 0.43):
        make_box(f"Desk_Leg_{ly:.2f}", (dx - 0.21, ly, 0.37), (0.05, 0.05, 0.74), COL_WOOD)
        make_box(f"Desk_Leg_i_{ly:.2f}", (dx + 0.21, ly, 0.37), (0.05, 0.05, 0.74), COL_WOOD)
    make_box("Desk_Papers", (dx, dy, 0.775), (0.32, 0.42, 0.01), COL_CANVAS)
    make_cyl("Chair_Seat", (2.0, dy, 0.46), 0.19, 0.05, COL_WOOD_LT, segments=10)
    for li in range(3):
        ang = li * 2.09
        make_cyl(f"Chair_Leg_{li}", (2.0 + 0.13 * math.cos(ang),
                 dy + 0.13 * math.sin(ang), 0.22), 0.018, 0.44, COL_WOOD, segments=5)


def build_kitchenette():
    """SW corner: short counter run, sink, cupboard, kettle — and
    the MIRROR CABINET above the sink (canon: "Faust looks in the
    mirror… He OPENS the mirror to get his vitamins")."""
    make_box("Kit_Counter", (-2.55, 0.75, 0.45), (0.85, 1.3, 0.90), COL_COUNTER)
    make_box("Kit_Top", (-2.55, 0.75, 0.92), (0.90, 1.35, 0.05), COL_STEEL)
    make_box("Kit_Sink", (-2.55, 1.05, 0.93), (0.45, 0.40, 0.06), (0.40, 0.42, 0.44, 1.0))
    make_cyl("Kit_Faucet", (-2.78, 1.05, 1.05), 0.02, 0.22, COL_STEEL, segments=6)
    # Cupboard pulled south + narrowed — at y 0.55 x 0.9 wide it ran
    # through the mirror cabinet's corner.
    make_box("Kit_Cupboard", (-2.72, 0.40, 1.85), (0.5, 0.7, 0.6), COL_WOOD)
    make_cyl("Kettle", (-2.45, 0.35, 1.02), 0.10, 0.18, COL_STEEL, segments=10)
    # The mirror cabinet over the sink, W wall — door hinged, ajar
    make_box("Mirror_Cabinet", (-2.90, 1.05, 1.62), (0.10, 0.50, 0.65), COL_WOOD)
    make_box("Mirror_Door", (-2.83, 0.94, 1.62), (0.03, 0.42, 0.58), (0.68, 0.74, 0.78, 1.0))
    make_cyl("Vitamin_Bottle", (-2.86, 1.18, 1.37), 0.022, 0.08,
             (0.66, 0.52, 0.24, 1.0), segments=8)
    make_cyl("Vitamin_Bottle_Cap", (-2.86, 1.18, 1.42), 0.024, 0.02,
             (0.92, 0.92, 0.90, 1.0), segments=8)


def build_bicycle():
    """Faust bicycles to work — his bike leans on the S wall by the
    door: two wheels, frame bars, seat, handlebars."""
    bx, by = 1.2, 0.28
    for wx in (bx - 0.52, bx + 0.52):
        make_cyl(f"Bike_Wheel_{wx:.2f}", (wx, by, 0.34), 0.33, 0.04, COL_FRAME,
                 segments=14, axis='Y')
        make_cyl(f"Bike_Hub_{wx:.2f}", (wx, by, 0.34), 0.05, 0.06, COL_STEEL,
                 segments=8, axis='Y')
    make_box("Bike_Bar_Top", (bx, by, 0.62), (0.72, 0.03, 0.04), (0.46, 0.20, 0.16, 1.0))
    make_box("Bike_Bar_Down", (bx - 0.12, by, 0.48), (0.55, 0.03, 0.04), (0.46, 0.20, 0.16, 1.0))
    make_box("Bike_Seat", (bx - 0.30, by, 0.78), (0.16, 0.06, 0.05), COL_FRAME)
    make_box("Bike_Post", (0.90, by, 0.70), (0.03, 0.03, 0.14), COL_STEEL)
    make_box("Bike_Handlebar", (bx + 0.42, by, 0.82), (0.05, 0.30, 0.04), COL_STEEL)
    make_box("Bike_Stem", (bx + 0.44, by, 0.72), (0.03, 0.03, 0.18), COL_STEEL)


def build_fixtures():
    # Bare ceiling bulb on a cord, room center
    make_box("Bulb_Cord", (0.0, 2.5, CEIL - 0.14), (0.02, 0.02, 0.28), COL_FRAME)
    make_cyl("Bulb", (0.0, 2.5, CEIL - 0.32), 0.055, 0.10, COL_LAMP, segments=8)
    # Wall clock, N wall — the 4am prop
    make_cyl("Clock_Face", (0.8, ROOM_D - 0.06, 2.05), 0.17, 0.05, COL_CLOCK,
             segments=14, axis='Y')
    make_box("Clock_Hand_H", (0.76, ROOM_D - 0.10, 2.08), (0.09, 0.015, 0.02), COL_FRAME)
    make_box("Clock_Hand_M", (0.8, ROOM_D - 0.10, 2.12), (0.02, 0.015, 0.13), COL_FRAME)
    # Canvases leaned against the S wall, faces to the plaster
    for i, (cx, cw, ch) in enumerate(((0.4, 0.6, 0.85), (-0.35, 0.5, 0.7))):
        make_box(f"Leaned_Canvas_{i}", (cx, 0.16, ch / 2.0 + 0.02), (cw, 0.05, ch), COL_CANVAS)


def main():
    clear_scene()
    build_shell()
    build_bed()
    build_window()
    build_easel()
    build_bookcase_desk()
    build_kitchenette()
    build_bicycle()
    build_fixtures()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/faust_apartment.glb"))
    print(f"\n[build_faust_apartment] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
