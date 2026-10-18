"""bus_station — vol 4's city bus station and the bus (draft 1, 2026-10-18).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
vol4_cc_1 / cc_2 (the screenplay adaptation): a city never named, day.
THE STATION (origin) — "A Bus Station / Ext. · Day": "CAROLINE walks up to
the bus overhang. She has a bag by her side." Charlie stands reading a
newspaper with his own name on it, folds it, crosses to her, lights her
cigarette. The terminal's doors open onto the canopied curb; the street
and the city across it.
THE BUS (x 60..62.6, nose north) — "They both sit on the bus": seats in
side-by-side pairs, Carrie on the inside (window) seat, the aisle seat
beside her ("passing in front of" George to get off); "The window throws
the city across both their faces, a frame at a time"; stops, riders getting
on and off. No glass in the windows (our panes are opaque): the city stands
outside the frames.

Blender: x east, y north, z up; Godot (x, z, -y).

DRAFT 2 targets: the city passing the bus window as motion (a scrolling
backdrop); the station's inside past its doors; a bus at the curb; Deck
framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, join_stock, export_glb)
from _props.vehicles import make_car

CONCRETE = (0.70, 0.68, 0.64, 1.0); ASPHALT = (0.30, 0.30, 0.32, 1.0); CURB = (0.62, 0.60, 0.56, 1.0)
STEEL = (0.58, 0.60, 0.62, 1.0); GLASS = (0.36, 0.44, 0.50, 1.0)
CITY = [(0.62, 0.60, 0.56, 1.0), (0.48, 0.50, 0.54, 1.0), (0.70, 0.66, 0.58, 1.0), (0.40, 0.42, 0.46, 1.0), (0.76, 0.72, 0.64, 1.0)]


def city_block(prefix, x0, x1, y, side, seed=0, h0=12.0):
    """A row of city buildings fronting y, rising away from the street."""
    x = x0
    k = 0
    while x < x1:
        w = 8.0 + ((k * 7 + seed) % 4) * 3.0
        h = h0 + ((k * 5 + seed) % 5) * 8.0
        d = 14.0
        p = f"{prefix}_Stock_{k}"
        make_box(p + "_Mass", (x + w / 2.0, y + side * d / 2.0, h / 2.0), (w - 0.2, d, h), CITY[(k + seed) % len(CITY)])
        for f in range(int(h / 3.4)):
            make_box(p + f"_Band_{f}", (x + w / 2.0, y - side * 0.01, 1.8 + f * 3.4), (w - 0.8, 0.02, 1.4), (0.26, 0.30, 0.36, 1.0))
        x += w
        k += 1


def build_station():
    # the terminal along the N side, its glass doors, the overhang over the curb
    make_box("Term_Mass", (0.0, 8.0, 4.0), (30.0, 16.0, 8.0), (0.74, 0.72, 0.66, 1.0))
    make_box("Term_Glass_Band", (0.0, -0.01, 1.5), (18.0, 0.02, 2.8), GLASS)
    for k in range(10):
        if k in (4, 5):
            continue            # the doors stand here
        make_box(f"Term_Mullion_{k}", (-9.0 + k * 2.0, -0.04, 1.5), (0.08, 0.08, 2.8), STEEL)
    for s in (-1, 1):
        make_box(f"Term_Door_{s:+d}", (s * 0.6, -0.03, 1.31), (1.16, 0.04, 2.30), (0.30, 0.34, 0.40, 1.0))
    make_box("Term_Door_Frame", (0.0, -0.05, 2.52), (2.6, 0.06, 0.12), STEEL)
    make_box("Term_Sign", (0.0, -0.05, 3.70), (6.0, 0.08, 0.70), (0.20, 0.34, 0.60, 1.0))
    make_box("Term_Sign_Letters", (0.0, -0.10, 3.70), (4.6, 0.02, 0.32), (0.94, 0.94, 0.92, 1.0))
    # the overhang: a canopy out over the curb on its posts
    make_box("Overhang_Roof", (0.0, -2.65, 3.10), (24.0, 5.3, 0.24), (0.52, 0.54, 0.58, 1.0))
    make_box("Overhang_Fascia", (0.0, -5.30, 3.0), (24.0, 0.10, 0.44), (0.80, 0.30, 0.20, 1.0))
    for k in range(7):
        make_cyl(f"Overhang_Post_{k}", (-11.0 + k * 3.66, -4.9, 1.57), 0.10, 2.82, STEEL, segments=10)
    for k in range(4):
        make_box(f"Overhang_Light_{k}", (-9.0 + k * 6.0, -2.6, 2.97), (1.2, 0.30, 0.04), (0.96, 0.96, 0.92, 1.0))
    make_box("Platform", (0.0, -2.6, 0.08), (30.0, 5.4, 0.16), CONCRETE)
    make_box("Platform_Curb", (0.0, -5.35, 0.08), (30.0, 0.10, 0.16), (0.92, 0.80, 0.30, 1.0))
    for k in range(15):
        make_box(f"Platform_Seam_{k}", (-14.0 + k * 2.0, -2.6, 0.161), (0.02, 5.4, 0.002), (0.56, 0.54, 0.50, 1.0))
    make_cyl("Trash_Can", (4.5, -0.8, 0.56), 0.26, 0.80, (0.30, 0.34, 0.30, 1.0), segments=12)
    make_cyl("Ash_Urn", (-3.2, -0.6, 0.56), 0.16, 0.80, STEEL, segments=12)
    make_box("Bus_Stop_Sign", (7.18, -4.9, 2.4), (0.04, 0.60, 0.80), (0.94, 0.94, 0.92, 1.0))
    make_box("Bus_Stop_Sign_Band", (7.15, -4.9, 2.56), (0.02, 0.56, 0.16), (0.20, 0.34, 0.60, 1.0))
    # the bay, the street, the city across
    make_box("Bay_Lane", (0.0, -8.5, -0.01), (40.0, 6.0, 0.02), ASPHALT)
    make_box("Street", (0.0, -16.0, -0.01), (80.0, 9.0, 0.02), ASPHALT)
    for k in range(10):
        make_box(f"Street_Line_{k}", (-36.0 + k * 8.0, -16.0, 0.002), (3.0, 0.12, 0.004), (0.94, 0.94, 0.90, 1.0))
    make_box("Far_Walk", (0.0, -22.0, 0.06), (80.0, 3.0, 0.12), CONCRETE)
    city_block("CityS", -40.0, 40.0, -23.5, -1, seed=2)
    for k in range(4):
        make_car(f"Street_Car_{k}", -20.0 + k * 12.0, -12.4 - (k % 2) * 7.2, 4.4, CITY[(k + 1) % len(CITY)], along="X")
    for k in range(3):
        make_box(f"Term_Wing_{k}", (-26.0 + k * 26.0, 22.0, 6.0), (10.0, 10.0, 12.0), CITY[k])


# ── the bus ───────────────────────────────────────────────────────────
BX, BY0, BL, BW = 61.3, 0.0, 11.0, 2.5


def build_bus():
    cx, cy = BX, BY0 + BL / 2.0
    hw = BW / 2.0
    make_box("Bus_Floor", (cx, cy, 0.40), (BW, BL, 0.08), (0.30, 0.30, 0.32, 1.0))
    make_box("Bus_Aisle_Strip", (cx, cy, 0.442), (0.60, BL - 0.4, 0.004), (0.24, 0.24, 0.26, 1.0))
    make_box("Bus_Ceil", (cx, cy, 2.70), (BW, BL, 0.08), (0.86, 0.86, 0.84, 1.0))
    make_box("Bus_End_Front", (cx, BY0 + BL + 0.04, 1.55), (BW, 0.08, 2.30), (0.40, 0.40, 0.42, 1.0))
    make_box("Bus_End_Back", (cx, BY0 - 0.04, 1.55), (BW, 0.08, 2.30), (0.70, 0.70, 0.68, 1.0))
    # the sides: low panel, the window band as frames (no glass), the upper panel
    for s in (-1, 1):
        x = cx + s * (hw + 0.04)
        if s > 0:        # the right side opens for the rear doors (y 5.1..6.5)
            for nm, (y0_, y1_) in (("A", (BY0, BY0 + 5.1)), ("B", (BY0 + 6.5, BY0 + BL))):
                make_box(f"Bus_Side_Low_{s:+d}_{nm}", (x, (y0_ + y1_) / 2.0, 0.80), (0.08, y1_ - y0_, 0.80), (0.82, 0.82, 0.80, 1.0))
        else:
            make_box(f"Bus_Side_Low_{s:+d}", (x, cy, 0.80), (0.08, BL, 0.80), (0.82, 0.82, 0.80, 1.0))
        make_box(f"Bus_Side_High_{s:+d}", (x, cy, 2.45), (0.08, BL, 0.50), (0.82, 0.82, 0.80, 1.0))
        for k in range(10):
            y = BY0 + 0.45 + k * 1.1
            if s > 0 and 5.0 < y < 6.6:        # the rear doors on the right
                continue
            make_box(f"Bus_Pillar_{s:+d}_{k}", (x, y, 1.80), (0.08, 0.12, 0.80), (0.24, 0.24, 0.26, 1.0))
    make_box("Bus_Rear_Door_Frame", (cx + hw + 0.04, BY0 + 5.8, 2.24), (0.08, 1.4, 0.08), (0.24, 0.24, 0.26, 1.0))
    for s in (-1, 1):
        make_box(f"Bus_Rear_Door_Leaf_{s:+d}", (cx + hw + 0.02, BY0 + 5.8 + s * 0.35, 1.30), (0.04, 0.66, 1.76), (0.36, 0.40, 0.44, 1.0))
    # seats in pairs both sides, facing the nose; poles and the rail
    for k in range(8):
        y = BY0 + 0.9 + k * 1.1
        for s in (-1, 1):
            if s > 0 and 4.9 < y < 6.8:
                continue
            for pos in (0, 1):      # 0 = aisle, 1 = window
                x = cx + s * (0.36 + pos * 0.44)
                make_chamfer_box(f"Bus_Seat_{k}_{s:+d}_{pos}_Cush", (x, y, 0.70), (0.42, 0.44, 0.10), (0.20, 0.30, 0.54, 1.0), chamfer=0.03)
                make_chamfer_box(f"Bus_Seat_{k}_{s:+d}_{pos}_Back", (x, y - 0.22, 1.02), (0.42, 0.08, 0.58), (0.20, 0.30, 0.54, 1.0), chamfer=0.03)
            make_box(f"Bus_Seat_{k}_{s:+d}_Frame", (cx + s * 0.58, y, 0.55), (0.80, 0.30, 0.22), (0.36, 0.36, 0.38, 1.0))
            make_box(f"Bus_Seat_{k}_{s:+d}_Grab", (cx + s * 0.36, y - 0.22, 1.36), (0.04, 0.04, 0.10), (0.84, 0.70, 0.20, 1.0))
    for k in range(5):
        y = BY0 + 1.4 + k * 2.2
        for s in (-1, 1):
            make_cyl(f"Bus_Pole_{k}_{s:+d}", (cx + s * 0.32, y, 1.56), 0.02, 2.22, (0.84, 0.70, 0.20, 1.0), segments=8)
    for s in (-1, 1):
        make_cyl(f"Bus_Rail_{s:+d}", (cx + s * 0.32, cy, 2.30), 0.016, BL - 0.4, (0.84, 0.70, 0.20, 1.0), axis='Y', segments=8)
    for k in range(4):
        make_box(f"Bus_Ceil_Light_{k}", (cx, BY0 + 1.6 + k * 2.6, 2.655), (0.30, 1.2, 0.02), (0.96, 0.96, 0.92, 1.0))
    make_box("Bus_Stop_Cord", (cx - hw + 0.005, cy, 2.22), (0.01, BL - 0.6, 0.01), (0.90, 0.88, 0.80, 1.0))
    # the city outside the windows, both sides
    make_box("Bus_Road", (cx, cy, 0.0), (40.0, 60.0, 0.02), ASPHALT)
    for side in (-1, 1):
        y = BY0 - 14.0
        k = 0
        while y < BY0 + 26.0:
            w = 7.0 + (k * 5 % 4) * 2.5
            h = 10.0 + (k * 3 % 5) * 7.0
            p = f"BusCity_Stock_{side:+d}_{k}"
            xx = cx + side * 13.0
            make_box(p + "_Mass", (xx, y + w / 2.0, h / 2.0), (12.0, w - 0.2, h), CITY[(k + (side > 0)) % len(CITY)])
            for f in range(int(h / 3.4)):
                make_box(p + f"_Band_{f}", (xx - side * 6.01, y + w / 2.0, 1.8 + f * 3.4), (0.02, w - 0.8, 1.4),
                         (0.26, 0.30, 0.36, 1.0))
            y += w
            k += 1


def main():
    clear_scene()
    build_station()
    build_bus()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/bus_station.glb"))
    print(f"\n[build_bus_station] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
