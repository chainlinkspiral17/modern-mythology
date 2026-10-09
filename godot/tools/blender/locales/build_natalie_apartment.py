"""RELOCATED (canon): Simons, Gulf Coast parish walk-up — not San Francisco.
VOL 5 · Natalie's Apartment — Empress chapter (vol5_ch3).

PLACEMENT SCRIPT (uses _props/* library).

Canon: Natalie's small one-bedroom in San Francisco. Empress beat:
where John and Natalie made the choice. Used in 3 vol5 scenes
across chapters 3 + Empress cameos.

Footprint:
  Interior X ∈ [-3.5, +3.5], Y ∈ [0, +5.5], ceiling Z=2.60
  Front door south centre
  Living-area south half (sofa, coffee table, bookshelf)
  Kitchenette north-west (counter, sink, fridge)
  Bed nook north-east, low partition wall
  Tall window west wall — afternoon sun

Run:
    blender --background --python build_natalie_apartment.py

Output:
    godot/assets/3d/locales/natalie_apartment.glb

DRAFT 3 (2026-09-19, lore/_VISUAL_PROGRAM.md §3 backgrounds pass — the
first arcana set of the primitive upgrade; 3 VN placements + the
Empress board). LAYOUT the gates never reported: the sofa and coffee
table sat IN the front door's swing (the entry wear line ran through
the sofa); the scarf lamp floated 0.6 m in the air (no table under
it); the twilight quilt floated in the east half over nothing; the
record lay INSIDE the turntable's plinth; the record sleeve stood
half off the stand's top edge; the tarot deck and both dealt cards
lay under the sofa and the low table; the desk chair's seat ran into
the bookshelf; the coffee pots overlapped the phone. The living set
moved east and north out of the doorway, the reading rug and low
table north behind it, the bookshelf up the east wall, the quilt
folded over the sofa's arm, the lamp onto a side table. PRIMITIVES:
the sofa as chamfered cushions with rolled arms; the coffee table
and side table from the kit; the writing chair a kit chair; the desk
on turned legs; the nightstand lamp and scarf lamp as kit lamps; the
faucet a gooseneck; the kettle a profile; the platter, spindle and
tonearm as profiles. WEAR: her end of the sofa, the kettle path from
the rug to the counter, the desk's edge, the stove-front drip. D3:
the turntable's cord, the scarf lamp's cord, the kettle-side outlet.
D5: past the west window the neighbour's brick wall with one lit
window and the live oak's canopy; past the south-east window the
parish street, a far facade and its lamp. Scene: the free-floating
Practical_Lamp (nothing at 1.6, 1.6) becomes the under-cabinet
light's practical; shot_insert_deck re-aimed at the moved deck.
DRAFT 4 (2026-10-09): the futon (it was a sofa); the coat hook and
coat, the closet, THE SPARE CORNER (stove-to-bed nook: boxes, rug, the
record crate) Judgement clears for a crib; Hanged's dance shoes, leaning
book stacks and herb teacups; Moon's low candle (+ practical) and a deck
fanned on the floor — build_draft4_2026_10.
Draft 5 targets: the crib corner as a variant; a bedroom through a
doorway (a one-bedroom, not a nook); and from draft 4's list:
the L-counter's corner as one piece; the fridge's
seam, magnets and a photo; the blinds' cord; a second bookshelf
row of objects (a photo, a candle) so the shelf is hers; Deck: the
SW preset for the moved living set + establish_b.
"""
import os, sys, math
_BLENDER_TOOLS = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BLENDER_TOOLS not in sys.path:
    sys.path.insert(0, _BLENDER_TOOLS)

from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_chamfer_box, make_lathe, make_tube, make_blob, make_rot_box, export_glb
from _props.furniture import make_table, make_chair, make_lamp
from _props.structure import (make_wall_with_openings, 
    make_floor, make_wall, make_ceiling, make_window,
    make_crown_molding, make_door_hinges,
)
from _props.store_fixtures import make_counter, make_counter_bullnose
from _props.food_service import make_coffee_pots
from _props.decor import (
    make_wall_clock, make_floor_plant, make_faded_poster,
)
from _props.safety import (
    make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture,
)
from _props.detail import (make_floor_stain, make_traffic_wear, make_wall_outlet, make_wall_tint_band, make_scuff_band)
from _props.objects import make_mug


# Natalie's apartment palette — soft cream walls, warm wood floor,
# muted rose accents (her signature color), dusty teal couch.
PAL_APT_WALL = {
    "wall":      (0.92, 0.88, 0.82, 1.0),    # warm cream
    "baseboard": (0.62, 0.46, 0.30, 1.0),
}
PAL_APT_COUNTER = {
    "formica": (0.86, 0.78, 0.62, 1.0),       # honey laminate
    "top":     (0.32, 0.22, 0.16, 1.0),       # dark walnut
    "kick":    (0.32, 0.22, 0.16, 1.0),
}
COL_FLOOR_OAK     = (0.74, 0.58, 0.38, 1.0)
COL_FLOOR_OAK_SM  = (0.42, 0.30, 0.18, 1.0)
COL_COUCH_TEAL    = (0.42, 0.56, 0.58, 1.0)
COL_COUCH_TRIM    = (0.28, 0.38, 0.42, 1.0)
COL_ACCENT_ROSE   = (0.86, 0.62, 0.62, 1.0)
COL_WOOD_TRIM     = (0.46, 0.34, 0.22, 1.0)
COL_BED_LINEN     = (0.92, 0.86, 0.78, 1.0)
COL_BED_FRAME     = (0.36, 0.28, 0.20, 1.0)
COL_BOOK_SPINES   = [
    (0.62, 0.32, 0.30, 1.0),
    (0.42, 0.52, 0.62, 1.0),
    (0.56, 0.48, 0.32, 1.0),
    (0.32, 0.42, 0.32, 1.0),
    (0.74, 0.58, 0.30, 1.0),
    (0.42, 0.32, 0.42, 1.0),
]

