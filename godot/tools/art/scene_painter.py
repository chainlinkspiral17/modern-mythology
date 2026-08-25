#!/usr/bin/env python3
"""
scene_painter.py — best-effort PROCEDURAL painted sources.

The placeholder half of the hybrid art pipeline: paints a high-res,
atmospheric, painterly source (gradient skies, layered atmospheric-
perspective silhouettes, soft-blurred edges, value-noise texture, glow,
fog, vignette) — far richer than the old flat-vector HeroImage look —
then presses it through svga_quantize.py (the era-filter) to land the
early-90s 256-color Sierra/LucasArts SVGA register.

These are PLACEHOLDERS, dropped in until AI-painted sources (scene_
render.py) replace them through the same era-filter. The HTML studio
(art_studio.html) is the front end for generating and replacing them.

Usage:
    python3 scene_painter.py SCENE_ID out.png            # era-filtered final
    python3 scene_painter.py SCENE_ID out.png --source src.png --preview 3
    python3 scene_painter.py --list
"""
import argparse, sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import svga_quantize

RGB = tuple


# ── painterly primitives (operate on float32 HxWx3, 0..255) ──────────

def sky(H, W, stops):
    # stops: [(t0,(r,g,b)), ...] top(0) -> bottom(1), vertical gradient
    ys = np.linspace(0, 1, H)
    out = np.zeros((H, W, 3), np.float32)
    ts = [s[0] for s in stops]
    cs = [np.array(s[1], np.float32) for s in stops]
    for i in range(H):
        t = ys[i]
        # find segment
        k = 0
        while k < len(ts) - 2 and t > ts[k + 1]:
            k += 1
        span = max(1e-4, ts[k + 1] - ts[k])
        f = np.clip((t - ts[k]) / span, 0, 1)
        out[i, :, :] = cs[k] * (1 - f) + cs[k + 1] * f
    return out


def _mask(H, W, pts, blur=0.0):
    im = Image.new("L", (W, H), 0)
    ImageDraw.Draw(im).polygon([(float(x), float(y)) for x, y in pts], fill=255)
    if blur > 0:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(im, np.float32) / 255.0


def fill_poly(arr, pts, color, blur=0.0, opacity=1.0):
    H, W, _ = arr.shape
    m = _mask(H, W, pts, blur)[:, :, None] * opacity
    arr[:] = arr * (1 - m) + np.array(color, np.float32) * m


def grad_poly(arr, pts, top, bottom, blur=0.0, opacity=1.0):
    """Fill a polygon with a VERTICAL gradient — the cheapest unit
    of 'painted': every large surface carries light, top to base."""
    H, W, _ = arr.shape
    m = _mask(H, W, pts, blur)
    ys = [p[1] for p in pts]
    y0, y1 = max(0, int(min(ys))), min(H - 1, int(max(ys)))
    g = np.zeros((H, 1), np.float32)
    if y1 > y0:
        g[y0:y1 + 1, 0] = np.linspace(0, 1, y1 - y0 + 1)
        g[y1 + 1:, 0] = 1.0
    col = (np.array(top, np.float32)[None, None, :] * (1 - g[:, :, None]) +
           np.array(bottom, np.float32)[None, None, :] * g[:, :, None])
    mm = (m * opacity)[:, :, None]
    arr[:] = arr * (1 - mm) + col * mm


def drop_shadow(arr, pts, blur=4.0, opacity=0.35):
    """Soft dark pool under an object — what glues shapes to ground."""
    fill_poly(arr, pts, (10, 12, 14), blur=blur, opacity=opacity)


