#!/usr/bin/env python3
"""THE SISTERS WYRD · witch seat HeroImages · four seats, one loom.

Emits deterministic HeroImage JSONs (160x72, paperback inks) to
godot/resources/games/vol7/sisters_wyrd/hero_images/seat_<id>.json —
shown above the seat's PARLEY / DRAW / UNWEAVE screen.

Imagery per witches.json:
  north · a winter that never spread, snow falling upward, the net
  east  · a red dawn nailed in place, three shadows
  south · a drought with a house in it, real water on the porch
  west  · a sunset with a gallows in it, empty, patient

Run from the repo root:  python3 godot/tools/sprites/gen_wyrd_witch_heroes.py
Deterministic — run twice, diff clean.
"""
import json, os

W, H = 160, 72
OUT_DIR = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..",
    "resources", "games", "vol7", "sisters_wyrd", "hero_images"))

# Paperback inks — shared palette, one violet in reserve.
PAL = [
    "#201410",  # 0 ink
    "#c8a878",  # 1 dust
    "#e8dcc0",  # 2 bone
    "#7a3020",  # 3 blood
    "#b8bcc8",  # 4 silver
    "#8a58a8",  # 5 the wyrd (reserved)
    "#4a5a3a",  # 6 scrub
    "#a08858",  # 7 dust dark
    "#a84838",  # 8 blood light
    "#f0ece0",  # 9 snow / glare
    "#8a5838",  # 10 red dust
    "#38281c",  # 11 deep shadow
]

I_INK, I_DUST, I_BONE, I_BLOOD, I_SILVER, I_WYRD, I_SCRUB = 0, 1, 2, 3, 4, 5, 6
I_DUSTDK, I_BLOODLT, I_SNOW, I_REDDUST, I_SHADOW = 7, 8, 9, 10, 11


def doc(did, layers):
    return {"id": did, "w": W, "h": H, "palette": PAL, "layers": layers}


def north():
    L = []
    # hot sky over a hot territory
    L.append({"op": "vgrad", "y_range": [0, 44], "stops": [I_DUSTDK, I_DUST, I_BONE]})
    # ground
    L.append({"op": "hband", "y_range": [44, 72], "color": I_DUST})
    L.append({"op": "hline", "y": 44, "x_range": [0, W], "color": I_DUSTDK})
    L.append({"op": "noise", "xywh": [0, 46, W, 26], "color": I_DUSTDK,
              "density": 0.06, "seed": 11})
    # the cold column — one hex of winter, violet-edged
    L.append({"op": "shade", "xywh": [56, 4, 48, 62], "color": I_WYRD, "amount": 0.14})
    L.append({"op": "shade", "xywh": [62, 8, 36, 58], "color": I_SHADOW, "amount": 0.18})
    L.append({"op": "noise", "xywh": [58, 6, 44, 60], "color": I_SNOW,
              "density": 0.10, "seed": 21})
    # snow falling UP — short rising dashes
    for k, (sx, sy) in enumerate([(63, 50), (72, 34), (81, 56), (90, 26),
                                  (97, 44), (68, 16), (86, 12), (94, 60)]):
        L.append({"op": "vline", "x": sx, "y_range": [sy - 2, sy], "color": I_SNOW})
    # column edges, faint
    L.append({"op": "noise", "xywh": [55, 6, 2, 60], "color": I_WYRD,
              "density": 0.35, "seed": 31})
    L.append({"op": "noise", "xywh": [103, 6, 2, 60], "color": I_WYRD,
              "density": 0.35, "seed": 32})
    # her — seated in the middle of it, mending
    L.append({"op": "dot", "xy": [80, 40], "size": 4, "color": I_INK})        # head
    L.append({"op": "poly", "points": [[74, 44], [86, 44], [88, 56], [72, 56]],
              "color": I_INK})                                                 # shawl
    L.append({"op": "rect", "xywh": [72, 56, 16, 3], "color": I_INK})          # lap
    # the net no water ever saw
    L.append({"op": "polyline", "points": [[70, 58], [92, 60], [100, 66]], "color": I_SILVER})
    L.append({"op": "polyline", "points": [[72, 62], [88, 58], [98, 62]], "color": I_SILVER})
    L.append({"op": "polyline", "points": [[78, 58], [80, 66]], "color": I_SILVER})
    L.append({"op": "polyline", "points": [[88, 60], [92, 66]], "color": I_SILVER})
    return doc("seat_north", L)


