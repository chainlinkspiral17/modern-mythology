"""nexcorp_fueling_station — the NexCorp fueling station off FM-3411 (vol6 ch6:
vol6_ch6_fueling_station "Vince Walks", vol6_ch6_tome "Three Hundred in
Twenties", vol6_ch6_boyd "Nine Minutes").

DRAFT 2 (2026-10-10). Draft 1 was an auto-generated 8 x 6 m store interior,
and every one of the three chapters plays mostly OUTSIDE it:

  "The unmarked van is at pump six. The driver — Vince Kane ... is leaning
  against the driver's door, smoking ... Claire pulls up at the far pump ...
  [Vince] crosses the lot, gets into a beat-up sedan parked near the
  dumpster" · "In the back of the van, on the floor, wrapped in a blanket,
  Diego Ramos opens his eyes." · "Claire is at the counter, paying for a
  Diet Coke and a bag of pretzels, when Tomé's car pulls into the lot. She
  watches it through the front window ... a silver compact rental with a
  yellow air freshener visible through the windshield ... She crosses the
  lot." · "Boyd is ... leaning his forehead against the cool tile of the
  bathroom wall ... buys a Gatorade ... stumbles back to pump six" · "at
  07:43 on a Friday morning at a NexCorp fueling station off FM-3411".

So the set is the whole station, and it serves four presets:
  · nexcorp_fueling_station — THE FORECOURT: the navy-banded canopy over
    four islands (pumps 1-8), the unmarked white van at pump six, Claire's
    car at the far pump; the lot: Tomé's silver rental in a stall before
    the store, the dumpster and Vince's beat-up sedan beside it; the ice
    chest and propane cage at the store front; the pylon on FM-3411; the
    flat Texas fields.
  · nexcorp_fueling_store — THE STORE: the counter by the front window
    (register, cigarettes and lottery behind it), three gondolas, the
    cooler doors on the back wall, the coffee counter.
  · nexcorp_fueling_restroom — THE MEN'S ROOM off the back wall: the tile,
    the urinal, the sink and mirror, the hand dryer, the closed stall.
  · nexcorp_van_cargo — THE VAN'S CARGO BAY: the bare floor, the tie-down
    rails, the grey moving blanket on the floor, the jug, the open cab
    beyond with the station through the windshield.

Coordinate frame: Blender Z-up. The store's front (S) wall at y=0, the store
to y=12, the men's room behind it to y=15.6; the forecourt S of the store
(canopy y -6..-22), FM-3411 at y=-36. glTF export remaps to Godot (x, z, -y).

Draft 3 targets: the van's numbers off its plates; the oil stains under each
pump; the store's window posters and the NexCorp loyalty decals; the
restroom's graffiti; Boyd's Gatorade on the counter.
"""
import math
import os
import random
import sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_rot_box, export_glb
from _props.structure import make_floor, make_wall, make_wall_with_openings, make_ceiling, make_window
from _props.safety import make_fluorescent_tube_fixture
from _props.merch import stock_gondola
from _props.coolers_drinks import make_cooler_door
from _props.vehicles import make_car

SX0, SX1 = -8.0, 8.0            # the store
SY1 = 12.0
SCEIL = 3.2
RX0, RX1, RY1 = 4.6, 8.0, 15.6  # the men's room behind the store's NE
RCEIL = 3.0
ISLANDS = (-11.0, -4.0, 3.0, 10.0)
PUMP_Y = (-11.5, -16.5)
CANOPY_Z = 5.0

COL_NAVY = (0.18, 0.32, 0.50, 1.0)
COL_WHITE = (0.92, 0.92, 0.90, 1.0)
COL_CONCRETE = (0.70, 0.69, 0.66, 1.0)
COL_ASPHALT = (0.28, 0.28, 0.29, 1.0)
COL_STRIPE = (0.92, 0.92, 0.86, 1.0)
COL_DARK = (0.16, 0.16, 0.18, 1.0)
COL_STEEL = (0.66, 0.68, 0.70, 1.0)
COL_GLASS = (0.70, 0.78, 0.82, 0.30)
COL_FIELD = (0.62, 0.58, 0.36, 1.0)       # late-summer Texas grass
COL_TILE = (0.88, 0.90, 0.88, 1.0)
COL_TILE_BAND = (0.30, 0.44, 0.56, 1.0)


