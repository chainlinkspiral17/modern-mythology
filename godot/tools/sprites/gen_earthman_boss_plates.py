#!/usr/bin/env python3
"""Earthman Chronicles · combat boss plates · three arenas.

Emits deterministic HeroImage JSONs (160x40 wide strips, the
astro-cortex instrument palette) to
godot/resources/games/vol7/earthman_chronicles/hero_images/
boss_<boss_id>.json — shown above the combat log.

  hel_velli_duel · four arms, two blades drawn, two open · dune dusk
  thar_krai_tam  · seven feet two in the lantern-lit mines
  nalat          · the Order room whose floor is on his side

Run from the repo root:  python3 godot/tools/sprites/gen_earthman_boss_plates.py
Deterministic — run twice, diff clean.
"""
import json, os

W, H = 160, 40
OUT_DIR = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..",
    "resources", "games", "vol7", "earthman_chronicles", "hero_images"))

PAL = [
    "#0b080e",  # 0 void
    "#58305f",  # 1 cortex violet
    "#291a33",  # 2 panel violet
    "#c86020",  # 3 amber
    "#f8c848",  # 4 star gold
    "#c02020",  # 5 red
    "#e9d090",  # 6 cream
    "#f0f0f0",  # 7 white
    "#b8bcc8",  # 8 silver
    "#3a2348",  # 9 dusk violet
    "#16101c",  # 10 near-void
]

VOID, CORTEX, PANEL, AMBER, STAR, RED, CREAM, WHITE, SILVER, DUSK, NVOID = range(11)


def doc(did, layers):
    return {"id": did, "w": W, "h": H, "palette": PAL, "layers": layers}


def hel_velli():
    L = []
    # dune dusk, two moons
    L.append({"op": "vgrad", "y_range": [0, 30], "stops": [NVOID, DUSK, PANEL]})
    L.append({"op": "noise", "xywh": [0, 0, W, 12], "color": WHITE,
              "density": 0.012, "seed": 7})
    L.append({"op": "disk", "xy": [28, 8], "r": 4, "color": CREAM})
    L.append({"op": "disk", "xy": [27, 7], "r": 1, "color": WHITE})
    L.append({"op": "disk", "xy": [44, 12], "r": 2, "color": SILVER})
    # dunes
    L.append({"op": "poly", "points": [[0, 34], [40, 27], [90, 33], [160, 28],
                                       [160, 40], [0, 40]], "color": PANEL})
    L.append({"op": "poly", "points": [[0, 40], [60, 33], [120, 37], [160, 34],
                                       [160, 40]], "color": NVOID})
    # Hel Velli — four arms, two blades drawn, two open
    cx = 108
    L.append({"op": "dot", "xy": [cx, 12], "size": 4, "color": VOID})            # head
    L.append({"op": "poly", "points": [[cx - 4, 15], [cx + 4, 15],
                                       [cx + 5, 31], [cx - 5, 31]], "color": VOID})  # torso
    # upper arms raised, holding iron
    L.append({"op": "polyline", "points": [[cx - 3, 17], [cx - 10, 11]], "color": VOID})
    L.append({"op": "polyline", "points": [[cx - 10, 11], [cx - 15, 4]], "color": SILVER})
    L.append({"op": "polyline", "points": [[cx + 3, 17], [cx + 10, 12]], "color": VOID})
    L.append({"op": "polyline", "points": [[cx + 10, 12], [cx + 16, 6]], "color": SILVER})
    # lower arms open — he is trying to find out what you do
    L.append({"op": "polyline", "points": [[cx - 4, 22], [cx - 12, 26]], "color": VOID})
    L.append({"op": "polyline", "points": [[cx + 4, 22], [cx + 12, 26]], "color": VOID})
    # legs
    L.append({"op": "polyline", "points": [[cx - 3, 31], [cx - 4, 36]], "color": VOID})
    L.append({"op": "polyline", "points": [[cx + 3, 31], [cx + 4, 36]], "color": VOID})
    # eyes — patient
    L.append({"op": "dot", "xy": [cx - 1, 12], "size": 1, "color": AMBER})
    L.append({"op": "dot", "xy": [cx + 1, 12], "size": 1, "color": AMBER})
    return doc("boss_hel_velli_duel", L)


