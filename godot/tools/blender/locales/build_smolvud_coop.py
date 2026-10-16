"""smolvud_coop — the organic co-op on Smolvud's Main Street, vol7 (2026-10-10).

"The co-op opened at six. Margaret was at the front when he came in —
sixty-one years old, running the co-op since 2041, knowing Finn the way
the woman who had run a co-op for two decades knew the cyclist who
delivered the boxes. She was at the counter going through the morning's
invoices when he came in ... She put the pen down ... Bring me bread
from Hans tomorrow. The seeded kind." (vol7 ch12) — and through the
volume: Finn's "organic-co-op income", the boxes he delivers by bike,
"her apartment above the co-op", Margaret closing it for the morning.

It never had a set: ch12 played the whole visit on Main Street outside
Board Lords. This is the co-op: an old storefront on Main, 12 x 9 m under
a 3.4 m ceiling, wood floors; the big front windows on the rain and the
door with its bell; the front counter by the door with the register's
tablet, the clipboard of the morning's invoices and the pen, the scale;
the produce on tiered crates down the middle; the bulk bins and their
scoops along the W wall; two gondolas of jars, oats and coffee; the cooler
wall on the N (milk, eggs, the fish co-op's smoked salmon); Hans's bread
on its rack by the counter, the seeded loaves; the community corkboard;
by the back door the delivery crates stacked for Finn's bike, labelled;
the cargo bike under the awning outside; Main Street wet past the glass.

Coordinates: Blender Z-up, the street front on the S wall at y 0, x -6..6.
glTF export -> Godot (x, z, -y).

Draft 2 targets: the apartment stair at the back (Margaret's); Margaret's
reading glasses on the counter; the morning delivery staged on the crates.
"""
import os, sys, math, random
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_chamfer_box, make_lathe, make_tube, make_rot_box, make_blob, export_glb
from _props.structure import make_floor, make_wall, make_wall_with_openings
from _props.objects import make_bottle, make_can

W, D, H = 12.0, 9.0, 3.4
XW, XE, YS, YN = -W / 2.0, W / 2.0, 0.0, D
FW, FE, FS, FN = XW + 0.10, XE - 0.10, YS + 0.10, YN - 0.10
DOOR_X, DOOR_W, DOOR_H = 3.2, 1.1, 2.3
WIN = ((-3.2, 4.6), (0.9, 2.2))     # (centre x, width) of the two front windows
PAL = {"wall": (0.84, 0.80, 0.70, 1.0), "baseboard": (0.40, 0.30, 0.20, 1.0)}
WOOD = (0.56, 0.42, 0.28, 1.0); WOOD_DK = (0.40, 0.29, 0.19, 1.0); STEEL = (0.62, 0.64, 0.66, 1.0)
GREEN = (0.30, 0.44, 0.28, 1.0)
PRODUCE = [(0.86, 0.28, 0.20, 1.0), (0.92, 0.62, 0.20, 1.0), (0.40, 0.62, 0.26, 1.0), (0.62, 0.30, 0.46, 1.0), (0.90, 0.82, 0.36, 1.0), (0.30, 0.50, 0.24, 1.0)]


