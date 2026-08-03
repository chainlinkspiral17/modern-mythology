#!/usr/bin/env python3
"""gen_vol7_cgs.py — the twelve Vol 7 CG plates.

Every `cg` node in the game is in Vol 7 and (2026-08 audit) every one
pointed at a file that did not exist — the book's biggest authored
images presented as black. These are those twelve, generated in the
endpaper-plate language so they read as plates from the same book:
flat woodcut shapes, 3-5 values per plate, a deckle margin, laid-
paper grain (luminance-only jitter), true radial vignette. All
deterministic (zlib.crc32 seeds — Python's hash() is salted).

Output: godot/assets/cg/vol7_*.png · 1280×720.
Run twice → identical bytes (the determinism test).
"""
import os, zlib, math
from PIL import Image, ImageDraw

W, H = 1280, 720
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "cg")

def rng(seed_s):
    state = [zlib.crc32(seed_s.encode()) & 0xffffffff]
    def n():
        state[0] = (state[0] * 1664525 + 1013904223) & 0xffffffff
        return state[0] / 0xffffffff
    return n

def base(col):
    return Image.new("RGB", (W, H), col)

def vgrad(img, top, bottom, y0=0, y1=H):
    d = ImageDraw.Draw(img)
    for y in range(y0, y1):
        t = (y - y0) / max(1, (y1 - y0 - 1))
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)

def grain(img, seed, amt=7):
    # luminance-only jitter — per-channel jitter reads as rainbow noise
    n = rng(seed + ":grain")
    px = img.load()
    for y in range(0, H, 2):
        for x in range(0, W, 2):
            dl = int((n() - 0.5) * 2 * amt)
            r, g, b = px[x, y]
            px[x, y] = (max(0, min(255, r + dl)), max(0, min(255, g + dl)),
                        max(0, min(255, b + dl)))
    return img

def vignette(img, strength=0.42):
    # true radial ramp at low res, scaled up (rings antipattern fix)
    lw, lh = 160, 90
    m = Image.new("L", (lw, lh))
    mp = m.load()
    cx, cy = lw / 2, lh / 2
    maxd = math.hypot(cx, cy)
    for y in range(lh):
        for x in range(lw):
            d = math.hypot(x - cx, y - cy) / maxd
            mp[x, y] = int(255 * strength * (d ** 2.2))
    m = m.resize((W, H), Image.BILINEAR)
    black = Image.new("RGB", (W, H), (6, 5, 4))
    img.paste(black, (0, 0), m)
    return img

def deckle(img, seed, paper=(226, 218, 198), margin=26):
    # the endpaper deckle: a rough paper border so it reads as a plate
    n = rng(seed + ":deckle")
    d = ImageDraw.Draw(img)
    for side in range(4):
        pts = []
        steps = 64
        for i in range(steps + 1):
            t = i / steps
            wob = (n() - 0.5) * 10
            if side == 0:   x, y = t * W, margin + wob
            elif side == 1: x, y = t * W, H - margin + wob
            elif side == 2: x, y = margin + wob, t * H
            else:           x, y = W - margin + wob, t * H
            pts.append((x, y))
        if side == 0:
            d.polygon([(0, 0), (W, 0)] + pts[::-1], fill=paper)
        elif side == 1:
            d.polygon([(0, H), (W, H)] + pts[::-1], fill=paper)
        elif side == 2:
            d.polygon([(0, 0), (0, H)] + pts[::-1], fill=paper)
        else:
            d.polygon([(W, 0), (W, H)] + pts[::-1], fill=paper)
    return img

def spiral(d, cx, cy, r_out, turns, col, w=3):
    pts = []
    steps = int(60 * turns)
    for i in range(steps + 1):
        t = i / steps
        a = t * turns * 2 * math.pi
        r = r_out * t
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.line(pts, fill=col, width=w, joint="curve")

def stars(d, seed, n_stars, y_max, col):
    n = rng(seed + ":stars")
    for _ in range(n_stars):
        x, y = n() * W, n() * y_max
        s = 1 + int(n() * 2)
        d.ellipse([x, y, x + s, y + s], fill=col)

