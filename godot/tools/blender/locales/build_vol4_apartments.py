"""vol4_apartments — two vol 4 apartment buildings (draft 1, 2026-10-28).

Both played on vol 7's 2052 Finn apartment over the kayak shop. Vol 4 is
undated, nothing later than its PDAs and newspapers (see build_carrie_city).
  influx_a: "He wakes to troubled dreams and curled up tight sleep"; "He
   fills the morning emptiness with hot coffee diluted to last through the
   weekend. The sun will not make an appearance for an hour yet. He showers
   and shaves and brushes and dresses"; "the apartment gates inhale to let
   him out, and he drives through suburban side streets"
                    → x 0..7, y 0..6: a one-bedroom in a gated suburban
                      complex, before dawn; the lot and the gate out the window
  what_sort_of: "Chess motioned for the boy to follow her into the
   elevator"; "The elevator hums and settles, slow as an old man."; "The
   elevator opened and Norman Todd followed Chess out into hallway, where an
   elderly man was walking their way with a garden trough in his hand."
                    → x 40..44, y 0..30: the old elevator cab and the long
                      hallway it opens on, morning through the end window

PROPOSED: both floor plans, the complex's gate and lot, the hallway's
length, its carpet and sconces, the trough set down by a door.

Blender: x east, y north, z up; Godot (x, z, -y).

(DRAFT 2, 2026-10-29: Earl, a stooped figure carrying the trough.)
DRAFT 3 targets: the influx bathroom
mirror; Chess's own door at the hallway's end; Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_blob, make_lathe,
                             join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings, make_window, make_blinds
from _props.furniture import make_bed, make_chair, make_table, make_lamp
from _props.figures import make_standing_figure

BEIGE = {"wall": (0.84, 0.80, 0.70, 1.0), "baseboard": (0.70, 0.66, 0.58, 1.0)}
HALL = {"wall": (0.76, 0.72, 0.60, 1.0), "baseboard": (0.36, 0.28, 0.22, 1.0)}


def build_influx():
    """A one-bedroom in a gated suburban complex: the bed and its tangled
    sheets, the kitchenette with the coffee maker, the bathroom door ajar,
    the window onto the lot and the gate, the lamps off but one."""
    x0, x1, y0, y1, H = 0.0, 7.0, 0.0, 6.0, 2.5
    make_floor("Influx_Floor", ((x0 + x1) / 2, (y0 + y1) / 2, 0.0), size_x=x1 - x0, size_y=y1 - y0,
               palette={"vinyl": (0.62, 0.58, 0.50, 1.0), "seam": (0.56, 0.52, 0.44, 1.0)})
    make_box("Influx_Carpet", (2.0, 3.6, 0.006), (3.6, 4.4, 0.01), (0.54, 0.52, 0.46, 1.0))
    make_box("Influx_Ceiling", ((x0 + x1) / 2, (y0 + y1) / 2, H + 0.04), (x1 - x0 + 0.3, y1 - y0 + 0.3, 0.08), (0.92, 0.90, 0.86, 1.0))
    make_wall_with_openings("Influx_Wall_N", ((x0 + x1) / 2, y1, 0.0), length=x1 - x0 + 0.16, height=H, thickness=0.16, axis='X',
                            palette=BEIGE, baseboard_face_sign=-1, openings=[(2.2, 1.35, 1.6, 1.2)])
    make_window("Influx_Window", (2.2, y1 - 0.08, 1.35), width=1.6, height=1.2, axis='X', room_dir=-1)
    make_blinds("Influx_Blinds", (2.2, y1 - 0.08, 1.35), width=1.6, height=1.2, axis='X', room_dir=-1)
    make_wall("Influx_Wall_S", ((x0 + x1) / 2, y0, 0.0), length=x1 - x0 + 0.16, height=H, thickness=0.16, axis='X', palette=BEIGE, baseboard_face_sign=+1)
    make_wall("Influx_Wall_W", (x0, (y0 + y1) / 2, 0.0), length=y1 - y0, height=H, thickness=0.16, axis='Y', palette=BEIGE, baseboard_face_sign=+1)
    make_wall_with_openings("Influx_Wall_E", (x1, (y0 + y1) / 2, 0.0), length=y1 - y0, height=H, thickness=0.16, axis='Y',
                            palette=BEIGE, baseboard_face_sign=-1, openings=[(1.2, 1.02, 0.86, 2.04)])
    make_box("Influx_Front_Door", (x1 - 0.06, 1.2, 1.02), (0.04, 0.84, 2.04), (0.70, 0.64, 0.52, 1.0))
    make_box("Influx_Deadbolt", (x1 - 0.10, 0.9, 1.10), (0.04, 0.06, 0.06), (0.70, 0.62, 0.30, 1.0))
    # the bed and its tangled sheets, the nightstand, the alarm clock's red figures
    make_bed("Influx_Bed", 1.2, 4.6, head="+Y", w=1.4, d=2.0, style="frame")
    make_box("Influx_Sheets_Tangle", (1.1, 3.9, 0.62), (1.2, 1.1, 0.12), (0.84, 0.86, 0.88, 1.0))
    make_box("Influx_Nightstand", (0.25, 5.5, 0.30), (0.40, 0.40, 0.60), (0.46, 0.36, 0.26, 1.0))
    make_box("Influx_Alarm_Clock", (0.25, 5.45, 0.66), (0.18, 0.08, 0.10), (0.12, 0.12, 0.12, 1.0))
    make_box("Influx_Alarm_Clock_Digits", (0.25, 5.40, 0.66), (0.12, 0.004, 0.04), (0.90, 0.12, 0.10, 1.0))
    make_lamp("Influx_Lamp", 0.25, 5.55, base_z=0.60, h=0.40)
    # the kitchenette on the south wall: counter, sink, the coffee maker, the mug
    make_box("Influx_Counter", (4.6, 0.35, 0.45), (2.8, 0.60, 0.90), (0.80, 0.78, 0.72, 1.0))
    make_box("Influx_Counter_Top", (4.6, 0.35, 0.92), (2.9, 0.64, 0.04), (0.56, 0.54, 0.50, 1.0))
    make_box("Influx_Sink", (5.4, 0.35, 0.90), (0.50, 0.40, 0.06), (0.70, 0.72, 0.74, 1.0))
    make_box("Influx_Upper_Cabinets", (4.6, 0.20, 1.85), (2.8, 0.34, 0.70), (0.80, 0.78, 0.72, 1.0))
    make_box("Coffee_Maker_Body", (3.9, 0.30, 1.10), (0.22, 0.24, 0.32), (0.12, 0.12, 0.12, 1.0))
    make_cyl("Coffee_Maker_Carafe", (3.9, 0.22, 1.02), 0.07, 0.14, (0.40, 0.26, 0.16, 1.0), segments=10)
    make_box("Coffee_Maker_Light", (3.98, 0.17, 1.00), (0.02, 0.004, 0.02), (0.96, 0.20, 0.10, 1.0))
    make_lathe("Influx_Mug", (4.3, 0.40, 0.94), [(0.0, 0.0), (0.04, 0.0), (0.042, 0.10), (0.0, 0.10)], (0.30, 0.42, 0.60, 1.0), segments=10)
    make_box("Influx_Fridge", (6.6, 0.40, 0.85), (0.70, 0.70, 1.70), (0.88, 0.88, 0.86, 1.0))
    make_table("Influx_Table", 4.6, 2.6, w=0.9, d=0.7)
    make_chair("Influx_Chair", 4.6, 2.0, yaw=0.0)
    make_box("Influx_Keys", (4.4, 2.7, 0.77), (0.08, 0.04, 0.01), (0.80, 0.78, 0.70, 1.0))
    make_box("Influx_Bathroom_Door_Ajar", (6.0, 5.3, 1.02), (0.84, 0.04, 2.04), (0.80, 0.78, 0.72, 1.0))
    # outside the window: the lot under sodium lamps, the gate, the next building
    make_box("Complex_Lot", (3.0, 18.0, -2.8), (30.0, 22.0, 0.04), (0.20, 0.20, 0.22, 1.0))
    for k in range(6):
        make_box(f"Complex_Lot_Stripe_{k}", (-4.0 + k * 2.8, 12.0, -2.77), (0.10, 4.6, 0.01), (0.86, 0.86, 0.82, 1.0))
    for k, (cx, col) in enumerate(((-2.0, (0.50, 0.50, 0.54, 1.0)), (3.6, (0.24, 0.30, 0.44, 1.0)), (6.4, (0.66, 0.62, 0.56, 1.0)))):
        make_box(f"Complex_Car_{k}", (cx, 12.0, -2.2), (1.8, 4.4, 1.1), col)
    for k in range(3):
        make_cyl(f"Complex_Lamp_{k}_Pole", (-6.0 + k * 9.0, 16.0, 0.6), 0.08, 6.8, (0.30, 0.30, 0.30, 1.0), segments=8)
        make_box(f"Complex_Lamp_{k}_Head", (-6.0 + k * 9.0, 16.0, 4.0), (0.40, 0.30, 0.12), (1.0, 0.70, 0.36, 1.0))
    make_box("Complex_Gate_Arm", (10.0, 22.0, -1.8), (4.0, 0.10, 0.10), (0.92, 0.90, 0.30, 1.0))
    for k in range(10):
        make_box(f"Complex_Gate_Bar_{k}", (6.0 + k * 0.5, 23.0, -1.6), (0.04, 0.04, 2.4), (0.20, 0.20, 0.22, 1.0))
    make_box("Complex_Building_Across", (2.0, 28.0, 2.0), (20.0, 8.0, 10.0), (0.66, 0.60, 0.50, 1.0))
    for k in range(8):
        for j in range(2):
            make_box(f"Complex_Across_Window_{k}_{j}", (-6.0 + k * 2.4, 23.95, 0.4 + j * 3.0), (1.2, 0.04, 1.1),
                     (1.0, 0.82, 0.54, 1.0) if (k + j) % 4 == 0 else (0.16, 0.18, 0.22, 1.0))


def build_chess_hall():
    """x 40..44: the elevator cab (y 0..2) opening on a long hallway north
    (y 2..30): carpet runner, sconces, numbered doors both sides, the window
    at the far end; a garden trough set down by a door."""
    hx0, hx1, H = 40.6, 42.6, 2.6
    # the elevator cab
    make_box("Elevator_Floor", (41.6, 1.0, -0.02), (1.6, 1.6, 0.04), (0.40, 0.34, 0.30, 1.0))
    make_box("Elevator_Ceiling", (41.6, 1.0, 2.36), (1.6, 1.6, 0.04), (0.82, 0.80, 0.74, 1.0))
    make_box("Elevator_Ceiling_Light", (41.6, 1.0, 2.33), (0.8, 0.6, 0.02), (1.0, 0.96, 0.86, 1.0))
    for s in (-1, 1):
        make_box(f"Elevator_Wall_{s:+d}", (41.6 + s * 0.82, 1.0, 1.18), (0.04, 1.6, 2.36), (0.60, 0.50, 0.36, 1.0))
    make_box("Elevator_Wall_Back", (41.6, 0.18, 1.18), (1.6, 0.04, 2.36), (0.60, 0.50, 0.36, 1.0))
    make_box("Elevator_Handrail", (41.6, 0.24, 0.92), (1.4, 0.04, 0.04), (0.74, 0.66, 0.40, 1.0))
    make_box("Elevator_Panel", (42.38, 1.4, 1.2), (0.03, 0.22, 0.60), (0.70, 0.66, 0.56, 1.0))
    for k in range(8):
        make_cyl(f"Elevator_Button_{k}", (42.36, 1.34 + (k % 2) * 0.10, 0.98 + (k // 2) * 0.11), 0.018, 0.01, (0.94, 0.90, 0.70, 1.0), segments=8, axis='X')
    for s in (-1, 1):
        make_box(f"Elevator_Door_Open_{s:+d}", (41.6 + s * 0.70, 1.82, 1.08), (0.40, 0.04, 2.16), (0.62, 0.62, 0.64, 1.0))
    # the hallway
    make_box("Hall_Floor", (41.6, 16.0, -0.02), (2.0, 28.0, 0.04), (0.46, 0.40, 0.34, 1.0))
    make_box("Hall_Runner", (41.6, 16.0, 0.004), (1.2, 27.0, 0.01), (0.46, 0.16, 0.18, 1.0))
    for k in range(13):
        make_box(f"Hall_Runner_Band_{k}", (41.6, 3.0 + k * 2.0, 0.006), (1.2, 0.10, 0.01), (0.70, 0.56, 0.30, 1.0))
    make_box("Hall_Ceiling", (41.6, 16.0, H + 0.04), (2.4, 28.4, 0.08), (0.86, 0.84, 0.78, 1.0))
    doors_w = [(4.0 + k * 4.0, 1.0, 0.9, 2.1) for k in range(6)]
    doors_e = [(5.6 + k * 4.0, 1.0, 0.9, 2.1) for k in range(6)]
    make_wall_with_openings("Hall_Wall_W", (hx0, 16.0, 0.0), length=28.0, height=H, thickness=0.16, axis='Y', palette=HALL,
                            baseboard_face_sign=+1, openings=doors_w)
    make_wall_with_openings("Hall_Wall_E", (hx1, 16.0, 0.0), length=28.0, height=H, thickness=0.16, axis='Y', palette=HALL,
                            baseboard_face_sign=-1, openings=doors_e)
    for side, x, lst in (("W", hx0 + 0.02, doors_w), ("E", hx1 - 0.02, doors_e)):
        for k, (dy, _z, w, h) in enumerate(lst):
            make_box(f"Hall_Door_{side}_{k}", (x, dy, 1.05), (0.05, w - 0.04, 2.08), (0.44, 0.30, 0.20, 1.0))
            make_box(f"Hall_Door_{side}_{k}_Number", (x + (0.04 if side == "W" else -0.04), dy, 1.62), (0.01, 0.14, 0.08), (0.80, 0.70, 0.40, 1.0))
            make_cyl(f"Hall_Door_{side}_{k}_Knob", (x + (0.05 if side == "W" else -0.05), dy + 0.32, 0.98), 0.03, 0.04, (0.74, 0.66, 0.40, 1.0), segments=8, axis='X')
    for k in range(7):
        y = 3.0 + k * 4.0
        for s, x in ((-1, hx0 + 0.10), (1, hx1 - 0.10)):
            make_cyl(f"Hall_Sconce_{k}_{s:+d}", (x, y, 1.95), 0.08, 0.14, (1.0, 0.88, 0.64, 1.0), segments=10)
    make_wall_with_openings("Hall_Wall_N", (41.6, 30.0, 0.0), length=2.16, height=H, thickness=0.16, axis='X', palette=HALL,
                            baseboard_face_sign=-1, openings=[(41.6, 1.5, 1.0, 1.4)])
    make_window("Hall_End_Window", (41.6, 29.92, 1.5), width=1.0, height=1.4, axis='X', room_dir=-1)
    make_box("Hall_End_Backdrop", (41.6, 40.0, 3.0), (30.0, 0.2, 20.0), (0.76, 0.82, 0.90, 1.0))
    # (draft 2, 2026-10-29) EARL coming down the hall toward the elevator,
    # "with a garden trough in his hand": an old man, a little stooped, a
    # cardigan, the trough held in front of him
    hx, hy, hz = make_standing_figure("Earl", 41.75, 11.5, heading=math.pi, h=1.68, coat=(0.52, 0.46, 0.36, 1.0),
                                      pants=(0.36, 0.34, 0.32, 1.0), hair=(0.82, 0.82, 0.80, 1.0), arms="front", stoop=0.12)
    # (on his hands, not round them: 2026-10-30)
    make_box("Garden_Trough", (hx, hy, hz + 0.19), (0.70, 0.26, 0.20), (0.56, 0.36, 0.24, 1.0))
    make_box("Garden_Trough_Soil", (hx, hy, hz + 0.295), (0.66, 0.22, 0.01), (0.30, 0.22, 0.16, 1.0))
    for k in range(4):
        make_blob(f"Garden_Trough_Plant_{k}", (hx - 0.24 + k * 0.16, hy, hz + 0.39), 0.07, (0.34, 0.56, 0.28, 1.0), noise=0.2, seed=k, squash=0.9)
    make_box("Hall_Doormat", (40.95, 12.0, 0.008), (0.40, 0.70, 0.01), (0.40, 0.34, 0.24, 1.0))


def main():
    clear_scene()
    build_influx()
    build_chess_hall()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/vol4_apartments.glb"))
    print(f"\n[build_vol4_apartments] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
