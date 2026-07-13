"""caldwell_radio_room_night — Caldwell's late-night radio room. A
small station booth: a broadcast console with a mixing board (channel
strips + VU meters), an on-air mic on a boom arm, a monitor + second
CRT, an equipment rack on the W wall (reel-to-reel deck + cart
machines + EQ with glowing readouts), an ON AIR sign over the door,
coffee going cold on the desk. Night mood — a single bare bulb + the
warm glow of the gear. Rebuilt from the bare auto-generated template
(which imported store/shelving/food helpers it never used and shipped
only a desk-top + monitor box + two filing boxes).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import (make_floor, make_wall, make_ceiling,
                              make_crown_molding, make_window)
from _props.food_service import make_coffee_pots
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture

ROOM_W = 4.5; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall": (0.78, 0.70, 0.58, 1.0), "baseboard": (0.42, 0.32, 0.22, 1.0)}
COL_FLOOR = (0.62, 0.52, 0.42, 1.0); COL_SEAM = (0.32, 0.22, 0.14, 1.0)
COL_WOOD = (0.42, 0.30, 0.20, 1.0); COL_WOOD_DK = (0.30, 0.20, 0.13, 1.0)
COL_CONSOLE = (0.20, 0.20, 0.22, 1.0); COL_PANEL = (0.14, 0.14, 0.16, 1.0)
COL_METAL = (0.46, 0.46, 0.48, 1.0); COL_METAL_DK = (0.28, 0.28, 0.30, 1.0)
COL_VU_AMBER = (0.96, 0.78, 0.34, 1.0); COL_LED_GREEN = (0.34, 0.92, 0.44, 1.0)
COL_LED_RED = (0.96, 0.28, 0.22, 1.0); COL_KNOB = (0.62, 0.60, 0.58, 1.0)
COL_FADER = (0.72, 0.70, 0.68, 1.0); COL_SCREEN = (0.10, 0.14, 0.12, 1.0)
COL_PHOSPHOR = (0.30, 0.90, 0.52, 1.0); COL_ONAIR = (0.96, 0.20, 0.16, 1.0)
COL_BAKELITE = (0.16, 0.14, 0.13, 1.0)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL,
              axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL,
              axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
                                    ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
                                    ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_WOOD_DK})


def build_console_desk():
    """Broadcast desk + mixing board against the N wall."""
    dx, dy = 0.0, ROOM_D - 1.10
    top_z = 0.74
    # Desk top + modesty panel + side legs
    make_box("Desk_Top", (dx, dy, top_z), (2.20, 0.80, 0.05), COL_WOOD)
    make_box("Desk_Modesty", (dx, dy+0.36, 0.38), (2.20, 0.04, 0.72), COL_WOOD_DK)
    for sgn in (-1, +1):
        make_box(f"Desk_Leg_{sgn:+d}", (dx + sgn*1.02, dy, 0.36), (0.08, 0.76, 0.72), COL_WOOD_DK)

    # ── Mixing board (angled console) sitting on the desk ──
    bx, by = 0.0, dy - 0.06
    make_box("Board_Body", (bx, by, top_z + 0.06), (1.60, 0.56, 0.10), COL_CONSOLE)
    make_box("Board_Face", (bx, by - 0.02, top_z + 0.13), (1.56, 0.50, 0.02), COL_PANEL)
    # 8 channel strips: a fader slot + fader cap + two knobs + a channel LED
    for ci in range(8):
        cx = bx - 0.68 + ci * 0.195
        # fader travel slot
        make_box(f"Board_FaderSlot_{ci}", (cx, by + 0.12, top_z + 0.14),
                 (0.02, 0.18, 0.004), COL_METAL_DK)
        # fader cap
        make_box(f"Board_FaderCap_{ci}", (cx, by + 0.08 + (ci % 3) * 0.03, top_z + 0.15),
                 (0.05, 0.05, 0.02), COL_FADER)
        # two rotary knobs above the fader
        for ki, ky in enumerate([by - 0.10, by - 0.02]):
            make_cyl(f"Board_Knob_{ci}_{ki}", (cx, ky, top_z + 0.15),
                     0.022, 0.03, COL_KNOB, axis='Z', segments=8)
        # channel-on LED (alternating green/red)
        lc = COL_LED_GREEN if ci % 2 == 0 else COL_LED_RED
        make_cyl(f"Board_LED_{ci}", (cx, by - 0.18, top_z + 0.15),
                 0.010, 0.008, lc, axis='Z', segments=6)
    # Two VU meters flanking the strips (glowing amber windows)
    for sgn in (-1, +1):
        make_box(f"Board_VU_Housing_{sgn:+d}", (bx + sgn*0.70, by - 0.06, top_z + 0.15),
                 (0.20, 0.20, 0.03), COL_PANEL)
        make_box(f"Board_VU_Glass_{sgn:+d}", (bx + sgn*0.70, by - 0.16, top_z + 0.17),
                 (0.16, 0.005, 0.10), COL_VU_AMBER)

    # ── Monitor (CRT) + keyboard on the desk, W side ──
    mx, my = -0.80, dy + 0.18
    make_box("Monitor_Case", (mx, my, top_z + 0.22), (0.42, 0.40, 0.38), (0.86, 0.82, 0.74, 1.0))
    make_box("Monitor_Screen", (mx, my - 0.20, top_z + 0.24), (0.32, 0.02, 0.26), COL_SCREEN)
    for di, dxo in enumerate([-0.06, 0.0, +0.06]):
        make_box(f"Monitor_Phosphor_{di}", (mx + dxo, my - 0.201, top_z + 0.26),
                 (0.02, 0.001, 0.05), COL_PHOSPHOR)
    make_box("Keyboard", (mx, my - 0.34, top_z + 0.03), (0.36, 0.14, 0.03), (0.20, 0.20, 0.22, 1.0))
    # Small second monitor (log/queue), E side
    make_box("Monitor2_Case", (0.80, dy + 0.20, top_z + 0.18), (0.34, 0.32, 0.30), (0.20, 0.20, 0.22, 1.0))
    make_box("Monitor2_Screen", (0.80, dy + 0.03, top_z + 0.20), (0.26, 0.02, 0.22), COL_SCREEN)
    make_box("Monitor2_Line", (0.80, dy + 0.02, top_z + 0.22), (0.20, 0.001, 0.02), COL_PHOSPHOR)


def build_mic_and_boom():
    """On-air mic on a boom arm clamped to the desk, with pop filter."""
    dx, dy = 0.0, ROOM_D - 1.10
    top_z = 0.78
    clamp_x, clamp_y = -0.40, dy - 0.40
    # Clamp base at desk edge
    make_box("MicBoom_Clamp", (clamp_x, clamp_y, top_z), (0.08, 0.10, 0.10), COL_METAL_DK)
    # Vertical post
    make_cyl("MicBoom_Post", (clamp_x, clamp_y, top_z + 0.30), 0.014, 0.56, COL_METAL_DK, axis='Z')
    # Horizontal arm reaching toward the operator
    make_cyl("MicBoom_Arm", (clamp_x + 0.22, clamp_y - 0.18, top_z + 0.56),
             0.012, 0.60, COL_METAL_DK, axis='X')
    make_cyl("MicBoom_Arm2", (clamp_x + 0.30, clamp_y - 0.36, top_z + 0.48),
             0.012, 0.44, COL_METAL_DK, axis='Y')
    # Mic capsule hanging from the arm
    mic_x, mic_y, mic_z = clamp_x + 0.30, clamp_y - 0.56, top_z + 0.34
    make_cyl("Mic_Body", (mic_x, mic_y, mic_z), 0.035, 0.16, COL_BAKELITE, axis='Z', segments=10)
    make_cyl("Mic_Grille", (mic_x, mic_y, mic_z + 0.10), 0.040, 0.06, COL_METAL, axis='Z', segments=10)
    # Pop filter (thin disc in front of the mic, facing operator)
    make_cyl("Mic_PopFilter", (mic_x, mic_y - 0.09, mic_z + 0.06), 0.07, 0.006,
             (0.10, 0.10, 0.12, 0.6), axis='Y', segments=12)
    # Headphones hooked on the desk edge
    hx, hy = 0.85, dy - 0.42
    make_cyl("Phones_Band", (hx, hy, top_z + 0.06), 0.10, 0.03, COL_BAKELITE, axis='X', segments=12)
    for sgn in (-1, +1):
        make_cyl(f"Phones_Cup_{sgn:+d}", (hx + sgn*0.09, hy, top_z - 0.04),
                 0.06, 0.045, COL_BAKELITE, axis='X', segments=10)


def build_equipment_rack():
    """Equipment rack on the W wall: reel-to-reel + cart decks + EQ."""
    rx = -ROOM_W/2.0 + 0.35
    ry = 1.30
    # Rack frame
    make_box("Rack_Body", (rx, ry, 1.05), (0.55, 0.70, 2.05), COL_METAL_DK)
    make_box("Rack_Face", (rx + 0.27, ry, 1.05), (0.02, 0.62, 1.95), COL_PANEL)

    # Reel-to-reel deck (top bay) — panel + two reels + heads
    rr_z = 1.72
    make_box("Reel_Panel", (rx + 0.28, ry, rr_z), (0.02, 0.60, 0.46), (0.24, 0.24, 0.26, 1.0))
    for sgn, rlbl in ((-1, "L"), (+1, "R")):
        make_cyl(f"Reel_{rlbl}", (rx + 0.30, ry + sgn*0.16, rr_z + 0.04),
                 0.13, 0.03, (0.42, 0.42, 0.44, 1.0), axis='X', segments=14)
        make_cyl(f"Reel_{rlbl}_Hub", (rx + 0.31, ry + sgn*0.16, rr_z + 0.04),
                 0.04, 0.035, COL_METAL_DK, axis='X', segments=8)
    # Tape path heads (three small blocks between the reels)
    for hi, hy in enumerate([-0.04, 0.0, +0.04]):
        make_box(f"Reel_Head_{hi}", (rx + 0.31, ry + hy, rr_z - 0.14),
                 (0.02, 0.02, 0.05), COL_METAL)

    # Cart machines (mid bay) — three stacked with slots + status LEDs
    for ci in range(3):
        cz = 1.28 - ci * 0.20
        make_box(f"Cart_{ci}", (rx + 0.28, ry, cz), (0.02, 0.58, 0.16), (0.18, 0.18, 0.20, 1.0))
        make_box(f"Cart_{ci}_Slot", (rx + 0.29, ry - 0.06, cz + 0.02), (0.01, 0.34, 0.05), COL_METAL_DK)
        make_cyl(f"Cart_{ci}_LED", (rx + 0.29, ry + 0.22, cz + 0.02),
                 0.010, 0.006, COL_LED_RED if ci == 0 else COL_LED_GREEN, axis='X', segments=6)

    # EQ / processor (bottom bay) — a row of small faders + an amber readout
    eq_z = 0.66
    make_box("EQ_Panel", (rx + 0.28, ry, eq_z), (0.02, 0.58, 0.18), (0.16, 0.16, 0.18, 1.0))
    for fi in range(7):
        fy = ry - 0.22 + fi * 0.075
        make_box(f"EQ_Fader_{fi}", (rx + 0.29, fy, eq_z + (fi % 3)*0.02 - 0.02),
                 (0.01, 0.02, 0.05), COL_FADER)
    make_box("EQ_Readout", (rx + 0.29, ry + 0.20, eq_z + 0.05), (0.01, 0.10, 0.05), COL_VU_AMBER)


def build_on_air_sign():
    """ON AIR sign over the S door (lit red)."""
    sx, sy, sz = 0.0, 0.12, 2.18
    make_box("OnAir_Backing", (sx, sy, sz), (0.90, 0.06, 0.30), (0.10, 0.10, 0.12, 1.0))
    make_box("OnAir_Face", (sx, sy - 0.032, sz), (0.80, 0.005, 0.22), (0.16, 0.06, 0.06, 1.0))
    # "ON" + "AIR" letter blocks (emissive red)
    make_box("OnAir_ON", (sx - 0.20, sy - 0.035, sz), (0.26, 0.001, 0.12), COL_ONAIR)
    make_box("OnAir_AIR", (sx + 0.22, sy - 0.035, sz), (0.30, 0.001, 0.12), COL_ONAIR)


def build_coffee_and_clutter():
    dx, dy = 0.0, ROOM_D - 1.10
    top_z = 0.76
    # Coffee mug on the desk (going cold), E side near the operator
    mug_x, mug_y = 0.55, dy - 0.30
    make_cyl("Mug_Body", (mug_x, mug_y, top_z + 0.05), 0.045, 0.10, (0.72, 0.30, 0.22, 1.0),
             axis='Z', segments=12)
    make_cyl("Mug_Coffee", (mug_x, mug_y, top_z + 0.095), 0.038, 0.006, (0.20, 0.12, 0.08, 1.0),
             axis='Z', segments=12)
    make_cyl("Mug_Handle", (mug_x + 0.055, mug_y, top_z + 0.05), 0.022, 0.012, (0.72, 0.30, 0.22, 1.0),
             axis='X', segments=8)
    # Coffee maker on a small side table, SE corner (make_coffee_pots was unused)
    st_x, st_y = ROOM_W/2.0 - 0.45, 0.95
    make_box("SideTable_Top", (st_x, st_y, 0.72), (0.60, 0.72, 0.04), COL_WOOD)
    for (lx, ly) in [(-0.25, -0.30), (0.25, -0.30), (-0.25, 0.30), (0.25, 0.30)]:
        make_box(f"SideTable_Leg_{int(lx*100)}_{int(ly*100)}",
                 (st_x + lx, st_y + ly, 0.36), (0.04, 0.04, 0.72), COL_WOOD_DK)
    # pots span 0.5m in y; anchor +0.25 so the pair centers on the table
    make_coffee_pots("CoffeeMaker", (st_x, st_y + 0.25, 0.74), pots=2)
    # Desk lamp (gooseneck) at the console corner
    lp_x, lp_y = -1.00, dy + 0.10
    make_box("Lamp_Base", (lp_x, lp_y, top_z + 0.02), (0.14, 0.14, 0.03), COL_METAL_DK)
    make_cyl("Lamp_Column", (lp_x, lp_y, top_z + 0.20), 0.012, 0.34, COL_METAL_DK, axis='Z')
    make_cyl("Lamp_Arm", (lp_x + 0.10, lp_y - 0.06, top_z + 0.36), 0.010, 0.24, COL_METAL_DK, axis='X')
    make_cyl("Lamp_Head", (lp_x + 0.20, lp_y - 0.06, top_z + 0.34), 0.06, 0.08,
             (0.96, 0.86, 0.52, 1.0), axis='Z', segments=10)


def build_bulb():
    make_cyl("Bulb_Cord", (0.0, ROOM_D/2.0, CEIL-0.30), 0.005, 0.60, P.METAL_BLACK)
    make_cyl("Bulb_Glass", (0.0, ROOM_D/2.0, CEIL-0.86), 0.06, 0.14, (0.96, 0.86, 0.46, 1.0))


def build_window():
    # Small window on the S wall east of the door (night — dark warm glass)
    make_window("WindowS", (+1.55, 0.06, 1.55), width=1.00, height=0.90,
                palette={"glass": (0.10, 0.12, 0.18, 0.7),
                         "warm": (0.24, 0.20, 0.16, 0.5),
                         "frame": COL_WOOD_DK})


def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))
    make_hvac_vent("HVAC", (ROOM_W/2.0 - 0.7, ROOM_D - 0.6, CEIL))


def build_decor():
    make_wall_clock("Clock", (+ROOM_W/2.0-0.05, 3.6, 1.90), frozen_hour=2, frozen_min=14)
    make_calendar("Calendar", (-ROOM_W/2.0+0.05, 3.6, 1.85))
    make_faded_poster("StationLicense", (+ROOM_W/2.0-0.05, 2.2, 1.55))
    make_floor_plant("Plant", (-ROOM_W/2.0+0.45, ROOM_D-0.5, 0.0),
                     palette={"leaf": (0.34, 0.44, 0.30, 1.0)})


def main():
    clear_scene()
    build_shell()
    build_console_desk()
    build_mic_and_boom()
    build_equipment_rack()
    build_on_air_sign()
    build_coffee_and_clutter()
    build_bulb()
    build_window()
    build_ceiling_infra()
    build_decor()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/caldwell_radio_room_night.glb"))
    print(f"\n[build_caldwell_radio_room_night] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
