#!/usr/bin/env python3
"""Python mirror of WyrdFigureArt.gd — the drifter and the four sisters.

MUST BE KEPT IN LOCKSTEP with WyrdFigureArt.gd — when the GDScript
painter changes, change this mirror to match before trusting a
preview.

Same render language as the Earthman plates (5-value ramps with
Bayer-dithered transitions, folds, sloped organic silhouettes) in
the paperback inks. Transparent backgrounds — these composite over
existing screens — each figure standing on a small dust strip that
carries her motif.

  drifter · wide-brim hat, face in shadow beneath it, flared
            duster with folds, iron glint at the hip  (18x28)
  north   · shawled, the net draped between her hands, snow
            rising beside her
  east    · straight-backed in blood red, three shadows on the dust
  south   · rocking chair, the offered water glinting real
  west    · young, long ink hair, the violet eighth point at her
            collar  (sisters 28x44)
"""
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.getcwd(), "wyrd_figures.png")


def hexc(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16) / 255.0, int(s[2:4], 16) / 255.0,
            int(s[4:6], 16) / 255.0, 1.0)


CLEAR = (0, 0, 0, 0)
INK = hexc("201410")
DUST = hexc("c8a878")
BONE = hexc("e8dcc0")
BLOOD = hexc("7a3020")
SILVER = hexc("b8bcc8")
WYRD = hexc("8a58a8")
SCRUB = hexc("4a5a3a")


def darken(c, f):
    return (c[0] * (1 - f), c[1] * (1 - f), c[2] * (1 - f), 1.0)


def lighten(c, f):
    return (c[0] + (1 - c[0]) * f, c[1] + (1 - c[1]) * f, c[2] + (1 - c[2]) * f, 1.0)


def warm(c, f=0.22):
    l = lighten(c, f)
    return (min(1.0, l[0] * 1.08), l[1], l[2] * 0.92, 1.0)


_BAYER4 = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]


def bayer(x, y):
    return (_BAYER4[(y % 4) * 4 + (x % 4)] + 0.5) / 16.0


def h01(x, y, s):
    n = (x * 374761393 + y * 668265263 + s * 1442695041) & 0xFFFFFFFFFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFFFFFFFFFF
    n = n ^ (n >> 16)
    return (n & 0xFFFF) / 65536.0


class Img:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = [[CLEAR] * w for _ in range(h)]

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = c

    def hspan(self, x0, x1, y, c):
        for x in range(x0, x1 + 1):
            self.put(x, y, c)

    def vspan(self, x, y0, y1, c):
        for y in range(y0, y1 + 1):
            self.put(x, y, c)


def shaded_row(img, x0, x1, y, core):
    sh = darken(core, 0.42)
    mid = darken(core, 0.18)
    half = lighten(core, 0.10)
    lt = warm(core)
    span = max(1, x1 - x0)
    for x in range(x0, x1 + 1):
        t = (x - x0) / span
        if x == x1:
            c = lt
        elif t > 0.70:
            c = half if bayer(x, y) < 0.45 else core
        elif x == x0:
            c = sh
        elif t < 0.30:
            c = mid if bayer(x, y) < 0.6 else core
        else:
            c = core
        img.put(x, y, c)


def folds(img, x0, x1, y0, y1, core, seed, n):
    fold_c = darken(core, 0.30)
    for k in range(n):
        fx = x0 + 2 + int(h01(k, 5, seed) * max(1, (x1 - x0 - 3)))
        for y in range(y0 + 1, y1):
            if h01(fx, y, seed + k) < 0.75:
                img.put(fx, y, fold_c)


def dust_strip(img, base_y):
    """The ground the figure stands on — a small dust strip."""
    for y in range(base_y, min(img.h, base_y + 4)):
        for x in range(img.w):
            if bayer(x, y) < (0.85 - (y - base_y) * 0.25):
                img.put(x, y, DUST if y == base_y else darken(DUST, 0.25))


# ── the drifter · 18x28 ──────────────────────────────────────────

def drifter():
    img = Img(18, 28)
    cx = 9
    base = 24
    coat = hexc("2e1c14")
    dust_strip(img, base + 1)
    # boots
    for y in range(base - 1, base + 1):
        shaded_row(img, cx - 3, cx - 2, y, hexc("241a10"))
        shaded_row(img, cx + 1, cx + 2, y, hexc("241a10"))
    # the duster — flares from the waist, hem jitters
    for y in range(11, base - 1):
        t = (y - 11) / float(base - 12)
        hw = 3 + int(t * 3)
        if y > base - 4 and h01(1, y, 9) < 0.4:
            hw += 1
        shaded_row(img, cx - hw, cx + hw, y, coat)
    folds(img, cx - 3, cx + 3, 13, base - 2, coat, 9, 2)
    # coat splits over the front leg
    img.vspan(cx, base - 6, base - 2, darken(coat, 0.4))
    # shoulders slope
    shaded_row(img, cx - 3, cx + 3, 10, coat)
    shaded_row(img, cx - 4, cx + 4, 11, coat)
    # the iron at the hip — one silver glint
    img.put(cx + 4, 16, SILVER)
    img.put(cx + 4, 17, darken(SILVER, 0.3))
    # kerchief
    img.hspan(cx - 1, cx + 1, 9, BLOOD)
    # head — all shadow beneath the hat
    img.hspan(cx - 1, cx + 1, 7, darken(hexc("8a6848"), 0.45))
    img.hspan(cx - 1, cx + 1, 8, darken(hexc("8a6848"), 0.6))
    # the hat — wide brim, warm rim on the light side
    img.hspan(cx - 4, cx + 4, 6, INK)
    img.hspan(cx - 2, cx + 2, 5, INK)
    img.hspan(cx - 2, cx + 2, 4, INK)
    img.put(cx + 4, 6, warm(hexc("3a2c1c"), 0.3))
    img.put(cx + 2, 4, warm(hexc("3a2c1c"), 0.2))
    return img