def build_shell():
    make_floor("Floor", (0.0, D / 2.0, 0.0), size_x=W + 0.4, size_y=D + 0.4, palette={"vinyl": (0.62, 0.48, 0.32, 1.0), "seam": (0.46, 0.34, 0.22, 1.0)})
    make_wall("Wall_W", (XW, D / 2.0, 0), length=D + 0.4, height=H, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_E", (XE, D / 2.0, 0), length=D + 0.4, height=H, axis='Y', palette=PAL, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_N", (0.0, YN, 0), length=W + 0.4, height=H, axis='X', palette=PAL, baseboard_face_sign=-1,
                            openings=[(4.6, 1.05, 0.95, 2.1)])
    make_wall_with_openings("Wall_S", (0.0, YS, 0), length=W + 0.4, height=H, axis='X', palette=PAL, baseboard_face_sign=+1,
                            openings=[(x, 1.75, w, 2.1) for x, w in WIN] + [(DOOR_X, DOOR_H / 2.0, DOOR_W, DOOR_H)])
    make_box("Ceil", (0.0, D / 2.0, H + 0.05), (W + 0.4, D + 0.4, 0.10), (0.80, 0.76, 0.66, 1.0))
    for i in range(5):
        make_box(f"Ceil_Joist_{i}", (0.0, 1.0 + i * 1.75, H - 0.08), (W, 0.12, 0.16), WOOD_DK)
    for i, (x, w) in enumerate(WIN):
        make_box(f"Window_{i}_Glass", (x, YS, 1.75), (w, 0.01, 2.1), (0.70, 0.78, 0.82, 0.25))
        make_box(f"Window_{i}_Sill", (x, FS + 0.07, 0.68), (w + 0.1, 0.16, 0.04), WOOD)
        rnd = random.Random(i)
        for k in range(20):
            make_box(f"Window_{i}_Rain_{k}", (x + rnd.uniform(-w / 2 + 0.1, w / 2 - 0.1), YS - 0.012, rnd.uniform(1.0, 2.6)), (0.004, 0.002, rnd.uniform(0.05, 0.16)), (0.80, 0.86, 0.92, 0.5))
    make_box("Front_Door", (DOOR_X, YS - 0.02, DOOR_H / 2.0 - 0.01), (DOOR_W - 0.04, 0.05, DOOR_H - 0.02), GREEN)
    make_box("Front_Door_Glass", (DOOR_X, YS + 0.01, 1.40), (DOOR_W - 0.34, 0.01, 1.20), (0.70, 0.78, 0.82, 0.3))
    make_box("Front_Door_Bell_Bracket", (DOOR_X + 0.40, FS + 0.03, DOOR_H + 0.12), (0.04, 0.06, 0.04), (0.30, 0.30, 0.32, 1.0))
    make_lathe("Front_Door_Bell", (DOOR_X + 0.40, FS + 0.06, DOOR_H + 0.02), [(0.0, 0.0), (0.035, 0.0), (0.025, 0.06), (0.0, 0.08)], (0.80, 0.66, 0.30, 1.0), segments=8)
    make_box("Back_Door", (4.6, FN + 0.02, 1.04), (0.91, 0.05, 2.08), WOOD_DK)
    for i, x in enumerate((-4.0, 0.0, 4.0)):
        for j, y in enumerate((2.5, 6.2)):
            make_cyl(f"Pendant_{i}_{j}_Cord", (x, y, H - 0.35), 0.006, 0.70, (0.14, 0.14, 0.16, 1.0), segments=5)
            make_lathe(f"Pendant_{i}_{j}_Shade", (x, y, H - 0.88), [(0.0, 0.18), (0.22, 0.0), (0.26, 0.02), (0.05, 0.20), (0.0, 0.20)], GREEN, segments=12)
            make_cyl(f"Pendant_{i}_{j}_Bulb", (x, y, H - 0.84), 0.05, 0.06, (1.0, 0.90, 0.66, 1.0), segments=8)


