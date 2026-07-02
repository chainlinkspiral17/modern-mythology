"""
infra_library.py
══════════════════════════════════════════════════════════════════
Reusable suburban / urban INFRASTRUCTURE primitives for HCE,
Graustark, and any future district scripts.

Import from a build script:
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from infra_library import (
        highway_segment, suburban_drive, four_way_intersection,
        roundabout, cul_de_sac, circle_drive, bridge,
        crosswalk, parking_row, double_yellow,
        streetlight_pole, stop_sign, stop_light, utility_pole,
        fire_hydrant, mailbox, mailbox_cluster, bus_stop,
        COL_ASPHALT, COL_SIDEWALK, COL_PAINT_WHITE, COL_PAINT_YELLOW,
        ...
    )

Coordinate frame matches the build scripts:
    Blender Z-up, +X east, +Y north, 1 unit = 1 metre.
    glTF export converts to Y-up for Godot.

All functions add objects to the CURRENT Blender scene and return
the created object(s) so a caller can chain or tag them.

Per _3D_MODELING_PLAYBOOK.md:
  · Vertex-colour material zones (no textures)
  · Low-poly PS2-era silhouettes; round things use 6-12 segments
  · Material identities (asphalt vs paint vs concrete) are colour-
    distinct so the screen-space shaders can read each surface
══════════════════════════════════════════════════════════════════
"""

import math
import bpy

# ════════════════════════════════════════════════════════════════
# COLOURS — shared infrastructure palette
# Reusable across every build script. Hard surfaces (no seasonal
# variation). Seasonal lawn/buffer colours come from each build
# script's local SEASON parameter.
# ════════════════════════════════════════════════════════════════

COL_ASPHALT       = (0.22, 0.22, 0.22, 1.0)
COL_ASPHALT_FRESH = (0.16, 0.16, 0.17, 1.0)   # newer pavement, darker
COL_ASPHALT_AGED  = (0.30, 0.28, 0.24, 1.0)   # sun-baked
COL_PAINT_YELLOW  = (0.78, 0.66, 0.18, 1.0)
COL_PAINT_WHITE   = (0.86, 0.84, 0.78, 1.0)
COL_CURB          = (0.55, 0.55, 0.54, 1.0)
COL_SIDEWALK      = (0.72, 0.70, 0.66, 1.0)
COL_CONCRETE      = (0.78, 0.76, 0.70, 1.0)
COL_MEDIAN_GRASS  = (0.30, 0.50, 0.20, 1.0)
COL_SHOULDER      = (0.42, 0.40, 0.32, 1.0)   # gravel shoulder
COL_RUMBLE_STRIP  = (0.30, 0.28, 0.26, 1.0)

# Signage / fixtures
COL_POLE_DARK     = (0.28, 0.26, 0.22, 1.0)   # streetlight pole
COL_POLE_WOOD     = (0.32, 0.26, 0.20, 1.0)   # creosote utility pole
COL_WIRE          = (0.18, 0.18, 0.18, 1.0)
COL_SODIUM_HEAD   = (0.92, 0.62, 0.30, 1.0)   # sodium fixture (cold)
COL_LED_HEAD      = (0.92, 0.94, 0.95, 1.0)   # LED fixture (cold)
COL_TRANSFORMER   = (0.45, 0.45, 0.42, 1.0)
COL_HYDRANT_RED   = (0.78, 0.18, 0.16, 1.0)
COL_HYDRANT_YEL   = (0.85, 0.72, 0.20, 1.0)
COL_HYDRANT_BLU   = (0.18, 0.32, 0.62, 1.0)
COL_MAILBOX       = (0.55, 0.55, 0.55, 1.0)
COL_MAILBOX_RED   = (0.78, 0.18, 0.16, 1.0)   # flag
COL_STOP_RED      = (0.85, 0.18, 0.16, 1.0)
COL_STOP_WHITE    = (0.92, 0.90, 0.84, 1.0)
COL_YIELD_YELLOW  = (0.95, 0.78, 0.20, 1.0)
COL_SIGN_GREEN    = (0.18, 0.42, 0.26, 1.0)   # street-name signs
COL_SIGN_BROWN    = (0.40, 0.30, 0.20, 1.0)   # park signs
COL_STOPLIGHT_BOX = (0.18, 0.18, 0.18, 1.0)
COL_STOPLIGHT_R   = (0.90, 0.16, 0.14, 1.0)
COL_STOPLIGHT_A   = (0.95, 0.65, 0.18, 1.0)
COL_STOPLIGHT_G   = (0.30, 0.78, 0.34, 1.0)
COL_BENCH         = (0.42, 0.30, 0.20, 1.0)
COL_TRASHCAN      = (0.32, 0.32, 0.30, 1.0)
COL_SHELTER_ROOF  = (0.30, 0.30, 0.32, 1.0)


# ════════════════════════════════════════════════════════════════
# PRIMITIVES
# Self-contained so this module can be imported without touching
# the host script's own helpers.
# ════════════════════════════════════════════════════════════════

def _finalize_mesh(name, verts, faces, base_color):
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="Col")
    layer = mesh.vertex_colors["Col"]
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            layer.data[li].color = base_color
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def _box(name, center, size, color, open_faces=None):
    open_faces = open_faces or set()
    cx, cy, cz = center
    sx, sy, sz = size
    hx, hy, hz = sx/2, sy/2, sz/2
    verts = [
        (cx-hx, cy-hy, cz-hz), (cx+hx, cy-hy, cz-hz),
        (cx+hx, cy+hy, cz-hz), (cx-hx, cy+hy, cz-hz),
        (cx-hx, cy-hy, cz+hz), (cx+hx, cy-hy, cz+hz),
        (cx+hx, cy+hy, cz+hz), (cx-hx, cy+hy, cz+hz),
    ]
    face_defs = [
        ('-Z', (0,3,2,1)), ('+Z', (4,5,6,7)),
        ('-Y', (0,1,5,4)), ('+Y', (2,3,7,6)),
        ('-X', (3,0,4,7)), ('+X', (1,2,6,5)),
    ]
    faces = [list(vids) for (tag, vids) in face_defs if tag not in open_faces]
    return _finalize_mesh(name, verts, faces, color)


def _cyl(name, center, radius, height, color, segments=8, axis='Z'):
    cx, cy, cz = center
    h2 = height / 2.0
    verts = []
    for ring in (0, 1):
        z_off = -h2 if ring == 0 else h2
        for i in range(segments):
            ang = 2.0 * math.pi * i / segments
            a = math.cos(ang) * radius
            b = math.sin(ang) * radius
            if axis == 'Z':
                verts.append((cx + a, cy + b, cz + z_off))
            elif axis == 'Y':
                verts.append((cx + a, cy + z_off, cz + b))
            else:
                verts.append((cx + z_off, cy + a, cz + b))
    faces = []
    for i in range(segments):
        ni = (i + 1) % segments
        faces.append([i, ni, ni + segments, i + segments])
    faces.append(list(reversed(range(segments))))
    faces.append(list(range(segments, segments * 2)))
    return _finalize_mesh(name, verts, faces, color)