def noise(H, W, scale=16, seed=1, blur=1.5):
    rng = np.random.default_rng(seed)
    small = rng.random((max(2, H // scale), max(2, W // scale))).astype(np.float32)
    im = Image.fromarray((small * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    if blur > 0:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(im, np.float32) / 255.0


def tex(arr, region_mask, amt, seed, scale=10):
    # modulate brightness by smooth noise within a mask (painterly grain)
    H, W, _ = arr.shape
    n = noise(H, W, scale, seed)[:, :, None]
    arr[:] = arr + (n - 0.5) * amt * region_mask[:, :, None]


def glow(arr, cx, cy, r, color, strength=0.6):
    H, W, _ = arr.shape
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    f = np.clip(1 - d, 0, 1) ** 2
    arr[:] = arr + np.array(color, np.float32) * (f[:, :, None] * strength)


def vignette(arr, amount=0.35):
    H, W, _ = arr.shape
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    f = np.clip(d - 0.5, 0, 1)
    arr[:] = arr * (1 - f[:, :, None] * amount)


def spruce(arr, x, base, h, color, blur=0.6):
    w = max(6, h * 0.30)
    pts = [(x, base - h)]
    steps = 5
    for i in range(steps):
        yy = base - h + (h * (i + 1) / steps)
        wid = w * (i + 1) / steps
        pts.append((x + wid, yy - h * 0.04))
        pts.append((x + wid * 0.5, yy))
    pts.append((x, base))
    for i in range(steps - 1, -1, -1):
        yy = base - h + (h * (i + 1) / steps)
        wid = w * (i + 1) / steps
        pts.append((x - wid * 0.5, yy))
        pts.append((x - wid, yy - h * 0.04))
    fill_poly(arr, pts, color, blur=blur)


def sprucerow(arr, x0, x1, base, color, seed=1, blur=0.6):
    rng = np.random.default_rng(seed)
    x = x0
    while x < x1:
        h = rng.integers(int((x1 - x0) * 0.06), int((x1 - x0) * 0.16) + 6)
        spruce(arr, x, base + rng.integers(-4, 5), h, color, blur)
        x += rng.integers(int(h * 0.35), int(h * 0.7) + 3)


def clamp(arr):
    return np.clip(arr, 0, 255).astype(np.uint8)


# ── colors ───────────────────────────────────────────────────────────
C = dict(
    fog_hi=(150, 162, 170), fog_lo=(214, 206, 188), peach=(224, 196, 168),
    sea_hi=(64, 96, 112), sea_lo=(44, 70, 88), fir=(38, 58, 44),
    fir_far=(120, 140, 138), fir_mid=(74, 100, 92), basalt=(40, 46, 56),
    basalt_lit=(96, 104, 112), foam=(224, 232, 232), rust=(150, 84, 54),
    wood=(150, 108, 66), window=(232, 196, 108), warm=(240, 190, 96),
    ink=(28, 30, 34), gold=(216, 176, 80), night=(24, 30, 42),
    lamp=(232, 190, 120),
)


# ── scenes ───────────────────────────────────────────────────────────

def salmonberry_title(H, W):
    arr = sky(H, W, [(0.0, C["fog_hi"]), (0.55, (196, 194, 184)), (0.72, C["peach"]), (1.0, C["fog_lo"])])
    hz = int(H * 0.62)
    # soft sun/fog glow low behind the stacks
    glow(arr, W * 0.44, hz - 10, W * 0.42, (255, 226, 180), 0.5)
    # far headland (right), blurred + atmospheric
    fill_poly(arr, [(W * 0.55, hz), (W * 0.7, hz - H * 0.16), (W * 0.9, hz - H * 0.10), (W, hz - H * 0.13), (W, hz), ], C["fir_far"], blur=5)
    # mid headland
    fill_poly(arr, [(W * 0.62, hz), (W * 0.78, hz - H * 0.24), (W * 0.92, hz - H * 0.15), (W, hz - H * 0.19), (W, hz), ], C["fir_mid"], blur=2.5)
    sprucerow(arr, int(W * 0.72), int(W * 0.99), hz - 4, C["fir_mid"], seed=7, blur=1.5)
    # sea
    sea = sky(H, W, [(0.0, C["sea_hi"]), (1.0, C["sea_lo"])])
    seam = np.zeros((H, W, 1), np.float32); seam[hz:, :, 0] = 1.0
    arr[:] = arr * (1 - seam) + sea * seam
    tex(arr, seam[:, :, 0], 26, seed=3, scale=6)
    # sun glitter on the water
    glow(arr, W * 0.44, hz + 20, W * 0.3, (255, 236, 200), 0.28)
    # sea stacks with a lit edge
    for (cx, sh, sw) in [(W * 0.40, H * 0.30, W * 0.05), (W * 0.50, H * 0.22, W * 0.035), (W * 0.55, H * 0.13, W * 0.025)]:
        base = hz + 8
        pts = [(cx - sw, base), (cx - sw * 0.7, base - sh * 0.7), (cx - sw * 0.3, base - sh), (cx + sw * 0.3, base - sh), (cx + sw * 0.7, base - sh * 0.72), (cx + sw, base)]
        fill_poly(arr, pts, C["basalt"], blur=1.0)
        fill_poly(arr, [(cx + sw * 0.1, base), (cx + sw * 0.2, base - sh * 0.9), (cx + sw * 0.55, base - sh * 0.7), (cx + sw, base)], C["basalt_lit"], blur=1.2, opacity=0.6)
    # surf line
    fill_poly(arr, [(0, hz + 6), (W, hz + 2), (W, hz + 14), (0, hz + 20)], C["foam"], blur=3, opacity=0.5)
    # near headland (left), steep, dark, sharp, with spruce —
    # GRADED so the slope carries light, plus grain.
    head_pts = [(0, H), (0, H * 0.30), (W * 0.14, H * 0.36), (W * 0.26, H * 0.52), (W * 0.30, H)]
    grad_poly(arr, head_pts, (66, 92, 70), (26, 40, 32), blur=1.0)
    tex(arr, _mask(H, W, head_pts), 22, seed=14, scale=7)
    # sun-side rim on the headland's sea edge
    fill_poly(arr, [(W * 0.14, H * 0.36), (W * 0.26, H * 0.52), (W * 0.245, H * 0.545), (W * 0.132, H * 0.375)], (120, 140, 104), blur=1.5, opacity=0.7)
    sprucerow(arr, int(W * 0.02), int(W * 0.28), int(H * 0.40), C["fir"], seed=3, blur=1.0)
    # the cannery on pilings + the house, small, at the base of the headland
    dcx = int(W * 0.30)
    fill_poly(arr, [(dcx, hz + 4), (dcx + W * 0.14, hz + 4), (dcx + W * 0.14, hz + 22), (dcx, hz + 22)], C["rust"], blur=0.5)
    for i in range(6):
        px = dcx + int(W * 0.02) + i * int(W * 0.02)
        fill_poly(arr, [(px, hz + 22), (px + 3, hz + 22), (px + 3, hz + 48), (px, hz + 48)], C["ink"], blur=0)
    hx = int(W * 0.33)
    # ground the house: a grass shelf and its shadow first
    fill_poly(arr, [(hx - W * 0.03, H * 0.9), (hx + W * 0.13, H * 0.9), (hx + W * 0.15, H), (hx - W * 0.05, H)], (52, 68, 50), blur=2)
    drop_shadow(arr, [(hx - 6, H * 0.895), (hx + W * 0.09 + 8, H * 0.895), (hx + W * 0.09 + 14, H * 0.915), (hx - 12, H * 0.915)], blur=3, opacity=0.4)
    grad_poly(arr, [(hx, H * 0.78), (hx + W * 0.09, H * 0.78), (hx + W * 0.09, H * 0.90), (hx, H * 0.90)], (176, 132, 84), (108, 76, 46), blur=0.5)
    # clapboard hint: three darker courses
    for ci in range(3):
        yy = H * (0.81 + ci * 0.03)
        fill_poly(arr, [(hx, yy), (hx + W * 0.09, yy), (hx + W * 0.09, yy + 1.5), (hx, yy + 1.5)], (90, 64, 40), blur=0.3, opacity=0.5)
    grad_poly(arr, [(hx - 4, H * 0.78), (hx + W * 0.045, H * 0.72), (hx + W * 0.09 + 4, H * 0.78)], (196, 120, 78), (128, 70, 46), blur=0.5)
    # window with frame + sill, then the glow
    fill_poly(arr, [(hx + W * 0.025, H * 0.815), (hx + W * 0.055, H * 0.815), (hx + W * 0.055, H * 0.865), (hx + W * 0.025, H * 0.865)], (70, 50, 32), blur=0.3)
    fill_poly(arr, [(hx + W * 0.028, H * 0.82), (hx + W * 0.052, H * 0.82), (hx + W * 0.052, H * 0.86), (hx + W * 0.028, H * 0.86)], C["window"], blur=0.4)
    glow(arr, hx + W * 0.04, H * 0.84, 14, C["window"], 0.5)
    # fog veil in the mid-distance
    veil = np.zeros((H, W, 1), np.float32)
    veil[int(hz - H * 0.06):hz + 10, :, 0] = 1.0
    veil = np.asarray(Image.fromarray((veil[:, :, 0] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(20)), np.float32)[:, :, None] / 255.0
    arr[:] = arr * (1 - veil * 0.35) + np.array(C["fog_lo"], np.float32) * (veil * 0.35)
    # gulls
    _gulls(arr, [(W * 0.6, H * 0.22), (W * 0.66, H * 0.27), (W * 0.52, H * 0.18)])
    vignette(arr, 0.30)
    return arr


def salmonberry_song(H, W):
    arr = sky(H, W, [(0.0, C["night"]), (1.0, (16, 20, 28))])
    # warm room glow
    glow(arr, W * 0.32, H * 0.55, W * 0.5, C["lamp"], 0.45)
    # the window frame + warm pane
    fill_poly(arr, [(W * 0.14, H * 0.28), (W * 0.5, H * 0.28), (W * 0.5, H * 0.9), (W * 0.14, H * 0.9)], C["wood"], blur=1)
    fill_poly(arr, [(W * 0.17, H * 0.33), (W * 0.47, H * 0.33), (W * 0.47, H * 0.86), (W * 0.17, H * 0.86)], C["window"], blur=2)
    tex(arr, _mask(H, W, [(W * 0.17, H * 0.33), (W * 0.47, H * 0.33), (W * 0.47, H * 0.86), (W * 0.17, H * 0.86)]), 24, seed=5, scale=8)
    # the grandmother, a soft silhouette at the window
    fill_poly(arr, [(W * 0.27, H * 0.5), (W * 0.37, H * 0.5), (W * 0.37, H * 0.86), (W * 0.27, H * 0.86)], (60, 44, 40), blur=2)
    glow(arr, W * 0.32, H * 0.47, W * 0.05, (40, 30, 28), 0.9)
    # the melody, notes rising out into the dark
    rng = np.random.default_rng(2)
    for i in range(7):
        nx = W * (0.52 + i * 0.06); ny = H * (0.55 - i * 0.05)
        glow(arr, nx, ny, W * 0.02, C["gold"], 0.7)
    vignette(arr, 0.5)
    return arr


def salmonberry_coast(H, W):
    # a generic coast landscape (base for hands/leaver etc.)
    arr = sky(H, W, [(0.0, C["fog_hi"]), (0.6, (200, 198, 188)), (1.0, C["fog_lo"])])
    hz = int(H * 0.58)
    glow(arr, W * 0.7, hz - 20, W * 0.4, (255, 228, 188), 0.4)
    fill_poly(arr, [(W * 0.6, hz), (W * 0.78, hz - H * 0.3), (W, hz - H * 0.22), (W, hz)], C["fir_mid"], blur=3)
    fill_poly(arr, [(W * 0.72, H), (W * 0.72, hz - H * 0.34), (W * 0.9, hz - H * 0.2), (W, hz - H * 0.1), (W, H)], C["fir"], blur=1)
    sprucerow(arr, int(W * 0.74), int(W * 0.99), hz - H * 0.30, C["fir"], seed=5, blur=1.2)
    sea = sky(H, W, [(0.0, C["sea_hi"]), (1.0, C["sea_lo"])])
    seam = np.zeros((H, W, 1), np.float32); seam[hz:, :, 0] = 1.0
    arr[:] = arr * (1 - seam) + sea * seam
    tex(arr, seam[:, :, 0], 24, seed=4, scale=6)
    for (cx, sh, sw) in [(W * 0.18, H * 0.26, W * 0.045), (W * 0.26, H * 0.16, W * 0.03)]:
        base = hz + 8
        fill_poly(arr, [(cx - sw, base), (cx - sw * 0.4, base - sh), (cx + sw * 0.4, base - sh), (cx + sw, base)], C["basalt"], blur=1)
    fill_poly(arr, [(0, hz + 6), (W, hz + 2), (W, hz + 16), (0, hz + 22)], C["foam"], blur=3, opacity=0.5)
    _gulls(arr, [(W * 0.4, H * 0.2), (W * 0.46, H * 0.24)])
    vignette(arr, 0.3)
    return arr


def _gulls(arr, pts):
    for (x, y) in pts:
        for dx in (-1, 1):
            fill_poly(arr, [(x, y), (x + dx * 9, y - 5), (x + dx * 10, y - 4), (x + dx * 2, y + 1)], C["foam"], blur=0.4, opacity=0.9)


def salmonberry_town(H, W):
    """Main street, 1963, seen up the hill toward the water — false-
    front buildings receding left, wet street holding the sky, the
    sea a pale band at the street's end."""
    arr = sky(H, W, [(0.0, C["fog_hi"]), (0.5, (198, 196, 186)), (1.0, C["fog_lo"])])
    hz = int(H * 0.52)
    # spruce hill behind town
    fill_poly(arr, [(0, hz), (W * 0.3, hz - H * 0.10), (W * 0.7, hz - H * 0.07), (W, hz - H * 0.12), (W, hz)], C["fir_mid"], blur=3)
    sprucerow(arr, 0, W, hz - H * 0.06, C["fir_mid"], seed=11, blur=2)
    # the sea band at the end of the street
    fill_poly(arr, [(W * 0.40, hz - H * 0.02), (W * 0.60, hz - H * 0.02), (W * 0.60, hz + H * 0.055), (W * 0.40, hz + H * 0.055)], C["sea_hi"], blur=2)
    fill_poly(arr, [(W * 0.40, hz + H * 0.028), (W * 0.60, hz + H * 0.024), (W * 0.60, hz + H * 0.040), (W * 0.40, hz + H * 0.046)], C["foam"], blur=1.5, opacity=0.5)
    # wet street: a trapezoid of sky-colored asphalt
    grad_poly(arr, [(W * 0.42, hz + H * 0.05), (W * 0.58, hz + H * 0.05), (W * 0.86, H), (W * 0.10, H)], (148, 150, 154), (104, 106, 112), blur=1)
    tex(arr, _mask(H, W, [(W * 0.42, hz + H * 0.05), (W * 0.58, hz + H * 0.05), (W * 0.86, H), (W * 0.10, H)]), 12, seed=64, scale=10)
    drop_shadow(arr, [(W * 0.10, H), (W * 0.30, hz + H * 0.06), (W * 0.34, hz + H * 0.07), (W * 0.16, H)], blur=4, opacity=0.25)
    fill_poly(arr, [(W * 0.47, hz + H * 0.05), (W * 0.53, hz + H * 0.05), (W * 0.62, H), (W * 0.36, H)], (170, 174, 180), blur=3, opacity=0.3)
    # false-front row, LEFT side receding
    # nearest = leftmost = TALLEST; the row recedes toward the
    # street's end (first render read inverted: near fronts were
    # the shortest and the street vanished behind them).
    xs = [(0.00, 0.42, 0.26), (0.175, 0.30, 0.40), (0.30, 0.22, 0.48), (0.385, 0.15, 0.525)]
    cols = [((190, 142, 92), (118, 84, 52)), ((186, 108, 70), (112, 62, 42)),
            ((198, 184, 152), (128, 116, 90)), ((176, 130, 84), (108, 78, 48))]
    for i, (fx, fw, ft) in enumerate(xs):
        x0, x1 = W * fx, W * (fx + fw * 0.42)
        top = H * ft
        ctop, cbot = cols[i % 4]
        grad_poly(arr, [(x0, H), (x0, top), (x1, top + H * 0.02), (x1, H)], ctop, cbot, blur=0.8)
        tex(arr, _mask(H, W, [(x0, H), (x0, top), (x1, top + H * 0.02), (x1, H)]), 14, seed=60 + i, scale=6)
        # parapet cap + its cast shadow band
        fill_poly(arr, [(x0, top), (x1, top + H * 0.02), (x1, top + H * 0.035), (x0, top + H * 0.015)], (232, 226, 210), blur=0.4, opacity=0.8)
        fill_poly(arr, [(x0, top + H * 0.015), (x1, top + H * 0.035), (x1, top + H * 0.06), (x0, top + H * 0.045)], C["ink"], blur=1.0, opacity=0.4)
        # framed windows with sills, warm panes
        for wi in range(2):
            wx0 = x0 + (x1 - x0) * (0.2 + wi * 0.4)
            ww = W * 0.022
            fill_poly(arr, [(wx0 - 2, top + H * 0.115), (wx0 + ww + 2, top + H * 0.115), (wx0 + ww + 2, top + H * 0.205), (wx0 - 2, top + H * 0.205)], (64, 48, 34), blur=0.3)
            grad_poly(arr, [(wx0, top + H * 0.12), (wx0 + ww, top + H * 0.12), (wx0 + ww, top + H * 0.2), (wx0, top + H * 0.2)], (250, 220, 140), (200, 152, 84), blur=0.4)
            fill_poly(arr, [(wx0 - 3, top + H * 0.205), (wx0 + ww + 3, top + H * 0.205), (wx0 + ww + 3, top + H * 0.213), (wx0 - 3, top + H * 0.213)], (220, 210, 190), blur=0.3, opacity=0.7)
        # storefront: awning stripe + doorway on the two nearest
        if i < 2:
            fill_poly(arr, [(x0 + 4, H * 0.80), (x1 - 4, H * 0.80), (x1 - 10, H * 0.855), (x0 + 10, H * 0.855)], ((150, 60, 48) if i == 0 else (58, 84, 96)), blur=0.6)
            fill_poly(arr, [(x0 + (x1 - x0) * 0.4, H * 0.87), (x0 + (x1 - x0) * 0.62, H * 0.87), (x0 + (x1 - x0) * 0.62, H), (x0 + (x1 - x0) * 0.4, H)], (46, 34, 26), blur=0.4)
    glow(arr, W * 0.2, H * 0.7, W * 0.06, C["window"], 0.35)
    # RIGHT side: two nearer fronts, graded + textured
    for i, (fx, fw, ft) in enumerate([(0.62, 0.14, 0.50), (0.74, 0.45, 0.30)]):
        x0, x1 = W * fx, min(W, W * (fx + fw))
        top = H * ft
        ctop, cbot = ((186, 108, 70), (100, 56, 38)) if i == 0 else ((190, 142, 92), (104, 74, 46))
        grad_poly(arr, [(x0, H), (x0, top + H * 0.02), (x1, top), (x1, H)], ctop, cbot, blur=0.8)
        tex(arr, _mask(H, W, [(x0, H), (x0, top + H * 0.02), (x1, top), (x1, H)]), 16, seed=70 + i, scale=6)
        fill_poly(arr, [(x0, top + H * 0.02), (x1, top), (x1, top + H * 0.018), (x0, top + H * 0.038)], (232, 226, 210), blur=0.4, opacity=0.75)
        wx0 = x0 + (x1 - x0) * 0.3; wx1 = x0 + (x1 - x0) * 0.5
        fill_poly(arr, [(wx0 - 3, top + H * 0.135), (wx1 + 3, top + H * 0.135), (wx1 + 3, top + H * 0.245), (wx0 - 3, top + H * 0.245)], (64, 48, 34), blur=0.3)
        grad_poly(arr, [(wx0, top + H * 0.14), (wx1, top + H * 0.14), (wx1, top + H * 0.24), (wx0, top + H * 0.24)], (250, 220, 140), (198, 148, 82), blur=0.5)
    # cross-street breaks: shadow bands where the block lines cross
    # (they kill the vertical-waterfall read of the wet street)
    for by2, sp in ((0.66, 0.30), (0.78, 0.22), (0.90, 0.14)):
        x_l = W * (0.5 - sp); x_r = W * (0.5 + sp)
        fill_poly(arr, [(x_l, H * by2), (x_r, H * by2), (x_r, H * by2 + 3), (x_l, H * by2 + 3)], (70, 72, 78), blur=1.5, opacity=0.5)
    # power poles down the left walk, wires sagging
    for i, px in enumerate([0.40, 0.31, 0.20, 0.06]):
        ph = H * (0.10 + i * 0.05)
        fill_poly(arr, [(W * px, H * 0.56 - 2), (W * px + 3 + i, H * 0.56), (W * px + 3 + i, H * 0.56 + ph), (W * px, H * 0.56 + ph)], C["ink"], blur=0.4)
    # a pickup parked, small, mid-left
    drop_shadow(arr, [(W * 0.295, H * 0.868), (W * 0.425, H * 0.868), (W * 0.43, H * 0.885), (W * 0.29, H * 0.885)], blur=3, opacity=0.45)
    grad_poly(arr, [(W * 0.30, H * 0.80), (W * 0.42, H * 0.80), (W * 0.42, H * 0.87), (W * 0.30, H * 0.87)], (140, 84, 64), (76, 46, 38), blur=0.8)
    grad_poly(arr, [(W * 0.33, H * 0.76), (W * 0.40, H * 0.76), (W * 0.40, H * 0.80), (W * 0.33, H * 0.80)], (150, 92, 70), (96, 60, 48), blur=0.8)
    fill_poly(arr, [(W * 0.335, H * 0.765), (W * 0.395, H * 0.765), (W * 0.39, H * 0.79), (W * 0.34, H * 0.79)], (188, 198, 204), blur=0.5, opacity=0.85)
    for wxi in (0.315, 0.40):
        fill_poly(arr, [(W * wxi, H * 0.87), (W * (wxi + 0.012), H * 0.87), (W * (wxi + 0.012), H * 0.885), (W * wxi, H * 0.885)], (30, 28, 28), blur=0.4)
    _gulls(arr, [(W * 0.5, H * 0.3), (W * 0.55, H * 0.34)])
    vignette(arr, 0.32)
    return arr


def salmonberry_house(H, W):
    """Vovo's house on the headland: rust roof, lit kitchen window,
    the laundry line holding the wind, the path down."""
    arr = sky(H, W, [(0.0, C["fog_hi"]), (0.5, C["peach"]), (1.0, C["fog_lo"])])
    hz = int(H * 0.66)
    glow(arr, W * 0.75, hz - 30, W * 0.4, (255, 228, 184), 0.45)
    sea = sky(H, W, [(0.0, C["sea_hi"]), (1.0, C["sea_lo"])])
    seam = np.zeros((H, W, 1), np.float32); seam[hz:, :, 0] = 1.0
    arr[:] = arr * (1 - seam) + sea * seam
    tex(arr, seam[:, :, 0], 22, seed=9, scale=6)
    # the headland: a dark grass wedge over the water
    fill_poly(arr, [(0, H), (0, H * 0.42), (W * 0.3, H * 0.48), (W * 0.62, H * 0.58), (W * 0.75, H), ], (58, 74, 52), blur=1.2)
    tex(arr, _mask(H, W, [(0, H), (0, H * 0.42), (W * 0.3, H * 0.48), (W * 0.62, H * 0.58), (W * 0.75, H)]), 20, seed=12, scale=9)
    # the house: gable end toward us, rust roof, lit window
    hx, hy = W * 0.22, H * 0.44
    fill_poly(arr, [(hx, hy + H * 0.16), (hx + W * 0.16, hy + H * 0.16), (hx + W * 0.16, hy + H * 0.02), (hx + W * 0.08, hy - H * 0.05), (hx, hy + H * 0.02)], C["wood"], blur=0.6)
    fill_poly(arr, [(hx - W * 0.008, hy + H * 0.025), (hx + W * 0.08, hy - H * 0.06), (hx + W * 0.168, hy + H * 0.025), (hx + W * 0.16, hy + H * 0.04), (hx + W * 0.08, hy - H * 0.035), (hx + W * 0.008, hy + H * 0.04)], C["rust"], blur=0.6)
    fill_poly(arr, [(hx + W * 0.035, hy + H * 0.05), (hx + W * 0.065, hy + H * 0.05), (hx + W * 0.065, hy + H * 0.1), (hx + W * 0.035, hy + H * 0.1)], C["window"], blur=0.8)
    glow(arr, hx + W * 0.05, hy + H * 0.075, 18, C["window"], 0.6)
    fill_poly(arr, [(hx + W * 0.1, hy + H * 0.06), (hx + W * 0.125, hy + H * 0.06), (hx + W * 0.125, hy + H * 0.16), (hx + W * 0.1, hy + H * 0.16)], C["ink"], blur=0.5, opacity=0.7)
    # chimney + smoke drift
    fill_poly(arr, [(hx + W * 0.115, hy - H * 0.04), (hx + W * 0.135, hy - H * 0.04), (hx + W * 0.135, hy - H * 0.10), (hx + W * 0.115, hy - H * 0.10)], C["basalt"], blur=0.4)
    for i in range(4):
        glow(arr, hx + W * 0.125 + i * 12, hy - H * 0.12 - i * 10, 10 + i * 5, (220, 220, 216), 0.10)
    # laundry line: two posts, sagging line, three sheets in the wind
    lx0, lx1 = hx + W * 0.20, hx + W * 0.42
    ly = hy + H * 0.10
    for lx in (lx0, lx1):
        fill_poly(arr, [(lx, ly + H * 0.06), (lx + 3, ly + H * 0.06), (lx + 3, ly - H * 0.04), (lx, ly - H * 0.04)], C["wood"], blur=0.3)
    for i, sx in enumerate([0.25, 0.30, 0.36]):
        sx0 = hx + W * sx
        fill_poly(arr, [(sx0, ly - H * 0.028), (sx0 + W * 0.035, ly - H * 0.024), (sx0 + W * 0.045, ly + H * 0.035), (sx0 + W * 0.008, ly + H * 0.04)], C["foam"], blur=1.0, opacity=0.92)
    # the path down, pale, switchbacked
    fill_poly(arr, [(hx + W * 0.07, hy + H * 0.16), (hx + W * 0.09, hy + H * 0.16), (W * 0.5, H * 0.9), (W * 0.42, H)], (150, 138, 112), blur=2, opacity=0.7)
    sprucerow(arr, int(W * 0.8), W, int(H * 0.6), C["fir"], seed=8, blur=1.0)
    _gulls(arr, [(W * 0.62, H * 0.25)])
    vignette(arr, 0.3)
    return arr


def salmonberry_store(H, W):
    """The general store interior: shelf walls in lamp warmth, the
    counter, the fogged front window with the street beyond."""
    arr = sky(H, W, [(0.0, (44, 36, 30)), (1.0, (30, 24, 20))])
    # the front window, fog-bright, street shapes ghosted in it
    fill_poly(arr, [(W * 0.36, H * 0.12), (W * 0.64, H * 0.12), (W * 0.64, H * 0.62), (W * 0.36, H * 0.62)], (196, 198, 192), blur=1.5)
    fill_poly(arr, [(W * 0.42, H * 0.3), (W * 0.52, H * 0.26), (W * 0.52, H * 0.62), (W * 0.42, H * 0.62)], C["fir_far"], blur=3, opacity=0.5)
    fill_poly(arr, [(W * 0.49, H * 0.12), (W * 0.51, H * 0.12), (W * 0.51, H * 0.62), (W * 0.49, H * 0.62)], (60, 48, 38), blur=0.5)
    fill_poly(arr, [(W * 0.36, H * 0.36), (W * 0.64, H * 0.36), (W * 0.64, H * 0.385), (W * 0.36, H * 0.385)], (60, 48, 38), blur=0.5)
    # shelf walls, left and right, receding: bands of goods
    rng = np.random.default_rng(21)
    for side, x0f, x1f in ((0, 0.02, 0.30), (1, 0.70, 0.98)):
        for row in range(4):
            ry = H * (0.2 + row * 0.16)
            fill_poly(arr, [(W * x0f, ry), (W * x1f, ry + (H * 0.02 if side else -H * 0.02)), (W * x1f, ry + H * 0.035), (W * x0f, ry + H * 0.035)], (70, 54, 40), blur=0.6)
            x = x0f + 0.015
            while x < x1f - 0.02:
                wgt = rng.uniform(0.015, 0.03)
                col = [(150, 84, 54), (172, 156, 118), (90, 110, 84), (190, 170, 120), (120, 70, 52)][rng.integers(0, 5)]
                fill_poly(arr, [(W * x, ry - H * rng.uniform(0.04, 0.075)), (W * (x + wgt), ry - H * rng.uniform(0.04, 0.075)), (W * (x + wgt), ry), (W * x, ry)], col, blur=0.5)
                x += wgt + 0.006
    # two hanging lamps, warm pools
    for lx in (0.25, 0.75):
        fill_poly(arr, [(W * lx - 2, 0), (W * lx + 2, 0), (W * lx + 2, H * 0.14), (W * lx - 2, H * 0.14)], C["ink"], blur=0.3)
        fill_poly(arr, [(W * lx - W * 0.03, H * 0.14), (W * lx + W * 0.03, H * 0.14), (W * lx + W * 0.015, H * 0.18), (W * lx - W * 0.015, H * 0.18)], (60, 50, 40), blur=0.5)
        glow(arr, W * lx, H * 0.22, W * 0.13, C["lamp"], 0.55)
    # the counter, front and center-low, wood with a brass rail hint
    fill_poly(arr, [(W * 0.12, H), (W * 0.2, H * 0.68), (W * 0.8, H * 0.68), (W * 0.88, H)], (86, 62, 42), blur=0.8)
    fill_poly(arr, [(W * 0.2, H * 0.68), (W * 0.8, H * 0.68), (W * 0.8, H * 0.71), (W * 0.2, H * 0.71)], (150, 122, 76), blur=0.6)
    # the register + jar on the counter
    fill_poly(arr, [(W * 0.62, H * 0.56), (W * 0.72, H * 0.56), (W * 0.72, H * 0.685), (W * 0.62, H * 0.685)], C["basalt"], blur=0.6)
    fill_poly(arr, [(W * 0.3, H * 0.6), (W * 0.345, H * 0.6), (W * 0.345, H * 0.685), (W * 0.3, H * 0.685)], (200, 190, 150), blur=0.8, opacity=0.8)
    vignette(arr, 0.42)
    return arr


def salmonberry_winter(H, W):
    """The same coast, the year turned: storm light, white surf
    bands, the spruces leaning away from the wind."""
    arr = sky(H, W, [(0.0, (94, 102, 112)), (0.6, (130, 134, 138)), (1.0, (150, 148, 142))])
    hz = int(H * 0.55)
    glow(arr, W * 0.3, H * 0.2, W * 0.35, (170, 174, 180), 0.3)
    sea = sky(H, W, [(0.0, (52, 66, 78)), (1.0, (34, 46, 58))])
    seam = np.zeros((H, W, 1), np.float32); seam[hz:, :, 0] = 1.0
    arr[:] = arr * (1 - seam) + sea * seam
    tex(arr, seam[:, :, 0], 34, seed=17, scale=5)
    # three surf bands driving in
    rngb = np.random.default_rng(27)
    for i in range(3):
        by = hz + 14 + i * int(H * 0.09)
        pts_top = [(W * t / 8.0, by + rngb.integers(-8, 9) - 4) for t in range(9)]
        pts_bot = [(W * t / 8.0, by + 10 + i * 4 + rngb.integers(-6, 7)) for t in range(8, -1, -1)]
        fill_poly(arr, pts_top + pts_bot, C["foam"], blur=3.5, opacity=0.5 - i * 0.09)
    # the stacks in spray
    for (cx, sh, sw) in [(W * 0.42, H * 0.28, W * 0.05), (W * 0.52, H * 0.18, W * 0.033)]:
        base = hz + 10
        fill_poly(arr, [(cx - sw, base), (cx - sw * 0.4, base - sh), (cx + sw * 0.4, base - sh), (cx + sw, base)], (52, 58, 66), blur=1.4)
        glow(arr, cx, base - sh, sw * 2.4, (200, 206, 210), 0.25)
    # leaning spruces on the near headland — the wind made visible
    fill_poly(arr, [(0, H), (0, H * 0.34), (W * 0.2, H * 0.44), (W * 0.3, H * 0.6), (W * 0.34, H)], (44, 58, 48), blur=1)
    rng = np.random.default_rng(19)
    x = int(W * 0.02)
    while x < W * 0.3:
        h = int(rng.integers(int(H * 0.08), int(H * 0.16)))
        base = int(H * 0.46) + int(rng.integers(-8, 9))
        lean = int(h * 0.30)
        # a leaning spruce: stepped tiers like spruce(), sheared
        steps = 4
        pts = [(x + lean, base - h)]
        for s2 in range(steps):
            yy = base - h + h * (s2 + 1) / steps
            wid = 6 + 10 * (s2 + 1) / steps
            sh = lean * (1 - (s2 + 1) / steps)
            pts.append((x + sh + wid, yy))
            pts.append((x + sh + wid * 0.45, yy + 2))
        pts.append((x, base))
        for s2 in range(steps - 1, -1, -1):
            yy = base - h + h * (s2 + 1) / steps
            wid = 6 + 10 * (s2 + 1) / steps
            sh = lean * (1 - (s2 + 1) / steps)
            pts.append((x + sh - wid * 0.45, yy + 2))
            pts.append((x + sh - wid, yy))
        fill_poly(arr, pts, (38, 50, 42), blur=0.8)
        x += int(rng.integers(22, 44))
    # rain streaks
    streak = noise(H, W, scale=2, seed=23, blur=0)
    arr[:] = arr + ((streak[:, :, None] - 0.5) * 6)
    vignette(arr, 0.4)
    return arr


def estuary4_watershed(H, W):
    """Oneironautics field-guide gouache: the 2016 estuary — green
    flats, the winding channel, the tide gate, one heron."""
    arr = sky(H, W, [(0.0, (168, 186, 196)), (0.55, (204, 212, 208)), (1.0, (222, 220, 204))])
    hz = int(H * 0.42)
    fill_poly(arr, [(0, hz), (W * 0.35, hz - H * 0.08), (W * 0.7, hz - H * 0.03), (W, hz - H * 0.09), (W, hz)], C["fir_far"], blur=4)
    sprucerow(arr, 0, W, hz - 2, C["fir_far"], seed=31, blur=2.5)
    # the flats: layered greens with mud margins
    fill_poly(arr, [(0, H), (0, hz), (W, hz), (W, H)], (128, 148, 104), blur=0)
    tex(arr, _mask(H, W, [(0, H), (0, hz), (W, hz), (W, H)]), 18, seed=33, scale=8)
    fill_poly(arr, [(0, hz + H * 0.06), (W, hz + H * 0.02), (W, hz + H * 0.10), (0, hz + H * 0.16)], (150, 160, 108), blur=3, opacity=0.7)
    fill_poly(arr, [(0, H * 0.86), (W, H * 0.8), (W, H), (0, H)], (108, 124, 88), blur=3, opacity=0.8)
    # the channel: a winding pale-blue band, mud edges
    ch = [(W * 0.5, hz + 4), (W * 0.46, H * 0.47), (W * 0.42, H * 0.52),
          (W * 0.48, H * 0.575), (W * 0.55, H * 0.62), (W * 0.50, H * 0.69),
          (W * 0.44, H * 0.76), (W * 0.50, H * 0.83), (W * 0.58, H * 0.9),
          (W * 0.54, H * 0.95), (W * 0.5, H)]
    for i in range(len(ch) - 1):
        (x0, y0), (x1, y1) = ch[i], ch[i + 1]
        wd0 = 8 + i * 3; wd1 = 8 + (i + 1) * 3
        fill_poly(arr, [(x0 - wd0 - 6, y0), (x1 - wd1 - 6, y1), (x1 + wd1 + 6, y1), (x0 + wd0 + 6, y0)], (146, 128, 96), blur=2, opacity=0.8)
        fill_poly(arr, [(x0 - wd0, y0), (x1 - wd1, y1), (x1 + wd1, y1), (x0 + wd0, y0)], (140, 168, 176), blur=1.5)
    # the tide gate at the channel head: timber frame + wing walls
    gx, gy = W * 0.5, hz + 6
    fill_poly(arr, [(gx - 26, gy - 22), (gx + 26, gy - 22), (gx + 26, gy - 16), (gx - 26, gy - 16)], (108, 84, 56), blur=0.6)
    for px in (gx - 22, gx, gx + 22):
        fill_poly(arr, [(px - 3, gy - 20), (px + 3, gy - 20), (px + 3, gy + 10), (px - 3, gy + 10)], (96, 74, 50), blur=0.5)
    fill_poly(arr, [(gx - 46, gy - 4), (gx - 22, gy - 10), (gx - 22, gy + 6), (gx - 46, gy + 8)], (120, 96, 64), blur=0.8)
    fill_poly(arr, [(gx + 22, gy - 10), (gx + 46, gy - 4), (gx + 46, gy + 8), (gx + 22, gy + 6)], (120, 96, 64), blur=0.8)
    # THE HERON · one, standing in the channel's second bend
    bx, by = W * 0.44, H * 0.55
    fill_poly(arr, [(bx - 2, by), (bx + 2, by), (bx + 1, by + 22), (bx - 1, by + 22)], (90, 98, 104), blur=0.4)
    fill_poly(arr, [(bx - 7, by - 10), (bx + 5, by - 14), (bx + 8, by - 2), (bx - 2, by + 2)], (120, 128, 134), blur=0.6)
    fill_poly(arr, [(bx + 4, by - 14), (bx + 14, by - 18), (bx + 15, by - 16), (bx + 6, by - 11)], (90, 98, 104), blur=0.4)
    vignette(arr, 0.25)
    return arr


def northwind_morning(H, W):
    """The harbor, morning one: masts against the east light, the
    long dock, and the dog already out at the end of it."""
    arr = sky(H, W, [(0.0, (72, 88, 110)), (0.45, (150, 140, 130)), (0.62, (238, 196, 140)), (1.0, (250, 220, 170))])
    hz = int(H * 0.60)
    glow(arr, W * 0.62, hz - 12, W * 0.42, (255, 220, 160), 0.6)
    sea = sky(H, W, [(0.0, (110, 108, 106)), (1.0, (62, 70, 82))])
    seam = np.zeros((H, W, 1), np.float32); seam[hz:, :, 0] = 1.0
    arr[:] = arr * (1 - seam) + sea * seam
    tex(arr, seam[:, :, 0], 20, seed=41, scale=7)
    glow(arr, W * 0.62, hz + 26, W * 0.3, (255, 224, 168), 0.35)
    # moored fleet: hulls + mast lines against the light
    rng = np.random.default_rng(43)
    for i in range(6):
        bx = W * (0.14 + i * 0.13) + rng.integers(-10, 10)
        bw = W * rng.uniform(0.05, 0.08)
        by = hz + 6 + i % 3 * 4
        fill_poly(arr, [(bx - bw / 2, by), (bx + bw / 2, by), (bx + bw / 2 - 4, by + 12), (bx - bw / 2 + 4, by + 12)], C["ink"], blur=0.7)
        mh = H * rng.uniform(0.16, 0.3)
        fill_poly(arr, [(bx - 1, by), (bx + 1, by), (bx + 1, by - mh), (bx - 1, by - mh)], C["ink"], blur=0.3)
        fill_poly(arr, [(bx, by - mh), (bx + bw * 0.4, by - mh * 0.55), (bx + bw * 0.4 + 1, by - mh * 0.55 + 2), (bx + 1, by - mh + 2)], C["ink"], blur=0.3, opacity=0.8)
    # the dock: dark planks running right, pilings
    fill_poly(arr, [(W * 0.05, H * 0.78), (W, H * 0.70), (W, H * 0.78), (W * 0.05, H * 0.9)], (56, 44, 36), blur=0.7)
    for i in range(6):
        px = W * (0.12 + i * 0.15)
        py = H * (0.9 - i * 0.024)
        fill_poly(arr, [(px - 4, py), (px + 4, py), (px + 4, py + H * 0.08), (px - 4, py + H * 0.08)], (40, 32, 26), blur=0.5)
    # BOSUN · at the end of the dock, small, ears up, facing the sun
    dx, dy = W * 0.80, H * 0.705
    fill_poly(arr, [(dx - 10, dy), (dx + 8, dy), (dx + 8, dy - 12), (dx - 10, dy - 10)], C["ink"], blur=0.4)
    fill_poly(arr, [(dx + 6, dy - 12), (dx + 14, dy - 18), (dx + 15, dy - 8), (dx + 8, dy - 8)], C["ink"], blur=0.4)
    fill_poly(arr, [(dx + 9, dy - 18), (dx + 11, dy - 22), (dx + 13, dy - 18)], C["ink"], blur=0.3)
    fill_poly(arr, [(dx - 10, dy - 9), (dx - 16, dy - 14), (dx - 15, dy - 6), (dx - 10, dy - 4)], C["ink"], blur=0.4)
    _gulls(arr, [(W * 0.4, H * 0.26), (W * 0.47, H * 0.3), (W * 0.7, H * 0.2)])
    vignette(arr, 0.3)
    return arr


def feyfaire_gate(H, W):
    """The Faire gate at dusk: bulb-lit arch, deep violet sky, the
    wheel's silhouette beyond, the ticket booth's one warm window."""
    arr = sky(H, W, [(0.0, (34, 24, 58)), (0.5, (74, 42, 84)), (0.8, (140, 74, 92)), (1.0, (190, 110, 96))])
    hz = int(H * 0.72)
    # ground: trampled fairground dust catching the sky
    fill_poly(arr, [(0, H), (0, hz), (W, hz), (W, H)], (92, 62, 66), blur=0)
    tex(arr, _mask(H, W, [(0, H), (0, hz), (W, hz), (W, H)]), 20, seed=51, scale=8)
    # the wheel beyond, dark spokes
    wx, wy, wr = W * 0.78, H * 0.42, H * 0.26
    for k in range(12):
        a0 = k * math.pi / 6
        fill_poly(arr, [(wx, wy), (wx + wr * math.cos(a0), wy + wr * math.sin(a0)), (wx + wr * math.cos(a0) + 2, wy + wr * math.sin(a0) + 2)], (26, 18, 40), blur=0.5, opacity=0.9)
    for k in range(24):
        a0 = k * math.pi / 12
        glow(arr, wx + wr * math.cos(a0), wy + wr * math.sin(a0), 6, (240, 180, 120), 0.25)
    # THE GATE: two posts + arch, strung with bulbs
    g0, g1 = W * 0.28, W * 0.56
    for gx2 in (g0, g1):
        fill_poly(arr, [(gx2 - 8, H * 0.30), (gx2 + 8, H * 0.30), (gx2 + 10, hz + 8), (gx2 - 10, hz + 8)], (44, 30, 34), blur=0.5)
    fill_poly(arr, [(g0 - 12, H * 0.34), (g0 + (g1 - g0) / 2, H * 0.24), (g1 + 12, H * 0.34), (g1 + 12, H * 0.30), (g0 + (g1 - g0) / 2, H * 0.20), (g0 - 12, H * 0.30)], (44, 30, 34), blur=0.6)
    n_bulbs = 11
    for i in range(n_bulbs):
        t = i / (n_bulbs - 1)
        bxp = g0 + (g1 - g0) * t
        byp = H * 0.30 - math.sin(t * math.pi) * H * 0.065
        glow(arr, bxp, byp, 9, (255, 214, 150), 0.7)
    glow(arr, (g0 + g1) / 2, H * 0.30, (g1 - g0) * 0.8, (255, 200, 130), 0.22)
    # ticket booth, right of the gate, one warm window
    tb = W * 0.63
    fill_poly(arr, [(tb, hz + 6), (tb + W * 0.09, hz + 6), (tb + W * 0.09, H * 0.48), (tb, H * 0.48)], (66, 40, 48), blur=0.6)
    fill_poly(arr, [(tb - 6, H * 0.48), (tb + W * 0.045, H * 0.43), (tb + W * 0.09 + 6, H * 0.48)], (90, 52, 56), blur=0.6)
    fill_poly(arr, [(tb + W * 0.02, H * 0.54), (tb + W * 0.07, H * 0.54), (tb + W * 0.07, H * 0.62), (tb + W * 0.02, H * 0.62)], C["window"], blur=1)
    glow(arr, tb + W * 0.045, H * 0.58, 18, C["window"], 0.6)
    # the path in, worn pale through the gate
    fill_poly(arr, [(W * 0.36, H), ((g0 + g1) / 2 - 14, hz + 4), ((g0 + g1) / 2 + 14, hz + 4), (W * 0.56, H)], (140, 96, 84), blur=2.5, opacity=0.6)
    vignette(arr, 0.38)
    return arr


SCENES = {
    "salmonberry_title": salmonberry_title,
    "salmonberry_song": salmonberry_song,
    "salmonberry_coast": salmonberry_coast,
    "salmonberry_town": salmonberry_town,
    "salmonberry_house": salmonberry_house,
    "salmonberry_store": salmonberry_store,
    "salmonberry_winter": salmonberry_winter,
    "estuary4_watershed": estuary4_watershed,
    "northwind_morning": northwind_morning,
    "feyfaire_gate": feyfaire_gate,
}


def paint(scene_id, out_png, source_png=None, W=1280, H=720, colors=256, preview=0):
    if scene_id not in SCENES:
        raise SystemExit("unknown scene '%s' (see --list)" % scene_id)
    arr = SCENES[scene_id](H, W)
    src = Image.fromarray(clamp(arr))
    sp = source_png or (out_png.rsplit(".", 1)[0] + ".src.png")
    os.makedirs(os.path.dirname(os.path.abspath(sp)), exist_ok=True)
    src.save(sp)
    svga_quantize.quantize(sp, out_png, width=320, height=200, colors=colors,
                           dither="fs", preview=preview)
    return out_png


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene", nargs="?")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--source")
    ap.add_argument("--colors", type=int, default=256)
    ap.add_argument("--preview", type=int, default=0)
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        print("\n".join(sorted(SCENES.keys()))); return 0
    if not a.scene or not a.out:
        ap.error("need SCENE_ID out.png (or --list)")
    paint(a.scene, a.out, a.source, colors=a.colors, preview=a.preview)
    return 0


if __name__ == "__main__":
    sys.exit(main())
