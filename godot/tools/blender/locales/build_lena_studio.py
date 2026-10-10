"""lena_studio — Lena's painting studio behind the Daily Grind (vol7 ch3).

NEW SET (2026-10-10). vol7_ch3_studio played its studio half in Lena's
apartment. The prose:

  "The studio was a back room behind the Daily Grind that Hans the baker had
  rented her in 2049. The room had been storage for the Daily Grind's
  previous owner ... Twelve by sixteen. One north window. A sink. Cold
  concrete she had covered, in winter, with a wool rug from Margit's." ·
  "The canvas was on the wall. Six by eight. Stretched on bars she had made
  herself. The surface was the eleventh underpainting — layered grays and
  umbers and a green she had been mixing for months ... She had scraped a
  section in the lower-right quadrant last week, almost back to the gesso."
  · "The apron. The brushes. Bone black, Naples yellow, the green, titanium
  white onto the glass palette. Solvent at the corner of the table. Heater
  on, because the room was at fifty-three." · "she sat on the wooden stool
  in the corner" · "She locked the studio door behind her and stepped out
  into the alley." · (ch14) "the pigment she ground from the batch she made
  every six months in the studio".

The room is the size the prose gives — 12 x 16 ft, 3.66 x 4.88 m, under the
old storage room's 2.9 m ceiling — because the prose measures it:
  · THE CANVAS on the W wall, 8 ft wide and 6 ft tall on its handmade bars:
    the grays and umbers and the green, the scraped lower-right quadrant
    down to the gesso, the one line of bone black in the upper left.
  · THE TABLE on the E wall: the glass palette with its four colours laid
    out, the brushes in their jars, the tubes, the solvent at the corner,
    the rags, the muller and the jar of bone black she grinds; the apron on
    its hook; the clamp lamp on the canvas.
  · The utility sink in the NE corner under the shelf of old storage; the
    one north window on the wet alley wall; the wool rug on the concrete;
    the wooden stool in the SW corner with the space heater beside it; the
    old shelving of the room's storage days; the steel door to the alley.

Coordinate frame: Blender Z-up; x 0..3.66 (W-E), y 0..4.88 (S-N), the door
in the S wall. glTF export remaps to Godot (x, z, -y).

Draft 2 targets: the earlier canvases turned to the wall; drips on the
concrete; the rain on the north window; the Starfish Nebula's corner on the
alley wall past the window.
"""
import math
import os
import random
import sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_lathe, make_rot_box, export_glb
from _props.structure import make_floor, make_wall, make_wall_with_openings, make_window
from _props.furniture import make_stool

W, D, CEIL = 3.66, 4.88, 2.90

COL_WALL = (0.80, 0.78, 0.72, 1.0)       # old storage-room paint, scuffed
COL_CONCRETE = (0.50, 0.50, 0.48, 1.0)
COL_SEAM = (0.42, 0.42, 0.40, 1.0)
COL_WOOD = (0.56, 0.42, 0.28, 1.0)
COL_DARK = (0.16, 0.16, 0.18, 1.0)
COL_STEEL = (0.60, 0.62, 0.64, 1.0)
COL_GESSO = (0.94, 0.93, 0.88, 1.0)
COL_BONE_BLACK = (0.08, 0.08, 0.09, 1.0)
COL_NAPLES = (0.96, 0.84, 0.52, 1.0)
COL_GREEN = (0.34, 0.42, 0.30, 1.0)      # "a green she had been mixing for months"
COL_WHITE = (0.97, 0.97, 0.95, 1.0)


