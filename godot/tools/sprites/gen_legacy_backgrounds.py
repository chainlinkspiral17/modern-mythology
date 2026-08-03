#!/usr/bin/env python3
"""gen_legacy_backgrounds.py — the 39 missing Vol 1/2 backgrounds.

Vols 1-2 predate the 3D-locale era; their scenes reference 2D
backgrounds that were never produced, so both volumes largely played
over black (found by vn_asset_audit's first run, audit finding 1.6).

These are full-screen BACKGROUNDS, not plates: no deckle margin,
compositions keep the center third calm (portraits and the dialogue
column live there), values kept low-contrast so 34px serif stays
legible on top. Vol 1 runs warm-dark urban nights (the literary
skin); Vol 2 runs muted coastal-Americana with a faint cool cast
(the signal skin). Same determinism contract as every generator
here: crc32 seeds, luminance-only grain, true radial vignette.

Output: godot/assets/backgrounds/*.jpg (the scenes reference .jpg).
Run twice → identical bytes.
"""
import os, math
from PIL import Image, ImageDraw

import gen_vol7_cgs as lib   # rng / vgrad / grain / vignette / stars / rain / cedar

W, H = 1280, 720
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "backgrounds")


# ── shared motifs ────────────────────────────────────────────────

def room(d, wall, floor, floor_y=470):
    d.rectangle([0, 0, W, floor_y], fill=wall)
    d.rectangle([0, floor_y, W, H], fill=floor)
    d.line([(0, floor_y), (W, floor_y)], fill=tuple(int(c * 0.8) for c in wall), width=3)

