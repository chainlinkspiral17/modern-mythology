"""board_lords_interior — Kai's SKATEBOARD shop on Main (vol7).

REBUILT 2026-08-03 hero-prop pass: the previous build was a
board-GAME store (gondolas of boxed games, dice case, demo table) —
a wrong-shop read of the name. All five vol7 scenes are a skate
shop: "He cleaned the glass on the deck wall" · "Kai took the board
to the back bench, turned on the work lamp" · "Woke the lathe" ·
"the small drawer under the register where he kept the pieces of
paper" · "The three kids sat on the small bench against the front
window that Kai kept for parents waiting on repairs" · "pulled the
kettle out from under the counter… put it on the small electric
burner" · Devon's old desk in the back office with two boxes of
bearings.

Frame: Blender Z-up, y=0 south storefront wall (Main — the
laundromat's sanderling mural across the street), +Y to the back
wall at y=7, x=±4.5, ceiling 2.8. glTF export remaps to Godot
(x, z, -y).

DRAFT 3 (2026-09-19, lore/_VISUAL_PROGRAM.md §3 backgrounds pass; this
scene serves board_lords_interior AND the main_street preset — 15
placements together). Kit furniture (Devon's chair, the counter stool,
the parents' bench); the kettle as a profile with spout and bail on a
coil burner; the work lamp as a clamp, two arms and a cone; the lathe
with a tailstock, tool rest, motor and belt cover and its shavings;
the decks chamfered (a kicked nose is not a plank); pegs under the
parts; the wheels as wheels; the bearings boxes with one flap open;
the front door's push bar and kick plate. THE STREET: Finn's truck is
the kit pickup in the parking lane (it stood on the sidewalk); the
far facade runs the block (30 m) with a corner building each end,
the bookstore window, two parked cars at the far curb, a second
streetlamp, three rain puddles on Main; the near streetlamp on the
sidewalk, not the road. LAYOUT fixes: the repair bench's east end
inside the counter, the office partition through the counter's back,
the wheel bin in the east wall, the bearings boxes in Devon's chair,
the truck on the sidewalk. WEAR: the entry path, two roll-in wheel
lines from the door, three sit patches on the parents' bench, Kai's
stand spot at the deck-wall glass, the kid-height smudge on the front
window, the counter's elbow strip, the bench top's scars. D3: the
door switch, two outlets, cords from the lathe and the lamp, the
EXIT sign over the alley door (lit).
Draft 4 targets: trucks + wheels under three wall decks (complete
boards); a griptape sheet roll; the register's cord; a bell on a
spring over the door; the awning's valance scallops; the laundromat's
interior glow through its window at dusk; Deck: main_street preset +
shot_establish_b for the street's depth.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_chamfer_box, make_cyl, make_lathe, make_tube, make_rot_box, make_blob, export_glb
from _props.furniture import make_chair, make_stool, make_bench
from _props.detail import make_traffic_wear, make_floor_stain, make_light_switch, make_wall_outlet
from _props.vehicles import make_car
from _props.structure import make_floor, make_wall, make_ceiling, make_window
from _props.store_fixtures import make_counter, make_register
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture

ROOM_W = 9.0; ROOM_D = 7.0; CEIL = 2.8
PAL_WALL = {"wall": (0.50, 0.46, 0.42, 1.0), "baseboard": (0.24, 0.20, 0.16, 1.0)}
COL_FLOOR = (0.44, 0.34, 0.24, 1.0); COL_SEAM = (0.28, 0.20, 0.14, 1.0)
COL_WOOD = (0.42, 0.30, 0.18, 1.0)
COL_STEEL = (0.58, 0.60, 0.62, 1.0)
COL_GLASS = (0.55, 0.62, 0.66, 0.35)
CROW_X = 4.3   # the kit pickup's cab centre (rear glass 3.61 .. windshield 5.02, recorded)
# Deck graphics — a mixed wall of boards
DECK_TINTS = [(0.72, 0.26, 0.22, 1.0), (0.26, 0.44, 0.62, 1.0), (0.86, 0.72, 0.26, 1.0),
              (0.30, 0.52, 0.36, 1.0), (0.56, 0.34, 0.60, 1.0), (0.88, 0.86, 0.80, 1.0),
              (0.20, 0.22, 0.26, 1.0), (0.80, 0.48, 0.24, 1.0)]


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    # Back wall with a gap for the alley door (x ~ +3.4)
    make_wall("Wall_N_W", (-1.0, ROOM_D, 0), length=7.0, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_N_E", (4.15, ROOM_D, CEIL/2.0), (0.9, 0.20, CEIL), PAL_WALL["wall"])
    make_box("Wall_N_AboveAlley", (3.15, ROOM_D, CEIL-0.30), (1.1, 0.20, 0.60), PAL_WALL["wall"])
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    # Alley door leaf ("He pulled the truck out of the alley")
    make_box("Alley_Door", (3.15, ROOM_D-0.04, 1.03), (0.90, 0.05, 2.05), (0.34, 0.30, 0.28, 1.0))
    # Front door: bell + reversible OPEN/CLOSED + the taped note
    make_box("Front_Door", (0.0, 0.04, 1.02), (1.90, 0.04, 2.04), (0.30, 0.28, 0.26, 1.0))
    make_box("Front_Door_Glass", (0.0, 0.03, 1.20), (1.50, 0.02, 1.55), COL_GLASS)
    # (2026-09-22: the bell hangs from a bracket under the header — it
    # floated over the door with nothing holding it)
    make_box("Door_Bell_Bracket", (0.0, 0.16, 2.44), (0.03, 0.12, 0.12), (0.22, 0.20, 0.18, 1.0))
    make_cyl("Door_Bell", (0.0, 0.16, 2.35), 0.04, 0.06, (0.74, 0.58, 0.28, 1.0), segments=8)
    # (draft 3) the push bar and the kick plate
    make_tube("Front_Door_Bar", [(-0.70, 0.085, 1.02), (0.70, 0.085, 1.02)], 0.016, COL_STEEL, segments=6)
    for bx in (-0.66, 0.66):
        make_box(f"Front_Door_Bar_Post_{bx:+.1f}", (bx, 0.07, 1.02), (0.03, 0.03, 0.03), COL_STEEL)
    make_box("Front_Door_Kick", (0.0, 0.065, 0.16), (1.70, 0.006, 0.24), COL_STEEL)
    make_box("Open_Sign", (0.35, 0.06, 1.55), (0.24, 0.01, 0.16), (0.86, 0.82, 0.72, 1.0))
    make_box("Taped_Note", (0.35, 0.06, 1.74), (0.14, 0.008, 0.10), (0.94, 0.92, 0.84, 1.0))


def build_deck_wall():
    """The glass-fronted DECK WALL along the west side — the thing
    Kai cleans the glass on."""
    make_box("DeckWall_Back", (-4.44, 3.8, 1.30), (0.06, 4.4, 2.30), (0.30, 0.26, 0.22, 1.0))
    for r in range(2):
        for c in range(7):
            dy = 1.85 + c * 0.62
            dz = 0.85 + r * 1.05
            tint = DECK_TINTS[(r * 7 + c) % len(DECK_TINTS)]
            make_chamfer_box(f"Deck_{r}_{c}", (-4.36, dy, dz), (0.05, 0.22, 0.82), tint, chamfer=0.03)
            make_box(f"Deck_{r}_{c}_Stripe", (-4.33, dy, dz + 0.15), (0.04, 0.18, 0.10),
                     DECK_TINTS[(r * 7 + c + 3) % len(DECK_TINTS)])
    # The glass front Kai cleans — its frame on two end posts, the glass
    # itself as two glints (2026-09-24: a 4.3 x 2.2 m "glass" slab — this
    # pipeline has no alpha, so it rendered as a lavender wall over every
    # deck; the insert_decks / insert_deckwall frames were one flat colour)
    for pe, py_ in (("S", 1.625), ("N", 5.975)):
        make_box(f"DeckWall_Glass_Post_{pe}", (-4.10, py_, 1.225), (0.05, 0.05, 2.45), COL_STEEL)
    make_box("DeckWall_Glass_Frame_T", (-4.10, 3.8, 2.42), (0.05, 4.30, 0.06), COL_STEEL)
    make_box("DeckWall_Glass_Frame_B", (-4.10, 3.8, 0.18), (0.05, 4.30, 0.06), COL_STEEL)
    for gi, (gy, gw) in enumerate(((2.3, 0.03), (2.45, 0.012), (4.9, 0.02))):
        make_box(f"DeckWall_Glint_{gi}", (-4.10, gy, 1.30), (0.004, gw, 2.18), (0.86, 0.90, 0.92, 1.0))


def build_counter():
    """Sales counter, the stool behind it, the small drawer under
    the register, the kettle + electric burner underneath."""
    # make_counter's `depth` is the X extent, `length` the Y —
    # so length>depth built this counter ROTATED 90 DEGREES:
    # a narrow face against the wall and the run jutting into
    # the room. Swapped 2026-08-12 (same bug as the New
    # Orleans bar and the pit stop's lunch counter).
    # out of the door's swing (2026-09-24, the user: doorways obstructed)
    top_z = make_counter("Register", (2.25, 5.380, 0.0), length=1.00, depth=2.40, height=0.95,
                         palette={"formica": (0.52, 0.42, 0.30, 1.0),
                                  "top": (0.30, 0.22, 0.14, 1.0), "kick": (0.24, 0.18, 0.12, 1.0)})
    make_register("Register", (2.6, 5.280, top_z))
    # The small drawer under the register (the pieces of paper live here)
    make_box("Register_Drawer", (1.75, 4.900, 0.72), (0.40, 0.02, 0.14), (0.34, 0.24, 0.16, 1.0))
    make_box("Register_Drawer_Pull", (1.75, 4.880, 0.72), (0.10, 0.015, 0.03), COL_STEEL)
    # The stool behind the counter
    # (draft 3: the kit stool — turned legs, a foot ring)
    make_stool("Counter_Stool", 2.25, 6.15, h=0.72, wood=COL_WOOD)
    # Kettle on its small electric burner, the low shelf at the
    # counter's west end (draft 3: a profile with spout + bail, a coil)
    make_box("Under_Shelf", (0.75, 5.5, 0.28), (0.60, 0.60, 0.03), COL_WOOD)
    make_box("Electric_Burner", (0.75, 5.5, 0.325), (0.26, 0.26, 0.06), (0.22, 0.22, 0.24, 1.0))
    make_lathe("Electric_Burner_Coil", (0.75, 5.5, 0.358), [(0.075, 0.0), (0.085, 0.006), (0.075, 0.012)], (0.30, 0.28, 0.28, 1.0), segments=14, loop=True)
    make_lathe("Kettle", (0.75, 5.5, 0.365), [(0.0, 0.0), (0.085, 0.0), (0.095, 0.05), (0.09, 0.13), (0.06, 0.17), (0.035, 0.175), (0.035, 0.19), (0.0, 0.19)], COL_STEEL, segments=12)
    make_tube("Kettle_Spout", [(0.83, 5.5, 0.45), (0.90, 5.5, 0.52), (0.93, 5.5, 0.56)], 0.012, COL_STEEL, segments=6)
    make_tube("Kettle_Bail", [(0.75, 5.44, 0.53), (0.75, 5.46, 0.62), (0.75, 5.54, 0.62), (0.75, 5.56, 0.53)], 0.008, (0.18, 0.17, 0.16, 1.0), segments=5)


def build_repair_back():
    """The back of the shop: repair bench + work lamp + the lathe,
    each with its own light — 'turned on the back light over the
    repair bench.'"""
    # (draft 3: the bench at x -0.2 — its east end sat 5 cm inside the
    # counter's west end)
    bx = -0.2
    make_chamfer_box("Repair_Bench", (bx, 6.2, 0.45), (2.20, 0.70, 0.90), COL_WOOD)
    make_chamfer_box("Repair_Bench_Top", (bx, 6.2, 0.92), (2.26, 0.76, 0.05), (0.32, 0.24, 0.16, 1.0))
    # A board mid-repair on the bench, trucks off
    make_box("Repair_Board", (bx + 0.15, 6.15, 0.96), (0.80, 0.22, 0.03), DECK_TINTS[1])   # on the bench
    make_box("Repair_Truck_Loose", (bx - 0.45, 6.3, 0.96), (0.16, 0.10, 0.06), COL_STEEL)
    # the bench vise at the east end, the top's scars
    make_box("Repair_Vise_Body", (bx + 0.95, 6.02, 1.00), (0.16, 0.14, 0.11), (0.28, 0.30, 0.32, 1.0))
    make_box("Repair_Vise_Jaw", (bx + 0.95, 5.90, 1.00), (0.16, 0.05, 0.11), (0.28, 0.30, 0.32, 1.0))
    make_cyl("Repair_Vise_Screw", (bx + 0.95, 5.815, 1.00), 0.012, 0.12, COL_STEEL, axis='Y', segments=6)
    for si, (sx, sy, sl, syaw) in enumerate(((bx - 0.6, 6.05, 0.30, 0.3), (bx + 0.4, 6.40, 0.22, -0.5), (bx - 0.1, 6.45, 0.18, 1.1))):
        make_rot_box(f"Wear_Bench_Scar_{si}", (sx, sy, 0.9465), (sl, 0.012, 0.003), (0.22, 0.16, 0.10, 1.0), yaw=syaw)
    # The clamp work lamp (draft 3: a clamp at the bench's back edge,
    # two arms with an elbow, a cone head — the head where its
    # practical already is)
    make_box("Work_Lamp_Clamp", (bx, 6.56, 0.98), (0.06, 0.08, 0.10), (0.20, 0.19, 0.20, 1.0))
    make_tube("Work_Lamp_Arm", [(bx, 6.56, 1.03), (bx + 0.05, 6.50, 1.45), (bx, 6.30, 1.72)], 0.012, (0.20, 0.19, 0.20, 1.0), segments=6)
    make_lathe("Work_Lamp_Head", (bx, 6.25, 1.52), [(0.03, 0.0), (0.035, 0.05), (0.09, 0.16), (0.0, 0.16)], (0.96, 0.86, 0.55, 1.0), segments=10)
    # The single small tube over the bench (its own light)
    make_fluorescent_tube_fixture("Bench_Light", (bx, 6.2, CEIL), length=1.00, width=0.20)
    # The lathe, west of the bench against the N wall (draft 3: a
    # tailstock, a tool rest, the motor under the bed with its belt
    # cover, shavings on the floor)
    make_chamfer_box("Lathe_Bed", (-2.6, 6.35, 1.00), (1.40, 0.40, 0.25), COL_STEEL)
    for lx in (-3.15, -2.05):
        make_box(f"Lathe_Leg_{lx:.2f}", (lx, 6.35, 0.45), (0.14, 0.34, 0.90), (0.30, 0.32, 0.34, 1.0))
    make_cyl("Lathe_Head", (-3.05, 6.35, 1.20), 0.14, 0.24, (0.30, 0.32, 0.34, 1.0), axis='X', segments=10)
    make_cyl("Lathe_Stock", (-2.5, 6.35, 1.18), 0.05, 0.70, COL_WOOD, axis='X', segments=8)
    make_box("Lathe_Tailstock", (-2.05, 6.35, 1.20), (0.14, 0.16, 0.16), (0.30, 0.32, 0.34, 1.0))
    make_cyl("Lathe_Tail_Centre", (-2.16, 6.35, 1.18), 0.012, 0.10, COL_STEEL, axis='X', segments=6)
    make_box("Lathe_Tool_Rest", (-2.55, 6.14, 1.16), (0.30, 0.03, 0.02), (0.30, 0.32, 0.34, 1.0))
    make_box("Lathe_Tool_Rest_Post", (-2.55, 6.14, 1.05), (0.03, 0.03, 0.20), (0.30, 0.32, 0.34, 1.0))   # on the bed (2026-09-22)
    make_box("Lathe_Motor", (-2.85, 6.35, 0.45), (0.28, 0.24, 0.24), (0.24, 0.24, 0.26, 1.0))
    make_box("Lathe_Belt_Cover", (-3.05, 6.35, 0.80), (0.10, 0.14, 0.50), (0.30, 0.32, 0.34, 1.0))
    # (a shallow lathed mound: the recorder boxes a blob by its full
    # radius, squash or not, so a squashed blob on a floor is a clip)
    make_lathe("Lathe_Shavings", (-2.45, 6.05, 0.004), [(0.0, 0.0), (0.24, 0.0), (0.21, 0.02), (0.13, 0.045), (0.0, 0.06)], (0.70, 0.56, 0.36, 1.0), segments=10)
    for ci in range(4):
        make_tube(f"Lathe_Curl_{ci}", [(-2.7 + ci * 0.16, 5.92 + (ci % 2) * 0.07, 0.01), (-2.66 + ci * 0.16, 5.97 + (ci % 2) * 0.07, 0.04), (-2.6 + ci * 0.16, 5.93 + (ci % 2) * 0.07, 0.02)], 0.006, (0.78, 0.64, 0.42, 1.0), segments=4)


