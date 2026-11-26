"""small_wood_road — the county road past the property, Small Wood,
Oregon (vol1 + vol2). New 2026-09-03 (user: "the stretches of highway
across all the volumes look identical, same geometry, same camera").

vol1 ch3: "EXT. DRIVING AROUND — NIGHT. Good music is playing." vol2
ch1: "I began running along the road — up and down the property ...
Knotted paths leading both up and down the road, twisting alongside
cricks, emerging upon tool shed areas, out-of-the-way pole barns, and
the remains of fallen-in houses. Debris of lives lost in transition."
vol2 ch2: "Gloria was found by the side of the road — beaten and
dishevelled. Her rescuer was a travelling minister."

A narrow two-lane county road with gravel shoulders, the property
fence and gate on the west, the pole barn up the drive, the tool shed,
the chicken coop out back of a small house, the crick crossing under
a culvert with a concrete headwall, a fallen-in house in the field to
the east, Douglas firs standing over everything, a SMALL WOOD 3 sign,
mailboxes at the gate. Nothing here is Louisiana or Texas.

Presets (Background3D), each a different place, height and lens:
  small_wood_road        day · on the west shoulder at the gate, eye
                          1.7, NNE up the road past the pole barn · 60°
  small_wood_road_night  night · the car's hood, eye 1.0 on the
                          centerline, the dashes running into the
                          firs · 70°
  small_wood_roadside    dawn · in the east ditch, eye 0.7, looking
                          along the gravel where the minister stopped · 50°

DRAFT 4 (2026-10-31): the coast range all round as hills (the far bands
were slabs, E and W only), the night's car, spill and town lights tagged to
the night, each light to its views, a sky per preset and the far plane out
to 1100 m. DRAFT 5 targets: vol2 ch1's "Knotted paths leading both up and
down the road, twisting alongside cricks" (a footpath off the shoulder into
the firs); the gate's chain and padlock; the roadside preset's minister's
car; the near firs' lowest tiers (the day frame's top-right canopy).
DRAFT 5 (2026-11-01): the paths (along the crick, up to the shed), the
gate's chain and padlock, and the roadside view at night as its chapter
plays it. The minister's car is dropped: vol2 ch2's episode is 1910
("reported killed in 1910") and the text gives Cook no vehicle. DRAFT 6
targets: the crick's banks and alders where the path runs (draft 6, done
the same day); the fallen-in house to the east read from the roadside at
night (it stands behind that lens: it needs its own frame).

Coordinate frame: Blender Z-up. Road N-S along y at x 0, ±1200 so
the lines converge. The property gate at y 0 west; the crick at
y 30; the fallen-in house east at y -30. glTF export remaps to Godot
(x, z, -y).
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_blob, make_wedge, make_gable, make_tube, make_rot_box, export_glb
from _props.trees import make_conifer, make_broadleaf
from _props.vehicles import make_car
from _props.buildings import make_ranch_house, make_shed
from _props.detail import make_wire_fence, make_road_bend, make_ditch_field
from _props.trees import make_bare_tree, make_shrub

ASPHALT = (0.22, 0.22, 0.23, 1.0)
GRAVEL = (0.58, 0.54, 0.46, 1.0)
GRASS = (0.36, 0.44, 0.24, 1.0)
FIELD = (0.52, 0.50, 0.30, 1.0)
DIRT = (0.42, 0.34, 0.24, 1.0)
FIR = (0.16, 0.28, 0.18, 1.0)
FIR_LT = (0.22, 0.34, 0.22, 1.0)
TRUNK = (0.32, 0.24, 0.18, 1.0)
WOOD_GRAY = (0.50, 0.46, 0.40, 1.0)
WOOD_RED = (0.46, 0.24, 0.18, 1.0)
TIN = (0.56, 0.58, 0.58, 1.0)
CONCRETE = (0.60, 0.60, 0.58, 1.0)
WATER = (0.28, 0.36, 0.34, 0.8)
ROAD_FAR, ROAD_NEAR = 1200.0, -1200.0


def build_road():
    BEND_Y = 150.0
    span = (BEND_Y - ROAD_NEAR)
    mid = (BEND_Y + ROAD_NEAR) / 2.0
    # the far ground, cut round the ditches and the east ditch field
    # (2026-09-24: one 2.6 km sheet at -0.06 lay over the ditches, which
    # bottom at -0.36/-0.42 — hidden)
    gcol = (0.34, 0.40, 0.24, 1.0)
    def _g(nm, x0, x1, y0, y1):
        make_box(nm, ((x0 + x1) / 2.0, (y0 + y1) / 2.0, -0.06), (x1 - x0, y1 - y0, 0.02), gcol)
    FAR = 1300.0
    _g("Ground_Far", -FAR, -4.5, -FAR, FAR)
    _g("Ground_Far_Mid", -2.9, 2.9, -FAR, FAR)
    _g("Ground_Far_E", 8.9, FAR, -FAR, FAR)
    _g("Ground_Far_DW_S", -4.5, -2.9, -FAR, ROAD_NEAR)
    _g("Ground_Far_DW_N", -4.5, -2.9, BEND_Y, FAR)
    _g("Ground_Far_E1_S", 2.9, 8.9, -FAR, ROAD_NEAR)
    _g("Ground_Far_E1_N", 2.9, 8.9, BEND_Y, FAR)
    _g("Ground_Far_E2_S", 4.5, 8.9, ROAD_NEAR, -62.0)
    _g("Ground_Far_E2_N", 4.5, 8.9, 62.0, BEND_Y)
    make_box("Road_Asphalt", (0.0, mid, 0.0), (3.6, span, 0.04), ASPHALT)
    di = 0
    dy = ROAD_NEAR
    while dy < BEND_Y - 1.0:
        make_box(f"Road_CenterLine_{di}", (0.0, dy, 0.022), (0.08, 1.20, 0.005), (0.90, 0.84, 0.50, 1.0))
        dy += 10.0
        di += 1
    for sgn in (-1, +1):
        make_box(f"Road_Gravel_Shoulder_{sgn:+d}", (sgn * 2.35, mid, 0.01), (1.1, span, 0.02), GRAVEL)
    # the ditches: a heightfield surface beside the gate (east), wedges beyond
    # V ditches (pass 421): down from the shoulder and back up to the field —
    # one wedge each fell to an outer edge that met nothing, a black slot
    # the length of the road
    from _props.streets import make_v_ditch
    make_v_ditch("Ditch_-1", -2.9, -4.5, ROAD_NEAR, BEND_Y, -0.36, 0.0, -0.05, GRASS)
    make_v_ditch("Ditch_+1_S", 2.9, 4.5, ROAD_NEAR, -62.0, -0.36, 0.0, -0.05, GRASS)
    make_v_ditch("Ditch_+1_N", 2.9, 4.5, 62.0, BEND_Y, -0.36, 0.0, -0.05, GRASS)
    make_ditch_field("Ditch_Field_E", 2.9, 8.9, -62.0, 62.0, 1.0, ditch_x=4.2, ditch_depth=0.42, ditch_half=1.3, amp=0.06, seed=4, color=GRASS, base_z=0.0)
    # the bend: twenty degrees east into the firs, then the run to the horizon
    make_road_bend("Road_Bend", 0.0, BEND_Y, 0.0, 20.0, 100.0, 1000.0, 3.6, asphalt=ASPHALT, line=(0.90, 0.84, 0.50, 1.0),
                   edge=(0.92, 0.92, 0.88, 1.0), shoulder_w=1.1, shoulder=GRAVEL, seg_len=10.0, edge_lines=False)
    # frost heaves and patches: a road that has been fixed by the county
    for i in range(21):
        make_box(f"Road_Patch_{i}", ((i % 3 - 1) * 0.9, -300.0 + i * 21.0, 0.021), (1.1, 1.6, 0.002), (0.18, 0.18, 0.19, 1.0))
    # the crick: runs beside the road from the east, crosses under at y 30
    make_box("Crick_Bed", (0.0, 30.0, -0.30), (60.0, 2.4, 0.20), (0.30, 0.28, 0.22, 1.0))
    make_box("Crick_Water_E", (16.0, 30.0, -0.17), (28.0, 1.6, 0.06), WATER)
    make_box("Crick_Water_W", (-16.0, 30.0, -0.17), (28.0, 1.6, 0.06), WATER)
    make_cyl("Culvert_Pipe", (0.0, 30.0, -0.10), 0.55, 8.0, (0.36, 0.36, 0.38, 1.0), axis="X", segments=12)
    for sgn in (-1, 1):
        make_box(f"Culvert_Headwall_{sgn:+d}", (sgn * 4.3, 30.0, 0.25), (0.40, 3.0, 1.10), CONCRETE)
        for pi in range(3):
            make_cyl(f"Crick_Rock_{sgn:+d}_{pi}", (sgn * (6.0 + pi * 2.5), 30.6 - (pi % 2) * 1.0, -0.05), 0.30, 0.30, (0.40, 0.40, 0.38, 1.0), segments=7)
    # county sign, mile post
    make_cyl("County_Sign_Post", (3.2, -72.0, 1.2), 0.05, 2.4, (0.40, 0.42, 0.40, 1.0), segments=6)
    make_box("County_Sign", (3.2, -72.0, 2.6), (0.04, 1.2, 0.50), (0.16, 0.42, 0.24, 1.0))
    make_box("County_Sign_Text", (3.17, -72.0, 2.6), (0.005, 1.0, 0.16), (0.94, 0.94, 0.90, 1.0))
    make_cyl("Mile_Post", (-3.0, 90.0, 0.8), 0.04, 1.6, (0.80, 0.84, 0.62, 1.0), segments=6)


def build_property():
    """The fence, the gate, the drive, the pole barn, the tool shed, the
    small house with the chicken coop out back — the west side."""
    make_wire_fence("Fence", -4.8, -40.0, 101.0, h=1.1, post_every=3.0, wires=3, wood=WOOD_GRAY, gap=(1.0, 5.0))
    make_cyl("Gate_Post_S", (-4.8, 1.2, 0.8), 0.10, 1.6, WOOD_GRAY, segments=6)
    make_cyl("Gate_Post_N", (-4.8, 4.8, 0.8), 0.10, 1.6, WOOD_GRAY, segments=6)
    make_box("Gate_Bar_Top", (-4.8, 3.0, 1.15), (0.06, 3.4, 0.08), (0.44, 0.40, 0.34, 1.0))
    make_box("Gate_Bar_Low", (-4.8, 3.0, 0.55), (0.06, 3.4, 0.08), (0.44, 0.40, 0.34, 1.0))
    make_box("Gate_Brace", (-4.8, 3.0, 0.85), (0.05, 0.08, 0.52), (0.44, 0.40, 0.34, 1.0))
    # mailboxes at the gate, the drive up to the barn
    for mi in range(3):
        make_cyl(f"Mailbox_Post_{mi}", (-3.4, -1.6 - mi * 0.5, 0.5), 0.04, 1.0, WOOD_GRAY, segments=6)
        make_box(f"Mailbox_{mi}", (-3.4, -1.6 - mi * 0.5, 1.12), (0.22, 0.40, 0.22), (0.30, 0.32, 0.36, 1.0) if mi else (0.62, 0.20, 0.16, 1.0))
    make_box("Drive_Gravel", (-16.0, 3.0, 0.005), (22.0, 3.2, 0.01), GRAVEL)
    make_box("Drive_Grass_Strip", (-16.0, 3.0, 0.011), (20.0, 0.4, 0.004), GRASS)
    # the pole barn: open front, tin roof on poles
    bx, by = -24.0, 12.0
    make_box("Pole_Barn_Slab", (bx, by, 0.05), (12.0, 9.0, 0.10), CONCRETE)
    for pi, (px, py) in enumerate(((-5.5, -4.0), (0.0, -4.0), (5.5, -4.0), (-5.5, 4.0), (0.0, 4.0), (5.5, 4.0))):
        make_cyl(f"Pole_Barn_Pole_{pi}", (bx + px, by + py, 2.0), 0.14, 3.8, TRUNK, segments=6)
    make_box("Pole_Barn_Back", (bx, by + 4.4, 2.0), (12.0, 0.10, 3.8), WOOD_RED)
    make_box("Pole_Barn_Side_W", (bx - 6.0, by, 2.0), (0.10, 8.8, 3.8), WOOD_RED)
    make_gable("Pole_Barn_Roof", (bx, by, 3.9 + 0.9), (12.8, 9.8, 1.8), TIN, ridge_axis="X")
    # 2026-09-27 (the 09-26 sheet, the barn insert): the tractor and the
    # hay were two flat boxes under the tin — a red one and an orange one.
    # A tractor is its wheels: two tall rear wheels, two small front, a
    # narrow hood ahead of a seat and a stack; the hay is BALES, stacked
    # with the gaps a stack has.
    tx, ty = bx - 2.5, by + 1.0
    TRACTOR_RED = (0.60, 0.26, 0.12, 1.0)
    TYRE = (0.10, 0.10, 0.10, 1.0)
    make_box("Pole_Barn_Tractor_Hood", (tx, ty + 1.0, 1.05), (0.90, 1.70, 0.70), TRACTOR_RED)
    make_box("Pole_Barn_Tractor_Body", (tx, ty - 0.6, 0.80), (1.10, 1.50, 0.60), TRACTOR_RED)
    make_box("Pole_Barn_Tractor_Seat", (tx, ty - 0.9, 1.30), (0.50, 0.50, 0.40), (0.14, 0.13, 0.12, 1.0))
    make_cyl("Pole_Barn_Tractor_Wheel", (tx, ty - 0.5, 1.30), 0.20, 0.03, (0.14, 0.13, 0.12, 1.0), axis="Y", segments=10)
    make_cyl("Pole_Barn_Tractor_Stack", (tx + 0.25, ty + 1.5, 1.9), 0.05, 1.0, (0.20, 0.20, 0.20, 1.0), segments=6)
    for sgn in (-1, 1):
        make_cyl(f"Pole_Barn_Tractor_Rear_{sgn:+d}", (tx + sgn * 0.85, ty - 0.6, 0.80), 0.80, 0.40, TYRE, axis="X", segments=12)
        make_cyl(f"Pole_Barn_Tractor_Front_{sgn:+d}", (tx + sgn * 0.60, ty + 1.4, 0.40), 0.40, 0.22, TYRE, axis="X", segments=10)
    HAY = (0.72, 0.60, 0.32, 1.0)
    HAY_DARK = (0.62, 0.50, 0.26, 1.0)
    hx0, hy0 = bx + 3.5, by + 2.0
    for row in range(3):
        for col in range(2):
            for lvl in range(2 if row < 2 else 1):
                make_box(f"Pole_Barn_Bale_{row}{col}{lvl}",
                         (hx0 - 0.70 + col * 1.40 + (0.35 if lvl else 0.0), hy0 - 1.0 + row * 1.0, 0.25 + lvl * 0.50),
                         (1.30, 0.94, 0.48), HAY if (row + col + lvl) % 2 else HAY_DARK)
    # the tool shed, the small house, the chicken coop out back
    make_shed("Tool_Shed", -12.0, -12.0, front="+X", w=3.0, d=2.4, h=2.3, wall_col=WOOD_GRAY, roof_col=TIN)
    make_box("Tool_Shed_Wheelbarrow", (-10.0, -14.2, 0.35), (0.7, 1.3, 0.5), (0.50, 0.30, 0.22, 1.0))
    hx, hy = -18.0, -22.0
    make_ranch_house("Small_House", hx, hy, "+X", (0.80, 0.78, 0.70, 1.0), (0.36, 0.30, 0.26, 1.0), w=8.0, d=7.0, h=3.0,
                     garage=False, lit=(False, True, False), porch=True, shrubs=False)
    make_box("Chicken_Coop", (hx - 1.0, hy - 6.0, 0.7), (2.4, 1.8, 1.4), WOOD_RED)
    make_wedge("Chicken_Coop_Roof", (hx - 1.0, hy - 6.0, 1.4 + 0.25), (2.6, 2.0, 0.5), TIN, high_end="+Y")
    make_box("Chicken_Run_Floor", (hx + 1.5, hy - 6.0, 0.005), (2.6, 2.4, 0.01), DIRT)
    for ci, (cx, cy) in enumerate(((hx + 0.3, hy - 7.1), (hx + 2.7, hy - 7.1), (hx + 0.3, hy - 4.9), (hx + 2.7, hy - 4.9))):
        make_cyl(f"Chicken_Run_Post_{ci}", (cx, cy, 0.6), 0.03, 1.2, WOOD_GRAY, segments=5)
    make_box("Chicken_Run_Wire_S", (hx + 1.5, hy - 7.1, 0.6), (2.4, 0.01, 1.2), (0.60, 0.62, 0.60, 0.4))
    make_box("Chicken_Run_Wire_E", (hx + 2.7, hy - 6.0, 0.6), (0.01, 2.2, 1.2), (0.60, 0.62, 0.60, 0.4))
    for hi in range(4):
        make_blob(f"Chicken_{hi}", (hx + 0.8 + (hi % 2) * 1.2, hy - 6.6 + (hi // 2) * 1.0, 0.14), 0.12, (0.88, 0.84, 0.76, 1.0), noise=0.2, seed=70 + hi, squash=0.8)


def build_fallen_house():
    """East of the road, in the field: the remains of a fallen-in
    house — a wall still standing, the roof slumped into the room,
    the chimney the only plumb thing left."""
    fx, fy = 18.0, -30.0
    # (pass 461) FALLEN IN. Draft 1 was a wall, a lean-to roof and a chimney:
    # from the road it read as an intact shed. Now the west gable stands to
    # half its peak with three bare rafters still reaching for a ridge that
    # is gone; the south slope has come down in one piece, its west end hung
    # on the gable and its east end on the floor; the north wall is a corner
    # with an empty window, a door frame standing alone, and a section
    # leaning out over the yard; the south wall is studs.
    ROOF_D, IN_D, RUST = (0.30, 0.27, 0.24, 1.0), (0.34, 0.31, 0.27, 1.0), (0.42, 0.26, 0.18, 1.0)
    top = 0.20
    make_box("Fallen_House_Floor", (fx, fy, 0.10), (8.0, 7.0, 0.20), (0.44, 0.40, 0.34, 1.0))
    ny = fy + 3.45
    # north wall, west corner: the empty window
    make_box("Fallen_House_Wall_N_Sill", (15.525, ny, top + 0.50), (2.95, 0.10, 1.00), WOOD_GRAY)
    make_box("Fallen_House_Wall_N_Pier_W", (14.525, ny, top + 1.70), (0.95, 0.10, 1.40), WOOD_GRAY)
    make_box("Fallen_House_Wall_N_Pier_E", (16.50, ny, top + 1.70), (1.00, 0.10, 1.40), WOOD_GRAY)
    make_box("Fallen_House_Wall_N_Header", (15.50, ny, top + 2.15), (1.00, 0.10, 0.50), WOOD_GRAY)
    make_box("Fallen_House_Window_Sash", (15.50, ny + 0.02, top + 1.45), (0.06, 0.05, 0.90), IN_D)
    # the door frame, standing alone
    for k, dx in enumerate((17.15, 18.15)):
        make_box(f"Fallen_House_Door_Post_{k}", (dx, ny, top + 1.05), (0.12, 0.12, 2.10), IN_D)
    make_box("Fallen_House_Door_Head", (17.65, ny, top + 2.16), (1.12, 0.12, 0.12), IN_D)
    # a section leaning out over the yard, and the east corner's stub
    make_rot_box("Fallen_House_Wall_N_Leaning", (19.5, ny + 0.41, top + 1.02), (2.2, 0.10, 2.2), WOOD_GRAY, roll=-0.38)
    make_box("Fallen_House_Wall_N_Stub", (21.45, ny, top + 0.45), (1.10, 0.10, 0.90), WOOD_GRAY)
    make_box("Fallen_House_Wall_E_Stub", (fx + 3.95, fy + 2.5, top + 0.40), (0.10, 1.9, 0.80), WOOD_GRAY)
    # the west gable: full height to the ridge line, half its peak left
    wx = fx - 3.95
    make_box("Fallen_House_Wall_W_A", (wx, fy + 1.2, top + 1.20), (0.10, 4.4, 2.40), WOOD_GRAY)
    make_wedge("Fallen_House_Gable_Half", (wx, fy + 1.70, top + 2.40 + 0.75), (0.10, 3.4, 1.5), WOOD_GRAY, high_end="-Y")
    make_box("Fallen_House_Wall_W_Low", (wx, fy - 2.2, top + 0.55), (0.10, 2.4, 1.10), WOOD_GRAY)
    for k, (dy, hh) in enumerate(((-1.3, 2.0), (-2.1, 1.6), (-3.0, 2.3))):
        make_box(f"Fallen_House_Stud_W_{k}", (wx, fy + dy, top + hh / 2.0), (0.09, 0.09, hh), IN_D)
    # the south wall: its sill and five bare studs
    make_box("Fallen_House_Sill_S", (fx, fy - 3.45, top + 0.06), (7.8, 0.12, 0.12), IN_D)
    for k, (dx, hh) in enumerate(((-3.2, 2.2), (-1.8, 1.2), (-0.4, 2.0), (1.4, 0.8), (3.0, 1.7))):
        make_box(f"Fallen_House_Stud_S_{k}", (fx + dx, fy - 3.45, top + 0.12 + hh / 2.0), (0.09, 0.09, hh), IN_D)
    # three rafters still up at the gable, two broken off short
    for k, rx in enumerate((14.55, 15.35, 16.15)):
        make_rot_box(f"Fallen_House_Rafter_{k}", (rx, fy + 1.72, top + 3.15), (0.07, 3.78, 0.13), IN_D, roll=-0.41)
    make_rot_box("Fallen_House_Rafter_Broken_0", (16.95, ny - 0.75, top + 1.51), (0.07, 1.5, 0.13), IN_D, roll=0.95)
    # one more, down: its foot on the floor, its head against the door's head
    make_rot_box("Fallen_House_Rafter_Fallen", (17.75, ny - 0.68, top + 1.07), (0.07, 2.44, 0.13), IN_D, roll=1.037)
    # the south slope, down in one piece: hung on the gable, on the floor at
    # its east end; the north slope in two slabs on the floor under it
    make_rot_box("Fallen_House_Roof_S", (fx + 0.15, fy - 1.7, top + 1.95), (7.2, 3.2, 0.12), ROOF_D, pitch=0.50, roll=-0.12)
    make_rot_box("Fallen_House_Roof_N_0", (16.4, fy + 1.6, top + 0.30), (3.0, 2.6, 0.12), ROOF_D, roll=0.16, yaw=0.20)
    make_rot_box("Fallen_House_Roof_N_1", (19.4, fy + 0.6, top + 0.26), (2.4, 2.8, 0.12), ROOF_D, pitch=-0.14, yaw=-0.35)
    make_box("Fallen_House_Chimney", (fx + 2.5, fy + 2.8, 2.6), (0.7, 0.7, 5.2), (0.46, 0.32, 0.26, 1.0))
    make_box("Fallen_House_Chimney_Cap", (fx + 2.5, fy + 2.8, 5.25), (0.9, 0.9, 0.10), (0.36, 0.26, 0.22, 1.0))
    # debris of lives: the cookstove by the chimney, an iron bedstead on the
    # floor inside the door, boards and shingles in the yard
    make_box("Fallen_House_Stove", (19.55, fy + 2.75, top + 0.38), (0.70, 0.55, 0.76), RUST)
    make_box("Fallen_House_Stove_Pipe", (19.55, fy + 2.75, top + 1.06), (0.14, 0.14, 0.60), RUST)
    make_box("Fallen_House_Bed_Head", (17.2, fy + 2.3, top + 0.50), (1.30, 0.05, 1.00), (0.22, 0.22, 0.24, 1.0))
    make_box("Fallen_House_Bed_Rail", (17.2, fy + 1.4, top + 0.28), (1.30, 1.80, 0.06), (0.22, 0.22, 0.24, 1.0))
    for di in range(6):
        make_box(f"Fallen_Debris_{di}", (fx - 3.0 + di * 1.3, fy - 4.2 + (di % 2) * 0.8, 0.12), (1.2, 0.3, 0.24), WOOD_GRAY)
    for di, (bx, by, bl, byaw) in enumerate(((15.2, ny + 1.3, 2.4, 0.3), (16.8, ny + 2.2, 1.8, -0.5), (18.6, ny + 1.9, 2.8, 1.2),
                                              (20.9, ny + 1.4, 1.6, 0.1), (12.9, fy + 1.4, 2.2, 1.4), (12.6, fy - 1.2, 1.5, 0.8),
                                              (13.2, ny + 0.9, 1.9, -0.9))):
        make_rot_box(f"Fallen_Board_{di}", (bx, by, 0.05), (bl, 0.18, 0.06), WOOD_GRAY if di % 2 else IN_D, yaw=byaw)
    for di, (bx, by) in enumerate(((17.6, ny + 1.0), (14.6, ny + 0.8), (12.8, fy + 0.2))):
        make_rot_box(f"Fallen_Shingles_{di}", (bx, by, 0.07), (0.9, 0.7, 0.10), ROOF_D, yaw=0.4 * di)
    make_blob("Fallen_House_Bramble", (16.2, fy - 1.6, 0.85), 0.9, (0.30, 0.38, 0.22, 1.0), noise=0.28, seed=91, squash=0.6)   # (pass 461) clear of the studs
    make_blob("Fallen_House_Bramble_Window", (15.5, ny - 0.5, top + 0.9), 0.75, (0.26, 0.36, 0.20, 1.0), noise=0.30, seed=92, squash=0.9)
    make_blob("Fallen_House_Bramble_Door", (18.3, ny + 0.5, 0.45), 0.55, (0.30, 0.38, 0.22, 1.0), noise=0.30, seed=93, squash=0.7)
    make_blob("Fallen_House_Bramble_Corner", (13.7, ny + 0.3, 0.55), 0.70, (0.28, 0.36, 0.20, 1.0), noise=0.30, seed=94, squash=0.7)
    make_box("Ruin_Path", (9.0, fy + 1.0, 0.004), (10.0, 0.8, 0.008), DIRT)
    # the dead snag beside the ruin, the brush that has taken the yard
    make_bare_tree("Snag", fx + 7.5, fy + 5.5, 9.0, seed=3, limbs=6)
    for si, (sx, sy, sh) in enumerate(((fx - 6.5, fy + 4.5, 1.1), (fx + 5.5, fy - 5.0, 0.9), (fx - 6.0, fy - 5.5, 1.3))):
        make_shrub(f"Yard_Shrub_{si}", sx, sy, h=sh, r=sh * 0.6, col=(0.30, 0.38, 0.22, 1.0))


def build_trees_and_fields():
    """Douglas firs over everything; hay field east, pasture west."""
    # the crick cuts both plates at y 28.8..31.2
    make_box("Field_E_S", (60.0, -60.6, 0.004), (100.0, 178.8, 0.008), FIELD)
    make_box("Field_E_N", (60.0, 90.6, 0.004), (100.0, 118.8, 0.008), FIELD)
    make_box("Pasture_W_S", (-60.0, -40.6, 0.004), (100.0, 138.8, 0.008), GRASS)
    make_box("Pasture_W_N", (-60.0, 90.6, 0.004), (100.0, 118.8, 0.008), GRASS)
    firs = ((-8.0, -48.0, 22.0), (-7.5, -34.0, 19.0), (-9.0, 40.0, 24.0), (-8.0, 58.0, 21.0), (-9.5, 76.0, 23.0), (-8.5, 96.0, 20.0),
            (8.0, -50.0, 20.0), (7.5, 8.0, 22.0), (9.0, 22.0, 18.0), (8.5, 48.0, 24.0), (9.5, 66.0, 21.0), (8.0, 88.0, 23.0),
            (-30.0, 30.0, 26.0), (-36.0, 50.0, 24.0), (30.0, 40.0, 25.0), (34.0, 60.0, 22.0), (26.0, -60.0, 24.0))
    for i, (x, y, h) in enumerate(firs):
        make_conifer(f"Fir_{i}", x, y, h, FIR if i % 2 else FIR_LT, TRUNK)
    make_broadleaf("Gate_Maple", -6.5, -6.0, 9.0, (0.36, 0.44, 0.22, 1.0), TRUNK)
    # hay bales in the east field, a stock tank in the pasture
    for bi in range(5):
        make_cyl(f"Hay_Bale_{bi}", (30.0 + bi * 7.0, 8.0 + (bi % 2) * 6.0, 0.7), 0.7, 1.4, (0.74, 0.62, 0.34, 1.0), axis="Y", segments=10)
    make_cyl("Stock_Tank", (-30.0, -8.0, 0.35), 1.4, 0.7, (0.56, 0.58, 0.58, 1.0), segments=12)
    make_cyl("Stock_Tank_Water", (-30.0, -8.0, 0.705), 1.3, 0.01, WATER, segments=12)


def build_night():
    """vol1's driving: the car on the road for the night preset, its
    headlight spill on the asphalt ahead; the Small Wood lights far up."""
    # (2026-10-31) the night's alone: the car, its spill and the town's lights
    # stood in the day and the dawn views too (the spill a pale slab on the
    # day road)
    # (pass 411) the night views: vol1/vol2 ch10 and December (vol2 ch4, the
    # family "in the car ... to check out Christmas lights on display")
    NT = "__swr_night"
    make_car("Night_Car", 0.9, -22.0, 4.6, (0.30, 0.34, 0.42, 1.0), along="Y", z0=0.02)
    make_box("Headlight_Spill" + NT, (0.9, -8.0, 0.0205), (3.2, 24.0, 0.001), (0.34, 0.34, 0.30, 1.0))
    for i in range(3):
        make_box(f"Town_Glow_{i}" + NT, (-40.0 + i * 30.0, 400.0, 3.0 + i), (6.0, 0.4, 2.0), (0.60, 0.52, 0.34, 1.0))
    try:
        import bpy
        empty = bpy.data.objects.new("NightCar" + NT, None)
        bpy.context.scene.collection.objects.link(empty)
        for obj in list(bpy.data.objects):
            if obj is not empty and obj.parent is None and obj.name.startswith("Night_Car"):
                obj.parent = empty
    except Exception:
        pass
    make_box("Church_Steeple", (-20.0, 380.0, 9.0), (2.0, 2.0, 18.0), (0.84, 0.84, 0.80, 1.0))


def build_christmas_2026_11():
    """(pass 411) vol2 ch4 "night lights", December: "My mother had a
    tradition; she'd round the family up in the car and take us on a long
    winding ride to check out Christmas lights on display" (n7); "Christmas
    lights were dull and obnoxious to me, an eye sore" (n35). The night road
    had no lights. A string of big bulbs along the small house's front eave
    (the `house` frame's house), on its own view (small_wood_road_christmas)
    — the other night chapters are not December. Draft 2: a lit tree in the
    lit window, the neighbors' lots with trees for sale (n6)."""
    XT = "__small_wood_road_christmas"
    ex, z = -13.98, 2.94                        # under the front eave (front +X at x -14.5, eave 0.55)
    cols = ((0.95, 0.16, 0.10, 1.0), (0.12, 0.80, 0.26, 1.0), (0.16, 0.36, 0.96, 1.0), (1.0, 0.70, 0.12, 1.0))
    ys = [-25.7 + k * 0.40 for k in range(20)]
    wire = []
    for k, y in enumerate(ys):
        wire.append((ex, y, z + (0.045 if k % 2 == 0 else 0.010)))   # clipped every other bulb, dipping between
        make_blob("Xmas_Bulb_%d%s" % (k, XT), (ex, y, z - 0.03), 0.055, cols[k % 4], noise=0.05, seed=200 + k, rings=4, segments=6, squash=1.3)
    make_tube("Xmas_Wire" + XT, wire, 0.008, (0.10, 0.16, 0.10, 1.0), segments=4)


def build_horizon():
    """(2026-10-31, draft 4) the coast range all round: forested hills, a
    near ring dark with firs and a far ring in haze, each a squashed blob
    sunk below the fields. The 09-03 far bands were flat-topped slabs (the
    day view's right edge read as a dark wall) and stood E and W only, so
    the view up the road ran flat to the horizon like a prairie. Hills keep
    off the road's line (it bends 20 deg E at y 150) so it still runs into
    the firs. Joined as stock (join_stock in main)."""
    def road_x(y):
        return 0.0 if y < 150.0 else (y - 150.0) * math.tan(math.radians(20.0))
    k = 0
    for ring, (dist, rad, sq, col) in enumerate(((400.0, 115.0, 0.66, (0.18, 0.27, 0.20, 1.0)),
                                                 (760.0, 210.0, 0.58, (0.34, 0.42, 0.42, 1.0)))):
        n = 22 if ring == 0 else 26
        for i in range(n):
            a = 2.0 * math.pi * (i + 0.5 * ring) / n
            cx, cy = dist * math.sin(a), dist * math.cos(a)
            r = rad * (0.85 + 0.30 * ((i * 7 + ring) % 5) / 4.0)
            if abs(cx - road_x(cy)) < r * 1.05 + 12.0:
                continue                                  # the road runs through here (N and S)
            if math.hypot(cx + 10.0, cy - 390.0) < r + 45.0:
                continue                                  # the steeple and the town's lights
            hk = sq + 0.10 * ((i * 3 + ring) % 3)
            make_blob(f"Hills_Stock_{ring}_{i}", (cx, cy, -r * 0.15), r, col, noise=0.10, seed=200 + k, squash=hk)
            k += 1


def build_property_dressing_2026_09():
    """Draft 2 (2026-09-26) — the first sheet with this road on it read
    as a road with a gate and firs: a county road with nobody home.
    What a lived-on property has that the frame lacked:
      · A TRUCK IN THE DRIVE — a pickup up the gravel by the pole barn,
        nose to the barn, the way a truck is left at a place someone
        lives (the night preset's car on the road is vol1's; this is
        the property's);
      · REFLECTORS on the mailboxes' road faces, the one thing at a
        rural gate that reads from the road at dawn and at night.
    NEXT (draft 3): the gate's chain and padlock; a dog on the porch;
    the roadside preset's minister's car pulled onto the gravel; the
    crick's headwall wet after the vol2 rain."""
    make_car("Property_Truck", -11.0, 2.4, 5.4, (0.36, 0.30, 0.24, 1.0), pickup=True, along="X", z0=0.015)
    for mi in range(3):
        make_box("Mailbox_Reflector_%d" % mi, (-3.285, -1.6 - mi * 0.5, 1.12), (0.01, 0.06, 0.06), (0.92, 0.40, 0.22, 1.0))


def build_crick_2026_11():
    """(2026-11-01, draft 6) the crick the path twists alongside: its banks
    were the field plates' cut edges, a 20 cm sheer drop to the bed; now a
    sloped mud bank each side, clear of the culvert's headwalls, and alders
    along the water (the north bank, and the south bank west of the road,
    where no path runs)."""
    MUD = (0.34, 0.29, 0.22, 1.0)
    for side, (xa, xb) in (("E", (8.95, 30.0)), ("W", (-30.0, -4.9))):   # E: past the ditch field (x 2.9..8.9)
        ln = xb - xa
        cx = (xa + xb) / 2.0
        make_wedge(f"Crick_Bank_S_{side}", (cx, 29.0, -0.10), (ln, 0.4, 0.20), MUD, high_end="-Y")
        make_wedge(f"Crick_Bank_N_{side}", (cx, 31.0, -0.10), (ln, 0.4, 0.20), MUD, high_end="+Y")
    ALDER = (0.28, 0.38, 0.22, 1.0)
    # (9 m and more off the firs: a fir's lowest tier spreads ~6 m)
    for k, (x, y, h) in enumerate(((8.5, 32.6, 8.0), (14.0, 32.9, 9.5), (19.0, 32.5, 8.5),
                                   (-6.5, 27.2, 8.5), (-11.5, 27.4, 8.0), (-16.5, 27.4, 9.0))):
        make_broadleaf(f"Crick_Alder_{k}", x, y, h, ALDER, TRUNK)


def build_paths_and_gate_2026_11():
    """(2026-11-01, draft 5) vol2 ch1, the runs off the road: "Knotted paths
    leading both up and down the road, twisting alongside cricks, emerging
    upon tool shed areas, out-of-the-way pole barns" — a worn path leaves
    the hay field's edge past the east ditch and twists along the crick's
    south bank into the firs; a second runs up the west pasture's fence
    line to the tool shed. And the gate's chain and padlock, looped round
    the south post and the gate's end (draft 2's NEXT)."""
    from _props.geometry import make_rot_box
    PATH = (0.46, 0.38, 0.28, 1.0)
    def path(prefix, pts, w=0.55, z=0.0095):
        for k in range(len(pts) - 1):
            (x0, y0), (x1, y1) = pts[k], pts[k + 1]
            ln = math.hypot(x1 - x0, y1 - y0)
            yaw = math.atan2(y1 - y0, x1 - x0)
            make_rot_box(f"{prefix}_{k}", ((x0 + x1) / 2.0, (y0 + y1) / 2.0, z), (ln + 0.25, w, 0.003), PATH, yaw=yaw)
    # along the crick (water at y 29.2..30.8, the bed to 28.8): the south bank
    path("Footpath_Crick", [(10.4, 22.6), (11.8, 25.6), (15.0, 27.2), (19.0, 26.6), (23.0, 27.6), (27.5, 27.0), (31.0, 27.8)])
    # the west pasture: up the fence line toward the tool shed (-12, -12)
    # (on the bare ground between the fence and the pasture plate, top -0.05)
    path("Footpath_Shed", [(-5.4, -6.0), (-7.2, -8.0), (-8.8, -9.4), (-9.8, -10.9)], w=0.5, z=-0.0475)
    # the gate's chain: a loop round the south post and the gate's end, a
    # padlock hanging off it
    IRON = (0.22, 0.21, 0.20, 1.0)
    for k, (dx, dy) in enumerate(((0.0, -0.16), (0.16, 0.0), (0.0, 0.16), (-0.16, 0.0))):
        make_box(f"Gate_Chain_{k}", (-4.8 + dx, 1.26 + dy, 0.92), (0.03 if dx else 0.32, 0.32 if dx else 0.03, 0.03), IRON)
    make_box("Gate_Padlock", (-4.62, 1.26, 0.85), (0.05, 0.03, 0.07), (0.72, 0.58, 0.28, 1.0))
    make_box("Gate_Padlock_Shackle", (-4.62, 1.26, 0.905), (0.035, 0.01, 0.04), IRON)


def main():
    clear_scene()
    build_road()
    build_property()
    build_fallen_house()
    build_trees_and_fields()
    build_night()
    build_horizon()
    build_property_dressing_2026_09()
    build_paths_and_gate_2026_11()
    build_crick_2026_11()
    build_christmas_2026_11()
    from _props.geometry import join_stock
    join_stock()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/small_wood_road.glb"))
    print(f"\n[build_small_wood_road] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