ROOM_W = 7.0
ROOM_D = 5.5
CEIL_Z = 2.60
# draft 3 · the living set's anchors (sofa centre); the rug + low table
# sit north of the sofa's back
SOFA_X, SOFA_Y = 0.30, 1.70
RUG_X, RUG_Y = -0.60, 2.90
SHELF_Y = 2.20


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0),
               size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_FLOOR_OAK, "seam": COL_FLOOR_OAK_SM})
    # (2026-10-03: the walls behind the windows are CUT — they were solid)
    make_wall_with_openings("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0),
              length=ROOM_D + 0.4, height=CEIL_Z, axis='Y',
              palette=PAL_APT_WALL, baseboard_face_sign=+1,
              openings=[(2.5, 1.45, 1.70, 1.70)])
    make_wall("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0),
              length=ROOM_D + 0.4, height=CEIL_Z, axis='Y',
              palette=PAL_APT_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N", (0.0, ROOM_D, 0),
              length=ROOM_W + 0.4, height=CEIL_Z, axis='X',
              palette=PAL_APT_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-2.30, 0.0, 0),   # to the door edge the hinges mark (2026-09-23: 40 cm short)
              length=2.40, height=CEIL_Z, axis='X',
              palette=PAL_APT_WALL, baseboard_face_sign=+1)
    make_wall_with_openings("Wall_S_E", (+2.30, 0.0, 0),
              length=2.40, height=CEIL_Z, axis='X',
              palette=PAL_APT_WALL, baseboard_face_sign=+1,
              openings=[(2.0, 1.40, 1.40, 1.20)])
    # the opening is x -1.10..1.10 and the leaf -1.10..-0.20: the wall
    # closes the 1.3 m of daylight east of it, under Wall_S_AboveDoor
    # (2026-09-25, doorway_audit OPENING)
    make_wall("Wall_S_DoorFill_E", (0.45, 0.0, 0),
              length=1.30, height=CEIL_Z - 0.60, axis='X',
              palette=PAL_APT_WALL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL_Z - 0.30),
             (3.00, 0.20, 0.60), PAL_APT_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL_Z),
                 size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4, with_grid=False)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W / 2.0 + 0.10, ROOM_D / 2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W / 2.0 - 0.10, ROOM_D / 2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D - 0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy,
                           length=length, axis=ax, ceil_z=CEIL_Z,
                           palette={"wood": COL_WOOD_TRIM})
    # Tall west window (afternoon sun)
    # on the wall's room face, glass in front of the frame (2026-09-24: frame and glass
    # were offset from the wall's CENTRE line — inside the wall, never visible)
    # (2026-10-03: the frame was a solid plate behind the glass — four bars)
    for nm, fy, fz, sy, sz in (("Window_W_Frame_T", 2.5, 2.32, 1.80, 0.06), ("Window_W_Frame_B", 2.5, 0.58, 1.80, 0.06),
                               ("Window_W_Frame_S", 1.63, 1.45, 0.06, 1.80), ("Window_W_Frame_N", 3.37, 1.45, 0.06, 1.80),
                               ("Window_W_Mullion", 2.5, 1.45, 0.04, 1.70)):
        make_box(nm, (-ROOM_W / 2.0 + 0.12, fy, fz), (0.04, sy, sz), P.METAL_STEEL)
    make_box("Window_W_Glass", (-ROOM_W / 2.0 + 0.1425, 2.5, 1.45),
             (0.005, 1.70, 1.70), P.GLASS_WARM)
    # South window beside door
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    make_window("Window_SE", (+2.00, 0.10, 1.40),
                width=1.40, height=1.20, room_dir=+1)
    # Door hinges
    make_door_hinges("FrontDoor_Hinge", edge_x=-1.10, edge_y=0.0,
                     edge_z_centers=[0.30, 1.05, 1.80], axis='X')


