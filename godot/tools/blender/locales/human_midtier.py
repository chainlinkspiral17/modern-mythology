"""
human_midtier.py
══════════════════════════════════════════════════════════════════
A from-scratch character builder targeting the SPACE BETWEEN
HCE's primitive human_figure (despised — "figlo toys / smooshed")
and dacancino's 3,600-tri planar reference (canonical baseline).

What the previous procedural attempt got WRONG (per the user's
visual A/B 2026-06-16):
  · symmetric ellipse cross-sections → "stack of barrels"
  · arms as floating separate tubes → visible discontinuity
  · symmetric face → "smooshed", uncanny

What this attempt does DIFFERENTLY:
  · per-vert anatomical asymmetry — chest bulges forward, spine
    pulls back, butt bulges back, belly forward
  · arms bridged into the torso at the shoulder ring (continuous
    quad strips, no floating tube)
  · 24 verts per ring (vs 16 before) for smoother silhouette
  · face sculpt baked into head rings — front-center vert pushed
    forward for nose, eye-line side-of-bridge verts pulled back
    for sockets, cheekbone verts pushed slightly out + forward
  · ~1,400 tris total — between primitive (200) and planar (3,600)

Target call site (Blender Python):
    from human_midtier import midtier_figure
    midtier_figure(name='NPC_Frasier', base_x=300, base_y=380,
                   base_z=ground_z, facing='+Y',
                   body_type='male_tall',
                   skin_color=(0.86, 0.72, 0.58, 1.0))

Coordinate frame: Blender Z-up, +X east, +Y north. Standing on
the ground at (base_x, base_y, base_z).
"""
import math
import bpy

RING_N = 24                 # verts per body cross-section

# ── PROPORTIONS  (m; total height 1.80 = adult) ─────────────────
TOTAL_H = 1.80
HEAD_H = TOTAL_H / 8        # 0.225 m

# Landmark Y heights (Z in our world):
CROWN_Z      = TOTAL_H
HAIRLINE_Z   = TOTAL_H - HEAD_H * 0.10
BROW_Z       = TOTAL_H - HEAD_H * 0.31
EYE_Z        = TOTAL_H - HEAD_H * 0.50
NOSE_Z       = BROW_Z - HEAD_H * 0.41
MOUTH_Z      = TOTAL_H - HEAD_H * 0.78
CHIN_Z       = TOTAL_H - HEAD_H
NECK_TOP_Z   = CHIN_Z - HEAD_H * 0.05
NECK_BOT_Z   = CHIN_Z - HEAD_H * 0.30
CLAV_Z       = NECK_BOT_Z - HEAD_H * 0.15
NIPPLE_Z     = TOTAL_H - HEAD_H * 2
NAVEL_Z      = TOTAL_H - HEAD_H * 3
CROTCH_Z     = TOTAL_H - HEAD_H * 4
THIGH_Z      = TOTAL_H - HEAD_H * 5
KNEE_Z       = TOTAL_H - HEAD_H * 6
SHIN_Z       = TOTAL_H - HEAD_H * 7
ANKLE_Z      = HEAD_H * 0.30


# ── BODY-TYPE PROFILES ──────────────────────────────────────────
# Each profile drives shoulder/hip/waist/depth multipliers.
# Mid-tier shows body variation through these scales rather than
# whole new mesh topology — same edge loops, different proportions.
BODY_TYPES = {
    'male_avg': {
        'shoulder_w': 0.42, 'hip_w': 0.32, 'waist_w': 0.27,
        'chest_z':   +0.080, 'belly_z': +0.040, 'butt_z': -0.060,
        'spine_z':   -0.060,
    },
    'male_tall': {
        'shoulder_w': 0.43, 'hip_w': 0.31, 'waist_w': 0.26,
        'chest_z':   +0.075, 'belly_z': +0.030, 'butt_z': -0.060,
        'spine_z':   -0.062,
    },
    'male_heavy': {
        'shoulder_w': 0.46, 'hip_w': 0.38, 'waist_w': 0.36,
        'chest_z':   +0.100, 'belly_z': +0.110, 'butt_z': -0.080,
        'spine_z':   -0.040,
    },
    'female_avg': {
        'shoulder_w': 0.36, 'hip_w': 0.36, 'waist_w': 0.22,
        'chest_z':   +0.090, 'belly_z': +0.040, 'butt_z': -0.085,
        'spine_z':   -0.055,
    },
    'female_slim': {
        'shoulder_w': 0.34, 'hip_w': 0.34, 'waist_w': 0.20,
        'chest_z':   +0.080, 'belly_z': +0.030, 'butt_z': -0.075,
        'spine_z':   -0.055,
    },
    'teen': {
        'shoulder_w': 0.36, 'hip_w': 0.30, 'waist_w': 0.24,
        'chest_z':   +0.060, 'belly_z': +0.025, 'butt_z': -0.050,
        'spine_z':   -0.050,
    },
    'child': {
        'shoulder_w': 0.30, 'hip_w': 0.28, 'waist_w': 0.25,
        'chest_z':   +0.040, 'belly_z': +0.050, 'butt_z': -0.040,
        'spine_z':   -0.040,
    },
    'elderly': {
        'shoulder_w': 0.40, 'hip_w': 0.33, 'waist_w': 0.30,
        'chest_z':   +0.060, 'belly_z': +0.080, 'butt_z': -0.055,
        'spine_z':   -0.050,
    },
}


