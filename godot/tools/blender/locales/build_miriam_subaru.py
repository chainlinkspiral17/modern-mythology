"""miriam_subaru — Miriam's car, vol 5 (the Moon, ch 18; Judgement, ch 20).

"Miriam's car was a 2009 Subaru wagon, dark green, immaculate. The back
seat had a folded blanket and a thermos of coffee. The crow, as they
reached the car, took flight from Miriam's shoulder and settled on the
roof. It did not ride inside. It rode above." (ch 18)

"Natalie sat in the back with Nicola. Miriam drove. ... Somewhere south
of Opelousas the sun rose fully. The light, slanting in through the
passenger window, caught on Nicola's face. Nicola had ... fallen back
asleep — her head against the window, her hand against her stomach."
"Miriam's eyes met Natalie's in the rearview." "Nicola, suddenly,
reached forward through the gap between the front seats." "They
reached the county line at seven fifty-two AM. Miriam pulled into a
gas station just past the sign." "I've left you cash in the side
pocket." "... watched the Subaru pull out, turn west, cross the
overpass, and disappear. The crow ... landed, instead, on the traffic
light above the gas-station exit." "She went inside the gas station.
Bought coffee. Sat on the metal bench beside the ice machine."
Judgement (ch 20): "in the back seat of Miriam's Subaru — which had, by
then, crossed the county line and was moving west on a two-lane road
through cane fields".

Until 2026-10-04 both chapters borrowed vol 6's `vehicle_cab` — Ben's
crew-cab pickup parked at a scrub turnout, the camera at the front
console — for a moving wagon with the women in the back seat.

THE SET. The wagon faces blender +Y in the right lane of a two-lane road
(road centre x -1.8) running north through cane fields, the camera in
the back seat behind the gap between the front seats. Ahead on the
right, 260 m up the road: the county-line sign, then the gas station
(canopy, two pump islands, the store with the ice machine and the metal
bench, the price pylon, the traffic light over the exit with the crow
on it) — and Miriam's Subaru again, parked at a pump, crow on the roof:
the county-line scene is a marker (`shot_wide_station`) on the same
set. Past the station an interstate overpass crosses the road; a sugar
mill smokes on the horizon. Coordinate frame: Blender Z-up; glTF → Godot
(x, z, -y).

DRAFT 1 (2026-10-04). Draft 2 targets: the passing world has no
motion (a `[trip]`/motion shader could carry the road); the two women
are not figures (portraits retired — the frames hold their places:
the blanket, the window, the gap); headlights for a night drive.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path:
    sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_blob, make_lathe, make_chamfer_box,
                             make_rot_box, make_taper_cyl, make_tube, export_glb)
from _props.detail import make_far_bands
from _props.creatures import make_crow

SUBARU = (0.16, 0.27, 0.21, 1.0)          # dark green, immaculate
SUBARU_DK = (0.11, 0.19, 0.15, 1.0)
GLASS = (0.62, 0.70, 0.74, 0.22)
GLASS_TINT = (0.34, 0.40, 0.42, 0.42)     # the rear quarter + the parked car's tint
CHROME = (0.74, 0.76, 0.78, 1.0)
RUBBER = (0.10, 0.10, 0.11, 1.0)
DASH = (0.17, 0.17, 0.18, 1.0)
DASH_LT = (0.30, 0.30, 0.31, 1.0)
CLOTH = (0.60, 0.58, 0.54, 1.0)           # the 2009 Outback's light warm-grey cloth
CLOTH_DK = (0.48, 0.46, 0.43, 1.0)
HEADLINER = (0.74, 0.72, 0.66, 1.0)
CARPET = (0.20, 0.20, 0.20, 1.0)
ASPHALT = (0.28, 0.28, 0.30, 1.0)
CANE = ((0.34, 0.48, 0.24, 1.0), (0.40, 0.52, 0.28, 1.0), (0.30, 0.42, 0.22, 1.0), (0.44, 0.54, 0.30, 1.0))

Z_FLOOR = 0.40
Z_BELT = 1.02
Z_ROOF = 1.62          # (draft 1b: 1.53 left 0.89 m over the rear cushion — an Outback has ~0.98)
ROAD_CX = -1.8


def _h01(a, b):
    v = math.sin(a * 12.9898 + b * 78.233) * 43758.5453
    return v - math.floor(v)


# ── the road and the cane ─────────────────────────────────────────
def build_road():
    make_box("Ground_Far", (0.0, 0.0, -0.08), (1400.0, 1400.0, 0.02), (0.34, 0.36, 0.24, 1.0))
    make_box("Road_Asphalt", (ROAD_CX, 0.0, -0.03), (7.2, 900.0, 0.06), ASPHALT)
    for sgn in (-1, 1):
        make_box(f"Road_Shoulder_{'W' if sgn < 0 else 'E'}", (ROAD_CX + sgn * 4.2, 0.0, -0.035), (1.2, 900.0, 0.05),
                 (0.52, 0.49, 0.42, 1.0))
        make_box(f"Road_Ditch_{'W' if sgn < 0 else 'E'}", (ROAD_CX + sgn * 6.0, 0.0, -0.06), (2.4, 900.0, 0.03),
                 (0.24, 0.32, 0.18, 1.0))
        make_box(f"Road_Edge_Line_{'W' if sgn < 0 else 'E'}", (ROAD_CX + sgn * 3.45, 0.0, 0.002), (0.10, 900.0, 0.004),
                 (0.86, 0.86, 0.84, 1.0))
    for sgn in (-1, 1):
        make_box(f"Road_Center_Line_{'W' if sgn < 0 else 'E'}", (ROAD_CX + sgn * 0.09, 0.0, 0.002), (0.10, 900.0, 0.004),
                 (0.88, 0.74, 0.22, 1.0))


def build_cane():
    """Cane in rows parallel to the road, cut by headland lanes every
    200 m; a wall of green at the window, a texture to the horizon."""
    for side, x0, x1 in (("E", 5.4, 46.0), ("W", -48.0, -9.0)):
        nrows = int((x1 - x0) / 1.6)
        for r in range(nrows):
            rx = x0 + r * 1.6 + 0.45
            for sgi in range(22):
                y0 = -440.0 + sgi * 40.0
                if (sgi % 5) == 2:
                    continue                           # a headland lane
                if side == "E" and 238.0 < y0 + 40.0 and y0 < 300.0 and rx < 44.0:
                    continue                           # the gas station's lot
                if 360.0 < y0 + 40.0 and y0 < 385.0:
                    continue                           # under the overpass (piers, berms)
                h = 2.5 + 0.9 * _h01(r * 3 + (1 if side == "E" else 7), sgi)
                make_box(f"Cane_{side}_{r}_{sgi}", (rx, y0 + 20.0, h / 2.0), (0.95, 39.6, h),
                         CANE[int(_h01(r, sgi * 5) * 4) % 4])


def build_roadside():
    """Utility poles down the west shoulder with their wires, the
    county-line sign, the overpass past the station, the sugar mill."""
    pole = (0.36, 0.30, 0.22, 1.0)
    px = ROAD_CX - 7.6
    ys = [-430.0 + 45.0 * k for k in range(20)]
    for k, py in enumerate(ys):
        make_cyl(f"Pole_{k}", (px, py, 4.25), 0.13, 8.5, pole, segments=8)
        make_box(f"Pole_{k}_Crossarm", (px, py, 8.05), (1.8, 0.10, 0.10), pole)
    for wi, wx in enumerate((-0.75, 0.0, 0.75)):
        make_box(f"Pole_Wire_{wi}", (px + wx, (ys[0] + ys[-1]) / 2.0, 8.106), (0.012, ys[-1] - ys[0], 0.012),
                 (0.20, 0.20, 0.20, 1.0))
    # the county-line sign, facing the oncoming car
    for sx in (3.2, 4.8):
        make_box(f"County_Sign_Post_{sx:.1f}", (sx, 228.0, 1.10), (0.08, 0.08, 2.2), (0.60, 0.60, 0.58, 1.0))
    make_box("County_Sign", (4.0, 227.94, 2.05), (2.0, 0.04, 0.90), (0.12, 0.40, 0.24, 1.0))
    make_box("County_Sign_Border", (4.0, 227.915, 2.05), (1.86, 0.01, 0.76), (0.90, 0.90, 0.88, 1.0))
    make_box("County_Sign_Field", (4.0, 227.91, 2.05), (1.80, 0.004, 0.70), (0.12, 0.40, 0.24, 1.0))
    # the overpass the Subaru crosses under (I-49), past the station
    make_box("Overpass_Deck", (ROAD_CX, 372.0, 6.6), (90.0, 13.0, 0.9), (0.62, 0.61, 0.58, 1.0))
    for sgn in (-1, 1):
        make_box(f"Overpass_Parapet_{'S' if sgn < 0 else 'N'}", (ROAD_CX, 372.0 + sgn * 6.3, 7.45), (90.0, 0.35, 0.8),
                 (0.66, 0.65, 0.62, 1.0))
    for bx in (ROAD_CX - 9.0, ROAD_CX + 9.0):
        make_box(f"Overpass_Pier_{bx:.0f}", (bx, 372.0, 3.075), (1.2, 10.0, 6.15), (0.58, 0.57, 0.54, 1.0))
    for ex in (-40.0, 36.0):
        make_box(f"Overpass_Berm_{ex:.0f}", (ROAD_CX + ex, 372.0, 3.075), (14.0, 16.0, 6.15), (0.36, 0.40, 0.26, 1.0))
    # the sugar mill on the horizon, steaming
    mill = (0.46, 0.44, 0.42, 1.0)
    make_box("Sugar_Mill_Body", (190.0, 520.0, 9.0), (60.0, 30.0, 18.0), mill)
    make_box("Sugar_Mill_Shed", (148.0, 515.0, 5.0), (24.0, 26.0, 10.0), (0.52, 0.48, 0.42, 1.0))
    for si, sx in enumerate((176.0, 196.0, 212.0)):
        make_cyl(f"Sugar_Mill_Stack_{si}", (sx, 528.0, 18.0 + (16.0 + 4.0 * si) / 2.0), 1.8, 16.0 + 4.0 * si, (0.40, 0.36, 0.34, 1.0), segments=12)
        for pi in range(3):
            make_blob(f"Sugar_Mill_Steam_{si}_{pi}", (sx + pi * 4.0, 528.0 + pi * 2.0, 36.0 + 4.0 * si + pi * 5.0),
                      4.0 + pi * 1.5, (0.86, 0.86, 0.84, 1.0), noise=0.25, seed=si * 7 + pi, squash=0.7)
    make_far_bands("Far_Treeline", (0.30, 0.36, 0.26, 1.0),
                   [(560.0, 600.0, 14.0, 0.85), (640.0, 680.0, 20.0, 0.70)], sides="NEW", profile="treeline")


# ── the gas station at the county line ───────────────────────────
def build_station():
    lot = (0.36, 0.36, 0.37, 1.0)
    make_box("Station_Lot_Asphalt", (23.0, 268.0, -0.02), (38.0, 46.0, 0.05), lot)
    # canopy over two islands
    canopy = (0.88, 0.88, 0.86, 1.0)
    make_box("Station_Canopy", (13.0, 264.0, 4.85), (14.0, 11.0, 0.60), canopy)
    make_box("Station_Canopy_Band", (13.0, 258.47, 4.85), (14.0, 0.06, 0.40), (0.72, 0.16, 0.14, 1.0))
    for cx in (8.0, 18.0):
        for cy in (260.0, 268.0):
            make_box(f"Station_Canopy_Col_{cx:.0f}_{cy:.0f}", (cx, cy, 2.275), (0.40, 0.40, 4.55), canopy)
    for ii, ix in enumerate((9.5, 16.5)):
        make_box(f"Station_Island_{ii}", (ix, 264.0, 0.075), (0.9, 6.0, 0.15), (0.64, 0.63, 0.60, 1.0))
        for pj, py in enumerate((262.2, 265.8)):
            make_box(f"Station_Pump_{ii}{pj}", (ix, py, 0.15 + 0.85), (0.55, 0.75, 1.70), (0.84, 0.84, 0.82, 1.0))
            make_box(f"Station_Pump_{ii}{pj}_Face", (ix - 0.28, py, 1.30), (0.01, 0.55, 0.50), (0.18, 0.20, 0.22, 1.0))
            make_tube(f"Station_Pump_{ii}{pj}_Hose", [(ix - 0.29, py + 0.30, 1.40), (ix - 0.45, py + 0.32, 0.90),
                                                    (ix - 0.32, py + 0.30, 0.60)], 0.02, RUBBER, segments=5)
    # the store: ice machine and the metal bench at its front
    store = (0.78, 0.74, 0.66, 1.0)
    make_box("Station_Store", (32.0, 276.0, 2.0), (14.0, 9.0, 4.0), store)
    make_box("Station_Store_Fascia", (32.0, 271.47, 3.6), (14.2, 0.06, 0.8), (0.72, 0.16, 0.14, 1.0))
    make_box("Station_Store_Window", (33.6, 271.48, 1.55), (6.0, 0.03, 1.7), GLASS_TINT)
    make_box("Station_Store_Doorway", (28.6, 271.48, 1.10), (1.8, 0.03, 2.2), (0.20, 0.22, 0.24, 1.0))
    make_box("Station_Ice_Machine", (25.8, 270.9, 0.95), (1.3, 0.8, 1.9), (0.90, 0.92, 0.94, 1.0))
    make_box("Station_Ice_Machine_Label", (25.8, 270.495, 1.45), (0.9, 0.01, 0.35), (0.22, 0.44, 0.74, 1.0))
    make_box("Station_Bench_Seat", (36.8, 270.6, 0.45), (1.8, 0.40, 0.04), (0.56, 0.58, 0.60, 1.0))
    make_box("Station_Bench_Back", (36.8, 270.82, 0.73), (1.8, 0.04, 0.52), (0.56, 0.58, 0.60, 1.0))
    for lx in (36.0, 37.6):
        make_box(f"Station_Bench_Leg_{lx:.1f}", (lx, 270.6, 0.215), (0.05, 0.36, 0.43), (0.40, 0.42, 0.44, 1.0))
    # the price pylon at the road
    make_box("Station_Pylon_Post", (4.6, 248.0, 2.3), (0.35, 0.35, 4.6), (0.60, 0.60, 0.58, 1.0))
    make_box("Station_Pylon_Panel", (4.6, 248.0, 5.4), (2.2, 0.30, 1.6), (0.88, 0.86, 0.80, 1.0))
    make_box("Station_Pylon_Band", (4.6, 247.84, 5.95), (2.2, 0.02, 0.36), (0.72, 0.16, 0.14, 1.0))
    # the traffic light above the gas-station exit, the crow on it
    make_cyl("Signal_Mast", (3.4, 252.0, 2.9), 0.11, 5.8, (0.30, 0.31, 0.30, 1.0), segments=8)
    make_box("Signal_Arm", (ROAD_CX + 2.3, 252.0, 5.75), (7.2, 0.12, 0.12), (0.30, 0.31, 0.30, 1.0))
    make_box("Signal_Head", (ROAD_CX, 252.0, 5.20), (0.34, 0.30, 0.95), (0.18, 0.20, 0.10, 1.0))
    make_box("Signal_Head_Hanger", (ROAD_CX, 252.0, 5.6825), (0.05, 0.05, 0.015), (0.30, 0.31, 0.30, 1.0))
    for li, (lz, col) in enumerate(((5.50, (0.30, 0.10, 0.08, 1.0)), (5.20, (0.30, 0.24, 0.08, 1.0)), (4.90, (0.30, 0.90, 0.50, 1.0)))):
        make_cyl(f"Signal_Lamp_{li}", (ROAD_CX, 251.84, lz), 0.10, 0.02, col, axis='Y', segments=10)
    make_crow("Signal_Crow", 0.6, 252.0, 5.81, facing=1.0)        # on the mast arm (top 5.81), over the road edge


# ── the wagon ─────────────────────────────────────────────────────
def build_cabin():
    """The hollow the camera sits in: floor, sides, pillars, glass, the
    raked windshield, roof + headliner, rear hatch."""
    make_box("Car_Floor", (0.0, -0.30, Z_FLOOR - 0.02), (1.50, 3.40, 0.04), CARPET)
    for sgn, nm in ((-1, "L"), (1, "R")):
        make_box(f"Car_Skin_{nm}", (sgn * 0.775, -0.40, (0.30 + Z_BELT) / 2.0), (0.03, 3.30, Z_BELT - 0.30), SUBARU)
        make_box(f"Car_Door_Card_F_{nm}", (sgn * 0.745, 0.58, (Z_FLOOR + Z_BELT) / 2.0), (0.03, 1.00, Z_BELT - Z_FLOOR), CLOTH_DK)
        make_box(f"Car_Door_Card_R_{nm}", (sgn * 0.745, -0.52, (Z_FLOOR + Z_BELT) / 2.0), (0.03, 0.92, Z_BELT - Z_FLOOR), CLOTH_DK)
        make_box(f"Car_Armrest_F_{nm}", (sgn * 0.70, 0.45, 0.80), (0.06, 0.46, 0.05), DASH_LT)
        make_box(f"Car_Armrest_R_{nm}", (sgn * 0.70, -0.62, 0.80), (0.06, 0.40, 0.05), DASH_LT)
        make_box(f"Car_Door_Pocket_R_{nm}", (sgn * 0.715, -0.52, 0.58), (0.03, 0.50, 0.14), DASH)
        make_box(f"Car_Door_Handle_R_{nm}", (sgn * 0.728, -0.22, 0.90), (0.006, 0.12, 0.03), CHROME)
        # pillars: B, C, D vertical; glass between
        for pn, py, pw in (("B", 0.04, 0.10), ("C", -0.98, 0.10), ("D", -2.00, 0.12)):
            make_box(f"Car_Pillar_{pn}_{nm}", (sgn * 0.765, py, (Z_BELT + Z_ROOF) / 2.0), (0.04, pw, Z_ROOF - Z_BELT), SUBARU_DK)
        make_box(f"Car_Glass_F_{nm}", (sgn * 0.77, 0.58, (Z_BELT + Z_ROOF) / 2.0), (0.01, 1.00, Z_ROOF - Z_BELT - 0.02), GLASS)
        make_box(f"Car_Glass_R_{nm}", (sgn * 0.77, -0.47, (Z_BELT + Z_ROOF) / 2.0), (0.01, 0.92, Z_ROOF - Z_BELT - 0.02), GLASS)
        make_box(f"Car_Glass_Q_{nm}", (sgn * 0.77, -1.49, (Z_BELT + Z_ROOF) / 2.0), (0.01, 0.92, Z_ROOF - Z_BELT - 0.02), GLASS_TINT)
        make_box(f"Car_Belt_Trim_{nm}", (sgn * 0.765, -0.40, Z_BELT + 0.01), (0.05, 3.30, 0.02), DASH)
        make_box(f"Car_Roof_Rail_{nm}", (sgn * 0.62, -0.45, Z_ROOF + 0.06), (0.05, 2.30, 0.04), DASH)
        for ry in (0.60, -1.50):
            make_box(f"Car_Roof_Rail_Foot_{nm}_{ry:.1f}", (sgn * 0.62, ry, Z_ROOF + 0.03), (0.06, 0.08, 0.02), DASH)
    make_box("Car_Moving_Roof", (0.0, -0.48, Z_ROOF + 0.005), (1.56, 3.14, 0.04), SUBARU)
    make_box("Car_Headliner", (0.0, -0.48, Z_ROOF - 0.03), (1.48, 3.04, 0.01), HEADLINER)
    # the raked windshield, A pillars, cowl
    rake = math.atan2(0.62, Z_ROOF - Z_BELT)
    ln = math.hypot(0.62, Z_ROOF - Z_BELT)
    make_rot_box("Car_Windshield", (0.0, 1.38, (Z_BELT + Z_ROOF) / 2.0), (1.44, 0.01, ln), GLASS, roll=rake)
    for sgn, nm in ((-1, "L"), (1, "R")):
        make_rot_box(f"Car_Pillar_A_{nm}", (sgn * 0.745, 1.38, (Z_BELT + Z_ROOF) / 2.0), (0.06, 0.06, ln), SUBARU_DK, roll=rake)
    make_box("Car_Windshield_Header", (0.0, 1.08, Z_ROOF - 0.01), (1.48, 0.06, 0.04), SUBARU_DK)
    # rear hatch: panel + glass
    make_box("Car_Hatch_Panel", (0.0, -2.04, (0.30 + Z_BELT) / 2.0), (1.52, 0.03, Z_BELT - 0.30), SUBARU)
    make_box("Car_Hatch_Glass", (0.0, -2.04, (Z_BELT + Z_ROOF) / 2.0), (1.40, 0.01, Z_ROOF - Z_BELT - 0.04), GLASS_TINT)
    make_box("Car_Cargo_Floor", (0.0, -1.62, 0.60), (1.40, 0.80, 0.04), CARPET)
    for sgn, nm in ((-1, "L"), (1, "R")):
        make_box(f"Car_Cargo_Side_{nm}", (sgn * 0.725, -1.54, (Z_FLOOR + Z_BELT) / 2.0), (0.05, 0.96, Z_BELT - Z_FLOOR), CLOTH_DK)
    # dome + map lights, rearview, visors
    make_box("Car_Dome_Light", (0.0, -0.55, Z_ROOF - 0.04), (0.20, 0.10, 0.02), (0.92, 0.90, 0.82, 1.0))
    make_cyl("Car_Rearview_Stalk", (0.0, 1.11, Z_ROOF - 0.07), 0.012, 0.07, RUBBER, segments=6)
    make_box("Rearview_Mirror", (0.0, 1.10, Z_ROOF - 0.135), (0.25, 0.05, 0.07), (0.16, 0.16, 0.17, 1.0))
    make_box("Rearview_Mirror_Glass", (0.0, 1.0745, Z_ROOF - 0.135), (0.23, 0.001, 0.055), (0.62, 0.66, 0.70, 1.0))
    for sgn, nm in ((-1, "L"), (1, "R")):
        make_box(f"Car_Sun_Visor_{nm}", (sgn * 0.40, 1.00, Z_ROOF - 0.045), (0.58, 0.26, 0.02), HEADLINER)


def build_front():
    """Dash, cluster, the CD head unit, the wheel on the left; the hood
    beyond the glass."""
    make_box("Dash_Face", (0.0, 1.00, 0.72), (1.46, 0.06, 0.50), DASH)
    make_chamfer_box("Dash_Top", (0.0, 1.32, 0.99), (1.46, 0.66, 0.08), DASH_LT, chamfer=0.03)
    make_box("Car_Cluster_Hood", (-0.38, 1.06, 1.06), (0.42, 0.18, 0.06), DASH)
    make_box("Gauge_Cluster", (-0.38, 0.968, 0.92), (0.38, 0.004, 0.14), (0.08, 0.08, 0.09, 1.0))
    for gi, gx in enumerate((-0.46, -0.30)):
        make_cyl(f"Gauge_{gi}", (gx, 0.965, 0.92), 0.055, 0.003, (0.80, 0.62, 0.30, 1.0), axis="Y", segments=12)
    make_box("Head_Unit", (0.0, 0.968, 0.84), (0.30, 0.004, 0.16), (0.10, 0.10, 0.11, 1.0))
    make_box("Head_Unit_Display", (0.0, 0.965, 0.88), (0.16, 0.002, 0.04), (0.40, 0.74, 0.92, 1.0))
    make_box("Head_Unit_CD_Slot", (0.0, 0.965, 0.82), (0.14, 0.002, 0.006), (0.02, 0.02, 0.02, 1.0))
    for vi, vx in enumerate((-0.15, 0.15)):
        make_box(f"Dash_Vent_{vi}", (vx, 0.968, 0.96), (0.13, 0.004, 0.05), (0.12, 0.12, 0.13, 1.0))
    for ki, kx in enumerate((-0.09, 0.0, 0.09)):
        make_cyl(f"Climate_Knob_{ki}", (kx, 0.962, 0.70), 0.022, 0.016, DASH_LT, axis="Y", segments=10)
    make_box("Glovebox", (0.40, 0.968, 0.70), (0.48, 0.004, 0.22), DASH_LT)
    make_cyl("Steering_Column", (-0.38, 0.865, 0.86), 0.032, 0.21, DASH, axis="Y", segments=8)
    for si in range(16):
        a = si * 2.0 * math.pi / 16.0
        make_chamfer_box(f"Steering_Rim_{si}", (-0.38 + 0.185 * math.cos(a), 0.74, 0.86 + 0.185 * math.sin(a)),
                         (0.073, 0.032, 0.032), (0.12, 0.12, 0.12, 1.0), chamfer=0.01)
    make_lathe("Steering_Hub", (-0.38, 0.74, 0.86), [(0.0, 0.0), (0.07, 0.0), (0.075, 0.02), (0.06, 0.05), (0.0, 0.055)],
               DASH, segments=12)
    for sn, (dx, dz, sx, sz) in (("L", (-0.10, 0.0, 0.11, 0.03)), ("R", (0.10, 0.0, 0.11, 0.03)), ("D", (0.0, -0.09, 0.03, 0.15))):
        make_box(f"Steering_Spoke_{sn}", (-0.38 + dx, 0.74, 0.86 + dz), (sx, 0.02, sz), DASH)
    make_box("Steering_Spoke_U", (-0.38, 0.74, 0.86 + 0.10), (0.03, 0.02, 0.14), DASH)
    for di, a_ in enumerate((0.785, 2.356, 3.927, 5.498)):      # out to the rim
        make_rot_box(f"Steering_Spoke_X{di}", (-0.38 + 0.105 * math.cos(a_), 0.74, 0.86 + 0.105 * math.sin(a_)),
                     (0.14, 0.02, 0.03), DASH, pitch=-a_)
    # the hood + fenders past the glass, wipers parked on the cowl
    make_rot_box("Car_Moving_Hood", (0.0, 2.25, 0.93), (1.62, 1.30, 0.06), SUBARU, roll=-0.10)
    make_box("Car_Cowl", (0.0, 1.62, 1.00), (1.50, 0.16, 0.06), (0.10, 0.10, 0.11, 1.0))
    for sgn, nm in ((-1, "L"), (1, "R")):
        make_box(f"Car_Fender_{nm}", (sgn * 0.83, 2.25, 0.74), (0.12, 1.30, 0.42), SUBARU)
        make_rot_box(f"Car_Wiper_{nm}", (sgn * 0.30, 1.66, 1.04), (0.58, 0.015, 0.012), RUBBER, yaw=sgn * 0.08)


def build_seats():
    for sgn, nm in ((-1, "Driver"), (1, "Passenger")):
        x = sgn * 0.37
        make_chamfer_box(f"Seat_{nm}_Base", (x, 0.30, 0.56), (0.52, 0.52, 0.20), CLOTH, chamfer=0.04)
        make_rot_box(f"Seat_{nm}_Back", (x, -0.02, 0.97), (0.52, 0.12, 0.64), CLOTH, roll=0.18)
        hx, hz = x, 0.97 + 0.32 * math.cos(0.18) + 0.09
        hy = -0.02 - 0.32 * math.sin(0.18) - 0.02
        make_chamfer_box(f"Seat_{nm}_Headrest", (hx, hy, hz), (0.26, 0.10, 0.17), CLOTH_DK, chamfer=0.03)
        for px in (-0.07, 0.07):
            make_cyl(f"Seat_{nm}_Headrest_Post_{px:+.2f}", (hx + px, hy, hz - 0.115), 0.007, 0.06, CHROME, segments=6)
    make_chamfer_box("Console", (0.0, 0.40, 0.55), (0.24, 0.80, 0.30), DASH, chamfer=0.03)
    make_box("Console_Armrest", (0.0, 0.10, 0.715), (0.22, 0.30, 0.03), CLOTH_DK)
    make_cyl("Shifter_Boot", (0.0, 0.62, 0.715), 0.035, 0.03, RUBBER, segments=8)
    make_cyl("Shifter_Stalk", (0.0, 0.62, 0.79), 0.012, 0.12, CHROME, segments=6)
    make_lathe("Shifter_Knob", (0.0, 0.62, 0.85), [(0.0, 0.0), (0.02, 0.0), (0.03, 0.02), (0.028, 0.045), (0.0, 0.055)],
               (0.14, 0.14, 0.14, 1.0), segments=10)
    for ci, cy in enumerate((0.38, 0.30)):
        make_cyl(f"Cupholder_{ci}", (0.0, cy, 0.700), 0.045, 0.002, (0.08, 0.08, 0.08, 1.0), segments=12)
    # Miriam's travel mug in the near cupholder
    make_cyl("Miriam_Mug", (0.0, 0.38, 0.775), 0.040, 0.15, (0.72, 0.70, 0.66, 1.0), segments=12)
    make_cyl("Miriam_Mug_Lid", (0.0, 0.38, 0.855), 0.042, 0.012, (0.14, 0.14, 0.14, 1.0), segments=12)
    # the rear bench: base, back, three headrests
    make_chamfer_box("Rear_Bench_Base", (0.0, -0.74, 0.53), (1.40, 0.50, 0.22), CLOTH, chamfer=0.05)
    make_rot_box("Rear_Bench_Back", (0.0, -1.05, 0.96), (1.40, 0.12, 0.62), CLOTH, roll=0.16)
    for hx in (-0.42, 0.0, 0.42):
        # the right rear seat is Nicola's — her head against the window
        make_chamfer_box("Nicola_Headrest" if hx > 0.1 else f"Rear_Headrest_{hx:+.2f}", (hx, -1.05 - 0.31 * math.sin(0.16) - 0.02, 0.96 + 0.31 * math.cos(0.16) + 0.08),
                         (0.24, 0.09, 0.14), CLOTH_DK, chamfer=0.03)
    for sgn, nm in ((-1, "L"), (1, "R")):
        make_box(f"Floor_Mat_F_{nm}", (sgn * 0.37, 0.70, Z_FLOOR + 0.003), (0.48, 0.52, 0.006), (0.12, 0.12, 0.12, 1.0))
        make_box(f"Floor_Mat_R_{nm}", (sgn * 0.37, -0.28, Z_FLOOR + 0.003), (0.48, 0.34, 0.006), (0.12, 0.12, 0.12, 1.0))


def build_passengers_things():
    """What the back seat holds: the folded blanket and the thermos, the
    duffel at Nicola's feet, Miriam's canvas bag on the front seat, the
    cash in Natalie's side pocket."""
    seat_top = 0.64
    make_chamfer_box("Back_Seat_Blanket", (0.0, -0.70, seat_top + 0.06), (0.42, 0.32, 0.12), (0.46, 0.18, 0.16, 1.0), chamfer=0.02)
    for si, sx in enumerate((-0.12, 0.0, 0.12)):
        make_box(f"Back_Seat_Blanket_Stripe_{si}", (sx, -0.70, seat_top + 0.1205), (0.025, 0.32, 0.001), (0.20, 0.34, 0.24, 1.0))
    make_cyl("Back_Seat_Thermos", (0.20, -0.66, seat_top + 0.045), 0.045, 0.26, (0.26, 0.40, 0.36, 1.0), axis="Y", segments=12)
    make_cyl("Back_Seat_Thermos_Cap", (0.20, -0.515, seat_top + 0.045), 0.048, 0.03, (0.14, 0.14, 0.14, 1.0), axis="Y", segments=12)
    make_chamfer_box("Footwell_Duffel", (0.38, -0.30, Z_FLOOR + 0.006 + 0.14), (0.42, 0.26, 0.28), (0.24, 0.28, 0.36, 1.0), chamfer=0.05)
    make_chamfer_box("Miriam_Canvas_Bag", (0.37, 0.30, 0.66 + 0.06), (0.36, 0.26, 0.12), (0.62, 0.56, 0.42, 1.0), chamfer=0.03)
    make_box("Natalie_Cash_Envelope", (-0.697, -0.58, 0.67), (0.006, 0.11, 0.07), (0.92, 0.90, 0.84, 1.0))


