#!/usr/bin/env python3
"""Python mirror of EarthmanPortrait.gd (v3 PROFILES).

MUST BE KEPT IN LOCKSTEP with EarthmanPortrait.gd — when the
GDScript painter changes, change this mirror to match before
trusting a preview.

Fey Faire draws front-facing symmetric busts. These are SIDE
PROFILES on instrument plates — anthropological specimen drawings,
faces turned toward the key light. The species live in the
silhouette: the Kyrindi's long backswept cranium, the Delvanni's
massive jaw and tusk, the Kelait's small hooded curve, the human's
1940s haircut and straight nose, the Scarlet Woman's light
streaming behind her.

Chrome kept from v2 (already good): graticule + meridian, open
registration brackets, calibration ticks, spectral ID stamp.
"""
import os
from PIL import Image, ImageDraw

W, H = 40, 50
OUT = os.path.join(os.getcwd(), "earthman_profiles.png")


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
GRID = hexc("18101f")
MERIDIAN = hexc("241a30")
TICK = hexc("6a5878")


def darken(c, f):
    return (c[0] * (1 - f), c[1] * (1 - f), c[2] * (1 - f), 1.0)


def lighten(c, f):
    return (c[0] + (1 - c[0]) * f, c[1] + (1 - c[1]) * f, c[2] + (1 - c[2]) * f, 1.0)


def lit(c):
    l = lighten(c, 0.20)
    return (min(1.0, l[0] * 1.08), l[1], l[2] * 0.92, 1.0)


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