def window(d, x, y, w, h, sky, frame, panes=2):
    d.rectangle([x - 8, y - 8, x + w + 8, y + h + 8], fill=frame)
    d.rectangle([x, y, x + w, y + h], fill=sky)
    for i in range(1, panes):
        d.line([(x + w * i // panes, y), (x + w * i // panes, y + h)], fill=frame, width=6)
    d.line([(x, y + h // 2), (x + w, y + h // 2)], fill=frame, width=6)

def hang_lamp(d, x, y, col, r=26):
    d.line([(x, 0), (x, y - r)], fill=(30, 28, 26), width=3)
    d.polygon([(x - r, y), (x + r, y), (x + r * 2 // 3, y - r), (x - r * 2 // 3, y - r)], fill=(40, 36, 32))
    d.ellipse([x - r + 6, y - 10, x + r - 6, y + 10], fill=col)
    # pool of light on whatever is below
    d.ellipse([x - r * 3, H - 200, x + r * 3, H - 140], fill=tuple(min(255, int(c * 0.5)) for c in col))

def counter(d, y, face, top):
    d.rectangle([0, y, W, H], fill=face)
    d.rectangle([0, y - 18, W, y], fill=top)

def bottles(d, x0, y, n, seed):
    r = lib.rng(seed)
    for i in range(n):
        x = x0 + i * 34
        bh = 40 + int(r() * 30)
        col = [(90, 60, 40), (60, 80, 60), (80, 70, 50), (70, 60, 80)][int(r() * 4) % 4]
        d.rectangle([x, y - bh, x + 16, y], fill=col)
        d.rectangle([x + 5, y - bh - 12, x + 11, y - bh], fill=col)

def city_skyline(d, y, col, seed):
    r = lib.rng(seed)
    x = 0
    while x < W:
        bw = 60 + int(r() * 120)
        bh = 40 + int(r() * 160)
        d.rectangle([x, y - bh, x + bw, y], fill=col)
        for wy in range(int(y - bh + 12), int(y - 8), 22):
            for wx in range(x + 8, x + bw - 8, 26):
                if r() > 0.72:
                    d.rectangle([wx, wy, wx + 8, wy + 10], fill=(216, 180, 110))
        x += bw + int(r() * 30)

def road_v(d, horizon, road_col, edge_col):
    d.polygon([(W * 0.42, horizon), (W * 0.58, horizon), (W * 0.85, H), (W * 0.15, H)], fill=road_col)
    mid_y = horizon + 20
    while mid_y < H:
        t = (mid_y - horizon) / (H - horizon)
        seg = 10 + 40 * t
        wdt = 2 + 8 * t
        d.rectangle([W / 2 - wdt / 2, mid_y, W / 2 + wdt / 2, mid_y + seg], fill=edge_col)
        mid_y += seg * 2.2

def tree_line(d, y, col, seed, height=90):
    r = lib.rng(seed)
    x = -20
    while x < W + 20:
        th = height * (0.6 + r() * 0.7)
        tw = th * 0.9
        d.ellipse([x, y - th, x + tw, y + 10], fill=col)
        x += tw * 0.6

def sea(d, y, col, foam, t_seed):
    d.rectangle([0, y, W, H], fill=col)
    r = lib.rng(t_seed)
    for i in range(5):
        yy = y + 24 + i * ((H - y) // 6)
        amp = 4 + i * 2
        pts = [(x, yy + math.sin(x / 90.0 + r() * 6) * amp) for x in range(0, W + 1, 32)]
        d.line(pts, fill=foam, width=2)


# ── recipes ──────────────────────────────────────────────────────

def v1_faust_bedroom_night(img):
    d = ImageDraw.Draw(img)
    room(d, (30, 26, 34), (22, 19, 24), 480)
    window(d, 880, 120, 220, 260, (16, 20, 40), (20, 18, 22))
    lib.stars(d, "fbn", 22, 240, (170, 180, 205))
    d.rectangle([80, 380, 460, 480], fill=(44, 36, 44))       # the bed
    d.rectangle([80, 340, 460, 388], fill=(58, 50, 58))
    d.rectangle([60, 300, 100, 480], fill=(36, 30, 36))       # headboard
    hang_lamp(d, 640, 150, (196, 150, 92), 20)
    return img

def v1_faust_apartment_day(img):
    d = ImageDraw.Draw(img)
    room(d, (78, 72, 66), (58, 50, 44), 470)
    window(d, 160, 110, 260, 280, (168, 176, 186), (52, 46, 42))
    d.rectangle([860, 300, 1180, 470], fill=(64, 52, 44))     # easel table
    d.polygon([(940, 160), (1100, 160), (1080, 300), (960, 300)], fill=(96, 88, 78))  # the canvas
    d.rectangle([950, 176, 1070, 288], fill=(120, 108, 92))
    return img

def v1_jacob_apartment(img):
    d = ImageDraw.Draw(img)
    room(d, (58, 60, 56), (42, 40, 36), 470)
    window(d, 940, 130, 200, 240, (140, 150, 152), (44, 44, 40))
    for i in range(4):                                         # shelves
        d.rectangle([100, 150 + i * 70, 420, 162 + i * 70], fill=(40, 36, 30))
        bottles(d, 110, 150 + i * 70, 8, "jacob%d" % i)
    return img

def v1_wagner_home(img):
    d = ImageDraw.Draw(img)
    room(d, (72, 62, 52), (52, 42, 34), 470)
    window(d, 180, 120, 220, 250, (150, 158, 148), (56, 46, 38))
    d.rectangle([840, 330, 1180, 470], fill=(70, 52, 38))     # the couch
    d.rectangle([840, 280, 1180, 336], fill=(84, 62, 46))
    hang_lamp(d, 640, 130, (208, 168, 104), 22)
    return img

def v1_bar_interior(img):
    d = ImageDraw.Draw(img)
    room(d, (36, 28, 26), (26, 20, 18), 430)
    d.rectangle([0, 130, W, 260], fill=(30, 24, 22))          # backbar
    bottles(d, 60, 258, 34, "bar")
    counter(d, 430, (52, 38, 30), (86, 64, 44))
    for x in (240, 640, 1040):
        hang_lamp(d, x, 120, (200, 152, 88), 22)
    return img

def v1_bar_exterior_night(img):
    lib.vgrad(img, (12, 13, 24), (26, 24, 34))
    d = ImageDraw.Draw(img)
    lib.stars(d, "barx", 40, 200, (185, 190, 210))
    d.rectangle([120, 200, 900, 620], fill=(32, 26, 28))      # the bar building
    d.rectangle([150, 460, 300, 620], fill=(20, 16, 18))      # door
    d.rectangle([380, 300, 860, 420], fill=(48, 34, 34))      # sign band
    d.rectangle([400, 320, 840, 400], fill=(180, 84, 66))     # neon block
    d.rectangle([420, 336, 820, 384], fill=(226, 120, 92))
    d.polygon([(150, 620), (300, 620), (360, 700), (110, 700)], fill=(60, 44, 40))  # door spill
    return img

def v1_club_dance(img):
    lib.vgrad(img, (16, 10, 26), (30, 16, 40))
    d = ImageDraw.Draw(img)
    r = lib.rng("club")
    for i in range(7):                                         # light beams
        x = 100 + i * 180
        col = [(120, 60, 140), (60, 90, 160), (150, 70, 90)][i % 3]
        d.polygon([(x, 0), (x + 40, 0), (x + 220, H), (x - 140, H)], fill=tuple(int(c * 0.5) for c in col))
    d.rectangle([0, 560, W, H], fill=(24, 14, 32))            # floor
    for i in range(16):                                        # floor glints
        x, y = r() * W, 570 + r() * 130
        d.ellipse([x, y, x + 30, y + 8], fill=(70, 44, 90))
    return img

def v1_club_sharp(img):
    img = v1_club_dance(img)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 90], fill=(10, 6, 16))              # sharper, colder cut
    d.rectangle([0, H - 90, W, H], fill=(10, 6, 16))
    for x in range(0, W, 320):
        d.line([(x, 90), (x, H - 90)], fill=(40, 20, 56), width=2)
    return img

def v1_dream_bar(img):
    img = v1_bar_interior(img)
    d = ImageDraw.Draw(img)
    # the dream: the room's own colors, floating slightly wrong
    for i in range(5):
        y = 90 + i * 120
        d.line([(0, y), (W, y + 24)], fill=(120, 96, 150), width=2)
    d.ellipse([540, 200, 740, 400], outline=(150, 120, 180), width=3)
    return img

def v1_dream_bed(img):
    img = v1_faust_bedroom_night(img)
    d = ImageDraw.Draw(img)
    for i in range(6):
        r = 60 + i * 52
        d.ellipse([270 - r // 2, 400 - r // 3, 270 + r // 2, 400 + r // 3],
                  outline=(96, 84, 130), width=2)
    return img

def v1_grandparents_montage(img):
    lib.vgrad(img, (96, 84, 68), (70, 60, 50))
    d = ImageDraw.Draw(img)
    # three leaning photo rectangles, sepia
    for (x, y, w, h, tilt) in [(140, 150, 300, 220, -3), (520, 120, 320, 240, 2), (900, 170, 280, 210, -2)]:
        d.polygon([(x, y + tilt * 4), (x + w, y - tilt * 4), (x + w, y + h - tilt * 4), (x, y + h + tilt * 4)],
                  fill=(206, 190, 160))
        d.polygon([(x + 14, y + 14), (x + w - 14, y + 6), (x + w - 14, y + h - 22), (x + 14, y + h - 14)],
                  fill=(150, 128, 100))
    return img

def v1_jd_driving_night(img):
    lib.vgrad(img, (10, 11, 20), (22, 22, 30), 0, 360)
    d = ImageDraw.Draw(img)
    lib.stars(d, "jd", 30, 200, (170, 175, 195))
    road_v(d, 360, (30, 30, 36), (150, 140, 100))
    d.rectangle([0, 620, W, H], fill=(16, 14, 18))            # dashboard
    d.ellipse([220, 640, 420, 760], outline=(60, 56, 60), width=10)  # wheel arc
    d.ellipse([540, 350, 560, 366], fill=(220, 190, 130))     # far headlights
    d.ellipse([700, 352, 716, 364], fill=(200, 90, 80))
    return img

def v1_missing_link_interior(img):
    d = ImageDraw.Draw(img)
    room(d, (54, 46, 40), (40, 32, 28), 440)
    counter(d, 440, (60, 44, 34), (96, 74, 52))
    d.rectangle([0, 150, W, 240], fill=(46, 38, 34))          # menu board
    for i, x in enumerate(range(80, 1200, 200)):
        d.rectangle([x, 168, x + 150, 178], fill=(180, 160, 130))
        d.rectangle([x, 194, x + 110, 202], fill=(150, 132, 108))
    hang_lamp(d, 320, 120, (206, 160, 96), 20)
    hang_lamp(d, 960, 120, (206, 160, 96), 20)
    return img

def v1_missing_link_exterior(img):
    lib.vgrad(img, (26, 28, 44), (52, 48, 56))
    d = ImageDraw.Draw(img)
    lib.stars(d, "mlx", 26, 180, (180, 185, 200))
    d.rectangle([200, 260, 1080, 620], fill=(44, 38, 36))     # diner box
    d.rectangle([200, 230, 1080, 268], fill=(60, 50, 44))
    for x in range(260, 1040, 160):                            #窗 row
        d.rectangle([x, 340, x + 100, 470], fill=(212, 170, 100))
    d.rectangle([460, 150, 820, 226], fill=(56, 44, 48))      # sign
    d.rectangle([480, 164, 800, 212], fill=(224, 128, 96))
    return img

def v1_park_day(img):
    lib.vgrad(img, (170, 180, 186), (120, 136, 120), 0, 320)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 320, W, H], fill=(104, 118, 88))
    tree_line(d, 330, (74, 92, 66), "park", 110)
    d.polygon([(500, 720), (760, 720), (700, 430), (560, 430)], fill=(140, 132, 112))  # path
    d.rectangle([120, 430, 360, 470], fill=(96, 76, 56))      # bench
    d.rectangle([130, 470, 150, 520], fill=(80, 62, 46))
    d.rectangle([330, 470, 350, 520], fill=(80, 62, 46))
    return img

def v1_pharmacy_office(img):
    d = ImageDraw.Draw(img)
    room(d, (88, 92, 90), (70, 72, 68), 460)
    for i in range(3):
        d.rectangle([90 + i * 140, 140, 200 + i * 140, 400], fill=(78, 80, 76))
        for s in range(5):
            d.rectangle([96 + i * 140, 156 + s * 48, 194 + i * 140, 164 + s * 48], fill=(120, 122, 116))
    d.rectangle([760, 300, 1180, 460], fill=(96, 98, 94))     # desk
    d.rectangle([820, 240, 960, 300], fill=(60, 64, 66))      # monitor
    d.rectangle([0, 0, W, 60], fill=(150, 154, 150))          # fluorescent band
    return img

def v1_pharmacy_floor(img):
    d = ImageDraw.Draw(img)
    room(d, (96, 100, 98), (84, 88, 84), 430)
    for x in (180, 520, 860):                                  # aisles
        d.rectangle([x, 180, x + 240, 430], fill=(88, 90, 86))
        for s in range(4):
            d.rectangle([x + 8, 196 + s * 56, x + 232, 208 + s * 56], fill=(128, 130, 124))
            r = lib.rng("ph%d%d" % (x, s))
            for b in range(6):
                bx = x + 16 + b * 36
                d.rectangle([bx, 172 + s * 56 + 24, bx + 22, 196 + s * 56 + 12],
                            fill=[(150, 110, 100), (110, 130, 150), (150, 140, 100)][int(r() * 3) % 3])
    d.rectangle([0, 0, W, 56], fill=(158, 162, 158))
    return img

def v1_shuttle_bench(img):
    lib.vgrad(img, (34, 36, 52), (58, 56, 62))
    d = ImageDraw.Draw(img)
    lib.stars(d, "shb", 20, 160, (175, 180, 198))
    city_skyline(d, 300, (24, 26, 38), "shbcity")
    d.rectangle([0, 560, W, H], fill=(44, 44, 48))            # sidewalk
    d.rectangle([140, 400, 560, 430], fill=(88, 70, 50))      # the bench
    d.rectangle([140, 430, 560, 448], fill=(74, 58, 42))
    d.rectangle([160, 448, 180, 560], fill=(60, 48, 36))
    d.rectangle([520, 448, 540, 560], fill=(60, 48, 36))
    d.rectangle([900, 240, 916, 560], fill=(70, 72, 80))      # sign pole
    d.rectangle([860, 200, 1000, 248], fill=(90, 96, 120))    # SHUTTLE sign
    hang_lamp(d, 350, 160, (200, 170, 110), 18)
    return img

def v1_skatepark_day(img):
    lib.vgrad(img, (176, 184, 190), (140, 146, 148), 0, 340)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 340, W, H], fill=(128, 128, 124))
    d.ellipse([200, 380, 760, 640], fill=(108, 108, 106))     # the bowl
    d.ellipse([260, 410, 700, 610], fill=(96, 96, 96))
    d.polygon([(880, 340), (1180, 340), (1180, 480), (1020, 480)], fill=(118, 118, 114))  # ramp
    tree_line(d, 348, (96, 112, 84), "skate", 70)
    return img

# ── vol 2 ────────────────────────────────────────────────────────

def v2_briar_rest_stop(img):
    lib.vgrad(img, (150, 158, 158), (108, 120, 108), 0, 330)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 330, W, H], fill=(100, 110, 92))
    tree_line(d, 340, (66, 86, 64), "brs", 120)
    d.rectangle([160, 380, 560, 560], fill=(96, 82, 64))      # the rest-stop shelter
    d.polygon([(140, 380), (360, 300), (580, 380)], fill=(72, 60, 48))
    d.rectangle([760, 470, 1000, 500], fill=(90, 74, 54))     # picnic table
    d.rectangle([790, 500, 810, 560], fill=(76, 62, 46))
    d.rectangle([950, 500, 970, 560], fill=(76, 62, 46))
    return img

def v2_briar_trail(img):
    lib.vgrad(img, (140, 150, 146), (96, 110, 92), 0, 300)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 300, W, H], fill=(88, 100, 78))
    tree_line(d, 310, (58, 78, 58), "trail", 150)
    d.polygon([(560, 720), (820, 720), (700, 340), (640, 340)], fill=(122, 106, 82))  # the trail
    for cx, ch in [(220, 130), (1060, 150), (380, 100)]:
        lib.cedar(d, cx, 310, ch, (48, 66, 50))
    return img

def v2_briar_overlook(img):
    lib.vgrad(img, (168, 172, 176), (120, 132, 136), 0, 300)
    d = ImageDraw.Draw(img)
    d.polygon([(0, 300), (300, 250), (700, 310), (1280, 260), (1280, 380), (0, 380)], fill=(90, 102, 108))  # far hills
    d.rectangle([0, 380, W, H], fill=(70, 86, 78))            # valley
    d.polygon([(0, 560), (W, 520), (W, 720), (0, 720)], fill=(96, 92, 80))  # the ledge
    d.rectangle([420, 470, 440, 560], fill=(70, 60, 48))      # rail posts
    d.rectangle([820, 460, 840, 546], fill=(70, 60, 48))
    d.line([(420, 480), (840, 470)], fill=(84, 72, 56), width=6)
    return img

def v2_briar_building(img):
    d = ImageDraw.Draw(img)
    lib.vgrad(img, (152, 158, 160), (112, 120, 112), 0, 340)
    d.rectangle([0, 340, W, H], fill=(102, 108, 94))
    d.rectangle([300, 220, 980, 600], fill=(126, 108, 88))    # the lodge
    d.polygon([(270, 220), (640, 120), (1010, 220)], fill=(88, 72, 58))
    for x in (380, 600, 820):
        d.rectangle([x, 320, x + 110, 460], fill=(70, 78, 90))
    d.rectangle([560, 480, 720, 600], fill=(64, 52, 42))      # door
    return img

def v2_briar_picnic(img):
    img = v2_briar_rest_stop(img)
    d = ImageDraw.Draw(img)
    d.rectangle([600, 430, 980, 466], fill=(120, 98, 70))     # nearer table
    d.rectangle([640, 466, 660, 560], fill=(96, 78, 56))
    d.rectangle([920, 466, 940, 560], fill=(96, 78, 56))
    d.ellipse([700, 408, 760, 432], fill=(160, 60, 54))       # thermos
    return img

def v2_beach_night(img):
    lib.vgrad(img, (14, 16, 30), (30, 34, 46), 0, 330)
    d = ImageDraw.Draw(img)
    lib.stars(d, "bn", 60, 300, (190, 195, 215))
    d.ellipse([980, 80, 1080, 180], fill=(220, 220, 208))     # moon
    sea(d, 330, (26, 34, 48), (90, 104, 124), "bnsea")
    d.polygon([(0, 560), (W, 600), (W, 720), (0, 720)], fill=(70, 64, 54))  # sand
    return img

def v2_grunion_beach(img):
    img = v2_beach_night(img)
    d = ImageDraw.Draw(img)
    r = lib.rng("grunion")
    for i in range(60):                                        # the silver run
        x = r() * W
        y = 560 + r() * 80
        d.line([(x, y), (x + 10, y + 2)], fill=(198, 205, 215), width=2)
    return img

def v2_cannery_dawn(img):
    lib.vgrad(img, (150, 120, 96), (96, 84, 78), 0, 340)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 340, W, H], fill=(70, 68, 66))
    d.rectangle([180, 220, 1100, 560], fill=(84, 66, 56))     # cannery shed
    d.rectangle([180, 190, 1100, 228], fill=(60, 48, 42))
    d.rectangle([300, 90, 360, 220], fill=(74, 58, 50))       # stack
    for x in range(240, 1060, 140):
        d.rectangle([x, 300, x + 80, 400], fill=(52, 56, 64))
    d.rectangle([0, 620, W, H], fill=(50, 56, 60))            # wet lot
    return img