# ══════════════════════════════════════════════════════════════ the ground
def build_ground():
    make_box("Lot_Asphalt", (0.0, -8.0, -0.03), (60.0, 52.0, 0.06), COL_ASPHALT)
    make_box("Field_Ground", (0.0, -10.0, -0.07), (400.0, 300.0, 0.06), COL_FIELD)
    make_box("Store_Apron", (0.0, -1.0, 0.04), (SX1 - SX0 + 2.0, 2.0, 0.08), COL_CONCRETE)   # the sidewalk at the front
    make_box("Road_FM3411", (0.0, -36.0, -0.025), (400.0, 8.0, 0.05), (0.24, 0.24, 0.25, 1.0))
    make_box("Road_FM3411_Centerline", (0.0, -36.0, 0.004), (400.0, 0.12, 0.01), (0.92, 0.80, 0.20, 1.0))
    for e in (-1, 1):
        make_box(f"Road_FM3411_Edgeline_{e:+d}", (0.0, -36.0 + e * 3.7, 0.004), (400.0, 0.10, 0.01), COL_STRIPE)
    # the stalls in front of the store
    for k, sx in enumerate((-7.0, -4.3, 4.3, 7.0, 9.7)):
        make_box(f"Lot_Stall_Line_{k}", (sx - 1.35, -4.0, 0.004), (0.10, 4.6, 0.01), COL_STRIPE)
    make_box("Lot_Stall_Line_End", (11.05, -4.0, 0.004), (0.10, 4.6, 0.01), COL_STRIPE)
    # telephone poles and fence along the road, the flat fields
    for k in range(9):
        make_cyl(f"Road_Utility_Pole_{k}", (-60.0 + k * 15.0, -41.5, 4.5), 0.14, 9.0, (0.40, 0.32, 0.24, 1.0), segments=6)
        make_box(f"Road_Utility_Pole_{k}_Crossarm", (-60.0 + k * 15.0, -41.5, 8.6), (1.6, 0.12, 0.12), (0.40, 0.32, 0.24, 1.0))
    for k in range(5):
        make_box(f"Field_Barn_{k}", (-120.0 + k * 60.0, -110.0 - (k % 2) * 30.0, 3.0), (10.0, 8.0, 6.0), (0.56, 0.30, 0.24, 1.0) if k % 2 else (0.62, 0.62, 0.60, 1.0))


# ══════════════════════════════════════════════════════════════ the forecourt
def build_forecourt():
    cy = (PUMP_Y[0] + PUMP_Y[1]) / 2.0
    # the canopy: deck, fascia with its navy band, the columns, the light panels
    make_box("Canopy_Deck", (0.5, cy, CANOPY_Z + 0.35), (30.0, 14.0, 0.70), COL_WHITE)
    for e, fy in ((-1, cy - 7.02), (1, cy + 7.02)):
        make_box(f"Canopy_Fascia_Band_{e:+d}", (0.5, fy, CANOPY_Z + 0.40), (30.0, 0.04, 0.40), COL_NAVY)
        make_box(f"Canopy_Fascia_Stripe_{e:+d}", (0.5, fy + e * 0.003, CANOPY_Z + 0.16), (30.0, 0.04, 0.06), COL_WHITE)
    for e, fx in ((-1, 0.5 - 15.02), (1, 0.5 + 15.02)):
        make_box(f"Canopy_Fascia_Band_X{e:+d}", (fx, cy, CANOPY_Z + 0.40), (0.04, 14.0, 0.40), COL_NAVY)
    make_box("Canopy_Logo", (0.5, cy - 7.05, CANOPY_Z + 0.42), (3.4, 0.02, 0.30), COL_WHITE)
    for k, ix in enumerate(ISLANDS):
        make_cyl(f"Canopy_Column_{k}", (ix, cy, (0.16 + CANOPY_Z) / 2.0), 0.24, CANOPY_Z - 0.16, COL_WHITE, segments=12)
        for j, ly in enumerate((cy - 4.0, cy, cy + 4.0)):
            make_box(f"Canopy_Light_{k}_{j}", (ix + 3.5, ly, CANOPY_Z - 0.01), (1.2, 0.6, 0.02), (0.98, 0.98, 0.94, 1.0))
    # the islands and the dispensers, numbered 1-8
    n = 0
    for k, ix in enumerate(ISLANDS):
        make_box(f"Island_{k}_Curb", (ix, cy, 0.08), (1.20, 9.0, 0.16), COL_CONCRETE)
        for e in (-1, 1):
            make_cyl(f"Island_{k}_Bollard_{e:+d}", (ix, cy + e * 4.2, 0.16 + 0.45), 0.10, 0.90, (0.94, 0.80, 0.20, 1.0), segments=8)
        for d, py in enumerate(PUMP_Y):
            n += 1
            make_box(f"Pump_{n}_Body", (ix, py, 0.16 + 0.90), (0.70, 1.20, 1.80), COL_WHITE)
            make_box(f"Pump_{n}_Band", (ix, py, 0.16 + 1.62), (0.72, 1.22, 0.30), COL_NAVY)
            for s in (-1, 1):
                make_box(f"Pump_{n}_Display_{s:+d}", (ix + s * 0.352, py, 0.16 + 1.20), (0.004, 0.50, 0.30), (0.12, 0.14, 0.16, 1.0))
                make_box(f"Pump_{n}_Number_{s:+d}", (ix + s * 0.356, py, 0.16 + 1.62), (0.004, 0.24, 0.20), COL_WHITE)
                make_box(f"Pump_{n}_Nozzle_{s:+d}", (ix + s * 0.39, py + 0.40, 0.16 + 0.95), (0.08, 0.06, 0.24), COL_DARK)
                make_cyl(f"Pump_{n}_Hose_{s:+d}", (ix + s * 0.38, py + 0.45, 0.16 + 0.55), 0.02, 0.80, COL_DARK, segments=6)
        make_box(f"Island_{k}_Squeegee_Bin", (ix, cy + 1.2, 0.16 + 0.40), (0.40, 0.40, 0.80), (0.20, 0.36, 0.30, 1.0))
    # Doyle's NAPD courtesy badge, set down open on the bin lid at pump six
    make_box("Courtesy_Badge_Wallet", (ISLANDS[2] - 0.05, cy + 1.2, 0.16 + 0.80 + 0.004), (0.11, 0.08, 0.008), (0.30, 0.20, 0.14, 1.0))
    make_box("Courtesy_Badge_Shield", (ISLANDS[2] - 0.07, cy + 1.2, 0.16 + 0.80 + 0.0095), (0.035, 0.035, 0.003), (0.72, 0.60, 0.30, 1.0))
    # the pylon on FM-3411: NexCorp, the prices
    make_box("Pylon_Post", (16.0, -30.0, 2.8), (0.50, 0.30, 5.6), COL_STEEL)   # up to the price panel
    make_box("Pylon_Sign", (16.0, -30.0, 7.5), (2.6, 0.40, 1.40), COL_NAVY)
    make_box("Pylon_Sign_Logo", (16.0, -30.21, 7.6), (2.0, 0.004, 0.50), COL_WHITE)
    make_box("Pylon_Prices", (16.0, -30.0, 6.2), (2.6, 0.36, 1.20), (0.10, 0.10, 0.12, 1.0))
    for r in range(3):
        make_box(f"Pylon_Price_{r}", (16.0, -30.19, 5.85 + r * 0.34), (1.6, 0.004, 0.22), (0.96, 0.40, 0.20, 1.0))


