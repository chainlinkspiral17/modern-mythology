"""VOL 5 · THE IRON CROW — a Marigny dive (Strength, Judgement) · and
vol1's "A Hip Bar" (the chalk table, the pinball, Missile Command).

DRAFT 6 (2026-10-09) — rebuilt big from the prose. Draft 5 was a 9 x 6 m
box with a 3.6 m hole where the front door should have been, a pool
table built straight through Douglas's booth table, a round six-top
jammed between them, and vol1's CHALK TABLE misread as the pool table
— but the vol1 crowd SITS at the chalk table ("Faust and Jacob sit at
the table ... Helen pushes Margaret into the seat next to Faust ...
Emily puts her purse next to Faust ... Cozy corner"): it is a
chalkboard-topped table with benches, in a corner, and Faust is
"already drawing up some wacky shit" on it.

The chapters, what each one needs from the room:

- Strength: "The game flickered on the bar TV. Muted ... under the
  buzzing neon of three different beer signs, two of which had been
  advertising brands the bar no longer carried ... His corner booth
  smelled faintly of stale smoke ... His hands rested on the sticky
  tabletop ... the bartender — a tired-looking woman ... from behind
  the bar ... He stood up from the booth. The cheap vinyl sighed ...
  He left the empty bottles on the table ... a folded twenty under the
  saltshaker ... walked out into the humid New Orleans night."
- Judgement: "his corner booth at the Iron Crow ... The bar's lights
  flickered. The bartender gripped the edge of the bar ... He walked
  out of the Iron Crow into the shaking morning. He crossed the street."
- vol1 ch3: the chalk table, shots, ginger beer, "Going out for a
  smoke" (the front door + the sidewalk), "I didn't know they had
  pinball here. Yes. And Missile Command, too."

Plan (13 x 9 m, ceiling 3.9 m — an old Marigny storefront with a
pressed-tin ceiling): the street front on the S wall (two big windows,
a glazed door with a transom between them); the long bar on the N side
with a real bartender's lane (1.0 m) between it and the back bar; the
mirror, the bottle shelves, the TV up on the N wall where the corner
booth can see it; Douglas's L booth in the SW corner under the three
beer neons; the arcade (pinball, Missile Command) along the W wall; the
pool table mid-floor under its billiard lamp; the chalk-table corner SE
under the E window; the jukebox and the dartboard on the E wall; the
back hall (kegs, restroom, the delivery door) through the E wall's
north end; the street at night outside.

Draft 7 targets: a second gas-lamp and the gallery balconies across
the street read at window scale; the bartender's side (well, speed
rail) at insert scale; a crossword Times-Picayune for Judgement's
morning variant (a per-preset prop set, the way the day rigs work).
"""
import math, os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb, make_tube, make_dome, make_taper_cyl
from _props.structure import make_floor, make_wall, make_ceiling, make_window, make_wall_with_openings
from _props.store_fixtures import make_counter_bullnose
from _props.decor import make_wall_clock
from _props.objects import make_liquor_bottle, make_bowl, make_bottle, make_pint_glass, make_can
from _props.detail import make_traffic_wear, make_floor_stain

ROOM_W = 13.0; ROOM_D = 9.0; CEIL = 3.90
XW, XE = -ROOM_W / 2.0 + 0.10, ROOM_W / 2.0 - 0.10      # wall room faces
YS, YN = 0.10, ROOM_D - 0.10
PAL = {"wall": (0.50, 0.30, 0.21, 1.0), "baseboard": (0.16, 0.10, 0.08, 1.0)}
COL_FLOOR = (0.34, 0.24, 0.17, 1.0); COL_SEAM = (0.20, 0.13, 0.10, 1.0)
COL_WAIN = (0.24, 0.15, 0.10, 1.0); COL_RAIL = (0.30, 0.20, 0.13, 1.0)
COL_BAR = (0.40, 0.22, 0.14, 1.0); COL_TOP = (0.24, 0.14, 0.09, 1.0); COL_BRASS = (0.86, 0.62, 0.28, 1.0)
COL_BOTTLE_AMBER = (0.78, 0.42, 0.16, 1.0); COL_BOTTLE_CLEAR = (0.78, 0.84, 0.86, 0.55); COL_BOTTLE_GREEN = (0.32, 0.42, 0.20, 1.0)
VINYL = (0.40, 0.17, 0.15, 1.0); WOOD = (0.35, 0.24, 0.15, 1.0); IRON = (0.14, 0.14, 0.15, 1.0)
GLASS = (0.80, 0.86, 0.88, 0.5)
WIN_W_X, WIN_E_X, WIN_Z, WIN_WD, WIN_H = -3.4, 4.4, 1.80, 1.8, 1.5
DOOR_X, DOOR_W, DOOR_H = 1.2, 1.1, 2.9                   # opening incl. the transom
HALL_Y, HALL_W = 7.85, 1.0                               # back-hall opening in the E wall
BAR_X0, BAR_X1, BAR_Y0, BAR_Y1, BAR_H = -5.0, 3.0, 6.25, 6.85, 1.06
BACK_Y0 = 8.30                                           # back bar's front face
BOOTH = (-5.07, 1.33)                                    # Douglas's table centre
CHALK = (5.09, 1.98)                                     # the chalk table centre
POOL = (-0.8, 3.0)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y',
              palette=PAL, baseboard_face_sign=+1)
    make_wall_with_openings("Wall_E", (ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y',
                            palette=PAL, baseboard_face_sign=-1, openings=[(HALL_Y, 1.10, HALL_W, 2.20)])
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL, axis='X', palette=PAL,
              baseboard_face_sign=-1)
    make_wall_with_openings("Wall_S", (0.0, 0.0, 0), length=ROOM_W + 0.4, height=CEIL, axis='X', palette=PAL,
                            baseboard_face_sign=+1,
                            openings=[(WIN_W_X, WIN_Z, WIN_WD, WIN_H), (DOOR_X, DOOR_H / 2.0, DOOR_W, DOOR_H),
                                      (WIN_E_X, WIN_Z, WIN_WD, WIN_H)])
    # the pressed-tin ceiling: dark-painted tin squares on a grid, a cornice round it
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
                 palette={"tile": (0.36, 0.30, 0.22, 1.0), "grid": (0.22, 0.17, 0.12, 1.0)})
    for nm, c, s in (("Cornice_N", (0.0, YN - 0.06, CEIL - 0.09), (ROOM_W - 0.2, 0.12, 0.18)),
                     ("Cornice_S", (0.0, YS + 0.06, CEIL - 0.09), (ROOM_W - 0.2, 0.12, 0.18)),
                     ("Cornice_W", (XW + 0.06, ROOM_D / 2.0, CEIL - 0.09), (0.12, ROOM_D - 0.44, 0.18)),
                     ("Cornice_E", (XE - 0.06, ROOM_D / 2.0, CEIL - 0.09), (0.12, ROOM_D - 0.44, 0.18))):
        make_box(nm, c, s, (0.30, 0.24, 0.17, 1.0))
    for nm, x in (("Window_SW", WIN_W_X), ("Window_SE", WIN_E_X)):
        make_window(nm, (x, YS, WIN_Z), width=WIN_WD, height=WIN_H, room_dir=+1, see_through=True)


