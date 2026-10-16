"""VOL 5 · New Orleans Room — small hotel / boarding-house room.
Single bed, washbasin, single bulb on cord, peeling wallpaper,
sash window. Spare and worn.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.objects import make_mug
from _props.geometry import clear_scene, make_box, make_cyl, export_glb, make_tube, make_rot_box
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_wall_with_openings
from _props.decor import make_wall_clock, make_faded_poster
from _props.safety import make_smoke_detector
from _props.detail import (make_floor_stain, make_light_switch, make_threshold, make_traffic_wear, make_wall_outlet, make_wall_tint_band)

PAL = {"wall": (0.86, 0.78, 0.62, 1.0), "baseboard": (0.42, 0.30, 0.20, 1.0)}
COL_FLOOR = (0.42, 0.30, 0.18, 1.0); COL_SEAM = (0.22, 0.14, 0.10, 1.0)
COL_BED_FRAME = (0.32, 0.28, 0.24, 1.0); COL_LINEN = (0.86, 0.82, 0.74, 1.0)
COL_BASIN = (0.92, 0.92, 0.88, 1.0); COL_FAUCET = (0.62, 0.62, 0.60, 1.0)
COL_BULB = (0.96, 0.86, 0.46, 1.0); COL_WALLPAPER_PEEL = (0.62, 0.46, 0.32, 1.0)
ROOM_W = 4.0; ROOM_D = 5.0; CEIL = 2.80

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=bb)
    make_wall_with_openings("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1,
                            openings=[(0.9, 1.60, 1.20, 1.20)])   # cut for the sash window, OVER THE DESK (2026-10-03)
    make_wall("Wall_S_W", (-1.5, 0.0, 0), length=1.2, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+1.5, 0.0, 0), length=1.2, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=+1)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, with_grid=False)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10),("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": (0.42, 0.30, 0.20, 1.0)})
    # Sash window N wall
    # on the wall's room face, glass in front of the frame (2026-09-24: frame and glass
    # were offset from the wall's CENTRE line — inside the wall, never visible)
    # (2026-10-03: the frame was a solid plate behind the glass — four bars)
    for nm, fx, fz, sx, sz in (("Window_N_Frame_T", 0.0, 2.27, 1.40, 0.06), ("Window_N_Frame_B", 0.0, 0.93, 1.40, 0.06),
                               ("Window_N_Frame_L", -0.67, 1.60, 0.06, 1.40), ("Window_N_Frame_R", 0.67, 1.60, 0.06, 1.40)):
        make_box(nm, (fx + 0.9, ROOM_D-0.125, fz), (sx, 0.04, sz), (0.42, 0.30, 0.20, 1.0))   # on the glass, which bears on the wall; over the desk (2026-10-03)
    make_box("Window_N_Glass", (0.9, ROOM_D-0.1025, 1.60), (1.26, 0.005, 1.26), (0.78, 0.84, 0.86, 0.30))   # on the wall face, 3 cm over the opening's edges
    make_box("Window_N_Mull", (0.9, ROOM_D-0.125, 1.60), (1.30, 0.04, 0.04), (0.42, 0.30, 0.20, 1.0))   # bar to bar
    # Peeling wallpaper strips on E wall
    for pi in range(3):
        py = 1.0 + pi*1.5
        make_box(f"Peel_{pi}", (ROOM_W/2.0-0.06 - 0.0431, py, 1.50 + (pi%2)*0.20), (0.005, 0.36, 0.50), COL_WALLPAPER_PEEL)

def build_bed():
    bx, by = -0.1, 3.85         # head to the N wall, clear of the desk at x 0.6..1.6 (2026-09-10)
    # the shared bed, sheet rumpled in a heap (2026-09-07); boards stay
    from _props.furniture import make_bed
    make_bed("Bed", bx, by, head="+Y", w=1.20, d=1.80, style="platform",
             frame_col=COL_BED_FRAME, mattress_col=COL_LINEN, sheet_col=COL_LINEN,
             blanket_col=COL_LINEN, pillow_col=P.PAPER, pillows=1, made=False, headboard=False)
    # Head/foot board
    # to the floor (2026-09-23: it hung 2 cm over the platform)
    make_box("Bed_HeadBoard", (bx, by+0.92, 0.55), (1.20, 0.04, 1.10), COL_BED_FRAME)
    make_box("Bed_FootBoard", (bx, by-0.92, 0.46), (1.20, 0.04, 0.50), COL_BED_FRAME)
    # Nightstand
    make_box("Nightstand", (-0.95, 4.35, 0.40), (0.40, 0.40, 0.80), COL_BED_FRAME)   # at the bed's west side by the head (2026-09-10)
    # Glass of water on nightstand
    make_cyl("Glass_Water", (-0.95, 4.35, 0.86), 0.04, 0.12, (0.78, 0.84, 0.86, 0.50))

def build_washbasin():
    # Small porcelain washbasin in corner
    wx, wy = +1.60, 4.50
    make_box("Basin_Bracket", (wx, wy, 0.74), (0.04, 0.50, 0.10), COL_FAUCET)
    make_box("Basin_Bowl", (wx-0.20, wy, 0.84), (0.36, 0.46, 0.16), COL_BASIN)
    make_cyl("Basin_Faucet", (wx-0.20, wy, 1.00), 0.012, 0.20, COL_FAUCET)
    # spout off the faucet, drain up to the bowl (2026-09-23: both on air)
    make_box("Basin_Spout", (wx-0.26, wy, 1.08), (0.10, 0.04, 0.04), COL_FAUCET)
    make_cyl("Basin_DrainPipe", (wx-0.20, wy, 0.455), 0.025, 0.61, COL_FAUCET)
    # Towel hanging
    make_box("Basin_Towel", (wx-0.30, wy-0.30, 0.60), (0.02, 0.30, 0.40), (0.78, 0.62, 0.42, 1.0))

def build_decor():
    make_wall_clock("Clock", (-1.900, 2.0, 2.10), frozen_hour=11, frozen_min=24, facing='+X')
    make_faded_poster("Poster", (1.8965, 2.0, 1.50), into_room=-1)
    # Single chair
    # Chair at the desk, the jacket over its back (the sealed
    # envelope rides the inside pocket)
    make_box("Chair_Seat", (1.1, 3.75, 0.46), (0.40, 0.40, 0.04), COL_BED_FRAME)   # at the desk, facing it (2026-09-07)
    # legs (2026-09-08)
    for lx_ in (-1, 1):
        for ly_ in (-1, 1):
            make_box(f"Chair_Leg_{lx_:+d}_{ly_:+d}",
                     (1.1 + lx_ * 0.16, 3.75 + ly_ * 0.16, 0.23),
                     (0.035, 0.035, 0.46), COL_BED_FRAME)
    make_box("Chair_Back", (1.1, 3.57, 0.70), (0.40, 0.04, 0.50), COL_BED_FRAME)
    make_box("Jacket_Draped", (1.1, 3.54, 0.72), (0.44, 0.10, 0.46), (0.30, 0.28, 0.26, 1.0))
    # The Korea duffle, battered enough to look intentional
    make_cyl("Canvas_Duffle", (+1.20, 1.50, 0.16), 0.17, 0.62, (0.42, 0.40, 0.30, 1.0), segments=10, axis='Y')
    make_box("Duffle_Strap", (+1.20, 1.50, 0.34), (0.30, 0.05, 0.02), (0.30, 0.28, 0.22, 1.0))
    # Strap detail
    make_box("Suitcase_Strap", (+1.20, 1.50, 0.3331), (0.04, 0.40, 0.005), (0.86, 0.62, 0.28, 1.0))

def build_ceiling_infra():
    # Bare bulb on cord (only light)
    make_cyl("Bulb_Cord", (0.0, 2.5, CEIL-0.30), 0.005, 0.60, P.METAL_BLACK)
    # socket on the cord, bulb in the socket (2026-09-23: 3 cm and 5 cm gaps)
    make_cyl("Bulb_Socket", (0.0, 2.5, CEIL-0.63), 0.025, 0.06, (0.62, 0.62, 0.60, 1.0))
    make_cyl("Bulb_Glass", (0.0, 2.5, CEIL-0.72), 0.06, 0.12, COL_BULB)
    make_smoke_detector("Smoke", (+1.0, 1.5, CEIL))

def build_hero_props():
    """2026-08-03 tail pass: the small desk under the N window
    (paper, pen, the addressed envelope), the dresser + the small
    mirror above it."""
    wood = (0.38, 0.28, 0.18, 1.0)
    make_box("Desk_Top", (1.10, 4.55, 0.74), (1.00, 0.55, 0.05), wood)
    # legs and drawer follow the top (2026-09-10: the top moved to x 1.1
    # on 2026-09-07 but the legs and drawer stayed at x 0)
    for lx in (-0.44, 0.44):
        make_box(f"Desk_Leg_{lx:+.2f}", (1.10 + lx, 4.55, 0.37), (0.06, 0.50, 0.72), wood)
    make_box("Desk_Drawer", (1.10, 4.30, 0.62), (0.60, 0.02, 0.12), (0.30, 0.22, 0.14, 1.0))
    # on the desk, W of the basin (2026-09-23: the three stayed at the
    # desk's old x 0 when the top moved to 1.1 — over the pillow, on air)
    make_box("Letter_Paper", (0.78, 4.50, 0.7675), (0.16, 0.22, 0.005), (0.92, 0.90, 0.84, 1.0))
    make_box("Letter_Pen", (0.90, 4.48, 0.770), (0.02, 0.13, 0.01), (0.14, 0.14, 0.16, 1.0))
    make_box("Addressed_Envelope", (1.06, 4.64, 0.7675), (0.20, 0.10, 0.005), (0.90, 0.88, 0.82, 1.0))
    # Dresser + the small mirror
    make_box("Dresser", (-1.675, 2.60, 0.44), (0.45, 1.00, 0.88), wood)   # against the W wall face (2026-09-24: 7.5 cm into it)
    for di in range(3):
        make_box(f"Dresser_Drawer_{di}", (-1.445, 2.60, 0.20 + di * 0.26), (0.02, 0.86, 0.20), (0.30, 0.22, 0.14, 1.0))
    # (2026-10-03: the mirror hung INSIDE the west wall — its frame at -1.96 behind
    # the wall's face at -1.90 — and under the TV's top; on the face now, raised)
    make_box("Small_Mirror_Frame", (-1.885, 2.60, 1.60), (0.03, 0.44, 0.56), (0.28, 0.20, 0.13, 1.0))
    make_box("Small_Mirror", (-1.865, 2.60, 1.60), (0.01, 0.36, 0.48), (0.68, 0.74, 0.78, 1.0))



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


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    THE TV (the bar's muted game, cut to from this room): a hotel
    set on the dresser under the small mirror. Mirror exists
    (marker only)."""
    make_box("Room_TV", (-1.72, 2.6, 1.08), (0.36, 0.55, 0.40), (0.12, 0.12, 0.13, 1.0))
    make_box("Room_TV_Screen", (-1.535, 2.6, 1.08), (0.010, 0.48, 0.32), (0.35, 0.55, 0.80, 1.0))