def build_counter():
    """The front counter by the door: register tablet, the morning's
    invoices on a clipboard and the pen, the scale; Hans's bread rack."""
    cx, cy = 4.4, 2.0
    make_box("Counter_Body", (cx, cy, 0.47), (2.4, 0.70, 0.94), WOOD)
    make_box("Counter_Top", (cx, cy, 0.965), (2.5, 0.78, 0.05), (0.70, 0.56, 0.38, 1.0))
    top = 0.99
    make_box("Register_Tablet_Stand", (cx + 0.6, cy + 0.10, top + 0.06), (0.10, 0.08, 0.12), (0.62, 0.62, 0.64, 1.0))
    make_box("Register_Tablet", (cx + 0.6, cy + 0.05, top + 0.18), (0.26, 0.012, 0.18), (0.12, 0.12, 0.14, 1.0))
    make_box("Register_Tablet_Screen", (cx + 0.6, cy + 0.043, top + 0.18), (0.23, 0.002, 0.15), (0.40, 0.62, 0.70, 1.0))
    make_box("Invoice_Clipboard", (cx - 0.3, cy - 0.05, top + 0.008), (0.24, 0.33, 0.012), WOOD_DK)
    make_box("Invoice_Sheets", (cx - 0.3, cy - 0.07, top + 0.016), (0.21, 0.28, 0.006), (0.94, 0.93, 0.88, 1.0))
    make_box("Invoice_Clip", (cx - 0.3, cy + 0.10, top + 0.022), (0.08, 0.03, 0.012), (0.70, 0.70, 0.72, 1.0))
    make_cyl("Margaret_Pen", (cx - 0.12, cy - 0.10, top + 0.006), 0.005, 0.14, (0.20, 0.30, 0.60, 1.0), axis='Y', segments=6)
    make_box("Produce_Scale", (cx - 0.95, cy, top + 0.06), (0.36, 0.30, 0.12), (0.86, 0.86, 0.84, 1.0))
    make_box("Produce_Scale_Pan", (cx - 0.95, cy, top + 0.13), (0.30, 0.26, 0.02), STEEL)
    make_cyl("Tip_Jar", (cx + 1.0, cy - 0.20, top + 0.07), 0.05, 0.14, (0.80, 0.86, 0.88, 0.5), segments=10)
    # Hans's bread on its rack beside the counter — the seeded loaves on top
    bx, by = FE - 0.30, cy + 1.85
    for k, z in enumerate((0.30, 0.75, 1.20)):
        make_box(f"Bread_Rack_Shelf_{k}", (bx, by, z), (0.60, 0.90, 0.03), WOOD)
        for j in range(3):
            make_chamfer_box(f"Bread_Loaf_{k}_{j}", (bx, by - 0.28 + j * 0.28, z + 0.075), (0.18, 0.24, 0.12),
                             [(0.66, 0.44, 0.24, 1.0), (0.58, 0.40, 0.22, 1.0), (0.72, 0.52, 0.30, 1.0)][k], chamfer=0.04)
    for i, (dx, dy) in enumerate(((-0.28, -0.43), (0.28, -0.43), (-0.28, 0.43), (0.28, 0.43))):
        make_box(f"Bread_Rack_Post_{i}", (bx + dx, by + dy, 0.70), (0.03, 0.03, 1.40), WOOD_DK)
    make_box("Bread_Rack_Sign", (bx, by - 0.43, 1.33), (0.56, 0.01, 0.14), (0.20, 0.20, 0.18, 1.0))


