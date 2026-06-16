"""
preview_planar_human_png.py
══════════════════════════════════════════════════════════════════
Same idea as preview_planar_human.py (SVG), but raster output via
Pillow. Useful when the client doesn't render inline SVGs.

Run:
    python3 preview_planar_human_png.py

Output (next to this script):
    preview_planar_human_male_front.png
    preview_planar_human_male_side.png
    preview_planar_human_female_front.png
    preview_planar_human_female_side.png
"""
import os
import sys
import math
from PIL import Image, ImageDraw

_HERE = os.path.dirname(os.path.abspath(__file__))


class _A:
    def __getattr__(self, k): return _A()
    def __setattr__(self, k, v): pass
    def __getitem__(self, k): return _A()
    def __setitem__(self, k, v): pass
    def __call__(self, *a, **k): return _A()
    def __iter__(self): return iter([])
    def __bool__(self): return True
    def __float__(self): return 0.0
    def __int__(self): return 0
    def __len__(self): return 0
class _B:
    def __getattr__(self, k): return _A()


sys.modules['bpy'] = _B()
sys.modules['bmesh'] = _B()
sys.path.insert(0, _HERE)
import build_planar_human as B


def body_verts(profile):
    rings = B.cross_sections(profile)
    cx = profile['origin_x']
    out, ring_indices = [], []
    for label, y, half_w, half_d in rings:
        pts = B._ring_verts(cx, y, 0.0, half_w, half_d)
        if label in ('eye', 'cheekbone', 'nose_tip',
                     'upper_lip', 'lower_lip'):
            pts = B._carve_face(pts, label, y)
        i0 = len(out)
        out.extend(pts)
        ring_indices.append((label, list(range(i0, i0 + B.RING_N))))
    return out, ring_indices


def arm_verts(profile, side):
    cx0 = profile['origin_x'] + side * profile['shoulder_w'] / 2 * 0.85
    cx1 = profile['origin_x'] + side * profile['hip_w'] / 2 * 1.15
    arm_y_top = B.CLAV_Y - 0.010
    arm_y_bot = B.THIGH_Y - B.HEAD_H * 0.05
    upper_w = B.HEAD_W * 0.16
    fore_w = upper_w * profile['arm_taper']
    nr = 7
    rings = []
    for i in range(nr):
        t = i / (nr - 1)
        rings.append((
            arm_y_top + (arm_y_bot - arm_y_top) * t,
            cx0 + (cx1 - cx0) * t,
            upper_w + (fore_w - upper_w) * t,
        ))
    rings.append((arm_y_bot - 0.060, cx1 + side * 0.005, fore_w * 1.05))
    arn = 8
    out, ring_idx = [], []
    for y, cx, w in rings:
        i0 = len(out)
        for k in range(arn):
            ang = 2 * math.pi * k / arn
            out.append((cx + w * math.sin(ang), y, w * 0.85 * math.cos(ang)))
        ring_idx.append(list(range(i0, i0 + arn)))
    return out, ring_idx, arn


LANDMARKS = [
    ("crown",  B.CROWN_Y),  ("brow",   B.BROW_Y),
    ("eye",    B.EYE_Y),    ("nose",   B.NOSE_Y),
    ("mouth",  B.MOUTH_Y),  ("chin",   B.CHIN_Y),
    ("clav",   B.CLAV_Y),   ("nipple", B.NIPPLE_Y),
    ("navel",  B.NAVEL_Y),  ("crotch", B.CROTCH_Y),
    ("knee",   B.KNEE_Y),   ("ankle",  B.ANKLE_Y),
]


def render_png(profile, view, out_path):
    b_pts, b_rings = body_verts(profile)
    al_pts, al_idx, arn = arm_verts(profile, +1)
    ar_pts, ar_idx, _ = arm_verts(profile, -1)

    if view == 'front':
        project = lambda v: (v[0], v[1])
        wx0, wx1 = -0.45, 0.45
    else:
        project = lambda v: (v[2], v[1])
        wx0, wx1 = -0.25, 0.25
    wy0, wy1 = -0.05, 1.90
    W, H, margin = 360, 720, 28
    sx = (W - 2 * margin) / (wx1 - wx0)
    sy = (H - 2 * margin) / (wy1 - wy0)

    def to_screen(p):
        x, y = p
        return (margin + (x - wx0) * sx, H - margin - (y - wy0) * sy)

    img = Image.new('RGB', (W, H), (26, 26, 32))
    d = ImageDraw.Draw(img)
    d.text((margin, 6), f"{profile['label']} — {view.upper()}",
           fill=(180, 180, 180))

    # 8H grid + labels
    for k in range(9):
        ly = B.TOTAL_H - k * B.HEAD_H
        if wy0 <= ly <= wy1:
            ypx = H - margin - (ly - wy0) * sy
            for dx in range(margin, W - margin, 6):
                d.point((dx, int(ypx)), fill=(58, 58, 69))
            d.text((W - margin + 2, ypx - 6), f"{k}H",
                   fill=(90, 90, 112))

    # Centerline (dotted)
    cxpx = margin + (-wx0) * sx
    for ypx in range(margin, H - margin, 4):
        d.point((int(cxpx), ypx), fill=(42, 42, 50))

    # Silhouette envelope (max extent per Y row)
    all_proj = [project(v) for v in b_pts]
    for ap in (al_pts, ar_pts):
        all_proj.extend(project(v) for v in ap)
    screen_pts = [to_screen(p) for p in all_proj]
    bins = {}
    for sxp, syp in screen_pts:
        bk = int(syp // 3)
        bins.setdefault(bk, []).append(sxp)
    left, right = [], []
    for bk in sorted(bins.keys()):
        ys = bk * 3 + 1.5
        left.append((min(bins[bk]), ys))
        right.append((max(bins[bk]), ys))
    envelope = left + list(reversed(right))
    if len(envelope) > 2:
        d.polygon(envelope, fill=(180, 150, 110), outline=(224, 200, 150))

    # Body rings
    for label, ring in b_rings:
        pts2 = [to_screen(project(b_pts[i])) for i in ring]
        pts2.append(pts2[0])
        d.line(pts2, fill=(106, 138, 168), width=1)

    # Body longitudinals
    for vi in range(0, B.RING_N, 2):
        pts2 = [to_screen(project(b_pts[r[vi]])) for _, r in b_rings]
        d.line(pts2, fill=(106, 138, 168), width=1)

    # Arms
    for ap, ai in [(al_pts, al_idx), (ar_pts, ar_idx)]:
        for r in ai:
            pts2 = [to_screen(project(ap[i])) for i in r]
            pts2.append(pts2[0])
            d.line(pts2, fill=(160, 184, 200), width=1)
        for vi in range(0, arn, 2):
            pts2 = [to_screen(project(ap[r[vi]])) for r in ai]
            d.line(pts2, fill=(160, 184, 200), width=1)

    # Landmark callouts
    for label, ly in LANDMARKS:
        if wy0 <= ly <= wy1:
            ypx = H - margin - (ly - wy0) * sy
            d.line([(margin - 8, ypx), (margin, ypx)],
                   fill=(221, 136, 85), width=2)
            d.text((4, ypx - 5), label, fill=(221, 136, 85))

    img.save(out_path)
    print(f"wrote {out_path}")


def main():
    for body_label in ('male', 'female'):
        profile = dict(B.BODY_TYPES[body_label])
        profile['label'] = body_label
        for view in ('front', 'side'):
            out = os.path.join(
                _HERE, f"preview_planar_human_{body_label}_{view}.png")
            render_png(profile, view, out)


if __name__ == "__main__":
    main()
