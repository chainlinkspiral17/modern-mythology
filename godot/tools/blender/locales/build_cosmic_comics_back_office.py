"""Cosmic Comics — back office — vol6 placement script.

DRAFT 4 (2026-09-18, lore/_VISUAL_PROGRAM.md §3, 11 placements): turned
desk legs and an apron, the monitor on a foot and neck with a screen,
drawer pulls and labels on the filing cabinets, the bulb as a bulb on
a socket with a chain and a pull, the carafe and the chair seat as
profiles,  the room's first WEAR (entry
paths, the casters' oval, the forearm patch, coffee rings, ink, pin
holes); D3 (a power strip under the desk and cords from everything
that plugs in). The .tscn loses the two fluorescent practicals the
prose's "single overhead with a pull chain" never had.

DRAFT 5 targets: the longbox tops as comics at a lean, not a slab;
the light table lit from within (an emissive plane + practical); the
corkboard's pages as pages (a drawn line or two); the office door with
its knob and a hand-worn patch; the service door's threshold and the
alley beyond it when it stands open; Deck: the sheet's establish and
`insert notebook` under the bulb.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import (clear_scene, make_box, make_chamfer_box, make_cyl, make_lathe,
                             make_tube, make_rot_box, export_glb)
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots, make_donut_display
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture, make_ceiling_speaker

ROOM_W = 4.0; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall": (0.78, 0.70, 0.58, 1.0), "baseboard": (0.42, 0.32, 0.22, 1.0)}
COL_FLOOR = (0.62, 0.52, 0.42, 1.0); COL_SEAM = (0.32, 0.22, 0.14, 1.0); COL_WOOD = (0.42, 0.30, 0.20, 1.0)
COL_ACCENT = (0.78, 0.42, 0.22, 1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})

# The desk sits AGAINST the north wall (2026-09-07: "a desk in the
# center of the room, not against a wall like desks normally are"),
# shifted west so it clears the service door at x 0.75..1.65. Every
# desk-anchored prop below is offset by DESK_DX / DESK_DY from its
# original authoring.
DESK_DX, DESK_DY = -0.35, 1.05


def build_desk():
    dx, dy = 0.0 + DESK_DX, ROOM_D-1.5 + DESK_DY
    # draft 4 (2026-09-18): a chamfered top on turned legs, an apron
    make_chamfer_box("Desk_Top", (dx, dy, 0.74), (1.80, 0.80, 0.04), COL_WOOD, chamfer=0.01)
    make_box("Desk_Apron_F", (dx, dy-0.36, 0.68), (1.66, 0.025, 0.08), (0.34, 0.24, 0.16, 1.0))
    for li in range(4):
        lx, ly = dx+(-0.84,+0.84,-0.84,+0.84)[li], dy+(-0.34,-0.34,+0.34,+0.34)[li]
        make_lathe(f"Desk_Leg_{li}", (lx, ly, 0.0),
                   [(0.025, 0.0), (0.035, 0.05), (0.022, 0.10), (0.03, 0.22), (0.038, 0.30), (0.026, 0.42), (0.026, 0.65), (0.034, 0.68), (0.034, 0.72)],
                   COL_WOOD, segments=8)
    # Papers stacked
    for pi in range(3):
        make_box(f"Papers_{pi}", (dx-0.30+pi*0.18, dy, 0.78+pi*0.02), (0.20, 0.26, 0.03), P.PAPER)
    # Monitor + keyboard
    make_lathe("Monitor_Foot", (dx, dy+0.20, 0.76), [(0.11, 0.0), (0.10, 0.01), (0.04, 0.02), (0.03, 0.025), (0.0, 0.025)], (0.14, 0.15, 0.17, 1.0), segments=10)
    make_box("Monitor_Neck", (dx, dy+0.20, 0.83), (0.05, 0.03, 0.12), (0.14, 0.15, 0.17, 1.0))
    make_chamfer_box("Monitor", (dx, dy+0.20, 1.05), (0.50, 0.04, 0.30), (0.06, 0.08, 0.10, 1.0), chamfer=0.008)
    make_box("Monitor_Screen", (dx, dy+0.178, 1.05), (0.46, 0.002, 0.26), (0.18, 0.22, 0.28, 1.0))
    make_box("Keyboard", (dx, dy-0.10, 0.76), (0.42, 0.16, 0.02), (0.32, 0.30, 0.32, 1.0))

def build_filing():
    for ci in range(2):
        cx = -ROOM_W/2.0+0.30+ci*0.50
        make_chamfer_box(f"Filing_{ci}", (cx, 1.0, 0.65), (0.50, 0.60, 1.30), (0.62, 0.62, 0.58, 1.0))
        for di in range(4):
            make_box(f"Filing_{ci}_Drawer_{di}", (cx, 0.70, 1.20-di*0.30), (0.46, 0.04, 0.26), (0.78, 0.78, 0.74, 1.0))
            make_box(f"Filing_{ci}_Pull_{di}", (cx, 0.675, 1.20-di*0.30), (0.10, 0.012, 0.025), (0.50, 0.50, 0.48, 1.0))
            make_box(f"Filing_{ci}_Label_{di}", (cx-0.14, 0.677, 1.26-di*0.30), (0.07, 0.006, 0.03), (0.92, 0.90, 0.84, 1.0))

def build_cal():
    make_calendar("Calendar", (+ROOM_W/2.0-0.05, ROOM_D/2.0, 1.70))

def build_bulb():
    # "lit by a single overhead with a pull chain" — the bulb is the
    # room's only light (fluorescents removed, hero-prop pass)
    # draft 4: the ceiling box, the cord, a socket, a bulb that is a bulb, the chain and its pull
    make_lathe("Bulb_Ceiling_Box", (0.0, ROOM_D/2.0, CEIL-0.03), [(0.05, 0.0), (0.05, 0.03), (0.0, 0.03)], P.METAL_BLACK, segments=8)
    make_tube("Bulb_Cord", [(0.0, ROOM_D/2.0, CEIL-0.03), (0.0, ROOM_D/2.0, CEIL-0.66)], 0.005, P.METAL_BLACK, segments=4)
    make_lathe("Bulb_Socket", (0.0, ROOM_D/2.0, CEIL-0.72), [(0.02, 0.0), (0.022, 0.04), (0.018, 0.06), (0.0, 0.06)], (0.36, 0.30, 0.22, 1.0), segments=8)
    make_lathe("Bulb_Glass", (0.0, ROOM_D/2.0, CEIL-0.93), [(0.0, 0.0), (0.04, 0.02), (0.06, 0.08), (0.055, 0.14), (0.03, 0.19), (0.02, 0.21), (0.0, 0.21)], (0.96, 0.86, 0.46, 1.0), segments=10)
    make_tube("Bulb_PullChain", [(0.03, ROOM_D/2.0, CEIL-0.70), (0.06, ROOM_D/2.0, CEIL-1.10)], 0.003, (0.70, 0.70, 0.68, 1.0), segments=4)
    make_lathe("Bulb_Pull", (0.06, ROOM_D/2.0, CEIL-1.14), [(0.0, 0.0), (0.012, 0.005), (0.012, 0.035), (0.0, 0.04)], (0.44, 0.34, 0.22, 1.0), segments=6)

def build_ceiling_infra():
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))
    make_hvac_vent("HVAC", (-ROOM_W/4.0, ROOM_D-0.5, CEIL), width=0.80, depth=0.40)



def build_backoffice_detail():
    """Scene-standard deep pass (2026-07-12). The comic-shop back
    room (43 instances, vol6) was walls + a desk + filing cabinets.
    Adds the working clutter of a comics back office: stacked
    cardboard long-boxes of back issues, a glowing light table for
    inking, an articulated desk lamp, a rolling office chair, a
    corkboard of pinned pages on the north wall, a coffee maker on
    the filing cabinets, taped wall shelving with trade spines, and
    desk clutter (art boards, mug, pen cup). Room interior x -1.9..
    1.9, y 0..4.9; desk top z 0.8 at y 3.5; filing top z 1.3 at
    y ~1.0. make_box/make_cyl only."""
    import math as _m
    card = (0.62, 0.48, 0.30, 1.0)
    card_dk = (0.48, 0.36, 0.22, 1.0)
    steel = (0.40, 0.42, 0.45, 1.0)
    # ── Long-box stacks of comics down the EAST wall ──
    for s_i, (bx, by, n) in enumerate([(1.55, 1.45, 3), (1.55, 2.3, 2), (1.6, 3.75, 3)]):
        for k in range(n):
            bz = 0.12 + k * 0.24
            skew = 0.03 * ((s_i + k) % 2)
            make_box(f"LongBox_{s_i}_{k}", (bx + skew, by, bz),
                     (0.5, 0.72, 0.22), card if (s_i + k) % 2 else card_dk)
            make_box(f"LongBox_{s_i}_{k}_Lid", (bx + skew, by, bz + 0.115),
                     (0.53, 0.75, 0.02), card_dk)
            # a few comic tops poking above the open box
            make_box(f"LongBox_{s_i}_{k}_Tops", (bx + skew, by - 0.1, bz + 0.14),
                     (0.42, 0.4, 0.05), (0.72, 0.36, 0.30, 1.0))
    # ── Light table (glowing inking surface) on the WEST wall ──
    ltx, lty = -1.5, 2.6
    make_box("LightTable_Top", (ltx, lty, 0.78), (0.55, 0.8, 0.05), (0.30, 0.32, 0.36, 1.0))
    make_box("LightTable_Glass", (ltx, lty, 0.81), (0.48, 0.72, 0.02), (0.92, 0.94, 0.86, 1.0))
    make_box("LightTable_Page", (ltx + 0.05, lty + 0.05, 0.825),
             (0.30, 0.40, 0.004), (0.96, 0.95, 0.92, 1.0))
    for sgn in (-1, +1):
        make_box(f"LightTable_Leg_{sgn:+d}", (ltx + sgn * 0.22, lty, 0.38),
                 (0.05, 0.7, 0.76), steel)
    # ── Articulated desk lamp on the desk (base+arm+arm+head) ──
    lx, ly = -0.65 + DESK_DX, 3.75 + DESK_DY
    make_cyl("DeskLamp_Base", (lx, ly, 0.82), 0.07, 0.03, (0.18, 0.20, 0.24, 1.0), segments=8)
    make_cyl("DeskLamp_Arm1", (lx + 0.06, ly, 0.98), 0.014, 0.34, (0.24, 0.26, 0.30, 1.0), segments=5)
    make_cyl("DeskLamp_Arm2", (lx + 0.20, ly, 1.14), 0.014, 0.30, (0.24, 0.26, 0.30, 1.0), segments=5, axis='X')
    make_cyl("DeskLamp_Head", (lx + 0.33, ly, 1.10), 0.06, 0.10, (0.20, 0.22, 0.26, 1.0), segments=8)
    make_cyl("DeskLamp_Bulb", (lx + 0.35, ly, 1.06), 0.03, 0.03, (0.98, 0.92, 0.72, 1.0), segments=6)
    # ── Rolling office chair south of the desk ──
    # The chair faces the desk: its BACK is on the far side from the
    # desk (2026-09-07: it shipped with the back between seat and
    # desk, "facing the wrong direction away from the desk", and the
    # back floated 2 cm above the seat — "exploded"). Two posts now
    # carry the back off the seat.
    ch_x, ch_y = 0.0 + DESK_DX, 2.7 + DESK_DY
    make_cyl("Chair_Column", (ch_x, ch_y, 0.28), 0.03, 0.42, (0.12, 0.12, 0.14, 1.0), segments=6)
    make_lathe("Chair_Seat", (ch_x, ch_y, 0.46), [(0.10, 0.0), (0.22, 0.01), (0.24, 0.04), (0.235, 0.07), (0.20, 0.08), (0.0, 0.08)], (0.16, 0.16, 0.18, 1.0), segments=12)
    make_box("Chair_Back", (ch_x, ch_y - 0.22, 0.80), (0.42, 0.05, 0.40), (0.16, 0.16, 0.18, 1.0))
    for sgn in (-1, +1):
        make_box(f"Chair_BackPost_{sgn:+d}", (ch_x + sgn * 0.15, ch_y - 0.21, 0.585), (0.025, 0.03, 0.17), (0.12, 0.12, 0.14, 1.0))
    for k in range(5):
        a = k * (2 * _m.pi / 5)
        make_box(f"Chair_Star_{k}",
                 (ch_x + _m.cos(a) * 0.14, ch_y + _m.sin(a) * 0.14, 0.06),
                 (0.10, 0.10, 0.05), (0.10, 0.10, 0.12, 1.0))
        make_cyl(f"Chair_Caster_{k}",
                 (ch_x + _m.cos(a) * 0.26, ch_y + _m.sin(a) * 0.26, 0.04),
                 0.035, 0.05, (0.06, 0.06, 0.07, 1.0), segments=6, axis='X')
    # ── Corkboard of pinned pages on the NORTH wall ──
    make_box("Corkboard", (0.0, 4.82, 1.6), (1.4, 0.03, 0.9), (0.56, 0.42, 0.26, 1.0))
    make_box("Corkboard_Frame", (0.0, 4.80, 1.6), (1.48, 0.02, 0.98), (0.30, 0.22, 0.14, 1.0))
    for i, (px, pz, col) in enumerate([(-0.45, 1.8, (0.94, 0.92, 0.86)), (0.1, 1.9, (0.72, 0.78, 0.86)),
                                       (0.5, 1.7, (0.94, 0.92, 0.86)), (-0.2, 1.4, (0.90, 0.82, 0.72)),
                                       (0.4, 1.35, (0.94, 0.92, 0.86))]):
        make_box(f"Cork_Page_{i}", (px, 4.79, pz), (0.24, 0.01, 0.30), (*col, 1.0))
        make_cyl(f"Cork_Pin_{i}", (px, 4.77, pz + 0.12), 0.012, 0.02,
                 [(0.8,0.2,0.2,1),(0.2,0.4,0.8,1),(0.9,0.8,0.2,1)][i%3], segments=5, axis='Y')
    # ── Coffee maker on the filing cabinets (top z 1.3) ──
    cmx, cmy = -1.2, 1.0
    make_chamfer_box("CoffeeMaker_Body", (cmx, cmy, 1.48), (0.22, 0.28, 0.34), (0.16, 0.16, 0.18, 1.0))
    make_lathe("CoffeeMaker_Carafe", (cmx, cmy - 0.02, 1.34), [(0.05, 0.0), (0.07, 0.02), (0.072, 0.09), (0.05, 0.13), (0.04, 0.14)], (0.40, 0.28, 0.20, 0.9), segments=10)
    make_cyl("CoffeeMaker_Coffee", (cmx, cmy - 0.02, 1.36), 0.06, 0.03, (0.20, 0.12, 0.08, 1.0), segments=10)
    make_box("CoffeeMaker_Warmer", (cmx, cmy - 0.02, 1.33), (0.18, 0.20, 0.02), (0.10, 0.10, 0.11, 1.0))
    # ── Taped wall shelf with trade spines (west wall over table) ──
    make_box("WallShelf_Plank", (-1.82, 2.6, 1.7), (0.22, 1.2, 0.03), (0.44, 0.34, 0.24, 1.0))
    for i in range(9):
        sy = 2.05 + i * 0.13
        h = 0.24 + 0.03 * (i % 3)
        make_box(f"WallShelf_Book_{i}", (-1.82, sy, 1.72 + (h - 0.24) / 2),
                 (0.18, 0.11, h),
                 [(0.66,0.24,0.22,1),(0.24,0.42,0.52,1),(0.72,0.60,0.28,1),
                  (0.32,0.46,0.34,1)][i % 4])
    # ── Desk clutter: art boards + mug + pen cup ──
    make_box("Desk_ArtBoard_0", (0.35 + DESK_DX, 3.5 + DESK_DY, 0.815), (0.34, 0.44, 0.006), (0.94, 0.93, 0.88, 1.0))
    make_box("Desk_ArtBoard_1", (0.42 + DESK_DX, 3.55 + DESK_DY, 0.822), (0.34, 0.44, 0.006), (0.90, 0.90, 0.84, 1.0))
    make_cyl("Desk_Mug", (0.7 + DESK_DX, 3.2 + DESK_DY, 0.86), 0.04, 0.10, (0.30, 0.44, 0.52, 1.0), segments=8)
    make_cyl("Desk_PenCup", (-0.75 + DESK_DX, 3.3 + DESK_DY, 0.87), 0.045, 0.11, (0.20, 0.20, 0.24, 1.0), segments=8)
    for k in range(4):
        make_cyl(f"Desk_Pen_{k}", (-0.75 + (k - 1.5) * 0.012 + DESK_DX, 3.3 + DESK_DY, 0.95), 0.006, 0.14,
                 [(0.1,0.1,0.1,1),(0.2,0.3,0.7,1),(0.7,0.2,0.2,1),(0.1,0.5,0.3,1)][k], segments=4)


def build_hero_props():
    """2026-08-03 hero-prop pass — the props the vol6 office scenes
    revolve around."""
    iron = (0.20, 0.19, 0.20, 1.0)
    # THE SPEAK & SPELL — 1978 original, battered, cracked lower-left
    # corner, on the shelf above the file cabinet. Grille is its own
    # emissive object so the red glow can read (dim ch12, red ch21).
    make_box("SpeakSpell_Shelf", (-1.45, 1.0, 1.62), (0.60, 0.30, 0.035), (0.44, 0.32, 0.20, 1.0))
    make_chamfer_box("SpeakSpell_Body", (-1.45, 1.0, 1.665), (0.26, 0.20, 0.05), (0.72, 0.16, 0.14, 1.0))
    make_box("SpeakSpell_Keys", (-1.48, 0.96, 1.695), (0.16, 0.10, 0.01), (0.92, 0.88, 0.72, 1.0))
    make_box("SpeakSpell_Grille", (-1.36, 1.05, 1.695), (0.06, 0.06, 0.012), (0.94, 0.42, 0.30, 1.0))
    make_box("SpeakSpell_Crack", (-1.57, 0.92, 1.66), (0.03, 0.03, 0.045), (0.44, 0.10, 0.09, 1.0))
    # One-way mirror to the sales floor (installed 1983)
    make_box("OneWay_Mirror_Frame", (1.4, 0.10, 1.70), (1.20, 0.04, 0.95), (0.30, 0.26, 0.22, 1.0))
    make_box("OneWay_Mirror", (1.4, 0.08, 1.70), (1.10, 0.02, 0.85), (0.46, 0.52, 0.56, 1.0))
    # Desk drawer pedestal (top drawer takes the slip; green folder
    # in the second)
    make_chamfer_box("Desk_Pedestal", (0.62 + DESK_DX, 3.5 + DESK_DY, 0.38), (0.52, 0.72, 0.70), (0.40, 0.30, 0.20, 1.0))
    for di in range(3):
        make_box(f"Desk_Drawer_{di}", (0.62 + DESK_DX, 3.13 + DESK_DY, 0.62 - di * 0.21), (0.44, 0.02, 0.16), (0.34, 0.24, 0.16, 1.0))
        make_box(f"Desk_Drawer_{di}_Pull", (0.62 + DESK_DX, 3.11 + DESK_DY, 0.62 - di * 0.21), (0.12, 0.015, 0.03), iron)
    # Desk phone (Rick's long calls)
    make_box("Desk_Phone", (0.55 + DESK_DX, 3.72 + DESK_DY, 0.82), (0.22, 0.16, 0.08), (0.16, 0.16, 0.18, 1.0))
    make_box("Desk_Phone_Handset", (0.55 + DESK_DX, 3.72 + DESK_DY, 0.90), (0.20, 0.06, 0.04), (0.12, 0.12, 0.14, 1.0))
    # Overturned milk crate — Sam's seat, opposite the desk
    make_chamfer_box("Milk_Crate", (-0.20 + DESK_DX, 2.40 + DESK_DY, 0.16), (0.36, 0.36, 0.32), (0.62, 0.28, 0.24, 1.0))
    make_box("Milk_Crate_Rim", (-0.20 + DESK_DX, 2.40 + DESK_DY, 0.315), (0.38, 0.38, 0.03), (0.52, 0.22, 0.20, 1.0))
    # Mini-fridge + floor safe (one of the six keys)
    make_chamfer_box("Mini_Fridge", (1.65, 0.75, 0.42), (0.55, 0.55, 0.84), (0.82, 0.80, 0.76, 1.0))
    make_box("Mini_Fridge_Handle", (1.38, 0.55, 0.55), (0.03, 0.03, 0.30), iron)
    make_chamfer_box("Office_Safe", (1.62, 4.4, 0.28), (0.50, 0.50, 0.56), (0.24, 0.25, 0.28, 1.0))
    make_cyl("Safe_Dial", (1.62, 4.14, 0.32), 0.06, 0.03, (0.60, 0.62, 0.64, 1.0), axis='Y', segments=10)
    # The office door + the slide bolt Sam did not realize was there
    make_box("Office_Door", (0.0, 0.05, 1.03), (1.90, 0.05, 2.05), (0.40, 0.30, 0.20, 1.0))
    make_box("Office_Bolt_Plate", (0.85, 0.02, 1.20), (0.16, 0.02, 0.05), iron)
    make_box("Office_Bolt_Barrel", (0.78, 0.015, 1.20), (0.10, 0.025, 0.03), (0.60, 0.62, 0.64, 1.0))
    # Service/back door in the N wall, with its deadbolt
    make_box("Service_Door", (1.2, ROOM_D-0.05, 1.03), (0.90, 0.05, 2.05), (0.34, 0.30, 0.28, 1.0))
    make_box("Service_Deadbolt", (1.55, ROOM_D-0.09, 1.05), (0.06, 0.03, 0.10), (0.74, 0.60, 0.30, 1.0))


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    Three cues; the Speak & Spell on its shelf exists (marker
    only). Built: RICK'S NOTEBOOK ("the spiral notebook he had been
    keeping for her since Sunday. The notebook is open.") — open on
    the desk, its note page showing (the page carries the "note"
    cue: the list on its standard page).
    """
    make_box("Ricks_Notebook", (-0.25 + DESK_DX, 3.35 + DESK_DY, 0.766), (0.18, 0.24, 0.012), (0.30, 0.44, 0.58, 1.0))
    make_box("Ricks_Notebook_Wire", (-0.25 + DESK_DX, 3.476 + DESK_DY, 0.767), (0.18, 0.010, 0.014), (0.55, 0.56, 0.58, 1.0))
    make_box("Notebook_Note_Page", (-0.25 + DESK_DX, 3.34 + DESK_DY, 0.7735), (0.16, 0.21, 0.003), (0.94, 0.93, 0.88, 1.0))
    make_box("Note_Page_List_Lines", (-0.25 + DESK_DX, 3.36 + DESK_DY, 0.7755), (0.10, 0.12, 0.001), (0.36, 0.36, 0.40, 1.0))
    # ── 2026-09-03 · vol6 ch3_coda (re-homed off the street): "a small
    # folder in front of him. The folder contains three things." The
    # hand-drawn map with a single building circled in red ink; the 1974
    # Polaroid of Thomas in front of the Graustark storefront; F.T.'s
    # note, which goes back in its envelope, which goes in "the small
    # fireproof box under the desk — the one the store was sold with
    # in 1984". Open on the desk edge in front of the chair.
    make_box("Folder", (0.0 + DESK_DX, 3.21 + DESK_DY, 0.763), (0.30, 0.18, 0.006), (0.62, 0.56, 0.42, 1.0))
    make_box("Folder_Tab", (0.13 + DESK_DX, 3.305 + DESK_DY, 0.7635), (0.06, 0.012, 0.005), (0.58, 0.52, 0.38, 1.0))
    make_box("Map", (-0.02 + DESK_DX, 3.21 + DESK_DY, 0.767), (0.20, 0.14, 0.002), (0.94, 0.92, 0.84, 1.0))
    for mi, (mx, my, mw, md) in enumerate(((-0.09, 3.21, 0.004, 0.11), (-0.04, 3.24, 0.09, 0.003),
                                           (0.01, 3.19, 0.004, 0.09), (0.03, 3.16, 0.10, 0.003))):
        make_box(f"Map_Street_{mi}", (mx + DESK_DX, my + DESK_DY, 0.7685), (mw, md, 0.001), (0.30, 0.30, 0.34, 1.0))
    make_cyl("Map_Red_Circle", (0.045 + DESK_DX, 3.235 + DESK_DY, 0.7685), 0.016, 0.001, (0.82, 0.14, 0.10, 1.0), segments=12)
    make_box("Polaroid", (0.06 + DESK_DX, 3.17 + DESK_DY, 0.769), (0.088, 0.107, 0.002), (0.96, 0.95, 0.92, 1.0))
    make_box("Polaroid_Image", (0.06 + DESK_DX, 3.178 + DESK_DY, 0.7705), (0.076, 0.076, 0.001), (0.52, 0.48, 0.40, 1.0))
    make_box("Polaroid_Figure", (0.058 + DESK_DX, 3.170 + DESK_DY, 0.7715), (0.016, 0.040, 0.0005), (0.30, 0.34, 0.46, 1.0))
    make_box("Envelope", (-0.06 + DESK_DX, 3.265 + DESK_DY, 0.769), (0.16, 0.09, 0.003), (0.90, 0.86, 0.76, 1.0))
    make_box("Envelope_Flap_Line", (-0.06 + DESK_DX, 3.28 + DESK_DY, 0.7708), (0.14, 0.001, 0.0005), (0.60, 0.54, 0.44, 1.0))
    make_box("Fireproof_Box", (-0.45 + DESK_DX, 3.55 + DESK_DY, 0.12), (0.36, 0.28, 0.24), (0.28, 0.28, 0.30, 1.0))
    make_box("Fireproof_Box_Lid_Seam", (-0.45 + DESK_DX, 3.409 + DESK_DY, 0.19), (0.34, 0.002, 0.004), (0.14, 0.14, 0.15, 1.0))
    make_box("Fireproof_Box_Latch", (-0.45 + DESK_DX, 3.405 + DESK_DY, 0.14), (0.05, 0.008, 0.06), (0.64, 0.62, 0.56, 1.0))
    make_box("Fireproof_Box_Handle", (-0.45 + DESK_DX, 3.55 + DESK_DY, 0.255), (0.14, 0.02, 0.03), (0.20, 0.20, 0.22, 1.0))


