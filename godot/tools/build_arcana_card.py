#!/usr/bin/env python3
"""
Build one Major-Arcana card surface end to end:

  1. Inpaint the painted text out of the source PNG       -> assets/gallery/<card>_clean.png
  2. Convert the clean art to an aspect-correct mosaic     -> gallery/<card>_clean_blocks.json
  3. Emit a real-text overlay piece per spec element       -> pieces/<card>_txt_<n>.json
  4. Emit the AsciiComposition manifest                    -> compositions/<card>_card.json
  5. Register it in gallery/_index.json
  6. Emit a faithful composition preview                   -> /tmp/blockart/<card>_card.png

The preview renders the manifest the way Godot's AsciiWindow/AsciiComposition
will (SpaceMono, advance 0.612em, line-height 1.49em), so it is a true proxy.

Card specs live in tools/arcana_specs/<card>.json (coords in SOURCE-IMAGE px):
  { "card","source","width", "elements":[
      { "box":[x0,y0,x1,y1], "lines":["…"], "size":40,
        "fg":"#rrggbb", "panel":"#rrggbb"|null, "align":"left|center",
        "inpaint":true } ] }
"""
import argparse, json, sys, subprocess, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np, cv2

ROOT = Path(__file__).resolve().parent.parent      # godot/
SUB  = ROOT / "resources/substrates"
FONT = ROOT / "resources/fonts/SpaceMono-Regular.ttf"

ADV = 0.612      # SpaceMono advance / em
LH  = 1.49       # SpaceMono line height (ascent+descent) / em
CELL_ASPECT = 0.82   # sub-pixel w/h -> undistorted mosaic in-engine
BOX_MARGIN = 16      # px expansion to suppress paint bleed
MOSAIC_FONT = 6      # font_px for the background mosaic window
CANVAS_BG = "#040610"


def inpaint_text(src_img, elements):
    arr = np.array(src_img.convert("RGB"))
    H, W = arr.shape[:2]
    mask = np.zeros((H, W), np.uint8)
    m = BOX_MARGIN
    any_box = False
    for e in elements:
        if not e.get("inpaint", True):
            continue
        x0, y0, x1, y1 = e["box"]
        mask[max(0, y0 - m):min(H, y1 + m), max(0, x0 - m):min(W, x1 + m)] = 255
        any_box = True
    if not any_box:
        return src_img.convert("RGB")
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)
    return Image.fromarray(cv2.inpaint(arr, mask, 4, cv2.INPAINT_TELEA))