def build_vehicles():
    # Claire's car at the far pump (pump 1, island 0, W lane)
    make_car("Claire_Car", ISLANDS[0] - 2.5, PUMP_Y[0] - 0.4, 4.7, (0.30, 0.34, 0.36, 1.0), along="Y")
    # Tomé's silver compact rental in the stall before the store, nose to the store
    tx, ty = 7.0 - 1.35 + 1.35, -3.6
    make_car("Tome_Car", tx, ty, 4.3, (0.78, 0.79, 0.80, 1.0), along="Y", hatch=True, glass_col=(0.56, 0.62, 0.68, 1.0))   # a rental's clean glass, the morning on it
    make_box("Tome_Car_Air_Freshener", (tx, ty + 0.85, 1.18), (0.07, 0.01, 0.10), (0.96, 0.86, 0.16, 1.0))
    make_box("Tome_Car_Air_Freshener_String", (tx, ty + 0.85, 1.30), (0.004, 0.004, 0.14), COL_DARK)
    # "She hands him three hundred-dollar bills": fanned on the roof over the driver's
    # door, where she leans in (the audits read a make_car as a solid box — no lens can
    # look inside one — so the insert's bills are on its skin)
    for k in range(3):
        make_rot_box(f"Cash_Bill_{k}", (tx - 0.40 + 0.03 * k, ty - 0.30 + 0.02 * k, 1.4705 + 0.0012 * k), (0.066, 0.156, 0.001), (0.62, 0.70, 0.56, 1.0), yaw=0.25 * k)
    # Vince's beat-up sedan by the dumpster (named for what it is: a cue for "closeup vince" would find it), the dumpster in its enclosure
    make_car("Getaway_Sedan", 12.4, 4.0, 4.8, (0.40, 0.34, 0.26, 1.0), along="Y")
    make_box("Dumpster_Body", (12.6, 9.6, 0.65), (1.90, 1.20, 1.30), (0.20, 0.36, 0.28, 1.0))
    make_rot_box("Dumpster_Lid", (12.6, 9.6, 1.33), (1.92, 1.22, 0.06), (0.16, 0.20, 0.18, 1.0), roll=0.05)
    for e in (-1, 1):
        make_box(f"Dumpster_Enclosure_Side_{e:+d}", (12.6 + e * 1.3, 10.0, 0.9), (0.10, 2.4, 1.8), (0.60, 0.56, 0.48, 1.0))
    make_box("Dumpster_Enclosure_Back", (12.6, 11.25, 0.9), (2.7, 0.10, 1.8), (0.60, 0.56, 0.48, 1.0))


