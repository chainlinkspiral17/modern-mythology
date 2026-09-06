import math
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


# ════════════════════════════════════════════════════════════════
# DETAIL DRAFT 1 (2026-09-05) — the roadside kit. Poles with
# crossarms, insulators and wires that SAG; a W-beam guardrail on
# posts with bolt heads; a wire fence; a ditch that is a surface.
# ════════════════════════════════════════════════════════════════

def make_utility_pole(prefix, x, y, h=9.0, crossarm=True, transformer=False, wood=(0.36, 0.28, 0.20, 1.0)):
    from .geometry import make_lathe, make_box, make_cyl
    make_lathe(f"{prefix}_Pole", (x, y, 0.0), [(0.16, 0.0), (0.15, h * 0.4), (0.12, h - 0.3), (0.11, h)], wood, segments=8)
    if crossarm:
        make_box(f"{prefix}_Crossarm", (x, y, h - 0.45), (1.9, 0.09, 0.11), wood)
        make_box(f"{prefix}_Brace_L", (x - 0.55, y + 0.06, h - 0.85), (0.05, 0.03, 0.6), (0.50, 0.50, 0.52, 1.0))
        make_box(f"{prefix}_Brace_R", (x + 0.55, y + 0.06, h - 0.85), (0.05, 0.03, 0.6), (0.50, 0.50, 0.52, 1.0))
        for ii, dx in enumerate((-0.8, -0.3, 0.3, 0.8)):
            make_lathe(f"{prefix}_Insulator_{ii}", (x + dx, y, h - 0.395),
                       [(0.03, 0.0), (0.055, 0.05), (0.04, 0.09), (0.06, 0.13), (0.045, 0.17), (0.0, 0.19)],
                       (0.30, 0.44, 0.42, 1.0), segments=8)
    if transformer:
        make_cyl(f"{prefix}_Transformer", (x + 0.32, y, h - 1.6), 0.24, 0.9, (0.42, 0.44, 0.44, 1.0), segments=10)
        make_box(f"{prefix}_Transformer_Bracket", (x + 0.14, y, h - 1.2), (0.30, 0.06, 0.05), (0.50, 0.50, 0.52, 1.0))


def make_wire_run(prefix, poles, h=9.0, sag=0.9, offsets=(-0.8, -0.3, 0.3, 0.8), color=(0.16, 0.16, 0.18, 1.0)):
    """Wires between consecutive poles [(x, y), ...] — one tube per
    span per insulator offset (offsets along the crossarm, which
    runs along X). Named *_Wire_* so the overlap audit's flexible-
    line rule forgives the pole-top contact."""
    from .geometry import make_tube, catenary
    for i, ((x0, y0), (x1, y1)) in enumerate(zip(poles, poles[1:])):
        for wi, dx in enumerate(offsets):
            path = catenary((x0 + dx, y0, h - 0.20), (x1 + dx, y1, h - 0.20), sag, n=8)
            make_tube(f"{prefix}_Wire_{i}_{wi}", path, 0.018, color, segments=5)


def make_guardrail(prefix, x, y0, y1, side=1, post_every=3.8, steel=(0.62, 0.64, 0.66, 1.0)):
    """A W-beam guardrail along Y at x: the beam is a prism with the
    W profile (extruded along Y), posts are lathed, bolt heads every
    post. `side` +1 puts the posts on +X of the beam."""
    from .geometry import make_prism, make_lathe, make_cyl
    L = y1 - y0
    ym = (y0 + y1) / 2.0
    # W profile in (u=x, v=z), 8 mm plate, ~31 cm tall
    w = [(0.0, 0.0), (0.04, 0.04), (0.04, 0.10), (0.0, 0.14), (0.04, 0.18), (0.04, 0.26), (0.0, 0.30),
         (-0.012, 0.30), (0.028, 0.26), (0.028, 0.18), (-0.012, 0.14), (0.028, 0.10), (0.028, 0.04), (-0.012, 0.0)]
    make_prism(f"{prefix}_Beam", (x, ym, 0.56), w, L, steel, axis="Y")
    n = int(L / post_every)
    for i in range(n + 1):
        py = y0 + i * post_every + 0.4
        if py > y1 - 0.2:
            break
        make_lathe(f"{prefix}_Post_{i}", (x + side * 0.10, py, 0.0),
                   [(0.07, 0.0), (0.07, 0.72), (0.06, 0.80), (0.0, 0.80)], (0.40, 0.40, 0.42, 1.0), segments=6)
        make_cyl(f"{prefix}_Bolt_{i}", (x - side * 0.016, py, 0.70), 0.02, 0.012, (0.50, 0.50, 0.52, 1.0), axis="X", segments=6)