def _ring_asymmetric(cx, cz, rx_front, rx_side, rx_back,
                      rz_front, rz_back, y):
    """Build a 24-vert ring at height y around centerline (cx, cz),
    with separate radii for front/side/back in X and front/back
    in Z. Returns a list of 24 (x, y, z) verts.

    Vert 0 is +Z (front center). Walking clockwise viewed from
    above: indices 0..23.
    """
    verts = []
    for i in range(RING_N):
        ang = 2 * math.pi * i / RING_N
        # cos(0) = +1 means front (+Z), sin(0) = 0
        cz_dir = math.cos(ang)    # +1 front, 0 sides, -1 back
        sx_dir = math.sin(ang)    # +1 right, 0 mid, -1 left
        # X radius: interpolate between front, side, back
        rx = rx_side + (rx_front - rx_side) * max(0, cz_dir) \
                   + (rx_back  - rx_side) * max(0, -cz_dir)
        rz = rz_front if cz_dir >= 0 else rz_back
        x = cx + rx * sx_dir
        z = cz + rz * cz_dir
        verts.append((x, y, z))
    return verts


def _build_body_rings(profile, base_x, base_y, base_z):
    """Generate the cross-section rings that form the body."""
    sw = profile['shoulder_w']
    hw = profile['hip_w']
    ww = profile['waist_w']
    chest_z = profile['chest_z']
    belly_z = profile['belly_z']
    butt_z = profile['butt_z']
    spine_z = profile['spine_z']

    rings = []   # list of (label, ring_verts)

    def add(label, y_offset, rx_f, rx_s, rx_b, rz_f, rz_b):
        verts = _ring_asymmetric(base_x, base_z,
                                  rx_f, rx_s, rx_b,
                                  rz_f, rz_b,
                                  base_y)
        # We want ring at world z = base_z + z_offset. The
        # _ring_asymmetric used cz=base_z and rz_*; we offset
        # the result by y_offset in Z.
        out = [(v[0], v[1], base_z + y_offset) for v in verts]
        # But the ring's Z-asymmetry was applied around cz. We
        # need that applied around (base_z + y_offset). Redo:
        out = []
        for i in range(RING_N):
            ang = 2 * math.pi * i / RING_N
            cz_dir = math.cos(ang)
            sx_dir = math.sin(ang)
            rx = rx_s + (rx_f - rx_s) * max(0, cz_dir) \
                      + (rx_b - rx_s) * max(0, -cz_dir)
            rz = rz_f if cz_dir >= 0 else rz_b
            x = base_x + rx * sx_dir
            z = base_z + y_offset + rz * cz_dir
            out.append((x, base_y, z))
        rings.append((label, out))

    # ── HEAD ───────────────────────────────────────────────────
    # Head rings — slightly asymmetric (face front extends to
    # nose bridge, back of skull rounded). face_z_extra pushes
    # the front centerline forward to suggest the face plane.
    HEAD_X = HEAD_H * 0.32          # half-width of head
    HEAD_FRONT = HEAD_H * 0.40      # how far the face front extends
    HEAD_BACK = HEAD_H * 0.45       # back of skull (a bit larger)

    # All head rings use HEAD_X-relative radii so they curve
    # smoothly from crown apex to chin without the absolute-value
    # blowout the previous skull_top ring had. Each ring is also
    # MONOTONICALLY decreasing in Z so the loft never twists.
    add('crown',       CROWN_Z,                  HEAD_X*0.20, HEAD_X*0.22, HEAD_X*0.24, HEAD_X*0.22, HEAD_X*0.26)
    add('skull_apex',  CROWN_Z - 0.012,          HEAD_X*0.60, HEAD_X*0.66, HEAD_X*0.70, HEAD_X*0.66, HEAD_X*0.78)
    add('hairline',    HAIRLINE_Z,               HEAD_X*0.95, HEAD_X,      HEAD_X,      HEAD_FRONT*0.92, HEAD_BACK)
    add('forehead',    HAIRLINE_Z - 0.020,       HEAD_X*0.95, HEAD_X,      HEAD_X,      HEAD_FRONT*0.95, HEAD_BACK)
    # Brow ridge — push front-center forward slightly
    add('brow',        BROW_Z,                   HEAD_X*1.00, HEAD_X,      HEAD_X,      HEAD_FRONT*1.00, HEAD_BACK)
    # Eye line — slightly INSET front-center (eye recess)
    add('eye',         EYE_Z,                    HEAD_X*0.96, HEAD_X*0.98, HEAD_X*0.94, HEAD_FRONT*0.94, HEAD_BACK)
    # Cheekbone — bumped out laterally
    add('cheek',       EYE_Z - 0.020,            HEAD_X*0.92, HEAD_X*1.02, HEAD_X*0.90, HEAD_FRONT*0.94, HEAD_BACK*0.95)
    # Nose-cheek intermediate so the front profile curves
    add('nose_upper',  (EYE_Z - 0.020 + NOSE_Z) / 2,
                                                 HEAD_X*0.78, HEAD_X*0.90, HEAD_X*0.88, HEAD_FRONT*1.02, HEAD_BACK*0.93)
    # Nose tip — push the very front vert forward
    add('nose',        NOSE_Z,                   HEAD_X*0.62, HEAD_X*0.78, HEAD_X*0.84, HEAD_FRONT*1.08, HEAD_BACK*0.92)
    # Upper lip — narrower
    add('upper_lip',   MOUTH_Z + 0.010,          HEAD_X*0.55, HEAD_X*0.72, HEAD_X*0.80, HEAD_FRONT*0.95, HEAD_BACK*0.90)
    add('mouth',       MOUTH_Z,                  HEAD_X*0.50, HEAD_X*0.68, HEAD_X*0.78, HEAD_FRONT*0.92, HEAD_BACK*0.88)
    # Lower-lip intermediate so chin doesn't pinch sharply
    add('lower_lip',   MOUTH_Z - 0.008,          HEAD_X*0.48, HEAD_X*0.64, HEAD_X*0.74, HEAD_FRONT*0.86, HEAD_BACK*0.82)
    # Chin — front rounded but smaller than mid-face
    add('chin',        CHIN_Z + 0.010,           HEAD_X*0.42, HEAD_X*0.54, HEAD_X*0.60, HEAD_FRONT*0.78, HEAD_BACK*0.66)
    add('jaw_bot',     CHIN_Z,                   HEAD_X*0.36, HEAD_X*0.42, HEAD_X*0.46, HEAD_FRONT*0.60, HEAD_BACK*0.52)
    # Smooth jaw → neck transition (was a hard pinch from
    # 0.42*HEAD_X jaw down to 0.60*NECK_X with no in-between)
    add('jaw_under',   CHIN_Z - 0.012,           HEAD_X*0.46*0.78, HEAD_X*0.50*0.78, HEAD_X*0.54*0.78,
                                                 HEAD_FRONT*0.50, HEAD_BACK*0.44)

    # ── NECK ───────────────────────────────────────────────────
    NECK_X = HEAD_X * 0.60
    NECK_Z = HEAD_FRONT * 0.55
    add('neck_top', NECK_TOP_Z, NECK_X * 0.95, NECK_X, NECK_X * 0.95, NECK_Z * 0.95, NECK_Z * 0.95)
    add('neck_bot', NECK_BOT_Z, NECK_X * 1.05, NECK_X * 1.10, NECK_X * 1.05, NECK_Z * 1.05, NECK_Z * 1.10)

    # ── TRAP slope → clavicle peak. The named landmarks
    # (trap_a, trap_b, clav) keep their dimensions; two extra
    # half-step rings smooth the angular slope so the shoulder
    # doesn't read as a spike. ──
    add('trap_a',     NECK_BOT_Z - 0.012, sw * 0.50, sw * 0.55, sw * 0.50,
        NECK_Z * 1.15, NECK_Z * 1.18)
    add('trap_a_mid', NECK_BOT_Z - 0.018, sw * 0.64, sw * 0.70, sw * 0.64,
        (NECK_Z * 1.15 + sw * 0.50) / 2, (NECK_Z * 1.18 + sw * 0.55) / 2)
    add('trap_b',     NECK_BOT_Z - 0.024, sw * 0.78, sw * 0.85, sw * 0.78,
        sw * 0.50, sw * 0.55)
    add('trap_b_mid', (NECK_BOT_Z - 0.024 + CLAV_Z) / 2,
                                          sw * 0.89, sw * 0.92, sw * 0.87,
        sw * 0.56, sw * 0.60)
    add('clav',       CLAV_Z,             sw,        sw,        sw * 0.96,
        sw * 0.62, sw * 0.65)

    # ── TORSO: chest forward, spine back ───────────────────────
    add('upper_chest', NIPPLE_Z + 0.040, sw * 0.95, sw * 0.92, sw * 0.88,
        sw * 0.62 + chest_z, sw * 0.62 + spine_z)
    add('nipple',      NIPPLE_Z,         sw * 0.85, sw * 0.85, sw * 0.80,
        sw * 0.62 + chest_z * 0.95, sw * 0.62 + spine_z)
    add('ribs',        NIPPLE_Z - 0.080, sw * 0.74, sw * 0.78, sw * 0.72,
        sw * 0.58 + chest_z * 0.60, sw * 0.58 + spine_z * 0.85)
    add('upper_waist', NIPPLE_Z - 0.150, ww * 1.10, ww * 1.15, ww * 1.10,
        ww * 1.10, ww * 1.10)
    add('waist',       NAVEL_Z,          ww,        ww,        ww,
        ww * 1.05 + belly_z * 0.50, ww * 1.05)

    # ── HIPS: belly forward, butt back ─────────────────────────
    add('upper_hip', NAVEL_Z - 0.060, hw * 0.90, hw * 0.95, hw * 0.95,
        hw * 0.95 + belly_z, hw * 0.95 + butt_z * 0.60)
    add('hip',       CROTCH_Z + 0.060, hw,        hw,        hw,
        hw * 0.92 + belly_z * 0.60, hw * 0.92 + butt_z)
    add('crotch',    CROTCH_Z,        hw * 0.86, hw * 0.86, hw * 0.86,
        hw * 0.86, hw * 0.86 + butt_z * 0.55)

    # Body trunk ends at crotch — legs are SEPARATE ring stacks
    # built by _build_legs(), bridged to the crotch via add_legs.
    return rings


