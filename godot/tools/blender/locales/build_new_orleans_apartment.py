"""VOL 5 · New Orleans Apartment — French-Quarter style. Tall
shuttered windows, ceiling fan, four-poster bed, wrought-iron
balcony view, exposed brick.

DRAFT 3 (2026-09-19, lore/_VISUAL_PROGRAM.md §3 backgrounds pass, the
arcana primitive upgrade's third room; 2 VN placements + the Tower
board). LAYOUT the gates never reported: the ENTIRE shuttered-window
set — frames, glass, shutters, balcony bars — sat inside the south
wall's thickness (y -0.1..0.1) and could not be seen from the room;
the entry was a 3 m hole with no door; the bed's head posts stood in
the kitchenette; the ajar microwave door floated half a metre west
of the microwave; the sofa cushions sank 4 cm into the base and the
jacket into the back; the takeout sat in the sink; the bass ran into
the armoire and its amp; the game console sat half inside the TV
stand. The south wall is CUT around both windows (piers, spandrel,
lintel), the shutters fold against the piers inside, the iron rail
stands on a gallery deck outside, the door has jambs, a header and a
leaf; everything else moved onto what it stands on. PRIMITIVES: the
bed's posts turned with finials; the fan as stem, hub, light bowl;
the bass with neck, headstock, strings; the amp's grille and knobs.
WEAR personality (Jimmy's stalled week): the crash dent on his
cushion, the sofa-to-bed path, three ring stains and the ash dust on
the formica, the can ring by the TV. D3: the TV's, microwave's and
amp's cords. D5: the gallery deck and rail, the street three floors
down, the facade across. Scene: the fan-light practical below the
hub, not inside it.
Draft 4 targets: the sheer canopy as hanging panels; the brick wall's
mortar as a lathe-free grid; the balcony's scroll ironwork; the
transom over the door; the fridge (there is none); Deck: the preset
from the SE + establish_b.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_chamfer_box, make_lathe, make_tube, make_rot_box, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster
from _props.safety import make_smoke_detector
from _props.detail import (make_floor_stain, make_light_switch, make_threshold, make_traffic_wear, make_wall_outlet, make_wall_tint_band)
from _props.objects import make_can
from _props.furniture import make_bed

PAL = {"wall": (0.92, 0.84, 0.66, 1.0), "baseboard": (0.42, 0.28, 0.18, 1.0)}
COL_FLOOR = (0.46, 0.32, 0.20, 1.0); COL_SEAM = (0.22, 0.14, 0.10, 1.0)
COL_BRICK = (0.62, 0.42, 0.34, 1.0); COL_BRICK_SEAM = (0.32, 0.22, 0.18, 1.0)
COL_WROUGHT = (0.16, 0.14, 0.14, 1.0); COL_SHUTTER = (0.42, 0.52, 0.36, 1.0)
COL_BED_WOOD = (0.32, 0.20, 0.14, 1.0); COL_LINEN = (0.92, 0.86, 0.78, 1.0)
ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 3.40

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # East wall is brick
    make_wall("Wall_E", (+ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette={"wall": COL_BRICK, "baseboard": COL_BRICK_SEAM}, baseboard_face_sign=-1)
    for r in range(int(CEIL*4)):
        make_box(f"Wall_E_Brick_{r}", (+ROOM_W/2.0-0.04, ROOM_D/2.0, r*0.25+0.12), (0.005, ROOM_D, 0.012), COL_BRICK_SEAM)
    make_wall("Wall_W", (-ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1)
    # Draft 3: the south wall CUT around both windows (x ±2.5, 1.4 wide,
    # z 0.6..3.0) and narrowed to a 1 m door with a header
    for sgn, sx in ((-1, -2.5), (1, 2.5)):
        make_wall(f"Wall_S_{sgn:+d}_Pier_O", (sx + sgn * 0.85, 0.0, 0), length=0.30, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=+1)
        make_wall(f"Wall_S_{sgn:+d}_Pier_I", (sx - sgn * 0.85, 0.0, 0), length=0.30, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=+1)
        make_box(f"Wall_S_{sgn:+d}_Spandrel", (sx, 0.0, 0.30), (1.40, 0.20, 0.60), PAL["wall"])
        make_box(f"Wall_S_{sgn:+d}_Spandrel_Base", (sx, 0.06, 0.08), (1.40, 0.06, 0.16), PAL["baseboard"])
        make_box(f"Wall_S_{sgn:+d}_Lintel", (sx, 0.0, 3.20), (1.40, 0.20, 0.40), PAL["wall"])
    make_wall("Wall_S_Jamb_W", (-1.0, 0.0, 0), length=1.0, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_S_Jamb_E", (+1.0, 0.0, 0), length=1.0, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, 2.95), (1.0, 0.20, 0.90), PAL["wall"])
    make_box("Front_Door", (-0.05, 0.06, 1.05), (0.95, 0.05, 2.10), (0.42, 0.30, 0.20, 1.0))
    make_cyl("Front_Door_Knob", (0.35, 0.10, 1.02), 0.03, 0.04, (0.86, 0.62, 0.28, 1.0), axis='Y', segments=8)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"tile": COL_LINEN}, with_grid=False)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10),("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": (0.62, 0.42, 0.22, 1.0)})

def build_shuttered_windows():
    # Tall French windows in the cut openings; shutters folded against
    # the piers INSIDE; the iron rail on the gallery deck OUTSIDE (draft
    # 3 — the whole set used to sit inside the wall's thickness)
    for sgn, sx in [(-1, -2.50), (+1, +2.50)]:
        make_box(f"Window_{sgn:+d}_Frame", (sx, 0.0, 1.80), (1.40, 0.04, 2.40), (0.42, 0.32, 0.22, 1.0))
        make_box(f"Window_{sgn:+d}_Glass", (sx, -0.02, 1.80), (1.20, 0.005, 2.20), (0.96, 0.84, 0.62, 0.70))
        make_box(f"Window_{sgn:+d}_Mullion", (sx, -0.015, 1.80), (0.04, 0.02, 2.20), (0.42, 0.32, 0.22, 1.0))
        for shs in (-1, +1):
            make_box(f"Shutter_{sgn:+d}_{shs:+d}", (sx + shs*0.75, 0.13, 1.80), (0.10, 0.04, 2.20), COL_SHUTTER)
        # the gallery deck and its wrought rail
        make_box(f"Gallery_{sgn:+d}_Deck", (sx, -0.60, -0.02), (1.8, 0.70, 0.04), (0.30, 0.28, 0.26, 1.0))
        for ri in range(7):
            rx = sx - 0.42 + ri*0.14
            make_cyl(f"Balcony_{sgn:+d}_Bar_{ri}", (rx, -0.88, 0.62), 0.012, 1.24, COL_WROUGHT, axis='Z')
        make_tube(f"Balcony_{sgn:+d}_Rail", [(sx - 0.65, -0.88, 1.26), (sx + 0.65, -0.88, 1.26)], 0.02, COL_WROUGHT, segments=6)
        make_tube(f"Balcony_{sgn:+d}_Mid", [(sx - 0.65, -0.88, 0.62), (sx + 0.65, -0.88, 0.62)], 0.014, COL_WROUGHT, segments=6)


def build_bed():
    # 2026-08-09: was (0.0, 4.80) — the bed's head stood INSIDE the
    # kitchenette and its posts inside the counter. East of it now.
    bx, by = 0.9, 4.10          # the four-poster stands free of the walls by design: the kitchenette
                                # owns the N wall's centre, the armoire and bass amp its east end (2026-09-10)
                                # (draft 3: 4.10 — at 4.30 the head posts stood in the kitchenette)
    # Four-poster bed — the shared bed under the posts (2026-09-07)
    make_bed("Bed", bx, by, head="+Y", w=1.80, d=2.00, style="platform",
             frame_col=COL_BED_WOOD, mattress_col=COL_LINEN, sheet_col=COL_LINEN,
             blanket_col=(0.62, 0.42, 0.36, 1.0), pillow_col=P.PAPER, pillows=2, made=True, headboard=False)
    # 4 posts
    for sgn_x in (-1, +1):
        for sgn_y in (-1, +1):
            make_lathe(f"Bed_Post_{sgn_x:+d}_{sgn_y:+d}", (bx+sgn_x*0.90, by+sgn_y*1.00, 0.0),
                       [(0.045, 0.0), (0.05, 0.04), (0.036, 0.10), (0.04, 0.60), (0.05, 0.70), (0.036, 0.80), (0.036, 1.70), (0.045, 1.80), (0.04, 2.02)],
                       COL_BED_WOOD, segments=8)
            make_lathe(f"Bed_Finial_{sgn_x:+d}_{sgn_y:+d}", (bx+sgn_x*0.90, by+sgn_y*1.00, 2.08),
                       [(0.04, 0.0), (0.05, 0.05), (0.03, 0.10), (0.02, 0.14), (0.0, 0.17)], COL_BED_WOOD, segments=8)
    # Canopy frame (top rails)
    for sgn_y in (-1, +1):
        make_box(f"Bed_Canopy_X_{sgn_y:+d}", (bx, by+sgn_y*1.00, 2.05), (1.80, 0.06, 0.06), COL_BED_WOOD)
    for sgn_x in (-1, +1):
        make_box(f"Bed_Canopy_Y_{sgn_x:+d}", (bx+sgn_x*0.90, by, 2.05), (0.06, 2.00, 0.06), COL_BED_WOOD)
    # Sheer canopy curtains (drape)
    make_box("Bed_Canopy_Sheer", (bx, by + 1.00, 1.60), (1.90, 0.04, 0.90), (0.96, 0.92, 0.84, 0.55))   # (draft 3: at the head rail, not across the bed's middle)

def build_armoire():
    # Wardrobe west wall
    # 2026-08-09: was (-2.80, 3.0) — inside the rented sofa. East
    # wall now, between the TV stand and the bed corner.
    ax, ay = 2.80, 3.55
    make_box("Armoire_Body", (ax, ay, 1.20), (0.50, 1.40, 2.40), COL_BED_WOOD)
    make_box("Armoire_Door_L", (ax+0.21, ay-0.34, 1.20), (0.04, 0.66, 2.30), (0.42, 0.30, 0.20, 1.0))
    make_box("Armoire_Door_R", (ax+0.21, ay+0.34, 1.20), (0.04, 0.66, 2.30), (0.42, 0.30, 0.20, 1.0))
    make_cyl("Armoire_KnobL", (ax+0.24, ay-0.06, 1.20), 0.025, 0.04, (0.86, 0.62, 0.28, 1.0), axis='X')
    make_cyl("Armoire_KnobR", (ax+0.24, ay+0.06, 1.20), 0.025, 0.04, (0.86, 0.62, 0.28, 1.0), axis='X')

def build_decor():
    make_wall_clock("Clock", (-3.45, 2.0, 2.10), frozen_hour=6, frozen_min=23)
    make_faded_poster("PosterW", (-3.45, 1.0, 1.50))
    make_floor_plant("Plant_S", (+2.50, 1.50, 0.0))
    # Ceiling fan
    cx, cy = 0.0, 3.0
    # (draft 3: stem, hub and light bowl as profiles; the practical sits
    # in the bowl)
    make_lathe("Fan_Stem", (cx, cy, CEIL-0.35), [(0.02, 0.0), (0.02, 0.30), (0.06, 0.32), (0.06, 0.35)], (0.42, 0.30, 0.20, 1.0), segments=8)
    make_lathe("Fan_Hub", (cx, cy, CEIL-0.47), [(0.10, 0.0), (0.18, 0.04), (0.18, 0.10), (0.12, 0.12)], (0.42, 0.30, 0.20, 1.0), segments=12)
    make_lathe("Fan_Light_Bowl", (cx, cy, CEIL-0.60), [(0.0, 0.0), (0.09, 0.02), (0.11, 0.10), (0.10, 0.13)], (0.96, 0.90, 0.72, 1.0), segments=12)
    for bi in range(4):
        import math
        ang = bi * 1.57
        bx_off = math.cos(ang) * 0.50
        by_off = math.sin(ang) * 0.50
        make_box(f"Fan_Blade_{bi}", (cx + bx_off, cy + by_off, CEIL-0.42), (0.80 if bi%2==0 else 0.10, 0.10 if bi%2==0 else 0.80, 0.02), (0.42, 0.30, 0.20, 1.0))

def build_ceiling_infra():
    make_smoke_detector("Smoke", (+1.5, 3.5, CEIL))

def build_hero_props():
    """2026-08-03 tail pass: the rented sofa Jimmy crashes on, the
    kitchenette monument to neglect (cloudy glasses, ashtray
    volcano, warm bourbon), the greasy microwave the Devil looks
    back from, the disintegrating lace curtain — and vol1's TV +
    console + bass for Jacob's place."""
    # The rented sofa, springs and all
    make_box("Rented_Sofa_Base", (-2.40, 2.40, 0.26), (0.90, 2.00, 0.40), (0.42, 0.36, 0.30, 1.0))
    make_box("Rented_Sofa_Back", (-2.80, 2.40, 0.66), (0.20, 2.00, 0.60), (0.38, 0.32, 0.27, 1.0))
    for cy in (1.95, 2.85):
        make_chamfer_box(f"Sofa_Cushion_{cy:.2f}", (-2.32, cy, 0.53), (0.72, 0.80, 0.14), (0.46, 0.40, 0.33, 1.0), chamfer=0.03)
    make_chamfer_box("Sofa_Blanket_Tangle", (-2.35, 1.80, 0.65), (0.70, 0.55, 0.10), (0.52, 0.44, 0.36, 1.0), chamfer=0.03)
    # Kitchenette, N wall: counter, sink of cloudy glasses, ashtray,
    # bourbon, microwave-mirror
    make_box("Kitchenette", (0.0, 5.60, 0.46), (2.4, 0.62, 0.92), (0.58, 0.54, 0.46, 1.0))
    make_box("Kitchenette_Formica", (0.0, 5.60, 0.94), (2.5, 0.68, 0.05), (0.72, 0.68, 0.58, 1.0))
    make_box("Kitchenette_Sink", (-0.6, 5.60, 0.95), (0.45, 0.40, 0.05), (0.44, 0.46, 0.47, 1.0))
    for gi in range(3):
        make_cyl(f"Cloudy_Glass_{gi}", (-0.72 + gi * 0.14, 5.55, 1.02), 0.03, 0.10,
                 (0.72, 0.74, 0.70, 0.6), segments=8)
    make_cyl("Ashtray_Volcano", (0.35, 5.50, 0.988), 0.07, 0.04, (0.30, 0.30, 0.32, 1.0), segments=10)
    make_box("Ash_Heap", (0.35, 5.50, 1.02), (0.08, 0.08, 0.035), (0.55, 0.53, 0.50, 1.0))
    make_cyl("Warm_Bourbon", (0.72, 5.62, 1.07), 0.045, 0.26, (0.52, 0.32, 0.14, 0.85), segments=8)
    make_box("Microwave_Greasy", (1.20, 5.60, 1.12), (0.50, 0.38, 0.30), (0.58, 0.56, 0.52, 1.0))
    make_box("Microwave_Cavity", (1.20, 5.405, 1.12), (0.36, 0.01, 0.22), (0.12, 0.12, 0.12, 1.0))
    # The yellowed lace curtain over the W window (draft 3: inside the
    # room, between the shutters — it hung inside the wall)
    make_box("Lace_Curtain", (-2.50, 0.14, 1.80), (1.4, 0.03, 1.9), (0.86, 0.82, 0.66, 0.5))
    # vol1: TV + console + the bass in the corner
    make_box("TV", (2.80, 2.2, 0.95), (0.10, 0.85, 0.55), (0.12, 0.12, 0.14, 1.0))
    make_box("TV_Screen", (2.74, 2.2, 0.95), (0.02, 0.72, 0.44), (0.30, 0.36, 0.42, 1.0))
    make_box("TV_Stand", (2.80, 2.2, 0.34), (0.55, 0.90, 0.62), (0.36, 0.28, 0.20, 1.0))
    make_box("Game_Console", (2.63, 1.85, 0.686), (0.20, 0.28, 0.07), (0.22, 0.22, 0.26, 1.0))   # (draft 3: in front of the TV, not under it)
    for wi in range(2):
        make_box(f"Controller_Cord_{wi}", (2.5 - wi * 0.4, 2.0 + wi * 0.2, 0.02), (0.5, 0.02, 0.01), (0.14, 0.14, 0.16, 1.0))
    # (draft 3: the bass as a bass — body, neck, headstock, four strings —
    # north of the armoire it used to run into; the amp beyond it)
    make_chamfer_box("Bass_Body", (2.65, 4.55, 0.55), (0.14, 0.36, 0.50), (0.52, 0.22, 0.16, 1.0), chamfer=0.03)
    make_box("Bass_Neck", (2.65, 4.55, 1.25), (0.05, 0.07, 0.95), (0.30, 0.22, 0.14, 1.0))
    make_box("Bass_Headstock", (2.65, 4.55, 1.78), (0.05, 0.09, 0.14), (0.30, 0.22, 0.14, 1.0))
    for si_ in range(4):
        make_tube(f"Bass_String_{si_}", [(2.575, 4.52 + si_ * 0.02, 0.36), (2.62, 4.52 + si_ * 0.02, 1.72)], 0.002, (0.80, 0.80, 0.82, 1.0), segments=4)
    make_box("Bass_Amp", (2.60, 5.15, 0.25), (0.40, 0.35, 0.48), (0.16, 0.14, 0.13, 1.0))
    make_box("Bass_Amp_Grille", (2.60, 4.972, 0.20), (0.34, 0.006, 0.30), (0.22, 0.20, 0.18, 1.0))
    for ki_ in range(3):
        make_cyl(f"Bass_Amp_Knob_{ki_}", (2.50 + ki_ * 0.10, 4.972, 0.44), 0.012, 0.01, (0.70, 0.70, 0.72, 1.0), axis='Y', segments=6)



