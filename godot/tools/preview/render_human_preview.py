"""
render_human_preview.py — orthographic preview renderer for the
human_sculpt figures. Builds each body_type under stubbed bpy,
captures every (verts, faces, color) emit, then renders front +
side orthographic views into a PNG. Used to preview figures
WITHOUT rebuilding the full Blender GLB on the Deck.

Outputs /tmp/human_previews.png.
"""
import sys, math, os
from PIL import Image, ImageDraw, ImageFont

class _Anything:
    def __getattr__(self, k): return _Anything()
    def __setattr__(self, k, v): pass
    def __getitem__(self, k): return _Anything()
    def __setitem__(self, k, v): pass
    def __call__(self, *a, **k): return _Anything()
    def __iter__(self): return iter([])
    def __contains__(self, k): return True
    def __bool__(self): return True
    def __float__(self): return 0.0
    def __int__(self): return 0
    def __len__(self): return 0
class _Bpy:
    def __getattr__(self, k): return _Anything()
sys.modules['bpy'] = _Bpy()

sys.path.insert(0, '/home/user/modern-mythology/godot/tools/blender/locales')
import importlib
import human_sculpt_v2 as hs
importlib.reload(hs)

# Intercept _finalize_mesh
_meshes = []
_orig = hs._finalize_mesh
def _cap(name, verts, faces, color):
    _meshes.append((name, [tuple(v) for v in verts],
                    [list(f) for f in faces], tuple(color)))
    return _orig(name, verts, faces, color)
hs._finalize_mesh = _cap

# Camera projections
def project_front(v):
    # Figure faces -Y, so camera at -infinity Y looking +Y shows
    # the face. Depth = -Y so closer-to-camera (more negative Y)
    # renders LAST (higher depth value = later in painter's sort).
    return v[0], v[2], -v[1]
def project_side(v):      # YZ plane (X toward camera, from +X side)
    return v[1], v[2], v[0]
def project_iso(v):
    # Simple iso: rotate 30° + 30° elevation
    cos_a = math.cos(math.radians(30))
    sin_a = math.sin(math.radians(30))
    x_iso = v[0] * cos_a - v[1] * sin_a
    y_iso = v[2] + 0.5 * (v[0] * sin_a + v[1] * cos_a)
    depth = v[0] * sin_a + v[1] * cos_a
    return x_iso, y_iso, depth

def render_view(meshes, project, w=300, h=600,
                world_min_x=-0.4, world_max_x=0.4,
                world_min_y=-0.05, world_max_y=2.10):
    img = Image.new('RGB', (w, h), (28, 30, 34))
    draw = ImageDraw.Draw(img)
    def world_to_pixel(wx, wy):
        u = (wx - world_min_x) / (world_max_x - world_min_x)
        v = (wy - world_min_y) / (world_max_y - world_min_y)
        return (int(u * w), int(h - v * h))
    # Build faces list with depth + projected pixel coords + shade
    flat = []
    light = (0.5, 0.7, 0.5)  # light direction
    light_len = math.sqrt(sum(c*c for c in light))
    light = tuple(c / light_len for c in light)
    for (name, verts, faces, color) in meshes:
        proj = [project(v) for v in verts]
        for face in faces:
            if len(face) < 3:
                continue
            depth = sum(proj[i][2] for i in face) / len(face)
            # Compute approx face normal from first 3 verts
            v0 = verts[face[0]]
            v1 = verts[face[1]]
            v2 = verts[face[2]]
            e1 = (v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2])
            e2 = (v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2])
            nx = e1[1]*e2[2] - e1[2]*e2[1]
            ny = e1[2]*e2[0] - e1[0]*e2[2]
            nz = e1[0]*e2[1] - e1[1]*e2[0]
            nlen = math.sqrt(nx*nx+ny*ny+nz*nz) or 1
            nx, ny, nz = nx/nlen, ny/nlen, nz/nlen
            ndotl = max(0.25, abs(nx*light[0] + ny*light[1] + nz*light[2]))
            # Pixel poly
            pts = [world_to_pixel(proj[i][0], proj[i][1]) for i in face]
            shade = ndotl
            shaded_col = tuple(min(255, max(0, int(c * 255 * (0.45 + 0.55 * shade))))
                                for c in color[:3])
            flat.append((depth, pts, shaded_col))
    # Painter's algorithm — back to front
    flat.sort(key=lambda x: x[0])
    for depth, pts, col in flat:
        try:
            draw.polygon(pts, fill=col, outline=(15, 15, 18))
        except Exception:
            pass
    return img

def measure_body(body_type, scale=1.0, **kwargs):
    _meshes.clear()
    hs.human_figure(name='PV', base_x=0, base_y=0, base_z=0,
                    scale=scale, facing='-Y',
                    body_type=body_type,
                    with_ears=True, with_mouth=True,
                    **kwargs)
    return list(_meshes)