def v2_barn_interior(img):
    d = ImageDraw.Draw(img)
    room(d, (56, 42, 30), (44, 34, 24), 480)
    for x in range(0, W, 90):                                  # plank walls
        d.line([(x, 0), (x, 480)], fill=(48, 36, 26), width=3)
    d.polygon([(540, 0), (740, 0), (700, 160), (580, 160)], fill=(120, 104, 70))  # light shaft
    d.rectangle([120, 330, 420, 480], fill=(88, 70, 44))      # hay
    d.rectangle([160, 290, 380, 336], fill=(102, 82, 52))
    return img

def v2_crumpled_barn_ext(img):
    lib.vgrad(img, (140, 146, 152), (104, 112, 100), 0, 360)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 360, W, H], fill=(96, 104, 84))
    # the barn, leaning hard
    d.polygon([(360, 560), (900, 600), (860, 300), (480, 260)], fill=(96, 62, 50))
    d.polygon([(330, 300 + 40), (640, 160), (930, 340)], fill=(70, 50, 42))
    d.polygon([(560, 420), (700, 430), (690, 600), (570, 590)], fill=(40, 30, 26))  # the dark door
    tree_line(d, 366, (78, 94, 70), "cb", 80)
    return img

def v2_cliffside_circus(img):
    lib.vgrad(img, (120, 130, 146), (80, 92, 104), 0, 340)
    d = ImageDraw.Draw(img)
    d.polygon([(0, 340), (W, 380), (W, 720), (0, 720)], fill=(86, 82, 72))  # clifftop
    d.polygon([(0, 640), (W, 680), (W, 720), (0, 720)], fill=(60, 58, 52))  # cliff edge band
    # the big top, striped
    for i in range(8):
        x0 = 420 + i * 55
        col = (150, 68, 60) if i % 2 == 0 else (196, 186, 168)
        d.polygon([(x0, 480), (x0 + 55, 480), (640, 220)], fill=col)
    d.line([(640, 220), (640, 160)], fill=(90, 80, 70), width=4)
    d.polygon([(640, 160), (700, 184), (640, 200)], fill=(170, 76, 64))     # pennant
    return img

