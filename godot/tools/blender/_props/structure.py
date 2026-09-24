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
    along Y — i.e. the sign points from the wall INTO THE ROOM.

    2026-09-23: the baseboard was 6 cm thick centred 6 cm off the wall's
    centre line — wholly inside any 20 cm wall, on either side. 398
    baseboards in 79 rooms had never been visible. It sits ON the face
    now, 1.2 cm proud (under the overlap gate's 1.5 cm abutment
    tolerance, so furniture set against a wall still reads as flush)."""
    b_off = thickness / 2.0 + 0.006
    palette = palette or {}
    wall_col = palette.get("wall", P.WALL_CREAM)
    base_col = palette.get("baseboard", P.WALL_BASEBOARD)
    cx, cy, _ = anchor
    if axis == 'Y':
        make_box(f"{prefix}", (cx, cy, height / 2.0),
                 (thickness, length, height), wall_col)
        if with_baseboard:
            make_box(f"{prefix}_Base",
                     (cx + baseboard_face_sign * b_off, cy, 0.08),
                     (0.012, length, 0.16), base_col)
    else:
        make_box(f"{prefix}", (cx, cy, height / 2.0),
                 (length, thickness, height), wall_col)
        if with_baseboard:
            make_box(f"{prefix}_Base",
                     (cx, cy + baseboard_face_sign * b_off, 0.08),
                     (length, 0.012, 0.16), base_col)


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
    # Water stains (2026-09-24, the user: "furniture on ceilings"): they
    # were three SOLID 0.8 m squares in a dark tan, at fixed metre
    # offsets from the centre (so in small rooms they hit the walls) —
    # under a warm key they read as boards stuck to the ceiling. Now a
    # faint tint of the tile, an irregular blotch of three overlapping
    # pieces, placed at fractions of the ceiling so it stays inside it,
    # and none on a ceiling under 2.5 m across.
    if with_stains and min(size_x, size_y) >= 2.5:
        tint = tuple(tile[k] * 0.72 + stain[k] * 0.28 for k in range(3)) + (1.0,)
        for si, (fx, fy, r) in enumerate(((-0.26, -0.20, 0.34), (0.22, 0.28, 0.26))):
            sx, sy = cx + fx * size_x, cy + fy * size_y
            for pi, (ox, oy, k) in enumerate(((0.0, 0.0, 1.0), (0.14, 0.06, 0.62), (-0.08, 0.12, 0.48))):
                make_box(f"{prefix}_Stain_{si}_{pi}",
                         (sx + ox * r * 2.0, sy + oy * r * 2.0, ceil_z - 0.003 - 0.0005 * pi),
                         (r * k, r * k * 0.8, 0.002), tint)


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
                cross_mullion=True, palette=None, axis='X', room_dir=-1,
                see_through=False):
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
    cross_mullion=True draws horizontal + vertical bars.

    room_dir (2026-09-23): the side of the wall the ROOM is on, along
    the wall's normal (-1: the room is toward -Y / -X, a NORTH or EAST
    wall — the old fixed behaviour and the default; +1: a SOUTH or WEST
    wall). The glass and frame are built from the anchor toward the
    room. Before this, every south/west-wall window was built INTO its
    wall, and callers that passed the wall's centre line buried theirs
    on any wall: 43 windows in 34 rooms were invisible.

    see_through (2026-09-24): no glass and no warm pane — frame and
    mullions only, the opening left empty, two glints on the frame
    line. The pipeline has no alpha: the glass and the warm pane render
    as two OPAQUE panels, so a window something must be SEEN through
    (the cabin's crow on the outside sill) cannot have them (the 3D
    modelling playbook's picture-window rule)."""
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
            return (cx + room_dir * inset, cy + off, cz + dz)
        return (cx + off, cy + room_dir * inset, cz + dz)

    if see_through:
        # glints on the pane line, sill frame to head frame
        for gi, (go, gw) in enumerate(((-width * 0.18, 0.03), (-width * 0.12, 0.012))):
            make_box(f"{prefix}_Glint_{gi}", _at(go, 0.075, 0.0),   # in front of MullH
                     _sz(gw, 0.004, height - 0.10), (0.84, 0.88, 0.92, 1.0))
    else:
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


def make_case_shell(prefix, center, size, color, *, open_face='-Y', wall=0.02):
    """A display case / cooler / cabinet body as FIVE PANELS with one
    face open, same outer extents as a solid make_box(center, size).

    2026-09-24 (support pass, twenty-third draft): every glass-front
    case in the kits was a SOLID body with its product modelled inside
    it and a tinted "glass" slab in front — and this pipeline has no
    alpha (vertex colour only), so the glass rendered as an opaque
    panel over a solid block: 95 objects per kwik stop cooler door that
    no camera could ever see. Build the shell; put the product on
    shelves inside it; frame the opening and leave the glass out.

    Panels: `{prefix}_Top` / `_Bottom` span the full footprint; the two
    sides sit between them; the back sits between the sides. Faces
    touch, nothing overlaps. open_face: '-X', '+X', '-Y' or '+Y'."""
    cx, cy, cz = center
    sx, sy, sz = size
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    w = wall
    make_box(f"{prefix}_Top", (cx, cy, cz + hz - w / 2.0), (sx, sy, w), color)
    make_box(f"{prefix}_Bottom", (cx, cy, cz - hz + w / 2.0), (sx, sy, w), color)
    ih = sz - 2.0 * w
    if open_face in ('-Y', '+Y'):
        s = 1.0 if open_face == '-Y' else -1.0      # back is opposite the opening
        make_box(f"{prefix}_Side_L", (cx - hx + w / 2.0, cy, cz), (w, sy, ih), color)
        make_box(f"{prefix}_Side_R", (cx + hx - w / 2.0, cy, cz), (w, sy, ih), color)
        make_box(f"{prefix}_Back", (cx, cy + s * (hy - w / 2.0), cz), (sx - 2.0 * w, w, ih), color)
    else:
        s = 1.0 if open_face == '-X' else -1.0
        make_box(f"{prefix}_Side_L", (cx, cy - hy + w / 2.0, cz), (sx, w, ih), color)
        make_box(f"{prefix}_Side_R", (cx, cy + hy - w / 2.0, cz), (sx, w, ih), color)
        make_box(f"{prefix}_Back", (cx + s * (hx - w / 2.0), cy, cz), (w, sy - 2.0 * w, ih), color)