def build_office():
    """The back office: Devon's old desk, the chair Devon also left,
    two cardboard boxes of bearings on the floor."""
    # (draft 3: the partition at y 6.1 — at 6.0 it ran through the
    # counter's back edge)
    make_box("Office_Part", (3.55, 6.1, CEIL/2.0), (1.90, 0.10, CEIL), PAL_WALL["wall"])
    make_chamfer_box("Devon_Desk", (3.900, 6.55, 0.37), (1.00, 0.55, 0.74), COL_WOOD)
    make_box("Devon_Desk_Drawer", (3.390, 6.55, 0.55), (0.02, 0.36, 0.12), (0.34, 0.24, 0.16, 1.0))
    make_box("Devon_Desk_Drawer_Pull", (3.375, 6.55, 0.55), (0.01, 0.08, 0.02), COL_STEEL)
    # the chair Devon also left — a kit chair facing the desk
    import math as _m
    make_chair("Devon_Chair", 3.15, 6.5, yaw=-_m.pi / 2.0, wood=COL_WOOD, w=0.40)
    # two cardboard boxes of bearings — by the counter's east end
    # (ch12: Kai sits on one and looks at the hexagon), one flap open
    for bi, by in enumerate((5.35, 5.68)):
        make_box(f"Bearings_Box_{bi}", (3.95, by, 0.16), (0.34, 0.28, 0.32), (0.60, 0.48, 0.32, 1.0))
    make_rot_box("Bearings_Box_1_Flap", (3.95, 5.55, 0.33), (0.34, 0.14, 0.008), (0.64, 0.52, 0.36, 1.0), roll=1.1)
    make_box("Bearings_Box_0_Label", (3.78, 5.35, 0.18), (0.004, 0.16, 0.10), (0.92, 0.90, 0.84, 1.0))