def _plane(name, x0, y0, x1, y1, z, color):
    if x0 > x1: x0, x1 = x1, x0
    if y0 > y1: y0, y1 = y1, y0
    verts = [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]
    return _finalize_mesh(name, verts, [[0, 1, 2, 3]], color)


def _ring(name, center, inner_r, outer_r, z, color, segments=24):
    """Annulus — flat ring quad strip. For roundabouts, circle drives."""
    cx, cy, cz = center
    verts = []
    for i in range(segments):
        ang = 2.0 * math.pi * i / segments
        ca, sa = math.cos(ang), math.sin(ang)
        verts.append((cx + ca * inner_r, cy + sa * inner_r, cz))   # inner
        verts.append((cx + ca * outer_r, cy + sa * outer_r, cz))   # outer
    faces = []
    for i in range(segments):
        ni = (i + 1) % segments
        a = i * 2; b = i * 2 + 1
        c = ni * 2 + 1; d = ni * 2
        faces.append([a, b, c, d])
    return _finalize_mesh(name, verts, faces, color)


def _disc(name, center, radius, z, color, segments=24):
    """Filled disc. For roundabout centre island, manhole covers."""
    cx, cy, cz = center
    verts = [(cx, cy, cz)]
    for i in range(segments):
        ang = 2.0 * math.pi * i / segments
        verts.append((cx + math.cos(ang) * radius,
                      cy + math.sin(ang) * radius, cz))
    faces = []
    for i in range(segments):
        ni = (i + 1) % segments
        faces.append([0, 1 + i, 1 + ni])
    return _finalize_mesh(name, verts, faces, color)


# ════════════════════════════════════════════════════════════════
# ROADS — segments + intersections
# Coordinates: (x, y) = the road centre line in world metres.
# Z = ground (typically 0.0). Asphalt sits 0..0.01 above ground.
# ════════════════════════════════════════════════════════════════

def road_segment(name, p0, p1, width, color=COL_ASPHALT,
                 z=0.0, paint=None):
    """Straight road segment from p0 (x, y) to p1 (x, y).

    width: total road width in metres (no shoulder included).
    paint: optional string:
       'double_yellow'  · two yellow lines down the middle
       'single_yellow'  · single yellow centre line
       'dashed_white'   · dashed white centre line (residential)
       None             · plain asphalt
    """
    x0, y0 = p0; x1, y1 = p1
    dx = x1 - x0; dy = y1 - y0
    length = math.hypot(dx, dy)
    if length < 0.001:
        return None
    # Compute the centre + the perpendicular vector
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    ang = math.atan2(dy, dx)
    # We'll build the rectangle in world-aligned form by emitting
    # the 4 corner verts directly rather than using a box transform.
    perp_x = -math.sin(ang)
    perp_y =  math.cos(ang)
    half_w = width / 2.0
    verts = [
        (x0 - perp_x * half_w, y0 - perp_y * half_w, z),
        (x1 - perp_x * half_w, y1 - perp_y * half_w, z),
        (x1 + perp_x * half_w, y1 + perp_y * half_w, z),
        (x0 + perp_x * half_w, y0 + perp_y * half_w, z),
    ]
    _finalize_mesh(name, verts, [[0, 1, 2, 3]], color)
    if paint == 'double_yellow':
        _paint_double(name + "_Yellow", p0, p1, ang, z + 0.01)
    elif paint == 'single_yellow':
        _paint_centerline(name + "_Yellow", p0, p1, ang, z + 0.01,
                          color=COL_PAINT_YELLOW)
    elif paint == 'dashed_white':
        _paint_dashed(name + "_Dashed", p0, p1, ang, z + 0.01,
                      color=COL_PAINT_WHITE)
    return None


def _paint_centerline(name, p0, p1, ang, z, color):
    x0, y0 = p0; x1, y1 = p1
    perp_x = -math.sin(ang)
    perp_y =  math.cos(ang)
    half_w = 0.07
    verts = [
        (x0 - perp_x * half_w, y0 - perp_y * half_w, z),
        (x1 - perp_x * half_w, y1 - perp_y * half_w, z),
        (x1 + perp_x * half_w, y1 + perp_y * half_w, z),
        (x0 + perp_x * half_w, y0 + perp_y * half_w, z),
    ]
    _finalize_mesh(name, verts, [[0, 1, 2, 3]], color)


def _paint_double(name, p0, p1, ang, z):
    perp_x = -math.sin(ang)
    perp_y =  math.cos(ang)
    for sign, tag in ((-1, 'L'), (1, 'R')):
        off = sign * 0.18
        p0o = (p0[0] + perp_x * off, p0[1] + perp_y * off)
        p1o = (p1[0] + perp_x * off, p1[1] + perp_y * off)
        _paint_centerline(name + tag, p0o, p1o, ang, z, COL_PAINT_YELLOW)


def _paint_dashed(name, p0, p1, ang, z, color):
    x0, y0 = p0; x1, y1 = p1
    length = math.hypot(x1 - x0, y1 - y0)
    n = max(1, int(length / 6.0))
    dash_l = 3.0
    gap_l = 3.0
    for i in range(n):
        t0 = (i * (dash_l + gap_l)) / length
        t1 = (i * (dash_l + gap_l) + dash_l) / length
        if t1 > 1.0: t1 = 1.0
        sp0 = (x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0)
        sp1 = (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)
        _paint_centerline(f"{name}_{i}", sp0, sp1, ang, z, color)
        if t1 >= 1.0:
            break


