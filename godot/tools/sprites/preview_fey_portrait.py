#!/usr/bin/env python3
"""Python mirror of FeyPortrait.gd (v3 + species) for visual review.

Faithfully mirrors the GDScript, including GDScript String.hash()
(djb2 mod 2^32), int64 wraparound in the inline pixel hash, and the
exact paint order. Renders every non-humanoid fey in the catalog plus
a few humanoid references into a labeled contact sheet.

MUST BE KEPT IN LOCKSTEP with FeyPortrait.gd — when the GDScript
painter changes, change this mirror to match before trusting a
preview. Usage: preview_fey_portrait.py [out.png]
"""
import json, os, sys
from PIL import Image, ImageDraw

W, H = 40, 50
REPO = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), "fey_species.png")


def hexc(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16) / 255.0, int(s[2:4], 16) / 255.0,
            int(s[4:6], 16) / 255.0, 1.0)


def col(r, g, b, a=1.0):
    return (r, g, b, a)


def darkened(c, f):
    return (c[0] * (1 - f), c[1] * (1 - f), c[2] * (1 - f), c[3])


def lerpc(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(4))


def gd_hash(s):
    h = 5381
    for ch in s:
        h = (h * 33 + ord(ch)) & 0xFFFFFFFF
    return h


def i64(n):
    n &= 0xFFFFFFFFFFFFFFFF
    return n - 0x10000000000000000 if n >= 0x8000000000000000 else n


PALETTES = {
    "seelie": {
        "bg": hexc("#2a2418"), "aura": hexc("#4a3e22"), "frame": hexc("#f8c848"),
        "skins": [hexc("#f0d8b0"), hexc("#e8c890"), hexc("#f2ccc0")],
        "eye": hexc("#3a5a2a"), "eye_hi": hexc("#f8f4e0"), "feature": hexc("#e8a0b0"),
        "hairs": [hexc("#e8d090"), hexc("#c88848"), hexc("#f0f0e0"), hexc("#a86840")],
        "garment": hexc("#8a7440"),
    },
    "unseelie": {
        "bg": hexc("#1c1024"), "aura": hexc("#32204a"), "frame": hexc("#8a5aa8"),
        "skins": [hexc("#d8c8e0"), hexc("#e8e4e0"), hexc("#a8b0c8")],
        "eye": hexc("#601830"), "eye_hi": hexc("#f0d8e8"), "feature": hexc("#503060"),
        "hairs": [hexc("#302040"), hexc("#141020"), hexc("#684a78"), hexc("#8890a0")],
        "garment": hexc("#3a2a50"),
    },
    "wildfey": {
        "bg": hexc("#1c2014"), "aura": hexc("#32381e"), "frame": hexc("#c8983a"),
        "skins": [hexc("#c8b088"), hexc("#a88860"), hexc("#a8b080")],
        "eye": hexc("#c87828"), "eye_hi": hexc("#f4e8c8"), "feature": hexc("#587038"),
        "hairs": [hexc("#6a4a28"), hexc("#3a4a28"), hexc("#8a6838"), hexc("#484030")],
        "garment": hexc("#4a5230"),
    },
}

SPECIES_OVERRIDES = {
    "will_o_wisp": "wisp", "brollachan": "formless", "sluagh": "swarm",
    "nuckelavee": "abomination", "cricket_the_cricket": "insect",
    "salt_sisters": "triad", "hecate": "triad", "setebos": "bullhead",
    "kelpie": "beast", "pooka": "beast", "cu_sith": "beast",
    "black_dog": "beast", "cluricaunes_cat": "beast", "ossory_wolf": "beast",
    "selkie": "beast", "boggart": "beast",
    "green_man": "treefolk", "ghillie_dhu": "treefolk", "huldra": "treefolk",
    "skogsra": "treefolk",
    "ondine": "aquatic", "nixie": "aquatic", "merrow": "aquatic",
    "ceasg": "aquatic", "nokken": "aquatic", "fossegrim": "aquatic",
    "bean_nighe": "aquatic", "blue_man_minch": "aquatic",
    "moth": "winged", "queen_mab": "winged", "cobweb": "winged",
    "ariel": "wraith", "hamlets_ghost": "wraith", "ophelia_ghost": "wraith",
    "sycorax": "wraith", "banshee": "wraith", "fear_gorta": "wraith",
    "draugr": "wraith",
}


