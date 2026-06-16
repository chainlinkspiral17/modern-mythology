"""
human_sculpt_v2.py — REBUILT FROM SCRATCH 2026-06-15
═══════════════════════════════════════════════════════════════════
The previous human_sculpt.py accumulated 14 sculpt passes of
incremental "push/pull" detail on top of an axis-aligned-primitive
foundation that fundamentally read as Lego stacks, not humans.

The user's reference is the LOW-POLY SUIT MAN (faceted figure with
clear walking pose, 1:8 head ratio, broad-shoulders-tapered-waist).

Design from scratch:
  • 1.80 m total height anchored to a CANONICAL 8-HEAD PROPORTION
  • Head (h_head = total/8 = 0.225 m), faceted 6-ring skull,
    visible neck below
  • Trapezoidal torso prism, 8-sided horizontal cross-section,
    oriented to facing. Three rings: hip / waist / shoulder.
  • Arms: two ORIENTED tapered cylinders per side (upper + forearm)
    hung at +8° outward from vertical with a 12° elbow bend forward.
    Hand wedge at the end.
  • Legs: two ORIENTED tapered cylinders per side (thigh + shin)
    with a default WALKING STANCE — left leg 12 cm forward, right
    leg 8 cm back. Knee 15° bend on the forward leg.
  • Feet: pointed loafer wedges aligned to facing.

Public API unchanged: human_figure(name, base_x, base_y, base_z,
scale=1.0, facing='-Y', body_type='male_avg', ...) returns
{hands, head_base_z, shoulder_z}.

bpy is the only external dependency; the module loads under a stub
for the preview tool / overlap audit / smoke tests.
"""
import math
import bpy


# ── PROPORTIONS ────────────────────────────────────────────────────
# All distances in METRES at scale = 1.0. CANONICAL 8-HEAD body —
# head h = total / 8 = 0.225 m. Everything else flows from that.
PROP = {
    "total_h":        1.80,
    "head_h":         0.250,   # vertical extent of the head (taller
                                # than the v1 0.225 — was reading as
                                # "small head on a pin")
    # _ring() uses HALF-WIDTHS. head_w_max half = 0.078 → 15.6cm full,
    # at the upper end of real head width (~14-15cm). Slight upsize
    # over the previous 13.6 cm since the head looked overly small
    # against the broad shoulders.
    "head_w_max":     0.078,   # half-width at cheekbones (15.6cm full)
    "head_w_chin":    0.044,
    "head_d_max":     0.098,   # half-depth ear-to-nose (19.6cm full)
    "head_d_chin":    0.052,

    "neck_h":         0.060,   # SHORT neck — was 0.09 reading as long
    "neck_r_top":     0.062,   # THICKER (12.4cm full at head base)
    "neck_r_bot":     0.075,   # 15cm at shoulder blend (was 11cm)

    "shoulder_w":     0.500,   # full shoulder span (4× head_h /3)
    "torso_h":        0.610,   # neck base → top of pelvis
    "torso_chest_d":  0.230,
    "torso_waist_w":  0.300,
    "torso_waist_d":  0.180,
    "torso_hip_w":    0.380,
    "torso_hip_d":    0.200,
    "torso_bottom_drop": 0.020,   # pelvis lip below torso bottom ring

    "arm_upper_h":    0.330,
    "arm_lower_h":    0.330,
    "arm_r_shoulder": 0.060,
    "arm_r_elbow":    0.052,
    "arm_r_wrist":    0.044,
    "hand_l":         0.090,
    "hand_w":         0.075,

    "leg_h":          0.860,   # hip → ground
    "leg_thigh_frac": 0.50,    # thigh = 50% of leg
    "leg_r_hip":      0.090,
    "leg_r_knee":     0.075,
    "leg_r_ankle":    0.068,
    "leg_separation": 0.090,   # half-distance between leg centres

    "foot_l":         0.270,
    "foot_w":         0.105,
    "foot_h":         0.075,
}


BODY_PROFILES = {
    'male_avg':   {},
    'male_tall':  {'leg_h': 1.10, 'torso_h': 1.04,
                   'shoulder_w': 0.97, 'arm_upper_h': 1.06,
                   'arm_lower_h': 1.06,
                   'torso_chest_d': 0.94, 'torso_waist_d': 0.92,
                   'torso_waist_w': 0.92, 'torso_hip_w': 0.95,
                   'leg_r_hip': 0.92, 'leg_r_knee': 0.92,
                   'leg_r_ankle': 0.90, 'head_h': 0.96},
    'male_heavy': {'leg_h': 0.94, 'torso_h': 0.96,
                   'shoulder_w': 1.06,
                   'torso_chest_d': 1.20, 'torso_waist_d': 1.40,
                   'torso_waist_w': 1.30, 'torso_hip_w': 1.20,
                   'arm_r_shoulder': 1.15, 'arm_r_elbow': 1.15,
                   'arm_r_wrist': 1.10,
                   'leg_r_hip': 1.18, 'leg_r_knee': 1.15,
                   'leg_r_ankle': 1.10, 'head_h': 1.04},
    'female_avg': {'leg_h': 0.96, 'torso_h': 0.94,
                   'shoulder_w': 0.84,
                   'torso_chest_d': 0.85, 'torso_waist_w': 0.78,
                   'torso_waist_d': 0.80, 'torso_hip_w': 1.06,
                   'arm_upper_h': 0.96, 'arm_lower_h': 0.96,
                   'arm_r_shoulder': 0.85, 'arm_r_elbow': 0.85,
                   'arm_r_wrist': 0.82,
                   'leg_r_hip': 0.95, 'leg_r_knee': 0.92,
                   'leg_r_ankle': 0.90, 'head_h': 0.94},
    'female_slim':{'leg_h': 0.98, 'torso_h': 0.92,
                   'shoulder_w': 0.80,
                   'torso_chest_d': 0.78, 'torso_waist_w': 0.70,
                   'torso_waist_d': 0.72, 'torso_hip_w': 0.92,
                   'arm_upper_h': 0.95, 'arm_lower_h': 0.95,
                   'arm_r_shoulder': 0.78, 'arm_r_elbow': 0.78,
                   'arm_r_wrist': 0.76,
                   'leg_r_hip': 0.85, 'leg_r_knee': 0.82,
                   'leg_r_ankle': 0.80, 'head_h': 0.90},
    'teen':       {'leg_h': 0.94, 'torso_h': 0.88,
                   'shoulder_w': 0.88,
                   'torso_chest_d': 0.82, 'torso_waist_w': 0.78,
                   'torso_waist_d': 0.78,
                   'arm_upper_h': 0.96, 'arm_lower_h': 0.98,
                   'arm_r_shoulder': 0.84, 'arm_r_elbow': 0.82,
                   'arm_r_wrist': 0.80,
                   'leg_r_hip': 0.86, 'leg_r_knee': 0.84,
                   'leg_r_ankle': 0.82, 'head_h': 1.02},
    'child':      {'leg_h': 0.60, 'torso_h': 0.78,
                   'shoulder_w': 0.65,
                   'torso_chest_d': 0.72, 'torso_waist_w': 0.80,
                   'torso_waist_d': 0.85, 'torso_hip_w': 0.78,
                   'arm_upper_h': 0.66, 'arm_lower_h': 0.68,
                   'arm_r_shoulder': 0.72, 'arm_r_elbow': 0.72,
                   'arm_r_wrist': 0.70,
                   'leg_r_hip': 0.78, 'leg_r_knee': 0.76,
                   'leg_r_ankle': 0.74,
                   'foot_l': 0.72, 'foot_w': 0.78,
                   'hand_l': 0.78, 'hand_w': 0.78,
                   'neck_h': 0.70, 'neck_r_top': 0.85,
                   'neck_r_bot': 0.85,
                   'leg_separation': 0.75,
                   'head_h': 1.20, 'head_w_max': 1.05,
                   'head_d_max': 1.05},
    'elderly':    {'leg_h': 0.95, 'torso_h': 0.96,
                   'shoulder_w': 0.94,
                   'torso_chest_d': 0.92, 'torso_waist_d': 1.05,
                   'torso_waist_w': 1.05,
                   'arm_r_shoulder': 0.88, 'arm_r_elbow': 0.85,
                   'arm_r_wrist': 0.82,
                   'leg_r_hip': 0.90, 'leg_r_knee': 0.88,
                   'leg_r_ankle': 0.86},
}


def _props_for(body_type, scale):
    """Build a per-call PROP dict by applying body_type multipliers
    on the baseline. Returns absolute values (already × scale)."""
    profile = BODY_PROFILES.get(body_type, {})
    p = {}
    for key, base_val in PROP.items():
        mult = profile.get(key, 1.0)
        p[key] = base_val * mult * scale
    return p


# ── LOW-LEVEL MESH HELPERS ─────────────────────────────────────────


def _finalize_mesh(name, verts, faces, color):
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="Col")
    layer = mesh.vertex_colors["Col"]
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            layer.data[li].color = color
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def _ring(cx, cy, cz, half_x, half_y, segments, fwd, prp):
    """Generate a horizontal elliptical ring of vertices oriented
    so half_x is along the perpendicular-to-facing axis and half_y
    is along the facing axis. Returns list of verts."""
    fx, fy = fwd
    px, py = prp
    out = []
    for k in range(segments):
        ang = 2.0 * math.pi * k / segments
        ca, sa = math.cos(ang), math.sin(ang)
        vx = cx + ca * half_x * px + sa * half_y * fx
        vy = cy + ca * half_x * py + sa * half_y * fy
        out.append((vx, vy, cz))
    return out


def _prism(name, rings, segments, color, close_top=True, close_bot=True):
    """Build a vertical prism from a list of (z, half_x, half_y)
    rings. fwd/prp baked into the ring verts via _ring."""
    verts = []
    for ring in rings:
        verts.extend(ring)
    faces = []
    n_rings = len(rings) // segments    # rings is FLAT list, n verts
    # Wait, we pass a flat list of pre-generated verts. n_rings is
    # len(rings) // segments.
    n_rings = len(verts) // segments
    for r in range(n_rings - 1):
        a = r * segments
        b = (r + 1) * segments
        for k in range(segments):
            nk = (k + 1) % segments
            faces.append([a + k, a + nk, b + nk, b + k])
    if close_top:
        # Add top center vertex + fan
        zs_top = [verts[(n_rings - 1) * segments + k][2]
                  for k in range(segments)]
        xs_top = [verts[(n_rings - 1) * segments + k][0]
                  for k in range(segments)]
        ys_top = [verts[(n_rings - 1) * segments + k][1]
                  for k in range(segments)]
        verts.append((sum(xs_top) / segments,
                      sum(ys_top) / segments,
                      sum(zs_top) / segments))
        center_i = len(verts) - 1
        for k in range(segments):
            nk = (k + 1) % segments
            faces.append([center_i,
                          (n_rings - 1) * segments + k,
                          (n_rings - 1) * segments + nk])
    if close_bot:
        xs_b = [verts[k][0] for k in range(segments)]
        ys_b = [verts[k][1] for k in range(segments)]
        zs_b = [verts[k][2] for k in range(segments)]
        verts.append((sum(xs_b) / segments,
                      sum(ys_b) / segments,
                      sum(zs_b) / segments))
        center_i = len(verts) - 1
        for k in range(segments):
            nk = (k + 1) % segments
            faces.append([center_i, nk, k])
    _finalize_mesh(name, verts, faces, color)


def _oriented_cyl(name, p0, p1, r0, r1, color, segments=8):
    """Tapered cylinder from p0 (radius r0) to p1 (radius r1).
    Computes a perpendicular frame so the cylinder can point in any
    3D direction."""
    px = p1[0] - p0[0]
    py = p1[1] - p0[1]
    pz = p1[2] - p0[2]
    length = math.sqrt(px * px + py * py + pz * pz)
    if length < 0.001:
        return None
    dx, dy, dz = px / length, py / length, pz / length
    if abs(dz) < 0.9:
        ux, uy, uz = 0.0, 0.0, 1.0
    else:
        ux, uy, uz = 1.0, 0.0, 0.0
    p1x = dy * uz - dz * uy
    p1y = dz * ux - dx * uz
    p1z = dx * uy - dy * ux
    l1 = math.sqrt(p1x*p1x + p1y*p1y + p1z*p1z)
    p1x, p1y, p1z = p1x/l1, p1y/l1, p1z/l1
    p2x = dy * p1z - dz * p1y
    p2y = dz * p1x - dx * p1z
    p2z = dx * p1y - dy * p1x
    verts = []
    for ring in (0, 1):
        c = p0 if ring == 0 else p1
        r = r0 if ring == 0 else r1
        for i in range(segments):
            ang = 2.0 * math.pi * i / segments
            ca, sa = math.cos(ang), math.sin(ang)
            verts.append((
                c[0] + ca * r * p1x + sa * r * p2x,
                c[1] + ca * r * p1y + sa * r * p2y,
                c[2] + ca * r * p1z + sa * r * p2z,
            ))
    faces = []
    for i in range(segments):
        ni = (i + 1) % segments
        faces.append([i, ni, ni + segments, i + segments])
    faces.append(list(reversed(range(segments))))
    faces.append(list(range(segments, segments * 2)))
    _finalize_mesh(name, verts, faces, color)


def _box(name, center, size, color):
    cx, cy, cz = center
    sx, sy, sz = size
    hx, hy, hz = sx/2, sy/2, sz/2
    verts = [
        (cx-hx, cy-hy, cz-hz), (cx+hx, cy-hy, cz-hz),
        (cx+hx, cy+hy, cz-hz), (cx-hx, cy+hy, cz-hz),
        (cx-hx, cy-hy, cz+hz), (cx+hx, cy-hy, cz+hz),
        (cx+hx, cy+hy, cz+hz), (cx-hx, cy+hy, cz+hz),
    ]
    faces = [
        [4, 5, 6, 7], [0, 3, 2, 1],
        [0, 1, 5, 4], [2, 3, 7, 6],
        [3, 0, 4, 7], [1, 2, 6, 5],
    ]
    _finalize_mesh(name, verts, faces, color)


def _face_axis(facing):
    if facing == '+X': return (1.0, 0.0)
    if facing == '-X': return (-1.0, 0.0)
    if facing == '+Y': return (0.0, 1.0)
    return (0.0, -1.0)


# ── BODY PARTS ─────────────────────────────────────────────────────


def _build_head(name, base_x, base_y, head_base_z, p, fwd, prp,
                skin_color, hair_color, hair_style):
    """UV-sphere base mesh sculpted via per-vertex deformation:
       1. Generate a UV sphere (12 rings × 14 segments).
       2. Scale to head dimensions (width × depth × height).
       3. GRAB chin downward + forward (pull bottom-front out).
       4. FLATTEN sides at temple/cheek band (squeeze x toward 0).
       5. CARVE eye sockets (push inward at eye level on the front).
       6. PULL nose bridge + tip forward.
       7. CREASE mouth band.
    This mirrors the Blender sculpt workflow the user described.
    """
    head_h = p["head_h"]
    head_w_max = p["head_w_max"]
    head_d_max = p["head_d_max"]
    head_h_half = head_h / 2
    head_cz = head_base_z + head_h_half
    fwd_x, fwd_y = fwd
    prp_x, prp_y = prp

    rings = 12         # vertical rings between poles
    segs = 14          # segments around the equator
    # Generate UV sphere in local frame where:
    #   +Z = up (crown)
    #   +X_local = "front" (toward facing)
    #   +Y_local = "side" (perpendicular)
    # Then deform, then rotate into world frame via fwd/prp.
    local = []         # list of (lx, ly, lz) in normalized units
    # Top pole
    local.append((0.0, 0.0, 1.0))
    for r in range(1, rings):
        phi = math.pi * r / rings        # 0 = top pole, pi = bottom
        z = math.cos(phi)
        sin_phi = math.sin(phi)
        for s in range(segs):
            theta = 2.0 * math.pi * s / segs
            x = sin_phi * math.cos(theta)
            y = sin_phi * math.sin(theta)
            local.append((x, y, z))
    # Bottom pole
    local.append((0.0, 0.0, -1.0))

    def smoothstep01(x):
        x = max(0.0, min(1.0, x))
        return x * x * (3.0 - 2.0 * x)

    sculpted = []
    for (lx, ly, lz) in local:
        # 1) base scale: x ↔ depth axis, y ↔ width axis, z ↔ height.
        # Map to physical sizes.
        sx = lx * head_d_max
        sy = ly * head_w_max
        sz = lz * head_h_half

        # 2) GRAB chin: bottom-front-center gets pulled DOWN + FWD.
        # Region: lz < -0.4, lx > 0.2.
        chin_mask = smoothstep01((-0.4 - lz) / 0.55) \
                    * smoothstep01((lx - 0.0) / 0.7)
        if chin_mask > 0:
            sx += chin_mask * head_d_max * 0.08
            sz -= chin_mask * head_h_half * 0.18

        # 3) JAWLINE TAPER: bottom band gets squeezed in width.
        if lz < -0.2:
            taper = smoothstep01((-0.2 - lz) / 0.8)
            sy *= 1.0 - taper * 0.45    # narrow toward chin
            sx *= 1.0 - taper * 0.18    # slight depth reduction

        # 4) CROWN ROUNDING: top gets gently squeezed inward.
        if lz > 0.5:
            t = smoothstep01((lz - 0.5) / 0.5)
            sy *= 1.0 - t * 0.30
            sx *= 1.0 - t * 0.20

        # 5) TEMPLE FLATTEN: middle of head (lz between -0.3 and
        # +0.4) on the SIDES gets flattened — real heads have
        # flatter temples than a sphere's perfectly round side.
        if -0.3 < lz < 0.4 and abs(ly) > 0.6 and abs(lx) < 0.3:
            sy *= 0.94

        # 6) EYE SOCKET CARVE: at eye level (lz ~ +0.15), on the
        # FRONT (lx > 0.5), to the SIDES of center (|ly| ~ 0.3..0.6),
        # push the surface INWARD (reduce lx component).
        if lx > 0.45 and 0.0 < lz < 0.30 and 0.18 < abs(ly) < 0.55:
            socket_mask = smoothstep01((lx - 0.45) / 0.45) \
                          * smoothstep01((0.18 - abs(lz - 0.15)) / 0.18) \
                          * smoothstep01((abs(ly) - 0.18) / 0.20) \
                          * smoothstep01((0.55 - abs(ly)) / 0.10)
            sx -= socket_mask * head_d_max * 0.12

        # 7) NOSE BRIDGE + TIP: front-center band (|ly| < 0.20,
        # 0.0 < lz < 0.30) pulled OUTWARD on the depth axis.
        if lx > 0.4 and abs(ly) < 0.22 and -0.05 < lz < 0.30:
            nose_mask = smoothstep01((lx - 0.4) / 0.5) \
                        * smoothstep01((0.22 - abs(ly)) / 0.22) \
                        * smoothstep01((0.30 - abs(lz - 0.12)) / 0.18)
            sx += nose_mask * head_d_max * 0.15

        # 8) MOUTH CREASE: thin band below the nose, very slight
        # crease (inward press on lx of a few mm).
        if lx > 0.5 and abs(ly) < 0.30 and -0.20 < lz < -0.05:
            crease = smoothstep01((lx - 0.5) / 0.4) \
                     * smoothstep01((0.30 - abs(ly)) / 0.30) \
                     * smoothstep01((0.15 - abs(lz + 0.12)) / 0.10)
            sx -= crease * head_d_max * 0.03

        sculpted.append((sx, sy, sz))

    # Rotate from local (X=fwd, Y=perp, Z=up) to world frame using
    # fwd/prp and translate to head center
    world_verts = []
    for (sx, sy, sz) in sculpted:
        wx = base_x + sx * fwd_x + sy * prp_x
        wy = base_y + sx * fwd_y + sy * prp_y
        wz = head_cz + sz
        world_verts.append((wx, wy, wz))

    # Build faces — UV sphere connectivity
    faces = []
    # Top fan
    for s in range(segs):
        ns = (s + 1) % segs
        faces.append([0, 1 + s, 1 + ns])
    # Middle bands
    for r in range(rings - 2):
        a = 1 + r * segs
        b = 1 + (r + 1) * segs
        for s in range(segs):
            ns = (s + 1) % segs
            faces.append([a + s, a + ns, b + ns, b + s])
    # Bottom fan
    bot = 1 + (rings - 1) * segs
    last = 1 + (rings - 2) * segs
    for s in range(segs):
        ns = (s + 1) % segs
        faces.append([bot, last + ns, last + s])
    _finalize_mesh(f"{name}_Head", world_verts, faces, skin_color)

    # ── Facial features ────────────────────────────────────────
    fwd_x, fwd_y = fwd
    # NOSE — protruding wedge at brow_z, between cheekbones
    nose_z = head_base_z + head_h * 0.60
    nose_out = head_d_max * 0.55
    nose_x = base_x + fwd_x * nose_out
    nose_y = base_y + fwd_y * nose_out
    if abs(fwd_y) > abs(fwd_x):
        nose_size = (head_w_max * 0.30, 0.040, head_h * 0.22)
    else:
        nose_size = (0.040, head_w_max * 0.30, head_h * 0.22)
    _box(f"{name}_Nose", (nose_x, nose_y, nose_z),
         nose_size, skin_color)
    # EYE SOCKETS — recessed darker band across both eyes
    eye_z = head_base_z + head_h * 0.66
    socket_x = base_x + fwd_x * (head_d_max * 0.45)
    socket_y = base_y + fwd_y * (head_d_max * 0.45)
    socket_col = (skin_color[0] * 0.60,
                  skin_color[1] * 0.60,
                  skin_color[2] * 0.60, 1.0)
    if abs(fwd_y) > abs(fwd_x):
        _box(f"{name}_EyeSocket", (socket_x, socket_y, eye_z),
             (head_w_max * 1.60, 0.025, head_h * 0.12), socket_col)
    else:
        _box(f"{name}_EyeSocket", (socket_x, socket_y, eye_z),
             (0.025, head_w_max * 1.60, head_h * 0.12), socket_col)
    # EYES — sclera + pupil per side
    eye_offset = head_w_max * 0.55
    px_e, py_e = prp
    for eye_side, sgn in (('L', -1), ('R', +1)):
        ex = base_x + px_e * eye_offset * sgn \
             + fwd_x * (head_d_max * 0.50)
        ey = base_y + py_e * eye_offset * sgn \
             + fwd_y * (head_d_max * 0.50)
        _box(f"{name}_EyeWhite_{eye_side}",
             (ex, ey, eye_z),
             (0.035, 0.035, 0.030)
                 if abs(fwd_y) <= abs(fwd_x)
                 else (0.035, 0.025, 0.030),
             (0.94, 0.92, 0.88, 1.0))
        # Pupil
        _box(f"{name}_Pupil_{eye_side}",
             (ex + fwd_x * 0.010, ey + fwd_y * 0.010, eye_z),
             (0.020, 0.020, 0.020),
             (0.10, 0.08, 0.06, 1.0))
    # MOUTH — thin band
    mouth_z = head_base_z + head_h * 0.30
    mouth_x = base_x + fwd_x * (head_d_max * 0.46)
    mouth_y = base_y + fwd_y * (head_d_max * 0.46)
    mouth_col = (0.62, 0.32, 0.32, 1.0)
    if abs(fwd_y) > abs(fwd_x):
        _box(f"{name}_Mouth", (mouth_x, mouth_y, mouth_z),
             (head_w_max * 0.55, 0.020, head_h * 0.04),
             mouth_col)
    else:
        _box(f"{name}_Mouth", (mouth_x, mouth_y, mouth_z),
             (0.020, head_w_max * 0.55, head_h * 0.04),
             mouth_col)
    # EARS — small wedges flush with the side of the head
    for ear_side, sgn in (('L', -1), ('R', +1)):
        ear_x = base_x + px_e * sgn * (head_w_max * 0.95)
        ear_y = base_y + py_e * sgn * (head_w_max * 0.95)
        if abs(fwd_y) > abs(fwd_x):
            ear_size = (0.035, head_d_max * 0.40, head_h * 0.22)
        else:
            ear_size = (head_d_max * 0.40, 0.035, head_h * 0.22)
        _box(f"{name}_Ear_{ear_side}",
             (ear_x, ear_y, head_base_z + head_h * 0.55),
             ear_size, skin_color)

    # ── HAIR ───────────────────────────────────────────────────
    if hair_style != 'bald':
        if hair_style in ('cap', 'beanie'):
            # Hat covers the crown
            hat_color = hair_color
            hat_z = head_base_z + head_h * 1.00
            hat_h = head_h * 0.30
            hat_w = head_w_max * 1.05
            hat_d = head_d_max * 1.05
            if hair_style == 'cap':
                hat_color = (0.18, 0.32, 0.55, 1.0)
            else:
                hat_color = (0.18, 0.18, 0.22, 1.0)
            # Crown hat block (rings)
            hat_verts = []
            for (zof, hw, hd) in (
                (0.0, hat_w * 0.65, hat_d * 0.60),
                (hat_h * 0.5, hat_w, hat_d),
                (hat_h,  hat_w, hat_d),
            ):
                hat_verts.extend(_ring(base_x, base_y,
                                       hat_z + zof, hw, hd,
                                       8, fwd, prp))
            hat_faces = []
            for r in range(2):
                a = r * 8; b = (r + 1) * 8
                for k in range(8):
                    nk = (k + 1) % 8
                    hat_faces.append([a+k, a+nk, b+nk, b+k])
            # Cap brim sticking forward (for 'cap' only)
            _finalize_mesh(f"{name}_Hat", hat_verts, hat_faces,
                           hat_color)
            if hair_style == 'cap':
                brim_x = base_x + fwd_x * head_d_max * 1.05
                brim_y = base_y + fwd_y * head_d_max * 1.05
                if abs(fwd_y) > abs(fwd_x):
                    brim_size = (head_w_max * 1.20, 0.18, 0.03)
                else:
                    brim_size = (0.18, head_w_max * 1.20, 0.03)
                _box(f"{name}_CapBrim",
                     (brim_x, brim_y, hat_z + hat_h * 0.35),
                     brim_size, hat_color)
        else:
            # Hair cap sits on the crown, slightly larger than skull
            hair_verts = []
            hair_rings = [
                (head_h * 0.78,  head_w_max * 0.95, head_d_max * 0.96),
                (head_h * 0.92,  head_w_max * 0.90, head_d_max * 0.90),
                (head_h * 1.05,  head_w_max * 0.55, head_d_max * 0.50),
            ]
            for (zof, hw, hd) in hair_rings:
                hair_verts.extend(_ring(base_x, base_y,
                                        head_base_z + zof,
                                        hw, hd, 8, fwd, prp))
            hair_faces = []
            for r in range(2):
                a = r * 8; b = (r + 1) * 8
                for k in range(8):
                    nk = (k + 1) % 8
                    hair_faces.append([a+k, a+nk, b+nk, b+k])
            # Apex
            hair_verts.append((base_x, base_y,
                               head_base_z + head_h * 1.05))
            apex = len(hair_verts) - 1
            for k in range(8):
                nk = (k + 1) % 8
                hair_faces.append([apex, 16 + k, 16 + nk])
            _finalize_mesh(f"{name}_Hair", hair_verts, hair_faces,
                           hair_color)
            if hair_style == 'ponytail':
                # Tail trailing behind head
                tail_back_x = base_x - fwd_x * head_d_max * 0.55
                tail_back_y = base_y - fwd_y * head_d_max * 0.55
                _oriented_cyl(
                    f"{name}_Ponytail",
                    (tail_back_x, tail_back_y,
                     head_base_z + head_h * 0.88),
                    (tail_back_x - fwd_x * 0.05,
                     tail_back_y - fwd_y * 0.05,
                     head_base_z + head_h * 0.25),
                    head_w_max * 0.20, head_w_max * 0.08,
                    hair_color, segments=6)


def _build_torso(name, base_x, base_y, hip_top_z, p, fwd, prp,
                 jacket_color):
    """SCULPTED torso · cylinder base with vertex-level
    deformation matching real anatomy:
       1. Base cylinder (12 rings × 12 segments)
       2. Pinch waist (narrow ring at z ~0.4)
       3. Flare hips below the waist
       4. Broaden shoulders at top
       5. Push pec swell forward at upper chest
       6. Push buttocks backward at lower hip
       7. Round shoulder corners (pull top corners in toward
          neck so shoulders aren't a square corner)
    Returns shoulder_top_z."""
    torso_h = p["torso_h"]
    chest_d_half = p["torso_chest_d"] / 2
    waist_w_half = p["torso_waist_w"] / 2
    waist_d_half = p["torso_waist_d"] / 2
    hip_w_half = p["torso_hip_w"] / 2
    hip_d_half = p["torso_hip_d"] / 2
    shoulder_w_half = p["shoulder_w"] / 2
    fwd_x, fwd_y = fwd
    prp_x, prp_y = prp

    n_rings = 12
    segs = 12

    def smoothstep01(x):
        x = max(0.0, min(1.0, x))
        return x * x * (3.0 - 2.0 * x)

    # Build vertices in local frame: x=facing (depth), y=perp (width),
    # z=vertical (0 at hip, torso_h at shoulder). Then rotate to
    # world via fwd/prp.
    verts = []
    z_shoulder = hip_top_z + torso_h
    for r in range(n_rings):
        t = r / (n_rings - 1)   # 0 at hip, 1 at shoulder
        z_local = t * torso_h

        # Base width/depth profile by interpolating among the
        # 4 anatomical landmarks: hip / waist / chest / shoulder.
        # Smooth between them with a piecewise cubic.
        if t < 0.30:
            u = t / 0.30
            base_w = hip_w_half + (waist_w_half - hip_w_half) * smoothstep01(u)
            base_d = hip_d_half + (waist_d_half - hip_d_half) * smoothstep01(u)
        elif t < 0.75:
            u = (t - 0.30) / 0.45
            base_w = waist_w_half + (chest_d_half * 1.0 - waist_w_half) * smoothstep01(u)
            # Chest WIDTH ramps up from waist toward shoulder
            base_w = waist_w_half + (shoulder_w_half * 0.78 - waist_w_half) * smoothstep01(u)
            base_d = waist_d_half + (chest_d_half - waist_d_half) * smoothstep01(u)
        else:
            u = (t - 0.75) / 0.25
            base_w = shoulder_w_half * 0.78 + (shoulder_w_half - shoulder_w_half * 0.78) * smoothstep01(u)
            base_d = chest_d_half + (chest_d_half * 0.96 - chest_d_half) * smoothstep01(u)

        for s in range(segs):
            theta = 2.0 * math.pi * s / segs
            cs = math.cos(theta)
            sn = math.sin(theta)
            # cs = ±1 maps to side (perp axis), sn = ±1 to facing
            local_x = sn * base_d        # depth direction
            local_y = cs * base_w        # width direction

            # SCULPT: chest swell — push forward at upper chest
            if 0.55 < t < 0.90 and sn > 0.2:
                pec_mask = smoothstep01((t - 0.55) / 0.35) \
                           * smoothstep01((0.90 - t) / 0.35) \
                           * smoothstep01((sn - 0.2) / 0.8) \
                           * smoothstep01((0.6 - abs(cs)) / 0.6)
                local_x += pec_mask * chest_d_half * 0.22

            # SCULPT: butt curve — push back at lower hip
            if t < 0.25 and sn < -0.2:
                butt_mask = smoothstep01((0.25 - t) / 0.25) \
                            * smoothstep01((-sn - 0.2) / 0.8) \
                            * smoothstep01((0.55 - abs(cs)) / 0.55)
                local_x -= butt_mask * hip_d_half * 0.30

            # SCULPT: shoulder corner round — at top ring,
            # widest extreme points pulled slightly inward+upward
            # to soften the square shoulder corner.
            if t > 0.88 and abs(cs) > 0.85:
                round_mask = smoothstep01((t - 0.88) / 0.12) \
                             * smoothstep01((abs(cs) - 0.85) / 0.15)
                # Push the extreme side IN
                local_y *= 1.0 - round_mask * 0.18
                # Pull DOWN slightly so the shoulder slopes
                z_local -= round_mask * torso_h * 0.02

            wx = base_x + local_x * fwd_x + local_y * prp_x
            wy = base_y + local_x * fwd_y + local_y * prp_y
            wz = hip_top_z + z_local
            verts.append((wx, wy, wz))

    # Faces between adjacent rings
    faces = []
    for r in range(n_rings - 1):
        a = r * segs
        b = (r + 1) * segs
        for s in range(segs):
            ns = (s + 1) % segs
            faces.append([a + s, a + ns, b + ns, b + s])
    # Top cap — fan from shoulder center
    verts.append((base_x, base_y, z_shoulder))
    top_i = len(verts) - 1
    top_base = (n_rings - 1) * segs
    for s in range(segs):
        ns = (s + 1) % segs
        faces.append([top_i, top_base + s, top_base + ns])
    # Bottom cap — fan from hip center
    verts.append((base_x, base_y, hip_top_z))
    bot_i = len(verts) - 1
    for s in range(segs):
        ns = (s + 1) % segs
        faces.append([bot_i, ns, s])
    _finalize_mesh(f"{name}_Torso", verts, faces, jacket_color)
    # Z markers + scalars for downstream lapels/belt code
    z_chest = hip_top_z + torso_h * 0.78
    z_waist = hip_top_z + torso_h * 0.30
    shoulder_w = p["shoulder_w"]
    chest_d = p["torso_chest_d"]
    waist_w = p["torso_waist_w"]
    waist_d = p["torso_waist_d"]
    segments = 8

    # ── LAPELS · darker V down the front of the torso ──────────
    fwd_x, fwd_y = fwd
    prp_x, prp_y = prp
    lapel_color = (jacket_color[0] * 0.55,
                   jacket_color[1] * 0.55,
                   jacket_color[2] * 0.55,
                   jacket_color[3])
    lapel_h = torso_h * 0.55
    lapel_w = shoulder_w * 0.16
    lapel_z = z_chest - torso_h * 0.10
    for sgn in (-1, +1):
        l_perp = sgn * lapel_w * 0.7
        l_cx = base_x + fwd_x * (chest_d / 2 * 0.95) \
                      + prp_x * l_perp
        l_cy = base_y + fwd_y * (chest_d / 2 * 0.95) \
                      + prp_y * l_perp
        if abs(fwd_y) > abs(fwd_x):
            lapel_size = (lapel_w, 0.025, lapel_h)
        else:
            lapel_size = (0.025, lapel_w, lapel_h)
        _box(f"{name}_Lapel_{sgn:+d}",
             (l_cx, l_cy, lapel_z), lapel_size, lapel_color)

    # ── BELT · narrow darker band at the waist ─────────────────
    belt_color = (0.18, 0.14, 0.10, 1.0)
    belt_verts = []
    belt_z = z_waist - torso_h * 0.06
    belt_h = 0.030
    belt_rings = [
        (belt_z, waist_w / 2 * 1.04, waist_d / 2 * 1.04),
        (belt_z + belt_h, waist_w / 2 * 1.04, waist_d / 2 * 1.04),
    ]
    for (rz, hw, hd) in belt_rings:
        belt_verts.extend(_ring(base_x, base_y, rz,
                                 hw, hd, segments, fwd, prp))
    belt_faces = []
    for k in range(segments):
        nk = (k + 1) % segments
        belt_faces.append([k, nk, segments + nk, segments + k])
    _finalize_mesh(f"{name}_Belt", belt_verts, belt_faces,
                   belt_color)

    return z_shoulder


