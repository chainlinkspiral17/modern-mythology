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
import math
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


def make_smartphone(prefix, x, y, base_z, *, state="call", along="Y", head=1,
                    case=(0.10, 0.10, 0.12, 1.0), w=0.075, l=0.155):
    """A smartphone lying on a surface, readable from a close-up (pass 454).

    The phones were one dark box the colour of the desk under them: the
    New Orleans office's "insert phone" (11 lines) and the Miller
    kitchen's (9) framed a slab nobody would name. This is a case with a
    bright rim round it and a LIT screen that says what the line says:

      state "call"  an incoming call — avatar, name bar, red and green buttons
            "text"  a message thread — grey and blue bubbles, the input bar
            "lock"  a dim wallpaper and the clock
            "off"   black glass with one reflection
            "back"  face-down: the camera block, its lenses, the maker's dot

    `along` is the phone's long axis ('Y' or 'X'), `head` (+1 / -1) which
    end is its top. `prefix` may carry a `__view` tag; every part keeps it.
    There are no letters on it: the art layer (Hero Studio) carries words.
    """
    head_name, _, tag = prefix.partition("__")
    tag = ("__" + tag) if tag else ""

    def nm(part):
        return head_name + (("_" + part) if part else "") + tag

    def P(u, v, z, su, sv, sz, name, color):
        # (u across, v along the phone, toward its top) -> world
        if along == "Y":
            make_box(name, (x + u, y + head * v, base_z + z), (su, sv, sz), color)
        else:
            make_box(name, (x + head * v, y + u, base_z + z), (sv, su, sz), color)

    def D(u, v, z, r, name, color, h=0.001):
        if along == "Y":
            make_cyl(name, (x + u, y + head * v, base_z + z), r, h, color, segments=10)
        else:
            make_cyl(name, (x + head * v, y + u, base_z + z), r, h, color, segments=10)

    if state == "back" and case == (0.10, 0.10, 0.12, 1.0):
        case = (0.30, 0.35, 0.42, 1.0)      # a face-down phone is its case: a colour, not a black bar
    P(0, 0, 0.0035, w + 0.004, l + 0.004, 0.007, nm("Rim"), (0.74, 0.75, 0.77, 1.0))
    P(0, 0, 0.0045, w, l, 0.009, nm(""), case)
    if state == "back":
        P(-w / 2 + 0.022, l / 2 - 0.024, 0.0100, 0.030, 0.034, 0.002, nm("Camera"), (0.20, 0.20, 0.22, 1.0))
        D(-w / 2 + 0.022, l / 2 - 0.016, 0.0115, 0.008, nm("Lens_0"), (0.03, 0.03, 0.04, 1.0))
        D(-w / 2 + 0.022, l / 2 - 0.033, 0.0115, 0.008, nm("Lens_1"), (0.03, 0.03, 0.04, 1.0))
        D(0, 0, 0.0095, 0.007, nm("Mark"), (0.36, 0.36, 0.38, 1.0))
        return
    sw, sl = w - 0.008, l - 0.012
    lit = {"call": (0.80, 0.87, 0.97, 1.0), "text": (0.94, 0.95, 0.96, 1.0),
           "lock": (0.22, 0.30, 0.44, 1.0), "off": (0.03, 0.03, 0.04, 1.0)}[state]
    P(0, 0, 0.0095, sw, sl, 0.001, nm("Screen"), lit)
    z = 0.0105
    if state == "call":
        D(0, sl * 0.20, z, 0.015, nm("Screen_Avatar"), (0.42, 0.50, 0.66, 1.0))
        P(0, sl * 0.03, z, 0.040, 0.008, 0.001, nm("Screen_Name"), (0.12, 0.14, 0.20, 1.0))
        P(0, -sl * 0.05, z, 0.026, 0.005, 0.001, nm("Screen_Sub"), (0.46, 0.50, 0.58, 1.0))
        D(-sw * 0.27, -sl * 0.32, z, 0.010, nm("Screen_Decline"), (0.86, 0.18, 0.16, 1.0))
        D(sw * 0.27, -sl * 0.32, z, 0.010, nm("Screen_Accept"), (0.20, 0.72, 0.30, 1.0))
    elif state == "text":
        P(0, sl * 0.44, z, sw, 0.012, 0.001, nm("Screen_Bar"), (0.84, 0.86, 0.88, 1.0))
        P(-sw * 0.14, sl * 0.26, z, 0.044, 0.018, 0.001, nm("Screen_Bubble_0"), (0.78, 0.80, 0.83, 1.0))
        P(-sw * 0.10, sl * 0.08, z, 0.050, 0.026, 0.001, nm("Screen_Bubble_1"), (0.78, 0.80, 0.83, 1.0))
        P(sw * 0.16, -sl * 0.12, z, 0.040, 0.016, 0.001, nm("Screen_Bubble_2"), (0.22, 0.52, 0.94, 1.0))
        P(0, -sl * 0.42, z, sw - 0.010, 0.010, 0.001, nm("Screen_Input"), (0.84, 0.86, 0.88, 1.0))
    elif state == "lock":
        P(0, sl * 0.24, z, 0.036, 0.014, 0.001, nm("Screen_Clock"), (0.90, 0.92, 0.95, 1.0))
        P(0, sl * 0.12, z, 0.024, 0.004, 0.001, nm("Screen_Date"), (0.70, 0.74, 0.80, 1.0))
    else:
        P(sw * 0.22, 0, z, 0.010, sl * 0.6, 0.001, nm("Screen_Glare"), (0.10, 0.11, 0.14, 1.0))


def make_pallet(prefix, x, y, base_z, *, along="Y", w=1.00, l=1.20,
                wood=(0.62, 0.50, 0.34, 1.0), wood_dk=(0.50, 0.39, 0.26, 1.0)):
    """A wooden pallet you can see THROUGH (pass 455). Every pallet in the
    game was one solid box: the grocery aisle's "insert pallet" framed a
    slab under a crate. Three stringers, three bottom boards, seven deck
    boards with gaps — 144 mm tall, 1.0 x 1.2 m. `along` is the stringers'
    axis. Returns the deck's top z (stand the load on it)."""
    def B(name, u, v, z, su, sv, sz, col):
        # u across the stringers, v along them
        if along == "Y":
            make_box(name, (x + u, y + v, base_z + z), (su, sv, sz), col)
        else:
            make_box(name, (x + v, y + u, base_z + z), (sv, su, sz), col)
    for i, u in enumerate((-w / 2 + 0.05, 0.0, w / 2 - 0.05)):
        B(f"{prefix}_Stringer_{i}", u, 0.0, 0.022 + 0.050, 0.045, l, 0.100, wood_dk)
    for i, v in enumerate((-l / 2 + 0.05, 0.0, l / 2 - 0.05)):
        B(f"{prefix}_Bottom_{i}", 0.0, v, 0.011, w, 0.095, 0.022, wood)
    n = 7
    for i in range(n):
        v = -l / 2 + 0.05 + i * (l - 0.10) / (n - 1)
        B(f"{prefix}_Deck_{i}", 0.0, v, 0.122 + 0.011, w, 0.095, 0.022, wood if i % 2 == 0 else wood_dk)
    return base_z + 0.144


