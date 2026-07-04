"""THE MISSING LINK — Aud's diner — vol7 hero locale (Smolvud, OR).

Aud's counter-and-booths diner. Aud is seventy-three, came up from
Coos Bay and bought the diner in '46, has run it thirty years. She
knows the town by name and takes the local tokens at face value.
This is the 90s operator-noir register the build_daily_grind_interior
script names as its foil — formica counter, chrome-and-red-vinyl
stools, checkerboard vinyl, a drop ceiling of humming fluorescents —
NOT the Grind's warm 2025 PNW coffee bar.

CANON — the binding scenes (grep godot/resources/scenes for
"3d:missing_link_interior" → vol7_ch9_evening + vol7_ch16_aud). NOTE:
_ART_MANIFEST loosely calls this "Aud's bar," but the binding PROSE is
unambiguous and overrides: "The diner was Saturday-busy" / "I keep
Saturday morning's diner crew tight" / "I bought the diner" / "I've
been at this diner thirty [years]." It is a diner. It is ALSO a
different Missing Link from vol1's bus-depot diner (vol1_diner_ambient,
"no clock", the vol1_link_jukebox scenes) — do NOT borrow vol1
dressing (no jukebox here; vol7 prose never names one).

Prop list pulled straight from the two scenes:
  · vol7_ch16_aud (Saturday NOON): "The diner was Saturday-busy. The
    booths along the front window were full. The back booth was
    occupied by [Frog Petersen + Bernie Lund]." Kai "sat at the
    counter on the THIRD stool." Aud "came over with the coffee" and
    "went back behind the counter." The leek soup (Aud cut the leeks
    at five before the first customer), the SALMONBERRY PIE Aud kept
    a slice of in the cooler since Tuesday, a second cup of coffee at
    twelve forty-five.
  · vol7_ch9_evening (Tuesday EVENING, rain): "Aud was at the
    counter." She "seated them in the BOOTH AT THE BACK... the booth
    she gave the kids on Tuesday nights," brought coffee without
    asking, brought MENUS. Meatloaf, fish and chips, the salmonberry
    pie "fresh today." Kai "paid in TOKENS. The Missing Link did not,
    by Aud's specific arrangement, refuse the local tokens." They
    "went out into the RAIN at seven-forty-six."

CANON-NEGATIVES (absences are props too, per the 2026-07-02 lesson):
  · No jukebox — that is the vol1 Missing Link, not this one.
  · No liquor bar / taps / bottle wall — it is a diner, not a tavern,
    despite the manifest's loose "bar" label.
  · No espresso machine / pour-over / pastry case — that vocabulary
    is the Daily Grind's, explicitly contrasted against here.
  · No snack aisle / vending machine / endcaps (the auto-scaffold
    imported those Kwik-Stop fixtures — dropped).

No transparency: the front windows are REAL OPENINGS with painted
frames + mullions (no glass); the wet street and sidewalk live
outside them for the rain register. Text (the diner sign, OPEN sign,
the specials board, menus) is scene-side Label3D per the playbook;
this script bakes named vertex-colored panels:
  MissingLink_SignBoard, OpenSign_Board, SpecialsBoard, Menu_*.

Shell footprint kept from the scaffold (the .tscn camera + the three
directional lights are tuned to this 6 x 5 room, CEIL 2.6, entrance
door gap x -1..+1 in the south/street wall).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.food_service import make_coffee_pots, make_sugar_creamer_caddy
from _props.decor import (make_wall_clock, make_floor_plant, make_faded_poster,
                          make_calendar, make_payphone, make_fire_extinguisher)
from _props.safety import (make_smoke_detector, make_hvac_vent,
                           make_fluorescent_tube_fixture)

# ── Shell (footprint kept — do NOT retune, the .tscn is tuned to it) ─
ROOM_W = 6.0; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall": (0.80, 0.77, 0.68, 1.0),      # warm diner cream
            "baseboard": (0.30, 0.24, 0.18, 1.0)}

# ── Diner palette (90s operator-noir, warm-sunset muted saturation) ─
COL_FLOOR_LT  = (0.86, 0.82, 0.72, 1.0)   # checkerboard cream tile
COL_FLOOR_DK  = (0.30, 0.40, 0.38, 1.0)   # muted teal tile (not clown red)
COL_FLOOR_SEAM= (0.60, 0.55, 0.46, 1.0)
COL_FORMICA   = (0.74, 0.64, 0.42, 1.0)   # counter body laminate
COL_FORM_TOP  = (0.80, 0.74, 0.60, 1.0)   # boomerang counter/table top
COL_FORM_EDGE = (0.24, 0.20, 0.16, 1.0)   # dark counter edge band
COL_WOOD      = (0.42, 0.32, 0.22, 1.0)
COL_WOOD_DARK = (0.26, 0.20, 0.14, 1.0)
COL_VINYL_RED = (0.60, 0.26, 0.22, 1.0)   # booth + stool vinyl (muted)
COL_VINYL_DK  = (0.42, 0.18, 0.16, 1.0)
COL_CHROME    = P.METAL_STEEL
COL_STEEL     = P.METAL_STEEL
COL_BLACK     = P.METAL_BLACK
COL_CREAM     = (0.92, 0.90, 0.84, 1.0)
COL_GLASSISH  = (0.72, 0.78, 0.78, 1.0)   # opaque stand-in for glass
COL_COFFEE    = (0.20, 0.12, 0.08, 1.0)
COL_PIE_CRUST = (0.80, 0.62, 0.36, 1.0)   # salmonberry pie crust
COL_PIE_FILL  = (0.56, 0.22, 0.30, 1.0)   # salmonberry filling
COL_SOUP      = (0.86, 0.82, 0.62, 1.0)   # leek-and-cream
COL_KETCHUP   = (0.60, 0.16, 0.14, 1.0)
COL_MUSTARD   = (0.82, 0.66, 0.20, 1.0)
COL_HEATLAMP  = (0.98, 0.72, 0.34, 1.0)   # pass heat-lamp glow
COL_MENU      = P.PAPER
COL_SLATE     = (0.15, 0.16, 0.15, 1.0)   # specials chalkboard
COL_PLATE     = (0.90, 0.88, 0.82, 1.0)
COL_MEATLOAF  = (0.42, 0.26, 0.18, 1.0)
COL_FISH      = (0.82, 0.66, 0.40, 1.0)   # battered fish / fries
COL_CONCRETE  = (0.55, 0.54, 0.51, 1.0)
COL_ASPHALT   = (0.15, 0.15, 0.16, 1.0)   # rain-dark street (ch9)
COL_PUDDLE    = (0.30, 0.33, 0.36, 1.0)
COL_TOKEN     = (0.70, 0.58, 0.34, 1.0)   # Smolvud's local tokens

# Front windows: real openings, sill 0.75, head 2.30, no glass.
SILL_Z = 0.75; HEAD_Z = 2.30
WIN_H = HEAD_Z - SILL_Z


# ═════════════════════════════════════════════════════════════════
# Local furniture helpers (deterministic, index-cycled — no random)
# ═════════════════════════════════════════════════════════════════
def _checker_floor():
    """Cream/teal checkerboard laid over the vinyl slab (diner tell)."""
    tile = 0.58
    for i in range(-5, 6):          # x centres -2.90 .. +2.90
        for j in range(0, 9):       # y centres  0.29 .. +4.93
            if (i + j) % 2 != 0:
                continue
            cx = i * tile
            cy = 0.29 + j * tile
            if abs(cx) > 2.95 or cy > 4.9:
                continue
            make_box(f"FloorTile_{i}_{j}", (cx, cy, 0.008),
                     (tile - 0.03, tile - 0.03, 0.004), COL_FLOOR_DK)


def _stool(prefix, cx, cy):
    """Chrome-pedestal diner counter stool, red vinyl seat (~0.72 top)."""
    make_cyl(f"{prefix}_Seat", (cx, cy, 0.72), 0.17, 0.05, COL_VINYL_RED, segments=12)
    make_cyl(f"{prefix}_SeatRim", (cx, cy, 0.695), 0.175, 0.02, COL_CHROME, segments=12)
    make_cyl(f"{prefix}_Column", (cx, cy, 0.35), 0.045, 0.70, COL_CHROME, segments=12)
    make_cyl(f"{prefix}_Base", (cx, cy, 0.03), 0.20, 0.05, COL_CHROME, segments=12)
    # simple chrome foot-ring approximated by four short rungs
    for ri, (rx, ry, rsz) in enumerate([
            (0.0, -0.16, (0.30, 0.02, 0.02)), (0.0, +0.16, (0.30, 0.02, 0.02)),
            (-0.16, 0.0, (0.02, 0.30, 0.02)), (+0.16, 0.0, (0.02, 0.30, 0.02))]):
        make_box(f"{prefix}_FootRung_{ri}", (cx + rx, cy + ry, 0.24), rsz, COL_CHROME)


def _cup_saucer(prefix, cx, cy, bz, filled=True):
    make_cyl(f"{prefix}_Saucer", (cx, cy, bz + 0.006), 0.058, 0.012, COL_CREAM, segments=12)
    make_cyl(f"{prefix}_Cup", (cx, cy, bz + 0.045), 0.036, 0.065, COL_CREAM, segments=12)
    make_box(f"{prefix}_Handle", (cx + 0.045, cy, bz + 0.045), (0.014, 0.012, 0.04), COL_CREAM)
    if filled:
        make_cyl(f"{prefix}_Coffee", (cx, cy, bz + 0.072), 0.030, 0.006, COL_COFFEE, segments=12)


def _napkin_dispenser(prefix, cx, cy, bz):
    make_box(f"{prefix}_Body", (cx, cy, bz + 0.075), (0.10, 0.13, 0.15), COL_CHROME)
    make_box(f"{prefix}_Napkins", (cx, cy, bz + 0.075), (0.02, 0.11, 0.11), COL_CREAM)
    make_box(f"{prefix}_Top", (cx, cy, bz + 0.155), (0.11, 0.14, 0.01), COL_CHROME)


def _condiments(prefix, cx, cy, bz):
    """Ketchup + mustard squeeze bottles, salt & pepper shakers."""
    make_cyl(f"{prefix}_Ketchup", (cx - 0.05, cy, bz + 0.07), 0.028, 0.14, COL_KETCHUP, segments=10)
    make_cyl(f"{prefix}_KetchupCap", (cx - 0.05, cy, bz + 0.155), 0.016, 0.03, COL_WOOD_DARK, segments=8)
    make_cyl(f"{prefix}_Mustard", (cx + 0.05, cy, bz + 0.07), 0.028, 0.14, COL_MUSTARD, segments=10)
    make_cyl(f"{prefix}_MustardCap", (cx + 0.05, cy, bz + 0.155), 0.016, 0.03, COL_WOOD_DARK, segments=8)
    for si, (sx, scol) in enumerate([(-0.11, COL_CREAM), (+0.11, COL_WOOD_DARK)]):
        make_cyl(f"{prefix}_Shaker_{si}", (cx + sx, cy + 0.02, bz + 0.045), 0.020, 0.09, COL_GLASSISH, segments=8)
        make_cyl(f"{prefix}_ShakerTop_{si}", (cx + sx, cy + 0.02, bz + 0.095), 0.018, 0.014, COL_CHROME, segments=8)


def _pie_slice(prefix, cx, cy, bz):
    make_cyl(f"{prefix}_Plate", (cx, cy, bz + 0.008), 0.075, 0.016, COL_PLATE, segments=12)
    make_box(f"{prefix}_Crust", (cx, cy, bz + 0.035), (0.10, 0.06, 0.04), COL_PIE_CRUST)
    make_box(f"{prefix}_Fill", (cx, cy, bz + 0.033), (0.09, 0.05, 0.03), COL_PIE_FILL)


def _menu(prefix, cx, cy, bz, ang_box=(0.20, 0.30, 0.004)):
    make_box(f"{prefix}", (cx, cy, bz + 0.004), ang_box, COL_MENU)
    make_box(f"{prefix}_Band", (cx, cy, bz + 0.007), (ang_box[0] * 0.8, ang_box[1] * 0.2, 0.001),
             COL_VINYL_RED)


# A west-wall booth: two vinyl benches whose tall backs are the
# dividers, a formica table between, the table head against the
# west window. Occupants slide in from the east (aisle) side.
def _booth(prefix, bx, by, *, occupied=False, is_back=False):
    seat_z = 0.24
    back_top = 0.62
    for tag, sy in (("S", by - 0.45), ("N", by + 0.45)):
        make_box(f"{prefix}_{tag}_Seat", (bx, sy, seat_z), (1.28, 0.42, 0.12), COL_VINYL_RED)
        make_box(f"{prefix}_{tag}_SeatFace", (bx, sy - (0.21 if tag == "S" else -0.21), seat_z + 0.02),
                 (1.28, 0.02, 0.14), COL_VINYL_DK)
        # tall seat-back / divider on the outer edge
        oy = by - 0.63 if tag == "S" else by + 0.63
        make_box(f"{prefix}_{tag}_Back", (bx, oy, back_top), (1.28, 0.10, 0.85), COL_VINYL_RED)
        make_box(f"{prefix}_{tag}_BackCap", (bx, oy, 1.06), (1.30, 0.11, 0.05), COL_CHROME)
    # Table — formica top, chrome-edge, single pedestal, head at window
    make_box(f"{prefix}_TableTop", (bx, by, 0.72), (1.06, 0.56, 0.05), COL_FORM_TOP)
    make_box(f"{prefix}_TableEdge", (bx, by, 0.695), (1.09, 0.59, 0.02), COL_FORM_EDGE)
    make_cyl(f"{prefix}_TablePost", (bx, by, 0.37), 0.045, 0.70, COL_CHROME)
    make_cyl(f"{prefix}_TableFoot", (bx, by, 0.02), 0.22, 0.04, COL_CHROME, segments=12)
    # Standing condiment caddy + napkin holder at the window head (west)
    _napkin_dispenser(f"{prefix}_Napkins", bx - 0.42, by, 0.745)
    _condiments(f"{prefix}_Cond", bx - 0.14, by, 0.745)
    if occupied:
        # Frog + Bernie in the back booth; a full front booth otherwise
        _cup_saucer(f"{prefix}_CupS", bx + 0.18, by - 0.20, 0.745)
        _cup_saucer(f"{prefix}_CupN", bx + 0.22, by + 0.22, 0.745)
        if is_back:
            # Frog's leek soup (canon: "Frog likes the leek")
            make_cyl(f"{prefix}_SoupBowl", bx + 0.30, by - 0.14, 0.745 + 0.02,
                     0.075, 0.05, COL_CREAM, segments=12)
            make_cyl(f"{prefix}_Soup", (bx + 0.30, by - 0.14, 0.745 + 0.055),
                     0.062, 0.02, COL_SOUP, segments=12)
        else:
            _menu(f"{prefix}_Menu", bx + 0.20, by + 0.02, 0.745)
    else:
        _menu(f"{prefix}_Menu", bx + 0.24, by, 0.745)


# ═════════════════════════════════════════════════════════════════
# SHELL — 6 x 5 x 2.6 room (footprint kept). South (street) wall has
# the entrance (x -1..+1) + a big front window west of it (real
# openings, no glass). West wall carries the storefront window the
# booth row sits under. East + north walls solid (counter + back
# booth against them). Checkerboard vinyl, drop-tile ceiling.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_FLOOR_LT, "seam": COL_FLOOR_SEAM})
    _checker_floor()

    # ── South / street wall (y = 0): piers + door header + window
    #    sill/header. Openings: door x[-1,+1], front window x[-2.85,-1.25]
    for nm, px, pw in [("Wall_S_PierWW", -3.025, 0.35), ("Wall_S_PierWD", -1.125, 0.25),
                       ("Wall_S_PierE", 2.025, 1.95)]:
        make_box(nm, (px, 0.0, CEIL / 2.0), (pw, 0.20, CEIL), PAL_WALL["wall"])
    make_box("Wall_S_Win_Sill", (-2.05, 0.0, SILL_Z / 2.0), (1.60, 0.20, SILL_Z), PAL_WALL["wall"])
    make_box("Wall_S_Win_Base", (-2.05, 0.06, 0.08), (1.60, 0.06, 0.16), PAL_WALL["baseboard"])
    make_box("Wall_S_Win_Header", (-2.05, 0.0, (HEAD_Z + CEIL) / 2.0),
             (1.60, 0.20, CEIL - HEAD_Z), PAL_WALL["wall"])
    make_box("Wall_S_AboveDoor", (0.0, 0.0, (HEAD_Z + CEIL) / 2.0),
             (2.0, 0.20, CEIL - HEAD_Z), PAL_WALL["wall"])

    # ── West wall (x = -3.0): one long storefront window y[0.4,3.0]
    make_wall("Wall_W_S", (-ROOM_W / 2.0, 0.10, 0), length=0.60, height=CEIL, axis='Y',
              palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_W_N", (-ROOM_W / 2.0, 4.10, 0), length=2.20, height=CEIL, axis='Y',
              palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_W_Win_Sill", (-ROOM_W / 2.0, 1.70, SILL_Z / 2.0), (0.20, 2.60, SILL_Z),
             PAL_WALL["wall"])
    make_box("Wall_W_Win_Base", (-ROOM_W / 2.0 + 0.06, 1.70, 0.08), (0.06, 2.60, 0.16),
             PAL_WALL["baseboard"])
    make_box("Wall_W_Win_Header", (-ROOM_W / 2.0, 1.70, (HEAD_Z + CEIL) / 2.0),
             (0.20, 2.60, CEIL - HEAD_Z), PAL_WALL["wall"])

    # ── East + North walls (solid)
    make_wall("Wall_E", (ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)

    # ── Drop-tile ceiling (the diner's fluorescent grid rides this)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
                 palette={"tile": (0.90, 0.88, 0.80, 1.0), "grid": (0.52, 0.50, 0.44, 1.0)},
                 with_stains=True)


# ═════════════════════════════════════════════════════════════════
# STOREFRONT — painted frame + mullions in the two openings (NO
# glass per the no-transparency rule), the entrance door, the entry
# mat, coat pegs by the door (ch9: Finn's wool cap + coat come in out
# of the rain), the hanging OPEN sign + the exterior THE MISSING LINK
# board (lettering scene-side).
# ═════════════════════════════════════════════════════════════════
def _frame_south(wx):
    make_box("WinS_Sill", (wx, 0.0, SILL_Z - 0.015), (1.72, 0.22, 0.06), COL_CHROME)
    make_box("WinS_Ledge", (wx, 0.14, SILL_Z + 0.02), (1.60, 0.14, 0.03), COL_FORM_TOP)
    make_box("WinS_Head", (wx, 0.0, HEAD_Z + 0.015), (1.72, 0.22, 0.06), COL_CHROME)
    for sgn in (-1, +1):
        make_box(f"WinS_Jamb_{sgn:+d}", (wx + sgn * 0.83, 0.0, (SILL_Z + HEAD_Z) / 2.0),
                 (0.06, 0.22, WIN_H), COL_CHROME)
    make_box("WinS_MullV", (wx, 0.0, (SILL_Z + HEAD_Z) / 2.0), (0.05, 0.14, WIN_H), COL_CHROME)
    make_box("WinS_Transom", (wx, 0.0, 1.90), (1.60, 0.14, 0.05), COL_CHROME)


def _frame_west():
    cy = 1.70
    make_box("WinW_Sill", (-ROOM_W / 2.0, cy, SILL_Z - 0.015), (0.22, 2.72, 0.06), COL_CHROME)
    make_box("WinW_Ledge", (-ROOM_W / 2.0 + 0.14, cy, SILL_Z + 0.02), (0.14, 2.60, 0.03), COL_FORM_TOP)
    make_box("WinW_Head", (-ROOM_W / 2.0, cy, HEAD_Z + 0.015), (0.22, 2.72, 0.06), COL_CHROME)
    for i, my in enumerate((0.55, 1.70, 2.85)):
        make_box(f"WinW_MullV_{i}", (-ROOM_W / 2.0, my, (SILL_Z + HEAD_Z) / 2.0),
                 (0.14, 0.05, WIN_H), COL_CHROME)
    make_box("WinW_Transom", (-ROOM_W / 2.0, cy, 1.90), (0.14, 2.60, 0.05), COL_CHROME)


def build_storefront():
    _frame_south(-2.05)
    _frame_west()
    # Entrance — solid leaf, east-hinged, chrome push-bar, kick plate
    for sgn in (-1, +1):
        make_box(f"Door_Post_{sgn:+d}", (sgn * 0.98, 0.0, 1.15), (0.08, 0.18, 2.30), COL_CHROME)
    make_box("Door_Transom", (0.0, 0.0, 2.42), (2.04, 0.18, 0.14), COL_CHROME)
    make_box("Door_Leaf", (0.30, 0.02, 1.15), (1.16, 0.05, 2.24), COL_WOOD)
    make_box("Door_Window", (0.30, -0.005, 1.55), (0.80, 0.02, 1.00), COL_WOOD_DARK)  # dark inset, opaque
    make_box("Door_Rail_Mid", (0.30, -0.02, 1.02), (1.10, 0.04, 0.09), COL_WOOD_DARK)
    make_box("Door_KickPlate", (0.30, -0.02, 0.16), (1.10, 0.03, 0.28), COL_CHROME)
    make_cyl("Door_PushBar", (0.30, -0.06, 1.05), 0.020, 0.70, COL_CHROME, axis='X')
    # OPEN sign hung in the door window (lettering scene-side)
    make_cyl("OpenSign_Cord", (0.30, -0.02, 2.02), 0.004, 0.24, P.TWINE, axis='Z')
    make_box("OpenSign_Board", (0.30, -0.02, 1.80), (0.42, 0.02, 0.18), COL_VINYL_RED)
    make_box("OpenSign_TextBand", (0.30, -0.035, 1.80), (0.30, 0.006, 0.08), COL_CREAM)
    # Entry mat (ch9 rain register)
    make_box("EntryMat_Under", (0.30, 0.78, 0.004), (1.16, 0.96, 0.006), (0.14, 0.13, 0.13, 1.0))
    make_box("EntryMat", (0.30, 0.78, 0.011), (1.02, 0.82, 0.008), P.RUBBER_MAT)
    # Coat pegs by the door — Finn's wool cap + coat come in from the rain
    make_box("CoatRail", (1.60, 0.115, 1.72), (0.60, 0.05, 0.06), COL_WOOD_DARK)
    for pi, px in enumerate((1.42, 1.60, 1.78)):
        make_cyl(f"CoatPeg_{pi}", (px, 0.20, 1.70), 0.012, 0.10, COL_CHROME, axis='Y')
    make_box("Coat_Wax", (1.42, 0.24, 1.42), (0.30, 0.10, 0.52), (0.38, 0.36, 0.26, 1.0))
    make_box("Coat_WoolCap", (1.72, 0.20, 1.66), (0.12, 0.10, 0.10), (0.34, 0.30, 0.24, 1.0))
    # Exterior sign board above the door (THE MISSING LINK, scene-side)
    make_box("MissingLink_SignBracket", (0.30, -0.32, 2.60), (0.06, 0.60, 0.06), COL_BLACK)
    make_box("MissingLink_SignBoard", (0.30, -0.34, 2.42), (1.50, 0.06, 0.46), COL_VINYL_DK)
    for ri, sgn in enumerate((-1, +1)):
        make_box(f"MissingLink_SignRule_{ri}", (0.30, -0.37, 2.42 + sgn * 0.18),
                 (1.36, 0.02, 0.03), COL_CHROME)


# ═════════════════════════════════════════════════════════════════
# EXTERIOR — the wet street the front windows look onto (ch9 rain,
# ch16 Saturday). Sidewalk, curb, rain-dark asphalt, a puddle, a
# curb-side streetlamp (public right-of-way rule). Kept thin — this
# is an interior locale.
# ═════════════════════════════════════════════════════════════════
def build_exterior():
    # South (street) frontage seen through the door + south window
    make_box("Ext_Sidewalk_S", (0.0, -1.20, -0.03), (9.4, 2.40, 0.06), COL_CONCRETE)
    for si in range(4):
        make_box(f"Ext_SeamS_{si}", (-3.0 + si * 2.0, -1.20, 0.002),
                 (0.02, 2.40, 0.002), (0.40, 0.39, 0.37, 1.0))
    make_box("Ext_Curb_S", (0.0, -2.46, -0.02), (9.4, 0.16, 0.12), (0.46, 0.45, 0.43, 1.0))
    make_box("Ext_Street_S", (0.0, -3.60, -0.05), (9.4, 2.20, 0.04), COL_ASPHALT)
    make_box("Ext_Puddle_S", (1.5, -3.20, -0.028), (1.30, 0.60, 0.002), COL_PUDDLE)
    # West frontage seen through the long booth-row window
    make_box("Ext_Sidewalk_W", (-4.35, 1.70, -0.03), (2.30, 5.60, 0.06), COL_CONCRETE)
    make_box("Ext_Curb_W", (-5.55, 1.70, -0.02), (0.16, 5.60, 0.12), (0.46, 0.45, 0.43, 1.0))
    make_box("Ext_Street_W", (-6.70, 1.70, -0.05), (2.20, 5.60, 0.04), COL_ASPHALT)
    make_box("Ext_Puddle_W", (-4.70, 0.90, -0.028), (0.70, 0.90, 0.002), COL_PUDDLE)
    # Curb-side streetlamp (buffer strip, never in the roadway)
    make_cyl("Streetlamp_Pole", (-3.85, -2.30, 2.05), 0.045, 4.10, COL_BLACK, segments=12)
    make_cyl("Streetlamp_Arm", (-3.70, -2.30, 4.00), 0.025, 0.40, COL_BLACK, axis='X')
    make_cyl("Streetlamp_Head", (-3.48, -2.30, 3.94), 0.09, 0.14, COL_BLACK, segments=12)
    make_cyl("Streetlamp_Glow", (-3.48, -2.30, 3.85), 0.065, 0.05, (0.98, 0.84, 0.56, 1.0),
             segments=12)


# ═════════════════════════════════════════════════════════════════
# THE COUNTER — where Kai sat on the THIRD stool (ch16). Formica
# counter running N-S along the east side, chrome-edged; five chrome-
# and-red-vinyl stools face it. Behind it, the service aisle Aud
# works in ("went back behind the counter"): the backbar against the
# east wall with the drip-coffee station (Aud "came over with the
# coffee"), the register (tokens accepted), and the domed SALMONBERRY
# PIE case (ch16: the slice she kept in the cooler; ch9: "fresh
# today"). Kai's setting — soup + pie + coffee — at the third stool.
# ═════════════════════════════════════════════════════════════════
def build_counter():
    top_z = make_counter("Counter", (1.0, 2.70, 0.0), length=3.00, depth=0.60, height=0.90,
                         palette={"formica": COL_FORMICA, "top": COL_FORM_TOP,
                                  "kick": COL_FORM_EDGE})
    make_counter_bullnose("Counter", (0.70, 2.70, top_z), length=3.00,
                          palette={"top": COL_FORM_EDGE})
    # Stools — Kai's is the THIRD (counting from the south end)
    stool_y = [1.50, 2.10, 2.70, 3.30, 3.90]
    for si, sy in enumerate(stool_y):
        _stool(f"Stool_{si}", 0.30, sy)
    # Kai's setting on the counter at the third stool (ch16: soup + pie
    # + the second cup of coffee)
    kai_y = stool_y[2]
    _cup_saucer("KaiCup", 0.78, kai_y - 0.14, top_z)
    make_cyl("KaiSoupBowl", (0.86, kai_y + 0.10, top_z + 0.015), 0.078, 0.05, COL_CREAM, segments=12)
    make_cyl("KaiSoup", (0.86, kai_y + 0.10, top_z + 0.055), 0.064, 0.02, COL_SOUP, segments=12)
    _pie_slice("KaiPie", 0.62, kai_y + 0.02, top_z)
    # Napkin dispensers + sugar caddies spaced along the counter
    for ci, cy in enumerate((1.70, 3.10)):
        _napkin_dispenser(f"CounterNapkins_{ci}", 0.60, cy, top_z)
        make_sugar_creamer_caddy(f"CounterCaddy_{ci}", (0.58, cy + 0.30, top_z + 0.04))
    _condiments("CounterCond", 0.60, 2.40, top_z)

    # ── Backbar against the east wall (service side)
    bb_x = 2.55
    make_box("Backbar_Body", (bb_x, 2.70, 0.44), (0.55, 3.00, 0.88), COL_FORMICA)
    make_box("Backbar_Top", (bb_x, 2.70, 0.90), (0.60, 3.06, 0.05), COL_STEEL)
    make_box("Backbar_Kick", (bb_x - 0.27, 2.70, 0.10), (0.02, 3.00, 0.20), COL_FORM_EDGE)
    # Drip-coffee station (Y-spread pots ride the backbar perfectly)
    make_box("CoffeeMaker_Body", (bb_x + 0.05, 2.60, 1.06), (0.34, 0.60, 0.30), COL_STEEL)
    make_box("CoffeeMaker_Panel", (bb_x - 0.14, 2.60, 1.06), (0.02, 0.52, 0.22), COL_BLACK)
    make_coffee_pots("CoffeePots", (bb_x + 0.02, 2.60, 0.92),
                     palette={"glass": COL_GLASSISH})
    # Register (tokens accepted at face value, ch9)
    make_register("Register", (bb_x - 0.02, 3.85, 0.92), palette={"body": (0.28, 0.26, 0.26, 1.0)})
    make_cyl("TokenDish", (bb_x - 0.20, 3.55, 0.945), 0.055, 0.02, COL_WOOD, segments=12)
    for ti in range(4):
        make_cyl(f"Token_{ti}", (bb_x - 0.21 + (ti % 2) * 0.02, 3.55 + (ti % 3) * 0.012,
                 0.955 + (ti // 2) * 0.007), 0.026, 0.006, COL_TOKEN, segments=10)
    # Domed SALMONBERRY PIE case on the backbar (the canon pie)
    make_cyl("PieCase_Base", (bb_x - 0.02, 1.55, 0.94), 0.20, 0.03, COL_STEEL, segments=12)
    make_cyl("PieCase_Pie", (bb_x - 0.02, 1.55, 0.98), 0.18, 0.05, COL_PIE_CRUST, segments=12)
    make_cyl("PieCase_Top", (bb_x - 0.02, 1.55, 1.035), 0.175, 0.02, COL_PIE_FILL, segments=12)
    for wi in range(6):        # six wedge seams cut into the top
        make_box(f"PieCase_Wedge_{wi}", (bb_x - 0.02, 1.55, 1.05),
                 (0.34, 0.006, 0.006) if wi % 2 else (0.006, 0.34, 0.006), COL_CREAM)
    make_cyl("PieCase_Dome", (bb_x - 0.02, 1.55, 1.13), 0.21, 0.20, COL_GLASSISH, segments=12)
    make_cyl("PieCase_Knob", (bb_x - 0.02, 1.55, 1.25), 0.02, 0.04, COL_CHROME, segments=8)
    # A stack of clean plates + mugs at the north end of the backbar
    for pi in range(6):
        make_cyl(f"BackbarPlate_{pi}", (bb_x + 0.06, 4.10, 0.945 + pi * 0.012), 0.09, 0.012,
                 COL_PLATE, segments=12)
    for mi in range(4):
        make_cyl(f"BackbarMug_{mi}", (bb_x + 0.10, 4.35, 0.99), 0.038, 0.09, COL_CREAM, segments=10)


# ═════════════════════════════════════════════════════════════════
# THE KITCHEN PASS — recessed into the east wall over the north end
# of the backbar (Aud "went to put the order in"). A framed pass with
# a shadowed back (kitchen implied, no void), a heat-lamp glow, plated
# food from the two canon orders (meatloaf; fish and chips), and the
# order-ticket wheel.
# ═════════════════════════════════════════════════════════════════
def build_pass():
    px = ROOM_W / 2.0 - 0.10        # 2.90 interior east face
    cy = 3.00
    z0, z1 = 1.30, 1.98
    # Shadowed recess back (kitchen implied) + stainless frame
    make_box("Pass_Back", (px + 0.06, cy, (z0 + z1) / 2.0), (0.04, 1.30, z1 - z0), (0.10, 0.10, 0.11, 1.0))
    make_box("Pass_FrameT", (px, cy, z1 + 0.03), (0.10, 1.42, 0.06), COL_STEEL)
    make_box("Pass_FrameB", (px, cy, z0 - 0.03), (0.10, 1.42, 0.06), COL_STEEL)
    for sgn in (-1, +1):
        make_box(f"Pass_FrameSide_{sgn:+d}", (px, cy + sgn * 0.68, (z0 + z1) / 2.0),
                 (0.10, 0.06, z1 - z0 + 0.12), COL_STEEL)
    # Pass shelf (plates handed across) + heat-lamp hood + glow
    make_box("Pass_Shelf", (px - 0.14, cy, z0 + 0.02), (0.28, 1.30, 0.04), COL_STEEL)
    make_box("Pass_LampHood", (px - 0.10, cy, z1 - 0.05), (0.22, 1.20, 0.06), COL_BLACK)
    make_box("Pass_LampGlow", (px - 0.10, cy, z1 - 0.10), (0.16, 1.10, 0.02), COL_HEATLAMP)
    # Plated orders under the lamps — meatloaf (Kai) + fish and chips (Finn)
    make_cyl("PassPlate_Meatloaf", (px - 0.16, 2.62, z0 + 0.05), 0.10, 0.02, COL_PLATE, segments=12)
    make_box("PassMeatloaf", (px - 0.16, 2.62, z0 + 0.085), (0.11, 0.06, 0.05), COL_MEATLOAF)
    make_cyl("PassPlate_Fish", (px - 0.16, 3.38, z0 + 0.05), 0.10, 0.02, COL_PLATE, segments=12)
    for fi in range(4):
        make_box(f"PassFries_{fi}", (px - 0.20 + (fi % 2) * 0.04, 3.34 + (fi // 2) * 0.05, z0 + 0.09),
                 (0.02, 0.06, 0.02), COL_FISH)
    make_box("PassFish", (px - 0.14, 3.42, z0 + 0.085), (0.10, 0.05, 0.04), COL_FISH)
    # Order-ticket wheel (spins on a rod under the lamp)
    make_cyl("TicketWheel_Rod", (px - 0.06, cy, z1 - 0.16), 0.010, 0.20, COL_CHROME, axis='Y')
    for ti in range(5):
        ay = cy - 0.16 + ti * 0.08
        make_box(f"Ticket_{ti}", (px - 0.10, ay, z1 - 0.24), (0.10, 0.006, 0.12), COL_MENU)


# ═════════════════════════════════════════════════════════════════
# SEATING — the BOOTHS. Three vinyl-and-formica booths run along the
# west storefront window (ch16: "the booths along the front window
# were full"). The two front ones are the window booths; the
# northmost is THE BACK BOOTH (ch9: "the booth at the back... she
# gave the kids on Tuesday nights"; ch16: Frog Petersen + Bernie Lund
# and Frog's leek soup).
# ═════════════════════════════════════════════════════════════════
def build_booths():
    _booth("BoothFrontA", -2.20, 1.05, occupied=True)   # front window, full (Saturday)
    _booth("BoothFrontB", -2.20, 2.45, occupied=True)   # front window, full
    _booth("BoothBack", -2.20, 3.85, occupied=True, is_back=True)  # THE BACK BOOTH


# ═════════════════════════════════════════════════════════════════
# DECOR — the wall clock (noon, ch16), Aud's calendar, a couple of
# sun-faded coastal posters, the specials chalkboard (leek soup /
# salmonberry pie — lettering scene-side), a wall payphone (90s
# register), a fire extinguisher, and a floor plant by the entrance.
# ═════════════════════════════════════════════════════════════════
def build_decor():
    # Clock on the north wall over the counter — noon (ch16 "at noon")
    make_wall_clock("Clock", (0.0, ROOM_D - 0.10, 2.20), frozen_hour=12, frozen_min=5)
    # Specials chalkboard on the north wall (scene-side text)
    make_box("SpecialsBoard_Frame", (-1.35, ROOM_D - 0.11, 1.85), (0.90, 0.03, 0.66), COL_WOOD_DARK)
    make_box("SpecialsBoard", (-1.35, ROOM_D - 0.125, 1.85), (0.82, 0.02, 0.58), COL_SLATE)
    # Calendar + faded posters on the north wall
    make_calendar("Calendar", (1.55, ROOM_D - 0.12, 1.95))
    make_faded_poster("Poster_Coast", (2.55, ROOM_D - 0.12, 1.85),
                      palette={"body": (0.66, 0.62, 0.50, 1.0), "ink": (0.30, 0.34, 0.34, 1.0)})
    # Faded poster on the solid north stretch of the west wall (behind
    # the back booth divider)
    make_faded_poster("Poster_West", (-ROOM_W / 2.0 + 0.10, 4.30, 1.80),
                      palette={"body": (0.64, 0.58, 0.46, 1.0), "ink": (0.34, 0.26, 0.20, 1.0)})
    # Wall payphone by the entrance (east side of the door, 90s register)
    make_payphone("Payphone", (ROOM_W / 2.0 - 0.11, 0.55, 1.45))
    # Fire extinguisher on the east wall near the pass
    make_fire_extinguisher("FireExt", (ROOM_W / 2.0 - 0.12, 4.40, 0.0))
    # Floor plant by the entrance
    make_floor_plant("Plant", (-2.70, 0.55, 0.0),
                     palette={"leaf": (0.38, 0.48, 0.36, 1.0), "pot": (0.46, 0.34, 0.22, 1.0)})


# ═════════════════════════════════════════════════════════════════
# CEILING INFRA — the humming fluorescents that make the operator-
# noir register (three troffers), an HVAC supply grille, a smoke
# detector.
# ═════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    for j in range(3):
        ypos = 1.1 + j * 1.4
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.60, width=0.34)
    make_fluorescent_tube_fixture("Fluor_Booth", (-2.05, 2.45, CEIL), length=1.20, width=0.30)
    make_hvac_vent("HVAC", (1.6, 1.4, CEIL), width=0.90, depth=0.50)
    make_smoke_detector("Smoke", (0.6, 3.6, CEIL))


def main():
    clear_scene()
    build_shell()
    build_storefront()
    build_exterior()
    build_counter()
    build_pass()
    build_booths()
    build_decor()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/missing_link_interior.glb"))
    print(f"\n[build_missing_link_interior] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
