"""Diego's Bedroom — vol6 — Diego Ramos, at his grandmother Graciela's
house, 892 Ashberry Drive.

DRAFT 5 (2026-10-09, the overnight run): THE WRONG DRESSING. Drafts 1-4
made this "a shrine to the pitch" — jerseys and a scarf on the wall, a
Mexico flag, striker posters, a shelf of trophies, a soccer ball and
cleats. Nothing in vol6 says Diego plays; the prose says the opposite of
a shrine (ch0): "A photograph of Sam that he printed at the Walgreens
on Fifth, tucked into the corner of the mirror, which is the only
decoration in the room besides a periodic table he has had since seventh
grade and a calendar he stopped updating in March." And:
  "The bed has been slept in but not recently. The sheets are pushed to
   one side." · "On the floor near the desk there is an open duffel bag
   — the green one he has had since eighth grade, with the broken zipper
   on the front pocket ... The bag is half-packed. Three shirts, a phone
   charger, a pair of boots." · "On the desk: a water glass with a finger
   of water left in it. A textbook for a class he is not taking anymore."
   (ch0) · "He pulls the regular curtains in his bedroom — not the
   blackout ones, those are for the Saturday sleep" · "The clock on the
   dresser says three eleven." · "He writes at the small desk that has
   been his desk since he was nine ... He sets the envelope on the
   corner of the desk." (ch18) · "The fan, on the ceiling, clicks on the
   third rotation." (ch16) · "He has the laptop open." (ch23)
Rebuilt as that room, plain and specific: the twin bed with the sheets
pushed aside, the small desk (laptop, the water glass, the textbook, the
blue pen, the letter and its envelope on the corner), the dresser with
the clock and the mirror with SAM'S PHOTOGRAPH in its corner, the
periodic table, the calendar on March, the window's two curtains (the
blackout pair his mother drove up from San Antonio to install, and the
regular pair), the ceiling fan, the half-packed green duffel by the
desk, the closet, his door.
Coordinate frame: Blender Z-up. y=0 is the door (S) wall; the window is
in the N wall over the back yard. glTF export remaps to Godot (x, z, -y).

Draft 6 targets: the hall and Graciela's room (vol6 ch0's next beat);
the blackout curtains DRAWN as a per-scene state; Deck framing.
"""
import math
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_lathe, make_tube, make_rot_box, make_blob, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_wall_with_openings
from _props.views import make_view
from _props.furniture import make_bed, make_chair, make_lamp
from _props.detail import make_traffic_wear, make_floor_stain, make_light_switch, make_wall_outlet

ROOM_W = 4.4; ROOM_D = 4.8; CEIL = 2.6   # draft 5 (2026-10-09): was 4.0 x 4.5
XW, XE, YS, YN = -ROOM_W / 2.0 + 0.10, ROOM_W / 2.0 - 0.10, 0.10, ROOM_D - 0.10
PAL_WALL = {"wall": (0.80, 0.78, 0.70, 1.0), "baseboard": (0.86, 0.84, 0.78, 1.0)}   # his grandmother's beige
COL_FLOOR = (0.60, 0.50, 0.38, 1.0); COL_SEAM = (0.46, 0.36, 0.26, 1.0)
COL_WOOD = (0.50, 0.38, 0.26, 1.0); COL_WOOD_DK = (0.40, 0.30, 0.20, 1.0)
COL_WHITE = (0.90, 0.88, 0.84, 1.0)
DOOR = (1.30, 1.04, 0.86, 2.08)
WIN = (0.0, 1.50, 1.20, 1.10)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_E", (ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL, axis='X', palette=PAL_WALL,
                            baseboard_face_sign=-1, openings=[WIN])
    make_wall_with_openings("Wall_S", (0.0, 0.0, 0), length=ROOM_W + 0.4, height=CEIL, axis='X', palette=PAL_WALL,
                            baseboard_face_sign=+1, openings=[DOOR])
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
                 with_grid=False, with_stains=False, palette={"tile": (0.92, 0.90, 0.86, 1.0)})
    for nm, ax, length, wx, wy in [("Crown_W", 'Y', ROOM_D, XW, ROOM_D / 2.0), ("Crown_E", 'Y', ROOM_D, XE, ROOM_D / 2.0),
                                    ("Crown_N", 'X', ROOM_W, 0.0, YN), ("Crown_S", 'X', ROOM_W, 0.0, YS)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WHITE})
    dx = DOOR[0]
    make_box("Bedroom_Door_Leaf", (dx, 0.0, 1.035), (0.84, 0.045, 2.07), COL_WHITE)
    make_cyl("Bedroom_Door_Knob", (dx - 0.32, 0.05, 0.98), 0.03, 0.05, (0.66, 0.60, 0.42, 1.0), segments=10, axis='Y')
    for nm, x in (("A", dx - DOOR[2] / 2.0 - 0.035), ("B", dx + DOOR[2] / 2.0 + 0.035)):
        make_box(f"Bedroom_Door_Casing_{nm}", (x, YS + 0.01, 1.07), (0.07, 0.02, 2.14), COL_WHITE)
    make_box("Bedroom_Door_Casing_Head", (dx, YS + 0.01, 2.115), (DOOR[2] + 0.14, 0.02, 0.07), COL_WHITE)
    make_light_switch("Switch_Door", (dx + 0.62, 0.0), axis='X', face_sign=1, z=1.20)