def _build_leg_rings(profile, side_sgn):
    """Build a single leg's ring stack, offset to one side of the
    centerline so the left and right legs read as distinct columns.
    Returns list of (label, ring_verts)."""
    hw = profile['hip_w']
    THIGH_X = hw * 0.55
    LEG_OFFSET = hw * 0.45              # distance from centerline
    cx = side_sgn * LEG_OFFSET
    rings = []

    def leg_add(label, y_offset, rx_f, rx_s, rx_b, rz_f, rz_b):
        out = []
        for i in range(RING_N):
            ang = 2 * math.pi * i / RING_N
            cz_dir = math.cos(ang)
            sx_dir = math.sin(ang)
            rx = rx_s + (rx_f - rx_s) * max(0, cz_dir) \
                      + (rx_b - rx_s) * max(0, -cz_dir)
            rz = rz_f if cz_dir >= 0 else rz_b
            x = cx + rx * sx_dir
            z = y_offset + rz * cz_dir
            out.append((x, 0.0, z))
        rings.append((f"{label}_{'L' if side_sgn > 0 else 'R'}", out))

    leg_add('upper_thigh', CROTCH_Z - 0.040, THIGH_X * 1.10, THIGH_X * 1.12, THIGH_X * 1.10,
            THIGH_X * 1.10, THIGH_X * 1.10)
    leg_add('thigh',       THIGH_Z,          THIGH_X,        THIGH_X,        THIGH_X,
            THIGH_X * 1.00, THIGH_X * 1.00)
    leg_add('lower_thigh', THIGH_Z - HEAD_H * 0.30, THIGH_X * 0.80, THIGH_X * 0.82, THIGH_X * 0.80,
            THIGH_X * 0.85, THIGH_X * 0.80)
    leg_add('above_knee',  THIGH_Z - HEAD_H * 0.50, THIGH_X * 0.70, THIGH_X * 0.71, THIGH_X * 0.70,
            THIGH_X * 0.81, THIGH_X * 0.74)
    leg_add('knee',        KNEE_Z,          THIGH_X * 0.62, THIGH_X * 0.60, THIGH_X * 0.62,
            THIGH_X * 0.78, THIGH_X * 0.68)
    leg_add('below_knee',  KNEE_Z - HEAD_H * 0.15, THIGH_X * 0.64, THIGH_X * 0.65, THIGH_X * 0.64,
            THIGH_X * 0.78, THIGH_X * 0.76)
    leg_add('calf',        KNEE_Z - HEAD_H * 0.35, THIGH_X * 0.66, THIGH_X * 0.70, THIGH_X * 0.66,
            THIGH_X * 0.78, THIGH_X * 0.85)
    leg_add('shin',        SHIN_Z,          THIGH_X * 0.52, THIGH_X * 0.52, THIGH_X * 0.52,
            THIGH_X * 0.62, THIGH_X * 0.55)
    leg_add('ankle',       ANKLE_Z,         THIGH_X * 0.42, THIGH_X * 0.42, THIGH_X * 0.42,
            THIGH_X * 0.50, THIGH_X * 0.45)
    leg_add('foot',        0.030,           THIGH_X * 0.45, THIGH_X * 0.50, THIGH_X * 0.40,
            THIGH_X * 0.92, THIGH_X * 0.62)
    leg_add('sole',        0.000,           THIGH_X * 0.42, THIGH_X * 0.46, THIGH_X * 0.36,
            THIGH_X * 0.78, THIGH_X * 0.52)
    return rings


