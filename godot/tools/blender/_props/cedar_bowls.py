"""Olaf's cedar bowls — one bowl, every room (pass 454).

The cabin built them (build_cabin_interior.olaf_bowl); Hans's bakery had four
plain lathes for the same four bowls, and ch17's "insert bowl" lines framed
shallow dishes round a crow made of two boxes. The bowl is the text's: cedar,
"the size of two cupped hands", "A spiral was cut into the outside that ran
from the rim down to the base in a single continuous curve" (vol7 ch11_per),
three risen totems a quarter-turn apart from the rim — "A crow on a fencepost
at the level of the rim … An octopus a quarter of the way around … A ferret on
a stair-rail another quarter around" — smaller figures between them, and the
flame-mark on the base. The substrate-bowl is "the size of his palm" (s=0.62).

`kit` lets a builder pass its own (wrapped / shifted) geometry helpers; the
cabin builds inside a shifted block and must.
"""
import math as _m
from . import geometry as _G

CEDAR_LT = (0.72, 0.52, 0.32, 1.0)   # planed cedar heartwood
CEDAR_MD = (0.62, 0.43, 0.26, 1.0)   # the turned outside
CEDAR_DK = (0.44, 0.29, 0.18, 1.0)   # shadowed inside
CHAR = (0.20, 0.13, 0.09, 1.0)       # the heated-iron flame-mark
SLICKER = (0.88, 0.72, 0.18, 1.0)

_KIT = ("make_cyl", "make_taper_cyl", "make_tube", "make_blob", "make_lathe")


def make_olaf_bowl(pfx, bx, by, top_z, tag, s=1.0, mark=True, slicker=False, phase=None,
                   colors=None, kit=None, totem_names=False):
    """One bowl standing on a surface at `top_z`. Parts are `<pfx>_<Part>__<tag>`.
    `totem_names`: name the three totems Totem_Crow / Totem_Octopus /
    Totem_Ferret (a room whose lines cue "the crow on Roy's bowl") rather than
    Relief_0..2."""
    k = {n: getattr(_G, n) for n in _KIT}
    if kit:
        k.update(kit)
    make_cyl, make_taper_cyl, make_tube, make_blob, make_lathe = (k[n] for n in _KIT)
    cedar_dk, cedar_md, cedar_lt, char = colors or (CEDAR_DK, CEDAR_MD, CEDAR_LT, CHAR)
    T_ = lambda nm: "%s_%s__%s" % (pfx, nm, tag)
    make_cyl(T_("Foot"), (bx, by, top_z + 0.012 * s), 0.052 * s, 0.024 * s, cedar_dk, segments=14)
    if mark:
        make_cyl(T_("FlameMark"), (bx, by, top_z + 0.003), 0.026 * s, 0.004, char, segments=8)
    make_taper_cyl(T_("Body"), (bx, by, top_z + 0.072 * s), 0.058 * s, 0.115 * s, 0.096 * s, cedar_md, segments=16)

    def r_at(h):              # the body's outer radius, h (scaled) above its foot
        return (0.058 + 0.057 * h / (0.096 * s)) * s
    ph = (bx * 7.0 + by * 3.0) % 6.2832 if phase is None else phase
    sl = max(s, 0.85)          # the carving does not shrink with a palm-size bowl
    pts = []
    for i in range(41):
        u = i / 40.0
        h = (0.088 - 0.076 * u) * s
        a = ph + u * 2.5 * 6.2832
        r = r_at(h) + 0.0010 * s
        pts.append((bx + r * _m.cos(a), by + r * _m.sin(a), top_z + 0.024 * s + h))
    make_tube(T_("Spiral"), pts, 0.0030 * sl, cedar_dk, segments=5)
    names = ("Totem_Crow", "Totem_Octopus", "Totem_Ferret") if totem_names else ("Relief_0", "Relief_1", "Relief_2")
    for fi, (u, rr) in enumerate(((0.02, 0.0095), (0.12, 0.0095), (0.22, 0.0095),
                                  (0.07, 0.0060), (0.17, 0.0060), (0.27, 0.0060))):
        h = (0.088 - 0.076 * u) * s
        a = ph + u * 2.5 * 6.2832
        r = r_at(h) + 0.0015 * s
        # the substrate-bowl's young woman: "the woman's slicker was the yellow
        # of a slicker Kai had not … seen carved into any bowl" (ch11_bowl n55)
        rcol = SLICKER if (slicker and fi == 4) else cedar_lt
        make_blob(T_(names[fi] if fi < 3 else "Relief_%d" % fi),
                  (bx + r * _m.cos(a), by + r * _m.sin(a), top_z + 0.024 * s + h - 0.006 * s),
                  rr * sl, rcol, noise=0.25, seed=31 + fi, rings=4, segments=7, squash=1.0)
    make_lathe(T_("Rim"), (bx, by, top_z + 0.120 * s),
               [(0.104 * s, 0.0), (0.122 * s, 0.0), (0.122 * s, 0.020 * s), (0.104 * s, 0.020 * s), (0.104 * s, 0.0)],
               cedar_lt, segments=16)
    make_cyl(T_("Hollow"), (bx, by, top_z + 0.121 * s), 0.104 * s, 0.002, cedar_dk, segments=16)