def build_shell():
    make_floor("Floor", (W / 2.0, D / 2.0, 0.0), size_x=W + 0.4, size_y=D + 0.4, palette={"vinyl": COL_CONCRETE, "seam": COL_SEAM})
    pal = {"wall": COL_WALL, "baseboard": (0.40, 0.38, 0.34, 1.0)}
    make_wall("Wall_W", (0.0, D / 2.0, 0), length=D + 0.4, height=CEIL, axis='Y', palette=pal, baseboard_face_sign=+1)
    make_wall("Wall_E", (W, D / 2.0, 0), length=D + 0.4, height=CEIL, axis='Y', palette=pal, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_N", (W / 2.0, D, 0), length=W + 0.4, height=CEIL, axis='X', palette=pal,
                            baseboard_face_sign=-1, openings=[(1.55, 1.65, 1.10, 1.20)])
    make_wall_with_openings("Wall_S", (W / 2.0, 0.0, 0), length=W + 0.4, height=CEIL, axis='X', palette=pal,
                            baseboard_face_sign=+1, openings=[(2.85, 1.05, 0.90, 2.10)])
    make_box("Ceil", (W / 2.0, D / 2.0, CEIL + 0.05), (W + 0.4, D + 0.4, 0.10), (0.82, 0.80, 0.76, 1.0))
    # the one north window, on the wet alley
    make_window("Win_N", (1.55, D - 0.10, 1.65), width=1.10, height=1.20, room_dir=-1, see_through=True,
                palette={"frame": (0.70, 0.70, 0.66, 1.0)}, cross_mullion=True)
    make_box("Win_N_Glass", (1.55, D - 0.02, 1.65), (1.10, 0.01, 1.20), (0.70, 0.76, 0.80, 0.30))
    make_box("Win_N_Sill", (1.55, D - 0.17, 1.035), (1.24, 0.14, 0.03), (0.70, 0.70, 0.66, 1.0))
    # the steel door to the alley, shut, its deadbolt
    make_box("Alley_Door", (2.85, 0.0, 1.04), (0.88, 0.05, 2.08), (0.36, 0.40, 0.42, 1.0))
    make_box("Alley_Door_Deadbolt", (2.50, 0.035, 1.10), (0.06, 0.04, 0.06), COL_STEEL)
    make_box("Alley_Door_Lever", (2.50, 0.045, 0.98), (0.14, 0.04, 0.03), COL_STEEL)
    # the bare bulb overhead, the conduit to it
    make_cyl("Ceiling_Bulb_Socket", (1.8, 2.4, CEIL - 0.05), 0.04, 0.10, COL_DARK, segments=8)
    make_cyl("Ceiling_Bulb", (1.8, 2.4, CEIL - 0.14), 0.05, 0.08, (0.98, 0.90, 0.70, 1.0), segments=10)
    make_box("Ceiling_Conduit", (1.8, 1.2, CEIL - 0.015), (0.03, 2.40, 0.03), COL_STEEL)
    # the wool rug on the concrete, before the canvas
    make_box("Wool_Rug", (1.20, 2.40, 0.006), (1.80, 2.40, 0.012), (0.56, 0.36, 0.26, 1.0))