def _build_arms(name, base_x, base_y, shoulder_z, p, fwd, prp,
                jacket_color, skin_color, pose='walking'):
    """Two arms oriented to hang with slight outward angle + elbow
    bend. Default 'walking' pose: arms swing slightly forward
    (right) and backward (left)."""
    shoulder_w = p["shoulder_w"]
    arm_upper_h = p["arm_upper_h"]
    arm_lower_h = p["arm_lower_h"]
    r_sh = p["arm_r_shoulder"]
    r_el = p["arm_r_elbow"]
    r_wr = p["arm_r_wrist"]
    hand_l = p["hand_l"]
    hand_w = p["hand_w"]
    fwd_x, fwd_y = fwd
    prp_x, prp_y = prp
    hand_positions = {}
    for side, sgn in (('L', -1), ('R', +1)):
        # Shoulder anchor — just inside the torso shoulder ring
        sh_x = base_x + prp_x * sgn * (shoulder_w / 2 - r_sh * 0.5)
        sh_y = base_y + prp_y * sgn * (shoulder_w / 2 - r_sh * 0.5)
        sh_z = shoulder_z - r_sh * 0.6
        # Elbow — drops down arm_upper_h, with 6° outward + slight
        # forward bias for walking pose
        out_angle = math.radians(6)
        forward_swing = 0.0
        if pose == 'walking':
            # Right arm swings forward, left arm backs back
            forward_swing = fwd_x * 0.08 if sgn > 0 else -fwd_x * 0.08
            forward_swing_y = fwd_y * 0.08 if sgn > 0 else -fwd_y * 0.08
        else:
            forward_swing = 0.0
            forward_swing_y = 0.0
        el_x = sh_x + prp_x * sgn * (arm_upper_h * math.sin(out_angle)) \
                    + (forward_swing if pose == 'walking' else 0)
        el_y = sh_y + prp_y * sgn * (arm_upper_h * math.sin(out_angle))
        if pose == 'walking':
            el_y += forward_swing_y
        el_z = sh_z - arm_upper_h * math.cos(out_angle)
        # Wrist — forearm bent 14° forward at the elbow
        bend = math.radians(14)
        if pose == 'walking':
            # Forward arm bends more
            bend = math.radians(22) if sgn > 0 else math.radians(10)
        wr_x = el_x + fwd_x * arm_lower_h * math.sin(bend)
        wr_y = el_y + fwd_y * arm_lower_h * math.sin(bend)
        wr_z = el_z - arm_lower_h * math.cos(bend)
        # ── Upper arm with shoulder TOP extension so the arm
        # cylinder fades INTO the torso shoulder ring at the top.
        # Was a flat shoulder cap BOX sticking out above the
        # shoulder line — looked like a football shoulder pad.
        # Replaced with a wider shoulder-top vertex blended into a
        # narrower elbow vertex.
        sh_top_x = sh_x - prp_x * sgn * r_sh * 0.2     # tucked inward
        sh_top_y = sh_y - prp_y * sgn * r_sh * 0.2
        sh_top_z = shoulder_z + r_sh * 0.15            # above torso ring
        _oriented_cyl(f"{name}_UArm_{side}",
                      (sh_top_x, sh_top_y, sh_top_z),
                      (el_x, el_y, el_z),
                      r_sh * 1.35, r_el, jacket_color, segments=8)
        # ── Elbow joint ──
        _box(f"{name}_Elbow_{side}",
             (el_x, el_y, el_z),
             (r_el * 2.0, r_el * 2.0, r_el * 2.0), jacket_color)
        # ── Forearm ──
        _oriented_cyl(f"{name}_FArm_{side}",
                      (el_x, el_y, el_z),
                      (wr_x, wr_y, wr_z),
                      r_el, r_wr, jacket_color, segments=8)
        # ── Cuff (darker band at the wrist) ──
        cuff_color = (jacket_color[0] * 0.65,
                      jacket_color[1] * 0.65,
                      jacket_color[2] * 0.65,
                      jacket_color[3])
        _box(f"{name}_Cuff_{side}",
             (wr_x, wr_y, wr_z + r_wr * 0.2),
             (r_wr * 2.4, r_wr * 2.4, 0.025), cuff_color)
        # ── Hand · small wedge ──
        hand_z = wr_z - hand_l * 0.4
        _box(f"{name}_Hand_{side}",
             (wr_x + fwd_x * hand_l * 0.15,
              wr_y + fwd_y * hand_l * 0.15,
              hand_z),
             (hand_w, hand_w, hand_l * 0.8), skin_color)
        # Thumb stub on outside of hand
        _box(f"{name}_Thumb_{side}",
             (wr_x + fwd_x * hand_l * 0.10 + prp_x * sgn * hand_w * 0.5,
              wr_y + fwd_y * hand_l * 0.10 + prp_y * sgn * hand_w * 0.5,
              hand_z + hand_l * 0.15),
             (hand_w * 0.45, hand_w * 0.45, hand_w * 0.6),
             skin_color)
        hand_positions[side] = (wr_x + fwd_x * hand_l * 0.15,
                                wr_y + fwd_y * hand_l * 0.15,
                                hand_z)
    return hand_positions