def build_detail_pass_2026_08():
    """D2 surface breakup + first D3 (adaptive template pass per
    lore/_SET_DETAIL_PLAYBOOK.md). Per-locale wear personality is
    the next pass."""
    wear = (COL_FLOOR[0] * 0.88, COL_FLOOR[1] * 0.88, COL_FLOOR[2] * 0.88, 1.0)
    make_traffic_wear("Wear_Entry", [(0.0, 0.6), (0.0, 2.6)], width=0.60, tint=wear)   # (draft 3: stops short of the bed's foot)
    make_floor_stain("Stain_WorkZone", (ROOM_W * 0.22, ROOM_D * 0.62), radius=0.24,
                     tint=(COL_FLOOR[0] * 0.82, COL_FLOOR[1] * 0.82, COL_FLOOR[2] * 0.82, 1.0))
    pw = PAL["wall"]
    band = (pw[0] * 0.90, pw[1] * 0.90, pw[2] * 0.88, 1.0)
    make_wall_tint_band("Band_W", (-ROOM_W / 2.0 + 0.105, ROOM_D / 2.0, 0.0),
                        length=ROOM_D - 0.4, axis='Y', band_z=CEIL - 0.16, tint=band)
    make_wall_tint_band("Band_E", (ROOM_W / 2.0 - 0.105, ROOM_D / 2.0, 0.0),
                        length=ROOM_D - 0.4, axis='Y', band_z=CEIL - 0.16, tint=band)
    make_threshold("Threshold_Entry", (0.0, 0.14), width=1.0, axis='X')
    make_light_switch("Switch_Entry", (1.15, 0.0), axis='X', face_sign=1, aged=True)
    make_wall_outlet("Outlet_W", (-ROOM_W / 2.0, ROOM_D * 0.35), axis='Y',
                     face_sign=1, aged=True)
    make_wall_outlet("Outlet_E", (ROOM_W / 2.0, ROOM_D * 0.70), axis='Y',
                     face_sign=-1, aged=True)