def build_floor_goods():
    """Produce on tiered crates down the middle; the gondolas; the bulk bins
    on the W wall; the cooler wall on the N."""
    rnd = random.Random(4)
    for t, (tx, ty) in enumerate(((-1.2, 3.4), (-1.2, 5.8))):
        make_box(f"Produce_Table_{t}", (tx, ty, 0.40), (3.0, 1.2, 0.80), WOOD_DK)
        for r in range(2):
            for c in range(5):
                x = tx - 1.2 + c * 0.6
                y = ty - 0.3 + r * 0.6
                z = 0.80 + r * 0.18
                make_box(f"Crate_{t}_{r}_{c}", (x, y, z + 0.09), (0.56, 0.54, 0.18), WOOD)
                col = PRODUCE[rnd.randrange(len(PRODUCE))]
                make_blob(f"Produce_{t}_{r}_{c}", (x, y, z + 0.20), 0.22, col, noise=0.4, seed=t * 10 + r * 5 + c, squash=0.35)
                make_box(f"Price_Card_{t}_{r}_{c}", (x, y - 0.28, z + 0.20), (0.12, 0.004, 0.08), (0.14, 0.14, 0.14, 1.0))
            if r == 1:
                make_box(f"Produce_Riser_{t}", (tx, ty + 0.30, 0.89), (3.0, 0.6, 0.18), WOOD_DK)
    # two gondolas of jars, oats and coffee
    for g, gx in enumerate((1.8, 3.6)):
        gy0, gy1 = 3.9, 6.6
        make_box(f"Gondola_{g}_Shelf_Spine", (gx, (gy0 + gy1) / 2.0, 0.85), (0.08, gy1 - gy0, 1.70), WOOD_DK)
        make_box(f"Gondola_{g}_Base", (gx, (gy0 + gy1) / 2.0, 0.08), (0.80, gy1 - gy0, 0.16), WOOD_DK)
        for k, z in enumerate((0.55, 1.00, 1.45)):
            for s in (-1, 1):
                make_box(f"Gondola_{g}_Shelf_{k}_{s:+d}", (gx + s * 0.20, (gy0 + gy1) / 2.0, z), (0.34, gy1 - gy0, 0.03), WOOD)
                for j in range(9):
                    y = gy0 + 0.15 + j * 0.29
                    kind = (j + k + g) % 3
                    if kind == 0:
                        make_lathe(f"Jar_{g}_{k}_{s:+d}_{j}", (gx + s * 0.22, y, z + 0.015), [(0.0, 0.0), (0.05, 0.0), (0.055, 0.12), (0.04, 0.14), (0.0, 0.14)], (0.86, 0.66, 0.30, 0.8), segments=8)
                    elif kind == 1:
                        make_box(f"Bag_{g}_{k}_{s:+d}_{j}", (gx + s * 0.22, y, z + 0.11), (0.10, 0.16, 0.19), (0.74, 0.64, 0.46, 1.0))
                    else:
                        make_can(f"Can_{g}_{k}_{s:+d}_{j}", gx + s * 0.22, y, z + 0.015, [(0.40, 0.56, 0.30, 1.0), (0.70, 0.30, 0.24, 1.0)][j % 2])
    # the bulk bins along the W wall, their scoops
    for i in range(7):
        y = 1.2 + i * 0.85
        make_box(f"Bulk_Bin_{i}", (FW + 0.30, y, 0.95), (0.56, 0.76, 0.70), (0.80, 0.84, 0.86, 0.45))
        make_box(f"Bulk_Bin_{i}_Fill", (FW + 0.30, y, 0.80), (0.52, 0.72, 0.38), [(0.80, 0.70, 0.46, 1.0), (0.56, 0.40, 0.26, 1.0), (0.90, 0.86, 0.70, 1.0), (0.36, 0.30, 0.22, 1.0)][i % 4])
        make_box(f"Bulk_Bin_{i}_Label", (FW + 0.585, y, 1.16), (0.004, 0.24, 0.06), (0.94, 0.92, 0.86, 1.0))
        make_rot_box(f"Bulk_Bin_{i}_Scoop", (FW + 0.36, y + 0.22, 1.02), (0.06, 0.14, 0.04), STEEL, roll=0.3)
    make_box("Bulk_Bin_Counter", (FW + 0.30, 3.75, 0.30), (0.60, 5.90, 0.60), WOOD_DK)
    # the cooler wall on the N, W of the back door
    cx0, cx1 = -5.6, 3.6
    make_box("Cooler_Body", ((cx0 + cx1) / 2.0, FN - 0.40, 1.05), (cx1 - cx0, 0.80, 2.10), (0.20, 0.22, 0.24, 1.0))
    for i in range(6):
        x = cx0 + (i + 0.5) * (cx1 - cx0) / 6.0
        make_box(f"Cooler_Door_{i}", (x, FN - 0.81, 1.05), ((cx1 - cx0) / 6.0 - 0.06, 0.02, 1.90), (0.76, 0.84, 0.90, 0.35))
        make_box(f"Cooler_Handle_{i}", (x + 0.55, FN - 0.84, 1.10), (0.03, 0.04, 0.50), STEEL)
        for k, z in enumerate((0.45, 0.95, 1.45)):
            for j in range(4):
                xx = x - 0.48 + j * 0.32
                if (i + k) % 3 == 0:
                    make_box(f"Cooler_Milk_{i}_{k}_{j}", (xx, FN - 0.55, z + 0.12), (0.10, 0.10, 0.24), (0.94, 0.94, 0.92, 1.0))
                elif (i + k) % 3 == 1:
                    make_box(f"Cooler_Eggs_{i}_{k}_{j}", (xx, FN - 0.55, z + 0.04), (0.28, 0.12, 0.08), (0.70, 0.62, 0.48, 1.0))
                else:
                    make_box(f"Cooler_Salmon_{i}_{k}_{j}", (xx, FN - 0.55, z + 0.02), (0.24, 0.14, 0.04), (0.92, 0.56, 0.40, 1.0))
            make_box(f"Cooler_Shelf_{i}_{k}", (x, FN - 0.50, z), ((cx1 - cx0) / 6.0 - 0.10, 0.50, 0.02), STEEL)
    make_box("Cooler_Header_Sign", ((cx0 + cx1) / 2.0, FN - 0.81, 2.25), (cx1 - cx0, 0.03, 0.30), GREEN)