def build_van():
    """The unmarked white van at pump six (island 2, S dispenser, W lane), nose
    north; its cargo bay built inside so the camera can sit in it."""
    vx, vy0, vy1 = ISLANDS[2] - 2.6, -18.70, -13.30     # rear and nose
    W, z0, zr = 1.96, 0.42, 2.24
    hw = W / 2.0
    cab = -14.95                                         # cargo bay | cab
    white = (0.92, 0.92, 0.90, 1.0)
    grey = (0.50, 0.50, 0.52, 1.0)
    # wheels
    for wy in (vy0 + 0.95, vy1 - 0.95):
        for s in (-1, 1):
            make_cyl(f"Van_Wheel_{wy:.1f}_{s:+d}", (vx + s * (hw - 0.10), wy, 0.38), 0.38, 0.24, COL_DARK, segments=14, axis='X')
    # the floor (the cargo bay's, raised over the axles) and the cab floor
    make_box("Van_Floor", (vx, (vy0 + cab) / 2.0, z0 + 0.10), (W - 0.08, cab - vy0, 0.06), (0.36, 0.36, 0.38, 1.0))
    make_box("Van_Cab_Floor", (vx, (cab + vy1 - 0.9) / 2.0, z0 + 0.06), (W - 0.08, vy1 - 0.9 - cab, 0.06), COL_DARK)
    make_box("Van_Underbody", (vx, (vy0 + vy1) / 2.0, z0 - 0.02), (W - 0.30, vy1 - vy0 - 0.4, 0.14), COL_DARK)
    # the sides: blank panels down the cargo bay; the cab doors with their windows
    for s in (-1, 1):
        make_box(f"Van_Body_Side_{s:+d}", (vx + s * (hw - 0.02), (vy0 + cab) / 2.0, (z0 + zr) / 2.0), (0.04, cab - vy0, zr - z0), white)
        make_box(f"Van_Door_Lower_{s:+d}", (vx + s * (hw - 0.02), (cab + vy1 - 0.9) / 2.0, z0 + 0.48), (0.04, vy1 - 0.9 - cab, 0.96), white)
        make_box(f"Van_Door_Glass_{s:+d}", (vx + s * (hw - 0.02), (cab + vy1 - 0.9) / 2.0, z0 + 1.38), (0.02, vy1 - 0.9 - cab - 0.16, 0.78), COL_GLASS)
        make_box(f"Van_Door_Pillar_{s:+d}", (vx + s * (hw - 0.02), vy1 - 0.96, z0 + 1.38), (0.05, 0.12, 0.80), white)
        make_box(f"Van_Door_Handle_{s:+d}", (vx + s * (hw + 0.005), cab + 0.30, z0 + 0.86), (0.02, 0.16, 0.04), COL_DARK)
        # the tie-down rails down the cargo walls
        for r, rz in enumerate((z0 + 0.55, z0 + 1.25)):
            make_box(f"Van_Rail_{s:+d}_{r}", (vx + s * (hw - 0.055), (vy0 + cab) / 2.0, rz), (0.03, cab - vy0 - 0.2, 0.05), COL_STEEL)
    make_box("Van_Roof", (vx, (vy0 + vy1 - 0.9) / 2.0, zr + 0.03), (W, vy1 - 0.9 - vy0, 0.06), white)
    make_box("Van_Headliner", (vx, (vy0 + cab) / 2.0, zr - 0.01), (W - 0.10, cab - vy0, 0.02), (0.70, 0.70, 0.68, 1.0))
    make_cyl("Van_Dome_Lamp", (vx, (vy0 + cab) / 2.0, zr - 0.04), 0.08, 0.04, (0.98, 0.94, 0.82, 1.0), segments=10)
    # the rear doors, shut, with their small windows
    for s in (-1, 1):
        make_box(f"Van_Rear_Door_{s:+d}", (vx + s * hw / 2.0, vy0 + 0.02, (z0 + zr) / 2.0 - 0.18), (hw - 0.01, 0.04, zr - z0 - 0.36), white)
        make_box(f"Van_Rear_Door_Glass_{s:+d}", (vx + s * hw / 2.0, vy0 + 0.02, zr - 0.20), (hw - 0.16, 0.02, 0.32), COL_GLASS)
        make_box(f"Van_Rear_Door_Frame_{s:+d}", (vx + s * (hw - 0.04), vy0 + 0.02, zr - 0.20), (0.08, 0.04, 0.36), white)
    make_box("Van_Rear_Door_Head", (vx, vy0 + 0.02, zr - 0.02), (W, 0.04, 0.04), white)
    make_box("Van_Rear_Bumper", (vx, vy0 - 0.06, z0 + 0.05), (W, 0.14, 0.16), COL_DARK)
    # the nose: hood, grille, the windshield, the dash, the two seats
    make_box("Van_Hood", (vx, vy1 - 0.45, z0 + 0.50), (W, 0.90, 1.00), white)
    make_box("Van_Grille", (vx, vy1 + 0.005, z0 + 0.45), (W - 0.40, 0.02, 0.40), COL_DARK)
    make_box("Van_Front_Bumper", (vx, vy1 + 0.06, z0 + 0.05), (W, 0.14, 0.16), COL_DARK)
    make_rot_box("Van_Windshield", (vx, vy1 - 0.70, z0 + 1.48), (W - 0.12, 0.02, 1.00), COL_GLASS, roll=0.42)
    for s in (-1, 1):
        make_rot_box(f"Van_A_Pillar_{s:+d}", (vx + s * (hw - 0.04), vy1 - 0.70, z0 + 1.48), (0.06, 0.06, 1.02), white, roll=0.42)
    make_box("Van_Dash", (vx, vy1 - 1.05, z0 + 0.82), (W - 0.10, 0.40, 0.30), COL_DARK)
    make_box("Van_Steering_Column", (vx - 0.45, vy1 - 1.22, z0 + 1.00), (0.06, 0.14, 0.06), COL_DARK)
    make_cyl("Van_Wheel_Steering", (vx - 0.45, vy1 - 1.30, z0 + 1.02), 0.19, 0.03, COL_DARK, segments=14, axis='Y')
    for s in (-1, 1):
        sx = vx + s * 0.45
        make_box(f"Van_Seat_{s:+d}_Base", (sx, cab + 0.55, z0 + 0.32), (0.52, 0.52, 0.40), grey)
        make_box(f"Van_Seat_{s:+d}_Cushion", (sx, cab + 0.55, z0 + 0.57), (0.52, 0.52, 0.10), grey)
        make_box(f"Van_Seat_{s:+d}_Back", (sx, cab + 0.27, z0 + 0.97), (0.52, 0.10, 0.70), grey)
    # in the cargo bay: the grey moving blanket on the floor, a water jug, a strap
    fz = z0 + 0.13
    make_rot_box("Van_Blanket", (vx - 0.25, -17.10, fz + 0.11), (0.62, 1.70, 0.22), (0.40, 0.42, 0.48, 1.0), yaw=0.06)
    make_rot_box("Van_Blanket_Fold", (vx - 0.20, -16.15, fz + 0.15), (0.56, 0.36, 0.30), (0.40, 0.42, 0.48, 1.0), yaw=-0.10)
    make_box("Van_Blanket_Stitch", (vx - 0.25, -17.10, fz + 0.221), (0.60, 1.60, 0.002), (0.30, 0.32, 0.38, 1.0))
    make_cyl("Van_Water_Jug", (vx + 0.65, -18.25, fz + 0.15), 0.10, 0.30, (0.80, 0.86, 0.88, 0.6), segments=10)
    make_box("Van_Strap", (vx + 0.70, -16.6, fz + 0.012), (0.05, 1.20, 0.02), (0.86, 0.60, 0.16, 1.0))


