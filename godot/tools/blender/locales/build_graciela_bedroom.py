"""Graciela's Bedroom — vol6 — Graciela Ramos (Diego's grandmother, 71,
892 Ashberry Drive, Harmony Creek Estates). A devout Latina abuela's
room: survived four hurricanes and two husbands. NOTHING like Diego's
crisp-white soccer shrine down the hall — warm peach walls, dark
traditional wood, and a home altar (retablo) that is the hero of the
room: crucifix, a framed Virgen de Guadalupe, saint statuettes, and
votive candles (veladoras) whose glow is the room's motivated light
(canon: ch0 prelude has her "on the edge of her bed in the dark,
holding a rosary she is not praying with" — so the altar candles are
the one warm thing in a dark room).

Re-arranged vs every other bedroom so it never reads as a reskin: the
BED sits headboard-against-the-NORTH wall (teen rooms put beds on a
side wall); the altar owns the EAST wall; a lace-curtained window +
photo dresser on the WEST wall; an upholstered rocker with a crocheted
afghan in the SW corner. Vertex colors carry albedo; graciela_bedroom.
tscn does the warm-dim candlelit lighting.

Coordinate frame: Blender Z-up. Interior y 0 (south door wall) → +Y
(north), walls at x = ±ROOM_W/2, ceiling at CEIL. glTF remaps to Godot
(x, z, -y). make_box / make_cyl only.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import (make_floor, make_wall, make_ceiling,
                              make_crown_molding, make_window)

ROOM_W = 4.0      # x ∈ [-2, 2]
ROOM_D = 4.5      # y ∈ [0, 4.5]  (door/S wall at y=0)
CEIL = 2.6

# ── Palette — warm, traditional, lived-in ──
COL_WALL = (0.80, 0.66, 0.54, 1.0)      # warm peach plaster
COL_BASE = (0.40, 0.28, 0.20, 1.0)
COL_FLOOR = (0.44, 0.30, 0.19, 1.0)     # dark wood
COL_SEAM = (0.28, 0.18, 0.11, 1.0)
COL_WOOD = (0.30, 0.18, 0.12, 1.0)      # dark traditional furniture
COL_WOOD_DK = (0.22, 0.13, 0.09, 1.0)
COL_SPREAD = (0.64, 0.38, 0.44, 1.0)    # rose chenille bedspread
COL_SPREAD_DK = (0.52, 0.28, 0.34, 1.0)
COL_PILLOW = (0.90, 0.85, 0.76, 1.0)
COL_LACE = (0.90, 0.87, 0.80, 1.0)      # doilies / lace
COL_BRASS = (0.72, 0.54, 0.24, 1.0)
COL_CORPUS = (0.84, 0.79, 0.70, 1.0)    # crucifix corpus / statues
COL_STATUE_BLUE = (0.72, 0.78, 0.86, 1.0)
COL_GUAD_ROBE = (0.24, 0.40, 0.34, 1.0) # Guadalupe teal robe
COL_GUAD_RAY = (0.80, 0.62, 0.24, 1.0)  # gold rays / mandorla
COL_CANDLE = (0.92, 0.88, 0.78, 1.0)
COL_FLAME = (1.0, 0.72, 0.30, 1.0)      # blooms via env glow
COL_ROSARY = (0.55, 0.18, 0.22, 1.0)
COL_LAMP_SHADE = (0.92, 0.80, 0.56, 1.0)
COL_LAMP_GLOW = (1.0, 0.86, 0.60, 1.0)
COL_CHAIR = (0.42, 0.30, 0.24, 1.0)     # upholstered rocker
COL_AFGHAN_A = (0.66, 0.34, 0.30, 1.0)  # crocheted afghan stripes
COL_AFGHAN_B = (0.70, 0.56, 0.28, 1.0)
COL_AFGHAN_C = (0.34, 0.44, 0.40, 1.0)
COL_RUG = (0.50, 0.24, 0.22, 1.0)
COL_RUG_BORDER = (0.30, 0.16, 0.14, 1.0)
COL_PHOTO_BW = (0.72, 0.70, 0.66, 1.0)
COL_GLASS = (0.62, 0.72, 0.78, 0.6)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
                  axis='Y', palette=pal, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=pal, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W / 4.0 + 0.5), 0.0, 0),
              length=ROOM_W / 2.0 - 1.0, height=CEIL, axis='X', palette=pal)
    make_wall("Wall_S_E", (+(ROOM_W / 4.0 + 0.5), 0.0, 0),
              length=ROOM_W / 2.0 - 1.0, height=CEIL, axis='X', palette=pal)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.30), (2.0, 0.20, 0.60), COL_WALL)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, with_grid=False, with_stains=False)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W / 2.0 + 0.10, ROOM_D / 2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W / 2.0 - 0.10, ROOM_D / 2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D - 0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_WOOD})


def build_bed():
    """Double bed, headboard against the NORTH wall (the re-arrangement
    that separates her from the teen rooms). Rose chenille spread,
    stacked pillows, a folded quilt at the foot, a small crucifix above."""
    bx = 0.0
    hb_y = ROOM_D - 0.16
    foot_y = 2.35
    by = (hb_y + foot_y) / 2.0
    bw = 1.55
    mattress_z = 0.52
    # Carved wooden headboard
    make_box("Bed_Headboard", (bx, hb_y, 0.95), (bw + 0.12, 0.10, 1.10), COL_WOOD_DK)
    make_box("Bed_Headboard_Crest", (bx, hb_y, 1.52), (bw - 0.2, 0.12, 0.14), COL_WOOD)
    for sgn in (-1, 1):
        make_cyl(f"Bed_Post_{sgn:+d}", (bx + sgn * (bw / 2.0 + 0.02), hb_y, 0.85),
                 0.05, 1.7, COL_WOOD_DK, segments=8)
    # Frame + mattress + spread
    make_box("Bed_Frame", (bx, by, 0.28), (bw + 0.08, hb_y - foot_y, 0.30), COL_WOOD)
    make_box("Bed_Mattress", (bx, by, mattress_z), (bw, hb_y - foot_y - 0.06, 0.18), COL_PILLOW)
    make_box("Bed_Spread", (bx, by + 0.05, mattress_z + 0.02),
             (bw + 0.06, hb_y - foot_y - 0.10, 0.14), COL_SPREAD)
    # spread hangs down the sides
    for sgn in (-1, 1):
        make_box(f"Bed_Spread_Drape_{sgn:+d}", (bx + sgn * (bw / 2.0 + 0.02), by + 0.05, 0.34),
                 (0.04, hb_y - foot_y - 0.10, 0.30), COL_SPREAD_DK)
    # Folded quilt at the foot
    make_box("Bed_FootQuilt", (bx, foot_y + 0.16, mattress_z + 0.06),
             (bw, 0.30, 0.10), COL_AFGHAN_B)
    # Pillows stacked against the headboard
    for pi, px in enumerate((-0.42, 0.42)):
        make_box(f"Bed_Pillow_{pi}", (bx + px, hb_y - 0.34, mattress_z + 0.12),
                 (0.62, 0.34, 0.16), COL_PILLOW)
    make_box("Bed_Pillow_Accent", (bx, hb_y - 0.30, mattress_z + 0.20),
             (0.50, 0.26, 0.12), COL_SPREAD_DK)
    # A rosary draped over the near bedpost, and one laid on the spread
    make_cyl("Rosary_Drape", (bx - (bw / 2.0 + 0.02), hb_y, 1.35), 0.02, 0.5,
             COL_ROSARY, segments=6)
    for k in range(6):
        make_box(f"Rosary_Bead_{k}", (bx - 0.2 + k * 0.05, by - 0.2, mattress_z + 0.11),
                 (0.02, 0.02, 0.02), COL_ROSARY)
    make_box("Rosary_Cross", (bx + 0.12, by - 0.2, mattress_z + 0.11),
             (0.02, 0.05, 0.02), COL_BRASS)
    # Small crucifix centered above the headboard on the north wall
    make_box("BedCrucifix_V", (bx, ROOM_D - 0.03, 2.1), (0.05, 0.02, 0.26), COL_WOOD_DK)
    make_box("BedCrucifix_H", (bx, ROOM_D - 0.03, 2.14), (0.18, 0.02, 0.05), COL_WOOD_DK)
    make_box("BedCrucifix_Corpus", (bx, ROOM_D - 0.045, 2.13), (0.06, 0.02, 0.12), COL_CORPUS)


def build_altar():
    """Home altar (retablo) on the EAST wall — the hero. Low chest with
    a lace cloth, a standing crucifix, a framed Virgen de Guadalupe, two
    saint statuettes, and a row of votive candles whose flames are the
    room's warm practical (the tscn Omni sits at Altar_Candles)."""
    ax = ROOM_W / 2.0 - 0.24
    ay = 1.45
    top_z = 0.82
    # Chest / altar table
    make_box("Altar_Chest", (ax, ay, top_z / 2.0), (0.40, 0.9, top_z), COL_WOOD)
    for dz in (0.24, 0.54):
        make_box(f"Altar_Drawer_{dz}", (ax - 0.20, ay, dz), (0.02, 0.8, 0.22), COL_WOOD_DK)
        make_cyl(f"Altar_Pull_{dz}", (ax - 0.21, ay, dz), 0.02, 0.03, COL_BRASS,
                 segments=6, axis='X')
    # Lace altar cloth draped over the top
    make_box("Altar_Cloth", (ax, ay, top_z + 0.01), (0.42, 0.94, 0.02), COL_LACE)
    make_box("Altar_Cloth_Fringe", (ax - 0.20, ay, top_z - 0.04), (0.02, 0.94, 0.08), COL_LACE)
    # Framed Virgen de Guadalupe on the wall above the altar
    gx = ROOM_W / 2.0 - 0.04
    make_box("Guadalupe_Frame", (gx, ay, 1.62), (0.03, 0.44, 0.62), COL_GUAD_RAY)
    make_box("Guadalupe_Image", (gx - 0.005, ay, 1.62), (0.02, 0.36, 0.54), COL_GUAD_ROBE)
    make_box("Guadalupe_Figure", (gx - 0.012, ay, 1.60), (0.02, 0.14, 0.34), COL_CORPUS)
    make_box("Guadalupe_Mandorla", (gx - 0.008, ay, 1.62), (0.02, 0.24, 0.44), COL_GUAD_RAY)
    make_box("Guadalupe_Robe", (gx - 0.014, ay, 1.56), (0.02, 0.12, 0.24), COL_GUAD_ROBE)
    # Standing crucifix on the altar
    make_box("Altar_Crucifix_Base", (ax, ay - 0.28, top_z + 0.05), (0.10, 0.10, 0.06), COL_WOOD_DK)
    make_box("Altar_Crucifix_V", (ax, ay - 0.28, top_z + 0.24), (0.03, 0.03, 0.34), COL_WOOD_DK)
    make_box("Altar_Crucifix_H", (ax, ay - 0.28, top_z + 0.30), (0.03, 0.18, 0.03), COL_WOOD_DK)
    make_box("Altar_Crucifix_Corpus", (ax - 0.01, ay - 0.28, top_z + 0.28), (0.02, 0.05, 0.11), COL_BRASS)
    # Two saint statuettes
    for si, (sy, col) in enumerate([(ay + 0.28, COL_STATUE_BLUE), (ay + 0.10, COL_CORPUS)]):
        make_cyl(f"Saint_{si}_Body", (ax, sy, top_z + 0.12), 0.045, 0.20, col, segments=8)
        make_cyl(f"Saint_{si}_Head", (ax, sy, top_z + 0.25), 0.03, 0.06, COL_CORPUS, segments=6)
        make_box(f"Saint_{si}_Halo", (ax, sy, top_z + 0.30), (0.02, 0.08, 0.02), COL_GUAD_RAY)
    # Row of votive candles (veladoras) — the practical light source
    for ci, cy in enumerate((ay - 0.10, ay - 0.02, ay + 0.34)):
        h = 0.14 + 0.03 * (ci % 2)
        make_cyl(f"Altar_Votive_{ci}", (ax + 0.06, cy, top_z + h / 2.0 + 0.02), 0.035, h,
                 (0.86, 0.30, 0.26, 0.9), segments=8)   # red glass veladora
        make_cyl(f"Altar_Candles", (ax + 0.06, cy, top_z + h + 0.05), 0.012, 0.05,
                 COL_CANDLE, segments=6)
        make_box(f"Altar_Flame_{ci}", (ax + 0.06, cy, top_z + h + 0.10),
                 (0.02, 0.02, 0.04), COL_FLAME)
    # A framed family photo and a small dish of holy water
    make_box("Altar_Photo", (ax + 0.10, ay - 0.38, top_z + 0.10), (0.02, 0.14, 0.16), COL_BRASS)
    make_box("Altar_Photo_Img", (ax + 0.09, ay - 0.38, top_z + 0.10), (0.01, 0.10, 0.12), COL_PHOTO_BW)