def highway_segment(name, p0, p1, lanes=4, with_shoulder=True,
                    with_median=True, z=0.0):
    """A divided highway. 4 lanes (2 each way) by default with a
    grass median between directions. Includes gravel shoulders on
    both outside edges. Width:
      lanes * 3.6 m  + median 3.0 m + shoulder 2.5 m each side."""
    lane_w = 3.6
    median_w = 3.0 if with_median else 0.0
    shoulder_w = 2.5 if with_shoulder else 0.0
    half_lanes = lanes // 2
    travel_w = lane_w * half_lanes
    total_w = 2 * travel_w + median_w + 2 * shoulder_w

    x0, y0 = p0; x1, y1 = p1
    ang = math.atan2(y1 - y0, x1 - x0)
    perp_x = -math.sin(ang); perp_y = math.cos(ang)

    # Outer shoulders
    if with_shoulder:
        for sign in (-1, 1):
            off = sign * (median_w / 2 + travel_w + shoulder_w / 2)
            cp0 = (x0 + perp_x * off, y0 + perp_y * off)
            cp1 = (x1 + perp_x * off, y1 + perp_y * off)
            road_segment(f"{name}_Shoulder_{sign:+d}", cp0, cp1,
                         shoulder_w, color=COL_SHOULDER, z=z)
    # Travel lanes on each side of the median
    for sign in (-1, 1):
        off = sign * (median_w / 2 + travel_w / 2)
        cp0 = (x0 + perp_x * off, y0 + perp_y * off)
        cp1 = (x1 + perp_x * off, y1 + perp_y * off)
        road_segment(f"{name}_Lanes_{sign:+d}", cp0, cp1, travel_w,
                     color=COL_ASPHALT, z=z + 0.001,
                     paint='dashed_white' if half_lanes > 1 else None)
        # Solid edge line on the shoulder side
        edge_off = sign * (travel_w / 2 - 0.18)
        ep0 = (cp0[0] + perp_x * edge_off, cp0[1] + perp_y * edge_off)
        ep1 = (cp1[0] + perp_x * edge_off, cp1[1] + perp_y * edge_off)
        _paint_centerline(f"{name}_EdgeLine_{sign:+d}", ep0, ep1, ang,
                          z + 0.012, COL_PAINT_WHITE)
    # Grass median
    if with_median:
        road_segment(f"{name}_Median", p0, p1, median_w,
                     color=COL_MEDIAN_GRASS, z=z + 0.001)


def suburban_drive(name, p0, p1, width=11.0, z=0.0,
                   paint='single_yellow', with_sidewalk=True,
                   sidewalk_w=1.8, buffer_w=0.8):
    """Residential street with optional sidewalk + planted buffer.
    Width per _HCE_TOPOGRAPHY.md ROAD_W = 11 m, SIDE_W = 1.8 m,
    BUFFER_W = 2.5 m (this default uses 0.8 m for tighter blocks)."""
    road_segment(name + "_Road", p0, p1, width, z=z, paint=paint)
    if with_sidewalk:
        x0, y0 = p0; x1, y1 = p1
        ang = math.atan2(y1 - y0, x1 - x0)
        perp_x = -math.sin(ang); perp_y = math.cos(ang)
        for sign in (-1, 1):
            # Buffer strip just outside the road
            buf_off = sign * (width / 2 + buffer_w / 2)
            bp0 = (x0 + perp_x * buf_off, y0 + perp_y * buf_off)
            bp1 = (x1 + perp_x * buf_off, y1 + perp_y * buf_off)
            road_segment(f"{name}_Buffer_{sign:+d}", bp0, bp1,
                         buffer_w, color=COL_MEDIAN_GRASS, z=z + 0.002)
            # Sidewalk outside the buffer
            sw_off = sign * (width / 2 + buffer_w + sidewalk_w / 2)
            sp0 = (x0 + perp_x * sw_off, y0 + perp_y * sw_off)
            sp1 = (x1 + perp_x * sw_off, y1 + perp_y * sw_off)
            road_segment(f"{name}_Sidewalk_{sign:+d}", sp0, sp1,
                         sidewalk_w, color=COL_SIDEWALK, z=z + 0.003)


def four_way_intersection(name, center, ns_width=14.0, ew_width=14.0,
                          z=0.0, with_crosswalks=True):
    """4-way perpendicular intersection. Just the asphalt patch +
    crosswalks. The arterial roads connecting to it are separate
    suburban_drive / highway_segment calls."""
    cx, cy = center
    half_n = ns_width / 2
    half_e = ew_width / 2
    # NS asphalt across the intersection
    _plane(f"{name}_AsphaltNS",
           cx - half_n, cy - half_e, cx + half_n, cy + half_e,
           z, COL_ASPHALT)
    if with_crosswalks:
        for leg, axis in [('N', '+Y'), ('S', '-Y'), ('E', '+X'), ('W', '-X')]:
            crosswalk(f"{name}_CW_{leg}",
                      (cx + (half_n + 0.5) * (1 if axis == '+X' else (-1 if axis == '-X' else 0)),
                       cy + (half_e + 0.5) * (1 if axis == '+Y' else (-1 if axis == '-Y' else 0))),
                      axis,
                      ns_width if axis in ('+Y', '-Y') else ew_width,
                      z=z + 0.025)


def crosswalk(name, position, axis, width, z=0.025, stripes=6):
    """Standard zebra crosswalk. axis ∈ {'+X','-X','+Y','-Y'} is
    the direction the crosswalk runs (pedestrian travel direction).
    width = perpendicular extent (the road width being crossed)."""
    cx, cy = position
    stripe_w = (width - 1.0) / stripes
    for i in range(stripes):
        off = -width / 2 + 0.5 + i * (width - 1.0) / (stripes - 1)
        if axis in ('+X', '-X'):
            # crosswalk runs E-W; stripes perpendicular to that — bars run N-S
            _plane(f"{name}_S{i}",
                   cx - 0.30, cy + off - 0.05,
                   cx + 0.30, cy + off + 0.05,
                   z, COL_PAINT_WHITE)
        else:
            # crosswalk runs N-S; stripes E-W
            _plane(f"{name}_S{i}",
                   cx + off - 0.05, cy - 0.30,
                   cx + off + 0.05, cy + 0.30,
                   z, COL_PAINT_WHITE)


def parking_row(name, start, end, n_spaces, depth=5.5, angle='perp',
                z=0.0):
    """A row of parking spaces. start/end define the curb-side edge.
    angle='perp' (90°) is the default supermarket-row angle."""
    x0, y0 = start; x1, y1 = end
    ang = math.atan2(y1 - y0, x1 - x0)
    perp_x = -math.sin(ang); perp_y = math.cos(ang)
    length = math.hypot(x1 - x0, y1 - y0)
    space_w = length / n_spaces
    # Asphalt pad behind the row
    pad_cx = (x0 + x1) / 2 + perp_x * depth / 2
    pad_cy = (y0 + y1) / 2 + perp_y * depth / 2
    # Approximate as a rectangle in world coords (axis-aligned ok at
    # small angles; for now we just place the pad along world axes)
    _plane(f"{name}_Pad",
           min(x0, x1) - 0.1,
           min(y0, y1) - 0.1,
           max(x0, x1) + perp_x * depth + 0.1,
           max(y0, y1) + perp_y * depth + 0.1,
           z, COL_ASPHALT)
    # Painted stall lines (white) — one per space boundary
    for i in range(n_spaces + 1):
        t = i / n_spaces
        bx = x0 + (x1 - x0) * t
        by = y0 + (y1 - y0) * t
        ex = bx + perp_x * depth
        ey = by + perp_y * depth
        _paint_centerline(f"{name}_Line_{i}", (bx, by), (ex, ey),
                          ang + math.pi / 2, z + 0.01, COL_PAINT_WHITE)