def _build_legs_and_feet(name, base_x, base_y, base_z, p, fwd, prp,
                          pants_color, shoe_color, pose='walking'):
    """Two legs with default WALKING pose (one forward, one back)
    plus shoes. Returns hip_top_z for pelvis/torso attachment."""
    leg_h = p["leg_h"]
    thigh_h = leg_h * p["leg_thigh_frac"]
    shin_h = leg_h - thigh_h
    r_hip = p["leg_r_hip"]
    r_knee = p["leg_r_knee"]
    r_ankle = p["leg_r_ankle"]
    sep = p["leg_separation"]
    foot_l = p["foot_l"]
    foot_w = p["foot_w"]
    foot_h = p["foot_h"]
    fwd_x, fwd_y = fwd
    prp_x, prp_y = prp
    hip_top_z = base_z + leg_h
    # Walking stance: LEFT leg forward, RIGHT leg back. Forward leg
    # foot is planted slightly ahead; back leg is at neutral.
    stride_offset = {
        'walking':  {'L': +0.12, 'R': -0.08},
        'standing': {'L':  0.0,  'R':  0.0},
    }
    knee_bend_deg = {
        'walking':  {'L': 8,    'R': 14},     # back leg bends more
        'standing': {'L': 0,    'R': 0},
    }
    sel = stride_offset.get(pose, stride_offset['walking'])
    bend = knee_bend_deg.get(pose, knee_bend_deg['walking'])
    for side, sgn in (('L', -1), ('R', +1)):
        # Hip anchor at top of leg
        hip_x = base_x + prp_x * sgn * sep
        hip_y = base_y + prp_y * sgn * sep
        # Foot position (with stride offset along facing axis)
        foot_x = hip_x + fwd_x * sel[side]
        foot_y = hip_y + fwd_y * sel[side]
        foot_z = base_z
        # Knee position: at thigh_h below hip, with forward bend
        knee_bend_rad = math.radians(bend[side])
        knee_x = hip_x + fwd_x * thigh_h * math.sin(knee_bend_rad)
        knee_y = hip_y + fwd_y * thigh_h * math.sin(knee_bend_rad)
        knee_z = hip_top_z - thigh_h * math.cos(knee_bend_rad)
        # Thigh
        _oriented_cyl(f"{name}_Thigh_{side}",
                      (hip_x, hip_y, hip_top_z),
                      (knee_x, knee_y, knee_z),
                      r_hip, r_knee, pants_color, segments=8)
        # Knee
        _box(f"{name}_Knee_{side}",
             (knee_x, knee_y, knee_z),
             (r_knee * 2.0, r_knee * 2.0, r_knee * 1.8),
             pants_color)
        # Shin (from knee to ankle which is just above foot)
        ankle_z = base_z + foot_h * 0.7
        _oriented_cyl(f"{name}_Shin_{side}",
                      (knee_x, knee_y, knee_z),
                      (foot_x, foot_y, ankle_z),
                      r_knee * 0.92, r_ankle,
                      pants_color, segments=8)
        # Pant cuff (darker band at ankle)
        cuff_color = (pants_color[0] * 0.65,
                      pants_color[1] * 0.65,
                      pants_color[2] * 0.65,
                      pants_color[3])
        _box(f"{name}_PantCuff_{side}",
             (foot_x, foot_y, ankle_z),
             (r_ankle * 2.6, r_ankle * 2.6, 0.035),
             cuff_color)
        # ── Shoe · 3-part loafer · heel + main + pointed toe ─
        if abs(fwd_x) > abs(fwd_y):
            sx_main, sy_main = foot_l * 0.50, foot_w * 0.95
        else:
            sx_main, sy_main = foot_w * 0.95, foot_l * 0.50
        # Heel
        heel_x = foot_x - fwd_x * foot_l * 0.30
        heel_y = foot_y - fwd_y * foot_l * 0.30
        if abs(fwd_x) > abs(fwd_y):
            heel_size = (foot_l * 0.30, foot_w * 0.90, foot_h * 0.85)
        else:
            heel_size = (foot_w * 0.90, foot_l * 0.30, foot_h * 0.85)
        heel_color = (shoe_color[0] * 0.80,
                      shoe_color[1] * 0.80,
                      shoe_color[2] * 0.80,
                      shoe_color[3])
        _box(f"{name}_ShoeHeel_{side}",
             (heel_x, heel_y, foot_z + foot_h * 0.40),
             heel_size, heel_color)
        # Main
        _box(f"{name}_ShoeMain_{side}",
             (foot_x, foot_y, foot_z + foot_h * 0.35),
             (sx_main, sy_main, foot_h * 0.70), shoe_color)
        # Toe — pointed forward, tapered
        toe_x = foot_x + fwd_x * foot_l * 0.30
        toe_y = foot_y + fwd_y * foot_l * 0.30
        if abs(fwd_x) > abs(fwd_y):
            toe_size = (foot_l * 0.30, foot_w * 0.62, foot_h * 0.55)
        else:
            toe_size = (foot_w * 0.62, foot_l * 0.30, foot_h * 0.55)
        _box(f"{name}_ShoeToe_{side}",
             (toe_x, toe_y, foot_z + foot_h * 0.30),
             toe_size, shoe_color)
        # Toe tip — narrowest, very pointed
        ttip_x = foot_x + fwd_x * foot_l * 0.45
        ttip_y = foot_y + fwd_y * foot_l * 0.45
        if abs(fwd_x) > abs(fwd_y):
            ttip_size = (foot_l * 0.18, foot_w * 0.40, foot_h * 0.40)
        else:
            ttip_size = (foot_w * 0.40, foot_l * 0.18, foot_h * 0.40)
        _box(f"{name}_ShoeTip_{side}",
             (ttip_x, ttip_y, foot_z + foot_h * 0.25),
             ttip_size, shoe_color)
        # Sole — full footprint, thin, lighter
        sole_color = (0.90, 0.88, 0.82, 1.0)
        if abs(fwd_x) > abs(fwd_y):
            sole_size = (foot_l * 0.95, foot_w * 1.00, foot_h * 0.30)
        else:
            sole_size = (foot_w * 1.00, foot_l * 0.95, foot_h * 0.30)
        _box(f"{name}_Sole_{side}",
             (foot_x + fwd_x * foot_l * 0.08,
              foot_y + fwd_y * foot_l * 0.08,
              foot_z + foot_h * 0.05),
             sole_size, sole_color)
    return hip_top_z


