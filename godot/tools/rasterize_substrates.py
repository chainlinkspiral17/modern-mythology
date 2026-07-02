"""Pre-rasterize substrate JSON files to PNGs.

Godot's RichTextLabel BBCode renderer chokes on substrates over
~5k cells (measured 13s freeze on a 24k-cell mosaic). This tool
walks every substrate JSON in resources/substrates/gallery/ and
renders it into a PNG using PIL — drawing each half-block cell
directly as a small rectangle. The result is a tiny image that
Godot loads instantly via Image.load_from_file.

Output: same directory, same basename, .png extension.

Usage:
    python3 godot/tools/rasterize_substrates.py
    python3 godot/tools/rasterize_substrates.py --only gallery/fool
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from PIL import Image

SUB_ROOT = Path("godot/resources/substrates")
GALLERY = SUB_ROOT / "gallery"

# Cell rendering size in pixels. Bigger → sharper visuals + bigger PNG.
# Half-block character (▀ = top half FG + bottom half BG) means CELL_H
# wants to be even. 6x12 gives detailed gallery view without bloating
# the PNGs to insanity.
CELL_W = 6
CELL_H = 12


def parse_color(s) -> tuple:
    """`#rrggbb` → (r, g, b)."""
    if not s:
        return (0, 0, 0)
    s = str(s).lstrip("#")
    if len(s) == 6:
        return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
    if len(s) == 3:
        return tuple(int(c * 2, 16) for c in s)
    return (0, 0, 0)


def render_cells(data: dict) -> Image.Image:
    cells = data.get("cells", [])
    if not cells:
        return Image.new("RGBA", (4, 4), (0, 0, 0, 0))
    rows = len(cells)
    cols = max(len(r) for r in cells)
    img = Image.new("RGBA", (cols * CELL_W, rows * CELL_H), (0, 0, 0, 255))
    px = img.load()
    half_h = CELL_H // 2
    for y, row in enumerate(cells):
        for x, cell in enumerate(row):
            if cell is None:
                continue
            c = cell.get("c", " ")
            fg = parse_color(cell.get("fg"))
            bg = parse_color(cell.get("bg")) if "bg" in cell else fg
            base_x = x * CELL_W
            base_y = y * CELL_H
            # Render half-block characters as solid color rectangles.
            # ▀ (upper) → top half = fg, bottom half = bg
            # ▄ (lower) → top half = bg, bottom half = fg
            # █ (full)  → entire cell = fg
            # everything else → solid fg
            if c == "▀":  # ▀
                top, bot = fg, bg
            elif c == "▄":  # ▄
                top, bot = bg, fg
            elif c == " ":
                top = bot = bg if "bg" in cell else (0, 0, 0)
            else:
                # full block, glyphs, etc. — just solid fg
                top = bot = fg
            for dy in range(half_h):
                for dx in range(CELL_W):
                    px[base_x + dx, base_y + dy] = top + (255,)
            for dy in range(half_h, CELL_H):
                for dx in range(CELL_W):
                    px[base_x + dx, base_y + dy] = bot + (255,)
    return img


def process(path: Path) -> None:
    out = path.with_suffix(".png")
    with open(path) as f:
        data = json.load(f)
    img = render_cells(data)
    img.save(out)
    print(f"  {path.name:48s} → {img.size[0]}x{img.size[1]}px {out.name}")


def main():
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]
    targets = []
    for f in sorted(GALLERY.iterdir()):
        if f.suffix != ".json" or not f.stem.endswith("_clean_blocks"):
            continue
        if only and only not in str(f):
            continue
        targets.append(f)
    print(f"Rasterizing {len(targets)} substrates...")
    for t in targets:
        try:
            process(t)
        except Exception as e:
            print(f"  ! {t.name}: {e}")


if __name__ == "__main__":
    main()
