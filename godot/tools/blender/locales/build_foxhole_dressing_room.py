"""foxhole_dressing_room — backstage at the Foxhole venue. Bulb-framed
vanity mirror, clothing rack with garments, a beat-up couch, guitar
cases, a taped-up setlist + stickers, a mini-fridge. Warm dressing-
room bulb lighting (see .tscn).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling
from _props.safety import make_smoke_detector

ROOM_W = 4.0; ROOM_D = 4.0; CEIL = 2.6
PAL_WALL = {"wall":(0.46,0.40,0.34,1.0),"baseboard":(0.28,0.22,0.16,1.0)}
COL_FLOOR = (0.42,0.34,0.28,1.0); COL_SEAM = (0.24,0.18,0.14,1.0)
COL_WOOD = (0.42,0.30,0.20,1.0); COL_STEEL = P.METAL_STEEL; COL_BLACK = P.METAL_BLACK
COL_BULB = (0.98,0.92,0.72,1.0); COL_MIRROR = (0.38,0.42,0.48,0.9)
COL_COUCH = (0.40,0.28,0.34,1.0); COL_COUCH_CUSH = (0.48,0.34,0.40,1.0)
COL_ACCENT = (0.86,0.46,0.24,1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)

def build_vanity():
    vy = 3.60
    # Table
    make_box("Vanity_Top", (0.0, vy, 0.75), (1.60, 0.46, 0.05), COL_WOOD)
    for sx in (-0.72, 0.72):
        make_box(f"Vanity_Side_{sx:+.0f}", (sx, vy, 0.37), (0.06, 0.44, 0.74), COL_WOOD)
    make_box("Vanity_Back", (0.0, vy+0.20, 0.42), (1.60, 0.04, 0.60), (0.36,0.26,0.18,1.0))
    # Mirror + frame
    make_box("Vanity_MirrorFrame", (0.0, 3.83, 1.55), (1.06, 0.04, 0.96), (0.30,0.22,0.16,1.0))
    make_box("Vanity_Mirror", (0.0, 3.80, 1.55), (0.92, 0.03, 0.82), COL_MIRROR)
    # Bulb frame — top row + side columns
    for bi in range(5):
        bx = -0.44 + bi * 0.22
        make_cyl(f"Vanity_BulbTop_{bi}", (bx, 3.78, 2.06), 0.045, 0.06, COL_BULB, segments=8)
    for si, bz in enumerate([1.30, 1.55, 1.80]):
        make_cyl(f"Vanity_BulbL_{si}", (-0.58, 3.78, bz), 0.045, 0.06, COL_BULB, segments=8)
        make_cyl(f"Vanity_BulbR_{si}", (0.58, 3.78, bz), 0.045, 0.06, COL_BULB, segments=8)
    # Clutter on the vanity
    make_cyl("Vanity_Jar", (-0.30, vy, 0.85), 0.05, 0.14, (0.42,0.62,0.58,0.6))
    make_cyl("Vanity_Bottle", (0.34, vy, 0.87), 0.04, 0.18, (0.72,0.32,0.24,1.0))
    make_box("Vanity_Tin", (0.10, vy-0.10, 0.80), (0.14,0.10,0.06), COL_STEEL)
    # Stool
    make_cyl("Vanity_Stool_Seat", (0.0, 3.05, 0.46), 0.16, 0.05, COL_COUCH, segments=12)
    for li, (ox, oy) in enumerate([(-0.11,-0.11),(0.11,-0.11),(-0.11,0.11),(0.11,0.11)]):
        make_cyl(f"Vanity_Stool_Leg_{li}", (ox, 3.05+oy, 0.22), 0.015, 0.44, COL_BLACK)

def build_clothing_rack():
    rx = 1.62
    for pi, py in enumerate([1.0, 2.8]):
        make_cyl(f"Rack_Pole_{pi}", (rx, py, 0.85), 0.02, 1.70, COL_STEEL)
        make_cyl(f"Rack_Foot_{pi}", (rx, py, 0.03), 0.14, 0.03, COL_BLACK, segments=10)
    make_cyl("Rack_Bar", (rx, 1.9, 1.68), 0.015, 1.80, COL_STEEL, axis='Y')
    garment_cols = [(0.24,0.28,0.42,1.0),(0.62,0.20,0.22,1.0),(0.20,0.20,0.22,1.0),
                    (0.52,0.42,0.24,1.0),(0.32,0.42,0.36,1.0)]
    for gi in range(5):
        gy = 1.15 + gi * 0.40
        make_cyl(f"Rack_Hanger_{gi}", (rx, gy, 1.62), 0.008, 0.10, COL_STEEL)
        make_box(f"Rack_Garment_{gi}", (rx-0.02, gy, 1.15), (0.10, 0.20, 0.80), garment_cols[gi])

def build_couch():
    cx = -1.52
    make_box("Couch_Base", (cx, 2.0, 0.24), (0.72, 1.70, 0.22), COL_COUCH)
    make_box("Couch_Back", (cx-0.28, 2.0, 0.58), (0.18, 1.70, 0.56), COL_COUCH)
    for ay in (1.20, 2.80):
        make_box(f"Couch_Arm_{ay:.0f}", (cx, ay, 0.42), (0.68, 0.16, 0.36), COL_COUCH)
    for ci, cy in enumerate([1.55, 2.45]):
        make_box(f"Couch_SeatCush_{ci}", (cx+0.02, cy, 0.40), (0.60, 0.62, 0.14), COL_COUCH_CUSH)
        make_box(f"Couch_BackCush_{ci}", (cx-0.18, cy, 0.62), (0.20, 0.60, 0.40), COL_COUCH_CUSH)
    # A tossed jacket on the arm
    make_box("Couch_Jacket", (cx, 1.20, 0.62), (0.62, 0.30, 0.10), (0.30,0.22,0.20,1.0))

def _make_guitar_case(prefix, cx, cy, col, rot_y=False):
    if rot_y:
        make_box(f"{prefix}_Body", (cx, cy, 0.13), (0.90, 0.44, 0.14), col)
        make_box(f"{prefix}_Neck", (cx+0.62, cy, 0.13), (0.42, 0.16, 0.11), col)
        make_box(f"{prefix}_Handle", (cx, cy-0.24, 0.20), (0.16, 0.03, 0.03), COL_BLACK)
        make_box(f"{prefix}_LatchA", (cx-0.20, cy-0.23, 0.13), (0.05,0.02,0.05), COL_STEEL)
        make_box(f"{prefix}_LatchB", (cx+0.20, cy-0.23, 0.13), (0.05,0.02,0.05), COL_STEEL)
    else:
        make_box(f"{prefix}_Body", (cx, cy, 0.13), (0.44, 0.90, 0.14), col)
        make_box(f"{prefix}_Neck", (cx, cy+0.62, 0.13), (0.16, 0.42, 0.11), col)
        make_box(f"{prefix}_Handle", (cx-0.24, cy, 0.20), (0.03, 0.16, 0.03), COL_BLACK)
        make_box(f"{prefix}_LatchA", (cx-0.23, cy-0.20, 0.13), (0.02,0.05,0.05), COL_STEEL)
        make_box(f"{prefix}_LatchB", (cx-0.23, cy+0.20, 0.13), (0.02,0.05,0.05), COL_STEEL)

def build_cases():
    _make_guitar_case("Case_A", -0.30, 0.70, (0.14,0.12,0.12,1.0), rot_y=False)
    _make_guitar_case("Case_B", 0.60, 0.55, (0.28,0.20,0.14,1.0), rot_y=True)

def build_setlist_stickers():
    # Taped setlist on the east wall by the door.
    make_box("Setlist_Paper", (1.95, 0.90, 1.45), (0.02, 0.24, 0.32), P.PAPER)
    for li in range(6):
        make_box(f"Setlist_Line_{li}", (1.938, 0.90, 1.58 - li*0.05), (0.002, 0.18, 0.012), (0.20,0.18,0.16,1.0))
    for ti, (ty, tz) in enumerate([(0.80,1.62),(1.02,1.55),(0.86,1.32)]):
        make_box(f"Setlist_Tape_{ti}", (1.94, ty, tz), (0.006, 0.05, 0.03), (0.86,0.82,0.70,0.7))
    # Sticker cluster on the same wall.
    sticker_cols = [(0.86,0.24,0.20,1.0),(0.24,0.62,0.72,1.0),(0.92,0.72,0.24,1.0),(0.42,0.62,0.36,1.0)]
    for si, (sy, sz) in enumerate([(1.40,1.70),(1.55,1.55),(1.42,1.42),(1.58,1.78)]):
        make_box(f"Sticker_{si}", (1.94, sy, sz), (0.006, 0.10, 0.10), sticker_cols[si])

def build_mini_fridge():
    fx, fy = 1.55, 3.45
    make_box("Fridge_Body", (fx, fy, 0.42), (0.52, 0.50, 0.84), (0.82,0.80,0.76,1.0))
    make_box("Fridge_Door", (fx-0.27, fy, 0.42), (0.03, 0.46, 0.78), (0.88,0.86,0.82,1.0))
    make_box("Fridge_Handle", (fx-0.30, fy-0.16, 0.50), (0.03, 0.04, 0.24), COL_STEEL)
    make_box("Fridge_Top", (fx, fy, 0.86), (0.52, 0.50, 0.03), (0.72,0.70,0.66,1.0))
    # Stuff on top: a couple of cans + a coffee mug
    for ci, cy in enumerate([3.32, 3.46, 3.60]):
        make_cyl(f"Fridge_Can_{ci}", (fx+0.06, cy, 0.94), 0.03, 0.12,
                 [(0.86,0.24,0.20,1.0),(0.24,0.42,0.68,1.0),(0.42,0.62,0.36,1.0)][ci])

def build_rug():
    make_cyl("Rug", (-0.2, 1.7, 0.012), 1.00, 0.005, COL_ACCENT, segments=20)

def build_ceiling_infra():
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def main():
    clear_scene()
    build_shell()
    build_vanity()
    build_clothing_rack()
    build_couch()
    build_cases()
    build_setlist_stickers()
    build_mini_fridge()
    build_rug()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/foxhole_dressing_room.glb"))
    print(f"\n[build_foxhole_dressing_room] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
