"""
human_sculpt.py
══════════════════════════════════════════════════════════════════
Parametric human-figure builder. The pipeline behind every NPC
sculpt, public-art statue, and gauntlet portrait that needs to
read as a recognizable person at PS2-era polycount.

Design rules (per _3D_MODELING_PLAYBOOK.md):
  · Low-poly: spheres 4 rings × 6-8 segments, cylinders 6-8 sided.
  · Vertex-colour material zones — no textures.
  · Coordinate frame: Blender Z-up, +X east, +Y north.
  · Figure stands at base_z; head reaches base_z + (scale × 1.80).
  · scale = 1.0 means real human size; scale = 2.0 makes a statue.

Call site:
    human_figure(
        name="Oliver_Tree",
        base_x=-260, base_y=120, base_z=plinth_top_z,
        scale=2.0,
        hair_style='bowl', hair_color=COL_HAIR_BROWN,
        pants_color=COL_PANTS_BLUE,
        pants_flare=2.6,             # the JNCO signature
        jacket_color=COL_JACKET_PINK,
        jacket_yoke_color=COL_JACKET_PURPLE,
        jacket_accent='star',         # decorative front patch
        jacket_accent_color=COL_JACKET_PINK,
        scarf_color=COL_SCARF_YELLOW,
        has_sunglasses=True,
        sunglasses_color=COL_GLASSES_PINK,
        face_facing='-Y',             # south
    )

Parts produced (each as its own MeshInstance3D after glTF):
  Head_Skull         — spheroid head
  Head_Face          — peach inset on the facing direction
  Head_Hair_*        — hair-style geometry (bowl / mohawk / etc.)
  Head_Glasses       — sunglasses band (if requested)
  Neck               — small cylinder
  Scarf              — collar wrap (if requested)
  Torso_Body         — jacket / shirt body
  Torso_Yoke         — shoulder yoke contrast colour
  Torso_Accent       — chest accent (star, stripe, etc.)
  Arm_L / Arm_R      — hanging arm cylinders
  Hand_L / Hand_R    — small fist boxes
  Pelvis             — hip block
  Leg_L / Leg_R      — leg cylinders (flared if pants_flare > 1)
  Shoe_L / Shoe_R    — foot boxes
"""

import math
import bpy


# ── PRIMITIVES ─────────────────────────────────────────────────────

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
    return _finalize_mesh(name, verts, faces, color)


def _oriented_cyl(name, p0, p1, r0, r1, color, segments=8):
    """Tapered cylinder from p0 (radius r0) to p1 (radius r1).
    Computes a perpendicular frame so the cylinder can point in any
    3D direction — used for articulated arms that aren't axis-aligned."""
    px = p1[0] - p0[0]
    py = p1[1] - p0[1]
    pz = p1[2] - p0[2]
    length = math.sqrt(px * px + py * py + pz * pz)
    if length < 0.001:
        return None
    dx, dy, dz = px / length, py / length, pz / length
    # Find a reference up vector that isn't parallel to direction
    if abs(dz) < 0.9:
        ux, uy, uz = 0.0, 0.0, 1.0
    else:
        ux, uy, uz = 1.0, 0.0, 0.0
    # Perp1 = direction × up
    p1x = dy * uz - dz * uy
    p1y = dz * ux - dx * uz
    p1z = dx * uy - dy * ux
    l1 = math.sqrt(p1x * p1x + p1y * p1y + p1z * p1z)
    p1x, p1y, p1z = p1x / l1, p1y / l1, p1z / l1
    # Perp2 = direction × perp1
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
    return _finalize_mesh(name, verts, faces, color)


def _cyl_taper(name, center, r_bottom, r_top, height, color, segments=8):
    """Tapered cylinder — different radius at bottom vs top. Used for
    legs (wider at the cuff = JNCO flare), torsos (narrower at waist),
    arms (slightly narrower at the wrist)."""
    cx, cy, cz = center
    h2 = height / 2.0
    verts = []
    for ring in (0, 1):
        r = r_bottom if ring == 0 else r_top
        z_off = -h2 if ring == 0 else h2
        for i in range(segments):
            ang = 2.0 * math.pi * i / segments
            verts.append((cx + math.cos(ang) * r,
                          cy + math.sin(ang) * r,
                          cz + z_off))
    faces = []
    for i in range(segments):
        ni = (i + 1) % segments
        faces.append([i, ni, ni + segments, i + segments])
    faces.append(list(reversed(range(segments))))
    faces.append(list(range(segments, segments * 2)))
    return _finalize_mesh(name, verts, faces, color)


def _sphere_low(name, center, radius, color, rings=4, segments=8,
                squash_z=1.0):
    """Lowpoly UV sphere. squash_z < 1.0 flattens the sphere (head
    is slightly egg-shaped). PS2-grade — 4 rings × 8 segs = 32 verts."""
    cx, cy, cz = center
    rz = radius * squash_z
    verts = [(cx, cy, cz + rz)]
    for r in range(1, rings):
        phi = math.pi * r / rings
        rr = radius * math.sin(phi)
        zh = rz * math.cos(phi)
        for s in range(segments):
            ang = 2.0 * math.pi * s / segments
            verts.append((cx + rr * math.cos(ang),
                          cy + rr * math.sin(ang),
                          cz + zh))
    verts.append((cx, cy, cz - rz))
    faces = []
    for s in range(segments):
        faces.append([0, 1 + s, 1 + (s + 1) % segments])
    for r in range(rings - 2):
        base = 1 + r * segments
        nxt = 1 + (r + 1) * segments
        for s in range(segments):
            faces.append([base + s, nxt + s,
                          nxt + (s + 1) % segments,
                          base + (s + 1) % segments])
    last = len(verts) - 1
    base = 1 + (rings - 2) * segments
    for s in range(segments):
        faces.append([last, base + (s + 1) % segments, base + s])
    return _finalize_mesh(name, verts, faces, color)