# Render 8 body types in a grid · 2 columns × 4 rows
# Each cell shows front + side
BODY_TYPES = [
    ('male_avg',   {'jacket_color': (0.18, 0.32, 0.55, 1.0),
                    'pants_color':  (0.18, 0.18, 0.22, 1.0)}),
    ('male_tall',  {'jacket_color': (0.32, 0.18, 0.32, 1.0),
                    'pants_color':  (0.32, 0.32, 0.36, 1.0)}),
    ('male_heavy', {'jacket_color': (0.78, 0.74, 0.66, 1.0),
                    'pants_color':  (0.42, 0.30, 0.20, 1.0)}),
    ('female_avg', {'jacket_color': (0.85, 0.42, 0.62, 1.0),
                    'pants_color':  (0.18, 0.32, 0.55, 1.0)}),
    ('female_slim',{'jacket_color': (0.42, 0.65, 0.62, 1.0),
                    'pants_color':  (0.18, 0.18, 0.22, 1.0)}),
    ('teen',       {'jacket_color': (0.85, 0.22, 0.20, 1.0),
                    'pants_color':  (0.18, 0.22, 0.32, 1.0)}),
    ('child',      {'jacket_color': (0.95, 0.85, 0.30, 1.0),
                    'pants_color':  (0.55, 0.32, 0.22, 1.0)}),
    ('elderly',    {'jacket_color': (0.42, 0.42, 0.45, 1.0),
                    'pants_color':  (0.32, 0.30, 0.28, 1.0)}),
]

CELL_W = 360
CELL_H = 640
COLS = 4   # 2 views per body type, so 4 cells = 2 figures
LABEL_H = 24

# Layout: 2 columns of (front, side), 4 rows = 8 figures
rows = 4
panel_w = CELL_W * COLS
panel_h = (CELL_H + LABEL_H) * rows
panel = Image.new('RGB', (panel_w, panel_h), (15, 16, 18))
draw_panel = ImageDraw.Draw(panel)
try:
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
except Exception:
    font = ImageFont.load_default()

for idx, (bt, kw) in enumerate(BODY_TYPES):
    row = idx // 2
    col_grp = idx % 2     # 0 or 1 (left half or right half of row)
    x0 = col_grp * 2 * CELL_W
    y0 = row * (CELL_H + LABEL_H)
    meshes = measure_body(bt, **kw)
    front = render_view(meshes, project_front, CELL_W, CELL_H)
    side = render_view(meshes, project_side, CELL_W, CELL_H)
    panel.paste(front, (x0, y0 + LABEL_H))
    panel.paste(side,  (x0 + CELL_W, y0 + LABEL_H))
    draw_panel.text((x0 + 8, y0 + 4),
                    f"{bt}  ·  front  /  side",
                    fill=(220, 220, 230), font=font)

out_path = '/tmp/human_previews.png'
panel.save(out_path, 'PNG')
print(f"Wrote {out_path}  ({panel.size[0]}x{panel.size[1]})")

# ── HEAD CLOSE-UPS · zoomed crop of just the head region for
# all 8 body_types · single column · front + side
HEAD_CELL_W = 360
HEAD_CELL_H = 360
HEAD_COLS = 4    # 2 views × 4 body_types per row
head_rows = 2    # 8 body_types / 4 = 2 rows
head_panel_w = HEAD_CELL_W * HEAD_COLS
head_panel_h = (HEAD_CELL_H + LABEL_H) * head_rows
head_panel = Image.new('RGB', (head_panel_w, head_panel_h), (15, 16, 18))
head_draw = ImageDraw.Draw(head_panel)
for idx, (bt, kw) in enumerate(BODY_TYPES):
    row = idx // 2
    col_grp = idx % 2
    x0 = col_grp * 2 * HEAD_CELL_W
    y0 = row * (HEAD_CELL_H + LABEL_H)
    meshes = measure_body(bt, **kw)
    # Tighter crop on the head + chin so face features are
    # readable in the close-up panel.
    front = render_view(meshes, project_front,
                        HEAD_CELL_W, HEAD_CELL_H,
                        world_min_x=-0.12, world_max_x=0.12,
                        world_min_y=1.55,  world_max_y=1.85)
    side  = render_view(meshes, project_side,
                        HEAD_CELL_W, HEAD_CELL_H,
                        world_min_x=-0.13, world_max_x=0.13,
                        world_min_y=1.55,  world_max_y=1.85)
    head_panel.paste(front, (x0, y0 + LABEL_H))
    head_panel.paste(side,  (x0 + HEAD_CELL_W, y0 + LABEL_H))
    head_draw.text((x0 + 8, y0 + 4),
                   f"{bt}  ·  HEAD close-up",
                   fill=(220, 220, 230), font=font)
head_panel.save('/tmp/human_heads.png', 'PNG')
print(f"Wrote /tmp/human_heads.png  ({head_panel.size[0]}x{head_panel.size[1]})")
