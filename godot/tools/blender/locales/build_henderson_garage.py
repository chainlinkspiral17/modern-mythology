"""Henderson garage — vol6 placement script.

Jesse Henderson's garage, home of Suburban Blight (band name on the
flyer: SUBSTATION NINE bill at the Foxhole). The door is UP — August
in Harmony Creek, the temperature threshold rule — so the establishing
shot looks IN from the driveway at dusk: lit interior framed by the
open door, drum kit and amps center, pegboard and paint shelf behind.
Canon beats staged here: ch5 Garage Band Catharsis (swept floor —
keep the floor CLEAN, one faint oil stain only), ch14 the flyer kid
at the foot of the driveway, ch20 bridge practice with Carl / Nate /
Em.

Hero props: the drum kit (kick, snare, rack tom, floor tom, hi-hat,
crash), two guitar amps + a bass amp, the Telecaster on a stand, the
mic stand front-center, cable runs. Support: workbench + pegboard on
the north wall, paint-can shelf, box fan, mini fridge, milk crates,
the rolled-up door panel overhead, the driveway pad outside with a
basketball hoop backboard on the eave.

Coordinate frame: Blender Z-up. y=0 is the OPEN garage-door plane
(south, to the driveway); +Y into the garage; walls at x=±ROOM_W/2.
glTF export remaps to Godot (x, z, -y).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling

# ── Single-bay garage footprint ──
ROOM_W = 5.6      # x ∈ [-2.8, 2.8]
ROOM_D = 5.8      # y ∈ [0, 5.8]  (open door at y=0)
CEIL = 2.7

COL_WALL = (0.62, 0.60, 0.55, 1.0)      # unpainted drywall grey-tan
COL_BASE = (0.40, 0.38, 0.34, 1.0)
COL_FLOOR = (0.44, 0.44, 0.46, 1.0)     # sealed concrete (swept)
COL_SEAM = (0.36, 0.36, 0.38, 1.0)
COL_STAIN = (0.30, 0.29, 0.30, 1.0)     # one faint old oil stain
COL_DOOR = (0.82, 0.81, 0.78, 1.0)      # white steel door panel
COL_TRACK = (0.30, 0.31, 0.34, 1.0)
COL_BENCH = (0.42, 0.30, 0.18, 1.0)     # plywood workbench
COL_BENCH_DK = (0.30, 0.21, 0.13, 1.0)
COL_PEG = (0.55, 0.42, 0.26, 1.0)       # pegboard tan
COL_STEEL = (0.34, 0.35, 0.38, 1.0)
COL_STEEL_DK = (0.18, 0.18, 0.20, 1.0)
COL_AMP = (0.10, 0.10, 0.11, 1.0)       # tolex black
COL_GRILLE = (0.52, 0.46, 0.34, 1.0)    # wheat grille cloth
COL_KNOB = (0.78, 0.76, 0.70, 1.0)
COL_DRUM = (0.55, 0.14, 0.14, 1.0)      # wine-red wrap kit
COL_DRUM_DK = (0.38, 0.09, 0.09, 1.0)
COL_HEAD = (0.88, 0.87, 0.82, 1.0)      # coated drumhead
COL_CYMBAL = (0.76, 0.64, 0.30, 1.0)
COL_TELE = (0.72, 0.60, 0.34, 1.0)      # butterscotch Telecaster
COL_TELE_GUARD = (0.12, 0.12, 0.12, 1.0)
COL_BASS = (0.16, 0.20, 0.34, 1.0)      # navy bass
COL_CABLE = (0.08, 0.08, 0.09, 1.0)
COL_PAINT = (0.70, 0.68, 0.62, 1.0)     # paint-can steel
COL_FRIDGE = (0.80, 0.80, 0.78, 1.0)
COL_CRATE = (0.68, 0.30, 0.14, 1.0)     # orange milk crate
COL_DRIVE = (0.50, 0.49, 0.50, 1.0)     # driveway concrete (dusk)
COL_LAWN = (0.22, 0.30, 0.16, 1.0)
COL_BULB = (1.00, 0.88, 0.62, 1.0)      # bare bulb — blooms via glow
COL_FLYER = (0.90, 0.88, 0.80, 1.0)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # One faint oil stain — the floor is otherwise swept (ch5 canon).
    make_box("Floor_OilStain", (0.9, 4.2, 0.005), (0.7, 0.9, 0.004), COL_STAIN)
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
                  axis='Y', palette=pal, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=pal, baseboard_face_sign=-1)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, with_grid=False, with_stains=False)
    # South header above the door opening
    make_box("Door_Header", (0.0, 0.0, CEIL - 0.15), (ROOM_W + 0.4, 0.22, 0.30), COL_WALL)
    # Side jambs
    for sgn in (-1, 1):
        make_box(f"Door_Jamb_{sgn:+d}", (sgn * (ROOM_W / 2.0 - 0.10), 0.0, CEIL / 2.0),
                 (0.20, 0.22, CEIL), COL_WALL)
    # The door itself is UP: rolled panel sections lying under the
    # ceiling along the tracks, plus the curved track pair.
    for k in range(4):
        make_box(f"Door_Panel_{k}", (0.0, 0.55 + k * 0.42, CEIL - 0.10),
                 (ROOM_W - 0.7, 0.40, 0.05), COL_DOOR)
    for sgn in (-1, 1):
        make_box(f"Door_Track_{sgn:+d}", (sgn * (ROOM_W / 2.0 - 0.32), 1.2, CEIL - 0.16),
                 (0.05, 2.4, 0.05), COL_TRACK)
        make_box(f"Door_Track_V_{sgn:+d}", (sgn * (ROOM_W / 2.0 - 0.32), 0.10, CEIL - 0.75),
                 (0.05, 0.05, 1.3), COL_TRACK)
    # Opener rail + motor box on the ceiling centerline
    make_box("Opener_Rail", (0.0, 1.9, CEIL - 0.20), (0.06, 3.0, 0.06), COL_TRACK)
    make_box("Opener_Motor", (0.0, 3.4, CEIL - 0.28), (0.34, 0.44, 0.22), COL_STEEL_DK)


def build_driveway():
    """Outside the open door: the driveway pad, a strip of lawn each
    side, and the basketball backboard over the eave — enough world
    that the from-the-driveway establishing shot has a foreground."""
    make_box("Driveway", (0.0, -2.6, -0.02), (ROOM_W - 0.4, 5.2, 0.04), COL_DRIVE)
    # Expansion joints
    for k in range(3):
        make_box(f"Driveway_Joint_{k}", (0.0, -1.2 - k * 1.5, 0.001),
                 (ROOM_W - 0.4, 0.03, 0.006), COL_SEAM)
    for sgn in (-1, 1):
        make_box(f"Lawn_{sgn:+d}", (sgn * (ROOM_W / 2.0 + 0.9), -2.6, -0.03),
                 (2.2, 5.2, 0.03), COL_LAWN)
    # Basketball backboard + hoop on the eave over the door
    make_box("Hoop_Backboard", (0.6, -0.14, CEIL + 0.45), (1.0, 0.05, 0.7),
             (0.85, 0.85, 0.82, 1.0))
    make_box("Hoop_Square", (0.6, -0.16, CEIL + 0.35), (0.4, 0.02, 0.3),
             (0.70, 0.30, 0.16, 1.0))
    make_cyl("Hoop_Rim", (0.6, -0.38, CEIL + 0.22), 0.23, 0.03,
             (0.72, 0.28, 0.14, 1.0), segments=12)


def build_band_gear():
    """The hero cluster: kit at back-center facing the door, amps
    flanking, Telecaster on its stand, mic front-center."""
    # ── Drum kit (facing -Y / the door) ──
    kx, ky = -0.3, 4.3
    # Kick drum — cylinder lying on axis Y
    make_cyl("Kick", (kx, ky, 0.30), 0.30, 0.45, COL_DRUM, segments=14, axis='Y')
    make_cyl("Kick_HeadF", (kx, ky - 0.24, 0.30), 0.29, 0.02, COL_HEAD, segments=14, axis='Y')
    make_box("Kick_Pedal", (kx, ky - 0.42, 0.05), (0.12, 0.20, 0.10), COL_STEEL_DK)
    # Snare on a stand, left of kick (player's view)
    make_cyl("Snare", (kx - 0.48, ky - 0.28, 0.62), 0.18, 0.14, COL_DRUM_DK, segments=12)
    make_cyl("Snare_Head", (kx - 0.48, ky - 0.28, 0.695), 0.17, 0.01, COL_HEAD, segments=12)
    make_cyl("Snare_Stand", (kx - 0.48, ky - 0.28, 0.30), 0.02, 0.60, COL_STEEL, segments=6)
    # Rack tom on the kick
    make_cyl("Tom_Rack", (kx + 0.10, ky - 0.05, 0.78), 0.16, 0.18, COL_DRUM, segments=12)
    make_cyl("Tom_Rack_Head", (kx + 0.10, ky - 0.05, 0.875), 0.15, 0.01, COL_HEAD, segments=12)
    # Floor tom right
    make_cyl("Tom_Floor", (kx + 0.55, ky - 0.20, 0.48), 0.20, 0.30, COL_DRUM, segments=12)
    make_cyl("Tom_Floor_Head", (kx + 0.55, ky - 0.20, 0.635), 0.19, 0.01, COL_HEAD, segments=12)
    for li, lx in enumerate((-0.12, 0.0, 0.12)):
        make_cyl(f"Tom_Floor_Leg_{li}", (kx + 0.55 + lx, ky - 0.20 + (0.12 if li == 1 else -0.08),
                 0.17), 0.012, 0.34, COL_STEEL, segments=5)
    # Hi-hat (two thin discs) left
    make_cyl("HiHat_Stand", (kx - 0.85, ky - 0.30, 0.45), 0.015, 0.90, COL_STEEL, segments=6)
    make_cyl("HiHat_Top", (kx - 0.85, ky - 0.30, 0.92), 0.16, 0.008, COL_CYMBAL, segments=14)
    make_cyl("HiHat_Bot", (kx - 0.85, ky - 0.30, 0.90), 0.16, 0.008, COL_CYMBAL, segments=14)
    # Crash cymbal right, higher
    make_cyl("Crash_Stand", (kx + 0.85, ky + 0.05, 0.60), 0.015, 1.20, COL_STEEL, segments=6)
    make_cyl("Crash", (kx + 0.85, ky + 0.05, 1.22), 0.20, 0.008, COL_CYMBAL, segments=14)
    # Throne
    make_cyl("Throne_Seat", (kx, ky + 0.55, 0.50), 0.17, 0.08, COL_AMP, segments=10)
    make_cyl("Throne_Post", (kx, ky + 0.55, 0.25), 0.03, 0.50, COL_STEEL, segments=6)

    # ── Amps: two guitar combos W side, bass amp E side ──
    for ai, (ax, ay) in enumerate([(-2.05, 3.6), (-2.15, 2.6)]):
        make_box(f"Amp_{ai}", (ax, ay, 0.30), (0.62, 0.30, 0.55), COL_AMP)
        make_box(f"Amp_{ai}_Grille", (ax + 0.02, ay - 0.16, 0.26), (0.54, 0.02, 0.40), COL_GRILLE)
        make_box(f"Amp_{ai}_Panel", (ax + 0.02, ay - 0.16, 0.52), (0.54, 0.02, 0.07), COL_STEEL_DK)
        for k in range(4):
            make_cyl(f"Amp_{ai}_Knob_{k}", (ax - 0.18 + k * 0.12, ay - 0.18, 0.52),
                     0.018, 0.02, COL_KNOB, segments=6, axis='Y')
    # Bass rig: head on cab
    make_box("BassCab", (2.1, 3.7, 0.36), (0.60, 0.50, 0.70), COL_AMP)
    make_box("BassCab_Grille", (2.1, 3.44, 0.34), (0.52, 0.02, 0.58), COL_GRILLE)
    make_box("BassHead", (2.1, 3.7, 0.82), (0.56, 0.44, 0.20), COL_STEEL_DK)
    for k in range(5):
        make_cyl(f"BassHead_Knob_{k}", (1.92 + k * 0.09, 3.46, 0.82), 0.015, 0.02,
                 COL_KNOB, segments=6, axis='Y')

    # ── Telecaster on a stand (butterscotch, the ch14 hero) ──
    gx, gy = -1.55, 2.2
    make_box("Tele_Body", (gx, gy, 0.42), (0.30, 0.05, 0.38), COL_TELE)
    make_box("Tele_Guard", (gx - 0.05, gy - 0.028, 0.40), (0.16, 0.006, 0.24), COL_TELE_GUARD)
    make_box("Tele_Neck", (gx + 0.02, gy, 0.82), (0.055, 0.04, 0.46), COL_BENCH)
    make_box("Tele_Head", (gx + 0.02, gy, 1.10), (0.08, 0.035, 0.14), COL_TELE)
    make_box("GStand_Leg_A", (gx - 0.10, gy + 0.08, 0.22), (0.03, 0.03, 0.45), COL_STEEL_DK)
    make_box("GStand_Leg_B", (gx + 0.10, gy + 0.08, 0.22), (0.03, 0.03, 0.45), COL_STEEL_DK)
    make_box("GStand_Foot", (gx, gy - 0.02, 0.03), (0.30, 0.26, 0.03), COL_STEEL_DK)
    # Bass on a stand by the bass rig
    make_box("Bass_Body", (1.55, 2.4, 0.44), (0.28, 0.05, 0.40), COL_BASS)
    make_box("Bass_Neck", (1.57, 2.4, 0.92), (0.05, 0.04, 0.56), COL_BENCH_DK)
    make_box("BStand_Foot", (1.55, 2.38, 0.03), (0.28, 0.26, 0.03), COL_STEEL_DK)

    # ── Mic stand front-center (Em's portable one) ──
    make_cyl("Mic_Post", (0.2, 1.35, 0.75), 0.018, 1.50, COL_STEEL_DK, segments=6)
    make_box("Mic_Boom", (0.2, 1.20, 1.50), (0.03, 0.34, 0.03), COL_STEEL_DK)
    make_cyl("Mic", (0.2, 1.02, 1.50), 0.028, 0.16, COL_STEEL, segments=8, axis='Y')
    make_box("Mic_Base", (0.2, 1.35, 0.02), (0.34, 0.30, 0.03), COL_STEEL_DK)

    # ── Cables snaking the floor ──
    for ci, (x0, y0, x1, y1) in enumerate([
            (-1.55, 2.0, -2.0, 3.4), (0.2, 1.5, -1.9, 2.6),
            (1.55, 2.6, 2.05, 3.4), (-0.3, 3.9, -2.0, 3.7)]):
        mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        make_box(f"Cable_{ci}", (mx, my, 0.012), (max(abs(x1 - x0), 0.02),
                 max(abs(y1 - y0), 0.02), 0.008), COL_CABLE)


def build_wall_dressing():
    """Workbench + pegboard on the north wall, paint shelf, fridge,
    box fan, crates, and the Foxhole flyer pinned by the door."""
    ny = ROOM_D - 0.30
    make_box("Bench_Top", (1.4, ny, 0.90), (2.2, 0.55, 0.05), COL_BENCH)
    for lx in (0.45, 2.35):
        make_box(f"Bench_Leg_{lx:.1f}", (lx, ny, 0.45), (0.06, 0.5, 0.90), COL_BENCH_DK)
    make_box("Bench_Shelf", (1.4, ny, 0.30), (2.1, 0.45, 0.03), COL_BENCH_DK)
    # Pegboard above the bench with hung tools
    make_box("Pegboard", (1.4, ROOM_D - 0.04, 1.65), (2.0, 0.03, 0.95), COL_PEG)
    make_box("Peg_Hammer_Handle", (0.8, ROOM_D - 0.07, 1.60), (0.035, 0.02, 0.30), COL_BENCH)
    make_box("Peg_Hammer_Head", (0.8, ROOM_D - 0.07, 1.77), (0.14, 0.03, 0.05), COL_STEEL_DK)
    make_box("Peg_Wrench", (1.15, ROOM_D - 0.07, 1.62), (0.04, 0.015, 0.26), COL_STEEL)
    make_cyl("Peg_TapeRoll", (1.5, ROOM_D - 0.09, 1.62), 0.07, 0.04, COL_STEEL_DK,
             segments=10, axis='Y')
    make_box("Peg_Saw", (1.95, ROOM_D - 0.07, 1.60), (0.30, 0.015, 0.10), COL_STEEL)
    make_box("Peg_Saw_Handle", (2.12, ROOM_D - 0.07, 1.60), (0.08, 0.02, 0.12), COL_BENCH_DK)
    # Paint-can shelf on the west wall
    make_box("PaintShelf", (-ROOM_W / 2.0 + 0.20, 4.6, 1.35), (0.36, 1.4, 0.03), COL_BENCH_DK)
    for pi in range(4):
        h = 0.20 if pi % 2 == 0 else 0.14
        make_cyl(f"PaintCan_{pi}", (-ROOM_W / 2.0 + 0.20, 4.05 + pi * 0.36, 1.37 + h / 2.0),
                 0.09, h, COL_PAINT, segments=10)
    # Mini fridge (E wall, band supplies)
    make_box("Fridge", (2.45, 1.4, 0.42), (0.55, 0.55, 0.84), COL_FRIDGE)
    make_box("Fridge_Door_Seam", (2.44, 1.12, 0.42), (0.52, 0.01, 0.80), COL_STEEL)
    make_box("Fridge_Handle", (2.20, 1.14, 0.60), (0.03, 0.02, 0.22), COL_STEEL_DK)
    # Box fan pointed at the kit (it is August)
    make_box("BoxFan", (-2.3, 1.5, 0.35), (0.14, 0.55, 0.55), COL_STEEL_DK)
    make_cyl("BoxFan_Grille", (-2.22, 1.5, 0.35), 0.24, 0.02, COL_STEEL, segments=14, axis='X')
    # Milk crates stacked by the amps
    for ci, (cx, cy, cz) in enumerate([(-2.45, 4.4, 0.17), (-2.45, 4.4, 0.51), (2.5, 4.5, 0.17)]):
        make_box(f"Crate_{ci}", (cx, cy, cz), (0.33, 0.33, 0.32), COL_CRATE, open_faces={"+Z"})
    # The Foxhole flyer pinned by the door jamb (ch14)
    make_box("Flyer", (ROOM_W / 2.0 - 0.13, 0.35, 1.45), (0.02, 0.22, 0.28), COL_FLYER)
    make_box("Flyer_Band", (ROOM_W / 2.0 - 0.125, 0.35, 1.52), (0.015, 0.18, 0.05), COL_STEEL_DK)
    # Bare-bulb ceiling fixture — the practical the tscn Omni sits on
    make_cyl("Bulb_Base", (0.0, 2.6, CEIL - 0.06), 0.05, 0.06, COL_STEEL_DK, segments=8)
    make_cyl("Bulb", (0.0, 2.6, CEIL - 0.14), 0.045, 0.09, COL_BULB, segments=10)


def main():
    clear_scene()
    build_shell()
    build_driveway()
    build_band_gear()
    build_wall_dressing()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/henderson_garage.glb"))
    print(f"\n[build_henderson_garage] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
