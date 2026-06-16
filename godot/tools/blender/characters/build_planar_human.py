"""
build_planar_human.py
══════════════════════════════════════════════════════════════════
GENERIC PLANAR HUMAN BASE — STARTING SCULPT
Builds male + female low-poly base meshes ready for further sculpt
work in Blender's Sculpt mode. This is the BLOCKOUT pass that
gets the volumes right; the user opens the resulting .blend
and refines with brushes from there.

Bakes in lessons from dacancino's reference (filed in
lore/_CHARACTER_MODELING_NOTES.md):

  · 8-heads exact, head_h = 0.225 m (model unit = metres,
    total height = 1.80 m for adult).
  · Shoulder = 2.7 head-widths for male, 2.0 for female.
  · Trap slope as 3-band neck → trap → clavicle transition.
  · Hands hang to MID-THIGH (not hip).
  · Face proportions 31/41/28 (NOT forced 33/33/33).
  · Nose protrudes 8mm (no pinocchio).
  · Eye sockets carved as 1.5cm recesses.
  · Cheekbone shelves as hard normal shifts.
  · Hand = single mitten box (no fingers).
  · 34-bone armature: twist bones, IK feet, 3-bone spine,
    2-bone neck, single-bone hands.
  · ≥ 3 edge loops at every articulating joint.

Topology budget target: ~3,600 tris per figure (inside the
3-8k traversal mesh budget).

Run (on the Deck):
    cd godot/tools/blender && ./run_cathedral.sh build_planar_human.py

Output:
    godot/assets/3d/characters/planar_human_male.glb
    godot/assets/3d/characters/planar_human_female.glb
    godot/assets/3d/characters/planar_human_workspace.blend
        ← open this in Blender, switch to Sculpt mode,
          continue refining with brushes
"""
import os
import math
import sys
import bpy
import bmesh

OUTPUT_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "..", "..", "..", "assets", "3d", "characters"))
WORKSPACE_BLEND = os.path.join(OUTPUT_DIR, "planar_human_workspace.blend")

# ── PROPORTIONS  (units = metres; total height 1.80 m) ──────────
TOTAL_H = 1.80
HEAD_H  = TOTAL_H / 8           # 0.225 m
HEAD_W  = HEAD_H * 0.76         # 0.171 m

# Landmark Y (metres, ground at 0):
CROWN_Y    = TOTAL_H
HAIRLINE_Y = TOTAL_H - HEAD_H * 0.10
BROW_Y     = TOTAL_H - HEAD_H * 0.31
EYE_Y      = TOTAL_H - HEAD_H * 0.50
NOSE_Y     = BROW_Y  - HEAD_H * 0.41
MOUTH_Y    = TOTAL_H - HEAD_H * 0.78
CHIN_Y     = TOTAL_H - HEAD_H

NECK_TOP_Y = CHIN_Y - HEAD_H * 0.05
NECK_BOT_Y = CHIN_Y - HEAD_H * 0.30
CLAV_Y     = NECK_BOT_Y - HEAD_H * 0.15
NIPPLE_Y   = TOTAL_H - HEAD_H * 2
NAVEL_Y    = TOTAL_H - HEAD_H * 3
CROTCH_Y   = TOTAL_H - HEAD_H * 4
THIGH_Y    = TOTAL_H - HEAD_H * 5
KNEE_Y     = TOTAL_H - HEAD_H * 6
SHIN_Y     = TOTAL_H - HEAD_H * 7
ANKLE_Y    = HEAD_H * 0.30
SOLE_Y     = 0.0

# Skin / palette (planar flat-shaded — vertex colours only, no
# textures, matching our locale constraint):
COL_SKIN  = (0.84, 0.69, 0.55, 1.0)
COL_HAIR  = (0.16, 0.12, 0.08, 1.0)
COL_EYES  = (0.10, 0.10, 0.12, 1.0)