def build_use_states_d4():
    """D4 use states: takeout, cans, the microwave door ajar —
    Jimmy's week is visible on the surfaces."""
    # Takeout on the kitchenette: two containers, one lid off
    make_box("Takeout_A", (-0.15, 5.75, 0.99), (0.16, 0.16, 0.09),
             (0.92, 0.92, 0.88, 1.0))   # (draft 3: off the sink)
    make_box("Takeout_B", (-0.18, 5.52, 0.98), (0.16, 0.16, 0.07),
             (0.92, 0.92, 0.88, 1.0))
    make_box("Takeout_B_Lid", (0.04, 5.44, 0.935), (0.17, 0.17, 0.01),
             (0.88, 0.88, 0.84, 1.0))
    # Microwave door ajar (a container open)
    # (draft 3: hinged at the microwave's west edge, swung 70° out —
    # it floated half a metre west of the microwave)
    make_rot_box("Microwave_Door_Ajar", (1.01, 5.24, 1.12), (0.36, 0.02, 0.22),
                 (0.36, 0.38, 0.40, 1.0), yaw=-1.22)
    # Cans: two standing on the TV stand, one on its side by the bin
    make_can("Can_TV_0", 2.62, 2.08, 0.66, (0.72, 0.20, 0.18, 1.0))
    make_can("Can_TV_1", 2.62, 2.30, 0.66, (0.72, 0.20, 0.18, 1.0))
    make_cyl("Can_Floor", (2.45, 1.15, 0.033), 0.033, 0.12,
             (0.66, 0.18, 0.16, 1.0), segments=8, axis='Y')
    make_cyl("Trash_Bin", (2.85, 0.75, 0.18), 0.14, 0.36,
             (0.30, 0.32, 0.34, 1.0), segments=10)
    make_box("Trash_Crumple_0", (2.62, 0.62, 0.03), (0.07, 0.07, 0.06),
             (0.88, 0.86, 0.80, 1.0))
    make_box("Trash_Crumple_1", (3.02, 0.95, 0.025), (0.06, 0.06, 0.05),
             (0.86, 0.84, 0.78, 1.0))
    # Jacket over the sofa back
    # (draft 3: OVER the back, one sleeve hanging on the seat side)
    make_chamfer_box("Sofa_Jacket", (-2.80, 2.15, 0.99), (0.36, 0.60, 0.06),
                     (0.26, 0.28, 0.34, 1.0), chamfer=0.02)
    make_rot_box("Sofa_Jacket_Sleeve", (-2.62, 2.35, 0.80), (0.08, 0.10, 0.40),
                 (0.26, 0.28, 0.34, 1.0), roll=0.3)