def make_paper_cup(prefix, x, y, base_z, *, h=0.095, sleeve=(0.56, 0.40, 0.24, 1.0),
                   paper=(0.95, 0.94, 0.90, 1.0), coffee=(0.20, 0.12, 0.07, 1.0), full=True):
    """A paper hot cup, no lid: tapered white wall, a kraft sleeve, the
    rolled rim, the coffee in it. `full=False` leaves it drained."""
    make_taper_cyl(f"{prefix}", (x, y, base_z + h / 2.0), 0.029, 0.040, h, paper, segments=14)
    make_taper_cyl(f"{prefix}_Sleeve", (x, y, base_z + h * 0.50), 0.0335, 0.0385, h * 0.42, sleeve, segments=14)
    make_cyl(f"{prefix}_Rim", (x, y, base_z + h + 0.002), 0.0425, 0.005, paper, segments=14)
    make_cyl(f"{prefix}_Coffee", (x, y, base_z + (h - 0.008 if full else 0.006)), 0.037 if full else 0.028, 0.003, coffee, segments=14)


def _local(x, y, yaw):
    """(u, v) offsets in an object's own frame -> world x, y, for a yaw."""
    import math
    c, s = math.cos(yaw), math.sin(yaw)
    return lambda u, v: (x + u * c - v * s, y + u * s + v * c)


def make_cordless(prefix, x, y, base_z, *, yaw=0.0, body=(0.88, 0.87, 0.82, 1.0),
                  dark=(0.20, 0.20, 0.22, 1.0)):
    """A cordless handset lying on its back (pass 456): the earpiece end
    thicker, a lit green screen, twelve keys in a grid, the talk key, the
    stub antenna. It was a cream bar with a grey patch. Its top (antenna)
    points local +v."""
    from .geometry import make_rot_box
    at = _local(x, y, yaw)
    if sum(body[:3]) < 1.2 and dark == (0.20, 0.20, 0.22, 1.0):
        dark = (0.80, 0.80, 0.76, 1.0)      # a dark handset: pale keys
    def B(part, u, v, z, su, sv, sz, col):
        px, py = at(u, v)
        make_rot_box(f"{prefix}{part}", (px, py, base_z + z), (su, sv, sz), col, yaw=yaw)
    B("", 0.0, 0.0, 0.0125, 0.052, 0.170, 0.025, body)
    B("_Ear", 0.0, 0.066, 0.029, 0.050, 0.036, 0.008, body)
    B("_Ear_Grille", 0.0, 0.068, 0.0335, 0.026, 0.012, 0.001, dark)
    B("_Screen", 0.0, 0.034, 0.0256, 0.036, 0.024, 0.0012, (0.56, 0.82, 0.52, 1.0))
    B("_Talk", 0.0, 0.010, 0.0256, 0.030, 0.010, 0.0012, (0.24, 0.62, 0.30, 1.0))
    for r in range(4):
        for c in range(3):
            B(f"_Key_{r}_{c}", -0.013 + c * 0.013, -0.008 - r * 0.014, 0.0258, 0.009, 0.009, 0.0016, dark)
    B("_Mic", 0.0, -0.074, 0.0256, 0.010, 0.004, 0.0012, dark)
    px, py = at(0.016, 0.092)
    make_rot_box(f"{prefix}_Antenna", (px, py, base_z + 0.015), (0.010, 0.022, 0.012), dark, yaw=yaw)


def make_milk_crate(prefix, x, y, base_z, *, s=0.33, h=0.28, color=(0.20, 0.34, 0.60, 1.0), upside_down=False):
    """A plastic milk crate you can see through (pass 456): corner posts, a
    rim, a mid band, slats on each side with gaps, and the grid of its
    bottom — the three in the alley were solid tan cubes. `upside_down`
    puts the bottom grid on top (a seat, a stand)."""
    hs = s / 2.0
    t = 0.022
    prefix, _, _tag = prefix.partition("__")
    _mbx = globals()["make_box"]      # the def below makes the name local: read the module's

    def make_box(name, *a, **k):          # every part keeps the view tag at its END
        return _mbx(name + (("__" + _tag) if _tag else ""), *a, **k)
    for i, (ex, ey) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        make_box(f"{prefix}_Post_{i}", (x + ex * (hs - t / 2), y + ey * (hs - t / 2), base_z + h / 2.0), (t, t, h), color)
    for nm, z, hh in (("Rim", h - 0.018, 0.036), ("Band", h * 0.48, 0.030), ("Foot", 0.012, 0.024)):
        for e in (-1, 1):
            make_box(f"{prefix}_{nm}_X{e:+d}", (x, y + e * (hs - 0.007), base_z + z), (s - 2 * t, 0.014, hh), color)
            make_box(f"{prefix}_{nm}_Y{e:+d}", (x + e * (hs - 0.007), y, base_z + z), (0.014, s - 2 * t, hh), color)
    n = 3
    for k in range(n):
        off = -hs + t + (k + 0.5) * (s - 2 * t) / n
        for e in (-1, 1):
            make_box(f"{prefix}_Slat_X{e:+d}_{k}", (x + off, y + e * (hs - 0.007), base_z + h / 2.0), (0.020, 0.010, h - 0.05), color)
            make_box(f"{prefix}_Slat_Y{e:+d}_{k}", (x + e * (hs - 0.007), y + off, base_z + h / 2.0), (0.010, 0.020, h - 0.05), color)
    gz = base_z + (h - 0.008 if upside_down else 0.008)
    for k in range(4):
        off = -hs + t + (k + 0.5) * (s - 2 * t) / 4
        make_box(f"{prefix}_Grid_X_{k}", (x, y + off, gz), (s - 2 * t, 0.018, 0.012), color)
        make_box(f"{prefix}_Grid_Y_{k}", (x + off, y, gz), (0.018, s - 2 * t, 0.012), color)
    return base_z + h