def build_exterior_shell():
    """What of the moving wagon shows outside its own glass — and the
    crow, riding above."""
    for sgn, nm in ((-1, "L"), (1, "R")):
        for wy, wn in ((1.60, "F"), (-1.40, "R")):
            make_cyl(f"Car_Wheel_{wn}_{nm}", (sgn * 0.82, wy, 0.33), 0.33, 0.20, RUBBER, axis="X", segments=16)
            make_cyl(f"Car_Wheel_{wn}_{nm}_Hub", (sgn * 0.923, wy, 0.33), 0.20, 0.006, CHROME, axis="X", segments=12)
        make_box(f"Car_Mirror_{nm}", (sgn * 0.88, 1.12, 1.08), (0.18, 0.06, 0.12), SUBARU)
    make_box("Car_Moving_Underbody", (0.0, -0.20, 0.31), (1.50, 3.60, 0.10), (0.08, 0.08, 0.08, 1.0))
    make_box("Car_Front_Bumper", (0.0, 2.95, 0.55), (1.70, 0.12, 0.36), SUBARU_DK)
    make_box("Car_Rear_Bumper", (0.0, -2.12, 0.50), (1.70, 0.12, 0.34), SUBARU_DK)
    make_crow("Car_Roof_Crow", 0.18, -0.70, Z_ROOF + 0.025, facing=1.0)


