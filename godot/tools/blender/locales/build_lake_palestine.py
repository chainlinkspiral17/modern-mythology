"""lake_palestine — the north boat ramp, Sunday six-thirty in late May.
vol6 ch8 (The Boat Ramp), re-homed off louisiana_road (2026-09-03).

"Her father pulls into the lot near the north boat ramp." The dock:
"the same dock, she registers, that he is talking about, which is,
twelve years on, the same wood, very slightly more weathered, with
the same metal cleat at the far end where she had, at six, decided
cleats were boring and had returned to the Cheez-It box. They walk
to the end of the dock. They sit on the edge with their feet over
the water." Then: "The sun comes up over the trees on the eastern
shore. The light gets into the water. The water lights up. Two bass
boats — finally, at seven-fifteen — emerge from the launch on the
far side and begin their slow patient circuits along the cove."
"I brought sandwiches. They're in the cooler in the bed."

This is the chapter where Chief Miller tells Sam the accounting, so
the set is a long straight line: the truck in the lot, the dock
running south from the shore, the cleat at the far end, the far
shore across the cove with the sun behind it.

Coordinate frame: Blender Z-up. Shore line along y=0; the lake is
south (y<0), the lot north (y 3..22). The dock runs from the shore
at (0, 1) to the cleat at (0, -15.8). The ramp slab is west of the
dock at x=-8. Eastern shore treeline at x≈+30. glTF export remaps to
Godot (x, z, -y).

DRAFT 1 (2026-09-03): the lot with stripes, the honor-box fee kiosk,
the ramp sign, a light pole, bollards, the trash can; Miller's truck
with the cooler in the bed; the ramp slab running under the water;
the shore gravel + reeds; the dock (abutment, deck planks, rub
rail, pilings, the metal cleat with a rope coil), the lake in three
slabs around the ramp, two bass boats on the far side, the far
south shore, pines on both shores and behind the lot, far bands.
Draft 2 targets: the eastern-shore sun as a practical glint band
on the water, a Cheez-It box residue (no — memory, not object),
the launch ramp on the far side the boats emerge from, wake lines.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_blob, make_wedge, make_taper_cyl, make_lathe, export_glb
from _props.detail import make_far_bands
from _props.vehicles import make_car

ASPHALT = (0.32, 0.32, 0.33, 1.0)
CONCRETE = (0.62, 0.61, 0.58, 1.0)
GRAVEL = (0.56, 0.52, 0.44, 1.0)
WATER = (0.16, 0.30, 0.34, 0.85)
WATER_LIT = (0.30, 0.44, 0.44, 0.85)
DOCK_WOOD = (0.52, 0.46, 0.36, 1.0)
DOCK_WOOD_DK = (0.42, 0.37, 0.29, 1.0)
PILING = (0.34, 0.30, 0.24, 1.0)
STEEL = (0.62, 0.64, 0.66, 1.0)
RUBBER = (0.12, 0.12, 0.13, 1.0)
TRUCK_BLUE = (0.20, 0.26, 0.38, 1.0)
TRUCK_BLUE_DK = (0.14, 0.18, 0.28, 1.0)
GLASS = (0.55, 0.62, 0.70, 0.40)
PINE = (0.16, 0.26, 0.16, 1.0)
PINE_LT = (0.22, 0.32, 0.20, 1.0)
TRUNK = (0.34, 0.26, 0.18, 1.0)
REED = (0.42, 0.46, 0.26, 1.0)

DOCK_END_Y = -15.8


def build_ground_and_lot():
    make_box("Ground_Far", (0.0, 40.0, -0.12), (700.0, 700.0, 0.02), (0.30, 0.34, 0.22, 1.0))
    # the two shores of the cove: land at water level east of x=22 and west of x=-30
    make_box("East_Shore", (121.0, -100.0, -0.06), (198.0, 200.0, 0.08), (0.34, 0.36, 0.24, 1.0))
    make_box("West_Shore", (-125.0, -100.0, -0.06), (190.0, 200.0, 0.08), (0.34, 0.36, 0.24, 1.0))
    make_box("Lot_Asphalt", (0.0, 12.5, -0.03), (40.0, 19.0, 0.06), ASPHALT)
    make_box("Shore_Gravel", (0.0, 1.5, 0.03), (60.0, 3.0, 0.06), GRAVEL)
    # parking stripes, angled row facing the water
    for i in range(7):
        make_box(f"Lot_Stripe_{i}", (-12.0 + i * 3.0, 9.5, 0.002), (0.12, 5.0, 0.004), (0.84, 0.84, 0.80, 1.0))
    # the honor-box fee kiosk, the ramp sign, the light pole, bollards, the can
    make_cyl("Fee_Kiosk_Post", (8.0, 5.0, 0.6), 0.05, 1.2, STEEL, segments=8)
    make_box("Fee_Kiosk_Box", (8.0, 5.0, 1.42), (0.40, 0.22, 0.44), (0.30, 0.42, 0.32, 1.0))
    make_box("Fee_Kiosk_Slot", (8.0, 4.885, 1.50), (0.16, 0.002, 0.02), RUBBER)
    make_box("Fee_Kiosk_Envelopes", (8.0, 4.885, 1.32), (0.20, 0.002, 0.10), (0.86, 0.84, 0.76, 1.0))
    make_cyl("Ramp_Sign_Post", (-4.5, 4.2, 1.1), 0.04, 2.2, STEEL, segments=6)
    make_box("Ramp_Sign", (-4.5, 4.2, 2.35), (0.60, 0.03, 0.40), (0.42, 0.28, 0.12, 1.0))
    make_box("Ramp_Sign_Text", (-4.5, 4.18, 2.35), (0.50, 0.002, 0.10), (0.92, 0.90, 0.84, 1.0))
    make_cyl("Light_Pole", (12.0, 14.0, 4.0), 0.10, 8.0, (0.36, 0.36, 0.38, 1.0), segments=8)
    make_box("Light_Pole_Arm", (12.0, 13.4, 7.9), (0.10, 1.2, 0.10), (0.36, 0.36, 0.38, 1.0))
    make_box("Light_Pole_Head", (12.0, 12.8, 7.8), (0.40, 0.50, 0.16), (0.90, 0.90, 0.84, 1.0))
    for bi, bx in enumerate((-11.0, -5.0)):
        make_cyl(f"Bollard_{bi}", (bx, 3.6, 0.48), 0.10, 0.96, (0.80, 0.72, 0.20, 1.0), segments=8)
    make_cyl("Trash_Can", (5.5, 3.6, 0.48), 0.30, 0.96, (0.24, 0.30, 0.26, 1.0), segments=12)
    make_cyl("Trash_Can_Lid", (5.5, 3.6, 0.99), 0.32, 0.06, (0.18, 0.22, 0.20, 1.0), segments=12)
    # the ramp slab: level with the lot at y=3, running under the water by y=-6
    make_wedge("Ramp_Slab", (-8.0, -1.5, -0.25), (5.0, 9.0, 0.5), CONCRETE, high_end="+Y")


def build_truck():
    """Chief Miller's truck, nose to the water, the cooler in the bed."""
    tx, ty = -3.5, 10.0
    # nose to the water (-Y): make_car's nose is +axis, so the truck is
    # laid along Y and the frame flipped by placing it as a -Y facer:
    # we build it along "Y" and let the cooler sit in the bed at the
    # +Y (tail) end, which is the end away from the water.
    make_car("Truck", tx, ty, 5.6, TRUCK_BLUE, pickup=True, along="Y", z0=0.0)
    make_box("Truck_Light_Bar", (tx, ty - 0.6, 1.76), (1.20, 0.30, 0.10), (0.20, 0.20, 0.22, 1.0))
    # the cooler in the bed, a tackle box beside it, the sandwiches inside
    make_box("Truck_Cooler_Body", (tx + 0.30, ty - 1.9, 1.20), (0.55, 0.38, 0.40), (0.86, 0.86, 0.84, 1.0))
    make_box("Truck_Cooler_Lid", (tx + 0.30, ty - 1.9, 1.425), (0.57, 0.40, 0.05), (0.70, 0.20, 0.16, 1.0))
    make_box("Truck_Tackle_Box", (tx - 0.40, ty - 2.1, 1.12), (0.40, 0.22, 0.24), (0.30, 0.34, 0.30, 1.0))