def build_living_room():
    # Sofa — faces south to the coffee table and the door (draft 3:
    # chamfered cushions, rolled arms; moved east + north out of the
    # door's swing)
    sx, sy = SOFA_X, SOFA_Y
    # DRAFT 4 (2026-10-09): THE FUTON — "Nicola had slept, immediately, on
    # the futon, under the twilight-colored quilt" (Moon). Drafts 1-3 built
    # a teal sofa: now a low slatted wood frame, the teal mattress folded
    # into seat and back, wooden arms.
    make_chamfer_box("Sofa_Base", (sx, sy, 0.14), (1.80, 0.80, 0.28), COL_BED_FRAME, chamfer=0.01)
    for si in range(5):
        make_box(f"Futon_Front_Slat_{si}", (sx - 0.72 + si * 0.36, sy - 0.405, 0.14), (0.26, 0.012, 0.20), COL_WOOD_TRIM)
    make_chamfer_box("Futon_Seat_Cushion", (sx, sy - 0.04, 0.355), (1.72, 0.70, 0.17), COL_COUCH_TEAL, chamfer=0.05)
    make_chamfer_box("Sofa_Back", (sx, sy + 0.30, 0.74), (1.72, 0.18, 0.62), COL_COUCH_TEAL, chamfer=0.05)
    for ti, tz in enumerate((0.58, 0.88)):
        make_box(f"Futon_Back_Rail_{ti}", (sx, sy + 0.40, tz), (1.72, 0.03, 0.06), COL_BED_FRAME)
    for ci, cx in enumerate((-0.43, 0.43)):
        make_box(f"Futon_Tuft_{ci}", (sx + cx, sy - 0.04, 0.4415), (0.04, 0.04, 0.003), COL_COUCH_TRIM)
    for cs in (-1, +1):
        make_box(f"Sofa_Arm_{cs:+d}", (sx + cs * 0.94, sy, 0.3575), (0.16, 0.80, 0.715), COL_BED_FRAME)
        make_box(f"Futon_Arm_Cap_{cs:+d}", (sx + cs * 0.94, sy, 0.725), (0.18, 0.84, 0.02), COL_WOOD_TRIM)
    # Throw pillows (rose accent)
    for pi, px in enumerate([-0.50, +0.30, +0.70]):
        make_chamfer_box(f"Sofa_Pillow_{pi}", (sx + px, sy + 0.10, 0.53), (0.30, 0.20, 0.18), COL_ACCENT_ROSE, chamfer=0.03)   # on the cushions
    # Coffee table (draft 3: the kit table, turned legs and an apron)
    make_table("CoffeeTable", sx + 0.15, sy - 0.80, w=1.20, d=0.60, h=0.40, wood=COL_WOOD_TRIM)   # out of the front door's swing (2026-09-24, the user: "doorways obstructed")
    # Mug + book on coffee table
    make_cyl("Mug", (sx - 0.15, sy - 0.80, 0.45), 0.05, 0.10, COL_ACCENT_ROSE)
    make_box("Book", (sx + 0.30, sy - 0.80, 0.42), (0.20, 0.28, 0.04), COL_BOOK_SPINES[0])
    # Bookshelf along east wall (draft 3: at y 2.2 — at 1.5 its side ran
    # into the writing chair)
    sx2 = +3.04   # its back on the E wall's face (2026-09-25: 14 cm off it)
    make_box("Bookshelf_Side_L", (sx2 - 0.36, SHELF_Y, 1.00),
             (0.04, 0.36, 2.00), COL_BED_FRAME)
    make_box("Bookshelf_Side_R", (sx2 + 0.36, SHELF_Y, 1.00),
             (0.04, 0.36, 2.00), COL_BED_FRAME)
    for shf in range(5):
        sz = 0.20 + shf * 0.42
        make_box(f"Bookshelf_Shelf_{shf}", (sx2, SHELF_Y, sz),
                 (0.76, 0.36, 0.02), COL_BED_FRAME)
        for bi in range(6):
            bx = sx2 - 0.30 + bi * 0.12
            spine = COL_BOOK_SPINES[(shf * 2 + bi) % len(COL_BOOK_SPINES)]
            make_box(f"Bookshelf_Book_{shf}_{bi}",
                     (bx, SHELF_Y, sz + 0.16),
                     (0.10, 0.28, 0.30), spine)


def build_kitchenette():
    # Small kitchenette north-west — L-shaped counter
    top_z = make_counter("Kitchen_W", (-3.0, 4.20, 0.0),
                         length=1.80, depth=0.70, height=0.92,
                         palette=PAL_APT_COUNTER)
    # Sink
    make_box("Kitchen_Sink", (-3.0, 4.20, 0.86),
             (0.50, 0.40, 0.12), P.METAL_STEEL)
    make_tube("Kitchen_Faucet", [(-3.18, 4.20, top_z), (-3.18, 4.20, top_z + 0.24), (-3.06, 4.20, top_z + 0.30), (-2.96, 4.20, top_z + 0.22)], 0.014, P.METAL_STEEL, segments=6)
    make_lathe("Kitchen_Faucet_Base", (-3.18, 4.20, top_z), [(0.03, 0.0), (0.03, 0.02), (0.018, 0.03), (0.0, 0.03)], P.METAL_STEEL, segments=8)
    # Counter run east — under fridge
    make_box("Kitchen_Counter_N", (-1.50, 5.050, 0.46),
             (2.40, 0.70, 0.92), PAL_APT_COUNTER["formica"])
    # (2026-10-02: the slab was centred ON top_z, so it stood 0.95..1.01 while
    # the west counter's top is 0.92..0.98 — the phone and the mug were inside it)
    make_box("Kitchen_Counter_N_Top", (-1.50, 5.050, top_z - 0.03),
             (2.50, 0.80, 0.06), PAL_APT_COUNTER["top"])
    # Stove
    make_box("Stove_Body", (0.05, 5.050, 0.46),
             (0.70, 0.70, 0.92), (0.86, 0.84, 0.80, 1.0))
    make_box("Stove_Top", (0.05, 5.05, 0.94),
             (0.70, 0.70, 0.04), P.METAL_BLACK)
    for bi, (bx, by) in enumerate([
            (-0.15, 4.90), (0.25, 4.90), (-0.15, 5.20), (0.25, 5.20)]):
        make_cyl(f"Stove_Burner_{bi}", (bx, by, 0.96),
                 0.08, 0.02, P.METAL_STEEL)
    # Coffee pots on the counter
    make_coffee_pots("Coffee", (-2.35, 5.20, top_z), pots=1)   # (draft 3: west, off the phone)
    # Fridge — east end of counter run
    make_box("Fridge_Body", (-3.05, 0.480, 1.00),   # SW corner, door to the room (2026-09-25: between the stove and the bed it left 30 cm to make the bed by; the NW corner is the counters' L)
             (0.70, 0.70, 2.00), (0.86, 0.84, 0.80, 1.0))
    make_box("Fridge_Handle", (-2.69, 0.28, 1.40),
             (0.03, 0.04, 0.10), P.METAL_STEEL)


