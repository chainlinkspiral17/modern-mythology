"""lena_apartment — vol7's home base, rebuilt from the prose
(2026-08-03 hero-prop pass; it had shipped as a dorm room).

Canon (21 vol7 scenes): a small one-bedroom on Hemlock. The kitchen
window over the sink looks onto the alley and the Starfish Nebula
mural; the front window looks DOWN onto the street; the small round
oak table from the seventies wobbles on one leg and its four chairs
are not a matched set; the couch keeps a wool blanket folded over
its back; the chair by the window has a small wooden side table
(the Estuary 7 beat happens on it); four hooks by the door hold
four coats; the deadbolt gets locked for the first time in three
years at the end of ch7; the ceiling has three water stains Lena
refuses to paint over; the bedroom closes behind its own door.

Coordinate frame: Blender Z-up, y=0 front (Hemlock) wall with the
door, +Y into the apartment, walls x=±2.5, back wall y=5.0, ceiling
2.6. Kitchen along the W wall; bedroom nook behind a partition at
y=3.05; front room center/east. glTF export remaps to Godot
(x, z, -y).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.furniture import make_chair
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_window
from _props.decor import make_floor_plant, make_faded_poster
from _props.safety import make_smoke_detector

ROOM_W = 5.0; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall": (0.96, 0.86, 0.78, 1.0), "baseboard": (0.62, 0.46, 0.30, 1.0)}
COL_FLOOR = (0.74, 0.58, 0.38, 1.0); COL_SEAM = (0.42, 0.30, 0.18, 1.0)
COL_WOOD = (0.46, 0.34, 0.22, 1.0)
COL_OAK = (0.58, 0.42, 0.24, 1.0)
COL_ACCENT = (0.86, 0.62, 0.62, 1.0)
COL_GLASS = (0.45, 0.52, 0.60, 0.5)
COL_FRAME = (0.34, 0.28, 0.22, 1.0)
COL_STEEL = (0.60, 0.62, 0.63, 1.0)
COL_COUNTER = (0.52, 0.48, 0.42, 1.0)
# The four chairs are not a matched set — four different woods
CHAIR_WOODS = [(0.46, 0.34, 0.22, 1.0), (0.56, 0.44, 0.30, 1.0),
               (0.38, 0.26, 0.18, 1.0), (0.50, 0.36, 0.28, 1.0)]


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    # The front door itself, ajar-closed in the opening, with the
    # deadbolt ("She had not, in three years, locked the deadbolt")
    make_box("Front_Door", (0.0, 0.06, 1.02), (0.90, 0.05, 2.04), COL_WOOD)
    make_cyl("Door_Knob", (0.34, 0.10, 1.00), 0.035, 0.04, (0.66, 0.52, 0.24, 1.0), axis='Y', segments=8)
    make_box("Deadbolt", (0.34, 0.10, 1.22), (0.06, 0.03, 0.10), (0.74, 0.60, 0.30, 1.0))
    # Four hooks, four coats — by the door
    for i, hx in enumerate((-1.15, -0.95, -0.75, -0.55)):
        make_cyl(f"Coat_Hook_{i}", (hx, 0.10, 1.70), 0.015, 0.06, COL_FRAME, axis='Y', segments=6)
        coat_cols = [(0.30, 0.34, 0.40, 1.0), (0.44, 0.30, 0.22, 1.0),
                     (0.26, 0.36, 0.30, 1.0), (0.52, 0.44, 0.30, 1.0)]
        make_box(f"Coat_{i}", (hx, 0.16, 1.32), (0.16, 0.10, 0.72), coat_cols[i])
    # Bedroom partition at y=3.05 (x -2.5..+0.4) with its own door
    make_wall("Bedroom_Part_W", (-1.625, 3.05, 0), length=1.75, height=CEIL,
              axis='X', palette=PAL_WALL)
    make_box("Bedroom_Part_E", (0.275, 3.05, CEIL/2.0), (0.25, 0.16, CEIL), PAL_WALL["wall"])
    make_box("Bedroom_Part_Header", (-0.30, 3.05, CEIL-0.25), (0.90, 0.16, 0.50), PAL_WALL["wall"])
    make_box("Bedroom_Door", (-0.62, 3.02, 1.02), (0.62, 0.04, 2.04), COL_WOOD)
    # The three ceiling water stains ("proof her upstairs neighbor's
    # bathtub leaked... painting them over would be a lie")
    for i, (sx, sy, sr) in enumerate(((0.40, 3.55, 0.22), (0.62, 3.78, 0.14), (0.48, 3.98, 0.10))):
        make_cyl(f"Ceil_Stain_{i}", (sx, sy, CEIL-0.005), sr, 0.004,
                 (0.78, 0.70, 0.58, 1.0), segments=12)


def build_kitchen():
    """W wall: counter + sink under the alley window, stove, fridge
    at the SW corner end, dish drainer, kettle, braided rug."""
    # The window over the sink → the alley + the Starfish Nebula mural
    make_window("Kitchen_Window", (-ROOM_W/2.0+0.02, 1.30, 1.50), width=1.10, height=1.10, axis='Y')
    # Counter run
    make_box("Counter_Body", (-2.20, 1.40, 0.44), (0.60, 2.00, 0.88), COL_WOOD)
    make_box("Counter_Top", (-2.20, 1.40, 0.90), (0.64, 2.06, 0.05), COL_COUNTER)
    make_box("Sink_Bowl", (-2.24, 1.30, 0.905), (0.42, 0.44, 0.05), (0.42, 0.44, 0.45, 1.0))
    make_cyl("Faucet", (-2.44, 1.30, 1.03), 0.02, 0.22, COL_STEEL, segments=6)
    # Dish drainer beside the sink
    make_box("Dish_Drainer", (-2.20, 1.82, 0.945), (0.34, 0.28, 0.06), COL_STEEL)
    make_box("Drainer_Plate", (-2.20, 1.82, 1.00), (0.03, 0.20, 0.16), (0.86, 0.82, 0.74, 1.0))
    # Stove at the counter's S end, kettle on it
    make_box("Stove_Body", (-2.18, 0.50, 0.44), (0.62, 0.62, 0.88), (0.82, 0.80, 0.76, 1.0))
    make_box("Stove_Top", (-2.18, 0.50, 0.895), (0.60, 0.60, 0.03), (0.22, 0.22, 0.24, 1.0))
    for bi, (ox, oy) in enumerate(((-0.15, -0.15), (0.15, -0.15), (-0.15, 0.15), (0.15, 0.15))):
        make_cyl(f"Burner_{bi}", (-2.18+ox, 0.50+oy, 0.912), 0.09, 0.01,
                 (0.14, 0.14, 0.15, 1.0), segments=10)
    make_cyl("Kettle", (-2.03, 0.35, 0.99), 0.10, 0.16, COL_STEEL, segments=10)
    make_box("Kettle_Handle", (-2.03, 0.35, 1.10), (0.14, 0.02, 0.03), (0.20, 0.18, 0.16, 1.0))
    # Cast iron pan hanging by the stove; hand grinder + cone on top
    make_cyl("CastIron_Pan", (-2.44, 0.82, 1.35), 0.14, 0.03, (0.16, 0.16, 0.17, 1.0), axis='Y', segments=12)
    make_box("Coffee_Grinder", (-2.28, 2.28, 1.00), (0.10, 0.10, 0.16), COL_WOOD)
    make_cyl("Coffee_Cone", (-2.12, 2.28, 0.97), 0.06, 0.09, (0.86, 0.82, 0.74, 1.0), segments=8)
    # Fridge, E wall near the S corner ("four eggs in the carton on
    # the second shelf")
    make_box("Fridge", (2.15, 0.55, 0.90), (0.66, 0.66, 1.80), (0.88, 0.86, 0.82, 1.0))
    make_box("Fridge_Handle", (1.80, 0.30, 1.10), (0.03, 0.04, 0.60), COL_STEEL)
    # Braided rag rug in front of the sink
    make_cyl("Sink_Rug", (-1.85, 1.35, 0.010), 0.42, 0.006, COL_ACCENT, segments=14)
    make_cyl("Sink_Rug_Ring", (-1.85, 1.35, 0.013), 0.30, 0.005, (0.66, 0.44, 0.40, 1.0), segments=14)


def build_kitchen_table():
    """The small round oak table from the seventies — wobble in one
    leg — and four chairs that are not a matched set. The hexagon
    gets laid out here in ch12; four people eat here in ch8."""
    tx, ty = -0.80, 1.60
    make_cyl("Table_Top", (tx, ty, 0.745), 0.55, 0.045, COL_OAK, segments=16)
    make_cyl("Table_Pedestal", (tx, ty, 0.38), 0.07, 0.70, COL_OAK, segments=10)
    # Four feet — one shorter: the wobble
    for fi, ang_off in enumerate(((0.30, 0.0), (-0.30, 0.0), (0.0, 0.30), (0.0, -0.30))):
        h = 0.055 if fi != 2 else 0.047   # the wobbling leg
        make_box(f"Table_Foot_{fi}", (tx+ang_off[0], ty+ang_off[1], h/2.0),
                 (0.34 if ang_off[1]==0.0 else 0.10,
                  0.10 if ang_off[1]==0.0 else 0.34, h), COL_OAK)
    # Four mismatched chairs
    for ci, (cx, cy) in enumerate(((tx-1.0, ty), (tx+1.0, ty), (tx, ty-1.0), (tx, ty+1.0))):
        wood = CHAIR_WOODS[ci]
        back_dx = -0.20 if cx < tx else (0.20 if cx > tx else 0.0)
        back_dy = -0.20 if cy < ty else (0.20 if cy > ty else 0.0)
        import math as _mm
        make_chair(f"KChair_{ci}", cx, cy, yaw=_mm.atan2(back_dx, -back_dy) if (back_dx or back_dy) else 0.0, wood=wood, w=0.42)


def build_front_room():
    """Couch + wool blanket, the chair by the window with its side
    table, the front window down onto Hemlock."""
    # The front window (Wall_S_E) — "she went to the front window
    # and looked down"
    make_window("Front_Window", (1.75, 0.02, 1.42), width=1.00, height=1.20)
    # Couch against the partition's east reach, facing south
    sx, sy = 0.70, 3.60
    make_box("Couch_Base", (sx, sy, 0.24), (1.90, 0.85, 0.36), (0.44, 0.40, 0.34, 1.0))
    make_box("Couch_Back", (sx, sy+0.36, 0.62), (1.90, 0.18, 0.60), (0.40, 0.36, 0.30, 1.0))
    for ax in (sx-0.88, sx+0.88):
        make_box(f"Couch_Arm_{ax:.1f}", (ax, sy, 0.48), (0.16, 0.85, 0.48), (0.40, 0.36, 0.30, 1.0))
    for pi, px in enumerate((sx-0.45, sx+0.45)):
        make_box(f"Couch_Cushion_{pi}", (px, sy-0.05, 0.46), (0.80, 0.66, 0.14), (0.48, 0.44, 0.38, 1.0))
    # The wool blanket, folded over the back
    make_box("Wool_Blanket", (sx-0.30, sy+0.36, 0.945), (0.70, 0.24, 0.06), (0.56, 0.40, 0.30, 1.0))
    # The chair by the window + the small wooden side table (the
    # Estuary 7 beat happens on this table)
    make_box("WChair_Base", (1.70, 1.60, 0.26), (0.72, 0.72, 0.40), (0.36, 0.42, 0.38, 1.0))
    make_box("WChair_Back", (1.70, 1.94, 0.66), (0.72, 0.20, 0.62), (0.33, 0.38, 0.34, 1.0))
    for ax in (1.36, 2.04):
        make_box(f"WChair_Arm_{ax:.2f}", (ax, 1.60, 0.52), (0.14, 0.70, 0.42), (0.33, 0.38, 0.34, 1.0))
    make_cyl("Side_Table_Top", (1.40, 0.95, 0.52), 0.28, 0.04, COL_WOOD, segments=12)
    make_cyl("Side_Table_Post", (1.70, 0.95, 0.26), 0.04, 0.50, COL_WOOD, segments=8)
    # Radiator pipe in the SE corner (the one that clicks)
    make_cyl("Radiator_Pipe", (2.38, 0.25, 1.30), 0.04, 2.55, (0.60, 0.56, 0.50, 1.0), segments=8)


def build_bedroom():
    """Behind the partition: the bed (kept from the old build), the
    nightstand, the thermostat that reads 61, two posters."""
    # The bed is 1.94 long and the bedroom is 1.95 deep behind
    # the y=3.05 partition — at ROOM_D-1.15 its footboard
    # crossed into the partition. Pushed to the north wall.
    bx, by = -1.0, ROOM_D - 0.99
    make_box("Bed_Frame", (bx, by, 0.20), (1.50, 1.94, 0.22), (0.42, 0.30, 0.20, 1.0))
    make_box("Bed_Mattress", (bx, by, 0.42), (1.40, 1.84, 0.16), (0.92, 0.86, 0.78, 1.0))
    make_box("Bed_Headboard", (bx, by+1.00, 0.66), (1.54, 0.08, 0.66), (0.40, 0.28, 0.18, 1.0))
    make_box("Bed_Footboard", (bx, by-0.98, 0.42), (1.54, 0.08, 0.34), (0.40, 0.28, 0.18, 1.0))
    make_box("Bed_Pillow_L", (bx-0.36, by+0.68, 0.54), (0.62, 0.36, 0.12), (0.98, 0.94, 0.90, 1.0))
    make_box("Bed_Pillow_R", (bx+0.36, by+0.68, 0.54), (0.62, 0.36, 0.12), (0.98, 0.94, 0.90, 1.0))
    make_box("Bed_Duvet", (bx, by-0.24, 0.52), (1.44, 1.18, 0.10), (0.72, 0.46, 0.52, 1.0))
    # vol7 interlude ii (2026-09-03): "Her thigh has charcoal on it in the
    # shape of three letters: S U N ... There is no charcoal in the
    # apartment." The residue it left on the duvet where she slept.
    for ci, (dx, w) in enumerate(((-0.16, 0.06), (0.0, 0.05), (0.16, 0.06))):
        make_box("Charcoal_Letter_%d" % ci, (bx - 0.10 + dx, by - 0.36, 0.5715), (w, 0.07, 0.003), (0.16, 0.15, 0.15, 1.0))
    make_box("Charcoal_Smudge", (bx - 0.10, by - 0.30, 0.5705), (0.40, 0.06, 0.001), (0.36, 0.34, 0.34, 1.0))
    make_box("Nightstand", (bx+0.95, by+0.7, 0.30), (0.42, 0.42, 0.60), COL_WOOD)
    make_box("Clock", (bx+0.95, by+0.7, 0.66), (0.16, 0.10, 0.10), P.METAL_BLACK)
    # Thermostat above the bed (reads 61)
    make_box("Thermostat", (bx, ROOM_D-0.06, 1.85), (0.14, 0.05, 0.10), (0.88, 0.86, 0.82, 1.0))
    # The small side table just OUTSIDE the bedroom door (Kai's cup)
    make_box("Hall_Table", (0.05, 2.78, 0.34), (0.36, 0.30, 0.68), COL_WOOD)
    # Posters on the W wall, bedroom side
    for pi, py in enumerate((3.55, 4.35)):
        make_faded_poster(f"Poster_W_{pi}", (-ROOM_W/2.0+0.05, py, 1.50))
    # Space heater by the bedroom doorway
    make_box("Space_Heater", (1.05, 2.90, 0.18), (0.30, 0.16, 0.36), (0.80, 0.78, 0.74, 1.0))
    make_box("Heater_Grille", (1.05, 3.00, 0.18), (0.24, 0.02, 0.26), (0.94, 0.60, 0.34, 1.0))


def build_dressing():
    """Bookshelf, plant, string lights, center rug — the parts of
    the old build the prose supports, kept."""
    BOOK_COLS = [(0.62, 0.24, 0.24, 1.0), (0.24, 0.42, 0.52, 1.0),
                 (0.72, 0.62, 0.30, 1.0), (0.30, 0.46, 0.34, 1.0)]
    shx = ROOM_W/2.0 - 0.20
    make_box("Shelf_Body", (shx, ROOM_D-1.2, 0.90), (0.30, 1.00, 1.80), COL_WOOD)
    for r in range(4):
        for c in range(6):
            make_box(f"Shelf_Book_{r}_{c}", (shx-0.03, ROOM_D-1.7+c*0.16, 0.35+r*0.42),
                     (0.22, 0.12, 0.26), BOOK_COLS[(r+c) % 4])
    make_floor_plant("Plant", (-ROOM_W/2.0+0.5, ROOM_D-0.6, 0.0),
                     palette={"leaf": (0.36, 0.48, 0.30, 1.0), "pot": (0.66, 0.40, 0.26, 1.0)})
    for i in range(9):
        make_cyl(f"Fairy_{i}", (-1.6+i*0.4, ROOM_D-0.08, 2.10), 0.03, 0.03,
                 (1.0, 0.82, 0.5, 1.0), segments=6)
    make_cyl("Rug", (0.5, 2.2, 0.012), 0.95, 0.005, COL_ACCENT)
    # No fluorescents: this home lights by kettle, gooseneck and the
    # laundromat's orange spill (mood strata carry the rest)
    make_smoke_detector("Smoke", (0.9, ROOM_D/2.0, CEIL))


def build_canvas_2026_08():
    """LENA'S WORKING CANVAS (shot_marker_audit --props, 2026-08-12):
    [shot:insert canvas] fires on this locale and there was no canvas
    — she is the volume's zine artist and her apartment had nothing
    of her work in it.

    An A-frame easel in the light of the west window with a
    half-finished board on it: gessoed ground, a blocked-in shape,
    and the edge she has not decided about yet. Paint is stacked
    where a working painter stacks it — on the floor beside the
    easel, not in a tidy box.
    """
    pine = (0.68, 0.56, 0.38, 1.0)
    pine_dk = (0.52, 0.42, 0.28, 1.0)
    gesso = (0.90, 0.88, 0.82, 1.0)
    block = (0.36, 0.46, 0.52, 1.0)      # the blocked-in shape
    block_dk = (0.24, 0.32, 0.40, 1.0)
    ex, ey = -1.72, 2.35                 # in the west window's light
    # Easel: two front legs splayed, one back leg, a mast, a tray
    for sgn in (-1, 1):
        make_box("Easel_Leg_%d" % sgn, (ex + sgn * 0.30, ey - 0.10, 0.72),
                 (0.045, 0.045, 1.44), pine)
    make_box("Easel_BackLeg", (ex, ey + 0.34, 0.70),
             (0.045, 0.045, 1.40), pine_dk)
    make_box("Easel_Mast", (ex, ey - 0.10, 1.05), (0.05, 0.05, 0.90), pine)
    make_box("Easel_Tray", (ex, ey - 0.16, 0.86), (0.72, 0.09, 0.035), pine_dk)
    make_box("Easel_TrayLip", (ex, ey - 0.20, 0.885), (0.72, 0.018, 0.030), pine)
    # The board on the tray, leaning back with the mast
    make_box("Canvas_Board", (ex, ey - 0.09, 1.20), (0.60, 0.022, 0.72), gesso)
    make_box("Canvas_Edge_T", (ex, ey - 0.10, 1.555), (0.62, 0.030, 0.028), pine_dk)
    make_box("Canvas_Edge_B", (ex, ey - 0.10, 0.845), (0.62, 0.030, 0.028), pine_dk)
    # What is ON it: a blocked-in headland shape, unfinished at the
    # right edge — the painting is in progress, which is the point.
    make_box("Canvas_Block", (ex - 0.09, ey - 0.102, 1.13),
             (0.34, 0.004, 0.40), block)
    make_box("Canvas_Block_Dk", (ex - 0.14, ey - 0.104, 1.01),
             (0.22, 0.004, 0.16), block_dk)
    make_box("Canvas_Horizon", (ex, ey - 0.104, 1.28),
             (0.56, 0.004, 0.012), block_dk)
    # Brushes in a jar on the tray + a rag over the tray lip
    make_cyl("Canvas_Jar", (ex + 0.24, ey - 0.15, 0.945),
             0.045, 0.13, (0.72, 0.76, 0.74, 0.65), segments=10)
    for bi, bo in enumerate((-0.012, 0.0, 0.014)):
        make_cyl("Canvas_Brush_%d" % bi, (ex + 0.24 + bo, ey - 0.15, 1.055),
                 0.006, 0.20, (0.62, 0.50, 0.32, 1.0), segments=6)
    make_box("Canvas_Rag", (ex - 0.26, ey - 0.20, 0.865),
             (0.16, 0.05, 0.10), (0.74, 0.70, 0.62, 1.0))
    # Paint tubes stacked on the floor where a working painter keeps
    # them — squeezed flat, capped, not in a box.
    for ti, (tx2, ty2, col) in enumerate((
            (ex - 0.34, ey - 0.30, (0.72, 0.24, 0.20, 1.0)),
            (ex - 0.28, ey - 0.36, (0.24, 0.34, 0.52, 1.0)),
            (ex - 0.38, ey - 0.40, (0.86, 0.80, 0.42, 1.0)),
            (ex - 0.24, ey - 0.28, (0.30, 0.36, 0.28, 1.0)))):
        make_cyl("Canvas_Tube_%d" % ti, (tx2, ty2, 0.022),
                 0.018, 0.11, col, segments=6, axis='Y')
        make_cyl("Canvas_TubeCap_%d" % ti, (tx2, ty2 - 0.062, 0.022),
                 0.012, 0.02, (0.30, 0.30, 0.32, 1.0), segments=6, axis='Y')
    # A finished board leaning face-in against the wall — the ones
    # she is not looking at today.
    make_box("Canvas_Stack_A", (ex - 0.40, ey + 0.05, 0.42),
             (0.52, 0.030, 0.68), pine_dk)
    make_box("Canvas_Stack_B", (ex - 0.44, ey + 0.02, 0.38),
             (0.44, 0.026, 0.60), gesso)


def build_starfish_nebula_2026_08():
    """THE STARFISH NEBULA AND THE FOUR PATCHES (--props, 2026-08).

    Canon: "She sat at the kitchen table with the cup and looked
    through the window at the alley and at the Starfish Nebula and
    at the four patches and did not, this evening, do anything
    about any of it." The mural is on the alley wall OUTSIDE her
    kitchen window (west, x = -2.5); somebody painted over parts of
    it in four rectangles of almost-but-not-the-mural's color, and
    the patches are the wound the chapter keeps touching.
    """
    wx = -ROOM_W/2.0 - 2.6           # the alley wall, 2.6m across
    brick = (0.44, 0.30, 0.24, 1.0)
    deep = (0.13, 0.10, 0.26, 1.0)   # nebula ground
    violet = (0.34, 0.20, 0.46, 1.0)
    teal = (0.16, 0.38, 0.44, 1.0)
    rose = (0.62, 0.32, 0.42, 1.0)
    star = (0.88, 0.84, 0.66, 1.0)
    patch = (0.41, 0.33, 0.28, 1.0)  # almost the brick, not quite
    # The wall itself, running past the window frame both ways.
    make_box("Nebula_AlleyWall", (wx, 1.30, 1.60), (0.15, 6.5, 3.2), brick)
    # The mural ground and its bands, proud of the wall by paint.
    make_box("Nebula_Ground", (wx + 0.083, 1.30, 1.70), (0.012, 3.6, 2.2), deep)
    make_box("Nebula_Band_Violet", (wx + 0.090, 0.75, 1.95), (0.010, 1.9, 0.85), violet)
    make_box("Nebula_Band_Teal", (wx + 0.090, 1.95, 1.45), (0.010, 1.7, 0.95), teal)
    make_box("Nebula_Band_Rose", (wx + 0.095, 1.35, 2.25), (0.008, 1.2, 0.55), rose)
    # The starfish: a center and five arms, staggered boxes.
    make_box("Nebula_Star_Core", (wx + 0.100, 1.30, 1.75), (0.007, 0.34, 0.34), star)
    for ai, (dy, dz, w, h) in enumerate((
            (0.0, 0.42, 0.16, 0.55), (0.40, 0.16, 0.48, 0.16),
            (-0.40, 0.16, 0.48, 0.16), (0.26, -0.34, 0.20, 0.48),
            (-0.26, -0.34, 0.20, 0.48))):
        make_box("Nebula_Star_Arm_%d" % ai,
                 (wx + 0.100, 1.30 + dy, 1.75 + dz), (0.007, w, h), star)
    # THE FOUR PATCHES · rectangles of almost-right paint, each a
    # little differently wrong, one visibly newer than the rest.
    for pi, (py, pz, w, h, col) in enumerate((
            (0.55, 2.30, 0.55, 0.40, patch),
            (2.30, 1.15, 0.48, 0.55, (0.38, 0.31, 0.27, 1.0)),
            (1.85, 2.35, 0.40, 0.35, (0.44, 0.35, 0.29, 1.0)),
            (0.85, 0.95, 0.50, 0.45, (0.48, 0.38, 0.31, 1.0)))):
        make_box("Nebula_Patch_%d" % (pi + 1), (wx + 0.105, py, pz),
                 (0.006, w, h), col)


def build_wear_personality_2026_08():
    """WHOSE FEET, WHOSE SPILLS (wear-personality pass 2, 2026-08-19).

    Lena's wear against Olaf's: the cabin remembers one man's
    decades; this apartment remembers three years of ONE woman who
    makes things, keeps the heat at sixty-one, and suddenly hosts
    three guests. Her wear is pigment and coffee; the crowding is
    too new to mark the floor, so it shows in the OBJECTS instead
    (a flattened cushion, a folded floor blanket).
    """
    from _props.detail import make_traffic_wear, make_floor_stain, make_scuff_band
    floor_dk = (0.33, 0.29, 0.24, 1.0)
    coffee = (0.36, 0.25, 0.15, 1.0)
    # ── HER THREE YEARS ────────────────────────────────────────
    # One narrow path: door → kitchen → the easel light → bedroom.
    # A person alone walks a thinner line than a family.
    make_traffic_wear("Wear_Lena_Path",
                      [(0.6, 0.8), (-0.8, 1.2), (-1.6, 1.6), (-1.7, 2.3)],
                      width=0.38, tint=floor_dk)
    make_traffic_wear("Wear_Lena_Path_Bed",
                      [(-1.0, 1.9), (-0.62, 2.9)],
                      width=0.34, tint=floor_dk)
    # THE CONE AND THE KETTLE · she "worked the cone and the
    # kettle" — the cone lives at one spot on the counter: a ring
    # of rings, and a drip line down the counter face.
    for ri, (rx, ry, rr) in enumerate(((-2.14, 1.02, 0.055), (-2.24, 1.10, 0.045),
                                       (-2.18, 0.94, 0.038))):
        make_cyl("Wear_ConeRing_%d" % ri, (rx, ry, 0.928), rr, 0.003, coffee, segments=8)
    make_scuff_band("Wear_Counter_Drip", (-1.86, 1.05), 0.5, axis='Y',
                    height=0.14, band_z=0.62, tint=(0.30, 0.22, 0.14, 1.0))
    # ── THE ARTIST'S FLOOR · around the easel (-1.72, 2.35) ──
    # Paint lands where work happens: a constellation of small
    # hard-edged drips in HER palette (the nebula's colors — she
    # mixes what she paints with), plus one solvent bloom.
    for di, (dx, dy, dr, col) in enumerate((
            (-1.45, 2.05, 0.030, (0.34, 0.20, 0.46, 1.0)),
            (-1.95, 2.10, 0.024, (0.16, 0.38, 0.44, 1.0)),
            (-1.60, 2.62, 0.036, (0.62, 0.32, 0.42, 1.0)),
            (-2.05, 2.50, 0.020, (0.88, 0.84, 0.66, 1.0)),
            (-1.30, 2.40, 0.026, (0.13, 0.10, 0.26, 1.0)))):
        make_cyl("Wear_PaintDrip_%d" % di, (dx, dy, 0.007), dr, 0.004, col, segments=6)
    make_floor_stain("Wear_SolventBloom", (-1.80, 2.75), radius=0.14,
                     tint=(0.38, 0.35, 0.30, 1.0), segments=9)
    # Charcoal smudge on the west wall at hand height, where she
    # steadies herself leaning in to the board.
    make_box("Wear_CharcoalSmudge", (-2.46, 2.15, 1.32), (0.012, 0.16, 0.10),
             (0.24, 0.23, 0.22, 1.0))
    # ── SIXTY-ONE DEGREES ──────────────────────────────────────
    # The thermostat reads what it reads; the draft towel at the
    # door base is how a cold apartment answers its own door.
    make_box("Thermostat_Body", (2.46, 2.2, 1.45), (0.035, 0.14, 0.10),
             (0.86, 0.84, 0.78, 1.0))
    make_box("Thermostat_Needle", (2.44, 2.19, 1.45), (0.008, 0.05, 0.012),
             (0.72, 0.24, 0.18, 1.0))
    make_box("Wear_DraftTowel", (0.60, 0.14, 0.035), (0.85, 0.14, 0.07),
             (0.55, 0.50, 0.42, 1.0))
    # ── THE CROWDING (weeks, so: objects, not floor) ───────────
    # Finn's end of the couch: one cushion sits lower and prouder
    # at the front edge than its twin.
    # (couch sits at (0.70, 3.60); first placement floated in front
    # of it and hit the partition — the flat sits ON Finn's cushion)
    make_box("Wear_Cushion_Flat", (0.25, 3.51, 0.545), (0.74, 0.58, 0.030),
             (0.45, 0.41, 0.35, 1.0))
    # Kai's floor bed, folded and stacked by the couch arm each
    # morning — a guest who folds is a guest who knows he's one.
    make_box("Wear_FloorBed_Folded", (1.55, 2.55, 0.09), (0.55, 0.42, 0.18),
             (0.50, 0.44, 0.36, 1.0))
    make_box("Wear_FloorBed_Pillow", (1.55, 2.55, 0.225), (0.42, 0.30, 0.09),
             (0.82, 0.78, 0.70, 1.0))


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    Nine distinct insert cues fire on this locale with no marker and
    (for most) no geometry. The apartment is where vol7 keeps its
    smallest, heaviest objects, and none of them were in the room:

    - THE ESTUARY 7 STICK (ch7/ch8 six-oclock): "she had pulled the
      Estuary 7 stick out of her inside coat pocket and set it on
      the small wooden side table by the chair" — the waxed-paper
      sleeve, the stick's end proud of it, Ines Rocha's white label.
    - THE HEXAGON (ch12_lena): "He laid the eight pieces on her
      kitchen table in the configuration he had assembled them in:
      six in the ring, the cedar face in the center, the AR I A
      piece beside." Cloth, ring, face, ARIA piece — and THE EIGHTH
      PIECE ("She picked up the eighth piece. She held it in her
      palm") as its own palm-sized cedar block on the cloth.
    - THE LETTER TO JORGEN (ch6 sunday/cale_opening): "a sheet of
      paper and a pen the ink in which had dried. She got up and
      found another. She came back and wrote Jorgen at the top of
      the page" — sheet, the dead pen, the second pen, the cup.
      One prop serves both the paper and letter cues.
    - LENA'S PHONE (ch6): Tem's twelve-fourteen message.
    - THE BREAD (ch7 six-oclock): "the sound in the apartment was
      Kai cutting bread on the small wooden board" — board, loaf,
      cut slice, knife, at the counter.
    - THE BOWL (ch8 the_table): "She pushed the bowl an inch away
      from her" — one bowl at the east place, an inch off true.
    (The deadbolt cue aims at the Deadbolt the 2026-08 pass built.)

    Draft note: this is co-staging — ch6, ch7, ch8 and ch12 objects
    share one tabletop, separated so nothing clips. Draft N+1 could
    key hero props to chapter flags the way the mural patch states
    would want, once locales know which scene is looking at them.
    """
    waxpaper = (0.88, 0.84, 0.72, 1.0)
    cedar = (0.55, 0.38, 0.26, 1.0)
    cedar_dk = (0.44, 0.30, 0.20, 1.0)
    cloth_col = (0.78, 0.74, 0.64, 1.0)
    paper_col = (0.94, 0.92, 0.86, 1.0)

    # ── THE ESTUARY 7 STICK · side table (1.40, 0.95), top 0.54 ──
    make_box("Estuary_Stick_Sleeve", (1.44, 0.95, 0.551), (0.26, 0.09, 0.020), waxpaper)
    make_box("Estuary_Stick", (1.258, 0.95, 0.549), (0.10, 0.05, 0.016), (0.30, 0.26, 0.22, 1.0))
    make_box("Stick_Label", (1.44, 0.95, 0.563), (0.10, 0.05, 0.002), (0.96, 0.95, 0.92, 1.0))

    # ── THE HEXAGON · kitchen table north half, tabletop 0.7675 ──
    hx, hy = -0.80, 1.78
    make_box("Hexagon_Cloth", (hx, hy, 0.770), (0.40, 0.36, 0.004), cloth_col)
    import math as _m
    for hi in range(6):
        ang = _m.pi / 3.0 * hi + _m.pi / 6.0
        make_box(f"Hexagon_Ring_{hi}",
                 (hx + 0.13 * _m.cos(ang), hy + 0.13 * _m.sin(ang), 0.781),
                 (0.085, 0.085, 0.018), cedar)
    make_cyl("Hexagon_Center_Face", (hx, hy, 0.780), 0.055, 0.016, cedar_dk, segments=12)
    make_cyl("Hexagon_Face_Inlay", (hx, hy, 0.7895), 0.030, 0.003,
             (0.62, 0.46, 0.32, 1.0), segments=10)
    # The ARIA piece beside the ring, still on the cloth
    make_box("Hexagon_Aria_Piece", (-0.645, 1.635, 0.782), (0.070, 0.050, 0.020), cedar)
    # The eighth piece — the one she holds in her palm — on the
    # cloth's far corner, apart from the configuration
    make_box("Eighth_Piece", (-0.955, 1.920, 0.782), (0.070, 0.050, 0.020), cedar_dk)

    # ── THE LETTER TO JORGEN · table south-east, one sheet ──
    make_box("Letter_Paper", (-0.55, 1.35, 0.769), (0.21, 0.28, 0.003), paper_col)
    make_box("Letter_Name_Line", (-0.55, 1.46, 0.771), (0.12, 0.010, 0.001),
             (0.30, 0.30, 0.34, 1.0))
    make_cyl("Letter_Pen_Dry", (-0.42, 1.28, 0.7735), 0.005, 0.13,
             (0.24, 0.24, 0.28, 1.0), axis='Y', segments=6)
    make_cyl("Letter_Pen_Second", (-0.46, 1.44, 0.7735), 0.005, 0.13,
             (0.52, 0.30, 0.24, 1.0), axis='Y', segments=6)
    make_cyl("Letter_Coffee_Cup", (-0.76, 1.30, 0.813), 0.040, 0.088,
             (0.86, 0.82, 0.76, 1.0), segments=10)

    # ── LENA'S PHONE · by her place at the table ──
    make_box("Lena_Phone", (-0.95, 1.30, 0.774), (0.070, 0.140, 0.012),
             (0.16, 0.16, 0.18, 1.0))
    make_box("Lena_Phone_Screen", (-0.95, 1.30, 0.781), (0.058, 0.124, 0.002),
             (0.30, 0.36, 0.44, 1.0))

    # ── THE BREAD · counter between drainer and grinder ──
    make_box("Bread_Board", (-2.14, 2.08, 0.935), (0.30, 0.20, 0.018), COL_WOOD)
    make_box("Bread_Loaf", (-2.18, 2.10, 0.979), (0.150, 0.095, 0.070),
             (0.76, 0.58, 0.34, 1.0))
    make_box("Bread_Slice", (-2.03, 2.04, 0.951), (0.020, 0.090, 0.014),
             (0.88, 0.78, 0.58, 1.0))
    make_box("Bread_Knife", (-2.10, 1.99, 0.947), (0.190, 0.024, 0.006), COL_STEEL)
    make_box("Bread_Knife_Handle", (-1.985, 1.99, 0.947), (0.040, 0.028, 0.014), COL_WOOD)

    # ── THE BOWL · the east place setting, an inch off true ──
    make_cyl("Table_Place_Bowl", (-0.40, 1.60, 0.790), 0.075, 0.044,
             (0.58, 0.52, 0.46, 1.0), segments=12)
    make_cyl("Table_Place_Bowl_Inner", (-0.40, 1.60, 0.8145), 0.058, 0.005,
             (0.42, 0.36, 0.30, 1.0), segments=12)


def main():
    clear_scene()
    build_shell()
    build_kitchen()
    build_kitchen_table()
    build_front_room()
    build_bedroom()
    build_dressing()
    build_canvas_2026_08()
    build_starfish_nebula_2026_08()
    build_wear_personality_2026_08()
    build_hero_props_2026_09()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/lena_apartment.glb"))
    print(f"\n[build_lena_apartment] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