def build_dock():
    """Sixteen meters of weathered planks on pilings, the rub rail, the
    metal cleat at the far end with its rope."""
    make_box("Dock_Abutment", (0.0, 0.5, 0.28), (2.2, 1.0, 0.44), CONCRETE)
    n_planks = 56
    for i in range(n_planks):
        y = 0.85 - i * 0.30
        shade = 1.0 if i % 3 else 0.86
        c = (DOCK_WOOD[0] * shade, DOCK_WOOD[1] * shade, DOCK_WOOD[2] * shade, 1.0)
        make_box(f"Dock_Plank_{i}", (0.0, y, 0.53), (2.0, 0.27, 0.06), c)
    # stringers under the planks, pilings standing on the water
    for sgn, nm in ((1, "E"), (-1, "W")):
        make_box(f"Dock_Stringer_{nm}", (sgn * 0.85, -7.925, 0.42), (0.10, 15.85, 0.16), DOCK_WOOD_DK)
        for pi in range(6):
            py = -0.5 - pi * 3.0
            make_lathe(f"Dock_Piling_{nm}_{pi}", (sgn * 1.05, py, -0.02), [(0.13, 0.0), (0.12, 0.30), (0.11, 0.46), (0.09, 0.52), (0.0, 0.52)], PILING, segments=8)
        make_box(f"Dock_Rub_Rail_{nm}", (sgn * 1.03, -7.925, 0.59), (0.06, 15.85, 0.06), DOCK_WOOD_DK)
    make_box("Dock_End_Plank", (0.0, DOCK_END_Y - 0.15, 0.53), (2.0, 0.30, 0.06), DOCK_WOOD_DK)
    # the same metal cleat at the far end, twelve years on
    cx, cy = 0.55, DOCK_END_Y - 0.05
    make_box("Dock_Cleat_Base", (cx, cy, 0.5765), (0.16, 0.08, 0.03), STEEL)
    make_cyl("Dock_Cleat_Stem", (cx, cy, 0.6215), 0.025, 0.06, STEEL, segments=8)
    make_cyl("Dock_Cleat_Horn", (cx, cy, 0.6715), 0.02, 0.24, STEEL, axis="X", segments=8)
    make_cyl("Dock_Cleat_Rope", (cx, cy - 0.16, 0.575), 0.09, 0.03, (0.74, 0.66, 0.48, 1.0), segments=10)
    make_box("Dock_Cleat_Rust", (cx, cy, 0.5605), (0.26, 0.20, 0.001), (0.44, 0.30, 0.20, 1.0))
    # worn patch where people sit at the end, feet over the water
    make_box("Dock_Sit_Wear", (-0.30, DOCK_END_Y + 0.35, 0.5605), (0.90, 0.50, 0.001), (0.58, 0.53, 0.44, 1.0))


