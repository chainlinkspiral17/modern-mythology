#!/usr/bin/env python3
"""Python mirror of EarthmanPortrait.gd (v4 FULL-FIGURE plates).

MUST BE KEPT IN LOCKSTEP with EarthmanPortrait.gd — when the
GDScript painter changes, change this mirror to match before
trusting a preview.

Per the user's reference images: painterly pixel art, silhouette-
first figures where costume, pose, and height carry identity, and
faces are mostly shadow with a glint. No more 40px face-drawing.

Each character stands in a dithered Parsan dusk — deep violet sky
banding down to an amber horizon, two moons, rust dunes. Species
read at a glance from the SILHOUETTE:
  human    · mid-height · jacket, boots, holster · 1940s
  kyrindi  · tall and slender · long robe, high silver collar
  delvanni · massive · FOUR ARMS visible at last · greatsword
  kelait   · small hooded cone · lit eyes in the hood shadow
  scarlet  · pale glow, hair streaming, feet not quite touching
Chrome kept minimal: corner brackets + the spectral ID stamp.

Canvas 36x60, displayed 2x (72x120).
"""
import os
from PIL import Image, ImageDraw

W, H = 36, 60
OUT = os.path.join(os.getcwd(), "earthman_plates.png")


def hexc(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16) / 255.0, int(s[2:4], 16) / 255.0,
            int(s[4:6], 16) / 255.0, 1.0)


# plate + dusk
VOID = hexc("100a16")
CORTEX = hexc("58305f")
AMBER = hexc("c86020")
STAR = hexc("f8c848")
CREAM = hexc("e9d090")
WHITE = hexc("f0f0f0")
SILVER = hexc("b8bcc8")
RED = hexc("c02020")
SKY = [hexc("100a16"), hexc("2a1428"), hexc("58223a"), hexc("9a4838"), hexc("d08448")]
GROUND = hexc("6a3024")
GROUND_DK = hexc("3a1a16")
GROUND_LT = hexc("8a4430")

HORIZON = 44
BASE = 54          # where boots touch dust


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

    def rect(self, x0, y0, w, h, c):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                self.put(x, y, c)


def dusk_bg(img, seed):
    # banded dusk down to the amber horizon
    for y in range(0, HORIZON):
        t = y / float(HORIZON)
        f = t * (len(SKY) - 1)
        i = min(int(f), len(SKY) - 2)
        c = SKY[i + 1] if (f - i) > bayer(0, y) * 0.999 else SKY[i]
        for x in range(W):
            fx = t * (len(SKY) - 1)
            img.px[y][x] = SKY[i + 1] if (fx - i) > bayer(x, y) else SKY[i]
    # stars in the high dusk
    for y in range(0, 16):
        for x in range(W):
            if h01(x, y, seed) < 0.012:
                img.px[y][x] = SILVER
    # the two moons
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx * dx + dy * dy <= 4:
                img.put(7 + dx, 7 + dy, CREAM)
    img.put(6, 6, WHITE)
    img.put(13, 11, SILVER)
    img.put(14, 11, SILVER)
    img.put(13, 12, SILVER)
    # ground — rust dunes
    for y in range(HORIZON, H):
        c = GROUND if y < BASE else GROUND_DK
        for x in range(W):
            img.px[y][x] = c
    # dune ridges, hash-placed
    for k in range(3):
        ry = HORIZON + 2 + k * 3 + int(h01(k, 3, seed) * 2)
        rx = int(h01(3, k, seed) * 20)
        img.hspan(rx, rx + 10 + k * 4, ry, GROUND_LT)
    img.hspan(0, W - 1, HORIZON, darken(GROUND, 0.35))
    # horizon glow kiss
    for x in range(W):
        if bayer(x, HORIZON - 1) < 0.5:
            img.px[HORIZON - 1][x] = SKY[4]


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
    for x in range(cx - half_w, cx + half_w + 1):
        if bayer(x, BASE + 1) < 0.7:
            img.put(x, BASE + 1, GROUND_DK)
    for x in range(cx - half_w + 2, cx + half_w - 1):
        img.put(x, BASE + 2, GROUND_DK)


