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
        make_box(f"KChair_{ci}_Seat", (cx, cy, 0.45), (0.42, 0.42, 0.05), wood)
        make_box(f"KChair_{ci}_Back", (cx+back_dx, cy+back_dy, 0.74),
                 (0.05 if back_dx else 0.42, 0.42 if back_dx else 0.05, 0.52), wood)
        for li, (lx, ly) in enumerate(((-0.16, -0.16), (0.16, -0.16), (-0.16, 0.16), (0.16, 0.16))):
            make_box(f"KChair_{ci}_Leg_{li}", (cx+lx, cy+ly, 0.22), (0.045, 0.045, 0.44), wood)


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
    bx, by = -1.0, ROOM_D - 1.15
    make_box("Bed_Frame", (bx, by, 0.20), (1.50, 1.94, 0.22), (0.42, 0.30, 0.20, 1.0))
    make_box("Bed_Mattress", (bx, by, 0.42), (1.40, 1.84, 0.16), (0.92, 0.86, 0.78, 1.0))
    make_box("Bed_Headboard", (bx, by+1.00, 0.66), (1.54, 0.08, 0.66), (0.40, 0.28, 0.18, 1.0))
    make_box("Bed_Footboard", (bx, by-0.98, 0.42), (1.54, 0.08, 0.34), (0.40, 0.28, 0.18, 1.0))
    make_box("Bed_Pillow_L", (bx-0.36, by+0.68, 0.54), (0.62, 0.36, 0.12), (0.98, 0.94, 0.90, 1.0))
    make_box("Bed_Pillow_R", (bx+0.36, by+0.68, 0.54), (0.62, 0.36, 0.12), (0.98, 0.94, 0.90, 1.0))
    make_box("Bed_Duvet", (bx, by-0.24, 0.52), (1.44, 1.18, 0.10), (0.72, 0.46, 0.52, 1.0))
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


def main():
    clear_scene()
    build_shell()
    build_kitchen()
    build_kitchen_table()
    build_front_room()
    build_bedroom()
    build_dressing()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/lena_apartment.glb"))
    print(f"\n[build_lena_apartment] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