def build_lake():
    """The water in three slabs around the ramp so the slab can run
    under it; the far south shore; two bass boats far off."""
    make_box("Lake_Water_W", (-20.5, -100.0, -0.06), (19.0, 200.0, 0.08), WATER)
    make_box("Lake_Water_S", (-8.0, -103.0, -0.06), (6.0, 194.0, 0.08), WATER)
    make_box("Lake_Water_E", (8.5, -100.0, -0.06), (27.0, 200.0, 0.08), WATER)
    # the light gets into the water: a lit band toward the eastern shore
    make_box("Lake_Glint_Band", (12.0, -40.0, -0.019), (18.0, 60.0, 0.002), WATER_LIT)
    # shore reeds
    for i, (x, r, s) in enumerate(((-16.0, 0.9, 1), (-13.5, 0.7, 2), (4.0, 0.8, 3), (7.5, 1.0, 4), (11.0, 0.7, 5), (16.0, 0.9, 6))):
        make_blob(f"Reeds_{i}", (x, -1.2, 0.80), r, REED, noise=0.3, seed=s, squash=0.6)
    # two bass boats emerging from the launch on the far side
    for bi, (bx, by) in enumerate(((12.0, -60.0), (-14.0, -75.0))):
        make_box(f"Bass_Boat_{bi}_Hull", (bx, by, 0.24), (2.0, 5.0, 0.52), (0.84, 0.86, 0.86, 1.0))
        make_box(f"Bass_Boat_{bi}_Console", (bx, by + 0.4, 0.75), (0.7, 0.8, 0.50), (0.30, 0.34, 0.40, 1.0))
        make_box(f"Bass_Boat_{bi}_Motor", (bx, by - 2.7, 0.45), (0.4, 0.4, 0.70), (0.16, 0.16, 0.18, 1.0))
    # the far south shore across the cove
    make_box("Far_Shore_S", (0.0, -260.0, 4.0), (400.0, 30.0, 8.0), (0.18, 0.24, 0.16, 1.0))
    make_box("Far_Shore_S_Bank", (0.0, -242.0, 0.4), (400.0, 4.0, 0.8), (0.50, 0.46, 0.38, 1.0))