def rain(d, seed, col, count=340):
    n = rng(seed + ":rain")
    for _ in range(count):
        x, y = n() * W, n() * H
        ln = 8 + n() * 16
        d.line([(x, y), (x - 3, y + ln)], fill=col, width=1)

def cedar(d, x, y_base, h, col):
    w = h * 0.38
    for tier in range(3):
        t0 = y_base - h * (0.35 + 0.3 * tier)
        tw = w * (1.0 - 0.28 * tier)
        d.polygon([(x, t0 - h * 0.28), (x - tw / 2, t0), (x + tw / 2, t0)], fill=col)
    d.rectangle([x - 4, y_base - h * 0.3, x + 4, y_base], fill=col)


# ── the twelve plates ────────────────────────────────────────────

def smolvud_alley_night(img):
    # Hemlock at night · the bookstore · the alley
    vgrad(img, (14, 16, 30), (30, 30, 44))
    d = ImageDraw.Draw(img)
    stars(d, "alley", 60, 260, (200, 205, 220))
    # facing building silhouettes forming the alley
    d.polygon([(0, 180), (470, 260), (470, 720), (0, 720)], fill=(20, 18, 26))
    d.polygon([(1280, 160), (820, 250), (820, 720), (1280, 720)], fill=(17, 15, 23))
    # the bookstore's one lit window, warm, left wall
    d.rectangle([300, 380, 384, 470], fill=(216, 168, 88))
    d.rectangle([316, 396, 368, 454], fill=(240, 205, 130))
    d.line([(342, 396), (342, 454)], fill=(216, 168, 88), width=3)
    # spill on the alley floor
    d.polygon([(300, 470), (384, 470), (470, 620), (250, 620)], fill=(58, 48, 38))
    # cobble suggestion
    for yy in range(560, 700, 18):
        d.line([(360 - (yy - 560), yy), (900 + (yy - 560), yy)], fill=(26, 25, 34), width=2)
    return img

def four_bowls_cedar(img):
    # the cedar bowl, spiral outside, two cupped hands wide
    vgrad(img, (42, 34, 28), (24, 19, 16))
    d = ImageDraw.Draw(img)
    # table line
    d.rectangle([0, 500, W, 720], fill=(32, 25, 20))
    d.line([(0, 500), (W, 500)], fill=(58, 46, 36), width=3)
    # the bowl
    d.ellipse([440, 300, 840, 520], fill=(122, 84, 52))
    d.ellipse([470, 315, 810, 460], fill=(74, 50, 32))
    d.ellipse([500, 330, 780, 430], fill=(96, 66, 42))
    spiral(d, 640, 470, 150, 2.4, (60, 40, 26), 5)
    # a soft top light
    d.ellipse([560, 292, 720, 330], fill=(150, 108, 70))
    return img

def olafs_bell(img):
    # Olaf's bell, cedar, the carved spiral
    vgrad(img, (26, 30, 34), (16, 18, 22))
    d = ImageDraw.Draw(img)
    # beam + cord
    d.rectangle([0, 60, W, 110], fill=(44, 34, 26))
    d.line([(640, 110), (640, 220)], fill=(120, 110, 92), width=6)
    # the bell body (cedar)
    d.polygon([(520, 220), (760, 220), (820, 500), (460, 500)], fill=(110, 76, 46))
    d.polygon([(540, 220), (740, 220), (790, 480), (490, 480)], fill=(128, 90, 55))
    d.rectangle([460, 500, 820, 528], fill=(86, 58, 36))
    spiral(d, 640, 380, 96, 2.2, (66, 44, 28), 5)
    # clapper
    d.line([(640, 528), (640, 590)], fill=(90, 84, 70), width=5)
    d.ellipse([620, 586, 660, 626], fill=(120, 110, 92))
    return img

