"""detail.py — shared helpers for THE DRAFTING PROGRAM's detail
passes (see lore/_SET_DETAIL_PLAYBOOK.md).

D2 surface breakup: make_traffic_wear, make_floor_stain,
    make_scuff_band, make_wall_tint_band, make_threshold
D3 infrastructure: make_wall_outlet, make_light_switch,
    make_cord_run, make_thermostat, make_corner_guard

All anchors follow the build-script frame: z-up, y=0 = south/door
wall, +Y into the room. Wall-mounted helpers take an `axis` +
`face_sign` describing which wall they sit on, matching the
make_wall convention (wall slab 0.20 thick, centered; interior face
0.10 inboard — callers pass the WALL PLANE coordinate and these
helpers push the plate proud of it by ~0.11-0.13).
"""
from .geometry import make_box, make_cyl

COL_PLATE = (0.90, 0.89, 0.84, 1.0)     # almond plastic
COL_PLATE_OLD = (0.82, 0.79, 0.68, 1.0) # yellowed almond
COL_CORD = (0.22, 0.22, 0.24, 1.0)
COL_WEAR = (0.0, 0.0, 0.0, 1.0)         # placeholder — pass real tints


def make_traffic_wear(name, waypoints, width=0.7, floor_z=0.0,
                      tint=(0.0, 0.0, 0.0, 1.0)):
    """The darker ribbon where feet actually go — door to counter,
    counter to kitchen. `waypoints` is a list of (x, y); a thin
    quad strip is laid just above the floor. `tint` should be the
    floor color darkened ~12% by the CALLER (this module can't see
    the floor palette)."""
    for i in range(len(waypoints) - 1):
        x0, y0 = waypoints[i]
        x1, y1 = waypoints[i + 1]
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        # Axis-aligned segments only (make_box has no rotation) —
        # author waypoint runs as L-shapes, not diagonals.
        sx = max(dx, 0.0) + (width if dy > dx else 0.0)
        sy = max(dy, 0.0) + (width if dx >= dy else 0.0)
        make_box(f"{name}_Seg{i}", (cx, cy, floor_z + 0.008),
                 (max(sx, width), max(sy, width), 0.006), tint)


def make_floor_stain(name, center, radius=0.22, floor_z=0.0,
                     tint=(0.0, 0.0, 0.0, 1.0), segments=8):
    """A near-flat disc just above the floor. Ring stains: call
    twice, smaller radius with the floor's own color on top."""
    cx, cy = center
    make_cyl(name, (cx, cy, floor_z + 0.006), radius, 0.004, tint,
             segments=segments)


def make_scuff_band(name, center, length, axis='X', height=0.16,
                    band_z=0.10, tint=(0.0, 0.0, 0.0, 1.0)):
    """Kick-zone scuffing on a counter face / wall base / door
    bottom. A thin dark plate proud of the surface by 5 mm; the
    caller positions it just off the face it scuffs."""
    if axis == 'X':
        size = (length, 0.012, height)
    else:
        size = (0.012, length, height)
    make_box(name, (center[0], center[1], band_z), size, tint)


def make_wall_tint_band(name, center, length, axis='X', height=0.30,
                        band_z=2.60, tint=(0.0, 0.0, 0.0, 1.0)):
    """The slightly darker gather at the top of a wall (ceiling
    shadow) or a wainscot band lower down. Thin plate proud of the
    wall plane by ~5 mm (caller offsets)."""
    if axis == 'X':
        size = (length, 0.010, height)
    else:
        size = (0.010, length, height)
    make_box(name, (center[0], center[1], band_z), size, tint)


def make_threshold(name, center, width=1.0, axis='X',
                   tint=(0.45, 0.38, 0.30, 1.0)):
    """Metal/wood strip across a doorway floor."""
    if axis == 'X':
        size = (width, 0.10, 0.02)
    else:
        size = (0.10, width, 0.02)
    make_box(name, (center[0], center[1], 0.012), size, tint)


def _wall_offsets(axis, face_sign, proud):
    """(dx, dy) pushing a plate proud of a wall plane. axis is the
    wall's RUN axis ('X' = S/N wall, plate faces ±Y; 'Y' = W/E
    wall, plate faces ±X)."""
    if axis == 'X':
        return (0.0, face_sign * proud)
    return (face_sign * proud, 0.0)


def make_wall_outlet(name, wall_point, axis='X', face_sign=1,
                     z=0.30, aged=False):
    """Duplex outlet plate at wall_point=(x, y) on the wall plane."""
    dx, dy = _wall_offsets(axis, face_sign, 0.115)
    col = COL_PLATE_OLD if aged else COL_PLATE
    x, y = wall_point
    if axis == 'X':
        make_box(f"{name}_Plate", (x + dx, y + dy, z), (0.075, 0.012, 0.115), col)
        for si, zo in enumerate((0.028, -0.028)):
            make_box(f"{name}_Socket_{si}", (x + dx, y + dy + face_sign * 0.004, z + zo),
                     (0.032, 0.006, 0.036), (0.30, 0.29, 0.27, 1.0))
    else:
        make_box(f"{name}_Plate", (x + dx, y + dy, z), (0.012, 0.075, 0.115), col)
        for si, zo in enumerate((0.028, -0.028)):
            make_box(f"{name}_Socket_{si}", (x + dx + face_sign * 0.004, y + dy, z + zo),
                     (0.006, 0.032, 0.036), (0.30, 0.29, 0.27, 1.0))