def make_wire_fence(prefix, x, y0, y1, h=1.1, post_every=3.0, wires=3, wood=(0.50, 0.46, 0.40, 1.0), gap=None):
    """Field fence along Y at x: lathed posts with a chamfered top,
    strands as tubes with a little sag. `gap` = (ya, yb) leaves an
    opening (a gate)."""
    from .geometry import make_lathe, make_tube, catenary
    ys = []
    y = y0
    while y <= y1 + 1e-6:
        if not (gap and gap[0] < y < gap[1]):
            ys.append(y)
        y += post_every
    for i, py in enumerate(ys):
        make_lathe(f"{prefix}_Post_{i}", (x, py, 0.0), [(0.06, 0.0), (0.06, h - 0.05), (0.04, h), (0.0, h)], wood, segments=6)
    for i, (a, b) in enumerate(zip(ys, ys[1:])):
        if gap and a < gap[0] < b:
            continue
        for wi in range(wires):
            z = h - 0.10 - wi * ((h - 0.35) / max(wires - 1, 1))
            make_tube(f"{prefix}_Wire_{i}_{wi}", catenary((x, a, z), (x, b, z), 0.025, n=4), 0.006, (0.50, 0.50, 0.48, 1.0), segments=4)


def make_ditch_field(prefix, x0, x1, y0, y1, cell, ditch_x, ditch_depth=0.45, ditch_half=1.2, amp=0.08, seed=0, color=(0.36, 0.44, 0.24, 1.0), base_z=0.0):
    """A rolling ground patch with a bar ditch running along Y at
    ditch_x — the shoulder that falls away instead of a wedge."""
    from .geometry import make_heightfield, rolling_heights
    cols = int((x1 - x0) / cell) + 1
    rows = int((y1 - y0) / cell) + 1
    hs = rolling_heights(rows, cols, amp, seed=seed)
    for r in range(rows):
        for c in range(cols):
            xx = x0 + c * cell
            d = abs(xx - ditch_x)
            if d < ditch_half:
                t = 1.0 - d / ditch_half
                hs[r][c] -= ditch_depth * (t * t * (3 - 2 * t))
    make_heightfield(prefix, (x0, y0, base_z), cell, hs, color, skirt=0.4)


