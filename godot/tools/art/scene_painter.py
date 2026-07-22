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
    # near headland (left), steep, dark, sharp, with spruce
    fill_poly(arr, [(0, H), (0, H * 0.30), (W * 0.14, H * 0.36), (W * 0.26, H * 0.52), (W * 0.30, H), ], C["fir"], blur=1.0)
    sprucerow(arr, int(W * 0.02), int(W * 0.28), int(H * 0.40), C["fir"], seed=3, blur=1.0)
    # the cannery on pilings + the house, small, at the base of the headland
    dcx = int(W * 0.30)
    fill_poly(arr, [(dcx, hz + 4), (dcx + W * 0.14, hz + 4), (dcx + W * 0.14, hz + 22), (dcx, hz + 22)], C["rust"], blur=0.5)
    for i in range(6):
        px = dcx + int(W * 0.02) + i * int(W * 0.02)
        fill_poly(arr, [(px, hz + 22), (px + 3, hz + 22), (px + 3, hz + 48), (px, hz + 48)], C["ink"], blur=0)
    hx = int(W * 0.33)
    fill_poly(arr, [(hx, H * 0.78), (hx + W * 0.09, H * 0.78), (hx + W * 0.09, H * 0.90), (hx, H * 0.90)], C["wood"], blur=0.5)
    fill_poly(arr, [(hx - 4, H * 0.78), (hx + W * 0.045, H * 0.72), (hx + W * 0.09 + 4, H * 0.78)], C["rust"], blur=0.5)
    glow(arr, hx + W * 0.03, H * 0.84, 14, C["window"], 0.5)
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


SCENES = {
    "salmonberry_title": salmonberry_title,
    "salmonberry_song": salmonberry_song,
    "salmonberry_coast": salmonberry_coast,
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