# ── HUMAN PROPORTIONS (in metres, scaled by `scale`) ───────────────
# Approximations of real human anatomy. ~7-head-tall figure
# (idealised proportion). All numbers are for scale = 1.0 (1.80 m
# total).
PROP = {
    "total_h":        1.80,
    "head_d":         0.18,    # head diameter (overall sphere)
    "head_squash":    0.92,    # slightly egg-shaped
    "neck_h":         0.06,
    "neck_r":         0.055,
    "shoulder_w":     0.46,    # full shoulder span
    "torso_h":        0.62,    # neck base → pelvis top
    "torso_r_top":    0.20,    # half-shoulder roughly
    "torso_r_bot":    0.18,    # waist
    "pelvis_h":       0.08,    # the hip block
    "pelvis_w":       0.36,
    "arm_h":          0.65,    # full arm
    "arm_r_top":      0.052,
    "arm_r_bot":      0.045,
    "hand_size":      0.08,
    "leg_h":          0.92,    # waist → ground
    "leg_r_top":      0.085,
    "leg_r_bot":      0.075,
    "leg_separation": 0.12,    # half-distance between leg centres
    "foot_w":         0.10,
    "foot_l":         0.22,
    "foot_h":         0.07,
}


# ── FACE-DIRECTION HELPERS ─────────────────────────────────────────

def _face_axis(facing):
    """Return (forward_unit, perp_unit) for the requested facing
    direction. facing ∈ {'+X','-X','+Y','-Y'}."""
    if facing == '+X': return (1, 0)
    if facing == '-X': return (-1, 0)
    if facing == '+Y': return (0, 1)
    return (0, -1)        # '-Y' default


# ── BODY PARTS ─────────────────────────────────────────────────────

def _build_legs(name, base_x, base_y, base_z, s, pants_color, pants_flare,
                skin_color=None):
    """Two legs as tapered cylinders from base_z up to pelvis_z.
    pants_flare > 1.0 widens the BOTTOM radius for the JNCO look."""
    leg_h = PROP["leg_h"] * s
    leg_r_top = PROP["leg_r_top"] * s
    leg_r_bot = PROP["leg_r_bot"] * s * pants_flare
    sep = PROP["leg_separation"] * s
    leg_cz = base_z + leg_h / 2
    for side, sign in (('L', -1), ('R', +1)):
        _cyl_taper(f"{name}_Leg_{side}",
                   (base_x + sign * sep, base_y, leg_cz),
                   leg_r_bot, leg_r_top, leg_h, pants_color,
                   segments=8)
        # KNEE BUMP · small slightly-larger sphere just above the
        # leg's vertical mid-point, suggesting the knee joint
        # under the pants. Visible as a subtle silhouette break
        # rather than a straight cylinder.
        knee_z = base_z + leg_h * 0.52
        knee_r = leg_r_top * 1.10
        _sphere_low(f"{name}_Knee_{side}",
                    (base_x + sign * sep, base_y, knee_z),
                    knee_r, pants_color,
                    rings=3, segments=8, squash_z=0.55)
    return base_z + leg_h    # returns pelvis-bottom z


def _build_feet(name, base_x, base_y, base_z, s, facing, shoe_color):
    """Shoes are now TWO PARTS each — main upper + tapered toe cap +
    visible white sole at the bottom. Reads as actual footwear, not
    rectangular blocks."""
    fwd_x, fwd_y = _face_axis(facing)
    foot_w = PROP["foot_w"] * s
    foot_l = PROP["foot_l"] * s
    foot_h = PROP["foot_h"] * s
    sep = PROP["leg_separation"] * s
    sole_color = (0.92, 0.90, 0.84, 1.0)
    for side, sign in (('L', -1), ('R', +1)):
        cx = base_x + sign * sep + fwd_x * foot_l * 0.18
        cy = base_y + fwd_y * foot_l * 0.18
        if abs(fwd_x) > abs(fwd_y):
            sx_size, sy_size = foot_l, foot_w
        else:
            sx_size, sy_size = foot_w, foot_l
        # Upper (main shoe body — coloured)
        _box(f"{name}_Shoe_{side}_Upper",
             (cx, cy, base_z + foot_h / 2 + foot_h * 0.25),
             (sx_size * 0.92, sy_size * 0.92, foot_h * 0.55),
             shoe_color)
        # Toe cap (extends forward, tapered narrower)
        toe_cx = cx + fwd_x * foot_l * 0.20
        toe_cy = cy + fwd_y * foot_l * 0.20
        toe_sx = sx_size * 0.55 if abs(fwd_x) > abs(fwd_y) else sx_size * 0.78
        toe_sy = sy_size * 0.78 if abs(fwd_x) > abs(fwd_y) else sy_size * 0.55
        _box(f"{name}_Shoe_{side}_Toe",
             (toe_cx, toe_cy, base_z + foot_h * 0.45),
             (toe_sx, toe_sy, foot_h * 0.65),
             shoe_color)
        # White sole — full footprint, thin
        _box(f"{name}_Shoe_{side}_Sole",
             (cx + fwd_x * foot_l * 0.10, cy + fwd_y * foot_l * 0.10,
              base_z + foot_h * 0.15),
             (sx_size * 1.05, sy_size * 1.05, foot_h * 0.30),
             sole_color)


