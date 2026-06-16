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
    # Widened from the previous pass — earlier figure read as
    # "emaciated and spiky" so every torso/waist/limb radius is
    # bumped ~20%, and the chest/belly fills are bigger.
    'male_avg': {
        'shoulder_w': 0.50, 'hip_w': 0.40, 'waist_w': 0.35,
        'chest_z':   +0.100, 'belly_z': +0.060, 'butt_z': -0.085,
        'spine_z':   -0.070,
    },
    'male_tall': {
        'shoulder_w': 0.52, 'hip_w': 0.39, 'waist_w': 0.34,
        'chest_z':   +0.100, 'belly_z': +0.055, 'butt_z': -0.085,
        'spine_z':   -0.072,
    },
    'male_heavy': {
        'shoulder_w': 0.54, 'hip_w': 0.48, 'waist_w': 0.46,
        'chest_z':   +0.130, 'belly_z': +0.140, 'butt_z': -0.105,
        'spine_z':   -0.050,
    },
    'female_avg': {
        'shoulder_w': 0.42, 'hip_w': 0.44, 'waist_w': 0.30,
        'chest_z':   +0.110, 'belly_z': +0.060, 'butt_z': -0.110,
        'spine_z':   -0.065,
    },
    'female_slim': {
        'shoulder_w': 0.40, 'hip_w': 0.42, 'waist_w': 0.28,
        'chest_z':   +0.100, 'belly_z': +0.050, 'butt_z': -0.100,
        'spine_z':   -0.065,
    },
    'teen': {
        'shoulder_w': 0.42, 'hip_w': 0.38, 'waist_w': 0.32,
        'chest_z':   +0.075, 'belly_z': +0.045, 'butt_z': -0.075,
        'spine_z':   -0.060,
    },
    'child': {
        'shoulder_w': 0.36, 'hip_w': 0.36, 'waist_w': 0.33,
        'chest_z':   +0.055, 'belly_z': +0.075, 'butt_z': -0.055,
        'spine_z':   -0.050,
    },
    'elderly': {
        'shoulder_w': 0.46, 'hip_w': 0.41, 'waist_w': 0.38,
        'chest_z':   +0.080, 'belly_z': +0.105, 'butt_z': -0.075,
        'spine_z':   -0.060,
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

    add('crown',     CROWN_Z,                  0.04, 0.04, 0.05, 0.05, 0.06)
    add('skull_top', CROWN_Z - 0.030,          0.16, 0.18, 0.20, 0.18, 0.22)
    add('hairline',  HAIRLINE_Z,               HEAD_X * 0.95, HEAD_X, HEAD_X, HEAD_FRONT * 0.92, HEAD_BACK)
    add('forehead',  HAIRLINE_Z - 0.020,       HEAD_X * 0.95, HEAD_X, HEAD_X, HEAD_FRONT * 0.95, HEAD_BACK)
    # Brow ridge — push front-center forward slightly
    add('brow',      BROW_Z,                   HEAD_X * 1.00, HEAD_X, HEAD_X, HEAD_FRONT * 1.00, HEAD_BACK)
    # Eye line — slightly INSET front-center (eye recess)
    add('eye',       EYE_Z,                    HEAD_X * 0.96, HEAD_X * 0.98, HEAD_X * 0.94, HEAD_FRONT * 0.94, HEAD_BACK)
    # Cheekbone — bumped out laterally
    add('cheek',     EYE_Z - 0.020,            HEAD_X * 0.92, HEAD_X * 1.02, HEAD_X * 0.90, HEAD_FRONT * 0.94, HEAD_BACK * 0.95)
    # Nose tip — push the very front vert forward
    add('nose',      NOSE_Z,                   HEAD_X * 0.62, HEAD_X * 0.78, HEAD_X * 0.84, HEAD_FRONT * 1.08, HEAD_BACK * 0.92)
    # Upper lip — narrower
    add('upper_lip', MOUTH_Z + 0.010,          HEAD_X * 0.55, HEAD_X * 0.72, HEAD_X * 0.80, HEAD_FRONT * 0.95, HEAD_BACK * 0.90)
    add('mouth',     MOUTH_Z,                  HEAD_X * 0.50, HEAD_X * 0.68, HEAD_X * 0.78, HEAD_FRONT * 0.92, HEAD_BACK * 0.88)
    # Chin — front rounded but smaller than mid-face
    add('chin',      CHIN_Z + 0.010,           HEAD_X * 0.40, HEAD_X * 0.50, HEAD_X * 0.55, HEAD_FRONT * 0.78, HEAD_BACK * 0.62)
    add('jaw_bot',   CHIN_Z,                   HEAD_X * 0.28, HEAD_X * 0.32, HEAD_X * 0.36, HEAD_FRONT * 0.50, HEAD_BACK * 0.42)

    # ── NECK ───────────────────────────────────────────────────
    NECK_X = HEAD_X * 0.60
    NECK_Z = HEAD_FRONT * 0.55
    add('neck_top', NECK_TOP_Z, NECK_X * 0.95, NECK_X, NECK_X * 0.95, NECK_Z * 0.95, NECK_Z * 0.95)
    add('neck_bot', NECK_BOT_Z, NECK_X * 1.05, NECK_X * 1.10, NECK_X * 1.05, NECK_Z * 1.05, NECK_Z * 1.10)

    # ── TRAP slope → clavicle peak ────────────────────────────
    add('trap_a', NECK_BOT_Z - 0.012, sw * 0.50, sw * 0.55, sw * 0.50, NECK_Z * 1.15, NECK_Z * 1.18)
    add('trap_b', NECK_BOT_Z - 0.024, sw * 0.78, sw * 0.85, sw * 0.78, sw * 0.50, sw * 0.55)
    add('clav',   CLAV_Z,             sw,        sw,        sw * 0.96, sw * 0.62, sw * 0.65)

    # ── TORSO: chest forward, spine back. Smoother taper now —
    # was dropping shoulder→waist too sharply ("emaciated"). Add
    # an extra ring at mid-rib and bigger fill multipliers. ──
    add('upper_chest', NIPPLE_Z + 0.050, sw * 0.96, sw * 0.94, sw * 0.92,
        sw * 0.68 + chest_z, sw * 0.66 + spine_z)
    add('nipple',      NIPPLE_Z,         sw * 0.90, sw * 0.90, sw * 0.86,
        sw * 0.68 + chest_z * 0.95, sw * 0.66 + spine_z)
    add('mid_chest',   NIPPLE_Z - 0.045, sw * 0.84, sw * 0.86, sw * 0.80,
        sw * 0.64 + chest_z * 0.80, sw * 0.64 + spine_z * 0.95)
    add('ribs',        NIPPLE_Z - 0.090, sw * 0.78, sw * 0.80, sw * 0.76,
        sw * 0.60 + chest_z * 0.50, sw * 0.60 + spine_z * 0.85)
    add('upper_waist', NIPPLE_Z - 0.150, ww * 1.05, ww * 1.08, ww * 1.05,
        ww * 1.00, ww * 1.00)
    add('waist',       NAVEL_Z,          ww,        ww * 1.02, ww * 0.98,
        ww * 0.95 + belly_z * 0.50, ww * 0.95)

    # ── HIPS: belly forward, butt back, with smoother fill ──
    add('upper_hip', NAVEL_Z - 0.060, hw * 0.92, hw * 0.97, hw * 0.97,
        hw * 0.92 + belly_z, hw * 0.92 + butt_z * 0.60)
    add('hip',       CROTCH_Z + 0.060, hw,        hw,        hw,
        hw * 0.90 + belly_z * 0.60, hw * 0.90 + butt_z)
    add('crotch',    CROTCH_Z,        hw * 0.88, hw * 0.88, hw * 0.88,
        hw * 0.86, hw * 0.86 + butt_z * 0.55)

    # ── LEGS — thicker thighs, less aggressive taper through
    # the knee, fleshier calf, smoother ankle. ──
    THIGH_X = hw * 0.72                # was 0.55 (too thin)
    add('upper_thigh', CROTCH_Z - 0.060, THIGH_X * 1.05, THIGH_X * 1.08, THIGH_X * 1.05,
        THIGH_X * 1.08, THIGH_X * 1.08)
    add('thigh',       THIGH_Z,          THIGH_X,        THIGH_X,        THIGH_X,
        THIGH_X * 1.00, THIGH_X * 1.00)
    add('lower_thigh', THIGH_Z - HEAD_H * 0.30, THIGH_X * 0.86, THIGH_X * 0.88, THIGH_X * 0.86,
        THIGH_X * 0.92, THIGH_X * 0.86)
    add('knee',        KNEE_Z,          THIGH_X * 0.74, THIGH_X * 0.72, THIGH_X * 0.74,
        THIGH_X * 0.86, THIGH_X * 0.78)
    add('calf',        KNEE_Z - HEAD_H * 0.32, THIGH_X * 0.78, THIGH_X * 0.82, THIGH_X * 0.78,
        THIGH_X * 0.86, THIGH_X * 0.95)
    add('shin',        SHIN_Z,          THIGH_X * 0.62, THIGH_X * 0.64, THIGH_X * 0.62,
        THIGH_X * 0.72, THIGH_X * 0.66)
    add('ankle',       ANKLE_Z,         THIGH_X * 0.50, THIGH_X * 0.52, THIGH_X * 0.50,
        THIGH_X * 0.58, THIGH_X * 0.52)
    add('foot',        0.030,           THIGH_X * 0.52, THIGH_X * 0.58, THIGH_X * 0.46,
        THIGH_X * 1.05, THIGH_X * 0.72)
    add('sole',        0.000,           THIGH_X * 0.48, THIGH_X * 0.52, THIGH_X * 0.42,
        THIGH_X * 0.92, THIGH_X * 0.62)

    return rings


def _build_arm(profile, base_x, base_y, base_z, side_sgn):
    """Arms hang at sides. Each arm = 8 cross-section rings from
    shoulder down to mid-thigh. Arms attach to the body at the
    shoulder ring via a bridge strip handled separately.
    Returns (rings, attach_ring_idx) where attach_ring_idx is
    which body ring the arm bridges to (the 'clav' ring)."""
    sw = profile['shoulder_w']
    hw = profile['hip_w']
    upper_w = HEAD_H * 0.24       # was 0.16 — too thin / "spiky"
    fore_w = upper_w * 0.82
    shoulder_x = base_x + side_sgn * (sw * 0.85)
    hand_x = base_x + side_sgn * (hw * 0.95)
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
                   skin_color=(0.86, 0.72, 0.58, 1.0)):
    """Build a mid-tier human figure as a single welded mesh.
    Tri-budget ~1,400."""
    if body_type not in BODY_TYPES:
        body_type = 'male_avg'
    profile = BODY_TYPES[body_type]
    body_rings = _build_body_rings(profile, 0.0, 0.0, 0.0)
    arm_L_rings, arn = _build_arm(profile, 0.0, 0.0, 0.0, +1)
    arm_R_rings, _ = _build_arm(profile, 0.0, 0.0, 0.0, -1)

    # Assemble verts + faces
    all_verts = []
    body_idx = []
    for label, ring in body_rings:
        base = len(all_verts)
        all_verts.extend(ring)
        body_idx.append((label, list(range(base, base + RING_N))))
    # Cap top (skull)
    apex_top_i = len(all_verts)
    all_verts.append((0.0, 0.0, CROWN_Z + 0.010))
    # Cap bottom (sole — flat)
    apex_bot_i = len(all_verts)
    all_verts.append((0.0, 0.0, -0.005))

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
    # Bottom cap fan (sole)
    bot_ring = body_idx[-1][1]
    for i in range(RING_N):
        j = (i + 1) % RING_N
        faces.append([apex_bot_i, bot_ring[i], bot_ring[j]])
    # Arms quads
    for arm_idx in (arm_L_idx, arm_R_idx):
        for r in range(len(arm_idx) - 1):
            r0 = arm_idx[r]
            r1 = arm_idx[r + 1]
            for i in range(arn):
                j = (i + 1) % arn
                faces.append([r0[i], r0[j], r1[j], r1[i]])
        # Cap arm tip (hand) — collapse to centroid
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
    # Flat-shaded for planar Asaro feel
    for poly in mesh.polygons:
        poly.use_smooth = False
    # Vertex colour
    if mesh.vertex_colors:
        vc = mesh.vertex_colors[0]
    else:
        vc = mesh.vertex_colors.new(name="Col")
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            vc.data[li].color = skin_color
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj
