"""Sam's Bedroom — vol5-7 — Sam (the kid protagonist; into Cosmic Comics
and video games). Boyish BLUE/GREEN palette and a distinct prop set:
a captain's bed with storage drawers, comic/movie posters, a shelf of
comic longboxes + action figures, a CRT/TV + game console, a desk with
sketches + a lamp, a beanbag, and model kits — so it reads as a
comics-and-games kid's room, not a reskin of Maya's.

DRAFT 4 (2026-09-18, lore/_VISUAL_PROGRAM.md §3): turned desk legs and
an apron, the clip lamp with a neck and a bulb, the kit chair facing
the desk, one sat-in beanbag, the skateboard leaning on trucks and
wheels, dresser pulls, the bedside lamp as base + shade profiles, the
fan's pull chain; first WEAR (paths, the chair's patch, the forearm,
the bed's kick, stickers and a peeled one on his door); D3 switch,
power strip, five cords; D5 the backyard through the north window.

DRAFT 5 targets: the action figures as figures (a pose each); the
longboxes with lids; the CRT's bezel and a screen glow practical when
the console is on; the curtains hung from rings; the laundry as
clothes, not discs; Deck: the sheet's establish and `insert notebook`.
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
from _props.food_service import make_coffee_pots
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture
from _props.furniture import make_bed, make_chair

ROOM_W = 4.0; ROOM_D = 5.0; CEIL = 2.6
# Denim-blue walls, lime-green accent — boyish, distinct from the girls'/others'.
PAL_WALL = {"wall":(0.56,0.66,0.78,1.0),"baseboard":(0.32,0.40,0.50,1.0)}
COL_FLOOR = (0.60,0.60,0.62,1.0); COL_SEAM = (0.38,0.38,0.42,1.0); COL_WOOD = (0.40,0.46,0.40,1.0)
COL_ACCENT = (0.44,0.66,0.36,1.0)        # lime green
COL_BLUE = (0.24,0.42,0.66,1.0)          # cosmic blue bedding
COL_BLUE_DK = (0.16,0.28,0.46,1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
                 with_grid=False, with_stains=False,
                 palette={"tile": (0.90, 0.90, 0.86, 1.0)})

def build_bed():
    # Captain's bed: raised frame with a row of storage drawers underneath.
    bx, by = -ROOM_W/4.0, ROOM_D - 0.15 - 0.92   # head to the N wall (2026-09-10: mid-room)
    # the shared captain's bed: drawers on the +X side, cosmic-blue
    # blanket made up (2026-09-07: the stripe sat inside the comforter)
    make_bed("Bed", bx, by, head="+Y", w=1.24, d=1.84, style="captain",
             frame_col=COL_WOOD, mattress_col=(0.90, 0.90, 0.86, 1.0),
             blanket_col=COL_BLUE, pillow_col=(0.92, 0.92, 0.86, 1.0), pillows=2, made=True, headboard=True)

def build_desk_lamp():
    dx, dy = +ROOM_W/4.0, ROOM_D - 0.45   # 13 cm off the N wall (2026-09-07: it stood mid-room)
    # draft 4 (2026-09-18): chamfered top, apron, turned legs; the clip
    # lamp a weighted base, a column, a bent neck, a cone head
    make_chamfer_box("Desk_Top", (dx, dy, 0.74), (1.00, 0.60, 0.04), COL_WOOD, chamfer=0.01)
    make_box("Desk_Apron_F", (dx, dy-0.27, 0.68), (0.88, 0.02, 0.08), (0.32, 0.38, 0.32, 1.0))
    for i, (lx, ly) in enumerate([(-0.44, -0.26), (0.44, -0.26), (-0.44, 0.26), (0.44, 0.26)]):
        make_lathe(f"Desk_Leg_{i}", (dx+lx, dy+ly, 0.0), [(0.025, 0.0), (0.032, 0.05), (0.022, 0.10), (0.028, 0.30), (0.034, 0.40), (0.024, 0.55), (0.024, 0.68), (0.03, 0.72)], COL_WOOD, segments=8)
    make_lathe("Lamp_Base", (dx-0.34, dy+0.18, 0.76), [(0.07, 0.0), (0.065, 0.02), (0.03, 0.035), (0.02, 0.04), (0.0, 0.04)], P.METAL_BLACK, segments=10)
    make_cyl("Lamp_Col", (dx-0.34, dy+0.18, 0.98), 0.014, 0.36, P.METAL_BLACK, segments=6)
    make_tube("Lamp_Neck", [(dx-0.34, dy+0.18, 1.16), (dx-0.30, dy+0.19, 1.20), (dx-0.25, dy+0.20, 1.18)], 0.008, P.METAL_BLACK, segments=5)
    make_lathe("Lamp_Head", (dx-0.24, dy+0.20, 1.11), [(0.0, 0.0), (0.03, 0.0), (0.065, 0.10), (0.06, 0.11), (0.0, 0.11)], COL_ACCENT, segments=10)
    make_lathe("Lamp_Bulb", (dx-0.24, dy+0.20, 1.12), [(0.0, 0.0), (0.02, 0.005), (0.024, 0.03), (0.0, 0.05)], (0.98, 0.94, 0.80, 1.0), segments=8)
    # Chunky CRT monitor + keyboard
    make_chamfer_box("Monitor_Body", (dx+0.10, dy+0.14, 0.98), (0.42, 0.40, 0.38), (0.24, 0.24, 0.26, 1.0))
    make_box("Monitor_Screen", (dx+0.10, dy-0.06, 0.98), (0.34, 0.02, 0.28), (0.30, 0.52, 0.70, 1.0))
    make_box("Keyboard", (dx+0.10, dy-0.20, 0.77), (0.40, 0.16, 0.03), (0.32, 0.32, 0.34, 1.0))
    # Game console + controller
    make_chamfer_box("Console", (dx-0.30, dy-0.16, 0.79), (0.26, 0.20, 0.06), P.METAL_BLACK)
    make_box("Controller", (dx+0.02, dy-0.22, 0.77), (0.14, 0.09, 0.03), COL_ACCENT)
    # Comic sketches / drawing pad + pencils spread on the desk
    make_box("SketchPad", (dx-0.20, dy+0.12, 0.765), (0.30, 0.40, 0.01), P.PAPER)
    for si in range(3):
        make_box(f"Sketch_{si}", (dx-0.28+si*0.10, dy+0.24, 0.767), (0.20, 0.26, 0.004), (0.92, 0.90, 0.84, 1.0))
    make_cyl("Pencil", (dx-0.05, dy+0.06, 0.762), 0.01, 0.18, (0.86, 0.72, 0.28, 1.0), axis='Y', segments=6)
    # Desk chair
    make_chair("Chair", dx+0.22, dy-0.66, yaw=0.55, wood=COL_WOOD, seat_col=COL_BLUE, w=0.42)   # draft 4: the kit chair, facing the desk

def build_posters():
    # Comic / movie posters along the west wall
    for pi in range(3):
        px = -ROOM_W/2.0+0.05; py = 1.0 + pi*1.5
        make_faded_poster(f"Poster_W_{pi}", (px, py, 1.55))

def build_rug():
    make_cyl("Rug", (0.0, ROOM_D/2.0, 0.012), 1.20, 0.005, COL_BLUE_DK)

def build_win():
    make_window("Window_N", (0.0, ROOM_D-0.02, 1.50), width=1.20, height=1.00)

def build_ceiling_infra():
    # THE CEILING FAN — clicks on the third, sixth, ninth rotation.
    # The most-repeated object in Sam's room; the fluorescents that
    # occupied its centreline are gone.
    make_cyl("Fan_Downrod", (0.0, 2.5, CEIL-0.10), 0.02, 0.20, P.METAL_BLACK, segments=6)
    make_cyl("Fan_Hub", (0.0, 2.5, CEIL-0.24), 0.11, 0.10, P.METAL_BLACK, segments=10)
    make_tube("Fan_Pull_Chain", [(0.05, 2.5, CEIL-0.29), (0.06, 2.5, CEIL-0.56)], 0.003, (0.70, 0.70, 0.68, 1.0), segments=4)
    import math as _m
    for bi in range(5):
        ang = bi * (2.0 * _m.pi / 5.0)
        make_box(f"Fan_Blade_{bi}", (0.45 * _m.cos(ang), 2.5 + 0.45 * _m.sin(ang), CEIL-0.26),
                 (0.62 if abs(_m.cos(ang)) > 0.5 else 0.18,
                  0.18 if abs(_m.cos(ang)) > 0.5 else 0.62, 0.02),
                 (0.44, 0.32, 0.22, 1.0))
    make_smoke_detector("Smoke", (0.9, ROOM_D/2.0, CEIL))


def build_dressing():
    """Comics-and-games clutter: a nightstand + clock, a shelf of comic
    longboxes + action figures, a stack of model kits, a beanbag, a
    skateboard, and a laundry pile. make_floor_plant is imported but this
    kid keeps no plants — wired here as a single small windowsill sprout."""
    bx, by = -ROOM_W/4.0, ROOM_D - 0.15 - 0.92   # head to the N wall (2026-09-10: mid-room)
    TINTS = P.SNACK_TINTS
    nsx = bx + 0.95
    make_chamfer_box("Nightstand", (nsx, by+0.7, 0.28), (0.40, 0.40, 0.56), COL_WOOD)
    make_box("Clock", (nsx, by+0.7, 0.62), (0.16, 0.10, 0.10), P.METAL_BLACK)
    # Shelf on the east wall: comic longboxes on the bottom, figures on top
    shx = ROOM_W/2.0 - 0.18
    # (2026-09-09: was one solid block with the longboxes and figures
    # INSIDE it — now back, sides, top and three boards)
    make_box("Shelf_Back", (shx + 0.16, ROOM_D-1.4, 0.80), (0.02, 1.20, 1.60), COL_WOOD)
    for sy_ in (-1, 1):
        make_box(f"Shelf_Side_{sy_:+d}", (shx, ROOM_D-1.4 + sy_ * 0.59, 0.80), (0.34, 0.02, 1.60), COL_WOOD)
    make_box("Shelf_Top", (shx, ROOM_D-1.4, 1.59), (0.34, 1.20, 0.02), COL_WOOD)
    for bz_ in (0.23, 0.64, 1.06):
        make_box(f"Shelf_Board_{bz_:.2f}", (shx, ROOM_D-1.4, bz_), (0.32, 1.16, 0.02), COL_WOOD)
    # comic longboxes (long white boxes) on the lowest shelf
    for c in range(3):
        make_box(f"Longbox_{c}", (shx-0.02, ROOM_D-1.9+c*0.36, 0.34), (0.28, 0.32, 0.20), (0.88, 0.86, 0.80, 1.0))
    # action figures / statues on the middle + upper shelves
    for r in range(2):
        for c in range(4):
            fc = TINTS[(r*4+c) % len(TINTS)]
            make_cyl(f"Figure_{r}_{c}", (shx-0.04, ROOM_D-1.85+c*0.30, 0.78+r*0.42), 0.06, 0.26, fc, segments=8)
            make_cyl(f"FigureHead_{r}_{c}", (shx-0.04, ROOM_D-1.85+c*0.30, 0.95+r*0.42), 0.05, 0.10, (0.86, 0.70, 0.54, 1.0), segments=8)
    # Stack of model kit boxes in the SE corner
    for mi in range(3):
        make_box(f"ModelKit_{mi}", (ROOM_W/2.0-0.4, 0.7, 0.12+mi*0.16), (0.42-mi*0.04, 0.30, 0.14), TINTS[(mi*2) % len(TINTS)])
    # Beanbag chair (squashed stack of discs)
    make_lathe("Beanbag", (0.3, 1.1, 0.0), [(0.36, 0.0), (0.44, 0.06), (0.45, 0.16), (0.40, 0.26), (0.30, 0.34), (0.14, 0.40), (0.0, 0.41)], COL_ACCENT, segments=14)   # draft 4: one sat-in shape
    make_lathe("Beanbag_Dent", (0.34, 1.06, 0.36), [(0.16, 0.0), (0.12, 0.02), (0.0, 0.03)], (0.38, 0.58, 0.32, 1.0), segments=12)
    # Skateboard leaning against the south wall
    # draft 4: the deck leans on the wall (tail on the floor), trucks and wheels on the room side
    make_rot_box("Skateboard", (0.9, 0.21, 0.40), (0.20, 0.02, 0.80), COL_BLUE, pitch=0.28)
    for wi, (wy, wz) in enumerate(((0.26, 0.16), (0.33, 0.66))):
        make_box(f"Skate_Truck_{wi}", (0.9, wy, wz), (0.16, 0.05, 0.025), P.METAL_STEEL)
        for sgn in (-1, 1):
            make_cyl(f"Skate_Wheel_{wi}_{sgn:+d}", (0.9 + sgn * 0.09, wy + 0.03, wz), 0.025, 0.02, (0.86, 0.82, 0.30, 1.0), axis='X', segments=8)
    # Laundry pile in the corner
    for li, (lc, lz) in enumerate([((0.30, 0.44, 0.62, 1.0), 0.06), ((0.46, 0.60, 0.36, 1.0), 0.14), ((0.24, 0.36, 0.52, 1.0), 0.20)]):
        make_cyl(f"Laundry_{li}", (-ROOM_W/2.0+0.5, 0.6, lz), 0.24-li*0.04, 0.10, lc, segments=10)
    # Single small sprout on the windowsill (wires the imported helper)
    make_floor_plant("Sill_Sprout", (0.5, ROOM_D-0.4, 0.0), palette={"leaf": (0.40, 0.58, 0.34, 1.0), "pot": (0.30, 0.42, 0.30, 1.0)})

def build_hero_props():
    """2026-08-03 hero-prop pass: box spring (the notebook's hiding
    place), the 99-cent spiral notebook at the mattress seam,
    curtains, dresser + phone, closet doors, bedside lamp."""
    # Box spring under the mattress — "She slides it between the
    # mattress and the box spring."
    make_chamfer_box("Bed_BoxSpring", (-1.0, 2.5, 0.50), (1.12, 1.72, 0.14), (0.86, 0.84, 0.78, 1.0))
    make_box("Sams_Notebook", (-0.55, 2.10, 0.58), (0.16, 0.22, 0.012), (0.72, 0.62, 0.30, 1.0))
    # Curtains on the N window
    make_cyl("Curtain_Rod", (0.0, 4.88, 2.14), 0.015, 1.60, (0.20, 0.19, 0.20, 1.0), axis='X', segments=6)
    for cx in (-0.72, 0.72):
        make_box(f"Curtain_{cx:+.2f}", (cx, 4.88, 1.50), (0.44, 0.04, 1.20), (0.55, 0.60, 0.70, 1.0))
    # Dresser with the phone on it ("Sam's phone, on her dresser,
    # buzzes")
    make_chamfer_box("Dresser", (1.62, 2.45, 0.42), (0.50, 1.00, 0.84), (0.46, 0.34, 0.22, 1.0))
    for di in range(3):
        make_box(f"Dresser_Drawer_{di}", (1.36, 2.45, 0.20 + di * 0.26), (0.02, 0.86, 0.20), (0.38, 0.28, 0.18, 1.0))
        make_lathe(f"Dresser_Pull_{di}", (1.35, 2.45, 0.19 + di * 0.26), [(0.0, 0.0), (0.012, 0.0), (0.014, 0.01), (0.008, 0.02), (0.0, 0.02)], (0.60, 0.56, 0.42, 1.0), segments=8)
    make_box("Sams_Phone", (1.62, 2.0, 0.855), (0.08, 0.15, 0.012), (0.12, 0.12, 0.14, 1.0))
    # Closet bi-fold in the S wall east segment
    for ci, cx in enumerate((1.10, 1.60)):
        make_box(f"Closet_Leaf_{ci}", (cx, 0.10, 1.05), (0.48, 0.05, 2.10), (0.82, 0.80, 0.74, 1.0))
    # Bedside lamp on the nightstand
    make_lathe("Bedside_Lamp_Base", (-0.05, 3.2, 0.60), [(0.08, 0.0), (0.075, 0.02), (0.04, 0.03), (0.03, 0.05), (0.02, 0.08), (0.03, 0.10), (0.018, 0.12), (0.0, 0.12)], (0.42, 0.30, 0.18, 1.0), segments=10)
    make_cyl("Bedside_Lamp_Post", (-0.05, 3.2, 0.74), 0.012, 0.16, (0.20, 0.19, 0.20, 1.0), segments=6)
    make_lathe("Bedside_Lamp_Shade", (-0.05, 3.2, 0.80), [(0.08, 0.0), (0.12, 0.16), (0.0, 0.16)], (0.86, 0.78, 0.62, 1.0), segments=12)


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    Four cues, three distinct; Sams_Phone exists on the dresser
    (marker only). Built:

    - THE DOOR: the south-wall door gap had no door — a painted
      slab now fills it (the door she hears her father's phone
      through, two walls away), with knob and frame sides.
    - THE WEDNESDAY LIST ("a small header at the top in block
      capitals: WEDNESDAY LIST"): sheet + header bar + pen on the
      dresser top beside the phone — the desk is fully claimed by
      the monitor, console, and sketch spread.
    """
    white_door = (0.88, 0.86, 0.80, 1.0)
    make_box("Sams_Door", (0.0, 0.06, 1.02), (0.90, 0.05, 2.04), white_door)
    make_cyl("Sams_Door_Knob", (0.34, 0.105, 1.00), 0.03, 0.04,
             (0.66, 0.60, 0.42, 1.0), axis='Y', segments=8)
    for sgn in (-1, 1):
        make_box(f"Sams_Door_Frame_{'W' if sgn < 0 else 'E'}",
                 (0.49 * sgn, 0.06, 1.06), (0.07, 0.09, 2.12), (0.72, 0.68, 0.60, 1.0))
    make_box("Wednesday_List", (1.62, 2.45, 0.8425), (0.21, 0.28, 0.003),
             (0.94, 0.93, 0.88, 1.0))
    make_box("List_Header_Bar", (1.62, 2.56, 0.8445), (0.13, 0.012, 0.001),
             (0.28, 0.28, 0.32, 1.0))
    make_cyl("List_Pen", (1.50, 2.32, 0.845), 0.005, 0.13,
             (0.24, 0.28, 0.52, 1.0), axis='Y', segments=6)


