"""VOL 5 · Hospice Room — late chapter, end-of-life palliative care.
Adjustable bed, IV stand, monitor, chair for visitor, soft window
light, gentle palette.

DRAFT 3 (2026-09-19, lore/_VISUAL_PROGRAM.md §3 backgrounds pass, the
arcana primitive upgrade's sixth room; 1 VN placement + the board).
LAYOUT the gates never reported: the north window's frame and glass
sat inside the wall's thickness (invisible); the beach print hung
INSIDE the window's opening; the spare blanket floated 70 cm south of
the bed's foot; a second water glass floated beside the bed; two
pairs of slippers shared names (one unworn by the door — canon —
one kicked under the bed); three flower stems stood in the air over
the bed table with no vase, while the vase floated on a sill that
did not exist, in the same space as the rose's votive; the prayer
book sat in the lamp's base. The north wall is cut around the
window (piers, spandrel, lintel) with a sill for the votive; the
print moved to the west wall; the blanket drapes over the foot
panel; the vase and its flowers are on the dresser; the D4 glass and
slippers are gone (the hero pair stays); the book is off the lamp.
PRIMITIVES: the visitor chair as chamfered cushions with rolled
arms, the throw draped; the bedside lamp as base, column, shade,
bulb; the IV line as a tube to the bed rail; the monitor's pole with
a collar, its cable to the bed; the control pendant on its cord; a
gooseneck at the sink. WEAR (three weeks of a vigil): the visitor's
floor patch, the bed table's ring, the door-side kick, the chair
arm's shine. D3: the monitor's and lamp's cords. D5: the hospice
garden past the window — lawn, hedge, a birch, a bench. Scene: the
"BedsideLamp" light 1.5 m from the lamp becomes the under-cabinet
light's practical (the hero-props note calls it the scene's only
light).
Draft 4 targets: the raised head section in make_bed's hospital
style; the sink's mirror; the curtains as gathered lathes; the wall
oxygen outlet; Deck: the preset + establish_b.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_chamfer_box, make_lathe, make_tube, make_rot_box, export_glb
from _props.furniture import make_lamp
from _props.trees import make_broadleaf
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster
from _props.safety import make_smoke_detector, make_fluorescent_tube_fixture, make_sprinkler
from _props.detail import (make_floor_stain, make_light_switch, make_threshold, make_traffic_wear, make_wall_outlet, make_wall_tint_band)
from _props.objects import make_drinking_glass

# Warm, home-like palette (hospice reads gentle, not clinical)
PAL = {"wall": (0.90, 0.84, 0.74, 1.0), "baseboard": (0.62, 0.52, 0.40, 1.0)}
COL_FLOOR = (0.66, 0.52, 0.38, 1.0); COL_SEAM = (0.48, 0.36, 0.26, 1.0)
COL_BED_FRAME = (0.68, 0.60, 0.52, 1.0); COL_LINEN = (0.96, 0.94, 0.88, 1.0)
COL_CHAIR = (0.60, 0.40, 0.34, 1.0); COL_MEDICAL = (0.86, 0.86, 0.84, 1.0)
COL_MONITOR_SCREEN = (0.12, 0.42, 0.32, 1.0); COL_IV_BAG = (0.86, 0.92, 0.86, 1.0)
COL_PLANT_LEAF = (0.42, 0.52, 0.36, 1.0)
COL_BLANKET = (0.62, 0.70, 0.58, 1.0); COL_THROW = (0.72, 0.54, 0.42, 1.0)
COL_LAMP_SHADE = (0.96, 0.86, 0.66, 1.0); COL_DRESSER = (0.56, 0.42, 0.28, 1.0)
COL_VASE = (0.42, 0.56, 0.62, 1.0)
COL_FLOWER = [(0.88, 0.46, 0.52, 1.0), (0.92, 0.74, 0.36, 1.0), (0.80, 0.56, 0.78, 1.0)]
ROOM_W = 6.0; ROOM_D = 5.5; CEIL = 2.80
WIN_X = 1.5   # draft 3: the north window's centre (east of the bed)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=bb)
    # Draft 3: the north wall CUT around the window — the frame and
    # glass used to sit inside the wall. The window is EAST of the bed
    # (x 0.5..2.5, z 0.9..2.5) so the bed's head backs a real wall and
    # the sink sits under the light.
    make_wall("Wall_N_W", (-1.35, ROOM_D, 0), length=3.7, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (+2.85, ROOM_D, 0), length=0.7, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_box("Wall_N_Spandrel", (WIN_X, ROOM_D, 0.45), (2.00, 0.20, 0.90), PAL["wall"])
    make_box("Wall_N_Spandrel_Base", (WIN_X, ROOM_D - 0.06, 0.08), (2.00, 0.06, 0.16), PAL["baseboard"])
    make_box("Wall_N_Lintel", (WIN_X, ROOM_D, 2.65), (2.00, 0.20, 0.30), PAL["wall"])
    make_wall("Wall_S_W", (-2.0, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL)
    make_wall("Wall_S_E", (+2.0, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, with_grid=False)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10),("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": (0.62, 0.58, 0.54, 1.0)})
    # Large window N wall (soft natural light)
    # (the sill at 0.9 — a hospice window over a bed's head; the wall
    # behind the mattress is the spandrel, which the bed rule reads)
    make_box("Window_N_Frame", (WIN_X, ROOM_D, 1.70), (2.00, 0.04, 1.60), COL_MEDICAL)
    make_box("Window_N_Glass", (WIN_X, ROOM_D, 1.70), (1.80, 0.005, 1.40), (0.92, 0.92, 0.86, 0.50))
    make_box("Window_N_Mullion", (WIN_X, ROOM_D - 0.005, 1.70), (0.04, 0.02, 1.40), COL_MEDICAL)
    # the sill (the votive stands on it), the sheer curtains inside
    make_box("Window_N_Sill", (WIN_X, ROOM_D - 0.15, 0.88), (2.20, 0.16, 0.04), (0.62, 0.58, 0.54, 1.0))
    make_box("Window_N_Curtain_L", (WIN_X - 1.12, ROOM_D-0.12, 1.70), (0.30, 0.04, 1.60), COL_LINEN)
    make_box("Window_N_Curtain_R", (WIN_X + 1.12, ROOM_D-0.12, 1.70), (0.30, 0.04, 1.60), COL_LINEN)

def build_hospital_bed():
    bx, by = 0.0, 4.15          # head to the N wall (2026-09-10)
    # the shared hospital bed — posts on casters, deck, thin mattress,
    # side rails, one pillow, a tucked sage blanket (2026-09-07; the
    # raised head section is a next-pass target for make_bed)
    from _props.furniture import make_bed
    make_bed("Bed", bx, by, head="+Y", w=1.20, d=2.20, style="hospital",
             frame_col=COL_BED_FRAME, mattress_col=COL_LINEN, blanket_col=COL_BLANKET, pillow_col=P.PAPER)
    # Foot panel
    make_box("Bed_Foot", (bx, by-1.07, 0.60), (1.20, 0.04, 0.60), COL_BED_FRAME)   # against the deck (2026-09-23: 3 cm off it)
    # Bed controls dangling on their cord from the rail (draft 3)
    # the pendant hangs from the side rail by its cord (2026-09-23: both in the air)
    make_chamfer_box("Bed_Controls", (bx+0.64, by-0.20, 0.40), (0.10, 0.06, 0.20), COL_MEDICAL, chamfer=0.01)
    make_tube("Bed_Controls_Cord", [(bx+0.64, by-0.20, 0.50), (bx+0.58, by-0.20, 0.86)], 0.006, (0.70, 0.70, 0.70, 1.0), segments=5)

def build_iv_stand_and_monitor():
    # IV stand beside bed
    ix, iy = +1.0, 4.20
    make_cyl("IV_Pole", (ix, iy, 1.05), 0.012, 1.94, COL_MEDICAL)
    make_lathe("IV_Base", (ix, iy, 0.0), [(0.20, 0.0), (0.20, 0.03), (0.06, 0.06), (0.02, 0.08)], COL_MEDICAL, segments=10)
    make_tube("IV_Hook", [(ix, iy, 1.98), (ix - 0.06, iy, 2.02), (ix - 0.10, iy, 1.92)], 0.006, COL_MEDICAL, segments=5)
    make_chamfer_box("IV_Bag", (ix-0.04, iy, 1.70), (0.04, 0.16, 0.30), COL_IV_BAG, chamfer=0.01)   # on the pole (2026-09-23: 7 cm off it)
    # the drip line to the bed rail (draft 3: a tube, not a post)
    make_tube("IV_Tube", [(ix-0.04, iy, 1.55), (ix-0.09, iy, 1.00), (ix-0.41, iy, 0.86)], 0.004, COL_IV_BAG, segments=4)   # bag to the bed rail
    # Vitals monitor on a cart
    mx, my = -1.0, 4.20
    make_box("Monitor_Cart_Base", (mx, my, 0.05), (0.50, 0.50, 0.10), COL_MEDICAL)
    for wi, (wx, wy) in enumerate([(mx-0.22, my-0.22),(mx+0.22, my-0.22),(mx-0.22, my+0.22),(mx+0.22, my+0.22)]):
        make_cyl(f"Monitor_Wheel_{wi}", (wx, wy, 0.04), 0.04, 0.04, P.METAL_BLACK, axis='X')
    make_lathe("Monitor_Pole", (mx, my, 0.10), [(0.045, 0.0), (0.045, 0.60), (0.06, 0.62), (0.06, 0.66), (0.04, 0.68), (0.04, 0.96)], COL_MEDICAL, segments=10)
    make_chamfer_box("Monitor_Body", (mx, my, 1.20), (0.40, 0.30, 0.30), COL_MEDICAL, chamfer=0.015)
    make_tube("Monitor_Cable", [(mx + 0.18, my + 0.10, 1.06), (mx + 0.30, my + 0.05, 0.40), (mx + 0.42, my - 0.10, 0.30)], 0.005, (0.40, 0.40, 0.42, 1.0), segments=4)
    make_box("Monitor_Screen", (mx, my-0.16, 1.22), (0.34, 0.005, 0.22), COL_MONITOR_SCREEN)
    # Vitals waveform — abstracted as small lines on the screen
    for li in range(8):
        make_box(f"Monitor_Wave_{li}", (mx - 0.14 + li*0.04, my-0.165, 1.22), (0.02, 0.005, 0.02), (0.62, 0.96, 0.62, 1.0))

def build_visitor_chair_and_decor():
    # Comfortable visitor armchair (upholstered, w/ arms) BY THE
    # WINDOW, back against the north wall, facing the bed — the
    # script's "the chair by the window", and no chair floats in
    # the middle of a floor (user note 2026-08-09).
    cx, cy = -1.90, 5.00
    # (draft 3: chamfered cushions, rolled arms, turned legs, the throw
    # draped over the left arm)
    make_chamfer_box("VisitorChair_Seat", (cx, cy, 0.46), (0.56, 0.56, 0.14), COL_CHAIR, chamfer=0.03)
    make_chamfer_box("VisitorChair_Back", (cx, cy+0.26, 0.82), (0.56, 0.12, 0.72), COL_CHAIR, chamfer=0.03)
    for sgn in (-1, +1):
        make_chamfer_box(f"VisitorChair_Arm_{sgn:+d}", (cx+sgn*0.30, cy, 0.60), (0.10, 0.52, 0.14), COL_CHAIR, chamfer=0.02)
        make_cyl(f"VisitorChair_Arm_Roll_{sgn:+d}", (cx+sgn*0.30, cy, 0.70), 0.05, 0.52, COL_CHAIR, segments=10, axis='Y')
    for li, (lx, ly) in enumerate([(cx-0.24,cy-0.24),(cx+0.24,cy-0.24),(cx-0.24,cy+0.24),(cx+0.24,cy+0.24)]):
        make_lathe(f"VisitorChair_Leg_{li}", (lx, ly, 0.0), [(0.022, 0.0), (0.026, 0.03), (0.02, 0.08), (0.024, 0.30), (0.03, 0.36), (0.025, 0.39)], (0.40, 0.28, 0.18, 1.0), segments=8)
    make_rot_box("VisitorChair_Throw", (cx-0.30, cy+0.02, 0.76), (0.18, 0.44, 0.06), COL_THROW, roll=0.0, pitch=0.35)
    # Small bedside table (warm wood top)
    tx, ty = +0.95, 4.60      # beside the bed's head (2026-09-10: the bed moved to the N wall)
    make_box("BedTable_Top", (tx, ty, 0.74), (0.52, 0.42, 0.04), COL_DRESSER)
    make_cyl("BedTable_Pole", (tx, ty, 0.37), 0.025, 0.70, COL_MEDICAL)
    make_box("BedTable_Shelf", (tx, ty, 0.40), (0.46, 0.36, 0.03), COL_DRESSER)
    # Glass of water + photo frame on bedside table
    make_lathe("WaterGlass", (tx-0.16, ty, 0.76), [(0.0, 0.0), (0.032, 0.0), (0.04, 0.10), (0.0, 0.10)], (0.78, 0.84, 0.86, 0.55), segments=10)
    make_box("PhotoFrame", (tx-0.18, ty+0.16, 0.84), (0.14, 0.02, 0.16), (0.46, 0.34, 0.22, 1.0))   # (draft 3: NW corner, off the book)
    # Bedside lamp (draft 3: the kit lamp — base, column, shade, bulb;
    # its practical BedLamp_Column_Practical sits at the column's top)
    make_lamp("BedLamp", tx+0.02, ty+0.10, base_z=0.76, h=0.44, shade_col=COL_LAMP_SHADE, body_col=(0.46, 0.34, 0.22, 1.0))
    # A vase of flowers — ON THE DRESSER (draft 3: the vase floated on
    # a sill that did not exist, inside the rose's votive; the stems
    # stood in the air over the bed table)
    make_lathe("Vase_Body", (-2.60, 3.30, 0.94), [(0.0, 0.0), (0.04, 0.0), (0.055, 0.06), (0.04, 0.13), (0.03, 0.16), (0.0, 0.16)], COL_VASE, segments=10)
    for fi, (fx, fy, fh) in enumerate(((0.0, 0.0, 0.22), (0.03, -0.02, 0.18), (-0.025, 0.02, 0.20))):
        make_tube(f"Flower_Stem_{fi}", [(-2.60, 3.30, 1.08), (-2.60 + fx * 1.5, 3.30 + fy * 1.5, 1.08 + fh)], 0.004, COL_PLANT_LEAF, segments=4)
        make_lathe(f"Flower_Bloom_{fi}", (-2.60 + fx * 1.5, 3.30 + fy * 1.5, 1.08 + fh), [(0.0, 0.0), (0.03, 0.01), (0.035, 0.03), (0.02, 0.045), (0.0, 0.05)], COL_FLOWER[fi], segments=8)
    # Small dresser against the W wall
    dxx, dyy = -2.62, 3.40
    make_box("Dresser_Body", (dxx, dyy, 0.44), (0.50, 1.00, 0.88), COL_DRESSER)
    make_box("Dresser_Top", (dxx, dyy, 0.90), (0.54, 1.04, 0.04), (0.46, 0.34, 0.22, 1.0))
    for di in range(3):
        dz = 0.22 + di*0.24
        make_box(f"Dresser_Drawer_{di}", (dxx+0.24, dyy, dz), (0.02, 0.90, 0.20), (0.48, 0.36, 0.24, 1.0))
        make_box(f"Dresser_Pull_{di}", (dxx+0.26, dyy, dz), (0.02, 0.14, 0.03), (0.72, 0.60, 0.34, 1.0))
    # A folded runner cloth + a small framed photo on the dresser top
    make_box("Dresser_Runner", (dxx, dyy, 0.93), (0.44, 0.60, 0.02), COL_BLANKET)
    make_box("Dresser_Photo", (dxx-0.02, dyy+0.28, 1.02), (0.14, 0.02, 0.16), (0.46, 0.34, 0.22, 1.0))
    # Gentle wall crucifix on the W wall above the dresser
    make_box("Cross_Vert", (-2.89, dyy, 1.75), (0.03, 0.06, 0.34), (0.46, 0.34, 0.22, 1.0))
    make_box("Cross_Horiz", (-2.89, dyy, 1.80), (0.03, 0.24, 0.06), (0.46, 0.34, 0.22, 1.0))
    # Plant by window
    make_floor_plant("Plant", (-2.50, ROOM_D-0.50, 0.0), palette={"leaf": COL_PLANT_LEAF})
    make_wall_clock("Clock", (-2.95, 1.5, 2.10), frozen_hour=4, frozen_min=15)
    make_faded_poster("Poster", (+2.95, 2.0, 1.50), palette={"body": (0.80, 0.70, 0.52, 1.0)})

def build_ceiling_infra():
    for j, ypos in enumerate([1.8, 3.8]):
        make_smoke_detector("Smoke", (0.0, 2.5, CEIL))
    make_sprinkler("Spr", (-1.0, 2.5, CEIL))

def build_hero_props():
    """2026-08-03 tail pass: the single white rose in its votive
    glass ON THE SILL, the sink + the under-cabinet light that is
    the scene's only light, the unidentified-beach print above the
    bed, the Book of Common Prayer, the swab dispenser + bent
    straw, the unworn slippers."""
    # The rose (single bloom) in the votive glass on the north sill
    # (draft 3: on the sill, which exists now — z 0.90)
    make_lathe("Rose_Votive", (WIN_X, 5.36, 0.90), [(0.0, 0.0), (0.03, 0.0), (0.035, 0.09), (0.0, 0.09)], (0.80, 0.84, 0.86, 0.5), segments=8)
    make_cyl("Rose_Stem", (WIN_X, 5.36, 1.01), 0.005, 0.14, (0.30, 0.42, 0.28, 1.0), segments=5)
    make_lathe("Rose_Bloom", (WIN_X, 5.36, 1.08), [(0.0, 0.0), (0.02, 0.005), (0.028, 0.025), (0.022, 0.04), (0.0, 0.045)], (0.94, 0.93, 0.90, 1.0), segments=8)
    # Sink + cabinet + the under-cabinet light, east wall (draft 3: a
    # gooseneck at the basin)
    make_box("Sink_Counter", (2.40, 4.60, 0.45), (0.9, 0.55, 0.90), (0.72, 0.70, 0.66, 1.0))
    make_box("Sink_Basin", (2.40, 4.60, 0.91), (0.42, 0.36, 0.05), (0.86, 0.86, 0.84, 1.0))
    make_tube("Sink_Faucet", [(2.66, 4.60, 0.935), (2.66, 4.60, 1.12), (2.58, 4.60, 1.16), (2.50, 4.60, 1.10)], 0.012, (0.80, 0.82, 0.84, 1.0), segments=6)
    make_box("Sink_Cabinet", (2.725, 4.60, 1.70), (0.35, 0.55, 0.60), (0.66, 0.62, 0.56, 1.0))   # on the E wall (2026-09-23: 2.5 cm off it)
    make_box("UnderCab_Light", (2.505, 4.60, 1.395), (0.30, 0.45, 0.03), (0.98, 0.90, 0.72, 1.0))
    # The beach print — on the west wall by the clock (draft 3: over
    # the bed it hung inside the window's opening)
    make_box("Beach_Print_Frame", (-2.88, 2.2, 1.70), (0.04, 0.70, 0.50), (0.42, 0.36, 0.28, 1.0))
    make_box("Beach_Print_Sky", (-2.855, 2.2, 1.80), (0.03, 0.60, 0.24), (0.66, 0.74, 0.78, 1.0))
    make_box("Beach_Print_Sand", (-2.855, 2.2, 1.59), (0.03, 0.60, 0.18), (0.78, 0.70, 0.54, 1.0))
    # The Book of Common Prayer, closed, doing its quiet work on the
    # bed table (draft 3: the SE corner — it sat in the lamp's base)
    make_box("Prayer_Book", (1.10, 4.50, 0.785), (0.13, 0.19, 0.04), (0.24, 0.20, 0.28, 1.0))
    # Mouth-swab dispenser + the bent straw
    make_box("Swab_Dispenser", (0.85, 4.46, 0.83), (0.10, 0.07, 0.14), (0.86, 0.88, 0.90, 0.8))
    make_cyl("Bent_Straw_Lower", (0.79, 4.60, 0.90), 0.006, 0.10, (0.90, 0.90, 0.92, 1.0), segments=5)
    make_box("Bent_Straw_Upper", (0.81, 4.58, 0.965), (0.012, 0.012, 0.06), (0.90, 0.90, 0.92, 1.0))
    # The slippers by the door, three weeks unworn
    make_box("Slipper_L", (-0.75, 0.35, 0.03), (0.10, 0.26, 0.05), (0.66, 0.58, 0.50, 1.0))
    make_box("Slipper_R", (-0.55, 0.32, 0.03), (0.10, 0.26, 0.05), (0.66, 0.58, 0.50, 1.0))



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
    """D4 use states (2026-08-09): mid-vigil, not showroom. The
    visitor's paperback face-down on the chair, water with a straw,
    the spare blanket, slippers not quite squared, the nurse's
    clipboard at the door."""
    wood = (0.40, 0.28, 0.18, 1.0)
    # Water glass with straw on the bedside table (drinks are round)
    # (draft 3: the second glass floated at z 0.62 beside the bed — the
    # hero glass with the bent straw is the water)
    # The visitor's paperback, face-down and splayed on the chair seat
    make_box("Chair_Paperback", (-1.85, 4.92, 0.56), (0.13, 0.19, 0.025),
             (0.62, 0.54, 0.40, 1.0))
    make_box("Chair_Paperback_Pages", (-1.85, 4.92, 0.545), (0.12, 0.18, 0.012),
             (0.90, 0.88, 0.80, 1.0))
    # Spare blanket folded at the bed's foot, one corner off-square
    # (draft 3: draped over the foot panel — it floated 70 cm south of
    # the bed at bed height)
    make_chamfer_box("Spare_Blanket", (0.0, 3.05, 0.92), (0.55, 0.20, 0.06),
                     (0.58, 0.62, 0.58, 1.0), chamfer=0.015)
    make_box("Spare_Blanket_Corner", (0.22, 3.12, 0.96), (0.18, 0.10, 0.02),
             (0.54, 0.58, 0.54, 1.0))
    # (the second pair of slippers is gone — canon has one pair, by
    # the door, three weeks unworn)
    # The nurse's clipboard hanging at the door
    # on the wall beside the doorway (2026-09-23: in the open doorway — the
    # room has no door leaf)
    make_box("Door_Clipboard", (-1.25, 0.11, 1.35), (0.24, 0.02, 0.32), wood)
    make_box("Door_Clipboard_Sheet", (-1.25, 0.1225, 1.34), (0.20, 0.005, 0.26),
             (0.92, 0.92, 0.88, 1.0))
    # Erica's unsent thank-you: an envelope square on the dresser
    make_box("Dresser_Envelope", (-2.60, 3.25, 0.895), (0.16, 0.11, 0.008),
             (0.90, 0.88, 0.80, 1.0))

def build_draft3_2026_09():
    """DRAFT 3 (2026-09-19) · three weeks of a vigil, the cords, the
    garden. No part name carries a cue word (rose · chair)."""
    wear = (COL_FLOOR[0] * 0.86, COL_FLOOR[1] * 0.86, COL_FLOOR[2] * 0.86, 1.0)
    cord = (0.40, 0.40, 0.42, 1.0)
    make_floor_stain("Wear_Visitor", (-1.90, 4.50), radius=0.28, tint=wear, segments=10)
    make_cyl("Wear_Table_Ring", (0.79, 4.50, 0.761), 0.042, 0.002, (0.48, 0.38, 0.28, 1.0), segments=10)
    # (2026-09-23: a door-kick scuff hung across the open doorway — there is
    # no door for it to be on; removed)
    make_box("Wear_Arm_Shine", (-1.60, 5.00, 0.7515), (0.06, 0.30, 0.003), (0.66, 0.46, 0.40, 1.0))
    # D3 · the monitor's cord to the north-east outlet, the lamp's cord
    # off the table's back to the same wall
    make_wall_outlet("Outlet_N_1", (-1.6, ROOM_D), axis='X', face_sign=-1, z=0.30, aged=True)
    make_tube("Cord_1", [(-1.0, 4.46, 0.10), (-1.0, 5.20, 0.10)], 0.008, cord, segments=5)
    make_tube("Cord_1b", [(-1.0, 5.20, 0.10), (-1.6, ROOM_D - 0.13, 0.30)], 0.008, cord, segments=5)
    make_wall_outlet("Outlet_N_2", (1.6, ROOM_D), axis='X', face_sign=-1, z=0.30, aged=True)
    make_tube("Cord_2", [(0.97, 4.82, 0.76), (0.97, 4.82, 0.10)], 0.008, cord, segments=5)
    make_tube("Cord_2b", [(0.97, 4.82, 0.10), (1.6, ROOM_D - 0.13, 0.30)], 0.008, cord, segments=5)
    # D5 · the hospice garden past the window
    make_box("Garden_Lawn", (0.0, ROOM_D + 4.5, -0.03), (14.0, 8.0, 0.05), (0.36, 0.46, 0.28, 1.0))
    make_box("Garden_Path", (0.0, ROOM_D + 1.2, -0.005), (14.0, 1.0, 0.02), (0.60, 0.56, 0.48, 1.0))
    make_box("Garden_Hedge", (0.0, ROOM_D + 8.2, 0.55), (14.0, 0.6, 1.1), (0.22, 0.34, 0.20, 1.0))
    make_broadleaf("Garden_Birch", 2.8, ROOM_D + 4.0, 5.0, (0.44, 0.56, 0.32, 1.0), (0.86, 0.86, 0.80, 1.0), crown=0.30)
    make_chamfer_box("Garden_Bench_Seat", (-2.2, ROOM_D + 3.0, 0.44), (1.40, 0.36, 0.05), (0.46, 0.34, 0.22, 1.0), chamfer=0.01)
    for bx in (-2.75, -1.65):
        make_box(f"Garden_Bench_Leg_{bx:+.2f}", (bx, ROOM_D + 3.0, 0.21), (0.05, 0.32, 0.42), (0.30, 0.22, 0.14, 1.0))
    make_box("Garden_Far_Trees", (0.0, ROOM_D + 12.0, 3.0), (30.0, 0.6, 6.0), (0.18, 0.28, 0.20, 1.0))


def main():
    clear_scene(); build_shell(); build_hospital_bed(); build_iv_stand_and_monitor(); build_visitor_chair_and_decor(); build_ceiling_infra()
    build_hero_props()
    build_detail_pass_2026_08()
    build_use_states_d4()
    build_draft3_2026_09()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/hospice_room.glb"))
    print(f"\n[build_hospice_room] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