def build_window():
    """The window over the back yard: the frame, the glass; the REGULAR
    curtains half-drawn on the inner rod, the BLACKOUT pair pushed aside on
    the outer one ("not the blackout ones, those are for the Saturday
    sleep")."""
    wx, wz, ww, wh = WIN
    for nm, c, sz in (("Head", (wx, ROOM_D, wz + wh / 2.0 - 0.035), (ww, 0.10, 0.07)),
                      ("Sill", (wx, ROOM_D, wz - wh / 2.0 + 0.035), (ww, 0.10, 0.07)),
                      ("JambW", (wx - ww / 2.0 + 0.035, ROOM_D, wz), (0.07, 0.10, wh - 0.14)),
                      ("JambE", (wx + ww / 2.0 - 0.035, ROOM_D, wz), (0.07, 0.10, wh - 0.14)),
                      ("Mullion", (wx, ROOM_D, wz), (0.04, 0.06, wh - 0.14))):
        make_box(f"Window_Frame_{nm}", c, sz, COL_WHITE)
    make_box("Window_Glass", (wx, ROOM_D, wz), (ww - 0.14, 0.01, wh - 0.14), (0.62, 0.70, 0.78, 0.45))
    make_box("Window_Stool", (wx, YN - 0.07, wz - wh / 2.0 - 0.015), (ww + 0.16, 0.16, 0.03), COL_WHITE)
    rz = wz + wh / 2.0 + 0.16
    for nm, oy, ext in (("Outer", 0.07, 0.95), ("Inner", 0.16, 0.85)):
        make_cyl(f"Curtain_Rod_{nm}", (wx, YN - oy, rz + (0.04 if nm == "Outer" else 0.0)), 0.011, ww + 2 * ext - 0.4, (0.40, 0.38, 0.34, 1.0), segments=6, axis='X')
    for k, x in enumerate((wx - ww / 2.0 - 0.38, wx + ww / 2.0 + 0.38)):
        make_box(f"Curtain_Rod_Bracket_{k}", (x, YN - 0.08, rz + 0.02), (0.02, 0.16, 0.02), (0.40, 0.38, 0.34, 1.0))
    # the blackout pair, pushed to both sides on the outer rod
    for nm, x in (("W", wx - ww / 2.0 - 0.20), ("E", wx + ww / 2.0 + 0.20)):
        make_box(f"Curtain_Blackout_{nm}", (x, YN - 0.07, (rz + 0.03 + 0.25) / 2.0), (0.34, 0.05, rz + 0.03 - 0.25), (0.16, 0.18, 0.24, 1.0))
    # the regular pair on the inner rod, one panel half across the glass
    make_box("Curtain_Regular_W", (wx - 0.30, YN - 0.16, (rz - 0.012 + 0.90) / 2.0), (0.52, 0.02, rz - 0.012 - 0.90), (0.86, 0.80, 0.66, 1.0))
    make_box("Curtain_Regular_E", (wx + ww / 2.0 + 0.10, YN - 0.16, (rz - 0.012 + 0.90) / 2.0), (0.30, 0.04, rz - 0.012 - 0.90), (0.86, 0.80, 0.66, 1.0))
    make_view("View_N", "N", ROOM_D, 0.0, kind="back", ground_z=0.0, seed=11)