def v2_seagash_circus_old(img):
    img = v2_cliffside_circus(img)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=None)
    # faded overlay: mute it like an old photograph
    px = img.load()
    for y in range(0, H, 2):
        for x in range(0, W, 2):
            r0, g0, b0 = px[x, y]
            m = (r0 + g0 + b0) // 3
            px[x, y] = ((r0 + m * 2) // 3 + 14, (g0 + m * 2) // 3 + 10, (b0 + m * 2) // 3)
    return img

def v2_football_practice(img):
    lib.vgrad(img, (160, 168, 172), (110, 126, 104), 0, 320)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 320, W, H], fill=(92, 112, 76))
    for i in range(6):                                         # yard lines
        y = 380 + i * 56
        d.line([(0, y), (W, y - 14)], fill=(180, 190, 172), width=3)
    d.rectangle([600, 210, 616, 330], fill=(180, 178, 160))   # goal upright
    d.line([(560, 240), (656, 240)], fill=(180, 178, 160), width=6)
    d.line([(560, 240), (560, 210)], fill=(180, 178, 160), width=6)
    d.line([(656, 240), (656, 210)], fill=(180, 178, 160), width=6)
    return img

def v2_ice_storm(img):
    lib.vgrad(img, (120, 128, 140), (88, 96, 108))
    d = ImageDraw.Draw(img)
    tree_line(d, 420, (70, 80, 88), "ice", 140)
    d.rectangle([0, 420, W, H], fill=(126, 132, 142))
    lib.rain(d, "icestorm", (196, 204, 216), 520)
    return img