def _build_torso(name, base_x, base_y, pelvis_top_z, s,
                 jacket_color, yoke_color=None,
                 accent='none', accent_color=None,
                 facing='-Y', puffy=False):
    """Torso as a tapered cylinder. yoke = darker shoulder cap.
    accent draws a contrast shape on the facing direction (chest).
    puffy=True replaces the tapered cylinder with a wider squashed
    sphere — the marshmallow silhouette of a puffer jacket."""
    torso_h = PROP["torso_h"] * s
    torso_r_top = PROP["torso_r_top"] * s
    torso_r_bot = PROP["torso_r_bot"] * s
    torso_cz = pelvis_top_z + torso_h / 2
    # Pelvis (narrow block to bridge legs → torso)
    pelvis_h = PROP["pelvis_h"] * s
    _box(f"{name}_Pelvis",
         (base_x, base_y, pelvis_top_z + pelvis_h / 2),
         (PROP["pelvis_w"] * s, PROP["pelvis_w"] * s * 0.6, pelvis_h),
         jacket_color)
    # BELT · thin darker band at the waist where jacket meets pants
    _box(f"{name}_Belt",
         (base_x, base_y, pelvis_top_z + pelvis_h / 2),
         (PROP["pelvis_w"] * s * 1.02,
          PROP["pelvis_w"] * s * 0.62,
          pelvis_h * 0.50),
         (0.18, 0.14, 0.10, 1.0))
    # Belt buckle on the front
    fwd_x_b, fwd_y_b = _face_axis(facing)
    bx_buck = base_x + fwd_x_b * PROP["pelvis_w"] * s * 0.52
    by_buck = base_y + fwd_y_b * PROP["pelvis_w"] * s * 0.52
    if abs(fwd_y_b) > abs(fwd_x_b):
        _box(f"{name}_BeltBuckle",
             (bx_buck, by_buck, pelvis_top_z + pelvis_h * 0.55),
             (0.05 * s, 0.02, 0.04 * s),
             (0.85, 0.78, 0.42, 1.0))
    else:
        _box(f"{name}_BeltBuckle",
             (bx_buck, by_buck, pelvis_top_z + pelvis_h * 0.55),
             (0.02, 0.05 * s, 0.04 * s),
             (0.85, 0.78, 0.42, 1.0))
    # Torso main body — puffer uses a wider squashed sphere
    if puffy:
        puff_r = torso_r_top * 1.55
        # Lower puffer band — bigger ball at the chest line
        _sphere_low(f"{name}_Puff_Lower",
                    (base_x, base_y, torso_cz - torso_h * 0.10),
                    puff_r, jacket_color,
                    rings=4, segments=10,
                    squash_z=(torso_h * 0.55) / puff_r)
        # Upper puffer band — slightly smaller, at the shoulder
        _sphere_low(f"{name}_Puff_Upper",
                    (base_x, base_y, torso_cz + torso_h * 0.20),
                    puff_r * 0.95, jacket_color,
                    rings=4, segments=10,
                    squash_z=(torso_h * 0.50) / (puff_r * 0.95))
    else:
        _cyl_taper(f"{name}_Torso",
                   (base_x, base_y, torso_cz),
                   torso_r_bot, torso_r_top, torso_h, jacket_color,
                   segments=10)
        # CHEST CAP · slight forward bulge at the upper chest so
        # the torso isn't a uniform cylinder. Squashed sphere
        # blended into the upper torso silhouette.
        fwd_x_t, fwd_y_t = _face_axis(facing)
        chest_z = torso_cz + torso_h * 0.18
        chest_cx = base_x + fwd_x_t * (torso_r_top * 0.10)
        chest_cy = base_y + fwd_y_t * (torso_r_top * 0.10)
        _sphere_low(f"{name}_Chest",
                    (chest_cx, chest_cy, chest_z),
                    torso_r_top * 1.05, jacket_color,
                    rings=3, segments=10, squash_z=0.60)
        # WAIST NARROWING · slight inward dimple at the natural
        # waist height — built as a small DARKER ring band so the
        # eye reads narrowing. (Pure-geometry narrowing would
        # require remeshing the torso cylinder; this fakes it
        # with a contrast ring at the right height.)
        waist_z = torso_cz - torso_h * 0.20
        # Only emit if there's a yoke (so the torso isn't a single
        # uniform block) — otherwise this would conflict with the
        # base jacket geometry.
        if yoke_color is None:
            _cyl_taper(f"{name}_WaistBand",
                       (base_x, base_y, waist_z),
                       torso_r_bot * 0.95, torso_r_bot * 0.95,
                       torso_h * 0.10,
                       (jacket_color[0] * 0.82,
                        jacket_color[1] * 0.82,
                        jacket_color[2] * 0.82,
                        jacket_color[3]),
                       segments=10)
    # COLLAR · subtle V-shape or crew-neck shape at the top of the
    # torso where the jacket meets the neck. Emitted as a small
    # darker triangle on the facing axis.
    if yoke_color is None:
        fwd_x_c, fwd_y_c = _face_axis(facing)
        collar_z = torso_cz + torso_h / 2 - 0.04
        cx_col = base_x + fwd_x_c * torso_r_top * 0.85
        cy_col = base_y + fwd_y_c * torso_r_top * 0.85
        collar_dark = (jacket_color[0] * 0.65, jacket_color[1] * 0.65,
                       jacket_color[2] * 0.65, jacket_color[3])
        if abs(fwd_y_c) > abs(fwd_x_c):
            _box(f"{name}_Collar",
                 (cx_col, cy_col, collar_z),
                 (torso_r_top * 1.4, 0.04, 0.08),
                 collar_dark)
        else:
            _box(f"{name}_Collar",
                 (cx_col, cy_col, collar_z),
                 (0.04, torso_r_top * 1.4, 0.08),
                 collar_dark)
    # Yoke — wider band at the shoulders
    if yoke_color is not None:
        yoke_h = torso_h * 0.42
        _cyl_taper(f"{name}_Yoke",
                   (base_x, base_y, torso_cz + torso_h / 2 - yoke_h / 2),
                   torso_r_top * 1.02, torso_r_top * 1.06,
                   yoke_h, yoke_color, segments=10)
    # Front accent (star, stripe, name plate)
    if accent != 'none' and accent_color is not None:
        fwd_x, fwd_y = _face_axis(facing)
        a_z = torso_cz - 0.08
        if accent == 'star':
            # Diamond-shaped chest accent — built from a small box
            ax = base_x + fwd_x * (torso_r_top * 0.98 + 0.01)
            ay = base_y + fwd_y * (torso_r_top * 0.98 + 0.01)
            if abs(fwd_x) > abs(fwd_y):
                _box(f"{name}_Accent",
                     (ax, ay, a_z),
                     (0.04, 0.16 * s, 0.22 * s), accent_color)
            else:
                _box(f"{name}_Accent",
                     (ax, ay, a_z),
                     (0.16 * s, 0.04, 0.22 * s), accent_color)
        elif accent == 'stripe':
            ax = base_x + fwd_x * (torso_r_top * 0.98 + 0.01)
            ay = base_y + fwd_y * (torso_r_top * 0.98 + 0.01)
            if abs(fwd_x) > abs(fwd_y):
                _box(f"{name}_Accent",
                     (ax, ay, torso_cz),
                     (0.04, 0.10 * s, torso_h * 0.85), accent_color)
            else:
                _box(f"{name}_Accent",
                     (ax, ay, torso_cz),
                     (0.10 * s, 0.04, torso_h * 0.85), accent_color)
    return torso_cz + torso_h / 2     # returns shoulder z (= neck base)


