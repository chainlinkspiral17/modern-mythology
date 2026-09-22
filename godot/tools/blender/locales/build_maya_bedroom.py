"""Maya's Bedroom — vol6 — Maya Miller (Chief Miller's daughter, a
sharp, observant teenage girl). Distinct LAVENDER + teal palette and a
teen-girl prop set (vanity + round mirror + string lights, a bulletin
board of photos & concert tickets, a bookshelf of paperbacks, a record
player, plants, a patterned duvet + throw pillows, a hamper, a rug) so
the room reads unmistakably as HERS — not a reskin of Sam's.

DRAFT 4 (2026-09-18, lore/_VISUAL_PROGRAM.md §3): turned desk legs and
an apron, a real desk lamp (weighted base, bent arm, cone head, bulb),
pulls on the nightstand and vanity, perfume bottles as bottles, the
record player with a record on the platter and a tonearm, the crate
slotted, the hamper a basket with a lid, the fairy string strung; HER
DOOR (the opening had no leaf) with stickers; first WEAR; D3 switch,
outlets, five cords; D5 the backyard through the north window (the
shared `make_backyard_view`). The .tscn gains the fairy string's wash.

DRAFT 5 targets: the corkboard's photos as photos; the bookshelf's
paperbacks at a lean; the vanity mirror's frame as a lathe ring; the
duvet's pattern (the teal band as a real stripe); the box fan's blades;
Deck: the sheet's establish at night and `insert floorboard`.
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
# Lavender walls, teal accent — cool, distinct from the boys' tan rooms.
PAL_WALL = {"wall": (0.74, 0.68, 0.86, 1.0), "baseboard": (0.50, 0.44, 0.62, 1.0)}
COL_FLOOR = (0.70, 0.60, 0.50, 1.0); COL_SEAM = (0.44, 0.34, 0.26, 1.0); COL_WOOD = (0.56, 0.42, 0.52, 1.0)
COL_ACCENT = (0.36, 0.72, 0.70, 1.0)     # teal
COL_DUVET = (0.60, 0.42, 0.72, 1.0)      # violet duvet
COL_DUVET2 = (0.42, 0.70, 0.68, 1.0)     # teal patterned band
COL_PILLOW = (0.94, 0.80, 0.86, 1.0)     # blush throw pillows

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
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
                 with_grid=False, with_stains=False,
                 palette={"tile": (0.96, 0.93, 0.74, 1.0)})  # the pale yellow ceiling
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})

def build_bed():
    # Re-arranged (2026-07-15): bed pushed under the N window, headboard
    # against the N wall — frees the W wall for the vanity and reads
    # distinct from the shared -ROOM_W/4 side-wall twin. Keeps her
    # violet/teal duvet + throw pillows.
    bx, by = 0.0, ROOM_D - 1.15
    # the shared bed, violet duvet made (2026-09-07); the headboard stays
    from _props.furniture import make_bed
    # "frame" (open underneath): the loose floorboard, the envelope and
    # the photograph hide UNDER this bed and their inserts look under it
    make_bed("Bed", bx, by, head="+Y", w=1.24, d=1.86, style="frame",
             frame_col=(0.52, 0.40, 0.50, 1.0), mattress_col=(0.92, 0.86, 0.84, 1.0),
             blanket_col=COL_DUVET, pillow_col=P.PAPER, pillows=2, made=True, headboard=True)
    # Throw pillows in front of the sleeping pillow
    make_chamfer_box("Bed_ThrowPillow_A", (bx-0.30, by+0.12, 0.67), (0.34, 0.34, 0.16), COL_PILLOW)
    make_chamfer_box("Bed_ThrowPillow_B", (bx+0.30, by+0.12, 0.67), (0.34, 0.34, 0.16), COL_ACCENT)

def build_desk_lamp():
    dx, dy = ROOM_W/2.0 - 0.54, 1.5   # end against the E wall; the bed owns the N wall (2026-09-07)
    # draft 4 (2026-09-18): chamfered top, apron, turned legs; the lamp
    # a weighted base, a bent arm, a cone head
    make_chamfer_box("Desk_Top", (dx, dy, 0.74), (1.00, 0.60, 0.04), COL_WOOD, chamfer=0.01)
    make_box("Desk_Apron_F", (dx, dy-0.27, 0.68), (0.88, 0.02, 0.08), (0.46, 0.34, 0.44, 1.0))
    for li in range(4):
        lx, ly = dx+(-0.44,+0.44,-0.44,+0.44)[li], dy+(-0.24,-0.24,+0.24,+0.24)[li]
        make_lathe(f"Desk_Leg_{li}", (lx, ly, 0.0), [(0.022, 0.0), (0.03, 0.05), (0.02, 0.10), (0.026, 0.30), (0.032, 0.40), (0.022, 0.55), (0.022, 0.68), (0.03, 0.72)], COL_WOOD, segments=8)
    make_lathe("Lamp_Base", (dx-0.30, dy+0.20, 0.76), [(0.07, 0.0), (0.065, 0.02), (0.03, 0.035), (0.012, 0.04), (0.0, 0.04)], P.METAL_BLACK, segments=10)
    make_tube("Lamp_Arm", [(dx-0.30, dy+0.20, 0.80), (dx-0.30, dy+0.20, 1.02), (dx-0.22, dy+0.20, 1.14)], 0.01, P.METAL_BLACK, segments=5)
    make_lathe("Lamp_Head", (dx-0.20, dy+0.20, 1.10), [(0.0, 0.0), (0.03, 0.0), (0.065, 0.10), (0.06, 0.11), (0.0, 0.11)], COL_ACCENT, segments=10)
    make_lathe("Lamp_Bulb", (dx-0.20, dy+0.20, 1.11), [(0.0, 0.0), (0.02, 0.005), (0.024, 0.03), (0.0, 0.05)], (0.98, 0.94, 0.80, 1.0), segments=8)
    # A laptop, open, on the desk
    make_box("Laptop_Base", (dx+0.16, dy+0.06, 0.77), (0.34, 0.24, 0.03), P.METAL_STEEL)
    make_box("Laptop_Screen", (dx+0.16, dy+0.18, 0.90), (0.34, 0.02, 0.24), (0.62, 0.80, 0.92, 1.0))
    # A little stack of paperbacks
    for bi in range(3):
        make_box(f"Desk_Book_{bi}", (dx-0.36, dy-0.14+bi*0.05, 0.79+bi*0.05), (0.16, 0.24, 0.05),
                 P.SNACK_TINTS[bi%len(P.SNACK_TINTS)])

def build_posters():
    # Band / art posters along the west wall
    for pi in range(3):
        px = -ROOM_W/2.0+0.05
        py = 1.0 + pi*1.5
        make_faded_poster(f"Poster_W_{pi}", (px, py, 1.60))

def build_rug():
    make_cyl("Rug", (0.0, ROOM_D/2.0, 0.012), 1.20, 0.005, COL_ACCENT)

def build_win():
    make_window("Window_N", (0.0, ROOM_D-0.02, 1.50), width=1.20, height=1.00)

def build_ceiling_infra():
    # A 1991 bedroom: one dome fixture, no shop tubes (lamp is the
    # scene light — "She turns off the lamp.")
    make_cyl("Ceiling_Dome", (0.0, 2.5, CEIL-0.10), 0.16, 0.16, (0.96, 0.90, 0.72, 1.0), segments=12)
    make_smoke_detector("Smoke", (0.9, ROOM_D/2.0, CEIL))
    make_hvac_vent("HVAC", (-ROOM_W/4.0, ROOM_D-0.5, CEIL), width=0.80, depth=0.40)


def build_dressing():
    """Teen-girl dressing: a vanity with a ROUND mirror + trinket bottles,
    warm string lights along the north wall, a bulletin board of photos &
    concert tickets, a bookshelf of paperbacks, a record player on a
    crate, a hamper, and a floor plant."""
    bx, by = 0.0, ROOM_D - 1.15
    # Nightstand + alarm clock beside the bed
    nsx = bx + 0.95
    make_chamfer_box("Nightstand", (nsx, by+0.7, 0.28), (0.40, 0.40, 0.56), COL_WOOD)
    make_box("Clock", (nsx, by+0.7, 0.62), (0.15, 0.10, 0.10), P.METAL_BLACK)
    make_lathe("Nightstand_Pull", (nsx, by+0.7-0.205, 0.40), [(0.0, 0.0), (0.012, 0.0), (0.014, 0.01), (0.008, 0.02), (0.0, 0.02)], (0.66, 0.60, 0.42, 1.0), segments=8)
    # Vanity dresser against the east wall: body, three drawers, ROUND mirror
    vx = ROOM_W/2.0 - 0.30
    make_chamfer_box("Vanity_Body", (vx, ROOM_D-1.2, 0.42), (0.50, 0.90, 0.84), COL_WOOD)
    for di in range(3):
        make_box(f"Vanity_Drawer_{di}", (vx-0.26, ROOM_D-1.2, 0.24+di*0.24), (0.02, 0.80, 0.18), (0.44, 0.32, 0.42, 1.0))
        make_lathe(f"Vanity_Pull_{di}", (vx-0.27, ROOM_D-1.2, 0.23+di*0.24), [(0.0, 0.0), (0.012, 0.0), (0.014, 0.01), (0.008, 0.02), (0.0, 0.02)], (0.66, 0.60, 0.42, 1.0), segments=8)
    make_cyl("Vanity_Mirror", (vx-0.02, ROOM_D-1.2, 1.34), 0.34, 0.03, (0.80, 0.86, 0.92, 0.6), axis='X', segments=16)
    make_cyl("Vanity_MirrorFrame", (vx+0.005, ROOM_D-1.2, 1.34), 0.38, 0.03, COL_ACCENT, axis='X', segments=16)
    # Perfume/trinket bottles on the vanity top
    for ti, tc in enumerate([(0.86, 0.62, 0.72, 1.0), (0.62, 0.78, 0.86, 1.0), (0.92, 0.82, 0.42, 1.0)]):
        make_lathe(f"Trinket_{ti}", (vx-0.1, ROOM_D-1.5+ti*0.2, 0.84),
                   [(0.02, 0.0), (0.03, 0.01), (0.032, 0.06 + 0.01 * ti), (0.018, 0.09 + 0.01 * ti), (0.012, 0.11 + 0.01 * ti), (0.016, 0.125 + 0.01 * ti), (0.0, 0.13 + 0.01 * ti)],
                   tc, segments=8)
    # Bulletin board (cork) with a scatter of photos + concert tickets, west wall
    bbx = -ROOM_W/2.0 + 0.06
    make_box("Corkboard", (bbx, ROOM_D-1.0, 1.55), (0.04, 1.10, 0.80), (0.62, 0.46, 0.30, 1.0))
    for pi in range(6):
        col = (0.90, 0.88, 0.82, 1.0) if pi % 2 == 0 else P.SNACK_TINTS[pi % len(P.SNACK_TINTS)]
        oy = ROOM_D-1.4 + (pi % 3) * 0.34
        oz = 1.30 + (pi // 3) * 0.36
        make_box(f"Pin_{pi}", (bbx+0.03, oy, oz), (0.01, 0.24, 0.18), col)
    # Bookshelf of paperbacks against the north wall
    shx = ROOM_W/2.0 - 0.9
    # (2026-09-08: was one solid block with the books INSIDE it —
    # now a carcass: back, sides, top, three boards the books sit on)
    make_box("Bookshelf_Back", (shx, ROOM_D-0.08, 0.90), (0.90, 0.02, 1.80), COL_WOOD)
    for sx_ in (-1, 1):
        make_box(f"Bookshelf_Side_{sx_:+d}", (shx + sx_ * 0.44, ROOM_D-0.20, 0.90), (0.02, 0.26, 1.80), COL_WOOD)
    make_box("Bookshelf_Top", (shx, ROOM_D-0.20, 1.79), (0.90, 0.26, 0.02), COL_WOOD)
    for r_ in range(3):
        make_box(f"Bookshelf_Board_{r_}", (shx, ROOM_D-0.20, 0.26 + r_*0.52), (0.86, 0.24, 0.02), COL_WOOD)
    for r in range(3):
        for c in range(7):
            make_box(f"Book_{r}_{c}", (shx-0.42+c*0.12, ROOM_D-0.22, 0.42+r*0.52),
                     (0.10, 0.20, 0.30), P.SNACK_TINTS[(r*7+c) % len(P.SNACK_TINTS)])
    # Record player on a milk crate, SE
    rcx, rcy = ROOM_W/2.0-0.4, 0.8
    make_chamfer_box("Crate", (rcx, rcy, 0.24), (0.44, 0.44, 0.48), (0.42, 0.52, 0.62, 1.0), chamfer=0.01)
    for si2 in range(3):
        make_box(f"Crate_Slot_{si2}", (rcx - 0.222, rcy, 0.12 + si2 * 0.12), (0.004, 0.36, 0.05), (0.30, 0.38, 0.46, 1.0))
    make_chamfer_box("RecordPlayer", (rcx, rcy, 0.52), (0.42, 0.42, 0.10), P.METAL_BLACK, chamfer=0.008)
    make_cyl("RecordPlatter", (rcx, rcy, 0.58), 0.16, 0.01, (0.14, 0.14, 0.16, 1.0), segments=16)
    make_cyl("Record", (rcx, rcy, 0.588), 0.15, 0.003, (0.08, 0.08, 0.09, 1.0), segments=20)
    make_cyl("Record_Label", (rcx, rcy, 0.5905), 0.05, 0.002, (0.86, 0.62, 0.72, 1.0), segments=12)
    make_lathe("Tonearm_Pivot", (rcx + 0.17, rcy - 0.16, 0.57), [(0.02, 0.0), (0.02, 0.03), (0.0, 0.03)], P.METAL_STEEL, segments=8)
    make_tube("Tonearm", [(rcx + 0.17, rcy - 0.16, 0.605), (rcx + 0.05, rcy + 0.02, 0.60)], 0.005, P.METAL_STEEL, segments=5)
    # Wicker hamper, corner
    make_lathe("Hamper", (-ROOM_W/2.0+0.5, 0.6, 0.0), [(0.21, 0.0), (0.23, 0.02), (0.27, 0.62), (0.28, 0.66), (0.26, 0.68), (0.0, 0.66)], (0.74, 0.62, 0.44, 1.0), segments=12)
    make_lathe("Hamper_Lid", (-ROOM_W/2.0+0.5, 0.6, 0.68), [(0.29, 0.0), (0.29, 0.02), (0.20, 0.045), (0.0, 0.05)], (0.68, 0.56, 0.40, 1.0), segments=12)
    # Floor plant, SE corner
    make_floor_plant("Plant", (ROOM_W/2.0-0.5, 0.7, 0.0), palette={"leaf": (0.40, 0.60, 0.42, 1.0), "pot": (0.42, 0.72, 0.70, 1.0)})
    # Warm string / fairy lights along the north wall
    for i in range(8):
        make_cyl(f"Fairy_{i}", (-1.4+i*0.4, ROOM_D-0.08, 2.05), 0.028, 0.028, (1.0, 0.84, 0.6, 1.0), segments=6)
        if i < 7:
            make_tube(f"Fairy_String_{i}", [(-1.4+i*0.4, ROOM_D-0.07, 2.06), (-1.2+i*0.4, ROOM_D-0.07, 2.02), (-1.0+i*0.4, ROOM_D-0.07, 2.06)], 0.003, (0.30, 0.30, 0.28, 1.0), segments=4)

def build_hero_props():
    """2026-08-03 hero-prop pass. THE LOOSE THIRD FLOORBOARD —
    counted in from the N window, under the pulled-back rug — with
    the shallow cavity and the sealed manila envelope (the whole of
    vol6_ch4_maya_floor). Cavity at y=3.30 so it's clear of the bed;
    the rug re-centres over it."""
    pine = (0.78, 0.62, 0.38, 1.0)       # worn honey pine
    pine_dk = (0.66, 0.52, 0.30, 1.0)
    # Countable plank seams running E-W, 0.14 m apart, over the slab
    n = int(5.0 / 0.14)
    for i in range(n):
        py = 0.07 + i * 0.14
        make_box(f"Plank_Seam_{i}", (0.0, py, 0.004), (4.0, 0.012, 0.004), pine_dk)
    make_box("Plank_Field", (0.0, 2.5, 0.002), (4.0, 5.0, 0.003), pine)
    # The loose board, lifted a crack at one end
    make_box("Loose_Board", (0.0, 3.30, 0.020), (0.90, 0.13, 0.018), pine_dk)
    # The cavity + the envelope
    make_box("Cavity_Void", (0.0, 3.30, -0.035), (0.42, 0.125, 0.07), (0.10, 0.08, 0.06, 1.0))
    make_box("Manila_Envelope", (0.0, 3.30, -0.008), (0.26, 0.11, 0.006), (0.82, 0.72, 0.50, 1.0))
    # Rug re-centred so it covers the board when smoothed back
    # (the build's Rug cyl stays; this ring marks the pulled-back lip)
    make_cyl("Rug_Fold", (0.0, 3.02, 0.018), 0.55, 0.012, (0.72, 0.42, 0.44, 1.0), segments=14)
    # The box fan by the window ("The fan is on.")
    make_chamfer_box("Box_Fan", (-1.30, 4.40, 0.24), (0.44, 0.16, 0.44), (0.80, 0.78, 0.74, 1.0))
    make_cyl("Box_Fan_Grille", (-1.30, 4.31, 0.24), 0.17, 0.02, (0.30, 0.30, 0.32, 1.0), axis='Y', segments=12)
    # The spiral notebook on the desk + the packing-order supplies
    make_box("Spiral_Notebook", (0.64, 1.62, 0.765), (0.20, 0.26, 0.012), (0.30, 0.44, 0.62, 1.0))
    make_cyl("Spiral_Coil", (0.545, 1.62, 0.772), 0.008, 0.25, (0.60, 0.62, 0.64, 1.0), axis='Y', segments=6)
    for si, (sx, col) in enumerate(((0.60, (0.62, 0.24, 0.24, 1.0)), (0.80, (0.24, 0.42, 0.52, 1.0)),
                                    (1.00, (0.72, 0.62, 0.30, 1.0)), (1.20, (0.86, 0.82, 0.72, 1.0)))):
        make_box(f"Pack_Supply_{si}", (sx, 1.30, 0.785), (0.14, 0.10, 0.03), col)
    # Phone on the nightstand
    make_box("Phone", (0.95, 4.55, 0.585), (0.08, 0.15, 0.012), (0.12, 0.12, 0.14, 1.0))


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    Four distinct cues. The floorboard station exists (Loose_Board
    + Cavity_Void + Manila_Envelope + Rug_Fold — a new SYNONYMS
    entry floorboards -> board lets the tools see it). Built:

    - THE PHOTOGRAPH (the dock at dusk, 1978, the charcoal suit):
      a small print lying on the rug beside the pulled-back fold,
      where it came out of the envelope.
    - THE HANDS ("Her grandmother's hand on her hand", in the
      dark): the duvet-crease residue grammar, two creases where
      they sat.
    """
    make_box("Dock_Photograph", (0.30, 3.15, 0.0165), (0.110, 0.160, 0.001),
             (0.82, 0.80, 0.74, 1.0))
    make_box("Photograph_Border", (0.30, 3.15, 0.0175), (0.094, 0.144, 0.0005),
             (0.35, 0.33, 0.30, 1.0))
    make_box("Hands_Duvet_Crease_A", (0.30, 3.60, 0.596), (0.16, 0.05, 0.012),
             (0.44, 0.34, 0.52, 1.0))
    make_box("Hands_Duvet_Crease_B", (0.33, 3.72, 0.595), (0.05, 0.13, 0.010),
             (0.42, 0.32, 0.50, 1.0))