def build_wainscot():
    """Dark beadboard to 1.0 m on every wall, a chair rail on top —
    sitting on the baseboard (z 0.16), stopping at the openings."""
    top, z0 = 1.00, 0.16
    zc, h = (top + z0) / 2.0, top - z0
    runs = [("W", 'Y', XW, 0.10, ROOM_D - 0.10, None), ("N", 'X', YN, -ROOM_W / 2.0 + 0.10, ROOM_W / 2.0 - 0.10, None),
            ("E0", 'Y', XE, 0.10, HALL_Y - HALL_W / 2.0, None), ("E1", 'Y', XE, HALL_Y + HALL_W / 2.0, ROOM_D - 0.10, None),
            ("S0", 'X', YS, -ROOM_W / 2.0 + 0.10, DOOR_X - DOOR_W / 2.0, None),
            ("S1", 'X', YS, DOOR_X + DOOR_W / 2.0, ROOM_W / 2.0 - 0.10, None)]
    for tag, ax, line, a0, a1, _ in runs:
        sign = {"W": 1, "E0": -1, "E1": -1, "N": -1, "S0": 1, "S1": 1}[tag]
        mid, ln = (a0 + a1) / 2.0, a1 - a0
        if ax == 'Y':
            make_box(f"Wainscot_{tag}", (line + sign * 0.01, mid, zc), (0.02, ln, h), COL_WAIN)
            make_box(f"ChairRail_{tag}", (line + sign * 0.02, mid, top + 0.02), (0.04, ln, 0.04), COL_RAIL)
        else:
            make_box(f"Wainscot_{tag}", (mid, line + sign * 0.01, zc), (ln, 0.02, h), COL_WAIN)
            make_box(f"ChairRail_{tag}", (mid, line + sign * 0.02, top + 0.02), (ln, 0.04, 0.04), COL_RAIL)


def build_front_door():
    """The glazed street door (closed) with its transom; the push bar
    and the bell; OPEN neon hung in the E window."""
    dx, y = DOOR_X, 0.0
    make_box("Front_Door_Frame_Head", (dx, y, 2.38), (DOOR_W, 0.24, 0.06), WOOD)
    make_box("Front_Door_Transom", (dx, y, 2.64), (DOOR_W - 0.08, 0.03, 0.44), (0.62, 0.70, 0.74, 0.45))
    make_box("Front_Door_Leaf", (dx, y + 0.02, 1.175), (DOOR_W - 0.06, 0.05, 2.33), (0.26, 0.17, 0.11, 1.0))
    make_box("Front_Door_Glass", (dx, y + 0.05, 1.45), (DOOR_W - 0.34, 0.01, 1.30), (0.55, 0.62, 0.66, 0.45))
    make_box("Front_Door_PushBar", (dx, y + 0.10, 1.05), (DOOR_W - 0.30, 0.03, 0.04), COL_BRASS)
    for i, sx in enumerate((-0.38, 0.38)):
        make_box(f"Front_Door_PushBar_Post_{i}", (dx + sx, y + 0.065, 1.05), (0.03, 0.04, 0.04), COL_BRASS)
    make_box("Front_Door_Mat", (dx, 0.55, 0.008), (1.2, 0.8, 0.016), (0.16, 0.14, 0.12, 1.0))
    make_box("Open_Neon_Box", (WIN_E_X + 0.45, YS + 0.08, 2.15), (0.62, 0.03, 0.26), (0.10, 0.10, 0.12, 1.0))
    make_box("Open_Neon_Tube", (WIN_E_X + 0.45, YS + 0.10, 2.15), (0.50, 0.01, 0.14), (0.96, 0.30, 0.34, 1.0))
    make_tube("Open_Neon_Chain", [(WIN_E_X + 0.25, YS + 0.08, 2.28), (WIN_E_X + 0.45, YS + 0.08, 2.52),
                                  (WIN_E_X + 0.65, YS + 0.08, 2.28)], 0.004, IRON, segments=4)


def build_bar():
    """The long bar: panelled mahogany front, the top with its bullnose,
    the brass foot rail on standoffs; the underbar on the bartender's
    side; the back bar, the mirror, two bottle shelves on brackets."""
    bx, bl = (BAR_X0 + BAR_X1) / 2.0, BAR_X1 - BAR_X0
    by, bd = (BAR_Y0 + BAR_Y1) / 2.0, BAR_Y1 - BAR_Y0
    make_box("Bar_Front", (bx, by, BAR_H / 2.0), (bl, bd, BAR_H), COL_BAR)
    top_z = BAR_H + 0.06
    make_box("Bar_Top", (bx, by - 0.10, BAR_H + 0.03), (bl + 0.10, bd + 0.20, 0.06), COL_TOP)
    make_counter_bullnose("Bar", (bx, BAR_Y0 - 0.20, top_z), length=bl + 0.10, palette={"top": COL_TOP}, axis='X')
    make_box("Bar_Kick", (bx, BAR_Y0 - 0.01, 0.08), (bl, 0.02, 0.16), (0.14, 0.08, 0.05, 1.0))
    for i in range(9):                                   # raised panels on the customer face
        px = BAR_X0 + 0.45 + i * (bl - 0.9) / 8.0
        make_box(f"Bar_Panel_{i}", (px, BAR_Y0 - 0.012, 0.60), (0.70, 0.02, 0.62), (0.46, 0.27, 0.17, 1.0))
    make_cyl("Bar_FootRail", (bx, BAR_Y0 - 0.22, 0.20), 0.025, bl - 0.2, COL_BRASS, axis='X', segments=8)
    for i in range(6):
        sx = BAR_X0 + 0.3 + i * (bl - 0.6) / 5.0
        make_box(f"Bar_FootRail_Standoff_{i}", (sx, BAR_Y0 - 0.125, 0.20), (0.03, 0.25, 0.03), COL_BRASS)
    make_box("Bar_End_E", (BAR_X1 + 0.015, by, BAR_H / 2.0), (0.03, bd, BAR_H), (0.46, 0.27, 0.17, 1.0))
    # the underbar: the bartender's work shelf, the ice well, the speed rail
    make_box("Underbar", (bx, BAR_Y1 + 0.22, 0.43), (bl - 0.2, 0.44, 0.86), (0.52, 0.52, 0.54, 1.0))
    make_box("Ice_Well", (-1.6, BAR_Y1 + 0.22, 0.865), (0.80, 0.34, 0.01), (0.86, 0.90, 0.92, 1.0))
    make_box("Speed_Rail", (-1.6, BAR_Y1 + 0.47, 0.70), (1.10, 0.06, 0.04), (0.62, 0.62, 0.64, 1.0))
    for i in range(6):
        make_liquor_bottle(f"Well_Bottle_{i}", -2.10 + i * 0.2, BAR_Y1 + 0.47, 0.72,
                           [COL_BOTTLE_CLEAR, COL_BOTTLE_AMBER, COL_BOTTLE_GREEN][i % 3], h=0.26, r=0.03)
    for i, x in enumerate((-3.4, 0.6)):
        make_box(f"Bar_Mat_Rubber_{i}", (x, BAR_Y1 + 0.85, 0.008), (1.4, 0.60, 0.016), (0.10, 0.10, 0.11, 1.0))
    # the back bar: cabinet, its top, the mirror, two glass shelves on brackets
    cx0, cx1 = BAR_X0, 3.0
    make_box("BackBar_Cabinet", ((cx0 + cx1) / 2.0, (BACK_Y0 + YN) / 2.0, 0.46), (cx1 - cx0, YN - BACK_Y0, 0.92), COL_BAR)
    make_box("BackBar_Top", ((cx0 + cx1) / 2.0, (BACK_Y0 + YN) / 2.0 - 0.02, 0.95), (cx1 - cx0, YN - BACK_Y0 + 0.04, 0.06), COL_TOP)
    for i in range(6):
        make_box(f"BackBar_Door_{i}", (cx0 + 0.67 + i * 1.33, BACK_Y0 - 0.01, 0.48), (1.15, 0.02, 0.70), (0.46, 0.27, 0.17, 1.0))
    make_box("Bar_Mirror", (-1.0, YN - 0.01, 1.85), (7.2, 0.02, 1.50), (0.36, 0.38, 0.38, 1.0))   # old smoky glass (draft 6: a bright pane read as a white wall)
    for i, x in enumerate((-4.6, 2.6)):
        make_box(f"Bar_Mirror_Pilaster_{i}", (x, YN - 0.04, 1.85), (0.16, 0.06, 1.62), COL_BAR)
    make_box("Bar_Mirror_Head", (-1.0, YN - 0.05, 2.70), (7.6, 0.08, 0.12), COL_BAR)
    for shf, sz in enumerate((1.42, 1.86)):
        make_box(f"Bottle_Shelf_{shf}", (-1.0, YN - 0.13, sz), (6.6, 0.22, 0.02), (0.70, 0.78, 0.80, 0.55))
        for j, x in enumerate((-4.0, -1.0, 2.0)):
            make_box(f"Bottle_Shelf_{shf}_Bracket_{j}", (x, YN - 0.12, sz - 0.05), (0.03, 0.20, 0.08), COL_BRASS)
        for bi in range(20):
            bxp = -4.15 + bi * 0.33
            tint = [COL_BOTTLE_AMBER, COL_BOTTLE_CLEAR, COL_BOTTLE_GREEN][(shf + bi) % 3]
            make_liquor_bottle(f"Bottle_{shf}_{bi}", bxp, YN - 0.13, sz + 0.01, tint,
                               h=0.24 + ((shf + bi) % 3) * 0.035, r=0.033)
    for bi in range(16):                                 # the back bar top: the everyday bottles
        make_liquor_bottle(f"BackBar_Bottle_{bi}", -4.4 + bi * 0.27, BACK_Y0 + 0.30, 0.98,
                           [COL_BOTTLE_CLEAR, COL_BOTTLE_AMBER, COL_BOTTLE_AMBER, COL_BOTTLE_GREEN][bi % 4],
                           h=0.28 + (bi % 3) * 0.03, r=0.036)
    make_box("Register", (1.9, BACK_Y0 + 0.30, 1.12), (0.42, 0.38, 0.28), (0.60, 0.60, 0.58, 1.0))
    make_box("Register_Keys", (1.9, BACK_Y0 + 0.10, 1.17), (0.32, 0.02, 0.10), (0.30, 0.30, 0.32, 1.0))
    make_box("Register_Drawer", (1.9, BACK_Y0 + 0.10, 1.02), (0.36, 0.02, 0.06), (0.50, 0.50, 0.48, 1.0))
    # the beer cooler at the back bar's east end: glass doors, cans inside, its own light
    make_box("Cooler_Body", (3.75, (BACK_Y0 + YN) / 2.0, 0.95), (1.40, YN - BACK_Y0, 1.90), (0.18, 0.18, 0.20, 1.0))
    for i, x in enumerate((3.42, 4.08)):
        make_box(f"Cooler_Glass_{i}", (x, BACK_Y0 - 0.01, 1.00), (0.60, 0.02, 1.50), (0.70, 0.84, 0.90, 0.45))
        make_box(f"Cooler_Handle_{i}", (x + (0.24 if i == 0 else -0.24), BACK_Y0 - 0.04, 1.05), (0.03, 0.04, 0.40), (0.62, 0.62, 0.64, 1.0))
    for r_, z in enumerate((0.42, 0.86, 1.30)):
        make_box(f"Cooler_Rack_{r_}", (3.75, BACK_Y0 + 0.30, z), (1.24, 0.50, 0.015), (0.70, 0.72, 0.74, 1.0))
        for k in range(8):
            make_can(f"Cooler_Can_{r_}_{k}", 3.22 + k * 0.15, BACK_Y0 + 0.15, z + 0.008,
                     [(0.80, 0.20, 0.18, 1.0), (0.86, 0.80, 0.70, 1.0), (0.20, 0.36, 0.66, 1.0), (0.30, 0.50, 0.30, 1.0)][(k + r_) % 4])
    make_box("Cooler_Light", (3.75, BACK_Y0 + 0.08, 1.80), (1.20, 0.06, 0.03), (0.90, 0.96, 1.0, 1.0))