def cabin_door_302am(img):
    # the cabin door at 3:02 AM · figure on the porch · rain
    vgrad(img, (10, 12, 22), (20, 22, 34))
    d = ImageDraw.Draw(img)
    # porch frame + door
    d.rectangle([390, 130, 890, 720], fill=(30, 24, 20))
    d.rectangle([440, 180, 840, 720], fill=(48, 38, 30))
    d.rectangle([500, 240, 780, 720], fill=(64, 48, 34))   # the door
    d.rectangle([520, 260, 760, 700], fill=(56, 42, 30))
    d.ellipse([730, 470, 754, 494], fill=(150, 138, 110))   # knob
    # the figure — a darker absence against the door, rimmed faintly
    d.polygon([(600, 300), (680, 300), (700, 720), (580, 720)], fill=(14, 13, 18))
    d.ellipse([606, 236, 674, 306], fill=(14, 13, 18))
    d.arc([602, 232, 678, 310], 200, 340, fill=(90, 96, 120), width=3)
    rain(d, "302", (70, 78, 104))
    return img

def the_form(img):
    # each of them sees something different — concentric almosts
    vgrad(img, (16, 14, 24), (28, 22, 36))
    d = ImageDraw.Draw(img)
    n = rng("form")
    cx, cy = 640, 360
    for ring in range(9):
        r = 60 + ring * 34
        pts = []
        steps = 72
        for i in range(steps + 1):
            a = (i / steps) * 2 * math.pi
            wob = 1.0 + (n() - 0.5) * 0.22
            pts.append((cx + r * wob * math.cos(a),
                        cy + r * wob * 0.82 * math.sin(a)))
        v = 44 + ring * 9
        d.line(pts, fill=(v, v - 6, v + 12), width=2)
    # the almost-figure at center · shoulders, or a bowl, or a bell
    d.polygon([(590, 420), (690, 420), (665, 300), (615, 300)], fill=(52, 44, 66))
    d.ellipse([612, 252, 668, 308], fill=(52, 44, 66))
    return img

def wall_milk_crate(img):
    # the wall · Lena's milk crate at its foot · 6:30 AM light
    vgrad(img, (110, 96, 92), (170, 140, 110), 0, 400)
    vgrad(img, (170, 140, 110), (94, 80, 66), 400, H)
    d = ImageDraw.Draw(img)
    # the wall — a long dark plane
    d.rectangle([0, 240, W, 560], fill=(58, 52, 50))
    for x in range(0, W, 86):
        d.line([(x, 240), (x, 560)], fill=(50, 45, 44), width=2)
    d.line([(0, 380), (W, 380)], fill=(50, 45, 44), width=2)
    # dawn rim on the wall top
    d.line([(0, 240), (W, 240)], fill=(214, 168, 118), width=4)
    # the milk crate, small against it
    d.rectangle([586, 500, 694, 560], fill=(140, 52, 40))
    for i in range(1, 4):
        d.line([(586 + i * 27, 500), (586 + i * 27, 560)], fill=(96, 36, 28), width=3)
    d.line([(586, 530), (694, 530)], fill=(96, 36, 28), width=3)
    # long morning shadow
    d.polygon([(586, 560), (694, 560), (860, 620), (700, 620)], fill=(74, 62, 52))
    return img

def floured_hand(img):
    # Hans's floured hand on Tem's face · Sunday morning
    vgrad(img, (40, 30, 30), (26, 18, 20))
    d = ImageDraw.Draw(img)
    # a face in profile, dark, filling the right
    d.polygon([(700, 120), (980, 200), (1030, 420), (940, 660), (700, 720),
               (700, 120)], fill=(58, 42, 38))
    d.ellipse([640, 100, 1060, 700], outline=(58, 42, 38), width=0)
    d.polygon([(660, 140), (1040, 240), (1060, 560), (900, 700), (640, 680)],
              fill=(64, 46, 40))
    # the floured hand print — pale, five fingers, unmistakable
    palm = (228, 220, 204)
    d.ellipse([760, 330, 900, 470], fill=palm)
    for i, (fx, fy, fl) in enumerate([(760, 300, 66), (800, 272, 84),
                                       (844, 264, 92), (886, 280, 80),
                                       (912, 330, 56)]):
        d.ellipse([fx, fy, fx + 34, fy + fl], fill=palm)
    # flour dust
    n = rng("flour")
    for _ in range(120):
        x = 700 + n() * 280
        y = 260 + n() * 280
        d.ellipse([x, y, x + 2, y + 2], fill=(210, 202, 188))
    return img