def make_notebook(prefix, x, y, base_z, *, yaw=0.0, w=0.14, l=0.21, state="closed",
                  cover=(0.14, 0.14, 0.16, 1.0), band=(0.74, 0.18, 0.14, 1.0), pen=True):
    """A pocket notebook that reads as one (pass 456): the cover a shade off
    the table, the cream page-block showing at three edges, an elastic band
    and a ribbon; `state="open"` lays two cream pages with ruled lines and a
    pen in the gutter. They were dark slabs."""
    from .geometry import make_rot_box
    at = _local(x, y, yaw)
    def B(part, u, v, z, su, sv, sz, col):
        px, py = at(u, v)
        make_rot_box(f"{prefix}{part}", (px, py, base_z + z), (su, sv, sz), col, yaw=yaw)
    page = (0.93, 0.91, 0.84, 1.0)
    if state == "open":
        B("", 0.0, 0.0, 0.003, 2 * w + 0.012, l + 0.008, 0.006, cover)
        for sg, nm in ((-1, "L"), (1, "R")):
            B(f"_Page_{nm}", sg * (w / 2 + 0.002), 0.0, 0.009, w - 0.004, l - 0.006, 0.006, page)
            for k in range(6):
                B(f"_Rule_{nm}_{k}", sg * (w / 2 + 0.002), l * 0.36 - k * l * 0.13, 0.0125, w * (0.78 if (k + (sg > 0)) % 3 else 0.52), 0.003, 0.001, (0.26, 0.28, 0.40, 1.0))
        if pen:   # pen=False: an open paperback (pass 462, Rick's book)
            B("_Pen", 0.0, -0.01, 0.0155, 0.008, 0.135, 0.008, (0.16, 0.20, 0.44, 1.0))
        return
    B("_Pages", 0.004, 0.0, 0.008, w - 0.004, l - 0.006, 0.012, page)
    B("_Back", 0.0, 0.0, 0.001, w, l, 0.002, cover)
    B("", 0.0, 0.0, 0.015, w, l, 0.002, cover)
    B("_Spine", -w / 2 + 0.003, 0.0, 0.008, 0.006, l, 0.016, cover)
    B("_Band", w / 2 - 0.022, 0.0, 0.0165, 0.008, l + 0.002, 0.001, band)
    B("_Ribbon", -0.01, -l / 2 - 0.012, 0.004, 0.006, 0.030, 0.001, band)


def make_scanner_gun(prefix, x, y, base_z, *, yaw=0.0, body=(0.20, 0.20, 0.23, 1.0)):
    """A hand-held inventory scanner lying on its side: the head with its red
    scan window and a small screen, the pistol grip, the yellow trigger."""
    from .geometry import make_rot_box
    at = _local(x, y, yaw)
    def B(part, u, v, z, su, sv, sz, col):
        px, py = at(u, v)
        make_rot_box(f"{prefix}{part}", (px, py, base_z + z), (su, sv, sz), col, yaw=yaw)
    B("", 0.0, 0.03, 0.025, 0.075, 0.150, 0.050, body)
    B("_Window", 0.0, 0.106, 0.025, 0.056, 0.004, 0.030, (0.84, 0.16, 0.12, 1.0))
    B("_Screen", 0.0, 0.03, 0.0508, 0.050, 0.060, 0.0016, (0.60, 0.84, 0.78, 1.0))
    for k in range(3):
        B(f"_Key_{k}", -0.018 + k * 0.018, -0.022, 0.0508, 0.012, 0.012, 0.0016, (0.70, 0.70, 0.72, 1.0))
    B("_Grip", 0.0, -0.085, 0.020, 0.044, 0.110, 0.040, body)
    B("_Trigger", 0.0, -0.036, 0.008, 0.018, 0.030, 0.016, (0.92, 0.76, 0.14, 1.0))


def make_speak_spell(prefix, x, y, base_z, *, yaw=0.0, body=(0.84, 0.26, 0.12, 1.0), lit=False):
    """The talking spelling toy on its back (pass 456): a red-orange slab
    with the carrying handle cut through its top, the display strip, the
    speaker grille's slots, and the membrane keyboard — four rows of
    letter keys and a row of function keys. It was a red block with a tan
    patch. `lit`: the display's segments glow (vol 6: "The grille is dim"
    is the default). The handle end is local +v."""
    from .geometry import make_rot_box
    at = _local(x, y, yaw)
    def B(part, u, v, z, su, sv, sz, col):
        px, py = at(u, v)
        make_rot_box(f"{prefix}{part}", (px, py, base_z + z), (su, sv, sz), col, yaw=yaw)
    W, L, H = 0.19, 0.26, 0.036
    B("_Body", 0.0, -0.02, H / 2, W, L - 0.04, H, body)
    # the handle: two cheeks and the bar across the top, a slot between
    for sg in (-1, 1):
        B(f"_Handle_Cheek_{sg:+d}", sg * (W / 2 - 0.022), L / 2 - 0.022, H / 2, 0.044, 0.044, H, body)
    B("_Handle_Bar", 0.0, L / 2 - 0.008, H / 2, W - 0.08, 0.016, H * 0.8, body)
    top = H + 0.0008
    dark = (0.10, 0.10, 0.11, 1.0)
    B("_Display", 0.0, 0.060, top, 0.150, 0.024, 0.0016, (0.06, 0.10, 0.08, 1.0))
    for k in range(8):
        B(f"_Display_Seg_{k}", -0.060 + k * 0.017, 0.060, top + 0.0012, 0.010, 0.014, 0.0008,
          (0.36, 0.96, 0.56, 1.0) if lit else (0.12, 0.22, 0.16, 1.0))
    for k in range(5):
        B(f"_Grille_{k}", 0.062, 0.036 - k * 0.0042 + 0.004, top, 0.040, 0.0018, 0.0012, dark)
    B("_Brand", -0.040, 0.034, top, 0.090, 0.012, 0.0012, (0.96, 0.82, 0.26, 1.0))
    keycols = ((0.98, 0.86, 0.50, 1.0), (0.96, 0.78, 0.36, 1.0))
    for r in range(4):
        for c in range(10):
            B(f"_Key_{r}_{c}", -0.0765 + c * 0.017, 0.012 - r * 0.019, top, 0.0135, 0.0145, 0.0014, keycols[(r + c) % 2])
    for c, col in enumerate(((0.30, 0.52, 0.86, 1.0), (0.30, 0.52, 0.86, 1.0), (0.90, 0.90, 0.86, 1.0), (0.30, 0.70, 0.40, 1.0), (0.86, 0.22, 0.18, 1.0))):
        B(f"_Fn_{c}", -0.068 + c * 0.034, -0.068, top, 0.028, 0.0145, 0.0014, col)


