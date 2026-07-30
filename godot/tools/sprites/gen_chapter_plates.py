#!/usr/bin/env python3
"""gen_chapter_plates.py — endpaper plates behind the VN chapter card.

The chapter card is the book's most-seen page (71 boundaries across
vols 5-7) and it has been type on a flat black field. These are the
ENDPAPERS: laid paper with chain lines, a fine marbled comb drawn
in the volume's own ink, foxing where old paper ages, and a heavy
deckle vignette so the type still owns the middle of the frame.

One palette per volume, three variants each so consecutive chapters
never repeat the same sheet. Deterministic (crc32 of vol+variant).

Output: godot/assets/vn/plates/chapter_v<N>_<k>.png (1280x720)
"""
import os, math, random, zlib
from PIL import Image, ImageDraw, ImageFilter

W, H = 1280, 720
OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "assets", "vn", "plates"))

# vol -> (paper base, ink for the comb, foxing tint)
# 5 · the arcana, the river, sodium and brass
# 6 · Texas, darkroom chemistry, the search — cooler, sparer
# 7 · the coast, cedar and bowl-brass, green-shot
VOLUMES = {
    5: ((54, 43, 32), (128, 92, 46), (104, 74, 40)),
    6: ((38, 44, 54), (74, 104, 130), (78, 84, 100)),
    7: ((38, 48, 42), (76, 118, 96), (74, 94, 74)),
}
VARIANTS = 3


def laid_paper(rng, base):
    """Hand-laid sheet: fine horizontal wire lines + widely spaced
    vertical chain lines, the way real endpaper reads in raking light."""
    img = Image.new("RGB", (W, H), base)
    d = ImageDraw.Draw(img)
    for y in range(0, H, 3):
        v = rng.randint(-6, 8)
        d.line([0, y, W, y], fill=tuple(max(0, min(255, c + v)) for c in base))
    x = rng.randint(0, 26)
    while x < W:
        v = rng.randint(9, 16)
        d.line([x, 0, x, H], fill=tuple(max(0, min(255, c + v)) for c in base))
        x += rng.randint(26, 34)
    return img


def comb_marble(rng, img, ink):
    """A marbler's comb: parallel waves pulled through, then raked
    across. Kept very low-contrast — this is a whisper under type."""
    d = ImageDraw.Draw(img, "RGBA")
    bands = 30
    phase = rng.uniform(0, math.tau)
    amp = rng.uniform(16.0, 30.0)
    freq = rng.uniform(1.6, 2.6)
    for b in range(bands):
        y0 = -40.0 + b * (H + 80.0) / bands
        pts = []
        for i in range(0, W + 20, 20):
            t = i / float(W)
            y = y0 + math.sin(t * math.tau * freq + phase + b * 0.30) * amp \
                   + math.sin(t * math.tau * freq * 2.3 + b * 0.7) * (amp * 0.28)
            pts.append((i, y))
        a = 62 if b % 2 == 0 else 34
        d.line(pts, fill=(ink[0], ink[1], ink[2], a), width=2 if b % 2 == 0 else 1)
    return img


def foxing(rng, img, tint):
    """Age spots — sparse, soft, never in the type's way (the centre
    band is skipped so the title never fights a blotch)."""
    spot = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(spot)
    for _ in range(90):
        cx = rng.randint(0, W)
        cy = rng.randint(0, H)
        if 250 < cy < 470 and 240 < cx < 1040:
            continue                      # keep the plate's heart clean
        r = rng.randint(6, 26)
        for k in range(r, 0, -2):
            a = int(30 * (1.0 - k / r) ** 2)
            d.ellipse([cx - k, cy - k, cx + k, cy + k],
                      fill=tuple(int(c * a / 255) for c in tint))
    spot = spot.filter(ImageFilter.GaussianBlur(7))
    return _screen(img, spot)


def _screen(a, b):
    pa, pb = a.load(), b.load()
    out = Image.new("RGB", (W, H))
    po = out.load()
    for y in range(H):
        for x in range(W):
            ra, ga, ba = pa[x, y]
            rb, gb, bb = pb[x, y]
            po[x, y] = (255 - (255 - ra) * (255 - rb) // 255,
                        255 - (255 - ga) * (255 - gb) // 255,
                        255 - (255 - ba) * (255 - bb) // 255)
    return out


def deckle(img):
    """Heavy edge fall-off to near-black: the plate must never compete
    with the Cinzel kicker and IM Fell title sitting on top of it.
    Built as a true radial ramp (ellipse OUTLINES draw rings, not a
    gradient — the first render proved that the hard way)."""
    sw, sh = 160, 90
    small = Image.new("L", (sw, sh))
    px = small.load()
    for y in range(sh):
        for x in range(sw):
            dx = (x - sw * 0.5) / (sw * 0.5)
            dy = (y - sh * 0.5) / (sh * 0.5)
            r = math.sqrt(dx * dx * 0.82 + dy * dy)
            v = 1.0 - max(0.0, min(1.0, (r - 0.62) / 0.78))
            px[x, y] = int(255 * (v ** 0.85))
    mask = small.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(24))
    dark = Image.new("RGB", (W, H), (5, 5, 6))
    return Image.composite(img, dark, mask)


def main():
    os.makedirs(OUT, exist_ok=True)
    n = 0
    for vol, (base, ink, tint) in sorted(VOLUMES.items()):
        for k in range(VARIANTS):
            rng = random.Random(zlib.crc32(("chapter_v%d_%d" % (vol, k)).encode()))
            img = laid_paper(rng, base)
            img = comb_marble(rng, img, ink)
            img = foxing(rng, img, tint)
            img = deckle(img)
            path = os.path.join(OUT, "chapter_v%d_%d.png" % (vol, k))
            img.save(path, optimize=True)
            print("wrote", os.path.basename(path))
            n += 1
    print(n, "chapter plates")


if __name__ == "__main__":
    main()
