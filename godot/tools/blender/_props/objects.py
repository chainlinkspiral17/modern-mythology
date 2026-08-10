"""Recognizable everyday objects — composite silhouettes.

2026-08-09, user: "the bar, all the bottles are cubes. make bottles,
make cans, make recognizable objects for all the scenes."

Every helper here emits a SMALL STACK of primitives whose combined
silhouette reads as the thing at couch distance: a bottle is a body,
a shoulder, a neck and a cap — never a box, never a single cylinder.
All pieces share the caller's prefix so the overlap audit's assembly
rule treats each object as one unit.

Sizes are real-world: a longneck is 23cm, a soda can 12cm, a rocks
glass 9cm. Callers place the BASE (z of the surface the object
stands on).
"""
from .geometry import make_box, make_cyl, make_taper_cyl, make_dome

GLASS_CLEAR = (0.74, 0.82, 0.84, 0.55)


def make_bottle(prefix, x, y, base_z, color,
                h=0.23, r=0.032, cap_color=(0.72, 0.70, 0.66, 1.0),
                segments=8):
    """Longneck silhouette: body 60%, shoulder taper 15%, neck 20%,
    cap 5%. `color` is the glass; amber (0.60,0.34,0.12,0.9), green
    (0.22,0.40,0.20,0.9) and clear read instantly."""
    body_h = h * 0.60
    shoulder_h = h * 0.15
    neck_h = h * 0.20
    cap_h = h * 0.05
    neck_r = r * 0.38
    make_cyl(f"{prefix}_Body", (x, y, base_z + body_h / 2.0), r, body_h,
             color, segments=segments)
    make_taper_cyl(f"{prefix}_Shoulder",
                   (x, y, base_z + body_h + shoulder_h / 2.0),
                   r, neck_r, shoulder_h, color, segments=segments)
    make_cyl(f"{prefix}_Neck",
             (x, y, base_z + body_h + shoulder_h + neck_h / 2.0),
             neck_r, neck_h, color, segments=segments)
    make_cyl(f"{prefix}_Cap",
             (x, y, base_z + h - cap_h / 2.0),
             neck_r * 1.15, cap_h, cap_color, segments=segments)


def make_liquor_bottle(prefix, x, y, base_z, color,
                       h=0.30, r=0.042, segments=8):
    """Squarer-shouldered spirits bottle: taller body, short neck,
    foil-dark cap."""
    make_bottle(prefix, x, y, base_z, color, h=h, r=r,
                cap_color=(0.18, 0.16, 0.14, 1.0), segments=segments)


def make_can(prefix, x, y, base_z, color,
             h=0.122, r=0.033, segments=8):
    """Soda/beer can: body + darker chamfered rims top and bottom +
    lid disc."""
    rim = (color[0] * 0.55, color[1] * 0.55, color[2] * 0.55, 1.0)
    lid = (0.74, 0.75, 0.77, 1.0)
    make_taper_cyl(f"{prefix}_RimB", (x, y, base_z + 0.006),
                   r * 0.88, r, 0.012, rim, segments=segments)
    make_cyl(f"{prefix}_Body", (x, y, base_z + h / 2.0), r, h - 0.024,
             color, segments=segments)
    make_taper_cyl(f"{prefix}_RimT", (x, y, base_z + h - 0.006),
                   r, r * 0.88, 0.012, rim, segments=segments)
    make_cyl(f"{prefix}_Lid", (x, y, base_z + h - 0.002),
             r * 0.86, 0.004, lid, segments=segments)


def make_drinking_glass(prefix, x, y, base_z, color=GLASS_CLEAR,
                        h=0.10, r=0.035, segments=8):
    """Rocks glass: slight outward taper, thick base disc."""
    make_cyl(f"{prefix}_Base", (x, y, base_z + 0.008), r * 0.92, 0.016,
             (color[0] * 0.9, color[1] * 0.9, color[2] * 0.9, 1.0),
             segments=segments)
    make_taper_cyl(f"{prefix}_Wall", (x, y, base_z + 0.016 + (h - 0.016) / 2.0),
                   r * 0.92, r, h - 0.016, color, segments=segments)


def make_pint_glass(prefix, x, y, base_z, color=GLASS_CLEAR,
                    h=0.15, r=0.040, segments=8):
    make_taper_cyl(f"{prefix}_Wall", (x, y, base_z + h / 2.0),
                   r * 0.72, r, h, color, segments=segments)


def make_mug(prefix, x, y, base_z, color,
             h=0.095, r=0.040, handle_side=+1, segments=8):
    """Coffee mug: cylinder + a C-suggesting handle block off one
    side (a full torus is wasted at this scale)."""
    make_cyl(f"{prefix}_Body", (x, y, base_z + h / 2.0), r, h,
             color, segments=segments)
    make_box(f"{prefix}_Handle",
             (x + handle_side * (r + 0.016), y, base_z + h * 0.52),
             (0.016, 0.030, h * 0.55), color)


def make_jar(prefix, x, y, base_z, color=GLASS_CLEAR,
             h=0.14, r=0.05, lid_color=(0.62, 0.58, 0.50, 1.0),
             segments=8):
    make_cyl(f"{prefix}_Body", (x, y, base_z + h * 0.45), r, h * 0.9,
             color, segments=segments)
    make_cyl(f"{prefix}_Lid", (x, y, base_z + h * 0.95), r * 1.04,
             h * 0.1, lid_color, segments=segments)


def make_plate(prefix, x, y, base_z, color,
               r=0.13, segments=10):
    make_taper_cyl(f"{prefix}_Plate", (x, y, base_z + 0.012),
                   r * 0.62, r, 0.024, color, segments=segments)


def make_bowl(prefix, x, y, base_z, color,
              r=0.10, h=0.06, segments=10):
    make_taper_cyl(f"{prefix}_Bowl", (x, y, base_z + h / 2.0),
                   r * 0.55, r, h, color, segments=segments)


def make_wine_bottle(prefix, x, y, base_z, color=(0.14, 0.22, 0.14, 0.95),
                     h=0.30, r=0.037, segments=8):
    """Burgundy silhouette: taller shoulder curve than a longneck."""
    make_cyl(f"{prefix}_Body", (x, y, base_z + h * 0.30), r, h * 0.60,
             color, segments=segments)
    make_taper_cyl(f"{prefix}_Shoulder", (x, y, base_z + h * 0.70),
                   r, r * 0.30, h * 0.20, color, segments=segments)
    make_cyl(f"{prefix}_Neck", (x, y, base_z + h * 0.875),
             r * 0.30, h * 0.15, color, segments=segments)
    make_cyl(f"{prefix}_Foil", (x, y, base_z + h * 0.97),
             r * 0.33, h * 0.06, (0.50, 0.14, 0.14, 1.0), segments=segments)