def v2_little_switzerland(img):
    lib.vgrad(img, (158, 166, 176), (112, 124, 120), 0, 300)
    d = ImageDraw.Draw(img)
    d.polygon([(0, 300), (240, 150), (460, 300)], fill=(120, 128, 138))     # peaks
    d.polygon([(380, 300), (680, 120), (980, 300)], fill=(132, 140, 150))
    d.polygon([(640, 172), (680, 120), (724, 176)], fill=(210, 214, 220))   # snowcap
    d.polygon([(900, 300), (1120, 180), (1280, 300)], fill=(118, 126, 136))
    d.rectangle([0, 300, W, H], fill=(96, 112, 88))
    d.rectangle([480, 420, 800, 560], fill=(112, 88, 62))     # chalet
    d.polygon([(450, 420), (640, 330), (830, 420)], fill=(80, 62, 48))
    return img

def v2_rec_center_dance(img):
    d = ImageDraw.Draw(img)
    room(d, (64, 56, 66), (48, 42, 50), 470)
    r = lib.rng("rec")
    for i in range(9):                                         # streamers
        x0 = 60 + i * 140
        d.arc([x0, 60, x0 + 200, 220], 200, 340, fill=(150, 90, 110), width=4)
    for i in range(14):                                        # floor scatter light
        gx = r() * (W - 40)
        gy = 480 + r() * 180
        d.ellipse([gx, gy, gx + 28, gy + 9], fill=(74, 62, 76))
    d.rectangle([980, 260, 1180, 470], fill=(56, 48, 58))     # speaker stack
    d.rectangle([1010, 290, 1150, 350], fill=(40, 34, 42))
    return img