def tower_portal_door(img):
    # the portal-room door · cedar · six-by-six window at chest height
    vgrad(img, (22, 22, 30), (14, 14, 20))
    d = ImageDraw.Draw(img)
    # stone corridor walls converging
    d.polygon([(0, 0), (360, 140), (360, 620), (0, 720)], fill=(34, 34, 42))
    d.polygon([(1280, 0), (920, 140), (920, 620), (1280, 720)], fill=(30, 30, 38))
    d.rectangle([360, 620, 920, 720], fill=(26, 26, 32))
    # the door
    d.rectangle([460, 150, 820, 620], fill=(96, 66, 42))
    d.rectangle([480, 170, 800, 600], fill=(110, 76, 48))
    for yy in range(170, 600, 62):
        d.line([(480, yy), (800, yy)], fill=(88, 60, 38), width=2)
    # the small window, chest height, LIT from the other side
    d.rectangle([604, 360, 676, 432], fill=(40, 30, 22))
    d.rectangle([612, 368, 668, 424], fill=(196, 220, 190))
    d.rectangle([624, 380, 656, 412], fill=(232, 244, 224))
    # light through it, a thin beam on the floor
    d.polygon([(612, 424), (668, 424), (760, 700), (520, 700)], fill=(52, 56, 48))
    return img

def box_of_three_sticks(img):
    # three sticks · ESTUARY 7 — INES ROCHA 2046
    vgrad(img, (36, 32, 30), (22, 19, 18))
    d = ImageDraw.Draw(img)
    # the box, open, slight top-down
    d.polygon([(360, 300), (920, 300), (980, 560), (300, 560)], fill=(70, 52, 36))
    d.polygon([(390, 320), (890, 320), (940, 540), (340, 540)], fill=(44, 32, 24))
    # three cartridges
    for i, (x, c) in enumerate([(430, (90, 96, 110)), (610, (110, 96, 84)),
                                 (790, (128, 118, 96))]):
        d.polygon([(x, 350), (x + 120, 350), (x + 136, 512), (x - 16, 512)], fill=c)
        d.rectangle([x + 18, 372, x + 102, 412], fill=(30, 27, 24))
    # the third's label, brighter — the hand-lettered one
    d.rectangle([806, 368, 912, 416], fill=(214, 204, 182))
    for yy in (380, 392, 404):
        d.line([(814, yy), (904, yy)], fill=(88, 74, 58), width=2)
    return img

def estuary_7_opening(img):
    # Estuary 7 · planner's view · the river down from the cedars
    vgrad(img, (188, 168, 128), (120, 124, 104), 0, 300)
    vgrad(img, (120, 124, 104), (60, 72, 66), 300, H)
    d = ImageDraw.Draw(img)
    # ridge line
    d.polygon([(0, 300), (240, 220), (520, 280), (820, 200), (1120, 270),
               (1280, 240), (1280, 340), (0, 340)], fill=(52, 64, 54))
    # cedars on the ridge
    for x, h in [(120, 90), (300, 70), (460, 96), (700, 80), (900, 100),
                 (1060, 76), (1210, 88)]:
        cedar(d, x, 320, h, (38, 50, 42))
    # the river, coming down in bends
    pts = [(640, 330), (560, 400), (700, 470), (580, 540), (720, 610),
           (620, 680), (700, 720)]
    for wdt, col in [(64, (86, 104, 108)), (40, (110, 132, 134))]:
        d.line(pts, fill=col, width=wdt, joint="curve")
    # the bar of sand at the mouth
    d.ellipse([420, 640, 900, 760], fill=(178, 158, 118))
    return img

