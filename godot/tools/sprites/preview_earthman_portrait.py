#!/usr/bin/env python3
"""Python mirror of EarthmanPortrait.gd — species-driven NPC portraits.

MUST BE KEPT IN LOCKSTEP with EarthmanPortrait.gd — when the
GDScript painter changes, change this mirror to match before
trusting a preview. Renders the full roster contact sheet.

Astro-Cortex instrument-plate style: void ground, hairline violet
frame with corner ticks, figure lit like a specimen plate. Species
body plans from species.json / the design doc:
  human_earth · 1940s Pasadena
  kyrindi     · tall-and-blue, high silver collar, song-sigil
  delvanni    · four-armed rust-red, heavy brow, tusks, double shoulders
  kelait      · small, children-shaped, ancient eyes, hooded
  scarlet     · clothed in a light not of Parsa

Usage: preview_earthman_portrait.py  (writes earthman_portraits.png
into the current working directory)
"""
import os
from PIL import Image, ImageDraw

W, H = 40, 50
OUT = os.path.join(os.getcwd(), "earthman_portraits.png")


def hexc(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16) / 255.0, int(s[2:4], 16) / 255.0,
            int(s[4:6], 16) / 255.0, 1.0)


VOID = hexc("0b080e")
PANEL = hexc("291a33")
CORTEX = hexc("58305f")
AMBER = hexc("c86020")
STAR = hexc("f8c848")
CREAM = hexc("e9d090")
WHITE = hexc("f0f0f0")
SILVER = hexc("b8bcc8")
RED = hexc("c02020")


def darken(c, f):
    return (c[0] * (1 - f), c[1] * (1 - f), c[2] * (1 - f), 1.0)


def lighten(c, f):
    return (c[0] + (1 - c[0]) * f, c[1] + (1 - c[1]) * f, c[2] + (1 - c[2]) * f, 1.0)


def gd_hash(s):
    h = 5381
    for ch in s:
        h = (h * 33 + ord(ch)) & 0xFFFFFFFF
    return h


_BAYER4 = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]


def bayer(x, y):
    return (_BAYER4[(y % 4) * 4 + (x % 4)] + 0.5) / 16.0


class Img:
    def __init__(self, fill):
        self.px = [[fill] * W for _ in range(H)]

    def put(self, x, y, c):
        if 1 <= x < W - 1 and 1 <= y < H - 1:
            self.px[y][x] = c

    def hspan(self, x0, x1, y, c):
        for x in range(x0, x1 + 1):
            self.put(x, y, c)


def frame(img):
    # hairline instrument frame + corner ticks
    for x in range(W):
        img.px[0][x] = CORTEX
        img.px[H - 1][x] = CORTEX
    for y in range(H):
        img.px[y][0] = CORTEX
        img.px[y][W - 1] = CORTEX
    for tx, ty, dx, dy in [(2, 2, 1, 1), (W - 3, 2, -1, 1),
                           (2, H - 3, 1, -1), (W - 3, H - 3, -1, -1)]:
        img.put(tx, ty, AMBER)
        img.put(tx + dx, ty, AMBER)
        img.put(tx, ty + dy, AMBER)


def plate_wash(img):
    # faint panel gradient behind the figure — the instrument's glass
    for y in range(1, H - 1):
        t = 1.0 - abs(y - H * 0.40) / (H * 0.55)
        for x in range(1, W - 1):
            tx = 1.0 - abs(x - W / 2.0) / (W * 0.60)
            if t * tx * 0.8 > bayer(x, y):
                img.px[y][x] = PANEL


