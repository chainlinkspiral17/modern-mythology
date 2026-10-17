"""airport_cabin — vol 3's LAX gate and the airliner cabin of three flights
(draft 1, 2026-10-17).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
The text names no airline, aircraft, gate, livery or seat map, so nothing
here is branded and nothing carries a name but the shop.

THE GATE AT LAX (origin) — Janessa waits for her flight to Houston.
  "Janessa waits at LAX for the flight to up up and away."
                                       → the gate's seating rows (x < 0)
  "She buys books and gifts in the airport convenience store."
                                       → the store across the concourse
                                         (x 4..12): book racks, gift shelves
  "She packed light, barely anything." / "the anniversary card and gift in
   her bag" / "She itemizes her packing list"
                                       → her small bag, the shop bag, the
                                         list and pen on the seat beside hers
  The text says nothing of windows, planes or the sky: the W wall is the
  gate's wall, its jet-bridge door shut.

THE CABIN (x 56..64, the nose toward +y) — one plain economy cabin, 3 + 3:
  plane_night (vol3_ch5_flight, Oregon to Houston): Andy "seated at the
  window", the armrest between him and the businesswoman up ("She asks Andy
  if she can put the arm rest up"), the "satellite lamp overhead", "the fan
  positioned to hit him hard in the face", "the call button", "the in-flight
  embedded headrest monitor", "the many ice cubes in clear plastic cups",
  "her portable CD player" — the window black.
  plane_day (vol3_ch6_stacks, "flight number one", Texas to LAX): Andy alone
  with the "hardcover notebook", the pen, something serious to read; the
  shades up on daylight (the orange-pink sunset is his memory, not the
  window).
  plane_vol4 (vol4_story_everyday_in_november): "i fall asleep among
  strangers" — the cabin full, blankets and pillows on the seats, most
  shades down, nothing of vol 3's.
Props that belong to one flight carry its preset (`<Name>__<preset>`).

Blender: x east, y north, z up; Godot (x, z, -y).

DRAFT 2 targets: the night window's "string of town lights along a highway"
below (a ground plane under the wing); the window POV and the overhead
close (the PSU) as presets; the jet bridge ("the tunnel") at Houston; the
gate's other travellers as luggage and coats; the store's clerk counter
dressing; the LAX concourse running on past both ends; Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_blob, make_lathe,
                             join_stock, export_glb)
from _props.structure import make_floor

try:
    import bpy
except ImportError:
    bpy = None

# ── the gate ──────────────────────────────────────────────────────────
LX0, LX1, LY0, LY1, LH = -12.0, 12.0, 0.0, 50.0, 5.5
TERRAZZO = (0.78, 0.76, 0.72, 1.0); TERRAZZO_SEAM = (0.66, 0.64, 0.60, 1.0)
GATE_CARPET = (0.26, 0.30, 0.40, 1.0)
WALL = (0.86, 0.86, 0.84, 1.0); WALL_DARK = (0.56, 0.58, 0.60, 1.0)
CHROME = (0.70, 0.72, 0.74, 1.0); SEAT_VINYL = (0.14, 0.16, 0.20, 1.0)
STORE_X = 4.0
STORE_Y0, STORE_Y1 = 16.0, 30.0

# ── the cabin ─────────────────────────────────────────────────────────
CX = 60.0                           # aisle centre line
CY0, ROWS, PITCH = 2.0, 14, 0.81
SEAT_W, ARM = 0.46, 0.05
HALF = 1.85                         # half the cabin's width at the armrests
ANDY_ROW = 7
CABIN_WALL = (0.84, 0.84, 0.80, 1.0); CABIN_BIN = (0.90, 0.90, 0.88, 1.0)
CABIN_CARPET = (0.24, 0.26, 0.34, 1.0)
SEAT_FABRIC = (0.22, 0.26, 0.38, 1.0); SEAT_FABRIC_2 = (0.18, 0.22, 0.32, 1.0)


def join_named(prefix, out_name):
    """Join meshes whose names start with `prefix` into one, named so its
    `__<preset>` suffix survives (join_stock would drop it)."""
    if bpy is None:
        return
    objs = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith(prefix)]
    if len(objs) < 2:
        return
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    objs[0].name = out_name
    bpy.ops.object.select_all(action='DESELECT')


def build_gate():
    cy = (LY0 + LY1) / 2.0
    make_floor("Gate_Floor", (0.0, cy, 0.0), size_x=LX1 - LX0, size_y=LY1 - LY0,
               palette={"vinyl": TERRAZZO, "seam": TERRAZZO_SEAM})
    make_box("Gate_Carpet", ((LX0 + 0.0) / 2.0 - 0.5, cy, 0.006), (11.0, 36.0, 0.012), GATE_CARPET)
    make_box("Gate_Ceil", (0.0, cy, LH + 0.05), (LX1 - LX0, LY1 - LY0, 0.10), (0.80, 0.80, 0.80, 1.0))
    make_box("Gate_Wall_W", (LX0 - 0.1, cy, LH / 2.0), (0.2, LY1 - LY0, LH), WALL)
    make_box("Gate_Wall_E", (LX1 + 0.1, cy, LH / 2.0), (0.2, LY1 - LY0, LH), WALL)
    make_box("Gate_End_S", (0.0, LY0 - 0.1, LH / 2.0), (LX1 - LX0, 0.2, LH), WALL_DARK)
    make_box("Gate_End_N", (0.0, LY1 + 0.1, LH / 2.0), (LX1 - LX0, 0.2, LH), WALL_DARK)
    # the ceiling's light panels in rows, and the structure's columns
    for i in range(3):
        for j in range(9):
            make_box(f"Gate_Light_Panel_{i}_{j}", (-8.0 + i * 8.0, 3.0 + j * 5.5, LH - 0.01), (2.4, 1.2, 0.02), (0.98, 0.98, 0.94, 1.0))
    for j in range(5):
        for x in (-0.6, 3.4):
            make_box(f"Gate_Column_{j}_{x:+.0f}", (x, 5.0 + j * 10.0, LH / 2.0), (0.6, 0.6, LH), (0.82, 0.82, 0.80, 1.0))
    # the gate: the podium, the jet-bridge door (shut), a departures screen (no lettering)
    make_box("Gate_Podium", (LX0 + 2.2, 24.0, 0.55), (0.70, 1.80, 1.10), (0.40, 0.42, 0.46, 1.0))
    make_box("Gate_Podium_Top", (LX0 + 2.2, 24.0, 1.115), (0.78, 1.90, 0.03), (0.70, 0.70, 0.70, 1.0))
    make_box("Gate_Jetway_Door", (LX0 + 0.02, 28.0, 1.2), (0.04, 1.80, 2.4), (0.52, 0.54, 0.58, 1.0))
    make_box("Gate_Jetway_Frame", (LX0 + 0.01, 28.0, 1.22), (0.02, 2.00, 2.52), (0.36, 0.38, 0.40, 1.0))
    make_box("Gate_Screen", (LX0 + 0.04, 24.0, 2.9), (0.06, 1.60, 0.90), (0.10, 0.10, 0.12, 1.0))
    make_box("Gate_Screen_Face", (LX0 + 0.075, 24.0, 2.9), (0.004, 1.48, 0.80), (0.24, 0.34, 0.56, 1.0))
    for k in range(5):
        make_box(f"Gate_Screen_Line_{k}", (LX0 + 0.079, 24.0, 3.18 - k * 0.13), (0.002, 1.30, 0.04), (0.86, 0.86, 0.80, 1.0))
    make_box("Gate_Screen_Bracket", (LX0 + 0.02, 24.0, 3.45), (0.04, 0.20, 0.20), (0.36, 0.38, 0.40, 1.0))
    # the seating: rows of joined seats on beams, facing the gate (west)
    for r, x in enumerate((-3.0, -4.9, -6.8, -8.7)):
        for half, (y0, n) in enumerate(((14.0, 8), (24.6, 8))):
            beam_l = n * 0.60
            make_box(f"GateSeat_Beam_{r}_{half}", (x + 0.10, y0 + beam_l / 2.0, 0.30), (0.08, beam_l, 0.06), CHROME)
            for e in (0, 1):
                ly = y0 + 0.2 + e * (beam_l - 0.4)
                make_box(f"GateSeat_Leg_{r}_{half}_{e}", (x + 0.10, ly, 0.135), (0.50, 0.06, 0.27), CHROME)
            for k in range(n):
                y = y0 + 0.30 + k * 0.60
                make_box(f"GateSeat_Pan_{r}_{half}_{k}", (x, y, 0.42), (0.48, 0.52, 0.06), SEAT_VINYL)
                make_rot_box(f"GateSeat_Back_{r}_{half}_{k}", (x + 0.27, y, 0.74), (0.06, 0.52, 0.60), SEAT_VINYL, pitch=0.12)
                make_box(f"GateSeat_Post_{r}_{half}_{k}", (x + 0.10, y, 0.36), (0.06, 0.06, 0.06), CHROME)
                if k < n - 1:
                    make_box(f"GateSeat_Arm_{r}_{half}_{k}", (x, y + 0.30, 0.62), (0.40, 0.04, 0.03), CHROME)
                    make_box(f"GateSeat_ArmPost_{r}_{half}_{k}", (x + 0.12, y + 0.30, 0.47), (0.04, 0.04, 0.28), CHROME)   # down to the beam
    # Janessa's seat: row 1, the seat at y 17.0; beside it her things
    jx, jy = -4.9, 14.0 + 0.30 + 4 * 0.60
    make_chamfer_box("Janessa_Bag", (jx, jy + 0.60, 0.59), (0.36, 0.30, 0.28), (0.36, 0.20, 0.24, 1.0), chamfer=0.04)
    make_box("Janessa_Bag_Strap", (jx, jy + 0.60, 0.74), (0.02, 0.28, 0.02), (0.20, 0.14, 0.14, 1.0))
    make_box("Shop_Bag", (jx - 0.10, jy + 1.20, 0.60), (0.26, 0.10, 0.30), (0.92, 0.90, 0.84, 1.0))
    make_box("Shop_Bag_Card", (jx - 0.08, jy + 1.20, 0.79), (0.16, 0.02, 0.10), (0.84, 0.36, 0.40, 1.0))
    make_rot_box("Packing_List", (jx - 0.04, jy + 0.70, 0.735), (0.22, 0.28, 0.003), (0.96, 0.96, 0.92, 1.0), yaw=0.2)
    make_rot_box("Packing_List_Pen", (jx - 0.02, jy + 0.66, 0.741), (0.14, 0.01, 0.01), (0.14, 0.20, 0.46, 1.0), yaw=0.6)
    # the convenience store across the concourse: a glass front, the door,
    # paperback racks, gift shelves, the counter and the cooler
    sx0, sx1 = STORE_X, LX1
    scx, scy = (sx0 + sx1) / 2.0, (STORE_Y0 + STORE_Y1) / 2.0
    make_box("Store_Floor", (scx, scy, 0.007), (sx1 - sx0, STORE_Y1 - STORE_Y0, 0.014), (0.86, 0.84, 0.78, 1.0))
    make_box("Store_Ceil", (scx, scy, 3.2), (sx1 - sx0, STORE_Y1 - STORE_Y0, 0.08), (0.94, 0.94, 0.92, 1.0))
    make_box("Store_Fascia", (sx0, scy, 3.6), (0.30, STORE_Y1 - STORE_Y0, 0.80), (0.20, 0.30, 0.46, 1.0))
    make_box("Store_Fascia_Band", (sx0 - 0.16, scy, 3.6), (0.02, STORE_Y1 - STORE_Y0 - 1.0, 0.24), (0.94, 0.86, 0.40, 1.0))
    for s, y in (("S", STORE_Y0), ("N", STORE_Y1)):
        make_box(f"Store_Wall_{s}", (scx, y, 1.6), (sx1 - sx0, 0.16, 3.2), WALL)
    door_y = 23.0
    y = STORE_Y0 + 0.08
    k = 0
    while y < STORE_Y1 - 0.1:
        if abs(y + 0.9 - door_y) < 1.3:
            y = door_y + 1.0
            continue
        w = min(1.8, STORE_Y1 - 0.08 - y)
        make_box(f"Store_Glass_{k}", (sx0, y + w / 2.0, 1.55), (0.02, w - 0.06, 3.0), (0.62, 0.72, 0.78, 1.0))
        make_box(f"Store_Mullion_{k}", (sx0, y, 1.6), (0.06, 0.06, 3.2), CHROME)
        y += w
        k += 1
    make_box("Store_Door_Head", (sx0, door_y, 3.1), (0.08, 2.0, 0.2), CHROME)
    make_box("Store_Mat", (sx0 + 0.8, door_y, 0.016), (1.2, 1.8, 0.012), (0.20, 0.20, 0.22, 1.0))
    # paperback racks: two long gondolas of books facing the glass, a spinner
    for g, gx in enumerate((6.0, 8.6)):
        make_box(f"Book_Gondola_{g}", (gx, scy + 1.0, 0.75), (0.60, 8.0, 1.50), (0.86, 0.84, 0.80, 1.0))
        for side in (-1, 1):
            for sh in range(4):
                z = 0.30 + sh * 0.34
                make_box(f"Book_Gondola_{g}_Shelf_{side:+d}_{sh}", (gx + side * 0.36, scy + 1.0, z), (0.12, 7.8, 0.02),
                         (0.78, 0.76, 0.72, 1.0))
                for b in range(26):
                    by = scy + 1.0 - 3.8 + b * 0.30
                    make_rot_box(f"Store_Stock_Book_{g}_{side:+d}_{sh}_{b}", (gx + side * 0.37, by, z + 0.11), (0.03, 0.12, 0.19),
                                 ((0.80, 0.30, 0.24, 1.0), (0.20, 0.36, 0.60, 1.0), (0.94, 0.90, 0.80, 1.0), (0.30, 0.50, 0.36, 1.0),
                                  (0.16, 0.16, 0.18, 1.0), (0.90, 0.70, 0.30, 1.0))[(g * 7 + sh * 3 + b + (side > 0)) % 6],
                                 roll=-0.25 * side)
    make_cyl("Book_Spinner_Base", (5.2, 18.2, 0.04), 0.30, 0.08, CHROME, segments=12)
    make_cyl("Book_Spinner_Post", (5.2, 18.2, 0.85), 0.03, 1.60, CHROME, segments=8)
    for t in range(4):
        make_cyl(f"Book_Spinner_Tier_{t}", (5.2, 18.2, 0.425 + t * 0.32), 0.26, 0.01, CHROME, segments=12)
        for a in range(4):
            ang = a * math.pi / 2.0
            make_rot_box(f"Store_Stock_Spinner_{t}_{a}", (5.2 + math.cos(ang) * 0.20, 18.2 + math.sin(ang) * 0.20, 0.55 + t * 0.32),
                         (0.04, 0.30, 0.24), ((0.90, 0.40, 0.30, 1.0), (0.30, 0.50, 0.80, 1.0))[(t + a) % 2], yaw=ang)
    # gift shelves on the E wall: mugs, plush, frames, cards
    for sh in range(5):
        z = 0.40 + sh * 0.42
        make_box(f"Gift_Shelf_{sh}", (sx1 - 0.25, scy, z), (0.40, 10.0, 0.03), (0.80, 0.78, 0.74, 1.0))
        for g in range(20):
            gy = scy - 4.6 + g * 0.48
            kind = (sh + g) % 3
            if kind == 0:
                make_cyl(f"Store_Stock_Mug_{sh}_{g}", (sx1 - 0.30, gy, z + 0.065), 0.045, 0.10,
                         ((0.92, 0.92, 0.90, 1.0), (0.20, 0.30, 0.56, 1.0))[g % 2], segments=10)
            elif kind == 1:
                make_blob(f"Store_Stock_Plush_{sh}_{g}", (sx1 - 0.30, gy, z + 0.09), 0.08,
                          ((0.70, 0.54, 0.36, 1.0), (0.86, 0.80, 0.70, 1.0))[g % 2], noise=0.1, seed=g)
            else:
                make_box(f"Store_Stock_Frame_{sh}_{g}", (sx1 - 0.36, gy, z + 0.09), (0.03, 0.14, 0.18), (0.62, 0.48, 0.30, 1.0))
    make_box("Gift_Shelf_Back", (sx1 - 0.04, scy, 1.25), (0.04, 10.0, 2.5), (0.74, 0.72, 0.68, 1.0))
    for sh in range(5):
        for s in (-1, 1):
            make_box(f"Gift_Shelf_Bracket_{sh}_{s:+d}", (sx1 - 0.25, scy + s * 4.9, 0.40 + sh * 0.42 - 0.04), (0.38, 0.03, 0.05),
                     (0.60, 0.60, 0.60, 1.0))
    # the counter by the door, the card rack on it, the drinks cooler
    make_box("Store_Counter", (sx0 + 1.6, STORE_Y1 - 1.6, 0.50), (1.40, 0.70, 1.00), (0.40, 0.42, 0.46, 1.0))
    make_box("Store_Register", (sx0 + 1.6, STORE_Y1 - 1.5, 1.08), (0.36, 0.30, 0.16), (0.16, 0.16, 0.18, 1.0))
    make_box("Store_CardRack", (sx0 + 1.1, STORE_Y1 - 1.70, 1.25), (0.30, 0.20, 0.50), (0.84, 0.36, 0.40, 1.0))
    make_box("Store_Cooler", (scx + 2.0, STORE_Y1 - 0.48, 1.0), (2.4, 0.80, 2.0), (0.70, 0.72, 0.74, 1.0))
    make_box("Store_Cooler_Glass", (scx + 2.0, STORE_Y1 - 0.884, 1.05), (2.2, 0.006, 1.70), (0.50, 0.60, 0.66, 1.0))
    # the concourse's other storefront, shuttered, for depth
    make_box("Shop_Shutter", (STORE_X, 38.0, 1.5), (0.06, 10.0, 3.0), (0.56, 0.58, 0.60, 1.0))
    make_box("Shop_Fascia", (STORE_X, 38.0, 4.25), (0.30, 10.0, 2.50), (0.30, 0.30, 0.34, 1.0))   # up to the ceiling
    for k in range(4):
        make_box(f"Bin_{k}", (2.6, 8.0 + k * 10.0, 0.45), (0.40, 0.40, 0.90), (0.40, 0.42, 0.44, 1.0))


# ── the cabin ─────────────────────────────────────────────────────────
def seat_x(side, pos):
    """pos 0 = aisle seat, 1 = middle, 2 = window; side -1 (port) / +1 (starboard)."""
    return CX + side * (0.25 + ARM + SEAT_W / 2.0 + pos * (SEAT_W + ARM))


def build_cabin():
    y0, y1 = CY0 - 1.6, CY0 + ROWS * PITCH + 1.2
    cy = (y0 + y1) / 2.0
    L = y1 - y0
    make_box("Cabin_Floor", (CX, cy, -0.02), (2 * HALF + 0.3, L, 0.04), CABIN_CARPET)
    make_box("Cabin_Aisle", (CX, cy, 0.003), (0.50, L, 0.006), (0.30, 0.32, 0.40, 1.0))
    for s in (-1, 1):
        # the sidewall: low vertical panel, the window belt, the cove up to the bins
        make_box(f"Cabin_Sidewall_Lo_{s:+d}", (CX + s * (HALF + 0.06), cy, 0.45), (0.06, L, 0.90), CABIN_WALL)
        make_box(f"Cabin_Sidewall_Belt_{s:+d}", (CX + s * (HALF + 0.06), cy, 1.23), (0.06, L, 0.66), CABIN_WALL)   # the window belt
        make_box(f"Cabin_Sidewall_Hi_{s:+d}", (CX + s * (HALF + 0.02), cy, 1.66), (0.06, L, 0.20), CABIN_WALL)
        make_rot_box(f"Cabin_Cove_{s:+d}", (CX + s * (HALF - 0.12), cy, 1.86), (0.06, L, 0.40), CABIN_WALL, roll=0.0,
                     pitch=-s * 0.65)
        # the overhead bins: their fronts, their undersides with the PSU strip
        make_box(f"Cabin_Bin_{s:+d}", (CX + s * (HALF - 0.42), cy, 1.98), (0.60, L, 0.40), CABIN_BIN)
        make_box(f"Cabin_Bin_Lip_{s:+d}", (CX + s * (HALF - 0.73), cy, 1.98), (0.03, L, 0.42), (0.80, 0.80, 0.78, 1.0))
        make_box(f"Cabin_PSU_{s:+d}", (CX + s * (HALF - 0.42), cy, 1.765), (0.56, L, 0.03), (0.86, 0.86, 0.84, 1.0))
        for k in range(int((y1 - y0 - 0.4) / (PITCH * 1.5))):
            make_box(f"Cabin_Bin_Seam_{s:+d}_{k}", (CX + s * (HALF - 0.745), CY0 + k * PITCH * 1.5, 1.98), (0.006, 0.01, 0.38),
                     (0.66, 0.66, 0.64, 1.0))
    make_box("Cabin_Ceiling", (CX, cy, 2.20), (1.30, L, 0.04), (0.92, 0.92, 0.90, 1.0))
    make_box("Cabin_Bulkhead_Fwd", (CX, y1 + 0.03, 1.1), (2 * HALF + 0.3, 0.06, 2.24), (0.80, 0.80, 0.78, 1.0))
    make_box("Cabin_Bulkhead_Aft", (CX, y0 - 0.03, 1.1), (2 * HALF + 0.3, 0.06, 2.24), (0.80, 0.80, 0.78, 1.0))
    # the windows: a bezel and glass per row each side — black at night,
    # sky by day, shades mostly down in November
    for s in (-1, 1):
        wx = CX + s * (HALF + 0.024)
        for k in range(ROWS):
            y = CY0 + k * PITCH + 0.15
            make_chamfer_box(f"Cabin_Win_Bezel_{s:+d}_{k}", (wx, y, 1.20), (0.012, 0.34, 0.46), (0.92, 0.92, 0.90, 1.0), chamfer=0.004)
            make_box(f"WinNight_{s:+d}_{k}__plane_night", (wx - s * 0.007, y, 1.20), (0.004, 0.24, 0.34), (0.02, 0.02, 0.04, 1.0))
            make_box(f"WinDay_{s:+d}_{k}__plane_day", (wx - s * 0.007, y, 1.20), (0.004, 0.24, 0.34), (0.74, 0.84, 0.96, 1.0))
            down = (k + (s > 0)) % 4 != 0
            make_box(f"WinV4_{s:+d}_{k}__plane_vol4", (wx - s * 0.007, y, 1.20 + (0.10 if down else 0.0)),
                     (0.004, 0.24, 0.34 if not down else 0.14),
                     (0.62, 0.66, 0.72, 1.0))
            make_box(f"ShadeV4_{s:+d}_{k}__plane_vol4", (wx - s * 0.008, y, 1.20 - (0.07 if down else -0.15)),
                     (0.004, 0.25, 0.20 if down else 0.04), (0.86, 0.86, 0.84, 1.0))
            make_box(f"ShadeUp_{s:+d}_{k}__plane_night__plane_day", (wx - s * 0.008, y, 1.35), (0.004, 0.25, 0.04),
                     (0.86, 0.86, 0.84, 1.0))
    # the seats, 3 + 3, every row facing the nose
    for k in range(ROWS):
        y = CY0 + k * PITCH
        for s in (-1, 1):
            for pos in range(3):
                x = seat_x(s, pos)
                col = SEAT_FABRIC if (k + pos) % 2 else SEAT_FABRIC_2
                p = f"CabSeat_Seat_{k}_{s:+d}_{pos}"
                make_box(p + "_Cush", (x, y + 0.04, 0.44), (SEAT_W, 0.48, 0.12), col)
                make_rot_box(p + "_Back", (x, y - 0.22, 0.82), (SEAT_W, 0.10, 0.68), col, roll=-0.10)
                make_box(p + "_Head", (x, y - 0.255, 1.20), (SEAT_W - 0.04, 0.12, 0.16), (0.86, 0.86, 0.84, 1.0))
                # the seatback behind: the headrest monitor, the stowed tray
                make_box(p + "_Monitor", (x, y - 0.312, 1.02), (0.20, 0.006, 0.14), (0.08, 0.08, 0.10, 1.0))
                make_box(p + "_Tray", (x, y - 0.29, 0.74), (0.38, 0.01, 0.26), (0.66, 0.66, 0.66, 1.0))
            # the frame under the triple and its armrests
            xs = [seat_x(s, p) for p in range(3)]
            make_box(f"CabSeat_Frame_{k}_{s:+d}", ((xs[0] + xs[2]) / 2.0, y + 0.04, 0.33), (3 * SEAT_W + 3 * ARM, 0.40, 0.10),
                     (0.36, 0.36, 0.38, 1.0))
            for e in (0, 1):
                ly = y + 0.04 + (e - 0.5) * 0.34
                make_box(f"CabSeat_Leg_{k}_{s:+d}_{e}", ((xs[0] + xs[2]) / 2.0, ly, 0.14), (0.04, 0.04, 0.28), (0.36, 0.36, 0.38, 1.0))
            for a in range(4):
                ax = CX + s * (0.25 + ARM / 2.0 + a * (SEAT_W + ARM))
                if k == ANDY_ROW and s == 1 and a == 2:
                    continue            # the armrest between Andy and the woman: up (below)
                make_box(f"CabSeat_Arm_{k}_{s:+d}_{a}", (ax, y + 0.02, 0.62), (ARM, 0.46, 0.05), (0.40, 0.40, 0.42, 1.0))
                make_box(f"CabSeat_ArmPost_{k}_{s:+d}_{a}", (ax, y - 0.16, 0.48), (ARM, 0.05, 0.24), (0.36, 0.36, 0.38, 1.0))
        # the PSU over each triple: two reading lamps, two vents, the call button
        for s in (-1, 1):
            for pos in range(3):
                x = CX + s * (HALF - 0.42) + s * (pos - 1) * 0.14
                make_cyl(f"CabSeat_Lamp_{k}_{s:+d}_{pos}", (x, y + 0.30, 1.745), 0.022, 0.012, (0.94, 0.94, 0.90, 1.0), segments=8)
                make_cyl(f"CabSeat_Vent_{k}_{s:+d}_{pos}", (x, y + 0.40, 1.74), 0.018, 0.02, (0.70, 0.70, 0.70, 1.0), segments=8)
            make_box(f"CabSeat_Call_{k}_{s:+d}", (CX + s * (HALF - 0.62), y + 0.36, 1.745), (0.03, 0.03, 0.012), (0.40, 0.56, 0.86, 1.0))

    # Andy's row: the window seat (starboard), the armrest up, his lamp and vent
    y = CY0 + ANDY_ROW * PITCH
    ax = CX + 1 * (0.25 + ARM / 2.0 + 2 * (SEAT_W + ARM))
    make_box("Andy_Armrest_Up", (ax, y - 0.18, 0.86), (ARM, 0.05, 0.46), (0.40, 0.40, 0.42, 1.0))
    make_box("Andy_Armrest_Post", (ax, y - 0.16, 0.48), (ARM, 0.05, 0.24), (0.36, 0.36, 0.38, 1.0))
    wx, mx = seat_x(1, 2), seat_x(1, 1)
    # the vent turned to his face (a tilted nozzle), the lamp's lens lit
    make_rot_box("Andy_Vent_Nozzle", (CX + (HALF - 0.42) + 0.14, y + 0.40, 1.715), (0.03, 0.03, 0.04), (0.60, 0.60, 0.60, 1.0), roll=0.5)
    make_cyl("Andy_Lamp_Lens__plane_night", (CX + (HALF - 0.42) + 0.14, y + 0.30, 1.738), 0.02, 0.004, (1.0, 0.96, 0.80, 1.0), segments=8)
    # the woman's tray down: clear cups with ice, the CD player (night)
    tz = 0.74
    make_box("Tray_Down_Woman__plane_night", (mx, y + 0.33, tz), (0.38, 0.26, 0.012), (0.66, 0.66, 0.66, 1.0))
    for k, (dx, dy) in enumerate(((-0.10, 0.04), (0.02, -0.04), (0.12, 0.06))):
        make_cyl(f"Cup_{k}__plane_night", (mx + dx, y + 0.33 + dy, tz + 0.055), 0.032, 0.10, (0.86, 0.90, 0.92, 1.0), segments=10)
        make_cyl(f"Cup_{k}_Ice__plane_night", (mx + dx, y + 0.33 + dy, tz + 0.08), 0.028, 0.04, (0.96, 0.98, 1.0, 1.0), segments=8)
    make_cyl("CD_Player__plane_night", (mx - 0.02, y + 0.27, tz + 0.02), 0.068, 0.028, (0.70, 0.72, 0.74, 1.0), segments=14)
    make_box("CD_Player_Cord__plane_night", (mx - 0.02, y + 0.19, tz + 0.009), (0.004, 0.14, 0.004), (0.10, 0.10, 0.10, 1.0))
    make_box("Tray_Bracket_L__plane_night", (mx - 0.20, y + 0.47, tz - 0.01), (0.012, 0.14, 0.02), (0.50, 0.50, 0.50, 1.0))
    make_box("Tray_Bracket_R__plane_night", (mx + 0.20, y + 0.47, tz - 0.01), (0.012, 0.14, 0.02), (0.50, 0.50, 0.50, 1.0))
    # day: Andy's tray down with the hardcover notebook, the pen, the book
    make_box("Tray_Down_Andy__plane_day", (wx, y + 0.33, tz), (0.38, 0.26, 0.012), (0.66, 0.66, 0.66, 1.0))
    make_box("Tray_Bracket_L_Andy__plane_day", (wx - 0.20, y + 0.47, tz - 0.01), (0.012, 0.14, 0.02), (0.50, 0.50, 0.50, 1.0))
    make_box("Tray_Bracket_R_Andy__plane_day", (wx + 0.20, y + 0.47, tz - 0.01), (0.012, 0.14, 0.02), (0.50, 0.50, 0.50, 1.0))
    make_box("Notebook_Open__plane_day", (wx, y + 0.33, tz + 0.016), (0.30, 0.22, 0.02), (0.94, 0.92, 0.84, 1.0))
    make_box("Notebook_Cover__plane_day", (wx, y + 0.33, tz + 0.008), (0.31, 0.23, 0.004), (0.16, 0.22, 0.32, 1.0))
    for k in range(6):
        make_box(f"Notebook_Line_{k}__plane_day", (wx - 0.07, y + 0.25 + k * 0.03, tz + 0.0265), (0.12, 0.004, 0.001), (0.20, 0.22, 0.36, 1.0))
    make_rot_box("Notebook_Pen__plane_day", (wx + 0.05, y + 0.31, tz + 0.03), (0.13, 0.008, 0.008), (0.10, 0.10, 0.12, 1.0), yaw=0.5)
    make_box("Serious_Book__plane_day", (mx, y + 0.06, 0.515), (0.16, 0.24, 0.03), (0.40, 0.18, 0.16, 1.0))
    # November: strangers asleep — blankets and pillows on most seats
    for k in range(ROWS):
        for s in (-1, 1):
            for pos in range(3):
                if (k * 3 + pos + (s > 0)) % 5 == 4:
                    continue
                x = seat_x(s, pos)
                yy = CY0 + k * PITCH
                make_chamfer_box(f"V4Blanket_{k}_{s:+d}_{pos}", (x, yy + 0.10, 0.56), (0.42, 0.40, 0.12),
                                 ((0.30, 0.34, 0.50, 1.0), (0.46, 0.30, 0.30, 1.0), (0.34, 0.40, 0.34, 1.0))[(k + pos) % 3], chamfer=0.04)
                if (k + pos) % 2 == 0:
                    make_chamfer_box(f"V4Pillow_{k}_{s:+d}_{pos}", (x + s * 0.10, yy - 0.12, 1.06), (0.22, 0.10, 0.16),
                                     (0.92, 0.92, 0.90, 1.0), chamfer=0.03)
    # the galley curtain at the forward bulkhead
    make_box("Cabin_Galley_Curtain", (CX, CY0 + ROWS * PITCH + 1.1, 1.05), (0.60, 0.03, 1.90), (0.24, 0.28, 0.40, 1.0))


def main():
    clear_scene()
    build_gate()
    build_cabin()
    try:
        join_stock()
        # the seats are furniture (the gates read them under their own
        # names); one mesh per kind for the draw-call budget
        join_named("GateSeat_", "Gate_Seats")
        join_named("CabSeat_", "Cabin_Seats")
        for pre, preset in (("WinNight_", "plane_night"), ("WinDay_", "plane_day"), ("WinV4_", "plane_vol4"),
                            ("ShadeV4_", "plane_vol4"), ("V4Blanket_", "plane_vol4"), ("V4Pillow_", "plane_vol4")):
            join_named(pre, pre.rstrip("_") + "__" + preset)
        join_named("ShadeUp_", "ShadeUp__plane_night__plane_day")
    except Exception as _e:
        print("[join] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/airport_cabin.glb"))
    print(f"\n[build_airport_cabin] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
