"""
preview_planar_human.py
══════════════════════════════════════════════════════════════════
Render front + side SVG previews of the planar human base mesh
WITHOUT booting Blender. Stub-imports build_planar_human, walks the
same cross-section + arm data the bpy script uses, projects to 2D,
and writes SVGs.

Run:
    python3 preview_planar_human.py

Output (next to this script):
    preview_planar_human_male_front.svg
    preview_planar_human_male_side.svg
    preview_planar_human_female_front.svg
    preview_planar_human_female_side.svg
"""
import os
import sys
import math

_HERE = os.path.dirname(os.path.abspath(__file__))

# Stub bpy/bmesh so we can import build_planar_human geometry-only:
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
    """Replicate build_body_mesh's vertex generation without bpy."""
    rings = B.cross_sections(profile)
    cx = profile['origin_x']
    out = []
    ring_indices = []
    for label, y, half_w, half_d in rings:
        pts = B._ring_verts(cx, y, 0.0, half_w, half_d)
        if label in ('eye', 'cheekbone', 'nose_tip',
                     'upper_lip', 'lower_lip'):
            pts = B._carve_face(pts, label, y)
        idx0 = len(out)
        out.extend(pts)
        ring_indices.append((label, list(range(idx0, idx0 + B.RING_N))))
    return out, ring_indices, rings


def arm_verts(profile, side):
    """Replicate build_arm_mesh."""
    cx0 = profile['origin_x'] + side * profile['shoulder_w'] / 2 * 0.85
    cx1 = profile['origin_x'] + side * profile['hip_w'] / 2 * 1.15
    arm_y_top = B.CLAV_Y - 0.010
    arm_y_bot = B.THIGH_Y - B.HEAD_H * 0.05
    upper_w = B.HEAD_W * 0.16
    fore_w  = upper_w * profile['arm_taper']
    n_rings = 7
    rings = []
    for i in range(n_rings):
        t = i / (n_rings - 1)
        y = arm_y_top + (arm_y_bot - arm_y_top) * t
        cx = cx0 + (cx1 - cx0) * t
        w = upper_w + (fore_w - upper_w) * t
        rings.append((y, cx, w))
    hand_y = arm_y_bot - 0.060
    rings.append((hand_y, cx1 + side * 0.005, fore_w * 1.05))

    arm_ring_n = 8
    out = []
    ring_idx = []
    for y, cx, w in rings:
        idx0 = len(out)
        for k in range(arm_ring_n):
            ang = 2 * math.pi * k / arm_ring_n
            x = cx + w * math.sin(ang)
            z = w * 0.85 * math.cos(ang)
            out.append((x, y, z))
        ring_idx.append(list(range(idx0, idx0 + arm_ring_n)))
    return out, ring_idx, arm_ring_n


