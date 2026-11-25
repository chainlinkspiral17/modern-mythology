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
