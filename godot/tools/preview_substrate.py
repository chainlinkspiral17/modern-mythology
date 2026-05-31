#!/usr/bin/env python3
"""
Render a substrate JSON grid to a PNG for quick visual QA — block-glyph aware,
so half-block / box-drawing mosaic art previews crisply with no inter-cell gaps.
Block glyphs are drawn as fills; other glyphs fall back to a mono font.

Usage: preview_substrate.py grid.json -o out.png [--cell 7x14] [--bg #0a0a12]
"""
import argparse, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def hx(s, default=(0, 0, 0)):
    if not s:
        return default
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def blend(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("grid")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--cell", default="7x14", help="WxH px per cell")
    ap.add_argument("--bg", default="#0a0a12", help="canvas / transparent-cell color")
    args = ap.parse_args()

    cw, ch = (int(v) for v in args.cell.lower().split("x"))
    canvas_bg = hx(args.bg)
    data = json.loads(Path(args.grid).read_text())
    W, H = data["width"], data["height"]
    img = Image.new("RGB", (W * cw, H * ch), canvas_bg)
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_PATH, ch)
    except Exception:
        font = ImageFont.load_default()

    for cy, row in enumerate(data["cells"]):
        for cx, cell in enumerate(row):
            c = cell.get("c", " ")
            fg = hx(cell.get("fg"), (200, 200, 200))
            bgv = cell.get("bg")
            x0, y0 = cx * cw, cy * ch
            x1, y1 = x0 + cw, y0 + ch
            bg = hx(bgv) if bgv else canvas_bg
            if bgv:
                d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=bg)
            ym = y0 + ch // 2
            xm = x0 + cw // 2
            if c == " " or c == "":
                continue
            elif c == "█":
                d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=fg)
            elif c == "▀":
                d.rectangle([x0, y0, x1 - 1, ym - 1], fill=fg)
            elif c == "▄":
                d.rectangle([x0, ym, x1 - 1, y1 - 1], fill=fg)
            elif c == "▌":
                d.rectangle([x0, y0, xm - 1, y1 - 1], fill=fg)
            elif c == "▐":
                d.rectangle([xm, y0, x1 - 1, y1 - 1], fill=fg)
            elif c in "░▒▓":
                t = {"░": 0.25, "▒": 0.5, "▓": 0.75}[c]
                d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=blend(bg, fg, t))
            else:
                d.text((x0, y0), c, fill=fg, font=font)

    img.save(args.out)
    print(args.out)


if __name__ == "__main__":
    main()