def build_draft4_2026_09():
    """DRAFT 4 (2026-09-18, lore/_VISUAL_PROGRAM.md §3; the office carries
    11 placements). The room's prose says one bulb on a pull chain; the
    scene has shipped two fluorescent practicals over it since the rig
    pass — they go. WEAR: the path from the office door to the chair and
    the spur to the coffee maker; the oval the casters have worn in
    front of the desk; the forearm patch at Rick's place; coffee rings
    on the filing cabinet's top; ink on the light table's edge; the
    corkboard's old pin holes. D3: a power strip under the desk on the
    wall side (monitor, lamp) and its cord to the outlet; the coffee
    maker, the mini fridge and the light table plugged into theirs.
    """
    from _props.detail import make_traffic_wear, make_floor_stain, make_scuff_band, make_wall_outlet, make_cord_run
    floor_dk = (0.50, 0.41, 0.32, 1.0)
    dx, dy = 0.0 + DESK_DX, ROOM_D-1.5 + DESK_DY
    ch_x, ch_y = 0.0 + DESK_DX, 2.7 + DESK_DY
    # ── WEAR ──
    make_traffic_wear("Wear_Path_Entry_A", [(0.0, 0.5), (-0.2, 1.6), (-0.35, 2.9), (ch_x, ch_y - 0.45)], width=0.45, tint=floor_dk)
    make_traffic_wear("Wear_Path_Entry_B", [(-0.2, 0.9), (-0.9, 1.15), (-1.15, 1.4)], width=0.34, tint=floor_dk)
    make_floor_stain("Wear_Caster_Oval", (ch_x, ch_y + 0.05), radius=0.42, tint=(0.46, 0.38, 0.30, 1.0), segments=12)
    make_box("Wear_Forearm", (dx + 0.10, dy - 0.32, 0.762), (0.42, 0.10, 0.004), (0.52, 0.40, 0.28, 1.0))
    for ri, (rx, ry) in enumerate(((-1.72, 0.85), (-1.62, 1.18), (-1.15, 1.22))):
        make_cyl(f"Wear_Ring_W_{ri}", (rx, ry, 1.303), 0.04, 0.003, (0.42, 0.30, 0.20, 1.0), segments=10)
    make_box("Wear_Ink_Spot", (-1.5 + 0.20, 2.6 - 0.30, 0.822), (0.08, 0.05, 0.002), (0.12, 0.12, 0.16, 1.0))
    for hi, (hx, hz) in enumerate(((-0.62, 1.95), (-0.55, 1.35), (0.25, 1.98), (0.62, 1.30), (0.05, 1.25))):
        make_cyl(f"Wear_PinHole_{hi}", (hx, 4.79, hz), 0.004, 0.006, (0.30, 0.22, 0.14, 1.0), axis='Y', segments=4)
    make_scuff_band("Wear_Kick_E", (1.55, 1.45), 0.7, axis='Y', height=0.05, band_z=0.02, tint=(0.38, 0.30, 0.22, 1.0))
    # ── D3 ──
    make_box("Power_Strip", (dx - 0.20, dy + 0.30, 0.03), (0.30, 0.06, 0.04), (0.86, 0.86, 0.82, 1.0))
    for si in range(4):
        make_box(f"Power_Strip_Socket_{si}", (dx - 0.31 + si * 0.07, dy + 0.30, 0.052), (0.03, 0.03, 0.004), (0.30, 0.30, 0.30, 1.0))
    make_wall_outlet("Outlet_N_1", (dx - 0.20, ROOM_D), axis='X', face_sign=-1, z=0.30, aged=True)
    make_cord_run("Cord_1", (dx - 0.20, dy + 0.33, 0.03), (dx - 0.20, ROOM_D - 0.12, 0.30), sag=0.0)
    make_cord_run("Cord_2", (dx, dy + 0.22, 0.78), (dx - 0.20, dy + 0.30, 0.05), sag=0.05)
    make_cord_run("Cord_3", (-0.65 + DESK_DX + 0.05, 3.75 + DESK_DY + 0.03, 0.80), (dx - 0.27, dy + 0.30, 0.05), sag=0.05)
    make_wall_outlet("Outlet_W_1", (-ROOM_W/2.0, 0.85), axis='Y', face_sign=1, z=1.45, aged=True)
    make_cord_run("Cord_4", (-1.31, 1.0, 1.36), (-ROOM_W/2.0 + 0.13, 0.85, 1.45), sag=0.03)
    make_wall_outlet("Outlet_W_2", (-ROOM_W/2.0, 2.95), axis='Y', face_sign=1, z=0.30, aged=True)
    make_cord_run("Cord_5", (-1.75, 2.9, 0.74), (-ROOM_W/2.0 + 0.13, 2.95, 0.30), sag=0.02)
    make_wall_outlet("Outlet_E_1", (ROOM_W/2.0, 1.10), axis='Y', face_sign=-1, z=0.30, aged=True)
    make_cord_run("Cord_6", (1.92, 0.95, 0.10), (ROOM_W/2.0 - 0.13, 1.10, 0.30), sag=0.0)


def main():
    clear_scene()
    build_shell()
    build_desk()
    build_filing()
    build_cal()
    build_bulb()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/cosmic_comics_back_office.glb"))
    print(f"\n[build_cosmic_comics_back_office] exporting to {out}")
    build_backoffice_detail()
    build_hero_props()
    build_hero_props_2026_09()
    build_draft4_2026_09()
    export_glb(out)

if __name__ == "__main__":
    main()