def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    THE PHONE ("The screen, when it came on, was not Antonio. The
    screen said Q. PAUL."): face-up on the rented sofa's far
    cushion, screen lit."""
    make_box("Antonios_Phone", (-2.32, 2.75, 0.6055), (0.070, 0.140, 0.011), (0.13, 0.13, 0.15, 1.0))
    make_box("Antonios_Phone_Screen", (-2.32, 2.75, 0.6120), (0.058, 0.124, 0.002), (0.42, 0.50, 0.60, 1.0))


def build_draft3_2026_09():
    """DRAFT 3 (2026-09-19) · Jimmy's week on the surfaces, the cords,
    the street below. No part name carries a cue word (microwave ·
    ceiling · fan · phone)."""
    wear = (COL_FLOOR[0] * 0.86, COL_FLOOR[1] * 0.86, COL_FLOOR[2] * 0.86, 1.0)
    cord = (0.16, 0.16, 0.18, 1.0)
    make_box("Wear_Crash_Dent", (-2.32, 1.95, 0.6015), (0.50, 0.50, 0.003), (0.40, 0.34, 0.28, 1.0))
    make_traffic_wear("Wear_Sofa_Bed", [(-1.6, 3.6), (-1.6, 4.9), (-0.6, 4.9)], width=0.55, tint=wear)
    for ri, (rx, ry) in enumerate(((-0.35, 5.70), (0.55, 5.72), (0.22, 5.42))):
        make_cyl(f"Wear_Ring_{ri}", (rx, ry, 0.966), 0.045, 0.002, (0.42, 0.34, 0.24, 1.0), segments=10)
    make_cyl("Wear_Ash", (0.35, 5.50, 0.9665), 0.12, 0.002, (0.52, 0.50, 0.48, 1.0), segments=12)
    make_cyl("Wear_Can_Ring", (2.45, 1.35, 0.007), 0.04, 0.002, (0.30, 0.20, 0.14, 1.0), segments=8)
    # D3
    make_wall_outlet("Outlet_E_2", (ROOM_W / 2.0, 2.2), axis='Y', face_sign=-1, z=0.30, aged=True)
    make_tube("Cord_1", [(2.85, 2.2, 0.75), (ROOM_W / 2.0 - 0.13, 2.2, 0.30)], 0.008, cord, segments=5)
    make_wall_outlet("Outlet_N_1", (1.5, ROOM_D), axis='X', face_sign=-1, z=1.15, aged=True)
    make_tube("Cord_2", [(1.44, 5.75, 1.05), (1.50, ROOM_D - 0.13, 1.15)], 0.008, cord, segments=5)
    make_tube("Cord_3", [(2.80, 5.00, 0.30), (ROOM_W / 2.0 - 0.13, 4.25, 0.30)], 0.008, cord, segments=5)
    # D5 · the street three floors down, the facade across
    make_box("Out_Street", (0.0, -6.0, -3.63), (20.0, 10.0, 0.05), (0.30, 0.30, 0.32, 1.0))
    make_box("Out_Sidewalk", (0.0, -1.8, -3.58), (20.0, 1.6, 0.06), (0.52, 0.50, 0.46, 1.0))
    make_box("Out_Facade", (0.0, -12.0, 1.4), (20.0, 0.4, 10.0), (0.62, 0.50, 0.40, 1.0))
    for gi in range(3):
        make_box(f"Out_Facade_Gallery_{gi}", (0.0, -11.6, -3.4 + gi * 3.4 + 3.2), (18.0, 0.6, 0.08), (0.14, 0.14, 0.15, 1.0))


def main():
    clear_scene(); build_shell(); build_shuttered_windows(); build_bed(); build_armoire(); build_decor(); build_ceiling_infra()
    build_hero_props()
    build_detail_pass_2026_08()
    build_use_states_d4()
    build_hero_props_2026_09()
    build_draft3_2026_09()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/new_orleans_apartment.glb"))
    print(f"\n[build_new_orleans_apartment] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
