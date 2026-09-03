"""accretion_basement — the corridor behind the hedge and the basement
with the boy at the desk. vol7 ch11 (Kestrel Mountain, nodes 41-128),
re-homed off cabin_interior (2026-09-03).

"The corridor was a hallway. The hallway was, by the way the substrate
rendered the walls, an institutional hallway from the late 1990s. The
walls were that kind of off-white that institutional walls were in
the late 1990s. The floor was linoleum in a pattern of flecks. The
ceiling had drop tiles. The lights were fluorescent." Doors on both
sides with "windows of wire-reinforced glass at face height." The
hallway turned right, then right again, then "went down a flight of
stairs. The stairs were concrete. The handrail was painted green."
"The stairs ended at a door. The door said, in stenciled letters: NO
ENTRY EXCEPT BY AUTHORIZED PERSONNEL." "The basement was a long room.
The ceiling was low. The fluorescents were the same fluorescents as
the hallway, but they were a worse run of the bulbs, and one of them,
at the far end of the room, was flickering at a rate his eye could
see. The racks of servers were on his left ... On the right side of
the room was a desk. At the desk was a person ... sitting in a wooden
chair with their back to Kai." On the desk: "a notebook open to a
page ... three pieces of cedar wood that the boy had been, when Kai
came in, arranging into a pattern."

The substrate's accretion — a 1993 kid's basement grown onto a 2034
mountain stick. Two presets over one glb: accretion_corridor (the
first leg, doors both sides, the right turn ahead) and
accretion_basement (just inside the stenciled door, looking down the
long room: racks left, the desk right, the flicker at the far end).

Coordinate frame: Blender Z-up. The first hallway leg runs +y from
y 0 to 24 at x 0; the second leg runs +x along y 24 to x 12; the
stairs drop 3 m along -y from y 24 to 19.8 at x 12; the door at
y 15.5; the basement runs -y from 15.5 to -15 at x 12, floor z -3.
glTF export remaps to Godot (x, z, -y).

DRAFT 1 (2026-09-03): both hallway legs (floor, drop-tile ceiling
with its grid, walls, ten doors with wire-glass windows and frames,
fluorescent fixtures), the stairwell (fifteen concrete steps, the
green stepped handrail, the landing), the stenciled door open into
the basement, the basement (low ceiling, fixtures with the far one
flickering, six server racks with LEDs and a cable tray, the desk
with the notebook, the three cedar pieces in their pattern, the
pencil, the wooden chair, a floor drain, a pipe run).
Draft 2 targets: the fleck pattern on the linoleum, the second leg's
own doors, the boy (cast), the rack hum as an ambient bed.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

OFFWHITE = (0.82, 0.80, 0.74, 1.0)
OFFWHITE_DK = (0.72, 0.70, 0.64, 1.0)
LINO = (0.60, 0.62, 0.56, 1.0)
LINO_FLECK = (0.48, 0.50, 0.44, 1.0)
TILE = (0.86, 0.86, 0.82, 1.0)
TILE_GRID = (0.62, 0.62, 0.58, 1.0)
FLUOR = (0.96, 0.98, 0.92, 1.0)
FLUOR_BAD = (0.80, 0.78, 0.60, 1.0)
DOOR = (0.52, 0.42, 0.30, 1.0)
FRAME = (0.36, 0.36, 0.38, 1.0)
GLASS = (0.62, 0.70, 0.72, 0.5)
WIRE = (0.34, 0.34, 0.36, 1.0)
CONCRETE = (0.56, 0.56, 0.54, 1.0)
CONCRETE_DK = (0.44, 0.44, 0.43, 1.0)
RAIL_GREEN = (0.20, 0.44, 0.30, 1.0)
GRAY_DOOR = (0.50, 0.52, 0.52, 1.0)
STENCIL = (0.14, 0.14, 0.16, 1.0)
BLOCK = (0.66, 0.64, 0.60, 1.0)
RACK = (0.16, 0.16, 0.18, 1.0)
RACK_FACE = (0.22, 0.22, 0.25, 1.0)
LED = (0.30, 0.86, 0.40, 1.0)
LED_AMBER = (0.92, 0.66, 0.20, 1.0)
WOOD = (0.50, 0.40, 0.28, 1.0)
WOOD_DK = (0.40, 0.31, 0.22, 1.0)
CEDAR = (0.64, 0.46, 0.30, 1.0)
PAPER = (0.94, 0.93, 0.88, 1.0)

H_W = 2.4      # hallway width
H_H = 2.7      # hallway height
WALL_T = 0.2
B_FLOOR = -3.0
B_H = 2.3


def hallway_leg(prefix, axis, a0, a1, c, doors=True, ceiling_grid=True):
    """A hallway leg along `axis` ('Y' or 'X') from a0 to a1 at cross
    position c. Floor, ceiling, two walls, doors, fixtures."""
    L = a1 - a0
    mid = (a0 + a1) / 2.0
    def pt(along, cross, z):
        return (cross, along, z) if axis == "Y" else (along, cross, z)
    def sz(along, cross, z):
        return (cross, along, z) if axis == "Y" else (along, cross, z)
    make_box(f"{prefix}_Floor", pt(mid, c, -0.05), sz(L, H_W, 0.10), LINO)
    make_box(f"{prefix}_Ceiling", pt(mid, c, H_H + 0.05), sz(L, H_W, 0.10), TILE)
    for sgn, nm in ((1, "L"), (-1, "R")):
        make_box(f"{prefix}_Wall_{nm}", pt(mid, c + sgn * (H_W / 2.0 + WALL_T / 2.0), H_H / 2.0), sz(L, WALL_T, H_H), OFFWHITE)
        if doors:
            make_box(f"{prefix}_Base_{nm}_0", pt(a0 + 0.775, c + sgn * (H_W / 2.0 - 0.02), 0.06), sz(1.55, 0.04, 0.12), OFFWHITE_DK)
            for bi in range(int(L / 4.0)):
                make_box(f"{prefix}_Base_{nm}_{bi + 1}", pt(a0 + 4.0 * bi + 4.0, c + sgn * (H_W / 2.0 - 0.02), 0.06), sz(3.1, 0.04, 0.12), OFFWHITE_DK)
        else:
            make_box(f"{prefix}_Base_{nm}", pt(mid, c + sgn * (H_W / 2.0 - 0.02), 0.06), sz(L, 0.04, 0.12), OFFWHITE_DK)
    if ceiling_grid:
        n = int(L / 0.6)
        for i in range(1, n):
            make_box(f"{prefix}_Grid_{i}", pt(a0 + i * 0.6, c, H_H - 0.005), sz(0.02, H_W, 0.01), TILE_GRID)
    n_fix = int(L / 4.0)
    for i in range(n_fix):
        make_box(f"{prefix}_Fluor_{i}", pt(a0 + 2.0 + i * 4.0, c, H_H - 0.03), sz(1.2, 0.3, 0.06), FLUOR)
    if doors:
        for i in range(int(L / 4.0)):
            for sgn, nm in ((1, "L"), (-1, "R")):
                x_face = c + sgn * (H_W / 2.0 - 0.025)
                make_box(f"{prefix}_Door_{i}_{nm}", pt(a0 + 4.0 * i + 2.0, x_face, 1.05), sz(0.90, 0.05, 2.10), DOOR)
                make_box(f"{prefix}_Door_{i}_{nm}_Frame_Top", pt(a0 + 4.0 * i + 2.0, x_face, 2.14), sz(1.02, 0.05, 0.08), FRAME)
                gx = c + sgn * (H_W / 2.0 - 0.055)
                make_box(f"{prefix}_Door_{i}_{nm}_Glass", pt(a0 + 4.0 * i + 2.0, gx, 1.55), sz(0.26, 0.01, 0.40), GLASS)
                for wi in range(3):
                    make_box(f"{prefix}_Door_{i}_{nm}_Wire_{wi}", pt(a0 + 4.0 * i + 2.0, gx - sgn * 0.006, 1.40 + wi * 0.15), sz(0.26, 0.002, 0.004), WIRE)
                make_box(f"{prefix}_Door_{i}_{nm}_Handle", pt(a0 + 4.0 * i + 2.0 + 0.32, c + sgn * (H_W / 2.0 - 0.07), 1.02), sz(0.04, 0.04, 0.12), FRAME)


def build_hallways():
    # first leg: +y from 0 to 24 at x 0 — the doors both sides, the turn ahead
    hallway_leg("Hall_A", "Y", 0.0, 22.8, 0.0)
    # the corner block: floor + ceiling square at the turn, the closing west wall
    make_box("Hall_Corner_Floor", (0.05, 24.0, -0.05), (H_W + 0.1, 2.4, 0.10), LINO)
    make_box("Hall_Corner_Ceiling", (0.05, 24.0, H_H + 0.05), (H_W + 0.1, 2.4, 0.10), TILE)
    make_box("Hall_Corner_Wall_W", (-(H_W / 2.0 + WALL_T / 2.0), 24.0, H_H / 2.0), (WALL_T, 2.4, H_H), OFFWHITE)
    make_box("Hall_Corner_Wall_N", (0.0, 25.2 + WALL_T / 2.0, H_H / 2.0), (H_W + 0.2, WALL_T, H_H), OFFWHITE)
    make_box("Hall_Corner_Fluor", (0.0, 24.0, H_H - 0.03), (0.3, 1.2, 0.06), FLUOR)
    # a fire-extinguisher case and a bulletin board on the first leg
    make_box("Extinguisher_Case", (1.16, 10.0, 1.25), (0.08, 0.30, 0.70), (0.72, 0.16, 0.14, 1.0))
    make_box("Extinguisher_Case_Glass", (1.115, 10.0, 1.25), (0.01, 0.24, 0.60), GLASS)
    make_box("Bulletin_Board", (-1.16, 14.0, 1.55), (0.08, 1.20, 0.90), (0.60, 0.46, 0.30, 1.0))
    for pi in range(4):
        make_box(f"Bulletin_Paper_{pi}", (-1.115, 13.55 + pi * 0.30, 1.60 - (pi % 2) * 0.2), (0.01, 0.21, 0.28), PAPER)
    # second leg: +x from 1.2 to 10.8 along y 24 (walls at y 22.8 / 25.2)
    hallway_leg("Hall_B", "X", 1.3, 10.8, 24.0, doors=False, ceiling_grid=False)
    make_box("Hall_B_Exit_Sign", (6.0, 25.15, 2.35), (0.30, 0.02, 0.14), (0.86, 0.20, 0.16, 1.0))


def build_stairwell():
    """Fifteen concrete steps down from the second right turn, the green
    handrail, the landing, the stenciled door."""
    # the well: corner floor square at (12, 24), walls at x 10.8 / 13.2 from y 25.2 down to 15.5
    make_box("Well_Corner_Floor", (12.0, 24.0, -0.05), (2.4, 2.4, 0.10), LINO)
    make_box("Well_Wall_E", (13.2 + WALL_T / 2.0, 20.4, (H_H - 3.0) / 2.0), (WALL_T, 10.0, H_H + 3.0), OFFWHITE)
    make_box("Well_Wall_W", (10.8 - WALL_T / 2.0, 19.0, (H_H - 3.0) / 2.0), (WALL_T, 7.2, H_H + 3.0), OFFWHITE)
    make_box("Well_Wall_N", (12.0, 25.2 + WALL_T / 2.0, H_H / 2.0), (2.4, WALL_T, H_H), OFFWHITE)
    make_box("Well_Ceiling", (12.0, 20.35, H_H + 0.05), (2.4, 9.7, 0.10), TILE)
    make_box("Well_Fluor", (12.0, 21.0, H_H - 0.03), (0.3, 1.2, 0.06), FLUOR)
    for i in range(14):
        y_hi = 22.8 - 0.28 * i
        top = -0.2 * (i + 1)
        make_box(f"Stair_Step_{i}", (12.0, y_hi - 0.14, (B_FLOOR + top) / 2.0), (2.4, 0.28, top - B_FLOOR), CONCRETE if i % 2 else CONCRETE_DK)
        make_box(f"Stair_Nosing_{i}", (12.0, y_hi - 0.02, top + 0.005), (2.4, 0.04, 0.01), (0.30, 0.30, 0.30, 1.0))
    make_box("Stair_Landing", (12.0, 17.24, B_FLOOR - 0.05), (2.4, 3.28, 0.10), CONCRETE)
    # the green handrail, stepped: posts + short rails
    for i in range(0, 14, 3):
        y = 22.8 - 0.28 * i - 0.14
        top = -0.2 * (i + 1)
        make_cyl(f"Rail_Post_{i}", (13.05, y, top + 0.45), 0.02, 0.90, RAIL_GREEN, segments=6)
        make_cyl(f"Rail_Run_{i}", (13.05, y - 0.42, top + 0.90 + 0.02), 0.02, 0.84, RAIL_GREEN, axis="Y", segments=6)
    make_cyl("Rail_Post_Landing", (13.05, 18.0, B_FLOOR + 0.45), 0.02, 0.90, RAIL_GREEN, segments=6)
    # the door at the stair foot: NO ENTRY EXCEPT BY AUTHORIZED PERSONNEL — open inward
    make_box("Basement_Wall_N_L", (9.7, 15.5, B_FLOOR + B_H / 2.0), (1.8, WALL_T, B_H), BLOCK)
    make_box("Basement_Wall_N_L2", (11.1, 15.5, B_FLOOR + B_H / 2.0), (0.6, WALL_T, B_H), BLOCK)
    make_box("Basement_Wall_N_R", (12.9, 15.5, B_FLOOR + B_H / 2.0), (0.6, WALL_T, B_H), BLOCK)
    make_box("Basement_Wall_N_R2", (14.3, 15.5, B_FLOOR + B_H / 2.0), (1.8, WALL_T, B_H), BLOCK)
    make_box("Basement_Lintel", (11.9, 15.5, B_FLOOR + 2.2), (1.0, WALL_T, 0.10), BLOCK)
    make_box("Basement_Jamb_L", (11.42, 15.5, B_FLOOR + 1.05), (0.04, WALL_T + 0.02, 2.10), FRAME)
    make_box("Basement_Jamb_R", (12.38, 15.5, B_FLOOR + 1.05), (0.04, WALL_T + 0.02, 2.10), FRAME)
    make_box("Door", (11.47, 14.95, B_FLOOR + 1.05), (0.05, 0.88, 2.08), GRAY_DOOR)
    for li, (w, z) in enumerate(((0.62, 1.62), (0.70, 1.50), (0.52, 1.38))):
        make_box(f"Door_Stencil_{li}", (11.443, 14.95, B_FLOOR + z), (0.004, w, 0.07), STENCIL)
    make_box("Door_Push_Bar", (11.425, 14.95, B_FLOOR + 1.0), (0.04, 0.70, 0.06), FRAME)


def build_basement():
    """The long room: low ceiling, the fixtures with the far one
    flickering, six racks on the left, the desk on the right."""
    cx, y_n, y_s = 12.0, 15.5, -13.0
    L = y_n - y_s
    ym = (y_n + y_s) / 2.0
    make_box("Basement_Floor", (cx, ym, B_FLOOR - 0.05), (6.0, L, 0.10), (0.40, 0.40, 0.40, 1.0))
    make_box("Basement_Ceiling", (cx, (y_s + 15.4) / 2.0, B_FLOOR + B_H + 0.05), (6.0, 15.4 - y_s, 0.10), (0.70, 0.70, 0.68, 1.0))
    make_box("Basement_Wall_E", (15.0 + WALL_T / 2.0, (y_s + 15.4) / 2.0, B_FLOOR + B_H / 2.0), (WALL_T, 15.4 - y_s, B_H), BLOCK)
    make_box("Basement_Wall_W", (9.0 - WALL_T / 2.0, (y_s + 15.4) / 2.0, B_FLOOR + B_H / 2.0), (WALL_T, 15.4 - y_s, B_H), BLOCK)
    make_box("Basement_Wall_S", (cx, y_s - WALL_T / 2.0, B_FLOOR + B_H / 2.0), (6.0 + 2 * WALL_T, WALL_T, B_H), BLOCK)
    # block-course lines on the west wall
    for i in range(1, 6):
        make_box(f"Block_Course_{i}", (9.005, ym, B_FLOOR + i * 0.4), (0.01, L, 0.012), (0.56, 0.54, 0.50, 1.0))
    # fixtures every five meters, the far one a worse run of the bulbs
    n = 6
    for i in range(n):
        y = y_n - 2.5 - i * 5.0
        bad = (i == n - 1)
        make_box(f"Basement_Fluor_{i}" if not bad else "Fluorescent_Far_Flicker", (cx, y, B_FLOOR + B_H - 0.03), (0.3, 1.2, 0.06), FLUOR_BAD if bad else FLUOR)
        make_box(f"Basement_Fluor_{i}_Housing", (cx, y, B_FLOOR + B_H - 0.075), (0.36, 1.26, 0.03), (0.60, 0.60, 0.58, 1.0))
    # pipe run and a floor drain
    make_cyl("Pipe_Run", (14.6, ym, B_FLOOR + B_H - 0.20), 0.06, L - 0.4, (0.46, 0.44, 0.40, 1.0), axis="Y", segments=8)
    make_cyl("Floor_Drain", (cx, 4.0, B_FLOOR + 0.002), 0.12, 0.004, (0.28, 0.28, 0.28, 1.0), segments=10)
    # six racks of servers on the left (east) wall
    for i in range(6):
        y = 12.0 - i * 2.2
        make_box(f"Rack_{i}", (14.2, y, B_FLOOR + 1.0), (0.60, 1.00, 2.00), RACK)
        make_box(f"Rack_{i}_Face", (13.895, y, B_FLOOR + 1.0), (0.01, 0.96, 1.96), RACK_FACE)
        for u in range(9):
            z = B_FLOOR + 0.25 + u * 0.19
            make_box(f"Rack_{i}_Unit_{u}", (13.885, y, z), (0.01, 0.90, 0.14), (0.26 + (u % 2) * 0.04, 0.26, 0.29, 1.0))
            make_box(f"Rack_{i}_LED_{u}", (13.878, y - 0.40, z + 0.04), (0.004, 0.02, 0.02), LED if (u + i) % 4 else LED_AMBER)
    make_box("Cable_Tray", (14.2, 6.5, B_FLOOR + 2.10), (0.30, 13.2, 0.06), (0.36, 0.36, 0.38, 1.0))
    for ci in range(3):
        make_cyl(f"Cable_Drop_{ci}", (14.2 + (ci - 1) * 0.08, 12.0 - ci * 4.4, B_FLOOR + 2.035), 0.012, 0.07, (0.20, 0.30, 0.60, 1.0), segments=6)
    # the desk on the right (west) wall, the wooden chair with its back to the door
    dx, dy = 9.5, -0.5
    make_box("Desk_Top", (dx, dy, B_FLOOR + 0.74), (0.80, 1.60, 0.04), WOOD)
    for li, (lx, ly) in enumerate(((dx - 0.36, dy - 0.76), (dx + 0.36, dy - 0.76), (dx - 0.36, dy + 0.76), (dx + 0.36, dy + 0.76))):
        make_box(f"Desk_Leg_{li}", (lx, ly, B_FLOOR + 0.36), (0.05, 0.05, 0.72), WOOD_DK)
    make_box("Desk_Apron", (dx, dy, B_FLOOR + 0.66), (0.66, 1.44, 0.10), WOOD_DK)
    make_box("Notebook", (dx + 0.05, dy + 0.20, B_FLOOR + 0.766), (0.24, 0.18, 0.012), (0.30, 0.44, 0.58, 1.0))
    make_box("Notebook_Page", (dx + 0.05, dy + 0.20, B_FLOOR + 0.7735), (0.22, 0.16, 0.003), PAPER)
    make_box("Notebook_Handwriting", (dx + 0.05, dy + 0.21, B_FLOOR + 0.7755), (0.14, 0.10, 0.001), (0.36, 0.36, 0.42, 1.0))
    # the three pieces of cedar in their pattern — a triangle, one piece turned
    for ci, (ox, oy, w, d) in enumerate(((-0.02, -0.34, 0.09, 0.03), (0.10, -0.46, 0.03, 0.09), (-0.14, -0.46, 0.09, 0.03))):
        make_box(f"Cedar_Piece_{ci}", (dx + ox, dy + oy, B_FLOOR + 0.775), (w, d, 0.03), CEDAR)
    make_cyl("Pencil", (dx + 0.30, dy + 0.05, B_FLOOR + 0.764), 0.004, 0.16, (0.84, 0.66, 0.24, 1.0), axis="Y", segments=6)
    make_box("Desk_Cup", (dx - 0.25, dy - 0.55, B_FLOOR + 0.80), (0.08, 0.08, 0.08), (0.80, 0.78, 0.72, 1.0))
    # the wooden chair, east of the desk, its back to the room
    chx, chy = dx + 0.85, dy
    make_box("Chair_Seat", (chx, chy, B_FLOOR + 0.45), (0.42, 0.42, 0.04), WOOD)
    make_box("Chair_Back", (chx + 0.19, chy, B_FLOOR + 0.80), (0.04, 0.42, 0.66), WOOD)
    for li, (lx, ly) in enumerate(((chx - 0.18, chy - 0.18), (chx + 0.18, chy - 0.18), (chx - 0.18, chy + 0.18), (chx + 0.18, chy + 0.18))):
        make_box(f"Chair_Leg_{li}", (lx, ly, B_FLOOR + 0.215), (0.04, 0.04, 0.43), WOOD_DK)
    # a boy has been here a number of hours: a second cup, a jacket over the chair back
    make_box("Jacket_On_Chair", (chx + 0.24, chy, B_FLOOR + 0.95), (0.06, 0.40, 0.30), (0.30, 0.34, 0.44, 1.0))


def main():
    clear_scene()
    build_hallways()
    build_stairwell()
    build_basement()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/accretion_basement.glb"))
    print(f"\n[build_accretion_basement] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