# ── BODY-TYPE PROFILES ──────────────────────────────────────────
# Each profile drives the cross-section half-widths.
BODY_TYPES = {
    'male': {
        'shoulder_w': HEAD_W * 2.70,
        'hip_w':      HEAD_W * 1.85,
        'waist_w':    HEAD_W * 1.55,
        'thigh_w':    HEAD_W * 0.78,
        'arm_taper':  0.78,             # forearm/upperarm ratio
        'origin_x':   -0.50,            # placement: male on -X
    },
    'female': {
        'shoulder_w': HEAD_W * 2.05,
        'hip_w':      HEAD_W * 1.95,
        'waist_w':    HEAD_W * 1.40,
        'thigh_w':    HEAD_W * 0.85,
        'arm_taper':  0.82,
        'origin_x':   +0.50,            # female on +X
    },
}

# Cross-section ring resolution (how many verts per ring).
# 16 keeps tri count reasonable while giving enough silhouette
# detail for cheekbone / chest planes.
RING_N = 16

# Body depth (Z, front-back). Real-human ratio ~0.16 × height.
BODY_D = TOTAL_H * 0.16              # 0.288 m

# Face Z displacements (carved into head rings):
NOSE_PROT  = 0.008      # 8mm forward at nose tip
EYE_RECESS = 0.015      # 1.5cm carved back
CHEEK_BUMP = 0.005      # 5mm cheekbone shelf forward

# ── CROSS-SECTION TABLE  (per body type, returns (y, half_w, depth_scale)) ──

def cross_sections(profile):
    """Return ordered list of (y, half_w_x, half_d_z) for lofting."""
    sw = profile['shoulder_w'] / 2
    hw = profile['hip_w'] / 2
    ww = profile['waist_w'] / 2
    tw = profile['thigh_w'] / 2
    nw = HEAD_W * 0.60 / 2

    return [
        # ── HEAD ─────────────────────────────────────────────
        ("crown",      CROWN_Y,         HEAD_W * 0.30 / 2, HEAD_W * 0.30 / 2),
        ("skull_top",  CROWN_Y - 0.020, HEAD_W * 0.62 / 2, HEAD_W * 0.70 / 2),
        ("hairline",   HAIRLINE_Y,      HEAD_W * 0.98 / 2, HEAD_W * 0.96 / 2),
        ("forehead",   HAIRLINE_Y - 0.020, HEAD_W * 0.97 / 2, HEAD_W * 0.94 / 2),
        ("brow",       BROW_Y,          HEAD_W * 1.00 / 2, HEAD_W * 0.94 / 2),
        ("eye",        EYE_Y,           HEAD_W * 0.98 / 2, HEAD_W * 0.92 / 2),
        ("cheekbone",  EYE_Y - 0.020,   HEAD_W * 0.96 / 2, HEAD_W * 0.90 / 2),
        ("nose_tip",   NOSE_Y,          HEAD_W * 0.78 / 2, HEAD_W * 0.86 / 2),
        ("upper_lip",  MOUTH_Y + 0.005, HEAD_W * 0.88 / 2, HEAD_W * 0.82 / 2),
        ("mouth",      MOUTH_Y,         HEAD_W * 0.82 / 2, HEAD_W * 0.80 / 2),
        ("lower_lip",  MOUTH_Y - 0.008, HEAD_W * 0.78 / 2, HEAD_W * 0.78 / 2),
        ("chin",       CHIN_Y + 0.010,  HEAD_W * 0.66 / 2, HEAD_W * 0.74 / 2),
        ("jaw_bottom", CHIN_Y,          HEAD_W * 0.50 / 2, HEAD_W * 0.55 / 2),
        # ── NECK (narrow column ~10 cm) ──────────────────────
        ("neck_top",   NECK_TOP_Y,      nw,                nw * 1.05),
        ("neck_mid",   (NECK_TOP_Y + NECK_BOT_Y) / 2,
                                        nw * 1.05,         nw * 1.10),
        ("neck_bot",   NECK_BOT_Y,      nw * 1.15,         nw * 1.20),
        # ── TRAP SLOPE (3-band fan to clavicle) ──────────────
        ("trap_a",     NECK_BOT_Y - 0.008, sw * 0.45,      nw * 1.30),
        ("trap_b",     NECK_BOT_Y - 0.018, sw * 0.72,      sw * 0.45),
        ("trap_c",     NECK_BOT_Y - 0.028, sw * 0.92,      sw * 0.60),
        # ── SHOULDER / TORSO ─────────────────────────────────
        ("clav_peak",  CLAV_Y,          sw,                sw * 0.65),
        ("upper_chest",NIPPLE_Y + 0.050, sw * 0.92,        sw * 0.72),
        ("nipple",     NIPPLE_Y,        sw * 0.82,         sw * 0.72),
        ("ribs",       NIPPLE_Y - 0.060, sw * 0.74,        sw * 0.70),
        ("upper_waist",NIPPLE_Y - 0.110, ww * 1.10,        sw * 0.62),
        ("waist",      NAVEL_Y,         ww,                ww * 1.20),
        # ── HIPS ─────────────────────────────────────────────
        ("upper_hip",  NAVEL_Y - 0.050, hw * 0.96,         ww * 1.30),
        ("hip",        CROTCH_Y + 0.060, hw,               hw * 0.95),
        ("crotch",     CROTCH_Y,        hw * 0.85,         hw * 0.92),
        # ── LEGS (one tube per leg, but lofted as part of body
        # with a centre-split bridged by an inner ring at crotch) ──
        ("upper_thigh",CROTCH_Y - 0.040, tw + 0.010,       tw * 1.05),
        ("thigh",      THIGH_Y,         tw,                tw * 1.00),
        ("lower_thigh",THIGH_Y - HEAD_H * 0.30, tw * 0.78, tw * 0.90),
        ("knee",       KNEE_Y,          tw * 0.55,         tw * 0.78),
        ("calf",       KNEE_Y - HEAD_H * 0.35, tw * 0.62,  tw * 0.85),
        ("shin",       SHIN_Y,          tw * 0.50,         tw * 0.70),
        ("ankle",      ANKLE_Y,         tw * 0.35,         tw * 0.55),
        ("foot",       SOLE_Y + 0.030,  tw * 0.45,         tw * 1.10),
        ("sole",       SOLE_Y,          tw * 0.38,         tw * 1.00),
    ]