def _build_arms(name, base_x, base_y, shoulder_z, s,
                jacket_color, skin_color, pose='standing',
                facing='-Y'):
    """Build arms in the requested pose. Returns dict of hand-tip
    positions {'L': (x, y, z), 'R': (x, y, z)} so callers can
    attach props (mic, scooter, drink, etc.) to a specific hand.

    pose options:
      'standing'   — both arms hang straight down (default)
      'right_mic'  — right arm raised forward holding a mic at
                     mouth height; left arm hangs
      'arms_out'   — both arms slightly splayed (welcoming)
    """
    arm_h = PROP["arm_h"] * s
    arm_r_top = PROP["arm_r_top"] * s
    arm_r_bot = PROP["arm_r_bot"] * s
    shoulder_w = PROP["shoulder_w"] * s
    hand_size = PROP["hand_size"] * s
    fwd_x, fwd_y = _face_axis(facing)
    hand_positions = {}

    for side, sign in (('L', -1), ('R', +1)):
        shoulder_x = base_x + sign * (shoulder_w / 2 - arm_r_top)
        shoulder_y = base_y
        shoulder_pz = shoulder_z - 0.02 * s

        # SHOULDER CAP · spheroid cap at the top of each arm so
        # the silhouette has a clear shoulder-deltoid bump rather
        # than the arm starting from a flat torso edge. Roughly
        # 1.7x the top arm radius, slightly squashed.
        _sphere_low(f"{name}_Shoulder_{side}",
                    (shoulder_x, shoulder_y, shoulder_pz - arm_r_top * 0.5),
                    arm_r_top * 1.6, jacket_color,
                    rings=3, segments=8, squash_z=0.75)

        # Default arm pose — hanging at a slight 6° outward angle
        # (natural standing — arms don't usually run dead-vertical
        # along the torso).
        relax_off = arm_h * 0.10
        hand_x = shoulder_x + sign * relax_off
        hand_y = shoulder_y
        hand_z = shoulder_pz - arm_h * 0.995    # 0.5% bend at elbow
        if pose == 'right_mic' and side == 'R':
            hand_x = shoulder_x + 0.05 * s
            hand_y = shoulder_y + fwd_y * (arm_h * 0.50)
            hand_z = shoulder_pz + 0.10 * s
        elif pose == 'arms_out':
            hand_x = shoulder_x + sign * (arm_h * 0.35)
            hand_y = shoulder_y
            hand_z = shoulder_pz - arm_h * 0.92
        elif pose == 'hands_on_counter':
            # Both arms forward and down, hands resting on a flat
            # surface (counter top) in front of the figure. Used
            # for clerks, bartenders, librarians at their station.
            hand_x = shoulder_x + sign * arm_r_top * 0.5
            hand_y = shoulder_y + fwd_y * (arm_h * 0.45)
            hand_z = shoulder_pz - arm_h * 0.55
        elif pose == 'arms_crossed':
            # Both arms folded across chest — for a relaxed/
            # observing pose. Each hand near the opposite shoulder.
            hand_x = shoulder_x - sign * (arm_h * 0.15)
            hand_y = shoulder_y + fwd_y * (arm_h * 0.18)
            hand_z = shoulder_pz - arm_h * 0.32
        elif pose == 'hands_pockets':
            # Hands in pants pockets — casual/idle pose. Hands
            # tucked just below the belt level, slightly forward.
            hand_x = shoulder_x + sign * arm_r_top * 0.8
            hand_y = shoulder_y + fwd_y * arm_r_top * 1.5
            hand_z = shoulder_pz - arm_h * 0.78
        elif pose == 'one_arm_lean':
            # Right arm extended out for leaning on something
            # (counter, ice freezer, doorframe). Left arm hangs.
            if side == 'R':
                hand_x = shoulder_x + sign * (arm_h * 0.30)
                hand_y = shoulder_y + fwd_y * (arm_h * 0.20)
                hand_z = shoulder_pz - arm_h * 0.40

        # ELBOW · break the arm into UPPER ARM + FOREARM with a
        # bump at the joint. Elbow at 55% along the arm path,
        # slightly bent (lateral 4% offset).
        elbow_t = 0.55
        elbow_x = shoulder_x + (hand_x - shoulder_x) * elbow_t
        elbow_y = shoulder_y + (hand_y - shoulder_y) * elbow_t
        elbow_z = shoulder_pz + (hand_z - shoulder_pz) * elbow_t
        # Slight outward kink at elbow (relaxed bend)
        if pose == 'standing':
            elbow_x += sign * 0.015 * s
        # Upper arm
        _oriented_cyl(f"{name}_UpperArm_{side}",
                       (shoulder_x, shoulder_y, shoulder_pz),
                       (elbow_x, elbow_y, elbow_z),
                       arm_r_top, arm_r_top * 0.95,
                       jacket_color, segments=8)
        # Elbow bump
        _sphere_low(f"{name}_Elbow_{side}",
                    (elbow_x, elbow_y, elbow_z),
                    arm_r_top * 1.05, jacket_color,
                    rings=3, segments=6, squash_z=0.80)
        # Forearm (slightly thinner toward wrist)
        _oriented_cyl(f"{name}_Forearm_{side}",
                       (elbow_x, elbow_y, elbow_z),
                       (hand_x, hand_y, hand_z),
                       arm_r_top * 0.92, arm_r_bot,
                       jacket_color, segments=8)
        # Hand · spheroid fist + small thumb stub.
        _sphere_low(f"{name}_Hand_{side}",
                    (hand_x, hand_y, hand_z - hand_size * 0.35),
                    hand_size * 0.55, skin_color,
                    rings=3, segments=6, squash_z=0.85)
        # Thumb stub on the side facing forward
        thumb_off_x = sign * hand_size * 0.30
        _box(f"{name}_Thumb_{side}",
             (hand_x + thumb_off_x, hand_y, hand_z - hand_size * 0.30),
             (hand_size * 0.30, hand_size * 0.30, hand_size * 0.45),
             skin_color)
        # 3 KNUCKLE BUMPS on top of the hand (back-of-hand)
        for k_knuck in range(3):
            kx_off = (k_knuck - 1) * hand_size * 0.18
            _box(f"{name}_Knuckle_{side}_{k_knuck}",
                 (hand_x + sign * kx_off,
                  hand_y - fwd_y * hand_size * 0.20,
                  hand_z - hand_size * 0.55),
                 (hand_size * 0.14, hand_size * 0.14, hand_size * 0.16),
                 skin_color)
        hand_positions[side] = (hand_x, hand_y, hand_z)
    return hand_positions


