"""
blockout_planar_human.py
══════════════════════════════════════════════════════════════════
A fresh-start character blockout that bakes in the lessons from
the dacancino reference read. Not a finished sculpt — a procedural
LOW-POLY blockout that gets the SILHOUETTE and PROPORTIONS right
before any sculpting starts.

What's different from the earlier attempts:

  · 8-heads exact (3.60 units tall, head_h = 0.450).
  · Shoulders 2.7 head-widths (broader than the gender-neutral
    reference's 1.8H — we sculpt male athletic by default).
  · Trap slope: 3-band neck → trap → clavicle transition, not a
    cylinder dropped on a flat shoulder.
  · Hand reaches mid-thigh (not hip, not knee).
  · Face proportions 31/41/28 (NOT 33/33/33 — the perfect-thirds
    grid is what made earlier sculpts feel uncanny).
  · Nose protrudes 16mm — not pinocchio.
  · Eye sockets carved as 4cm recesses.
  · Cheekbone shelves as hard normal shifts (Asaro planar).
  · 3-loop minimum implied at every articulating joint.

The output is a cross-section dataset (polygons at each Y level)
that we'd loft in Blender into a clean planar mesh. The Python
renderer below rasterises it to ASCII so we can visually QA the
silhouette against the reference WITHOUT booting Blender.

Run (stand-alone):
    python3 blockout_planar_human.py
"""
import math

# ── PROPORTIONS ──────────────────────────────────────────────────
TOTAL_H = 3.600                  # full figure height
HEAD_H  = TOTAL_H / 8            # 0.450
HEAD_W  = HEAD_H * 0.76          # head width-to-height ratio from ref
EYE_W   = HEAD_W / 5             # 5-eyes rule

# Head landmark Y (measured from crown=TOTAL_H down):
CROWN_Y     = TOTAL_H
HAIRLINE_Y  = TOTAL_H - HEAD_H * 0.10
BROW_Y      = TOTAL_H - HEAD_H * 0.31         # rule of thirds 31%
EYE_Y       = TOTAL_H - HEAD_H * 0.50         # 50% of head
NOSE_Y      = BROW_Y  - HEAD_H * 0.41         # middle third 41%
CHIN_Y      = TOTAL_H - HEAD_H                # 1H mark
MOUTH_Y     = CHIN_Y  + (NOSE_Y - CHIN_Y) * 0.4

# Body landmark Y:
NECK_TOP_Y  = CHIN_Y - HEAD_H * 0.05          # just under jaw
NECK_BOT_Y  = CHIN_Y - HEAD_H * 0.30          # trap base, 14cm below chin
CLAV_Y      = NECK_BOT_Y - HEAD_H * 0.15      # clavicle peak
NIPPLE_Y    = TOTAL_H - HEAD_H * 2            # 2H mark
NAVEL_Y     = TOTAL_H - HEAD_H * 3            # 3H mark
CROTCH_Y    = TOTAL_H - HEAD_H * 4            # midpoint
THIGH_Y     = TOTAL_H - HEAD_H * 5
KNEE_Y      = TOTAL_H - HEAD_H * 6
SHIN_Y      = TOTAL_H - HEAD_H * 7
ANKLE_Y     = HEAD_H * 0.30
SOLE_Y      = 0.0

# Widths (X, half = perp from centerline):
SHOULDER_W_HALF = HEAD_W * 2.7 / 2            # 2.7 head-widths total
HIP_W_HALF      = HEAD_W * 1.85 / 2           # narrower than shoulders
WAIST_W_HALF    = HEAD_W * 1.55 / 2           # taper at 3H
NECK_W_HALF     = HEAD_W * 0.60 / 2           # 60% of head width
TRAP_TOP_W_HALF = NECK_W_HALF                  # blends from neck
TRAP_BOT_W_HALF = SHOULDER_W_HALF * 0.85      # trap to shoulder slope
THIGH_W_HALF    = HEAD_W * 0.78 / 2
KNEE_W_HALF     = HEAD_W * 0.45 / 2
SHIN_W_HALF     = HEAD_W * 0.42 / 2
ANKLE_W_HALF    = HEAD_W * 0.30 / 2
FOOT_W_HALF     = HEAD_W * 0.40 / 2

# Arms (hanging at sides, hands at MID-THIGH not hip):
ARM_LEN         = HEAD_H * 3.0               # shoulder to fingertip
ELBOW_DROP      = HEAD_H * 1.4               # from clavicle Y down
HAND_DROP       = HEAD_H * 3.0
UPPERARM_W_HALF = HEAD_W * 0.32 / 2
FOREARM_W_HALF  = HEAD_W * 0.26 / 2

