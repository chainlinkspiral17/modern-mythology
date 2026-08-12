# _props/structure.py
# ════════════════════════════════════════════════════════════════
# Shell pieces every interior locale needs — walls, floors,
# ceilings, baseboards, crown molding, mullioned windows, door
# hinges. Callers compose these into footprints; library doesn't
# enforce a floorplan.
# ════════════════════════════════════════════════════════════════
from . import palette as P
from .geometry import make_box, make_cyl


def make_floor(prefix, anchor, *, size_x, size_y, palette=None):
    """Rectangular floor pad with N-S plank seams + E-W tile seams."""
    palette = palette or {}
    vinyl = palette.get("vinyl", P.FLOOR_VINYL)
    seam = palette.get("seam", P.FLOOR_SEAM)
    cx, cy, base_z = anchor
    make_box(f"{prefix}_Slab", (cx, cy, base_z - 0.05),
             (size_x, size_y, 0.10), vinyl)
    # N-S plank seams
    n_x = int(size_x)
    for i in range(-n_x // 2, n_x // 2 + 1):
        make_box(f"{prefix}_SeamX_{i}",
                 (cx + i, cy, base_z + 0.005),
                 (0.02, size_y, 0.001), seam)
    # E-W tile seams
    n_y = int(size_y)
    for j in range(int(cy - size_y / 2), int(cy + size_y / 2) + 1):
        make_box(f"{prefix}_SeamY_{j}",
                 (cx, j, base_z + 0.005),
                 (size_x, 0.02, 0.001), seam)


def make_wall(prefix, anchor, *, length, height=3.0, thickness=0.20,
              axis='Y', palette=None, with_baseboard=True,
              baseboard_face_sign=-1):
    """Single straight wall. axis='Y' (runs N-S) or 'X' (runs E-W).
    For Y walls, baseboard_face_sign=+1 puts baseboard on +X (east)
    side; -1 puts it on -X (west) side. For X walls, +1/-1 flip
    along Y."""
    palette = palette or {}
    wall_col = palette.get("wall", P.WALL_CREAM)
    base_col = palette.get("baseboard", P.WALL_BASEBOARD)
    cx, cy, _ = anchor
    if axis == 'Y':
        make_box(f"{prefix}", (cx, cy, height / 2.0),
                 (thickness, length, height), wall_col)
        if with_baseboard:
            make_box(f"{prefix}_Base",
                     (cx + baseboard_face_sign * 0.06, cy, 0.08),
                     (0.06, length, 0.16), base_col)
    else:
        make_box(f"{prefix}", (cx, cy, height / 2.0),
                 (length, thickness, height), wall_col)
        if with_baseboard:
            make_box(f"{prefix}_Base",
                     (cx, cy + baseboard_face_sign * 0.06, 0.08),
                     (length, 0.06, 0.16), base_col)


def make_ceiling(prefix, anchor, *, size_x, size_y, palette=None,
                 with_grid=True, with_stains=True):
    """Drop-tile ceiling with grid + occasional water stains."""
    palette = palette or {}
    tile = palette.get("tile", P.CEILING_TILE)
    grid = palette.get("grid", P.CEILING_GRID)
    stain = palette.get("stain", P.CEILING_STAIN)
    cx, cy, ceil_z = anchor
    make_box(f"{prefix}_Plane", (cx, cy, ceil_z + 0.05),
             (size_x, size_y, 0.10), tile)
    # Grid + stains hang BELOW the slab's underside (z-fight fix
    # 2026-08-09: they used to sit INSIDE the slab volume, near-
    # coplanar with its bottom face — "flickering geometry in the
    # roof" at glancing angles, in every interior using this).
    if with_grid:
        for i in range(int(cx - size_x / 2), int(cx + size_x / 2) + 1):
            make_box(f"{prefix}_GridX_{i}", (i, cy, ceil_z - 0.010),
                     (0.04, size_y, 0.012), grid)
        for j in range(int(cy - size_y / 2), int(cy + size_y / 2) + 1):
            make_box(f"{prefix}_GridY_{j}", (cx, j, ceil_z - 0.010),
                     (size_x, 0.04, 0.012), grid)
    if with_stains:
        for si, (sx, sy) in enumerate([
                (cx - 2, cy - 2), (cx + 1, cy + 1), (cx + 3, cy + 3)]):
            make_box(f"{prefix}_Stain_{si}",
                     (sx, sy, ceil_z - 0.004),
                     (0.80, 0.80, 0.003), stain)


def make_crown_molding(prefix, *, wall_x, wall_y, length, axis,
                       ceil_z, palette=None):
    """Half-round molding strip along a wall-ceiling junction.
    axis='Y' (E/W wall, runs N-S) or 'X' (N/S wall, runs E-W)."""
    palette = palette or {}
    col = palette.get("wood", P.CROWN_MOLD)
    seg_count = max(1, int(round(length / 1.0)))
    seg_len = length / seg_count
    for s in range(seg_count):
        if axis == 'Y':
            sy = wall_y - length / 2.0 + (s + 0.5) * seg_len
            make_cyl(f"{prefix}_{s}", (wall_x, sy, ceil_z - 0.06),
                     0.04, seg_len, col, axis='Y', segments=6)
        else:
            sx = wall_x - length / 2.0 + (s + 0.5) * seg_len
            make_cyl(f"{prefix}_{s}", (sx, wall_y, ceil_z - 0.06),
                     0.04, seg_len, col, axis='X', segments=6)


def make_window(prefix, anchor, *, width=2.60, height=1.50,
                cross_mullion=True, palette=None, axis='X'):
    """Mullioned multi-pane glass window.

    axis='X' (default): the window lies in a NORTH or SOUTH wall and
    spans X — anchor=(wall_x_center, wall_face_y, center_z).
    axis='Y': it lies in an EAST or WEST wall and spans Y —
    anchor=(wall_face_x, wall_y_center, center_z).

    The Y form was added 2026-08-12: five locales already placed
    windows on east/west walls, where the X-spanning build laid the
    glass ACROSS the room and 0.6m into the wall. `center_z` is a
    CENTER, not a sill — eleven callers passed 0 and got windows
    half-buried in the floor (fixed the same day).
    cross_mullion=True draws horizontal + vertical bars."""
    palette = palette or {}
    glass = palette.get("glass", P.GLASS)
    frame = palette.get("frame", P.METAL_STEEL)
    warm = palette.get("warm", P.GLASS_WARM)
    cx, cy, cz = anchor
    along_y = str(axis).upper() == 'Y'

    def _sz(span, thick, tall):
        """(x, y, z) extents for a member `span` long across the
        wall, `thick` through it, `tall` high."""
        return (thick, span, tall) if along_y else (span, thick, tall)

    def _at(off, inset, dz):
        """Position `off` along the wall, `inset` into it, dz up."""
        if along_y:
            return (cx - inset, cy + off, cz + dz)
        return (cx + off, cy - inset, cz + dz)

    # Glass behind a slight warm tint (sun-through-window canon)
    make_box(f"{prefix}_Glass", _at(0.0, 0.02, 0.0),
             _sz(width, 0.005, height), glass)
    make_box(f"{prefix}_Warm", _at(0.0, 0.01, 0.0),
             _sz(width * 0.96, 0.001, height * 0.96), warm)
    # Frame — top + bottom + sides
    make_box(f"{prefix}_FrameT", _at(0.0, 0.04, height / 2.0),
             _sz(width + 0.10, 0.08, 0.10), frame)
    make_box(f"{prefix}_FrameB", _at(0.0, 0.04, -height / 2.0),
             _sz(width + 0.10, 0.08, 0.10), frame)
    for sgn in (-1, +1):
        make_box(f"{prefix}_FrameSide_{sgn:+d}",
                 _at(sgn * (width / 2.0 + 0.04), 0.04, 0.0),
                 _sz(0.10, 0.08, height), frame)
    if cross_mullion:
        make_box(f"{prefix}_MullH", _at(0.0, 0.04, 0.0),
                 _sz(width, 0.06, 0.05), frame)
        for vm in (-width / 4.0, +width / 4.0):
            make_box(f"{prefix}_MullV_{vm:+.2f}",
                     _at(vm, 0.04, 0.0),
                     _sz(0.05, 0.06, height), frame)


def make_door_hinges(prefix, *, edge_x, edge_y, edge_z_centers,
                     axis='Y', palette=None):
    """3+ cylindrical hinge barrels along a door edge.
    axis='Y' = wall is on E/W axis (door swings on a Y-axis hinge),
    axis='X' = wall on N/S axis. Hinge cylinder axis aligns with wall."""
    palette = palette or {}
    col = palette.get("col", P.METAL_BLACK)
    for hi, hz in enumerate(edge_z_centers):
        make_cyl(f"{prefix}_{hi}", (edge_x, edge_y, hz),
                 0.018, 0.08, col, axis=axis)
