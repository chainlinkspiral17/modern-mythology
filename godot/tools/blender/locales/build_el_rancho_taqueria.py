"""el_rancho_taqueria — El Rancho, the taqueria (vols 5-7).

2026-08-03 tail pass: the round pedestal 2-tops (where group scenes
stage) are replaced with the LONG BOOTH + two square 6-tops the
prose seats; added the DRIVE-THRU window on the E wall with its
speaker box and the taped "SPEAKER BROKE — PULL FORWARD" sign, the
tip jar, the counter's yellow order pad, and the sauce-packet box.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture
from _props.objects import make_bottle

ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 2.8
PAL_WALL = {"wall":(0.96,0.84,0.62,1.0),"baseboard":(0.62,0.42,0.22,1.0)}
COL_FLOOR = (0.62,0.46,0.30,1.0); COL_SEAM = (0.32,0.22,0.14,1.0); COL_WOOD = (0.42,0.30,0.18,1.0)
COL_ACCENT = (0.78,0.42,0.22,1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)

def build_register_counter():
    top_z = make_counter("Register", (ROOM_W/4.0, ROOM_D-1.5, 0.0), length=2.40, depth=1.00, height=0.95,
                         palette={"formica": COL_WOOD, "top": (0.18, 0.12, 0.20, 1.0), "kick": (0.18, 0.12, 0.20, 1.0)})
    make_register("RegisterMachine", (ROOM_W/4.0, ROOM_D-1.5-0.30, top_z))
    # Chip warmer on the counter — metal case, warm lamp, tortilla chips.
    cx, cy = ROOM_W/4.0-0.85, ROOM_D-1.5
    make_box("ChipWarmer_Body", (cx, cy, top_z+0.22), (0.46,0.46,0.40), P.METAL_STEEL)
    make_box("ChipWarmer_Glass", (cx-0.24, cy, top_z+0.24), (0.02,0.42,0.34), P.GLASS_WARM)
    make_box("ChipWarmer_Lamp", (cx, cy, top_z+0.42), (0.44,0.44,0.03), (1.0,0.78,0.32,1.0))
    for i in range(3):
        make_box(f"Chips_{i}", (cx-0.12+i*0.12, cy, top_z+0.10), (0.08,0.32,0.14), (0.92,0.78,0.42,1.0))
    # Tip jar by the register (a few coins + folded bills).
    jx, jy = ROOM_W/4.0+0.55, ROOM_D-1.85
    make_cyl("TipJar", (jx, jy, top_z+0.09), 0.055, 0.18, (0.80, 0.86, 0.88, 0.55), segments=10)
    make_box("TipJar_Bills", (jx, jy, top_z+0.06), (0.07, 0.05, 0.05), (0.55, 0.62, 0.48, 1.0))
    make_box("TipJar_Label", (jx, jy-0.055, top_z+0.10), (0.07, 0.005, 0.05), (0.94, 0.92, 0.84, 1.0))
    # The yellow order pad + pen by the register.
    make_box("Order_Pad", (ROOM_W/4.0+0.35, ROOM_D-1.25, top_z+0.012), (0.15, 0.21, 0.012), (0.94, 0.88, 0.42, 1.0))
    make_cyl("Order_Pen", (ROOM_W/4.0+0.50, ROOM_D-1.20, top_z+0.02), 0.007, 0.13, (0.20, 0.24, 0.40, 1.0), axis='Y', segments=6)
    # Cardboard sauce-packet box at the counter's end.
    make_box("Sauce_Box", (ROOM_W/4.0+0.95, ROOM_D-1.5, top_z+0.07), (0.30, 0.24, 0.13), (0.62, 0.50, 0.34, 1.0))
    for si2 in range(6):
        make_box(f"Sauce_Packet_{si2}", (ROOM_W/4.0+0.86+0.06*(si2%3), ROOM_D-1.56+0.07*(si2//3), top_z+0.145),
                 (0.05, 0.06, 0.012), (0.70, 0.18, 0.12, 1.0))

def build_menu_board():
    mx, my, mz = ROOM_W/4.0, ROOM_D-0.06, 2.05
    make_box("MenuBoard_Frame", (mx, my+0.01, mz), (2.34, 0.02, 1.02), P.METAL_STEEL)
    make_box("MenuBoard", (mx, my, mz), (2.24, 0.04, 0.92), (0.14,0.13,0.12,1.0))
    row_cols = [(0.98,0.86,0.44,1.0),(0.92,0.62,0.28,1.0),(0.86,0.44,0.30,1.0),(0.72,0.82,0.60,1.0)]
    for col_i in range(2):
        for row in range(4):
            make_box(f"Menu_{col_i}_{row}", (mx-0.55+col_i*1.10, my-0.03, mz+0.28-row*0.18),
                     (0.80, 0.005, 0.05), row_cols[row])

def build_salsa_station():
    sx, sy = -ROOM_W/2.0+0.8, ROOM_D-1.2
    make_box("Salsa_Table", (sx, sy, 0.45), (1.10, 0.62, 0.06), COL_WOOD)
    for k,(ox,oy) in enumerate([(-0.46,-0.24),(0.46,-0.24),(-0.46,0.24),(0.46,0.24)]):
        make_box(f"Salsa_Leg_{k}", (sx+ox, sy+oy, 0.24), (0.05,0.05,0.42), COL_WOOD)
    salsa_cols = [(0.72,0.20,0.16,1.0),(0.36,0.52,0.24,1.0),(0.86,0.62,0.24,1.0)]
    for i in range(3):
        px = sx-0.34+i*0.34
        make_box(f"SalsaPan_{i}", (px, sy-0.05, 0.51), (0.26,0.32,0.10), P.METAL_STEEL)
        make_box(f"Salsa_{i}", (px, sy-0.05, 0.56), (0.22,0.28,0.03), salsa_cols[i])
    for i,col in enumerate([(0.86,0.22,0.16,1.0),(0.86,0.72,0.20,1.0),(0.36,0.46,0.24,1.0)]):
        make_bottle(f"Bottle_{i}", sx + 0.40, sy - 0.20 + i * 0.18, 0.50,
                    col, h=0.16, r=0.026)
    make_box("Napkins", (sx-0.40, sy+0.22, 0.54), (0.16,0.10,0.12), P.METAL_STEEL)

def _make_table(prefix, cx, cy):
    make_cyl(f"{prefix}_Top", (cx, cy, 0.74), 0.42, 0.05, COL_WOOD, segments=12)
    make_cyl(f"{prefix}_Column", (cx, cy, 0.38), 0.06, 0.68, P.METAL_BLACK)
    make_cyl(f"{prefix}_Base", (cx, cy, 0.03), 0.30, 0.05, P.METAL_BLACK, segments=12)
    for ci, ox in enumerate((-0.66, 0.66)):
        chx, chy = cx+ox, cy
        make_box(f"{prefix}_Ch{ci}_Seat", (chx, chy, 0.45), (0.38,0.38,0.05), COL_ACCENT)
        bx = chx + (-0.17 if ox < 0 else 0.17)
        make_box(f"{prefix}_Ch{ci}_Back", (bx, chy, 0.68), (0.04,0.38,0.44), COL_ACCENT)
        for k,(lx,ly) in enumerate([(-0.15,-0.15),(0.15,-0.15),(-0.15,0.15),(0.15,0.15)]):
            make_box(f"{prefix}_Ch{ci}_Leg_{k}", (chx+lx, chy+ly, 0.22), (0.04,0.04,0.42), P.METAL_BLACK)

def build_tables():
    # LONG BOOTH down the W wall — vinyl bench + long table + loose
    # chairs on the room side (seats a crowd, not a couple).
    bx = -ROOM_W/2.0 + 0.50
    make_box("LongBooth_Seat", (bx, 2.4, 0.44), (0.46, 3.4, 0.10), COL_ACCENT)
    make_box("LongBooth_Back", (bx-0.20, 2.4, 0.80), (0.10, 3.4, 0.85), COL_ACCENT)
    make_box("LongBooth_Base", (bx, 2.4, 0.20), (0.44, 3.35, 0.38), (0.40, 0.22, 0.12, 1.0))
    make_box("LongBooth_Table", (bx+0.62, 2.4, 0.74), (0.72, 3.2, 0.05), COL_WOOD)
    for li,(lyo) in enumerate([-1.35, 0.0, 1.35]):
        make_box(f"LongBooth_TLeg_{li}", (bx+0.62, 2.4+lyo, 0.36), (0.06, 0.06, 0.72), P.METAL_BLACK)
    for ci,cyo in enumerate([-1.1, -0.35, 0.35, 1.1]):
        make_box(f"LongBooth_Ch{ci}_Seat", (bx+1.35, 2.4+cyo, 0.45), (0.38, 0.38, 0.05), COL_ACCENT)
        make_box(f"LongBooth_Ch{ci}_Back", (bx+1.52, 2.4+cyo, 0.68), (0.04, 0.38, 0.44), COL_ACCENT)
    # Two square SIX-TOPS mid-floor.
    for ti,(tx,ty) in enumerate([(0.9, 1.6), (0.9, 3.4)]):
        make_box(f"SixTop_{ti}_Top", (tx, ty, 0.74), (1.60, 0.90, 0.05), COL_WOOD)
        for li2,(lxo,lyo) in enumerate([(-0.70,-0.38),(0.70,-0.38),(-0.70,0.38),(0.70,0.38)]):
            make_box(f"SixTop_{ti}_Leg_{li2}", (tx+lxo, ty+lyo, 0.36), (0.06, 0.06, 0.72), P.METAL_BLACK)
        for ci2,(cxo,cyo,along_x) in enumerate([(-0.50,-0.75,True),(0.50,-0.75,True),
                                                (-0.50,0.75,True),(0.50,0.75,True),
                                                (-1.05,0.0,False),(1.05,0.0,False)]):
            make_box(f"SixTop_{ti}_Ch{ci2}_Seat", (tx+cxo, ty+cyo, 0.45), (0.38, 0.38, 0.05), COL_ACCENT)
            if along_x:
                byo = 0.17 if cyo > 0 else -0.17
                make_box(f"SixTop_{ti}_Ch{ci2}_Back", (tx+cxo, ty+cyo+byo, 0.68), (0.38, 0.04, 0.44), COL_ACCENT)
            else:
                bxo = 0.17 if cxo > 0 else -0.17
                make_box(f"SixTop_{ti}_Ch{ci2}_Back", (tx+cxo+bxo, ty+cyo, 0.68), (0.04, 0.38, 0.44), COL_ACCENT)
        # Sauce caddy + napkins on each six-top.
        make_box(f"SixTop_{ti}_Caddy", (tx, ty+0.15, 0.80), (0.16, 0.12, 0.10), (0.72, 0.20, 0.14, 1.0))
        make_box(f"SixTop_{ti}_Napkins", (tx-0.20, ty-0.10, 0.79), (0.13, 0.06, 0.10), P.METAL_STEEL)


def build_drive_thru_2026_08():
    """The DRIVE-THRU on the E wall: sliding service window, the
    outside speaker box, and the taped SPEAKER BROKE sign (the
    order everyone yells through the window instead)."""
    wx = ROOM_W/2.0 - 0.10
    # X-thin window (E wall — hand-built; make_window is Y-axis only).
    make_box("DriveThru_Frame", (wx, 4.6, 1.45), (0.08, 1.30, 1.20), (0.55, 0.55, 0.58, 1.0))
    make_box("DriveThru_Glass", (wx+0.01, 4.85, 1.45), (0.03, 0.60, 1.04), (0.62, 0.72, 0.76, 0.6))
    make_box("DriveThru_Slide", (wx+0.02, 4.30, 1.45), (0.03, 0.55, 1.04), (0.58, 0.68, 0.72, 0.7))
    make_box("DriveThru_Sill", (wx-0.10, 4.6, 0.86), (0.30, 1.40, 0.05), (0.66, 0.62, 0.56, 1.0))
    # Interior headset hook + ticket spike at the window.
    make_cyl("DriveThru_Headset_Hook", (wx-0.14, 5.15, 1.65), 0.02, 0.06, P.METAL_STEEL, axis='X', segments=6)
    make_cyl("DriveThru_Ticket_Spike", (wx-0.16, 4.25, 0.92), 0.006, 0.12, P.METAL_STEEL)
    # Outside: the speaker box on a post + the taped sign.
    make_cyl("Speaker_Post", (ROOM_W/2.0+1.2, 3.2, 0.60), 0.04, 1.20, P.METAL_BLACK)
    make_box("Speaker_Box", (ROOM_W/2.0+1.2, 3.2, 1.35), (0.34, 0.24, 0.44), (0.30, 0.30, 0.32, 1.0))
    make_box("Speaker_Grille", (ROOM_W/2.0+1.06, 3.2, 1.40), (0.02, 0.16, 0.20), (0.16, 0.16, 0.18, 1.0))
    make_box("Speaker_Broke_Sign", (ROOM_W/2.0+1.04, 3.2, 1.12), (0.015, 0.20, 0.14), (0.94, 0.92, 0.84, 1.0))
    make_box("Speaker_Sign_Tape", (ROOM_W/2.0+1.03, 3.2, 1.20), (0.012, 0.10, 0.02), (0.75, 0.72, 0.60, 1.0))
    # Asphalt lane strip under the window.
    make_box("DriveThru_Lane", (ROOM_W/2.0+1.5, 4.2, -0.02), (2.6, 5.5, 0.04), (0.30, 0.30, 0.32, 1.0))

def build_neon_sign():
    sx = ROOM_W/2.0-0.06; sy = ROOM_D/2.0; sz = 2.0
    pink=(0.96,0.24,0.62,1.0); cyan=(0.30,0.82,0.92,1.0); amber=(1.0,0.72,0.28,1.0)
    make_box("Neon_Board", (sx+0.03, sy, sz), (0.03, 1.80, 0.92), (0.10,0.08,0.10,1.0))
    make_cyl("Neon_Top", (sx, sy, sz+0.38), 0.02, 1.70, pink, axis='Y')
    make_cyl("Neon_Bot", (sx, sy, sz-0.38), 0.02, 1.70, pink, axis='Y')
    make_cyl("Neon_L", (sx, sy-0.85, sz), 0.02, 0.76, pink, axis='Z')
    make_cyl("Neon_R", (sx, sy+0.85, sz), 0.02, 0.76, pink, axis='Z')
    for i in range(5):
        make_cyl(f"Neon_TxtA_{i}", (sx, sy-0.60+i*0.30, sz+0.12), 0.015, 0.22, cyan, axis='Z')
    for i in range(6):
        make_cyl(f"Neon_TxtB_{i}", (sx, sy-0.70+i*0.28, sz-0.14), 0.015, 0.18, amber, axis='Z')

def build_string_lights():
    for strand in range(2):
        sy = ROOM_D*(0.32+strand*0.34)
        make_box(f"Festoon_Wire_{strand}", (0.0, sy, CEIL-0.12), (ROOM_W-0.6, 0.01, 0.01), P.METAL_BLACK)
        span = ROOM_W-0.8
        for b in range(9):
            bx = -span/2.0 + b*(span/8.0)
            make_cyl(f"Festoon_Bulb_{strand}_{b}", (bx, sy, CEIL-0.20), 0.035, 0.08, (1.0,0.82,0.5,1.0))

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def main():
    clear_scene()
    build_shell()
    build_register_counter()
    build_menu_board()
    build_salsa_station()
    build_tables()
    build_drive_thru_2026_08()
    build_neon_sign()
    build_string_lights()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/el_rancho_taqueria.glb"))
    print(f"\n[build_el_rancho_taqueria] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