def build_retail():
    """Small-parts retail: bearings/trucks/wheels/wax pegwall on the
    E wall, plus the waiting bench under the front window."""
    make_box("Parts_Pegboard", (4.44, 4.0, 1.35), (0.05, 2.00, 0.95), (0.62, 0.56, 0.46, 1.0))
    for r in range(3):
        for c in range(5):
            py = 3.2 + c * 0.40
            pz = 1.05 + r * 0.30
            make_box(f"Part_{r}_{c}", (4.38, py, pz), (0.07, 0.16, 0.14),
                     [(0.72, 0.26, 0.22, 1.0), COL_STEEL, (0.86, 0.72, 0.26, 1.0)][(r + c) % 3])
            make_cyl(f"Parts_Peg_{r}_{c}", (4.395, py, pz + 0.09), 0.005, 0.05, COL_STEEL, axis='X', segments=5)
    # Wheels in a low bin (draft 3: the bin off the east wall; the
    # wheels as wheels — rounded edges, a bearing seat)
    make_chamfer_box("Wheel_Bin", (4.1, 2.4, 0.275), (0.55, 0.55, 0.55), COL_WOOD)   # on the floor
    for wi in range(4):
        make_lathe(f"Wheel_{wi}", (4.0 + (wi % 2) * 0.18, 2.3 + (wi // 2) * 0.18, 0.545),   # on the bin (2026-09-22: 7 cm over it)
                   [(0.03, 0.0), (0.06, 0.0), (0.07, 0.012), (0.07, 0.078), (0.06, 0.09), (0.03, 0.09), (0.03, 0.0)],
                   (0.92, 0.88, 0.66, 1.0), segments=12)
    # Front window + the parents' bench under it (NO staged board
    # games — the mural across Main does the window's work)
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    make_window("Win_S", (-2.75, 0.10, 1.55), width=2.60, height=1.50, room_dir=+1)
    # (draft 3: the kit bench)
    make_bench("Wait_Bench", -2.75, 0.55, length=1.80, wood=COL_WOOD, h=0.45)


def build_decor():
    make_wall_clock("Clock", (0.0, 6.900, CEIL-0.45), frozen_hour=10, frozen_min=5, facing='-Y')
    make_floor_plant("Plant", (-4.0, 0.8, 0.0),
                     palette={"leaf": (0.36, 0.48, 0.30, 1.0), "pot": (0.66, 0.40, 0.26, 1.0)})
    for pi, py in enumerate((1.5, 2.6)):
        make_faded_poster(f"Poster_E_{pi}", (ROOM_W/2.0-0.05 - 0.0535, py, 1.55), into_room=-1)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))
    make_hvac_vent("HVAC", (-2.0, ROOM_D-0.5, CEIL), width=0.80, depth=0.40)
    # Shop lighting: two tubes over the retail floor (a shop earns
    # them; the bench has its own)
    for j, ypos in enumerate((1.8, 4.0)):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)