def blank_template(img):
    # the blank template · schematic: river / bar / flats / bluff / ridge
    img.paste(Image.new("RGB", (W, H), (214, 206, 186)), (0, 0))
    d = ImageDraw.Draw(img)
    ink = (92, 84, 70)
    faint = (150, 142, 124)
    # drafting frame
    d.rectangle([90, 70, 1190, 650], outline=ink, width=3)
    # ridge (top band)
    d.line([(90, 180), (1190, 180)], fill=faint, width=2)
    for x in range(140, 1160, 90):
        d.polygon([(x, 176), (x - 18, 150), (x + 18, 150)], outline=ink, width=2)
    # bluff
    d.line([(90, 300), (620, 300), (700, 250), (1190, 250)], fill=ink, width=3)
    # the river — one drafted meander
    d.line([(640, 180), (560, 300), (700, 400), (580, 500), (660, 650)],
           fill=ink, width=4, joint="curve")
    # flats hatching
    for i in range(14):
        y = 430 + i * 14
        d.line([(140 + i * 8, y), (520 - i * 4, y)], fill=faint, width=1)
    # the bar of sand — dotted ellipse
    n = rng("template")
    for i in range(64):
        a = i / 64 * 2 * math.pi
        x = 640 + 190 * math.cos(a)
        y = 590 + 40 * math.sin(a)
        d.ellipse([x, y, x + 3, y + 3], fill=ink)
    return img

def freq_interlude_ii(img):
    # the minute Finn's radio goes quiet
    vgrad(img, (12, 16, 18), (18, 24, 26))
    d = ImageDraw.Draw(img)
    n = rng("freq")
    # a live waveform that flatlines at the golden section
    mid = 380
    quiet_x = int(W * 0.62)
    pts = []
    x = 40
    while x < quiet_x:
        amp = 90 * (0.4 + n() * 0.6)
        pts.append((x, mid + (n() - 0.5) * 2 * amp))
        x += 6
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=(96, 168, 152), width=2)
    d.line([(quiet_x, mid), (W - 40, mid)], fill=(96, 168, 152), width=2)
    # the dial glow, dimming past the quiet point
    d.rectangle([40, 560, W - 40, 600], fill=(24, 32, 34))
    d.rectangle([40, 560, quiet_x, 600], fill=(38, 52, 54))
    d.line([(quiet_x, 540), (quiet_x, 620)], fill=(150, 190, 178), width=3)
    # faint scale ticks
    for x in range(60, W - 40, 44):
        d.line([(x, 596), (x, 604)], fill=(60, 78, 80), width=1)
    return img


PLATES = {
    "vol7_smolvud_alley_night":   (smolvud_alley_night, (18, 18, 30)),
    "vol7_four_bowls_cedar":      (four_bowls_cedar, (30, 24, 20)),
    "vol7_olafs_bell":            (olafs_bell, (22, 24, 28)),
    "vol7_cabin_door_302am":      (cabin_door_302am, (12, 14, 24)),
    "vol7_the_form":              (the_form, (18, 16, 26)),
    "vol7_the_wall_milk_crate":   (wall_milk_crate, (100, 88, 80)),
    "vol7_floured_hand_on_face":  (floured_hand, (34, 26, 26)),
    "vol7_tower_portal_door":     (tower_portal_door, (18, 18, 26)),
    "vol7_box_of_three_sticks":   (box_of_three_sticks, (28, 25, 24)),
    "vol7_estuary_7_opening":     (estuary_7_opening, (150, 140, 110)),
    "vol7_blank_template":        (blank_template, (214, 206, 186)),
    "vol7_freq_interlude_ii":     (freq_interlude_ii, (14, 18, 20)),
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, (fn, bg) in sorted(PLATES.items()):
        img = base(bg)
        img = fn(img)
        img = grain(img, name)
        img = vignette(img)
        img = deckle(img, name)
        path = os.path.join(OUT, name + ".png")
        img.save(path, optimize=True)
        print("wrote", os.path.relpath(path))


if __name__ == "__main__":
    main()