def make_light_switch(name, wall_point, axis='X', face_sign=1,
                      z=1.20, aged=False):
    """Toggle switch plate — belongs beside the door."""
    dx, dy = _wall_offsets(axis, face_sign, 0.115)
    col = COL_PLATE_OLD if aged else COL_PLATE
    x, y = wall_point
    if axis == 'X':
        make_box(f"{name}_Plate", (x + dx, y + dy, z), (0.075, 0.012, 0.115), col)
        make_box(f"{name}_Toggle", (x + dx, y + dy + face_sign * 0.012, z),
                 (0.016, 0.014, 0.030), col)
    else:
        make_box(f"{name}_Plate", (x + dx, y + dy, z), (0.012, 0.075, 0.115), col)
        make_box(f"{name}_Toggle", (x + dx + face_sign * 0.012, y + dy, z),
                 (0.014, 0.016, 0.030), col)


def make_thermostat(name, wall_point, axis='X', face_sign=1, z=1.45):
    dx, dy = _wall_offsets(axis, face_sign, 0.125)
    x, y = wall_point
    if axis == 'X':
        make_box(f"{name}_Body", (x + dx, y + dy, z), (0.11, 0.025, 0.09), COL_PLATE)
        make_box(f"{name}_Window", (x + dx, y + dy + face_sign * 0.014, z + 0.012),
                 (0.055, 0.006, 0.022), (0.55, 0.60, 0.55, 1.0))
    else:
        make_box(f"{name}_Body", (x + dx, y + dy, z), (0.025, 0.11, 0.09), COL_PLATE)
        make_box(f"{name}_Window", (x + dx + face_sign * 0.014, y + dy, z + 0.012),
                 (0.006, 0.055, 0.022), (0.55, 0.60, 0.55, 1.0))


def make_cord_run(name, from_point, to_point, sag=0.10,
                  radius=0.008, color=COL_CORD):
    """A power cord from a device (x, y, z) to an outlet (x, y, z)
    as a two-segment sagging run. Segments are thin axis-aligned
    boxes (cheap and reads correctly at VN camera distance)."""
    x0, y0, z0 = from_point
    x1, y1, z1 = to_point
    mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    mz = min(z0, z1) * 0.5 - sag + 0.05
    mz = max(mz, 0.015)
    for i, (a, b) in enumerate((((x0, y0, z0), (mx, my, mz)),
                                ((mx, my, mz), (x1, y1, z1)))):
        ax_, ay, az = a
        bx, by, bz = b
        cx, cy, cz = (ax_ + bx) / 2.0, (ay + by) / 2.0, (az + bz) / 2.0
        sx = max(abs(bx - ax_), radius * 2)
        sy = max(abs(by - ay), radius * 2)
        sz = max(abs(bz - az), radius * 2)
        make_box(f"{name}_Seg{i}", (cx, cy, cz), (sx, sy, sz), color)


def make_corner_guard(name, corner_point, height=1.2,
                      tint=(0.62, 0.63, 0.65, 1.0)):
    """Metal corner guard on a high-traffic outside corner."""
    x, y = corner_point
    make_box(f"{name}_A", (x, y, height / 2.0), (0.035, 0.012, height), tint)
    make_box(f"{name}_B", (x, y, height / 2.0), (0.012, 0.035, height), tint)


# ── D5 edge treatment · far bands (2026-08-04, THE STUMP HUNT) ────
# locale_geometry_audit found 14 exteriors whose view stopped at
# 22-60m against the 120m threshold — dioramas. The fix is always
# the same shape: receding silhouette bands along the sightline,
# each dimmer and taller-but-farther, until scene fog eats them.
# This is the shared machinery; each locale supplies its own
# palette, profile and band distances so the horizon stays in
# character (Sitka ridgelines are not Louisiana hedgerows).

def make_far_bands(prefix, base_color, bands, sides="NSEW",
                   cx=0.0, cy=0.0, profile="treeline"):
    """Receding horizon bands for an exterior.

    bands   list of (dist, half_span, height, shade) — shade scales
            base_color per ring so aerial perspective has steps.
    sides   subset of "NSEW"; leave out a side that is open water
            or already handled (a sea plane, a real skyline).
    profile 'treeline' lumpy crowns · 'ridge' long overlapping
            wedges · 'roofline' blocky steps with a chimney or two.
    """
    for i, (dist, half_span, height, shade) in enumerate(bands):
        c = (base_color[0] * shade, base_color[1] * shade,
             base_color[2] * shade, 1.0)
        for side in sides:
            if side == "N":
                ctr, half = (cx, cy + dist), (half_span, 5.0)
            elif side == "S":
                ctr, half = (cx, cy - dist), (half_span, 5.0)
            elif side == "E":
                ctr, half = (cx + dist, cy), (5.0, half_span)
            else:
                ctr, half = (cx - dist, cy), (5.0, half_span)
            nm = "%s_%s%d" % (prefix, side, i)
            make_box(nm, (ctr[0], ctr[1], height * 0.5),
                     (half[0], half[1], height * 0.5), c)
            # break the top line so the band doesn't read as a slab
            along_x = side in "NS"
            n_lumps = 3 + (i % 2)
            for j in range(n_lumps):
                t = (2 * j + 1) / (2.0 * n_lumps) - 0.5
                off = t * half_span * 1.6
                if profile == "treeline":
                    lw, lh = half_span * 0.14, height * (0.30 + 0.12 * ((i + j) % 3))
                elif profile == "ridge":
                    lw, lh = half_span * 0.34, height * 0.22
                else:  # roofline
                    lw, lh = half_span * 0.10, height * (0.35 if (i + j) % 3 else 0.55)
                lc = (ctr[0] + (off if along_x else 0.0),
                      ctr[1] + (0.0 if along_x else off))
                lhalf = ((lw, 4.0) if along_x else (4.0, lw))
                make_box("%s_%s%d_l%d" % (prefix, side, i, j),
                         (lc[0], lc[1], height + lh * 0.5),
                         (lhalf[0], lhalf[1], lh * 0.5), c)
