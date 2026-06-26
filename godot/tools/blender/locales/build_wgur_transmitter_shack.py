"""XVI · TOWER — WGUR Broadcast Tower Transmitter Shack. Single-
storey concrete shack at the base of the 90m guyed radio tower.
Inside: vintage transmitter rack with VU meters glowing, patch
panel + jumpered cables, single operator desk with a Bakelite
mic + log binder, fluorescent above. Through the small N window:
the tower's red obstruction lights pulse against night sky. The
Tower card's beat — the carrier-wave structure that can't
go down.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
import math
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_calendar, make_faded_poster
from _props.safety import (make_smoke_detector, make_sprinkler,
                            make_fluorescent_tube_fixture)

PAL = {"wall": (0.62, 0.62, 0.58, 1.0), "baseboard": (0.32, 0.32, 0.30, 1.0)}
COL_FLOOR_VINYL = (0.42, 0.42, 0.40, 1.0); COL_SEAM = (0.22, 0.22, 0.22, 1.0)
COL_RACK_GREY = (0.42, 0.44, 0.46, 1.0); COL_RACK_PANEL = (0.32, 0.34, 0.36, 1.0)
COL_DIAL_RED = (0.96, 0.32, 0.20, 1.0); COL_DIAL_GREEN = (0.32, 0.86, 0.42, 1.0)
COL_BAKELITE = (0.22, 0.16, 0.14, 1.0); COL_DESK_WOOD = (0.42, 0.30, 0.22, 1.0)
COL_PATCH_BG = (0.18, 0.18, 0.18, 1.0); COL_CABLE_R = (0.96, 0.32, 0.20, 1.0)
COL_CABLE_Y = (0.96, 0.86, 0.20, 1.0); COL_CABLE_B = (0.20, 0.42, 0.74, 1.0)
COL_OBSTR_RED = (0.96, 0.18, 0.18, 1.0); COL_GUY_WIRE = (0.32, 0.32, 0.32, 1.0)
COL_NIGHT_SKY = (0.06, 0.08, 0.16, 1.0); COL_VU_GLASS = (0.96, 0.86, 0.42, 1.0)

ROOM_W = 5.5; ROOM_D = 4.0; CEIL = 2.80


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR_VINYL, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL, baseboard_face_sign=bb)
    # N wall: small high window for the tower view
    make_wall("Wall_N_W", (-1.40, ROOM_D, 0), length=2.40, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (+1.40, ROOM_D, 0), length=2.40, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-1.80, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL)
    make_wall("Wall_S_E", (+1.80, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),
                                    ("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),
                                    ("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_RACK_PANEL})


def build_n_window_and_tower_view():
    # Small high window N
    make_box("WindowN_Frame", (0.0, ROOM_D-0.04, 2.20), (1.20, 0.04, 0.50), COL_RACK_PANEL)
    make_box("WindowN_Glass", (0.0, ROOM_D-0.06, 2.20), (1.00, 0.005, 0.40),
             (0.78, 0.84, 0.86, 0.55))
    # Night sky backdrop beyond
    make_box("Sky", (0.0, ROOM_D + 12.0, 6.0), (40.0, 0.04, 14.0), COL_NIGHT_SKY)
    # 90m tower — central core + three guy wires
    tower_x, tower_y = +2.0, ROOM_D + 10.0
    # Lattice approximation: 4 vertical legs + horizontal braces every 3m
    for sgn_x in (-1, +1):
        for sgn_y in (-1, +1):
            make_box(f"TowerLeg_{sgn_x:+d}_{sgn_y:+d}",
                     (tower_x + sgn_x*0.40, tower_y + sgn_y*0.40, 4.5),
                     (0.08, 0.08, 9.0), COL_RACK_GREY)
    # Horizontal braces
    for li in range(6):
        bz = 1.0 + li * 1.50
        make_box(f"TowerBrace_S_{li}", (tower_x, tower_y - 0.40, bz),
                 (0.88, 0.04, 0.04), COL_RACK_GREY)
        make_box(f"TowerBrace_N_{li}", (tower_x, tower_y + 0.40, bz),
                 (0.88, 0.04, 0.04), COL_RACK_GREY)
        make_box(f"TowerBrace_W_{li}", (tower_x - 0.40, tower_y, bz),
                 (0.04, 0.88, 0.04), COL_RACK_GREY)
        make_box(f"TowerBrace_E_{li}", (tower_x + 0.40, tower_y, bz),
                 (0.04, 0.88, 0.04), COL_RACK_GREY)
    # Obstruction lights (red dots) at three heights
    for li, lz in enumerate([3.0, 6.0, 9.0]):
        make_cyl(f"Obstr_{li}", (tower_x, tower_y, lz), 0.16, 0.10, COL_OBSTR_RED, segments=10)
    # Three guy wires anchoring out
    for gi, ang_deg in enumerate([0, 120, 240]):
        ang = math.radians(ang_deg)
        ex = tower_x + math.cos(ang) * 5.5
        ey = tower_y + math.sin(ang) * 5.5
        # midpoint
        mx, my, mz = (tower_x+ex)/2.0, (tower_y+ey)/2.0, 4.5
        make_box(f"Guy_{gi}", (mx, my, mz), (0.04, 0.04, 9.0), COL_GUY_WIRE)
    # Transmitter shack visible from outside (other side of the wall)


def build_transmitter_rack():
    # Three-bay 19" rack against the W wall
    for bi in range(3):
        rx = -ROOM_W/2.0 + 0.55
        ry = 1.20 + bi * 0.80
        make_box(f"Rack_{bi}_Body", (rx, ry, 1.00), (0.50, 0.60, 2.00), COL_RACK_GREY)
        make_box(f"Rack_{bi}_Front", (rx + 0.24, ry, 1.00), (0.005, 0.50, 1.80), COL_RACK_PANEL)
        # VU meters + dials per bay (4 stacked panels)
        for pi in range(4):
            pz = 0.30 + pi * 0.46
            make_box(f"Rack_{bi}_Panel_{pi}", (rx + 0.245, ry, pz),
                     (0.005, 0.50, 0.40), COL_RACK_PANEL)
            # VU window
            make_box(f"VU_{bi}_{pi}", (rx + 0.247, ry, pz + 0.06),
                     (0.005, 0.30, 0.16), COL_VU_GLASS)
            # Two indicator LEDs
            make_cyl(f"LED_{bi}_{pi}_R", (rx + 0.247, ry-0.18, pz-0.10),
                     0.014, 0.005, COL_DIAL_RED, axis='X')
            make_cyl(f"LED_{bi}_{pi}_G", (rx + 0.247, ry+0.18, pz-0.10),
                     0.014, 0.005, COL_DIAL_GREEN, axis='X')


def build_patch_panel_and_cables():
    # Patch panel on the E wall above the desk
    px, py = +ROOM_W/2.0 - 0.06, 2.20
    make_box("Patch_Panel", (px, py, 1.80), (0.06, 1.40, 0.60), COL_PATCH_BG)
    # 4x12 grid of jacks
    for col in range(4):
        for row in range(12):
            jx = px - 0.04
            jy = py - 0.60 + row * 0.10
            jz = 1.60 + col * 0.10
            make_cyl(f"Jack_{col}_{row}", (jx, jy, jz), 0.014, 0.02,
                     (0.62, 0.62, 0.58, 1.0), axis='X', segments=6)
    # 8 patch cables snaking around
    cables = [(COL_CABLE_R, 0.05), (COL_CABLE_Y, 0.10), (COL_CABLE_B, 0.04)]
    for ci, (cc, droop) in enumerate(cables * 3):
        cy_top = py - 0.40 + ci * 0.10
        # arc cable down
        for seg in range(4):
            sz = 1.70 - seg * (0.30 - droop)
            sy = cy_top + seg * 0.10
            make_box(f"Cable_{ci}_{seg}", (px - 0.04, sy, sz),
                     (0.02, 0.04, 0.04), cc)


def build_operator_desk_and_mic():
    # Operator desk centered S of the rack
    dx, dy = -0.40, 1.40
    make_box("Desk_Top",  (dx, dy, 0.74), (1.40, 0.80, 0.04), COL_DESK_WOOD)
    make_box("Desk_Drawer", (dx, dy, 0.52), (1.40, 0.78, 0.20), COL_DESK_WOOD)
    for sgn in (-1, +1):
        make_box(f"Desk_Leg_{sgn:+d}", (dx + sgn*0.62, dy, 0.36),
                 (0.06, 0.78, 0.72), COL_DESK_WOOD)
    # Bakelite microphone on stand
    make_box("Mic_Base", (dx-0.30, dy, 0.78), (0.18, 0.18, 0.04), COL_BAKELITE)
    make_cyl("Mic_Stem", (dx-0.30, dy, 0.92), 0.014, 0.20, COL_BAKELITE)
    make_box("Mic_Head", (dx-0.30, dy, 1.10), (0.08, 0.10, 0.16), COL_BAKELITE)
    # Log binder + pen
    make_box("Log_Binder", (dx+0.20, dy, 0.78), (0.30, 0.40, 0.04), (0.62, 0.42, 0.20, 1.0))
    make_box("Pen", (dx+0.20, dy+0.18, 0.78), (0.12, 0.012, 0.012), COL_BAKELITE)
    # Headphones hanging on the desk edge
    make_cyl("Phones_Band", (dx+0.50, dy-0.40, 0.84), 0.10, 0.04, COL_BAKELITE, axis='X', segments=10)
    for sgn in (-1, +1):
        make_cyl(f"Phones_Cup_{sgn:+d}", (dx + 0.50 + sgn*0.08, dy - 0.40, 0.74),
                 0.06, 0.04, COL_BAKELITE, axis='X', segments=8)
    # Single chair S of desk
    cx, cy = dx, dy - 0.80
    make_box("Chair_Seat", (cx, cy, 0.46), (0.50, 0.50, 0.06), (0.42, 0.30, 0.22, 1.0))
    make_box("Chair_Back", (cx, cy-0.22, 0.86), (0.50, 0.06, 0.74), (0.42, 0.30, 0.22, 1.0))
    for li, (sgn_x, sgn_y) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_box(f"Chair_Leg_{li}", (cx + sgn_x*0.22, cy + sgn_y*0.22, 0.23),
                 (0.04, 0.04, 0.46), (0.32, 0.22, 0.16, 1.0))


def build_ceiling_infra():
    make_fluorescent_tube_fixture("Fluor", (0.0, 2.0, CEIL),
                                   length=1.40, width=0.32,
                                   palette={"diffuser": (1.0, 0.98, 0.92, 1.0)})
    make_smoke_detector("Smoke", (0.0, 2.0, CEIL))
    make_sprinkler("Spr", (0.0, 1.0, CEIL))


def build_decor():
    make_wall_clock("Clock", (+ROOM_W/2.0-0.05, 1.0, 2.30), frozen_hour=4, frozen_min=15)
    make_calendar("Calendar", (-ROOM_W/2.0+0.05, 3.5, 2.20))
    make_faded_poster("FCC_Poster", (+ROOM_W/2.0-0.05, 3.5, 1.50))


def build_tower_dressing():
    """Scene-description specifics from setup_carrier_wave_unbroken.json:
      · Evangeline's operator chair · empty + a slight worn-patch on
        the seat (she's been on it since 11 PM yesterday)
      · Terminal showing the render queue at 847 · CRT monitor
        with phosphor-green digits
      · Kill switch · big red bakelite button on the patch panel
        with a small placard above reading PULL TO KILL
      · Pulse-light reflections on the floor in front of the
        north window (the tower obstruction lights pulsing red)
      · Radio speaker on the desk · the canonical Evangeline-Feb
        broadcast playing in low quiet (visible as a small reel
        cassette in the desk's tape player)
    """
    desk_cx = 0.0
    desk_cy = -1.20
    desk_top_z = 0.78

    # Operator chair (empty · she's stepped to the window) — wear
    # on the seat shows it's been the watch chair tonight
    chair_x = desk_cx + 0.10
    chair_y = desk_cy - 0.80
    make_box("EvangelineChair_Seat",
             (chair_x, chair_y, 0.46),
             (0.50, 0.50, 0.08),
             (0.32, 0.22, 0.14, 1.0))
    # Worn patch
    make_box("EvangelineChair_WearPatch",
             (chair_x, chair_y, 0.51),
             (0.34, 0.34, 0.003),
             (0.22, 0.14, 0.08, 1.0))
    make_box("EvangelineChair_Back",
             (chair_x, chair_y + 0.22, 0.86),
             (0.50, 0.06, 0.60),
             (0.32, 0.22, 0.14, 1.0))
    # 5-star wheel base
    make_cyl("EvangelineChair_Post",
             (chair_x, chair_y, 0.22),
             0.025, 0.40,
             (0.22, 0.20, 0.18, 1.0),
             segments=6, axis='Z')

    # Terminal showing render queue at 847
    term_x = desk_cx
    term_y = desk_cy + 0.06
    # Beige CRT case
    make_box("WGUR_Terminal_Case",
             (term_x, term_y, desk_top_z + 0.18),
             (0.42, 0.40, 0.40),
             (0.86, 0.82, 0.74, 1.0))
    # Dark screen
    make_box("WGUR_Terminal_Screen",
             (term_x, term_y - 0.20, desk_top_z + 0.22),
             (0.32, 0.02, 0.26),
             (0.10, 0.10, 0.12, 1.0))
    # Phosphor-green "847" digits on the screen (three small bright boxes)
    for di, dx_off in enumerate([-0.05, 0.0, +0.05]):
        make_box("WGUR_Terminal_Digit_%d" % di,
                 (term_x + dx_off, term_y - 0.201, desk_top_z + 0.24),
                 (0.022, 0.001, 0.040),
                 (0.18, 0.96, 0.40, 1.0))
    # "RENDER QUEUE" label above the digits
    make_box("WGUR_Terminal_QueueLabel",
             (term_x, term_y - 0.201, desk_top_z + 0.30),
             (0.18, 0.001, 0.012),
             (0.18, 0.96, 0.40, 1.0))

    # Kill switch — big red bakelite button on the patch panel
    # Patch panel approx at the east wall, near (+1.8, +0.5)
    ks_x = +1.8
    ks_y = +0.5
    # Mounting plate (gray metal)
    make_box("KillSwitch_Plate",
             (ks_x, ks_y - 0.045, 1.40),
             (0.20, 0.04, 0.20),
             (0.62, 0.62, 0.62, 1.0))
    # The big red button (low-poly cylinder facing patron)
    make_cyl("KillSwitch_Button",
             (ks_x, ks_y - 0.090, 1.40),
             0.060, 0.04,
             (0.86, 0.18, 0.16, 1.0),
             segments=10, axis='Y')
    # Brass placard above the button
    make_box("KillSwitch_Placard",
             (ks_x, ks_y - 0.046, 1.54),
             (0.16, 0.001, 0.04),
             (0.78, 0.62, 0.30, 1.0))
    # Placard letters (dark)
    make_box("KillSwitch_Placard_Text",
             (ks_x, ks_y - 0.0465, 1.54),
             (0.12, 0.0005, 0.022),
             (0.20, 0.16, 0.10, 1.0))

    # Pulse-light reflections on the floor in front of the N window
    # (N window is at y = +3.0 approx; floor below it)
    for pi in range(3):
        px = -0.60 + pi * 0.60
        make_box("PulseLight_FloorReflect_%d" % pi,
                 (px, +2.50, 0.005),
                 (0.50, 0.30, 0.001),
                 (0.86, 0.18, 0.18, 0.5))

    # Radio speaker on the desk — playing the Evangeline-Feb broadcast
    spk_x = desk_cx + 0.60
    spk_y = desk_cy + 0.06
    # Speaker box (small cube)
    make_box("WGUR_RadioSpeaker_Body",
             (spk_x, spk_y, desk_top_z + 0.10),
             (0.20, 0.18, 0.20),
             (0.42, 0.32, 0.20, 1.0))
    # Speaker grille (dark mesh)
    make_box("WGUR_RadioSpeaker_Grille",
             (spk_x, spk_y - 0.091, desk_top_z + 0.10),
             (0.16, 0.005, 0.16),
             (0.10, 0.08, 0.06, 1.0))
    # Tape cassette in the slot (the Feb broadcast)
    make_box("WGUR_TapeCassette",
             (spk_x, spk_y + 0.10, desk_top_z + 0.04),
             (0.16, 0.04, 0.08),
             (0.18, 0.16, 0.14, 1.0))
    # Cassette label
    make_box("WGUR_TapeCassette_Label",
             (spk_x, spk_y + 0.10, desk_top_z + 0.082),
             (0.14, 0.04, 0.001),
             (0.94, 0.90, 0.80, 1.0))
    # Handwritten "FEB" on the label
    make_box("WGUR_TapeCassette_LabelText",
             (spk_x, spk_y + 0.10, desk_top_z + 0.083),
             (0.05, 0.020, 0.0005),
             (0.18, 0.16, 0.10, 1.0))


def main():
    clear_scene()
    build_shell()
    build_n_window_and_tower_view()
    build_transmitter_rack()
    build_patch_panel_and_cables()
    build_operator_desk_and_mic()
    build_ceiling_infra()
    build_decor()
    build_tower_dressing()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/wgur_transmitter_shack.glb"))
    print(f"\n[build_wgur_transmitter_shack] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