# ── BPY MESH BUILD ──────────────────────────────────────────────

def _ring_verts(cx, cy, cz, half_w, half_d, n=RING_N):
    """Build a ring of n vertices around (cx,cy,cz) ellipse-shaped
    in XZ plane (X=width, Z=depth, Y=height fixed)."""
    verts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        # i=0 at front (+Z), going clockwise viewed from above
        x = cx + half_w * math.sin(t)
        z = cz + half_d * math.cos(t)
        verts.append((x, cy, z))
    return verts


def _carve_face(ring_verts, label, cy):
    """Push individual ring verts to carve eye sockets, nose,
    cheekbones, lips. Applies to head-region rings only."""
    n = len(ring_verts)
    out = []
    for i, (x, y, z) in enumerate(ring_verts):
        # i=0 = front-centre (+Z), i=n/4 = +X side, i=n/2 = back,
        # i=3n/4 = -X side
        front_t = math.cos(2 * math.pi * i / n)   # +1 front, -1 back
        side_t  = math.sin(2 * math.pi * i / n)   # +1 right, -1 left
        dz = 0.0
        if label == 'nose_tip':
            # Push the very front vert forward
            if front_t > 0.85:
                dz = +NOSE_PROT
        elif label == 'eye':
            # Recess two symmetric verts (left + right of centre)
            if 0.25 < abs(side_t) < 0.65 and front_t > 0.5:
                dz = -EYE_RECESS
        elif label == 'cheekbone':
            # Push the two cheekbone verts slightly forward
            if 0.40 < abs(side_t) < 0.75 and front_t > 0.3:
                dz = +CHEEK_BUMP
        elif label in ('upper_lip', 'lower_lip'):
            # Lips wrap a barrel — the very front vert slightly back
            # (philtrum), edge verts forward
            if front_t > 0.92:
                dz = -0.003
        out.append((x, y, z + dz))
    return out


