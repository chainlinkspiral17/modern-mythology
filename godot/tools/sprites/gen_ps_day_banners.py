#!/usr/bin/env python3
"""Pirate Summer graphics pass 6 · day-intro banners + NG+ moment card.

Emits HeroImage JSONs to resources/games/vol7/pirate_summer/sprites/scenes/:
  day_banner_0..6.json   200x52 · one banner per day of the week,
                         shown at the top of the day-intro modal.
  moment_ng_remembered_summer.json  160x100 · the NG+ deja-vu card
                         (the camp gate, and its ghost, misaligned).

Deterministic: same output every run. Ops restricted to the set the
scratchpad previewer mirrors (no hgrad).
"""
import json, os

OUT = os.path.join(os.path.dirname(__file__), "..", "..",
                   "resources", "games", "vol7", "pirate_summer",
                   "sprites", "scenes")

def write(name, doc):
    path = os.path.abspath(os.path.join(OUT, name + ".json"))
    with open(path, "w") as f:
        json.dump(doc, f, indent=1)
    print("wrote", path)

W, H = 200, 52

# Shared coastal palette pieces
SKY_MORN   = ["#9fc4d8", "#b8d4e2"]
SKY_DUSK   = ["#3a4468", "#7a5a72", "#c88a5a"]
SPRUCE_D   = "#1e3428"
SPRUCE_M   = "#2a4a36"
GRAVEL     = "#8a8276"
WATER      = "#4a7a8c"
WATER_LT   = "#6a9aac"

def spruce_line(pal, y_base, color_idx, step=14, h1=16, h2=22, seed=3):
    """A jagged spruce treeline as one poly per tree."""
    ops = []
    x = -4
    k = seed
    while x < W + 8:
        th = h1 + ((x * 7 + k * 13) % (h2 - h1))
        half = 5 + ((x + k) % 4)
        ops.append({"op": "poly", "points": [[x, y_base], [x + half, y_base - th], [x + half * 2, y_base]], "color": color_idx})
        x += step
    return ops

def banner_sunday():
    # gravel road curving in from the left · the yellow bus arriving ·
    # spruce line behind · morning sky
    pal = [SKY_MORN[0], SKY_MORN[1], SPRUCE_D, SPRUCE_M, GRAVEL, "#d8b83a", "#5a4a1e", "#2a2a2a", "#e8e4da", "#6a6256"]
    L = [
        {"op": "vgrad", "stops": [1, 0], "y_range": [0, 30]},
        {"op": "hband", "y_range": [30, 52], "color": 9},
    ]
    L += spruce_line(pal, 30, 2, step=13, h1=12, h2=20, seed=5)
    L += spruce_line(pal, 31, 3, step=17, h1=8, h2=14, seed=11)
    # road wedge
    L += [
        {"op": "poly", "points": [[0, 52], [70, 34], [110, 34], [40, 52]], "color": 4},
        {"op": "poly", "points": [[40, 52], [110, 34], [118, 34], [78, 52]], "color": 9},
        # bus body
        {"op": "rect", "xywh": [118, 24, 44, 14], "color": 5},
        {"op": "rect", "xywh": [118, 24, 44, 4],  "color": 8},
        {"op": "rect", "xywh": [122, 27, 7, 5], "color": 7},
        {"op": "rect", "xywh": [132, 27, 7, 5], "color": 7},
        {"op": "rect", "xywh": [142, 27, 7, 5], "color": 7},
        {"op": "rect", "xywh": [152, 27, 7, 5], "color": 7},
        {"op": "disk", "xy": [127, 39], "r": 3, "color": 7},
        {"op": "disk", "xy": [152, 39], "r": 3, "color": 7},
        # flag pole at right
        {"op": "vline", "x": 184, "y_range": [10, 34], "color": 6},
        {"op": "rect", "xywh": [185, 10, 8, 5], "color": 8},
        {"op": "noise", "xywh": [0, 34, 200, 18], "density": 0.05, "color": 9, "seed": 9},
    ]
    return {"id": "day_banner_0", "w": W, "h": H, "palette": pal, "layers": L}

