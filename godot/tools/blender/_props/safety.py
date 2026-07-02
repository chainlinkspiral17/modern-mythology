# _props/safety.py
# ════════════════════════════════════════════════════════════════
# Building-code mandatory fixtures — security cameras, smoke
# detectors, sprinklers, conduit runs, HVAC vents. Reusable
# across any commercial interior.
# ════════════════════════════════════════════════════════════════
from . import palette as P
from .geometry import make_box, make_cyl


def make_security_camera(prefix, anchor, *, palette=None):
    """Dome-style ceiling-mounted security camera. anchor=(cx, cy, ceil_z)."""
    palette = palette or {}
    body = palette.get("body", P.METAL_BLACK)
    glass = palette.get("glass", (0.18, 0.20, 0.22, 0.70))
    cx, cy, ceil_z = anchor
    make_cyl(f"{prefix}_Dome", (cx, cy, ceil_z - 0.10),
             0.12, 0.12, body)
    make_cyl(f"{prefix}_Glass", (cx, cy, ceil_z - 0.16),
             0.10, 0.04, glass)


def make_smoke_detector(prefix, anchor, *, palette=None):
    """Ceiling-mounted smoke detector with status LED."""
    palette = palette or {}
    body = palette.get("body", P.PAPER)
    led = palette.get("led", (0.86, 0.42, 0.32, 1.0))
    cx, cy, ceil_z = anchor
    make_cyl(f"{prefix}_Body", (cx, cy, ceil_z - 0.04),
             0.10, 0.04, body)
    make_box(f"{prefix}_LED", (cx + 0.04, cy, ceil_z - 0.06),
             (0.012, 0.012, 0.012), led)


def make_sprinkler(prefix, anchor, *, palette=None):
    """Fire-suppression sprinkler head. anchor=(cx, cy, ceil_z)."""
    palette = palette or {}
    head = palette.get("head", P.METAL_STEEL)
    cap = palette.get("cap", P.METAL_BLACK)
    cx, cy, ceil_z = anchor
    make_cyl(f"{prefix}_Stem", (cx, cy, ceil_z - 0.04),
             0.025, 0.08, head)
    make_box(f"{prefix}_Cap", (cx, cy, ceil_z - 0.10),
             (0.06, 0.06, 0.02), cap)


def make_hvac_vent(prefix, anchor, *, width=1.20, depth=0.60,
                   slats=6, palette=None):
    """Rectangular HVAC supply / return grille with slats."""
    palette = palette or {}
    frame = palette.get("frame", P.METAL_STEEL)
    slat = palette.get("slat", P.METAL_BLACK)
    cx, cy, ceil_z = anchor
    make_box(f"{prefix}_Frame", (cx, cy, ceil_z - 0.02),
             (width, depth, 0.04), frame)
    for s in range(slats):
        offset = (s - (slats - 1) / 2.0) * (width / slats)
        make_box(f"{prefix}_Slat_{s}",
                 (cx + offset, cy, ceil_z - 0.05),
                 (width / slats * 0.5, depth * 0.83, 0.01), slat)


def make_ceiling_speaker(prefix, anchor, *, palette=None):
    """Round dome Muzak speaker."""
    palette = palette or {}
    body = palette.get("body", P.PAPER)
    cx, cy, ceil_z = anchor
    make_cyl(f"{prefix}_Dome", (cx, cy, ceil_z - 0.08),
             0.16, 0.08, body)


def make_emt_conduit_run(prefix, *, wall_x, wall_face_sign,
                         vert_y, vert_z_top, ceil_z,
                         horiz_y_end, palette=None):
    """White EMT conduit running UP a wall then ALONG the ceiling.
    Models a wall outlet → fluorescent fixture tap.
    `wall_x` is the wall's INTERIOR face X coordinate.
    `wall_face_sign` is +1 (east wall, conduit on west face) or -1
    (west wall, conduit on east face) — controls the small offset
    that pulls the conduit a few cm off the wall."""
    palette = palette or {}
    pipe = palette.get("pipe", P.PAPER)
    cx = wall_x - wall_face_sign * 0.02
    vert_len = vert_z_top - 0.30
    make_box(f"{prefix}_Vert",
             (cx, vert_y, 0.30 + vert_len / 2.0),
             (0.04, 0.04, vert_len), pipe)
    horiz_len = abs(horiz_y_end - vert_y)
    horiz_cy = (horiz_y_end + vert_y) / 2.0
    make_box(f"{prefix}_Horiz",
             (cx, horiz_cy, ceil_z - 0.06),
             (0.04, horiz_len, 0.04), pipe)


def make_bug_zapper(prefix, anchor, *, palette=None):
    """UV-blue bug zapper in a wire cage. anchor=(wall_x, wall_y, center_z)."""
    palette = palette or {}
    cage = palette.get("cage", P.METAL_STEEL)
    uv = palette.get("uv", (0.46, 0.56, 0.74, 1.0))
    bx, by, bz = anchor
    make_box(f"{prefix}_Cage", (bx, by, bz),
             (0.50, 0.10, 0.30), cage)
    for ti in range(2):
        make_box(f"{prefix}_Tube_{ti}",
                 (bx, by - 0.04, bz + 0.06 - ti * 0.12),
                 (0.46, 0.005, 0.04), uv)
    for wi in range(4):
        make_box(f"{prefix}_Bar_{wi}",
                 (bx, by - 0.05, bz + 0.12 - wi * 0.08),
                 (0.50, 0.005, 0.005), cage)


def make_fluorescent_tube_fixture(prefix, anchor, *,
                                   length=1.60, width=0.36,
                                   palette=None):
    """Recessed ceiling fluorescent tube housing. anchor=(cx, cy, ceil_z)."""
    palette = palette or {}
    tube = palette.get("tube", (0.96, 0.96, 0.92, 1.0))
    diffuser = palette.get("diffuser", (1.0, 0.96, 0.86, 1.0))
    frame = palette.get("frame", P.METAL_STEEL)
    cx, cy, ceil_z = anchor
    make_box(f"{prefix}_Tube", (cx, cy, ceil_z - 0.08),
             (length, width, 0.06), tube)
    make_box(f"{prefix}_Frame", (cx, cy, ceil_z - 0.10),
             (length + 0.10, width + 0.08, 0.02), frame)
    # Brighter under-strip
    make_box(f"{prefix}_Glow", (cx, cy, ceil_z - 0.14),
             (length - 0.10, width * 0.45, 0.02), diffuser)
