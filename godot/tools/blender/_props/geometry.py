# _props/geometry.py
# ════════════════════════════════════════════════════════════════
# Geometry primitives + Blender scene helpers used by every locale
# builder. Vertex-coloured, no PBR — matches the rest of the
# 3D pipeline (per CLAUDE.md "vertex-coloured locale geometry").
#
# Two primitives:
#   · make_box  — axis-aligned 6-face box with optional open faces
#   · make_cyl  — N-segment cylinder (default 8) about X / Y / Z
# Both attach a "Col" vertex-color layer initialised to base_color
# so the GLB export carries the colour without needing a material.
#
# clear_scene wipes Blender state — call at the top of every
# builder's main() so re-running the script doesn't accumulate
# objects from a prior run.
# ════════════════════════════════════════════════════════════════
import math
try:
    import bpy   # type: ignore
except ImportError:
    bpy = None   # Allow import outside Blender (lint / tests)


def clear_scene():
    if bpy is None:
        return
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh, do_unlink=True)


def _finalize_mesh(name, verts, faces, base_color):
    if bpy is None:
        return None
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="Col")
    layer = mesh.vertex_colors["Col"]
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            layer.data[li].color = base_color
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def make_box(name, center, size, base_color, open_faces=None):
    """6-face axis-aligned box centered at `center` with `size`
    (full XYZ dimensions). open_faces is an optional set of face
    tags ('+X','-X','+Y','-Y','+Z','-Z') to omit for inset hollows."""
    open_faces = open_faces or set()
    cx, cy, cz = center
    sx, sy, sz = size
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    verts = [
        (cx-hx, cy-hy, cz-hz), (cx+hx, cy-hy, cz-hz),
        (cx+hx, cy+hy, cz-hz), (cx-hx, cy+hy, cz-hz),
        (cx-hx, cy-hy, cz+hz), (cx+hx, cy-hy, cz+hz),
        (cx+hx, cy+hy, cz+hz), (cx-hx, cy+hy, cz+hz),
    ]
    face_defs = [('-Z',(0,3,2,1)), ('+Z',(4,5,6,7)),
                 ('-Y',(0,1,5,4)), ('+Y',(2,3,7,6)),
                 ('-X',(3,0,4,7)), ('+X',(1,2,6,5))]
    out_faces = [vids for tag, vids in face_defs if tag not in open_faces]
    return _finalize_mesh(name, verts, out_faces, base_color)


def make_cyl(name, center, radius, height, base_color,
             segments=8, axis='Z'):
    """N-segment cylinder. axis='Z' (default — height along Z),
    'X', or 'Y'. Segments default 8 — bump up to 12-16 for very
    prominent cylinders that read at close range."""
    cx, cy, cz = center
    h2 = height / 2.0
    verts = []
    for ring in (0, 1):
        z_off = -h2 if ring == 0 else h2
        for i in range(segments):
            ang = 2.0 * math.pi * i / segments
            a = math.cos(ang) * radius
            b = math.sin(ang) * radius
            if axis == 'Z':
                verts.append((cx + a, cy + b, cz + z_off))
            elif axis == 'Y':
                verts.append((cx + a, cy + z_off, cz + b))
            else:    # 'X'
                verts.append((cx + z_off, cy + a, cz + b))
    faces = []
    for i in range(segments):
        ni = (i + 1) % segments
        faces.append([i, ni, ni + segments, i + segments])
    faces.append(list(reversed(range(segments))))
    faces.append(list(range(segments, segments * 2)))
    return _finalize_mesh(name, verts, faces, base_color)


def export_glb(out_path, *, export_lights=False, export_cameras=False):
    """Standard glTF export — select-all + use_selection=False so
    every object lands in the GLB. Defaults match what all our
    locale builders need."""
    if bpy is None:
        return
    import os
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    bpy.ops.object.select_all(action='SELECT')
    base = {'filepath': out_path, 'export_format': 'GLB',
            'use_selection': False, 'export_apply': True,
            'export_lights': export_lights,
            'export_cameras': export_cameras}
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    legacy = {}
    if 'export_colors' in rna.properties:  legacy['export_colors'] = True
    if 'export_normals' in rna.properties: legacy['export_normals'] = True
    bpy.ops.export_scene.gltf(**base, **legacy)
    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[props.export_glb] wrote {out_path} ({size} bytes)")