def resolve_species(fey):
    fid = str(fey.get("id", ""))
    if fid in SPECIES_OVERRIDES:
        return SPECIES_OVERRIDES[fid]
    tf = str(fey.get("true_form", "")).lower()
    if "wing" in tf:
        return "winged"
    if ("dog" in tf or "wolf" in tf or "hound" in tf or " cat" in tf
            or "horse" in tf or "seal" in tf):
        return "beast"
    if ("moss" in tf or "leaves" in tf or "tree-" in tf
            or "pine-trunk" in tf or "bramble" in tf):
        return "treefolk"
    if ("mermaid" in tf or "fish-tail" in tf or "water-fey" in tf
            or "seawater" in tf):
        return "aquatic"
    if ("ghost" in tf or "shade" in tf or "revenant" in tf
            or "translucent" in tf):
        return "wraith"
    return "humanoid"


_BAYER4 = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]


def bayer(x, y):
    return (_BAYER4[(y % 4) * 4 + (x % 4)] + 0.5) / 16.0


class Img:
    def __init__(self, fill):
        self.px = [[fill] * W for _ in range(H)]

    def set_pixel(self, x, y, c):
        self.px[y][x] = c

    def get_pixel(self, x, y):
        return self.px[y][x]


def put(img, x, y, c):
    if 1 <= x < W - 1 and 1 <= y < H - 1:
        img.set_pixel(x, y, c)


def hspan(img, x0, x1, y, c):
    for x in range(x0, x1 + 1):
        put(img, x, y, c)


def pixel_hash(x_term, thresh_seed):
    """n = i64 mash; returns 0..1 float, mirroring the GDScript inline hash."""
    n = i64(x_term)
    n = i64((n ^ (n >> 13)) * 1274126177)
    return ((n ^ (n >> 16)) & 0xFFFF) / 65536.0


