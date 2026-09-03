"""vehicle_cab — the inside of a parked vehicle, and the gravel turnout
it is parked in. vol6's car scenes, re-homed off louisiana_road
(2026-09-03).

The volume keeps putting two people in a parked car and letting them
say the thing they cannot say indoors: "Ben, in the driver's seat,
does not start the engine" (ch5, Eight Minutes — four of them in the
truck, the safe-deposit box, the fake wrist brace); Maya "in the dark
of the passenger seat" (ch5, 1776 kHz); BT and Diego eating El Rancho
in the lay-by — "a small gravel turnout the city has, at some point in
the past, paved over with a single picnic table that nobody uses" —
the flauta box open on the center console, the green-sauce packets,
the El Diablito packet leaking under BT's thigh (ch16); Jesse in the
Civic in the lot after the DJ (ch20); Claire in the white sedan "at
the gravel turnout past the last named road" (ch4, ch6). Those were
all rendered from the shoulder of a highway. This is the cab.

One cab stands for every vehicle: Ben's crew-cab pickup is the
model, because it is the volume's spine (Ben drives everyone home).
The camera sits at the center console looking forward over the dash
through the windshield, so the exterior color is mostly a hood and
the interior — dash, wheel, cradle, radio, console, the two front
seats — is what the frame is made of. Claire's white sedan is parked
further along the turnout and reads through the driver's window.

Coordinate frame: Blender Z-up. The truck sits at the origin facing
+Y (north); the two-lane road runs east-west across the top of the
windshield at y≈9.5, the turnout is the gravel south of it, the
picnic table east of the truck, the sedan west. glTF export remaps to
Godot (x, z, -y): the cab preset at godot (0, 1.28, -0.10) with zero
yaw looks straight up blender +Y, over the hood, at the road.

DRAFT 1 (2026-09-03): hollow crew cab (pan, floor, doors, glass,
pillars, roof, windshield, rear glass), dash with cluster + radio
head + phone in its cradle, wheel + column + key, two front buckets
and the console between them with the El Rancho spread (flauta tray,
guac cup, sauce packets, the foil ball, the fountain cup in the
holder, the leaking El Diablito on the driver's seat), the rear
bench, dome light + rearview + visors, the truck exterior (hood
block, fenders, grille, bumpers, bed + toolbox + cooler, tailgate,
wheels), the gravel turnout, the paved pad with the picnic table and
its barrel, the white sedan, the two-lane road with its shoulders and
a mile marker, cedar scrub, treeline far bands.
Draft 2 targets: headlight cones + dash-glow practical variants per
scene (the night preset), a second cab preset from the rear bench
(ch5's four-up), rain on the windshield for ch4_storm, a
Civic-shaped hatch variant behind the sedan for Jesse's scenes.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_blob, make_wedge, export_glb
from _props.detail import make_far_bands

GRAVEL = (0.56, 0.52, 0.44, 1.0)
ASPHALT = (0.30, 0.30, 0.32, 1.0)
CONCRETE = (0.62, 0.61, 0.58, 1.0)
TRUCK_GREEN = (0.22, 0.34, 0.24, 1.0)
TRUCK_GREEN_DK = (0.16, 0.26, 0.18, 1.0)
GLASS = (0.55, 0.62, 0.70, 0.35)
CHROME = (0.72, 0.74, 0.76, 1.0)
RUBBER = (0.12, 0.12, 0.13, 1.0)
DASH = (0.20, 0.19, 0.18, 1.0)
DASH_LT = (0.28, 0.27, 0.25, 1.0)
SEAT = (0.40, 0.36, 0.30, 1.0)
SEAT_DK = (0.32, 0.29, 0.24, 1.0)
HEADLINER = (0.66, 0.64, 0.58, 1.0)
SCREEN = (0.55, 0.72, 0.90, 1.0)
FOIL = (0.80, 0.82, 0.84, 1.0)
SAUCE_GREEN = (0.46, 0.66, 0.30, 1.0)
SAUCE_RED = (0.62, 0.16, 0.10, 1.0)
CARD = (0.86, 0.78, 0.60, 1.0)
WOOD = (0.50, 0.40, 0.28, 1.0)

# cab envelope (blender): floor top z 0.46, belt line z 1.20, roof z 1.72
Z_FLOOR = 0.46
Z_BELT = 1.20
Z_ROOF = 1.72


def build_ground():
    make_box("Ground_Far", (0.0, 0.0, -0.07), (700.0, 700.0, 0.02), (0.30, 0.34, 0.22, 1.0))
    # the turnout: gravel south of the road, the road east-west
    make_box("Gravel_Turnout", (0.0, -1.0, -0.02), (26.0, 12.0, 0.04), GRAVEL)
    make_box("Turnout_Ruts", (-2.0, 0.0, 0.0005), (14.0, 0.6, 0.001), (0.50, 0.46, 0.38, 1.0))
    make_box("Road_Shoulder_S", (0.0, 5.5, -0.025), (300.0, 1.0, 0.05), (0.50, 0.47, 0.40, 1.0))
    make_box("Road_Asphalt", (0.0, 9.5, -0.03), (300.0, 7.0, 0.06), ASPHALT)
    make_box("Road_Shoulder_N", (0.0, 13.5, -0.025), (300.0, 1.0, 0.05), (0.50, 0.47, 0.40, 1.0))
    make_box("Road_Ditch_N", (0.0, 15.0, -0.045), (300.0, 2.0, 0.03), (0.26, 0.30, 0.18, 1.0))
    for i in range(30):
        make_box(f"Road_Center_Dash_{i}", (-72.5 + i * 5.0, 9.5, 0.002), (2.4, 0.12, 0.004), (0.82, 0.80, 0.60, 1.0))
    make_box("Road_Edge_Line_S", (0.0, 6.15, 0.002), (300.0, 0.10, 0.004), (0.86, 0.86, 0.84, 1.0))
    make_box("Road_Edge_Line_N", (0.0, 12.85, 0.002), (300.0, 0.10, 0.004), (0.86, 0.86, 0.84, 1.0))
    # mile marker on the far shoulder
    make_cyl("Mile_Marker_Post", (3.5, 13.8, 0.9), 0.04, 1.8, (0.40, 0.42, 0.40, 1.0), segments=6)
    make_box("Mile_Marker_Sign", (3.5, 13.8, 1.75), (0.22, 0.02, 0.36), (0.16, 0.42, 0.24, 1.0))
    # a fence line along the far ditch
    for i in range(14):
        make_cyl(f"Fence_Post_{i}", (-39.0 + i * 6.0, 16.5, 0.6), 0.05, 1.2, (0.36, 0.30, 0.22, 1.0), segments=6)
    make_box("Fence_Wire_Top", (0.0, 16.5, 1.12), (80.0, 0.01, 0.01), (0.50, 0.50, 0.48, 1.0))
    make_box("Fence_Wire_Mid", (0.0, 16.5, 0.72), (80.0, 0.01, 0.01), (0.50, 0.50, 0.48, 1.0))


def build_truck_exterior():
    """Ben's crew-cab pickup — green, a bed with a toolbox and the
    cooler. Skins are 25 mm plates OUTSIDE the cab shell (x ±0.90),
    wheels outside the skins (x ±0.94..1.20) so nothing intersects."""
    # underbody pan, the floor of the cab, the bed
    make_box("Truck_Pan", (0.0, -0.8, 0.35), (1.80, 5.60, 0.10), RUBBER)
    make_box("Cab_Floor", (0.0, 0.0, 0.43), (1.80, 3.10, 0.06), DASH)
    make_box("Truck_Bed_Floor", (0.0, -2.80, 0.49), (1.87, 2.40, 0.06), TRUCK_GREEN_DK)
    for sgn, nm in ((1, "R"), (-1, "L")):
        make_box(f"Truck_Bed_Side_{nm}", (sgn * 0.9175, -2.80, 0.795), (0.035, 2.40, 0.55), TRUCK_GREEN)
    make_box("Truck_Tailgate", (0.0, -4.025, 0.795), (1.80, 0.05, 0.55), TRUCK_GREEN)
    make_box("Truck_Rear_Bumper", (0.0, -4.11, 0.50), (2.00, 0.12, 0.16), CHROME)
    for sgn, nm in ((1, "R"), (-1, "L")):
        make_box(f"Truck_Taillight_{nm}", (sgn * 0.70, -4.06, 0.85), (0.22, 0.02, 0.14), (0.70, 0.12, 0.10, 1.0))
    # bed contents: the crossbed toolbox and the cooler with the sandwiches
    make_box("Truck_Toolbox", (0.0, -1.85, 0.73), (1.70, 0.45, 0.42), (0.74, 0.76, 0.78, 1.0))
    make_box("Truck_Toolbox_Lid_Lip", (0.0, -1.85, 0.955), (1.72, 0.47, 0.03), (0.66, 0.68, 0.70, 1.0))
    make_box("Cooler_Body", (0.35, -3.20, 0.72), (0.55, 0.38, 0.40), (0.86, 0.86, 0.84, 1.0))
    make_box("Cooler_Lid", (0.35, -3.20, 0.945), (0.57, 0.40, 0.05), (0.22, 0.34, 0.60, 1.0))
    make_cyl("Bed_Rope_Coil", (-0.45, -3.30, 0.56), 0.16, 0.08, (0.72, 0.64, 0.46, 1.0), segments=10)
    # hood block + slope, cowl, fenders, grille, bumper, lights
    make_box("Truck_Hood_Block", (0.0, 2.45, 0.74), (1.80, 1.70, 0.56), TRUCK_GREEN)
    make_wedge("Truck_Hood_Slope", (0.0, 2.45, 1.10), (1.80, 1.70, 0.20), TRUCK_GREEN, high_end="-Y")
    make_box("Truck_Cowl", (0.0, 1.575, 0.83), (1.86, 0.05, 0.74), TRUCK_GREEN)
    for sgn, nm in ((1, "R"), (-1, "L")):
        make_box(f"Truck_Fender_F_{nm}", (sgn * 0.9125, 2.45, 0.785), (0.025, 1.70, 0.55), TRUCK_GREEN)
        make_box(f"Truck_Mirror_Arm_{nm}", (sgn * 1.02, 1.30, 1.30), (0.20, 0.04, 0.04), RUBBER)
        make_box(f"Truck_Mirror_{nm}", (sgn * 1.16, 1.30, 1.30), (0.08, 0.14, 0.18), TRUCK_GREEN_DK)
    make_box("Truck_Grille", (0.0, 3.33, 0.75), (1.80, 0.06, 0.50), (0.22, 0.22, 0.24, 1.0))
    for sgn, nm in ((1, "R"), (-1, "L")):
        make_box(f"Truck_Headlight_{nm}", (sgn * 0.62, 3.37, 0.88), (0.34, 0.02, 0.18), (0.88, 0.88, 0.80, 1.0))
    make_box("Truck_Front_Bumper", (0.0, 3.43, 0.50), (2.00, 0.14, 0.18), CHROME)
    make_box("Truck_Plate", (0.0, 3.51, 0.50), (0.30, 0.01, 0.15), (0.88, 0.86, 0.80, 1.0))
    # wheels: outside the skins
    for wi, (wx, wy) in enumerate(((-1.07, 2.50), (1.07, 2.50), (-1.07, -2.60), (1.07, -2.60))):
        make_cyl(f"Truck_Wheel_{wi}", (wx, wy, 0.40), 0.40, 0.26, RUBBER, axis="X", segments=12)
        make_cyl(f"Truck_Hubcap_{wi}", (wx + (0.135 if wx > 0 else -0.135), wy, 0.40), 0.18, 0.01,
                 (0.60, 0.62, 0.64, 1.0), axis="X", segments=10)


def build_cab_shell():
    """Doors, pillars, glass, roof — the hollow the camera sits in."""
    for sgn, nm in ((1, "R"), (-1, "L")):
        x_skin = sgn * 0.9125
        x_glass = sgn * 0.915
        x_pillar = sgn * 0.91
        # door panels below the belt line, front and rear, the B pillar between
        make_box(f"Cab_Door_F_{nm}", (x_skin, 0.75, 0.83), (0.025, 1.30, 0.74), TRUCK_GREEN)
        make_box(f"Cab_Door_R_{nm}", (x_skin, -0.725, 0.83), (0.025, 1.35, 0.74), TRUCK_GREEN)
        make_box(f"Cab_Side_Cowl_{nm}", (x_skin, 1.475, 0.83), (0.025, 0.15, 0.74), TRUCK_GREEN)
        make_box(f"Cab_Side_Rear_{nm}", (x_skin, -1.475, 0.83), (0.025, 0.15, 0.74), TRUCK_GREEN)
        make_box(f"Cab_Pillar_A_{nm}", (x_pillar, 1.50, 1.46), (0.03, 0.10, 0.52), TRUCK_GREEN_DK)
        make_box(f"Cab_Pillar_B_{nm}", (x_pillar, 0.025, 1.46), (0.03, 0.15, 0.52), TRUCK_GREEN_DK)
        make_box(f"Cab_Pillar_C_{nm}", (x_pillar, -1.475, 1.46), (0.03, 0.15, 0.52), TRUCK_GREEN_DK)
        make_box(f"Cab_Glass_F_{nm}", (x_glass, 0.775, 1.46), (0.02, 1.25, 0.50), GLASS)
        make_box(f"Cab_Glass_R_{nm}", (x_glass, -0.75, 1.46), (0.02, 1.20, 0.50), GLASS)
        # interior door card + armrest + handle
        make_box(f"Cab_Door_Card_{nm}", (sgn * 0.885, 0.75, 0.83), (0.03, 1.28, 0.72), DASH_LT)
        make_box(f"Cab_Armrest_{nm}", (sgn * 0.82, 0.55, 0.98), (0.10, 0.50, 0.06), DASH)
        make_box(f"Cab_Door_Handle_{nm}", (sgn * 0.855, 1.05, 1.08), (0.03, 0.14, 0.03), CHROME)
    make_box("Cab_Windshield", (0.0, 1.565, 1.46), (1.76, 0.02, 0.50), GLASS)
    make_box("Cab_Windshield_Header", (0.0, 1.565, 1.71), (1.80, 0.03, 0.02), TRUCK_GREEN_DK)
    make_box("Cab_Rear_Glass", (0.0, -1.565, 1.46), (1.76, 0.02, 0.50), GLASS)
    make_box("Cab_Back_Wall", (0.0, -1.575, 0.83), (1.86, 0.05, 0.74), TRUCK_GREEN)
    make_box("Cab_Roof", (0.0, 0.0, 1.75), (1.86, 3.16, 0.06), TRUCK_GREEN)
    make_box("Cab_Headliner", (0.0, 0.0, 1.715), (1.76, 3.06, 0.01), HEADLINER)
    # dome light, rearview, visors
    make_box("Dome_Light", (0.0, -0.30, 1.70), (0.14, 0.10, 0.02), (0.96, 0.92, 0.80, 1.0))
    make_cyl("Rearview_Stalk", (0.0, 1.42, 1.66), 0.012, 0.09, RUBBER, segments=6)
    make_box("Rearview_Mirror", (0.0, 1.40, 1.58), (0.26, 0.05, 0.07), (0.30, 0.34, 0.38, 1.0))
    for sgn, nm in ((1, "R"), (-1, "L")):
        make_box(f"Sun_Visor_{nm}", (sgn * 0.47, 1.32, 1.695), (0.60, 0.30, 0.02), HEADLINER)


def build_dash():
    """Dash face + top, the cluster, the radio head, the vents, the
    phone in its dashboard cradle (BT presses play), the wheel."""
    make_box("Dash_Face", (0.0, 1.00, 0.77), (1.80, 0.10, 0.62), DASH)
    make_box("Dash_Top", (0.0, 1.25, 1.13), (1.80, 0.60, 0.10), DASH_LT)
    make_box("Dash_Defrost_Slot", (0.0, 1.45, 1.181), (1.30, 0.06, 0.002), RUBBER)
    # cluster behind the wheel
    make_box("Gauge_Cluster", (-0.46, 0.94, 0.98), (0.36, 0.02, 0.16), (0.10, 0.10, 0.11, 1.0))
    make_cyl("Gauge_Speedo", (-0.54, 0.928, 0.98), 0.055, 0.004, (0.80, 0.78, 0.70, 1.0), axis="Y", segments=12)
    make_cyl("Gauge_Tach", (-0.38, 0.928, 0.98), 0.055, 0.004, (0.80, 0.78, 0.70, 1.0), axis="Y", segments=12)
    # center stack: vents, the radio head with its dial, the climate knobs
    for vi, vx in enumerate((-0.16, 0.16)):
        make_box(f"Dash_Vent_{vi}", (vx, 0.94, 1.02), (0.14, 0.02, 0.06), (0.14, 0.14, 0.15, 1.0))
    make_box("Radio_Head", (0.0, 0.94, 0.90), (0.32, 0.02, 0.10), (0.12, 0.12, 0.13, 1.0))
    make_box("Radio_Display", (0.04, 0.928, 0.915), (0.14, 0.004, 0.03), (0.92, 0.62, 0.22, 1.0))
    make_cyl("Radio_Dial", (-0.11, 0.925, 0.90), 0.022, 0.014, CHROME, axis="Y", segments=10)
    make_cyl("Radio_Knob_Tune", (0.12, 0.925, 0.885), 0.012, 0.012, CHROME, axis="Y", segments=8)
    for ki, kx in enumerate((-0.10, 0.0, 0.10)):
        make_cyl(f"Climate_Knob_{ki}", (kx, 0.925, 0.76), 0.02, 0.014, DASH_LT, axis="Y", segments=8)
    make_box("Hazard_Button", (0.0, 0.928, 0.985), (0.03, 0.004, 0.02), (0.80, 0.18, 0.12, 1.0))
    # the phone in the dashboard cradle, screen lit
    make_box("Phone_Cradle", (0.22, 1.08, 1.25), (0.10, 0.03, 0.14), RUBBER)
    make_box("Phone_Cradle_Foot", (0.22, 1.08, 1.19), (0.06, 0.05, 0.02), RUBBER)
    make_box("Phone", (0.22, 1.058, 1.26), (0.076, 0.012, 0.152), (0.08, 0.08, 0.09, 1.0))
    make_box("Phone_Screen", (0.22, 1.0515, 1.26), (0.066, 0.001, 0.138), SCREEN)
    make_box("Phone_Play_Bar", (0.22, 1.0508, 1.21), (0.05, 0.0005, 0.012), (0.20, 0.24, 0.30, 1.0))
    # steering wheel, column, ignition key
    make_cyl("Steering_Column", (-0.46, 0.875, 0.98), 0.03, 0.15, DASH, axis="Y", segments=8)
    make_cyl("Steering_Wheel", (-0.46, 0.78, 0.98), 0.19, 0.03, (0.16, 0.15, 0.14, 1.0), axis="Y", segments=18)
    make_cyl("Steering_Hub", (-0.46, 0.79, 0.98), 0.07, 0.05, DASH, axis="Y", segments=10)
    make_box("Steering_Spoke_L", (-0.56, 0.78, 0.98), (0.10, 0.02, 0.03), DASH)
    make_box("Steering_Spoke_R", (-0.36, 0.78, 0.98), (0.10, 0.02, 0.03), DASH)
    make_box("Ignition_Key", (-0.34, 0.86, 0.94), (0.01, 0.05, 0.02), CHROME)
    make_box("Ignition_Fob", (-0.34, 0.83, 0.92), (0.02, 0.01, 0.03), (0.30, 0.28, 0.26, 1.0))
    # pedals, floor mats
    for pi, px in enumerate((-0.52, -0.40)):
        make_box(f"Pedal_{pi}", (px, 1.10, 0.56), (0.06, 0.02, 0.10), RUBBER)
    for sgn, nm in ((1, "R"), (-1, "L")):
        make_box(f"Floor_Mat_F_{nm}", (sgn * 0.46, 0.65, 0.463), (0.55, 0.60, 0.006), (0.15, 0.15, 0.15, 1.0))
        make_box(f"Floor_Mat_R_{nm}", (sgn * 0.46, -0.60, 0.463), (0.55, 0.50, 0.006), (0.15, 0.15, 0.15, 1.0))
    make_box("Glovebox_Door", (0.46, 0.945, 0.86), (0.50, 0.01, 0.26), DASH_LT)


def build_seats():
    """Two front buckets, the rear bench, and the console between the
    fronts — the console is where the El Rancho box opens."""
    for sgn, nm in ((-1, "Driver"), (1, "Passenger")):
        x = sgn * 0.46
        make_box(f"Seat_{nm}_Base", (x, 0.15, 0.67), (0.62, 0.55, 0.42), SEAT)
        make_box(f"Seat_{nm}_Back", (x, -0.18, 1.23), (0.62, 0.12, 0.70), SEAT)
        make_box(f"Seat_{nm}_Bolster", (x, 0.15, 0.905), (0.62, 0.55, 0.05), SEAT_DK)
        make_box(f"Seat_{nm}_Headrest", (x, -0.18, 1.645), (0.28, 0.10, 0.13), SEAT_DK)
        make_cyl(f"Seat_{nm}_Headrest_Post", (x, -0.18, 1.585), 0.008, 0.01, CHROME, segments=6)
        make_box(f"Seatbelt_Buckle_{nm}", (x - sgn * 0.26, 0.05, 0.955), (0.04, 0.10, 0.05), (0.14, 0.14, 0.15, 1.0))
    make_box("Rear_Bench_Base", (0.0, -0.90, 0.66), (1.70, 0.50, 0.40), SEAT)
    make_box("Rear_Bench_Back", (0.0, -1.21, 1.21), (1.70, 0.12, 0.70), SEAT)
    make_box("Rear_Bench_Bolster", (0.0, -0.90, 0.885), (1.70, 0.50, 0.05), SEAT_DK)
    # console
    make_box("Console", (0.0, 0.15, 0.61), (0.28, 0.70, 0.30), DASH)
    make_box("Console_Lid", (0.0, -0.10, 0.775), (0.26, 0.20, 0.03), DASH_LT)
    make_cyl("Cupholder_Ring", (0.0, 0.42, 0.765), 0.05, 0.01, DASH_LT, segments=12)
    make_cyl("Shifter_Boot", (0.0, 0.05, 0.775), 0.035, 0.03, RUBBER, segments=8)
    make_cyl("Shifter_Stalk", (0.0, 0.05, 0.86), 0.012, 0.14, CHROME, segments=6)
    make_cyl("Shifter_Knob", (0.0, 0.05, 0.945), 0.03, 0.03, (0.16, 0.15, 0.14, 1.0), segments=10)


def build_el_rancho():
    """The El Rancho spread. "He opens the box on the center console
    between them. The flautas are five rolled fried chicken cylinders
    with a small cup of guacamole in the corner of the box. He pours
    one of the green-sauce packets over the flautas." Later the
    dashboard accumulates the foil and three of the fourteen packets,
    and one El Diablito, dropped between BT's legs, ends up on the
    driver's seat under his thigh. "The packet leaks slowly."
    The fountain cup in the holder: "BT, in the driver's seat, looks
    at the cup." """
    bx, by, bz = 0.0, 0.25, 0.76   # tray bottom on the console top
    make_box("Flauta_Tray", (bx, by, bz + 0.004), (0.20, 0.14, 0.008), CARD)
    make_box("Flauta_Tray_Wall_S", (bx, by - 0.0675, bz + 0.024), (0.20, 0.005, 0.032), CARD)
    make_box("Flauta_Tray_Wall_N", (bx, by + 0.0675, bz + 0.024), (0.20, 0.005, 0.032), CARD)
    make_box("Flauta_Tray_Wall_W", (bx - 0.0975, by, bz + 0.024), (0.005, 0.13, 0.032), CARD)
    make_box("Flauta_Tray_Wall_E", (bx + 0.0975, by, bz + 0.024), (0.005, 0.13, 0.032), CARD)
    make_box("Flauta_Lid", (bx, by + 0.075, bz + 0.078), (0.20, 0.008, 0.14), CARD)
    for fi in range(5):
        make_cyl(f"Flauta_{fi}", (bx - 0.045 + fi * 0.0225, by - 0.015, bz + 0.02), 0.011, 0.11,
                 (0.72, 0.52, 0.26, 1.0), axis="Y", segments=8)
    make_box("Flauta_Sauce_Pour", (bx - 0.02, by - 0.01, bz + 0.0315), (0.10, 0.08, 0.002), SAUCE_GREEN)
    make_cyl("Guac_Cup", (bx + 0.075, by + 0.04, bz + 0.023), 0.02, 0.03, (0.94, 0.94, 0.92, 1.0), segments=10)
    make_cyl("Guac_Cup_Fill", (bx + 0.075, by + 0.04, bz + 0.0395), 0.018, 0.003, (0.46, 0.60, 0.26, 1.0), segments=10)
    # the fountain cup in the holder
    make_cyl("Cup", (0.0, 0.42, 0.855), 0.042, 0.17, (0.90, 0.30, 0.22, 1.0), segments=12)
    make_cyl("Cup_Lid", (0.0, 0.42, 0.945), 0.045, 0.012, (0.92, 0.92, 0.90, 1.0), segments=12)
    make_cyl("Cup_Straw", (0.012, 0.415, 1.02), 0.003, 0.14, (0.86, 0.86, 0.84, 1.0), segments=6)
    # the dash accumulates: foil, three packets
    make_blob("Foil_Ball", (-0.20, 1.20, 1.21), 0.03, FOIL, noise=0.3, seed=3, squash=0.9)
    make_box("Packet_Green_0", (0.02, 1.15, 1.182), (0.05, 0.032, 0.004), SAUCE_GREEN)
    make_box("Packet_Green_1", (0.09, 1.30, 1.182), (0.05, 0.032, 0.004), SAUCE_GREEN)
    make_box("Packet_Diablito_Dash", (-0.06, 1.34, 1.182), (0.05, 0.032, 0.004), SAUCE_RED)
    # the El Diablito on the driver's seat, leaking
    make_box("Packet_Leak", (-0.36, 0.30, 0.9305), (0.07, 0.055, 0.001), (0.40, 0.10, 0.07, 1.0))
    make_box("Packet_Diablito_Seat", (-0.36, 0.30, 0.9335), (0.05, 0.032, 0.005), SAUCE_RED)
    # the paper bag, folded, on the passenger floor
    make_box("El_Rancho_Bag", (0.52, 0.85, 0.53), (0.22, 0.14, 0.13), (0.72, 0.60, 0.42, 1.0))


