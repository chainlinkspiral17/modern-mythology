"""The Wagner home — vol1 ch2's living room (the visit after the
skatepark). A lived-in family front room, early evening.

Hero features: the three-seat sofa with throw cushions against the
W wall, the TV on its console opposite, coffee table between them
with mugs and a magazine, an armchair, the N-wall window with
curtains, a bookshelf, floor lamp, framed pictures, and a braided
rug tying it together.

Coordinate frame: Blender Z-up. y=0 is the entry (south) wall; +Y
runs back into the room; walls at x=±3.0, back wall y=5.0, ceiling
2.6. glTF export remaps to Godot (x, z, -y).

Vantage wired in Background3D.CAMERA_PRESETS:
  wagner_home — just inside the door, the room in one wide: sofa
  left, window back, TV right.
"""
import math
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling

ROOM_W = 6.0
ROOM_D = 5.0
CEIL = 2.6

COL_WALL = (0.58, 0.52, 0.42, 1.0)      # warm family beige
COL_BASE = (0.34, 0.28, 0.20, 1.0)
COL_FLOOR = (0.40, 0.29, 0.18, 1.0)
COL_SEAM = (0.30, 0.21, 0.13, 1.0)
COL_CEIL = (0.60, 0.57, 0.50, 1.0)
COL_SOFA = (0.36, 0.30, 0.24, 1.0)      # brown corduroy
COL_SOFA_DK = (0.28, 0.23, 0.18, 1.0)
COL_CUSHION = (0.52, 0.38, 0.24, 1.0)
COL_CHAIR = (0.34, 0.38, 0.30, 1.0)     # olive armchair
COL_WOOD = (0.34, 0.24, 0.16, 1.0)
COL_TV_BODY = (0.24, 0.20, 0.17, 1.0)
COL_TV_SCREEN = (0.55, 0.60, 0.62, 1.0) # cool glow — bloom lifts it
COL_RUG = (0.44, 0.30, 0.22, 1.0)
COL_RUG_RING = (0.34, 0.24, 0.18, 1.0)
COL_CURTAIN = (0.50, 0.42, 0.30, 1.0)
COL_GLASS = (0.35, 0.40, 0.50, 0.6)
COL_FRAME = (0.20, 0.18, 0.15, 1.0)
COL_LAMP = (1.00, 0.86, 0.55, 1.0)
COL_SHADE = (0.66, 0.56, 0.38, 1.0)
COL_PIC = (0.72, 0.68, 0.58, 1.0)
SPINES = [
    (0.48, 0.20, 0.16, 1.0), (0.22, 0.30, 0.24, 1.0), (0.60, 0.52, 0.36, 1.0),
    (0.24, 0.22, 0.34, 1.0), (0.55, 0.38, 0.20, 1.0), (0.42, 0.44, 0.46, 1.0),
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
    # Braided oval rug (rings suggested with two stacked slabs)
    make_box("Rug_Outer", (0.0, 2.6, 0.008), (2.8, 2.0, 0.012), COL_RUG_RING)
    make_box("Rug_Inner", (0.0, 2.6, 0.016), (2.2, 1.5, 0.010), COL_RUG)


def build_window():
    """N wall window with half-open curtains."""
    make_box("Win_Frame", (0.3, ROOM_D - 0.06, 1.60), (1.9, 0.08, 1.5), COL_FRAME)
    make_box("Win_Glass", (0.3, ROOM_D - 0.08, 1.60), (1.7, 0.05, 1.3), COL_GLASS)
    make_box("Win_Mull", (0.3, ROOM_D - 0.10, 1.60), (0.06, 0.05, 1.3), COL_FRAME)
    make_box("Win_Sill", (0.3, ROOM_D - 0.14, 0.82), (2.1, 0.20, 0.06), COL_FRAME)
    make_cyl("Curtain_Rod", (0.3, ROOM_D - 0.16, 2.42), 0.02, 2.3, COL_FRAME,
             segments=6, axis='X')
    make_box("Curtain_W", (-0.62, ROOM_D - 0.18, 1.55), (0.40, 0.12, 1.80), COL_CURTAIN)
    make_box("Curtain_E", (1.22, ROOM_D - 0.18, 1.55), (0.40, 0.12, 1.80), COL_CURTAIN)


def build_sofa():
    """Three-seat sofa against the W wall, facing the TV."""
    sx = -2.35
    make_box("Sofa_Base", (sx, 2.6, 0.28), (0.95, 2.2, 0.42), COL_SOFA_DK)
    make_box("Sofa_Back", (sx - 0.32, 2.6, 0.62), (0.30, 2.2, 0.75), COL_SOFA)
    for i, cy in enumerate((1.9, 2.6, 3.3)):
        make_box(f"Sofa_Seat_{i}", (sx + 0.08, cy, 0.50), (0.72, 0.64, 0.16), COL_SOFA)
    for cy in (1.55, 3.65):
        make_box(f"Sofa_Arm_{cy:.2f}", (sx, cy, 0.52), (0.95, 0.22, 0.50), COL_SOFA)
    make_box("Throw_Cushion_A", (sx - 0.10, 2.05, 0.72), (0.34, 0.34, 0.14), COL_CUSHION)
    make_box("Throw_Cushion_B", (sx - 0.10, 3.15, 0.72), (0.34, 0.34, 0.14), COL_CUSHION)


def build_tv():
    """CRT on its wood console, E wall."""
    make_box("TV_Console", (2.45, 2.6, 0.28), (0.75, 1.5, 0.55), COL_WOOD)
    make_box("TV_Body", (2.45, 2.6, 0.90), (0.66, 0.85, 0.68), COL_TV_BODY)
    make_box("TV_Screen", (2.10, 2.6, 0.90), (0.05, 0.62, 0.48), COL_TV_SCREEN)
    make_cyl("TV_Knob_A", (2.28, 3.02, 0.72), 0.035, 0.05, COL_FRAME, segments=8, axis='X')
    make_cyl("TV_Knob_B", (2.28, 3.02, 0.88), 0.035, 0.05, COL_FRAME, segments=8, axis='X')
    # Rabbit ears
    make_cyl("TV_Ear_L", (2.45, 2.45, 1.55), 0.012, 0.62, COL_FRAME, segments=5)
    make_cyl("TV_Ear_R", (2.55, 2.75, 1.55), 0.012, 0.62, COL_FRAME, segments=5)


def build_seating_extras():
    # Coffee table between sofa and TV
    make_box("Coffee_Top", (0.0, 2.6, 0.42), (1.2, 0.7, 0.05), COL_WOOD)
    for lx, ly in ((-0.5, 2.32), (0.5, 2.32), (-0.5, 2.88), (0.5, 2.88)):
        make_box(f"Coffee_Leg_{lx:.1f}_{ly:.2f}", (lx, ly, 0.21), (0.05, 0.05, 0.42), COL_WOOD)
    make_cyl("Mug_A", (-0.30, 2.50, 0.49), 0.045, 0.09, (0.60, 0.30, 0.24, 1.0), segments=8)
    make_cyl("Mug_B", (-0.12, 2.72, 0.49), 0.045, 0.09, (0.30, 0.40, 0.52, 1.0), segments=8)
    make_box("Magazine", (0.35, 2.55, 0.455), (0.30, 0.22, 0.012), (0.70, 0.66, 0.56, 1.0))
    # Armchair, SE corner angled into the group (axis-aligned)
    make_box("Chair_Base", (1.9, 1.0, 0.28), (0.85, 0.85, 0.42), COL_CHAIR)
    make_box("Chair_Back", (1.9, 0.62, 0.65), (0.85, 0.26, 0.72), COL_CHAIR)
    for cx in (1.52, 2.28):
        make_box(f"Chair_Arm_{cx:.2f}", (cx, 1.0, 0.52), (0.16, 0.85, 0.46), COL_CHAIR)


def build_details():
    # Bookshelf N wall, west of the window
    make_box("Shelf_Case", (-2.2, ROOM_D - 0.22, 0.95), (1.1, 0.32, 1.9), COL_WOOD)
    for zi, z in enumerate((0.35, 0.85, 1.35)):
        make_box(f"Shelf_S{zi}", (-2.2, ROOM_D - 0.22, z), (1.0, 0.28, 0.03),
                 (0.42, 0.30, 0.20, 1.0))
        for i in range(7):
            if (i + zi) % 5 == 3:
                continue
            k = (i * 5 + zi) % len(SPINES)
            h = 0.20 + 0.04 * ((i + zi) % 3)
            make_box(f"Shelf_Book_{zi}_{i}", (-2.62 + i * 0.13, ROOM_D - 0.22,
                     z + 0.02 + h / 2.0), (0.10, 0.20, h), SPINES[k])
    # Floor lamp beside the sofa
    make_cyl("Lamp_Post", (-2.5, 1.15, 0.72), 0.025, 1.44, COL_FRAME, segments=6)
    make_cyl("Lamp_Shade", (-2.5, 1.15, 1.55), 0.18, 0.24, COL_SHADE, segments=10)
    make_cyl("Lamp_Bulb", (-2.5, 1.15, 1.44), 0.05, 0.06, COL_LAMP, segments=8)
    # Framed pictures over the sofa
    for i, (py, pw) in enumerate(((2.1, 0.5), (2.75, 0.35), (3.3, 0.45))):
        make_box(f"Pic_{i}_Frame", (-2.93, py, 1.75), (0.04, pw, 0.42), COL_FRAME)
        make_box(f"Pic_{i}", (-2.91, py, 1.75), (0.03, pw - 0.08, 0.34), COL_PIC)
    # Ceiling fixture
    make_cyl("Ceiling_Dome", (0.0, 2.5, CEIL - 0.10), 0.16, 0.16, COL_LAMP, segments=10)


def main():
    clear_scene()
    build_shell()
    build_window()
    build_sofa()
    build_tv()
    build_seating_extras()
    build_details()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/wagner_home.glb"))
    print(f"\n[build_wagner_home] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