def build_dresser_window():
    """WEST wall: a lace-curtained window with warm light behind it, and
    below/beside it a dresser crowded with framed family photographs —
    the visual record of a long life."""
    # Window high on the west wall
    make_window("Window", (-ROOM_W / 2.0 + 0.05, 3.3, 1.55), width=1.10, height=1.10,
                cross_mullion=True,
                palette={"glass": COL_GLASS, "warm": (1.0, 0.82, 0.52, 0.7)})
    # Lace curtains (two panels + a valance)
    make_box("Curtain_Valance", (-ROOM_W / 2.0 + 0.10, 3.3, 2.18), (0.03, 1.4, 0.20), COL_LACE)
    for sgn, cy in [(-1, 3.3 - 0.62), (+1, 3.3 + 0.62)]:
        make_box(f"Curtain_Panel_{sgn:+d}", (-ROOM_W / 2.0 + 0.09, cy, 1.5),
                 (0.03, 0.26, 1.4), COL_LACE)
    # Dresser under the window
    dx, dy = -ROOM_W / 2.0 + 0.32, 3.3
    make_box("Dresser_Body", (dx, dy, 0.44), (0.44, 1.0, 0.88), COL_WOOD)
    for dz in (0.24, 0.50, 0.74):
        make_box(f"Dresser_Drawer_{dz}", (dx + 0.20, dy, dz), (0.02, 0.9, 0.22), COL_WOOD_DK)
        for hx in (-0.22, 0.22):
            make_cyl(f"Dresser_Pull_{dz}_{hx}", (dx + 0.21, dy + hx, dz), 0.018, 0.03,
                     COL_BRASS, segments=6, axis='X')
    # Lace runner + a crowd of framed photos on top
    make_box("Dresser_Runner", (dx, dy, 0.89), (0.40, 0.96, 0.02), COL_LACE)
    photo_specs = [(-0.34, 0.20, 0.24, COL_BRASS), (-0.10, 0.16, 0.20, COL_STATUE_BLUE),
                   (0.12, 0.22, 0.26, COL_WOOD_DK), (0.34, 0.14, 0.18, COL_BRASS),
                   (0.02, 0.18, 0.16, COL_GUAD_RAY)]
    for pi, (py, pw, ph, frame) in enumerate(photo_specs):
        make_box(f"Photo_{pi}_Frame", (dx - 0.06, dy + py, 0.90 + ph / 2.0),
                 (0.02, pw, ph), frame)
        make_box(f"Photo_{pi}_Img", (dx - 0.072, dy + py, 0.90 + ph / 2.0),
                 (0.01, pw - 0.04, ph - 0.04), COL_PHOTO_BW)
    # A jewelry box + a hairbrush + a small statue
    make_box("Dresser_JewelBox", (dx + 0.02, dy - 0.42, 0.94), (0.16, 0.12, 0.08), COL_WOOD_DK)
    make_box("Dresser_Brush", (dx + 0.06, dy + 0.44, 0.905), (0.12, 0.05, 0.03), COL_WOOD)