def plate_bg(img):
    for y in range(H):
        for x in range(W):
            if x % 8 == 4 or y % 8 == 4:
                img.px[y][x] = GRID
    for x in range(W):
        img.px[17][x] = MERIDIAN
    for i in range(-2, 3):
        img.px[10][W // 2 + i] = MERIDIAN
        img.px[10 + i][W // 2] = MERIDIAN


def plate_chrome(img, seed):
    for cx0, cy0, dx, dy in [(1, 1, 1, 1), (W - 2, 1, -1, 1),
                             (1, H - 2, 1, -1), (W - 2, H - 2, -1, -1)]:
        for i in range(5):
            img.px[cy0][cx0 + dx * i] = CORTEX
            img.px[cy0 + dy * i][cx0] = CORTEX
    for x in range(4, W - 4, 4):
        th = 2 if x % 8 == 0 else 1
        for t in range(th):
            img.px[H - 2 - t][x] = TICK
    for y in range(6, H - 6, 4):
        img.px[y][1] = TICK
        if y % 8 == 6:
            img.px[y][2] = TICK
    code_cols = [AMBER, STAR, SILVER, CORTEX, hexc("58a068"), RED]
    for i in range(6):
        c = code_cols[(seed >> (i * 4)) % len(code_cols)]
        for t in range(2):
            img.px[2][W - 16 + i * 2 + t] = c
            img.px[3][W - 16 + i * 2 + t] = c


# ── profile machinery ────────────────────────────────────────────
# The face looks RIGHT (into the key light). spec keys:
#   fx        · face line (forehead extent, rightmost)
#   bx        · back-of-skull line (leftmost)
#   head_top  · first skull row
#   crown     · rows of crown slope at the top
#   brow_rel / eye_rel / nose_rel / nose_len / mouth_rel / chin_rel
#   jaw_rel / jaw_slope · where the jaw starts sloping forward
#   head_bot  · last row of the head (chin tip region)

def build_profile(spec):
    face = {}
    backs = {}
    ht, hb = spec["head_top"], spec["head_bot"]
    fx, bx = spec["fx"], spec["bx"]
    crown = spec.get("crown", 4)
    for y in range(ht, hb + 1):
        rel = y - ht
        x = fx
        if rel < crown:
            x = fx - (crown - rel) * spec.get("crown_slope", 2)
        if rel == spec["brow_rel"]:
            x = fx + 1
        if spec["brow_rel"] < rel <= spec["eye_rel"] + 1:
            x = fx - 1
        nr = spec["nose_rel"]
        if nr <= rel < nr + 3:
            x = fx + [2, spec["nose_len"], 1][rel - nr]
        if rel == spec["mouth_rel"]:
            x = fx
        if rel == spec["mouth_rel"] + 1:
            x = fx - 1
        if rel == spec["mouth_rel"] + 2:
            x = fx
        if rel >= spec["chin_rel"]:
            x = fx - (rel - spec["chin_rel"]) * spec.get("chin_slope", 1)
        face[y] = x
        b = bx
        if rel < 4:
            b = bx + (4 - rel) * 2
        jr = spec.get("jaw_rel", spec["chin_rel"] - 2)
        if rel > jr:
            b = bx + (rel - jr) * spec.get("jaw_slope", 2)
        backs[y] = b
    return face, backs


def fill_profile(img, face, backs, skin, skin_sh, skin_lt):
    for y in face:
        b, f = backs[y], face[y]
        if f <= b:
            continue
        for x in range(b, f + 1):
            if x >= f - 1:
                img.put(x, y, skin_lt)
            elif x <= b + 1:
                img.put(x, y, skin_sh)
            else:
                img.put(x, y, skin)


def profile_features(img, spec, skin, skin_sh, eye_c):
    """Eye, nostril, mouth line, ear — shared profile furniture."""
    ht = spec["head_top"]
    fx = spec["fx"]
    bx = spec["bx"]
    eye_y = ht + spec["eye_rel"]
    ex = fx - 5
    img.put(ex, eye_y, eye_c)
    img.put(ex + 1, eye_y, eye_c)
    img.put(ex + 1, eye_y - 1, skin_sh)          # lid
    img.put(ex + 2, eye_y, WHITE)                # the light in it
    img.put(fx + 1, ht + spec["nose_rel"] + 2, skin_sh)   # nostril
    my = ht + spec["mouth_rel"] + 1
    img.hspan(fx - 4, fx - 1, my, skin_sh)       # mouth line
    # ear — back-center of the skull at eye height
    ear_x = bx + (fx - bx) // 2 - 2
    img.put(ear_x, eye_y, skin_sh)
    img.put(ear_x + 1, eye_y, skin_sh)
    img.put(ear_x, eye_y + 1, skin_sh)
    img.put(ear_x + 1, eye_y + 1, skin)
    img.put(ear_x, eye_y + 2, skin_sh)


def neck_and_shoulders(img, spec, skin, skin_sh, garment):
    hb = spec["head_bot"]
    bx = spec["bx"]
    fx = spec["fx"]
    ncx = bx + (fx - bx) // 2
    for y in range(hb - 3, hb + 4):
        img.hspan(ncx - 2, ncx + 3, y, skin_sh)
    for y in range(hb + 3, H - 3):
        widen = min(17, 6 + (y - hb - 3) * 3)
        img.hspan(ncx - widen, ncx + widen, y, garment)
        img.hspan(ncx + max(3, widen - 4), ncx + widen, y, lighten(garment, 0.14))
        img.hspan(ncx - widen, ncx - widen + 2, y, darken(garment, 0.25))
    return ncx


# ── species painters ─────────────────────────────────────────────

def paint_human(img, pid, seed):
    skins = [hexc("e8c8a0"), hexc("d4a878"), hexc("c09068")]
    skin = skins[(seed >> 15) % 3]
    skin_sh = darken(skin, 0.22)
    skin_lt = lit(skin)
    hairs = [hexc("3a2a1c"), hexc("6a4a2c"), hexc("222020"), hexc("8a8078")]
    hair = hairs[(seed >> 17) % 4]
    garment = hexc("4a3c30") if (seed >> 5) % 2 == 0 else hexc("3a4250")
    spec = {
        "fx": 30 + (seed & 0x1), "bx": 10 - ((seed >> 1) & 0x1),
        "head_top": 6, "head_bot": 31, "crown": 4,
        "brow_rel": 9, "eye_rel": 11,
        "nose_rel": 13, "nose_len": 3 + ((seed >> 3) & 0x1),
        "mouth_rel": 18, "chin_rel": 21, "chin_slope": 1,
        "jaw_rel": 19, "jaw_slope": 2,
    }
    face, backs = build_profile(spec)
    fill_profile(img, face, backs, skin, skin_sh, skin_lt)
    ncx = neck_and_shoulders(img, spec, skin, skin_sh, garment)
    # 1940s cut in profile — slick top, short back, sideburn
    ht = spec["head_top"]
    for y in range(ht - 1, ht + 4):
        b = backs.get(y, spec["bx"])
        img.hspan(b - 1, face.get(y, spec["fx"]) - 2, y, hair)
    for y in range(ht + 4, ht + 12):
        img.hspan(backs[y] - 1, backs[y] + 2, y, hair)          # short back
    img.hspan(backs[ht + 12] , backs[ht + 12] + 1, ht + 12, hair)  # sideburn
    profile_features(img, spec, skin, skin_sh, hexc("2a2420"))
    # collar + tie knot at the throat
    img.hspan(ncx - 4, ncx + 4, spec["head_bot"] + 4, CREAM)
    tie = RED if (seed >> 13) % 2 == 0 else darken(garment, 0.3)
    img.put(ncx + 1, spec["head_bot"] + 5, tie)
    img.put(ncx + 1, spec["head_bot"] + 6, tie)
    if pid == "rocha":
        # glasses in profile — one lens ring + arm back to the ear
        eye_y = ht + spec["eye_rel"]
        ex = spec["fx"] - 5
        lens = hexc("222020")
        for dx2, dy2 in [(-1, -1), (0, -1), (1, -1), (2, 0), (-2, 0),
                         (-1, 1), (0, 1), (1, 1)]:
            img.put(ex + dx2, eye_y + dy2, lens)
        img.hspan(spec["bx"] + 6, ex - 2, eye_y - 1, lens)      # the arm
        img.put(ncx + 5, spec["head_bot"] + 5, hexc("3868c8"))  # the blue pen
    if pid == "jack":
        # goggles pushed up — band across the crown, one lens up top
        img.hspan(backs[ht + 2] - 1, face[ht + 2] - 1, ht + 2, hexc("6a5a30"))
        img.put(face[ht + 2] - 3, ht + 1, STAR)


def paint_kyrindi(img, pid, seed):
    skins = [hexc("7a94c8"), hexc("8ea6d8"), hexc("6a82b8")]
    skin = skins[(seed >> 15) % 3]
    skin_sh = darken(skin, 0.25)
    skin_lt = lit(skin)
    garment = hexc("2a3450")
    # the long backswept cranium — bx runs almost to the plate edge
    spec = {
        "fx": 31, "bx": 4 + ((seed >> 1) & 0x1),
        "head_top": 7, "head_bot": 32, "crown": 6, "crown_slope": 4,
        "brow_rel": 10, "eye_rel": 12,
        "nose_rel": 14, "nose_len": 3,
        "mouth_rel": 19, "chin_rel": 22, "chin_slope": 1,
        "jaw_rel": 18, "jaw_slope": 3,
    }
    face, backs = build_profile(spec)
    fill_profile(img, face, backs, skin, skin_sh, skin_lt)
    ncx = neck_and_shoulders(img, spec, skin, skin_sh, garment)
    ht = spec["head_top"]
    # crest ridge along the swept skull, or a braid off the back
    crest = darken(skin, 0.4)
    if (seed >> 9) % 2 == 0:
        for x in range(backs[ht + 1] - 1, face[ht + 1] - 6):
            img.put(x, ht - 1, crest)
            if x % 3 == 0:
                img.put(x, ht - 2, crest)
    else:
        bx0 = spec["bx"] + 2
        for y in range(ht + 4, spec["head_bot"] + 6):
            img.put(bx0 - 2, y, crest)
            if y % 3 == 0:
                img.put(bx0 - 3, y, crest)
    # court markings — paired lines down the visible cheek
    eye_y = ht + spec["eye_rel"]
    mark = darken(hexc("2a3450"), 0.1)
    for dy in range(3):
        img.put(spec["fx"] - 6, eye_y + 3 + dy, mark)
        img.put(spec["fx"] - 8, eye_y + 4 + dy, mark)
    profile_features(img, spec, skin, skin_sh, hexc("18203a"))
    # high silver collar + the song-sigil at the throat
    img.hspan(ncx - 5, ncx + 5, spec["head_bot"] + 3, SILVER)
    img.hspan(ncx - 6, ncx + 6, spec["head_bot"] + 4, SILVER)
    img.hspan(ncx - 7, ncx + 7, spec["head_bot"] + 5, darken(SILVER, 0.3))
    img.put(ncx + 2, spec["head_bot"] + 2, STAR)


def paint_delvanni(img, pid, seed):
    skins = [hexc("b06038"), hexc("a05430"), hexc("c07048")]
    skin = skins[(seed >> 15) % 3]
    skin_sh = darken(skin, 0.25)
    skin_lt = lit(skin)
    garments = [hexc("4a3424"), hexc("3a3a2c"), hexc("55402a")]
    garment = garments[(seed >> 7) % 3]
    # massive skull, heavier brow, jaw that barely recedes
    spec = {
        "fx": 32, "bx": 7 - ((seed >> 1) & 0x1),
        "head_top": 5, "head_bot": 32, "crown": 4,
        "brow_rel": 10, "eye_rel": 12,
        "nose_rel": 14, "nose_len": 3,
        "mouth_rel": 19, "chin_rel": 24, "chin_slope": 1,
        "jaw_rel": 26, "jaw_slope": 2,
    }
    face, backs = build_profile(spec)
    # the brow SHELF — two extra rows jutting at brow height
    ht = spec["head_top"]
    face[ht + spec["brow_rel"]] = spec["fx"] + 2
    face[ht + spec["brow_rel"] - 1] = spec["fx"] + 1
    fill_profile(img, face, backs, skin, skin_sh, skin_lt)
    ncx = neck_and_shoulders(img, spec, skin, skin_sh, garment)
    if (seed >> 10) % 2 == 0:   # topknot
        knot = hexc("2a1a10")
        kx = backs[ht + 1] + 3
        img.hspan(kx, kx + 2, ht - 1, knot)
        img.hspan(kx, kx + 2, ht - 2, knot)
        img.put(kx + 1, ht - 3, knot)
    # the tusk — up past the lip, IN SILHOUETTE
    tusk = hexc("e8dcc0")
    my = ht + spec["mouth_rel"]
    tlen = 2 + ((seed >> 22) & 0x1)
    for t in range(tlen):
        img.put(spec["fx"] + 1 + (1 if t >= 2 else 0), my - 1 - t, tusk)
    img.put(spec["fx"], my, tusk)
    # war-paint band across the visible cheek, on some
    eye_y = ht + spec["eye_rel"]
    if (seed >> 12) % 3 == 0:
        img.hspan(spec["fx"] - 9, spec["fx"] - 2, eye_y + 2, darken(hexc("7a3020"), 0.15))
    # a kept scar, on some
    if (seed >> 20) % 3 == 1:
        for i in range(4):
            img.put(spec["fx"] - 10 + i, eye_y + 3 + i, darken(skin, 0.45))
    profile_features(img, spec, skin, skin_sh, hexc("301810"))
    # second shoulder pair + chest strap
    sh_y = spec["head_bot"] + 8
    img.hspan(ncx - 17, ncx - 11, sh_y, skin)
    img.hspan(ncx + 11, ncx + 17, sh_y, skin)
    img.hspan(ncx - 17, ncx - 12, sh_y + 1, skin_sh)
    img.hspan(ncx + 12, ncx + 17, sh_y + 1, skin_lt)
    for i in range(14):
        img.put(ncx - 7 + i, spec["head_bot"] + 5 + i // 3, darken(garment, 0.4))


def paint_kelait(img, pid, seed):
    skins = [hexc("c8b498"), hexc("b8a488"), hexc("d0c0a8")]
    skin = skins[(seed >> 15) % 3]
    skin_sh = darken(skin, 0.2)
    skin_lt = lit(skin)
    garments = [hexc("5a5048"), hexc("4c5248"), hexc("605444")]
    garment = garments[(seed >> 7) % 3]
    child = pid == "yr_kelait_child"
    ht = 21 if child else 17
    hb = (ht + 11) if child else (ht + 14)
    spec = {
        "fx": 28, "bx": 14 if child else 12,
        "head_top": ht, "head_bot": hb, "crown": 3,
        "brow_rel": 4, "eye_rel": 5,
        "nose_rel": 7, "nose_len": 2,
        "mouth_rel": 10, "chin_rel": 12, "chin_slope": 1,
        "jaw_rel": 11, "jaw_slope": 2,
    }
    face, backs = build_profile(spec)
    fill_profile(img, face, backs, skin, skin_sh, skin_lt)
    ncx = neck_and_shoulders(img, spec, skin, skin_sh, garment)
    # the hood — arcs over crown and down the back (elders)
    hood = darken(garment, 0.15)
    if not child:
        for y in range(ht - 3, hb + 3):
            b = backs.get(y, spec["bx"])
            reach = 3 + min(3, (y - (ht - 3)) // 4)
            img.hspan(b - reach, b - 1, y, hood)
        for y in range(ht - 3, ht - 1):
            img.hspan(backs.get(ht, spec["bx"]) - 3, face.get(ht, spec["fx"]) - 2, y, hood)
        img.hspan(backs[ht] - 1, face[ht] - 3, ht - 1, darken(hood, 0.25))
    # the ancient eye — larger than the face wants
    eye_y = ht + spec["eye_rel"]
    ex = spec["fx"] - 5
    dark = hexc("2a2018")
    img.put(ex, eye_y, dark)
    img.put(ex + 1, eye_y, dark)
    img.put(ex, eye_y + 1, dark)
    img.put(ex + 1, eye_y + 1, dark)
    img.put(ex + 1, eye_y, CREAM)
    img.put(spec["fx"] + 1, ht + spec["nose_rel"] + 2, skin_sh)
    img.hspan(spec["fx"] - 4, spec["fx"] - 1, ht + spec["mouth_rel"] + 1, skin_sh)
    # folded hands at the hem
    img.hspan(ncx - 2, ncx + 2, H - 6, skin)
    img.hspan(ncx - 2, ncx + 2, H - 5, skin_sh)


def paint_scarlet(img, pid, seed):
    # the shaft of light, and her profile within it — hair streaming
    # BACK as light
    shaft_l, shaft_r = 10, 30
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if shaft_l <= x <= shaft_r:
                edge = min(x - shaft_l, shaft_r - x)
                if edge >= 6:
                    c, a = hexc("9a3448"), 0.85
                elif edge >= 3:
                    c, a = hexc("7a2438"), 0.6
                else:
                    c, a = hexc("58182a"), 0.3
                if a > bayer(x, y):
                    img.px[y][x] = c
    skin = hexc("f4ead8")
    skin_sh = darken(skin, 0.12)
    skin_lt = WHITE
    garment = hexc("c03048")
    spec = {
        "fx": 29, "bx": 12,
        "head_top": 7, "head_bot": 30, "crown": 4,
        "brow_rel": 9, "eye_rel": 11,
        "nose_rel": 13, "nose_len": 3,
        "mouth_rel": 17, "chin_rel": 20, "chin_slope": 1,
        "jaw_rel": 18, "jaw_slope": 2,
    }
    face, backs = build_profile(spec)
    fill_profile(img, face, backs, skin, skin_sh, skin_lt)
    ncx = neck_and_shoulders(img, spec, skin, skin_sh, garment)
    ht = spec["head_top"]
    # hair as light, streaming back off the skull to the plate edge
    for y in range(ht - 1, ht + 16):
        b = backs.get(y, spec["bx"])
        stream = 2 + (y - ht + 2) % 3
        img.hspan(b - stream - 2, b - 1, y, CREAM)
        if y < ht + 4:
            img.hspan(b - 1, face.get(y, spec["fx"]) - 3, y, CREAM)
    eye_y = ht + spec["eye_rel"]
    img.put(spec["fx"] - 5, eye_y, hexc("6a1828"))
    img.put(spec["fx"] - 4, eye_y, hexc("6a1828"))
    img.hspan(spec["fx"] - 4, spec["fx"] - 1, ht + spec["mouth_rel"] + 1, skin_sh)
    # three points of light leading her gaze
    for sx, sy in [(34, 8), (36, 12), (35, 16)]:
        img.put(sx, sy, STAR)


PAINTERS = {
    "human_earth": paint_human, "kyrindi": paint_kyrindi,
    "delvanni": paint_delvanni, "kelait": paint_kelait,
    "scarlet_ambiguous": paint_scarlet,
}


def portrait(pid, species):
    img = Img(VOID)
    plate_bg(img)
    PAINTERS.get(species, paint_human)(img, pid, gd_hash(pid))
    plate_chrome(img, gd_hash(pid))
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
