"""editing_suite — the four's editing suite at Aud's, and vol 3's night edit
station (draft 1, 2026-10-18).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."

THE SUITE (origin) — the same room in vol 1, the vol 2 meld and vol 4's meld:
behind the grill wall at Aud's in Small Wood ("through the wall behind the
grill"). One window, "nothing out of it" (vol 1: "THE ARTIST is at the
window, looking out at nothing in particular"). What each scene puts in it:
  vol 1: "Monitors.", the console the Director types at, the couch with an
   arm (the Writer on it, the Human Being on the floor against it), the
   door the Fool bursts through, his popcorn bucket; at the end "The suite
   goes dark, all but the monitor."
  vol 2: "Four chairs on casters. A bank of monitors, and every one of them
   full of water." — the tide flats; the deck nobody touches.
  vol 4: 4 a.m., "Coffee rings on everything", the cup that runs over along
   the cables, the door with the gap the coffee goes out under; on the
   monitors a bakery window and a street of minivan doors.
What plays on the screens is per view (`<Name>__<preset>`), and so are the
popcorn and the coffee.
THE NIGHT EDIT STATION (x 40..44) — vol 3 ch4: the narrator and his friend
editing all weekend just after 2001; "the AVID software editing suite" is the
program. One desk, the computer, the monitor, the tape. Nothing more is given.

Blender: x east, y north, z up; Godot (x, z, -y).

DRAFT 2 targets: the grill wall as a real wall with Aud's on its other side
(the diner build); the frozen frame's painting as an image; the couch's
floor-sitter's spot worn; the edit station's tapes and the night outside;
Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_tube, catenary,
                             join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings
from _props.furniture import make_chair, make_lamp
from _props.detail import make_wall_outlet, make_light_switch

X0, X1, D, H, T = -3.8, 3.8, 6.6, 2.8, 0.20
WALL = (0.54, 0.52, 0.54, 1.0); BASE = (0.24, 0.24, 0.26, 1.0)
PAL = {"wall": WALL, "baseboard": BASE}
CARPET = (0.26, 0.26, 0.30, 1.0); CARPET_SEAM = (0.22, 0.22, 0.26, 1.0)
FLAT = (0.08, 0.08, 0.09, 1.0)
DECK = (0.18, 0.18, 0.20, 1.0)
WIDE, TIDE, FOUR = "__suite_wide", "__suite_tide", "__suite_4am"


def screen(prefix, x, y, z, w, h, contents):
    """A monitor on the wall rack: its bezel, then one face per view."""
    make_box(f"{prefix}_Bezel", (x, y, z), (w, 0.08, h), FLAT)
    for suffix, col in contents:
        make_box(f"{prefix}_Face{suffix}", (x, y - 0.042, z), (w - 0.06, 0.004, h - 0.06), col)


def build_suite():
    cx, cy = (X0 + X1) / 2.0, D / 2.0
    make_floor("Suite_Floor", (cx, cy, 0.0), size_x=X1 - X0 + 0.4, size_y=D + 0.4, palette={"vinyl": CARPET, "seam": CARPET_SEAM})
    make_box("Suite_Ceil", (cx, cy, H + 0.04), (X1 - X0 + 0.4, D + 0.4, 0.08), (0.30, 0.30, 0.32, 1.0))
    make_wall("Suite_Wall_N", (cx, D, 0), length=X1 - X0 + 0.4, height=H, thickness=T, axis='X', palette=PAL, baseboard_face_sign=-1)
    # the E wall is the one behind Aud's grill
    make_wall("Suite_Wall_E_Grill", (X1, cy, 0), length=D + 0.4, height=H, thickness=0.30, axis='Y', palette=PAL, baseboard_face_sign=-1)
    make_wall_with_openings("Suite_Wall_W", (X0, cy, 0), length=D + 0.4, height=H, thickness=T, axis='Y', palette=PAL,
                            baseboard_face_sign=+1, openings=[(3.6, 1.55, 1.2, 1.2)])
    # the one window and nothing out of it: a pale, featureless pane
    make_box("Suite_Window_Pane", (X0, 3.6, 1.55), (0.02, 1.2, 1.2), (0.70, 0.72, 0.74, 1.0))
    make_box("Suite_Window_Sill", (X0 + 0.14, 3.6, 0.93), (0.16, 1.32, 0.04), (0.50, 0.50, 0.52, 1.0))
    make_box("Suite_Window_Mullion", (X0 + 0.02, 3.6, 1.55), (0.03, 0.03, 1.2), (0.50, 0.50, 0.52, 1.0))
    make_wall_with_openings("Suite_Wall_S", (cx, 0.0, 0), length=X1 - X0 + 0.4, height=H, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=+1, openings=[(2.4, 1.02, 0.90, 2.04)])
    # the door, shut, the gap under it (the coffee goes out under it)
    make_box("Suite_Door", (2.4, 0.0, 1.05), (0.88, 0.05, 2.0), (0.40, 0.30, 0.24, 1.0))
    make_cyl("Suite_Door_Knob", (2.0, 0.045, 1.0), 0.026, 0.04, (0.70, 0.64, 0.44, 1.0), axis='Y', segments=10)
    make_light_switch("Suite_Switch", (1.6, 0.0), axis='X', face_sign=1)
    # the monitor wall on the N: a rack, the four monitors and the big one
    make_box("Monitor_Rack", (0.0, D - 0.10 - 0.30, 0.45), (4.4, 0.60, 0.90), (0.14, 0.14, 0.16, 1.0))
    tide = (0.62, 0.66, 0.66, 1.0); tide_wet = (0.50, 0.58, 0.62, 1.0)
    frozen = (0.80, 0.70, 0.52, 1.0)        # morning light on the painter's back, the blank canvas
    bakery = (0.86, 0.66, 0.40, 1.0); minivans = (0.46, 0.50, 0.58, 1.0)
    for k in range(4):
        x = -1.65 + k * 1.10
        screen(f"Monitor_{k}", x, D - 0.10 - 0.04, 1.32, 1.00, 0.70,
               ((WIDE, (0.24, 0.26, 0.30, 1.0)), (TIDE, (tide, tide_wet)[k % 2]), (FOUR, (bakery, minivans, (0.30, 0.30, 0.34, 1.0), bakery)[k])))
    screen("Monitor_Hero", 0.0, D - 0.10 - 0.04, 2.12, 1.80, 0.86,
           ((WIDE, frozen), (TIDE, tide), (FOUR, (0.40, 0.40, 0.46, 1.0))))
    # the frozen frame's painter (vol 1): back to camera, the blank canvas
    make_box("Frozen_Canvas" + WIDE, (0.25, D - 0.10 - 0.088, 2.10), (0.42, 0.004, 0.52), (0.96, 0.96, 0.94, 1.0))
    make_box("Frozen_Painter" + WIDE, (-0.25, D - 0.10 - 0.089, 2.02), (0.22, 0.004, 0.50), (0.30, 0.24, 0.20, 1.0))
    # the deck / console across in front of it
    make_box("Deck_Desk", (0.0, D - 1.55, 0.74), (3.40, 0.86, 0.04), DECK)
    for s in (-1, 1):
        make_box(f"Deck_Desk_Panel_{s:+d}", (s * 1.66, D - 1.55, 0.36), (0.04, 0.80, 0.72), DECK)
    make_box("Deck_Console", (0.0, D - 1.45, 0.80), (1.60, 0.50, 0.08), (0.24, 0.24, 0.26, 1.0))
    for k in range(16):
        make_box(f"Deck_Fader_{k}", (-0.70 + k * 0.093, D - 1.38, 0.845), (0.02, 0.10, 0.012), (0.70, 0.70, 0.72, 1.0))
    make_box("Deck_Keyboard", (0.0, D - 1.80, 0.77), (0.46, 0.16, 0.02), (0.20, 0.20, 0.22, 1.0))
    make_cyl("Deck_Jog", (0.60, D - 1.75, 0.78), 0.06, 0.03, (0.30, 0.30, 0.32, 1.0), segments=14)
    # the cables, from the rack down over the desk's edge and along the floor
    for k in range(5):
        x = -1.2 + k * 0.6
        make_tube(f"Cable_Stock_{k}", catenary((x, D - 1.15, 0.76), (x + 0.3, D - 1.15, 0.02), 0.20), 0.012, FLAT)
        make_tube(f"Cable_Stock_Floor_{k}", [(x + 0.3, D - 1.15, 0.012), (x + 0.4, D - 2.6, 0.012), (x + 0.2, 1.0, 0.012)], 0.012, FLAT)
    # four chairs on casters
    for k in range(4):
        x = -1.65 + k * 1.10
        make_cyl(f"Caster_Chair_{k}_Base", (x, D - 2.45, 0.02), 0.30, 0.04, (0.20, 0.20, 0.22, 1.0), segments=10)
        make_cyl(f"Caster_Chair_{k}_Post", (x, D - 2.45, 0.24), 0.03, 0.40, (0.30, 0.30, 0.32, 1.0), segments=8)
        make_chamfer_box(f"Caster_Chair_{k}_Seat", (x, D - 2.45, 0.49), (0.50, 0.50, 0.10), (0.20, 0.22, 0.30, 1.0), chamfer=0.03)
        make_chamfer_box(f"Caster_Chair_{k}_Back", (x, D - 2.45 - 0.24, 0.82), (0.46, 0.08, 0.56), (0.20, 0.22, 0.30, 1.0), chamfer=0.03)
    # the couch behind them, its arm, the open floor in front of it
    cy2 = 1.40
    make_box("Suite_Couch_Base", (-0.6, cy2, 0.22), (2.40, 0.90, 0.44), (0.40, 0.30, 0.22, 1.0))
    make_box("Suite_Couch_Back", (-0.6, cy2 - 0.36, 0.68), (2.40, 0.18, 0.56), (0.40, 0.30, 0.22, 1.0))
    for s in (-1, 1):
        make_box(f"Suite_Couch_Arm_{s:+d}", (-0.6 + s * 1.11, cy2, 0.56), (0.18, 0.90, 0.24), (0.40, 0.30, 0.22, 1.0))
    for k in range(3):
        make_box(f"Suite_Couch_Cush_{k}", (-1.30 + k * 0.70, cy2 + 0.06, 0.49), (0.66, 0.66, 0.12), (0.46, 0.36, 0.26, 1.0))
    make_box("Suite_Rug", (-0.6, 2.6, 0.006), (2.4, 1.4, 0.012), (0.34, 0.26, 0.24, 1.0))
    # vol 1: the Fool's popcorn bucket (mostly empty), the Writer's notebook
    make_lathe = None
    make_cyl("Popcorn_Bucket" + WIDE, (0.9, 2.2, 0.13), 0.12, 0.26, (0.90, 0.20, 0.18, 1.0), segments=12)
    make_box("Writer_Notebook" + WIDE, (0.66, cy2 + 0.02, 0.69), (0.16, 0.22, 0.02), (0.16, 0.20, 0.30, 1.0))
    # vol 4, 4 a.m.: the coffee — the pot set down, the cups, the rings, the spill along the cables
    make_cyl("Coffee_Pot" + FOUR, (1.20, D - 1.70, 0.84), 0.08, 0.16, (0.30, 0.20, 0.14, 1.0), segments=12)
    for k in range(4):
        make_cyl(f"Coffee_Cup_{k}" + FOUR, (-1.4 + k * 0.6, D - 1.80, 0.80), 0.04, 0.10, (0.92, 0.92, 0.90, 1.0), segments=10)
    for k in range(9):
        make_cyl(f"Coffee_Ring_{k}" + FOUR, (-1.5 + k * 0.36, D - 1.62 + (k % 2) * 0.12, 0.761), 0.04, 0.002, (0.44, 0.30, 0.18, 1.0), segments=12)
    make_box("Coffee_Spill_Desk" + FOUR, (-0.6, D - 1.20, 0.761), (0.60, 0.10, 0.002), (0.36, 0.22, 0.12, 1.0))
    make_box("Coffee_Spill_Floor" + FOUR, (-0.2, 3.2, 0.013), (0.14, 3.2, 0.002), (0.36, 0.22, 0.12, 1.0))
    make_box("Coffee_Spill_Door" + FOUR, (2.0, 0.6, 0.013), (0.80, 0.12, 0.002), (0.36, 0.22, 0.12, 1.0))
    make_wall_outlet("Suite_Outlet", (-2.6, D), axis='X', face_sign=-1)


def build_edit_station():
    """Vol 3 ch4: one desk, the computer running the edit software, the
    monitor with the tape on it, a chair; a small room at night."""
    x0, x1, d, h = 40.0, 44.0, 3.6, 2.6
    cx, cy = (x0 + x1) / 2.0, d / 2.0
    make_floor("Edit_Floor", (cx, cy, 0.0), size_x=x1 - x0 + 0.4, size_y=d + 0.4,
               palette={"vinyl": (0.48, 0.40, 0.32, 1.0), "seam": (0.40, 0.34, 0.28, 1.0)})
    make_box("Edit_Ceil", (cx, cy, h + 0.04), (x1 - x0 + 0.4, d + 0.4, 0.08), (0.80, 0.78, 0.74, 1.0))
    pal = {"wall": (0.74, 0.72, 0.66, 1.0), "baseboard": (0.42, 0.40, 0.36, 1.0)}
    make_wall("Edit_Wall_N", (cx, d, 0), length=x1 - x0 + 0.4, height=h, thickness=0.2, axis='X', palette=pal, baseboard_face_sign=-1)
    make_wall("Edit_Wall_E", (x1, cy, 0), length=d + 0.4, height=h, thickness=0.2, axis='Y', palette=pal, baseboard_face_sign=-1)
    make_wall_with_openings("Edit_Wall_W", (x0, cy, 0), length=d + 0.4, height=h, thickness=0.2, axis='Y', palette=pal,
                            baseboard_face_sign=+1, openings=[(1.8, 1.5, 1.0, 1.0)])
    make_box("Edit_Window_Night", (x0, 1.8, 1.5), (0.02, 1.0, 1.0), (0.04, 0.05, 0.08, 1.0))
    make_wall_with_openings("Edit_Wall_S", (cx, 0.0, 0), length=x1 - x0 + 0.4, height=h, thickness=0.2, axis='X', palette=pal,
                            baseboard_face_sign=+1, openings=[(x1 - 0.8, 1.0, 0.86, 2.0)])
    make_box("Edit_Door", (x1 - 0.8, 0.0, 1.0), (0.84, 0.05, 2.0), (0.52, 0.42, 0.32, 1.0))
    dx, dy = cx, d - 0.10 - 0.38
    make_box("Edit_Desk_Top", (dx, dy, 0.74), (1.80, 0.76, 0.03), (0.50, 0.40, 0.30, 1.0))
    for s in (-1, 1):
        make_box(f"Edit_Desk_Panel_{s:+d}", (dx + s * 0.88, dy, 0.36), (0.04, 0.72, 0.72), (0.44, 0.34, 0.26, 1.0))
    make_chamfer_box("Edit_CRT", (dx - 0.30, dy + 0.06, 0.97), (0.44, 0.42, 0.42), (0.20, 0.20, 0.22, 1.0), chamfer=0.03)
    make_box("Edit_CRT_Screen", (dx - 0.30, dy - 0.155, 0.98), (0.34, 0.004, 0.26), (0.30, 0.40, 0.70, 1.0))
    make_box("Edit_Second_Monitor", (dx + 0.40, dy + 0.10, 0.93), (0.40, 0.06, 0.32), FLAT)
    make_box("Edit_Second_Monitor_Screen", (dx + 0.40, dy + 0.068, 0.93), (0.36, 0.004, 0.28), (0.24, 0.26, 0.34, 1.0))
    make_box("Edit_Second_Monitor_Foot", (dx + 0.40, dy + 0.10, 0.765), (0.16, 0.12, 0.02), FLAT)
    make_box("Edit_Tower", (dx + 0.95 - 0.20, dy, 0.24), (0.20, 0.44, 0.48), (0.20, 0.20, 0.22, 1.0))
    make_box("Edit_Tape_Deck", (dx + 0.20, dy - 0.10, 0.79), (0.36, 0.26, 0.09), (0.14, 0.14, 0.16, 1.0))
    for k in range(4):
        make_box(f"Edit_Tape_{k}", (dx - 0.62, dy - 0.20 + k * 0.08, 0.77), (0.10, 0.06, 0.04), (0.10, 0.10, 0.12, 1.0))
    make_box("Edit_Keyboard", (dx - 0.20, dy - 0.24, 0.765), (0.44, 0.15, 0.02), (0.20, 0.20, 0.22, 1.0))
    make_lamp("Lamp_Edit", dx + 0.78, dy + 0.18, base_z=0.755, h=0.40)
    make_chair("Edit_Chair", dx - 0.10, dy - 0.75, yaw=0.0, wood=(0.24, 0.24, 0.26, 1.0))
    make_chair("Edit_Chair_2", dx + 0.60, dy - 0.85, yaw=0.3, wood=(0.24, 0.24, 0.26, 1.0))


def build_suite_dressing_2026_10():
    """DRAFT 2 (2026-10-30): the room read as four bare walls round the
    monitors — nothing an editing suite keeps. The text gives the monitors,
    the console, the couch, the window with nothing out of it, the door; this
    adds what such a room has and the text does not contradict: the tapes,
    the monitor speakers, the acoustic panels, a drop ceiling, and the worn
    carpet where the Human Being sits on the floor against the couch's arm."""
    WX = X0 + T / 2.0            # the W wall's room face
    NY = D - T / 2.0             # the N wall's room face
    # a tape shelf on the W wall between the couch end and the window
    sy0, sy1, sd, sh = 1.0, 2.8, 0.30, 2.0
    shelf = (0.20, 0.18, 0.18, 1.0)
    for k, y in enumerate((sy0, sy1)):
        make_box(f"Tape_Shelf_Side_{k}", (WX + sd / 2.0, y, sh / 2.0), (sd, 0.03, sh), shelf)
    for r in range(6):
        z = 0.06 + r * 0.38
        make_box(f"Tape_Shelf_Board_{r}", (WX + sd / 2.0, (sy0 + sy1) / 2.0, z), (sd, sy1 - sy0 - 0.03, 0.025), shelf)
        if r == 5:
            continue
        # the tapes standing on it, spines out: black cases, a few labelled
        y = sy0 + 0.04
        k = 0
        while y < sy1 - 0.06:
            w = 0.028 if (k * 7 + r) % 5 else 0.034
            col = (0.08, 0.08, 0.09, 1.0) if (k + r) % 4 else (0.70, 0.66, 0.58, 1.0)
            make_box(f"Tape_Stock_{r}_{k}", (WX + 0.12, y + w / 2.0, z + 0.0125 + 0.095), (0.18, w - 0.004, 0.19), col)
            y += w + (0.06 if (k * 3 + r) % 11 == 0 else 0.0)
            k += 1
    # the monitor speakers either side of the big monitor, on wall brackets
    for sx in (-1, 1):
        x = sx * 1.35
        make_box(f"Suite_Speaker_Bracket_{sx:+d}", (x, NY - 0.10, 1.86), (0.12, 0.20, 0.04), FLAT)
        make_chamfer_box(f"Suite_Speaker_{sx:+d}", (x, NY - 0.12, 2.06), (0.24, 0.22, 0.36), (0.12, 0.12, 0.13, 1.0), chamfer=0.01)
        make_cyl(f"Suite_Speaker_Cone_{sx:+d}", (x, NY - 0.235, 2.00), 0.08, 0.01, (0.20, 0.20, 0.22, 1.0), axis='Y', segments=14)
        make_cyl(f"Suite_Speaker_Tweeter_{sx:+d}", (x, NY - 0.235, 2.16), 0.025, 0.01, (0.30, 0.30, 0.32, 1.0), axis='Y', segments=10)
    # acoustic panels on the N wall past the monitors, two each side
    for sx in (-1, 1):
        for j in range(2):
            x = sx * (2.70 + j * 0.66)
            make_box(f"Suite_Acoustic_Panel_{sx:+d}_{j}", (x, NY - 0.025, 1.65), (0.60, 0.05, 1.20), (0.20, 0.22, 0.28, 1.0))
    # the drop ceiling: the grid's T-bars and two troffers (the overhead's)
    grid = (0.62, 0.62, 0.60, 1.0)
    for i in range(1, 11):
        y = i * 0.61
        make_box(f"Ceil_Grid_Stock_Y{i}", ((X0 + X1) / 2.0, y, H - 0.01), (X1 - X0, 0.025, 0.02), grid)
    for i in range(1, 7):
        x = X0 + i * 1.22 - 0.06
        make_box(f"Ceil_Grid_Stock_X{i}", (x, D / 2.0, H - 0.01), (0.025, D, 0.02), grid)
    for k, (x, y) in enumerate(((-0.81, 2.745), (1.63, 4.575))):
        make_box(f"Ceil_Troffer_{k}", (x, y, H - 0.012), (1.18, 0.57, 0.02), (0.88, 0.88, 0.84, 1.0))
    # the carpet worn flat where the Human Being sits against the couch's arm
    make_box("Suite_Carpet_Worn", (0.86, 1.50, 0.004), (0.54, 0.62, 0.004), (0.32, 0.31, 0.34, 1.0))


def main():
    clear_scene()
    build_suite()
    build_suite_dressing_2026_10()
    build_edit_station()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/editing_suite.glb"))
    print(f"\n[build_editing_suite] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
