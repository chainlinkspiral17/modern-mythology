# _props/views.py
# ════════════════════════════════════════════════════════════════
# WHAT IS OUTSIDE THE WINDOW (2026-10-07). Twenty-five rooms built
# their windows as panes on SOLID walls — nothing could be seen out of
# them, and a room with no outside is the claustrophobia the user keeps
# naming ("Backgrounds always felt small and claustrophobic"). A cut
# window needs a world past it; these lay one out beyond any wall.
#
#   make_view(prefix, side, wall_line, center, kind, ground_z=0.0, ...)
#
# side       'N' | 'S' | 'E' | 'W' — which wall the window is in (the
#            view runs AWAY from the room in that direction)
# wall_line  the wall's centre line (y for N/S, x for E/W)
# center     the window's centre along the wall
# kind       'front'  the street side of a planned-community house: lawn,
#                     walk, curb, street, the houses across with porch
#                     lights and mailboxes, a front-yard tree
#            'back'   the back yard: lawn, board fence, a tree, the
#                     neighbours' rooflines past the fence
#            'side'   the side yard: a strip of lawn, the neighbour's wall
#                     close, its window, a fence line
#            'street' a shop's street: walk, curb, two lanes, parked cars,
#                     the facades across, lamp posts
# ground_z   where the ground is relative to the room's floor (an upstairs
#            room: about -2.9)
# ════════════════════════════════════════════════════════════════
from .geometry import make_box, make_cyl, make_blob, make_taper_cyl

GRASS = (0.38, 0.50, 0.28, 1.0)
CONCRETE = (0.62, 0.60, 0.56, 1.0)
ASPHALT = (0.30, 0.30, 0.32, 1.0)
WOOD = (0.58, 0.48, 0.36, 1.0)
HOUSE_COLS = ((0.86, 0.80, 0.70, 1.0), (0.80, 0.82, 0.78, 1.0), (0.88, 0.78, 0.66, 1.0), (0.76, 0.72, 0.66, 1.0))
ROOF = (0.36, 0.32, 0.28, 1.0)


class _Frame:
    """u along the wall from the window's centre, v outward from the wall
    line, z up — mapped to the world for the wall's side."""

    def __init__(self, side, wall_line, center, gz):
        self.side, self.w, self.c, self.gz = side.upper(), wall_line, center, gz

    def p(self, u, v, z):
        s = self.side
        if s == 'N':
            return (self.c + u, self.w + v, self.gz + z)
        if s == 'S':
            return (self.c - u, self.w - v, self.gz + z)
        if s == 'E':
            return (self.w + v, self.c - u, self.gz + z)
        return (self.w - v, self.c + u, self.gz + z)

    def sz(self, su, sv, sz):
        return (su, sv, sz) if self.side in ('N', 'S') else (sv, su, sz)


def _box(F, name, u, v, z, su, sv, sz, col):
    make_box(name, F.p(u, v, z), F.sz(su, sv, sz), col)


def _house(F, pre, u, v, w, d, h, col, door=True, porch_light=False, facing_room=True):
    _box(F, f"{pre}_Wall", u, v + d / 2.0, (h - 0.12) / 2.0, w, d, h + 0.12, col)
    _box(F, f"{pre}_Roof", u, v + d / 2.0, h + 0.40, w + 0.8, d + 0.8, 0.80, ROOF)
    _box(F, f"{pre}_Roof_Ridge", u, v + d / 2.0, h + 0.95, w - 1.0, 0.5, 0.30, (0.30, 0.27, 0.24, 1.0))
    face = v - 0.02
    for k, du in enumerate((-w / 4.0, w / 4.0 + 0.6)):
        _box(F, f"{pre}_Window_{k}", u + du, face, 1.55, 1.40, 0.04, 1.10, (0.30, 0.34, 0.38, 1.0))
        _box(F, f"{pre}_Window_{k}_Trim", u + du, face - 0.01, 0.95, 1.56, 0.04, 0.10, (0.92, 0.90, 0.84, 1.0))
    if door:
        _box(F, f"{pre}_Door", u + 0.4, face, 1.05, 0.95, 0.04, 2.10, (0.42, 0.30, 0.22, 1.0))
        _box(F, f"{pre}_Stoop", u + 0.4, v - 0.60, 0.07, 1.6, 1.2, 0.14, CONCRETE)
    if porch_light:
        _box(F, f"{pre}_Porch_Light_Bracket", u + 1.05, face - 0.02, 2.22, 0.06, 0.04, 0.06, (0.20, 0.20, 0.22, 1.0))
        make_cyl(f"{pre}_Porch_Light", F.p(u + 1.05, face - 0.06, 2.10), 0.06, 0.12, (0.98, 0.86, 0.56, 1.0), segments=8)