def paint_custom_species(img, species, pal, seed):
    feat = pal["feature"]; frame = pal["frame"]; eye_hi = pal["eye_hi"]; bg = pal["bg"]
    if species == "wisp":
        fx, fy = 20, 24
        for y in range(fy - 9, fy + 8):
            r = 7 - abs(y - fy) if y >= fy - 2 else max(1, 5 - (fy - 2 - y) * 2)
            for x in range(fx - r, fx + r + 1):
                put(img, x, y, feat)
        for y2 in range(fy - 4, fy + 6):
            r2 = 4 - abs(y2 - (fy + 1))
            if r2 > 0:
                hspan(img, fx - r2, fx + r2, y2, eye_hi)
        hspan(img, fx - 1, fx + 1, fy + 2, frame)
        put(img, fx - 2, fy, bg)
        put(img, fx + 2, fy, bg)
        for s in [[10, 14], [30, 18], [13, 34], [28, 33], [20, 8]]:
            put(img, s[0], s[1], feat)
        for x3 in range(fx - 6, fx + 7):
            if bayer(x3, 40) < 0.4:
                put(img, x3, 40, feat)
    elif species == "formless":
        dark = col(0.05, 0.03, 0.08, 1.0)
        for y in range(16, H - 4):
            for x in range(4, W - 4):
                v = pixel_hash(x * 374761393 + y * 668265263 + seed, seed)
                edge = 1.0 - abs(x - W / 2.0) / (W * 0.42)
                depth = min(max((y - 14.0) / 16.0, 0.0), 1.0)
                if v < edge * depth * 0.96:
                    put(img, x, y, dark)
        hspan(img, 14, 15, 26, eye_hi)
        hspan(img, 24, 25, 29, eye_hi)
        for d in [[9, 45], [21, 46], [33, 44]]:
            put(img, d[0], d[1], dark)
    elif species == "swarm":
        body = col(0.08, 0.06, 0.10, 1.0)
        moon = col(0.55, 0.52, 0.62, 1.0)
        for my0 in range(10, 32):
            for mx0 in range(9, 32):
                mdx = mx0 - 20.0
                mdy = my0 - 20.0
                if mdx * mdx + mdy * mdy < 90.0 and bayer(mx0, my0) < 0.8:
                    put(img, mx0, my0, moon)
        wing = col(0.62, 0.60, 0.70, 1.0)
        idx = 0
        for row in range(3):
            for c in range(3 + (row % 2)):
                sx = 7 + c * 9 + (4 if row % 2 == 1 else 0)
                sy = 12 + row * 10 + ((seed >> (idx % 8)) & 0x3)
                hspan(img, sx - 1, sx + 1, sy, body)
                hspan(img, sx - 1, sx + 1, sy + 1, body)
                put(img, sx, sy - 1, body)
                put(img, sx - 2, sy, wing)
                put(img, sx + 2, sy, wing)
                put(img, sx, sy, eye_hi)
                idx += 1
        for wx in range(6, 34, 4):
            put(img, wx, 42, feat)
    elif species == "abomination":
        red = hexc("#7a2018"); red_dk = hexc("#4a100c")
        for y in range(28, 42):
            r3 = 13 - max(0, abs(y - 34) - 2)
            hspan(img, 20 - r3, 20 + r3, y, red)
        for lx in [10, 16, 24, 30]:
            for ly in range(42, 47):
                put(img, lx, ly, red_dk)
        for y4 in range(12, 30):
            r4 = 5 - max(0, abs(y4 - 20) - 5)
            if r4 > 0:
                hspan(img, 26 - r4, 26 + r4, y4, red)
        for my in range(30, 41, 3):
            hspan(img, 12, 28, my, red_dk)
        for my2 in range(14, 27, 3):
            hspan(img, 23, 29, my2, red_dk)
        for e in [[26, 15], [28, 17], [12, 31], [17, 30], [25, 32]]:
            put(img, e[0], e[1], eye_hi)
    elif species == "insect":
        shell = hexc("#3a6a30"); shell_lt = hexc("#58925a")
        for y5 in range(18, 34):
            put(img, 8, y5, feat)
            put(img, 32, y5, feat)
        for y6 in range(14, 28):
            r5 = 9 - max(0, abs(y6 - 21) - 4)
            hspan(img, 20 - r5, 20 + r5, y6, shell)
        hspan(img, 14, 26, 15, shell_lt)
        for e2 in [[15, 19], [20, 17], [25, 19]]:
            put(img, e2[0], e2[1], pal["eye"])
            put(img, e2[0], e2[1] - 1, eye_hi)
        put(img, 18, 27, shell_lt)
        put(img, 22, 27, shell_lt)
        for a in range(6):
            put(img, 15 - a, 13 - a, shell_lt)
            put(img, 25 + a, 13 - a, shell_lt)
        for i2 in range(3):
            lx2 = 14 + i2 * 6
            for ly2 in range(28, 34 + i2):
                put(img, lx2, ly2, shell)
                put(img, 40 - lx2, ly2, shell)
    elif species == "triad":
        skin3 = pal["skins"][0]
        skin3_sh = darkened(skin3, 0.25)
        for y7 in range(36, H - 3):
            widen3 = min(16, 8 + (y7 - 36) * 2)
            hspan(img, 20 - widen3, 20 + widen3, y7, pal["garment"])
        for side6 in [-1, 1]:
            hx2 = 20 + side6 * 10
            for y8 in range(18, 32):
                r6 = 4 - max(0, abs(y8 - 24) - 4)
                if r6 > 0:
                    hspan(img, hx2 - r6, hx2 + r6, y8, skin3_sh)
            put(img, hx2 - 1, 23, pal["eye"])
            put(img, hx2 + 1, 23, pal["eye"])
            hspan(img, hx2 - 3, hx2 + 3, 18, pal["hairs"][1])
        for y9 in range(14, 30):
            r7 = 5 - max(0, abs(y9 - 21) - 5)
            if r7 > 0:
                hspan(img, 20 - r7, 20 + r7, y9, skin3)
        put(img, 18, 20, pal["eye"])
        put(img, 22, 20, pal["eye"])
        put(img, 18, 19, pal["eye_hi"])
        hspan(img, 18, 22, 26, skin3_sh)
        hspan(img, 16, 24, 14, pal["hairs"][0])
        hspan(img, 15, 25, 15, pal["hairs"][0])