def make_desk_phone(prefix, x, y, base_z, *, yaw=0.0, body=(0.16, 0.16, 0.18, 1.0)):
    """An office desk telephone (pass 456): a wedge base, the handset lying
    across its left side with its two fat ends, a twelve-key pad and a row
    of line buttons (one lit), a display strip, the coiled cord. It was a
    black box with a bar on it. The front (keypad low edge) is local -v."""
    from .geometry import make_rot_box
    at = _local(x, y, yaw)
    def B(part, u, v, z, su, sv, sz, col, pitch=0.0):
        px, py = at(u, v)
        make_rot_box(f"{prefix}{part}", (px, py, base_z + z), (su, sv, sz), col, yaw=yaw, pitch=pitch)
    key = (0.82, 0.82, 0.78, 1.0) if sum(body[:3]) < 1.2 else (0.22, 0.22, 0.24, 1.0)
    B("", 0.0, 0.0, 0.020, 0.22, 0.20, 0.040, body)
    B("_Back", 0.0, 0.065, 0.052, 0.22, 0.07, 0.030, body)
    # the handset on its cradle, left
    B("_Handset", -0.070, 0.0, 0.075, 0.045, 0.200, 0.030, body)
    B("_Handset_Ear", -0.070, 0.082, 0.062, 0.056, 0.050, 0.040, body)
    B("_Handset_Mouth", -0.070, -0.082, 0.062, 0.056, 0.050, 0.040, body)
    B("_Display", 0.040, 0.066, 0.0685, 0.100, 0.030, 0.003, (0.52, 0.78, 0.62, 1.0))
    for r in range(4):
        for c in range(3):
            B(f"_Key_{r}_{c}", 0.012 + c * 0.024, 0.022 - r * 0.024, 0.0415, 0.017, 0.017, 0.004, key)
    for k in range(4):
        B(f"_Line_{k}", 0.092, 0.022 - k * 0.024, 0.0415, 0.014, 0.012, 0.004,
          (0.90, 0.30, 0.20, 1.0) if k == 0 else (0.40, 0.42, 0.44, 1.0))
    # the coiled cord, from the handset's mouth end round to the base's side
    for k in range(6):
        B(f"_Cord_{k}", -0.108 - 0.006 * (k % 2), -0.075 + k * 0.022, 0.012, 0.014, 0.016, 0.014, body)


def make_rotary_phone(prefix, x, y, base_z, *, yaw=0.0, body=(0.10, 0.10, 0.11, 1.0)):
    """A black rotary telephone (pass 457): a stepped body, the dial on its
    sloped face — a pale number plate, ten finger holes round it, the centre
    card and the finger stop — two cradle horns, and the handset across them
    with its ear and mouth cups. It was a box, a disc and a bar. The dial
    faces local -v."""
    import math
    from .geometry import make_rot_box
    at = _local(x, y, yaw)
    def B(part, u, v, z, su, sv, sz, col, pitch=0.0):
        px, py = at(u, v)
        make_rot_box(f"{prefix}{part}", (px, py, base_z + z), (su, sv, sz), col, yaw=yaw, pitch=pitch)
    def C(part, u, v, z, r, h, col, seg=10):
        px, py = at(u, v)
        make_cyl(f"{prefix}{part}", (px, py, base_z + z), r, h, col, segments=seg)
    B("_Body", 0.0, 0.0, 0.030, 0.24, 0.20, 0.060, body)
    B("_Body_Upper", 0.0, 0.035, 0.080, 0.20, 0.12, 0.040, body)
    # the dial, lying on the body's front shelf
    C("_Dial", 0.0, -0.045, 0.064, 0.070, 0.008, (0.86, 0.84, 0.76, 1.0), 14)
    C("_Dial_Wheel", 0.0, -0.045, 0.071, 0.062, 0.006, (0.16, 0.16, 0.17, 1.0), 14)
    for k in range(10):
        a = math.radians(-60 + k * 30)
        C(f"_Dial_Hole_{k}", 0.046 * math.cos(a), -0.045 + 0.046 * math.sin(a), 0.0745, 0.0095, 0.002, (0.86, 0.84, 0.76, 1.0), 8)
    C("_Dial_Card", 0.0, -0.045, 0.0745, 0.022, 0.002, (0.92, 0.90, 0.84, 1.0), 10)
    B("_Dial_Stop", 0.058, -0.082, 0.076, 0.022, 0.006, 0.006, (0.78, 0.78, 0.76, 1.0))
    # the cradle horns and the handset across them
    for sg in (-1, 1):
        B(f"_Horn_{sg:+d}", sg * 0.075, 0.045, 0.112, 0.030, 0.050, 0.026, body)
    B("_Handset", 0.0, 0.045, 0.138, 0.230, 0.040, 0.030, body)
    for sg, nm in ((-1, "Ear"), (1, "Mouth")):
        C(f"_Handset_{nm}", sg * 0.100, 0.045, 0.126, 0.034, 0.034, body, 10)
    for k in range(5):
        B(f"_Cord_{k}", -0.130 - 0.006 * (k % 2), 0.02 - k * 0.022, 0.012, 0.014, 0.016, 0.014, body)