def base_figure(img, seed, skin, skin_sh, garment, head_w, head_top, head_h,
                narrow_jaw=True):
    cx = W // 2
    head_left = cx - head_w // 2
    head_right = head_left + head_w
    head_bot = min(head_top + head_h, H - 10)
    # shoulders + garment
    for y in range(head_bot + 2, H - 2):
        widen = min(15, 6 + (y - head_bot - 2) * 2)
        img.hspan(cx - widen, cx + widen, y, garment)
    # neck
    for y in range(head_bot - 1, head_bot + 3):
        img.hspan(cx - 3, cx + 3, y, skin_sh)
    # head
    for y in range(head_top, head_bot):
        x0, x1 = head_left, head_right
        if y == head_top:
            x0 += 3; x1 -= 3
        elif y == head_top + 1:
            x0 += 1; x1 -= 1
        fb = head_bot - 1 - y
        if narrow_jaw:
            if fb == 0: x0 += 4; x1 -= 4
            elif fb == 1: x0 += 2; x1 -= 2
            elif fb == 2: x0 += 1; x1 -= 1
        else:
            if fb == 0: x0 += 2; x1 -= 2
            elif fb == 1: x0 += 1; x1 -= 1
        for x in range(x0, x1):
            img.put(x, y, skin_sh if (x >= x1 - 3 and fb > 2) else skin)
    return cx, head_left, head_right, head_bot


def eyes(img, cx, eye_y, eye_dx, eye_c, hi_c, brow_c, wide=False):
    for side in (-1, 1):
        ex = cx + side * eye_dx - 1
        img.hspan(ex, ex + (2 if wide else 1) + 1, eye_y, eye_c)
        img.put(ex + 1, eye_y, hi_c)
        img.hspan(ex, ex + 2, eye_y - 2, brow_c)


def paint_human(img, pid, seed):
    skins = [hexc("e8c8a0"), hexc("d4a878"), hexc("c09068")]
    skin = skins[(seed >> 15) % 3]
    skin_sh = darken(skin, 0.22)
    hairs = [hexc("3a2a1c"), hexc("6a4a2c"), hexc("222020"), hexc("8a8078")]
    hair = hairs[(seed >> 17) % 4]
    garment = hexc("4a3c30") if (seed >> 5) % 2 == 0 else hexc("3a4250")
    head_w = 15 + (seed & 0x3)
    head_top = 9
    head_h = 19 + ((seed >> 3) & 0x3)
    cx, hl, hr, hb = base_figure(img, seed, skin, skin_sh, garment,
                                 head_w, head_top, head_h)
    # 1940s hair — side-parted, slick
    part = cx - 2 if (seed >> 9) % 2 == 0 else cx + 2
    for y in range(head_top - 1, head_top + 4):
        img.hspan(hl, hr - 1, y, hair)
    img.hspan(hl, hr - 1, head_top + 4, darken(hair, 0.3))
    for x in range(part, part + 2):
        img.put(x, head_top + 1, skin_sh)   # the part line
    eye_y = head_top + 8
    eye_dx = 3 + ((seed >> 6) & 0x1)
    eyes(img, cx, eye_y, eye_dx, hexc("2a2420"), WHITE, skin_sh)
    img.put(cx, eye_y + 4, skin_sh)                       # nose
    img.hspan(cx - 2, cx + 2, hb - 5, skin_sh)            # mouth
    if (seed >> 11) % 4 == 0:
        img.hspan(cx - 2, cx + 2, hb - 7, darken(hair, 0.1))   # mustache
    # collar + tie
    img.hspan(cx - 6, cx + 6, hb + 3, CREAM)
    img.put(cx, hb + 4, RED if (seed >> 13) % 2 == 0 else darken(garment, 0.3))
    img.put(cx, hb + 5, RED if (seed >> 13) % 2 == 0 else darken(garment, 0.3))
    if pid == "rocha":
        # her glasses — full rings
        for side in (-1, 1):
            ex = cx + side * eye_dx
            for dx2, dy2 in [(-1, -1), (0, -1), (1, -1), (-2, 0), (2, 0),
                             (-1, 1), (0, 1), (1, 1)]:
                img.put(ex + dx2, eye_y + dy2, hexc("222020"))
        img.hspan(cx - 1, cx + 1, eye_y - 1, hexc("222020"))
        # blue pen at the collar
        img.put(cx + 5, hb + 4, hexc("3868c8"))
    if pid == "jack":
        # goggles pushed up on the forehead
        img.hspan(hl + 3, hr - 4, head_top + 3, hexc("6a5a30"))
        img.put(cx - 3, head_top + 3, STAR)
        img.put(cx + 3, head_top + 3, STAR)