def build_canvas():
    """Six by eight on handmade bars on the W wall; the eleventh underpainting."""
    face = 0.10
    cy0, cy1 = 1.20, 1.20 + 2.44                 # 8 ft wide along the wall
    z0, z1 = 0.42, 0.42 + 1.83                   # 6 ft tall, on two cleats
    cy, cz = (cy0 + cy1) / 2.0, (z0 + z1) / 2.0
    for k, (zz) in enumerate((z0 + 0.25, z1 - 0.25)):
        make_box(f"Canvas_Cleat_{k}", (face + 0.02, cy, zz), (0.04, 2.20, 0.06), COL_WOOD)
    make_box("Canvas_Stretcher", (face + 0.06, cy, cz), (0.04, cy1 - cy0, z1 - z0), COL_WOOD)
    make_box("Canvas_Surface", (face + 0.081, cy, cz), (0.002, cy1 - cy0 - 0.02, z1 - z0 - 0.02), (0.44, 0.42, 0.38, 1.0))
    # the layered grays and umbers and the green, in broad passages
    rnd = random.Random(11)
    cols = ((0.36, 0.34, 0.32, 1.0), (0.46, 0.38, 0.30, 1.0), (0.30, 0.28, 0.26, 1.0), COL_GREEN, (0.52, 0.50, 0.46, 1.0), (0.40, 0.32, 0.24, 1.0))
    for k in range(14):
        w, h = rnd.uniform(0.30, 1.00), rnd.uniform(0.25, 0.70)
        py = rnd.uniform(cy0 + w / 2.0, cy1 - 0.9 - w / 2.0) if k % 3 else rnd.uniform(cy0 + w / 2.0, cy1 - w / 2.0)
        pz = rnd.uniform(z0 + 0.7 + h / 2.0, z1 - h / 2.0) if k % 2 else rnd.uniform(z0 + h / 2.0, z1 - h / 2.0)
        make_box(f"Canvas_Passage_{k}", (face + 0.083, py, pz), (0.001, w, h), cols[k % len(cols)])
    # the scraped wound in the lower right (from the room: lower right = toward +y, low), almost back to the gesso
    make_box("Canvas_Scraped", (face + 0.084, cy1 - 0.52, z0 + 0.40), (0.001, 0.70, 0.52), (0.84, 0.82, 0.76, 1.0))
    make_box("Canvas_Scraped_Edge", (face + 0.0845, cy1 - 0.52, z0 + 0.67), (0.001, 0.72, 0.03), (0.30, 0.28, 0.26, 1.0))
    # the one line of bone black in the upper left, no wider than her smallest brush
    make_box("Canvas_Bone_Black_Line", (face + 0.085, cy0 + 0.50, z1 - 0.40), (0.001, 0.30, 0.008), COL_BONE_BLACK)
    # the clamp lamp on the top bar
    make_box("Clamp_Lamp_Clamp", (face + 0.06, cy0 + 0.30, z1 + 0.03), (0.06, 0.05, 0.06), COL_DARK)
    make_rot_box("Clamp_Lamp_Arm", (face + 0.18, cy0 + 0.30, z1 + 0.14), (0.24, 0.02, 0.02), COL_DARK, pitch=-0.6)
    make_lathe("Clamp_Lamp_Shade", (face + 0.30, cy0 + 0.30, z1 + 0.10), [(0.0, 0.14), (0.03, 0.14), (0.09, 0.0), (0.0, 0.0)], (0.66, 0.68, 0.70, 1.0), segments=12)
    make_cyl("Clamp_Lamp_Bulb", (face + 0.30, cy0 + 0.30, z1 + 0.12), 0.03, 0.04, (0.98, 0.92, 0.74, 1.0), segments=8)