def part(img, x0, x1, y0, y1, core):
    """A garment/limb block: shadow left column, lit right column."""
    sh = darken(core, 0.35)
    lt = warm(core)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if x == x1:
                img.put(x, y, lt)
            elif x == x0:
                img.put(x, y, sh)
            else:
                img.put(x, y, core)


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
    contact_shadow(img, cx, 6)
    # boots
    part(img, cx - 4, cx - 2, BASE - 3, BASE, hexc("241a14"))
    part(img, cx + 1, cx + 3, BASE - 3, BASE, hexc("241a14"))
    # legs
    part(img, cx - 4, cx - 2, top + 20, BASE - 4, pants)
    part(img, cx + 1, cx + 3, top + 20, BASE - 4, pants)
    # torso — jacket
    part(img, cx - 5, cx + 4, top + 9, top + 20, coat)
    img.hspan(cx - 4, cx + 3, top + 19, darken(coat, 0.45))       # belt
    # arms
    part(img, cx - 6, cx - 5, top + 10, top + 18, darken(coat, 0.12))
    part(img, cx + 5, cx + 6, top + 10, top + 18, coat)
    img.put(cx - 6, top + 19, skin)                                # hands
    img.put(cx + 6, top + 19, warm(skin))
    # holster glint at the right hip
    img.put(cx + 4, top + 21, SILVER)
    # head — small, face mostly shade, lit on the key side
    part(img, cx - 2, cx + 2, top, top + 6, skin)
    img.rect(cx - 2, top, 5, 2, hair)                              # 1940s cap of hair
    img.put(cx - 2, top + 2, darken(skin, 0.4))                    # shaded brow side
    img.put(cx - 1, top + 3, darken(skin, 0.3))
    img.put(cx + 1, top + 3, darken(hexc("241a14"), 0.0))          # eye shadow
    # collar
    img.hspan(cx - 2, cx + 2, top + 8, CREAM)
    if pid == "jack":
        img.put(cx, top, STAR)                                     # goggles up
        img.put(cx + 1, top, hexc("6a5a30"))
    if pid == "rocha":
        img.put(cx + 1, top + 3, WHITE)                            # glasses glint
        img.rect(cx - 8, top + 14, 3, 4, CREAM)                    # the notebook
        img.put(cx - 8, top + 15, hexc("3868c8"))                  # blue pen line
        part(img, cx - 5, cx + 4, top + 20, BASE - 6, coat)        # her coat runs long


def paint_kyrindi(img, pid, seed):
    cx = 18
    robes = [hexc("2a3450"), hexc("28304a"), hexc("323a58")]
    robe = robes[(seed >> 7) % 3]
    skins = [hexc("7a94c8"), hexc("8ea6d8"), hexc("6a82b8")]
    skin = skins[(seed >> 15) % 3]
    top = 12
    contact_shadow(img, cx, 5)
    # the long robe — a slender column flaring at the hem
    for y in range(top + 10, BASE + 1):
        t = (y - (top + 10)) / float(BASE - top - 10)
        hw = 3 + int(t * 3)
        img.hspan(cx - hw, cx + hw, y, robe)
        img.put(cx + hw, y, warm(robe))
        img.put(cx - hw, y, darken(robe, 0.35))
    # sleeves — thin arms folded into the robe
    part(img, cx - 5, cx - 4, top + 12, top + 22, darken(robe, 0.15))
    part(img, cx + 4, cx + 5, top + 12, top + 22, robe)
    img.put(cx + 5, top + 23, skin)                                # one visible hand
    # high silver collar
    img.hspan(cx - 3, cx + 3, top + 9, SILVER)
    img.hspan(cx - 2, cx + 2, top + 8, SILVER)
    # elongated head — pale blue, backswept
    part(img, cx - 2, cx + 1, top, top + 7, skin)
    img.vspan(cx - 3, top + 1, top + 5, darken(skin, 0.3))         # swept back of skull
    img.put(cx + 1, top + 3, hexc("18203a"))                       # eye, front
    img.put(cx + 2, top + 3, WHITE)                                # its light
    img.put(cx, top + 9, STAR)                                     # the song-sigil
    # the scholar's folio, on some
    if (seed >> 9) % 2 == 0:
        img.rect(cx - 8, top + 18, 3, 5, CREAM)
        img.vspan(cx - 8, top + 18, top + 22, darken(CREAM, 0.4))