def build_bed_nook():
    # Bed in north-east corner with low partition
    bx, by = +2.20, 4.50
    # Low partition (visual separator)
    make_box("Partition", (+0.80, 4.20, 0.60),
             (0.04, 0.80, 1.20), COL_WOOD_TRIM)
    # the shared bed in the nook, rose throw as the made blanket (2026-09-07)
    from _props.furniture import make_bed
    make_bed("Bed", bx, by, head="+Y", w=1.50, d=1.90, style="platform",
             frame_col=COL_BED_FRAME, mattress_col=COL_BED_LINEN, sheet_col=COL_BED_LINEN,
             blanket_col=COL_ACCENT_ROSE, pillow_col=P.PAPER, pillows=2, made=True, headboard=False)
    # Nightstand
    make_box("Nightstand", (bx + 0.90, by + 0.20, 0.36),
             (0.40, 0.36, 0.72), COL_WOOD_TRIM)
    # Lamp on nightstand
    make_lamp("Nightstand_Lamp", bx + 0.90, by + 0.20, base_z=0.72, h=0.50, shade_col=COL_BED_LINEN, body_col=P.METAL_BLACK)


def build_decor():
    # clear of the window (2026-09-24: once the clock faced the room it overlapped it)
    make_wall_clock("Clock", (-3.400, 3.65, 2.10),
                    frozen_hour=4, frozen_min=22, facing='+X')
    make_faded_poster("Poster_W", (-3.3965, 1.15, 1.40), into_room=+1)
    make_faded_poster("Poster_E", (3.3965, 4.5, 1.50),
                      palette={"body": COL_ACCENT_ROSE}, into_room=-1)
    make_floor_plant("Plant", (-2.5, 1.50, 0.0),
                     palette={"leaf": (0.42, 0.56, 0.42, 1.0)})


def build_ceiling_infra():
    # Candle-and-lamp apartment: no tubes; the under-cabinet strip,
    # the scarf lamp and the blinds' moonlight carry the room
    make_smoke_detector("Smoke", (0.0, 3.0, CEIL_Z))
    make_hvac_vent("HVAC", (-1.0, 5.0, CEIL_Z), width=0.60, depth=0.30)


def build_hero_props():
    """2026-08-03 tail pass: THE DUAL 1219 record player, the
    windowsill (the Hanged Man lives on it), the kettle, the rug +
    the low reading table + fanned cards, the under-cabinet light
    (the apartment's you're-welcome lamp), the futon quilt, the
    step-stool, the scarf lamp, the blinds."""
    # The Dual turntable on its stand, west corner
    make_box("Turntable_Stand", (-3.00, 1.90, 0.30), (0.50, 0.42, 0.60), (0.36, 0.26, 0.17, 1.0))
    make_box("Turntable_Plinth", (-3.00, 1.90, 0.66), (0.42, 0.36, 0.10), (0.30, 0.22, 0.14, 1.0))
    # (draft 3: platter, spindle, tonearm pivot + arm as profiles)
    make_lathe("Turntable_Platter", (-3.03, 1.90, 0.71), [(0.0, 0.0), (0.15, 0.0), (0.155, 0.02), (0.14, 0.03), (0.0, 0.03)], (0.12, 0.12, 0.13, 1.0), segments=14)
    make_cyl("Turntable_Spindle", (-3.03, 1.90, 0.755), 0.004, 0.03, (0.60, 0.62, 0.63, 1.0), segments=6)
    make_lathe("Turntable_Pivot", (-2.84, 2.03, 0.71), [(0.025, 0.0), (0.025, 0.05), (0.0, 0.05)], (0.60, 0.62, 0.63, 1.0), segments=8)
    make_tube("Turntable_Tonearm", [(-2.84, 2.03, 0.765), (-2.90, 1.98, 0.765), (-3.00, 1.86, 0.752)], 0.006, (0.60, 0.62, 0.63, 1.0), segments=5)
    # The windowsill + the Hanged Man face-up on it
    make_box("W_Sill", (-3.32, 2.5, 0.55), (0.16, 1.90, 0.05), (0.42, 0.30, 0.20, 1.0))
    make_box("HangedMan_Card", (-3.32, 2.20, 0.585), (0.10, 0.07, 0.002), (0.86, 0.82, 0.70, 1.0))
    make_box("HangedMan_Figure", (-3.32, 2.20, 0.587), (0.03, 0.045, 0.002), (0.30, 0.34, 0.52, 1.0))
    # The kettle on the front burner
    make_lathe("Kettle", (-0.68, 4.95, 0.98), [(0.0, 0.0), (0.085, 0.0), (0.095, 0.05), (0.09, 0.13), (0.06, 0.16), (0.035, 0.165), (0.035, 0.18), (0.0, 0.18)], (0.62, 0.64, 0.65, 1.0), segments=12)
    make_tube("Kettle_Spout", [(-0.60, 4.95, 1.06), (-0.53, 4.95, 1.13), (-0.50, 4.95, 1.17)], 0.012, (0.62, 0.64, 0.65, 1.0), segments=6)
    make_tube("Kettle_Bail", [(-0.68, 4.89, 1.14), (-0.68, 4.91, 1.23), (-0.68, 4.99, 1.23), (-0.68, 5.01, 1.14)], 0.008, (0.18, 0.17, 0.16, 1.0), segments=5)
    # The worn rug + the low reading table (daytime footstool) +
    # fanned cards
    # (draft 3: the rug + low table north of the sofa's back, y 2.9)
    make_box("Reading_Rug", (RUG_X, RUG_Y, 0.012), (2.20, 1.80, 0.02), (0.46, 0.34, 0.30, 1.0))
    make_box("Rug_Worn_Patch", (RUG_X - 0.80, RUG_Y, 0.024), (0.55, 0.45, 0.006), (0.54, 0.42, 0.36, 1.0))
    make_box("Low_Table", (RUG_X, RUG_Y, 0.146), (0.55, 0.55, 0.248), (0.42, 0.30, 0.20, 1.0))   # a footstool block ON the rug (2026-09-23: a top on nothing)
    for ci in range(5):
        make_box(f"Fanned_Card_{ci}", (RUG_X - 0.15 + ci * 0.09, RUG_Y - 0.18 + 0.02 * (ci % 2), 0.276),
                 (0.07, 0.11, 0.002), (0.86, 0.82, 0.70, 1.0))
    # Upper cabinets + THE under-cabinet light
    make_box("Upper_Cabs", (-1.50, 5.23, 1.85), (2.40, 0.34, 0.70), (0.42, 0.32, 0.24, 1.0))   # on the N wall (2026-09-23: 5 cm off it)
    make_box("UnderCab_Light", (-1.50, 5.09, 1.49), (2.30, 0.06, 0.03), (0.98, 0.90, 0.70, 1.0))
    # Futon-ify: the twilight quilt over the sofa/futon
    # (draft 3: folded over the sofa's east arm — it floated in the air
    # at (2.1, 2.4) with nothing under it)
    make_chamfer_box("Twilight_Quilt", (SOFA_X + 0.94, SOFA_Y, 0.78), (0.34, 0.60, 0.09), (0.34, 0.30, 0.50, 1.0), chamfer=0.03)
    # Step-stool by the bookshelf, the scarf lamp ON a side table (it
    # floated at z 0.6), the blinds
    make_box("Step_Stool", (3.15, 3.55, 0.16), (0.36, 0.30, 0.32), (0.46, 0.34, 0.22, 1.0))
    make_table("Side_Table", 1.15, 0.55, w=0.45, d=0.45, h=0.60, wood=(0.36, 0.26, 0.17, 1.0))
    make_lamp("Scarf_Lamp", 1.15, 0.55, base_z=0.60, h=0.55, shade_col=(0.62, 0.34, 0.44, 0.9), body_col=(0.30, 0.22, 0.14, 1.0))
    make_rot_box("Draped_Scarf", (1.22, 0.50, 1.05), (0.20, 0.16, 0.04), (0.56, 0.28, 0.40, 1.0), yaw=0.4, roll=0.25)
    for bi in range(8):
        make_box(f"Blind_Slat_{bi}", (-3.42, 2.5, 0.80 + bi * 0.14), (0.02, 1.80, 0.03), (0.72, 0.70, 0.64, 1.0))   # in the window (2026-09-23: 13 cm into the room)