def build_table():
    """The work table on the E wall: the glass palette, the colours, the brushes, the solvent."""
    tx, ty = W - 0.10 - 0.40, 2.30
    tw, td, th = 0.80, 1.80, 0.86
    make_box("Work_Table_Top", (tx, ty, th - 0.02), (tw, td, 0.04), COL_WOOD)
    for i, (lx, ly) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        make_box(f"Work_Table_Leg_{i}", (tx + lx * (tw / 2.0 - 0.04), ty + ly * (td / 2.0 - 0.04), (th - 0.04) / 2.0), (0.05, 0.05, th - 0.04), COL_WOOD)
    for e in (-1, 1):   # the stretchers the shelf rests on, leg to leg
        make_box(f"Work_Table_Stretcher_{e:+d}", (tx + e * (tw / 2.0 - 0.04), ty, 0.17), (0.04, td - 0.13, 0.04), COL_WOOD)
    make_box("Work_Table_Shelf", (tx, ty, 0.20), (tw - 0.10, td - 0.14, 0.03), COL_WOOD)
    t = th
    # the glass palette and the four colours on it
    make_box("Glass_Palette", (tx - 0.10, ty - 0.20, t + 0.004), (0.45, 0.60, 0.008), (0.82, 0.86, 0.86, 1.0))
    for k, (col, py) in enumerate(((COL_BONE_BLACK, -0.42), (COL_NAPLES, -0.28), (COL_GREEN, -0.14), (COL_WHITE, 0.00))):
        make_cyl(f"Palette_Daub_{k}", (tx - 0.26, ty - 0.20 + py + 0.21, t + 0.012), 0.035, 0.010, col, segments=10)
    make_box("Palette_Knife", (tx - 0.02, ty - 0.10, t + 0.010), (0.03, 0.20, 0.004), COL_STEEL)
    # the tubes laid out beside it
    for k, col in enumerate((COL_BONE_BLACK, COL_NAPLES, COL_GREEN, COL_WHITE, (0.48, 0.30, 0.20, 1.0))):
        make_cyl(f"Paint_Tube_{k}", (tx + 0.22, ty - 0.45 + k * 0.07, t + 0.018), 0.017, 0.14, col, segments=8, axis='X')
    # the brushes in their jars, the solvent capped at the table's corner, the rags
    for j, jy in enumerate((ty + 0.30, ty + 0.48)):
        make_cyl(f"Brush_Jar_{j}", (tx + 0.05, jy, t + 0.07), 0.05, 0.14, (0.72, 0.78, 0.76, 0.6), segments=10)
        for b in range(5):
            a = (b - 2) * 0.10
            make_rot_box(f"Brush_Jar_{j}_Brush_{b}", (tx + 0.05 + 0.03 * math.sin(a), jy + 0.03 * math.cos(a), t + 0.20), (0.008, 0.008, 0.26), COL_WOOD, pitch=a, roll=0.08 * (b % 2))
    make_cyl("Solvent_Can", (tx + 0.25, ty + 0.78, t + 0.09), 0.06, 0.18, (0.62, 0.20, 0.16, 1.0), segments=10)
    make_cyl("Solvent_Can_Cap", (tx + 0.25, ty + 0.78, t + 0.19), 0.02, 0.02, COL_DARK, segments=8)
    make_rot_box("Rag", (tx - 0.20, ty + 0.62, t + 0.01), (0.26, 0.22, 0.02), (0.84, 0.78, 0.66, 1.0), yaw=0.4)
    # the bone black she grinds: the jar, the muller on its slab
    make_box("Grinding_Slab", (tx - 0.15, ty + 0.30, t + 0.01), (0.25, 0.25, 0.02), (0.80, 0.80, 0.78, 1.0))
    make_lathe("Muller", (tx - 0.15, ty + 0.30, t + 0.02), [(0.0, 0.0), (0.05, 0.0), (0.04, 0.03), (0.02, 0.06), (0.02, 0.12), (0.0, 0.12)], (0.86, 0.86, 0.84, 1.0), segments=12)
    make_cyl("Bone_Black_Jar", (tx + 0.25, ty + 0.30, t + 0.06), 0.045, 0.12, (0.80, 0.84, 0.84, 0.6), segments=10)
    make_cyl("Bone_Black_Jar_Fill", (tx + 0.25, ty + 0.30, t + 0.045), 0.04, 0.08, COL_BONE_BLACK, segments=10)
    # under the table: the gesso bucket, the stacked stretcher bars
    make_cyl("Gesso_Bucket", (tx, ty - 0.55, 0.215 + 0.14), 0.13, 0.28, COL_WHITE, segments=12)
    for k in range(4):
        make_box(f"Stretcher_Bar_{k}", (tx, ty + 0.30, 0.215 + 0.025 + k * 0.05), (0.06, 1.10, 0.05), COL_WOOD)
    # the apron on its hook by the door
    make_box("Apron_Hook", (2.20, 0.13, 1.65), (0.04, 0.06, 0.04), COL_STEEL)
    make_box("Apron", (2.20, 0.17, 1.25), (0.50, 0.04, 0.80), (0.42, 0.40, 0.34, 1.0))
    for k in range(4):
        make_box(f"Apron_Smear_{k}", (2.08 + k * 0.08, 0.192, 1.15 + 0.08 * (k % 2)), (0.05, 0.002, 0.10), (COL_BONE_BLACK, COL_GREEN, COL_NAPLES, (0.46, 0.38, 0.30, 1.0))[k])