def make_loaf(prefix, x, y, base_z, *, along="X", length=0.30, r=0.075,
              crust=(0.66, 0.44, 0.22, 1.0), crumb=(0.93, 0.86, 0.68, 1.0), slices=2):
    """A loaf of bread with one end cut (pass 457): a low base, a round crown
    along its length, the pale cut face at local +v, and slices lying by it.
    Loaves were bricks. `prefix` may carry a `__view` tag."""
    head, _, tag = prefix.partition("__")
    tag = ("__" + tag) if tag else ""
    def nm(part):
        return head + (("_" + part) if part else "") + tag
    def W(u, v):                          # u across, v along
        return (x + v, y + u) if along == "X" else (x + u, y + v)
    def S(su, sv, sz):
        return (sv, su, sz) if along == "X" else (su, sv, sz)
    cx, cy = W(0.0, 0.0)
    make_box(nm(""), (cx, cy, base_z + r * 0.30), S(r * 2.0, length, r * 0.60), crust)
    make_cyl(nm("Crown"), (cx, cy, base_z + r * 0.62), r * 0.98, length, crust, segments=12, axis=along)
    # the baker's slashes across the crown, floured pale: what says BREAD from above
    from .geometry import make_rot_box
    for k in range(3):
        sx, sy = W(0.0, -length * 0.28 + k * length * 0.24)
        make_rot_box(nm(f"Score_{k}"), (sx, sy, base_z + r * 1.585), S(r * 1.25, 0.014, 0.006), (0.90, 0.80, 0.60, 1.0),
                     yaw=(0.55 if along == "X" else -0.55))
    fx, fy = W(0.0, length / 2.0 + 0.002)
    make_cyl(nm("Face"), (fx, fy, base_z + r * 0.62), r * 0.90, 0.004, crumb, segments=12, axis=along)
    lx, ly = W(0.0, length / 2.0 + 0.003)
    make_box(nm("Face_Low"), (lx, ly, base_z + r * 0.30), S(r * 1.80, 0.008, r * 0.56), crumb)
    for k in range(slices):
        sx, sy = W((-1) ** k * r * 0.5, length / 2.0 + 0.07 + k * 0.045)     # close by the cut end: further out they left the board
        make_cyl(nm(f"Slice_{k}"), (sx, sy, base_z + 0.007 + k * 0.012), r * 0.90, 0.012, crumb, segments=12)
        make_cyl(nm(f"Slice_{k}_Crust"), (sx, sy, base_z + 0.0065 + k * 0.012), r * 0.98, 0.010, crust, segments=12)


def make_iced_tea(prefix, x, y, base_z, *, h=0.145, r=0.036, lemon=True, straw=False):
    """A tall glass of iced tea (pass 458): the glass, the amber tea to
    three-quarters, ice at the surface, a lemon wedge on the rim. They were
    tan cylinders — wooden cups in the frame."""
    make_cyl(f"{prefix}", (x, y, base_z + h / 2.0), r, h, (0.80, 0.88, 0.90, 0.32), segments=14)
    make_cyl(f"{prefix}_Tea", (x, y, base_z + h * 0.39), r * 0.90, h * 0.74, (0.66, 0.34, 0.10, 0.92), segments=14)
    for k, (dx, dy) in enumerate(((0.012, 0.006), (-0.012, 0.004), (0.0, -0.013))):
        make_box(f"{prefix}_Ice_{k}", (x + dx, y + dy, base_z + h * 0.78), (0.018, 0.018, 0.016), (0.92, 0.95, 0.96, 0.85))
    make_cyl(f"{prefix}_Base", (x, y, base_z + 0.004), r * 0.94, 0.008, (0.86, 0.92, 0.94, 0.6), segments=14)
    if lemon:
        make_box(f"{prefix}_Lemon", (x + r * 0.92, y, base_z + h + 0.004), (0.010, 0.030, 0.022), (0.96, 0.86, 0.24, 1.0))
    if straw:
        make_cyl(f"{prefix}_Straw", (x - r * 0.45, y, base_z + h * 0.72), 0.004, h * 0.85, (0.90, 0.28, 0.24, 1.0), segments=5)


def make_laptop(prefix, x, y, base_z, *, yaw=0.0, w=0.34, d=0.24, body=(0.16, 0.16, 0.18, 1.0), screen="chat", lid=True):
    """An open laptop (pass 458): the base with its keyboard — five rows of
    keys, the trackpad, a red pointing-stick dot — and the lid standing
    behind it, its screen LIT with what the line says: "chat" (a window, a
    side list, message bubbles, the input bar) or "doc" (ruled text). They
    were a grey slab and a pale-blue slab. The lid stands at local +v, the
    screen facing -v."""
    from .geometry import make_rot_box
    at = _local(x, y, yaw)
    def B(part, u, v, z, su, sv, sz, col, pitch=0.0):
        px, py = at(u, v)
        make_rot_box(f"{prefix}{part}", (px, py, base_z + z), (su, sv, sz), col, yaw=yaw, pitch=pitch)
    B("_Base", 0.0, 0.0, 0.009, w, d, 0.018, body)
    key = (0.30, 0.30, 0.33, 1.0)
    for r in range(5):
        for c in range(11):
            B(f"_Key_{r}_{c}", -w * 0.42 + c * w * 0.084, d * 0.36 - r * d * 0.115, 0.0188, w * 0.068, d * 0.085, 0.0016, key)
    B("_Trackpad", 0.0, -d * 0.36, 0.0188, w * 0.30, d * 0.20, 0.0012, (0.24, 0.24, 0.27, 1.0))
    B("_Stick", 0.0, d * 0.13, 0.0200, 0.008, 0.008, 0.002, (0.86, 0.16, 0.14, 1.0))
    if not lid:
        # the builder keeps its own lid and display: a hero-art picture is
        # placed on that display by name (pass 459: Kai's and Bianca's)
        return
    sh = d * 0.96                       # the lid's height
    lv = d / 2.0 + 0.004
    B("_Lid", 0.0, lv, 0.018 + sh / 2.0, w, 0.010, sh, body)
    sv = lv - 0.0065
    lit = (0.92, 0.94, 0.97, 1.0)
    B("_Screen", 0.0, sv, 0.018 + sh / 2.0, w * 0.90, 0.003, sh * 0.86, lit)
    z0 = 0.018 + sh / 2.0
    f = sv - 0.0022
    if screen == "chat":
        B("_Screen_Bar", 0.0, f, z0 + sh * 0.385, w * 0.90, 0.0014, sh * 0.07, (0.24, 0.30, 0.44, 1.0))
        B("_Screen_List", -w * 0.33, f, z0 - sh * 0.03, w * 0.22, 0.0014, sh * 0.74, (0.80, 0.83, 0.88, 1.0))
        for k, (uu, zz, ww, col) in enumerate(((0.02, 0.24, 0.30, (0.78, 0.80, 0.84, 1.0)), (0.22, 0.10, 0.26, (0.26, 0.54, 0.94, 1.0)),
                                               (0.04, -0.04, 0.34, (0.78, 0.80, 0.84, 1.0)), (0.20, -0.17, 0.22, (0.26, 0.54, 0.94, 1.0)))):
            B(f"_Screen_Bubble_{k}", w * uu, f, z0 + sh * zz, w * ww, 0.0014, sh * 0.09, col)
        B("_Screen_Input", w * 0.11, f, z0 - sh * 0.36, w * 0.62, 0.0014, sh * 0.06, (0.84, 0.86, 0.90, 1.0))
    else:
        for k in range(7):
            B(f"_Screen_Line_{k}", -w * 0.04 if k % 3 else -w * 0.10, f, z0 + sh * (0.30 - k * 0.095), w * (0.70 if k % 3 else 0.56), 0.0014, sh * 0.03, (0.20, 0.22, 0.28, 1.0))


