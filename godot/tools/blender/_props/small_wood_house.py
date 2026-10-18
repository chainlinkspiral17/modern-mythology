"""SMALL WOOD HOUSE — one floor plan behind vol 2's two houses (2026-10-18).

The user (2026-10-18): "Dean's house can be the same layout, just dressed
different. There is the idea of two overlapping houses in the dreams."
So the narrator's bedroom in the old ranch house (small_wood_ranch) and
N. Dean's bedroom in the rented house up the Alsea (dean_house_1994) are
one room: the same walls, the same window, the same door, each builder
dressing it for its own house and year. The house itself is "ten miles
inland from the coast but 'on the coast'" (the user).

The room: W x D under a low farmhouse ceiling, its window on the N wall
(the firs and the moon for one house, the pasture and the Hagstrom place
for the other), its door on the S wall. Coordinates are the room's own:
x -W/2..W/2, y 0..D, the floor at z 0.
"""
from .structure import make_floor, make_wall, make_ceiling, make_window, make_wall_with_openings

W, D, CEIL, T = 3.8, 4.2, 2.45, 0.20
WIN_X, WIN_W, WIN_H, WIN_Z = 0.20, 1.30, 1.25, 1.45
DOOR_X = 1.20


def bedroom_shell(pal, floor_cols, ceil_tile, prefix=""):
    """The bedroom's floor, ceiling, four walls, the N window and the S
    door's opening. `pal` is the wall palette, `floor_cols` (board, seam)."""
    make_floor(f"{prefix}Floor", (0.0, D / 2.0, 0.0), size_x=W + 0.4, size_y=D + 0.4,
               palette={"vinyl": floor_cols[0], "seam": floor_cols[1]})
    make_ceiling(f"{prefix}Ceil", (0.0, D / 2.0, CEIL), size_x=W + 0.4, size_y=D + 0.4, with_grid=False, with_stains=True,
                 palette={"tile": ceil_tile})
    make_wall(f"{prefix}Wall_W", (-W / 2.0, D / 2.0, 0), length=D + 0.4, height=CEIL, thickness=T, axis='Y', palette=pal,
              baseboard_face_sign=+1)
    make_wall(f"{prefix}Wall_E", (W / 2.0, D / 2.0, 0), length=D + 0.4, height=CEIL, thickness=T, axis='Y', palette=pal,
              baseboard_face_sign=-1)
    make_wall_with_openings(f"{prefix}Wall_N", (0.0, D, 0), length=W + 0.4, height=CEIL, thickness=T, axis='X', palette=pal,
                            baseboard_face_sign=-1, openings=[(WIN_X, WIN_Z, WIN_W, WIN_H)])
    make_wall_with_openings(f"{prefix}Wall_S", (0.0, 0.0, 0), length=W + 0.4, height=CEIL, thickness=T, axis='X', palette=pal,
                            baseboard_face_sign=+1, openings=[(DOOR_X, 1.0, 0.82, 2.0)])
    make_window(f"{prefix}Window_N", (WIN_X, D - 0.10, WIN_Z), width=WIN_W, height=WIN_H, see_through=True)
