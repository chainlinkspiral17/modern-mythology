#!/usr/bin/env python3
"""gen_gauntlet_floors.py — atmospheric floor plates for the TAROT
GAUNTLET top-down board, one per location.

The old approach (painted literal maps) could never align with the
JSON's pos_xy stations, so the engine ghosts the board bg at 12%
alpha. These plates are PURE MATERIAL — floorboards, stone flags,
linoleum, gravel — plus two or three soft pools of the location's
accent light and a heavy vignette. Nothing in them can misalign,
so the engine can afford to show them warmer. The engine-drawn
markers + adjacency lines stay the authoritative map.

Deterministic (seeded per location id). Output:
  godot/assets/gallery/locations/<id>_gauntlet_board.png  (1000x600)

Run twice → identical bytes (git-diff clean).
"""
import os, math, random, zlib
from PIL import Image, ImageDraw, ImageFilter

W, H = 1000, 600
OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "assets", "gallery", "locations"))

# id -> (material, base RGB, accent RGB)
LOCATIONS = {
    "dambrosios":            ("checker",  (46, 38, 30),  (216, 138, 48)),
    "cathedral":             ("flagstone",(36, 36, 44),  (208, 168, 88)),
    "riverboat_interior":    ("plank",    (44, 32, 24),  (206, 148, 62)),
    "elicia_bungalow":       ("carpet",   (48, 38, 40),  (222, 158, 96)),
    "ember_ash_office":      ("tile",     (38, 40, 44),  (168, 190, 200)),
    "asylum_ward_c":         ("tile",     (40, 46, 42),  (170, 200, 178)),
    "bayou_lighthouse":      ("plank",    (34, 38, 42),  (140, 176, 196)),
    "carnival_lot":          ("gravel",   (40, 34, 28),  (228, 170, 84)),
    "christian_ice_co":      ("concrete", (38, 42, 46),  (168, 208, 224)),
    "courthouse_chamber":    ("flagstone",(42, 38, 34),  (196, 168, 120)),
    "daigles_roadhouse":     ("plank",    (40, 28, 24),  (216, 92, 84)),
    "frog_knows_best":       ("tile",     (36, 42, 36),  (150, 200, 130)),
    "lacombe_service_garage":("concrete", (36, 36, 36),  (222, 186, 110)),
    "le_roulant_casino":     ("carpet",   (40, 30, 38),  (216, 180, 90)),
    "mixing_glass":          ("plank",    (32, 26, 24),  (214, 160, 84)),
    "parish_cemetery":       ("gravel",   (32, 36, 32),  (176, 190, 210)),
    "roadside_chapel":       ("plank",    (42, 34, 26),  (226, 178, 112)),
    "roberts_house":         ("plank",    (46, 36, 28),  (222, 170, 110)),
    "simon_apartment":       ("carpet",   (42, 40, 36),  (206, 180, 130)),
    "solenade_garden":       ("brick",    (40, 36, 32),  (228, 196, 120)),
    "static_drive_in":       ("asphalt",  (30, 32, 36),  (150, 178, 214)),
    "the_hierophant_circuit":("asphalt",  (34, 34, 34),  (222, 168, 96)),
    "wgur_transmitter_shack":("plank",    (38, 34, 28),  (224, 110, 96)),
}


def jitter(rng, c, amt):
    # LUMINANCE jitter — one shared delta keeps material reading as
    # one substance under varied light; per-channel deltas read as
    # rainbow noise (the first render's flagstones proved it).
    d = rng.randint(-amt, amt)
    return tuple(max(0, min(255, v + d)) for v in c)