# ══════════════════════════════════════════════════════════════ the store
def build_store():
    make_floor("Store_Floor", (0.0, SY1 / 2.0, 0.0), size_x=SX1 - SX0 + 0.4, size_y=SY1 + 0.4,
               palette={"vinyl": (0.82, 0.82, 0.80, 1.0), "seam": (0.66, 0.66, 0.64, 1.0)})
    pal = {"wall": (0.88, 0.88, 0.86, 1.0), "baseboard": (0.30, 0.32, 0.36, 1.0)}
    make_wall("Store_Wall_W", (SX0, SY1 / 2.0, 0), length=SY1 + 0.4, height=SCEIL, axis='Y', palette=pal, baseboard_face_sign=+1)
    make_wall("Store_Wall_E", (SX1, SY1 / 2.0, 0), length=SY1 + 0.4, height=SCEIL, axis='Y', palette=pal, baseboard_face_sign=-1)
    make_wall_with_openings("Store_Wall_N", (0.0, SY1, 0), length=SX1 - SX0 + 0.4, height=SCEIL, axis='X', palette=pal,
                            baseboard_face_sign=-1, openings=[(7.30, 1.05, 0.90, 2.10)])
    make_wall_with_openings("Store_Wall_S", (0.0, 0.0, 0), length=SX1 - SX0 + 0.4, height=SCEIL, axis='X', palette=pal,
                            baseboard_face_sign=+1, openings=[(-4.0, 1.55, 6.0, 2.30), (0.0, 1.20, 2.0, 2.40), (4.0, 1.55, 6.0, 2.30)])
    make_ceiling("Store_Ceil", (0.0, SY1 / 2.0, SCEIL), size_x=SX1 - SX0 + 0.4, size_y=SY1 + 0.4, with_grid=True, with_stains=True,
                 palette={"tile": (0.90, 0.90, 0.88, 1.0)})
    # the front: the glass and its mullions, the doors, the parapet with the navy band
    for k, (cx, w) in enumerate(((-4.0, 6.0), (4.0, 6.0))):
        make_box(f"Store_Front_Glass_{k}", (cx, 0.02, 1.55), (w, 0.01, 2.30), COL_GLASS)
        for m in range(4):
            make_box(f"Store_Front_Mullion_{k}_{m}", (cx - w / 2.0 + m * w / 3.0, 0.0, 1.55), (0.06, 0.12, 2.30), COL_DARK)
    for s in (-1, 1):
        for e in (-1, 1):   # stiles and rails round the glass (a solid board behind a pane reads as a wall)
            make_box(f"Store_Door_{s:+d}_Stile_{e:+d}", (s * 0.50 + e * 0.44, 0.03, 1.20), (0.08, 0.05, 2.38), COL_DARK)
        make_box(f"Store_Door_{s:+d}_Rail_Top", (s * 0.50, 0.03, 2.33), (0.80, 0.05, 0.08), COL_DARK)
        make_box(f"Store_Door_{s:+d}_Rail_Bottom", (s * 0.50, 0.03, 0.10), (0.80, 0.05, 0.20), COL_DARK)
        make_box(f"Store_Door_{s:+d}_Glass", (s * 0.50, 0.035, 1.25), (0.80, 0.01, 2.10), COL_GLASS)
        make_box(f"Store_Door_{s:+d}_Pull", (s * 0.10, -0.005, 1.05), (0.03, 0.04, 0.50), COL_STEEL)
    make_box("Store_Parapet", (0.0, -0.05, SCEIL + 0.60), (SX1 - SX0 + 0.4, 0.30, 1.20), COL_WHITE)
    make_box("Store_Parapet_Band", (0.0, -0.21, SCEIL + 0.60), (SX1 - SX0 + 0.4, 0.02, 0.50), COL_NAVY)
    make_box("Store_Parapet_Logo", (0.0, -0.225, SCEIL + 0.60), (3.0, 0.004, 0.36), COL_WHITE)
    make_box("Store_Roof", (0.0, (0.10 + SY1 + 0.2) / 2.0, SCEIL + 0.25), (SX1 - SX0 + 0.4, SY1 + 0.1, 0.30), (0.50, 0.50, 0.50, 1.0))
    # the ice chest and the propane cage at the front
    make_box("Ice_Chest", (-2.4, -0.80, 0.08 + 0.60), (1.50, 0.70, 1.20), COL_WHITE)
    make_box("Ice_Chest_Band", (-2.4, -1.152, 0.08 + 0.80), (1.40, 0.004, 0.30), (0.20, 0.50, 0.80, 1.0))
    # Boyd's phone and his Gatorade, put down on the ice chest (named for where they lie: "closeup boyd" would find a Boyd_ part) ("He calls his handler")
    make_box("Ice_Chest_Phone", (-2.15, -0.80, 0.08 + 1.20 + 0.0055), (0.070, 0.140, 0.011), (0.13, 0.13, 0.15, 1.0))
    make_cyl("Ice_Chest_Gatorade", (-2.65, -0.75, 0.08 + 1.20 + 0.12), 0.04, 0.24, (0.94, 0.56, 0.12, 1.0), segments=10)
    make_cyl("Ice_Chest_Gatorade_Cap", (-2.65, -0.75, 0.08 + 1.20 + 0.255), 0.025, 0.03, (0.16, 0.30, 0.62, 1.0), segments=8)
    make_box("Propane_Cage", (2.6, -0.80, 0.08 + 0.75), (1.40, 0.70, 1.50), (0.40, 0.42, 0.44, 1.0))
    for k in range(3):
        make_cyl(f"Propane_Tank_{k}", (2.2 + k * 0.40, -0.80, 0.08 + 0.32), 0.15, 0.48, COL_WHITE, segments=10)
    # the troffers
    for i, fx in enumerate((-5.0, 0.0, 5.0)):
        for j, fy in enumerate((3.0, 8.0)):
            make_fluorescent_tube_fixture(f"Store_Fluor_{i}_{j}", (fx, fy, SCEIL), length=1.20, width=0.60)
    # the counter by the front window, the cashier's side to the W
    cx = -5.3
    make_box("Counter_Body", (cx, 3.6, 0.48), (0.80, 4.0, 0.96), (0.30, 0.32, 0.36, 1.0))
    make_box("Counter_Top", (cx, 3.6, 0.98), (0.90, 4.1, 0.04), (0.62, 0.60, 0.56, 1.0))
    make_box("Counter_Register", (cx - 0.10, 2.6, 1.10), (0.40, 0.36, 0.20), COL_DARK)
    make_box("Counter_Register_Screen", (cx - 0.15, 2.6, 1.33), (0.04, 0.34, 0.26), COL_DARK)   # on the register
    make_box("Counter_Card_Reader", (cx + 0.32, 2.9, 1.06), (0.10, 0.16, 0.12), COL_DARK)
    make_cyl("Counter_Diet_Coke", (cx + 0.30, 2.30, 1.06), 0.033, 0.12, (0.80, 0.80, 0.82, 1.0), segments=8)
    make_box("Counter_Pretzels", (cx + 0.28, 2.05, 1.10), (0.16, 0.06, 0.20), (0.20, 0.36, 0.66, 1.0))
    for k in range(4):
        make_box(f"Counter_Impulse_{k}", (cx + 0.15, 4.2 + k * 0.30, 1.06), (0.24, 0.24, 0.12), ((0.80, 0.18, 0.14, 1.0), (0.94, 0.74, 0.16, 1.0))[k % 2])
    # behind the counter: the cigarette rack and the lottery
    make_box("Cigarette_Rack", (SX0 + 0.10 + 0.18, 3.6, 1.65), (0.36, 3.0, 1.40), (0.24, 0.24, 0.26, 1.0))
    for r in range(4):
        for c in range(10):
            make_box(f"Cigarette_Rack_Stock_{r}_{c}", (SX0 + 0.10 + 0.37, 2.25 + c * 0.30, 1.10 + r * 0.32), (0.02, 0.24, 0.10),
                     ((0.86, 0.20, 0.16, 1.0), (0.92, 0.92, 0.90, 1.0), (0.20, 0.40, 0.70, 1.0), (0.20, 0.50, 0.30, 1.0))[(r + c) % 4])
    make_box("Lottery_Display", (cx + 0.20, 5.25, 1.22), (0.40, 0.30, 0.44), (0.20, 0.50, 0.30, 1.0))
    # the gondolas
    for k, gy in enumerate((5.4, 7.6)):
        stock_gondola(f"Gondola_{k}", (1.0, gy, 0.0), length=7.0, levels=(0.25, 0.62, 0.99, 1.36), plan=("chips", "candy")[k],
                      seed=k * 4, axis='X', depth=0.80, base_col=COL_DARK, metal=COL_STEEL, tag_col=COL_WHITE, lean=True)
    stock_gondola("Gondola_2", (1.0, 3.2, 0.0), length=5.0, levels=(0.25, 0.62, 0.99), plan="convenience",
                  seed=11, axis='X', depth=0.80, base_col=COL_DARK, metal=COL_STEEL, tag_col=COL_WHITE, lean=True)
    # the coolers along the back wall (Diet Coke, Gatorade)
    wall_y = SY1 - 0.10 - 0.50
    for i in range(8):
        make_cooler_door(f"Cooler_{i}", (-3.75 + i * 1.30, wall_y, 1.30), stock="beverage", seed=i)
    make_box("Cooler_Header", (0.8, wall_y - 0.02, 2.60), (10.6, 0.04, 0.24), COL_NAVY)
    make_box("Cooler_Soffit", (0.8, wall_y + 0.25, (2.72 + SCEIL) / 2.0), (10.6, 0.70, SCEIL - 2.72), (0.88, 0.88, 0.86, 1.0))
    # the coffee counter on the E wall
    make_box("Coffee_Counter", (SX1 - 0.10 - 0.32, 4.0, 0.46), (0.64, 3.0, 0.92), (0.30, 0.32, 0.36, 1.0))
    make_box("Coffee_Counter_Top", (SX1 - 0.10 - 0.33, 4.0, 0.94), (0.66, 3.04, 0.04), (0.62, 0.60, 0.56, 1.0))
    for k in range(3):
        make_box(f"Coffee_Brewer_{k}", (SX1 - 0.10 - 0.28, 3.0 + k * 0.80, 1.24), (0.40, 0.40, 0.56), COL_DARK)
        make_cyl(f"Coffee_Brewer_{k}_Pot", (SX1 - 0.10 - 0.52, 3.0 + k * 0.80, 1.05), 0.07, 0.18, (0.30, 0.20, 0.14, 1.0), segments=10)
    make_cyl("Coffee_Cup_Stack", (SX1 - 0.10 - 0.40, 5.2, 1.08), 0.05, 0.24, COL_WHITE, segments=8)
    make_box("Restroom_Sign", (7.30, SY1 - 0.105, 2.40), (0.40, 0.01, 0.16), COL_NAVY)