def build_back_and_board():
    """The delivery crates stacked by the back door for Finn's bike; the
    community corkboard by the front door; the cargo bike outside."""
    for c in range(3):
        for k in range(3):
            y = 6.9 - c * 0.62
            make_box(f"Delivery_Crate_{c}_{k}", (FE - 0.28, y, 0.15 + k * 0.30), (0.54, 0.56, 0.30), (0.40, 0.52, 0.36, 1.0))
            make_box(f"Delivery_Crate_{c}_{k}_Label", (FE - 0.28 - 0.272, y, 0.19 + k * 0.30), (0.004, 0.24, 0.10), (0.94, 0.92, 0.86, 1.0))
    make_box("Corkboard", (FE - 0.02, 0.9, 1.55), (0.03, 1.10, 0.80), (0.62, 0.48, 0.32, 1.0))
    for i in range(7):
        make_box(f"Corkboard_Flyer_{i}", (FE - 0.04, 0.48 + (i % 4) * 0.27, 1.75 - (i // 4) * 0.36), (0.004, 0.20, 0.26),
                 [(0.94, 0.92, 0.86, 1.0), (0.96, 0.86, 0.40, 1.0), (0.70, 0.86, 0.96, 1.0)][i % 3])
    make_box("Chalkboard_Prices", (FW + 0.015, 4.2, 2.35), (0.03, 3.0, 0.70), (0.14, 0.16, 0.14, 1.0))
    for i in range(6):
        make_box(f"Chalkboard_Line_{i}", (FW + 0.032, 3.0 + (i % 2) * 1.3, 2.55 - (i // 2) * 0.18), (0.002, 0.90, 0.03), (0.92, 0.90, 0.80, 1.0))
    # outside: the sidewalk, the awning, Finn's cargo bike, the wet street
    make_box("Out_Sidewalk", (0.0, -1.8, -0.03), (30.0, 3.6, 0.06), (0.42, 0.42, 0.42, 1.0))
    make_box("Out_Street", (0.0, -8.0, -0.12), (30.0, 9.0, 0.06), (0.20, 0.20, 0.22, 1.0))
    make_rot_box("Out_Awning", (0.0, -0.75, 2.85), (W - 0.4, 1.50, 0.04), GREEN, pitch=0.0, roll=0.0)
    for i, x in enumerate((-5.6, 5.6)):
        make_box(f"Out_Awning_Bracket_{i}", (x, -0.40, 2.80), (0.04, 0.80, 0.04), (0.20, 0.20, 0.22, 1.0))
    bx, by = -1.0, -1.4
    make_box("Cargo_Bike_Box", (bx + 0.5, by, 0.55), (0.70, 0.60, 0.40), WOOD)
    for i, x in enumerate((bx + 0.5, bx - 0.9)):
        make_cyl(f"Cargo_Bike_Wheel_{i}", (x, by, 0.30), 0.30, 0.04, (0.12, 0.12, 0.13, 1.0), axis='Y', segments=14)
    make_box("Cargo_Bike_Frame", (bx - 0.20, by, 0.55), (1.30, 0.04, 0.04), (0.30, 0.42, 0.30, 1.0))
    make_box("Cargo_Bike_Seat_Post", (bx - 0.55, by, 0.75), (0.04, 0.04, 0.42), (0.30, 0.42, 0.30, 1.0))
    make_box("Cargo_Bike_Seat", (bx - 0.55, by, 0.98), (0.24, 0.10, 0.05), (0.14, 0.14, 0.16, 1.0))
    make_box("Cargo_Bike_Bars", (bx + 0.05, by, 1.00), (0.04, 0.50, 0.04), (0.20, 0.20, 0.22, 1.0))
    make_box("Cargo_Bike_Stem", (bx + 0.05, by, 0.78), (0.04, 0.04, 0.44), (0.30, 0.42, 0.30, 1.0))
    for i in range(5):
        make_box(f"Out_Facade_Across_{i}", (-10.0 + i * 5.0, -13.0, 3.5), (4.8, 0.6, 7.0), [(0.62, 0.66, 0.70, 1.0), (0.74, 0.62, 0.50, 1.0), (0.50, 0.56, 0.52, 1.0)][i % 3])


def main():
    clear_scene()
    build_shell(); build_counter(); build_floor_goods(); build_back_and_board()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/smolvud_coop.glb"))
    print(f"\n[build_smolvud_coop] exporting to {out}")
    export_glb(out)


if __name__ == "__main__": main()