def material_layer(rng, mat, base):
    img = Image.new("RGB", (W, H), base)
    d = ImageDraw.Draw(img)
    if mat == "plank":
        y = 0
        while y < H:
            bh = rng.randint(34, 52)
            col = jitter(rng, base, 6)
            d.rectangle([0, y, W, y + bh], fill=col)
            d.line([0, y, W, y], fill=jitter(rng, base, 14), width=1)
            # board seams staggered along the run
            x = rng.randint(-80, 0)
            while x < W:
                seg = rng.randint(160, 340)
                x += seg
                d.line([x, y + 2, x, y + bh - 2], fill=jitter(rng, base, 16), width=1)
            # grain flecks
            for _ in range(26):
                gx, gy = rng.randint(0, W), rng.randint(y + 3, min(H - 1, y + bh - 3))
                d.line([gx, gy, gx + rng.randint(8, 30), gy], fill=jitter(rng, col, 8), width=1)
            y += bh
    elif mat == "flagstone":
        y = 0
        while y < H:
            rh = rng.randint(70, 110)
            x = rng.randint(-60, 0)
            while x < W:
                rw = rng.randint(90, 170)
                col = jitter(rng, base, 8)
                d.rectangle([x + 2, y + 2, x + rw - 2, y + rh - 2], fill=col)
                x += rw
            y += rh
    elif mat == "checker":
        s = 56
        for gy in range(0, H // s + 1):
            for gx in range(0, W // s + 1):
                if (gx + gy) % 2 == 0:
                    d.rectangle([gx * s, gy * s, gx * s + s, gy * s + s],
                                fill=jitter(rng, tuple(min(255, v + 10) for v in base), 4))
    elif mat == "tile":
        s = 64
        for gy in range(0, H // s + 1):
            for gx in range(0, W // s + 1):
                d.rectangle([gx * s + 1, gy * s + 1, gx * s + s - 1, gy * s + s - 1],
                            fill=jitter(rng, base, 5))
    elif mat == "carpet":
        for _ in range(9000):
            x, y = rng.randint(0, W - 1), rng.randint(0, H - 1)
            d.point((x, y), fill=jitter(rng, base, 10))
    elif mat == "concrete":
        for _ in range(6000):
            x, y = rng.randint(0, W - 1), rng.randint(0, H - 1)
            d.point((x, y), fill=jitter(rng, base, 7))
        for _ in range(5):   # expansion cracks
            x = rng.randint(80, W - 80)
            d.line([x, 0, x + rng.randint(-40, 40), H], fill=jitter(rng, base, 18), width=1)
    elif mat == "gravel":
        for _ in range(4200):
            x, y = rng.randint(0, W - 4), rng.randint(0, H - 4)
            r = rng.randint(1, 3)
            d.ellipse([x, y, x + r, y + r], fill=jitter(rng, base, 16))
    elif mat == "brick":
        bh, bw = 30, 80
        for gy in range(0, H // bh + 1):
            off = (bw // 2) if gy % 2 else 0
            for gx in range(-1, W // bw + 1):
                d.rectangle([gx * bw + off + 2, gy * bh + 2,
                             gx * bw + off + bw - 2, gy * bh + bh - 2],
                            fill=jitter(rng, base, 9))
    elif mat == "asphalt":
        for _ in range(8000):
            x, y = rng.randint(0, W - 1), rng.randint(0, H - 1)
            d.point((x, y), fill=jitter(rng, base, 9))
    return img


def light_pools(rng, img, accent):
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(glow)
    for _ in range(3):
        cx, cy = rng.randint(150, W - 150), rng.randint(120, H - 120)
        r = rng.randint(140, 240)
        for k in range(r, 0, -6):
            a = int(72 * (1.0 - k / r) ** 2)
            d.ellipse([cx - k, cy - k, cx + k, cy + k],
                      fill=tuple(int(v * a / 255) for v in accent))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    return Image.blend(img, Image.composite(glow, img, Image.new("L", (W, H), 110)), 0.5) \
        if False else _screen(img, glow)


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


def vignette(img):
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    for k in range(120):
        a = int(150 * (k / 120.0) ** 1.6)
        d.rectangle([k * W // 240, k * H // 240, W - k * W // 240, H - k * H // 240],
                    outline=a)
    mask = mask.filter(ImageFilter.GaussianBlur(30))
    black = Image.new("RGB", (W, H), (6, 6, 8))
    return Image.composite(img, black, mask.point(lambda v: 255 - v))


def main():
    os.makedirs(OUT, exist_ok=True)
    for lid, (mat, base, accent) in sorted(LOCATIONS.items()):
        rng = random.Random(zlib.crc32(lid.encode()))
        img = material_layer(rng, mat, base)
        img = light_pools(rng, img, accent)
        img = vignette(img)
        path = os.path.join(OUT, "%s_gauntlet_board.png" % lid)
        img.save(path, optimize=True)
        print("wrote", os.path.basename(path))
    print(len(LOCATIONS), "floor plates")


if __name__ == "__main__":
    main()
