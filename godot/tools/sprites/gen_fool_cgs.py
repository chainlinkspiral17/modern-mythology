#!/usr/bin/env python3
"""TAROT GAUNTLET · the eight Fool win/loss CGs.

TarotGauntletGame.gd has referenced res://assets/cg/fool_*.png
since the Fool's narrative pass; the files never existed (silent
null). This authors them: 320x180 pixel paintings in the house
dusk-scene language — Bayer-dithered gradients, silhouettes, one
light source each. Deterministic; run twice, diff clean.

Run from repo root: python3 godot/tools/sprites/gen_fool_cgs.py
"""
import os, zlib, struct

W, H = 320, 180
OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "assets", "cg"))

BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]


def bayer(x, y):
    return (BAYER[(y % 4) * 4 + (x % 4)] + 0.5) / 16.0


def h01(x, y, s):
    n = (x * 374761393 + y * 668265263 + s * 1442695041) & 0xFFFFFFFFFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFFFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65536.0


def hexc(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Img:
    def __init__(self, fill):
        self.px = [[fill] * W for _ in range(H)]

    def put(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            self.px[y][x] = c

    def rect(self, x0, y0, w, h, c):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                self.put(x, y, c)

    def vgrad(self, y0, y1, stops):
        for y in range(y0, y1):
            f = (y - y0) / max(1, y1 - y0 - 1) * (len(stops) - 1)
            i = min(int(f), len(stops) - 2)
            for x in range(W):
                self.px[y][x] = stops[i + 1] if (f - i) > bayer(x, y) else stops[i]

    def glow(self, cx, cy, r, c, amt=0.6):
        for y in range(max(0, cy - r), min(H, cy + r + 1)):
            for x in range(max(0, cx - r), min(W, cx + r + 1)):
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / r
                if d < 1.0 and (1.0 - d) * amt > bayer(x, y):
                    self.px[y][x] = c

    def figure(self, cx, base, h, c):
        """Small standing silhouette, head + body + legs."""
        hd = max(2, h // 6)
        self.rect(cx - hd // 2, base - h, hd, hd, c)                    # head
        self.rect(cx - hd, base - h + hd + 1, hd * 2, h - hd * 2 - 1, c)  # body
        self.rect(cx - hd + 1, base - hd, hd - 1, hd, c)                # legs
        self.rect(cx + 1, base - hd, hd - 1, hd, c)

    def save(self, path):
        raw = b""
        for y in range(H):
            raw += b"\x00" + bytes(v for px in self.px[y] for v in px)
        def chunk(t, d):
            c = t + d
            return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
        png += chunk(b"IDAT", zlib.compress(raw, 9))
        png += chunk(b"IEND", b"")
        open(path, "wb").write(png)


NIGHT = [hexc("0a0812"), hexc("141024"), hexc("241a38"), hexc("38284a")]
SODIUM = hexc("d89040")
INK = hexc("100c14")
CREAM = hexc("e9d090")
RED = hexc("c03028")


def leap_parking_lot():
    im = Img(NIGHT[0])
    im.vgrad(0, 110, NIGHT)
    for i in range(40):                                    # stars
        im.put(int(h01(i, 1, 3) * W), int(h01(1, i, 3) * 50), hexc("8890a0"))
    im.rect(0, 110, W, 70, hexc("201828"))                 # asphalt
    im.glow(200, 60, 70, mix(NIGHT[3], SODIUM, 0.25), 0.5)
    im.rect(198, 30, 4, 84, INK)                           # lamp post
    im.rect(190, 26, 20, 6, INK)
    im.glow(200, 34, 12, SODIUM, 0.9)
    im.glow(200, 118, 46, mix(hexc("201828"), SODIUM, 0.35), 0.55)  # light pool
    for k in range(5):                                     # painted stalls
        x = 30 + k * 60
        im.rect(x, 140, 3, 30, hexc("585060"))
    im.figure(166, 132, 34, INK)                           # the Fool, edge of the light
    im.rect(140, 128, 24, 3, hexc("0c0a10"))               # long shadow, away from it
    return im


def leap_river_window():
    im = Img(hexc("16121a"))
    for y in range(H):                                     # dark room wall
        for x in range(W):
            if h01(x, y, 7) < 0.04:
                im.put(x, y, hexc("1c1622"))
    wx, wy, ww, wh = 100, 30, 120, 100                     # the window
    im.rect(wx - 6, wy - 6, ww + 12, wh + 12, hexc("2a2230"))
    # moonlit river inside the frame
    for y in range(wy, wy + wh):
        t = (y - wy) / wh
        for x in range(wx, wx + ww):
            c = mix(hexc("1a2238"), hexc("30405c"), t)
            im.put(x, y, c)
    for y in range(wy + 55, wy + wh):                      # the river bend
        sway = int(18 * ((y - wy - 55) / 45.0) ** 1.5)
        for x in range(wx + 30 - sway, wx + 74 - sway):
            gl = mix(hexc("485a78"), hexc("b8c4d8"), h01(x, y, 5) * 0.5)
            if bayer(x, y) < 0.75:
                im.put(x, y, gl)
    im.glow(wx + 84, wy + 18, 10, hexc("d8dce8"), 0.95)    # the moon
    im.rect(wx + ww // 2 - 2, wy, 4, wh, hexc("2a2230"))   # mullion
    im.rect(wx, wy + wh // 2 - 2, ww, 4, hexc("2a2230"))
    im.figure(70, 150, 40, INK)                            # watching from the dark
    return im


def leap_precipice_door():
    im = Img(NIGHT[0])
    im.vgrad(0, 120, NIGHT)
    for i in range(60):
        im.put(int(h01(i, 2, 9) * W), int(h01(2, i, 9) * 90), hexc("8890a0"))
    for y in range(120, H):                                # the precipice
        edge = 190 - (y - 120) * 2
        for x in range(0, edge):
            im.put(x, y, mix(hexc("181220"), hexc("241a2c"), h01(x, y, 4) * 0.6))
    im.rect(120, 60, 34, 62, hexc("2a2230"))               # door frame, freestanding
    im.rect(124, 64, 26, 58, CREAM)                        # light through it
    for y in range(64, 122):                               # warm spill
        for x in range(124, 150):
            if bayer(x, y) < 0.3:
                im.put(x, y, mix(CREAM, SODIUM, 0.4))
    im.glow(137, 130, 30, mix(hexc("181220"), CREAM, 0.3), 0.4)
    im.figure(105, 122, 30, INK)                           # one step from it
    return im


def finale_wipe_forever():
    im = Img(hexc("181420"))
    im.rect(0, 0, W, 40, hexc("100c14"))
    im.rect(20, 36, 280, 6, hexc("c8d0d8"))                # fluorescent tube
    im.glow(160, 40, 90, mix(hexc("181420"), hexc("c8d0d8"), 0.18), 0.4)
    im.rect(0, 120, W, 60, hexc("241c28"))                 # floor
    im.rect(60, 90, 200, 34, hexc("3a3040"))               # the counter
    im.rect(60, 88, 200, 4, hexc("585068"))
    im.figure(150, 92, 34, INK)                            # bent to the work
    im.rect(158, 86, 10, 3, hexc("d8d0c0"))                # the cloth
    im.glow(163, 87, 7, hexc("e8e4d8"), 0.5)               # the spot, clean, again
    im.rect(272, 60, 26, 22, hexc("100c14"))               # wall clock
    im.glow(285, 71, 9, hexc("202830"), 0.9)
    im.put(285, 71, RED)
    return im


def finale_24_hour_diner():
    im = Img(NIGHT[0])
    im.vgrad(0, 100, NIGHT)
    im.rect(0, 100, W, 80, hexc("141020"))                 # lot
    im.rect(50, 60, 220, 60, hexc("221a28"))               # the diner
    im.rect(50, 54, 220, 8, hexc("30283a"))
    for k in range(4):                                     # glowing windows
        x = 66 + k * 52
        im.rect(x, 72, 36, 30, mix(SODIUM, CREAM, 0.5))
        for yy in range(72, 102):
            for xx in range(x, x + 36):
                if bayer(xx, yy) < 0.25:
                    im.put(xx, yy, SODIUM)
    im.figure(118, 102, 22, hexc("0e0a12"))                # one customer inside
    im.rect(140, 30, 60, 16, hexc("100c14"))               # sign
    im.glow(170, 38, 26, mix(NIGHT[1], RED, 0.5), 0.55)
    im.rect(148, 34, 44, 8, RED)                           # OPEN, always
    im.glow(160, 120, 80, mix(hexc("141020"), SODIUM, 0.2), 0.35)
    return im


def finale_empty_room():
    im = Img(hexc("16121c"))
    im.rect(0, 130, W, 50, hexc("221a26"))                 # floor
    im.rect(0, 128, W, 3, hexc("2e2434"))                  # skirting
    im.rect(220, 30, 70, 80, hexc("242c40"))               # window, pre-dawn
    im.vgrad(30, 110, [hexc("242c40"), hexc("38405c")])
    im.rect(220, 30, 70, 80, hexc("242c40"))
    for y in range(30, 110):
        t = (y - 30) / 80
        for x in range(220, 290):
            im.put(x, y, mix(hexc("222a3e"), hexc("3a4460"), t))
    im.rect(252, 30, 4, 80, hexc("1c1622"))                # mullion
    # the light parallelogram on the floor
    for y in range(132, 168):
        off = (y - 132) * 2
        for x in range(180 - off, 262 - off):
            if bayer(x, y) < 0.4:
                im.put(x, y, mix(hexc("221a26"), hexc("48506a"), 0.8))
    return im


def finale_room_listens():
    im = finale_empty_room()
    # the same room. a chair faces the wall. the light casts TWO ways.
    im.rect(60, 104, 22, 4, hexc("100c14"))                # chair seat
    im.rect(60, 108, 3, 22, hexc("100c14"))
    im.rect(79, 108, 3, 22, hexc("100c14"))
    im.rect(60, 84, 3, 22, hexc("100c14"))                 # back — facing the wall
    im.rect(60, 84, 14, 3, hexc("0c0a10"))
    for y in range(132, 158):                              # the second light, wrong way
        off = (y - 132) * 2
        for x in range(70 + off, 120 + off):
            if bayer(x, y) < 0.2:
                im.put(x, y, mix(hexc("221a26"), hexc("504058"), 0.7))
    return im


def finale_three_forty_seven():
    im = Img(hexc("0c0a12"))
    im.rect(240, 20, 60, 70, hexc("141828"))               # window, deep night
    for i in range(12):
        im.put(244 + int(h01(i, 4, 11) * 52), 24 + int(h01(4, i, 11) * 60), hexc("687088"))
    im.rect(30, 120, 110, 40, hexc("1a1420"))              # nightstand
    im.rect(44, 92, 82, 30, hexc("100c14"))                # the clock, huge in the dark
    im.glow(85, 106, 52, mix(hexc("0c0a12"), RED, 0.25), 0.5)
    # 3:47 in blocky segments
    def seg(x0, digit):
        segs = {"3": [(0,0,10,3),(7,0,3,16),(2,7,8,3),(0,13,10,3)],
                "4": [(0,0,3,10),(7,0,3,16),(0,7,10,3)],
                "7": [(0,0,10,3),(7,0,3,16)],
                ":": [(4,4,3,3),(4,10,3,3)]}
        for dx, dy, w2, h2 in segs[digit]:
            im.rect(x0 + dx, 98 + dy, w2, h2, RED)
    seg(50, "3"); seg(64, ":"); seg(78, "4"); seg(92, "7")
    return im


CGS = {
    "fool_leap_parking_lot": leap_parking_lot,
    "fool_leap_river_window": leap_river_window,
    "fool_leap_precipice_door": leap_precipice_door,
    "fool_finale_wipe_forever": finale_wipe_forever,
    "fool_finale_24_hour_diner": finale_24_hour_diner,
    "fool_finale_empty_room": finale_empty_room,
    "fool_finale_room_listens": finale_room_listens,
    "fool_finale_three_forty_seven": finale_three_forty_seven,
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in CGS.items():
        p = os.path.join(OUT, name + ".png")
        fn().save(p)
        print("wrote", p)


if __name__ == "__main__":
    main()
