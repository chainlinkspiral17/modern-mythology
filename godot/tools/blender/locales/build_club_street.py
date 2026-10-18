"""club_street — vol 1's street outside Club # (draft 1, 2026-10-18).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
The club's inside is club_sharp; this is its street face, on the lot Wagner
"walk[s] by all the time" ("Above the door, the # logo hangs unlit."):
  ch8 triumvirate: "Outside, the world is a wash of color and activity."
   (how the three now see: the mood stack, not neon fixtures)
                                              → club_street_door
  ch9 the street: "Every streetlight has a halo and each halo has its own
   halo."; "A bus goes by with an ad on the side for a product that doesn't
   exist yet."; "The three stand on the curb"; Judgement Day "parked at the
   curb where nobody parked it", the frame shirt tied to its rearview
   ("It hangs there like fuzzy dice."; the shirt itself is draft 2: a prop
   inside the car's body reads as a clip to the gates)
                                                 → club_street_curb
  meld kaleidoscope: "neon over a city at night" → club_street_neon_wide
  ch16 four am: "They walk out together into a street that is just a street,
   ordinary, gray, about to be morning. Judgement Day is parked at the
   curb."                                         → club_street_dawn
No city or street is named; nothing later than 2010 (the book): sodium
streetlights, a 2000s bus with a blank ad, no LED screens.

Blender: x east, y north, z up; Godot (x, z, -y). The club's facade stands
on x 0 (the building west of it), the street runs N-S at x 4..14, the far
side's frontages from x 18. Everything inside 200 m of every camera.

DRAFT 2 targets: the club's door opening onto club_sharp's floor (one
building); passers-by as sprites' marks; the bus's motion; the far side's
frontages as real shop interiors behind their glass.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_blob,
                             join_stock, export_glb)
from _props.vehicles import make_car

CONC = (0.56, 0.55, 0.52, 1.0); ASPHALT = (0.20, 0.20, 0.22, 1.0)
CLUB = (0.12, 0.11, 0.14, 1.0)
CURB_VIEW = "__club_street_curb"
NIGHT_ONLY = "__club_street_door__club_street_curb"


def build_club_front():
    # the club's long black facade, the double door, the # over it
    make_box("Club_Facade", (-0.15, 0.0, 4.0), (0.30, 26.0, 8.0), CLUB)
    make_box("Club_Facade_Cornice", (0.05, 0.0, 7.9), (0.30, 26.2, 0.20), (0.20, 0.18, 0.22, 1.0))
    make_box("Club_Door_Frame", (0.02, 0.0, 1.25), (0.08, 2.0, 2.5), (0.30, 0.28, 0.32, 1.0))
    for s in (-1, 1):
        make_box(f"Club_Door_Leaf_{s:+d}", (0.06, s * 0.46, 1.2), (0.04, 0.88, 2.36), (0.06, 0.06, 0.08, 1.0))
    make_box("Club_Door_Push_Bar", (0.09, 0.0, 1.05), (0.02, 1.6, 0.04), (0.60, 0.60, 0.62, 1.0))
    # the # logo: two uprights and two crossbars on a backing plate
    make_box("Club_Hash_Backing", (0.02, 0.0, 3.4), (0.04, 1.4, 1.4), (0.08, 0.08, 0.10, 1.0))
    for s in (-1, 1):
        make_rot_box(f"Club_Hash_Upright_{s:+d}", (0.065, s * 0.24, 3.4), (0.05, 0.10, 1.2), (0.86, 0.30, 0.60, 1.0), roll=0.18)
        make_box(f"Club_Hash_Bar_{s:+d}", (0.065, 0.0, 3.4 + s * 0.24), (0.05, 1.1, 0.10), (0.86, 0.30, 0.60, 1.0))
    for k, y in enumerate((-9.0, -5.0, 5.0, 9.0)):
        make_box(f"Club_Window_Blacked_{k}", (0.03, y, 4.8), (0.04, 2.0, 1.6), (0.04, 0.04, 0.05, 1.0))
    make_box("Club_Door_Lamp_Mounted", (0.05, 1.3, 2.7), (0.10, 0.16, 0.24), (0.96, 0.84, 0.60, 1.0))
    # the neighbours on this side: a liquor store N, a shut shop S
    make_box("Liquor_Store_Facade", (-0.15, 26.0, 2.8), (0.30, 26.0, 5.6), (0.46, 0.36, 0.30, 1.0))
    make_box("Liquor_Store_Window_Glow", (0.03, 22.0, 1.6), (0.04, 6.0, 1.8), (0.96, 0.86, 0.60, 1.0))
    make_box("Liquor_Store_Sign_Board", (0.03, 22.0, 3.6), (0.06, 5.0, 0.9), (0.80, 0.24, 0.20, 1.0))
    make_box("Shut_Shop_Facade", (-0.15, -26.0, 3.4), (0.30, 26.0, 6.8), (0.40, 0.40, 0.44, 1.0))
    make_box("Shut_Shop_Grille", (0.02, -20.0, 1.5), (0.04, 7.0, 2.4), (0.30, 0.30, 0.32, 1.0))
    make_box("Shut_Shop_Sign_Board", (0.03, -20.0, 3.4), (0.06, 6.0, 0.8), (0.30, 0.50, 0.70, 1.0))
    for k, y in enumerate((-66.0, 66.0)):
        make_box(f"Near_Block_Facade_{k}", (-0.15, y, 5.0), (0.30, 54.0, 10.0), ((0.36, 0.32, 0.30, 1.0), (0.30, 0.32, 0.36, 1.0))[k])
        for j in range(8):
            make_box(f"Near_Block_Window_Glow_{k}_{j}", (0.03, y - 21.0 + j * 6.0, 3.0 + (j % 2) * 3.2), (0.04, 2.0, 1.6),
                     ((1.0, 0.82, 0.52, 1.0), (0.10, 0.10, 0.12, 1.0))[(j + k) % 2])


def build_street():
    make_box("Sidewalk", (2.0, 0.0, 0.06), (4.0, 190.0, 0.12), CONC)
    make_box("Curb", (4.05, 0.0, 0.07), (0.10, 190.0, 0.14), (0.62, 0.60, 0.56, 1.0))
    make_box("Street_Asphalt", (9.0, 0.0, -0.01), (10.0, 190.0, 0.02), ASPHALT)
    for k in range(19):
        make_box(f"Lane_Dash_Stock_{k}", (9.0, -90.0 + k * 10.0, 0.002), (0.12, 3.0, 0.004), (0.86, 0.80, 0.40, 1.0))
    make_box("Curb_Far", (13.95, 0.0, 0.07), (0.10, 190.0, 0.14), (0.62, 0.60, 0.56, 1.0))
    make_box("Sidewalk_Far", (16.0, 0.0, 0.06), (4.0, 190.0, 0.12), CONC)
    # the streetlights (sodium) along the curb
    for k, y in enumerate((-60.0, -30.0, 0.0, 30.0, 60.0)):
        make_cyl(f"Streetlight_{k}_Pole", (4.5, y + 3.0, 2.9), 0.08, 5.8, (0.36, 0.36, 0.38, 1.0), segments=8)
        make_box(f"Streetlight_{k}_Arm", (5.1, y + 3.0, 5.75), (1.2, 0.10, 0.10), (0.36, 0.36, 0.38, 1.0))
        make_box(f"Streetlight_{k}_Head_Glow", (5.7, y + 3.0, 5.66), (0.50, 0.26, 0.12), (1.0, 0.80, 0.50, 1.0))
    # Judgement Day at the curb: the beat-up maroon sedan; the frame shirt on
    # its rearview in the ch9 view; the cat hair is the sprite-scale detail
    make_car("JD", 5.15, -4.0, 4.70, (0.40, 0.18, 0.16, 1.0), along="Y")
    make_box("JD_Primer_Patch", (5.15 - 0.885, -3.4, 0.62), (0.006, 0.80, 0.30), (0.56, 0.56, 0.54, 1.0))
    make_box("JD_Rearview_Hang", (5.15, -3.0, 1.32), (0.20, 0.04, 0.06), (0.10, 0.10, 0.10, 1.0))
    # other cars parked along the far curb
    for k, (y, col) in enumerate(((-20.0, (0.30, 0.32, 0.36, 1.0)), (14.0, (0.70, 0.70, 0.68, 1.0)), (36.0, (0.20, 0.26, 0.34, 1.0)))):
        make_car(f"Parked_Far_{k}", 12.85, y, 4.6, col, along="Y")
    # the bus in the far lane, a blank ad on its side
    bx, by = 11.0, 22.0
    make_chamfer_box("Bus_Body" + NIGHT_ONLY, (bx, by, 1.75), (2.5, 12.0, 2.9), (0.86, 0.86, 0.82, 1.0), chamfer=0.15)
    make_box("Bus_Window_Band" + NIGHT_ONLY, (bx - 1.26, by + 0.5, 2.25), (0.02, 10.0, 1.0), (0.30, 0.34, 0.36, 1.0))
    make_box("Bus_Side_Ad_Blank" + NIGHT_ONLY, (bx - 1.27, by - 1.0, 1.10), (0.02, 5.0, 0.80), (0.96, 0.94, 0.86, 1.0))
    for s in (-1, 1):
        for t in (-1, 1):
            make_cyl(f"Bus_Wheel_{s:+d}{t:+d}" + NIGHT_ONLY, (bx + s * 1.1, by + t * 4.0, 0.50), 0.50, 0.30, (0.10, 0.10, 0.10, 1.0),
                     axis='X', segments=12)


def build_far_side():
    # the far side's frontages: shops and bars of two and three storeys,
    # their windows and signs lit (the neon the meld remembers)
    sign_cols = [(0.98, 0.30, 0.60, 1.0), (0.30, 0.90, 0.98, 1.0), (0.98, 0.76, 0.30, 1.0), (0.50, 0.98, 0.40, 1.0)]
    for k in range(13):
        y = -84.0 + k * 14.0
        h = 7.0 + (k % 3) * 3.5
        make_box(f"Far_Frontage_{k}", (24.0, y, h / 2.0), (12.0, 13.6, h), ((0.34, 0.30, 0.28, 1.0), (0.28, 0.30, 0.34, 1.0),
                                                                          (0.40, 0.34, 0.30, 1.0))[k % 3])
        make_box(f"Far_Shop_Window_Glow_{k}", (17.98, y, 1.6), (0.04, 9.0, 2.0), ((1.0, 0.86, 0.60, 1.0), (0.12, 0.12, 0.14, 1.0))[k % 4 == 3])
        make_box(f"Far_Sign_Glow_{k}", (17.94, y, 3.4), (0.08, 6.0, 0.9), sign_cols[k % 4])
        for j in range(3):
            make_box(f"Far_Upper_Window_Glow_{k}_{j}", (17.98, y - 4.0 + j * 4.0, 5.2), (0.04, 1.6, 1.4),
                     ((1.0, 0.82, 0.52, 1.0), (0.10, 0.10, 0.12, 1.0))[(j + k) % 2])
    make_box("Far_Rooftops_Band", (60.0, 0.0, 10.0), (0.2, 190.0, 20.0), (0.08, 0.08, 0.10, 1.0))
    # the night sky is the environment's own colour; the grey before
    # morning needs cards
    make_box("Sky_Grey_S__club_street_dawn", (8.0, -96.0, 40.0), (200.0, 0.2, 100.0), (0.46, 0.48, 0.52, 1.0))
    make_box("Sky_Grey_N__club_street_dawn", (8.0, 96.0, 40.0), (200.0, 0.2, 100.0), (0.46, 0.48, 0.52, 1.0))
    make_box("Sky_Grey_E__club_street_dawn", (90.0, 0.0, 40.0), (0.2, 200.0, 100.0), (0.54, 0.56, 0.60, 1.0))


def main():
    clear_scene()
    build_club_front()
    build_street()
    build_far_side()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/club_street.glb"))
    print(f"\n[build_club_street] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
