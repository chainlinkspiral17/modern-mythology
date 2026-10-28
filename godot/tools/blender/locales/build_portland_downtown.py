"""portland_downtown — vol 3 ch 4 "invitation only": a Friday in downtown
Portland, early 2000s, and the vacant gallery that night (draft 1, 2026-10-28).

It played on vol 7's 2052 Smolvud Main Street and the 2052 cedar tower
lobby. Vol 3 is "all over the map, but early 2000s" (Andy, 2026-10-27).
The text:
  "We wandered streets in the early evening, window drop shopping
   independent record stores, trailblazing Powells book store"
  "She found me ... Practically assaulted me in the street"; "The three of
   us in the road, just like that."
  "bought disposable cameras which we emptied, pow pow pow, in a pigeon
   occupied park plaza"; "The whole flock lifts an inch off the stones and
   settles again where it was."            → portland_street_friday (+ the plaza)
  the invite's "gallery space she told us her friend once used, but had
   since reverted vacant": "A colic youth ... unlocked the glass doors, kick
   stopped them open and disappeared into dark leaving us to watch as
   lights appeared non-sequentially"; "The floor was unswept meaning dust
   was kicked up and footprints emerged"; "a table with refreshments set up
   along one wall, a trashcan filled with ice and cans of beer"; "a strange
   young woman in the corner"           → vacant_gallery_lobby

PROPOSED: the block itself (a Burnside-and-10th-like corner: a city block
of a bookstore with its red band, brick four-storeys, a record store, a
coffee shop, the streetcar rails of 2001), the plaza's brick amphitheatre
steps, the gallery's size and its dark screening room beyond.

Blender: x east, y north, z up; Godot (x, z, -y). The street runs E-W on
y 0..14 (the camera's sidewalk on the south side, y 0..4); the plaza at
its east end (x 40..64); the gallery a separate area at x 100..114.

DRAFT 2 targets: hero art for the bookstore's sign, the record store's
window of LP covers, the invite card; figures in the line at the gallery
door; the screening room beyond the dark; Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_blob, make_taper_cyl,
                             join_stock, export_glb)
from _props.structure import make_wall, make_wall_with_openings
from _props.furniture import make_chair

BRICK = (0.56, 0.32, 0.26, 1.0)
BRICK_DK = (0.44, 0.26, 0.22, 1.0)
CREAM = (0.86, 0.82, 0.72, 1.0)
ASPHALT = (0.22, 0.22, 0.24, 1.0)
WALK = (0.66, 0.64, 0.60, 1.0)
GLASS = (0.30, 0.36, 0.40, 1.0)
WARM = (1.0, 0.86, 0.60, 1.0)
TREE = (0.26, 0.38, 0.22, 1.0)


def _rng(seed):
    s = [seed & 0x7fffffff or 1]
    def r():
        s[0] = (s[0] * 1103515245 + 12345) & 0x7fffffff
        return s[0] / 0x7fffffff
    return r


def _facade(name, x0, x1, y, h, col, storefront_col, sign_col=None, lit=True):
    """A building face on the street's north side (y = its face), its
    storefront at the bottom and rows of windows above."""
    w = x1 - x0
    xc = (x0 + x1) / 2.0
    make_box(f"{name}_Mass", (xc, y + 6.0, h / 2.0), (w, 12.0, h), col)
    make_box(f"{name}_Storefront_Glass", (xc, y - 0.02, 1.6), (w - 1.2, 0.04, 2.6), storefront_col)
    make_box(f"{name}_Storefront_Kick", (xc, y - 0.03, 0.2), (w - 1.0, 0.06, 0.4), (0.20, 0.20, 0.22, 1.0))
    if sign_col:
        make_box(f"{name}_Sign", (xc, y - 0.10, 3.3), (w - 1.6, 0.16, 0.7), sign_col)
    floors = int((h - 4.2) / 3.2)
    for f in range(floors):
        for k in range(int(w / 2.2)):
            make_box(f"{name}_Window_{f}_{k}", (x0 + 1.2 + k * 2.2, y - 0.02, 5.2 + f * 3.2), (1.2, 0.04, 1.6),
                     WARM if (lit and (f + k) % 3 == 0) else GLASS)
    make_box(f"{name}_Cornice", (xc, y - 0.15, h - 0.2), (w + 0.2, 0.3, 0.4), CREAM)


def build_street():
    """The block: the bookstore on the corner with its red band, a record
    store, a coffee shop, brick four-storeys; the street and its streetcar
    rails; the south sidewalk the camera stands on."""
    make_box("Street_Asphalt", (0.0, 7.0, -0.05), (140.0, 10.0, 0.06), ASPHALT)
    for s in (-1, 1):
        make_box(f"Streetcar_Rail_{s:+d}", (0.0, 7.0 + s * 0.72, -0.015), (140.0, 0.08, 0.02), (0.56, 0.56, 0.58, 1.0))
    for k in range(10):
        make_box(f"Street_Dash_{k}", (-60.0 + k * 13.0, 9.6, -0.018), (3.0, 0.12, 0.01), (0.92, 0.88, 0.62, 1.0))
    make_box("Sidewalk_S", (0.0, 0.0, 0.02), (140.0, 4.0, 0.14), WALK)
    make_box("Sidewalk_N", (0.0, 14.0, 0.02), (140.0, 4.0, 0.14), WALK)
    make_box("Curb_S", (0.0, 2.05, 0.05), (140.0, 0.12, 0.18), (0.76, 0.74, 0.70, 1.0))
    make_box("Curb_N", (0.0, 11.95, 0.05), (140.0, 0.12, 0.18), (0.76, 0.74, 0.70, 1.0))
    # north side, facing the camera across the street
    _facade("Bookstore", -30.0, -4.0, 16.0, 13.0, (0.80, 0.76, 0.66, 1.0), (0.96, 0.84, 0.56, 1.0), sign_col=(0.74, 0.14, 0.14, 1.0))
    make_box("Bookstore_Corner_Sign", (-4.4, 15.4, 6.0), (0.3, 1.2, 5.0), (0.74, 0.14, 0.14, 1.0))
    make_box("Bookstore_Entry_Canopy", (-17.0, 15.2, 3.0), (6.0, 1.8, 0.2), (0.74, 0.14, 0.14, 1.0))
    for k in range(6):
        make_box(f"Bookstore_Window_Books_{k}", (-26.0 + k * 3.8, 15.9, 1.0), (2.6, 0.30, 0.9), ((0.4, 0.3, 0.2, 1.0), (0.2, 0.3, 0.5, 1.0), (0.6, 0.2, 0.2, 1.0))[k % 3])
    _facade("Record_Store", -2.0, 8.0, 16.0, 9.6, BRICK, (0.92, 0.76, 0.50, 1.0), sign_col=(0.12, 0.12, 0.14, 1.0))
    for k in range(8):
        make_box(f"Record_Store_LP_{k}", (-1.0 + k * 1.1, 15.9, 1.7 + (k % 2) * 0.4), (0.31, 0.02, 0.31),
                 ((0.86, 0.30, 0.20, 1.0), (0.20, 0.30, 0.70, 1.0), (0.94, 0.86, 0.30, 1.0), (0.10, 0.10, 0.10, 1.0))[k % 4])
    _facade("Coffee_Shop", 10.0, 18.0, 16.0, 9.6, BRICK_DK, (1.0, 0.82, 0.52, 1.0), sign_col=(0.18, 0.34, 0.26, 1.0))
    make_box("Coffee_Shop_Awning", (14.0, 15.2, 3.0), (7.6, 1.6, 0.2), (0.18, 0.34, 0.26, 1.0))
    _facade("Brick_Block_E", 20.0, 38.0, 16.0, 16.2, BRICK, (0.86, 0.70, 0.48, 1.0))
    _facade("Brick_Block_W", -50.0, -32.0, 16.0, 19.4, BRICK_DK, (0.80, 0.68, 0.48, 1.0))
    # the south side behind the camera (seen in the reverse)
    _facade("South_Block", -40.0, 36.0, -14.0, 13.0, (0.70, 0.66, 0.58, 1.0), (0.84, 0.70, 0.48, 1.0))
    # street trees, newspaper boxes, a bus shelter, parked early-2000s cars
    r = _rng(2001)
    for k in range(10):
        tx = -44.0 + k * 9.0
        make_taper_cyl(f"Street_Tree_{k}_Trunk", (tx, 13.4, 1.6), 0.14, 0.10, 3.2, (0.36, 0.28, 0.22, 1.0), segments=8)
        make_blob(f"Street_Tree_{k}_Crown", (tx, 13.4, 4.4), 1.8, TREE, noise=0.25, seed=100 + k, squash=0.85)
    for k, (bx, col) in enumerate(((-6.0, (0.20, 0.36, 0.70, 1.0)), (-5.4, (0.86, 0.20, 0.20, 1.0)), (-4.8, (0.94, 0.80, 0.20, 1.0)))):
        make_box(f"News_Box_{k}", (bx, 13.0, 0.55), (0.46, 0.40, 1.0), col)
    make_box("Bus_Shelter_Roof", (22.0, 1.2, 2.5), (3.6, 1.4, 0.08), (0.30, 0.32, 0.34, 1.0))
    make_box("Bus_Shelter_Back", (22.0, 0.55, 1.3), (3.6, 0.04, 2.3), (0.50, 0.58, 0.62, 1.0))
    for k, (cx, cy, col) in enumerate(((-24.0, 11.0, (0.62, 0.62, 0.66, 1.0)), (-34.0, 11.0, (0.20, 0.30, 0.50, 1.0)),
                                       (16.0, 3.0, (0.60, 0.14, 0.14, 1.0)), (-30.0, 3.0, (0.86, 0.84, 0.78, 1.0)))):
        make_box(f"Parked_Car_{k}_Body", (cx, cy, 0.62), (4.5, 1.75, 0.72), col)
        make_box(f"Parked_Car_{k}_Cabin", (cx - 0.2, cy, 1.18), (2.5, 1.6, 0.46), (0.26, 0.30, 0.34, 1.0))
        for s in (-1, 1):
            for e in (-1, 1):
                make_cyl(f"Parked_Car_{k}_Wheel_{s:+d}{e:+d}", (cx + s * 1.4, cy + e * 0.82, 0.32), 0.32, 0.20, (0.10, 0.10, 0.10, 1.0), segments=10, axis='Y')
    for k in range(6):
        make_cyl(f"Street_Lamp_{k}_Pole", (-40.0 + k * 16.0, 2.4, 2.4), 0.07, 4.8, (0.20, 0.22, 0.20, 1.0), segments=8)
        make_blob(f"Street_Lamp_{k}_Globe", (-40.0 + k * 16.0, 2.4, 4.95), 0.24, (1.0, 0.92, 0.72, 1.0), noise=0.02, seed=k, squash=1.0)


def build_plaza():
    """The pigeon-occupied park plaza at the street's east end: brick paving,
    the amphitheatre steps, the flock on the stones."""
    make_box("Plaza_Brick", (52.0, 7.0, 0.0), (24.0, 22.0, 0.06), (0.62, 0.40, 0.32, 1.0))
    for k in range(22):
        make_box(f"Plaza_Brick_Line_{k}", (52.0, -3.5 + k * 1.0, 0.032), (24.0, 0.02, 0.004), (0.52, 0.34, 0.28, 1.0))
    for k in range(5):
        make_box(f"Plaza_Step_{k}", (60.0 - k * 0.0, 14.0 + k * 0.6, 0.12 + k * 0.24), (16.0, 0.6, 0.24 + k * 0.48), (0.66, 0.44, 0.36, 1.0))
    r = _rng(26)
    for k in range(34):
        px, py = 46.0 + r() * 10.0, 2.0 + r() * 8.0
        make_blob(f"Pigeon_{k}", (px, py, 0.12), 0.10, ((0.46, 0.48, 0.54, 1.0), (0.36, 0.38, 0.42, 1.0), (0.56, 0.56, 0.58, 1.0))[k % 3],
                  noise=0.15, seed=k, squash=0.75)
        make_blob(f"Pigeon_{k}_Head", (px + 0.08, py, 0.22), 0.045, (0.30, 0.34, 0.40, 1.0), noise=0.05, seed=k + 50, squash=1.0)
    for k in range(4):
        make_cyl(f"Plaza_Lamp_{k}_Pole", (44.0 + k * 6.0, 12.0, 2.2), 0.08, 4.4, (0.18, 0.20, 0.18, 1.0), segments=8)
        make_blob(f"Plaza_Lamp_{k}_Globe", (44.0 + k * 6.0, 12.0, 4.5), 0.26, (1.0, 0.92, 0.72, 1.0), noise=0.02, seed=k + 9, squash=1.0)
    make_box("Plaza_Bench", (50.0, -1.5, 0.45), (2.4, 0.5, 0.10), (0.40, 0.30, 0.20, 1.0))
    make_box("Plaza_Building_E", (72.0, 7.0, 10.0), (12.0, 30.0, 20.0), (0.76, 0.72, 0.64, 1.0))


def build_gallery():
    """x 100..114, y 0..10: the vacant gallery space behind its glass doors,
    one long room, raw and unswept; the refreshment table along the west
    wall, the trashcan of ice and beer; fluorescent rows, some lit; the
    doorway at the back into dark (the screening)."""
    x0, x1, y0, y1, H = 100.0, 114.0, 0.0, 10.0, 3.6
    PAL = {"wall": (0.86, 0.86, 0.84, 1.0), "baseboard": (0.60, 0.60, 0.58, 1.0)}
    make_box("Gallery_Floor", ((x0 + x1) / 2, (y0 + y1) / 2, -0.03), (x1 - x0, y1 - y0, 0.06), (0.60, 0.58, 0.54, 1.0))
    r = _rng(31)
    for k in range(40):
        make_box(f"Gallery_Footprint_{k}", (x0 + 2.0 + r() * 10.0, y0 + 0.8 + r() * 8.0, 0.002), (0.10, 0.26, 0.002), (0.48, 0.46, 0.42, 1.0))
    for k in range(10):
        make_box(f"Gallery_Dust_{k}", (x0 + 1.0 + r() * 12.0, y0 + 0.5 + r() * 9.0, 0.003), (0.8 + r(), 0.6 + r(), 0.002), (0.66, 0.64, 0.58, 1.0))
    make_box("Gallery_Ceiling", ((x0 + x1) / 2, (y0 + y1) / 2, H + 0.05), (x1 - x0, y1 - y0, 0.10), (0.30, 0.30, 0.32, 1.0))
    for k in range(3):
        make_cyl(f"Gallery_Duct_{k}", ((x0 + x1) / 2, 2.0 + k * 3.0, H - 0.35), 0.24, x1 - x0, (0.62, 0.64, 0.66, 1.0), segments=10, axis='X')
    lit = {(0, 1), (1, 3), (2, 0), (2, 2)}
    for k in range(3):
        for j in range(4):
            make_box(f"Gallery_Tube_{k}_{j}", (x0 + 2.5 + j * 3.0, 1.8 + k * 3.2, H - 0.6), (1.2, 0.18, 0.06),
                     (0.96, 1.0, 1.0, 1.0) if (k, j) in lit else (0.46, 0.48, 0.50, 1.0))
    # the glass front on y 0 with its doors kick-stopped open
    make_wall_with_openings("Gallery_Wall_S", ((x0 + x1) / 2, y0, 0.0), length=x1 - x0, height=H, thickness=0.16, axis='X', palette=PAL,
                            baseboard_face_sign=+1, openings=[(104.0, 1.4, 5.0, 2.6), (110.0, 1.4, 5.0, 2.6)])
    make_box("Gallery_Front_Glass", (110.0, y0, 1.4), (5.0, 0.03, 2.6), (0.30, 0.36, 0.40, 1.0))
    make_box("Gallery_Door_L_Open", (103.0, y0 + 0.5, 1.15), (0.04, 0.95, 2.3), (0.30, 0.36, 0.40, 1.0))
    make_box("Gallery_Door_R_Open", (105.0, y0 + 0.5, 1.15), (0.04, 0.95, 2.3), (0.30, 0.36, 0.40, 1.0))
    make_box("Gallery_Doorstop", (105.0, y0 + 0.95, 0.03), (0.08, 0.14, 0.05), (0.40, 0.20, 0.14, 1.0))
    make_wall("Gallery_Wall_W", (x0, (y0 + y1) / 2, 0.0), length=y1 - y0, height=H, thickness=0.16, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall("Gallery_Wall_E", (x1, (y0 + y1) / 2, 0.0), length=y1 - y0, height=H, thickness=0.16, axis='Y', palette=PAL, baseboard_face_sign=-1)
    make_wall_with_openings("Gallery_Wall_N", ((x0 + x1) / 2, y1, 0.0), length=x1 - x0, height=H, thickness=0.16, axis='X', palette=PAL,
                            baseboard_face_sign=-1, openings=[(107.0, 1.2, 1.8, 2.4)])
    make_box("Gallery_Dark_Beyond", (107.0, y1 + 2.0, 1.6), (6.0, 0.1, 3.2), (0.02, 0.02, 0.03, 1.0))
    # ghosts of the old gallery: nail holes, pale rectangles where frames hung
    for k in range(5):
        make_box(f"Gallery_Pale_Rect_{k}", (x1 - 0.09, 1.4 + k * 1.7, 1.7), (0.004, 1.0, 0.8), (0.92, 0.92, 0.90, 1.0))
    # the refreshment table along the west wall, the trashcan of ice and beer
    make_box("Refreshment_Table_Top", (x0 + 0.6, 5.0, 0.74), (0.76, 2.4, 0.04), (0.90, 0.90, 0.88, 1.0))
    make_box("Refreshment_Table_Cloth", (x0 + 0.6, 5.0, 0.60), (0.80, 2.44, 0.28), (0.94, 0.94, 0.92, 1.0))
    for s in (-1, 1):
        make_box(f"Refreshment_Table_Leg_{s:+d}", (x0 + 0.6, 5.0 + s * 1.1, 0.36), (0.6, 0.04, 0.72), (0.30, 0.30, 0.30, 1.0))
    for k in range(6):
        make_cyl(f"Refreshment_Cup_{k}", (x0 + 0.5, 4.1 + k * 0.16, 0.81), 0.04, 0.11, (0.94, 0.94, 0.92, 1.0), segments=8)
    make_box("Refreshment_Chips_Bowl", (x0 + 0.6, 5.4, 0.80), (0.36, 0.36, 0.08), (0.86, 0.70, 0.30, 1.0))
    make_box("Refreshment_Cookie_Tray", (x0 + 0.6, 6.0, 0.77), (0.40, 0.30, 0.02), (0.80, 0.80, 0.82, 1.0))
    make_cyl("Trashcan_Beer", (x0 + 0.6, 6.9, 0.40), 0.30, 0.80, (0.30, 0.32, 0.30, 1.0), segments=14)
    make_cyl("Trashcan_Beer_Ice", (x0 + 0.6, 6.9, 0.80), 0.28, 0.02, (0.86, 0.92, 0.96, 1.0), segments=14)
    for k in range(9):
        a = k * math.tau / 9.0
        make_cyl(f"Trashcan_Beer_Can_{k}", (x0 + 0.6 + math.cos(a) * 0.17, 6.9 + math.sin(a) * 0.17, 0.85), 0.033, 0.12,
                 ((0.80, 0.80, 0.84, 1.0), (0.20, 0.30, 0.70, 1.0), (0.80, 0.16, 0.14, 1.0))[k % 3], segments=8)
    # folding chairs scattered, the strange young woman's corner (NE)
    for k, (cx, cy, yaw) in enumerate(((109.5, 6.5, 0.4), (110.8, 7.4, -0.3), (112.6, 8.6, 2.6), (106.0, 3.2, 1.2))):
        make_chair(f"Folding_Chair_{k}", cx, cy, yaw=yaw, wood=(0.36, 0.36, 0.38, 1.0))
    make_box("Corner_Rug_Remnant", (112.6, 9.0, 0.004), (1.4, 1.0, 0.006), (0.56, 0.30, 0.32, 1.0))


def main():
    clear_scene()
    build_street()
    build_plaza()
    build_gallery()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/portland_downtown.glb"))
    print(f"\n[build_portland_downtown] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