def build_fan():
    """"The fan, on the ceiling, clicks on the third rotation." """
    fx, fy = 0.0, 2.5
    make_cyl("Fan_Canopy", (fx, fy, CEIL - 0.04), 0.08, 0.08, COL_WHITE, segments=12)
    make_cyl("Fan_Downrod", (fx, fy, CEIL - 0.20), 0.015, 0.26, COL_WHITE, segments=6)
    make_cyl("Fan_Motor", (fx, fy, CEIL - 0.37), 0.13, 0.10, (0.70, 0.66, 0.58, 1.0), segments=14)
    for k in range(4):
        a = math.radians(k * 90.0 + 20.0)
        make_rot_box(f"Fan_Blade_{k}", (fx + 0.42 * math.cos(a), fy + 0.42 * math.sin(a), CEIL - 0.37), (0.56, 0.13, 0.012), COL_WOOD_DK, yaw=a)
    make_cyl("Fan_Pull_Chain", (fx + 0.06, fy, CEIL - 0.52), 0.003, 0.20, (0.70, 0.66, 0.50, 1.0), segments=4)
    make_cyl("Fan_Pull_Fob", (fx + 0.06, fy, CEIL - 0.63), 0.012, 0.03, (0.70, 0.66, 0.50, 1.0), segments=6)


def build_bed():
    """The twin bed, head to the W wall, the sheets pushed to one side."""
    bx, by = XW + 1.02, 2.95
    make_bed("Bed", bx, by, head="-X", w=1.00, d=2.0, style="frame", frame_col=COL_WOOD,
             mattress_col=(0.88, 0.86, 0.82, 1.0), sheet_col=(0.84, 0.86, 0.88, 1.0), blanket_col=(0.40, 0.46, 0.54, 1.0),
             pillow_col=(0.90, 0.90, 0.88, 1.0), pillows=1, made=False)
    nx, ny = XW + 0.24, by + 0.80
    make_box("Nightstand", (nx, ny, 0.28), (0.40, 0.38, 0.56), COL_WOOD)
    make_box("Nightstand_Drawer", (nx + 0.205, ny, 0.44), (0.012, 0.32, 0.12), COL_WOOD_DK)
    make_box("Nightstand_Phone_Charger", (nx + 0.05, ny + 0.08, 0.565), (0.06, 0.04, 0.01), (0.90, 0.90, 0.88, 1.0))
    make_wall_outlet("Outlet_Bed", (-ROOM_W / 2.0, ny + 0.32), axis='Y', face_sign=1)


