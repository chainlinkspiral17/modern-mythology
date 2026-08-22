"""V · HIEROPHANT — the_hierophant_circuit.

Paul's Sunday circuit is a multi-stop day. Three scenarios:

  st_judes_morning      · 10:42 AM · church steps
                                    · long black car at curb
  sunday_brunch         · 11:47 AM · Brunch Court at Table 17
                                    · the carefully crafted sentence
  the_bandstand_calls   · 3:18 PM  · park bandstand + bench
                                    · phone call to Antonio

This GLB hosts two physical stops:
  · St. Jude's church (exterior facade + steps + curbside long car)
  · The park bandstand (octagonal raised stage + bench + path)

The third stop — Sunday brunch at Table 17 — already exists in the
riverboat GLB (build_riverboat_interior.py with its build_table_17
+ build_empress_dressing for the "14" plaque, which I now extend
to label Table 17 too if needed). The Hierophant host script can
swap GLBs between stops, OR the gauntlet can render the riverboat
GLB into its SubViewport for the brunch scenario specifically.

Layout in this GLB (all on one continuous ground plane):
  ST. JUDE'S  (south end, around Y=-12..0)
      Church exterior facade · cream plaster wall + 6 wide steps
      up to twin paneled doors + an arched window above + two
      flanking statuary niches + a small bell tower hint
      Long black car at the curb · 1990s town car, parked
  CONNECTING PATH (Y=0..+10) · sidewalk + grass + 4 trees
  PARK BANDSTAND (north end, Y=+10..+22)
      Octagonal raised stage 6m diameter · 8 columns + hipped
      roof + low railing + a single park bench + a gravel path
      leading up

COORDINATE FRAME (Blender → Godot):
    +X east   → +X
    +Y north  → -Z
    +Z up     → +Y
1 unit = 1 m.

Run:
    blender --background --python build_hierophant_circuit.py

Output: godot/assets/3d/locales/hierophant_circuit.glb
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

# ── Palette ─────────────────────────────────────────────────────
COL_GRASS         = (0.42, 0.50, 0.30, 1.0)
COL_CONCRETE      = (0.72, 0.70, 0.66, 1.0)
COL_ASPHALT       = (0.20, 0.20, 0.20, 1.0)
COL_GRAVEL        = (0.60, 0.56, 0.50, 1.0)
COL_CHURCH_PLASTER = (0.92, 0.86, 0.72, 1.0)   # warm cream
COL_CHURCH_TRIM   = (0.78, 0.68, 0.46, 1.0)
COL_CHURCH_DOOR   = (0.32, 0.20, 0.12, 1.0)
COL_CHURCH_DOOR_DK = (0.20, 0.12, 0.06, 1.0)
COL_BRASS         = (0.78, 0.62, 0.30, 1.0)
COL_BRASS_DARK    = (0.42, 0.32, 0.16, 1.0)
COL_GLASS_DEVOT   = (0.62, 0.32, 0.18, 1.0)   # devotional amber
COL_STATUE_WEATHERED = (0.78, 0.74, 0.66, 1.0)
COL_ROOF_SHINGLE  = (0.46, 0.32, 0.22, 1.0)
COL_BELL_BRASS    = (0.78, 0.64, 0.30, 1.0)

COL_CAR_BODY      = (0.08, 0.08, 0.10, 1.0)   # the long black car
COL_CAR_TRIM      = (0.62, 0.62, 0.60, 1.0)
COL_CAR_GLASS     = (0.18, 0.20, 0.22, 0.85)
COL_CAR_WHEEL     = (0.16, 0.14, 0.14, 1.0)
COL_CAR_HUB       = (0.62, 0.62, 0.62, 1.0)
COL_CAR_HEADLIGHT = (0.92, 0.88, 0.74, 1.0)

COL_BANDSTAND_WHITE = (0.94, 0.92, 0.86, 1.0)
COL_BANDSTAND_TRIM  = (0.46, 0.32, 0.22, 1.0)
COL_BANDSTAND_ROOF  = (0.42, 0.32, 0.20, 1.0)
COL_BENCH_WOOD      = (0.38, 0.26, 0.18, 1.0)
COL_BENCH_IRON      = (0.18, 0.16, 0.14, 1.0)

COL_TREE_TRUNK    = (0.32, 0.22, 0.14, 1.0)
COL_TREE_LEAF     = (0.32, 0.46, 0.22, 1.0)


# ── Ground plane ─────────────────────────────────────────────────

def build_ground():
    # Big grass plane covering both stops
    make_box("Ground_Grass",
             (0.0, +5.0, -0.04),
             (40.0, 40.0, 0.04),
             COL_GRASS)


# ── ST. JUDE'S CHURCH (south stop) ───────────────────────────────

def build_church():
    """Church exterior facade only — the player faces it from the
    sidewalk at the curb. South-facing facade at Y = -7."""
    facade_y = -7.0
    # Curb-side asphalt street + sidewalk in front of the facade
    make_box("Church_Street",
             (0.0, -11.0, -0.030),
             (32.0, 4.0, 0.05),
             COL_ASPHALT)
    make_box("Church_Curb",
             (0.0, -9.0, 0.00),
             (32.0, 0.30, 0.10),
             COL_CONCRETE)
    make_box("Church_Sidewalk",
             (0.0, -8.3, 0.00),
             (32.0, 1.40, 0.06),
             COL_CONCRETE)
    # The plaza in front of the steps
    make_box("Church_Plaza",
             (0.0, facade_y + 4.0, 0.02),
             (16.0, 4.0, 0.06),
             COL_CONCRETE)
    # 6 wide stone steps leading up to the doors
    for s in range(6):
        make_box("Church_Step_%d" % s,
                 (0.0, facade_y + 2.8 - s * 0.32, 0.06 + s * 0.16),
                 (12.0 - s * 0.6, 0.40, 0.18),
                 (0.66, 0.60, 0.50, 1.0))
    # Facade — a tall plaster wall
    facade_z_top = 9.0
    make_box("Church_Facade",
             (0.0, facade_y, facade_z_top / 2.0),
             (14.0, 0.40, facade_z_top),
             COL_CHURCH_PLASTER)
    # Plinth at the base of the facade
    make_box("Church_Plinth",
             (0.0, facade_y - 0.10, 0.40),
             (14.0, 0.60, 0.80),
             COL_CHURCH_TRIM)
    # ── Twin paneled doors at the top of the steps ──
    door_w, door_h = 1.10, 3.40
    door_cy = facade_y + 0.04
    door_cz = door_h / 2.0 + 1.50   # raised on a top step landing
    for sgn in (-1, +1):
        dx = sgn * 0.62
        # Door body
        make_box("Church_Door_%+d" % sgn,
                 (dx, door_cy - 0.04, door_cz),
                 (door_w, 0.10, door_h),
                 COL_CHURCH_DOOR)
        # Door inset panels (4 stacked rectangles)
        for pi in range(4):
            pz = door_cz - door_h/2.0 + 0.32 + pi * 0.82
            make_box("Church_Door_%+d_Panel_%d" % (sgn, pi),
                     (dx, door_cy - 0.10, pz),
                     (door_w - 0.18, 0.005, 0.66),
                     COL_CHURCH_DOOR_DK)
        # Brass door handle ring
        make_cyl("Church_Door_%+d_Ring" % sgn,
                 (dx + (sgn * (door_w/2.0 - 0.18)), door_cy - 0.15, door_cz),
                 0.10, 0.012,
                 COL_BRASS, segments=10, axis='Y')
    # Doorway lintel (a stone lintel band above the doors)
    make_box("Church_DoorLintel",
             (0.0, door_cy - 0.04, door_cz + door_h/2.0 + 0.12),
             (3.60, 0.20, 0.24),
             COL_CHURCH_TRIM)
    # ── Arched window above the doors ──
    win_cz = door_cz + door_h/2.0 + 1.50
    # Window body (rectangle base + half-disc top)
    make_box("Church_ArchWin_Body",
             (0.0, door_cy - 0.06, win_cz),
             (2.40, 0.04, 1.60),
             COL_GLASS_DEVOT)
    make_cyl("Church_ArchWin_Top",
             (0.0, door_cy - 0.06, win_cz + 0.80),
             1.20, 0.04,
             COL_GLASS_DEVOT, segments=12, axis='Y')
    # Window leading (a cross-pattern of lead came)
    make_box("Church_ArchWin_MullV",
             (0.0, door_cy - 0.08, win_cz),
             (0.06, 0.06, 1.60),
             COL_BRASS_DARK)
    make_box("Church_ArchWin_MullH",
             (0.0, door_cy - 0.08, win_cz),
             (2.40, 0.06, 0.06),
             COL_BRASS_DARK)
    # ── Two flanking statuary niches ──
    for sgn in (-1, +1):
        nx = sgn * 4.6
        ncz = 3.40
        # Recess
        make_box("Church_Niche_%+d_Recess" % sgn,
                 (nx, facade_y - 0.05, ncz),
                 (0.80, 0.04, 1.60),
                 COL_CHURCH_TRIM)
        # Arched top
        make_cyl("Church_Niche_%+d_Arch" % sgn,
                 (nx, facade_y - 0.05, ncz + 0.80),
                 0.40, 0.04,
                 COL_CHURCH_TRIM, segments=12, axis='Y')
        # Statue (weathered saint)
        # Robe / body
        make_box("Church_Niche_%+d_Statue_Robe" % sgn,
                 (nx, facade_y - 0.12, ncz - 0.10),
                 (0.34, 0.20, 1.10),
                 COL_STATUE_WEATHERED)
        # Head
        make_cyl("Church_Niche_%+d_Statue_Head" % sgn,
                 (nx, facade_y - 0.12, ncz + 0.60),
                 0.16, 0.30,
                 COL_STATUE_WEATHERED, segments=10, axis='Z')
        # Arms (folded across chest)
        for ax_sgn in (-1, +1):
            make_box("Church_Niche_%+d_Statue_Arm_%+d" % (sgn, ax_sgn),
                     (nx + ax_sgn * 0.10, facade_y - 0.12, ncz + 0.10),
                     (0.10, 0.16, 0.40),
                     COL_STATUE_WEATHERED)
    # ── Small bell tower hint above the facade peak ──
    peak_z = facade_z_top + 0.40
    # Square stone base
    make_box("Church_BellTower_Base",
             (0.0, facade_y, peak_z + 0.80),
             (1.80, 1.60, 1.60),
             COL_CHURCH_PLASTER)
    # Open belfry (4 columns + roof)
    for sgn_x in (-1, +1):
        for sgn_y in (-1, +1):
            make_box("Church_BellTower_Column_%+d_%+d" % (sgn_x, sgn_y),
                     (sgn_x * 0.70, facade_y + sgn_y * 0.60, peak_z + 2.00),
                     (0.16, 0.16, 1.20),
                     COL_CHURCH_PLASTER)
    # Pyramidal roof (a single tapered box for the steeple)
    make_box("Church_BellTower_Roof",
             (0.0, facade_y, peak_z + 3.20),
             (1.40, 1.20, 0.80),
             COL_ROOF_SHINGLE)
    # Small cross at the peak
    make_box("Church_Cross_V",
             (0.0, facade_y, peak_z + 4.20),
             (0.04, 0.04, 0.60),
             COL_BRASS)
    make_box("Church_Cross_H",
             (0.0, facade_y, peak_z + 4.40),
             (0.28, 0.04, 0.04),
             COL_BRASS)
    # The bell visible in the belfry
    make_cyl("Church_Bell",
             (0.0, facade_y, peak_z + 2.40),
             0.32, 0.40,
             COL_BELL_BRASS, segments=10, axis='Z')


def build_long_black_car():
    """The long black car idling at the curb. 1990s town car
    silhouette. Parked east of the church steps · the canonical
    "Paul will arrive at Table 17 turn 3" car.
    """
    # Curb is at Y=-9; park the car centered at Y=-10 (in the
    # street, parallel to the curb), and east of the church plaza.
    cx = -2.5
    cy = -10.0
    # Wheelbase-long body
    body_w, body_d, body_h = 5.40, 1.85, 1.15
    # Main lower body
    make_box("Car_LowerBody",
             (cx, cy, 0.55),
             (body_w, body_d, body_h - 0.30),
             COL_CAR_BODY)
    # Upper greenhouse (slightly inset on Y)
    make_box("Car_Greenhouse",
             (cx + 0.10, cy, 1.30),
             (body_w - 2.20, body_d - 0.16, 0.60),
             COL_CAR_BODY)
    # Windshield (a sloped pane on the front — we use a tilted box)
    make_box("Car_Windshield",
             (cx - 1.30, cy, 1.20),
             (0.60, body_d - 0.20, 0.70),
             COL_CAR_GLASS)
    # Rear window
    make_box("Car_RearWindow",
             (cx + 1.80, cy, 1.20),
             (0.60, body_d - 0.20, 0.70),
             COL_CAR_GLASS)
    # Side windows (driver / passenger / rear-driver / rear-passenger)
    for sgn in (-1, +1):
        # Front side window
        make_box("Car_SideWin_F_%+d" % sgn,
                 (cx - 0.20, cy + sgn * (body_d / 2.0 - 0.04), 1.30),
                 (1.30, 0.04, 0.50),
                 COL_CAR_GLASS)
        # Rear side window
        make_box("Car_SideWin_R_%+d" % sgn,
                 (cx + 1.10, cy + sgn * (body_d / 2.0 - 0.04), 1.30),
                 (1.30, 0.04, 0.50),
                 COL_CAR_GLASS)
    # Chrome trim along the lower body (a thin strip)
    make_box("Car_LowerTrim",
             (cx, cy, 0.32),
             (body_w + 0.04, body_d + 0.04, 0.04),
             COL_CAR_TRIM)
    # Grille (front)
    make_box("Car_Grille",
             (cx - body_w/2.0 + 0.05, cy, 0.62),
             (0.04, body_d - 0.20, 0.30),
             COL_CAR_TRIM)
    # 7 vertical grille slats
    for gi in range(7):
        gx_off = -0.50 + gi * 0.18
        make_box("Car_GrilleSlat_%d" % gi,
                 (cx - body_w/2.0 + 0.04, cy + gx_off / 2.0, 0.62),
                 (0.005, 0.10, 0.22),
                 COL_CAR_BODY)
    # Headlights (two on the front)
    for sgn in (-1, +1):
        make_cyl("Car_Headlight_%+d" % sgn,
                 (cx - body_w/2.0 + 0.04, cy + sgn * 0.65, 0.62),
                 0.14, 0.06,
                 COL_CAR_HEADLIGHT, segments=10, axis='X')
    # Tail lights
    for sgn in (-1, +1):
        make_box("Car_Taillight_%+d" % sgn,
                 (cx + body_w/2.0 - 0.02, cy + sgn * 0.50, 0.66),
                 (0.04, 0.30, 0.16),
                 (0.62, 0.16, 0.14, 1.0))
    # 4 wheels
    for sgn_x, sgn_y in [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]:
        wx = cx + sgn_x * (body_w / 2.0 - 0.80)
        wy = cy + sgn_y * (body_d / 2.0)
        make_cyl("Car_Wheel_%+d_%+d_Tire" % (sgn_x, sgn_y),
                 (wx, wy, 0.34),
                 0.34, 0.24,
                 COL_CAR_WHEEL, segments=12, axis='Y')
        # Chrome hub
        make_cyl("Car_Wheel_%+d_%+d_Hub" % (sgn_x, sgn_y),
                 (wx, wy + sgn_y * 0.025, 0.34),
                 0.16, 0.05,
                 COL_CAR_HUB, segments=10, axis='Y')
    # Side mirror (driver's side)
    make_box("Car_SideMirror",
             (cx - 1.20, cy - body_d / 2.0 - 0.10, 1.20),
             (0.16, 0.10, 0.10),
             COL_CAR_BODY)
    # Exhaust pipe (small chrome tube at the back, low)
    make_cyl("Car_Exhaust",
             (cx + body_w / 2.0 + 0.04, cy - 0.50, 0.22),
             0.030, 0.18,
             COL_CAR_TRIM, segments=8, axis='X')
    # Hood ornament (a tiny brass mascot)
    make_box("Car_HoodOrnament",
             (cx - body_w/2.0 + 0.50, cy, 0.92),
             (0.04, 0.04, 0.10),
             COL_BRASS)


# ── PARK BANDSTAND (north stop) ──────────────────────────────────

def build_bandstand():
    """Octagonal raised stage with 8 columns + hipped roof, plus a
    park bench and a gravel path leading up. Per the_bandstand_calls:
    "John Frank is on a bench, writing AROUND you."
    """
    bs_cx = 0.0
    bs_cy = +18.0
    # Stone path leading from the south to the bandstand
    make_box("Bandstand_Path",
             (0.0, +10.0, 0.00),
             (1.80, 12.0, 0.05),
             COL_GRAVEL)
    # ── Octagonal stage platform ──
    stage_radius = 3.20
    stage_h = 0.60
    # Build the octagonal stage as a low cylinder with 8 sides
    make_cyl("Bandstand_Stage",
             (bs_cx, bs_cy, stage_h / 2.0),
             stage_radius, stage_h,
             COL_BANDSTAND_WHITE, segments=8, axis='Z')
    # Trim at the top edge of the stage
    make_cyl("Bandstand_StageTrim",
             (bs_cx, bs_cy, stage_h + 0.01),
             stage_radius + 0.04, 0.04,
             COL_BANDSTAND_TRIM, segments=8, axis='Z')
    # 4 steps up to the stage on the south side
    for s in range(3):
        make_box("Bandstand_Step_%d" % s,
                 (bs_cx, bs_cy - stage_radius - 0.20 - s * 0.30, 0.08 + s * 0.16),
                 (1.40, 0.30, 0.18),
                 (0.66, 0.60, 0.50, 1.0))
    # ── 8 columns ──
    col_h = 2.80
    for ci in range(8):
        ang = math.radians(45 * ci + 22.5)
        cx = bs_cx + (stage_radius - 0.20) * math.cos(ang)
        cy = bs_cy + (stage_radius - 0.20) * math.sin(ang)
        # Column shaft
        make_cyl("Bandstand_Column_%d" % ci,
                 (cx, cy, stage_h + col_h / 2.0),
                 0.10, col_h,
                 COL_BANDSTAND_WHITE, segments=8, axis='Z')
        # Capital (a small wider block at the top)
        make_box("Bandstand_ColumnCap_%d" % ci,
                 (cx, cy, stage_h + col_h + 0.04),
                 (0.24, 0.24, 0.08),
                 COL_BANDSTAND_WHITE)
        # Base (a small wider block at the bottom)
        make_box("Bandstand_ColumnBase_%d" % ci,
                 (cx, cy, stage_h + 0.04),
                 (0.22, 0.22, 0.08),
                 COL_BANDSTAND_WHITE)
    # ── Octagonal roof ring (an entablature) ──
    roof_z = stage_h + col_h + 0.12
    make_cyl("Bandstand_RoofRing",
             (bs_cx, bs_cy, roof_z),
             stage_radius + 0.10, 0.18,
             COL_BANDSTAND_TRIM, segments=8, axis='Z')
    # Hipped/conical roof — a cone above (using a stack of two
    # cylinders to fake the taper)
    make_cyl("Bandstand_Roof_Lower",
             (bs_cx, bs_cy, roof_z + 0.50),
             stage_radius - 0.10, 0.80,
             COL_BANDSTAND_ROOF, segments=8, axis='Z')
    make_cyl("Bandstand_Roof_Upper",
             (bs_cx, bs_cy, roof_z + 1.20),
             stage_radius - 1.80, 0.80,
             COL_BANDSTAND_ROOF, segments=8, axis='Z')
    # Small finial at the top
    make_cyl("Bandstand_Finial_Post",
             (bs_cx, bs_cy, roof_z + 1.80),
             0.020, 0.30,
             COL_BRASS, segments=4, axis='Z')
    make_cyl("Bandstand_Finial_Ball",
             (bs_cx, bs_cy, roof_z + 2.00),
             0.080, 0.08,
             COL_BRASS, segments=10, axis='Z')
    # ── Low railing between columns (skip the south-facing gap
    # for the entry steps) ──
    for ri in range(8):
        # Skip the south-facing gap (between columns 2 and 3 ish —
        # ang ~ 22.5 + 2*45 = 112.5 and 22.5+3*45=157.5; the south
        # gap is at ang ~ 270° → skip the segment between ci=5 and ci=6)
        if ri == 5:
            continue
        ang1 = math.radians(45 * ri + 22.5)
        ang2 = math.radians(45 * (ri + 1) + 22.5)
        mx = bs_cx + (stage_radius - 0.20) * (math.cos(ang1) + math.cos(ang2)) / 2.0
        my = bs_cy + (stage_radius - 0.20) * (math.sin(ang1) + math.sin(ang2)) / 2.0
        # Approximate segment length
        seg_len = math.hypot(math.cos(ang1) - math.cos(ang2),
                              math.sin(ang1) - math.sin(ang2)) * (stage_radius - 0.20)
        # Rotate the rail segment to align with the chord
        chord_ang = math.atan2(math.sin(ang2) - math.sin(ang1),
                                math.cos(ang2) - math.cos(ang1))
        rail_o = make_box("Bandstand_Rail_%d" % ri,
                          (mx, my, stage_h + 0.50),
                          (seg_len - 0.20, 0.05, 0.06),
                          COL_BANDSTAND_TRIM)
        rail_o.rotation_euler = (0, 0, chord_ang)
        import bpy
        bpy.ops.object.transform_apply(rotation=True)
        # Balusters along the rail (3 per segment)
        for bi in range(3):
            t = (bi + 1) / 4.0
            bx = bs_cx + (stage_radius - 0.20) * (
                math.cos(ang1) * (1 - t) + math.cos(ang2) * t)
            by = bs_cy + (stage_radius - 0.20) * (
                math.sin(ang1) * (1 - t) + math.sin(ang2) * t)
            make_box("Bandstand_Baluster_%d_%d" % (ri, bi),
                     (bx, by, stage_h + 0.25),
                     (0.04, 0.04, 0.40),
                     COL_BANDSTAND_TRIM)

    # ── The park bench (John Frank's bench) ──
    # South of the bandstand entry, on the grass next to the path
    bench_cx = -2.40
    bench_cy = +14.0
    # Seat
    make_box("Bench_Seat",
             (bench_cx, bench_cy, 0.44),
             (1.80, 0.40, 0.08),
             COL_BENCH_WOOD)
    # Backrest
    make_box("Bench_Back",
             (bench_cx, bench_cy + 0.18, 0.78),
             (1.80, 0.06, 0.50),
             COL_BENCH_WOOD)
    # 5 slats on the backrest (visible texture detail)
    for si in range(5):
        sx = bench_cx - 0.72 + si * 0.36
        make_box("Bench_BackSlat_%d" % si,
                 (sx, bench_cy + 0.19, 0.78),
                 (0.30, 0.005, 0.40),
                 (0.32, 0.20, 0.14, 1.0))
    # Cast-iron end supports
    for sgn in (-1, +1):
        # Foot scroll
        make_box("Bench_Iron_Foot_%+d" % sgn,
                 (bench_cx + sgn * 0.90, bench_cy, 0.04),
                 (0.10, 0.40, 0.10),
                 COL_BENCH_IRON)
        # Vertical post
        make_box("Bench_Iron_Post_%+d" % sgn,
                 (bench_cx + sgn * 0.90, bench_cy + 0.18, 0.50),
                 (0.05, 0.05, 0.90),
                 COL_BENCH_IRON)
        # Arm rest
        make_box("Bench_Iron_ArmRest_%+d" % sgn,
                 (bench_cx + sgn * 0.90, bench_cy, 0.78),
                 (0.05, 0.40, 0.04),
                 COL_BENCH_IRON)
    # ── John Frank's notebook on the bench ──
    # Per the_bandstand_calls: "John Frank is on a bench, writing
    # AROUND you." The notebook sits on the bench seat — the player
    # is presumably standing nearby. Add the notebook + a pencil.
    make_box("Bench_Notebook",
             (bench_cx + 0.30, bench_cy + 0.04, 0.50),
             (0.16, 0.22, 0.024),
             (0.32, 0.26, 0.18, 1.0))
    # Open page (a lighter rectangle on top)
    make_box("Bench_Notebook_OpenPage",
             (bench_cx + 0.30, bench_cy + 0.04, 0.513),
             (0.14, 0.20, 0.002),
             (0.94, 0.90, 0.78, 1.0))
    # 4 written lines on the page (thin darker streaks)
    for li in range(4):
        make_box("Bench_Notebook_Line_%d" % li,
                 (bench_cx + 0.30, bench_cy + 0.04, 0.514),
                 (0.10, 0.18 - li * 0.02, 0.001),
                 (0.20, 0.18, 0.14, 1.0))
    # Pencil resting on the open page
    make_cyl("Bench_Pencil",
             (bench_cx + 0.46, bench_cy + 0.04, 0.518),
             0.004, 0.14,
             (0.86, 0.66, 0.20, 1.0), segments=4, axis='Y')


# ── Connecting trees ─────────────────────────────────────────────

def build_trees():
    """A few mature trees along the connecting path between the
    church and the bandstand. Helps the locale read as a Sunday
    afternoon park stroll between stops."""
    tree_positions = [
        (-5.5, -3.0), (+5.5, -3.0),     # near the church
        (-6.5, +5.0), (+6.5, +5.0),     # midway
        (-6.5, +14.0), (+6.5, +14.0),   # near the bandstand
        (-3.5, +9.0),                    # path-side
    ]
    for ti, (tx, ty) in enumerate(tree_positions):
        # Trunk
        make_cyl("Tree_%d_Trunk" % ti,
                 (tx, ty, 1.40),
                 0.20, 2.80,
                 COL_TREE_TRUNK, segments=6, axis='Z')
        # Canopy — the comment always said "3 overlapping spheres"
        # but the code drew CYLINDERS (the module had no sphere until
        # 2026-08-04). Actual blobs now, per the original intent.
        from _props.geometry import make_blob
        for sj, dz in enumerate([2.60, 3.00, 2.80]):
            make_blob("Tree_%d_Canopy_%d" % (ti, sj),
                      (tx + (sj - 1) * 0.20, ty, dz), 0.95,
                      COL_TREE_LEAF, noise=0.20,
                      seed=ti * 13 + sj, squash=0.85)


def build_circuit_stations_2026_08():
    """THE CIRCUIT'S OTHER STATIONS (gauntlet FP draft 2).

    Seven of the Hierophant board's eleven stations had no
    geometry. The flavor text is the spec: St Jude's INTERIOR
    ("old incense, wet wood, something older than either"),
    D'Ambrosio's RIVERBOAT with its brunch floor and table 17
    "overlooking the muddy divide," the kitchen and the staff
    corridor with the time clock, the old armory ("brick and tin
    and the kind of plaque nobody cleans"), and the riverfront —
    "the place where texas becomes louisiana under your shoes."

    Layout: nave behind the facade (south), armory at the park's
    west edge, riverfront + moored boat at the far north.
    """
    plaster = (0.82, 0.78, 0.70, 1.0)
    wood_dk = (0.36, 0.26, 0.18, 1.0)
    pew = (0.46, 0.34, 0.24, 1.0)
    brick = (0.48, 0.34, 0.28, 1.0)
    tin = (0.55, 0.56, 0.58, 1.0)
    hull_w = (0.92, 0.90, 0.86, 1.0)
    hull_r = (0.62, 0.18, 0.16, 1.0)
    water = (0.42, 0.36, 0.28, 0.9)   # the muddy divide is MUD-colored
    deck = (0.58, 0.46, 0.32, 1.0)
    # ── ST JUDE'S NAVE · behind the facade (y -7), going north ──
    make_box("Nave_Floor", (0.0, -1.5, 0.02), (13.0, 10.6, 0.06), wood_dk)
    make_box("Nave_Wall_W", (-6.5, -1.5, 3.6), (0.30, 10.6, 7.2), plaster)
    make_box("Nave_Wall_E", (6.5, -1.5, 3.6), (0.30, 10.6, 7.2), plaster)
    make_box("Nave_Wall_N", (0.0, 3.8, 3.6), (13.3, 0.30, 7.2), plaster)
    make_box("Nave_Ceil", (0.0, -1.5, 7.2), (13.3, 10.6, 0.20), (0.30, 0.26, 0.22, 1.0))
    # Pews · two banks with a center aisle, wet-wood dark
    for ri in range(5):
        py = -5.0 + ri * 1.35
        for sgn in (-1, 1):
            make_box("Nave_Pew_%d_%+d" % (ri, sgn), (sgn * 3.1, py, 0.48),
                     (4.6, 0.34, 0.16), pew)
            make_box("Nave_PewBack_%d_%+d" % (ri, sgn), (sgn * 3.1, py + 0.16, 0.85),
                     (4.6, 0.06, 0.60), pew)
    # Altar + the office that owns him
    make_box("Nave_AltarStep", (0.0, 2.9, 0.12), (5.2, 1.6, 0.24), (0.62, 0.58, 0.52, 1.0))
    make_box("Nave_Altar", (0.0, 3.1, 0.85), (2.2, 0.9, 1.00), plaster)
    make_box("Nave_AltarCloth", (0.0, 3.1, 1.38), (2.3, 0.95, 0.06), (0.86, 0.82, 0.72, 1.0))
    for ci in (-1, 1):
        make_cyl("Nave_Candle_%+d" % ci, (ci * 0.8, 3.1, 1.55), 0.035, 0.28,
                 (0.90, 0.88, 0.80, 1.0), segments=6)
    # Incense haze · one thin warm sheet in the crossing light
    make_box("Nave_IncenseHaze", (0.0, -0.5, 3.4), (5.5, 0.02, 3.4),
             (0.85, 0.80, 0.66, 0.16))
    # ── OLD ARMORY · park's west edge ──
    ax, ay = -17.0, 12.0
    make_box("Armory_Body", (ax, ay, 2.6), (7.0, 10.0, 5.2), brick)
    make_box("Armory_Roof", (ax, ay, 5.55), (7.6, 10.6, 0.7), tin)
    make_box("Armory_RoofRidge", (ax, ay, 6.05), (0.5, 10.6, 0.35), tin)
    make_box("Armory_Door", (ax + 3.52, ay - 2.0, 1.5), (0.08, 1.8, 3.0), wood_dk)
    for wi in range(3):
        make_box("Armory_WinBoard_%d" % wi, (ax + 3.52, ay + 1.2 + wi * 2.2, 3.4),
                 (0.06, 1.0, 1.5), (0.42, 0.34, 0.26, 1.0))
    # The plaque nobody cleans · low, by the door
    make_box("Armory_Plaque", (ax + 3.56, ay - 3.4, 1.3), (0.03, 0.55, 0.40),
             (0.42, 0.44, 0.38, 1.0))
    make_box("Armory_Plaque_Grime", (ax + 3.575, ay - 3.5, 1.18), (0.02, 0.35, 0.10),
             (0.30, 0.32, 0.28, 1.0))
    # ── RIVERFRONT · far north · the muddy divide ──
    make_box("River_Bank", (0.0, 30.0, -0.05), (40.0, 4.0, 0.14), (0.52, 0.44, 0.34, 1.0))
    make_box("River_Water", (0.0, 40.0, -0.30), (40.0, 16.0, 0.10), water)
    make_box("River_Wharf", (2.0, 32.6, 0.10), (22.0, 2.4, 0.24), deck)
    for bi in range(5):
        make_cyl("River_Bollard_%d" % bi, (-7.0 + bi * 4.5, 33.5, 0.42), 0.14, 0.65,
                 (0.30, 0.28, 0.26, 1.0), segments=8)
    # The state line under your shoes · a worn painted stripe on
    # the wharf and a stamped plate: TX | LA.
    make_box("River_StateLine", (2.0, 32.6, 0.235), (0.14, 2.4, 0.012),
             (0.86, 0.82, 0.66, 1.0))
    make_box("River_StatePlate", (2.35, 32.0, 0.235), (0.35, 0.25, 0.014),
             (0.58, 0.56, 0.52, 1.0))
    # ── D'AMBROSIO'S RIVERBOAT · moored along the wharf ──
    bx, by = 6.0, 37.0
    make_box("Boat_Hull", (bx, by, 0.55), (16.0, 5.6, 1.5), hull_w)
    make_box("Boat_HullStripe", (bx, by, 1.05), (16.1, 5.65, 0.18), hull_r)
    make_box("Boat_MainDeck", (bx, by, 1.35), (15.4, 5.2, 0.14), deck)
    make_box("Boat_UpperDeck", (bx, by, 3.95), (13.0, 4.4, 0.14), deck)
    for pi in range(6):
        make_box("Boat_DeckPost_%d" % pi, (bx - 6.0 + pi * 2.4, by - 2.35, 2.65),
                 (0.10, 0.10, 2.6), hull_w)
    make_box("Boat_Rail", (bx, by - 2.4, 2.15), (15.0, 0.05, 0.06), hull_w)
    # Twin stacks + THE PADDLEWHEEL at the stern (playbook rule 6:
    # wheel circle PERPENDICULAR to the axle; axle runs Y; one
    # assembly prefix).
    for si in (-1, 1):
        make_cyl("Boat_Stack_%+d" % si, (bx - 2.0 * si, by + 1.2, 5.6), 0.30, 3.2,
                 (0.22, 0.20, 0.20, 1.0), segments=8)
    wx = bx + 8.6
    make_cyl("Boat_Paddle_Axle", (wx, by, 1.3), 0.10, 4.2, (0.30, 0.28, 0.26, 1.0),
             segments=8, axis='Y')
    import math as _m
    for pb in range(8):
        ang = 2 * _m.pi * pb / 8
        # blade centers on a circle in the XZ plane (perpendicular
        # to the Y axle), riding the axle
        bxo = _m.cos(ang) * 1.05
        bzo = _m.sin(ang) * 1.05
        make_box("Boat_Paddle_Blade_%d" % pb, (wx + bxo, by, 1.3 + bzo),
                 (0.55, 3.9, 0.16), hull_r)
    make_box("Boat_Paddle_Box", (wx, by + 2.35, 2.1), (2.9, 0.7, 2.2), hull_r)
    # ── THE BRUNCH FLOOR · main-deck dining slice ──
    # Twelve tables in canon; six modeled forward + TABLE 17, the
    # corner booth at the stern rail overlooking the divide.
    for ti in range(6):
        tx2 = bx - 5.5 + (ti % 3) * 2.4
        ty2 = by - 0.9 + (ti // 3) * 1.9
        make_cyl("Boat_Table_%d" % ti, (tx2, ty2, 1.75), 0.45, 0.05, hull_w, segments=10)
        make_cyl("Boat_Table_%d_Post" % ti, (tx2, ty2, 1.55), 0.05, 0.40,
                 (0.30, 0.28, 0.26, 1.0), segments=6)
    make_box("Table17_Booth_Seat", (bx + 5.6, by - 1.6, 1.62), (1.6, 0.5, 0.14), hull_r)
    make_box("Table17_Booth_Back", (bx + 5.6, by - 1.32, 1.98), (1.6, 0.10, 0.62), hull_r)
    make_box("Table17_Top", (bx + 5.6, by - 2.05, 1.80), (1.4, 0.7, 0.05), hull_w)
    make_box("Table17_Card", (bx + 5.3, by - 2.05, 1.84), (0.10, 0.14, 0.015),
             (0.88, 0.86, 0.80, 1.0))
    # ── KITCHEN + BACK CORRIDOR · aft deckhouse ──
    make_box("BoatKitchen_House", (bx + 2.8, by + 1.5, 2.45), (5.0, 2.0, 2.1), hull_w)
    make_box("BoatKitchen_SwingDoor", (bx + 0.28, by + 1.0, 2.25), (0.06, 0.8, 1.7), wood_dk)
    make_box("BoatKitchen_Line", (bx + 3.6, by + 1.9, 1.85), (2.8, 0.5, 0.9),
             (0.66, 0.68, 0.70, 1.0))
    make_box("BoatKitchen_Pass", (bx + 1.6, by + 1.55, 2.35), (1.2, 0.08, 0.5),
             (0.66, 0.68, 0.70, 1.0))
    # Corridor between kitchen house and stern: time clock + coats.
    make_box("Corridor_TimeClock", (bx + 5.55, by + 1.1, 2.6), (0.24, 0.10, 0.34),
             (0.72, 0.70, 0.66, 1.0))
    make_box("Corridor_CardRack", (bx + 5.55, by + 1.5, 2.5), (0.30, 0.06, 0.4), wood_dk)
    for ci2 in range(3):
        make_box("Corridor_Coat_%d" % ci2, (bx + 5.0 - ci2 * 0.35, by + 2.62, 2.2),
                 (0.22, 0.10, 0.75), (0.30 + ci2 * 0.08, 0.28, 0.30, 1.0))
    # ── THE CURB · gangway + bell above the front door ──
    make_box("Curb_Gangway", (bx - 7.2, by - 3.6, 0.75), (1.2, 2.6, 0.10), deck)
    make_box("Curb_Strip", (bx - 7.2, by - 5.2, 0.06), (6.0, 0.9, 0.12), (0.62, 0.60, 0.56, 1.0))
    make_box("Curb_DoorFrame", (bx - 7.2, by - 2.45, 2.3), (1.4, 0.12, 1.9), wood_dk)
    make_cyl("Curb_Bell", (bx - 7.2, by - 2.5, 3.35), 0.10, 0.14, (0.72, 0.60, 0.30, 1.0),
             segments=8)
    # The long black car's SPOT at the curb is empty — the car
    # itself is parked at the church (it drives the circuit).
    make_box("Curb_NoParking_Stencil", (bx - 7.2, by - 5.15, 0.125), (1.8, 0.35, 0.012),
             (0.82, 0.78, 0.55, 1.0))


def main():
    clear_scene()
    build_ground()
    build_church()
    build_long_black_car()
    build_bandstand()
    build_trees()
    build_circuit_stations_2026_08()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/hierophant_circuit.glb"))
    print(f"\n[build_hierophant_circuit] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
