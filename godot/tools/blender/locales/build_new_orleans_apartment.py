"""VOL 5 · New Orleans Apartment — French-Quarter style. Tall
shuttered windows, ceiling fan, four-poster bed, wrought-iron
balcony view, exposed brick.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster
from _props.safety import make_smoke_detector
from _props.detail import (make_floor_stain, make_light_switch, make_threshold, make_traffic_wear, make_wall_outlet, make_wall_tint_band)
from _props.objects import make_can

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
    make_wall("Wall_S_W", (-2.5, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL)
    make_wall("Wall_S_E", (+2.5, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"tile": COL_LINEN})
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10),("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": (0.62, 0.42, 0.22, 1.0)})

def build_shuttered_windows():
    # Tall French shutters S wall on either side of door
    for sgn, sx in [(-1, -2.50), (+1, +2.50)]:
        # Window opening with iron balcony rail
        make_box(f"Window_{sgn:+d}_Frame", (sx, 0.0, 1.80), (1.40, 0.04, 2.40), (0.42, 0.32, 0.22, 1.0))
        make_box(f"Window_{sgn:+d}_Glass", (sx, -0.02, 1.80), (1.20, 0.005, 2.20), (0.96, 0.84, 0.62, 0.70))
        # Wrought iron balcony rail (mid-height curls)
        for ri in range(7):
            rx = sx - 0.42 + ri*0.14
            make_cyl(f"Balcony_{sgn:+d}_Bar_{ri}", (rx, -0.08, 0.90), 0.012, 0.60, COL_WROUGHT, axis='Z')
        make_cyl(f"Balcony_{sgn:+d}_Rail", (sx, -0.10, 1.20), 0.020, 1.20, COL_WROUGHT, axis='X')
        # Folded shutters either side
        for shs in (-1, +1):
            make_box(f"Shutter_{sgn:+d}_{shs:+d}", (sx + shs*0.70, 0.02, 1.80), (0.10, 0.04, 2.20), COL_SHUTTER)

def build_bed():
    # 2026-08-09: was (0.0, 4.80) — the bed's head stood INSIDE the
    # kitchenette and its posts inside the counter. East of it now.
    bx, by = 0.9, 4.30
    # Four-poster bed
    make_box("Bed_Frame", (bx, by, 0.20), (1.80, 2.00, 0.20), COL_BED_WOOD)
    make_box("Bed_Mattress", (bx, by, 0.50), (1.60, 1.80, 0.30), COL_LINEN)
    make_box("Bed_Pillow", (bx, by+0.70, 0.74), (1.40, 0.50, 0.16), P.PAPER)
    # Throw
    make_box("Bed_Throw", (bx, by-0.50, 0.70), (1.40, 0.60, 0.08), (0.62, 0.42, 0.36, 1.0))
    # 4 posts
    for sgn_x in (-1, +1):
        for sgn_y in (-1, +1):
            make_box(f"Bed_Post_{sgn_x:+d}_{sgn_y:+d}", (bx+sgn_x*0.90, by+sgn_y*1.00, 1.10), (0.08, 0.08, 2.00), COL_BED_WOOD)
    # Canopy frame (top rails)
    for sgn_y in (-1, +1):
        make_box(f"Bed_Canopy_X_{sgn_y:+d}", (bx, by+sgn_y*1.00, 2.05), (1.80, 0.06, 0.06), COL_BED_WOOD)
    for sgn_x in (-1, +1):
        make_box(f"Bed_Canopy_Y_{sgn_x:+d}", (bx+sgn_x*0.90, by, 2.05), (0.06, 2.00, 0.06), COL_BED_WOOD)
    # Sheer canopy curtains (drape)
    make_box("Bed_Canopy_Sheer", (bx, by, 1.60), (1.90, 0.04, 0.90), (0.96, 0.92, 0.84, 0.55))

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
    make_cyl("Fan_Stem", (cx, cy, CEIL-0.20), 0.04, 0.30, (0.42, 0.30, 0.20, 1.0))
    make_cyl("Fan_Hub", (cx, cy, CEIL-0.42), 0.18, 0.10, (0.42, 0.30, 0.20, 1.0))
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
        make_box(f"Sofa_Cushion_{cy:.2f}", (-2.32, cy, 0.49), (0.72, 0.80, 0.14), (0.46, 0.40, 0.33, 1.0))
    make_box("Sofa_Blanket_Tangle", (-2.35, 1.80, 0.60), (0.70, 0.55, 0.10), (0.52, 0.44, 0.36, 1.0))
    # Kitchenette, N wall: counter, sink of cloudy glasses, ashtray,
    # bourbon, microwave-mirror
    make_box("Kitchenette", (0.0, 5.60, 0.46), (2.4, 0.62, 0.92), (0.58, 0.54, 0.46, 1.0))
    make_box("Kitchenette_Formica", (0.0, 5.60, 0.94), (2.5, 0.68, 0.05), (0.72, 0.68, 0.58, 1.0))
    make_box("Kitchenette_Sink", (-0.6, 5.60, 0.95), (0.45, 0.40, 0.05), (0.44, 0.46, 0.47, 1.0))
    for gi in range(3):
        make_cyl(f"Cloudy_Glass_{gi}", (-0.72 + gi * 0.14, 5.55, 1.02), 0.03, 0.10,
                 (0.72, 0.74, 0.70, 0.6), segments=8)
    make_cyl("Ashtray_Volcano", (0.35, 5.50, 0.985), 0.07, 0.04, (0.30, 0.30, 0.32, 1.0), segments=10)
    make_box("Ash_Heap", (0.35, 5.50, 1.02), (0.08, 0.08, 0.035), (0.55, 0.53, 0.50, 1.0))
    make_cyl("Warm_Bourbon", (0.72, 5.62, 1.07), 0.045, 0.26, (0.52, 0.32, 0.14, 0.85), segments=8)
    make_box("Microwave_Greasy", (1.20, 5.60, 1.12), (0.50, 0.38, 0.30), (0.58, 0.56, 0.52, 1.0))
    make_box("Microwave_Mirror_Door", (1.20, 5.40, 1.12), (0.38, 0.02, 0.22), (0.36, 0.38, 0.40, 1.0))
    # The yellowed lace curtain over the W window
    make_box("Lace_Curtain", (-2.50, -0.02, 1.80), (1.4, 0.03, 1.9), (0.86, 0.82, 0.66, 0.5))
    # vol1: TV + console + the bass in the corner
    make_box("TV", (2.80, 2.2, 0.95), (0.10, 0.85, 0.55), (0.12, 0.12, 0.14, 1.0))
    make_box("TV_Screen", (2.74, 2.2, 0.95), (0.02, 0.72, 0.44), (0.30, 0.36, 0.42, 1.0))
    make_box("TV_Stand", (2.80, 2.2, 0.34), (0.55, 0.90, 0.62), (0.36, 0.28, 0.20, 1.0))
    make_box("Game_Console", (2.72, 1.85, 0.63), (0.28, 0.22, 0.07), (0.22, 0.22, 0.26, 1.0))
    for wi in range(2):
        make_box(f"Controller_Cord_{wi}", (2.5 - wi * 0.4, 2.0 + wi * 0.2, 0.02), (0.5, 0.02, 0.01), (0.14, 0.14, 0.16, 1.0))
    make_box("Bass_Body", (2.65, 4.4, 0.55), (0.14, 0.36, 0.50), (0.52, 0.22, 0.16, 1.0))
    make_box("Bass_Neck", (2.65, 4.4, 1.25), (0.05, 0.07, 0.95), (0.30, 0.22, 0.14, 1.0))
    make_box("Bass_Amp", (2.60, 4.85, 0.25), (0.40, 0.35, 0.48), (0.16, 0.14, 0.13, 1.0))



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
    """D4 use states: takeout, cans, the microwave door ajar —
    Jimmy's week is visible on the surfaces."""
    # Takeout on the kitchenette: two containers, one lid off
    make_box("Takeout_A", (-0.45, 5.72, 0.99), (0.16, 0.16, 0.09),
             (0.92, 0.92, 0.88, 1.0))
    make_box("Takeout_B", (-0.18, 5.52, 0.98), (0.16, 0.16, 0.07),
             (0.92, 0.92, 0.88, 1.0))
    make_box("Takeout_B_Lid", (0.04, 5.44, 0.935), (0.17, 0.17, 0.01),
             (0.88, 0.88, 0.84, 1.0))
    # Microwave door ajar (a container open)
    make_box("Microwave_Door_Ajar", (0.42, 5.38, 1.06), (0.03, 0.26, 0.24),
             (0.24, 0.24, 0.26, 1.0))
    # Cans: two standing on the TV stand, one on its side by the bin
    make_can("Can_TV_0", 2.62, 2.02, 0.66, (0.72, 0.20, 0.18, 1.0))
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
    make_box("Sofa_Jacket", (-2.72, 2.15, 0.62), (0.16, 0.60, 0.30),
             (0.26, 0.28, 0.34, 1.0))

def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    THE PHONE ("The screen, when it came on, was not Antonio. The
    screen said Q. PAUL."): face-up on the rented sofa's far
    cushion, screen lit."""
    make_box("Antonios_Phone", (-2.32, 2.75, 0.5655), (0.070, 0.140, 0.011), (0.13, 0.13, 0.15, 1.0))
    make_box("Antonios_Phone_Screen", (-2.32, 2.75, 0.5720), (0.058, 0.124, 0.002), (0.42, 0.50, 0.60, 1.0))


def main():
    clear_scene(); build_shell(); build_shuttered_windows(); build_bed(); build_armoire(); build_decor(); build_ceiling_infra()
    build_hero_props()
    build_detail_pass_2026_08()
    build_use_states_d4()
    build_hero_props_2026_09()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/new_orleans_apartment.glb"))
    print(f"\n[build_new_orleans_apartment] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
