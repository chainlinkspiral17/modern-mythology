#!/usr/bin/env python3
"""
Build one Major-Arcana card surface:

  1. Inpaint the painted text out of the source PNG  -> <card>_clean.png
  2. Convert the clean art to a 560-cell mosaic substrate
  3. Overlay fresh, real text (SpaceMono) where the painted text was
  4. Emit a faithful PNG preview (proxy for the Godot render)

Card specs live in tools/arcana_specs/<card>.json:
  {
    "card": "fool",
    "source": "assets/gallery/fool.png",
    "width": 560,
    "elements": [
      { "box":[x0,y0,x1,y1],         # image-space text region to inpaint
        "lines":["..."],             # real text to lay back down
        "size": 40, "fg":"#f2eedc",
        "align":"left|center",
        "inpaint": true,
        "panel": "#0d0b08"|null }    # optional backing behind the new text
    ]
  }
Coordinates are in SOURCE-IMAGE pixels.
"""
import argparse, json, sys, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np, cv2

ROOT = Path(__file__).resolve().parent.parent      # godot/
FONT = ROOT / "resources/fonts/SpaceMono-Regular.ttf"
PREVIEW_CELL_W = 4                                  # px per mosaic cell in preview
BOX_MARGIN = 16                                     # px expansion to catch bleed


def inpaint_text(src_img, elements):
    arr = np.array(src_img.convert("RGB"))
    H, W = arr.shape[:2]
    mask = np.zeros((H, W), np.uint8)
    m = BOX_MARGIN
    for e in elements:
        if not e.get("inpaint", True):
            continue
        x0, y0, x1, y1 = e["box"]
        mask[max(0, y0 - m):min(H, y1 + m), max(0, x0 - m):min(W, x1 + m)] = 255
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)
    out = cv2.inpaint(arr, mask, 4, cv2.INPAINT_TELEA)
    return Image.fromarray(out)


def render_preview(mosaic_json, elements, scale, out_png):
    # Mosaic background, block-rectangle rendered (proxy for SpaceMono blocks).
    tmp = out_png.parent / (out_png.stem + "_bg.png")
    subprocess.run([sys.executable, str(ROOT / "tools/preview_substrate.py"),
                    str(mosaic_json), "-o", str(tmp),
                    "--cell", f"{PREVIEW_CELL_W}x{PREVIEW_CELL_W*2}"],
                   check=True, stdout=subprocess.DEVNULL)
    img = Image.open(tmp).convert("RGB")
    d = ImageDraw.Draw(img)

    def F(px):
        return ImageFont.truetype(str(FONT), max(6, round(px * scale)))

    for e in elements:
        lines = e.get("lines", [])
        if not lines:
            continue
        x0, y0, x1, y1 = e["box"]
        size = e.get("size", 16)
        f = F(size)
        fg = e.get("fg", "#e8e0d0")
        panel = e.get("panel")
        align = e.get("align", "left")
        step = round(size * scale * 1.42)
        bx0, by0 = x0 * scale, y0 * scale
        tw = max(d.textlength(l, font=f) for l in lines)
        # Panel masks the FULL painted-text box (scaled), so the painting
        # never bleeds around the new text regardless of small coord error.
        if panel:
            pad = BOX_MARGIN * scale
            d.rectangle([x0 * scale - pad, y0 * scale - pad,
                         x1 * scale + pad, y1 * scale + pad], fill=panel)
        for i, l in enumerate(lines):
            lw = d.textlength(l, font=f)
            lx = bx0 + ((tw - lw) / 2 if align == "center" else 0)
            d.text((lx, by0 + i * step), l, font=f, fill=fg)
    img.save(out_png)
    tmp.unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--no-commit-assets", action="store_true")
    args = ap.parse_args()
    spec = json.loads(Path(args.spec).read_text())
    card = spec["card"]
    src = ROOT / spec["source"]
    width = spec.get("width", 560)
    elements = spec["elements"]

    img = Image.open(src)
    clean = inpaint_text(img, elements)
    clean_path = ROOT / f"assets/gallery/{card}_clean.png"
    clean.save(clean_path)

    mosaic_json = ROOT / f"resources/substrates/gallery/{card}_blocks.json"
    subprocess.run([sys.executable, str(ROOT / "tools/img2ansiblocks.py"),
                    str(clean_path), "-w", str(width), "--mode", "adaptive",
                    "--colors", "24", "--autocontrast", "-o", str(mosaic_json)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    d = json.loads(mosaic_json.read_text())
    d["charset"] = "blocks"; d["source"] = f"{card}.png (clean mosaic {width})"
    mosaic_json.write_text(json.dumps(d))

    # preview scale: source-image px -> preview px
    iw = img.size[0]
    scale = (d["width"] * PREVIEW_CELL_W) / iw
    out_png = Path("/tmp/blockart") / f"{card}_final.png"
    out_png.parent.mkdir(parents=True, exist_ok=True)
    render_preview(mosaic_json, elements, scale, out_png)
    print(f"{card}: clean={clean_path.name} mosaic={d['width']}x{d['height']} preview={out_png}")


if __name__ == "__main__":
    main()