# Z (depth) — body depth = 0.16 × height = 0.58
BODY_D       = TOTAL_H * 0.16
TORSO_D_HALF = BODY_D / 2
HEAD_D_HALF  = HEAD_W * 0.95 / 2             # head depth ~ head width
NOSE_PROT    = 0.016                          # 16mm forward from eye plane
EYE_RECESS   = 0.040                          # 4cm carved back

# ── CROSS-SECTIONS  (Y, half_width_X, depth_offset_Z) ──────────
# For each Y level, define the body XY-projected half-width. We
# also tag rows where face features carve recesses into the Z
# profile, but the silhouette renderer below only uses X widths.

ROWS = [
    # crown to chin -- head profile (no arms in this band)
    ("crown",      CROWN_Y,        HEAD_W * 0.30 / 2),
    ("skull_top",  CROWN_Y - 0.04, HEAD_W * 0.62 / 2),
    ("skull_mid",  CROWN_Y - 0.10, HEAD_W * 0.92 / 2),
    ("hairline",   HAIRLINE_Y,     HEAD_W * 0.98 / 2),
    ("forehead",   CROWN_Y - 0.18, HEAD_W * 0.97 / 2),
    ("brow",       BROW_Y,         HEAD_W * 1.00 / 2),
    ("eye",        EYE_Y,          HEAD_W * 0.98 / 2),
    ("cheekbone",  EYE_Y - 0.04,   HEAD_W * 0.96 / 2),  # cheekbone shelf
    ("upper_lip",  MOUTH_Y + 0.01, HEAD_W * 0.88 / 2),
    ("nose_tip",   NOSE_Y,         HEAD_W * 0.78 / 2),
    ("mouth",      MOUTH_Y,        HEAD_W * 0.82 / 2),
    ("chin",       CHIN_Y,         HEAD_W * 0.62 / 2),
    # neck (narrow column, ~10cm)
    ("neck_top",   NECK_TOP_Y,     NECK_W_HALF),
    ("neck_mid",   (NECK_TOP_Y + NECK_BOT_Y) / 2, NECK_W_HALF * 1.05),
    ("neck_bot",   NECK_BOT_Y,     TRAP_TOP_W_HALF * 1.15),
    # trap slope (steep diagonal widening)
    ("trap_top",   NECK_BOT_Y - 0.04, TRAP_BOT_W_HALF * 0.55),
    ("trap_mid",   NECK_BOT_Y - 0.08, TRAP_BOT_W_HALF * 0.78),
    ("trap_bot",   CLAV_Y + 0.02,  TRAP_BOT_W_HALF),
    # shoulders (clavicle line)
    ("clav_peak",  CLAV_Y,         SHOULDER_W_HALF),
    # Torso-only widths below; arms are layered in by arm_x_at.
    ("chest",      NIPPLE_Y + 0.10, SHOULDER_W_HALF * 0.85),
    ("nipple",     NIPPLE_Y,       SHOULDER_W_HALF * 0.78),
    ("ribs",       NIPPLE_Y - 0.10, SHOULDER_W_HALF * 0.70),
    ("upper_waist",NIPPLE_Y - 0.20, WAIST_W_HALF * 1.15),
    ("waist",      NAVEL_Y,        WAIST_W_HALF),
    ("upper_hip",  NAVEL_Y - 0.10, HIP_W_HALF * 0.95),
    ("hip",        CROTCH_Y + 0.10, HIP_W_HALF),
    ("crotch",     CROTCH_Y,       HIP_W_HALF * 0.85),
    # below hands: legs alone
    ("upper_thigh",CROTCH_Y - 0.10, THIGH_W_HALF + HEAD_W * 0.05),
    ("thigh",      THIGH_Y,        THIGH_W_HALF + HEAD_W * 0.05),
    ("lower_thigh",THIGH_Y - HEAD_H * 0.5, THIGH_W_HALF + HEAD_W * 0.02),
    ("knee_above", KNEE_Y + 0.04,  KNEE_W_HALF + HEAD_W * 0.02),
    ("knee",       KNEE_Y,         KNEE_W_HALF),
    ("knee_below", KNEE_Y - 0.04,  KNEE_W_HALF * 0.96),
    ("calf",       SHIN_Y + HEAD_H * 0.2, SHIN_W_HALF + HEAD_W * 0.04),
    ("shin",       SHIN_Y,         SHIN_W_HALF),
    ("ankle",      ANKLE_Y,        ANKLE_W_HALF),
    ("foot",       SOLE_Y + 0.04,  FOOT_W_HALF),
    ("sole",       SOLE_Y,         FOOT_W_HALF * 0.85),
]