def _split_tag(prefix):
    """("Name", "__tag") from "Name__tag": parts are named Name_Part__tag."""
    i = prefix.find("__")
    return (prefix, "") if i < 0 else (prefix[:i], prefix[i:])


def _tint(c, k):
    return (min(1.0, c[0] * k), min(1.0, c[1] * k), min(1.0, c[2] * k), c[3])


def make_recliner(prefix, x, y, base_z, *, yaw=0.0, w=0.88, color=(0.40, 0.30, 0.24, 1.0), reclined=True):
    """An upholstered recliner (pass 461): a skirted base, a seat cushion,
    two fat arms with padded tops, a tall back in two tufted cushions with a
    headrest roll, the footrest out on its scissor arms and the side lever.
    It was two slabs and a plank. The front (footrest) is local +v; the back
    leans toward -v. `reclined=False` folds the footrest under the seat."""
    from .geometry import make_rot_box
    name, tag = _split_tag(prefix)
    at = _local(x, y, yaw)
    pad, dark, metal = _tint(color, 1.16), _tint(color, 0.74), (0.20, 0.20, 0.21, 1.0)
    def B(part, u, v, z, su, sv, sz, col, roll=0.0):
        px, py = at(u, v)
        make_rot_box(f"{name}{part}{tag}", (px, py, base_z + z), (su, sv, sz), col, yaw=yaw, roll=roll)
    inner = w - 0.36
    B("_Base", 0.0, 0.0, 0.13, w - 0.04, 0.78, 0.22, dark)
    B("_Foot_L", -(w / 2.0 - 0.08), 0.0, 0.01, 0.08, 0.70, 0.02, metal)
    B("_Foot_R", (w / 2.0 - 0.08), 0.0, 0.01, 0.08, 0.70, 0.02, metal)
    B("_Seat", 0.0, 0.05, 0.33, inner, 0.62, 0.18, pad)
    for s, nm in ((-1, "L"), (1, "R")):
        B(f"_Arm_{nm}", s * (w / 2.0 - 0.09), 0.0, 0.40, 0.18, 0.82, 0.32, color)
        B(f"_Arm_{nm}_Pad", s * (w / 2.0 - 0.09), 0.02, 0.59, 0.20, 0.78, 0.06, pad)
    lean = 0.42 if reclined else 0.14
    # the back: a frame, two tufted cushions and the headrest roll
    B("_Back", 0.0, -0.42 - 0.10 * math.sin(lean), 0.74, inner + 0.10, 0.14, 0.86, color, roll=lean)
    for k, zz in enumerate((0.56, 0.84)):
        B(f"_Back_Cushion_{k}", 0.0, -0.33 - (zz - 0.40) * math.tan(lean) * 0.9, zz, inner - 0.02, 0.10, 0.25, pad, roll=lean)
    B("_Headrest", 0.0, -0.33 - (1.06 - 0.40) * math.tan(lean) * 0.9, 1.06, inner - 0.06, 0.13, 0.15, pad, roll=lean)
    if reclined:
        B("_Footrest", 0.0, 0.74, 0.37, inner + 0.04, 0.42, 0.09, pad, roll=-0.10)
        for s, nm in ((-1, "L"), (1, "R")):
            B(f"_Footrest_Arm_{nm}", s * (inner / 2.0 - 0.04), 0.50, 0.29, 0.03, 0.36, 0.03, metal, roll=0.30)
    else:
        B("_Footrest", 0.0, 0.40, 0.20, inner + 0.04, 0.05, 0.30, pad)
    B("_Lever", (w / 2.0 + 0.012), 0.12, 0.36, 0.024, 0.04, 0.18, metal, roll=-0.5)
    B("_Lever_Grip", (w / 2.0 + 0.012), 0.165, 0.45, 0.034, 0.05, 0.06, (0.50, 0.38, 0.26, 1.0), roll=-0.5)