def build_on_the_bar():
    top = BAR_H + 0.06
    make_box("Tap_Tower", (-0.70, 6.62, top + 0.14), (0.42, 0.10, 0.28), (0.72, 0.72, 0.74, 1.0))
    for i, tx in enumerate((-0.84, -0.70, -0.56)):
        make_cyl(f"Tap_{i}_Spout", (tx, 6.54, top + 0.16), 0.012, 0.08, COL_BRASS, segments=6, axis='Y')
        make_cyl(f"Tap_{i}_Handle", (tx, 6.62, top + 0.36), 0.018, 0.16,
                 [(0.86, 0.20, 0.18, 1.0), (0.14, 0.14, 0.16, 1.0), (0.92, 0.84, 0.40, 1.0)][i], segments=6)
    make_box("Bar_Mat", (-0.70, 6.35, top + 0.006), (0.60, 0.28, 0.012), (0.12, 0.12, 0.14, 1.0))
    make_cyl("Tip_Jar", (0.40, 6.62, top + 0.08), 0.06, 0.16, (0.78, 0.84, 0.86, 0.5), segments=10)
    make_box("Tip_Jar_Bills", (0.40, 6.62, top + 0.05), (0.07, 0.05, 0.08), (0.56, 0.62, 0.50, 1.0))
    for i, nx in enumerate((-3.2, 1.6)):
        make_box(f"Napkin_Dispenser_{i}", (nx, 6.66, top + 0.07), (0.14, 0.09, 0.14), (0.62, 0.62, 0.64, 1.0))
        make_box(f"Napkin_{i}", (nx, 6.605, top + 0.07), (0.10, 0.004, 0.09), (0.94, 0.94, 0.90, 1.0))
    for i, ax in enumerate((-4.0, -1.9, 0.9, 2.4)):
        make_cyl(f"Bar_Ashtray_{i}", (ax, 6.25, top + 0.015), 0.055, 0.03, (0.30, 0.30, 0.32, 1.0), segments=10)
    make_bowl("Peanut_Bowl", -2.6, 6.30, top, (0.46, 0.40, 0.32, 1.0), r=0.09, h=0.05)
    # the last customer's glass and bottle, a coaster
    make_pint_glass("Bar_Pint_0", -0.10, 6.22, top, (0.86, 0.66, 0.30, 0.7))
    make_bottle("Bar_Longneck_0", 1.20, 6.30, top, (0.60, 0.34, 0.12, 0.9))
    make_box("Bar_Coaster_0", (-0.10, 6.22, top + 0.002), (0.10, 0.10, 0.004), (0.86, 0.84, 0.78, 1.0))
    # the glass rack over the bar, on chains to the tin
    make_box("Glass_Rack", (0.0, 6.55, 2.45), (3.0, 0.40, 0.03), WOOD)
    for i in range(4):
        make_cyl(f"Glass_Rack_Rail_{i}", (0.0, 6.40 + i * 0.10, 2.42), 0.008, 3.0, COL_BRASS, segments=6, axis='X')
    for i in range(14):
        make_cyl(f"Hung_Glass_{i}", (-1.3 + i * 0.2, 6.45 + (i % 3) * 0.10, 2.33), 0.035, 0.14, GLASS, segments=8)
    for i, cx in enumerate((-1.3, 1.3)):
        make_cyl(f"Glass_Rack_Chain_{i}", (cx, 6.55, (2.465 + CEIL) / 2.0), 0.006, CEIL - 2.465, (0.30, 0.30, 0.32, 1.0), segments=5)


def build_stools():
    for si in range(7):
        sx = -4.4 + si * 1.15
        sy = BAR_Y0 - 0.55
        make_cyl(f"Stool_{si}_Seat", (sx, sy, 0.77), 0.19, 0.08, VINYL, segments=12)
        make_cyl(f"Stool_{si}_Pillar", (sx, sy, 0.375), 0.035, 0.69, (0.70, 0.70, 0.72, 1.0), segments=8)
        make_cyl(f"Stool_{si}_Foot", (sx, sy, 0.0125), 0.20, 0.025, (0.30, 0.30, 0.32, 1.0), segments=12)
        make_box(f"Stool_{si}_FootBar", (sx, sy, 0.30), (0.34, 0.025, 0.025), (0.70, 0.70, 0.72, 1.0))