def render_svg(profile, view, body_pts, body_rings,
               arms_pts_l, arms_idx_l, arms_pts_r, arms_idx_r,
               arm_ring_n, landmarks):
    """view = 'front' (X-Y) or 'side' (Z-Y, +Z forward to the right).
    Returns SVG string."""
    if view == 'front':
        project = lambda v: (v[0], v[1])
    else:
        project = lambda v: (v[2], v[1])

    # World bounds (consistent across both figures so we can
    # compare male vs female at the same scale):
    if view == 'front':
        wx0, wx1 = -0.45, 0.45
    else:
        wx0, wx1 = -0.25, 0.25
    wy0, wy1 = -0.05, 1.90

    W, H = 360, 720
    margin = 24
    sx = (W - 2 * margin) / (wx1 - wx0)
    sy = (H - 2 * margin) / (wy1 - wy0)

    def to_screen(p):
        x, y = p
        sx_px = margin + (x - wx0) * sx
        sy_px = H - margin - (y - wy0) * sy
        return sx_px, sy_px

    parts = []
    parts.append(f'<?xml version="1.0" encoding="UTF-8"?>')
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                 f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
                 f'style="background:#1a1a20;font-family:monospace;font-size:9px;">')

    # Title
    title = f"{profile.get('label','?')} — {view.upper()} view"
    parts.append(f'<text x="{margin}" y="{margin-6}" fill="#aaa">{title}</text>')

    # 8-head grid lines + landmark markers
    for k in range(9):
        ly = B.TOTAL_H - k * B.HEAD_H
        if wy0 <= ly <= wy1:
            sy_px = H - margin - (ly - wy0) * sy
            parts.append(
                f'<line x1="{margin}" y1="{sy_px:.1f}" '
                f'x2="{W-margin}" y2="{sy_px:.1f}" '
                f'stroke="#3a3a45" stroke-width="0.5" '
                f'stroke-dasharray="2 3"/>')
            parts.append(
                f'<text x="{W - margin + 2}" y="{sy_px-1:.1f}" '
                f'fill="#5a5a70">{k}H</text>')

    # Centerline
    cx_px = (W - 2 * margin) / 2 + margin if view == 'side' else \
            (-wx0) / (wx1 - wx0) * (W - 2 * margin) + margin
    parts.append(
        f'<line x1="{cx_px:.1f}" y1="{margin}" '
        f'x2="{cx_px:.1f}" y2="{H-margin}" '
        f'stroke="#2a2a32" stroke-width="0.4"/>')

    # ── BODY MESH WIRE ──────────────────────────────────────────
    # Horizontal rings
    for label, ring in body_rings:
        pts2 = [to_screen(project(body_pts[i])) for i in ring]
        # Close the ring
        pts2.append(pts2[0])
        d = 'M ' + ' L '.join(f'{x:.1f},{y:.1f}' for x, y in pts2)
        parts.append(f'<path d="{d}" stroke="#6a8aa8" '
                     f'stroke-width="0.5" fill="none" opacity="0.55"/>')

    # Longitudinal lines between rings (every other vert for clarity)
    for v_i in range(0, B.RING_N, 2):
        pts2 = []
        for label, ring in body_rings:
            pts2.append(to_screen(project(body_pts[ring[v_i]])))
        d = 'M ' + ' L '.join(f'{x:.1f},{y:.1f}' for x, y in pts2)
        parts.append(f'<path d="{d}" stroke="#6a8aa8" '
                     f'stroke-width="0.5" fill="none" opacity="0.65"/>')

    # ── ARMS ───────────────────────────────────────────────────
    for arm_pts, arm_rings in [(arms_pts_l, arms_idx_l),
                                (arms_pts_r, arms_idx_r)]:
        # Rings
        for ring in arm_rings:
            pts2 = [to_screen(project(arm_pts[i])) for i in ring]
            pts2.append(pts2[0])
            d = 'M ' + ' L '.join(f'{x:.1f},{y:.1f}' for x, y in pts2)
            parts.append(f'<path d="{d}" stroke="#a0b8c8" '
                         f'stroke-width="0.5" fill="none" opacity="0.6"/>')
        # Longitudinal
        for v_i in range(0, arm_ring_n, 2):
            pts2 = [to_screen(project(arm_pts[r[v_i]])) for r in arm_rings]
            d = 'M ' + ' L '.join(f'{x:.1f},{y:.1f}' for x, y in pts2)
            parts.append(f'<path d="{d}" stroke="#a0b8c8" '
                         f'stroke-width="0.5" fill="none" opacity="0.65"/>')

    # ── SILHOUETTE OUTLINE (envelope) ──────────────────────────
    # Build the outer envelope by taking, per Y-screen-row, the
    # min and max screen-X across all body+arm projected points.
    all_proj = [project(v) for v in body_pts]
    for ap in (arms_pts_l, arms_pts_r):
        all_proj.extend(project(v) for v in ap)
    screen_pts = [to_screen(p) for p in all_proj]

    # Bin by screen-Y in 4-px bands
    bins = {}
    for sx_px, sy_px in screen_pts:
        bk = int(sy_px // 4)
        bins.setdefault(bk, []).append(sx_px)
    left_edge, right_edge = [], []
    for bk in sorted(bins.keys()):
        ys = bk * 4 + 2
        left_edge.append((min(bins[bk]), ys))
        right_edge.append((max(bins[bk]), ys))
    envelope = left_edge + list(reversed(right_edge))
    d = 'M ' + ' L '.join(f'{x:.1f},{y:.1f}' for x, y in envelope) + ' Z'
    parts.append(f'<path d="{d}" fill="#c8a880" fill-opacity="0.13" '
                 f'stroke="#e0c898" stroke-width="1.2" stroke-opacity="0.55"/>')

    # ── LANDMARK LABELS ────────────────────────────────────────
    for label, ly in landmarks:
        if wy0 <= ly <= wy1:
            sy_px = H - margin - (ly - wy0) * sy
            parts.append(
                f'<line x1="{margin-6}" y1="{sy_px:.1f}" '
                f'x2="{margin}" y2="{sy_px:.1f}" '
                f'stroke="#dd8855" stroke-width="1.2"/>')
            parts.append(
                f'<text x="{margin-10}" y="{sy_px+3:.1f}" '
                f'fill="#dd8855" text-anchor="end">{label}</text>')

    # Y axis label
    parts.append(f'<text x="6" y="{H/2:.1f}" fill="#666" '
                 f'transform="rotate(-90 6 {H/2:.1f})">Y (height, metres)</text>')

    parts.append('</svg>')
    return '\n'.join(parts)


LANDMARKS = [
    ("crown",    B.CROWN_Y),
    ("brow",     B.BROW_Y),
    ("eye",      B.EYE_Y),
    ("nose",     B.NOSE_Y),
    ("mouth",    B.MOUTH_Y),
    ("chin",     B.CHIN_Y),
    ("clav",     B.CLAV_Y),
    ("nipple",   B.NIPPLE_Y),
    ("navel",    B.NAVEL_Y),
    ("crotch",   B.CROTCH_Y),
    ("knee",     B.KNEE_Y),
    ("ankle",    B.ANKLE_Y),
]


def main():
    for body_label in ('male', 'female'):
        profile = dict(B.BODY_TYPES[body_label])
        profile['label'] = body_label
        b_pts, b_rings, _ = body_verts(profile)
        al_pts, al_idx, arn = arm_verts(profile, +1)
        ar_pts, ar_idx, _   = arm_verts(profile, -1)
        for view in ('front', 'side'):
            svg = render_svg(profile, view, b_pts, b_rings,
                              al_pts, al_idx, ar_pts, ar_idx,
                              arn, LANDMARKS)
            out = os.path.join(_HERE,
                f"preview_planar_human_{body_label}_{view}.svg")
            with open(out, 'w') as f:
                f.write(svg)
            print(f"wrote {out}")


if __name__ == "__main__":
    main()