def build_turnout_furniture():
    """The single picnic table nobody uses, on its paved pad, with a
    barrel; the white sedan further along the turnout."""
    px, py = 5.0, -3.5
    make_box("Picnic_Pad", (px, py, 0.03), (3.2, 2.8, 0.06), CONCRETE)
    make_box("Picnic_Table_Top", (px, py, 0.785), (1.80, 0.72, 0.05), WOOD)
    for sgn, nm in ((1, "N"), (-1, "S")):
        make_box(f"Picnic_Bench_{nm}", (px, py + sgn * 0.60, 0.47), (1.80, 0.26, 0.04), WOOD)
    for sgn, nm in ((1, "E"), (-1, "W")):
        make_box(f"Picnic_Leg_{nm}", (px + sgn * 0.70, py, 0.41), (0.08, 1.40, 0.70), (0.44, 0.34, 0.24, 1.0))
    make_cyl("Trash_Barrel", (px + 1.9, py + 0.9, 0.45), 0.28, 0.90, (0.28, 0.30, 0.30, 1.0), segments=12)
    make_cyl("Trash_Barrel_Rim", (px + 1.9, py + 0.9, 0.915), 0.30, 0.03, (0.20, 0.22, 0.22, 1.0), segments=12)
    # Claire's white sedan, nose to the road, west of the truck
    sx, sy = -8.5, -2.5
    make_box("Sedan_Body", (sx, sy, 0.62), (1.70, 4.20, 0.60), (0.90, 0.90, 0.88, 1.0))
    make_box("Sedan_Cabin", (sx, sy - 0.3, 1.13), (1.50, 2.20, 0.42), (0.82, 0.83, 0.82, 1.0))
    make_box("Sedan_Windshield", (sx, sy + 0.815, 1.15), (1.30, 0.03, 0.30), (0.26, 0.30, 0.36, 1.0))
    for sgn, nm in ((1, "R"), (-1, "L")):
        make_box(f"Sedan_Side_Glass_{nm}", (sx + sgn * 0.765, sy - 0.3, 1.15), (0.03, 1.80, 0.30), (0.26, 0.30, 0.36, 1.0))
    for wi, (wx, wy) in enumerate(((sx - 0.975, sy - 1.4), (sx + 0.975, sy - 1.4), (sx - 0.975, sy + 1.4), (sx + 0.975, sy + 1.4))):
        make_cyl(f"Sedan_Wheel_{wi}", (wx, wy, 0.33), 0.33, 0.25, RUBBER, axis="X", segments=10)
    make_box("Sedan_Bumper_F", (sx, sy + 2.15, 0.50), (1.60, 0.10, 0.20), (0.80, 0.80, 0.78, 1.0))
    make_box("Sedan_Plate", (sx, sy + 2.205, 0.55), (0.30, 0.01, 0.15), (0.88, 0.86, 0.80, 1.0))