def build_detail_pass_2026_08():
    """D2 surface breakup + first D3 (adaptive template pass per
    lore/_SET_DETAIL_PLAYBOOK.md). Per-locale wear personality is
    the next pass."""
    wear = (COL_FLOOR_OAK[0] * 0.88, COL_FLOOR_OAK[1] * 0.88, COL_FLOOR_OAK[2] * 0.88, 1.0)
    # (draft 3: the door's own step-in, then the aisle west of the sofa
    # north to the kitchen — the old line ran through the sofa)
    make_traffic_wear("Wear_Entry", [(-0.65, 0.35), (-0.65, 0.9)], width=0.75, tint=wear)
    make_traffic_wear("Wear_Aisle", [(-1.0, 0.9), (-1.0, 1.9)], width=0.5, tint=wear)
    make_floor_stain("Stain_WorkZone", (ROOM_W * 0.22, ROOM_D * 0.62), radius=0.24,
                     tint=(COL_FLOOR_OAK[0] * 0.82, COL_FLOOR_OAK[1] * 0.82, COL_FLOOR_OAK[2] * 0.82, 1.0))
    pw = PAL_APT_WALL["wall"]
    band = (pw[0] * 0.90, pw[1] * 0.90, pw[2] * 0.88, 1.0)
    make_wall_tint_band("Band_W", (-ROOM_W / 2.0 + 0.105, ROOM_D / 2.0, 0.0),
                        length=ROOM_D - 0.4, axis='Y', band_z=CEIL_Z - 0.16, tint=band)
    make_wall_tint_band("Band_E", (ROOM_W / 2.0 - 0.105, ROOM_D / 2.0, 0.0),
                        length=ROOM_D - 0.4, axis='Y', band_z=CEIL_Z - 0.16, tint=band)
    make_wall_outlet("Outlet_W", (-ROOM_W / 2.0, ROOM_D * 0.35), axis='Y',
                     face_sign=1, aged=True)
    make_wall_outlet("Outlet_E", (ROOM_W / 2.0, ROOM_D * 0.70), axis='Y',
                     face_sign=-1, aged=True)