def build_nightstand():
    """Nightstand on the near (east-of-bed) side: a warm lamp (secondary
    practical), reading glasses, a well-thumbed missal, a glass of
    water, a pill organizer."""
    nx, ny = 0.98, 2.7
    top_z = 0.56
    make_box("Nightstand_Body", (nx, ny, top_z / 2.0), (0.40, 0.40, top_z), COL_WOOD)
    make_box("Nightstand_Drawer", (nx, ny - 0.20, 0.40), (0.34, 0.02, 0.16), COL_WOOD_DK)
    make_cyl("Nightstand_Pull", (nx, ny - 0.21, 0.40), 0.02, 0.03, COL_BRASS, segments=6, axis='Y')
    make_box("Nightstand_Doily", (nx, ny, top_z + 0.01), (0.36, 0.36, 0.02), COL_LACE)
    # Lamp
    make_cyl("Lamp_Base", (nx, ny + 0.06, top_z + 0.05), 0.07, 0.05, COL_WOOD_DK, segments=10)
    make_cyl("Lamp_Stem", (nx, ny + 0.06, top_z + 0.20), 0.015, 0.24, COL_BRASS, segments=6)
    make_cyl("Lamp_Shade", (nx, ny + 0.06, top_z + 0.36), 0.12, 0.16, COL_LAMP_SHADE, segments=12)
    make_cyl("Lamp_Glow", (nx, ny + 0.06, top_z + 0.34), 0.09, 0.10, COL_LAMP_GLOW, segments=10)
    # Missal, glasses, water glass, pill organizer
    make_box("Missal", (nx - 0.08, ny - 0.06, top_z + 0.03), (0.14, 0.20, 0.04), COL_WOOD_DK)
    make_box("Missal_Ribbon", (nx - 0.08, ny + 0.02, top_z + 0.05), (0.02, 0.10, 0.005), COL_ROSARY)
    make_box("ReadingGlasses", (nx + 0.10, ny - 0.02, top_z + 0.02), (0.12, 0.05, 0.01), COL_WOOD_DK)
    make_cyl("WaterGlass", (nx + 0.10, ny + 0.12, top_z + 0.06), 0.03, 0.10, COL_GLASS, segments=8)
    make_box("PillOrganizer", (nx - 0.02, ny + 0.14, top_z + 0.02), (0.16, 0.05, 0.02),
             COL_STATUE_BLUE)


