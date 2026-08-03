"""The pharmacy — vol1 ch2's workplace (the "everyday tedium" pair).

One interior, two wired vantages: the retail FLOOR with its gondola
aisles, RX counter and the mirror pillar (the ch2 mirror scene), and
the cramped back OFFICE where the manager talk happens.

Hero features: two gondola shelf runs with color-coded product bands,
wall bays, the raised RX counter at back with its high back-counter
and pill shelves, the RX sign, a full-height mirror pillar on the E
wall, checkout stand with register, and the office annex — desk,
files, paper stacks, a window looking onto the floor.

Coordinate frame: Blender Z-up. y=0 is the storefront (south) wall
with the entry; +Y runs back to the RX counter; walls at x=±4.0,
back wall y=6.0, ceiling 2.8. glTF export remaps to Godot (x,z,-y).

Vantages wired in Background3D.CAMERA_PRESETS:
  pharmacy_floor  — front of store looking N up the aisle to RX.
  pharmacy_office — inside the annex at the desk.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling

ROOM_W = 8.0   # x ∈ [-4, 4]
ROOM_D = 6.0   # y ∈ [0, 6]
CEIL = 2.8

COL_WALL = (0.62, 0.63, 0.60, 1.0)
COL_BASE = (0.34, 0.34, 0.32, 1.0)
COL_FLOOR = (0.58, 0.57, 0.52, 1.0)    # worn vinyl
COL_SEAM = (0.44, 0.43, 0.40, 1.0)
COL_CEIL = (0.66, 0.66, 0.63, 1.0)
COL_SHELF = (0.72, 0.72, 0.70, 1.0)    # white gondola steel
COL_SHELF_DK = (0.52, 0.52, 0.50, 1.0)
COL_COUNTER = (0.46, 0.40, 0.34, 1.0)
COL_RX_SIGN = (0.20, 0.42, 0.30, 1.0)  # green cross field
COL_RX_TXT = (0.88, 0.88, 0.84, 1.0)
COL_MIRROR = (0.70, 0.76, 0.80, 1.0)   # cool reflective panel
COL_MIRROR_FR = (0.30, 0.28, 0.24, 1.0)
COL_DESK = (0.40, 0.32, 0.24, 1.0)
COL_FILE = (0.44, 0.46, 0.48, 1.0)
COL_PAPER = (0.84, 0.82, 0.74, 1.0)
COL_GLASS = (0.55, 0.62, 0.66, 0.4)
COL_FLUOR = (0.94, 0.96, 0.90, 1.0)    # tube panels — bloom via glow

# Product bands cycled along shelves — reads as stocked without detail
PRODUCTS = [
    (0.66, 0.32, 0.28, 1.0), (0.30, 0.44, 0.58, 1.0), (0.72, 0.62, 0.30, 1.0),
    (0.36, 0.52, 0.38, 1.0), (0.60, 0.44, 0.56, 1.0), (0.78, 0.74, 0.66, 1.0),
]


def _stocked_run(prefix, x0, x1, y, z, seed=0):
    n = max(3, int((x1 - x0) / 0.30))
    w = (x1 - x0) / n
    for i in range(n):
        if (i + seed) % 7 == 3:
            continue
        k = (i * 5 + seed * 3) % len(PRODUCTS)
        h = 0.14 + 0.04 * ((i + seed) % 3)
        make_box(f"{prefix}_{i}", (x0 + w * (i + 0.5), y, z + h / 2.0),
                 (w * 0.8, 0.24, h), PRODUCTS[k])


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=pal, baseboard_face_sign=+1)
    make_wall("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=pal, baseboard_face_sign=-1)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=pal, baseboard_face_sign=-1)
    make_wall("Wall_S", (0.0, 0.0, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=pal, baseboard_face_sign=+1)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, with_grid=True, with_stains=False,
                 palette={"tile": COL_CEIL})
    # Storefront glass door + window, S wall
    make_box("Door", (-2.6, 0.08, 1.10), (0.95, 0.05, 2.20), COL_MIRROR_FR)
    make_box("Door_Glass", (-2.6, 0.06, 1.20), (0.70, 0.04, 1.70), COL_GLASS)
    make_box("Front_Glass", (-0.6, 0.06, 1.45), (2.4, 0.04, 1.60), COL_GLASS)
    # Fluorescent tube panels (the practicals sit on these)
    for i, fy in enumerate((1.6, 3.2, 4.8)):
        make_box(f"Fluor_{i}", (0.0, fy, CEIL - 0.03), (2.6, 0.34, 0.05), COL_FLUOR)


def build_gondolas():
    """Two double-sided gondola runs making three aisles."""
    for gi, gx in enumerate((-1.5, 1.5)):
        make_box(f"Gondola_{gi}_Base", (gx, 2.7, 0.10), (0.9, 3.0, 0.20), COL_SHELF_DK)
        make_box(f"Gondola_{gi}_Spine", (gx, 2.7, 0.85), (0.10, 3.0, 1.5), COL_SHELF)
        for zi, z in enumerate((0.35, 0.80, 1.25)):
            for side, sx in ((0, gx - 0.34), (1, gx + 0.34)):
                make_box(f"Gondola_{gi}_{side}_S{zi}", (sx, 2.7, z),
                         (0.55, 2.9, 0.035), COL_SHELF)
            _stocked_run(f"Stock_{gi}_W_{zi}", gx - 0.55, gx - 0.12, 2.7, 0.37 + zi * 0.45,
                         seed=gi * 5 + zi)
            _stocked_run(f"Stock_{gi}_E_{zi}", gx + 0.12, gx + 0.55, 2.7, 0.37 + zi * 0.45,
                         seed=gi * 7 + zi + 2)
    # W wall bays
    for zi, z in enumerate((0.40, 0.90, 1.40, 1.90)):
        make_box(f"WallBay_S{zi}", (-3.8, 3.0, z), (0.35, 4.2, 0.035), COL_SHELF)
    make_box("WallBay_Back", (-3.95, 3.0, 1.2), (0.06, 4.2, 2.4), COL_SHELF_DK)


def build_rx_counter():
    """Raised RX counter along the back, high back-counter with pill
    shelves, the green RX sign overhead."""
    make_box("RX_Counter", (-0.8, 5.15, 0.55), (4.4, 0.7, 1.10), COL_COUNTER)
    make_box("RX_Top", (-0.8, 5.15, 1.13), (4.5, 0.8, 0.06), (0.58, 0.52, 0.44, 1.0))
    make_box("RX_Back", (-0.8, 5.85, 1.10), (4.6, 0.10, 2.20), COL_SHELF_DK)
    for zi, z in enumerate((1.35, 1.70, 2.05)):
        make_box(f"RX_Shelf_{zi}", (-0.8, 5.76, z), (4.4, 0.22, 0.03), COL_SHELF)
        _stocked_run(f"RX_Stock_{zi}", -2.9, 1.3, 5.76, z + 0.02, seed=11 + zi)
    make_box("RX_Sign", (-0.8, 5.90, 2.50), (1.4, 0.08, 0.5), COL_RX_SIGN)
    make_box("RX_Sign_Txt", (-0.8, 5.85, 2.50), (0.8, 0.05, 0.22), COL_RX_TXT)
    # Register on the counter's east end
    make_box("Register", (0.9, 5.05, 1.32), (0.40, 0.32, 0.30), COL_MIRROR_FR)


def build_mirror():
    """The full-height mirror pillar, E wall mid-store — the ch2
    mirror scene stands here."""
    make_box("Mirror_Frame", (3.92, 2.8, 1.30), (0.08, 0.85, 2.30), COL_MIRROR_FR)
    make_box("Mirror_Glass", (3.88, 2.8, 1.30), (0.05, 0.70, 2.10), COL_MIRROR)


def build_office():
    """Back-office annex, NE corner: partition, desk, files, paper."""
    make_box("Office_Part_S", (3.0, 4.5, 1.15), (2.0, 0.08, 2.3), COL_WALL)
    make_box("Office_Part_Win", (3.0, 4.5, 1.65), (1.2, 0.06, 0.7), COL_GLASS)
    make_box("Office_Part_W", (2.0, 5.25, 1.15), (0.08, 1.5, 2.3), COL_WALL)
    # Desk against the N wall
    make_box("Office_Desk", (3.2, 5.60, 0.72), (1.3, 0.65, 0.06), COL_DESK)
    for lx in (2.65, 3.75):
        make_box(f"Office_DeskLeg_{lx:.2f}", (lx, 5.60, 0.36), (0.06, 0.6, 0.72), COL_DESK)
    # The computer (canon: "sits down at the computer") — beige CRT
    # + keyboard — plus his coffee and the pill bottle
    make_box("Office_CRT", (3.35, 5.68, 0.95), (0.42, 0.40, 0.38), (0.74, 0.70, 0.60, 1.0))
    make_box("Office_Screen", (3.35, 5.47, 0.96), (0.30, 0.02, 0.24), (0.30, 0.42, 0.38, 1.0))
    make_box("Office_Keyboard", (3.35, 5.38, 0.77), (0.36, 0.14, 0.03), (0.66, 0.62, 0.54, 1.0))
    make_cyl("Office_Coffee", (2.95, 5.42, 0.80), 0.045, 0.10, (0.50, 0.28, 0.22, 1.0), segments=8)
    make_cyl("Pill_Bottle", (3.68, 5.44, 0.79), 0.035, 0.09, (0.78, 0.56, 0.28, 1.0), segments=8)
    make_box("Office_Papers", (2.75, 5.68, 0.78), (0.4, 0.3, 0.08), COL_PAPER)
    make_box("Office_Ledger", (3.75, 5.66, 0.77), (0.28, 0.20, 0.04), (0.30, 0.24, 0.20, 1.0))
    make_cyl("Office_Lamp_Post", (3.75, 5.75, 0.92), 0.018, 0.34, COL_MIRROR_FR, segments=6)
    make_box("Office_Lamp_Shade", (3.70, 5.72, 1.10), (0.22, 0.14, 0.08), (0.30, 0.34, 0.28, 1.0))
    # File cabinet + chair
    make_box("Office_File", (2.35, 5.70, 0.65), (0.45, 0.55, 1.30), COL_FILE)
    for d in range(3):
        make_box(f"Office_File_D{d}", (2.35, 5.42, 0.28 + d * 0.42), (0.38, 0.03, 0.32), COL_SHELF_DK)
    make_box("Office_Chair_Seat", (3.1, 4.95, 0.46), (0.42, 0.42, 0.06), COL_MIRROR_FR)
    make_box("Office_Chair_Back", (3.1, 5.15, 0.80), (0.42, 0.05, 0.55), COL_MIRROR_FR)


def build_checkout():
    """Checkout stand near the door."""
    make_box("Checkout", (-2.7, 1.3, 0.50), (0.9, 0.6, 1.00), COL_COUNTER)
    make_box("Checkout_Top", (-2.7, 1.3, 1.03), (1.0, 0.7, 0.05), (0.58, 0.52, 0.44, 1.0))
    make_box("Checkout_Reg", (-2.7, 1.45, 1.22), (0.36, 0.28, 0.28), COL_MIRROR_FR)
    make_cyl("Gum_Rack", (-2.3, 0.95, 0.70), 0.12, 1.35, COL_SHELF, segments=8)


def main():
    clear_scene()
    build_shell()
    build_gondolas()
    build_rx_counter()
    build_mirror()
    build_office()
    build_checkout()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/pharmacy.glb"))
    print(f"\n[build_pharmacy] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