def build_use_states_d4():
    """D4 use states: the record playing, the reading half-dealt,
    the mug with its ring. A room used at 2am."""
    # (draft 3: the record ON the platter — it lay inside the plinth;
    # the sleeve flat on the floor by the stand — it stood half off it)
    make_cyl("Turntable_Record", (-3.03, 1.9, 0.7425), 0.15, 0.005,
             (0.10, 0.10, 0.11, 1.0), segments=12)
    make_box("Record_Sleeve", (-2.55, 1.90, 0.014), (0.30, 0.30, 0.004),
             (0.50, 0.30, 0.24, 1.0))
    # Tarot: two cards face-up on the rug beside the low table, the
    # deck stacked off-square (draft 3: they lay under the sofa)
    make_box("Tarot_Card_A", (RUG_X - 0.60, RUG_Y - 0.35, 0.024), (0.07, 0.12, 0.004),
             (0.88, 0.84, 0.72, 1.0))
    make_box("Tarot_Card_B", (RUG_X - 0.45, RUG_Y - 0.50, 0.024), (0.07, 0.12, 0.004),
             (0.88, 0.84, 0.72, 1.0))
    make_box("Tarot_Deck", (RUG_X - 0.80, RUG_Y - 0.55, 0.037), (0.075, 0.125, 0.03),
             (0.30, 0.24, 0.38, 1.0))
    make_box("Tarot_Deck_Skew", (RUG_X - 0.795, RUG_Y - 0.555, 0.057), (0.075, 0.125, 0.012),
             (0.32, 0.26, 0.40, 1.0))
    # Coffee mug on the kitchen counter + the ring it left earlier
    make_mug("Counter_Mug", -1.2, 4.95, 0.98, (0.62, 0.28, 0.24, 1.0))
    make_cyl("Counter_MugRing", (-0.95, 4.90, 0.981), 0.045, 0.002,
             (0.38, 0.30, 0.24, 1.0), segments=10)
    # Blanket half-slid off the sofa
    make_chamfer_box("Sofa_Blanket", (SOFA_X - 0.45, SOFA_Y - 0.05, 0.47), (0.55, 0.42, 0.06),
                     (0.46, 0.36, 0.30, 1.0), chamfer=0.02)
    make_chamfer_box("Sofa_Blanket_Drape", (SOFA_X - 0.75, SOFA_Y - 0.25, 0.22), (0.25, 0.30, 0.30),
                     (0.44, 0.34, 0.28, 1.0), chamfer=0.03)