def east():
    L = []
    # a red dawn nailed in place
    L.append({"op": "vgrad", "y_range": [0, 46], "stops": [I_BLOOD, I_BLOODLT, I_BLOOD]})
    # the sun, arrested at the horizon
    L.append({"op": "disk", "xy": [80, 46], "r": 12, "color": I_BONE})
    L.append({"op": "ring", "xy": [80, 46], "r": 12, "color": I_BLOODLT})
    # ground — red dust
    L.append({"op": "hband", "y_range": [46, 72], "color": I_REDDUST})
    L.append({"op": "hline", "y": 46, "x_range": [0, W], "color": I_INK})
    L.append({"op": "noise", "xywh": [0, 48, W, 24], "color": I_SHADOW,
              "density": 0.05, "seed": 41})
    # her — standing in the light
    L.append({"op": "dot", "xy": [80, 26], "size": 4, "color": I_INK})
    L.append({"op": "poly", "points": [[76, 30], [84, 30], [85, 46], [75, 46]],
              "color": I_INK})
    # casting THREE shadows — thin, wrong, disagreeing
    L.append({"op": "poly", "points": [[78, 46], [82, 46], [52, 57], [48, 55]],
              "color": I_SHADOW})
    L.append({"op": "poly", "points": [[78, 46], [82, 46], [81, 64], [77, 64]],
              "color": I_INK})
    L.append({"op": "poly", "points": [[78, 46], [82, 46], [112, 55], [108, 57]],
              "color": I_SHADOW})
    # the mirror, face-down beside her (the peddler's kindness)
    L.append({"op": "rect", "xywh": [96, 44, 8, 2], "color": I_SILVER})
    L.append({"op": "hline", "y": 46, "x_range": [96, 104], "color": I_INK})
    return doc("seat_east", L)


def south():
    L = []
    # white-hot drought sky
    L.append({"op": "vgrad", "y_range": [0, 42], "stops": [I_BONE, I_DUST]})
    L.append({"op": "noise", "xywh": [0, 34, W, 8], "color": I_BONE,
              "density": 0.10, "seed": 51})   # heat shimmer at the horizon
    # cracked earth
    L.append({"op": "hband", "y_range": [42, 72], "color": I_DUSTDK})
    L.append({"op": "hline", "y": 42, "x_range": [0, W], "color": I_INK})
    for pts in [[[10, 48], [24, 52], [30, 62], [26, 71]],
                [[52, 46], [60, 54], [56, 64]],
                [[40, 58], [50, 60], [58, 70]],
                [[8, 62], [18, 64], [22, 71]],
                [[70, 50], [76, 58], [72, 66]]]:
        L.append({"op": "polyline", "points": pts, "color": I_INK})
    # the driest house the territory owns
    L.append({"op": "rect", "xywh": [104, 26, 40, 16], "color": I_BONE})       # wall
    L.append({"op": "rect", "xywh": [104, 26, 40, 3], "color": I_DUSTDK})      # weathering
    L.append({"op": "poly", "points": [[100, 26], [148, 26], [140, 18], [108, 18]],
              "color": I_INK})                                                  # roof
    L.append({"op": "rect", "xywh": [110, 32, 5, 6], "color": I_SHADOW})       # window
    L.append({"op": "rect", "xywh": [132, 30, 6, 12], "color": I_SHADOW})      # door
    # porch
    L.append({"op": "rect", "xywh": [100, 42, 48, 2], "color": I_SHADOW})
    L.append({"op": "vline", "x": 102, "y_range": [30, 42], "color": I_INK})
    L.append({"op": "vline", "x": 146, "y_range": [30, 42], "color": I_INK})
    L.append({"op": "hline", "y": 30, "x_range": [100, 148], "color": I_INK})
    # her, rocking
    L.append({"op": "dot", "xy": [122, 34], "size": 3, "color": I_INK})
    L.append({"op": "poly", "points": [[118, 37], [126, 37], [127, 42], [117, 42]],
              "color": I_INK})
    L.append({"op": "polyline", "points": [[115, 43], [129, 43]], "color": I_INK})  # rocker
    # the water · real · the frightening part
    L.append({"op": "dot", "xy": [96, 44], "size": 3, "color": I_SILVER})
    L.append({"op": "dot", "xy": [96, 43], "size": 1, "color": I_SNOW})
    # one dead tree, west of the house
    L.append({"op": "vline", "x": 28, "y_range": [26, 42], "color": I_INK})
    L.append({"op": "polyline", "points": [[28, 30], [22, 26]], "color": I_INK})
    L.append({"op": "polyline", "points": [[28, 33], [34, 28]], "color": I_INK})
    return doc("seat_south", L)