def make_mosaic(clean_png, out_json, width):
    subprocess.run([sys.executable, str(ROOT / "tools/img2ansiblocks.py"),
                    str(clean_png), "-w", str(width), "--mode", "adaptive",
                    "--colors", "24", "--autocontrast",
                    "--cell-aspect", str(CELL_ASPECT), "-o", str(out_json)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    d = json.loads(out_json.read_text())
    d["charset"] = "blocks"
    out_json.write_text(json.dumps(d))
    return d["width"], d["height"]


def _grid(cols, rows, fill):
    return {"width": cols, "height": rows, "charset": "blocks",
            "color": "fgbg", "source": "arcana overlay",
            "cells": [[dict(fill) for _ in range(cols)] for _ in range(rows)]}


def element_windows(element, sx, sy):
    """Return a list of (piece_dict, window_dict) for one text element:
    a fine mask piece (exactly covers the painted-text box) + the crisp
    text piece (centred on the box centre at the element font size)."""
    x0, y0, x1, y1 = element["box"]
    lines = element["lines"]
    size = element.get("size", 16)
    fg = element.get("fg", "#e8e0d0")
    panel = element.get("panel")
    align = element.get("align", "left")
    m = BOX_MARGIN
    out = []

    # 1. Mask: opaque panel at the mosaic font for fine box coverage.
    if panel is not None:
        w_px = (x1 - x0 + 2 * m) * sx
        h_px = (y1 - y0 + 2 * m) * sy
        mc = max(1, round(w_px / (ADV * MOSAIC_FONT)))
        mr = max(1, round(h_px / (LH * MOSAIC_FONT)))
        mask = _grid(mc, mr, {"c": " ", "fg": None, "bg": panel})
        out.append((mask, {"x": round((x0 - m) * sx), "y": round((y0 - m) * sy),
                           "font_px": MOSAIC_FONT, "z": 4}))

    # 2. Text: crisp, centred on the box centre.
    ft = max(6, round(size * sy))
    maxlen = max(len(l) for l in lines)
    grid = _grid(maxlen, len(lines), {"c": " "})
    for i, line in enumerate(lines):
        c0 = (maxlen - len(line)) // 2 if align == "center" else 0
        for j, ch in enumerate(line):
            grid["cells"][i][c0 + j] = {"c": ch, "fg": fg}
    block_w = maxlen * ADV * ft
    block_h = len(lines) * LH * ft
    ccx = ((x0 + x1) / 2) * sx
    ccy = ((y0 + y1) / 2) * sy
    tx = ccx - block_w / 2 if align == "center" else x0 * sx + 2
    ty = ccy - block_h / 2
    out.append((grid, {"x": round(tx), "y": round(ty), "font_px": ft, "z": 5}))
    return out


def build(spec):
    card = spec["card"]
    src_path = ROOT / spec["source"]
    width = spec.get("width", 560)
    elements = spec.get("elements", [])
    img = Image.open(src_path)
    sw, sh = img.size

    # 1-2. clean art + aspect-correct mosaic
    clean = inpaint_text(img, elements)
    clean_png = ROOT / f"assets/gallery/{card}_clean.png"
    clean.save(clean_png)
    mosaic_json = SUB / f"gallery/{card}_clean_blocks.json"
    mcols, mrows = make_mosaic(clean_png, mosaic_json, width)

    canvas_w = round(mcols * ADV * MOSAIC_FONT)
    canvas_h = round(mrows * LH * MOSAIC_FONT)
    sx, sy = canvas_w / sw, canvas_h / sh

    windows = [{"path": f"gallery/{card}_clean_blocks", "x": 0, "y": 0,
                "font_px": MOSAIC_FONT, "z": 1}]

    # 3. mask + text pieces + windows
    (SUB / "pieces").mkdir(exist_ok=True)
    for n, e in enumerate(elements):
        if not e.get("lines"):
            continue
        for k, (piece, win) in enumerate(element_windows(e, sx, sy)):
            pid = f"{card}_ov_{n}_{k}"
            (SUB / f"pieces/{pid}.json").write_text(json.dumps(piece))
            win["path"] = f"pieces/{pid}"
            windows.append(win)

    # 4. composition manifest
    comp = {"id": f"{card}_card", "canvas": [canvas_w, canvas_h],
            "bg": CANVAS_BG, "windows": windows}
    comp_path = SUB / f"compositions/{card}_card.json"
    comp_path.write_text(json.dumps(comp, indent=2))

    # 5. register in gallery index
    register(card)

    # 6. preview
    preview = Path("/tmp/blockart") / f"{card}_card.png"
    preview.parent.mkdir(parents=True, exist_ok=True)
    render_composition(comp, preview)
    print(f"{card}: canvas={canvas_w}x{canvas_h} mosaic={mcols}x{mrows} "
          f"windows={len(windows)} -> {comp_path.relative_to(ROOT)}")


ROMAN = {"fool": "0", "magician": "I", "high_priestess": "II",
         "empress": "III", "emperor": "IV", "hierophant": "V"}
NAME = {"fool": "THE FOOL", "magician": "THE MAGICIAN",
        "high_priestess": "THE HIGH PRIESTESS", "empress": "THE EMPRESS",
        "emperor": "THE EMPEROR", "hierophant": "THE HIEROPHANT"}


def register(card):
    idx_path = SUB / "gallery/_index.json"
    idx = json.loads(idx_path.read_text())
    cid = f"{card}_card"
    title = f"{ROMAN[card]} — {NAME[card]}  (composition)"
    entry = {"id": cid, "title": title, "set": "Major Arcana (Block Art)",
             "type": "composition", "path": f"{card}_card", "always_unlocked": True}
    items = [i for i in idx["items"] if i.get("id") != cid]
    items.insert(0, entry)
    idx["items"] = items
    idx_path.write_text(json.dumps(idx, indent=2))


def render_composition(comp, out_png):
    cw, ch = comp["canvas"]
    img = Image.new("RGB", (cw, ch), _hx(comp.get("bg", "#000000")))
    d = ImageDraw.Draw(img)
    for w in sorted(comp["windows"], key=lambda w: w.get("z", 0)):
        data = json.loads((SUB / (w["path"] + ".json")).read_text())
        f = w["font_px"]
        cwid, chgt = ADV * f, LH * f
        x0, y0 = w["x"], w["y"]
        font = ImageFont.truetype(str(FONT), max(6, round(f)))
        for ry, row in enumerate(data["cells"]):
            for rx, cell in enumerate(row):
                c = cell.get("c", " ")
                fg = cell.get("fg"); bg = cell.get("bg")
                cx = x0 + rx * cwid; cy = y0 + ry * chgt
                if bg:
                    d.rectangle([cx, cy, cx + cwid, cy + chgt], fill=_hx(bg))
                if c == " " or c == "":
                    continue
                if c == "▀" and fg:
                    d.rectangle([cx, cy, cx + cwid, cy + chgt / 2], fill=_hx(fg))
                elif c == "█" and fg:
                    d.rectangle([cx, cy, cx + cwid, cy + chgt], fill=_hx(fg))
                elif fg:
                    d.text((cx, cy), c, font=font, fill=_hx(fg))
    img.save(out_png)


def _hx(s):
    s = s.lstrip("#"); return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    build(json.loads(Path(ap.parse_args().spec).read_text()))


if __name__ == "__main__":
    main()