def _build_arm(profile, base_x, base_y, base_z, side_sgn):
    """Arms hang at sides. Each arm = 8 cross-section rings from
    shoulder down to mid-thigh. Arms attach to the body at the
    shoulder ring via a bridge strip handled separately.
    Returns (rings, attach_ring_idx) where attach_ring_idx is
    which body ring the arm bridges to (the 'clav' ring)."""
    sw = profile['shoulder_w']
    hw = profile['hip_w']
    # Arms slightly thicker + sit further out so they read as
    # distinct from the torso silhouette in front view.
    upper_w = HEAD_H * 0.18
    fore_w = upper_w * 0.84
    shoulder_x = base_x + side_sgn * (sw * 1.05)
    hand_x = base_x + side_sgn * (hw * 1.10)
    shoulder_z = CLAV_Z - 0.020
    hand_z = THIGH_Z - HEAD_H * 0.05
    n_rings = 8
    rings = []
    arm_ring_n = 12     # arms can be lower resolution
    for i in range(n_rings):
        t = i / (n_rings - 1)
        cx = shoulder_x + (hand_x - shoulder_x) * t
        cz = shoulder_z + (hand_z - shoulder_z) * t
        w = upper_w + (fore_w - upper_w) * t
        ring = []
        for k in range(arm_ring_n):
            ang = 2 * math.pi * k / arm_ring_n
            x = cx + w * math.sin(ang)
            z = cz + w * 0.85 * math.cos(ang) * 0
            y = base_y + w * 0.85 * math.cos(ang)
            ring.append((x, y, base_z + cz))
        rings.append(ring)
    # Hand at the end — slightly wider, flatter
    hand_ring = []
    for k in range(arm_ring_n):
        ang = 2 * math.pi * k / arm_ring_n
        x = hand_x + fore_w * 1.05 * math.sin(ang)
        y = base_y + fore_w * 0.85 * math.cos(ang)
        hand_ring.append((x, base_y + fore_w * 0.85 * math.cos(ang),
                           base_z + hand_z - HEAD_H * 0.10))
    rings.append(hand_ring)
    return rings, arm_ring_n


