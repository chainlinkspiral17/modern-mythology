#!/usr/bin/env python3
"""
Rasterize an ASCII substrate JSON (pieces/<id>.json) to a PNG.

Mirrors what AsciiSubstrateRaster.gd does at runtime: draws each cell with
SpaceMono at a chosen font size, respecting per-cell fg/bg. Transparent
bg (`null`) becomes alpha=0 in the output.

Used to bake portrait substrates into PNGs the CharLayer can load directly
without spinning up a Godot SubViewport.
"""
import argparse, json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT_DEFAULT = Path(__file__).resolve().parent.parent / "resources/fonts/SpaceMono-Regular.ttf"


def parse_hex(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def tint_fg(fg_hex, tint):
    """Multiply an fg color by a tint (r,g,b in 0..1). Used for expression variants."""
    if fg_hex is None:
        return None
    r, g, b = parse_hex(fg_hex)
    tr, tg, tb = tint
    return (min(255, int(r * tr)), min(255, int(g * tg)), min(255, int(b * tb)))


# SpaceMono lacks the Unicode block-shading glyphs, so we paint them as
# fractional-alpha fills sized to the cell. Keys are Unicode code points.
BLOCK_FILL_ALPHA = {
    0x2591: 64,   # ░  light shade
    0x2592: 128,  # ▒  medium shade
    0x2593: 192,  # ▓  dark shade
    0x2588: 255,  # █  full block
}


def rasterize(piece_path, out_path, font_px, font_path, tint):
    data = json.loads(Path(piece_path).read_text())
    w = data["width"]
    h = data["height"]
    cells = data["cells"]

    font = ImageFont.truetype(str(font_path), font_px)
    # Use "M" (always present, full-cap height) to size the cell; "█" returns
    # the right bbox even when the font has no glyph for it.
    bbox = font.getbbox("M")
    cw = max(1, bbox[2] - bbox[0])
    ascent, descent = font.getmetrics()
    ch = ascent + descent
    x0_off = -bbox[0]

    img = Image.new("RGBA", (cw * w, ch * h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for cy, row in enumerate(cells):
        for cx, cell in enumerate(row):
            c = cell.get("c", " ")
            fg = cell.get("fg")
            bg = cell.get("bg")
            x = cx * cw
            y = cy * ch
            if bg is not None:
                br, bgc, bb = parse_hex(bg)
                draw.rectangle([x, y, x + cw, y + ch], fill=(br, bgc, bb, 255))
            if c == " " or c == "" or fg is None:
                continue
            rgb = tint_fg(fg, tint)
            cp = ord(c[0])
            if cp in BLOCK_FILL_ALPHA:
                a = BLOCK_FILL_ALPHA[cp]
                draw.rectangle([x, y, x + cw, y + ch], fill=(rgb[0], rgb[1], rgb[2], a))
            else:
                draw.text((x + x0_off, y), c, font=font, fill=(rgb[0], rgb[1], rgb[2], 255))

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    return img.size


# Expression tints — multipliers applied to fg color.
# Mono substrates (fg=#ffffff) take the tint full strength.
EXPRESSION_TINTS = {
    "neutral":   (1.00, 1.00, 1.00),
    "happy":     (1.00, 0.96, 0.80),  # warm
    "sad":       (0.72, 0.82, 1.00),  # cool blue
    "surprised": (1.00, 1.00, 0.78),  # bright warm
    "angry":     (1.00, 0.55, 0.50),  # red shift
    "tired":     (0.78, 0.82, 0.92),  # cool grey
}


def main():
    ap = argparse.ArgumentParser(description="Substrate JSON -> PNG rasterizer")
    ap.add_argument("piece")
    ap.add_argument("-o", "--out", required=True, help="Output PNG path")
    ap.add_argument("--font-px", type=int, default=12)
    ap.add_argument("--font", default=str(FONT_DEFAULT))
    ap.add_argument("--expr", default="neutral", help="Expression tint name")
    ap.add_argument("--all-expressions", action="store_true",
                    help="Emit one PNG per known expression. -o becomes a directory.")
    args = ap.parse_args()

    if args.all_expressions:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = Path(args.piece).stem.replace("_portrait", "")
        for expr, tint in EXPRESSION_TINTS.items():
            out = out_dir / f"{stem}_{expr}.png"
            sz = rasterize(args.piece, out, args.font_px, args.font, tint)
            print(f"{out}  {sz[0]}x{sz[1]}")
    else:
        tint = EXPRESSION_TINTS.get(args.expr, (1.0, 1.0, 1.0))
        sz = rasterize(args.piece, args.out, args.font_px, args.font, tint)
        print(f"{args.out}  {sz[0]}x{sz[1]}")


if __name__ == "__main__":
    main()