def banner_monday():
    # the lake · swim floats · archery target right
    pal = ["#a8d0dc", "#c4e0e8", WATER, WATER_LT, SPRUCE_D, "#e8e4da", "#c83a2a", "#e8d43a", "#6a5a3e", "#f4f0e8"]
    L = [
        {"op": "vgrad", "stops": [1, 0], "y_range": [0, 22]},
        {"op": "hband", "y_range": [22, 44], "color": 2},
        {"op": "hband", "y_range": [44, 52], "color": 8},
    ]
    L += spruce_line(pal, 22, 4, step=15, h1=8, h2=13, seed=7)
    for i, wx in enumerate(range(8, 190, 16)):
        L.append({"op": "hline", "y": 26 + (i % 4) * 4, "x_range": [wx, wx + 8], "color": 3})
    L += [
        # swim floats
        {"op": "dot", "xy": [52, 30], "color": 5}, {"op": "dot", "xy": [60, 31], "color": 6},
        {"op": "dot", "xy": [68, 30], "color": 5}, {"op": "dot", "xy": [76, 31], "color": 6},
        # archery target on the sand
        {"op": "disk", "xy": [168, 38], "r": 10, "color": 9},
        {"op": "ring", "xy": [168, 38], "r": 8, "color": 6},
        {"op": "ring", "xy": [168, 38], "r": 5, "color": 7},
        {"op": "disk", "xy": [168, 38], "r": 2, "color": 6},
        {"op": "vline", "x": 160, "y_range": [44, 51], "color": 8},
        {"op": "vline", "x": 176, "y_range": [44, 51], "color": 8},
    ]
    return {"id": "day_banner_1", "w": W, "h": H, "palette": pal, "layers": L}

def banner_tuesday():
    # canoes at dusk · one lit window far right · homesick night
    pal = [SKY_DUSK[0], SKY_DUSK[1], SKY_DUSK[2], "#26364a", "#16242e", "#6a4a2e", "#8a5a36", "#e8c85a", "#1a2a20"]
    L = [
        {"op": "vgrad", "stops": [0, 1, 2], "y_range": [0, 26]},
        {"op": "hband", "y_range": [26, 52], "color": 3},
        {"op": "hband", "y_range": [26, 28], "color": 2},
    ]
    L += spruce_line(pal, 26, 8, step=16, h1=9, h2=15, seed=13)
    L += [
        # two canoes
        {"op": "poly", "points": [[40, 38], [48, 42], [76, 42], [84, 38], [76, 40], [48, 40]], "color": 5},
        {"op": "poly", "points": [[100, 44], [108, 48], [136, 48], [144, 44], [136, 46], [108, 46]], "color": 6},
        # reflections
        {"op": "hline", "y": 44, "x_range": [48, 76], "color": 4},
        {"op": "hline", "y": 50, "x_range": [108, 136], "color": 4},
        # the cabin with one lit window
        {"op": "rect", "xywh": [168, 16, 24, 12], "color": 8},
        {"op": "poly", "points": [[166, 16], [180, 8], [194, 16]], "color": 4},
        {"op": "rect", "xywh": [174, 20, 5, 5], "color": 7},
        {"op": "noise", "xywh": [0, 0, 200, 10], "density": 0.015, "color": 7, "seed": 21},
    ]
    return {"id": "day_banner_2", "w": W, "h": H, "palette": pal, "layers": L}

def banner_wednesday():
    # the hike up + the ghost pirate play stage
    pal = ["#b8d0c8", "#d0e0d8", SPRUCE_D, SPRUCE_M, "#7a6a4e", "#4a3a2a", "#e8e4da", "#2a2a2a", "#c8b89a"]
    L = [
        {"op": "vgrad", "stops": [1, 0], "y_range": [0, 30]},
        # hillside
        {"op": "poly", "points": [[0, 52], [0, 34], [60, 22], [130, 30], [200, 24], [200, 52]], "color": 3},
        {"op": "poly", "points": [[0, 52], [0, 40], [70, 30], [140, 38], [200, 32], [200, 52]], "color": 2},
        # switchback trail
        {"op": "polyline", "points": [[10, 50], [60, 42], [30, 38], [90, 30], [70, 27], [120, 24]], "color": 8},
    ]
    L += [
        # stage at right: planks + two masts + skull pennant
        {"op": "rect", "xywh": [148, 34, 44, 10], "color": 4},
        {"op": "vline", "x": 152, "y_range": [16, 34], "color": 5},
        {"op": "vline", "x": 188, "y_range": [16, 34], "color": 5},
        {"op": "hline", "y": 16, "x_range": [152, 188], "color": 5},
        {"op": "rect", "xywh": [153, 17, 6, 12], "color": 7},
        {"op": "rect", "xywh": [181, 17, 6, 12], "color": 7},
        {"op": "hline", "y": 17, "x_range": [153, 187], "color": 7},
        {"op": "poly", "points": [[166, 18], [174, 18], [170, 25]], "color": 6},
        {"op": "dot", "xy": [169, 20], "color": 7}, {"op": "dot", "xy": [172, 20], "color": 7},
    ]
    return {"id": "day_banner_3", "w": W, "h": H, "palette": pal, "layers": L}