def build_rocker():
    """Upholstered rocking chair in the SW corner with a crocheted
    afghan thrown over the back — where she sits with the rosary."""
    cx, cy = -1.35, 1.0
    seat_z = 0.44
    make_box("Rocker_Seat", (cx, cy, seat_z), (0.5, 0.5, 0.10), COL_CHAIR)
    make_box("Rocker_Back", (cx, cy + 0.24, seat_z + 0.34), (0.5, 0.08, 0.62), COL_CHAIR)
    for sgn in (-1, 1):
        make_box(f"Rocker_Arm_{sgn:+d}", (cx + sgn * 0.27, cy, seat_z + 0.18),
                 (0.06, 0.44, 0.10), COL_WOOD_DK)
        make_box(f"Rocker_ArmPost_{sgn:+d}", (cx + sgn * 0.27, cy - 0.18, seat_z / 2.0),
                 (0.05, 0.05, seat_z), COL_WOOD_DK)
    # Curved rockers (approximate with two long low boxes)
    for sgn in (-1, 1):
        make_box(f"Rocker_Runner_{sgn:+d}", (cx + sgn * 0.24, cy, 0.05),
                 (0.05, 0.66, 0.06), COL_WOOD_DK)
    # Crocheted afghan over the back, three-color stripes
    afg = [COL_AFGHAN_A, COL_AFGHAN_B, COL_AFGHAN_C]
    for k in range(5):
        make_box(f"Afghan_{k}", (cx, cy + 0.20, seat_z + 0.16 + k * 0.10),
                 (0.52, 0.05, 0.10), afg[k % 3])
    make_box("Afghan_Lap", (cx, cy - 0.05, seat_z + 0.06), (0.48, 0.30, 0.06), COL_AFGHAN_A)