def v2_road_running(img):
    lib.vgrad(img, (150, 158, 166), (108, 118, 108), 0, 340)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 340, W, H], fill=(100, 110, 88))
    road_v(d, 340, (96, 96, 98), (200, 196, 170))
    tree_line(d, 350, (74, 92, 68), "rr", 90)
    return img

def v2_small_town_road(img):
    lib.vgrad(img, (146, 152, 160), (110, 116, 108), 0, 330)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 330, W, H], fill=(104, 108, 96))
    road_v(d, 330, (92, 92, 94), (196, 192, 168))
    for (x, w, h) in [(80, 220, 180), (940, 260, 200)]:        # storefronts either side
        d.rectangle([x, 330 - h, x + w, 330 + 60], fill=(118, 100, 84))
        d.rectangle([x + 20, 330 - h + 30, x + w - 20, 330 - h + 90], fill=(88, 96, 108))
    return img

def v2_sapo_falls(img):
    lib.vgrad(img, (138, 150, 148), (92, 110, 100), 0, 280)
    d = ImageDraw.Draw(img)
    d.polygon([(0, 280), (420, 240), (520, 300), (W, 260), (W, 720), (0, 720)], fill=(72, 88, 78))
    d.rectangle([560, 240, 700, 560], fill=(168, 184, 190))   # the falls
    for x in range(566, 696, 18):
        d.line([(x, 250), (x, 556)], fill=(196, 208, 212), width=4)
    d.ellipse([460, 540, 820, 660], fill=(120, 142, 150))     # plunge pool
    lib.cedar(d, 220, 300, 130, (52, 72, 56))
    lib.cedar(d, 1080, 290, 150, (52, 72, 56))
    return img