def build_hero_props():
    """The prose-anchored objects (2026-08-31 wave · 5 blind cue ids):

    · THE SANDERLING MURAL + THE PATCH — Janet Halfmoon's thirty-foot
      sanderling on the brick wall ACROSS Main, seen through Win_S.
      Built at the ch10 state: the center patch has taken most of the
      body and, this week, the head ("mostly a flat black shape with
      a beak and one foot"). The street ground plane rides along so
      the far facade doesn't float (ground-plane rule).
    · THE HEXAGON — Olaf's eight cedar pieces on a cloth on the
      counter: six in the ring, the face in the center, the AR I A
      piece beside (ch12: Kai sits on the bearings box and looks).
    · THE BREAD — Hans's Wednesday rye on its board, one cut slice
      (ch10: "The bread was good. The bread was always good.")
    · THE PHONE — Kai's phone face-up on the counter (the patch
      photos, Tem's midnight message).
    """
    # ── Main street + the far facade (through the front window) ──
    # (draft 3: the road ends at the curbs — y -8.0..-2.3; it used to run
    # under both sidewalks, so a car at the curb read as mid-lane)
    make_box("Main_Street", (0.0, -5.15, -0.03), (30.0, 5.7, 0.06),
             (0.30, 0.30, 0.32, 1.0))
    make_box("Main_Sidewalk_Near", (0.0, -1.10, 0.02), (30.0, 1.80, 0.10),
             (0.55, 0.54, 0.50, 1.0))
    make_box("Main_Curb_Near", (0.0, -2.15, 0.03), (30.0, 0.30, 0.12),
             (0.52, 0.52, 0.50, 1.0))
    make_box("Main_Sidewalk_Far", (0.0, -8.45, 0.02), (30.0, 0.90, 0.10),
             (0.55, 0.54, 0.50, 1.0))
    make_box("Across_Facade", (0.0, -9.05, 2.20), (18.0, 0.25, 4.40),
             (0.46, 0.32, 0.26, 1.0))
    # the mural panel: beach bands, then the bird, then the substrate's patch
    make_box("Sanderling_Mural_Sky", (-2.75, -8.90, 2.55), (6.0, 0.06, 1.30),
             (0.72, 0.76, 0.78, 1.0))
    make_box("Sanderling_Mural_Wet", (-2.75, -8.90, 1.62), (6.0, 0.06, 0.60),
             (0.56, 0.62, 0.64, 1.0))
    make_box("Sanderling_Mural_Sand", (-2.75, -8.90, 1.02), (6.0, 0.06, 0.65),
             (0.74, 0.68, 0.56, 1.0))
    make_chamfer_box("Sanderling_Body", (-3.30, -8.845, 1.80), (1.60, 0.05, 0.78),
                     (0.88, 0.87, 0.84, 1.0))
    make_chamfer_box("Sanderling_Head", (-2.32, -8.845, 2.24), (0.46, 0.05, 0.42),
                     (0.88, 0.87, 0.84, 1.0))
    make_box("Sanderling_Beak", (-1.98, -8.85, 2.22), (0.30, 0.04, 0.07),
             (0.28, 0.26, 0.24, 1.0))
    make_box("Sanderling_Leg", (-3.05, -8.85, 1.22), (0.06, 0.04, 0.44),
             (0.30, 0.28, 0.26, 1.0))
    # the patch · flat, black, wrong · body first, the head this week
    make_box("Mural_Patch", (-3.30, -8.855, 1.80), (1.15, 0.03, 1.02),   # on the mural (2026-09-22: 10 cm off it)
             (0.06, 0.06, 0.07, 1.0))
    make_box("Mural_Patch_Head", (-2.32, -8.855, 2.24), (0.52, 0.03, 0.46),
             (0.06, 0.06, 0.07, 1.0))

    # ── the counter still life ──
    top = 0.95
    make_box("Bread_Board", (1.45, 5.35, top + 0.015), (0.46, 0.32, 0.03),
             (0.56, 0.42, 0.26, 1.0))
    make_chamfer_box("Bread_Loaf", (1.42, 5.38, top + 0.10), (0.32, 0.17, 0.13),
                     (0.46, 0.32, 0.18, 1.0))
    make_box("Bread_Slice", (1.66, 5.26, top + 0.05), (0.03, 0.15, 0.11),
             (0.62, 0.50, 0.34, 1.0))
    make_box("Bread_Knife", (1.45, 5.18, top + 0.035), (0.34, 0.035, 0.012),
             COL_STEEL)

    make_box("Hexagon_Cloth", (2.95, 5.50, top + 0.006), (0.64, 0.64, 0.012),
             (0.82, 0.78, 0.70, 1.0))
    import math as _m
    for hi in range(6):
        a = _m.pi / 3.0 * hi + _m.pi / 6.0
        hx = 2.95 + 0.19 * _m.cos(a)
        hy = 5.50 + 0.19 * _m.sin(a)
        make_box(f"Hexagon_Ring_{hi}", (hx, hy, top + 0.03), (0.085, 0.07, 0.036),
                 (0.60, 0.44, 0.28, 1.0))
    make_box("Hexagon_Center_Face", (2.95, 5.50, top + 0.038), (0.10, 0.10, 0.05),
             (0.66, 0.48, 0.30, 1.0))
    make_box("Hexagon_Face_Inlay", (2.95, 5.52, top + 0.066), (0.06, 0.05, 0.008),
             (0.38, 0.26, 0.16, 1.0))
    make_box("Hexagon_Aria_Piece", (2.95, 5.86, top + 0.03), (0.16, 0.06, 0.036),
             (0.60, 0.44, 0.28, 1.0))

    make_box("Shop_Phone", (1.90, 5.78, top + 0.008), (0.16, 0.075, 0.014),
             (0.10, 0.10, 0.12, 1.0))
    make_box("Shop_Phone_Screen", (1.90, 5.78, top + 0.017), (0.14, 0.062, 0.004),
             (0.42, 0.50, 0.58, 1.0))


