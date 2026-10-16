"""VOL 5 · Montreal Apartment — winter scene cameo.
Small Mile-End apartment: radiator under window, hardwood floors,
heavy curtains, French-press on the counter, books everywhere.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.furniture import make_lamp
from _props.geometry import clear_scene, make_box, make_cyl, export_glb, make_chamfer_box
from _props.structure import make_floor, make_wall, make_ceiling, make_window, make_crown_molding
from _props.store_fixtures import make_counter, make_counter_bullnose
from _props.decor import make_wall_clock, make_faded_poster, make_floor_plant
from _props.safety import make_smoke_detector, make_fluorescent_tube_fixture
from _props.detail import (make_floor_stain, make_light_switch, make_threshold, make_traffic_wear, make_wall_outlet, make_wall_tint_band)
from _props.objects import make_mug, make_plate, make_bowl

PAL = {"wall": (0.92, 0.88, 0.78, 1.0), "baseboard": (0.42, 0.32, 0.22, 1.0)}
COL_FLOOR = (0.62, 0.46, 0.30, 1.0); COL_SEAM = (0.32, 0.22, 0.14, 1.0)
COL_WOOD = (0.42, 0.30, 0.18, 1.0); COL_CURTAIN = (0.52, 0.32, 0.32, 1.0)
COL_RADIATOR = (0.86, 0.80, 0.72, 1.0); COL_BOOK_SPINES = [(0.62, 0.32, 0.30, 1.0), (0.42, 0.52, 0.62, 1.0), (0.56, 0.48, 0.32, 1.0), (0.32, 0.42, 0.32, 1.0)]
ROOM_W = 6.0; ROOM_D = 5.0; CEIL = 2.80

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, ax, bb in [("Wall_W", -ROOM_W/2.0, 'Y', +1), ("Wall_E", +ROOM_W/2.0, 'Y', -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis=ax, palette=PAL, baseboard_face_sign=bb)
    # the north wall CUT around the window (x -1.1..1.1, z 0.6..2.6) — it was
    # solid behind the pane, so the alley the chapter looks at was a wall
    # (2026-10-03): two piers, a spandrel under the sill, a lintel over it
    make_wall("Wall_N_Pier_W", (-2.15, ROOM_D, 0), length=2.10, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_N_Pier_E", (+2.15, ROOM_D, 0), length=2.10, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_box("Wall_N_Spandrel", (0.0, ROOM_D, 0.30), (2.20, 0.20, 0.60), PAL["wall"])
    make_box("Wall_N_Spandrel_Base", (0.0, ROOM_D - 0.106, 0.08), (2.20, 0.012, 0.16), PAL["baseboard"])
    make_box("Wall_N_Lintel", (0.0, ROOM_D, CEIL - 0.10), (2.20, 0.20, 0.20), PAL["wall"])
    make_wall("Wall_S_W", (-2.0, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+2.0, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, with_grid=False)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10),("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})
    # Tall north window with snow-light through
    # on the wall's room face, glass in front of the frame (2026-09-24: frame and glass
    # were offset from the wall's CENTRE line — inside the wall, never visible)
    # (2026-10-03: the "frame" was a solid steel PLATE behind the glass — the
    # alley the chapter looks at was never visible; a frame is four bars
    # and two mullions)
    for nm, cx, cz, w, h in (("Window_N_Frame_T", 0.0, 2.57, 2.20, 0.06), ("Window_N_Frame_B", 0.0, 0.63, 2.20, 0.06),
                             ("Window_N_Frame_L", -1.07, 1.60, 0.06, 2.00), ("Window_N_Frame_R", 1.07, 1.60, 0.06, 2.00),
                             ("Window_N_Mullion_V", 0.0, 1.60, 0.04, 1.88), ("Window_N_Mullion_H", 0.0, 1.60, 2.08, 0.04)):
        make_box(nm, (cx, ROOM_D-0.12, cz), (w, 0.04, h), P.METAL_STEEL)
    make_box("Window_N_Glass", (0.0, ROOM_D-0.1425, 1.60), (2.00, 0.005, 1.80), (0.78, 0.84, 0.92, 0.22))   # (2026-10-03: glass is glass now — at 0.65 the alley was a pale wash; the brick, the moss and the drainpipe show)
    # Heavy curtains either side
    for cs in (-1, +1):
        make_box(f"Curtain_{cs:+d}", (cs*1.30, ROOM_D-0.08, 1.60), (0.20, 0.06, 2.00), COL_CURTAIN)

COL_SOFA = (0.46, 0.36, 0.42, 1.0); COL_CHAIR = (0.42, 0.44, 0.40, 1.0)
COL_RUG = (0.52, 0.28, 0.26, 1.0); COL_THROW = (0.72, 0.58, 0.34, 1.0)

def build_living():
    # Living area rug
    make_box("Rug", (-0.70, 1.90, 0.015), (2.5, 2.3, 0.02), COL_RUG)
    make_box("Rug_Border", (-0.70, 1.90, 0.018), (2.3, 2.1, 0.008), (0.64, 0.40, 0.34, 1.0))
    # Sofa facing north toward the snow-lit window (base + back + arms +
    # cushions + legs + a tossed winter throw).
    sx, sy = -0.70, 1.15
    make_box("Sofa_Base", (sx, sy, 0.30), (1.70, 0.85, 0.18), COL_SOFA)
    make_box("Sofa_Back", (sx, sy-0.42, 0.62), (1.70, 0.18, 0.52), COL_SOFA)
    for ax in (-0.85, 0.85):
        make_box(f"Sofa_Arm_{'L' if ax<0 else 'R'}", (sx+ax, sy, 0.44), (0.18, 0.85, 0.34), COL_SOFA)
    for ci in range(3):
        make_box(f"Sofa_SeatCushion_{ci}", (sx-0.55+ci*0.55, sy+0.06, 0.42), (0.50, 0.70, 0.14), (0.52, 0.42, 0.48, 1.0))
        make_box(f"Sofa_BackCushion_{ci}", (sx-0.55+ci*0.55, sy-0.34, 0.66), (0.48, 0.14, 0.40), (0.52, 0.42, 0.48, 1.0))
    for i, (lx, ly) in enumerate([(-0.78,-0.38),(0.78,-0.38),(-0.78,0.38),(0.78,0.38)]):
        make_box(f"Sofa_Leg_{i}", (sx+lx, sy+ly, 0.12), (0.06, 0.06, 0.24), COL_WOOD)
    make_box("Sofa_Throw", (sx+0.5, sy+0.10, 0.50), (0.60, 0.66, 0.10), COL_THROW)
    # Coffee table north of the sofa, on the rug
    tx, ty = -0.70, 2.45
    make_box("Coffee_Top", (tx, ty, 0.42), (1.10, 0.60, 0.05), COL_WOOD)
    for i, (lx, ly) in enumerate([(-0.50,-0.24),(0.50,-0.24),(-0.50,0.24),(0.50,0.24)]):
        make_box(f"Coffee_Leg_{i}", (tx+lx, ty+ly, 0.21), (0.05, 0.05, 0.42), COL_WOOD)
    make_box("Coffee_Books", (tx-0.28, ty, 0.48), (0.30, 0.24, 0.06), COL_BOOK_SPINES[1])
    make_cyl("Coffee_Mug", (tx+0.28, ty+0.08, 0.49), 0.05, 0.10, (0.62, 0.32, 0.30, 1.0), segments=10)
    # Armchair to the west, angled toward the coffee table
    ax, ay = -2.30, 2.30
    make_box("Chair_Base", (ax, ay, 0.32), (0.72, 0.76, 0.16), COL_CHAIR)
    make_box("Chair_Back", (ax-0.30, ay, 0.66), (0.16, 0.76, 0.52), COL_CHAIR)
    for arm in (-0.42, 0.42):
        make_box(f"ArmC_Arm_{'S' if arm<0 else 'N'}", (ax, ay+arm, 0.46), (0.72, 0.14, 0.30), COL_CHAIR)
    make_box("Chair_Cushion", (ax, ay, 0.44), (0.56, 0.62, 0.14), (0.50, 0.52, 0.48, 1.0))
    make_box("Chair_Throw", (ax-0.10, ay+0.30, 0.52), (0.40, 0.24, 0.08), COL_THROW)
    for i, (lx, ly) in enumerate([(-0.30,-0.32),(0.30,-0.32),(-0.30,0.32),(0.30,0.32)]):
        make_box(f"ArmC_Leg_{i}", (ax+lx, ay+ly, 0.12), (0.06, 0.06, 0.24), COL_WOOD)
    # Bookshelf east wall — overflowing
    sx2 = +2.66   # its back on the E wall's face (2026-09-25: 16 cm off it)
    # (2026-10-03: seven identical 12 cm books a shelf read as a rack of boxes;
    # a shelf is a run of thicknesses and heights, a lean at the end of a row,
    # a few laid flat — the 20 cm north of each run holds the collection)
    import random as _r
    rnd = _r.Random(27)
    for shf in range(6):
        sz = 0.20 + shf*0.40
        make_box(f"BookShelf_{shf}", (sx2, 1.55, sz), (0.40, 1.40, 0.02), COL_WOOD)
        y = 1.55 - 0.66
        bi = 0
        while y < 1.86:   # the run ends short of the flats and the collection at 2.14
            t = rnd.choice((0.022, 0.028, 0.034, 0.042, 0.050))
            h = rnd.choice((0.19, 0.22, 0.25, 0.28, 0.31))
            d = rnd.uniform(0.14, 0.22)
            spine = COL_BOOK_SPINES[(shf*5+bi*3)%len(COL_BOOK_SPINES)]
            make_box(f"Book_{shf}_{bi}", (sx2 + rnd.uniform(-0.02, 0.02), y + t/2.0, sz + 0.01 + h/2.0), (d, t, h), spine)
            y += t + rnd.choice((0.0, 0.0, 0.0, 0.006))
            bi += 1
        if shf in (1, 4):   # two laid flat on the run's end
            for k in range(2):
                make_box(f"Book_{shf}_Flat_{k}", (sx2, 1.96, sz + 0.01 + 0.018 * k + 0.009), (0.16, 0.11, 0.018), COL_BOOK_SPINES[(shf+k)%len(COL_BOOK_SPINES)])
    make_box("BookShelf_Side_S", (sx2+0.02, 0.83, 1.30), (0.44, 0.04, 2.60), COL_WOOD)   # to the floor (2026-09-22: 20 cm up)
    make_box("BookShelf_Side_N", (sx2+0.02, 2.27, 1.30), (0.44, 0.04, 2.60), COL_WOOD)

def build_dining_nook():
    # Small bistro dining nook east-centre, between bookshelf & kitchen.
    tx, ty = 1.35, 3.55
    make_cyl("Dine_Pedestal", (tx, ty, 0.36), 0.06, 0.72, COL_WOOD, segments=8)
    make_cyl("Dine_Foot", (tx, ty, 0.03), 0.28, 0.05, (0.32, 0.22, 0.14, 1.0), segments=12)
    make_cyl("Dine_Top", (tx, ty, 0.74), 0.42, 0.05, COL_WOOD, segments=16)
    make_cyl("Dine_Plate", (tx-0.14, ty, 0.78), 0.10, 0.02, (0.86, 0.84, 0.80, 1.0), segments=12)
    make_cyl("Dine_Mug", (tx+0.16, ty+0.10, 0.80), 0.045, 0.09, (0.42, 0.52, 0.62, 1.0), segments=10)
    for ci, (cx3, cy3) in enumerate([(tx-0.62, ty), (tx+0.62, ty)]):
        make_box(f"Dine_Chair_{ci}_Seat", (cx3, cy3, 0.46), (0.40, 0.40, 0.05), COL_WOOD)
        bxo = -0.18 if cx3 < tx else 0.18
        make_box(f"Dine_Chair_{ci}_Back", (cx3+bxo, cy3, 0.72), (0.04, 0.40, 0.46), COL_WOOD)
        for i, (lx, ly) in enumerate([(-0.16,-0.16),(0.16,-0.16),(-0.16,0.16),(0.16,0.16)]):
            make_box(f"Dine_Chair_{ci}_Leg_{i}", (cx3+lx, cy3+ly, 0.22), (0.04, 0.04, 0.44), COL_WOOD)

def build_floor_lamp():
    # Arc floor lamp in the SW corner beside the sofa.
    lx, ly = -2.72, 0.85
    make_cyl("FloorLamp_Base", (lx, ly, 0.03), 0.16, 0.06, P.METAL_BLACK, segments=12)
    make_cyl("FloorLamp_Pole", (lx, ly, 0.95), 0.02, 1.80, P.METAL_STEEL, segments=8)
    make_cyl("FloorLamp_Shade", (lx, ly, 1.80), 0.16, 0.22, (0.94, 0.86, 0.62, 1.0), segments=12)

def build_kitchenette():
    # Tiny corner kitchen N-E
    cx, cy = +2.5, 4.5
    top_z = make_counter("Kitch", (cx, cy, 0.0), length=1.20, depth=0.70, height=0.92, palette={"formica": (0.74, 0.62, 0.42, 1.0), "top": (0.32, 0.22, 0.14, 1.0), "kick": (0.32, 0.22, 0.14, 1.0)})
    make_counter_bullnose("Kitch", (cx-0.35, cy, top_z), length=1.20, palette={"top": (0.32, 0.22, 0.14, 1.0)})
    # French press
    make_cyl("FrenchPress_Body", (cx-0.20, cy, top_z+0.10), 0.06, 0.20, (0.78, 0.84, 0.86, 0.55))   # on the top
    make_cyl("FrenchPress_Plunger", (cx-0.20, cy, top_z+0.26), 0.012, 0.10, P.METAL_STEEL)
    make_cyl("FrenchPress_Lid", (cx-0.20, cy, top_z+0.30), 0.06, 0.02, P.METAL_BLACK)
    # Coffee in press
    make_cyl("FrenchPress_Coffee", (cx-0.20, cy, top_z+0.08), 0.05, 0.10, (0.18, 0.10, 0.06, 1.0))
    # Mug
    make_cyl("Mug", (cx+0.05, cy, top_z+0.06), 0.05, 0.10, (0.62, 0.32, 0.30, 1.0))

def build_radiator_under_window():
    # Cast-iron radiator under the N window
    rx, ry = 0.0, ROOM_D-0.20
    for fi in range(6):
        make_box(f"Radiator_Fin_{fi}", (rx-0.55+fi*0.22, ry, 0.40), (0.06, 0.16, 0.80), COL_RADIATOR)
    make_box("Radiator_Top", (rx, ry, 0.82), (1.40, 0.20, 0.04), COL_RADIATOR)
    make_box("Radiator_Pipe", (rx-0.70, ry+0.06, 0.30), (0.04, 0.06, 0.60), COL_RADIATOR)

def build_decor():
    make_wall_clock("Clock", (-2.900, 2.5, 2.10), frozen_hour=10, frozen_min=33, facing='+X')
    make_faded_poster("Poster", (2.8965, 0.8, 1.60), into_room=-1)
    make_faded_poster("Art_W", (-2.8965, 1.1, 1.65), palette={"body": (0.52, 0.56, 0.60, 1.0)}, into_room=+1)
    make_floor_plant("Plant", (-2.0, 4.0, 0.0))
    # Stack of books on floor
    for bi in range(5):
        col = COL_BOOK_SPINES[bi%len(COL_BOOK_SPINES)]
        make_box(f"FloorBook_{bi}", (-1.20, 0.80, 0.04+bi*0.05), (0.30, 0.22, 0.05), col)

def build_ceiling_infra():
    # Mile-End apartment: one warm dome, no shop tubes
    make_cyl("Ceiling_Dome", (0.0, 2.5, CEIL-0.10), 0.15, 0.14, (0.94, 0.88, 0.70, 1.0), segments=12)
    make_smoke_detector("Smoke", (0.9, 2.5, CEIL))


def build_hero_props():
    """2026-08-03 tail pass: John's desk (its paper drifts), the
    narwhal mug on its coaster, the gurgling drip coffee maker, the
    notebook ziggurats, the fridge + dish rack, and the ALLEY the
    window actually looks at (bins, mossy brick, the drainpipe)."""
    wood = (0.42, 0.30, 0.20, 1.0)
    # The desk, W wall, task chair — everything happens here
    make_box("Desk_Top", (-2.20, 3.40, 0.74), (1.40, 0.70, 0.05), wood)
    for lx, ly in ((-2.82, 3.10), (-1.58, 3.10), (-2.82, 3.70), (-1.58, 3.70)):
        make_box(f"Desk_Leg_{lx:.2f}_{ly:.2f}", (lx, ly, 0.37), (0.05, 0.05, 0.72), wood)
    make_box("Desk_Paper_Drift_A", (-2.45, 3.30, 0.775), (0.45, 0.35, 0.04), (0.88, 0.86, 0.80, 1.0))
    make_box("Desk_Paper_Drift_B", (-1.95, 3.55, 0.79), (0.38, 0.30, 0.06), (0.84, 0.82, 0.74, 1.0))
    make_box("Desk_Phone", (-2.05, 3.20, 0.775), (0.08, 0.15, 0.012), (0.12, 0.12, 0.14, 1.0))
    make_box("Task_Chair", (-1.50, 3.40, 0.46), (0.44, 0.44, 0.05), (0.28, 0.28, 0.30, 1.0))
    make_cyl("Task_Chair_Post", (-1.50, 3.40, 0.22), 0.03, 0.44, (0.20, 0.20, 0.22, 1.0), segments=8)   # pedestal + base (2026-09-09)
    make_cyl("Task_Chair_Base", (-1.50, 3.40, 0.02), 0.28, 0.04, (0.20, 0.20, 0.22, 1.0), segments=12)
    make_box("Task_Chair_Back", (-1.28, 3.40, 0.76), (0.05, 0.44, 0.55), (0.24, 0.24, 0.26, 1.0))   # from the seat (2026-09-22)
    # THE NARWHAL MUG on its coaster
    make_cyl("Coaster", (-2.55, 3.55, 0.772), 0.06, 0.008, (0.34, 0.26, 0.20, 1.0), segments=10)
    make_cyl("Narwhal_Mug", (-2.55, 3.55, 0.82), 0.045, 0.09, (0.55, 0.72, 0.80, 1.0), segments=10)
    make_box("Narwhal_Decal", (-2.51, 3.55, 0.83), (0.012, 0.045, 0.04), (0.90, 0.92, 0.94, 1.0))
    make_cyl("Narwhal_Tusk", (-2.49, 3.53, 0.86), 0.006, 0.04, (0.94, 0.92, 0.86, 1.0), segments=5)
    # The drip coffee maker (a French press does not gurgle)
    make_box("Drip_Maker", (2.80, 4.50, 1.10), (0.28, 0.28, 0.36), (0.20, 0.20, 0.22, 1.0))
    make_cyl("Drip_Carafe", (2.80, 4.42, 1.00), 0.09, 0.16, (0.45, 0.38, 0.28, 0.7), segments=10)
    # Notebook ziggurats on every available surface
    # (2026-09-22: stack 1 hung 42 cm up on nothing — on the floor by the
    # sofa now; stack 2 was past the counter's west edge)
    # (2026-09-24: stack 0 at y 2.9 stood 2 cm off the desk's front edge)
    for zi, (zx, zy, zz, n) in enumerate(((-2.65, 3.20, 0.78, 4), (0.4, 2.2, 0.015, 3), (2.25, 4.75, 0.995, 3))):
        for k in range(n):
            make_box(f"Ziggurat_{zi}_{k}", (zx + 0.01 * (k % 2), zy, zz + k * 0.035),
                     (0.20 - 0.02 * k, 0.26 - 0.02 * k, 0.03),
                     [(0.62, 0.24, 0.24, 1.0), (0.24, 0.42, 0.52, 1.0), (0.72, 0.62, 0.30, 1.0)][k % 3])
    # Fridge + dish rack
    make_box("Fridge", (2.72, 3.4, 0.85), (0.60, 0.60, 1.70), (0.85, 0.84, 0.80, 1.0))
    make_box("Dish_Rack", (2.35, 4.75, 0.98), (0.30, 0.26, 0.05), (0.60, 0.62, 0.63, 1.0))
    # THE ALLEY beyond the N window: opposite brick, moss, the
    # graffiti-scarred drainpipe, recycling bins
    make_box("Alley_Brick", (0.0, 7.4, 1.8), (7.0, 0.2, 3.6), (0.42, 0.30, 0.26, 1.0))
    make_box("Alley_Moss", (-1.2, 7.28, 0.9), (1.6, 0.03, 1.2), (0.30, 0.40, 0.26, 1.0))
    make_cyl("Alley_Drainpipe", (1.4, 7.25, 1.8), 0.06, 3.6, (0.36, 0.38, 0.40, 1.0), segments=8)
    make_box("Drainpipe_Graffiti", (1.33, 7.20, 1.3), (0.02, 0.03, 0.35), (0.72, 0.32, 0.52, 1.0))
    for bi, bx in enumerate((-0.8, 0.2)):
        make_box(f"Alley_Bin_{bi}", (bx, 6.6, 0.55), (0.55, 0.5, 1.1), (0.26, 0.40, 0.52, 1.0))



def build_detail_pass_2026_08():
    """D2 surface breakup + first D3 (adaptive template pass per
    lore/_SET_DETAIL_PLAYBOOK.md). Per-locale wear personality is
    the next pass."""
    wear = (COL_FLOOR[0] * 0.88, COL_FLOOR[1] * 0.88, COL_FLOOR[2] * 0.88, 1.0)
    make_traffic_wear("Wear_Entry", [(0.0, 0.6), (0.0, ROOM_D * 0.55)],
                      width=0.75, tint=wear)
    make_floor_stain("Stain_WorkZone", (ROOM_W * 0.22, ROOM_D * 0.62), radius=0.24,
                     tint=(COL_FLOOR[0] * 0.82, COL_FLOOR[1] * 0.82, COL_FLOOR[2] * 0.82, 1.0))
    pw = PAL["wall"]
    band = (pw[0] * 0.90, pw[1] * 0.90, pw[2] * 0.88, 1.0)
    make_wall_tint_band("Band_W", (-ROOM_W / 2.0 + 0.105, ROOM_D / 2.0, 0.0),
                        length=ROOM_D - 0.4, axis='Y', band_z=CEIL - 0.16, tint=band)
    make_wall_tint_band("Band_E", (ROOM_W / 2.0 - 0.105, ROOM_D / 2.0, 0.0),
                        length=ROOM_D - 0.4, axis='Y', band_z=CEIL - 0.16, tint=band)
    make_threshold("Threshold_Entry", (0.0, 0.10), width=1.9, axis='X')
    make_light_switch("Switch_Entry", (1.15, 0.0), axis='X', face_sign=1, aged=True)
    make_wall_outlet("Outlet_W", (-ROOM_W / 2.0, ROOM_D * 0.35), axis='Y',
                     face_sign=1, aged=True)
    make_wall_outlet("Outlet_E", (ROOM_W / 2.0, ROOM_D * 0.70), axis='Y',
                     face_sign=-1, aged=True)


def build_use_states_d4():
    """D4 use states: Temperance is patience — the notebook open
    mid-entry, dishes drying, the kettle waiting."""
    # The notebook OPEN on the reading chair, pen in the gutter
    make_box("Chair_Notebook_L", (-2.38, 2.28, 0.415), (0.14, 0.20, 0.015),
             (0.90, 0.88, 0.82, 1.0))
    make_box("Chair_Notebook_R", (-2.22, 2.30, 0.418), (0.14, 0.20, 0.015),
             (0.92, 0.90, 0.84, 1.0))
    make_cyl("Chair_Pen", (-2.30, 2.29, 0.44), 0.006, 0.13,
             (0.20, 0.22, 0.30, 1.0), segments=6, axis='X')
    # Drying rack by the fridge: two plates on edge, a bowl, a mug
    # ON the kitchen counter (Kitch_Top: x 2.1..2.9, y 3.85..5.15, top
    # 0.98). 2026-09-22: rack, plates, bowl, mug and kettle sat south of
    # the fridge at y 2.4..3.0 — on air.
    make_box("Drying_Rack", (2.35, 4.15, 1.00), (0.40, 0.28, 0.04),
             (0.60, 0.62, 0.64, 1.0))
    make_box("Drying_Plate_A", (2.28, 4.12, 1.12), (0.02, 0.24, 0.24),
             (0.88, 0.86, 0.82, 1.0))
    make_box("Drying_Plate_B", (2.38, 4.14, 1.11), (0.02, 0.23, 0.23),
             (0.86, 0.84, 0.80, 1.0))
    make_bowl("Drying_Bowl", 2.52, 4.10, 1.02, (0.80, 0.76, 0.68, 1.0), r=0.09)
    make_mug("Counter_Mug", 2.60, 4.45, 0.98, (0.46, 0.54, 0.50, 1.0))
    # Kettle on the stove-side of the counter
    make_cyl("Kettle_Body", (2.72, 4.75, 1.05), 0.09, 0.14,
             (0.72, 0.72, 0.74, 1.0), segments=10)
    make_cyl("Kettle_Lidknob", (2.72, 4.75, 1.135), 0.02, 0.03,
             (0.30, 0.30, 0.32, 1.0), segments=6)
    make_box("Kettle_Spout", (2.62, 4.66, 1.06), (0.05, 0.05, 0.04),
             (0.70, 0.70, 0.72, 1.0))
    # Folded laundry on the sofa arm, one sock off the stack
    make_box("Laundry_Stack", (-1.42, 0.95, 0.52), (0.28, 0.24, 0.14),
             (0.76, 0.72, 0.66, 1.0))
    make_box("Laundry_Sock", (-1.25, 0.78, 0.44), (0.08, 0.14, 0.03),
             (0.50, 0.54, 0.60, 1.0))

def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    Three distinct cues; Desk_Phone and the graffiti-scarred
    Alley_Drainpipe exist (markers only). Built: THE DUST ("dust
    motes performing their intricate silent ballet in the shaft of
    late-morning Montreal sunlight") — seven pale specks hanging
    in front of the north window. The shaft itself is the post
    stack's job (screen-space only, per the visuals playbook);
    the motes give the insert something real to find.
    """
    for mi, (mx2, my2, mz2) in enumerate((
            (0.15, 4.40, 1.55), (-0.20, 4.20, 1.35), (0.05, 4.00, 1.70),
            (0.30, 4.30, 1.20), (-0.10, 4.50, 1.05), (0.20, 4.10, 0.90),
            (-0.30, 4.35, 1.50))):
        make_cyl(f"Dust_Mote_{mi}", (mx2, my2, mz2), 0.006, 0.006,
                 (0.96, 0.92, 0.80, 0.75), segments=6)


