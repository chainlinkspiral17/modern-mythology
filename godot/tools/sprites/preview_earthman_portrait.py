#!/usr/bin/env python3
"""Python mirror of EarthmanPortrait.gd.

MUST BE KEPT IN LOCKSTEP with EarthmanPortrait.gd — when the GDScript
painter changes, change this mirror to match before trusting a
preview.

Refinement over the first full-figure draft, per feedback ("too
blocky and basic"), taking the render language from the reference
boards:
  · 7-stop sky ramp, distant butte silhouettes for depth
  · organic silhouettes — sloped shoulders, tapered limbs, robe
    hems that jitter, no naked rectangles
  · 5-value material shading with Bayer-dithered transitions
    (deep shadow / mid / core / half-light / warm rim)
  · fabric fold lines inside every garment
  · ground speckle + wind streaks, soft dithered contact shadows
Canvas 36x60, displayed 2x.
"""
import os
from PIL import Image, ImageDraw

W, H = 36, 60
OUT = os.path.join(os.getcwd(), "earthman_plates.png")


def hexc(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16) / 255.0, int(s[2:4], 16) / 255.0,
            int(s[4:6], 16) / 255.0, 1.0)


VOID = hexc("100a16")
CORTEX = hexc("58305f")
AMBER = hexc("c86020")
STAR = hexc("f8c848")
CREAM = hexc("e9d090")
WHITE = hexc("f0f0f0")
SILVER = hexc("b8bcc8")
RED = hexc("c02020")
SKY = [hexc("100a16"), hexc("1e1022"), hexc("331632"), hexc("58223a"),
       hexc("7e3038"), hexc("a85038"), hexc("d08448")]
BUTTE = hexc("2c1220")
BUTTE2 = hexc("451a28")
GROUND = hexc("6a3024")
GROUND_DK = hexc("3a1a16")
GROUND_LT = hexc("8a4430")

HORIZON = 44
BASE = 54


def darken(c, f):
    return (c[0] * (1 - f), c[1] * (1 - f), c[2] * (1 - f), 1.0)


def lighten(c, f):
    return (c[0] + (1 - c[0]) * f, c[1] + (1 - c[1]) * f, c[2] + (1 - c[2]) * f, 1.0)


def warm(c, f=0.22):
    l = lighten(c, f)
    return (min(1.0, l[0] * 1.10), l[1], l[2] * 0.90, 1.0)


def gd_hash(s):
    h = 5381
    for ch in s:
        h = (h * 33 + ord(ch)) & 0xFFFFFFFF
    return h


_BAYER4 = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]


def bayer(x, y):
    return (_BAYER4[(y % 4) * 4 + (x % 4)] + 0.5) / 16.0


def h01(x, y, s):
    n = (x * 374761393 + y * 668265263 + s * 1442695041) & 0xFFFFFFFFFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFFFFFFFFFF
    n = n ^ (n >> 16)
    return (n & 0xFFFF) / 65536.0