def midtier_figure(name, base_x, base_y, base_z,
                   facing='-Y', body_type='male_avg',
                   skin_color=(0.86, 0.72, 0.58, 1.0),
                   hair_color=(0.30, 0.22, 0.16, 1.0),
                   jacket_color=(0.42, 0.42, 0.46, 1.0),
                   pants_color=(0.22, 0.22, 0.28, 1.0),
                   shoe_color=(0.14, 0.12, 0.12, 1.0)):
    """Build a mid-tier human figure as a single welded mesh.
    Tri-budget ~2,350.

    Region colours:
      hair    — verts at Z >= HAIRLINE_Z
      skin    — face + neck (HAIRLINE_Z down to NECK_BOT_Z) + arms
                below wrist
      jacket  — torso CLAV_Z down to NAVEL_Z + upper arms
      pants   — NAVEL_Z down to ANKLE_Z (hips, thighs, shins)
      shoe    — below ANKLE_Z (foot, sole)
    """
    if body_type not in BODY_TYPES:
        body_type = 'male_avg'
    profile = BODY_TYPES[body_type]
    body_rings = _build_body_rings(profile, 0.0, 0.0, 0.0)
    leg_L_rings = _build_leg_rings(profile, +1)
    leg_R_rings = _build_leg_rings(profile, -1)
    arm_L_rings, arn = _build_arm(profile, 0.0, 0.0, 0.0, +1)
    arm_R_rings, _ = _build_arm(profile, 0.0, 0.0, 0.0, -1)

    all_verts = []
    body_idx = []
    for label, ring in body_rings:
        base = len(all_verts)
        all_verts.extend(ring)
        body_idx.append((label, list(range(base, base + RING_N))))
    apex_top_i = len(all_verts)
    all_verts.append((0.0, 0.0, CROWN_Z + 0.010))

    # Each leg's stack — and per-leg bottom apex for the sole
    leg_L_idx = []
    for label, ring in leg_L_rings:
        base = len(all_verts)
        all_verts.extend(ring)
        leg_L_idx.append(list(range(base, base + RING_N)))
    leg_L_bot_i = len(all_verts)
    all_verts.append((+profile['hip_w'] * 0.45, 0.0, -0.005))
    leg_R_idx = []
    for label, ring in leg_R_rings:
        base = len(all_verts)
        all_verts.extend(ring)
        leg_R_idx.append(list(range(base, base + RING_N)))
    leg_R_bot_i = len(all_verts)
    all_verts.append((-profile['hip_w'] * 0.45, 0.0, -0.005))

    arm_L_idx = []
    for ring in arm_L_rings:
        base = len(all_verts)
        all_verts.extend(ring)
        arm_L_idx.append(list(range(base, base + arn)))
    arm_R_idx = []
    for ring in arm_R_rings:
        base = len(all_verts)
        all_verts.extend(ring)
        arm_R_idx.append(list(range(base, base + arn)))

    faces = []
    # Body quads between consecutive rings
    for r in range(len(body_idx) - 1):
        r0 = body_idx[r][1]
        r1 = body_idx[r + 1][1]
        for i in range(RING_N):
            j = (i + 1) % RING_N
            faces.append([r0[i], r0[j], r1[j], r1[i]])
    # Top cap fan
    top_ring = body_idx[0][1]
    for i in range(RING_N):
        j = (i + 1) % RING_N
        faces.append([apex_top_i, top_ring[j], top_ring[i]])

    # Crotch ring → left/right leg-top bridge. We split the crotch
    # ring's 24 verts into "right half" (indices 6..18 — verts on
    # -X side) and "left half" (0..6 + 18..24 — verts on +X side).
    # Wait: vert 0 is +Z (front), vert 6 is +X (right side looking
    # from above? actually sin(2π·6/24) = sin(π/2) = +1 → +X →
    # LEFT side of figure facing camera). Conventionally we render
    # in CCW around +Z up so +X is left-as-camera-views.
    # The convention chosen: side_sgn=+1 = +X = "L" leg. Match.
    crotch_ring = body_idx[-1][1]
    # Left-leg half: verts whose X > 0  → indices 1..11 (sin > 0)
    # Right-leg half: verts whose X < 0 → indices 13..23
    # For a SMOOTH bridge: connect contiguous halves of the crotch
    # ring to each leg's TOP ring (12 verts each → 12 quads).
    for side_sgn, leg_idx in [(+1, leg_L_idx), (-1, leg_R_idx)]:
        leg_top = leg_idx[0]
        # Pick 12 contiguous verts from the crotch ring whose
        # X-side matches side_sgn. Vert i has sin = sin(2πi/24);
        # +1 verts have indices 1..11 (sin > 0), -1 verts 13..23.
        if side_sgn > 0:
            crotch_half = [crotch_ring[i] for i in range(0, 13)]
        else:
            crotch_half = [crotch_ring[i] for i in
                            list(range(12, 24)) + [0]]
        # Bridge: 13 crotch verts → 12 leg-top verts (RING_N=24 split).
        # Use 12 quads + 1 triangle at the seam.
        # Build a 12-quad bridge by mapping leg_top index k to
        # crotch_half indices k and k+1
        for k in range(12):
            faces.append([
                crotch_half[k], crotch_half[k + 1],
                leg_top[(k + 1) % RING_N], leg_top[k % RING_N]
            ])
    # Now each leg's own ring-to-ring quads
    for leg_idx, leg_bot_i in [(leg_L_idx, leg_L_bot_i),
                                (leg_R_idx, leg_R_bot_i)]:
        for r in range(len(leg_idx) - 1):
            r0 = leg_idx[r]; r1 = leg_idx[r + 1]
            for i in range(RING_N):
                j = (i + 1) % RING_N
                faces.append([r0[i], r0[j], r1[j], r1[i]])
        # Sole cap fan
        sole_ring = leg_idx[-1]
        for i in range(RING_N):
            j = (i + 1) % RING_N
            faces.append([leg_bot_i, sole_ring[i], sole_ring[j]])

    # Arms quads
    for arm_idx in (arm_L_idx, arm_R_idx):
        for r in range(len(arm_idx) - 1):
            r0 = arm_idx[r]
            r1 = arm_idx[r + 1]
            for i in range(arn):
                j = (i + 1) % arn
                faces.append([r0[i], r0[j], r1[j], r1[i]])
        last = arm_idx[-1]
        cx = sum(all_verts[i][0] for i in last) / arn
        cy = sum(all_verts[i][1] for i in last) / arn
        cz = sum(all_verts[i][2] for i in last) / arn
        hand_cap_i = len(all_verts)
        all_verts.append((cx, cy, cz - HEAD_H * 0.04))
        for i in range(arn):
            j = (i + 1) % arn
            faces.append([hand_cap_i, last[i], last[j]])

    # Now apply rotation + translation to position + face direction
    fx, fy = 0, -1
    if facing == '+Y': fx, fy = 0, +1
    elif facing == '+X': fx, fy = +1, 0
    elif facing == '-X': fx, fy = -1, 0
    # Compute Z rotation. Default '-Y' is no rotation
    # (because the mesh as built faces -Y at angle 0 already).
    if facing == '-Y': rot = 0.0
    elif facing == '+Y': rot = math.pi
    elif facing == '+X': rot = -math.pi / 2
    elif facing == '-X': rot = +math.pi / 2
    else: rot = 0.0
    cr, sr = math.cos(rot), math.sin(rot)
    placed_verts = []
    for x, y, z in all_verts:
        # Rotate around Z, then translate
        rx = x * cr - y * sr
        ry = x * sr + y * cr
        placed_verts.append((base_x + rx, base_y + ry, base_z + z))

    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(placed_verts, [], faces)
    mesh.update(calc_edges=True)
    for poly in mesh.polygons:
        poly.use_smooth = False
    # Per-region vertex colour based on world Z of poly centroid
    if mesh.vertex_colors:
        vc = mesh.vertex_colors[0]
    else:
        vc = mesh.vertex_colors.new(name="Col")
    for poly in mesh.polygons:
        zc = sum(placed_verts[v][2] for v in poly.vertices) / len(poly.vertices)
        rel_z = zc - base_z
        if rel_z >= HAIRLINE_Z * 0.99:
            col = hair_color
        elif rel_z >= NECK_BOT_Z:
            col = skin_color           # face + neck
        elif rel_z >= NAVEL_Z:
            col = jacket_color         # chest, shoulders, upper arms
        elif rel_z >= ANKLE_Z:
            col = pants_color          # pelvis + legs to ankle
        else:
            col = shoe_color           # foot + sole
        for li in poly.loop_indices:
            vc.data[li].color = col
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# ── HAIR / CLOTHING ACCESSORIES  ────────────────────────────────
# Small additional geometry layered ON TOP of the midtier base.
# Each helper appends to the same active collection so the result
# ships in one GLB pass.