def build_archive_of_selves_2026_10():
    """CHARACTER PASS (2026-10-03, the Deck's standard from the Roberts
    house: "cozy, brimming with detail. Photos, and collections and
    comfy furniture and book shelves and lived in spaces"). The chapter:
    "His apartment … was a cluttered archive of selves. Movie posters
    (mostly Criterion Collection reprints now) jostled for wall space
    with pages torn from obscure literary journals. Notebooks filled
    with fragmented observations and abandoned narratives formed
    precarious ziggurats on every available surface." So: four posters,
    a cluster of torn pages pinned over the desk, ziggurats on EVERY
    surface (the coffee table, the bistro table, the floor by the desk,
    the sofa, the floor by the armchair), the desk lamp and the pen cup
    and the notebook open mid-line, the kitchen drawer half out with the
    private notebook in it, the bookshelf's collection (DVDs, a camera,
    a photo, a jar of pens, a small plant), a winter coat and boots by
    the door."""
    import random
    rnd = random.Random(14)
    wood = (0.42, 0.30, 0.20, 1.0)
    paper = (0.90, 0.88, 0.82, 1.0)
    ink = (0.24, 0.24, 0.28, 1.0)
    # ── four posters: a dark field, a pale title band, two lines
    def poster(name, face_xy, z, facing, field, band, w=0.60, h=0.90):
        fx, fy = face_xy
        nx, ny = {"+X": (1, 0), "-X": (-1, 0), "+Y": (0, 1), "-Y": (0, -1)}[facing]
        along_y = facing in ("+X", "-X")
        def sz(wd, ht, th): return (th, wd, ht) if along_y else (wd, th, ht)
        make_box(f"{name}_Sheet", (fx + nx * 0.004, fy + ny * 0.004, z), sz(w, h, 0.008), field)
        make_box(f"{name}_Band", (fx + nx * 0.009, fy + ny * 0.009, z - h * 0.32), sz(w * 0.84, h * 0.16, 0.002), band)
        for i in range(2):
            make_box(f"{name}_Line_{i}", (fx + nx * 0.011, fy + ny * 0.011, z - h * 0.32 + 0.03 - i * 0.035), sz(w * (0.5 - i * 0.14), 0.012, 0.002), ink)
        make_box(f"{name}_Figure", (fx + nx * 0.009, fy + ny * 0.009, z + h * 0.12), sz(w * 0.42, h * 0.46, 0.002), (field[0] * 1.7, field[1] * 1.6, field[2] * 1.5, 1.0))
    poster("Poster_Criterion_A", (-2.0, 0.105), 1.72, "+Y", (0.16, 0.20, 0.30, 1.0), (0.88, 0.84, 0.72, 1.0))
    poster("Poster_Criterion_B", (1.95, 0.105), 1.68, "+Y", (0.30, 0.14, 0.14, 1.0), (0.90, 0.88, 0.80, 1.0), w=0.56, h=0.84)
    poster("Poster_Criterion_C", (2.8965, 2.68), 1.72, "-X", (0.12, 0.22, 0.20, 1.0), (0.86, 0.84, 0.70, 1.0), w=0.56, h=0.84)
    poster("Poster_Criterion_D", (-2.8965, 4.30), 1.70, "+X", (0.34, 0.26, 0.12, 1.0), (0.90, 0.86, 0.74, 1.0), w=0.50, h=0.76)
    # ── torn journal pages pinned over the desk (west wall, y 2.95..3.85)
    for i in range(11):
        py = 2.95 + rnd.uniform(0.0, 0.90)
        pz = 1.25 + rnd.uniform(0.0, 0.95)
        w, h = rnd.choice(((0.12, 0.17), (0.14, 0.20), (0.10, 0.15), (0.16, 0.12)))
        tint = rnd.choice((paper, (0.86, 0.84, 0.76, 1.0), (0.92, 0.90, 0.86, 1.0)))
        make_box(f"Torn_Page_{i}", (-2.8965 + 0.004, py, pz), (0.006, w, h), tint)
        for k in range(3):
            make_box(f"Torn_Page_{i}_Line_{k}", (-2.8965 + 0.009, py, pz + h * 0.25 - k * h * 0.22), (0.002, w * rnd.uniform(0.45, 0.8), 0.006), ink)
        make_cyl(f"Torn_Page_{i}_Pin", (-2.8965 + 0.010, py, pz + h / 2.0 - 0.012), 0.006, 0.006, (0.80, 0.20, 0.18, 1.0), segments=6, axis='X')
    # ── ziggurats on every surface
    def ziggurat(prefix, x, y, z0, n):
        for k in range(n):
            make_box(f"{prefix}_{k}", (x + 0.012 * (k % 2) - 0.006, y + 0.008 * ((k + 1) % 2), z0 + k * 0.035 + 0.0175),
                     (0.20 - 0.015 * k, 0.26 - 0.015 * k, 0.035),
                     [(0.62, 0.24, 0.24, 1.0), (0.24, 0.42, 0.52, 1.0), (0.72, 0.62, 0.30, 1.0), (0.30, 0.30, 0.34, 1.0), (0.46, 0.52, 0.36, 1.0)][(k + n) % 5])
    ziggurat("Zig_Coffee", -1.05, 2.60, 0.445, 3)
    ziggurat("Zig_Bistro", 1.22, 3.72, 0.765, 3)
    ziggurat("Zig_DeskFloor", -2.72, 2.70, 0.0, 6)
    ziggurat("Zig_Sofa", -1.22, 1.22, 0.49, 2)   # the west cushion (the throw lies on the east one)
    ziggurat("Zig_ChairFloor", -2.78, 1.72, 0.0, 4)
    ziggurat("Zig_Radiator", 0.52, 4.80, 0.84, 2)
    # ── the desk: the lamp, the pen cup, the notebook open mid-line
    make_lamp("Desk_Lamp", -2.82, 3.66, base_z=0.765, h=0.42)
    make_cyl("Pen_Cup", (-1.62, 3.66, 0.815), 0.035, 0.10, (0.32, 0.36, 0.40, 1.0), segments=8)
    for i, (dx, dy) in enumerate(((-0.01, 0.0), (0.012, 0.01), (0.0, -0.012))):
        make_cyl(f"Pen_{i}", (-1.62 + dx, 3.66 + dy, 0.90), 0.004, 0.14, [(0.20, 0.22, 0.30, 1.0), (0.70, 0.20, 0.18, 1.0), (0.86, 0.80, 0.40, 1.0)][i], segments=5)
    make_box("Desk_Notebook_Open_L", (-1.83, 3.26, 0.773), (0.14, 0.20, 0.012), paper)
    make_box("Desk_Notebook_Open_R", (-1.68, 3.26, 0.773), (0.14, 0.20, 0.012), (0.92, 0.90, 0.84, 1.0))
    for k in range(5):
        make_box(f"Desk_Notebook_Line_{k}", (-1.83, 3.33 - k * 0.03, 0.780), (0.09 - 0.01 * (k % 3), 0.004, 0.002), ink)
    make_cyl("Desk_Pen_Open", (-1.70, 3.20, 0.785), 0.005, 0.13, (0.20, 0.22, 0.30, 1.0), segments=6, axis='X')
    # ── the kitchen drawer half out, the private notebook inside
    make_box("Kitchen_Drawer_Open", (1.98, 4.10, 0.80), (0.26, 0.40, 0.03), wood)
    make_box("Kitchen_Drawer_Front", (1.86, 4.10, 0.80), (0.02, 0.42, 0.14), (0.52, 0.40, 0.28, 1.0))
    for sgn in (-1, 1):
        make_box(f"Kitchen_Drawer_Side_{sgn:+d}", (1.98, 4.10 + sgn * 0.195, 0.86), (0.26, 0.01, 0.10), wood)
    make_cyl("Kitchen_Drawer_Knob", (1.845, 4.10, 0.80), 0.012, 0.02, P.METAL_STEEL, segments=6, axis='X')
    make_box("Private_Notebook", (1.98, 4.10, 0.825), (0.14, 0.20, 0.02), (0.22, 0.20, 0.26, 1.0))
    make_box("Private_Notebook_Band", (1.98, 4.10, 0.837), (0.14, 0.03, 0.002), (0.62, 0.24, 0.24, 1.0))
    # ── the bookshelf's collection, in the 20 cm north of each shelf's books
    sx2 = 2.66
    for shf, (kind) in enumerate(("keys", "dvds", "pens", "photo", "plant", "camera")):
        z = 0.20 + shf * 0.40 + 0.01
        y = 2.14
        if kind == "keys":
            make_bowl("Shelf_Key_Bowl", sx2, y, z, (0.46, 0.56, 0.52, 1.0), r=0.07, h=0.04)
        elif kind == "dvds":
            for k in range(5):
                make_box(f"Shelf_DVD_{k}", (sx2, y, z + 0.015 * k + 0.0075), (0.13, 0.18, 0.015), [(0.16, 0.16, 0.18, 1.0), (0.62, 0.60, 0.56, 1.0), (0.30, 0.22, 0.20, 1.0)][k % 3])
        elif kind == "pens":
            make_cyl("Shelf_Pen_Jar", (sx2, y, z + 0.055), 0.04, 0.11, (0.72, 0.80, 0.78, 0.6), segments=8)
            for k in range(4):
                make_cyl(f"Shelf_Pen_{k}", (sx2 + 0.012 * (k - 1.5), y + 0.008 * (k % 2), z + 0.11), 0.004, 0.16, (0.20 + 0.1 * k, 0.22, 0.30, 1.0), segments=5)
        elif kind == "photo":
            make_box("Shelf_Photo_Frame", (sx2 + 0.05, y, z + 0.08), (0.02, 0.14, 0.16), (0.24, 0.18, 0.12, 1.0))
            make_box("Shelf_Photo_Pic", (sx2 + 0.038, y, z + 0.08), (0.004, 0.11, 0.13), (0.58, 0.62, 0.66, 1.0))
            make_box("Shelf_Photo_Strut", (sx2 + 0.10, y, z + 0.04), (0.08, 0.02, 0.08), (0.24, 0.18, 0.12, 1.0))
        elif kind == "plant":
            make_cyl("Shelf_Plant_Pot", (sx2, y, z + 0.045), 0.045, 0.09, (0.72, 0.42, 0.28, 1.0), segments=8)
            for k in range(3):
                make_box(f"Shelf_Plant_Leaf_{k}", (sx2 + 0.03 * (k - 1), y + 0.02 * (k % 2), z + 0.13 + 0.02 * k), (0.06, 0.05, 0.008), (0.34, 0.52, 0.26, 1.0))
        else:
            make_box("Shelf_Camera", (sx2, y, z + 0.035), (0.12, 0.08, 0.07), (0.14, 0.14, 0.16, 1.0))
            make_cyl("Shelf_Camera_Lens", (sx2 - 0.07, y, z + 0.04), 0.025, 0.03, (0.10, 0.10, 0.12, 1.0), segments=8, axis='X')
    # ── the winter coat and the boots by the door (Montreal)
    make_box("Coat_Hooks", (1.45, 0.115, 1.74), (0.30, 0.02, 0.05), wood)
    make_chamfer_box("Winter_Coat", (1.42, 0.205, 1.26), (0.26, 0.16, 0.86), (0.22, 0.26, 0.34, 1.0), chamfer=0.03)   # against the hook rail
    make_chamfer_box("Winter_Coat_Hood", (1.42, 0.195, 1.74), (0.28, 0.14, 0.12), (0.26, 0.30, 0.38, 1.0), chamfer=0.03)
    make_box("Scarf", (1.56, 0.155, 1.40), (0.08, 0.06, 0.60), (0.62, 0.24, 0.24, 1.0))
    make_box("Boot_A", (1.25, 0.36, 0.12), (0.12, 0.30, 0.24), (0.20, 0.18, 0.16, 1.0))
    make_box("Boot_B", (1.42, 0.38, 0.12), (0.12, 0.30, 0.24), (0.20, 0.18, 0.16, 1.0))
    make_box("Boot_Tray", (1.34, 0.38, 0.006), (0.40, 0.36, 0.012), (0.30, 0.30, 0.32, 1.0))


def main():
    clear_scene(); build_shell(); build_living(); build_dining_nook(); build_floor_lamp(); build_kitchenette(); build_radiator_under_window(); build_decor(); build_ceiling_infra()
    build_hero_props()
    build_detail_pass_2026_08()
    build_use_states_d4()
    build_hero_props_2026_09()
    build_archive_of_selves_2026_10()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/montreal_apartment.glb"))
    print(f"\n[build_montreal_apartment] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
