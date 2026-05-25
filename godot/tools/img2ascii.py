#!/usr/bin/env python3
"""
Convert an image to an ASCII-art JSON grid.

Output schema:
{
  "width":  <cells>,
  "height": <cells>,
  "charset": "ascii" | "blocks" | "braille",
  "color":   "fg" | "fgbg" | "mono",
  "cells":  [ [ {"c": "#", "fg": "#rrggbb", "bg": "#rrggbb" | null}, ... ], ... ]
}

Cell character aspect is assumed ~0.5 (twice as tall as wide), so vertical
sampling is halved relative to horizontal to keep proportions.
"""
import argparse, json, sys
from pathlib import Path
from PIL import Image

RAMPS = {
    "ascii":   " .:-=+*#%@",
    "blocks":  " .:-=+*#%@░▒▓█",
}
CELL_ASPECT = 0.6  # Approximate; override per-font with --aspect (SpaceMono ≈ 0.37)

BRAILLE_BASE = 0x2800
BRAILLE_DOTS = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(0,3),(1,3)]


def luminance(px):
    r, g, b = px[0], px[1], px[2]
    return 0.2126*r + 0.7152*g + 0.0722*b


def avg_color(img, x0, y0, x1, y1):
    region = img.crop((x0, y0, x1, y1))
    px = region.resize((1, 1), Image.LANCZOS).getpixel((0, 0))
    return px[:3]


def hex_color(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def render_simple(img, width, ramp, color_mode, aspect=CELL_ASPECT):
    iw, ih = img.size
    cell_w = iw / width
    cell_h = cell_w / aspect
    height = max(1, int(ih / cell_h))
    cells = []
    for cy in range(height):
        row = []
        for cx in range(width):
            x0 = int(cx * cell_w); x1 = int((cx + 1) * cell_w)
            y0 = int(cy * cell_h); y1 = int((cy + 1) * cell_h)
            x1 = max(x0 + 1, x1); y1 = max(y0 + 1, y1)
            avg = avg_color(img, x0, y0, x1, y1)
            lum = luminance(avg) / 255.0
            ch = ramp[min(len(ramp) - 1, int(lum * len(ramp)))]
            cell = {"c": ch}
            if color_mode == "fg":
                cell["fg"] = hex_color(avg); cell["bg"] = None
            elif color_mode == "fgbg":
                cell["fg"] = hex_color(avg); cell["bg"] = hex_color(avg)
            else:
                cell["fg"] = "#ffffff"; cell["bg"] = None
            row.append(cell)
        cells.append(row)
    return cells, width, height


def render_braille(img, width, color_mode, threshold=0.5):
    iw, ih = img.size
    sub_w = width * 2
    cell_w = iw / sub_w
    cell_h = cell_w
    sub_h = max(4, int(ih / cell_h))
    sub_h -= sub_h % 4
    height = sub_h // 4
    gray = img.convert("L").resize((sub_w, sub_h), Image.LANCZOS)
    color_src = img.resize((sub_w, sub_h), Image.LANCZOS)
    px = gray.load(); cp = color_src.load()
    cells = []
    for cy in range(height):
        row = []
        for cx in range(width):
            bits = 0
            rs = gs = bs = n = 0
            for i, (dx, dy) in enumerate(BRAILLE_DOTS):
                sx = cx * 2 + dx; sy = cy * 4 + dy
                v = px[sx, sy] / 255.0
                lit = v > threshold
                if lit:
                    bits |= (1 << i)
                    c = cp[sx, sy]
                    rs += c[0]; gs += c[1]; bs += c[2]; n += 1
            ch = chr(BRAILLE_BASE + bits)
            if n == 0:
                avg = cp[cx * 2, cy * 4][:3]
            else:
                avg = (rs // n, gs // n, bs // n)
            cell = {"c": ch}
            if color_mode == "fg":
                cell["fg"] = hex_color(avg); cell["bg"] = None
            elif color_mode == "fgbg":
                cell["fg"] = hex_color(avg); cell["bg"] = hex_color(avg)
            else:
                cell["fg"] = "#ffffff"; cell["bg"] = None
            row.append(cell)
        cells.append(row)
    return cells, width, height


def convert(image_path, width, charset, color_mode, invert, aspect=CELL_ASPECT):
    img = Image.open(image_path).convert("RGB")
    if charset == "braille":
        cells, w, h = render_braille(img, width, color_mode)
    else:
        ramp = RAMPS[charset]
        if invert:
            ramp = ramp[::-1]
        cells, w, h = render_simple(img, width, ramp, color_mode, aspect)
    return {
        "width": w, "height": h,
        "charset": charset, "color": color_mode,
        "source": Path(image_path).name,
        "cells": cells,
    }


def main():
    ap = argparse.ArgumentParser(description="Image -> ASCII JSON grid")
    ap.add_argument("image")
    ap.add_argument("-o", "--out", help="Output JSON path (default: <image>.<variant>.json)")
    ap.add_argument("-w", "--width", type=int, default=80, help="Grid width in cells")
    ap.add_argument("--charset", choices=["ascii", "blocks", "braille"], default="ascii")
    ap.add_argument("--color", choices=["fg", "fgbg", "mono"], default="fg")
    ap.add_argument("--invert", action="store_true", help="Invert ramp (for dark-on-light)")
    ap.add_argument("--aspect", type=float, default=CELL_ASPECT,
                    help="Cell width/height ratio of the target font (SpaceMono ≈ 0.37)")
    ap.add_argument("--all-variants", action="store_true",
                    help="Emit every charset x color combo next to the image")
    args = ap.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        sys.exit(f"not found: {image_path}")

    out_dir = image_path.parent
    stem = image_path.stem

    if args.all_variants:
        written = []
        for cs in ("ascii", "blocks", "braille"):
            for cm in ("fg", "fgbg", "mono"):
                data = convert(image_path, args.width, cs, cm, args.invert, args.aspect)
                out = out_dir / f"{stem}.{cs}-{cm}.json"
                out.write_text(json.dumps(data))
                written.append(out)
        for p in written:
            print(p)
        return

    data = convert(image_path, args.width, args.charset, args.color, args.invert, args.aspect)
    out = Path(args.out) if args.out else out_dir / f"{stem}.{args.charset}-{args.color}.json"
    out.write_text(json.dumps(data))
    print(out)


if __name__ == "__main__":
    main()
