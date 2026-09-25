"""VOL 5 · New Orleans Office — period law/insurance office. Heavy
oak desk, leather chair, wood paneling, banker's-lamp green-glass.

DRAFT 3 (2026-09-19, lore/_VISUAL_PROGRAM.md §3 backgrounds pass, the
arcana primitive upgrade's second room; 2 VN placements + the board).
LAYOUT the gates never reported: the desk's modesty panel faced the
SITTER (knees into oak); the filing cabinet stood in front of the
back-stair door; the west wainscot panels sat INSIDE the wall (behind
its face — invisible); the AC was wedged into a street window that
did not exist; the entry wear line ran from mid-wall through the
chair; the banker's-lamp practical hung 0.85 m off its lamp. The
panel is on the visitor's side, the cabinet up the east wall, the
wainscot proud of the face, the south window built, the bourbon on
the desk beside the chipped glass (the marker follows it).
PRIMITIVES: the kit pendant; the banker's lamp as base + stem +
rolled green shade; the executive chair with a five-star base,
casters, arms and a headroll; a rotary phone (dial, cradle, handset
arc, coiled cord); the inkwell a profile; a leather inlay on the
desk. WEAR personality: the pacing carpet stays; the sitter's floor
arc behind the desk, the drawer-pull patch on the second drawer, the
desk's elbow strips, the door-side kick. D3: the lamp's cord, the
phone's line to a wall jack, the AC's cord. D5: the gallery rail and
the neighbour's brick past the east window; the street past the
south ones. Scene: the lamp practical onto the lamp.
Draft 4 targets: the room at canon's twelve-by-ten (it is four times
the size — the full rebuild the audit doc notes); the ceiling fan;
the transom over the front door; the rolled plans as a tube with
paper ends; Deck: the preset from the SW + establish_b.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_chamfer_box, make_lathe, make_tube, make_rot_box, export_glb
from _props.furniture import make_pendant
from _props.structure import make_floor, make_wall, make_ceiling, make_window, make_crown_molding
from _props.decor import make_wall_clock, make_faded_poster, make_floor_plant
from _props.safety import make_fluorescent_tube_fixture, make_smoke_detector
from _props.detail import (make_floor_stain, make_traffic_wear, make_wall_outlet, make_wall_tint_band, make_scuff_band)

PAL = {"wall": (0.46, 0.32, 0.22, 1.0), "baseboard": (0.22, 0.16, 0.12, 1.0)}
COL_FLOOR = (0.42, 0.30, 0.20, 1.0); COL_SEAM = (0.22, 0.16, 0.12, 1.0)
COL_OAK = (0.46, 0.32, 0.20, 1.0); COL_OAK_DARK = (0.22, 0.14, 0.10, 1.0); COL_BRASS = (0.86, 0.62, 0.28, 1.0)
COL_LEATHER = (0.32, 0.20, 0.14, 1.0); COL_BANKER_GREEN = (0.20, 0.46, 0.22, 1.0)
COL_BOOK = [(0.62, 0.32, 0.30, 1.0), (0.42, 0.30, 0.18, 1.0), (0.30, 0.42, 0.32, 1.0), (0.42, 0.42, 0.18, 1.0)]
ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 3.20

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_S", (0.0, 0.0, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=+1)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"tile": (0.62, 0.42, 0.22, 1.0)})
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10),("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_OAK_DARK})
    # Tall window E wall (afternoon sun)
    # (2026-09-24: a SOLID black slab the size of the window stood inside
    # the E wall with the glass behind it — the insert framed a black
    # rectangle. A frame of four bars on the wall face now, the glass in it.)
    fx = ROOM_W/2.0 - 0.12
    for tag, (fy, fz, sy, sz) in (("T", (3.0, 2.85, 1.80, 0.10)), ("B", (3.0, 0.75, 1.80, 0.10)),
                                  ("L", (2.15, 1.80, 0.10, 2.20)), ("R", (3.85, 1.80, 0.10, 2.20))):
        make_box(f"Window_E_Frame_{tag}", (fx, fy, fz), (0.04, sy, sz), P.METAL_BLACK)
    make_box("Window_E_Glass", (fx - 0.005, 3.0, 1.80), (0.005, 1.60, 2.00), (0.96, 0.86, 0.62, 0.70))
    # Wainscoting along west wall (vertical wood panels)
    for pi in range(6):
        py = 0.5 + pi*1.0
        # (draft 3: proud of the wall FACE at -3.40 — at +0.06 from the
        # wall centre the panels sat inside the wall)
        make_box(f"Wainscot_W_{pi}", (-ROOM_W/2.0+0.103, py, 0.55), (0.006, 0.96, 1.10), COL_OAK_DARK)
    # The south street window the AC is wedged into (draft 3: it had
    # never been built) — west of the leaded window
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    make_window("Window_S", (-0.80, 0.10, 1.45), width=1.40, height=1.20, room_dir=+1)

def build_desk_and_chair():
    # Heavy oak desk in centre
    dx, dy = 0.0, 3.5
    make_box("Desk_Top", (dx, dy, 0.76), (2.20, 1.00, 0.06), COL_OAK)
    # Modesty panel on the VISITOR's side (draft 3: it faced the chair)
    make_box("Desk_Front", (dx, dy+0.50, 0.40), (2.20, 0.05, 0.70), COL_OAK_DARK)
    make_box("Desk_Inlay", (dx, dy, 0.792), (1.60, 0.62, 0.004), (0.24, 0.14, 0.10, 1.0))
    # Side panels (with drawers facing the sitter)
    for sgn in (-1, +1):
        make_box(f"Desk_Side_{sgn:+d}", (dx+sgn*1.05, dy, 0.40), (0.10, 1.00, 0.74), COL_OAK_DARK)
        # 3 drawers
        for di in range(3):
            make_box(f"Desk_Drawer_{sgn:+d}_{di}", (dx+sgn*1.05, dy-0.40, 0.62 - di*0.22), (0.04, 0.50, 0.16), COL_OAK)
            make_cyl(f"Desk_DrawerKnob_{sgn:+d}_{di}", (dx+sgn*1.10, dy-0.40, 0.62 - di*0.22), 0.025, 0.04, COL_BRASS, axis='X')
    # Leather executive chair (draft 3: five-star base, casters, a
    # pillar, arms, a headroll)
    cx_, cy_ = dx, dy-0.80
    make_chamfer_box("Chair_Seat", (cx_, cy_, 0.50), (0.62, 0.50, 0.10), COL_LEATHER, chamfer=0.03)
    make_chamfer_box("Chair_Back", (cx_, cy_-0.22, 1.10), (0.62, 0.06, 1.20), COL_LEATHER, chamfer=0.02)
    make_cyl("Chair_Headroll", (cx_, cy_-0.19, 1.62), 0.06, 0.58, COL_LEATHER, axis='X', segments=10)
    for ai, ax in enumerate((-0.33, 0.33)):
        make_tube(f"Chair_Arm_{ai}", [(cx_ + ax, cy_ - 0.20, 0.55), (cx_ + ax, cy_ - 0.20, 0.75), (cx_ + ax, cy_ + 0.18, 0.75)], 0.018, COL_OAK_DARK, segments=6)
    make_lathe("Chair_Pillar", (cx_, cy_, 0.06), [(0.045, 0.0), (0.045, 0.32), (0.06, 0.36), (0.06, 0.39), (0.0, 0.39)], P.METAL_BLACK, segments=8)
    import math as _m
    for si in range(5):
        a = si * 2.0 * _m.pi / 5.0
        make_rot_box(f"Chair_Star_{si}", (cx_ + 0.15 * _m.cos(a), cy_ + 0.15 * _m.sin(a), 0.055), (0.30, 0.04, 0.035), P.METAL_BLACK, yaw=a)
        make_cyl(f"Chair_Caster_{si}", (cx_ + 0.29 * _m.cos(a), cy_ + 0.29 * _m.sin(a), 0.025), 0.025, 0.04, P.METAL_BLACK, axis='Y', segments=6)
    # Banker's lamp (draft 3: a weighted base, a brass stem, the rolled
    # green shade — its practical sits on the shade)
    lx_, ly_ = dx-0.60, dy+0.20
    make_lathe("Lamp_Base", (lx_, ly_, 0.79), [(0.0, 0.0), (0.09, 0.0), (0.08, 0.02), (0.04, 0.03), (0.012, 0.035), (0.012, 0.22), (0.0, 0.22)], COL_BRASS, segments=10)
    make_tube("Lamp_Arm", [(lx_, ly_, 1.00), (lx_, ly_ - 0.06, 1.06)], 0.008, COL_BRASS, segments=5)
    make_cyl("Lamp_Shade", (lx_, ly_ - 0.06, 1.06), 0.075, 0.36, COL_BANKER_GREEN, axis='X', segments=10)
    make_cyl("Lamp_Shade_Cap_0", (lx_ - 0.185, ly_ - 0.06, 1.06), 0.078, 0.01, COL_BRASS, axis='X', segments=10)
    make_cyl("Lamp_Shade_Cap_1", (lx_ + 0.185, ly_ - 0.06, 1.06), 0.078, 0.01, COL_BRASS, axis='X', segments=10)
    # Rotary phone (draft 3: body, dial, cradle, handset arc, coiled cord)
    px_, py_ = dx+0.50, dy+0.20
    make_chamfer_box("Phone_Base", (px_, py_, 0.83), (0.20, 0.24, 0.08), COL_LEATHER, chamfer=0.015)
    make_lathe("Phone_Dial", (px_, py_ - 0.06, 0.87), [(0.0, 0.0), (0.05, 0.0), (0.05, 0.008), (0.0, 0.008)], (0.90, 0.88, 0.80, 1.0), segments=12)
    make_box("Phone_Cradle", (px_, py_ + 0.06, 0.885), (0.16, 0.05, 0.03), COL_LEATHER)
    make_tube("Phone_Handset", [(px_ - 0.10, py_ + 0.06, 0.92), (px_, py_ + 0.06, 0.96), (px_ + 0.10, py_ + 0.06, 0.92)], 0.02, COL_LEATHER, segments=8)
    make_tube("Phone_Cord", [(px_ + 0.10, py_ + 0.12, 0.83), (px_ + 0.22, py_ + 0.25, 0.81), (px_ + 0.32, py_ + 0.40, 0.80)], 0.006, COL_LEATHER, segments=5)
    # Papers + inkwell
    make_box("Papers", (dx, dy+0.10, 0.80), (0.36, 0.26, 0.02), P.PAPER)
    make_lathe("Inkwell", (dx-0.75, dy+0.35, 0.79), [(0.0, 0.0), (0.04, 0.0), (0.045, 0.04), (0.03, 0.06), (0.018, 0.065), (0.018, 0.075), (0.0, 0.075)], COL_OAK_DARK, segments=8)

def build_bookcase_and_filing():
    # Floor-to-near-ceiling bookcase west wall
    # the case's sides (2026-09-23: six shelves on nothing)
    for sy_ in (1.78, 4.22):
        make_box(f"BookCase_Side_{sy_:.2f}", (-3.2, sy_, 1.30), (0.40, 0.04, 2.60), COL_OAK_DARK)   # to the W wall's face (2026-09-25: 20 cm off it)
    for shf in range(6):
        sz = 0.30 + shf*0.45
        make_box(f"BookCase_Shelf_{shf}", (-3.0, 3.0, sz), (0.40, 2.40, 0.04), COL_OAK_DARK)
        for bi in range(10):
            make_box(f"Book_{shf}_{bi}", (-3.0, 1.9 + bi*0.22, sz + 0.20), (0.16, 0.18, 0.36), COL_BOOK[(shf+bi)%len(COL_BOOK)])   # ON the shelf (2026-09-23: 2 cm into it)
    # Filing cabinet north-east
    # (draft 3: up the east wall at y 4.9 — at 5.5 it stood in front of
    # the back-stair door)
    make_box("Filing_Body", (+3.1, 4.9, 0.65), (0.50, 0.60, 1.30), COL_OAK_DARK)
    for di in range(4):
        make_box(f"Filing_Drawer_{di}", (+3.1, 4.60, 1.20 - di*0.30), (0.46, 0.04, 0.26), COL_OAK)
        make_box(f"Filing_Handle_{di}", (+3.1, 4.58, 1.20 - di*0.30), (0.16, 0.04, 0.02), COL_BRASS)

def build_decor():
    make_wall_clock("Clock", (0.0, 5.900, 2.50), frozen_hour=3, frozen_min=42, facing='-Y')
    make_faded_poster("DiplomaW", (-3.3965, 4.5, 2.10), palette={"body": P.PAPER_AGED}, into_room=+1)
    make_faded_poster("DiplomaE", (-3.3965, 4.5, 1.55), palette={"body": P.PAPER_AGED}, into_room=+1)
    make_floor_plant("Plant", (+2.5, 1.0, 0.0))

def build_ceiling_infra():
    # Single overhead pendant (warm)
    make_pendant("Pendant", 0.0, 3.0, CEIL - 0.85, CEIL, shade_col=COL_BANKER_GREEN, cord_col=P.METAL_BLACK, shade_r=0.26)
    make_smoke_detector("Smoke", (0.0, 1.5, CEIL))

def build_hero_props():
    """2026-08-03 tail pass: the two exits the scenes need (front
    iron-stair door + back-stair door), the personality-having
    window AC unit, the small leaded window, the emergency bourbon
    + chipped glass, the rolled plans, the pacing carpet. (Known
    deferred: the room is ~4x canon's twelve-by-ten and dressed a
    genre too grand — full rebuild noted in the audit doc.)"""
    wood = (0.36, 0.26, 0.16, 1.0)
    # Front door (to the rusted iron stair), S wall west end
    make_box("Front_Door", (-2.6, 0.06, 1.05), (0.95, 0.06, 2.10), wood)
    make_cyl("Front_Knob", (-2.25, 0.10, 1.02), 0.03, 0.04, (0.66, 0.52, 0.24, 1.0), axis='Y', segments=8)
    # Back-stair door, N wall east end
    make_box("Back_Door", (2.6, ROOM_D-0.06, 1.05), (0.95, 0.06, 2.10), wood)
    # The window AC, wedged into the S street window, half-capacity
    make_box("Window_AC", (-0.80, 0.10, 1.10), (0.60, 0.45, 0.40), (0.78, 0.76, 0.70, 1.0))
    make_box("Window_AC_Grille", (-0.80, -0.14, 1.10), (0.50, 0.02, 0.30), (0.60, 0.58, 0.54, 1.0))
    # The small leaded window beside it (the charcoal-suit watch)
    # on the wall's room face, glass in front of the frame (2026-09-24: frame and glass
    # were offset from the wall's CENTRE line — inside the wall, never visible)
    make_box("Leaded_Win_Frame", (0.85, 0.14, 1.45), (0.80, 0.08, 0.90), wood)
    make_box("Leaded_Win_Glass", (0.85, 0.205, 1.45), (0.66, 0.05, 0.76), (0.50, 0.56, 0.60, 0.5))
    make_box("Leaded_Win_MullV", (0.85, 0.20, 1.45), (0.03, 0.04, 0.76), wood)
    make_box("Leaded_Win_MullH", (0.85, 0.20, 1.45), (0.66, 0.04, 0.03), wood)
    # Emergency bourbon (second drawer) + the chipped glass on the desk
    # (draft 3: on the desk beside the glass — out of the second drawer,
    # which is where it lives; at (2.75, 5.15) it stood on the floor by
    # the filing cabinet)
    make_lathe("Bourbon_Bottle", (0.55, 3.45, 0.79), [(0.0, 0.0), (0.045, 0.0), (0.05, 0.03), (0.05, 0.17), (0.03, 0.22), (0.016, 0.24), (0.016, 0.28), (0.0, 0.28)], (0.48, 0.30, 0.12, 0.9), segments=8)
    make_cyl("Chipped_Glass", (0.35, 3.45, 0.83), 0.04, 0.09, (0.72, 0.74, 0.70, 0.6), segments=8)
    # The rolled architectural plans on the desk
    for ri, (rx, ry) in enumerate(((-0.35, 3.60), (-0.28, 3.72))):
        make_cyl(f"Plans_Roll_{ri}", (rx, ry, 0.84), 0.045, 0.75, (0.88, 0.85, 0.76, 1.0), segments=8, axis='X')
    # The pacing carpet, worn path visible
    make_box("Pacing_Carpet", (0.0, 2.2, 0.012), (2.6, 1.4, 0.015), (0.36, 0.26, 0.22, 1.0))
    make_box("Pacing_Path", (0.0, 2.2, 0.022), (2.0, 0.45, 0.006), (0.30, 0.21, 0.18, 1.0))



def build_detail_pass_2026_08():
    """D2 surface breakup + first D3 (adaptive template pass per
    lore/_SET_DETAIL_PLAYBOOK.md). Per-locale wear personality is
    the next pass."""
    wear = (COL_FLOOR[0] * 0.88, COL_FLOOR[1] * 0.88, COL_FLOOR[2] * 0.88, 1.0)
    # (draft 3: from the front door east along the south wall, and the
    # back door's line — the old line ran from mid-wall into the chair)
    make_traffic_wear("Wear_Entry", [(-2.6, 0.35), (-2.6, 1.2), (-1.6, 1.2)], width=0.6, tint=wear)
    make_traffic_wear("Wear_Back", [(2.4, 5.6), (2.4, 4.6)], width=0.5, tint=wear)
    make_floor_stain("Stain_WorkZone", (ROOM_W * 0.22, ROOM_D * 0.62), radius=0.24,
                     tint=(COL_FLOOR[0] * 0.82, COL_FLOOR[1] * 0.82, COL_FLOOR[2] * 0.82, 1.0))
    pw = PAL["wall"]
    band = (pw[0] * 0.90, pw[1] * 0.90, pw[2] * 0.88, 1.0)
    make_wall_tint_band("Band_W", (-ROOM_W / 2.0 + 0.105, ROOM_D / 2.0, 0.0),
                        length=ROOM_D - 0.4, axis='Y', band_z=CEIL - 0.16, tint=band)
    make_wall_tint_band("Band_E", (ROOM_W / 2.0 - 0.105, ROOM_D / 2.0, 0.0),
                        length=ROOM_D - 0.4, axis='Y', band_z=CEIL - 0.16, tint=band)
    make_wall_outlet("Outlet_W", (-ROOM_W / 2.0, ROOM_D * 0.35), axis='Y',
                     face_sign=1, aged=True)
    make_wall_outlet("Outlet_E", (ROOM_W / 2.0, ROOM_D * 0.70), axis='Y',
                     face_sign=-1, aged=True)


def build_draft3_2026_09():
    """DRAFT 3 (2026-09-19) · wear personality, cords, both windows'
    outsides. No part name carries a cue word (phone · bourbon · window)."""
    wear = (COL_FLOOR[0] * 0.86, COL_FLOOR[1] * 0.86, COL_FLOOR[2] * 0.86, 1.0)
    cord = (0.16, 0.16, 0.18, 1.0)
    # the sitter's arc behind the desk (the chair rolls), the pull patch
    # on the second drawer, the elbow strips, the kick by the front door
    make_floor_stain("Wear_Chair_Arc", (0.0, 2.55), radius=0.45, tint=wear, segments=12)
    make_box("Wear_Pull_Patch", (1.113, 3.10, 0.40), (0.003, 0.14, 0.10), (0.56, 0.42, 0.28, 1.0))
    for ei, ey in enumerate((3.03, 3.97)):
        make_box(f"Wear_Elbow_{ei}", (0.0, ey, 0.7915), (1.9, 0.05, 0.003), (0.38, 0.26, 0.16, 1.0))
    make_scuff_band("Wear_Door_Kick", (-2.6, 0.106), 0.9, axis='X', height=0.12, band_z=0.20, tint=(0.24, 0.16, 0.12, 1.0))
    # D3 · the lamp's cord off the desk's back to Outlet_E's wall, the
    # phone's line to a jack, the AC's cord
    make_wall_outlet("Outlet_N_1", (-0.60, ROOM_D), axis='X', face_sign=-1, z=0.30, aged=True)
    make_tube("Cord_1", [(-0.60, 4.02, 0.78), (-0.60, ROOM_D - 0.13, 0.30)], 0.008, cord, segments=5)
    make_box("Phone_Jack", (0.90, ROOM_D - 0.115, 0.32), (0.06, 0.012, 0.06), (0.82, 0.79, 0.68, 1.0))
    make_tube("Cord_2", [(0.82, 3.98, 0.80), (0.90, ROOM_D - 0.13, 0.32)], 0.006, COL_LEATHER, segments=5)
    make_wall_outlet("Outlet_S_1", (-1.60, 0.0), axis='X', face_sign=1, z=0.30, aged=True)
    make_tube("Cord_3", [(-1.05, 0.33, 0.95), (-1.60, 0.13, 0.30)], 0.008, cord, segments=5)
    # D5 · past the east window: the gallery's iron rail and the
    # neighbour's brick; past the south windows: the street and the
    # building across
    make_box("Out_E_Gallery", (4.2, 3.0, 0.0), (1.4, 8.0, 0.06), (0.30, 0.28, 0.26, 1.0))
    for pi_, py_ in enumerate((1.2, 2.4, 3.6, 4.8)):
        make_lathe(f"Out_E_Rail_Post_{pi_}", (4.8, py_, 0.03), [(0.02, 0.0), (0.02, 1.0), (0.03, 1.0), (0.03, 1.04), (0.0, 1.04)], (0.14, 0.14, 0.15, 1.0), segments=6)
    make_tube("Out_E_Rail_Top", [(4.8, 0.9, 1.02), (4.8, 5.1, 1.02)], 0.02, (0.14, 0.14, 0.15, 1.0), segments=6)
    make_tube("Out_E_Rail_Mid", [(4.8, 0.9, 0.55), (4.8, 5.1, 0.55)], 0.014, (0.14, 0.14, 0.15, 1.0), segments=6)
    make_box("Out_E_Ground", (6.9, 3.0, -0.03), (4.4, 12.0, 0.05), (0.26, 0.26, 0.24, 1.0))
    make_box("Out_E_Brick", (8.5, 3.0, 3.0), (0.4, 12.0, 6.0), (0.50, 0.34, 0.28, 1.0))
    for si_, sy_ in enumerate((2.0, 4.2)):
        make_box(f"Out_E_Shutter_{si_}", (8.28, sy_, 2.2), (0.04, 0.9, 1.8), (0.16, 0.24, 0.20, 1.0))
    make_box("Out_S_Street", (0.0, -4.0, -0.03), (16.0, 7.0, 0.05), (0.30, 0.30, 0.32, 1.0))
    make_box("Out_S_Facade", (0.0, -7.8, 3.0), (16.0, 0.4, 6.0), (0.56, 0.48, 0.40, 1.0))
    make_box("Out_S_Balcony", (0.0, -7.4, 3.2), (12.0, 0.5, 0.08), (0.14, 0.14, 0.15, 1.0))


def main():
    clear_scene(); build_shell(); build_desk_and_chair(); build_bookcase_and_filing(); build_decor(); build_ceiling_infra()
    build_hero_props()
    build_detail_pass_2026_08()
    build_draft3_2026_09()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/new_orleans_office.glb"))
    print(f"\n[build_new_orleans_office] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