def apply_species_modifier(img, species, pal, ctx):
    head_left = ctx["head_left"]; head_right = ctx["head_right"]
    head_top = ctx["head_top"]; head_bot = ctx["head_bot"]
    cx = ctx["cx"]; eye_y = ctx["eye_y"]; eye_dx = ctx["eye_dx"]
    skin = ctx["skin"]; skin_sh = ctx["skin_sh"]
    hair = ctx["hair"]; hair_sh = ctx["hair_sh"]; garment = ctx["garment"]
    seed = ctx["seed"]
    feat = pal["feature"]; eye = pal["eye"]; eye_hi = pal["eye_hi"]
    bg = pal["bg"]; aura = pal["aura"]
    if species == "beast":
        for y in range(head_top - 2, head_bot):
            for x in range(head_left, head_right):
                put(img, x, y, hair if x < head_right - 3 else hair_sh)
        for y2 in range(eye_y + 3, head_bot - 1):
            hspan(img, cx - 3, cx + 3, y2, skin)
        hspan(img, cx - 1, cx + 1, eye_y + 4, hair_sh)
        put(img, cx, head_bot - 3, hair_sh)
        for side in [-1, 1]:
            ex = cx + side * eye_dx
            put(img, ex, eye_y, eye)
            put(img, ex + 1, eye_y, eye)
            put(img, ex, eye_y + 1, eye)
            put(img, ex + 1, eye_y + 1, eye)
            put(img, ex, eye_y, eye_hi)
        for side2 in [-1, 1]:
            ax = cx + side2 * 6
            put(img, ax, head_top - 3, hair)
            hspan(img, ax - 1, ax + 1, head_top - 2, hair)
            hspan(img, ax - 2, ax + 2, head_top - 1, hair)
    elif species == "treefolk":
        bark = col(garment[0] * 0.8, garment[1] * 0.7, garment[2] * 0.5, 1.0)
        bark_dk = darkened(bark, 0.35)
        for y3 in range(head_top - 1, head_bot):
            for x2 in range(head_left, head_right):
                put(img, x2, y3, bark)
        for gx in range(head_left + 2, head_right - 1, 3):
            for gy in range(head_top, head_bot - 1):
                if (gy + gx) % 7 < 3:
                    put(img, gx, gy, bark_dk)
        for lx in range(head_left - 1, head_right + 1, 2):
            put(img, lx, head_top - 2, feat)
            put(img, lx + 1, head_top - 3, feat)
        put(img, cx - 8, head_bot + 4, feat)
        put(img, cx + 7, head_bot + 5, feat)
        put(img, cx + 8, head_bot + 4, feat)
        for side3 in [-1, 1]:
            ex2 = cx + side3 * eye_dx
            put(img, ex2, eye_y, eye_hi)
            put(img, ex2 + 1, eye_y, eye_hi)
            put(img, ex2, eye_y + 1, bark_dk)
        hspan(img, cx - 2, cx + 2, head_bot - 4, bark_dk)
    elif species == "aquatic":
        tint = col(0.35, 0.62, 0.60, 1.0)
        for ty in range(head_top, head_bot + 3):
            for tx in range(head_left - 1, head_right + 1):
                c0 = img.get_pixel(min(max(tx, 1), W - 2), min(max(ty, 1), H - 2))
                if c0 == skin or c0 == skin_sh:
                    put(img, tx, ty, lerpc(c0, tint, 0.30))
        for side4 in [-1, 1]:
            fx2 = (head_left - 1) if side4 < 0 else head_right
            for i in range(4):
                for j in range(i + 1):
                    put(img, fx2 + side4 * j, eye_y - 2 + i, feat)
        for side5 in [-1, 1]:
            for g2 in range(3):
                put(img, cx + side5 * 2, head_bot + g2, darkened(skin_sh, 0.2))
        for sc in [[cx - eye_dx - 1, eye_y + 3], [cx + eye_dx + 1, eye_y + 4],
                   [cx - eye_dx, eye_y + 5]]:
            put(img, sc[0], sc[1], feat)
        hspan(img, head_left + 1, head_right - 2, head_top + 4, hair_sh)
    elif species == "winged":
        wing_c = lerpc(feat, eye_hi, 0.30)
        for side6 in [-1, 1]:
            for wy in range(14, 34):
                reach = 9 - abs(wy - 22) // 2
                for wxi in range(reach):
                    wx = (head_left - 3 - wxi) if side6 < 0 else (head_right + 2 + wxi)
                    cur = img.get_pixel(min(max(wx, 1), W - 2), wy)
                    if cur == bg or cur == aura:
                        put(img, wx, wy, wing_c)
            sx2 = (head_left - 6) if side6 < 0 else (head_right + 5)
            put(img, sx2, 21, eye_hi)
            put(img, sx2, 22, hair_sh)
        for side7 in [-1, 1]:
            for a2 in range(4):
                put(img, cx + side7 * (2 + a2), head_top - 2 - a2, hair_sh)
    elif species == "wraith":
        for y4 in range(1, H - 1):
            for x3 in range(1, W - 1):
                c = img.get_pixel(x3, y4)
                if c in (skin, skin_sh, hair, hair_sh, garment):
                    img.set_pixel(x3, y4, lerpc(c, bg, 0.45))
        for x4 in range(8, W - 8):
            n2 = i64(x4 * 374761393 + seed)
            n2 = i64((n2 ^ (n2 >> 13)) * 1274126177)
            frays = 2 + ((n2 ^ (n2 >> 16)) & 0x3)
            for f2 in range(frays):
                put(img, x4, H - 4 - f2, bg)
        for side8 in [-1, 1]:
            ex3 = cx + side8 * eye_dx
            put(img, ex3, eye_y, eye_hi)
            put(img, ex3 + 1, eye_y, eye_hi)
            put(img, ex3, eye_y + 1, eye_hi)
    elif species == "bullhead":
        bone = hexc("#d8d0be")
        for y5 in range(eye_y + 2, head_bot):
            hspan(img, cx - 5, cx + 5, y5, hair)
        put(img, cx - 2, eye_y + 5, hair_sh)
        put(img, cx + 2, eye_y + 5, hair_sh)
        for side9 in [-1, 1]:
            hx3 = head_left if side9 < 0 else (head_right - 1)
            hy2 = head_top + 2
            for i3 in range(5):
                dy = i3 if i3 < 3 else 2 + i3 % 2
                put(img, hx3 + side9 * i3, hy2 - dy, bone)
                put(img, hx3 + side9 * i3, hy2 - dy + 1, bone)