def v2_school_newspaper(img):
    d = ImageDraw.Draw(img)
    room(d, (86, 84, 78), (66, 64, 58), 460)
    d.rectangle([0, 0, W, 54], fill=(140, 144, 140))          # fluorescents
    for x in (120, 700):                                       # paste-up tables
        d.rectangle([x, 320, x + 420, 460], fill=(104, 96, 82))
        r = lib.rng("news%d" % x)
        for i in range(6):
            px_, py = x + 20 + r() * 340, 330 + r() * 90
            d.rectangle([px_, py, px_ + 60, py + 40], fill=(190, 186, 172))
    d.rectangle([500, 140, 780, 300], fill=(72, 70, 66))      # corkboard
    for i in range(5):
        d.rectangle([516 + i * 50, 160 + (i % 2) * 60, 552 + i * 50, 210 + (i % 2) * 60], fill=(182, 178, 164))
    return img


RECIPES = {
    "vol1_faust_bedroom_night": v1_faust_bedroom_night,
    "vol1_faust_apartment_day": v1_faust_apartment_day,
    "vol1_jacob_apartment":     v1_jacob_apartment,
    "vol1_wagner_home":         v1_wagner_home,
    "vol1_bar_interior":        v1_bar_interior,
    "vol1_bar_exterior_night":  v1_bar_exterior_night,
    "vol1_club_dance":          v1_club_dance,
    "vol1_club_sharp":          v1_club_sharp,
    "vol1_dream_bar":           v1_dream_bar,
    "vol1_dream_bed":           v1_dream_bed,
    "vol1_grandparents_montage": v1_grandparents_montage,
    "vol1_jd_driving_night":    v1_jd_driving_night,
    "vol1_missing_link_interior": v1_missing_link_interior,
    "vol1_missing_link_exterior": v1_missing_link_exterior,
    "vol1_park_day":            v1_park_day,
    "vol1_pharmacy_office":     v1_pharmacy_office,
    "vol1_pharmacy_floor":      v1_pharmacy_floor,
    "vol1_shuttle_bench":       v1_shuttle_bench,
    "vol1_skatepark_day":       v1_skatepark_day,
    "vol2_briar_falls_rest_stop": v2_briar_rest_stop,
    "vol2_briar_falls_trail":   v2_briar_trail,
    "vol2_briar_falls_overlook": v2_briar_overlook,
    "vol2_briar_falls_building": v2_briar_building,
    "vol2_briar_falls_picnic":  v2_briar_picnic,
    "vol2_beach_night":         v2_beach_night,
    "vol2_grunion_beach":       v2_grunion_beach,
    "vol2_cannery_dawn":        v2_cannery_dawn,
    "vol2_barn_interior":       v2_barn_interior,
    "vol2_crumpled_barn_ext":   v2_crumpled_barn_ext,
    "vol2_cliffside_circus":    v2_cliffside_circus,
    "vol2_seagash_circus_old":  v2_seagash_circus_old,
    "vol2_football_practice":   v2_football_practice,
    "vol2_ice_storm":           v2_ice_storm,
    "vol2_little_switzerland":  v2_little_switzerland,
    "vol2_rec_center_dance":    v2_rec_center_dance,
    "vol2_road_running":        v2_road_running,
    "vol2_small_town_road":     v2_small_town_road,
    "vol2_sapo_falls":          v2_sapo_falls,
    "vol2_school_newspaper":    v2_school_newspaper,
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in sorted(RECIPES.items()):
        img = Image.new("RGB", (W, H), (20, 20, 20))
        img = fn(img)
        img = lib.grain(img, name, 5)
        img = lib.vignette(img, 0.34)
        path = os.path.join(OUT, name + ".jpg")
        img.save(path, quality=90)
        print("wrote", os.path.relpath(path))


if __name__ == "__main__":
    main()
