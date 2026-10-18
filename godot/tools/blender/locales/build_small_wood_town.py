"""small_wood_town — two rooms of vol 2's Small Wood: the radio studio of the
town's annual radio drama (December 1992) and Chuck's video store (February
2013) (draft 1, 2026-10-18).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
  night_lights: "the town's annual radio drama rendition of some sappy
   holiday pap our school librarian had written"; "I was to play Santa.";
   "when it came time to do a live reading on the air, I stumbled through
   my lines"                              → radio_studio (x 0..5)
   The text gives no room, no station name and no call letters: a plain
   small-town studio of 1992 (mics on boom arms, the script, headphones,
   the on-air lamp, the board through the control-room window).
  field_notes: "Small Wood still has a local video store."; "take the tape
   to the counter" / "leave it on the shelf"; "Chuck pulled the tape out
   from behind the counter."; "Need to get a VHS player"; "Weather is cold
   and clammy here on the coast"          → video_store_counter (x 40..48)
   A long-lived independent shop in 2013 that still rents VHS: older
   fixtures, hand-lettered shelf cards, no chain branding.

Blender: x east, y north, z up; Godot (x, z, -y).

DRAFT 2 targets: the station's outside and the town's one stoplight; the
store's front from the street; the tape's case as an image; Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_blob, make_lathe,
                             join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings
from _props.furniture import make_table, make_chair

T = 0.18
STUDIO_PAL = {"wall": (0.70, 0.66, 0.58, 1.0), "baseboard": (0.36, 0.30, 0.24, 1.0)}
STORE_PAL = {"wall": (0.84, 0.82, 0.76, 1.0), "baseboard": (0.40, 0.36, 0.30, 1.0)}
TRIM = (0.86, 0.84, 0.78, 1.0)


def build_studio():
    """x 0..5, y 0..4 the studio; y 4..7 the control room through the glass."""
    H = 2.6
    make_floor("Studio_Floor", (2.5, 3.5, 0.0), size_x=5.0, size_y=7.0,
               palette={"vinyl": (0.40, 0.34, 0.30, 1.0), "seam": (0.36, 0.30, 0.26, 1.0)})
    make_box("Studio_Ceil", (2.5, 3.5, H + 0.04), (5.4, 7.4, 0.08), (0.80, 0.78, 0.74, 1.0))
    make_wall_with_openings("Studio_Wall_S", (2.5, 0.0, 0), length=5.0 + T, height=H, thickness=T, axis='X', palette=STUDIO_PAL,
                            baseboard_face_sign=+1, openings=[(4.2, 1.0, 0.86, 2.0)])
    make_wall("Studio_Wall_N", (2.5, 7.0, 0), length=5.0 + T, height=H, thickness=T, axis='X', palette=STUDIO_PAL, baseboard_face_sign=-1)
    make_wall("Studio_Wall_W", (0.0, 3.5, 0), length=7.0 - T, height=H, thickness=T, axis='Y', palette=STUDIO_PAL, baseboard_face_sign=+1)
    make_wall("Studio_Wall_E", (5.0, 3.5, 0), length=7.0 - T, height=H, thickness=T, axis='Y', palette=STUDIO_PAL, baseboard_face_sign=-1)
    make_wall_with_openings("Studio_Glass_Wall", (2.5, 4.0, 0), length=5.0 - T, height=H, thickness=0.16, axis='X', palette=STUDIO_PAL,
                            baseboard_face_sign=+1, openings=[(2.5, 1.45, 2.0, 0.9), (4.3, 1.0, 0.8, 2.0)])
    for s in (-1, 1):
        make_box(f"Control_Window_Frame_Jamb_{s:+d}", (2.5 + s * 0.97, 4.0, 1.45), (0.06, 0.18, 0.9), (0.30, 0.28, 0.26, 1.0))
    for zz in (1.03, 1.87):
        make_box(f"Control_Window_Frame_Rail_{zz:.2f}", (2.5, 4.0, zz), (1.88, 0.18, 0.06), (0.30, 0.28, 0.26, 1.0))
    make_box("Control_Door_Shut", (4.3, 4.0, 1.0), (0.78, 0.04, 2.0), (0.50, 0.40, 0.30, 1.0))
    # the acoustic panels (fabric squares) on the studio walls
    k = 0
    for y in (0.8, 1.9, 3.0):
        for z in (1.1, 1.9):
            make_box(f"Acoustic_Panel_W_{k}", (0.09 + 0.025, y, z), (0.05, 0.9, 0.7), ((0.36, 0.34, 0.40, 1.0), (0.40, 0.30, 0.28, 1.0))[k % 2])
            make_box(f"Acoustic_Panel_E_{k}", (4.91 - 0.025, y, z), (0.05, 0.9, 0.7), ((0.40, 0.30, 0.28, 1.0), (0.36, 0.34, 0.40, 1.0))[k % 2])
            k += 1
    # the table, the three mics on boom arms, the script, the headphones
    tx, ty = 2.5, 2.0
    make_table("Studio_Table", tx, ty, w=2.4, d=1.0, h=0.74, wood=(0.36, 0.28, 0.20, 1.0))
    top = 0.74
    for i, x in enumerate((tx - 0.8, tx, tx + 0.8)):
        make_cyl(f"Mic_Boom_Clamp_{i}", (x, ty + 0.46, top + 0.04), 0.03, 0.08, (0.20, 0.20, 0.22, 1.0), segments=8)
        make_box(f"Mic_Boom_Post_{i}", (x, ty + 0.46, top + 0.28), (0.02, 0.02, 0.40), (0.20, 0.20, 0.22, 1.0))
        make_rot_box(f"Mic_Boom_Arm_{i}", (x, ty + 0.24, top + 0.52), (0.02, 0.50, 0.02), (0.20, 0.20, 0.22, 1.0), roll=0.4)
        make_chamfer_box(f"Mic_Head_{i}", (x, ty + 0.02, top + 0.40), (0.07, 0.14, 0.07), (0.30, 0.30, 0.32, 1.0), chamfer=0.02)
        make_box(f"Script_Page_{i}", (x, ty - 0.22, top + 0.003), (0.21, 0.28, 0.004), (0.94, 0.94, 0.90, 1.0))
        make_box(f"Script_Page_Under_{i}", (x + 0.02, ty - 0.20, top + 0.0005), (0.21, 0.28, 0.001), (0.90, 0.90, 0.86, 1.0))
        make_blob(f"Headphones_{i}", (x - 0.30, ty - 0.10, top + 0.04), 0.08, (0.12, 0.12, 0.12, 1.0), noise=0.0, seed=i, squash=0.5)
        make_chair(f"Studio_Chair_{i}", x, ty - 0.80, yaw=0.0, wood=(0.30, 0.30, 0.32, 1.0), seat_col=(0.40, 0.30, 0.26, 1.0))
    make_cyl("Water_Glass", (tx + 1.05, ty - 0.30, top + 0.06), 0.035, 0.12, (0.80, 0.84, 0.86, 1.0), segments=10)
    # the on-air lamp over the glass, the clock
    make_box("On_Air_Lamp_Mounted_Glow", (2.5, 4.0 - 0.10, 2.25), (0.50, 0.06, 0.16), (0.96, 0.20, 0.16, 1.0))
    make_cyl("Studio_Clock_Mounted", (0.8, 4.0 - 0.09, 2.15), 0.15, 0.02, (0.92, 0.92, 0.88, 1.0), axis='Y', segments=16)
    # the control room beyond: the board, its reels and carts, the engineer's chair
    make_box("Board_Desk", (2.5, 5.0, 0.40), (2.6, 0.80, 0.80), (0.34, 0.30, 0.28, 1.0))
    make_rot_box("Board_Console", (2.5, 5.0, 0.88), (2.4, 0.70, 0.12), (0.24, 0.24, 0.26, 1.0), roll=-0.15)
    for k in range(16):
        make_box(f"Board_Fader_{k}", (1.5 + k * 0.13, 4.9, 0.955), (0.03, 0.10, 0.012), (0.80, 0.78, 0.70, 1.0))
    make_box("Reel_Deck", (0.9, 6.5, 0.70), (0.80, 0.60, 1.40), (0.30, 0.30, 0.32, 1.0))
    for s in (-1, 1):
        make_cyl(f"Reel_{s:+d}", (0.9 + s * 0.20, 6.5 - 0.31, 1.15), 0.16, 0.02, (0.50, 0.48, 0.44, 1.0), axis='Y', segments=16)
    make_box("Cart_Rack", (4.2, 6.6, 1.0), (1.20, 0.40, 2.0), (0.40, 0.34, 0.28, 1.0))
    make_chair("Engineer_Chair", 2.5, 5.75, yaw=math.pi, wood=(0.30, 0.30, 0.32, 1.0), seat_col=(0.24, 0.24, 0.30, 1.0))


def build_store():
    """x 40..48, y 0..10: the front windows S, the aisles of tapes, the
    counter at y 7 with the stock behind it to the N wall."""
    H = 2.9
    x0, x1, y0, y1 = 40.0, 48.0, 0.0, 10.0
    make_floor("Store_Floor", (44.0, 5.0, 0.0), size_x=8.0, size_y=10.0,
               palette={"vinyl": (0.66, 0.64, 0.58, 1.0), "seam": (0.58, 0.56, 0.50, 1.0)})
    make_box("Store_Ceil", (44.0, 5.0, H + 0.04), (8.4, 10.4, 0.08), (0.88, 0.88, 0.86, 1.0))
    for k in range(3):
        make_box(f"Store_Fluorescent_Glow_{k}", (44.0, 2.0 + k * 3.0, H - 0.04), (0.30, 1.4, 0.06), (0.96, 0.98, 0.96, 1.0))
    make_wall_with_openings("Store_Wall_S", (44.0, y0, 0), length=8.0 + T, height=H, thickness=T, axis='X', palette=STORE_PAL,
                            baseboard_face_sign=+1, openings=[(41.8, 1.4, 2.6, 1.9), (46.8, 1.05, 1.0, 2.1)])
    make_wall("Store_Wall_N", (44.0, y1, 0), length=8.0 + T, height=H, thickness=T, axis='X', palette=STORE_PAL, baseboard_face_sign=-1)
    make_wall("Store_Wall_W", (x0, 5.0, 0), length=10.0 - T, height=H, thickness=T, axis='Y', palette=STORE_PAL, baseboard_face_sign=+1)
    make_wall("Store_Wall_E", (x1, 5.0, 0), length=10.0 - T, height=H, thickness=T, axis='Y', palette=STORE_PAL, baseboard_face_sign=-1)
    for s in (-1, 1):
        make_box(f"Store_Window_Frame_Jamb_{s:+d}", (41.8 + s * 1.27, y0, 1.4), (0.06, T + 0.02, 1.9), TRIM)
    for zz in (0.48, 2.32):
        make_box(f"Store_Window_Frame_Rail_{zz:.2f}", (41.8, y0, zz), (2.48, T + 0.02, 0.06), TRIM)
    make_box("Store_Door_Glass_Frame", (46.8, y0, 1.05), (0.98, 0.05, 2.08), (0.30, 0.30, 0.30, 1.0))
    make_box("Store_Door_Glass_Pane", (46.8, y0, 1.15), (0.80, 0.02, 1.70), (0.62, 0.66, 0.68, 1.0))
    make_box("Store_Hours_Card_Mounted", (46.8, y0 - 0.025, 1.50), (0.20, 0.01, 0.14), (0.94, 0.92, 0.84, 1.0))
    # the counter at y 7 (x 41..46), the register, the stock behind it
    make_box("Counter_Front", (43.5, 7.0, 0.50), (5.0, 0.60, 1.00), (0.44, 0.34, 0.24, 1.0))
    make_box("Counter_Top", (43.5, 7.0, 1.02), (5.1, 0.70, 0.04), (0.66, 0.60, 0.50, 1.0))
    make_chamfer_box("Register", (42.4, 7.05, 1.16), (0.40, 0.36, 0.24), (0.30, 0.30, 0.30, 1.0), chamfer=0.03)
    make_box("Melody_Tape_Case", (44.2, 6.9, 1.06), (0.12, 0.20, 0.03), (0.16, 0.20, 0.34, 1.0))
    make_box("Melody_Tape_Label", (44.2, 6.9, 1.0765), (0.10, 0.16, 0.003), (0.86, 0.80, 0.62, 1.0))
    make_box("Rental_Card_Box", (45.6, 7.0, 1.10), (0.24, 0.16, 0.12), (0.70, 0.58, 0.40, 1.0))
    make_box("Return_Slot_Box", (46.6, 7.0, 0.50), (0.60, 0.50, 1.00), (0.44, 0.34, 0.24, 1.0))
    for lvl in range(5):
        make_box(f"Back_Stock_Shelf_{lvl}", (44.0, y1 - 0.09 - 0.20, 0.30 + lvl * 0.42), (6.8, 0.40, 0.03), (0.52, 0.44, 0.32, 1.0))
        for k in range(30):
            make_box(f"Back_Stock_Tape_Stock_{lvl}_{k}", (40.9 + k * 0.21, y1 - 0.09 - 0.22, 0.30 + lvl * 0.42 + 0.115),
                     (0.03, 0.19, 0.20), ((0.16, 0.16, 0.18, 1.0), (0.80, 0.78, 0.72, 1.0), (0.30, 0.26, 0.40, 1.0))[(k + lvl) % 3])
    for s in (-1, 1):
        make_box(f"Back_Stock_Upright_{s:+d}", (44.0 + s * 3.42, y1 - 0.09 - 0.20, 1.10), (0.04, 0.40, 2.20), (0.46, 0.38, 0.28, 1.0))
    # the aisles out front: two double-sided shelves, hand-lettered cards
    for a, x in enumerate((42.2, 45.8)):
        make_box(f"Aisle_Gondola_{a}", (x, 3.6, 0.80), (0.60, 4.0, 1.60), (0.52, 0.44, 0.32, 1.0))
        for lvl in range(4):
            for side in (-1, 1):
                for k in range(16):
                    make_box(f"Aisle_Tape_Stock_{a}_{lvl}_{side:+d}_{k}", (x + side * 0.315, 1.8 + k * 0.24, 0.30 + lvl * 0.36),
                             (0.03, 0.19, 0.20), ((0.20, 0.24, 0.40, 1.0), (0.70, 0.20, 0.18, 1.0), (0.86, 0.84, 0.78, 1.0),
                                                  (0.16, 0.16, 0.18, 1.0))[(k + lvl + a) % 4])
            make_box(f"Aisle_Shelf_Card_{a}_{lvl}", (x - 0.335, 2.4 + (lvl % 2) * 2.0, 0.20 + lvl * 0.36), (0.004, 0.18, 0.06),
                     (0.96, 0.94, 0.86, 1.0))
    for k in range(6):
        make_box(f"Wall_Tape_Shelf_W_{k}", (x0 + 0.09 + 0.15, 1.2 + k * 0.9, 1.30), (0.30, 0.80, 2.4), (0.52, 0.44, 0.32, 1.0))
        for lvl in range(5):
            make_box(f"Wall_Tape_Row_Stock_{k}_{lvl}", (x0 + 0.09 + 0.31, 1.2 + k * 0.9, 0.40 + lvl * 0.42), (0.02, 0.74, 0.20),
                     ((0.30, 0.30, 0.36, 1.0), (0.60, 0.30, 0.24, 1.0))[(k + lvl) % 2])
    make_box("Store_Mat", (46.8, 0.7, 0.006), (1.2, 0.8, 0.012), (0.26, 0.26, 0.28, 1.0))
    # outside the window: the wet street, the grey February coast
    make_box("Street_Asphalt_Wet", (44.0, -8.0, -0.02), (40.0, 10.0, 0.04), (0.26, 0.26, 0.28, 1.0))
    make_box("Sidewalk", (44.0, -1.5, 0.06), (40.0, 3.0, 0.12), (0.54, 0.54, 0.52, 1.0))
    make_box("Across_Street_Facade", (44.0, -14.0, 3.0), (40.0, 0.4, 6.0), (0.56, 0.52, 0.46, 1.0))
    make_box("Sky_Grey_S", (44.0, -60.0, 20.0), (200.0, 0.2, 80.0), (0.66, 0.68, 0.70, 1.0))


def main():
    clear_scene()
    build_studio()
    build_store()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/small_wood_town.glb"))
    print(f"\n[build_small_wood_town] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