def _build_neck(name, base_x, base_y, shoulder_z, s, skin_color):
    neck_h = PROP["neck_h"] * s
    neck_r = PROP["neck_r"] * s
    _cyl_taper(f"{name}_Neck",
               (base_x, base_y, shoulder_z + neck_h / 2),
               neck_r, neck_r, neck_h, skin_color, segments=6)
    return shoulder_z + neck_h


def _build_head(name, base_x, base_y, head_base_z, s,
                skin_color, hair_color, hair_style, facing='-Y',
                has_sunglasses=False, sunglasses_color=None,
                with_ears=False, with_mouth=False,
                mouth_color=(0.62, 0.30, 0.32, 1.0)):
    head_d = PROP["head_d"] * s
    head_squash = PROP["head_squash"]
    head_r = head_d / 2
    head_cz = head_base_z + head_r * head_squash
    # Skull (skin sphere) — narrower on the facing axis (head depth)
    # so the head is more egg-shaped than spherical from above
    _sphere_low(f"{name}_Head_Skull",
                (base_x, base_y, head_cz),
                head_r, skin_color,
                rings=4, segments=10, squash_z=head_squash)
    # CHEEKBONES · two small subtly-protruding skin spheres on the
    # sides of the head at eye height. Define the face's width
    # without exaggeration.
    fwd_x_h, fwd_y_h = _face_axis(facing)
    side_x_h = -fwd_y_h; side_y_h = fwd_x_h
    cheek_z = head_cz + head_r * 0.05
    for ch_side, ch_sign in (('L', -1), ('R', +1)):
        cx_pos = base_x + side_x_h * ch_sign * (head_r * 0.78) + fwd_x_h * (head_r * 0.55)
        cy_pos = base_y + side_y_h * ch_sign * (head_r * 0.78) + fwd_y_h * (head_r * 0.55)
        _sphere_low(f"{name}_Cheek_{ch_side}",
                    (cx_pos, cy_pos, cheek_z),
                    head_r * 0.22, skin_color,
                    rings=2, segments=6, squash_z=0.70)
    # JAW LINE · small angular box across the lower face giving
    # the head a clear chin/jaw silhouette from the side
    jaw_z = head_cz - head_r * 0.42
    jx = base_x + fwd_x_h * (head_r * 0.55)
    jy = base_y + fwd_y_h * (head_r * 0.55)
    if abs(fwd_y_h) > abs(fwd_x_h):
        _box(f"{name}_Jaw",
             (jx, jy, jaw_z),
             (head_d * 0.62, head_d * 0.50, head_d * 0.14),
             skin_color)
    else:
        _box(f"{name}_Jaw",
             (jx, jy, jaw_z),
             (head_d * 0.50, head_d * 0.62, head_d * 0.14),
             skin_color)
    # BROW RIDGE · always present (used to be tied to with_mouth).
    # Subtle skin-toned ridge above the eye line.
    br_z = head_cz + head_r * 0.20
    brx = base_x + fwd_x_h * (head_r * 0.92)
    bry = base_y + fwd_y_h * (head_r * 0.92)
    if abs(fwd_y_h) > abs(fwd_x_h):
        _box(f"{name}_BrowRidge",
             (brx, bry, br_z),
             (head_d * 0.78, head_d * 0.10, head_d * 0.08),
             skin_color)
    else:
        _box(f"{name}_BrowRidge",
             (brx, bry, br_z),
             (head_d * 0.10, head_d * 0.78, head_d * 0.08),
             skin_color)
    # Ears — small skin boxes on the head's left + right sides,
    # perpendicular to the facing axis.
    if with_ears:
        fwd_x, fwd_y = _face_axis(facing)
        # Side axis = facing perpendicular (rotated 90° around z)
        side_x = -fwd_y
        side_y =  fwd_x
        for side, sign in (('L', -1), ('R', +1)):
            ex = base_x + sign * side_x * (head_r * 0.95)
            ey = base_y + sign * side_y * (head_r * 0.95)
            _box(f"{name}_Ear_{side}",
                 (ex, ey, head_cz),
                 (0.06 * s if abs(side_x) < 0.5 else 0.04 * s,
                  0.04 * s if abs(side_x) < 0.5 else 0.06 * s,
                  head_d * 0.30),
                 skin_color)
    # Hair — varies by style
    if hair_style == 'bowl':
        # Mushroom bowl-cut: flattened dome covering top + forward
        # bang fringe + ASYMMETRIC side-sweep so the silhouette
        # isn't a perfect bowl.
        _sphere_low(f"{name}_Hair_Bowl",
                    (base_x, base_y, head_cz + head_r * 0.05),
                    head_r * 1.08, hair_color,
                    rings=3, segments=10, squash_z=0.65)
        fwd_x, fwd_y = _face_axis(facing)
        # Forward bang
        _box(f"{name}_Hair_Bang",
             (base_x + fwd_x * head_r * 0.45,
              base_y + fwd_y * head_r * 0.45,
              head_cz + head_r * 0.35),
             (head_d * 0.85 if abs(fwd_y) > abs(fwd_x) else 0.04,
              head_d * 0.85 if abs(fwd_x) > abs(fwd_y) else 0.04,
              head_d * 0.55),
             hair_color)
        # Asymmetric side-sweep — extra clump hanging off the LEFT
        # side (perpendicular to facing axis) so the bowl reads
        # less symmetric. Side axis = facing rotated 90° around z.
        side_x = -fwd_y; side_y = fwd_x
        _box(f"{name}_Hair_SideSweep",
             (base_x + side_x * head_r * 0.55 + fwd_x * head_r * 0.20,
              base_y + side_y * head_r * 0.55 + fwd_y * head_r * 0.20,
              head_cz - head_r * 0.05),
             (head_d * 0.30 if abs(side_x) > abs(side_y) else head_d * 0.45,
              head_d * 0.45 if abs(side_x) > abs(side_y) else head_d * 0.30,
              head_d * 0.50),
             hair_color)
    elif hair_style == 'short':
        _sphere_low(f"{name}_Hair_Cap",
                    (base_x, base_y, head_cz + head_r * 0.10),
                    head_r * 1.03, hair_color,
                    rings=3, segments=8, squash_z=0.55)
    elif hair_style == 'ponytail':
        # Crown cap
        _sphere_low(f"{name}_Hair_Crown",
                    (base_x, base_y, head_cz + head_r * 0.08),
                    head_r * 1.05, hair_color,
                    rings=3, segments=8, squash_z=0.60)
        # Ponytail trailing back from the crown
        fwd_x_p, fwd_y_p = _face_axis(facing)
        back_x = base_x - fwd_x_p * head_r * 0.85
        back_y = base_y - fwd_y_p * head_r * 0.85
        _cyl_taper(f"{name}_Hair_Ponytail",
                   (back_x, back_y, head_cz - head_r * 0.25),
                   head_r * 0.18, head_r * 0.08, head_d * 1.20,
                   hair_color, segments=6)
        # Hair tie band
        _cyl_taper(f"{name}_Hair_Tie",
                   (back_x, back_y, head_cz + head_r * 0.10),
                   head_r * 0.22, head_r * 0.22, 0.025,
                   (0.85, 0.20, 0.18, 1.0), segments=6)
    elif hair_style == 'cap':
        # Baseball cap — curved-front body + bill sticking forward
        _sphere_low(f"{name}_Hat_Crown",
                    (base_x, base_y, head_cz + head_r * 0.32),
                    head_r * 1.10, hair_color,
                    rings=3, segments=10, squash_z=0.55)
        fwd_x_c, fwd_y_c = _face_axis(facing)
        # Bill (visor)
        bx = base_x + fwd_x_c * head_r * 0.95
        by = base_y + fwd_y_c * head_r * 0.95
        if abs(fwd_y_c) > abs(fwd_x_c):
            _box(f"{name}_Hat_Bill",
                 (bx, by, head_cz + head_r * 0.28),
                 (head_d * 1.10, head_d * 0.55, 0.04),
                 hair_color)
        else:
            _box(f"{name}_Hat_Bill",
                 (bx, by, head_cz + head_r * 0.28),
                 (head_d * 0.55, head_d * 1.10, 0.04),
                 hair_color)
    elif hair_style == 'beanie':
        # Knit beanie — tall rounded cap sitting low on forehead
        _sphere_low(f"{name}_Hat_Beanie",
                    (base_x, base_y, head_cz + head_r * 0.42),
                    head_r * 1.18, hair_color,
                    rings=3, segments=10, squash_z=0.80)
        # Rolled brim
        _cyl_taper(f"{name}_Hat_BeanieBrim",
                   (base_x, base_y, head_cz + head_r * 0.10),
                   head_r * 1.08, head_r * 1.08, head_r * 0.18,
                   (hair_color[0] * 0.78, hair_color[1] * 0.78,
                    hair_color[2] * 0.78, hair_color[3]),
                   segments=10)
    elif hair_style == 'mohawk':
        # Center strip from forehead to back of head
        fwd_x_m, fwd_y_m = _face_axis(facing)
        if abs(fwd_y_m) > abs(fwd_x_m):
            _box(f"{name}_Hair_Mohawk",
                 (base_x, base_y, head_cz + head_r * 0.65),
                 (0.04, head_d * 1.0, head_d * 0.85),
                 hair_color)
        else:
            _box(f"{name}_Hair_Mohawk",
                 (base_x, base_y, head_cz + head_r * 0.65),
                 (head_d * 1.0, 0.04, head_d * 0.85),
                 hair_color)
        # Buzzed sides — short skin (no hair) — handled by no
        # additional geometry on the sides; skull sphere visible.
    elif hair_style == 'bald':
        pass    # skull already in skin colour
    # Sunglasses — horizontal band across the eye line, with EYES
    # peeking out underneath (small white circles + dark pupils
    # behind the lens for character). Even with shades, you can
    # see the suggestion of eyes through tinted plastic.
    if has_sunglasses and sunglasses_color is not None:
        fwd_x, fwd_y = _face_axis(facing)
        gx = base_x + fwd_x * (head_r * 0.95 + 0.005)
        gy = base_y + fwd_y * (head_r * 0.95 + 0.005)
        gz = head_cz + head_r * 0.10
        # Eyes BEHIND the glasses (placed first, then lens covers
        # most of them — but the bottom edge peeks).
        eye_offset = head_d * 0.22
        side_x = -fwd_y; side_y = fwd_x
        for eye_side, eye_sign in (('L', -1), ('R', +1)):
            ex = gx + side_x * eye_offset * eye_sign - fwd_x * 0.015
            ey = gy + side_y * eye_offset * eye_sign - fwd_y * 0.015
            ez = gz - 0.005
            # White sclera
            _sphere_low(f"{name}_Eye_{eye_side}",
                        (ex, ey, ez), head_d * 0.07,
                        (0.96, 0.94, 0.90, 1.0),
                        rings=3, segments=6)
            # Dark pupil offset slightly forward
            _sphere_low(f"{name}_Pupil_{eye_side}",
                        (ex + fwd_x * 0.01, ey + fwd_y * 0.01, ez),
                        head_d * 0.035,
                        (0.10, 0.08, 0.06, 1.0),
                        rings=2, segments=6)
        # Lens band — covers most of the eyes, with the bottom
        # edge slightly above the eye bottom so a sliver peeks.
        if abs(fwd_y) > abs(fwd_x):
            _box(f"{name}_Glasses",
                 (gx, gy, gz + head_d * 0.04),
                 (head_d * 0.95, 0.035, head_d * 0.18),
                 sunglasses_color)
            # Bridge — thin connector across the nose
            _box(f"{name}_GlassesBridge",
                 (gx, gy + 0.001, gz + head_d * 0.05),
                 (head_d * 0.10, 0.04, head_d * 0.04),
                 sunglasses_color)
        else:
            _box(f"{name}_Glasses",
                 (gx, gy, gz + head_d * 0.04),
                 (0.035, head_d * 0.95, head_d * 0.18),
                 sunglasses_color)
            _box(f"{name}_GlassesBridge",
                 (gx + 0.001, gy, gz + head_d * 0.05),
                 (0.04, head_d * 0.10, head_d * 0.04),
                 sunglasses_color)
    # FACIAL FEATURES · always present now (no more with_mouth gate).
    # Every face gets: eyes (visible even behind sunglasses), nose,
    # mouth/lips, eyebrows. Real PS2-era characters always had a
    # face — the absence was leaving figures looking blank.
    fwd_x, fwd_y = _face_axis(facing)

    # EYES (always) — two small dark dots on the face. Visible even
    # without sunglasses; sunglasses lens covers them but the
    # bottom edge peeks.
    if not has_sunglasses:
        eye_offset = head_d * 0.22
        side_x_e = -fwd_y; side_y_e = fwd_x
        eye_z = head_cz + head_r * 0.10
        for eye_side, eye_sign in (('L', -1), ('R', +1)):
            ex = base_x + side_x_e * eye_offset * eye_sign \
                 + fwd_x * (head_r * 0.95)
            ey = base_y + side_y_e * eye_offset * eye_sign \
                 + fwd_y * (head_r * 0.95)
            # White sclera
            _sphere_low(f"{name}_Eye_{eye_side}",
                        (ex, ey, eye_z), head_d * 0.07,
                        (0.96, 0.94, 0.90, 1.0),
                        rings=3, segments=6)
            # Dark pupil
            _sphere_low(f"{name}_Pupil_{eye_side}",
                        (ex + fwd_x * 0.01, ey + fwd_y * 0.01, eye_z),
                        head_d * 0.035,
                        (0.10, 0.08, 0.06, 1.0),
                        rings=2, segments=6)

    # NOSE · pyramidal nub centered between eyes and mouth
    nz = head_cz - head_r * 0.08
    nx = base_x + fwd_x * (head_r * 0.98 + 0.008)
    ny = base_y + fwd_y * (head_r * 0.98 + 0.008)
    if abs(fwd_y) > abs(fwd_x):
        _box(f"{name}_Nose",
             (nx, ny, nz),
             (head_d * 0.14, 0.05, head_d * 0.18),
             skin_color)
        # Nostril shadow (thin dark strip under the nose)
        _box(f"{name}_NoseShadow",
             (nx, ny, nz - head_d * 0.09),
             (head_d * 0.10, 0.04, head_d * 0.025),
             (skin_color[0] * 0.55, skin_color[1] * 0.55,
              skin_color[2] * 0.55, 1.0))
    else:
        _box(f"{name}_Nose",
             (nx, ny, nz),
             (0.05, head_d * 0.14, head_d * 0.18),
             skin_color)
        _box(f"{name}_NoseShadow",
             (nx, ny, nz - head_d * 0.09),
             (0.04, head_d * 0.10, head_d * 0.025),
             (skin_color[0] * 0.55, skin_color[1] * 0.55,
              skin_color[2] * 0.55, 1.0))

    # MOUTH / LIPS · two-tone (darker lower lip + lighter upper)
    mz_mouth = head_cz - head_r * 0.30
    mx = base_x + fwd_x * (head_r * 0.95 + 0.005)
    my = base_y + fwd_y * (head_r * 0.95 + 0.005)
    upper_lip_col = mouth_color
    lower_lip_col = (mouth_color[0] * 0.78, mouth_color[1] * 0.78,
                     mouth_color[2] * 0.78, mouth_color[3])
    if abs(fwd_y) > abs(fwd_x):
        # Upper lip
        _box(f"{name}_UpperLip",
             (mx, my, mz_mouth + head_d * 0.025),
             (head_d * 0.34, 0.02, head_d * 0.05),
             upper_lip_col)
        # Lower lip (darker, slightly wider)
        _box(f"{name}_LowerLip",
             (mx, my, mz_mouth - head_d * 0.025),
             (head_d * 0.36, 0.02, head_d * 0.055),
             lower_lip_col)
    else:
        _box(f"{name}_UpperLip",
             (mx, my, mz_mouth + head_d * 0.025),
             (0.02, head_d * 0.34, head_d * 0.05),
             upper_lip_col)
        _box(f"{name}_LowerLip",
             (mx, my, mz_mouth - head_d * 0.025),
             (0.02, head_d * 0.36, head_d * 0.055),
             lower_lip_col)

    # EYEBROWS · always present
    eb_z = head_cz + head_r * 0.28
    ebx = base_x + fwd_x * (head_r * 0.95 + 0.005)
    eby = base_y + fwd_y * (head_r * 0.95 + 0.005)
    for side, sign in (('L', -1), ('R', +1)):
        perp_x = -fwd_y; perp_y = fwd_x
        ox = perp_x * head_d * 0.20 * sign
        oy = perp_y * head_d * 0.20 * sign
        if abs(fwd_y) > abs(fwd_x):
            _box(f"{name}_Eyebrow_{side}",
                 (ebx + ox, eby + oy, eb_z),
                 (head_d * 0.22, 0.025, head_d * 0.05),
                 hair_color)
        else:
            _box(f"{name}_Eyebrow_{side}",
                 (ebx + ox, eby + oy, eb_z),
                 (0.025, head_d * 0.22, head_d * 0.05),
                 hair_color)
    # CHIN · skin extension below the mouth — replaces the old jaw
    # box at this position with a tighter chin protrusion (the
    # broader jaw_box above the mouth handled jaw width).
    cz = head_cz - head_r * 0.50
    cx = base_x + fwd_x * (head_r * 0.85)
    cy = base_y + fwd_y * (head_r * 0.85)
    if abs(fwd_y) > abs(fwd_x):
        _box(f"{name}_Chin",
             (cx, cy, cz),
             (head_d * 0.30, head_d * 0.20, head_d * 0.12),
             skin_color)
    else:
        _box(f"{name}_Chin",
             (cx, cy, cz),
             (head_d * 0.20, head_d * 0.30, head_d * 0.12),
             skin_color)