def build_tv_and_signs():
    """The bar TV up on the N wall's west end over the bottles — where
    the corner booth looks; the IRON CROW neon over the mirror; the
    clock; the gator; the beads; the specials board."""
    tx, tz = -3.2, 3.10
    make_box("Bar_TV_Mount", (tx, YN - 0.04, tz), (0.30, 0.08, 0.20), IRON)
    make_box("Bar_TV", (tx, YN - 0.12, tz), (1.30, 0.08, 0.76), (0.10, 0.10, 0.12, 1.0))
    make_box("Bar_TV_Screen", (tx, YN - 0.165, tz), (1.20, 0.01, 0.66), (0.30, 0.46, 0.40, 1.0))
    # the game: a green field, the line of scrimmage, the score bug
    make_box("Bar_TV_Field_Line", (tx + 0.05, YN - 0.171, tz - 0.05), (0.02, 0.003, 0.50), (0.90, 0.92, 0.88, 1.0))
    make_box("Bar_TV_ScoreBug", (tx - 0.38, YN - 0.171, tz - 0.26), (0.36, 0.003, 0.08), (0.12, 0.14, 0.30, 1.0))
    make_tube("Bar_TV_Cord", [(tx + 0.10, YN - 0.08, tz - 0.38), (tx + 0.10, YN - 0.05, 2.75)], 0.008, IRON, segments=4)
    # IRON CROW: a crow in neon over the mirror's head, the name beside it
    cx, cz = 0.4, 3.18
    make_box("IronCrow_Box", (cx, YN - 0.03, cz), (2.10, 0.06, 0.56), (0.12, 0.10, 0.12, 1.0))
    red = (0.96, 0.26, 0.20, 1.0)
    make_box("IronCrow_Tube", (cx + 0.30, YN - 0.07, cz + 0.05), (1.20, 0.02, 0.14), red)
    make_box("IronCrow_Tube_Underline", (cx + 0.30, YN - 0.07, cz - 0.12), (1.30, 0.02, 0.025), red)
    make_box("IronCrow_Bird_Body", (cx - 0.68, YN - 0.07, cz), (0.30, 0.02, 0.12), red)
    make_box("IronCrow_Bird_Head", (cx - 0.50, YN - 0.07, cz + 0.08), (0.10, 0.02, 0.09), red)
    make_box("IronCrow_Bird_Beak", (cx - 0.42, YN - 0.07, cz + 0.07), (0.07, 0.02, 0.025), (0.98, 0.78, 0.30, 1.0))
    make_box("IronCrow_Bird_Tail", (cx - 0.88, YN - 0.07, cz - 0.04), (0.14, 0.02, 0.05), red)
    make_box("IronCrow_Bird_Leg", (cx - 0.66, YN - 0.07, cz - 0.11), (0.02, 0.02, 0.10), red)
    make_wall_clock("Clock", (2.15, YN, 3.20), frozen_hour=11, frozen_min=47, facing='-Y')
    # the gator over the cooler
    gx, gz = 3.85, 3.10
    make_box("Gator_Plaque", (gx, YN - 0.02, gz), (0.90, 0.04, 0.34), WOOD)
    make_box("Gator_Head", (gx + 0.05, YN - 0.13, gz), (0.52, 0.18, 0.16), (0.30, 0.34, 0.22, 1.0))
    make_box("Gator_Snout", (gx - 0.30, YN - 0.13, gz - 0.03), (0.22, 0.14, 0.10), (0.30, 0.34, 0.22, 1.0))
    make_box("Gator_Jaw", (gx - 0.20, YN - 0.13, gz - 0.09), (0.40, 0.16, 0.04), (0.42, 0.40, 0.28, 1.0))
    for i in range(6):
        make_box(f"Gator_Tooth_{i}", (gx - 0.36 + i * 0.07, YN - 0.13 + (0.06 if i % 2 else -0.06), gz - 0.065),
                 (0.015, 0.012, 0.025), (0.92, 0.90, 0.82, 1.0))
    for i, oy in enumerate((-0.07, 0.07)):
        make_dome(f"Gator_Eye_{i}", (gx + 0.18, YN - 0.13 + oy, gz + 0.08), 0.025, (0.86, 0.70, 0.20, 1.0), rings=3, segments=8)
    # Mardi Gras beads on the mirror's pilasters, and off the TV's corner (draft 6: not across the screen)
    for i, (x0, x1, z, col) in enumerate(((-4.8, -4.4, 2.50, (0.60, 0.26, 0.74, 1.0)),
                                          (2.4, 2.8, 2.50, (0.26, 0.70, 0.36, 1.0)))):
        make_tube(f"Beads_{i}", [(x0, YN - 0.09, z + 0.20), ((x0 + x1) / 2.0, YN - 0.09, z - 0.10), (x1, YN - 0.09, z + 0.20)], 0.012, col, segments=6)
    make_tube("Beads_2", [(tx - 0.62, YN - 0.17, tz + 0.37), (tx - 0.70, YN - 0.17, tz + 0.05), (tx - 0.68, YN - 0.17, tz - 0.30)],
              0.012, (0.92, 0.78, 0.22, 1.0), segments=6)
    # the specials board on the E wall's north end, over the bartender's exit
    make_box("Specials_Board", (XE - 0.015, 6.55, 2.05), (0.012, 0.66, 0.80), (0.12, 0.14, 0.12, 1.0))
    make_box("Specials_Board_Frame", (XE - 0.006, 6.55, 2.05), (0.008, 0.72, 0.86), WOOD)
    for i in range(5):
        make_box(f"Specials_Line_{i}", (XE - 0.023, 6.55 + (0.03 if i % 2 else -0.03), 2.33 - i * 0.14),
                 (0.002, 0.40 - (i % 3) * 0.06, 0.03),
                 [(0.92, 0.88, 0.70, 1.0), (0.96, 0.60, 0.60, 1.0), (0.70, 0.90, 0.96, 1.0)][i % 3])