# ── the sisters · 28x44 ──────────────────────────────────────────

def sister_north():
    img = Img(28, 44)
    cx = 14
    base = 38
    shawl = hexc("8890a0")
    dress = hexc("5a5a68")
    dust_strip(img, base + 1)
    # dress column
    for y in range(18, base + 1):
        t = (y - 18) / float(base - 18)
        hw = 3 + int(t * 3)
        shaded_row(img, cx - hw, cx + hw, y, dress)
    folds(img, cx - 3, cx + 3, 20, base - 1, dress, 11, 2)
    # shawl over head and shoulders
    for y in range(8, 18):
        hw = 2 + min(3, (y - 8) // 2)
        shaded_row(img, cx - hw, cx + hw, y, shawl)
    img.hspan(cx - 1, cx + 1, 11, darken(hexc("d8ccc0"), 0.15))    # face in the hood
    img.put(cx - 1, 12, darken(hexc("d8ccc0"), 0.4))
    img.put(cx + 1, 12, INK)                                       # one seen eye
    # arms out, the net draped between her hands
    img.vspan(cx - 6, 19, 24, darken(shawl, 0.2))
    img.vspan(cx + 6, 19, 24, warm(shawl, 0.1))
    for i, (x0, y0, x1, y1) in enumerate([(cx - 6, 25, cx + 6, 27),
                                          (cx - 6, 27, cx + 6, 25),
                                          (cx - 4, 24, cx - 1, 29),
                                          (cx + 1, 29, cx + 4, 24)]):
        steps = max(abs(x1 - x0), abs(y1 - y0))
        for s in range(steps + 1):
            x = x0 + (x1 - x0) * s // max(1, steps)
            y = y0 + (y1 - y0) * s // max(1, steps)
            img.put(x, y, SILVER)
    # snow, rising
    for sx, sy in [(3, 30), (5, 18), (23, 24), (25, 12), (2, 8), (24, 36), (7, 38)]:
        img.put(sx, sy, BONE)
        img.put(sx, sy - 1, hexc("f4f0e8"))
    return img


def sister_east():
    img = Img(28, 44)
    cx = 14
    base = 38
    dress = hexc("7a3020")
    dust_strip(img, base + 1)
    # three shadows on the dust, disagreeing
    for dx0, dx1 in [(-11, -4), (-1, 1), (4, 11)]:
        for t in range(8):
            x = cx + dx0 + (dx1 - dx0) * t // 8
            if bayer(x, base + 1 + t // 4) < 0.6:
                img.put(cx + dx0 + (dx1 - dx0) * t // 8, base + 1 + t // 4, INK)
    # dress — straight-backed, narrow
    for y in range(14, base + 1):
        t = (y - 14) / float(base - 14)
        hw = 2 + int(t * 3)
        shaded_row(img, cx - hw, cx + hw, y, dress)
    folds(img, cx - 3, cx + 3, 16, base - 1, dress, 13, 2)
    # arms folded
    img.hspan(cx - 3, cx + 3, 20, darken(dress, 0.3))
    img.hspan(cx - 3, cx + 3, 21, lighten(dress, 0.1))
    # head — dark hair pulled tight, face lit hard from the dawn
    shaded_row(img, cx - 2, cx + 2, 9, hexc("d8b8a0"))
    shaded_row(img, cx - 2, cx + 2, 10, hexc("d8b8a0"))
    shaded_row(img, cx - 2, cx + 2, 11, hexc("d8b8a0"))
    img.hspan(cx - 2, cx + 2, 8, INK)
    img.hspan(cx - 2, cx + 2, 7, INK)
    img.vspan(cx - 3, 9, 13, INK)
    img.put(cx + 1, 10, INK)                                       # eye
    img.hspan(cx - 1, cx + 1, 12, darken(hexc("d8b8a0"), 0.3))
    # the face-down mirror at her feet
    img.hspan(cx + 5, cx + 8, base, SILVER)
    img.hspan(cx + 5, cx + 8, base - 1, darken(SILVER, 0.35))
    return img


def sister_south():
    img = Img(28, 44)
    cx = 13
    base = 38
    dress = hexc("8a6838")
    chair = hexc("4a3018")
    dust_strip(img, base + 1)
    # the rocker
    for x0, y0, x1, y1 in [(4, base, 24, base - 3), (4, base - 3, 24, base)]:
        steps = 20
        for s in range(steps + 1):
            x = x0 + (x1 - x0) * s // steps
            y = y0 + (y1 - y0) * s // steps
            img.put(x, y, chair)
    img.vspan(6, 14, base - 2, chair)                              # chair back
    img.vspan(7, 12, base - 2, darken(chair, 0.2))
    img.vspan(20, 26, base - 2, chair)                             # front leg
    # seated figure
    for y in range(16, 27):                                        # torso, leaning back
        hw = 2 + (y - 16) // 4
        shaded_row(img, cx - hw + (26 - y) // 6, cx + hw, y, dress)
    for y in range(27, 33):                                        # lap, forward
        shaded_row(img, cx - 2, cx + 6, y, dress)
    folds(img, cx - 1, cx + 5, 27, 32, dress, 15, 2)
    img.vspan(cx + 6, 33, base - 1, darken(dress, 0.25))           # shin
    img.put(cx + 6, base, hexc("241a10"))                          # shoe
    # head — grey bun, kind face shaded
    shaded_row(img, cx - 1, cx + 3, 11, hexc("d0b898"))
    shaded_row(img, cx - 1, cx + 3, 12, hexc("d0b898"))
    shaded_row(img, cx - 1, cx + 3, 13, hexc("d0b898"))
    img.hspan(cx - 1, cx + 3, 10, SILVER)                          # the bun
    img.put(cx - 2, 11, SILVER)
    img.put(cx + 2, 12, INK)                                       # eye
    # the offered water — real, and that is the frightening part
    img.vspan(cx + 8, 24, 26, darken(dress, 0.2))                  # extended arm
    img.put(cx + 9, 26, SILVER)                                    # the cup
    img.put(cx + 9, 25, hexc("f4f0e8"))                            # the water's light
    return img


def sister_west():
    img = Img(28, 44)
    cx = 14
    base = 38
    dress = hexc("a08858")
    hair = hexc("241814")
    dust_strip(img, base + 1)
    # dress — young, a little wind in the hem
    for y in range(14, base + 1):
        t = (y - 14) / float(base - 14)
        hw = 2 + int(t * 4)
        lean = int(t * 2)                                          # hem drifts west
        shaded_row(img, cx - hw - lean, cx + hw - lean // 2, y, dress)
    folds(img, cx - 4, cx + 3, 16, base - 1, dress, 17, 3)
    # long ink hair, loose, falling past the shoulders
    for y in range(7, 22):
        w = 1 if y < 10 else 2
        img.vspan(cx - 3 - (y - 7) // 6, y, y, hair)
        for dx in range(w):
            img.put(cx - 3 - (y - 7) // 6 - dx, y, hair)
    img.hspan(cx - 2, cx + 2, 7, hair)
    img.hspan(cx - 2, cx + 2, 6, hair)
    # face — lit by the sunset, one eye, unhurried
    shaded_row(img, cx - 2, cx + 2, 9, hexc("e0c0a0"))
    shaded_row(img, cx - 2, cx + 2, 10, hexc("e0c0a0"))
    shaded_row(img, cx - 2, cx + 2, 11, hexc("e0c0a0"))
    img.put(cx + 1, 10, INK)
    img.hspan(cx - 1, cx + 1, 12, darken(hexc("e0c0a0"), 0.3))
    # hand on hip
    img.vspan(cx + 4, 18, 22, darken(dress, 0.2))
    img.put(cx + 4, 23, hexc("e0c0a0"))
    # the eighth point at her collar — the only violet in the figure
    img.put(cx, 14, WYRD)
    img.put(cx - 1, 13, WYRD)
    img.put(cx + 1, 13, WYRD)
    img.put(cx, 12, lighten(WYRD, 0.3))
    return img


FIGS = [("drifter", drifter), ("north", sister_north), ("east", sister_east),
        ("south", sister_south), ("west", sister_west)]


def main():
    scale = 5
    pad = 10
    tiles = []
    for name, fn in FIGS:
        img = fn()
        tile = Image.new("RGBA", (img.w, img.h))
        for y in range(img.h):
            for x in range(img.w):
                c = img.px[y][x]
                tile.putpixel((x, y), tuple(int(round(min(max(v, 0), 1) * 255)) for v in c))
        tiles.append((name, tile.resize((img.w * scale, img.h * scale), Image.NEAREST)))
    wtot = sum(t.width + pad for _, t in tiles) + pad
    htot = max(t.height for _, t in tiles) + 30
    sheet = Image.new("RGB", (wtot, htot), (44, 30, 22))   # dust-dark review ground
    draw = ImageDraw.Draw(sheet)
    x = pad
    for name, t in tiles:
        sheet.paste(t, (x, htot - t.height - 24), t)
        draw.text((x, htot - 18), name, fill=(230, 218, 195))
        x += t.width + pad
    sheet.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