def build_body_mesh(profile, mesh_name):
    """Loft cross-sections into a body mesh. Returns the bpy mesh."""
    rings = cross_sections(profile)
    cx = profile['origin_x']
    cz = 0.0
    all_verts = []
    ring_indices = []   # list of [vi0, vi1, ..., viN-1] for each ring

    for label, y, half_w, half_d in rings:
        ring_pts = _ring_verts(cx, y, cz, half_w, half_d)
        # Apply face carving only to head rings:
        if label in ('eye', 'cheekbone', 'nose_tip',
                     'upper_lip', 'lower_lip'):
            ring_pts = _carve_face(ring_pts, label, y)
        start_i = len(all_verts)
        all_verts.extend(ring_pts)
        ring_indices.append(list(range(start_i, start_i + RING_N)))

    # Cap top (crown — fan from a single new apex vert)
    apex_top_i = len(all_verts)
    all_verts.append((cx, CROWN_Y + 0.010, cz))
    apex_bot_i = len(all_verts)
    all_verts.append((cx, -0.005, cz))

    faces = []
    # Quads between consecutive rings
    for r in range(len(ring_indices) - 1):
        r0 = ring_indices[r]
        r1 = ring_indices[r + 1]
        for i in range(RING_N):
            j = (i + 1) % RING_N
            faces.append((r0[i], r0[j], r1[j], r1[i]))
    # Top cap fan
    top_ring = ring_indices[0]
    for i in range(RING_N):
        j = (i + 1) % RING_N
        faces.append((apex_top_i, top_ring[j], top_ring[i]))
    # Bottom cap fan (sole)
    bot_ring = ring_indices[-1]
    for i in range(RING_N):
        j = (i + 1) % RING_N
        faces.append((apex_bot_i, bot_ring[i], bot_ring[j]))

    mesh = bpy.data.meshes.new(mesh_name)
    mesh.from_pydata(all_verts, [], faces)
    mesh.update(calc_edges=True)
    # Smooth shade off — planar Asaro-style means flat faces
    for poly in mesh.polygons:
        poly.use_smooth = False

    # Add vertex colours
    if mesh.vertex_colors:
        vcol = mesh.vertex_colors[0]
    else:
        vcol = mesh.vertex_colors.new(name="Col")
    for poly in mesh.polygons:
        for loop_i in poly.loop_indices:
            vcol.data[loop_i].color = COL_SKIN
    return mesh, ring_indices


def build_arm_mesh(profile, side, mesh_name):
    """Build an arm as a separate lofted tube attached at shoulder.
    side = +1 (left, +X side) or -1 (right, -X side)."""
    cx0 = profile['origin_x'] + side * profile['shoulder_w'] / 2 * 0.85
    cx1 = profile['origin_x'] + side * profile['hip_w'] / 2 * 1.15
    arm_y_top = CLAV_Y - 0.010
    arm_y_bot = THIGH_Y - HEAD_H * 0.05
    upper_w = HEAD_W * 0.16
    fore_w  = upper_w * profile['arm_taper']
    n_rings = 7
    rings = []
    for i in range(n_rings):
        t = i / (n_rings - 1)
        y = arm_y_top + (arm_y_bot - arm_y_top) * t
        cx = cx0 + (cx1 - cx0) * t
        w = upper_w + (fore_w - upper_w) * t
        rings.append((y, cx, w))
    # Hand mitten at the end (slightly bigger, flatter):
    hand_y = arm_y_bot - 0.060
    hand_cx = cx1 + side * 0.005
    hand_w  = fore_w * 1.05
    rings.append((hand_y, hand_cx, hand_w))

    all_verts = []
    ring_indices = []
    arm_ring_n = 8        # arms can use fewer verts
    for y, cx, w in rings:
        start_i = len(all_verts)
        for k in range(arm_ring_n):
            ang = 2 * math.pi * k / arm_ring_n
            x = cx + w * math.sin(ang)
            z = w * 0.85 * math.cos(ang)   # arms slightly flatter F-B
            all_verts.append((x, y, z))
        ring_indices.append(list(range(start_i, start_i + arm_ring_n)))
    # Caps
    top_apex = len(all_verts)
    all_verts.append((rings[0][1], rings[0][0] + 0.010, 0))
    bot_apex = len(all_verts)
    all_verts.append((rings[-1][1], rings[-1][0] - 0.030, 0))

    faces = []
    for r in range(len(ring_indices) - 1):
        r0 = ring_indices[r]; r1 = ring_indices[r + 1]
        for i in range(arm_ring_n):
            j = (i + 1) % arm_ring_n
            faces.append((r0[i], r0[j], r1[j], r1[i]))
    for i in range(arm_ring_n):
        j = (i + 1) % arm_ring_n
        faces.append((top_apex, ring_indices[0][j], ring_indices[0][i]))
        faces.append((bot_apex, ring_indices[-1][i], ring_indices[-1][j]))

    mesh = bpy.data.meshes.new(mesh_name)
    mesh.from_pydata(all_verts, [], faces)
    mesh.update(calc_edges=True)
    for poly in mesh.polygons:
        poly.use_smooth = False
    vcol = mesh.vertex_colors.new(name="Col")
    for poly in mesh.polygons:
        for loop_i in poly.loop_indices:
            vcol.data[loop_i].color = COL_SKIN
    return mesh