def make_panel_door(prefix, x, y, base_z, *, axis="Y", w=0.84, h=2.0, t=0.045, color=(0.64, 0.56, 0.44, 1.0),
                    faces=(-1, 1), glass=False, knob_side=1, deadbolt=True, casing=0.0,
                    trim=(0.86, 0.84, 0.78, 1.0), brass=(0.72, 0.58, 0.28, 1.0), pane=(0.10, 0.13, 0.19, 1.0)):
    """A shut door that reads as a door (pass 461): the slab, raised panels
    on each face named in `faces` (six, or with `glass=True` a four-light
    window over two panels), a knob on its rose, a deadbolt above it and
    three hinge knuckles on the other stile. `axis` is the axis the door's
    WIDTH runs along; `faces` are the signs, across the slab, that get the
    detail; `knob_side` is the sign, along the width, of the latch stile.
    `casing` is the thickness of the wall the door hangs in: given, each
    detailed face also gets the casing boards round the opening, on the wall.
    It was one flat slab in an opening."""
    name, tag = _split_tag(prefix)
    hi, lo = _tint(color, 1.10), _tint(color, 0.80)
    def B(part, a, c, z, sa, sc, sz, col):
        if axis == "Y":
            make_box(f"{name}{part}{tag}", (x + c, y + a, base_z + z), (sc, sa, sz), col)
        else:
            make_box(f"{name}{part}{tag}", (x + a, y + c, base_z + z), (sa, sc, sz), col)
    B("", 0.0, 0.0, h / 2.0, w, t, h, color)
    for s in faces:
        f = "N" if s < 0 else "P"
        c1 = s * (t / 2.0 + 0.005)
        if glass:
            z0, z1 = 0.54 * h, 0.92 * h
            B(f"_{f}_Light", 0.0, c1, (z0 + z1) / 2.0, w * 0.66, 0.010, z1 - z0, pane)
            B(f"_{f}_Muntin_V", 0.0, s * (t / 2.0 + 0.011), (z0 + z1) / 2.0, 0.024, 0.012, z1 - z0, hi)
            B(f"_{f}_Muntin_H", 0.0, s * (t / 2.0 + 0.010), (z0 + z1) / 2.0, w * 0.66, 0.010, 0.024, hi)
            rows = ((0.10 * h, 0.46 * h),)
        else:
            rows = ((0.10 * h, 0.40 * h), (0.45 * h, 0.76 * h), (0.80 * h, 0.93 * h))
        for r, (z0, z1) in enumerate(rows):
            for k, a in enumerate((-w * 0.215, w * 0.215)):
                B(f"_{f}_Panel_{r}_{k}", a, c1, (z0 + z1) / 2.0, w * 0.33, 0.010, z1 - z0, lo)
                B(f"_{f}_Panel_{r}_{k}_Field", a, s * (t / 2.0 + 0.014), (z0 + z1) / 2.0, w * 0.33 - 0.07, 0.008, z1 - z0 - 0.07, hi)
        if casing > 0.0:
            cc = s * (casing / 2.0 + 0.007)
            for k in (-1, 1):
                B(f"_{f}_Casing_{'A' if k < 0 else 'B'}", k * (w / 2.0 + 0.055), cc, (h + 0.09) / 2.0, 0.08, 0.014, h + 0.09, trim)
            B(f"_{f}_Casing_Head", 0.0, cc, h + 0.055, w + 0.19, 0.014, 0.09, trim)
        ka = knob_side * (w / 2.0 - 0.07)
        B(f"_{f}_Rose", ka, c1, 0.96, 0.07, 0.010, 0.07, brass)
        B(f"_{f}_Knob_Stem", ka, s * (t / 2.0 + 0.022), 0.96, 0.024, 0.024, 0.024, brass)
        B(f"_{f}_Knob", ka, s * (t / 2.0 + 0.052), 0.96, 0.056, 0.036, 0.056, brass)
        if deadbolt:
            B(f"_{f}_Deadbolt", ka, c1, 1.12, 0.06, 0.010, 0.06, brass)
            B(f"_{f}_Deadbolt_Turn", ka, s * (t / 2.0 + 0.018), 1.12, 0.016, 0.016, 0.040, brass)
        for k, zz in enumerate((0.20, h / 2.0, h - 0.20)):
            B(f"_{f}_Hinge_{k}", -knob_side * (w / 2.0 - 0.008), s * (t / 2.0 + 0.008), zz, 0.016, 0.016, 0.10, (0.50, 0.48, 0.44, 1.0))


def make_electric_guitar(prefix, x, y, base_z, *, yaw=0.0, body=(0.86, 0.60, 0.26, 1.0), guard=(0.08, 0.08, 0.09, 1.0),
                         neck=(0.88, 0.76, 0.52, 1.0), stand=True):
    """A single-cutaway slab electric on an A-frame stand (pass 462: Jesse's
    Telecaster): the body with its one horn, the pickguard, the bridge plate
    and neck pickup, the control plate with two knobs, the maple neck with
    frets and dots, the six-in-line headstock and its tuners. The FRONT is
    local -v. Every part is 8 mm or thicker (the old one's 3 mm pickguard,
    plate and fretboard drew black) and stands proud of the part under it."""
    from .geometry import make_rot_box
    name, tag = _split_tag(prefix)
    at = _local(x, y, yaw)
    chrome, dark = (0.78, 0.80, 0.82, 1.0), (0.10, 0.10, 0.11, 1.0)
    def B(part, u, v, z, su, sv, sz, col):
        px, py = at(u, v)
        make_rot_box(f"{name}{part}{tag}", (px, py, base_z + z), (su, sv, sz), col, yaw=yaw)
    if stand:
        for s, nm in ((-1, "L"), (1, "R")):
            B(f"_Stand_Leg_{nm}", s * 0.13, 0.07, 0.31, 0.03, 0.03, 0.62, dark)
            B(f"_Stand_Foot_{nm}", s * 0.13, 0.02, 0.015, 0.03, 0.30, 0.03, dark)
            B(f"_Stand_Cradle_{nm}", s * 0.10, 0.02, 0.285, 0.03, 0.13, 0.03, dark)
        B("_Stand_Cross", 0.0, 0.07, 0.285, 0.29, 0.03, 0.03, dark)
        B("_Stand_Post", 0.0, 0.07, 0.72, 0.03, 0.03, 0.84, dark)
        B("_Stand_Yoke", 0.0, 0.045, 1.13, 0.09, 0.08, 0.03, dark)
    # the slab body: lower bout, waist, the one (bass-side) horn
    B("_Body", 0.0, 0.0, 0.43, 0.33, 0.045, 0.26, body)
    B("_Body_Waist", -0.01, 0.0, 0.62, 0.29, 0.045, 0.14, body)
    B("_Body_Horn", -0.095, 0.0, 0.735, 0.12, 0.045, 0.10, body)
    f1 = -0.0225 - 0.005
    B("_Pickguard", -0.03, f1, 0.60, 0.20, 0.010, 0.20, guard)
    B("_Bridge_Plate", 0.0, f1, 0.405, 0.09, 0.010, 0.11, chrome)
    B("_Bridge_Pickup", 0.0, f1 - 0.008, 0.425, 0.07, 0.008, 0.022, dark)
    B("_Neck_Pickup", -0.005, f1 - 0.009, 0.665, 0.075, 0.008, 0.032, chrome)
    B("_Control_Plate", 0.115, f1, 0.44, 0.036, 0.010, 0.15, chrome)
    for k, zz in enumerate((0.395, 0.445)):
        B(f"_Knob_{k}", 0.115, f1 - 0.013, zz, 0.024, 0.016, 0.024, chrome)
    B("_Switch_Tip", 0.115, f1 - 0.012, 0.495, 0.012, 0.014, 0.012, dark)
    # the neck, its fretboard, frets and dots; the headstock and tuners
    B("_Neck", 0.0, -0.004, 1.04, 0.056, 0.030, 0.70, neck)
    B("_Fretboard", 0.0, -0.029, 1.045, 0.052, 0.010, 0.68, _tint(neck, 1.08))
    zf = 1.375
    for k in range(10):
        B(f"_Fret_{k}", 0.0, -0.036, zf, 0.052, 0.008, 0.008, chrome)
        if k in (2, 4, 6):
            B(f"_Dot_{k}", 0.0, -0.036, zf - 0.028, 0.012, 0.008, 0.012, dark)
        zf -= 0.075 - k * 0.004
    B("_Nut", 0.0, -0.036, 1.392, 0.054, 0.012, 0.010, (0.94, 0.92, 0.86, 1.0))
    B("_Head", -0.012, -0.004, 1.49, 0.084, 0.022, 0.20, neck)
    for k in range(6):
        B(f"_Tuner_{k}", -0.066, -0.004, 1.415 + k * 0.030, 0.026, 0.016, 0.016, chrome)
        B(f"_Tuner_Post_{k}", -0.035, -0.019, 1.415 + k * 0.030, 0.010, 0.010, 0.010, chrome)