def banner_thursday():
    # the map unrolled + talent show string lights
    pal = ["#3a4468", "#54507a", "#26364a", "#e8d8b0", "#c8b083", "#8a5a36", "#e8c85a", "#c83a2a", "#1a2a20", "#6a4a2e"]
    L = [
        {"op": "vgrad", "stops": [0, 1], "y_range": [0, 52]},
    ]
    L += spruce_line(pal, 52, 8, step=18, h1=18, h2=26, seed=17)
    # string lights, two swags
    for x0, x1, ymid in [(0, 100, 14), (100, 200, 12)]:
        pts = []
        for i in range(0, 11):
            t = i / 10.0
            x = x0 + (x1 - x0) * t
            y = int(6 + (ymid - 6) * (4 * t * (1 - t)))
            pts.append([int(x), y])
        L.append({"op": "polyline", "points": pts, "color": 9})
        for i in range(1, 10, 2):
            L.append({"op": "dot", "xy": [pts[i][0], pts[i][1] + 1], "color": 6})
    L += [
        # the map, unrolled at an angle, X marked
        {"op": "poly", "points": [[52, 46], [64, 24], [136, 20], [148, 42]], "color": 3},
        {"op": "poly", "points": [[56, 44], [66, 26], [134, 22], [144, 40]], "color": 4},
        {"op": "polyline", "points": [[70, 36], [90, 32], [108, 34], [124, 28]], "color": 5},
        {"op": "polyline", "points": [[118, 30], [124, 36]], "color": 7},
        {"op": "polyline", "points": [[124, 30], [118, 36]], "color": 7},
    ]
    return {"id": "day_banner_4", "w": W, "h": H, "palette": pal, "layers": L}

def banner_friday():
    # the closing bonfire · sparks · ring of silhouettes
    pal = ["#1a2030", "#2a2438", "#16242e", "#e8c85a", "#e88a3a", "#c84a2a", "#6a4a2e", "#0e1616", "#f4e8c8"]
    L = [
        {"op": "vgrad", "stops": [1, 0], "y_range": [0, 52]},
    ]
    L += spruce_line(pal, 52, 2, step=17, h1=16, h2=24, seed=23)
    L += [
        # fire
        {"op": "poly", "points": [[88, 46], [96, 22], [100, 34], [106, 18], [110, 34], [116, 26], [120, 46]], "color": 5},
        {"op": "poly", "points": [[94, 46], [101, 30], [105, 38], [110, 28], [115, 46]], "color": 4},
        {"op": "poly", "points": [[100, 46], [104, 36], [108, 40], [112, 46]], "color": 3},
        # logs
        {"op": "hline", "y": 46, "x_range": [84, 124], "color": 6},
        {"op": "hline", "y": 47, "x_range": [88, 120], "color": 6},
        # sparks
        {"op": "dot", "xy": [98, 14], "color": 3}, {"op": "dot", "xy": [112, 10], "color": 3},
        {"op": "dot", "xy": [105, 7], "color": 8}, {"op": "dot", "xy": [118, 16], "color": 4},
        # silhouettes around the ring
        {"op": "rect", "xywh": [64, 40, 5, 8], "color": 7}, {"op": "disk", "xy": [66, 38], "r": 3, "color": 7},
        {"op": "rect", "xywh": [138, 40, 5, 8], "color": 7}, {"op": "disk", "xy": [140, 38], "r": 3, "color": 7},
        {"op": "rect", "xywh": [52, 43, 5, 7], "color": 7}, {"op": "disk", "xy": [54, 41], "r": 3, "color": 7},
        {"op": "rect", "xywh": [150, 43, 5, 7], "color": 7}, {"op": "disk", "xy": [152, 41], "r": 3, "color": 7},
    ]
    return {"id": "day_banner_5", "w": W, "h": H, "palette": pal, "layers": L}

