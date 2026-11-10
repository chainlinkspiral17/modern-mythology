"""hans_bakery_back_kitchen — vol5-7 bakery back-of-house kitchen.

Was well-lit but sparse (a counter, a deck oven, a speed rack, a prep
table, flour sacks, a bowl shelf; ~35 calls). Enriched to a working
bakery kitchen: a taller PROOFER cabinet beside the oven, a planetary
STAND MIXER, a rolling FLOUR BIN, a platform SCALE, a wire COOLING
RACK of loaves, a wall UTENSIL RAIL of hanging tools, a subway-TILE
backsplash band, and a PASS WINDOW to the front counter with a ticket
rail. Room: door/S wall at blender y=0, extends +Y; interior lands at
godot -Z. Props kept inside the 6.0 x 5.0 footprint.

DRAFT 4 (2026-09-19, lore/_VISUAL_PROGRAM.md §3 backgrounds pass, 20
placements). The bakery is vol7's table: six scenes sit the eleven of
them at it, and the chairs were twelve box stacks. This draft:
  · the ten side chairs, both head chairs and the window chair are
    kit chairs (turned legs, spindled backs), Roy's in the darker
    wood; the communal table gets turned legs and leg-to-leg rails;
  · the pass window is CUT THROUGH the south wall and the front of
    house stands beyond it (the display case, the front counter,
    the street window's pre-dawn grey);
  · the hemlock outside Win_W, with ground and a far dark band;
  · the four cedar bowls are lathed and hollow (the 42° insert sees
    an interior now, not a puck); the mixer's bowl and whisk are
    lathed; the oven's doors get bar handles on standoffs;
  · WEAR: the flour path from the prep table to the oven, the seat
    patches down both sides of the table, the elbow strip on the
    table's long edges, the oven-door handle patch, the drip line
    below the counter; D3: the door switch, three outlets, straight
    cords from the mixer, the proofer and the oven.
Draft 5 targets: a hollow proofer with the trays behind real glass
(the door is a tinted slab); the speed-rack loaves and cooling-rack
loaves as lathed loaves with a scored top; a flour haze band at the
prep table (a low alpha slab); Greta's cloth drawer half-open with
the cloth spilling; the crown molding on the south wall segments;
and a Deck frame of shot_establish_b to judge the front-of-house
depth through the pass.

DRAFT 5 (2026-10-09, the overnight run; CLAUDE.md "build big"). Hans
"had set the long dining table for thirteen" in a 6 x 5 m back kitchen
that also held a deck oven, a proofer, a counter, a prep table and two
racks: every aisle was a chair-width and the preset's right third was a
grey slab — the cooling rack's "frame", a SOLID 1.7 m box with its
shelves and loaves inside it (the speed rack's too). The room is
9.0 x 7.6 under 3.0 m now, each area moved rigidly by plan.shifted():
the bake line (counter + mixer W, oven + proofer E) on the new N wall,
the table mid-room with 1.2 m+ aisles all round, the Hemlock-window
corner and the prep bench on the W wall, the racks on the E wall —
open post frames, trays on runners. The S wall (door, pass, bench)
stays where the front of house expects it.
Draft 6 targets: the E aisle is generous now — a bread shelf of the
morning's loaves for the front, or the flour bin's partner; the
proofer as real glass; lathed scored loaves; the flour haze slab;
Greta's drawer half-open; Deck framing.

DRAFT 6 · THE PLAN (2026-11-10, lore/_BACKGROUND_STATUS_2026_11.md). A
plan pass, not a detail pass: 664 of the 695 lines that play here are
not in a back kitchen. The text (vol7 ch15_loft 111-119, ch15_bread 11 /
48 / 87 / 133, ch15_wagon 7-9, ch17_bakery 7 / 39 / 83 / 95, ch17_roy
8-19, ch17_aria 171, ch10_cabin 6-24):
  · "The bakery's MAIN ROOM ... had three long tables: the worktable,
    the cooling rack table, and the dining table Hans had moved in in
    2046." The back door opens into it ("Marina came in last. She
    closed the back door behind her"; "the long table at the end
    nearest the back door"), and so does the FRONT: "the bell rang at
    the front of the bakery ... She walked to the front of the room.
    Greta came out from behind the front counter ... went to the door.
    She opened it ... He looked across the room at the ten at the
    table." "The bread for the morning's customers brought from the
    back to the front cases." "Greta was at the kettle ... Hans's
    wedding-photo on the wall behind her." "The kitchenette sink."
  · the BACK KITCHEN is next door: "Per came in from the back kitchen
    with a basket"; "on the bench in the back kitchen with a coffee";
    "He was at the floured board with his hands at rest on the dough.
    Hans was at the stove. He had two trays out of the oven"; "the
    canvas coat ... on the peg ... a wooden box from the bench by the
    door."
The set had ONE room: the dining table and the ovens together, and the
front of house behind a wall with a pass window in it. Now:
  · THE MAIN ROOM runs from the street wall (y -4.4: the belled door on
    the table's own axis, the front window, the front counter with its
    case, the bread shelves, a waiting bench) under a header where the
    old wall stood (y 0), past the three long tables — the dining table
    (as it was), the WORKTABLE (the baker's bench, E aisle), the COOLING
    RACK TABLE (E wall) — to the kitchenette on the N wall: the sink,
    the kettle, Greta's drawer, the wedding photograph.
  · THE BACK KITCHEN (x -0.9..4.5, y 7.6..11.4) through a doorway in the
    N wall: the deck oven and the proofer (moved, with their wear and
    wiring), the stove, the landing table with the trays, the kneading
    board, the mixer, the speed rack, the flour, and by the door the
    bench with Per's box and the coat on its peg.
  · gone: the south wall and its pass window, the prep table and its
    scale, the rolling cooling rack (it is a table now), the hand sink
    and the interior "back-kitchen light" (the light Marina stands
    under is the one over the back door, outside — it was built in
    pass 69).
Draft 7 targets: the front end is plan and counter only — its D2/D3
(the price tags' rail, the till's cord, wear at the door and along the
counter's customer side, the street window's display ledge with the
morning's loaves); the back kitchen's D2-D4 (grease behind the stove,
the tray landing's burn marks, the proofer's condensate, a window);
the loft stair the text implies ("He came down at five-thirty"); the
kitchenette as a real unit (uppers, the cups Kai and Lena carry); the
cooling rack table's loaves as lathed scored loaves; a Deck read of
establish_b, which now looks the whole length of the room to the
street door.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.vehicles import make_car
from _props.geometry import clear_scene, make_box, make_chamfer_box, make_blob, make_cyl, make_lathe, make_tube, make_taper_cyl, make_rot_box, export_glb
from _props.furniture import make_chair, make_pendant
from _props.detail import make_traffic_wear, make_floor_stain, make_scuff_band, make_light_switch, make_wall_outlet, make_cord_run
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window, make_case_shell, make_wall_with_openings
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture
from _props.plan import shifted

ROOM_W = 9.0; ROOM_D = 7.6; CEIL = 3.0   # draft 5 (2026-10-09): was 6.0 x 5.0 x 2.8
PAL_WALL = {"wall":(0.82,0.70,0.52,1.0),"baseboard":(0.62,0.42,0.22,1.0)}   # draft 5: aged plaster (0.96 yellow washed every frame out)
COL_FLOOR = (0.62,0.46,0.30,1.0); COL_SEAM = (0.32,0.22,0.14,1.0); COL_WOOD = (0.42,0.30,0.18,1.0)
COL_ACCENT = (0.78,0.42,0.22,1.0)
COUNTER_CX = -1.65   # draft 4 · the north counter runs x -2.70..-0.60
# draft 6 (2026-11-10) · the plan
FRONT_D = 4.4                               # the front end: y -4.4 .. 0 (the street wall where the front of house's stood)
BK_X0, BK_X1, BK_Y1 = -0.9, 4.5, 12.4       # the back kitchen, north of the main room's N wall (y 7.6)
BK_DOOR_X = 3.05                            # its doorway in that wall, 1.0 wide
COL_BK_FLOOR = (0.52, 0.50, 0.46, 1.0)

def build_shell():
    # draft 6: one floor and one ceiling from the street wall to the N wall
    span = ROOM_D + FRONT_D
    mid = (ROOM_D - FRONT_D) / 2.0
    make_floor("Floor", (0.0, mid, 0.0), size_x=ROOM_W+0.4, size_y=span+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # (2026-10-07) Wall_W out of the loop: its window is cut
    make_wall_with_openings("Wall_W", (-ROOM_W/2.0, mid, 0), length=span+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=+1, openings=[(2.6 + SH_W[1], 1.50, 1.10, 1.10), (5.60, 1.05, 0.95, 2.10)])   # (pass 69) the back door, N of the window
    # the E wall runs on past the N wall: it is the back kitchen's too
    make_wall("Wall_E", (+ROOM_W/2.0, (BK_Y1 - FRONT_D) / 2.0, 0), length=BK_Y1 + FRONT_D + 0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    # the N wall, with the doorway to the back kitchen
    make_wall_with_openings("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1,
                            openings=[(BK_DOOR_X, 1.05, 1.00, 2.10)])
    # THE STREET WALL: the door on the table's own axis (Roy "looked across
    # the room at the ten at the table")
    make_wall_with_openings("Wall_Street", (0.0, -FRONT_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1,
                            openings=[(0.0, 1.05, 1.00, 2.10), (2.0, 1.55, 2.40, 1.60)])   # the door; the front window (the picture's pane fills the hole)
    # where the house's wall was taken out: a header on two piers
    make_box("Front_Header", (0.0, 0.0, CEIL - 0.22), (ROOM_W - 0.4, 0.26, 0.44), (0.36, 0.26, 0.17, 1.0))
    for k, hx in enumerate((-(ROOM_W/2.0 - 0.32), ROOM_W/2.0 - 0.32)):
        make_box(f"Front_Header_Pier_{k}", (hx, 0.0, 0.16 + (CEIL - 0.60) / 2.0), (0.44, 0.26, CEIL - 0.60), PAL_WALL["wall"])
        make_box(f"Front_Header_Pier_{k}_Base", (hx, 0.0, 0.08), (0.464, 0.284, 0.16), PAL_WALL["baseboard"])
    # plaster on beams (draft 5: the drop-tile grid read as an office; beams in the fill pass)
    make_ceiling("Ceil", (0.0, mid, CEIL), size_x=ROOM_W+0.4, size_y=span+0.4, with_grid=False, with_stains=False,
                 palette={"tile": (0.90, 0.86, 0.78, 1.0)})
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', span, -ROOM_W/2.0+0.10, mid),
            ("Crown_E", 'Y', span, +ROOM_W/2.0-0.10, mid),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10),
            ("Crown_Street", 'X', ROOM_W, 0.0, -FRONT_D+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})
    # ── the back kitchen's shell ──
    bw, bd = BK_X1 - BK_X0, BK_Y1 - ROOM_D
    bcx, bcy = (BK_X0 + BK_X1) / 2.0, (ROOM_D + BK_Y1) / 2.0
    # (its floor and ceiling start where the main room's end, y ROOM_D + 0.2: two slabs sharing a strip flicker)
    make_floor("BK_Floor", (bcx, bcy + 0.15, 0.0), size_x=bw + 0.2, size_y=bd - 0.1, palette={"vinyl": COL_BK_FLOOR, "seam": (0.34, 0.33, 0.31, 1.0)})
    make_wall("BK_Wall_W", (BK_X0, bcy + 0.1, 0), length=bd + 0.2, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("BK_Wall_N", (bcx, BK_Y1, 0), length=bw + 0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_ceiling("BK_Ceil", (bcx, bcy + 0.15, CEIL), size_x=bw + 0.2, size_y=bd - 0.1, with_grid=False, with_stains=False,
                 palette={"tile": (0.88, 0.86, 0.80, 1.0)})
    # the doorway's casing (both faces) and a sill strip between the two floors
    for face, fy in (("S", ROOM_D - 0.112), ("N", ROOM_D + 0.112)):
        for e, ex in (("L", BK_DOOR_X - 0.54), ("R", BK_DOOR_X + 0.54)):
            make_box(f"BK_Door_Casing_{face}_{e}", (ex, fy, 1.07), (0.08, 0.024, 2.14), COL_WOOD)
        make_box(f"BK_Door_Casing_{face}_Head", (BK_DOOR_X, fy, 2.14), (1.16, 0.024, 0.08), COL_WOOD)
    make_box("BK_Door_Sill", (BK_DOOR_X, ROOM_D + 0.07, 0.006), (1.0, 0.34, 0.012), (0.30, 0.22, 0.14, 1.0))

def build_tile():
    # White subway-tile backsplash band behind the north work wall +
    # a tiled wainscot along the east wall, with darker grout seams.
    tile = (0.90, 0.90, 0.86, 1.0); grout = (0.66, 0.64, 0.58, 1.0)
    # draft 6: the band is the kitchenette counter's backsplash
    tx0, tx1 = -ROOM_W/2.0 + 0.2, COUNTER_CX + SH_NW[0] + 1.25     # a backsplash for the kitchenette; plaster E of it
    tcx, tw = (tx0 + tx1) / 2.0, tx1 - tx0
    make_box("Backsplash_N", (tcx, ROOM_D-0.11, 1.35), (tw, 0.02, 0.90), tile)
    for gi in range(6):
        make_box(f"Grout_N_H_{gi}", (tcx, ROOM_D-0.10, 0.95+gi*0.15), (tw, 0.005, 0.01), grout)
    nv = int(tw / 0.52)
    for gi in range(nv + 1):
        make_box(f"Grout_N_V_{gi}", (tx0 + (tw - nv * 0.52) / 2.0 + gi*0.52, ROOM_D-0.10, 1.35), (0.01, 0.005, 0.90), grout)
    make_box("Wainscot_E", (ROOM_W/2.0-0.11, ROOM_D/2.0, 0.70), (0.02, ROOM_D-0.4, 1.20), tile)

def build_counter():
    # make_counter's `depth` is the X extent, `length` the Y —
    # so length>depth built this counter ROTATED 90 DEGREES:
    # a narrow face against the wall and the run jutting into
    # the room. Swapped 2026-08-12 (same bug as the New
    # Orleans bar and the pit stop's lunch counter).
    # Draft 4: 2.10 long, centred at -1.65 — the 2.40 run reached x
    # -0.30 and its SE corner sat inside the communal table's north end
    # (x -0.55, y 3.65..4.0), a clip the recorder's threshold hid.
    top_z = make_counter("Counter", (COUNTER_CX, ROOM_D-1.0, 0.0), length=0.70, depth=2.10, height=0.92,
                         palette={"formica": (0.78, 0.66, 0.42, 1.0), "top": (0.32, 0.22, 0.14, 1.0), "kick": (0.32, 0.22, 0.14, 1.0)})
    make_counter_bullnose("Counter", (COUNTER_CX, ROOM_D-1.0 - 0.35, top_z), length=2.10, axis='X')

def build_stove():
    # Commercial deck oven: stainless body, two glass doors with warm
    # interiors + bar handles, a vent hood above.
    sx, sy = +ROOM_W/4.0, ROOM_D-0.5
    make_chamfer_box("Oven_Body", (sx, sy, 0.75), (1.00, 0.80, 1.50), (0.80, 0.82, 0.86, 1.0))
    for di, dz in enumerate([0.55, 1.05]):
        make_box(f"Oven_Door_{di}", (sx-0.42, sy, dz), (0.06, 0.66, 0.40), (0.28, 0.24, 0.22, 1.0))
        make_box(f"Oven_Window_{di}", (sx-0.46, sy, dz), (0.02, 0.46, 0.24), (1.0, 0.62, 0.26, 0.8))
        make_cyl(f"Oven_Handle_{di}", (sx-0.50, sy, dz-0.24), 0.02, 0.60, P.METAL_STEEL, axis='Y', segments=8)
        for k, hy in enumerate((sy-0.26, sy+0.26)):
            make_cyl(f"Oven_Handle_Post_{di}_{k}", (sx-0.475, hy, dz-0.24), 0.012, 0.05, P.METAL_STEEL, axis='X', segments=6)
    make_chamfer_box("Oven_Hood", (sx, sy, 1.65), (1.10, 0.90, 0.30), P.METAL_STEEL)   # on the oven (2026-09-23: 5 cm over it)

def build_speed_rack():
    """A rolling speed rack of sheet trays + loaves. (Draft 5: the frame
    was one SOLID 0.7 x 0.6 x 1.8 box with the trays inside it; four
    corner posts and a top now.)"""
    # Speed rack (rolling tray rack) near the centre
    # Draft 4: the rack rolled to the east aisle (x 2.5, y 2.7) — at
    # (-2.55, 2.2) its frame shared floor with the window chair AND the
    # prep table once the table moved west off the side chairs.
    rx, ry = 2.5, 2.7
    for pi, (ox, oy) in enumerate(((-0.335, -0.285), (0.335, -0.285), (-0.335, 0.285), (0.335, 0.285))):
        make_box(f"Rack_Post_{pi}", (rx + ox, ry + oy, 0.96), (0.03, 0.03, 1.74), P.METAL_STEEL)
        make_cyl(f"Rack_Caster_{pi}", (rx + ox, ry + oy, 0.045), 0.045, 0.04, P.METAL_BLACK, axis='X', segments=8)
    make_box("Rack_Top", (rx, ry, 1.815), (0.70, 0.60, 0.03), P.METAL_STEEL)
    for ti, tz in enumerate([0.4, 0.7, 1.0, 1.3, 1.6]):
        for sgn in (-1, 1):
            make_box(f"Rack_Runner_{ti}_{sgn:+d}", (rx + sgn * 0.3125, ry, tz - 0.02), (0.015, 0.54, 0.01), P.METAL_STEEL)
    for ti, tz in enumerate([0.4, 0.7, 1.0, 1.3, 1.6]):
        make_box(f"Rack_Tray_{ti}", (rx, ry, tz), (0.64, 0.54, 0.03), (0.72, 0.72, 0.74, 1.0))
        for li in range(3):
            make_cyl(f"Rack_Loaf_{ti}_{li}", (rx-0.2+li*0.2, ry, tz+0.06), 0.06, 0.26, (0.72, 0.52, 0.30, 1.0), axis='X', segments=8)


def build_flour_sacks():
    # Stacked flour sacks in the SW corner
    # seated by their squashed height (2026-09-24)
    for si, (sx2, sz) in enumerate([(-ROOM_W/2.0+0.6, 0.20), (-ROOM_W/2.0+0.55, 0.60), (-ROOM_W/2.0+0.85, 0.20)]):
        make_blob(f"FlourSack_{si}", (sx2, 0.7, sz), 0.21,
                  (0.88, 0.84, 0.76, 1.0), noise=0.16, seed=11 + si,
                  squash=0.95)


def build_bowl_shelf():
    # Wall shelf of mixing bowls, west wall
    make_box("BowlShelf", (-ROOM_W/2.0+0.14, ROOM_D-1.4, 1.7), (0.10, 1.20, 0.06), COL_WOOD)
    for bi in range(3):
        make_cyl(f"Bowl_{bi}", (-ROOM_W/2.0+0.30, ROOM_D-1.9+bi*0.5, 1.80), 0.14, 0.16, P.METAL_STEEL, segments=12)

def build_proofer():
    # Roll-in proofing cabinet on casters, east of the oven: stainless
    # body, a full glass door showing racked trays, a warm proof glow.
    px, py = ROOM_W/2.0 - 0.55, ROOM_D - 1.4
    # (2026-09-24: a SOLID body with the trays inside it, a solid door,
    # and a glass slab on the door — no alpha in this pipeline. Now an
    # open shell, the door a frame round its window, trays side to side,
    # the proof glow on the back panel over each tray.)
    make_case_shell("Proofer_Body", (px, py, 1.00), (0.66, 0.80, 1.90), (0.78, 0.80, 0.84, 1.0), open_face='-X')
    dk = (0.30, 0.30, 0.32, 1.0)
    make_box("Proofer_Door_T", (px-0.30, py, 1.81), (0.06, 0.76, 0.08), dk)
    make_box("Proofer_Door_B", (px-0.30, py, 0.29), (0.06, 0.76, 0.08), dk)
    for sgn, tag in ((-1, "L"), (1, "R")):
        make_box(f"Proofer_Door_{tag}", (px-0.30, py + sgn * 0.325, 1.05), (0.06, 0.11, 1.44), dk)
    for gi, (gy, gw) in enumerate(((-0.16, 0.02), (-0.09, 0.01))):
        make_box(f"Proofer_Glint_{gi}", (px-0.30, py+gy, 1.05), (0.004, gw, 1.44), (0.86, 0.90, 0.92, 1.0))
    make_cyl("Proofer_Handle", (px-0.35, py+0.325, 1.05), 0.02, 0.70, P.METAL_STEEL, axis='Z', segments=8)   # on the door's latch stile
    for ti, tz in enumerate([0.55, 0.85, 1.15, 1.45, 1.75]):
        make_box(f"Proofer_Tray_{ti}", (px+0.03, py, tz), (0.56, 0.76, 0.03), (0.72, 0.72, 0.74, 1.0))
        make_box(f"Proofer_Glow_{ti}", (px+0.30, py, tz+0.08), (0.02, 0.50, 0.10), (1.0, 0.78, 0.42, 0.7))
    for wi, wo in enumerate([-0.26, 0.26]):
        make_cyl(f"Proofer_Wheel_{wi}", (px+wo, py, 0.05), 0.05, 0.05, P.METAL_BLACK, axis='X', segments=8)

def build_mixer():
    # Planetary stand mixer on the north counter's west end.
    mx, my = -ROOM_W/4.0-0.9, ROOM_D-1.0
    top = 0.96
    make_chamfer_box("Mixer_Base", (mx, my, top+0.06), (0.28, 0.34, 0.12), (0.86, 0.84, 0.82, 1.0))
    make_box("Mixer_Column", (mx+0.10, my, top+0.34), (0.14, 0.24, 0.44), (0.86, 0.84, 0.82, 1.0))
    make_chamfer_box("Mixer_Head", (mx-0.06, my, top+0.52), (0.34, 0.22, 0.16), (0.86, 0.84, 0.82, 1.0))
    # Draft 4: a lathed balloon whisk and a bellied bowl (both were
    # straight cylinders).
    make_lathe("Mixer_Whisk", (mx-0.10, my, top+0.20), [(0.012, 0.0), (0.045, 0.04), (0.05, 0.09), (0.03, 0.15), (0.012, 0.18), (0.012, 0.20)], P.METAL_STEEL, segments=8)
    make_lathe("Mixer_Bowl", (mx-0.10, my, top+0.05), [(0.06, 0.0), (0.105, 0.03), (0.13, 0.09), (0.135, 0.15), (0.128, 0.18)], P.METAL_STEEL, segments=12)


def build_flour_bin():
    # Rolling flour ingredient bin in the SW.
    fx, fy = -ROOM_W/2.0+0.55, ROOM_D/2.0+0.75
    make_chamfer_box("FlourBin_Body", (fx, fy, 0.40), (0.50, 0.60, 0.72), (0.72, 0.60, 0.42, 1.0))
    make_box("FlourBin_Lid", (fx, fy, 0.78), (0.52, 0.62, 0.06), (0.56, 0.46, 0.32, 1.0))
    make_cyl("FlourBin_Scoop", (fx, fy-0.10, 0.86), 0.05, 0.14, P.METAL_STEEL, segments=8)
    for wi, wo in enumerate([-0.20, 0.20]):
        make_cyl(f"FlourBin_Wheel_{wi}", (fx+wo, fy, 0.05), 0.05, 0.05, P.METAL_BLACK, axis='X', segments=8)


def build_utensil_rail():
    # Wall rail of hanging tools above the north counter.
    rx0, rx1 = COUNTER_CX-1.0, COUNTER_CX+0.9
    ry = ROOM_D - 0.14
    make_box("Rail", ((rx0+rx1)/2.0, ry, 1.85), (rx1-rx0, 0.03, 0.03), P.METAL_STEEL)
    # the rail's wall brackets (2026-09-23: rail, hooks and tools on air)
    for k, bxk in enumerate((rx0 + 0.05, rx1 - 0.05)):
        make_box(f"Rail_Bracket_{k}", (bxk, ROOM_D - 0.1125, 1.85), (0.03, 0.025, 0.04), P.METAL_STEEL)
    tools = [("Whisk", 0.10, 0.22, P.METAL_STEEL), ("Spatula", 0.05, 0.26, (0.42,0.30,0.18,1.0)),
             ("Scraper", 0.08, 0.20, (0.30,0.42,0.52,1.0)), ("Ladle", 0.07, 0.24, P.METAL_STEEL),
             ("Brush", 0.05, 0.22, (0.62,0.46,0.30,1.0)), ("Sieve", 0.10, 0.18, P.METAL_STEEL)]
    n = len(tools)
    for i, (nm, w, h, col) in enumerate(tools):
        tx = rx0 + (i+0.5)*(rx1-rx0)/n
        make_cyl(f"RailHook_{i}", (tx, ry-0.02, 1.80), 0.006, 0.06, P.METAL_STEEL)
        make_box(f"Tool_{nm}", (tx, ry-0.04, 1.80-h/2.0), (w, 0.03, h), col)

def build_calendar():
    make_calendar("Calendar", (-ROOM_W/2.0+0.1025, 1.4, 1.70))   # on the wall (2026-09-23: 2.7 cm off it)


def build_poster():
    make_faded_poster("Poster_E", (ROOM_W/2.0-0.05 - 0.0535, 1.6, 1.60), into_room=-1)


def build_clock():
    make_wall_clock("Clock", (0.0, 4.900, CEIL-0.50), frozen_hour=6, frozen_min=1, facing='-Y')

def build_ceiling_infra():
    # tubes over the bake line only; the table has its pendants (draft 5 fill)
    # draft 6: the bake line is in the back kitchen, and its tubes with it
    for j, (fx_, fy_) in enumerate(((0.6, 10.0), (3.0, 10.0))):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (fx_, fy_, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def build_communal_table():
    """2026-08-03 hero-prop pass. THE TABLE — all six scenes are
    staged at it: "The ten of them were at the table. Tem at one
    end. Hans at the other." / "the eleven of us at the table." Long
    N-S run down the room center, ten side chairs + two head chairs
    (the far head is ROY'S CHAIR — the four carved crows watch it).
    Plus the Hemlock window with its sill, the chair by the window,
    Greta's cloth drawer, the chapbook drawer, and the table
    dressing (press, brotchen basket, preserves)."""
    wood = (0.46, 0.34, 0.22, 1.0)
    wood_dk = (0.36, 0.26, 0.16, 1.0)
    make_chamfer_box("Communal_Table_Top", (0.0, 2.3, 0.75), (1.10, 3.40, 0.06), wood)
    # Draft 4: turned legs, an apron under the top, leg-to-leg rails
    # at shin height with a cross rail (the legs were four posts).
    make_box("Communal_Apron", (0.0, 2.3, 0.695), (1.00, 3.30, 0.05), wood_dk)
    for lx, ly in ((-0.50, 0.75), (0.50, 0.75), (-0.50, 3.85), (0.50, 3.85)):
        make_lathe(f"Communal_Leg_{lx:.1f}_{ly:.2f}", (lx, ly, 0.0),
                   [(0.045, 0.0), (0.055, 0.04), (0.038, 0.10), (0.042, 0.34), (0.058, 0.44), (0.042, 0.54), (0.042, 0.66), (0.05, 0.69), (0.05, 0.72)],
                   wood_dk, segments=8)
    for ri, rx in enumerate((-0.50, 0.50)):
        make_tube(f"Communal_Rail_{ri}", [(rx, 0.75, 0.15), (rx, 3.85, 0.15)], 0.018, wood_dk, segments=5)
    make_tube("Communal_Rail_X", [(-0.50, 2.3, 0.15), (0.50, 2.3, 0.15)], 0.018, wood_dk, segments=5)
    # Ten side chairs — kit chairs (turned legs, spindled backs) facing
    # the table; the fifth pair sits at 3.60 (was 3.35, 0.40 from the
    # fourth — two 0.42 seats cannot share 0.40).
    import math as _m
    for si, cy in enumerate((1.0, 1.65, 2.30, 2.95, 3.60)):
        for xi, cx in enumerate((-0.85, 0.85)):
            make_chair(f"TChair_{si}_{xi}", cx, cy, yaw=(-_m.pi/2.0 if cx < 0 else _m.pi/2.0), wood=wood, w=0.42)
    # Head chairs: Tem's (near, back to the door) and ROY'S (far —
    # distinct, darker, a hair wider)
    make_chair("Head_Chair", 0.0, 0.45, yaw=0.0, wood=wood, w=0.42)
    make_chair("Roys_Chair", 0.0, 4.15, yaw=_m.pi, wood=wood_dk, w=0.44)
    # Table dressing: coffee press, brotchen basket, preserves, butter
    make_cyl("Coffee_Press", (0.0, 2.7, 0.90), 0.06, 0.24, (0.55, 0.62, 0.66, 0.6), segments=10)
    make_cyl("Press_Plunger", (0.0, 2.7, 1.04), 0.012, 0.08, (0.20, 0.19, 0.20, 1.0), segments=6)
    make_chamfer_box("Brotchen_Basket", (0.0, 2.1, 0.84), (0.34, 0.28, 0.12), (0.62, 0.46, 0.26, 1.0))
    for bi in range(3):
        make_cyl(f"Brotchen_{bi}", (-0.08 + bi * 0.09, 2.1, 0.92), 0.05, 0.07, (0.80, 0.62, 0.36, 1.0), segments=8)
    make_cyl("Preserve_Jar", (0.28, 2.45, 0.85), 0.045, 0.12, (0.48, 0.22, 0.30, 0.9), segments=8)
    make_box("Butter_Dish", (-0.28, 2.45, 0.80), (0.16, 0.10, 0.06), (0.90, 0.88, 0.80, 1.0))


def build_window_corner():
    import math as _m
    wood = (0.46, 0.34, 0.22, 1.0)
    # The Hemlock window + sill + the chair beside it (W wall)
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    make_window("Win_W", (-2.90, 2.6, 1.50), width=1.10, height=1.10, axis='Y', room_dir=+1, see_through=True)
    make_box("Win_W_Sill", (-2.86, 2.6, 0.95), (0.26, 1.10, 0.06), wood)
    # (draft 4: a kit chair, back to the window, at y 2.75 — at 2.6 its
    # seat shared 0.1 m with the speed rack's frame)
    make_chair("WinChair", -2.35, 2.75, yaw=-_m.pi/2.0, wood=wood, w=0.40)


def build_counter_drawers():
    wood_dk = (0.36, 0.26, 0.16, 1.0)
    # Greta's cloth drawer + the chapbook drawer, N counter faces
    make_box("Greta_Drawer", (-1.5, 3.64, 0.74), (0.44, 0.02, 0.16), wood_dk)   # on the counter face (2026-09-23: 2 cm off it)
    make_box("Greta_Cloth", (-1.5, 3.70, 0.70), (0.20, 0.12, 0.02), (0.88, 0.86, 0.80, 1.0))
    make_box("Chapbook_Drawer", (-1.9, 3.64, 0.56), (0.44, 0.02, 0.16), wood_dk)


def build_pers_box_2026_08():
    """PER'S WOODEN BOX (--props, 2026-08 · [shot:insert box] x4).

    Canon: "He picked up a wooden box from the bench by the door.
    The box was about a foot long and six inches deep, with a
    hinged lid." The bench did not exist either. Both do now, by
    the south door where Per hangs the canvas coat.
    """
    wood = (0.52, 0.40, 0.28, 1.0)
    wood_dk = (0.40, 0.30, 0.20, 1.0)
    brass = (0.62, 0.52, 0.30, 1.0)
    bx, by = 1.35, 0.42
    make_box("DoorBench_Seat", (bx, by, 0.44), (1.10, 0.34, 0.05), wood)
    for li, lx in enumerate((bx - 0.46, bx + 0.46)):
        make_box("DoorBench_Leg_%d" % li, (lx, by, 0.21), (0.05, 0.30, 0.42), wood_dk)
    # The box: ~0.30 x 0.15, hinged lid sitting a hair proud.
    make_box("PersBox_Body", (bx - 0.22, by, 0.525), (0.305, 0.155, 0.115), wood)
    make_box("PersBox_Lid", (bx - 0.22, by, 0.590), (0.315, 0.165, 0.022), wood_dk)
    for hi, hy in enumerate((by - 0.05, by + 0.05)):
        make_box("PersBox_Hinge_%d" % hi, (bx - 0.065, hy, 0.578),
                 (0.014, 0.030, 0.020), brass)
    make_box("PersBox_Clasp", (bx - 0.375, by, 0.560), (0.010, 0.035, 0.030), brass)
    # The coat peg row above the bench (the canvas coat's home).
    for pi2, py2 in enumerate((by - 0.10, by + 0.14)):
        # out of the S wall beside the door (2026-09-23: two pegs in the air
        # in front of the pass window)
        make_cyl("DoorPeg_%d" % pi2, (1.08 + pi2 * 0.16, 0.145, 1.52), 0.016, 0.09,
                 wood_dk, segments=6, axis='Y')


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    Six cues fire here with no marker; four had no geometry at all.
    The bakery chapters (ch15/ch17) put vol7's heaviest objects on
    THE TABLE, and the table only had breakfast on it:

    - THE FOUR CEDAR BOWLS (ch17_aria): "The figures on the four
      bowls — Tem registered, watching from above as she stood at
      the table — began to align." Four palm-and-two-hands cedar
      bowls in a loose cluster at the table's north half, each with
      the spiral rim. The second one is the substrate-bowl.
    - THE CROW (ch17_aria): "The crow stood on the rim of the
      substrate-bowl and looked down at the young woman inside it."
      Perched on the rim, head over the interior, beak down-table.
    - THE HANDS (ch17_bakery): "Aud put her hand briefly on Marit's
      hand on the table." Rendered as residue, not figures: two
      floured handprints at the west seat, Aud's lapped flush
      against Marit's — a baker's table remembers hands in flour.
    - THE BACK-KITCHEN LIGHT (ch15_loft): "Hans's back-kitchen
      light at four AM had been listed as one of the reliable
      markers" — a wall shade + warm bulb over the south door,
      the light Marina stands under at five forty-seven.
    (window aims at Win_W — the Hemlock window already built.)

    Draft note: bowls are static cedar here; the figures-that-move
    live in prose and mood, not geometry. Draft N+1 could give the
    substrate-bowl its own inner figure blocks once a close-up
    camera proves the 42° insert actually resolves them.
    """
    cedar = (0.55, 0.38, 0.26, 1.0)
    cedar_dk = (0.44, 0.30, 0.20, 1.0)
    flour = (0.92, 0.90, 0.84, 1.0)
    crow_black = (0.10, 0.10, 0.12, 1.0)

    # ── THE FOUR CEDAR BOWLS · table north half, top z 0.78 ──
    bowl_xy = ((-0.30, 3.10), (0.10, 3.05), (0.30, 3.30), (-0.10, 3.40))
    for bi, (bx, by) in enumerate(bowl_xy):
        # (draft 4: a bellied lathe on a foot, not a puck)
        make_lathe(f"Cedar_Bowl_{bi}", (bx, by, 0.78), [(0.040, 0.0), (0.040, 0.006), (0.072, 0.02), (0.085, 0.04), (0.085, 0.055)], cedar, segments=12)
        make_cyl(f"Cedar_Bowl_Rim_{bi}", (bx, by, 0.8375), 0.068, 0.005,
                 cedar_dk, segments=12)

    # ── THE CROW · on the substrate-bowl's rim (bowl 1) ──
    make_cyl("Crow_Leg_0", (0.136, 3.014, 0.8425), 0.004, 0.005, crow_black, segments=6)
    make_cyl("Crow_Leg_1", (0.146, 3.002, 0.8425), 0.004, 0.005, crow_black, segments=6)
    make_box("Crow_Body", (0.141, 3.008, 0.876), (0.055, 0.095, 0.062), crow_black)
    make_box("Crow_Head", (0.113, 3.036, 0.924), (0.036, 0.036, 0.034),
             (0.12, 0.12, 0.14, 1.0))
    make_box("Crow_Beak", (0.080, 3.036, 0.916), (0.030, 0.024, 0.012),
             (0.16, 0.15, 0.14, 1.0))
    make_box("Crow_Tail", (0.1985, 3.008, 0.885), (0.060, 0.040, 0.014), crow_black)

    # ── 2026-09-01 second pass: the three cues the first wave's
    # truncated listing hid (brioche / coffee / bag; coffee aims
    # at the existing press) ──
    # THE BRIOCHE ("The brioche on the table held the room."):
    # plate + three braided lobes, table south-east
    make_cyl("Brioche_Plate", (0.32, 1.95, 0.786), 0.110, 0.012,
             (0.92, 0.90, 0.86, 1.0), segments=12)
    for li2, lx2 in enumerate((0.26, 0.32, 0.38)):
        make_cyl(f"Brioche_Lobe_{li2}", (lx2, 1.95, 0.817), 0.038, 0.050,
                 (0.78, 0.56, 0.28, 1.0), segments=8)
    # ── THE HANDS · floured prints at the west seat (y 1.65) ──
    # (pass 86: no character's name in a prop's name — it answers that
    # character's closeup cue; the two pairs are Marit's and Aud's)
    for who, py, fy0 in (("A", 1.620, 1.585), ("B", 1.705, 1.670)):
        make_box(f"Hands_Print_{who}", (-0.400, py, 0.7815), (0.070, 0.085, 0.0015), flour)
        for fi in range(4):
            make_box(f"Hands_Print_{who}_F{fi}", (-0.325, fy0 + fi * 0.022, 0.7815),
                     (0.055, 0.014, 0.0015), flour)



def build_door_props():
    # (draft 6: the wall shade over the old south door is gone with the
    # wall. "The bakery's back-kitchen light was on" is read from OUTSIDE,
    # and "at the back door under that light" is Bakery_Back_Light.)
    # THE BAG ("She handed him the bag."): the canvas stick bag on
    # the door bench beside Per's box
    make_box("Canvas_Bag", (1.62, 0.42, 0.555), (0.28, 0.20, 0.18),
             (0.62, 0.58, 0.48, 1.0))
    make_box("Canvas_Bag_Strap", (1.62, 0.42, 0.657), (0.24, 0.05, 0.024),
             (0.48, 0.44, 0.36, 1.0))


def build_draft4_2026_09():
    """DRAFT 4 (2026-09-19, lore/_VISUAL_PROGRAM.md §3). Wear, D3, D5 —
    see the module docstring. Cords are straight make_tube runs: the
    cord helper's diagonal segments are axis-aligned SLABS, not cords
    (its midpoint dips to half height, so a counter-to-outlet run is
    a 0.4 m plank behind the counter). Draft 5 split this pass by AREA
    (the build_wear_* / build_d3_* functions below) so each part moves
    with the furniture it belongs to; the paths are re-walked here."""
    floor_dk = (0.54, 0.40, 0.26, 1.0)
    flour_dk = (0.72, 0.58, 0.42, 1.0)
    # ── WEAR · the paths, re-walked on the draft-5 plan ──
    # the flour path: prep table → up the west aisle past the window
    # chair → the mixer end of the counter (the bakers' morning)
    make_traffic_wear("Wear_Path_Flour", [(-3.1, 2.55), (-2.7, 3.4), (-2.6, 5.0), (-2.7, 6.0)], width=0.55, tint=flour_dk)
    # the oven approach down the east aisle to the oven doors
    # draft 6: the bread's path, the back kitchen's doorway down the east
    # aisle to the front cases; and the customers', the street door to the counter
    make_traffic_wear("Wear_Path_Oven", [(BK_DOOR_X, ROOM_D - 0.5), (1.75, 5.9), (1.75, 0.6), (2.2, -1.3)], width=0.45, tint=floor_dk)
    make_traffic_wear("Wear_Path_Door", [(0.0, -FRONT_D + 0.35), (0.5, -3.2), (1.6, -2.75)], width=0.9, tint=floor_dk)


def build_wear_table():
    for si, cy in enumerate((1.0, 1.65, 2.30, 2.95, 3.60)):
        for xi, cx in enumerate((-0.85, 0.85)):
            make_floor_stain(f"Wear_Seat_{si}_{xi}", (cx, cy), radius=0.25, tint=(0.58, 0.43, 0.28, 1.0), segments=10)
    # the elbow strips down the table's long edges (eleven forearms a
    # morning)
    for ei, ex in enumerate((-0.50, 0.50)):
        make_box(f"Wear_Edge_{ei}", (ex, 2.3, 0.7815), (0.06, 3.20, 0.003), (0.40, 0.29, 0.18, 1.0))


def build_wear_oven():
    # the grip patch under each oven handle, the proofer's door-edge patch
    sx, sy = +ROOM_W/4.0, ROOM_D-1.0
    for di, dz in enumerate([0.55, 1.05]):
        make_box(f"Wear_Grip_{di}", (sx-0.452 - 0.0506, sy, dz-0.19), (0.004, 0.30, 0.08), (0.36, 0.32, 0.30, 1.0))
    make_box("Wear_Proofer_Edge", (ROOM_W/2.0-0.55-0.342, ROOM_D-1.4+0.24, 1.05), (0.003, 0.05, 0.60), (0.62, 0.62, 0.64, 1.0))


def build_wear_counter():
    # the kick scuff on the counter's face below the drawers
    make_scuff_band("Wear_Kick", (-1.0, ROOM_D-1.0-0.356), 0.8, axis='X', height=0.10, band_z=0.30, tint=(0.24, 0.16, 0.10, 1.0))


_CORD = (0.16, 0.16, 0.18, 1.0)


def build_d3_nw():
    make_wall_outlet("Outlet_N_1", (-2.30, ROOM_D-0.02), axis='X', face_sign=-1, z=1.175, aged=True)
    make_tube("Cord_1", [(-2.35, 4.19, 1.00), (-2.30, 4.86, 1.175)], 0.008, _CORD, segments=5)


def build_d3_ne():
    make_wall_outlet("Outlet_N_2", (2.35, ROOM_D), axis='X', face_sign=-1, z=0.40, aged=True)
    make_tube("Cord_2", [(2.02, 4.60, 0.40), (2.35, 4.86, 0.40)], 0.008, _CORD, segments=5)


def build_d3_e():
    make_wall_outlet("Outlet_E_1", (ROOM_W/2.0-0.02, 3.4), axis='Y', face_sign=-1, z=0.35, aged=True)
    # (draft 6: Cord_3 ran to the rolling cooling rack, which is a table now)


def build_hemlock():
    # ── D5 · the hemlock outside Win_W (4 AM: near-black green) ──
    make_box("Hemlock_Ground", (-5.6, 2.6, -0.03), (5.0, 7.0, 0.05), (0.16, 0.18, 0.14, 1.0))
    make_taper_cyl("Hemlock_Trunk", (-4.7, 2.3, 0.0), 0.20, 0.08, 4.2, (0.20, 0.16, 0.13, 1.0), segments=8)
    for ci, (cz, cr) in enumerate(((2.4, 1.4), (3.4, 1.1), (4.3, 0.7))):
        make_blob(f"Hemlock_Canopy_{ci}", (-4.7, 2.3, cz), cr, (0.14, 0.24, 0.18, 1.0), noise=0.24, seed=31+ci, squash=0.7)
    make_taper_cyl("Hemlock_Trunk_Far", (-6.4, 1.2, 0.0), 0.16, 0.07, 4.0, (0.16, 0.13, 0.11, 1.0), segments=6)
    make_blob("Hemlock_Canopy_Far", (-6.4, 1.2, 3.0), 1.5, (0.11, 0.19, 0.15, 1.0), noise=0.24, seed=37, squash=0.75)
    make_box("Hemlock_Far_Band", (-24.0, 2.6, 2.2), (0.20, 40.0, 4.6), (0.06, 0.08, 0.12, 1.0))   # (pass 69) past Hemlock Street now


def build_back_door_2026_10():
    """THE BACK DOOR AND THE SIDE LOT (pass 69, 2026-10-11): vol7 ch18 Stick
    — "Eight twelve at the back door of the bakery... Finn had been at the
    truck. He had been about to get in when Tem came out of the back door
    with a brown paper bag in her hand... She went to the wagon. The wagon
    had been waiting on Hemlock at the curb." The door in the W wall north
    of the Hemlock window (the steel leaf open outward, the frame, the
    stoop, the flour-dust mat, the wall-pack over it, bread crates stacked
    beside it, the delivery rack), the gravel side lot with Finn's truck
    (the crow's dashboard), the sidewalk and Hemlock Street with the wagon
    at the curb, Cale's empty spot, the houses across the street. Draft 2
    targets: the bakery's W facade as boards with the window's outside
    casing; the front of house's corner and the sidewalk Lena and Kai stand
    on; the crow on the truck's dashboard; the wagon as the station wagon
    it is; Hans's house up the street."""
    steel_dk = (0.30, 0.31, 0.34, 1.0)
    dx, dy = -ROOM_W / 2.0, 5.60
    make_box("Bakery_Back_Door_Head", (dx, dy, 2.13), (0.24, 1.07, 0.06), steel_dk)
    for e, nm in ((-1, "S"), (1, "N")):
        make_box(f"Bakery_Back_Door_Jamb_{nm}", (dx, dy + e * 0.505, 1.05), (0.24, 0.06, 2.10), steel_dk)
    make_box("Bakery_Back_Door", (dx - 0.12 - 0.475, dy + 0.475 - 0.025, 1.05), (0.95, 0.045, 2.10), (0.52, 0.50, 0.46, 1.0))   # open outward, on its N hinge
    make_box("Bakery_Back_Door_Bar", (dx - 0.12 - 0.475, dy + 0.475 - 0.06, 1.02), (0.70, 0.03, 0.05), (0.60, 0.62, 0.64, 1.0))
    make_box("Bakery_Back_Stoop", (dx - 0.72, dy, -0.015), (1.20, 1.40, 0.03), (0.60, 0.59, 0.58, 1.0))
    make_box("Bakery_Back_Mat", (dx - 0.72, dy, 0.012), (0.80, 0.60, 0.024), (0.30, 0.28, 0.26, 1.0))
    make_box("Bakery_Back_Light", (dx - 0.18, dy, 2.45), (0.14, 0.26, 0.18), (1.0, 0.92, 0.70, 1.0))
    make_box("Bakery_Back_Light_Hood", (dx - 0.20, dy, 2.56), (0.20, 0.30, 0.03), steel_dk)
    for ci, (cy_, cz_) in enumerate(((7.4, 0.14), (7.4, 0.42), (7.9, 0.14))):   # clear of the leaf's 0.9 m
        make_box(f"Bread_Crate_{ci}", (dx - 0.42, cy_, cz_), (0.44, 0.44, 0.28), (0.30, 0.44, 0.62, 1.0) if ci != 1 else (0.62, 0.30, 0.26, 1.0))
    # the gravel side lot, Finn's truck (the crow on its dashboard), the paper bag on the hood
    make_box("Hemlock_Lot_Gravel", (-7.2, 5.0, -0.02), (5.2, 11.6, 0.03), (0.52, 0.50, 0.44, 1.0))
    make_car("Pickup_Toyota", -8.6, 7.0, 4.9, (0.56, 0.54, 0.48, 1.0), pickup=True, along="Y")
    make_box("Paper_Bag", (-4.92, 7.4, 0.67), (0.16, 0.12, 0.22), (0.72, 0.60, 0.42, 1.0))   # on the bread crates by the door
    # the sidewalk, the curb, Hemlock Street with the wagon at the curb, Cale's empty spot, the houses across
    make_box("Hemlock_Sidewalk", (-10.4, 4.0, -0.02), (1.4, 40.0, 0.04), (0.60, 0.59, 0.58, 1.0))
    make_box("Hemlock_Curb", (-11.2, 4.0, -0.03), (0.2, 40.0, 0.10), (0.58, 0.57, 0.55, 1.0))
    make_box("Hemlock_Street", (-16.15, 4.0, -0.06), (5.1, 40.0, 0.04), (0.26, 0.26, 0.28, 1.0))
    make_box("Hemlock_Street_Centerline", (-16.15, 4.0, -0.038), (0.10, 40.0, 0.004), (0.84, 0.78, 0.30, 1.0))
    make_box("Hemlock_Curb_Parking_Asphalt", (-12.45, 4.0, -0.055), (2.3, 40.0, 0.03), (0.28, 0.28, 0.30, 1.0))   # the parking strip along the curb
    make_car("Station_Wagon", -12.45, 8.5, 4.9, (0.34, 0.40, 0.36, 1.0), along="Y")
    make_box("Hemlock_Far_Ground", (-22.0, 4.0, -0.03), (8.0, 40.0, 0.03), (0.22, 0.30, 0.16, 1.0))
    for hi, hy in enumerate((-4.0, 6.0, 16.0)):
        make_box(f"Hemlock_House_{hi}", (-21.5, hy, 1.6), (7.0, 7.0, 3.2), ((0.56, 0.52, 0.48, 1.0), (0.64, 0.60, 0.52, 1.0), (0.50, 0.54, 0.50, 1.0))[hi])
        make_box(f"Hemlock_House_{hi}_Roof", (-21.5, hy, 3.45), (7.6, 7.6, 0.50), (0.32, 0.30, 0.30, 1.0))
    make_box("Hemlock_Lamp_Post", (-10.9, 10.5, 2.4), (0.14, 0.14, 4.8), steel_dk)
    make_box("Hemlock_Lamp_Head", (-11.15, 10.5, 4.85), (0.70, 0.30, 0.18), steel_dk)


def build_front_2026_11():
    """DRAFT 6 · THE FRONT OF THE ROOM. "At six twelve the bell rang at the
    front of the bakery ... She walked to the front of the room. Greta came
    out from behind the front counter ... went to the door. She opened it."
    The street door on the dining table's axis with its bell, the front
    window (the roster's picture: FOH_Street_Pane keeps its name, place and
    size), the counter across the east half with the case ("two loaves of
    the rye and the country and twelve Sunday rolls"), the bread shelves
    behind it, a waiting bench and a small table on the west half, and the
    street outside the door's glass."""
    wood, wood_dk = (0.46, 0.34, 0.22, 1.0), (0.36, 0.26, 0.16, 1.0)
    brass = (0.70, 0.56, 0.26, 1.0)
    steel = (0.72, 0.72, 0.74, 1.0)
    crust, crust_dk, pale = (0.74, 0.52, 0.30, 1.0), (0.44, 0.30, 0.18, 1.0), (0.84, 0.66, 0.40, 1.0)
    y0 = -FRONT_D
    fy = y0 + 0.10                                   # the street wall's room face
    # ── the door: jambs and head, the leaf closed, a glass light, the handle ──
    for e, ex in (("L", -0.53), ("R", 0.53)):
        make_box(f"Front_Door_Jamb_{e}", (ex, y0, 1.05), (0.06, 0.24, 2.10), wood_dk)
    make_box("Front_Door_Head", (0.0, y0, 2.13), (1.12, 0.24, 0.06), wood_dk)
    for e, ex in (("L", -0.43), ("R", 0.43)):
        make_box(f"Front_Door_Stile_{e}", (ex, y0, 1.05), (0.12, 0.045, 2.04), wood)
    make_box("Front_Door_Rail_Top", (0.0, y0, 2.00), (0.74, 0.045, 0.14), wood)
    make_box("Front_Door_Rail_Mid", (0.0, y0, 1.00), (0.74, 0.045, 0.12), wood)
    make_box("Front_Door_Rail_Bottom", (0.0, y0, 0.12), (0.74, 0.045, 0.18), wood)
    make_box("Front_Door_Panel", (0.0, y0, 0.575), (0.74, 0.024, 0.73), wood_dk)
    make_box("Front_Door_Glass", (0.0, y0, 1.495), (0.74, 0.010, 0.87), (0.62, 0.70, 0.76, 0.28))
    make_box("Front_Door_Push", (0.30, y0 + 0.035, 1.08), (0.04, 0.025, 0.30), brass)
    make_box("Front_Door_Mat", (0.0, fy + 0.50, 0.012), (0.90, 0.60, 0.024), (0.28, 0.24, 0.20, 1.0))
    # ── THE BELL on its spring over the door ──
    make_box("Front_Bell_Plate", (0.30, fy + 0.006, 2.34), (0.06, 0.012, 0.10), wood_dk)
    make_tube("Front_Bell_Spring", [(0.30, fy + 0.012, 2.34), (0.30, fy + 0.10, 2.40), (0.30, fy + 0.20, 2.345)], 0.006, brass, segments=5)
    make_lathe("Front_Bell", (0.30, fy + 0.20, 2.25), [(0.046, 0.0), (0.044, 0.012), (0.034, 0.05), (0.018, 0.075), (0.007, 0.088), (0.0, 0.092)], brass, segments=10)
    make_cyl("Front_Bell_Clapper", (0.30, fy + 0.20, 2.245), 0.008, 0.03, wood_dk, segments=6)
    # ── the front window: the picture's pane, its mullion, casing and ledge ──
    make_box("FOH_Street_Pane", (2.0, -4.28, 1.55), (2.4, 0.02, 1.6), (0.30, 0.36, 0.46, 1.0))
    make_box("FOH_Street_Mullion", (2.0, -4.26, 1.55), (0.04, 0.02, 1.6), (0.30, 0.24, 0.18, 1.0))
    make_box("Front_Window_Casing_T", (2.0, -4.285, 2.39), (2.56, 0.03, 0.08), wood_dk)
    make_box("Front_Window_Casing_B", (2.0, -4.285, 0.71), (2.56, 0.03, 0.08), wood_dk)
    for e, ex in (("L", 0.76), ("R", 3.24)):
        make_box(f"Front_Window_Casing_{e}", (ex, -4.285, 1.55), (0.08, 0.03, 1.60), wood_dk)
    # ── the street, through the door's glass (pre-dawn: all of it dark) ──
    make_box("Front_Sidewalk", (3.2, y0 - 1.35, -0.02), (25.6, 2.5, 0.04), (0.50, 0.49, 0.48, 1.0))
    make_box("Front_Curb", (3.2, y0 - 2.70, -0.03), (25.6, 0.2, 0.10), (0.48, 0.47, 0.45, 1.0))
    make_box("Front_Street", (3.2, y0 - 6.0, -0.06), (25.6, 6.4, 0.04), (0.20, 0.20, 0.22, 1.0))
    make_box("Front_Far_Walk", (3.2, y0 - 10.3, -0.02), (25.6, 2.2, 0.04), (0.44, 0.43, 0.42, 1.0))
    for hi, (hx, hw, hh, col) in enumerate(((-5.5, 7.0, 6.4, (0.34, 0.30, 0.28, 1.0)), (1.6, 6.6, 7.0, (0.40, 0.34, 0.30, 1.0)),
                                            (8.4, 6.4, 6.2, (0.30, 0.32, 0.34, 1.0)), (14.4, 5.2, 6.8, (0.36, 0.32, 0.26, 1.0)))):
        make_box(f"Front_Far_Shop_{hi}", (hx, y0 - 14.6, hh / 2.0), (hw, 6.0, hh), col)
        make_box(f"Front_Far_Shop_{hi}_Awning", (hx, y0 - 11.3, 2.7), (hw - 0.8, 0.9, 0.08), (0.22, 0.26, 0.24, 1.0))
    # ── THE FRONT COUNTER (customers south of it, Greta north) ──
    top = make_counter("Front_Counter", (2.60, -2.0, 0.0), length=0.65, depth=3.40, height=0.95,
                       palette={"formica": wood, "top": (0.30, 0.21, 0.13, 1.0), "kick": wood_dk})
    make_counter_bullnose("Front_Counter", (2.60, -2.0 - 0.325, top), length=3.40, axis='X')
    # the case on its west run: glass on three sides and the top, open to Greta
    cx = 1.85
    make_box("Front_Case_Base", (cx, -2.0, top + 0.015), (1.70, 0.56, 0.03), wood_dk)
    make_box("Front_Case_Glass_Front", (cx, -2.274, top + 0.28), (1.70, 0.012, 0.50), (0.80, 0.86, 0.90, 0.25))
    make_box("Front_Case_Glass_Top", (cx, -2.0, top + 0.536), (1.70, 0.56, 0.012), (0.80, 0.86, 0.90, 0.25))
    for e, ex in (("W", cx - 0.844), ("E", cx + 0.844)):
        make_box(f"Front_Case_Glass_{e}", (ex, -2.0, top + 0.28), (0.012, 0.536, 0.50), (0.80, 0.86, 0.90, 0.25))
    make_box("Front_Case_Shelf", (cx, -1.97, top + 0.28), (1.64, 0.40, 0.012), steel)
    for k, sx in enumerate((cx - 0.79, cx + 0.79)):
        make_box(f"Front_Case_Shelf_Bracket_{k}", (sx, -1.97, top + 0.152), (0.02, 0.36, 0.244), steel)
    # "two loaves of the rye and the country and twelve Sunday rolls"
    for li, lx in enumerate((cx - 0.55, cx - 0.20)):
        make_cyl(f"Front_Loaf_Rye_{li}", (lx, -2.0, top + 0.085), 0.055, 0.28, crust_dk, axis='Y', segments=8)
    make_lathe("Front_Loaf_Country", (cx + 0.38, -2.0, top + 0.03), [(0.11, 0.0), (0.13, 0.03), (0.11, 0.08), (0.05, 0.11), (0.0, 0.115)], crust, segments=10)
    for ri in range(12):
        make_cyl(f"Front_Roll_{ri}", (cx - 0.62 + (ri % 6) * 0.24, -1.88 - (ri // 6) * 0.15, top + 0.311), 0.045, 0.05, pale, segments=8)
    make_register("Front_Register", (3.75, -1.95, top))
    make_box("Front_Paper_Stack", (3.15, -1.92, top + 0.04), (0.22, 0.30, 0.08), (0.72, 0.60, 0.42, 1.0))
    # the bread shelves on the east wall behind the counter
    for k, sz in enumerate((1.25, 1.65, 2.05)):
        make_box(f"Front_Bread_Shelf_{k}", (ROOM_W/2.0 - 0.22, -0.95, sz), (0.24, 1.50, 0.03), wood)
        for b2, by2 in enumerate((-1.60, -0.30)):
            make_box(f"Front_Bread_Shelf_{k}_Bracket_{b2}", (ROOM_W/2.0 - 0.13, by2, sz - 0.075), (0.06, 0.03, 0.12), wood_dk)
        for li in range(4):
            make_cyl(f"Front_Shelf_Loaf_{k}_{li}", (ROOM_W/2.0 - 0.22, -1.50 + li * 0.36, sz + 0.07), 0.055, 0.20, crust if (k + li) % 2 else crust_dk, axis='X', segments=8)
    # two pendants over the counter; two more beams
    for k, px in enumerate((1.80, 3.40)):
        make_pendant(f"Front_Pendant_{k}", px, -2.0, 2.10, CEIL, shade_col=(0.30, 0.36, 0.30, 1.0), shade_r=0.18)
    for k, by2 in enumerate((-1.25, -3.05)):
        make_box(f"Ceil_Beam_F{k}", (0.0, by2, CEIL - 0.12), (ROOM_W - 0.2, 0.18, 0.24), (0.36, 0.26, 0.17, 1.0))
    # ── the west half: a waiting bench under coat pegs, a small table, the plant ──
    wx = -ROOM_W/2.0 + 0.10                          # the W wall's room face
    make_box("Front_Bench_Seat", (wx + 0.22, -2.5, 0.44), (0.42, 1.80, 0.05), wood)
    for k, ly in enumerate((-3.30, -2.5, -1.70)):
        make_box(f"Front_Bench_Leg_{k}", (wx + 0.22, ly, 0.2075), (0.36, 0.05, 0.415), wood_dk)
    make_box("Front_Bench_Back", (wx + 0.015, -2.5, 0.80), (0.03, 1.80, 0.30), wood)
    make_box("Front_Peg_Board", (wx + 0.012, -2.5, 1.66), (0.024, 1.40, 0.08), wood_dk)
    for k in range(4):
        make_cyl(f"Front_Peg_{k}", (wx + 0.064, -3.05 + k * 0.37, 1.66), 0.014, 0.08, wood_dk, axis='X', segments=6)
    make_box("Front_Table_Top", (-2.2, -2.9, 0.735), (0.72, 0.72, 0.03), wood)
    make_cyl("Front_Table_Post", (-2.2, -2.9, 0.37), 0.04, 0.70, P.METAL_BLACK, segments=8)
    make_cyl("Front_Table_Foot", (-2.2, -2.9, 0.01), 0.22, 0.02, P.METAL_BLACK, segments=10)
    import math as _m
    make_chair("Front_Chair_0", -2.2, -3.52, yaw=0.0, wood=wood, w=0.40)
    make_chair("Front_Chair_1", -2.2, -2.28, yaw=_m.pi, wood=wood, w=0.40)
    make_floor_plant("Plant", (-3.9, -3.85, 0.0))
    make_light_switch("Switch_1", (-0.78, y0), axis='X', face_sign=1, z=1.25, aged=True)


def build_main_room_2026_11():
    """DRAFT 6 · THE MAIN ROOM. The kitchenette on the N counter ("Greta
    was at the kettle"; "the kitchenette sink"), Hans's wedding photograph
    on the wall behind it, the COOLING RACK TABLE on the east wall (the
    third of the three long tables; the worktable is the baker's bench of
    draft 5), the aprons on the W wall."""
    wood, wood_dk = (0.46, 0.34, 0.22, 1.0), (0.36, 0.26, 0.16, 1.0)
    steel, steel_dk = (0.72, 0.72, 0.74, 1.0), (0.34, 0.35, 0.37, 1.0)
    crust, crust_dk = (0.74, 0.52, 0.30, 1.0), (0.50, 0.34, 0.20, 1.0)
    top = 0.96                                       # the N counter's top (the mixer stood on it)
    ccx, ccy = COUNTER_CX + SH_NW[0], ROOM_D - 1.0
    # ── the sink, the cups beside it ──
    sx = ccx + 0.55
    make_box("Kitchenette_Sink_Rim", (sx, ccy, top + 0.006), (0.50, 0.40, 0.012), steel)
    make_box("Kitchenette_Sink_Bowl", (sx, ccy, top + 0.0135), (0.42, 0.32, 0.003), steel_dk)
    make_cyl("Kitchenette_Faucet", (sx, ccy + 0.25, top + 0.11), 0.014, 0.22, steel, segments=6)
    make_box("Kitchenette_Spout", (sx, ccy + 0.165, top + 0.21), (0.024, 0.18, 0.02), steel)
    for k in range(3):
        make_cyl(f"Kitchenette_Cup_{k}", (sx - 0.42 - k * 0.11, ccy - 0.12 + (k % 2) * 0.10, top + 0.045), 0.038, 0.09, (0.90, 0.88, 0.82, 1.0), segments=8)
    # ── THE WEDDING PHOTOGRAPH: on plaster, east of the tile, at eye height ──
    py = ROOM_D - 0.10                               # the N wall's room face
    make_box("Wedding_Photo_Frame", (-0.9, py - 0.012, 1.62), (0.40, 0.024, 0.50), wood_dk)
    make_box("Wedding_Photo_Print", (-0.9, py - 0.027, 1.62), (0.32, 0.006, 0.42), (0.80, 0.76, 0.66, 1.0))
    # a sideboard under it: the cups' home, the coffee things
    make_chamfer_box("Sideboard", (-0.9, py - 0.23, 0.43), (1.40, 0.44, 0.86), wood, chamfer=0.02)
    make_box("Sideboard_Top", (-0.9, py - 0.23, 0.875), (1.46, 0.48, 0.03), wood_dk)
    for k, dx in enumerate((-0.35, 0.35)):
        make_box(f"Sideboard_Door_{k}", (-0.9 + dx, py - 0.456, 0.40), (0.62, 0.012, 0.62), wood_dk)
        make_cyl(f"Sideboard_Knob_{k}", (-0.9 + dx * 0.14, py - 0.470, 0.42), 0.012, 0.016, (0.70, 0.56, 0.26, 1.0), axis='Y', segments=6)
    for k in range(4):
        make_cyl(f"Sideboard_Cup_{k}", (-0.70 + k * 0.12, py - 0.20, 0.935), 0.038, 0.09, (0.90, 0.88, 0.82, 1.0), segments=8)
    # ── THE KETTLE on its hob, on the sideboard: "Greta was at the kettle ...
    # Hans's wedding-photo on the wall behind her" ──
    kx, ky, kt = -1.28, py - 0.23, 0.89
    make_box("Kettle_Hob", (kx, ky, kt + 0.015), (0.30, 0.30, 0.03), (0.16, 0.16, 0.18, 1.0))
    make_lathe("Kettle", (kx, ky, kt + 0.03), [(0.085, 0.0), (0.10, 0.03), (0.095, 0.10), (0.06, 0.15), (0.02, 0.165), (0.0, 0.17)], steel, segments=12)
    make_box("Kettle_Spout", (kx + 0.115, ky, kt + 0.13), (0.07, 0.03, 0.03), steel)
    make_tube("Kettle_Handle", [(kx - 0.05, ky, kt + 0.185), (kx, ky, kt + 0.245), (kx + 0.05, ky, kt + 0.185)], 0.008, (0.16, 0.14, 0.12, 1.0), segments=5)
    # ── THE COOLING RACK TABLE, east wall ──
    tx, ty, tw, tl = ROOM_W/2.0 - 0.56, 2.0, 0.84, 2.80
    make_chamfer_box("Cooling_Table_Top", (tx, ty, 0.875), (tw, tl, 0.05), wood, chamfer=0.012)
    for k, (ox, oy) in enumerate(((-0.36, -1.32), (0.36, -1.32), (-0.36, 1.32), (0.36, 1.32))):
        make_box(f"Cooling_Table_Leg_{k}", (tx + ox, ty + oy, 0.425), (0.07, 0.07, 0.85), wood_dk)
    # the shelf sits BETWEEN the legs' inner faces (a slab the legs pass through is a POKE)
    make_box("Cooling_Table_Shelf", (tx, ty, 0.24), (0.65, 2.57, 0.03), wood_dk)
    for k in range(3):
        make_box(f"Cooling_Table_Tray_{k}", (tx, ty - 0.8 + k * 0.02, 0.262 + k * 0.016), (0.46, 0.66, 0.014), steel)
    for r, ry in enumerate((ty - 0.90, ty, ty + 0.90)):
        # a wire rack on four feet: the frame, its bars
        for e, ex in (("W", -0.30), ("E", 0.30)):
            make_box(f"Cooling_Rack_{r}_Side_{e}", (tx + ex, ry, 0.955), (0.012, 0.76, 0.012), steel)
        for e, ey in (("S", -0.38), ("N", 0.38)):
            make_box(f"Cooling_Rack_{r}_End_{e}", (tx, ry + ey, 0.955), (0.612, 0.012, 0.012), steel)
        for f, (fx2, fy2) in enumerate(((-0.30, -0.38), (0.30, -0.38), (-0.30, 0.38), (0.30, 0.38))):
            make_box(f"Cooling_Rack_{r}_Foot_{f}", (tx + fx2, ry + fy2, 0.9245), (0.012, 0.012, 0.049), steel)
        for b2 in range(7):
            make_box(f"Cooling_Rack_{r}_Bar_{b2}", (tx, ry - 0.30 + b2 * 0.10, 0.955), (0.588, 0.006, 0.006), steel)
        if r == 1:
            for li in range(3):
                make_lathe(f"Cooling_Boule_{li}", (tx - 0.02, ry - 0.24 + li * 0.24, 0.961), [(0.085, 0.0), (0.105, 0.03), (0.09, 0.07), (0.04, 0.095), (0.0, 0.10)], crust, segments=10)
        else:
            for li in range(4):
                make_cyl(f"Cooling_Loaf_{r}_{li}", (tx, ry - 0.27 + li * 0.18, 1.016), 0.055, 0.44, crust if li % 2 else crust_dk, axis='X', segments=8)
    # ── THE BOX ON THE TABLE (ch17_bakery 94-95, ch17_roy 14 / 111 / 121): "She
    # set the box on the long table at the end nearest the back door"; Roy's
    # is "the size of Per's box" and sits "on the table in front of him".
    # [shot:insert box] aimed at Per's box on the door bench until draft 6. ──
    make_box("Table_Box_Body", (0.22, 4.90, 0.8375), (0.305, 0.155, 0.115), (0.52, 0.40, 0.28, 1.0))
    make_box("Table_Box_Lid", (0.22, 4.90, 0.906), (0.315, 0.165, 0.022), (0.40, 0.30, 0.20, 1.0))
    make_box("Table_Box_Clasp", (0.22, 4.819, 0.875), (0.035, 0.008, 0.030), (0.62, 0.52, 0.30, 1.0))
    # ── the aprons, on the W wall by the front ──
    wx = -ROOM_W/2.0 + 0.10
    make_box("Apron_Hook_Board", (wx + 0.022, 0.95, 1.66), (0.02, 0.80, 0.08), wood_dk)
    for k, (oy, col) in enumerate(((0.65, (0.92, 0.90, 0.84, 1.0)), (0.95, (0.40, 0.46, 0.56, 1.0)), (1.25, (0.92, 0.90, 0.84, 1.0)))):
        make_box(f"Apron_Hook_{k}", (wx + 0.052, oy, 1.64), (0.04, 0.02, 0.02), (0.30, 0.30, 0.32, 1.0))
        make_box(f"Apron_{k}", (wx + 0.057, oy, 1.25), (0.03, 0.22, 0.78), col)
        make_box(f"Apron_{k}_Strap", (wx + 0.057, oy, 1.645), (0.032, 0.06, 0.02), col)


def build_back_kitchen_2026_11():
    """DRAFT 6 · THE BACK KITCHEN (ch10_cabin 6-24). "Per was at the back
    kitchen ... He had been kneading. He was at the floured board with his
    hands at rest on the dough. Hans was at the stove. He had two trays out
    of the oven and was, when Kai came in, lifting a third." The stove on
    the N wall, the island with the floured board and the two trays, the
    counter on the W wall (the mixer stands on it). The deck oven, the
    proofer, the speed rack, the flour and the bench by the door are the
    old builders, moved (see main)."""
    wood, wood_dk = (0.62, 0.50, 0.34, 1.0), (0.44, 0.34, 0.22, 1.0)
    steel, steel_dk = (0.74, 0.75, 0.77, 1.0), (0.30, 0.31, 0.34, 1.0)
    black = (0.16, 0.16, 0.18, 1.0)
    dough, flour, roll = (0.92, 0.88, 0.76, 1.0), (0.94, 0.92, 0.86, 1.0), (0.84, 0.66, 0.40, 1.0)
    nf = BK_Y1 - 0.10                                # the N wall's room face
    # ── THE STOVE ──
    sx, sy = 0.75, nf - 0.40
    make_chamfer_box("Stove_Body", (sx, sy, 0.45), (1.00, 0.76, 0.90), black, chamfer=0.015)
    make_box("Stove_Top", (sx, sy, 0.915), (1.02, 0.78, 0.03), steel_dk)
    for k, (ox, oy) in enumerate(((-0.25, -0.18), (0.25, -0.18), (-0.25, 0.18), (0.25, 0.18))):
        make_cyl(f"Stove_Burner_{k}", (sx + ox, sy + oy, 0.936), 0.10, 0.012, black, segments=10)
    make_box("Stove_Backguard", (sx, sy + 0.37, 1.08), (1.00, 0.04, 0.30), steel)
    make_box("Stove_Oven_Door", (sx, sy - 0.386, 0.42), (0.80, 0.012, 0.50), steel_dk)
    make_cyl("Stove_Oven_Handle", (sx, sy - 0.42, 0.70), 0.014, 0.66, steel, axis='X', segments=6)
    for k, hx in enumerate((sx - 0.30, sx + 0.30)):
        make_cyl(f"Stove_Oven_Handle_Post_{k}", (hx, sy - 0.404, 0.70), 0.010, 0.024, steel, axis='Y', segments=6)
    for k in range(4):
        make_cyl(f"Stove_Knob_{k}", (sx - 0.33 + k * 0.22, sy - 0.39, 0.83), 0.022, 0.02, steel, axis='Y', segments=8)
    make_cyl("Stove_Pot", (sx - 0.25, sy + 0.18, 1.022), 0.11, 0.16, steel, segments=12)
    make_cyl("Stove_Pot_Lid", (sx - 0.25, sy + 0.18, 1.108), 0.115, 0.012, steel_dk, segments=12)
    make_chamfer_box("Stove_Hood", (sx, sy + 0.04, 1.98), (1.10, 0.70, 0.26), steel, chamfer=0.02)
    make_box("Stove_Hood_Duct", (sx, sy + 0.22, 2.555), (0.30, 0.30, 0.89), steel)
    # ── THE ISLAND: the floured board (Per), the two trays (Hans) ──
    ix, iy = 1.55, 10.0
    make_chamfer_box("Island_Top", (ix, iy, 0.875), (1.70, 0.85, 0.05), wood, chamfer=0.012)
    for k, (ox, oy) in enumerate(((-0.78, -0.36), (0.78, -0.36), (-0.78, 0.36), (0.78, 0.36))):
        make_box(f"Island_Leg_{k}", (ix + ox, iy + oy, 0.425), (0.07, 0.07, 0.85), wood_dk)
    make_box("Island_Shelf", (ix, iy, 0.22), (1.49, 0.65, 0.03), wood_dk)
    make_box("Island_Shelf_Bin", (ix - 0.35, iy, 0.345), (0.50, 0.40, 0.22), (0.86, 0.86, 0.84, 1.0))
    make_box("Kneading_Board", (ix - 0.45, iy, 0.910), (0.60, 0.50, 0.02), (0.78, 0.66, 0.46, 1.0))
    make_box("Kneading_Board_Flour", (ix - 0.45, iy, 0.921), (0.52, 0.42, 0.002), flour)
    make_blob("Kneading_Dough", (ix - 0.45, iy, 0.975), 0.13, dough, noise=0.10, seed=7, squash=0.45)
    for t, tx2 in enumerate((ix + 0.19, ix + 0.62)):
        make_box(f"Island_Tray_{t}", (tx2, iy, 0.908), (0.40, 0.60, 0.016), steel)
        for ri in range(12):
            make_cyl(f"Island_Tray_{t}_Roll_{ri}", (tx2 - 0.12 + (ri % 3) * 0.12, iy - 0.21 + (ri // 3) * 0.14, 0.941), 0.045, 0.05, roll, segments=8)
    # ── the counter on the W wall (the mixer's; its top is the N counter's 0.96) ──
    top = make_counter("BK_Counter", (BK_X0 + 0.10 + 0.325, 10.2, 0.0), length=2.00, depth=0.65, height=0.92,
                       palette={"formica": steel, "top": steel_dk, "kick": steel_dk})
    make_box("BK_Counter_Bowl_Stack", (BK_X0 + 0.42, 9.55, top + 0.06), (0.30, 0.30, 0.12), steel)
    # Per's coffee, on the bench by the door
    make_cyl("Bench_Coffee_Mug", (0.62, 8.02, 0.51), 0.04, 0.09, (0.90, 0.88, 0.82, 1.0), segments=8)
    # the path the trays take: the oven's doors to the island
    make_traffic_wear("Wear_Path_BK", [(BK_DOOR_X, ROOM_D + 0.4), (2.6, 9.3), (2.2, 11.6)], width=0.5, tint=(0.44, 0.42, 0.39, 1.0))


def build_draft5_fill_2026_10():
    """DRAFT 5 · THE FILL (2026-10-09). Built on the new 9 x 7.6 plan (no
    shift). The bigger room read as an empty hall: the baker's bench in
    the E aisle (the morning's dough, bannetons, the scraper), a timber
    wainscot on the W and S walls, aprons and a hand sink by the door,
    and a plaster ceiling on beams with two warm pendants over the
    table in place of the drop-tile grid (it read as an office)."""
    maple, maple_dk = (0.74, 0.60, 0.42, 1.0), (0.52, 0.40, 0.26, 1.0)
    dough = (0.92, 0.88, 0.76, 1.0)
    flour = (0.94, 0.92, 0.86, 1.0)
    cane = (0.70, 0.56, 0.36, 1.0)
    # ── the baker's bench, E aisle ──
    bx, by, bw, bd = 2.55, 4.55, 0.90, 2.20
    make_box("Bench_Top", (bx, by, 0.90), (bw, bd, 0.08), maple)
    for li, (ox, oy) in enumerate(((-0.40, -1.05), (0.40, -1.05), (-0.40, 1.05), (0.40, 1.05))):
        make_box(f"Bench_Leg_{li}", (bx + ox, by + oy, 0.43), (0.08, 0.08, 0.86), maple_dk)
    make_box("Bench_Shelf", (bx, by, 0.22), (bw - 0.16, bd - 0.16, 0.03), maple_dk)
    for ti, ty in enumerate((by - 0.6, by + 0.1)):
        make_box(f"Bench_Tub_{ti}", (bx, ty, 0.355), (0.55, 0.45, 0.24), (0.86, 0.86, 0.84, 1.0))
        make_box(f"Bench_Tub_{ti}_Lid", (bx, ty, 0.48), (0.57, 0.47, 0.02), (0.30, 0.46, 0.62, 1.0))
    make_box("Bench_Flour_Dust", (bx - 0.05, by - 0.35, 0.941), (0.70, 1.10, 0.002), flour)
    make_blob("Bench_Dough_Mass", (bx - 0.05, by - 0.55, 0.99), 0.17, dough, noise=0.12, seed=5, squash=0.45)
    for di in range(6):
        make_cyl(f"Bench_Dough_Round_{di}", (bx - 0.25 + (di % 2) * 0.30, by - 0.05 + (di // 2) * 0.24, 0.975), 0.075, 0.07, dough, segments=12)
    make_box("Bench_Scraper", (bx + 0.25, by - 0.75, 0.948), (0.12, 0.10, 0.012), (0.70, 0.72, 0.74, 1.0))
    make_box("Bench_Scraper_Grip", (bx + 0.25, by - 0.69, 0.962), (0.12, 0.02, 0.025), (0.20, 0.20, 0.22, 1.0))
    # bannetons: cane proofing baskets, a stack and a row with dough in them
    for k in range(4):
        make_lathe(f"Banneton_Stack_{k}", (bx + 0.20, by + 0.80, 0.94 + k * 0.075),
                   [(0.08, 0.0), (0.10, 0.02), (0.12, 0.075), (0.11, 0.075), (0.09, 0.02), (0.0, 0.01)], cane, segments=12)
    for k in range(3):
        make_lathe(f"Banneton_{k}", (bx - 0.22, by + 0.45 + k * 0.26, 0.94),
                   [(0.07, 0.0), (0.09, 0.02), (0.11, 0.08), (0.10, 0.08), (0.08, 0.02), (0.0, 0.01)], cane, segments=12)
        make_cyl(f"Banneton_{k}_Dough", (bx - 0.22, by + 0.45 + k * 0.26, 1.01), 0.085, 0.03, dough, segments=12)
    make_box("Bench_Flour_Bag", (bx + 0.22, by + 0.30, 1.06), (0.26, 0.16, 0.24), (0.86, 0.80, 0.66, 1.0))
    # ── timber wainscot: W wall (under the window's sill line) and the S wall W of the door ──
    wain, cap = (0.50, 0.36, 0.22, 1.0), (0.40, 0.28, 0.17, 1.0)
    XW = -ROOM_W / 2.0 + 0.10
    # (draft 6: from the header's pier, not from the old S wall)
    make_box("Wainscot_W", (XW + 0.01, ROOM_D / 2.0 + 0.03, 0.45), (0.02, ROOM_D - 0.26, 0.90), wain)
    make_box("Wainscot_W_Cap", (XW + 0.02, ROOM_D / 2.0 + 0.03, 0.915), (0.04, ROOM_D - 0.26, 0.03), cap)
    for k in range(int((ROOM_D - 0.2) / 0.30)):
        make_box(f"Wainscot_W_Batten_{k}", (XW + 0.025, 0.25 + k * 0.30, 0.45), (0.01, 0.025, 0.86), cap)
    # (draft 6: the S wall's wainscot, the hand sink and the towel
    # dispenser went with the wall; the aprons hang on the W wall now —
    # build_main_room_2026_11)
    # ── the ceiling: plaster on four beams, two warm pendants over the table ──
    for k, y in enumerate((1.4, 3.2, 5.0, 6.8)):
        make_box(f"Ceil_Beam_{k}", (0.0, y, CEIL - 0.12), (ROOM_W - 0.2, 0.18, 0.24), (0.36, 0.26, 0.17, 1.0))
    for k, y in enumerate((2.6, 4.4)):
        make_pendant(f"Table_Pendant_{k}", 0.0, y, 2.05, CEIL, shade_col=(0.30, 0.36, 0.30, 1.0), shade_r=0.20)


# ── DRAFT 5 · THE BIGGER ROOM (2026-10-09, lore/_SET_DETAIL_PLAYBOOK.md) ──
# Each area was authored against the 6 x 5 walls; it is built inside
# shifted(), handed the old ROOM_W/ROOM_D, and moved rigidly onto the
# 9 x 7.6 plan. The S wall (the door, the pass, the bench) does not move.
_OLD = dict(ROOM_W=6.0, ROOM_D=5.0)
_EXTRA = ("make_counter", "make_counter_bullnose", "make_case_shell", "make_wall_clock", "make_wall_outlet",
          "make_light_switch", "make_floor_stain", "make_scuff_band")
SH_NW = (-1.2, 2.6)     # counter, mixer, utensil rail, drawers, kick, outlet N1
SH_NE = (1.5, 2.6)      # oven + hood, proofer, their wear, outlet N2
SH_TABLE = (0.0, 1.2)   # the communal table, its hero props, its wear
SH_W = (-1.5, 1.2)      # the Hemlock window corner, bowl shelf, flour bin, calendar, the hemlock
SH_SW = (-1.4, 0.3)     # prep table, scale, flour sacks
SH_E = (1.5, 1.2)       # speed rack, cooling rack, poster, outlet E1
SH_CLOCK = (0.0, 2.6)
# draft 6 · where the old areas land in the back kitchen (old 6 x 5 coordinates + these)
SH_BK_OVEN = (1.5, 7.4)      # the deck oven (old 1.5, 4.5) to the N wall at 3.0, 11.9; the proofer to 3.95, 11.0
SH_BK_MIXER = (1.925, 6.6)   # the mixer (old -2.4, 4.0) onto BK_Counter at -0.475, 10.6
SH_BK_RACK = (1.55, 6.2)     # the speed rack (old 2.5, 2.7) to the E wall at 4.05, 8.9
SH_BK_SACKS = (2.05, 11.25)  # the flour sacks (old ~-2.4, 0.7) to the NW corner
SH_BK_BIN = (2.0, 4.8)       # the flour bin (old -2.45, 3.25) to the S wall, W of the bench
SH_BK_BENCH = (-0.25, 7.6)   # the bench by the door, the pegs, Per's box, the canvas bag (were by the old S door)


def _in(sh):
    return shifted(globals(), sh[0], sh[1], extra=_EXTRA, extra_paths=("make_traffic_wear",), **_OLD)


def main():
    clear_scene()
    build_shell()
    build_tile()
    with _in(SH_NW):
        build_counter(); build_utensil_rail(); build_counter_drawers(); build_wear_counter(); build_d3_nw()
    with _in(SH_TABLE):
        build_communal_table(); build_hero_props_2026_09(); build_wear_table()
    with _in(SH_W):
        build_window_corner(); build_bowl_shelf(); build_calendar(); build_hemlock()
    with _in(SH_E):
        build_poster(); build_d3_e()
    with _in(SH_CLOCK):
        build_clock()
    # ── draft 6: the bake line, in the back kitchen ──
    with _in(SH_BK_OVEN):
        build_stove(); build_proofer(); build_wear_oven(); build_d3_ne()
    with _in(SH_BK_MIXER):
        build_mixer()
    with _in(SH_BK_RACK):
        build_speed_rack()
    with _in(SH_BK_SACKS):
        build_flour_sacks()
    with _in(SH_BK_BIN):
        build_flour_bin()
    with shifted(globals(), SH_BK_BENCH[0], SH_BK_BENCH[1], extra=_EXTRA):
        build_pers_box_2026_08(); build_door_props()
    build_front_2026_11()
    build_main_room_2026_11()
    build_back_kitchen_2026_11()
    build_back_door_2026_10()
    build_draft4_2026_09()
    build_ceiling_infra()
    build_draft5_fill_2026_10()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/hans_bakery_back_kitchen.glb"))
    print(f"\n[build_hans_bakery_back_kitchen] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