_AX = {"X": (1.0, 0.0, 0.0), "Y": (0.0, 1.0, 0.0), "Z": (0.0, 0.0, 1.0)}


def make_skateboard(prefix, x, y, z, *, L="Y", W="Z", N="+X", length=0.80, width=0.20,
                    deck=(0.12, 0.12, 0.14, 1.0), graphic=(0.80, 0.30, 0.20, 1.0), wheel=(0.92, 0.88, 0.72, 1.0)):
    """A skateboard (pass 463): a deck with a narrowed nose and tail, grip
    tape on top, a graphic and two stripes underneath, two trucks (baseplate
    and hanger) and four wheels on the hanger ends. (x, y, z) is the deck's
    centre; L and W are the world axes its length and width run along, N the
    signed axis from the deck toward its WHEELS ("+X": hung on a wall, wheels
    out into the room; "-Z": on the floor, at z 0.072). It was a slab with two
    wheels on its centreline."""
    name, tag = _split_tag(prefix)
    sgn = -1.0 if N[0] == "-" else 1.0
    lv, wv, nv = _AX[L], _AX[W], tuple(sgn * c for c in _AX[N[-1]])
    def P(l, w, n):
        return (x + l * lv[0] + w * wv[0] + n * nv[0], y + l * lv[1] + w * wv[1] + n * nv[1], z + l * lv[2] + w * wv[2] + n * nv[2])
    def Sz(sl, sw, sn):
        return tuple(abs(sl * lv[i]) + abs(sw * wv[i]) + abs(sn * nv[i]) for i in range(3))
    def B(part, l, w, n, sl, sw, sn, col):
        make_box(f"{name}{part}{tag}", P(l, w, n), Sz(sl, sw, sn), col)
    steel = (0.62, 0.63, 0.65, 1.0)
    B("_Deck", 0.0, 0.0, 0.0, length - 0.16, width, 0.014, deck)
    for s, nm in ((-1, "Tail"), (1, "Nose")):
        B(f"_Deck_{nm}", s * (length / 2.0 - 0.055), 0.0, 0.0, 0.05, width - 0.03, 0.014, deck)
        B(f"_Deck_{nm}_Tip", s * (length / 2.0 - 0.015), 0.0, 0.0, 0.03, width - 0.09, 0.014, deck)
    B("_Grip", 0.0, 0.0, -0.011, length - 0.18, width - 0.012, 0.008, (0.07, 0.07, 0.08, 1.0))
    B("_Graphic", 0.0, 0.0, 0.011, length * 0.34, width - 0.05, 0.008, graphic)
    for s, nm in ((-1, "A"), (1, "B")):
        B(f"_Graphic_Stripe_{nm}", s * length * 0.235, 0.0, 0.011, 0.022, width - 0.05, 0.008, _tint(graphic, 1.25))
        B(f"_Truck_{nm}_Base", s * 0.26, 0.0, 0.017, 0.07, 0.055, 0.020, steel)
        B(f"_Truck_{nm}_Hanger", s * 0.26, 0.0, 0.040, 0.030, width - 0.07, 0.026, steel)
        for ws, wn in ((-1, "L"), (1, "R")):
            make_cyl(f"{name}_Wheel_{nm}_{wn}{tag}", P(s * 0.26, ws * (width / 2.0 - 0.017), 0.045), 0.027, 0.034, wheel, segments=10, axis=W)


def make_toilet(prefix, x, y, base_z, *, yaw=0.0, lid_up=True, enamel=(0.86, 0.86, 0.82, 1.0)):
    """A toilet (pass 463): the tank and its lid, the flush lever, the bowl
    as a lathe, the SEAT as a ring with the water showing in it, and the lid
    stood up against the tank (or shut). The bowl's centre is (x, y); the
    tank is toward local -v. The seat was a solid slab: from above the
    fixture read as a box."""
    from .geometry import make_rot_box, make_lathe
    name, tag = _split_tag(prefix)
    at = _local(x, y, yaw)
    seat = _tint(enamel, 0.94)
    def B(part, u, v, z, su, sv, sz, col, roll=0.0):
        px, py = at(u, v)
        make_rot_box(f"{name}{part}{tag}", (px, py, base_z + z), (su, sv, sz), col, yaw=yaw, roll=roll)
    B("_Tank", 0.0, -0.32, 0.62, 0.44, 0.20, 0.38, enamel)
    B("_Tank_Lid", 0.0, -0.32, 0.825, 0.46, 0.22, 0.03, enamel)
    B("_Flush", -0.15, -0.212, 0.74, 0.07, 0.016, 0.024, (0.62, 0.63, 0.65, 1.0))
    B("_Neck", 0.0, -0.20, 0.30, 0.22, 0.14, 0.24, enamel)
    make_lathe(f"{name}_Bowl{tag}", (x, y, base_z), [(0.13, 0.0), (0.10, 0.08), (0.12, 0.25), (0.20, 0.39), (0.0, 0.39)], enamel, segments=14)
    make_lathe(f"{name}_Seat{tag}", (x, y, base_z + 0.39), [(0.135, 0.0), (0.215, 0.0), (0.215, 0.028), (0.135, 0.028)], seat, segments=14)
    # (make_lathe caps its ends, so the "ring" is a disc: the water sits ON it,
    # a centimetre proud, and reads as the water in the bowl)
    make_cyl(f"{name}_Water{tag}", (x, y, base_z + 0.423), 0.128, 0.010, (0.56, 0.76, 0.88, 1.0), segments=14)
    if lid_up:
        B("_Lid_Leaf", 0.0, -0.185, 0.63, 0.40, 0.03, 0.42, seat, roll=0.10)
    else:
        B("_Lid_Leaf", 0.0, 0.0, 0.433, 0.40, 0.43, 0.03, seat)