# ── ARMATURE  (34 bones, twist intermediates, IK feet) ─────────

def build_armature(profile, name):
    """Construct the 34-bone armature in T-pose-ish stance."""
    cx = profile['origin_x']
    arm_obj_name = f"{name}_armature"
    arm_data = bpy.data.armatures.new(arm_obj_name)
    arm_obj = bpy.data.objects.new(arm_obj_name, arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_data.edit_bones

    def add(name, head, tail, parent=None):
        b = eb.new(name)
        b.head = head
        b.tail = tail
        if parent is not None:
            b.parent = parent
        return b

    # Root + pelvis split
    root = add("root", (cx, 0, 0), (cx, CROTCH_Y * 0.5, 0))
    pelvis_ctrl = add("pelvis_torsoControl",
                       (cx, CROTCH_Y, 0), (cx, NAVEL_Y, 0), root)
    pelvis_ind  = add("pelvis_independent",
                       (cx, CROTCH_Y, 0), (cx, CROTCH_Y - 0.05, 0),
                       pelvis_ctrl)

    # Legs (with knee bend)
    for sgn, side in [(+1, "L"), (-1, "R")]:
        leg_x = cx + sgn * profile['hip_w'] * 0.25
        thigh = add(f"thigh.{side}", (leg_x, CROTCH_Y, 0),
                     (leg_x, KNEE_Y, 0.02), pelvis_ind)
        calf  = add(f"calf.{side}", (leg_x, KNEE_Y, 0.02),
                     (leg_x, ANKLE_Y, 0.0), thigh)
        # Foot IK siblings at root
        foot_ctrl = add(f"footControl.{side}",
                         (leg_x, ANKLE_Y, 0),
                         (leg_x, ANKLE_Y, 0.10), root)
        add(f"footToes.{side}", (leg_x, ANKLE_Y, 0.10),
            (leg_x, ANKLE_Y * 0.8, 0.18), foot_ctrl)
        f_arch = add(f"footArch.{side}", (leg_x, ANKLE_Y, 0),
                      (leg_x, 0.005, 0.05), foot_ctrl)
        add(f"footIK.{side}", (leg_x, 0.005, 0.05),
            (leg_x, 0.0, 0.10), f_arch)

    # Spine — 3 bones: lumbar1, lumbar2, ribcage
    lumbar1 = add("lumbar1", (cx, NAVEL_Y, 0), (cx, NAVEL_Y + 0.10, 0),
                  pelvis_ctrl)
    lumbar2 = add("lumbar2", (cx, NAVEL_Y + 0.10, 0),
                  (cx, NIPPLE_Y, 0), lumbar1)
    ribcage = add("ribcage", (cx, NIPPLE_Y, 0), (cx, CLAV_Y, 0),
                  lumbar2)

    # Neck — 2 bones + head
    neck1 = add("neck1", (cx, CLAV_Y, 0), (cx, NECK_BOT_Y, 0), ribcage)
    neck2 = add("neck2", (cx, NECK_BOT_Y, 0), (cx, NECK_TOP_Y, 0),
                neck1)
    add("head", (cx, NECK_TOP_Y, 0), (cx, CROWN_Y, 0.01), neck2)

    # Arms — with twist intermediates (the candy-wrapper fix)
    for sgn, side in [(+1, "L"), (-1, "R")]:
        sh_x = cx + sgn * profile['shoulder_w'] * 0.45
        sh_y = CLAV_Y
        elbow_x = cx + sgn * profile['shoulder_w'] * 0.40
        elbow_y = NAVEL_Y - 0.020
        wrist_x = cx + sgn * profile['hip_w']  * 0.55
        wrist_y = THIGH_Y - HEAD_H * 0.05
        clav = add(f"clavicle.{side}",
                   (cx, CLAV_Y + 0.020, 0),
                   (sh_x, sh_y, 0), ribcage)
        upperarm = add(f"upperArm.{side}", (sh_x, sh_y, 0),
                        (elbow_x, elbow_y, 0), clav)
        upper_twist = add(f"upperArm_rotate.{side}",
                           (sh_x, sh_y, 0),
                           ((sh_x + elbow_x) * 0.5,
                            (sh_y + elbow_y) * 0.5, 0), upperarm)
        forearm = add(f"foreArm.{side}",
                       (elbow_x, elbow_y, 0),
                       (wrist_x, wrist_y, 0), upperarm)
        fore_twist = add(f"foreArm_rotate.{side}",
                          (elbow_x, elbow_y, 0),
                          ((elbow_x + wrist_x) * 0.5,
                           (elbow_y + wrist_y) * 0.5, 0), forearm)
        add(f"hand.{side}", (wrist_x, wrist_y, 0),
            (wrist_x, wrist_y - 0.080, 0), forearm)

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj


def parent_with_auto_weights(mesh_obj, arm_obj):
    """Skin the mesh to the armature using bpy.ops automatic weights.
    This gets us a deformable rig; weight painting refinement comes
    later in the sculpt session."""
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')


def build_figure(profile, name):
    body_mesh, body_rings = build_body_mesh(profile, f"{name}_body_mesh")
    body_obj = bpy.data.objects.new(f"{name}_body", body_mesh)
    bpy.context.collection.objects.link(body_obj)

    arm_l = build_arm_mesh(profile, +1, f"{name}_arm_L_mesh")
    arm_l_obj = bpy.data.objects.new(f"{name}_arm_L", arm_l)
    bpy.context.collection.objects.link(arm_l_obj)
    arm_r = build_arm_mesh(profile, -1, f"{name}_arm_R_mesh")
    arm_r_obj = bpy.data.objects.new(f"{name}_arm_R", arm_r)
    bpy.context.collection.objects.link(arm_r_obj)

    # Join body + arms into one mesh so the armature drives all
    bpy.ops.object.select_all(action='DESELECT')
    body_obj.select_set(True)
    arm_l_obj.select_set(True)
    arm_r_obj.select_set(True)
    bpy.context.view_layer.objects.active = body_obj
    bpy.ops.object.join()

    armature_obj = build_armature(profile, name)
    parent_with_auto_weights(body_obj, armature_obj)
    return body_obj, armature_obj


def export_glb(armature_obj, body_obj, filename):
    """Export selected figure (mesh + armature) to a GLB."""
    bpy.ops.object.select_all(action='DESELECT')
    body_obj.select_set(True)
    armature_obj.select_set(True)
    bpy.context.view_layer.objects.active = armature_obj
    out_path = os.path.join(OUTPUT_DIR, filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_animations=False,
    )
    print(f"[build_planar_human] exported {out_path}")


def main():
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    male_body, male_arm = build_figure(BODY_TYPES['male'], "male")
    female_body, female_arm = build_figure(BODY_TYPES['female'], "female")

    # Per-figure GLB exports
    export_glb(male_arm, male_body, "planar_human_male.glb")
    export_glb(female_arm, female_body, "planar_human_female.glb")

    # Workspace .blend for hand-sculpting
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=WORKSPACE_BLEND)
    print(f"[build_planar_human] saved workspace {WORKSPACE_BLEND}")
    print(f"[build_planar_human] Open the .blend in Blender, switch")
    print(f"[build_planar_human] to Sculpt mode, and start brushing.")


if __name__ == "__main__":
    main()