def build_booth():
    """Douglas's corner booth, SW: cheap oxblood vinyl on an L of
    benches, the table on its pedestal, the sconce, and on the table
    what Strength leaves there — the empties, the saltshaker with the
    folded twenty under it, an ashtray, the sticky patches where his
    hands rest. Three beer neons round the corner: two dead brands,
    one live."""
    tx, ty = BOOTH
    # W bench (he sits here, facing the room and the TV)
    make_box("Booth_Bench_W", (XW + 0.395, 1.73, 0.23), (0.55, 1.90, 0.46), VINYL)
    make_box("Booth_Back_W", (XW + 0.07, 1.73 - 0.275, 0.73), (0.10, 2.45, 0.54), VINYL)
    make_box("Booth_Bench_S", (-5.47, YS + 0.405, 0.23), (1.60, 0.55, 0.46), VINYL)
    make_box("Booth_Back_S", (-5.47 + 0.05, YS + 0.07, 0.73), (1.50, 0.10, 0.54), VINYL)
    for i, (c, s) in enumerate((((XW + 0.395, 1.73, 0.475), (0.53, 1.86, 0.03)), ((-5.47, YS + 0.405, 0.475), (1.56, 0.53, 0.03)))):
        make_box(f"Booth_Cushion_{i}", c, s, (0.46, 0.20, 0.17, 1.0))
    make_box("Booth_Cushion_Tear", (XW + 0.40, 1.30, 0.492), (0.08, 0.14, 0.004), (0.80, 0.72, 0.56, 1.0))
    make_box("Booth_Table", (tx, ty, 0.725), (1.10, 0.90, 0.05), WOOD)
    make_box("Booth_Table_Edge", (tx, ty - 0.455, 0.725), (1.10, 0.01, 0.05), COL_BRASS)
    make_cyl("Booth_Table_Leg", (tx, ty, 0.35), 0.05, 0.70, (0.20, 0.19, 0.20, 1.0), segments=8)
    make_box("Booth_Table_Foot", (tx, ty, 0.015), (0.56, 0.56, 0.03), (0.20, 0.19, 0.20, 1.0))
    # the sconce over the table on the W wall
    make_box("Booth_Sconce_Plate", (XW + 0.01, ty, 1.78), (0.02, 0.14, 0.22), (0.30, 0.24, 0.16, 1.0))
    make_box("Booth_Sconce_Arm", (XW + 0.08, ty, 1.80), (0.12, 0.02, 0.02), (0.30, 0.24, 0.16, 1.0))
    make_taper_cyl("Booth_Sconce_Shade", (XW + 0.20, ty, 1.80), 0.09, 0.05, 0.14, (0.86, 0.56, 0.28, 1.0), segments=10)
    t = 0.75
    make_cyl("Saltshaker", (tx + 0.12, ty - 0.08, t + 0.04), 0.022, 0.08, (0.88, 0.88, 0.84, 0.9), segments=8)
    make_box("Folded_Twenty", (tx + 0.12, ty - 0.08, t + 0.003), (0.08, 0.04, 0.006), (0.55, 0.62, 0.50, 1.0))
    for bi, (bx, by) in enumerate(((tx - 0.25, ty + 0.18), (tx + 0.22, ty + 0.25))):
        make_bottle(f"Empty_Bottle_{bi}", bx, by, t, (0.36, 0.26, 0.14, 0.8))
    make_cyl("Booth_Ashtray", (tx + 0.30, ty - 0.22, t + 0.015), 0.055, 0.03, (0.30, 0.30, 0.32, 1.0), segments=10)
    make_box("Booth_Ashtray_Butt", (tx + 0.30, ty - 0.22, t + 0.033), (0.04, 0.008, 0.008), (0.90, 0.86, 0.78, 1.0))
    make_box("Hands_Sticky_Patch_A", (tx - 0.32, ty - 0.10, t + 0.0008), (0.14, 0.11, 0.0015), (0.38, 0.30, 0.22, 1.0))
    make_box("Hands_Sticky_Patch_B", (tx - 0.30, ty + 0.14, t + 0.0008), (0.11, 0.13, 0.0015), (0.36, 0.28, 0.21, 1.0))
    # three beer neons: over the booth, on the S pier by the booth, over the arcade
    for ni, (c, s, tube, col) in enumerate((
            ((XW + 0.03, 1.95, 2.30), (0.06, 0.90, 0.46), (XW + 0.07, 1.95, 2.30), (0.86, 0.32, 0.34, 1.0)),
            ((-5.55, YS + 0.03, 2.40), (0.80, 0.06, 0.40), (-5.55, YS + 0.07, 2.40), (0.30, 0.72, 0.62, 1.0)),
            ((XW + 0.03, 4.00, 2.40), (0.06, 0.85, 0.45), (XW + 0.07, 4.00, 2.40), (0.90, 0.70, 0.28, 1.0)))):
        make_box(f"BeerNeon_{ni}_Box", c, s, (0.14, 0.12, 0.14, 1.0))
        ts = (0.02, s[1] - 0.20, s[2] - 0.17) if s[0] < 0.1 else (s[0] - 0.20, 0.02, s[2] - 0.17)
        make_box(f"BeerNeon_{ni}_Tube", tube, ts, col)