def thar_krai_tam():
    L = []
    L.append({"op": "fill", "color": VOID})
    # mine strata
    for y, c in [(6, NVOID), (14, PANEL), (26, NVOID), (34, PANEL)]:
        L.append({"op": "hline", "y": y, "x_range": [0, W], "color": c})
    L.append({"op": "noise", "xywh": [0, 0, W, 40], "color": NVOID,
              "density": 0.10, "seed": 17})
    # lanterns — the courtesy of light
    for lx, ly in [(22, 18), (138, 14)]:
        L.append({"op": "shade", "xywh": [lx - 10, ly - 8, 20, 16], "color": PANEL,
                  "amount": 0.5})
        L.append({"op": "shade", "xywh": [lx - 6, ly - 5, 12, 10], "color": AMBER,
                  "amount": 0.3})
        L.append({"op": "disk", "xy": [lx, ly], "r": 2, "color": AMBER})
        L.append({"op": "dot", "xy": [lx, ly - 1], "size": 1, "color": STAR})
        L.append({"op": "vline", "x": lx, "y_range": [ly - 8, ly - 3], "color": PANEL})
    # Thar-Krai-Tam — seven feet two, filling the seam
    cx = 80
    L.append({"op": "poly", "points": [[cx - 7, 10], [cx + 7, 10],
                                       [cx + 9, 38], [cx - 9, 38]], "color": PANEL})
    L.append({"op": "dot", "xy": [cx, 6], "size": 6, "color": PANEL})            # head
    # four arms — two crossed, two at rest
    L.append({"op": "polyline", "points": [[cx - 7, 15], [cx + 6, 19]], "color": PANEL})
    L.append({"op": "polyline", "points": [[cx + 7, 15], [cx - 6, 19]], "color": PANEL})
    L.append({"op": "polyline", "points": [[cx - 7, 22], [cx - 12, 30]], "color": PANEL})
    L.append({"op": "polyline", "points": [[cx + 7, 22], [cx + 12, 30]], "color": PANEL})
    # lantern-side edge light
    L.append({"op": "vline", "x": cx - 8, "y_range": [12, 36], "color": AMBER})
    # the silvered blade, sheathed until the third turn
    L.append({"op": "polyline", "points": [[cx + 8, 27], [cx + 15, 33]], "color": SILVER})
    L.append({"op": "dot", "xy": [cx + 8, 26], "size": 2, "color": CREAM})       # hilt
    # eyes
    L.append({"op": "dot", "xy": [cx - 2, 6], "size": 1, "color": CREAM})
    L.append({"op": "dot", "xy": [cx + 2, 6], "size": 1, "color": CREAM})
    return doc("boss_thar_krai_tam", L)


def eight_star(L, x, y, color):
    L.append({"op": "polyline", "points": [[x, y - 3], [x, y + 3]], "color": color})
    L.append({"op": "polyline", "points": [[x - 3, y], [x + 3, y]], "color": color})
    L.append({"op": "dot", "xy": [x - 2, y - 2], "size": 1, "color": color})
    L.append({"op": "dot", "xy": [x + 2, y - 2], "size": 1, "color": color})
    L.append({"op": "dot", "xy": [x - 2, y + 2], "size": 1, "color": color})
    L.append({"op": "dot", "xy": [x + 2, y + 2], "size": 1, "color": color})


def nalat():
    L = []
    L.append({"op": "fill", "color": VOID})
    # the room — columns, a floor that answers to him
    L.append({"op": "vband", "x_range": [10, 15], "color": NVOID})
    L.append({"op": "vband", "x_range": [145, 150], "color": NVOID})
    L.append({"op": "vline", "x": 12, "y_range": [0, 26], "color": PANEL})
    L.append({"op": "vline", "x": 147, "y_range": [0, 26], "color": PANEL})
    L.append({"op": "hband", "y_range": [26, 40], "color": NVOID})
    L.append({"op": "hline", "y": 26, "x_range": [0, W], "color": PANEL})
    L.append({"op": "polyline", "points": [[20, 40], [50, 26]], "color": PANEL})
    L.append({"op": "polyline", "points": [[140, 40], [110, 26]], "color": PANEL})
    # the stars in the floor · brighter where he stands
    eight_star(L, 46, 33, PANEL)
    eight_star(L, 114, 33, PANEL)
    eight_star(L, 68, 36, STAR)
    eight_star(L, 92, 36, STAR)
    # Nalat — Order Senior Second Class
    cx = 80
    L.append({"op": "shade", "xywh": [cx - 14, 24, 28, 12], "color": CORTEX,
              "amount": 0.25})                                       # the room, siding with him
    L.append({"op": "poly", "points": [[cx - 5, 12], [cx + 5, 12],
                                       [cx + 8, 34], [cx - 8, 34]], "color": CORTEX})  # robe
    L.append({"op": "vline", "x": cx, "y_range": [13, 33], "color": PANEL})     # robe seam
    L.append({"op": "dot", "xy": [cx, 8], "size": 4, "color": CREAM})           # head
    L.append({"op": "hline", "y": 6, "x_range": [cx - 2, cx + 3], "color": CORTEX})  # cap
    # the ceremonial blade, held wrong on purpose
    L.append({"op": "polyline", "points": [[cx + 7, 20], [cx + 13, 14]], "color": SILVER})
    L.append({"op": "dot", "xy": [cx + 7, 21], "size": 2, "color": STAR})       # hilt
    # the eight points on his collar
    L.append({"op": "dot", "xy": [cx - 2, 13], "size": 1, "color": STAR})
    L.append({"op": "dot", "xy": [cx + 2, 13], "size": 1, "color": STAR})
    return doc("boss_nalat", L)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for d in [hel_velli(), thar_krai_tam(), nalat()]:
        path = os.path.join(OUT_DIR, d["id"] + ".json")
        with open(path, "w") as f:
            json.dump(d, f, indent=1)
            f.write("\n")
        print("wrote", path)


if __name__ == "__main__":
    main()