def _build_scarf(name, base_x, base_y, shoulder_z, s, scarf_color):
    """Scarf / cravat — a thick collar wrap sitting just above the
    torso. Reads as the yellow Oliver Tree neckwear or any other
    collar accent."""
    if scarf_color is None:
        return
    scarf_r = PROP["neck_r"] * s * 1.8
    scarf_h = PROP["neck_h"] * s * 1.8
    _cyl_taper(f"{name}_Scarf",
               (base_x, base_y, shoulder_z + scarf_h / 2 - 0.01),
               scarf_r * 1.05, scarf_r, scarf_h, scarf_color,
               segments=10)


# ── PUBLIC API ─────────────────────────────────────────────────────

def human_figure(name, base_x, base_y, base_z, scale=1.0,
                 facing='-Y',
                 # Skin / hair
                 skin_color=(0.92, 0.75, 0.62, 1.0),
                 hair_style='short',
                 hair_color=(0.32, 0.22, 0.16, 1.0),
                 # Top
                 jacket_color=(0.62, 0.62, 0.62, 1.0),
                 yoke_color=None,
                 accent='none',
                 accent_color=None,
                 scarf_color=None,
                 # Bottom
                 pants_color=(0.40, 0.40, 0.42, 1.0),
                 pants_flare=1.0,
                 shoe_color=(0.18, 0.18, 0.20, 1.0),
                 # Face
                 has_sunglasses=False,
                 sunglasses_color=(0.15, 0.15, 0.15, 1.0),
                 with_ears=False,
                 with_mouth=False,
                 mouth_color=(0.62, 0.30, 0.32, 1.0),
                 jacket_puffy=False,
                 pose='standing',
                 lean_x=0.0):
    """Build a parametric standing human figure at (base_x, base_y,
    base_z) with feet on the ground at base_z. See module docstring
    for full parameter notes."""
    s = scale
    # Feet first (they sit at base_z)
    _build_feet(name, base_x, base_y, base_z, s, facing, shoe_color)
    # Legs from base_z + foot_h up to pelvis
    pelvis_bottom_z = _build_legs(name, base_x, base_y,
                                  base_z + PROP["foot_h"] * s,
                                  s, pants_color, pants_flare)
    # Torso — contrapposto lean offsets upper body by lean_x metres.
    # Pelvis stays anchored on the leg centreline so the figure
    # reads as a hip shift / shoulder counter-tilt classical pose.
    shoulder_z = _build_torso(name, base_x + lean_x, base_y,
                              pelvis_bottom_z + PROP["pelvis_h"] * s,
                              s, jacket_color,
                              yoke_color=yoke_color,
                              accent=accent,
                              accent_color=accent_color,
                              facing=facing,
                              puffy=jacket_puffy)
    # Arms — pose-aware, shifted by the same lean offset as torso
    hand_positions = _build_arms(name, base_x + lean_x, base_y,
                                  shoulder_z, s,
                                  jacket_color, skin_color,
                                  pose=pose, facing=facing)
    # Scarf wraps the neck base — also leans with the torso
    _build_scarf(name, base_x + lean_x, base_y, shoulder_z, s, scarf_color)
    # Neck on top of scarf area
    head_base_z = _build_neck(name, base_x + lean_x, base_y,
                              shoulder_z, s, skin_color)
    # Head — counter-tilt by half the lean for a subtle s-curve
    head_x = base_x + lean_x * 0.5
    _build_head(name, head_x, base_y, head_base_z, s,
                skin_color, hair_color, hair_style, facing,
                has_sunglasses=has_sunglasses,
                sunglasses_color=sunglasses_color,
                with_ears=with_ears,
                with_mouth=with_mouth,
                mouth_color=mouth_color)
    return {"hands": hand_positions,
            "head_base_z": head_base_z,
            "shoulder_z": shoulder_z}


__all__ = ["human_figure", "PROP"]