def build_arcade():
    """vol1: "I didn't know they had pinball here. Yes. And Missile
    Command, too." Along the W wall north of the booth."""
    py = 3.20
    make_box("Pinball_Body", (XW + 0.95, py, 0.78), (1.35, 0.72, 0.30), (0.62, 0.26, 0.30, 1.0))
    make_box("Pinball_Glass", (XW + 0.95, py, 0.945), (1.25, 0.66, 0.03), (0.55, 0.62, 0.66, 0.4))
    make_box("Pinball_Backbox", (XW + 0.36, py, 1.42), (0.16, 0.70, 0.70), (0.70, 0.32, 0.36, 1.0))
    make_box("Pinball_Backglass", (XW + 0.45, py, 1.45), (0.01, 0.60, 0.52), (0.92, 0.62, 0.34, 1.0))
    make_box("Pinball_Neck", (XW + 0.36, py, 1.01), (0.14, 0.40, 0.14), (0.62, 0.26, 0.30, 1.0))
    for li in range(4):
        make_box(f"Pinball_Leg_{li}", (XW + 0.38 + 1.15 * (li % 2), py - 0.30 + 0.60 * (li // 2), 0.315),
                 (0.05, 0.05, 0.63), (0.55, 0.57, 0.58, 1.0))
    make_box("Pinball_Coin_Door", (XW + 1.630, py, 0.78), (0.01, 0.30, 0.22), (0.30, 0.30, 0.32, 1.0))
    my = 4.70
    make_box("MissileCmd_Cab", (XW + 0.40, my, 0.88), (0.80, 0.70, 1.76), (0.16, 0.16, 0.20, 1.0))
    make_box("MissileCmd_Screen", (XW + 0.805, my, 1.28), (0.01, 0.54, 0.42), (0.14, 0.30, 0.22, 1.0))
    make_box("MissileCmd_Marquee", (XW + 0.805, my, 1.66), (0.01, 0.62, 0.18), (0.80, 0.30, 0.24, 1.0))
    make_box("MissileCmd_Panel", (XW + 0.88, my, 0.98), (0.16, 0.62, 0.06), (0.24, 0.24, 0.28, 1.0))
    make_cyl("MissileCmd_Trackball", (XW + 0.88, my, 1.02), 0.035, 0.02, (0.86, 0.80, 0.30, 1.0), segments=10)
    # the cigarette machine and the ATM in the nook past the bar's west end
    make_box("Cig_Machine", (XW + 0.32, 7.25, 0.85), (0.62, 0.85, 1.70), (0.48, 0.42, 0.34, 1.0))
    make_box("Cig_Machine_Window", (XW + 0.635, 7.25, 1.20), (0.01, 0.70, 0.40), (0.86, 0.80, 0.66, 1.0))
    for k in range(6):
        make_box(f"Cig_Machine_Knob_{k}", (XW + 0.65, 6.95 + k * 0.12, 0.88), (0.02, 0.06, 0.04), (0.76, 0.74, 0.70, 1.0))
    make_box("ATM", (XW + 0.25, 8.35, 0.80), (0.50, 0.55, 1.60), (0.30, 0.32, 0.36, 1.0))
    make_box("ATM_Screen", (XW + 0.505, 8.35, 1.30), (0.01, 0.30, 0.22), (0.30, 0.56, 0.62, 1.0))


def build_pool():
    """The pool table mid-floor under its billiard lamp; the cue rack
    on the S wall pier between the window and the door."""
    x, y = POOL
    make_box("Pool_Table_Body", (x, y, 0.62), (2.50, 1.40, 0.36), WOOD)
    make_box("Pool_Table_Felt", (x, y, 0.805), (2.24, 1.14, 0.02), (0.16, 0.36, 0.24, 1.0))
    for i, (c, s) in enumerate((((x, y - 0.635, 0.82), (2.50, 0.13, 0.05)), ((x, y + 0.635, 0.82), (2.50, 0.13, 0.05)),
                                ((x - 1.185, y, 0.82), (0.13, 1.14, 0.05)), ((x + 1.185, y, 0.82), (0.13, 1.14, 0.05)))):
        make_box(f"Pool_Table_Rail_{i}", c, s, (0.28, 0.19, 0.12, 1.0))
    for lx in (-1.05, 1.05):
        for ly in (-0.55, 0.55):
            make_box(f"Pool_Leg_{lx:+.2f}_{ly:+.2f}", (x + lx, y + ly, 0.22), (0.16, 0.16, 0.44), WOOD)
    for bi in range(5):
        make_cyl(f"Pool_Ball_{bi}", (x - 0.4 + bi * 0.22, y - 0.05 + 0.12 * (bi % 2), 0.843), 0.028, 0.056,
                 [(0.86, 0.82, 0.74, 1.0), (0.72, 0.22, 0.18, 1.0), (0.14, 0.14, 0.16, 1.0), (0.86, 0.70, 0.20, 1.0),
                  (0.22, 0.30, 0.66, 1.0)][bi], segments=8)
    make_box("Pool_Cue_Chalk", (x + 1.185, y + 0.40, 0.857), (0.024, 0.024, 0.024), (0.30, 0.50, 0.80, 1.0))
    # the billiard lamp: a long shade on two chains
    make_box("Pool_Lamp_Shade", (x, y, 1.80), (1.60, 0.36, 0.16), (0.16, 0.30, 0.20, 1.0))
    for i in range(3):
        make_cyl(f"Pool_Lamp_Bulb_{i}" if i else "Pool_Lamp_Bulb", (x - 0.5 + i * 0.5, y, 1.70), 0.05, 0.04, (1.0, 0.88, 0.60, 1.0), segments=8)
    for i, cx in enumerate((-0.6, 0.6)):
        make_cyl(f"Pool_Lamp_Chain_{i}", (x + cx, y, (1.88 + CEIL) / 2.0), 0.006, CEIL - 1.88, (0.30, 0.30, 0.32, 1.0), segments=5)
    make_box("Cue_Rack", (-1.2, YS + 0.03, 1.35), (0.60, 0.06, 1.10), WOOD)
    for ci in range(4):
        make_cyl(f"Cue_{ci}", (-1.38 + ci * 0.12, YS + 0.07, 1.35), 0.012, 1.00, (0.66, 0.52, 0.34, 1.0), segments=5)
    # a high-top between the pool table and the chalk corner
    hx, hy = 2.80, 2.60
    make_cyl("HighTop_Top", (hx, hy, 1.04), 0.36, 0.04, WOOD, segments=14)
    make_cyl("HighTop_Post", (hx, hy, 0.52), 0.04, 1.00, IRON, segments=8)
    make_cyl("HighTop_Foot", (hx, hy, 0.015), 0.26, 0.03, IRON, segments=12)
    for i, sy in enumerate((hy - 0.58, hy + 0.58)):
        make_cyl(f"HighTop_Stool_{i}_Seat", (hx, sy, 0.77), 0.17, 0.06, WOOD, segments=12)
        make_cyl(f"HighTop_Stool_{i}_Pillar", (hx, sy, 0.38), 0.03, 0.70, IRON, segments=8)
        make_cyl(f"HighTop_Stool_{i}_Foot", (hx, sy, 0.0125), 0.18, 0.025, IRON, segments=12)
    make_pint_glass("HighTop_Pint", hx + 0.10, hy, 1.06, (0.86, 0.66, 0.30, 0.7))


def build_chalk_table():
    """vol1's CHALK TABLE, SE: a chalkboard-topped table in the cozy
    corner — the E bench along the wall and an L round the S wall under
    the window, a loose bench on the west side. On it what vol1 puts
    there: the shots, the ginger beer, the chalk, Faust's drawing."""
    tx, ty = CHALK
    make_box("Chalk_Bench_E", (XE - 0.395, 1.98, 0.23), (0.55, 2.40, 0.46), VINYL)
    make_box("Chalk_Back_E", (XE - 0.07, 1.98 - 0.275, 0.73), (0.10, 2.95, 0.54), VINYL)
    make_box("Chalk_Bench_S", (5.43, YS + 0.405, 0.23), (1.70, 0.55, 0.46), VINYL)
    make_box("Chalk_Back_S", (5.43 - 0.05, YS + 0.07, 0.73), (1.60, 0.10, 0.54), VINYL)
    make_box("Chalk_Bench_W_Seat", (tx - 0.88, ty + 0.05, 0.44), (0.40, 1.90, 0.05), WOOD)
    for i, ly in enumerate((-0.80, 0.90)):
        make_box(f"Chalk_Bench_W_Leg_{i}", (tx - 0.88, ty + 0.05 + ly, 0.2075), (0.34, 0.06, 0.415), WOOD)
    make_box("Chalk_Table_Top", (tx, ty, 0.73), (1.08, 2.20, 0.04), (0.11, 0.14, 0.12, 1.0))
    for i, (c, s) in enumerate((((tx, ty - 1.12, 0.735), (1.12, 0.04, 0.05)), ((tx, ty + 1.12, 0.735), (1.12, 0.04, 0.05)),
                                ((tx - 0.56, ty, 0.735), (0.04, 2.28, 0.05)), ((tx + 0.56, ty, 0.735), (0.04, 2.28, 0.05)))):
        make_box(f"Chalk_Table_Frame_{i}", c, s, WOOD)
    for i, ly in enumerate((-0.80, 0.80)):
        make_box(f"Chalk_Table_Leg_{i}", (tx, ty + ly, 0.355), (0.10, 0.10, 0.71), IRON)
        make_box(f"Chalk_Table_Foot_{i}", (tx, ty + ly, 0.015), (0.70, 0.08, 0.03), IRON)
    t = 0.75
    # the drawing: a face in chalk lines, a star, a rocket, scribbles
    chalk = [(0.94, 0.94, 0.90, 1.0), (0.96, 0.70, 0.74, 1.0), (0.70, 0.86, 0.96, 1.0), (0.96, 0.90, 0.56, 1.0)]
    for i in range(12):
        a = i * math.pi / 6.0
        make_box(f"Chalk_Doodle_Face_{i}", (tx + 0.18 + 0.16 * math.cos(a), ty - 0.35 + 0.16 * math.sin(a), t + 0.0006),
                 (0.07, 0.012, 0.001), chalk[0])
    for i, (dx, dy) in enumerate(((0.12, -0.30), (0.24, -0.30))):
        make_box(f"Chalk_Doodle_Eye_{i}", (tx + dx, ty + dy, t + 0.0006), (0.02, 0.02, 0.001), chalk[0])
    make_box("Chalk_Doodle_Mouth", (tx + 0.18, ty - 0.42, t + 0.0006), (0.10, 0.012, 0.001), chalk[1])
    for i in range(5):
        a = i * 2.0 * math.pi / 5.0
        make_box(f"Chalk_Doodle_Star_{i}", (tx - 0.20 + 0.06 * math.cos(a), ty + 0.40 + 0.06 * math.sin(a), t + 0.0006),
                 (0.14, 0.012, 0.001), chalk[3])
    for i in range(6):
        make_box(f"Chalk_Doodle_Scrawl_{i}", (tx - 0.25 + (i % 2) * 0.05, ty - 0.80 + i * 0.05, t + 0.0006),
                 (0.24 - i * 0.02, 0.01, 0.001), chalk[2 if i % 2 else 1])
    make_box("Chalk_Doodle_Rocket", (tx + 0.10, ty + 0.75, t + 0.0006), (0.06, 0.26, 0.001), chalk[2])
    make_cyl("Chalk_Tin", (tx + 0.38, ty + 0.95, t + 0.03), 0.045, 0.06, (0.62, 0.62, 0.64, 1.0), segments=10)
    for i in range(4):
        make_box(f"Chalk_Stick_{i}", (tx + 0.33 + i * 0.04, ty + 0.70, t + 0.006), (0.012, 0.08, 0.012), chalk[i])
    # the round: shots, the ginger beer, two pints
    for i in range(6):
        make_cyl(f"Chalk_Shot_{i}", (tx - 0.36 + (i % 2) * 0.10, ty - 0.40 + (i // 2) * 0.22, t + 0.03), 0.022, 0.06, GLASS, segments=8)
    make_bottle("Ginger_Beer", tx + 0.36, ty + 0.10, t, (0.80, 0.70, 0.40, 0.9))
    for i, (dx, dy) in enumerate(((-0.30, 0.35), (0.34, -0.70))):
        make_pint_glass(f"Chalk_Pint_{i}", tx + dx, ty + dy, t, (0.86, 0.66, 0.30, 0.7))
    # Emily's purse on the bench next to Faust
    make_box("Emily_Purse", (XE - 0.40, 2.70, 0.55), (0.26, 0.12, 0.18), (0.20, 0.30, 0.56, 1.0))
    make_tube("Emily_Purse_Strap", [(XE - 0.50, 2.70, 0.64), (XE - 0.40, 2.70, 0.74), (XE - 0.30, 2.70, 0.64)], 0.006,
              (0.12, 0.12, 0.14, 1.0), segments=4)
    # its pendant
    make_cyl("Chalk_Lamp_Cord", (tx, ty, (CEIL + 1.98) / 2.0), 0.006, CEIL - 1.98, IRON, segments=5)
    make_taper_cyl("Chalk_Lamp_Shade", (tx, ty, 1.90), 0.22, 0.06, 0.16, (0.80, 0.40, 0.20, 1.0), segments=12)
    make_cyl("Chalk_Lamp_Bulb", (tx, ty, 1.80), 0.05, 0.05, (1.0, 0.82, 0.50, 1.0), segments=8)
    # the photos and flyers over the corner
    for i, (y, z, w, h, col) in enumerate(((1.10, 1.70, 0.30, 0.40, (0.86, 0.80, 0.66, 1.0)),
                                           (1.70, 1.85, 0.42, 0.56, (0.70, 0.30, 0.30, 1.0)),
                                           (2.35, 1.70, 0.30, 0.30, (0.30, 0.40, 0.60, 1.0)),
                                           (2.90, 1.90, 0.36, 0.48, (0.92, 0.84, 0.40, 1.0)))):
        make_box(f"Chalk_Corner_Flyer_{i}", (XE - 0.006, y, z), (0.012, w, h), col)


def build_jukebox_and_darts():
    jx, jy = XE - 0.30, 3.95
    make_box("Jukebox_Body", (jx, jy, 0.75), (0.60, 0.80, 1.50), (0.78, 0.42, 0.16, 1.0))
    make_box("Jukebox_TopArch", (jx, jy, 1.70), (0.60, 0.80, 0.40), (0.62, 0.32, 0.14, 1.0))
    make_box("Jukebox_Glass", (jx - 0.305, jy, 1.10), (0.01, 0.70, 0.50), (0.32, 0.22, 0.18, 0.55))
    make_box("Jukebox_LightBar", (jx - 0.305, jy, 1.50), (0.01, 0.70, 0.10), (0.96, 0.78, 0.42, 1.0))
    for i, dy in enumerate((-0.36, 0.36)):
        make_box(f"Jukebox_Bubbler_{i}", (jx - 0.305, jy + dy, 1.10), (0.01, 0.05, 1.00), (0.96, 0.56, 0.30, 1.0))
    dy = 5.50
    make_cyl("Dartboard", (XE - 0.025, dy, 1.73), 0.23, 0.04, (0.20, 0.18, 0.16, 1.0), segments=16, axis='X')
    make_cyl("Dartboard_Bull", (XE - 0.048, dy, 1.73), 0.03, 0.006, (0.80, 0.20, 0.18, 1.0), segments=10, axis='X')
    for i in range(6):
        make_box(f"Dartboard_Wedge_{i}", (XE - 0.047, dy + 0.14 * (1 if i % 2 else -1) * (0.5 + 0.5 * (i // 2)) * 0.4,
                                          1.73 + 0.12 * ((i // 2) - 1)), (0.004, 0.05, 0.05),
                 (0.86, 0.82, 0.70, 1.0) if i % 2 else (0.20, 0.48, 0.30, 1.0))
    make_box("Dartboard_Surround", (XE - 0.008, dy, 1.73), (0.016, 0.80, 0.80), (0.12, 0.10, 0.10, 1.0))
    make_box("Score_Board", (XE - 0.012, dy + 0.70, 1.70), (0.012, 0.40, 0.50), (0.12, 0.14, 0.12, 1.0))
    for i in range(5):
        make_box(f"Score_Line_{i}", (XE - 0.018, dy + 0.70 - 0.12 + (i % 2) * 0.22, 1.88 - i * 0.07), (0.002, 0.10, 0.012),
                 (0.88, 0.88, 0.84, 1.0))
    make_box("Oche_Tape", (XE - 2.37, dy, 0.001), (0.04, 0.60, 0.002), (0.86, 0.80, 0.30, 1.0))


def build_back_hall():
    """Through the E wall's north end: the short back hall — kegs, the
    restroom door, the delivery door with its push bar and EXIT sign."""
    hx0, hx1 = ROOM_W / 2.0 + 0.10, ROOM_W / 2.0 + 2.10
    hy0, hy1 = HALL_Y - 0.95, ROOM_D - 0.10
    hc = 3.0
    make_box("Hall_Floor", ((hx0 + hx1) / 2.0, (hy0 + hy1) / 2.0, -0.05), (hx1 - hx0 + 0.1, hy1 - hy0 + 0.1, 0.10), (0.30, 0.30, 0.28, 1.0))
    make_box("Hall_Ceil", ((hx0 + hx1) / 2.0, (hy0 + hy1) / 2.0, hc + 0.05), (hx1 - hx0 + 0.2, hy1 - hy0 + 0.2, 0.10), (0.56, 0.54, 0.50, 1.0))
    hpal = {"wall": (0.62, 0.58, 0.48, 1.0), "baseboard": (0.20, 0.18, 0.16, 1.0)}
    make_wall("Hall_Wall_S", ((hx0 + hx1) / 2.0, hy0 - 0.10, 0), length=hx1 - hx0, height=hc, axis='X', palette=hpal, baseboard_face_sign=+1)
    make_wall("Hall_Wall_N", ((hx0 + hx1) / 2.0, hy1 + 0.10, 0), length=hx1 - hx0, height=hc, axis='X', palette=hpal, baseboard_face_sign=-1)
    make_wall("Hall_Wall_E", (hx1 + 0.10, (hy0 + hy1) / 2.0, 0), length=hy1 - hy0 + 0.4, height=hc, axis='Y', palette=hpal, baseboard_face_sign=-1)
    make_box("Back_Door", (hx1 - 0.025, HALL_Y, 1.05), (0.05, 0.92, 2.10), (0.44, 0.46, 0.48, 1.0))
    make_box("Back_Door_PushBar", (hx1 - 0.08, HALL_Y, 1.02), (0.04, 0.72, 0.05), (0.70, 0.70, 0.72, 1.0))
    make_box("Exit_Sign", (hx1 - 0.06, HALL_Y, 2.35), (0.10, 0.38, 0.16), (0.16, 0.16, 0.18, 1.0))
    make_box("Exit_Sign_Face", (hx1 - 0.115, HALL_Y, 2.35), (0.01, 0.30, 0.10), (0.96, 0.24, 0.20, 1.0))
    make_box("Restroom_Door", ((hx0 + hx1) / 2.0, hy1 - 0.025, 1.05), (0.82, 0.05, 2.10), (0.30, 0.22, 0.14, 1.0))
    make_cyl("Restroom_Door_Knob", ((hx0 + hx1) / 2.0 + 0.30, hy1 - 0.07, 1.00), 0.03, 0.04, COL_BRASS, segments=8, axis='Y')
    make_box("Restroom_Sign", ((hx0 + hx1) / 2.0, hy1 - 0.056, 1.60), (0.36, 0.012, 0.12), (0.92, 0.90, 0.84, 1.0))
    for k in range(3):
        kx = hx0 + 0.40 + k * 0.55
        make_cyl(f"Keg_{k}", (kx, hy0 + 0.30, 0.30), 0.21, 0.60, (0.70, 0.72, 0.74, 1.0), segments=12)
        make_cyl(f"Keg_{k}_Coupler", (kx, hy0 + 0.30, 0.63), 0.04, 0.06, (0.30, 0.30, 0.32, 1.0), segments=8)
    make_cyl("Keg_3", (hx0 + 0.67, hy0 + 0.30, 0.90), 0.21, 0.60, (0.70, 0.72, 0.74, 1.0), segments=12)
    make_box("Hand_Truck_Plate", (hx1 - 0.35, hy0 + 0.20, 0.02), (0.36, 0.22, 0.02), (0.30, 0.32, 0.34, 1.0))
    make_box("Hand_Truck_Frame", (hx1 - 0.35, hy0 + 0.12, 0.62), (0.40, 0.04, 1.20), (0.30, 0.32, 0.34, 1.0))
    make_cyl("Hall_Bulb_Cord", ((hx0 + hx1) / 2.0, HALL_Y, hc - 0.10), 0.006, 0.20, IRON, segments=5)
    make_cyl("Hall_Bulb", ((hx0 + hx1) / 2.0, HALL_Y, hc - 0.24), 0.04, 0.08, (1.0, 0.86, 0.58, 1.0), segments=8)


def build_ceiling():
    """Two slow fans with light kits, the pendants over the bar."""
    for fi, (fx, fy) in enumerate(((-3.6, 2.6), (3.2, 4.6))):
        fz = CEIL - 0.25
        make_cyl(f"Fan_{fi}_Downrod", (fx, fy, CEIL - 0.25), 0.02, 0.50, P.METAL_BLACK)
        make_cyl(f"Fan_{fi}_Motor", (fx, fy, fz - 0.32), 0.12, 0.14, COL_BRASS, segments=12)
        for bi, (dx, dy, sw, sd) in enumerate(((0.46, 0, 0.66, 0.16), (-0.46, 0, 0.66, 0.16), (0, 0.46, 0.16, 0.66), (0, -0.46, 0.16, 0.66))):
            make_box(f"Fan_{fi}_Blade_{bi}", (fx + dx, fy + dy, fz - 0.33), (sw, sd, 0.02), (0.36, 0.24, 0.14, 1.0))
        make_cyl(f"Fan_{fi}_LightKit", (fx, fy, fz - 0.45), 0.09, 0.12, (0.96, 0.84, 0.62, 1.0), segments=12)
    for pi, px in enumerate((-4.0, -2.4, 2.3)):
        make_cyl(f"Pendant_{pi}_Cord", (px, 6.45, (CEIL + 2.45) / 2.0), 0.005, CEIL - 2.45, P.METAL_BLACK)
        make_taper_cyl(f"Pendant_{pi}_Shade", (px, 6.45, 2.37), 0.17, 0.05, 0.16, (0.92, 0.66, 0.28, 1.0), segments=12)
        make_cyl(f"Pendant_{pi}_Bulb", (px, 6.45, 2.27), 0.05, 0.05, (1.0, 0.86, 0.56, 1.0), segments=8)


def build_wear():
    make_traffic_wear("Wear_Door_Bar", [(DOOR_X, 0.4), (1.4, 3.0), (0.6, 5.0)], width=0.9)
    make_traffic_wear("Wear_Booth", [(-4.3, 1.4), (-3.0, 3.6), (-1.5, 5.0)], width=0.6)
    make_traffic_wear("Wear_Hall", [(3.4, 7.4), (6.2, HALL_Y)], width=0.7)
    for i, (c, r) in enumerate((((-1.4, 5.4), 0.25), ((0.8, 5.5), 0.18), ((5.0, 3.4), 0.2), ((-5.2, 2.3), 0.22))):
        make_floor_stain(f"Floor_Stain_{i}", c, radius=r)


def build_street():
    """The Marigny at night outside the windows and the door."""
    make_box("Ground_Sidewalk", (0.0, -2.0, -0.03), (30.0, 4.0, 0.06), (0.52, 0.50, 0.46, 1.0))
    make_box("Curb", (0.0, -4.05, -0.06), (30.0, 0.14, 0.14), (0.60, 0.58, 0.54, 1.0))
    make_box("Ground_Street", (0.0, -10.0, -0.14), (30.0, 12.0, 0.06), (0.24, 0.24, 0.26, 1.0))
    make_box("Ground_Sidewalk_Far", (0.0, -17.0, -0.03), (30.0, 2.0, 0.06), (0.50, 0.48, 0.44, 1.0))
    # Creole cottages across the street: pastel fronts, shutters, a gallery
    cols = [(0.62, 0.70, 0.62, 1.0), (0.80, 0.62, 0.48, 1.0), (0.56, 0.62, 0.74, 1.0), (0.84, 0.76, 0.52, 1.0), (0.70, 0.50, 0.52, 1.0)]
    for c in range(5):
        cx = -11.0 + c * 5.5
        make_box(f"Out_Cottage_{c}", (cx, -18.6, 2.8), (5.3, 1.2, 5.6), cols[c])
        make_box(f"Out_Cottage_{c}_Roof", (cx, -18.9, 5.9), (5.5, 1.6, 0.6), (0.30, 0.26, 0.24, 1.0))
        for w in range(2):
            wx = cx - 1.2 + w * 2.4
            lit = (c + w) % 3 == 0
            make_box(f"Out_Cottage_{c}_Win_{w}", (wx, -17.99, 2.0), (0.90, 0.02, 2.2),
                     (0.92, 0.78, 0.44, 1.0) if lit else (0.16, 0.18, 0.22, 1.0))
            for s in (-1, 1):
                make_box(f"Out_Cottage_{c}_Shutter_{w}_{s:+d}", (wx + s * 0.62, -17.98, 2.0), (0.32, 0.02, 2.2), (0.20, 0.36, 0.30, 1.0))
        make_box(f"Out_Cottage_{c}_Gallery", (cx, -17.3, 3.9), (5.3, 1.4, 0.08), (0.36, 0.34, 0.32, 1.0))
        for k in range(3):
            make_box(f"Out_Cottage_{c}_Post_{k}", (cx - 2.4 + k * 2.4, -16.7, 1.95), (0.10, 0.10, 3.9), (0.86, 0.84, 0.80, 1.0))
    make_cyl("Street_Lamp_Pole", (-1.6, -3.7, 2.0), 0.05, 4.0, (0.20, 0.22, 0.24, 1.0), segments=8)
    make_box("Street_Lamp_Head", (-1.6, -4.1, 3.9), (0.28, 0.46, 0.14), (0.96, 0.88, 0.60, 1.0))
    from _props.vehicles import make_car
    make_car("Parked_Car", 5.6, -6.0, 4.4, (0.26, 0.26, 0.30, 1.0), along="X", z0=-0.11)
    make_car("Parked_Car_1", -7.2, -6.0, 4.6, (0.48, 0.20, 0.18, 1.0), along="X", z0=-0.11)


def main():
    clear_scene()
    build_shell(); build_wainscot(); build_front_door()
    build_bar(); build_on_the_bar(); build_stools(); build_tv_and_signs()
    build_booth(); build_arcade(); build_pool(); build_chalk_table(); build_jukebox_and_darts()
    build_back_hall(); build_ceiling(); build_wear(); build_street()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/new_orleans_bar.glb"))
    print(f"\n[build_new_orleans_bar] exporting to {out}")
    export_glb(out)


if __name__ == "__main__": main()
