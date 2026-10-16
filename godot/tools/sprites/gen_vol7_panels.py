#!/usr/bin/env python3
"""gen_vol7_panels.py — Vol 7's first five [panel:] info cards.

The audit measured 23 panel uses ever, ZERO in Vol 7 — the volume
richest in documents (patch notes, hand-lettered labels, schedules,
logs) never once holds one up to the reader. These five are the
fiction's own paperwork, in the established HeroImage primitive
language (fill / noise / shade / poly), sized like the vol5/6 panels
(~130×95 logical px, upscaled by the renderer).

Output: godot/resources/vn/panels/vol7_*.json · deterministic.
"""
import json, os

OUT = os.path.join(os.path.dirname(__file__), "..", "..",
                   "resources", "vn", "panels")


def rectp(x, y, w, h, color):
    return {"op": "poly", "color": color,
            "points": [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]}


def text_bars(x, y, widths, color, gap=6, h=3):
    """suggested handwriting/type: one thin bar per line."""
    out = []
    for i, w in enumerate(widths):
        out.append(rectp(x, y + i * gap, w, h, color))
    return out


def panel(pid, palette, layers):
    return {"id": pid, "w": 130, "h": 95, "palette": palette,
            "layers": [{"op": "fill", "color": 0},
                       {"op": "noise", "xywh": [0, 0, 130, 95],
                        "density": 0.05, "seed": 7, "color": 1}] + layers}


PANELS = []

# 1 · the tower patch work-order · taped, official, two years old
PANELS.append(panel("vol7_tower_patch_note",
    ["#20241e", "#2a2e28", "#ded8c4", "#c8c2ae", "#8a4a3a", "#485058",
     "#b0a88e", "#343830"],
    [rectp(14, 10, 102, 74, 3),                       # the sheet, skewed under
     rectp(12, 8, 102, 74, 2),                        # the sheet
     rectp(50, 2, 28, 12, 6),                         # tape
     rectp(18, 16, 60, 8, 5),                         # letterhead block
     ] + text_bars(18, 30, [88, 84, 90, 60], 7)
      + [rectp(18, 58, 40, 10, 4),                    # the red PATCH stamp
         ] + text_bars(64, 60, [44, 36], 7)
      + [rectp(18, 74, 30, 3, 5)]))                   # signature line

# 2 · the third cartridge's label · Cale's hand · ESTUARY 7 — INES ROCHA 2046
PANELS.append(panel("vol7_estuary7_label",
    ["#26221c", "#2e2a22", "#8a8e9c", "#6a6e7c", "#d8d2be", "#3a3630",
     "#2c3038", "#584838"],
    [rectp(10, 14, 110, 66, 3),                       # cartridge body shadow
     rectp(8, 12, 110, 66, 2),                        # cartridge body
     rectp(20, 22, 86, 44, 4),                        # the label
     rectp(20, 22, 86, 6, 7),                         # label top band
     ] + text_bars(26, 34, [72, 56], 5, 8, 4)         # ESTUARY 7 / INES ROCHA
      + text_bars(26, 52, [30], 6, 6, 3)              # 2046
      + [rectp(8, 12, 110, 4, 6),                     # top edge
         rectp(30, 70, 66, 4, 5)]))                   # connector slot

# 3 · the Smolvud bus schedule · the hill run struck out
PANELS.append(panel("vol7_bus_schedule",
    ["#1e2220", "#262a28", "#e2dcc8", "#ccc6b2", "#3a4048", "#8a4a3a",
     "#6a706a", "#b8b29e"],
    [rectp(16, 6, 98, 82, 3),
     rectp(14, 4, 98, 82, 2),
     rectp(20, 10, 60, 8, 4),                         # SMOLVUD TRANSIT head
     ] + text_bars(20, 24, [80, 80, 80, 80, 80], 6, 9, 3)   # five routes
      + [rectp(20, 51, 80, 3, 5),                     # the STRUCK route
         rectp(18, 46, 86, 1, 5),                     # strike-through
         rectp(20, 78, 44, 3, 7)]))                   # fine print

# 4 · the Saturday-night photograph · March 1994 · Lena's inheritance
PANELS.append(panel("vol7_daughter_photo",
    ["#221e1a", "#2a2622", "#e6e0cc", "#4a4238", "#6a5a44", "#948a72",
     "#38342c", "#c8bfa4"],
    [rectp(24, 8, 82, 78, 2),                         # the print's border
     rectp(30, 14, 70, 56, 3),                        # the photo, dark
     rectp(36, 44, 14, 26, 4),                        # two figures
     rectp(56, 40, 14, 30, 4),
     rectp(34, 20, 62, 10, 5),                        # a lit doorway behind
     rectp(30, 74, 40, 4, 7),                         # the pencil caption
     rectp(74, 74, 18, 4, 7)]))

# 5 · Finn's radio log · the quiet minute, logged in his hand
PANELS.append(panel("vol7_freq_log",
    ["#181e1e", "#20262a", "#d8d4c0", "#c2beaa", "#3a5048", "#8a4a3a",
     "#586460", "#a8a48e"],
    [rectp(12, 8, 106, 78, 3),
     rectp(10, 6, 106, 78, 2),
     rectp(16, 12, 52, 7, 6),                         # FREQ LOG header
     ] + text_bars(16, 26, [88, 84, 88, 80], 7, 8, 3)  # entries
      + [rectp(16, 60, 88, 3, 4),                     # the waveform row
         rectp(16, 58, 46, 7, 4),
         rectp(66, 60, 38, 1, 5),                     # ...that goes flat (red)
         ] + text_bars(16, 74, [60], 5, 6, 3)))       # the annotation


def main():
    os.makedirs(OUT, exist_ok=True)
    for p in PANELS:
        path = os.path.join(OUT, p["id"] + ".json")
        json.dump(p, open(path, "w"), indent=1)
        print("wrote", os.path.relpath(path))


if __name__ == "__main__":
    main()