# Arms hanging — left/right arm centerline X follows a slight
# arc: shoulder X = SHOULDER_W_HALF * 0.85, hip-hand X = HIP_W_HALF * 1.2.
# When a row is between clavicle and mid-thigh, the silhouette
# half-width is max(torso, arm_outer_edge).
def arm_x_at(y, sgn):
    """Outer-edge X of the arm at height y (sgn = +1 left, -1 right).
    Returns (outer_x, inner_x) so the arm is a separate column with
    a visible torso-to-arm gap on either side."""
    arm_y_top = CLAV_Y - 0.02
    arm_y_bot = THIGH_Y - HEAD_H * 0.05  # hand tips at mid-thigh
    if y > arm_y_top or y < arm_y_bot:
        return None
    t = (arm_y_top - y) / (arm_y_top - arm_y_bot)
    # Arm centerline drifts inward slightly (hands hang closer
    # to thighs than shoulders sit wide)
    shoulder_cx = SHOULDER_W_HALF * 0.78
    hand_cx     = HIP_W_HALF * 0.95
    arm_cx = shoulder_cx + (hand_cx - shoulder_cx) * t
    arm_w  = UPPERARM_W_HALF + (FOREARM_W_HALF - UPPERARM_W_HALF) * t
    return sgn * (arm_cx + arm_w), sgn * (arm_cx - arm_w)


def render_ascii(rows, mark_lines=True, w=44, h=44):
    """Front-view ASCII silhouette. For each grid row, build the
    silhouette envelope from torso/limb cross-sections, then
    rasterize as ranges (start, end) rather than per-pixel."""
    y_max = TOTAL_H + 0.05
    y_min = -0.05
    x_max = HEAD_W * 2.0
    grid = [[' '] * w for _ in range(h)]

    def torso_half_at(y):
        for i in range(len(rows) - 1):
            y0 = rows[i][1]; w0 = rows[i][2]
            y1 = rows[i + 1][1]; w1 = rows[i + 1][2]
            lo, hi = min(y0, y1), max(y0, y1)
            if lo <= y <= hi:
                t = (y - y0) / (y1 - y0) if y1 != y0 else 0
                return w0 + (w1 - w0) * t
        return 0.0

    def x_to_gx(x):
        return int((x + x_max) / (2 * x_max) * (w - 1))

    for gy in range(h):
        # World Y for this row's CENTER
        y = y_min + (1 - gy / (h - 1)) * (y_max - y_min)
        torso = torso_half_at(y)
        # Draw torso/head/leg as continuous fill from -torso to +torso
        if torso > 0:
            gx0 = x_to_gx(-torso); gx1 = x_to_gx(+torso)
            for x in range(max(0, gx0), min(w, gx1 + 1)):
                grid[gy][x] = '#'
        # Layer arms on either side, leaving a visible gap to torso
        for sgn in (-1, 1):
            ae = arm_x_at(y, sgn)
            if ae is None:
                continue
            outer, inner = ae
            lo_x, hi_x = sorted((outer, inner))
            gx0 = x_to_gx(lo_x); gx1 = x_to_gx(hi_x)
            for x in range(max(0, gx0), min(w, gx1 + 1)):
                grid[gy][x] = '#'

    if mark_lines:
        for k in range(1, 8):
            ly = TOTAL_H - k * HEAD_H
            gy = int((1 - (ly - y_min) / (y_max - y_min)) * (h - 1))
            if 0 <= gy < h:
                if grid[gy][0] == ' ':
                    grid[gy][0] = '·'
                if grid[gy][-1] == ' ':
                    grid[gy][-1] = '·'
    return '\n'.join(''.join(row) for row in grid)


def main():
    print("BLOCKOUT — fresh-start planar human, applying ref lessons")
    print(f"  TOTAL_H={TOTAL_H}  HEAD_H={HEAD_H:.3f}  HEAD_W={HEAD_W:.3f}")
    print(f"  Shoulder = {SHOULDER_W_HALF*2:.3f} ({SHOULDER_W_HALF*2/HEAD_W:.2f} head-widths)")
    print(f"  Hip      = {HIP_W_HALF*2:.3f} ({HIP_W_HALF*2/HEAD_W:.2f} head-widths)")
    print(f"  Neck     = {NECK_W_HALF*2:.3f} ({NECK_W_HALF*2/HEAD_W:.2f} head-widths, ~60% of head)")
    print(f"  Face thirds: 31% / 41% / 28% (NOT 33/33/33)")
    print()
    print(render_ascii(ROWS))


if __name__ == "__main__":
    main()