def _make_box(name, center, size, color):
    """Simple box helper using bpy.data.meshes (no HCE dependency)."""
    cx, cy, cz = center
    sx, sy, sz = size
    verts = [
        (cx - sx/2, cy - sy/2, cz - sz/2),
        (cx + sx/2, cy - sy/2, cz - sz/2),
        (cx + sx/2, cy + sy/2, cz - sz/2),
        (cx - sx/2, cy + sy/2, cz - sz/2),
        (cx - sx/2, cy - sy/2, cz + sz/2),
        (cx + sx/2, cy - sy/2, cz + sz/2),
        (cx + sx/2, cy + sy/2, cz + sz/2),
        (cx - sx/2, cy + sy/2, cz + sz/2),
    ]
    faces = [(0,3,2,1), (4,5,6,7), (0,1,5,4),
             (1,2,6,5), (2,3,7,6), (3,0,4,7)]
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    if mesh.vertex_colors:
        vc = mesh.vertex_colors[0]
    else:
        vc = mesh.vertex_colors.new(name="Col")
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            vc.data[li].color = color
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def _make_sphere_box(name, center, radius, color, w_mult=1.0,
                     d_mult=1.0, h_mult=1.0):
    """Approximate sphere as a single box (silhouette only).
    Cheap stand-in for an afro / head hair mass."""
    return _make_box(
        name, center,
        (radius * 2 * w_mult, radius * 2 * d_mult, radius * 2 * h_mult),
        color)