def procedural(fey):
    fid = str(fey.get("id", "unknown"))
    court = str(fey.get("court", "wildfey"))
    tier = min(max(int(fey.get("tier", 1)), 1), 6)
    pal = PALETTES.get(court, PALETTES["wildfey"])
    seed = gd_hash(fid)

    img = Img(pal["bg"])

    aura = pal["aura"]
    aura_w = W * (0.50 if court == "unseelie" else 0.62)
    aura_h = H * (0.62 if court == "wildfey" else 0.55)
    if court == "unseelie":
        aura_h = H * 0.70
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            dx = (x - W / 2.0) / aura_w
            dy = (y - H * 0.42) / aura_h
            g = min(max(1.0 - (dx * dx + dy * dy) ** 0.5, 0.0), 1.0)
            if g * 0.85 > bayer(x, y):
                img.set_pixel(x, y, aura)

    frame = pal["frame"]
    for x in range(W):
        img.set_pixel(x, 0, frame)
        img.set_pixel(x, H - 1, frame)
    for y in range(H):
        img.set_pixel(0, y, frame)
        img.set_pixel(W - 1, y, frame)
    inset = col(frame[0] * 0.4, frame[1] * 0.4, frame[2] * 0.4, 1.0)
    for x in range(2, W - 2):
        put(img, x, 2, inset)
        put(img, x, H - 3, inset)
    for y in range(2, H - 2):
        put(img, 2, y, inset)
        put(img, W - 3, y, inset)

    species = resolve_species(fey)
    if species in ("wisp", "formless", "swarm", "abomination", "insect", "triad"):
        paint_custom_species(img, species, pal, seed)
        for t0 in range(tier):
            put(img, 5 + t0 * 5, H - 3, frame)
            put(img, 6 + t0 * 5, H - 3, frame)
        return img, species

    head_w = 14 + (seed & 0x7)
    head_h = 17 + ((seed >> 3) & 0x7)
    eye_dx = 3 + ((seed >> 6) & 0x3)
    eye_size = 1 + ((seed >> 8) & 0x1)
    mouth_style = (seed >> 9) & 0x3
    feature_kind = (seed >> 11) & 0x3
    hair_style = (seed >> 13) & 0x3
    skins = pal["skins"]
    skin = skins[((seed >> 15) & 0x3) % len(skins)]
    skin_sh = darkened(skin, 0.22)
    hairs = pal["hairs"]
    hair = hairs[((seed >> 17) & 0x3) % len(hairs)]
    hair_sh = darkened(hair, 0.28)
    eye_style = (seed >> 19) & 0x1
    marking = (seed >> 20) & 0x3
    adornment = (seed >> 22) & 0x3

    cx = W // 2
    head_top = 10
    head_left = cx - head_w // 2
    head_right = head_left + head_w
    head_bot = min(head_top + head_h, H - 12)

    garment = pal["garment"]
    for y in range(head_bot + 2, H - 3):
        widen = min(14, 5 + (y - head_bot - 2) * 2)
        hspan(img, cx - widen, cx + widen, y, garment)
    hspan(img, cx - 6, cx + 6, head_bot + 2, skin_sh)
    for y in range(head_bot - 1, head_bot + 3):
        hspan(img, cx - 3, cx + 3, y, skin_sh)

    for y in range(head_top, head_bot):
        x0 = head_left
        x1 = head_right
        if y == head_top:
            x0 += 3; x1 -= 3
        elif y == head_top + 1:
            x0 += 1; x1 -= 1
        from_bot = head_bot - 1 - y
        if from_bot == 0:
            x0 += 4; x1 -= 4
        elif from_bot == 1:
            x0 += 2; x1 -= 2
        elif from_bot == 2:
            x0 += 1; x1 -= 1
        for x in range(x0, x1):
            if x >= x1 - 3 and from_bot > 2:
                put(img, x, y, skin_sh)
            else:
                put(img, x, y, skin)

    if hair_style == 0:
        for y in range(head_top - 1, head_top + 4):
            pad = 2 if y <= head_top else 0
            hspan(img, head_left + pad, head_right - 1 - pad, y, hair)
        hspan(img, head_left, head_right - 1, head_top + 4, hair_sh)
    elif hair_style == 1:
        for y in range(head_top - 1, head_top + 4):
            hspan(img, head_left, head_right - 1, y, hair)
        for y in range(head_top + 4, head_bot + 4):
            hspan(img, head_left - 2, head_left, y, hair)
            hspan(img, head_right - 1, head_right + 1, y, hair_sh)
        hspan(img, head_left, head_right - 1, head_top + 4, hair_sh)
    elif hair_style == 2:
        for y in range(head_top - 3, head_top + 5):
            for x in range(head_left - 2, head_right + 2):
                v = pixel_hash(x * 374761393 + y * 668265263 + seed, seed)
                if v > 0.22:
                    put(img, x, y, hair if y < head_top + 3 else hair_sh)
    else:
        for y in range(head_top - 1, head_top + 3):
            hspan(img, head_left, head_right - 1, y, hair)
        hspan(img, head_left, cx + 1, head_top + 3, hair)
        hspan(img, head_left, cx - 3, head_top + 4, hair)
        hspan(img, head_left, head_right - 1, head_top + 5, hair_sh)

    ear_base = head_top + 8
    for side_e in [-1, 1]:
        ear_x = (head_left - 1) if side_e < 0 else head_right
        put(img, ear_x, ear_base, skin)
        put(img, ear_x, ear_base + 1, skin_sh)
        put(img, ear_x + side_e, ear_base - 1, skin)

    eye_y = head_top + 7
    eye = pal["eye"]
    eye_hi = pal["eye_hi"]
    for side in [-1, 1]:
        ex0 = cx + side * eye_dx - 1
        for ey in range(eye_size + 1):
            hspan(img, ex0, ex0 + eye_size + 1, eye_y + ey, eye)
        if eye_style == 1:
            hspan(img, ex0 + 1, ex0 + eye_size, eye_y - 1, eye)
        if court == "unseelie":
            for ey2 in range(eye_size + 1):
                put(img, ex0 + 1, eye_y + ey2, eye_hi)
        else:
            put(img, ex0 + (0 if side < 0 else eye_size), eye_y, eye_hi)
    for side2 in [-1, 1]:
        bx0 = cx + side2 * eye_dx - 1
        hspan(img, bx0, bx0 + eye_size + 1, eye_y - 2, skin_sh)

    put(img, cx, eye_y + 4, skin_sh)

    if marking == 1:
        put(img, cx - eye_dx - 1, eye_y + 4, skin_sh)
        put(img, cx + eye_dx, eye_y + 5, skin_sh)
        put(img, cx + eye_dx + 2, eye_y + 4, skin_sh)
    elif marking == 2:
        put(img, cx - eye_dx, eye_y + 3, pal["feature"])
        put(img, cx - eye_dx, eye_y + 4, pal["feature"])
    elif marking == 3:
        put(img, cx, eye_y - 4, pal["feature"])

    mouth_y = head_bot - 5
    if mouth_style == 0:
        hspan(img, cx - 2, cx + 2, mouth_y, skin_sh)
    elif mouth_style == 1:
        put(img, cx - 3, mouth_y - 1, skin_sh)
        hspan(img, cx - 2, cx + 2, mouth_y, skin_sh)
        put(img, cx + 3, mouth_y - 1, skin_sh)
    elif mouth_style == 2:
        put(img, cx, mouth_y, eye)
        put(img, cx, mouth_y - 1, skin_sh)
    else:
        put(img, cx - 3, mouth_y, skin_sh)
        hspan(img, cx - 2, cx + 2, mouth_y - 1, skin_sh)
        put(img, cx + 3, mouth_y, skin_sh)

    feat = pal["feature"]
    if court == "seelie":
        ear_y = head_top + 6 + feature_kind
        for side3 in [-1, 1]:
            ex = (head_left - 1) if side3 < 0 else head_right
            put(img, ex, ear_y, feat)
            put(img, ex, ear_y + 1, feat)
            put(img, ex + side3, ear_y - 1, feat)
            put(img, ex + side3, ear_y, feat)
            put(img, ex + side3 * 2, ear_y - 2, feat)
        put(img, cx - eye_dx - 2, eye_y + 3, feat)
        put(img, cx + eye_dx + 2, eye_y + 3, feat)
        if tier >= 4:
            for cxx in [cx - 3, cx, cx + 3]:
                put(img, cxx, head_top - 4, frame)
            put(img, cx, head_top - 5, frame)
    elif court == "unseelie":
        horn_len = 4 + feature_kind
        for side4 in [-1, 1]:
            hx = (head_left + 2) if side4 < 0 else (head_right - 3)
            hy = head_top
            for i in range(horn_len):
                lean = side4 if i * 2 >= horn_len else 0
                hx += lean
                hy -= 1
                put(img, hx, hy, feat)
                put(img, hx + side4, hy, feat)
            put(img, hx, hy - 1, eye_hi)
        if tier >= 4:
            hspan(img, cx - 4, cx + 4, head_top - 7, feat)
    elif court == "wildfey":
        ant_len = 5 + feature_kind
        for side5 in [-1, 1]:
            ax = (head_left + 3) if side5 < 0 else (head_right - 4)
            for i in range(ant_len):
                ay = head_top - 1 - i
                put(img, ax, ay, feat)
                if i == 2:
                    put(img, ax + side5, ay, feat)
                    put(img, ax + side5 * 2, ay - 1, feat)
                if i == ant_len - 1:
                    put(img, ax + side5, ay - 1, feat)
        put(img, cx - 8, H - 8, feat)
        put(img, cx + 7, H - 10, feat)

    if adornment == 1:
        put(img, head_left - 1, ear_base + 2, frame)
        put(img, head_right, ear_base + 2, frame)
    elif adornment == 2:
        hspan(img, head_left + 2, head_right - 3, head_top + 5, frame)
    elif adornment == 3:
        put(img, cx, head_bot + 4, frame)
        put(img, cx, head_bot + 5, inset)

    garment_sh = darkened(garment, 0.25)
    for y3 in range(head_bot + 3, H - 3):
        widen2 = min(14, 5 + (y3 - head_bot - 2) * 2)
        for x3 in range(cx + widen2 - 4, cx + widen2 + 1):
            if img.get_pixel(min(max(x3, 1), W - 2), y3) == garment:
                put(img, x3, y3, garment_sh)
    hspan(img, cx - 7, cx + 7, head_bot + 3, garment_sh)

    if species != "humanoid":
        apply_species_modifier(img, species, pal, {
            "seed": seed, "head_left": head_left, "head_right": head_right,
            "head_top": head_top, "head_bot": head_bot, "cx": cx,
            "eye_y": eye_y, "eye_dx": eye_dx, "eye_size": eye_size,
            "skin": skin, "skin_sh": skin_sh, "hair": hair, "hair_sh": hair_sh,
            "garment": garment,
        })

    for t in range(tier):
        put(img, 5 + t * 5, H - 3, frame)
        put(img, 6 + t * 5, H - 3, frame)
    return img, species