def banner_saturday():
    # the bus leaving right · long shadows · the empty flagpole
    pal = ["#d8c8a0", "#e8dcc0", SPRUCE_D, SPRUCE_M, GRAVEL, "#d8b83a", "#5a4a1e", "#2a2a2a", "#e8e4da", "#9a8e72"]
    L = [
        {"op": "vgrad", "stops": [1, 0], "y_range": [0, 30]},
        {"op": "hband", "y_range": [30, 52], "color": 9},
    ]
    L += spruce_line(pal, 30, 2, step=14, h1=11, h2=18, seed=29)
    L += [
        # road out to the right
        {"op": "poly", "points": [[200, 52], [120, 34], [88, 34], [160, 52]], "color": 4},
        # bus, smaller, heading away
        {"op": "rect", "xywh": [128, 27, 30, 10], "color": 5},
        {"op": "rect", "xywh": [128, 27, 30, 3], "color": 8},
        {"op": "rect", "xywh": [132, 29, 5, 4], "color": 7},
        {"op": "rect", "xywh": [140, 29, 5, 4], "color": 7},
        {"op": "rect", "xywh": [148, 29, 5, 4], "color": 7},
        {"op": "disk", "xy": [134, 38], "r": 2, "color": 7},
        {"op": "disk", "xy": [152, 38], "r": 2, "color": 7},
        # long morning shadows
        {"op": "poly", "points": [[126, 39], [112, 44], [162, 44], [158, 39]], "color": 6},
        # empty flagpole, left
        {"op": "vline", "x": 24, "y_range": [8, 34], "color": 6},
        {"op": "hline", "y": 9, "x_range": [24, 28], "color": 6},
        {"op": "polyline", "points": [[24, 34], [6, 40]], "color": 6},
    ]
    return {"id": "day_banner_6", "w": W, "h": H, "palette": pal, "layers": L}

def moment_ng():
    # the camp gate arch, and its ghost double, misaligned · the
    # remembered summer standing slightly beside the real one
    pal = ["#2a2440", "#4a3c62", "#6a5480", "#1a3428", "#2a4a36", "#8a7a5e", "#c8b083", "#a89cd0", "#e8d8b0"]
    W2, H2 = 160, 100
    L = [
        {"op": "vgrad", "stops": [0, 1], "y_range": [0, 70]},
        {"op": "hband", "y_range": [70, 100], "color": 3},
        {"op": "hband", "y_range": [70, 72], "color": 4},
    ]
    L += spruce_line(pal, 70, 4, step=18, h1=20, h2=30, seed=31)
    # ghost gate first (behind, offset up-left, dimmer)
    L += [
        {"op": "vline", "x": 46, "y_range": [26, 66], "color": 7},
        {"op": "vline", "x": 104, "y_range": [26, 66], "color": 7},
        {"op": "hline", "y": 26, "x_range": [46, 104], "color": 7},
        {"op": "hline", "y": 27, "x_range": [46, 104], "color": 7},
        {"op": "text", "xy": [56, 30], "s": "SWEETGUM", "color": 7},
    ]
    # real gate (solid, offset down-right)
    L += [
        {"op": "vline", "x": 52, "y_range": [32, 72], "color": 5},
        {"op": "vline", "x": 53, "y_range": [32, 72], "color": 5},
        {"op": "vline", "x": 110, "y_range": [32, 72], "color": 5},
        {"op": "vline", "x": 111, "y_range": [32, 72], "color": 5},
        {"op": "hline", "y": 32, "x_range": [52, 112], "color": 6},
        {"op": "hline", "y": 33, "x_range": [52, 112], "color": 6},
        {"op": "hline", "y": 34, "x_range": [52, 112], "color": 5},
        {"op": "text", "xy": [62, 37], "s": "SWEETGUM", "color": 8},
        # the path through, doubled footprints
        {"op": "poly", "points": [[70, 100], [78, 72], [88, 72], [96, 100]], "color": 5},
        {"op": "dot", "xy": [80, 82], "color": 6}, {"op": "dot", "xy": [85, 88], "color": 6},
        {"op": "dot", "xy": [79, 94], "color": 6},
        {"op": "dot", "xy": [76, 80], "color": 7}, {"op": "dot", "xy": [81, 86], "color": 7},
        {"op": "dot", "xy": [75, 92], "color": 7},
        {"op": "noise", "xywh": [0, 0, 160, 24], "density": 0.05, "color": 2, "seed": 37},
    ]
    return {"id": "moment_ng_remembered_summer", "w": W2, "h": H2, "palette": pal, "layers": L}

if __name__ == "__main__":
    write("day_banner_0", banner_sunday())
    write("day_banner_1", banner_monday())
    write("day_banner_2", banner_tuesday())
    write("day_banner_3", banner_wednesday())
    write("day_banner_4", banner_thursday())
    write("day_banner_5", banner_friday())
    write("day_banner_6", banner_saturday())
    write("moment_ng_remembered_summer", moment_ng())
