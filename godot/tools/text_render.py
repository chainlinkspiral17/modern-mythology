#!/usr/bin/env python3
"""
Render an image as ASCII using the characters of a narrative text as the
character vocabulary, mapped by per-cell luminance.

The bright regions of the image consume characters from the text stream
in order; dark regions stay empty. Result: the image's silhouette is
literally written out of the narrative.

  python3 tools/text_render.py path/to/img.png \
      --text resources/scenes/vol5/vol5_ch0_booth6.json \
      -w 80 \
      -o resources/substrates/pieces/fool_card_textual.json

If --text is a scene JSON (file containing a "nodes" array), narrative
fields (narrate / say / think) are extracted and concatenated.
Otherwise --text is read as a plain text file.

Output schema matches the substrate format from img2ascii.py.
"""
import argparse, json, sys
from pathlib import Path
from PIL import Image

CELL_ASPECT = 0.5


def extract_narrative_text(scene_path: Path) -> str:
    try:
        d = json.loads(scene_path.read_text())
    except json.JSONDecodeError:
        return scene_path.read_text()
    if not isinstance(d, dict) or "nodes" not in d:
        return scene_path.read_text()
    parts = []
    for node in d.get("nodes", []):
        t = node.get("t", "")
        if t == "narrate":
            parts.append(str(node.get("text", "")))
        elif t == "say":
            spk = str(node.get("char", "") or "").upper()
            parts.append(f"{spk}: {node.get('text', '')}")
        elif t == "think":
            parts.append(f"({node.get('text', '')})")
    return "  ".join(parts)


def clean_text_stream(text: str) -> list[str]:
    """Strip control chars; collapse repeated whitespace; keep punctuation."""
    out = []
    last_space = False
    for ch in text:
        if ch in "\n\r\t":
            ch = " "
        if ch == " ":
            if last_space:
                continue
            last_space = True
        else:
            last_space = False
        if 32 <= ord(ch) < 127:
            out.append(ch)
    return out


def render(image_path: Path, text: str, width: int,
           fg_high: str = "#ffffff",
           fg_mid:  str = "#7a8198",
           fg_low:  str = "#3a4258",
           shadow_bg: str | None = None,
           low_shadow_bg: str | None = None,
           high_threshold: float = 0.62,
           mid_threshold:  float = 0.32) -> dict:
    """
    shadow_bg     — applied as bg on every bright (high+mid) cell, giving
                    text a "boxed" backdrop for legibility (ASCII drop shadow)
    low_shadow_bg — bg on dark/empty cells; usually null. Set for total
                    field-fill effect.
    """
    img = Image.open(image_path).convert("L")
    iw, ih = img.size
    cell_w = iw / width
    cell_h = cell_w / CELL_ASPECT
    height = max(1, int(ih / cell_h))
    img = img.resize((width, height), Image.LANCZOS)
    px = img.load()

    stream = clean_text_stream(text)
    if not stream:
        stream = list("the fool walks off a cliff at the beginning of every retelling ")
    pos = 0

    cells = []
    for cy in range(height):
        row = []
        for cx in range(width):
            lum = px[cx, cy] / 255.0
            if lum >= high_threshold:
                ch = stream[pos % len(stream)]; pos += 1
                fg = fg_high
                bg = shadow_bg
            elif lum >= mid_threshold:
                ch = stream[pos % len(stream)]; pos += 1
                fg = fg_mid
                bg = shadow_bg
            else:
                ch = " "
                fg = fg_low
                bg = low_shadow_bg
            row.append({"c": ch, "fg": fg, "bg": bg})
        cells.append(row)

    return {
        "width": width,
        "height": height,
        "charset": "text-source",
        "color": "fg" if shadow_bg is None else "fgbg",
        "source": str(image_path.name),
        "cells": cells,
    }


def main():
    ap = argparse.ArgumentParser(description="Image rendered using narrative text as char vocab")
    ap.add_argument("image")
    ap.add_argument("--text", required=True,
                    help="Plain text file OR a scene JSON with narrative nodes")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("-w", "--width", type=int, default=80)
    ap.add_argument("--high", type=float, default=0.62,
                    help="Luminance above this gets bright text")
    ap.add_argument("--mid",  type=float, default=0.32,
                    help="Luminance above this gets mid-tone text")
    ap.add_argument("--fg-high", default="#ffffff")
    ap.add_argument("--fg-mid",  default="#7a8198")
    ap.add_argument("--shadow-bg", default=None,
                    help='Bg color on text cells (e.g. "#0e0a0a"). Acts as a '
                         'per-cell drop shadow that makes text legible against '
                         'any backdrop. Null = transparent.')
    args = ap.parse_args()

    text_path = Path(args.text)
    if not text_path.exists():
        sys.exit(f"text file not found: {text_path}")
    if text_path.suffix == ".json":
        text = extract_narrative_text(text_path)
    else:
        text = text_path.read_text()
    if not text.strip():
        sys.exit("no text extracted")

    img_path = Path(args.image)
    if not img_path.exists():
        sys.exit(f"image not found: {img_path}")

    data = render(img_path, text, args.width,
                  fg_high=args.fg_high, fg_mid=args.fg_mid,
                  shadow_bg=args.shadow_bg,
                  high_threshold=args.high, mid_threshold=args.mid)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data))
    print(out, f"  {data['width']}x{data['height']}  text chars used:", len(clean_text_stream(text)))


if __name__ == "__main__":
    main()