def build_main_street_2026_09():
    """MAIN STREET, SMOLVUD (re-homing pass, 2026-09-01). Eight vol7
    segments walk this block on a road backdrop; the interior builder
    already carries Main + the mural. This gives the street a face
    from the sidewalk side: Board Lords' awning and sign, the CLOSED
    sign in the door, the laundromat door + window and the shoe-repair
    window flanking the mural on the far facade, a streetlamp at the
    curb, Finn's truck at the curb (ch5: "Finn's truck was at the
    curb"). Presets: main_street (sidewalk, looking across).
    Draft 2: the Daily Grind's corner four blocks down as a far band,
    rain puddles on Main, the bookstore window.
    """
    # Board Lords' front: awning + sign on the parapet, CLOSED sign
    make_box("Shop_Awning", (0.0, -0.62, 2.55), (4.0, 1.00, 0.06), (0.30, 0.34, 0.42, 1.0))
    for ai, ax in enumerate((-1.85, 1.85)):
        make_box(f"Shop_Awning_Arm_{ai}", (ax, -0.60, 2.50), (0.04, 1.02, 0.04), (0.20, 0.20, 0.22, 1.0))   # reaches the wall face and the awning
    make_box("Shop_Sign", (0.0, -0.13, 2.85), (2.40, 0.06, 0.50), (0.22, 0.18, 0.16, 1.0))
    make_box("Shop_Sign_Letters", (0.0, -0.165, 2.85), (2.00, 0.01, 0.22), (0.88, 0.80, 0.52, 1.0))
    make_box("Closed_Sign", (0.55, 0.014, 1.35), (0.22, 0.008, 0.14), (0.90, 0.88, 0.82, 1.0))   # on the door glass, street side
    # the far facade's breaks: laundromat (east of the mural), shoe repair (west)
    make_box("Laundromat_Door", (2.4, -8.92, 1.05), (0.95, 0.04, 2.10), (0.66, 0.64, 0.60, 1.0))
    make_box("Laundromat_Window", (4.2, -8.92, 1.55), (2.00, 0.03, 1.40), (0.55, 0.62, 0.66, 0.6))
    make_box("Laundromat_Sign", (3.3, -8.90, 3.05), (3.60, 0.04, 0.50), (0.24, 0.40, 0.52, 1.0))
    make_box("Shoe_Repair_Window", (-6.0, -8.92, 1.50), (1.40, 0.03, 1.30), (0.50, 0.46, 0.40, 0.6))
    make_box("Shoe_Repair_Sign", (-6.0, -8.90, 2.85), (1.60, 0.04, 0.40), (0.42, 0.30, 0.22, 1.0))
    # streetlamp on the near sidewalk (draft 3: it stood in the road,
    # just off the curb), a lathed base, the arm as a tube
    make_lathe("Streetlamp_Pole", (-4.0, -1.6, 0.07), [(0.14, 0.0), (0.14, 0.06), (0.08, 0.10), (0.06, 0.6), (0.05, 4.3), (0.0, 4.3)], (0.28, 0.28, 0.30, 1.0), segments=8)
    make_tube("Streetlamp_Arm", [(-4.0, -1.6, 4.30), (-3.7, -1.6, 4.36), (-3.3, -1.6, 4.36)], 0.03, (0.28, 0.28, 0.30, 1.0), segments=6)
    make_box("Streetlamp_Head", (-3.2, -1.6, 4.25), (0.40, 0.22, 0.14), (0.92, 0.88, 0.72, 1.0))
    # Finn's truck in the parking lane along Main (draft 3: the kit
    # pickup; the 09-07 move to "the curb" put the old box body on the
    # sidewalk, y -2.15..-0.35 — the sidewalk is -2.0..-0.2)
    make_car("Finn_Truck", 4.6, -3.25, 4.9, (0.44, 0.48, 0.42, 1.0), pickup=True, along="X")
    # the crow rides the cab roof while they get in (ch5: "The crow
    # stayed on Finn's shoulder" — then the truck)
    from _props.creatures import make_crow
    make_crow("Crow", CROW_X, -3.25, 1.70, facing=1.0)
    # ── draft 3 · the block ──
    # the far facade's corner buildings (taller, other brick), the
    # bookstore window west of the shoe repair
    make_box("Across_Corner_W", (-12.0, -9.10, 2.75), (6.0, 0.35, 5.50), (0.52, 0.40, 0.34, 1.0))
    make_box("Across_Corner_E", (12.0, -9.10, 2.60), (6.0, 0.35, 5.20), (0.40, 0.36, 0.34, 1.0))
    make_box("Across_Corner_W_Cornice", (-12.0, -8.90, 5.40), (6.2, 0.10, 0.20), (0.62, 0.50, 0.42, 1.0))
    make_box("Bookstore_Window", (-8.0, -8.92, 1.45), (1.60, 0.03, 1.30), (0.42, 0.36, 0.30, 0.6))
    make_box("Bookstore_Sign", (-8.0, -8.90, 2.70), (1.80, 0.04, 0.40), (0.26, 0.22, 0.30, 1.0))
    for ci, (cx_, col_) in enumerate(((-6.8, (0.30, 0.32, 0.36, 1.0)), (9.2, (0.62, 0.20, 0.16, 1.0)))):
        make_car(f"Far_Car_{ci}", cx_, -7.0, 4.3, col_, along="X")
    make_lathe("Streetlamp_Far_Pole", (6.0, -8.3, 0.07), [(0.14, 0.0), (0.14, 0.06), (0.08, 0.10), (0.06, 0.6), (0.05, 4.3), (0.0, 4.3)], (0.28, 0.28, 0.30, 1.0), segments=8)
    make_tube("Streetlamp_Far_Arm", [(6.0, -8.3, 4.30), (6.0, -8.0, 4.36), (6.0, -7.6, 4.36)], 0.03, (0.28, 0.28, 0.30, 1.0), segments=6)
    make_box("Streetlamp_Far_Head", (6.0, -7.5, 4.25), (0.22, 0.40, 0.14), (0.92, 0.88, 0.72, 1.0))
    for pi_, (px_, py_, pr_) in enumerate(((-3.0, -5.5, 0.7), (2.2, -6.6, 0.55), (-7.5, -3.6, 0.8))):
        make_cyl(f"Main_Puddle_{pi_}", (px_, py_, 0.003), pr_, 0.004, (0.46, 0.50, 0.54, 1.0), segments=12)