def build_draft4_2026_09():
    """DRAFT 4 (2026-09-18, lore/_VISUAL_PROGRAM.md §3; 10 placements).
    Her door (the shell had an opening and no leaf), the room's first
    WEAR (door to bed to desk; the rug's worn centre; the forearm patch
    at the desk; a scuff where the headboard meets the wall; scuffs at
    the bed's foot; pin holes on the corkboard), D3 (the switch by the
    door, outlets, and cords from the desk lamp, the laptop, the record
    player, the fairy lights and the box fan), D5 (the backyard the
    north window looks at: lawn, board fence, a tree, a roofline).
    """
    from _props.detail import make_traffic_wear, make_floor_stain, make_scuff_band, make_light_switch, make_wall_outlet, make_cord_run, make_backyard_view
    floor_dk = (0.58, 0.49, 0.40, 1.0)
    bx, by = 0.0, ROOM_D - 1.15
    dx, dy = ROOM_W/2.0 - 0.54, 1.5
    # ── her door in the south opening, with knob and frame ──
    make_box("Mayas_Door", (0.0, 0.06, 1.02), (0.90, 0.05, 2.04), (0.90, 0.88, 0.86, 1.0))
    make_lathe("Mayas_Door_Knob_Rose", (0.34, 0.09, 1.00), [(0.03, 0.0), (0.03, 0.01), (0.0, 0.01)], (0.66, 0.60, 0.42, 1.0), segments=8)
    make_cyl("Mayas_Door_Knob", (0.34, 0.115, 1.00), 0.028, 0.04, (0.66, 0.60, 0.42, 1.0), axis='Y', segments=8)
    for sgn in (-1, 1):
        make_box(f"Mayas_Door_Frame_{'W' if sgn < 0 else 'E'}", (0.49 * sgn, 0.06, 1.06), (0.07, 0.09, 2.12), (0.78, 0.74, 0.80, 1.0))
    for si, (sx_, sz_, sc_) in enumerate(((0.10, 1.30, (0.36, 0.72, 0.70, 1.0)), (0.22, 1.42, (0.86, 0.62, 0.72, 1.0)), (-0.15, 1.36, (0.92, 0.82, 0.42, 1.0)))):
        make_box(f"Sticker_{si}", (sx_, 0.087, sz_), (0.06, 0.002, 0.06), sc_)
    # ── WEAR ──
    make_traffic_wear("Wear_Path_Entry_A", [(0.0, 0.5), (-0.2, 1.6), (-0.4, 2.6), (-0.3, 3.0)], width=0.42, tint=floor_dk)
    make_traffic_wear("Wear_Path_B", [(-0.2, 2.6), (0.6, 2.0), (1.1, 1.6)], width=0.34, tint=floor_dk)
    make_floor_stain("Wear_Centre", (0.0, ROOM_D/2.0 - 0.2), radius=0.50, tint=(0.32, 0.64, 0.62, 1.0), segments=12)
    make_box("Wear_Forearm", (dx + 0.05, dy - 0.22, 0.762), (0.36, 0.09, 0.004), (0.62, 0.48, 0.58, 1.0))
    make_scuff_band("Wear_Wall_Rub", (bx, ROOM_D), 1.30, axis='X', height=0.10, band_z=0.95, tint=(0.66, 0.60, 0.78, 1.0))
    make_scuff_band("Wear_Kick_Foot", (bx, by - 0.93), 1.10, axis='X', height=0.05, band_z=0.06, tint=(0.44, 0.34, 0.42, 1.0))
    for hi, (hy, hz) in enumerate(((ROOM_D-1.25, 1.75), (ROOM_D-0.75, 1.30), (ROOM_D-1.0, 1.85))):
        make_cyl(f"Wear_PinHole_{hi}", (-ROOM_W/2.0 + 0.085, hy, hz), 0.004, 0.006, (0.40, 0.28, 0.18, 1.0), axis='X', segments=4)
    # ── D3 ──
    make_light_switch("Switch_Door", (1.15, 0.0), axis='X', face_sign=1, z=1.20, aged=True)   # on the wall east of the door gap (2026-09-22: it hung in the doorway)
    make_wall_outlet("Outlet_E_1", (ROOM_W/2.0, 1.20), axis='Y', face_sign=-1, z=0.30, aged=True)
    make_cord_run("Cord_1", (dx-0.30, dy+0.20, 0.76), (ROOM_W/2.0 - 0.13, 1.20, 0.30), sag=0.06)
    make_cord_run("Cord_2", (dx+0.16, dy+0.18, 0.76), (ROOM_W/2.0 - 0.13, 1.20, 0.30), sag=0.04)
    make_wall_outlet("Outlet_S_1", (ROOM_W/2.0 - 0.6, 0.0), axis='X', face_sign=1, z=0.30, aged=True)
    make_cord_run("Cord_3", (ROOM_W/2.0-0.4, 0.8 + 0.21, 0.50), (ROOM_W/2.0 - 0.6, 0.13, 0.30), sag=0.04)
    make_wall_outlet("Outlet_N_1", (-1.62, ROOM_D), axis='X', face_sign=-1, z=0.30, aged=True)
    make_cord_run("Cord_4", (-1.42, ROOM_D - 0.08, 2.04), (-1.62, ROOM_D - 0.12, 0.30), sag=0.0)
    make_cord_run("Cord_5", (-1.30, 4.32, 0.06), (-1.62, ROOM_D - 0.12, 0.30), sag=0.02)
    # ── D5 · the backyard through the north window ──
    make_backyard_view("Yard", ROOM_D, span=6.0, tree=(-2.4, 3.2))


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
        "../../../assets/3d/locales/maya_bedroom.glb"))
    print(f"\n[build_maya_bedroom] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