def build_scrub():
    """Cedar scrub across the road and behind the turnout."""
    for i, (x, y, r, s) in enumerate(((-14.0, 20.0, 2.2, 1), (-7.0, 21.5, 1.8, 2), (1.0, 19.5, 2.4, 3),
                                      (8.0, 22.0, 2.0, 4), (15.0, 20.5, 2.6, 5), (22.0, 21.0, 1.9, 6),
                                      (-10.0, -12.5, 2.0, 7), (0.5, -13.5, 2.4, 8), (11.0, -12.0, 1.8, 9),
                                      (-20.0, -11.0, 2.2, 10), (19.0, -13.0, 2.3, 11))):
        make_cyl(f"Scrub_{i}_Trunk", (x, y, 0.9), 0.14, 1.8, (0.30, 0.24, 0.18, 1.0), segments=6)
        make_blob(f"Scrub_{i}_Crown", (x, y, 1.8 + r * 0.8), r, (0.24, 0.32, 0.20, 1.0), noise=0.24, seed=s, squash=0.85)


def build_horizon():
    make_far_bands("FarTrees", (0.22, 0.28, 0.18),
                   [(60.0, 90.0, 7.0, 0.90), (120.0, 150.0, 9.0, 0.72),
                    (250.0, 260.0, 11.0, 0.55), (500.0, 420.0, 14.0, 0.42)],
                   cx=0.0, cy=0.0, profile="treeline")


def main():
    clear_scene()
    build_ground()
    build_truck_exterior()
    build_cab_shell()
    build_dash()
    build_seats()
    build_el_rancho()
    build_turnout_furniture()
    build_scrub()
    build_horizon()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/vehicle_cab.glb"))
    print(f"\n[build_vehicle_cab] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
