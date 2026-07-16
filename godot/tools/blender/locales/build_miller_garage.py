"""Chief Miller's garage — vol6 — Harmony Creek Estates.

Canon (vol6 ch1): Sunday 17:02, dusk. Sam pulls in; her father is in the
garage, on the phone, speaking quietly. A tidy suburban two-car garage
turned one man's ordered domain: a workbench with a pegboard of tools
and a bench vise down the E wall, gray steel shelving of labeled bins +
paint cans down the W wall, a rolling red tool chest, a water heater and
furnace in the NW corner, a chest freezer, a bicycle, a push mower, and
the segmented roll-up door across the S. Concrete floor with old oil
stains. The light is a cool hanging fluorescent + a warm dusk spill
leaking under the cracked garage door (miller_garage.tscn does the rig).

Coordinate frame: Blender Z-up. Interior y 0 (S / garage-door wall) → +Y
(N), walls x = ±ROOM_W/2, ceiling CEIL. glTF remaps to Godot (x, z, -y).
make_box / make_cyl only.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling

ROOM_W = 5.4      # x ∈ [-2.7, 2.7]  (two-car width)
ROOM_D = 5.6      # y ∈ [0, 5.6]
CEIL = 2.5

COL_FLOOR = (0.42, 0.42, 0.44, 1.0)
COL_STAIN = (0.20, 0.19, 0.20, 1.0)
COL_SEAM = (0.30, 0.30, 0.32, 1.0)
COL_WALL = (0.58, 0.56, 0.50, 1.0)      # painted garage drywall
COL_BASE = (0.40, 0.38, 0.34, 1.0)
COL_DOOR = (0.72, 0.72, 0.70, 1.0)      # roll-up door panels
COL_DOOR_SEAM = (0.52, 0.52, 0.50, 1.0)
COL_BENCH = (0.46, 0.34, 0.22, 1.0)
COL_BENCH_DK = (0.32, 0.23, 0.15, 1.0)
COL_STEEL = (0.50, 0.52, 0.55, 1.0)
COL_STEEL_DK = (0.30, 0.31, 0.34, 1.0)
COL_PEG = (0.72, 0.60, 0.40, 1.0)       # pegboard
COL_TOOL = (0.20, 0.20, 0.22, 1.0)
COL_BIN_B = (0.24, 0.36, 0.56, 1.0)
COL_BIN_R = (0.60, 0.26, 0.22, 1.0)
COL_BIN_Y = (0.72, 0.62, 0.24, 1.0)
COL_CAN = (0.66, 0.66, 0.64, 1.0)
COL_WHITE = (0.80, 0.80, 0.78, 1.0)
COL_REDCHEST = (0.60, 0.20, 0.18, 1.0)
COL_FLUOR = (0.94, 0.96, 0.98, 1.0)
COL_TIRE = (0.12, 0.12, 0.13, 1.0)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # a couple of oil stains
    for si, (sx, sy) in enumerate([(0.6, 2.2), (-0.9, 3.4), (0.2, 1.4)]):
        make_box(f"Stain_{si}", (sx, sy, 0.005), (0.5, 0.7, 0.002), COL_STAIN)
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
                  axis='Y', palette=pal, baseboard_face_sign=bb, with_baseboard=False)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=pal, baseboard_face_sign=-1, with_baseboard=False)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, with_grid=False, with_stains=False)
    # ── Segmented roll-up garage door across the S wall (y≈0) ──
    for pi in range(4):
        pz = 0.30 + pi * 0.56
        make_box(f"GarageDoor_Panel_{pi}", (0.0, 0.06, pz), (ROOM_W - 0.1, 0.10, 0.52), COL_DOOR)
        make_box(f"GarageDoor_Seam_{pi}", (0.0, 0.005, pz - 0.28), (ROOM_W - 0.1, 0.04, 0.03), COL_DOOR_SEAM)
        # window lites in the top panel
        if pi == 3:
            for wj in range(4):
                make_box(f"GarageDoor_Lite_{wj}", (-1.8 + wj * 1.2, 0.02, pz), (0.7, 0.02, 0.30),
                         (0.44, 0.40, 0.34, 0.7))
    make_box("GarageDoor_Track_L", (-ROOM_W / 2.0 + 0.08, 0.14, CEIL / 2.0), (0.06, 0.06, CEIL), COL_STEEL_DK)
    make_box("GarageDoor_Track_R", (ROOM_W / 2.0 - 0.08, 0.14, CEIL / 2.0), (0.06, 0.06, CEIL), COL_STEEL_DK)
    # warm dusk gap under the door (a bright thin strip that blooms)
    make_box("Door_DuskGap", (0.0, 0.02, 0.03), (ROOM_W - 0.6, 0.02, 0.03), (1.0, 0.72, 0.42, 1.0))


def build_workbench():
    """E-wall workbench: thick top + metal legs, a bench vise, a pegboard
    of tool silhouettes, a shop-rag, jars of hardware."""
    bx = ROOM_W / 2.0 - 0.36
    top_z = 0.90
    y0, y1 = 1.0, 4.4
    by = (y0 + y1) / 2.0
    make_box("Bench_Top", (bx, by, top_z), (0.62, y1 - y0, 0.06), COL_BENCH)
    make_box("Bench_Lip", (bx - 0.30, by, top_z - 0.02), (0.03, y1 - y0, 0.10), COL_BENCH_DK)
    for ly in (y0 + 0.2, y1 - 0.2):
        for lx in (bx - 0.24, bx + 0.24):
            make_box(f"Bench_Leg_{lx:.1f}_{ly:.1f}", (lx, ly, top_z / 2.0), (0.05, 0.05, top_z), COL_STEEL_DK)
    make_box("Bench_LowShelf", (bx, by, 0.30), (0.56, y1 - y0 - 0.2, 0.03), COL_BENCH_DK)
    # Bench vise
    make_box("Vise_Body", (bx - 0.10, y0 + 0.4, top_z + 0.10), (0.16, 0.20, 0.12), COL_STEEL_DK)
    make_box("Vise_Jaw", (bx - 0.10, y0 + 0.30, top_z + 0.10), (0.16, 0.06, 0.10), COL_STEEL)
    # Pegboard above the bench with tool silhouettes
    pbx = ROOM_W / 2.0 - 0.06
    make_box("Pegboard", (pbx, by, 1.62), (0.03, y1 - y0 - 0.2, 0.9), COL_PEG)
    tool_specs = [(-1.0, 0.5, 0.04), (-0.4, 0.3, 0.03), (0.2, 0.6, 0.05), (0.8, 0.4, 0.03), (1.2, 0.5, 0.06)]
    for ti, (toff, th, tw) in enumerate(tool_specs):
        make_box(f"Tool_{ti}", (pbx - 0.02, by + toff, 1.62, ), (0.01, tw, th), COL_TOOL)
    # Jars of hardware on the bench
    for ji in range(3):
        make_cyl(f"Jar_{ji}", (bx + 0.10, y1 - 0.4 - ji * 0.22, top_z + 0.10), 0.05, 0.14,
                 (0.66, 0.72, 0.70, 0.7), segments=8)
    make_box("ShopRag", (bx + 0.05, by + 0.3, top_z + 0.03), (0.20, 0.24, 0.02), COL_BIN_R)


def build_shelving():
    """W-wall gray steel shelving: labeled bins + stacked paint cans +
    cardboard boxes."""
    sx = -ROOM_W / 2.0 + 0.32
    y0, y1 = 1.0, 4.6
    for post_y in (y0, y1):
        for px in (sx - 0.22, sx + 0.22):
            make_box(f"Shelf_Post_{post_y:.1f}_{px:.1f}", (px, post_y, CEIL / 2.0 - 0.2),
                     (0.05, 0.05, CEIL - 0.4), COL_STEEL_DK)
    for si, sz in enumerate((0.5, 1.0, 1.5, 2.0)):
        make_box(f"Shelf_Deck_{si}", (sx, (y0 + y1) / 2.0, sz), (0.5, y1 - y0, 0.03), COL_STEEL)
        for bi in range(6):
            by = y0 + 0.3 + bi * 0.58
            if (si + bi) % 3 == 0:
                col = [COL_BIN_B, COL_BIN_R, COL_BIN_Y][(si + bi) % 3]
                make_box(f"Bin_{si}_{bi}", (sx, by, sz + 0.16), (0.40, 0.44, 0.24), col)
                make_box(f"BinLabel_{si}_{bi}", (sx - 0.21, by, sz + 0.16), (0.005, 0.20, 0.10), COL_WHITE)
            elif (si + bi) % 3 == 1:
                make_cyl(f"PaintCan_{si}_{bi}", (sx, by, sz + 0.13), 0.10, 0.22, COL_CAN, segments=10)
                make_cyl(f"PaintCan_Lid_{si}_{bi}", (sx, by, sz + 0.24), 0.10, 0.02, COL_STEEL_DK, segments=10)
            else:
                make_box(f"Box_{si}_{bi}", (sx, by, sz + 0.14), (0.42, 0.42, 0.24), (0.62, 0.50, 0.36, 1.0))


def build_appliances():
    """NW corner: water heater + a furnace box; a chest freezer along the
    N wall; a rolling red tool chest; a bike + a push mower on the floor."""
    # Water heater (tall white cylinder) NW corner
    make_cyl("WaterHeater", (-ROOM_W / 2.0 + 0.45, ROOM_D - 0.5, 0.75), 0.30, 1.5, COL_WHITE, segments=14)
    make_cyl("WaterHeater_Top", (-ROOM_W / 2.0 + 0.45, ROOM_D - 0.5, 1.52), 0.30, 0.06, COL_STEEL_DK, segments=14)
    make_cyl("WaterHeater_Flue", (-ROOM_W / 2.0 + 0.45, ROOM_D - 0.5, 1.9), 0.05, 0.6, COL_STEEL, segments=8)
    # Furnace box next to it
    make_box("Furnace", (-ROOM_W / 2.0 + 1.15, ROOM_D - 0.5, 0.85), (0.6, 0.6, 1.7), COL_STEEL)
    make_box("Furnace_Vent", (-ROOM_W / 2.0 + 1.15, ROOM_D - 0.82, 0.9), (0.44, 0.02, 0.5), COL_STEEL_DK)
    # Chest freezer along the N wall (center)
    make_box("Freezer", (0.7, ROOM_D - 0.45, 0.44), (1.1, 0.6, 0.88), COL_WHITE)
    make_box("Freezer_Lid", (0.7, ROOM_D - 0.45, 0.90), (1.12, 0.62, 0.06), (0.86, 0.86, 0.84, 1.0))
    make_box("Freezer_Handle", (0.7, ROOM_D - 0.76, 0.86), (0.30, 0.04, 0.04), COL_STEEL_DK)
    # Rolling red tool chest (E side, S end)
    tx = ROOM_W / 2.0 - 0.5
    make_box("ToolChest", (tx, 0.8, 0.55), (0.56, 0.44, 1.02), COL_REDCHEST)
    for dz in (0.30, 0.55, 0.80):
        make_box(f"ToolChest_Drawer_{dz}", (tx - 0.28, 0.8, dz), (0.02, 0.38, 0.14), (0.42, 0.14, 0.13, 1.0))
        make_box(f"ToolChest_Pull_{dz}", (tx - 0.29, 0.8, dz), (0.01, 0.20, 0.03), COL_STEEL)
    for cx2 in (-0.2, 0.2):
        make_cyl(f"ToolChest_Caster_{cx2}", (tx + cx2, 0.8, 0.04), 0.04, 0.05, COL_TOOL, segments=6, axis='X')
    # Bicycle leaning on the W wall (simple: two wheels + frame bars)
    bkx = -ROOM_W / 2.0 + 0.5
    for wy, nm in [(1.3, "Front"), (2.1, "Rear")]:
        make_cyl(f"Bike_Wheel_{nm}", (bkx, wy, 0.34), 0.32, 0.04, COL_TIRE, segments=16, axis='Y')
        make_cyl(f"Bike_Hub_{nm}", (bkx, wy, 0.34), 0.05, 0.05, COL_STEEL, segments=8, axis='Y')
    make_box("Bike_Frame", (bkx + 0.02, 1.7, 0.55), (0.06, 0.9, 0.10), COL_BIN_B)
    make_box("Bike_Seat", (bkx, 2.1, 0.74), (0.10, 0.22, 0.05), COL_TOOL)
    make_box("Bike_Bars", (bkx, 1.3, 0.72), (0.10, 0.30, 0.05), COL_STEEL_DK)
    # Push mower on the floor (center-S)
    make_box("Mower_Deck", (-0.6, 1.3, 0.22), (0.5, 0.56, 0.18), COL_BIN_R)
    for mw in (-0.22, 0.22):
        for my in (1.05, 1.55):
            make_cyl(f"Mower_Wheel_{mw}_{my}", (-0.6 + mw, my, 0.12), 0.11, 0.06, COL_TOOL, segments=10, axis='Y')
    make_box("Mower_Handle", (-0.6, 0.85, 0.62), (0.44, 0.5, 0.04), COL_STEEL_DK)


def build_shoplight():
    """Hanging twin-tube fluorescent shop light over the bay + a couple of
    ceiling joists to catch it."""
    lx, ly = 0.0, ROOM_D / 2.0
    for cy in (2.0, 4.0):
        make_box(f"Joist_{cy}", (0.0, cy, CEIL - 0.04), (ROOM_W - 0.2, 0.10, 0.08), COL_BENCH_DK)
    make_box("ShopLight_Body", (lx, ly, CEIL - 0.18), (0.24, 1.30, 0.10), COL_STEEL)
    make_box("ShopLight_Tube_L", (lx - 0.06, ly, CEIL - 0.24), (0.05, 1.24, 0.05), COL_FLUOR)
    make_box("ShopLight_Tube_R", (lx + 0.06, ly, CEIL - 0.24), (0.05, 1.24, 0.05), COL_FLUOR)
    for chy in (ly - 0.5, ly + 0.5):
        make_cyl(f"ShopLight_Chain_{chy}", (lx, chy, CEIL - 0.10), 0.006, 0.16, COL_STEEL_DK, segments=4)


def main():
    clear_scene()
    build_shell()
    build_workbench()
    build_shelving()
    build_appliances()
    build_shoplight()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/miller_garage.glb"))
    print(f"\n[build_miller_garage] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