def build_draft3_2026_09():
    """DRAFT 3 (2026-09-19) · wear and infrastructure — see the module
    docstring. Names carry none of the scene's cue words (deck · door ·
    lathe · bread · hexagon · phone · sanderling · patch · note ·
    window · crow)."""
    floor_dk = (0.38, 0.29, 0.20, 1.0)
    make_traffic_wear("Wear_Path_Entry", [(0.0, 0.4), (0.0, 3.0), (1.8, 3.0), (1.8, 4.6)], width=0.55, tint=floor_dk)
    make_traffic_wear("Wear_Path_Back", [(-0.6, 4.6), (-0.6, 5.5)], width=0.45, tint=floor_dk)
    # two roll-in wheel lines from the door (kids ride in)
    for ri, rx in enumerate((-0.09, 0.09)):
        make_box(f"Wear_Roll_{ri}", (rx + 0.5, 1.7, 0.012), (0.03, 2.6, 0.003), (0.30, 0.23, 0.16, 1.0))
    # three sit patches on the parents' bench, Kai's stand spot at the
    # deck-wall glass, the smudge at kid height on the front window
    for si, sx in enumerate((-3.35, -2.75, -2.15)):
        make_box(f"Wear_Sit_{si}", (sx, 0.55, 0.4515), (0.42, 0.30, 0.003), (0.36, 0.26, 0.16, 1.0))
    make_floor_stain("Wear_Stand_Glass", (-3.75, 3.8), radius=0.30, tint=floor_dk, segments=10)
    make_box("Wear_Win_Smudge", (-2.75, 0.104, 1.05), (1.40, 0.004, 0.10), (0.62, 0.66, 0.68, 0.5))
    make_box("Wear_Elbow", (2.25, 5.03, 0.953), (2.20, 0.06, 0.003), (0.24, 0.17, 0.11, 1.0))
    # D3
    make_light_switch("Switch_1", (1.15, 0.0), axis='X', face_sign=1, z=1.25, aged=True)
    make_wall_outlet("Outlet_N_1", (-2.4, ROOM_D), axis='X', face_sign=-1, z=0.35, aged=True)
    make_tube("Cord_1", [(-2.85, 6.47, 0.35), (-2.4, 6.86, 0.35)], 0.008, (0.16, 0.16, 0.18, 1.0), segments=5)
    make_wall_outlet("Outlet_N_2", (-0.6, ROOM_D), axis='X', face_sign=-1, z=1.10, aged=True)
    make_tube("Cord_2", [(-0.23, 6.60, 0.98), (-0.6, 6.86, 1.10)], 0.008, (0.16, 0.16, 0.18, 1.0), segments=5)
    # the EXIT sign over the alley door (its practical is in the tscn)
    make_box("Exit_Sign", (3.15, ROOM_D - 0.13, 2.62), (0.32, 0.06, 0.16), (0.30, 0.10, 0.08, 1.0))   # on the wall (2026-09-22: 3 cm off it)
    make_box("Exit_Sign_Face", (3.15, ROOM_D - 0.162, 2.62), (0.26, 0.004, 0.10), (0.96, 0.30, 0.22, 1.0))



def build_door_infill_alley_door_2026_09():
    """Alley_Door was narrower than its wall opening (the user, 2026-09-24:
    "doorways ... misaligned"): close the gap to the door and its frame."""
    make_wall("Wall_Fill_Alley_Door_W", (2.600, 7.000, 0), length=0.200, height=2.784, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_Fill_Alley_Door_E", (3.650, 7.000, 0), length=0.100, height=2.784, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)

def main():
    clear_scene()
    build_shell()
    build_deck_wall()
    build_counter()
    build_repair_back()
    build_office()
    build_retail()
    build_hero_props()
    build_main_street_2026_09()
    build_decor()
    build_draft3_2026_09()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/board_lords_interior.glb"))
    build_door_infill_alley_door_2026_09()
    print(f"\n[build_board_lords_interior] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
