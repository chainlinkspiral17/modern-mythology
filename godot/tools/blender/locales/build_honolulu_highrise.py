"""honolulu_highrise — vol 3 ch 6 "arcadeum": the Honolulu high-rise's
ground floor and the boutique game store in it (draft 1, 2026-10-28).

It played on vol 7's 2052 cedar tower lobby and vol 6's 2026 Cosmic Comics.
Vol 3 is "all over the map, but early 2000s" (Andy, 2026-10-27). The text:
  "The first office is a hollowed out chunk of Honolulu high-rise. Ground
   floors are tourist trap photography parlour, travel agency, corner suit
   shoppe & luggage boutique."
  "she ... went to the lobby, and returned by a boutique video game store
   that sat between a men's suit and leather case store and a dry cleaner"
  "The name outside the game store was a cheap box vinyl back-lit
   fluorescent number that promised only COMPUTER GAMES, and inside an
   anxious man staffed the store."
  "The newest game in their front window display was Mountaintop's Final
   Cut ... one of their first CD-ROM enhanced titles."
  "She did eye something unique in the clear display underneath the
   register. A mysterious game by the name WHAT LIES BEYOND in a regal
   cloudy blue script."
  "He swiped it under two-part transfer paper in a hard plastic shell."
  (a manual card imprinter); "These are old used games."
                         → honolulu_lobby, honolulu_game_store

PROPOSED: the lobby's size and finish (a 1970s tower's marble and brass,
a double-height glass street front), the street outside (Bishop-Street-like
palms and towers), the store's shelving and its posters.

Blender: x east, y north, z up; Godot (x, z, -y). The lobby x -9..9,
y 0..16, 5.5 m high, its glass front on y 0 facing the street (y < 0).
The game store opens off the lobby's east wall: x 9..15, y 5.7..10.3.

DRAFT 2 (2026-10-30): the four shops are rooms 5.8 m deep, not 2 m boxes.
The parlour has a painted beach backdrop, softboxes, a camera on a tripod,
leis and a surfboard. The agency has two desks with beige PCs and island
posters. The suit shop has wall rails of suits, a shirt table, a tie case,
a three-way mirror and a luggage wall. The dry cleaner has a counter and
a garment conveyor of bagged clothes. The towers across the street are
curtain walls: mullions every 1.5 m, floor spandrels, lit storefronts.

DRAFT 3 targets: hero art for the shop signs, the travel agency's island
posters and the game boxes (Final Cut, WHAT LIES BEYOND); the anxious
clerk's stool and coffee; the dry cleaner's rack seen through its glass;
camera coverage of the window display from the lobby; Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_blob, make_taper_cyl,
                             join_stock, export_glb)
from _props.structure import make_wall_with_openings, make_wall
from _props.furniture import make_stool, make_bench

MARBLE = (0.86, 0.82, 0.74, 1.0)
MARBLE_SEAM = (0.70, 0.66, 0.58, 1.0)
WALL = (0.90, 0.88, 0.82, 1.0)
BRASS = (0.78, 0.64, 0.32, 1.0)
GLASS = (0.62, 0.74, 0.78, 0.25)
DARK = (0.14, 0.14, 0.15, 1.0)
CARPET = (0.34, 0.34, 0.38, 1.0)
SHELF = (0.62, 0.58, 0.52, 1.0)
SIGN_LIT = (0.96, 0.98, 1.0, 1.0)
LH = 5.5          # lobby height
SX0, SX1, SY0, SY1, SH = 9.0, 15.0, 5.7, 10.3, 3.0   # the store


def _rng(seed):
    s = [seed & 0x7fffffff or 1]
    def r():
        s[0] = (s[0] * 1103515245 + 12345) & 0x7fffffff
        return s[0] / 0x7fffffff
    return r


def build_lobby():
    """Marble floor, the elevator bank, the security desk, the directory,
    the glass street front, the shopfronts down both sides."""
    make_box("Lobby_Floor", (0.0, 8.0, -0.05), (18.0, 16.0, 0.10), MARBLE)
    for k in range(1, 18):
        make_box(f"Lobby_Floor_Seam_X_{k}", (-9.0 + k, 8.0, 0.002), (0.012, 16.0, 0.004), MARBLE_SEAM)
    for k in range(1, 16):
        make_box(f"Lobby_Floor_Seam_Y_{k}", (0.0, float(k), 0.002), (18.0, 0.012, 0.004), MARBLE_SEAM)
    make_box("Lobby_Runner", (0.0, 5.5, 0.006), (2.4, 11.0, 0.01), (0.44, 0.16, 0.18, 1.0))
    make_box("Lobby_Ceiling", (0.0, 8.0, LH + 0.05), (18.0, 16.0, 0.10), (0.94, 0.92, 0.88, 1.0))
    for k in range(4):
        make_box(f"Lobby_Coffer_{k}", (0.0, 2.5 + k * 3.6, LH - 0.15), (14.0, 0.30, 0.30), (0.88, 0.86, 0.80, 1.0))
    for k in range(6):
        make_cyl(f"Lobby_Downlight_{k}", (-5.0 + (k % 3) * 5.0, 4.0 + (k // 3) * 7.0, LH - 0.02), 0.25, 0.04,
                 (1.0, 0.96, 0.86, 1.0), segments=12)
    # the north wall: four brass elevator doors, indicator dials over them
    make_wall("Lobby_Wall_N", (0.0, 16.1, 0.0), length=18.0, height=LH, thickness=0.20, axis='X',
              palette={"wall": (0.78, 0.72, 0.62, 1.0)})
    for k, ex in enumerate((-4.5, -1.5, 1.5, 4.5)):
        make_box(f"Elevator_{k}_Door", (ex, 15.97, 1.2), (1.2, 0.04, 2.4), BRASS)
        make_box(f"Elevator_{k}_Seam", (ex, 15.94, 1.2), (0.01, 0.02, 2.4), (0.52, 0.42, 0.20, 1.0))
        make_box(f"Elevator_{k}_Frame", (ex, 15.98, 1.25), (1.5, 0.03, 2.6), (0.30, 0.26, 0.20, 1.0))
        make_cyl(f"Elevator_{k}_Dial", (ex, 15.985, 2.85), 0.22, 0.03, BRASS, segments=14, axis='Y')
        make_box(f"Elevator_{k}_Button", (ex + 0.95, 15.985, 1.1), (0.10, 0.03, 0.20), BRASS)
    # the security desk, the guard's stool, the directory board
    make_box("Security_Desk", (0.0, 11.0, 0.55), (3.2, 0.8, 1.1), (0.40, 0.28, 0.20, 1.0))
    make_box("Security_Desk_Top", (0.0, 11.0, 1.12), (3.4, 0.95, 0.05), (0.20, 0.18, 0.16, 1.0))
    make_box("Security_Desk_Monitor", (0.6, 11.2, 1.295), (0.36, 0.30, 0.30), (0.80, 0.78, 0.72, 1.0))
    make_box("Security_Desk_Logbook", (-0.5, 10.8, 1.16), (0.40, 0.28, 0.03), (0.16, 0.20, 0.36, 1.0))
    make_stool("Security_Stool", 0.3, 11.8, h=0.75)
    make_box("Directory_Board", (-7.3, 15.97, 1.8), (1.6, 0.06, 1.6), (0.10, 0.10, 0.12, 1.0))
    for k in range(10):
        make_box(f"Directory_Board_Line_{k}", (-7.3, 15.935, 2.4 - k * 0.13), (1.2, 0.01, 0.03), (0.94, 0.94, 0.90, 1.0))
    # potted palms and a bench by the glass
    for k, (px, py) in enumerate(((-7.6, 1.4), (7.6, 1.4), (-6.0, 14.8), (6.0, 14.8))):
        make_cyl(f"Lobby_Planter_{k}", (px, py, 0.35), 0.38, 0.7, (0.30, 0.26, 0.22, 1.0), segments=14)
        make_taper_cyl(f"Lobby_Palm_{k}_Trunk", (px, py, 1.2), 0.07, 0.05, 1.2, (0.42, 0.34, 0.24, 1.0), segments=8)
        for f in range(6):
            a = f * math.pi / 3.0
            make_blob(f"Lobby_Palm_{k}_Frond_{f}", (px + math.cos(a) * 0.45, py + math.sin(a) * 0.45, 1.85),
                      0.32, (0.24, 0.46, 0.22, 1.0), noise=0.2, seed=k * 7 + f, squash=0.35)
    make_bench("Lobby_Bench", -4.0, 2.2, length=2.2)
    make_bench("Lobby_Bench_E", 4.0, 2.2, length=2.2)


def build_street_front():
    """The double-height glass front on y 0 and the street beyond it."""
    for k in range(10):
        x = -9.0 + k * 2.0
        make_box(f"Front_Mullion_{k}", (x, 0.0, LH / 2.0), (0.10, 0.14, LH), DARK)
    make_box("Front_Mullion_End", (9.0, 0.0, LH / 2.0), (0.10, 0.14, LH), DARK)
    make_box("Front_Transom", (0.0, 0.0, 2.8), (18.0, 0.14, 0.10), DARK)
    make_box("Front_Head", (0.0, 0.0, LH - 0.05), (18.0, 0.20, 0.10), DARK)
    for k in range(9):
        x = -8.0 + k * 2.0
        if abs(x) < 1.1:
            continue        # the doors
        make_box(f"Front_Glass_{k}", (x, 0.0, LH / 2.0), (1.9, 0.02, LH - 0.1), GLASS)
    for s in (-1, 1):
        make_box(f"Front_Door_{s:+d}_Glass", (s * 0.5, 0.0, 1.35), (0.92, 0.02, 2.6), GLASS)
        make_box(f"Front_Door_{s:+d}_Pull", (s * 0.12, -0.03, 1.1), (0.04, 0.04, 0.9), BRASS)
    make_box("Front_Door_Transom_Glass", (0.0, 0.0, 4.15), (1.9, 0.02, 2.6), GLASS)
    # the street: sidewalk, kerb, asphalt, palms, the towers across
    make_box("Street_Sidewalk", (0.0, -3.0, -0.04), (160.0, 6.0, 0.08), (0.74, 0.72, 0.68, 1.0))
    make_box("Street_Kerb", (0.0, -6.05, 0.03), (160.0, 0.15, 0.15), (0.80, 0.78, 0.74, 1.0))
    make_box("Street_Asphalt", (0.0, -11.0, -0.06), (160.0, 10.0, 0.04), (0.20, 0.20, 0.22, 1.0))
    for k in range(5):
        make_box(f"Street_Dash_{k}", (-20.0 + k * 10.0, -11.0, -0.035), (3.0, 0.12, 0.01), (0.94, 0.90, 0.60, 1.0))
    make_box("Street_Far_Sidewalk", (0.0, -19.0, -0.04), (160.0, 6.0, 0.08), (0.70, 0.68, 0.64, 1.0))
    r = _rng(808)
    for k in range(6):
        px = -22.0 + k * 9.0
        make_taper_cyl(f"Street_Palm_{k}_Trunk", (px, -5.0, 4.5), 0.18, 0.12, 9.0, (0.52, 0.44, 0.34, 1.0), segments=8)
        for f in range(7):
            a = f * math.tau / 7.0 + r()
            make_blob(f"Street_Palm_{k}_Frond_{f}", (px + math.cos(a) * 1.2, -5.0 + math.sin(a) * 1.2, 8.9),
                      0.9, (0.26, 0.48, 0.24, 1.0), noise=0.25, seed=40 + k * 7 + f, squash=0.30)
    # the towers across the street (draft 2, 2026-10-30): 1970s-2000s
    # downtown curtain walls, not slabs with stripes. Each has glass between
    # aluminium mullions every 1.5 m, a spandrel at every 3.6 m floor, and a
    # lit storefront storey on the sidewalk. Built big: 22-30 m wide, 60-130 m tall.
    tx = -44.0
    for k in range(5):
        tw = 22.0 + r() * 8.0
        h = 60.0 + r() * 70.0
        bx = tx + tw / 2.0
        tx += tw + 4.0
        glass, spand = (((0.30, 0.40, 0.46, 1.0), (0.82, 0.80, 0.74, 1.0)), ((0.22, 0.30, 0.34, 1.0), (0.56, 0.58, 0.58, 1.0)),
                        ((0.40, 0.48, 0.50, 1.0), (0.90, 0.88, 0.84, 1.0)))[k % 3]
        make_box(f"Tower_Across_{k}", (bx, -34.0, h / 2.0), (tw, 24.0, h), glass)
        fy = -21.97
        for f in range(1, int(h / 3.6)):
            make_box(f"Tower_Across_{k}_Spandrel_Stock_{f}", (bx, fy - 0.03, 4.6 + (f - 1) * 3.6), (tw, 0.10, 1.0), spand)
        for i in range(int(tw / 1.5) + 1):
            make_box(f"Tower_Across_{k}_Mullion_Stock_{i}", (bx - tw / 2.0 + 0.06 + i * (tw - 0.12) / int(tw / 1.5), fy + 0.05, h / 2.0 + 2.0),
                     (0.12, 0.14, h - 4.0), (0.68, 0.70, 0.72, 1.0))
        make_box(f"Tower_Across_{k}_Storefront", (bx, fy + 0.0, 2.0), (tw - 1.0, 0.06, 3.2), (0.96, 0.92, 0.78, 1.0))
        make_box(f"Tower_Across_{k}_Canopy", (bx, fy + 1.18, 3.85), (tw, 2.4, 0.25), (0.30, 0.30, 0.32, 1.0))
    for k, (cx, col) in enumerate(((-12.0, (0.86, 0.86, 0.84, 1.0)), (6.0, (0.60, 0.12, 0.14, 1.0)))):
        make_box(f"Street_Car_{k}_Body", (cx, -9.0 if k == 0 else -13.0, 0.62), (4.4, 1.75, 0.75), col)
        make_box(f"Street_Car_{k}_Cabin", (cx - 0.2, -9.0 if k == 0 else -13.0, 1.22), (2.4, 1.6, 0.5), (0.30, 0.36, 0.40, 1.0))


SHOP_D = 5.8      # the shops run 5.8 m back from the lobby wall (were 2 m boxes)


def _shopfront(name, wall_x, y0, y1, sign_col, inside_col, room_sign, floor_col=(0.56, 0.52, 0.48, 1.0)):
    """A glass shopfront in the lobby's side wall: the sign band, the glass,
    and behind it a real shop, SHOP_D deep, with its own floor, walls,
    ceiling and troffers. (Draft 2, 2026-10-30: the shops were 2 m boxes
    with one colour on the back, so each read as a painted panel.)
    room_sign -1 runs the shop east (+x), +1 west."""
    yc, w = (y0 + y1) / 2.0, y1 - y0
    make_box(f"{name}_Sign", (wall_x + room_sign * 0.05, yc, 3.2), (0.10, w - 0.2, 0.6), sign_col)
    make_box(f"{name}_Glass", (wall_x, yc, 1.4), (0.02, w - 0.2, 2.6), GLASS)
    make_box(f"{name}_Frame_T", (wall_x, yc, 2.75), (0.08, w, 0.10), DARK)
    for s in (-1, 1):
        make_box(f"{name}_Frame_{s:+d}", (wall_x, yc + s * (w / 2.0 - 0.05), 1.4), (0.08, 0.10, 2.8), DARK)
    x0 = wall_x - room_sign * 0.2                    # the lobby wall's far face
    back = wall_x - room_sign * (0.2 + SHOP_D)
    xm, dl = (x0 + back) / 2.0, SHOP_D
    make_box(f"{name}_Wall_Back", (back - room_sign * 0.05, yc, 1.55), (0.10, w + 0.16, 3.1), inside_col)
    make_box(f"{name}_Floor", (xm, yc, 0.01), (dl, w, 0.02), floor_col)
    make_box(f"{name}_Ceiling", (xm, yc, 3.05), (dl, w + 0.16, 0.10), (0.94, 0.94, 0.92, 1.0))
    for s in (-1, 1):
        make_box(f"{name}_Wall_{s:+d}", (xm, yc + s * (w / 2.0 + 0.04), 1.5), (dl, 0.08, 3.0), inside_col)
    for k in range(2):
        make_box(f"{name}_Troffer_{k}", (x0 - room_sign * (1.6 + k * 2.6), yc, 2.985), (1.2, 0.6, 0.03), (0.98, 1.0, 1.0, 1.0))
    return x0, back, yc, w


def build_shops():
    """West: the photography parlour and the travel agency. East: the suit
    and leather case store, the game store's front, the dry cleaner. Each
    is a room you see into from the lobby."""
    r = _rng(4242)
    make_wall_with_openings("Lobby_Wall_W", (-9.1, 8.0, 0.0), length=16.0, axis='Y', height=LH, thickness=0.20,
                            openings=[(5.0, 1.4, 3.8, 2.8), (10.5, 1.4, 4.4, 2.8)], palette={"wall": WALL})
    # "tourist trap photography parlour": a painted beach backdrop, the studio
    # lights on stands, the camera on its tripod, the grass skirts and leis
    # on a rack, a surfboard, sample prints in frames down the walls
    x0, back, yc, w = _shopfront("Photo_Parlour", -9.0, 3.1, 6.9, (0.94, 0.80, 0.26, 1.0), (0.86, 0.80, 0.68, 1.0), +1,
                                 floor_col=(0.62, 0.52, 0.40, 1.0))
    make_box("Photo_Parlour_Backdrop", (back + 0.06, yc, 1.45), (0.02, 3.4, 2.6), (0.98, 0.70, 0.44, 1.0))
    make_box("Photo_Parlour_Backdrop_Sea", (back + 0.075, yc, 0.95), (0.01, 3.4, 0.9), (0.18, 0.52, 0.66, 1.0))
    make_box("Photo_Parlour_Backdrop_Sun", (back + 0.08, yc + 0.6, 1.75), (0.01, 0.7, 0.7), (1.0, 0.90, 0.50, 1.0))
    make_box("Photo_Parlour_Backdrop_Sand", (back + 0.5, yc, 0.04), (0.9, 3.4, 0.06), (0.90, 0.80, 0.58, 1.0))
    make_box("Photo_Parlour_Stool_Seat", (back + 1.1, yc, 0.46), (0.40, 0.40, 0.06), (0.46, 0.30, 0.18, 1.0))
    make_box("Photo_Parlour_Stool_Leg", (back + 1.1, yc, 0.22), (0.08, 0.08, 0.42), (0.30, 0.22, 0.16, 1.0))
    for s in (-1, 1):
        lx, ly = back + 2.6, yc + s * 1.2
        make_cyl(f"Photo_Parlour_Light_{s:+d}_Stand", (lx, ly, 0.9), 0.02, 1.8, DARK, segments=6)
        make_box(f"Photo_Parlour_Light_{s:+d}_Foot", (lx, ly, 0.02), (0.5, 0.5, 0.04), DARK)
        make_box(f"Photo_Parlour_Light_{s:+d}_Softbox", (lx, ly, 1.95), (0.30, 0.6, 0.6), (0.98, 0.98, 0.96, 1.0))
    make_cyl("Photo_Parlour_Tripod", (back + 4.0, yc, 0.65), 0.025, 1.3, DARK, segments=6)
    make_box("Photo_Parlour_Tripod_Foot", (back + 4.0, yc, 0.02), (0.6, 0.6, 0.04), DARK)
    make_box("Photo_Parlour_Camera", (back + 4.0, yc, 1.38), (0.16, 0.22, 0.16), (0.16, 0.16, 0.18, 1.0))
    make_box("Photo_Parlour_Grass_Skirt_Rack", (x0 - 0.5, yc + 1.4, 0.8), (0.5, 0.5, 1.6), (0.70, 0.62, 0.36, 1.0))
    for k in range(5):
        make_cyl(f"Photo_Parlour_Lei_{k}", (x0 - 0.5, yc + 1.4 - 0.2 + k * 0.1, 1.62), 0.11, 0.03,
                 ((0.96, 0.40, 0.56, 1.0), (0.98, 0.84, 0.30, 1.0), (0.96, 0.96, 0.92, 1.0), (0.80, 0.30, 0.70, 1.0), (0.98, 0.56, 0.26, 1.0))[k], segments=10)
    make_box("Photo_Parlour_Surfboard", (x0 - 1.2, yc - w / 2.0 + 0.04, 1.12), (0.50, 0.08, 2.2), (0.20, 0.70, 0.76, 1.0))
    for s in (-1, 1):
        for k in range(4):
            make_box(f"Photo_Parlour_Print_{s:+d}_{k}", (x0 - 1.9 - k * 0.95, yc + s * (w / 2.0 - 0.015), 1.75), (0.6, 0.03, 0.8),
                     (0.30 + r() * 0.5, 0.50 + r() * 0.3, 0.60 + r() * 0.3, 1.0))
    # "travel agency": two desks with their beige PCs, the chairs, the island
    # posters, the brochure rack by the door, a globe
    x0, back, yc, w = _shopfront("Travel_Agency", -9.0, 8.3, 12.7, (0.20, 0.50, 0.70, 1.0), (0.86, 0.86, 0.82, 1.0), +1,
                                 floor_col=(0.36, 0.44, 0.50, 1.0))
    for k, dy in enumerate((-1.0, 1.0)):
        dx = back + 1.4
        make_box(f"Travel_Agency_Desk_{k}", (dx, yc + dy, 0.38), (0.8, 1.5, 0.76), (0.50, 0.38, 0.26, 1.0))
        make_box(f"Travel_Agency_Desk_{k}_Top", (dx, yc + dy, 0.775), (0.84, 1.56, 0.03), (0.36, 0.28, 0.20, 1.0))
        make_box(f"Travel_Agency_Desk_{k}_PC", (dx - 0.1, yc + dy + 0.3, 0.98), (0.38, 0.38, 0.38), (0.84, 0.82, 0.74, 1.0))
        make_box(f"Travel_Agency_Desk_{k}_Screen", (dx + 0.095, yc + dy + 0.3, 1.0), (0.01, 0.28, 0.22), (0.30, 0.46, 0.60, 1.0))
        make_box(f"Travel_Agency_Desk_{k}_Keyboard", (dx + 0.25, yc + dy + 0.1, 0.80), (0.16, 0.42, 0.02), (0.84, 0.82, 0.74, 1.0))
        make_stool(f"Travel_Agency_Chair_{k}", dx + 1.0, yc + dy, h=0.48)
        make_stool(f"Travel_Agency_Agent_Chair_{k}", back + 0.55, yc + dy, h=0.48)
    for s in (-1, 1):
        for k in range(3):
            make_box(f"Travel_Agency_Poster_{s:+d}_{k}", (x0 - 1.2 - k * 1.5, yc + s * (w / 2.0 - 0.015), 1.75), (0.8, 0.03, 1.1),
                     (0.16 + r() * 0.2, 0.52 + r() * 0.3, 0.70 + r() * 0.2, 1.0))
    make_box("Travel_Agency_Poster_Back", (back + 0.015, yc, 1.9), (0.03, 1.6, 1.0), (0.96, 0.66, 0.30, 1.0))
    make_box("Travel_Agency_Brochure_Rack", (x0 - 0.35, yc + 1.8, 0.8), (0.3, 0.5, 1.6), (0.80, 0.80, 0.82, 1.0))
    make_cyl("Travel_Agency_Globe_Stand", (back + 0.4, yc - 1.95, 0.45), 0.03, 0.9, BRASS, segments=8)
    make_blob("Travel_Agency_Globe", (back + 0.4, yc - 1.95, 1.05), 0.2, (0.30, 0.50, 0.66, 1.0), noise=0.0, seed=3)
    # east wall: cut for the suit shop, the game store's front, the dry cleaner
    make_wall_with_openings("Lobby_Wall_E", (9.1, 8.0, 0.0), length=16.0, axis='Y', height=LH, thickness=0.20,
                            openings=[(3.7, 1.4, 3.2, 2.8), (8.0, 1.5, 4.4, 3.0), (12.3, 1.4, 3.2, 2.8)],
                            palette={"wall": WALL})
    # "a men's suit and leather case store": suits down both walls, the
    # shirt table, the three-way mirror, the luggage wall at the back
    x0, back, yc, w = _shopfront("Suit_Shop", 9.0, 2.1, 5.3, (0.16, 0.16, 0.20, 1.0), (0.66, 0.60, 0.52, 1.0), -1,
                                 floor_col=(0.30, 0.20, 0.16, 1.0))
    for k in range(3):
        make_box(f"Suit_Shop_Suit_{k}", (10.3, 2.8 + k * 0.9, 1.3), (0.30, 0.50, 1.1), (0.18 + k * 0.05, 0.18, 0.22, 1.0))
    make_box("Suit_Shop_Rail", (10.3, 3.7, 1.88), (0.04, 3.2, 0.04), (0.70, 0.70, 0.72, 1.0))  # the suits hang from it
    for s in (-1, 1):
        ry = yc + s * (w / 2.0 - 0.32)
        make_box(f"Suit_Shop_Wall_Rail_{s:+d}", (12.6, ry, 1.75), (3.6, 0.04, 0.04), (0.70, 0.70, 0.72, 1.0))
        for b in (-1, 1):
            make_box(f"Suit_Shop_Wall_Rail_{s:+d}_Bracket_{b:+d}", (12.6 + b * 1.7, ry + s * 0.15, 1.75), (0.04, 0.34, 0.04), (0.70, 0.70, 0.72, 1.0))
        for k in range(11):
            make_box(f"Suit_Shop_Hung_Stock_{s:+d}_{k}", (11.0 + k * 0.32, ry, 1.18), (0.07, 0.52, 1.10),
                     ((0.14, 0.14, 0.18, 1.0), (0.22, 0.22, 0.28, 1.0), (0.30, 0.26, 0.22, 1.0), (0.40, 0.40, 0.44, 1.0))[(k + (s > 0)) % 4])
    make_box("Suit_Shop_Table", (12.4, yc, 0.42), (1.6, 0.9, 0.84), (0.36, 0.24, 0.16, 1.0))
    for k in range(8):
        make_box(f"Suit_Shop_Shirt_Stock_{k}", (11.85 + (k % 4) * 0.37, yc - 0.2 + (k // 4) * 0.4, 0.875),
                 (0.30, 0.34, 0.07), ((0.94, 0.94, 0.96, 1.0), (0.72, 0.82, 0.94, 1.0), (0.96, 0.92, 0.84, 1.0), (0.86, 0.72, 0.76, 1.0))[k % 4])
    make_box("Suit_Shop_Tie_Case", (13.6, yc, 0.5), (0.5, 0.9, 1.0), (0.30, 0.22, 0.16, 1.0))
    make_box("Suit_Shop_Tie_Case_Glass", (13.6, yc, 1.02), (0.5, 0.9, 0.04), GLASS)
    for k in range(3):
        make_box(f"Suit_Shop_Mirror_{k}", (back - 0.02, yc - 0.55 + k * 0.55, 1.15), (0.04, 0.52, 1.9), (0.74, 0.80, 0.82, 1.0))
    for k in range(4):
        make_box(f"Suit_Shop_Luggage_Shelf_{k}", (back - 0.25, yc - 1.15, 0.3 + k * 0.6), (0.44, 0.9, 0.03), SHELF)
        make_box(f"Suit_Shop_Case_Stock_{k}", (back - 0.25, yc - 1.15, 0.47 + k * 0.6), (0.38, 0.6, 0.31),
                 ((0.42, 0.26, 0.14, 1.0), (0.20, 0.14, 0.10, 1.0), (0.30, 0.18, 0.12, 1.0), (0.56, 0.40, 0.24, 1.0))[k])
    make_box("Suit_Shop_Luggage_Shelf_Upright", (back - 0.25, yc - 1.15 - 0.47, 1.1), (0.44, 0.04, 2.2), SHELF)
    make_box("Suit_Shop_Luggage", (9.7, 4.6, 0.35), (0.5, 0.7, 0.7), (0.42, 0.26, 0.14, 1.0))
    make_box("Suit_Shop_Briefcase", (9.7, 4.6, 0.82), (0.45, 0.10, 0.34), (0.30, 0.18, 0.10, 1.0))
    # the dry cleaner: the counter across the shop with its bell and ticket
    # spike, and behind it the garment conveyor, the bags looping to the back
    x0, back, yc, w = _shopfront("Dry_Cleaner", 9.0, 10.7, 13.9, (0.86, 0.90, 0.94, 1.0), (0.86, 0.88, 0.90, 1.0), -1,
                                 floor_col=(0.74, 0.74, 0.72, 1.0))
    make_box("Dry_Cleaner_Counter", (11.1, yc - 0.35, 0.52), (0.6, 2.5, 1.04), (0.52, 0.56, 0.60, 1.0))
    make_box("Dry_Cleaner_Counter_Top", (11.1, yc - 0.35, 1.055), (0.66, 2.56, 0.03), (0.86, 0.84, 0.80, 1.0))
    make_cyl("Dry_Cleaner_Bell", (11.0, yc - 1.2, 1.10), 0.05, 0.06, BRASS, segments=10)
    make_cyl("Dry_Cleaner_Ticket_Spike", (11.0, yc + 0.4, 1.13), 0.01, 0.12, DARK, segments=6)
    make_box("Dry_Cleaner_Ticket_Pad", (11.1, yc, 1.075), (0.14, 0.20, 0.01), (0.96, 0.74, 0.70, 1.0))
    # the conveyor: an oval rail at 2.2 m on hangers from the ceiling, the
    # bagged clothes hanging all the way round it
    cx0, cx1 = 12.0, back - 0.5
    for s in (-1, 1):
        make_box(f"Dry_Cleaner_Conveyor_{s:+d}", ((cx0 + cx1) / 2.0, yc + s * 0.7, 2.25), (cx1 - cx0, 0.05, 0.05), (0.70, 0.70, 0.72, 1.0))
        make_box(f"Dry_Cleaner_Conveyor_End_{s:+d}", (cx0 if s < 0 else cx1, yc, 2.25), (0.05, 1.45, 0.05), (0.70, 0.70, 0.72, 1.0))
        for k in range(3):
            make_box(f"Dry_Cleaner_Conveyor_Hanger_{s:+d}_{k}", (cx0 + 0.2 + k * (cx1 - cx0 - 0.4) / 2.0, yc + s * 0.7, 2.65),
                     (0.03, 0.03, 0.75), (0.60, 0.60, 0.62, 1.0))
        n = int((cx1 - cx0) / 0.17)
        for k in range(n):
            make_box(f"Dry_Cleaner_Bag_Stock_{s:+d}_{k}", (cx0 + 0.1 + k * 0.17, yc + s * 0.7, 1.67), (0.06, 0.50, 1.12),
                     (0.92, 0.92, 0.94, 1.0) if k % 5 else (0.84, 0.88, 0.94, 1.0))
            make_box(f"Dry_Cleaner_Bag_Stock_{s:+d}_{k}_Hem", (cx0 + 0.1 + k * 0.17, yc + s * 0.7, 1.16), (0.05, 0.42, 0.10),
                     ((0.20, 0.22, 0.30, 1.0), (0.46, 0.20, 0.18, 1.0), (0.24, 0.24, 0.24, 1.0))[(k * 7 + (s > 0)) % 3])
    make_box("Dry_Cleaner_Press", (back - 0.6, yc - w / 2.0 + 0.5, 0.5), (0.9, 0.6, 1.0), (0.80, 0.80, 0.78, 1.0))
    make_box("Dry_Cleaner_Press_Head", (back - 0.6, yc - w / 2.0 + 0.5, 1.12), (0.8, 0.5, 0.20), (0.62, 0.64, 0.66, 1.0))


def build_store():
    """The game store: its lit box sign over the front, the window
    display, walls of old big-box PC games, the glass case under the
    register with WHAT LIES BEYOND in it, the card imprinter."""
    # the front on the lobby's east wall (x 9): display window, door, window
    make_box("Game_Store_Sign", (8.86, 8.0, 3.3), (0.16, 3.8, 0.6), SIGN_LIT)
    make_box("Game_Store_Sign_Letters", (8.77, 8.0, 3.3), (0.01, 3.2, 0.32), (0.86, 0.16, 0.14, 1.0))
    make_box("Game_Store_Sign_Box", (8.97, 8.0, 3.3), (0.06, 3.9, 0.7), (0.24, 0.24, 0.26, 1.0))
    make_box("Game_Store_Window_Glass", (9.0, 6.7, 1.45), (0.02, 1.8, 2.3), GLASS)
    make_box("Game_Store_Window_2_Glass", (9.0, 9.55, 1.45), (0.02, 1.2, 2.3), GLASS)
    make_box("Game_Store_Door_Glass", (9.0, 8.4, 1.20), (0.02, 1.0, 2.4), GLASS)
    make_box("Game_Store_Door_Frame", (9.0, 8.4, 2.45), (0.08, 1.1, 0.10), DARK)
    make_box("Game_Store_Door_Pull", (8.97, 8.0, 1.1), (0.04, 0.04, 0.4), BRASS)
    make_box("Game_Store_Door_Hours", (8.98, 8.7, 1.5), (0.01, 0.24, 0.30), (0.96, 0.96, 0.94, 1.0))
    # the room
    make_box("Game_Store_Carpet", ((SX0 + SX1) / 2, (SY0 + SY1) / 2, 0.01), (SX1 - SX0, SY1 - SY0, 0.02), CARPET)
    make_box("Game_Store_Ceiling", ((SX0 + SX1) / 2, (SY0 + SY1) / 2, SH + 0.05), (SX1 - SX0, SY1 - SY0, 0.10), (0.92, 0.92, 0.90, 1.0))
    for k in range(3):
        for j in range(2):
            make_box(f"Game_Store_Troffer_{k}_{j}", (10.2 + k * 1.8, 7.0 + j * 2.0, SH - 0.02), (1.2, 0.6, 0.03), (0.98, 1.0, 1.0, 1.0))
    make_wall("Game_Store_Wall_S", ((SX0 + SX1) / 2, SY0 - 0.1, 0.0), length=SX1 - SX0, height=SH, axis='X',
              palette={"wall": (0.84, 0.84, 0.86, 1.0)})
    make_wall("Game_Store_Wall_N", ((SX0 + SX1) / 2, SY1 + 0.1, 0.0), length=SX1 - SX0, height=SH, axis='X',
              palette={"wall": (0.84, 0.84, 0.86, 1.0)})
    make_wall("Game_Store_Wall_E", (SX1 + 0.1, (SY0 + SY1) / 2, 0.0), length=SY1 - SY0, height=SH, axis='Y',
              palette={"wall": (0.84, 0.84, 0.86, 1.0)})
    # the window display: a stepped riser inside the front window, Final Cut on top
    for k in range(3):
        make_box(f"Window_Display_Riser_{k}", (9.45 + k * 0.30, 6.7, 0.20 + k * 0.20), (0.30, 1.6, 0.40 + k * 0.40), (0.62, 0.66, 0.76, 1.0))
    make_box("Window_Display_Final_Cut", (10.05, 6.7, 1.37), (0.08, 0.26, 0.34), (0.82, 0.30, 0.16, 1.0))
    r = _rng(2002)
    for k in range(6):
        make_box(f"Window_Display_Game_{k}", (9.45 + (k % 3) * 0.30, 6.2 + (k // 3) * 0.9, 0.555 + (k % 3) * 0.40),  # on each step
                 (0.07, 0.24, 0.31), (0.2 + r() * 0.7, 0.2 + r() * 0.6, 0.2 + r() * 0.7, 1.0))
    # shelving down both side walls and across the back: rows of big boxes
    def shelves(prefix, x0, x1, y, face):
        n = int((x1 - x0) / 1.0)
        for u in range(n):
            ux = x0 + 0.5 + u * 1.0
            make_box(f"{prefix}_{u}_Upright", (ux - 0.48, y, 1.1), (0.04, 0.40, 2.2), SHELF)
            for s in range(5):
                sz = 0.25 + s * 0.42
                make_box(f"{prefix}_{u}_Shelf_{s}", (ux, y, sz), (0.96, 0.40, 0.03), SHELF)
                for b in range(6):
                    make_box(f"{prefix}_{u}_Game_Stock_{s}_{b}", (ux - 0.38 + b * 0.15, y + face * 0.05, sz + 0.17),
                             (0.07, 0.24, 0.31), (0.15 + r() * 0.8, 0.15 + r() * 0.7, 0.15 + r() * 0.8, 1.0))
    shelves("Shelf_N", 10.4, 15.0, SY1 - 0.22, -1)
    shelves("Shelf_S", 11.2, 15.0, SY0 + 0.22, +1)
    for u in range(4):
        uy = SY0 + 0.6 + u * 1.0
        make_box(f"Shelf_E_{u}_Upright", (SX1 - 0.22, uy, 1.1), (0.40, 0.04, 2.2), SHELF)
        for s in range(5):
            make_box(f"Shelf_E_{u}_Shelf_{s}", (SX1 - 0.22, uy + 0.5, 0.25 + s * 0.42), (0.40, 0.96, 0.03), SHELF)
            for b in range(6):
                make_box(f"Shelf_E_{u}_Game_Stock_{s}_{b}", (SX1 - 0.27, uy + 0.12 + b * 0.15, 0.42 + s * 0.42),
                         (0.24, 0.07, 0.31), (0.15 + r() * 0.8, 0.15 + r() * 0.7, 0.15 + r() * 0.8, 1.0))
    # the used-games bin in the middle of the floor
    make_box("Used_Bin", (11.8, 9.0, 0.45), (1.2, 0.7, 0.9), (0.40, 0.30, 0.22, 1.0))
    for k in range(10):
        make_box(f"Used_Bin_Game_Stock_{k}", (11.3 + (k % 5) * 0.24, 8.8 + (k // 5) * 0.36, 0.98),
                 (0.07, 0.24, 0.31), (0.3 + r() * 0.5, 0.3 + r() * 0.4, 0.3 + r() * 0.5, 1.0))
    make_box("Used_Bin_Card", (11.8, 8.64, 0.85), (0.40, 0.01, 0.20), (0.96, 0.92, 0.40, 1.0))
    # the counter: a glass display case under the register
    cx, cy = 13.2, 6.7
    make_box("Display_Case_Base", (cx, cy, 0.18), (2.2, 0.62, 0.36), (0.20, 0.20, 0.22, 1.0))
    make_box("Display_Case_Glass_Front", (cx, cy - 0.30, 0.66), (2.2, 0.02, 0.60), GLASS)
    make_box("Display_Case_Glass_Top", (cx, cy, 0.97), (2.2, 0.62, 0.02), GLASS)
    make_box("Display_Case_Shelf", (cx, cy, 0.62), (2.17, 0.55, 0.02), (0.86, 0.86, 0.84, 1.0))
    for s in (-1, 1):
        make_box(f"Display_Case_End_{s:+d}", (cx + s * 1.1, cy, 0.66), (0.03, 0.62, 0.62), (0.70, 0.70, 0.72, 1.0))
    # WHAT LIES BEYOND: the one box face-up in the case, regal cloudy blue
    make_box("What_Lies_Beyond", (cx - 0.3, cy - 0.05, 0.66), (0.24, 0.31, 0.06), (0.30, 0.46, 0.74, 1.0))
    for k in range(4):
        make_box(f"Display_Case_Collectible_{k}", (cx + 0.2 + k * 0.22, cy, 0.68), (0.16, 0.20, 0.10),
                 (0.5 + r() * 0.4, 0.4 + r() * 0.3, 0.3 + r() * 0.3, 1.0))
    # the register on the counter, the imprinter beside it
    make_box("Register_Body", (cx + 0.5, cy + 0.05, 1.10), (0.42, 0.40, 0.24), (0.80, 0.78, 0.72, 1.0))
    make_box("Register_Keys", (cx + 0.5, cy - 0.10, 1.23), (0.36, 0.16, 0.03), (0.30, 0.30, 0.32, 1.0))
    make_box("Register_Display", (cx + 0.5, cy + 0.20, 1.28), (0.24, 0.06, 0.12), (0.20, 0.30, 0.24, 1.0))
    make_box("Register_Drawer", (cx + 0.5, cy + 0.05, 0.99), (0.40, 0.38, 0.04), (0.66, 0.64, 0.58, 1.0))
    make_box("Imprinter_Base", (cx - 0.25, cy + 0.05, 1.00), (0.34, 0.20, 0.04), (0.20, 0.20, 0.22, 1.0))
    make_box("Imprinter_Slider", (cx - 0.25, cy + 0.05, 1.05), (0.10, 0.22, 0.05), (0.62, 0.62, 0.64, 1.0))
    make_box("Imprinter_Slip", (cx - 0.25, cy + 0.05, 1.025), (0.30, 0.16, 0.004), (0.96, 0.94, 0.86, 1.0))
    make_box("Counter_Receipt_Pad", (cx + 0.05, cy + 0.15, 0.99), (0.12, 0.18, 0.02), (0.94, 0.92, 0.84, 1.0))
    # the clerk's stool behind the counter, his coffee
    make_stool("Clerk_Stool", cx + 0.2, cy + 0.8, h=0.75)
    make_cyl("Clerk_Coffee", (cx - 0.8, cy + 0.15, 1.04), 0.04, 0.10, (0.94, 0.94, 0.92, 1.0), segments=10)
    # posters over the shelves
    for k in range(3):
        make_box(f"Game_Store_Poster_{k}", (10.6 + k * 1.6, SY1 - 0.02, 2.55), (1.0, 0.02, 0.62),
                 (0.3 + k * 0.2, 0.3, 0.6 - k * 0.1, 1.0))


def main():
    clear_scene()
    build_lobby()
    build_street_front()
    build_shops()
    build_store()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/honolulu_highrise.glb"))
    print(f"\n[build_honolulu_highrise] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