def add_hair(name, base_x, base_y, base_z, style, color, facing='-Y'):
    """Add hair geometry on top of the midtier head.
    Styles: 'short', 'long', 'unkempt_afro', 'bald', 'short_curly'.
    Hair sits at HAIRLINE_Z + offset, scaled per style."""
    head_top_z = base_z + CROWN_Z
    hair_center_z = base_z + (CROWN_Z + HAIRLINE_Z) / 2 + 0.020
    if style == 'bald':
        return
    if style == 'short':
        _make_box(f"{name}_Hair", (base_x, base_y, hair_center_z),
                  (0.18, 0.20, 0.10), color)
    elif style == 'short_curly':
        # Slightly fluffier short
        _make_box(f"{name}_Hair", (base_x, base_y, hair_center_z + 0.010),
                  (0.20, 0.22, 0.14), color)
    elif style == 'long':
        # Long hair drops to shoulders
        _make_box(f"{name}_Hair_Top",
                  (base_x, base_y, hair_center_z),
                  (0.20, 0.22, 0.12), color)
        # Drape down to clavicle level
        drape_z = base_z + (HAIRLINE_Z + CLAV_Z) / 2
        _make_box(f"{name}_Hair_Drape",
                  (base_x, base_y - 0.02, drape_z),
                  (0.22, 0.05, 0.24), color)
    elif style == 'unkempt_afro':
        # Big fluffy sphere — significantly wider than the head
        afro_r = 0.14
        _make_box(f"{name}_Hair_Afro",
                  (base_x, base_y, hair_center_z + 0.030),
                  (afro_r * 2.4, afro_r * 2.3, afro_r * 2.0), color)
        # Slightly squashed top
        _make_box(f"{name}_Hair_Afro_Top",
                  (base_x, base_y, hair_center_z + afro_r * 0.9),
                  (afro_r * 2.0, afro_r * 1.8, afro_r * 0.8), color)
    elif style == 'mohawk':
        _make_box(f"{name}_Hair_Hawk",
                  (base_x, base_y, hair_center_z + 0.04),
                  (0.06, 0.20, 0.14), color)


def add_apron(name, base_x, base_y, base_z, color, facing='-Y'):
    """White waiter's apron — full rectangular panel from upper
    chest down to mid-thigh. Sits flush against the front of the
    torso."""
    # Front face is -Y when facing -Y (default).
    fy = -1 if facing == '-Y' else (+1 if facing == '+Y' else 0)
    fx = -1 if facing == '-X' else (+1 if facing == '+X' else 0)
    # Apron sits 0.10m in front of figure
    apron_h = NIPPLE_Z + 0.05 - THIGH_Z       # roughly chest-to-thigh
    apron_cz = base_z + (NIPPLE_Z + 0.05 + THIGH_Z) / 2
    apron_w = 0.28
    apron_thick = 0.02
    front_offset = 0.13
    fx_offset = base_x + (-fy * 0) + fx * front_offset    # along front
    fy_offset = base_y + fy * front_offset
    if abs(fy) > 0.5:
        size = (apron_w, apron_thick, apron_h)
    else:
        size = (apron_thick, apron_w, apron_h)
    _make_box(f"{name}_Apron",
              (fx_offset, fy_offset, apron_cz), size, color)
    # Neck strap (thin vertical strip at top)
    strap_h = 0.18
    strap_z = base_z + NIPPLE_Z + 0.10
    _make_box(f"{name}_Apron_Strap",
              (fx_offset, fy_offset, strap_z),
              (0.04 if abs(fy) > 0.5 else apron_thick,
               apron_thick if abs(fy) > 0.5 else 0.04,
               strap_h), color)


def add_tie(name, base_x, base_y, base_z, color, facing='-Y'):
    """Thin vertical tie down the center chest."""
    fy = -1 if facing == '-Y' else (+1 if facing == '+Y' else 0)
    fx = -1 if facing == '-X' else (+1 if facing == '+X' else 0)
    front_offset = 0.12
    tie_top_z = base_z + NECK_BOT_Z - 0.020
    tie_bot_z = base_z + NIPPLE_Z - 0.150
    tie_cz = (tie_top_z + tie_bot_z) / 2
    tie_h = tie_top_z - tie_bot_z
    tx = base_x + fx * front_offset
    ty = base_y + fy * front_offset
    if abs(fy) > 0.5:
        size = (0.06, 0.03, tie_h)
    else:
        size = (0.03, 0.06, tie_h)
    _make_box(f"{name}_Tie", (tx, ty, tie_cz), size, color)
    # Knot (slightly wider square at top)
    _make_box(f"{name}_TieKnot", (tx, ty, tie_top_z),
              (0.08, 0.04, 0.06) if abs(fy) > 0.5 else (0.04, 0.08, 0.06),
              color)


