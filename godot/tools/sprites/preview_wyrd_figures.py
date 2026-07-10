#!/usr/bin/env python3
"""Python mirror of WyrdFigureArt.gd.

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


# ── human bones ──────────────────────────────────────────────────
# Head ≈ 1/6 of figure height, neck, sloped shoulders ≈ two head
# widths, fitted bodice to a WAIST, skirts flare from the waist.

def head6(img, cx, top, skin):
    """Rounded 5x6 head with two eyes and a mouth hint."""
    for y in range(top, top + 6):
        x0, x1 = cx - 2, cx + 2
        if y == top or y == top + 5:
            x0, x1 = cx - 1, cx + 1
        shaded_row(img, x0, x1, y, skin)
    img.put(cx - 1, top + 3, INK)
    img.put(cx + 1, top + 3, INK)
    img.put(cx, top + 5, darken(skin, 0.25))


def neck_shoulders(img, cx, top, skin, garment):
    """Neck at top..top+1, shoulders sloping out beneath."""
    img.hspan(cx - 1, cx + 1, top, darken(skin, 0.2))
    shaded_row(img, cx - 3, cx + 3, top + 1, garment)
    shaded_row(img, cx - 5, cx + 5, top + 2, garment)


def bodice(img, cx, y0, y1, garment):
    """Fitted torso: shoulders half-width 5 tapering to waist 3."""
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(1, y1 - y0)
        hw = 5 - int(t * 2)
        shaded_row(img, cx - hw, cx + hw, y, garment)


def arm(img, sx, sy, skin, garment, bend=0):
    """Upper arm 2px from the shoulder, elbow, forearm, hand."""
    side = 1 if sx > 0 else -1
    for y in range(sy, sy + 5):
        img.put(sx, y, darken(garment, 0.18) if side < 0 else warm(garment, 0.1))
    ex = sx + bend * side
    for y in range(sy + 5, sy + 9):
        img.put(ex, y, darken(garment, 0.25) if side < 0 else garment)
    img.put(ex, sy + 9, skin)


# ── the drifter · 18x28 ──────────────────────────────────────────

def drifter():
    img = Img(18, 28)
    cx = 9
    base = 24
    coat = hexc("2e1c14")
    skin = hexc("c09068")
    dust_strip(img, base + 1)
    # legs in the coat split + boots
    img.vspan(cx - 2, base - 5, base - 2, darken(coat, 0.35))
    img.vspan(cx + 1, base - 5, base - 2, darken(coat, 0.3))
    for bx in (cx - 3, cx + 1):
        img.hspan(bx, bx + 2, base - 1, hexc("241a10"))
        img.hspan(bx, bx + 2, base, hexc("241a10"))
        img.put(bx + 2, base, warm(hexc("241a10"), 0.3))
    # coat skirt — flares from the WAIST, split up the front
    for y in range(17, base - 1):
        t = (y - 17) / float(base - 18)
        hw = 3 + int(t * 3)
        shaded_row(img, cx - hw, cx + hw, y, coat)
        if y > 18:
            img.put(cx, y, CLEAR)                      # the split
            img.put(cx - 1, y, darken(coat, 0.4))
    # torso — shoulders to waist
    shaded_row(img, cx - 3, cx + 3, 11, coat)          # shoulder slope
    shaded_row(img, cx - 5, cx + 5, 12, coat)
    for y in range(13, 17):
        t = (y - 13) / 3.0
        hw = 5 - int(t * 2)
        shaded_row(img, cx - hw, cx + hw, y, coat)
    folds(img, cx - 3, cx + 3, 13, 16, coat, 9, 1)
    img.hspan(cx - 3, cx + 3, 17, darken(coat, 0.5))   # belt
    img.put(cx + 3, 17, SILVER)                        # the iron
    # arms — elbows bent slightly out, gloved hands at the hips
    for y in range(13, 17):
        img.put(cx - 5, y, darken(coat, 0.2))
        img.put(cx + 5, y, warm(coat, 0.12))
    img.put(cx - 5, 17, darken(coat, 0.35))            # forearm drop
    img.put(cx + 5, 17, coat)
    img.put(cx - 5, 18, hexc("3a2418"))                # gloves
    img.put(cx + 5, 18, hexc("4a2e1c"))
    # neck + kerchief
    img.put(cx, 10, darken(skin, 0.3))
    img.hspan(cx - 1, cx + 1, 10, BLOOD)
    # face — jaw lit under the brim shadow
    img.hspan(cx - 1, cx + 1, 7, darken(skin, 0.55))   # eyes in shadow
    img.hspan(cx - 1, cx + 1, 8, darken(skin, 0.4))
    img.hspan(cx - 1, cx + 1, 9, darken(skin, 0.15))   # lit jaw
    img.put(cx + 1, 9, warm(skin, 0.1))
    # the hat — wide brim above the shadow
    img.hspan(cx - 4, cx + 4, 6, INK)
    img.put(cx - 4, 6, darken(hexc("3a2c1c"), 0.1))
    img.put(cx + 4, 6, warm(hexc("3a2c1c"), 0.3))
    img.hspan(cx - 2, cx + 2, 5, INK)
    img.hspan(cx - 2, cx + 2, 4, INK)
    img.put(cx + 2, 4, warm(hexc("3a2c1c"), 0.2))
    img.hspan(cx - 2, cx + 2, 3, darken(INK, 0.0))
    return img


# ── the sisters · 28x44 ──────────────────────────────────────────

def sister_north():
    img = Img(28, 44)
    cx = 14
    base = 38
    shawl = hexc("8890a0")
    dress = hexc("5a5a68")
    skin = hexc("d8ccc0")
    dust_strip(img, base + 1)
    # skirt — flares from the WAIST
    for y in range(22, base + 1):
        t = (y - 22) / float(base - 22)
        hw = 3 + int(t * 4)
        shaded_row(img, cx - hw, cx + hw, y, dress)
    folds(img, cx - 4, cx + 4, 24, base - 1, dress, 11, 2)
    # bodice: shoulders to waist
    neck_shoulders(img, cx, 14, skin, dress)
    bodice(img, cx, 16, 21, dress)
    # head under the shawl hood
    head6(img, cx, 8, skin)
    for y in range(6, 9):                                # hood crown
        img.hspan(cx - 2, cx + 2, y, shawl)
    img.vspan(cx - 3, 8, 15, shawl)                      # hood sides
    img.vspan(cx + 3, 8, 15, warm(shawl, 0.1))
    img.hspan(cx - 4, cx + 4, 15, shawl)                 # shawl over shoulders
    img.hspan(cx - 5, cx + 5, 16, darken(shawl, 0.15))
    # arms out, the net draped between her hands
    for y in range(17, 24):
        img.put(cx - 6, y, darken(shawl, 0.2))
        img.put(cx + 6, y, warm(shawl, 0.1))
    img.put(cx - 6, 24, skin)                            # hands
    img.put(cx + 6, 24, warm(skin, 0.1))
    for x0, y0, x1, y1 in [(cx - 6, 25, cx + 6, 27), (cx - 6, 27, cx + 6, 25),
                           (cx - 4, 25, cx - 1, 29), (cx + 1, 29, cx + 4, 25)]:
        steps = max(abs(x1 - x0), abs(y1 - y0))
        for s in range(steps + 1):
            img.put(x0 + (x1 - x0) * s // max(1, steps),
                    y0 + (y1 - y0) * s // max(1, steps), SILVER)
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
    skin = hexc("d8b8a0")
    dust_strip(img, base + 1)
    # three shadows on the dust, disagreeing
    for dx0, dx1 in [(-11, -4), (-1, 1), (4, 11)]:
        for t in range(8):
            x = cx + dx0 + (dx1 - dx0) * t // 8
            if bayer(x, base + 1 + t // 4) < 0.6:
                img.put(x, base + 1 + t // 4, INK)
    # skirt from the waist — narrow, severe
    for y in range(22, base + 1):
        t = (y - 22) / float(base - 22)
        hw = 3 + int(t * 3)
        shaded_row(img, cx - hw, cx + hw, y, dress)
    folds(img, cx - 3, cx + 3, 24, base - 1, dress, 13, 2)
    # bodice + shoulders + neck
    neck_shoulders(img, cx, 14, skin, dress)
    bodice(img, cx, 16, 21, dress)
    # arms folded at the waist
    img.hspan(cx - 4, cx + 4, 20, darken(dress, 0.3))
    img.hspan(cx - 4, cx + 4, 21, lighten(dress, 0.1))
    img.put(cx - 4, 20, skin)                            # a hand at each elbow
    img.put(cx + 4, 21, warm(skin, 0.1))
    # head — dark hair pulled tight to a knot
    head6(img, cx, 8, skin)
    img.hspan(cx - 2, cx + 2, 7, INK)
    img.hspan(cx - 1, cx + 1, 8, INK)
    img.put(cx - 2, 9, INK)
    img.put(cx + 3, 9, INK)                              # the knot
    # the face-down mirror at her feet
    img.hspan(cx + 6, cx + 9, base, SILVER)
    img.hspan(cx + 6, cx + 9, base - 1, darken(SILVER, 0.35))
    return img


def sister_south():
    img = Img(28, 44)
    cx = 12
    base = 38
    dress = hexc("8a6838")
    chair = hexc("4a3018")
    skin = hexc("d0b898")
    dust_strip(img, base + 1)
    # the rocker
    for x0, y0, x1, y1 in [(4, base, 24, base - 3), (4, base - 3, 24, base)]:
        steps = 20
        for s in range(steps + 1):
            img.put(x0 + (x1 - x0) * s // steps,
                    y0 + (y1 - y0) * s // steps, chair)
    img.vspan(5, 12, base - 2, chair)                              # chair back
    img.vspan(6, 11, base - 2, darken(chair, 0.2))
    img.vspan(21, 27, base - 2, chair)                             # front leg
    # head — proper, with the grey bun
    head6(img, cx, 10, skin)
    img.hspan(cx - 1, cx + 1, 9, SILVER)                           # the bun
    img.put(cx - 2, 10, SILVER)
    img.put(cx, 8, SILVER)
    # neck + shoulders, seated slightly back
    img.hspan(cx - 1, cx + 1, 16, darken(skin, 0.2))
    shaded_row(img, cx - 3, cx + 3, 17, dress)
    shaded_row(img, cx - 4, cx + 4, 18, dress)
    # torso to the lap
    for y in range(19, 27):
        t = (y - 19) / 8.0
        hw = 4 - int(t)
        shaded_row(img, cx - hw, cx + hw + int(t * 2), y, dress)
    for y in range(27, 33):                                        # lap, forward
        shaded_row(img, cx - 3, cx + 7, y, dress)
    folds(img, cx - 2, cx + 6, 27, 32, dress, 15, 2)
    img.vspan(cx + 7, 33, base - 1, darken(dress, 0.25))           # shin
    img.put(cx + 7, base, hexc("241a10"))                          # shoe
    # resting arm along the lap
    img.hspan(cx - 3, cx + 2, 26, darken(dress, 0.3))
    img.put(cx - 3, 26, skin)
    # the offered water — arm extended, real, frightening
    img.hspan(cx + 4, cx + 8, 23, darken(dress, 0.2))              # forearm out
    img.put(cx + 9, 23, skin)                                      # her hand
    img.put(cx + 10, 23, SILVER)                                   # the cup
    img.put(cx + 10, 22, hexc("f4f0e8"))                           # the water's light
    return img


def sister_west():
    img = Img(28, 44)
    cx = 14
    base = 38
    dress = hexc("a08858")
    hair = hexc("241814")
    skin = hexc("e0c0a0")
    dust_strip(img, base + 1)
    # skirt from the waist — wind drifts the hem west
    for y in range(22, base + 1):
        t = (y - 22) / float(base - 22)
        hw = 3 + int(t * 4)
        lean = int(t * 2)
        shaded_row(img, cx - hw - lean, cx + hw - lean // 2, y, dress)
    folds(img, cx - 5, cx + 3, 24, base - 1, dress, 17, 3)
    # bodice + shoulders + neck
    neck_shoulders(img, cx, 14, skin, dress)
    bodice(img, cx, 16, 21, dress)
    # head with loose ink hair falling past the shoulders
    head6(img, cx, 8, skin)
    img.hspan(cx - 2, cx + 2, 7, hair)                             # crown
    img.hspan(cx - 2, cx + 1, 8, hair)                             # swept fringe
    for y in range(8, 20):                                         # the fall of it
        img.put(cx - 3, y, hair)
        if y > 10:
            img.put(cx - 4, y, darken(hair, 0.0) if h01(4, y, 3) < 0.7 else hair)
    img.put(cx + 3, 9, hair)                                       # a strand past the ear
    img.put(cx + 3, 10, hair)
    # left arm hangs; right hand on hip (elbow out)
    arm(img, cx - 5, 17, skin, dress, bend=0)
    img.put(cx + 5, 17, warm(dress, 0.1))
    img.put(cx + 6, 18, warm(dress, 0.1))                          # elbow out
    img.put(cx + 6, 19, dress)
    img.put(cx + 5, 20, skin)                                      # hand at the hip
    # the eighth point at her collar — the only violet in the figure
    img.put(cx, 16, WYRD)
    img.put(cx - 1, 15, WYRD)
    img.put(cx + 1, 15, WYRD)
    img.put(cx, 14, lighten(WYRD, 0.3))
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