def paint_delvanni(img, pid, seed):
    cx = 18
    armors = [hexc("4a3424"), hexc("3a3a2c"), hexc("55402a")]
    armor = armors[(seed >> 7) % 3]
    skins = [hexc("b06038"), hexc("a05430"), hexc("c07048")]
    skin = skins[(seed >> 15) % 3]
    top = 10
    contact_shadow(img, cx, 9)
    # the greatsword on the back — only hilt and tip show past the mass
    img.put(cx - 6, top + 8, SILVER)                               # grip above shoulder
    img.put(cx - 7, top + 7, SILVER)
    img.hspan(cx - 9, cx - 5, top + 6, darken(hexc("6a4a2c"), 0.1))  # crossguard
    img.put(cx - 7, top + 5, CREAM)                                # pommel
    img.put(cx + 8, top + 30, SILVER)                              # tip past the hip
    img.put(cx + 9, top + 32, SILVER)
    # legs — wide stance
    part(img, cx - 6, cx - 3, top + 28, BASE, darken(armor, 0.2))
    part(img, cx + 3, cx + 6, top + 28, BASE, darken(armor, 0.2))
    # torso — massive, tapering to the belt
    part(img, cx - 7, cx + 7, top + 12, top + 27, armor)
    img.hspan(cx - 6, cx + 6, top + 26, darken(armor, 0.45))       # belt
    # LOWER arm pair — hanging, bare rust skin
    part(img, cx - 9, cx - 8, top + 16, top + 26, skin)
    part(img, cx + 8, cx + 9, top + 16, top + 26, skin)
    # UPPER arm pair — crossed over the chest, bare skin
    img.hspan(cx - 6, cx + 1, top + 15, skin)
    img.hspan(cx - 1, cx + 6, top + 17, warm(skin))
    img.hspan(cx - 6, cx + 6, top + 16, darken(skin, 0.15))
    # shoulders
    img.hspan(cx - 8, cx - 5, top + 12, warm(armor))
    img.hspan(cx + 5, cx + 8, top + 12, warm(armor))
    # head — small on the mass, heavy brow, tusk
    part(img, cx - 2, cx + 2, top + 4, top + 11, skin)
    img.hspan(cx - 2, cx + 2, top + 6, darken(skin, 0.4))          # brow shelf
    img.put(cx + 1, top + 7, hexc("301810"))                       # deep-set eye
    img.put(cx + 3, top + 9, hexc("e8dcc0"))                       # the tusk
    img.put(cx + 3, top + 8, hexc("e8dcc0"))
    if (seed >> 10) % 2 == 0:                                      # topknot
        img.put(cx, top + 3, hexc("2a1a10"))
        img.put(cx, top + 2, hexc("2a1a10"))
    if (seed >> 12) % 3 == 0:                                      # war-paint
        img.hspan(cx - 2, cx + 2, top + 8, darken(hexc("7a3020"), 0.1))


def paint_kelait(img, pid, seed):
    cx = 18
    robes = [hexc("5a5048"), hexc("4c5248"), hexc("605444")]
    robe = robes[(seed >> 7) % 3]
    child = pid == "yr_kelait_child"
    top = 40 if child else 33
    contact_shadow(img, cx, 4)
    # the hooded cone — small, quiet
    for y in range(top, BASE + 1):
        t = (y - top) / float(BASE - top)
        hw = 1 + int(t * 4)
        img.hspan(cx - hw, cx + hw, y, robe)
        img.put(cx + hw, y, warm(robe))
        img.put(cx - hw, y, darken(robe, 0.35))
    # the hood shadow, and the eyes lit inside it
    hood_dk = darken(robe, 0.55)
    img.hspan(cx - 1, cx + 1, top + 1, hood_dk)
    img.hspan(cx - 1, cx + 1, top + 2, hood_dk)
    img.put(cx - 1, top + 2, CREAM)                                # the ancient eyes
    img.put(cx + 1, top + 2, CREAM)
    # a staff taller than they are, on some elders
    if not child and (seed >> 9) % 2 == 0:
        img.vspan(cx + 6, top - 8, BASE, hexc("6a4a2c"))
        img.put(cx + 6, top - 9, AMBER)                            # lantern ember
    # the child looks UP — one extra pixel of lifted face
    if child:
        img.put(cx, top, hexc("c8b498"))


def paint_scarlet(img, pid, seed):
    cx = 18
    gown = hexc("c03048")
    skin = hexc("f4ead8")
    top = 18
    # she casts light DOWN onto the dust, and no contact shadow
    for x in range(cx - 5, cx + 6):
        if bayer(x, BASE + 1) < 0.5:
            img.put(x, BASE + 1, warm(GROUND_LT, 0.3))
    # the gown — floating a pixel off the dust
    for y in range(top + 9, BASE):
        t = (y - (top + 9)) / float(BASE - top - 9)
        hw = 2 + int(t * 4)
        img.hspan(cx - hw, cx + hw, y, gown)
        img.put(cx + hw, y, lighten(gown, 0.3))
        img.put(cx - hw, y, darken(gown, 0.3))
    # hair streaming back as light — tapering ribbons, not a block
    for y in range(top - 2, top + 12):
        rel = y - (top - 2)
        stream = max(1, 5 - rel // 3) + (1 if h01(3, y, 77) < 0.5 else 0)
        x1 = cx - 3 - rel // 4
        img.hspan(x1 - stream, x1, y, CREAM)
    # head and shoulders — pale, lit from within
    part(img, cx - 2, cx + 2, top, top + 6, skin)
    img.put(cx + 1, top + 3, hexc("6a1828"))                       # her eye
    img.hspan(cx - 3, cx + 3, top + 7, lighten(gown, 0.2))
    # arms open slightly
    img.vspan(cx - 4, top + 9, top + 16, skin)
    img.vspan(cx + 4, top + 9, top + 16, WHITE)
    # three points of light leading her gaze
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