def make_pine(prefix, x, y, z0, h=8.0, seed=0):
    """Trunk + three stacked cones, touching, never overlapping."""
    make_taper_cyl(f"{prefix}_Trunk", (x, y, z0 + h * 0.15), 0.24, 0.14, h * 0.30, TRUNK, segments=6)
    tiers = ((0.30, 0.30, 1.9), (0.60, 0.25, 1.4), (0.85, 0.15, 0.9))
    for ti, (base, span, r) in enumerate(tiers):
        make_taper_cyl(f"{prefix}_Cone_{ti}", (x, y, z0 + h * (base + span / 2.0)), r * (h / 8.0), 0.0,
                       h * span, PINE if ti % 2 == 0 else PINE_LT, segments=7)


def build_pines():
    # the eastern shore the sun comes up over, the western point, the trees behind the lot
    east = ((25.0, -3.0, 9.0), (29.0, -9.0, 11.0), (34.0, -4.0, 8.5), (38.0, -14.0, 10.0), (42.0, -2.0, 9.5),
            (46.0, -20.0, 11.5), (50.0, -8.0, 9.0), (54.0, -28.0, 10.5), (33.0, -22.0, 9.5))
    west = ((-33.0, -2.0, 9.5), (-37.0, -9.0, 8.5), (-41.0, -4.0, 10.0), (-45.0, -16.0, 9.0), (-38.0, -24.0, 11.0))
    north = ((-16.0, 26.0, 10.0), (-8.0, 27.5, 9.0), (0.0, 26.5, 11.0), (8.0, 28.0, 9.5), (16.0, 26.0, 10.5), (22.0, 24.0, 9.0))
    for gi, group in enumerate((east, west, north)):
        for pi, (x, y, h) in enumerate(group):
            make_pine(f"Pine_{gi}_{pi}", x, y, (-0.11 if gi == 2 else -0.02), h=h, seed=pi)


def build_horizon():
    make_far_bands("FarPines", (0.16, 0.24, 0.16),
                   [(70.0, 100.0, 12.0, 0.90), (140.0, 160.0, 14.0, 0.72),
                    (280.0, 280.0, 16.0, 0.55), (520.0, 440.0, 18.0, 0.42)],
                   sides="NEW", cx=0.0, cy=10.0, profile="ridge")


def main():
    clear_scene()
    build_ground_and_lot()
    build_truck()
    build_dock()
    build_lake()
    build_pines()
    build_horizon()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/lake_palestine.glb"))
    print(f"\n[build_lake_palestine] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