def build_draft4_2026_09():
    """DRAFT 4 (2026-09-18, lore/_VISUAL_PROGRAM.md §3; 9 placements).
    The room's first WEAR (door to bed to desk; the chair's patch; the
    forearm at the desk; the bed's kick scuff; sticker residue on his
    door; the beanbag's floor ring), D3 (the switch, a power strip under
    the desk for the monitor and console, cords from the desk lamp and
    the bedside lamp), D5 (the backyard through the north window — the
    same yard the porch looks at, from the other side of the house).
    """
    from _props.detail import make_traffic_wear, make_floor_stain, make_scuff_band, make_light_switch, make_wall_outlet, make_cord_run, make_backyard_view
    floor_dk = (0.50, 0.50, 0.53, 1.0)
    bx, by = -ROOM_W/4.0, ROOM_D - 0.15 - 0.92
    dx, dy = +ROOM_W/4.0, ROOM_D - 0.45
    # ── WEAR ──
    make_traffic_wear("Wear_Path_Entry_A", [(0.0, 0.5), (-0.3, 1.6), (-0.6, 2.6), (-0.7, 3.2)], width=0.42, tint=floor_dk)
    make_traffic_wear("Wear_Path_Entry_B", [(0.2, 1.4), (0.7, 2.6), (1.0, 3.6)], width=0.36, tint=floor_dk)
    make_floor_stain("Wear_Patch_Seat", (dx+0.1, dy - 0.58), radius=0.32, tint=(0.46, 0.46, 0.49, 1.0), segments=10)
    make_floor_stain("Wear_Ring_Floor", (0.3, 1.1), radius=0.48, tint=(0.54, 0.54, 0.57, 1.0), segments=12)
    make_box("Wear_Forearm", (dx - 0.05, dy - 0.24, 0.762), (0.36, 0.08, 0.004), (0.48, 0.54, 0.48, 1.0))
    make_scuff_band("Wear_Kick_Foot", (bx, by - 0.92), 1.10, axis='X', height=0.05, band_z=0.06, tint=(0.32, 0.36, 0.32, 1.0))
    for si, (sx_, sz_, sc_) in enumerate(((-0.12, 1.32, (0.44, 0.66, 0.36, 1.0)), (0.06, 1.44, (0.24, 0.42, 0.66, 1.0)), (0.18, 1.28, (0.86, 0.82, 0.30, 1.0)), (-0.22, 1.50, (0.72, 0.30, 0.28, 1.0)))):
        make_box(f"Sticker_{si}", (sx_, 0.087, sz_), (0.06, 0.002, 0.06), sc_)
    make_box("Sticker_Residue", (0.24, 0.086, 1.40), (0.05, 0.001, 0.05), (0.80, 0.78, 0.72, 1.0))
    # ── D3 ──
    make_light_switch("Switch_Door", (0.70, 0.0), axis='X', face_sign=1, z=1.20, aged=True)
    make_box("Power_Strip", (dx + 0.20, dy + 0.22, 0.03), (0.30, 0.06, 0.04), (0.86, 0.86, 0.82, 1.0))
    make_wall_outlet("Outlet_N_1", (dx + 0.20, ROOM_D), axis='X', face_sign=-1, z=0.30, aged=True)
    make_cord_run("Cord_1", (dx + 0.20, dy + 0.25, 0.03), (dx + 0.20, ROOM_D - 0.12, 0.30), sag=0.0)
    make_cord_run("Cord_2", (dx + 0.10, dy + 0.34, 0.80), (dx + 0.12, dy + 0.22, 0.05), sag=0.03)
    make_cord_run("Cord_3", (dx - 0.30, dy - 0.06, 0.77), (dx + 0.06, dy + 0.22, 0.05), sag=0.03)
    make_cord_run("Cord_4", (dx - 0.34, dy + 0.22, 0.76), (dx + 0.08, dy + 0.22, 0.05), sag=0.03)
    make_wall_outlet("Outlet_N_2", (0.30, ROOM_D), axis='X', face_sign=-1, z=0.30, aged=True)
    make_cord_run("Cord_5", (-0.05, 3.28, 0.60), (0.30, ROOM_D - 0.12, 0.30), sag=0.02)
    # ── D5 · the backyard through the north window ──
    make_backyard_view("Yard", ROOM_D, span=6.0, tree=(2.6, 3.0))


def main():
    clear_scene()
    build_shell()
    build_bed()
    build_desk_lamp()
    build_posters()
    build_rug()
    build_win()
    build_ceiling_infra()
    build_dressing()
    build_hero_props()
    build_hero_props_2026_09()
    build_draft4_2026_09()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/sam_bedroom.glb"))
    print(f"\n[build_sam_bedroom] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