def _build_neck(name, base_x, base_y, shoulder_z, p, fwd, prp,
                skin_color):
    """Tapered neck (wider at shoulder, narrower at head). Returns
    head_base_z = top of neck."""
    neck_h = p["neck_h"]
    r_top = p["neck_r_top"]
    r_bot = p["neck_r_bot"]
    segments = 8
    verts = []
    for ring_z in (shoulder_z, shoulder_z + neck_h):
        r = r_bot if ring_z == shoulder_z else r_top
        verts.extend(_ring(base_x, base_y, ring_z, r, r,
                           segments, fwd, prp))
    faces = []
    for k in range(segments):
        nk = (k + 1) % segments
        faces.append([k, nk, segments + nk, segments + k])
    _finalize_mesh(f"{name}_Neck", verts, faces, skin_color)
    # Adam's apple
    fwd_x, fwd_y = fwd
    aa_z = shoulder_z + neck_h * 0.5
    _box(f"{name}_Adam",
         (base_x + fwd_x * r_top * 1.05,
          base_y + fwd_y * r_top * 1.05, aa_z),
         (0.035, 0.035, 0.035), skin_color)
    return shoulder_z + neck_h


# ── PUBLIC ENTRY POINT ─────────────────────────────────────────────


def human_figure(name, base_x, base_y, base_z, scale=1.0,
                 facing='-Y',
                 body_type='male_avg',
                 # Skin / hair
                 skin_color=(0.92, 0.75, 0.62, 1.0),
                 hair_style='short',
                 hair_color=(0.32, 0.22, 0.16, 1.0),
                 # Top
                 jacket_color=(0.32, 0.32, 0.36, 1.0),
                 yoke_color=None,
                 accent='none',
                 accent_color=None,
                 scarf_color=None,
                 # Bottom
                 pants_color=(0.20, 0.20, 0.24, 1.0),
                 pants_flare=1.0,
                 shoe_color=(0.18, 0.18, 0.20, 1.0),
                 # Face
                 has_sunglasses=False,
                 sunglasses_color=(0.15, 0.15, 0.15, 1.0),
                 with_ears=True,
                 with_mouth=True,
                 mouth_color=(0.62, 0.30, 0.32, 1.0),
                 beard='none',
                 jacket_puffy=False,
                 pose='walking',
                 lean_x=0.0):
    """Build a parametric human figure at (base_x, base_y, base_z)
    with feet on the ground at base_z. See module docstring.

    Default pose is 'walking' for natural-looking stance. Use
    'standing' for stiff symmetric pose (clerks behind counters).
    """
    p = _props_for(body_type, scale)
    fwd = _face_axis(facing)
    prp = (-fwd[1], fwd[0])
    # Legs + feet (returns hip_top_z = top of legs)
    hip_top_z = _build_legs_and_feet(name, base_x, base_y, base_z,
                                      p, fwd, prp,
                                      pants_color, shoe_color,
                                      pose=pose)
    # Torso (returns shoulder_z)
    shoulder_z = _build_torso(name, base_x + lean_x, base_y,
                               hip_top_z, p, fwd, prp,
                               jacket_color)
    # Arms
    hands = _build_arms(name, base_x + lean_x, base_y,
                         shoulder_z, p, fwd, prp,
                         jacket_color, skin_color, pose=pose)
    # Neck (returns head_base_z)
    head_base_z = _build_neck(name, base_x + lean_x * 0.7, base_y,
                               shoulder_z, p, fwd, prp,
                               skin_color)
    # Head (with face + hair)
    _build_head(name, base_x + lean_x * 0.5, base_y,
                head_base_z, p, fwd, prp,
                skin_color, hair_color, hair_style)
    return {"hands": hands,
            "head_base_z": head_base_z,
            "shoulder_z": shoulder_z}


__all__ = ["human_figure", "PROP", "BODY_PROFILES"]