def _tree(F, pre, u, v, h=4.5, r=1.6, col=(0.30, 0.44, 0.24, 1.0), seed=0):
    make_taper_cyl(f"{pre}_Trunk", F.p(u, v, h * 0.35 - 0.06), 0.16, 0.10, h * 0.7 + 0.12, (0.40, 0.32, 0.24, 1.0), segments=8)
    make_blob(f"{pre}_Canopy", F.p(u, v, h * 0.75), r, col, noise=0.24, seed=seed, squash=0.8)


def make_view(prefix, side, wall_line, center, kind="back", ground_z=0.0, span=24.0, seed=0, logo_mailbox=False):
    F = _Frame(side, wall_line, center, ground_z)
    gz = -0.03
    if kind == "front":
        _box(F, f"{prefix}_Ground_Lawn", 0.0, 4.3, gz, span, 8.0, 0.05, GRASS)
        _box(F, f"{prefix}_Ground_Walk", 0.0, 8.9, gz + 0.01, span, 1.2, 0.05, CONCRETE)
        _box(F, f"{prefix}_Ground_Curb", 0.0, 9.6, gz + 0.04, span, 0.15, 0.12, (0.56, 0.54, 0.50, 1.0))
        _box(F, f"{prefix}_Ground_Street", 0.0, 13.2, gz, span, 7.0, 0.05, ASPHALT)
        _box(F, f"{prefix}_Ground_Curb_Far", 0.0, 16.8, gz + 0.04, span, 0.15, 0.12, (0.56, 0.54, 0.50, 1.0))
        _box(F, f"{prefix}_Ground_Walk_Far", 0.0, 17.5, gz + 0.01, span, 1.2, 0.05, CONCRETE)
        _box(F, f"{prefix}_Ground_Lawn_Far", 0.0, 22.0, gz, span, 7.8, 0.05, GRASS)
        for k, du in enumerate((-9.0, 0.5, 10.0)):
            _house(F, f"{prefix}_House_{k}", du, 24.0, 8.0, 7.0, 3.4, HOUSE_COLS[(k + seed) % 4], porch_light=True)
            make_cyl(f"{prefix}_House_{k}_Mailbox_Post", F.p(du + 2.6, 18.3, 0.55), 0.05, 1.10, (0.30, 0.30, 0.32, 1.0), segments=6)
            _box(F, f"{prefix}_House_{k}_Mailbox", du + 2.6, 18.3, 1.18, 0.48, 0.22, 0.24, (0.20, 0.20, 0.22, 1.0))
            if logo_mailbox:
                _box(F, f"{prefix}_House_{k}_Mailbox_Logo", du + 2.6, 18.18, 1.18, 0.20, 0.004, 0.08, (0.16, 0.32, 0.56, 1.0))
        _tree(F, f"{prefix}_Front_Tree", -4.5, 4.5, h=5.0, r=1.8, seed=seed)
        for k, du in enumerate((-2.0, 2.5)):
            make_cyl(f"{prefix}_Sprinkler_{k}", F.p(du, 3.0, 0.03), 0.03, 0.07, (0.30, 0.32, 0.30, 1.0), segments=6)
        for k, du in enumerate((-7.0, 7.0)):
            make_cyl(f"{prefix}_Street_Light_{k}_Pole", F.p(du, 9.9, 3.0), 0.08, 6.0, (0.50, 0.50, 0.52, 1.0), segments=6)
            _box(F, f"{prefix}_Street_Light_{k}_Head", du, 10.4, 5.95, 0.30, 1.0, 0.14, (0.40, 0.40, 0.42, 1.0))
    elif kind == "back":
        _box(F, f"{prefix}_Ground_Lawn", 0.0, 4.0, gz, span, 8.0, 0.05, GRASS)
        _box(F, f"{prefix}_Ground_Patio", 0.0, 1.4, gz + 0.02, 4.0, 2.4, 0.05, CONCRETE)
        fv = 7.5
        _box(F, f"{prefix}_Fence_Boards", 0.0, fv, 0.85, span, 0.04, 1.80, WOOD)
        n = int(span / 2.4)
        for k in range(n + 1):
            _box(F, f"{prefix}_Fence_Post_{k}", -span / 2.0 + k * span / n, fv - 0.05, 0.92, 0.10, 0.10, 1.94, (0.50, 0.42, 0.32, 1.0))
        _tree(F, f"{prefix}_Tree", -3.0, 4.6, h=5.5, r=2.0, seed=seed)
        _box(F, f"{prefix}_Ground_Beyond", 0.0, fv + 8.0, gz, span * 2, 16.0, 0.05, GRASS)
        for k, du in enumerate((-8.0, 4.0)):
            _house(F, f"{prefix}_Neighbor_{k}", du, fv + 4.0, 9.0, 7.0, 3.2, HOUSE_COLS[(k + seed + 1) % 4], door=False)
        _tree(F, f"{prefix}_Tree_Far", 9.0, fv + 2.2, h=6.5, r=2.4, col=(0.26, 0.40, 0.22, 1.0), seed=seed + 3)
    elif kind == "side":
        _box(F, f"{prefix}_Ground_Lawn", 0.0, 2.2, gz, span, 4.4, 0.05, GRASS)
        _box(F, f"{prefix}_Fence_Boards", 6.0, 2.2, 0.85, 0.04, 4.0, 1.80, WOOD)
        _house(F, f"{prefix}_Neighbor", 0.0, 4.4, 12.0, 8.0, 3.2, HOUSE_COLS[(seed + 2) % 4], door=False)
        _box(F, f"{prefix}_Ground_AC_Pad", -3.0, 3.8, gz + 0.03, 1.0, 0.8, 0.06, CONCRETE)
        _box(F, f"{prefix}_AC_Unit", -3.0, 3.8, 0.38, 0.80, 0.70, 0.70, (0.66, 0.66, 0.64, 1.0))
    else:   # street
        _box(F, f"{prefix}_Ground_Walk", 0.0, 1.2, gz + 0.01, span, 2.4, 0.05, CONCRETE)
        _box(F, f"{prefix}_Ground_Curb", 0.0, 2.45, gz + 0.04, span, 0.15, 0.12, (0.56, 0.54, 0.50, 1.0))
        _box(F, f"{prefix}_Ground_Street", 0.0, 6.5, gz, span, 8.0, 0.05, ASPHALT)
        for k in range(int(span / 6)):
            _box(F, f"{prefix}_Ground_Street_Dash_{k}", -span / 2.0 + 3.0 + k * 6.0, 6.5, gz + 0.03, 2.0, 0.12, 0.005, (0.92, 0.88, 0.70, 1.0))
        _box(F, f"{prefix}_Ground_Walk_Far", 0.0, 11.7, gz + 0.01, span, 2.4, 0.05, CONCRETE)
        for k, du in enumerate((-8.0, 0.0, 8.0)):
            col = HOUSE_COLS[(k + seed) % 4]
            _box(F, f"{prefix}_Facade_{k}", du, 15.0, 2.4, 7.8, 4.0, 4.8, col)
            _box(F, f"{prefix}_Facade_{k}_Glass", du, 12.98, 1.5, 5.0, 0.04, 1.8, (0.26, 0.32, 0.36, 1.0))
            _box(F, f"{prefix}_Facade_{k}_Sign", du, 12.96, 3.6, 4.0, 0.06, 0.6, ((0.70, 0.20, 0.16, 1.0), (0.20, 0.36, 0.56, 1.0), (0.86, 0.66, 0.24, 1.0))[(k + seed) % 3])
        for k, du in enumerate((-4.0, 5.0)):
            _box(F, f"{prefix}_Parked_Car_{k}_Body", du, 3.6, 0.62, 4.2, 1.7, 0.60, ((0.62, 0.64, 0.66, 1.0), (0.40, 0.18, 0.16, 1.0))[k])
            _box(F, f"{prefix}_Parked_Car_{k}_Cabin", du - 0.2, 3.6, 1.12, 2.2, 1.5, 0.42, (0.24, 0.28, 0.30, 1.0))
            for e, (wu, wv) in enumerate(((-1.4, -0.86), (1.4, -0.86), (-1.4, 0.86), (1.4, 0.86))):
                make_cyl(f"{prefix}_Parked_Car_{k}_Wheel_{e}", F.p(du + wu, 3.6 + wv, 0.31), 0.31, 0.22, (0.14, 0.14, 0.15, 1.0),
                         axis=('Y' if F.side in ('N', 'S') else 'X'), segments=10)
        for k, du in enumerate((-6.0, 6.0)):
            make_cyl(f"{prefix}_Lamp_Post_{k}", F.p(du, 2.2, 2.6), 0.08, 5.2, (0.30, 0.30, 0.32, 1.0), segments=6)
            _box(F, f"{prefix}_Lamp_Post_{k}_Head", du, 2.2, 5.25, 0.40, 0.40, 0.20, (0.30, 0.30, 0.32, 1.0))