def build_room_over_laundromat_2026_10():
    """CHARACTER PASS (2026-10-03). The chapter: "the room above the
    laundromat that Jimmy had rented for him, on a month-to-month, paid
    in cash … smelled, faintly, of dryer sheets … He sat at the small
    desk under the window … the small mirror above the dresser … He went
    to the window. He looked down at the street … The chain rattled
    once." The window is over the desk now (it was over the bed's
    head); the LAUNDROMAT sign glows up from the facade below it, the
    street three floors down; the door has its chain; and the small
    things of a man living out of a duffle: the shade half drawn, a
    towel on its hook, shoes under the bed, a rug, paperbacks on the
    dresser, the radio and the mug on the desk, the key and the
    cigarettes on the nightstand, a wastebasket."""
    wood = (0.38, 0.28, 0.18, 1.0)
    # ── the door in the south opening, with its chain
    for sx in (-0.675, 0.675):
        make_box(f"Wall_S_Fill_{sx:+.2f}", (sx, 0.0, 1.40), (0.45, 0.20, 2.80), PAL["wall"])
        make_box(f"Wall_S_Fill_{sx:+.2f}_Base", (sx, 0.106, 0.08), (0.45, 0.012, 0.16), PAL["baseboard"])
    make_box("Wall_S_AboveDoor", (0.0, 0.0, 2.50), (0.90, 0.20, 0.60), PAL["wall"])
    make_box("Room_Door", (0.0, 0.06, 1.05), (0.88, 0.05, 2.10), (0.42, 0.32, 0.22, 1.0))
    make_cyl("Room_Door_Knob", (0.34, 0.10, 1.02), 0.028, 0.04, (0.72, 0.60, 0.30, 1.0), segments=8, axis='Y')
    make_box("Door_Chain_Plate", (0.30, 0.095, 1.50), (0.06, 0.012, 0.04), (0.62, 0.62, 0.60, 1.0))
    make_box("Door_Chain_Slide", (0.56, 0.115, 1.50), (0.08, 0.012, 0.03), (0.62, 0.62, 0.60, 1.0))
    make_tube("Door_Chain", [(0.32, 0.10, 1.48), (0.44, 0.11, 1.40), (0.54, 0.12, 1.49)], 0.006, (0.66, 0.66, 0.64, 1.0), segments=5)
    # ── the window's shade half drawn; the LAUNDROMAT sign and the street below
    make_box("Window_Shade", (0.9, ROOM_D - 0.16, 2.02), (1.20, 0.02, 0.36), (0.90, 0.86, 0.74, 1.0))
    make_cyl("Window_Shade_Roll", (0.9, ROOM_D - 0.16, 2.22), 0.03, 1.24, (0.42, 0.30, 0.20, 1.0), segments=8, axis='X')
    make_box("Laundromat_Sign_Box", (0.9, ROOM_D + 0.22, -0.55), (2.60, 0.24, 0.60), (0.86, 0.84, 0.80, 1.0))
    make_box("Laundromat_Sign_Face", (0.9, ROOM_D + 0.345, -0.55), (2.40, 0.01, 0.46), (0.96, 0.46, 0.66, 1.0))
    make_box("Laundromat_Sign_Text", (0.9, ROOM_D + 0.352, -0.55), (2.00, 0.004, 0.18), (0.98, 0.94, 0.96, 1.0))
    make_box("Out_Facade_Below", (0.0, ROOM_D + 0.10, -1.9), (12.0, 0.2, 3.6), (0.56, 0.48, 0.40, 1.0))
    make_box("Out_Facade_Above", (0.0, ROOM_D + 0.10, 4.2), (12.0, 0.2, 3.0), (0.56, 0.48, 0.40, 1.0))
    make_box("Ground_Sidewalk", (0.0, ROOM_D + 2.0, -3.63), (12.0, 3.6, 0.06), (0.52, 0.50, 0.46, 1.0))
    make_box("Ground_Street", (0.0, ROOM_D + 8.0, -3.70), (14.0, 8.5, 0.06), (0.26, 0.26, 0.28, 1.0))
    make_box("Out_Facade_Across", (0.0, ROOM_D + 12.5, 1.5), (14.0, 0.4, 10.0), (0.44, 0.36, 0.30, 1.0))
    for c in range(6):
        for r in range(3):
            make_box(f"Across_Win_{c}_{r}", (-5.5 + c * 2.2, ROOM_D + 12.29, -1.5 + r * 2.8), (1.0, 0.02, 1.4), [(0.92, 0.78, 0.40, 1.0), (0.14, 0.16, 0.20, 1.0)][(c + r) % 2])
    make_cyl("Street_Lamp", (-2.5, ROOM_D + 1.2, -1.6), 0.05, 4.0, (0.20, 0.22, 0.24, 1.0), segments=8)
    make_box("Street_Lamp_Head", (-2.5, ROOM_D + 1.5, 0.35), (0.28, 0.40, 0.14), (0.96, 0.88, 0.60, 1.0))
    # ── a man living out of a duffle
    make_box("Hook_Towel_Hook", (ROOM_W / 2.0 - 0.115, 3.70, 1.60), (0.03, 0.03, 0.05), (0.62, 0.62, 0.60, 1.0))
    make_box("Hook_Towel", (ROOM_W / 2.0 - 0.145, 3.70, 1.30), (0.03, 0.30, 0.60), (0.72, 0.68, 0.58, 1.0))
    make_box("Shoe_A", (-0.35, 2.80, 0.05), (0.11, 0.28, 0.10), (0.18, 0.16, 0.14, 1.0))
    make_rot_box("Shoe_B", (-0.18, 2.78, 0.05), (0.11, 0.28, 0.10), (0.18, 0.16, 0.14, 1.0), yaw=0.25)
    make_box("Bedside_Rug", (-0.1, 2.35, 0.006), (0.70, 0.90, 0.012), (0.46, 0.34, 0.30, 1.0))
    make_box("Bedside_Rug_Border", (-0.1, 2.35, 0.013), (0.60, 0.80, 0.002), (0.62, 0.52, 0.40, 1.0))
    for i in range(3):
        make_box(f"Paperback_{i}", (-1.62, 3.00, 0.88 + 0.022 * i + 0.011), (0.11 - 0.01 * i, 0.17, 0.022), [(0.52, 0.20, 0.16, 1.0), (0.86, 0.82, 0.72, 1.0), (0.24, 0.34, 0.46, 1.0)][i])
    make_box("Transistor_Radio", (1.45, 4.70, 0.815), (0.16, 0.08, 0.10), (0.30, 0.28, 0.26, 1.0))
    make_box("Transistor_Radio_Grille", (1.45, 4.658, 0.815), (0.10, 0.004, 0.07), (0.62, 0.58, 0.50, 1.0))
    make_cyl("Transistor_Aerial", (1.50, 4.72, 1.02), 0.003, 0.30, (0.70, 0.70, 0.72, 1.0), segments=5)
    make_mug("Desk_Mug", 0.72, 4.72, 0.765, (0.42, 0.44, 0.50, 1.0))
    make_box("Room_Key", (-1.05, 4.25, 0.81), (0.06, 0.025, 0.006), (0.72, 0.62, 0.30, 1.0))
    make_box("Key_Tag", (-1.10, 4.25, 0.81), (0.04, 0.03, 0.006), (0.86, 0.30, 0.26, 1.0))
    make_box("Cigarette_Pack", (-0.85, 4.45, 0.81), (0.055, 0.085, 0.02), (0.84, 0.82, 0.76, 1.0))
    make_cyl("Wastebasket", (1.55, 4.00, 0.13), 0.12, 0.26, (0.30, 0.32, 0.34, 1.0), segments=10)
    make_box("Wastebasket_Crumple", (1.52, 4.02, 0.28), (0.07, 0.07, 0.06), (0.90, 0.88, 0.82, 1.0))
    make_box("Dryer_Sheet_Box", (-1.72, 2.20, 0.93), (0.14, 0.10, 0.10), (0.44, 0.70, 0.86, 1.0))


def main():
    clear_scene(); build_shell(); build_bed(); build_washbasin(); build_decor(); build_ceiling_infra()
    build_hero_props()
    build_detail_pass_2026_08()
    build_hero_props_2026_09()
    build_room_over_laundromat_2026_10()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/new_orleans_room.glb"))
    print(f"\n[build_new_orleans_room] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