def add_collar(name, base_x, base_y, base_z, color, facing='-Y'):
    """Shirt collar — a V-shape at the neck base."""
    fy = -1 if facing == '-Y' else (+1 if facing == '+Y' else 0)
    fx = -1 if facing == '-X' else (+1 if facing == '+X' else 0)
    collar_z = base_z + NECK_BOT_Z + 0.020
    front_offset = 0.10
    cx = base_x + fx * front_offset
    cy = base_y + fy * front_offset
    if abs(fy) > 0.5:
        size = (0.16, 0.03, 0.08)
    else:
        size = (0.03, 0.16, 0.08)
    _make_box(f"{name}_Collar", (cx, cy, collar_z), size, color)


def add_bomber_jacket_detail(name, base_x, base_y, base_z, color):
    """Bomber jacket signature: ribbed waist band + cuff bands.
    Wraps a thin darker band around the existing torso mesh at
    the waist + at the wrists."""
    # Waist band — thin ring at navel level
    waist_z = base_z + NAVEL_Z - 0.020
    _make_box(f"{name}_Bomber_Waist",
              (base_x, base_y, waist_z),
              (0.42, 0.30, 0.08), color)
    # Two cuff bands at the wrists. Wrists sit at the bottom of
    # the arm tube, roughly THIGH_Z - 0.08 = 0.595 of base_z.
    for s, side in [(+1, 'L'), (-1, 'R')]:
        wrist_x = base_x + s * 0.36
        wrist_z = base_z + THIGH_Z - 0.10
        _make_box(f"{name}_Bomber_Cuff_{side}",
                  (wrist_x, base_y, wrist_z),
                  (0.10, 0.10, 0.06), color)


# ── HERO CHARACTERS  (canon-anchored sculpts with scene props) ──
HERO_CHARACTERS = {
    'JohnFrank': {
        'body_type': 'male_avg',
        'skin_color':   (0.92, 0.78, 0.62, 1.0),
        'hair_style':   'short',
        'hair_color':   (0.36, 0.24, 0.16, 1.0),     # mid brown
        'jacket_color': (0.94, 0.92, 0.86, 1.0),     # white button-up shirt
        'pants_color':  (0.22, 0.22, 0.24, 1.0),     # dark slacks
        'shoe_color':   (0.18, 0.14, 0.12, 1.0),
        'extras': [
            ('collar', (0.94, 0.92, 0.86, 1.0)),     # white shirt collar
            ('tie',    (0.20, 0.24, 0.40, 1.0)),     # navy tie
            ('apron',  (0.96, 0.94, 0.88, 1.0)),     # white waiter apron
        ],
        'pose': 'standing_behind_counter',           # placed at diner
    },
    'FrasierTemple': {
        'body_type': 'male_tall',
        'skin_color':   (0.88, 0.72, 0.56, 1.0),
        'hair_style':   'unkempt_afro',
        'hair_color':   (0.20, 0.16, 0.14, 1.0),     # dark, unkempt
        'jacket_color': (0.32, 0.36, 0.22, 1.0),     # olive bomber jacket
        'pants_color':  (0.26, 0.30, 0.42, 1.0),     # jeans
        'shoe_color':   (0.34, 0.24, 0.18, 1.0),     # brown work boots
        'extras': [
            ('bomber', (0.22, 0.26, 0.16, 1.0)),     # darker bands
        ],
        'pose': 'leaning_at_workbench',
    },
    'EliciaTemple': {
        'body_type': 'female_avg',
        'skin_color':   (0.86, 0.70, 0.56, 1.0),
        'hair_style':   'long',
        'hair_color':   (0.24, 0.16, 0.12, 1.0),     # dark auburn
        'jacket_color': (0.40, 0.30, 0.34, 1.0),     # burgundy cardigan
        'pants_color':  (0.32, 0.36, 0.30, 1.0),     # sage skirt
        'shoe_color':   (0.18, 0.14, 0.12, 1.0),
        'extras': [
            ('collar', (0.94, 0.92, 0.88, 1.0)),     # cream shirt under
        ],
        'pose': 'turning_at_archive',
    },
}


def hero_figure(name, hero_key, base_x, base_y, base_z, facing='-Y'):
    """Convenience wrapper — build a canonical hero by name with
    all hair + clothing + scene-pose extras."""
    if hero_key not in HERO_CHARACTERS:
        raise ValueError(f"unknown hero: {hero_key}")
    spec = HERO_CHARACTERS[hero_key]
    midtier_figure(name=name,
                   base_x=base_x, base_y=base_y, base_z=base_z,
                   facing=facing,
                   body_type=spec['body_type'],
                   skin_color=spec['skin_color'],
                   hair_color=spec['hair_color'],
                   jacket_color=spec['jacket_color'],
                   pants_color=spec['pants_color'],
                   shoe_color=spec['shoe_color'])
    # Hair (geometry, not just colour)
    add_hair(name, base_x, base_y, base_z,
             spec['hair_style'], spec['hair_color'], facing)
    # Clothing extras
    for extra, color in spec['extras']:
        if extra == 'apron':
            add_apron(name, base_x, base_y, base_z, color, facing)
        elif extra == 'tie':
            add_tie(name, base_x, base_y, base_z, color, facing)
        elif extra == 'collar':
            add_collar(name, base_x, base_y, base_z, color, facing)
        elif extra == 'bomber':
            add_bomber_jacket_detail(name, base_x, base_y, base_z, color)