def roundabout(name, center, outer_r=20.0, inner_r=8.0, z=0.0,
               n_legs=4, leg_width=11.0):
    """Roundabout with a central island (planted green) and a circular
    asphalt ring. n_legs straight road stubs extend outward to
    n_legs cardinal directions, ready to be tied into a wider grid.

    outer_r · the outer edge of the asphalt ring
    inner_r · the inner edge (the green island's radius)
    """
    cx, cy = center
    # Asphalt annulus
    _ring(f"{name}_Asphalt", (cx, cy, z), inner_r, outer_r, z, COL_ASPHALT)
    # Central green island
    _disc(f"{name}_Island", (cx, cy, z + 0.001), inner_r * 0.95, z + 0.001,
          COL_MEDIAN_GRASS)
    # Inner curb ring (raised concrete around the island)
    _ring(f"{name}_InnerCurb", (cx, cy, z + 0.001), inner_r * 0.95,
          inner_r, z + 0.001, COL_CURB)
    # Outer curb ring
    _ring(f"{name}_OuterCurb", (cx, cy, z + 0.001), outer_r,
          outer_r + 0.25, z + 0.001, COL_CURB)
    # Dashed white lane line in the middle of the ring
    mid_r = (inner_r + outer_r) / 2
    n_dashes = max(8, int(2 * math.pi * mid_r / 3.0))
    for i in range(n_dashes):
        a0 = 2 * math.pi * i / n_dashes
        a1 = 2 * math.pi * (i + 0.5) / n_dashes
        p0 = (cx + math.cos(a0) * mid_r, cy + math.sin(a0) * mid_r)
        p1 = (cx + math.cos(a1) * mid_r, cy + math.sin(a1) * mid_r)
        _paint_centerline(f"{name}_LaneDash_{i}", p0, p1,
                          math.atan2(p1[1]-p0[1], p1[0]-p0[0]),
                          z + 0.012, COL_PAINT_WHITE)
    # Approach road stubs — straight legs extending outward, equal
    # angle spacing. Caller can extend with their own suburban_drive
    # calls beyond the stubs if they want continuing roads.
    stub_len = 18.0
    for i in range(n_legs):
        a = 2 * math.pi * i / n_legs
        sp_start = (cx + math.cos(a) * outer_r, cy + math.sin(a) * outer_r)
        sp_end = (cx + math.cos(a) * (outer_r + stub_len),
                  cy + math.sin(a) * (outer_r + stub_len))
        suburban_drive(f"{name}_Stub_{i}", sp_start, sp_end,
                       width=leg_width, z=z, paint='single_yellow',
                       with_sidewalk=False)


def cul_de_sac(name, center, radius=12.0, entry_dir='+Y',
               entry_width=8.0, z=0.0):
    """Dead-end residential loop. The 'bulb' at the closed end of
    the street. entry_dir is the direction the entry road comes
    from (the side where the road STILL goes, opposite the dead end).
    """
    cx, cy = center
    # Asphalt disc for the turn-around
    _disc(f"{name}_Asphalt", (cx, cy, z + 0.001), radius, z + 0.001,
          COL_ASPHALT)
    # Curb ring
    _ring(f"{name}_Curb", (cx, cy, z + 0.001), radius,
          radius + 0.25, z + 0.001, COL_CURB)
    # Sidewalk ring outside the curb
    _ring(f"{name}_Sidewalk", (cx, cy, z + 0.002), radius + 0.25,
          radius + 0.25 + 1.6, z + 0.002, COL_SIDEWALK)
    # Cut the entry — fill back asphalt where the road connects
    # (just a thick straight stub)
    if entry_dir == '+Y':
        suburban_drive(f"{name}_Entry", (cx, cy + radius + 0.25),
                       (cx, cy + radius + 14), width=entry_width,
                       z=z, paint='single_yellow', with_sidewalk=True)
    elif entry_dir == '-Y':
        suburban_drive(f"{name}_Entry", (cx, cy - radius - 14),
                       (cx, cy - radius - 0.25), width=entry_width,
                       z=z, paint='single_yellow', with_sidewalk=True)
    elif entry_dir == '+X':
        suburban_drive(f"{name}_Entry", (cx + radius + 0.25, cy),
                       (cx + radius + 14, cy), width=entry_width,
                       z=z, paint='single_yellow', with_sidewalk=True)
    else:
        suburban_drive(f"{name}_Entry", (cx - radius - 14, cy),
                       (cx - radius - 0.25, cy), width=entry_width,
                       z=z, paint='single_yellow', with_sidewalk=True)


def circle_drive(name, center, radius=15.0, drive_w=4.5, z=0.0,
                 entry_dirs=('+Y',)):
    """Private circular driveway — a partial ring (often in front of
    larger homes / clubhouses). entry_dirs lists the cardinal points
    where the drive opens onto the street."""
    cx, cy = center
    _ring(f"{name}_Drive", (cx, cy, z), radius - drive_w / 2,
          radius + drive_w / 2, z, COL_ASPHALT)
    # Lawn island inside
    _disc(f"{name}_Lawn", (cx, cy, z + 0.001),
          radius - drive_w / 2 - 0.1, z + 0.001, COL_MEDIAN_GRASS)
    # Connector stubs at each entry direction
    for d in entry_dirs:
        if d == '+Y':
            ang = math.pi / 2
        elif d == '-Y':
            ang = -math.pi / 2
        elif d == '+X':
            ang = 0
        elif d == '-X':
            ang = math.pi
        else:
            continue
        ex, ey = cx + math.cos(ang) * radius, cy + math.sin(ang) * radius
        # Short stub leading away from the circle
        stub_end = (cx + math.cos(ang) * (radius + 8),
                    cy + math.sin(ang) * (radius + 8))
        suburban_drive(f"{name}_Connector_{d}", (ex, ey), stub_end,
                       width=drive_w, z=z, paint=None,
                       with_sidewalk=False)


