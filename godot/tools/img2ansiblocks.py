#!/usr/bin/env python3
"""
Convert an image into mosaic *half-block* art in the project's substrate JSON
schema — the real "wizard of blocks" technique used by modern ANS artists.

Each output cell is the upper-half-block glyph ``▀`` carrying TWO colors:
foreground = the top sub-pixel, background = the bottom sub-pixel. That gives
two square sub-pixels per character cell. Colors are quantized to the 16-color
VGA/CP437 palette with Floyd–Steinberg dithering, which is what produces the
dense, hand-pixeled mosaic look (as opposed to a naive ░▒▓█ luminance ramp).

Output schema (identical to tools/img2ascii.py, consumed by AsciiSubstrate.gd):
  { "width", "height", "charset":"halfblock", "color":"fgbg",
    "source", "cells":[[{"c","fg","bg"}]] }

A cell whose two sub-pixels match collapses to a solid '█' (fg only) so flat
regions stay clean.
"""
import argparse, json, sys
from pathlib import Path
from PIL import Image

# Canonical 16-color VGA / CP437 / ANSI palette (low-intensity 0-7, high 8-15).
VGA16 = [
    (0x00, 0x00, 0x00), (0xAA, 0x00, 0x00), (0x00, 0xAA, 0x00), (0xAA, 0x55, 0x00),
    (0x00, 0x00, 0xAA), (0xAA, 0x00, 0xAA), (0x00, 0xAA, 0xAA), (0xAA, 0xAA, 0xAA),
    (0x55, 0x55, 0x55), (0xFF, 0x55, 0x55), (0x55, 0xFF, 0x55), (0xFF, 0xFF, 0x55),
    (0x55, 0x55, 0xFF), (0xFF, 0x55, 0xFF), (0x55, 0xFF, 0xFF), (0xFF, 0xFF, 0xFF),
]

UPPER_HALF = "▀"  # ▀
FULL_BLOCK = "█"  # █


def build_palette_image(palette):
    pal = Image.new("P", (1, 1))
    flat = []
    for rgb in palette:
        flat.extend(rgb)
    flat.extend(palette[0] * (256 - len(palette)))  # pad to 256 entries
    pal.putpalette(flat)
    return pal


def hex_color(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def convert(image_path, width, dither, bg_index, palette, mode="vga16", colors=12):
    img = Image.open(image_path).convert("RGB")
    iw, ih = img.size
    # Square sub-pixels: sub-grid is `width` wide; height keeps image aspect.
    sub_h = max(2, round(width * ih / iw))
    if sub_h % 2:
        sub_h += 1
    rows = sub_h // 2
    small = img.resize((width, sub_h), Image.LANCZOS)

    dmode = Image.FLOYDSTEINBERG if dither else Image.NONE
    if mode == "adaptive":
        # Harmonized sub-palette pulled from the image itself — avoids the
        # rainbow-confetti you get dithering smooth tones across raw VGA16.
        q = small.quantize(colors=colors, method=Image.MEDIANCUT, dither=dmode)
        flat = q.getpalette()
        palette = [tuple(flat[i:i + 3]) for i in range(0, colors * 3, 3)]
        # Treat the darkest palette entry as the transparent background.
        bg_index = min(range(len(palette)),
                       key=lambda i: sum(palette[i]))
        idx = q.load()
    else:
        pal_img = build_palette_image(palette)
        q = small.quantize(palette=pal_img, dither=dmode)
        idx = q.load()

    cells = []
    for r in range(rows):
        row = []
        for x in range(width):
            top = idx[x, 2 * r]
            bot = idx[x, 2 * r + 1]
            if top == bot:
                if top == bg_index:
                    row.append({"c": " "})  # empty -> substrate bg shows through
                else:
                    row.append({"c": FULL_BLOCK, "fg": hex_color(palette[top])})
            else:
                cell = {"c": UPPER_HALF, "fg": hex_color(palette[top])}
                cell["bg"] = None if bot == bg_index else hex_color(palette[bot])
                row.append(cell)
        cells.append(row)
    return {
        "width": width, "height": rows,
        "charset": "halfblock", "color": "fgbg",
        "source": Path(image_path).name,
        "cells": cells,
    }


def main():
    ap = argparse.ArgumentParser(description="Image -> VGA-16 half-block substrate JSON")
    ap.add_argument("image")
    ap.add_argument("-o", "--out", help="Output JSON path")
    ap.add_argument("-w", "--width", type=int, default=80, help="Grid width in cells")
    ap.add_argument("--no-dither", action="store_true", help="Disable Floyd-Steinberg dither")
    ap.add_argument("--bg-index", type=int, default=0,
                    help="Palette index treated as transparent (default 0 = black)")
    ap.add_argument("--mode", choices=["vga16", "adaptive"], default="adaptive",
                    help="vga16 = authentic palette; adaptive = harmonized image palette")
    ap.add_argument("--colors", type=int, default=12, help="adaptive palette size")
    args = ap.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        sys.exit(f"not found: {image_path}")

    data = convert(image_path, args.width, not args.no_dither, args.bg_index, VGA16,
                   mode=args.mode, colors=args.colors)
    out = Path(args.out) if args.out else image_path.with_suffix(".halfblock.json")
    out.write_text(json.dumps(data))
    print(out)


if __name__ == "__main__":
    main()