# ══════════════════════════════════════════════════════════════ the men's room
def build_restroom():
    pal = {"wall": COL_TILE, "baseboard": (0.70, 0.72, 0.70, 1.0)}
    make_box("Restroom_Floor", ((RX0 + RX1) / 2.0, (SY1 + RY1) / 2.0, -0.05), (RX1 - RX0 + 0.2, RY1 - SY1 + 0.2, 0.10), (0.56, 0.58, 0.56, 1.0))
    make_wall("Restroom_Wall_W", (RX0, (SY1 + RY1) / 2.0, 0), length=RY1 - SY1 + 0.2, height=SCEIL, axis='Y', palette=pal, baseboard_face_sign=+1)
    make_wall("Restroom_Wall_E", (RX1, (SY1 + RY1) / 2.0, 0), length=RY1 - SY1 + 0.2, height=SCEIL, axis='Y', palette=pal, baseboard_face_sign=-1)
    make_wall("Restroom_Wall_N", ((RX0 + RX1) / 2.0, RY1, 0), length=RX1 - RX0 + 0.2, height=SCEIL, axis='X', palette=pal, baseboard_face_sign=-1)
    make_box("Restroom_Ceil", ((RX0 + RX1) / 2.0, (SY1 + RY1) / 2.0, RCEIL + 0.05), (RX1 - RX0, RY1 - SY1, 0.10), (0.86, 0.86, 0.84, 1.0))
    make_fluorescent_tube_fixture("Restroom_Fluor", ((RX0 + RX1) / 2.0, 13.6, RCEIL), length=1.20, width=0.30)
    # the tile: a band at chair height round the room's faces
    make_box("Restroom_Tile_Band_W", (RX0 + 0.101, (SY1 + RY1) / 2.0, 1.20), (0.004, RY1 - SY1 - 0.2, 0.10), COL_TILE_BAND)
    make_box("Restroom_Tile_Band_E", (RX1 - 0.101, (SY1 + RY1) / 2.0, 1.20), (0.004, RY1 - SY1 - 0.2, 0.10), COL_TILE_BAND)
    make_box("Restroom_Tile_Band_N", ((RX0 + RX1) / 2.0, RY1 - 0.101, 1.20), (RX1 - RX0 - 0.2, 0.004, 0.10), COL_TILE_BAND)
    # the door from the store, standing open against the E wall
    make_box("Restroom_Door", (RX1 - 0.12, SY1 + 0.55, 1.03), (0.04, 0.90, 2.06), (0.30, 0.32, 0.36, 1.0))
    # the sink and mirror on the W wall, the hand dryer, the bin
    make_box("Restroom_Sink", (RX0 + 0.10 + 0.25, 13.4, 0.84), (0.50, 0.56, 0.18), COL_WHITE)
    make_box("Restroom_Sink_Bracket", (RX0 + 0.10 + 0.05, 13.4, 0.55), (0.10, 0.30, 0.40), COL_STEEL)
    make_cyl("Restroom_Faucet", (RX0 + 0.10 + 0.08, 13.4, 1.00), 0.015, 0.16, COL_STEEL, segments=6)
    make_box("Restroom_Mirror", (RX0 + 0.10 + 0.01, 13.4, 1.55), (0.02, 0.60, 0.80), (0.70, 0.76, 0.80, 1.0))
    make_box("Restroom_Hand_Dryer", (RX0 + 0.10 + 0.12, 12.55, 1.25), (0.24, 0.30, 0.26), COL_STEEL)
    make_cyl("Restroom_Bin", (RX0 + 0.35, 14.3, 0.35), 0.22, 0.70, (0.40, 0.42, 0.44, 1.0), segments=10)
    # the urinal on the N wall
    make_box("Restroom_Urinal", (5.4, RY1 - 0.10 - 0.18, 0.80), (0.42, 0.36, 0.70), COL_WHITE)
    make_cyl("Restroom_Urinal_Flush", (5.4, RY1 - 0.12, 1.30), 0.03, 0.30, COL_STEEL, segments=6)
    # the stall in the NE corner — shut, occupied
    st_x0, st_y0 = 6.50, 13.90
    make_box("Stall_Partition_W", (st_x0, (st_y0 + RY1 - 0.10) / 2.0, 0.15 + 0.85), (0.03, RY1 - 0.10 - st_y0, 1.70), (0.36, 0.44, 0.52, 1.0))
    make_box("Stall_Partition_Front_Post", (st_x0, st_y0, 0.15 + 0.85), (0.05, 0.05, 1.70), COL_STEEL)
    make_box("Stall_Door", (st_x0 + 0.70, st_y0, 0.15 + 0.85), (1.30, 0.03, 1.70), (0.36, 0.44, 0.52, 1.0))
    make_box("Stall_Door_Latch_Red", (st_x0 + 1.25, st_y0 - 0.02, 1.05), (0.06, 0.012, 0.03), (0.80, 0.16, 0.14, 1.0))
    for k, px in enumerate((st_x0, st_x0 + 1.32)):
        make_box(f"Stall_Foot_{k}", (px, st_y0, 0.075), (0.05, 0.05, 0.15), COL_STEEL)
    make_box("Stall_Toilet_Bowl", (7.25, 14.95, 0.22), (0.38, 0.55, 0.44), COL_WHITE)
    make_box("Stall_Toilet_Tank", (7.25, RY1 - 0.10 - 0.11, 0.62), (0.44, 0.20, 0.36), COL_WHITE)
    make_box("Stall_TP_Holder", (RX1 - 0.10 - 0.05, 14.70, 0.65), (0.10, 0.18, 0.18), COL_STEEL)


def main():
    clear_scene()
    build_ground()
    build_forecourt()
    build_vehicles()
    build_van()
    build_store()
    build_restroom()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/nexcorp_fueling_station.glb"))
    print(f"\n[build_nexcorp_fueling_station] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