def bridge(name, p0, p1, width, deck_h=2.5, z=0.0,
           with_rails=True):
    """Road bridge — deck raised above the ground (e.g. crossing
    a creek). Includes two stone abutments at each end and side
    rails along the deck."""
    x0, y0 = p0; x1, y1 = p1
    ang = math.atan2(y1 - y0, x1 - x0)
    perp_x = -math.sin(ang); perp_y = math.cos(ang)
    length = math.hypot(x1 - x0, y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    # Deck slab
    verts = [
        (x0 - perp_x * width / 2, y0 - perp_y * width / 2, z + deck_h - 0.20),
        (x1 - perp_x * width / 2, y1 - perp_y * width / 2, z + deck_h - 0.20),
        (x1 + perp_x * width / 2, y1 + perp_y * width / 2, z + deck_h - 0.20),
        (x0 + perp_x * width / 2, y0 + perp_y * width / 2, z + deck_h - 0.20),
        # bottom of deck
        (x0 - perp_x * width / 2, y0 - perp_y * width / 2, z + deck_h - 0.50),
        (x1 - perp_x * width / 2, y1 - perp_y * width / 2, z + deck_h - 0.50),
        (x1 + perp_x * width / 2, y1 + perp_y * width / 2, z + deck_h - 0.50),
        (x0 + perp_x * width / 2, y0 + perp_y * width / 2, z + deck_h - 0.50),
    ]
    faces = [
        [0, 1, 2, 3],     # top (driving surface)
        [4, 7, 6, 5],     # bottom
        [0, 4, 5, 1],     # west side
        [2, 6, 7, 3],     # east side
        [0, 3, 7, 4],     # south face
        [1, 5, 6, 2],     # north face
    ]
    _finalize_mesh(name + "_Deck", verts, faces, COL_CONCRETE)
    # Abutments at each end (small stone blocks)
    for end_pt, tag in ((p0, 'A'), (p1, 'B')):
        _box(f"{name}_Abutment_{tag}",
             (end_pt[0], end_pt[1], z + deck_h / 2),
             (width + 0.6, 0.8, deck_h), COL_CONCRETE)
    # Side rails
    if with_rails:
        rail_h = 1.0
        for sign in (-1, 1):
            r_off = sign * (width / 2 - 0.15)
            r_x0 = x0 + perp_x * r_off; r_y0 = y0 + perp_y * r_off
            r_x1 = x1 + perp_x * r_off; r_y1 = y1 + perp_y * r_off
            # Rail as a thin tall box along the deck edge
            mx, my = (r_x0 + r_x1) / 2, (r_y0 + r_y1) / 2
            # Approximation — axis-aligned box, length along longer axis
            if abs(r_x1 - r_x0) > abs(r_y1 - r_y0):
                _box(f"{name}_Rail_{sign:+d}",
                     (mx, my, z + deck_h + rail_h / 2),
                     (length, 0.10, rail_h), COL_POLE_DARK)
            else:
                _box(f"{name}_Rail_{sign:+d}",
                     (mx, my, z + deck_h + rail_h / 2),
                     (0.10, length, rail_h), COL_POLE_DARK)


# ════════════════════════════════════════════════════════════════
# FIXTURES — signage + utility + civic furniture
# ════════════════════════════════════════════════════════════════

def streetlight_pole(name, position, head_dir='+X', pole_h=7.5,
                     arm_len=2.5, head_color=COL_SODIUM_HEAD, z=0.0):
    """Cobra-head streetlight. head_dir is the cardinal direction the
    arm reaches (where the road is). Returns the pole object."""
    cx, cy = position
    if head_dir == '+X':
        dx, dy = 1, 0
    elif head_dir == '-X':
        dx, dy = -1, 0
    elif head_dir == '+Y':
        dx, dy = 0, 1
    else:
        dx, dy = 0, -1
    _cyl(f"{name}_Pole", (cx, cy, z + pole_h / 2), 0.12, pole_h,
         COL_POLE_DARK, segments=8)
    # Arm
    arm_cx = cx + dx * arm_len / 2
    arm_cy = cy + dy * arm_len / 2
    _box(f"{name}_Arm",
         (arm_cx, arm_cy, z + pole_h - 0.30),
         (max(0.10, abs(dx) * arm_len), max(0.10, abs(dy) * arm_len), 0.10),
         COL_POLE_DARK)
    # Head
    head_cx = cx + dx * arm_len
    head_cy = cy + dy * arm_len
    _box(f"{name}_Head",
         (head_cx, head_cy, z + pole_h - 0.50),
         (0.70, 0.50, 0.30), head_color)


def stop_sign(name, position, facing='+X', z=0.0, post_h=2.4):
    """Stop sign — red octagon-shaped panel on a grey post.
    facing is the cardinal direction the SIGN FACE points (where
    the driver approaches from)."""
    cx, cy = position
    _cyl(f"{name}_Post", (cx, cy, z + post_h / 2), 0.05, post_h,
         COL_POLE_DARK, segments=6)
    # Sign face — a small thin box approximating the octagon
    if facing in ('+X', '-X'):
        size = (0.06, 0.70, 0.70)
    else:
        size = (0.70, 0.06, 0.70)
    _box(f"{name}_Face",
         (cx, cy, z + post_h - 0.20),
         size, COL_STOP_RED)
    # White border / "STOP" text suggestion — a thin white inset
    if facing in ('+X', '-X'):
        size_inner = (0.07, 0.50, 0.18)
    else:
        size_inner = (0.50, 0.07, 0.18)
    _box(f"{name}_Text",
         (cx, cy, z + post_h - 0.20),
         size_inner, COL_STOP_WHITE)


def stop_light(name, position, z_top=6.5, n_lights=3):
    """3-color hanging stop light on a thin stub. position is
    where the light hangs (typically over the centre of a lane).
    z_top is the height of the top of the light box."""
    cx, cy = position
    # Hanging stub (cable)
    _cyl(f"{name}_Stub", (cx, cy, z_top + 0.30), 0.05, 0.6,
         COL_STOPLIGHT_BOX, segments=6)
    # Housing
    _box(f"{name}_Housing", (cx - 0.20, cy, z_top - 0.45),
         (0.10, 0.34, 0.95), COL_STOPLIGHT_BOX)
    colors = [COL_STOPLIGHT_R, COL_STOPLIGHT_A, COL_STOPLIGHT_G]
    for i in range(min(n_lights, 3)):
        _box(f"{name}_Lens_{i}",
             (cx, cy, z_top - i * 0.30),
             (0.32, 0.30, 0.28), colors[i])


def utility_pole(name, position, pole_h=9.0, z=0.0,
                 with_transformer=False):
    """Wooden creosote pole with a horizontal crossbar at the top.
    with_transformer adds a transformer can mounted to one side."""
    cx, cy = position
    _cyl(f"{name}_Pole", (cx, cy, z + pole_h / 2), 0.20, pole_h,
         COL_POLE_WOOD, segments=6)
    _box(f"{name}_Crossbar",
         (cx, cy, z + pole_h - 0.30),
         (2.2, 0.16, 0.16), COL_POLE_WOOD)
    if with_transformer:
        _cyl(f"{name}_Transformer",
             (cx + 0.40, cy, z + pole_h - 1.4),
             0.30, 0.90, COL_TRANSFORMER, segments=8)


def utility_wire(name, p0, p1, z_top, sag=0.4):
    """Approximate a power wire as a thin box between two pole tops.
    sag would be implemented as a polyline if we cared about the
    catenary — for low-poly we keep it straight."""
    x0, y0 = p0; x1, y1 = p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    length = math.hypot(x1 - x0, y1 - y0)
    if abs(x1 - x0) > abs(y1 - y0):
        _box(name, (mx, my, z_top - sag * 0.5),
             (length, 0.04, 0.04), COL_WIRE)
    else:
        _box(name, (mx, my, z_top - sag * 0.5),
             (0.04, length, 0.04), COL_WIRE)


def fire_hydrant(name, position, z=0.0, color=COL_HYDRANT_RED):
    """The classic stubby hydrant. ~0.7 m tall, 0.22 m wide barrel."""
    cx, cy = position
    # Barrel
    _cyl(f"{name}_Barrel", (cx, cy, z + 0.35), 0.18, 0.70,
         color, segments=8)
    # Top cap (dome)
    _cyl(f"{name}_Cap", (cx, cy, z + 0.75), 0.10, 0.10,
         color, segments=6)
    # Two side outlets
    for sign in (-1, 1):
        _cyl(f"{name}_Outlet_{sign:+d}",
             (cx + sign * 0.18, cy, z + 0.45),
             0.08, 0.10, color, segments=6, axis='X')


def mailbox(name, position, facing='+X', z=0.0):
    """Single mailbox on a post — the rural / suburban kind. Flag
    on one side (the lithograph red bleed gate fires on the flag
    when it's up — uncomment to randomise that)."""
    cx, cy = position
    _cyl(f"{name}_Post", (cx, cy, z + 0.55), 0.04, 1.10,
         COL_POLE_WOOD, segments=4)
    # Box (the actual mailbox — half-cylinder approx with a box)
    if facing in ('+X', '-X'):
        _box(f"{name}_Box", (cx, cy, z + 1.15), (0.45, 0.18, 0.18),
             COL_MAILBOX)
    else:
        _box(f"{name}_Box", (cx, cy, z + 1.15), (0.18, 0.45, 0.18),
             COL_MAILBOX)


def mailbox_cluster(name, position, count=4, z=0.0):
    """The shared mailbox bank at the entrance of a Phase II / III
    subdivision. Per _VOL6_WIKI.md a key social marker — Maya's
    zines drop here, Norman Lott's NexCorp branding flyers go up,
    etc. A horizontal bank of count individual boxes on a single
    crossbeam."""
    cx, cy = position
    span = max(1.0, (count - 1) * 0.35)
    # Two support posts
    for sign in (-1, 1):
        _cyl(f"{name}_Post_{sign:+d}",
             (cx + sign * (span / 2 + 0.30), cy, z + 0.65),
             0.06, 1.30, COL_POLE_DARK, segments=4)
    # Crossbeam plank
    _box(f"{name}_Plank",
         (cx, cy, z + 1.15),
         (span + 0.80, 0.30, 0.20), COL_BENCH)
    # Individual boxes on top of the plank
    for i in range(count):
        ox = -span / 2 + i * (span / max(1, count - 1)) if count > 1 else 0
        _box(f"{name}_Box_{i}",
             (cx + ox, cy, z + 1.40),
             (0.30, 0.18, 0.20), COL_MAILBOX)


def bus_stop(name, position, facing='+Y', z=0.0, with_shelter=True):
    """Bus stop sign + optional 3-sided shelter with a bench."""
    cx, cy = position
    # Sign
    _cyl(f"{name}_SignPost", (cx, cy, z + 1.05), 0.04, 2.10,
         COL_POLE_DARK, segments=4)
    if facing in ('+X', '-X'):
        sign_size = (0.06, 0.45, 0.50)
    else:
        sign_size = (0.45, 0.06, 0.50)
    _box(f"{name}_SignFace", (cx, cy, z + 2.00),
         sign_size, COL_SIGN_GREEN)
    if with_shelter:
        # Shelter roof — thin box overhead
        # Place 0.5 m behind the sign (away from road), facing front-open
        if facing == '+Y':   # road is to the +Y; shelter behind (-Y)
            ox, oy = 0, -1.5
        elif facing == '-Y':
            ox, oy = 0, 1.5
        elif facing == '+X':
            ox, oy = -1.5, 0
        else:
            ox, oy = 1.5, 0
        shelter_cx, shelter_cy = cx + ox, cy + oy
        _box(f"{name}_ShelterRoof",
             (shelter_cx, shelter_cy, z + 2.40),
             (2.2, 1.4, 0.10), COL_SHELTER_ROOF)
        # Three glass walls (suggestion — thin transparent-blue boxes)
        glass_color = (0.30, 0.42, 0.50, 1.0)
        # Back wall
        if facing in ('+Y', '-Y'):
            _box(f"{name}_ShelterBack",
                 (shelter_cx, shelter_cy - (1.5 if facing == '+Y' else -1.5) * 0.46,
                  z + 1.15),
                 (2.2, 0.05, 2.30), glass_color)
            for sign in (-1, 1):
                _box(f"{name}_ShelterSide_{sign:+d}",
                     (shelter_cx + sign * 1.05, shelter_cy, z + 1.15),
                     (0.05, 1.4, 2.30), glass_color)
        else:
            _box(f"{name}_ShelterBack",
                 (shelter_cx - (1.5 if facing == '+X' else -1.5) * 0.46,
                  shelter_cy, z + 1.15),
                 (0.05, 2.2, 2.30), glass_color)
            for sign in (-1, 1):
                _box(f"{name}_ShelterSide_{sign:+d}",
                     (shelter_cx, shelter_cy + sign * 1.05, z + 1.15),
                     (1.4, 0.05, 2.30), glass_color)
        # Bench inside
        _box(f"{name}_Bench",
             (shelter_cx, shelter_cy, z + 0.45),
             (1.80, 0.35, 0.05), COL_BENCH)


def trashcan(name, position, z=0.0, color=COL_TRASHCAN):
    """A wheeled curbside trash receptacle. Suggestion: position
    these at curb edges, especially on residential streets."""
    cx, cy = position
    _box(f"{name}_Body", (cx, cy, z + 0.60),
         (0.55, 0.50, 1.10), color)
    _box(f"{name}_Lid", (cx, cy, z + 1.20),
         (0.60, 0.55, 0.10), color)


def manhole(name, position, z=0.0, radius=0.45):
    """Cast-iron manhole cover flush with the road surface."""
    cx, cy = position
    _disc(f"{name}_Cover", (cx, cy, z + 0.025), radius, z + 0.025,
          (0.32, 0.30, 0.28, 1.0))


def storm_drain(name, position, axis='+Y', z=0.0):
    """Curb-side storm drain — a dark rectangular slot at the
    asphalt edge. axis is the long direction of the slot."""
    cx, cy = position
    if axis in ('+Y', '-Y'):
        _box(f"{name}_Grate", (cx, cy, z + 0.02),
             (0.50, 1.20, 0.04), (0.10, 0.10, 0.08, 1.0))
    else:
        _box(f"{name}_Grate", (cx, cy, z + 0.02),
             (1.20, 0.50, 0.04), (0.10, 0.10, 0.08, 1.0))


def school_zone_sign(name, position, facing='+X', z=0.0,
                     post_h=2.8):
    """Fluorescent-yellow pentagon school zone sign — the kind
    posted near elementary schools. Pair with a SCHOOL CROSSING
    sign at the actual crosswalk approach."""
    cx, cy = position
    _cyl(f"{name}_Post", (cx, cy, z + post_h / 2), 0.05, post_h,
         COL_POLE_DARK, segments=6)
    if facing in ('+X', '-X'):
        size = (0.06, 0.65, 0.75)
    else:
        size = (0.65, 0.06, 0.75)
    # Fluorescent green-yellow (FYG) — the modern standard
    fyg = (0.78, 0.92, 0.20, 1.0)
    _box(f"{name}_Face", (cx, cy, z + post_h - 0.30), size, fyg)
    # Black silhouette suggestion (two figures)
    if facing in ('+X', '-X'):
        inner = (0.07, 0.40, 0.50)
    else:
        inner = (0.40, 0.07, 0.50)
    _box(f"{name}_Symbol", (cx, cy, z + post_h - 0.30), inner,
         (0.10, 0.10, 0.08, 1.0))


def library_sign(name, position, facing='+X', z=0.0, post_h=2.6,
                 panel_w=2.4, panel_h=1.2):
    """Brown civic signage — the kind in front of a small branch
    library or municipal building. Brown panel with cream lettering
    area (left blank — Label3D in Godot handles the text)."""
    cx, cy = position
    # Two posts flanking the panel
    for sign in (-1, 1):
        _cyl(f"{name}_Post_{sign:+d}",
             (cx + sign * (panel_w / 2 - 0.10), cy, z + post_h / 2),
             0.06, post_h, COL_POLE_DARK, segments=4)
    if facing in ('+X', '-X'):
        size = (0.08, panel_w, panel_h)
    else:
        size = (panel_w, 0.08, panel_h)
    _box(f"{name}_Panel", (cx, cy, z + post_h - panel_h / 2),
         size, COL_SIGN_BROWN)
    # Cream lettering area (inset)
    if facing in ('+X', '-X'):
        size_inner = (0.09, panel_w - 0.30, panel_h - 0.30)
    else:
        size_inner = (panel_w - 0.30, 0.09, panel_h - 0.30)
    _box(f"{name}_LetteringArea", (cx, cy, z + post_h - panel_h / 2),
         size_inner, (0.86, 0.82, 0.70, 1.0))


def park_sign(name, position, facing='+X', z=0.0):
    """Brown wooden park entry sign — for the public walkway / park
    boundaries. Same brown civic palette as library_sign but smaller."""
    library_sign(name, position, facing=facing, z=z,
                 post_h=2.2, panel_w=1.8, panel_h=0.9)


def public_walkway(name, p0, p1, width=2.5, z=0.0,
                   color=COL_SIDEWALK, with_lampposts=False,
                   lamp_spacing=20.0):
    """Concrete walkway through a park / public greenway. Like
    suburban_drive's sidewalk but stand-alone (no road). Optionally
    drops lampposts at regular intervals along the path."""
    road_segment(name + "_Path", p0, p1, width, color=color, z=z + 0.005)
    if with_lampposts:
        x0, y0 = p0; x1, y1 = p1
        length = math.hypot(x1 - x0, y1 - y0)
        ang = math.atan2(y1 - y0, x1 - x0)
        perp_x = -math.sin(ang); perp_y = math.cos(ang)
        n = max(1, int(length / lamp_spacing))
        for i in range(n + 1):
            t = i / max(1, n)
            cx = x0 + (x1 - x0) * t
            cy = y0 + (y1 - y0) * t
            # Lamps offset perpendicular to the path (alternating sides)
            sign = 1 if i % 2 == 0 else -1
            lp_x = cx + perp_x * (width / 2 + 0.4) * sign
            lp_y = cy + perp_y * (width / 2 + 0.4) * sign
            streetlight_pole(f"{name}_Lamp_{i}", (lp_x, lp_y),
                             head_dir='+X', pole_h=3.5, arm_len=0.6,
                             head_color=COL_LED_HEAD, z=z)


def bench(name, position, facing='+Y', z=0.0):
    """Park bench — wooden slats on iron supports. Sits along
    walkways. facing is the direction the seat faces (where the
    sitter looks)."""
    cx, cy = position
    if facing in ('+X', '-X'):
        seat = (0.45, 1.80, 0.06)
        back = (0.06, 1.80, 0.45)
        bx = 0.20 * (1 if facing == '+X' else -1)
    else:
        seat = (1.80, 0.45, 0.06)
        back = (1.80, 0.06, 0.45)
        bx = 0
    by = 0.20 * (1 if facing == '+Y' else -1) if facing in ('+Y', '-Y') else 0
    _box(f"{name}_Seat", (cx, cy, z + 0.43), seat, COL_BENCH)
    _box(f"{name}_Back", (cx - bx, cy - by, z + 0.85), back, COL_BENCH)
    # Two iron legs
    for sign in (-1, 1):
        if facing in ('+Y', '-Y'):
            _box(f"{name}_Leg_{sign:+d}",
                 (cx + sign * 0.80, cy, z + 0.22),
                 (0.05, 0.40, 0.45), (0.18, 0.18, 0.16, 1.0))
        else:
            _box(f"{name}_Leg_{sign:+d}",
                 (cx, cy + sign * 0.80, z + 0.22),
                 (0.40, 0.05, 0.45), (0.18, 0.18, 0.16, 1.0))


def picnic_table(name, position, z=0.0):
    """Park picnic table — top with two flanking benches."""
    cx, cy = position
    _box(f"{name}_Top", (cx, cy, z + 0.75),
         (1.8, 0.8, 0.06), COL_BENCH)
    for sign in (-1, 1):
        _box(f"{name}_Bench_{sign:+d}",
             (cx, cy + sign * 0.65, z + 0.42),
             (1.8, 0.35, 0.05), COL_BENCH)


# ════════════════════════════════════════════════════════════════
# FENCES — suburban privacy walls + decorative iron lattice
# ════════════════════════════════════════════════════════════════

COL_BRICK_WALL    = (0.55, 0.32, 0.26, 1.0)   # red brick privacy
COL_BRICK_CAP     = (0.78, 0.74, 0.66, 1.0)   # cream stone cap
COL_IRON_FENCE    = (0.10, 0.10, 0.10, 1.0)   # black wrought iron


def brick_wall(name, p0, p1, height=1.8, thickness=0.30, z=0.0,
               z1=None,
               with_cap=True, color=COL_BRICK_WALL,
               cap_color=COL_BRICK_CAP):
    """Suburban privacy brick wall.

    z + z1 enable terrain-following: the wall slants from z at p0
    to z1 at p1, so consecutive segments emitted by _fence_along
    meet at the same elevation and the wall reads as smoothly
    following the grade. If z1 is None, the wall is horizontal."""
    if z1 is None:
        z1 = z
    z0 = z
    x0, y0 = p0; x1, y1 = p1
    dx = x1 - x0; dy = y1 - y0
    length = math.hypot(dx, dy)
    if length < 0.001:
        return None
    ang = math.atan2(dy, dx)
    perp_x = -math.sin(ang); perp_y = math.cos(ang)
    half_t = thickness / 2
    verts = [
        (x0 - perp_x * half_t, y0 - perp_y * half_t, z0),
        (x1 - perp_x * half_t, y1 - perp_y * half_t, z1),
        (x1 + perp_x * half_t, y1 + perp_y * half_t, z1),
        (x0 + perp_x * half_t, y0 + perp_y * half_t, z0),
        (x0 - perp_x * half_t, y0 - perp_y * half_t, z0 + height),
        (x1 - perp_x * half_t, y1 - perp_y * half_t, z1 + height),
        (x1 + perp_x * half_t, y1 + perp_y * half_t, z1 + height),
        (x0 + perp_x * half_t, y0 + perp_y * half_t, z0 + height),
    ]
    faces = [
        [4, 5, 6, 7],     # top
        [0, 3, 2, 1],     # bottom
        [0, 1, 5, 4],     # west face
        [2, 3, 7, 6],     # east face
        [0, 4, 7, 3],     # south end
        [1, 2, 6, 5],     # north end
    ]
    _finalize_mesh(name + "_Brick", verts, faces, color)
    if with_cap:
        # Cream-stone cap — slightly wider, also slants z0..z1
        cap_t = thickness + 0.10
        cap_h = 0.12
        half_c = cap_t / 2
        cverts = [
            (x0 - perp_x * half_c, y0 - perp_y * half_c, z0 + height),
            (x1 - perp_x * half_c, y1 - perp_y * half_c, z1 + height),
            (x1 + perp_x * half_c, y1 + perp_y * half_c, z1 + height),
            (x0 + perp_x * half_c, y0 + perp_y * half_c, z0 + height),
            (x0 - perp_x * half_c, y0 - perp_y * half_c, z0 + height + cap_h),
            (x1 - perp_x * half_c, y1 - perp_y * half_c, z1 + height + cap_h),
            (x1 + perp_x * half_c, y1 + perp_y * half_c, z1 + height + cap_h),
            (x0 + perp_x * half_c, y0 + perp_y * half_c, z0 + height + cap_h),
        ]
        cfaces = [
            [4, 5, 6, 7], [0, 3, 2, 1],
            [0, 1, 5, 4], [2, 3, 7, 6],
            [0, 4, 7, 3], [1, 2, 6, 5],
        ]
        _finalize_mesh(name + "_Cap", cverts, cfaces, cap_color)


def iron_lattice_fence(name, p0, p1, height=1.4, post_spacing=2.5,
                       bar_spacing=0.40, z=0.0,
                       color=COL_IRON_FENCE,
                       with_end_posts=True):
    """Black wrought-iron bar fence. SPARSE district-scale version.
    with_end_posts=False is used by _fence_along subdividers so
    internal segment joints don't double up on posts; the caller
    drops one pair of end-posts at the full run's start + end."""
    x0, y0 = p0; x1, y1 = p1
    dx = x1 - x0; dy = y1 - y0
    length = math.hypot(dx, dy)
    if length < 0.001:
        return None
    ang = math.atan2(dy, dx)

    # Top and bottom rails — single box per rail (already efficient)
    rail_t = 0.05
    for rh in (0.20, height - 0.10):
        mx = (x0 + x1) / 2; my = (y0 + y1) / 2
        if abs(dx) > abs(dy):
            _box(f"{name}_Rail_{int(rh*100)}",
                 (mx, my, z + rh),
                 (length, rail_t, rail_t * 1.4), color)
        else:
            _box(f"{name}_Rail_{int(rh*100)}",
                 (mx, my, z + rh),
                 (rail_t, length, rail_t * 1.4), color)

    # Vertical bars — sparse so the polycount stays sane
    n_bars = max(2, int(length / bar_spacing))
    for i in range(n_bars + 1):
        t = i / n_bars
        bx = x0 + dx * t; by = y0 + dy * t
        _box(f"{name}_Bar_{i}",
             (bx, by, z + height / 2),
             (rail_t * 0.7, rail_t * 0.7, height),
             color)

    # End posts only when this segment IS a full run, not a
    # subdivision of a longer run.
    if with_end_posts:
        for end_idx, (bx, by) in enumerate([(x0, y0), (x1, y1)]):
            _box(f"{name}_Post_{end_idx}",
                 (bx, by, z + (height + 0.20) / 2),
                 (0.12, 0.12, height + 0.20),
                 color)


def double_yellow(name, p0, p1, z=0.0):
    """Standalone double-yellow centre line — for when a build
    script needs to drop the lines independent of a road call."""
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    _paint_double(name, p0, p1, ang, z + 0.01)


__all__ = [
    # Roads
    "road_segment", "highway_segment", "suburban_drive",
    "four_way_intersection", "roundabout", "cul_de_sac",
    "circle_drive", "bridge",
    # Markings
    "crosswalk", "parking_row", "double_yellow",
    # Fixtures
    "streetlight_pole", "stop_sign", "stop_light", "utility_pole",
    "utility_wire", "fire_hydrant", "mailbox", "mailbox_cluster",
    "bus_stop", "trashcan", "manhole", "storm_drain",
    # Civic / parks
    "school_zone_sign", "library_sign", "park_sign",
    "public_walkway", "bench", "picnic_table",
    # Fences / walls
    "brick_wall", "iron_lattice_fence",
    "COL_BRICK_WALL", "COL_BRICK_CAP", "COL_IRON_FENCE",
    # Colours (re-export so build scripts don't redefine)
    "COL_ASPHALT", "COL_ASPHALT_FRESH", "COL_ASPHALT_AGED",
    "COL_PAINT_YELLOW", "COL_PAINT_WHITE", "COL_CURB",
    "COL_SIDEWALK", "COL_CONCRETE", "COL_MEDIAN_GRASS",
    "COL_SHOULDER", "COL_POLE_DARK", "COL_POLE_WOOD",
    "COL_WIRE", "COL_SODIUM_HEAD", "COL_LED_HEAD",
    "COL_TRANSFORMER", "COL_HYDRANT_RED", "COL_HYDRANT_YEL",
    "COL_HYDRANT_BLU", "COL_MAILBOX", "COL_MAILBOX_RED",
    "COL_STOP_RED", "COL_STOP_WHITE", "COL_YIELD_YELLOW",
    "COL_SIGN_GREEN", "COL_SIGN_BROWN", "COL_STOPLIGHT_BOX",
    "COL_STOPLIGHT_R", "COL_STOPLIGHT_A", "COL_STOPLIGHT_G",
    "COL_BENCH", "COL_TRASHCAN", "COL_SHELTER_ROOF",
]