def make_road_bend(prefix, x0, y0, heading0, turn_deg, arc_len, run_len, width,
                   asphalt=(0.24, 0.24, 0.25, 1.0), line=(0.92, 0.86, 0.50, 1.0), edge=(0.92, 0.92, 0.88, 1.0),
                   shoulder_w=1.0, shoulder=(0.50, 0.47, 0.40, 1.0), seg_len=8.0, z=0.0, dash=True,
                   edge_lines=True):
    """A road that BENDS: from (x0, y0) heading `heading0` (radians,
    0 = +Y, positive = toward +X), an arc turning `turn_deg` over
    `arc_len`, then a straight `run_len`. Built as flat prisms
    (asphalt, shoulders, edge lines, center dashes) named
    <prefix>_* so the overlap gate treats the chain as one assembly.
    DETAIL DRAFT 3B (2026-09-06): "every road is still straight."
    Returns the end point and heading so the caller can continue."""
    from .geometry import make_prism
    hw = width / 2.0
    pts = []
    x, y, h = x0, y0, heading0
    n_arc = max(1, int(arc_len / seg_len))
    dh = math.radians(turn_deg) / n_arc
    pts.append((x, y, h))
    for i in range(n_arc):
        h += dh
        x += math.sin(h) * seg_len
        y += math.cos(h) * seg_len
        pts.append((x, y, h))
    n_run = max(1, int(run_len / seg_len))
    for i in range(n_run):
        x += math.sin(h) * seg_len
        y += math.cos(h) * seg_len
        pts.append((x, y, h))
    def left(px, py, ph, d):
        return (px - math.cos(ph) * d, py + math.sin(ph) * d)
    for i, ((ax, ay, ah), (bx, by, bh)) in enumerate(zip(pts, pts[1:])):
        cx, cy = (ax + bx) / 2.0, (ay + by) / 2.0
        def quad(dl, dr):
            a_l = left(ax, ay, ah, dl); a_r = left(ax, ay, ah, -dr)
            b_l = left(bx, by, bh, dl); b_r = left(bx, by, bh, -dr)
            return [(a_r[0] - cx, a_r[1] - cy), (b_r[0] - cx, b_r[1] - cy), (b_l[0] - cx, b_l[1] - cy), (a_l[0] - cx, a_l[1] - cy)]
        make_prism(f"{prefix}_Asphalt_{i}", (cx, cy, z), quad(hw, hw), 0.04, asphalt, axis="Z")
        if shoulder_w > 0.0:
            make_prism(f"{prefix}_Shoulder_L_{i}", (cx, cy, z - 0.005), [(u, v) for (u, v) in
                       [(left(ax, ay, ah, hw + shoulder_w)[0] - cx, left(ax, ay, ah, hw + shoulder_w)[1] - cy),
                        (left(bx, by, bh, hw + shoulder_w)[0] - cx, left(bx, by, bh, hw + shoulder_w)[1] - cy),
                        (left(bx, by, bh, hw)[0] - cx, left(bx, by, bh, hw)[1] - cy),
                        (left(ax, ay, ah, hw)[0] - cx, left(ax, ay, ah, hw)[1] - cy)]], 0.03, shoulder, axis="Z")
            make_prism(f"{prefix}_Shoulder_R_{i}", (cx, cy, z - 0.005), [(u, v) for (u, v) in
                       [(left(ax, ay, ah, -hw)[0] - cx, left(ax, ay, ah, -hw)[1] - cy),
                        (left(bx, by, bh, -hw)[0] - cx, left(bx, by, bh, -hw)[1] - cy),
                        (left(bx, by, bh, -hw - shoulder_w)[0] - cx, left(bx, by, bh, -hw - shoulder_w)[1] - cy),
                        (left(ax, ay, ah, -hw - shoulder_w)[0] - cx, left(ax, ay, ah, -hw - shoulder_w)[1] - cy)]], 0.03, shoulder, axis="Z")
        if edge_lines:
            for sgn, nm in ((1, "L"), (-1, "R")):
                d0, d1 = sgn * (hw - 0.14), sgn * (hw - 0.06)
                q = [(left(ax, ay, ah, d1)[0] - cx, left(ax, ay, ah, d1)[1] - cy), (left(bx, by, bh, d1)[0] - cx, left(bx, by, bh, d1)[1] - cy),
                     (left(bx, by, bh, d0)[0] - cx, left(bx, by, bh, d0)[1] - cy), (left(ax, ay, ah, d0)[0] - cx, left(ax, ay, ah, d0)[1] - cy)]
                if sgn < 0:
                    q = list(reversed(q))
                make_prism(f"{prefix}_Edge_{nm}_{i}", (cx, cy, z + 0.022), q, 0.005, edge, axis="Z")
        if dash and i % 2 == 0:
            mx, my, mh = (ax + bx) / 2.0, (ay + by) / 2.0, (ah + bh) / 2.0
            L = 1.5
            a2 = (mx - math.sin(mh) * L / 2.0, my - math.cos(mh) * L / 2.0)
            b2 = (mx + math.sin(mh) * L / 2.0, my + math.cos(mh) * L / 2.0)
            q = [(left(a2[0], a2[1], mh, -0.05)[0] - cx, left(a2[0], a2[1], mh, -0.05)[1] - cy), (left(b2[0], b2[1], mh, -0.05)[0] - cx, left(b2[0], b2[1], mh, -0.05)[1] - cy),
                 (left(b2[0], b2[1], mh, 0.05)[0] - cx, left(b2[0], b2[1], mh, 0.05)[1] - cy), (left(a2[0], a2[1], mh, 0.05)[0] - cx, left(a2[0], a2[1], mh, 0.05)[1] - cy)]
            make_prism(f"{prefix}_Dash_{i}", (cx, cy, z + 0.022), q, 0.005, line, axis="Z")
    return pts[-1]