def paint_kyrindi(img, pid, seed):
    skins = [hexc("7a94c8"), hexc("8ea6d8"), hexc("6a82b8")]
    skin = skins[(seed >> 15) % 3]
    skin_sh = darken(skin, 0.25)
    garment = hexc("2a3450")
    head_w = 12 + (seed & 0x3)          # narrower
    head_top = 6                         # taller
    head_h = 24 + ((seed >> 3) & 0x3)
    cx, hl, hr, hb = base_figure(img, seed, skin, skin_sh, garment,
                                 head_w, head_top, head_h)
    # swept-back crest ridge, or a scholar's braid
    crest = darken(skin, 0.4)
    if (seed >> 9) % 2 == 0:
        for i in range(6):
            img.put(cx - 2 + i // 2, head_top - 2 - i // 3, crest)
            img.put(cx + 1 + i // 2, head_top - 1 - i // 3, crest)
    else:
        for y in range(head_top + 2, hb + 6):
            img.put(hr, y, crest)
            if y % 3 == 0:
                img.put(hr + 1, y, crest)
    eye_y = head_top + 10
    eye_dx = 3
    eyes(img, cx, eye_y, eye_dx, hexc("18203a"), SILVER, skin_sh)
    img.put(cx, eye_y + 5, skin_sh)
    img.hspan(cx - 1, cx + 1, hb - 5, skin_sh)
    # high silver collar
    img.hspan(cx - 5, cx + 5, hb + 2, SILVER)
    img.hspan(cx - 6, cx + 6, hb + 3, SILVER)
    img.hspan(cx - 7, cx + 7, hb + 4, darken(SILVER, 0.3))
    # the song-sigil at the throat
    img.put(cx, hb + 1, STAR)


def paint_delvanni(img, pid, seed):
    skins = [hexc("b06038"), hexc("a05430"), hexc("c07048")]
    skin = skins[(seed >> 15) % 3]
    skin_sh = darken(skin, 0.25)
    garments = [hexc("4a3424"), hexc("3a3a2c"), hexc("55402a")]
    garment = garments[(seed >> 7) % 3]
    head_w = 18 + (seed & 0x3)          # broad
    head_top = 10
    head_h = 18 + ((seed >> 3) & 0x3)
    cx, hl, hr, hb = base_figure(img, seed, skin, skin_sh, garment,
                                 head_w, head_top, head_h, narrow_jaw=False)
    # topknot, on some
    if (seed >> 10) % 2 == 0:
        img.hspan(cx - 1, cx + 1, head_top - 1, hexc("2a1a10"))
        img.hspan(cx - 1, cx + 1, head_top - 2, hexc("2a1a10"))
        img.put(cx, head_top - 3, hexc("2a1a10"))
    # heavy brow band
    eye_y = head_top + 8
    img.hspan(hl + 2, hr - 3, eye_y - 3, skin_sh)
    img.hspan(hl + 2, hr - 3, eye_y - 2, darken(skin, 0.35))
    # war-paint band across the eyes, on some
    if (seed >> 12) % 3 == 0:
        img.hspan(hl + 2, hr - 3, eye_y + 1, darken(hexc("7a3020"), 0.15))
    eyes(img, cx, eye_y, 4, hexc("301810"), AMBER, darken(skin, 0.35))
    img.put(cx, eye_y + 4, skin_sh)
    img.hspan(cx - 2, cx + 2, hb - 4, darken(skin, 0.35))
    # a kept scar, on some — remembered by name for six generations
    if (seed >> 20) % 3 == 1:
        for i in range(4):
            img.put(hl + 4 + i, eye_y + 2 + i, darken(skin, 0.45))
    # tusks — up from the jaw · length varies by line
    tusk = hexc("e8dcc0")
    tlen = 2 + ((seed >> 22) & 0x1)
    for t in range(tlen):
        img.put(cx - 4, hb - 4 - t, tusk)
        img.put(cx + 4, hb - 4 - t, tusk)
    # the second pair of shoulders — the four-arm read
    sh_y = hb + 6
    img.hspan(cx - 15, cx - 9, sh_y, skin)
    img.hspan(cx + 9, cx + 15, sh_y, skin)
    img.hspan(cx - 15, cx - 10, sh_y + 1, skin_sh)
    img.hspan(cx + 10, cx + 15, sh_y + 1, skin_sh)
    # chest strap
    for i in range(12):
        img.put(cx - 6 + i, hb + 3 + i // 3, darken(garment, 0.4))


def paint_kelait(img, pid, seed):
    skins = [hexc("c8b498"), hexc("b8a488"), hexc("d0c0a8")]
    skin = skins[(seed >> 15) % 3]
    skin_sh = darken(skin, 0.2)
    garments = [hexc("5a5048"), hexc("4c5248"), hexc("605444")]
    garment = garments[(seed >> 7) % 3]
    # small — head lower and smaller; the frame mostly holds quiet.
    # Children (Yr) are smaller still, and bare-headed.
    child = pid == "yr_kelait_child"
    head_w = (10 if child else 12) + (seed & 0x1)
    head_top = 20 if child else 16
    head_h = 11 if child else 14
    cx, hl, hr, hb = base_figure(img, seed, skin, skin_sh, garment,
                                 head_w, head_top, head_h)
    # hooded shawl arcing over the head — elders only
    hood = darken(garment, 0.15)
    if not child:
        for y in range(head_top - 3, hb + 2):
            t = y - (head_top - 3)
            reach = 2 + min(3, t // 3)
            img.hspan(hl - reach, hl - 1, y, hood)
            img.hspan(hr, hr + reach - 1, y, hood)
        for x in range(hl - 2, hr + 2):
            img.put(x, head_top - 3, hood)
            img.put(x, head_top - 2, hood)
        img.hspan(hl, hr - 1, head_top - 1, darken(hood, 0.25))
    else:
        # Yr looks up — a thin wash of sky he has never seen
        img.hspan(hl, hr - 1, head_top - 1, darken(skin, 0.35))
    # ancient eyes — large, round, lit
    eye_y = head_top + 6
    for side in (-1, 1):
        ex = cx + side * 3
        img.put(ex, eye_y, hexc("2a2018"))
        img.put(ex + 1, eye_y, hexc("2a2018"))
        img.put(ex, eye_y + 1, hexc("2a2018"))
        img.put(ex + 1, eye_y + 1, hexc("2a2018"))
        img.put(ex, eye_y, CREAM)
    img.hspan(cx - 1, cx + 1, hb - 3, skin_sh)
    # small folded hands at the hem
    img.hspan(cx - 2, cx + 2, H - 6, skin)
    img.hspan(cx - 2, cx + 2, H - 5, skin_sh)


def paint_scarlet(img, pid, seed):
    # clothed in a light not of Parsa
    glow = CREAM
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            d = ((x - W / 2.0) ** 2 / (W * 0.55) ** 2 +
                 (y - H * 0.42) ** 2 / (H * 0.50) ** 2) ** 0.5
            g = max(0.0, 1.0 - d)
            if g * 0.7 > bayer(x, y):
                img.px[y][x] = darken(hexc("8a2438"), (1.0 - g) * 0.4)
    skin = hexc("f4ead8")
    skin_sh = darken(skin, 0.12)
    garment = hexc("c03048")
    head_w = 13
    head_top = 9
    head_h = 20
    cx, hl, hr, hb = base_figure(img, seed, skin, skin_sh, garment,
                                 head_w, head_top, head_h)
    # hair as falling light
    for y in range(head_top - 2, hb + 8):
        img.put(hl - 1, y, glow)
        img.put(hr, y, glow)
        if y < head_top + 4:
            img.hspan(hl, hr - 1, y, glow)
    # features barely there
    eye_y = head_top + 8
    img.put(cx - 3, eye_y, hexc("6a1828"))
    img.put(cx + 3, eye_y, hexc("6a1828"))
    img.hspan(cx - 1, cx + 1, hb - 5, skin_sh)
    # the crown of the working — seven points of light
    for i, (sx, sy) in enumerate([(cx - 6, head_top - 4), (cx, head_top - 6),
                                  (cx + 6, head_top - 4)]):
        img.put(sx, sy, STAR)


PAINTERS = {
    "human_earth": paint_human, "kyrindi": paint_kyrindi,
    "delvanni": paint_delvanni, "kelait": paint_kelait,
    "scarlet_ambiguous": paint_scarlet,
}


def portrait(pid, species):
    img = Img(VOID)
    plate_wash(img)
    painter = PAINTERS.get(species, paint_human)
    painter(img, pid, gd_hash(pid))
    frame(img)
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