def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    Four distinct cues; the Tarot_Deck exists (marker only). Built:

    - THE DOOR: FrontDoor_Hinges existed WITHOUT A DOOR — the
      apartment door Nicola knocks at now hangs on them, with its
      knob and chain plate.
    - THE DESK ("She sat at her desk and opened, for the first
      time in three years, the little spiral notebook she had
      used for dream-journaling"): a small writing desk under the
      SE window with the dream journal open on it, a pen, and a
      chair facing it.
    - NATALIE'S PHONE ("Her phone, on the kitchen counter, rang"):
      face-up on the north counter, clear of the mug.
    """
    wood = (0.46, 0.34, 0.24, 1.0)
    wood_dk = (0.38, 0.28, 0.19, 1.0)
    # ── THE DOOR · hung on the existing hinges (x -1.10) ──
    make_box("Front_Door", (-0.65, 0.06, 1.05), (0.90, 0.05, 2.10),
             (0.52, 0.40, 0.28, 1.0))
    make_cyl("Front_Door_Knob", (-0.30, 0.105, 1.02), 0.030, 0.040,
             (0.66, 0.56, 0.34, 1.0), axis='Y', segments=8)
    make_box("Front_Door_Chain_Plate", (-0.36, 0.09, 1.45), (0.060, 0.010, 0.030),
             (0.62, 0.62, 0.60, 1.0))
    # ── THE DESK · under the SE window ──
    make_box("Writing_Desk_Top", (2.5, 0.70, 0.74), (0.90, 0.50, 0.04), wood)
    for li2, (lx2, ly2) in enumerate(((2.10, 0.50), (2.90, 0.50),
                                      (2.10, 0.90), (2.90, 0.90))):
        make_lathe(f"Writing_Desk_Leg_{li2}", (lx2, ly2, 0.0), [(0.024, 0.0), (0.028, 0.03), (0.02, 0.08), (0.022, 0.45), (0.03, 0.52), (0.022, 0.60), (0.025, 0.72)], wood_dk, segments=8)
    make_box("Writing_Desk_Apron", (2.5, 0.70, 0.70), (0.82, 0.42, 0.04), wood_dk)
    make_box("Dream_Journal", (2.35, 0.70, 0.766), (0.150, 0.200, 0.012),
             (0.62, 0.54, 0.38, 1.0))
    make_box("Dream_Journal_Wire", (2.266, 0.70, 0.767), (0.010, 0.200, 0.014),
             (0.55, 0.56, 0.58, 1.0))
    make_cyl("Journal_Pen", (2.62, 0.62, 0.7655), 0.005, 0.130,
             (0.24, 0.24, 0.28, 1.0), axis='Y', segments=6)
    # (draft 3: the kit chair, facing the desk; named without the cue
    # word so the desk insert keeps the desk)
    make_chair("Writing_Chair", 2.5, 1.25, yaw=3.14159, wood=wood, w=0.40)
    # ── NATALIE'S PHONE · kitchen counter north (top 0.98) ──
    # (2026-10-02: "Natalies_Phone" carried the closeup-natalie cue word)
    make_box("Her_Phone", (-1.85, 5.05, 0.9855), (0.070, 0.140, 0.011),
             (0.13, 0.13, 0.15, 1.0))


def build_draft3_2026_09():
    """DRAFT 3 (2026-09-19) · wear personality, cords, both windows'
    outsides. No part name carries a cue word (record · player · card
    · deck · phone · door · desk)."""
    wear = (COL_FLOOR_OAK[0] * 0.86, COL_FLOOR_OAK[1] * 0.86, COL_FLOOR_OAK[2] * 0.86, 1.0)
    cord = (0.16, 0.16, 0.18, 1.0)
    # WEAR · her end of the sofa (the west cushion, the reading end),
    # the kettle path from the rug north to the counter, the desk's
    # edge, the stove-front drip
    make_box("Wear_Her_Seat", (SOFA_X - 0.44, SOFA_Y - 0.04, 0.4415), (0.50, 0.44, 0.003), (0.36, 0.48, 0.50, 1.0))
    make_traffic_wear("Wear_Kettle", [(-1.2, RUG_Y + 1.0), (-1.2, 4.5)], width=0.5, tint=wear)
    make_box("Wear_Desk_Edge", (2.5, 0.47, 0.7615), (0.70, 0.05, 0.003), (0.38, 0.28, 0.19, 1.0))
    make_scuff_band("Wear_Stove_Drip", (0.05, 5.05 - 0.356), 0.40, axis='X', height=0.10, band_z=0.55, tint=(0.62, 0.58, 0.52, 1.0))
    # D3 · the turntable's cord to Outlet_W, the scarf lamp's cord to a
    # south-wall outlet, the kettle-side outlet above the counter
    # over the stand's top and down its west face (2026-09-23: a diagonal through the stand)
    make_tube("Cord_1A", [(-3.10, 1.92, 0.61), (-3.265, 1.92, 0.61)], 0.008, cord, segments=5)
    make_tube("Cord_1B", [(-3.265, 1.92, 0.61), (-3.265, 1.925, 0.30)], 0.008, cord, segments=5)
    make_tube("Cord_1C", [(-3.265, 1.925, 0.30), (-3.385, 1.925, 0.30)], 0.008, cord, segments=5)
    make_wall_outlet("Outlet_S_1", (1.60, 0.0), axis='X', face_sign=1, z=0.30, aged=True)
    make_tube("Cord_2", [(1.20, 0.40, 0.60), (1.60, 0.12, 0.30)], 0.008, cord, segments=5)
    make_wall_outlet("Outlet_N_1", (-0.90, ROOM_D), axis='X', face_sign=-1, z=1.15, aged=True)
    make_tube("Cord_3", [(-0.62, 5.02, 1.00), (-0.90, ROOM_D - 0.13, 1.15)], 0.008, cord, segments=5)
    # D5 · past the west window: the neighbour's brick wall, one lit
    # window, the live oak's canopy over the gap; past the SE window:
    # the parish street, a far facade, its lamp
    make_box("Out_W_Ground", (-6.0, 2.75, -0.03), (5.0, 9.0, 0.05), (0.30, 0.30, 0.28, 1.0))
    make_box("Out_W_Wall", (-8.0, 2.75, 3.0), (0.4, 12.0, 6.0), (0.46, 0.32, 0.26, 1.0))
    make_box("Out_W_LitWin", (-7.78, 3.4, 1.6), (0.02, 1.0, 1.2), (0.96, 0.82, 0.52, 1.0))
    make_lathe("Out_W_Oak_Trunk", (-6.2, 4.6, 0.0), [(0.30, 0.0), (0.24, 2.0), (0.18, 3.4), (0.0, 3.4)], (0.30, 0.24, 0.18, 1.0), segments=8)
    make_blob("Out_W_Oak_Canopy", (-6.2, 4.4, 4.6), 2.6, (0.24, 0.34, 0.22, 1.0), noise=0.22, seed=17, squash=0.7)
    make_box("Out_S_Ground", (0.0, -4.0, -0.03), (16.0, 7.0, 0.05), (0.30, 0.30, 0.32, 1.0))
    make_box("Out_S_Facade", (0.0, -8.0, 2.4), (16.0, 0.4, 4.8), (0.52, 0.46, 0.40, 1.0))
    make_lathe("Out_S_Lamp_Pole", (3.2, -3.2, 0.0), [(0.12, 0.0), (0.06, 0.1), (0.05, 3.6), (0.0, 3.6)], (0.28, 0.28, 0.30, 1.0), segments=8)
    make_lathe("Out_S_Lamp_Globe", (3.2, -3.2, 3.6), [(0.0, 0.0), (0.16, 0.06), (0.14, 0.28), (0.0, 0.32)], (0.98, 0.88, 0.66, 1.0), segments=10)


def build_draft4_2026_10():
    """DRAFT 4 (2026-10-09) — the things the prose puts in the room that
    the set did not have. Judgement: "Natalie took off her coat. Hung it
    on the hook. Walked to the closet. Began ... clearing the spare corner
    — the one she had kept, for ten years, as a storage space for things
    she had not, strictly, needed — to make room for a crib." Hanged:
    "a nest woven from discarded dance shoes soft as moth wings, stacks
    of books leaning at precarious Borgesian angles, chipped porcelain
    teacups holding dried herbs, and tarot decks fanned out on the floor
    like fallen leaves." Moon: "the candle she had lit at midnight
    burning low", on the rug among the cards."""
    rose_pale = (0.92, 0.80, 0.78, 1.0)
    porcelain = (0.92, 0.90, 0.86, 1.0)
    # the coat hook by the door and her coat on it
    make_box("Coat_Hook_Rail", (-1.60, 0.115, 1.70), (0.50, 0.03, 0.08), COL_WOOD_TRIM)
    for hi, hx in enumerate((-1.75, -1.45)):
        make_cyl(f"Coat_Hook_{hi}", (hx, 0.16, 1.70), 0.012, 0.06, P.METAL_BLACK, axis='Y', segments=6)
    make_chamfer_box("Her_Coat", (-1.75, 0.20, 1.24), (0.44, 0.08, 0.90), (0.30, 0.28, 0.34, 1.0), chamfer=0.03)
    make_box("Her_Coat_Collar", (-1.75, 0.20, 1.68), (0.20, 0.08, 0.06), (0.26, 0.24, 0.30, 1.0))
    # her work shoes under it, and the soft dance shoes kicked off in the aisle
    for si, (sx_, sy_) in enumerate(((-1.85, 0.30), (-1.66, 0.32))):
        make_chamfer_box(f"Work_Shoe_{si}", (sx_, sy_, 0.04), (0.10, 0.26, 0.08), P.METAL_BLACK, chamfer=0.02)
    for si, (sx_, sy_, yaw) in enumerate(((-1.30, 1.50, 0.5), (-1.15, 1.66, -0.3))):
        make_rot_box(f"Dance_Shoe_{si}", (sx_, sy_, 0.025), (0.08, 0.22, 0.05), rose_pale, yaw=yaw)
    # the closet on the E wall between the bookshelf and the step-stool
    make_box("Closet_Door", (ROOM_W / 2.0 - 0.125, 3.10, 1.00), (0.05, 0.70, 2.00), (0.86, 0.82, 0.74, 1.0))
    make_box("Closet_Door_Casing", (ROOM_W / 2.0 - 0.105, 3.10, 2.04), (0.02, 0.80, 0.08), COL_WOOD_TRIM)
    make_cyl("Closet_Door_Knob", (ROOM_W / 2.0 - 0.17, 2.85, 0.98), 0.025, 0.04, (0.72, 0.62, 0.36, 1.0), axis='X', segments=8)
    # THE SPARE CORNER: the dead nook between the stove and the bed, ten years of storage
    for bi, (bx, by, bz, w, d, h) in enumerate(((0.70, 5.05, 0.20, 0.55, 0.50, 0.40), (0.72, 5.05, 0.60, 0.50, 0.46, 0.40),
                                               (1.12, 5.12, 0.18, 0.30, 0.42, 0.36))):
        make_box(f"Spare_Box_{bi}", (bx, by, bz), (w, d, h), (0.66, 0.54, 0.40, 1.0))
        make_box(f"Spare_Box_{bi}_Tape", (bx, by, bz + h / 2.0 + 0.001), (0.05, d, 0.002), (0.80, 0.72, 0.56, 1.0))
    make_cyl("Spare_Rolled_Rug", (0.75, 4.72, 0.08), 0.08, 0.80, (0.50, 0.36, 0.40, 1.0), axis='X', segments=10)
    make_box("Spare_Record_Crate", (1.12, 5.12, 0.47), (0.32, 0.40, 0.22), (0.46, 0.36, 0.24, 1.0))
    # chipped teacups with dried herbs on the windowsill, past the Hanged Man
    for ti, ty in enumerate((2.70, 2.92, 3.14)):
        make_lathe(f"Herb_Teacup_{ti}", (-3.32, ty, 0.575), [(0.0, 0.0), (0.025, 0.0), (0.03, 0.01), (0.042, 0.055), (0.0, 0.055)], porcelain, segments=10)
        make_blob(f"Herb_Teacup_{ti}_Herbs", (-3.32, ty, 0.632), 0.034, [(0.46, 0.50, 0.32, 1.0), (0.52, 0.44, 0.40, 1.0), (0.40, 0.46, 0.30, 1.0)][ti], noise=0.4, seed=11 + ti, squash=0.5)
    # stacks of books leaning beside the bookshelf
    for bi in range(6):
        make_box(f"Floor_Books_A_{bi}", (2.30, 2.25, 0.03 + bi * 0.055), (0.26 - (bi % 2) * 0.03, 0.20, 0.05), COL_BOOK_SPINES[bi % len(COL_BOOK_SPINES)])
    for bi in range(5):
        make_rot_box(f"Floor_Books_B_{bi}", (2.32 + bi * 0.012, 2.62, 0.03 + bi * 0.054), (0.24, 0.18, 0.05), COL_BOOK_SPINES[(bi + 3) % len(COL_BOOK_SPINES)], yaw=0.12 * bi)
    # the candle burned low on the rug, the second deck fanned on the floor
    make_cyl("Rug_Candle_Saucer", (RUG_X + 0.48, RUG_Y - 0.40, 0.026), 0.06, 0.008, porcelain, segments=12)
    make_cyl("Rug_Candle", (RUG_X + 0.48, RUG_Y - 0.40, 0.055), 0.03, 0.05, (0.94, 0.90, 0.80, 1.0), segments=10)
    make_cyl("Rug_Candle_Wick", (RUG_X + 0.48, RUG_Y - 0.40, 0.086), 0.002, 0.012, P.METAL_BLACK, segments=4)
    for ci in range(7):
        a = -0.9 + ci * 0.3
        make_rot_box(f"Floor_Fan_Card_{ci}", (RUG_X + 0.55 + 0.10 * math.sin(a), RUG_Y + 0.35 + 0.10 * math.cos(a), 0.0235 + ci * 0.0006), (0.07, 0.11, 0.0008), (0.86, 0.82, 0.70, 1.0), yaw=-a)


def main():
    clear_scene()
    build_shell()
    build_living_room()
    build_kitchenette()
    build_bed_nook()
    build_decor()
    build_ceiling_infra()
    out_path = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/natalie_apartment.glb"))
    print(f"\n[build_natalie_apartment] exporting to {out_path}")
    build_hero_props()
    build_hero_props_2026_09()
    build_detail_pass_2026_08()
    build_use_states_d4()
    build_draft3_2026_09()
    build_draft4_2026_10()
    export_glb(out_path)


if __name__ == "__main__":
    main()