def to_pil(img, scale=4):
    p = Image.new("RGB", (W, H))
    for y in range(H):
        for x in range(W):
            c = img.px[y][x]
            p.putpixel((x, y), tuple(int(round(min(max(v, 0.0), 1.0) * 255)) for v in c[:3]))
    return p.resize((W * scale, H * scale), Image.NEAREST)


def main():
    feys = json.load(open(os.path.join(
        REPO, "godot/resources/games/vol7/fey_faire/feys.json")))["feys"] \
        if False else None
    with open(os.path.join(REPO, "godot/resources/games/vol7/fey_faire/feys.json")) as f:
        data = json.load(f)
    feys = data if isinstance(data, list) else data["feys"]
    by_id = {f["id"]: f for f in feys}

    order = ["wisp", "formless", "swarm", "abomination", "insect", "triad",
             "bullhead", "beast", "treefolk", "aquatic", "winged", "wraith",
             "humanoid"]
    picked = []
    counts = {}
    for fey in feys:
        sp = resolve_species(fey)
        counts[sp] = counts.get(sp, 0) + 1
        if sp != "humanoid":
            picked.append((sp, fey))
    # a few humanoid references at the end
    href = [f for f in feys if resolve_species(f) == "humanoid"][:4]
    picked += [("humanoid", f) for f in href]
    picked.sort(key=lambda t: (order.index(t[0]), t[1]["id"]))
    print("species counts:", {k: counts.get(k, 0) for k in order})
    print("rendering", len(picked))

    scale = 4
    cols = 8
    cw, ch = W * scale + 8, H * scale + 22
    rows = (len(picked) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cw + 8, rows * ch + 8), (16, 14, 18))
    draw = ImageDraw.Draw(sheet)
    for i, (sp, fey) in enumerate(picked):
        img, _ = procedural(fey)
        tile = to_pil(img, scale)
        gx = 8 + (i % cols) * cw
        gy = 8 + (i // cols) * ch
        sheet.paste(tile, (gx, gy))
        draw.text((gx, gy + H * scale + 2), fey["id"][:20], fill=(200, 195, 180))
        draw.text((gx, gy + H * scale + 11), sp, fill=(140, 130, 120))
    sheet.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
