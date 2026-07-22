#!/usr/bin/env python3
"""
svga_quantize.py — the ERA FILTER.

The alt-reality prism, made literal: take a modern painted source image
(an AI-generated background, or any high-res painting) and press it
through an early-1990s 256-color SVGA adventure-game look — the Sierra /
LucasArts register — by downscaling to a period internal resolution and
quantizing to a small indexed palette with ordered or Floyd-Steinberg
dithering.

This is deterministic and has NO network dependency. It is the second
half of the hybrid art pipeline (see scene_render.py for the first half,
which fetches the painted source). It can also be run on any hand- or
procedurally-painted source with zero AI involved.

Usage:
    python3 svga_quantize.py IN.png OUT.png
    python3 svga_quantize.py IN.png OUT.png --width 320 --height 200 \
        --colors 256 --dither fs --preview 3
    python3 svga_quantize.py --selftest OUT_DIR

Options:
    --width/--height   period internal resolution (default 320x200)
    --colors N         palette size (default 256; try 64/32 for older look)
    --dither fs|ordered|none   (default fs)
    --palette FILE     fixed shared palette (one #rrggbb per line);
                       omit for a per-image ADAPTIVE palette (authentic:
                       SCI/SCUMM rooms often had their own 256)
    --posterize P      optional pre-quantize value-posterize (0=off)
    --saturate S       optional saturation multiply before quantize (1.0=off)
    --preview N        also write OUT.preview.png at N x nearest upscale
"""
import argparse, sys, os, math
from PIL import Image, ImageEnhance

BAYER8 = [
    [0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44, 4, 36, 14, 46, 6, 38], [60, 28, 52, 20, 62, 30, 54, 22],
    [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21],
]


def _hex(s):
    s = s.strip().lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def _load_palette(path):
    cols = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") or (line.startswith("#") and len(line) in (7, 4)):
                if line.startswith("#") and len(line) == 7:
                    cols.append(_hex(line))
                elif not line.startswith("#") and len(line) == 6:
                    cols.append(_hex(line))
    return cols


def _palette_image(cols):
    pal = []
    for c in cols[:256]:
        pal.extend(c)
    # pad to 256 entries
    while len(pal) < 256 * 3:
        pal.extend(cols[-1] if cols else (0, 0, 0))
    p = Image.new("P", (1, 1))
    p.putpalette(pal)
    return p


def _ordered_dither_to_palette(img, cols):
    # manual ordered (Bayer 8x8) dither to a fixed palette
    import numpy as np
    arr = np.asarray(img.convert("RGB"), dtype=np.float32)
    h, w, _ = arr.shape
    pal = np.array(cols, dtype=np.float32)              # (K,3)
    # bayer threshold map centered at 0, scaled to ~ one palette step
    bay = np.array(BAYER8, dtype=np.float32) / 64.0 - 0.5
    tile = np.tile(bay, (h // 8 + 1, w // 8 + 1))[:h, :w]
    spread = 32.0                                        # dither strength in 0-255
    arr = arr + tile[:, :, None] * spread
    flat = arr.reshape(-1, 3)
    # nearest palette entry per pixel
    d = ((flat[:, None, :] - pal[None, :, :]) ** 2).sum(2)
    idx = d.argmin(1).astype(np.uint8)
    out = Image.new("P", (w, h))
    palflat = []
    for c in cols[:256]:
        palflat.extend([int(c[0]), int(c[1]), int(c[2])])
    while len(palflat) < 256 * 3:
        palflat.extend([0, 0, 0])
    out.putpalette(palflat)
    out.putdata(idx.tolist())
    return out


def quantize(inp, outp, width=320, height=200, colors=256, dither="fs",
             palette=None, posterize=0, saturate=1.0, preview=0):
    img = Image.open(inp).convert("RGB")
    # downscale to the period internal resolution (LANCZOS keeps it painterly)
    if width and height:
        img = img.resize((width, height), Image.LANCZOS)
    if saturate and abs(saturate - 1.0) > 1e-3:
        img = ImageEnhance.Color(img).enhance(saturate)
    if posterize and posterize > 0:
        from PIL import ImageOps
        img = ImageOps.posterize(img, max(1, min(8, int(posterize))))

    cols = _load_palette(palette) if palette else None
    if cols:
        if dither == "ordered":
            out = _ordered_dither_to_palette(img, cols)
        else:
            pimg = _palette_image(cols)
            d = Image.Dither.FLOYDSTEINBERG if dither == "fs" else Image.Dither.NONE
            out = img.quantize(palette=pimg, dither=d)
    else:
        d = Image.Dither.FLOYDSTEINBERG if dither == "fs" else Image.Dither.NONE
        # ADAPTIVE per-image palette (authentic per-room 256)
        out = img.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=d)

    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True)
    out.save(outp)
    n_used = len(out.getcolors(maxcolors=65536) or [])
    print("wrote %s  (%dx%d, %d colors used)" % (outp, out.width, out.height, n_used))
    if preview and preview > 1:
        pv = out.convert("RGB").resize((out.width * preview, out.height * preview), Image.NEAREST)
        pvp = outp.rsplit(".", 1)[0] + ".preview.png"
        pv.save(pvp)
        print("wrote %s  (%dx nearest)" % (pvp, preview))
    return outp


def _selftest(outdir):
    # synthesize a painterly source (gradient sky + soft blobs + noise),
    # then run it through the filter, to prove the transform end to end.
    import numpy as np
    os.makedirs(outdir, exist_ok=True)
    W, H = 960, 600
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    r = (0.55 + 0.35 * (1 - y)) * 255
    g = (0.60 + 0.30 * (1 - y)) * 255
    b = (0.70 + 0.25 * y) * 255
    arr = np.zeros((H, W, 3), np.float32)
    arr[..., 0] = r; arr[..., 1] = g; arr[..., 2] = b * np.ones_like(x)
    # a soft dark headland
    hill = (y * H > (H * 0.6 + 60 * np.sin(x * 6)))
    arr[hill] = arr[hill] * 0.25 + np.array([40, 70, 55]) * 0.75
    arr += (np.random.default_rng(7).random((H, W, 3)) - 0.5) * 16
    src = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    sp = os.path.join(outdir, "selftest.src.png"); src.save(sp)
    quantize(sp, os.path.join(outdir, "selftest.png"), colors=64, dither="fs", preview=2)
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp", nargs="?")
    ap.add_argument("outp", nargs="?")
    ap.add_argument("--width", type=int, default=320)
    ap.add_argument("--height", type=int, default=200)
    ap.add_argument("--colors", type=int, default=256)
    ap.add_argument("--dither", choices=["fs", "ordered", "none"], default="fs")
    ap.add_argument("--palette")
    ap.add_argument("--posterize", type=int, default=0)
    ap.add_argument("--saturate", type=float, default=1.0)
    ap.add_argument("--preview", type=int, default=0)
    ap.add_argument("--selftest")
    a = ap.parse_args()
    if a.selftest:
        _selftest(a.selftest); return 0
    if not a.inp or not a.outp:
        ap.error("need IN.png OUT.png (or --selftest DIR)")
    quantize(a.inp, a.outp, a.width, a.height, a.colors, a.dither,
             a.palette, a.posterize, a.saturate, a.preview)
    return 0


if __name__ == "__main__":
    sys.exit(main())