def build_desk():
    """"the small desk that has been his desk since he was nine", on the
    E wall: the laptop, the water glass with a finger of water, the
    textbook for a class he is not taking anymore, the blue pen, the
    letter and its envelope on the corner, a lamp."""
    dx, dy, dz = XE - 0.27, 2.95, 0.72
    make_box("Desk_Top", (dx, dy, dz - 0.015), (0.54, 1.00, 0.03), COL_WOOD)
    for li, (ox, oy) in enumerate(((-0.24, -0.46), (0.24, -0.46), (-0.24, 0.46), (0.24, 0.46))):
        make_box(f"Desk_Leg_{li}", (dx + ox, dy + oy, (dz - 0.03) / 2.0), (0.04, 0.04, dz - 0.03), COL_WOOD_DK)
    make_box("Desk_Drawer", (dx, dy + 0.20, dz - 0.08), (0.48, 0.50, 0.10), COL_WOOD_DK)
    make_box("Desk_Drawer_Front", (dx - 0.245, dy + 0.20, dz - 0.08), (0.01, 0.46, 0.08), COL_WOOD)
    make_chair("Desk_Chair", dx - 0.58, dy, yaw=-math.pi / 2.0, wood=COL_WOOD, w=0.40)
    make_box("Laptop_Base", (dx - 0.04, dy - 0.05, dz + 0.01), (0.30, 0.22, 0.02), (0.20, 0.20, 0.22, 1.0))
    make_rot_box("Laptop_Lid", (dx + 0.10, dy - 0.05, dz + 0.12), (0.02, 0.30, 0.21), (0.20, 0.20, 0.22, 1.0), roll=0.0, pitch=0.0, yaw=0.0)
    make_box("Laptop_Screen", (dx + 0.088, dy - 0.05, dz + 0.12), (0.004, 0.27, 0.18), (0.36, 0.44, 0.56, 1.0))
    make_lathe("Water_Glass", (dx - 0.16, dy + 0.40, dz), [(0.0, 0.0), (0.032, 0.0), (0.036, 0.11), (0.033, 0.11), (0.029, 0.006), (0.0, 0.006)], (0.80, 0.86, 0.90, 0.6), segments=10)
    make_cyl("Water_Glass_Water", (dx - 0.16, dy + 0.40, dz + 0.02), 0.029, 0.025, (0.62, 0.74, 0.82, 0.7), segments=10)
    make_box("Textbook", (dx + 0.02, dy + 0.34, dz + 0.025), (0.22, 0.28, 0.05), (0.30, 0.46, 0.36, 1.0))
    make_box("Letter_Paper", (dx - 0.13, dy - 0.32, dz + 0.001), (0.21, 0.28, 0.002), (0.96, 0.96, 0.94, 1.0))
    # "The letter is fourteen lines." — in the blue pen
    for k in range(14):
        ln = 0.15 - 0.05 * ((k * 7) % 3) / 2.0 if k not in (0, 13) else 0.06
        make_box(f"Letter_Line_{k}", (dx - 0.13 - (0.15 - ln) / 2.0, dy - 0.40 + k * 0.016, dz + 0.0025), (ln, 0.004, 0.0005), (0.24, 0.30, 0.56, 1.0))
    make_box("Blue_Pen", (dx - 0.02, dy - 0.32, dz + 0.006), (0.01, 0.14, 0.01), (0.18, 0.26, 0.62, 1.0))
    make_box("Letter_Envelope", (dx + 0.17, dy - 0.42, dz + 0.0025), (0.22, 0.11, 0.005), (0.94, 0.93, 0.90, 1.0))
    make_lamp("Lamp", dx + 0.12, dy + 0.12, base_z=dz, h=0.42, shade_col=(0.86, 0.82, 0.70, 1.0), body_col=(0.30, 0.30, 0.32, 1.0))
    make_wall_outlet("Outlet_Desk", (ROOM_W / 2.0, dy - 0.60), axis='Y', face_sign=-1)
    # THE PERIODIC TABLE "he has had since seventh grade", over the desk
    pz = 1.62
    make_box("Periodic_Table", (XE - 0.006, dy, pz), (0.012, 0.92, 0.62), (0.94, 0.92, 0.86, 1.0))
    for r in range(7):
        for c in range(18):
            if r == 0 and 0 < c < 17: continue
            if r in (1, 2) and 1 < c < 12: continue
            col = ((0.86, 0.50, 0.40, 1.0) if c < 2 else (0.52, 0.66, 0.82, 1.0) if c < 12 else (0.62, 0.78, 0.52, 1.0) if c < 17 else (0.86, 0.76, 0.46, 1.0))
            make_box(f"Periodic_Cell_{r}_{c}", (XE - 0.013, dy - 0.42 + c * 0.049, pz + 0.22 - r * 0.06), (0.002, 0.042, 0.052), col)
    # the calendar he stopped updating in March, by the door
    make_box("Calendar_March", (XE - 0.006, 0.95, 1.55), (0.012, 0.32, 0.46), (0.94, 0.92, 0.88, 1.0))
    make_box("Calendar_March_Photo", (XE - 0.013, 0.95, 1.67), (0.002, 0.28, 0.18), (0.46, 0.60, 0.70, 1.0))
    make_box("Calendar_March_Grid", (XE - 0.013, 0.95, 1.44), (0.002, 0.28, 0.18), (0.70, 0.68, 0.64, 1.0))