def west():
    L = []
    # a sunset with a gallows in it
    L.append({"op": "vgrad", "y_range": [0, 48], "stops": [I_BLOOD, I_BLOODLT, I_DUST]})
    # low glare where the sun went
    L.append({"op": "shade", "xywh": [24, 40, 60, 8], "color": I_BONE, "amount": 0.25})
    # ground
    L.append({"op": "hband", "y_range": [48, 72], "color": I_SHADOW})
    L.append({"op": "hline", "y": 48, "x_range": [0, W], "color": I_INK})
    L.append({"op": "noise", "xywh": [0, 52, W, 20], "color": I_INK,
              "density": 0.05, "seed": 61})
    # the gallows · empty · patient
    L.append({"op": "rect", "xywh": [102, 16, 3, 33], "color": I_INK})          # post
    L.append({"op": "rect", "xywh": [102, 16, 26, 2], "color": I_INK})          # arm
    L.append({"op": "polyline", "points": [[105, 24], [112, 17]], "color": I_INK})  # brace
    L.append({"op": "vline", "x": 124, "y_range": [18, 30], "color": I_DUSTDK})     # rope
    L.append({"op": "ring", "xy": [124, 33], "r": 3, "color": I_DUSTDK})            # noose
    # thirteen steps, worn
    L.append({"op": "polyline", "points": [[96, 48], [102, 44], [108, 48]], "color": I_SHADOW})
    # her — younger than the others, or wears it better, or is lying
    L.append({"op": "dot", "xy": [56, 28], "size": 3, "color": I_INK})
    L.append({"op": "poly", "points": [[53, 31], [59, 31], [60, 48], [52, 48]],
              "color": I_INK})
    L.append({"op": "vline", "x": 60, "y_range": [28, 40], "color": I_INK})     # long hair
    L.append({"op": "vline", "x": 61, "y_range": [30, 36], "color": I_INK})
    # the eighth point, high and violet and uncommented
    L.append({"op": "polyline", "points": [[24, 6], [24, 14]], "color": I_WYRD})
    L.append({"op": "polyline", "points": [[20, 10], [28, 10]], "color": I_WYRD})
    L.append({"op": "dot", "xy": [22, 8], "size": 1, "color": I_WYRD})
    L.append({"op": "dot", "xy": [26, 8], "size": 1, "color": I_WYRD})
    L.append({"op": "dot", "xy": [22, 12], "size": 1, "color": I_WYRD})
    L.append({"op": "dot", "xy": [26, 12], "size": 1, "color": I_WYRD})
    return doc("seat_west", L)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for d in [north(), east(), south(), west()]:
        path = os.path.join(OUT_DIR, d["id"] + ".json")
        with open(path, "w") as f:
            json.dump(d, f, indent=1)
            f.write("\n")
        print("wrote", path)


if __name__ == "__main__":
    main()