def build_parked_subaru():
    """The same car at the county-line pump, crow on the roof — the
    station marker's subject. Tinted glass (no interior to see)."""
    cx, cy = 12.2, 262.0
    make_box("Parked_Subaru_Body", (cx, cy, 0.68), (1.78, 4.70, 0.70), SUBARU)
    make_box("Parked_Subaru_Greenhouse", (cx, cy - 0.35, (1.03 + Z_ROOF) / 2.0), (1.52, 3.00, Z_ROOF - 1.03 + 0.01), GLASS_TINT)
    make_box("Parked_Subaru_Roof", (cx, cy - 0.35, Z_ROOF + 0.025), (1.56, 3.10, 0.05), SUBARU)
    make_rot_box("Parked_Subaru_Hood", (cx, cy + 1.75, 1.07), (1.70, 1.10, 0.06), SUBARU, roll=-0.08)
    for sgn in (-1, 1):
        make_box(f"Parked_Subaru_Rail_{sgn:+d}", (cx + sgn * 0.62, cy - 0.35, Z_ROOF + 0.08), (0.05, 2.20, 0.04), DASH)
        for wy in (1.55, -1.45):
            make_cyl(f"Parked_Subaru_Wheel_{sgn:+d}_{wy:+.1f}", (cx + sgn * 0.80, cy + wy, 0.33), 0.33, 0.22, RUBBER, axis="X", segments=16)
        make_box(f"Parked_Subaru_Light_F_{sgn:+d}", (cx + sgn * 0.62, cy + 2.355, 0.86), (0.36, 0.01, 0.14), (0.92, 0.90, 0.80, 1.0))
        make_box(f"Parked_Subaru_Light_R_{sgn:+d}", (cx + sgn * 0.66, cy - 2.355, 0.92), (0.26, 0.01, 0.24), (0.62, 0.10, 0.08, 1.0))
    make_crow("Parked_Subaru_Crow", cx - 0.15, cy - 0.60, Z_ROOF + 0.05, facing=-1.0)


def main():
    clear_scene()
    build_road()
    build_cane()
    build_roadside()
    build_station()
    build_cabin()
    build_front()
    build_seats()
    build_passengers_things()
    build_exterior_shell()
    build_parked_subaru()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/miriam_subaru.glb"))
    print(f"\n[build_miriam_subaru] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