def build_dressing():
    """Rug + a wall crucifix niche near the door + a small trash bin, to
    finish the room."""
    # Patterned area rug centered in the floor
    make_box("Rug", (0.0, 2.2, 0.02), (2.4, 2.6, 0.02), COL_RUG)
    make_box("Rug_Border", (0.0, 2.2, 0.025), (2.2, 2.4, 0.015), COL_RUG_BORDER)
    make_box("Rug_Field", (0.0, 2.2, 0.03), (1.9, 2.1, 0.012), COL_RUG)
    # A framed Sacred Heart print by the door (south-east wall)
    make_box("SacredHeart_Frame", (1.6, 0.12, 1.6), (0.36, 0.03, 0.46), COL_WOOD_DK)
    make_box("SacredHeart_Img", (1.6, 0.135, 1.6), (0.28, 0.02, 0.38), COL_ROSARY)
    make_box("SacredHeart_Heart", (1.6, 0.125, 1.58), (0.10, 0.02, 0.12), COL_FLAME)
    # Slippers on the floor by the bed
    for sgn in (-1, 1):
        make_box(f"Slipper_{sgn:+d}", (0.5 + sgn * 0.09, 2.3, 0.04), (0.10, 0.24, 0.06), COL_SPREAD_DK)


def main():
    clear_scene()
    build_shell()
    build_bed()
    build_altar()
    build_dresser_window()
    build_nightstand()
    build_rocker()
    build_dressing()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/graciela_bedroom.glb"))
    print(f"\n[build_graciela_bedroom] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