class Img:
    def __init__(self, fill):
        self.px = [[fill] * W for _ in range(H)]

    def put(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            self.px[y][x] = c

    def hspan(self, x0, x1, y, c):
        for x in range(x0, x1 + 1):
            self.put(x, y, c)

    def vspan(self, x, y0, y1, c):
        for y in range(y0, y1 + 1):
            self.put(x, y, c)


def shaded_row(img, x0, x1, y, core):
    """One garment row with the 5-value ramp: deep shadow, dithered
    mid, core, dithered half-light, warm rim."""
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
    """Vertical fabric fold lines with breaks."""
    fold_c = darken(core, 0.30)
    for k in range(n):
        fx = x0 + 2 + int(h01(k, 5, seed) * max(1, (x1 - x0 - 3)))
        for y in range(y0 + 1, y1):
            if h01(fx, y, seed + k) < 0.75:
                img.put(fx, y, fold_c)


def dusk_bg(img, seed):
    for y in range(0, HORIZON):
        t = y / float(HORIZON)
        f = t * (len(SKY) - 1)
        i = min(int(f), len(SKY) - 2)
        for x in range(W):
            img.px[y][x] = SKY[i + 1] if (f - i) > bayer(x, y) else SKY[i]
    # stars
    for y in range(0, 18):
        for x in range(W):
            if h01(x, y, seed) < 0.012:
                img.px[y][x] = SILVER
    # moons
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx * dx + dy * dy <= 4:
                img.put(7 + dx, 7 + dy, CREAM)
    img.put(6, 6, WHITE)
    img.put(13, 11, SILVER)
    img.put(14, 11, SILVER)
    img.put(13, 12, SILVER)
    # distant buttes — flat-topped silhouettes on the horizon
    b1x = 2 + int(h01(1, 9, seed) * 8)
    for y in range(HORIZON - 7, HORIZON):
        spread = min(3, (y - (HORIZON - 7)) // 2)
        img.hspan(b1x - spread, b1x + 5 + spread, y, BUTTE)
    b2x = 24 + int(h01(9, 1, seed) * 8)
    for y in range(HORIZON - 4, HORIZON):
        spread = min(2, (y - (HORIZON - 4)) // 2)
        img.hspan(b2x - spread, b2x + 3 + spread, y, BUTTE2)
    # ground
    for y in range(HORIZON, H):
        c = GROUND if y < BASE else GROUND_DK
        for x in range(W):
            img.px[y][x] = c
    # dune ridges + speckle + wind streaks
    for k in range(3):
        ry = HORIZON + 2 + k * 3 + int(h01(k, 3, seed) * 2)
        rx = int(h01(3, k, seed) * 20)
        img.hspan(rx, rx + 10 + k * 4, ry, GROUND_LT)
        img.hspan(rx + 2, rx + 8 + k * 4, ry + 1, darken(GROUND_LT, 0.15))
    for y in range(HORIZON + 1, H):
        for x in range(W):
            if h01(x, y, seed + 31) < 0.05:
                img.px[y][x] = darken(GROUND, 0.25)
            elif h01(x, y, seed + 32) < 0.03:
                img.px[y][x] = GROUND_LT
    img.hspan(0, W - 1, HORIZON, darken(GROUND, 0.35))
    for x in range(W):
        if bayer(x, HORIZON - 1) < 0.5:
            img.px[HORIZON - 1][x] = SKY[6]


def plate_chrome(img, seed):
    for cx0, cy0, dx, dy in [(1, 1, 1, 1), (W - 2, 1, -1, 1),
                             (1, H - 2, 1, -1), (W - 2, H - 2, -1, -1)]:
        for i in range(4):
            img.px[cy0][cx0 + dx * i] = CORTEX
            img.px[cy0 + dy * i][cx0] = CORTEX
    code_cols = [AMBER, STAR, SILVER, CORTEX, hexc("58a068"), RED]
    for i in range(6):
        c = code_cols[(seed >> (i * 4)) % len(code_cols)]
        for t in range(2):
            img.px[2][W - 15 + i * 2 + t] = c


def contact_shadow(img, cx, half_w):
    for r, hw in [(1, half_w), (2, half_w - 2)]:
        for x in range(cx - hw, cx + hw + 1):
            if bayer(x, BASE + r) < (0.75 - r * 0.2):
                img.put(x, BASE + r, GROUND_DK)


# ── figures ──────────────────────────────────────────────────────

def paint_human(img, pid, seed):
    cx = 18
    coats = [hexc("2c2233"), hexc("332a24"), hexc("22282e")]
    coat = coats[(seed >> 7) % 3]
    pants = darken(coat, 0.25)
    skins = [hexc("e8c8a0"), hexc("d4a878"), hexc("c09068")]
    skin = skins[(seed >> 15) % 3]
    hairs = [hexc("2a1e14"), hexc("4a3420"), hexc("1a1818"), hexc("6a6058")]
    hair = hairs[(seed >> 17) % 4]
    top = 20
    long_coat = pid == "rocha"
    contact_shadow(img, cx, 6)
    # boots — with a lit toe
    for bx in (cx - 4, cx + 1):
        for y in range(BASE - 2, BASE + 1):
            shaded_row(img, bx, bx + 2, y, hexc("241a14"))
        img.put(bx + 3, BASE, warm(hexc("241a14"), 0.35))
    # legs — tapering
    if not long_coat:
        for y in range(top + 20, BASE - 2):
            t = (y - top - 20) / float(BASE - 2 - top - 20)
            wdt = 2 if t < 0.6 else 1
            shaded_row(img, cx - 3 - (wdt - 1), cx - 2, y, pants)
            shaded_row(img, cx + 2, cx + 3 + (wdt - 1), y, pants)
    # torso — shoulders slope in over two rows
    for y in range(top + 9, top + 21):
        rel = y - (top + 9)
        wdt = 3 + min(2, rel)            # 3 → 5 half-width
        shaded_row(img, cx - wdt, cx + wdt - 1, y, coat)
    folds(img, cx - 4, cx + 3, top + 11, top + 19, coat, seed, 2)
    img.hspan(cx - 4, cx + 3, top + 19, darken(coat, 0.5))          # belt
    img.put(cx, top + 19, STAR)                                     # buckle
    if long_coat:
        for y in range(top + 20, BASE - 4):
            wdt = 4 + (1 if h01(2, y, seed) < 0.3 else 0)           # hem jitter
            shaded_row(img, cx - wdt, cx + wdt - 1, y, coat)
        folds(img, cx - 4, cx + 3, top + 20, BASE - 5, coat, seed + 1, 2)
    # arms — 1px shoulder step out then hang
    for y in range(top + 10, top + 19):
        img.put(cx - 6, y, darken(coat, 0.3) if y > top + 12 else darken(coat, 0.15))
        img.put(cx + 5, y, warm(coat) if y < top + 14 else lighten(coat, 0.1))
    img.put(cx - 6, top + 19, skin)
    img.put(cx + 5, top + 19, warm(skin))
    img.put(cx + 4, top + 21, SILVER)                               # holster glint
    # head — rounded, TWO eyes, a mouth, a neck
    for y in range(top, top + 7):
        x0, x1 = cx - 2, cx + 2
        if y == top or y == top + 6:
            x0 += 1; x1 -= 1
        shaded_row(img, x0, x1, y, skin)
    img.hspan(cx - 1, cx + 1, top, hair)                            # rounded hair cap
    img.hspan(cx - 2, cx + 2, top + 1, hair)
    img.put(cx - 2, top + 2, darken(hair, 0.2))                     # temple
    img.put(cx - 1, top + 3, hexc("241a14"))                        # eyes — both of them
    img.put(cx + 1, top + 3, hexc("241a14"))
    img.put(cx, top + 5, darken(skin, 0.3))                         # mouth
    img.hspan(cx - 1, cx + 1, top + 7, darken(skin, 0.25))          # neck
    img.hspan(cx - 2, cx + 2, top + 8, CREAM)                       # collar
    if pid == "jack":
        img.put(cx, top, STAR)
        img.put(cx + 1, top, hexc("6a5a30"))
    if pid == "rocha":
        img.put(cx + 1, top + 3, WHITE)
        for dy in range(4):                                         # the notebook
            img.hspan(cx - 8, cx - 6, top + 14 + dy, CREAM if dy % 2 == 0 else darken(CREAM, 0.12))
        img.put(cx - 8, top + 15, hexc("3868c8"))


def paint_kyrindi(img, pid, seed):
    cx = 18
    robes = [hexc("2a3450"), hexc("28304a"), hexc("323a58")]
    robe = robes[(seed >> 7) % 3]
    skins = [hexc("7a94c8"), hexc("8ea6d8"), hexc("6a82b8")]
    skin = skins[(seed >> 15) % 3]
    top = 12
    contact_shadow(img, cx, 5)
    # the robe — slender, flaring, hem jitter, sheen fold
    for y in range(top + 10, BASE + 1):
        t = (y - (top + 10)) / float(BASE - top - 10)
        hw = 3 + int(t * 3)
        if y > BASE - 3 and h01(1, y, seed) < 0.4:
            hw += 1                                                  # hem ripple
        shaded_row(img, cx - hw, cx + hw, y, robe)
    folds(img, cx - 3, cx + 3, top + 12, BASE - 2, robe, seed, 3)
    # sheen — one lit fold catching the horizon
    img.vspan(cx + 2, top + 14, BASE - 6, lighten(robe, 0.18))
    # sleeves
    for y in range(top + 12, top + 23):
        img.put(cx - 5, y, darken(robe, 0.35))
        img.put(cx + 5, y, warm(robe))
    img.put(cx + 5, top + 23, skin)
    # high silver collar — lit right
    img.hspan(cx - 3, cx + 3, top + 9, SILVER)
    img.hspan(cx - 2, cx + 2, top + 8, SILVER)
    img.put(cx + 3, top + 9, WHITE)
    # elongated head — rounded crown, backswept
    for y in range(top, top + 8):
        x0, x1 = cx - 2, cx + 1
        if y == top:
            x0 += 1
        shaded_row(img, x0, x1, y, skin)
    img.vspan(cx - 3, top + 2, top + 6, darken(skin, 0.3))
    img.put(cx - 3, top + 1, darken(skin, 0.4))
    img.put(cx - 1, top + 4, hexc("18203a"))                        # both eyes
    img.put(cx + 1, top + 4, hexc("18203a"))
    img.put(cx + 1, top + 3, WHITE)
    img.put(cx, top + 6, darken(skin, 0.3))                         # mouth
    img.put(cx, top + 9, STAR)
    if (seed >> 9) % 2 == 0:                                        # the folio
        for dy in range(5):
            img.hspan(cx - 8, cx - 6, top + 18 + dy, CREAM if dy % 2 == 0 else darken(CREAM, 0.12))
        img.vspan(cx - 8, top + 18, top + 22, darken(CREAM, 0.4))


def paint_delvanni(img, pid, seed):
    cx = 18
    armors = [hexc("4a3424"), hexc("3a3a2c"), hexc("55402a")]
    armor = armors[(seed >> 7) % 3]
    skins = [hexc("b06038"), hexc("a05430"), hexc("c07048")]
    skin = skins[(seed >> 15) % 3]
    top = 10
    contact_shadow(img, cx, 9)
    # greatsword — hilt over the shoulder, tip past the hip
    img.put(cx - 6, top + 8, SILVER)
    img.put(cx - 7, top + 7, SILVER)
    img.hspan(cx - 9, cx - 5, top + 6, darken(hexc("6a4a2c"), 0.1))
    img.put(cx - 7, top + 5, CREAM)
    img.put(cx + 8, top + 30, SILVER)
    img.put(cx + 9, top + 32, SILVER)
    # legs — thick, tapering
    for y in range(top + 28, BASE + 1):
        t = (y - top - 28) / float(BASE - top - 28)
        wdt = 2 if t < 0.7 else 1
        shaded_row(img, cx - 5 - (wdt - 1), cx - 3, y, darken(armor, 0.2))
        shaded_row(img, cx + 3, cx + 5 + (wdt - 1), y, darken(armor, 0.2))
    # torso — trapezoid: huge shoulders tapering to the belt
    for y in range(top + 12, top + 28):
        rel = y - (top + 12)
        wdt = 8 - min(2, rel // 6)
        shaded_row(img, cx - wdt + 1, cx + wdt - 1, y, armor)
    # armor plate seams
    img.hspan(cx - 6, cx + 6, top + 20, darken(armor, 0.35))
    img.hspan(cx - 5, cx + 5, top + 23, darken(armor, 0.3))
    img.hspan(cx - 6, cx + 6, top + 26, darken(armor, 0.5))         # belt
    img.put(cx, top + 26, STAR)
    # sloped shoulder pads
    img.hspan(cx - 8, cx - 5, top + 12, warm(armor))
    img.hspan(cx + 5, cx + 8, top + 12, warm(armor))
    img.hspan(cx - 7, cx - 5, top + 11, warm(armor, 0.1))
    img.hspan(cx + 5, cx + 7, top + 11, warm(armor, 0.1))
    # LOWER arms — hanging, muscled: 2px with shade split
    for y in range(top + 16, top + 27):
        img.put(cx - 9, y, darken(skin, 0.3))
        img.put(cx - 8, y, skin)
        img.put(cx + 8, y, skin)
        img.put(cx + 9, y, warm(skin))
    img.put(cx - 8, top + 27, darken(skin, 0.2))                    # fists
    img.put(cx + 9, top + 27, warm(skin, 0.1))
    # UPPER arms — crossed, with elbow bulges
    img.hspan(cx - 6, cx + 1, top + 15, skin)
    img.hspan(cx - 6, cx + 6, top + 16, darken(skin, 0.15))
    img.hspan(cx - 1, cx + 6, top + 17, warm(skin))
    img.put(cx - 7, top + 16, darken(skin, 0.3))                    # elbows out
    img.put(cx + 7, top + 16, warm(skin, 0.1))
    # head — rounded, heavy brow, tusk
    for y in range(top + 4, top + 12):
        x0, x1 = cx - 2, cx + 2
        if y == top + 4:
            x0 += 1; x1 -= 1
        shaded_row(img, x0, x1, y, skin)
    img.hspan(cx - 2, cx + 2, top + 6, darken(skin, 0.45))
    img.put(cx - 1, top + 7, hexc("301810"))                        # both deep-set eyes
    img.put(cx + 1, top + 7, hexc("301810"))
    img.hspan(cx - 1, cx + 1, top + 10, darken(skin, 0.35))         # the hard mouth
    img.put(cx + 3, top + 9, hexc("e8dcc0"))
    img.put(cx + 3, top + 8, hexc("e8dcc0"))
    img.put(cx - 3, top + 9, hexc("e8dcc0"))                        # matched tusks
    img.put(cx - 3, top + 8, hexc("e8dcc0"))
    if (seed >> 10) % 2 == 0:
        img.put(cx, top + 3, hexc("2a1a10"))
        img.put(cx, top + 2, hexc("2a1a10"))
    if (seed >> 12) % 3 == 0:
        img.hspan(cx - 2, cx + 2, top + 8, darken(hexc("7a3020"), 0.1))


def paint_kelait(img, pid, seed):
    cx = 18
    robes = [hexc("5a5048"), hexc("4c5248"), hexc("605444")]
    robe = robes[(seed >> 7) % 3]
    child = pid == "yr_kelait_child"
    top = 40 if child else 33
    contact_shadow(img, cx, 4)
    # the hooded cone — rounded, hem jitter
    for y in range(top, BASE + 1):
        t = (y - top) / float(BASE - top)
        hw = 1 + int(t * 4)
        if y > BASE - 2 and h01(1, y, seed) < 0.4:
            hw += 1
        shaded_row(img, cx - hw, cx + hw, y, robe)
    folds(img, cx - 2, cx + 2, top + 4, BASE - 1, robe, seed, 2)
    # hood shadow + the eyes
    hood_dk = darken(robe, 0.55)
    img.hspan(cx - 1, cx + 1, top + 1, hood_dk)
    img.hspan(cx - 1, cx + 1, top + 2, hood_dk)
    img.put(cx - 1, top + 2, CREAM)
    img.put(cx + 1, top + 2, CREAM)
    img.put(cx, top, warm(robe))                                    # hood rim light
    if not child and (seed >> 9) % 2 == 0:
        img.vspan(cx + 6, top - 8, BASE, hexc("6a4a2c"))
        img.put(cx + 5, top - 4, darken(hexc("6a4a2c"), 0.3))       # hand on staff
        img.put(cx + 6, top - 9, AMBER)
    if child:
        img.put(cx, top, hexc("c8b498"))


def paint_scarlet(img, pid, seed):
    cx = 18
    gown = hexc("c03048")
    skin = hexc("f4ead8")
    top = 18
    # light cast down, no contact shadow
    for x in range(cx - 5, cx + 6):
        if bayer(x, BASE + 1) < 0.5:
            img.put(x, BASE + 1, warm(GROUND_LT, 0.3))
    # a faint glow halo in the air around her
    for y in range(top - 3, BASE):
        for x in range(cx - 8, cx + 9):
            d = abs(x - cx) + abs(y - (top + 12)) // 3
            if d in (8, 9) and bayer(x, y) < 0.2:
                img.put(x, y, hexc("7a2438"))
    # the gown — flaring, folds, floating
    for y in range(top + 9, BASE):
        t = (y - (top + 9)) / float(BASE - top - 9)
        hw = 2 + int(t * 4)
        if y > BASE - 4 and h01(1, y, seed) < 0.4:
            hw += 1
        shaded_row(img, cx - hw, cx + hw, y, gown)
    folds(img, cx - 3, cx + 3, top + 12, BASE - 2, gown, seed, 2)
    # hair streaming back as tapered light
    for y in range(top - 2, top + 12):
        rel = y - (top - 2)
        stream = max(1, 5 - rel // 3) + (1 if h01(3, y, 77) < 0.5 else 0)
        x1 = cx - 3 - rel // 4
        img.hspan(x1 - stream, x1, y, CREAM)
        if h01(5, y, 78) < 0.4:
            img.put(x1 - stream - 1, y, darken(CREAM, 0.15))         # ribbon tips
    # head — rounded, lit from within
    for y in range(top, top + 7):
        x0, x1 = cx - 2, cx + 2
        if y == top:
            x0 += 1; x1 -= 1
        shaded_row(img, x0, x1, y, skin)
    img.put(cx - 1, top + 3, hexc("6a1828"))                        # both her eyes
    img.put(cx + 1, top + 3, hexc("6a1828"))
    img.put(cx, top + 5, darken(skin, 0.2))                         # her mouth
    img.hspan(cx - 3, cx + 3, top + 7, lighten(gown, 0.2))
    img.vspan(cx - 4, top + 9, top + 16, skin)
    img.vspan(cx + 4, top + 9, top + 16, WHITE)
    img.put(cx - 4, top + 17, skin)                                 # open hands
    img.put(cx + 4, top + 17, WHITE)
    for sx, sy in [(cx + 8, top - 4), (cx + 10, top), (cx + 9, top + 4)]:
        img.put(sx, sy, STAR)


PAINTERS = {
    "human_earth": paint_human, "kyrindi": paint_kyrindi,
    "delvanni": paint_delvanni, "kelait": paint_kelait,
    "scarlet_ambiguous": paint_scarlet,
}


def portrait(pid, species):
    seed = gd_hash(pid)
    img = Img(VOID)
    dusk_bg(img, seed)
    PAINTERS.get(species, paint_human)(img, pid, seed)
    plate_chrome(img, seed)
    return img


ROSTER = [
    ("jack", "human_earth"), ("rocha", "human_earth"),
    ("ronson_hubbard_analog", "human_earth"), ("j_f_astrocortex_colleague", "human_earth"),
    ("sara_nai", "kyrindi"), ("king_vessel_kyrindi", "kyrindi"),
    ("arentha_high_scribe", "kyrindi"),
    ("hel_velli", "delvanni"), ("thar_krai_tam_overseer", "delvanni"),
    ("dalev_overseer", "delvanni"), ("murg_kel_karai", "delvanni"),
    ("keran_dead_cousin", "delvanni"), ("wife_of_hel_velli_never_named", "delvanni"),
    ("mother_kanel", "kelait"), ("yr_kelait_child", "kelait"),
    ("jethers_specific_kelait_musician", "kelait"),
    ("scarlet_woman", "scarlet_ambiguous"),
]


def main():
    scale = 4
    cols = 6
    cw, ch = W * scale + 8, H * scale + 22
    rows = (len(ROSTER) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cw + 8, rows * ch + 8), (14, 11, 16))
    draw = ImageDraw.Draw(sheet)
    for i, (pid, sp) in enumerate(ROSTER):
        img = portrait(pid, sp)
        tile = Image.new("RGB", (W, H))
        for y in range(H):
            for x in range(W):
                c = img.px[y][x]
                tile.putpixel((x, y), tuple(int(round(min(max(v, 0), 1) * 255)) for v in c[:3]))
        tile = tile.resize((W * scale, H * scale), Image.NEAREST)
        gx = 8 + (i % cols) * cw
        gy = 8 + (i // cols) * ch
        sheet.paste(tile, (gx, gy))
        draw.text((gx, gy + H * scale + 2), pid[:22], fill=(205, 195, 180))
        draw.text((gx, gy + H * scale + 11), sp, fill=(130, 120, 130))
    sheet.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