def build_dresser():
    """The dresser on the S wall W of the door: the clock ("three eleven"),
    the mirror with SAM'S PHOTOGRAPH tucked in its corner."""
    ddx, ddy = -0.85, YS + 0.24
    make_box("Dresser", (ddx, ddy, 0.42), (0.96, 0.46, 0.84), COL_WOOD)
    for i in range(3):
        make_box(f"Dresser_Drawer_{i}", (ddx, ddy + 0.235, 0.15 + i * 0.25), (0.88, 0.012, 0.21), COL_WOOD_DK)
        make_box(f"Dresser_Drawer_{i}_Pull", (ddx, ddy + 0.245, 0.18 + i * 0.25), (0.12, 0.012, 0.02), (0.62, 0.58, 0.48, 1.0))
    make_box("Dresser_Clock", (ddx + 0.30, ddy + 0.06, 0.885), (0.16, 0.08, 0.09), (0.16, 0.16, 0.18, 1.0))
    make_box("Dresser_Clock_Digits", (ddx + 0.30, ddy + 0.101, 0.885), (0.11, 0.002, 0.04), (0.86, 0.26, 0.20, 1.0))
    make_box("Dresser_Wallet", (ddx - 0.25, ddy + 0.05, 0.852), (0.11, 0.08, 0.024), (0.24, 0.18, 0.12, 1.0))
    make_box("Mirror_Frame", (ddx, YS + 0.015, 1.40), (0.62, 0.03, 0.80), COL_WOOD_DK)
    make_box("Mirror_Glass", (ddx, YS + 0.032, 1.40), (0.54, 0.004, 0.72), (0.70, 0.76, 0.82, 1.0))
    # the photograph of Sam, printed at the Walgreens on Fifth, tucked in the corner
    make_rot_box("Sam_Photo", (ddx + 0.21, YS + 0.037, 1.70), (0.09, 0.003, 0.13), (0.94, 0.92, 0.88, 1.0), yaw=0.0, roll=0.0, pitch=0.0)
    make_box("Sam_Photo_Image", (ddx + 0.21, YS + 0.0395, 1.705), (0.075, 0.002, 0.10), (0.62, 0.56, 0.48, 1.0))


def build_closet_duffel():
    """The closet on the W wall's S end (bifold, shut); the green duffel
    by the desk — open, half-packed, the broken front-pocket zipper."""
    cy0, cy1 = YS + 0.30, YS + 1.50
    for k in range(4):
        y = cy0 + (cy1 - cy0) * (k + 0.5) / 4.0
        make_box(f"Closet_Door_Leaf_{k}", (XW + 0.02, y, 1.04), (0.03, (cy1 - cy0) / 4.0 - 0.01, 2.06), COL_WHITE)
    make_box("Closet_Casing_Head", (XW + 0.01, (cy0 + cy1) / 2.0, 2.11), (0.02, cy1 - cy0 + 0.14, 0.07), COL_WHITE)
    gx, gy = XE - 0.75, 1.75
    green = (0.26, 0.40, 0.26, 1.0)
    make_blob("Duffel_Body", (gx, gy, 0.17), 0.32, green, noise=0.12, seed=9, squash=0.55)
    make_box("Duffel_Front_Pocket", (gx, gy - 0.24, 0.16), (0.30, 0.03, 0.16), (0.22, 0.34, 0.22, 1.0))
    make_box("Duffel_Broken_Zip", (gx + 0.05, gy - 0.257, 0.22), (0.20, 0.006, 0.01), (0.66, 0.62, 0.50, 1.0))
    make_box("Duffel_Shirt_0", (gx - 0.08, gy + 0.02, 0.33), (0.26, 0.20, 0.04), (0.84, 0.84, 0.82, 1.0))
    make_box("Duffel_Shirt_1", (gx + 0.06, gy + 0.05, 0.36), (0.24, 0.18, 0.03), (0.30, 0.34, 0.46, 1.0))
    make_tube("Duffel_Charger_Cord", [(gx + 0.14, gy - 0.02, 0.37), (gx + 0.22, gy - 0.10, 0.35), (gx + 0.30, gy - 0.05, 0.02)], 0.004, COL_WHITE, segments=4)
    for k, ox in enumerate((-0.10, 0.10)):
        make_box(f"Duffel_Boot_{k}", (gx + ox + 0.48, gy + 0.10, 0.12), (0.12, 0.30, 0.24), (0.36, 0.26, 0.18, 1.0))
    make_box("Rug", (-0.35, 2.40, 0.006), (1.30, 0.90, 0.008), (0.52, 0.44, 0.36, 1.0))


def build_wear():
    dk = (COL_FLOOR[0] * 0.88, COL_FLOOR[1] * 0.88, COL_FLOOR[2] * 0.88, 1.0)
    make_traffic_wear("Wear_Path", [(DOOR[0], 0.5), (DOOR[0], 1.4), (0.6, 2.4), (-0.1, 3.2)], width=0.50, tint=dk)
    make_floor_stain("Wear_Chair", (XE - 0.85, 2.95), radius=0.26, tint=dk, segments=10)


def main():
    clear_scene()
    build_shell()
    build_window()
    build_fan()
    build_bed()
    build_desk()
    build_dresser()
    build_closet_duffel()
    build_wear()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/diego_bedroom.glb"))
    print(f"\n[build_diego_bedroom] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