def build_corners():
    # the utility sink in the NE corner under the old storage shelf
    sx, sy = W - 0.10 - 0.30, D - 0.10 - 0.28
    make_box("Utility_Sink", (sx, sy, 0.80), (0.56, 0.52, 0.30), (0.86, 0.86, 0.84, 1.0))
    for i, (lx, ly) in enumerate(((-1, -1), (1, -1))):
        make_box(f"Utility_Sink_Leg_{i}", (sx + lx * 0.24, sy + ly * 0.20, 0.33), (0.04, 0.04, 0.66), COL_STEEL)
    make_cyl("Utility_Sink_Faucet", (sx, sy + 0.20, 1.07), 0.012, 0.24, COL_STEEL, segments=6)
    make_box("Storage_Shelf", (W - 0.10 - 0.30, D - 0.10 - 0.18, 2.05), (0.60, 0.36, 0.03), COL_WOOD)
    for e in (-1, 1):
        make_box(f"Storage_Shelf_Bracket_{e:+d}", (W - 0.10 - 0.30 + e * 0.24, D - 0.10 - 0.05, 1.96), (0.03, 0.10, 0.15), COL_STEEL)
    for k in range(3):
        make_box(f"Storage_Box_{k}", (W - 0.10 - 0.48 + k * 0.18, D - 0.10 - 0.18, 2.15), (0.16, 0.30, 0.17), (0.78, 0.66, 0.48, 1.0))
    # the wooden stool in the SW corner, the space heater beside it
    make_stool("Stool", 0.45, 0.50, h=0.66, wood=COL_WOOD)
    make_box("Space_Heater", (0.95, 0.30, 0.26), (0.40, 0.18, 0.52), (0.86, 0.84, 0.80, 1.0))
    make_box("Space_Heater_Grille", (0.95, 0.389, 0.30), (0.32, 0.004, 0.34), (0.86, 0.36, 0.16, 1.0))
    make_box("Space_Heater_Cord", (1.20, 0.25, 0.01), (0.30, 0.02, 0.02), COL_DARK)
    # the earlier canvases, turned to the wall at the N end of the W wall
    for k in range(3):
        make_box(f"Old_Canvas_{k}", (0.10 + 0.05 + k * 0.05, 4.30, 0.49), (0.025, 0.90 - k * 0.12, 0.98), COL_WOOD)


def build_alley():
    """Past the north window: the alley, its wet pavement, the brick across it."""
    make_box("Alley_Pavement", (W / 2.0, D + 1.9, -0.05), (12.0, 3.4, 0.10), (0.30, 0.30, 0.31, 1.0))
    make_box("Alley_Brick_Wall", (W / 2.0, D + 3.6, 3.0), (12.0, 0.30, 6.0), (0.50, 0.30, 0.24, 1.0))
    for k in range(9):
        make_box(f"Alley_Brick_Wall_Course_{k}", (W / 2.0, D + 3.449, 0.3 + k * 0.62), (12.0, 0.004, 0.02), (0.62, 0.54, 0.46, 1.0))
    make_cyl("Alley_Downpipe", (0.6, D + 3.38, 3.0), 0.06, 6.0, (0.36, 0.38, 0.40, 1.0), segments=8)
    make_box("Alley_Dumpster", (3.4, D + 2.7, 0.65), (1.80, 1.00, 1.30), (0.22, 0.34, 0.30, 1.0))
    make_box("Alley_Puddle", (1.8, D + 1.6, 0.002), (1.40, 0.70, 0.004), (0.20, 0.22, 0.24, 1.0))


def main():
    clear_scene()
    build_shell()
    build_canvas()
    build_table()
    build_corners()
    build_alley()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/lena_studio.glb"))
    print(f"\n[build_lena_studio] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
