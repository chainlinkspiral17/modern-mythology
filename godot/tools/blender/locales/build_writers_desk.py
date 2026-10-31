"""writers_desk — vol 4's scrapbook desk (draft 1, 2026-10-16).

The user: "Let's move back to background and model work for all the new vol
1-4 stuff." Vol 4 (the scrapbook: poems, blog scraps, the stories, the zine)
is read at one desk — 33 scene uses across vol4_desk_night, desk_dawn,
bedroom_desk, corkboard_night and the two betterment desks; the most-used
new place in vols 1-4 (lore/_VOL1_4_SETS_AND_CAST.md).

What the scenes say, and where it is here:
  "The desk drawer sticks, then gives. Desert sand in the runners."
      → the pedestal's top drawer pulled 14 cm, a skim of sand in it
  "In the drawer, with the rubber bands and the dead nine-volts, a ball of
   red string."                         → Drawer_Bands / _9V_* / _String_Ball
  "Four clippings on the cork."        → Board_Clipping_0..3 (HeroArt-ready)
  "Over the desk the corkboard has gaps in it, pale squares where
   something ought to hang."           → Board_Gap_0..2, cork unfaded
  "The folder marked vii. is held shut with a pushpin through both
   covers."                             → Folder_vii + Folder_vii_Pin
  "The desk near dawn. Every drawer pulled. The corkboard in the window
   light, the red string gone brown."  → the board beside the N window;
   "Through the glass, the street. A car idles at the curb"
                                        → View_N, a street (make_view)
  A bed on the W wall for vol4_bedroom_desk ("nothing doing", "wit's end").

Room: 5.0 x 5.6 m, ceiling 2.7 — a real mid-2000s one-room apartment (BUILD
BIG: the desk, a bed, books and a door, with room to walk between them).
Blender axes: x east, y north, z up; Godot (x, z, -y).

DRAFT 2 (2026-10-20, the Deck: "interiors need more windows" / "still in
the too boxy phase"): a corner room — a second, narrow N window west of the
board and an E window on the side street (make_view "side"), each with the
kit's new trim (casing, stool, apron) and the big two curtained; the
rectangle broken by an old chimney breast on the W wall (fireplace bricked
up, a mantel); a two-panel door; the bed kit's soft mattress, stuffed
pillows and draped blanket. The sill papers sit on the stool.

DRAFT 3 (2026-10-30, the vols 1-4 sweep; the set carries 37 scene uses):
the text over the build — the lamp "has a round brass shade. Up close it
looks like a porthole" (it was a green banker's can); the kaleidoscope that
"rolls out from under the zine ... ducks printed on the paper, worn white at
both ends"; the top drawer's "newspaper, a novel, and a toy soldier"; and
the bottom FILE drawer of vol4_drawer (eleven scenes: "Green hanging
folders, the tabs typed ONEIRONAUTICS INC."), pulled in its own view
`writers_desk_drawer`, with every drawer pulled at dawn ("Every drawer
pulled out"). The pulled drawers hang under tagged empties; the views that
pull them `strip` the closed fronts.

DRAFT 4 targets: the four folding church-basement chairs of "curtain call"
(a tagged group, like the drawers, for the dawn); the RUTA 77 car at the
curb with its cardboard sign for the dawn; the man by the door "in line for
a movie" is a figure, not set; HeroArt entries for the four clippings and
the folder tabs' type; the corkboard's red string gone brown at dawn;
wear (a scorch under the lamp); Deck-verified framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_chamfer_box, make_soft_box, make_lathe, export_glb
from _props.views import make_view
from _props.structure import (make_floor, make_wall, make_ceiling, make_crown_molding,
                              make_window, make_wall_with_openings, make_curtains)
from _props.furniture import make_bed, make_chair
from _props.decor import make_faded_poster
from _props.safety import make_smoke_detector
from _props.detail import (make_traffic_wear, make_floor_stain, make_wall_tint_band,
                           make_threshold, make_wall_outlet, make_light_switch)

ROOM_W = 5.0; ROOM_D = 5.6; CEIL = 2.7
PAL_WALL = {"wall": (0.80, 0.78, 0.70, 1.0), "baseboard": (0.30, 0.26, 0.22, 1.0)}
COL_FLOOR = (0.46, 0.34, 0.22, 1.0); COL_SEAM = (0.30, 0.21, 0.13, 1.0)
WOOD = (0.36, 0.25, 0.15, 1.0); WOOD_DARK = (0.24, 0.16, 0.10, 1.0)
CORK = (0.66, 0.50, 0.32, 1.0); CORK_PALE = (0.86, 0.74, 0.54, 1.0)
RED_STRING = (0.70, 0.14, 0.12, 1.0)
MANILA = (0.86, 0.74, 0.48, 1.0)
WIN_X, WIN_W, WIN_H, WIN_Z = 1.25, 1.30, 1.35, 1.55     # the N window
WIN2_X, WIN2_W = -1.85, 0.55                            # (draft 2) the narrow N window, west of the board
WINE_Y, WINE_W = 4.35, 1.10                             # (draft 2) the E window, the side street
CURTAIN = (0.56, 0.46, 0.34, 1.0)                       # an old mustard-brown pair, sun-faded
DESK_X, DESK_Y = -0.55, ROOM_D - 0.42                   # desk centre, against Wall_N
DESK_W, DESK_D, DESK_H = 1.55, 0.72, 0.75


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM}, style="plank")
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y',
              palette=PAL_WALL, baseboard_face_sign=+1)
    # (draft 2, the Deck: "interiors need more windows") a corner room: the
    # E wall opens on the side street too
    make_wall_with_openings("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y',
                            palette=PAL_WALL, baseboard_face_sign=-1,
                            openings=[(WINE_Y, WIN_Z, WINE_W, WIN_H)])
    make_wall_with_openings("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL, axis='X',
                            palette=PAL_WALL, baseboard_face_sign=-1,
                            openings=[(WIN_X, WIN_Z, WIN_W, WIN_H), (WIN2_X, WIN_Z, WIN2_W, WIN_H)])
    # S wall with the door east of centre
    door_x = 1.45
    make_wall("Wall_S_W", ((-ROOM_W / 2.0 - 0.2 + door_x - 0.50) / 2.0, 0.0, 0), length=(door_x - 0.50) + ROOM_W / 2.0 + 0.2,
              height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", ((door_x + 0.50 + ROOM_W / 2.0 + 0.2) / 2.0, 0.0, 0), length=ROOM_W / 2.0 + 0.2 - door_x - 0.50,
              height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (door_x, 0.0, (2.08 + CEIL) / 2.0), (1.0, 0.20, CEIL - 2.08), PAL_WALL["wall"])
    make_box("Door", (door_x, 0.06, 1.03), (0.86, 0.045, 2.04), WOOD_DARK)
    make_cyl("Door_Knob", (door_x - 0.34, 0.10, 0.98), 0.028, 0.05, (0.66, 0.56, 0.30, 1.0), axis='Y', segments=10)
    for k, (pz, ph) in enumerate(((0.52, 0.66), (1.48, 0.86))):       # (draft 2) a two-panel door, not a slab
        make_soft_box(f"Door_Panel_{k}", (door_x, 0.086, pz), (0.62, 0.012, ph), (0.28, 0.19, 0.12, 1.0), round=0.12)
    for side in (-1, 1):
        make_box(f"Door_Casing_{'W' if side < 0 else 'E'}", (door_x + side * 0.48, 0.11, 1.05), (0.06, 0.02, 2.10), (0.70, 0.66, 0.58, 1.0))
    make_box("Door_Casing_Head", (door_x, 0.11, 2.12), (1.02, 0.02, 0.07), (0.70, 0.66, 0.58, 1.0))
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4, with_grid=False)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W / 2.0 + 0.10, ROOM_D / 2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W / 2.0 - 0.10, ROOM_D / 2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D - 0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL,
                           palette={"wood": (0.70, 0.66, 0.58, 1.0)})
    make_window("Window_N", (WIN_X, ROOM_D - 0.10, WIN_Z), width=WIN_W, height=WIN_H, see_through=True)
    make_window("Window_N2", (WIN2_X, ROOM_D - 0.10, WIN_Z), width=WIN2_W, height=WIN_H, see_through=True, cross_mullion=False)
    make_window("Window_E", (ROOM_W / 2.0 - 0.10, WINE_Y, WIN_Z), width=WINE_W, height=WIN_H, axis='Y', room_dir=-1,
                see_through=True)
    make_curtains("Curtain_N", (WIN_X, ROOM_D - 0.10, WIN_Z), width=WIN_W, height=WIN_H, color=CURTAIN)
    make_curtains("Curtain_E", (ROOM_W / 2.0 - 0.10, WINE_Y, WIN_Z), width=WINE_W, height=WIN_H, axis='Y', room_dir=-1,
                  color=CURTAIN)
    # the room is not a box: an old chimney breast stands out of the W wall,
    # its fireplace bricked up long ago, a mantel shelf across it
    cbx0, cbx1, cby0, cby1 = -ROOM_W / 2.0 + 0.10, -ROOM_W / 2.0 + 0.50, 3.90, 5.10
    make_box("ChimneyBreast", ((cbx0 + cbx1) / 2.0, (cby0 + cby1) / 2.0, CEIL / 2.0), (cbx1 - cbx0, cby1 - cby0, CEIL), PAL_WALL["wall"])
    make_box("ChimneyBreast_Base", (cbx1 + 0.006, (cby0 + cby1) / 2.0, 0.06), (0.012, cby1 - cby0, 0.12), PAL_WALL["baseboard"])
    make_box("Fireplace_Bricked", (cbx1 + 0.004, (cby0 + cby1) / 2.0, 0.42), (0.008, 0.62, 0.70), (0.52, 0.34, 0.26, 1.0))
    make_box("Fireplace_Surround", (cbx1 + 0.012, (cby0 + cby1) / 2.0, 0.42), (0.024, 0.86, 0.86), (0.84, 0.82, 0.76, 1.0))
    make_soft_box("Mantel_Shelf", (cbx1 + 0.08, (cby0 + cby1) / 2.0, 0.88), (0.18, 1.10, 0.05), (0.84, 0.82, 0.76, 1.0), round=0.15)
    make_box("Mantel_Book_0", (cbx1 + 0.08, 4.25, 0.99), (0.15, 0.04, 0.17), (0.44, 0.20, 0.16, 1.0))
    make_box("Mantel_Book_1", (cbx1 + 0.08, 4.30, 0.985), (0.15, 0.035, 0.16), (0.24, 0.30, 0.40, 1.0))
    make_cyl("Mantel_Candle", (cbx1 + 0.08, 4.85, 0.96), 0.025, 0.11, (0.90, 0.86, 0.72, 1.0), segments=10)
    # a radiator under the window, the sill a ledge of paper
    rx, ry = WIN_X, ROOM_D - 0.22
    for k in range(9):
        make_box(f"Radiator_Fin_{k}", (rx - 0.40 + k * 0.10, ry, 0.42), (0.05, 0.16, 0.60), (0.74, 0.72, 0.66, 1.0))
    make_box("Radiator_Rail", (rx, ry, 0.16), (0.90, 0.10, 0.04), (0.60, 0.58, 0.52, 1.0))
    for k, fx in enumerate((-0.40, 0.40)):                # its feet
        make_box(f"Radiator_Foot_{k}", (rx + fx, ry, 0.07), (0.06, 0.12, 0.14), (0.60, 0.58, 0.52, 1.0))
    # ON the window's stool now (draft 2: it hung in the frame, 5 cm over nothing)
    make_box("Sill_Papers", (WIN_X + 0.30, ROOM_D - 0.18, WIN_Z - WIN_H / 2.0 - 0.05 + 0.025), (0.30, 0.13, 0.05), P.PAPER_AGED)


def build_desk():
    x, y, top = DESK_X, DESK_Y, DESK_H
    make_chamfer_box("Desk_Top", (x, y, top - 0.02), (DESK_W, DESK_D, 0.04), WOOD, chamfer=0.006)
    # left legs; a three-drawer pedestal on the right
    for k, (lx, ly) in enumerate([(-0.72, -0.31), (-0.72, 0.31)]):
        make_box(f"Desk_Leg_{k}", (x + lx, y + ly, (top - 0.04) / 2.0), (0.05, 0.05, top - 0.04), WOOD_DARK)
    px = x + DESK_W / 2.0 - 0.24
    make_box("Desk_Pedestal", (px, y, (top - 0.04) / 2.0), (0.44, DESK_D - 0.04, top - 0.04), WOOD)
    make_box("Desk_Modesty", (x - 0.24, y + DESK_D / 2.0 - 0.03, 0.46), (DESK_W - 0.55, 0.02, 0.50), WOOD_DARK)
    # (draft 3) a pencil drawer, a middle drawer and a deep file drawer — "the
    # bottom drawer ... Green hanging folders" (vol4_drawer); z centre, height
    face_y = y - (DESK_D - 0.04) / 2.0
    DRAWERS = ((0.58, 0.18), (0.40, 0.14), (0.17, 0.28))
    for k, (z, dh) in enumerate(DRAWERS):
        pull = 0.26 if k == 0 else 0.0                 # the top drawer: stuck, then gave
        # flush on the pedestal's face; the stuck top drawer runs back into the
        # pedestal as a real drawer does. The closed middle and file drawers
        # are `strip`ped by the views that pull them (dawn: every drawer)
        make_box(f"Desk_Drawer_{k}", (px, face_y - (0.024 + pull) / 2.0 + 0.01, z), (0.40, 0.024 + pull + 0.02, dh), WOOD_DARK)
        make_box(f"Desk_Drawer_{k}_Pull", (px, face_y - 0.024 - pull - 0.009, z), (0.10, 0.02, 0.018), (0.62, 0.54, 0.34, 1.0))
    # the open drawer's contents: rubber bands, dead nine-volts, the red string,
    # sand in the runners — and (draft 3, the meld seam) "in there, for no
    # good reason, a newspaper, a novel, and a toy soldier"
    dz, dy = 0.66, y - DESK_D / 2.0 - 0.06
    make_box("Drawer_Sand", (px, dy, dz - 0.005), (0.34, 0.12, 0.004), (0.80, 0.70, 0.50, 1.0))
    for k, (bx, bc) in enumerate([(-0.11, (0.70, 0.56, 0.38, 1.0)), (-0.06, (0.56, 0.42, 0.30, 1.0))]):
        make_cyl(f"Drawer_Bands_{k}", (px + bx, dy, dz + 0.004), 0.028, 0.006, bc, segments=10)
    for k in range(2):
        make_box(f"Drawer_9V_{k}", (px + 0.02 + k * 0.035, dy - 0.01, dz + 0.012), (0.026, 0.017, 0.048), (0.16, 0.16, 0.18, 1.0))
        make_box(f"Drawer_9V_{k}_Cap", (px + 0.02 + k * 0.035, dy - 0.01, dz + 0.04), (0.02, 0.012, 0.008), (0.70, 0.62, 0.36, 1.0))
    make_cyl("Drawer_String_Ball", (px + 0.12, dy, dz + 0.03), 0.032, 0.06, RED_STRING, segments=10)
    make_box("Drawer_Newspaper", (px - 0.08, y - 0.545, dz + 0.006), (0.19, 0.11, 0.012), P.NEWSPRINT)
    make_box("Drawer_Novel", (px + 0.10, y - 0.545, dz + 0.012), (0.16, 0.10, 0.024), (0.50, 0.24, 0.18, 1.0))
    make_box("Drawer_Novel_Pages", (px + 0.10, y - 0.545, dz + 0.0125), (0.152, 0.104, 0.018), P.PAPER_AGED)
    sold = (0.34, 0.42, 0.22, 1.0)                       # the toy soldier, lying on his side
    make_box("Drawer_Soldier_Body", (px - 0.03, y - 0.475, dz + 0.009), (0.040, 0.012, 0.016), sold)
    make_cyl("Drawer_Soldier_Head", (px - 0.0035, y - 0.475, dz + 0.009), 0.0065, 0.012, sold, axis='X', segments=8)
    make_box("Drawer_Soldier_Base", (px - 0.054, y - 0.475, dz + 0.009), (0.004, 0.020, 0.018), sold)
    build_open_drawers(px, face_y, DRAWERS)
    # on the desk: the screen and keyboard (2006), the lamp, the paper
    make_box("Monitor_Stand", (x + 0.10, y + 0.16, top + 0.01), (0.20, 0.16, 0.02), P.METAL_BLACK)
    make_box("Monitor_Neck", (x + 0.10, y + 0.18, top + 0.11), (0.05, 0.03, 0.20), P.METAL_BLACK)
    make_chamfer_box("Monitor", (x + 0.10, y + 0.18, top + 0.36), (0.46, 0.05, 0.34), (0.20, 0.20, 0.22, 1.0), chamfer=0.008)
    make_box("Monitor_Screen", (x + 0.10, y + 0.152, top + 0.37), (0.42, 0.004, 0.28), (0.20, 0.30, 0.42, 1.0))
    make_box("Keyboard", (x + 0.10, y - 0.14, top + 0.012), (0.44, 0.15, 0.02), (0.84, 0.82, 0.76, 1.0))
    make_box("Mouse", (x + 0.42, y - 0.14, top + 0.015), (0.06, 0.10, 0.03), (0.84, 0.82, 0.76, 1.0))
    # (draft 3) "The desk lamp has a round brass shade. Up close it looks like
    # a porthole." (meld kaleidoscope e) — it was a green banker's can
    lx, ly = x - 0.62, y + 0.18
    BRASS, BRASS_DK = (0.74, 0.58, 0.28, 1.0), (0.52, 0.40, 0.18, 1.0)
    make_lathe("Lamp_Base", (lx, ly, top), [(0.0, 0.0), (0.075, 0.0), (0.075, 0.012), (0.05, 0.026), (0.012, 0.034), (0.0, 0.034)], BRASS_DK, segments=16)
    make_cyl("Lamp_Neck", (lx, ly, top + 0.20), 0.008, 0.34, BRASS_DK, segments=6)
    make_box("Lamp_Arm", (lx + 0.095, ly, top + 0.37), (0.19, 0.012, 0.012), BRASS_DK)        # off the post itself
    make_cyl("Lamp_Shade_Stem", (lx + 0.19, ly, top + 0.357), 0.006, 0.014, BRASS_DK, segments=6)
    make_lathe("Lamp_Shade", (lx + 0.19, ly, top + 0.27),
               [(0.095, 0.0), (0.093, 0.018), (0.082, 0.042), (0.062, 0.064), (0.034, 0.078), (0.0, 0.084)], BRASS, segments=20)
    make_lathe("Lamp_Shade_Rim", (lx + 0.19, ly, top + 0.27), [(0.090, 0.0), (0.100, 0.0), (0.100, 0.008), (0.090, 0.008)],
               BRASS_DK, segments=20, loop=True)
    make_cyl("Lamp_Bulb", (lx + 0.19, ly, top + 0.30), 0.03, 0.04, (1.0, 0.92, 0.70, 1.0), segments=10)
    # "A kaleidoscope rolls out from under the zine. The cheap cardboard kind,
    # ducks printed on the paper, worn white at both ends." (meld kaleidoscope a)
    kx, ky, kr, kl = x + 0.035, y - 0.30, 0.021, 0.22
    make_cyl("Kaleidoscope", (kx, ky, top + kr), kr, kl - 0.04, (0.46, 0.66, 0.84, 1.0), axis='X', segments=12)
    for e in (-1, 1):
        make_cyl(f"Kaleidoscope_End_{e:+d}", (kx + e * (kl / 2.0 - 0.01), ky, top + kr), kr + 0.001, 0.02, (0.90, 0.88, 0.82, 1.0), axis='X', segments=12)
    for d in range(3):                                   # the ducks: yellow flecks on the blue
        make_box(f"Kaleidoscope_Duck_{d}", (kx - 0.06 + d * 0.06, ky - kr * 0.55, top + kr * 1.7), (0.016, 0.004, 0.010), (0.96, 0.82, 0.26, 1.0))
    for k in range(5):                                   # the stacks: scraps, stories, the zine
        make_box(f"Paper_Stack_{k}", (x - 0.42 + (k % 2) * 0.08, y - 0.08 - (k // 2) * 0.02, top + 0.012 + k * 0.012),
                 (0.22, 0.29, 0.010), P.PAPER if k % 2 == 0 else P.PAPER_AGED)
    make_box("Zine_Stack", (x - 0.15, y - 0.24, top + 0.02), (0.15, 0.21, 0.025), (0.78, 0.76, 0.70, 1.0))
    make_box("Folder_vii", (x + 0.52, y + 0.02, top + 0.016), (0.24, 0.31, 0.022), MANILA)
    make_cyl("Folder_vii_Pin", (x + 0.52, y + 0.12, top + 0.034), 0.008, 0.016, RED_STRING, segments=8)
    make_box("Folder_vii_Label", (x + 0.45, y + 0.02, top + 0.028), (0.07, 0.03, 0.001), P.PAPER)
    make_cyl("Mug", (x + 0.66, y - 0.20, top + 0.05), 0.04, 0.10, (0.22, 0.28, 0.40, 1.0), segments=12)
    make_cyl("Pen_Cup", (x + 0.66, y + 0.20, top + 0.06), 0.035, 0.12, (0.30, 0.28, 0.26, 1.0), segments=10)
    for k in range(3):
        make_cyl(f"Pen_{k}", (x + 0.655 + k * 0.01, y + 0.20, top + 0.15), 0.004, 0.14, (0.10, 0.12, 0.40, 1.0), segments=6)
    make_box("Stapler", (x - 0.30, y + 0.24, top + 0.02), (0.05, 0.16, 0.04), (0.30, 0.30, 0.34, 1.0))
    make_chair("Desk_Chair", x + 0.05, y - 0.78, yaw=0.0, wood=WOOD_DARK, seat_col=(0.30, 0.22, 0.16, 1.0))
    # the wastebasket, crumpled drafts
    make_cyl("Wastebasket", (x - 0.95, y - 0.30, 0.16), 0.13, 0.32, (0.26, 0.26, 0.28, 1.0), segments=12)
    for k, (bx, by) in enumerate([(-0.04, 0.02), (0.04, -0.03), (0.0, 0.05)]):
        make_chamfer_box(f"Crumple_{k}", (x - 0.95 + bx, y - 0.30 + by, 0.30 + k * 0.02), (0.07, 0.07, 0.06), P.PAPER, chamfer=0.02)
    make_chamfer_box("Crumple_Floor", (x - 0.70, y - 0.58, 0.03), (0.07, 0.07, 0.06), P.PAPER, chamfer=0.02)


def build_open_drawers(px, face_y, drawers):
    """(draft 3) The pulled drawers, each under an empty tagged with the views
    it shows in: "The bottom drawer sticks, then gives. Green hanging folders,
    the tabs typed ONEIRONAUTICS INC. ... Pitches and design docs, a story, a
    deck of cards. Games, mostly." (vol4_drawer, eleven scenes) and the dawn's
    "Every drawer pulled out" (curtain call). Built as open boxes — front,
    sides, floor — so the folders show from above; the part still inside the
    pedestal is not built."""
    from _props.geometry import make_box as _mb
    # the middle drawer: pulled 20 cm, a few loose papers in it (dawn only)
    z, dh = drawers[1]
    pull = 0.20
    _open_box("DrawerMidOpen", px, face_y, z, dh, pull)
    for k in range(3):
        _mb(f"DrawerMidOpen_Paper_{k}", (px - 0.06 + k * 0.05, face_y - 0.10 - k * 0.02, z - dh / 2.0 + 0.032 + k * 0.004),
            (0.21, 0.15, 0.003), P.PAPER if k % 2 else P.PAPER_AGED)
    # the file drawer: pulled 36 cm on its slides, the folders hanging in it
    z, dh = drawers[2]
    pull = 0.36
    _open_box("DrawerFileOpen", px, face_y, z, dh, pull)
    rail_z = z + dh / 2.0 - 0.02
    greens = [(0.38, 0.60, 0.36, 1.0), (0.32, 0.54, 0.34, 1.0), (0.42, 0.64, 0.40, 1.0)]   # light enough to read in the drawer's shade
    tabs_x = (-0.12, -0.04, 0.04, 0.12)
    n = 11
    for i in range(n):
        fy = face_y - 0.33 + i * 0.03
        _mb(f"DrawerFileOpen_Folder_{i}", (px, fy, rail_z - 0.115), (0.33, 0.004, 0.22), greens[i % 3])
        _mb(f"DrawerFileOpen_Folder_{i}_Bar", (px, fy, rail_z + 0.004), (0.366, 0.006, 0.008), (0.20, 0.22, 0.20, 1.0))
        _mb(f"DrawerFileOpen_Folder_{i}_Tab", (px + tabs_x[i % 4], fy, rail_z + 0.020), (0.055, 0.003, 0.024), (0.92, 0.92, 0.86, 1.0))
        if i in (2, 5, 8):                               # a fat one: a deck of cards, a design doc
            _mb(f"DrawerFileOpen_Folder_{i}_Papers", (px, fy + 0.008, rail_z - 0.10), (0.30, 0.010, 0.20), P.PAPER)
    try:
        import bpy
        for empty_name, prefix in (("DrawerMid__writers_desk_dawn", "DrawerMidOpen"),
                                   ("DrawerFile__writers_desk_drawer__writers_desk_dawn", "DrawerFileOpen")):
            empty = bpy.data.objects.new(empty_name, None)
            bpy.context.scene.collection.objects.link(empty)
            for obj in list(bpy.data.objects):
                if obj is not empty and obj.parent is None and obj.name.startswith(prefix):
                    obj.parent = empty
    except Exception:
        pass


def _open_box(nm, px, face_y, z, dh, pull):
    """A drawer pulled `pull` m out of the pedestal face at `face_y` (-y is
    out): the front, the two sides and the floor of the part that shows."""
    w, t = 0.40, 0.016
    z0 = z - dh / 2.0
    make_box(f"{nm}_Front", (px, face_y - pull - 0.012, z), (w, 0.024, dh), WOOD_DARK)
    make_box(f"{nm}_Front_Pull", (px, face_y - pull - 0.033, z + dh * 0.20), (0.10, 0.02, 0.018), (0.62, 0.54, 0.34, 1.0))
    for sd in (-1, 1):
        make_box(f"{nm}_Side_{sd:+d}", (px + sd * (w / 2.0 - t / 2.0), face_y - pull / 2.0, z0 + 0.01 + (dh - 0.04) / 2.0),
                 (t, pull, dh - 0.04), WOOD)
    make_box(f"{nm}_Floor", (px, face_y - pull / 2.0, z0 + 0.016), (w - 2 * t, pull, 0.012), WOOD)


def build_corkboard():
    """Over the desk: cork in a thin frame, four clippings, pale gaps where
    something ought to hang, red string pin to pin."""
    bx, bw, bh, bz = DESK_X - 0.05, 1.30, 0.86, 1.62
    face = ROOM_D - 0.10 - 0.012
    make_box("Board_Frame", (bx, face + 0.004, bz), (bw + 0.06, 0.02, bh + 0.06), WOOD_DARK)
    make_box("Board_Cork", (bx, face - 0.008, bz), (bw, 0.012, bh), CORK)
    clips = [(-0.46, 0.20, 0.22, 0.28, P.NEWSPRINT), (-0.12, -0.18, 0.26, 0.18, P.NEWSPRINT),
             (0.20, 0.16, 0.20, 0.26, P.PAPER), (0.46, -0.20, 0.18, 0.24, (0.92, 0.90, 0.84, 1.0))]
    for k, (cx, cz, w, h, col) in enumerate(clips):
        make_box(f"Board_Clipping_{k}", (bx + cx, face - 0.016, bz + cz), (w, 0.003, h), col)
        make_cyl(f"Board_Pin_{k}", (bx + cx, face - 0.024, bz + cz + h / 2.0 - 0.03), 0.014, 0.018, RED_STRING,
                 axis='Y', segments=8)
    for k, (gx, gz, w, h) in enumerate([(-0.48, -0.24, 0.20, 0.16), (0.02, 0.30, 0.18, 0.14), (0.38, 0.32, 0.14, 0.12)]):
        make_box(f"Board_Gap_{k}", (bx + gx, face - 0.0145, bz + gz), (w, 0.001, h), CORK_PALE)
        for e, (ex, ez, ew, eh) in enumerate([(0, h / 2.0, w, 0.006), (0, -h / 2.0, w, 0.006), (-w / 2.0, 0, 0.006, h), (w / 2.0, 0, 0.006, h)]):
            make_box(f"Board_Gap_{k}_Edge_{e}", (bx + gx + ex, face - 0.015, bz + gz + ez), (ew, 0.001, eh), (0.52, 0.38, 0.24, 1.0))   # the faded cork stops at a line
    # the string: pin to pin, right to left ("You tie off on the zine first,
    # because it's farthest out"), a little slack between pins
    from _props.geometry import make_tube, catenary
    pins = [(bx + c[0], bz + c[1] + c[3] / 2.0 - 0.03) for c in clips]
    order = [3, 2, 1, 0]
    for k in range(len(order) - 1):
        (x0, z0), (x1, z1) = pins[order[k]], pins[order[k + 1]]
        yy = face - 0.030
        make_tube(f"Board_String_{k}", catenary((x0, yy, z0), (x1, yy, z1), 0.025, n=8), 0.0035, RED_STRING, segments=5)


def build_dawn_2026_10():
    """(DRAFT 4, 2026-10-30) curtain call's dawn, each piece under an empty
    tagged `__writers_desk_dawn` so it exists in that view only:
      "Four folding chairs, church basement, one with a lean" — they were
          not here before: three open on the rug facing the desk, the fourth
          folded and leaning on the W wall;
      "the red string gone brown" — a brown string over the same pins (the
          dawn view strips the red one, `Board_String_`);
      "Through the glass the street. A car idling at the curb, parking
          lights on, a cardboard sign wedged against the windshield" (RUTA 77,
          the por puesto) — at the far curb, where the lens sees it through
          the N window over the sill;
      the desk chair pushed back off the pulled drawers (the dawn view strips
          `Desk_Chair`)."""
    from _props.geometry import make_rot_box, make_tube, catenary
    from _props.furniture import make_chair
    from _props.vehicles import make_car
    METAL = (0.62, 0.58, 0.48, 1.0)                     # church-basement tan
    for k, (cx, cy, yaw) in enumerate(((-1.20, 3.10, 0.10), (-0.45, 2.95, 0.0), (0.30, 3.05, -0.10))):
        import math as _m
        c, s_ = _m.cos(yaw), _m.sin(yaw)
        def at(fx, fy, z):
            return (cx + fx * c + fy * s_, cy - fx * s_ + fy * c, z)
        make_rot_box(f"Dawn_Fold_Chair_{k}_Seat", at(0.0, 0.0, 0.455), (0.40, 0.38, 0.03), METAL, yaw=-yaw)
        for side in (-1, 1):
            make_rot_box(f"Dawn_Fold_Chair_{k}_Front_{side:+d}", at(side * 0.18, 0.16, 0.22), (0.022, 0.022, 0.44), METAL, yaw=-yaw)
            # rear leg stops under the seat; the back upright stands on the seat's top
            make_rot_box(f"Dawn_Fold_Chair_{k}_Rear_{side:+d}", at(side * 0.18, -0.17, 0.22), (0.022, 0.022, 0.44), METAL, yaw=-yaw)
            make_rot_box(f"Dawn_Fold_Chair_{k}_Upright_{side:+d}", at(side * 0.18, -0.17, 0.665), (0.022, 0.022, 0.39), METAL, yaw=-yaw)
        make_rot_box(f"Dawn_Fold_Chair_{k}_Back", at(0.0, -0.17, 0.74), (0.336, 0.02, 0.20), METAL, yaw=-yaw)
        make_rot_box(f"Dawn_Fold_Chair_{k}_Brace", at(0.0, 0.16, 0.12), (0.34, 0.016, 0.016), METAL, yaw=-yaw)
    # the fourth, folded, leaning on the W wall between the bed and the nightstand
    th = 0.20
    make_rot_box("Dawn_Fold_Chair_3_Folded", (-ROOM_W / 2.0 + 0.10 + 0.88 * math.sin(th) / 2.0 + 0.025, 2.50, 0.88 * math.cos(th) / 2.0),
                 (0.04, 0.42, 0.88), METAL, roll=th)
    # the string gone brown, over the same pins, a hair in front of the red
    bx, bz = DESK_X - 0.05, 1.62
    face = ROOM_D - 0.10 - 0.012
    clips = [(-0.46, 0.20, 0.28), (-0.12, -0.18, 0.18), (0.20, 0.16, 0.26), (0.46, -0.20, 0.24)]
    pins = [(bx + cx, bz + cz + h / 2.0 - 0.03) for cx, cz, h in clips]
    for k, (a, b) in enumerate(((3, 2), (2, 1), (1, 0))):
        (x0, z0), (x1, z1) = pins[a], pins[b]
        yy = face - 0.040
        make_tube(f"Dawn_Board_StringBrown_{k}", catenary((x0, yy, z0), (x1, yy, z1), 0.028, n=8), 0.0035, (0.42, 0.26, 0.16, 1.0), segments=5)
    # the desk chair pushed back and turned, off the pulled drawers
    make_chair("Dawn_Desk_Chair", DESK_X - 0.55, DESK_Y - 1.20, yaw=0.5, wood=WOOD_DARK, seat_col=(0.30, 0.22, 0.16, 1.0))
    # the por puesto at the far curb, idling, parking lights on, the sign in the windshield
    cx, cy, zc = 3.6, ROOM_D + 15.4, -3.2 - 0.03 + 0.025
    L = 4.5
    make_car("Dawn_Car", cx, cy, L, (0.82, 0.78, 0.66, 1.0), along="X", z0=zc)
    for sgn in (-1, 1):
        make_box(f"Dawn_Car_Park_Light_F_{sgn:+d}", (cx + L / 2.0 + 0.012, cy + sgn * 0.66, zc + 0.66), (0.025, 0.14, 0.06), (1.0, 0.70, 0.24, 1.0))
        make_box(f"Dawn_Car_Park_Light_R_{sgn:+d}", (cx - L / 2.0 - 0.012, cy + sgn * 0.66, zc + 0.80), (0.025, 0.16, 0.08), (0.90, 0.16, 0.12, 1.0))
    make_box("Dawn_Car_Sign", (cx + L / 2.0 - 1.45, cy - 0.30, zc + 1.12), (0.02, 0.48, 0.24), (0.70, 0.56, 0.36, 1.0))
    try:
        import bpy
        for empty_name, prefix in (("DawnChairs__writers_desk_dawn", "Dawn_Fold_Chair"),
                                   ("DawnString__writers_desk_dawn", "Dawn_Board_StringBrown"),
                                   ("DawnDeskChair__writers_desk_dawn", "Dawn_Desk_Chair"),
                                   ("DawnCar__writers_desk_dawn", "Dawn_Car")):
            empty = bpy.data.objects.new(empty_name, None)
            bpy.context.scene.collection.objects.link(empty)
            for obj in list(bpy.data.objects):
                if obj is not empty and obj.parent is None and obj.name.startswith(prefix):
                    obj.parent = empty
    except Exception:
        pass


def build_bed_and_books():
    # head against Wall_W: the bed lies along x, so its centre is half its length off the wall face
    make_bed("Bed", -ROOM_W / 2.0 + 0.10 + 1.95 / 2.0 + 0.02, 1.65, head="-X", w=1.0, d=1.95)
    make_box("Nightstand", (-ROOM_W / 2.0 + 0.30, 3.00, 0.28), (0.40, 0.40, 0.56), WOOD)
    make_box("Nightstand_Book", (-ROOM_W / 2.0 + 0.30, 3.00, 0.575), (0.14, 0.21, 0.03), (0.50, 0.22, 0.18, 1.0))
    make_cyl("Nightstand_Glass", (-ROOM_W / 2.0 + 0.40, 3.10, 0.61), 0.03, 0.10, (0.62, 0.70, 0.72, 0.5), segments=8)
    # two tall bookcases on the E wall
    for s in range(2):
        sy = 1.90 + s * 1.00
        sx = ROOM_W / 2.0 - 0.18
        make_box(f"Shelf_{s}_Back", (sx + 0.15, sy, 1.00), (0.02, 0.90, 2.00), WOOD_DARK)
        for side in (-1, 1):
            make_box(f"Shelf_{s}_Side_{'S' if side < 0 else 'N'}", (sx, sy + side * 0.44, 1.00), (0.30, 0.02, 2.00), WOOD)
        for b in range(6):
            z = 0.05 + b * 0.38
            make_box(f"Shelf_{s}_Board_{b}", (sx, sy, z), (0.30, 0.86, 0.02), WOOD)
            if b < 5:
                n = 9 - (b + s) % 3
                for i in range(n):
                    h = 0.20 + ((i * 7 + b * 3 + s) % 5) * 0.025
                    col = P.SNACK_TINTS[(i + b + s) % len(P.SNACK_TINTS)]
                    col = (col[0] * 0.7, col[1] * 0.7, col[2] * 0.7, 1.0)
                    make_box(f"Shelf_{s}_Book_{b}_{i}", (sx - 0.02, sy - 0.38 + i * 0.085, z + 0.01 + h / 2.0),
                             (0.20, 0.06, h), col)
    # boxes of zines and a crate of records under the window side
    for k in range(2):                       # (draft 2) two high: the E window's stool is above them
        make_box(f"Archive_Box_{k}", (ROOM_W / 2.0 - 0.30, 4.30 + (k % 2) * 0.05, 0.16 + k * 0.30), (0.34, 0.44, 0.30),
                 (0.70, 0.60, 0.42, 1.0))
    make_box("Rug", (-0.30, 2.60, 0.004), (2.20, 1.60, 0.008), (0.34, 0.24, 0.20, 1.0))
    make_faded_poster("Poster_W_0", (-ROOM_W / 2.0 + 0.1035, 3.20, 1.65), into_room=+1)
    make_faded_poster("Poster_W_1", (-ROOM_W / 2.0 + 0.5035, 4.50, 1.65), into_room=+1)    # on the chimney breast


def build_infra():
    make_cyl("Ceiling_Fixture", (0.0, ROOM_D / 2.0, CEIL - 0.06), 0.18, 0.10, (0.92, 0.88, 0.74, 1.0), segments=12)
    make_smoke_detector("Smoke", (-1.0, ROOM_D / 2.0, CEIL))
    wear = (COL_FLOOR[0] * 0.86, COL_FLOOR[1] * 0.86, COL_FLOOR[2] * 0.86, 1.0)
    make_traffic_wear("Wear_Door_To_Desk", [(1.45, 0.5), (DESK_X + 0.05, DESK_Y - 1.0)], width=0.6, tint=wear)
    make_floor_stain("Stain_Chair", (DESK_X + 0.05, DESK_Y - 0.80), radius=0.30, tint=wear)
    pw = PAL_WALL["wall"]
    band = (pw[0] * 0.90, pw[1] * 0.90, pw[2] * 0.88, 1.0)
    for nm, x, a in (("Band_W", -ROOM_W / 2.0 + 0.105, 'Y'), ("Band_E", ROOM_W / 2.0 - 0.105, 'Y')):
        make_wall_tint_band(nm, (x, ROOM_D / 2.0, 0.0), length=ROOM_D - 0.4, axis=a, band_z=CEIL - 0.16, tint=band)
    make_threshold("Threshold_Door", (1.45, 0.10), width=0.9, axis='X')
    make_light_switch("Switch_Door", (0.85, 0.0), axis='X', face_sign=1, aged=True)
    make_wall_outlet("Outlet_Desk", (DESK_X - 0.55, ROOM_D), axis='X', face_sign=-1, aged=True)
    make_wall_outlet("Outlet_Bed", (-ROOM_W / 2.0, 2.90), axis='Y', face_sign=1, aged=True)


def main():
    clear_scene()
    build_shell()
    build_desk()
    build_corkboard()
    build_bed_and_books()
    build_infra()
    # through the window: the street (curtain call's car is build_dawn_2026_10's)
    make_view("View_N", "N", ROOM_D, 0.0, kind="front", ground_z=-3.2, seed=11)   # a second-floor room over a residential street
    make_view("View_E", "E", ROOM_W / 2.0, WINE_Y, kind="side", ground_z=-3.2, seed=4)   # (draft 2) the side street
    build_dawn_2026_10()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/writers_desk.glb"))
    print(f"\n[build_writers_desk] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
