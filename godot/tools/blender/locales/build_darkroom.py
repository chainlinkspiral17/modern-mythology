"""Home darkroom — vol6 placement script.

A generic home photographic darkroom, reusable for any darkroom scene.
First use: vol6 ch0 prelude, Rick Salazar developing photographs in a
converted half-bath off the garage at 3017 Verbena Way (canon: original
1974 avocado tile). Small, cramped, light-tight. The look is
RED-AND-BLACK by design: matte-black walls +
dark floor, and the only practical is the red safelight dome on the
east wall (the tscn's Omni sits at Safelight_Dome). Vertex colors carry
believable albedo (white enamel trays, steel enlarger, amber chemistry,
near-white prints); the red safelight + red/black environment in
darkroom.tscn paint the room. Bright-red parts (safelight dome, enlarger
red filter) are tuned to bloom through the environment glow.

Hero props: the wet bench (three developing trays: developer / stop /
fix, with tongs and a print floating in the developer), the enlarger on
the north bench (baseboard + column + lamphouse + bellows + lens +
focus knob), the print washer sink, the drying line of hanging prints
across the room, the GraLab-style timer, amber chemistry on a shelf, the
light-tight door with its blackout curtain.

Coordinate frame: Blender Z-up. Interior y 0 (south door wall) → +Y
(north), walls at x = ±ROOM_W/2. Ceiling at CEIL. glTF export remaps to
Godot (x, z, -y). Ref: a home 8×10 wet darkroom converted from a linen
closet — bench heights ~0.90 m, GraLab 300 timer, Paterson trays.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling

# ── Cramped converted-closet footprint ──
ROOM_W = 2.6      # x ∈ [-1.3, 1.3]
ROOM_D = 3.4      # y ∈ [0, 3.4]  (door/S wall at y=0)
CEIL = 2.4

# ── Palette (albedo; the red safelight does the tinting) ──
COL_WALL = (0.06, 0.06, 0.07, 1.0)      # matte black wall
COL_BASE = (0.03, 0.03, 0.04, 1.0)      # near-black baseboard
COL_FLOOR = (0.09, 0.08, 0.08, 1.0)     # dark sealed concrete
COL_SEAM = (0.04, 0.04, 0.05, 1.0)
COL_BENCH = (0.20, 0.15, 0.11, 1.0)     # dark stained plywood bench
COL_BENCH_DK = (0.14, 0.10, 0.08, 1.0)
COL_STEEL = (0.32, 0.33, 0.36, 1.0)
COL_STEEL_DK = (0.16, 0.16, 0.18, 1.0)
COL_ENAMEL = (0.84, 0.84, 0.86, 1.0)    # white tray enamel
COL_TONG = (0.72, 0.60, 0.28, 1.0)      # bamboo tongs
COL_PRINT = (0.82, 0.82, 0.84, 1.0)     # photographic paper
COL_PRINT_IMG = (0.30, 0.30, 0.33, 1.0) # the exposed image on a print
COL_AMBER = (0.52, 0.28, 0.10, 0.92)    # amber chemistry bottle
COL_SAFERED = (0.90, 0.11, 0.09, 1.0)   # bright red — blooms via glow
COL_SAFERED_DIM = (0.46, 0.06, 0.05, 1.0)
COL_CURTAIN = (0.05, 0.04, 0.05, 1.0)
COL_WATER = (0.12, 0.13, 0.15, 1.0)     # sink water (dark under red)

# Developing-tray liquids — three subtly different tints so the trio
# reads as three chemistries, not one.
COL_DEV = (0.16, 0.11, 0.10, 1.0)
COL_STOP = (0.11, 0.13, 0.10, 1.0)
COL_FIX = (0.10, 0.11, 0.15, 1.0)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
                  axis='Y', palette=pal, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=pal, baseboard_face_sign=-1)
    # South wall split around a doorway (light-tight door + curtain)
    make_wall("Wall_S_W", (-(ROOM_W / 4.0 + 0.35), 0.0, 0),
              length=ROOM_W / 2.0 - 0.70, height=CEIL, axis='X', palette=pal)
    make_wall("Wall_S_E", (+(ROOM_W / 4.0 + 0.35), 0.0, 0),
              length=ROOM_W / 2.0 - 0.70, height=CEIL, axis='X', palette=pal)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.28), (1.5, 0.20, 0.56), COL_WALL)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, with_grid=False, with_stains=False)
    # Blackout curtain hung across the doorway (south)
    make_box("Curtain", (0.0, 0.14, 1.05), (1.30, 0.04, 2.05), COL_CURTAIN)
    make_box("Curtain_Rod", (0.0, 0.14, 2.12), (1.40, 0.03, 0.03), COL_STEEL_DK)
    # A couple of vertical folds so the curtain isn't a flat slab
    for fi, fx in enumerate((-0.42, -0.10, 0.24, 0.52)):
        make_box(f"Curtain_Fold_{fi}", (fx, 0.11, 1.05), (0.05, 0.03, 2.02), COL_BASE)


def build_wet_bench():
    """West-wall wet side: counter + three developing trays + tongs +
    a print floating in the developer + a chemistry shelf above."""
    bx = -1.02
    top_z = 0.86
    y0, y1 = 0.55, 2.75
    by = (y0 + y1) / 2.0
    depth = 0.52
    # Counter top + a raised back splash + a front lip (spill guard)
    make_box("WetBench_Top", (bx, by, top_z), (depth, y1 - y0, 0.05), COL_BENCH)
    make_box("WetBench_Splash", (bx - depth / 2.0 + 0.02, by, top_z + 0.16),
             (0.03, y1 - y0, 0.28), COL_BENCH_DK)
    make_box("WetBench_Lip", (bx + depth / 2.0 - 0.01, by, top_z + 0.03),
             (0.02, y1 - y0, 0.06), COL_BENCH_DK)
    for sgn, ly in [(-1, y0 + 0.15), (+1, y1 - 0.15)]:
        make_box(f"WetBench_Leg_{sgn:+d}", (bx, ly, top_z / 2.0),
                 (depth - 0.06, 0.05, top_z), COL_BENCH_DK)
    # ── Three trays in a row (dev → stop → fix) ──
    tray_ys = [y0 + 0.42, by, y1 - 0.42]
    tray_liq = [COL_DEV, COL_STOP, COL_FIX]
    tray_names = ["Dev", "Stop", "Fix"]
    for ti in range(3):
        ty = tray_ys[ti]
        tz = top_z + 0.05
        # enamel tray shell (open top) + a shallow chemistry surface
        make_box(f"Tray_{tray_names[ti]}", (bx, ty, tz + 0.03),
                 (0.40, 0.52, 0.06), COL_ENAMEL, open_faces={"+Z"})
        make_box(f"Tray_{tray_names[ti]}_Liquid", (bx, ty, tz + 0.035),
                 (0.34, 0.46, 0.025), tray_liq[ti])
    # A print floating face-up in the developer (the image "coming up")
    make_box("Tray_Dev_Print", (bx, tray_ys[0], top_z + 0.10),
             (0.22, 0.30, 0.004), COL_PRINT)
    make_box("Tray_Dev_Print_Img", (bx, tray_ys[0], top_z + 0.103),
             (0.16, 0.22, 0.002), COL_PRINT_IMG)
    # Bamboo print tongs resting on the splash
    for k in range(2):
        make_box(f"Tongs_{k}", (bx - 0.10 + k * 0.05, y0 + 0.05, top_z + 0.12),
                 (0.02, 0.24, 0.01), COL_TONG)
    # ── Chemistry shelf above the bench (amber bottles) ──
    make_box("ChemShelf", (-1.16, by, 1.62), (0.24, y1 - y0 - 0.3, 0.03), COL_BENCH_DK)
    make_box("ChemShelf_Bracket_0", (-1.16, y0 + 0.2, 1.50), (0.20, 0.03, 0.20), COL_STEEL_DK)
    make_box("ChemShelf_Bracket_1", (-1.16, y1 - 0.2, 1.50), (0.20, 0.03, 0.20), COL_STEEL_DK)
    for bi, byb in enumerate((y0 + 0.20, y0 + 0.62, by + 0.15, y1 - 0.25)):
        h = 0.24 + 0.04 * (bi % 2)
        make_cyl(f"ChemBottle_{bi}", (-1.16, byb, 1.64 + h / 2.0), 0.055, h,
                 COL_AMBER, segments=8)
        make_cyl(f"ChemBottle_{bi}_Cap", (-1.16, byb, 1.64 + h + 0.02), 0.03, 0.04,
                 COL_STEEL_DK, segments=6)
        # a pale hand-written label band
        make_box(f"ChemBottle_{bi}_Label", (-1.10, byb, 1.70 + h / 2.0),
                 (0.005, 0.08, 0.10), COL_PRINT)


def build_dry_bench():
    """North-wall dry side: the enlarger (hero prop) + the print washer
    sink + a light-tight paper safe underneath + the GraLab timer."""
    ny = ROOM_D - 0.30          # bench sits against north wall
    top_z = 0.88
    make_box("DryBench_Top", (0.0, ny, top_z), (ROOM_W - 0.3, 0.54, 0.06), COL_BENCH)
    for lx in (-ROOM_W / 2.0 + 0.45, ROOM_W / 2.0 - 0.45):
        make_box(f"DryBench_Leg_{lx:+.1f}", (lx, ny, top_z / 2.0),
                 (0.06, 0.5, top_z), COL_BENCH_DK)
    # Light-tight paper safe under the bench
    make_box("PaperSafe", (-0.55, ny, 0.34), (0.44, 0.44, 0.30), COL_STEEL_DK)
    make_box("PaperSafe_Door", (-0.55, ny - 0.24, 0.34), (0.36, 0.02, 0.24), COL_STEEL)
    make_box("PaperSafe_Handle", (-0.55, ny - 0.26, 0.34), (0.10, 0.02, 0.02), COL_TONG)

    # ── ENLARGER (hero) — baseboard, column, carriage, lamphouse,
    #    negative stage, bellows, lens, focus knob ──
    ex, ey = -0.35, ny + 0.02
    base_top = top_z + 0.06
    make_box("Enlarger_Baseboard", (ex, ey, base_top), (0.42, 0.42, 0.04), COL_BENCH_DK)
    # Column — square steel post rising from the back of the baseboard
    col_y = ey + 0.16
    make_box("Enlarger_Column", (ex, col_y, base_top + 0.62), (0.06, 0.06, 1.24), COL_STEEL)
    make_box("Enlarger_Column_Foot", (ex, col_y, base_top + 0.03), (0.14, 0.14, 0.04), COL_STEEL_DK)
    # Carriage clamp riding the column, holding the head out over the board
    car_z = base_top + 0.92
    make_box("Enlarger_Carriage", (ex, col_y - 0.02, car_z), (0.10, 0.12, 0.14), COL_STEEL_DK)
    make_box("Enlarger_Arm", (ex, ey + 0.02, car_z), (0.08, 0.30, 0.06), COL_STEEL)
    head_y = ey - 0.04
    # Lamphouse (the big head)
    make_box("Enlarger_Lamphouse", (ex, head_y, car_z + 0.05), (0.24, 0.22, 0.22), COL_STEEL_DK)
    make_box("Enlarger_Lamphouse_Vent", (ex, head_y, car_z + 0.18), (0.18, 0.16, 0.03), COL_STEEL)
    # Negative stage
    make_box("Enlarger_NegStage", (ex, head_y, car_z - 0.09), (0.22, 0.20, 0.03), COL_STEEL)
    # Bellows (tapered box stack down to the lens)
    for k in range(4):
        s = 0.18 - k * 0.02
        make_box(f"Enlarger_Bellows_{k}", (ex, head_y, car_z - 0.14 - k * 0.03),
                 (s, s, 0.03), COL_BASE)
    # Lens
    make_cyl("Enlarger_Lens", (ex, head_y, car_z - 0.30), 0.05, 0.06, COL_STEEL_DK, segments=10)
    make_cyl("Enlarger_Lens_Glass", (ex, head_y, car_z - 0.33), 0.038, 0.01,
             (0.20, 0.22, 0.26, 1.0), segments=10)
    # Red filter swung under the lens (the safelight-compatible printing filter)
    make_cyl("Enlarger_RedFilter", (ex + 0.10, head_y, car_z - 0.31), 0.05, 0.008,
             COL_SAFERED, segments=8)
    make_box("Enlarger_Filter_Arm", (ex + 0.05, head_y, car_z - 0.31),
             (0.10, 0.02, 0.01), COL_STEEL_DK)
    # Focus knob on the carriage
    make_cyl("Enlarger_FocusKnob", (ex + 0.09, col_y, car_z - 0.10), 0.035, 0.03,
             COL_TONG, segments=8, axis='X')
    # A test-strip easel + printing paper on the baseboard
    make_box("Enlarger_Easel", (ex, ey - 0.06, base_top + 0.03), (0.26, 0.20, 0.02), COL_STEEL_DK)
    make_box("Enlarger_Paper", (ex, ey - 0.06, base_top + 0.045), (0.18, 0.13, 0.004), COL_PRINT)

    # ── Print washer sink (east end of the bench) ──
    sx = 0.72
    make_box("Sink_Basin", (sx, ny, top_z + 0.10), (0.5, 0.46, 0.16), COL_STEEL,
             open_faces={"+Z"})
    make_box("Sink_Water", (sx, ny, top_z + 0.13), (0.44, 0.40, 0.06), COL_WATER)
    # Prints washing in the tray
    for k in range(3):
        make_box(f"Sink_Print_{k}", (sx - 0.12 + k * 0.11, ny + 0.04, top_z + 0.15),
                 (0.14, 0.18, 0.003), COL_PRINT)
    # Faucet + a thin water stream
    make_cyl("Sink_Faucet", (sx, ny + 0.20, top_z + 0.24), 0.02, 0.14, COL_STEEL_DK, segments=6)
    make_cyl("Sink_Faucet_Neck", (sx, ny + 0.14, top_z + 0.30), 0.02, 0.12, COL_STEEL_DK,
             segments=6, axis='Y')
    make_cyl("Sink_Stream", (sx, ny + 0.08, top_z + 0.20), 0.006, 0.14,
             (0.5, 0.55, 0.6, 0.7), segments=5)

    # ── GraLab-style timer on the north wall above the enlarger ──
    tz = 1.86
    make_cyl("Timer_Body", (ex, ROOM_D - 0.03, tz), 0.11, 0.05, COL_STEEL_DK,
             segments=14, axis='Y')
    make_cyl("Timer_Face", (ex, ROOM_D - 0.075, tz), 0.095, 0.01,
             (0.90, 0.88, 0.80, 1.0), segments=14, axis='Y')
    # a red sweep hand
    make_box("Timer_Hand", (ex + 0.02, ROOM_D - 0.085, tz + 0.03),
             (0.012, 0.006, 0.07), COL_SAFERED)


def build_drying_line():
    """A string across the room (west→east) with clipped prints drying."""
    ly = 1.35
    lz = 1.98
    make_cyl("DryLine", (0.0, ly, lz), 0.004, ROOM_W - 0.1, COL_PRINT, segments=4, axis='X')
    xs = [-0.95, -0.55, -0.12, 0.30, 0.72, 1.05]
    for i, px in enumerate(xs):
        drop = 0.02 * ((i % 3))
        # clothespin/clip
        make_box(f"DryClip_{i}", (px, ly, lz - 0.02), (0.03, 0.02, 0.05), COL_TONG)
        # hanging print (paper) with an image area, slight size variety
        pw = 0.20 + 0.03 * (i % 2)
        ph = 0.26 + 0.03 * ((i + 1) % 2)
        make_box(f"DryPrint_{i}", (px, ly + 0.01, lz - 0.06 - ph / 2.0 - drop),
                 (pw, 0.004, ph), COL_PRINT)
        make_box(f"DryPrint_{i}_Img", (px, ly + 0.013, lz - 0.06 - ph / 2.0 - drop),
                 (pw - 0.05, 0.002, ph - 0.06),
                 (0.28 + 0.06 * (i % 3), 0.28, 0.32 - 0.04 * (i % 2), 1.0))


def build_safelight():
    """The hero red safelight, wall-mounted high on the EAST wall. The
    tscn OmniLight sits at Safelight_Dome. Bright red so the environment
    glow blooms it into the room."""
    sx = ROOM_W / 2.0 - 0.06
    sy = ROOM_D * 0.55
    sz = 2.02
    # bracket off the wall
    make_box("Safelight_Bracket", (sx - 0.06, sy, sz), (0.10, 0.06, 0.06), COL_STEEL_DK)
    # housing
    make_box("Safelight_Housing", (sx - 0.16, sy, sz), (0.10, 0.16, 0.16), COL_STEEL_DK)
    # the red dome/lens facing into the room (-X)
    make_cyl("Safelight_Dome", (sx - 0.23, sy, sz), 0.09, 0.05, COL_SAFERED,
             segments=12, axis='X')
    make_cyl("Safelight_Lens", (sx - 0.255, sy, sz), 0.075, 0.01,
             (0.98, 0.20, 0.16, 1.0), segments=12, axis='X')
    # a faint inner-glow disc
    make_cyl("Safelight_Glow", (sx - 0.26, sy, sz), 0.05, 0.005,
             (1.0, 0.35, 0.30, 1.0), segments=12, axis='X')


def build_wall_dressing():
    """Small readables that sell a lived-in darkroom without adding
    light-fighting brightness: a pinned test-strip card, a wall clock
    face, a coiled squeegee, a roll of paper towels."""
    # Pinned test strip + notes on the west wall over the wet bench
    make_box("Pinned_TestStrip", (-1.28, 2.9, 1.55), (0.01, 0.10, 0.34), COL_PRINT)
    for k in range(5):
        make_box(f"TestStrip_Band_{k}", (-1.272, 2.9, 1.42 + k * 0.06),
                 (0.006, 0.09, 0.03), (0.12 + k * 0.15, 0.12 + k * 0.15, 0.14 + k * 0.14, 1.0))
    make_box("Pinned_Note", (-1.28, 2.5, 1.62), (0.01, 0.16, 0.20), (0.72, 0.70, 0.62, 1.0))
    # Squeegee hung by the sink
    make_box("Squeegee", (0.4, ROOM_D - 0.04, 1.5), (0.16, 0.02, 0.04), COL_STEEL_DK)
    make_box("Squeegee_Blade", (0.4, ROOM_D - 0.05, 1.46), (0.15, 0.01, 0.04), COL_BASE)
    # Paper-towel roll on a holder under the chem shelf
    make_cyl("PaperTowel", (-1.2, 0.9, 1.28), 0.06, 0.24, (0.86, 0.84, 0.78, 1.0),
             segments=10, axis='Y')
    make_cyl("PaperTowel_Core", (-1.2, 0.9, 1.28), 0.02, 0.28, COL_BENCH_DK,
             segments=6, axis='Y')
    # A small step-stool on the floor (the closet is tight)
    make_box("Stool_Top", (0.55, 1.0, 0.44), (0.30, 0.26, 0.03), COL_BENCH_DK)
    for sgn_x in (-1, 1):
        for sgn_y in (-1, 1):
            make_box(f"Stool_Leg_{sgn_x}_{sgn_y}",
                     (0.55 + sgn_x * 0.12, 1.0 + sgn_y * 0.10, 0.21),
                     (0.03, 0.03, 0.42), COL_BENCH_DK)


def main():
    clear_scene()
    build_shell()
    build_wet_bench()
    build_dry_bench()
    build_drying_line()
    build_safelight()
    build_wall_dressing()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/darkroom.glb"))
    print(f"\n[build_darkroom] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
