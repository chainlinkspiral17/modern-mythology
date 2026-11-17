"""STREETS (pass 421, 2026-11-16): curbs, walks, curb cuts and driveways
that meet one another.

The user: "Curbs and driveways look broken or incomplete." What the sets
had: a curb box laid straight across every driveway mouth (no car could
get in); driveways 4 cm lower than the walk they crossed, so each one
vanished under it; a cul-de-sac ring built from rotated boxes, saw-toothed
at its outer edge, meeting the straight walk in a notch.

What a street edge is here, built from ONE path — the asphalt's edge,
the curb face — so every part of it shares the same line:

    asphalt | curb (0.20, top 0.09) | walk (1.30, top 0.07) | lawn / drive

  * a CURB CUT at each driveway mouth: the curb drops to a 2 cm lip over
    the mouth and the walk's street half ramps up from it to walk height
    (an apron), with a 0.6 m transition each side where the curb comes
    down;
  * the DRIVEWAY starts at the walk's back edge, flush with the walk, and
    runs to the garage slab;
  * the LAWN's front edge follows the walk's back edge, curves and all.

Curves (a cul-de-sac bulb, the fillet that joins it to the street) are
just more path: the strips follow it with no gaps between pieces.

Every mesh is built here with its faces wound outward (no centroid
guesses), in pieces short enough that the audits' bounding boxes stay
tight on curves.
"""
import math

from .geometry import _finalize_mesh, make_box, make_wedge

CURB_COL = (0.56, 0.56, 0.54, 1.0)
WALK_COL = (0.62, 0.62, 0.60, 1.0)

CURB_W = 0.20
CURB_TOP = 0.09
WALK_W = 1.30
WALK_TOP = 0.07
LIP = 0.02          # the curb's height across a driveway mouth
RAMP = 0.80         # how far into the walk the apron's slope runs
WING = 0.60         # the curb's transition down to the lip, each side
FLARE = 0.30        # the mouth runs this much past the drive each side


# ── paths ─────────────────────────────────────────────────────────────

def line_path(p0, p1, step=12.0):
    d = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    n = max(1, int(math.ceil(d / step)))
    return [(p0[0] + (p1[0] - p0[0]) * i / n, p0[1] + (p1[1] - p0[1]) * i / n) for i in range(n + 1)]


def arc_path(c, r, a0_deg, a1_deg, step_deg=3.0):
    span = a1_deg - a0_deg
    n = max(1, int(math.ceil(abs(span) / step_deg)))
    out = []
    for i in range(n + 1):
        a = math.radians(a0_deg + span * i / n)
        out.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
    return out


def join_paths(*parts):
    out = []
    for part in parts:
        for p in part:
            if out and math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) < 1e-6:
                continue
            out.append((float(p[0]), float(p[1])))
    return out


def _orient(face, verts, want):
    """Wind `face` so its (Newell) normal points along `want`."""
    nx = ny = nz = 0.0
    m = len(face)
    for k in range(m):
        a = verts[face[k]]
        b = verts[face[(k + 1) % m]]
        nx += (a[1] - b[1]) * (a[2] + b[2])
        ny += (a[2] - b[2]) * (a[0] + b[0])
        nz += (a[0] - b[0]) * (a[1] + b[1])
    return list(face) if nx * want[0] + ny * want[1] + nz * want[2] >= 0.0 else list(reversed(face))


class EdgePath:
    """A street edge: the curb face's line in plan, walked with the
    asphalt on one side. `out_right` — the outward side (curb, walk,
    lawn) is on the right of the direction of travel (a path walked
    counter-clockwise round the asphalt)."""

    def __init__(self, pts, out_right=True):
        self.pts = [(float(x), float(y)) for x, y in pts]
        self.out_right = out_right
        self.s = [0.0]
        for i in range(1, len(self.pts)):
            a, b = self.pts[i - 1], self.pts[i]
            self.s.append(self.s[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))

    @property
    def length(self):
        return self.s[-1]

    def _seg_normal(self, a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        return (dy / L, -dx / L) if self.out_right else (-dy / L, dx / L)

    def normals(self, pts=None):
        pts = self.pts if pts is None else pts
        ns = []
        for i in range(len(pts)):
            ax = ay = 0.0
            if i > 0:
                n = self._seg_normal(pts[i - 1], pts[i])
                ax += n[0]; ay += n[1]
            if i < len(pts) - 1:
                n = self._seg_normal(pts[i], pts[i + 1])
                ax += n[0]; ay += n[1]
            L = math.hypot(ax, ay) or 1.0
            ns.append((ax / L, ay / L))
        return ns

    def offset(self, d, pts=None):
        pts = self.pts if pts is None else pts
        return [(p[0] + n[0] * d, p[1] + n[1] * d) for p, n in zip(pts, self.normals(pts))]

    def point_at(self, s):
        s = max(0.0, min(self.length, s))
        for i in range(1, len(self.pts)):
            if self.s[i] >= s - 1e-9:
                a, b = self.pts[i - 1], self.pts[i]
                seg = self.s[i] - self.s[i - 1]
                t = 0.0 if seg <= 0.0 else (s - self.s[i - 1]) / seg
                return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        return self.pts[-1]

    @staticmethod
    def _crossings(poly, x):
        out = []
        for i in range(1, len(poly)):
            a, b = poly[i - 1], poly[i]
            if (a[0] - x) * (b[0] - x) <= 0.0 and a[0] != b[0]:
                t = (x - a[0]) / (b[0] - a[0])
                out.append((i, t, a[1] + (b[1] - a[1]) * t))
        return out

    def s_at_x(self, x, near_y):
        """Where the curb face crosses the line x = const (the crossing
        nearest near_y)."""
        best = None
        for i, t, y in self._crossings(self.pts, x):
            s = self.s[i - 1] + (self.s[i] - self.s[i - 1]) * t
            if best is None or abs(y - near_y) < abs(best[1] - near_y):
                best = (s, y)
        return None if best is None else best[0]

    def y_at_x(self, x, d, near_y):
        """The y of the line `d` behind the curb face (CURB_W + WALK_W =
        the walk's back edge) at x."""
        best = None
        for i, t, y in self._crossings(self.offset(d), x):
            if best is None or abs(y - near_y) < abs(best - near_y):
                best = y
        return best

    def mouth(self, x0, x1, near_y):
        """The s-range of a driveway mouth between x0 and x1 (the drive's
        sides), flared FLARE each way."""
        sa = self.s_at_x(x0 - FLARE if x0 < x1 else x0 + FLARE, near_y)
        sb = self.s_at_x(x1 + FLARE if x0 < x1 else x1 - FLARE, near_y)
        if sa is None or sb is None:
            return None
        return (min(sa, sb), max(sa, sb))


# ── meshes ────────────────────────────────────────────────────────────

def _strip(name, pts, ns, gs, cols, base, color):
    """One closed piece of a strip along the path. cols: [(offset, top
    in the open, top in a mouth)] across the strip, inner to outer; gs:
    0..1 per sample, how far into a mouth it is."""
    nC = len(cols)
    per = nC + 2
    verts = []
    for p, n, g in zip(pts, ns, gs):
        for (o, h_open, h_mouth) in cols:
            verts.append((p[0] + n[0] * o, p[1] + n[1] * o, h_open * (1.0 - g) + h_mouth * g))
        verts.append((p[0] + n[0] * cols[0][0], p[1] + n[1] * cols[0][0], base))
        verts.append((p[0] + n[0] * cols[-1][0], p[1] + n[1] * cols[-1][0], base))
    T = lambda i, j: i * per + j
    BI = lambda i: i * per + nC
    BO = lambda i: i * per + nC + 1
    faces = []
    for i in range(len(pts) - 1):
        n = ns[i]
        for j in range(nC - 1):
            faces.append(_orient([T(i, j), T(i + 1, j), T(i + 1, j + 1), T(i, j + 1)], verts, (0.0, 0.0, 1.0)))
        faces.append(_orient([BI(i), BI(i + 1), T(i + 1, 0), T(i, 0)], verts, (-n[0], -n[1], 0.0)))
        faces.append(_orient([BO(i), BO(i + 1), T(i + 1, nC - 1), T(i, nC - 1)], verts, (n[0], n[1], 0.0)))
        faces.append(_orient([BI(i), BI(i + 1), BO(i + 1), BO(i)], verts, (0.0, 0.0, -1.0)))
    last = len(pts) - 1
    for i, j, sgn in ((0, 1, -1.0), (last, last - 1, -1.0)):
        t = (pts[j][0] - pts[i][0], pts[j][1] - pts[i][1])     # toward the piece's interior
        cap = [BI(i)] + [T(i, k) for k in range(nC)] + [BO(i)]
        faces.append(_orient(cap, verts, (sgn * t[0], sgn * t[1], 0.0)))
    return _finalize_mesh(name, verts, faces, color)


def make_street_edge(prefix, path, mouths=(), *, curb_w=CURB_W, curb_top=CURB_TOP, walk_w=WALK_W,
                     walk_top=WALK_TOP, lip=LIP, ramp=RAMP, wing=WING, base=-0.02,
                     curb_col=CURB_COL, walk_col=WALK_COL, chunk=12.0, turn=18.0):
    """The curb and the walk along `path` (an EdgePath), with a curb cut
    at each s-range in `mouths`. Emits <prefix>_Curb_<k> and
    <prefix>_Walk_<k> pieces, broken at every mouth and wing edge, every
    `chunk` metres of straight and every `turn` degrees of curve."""
    mouths = [m for m in mouths if m]
    L = path.length
    cuts = set()
    for s0, s1 in mouths:
        for v in (s0 - wing, s0, s1, s1 + wing):
            if 0.0 < v < L:
                cuts.add(round(v, 6))
    S = sorted(set([round(v, 6) for v in path.s] + list(cuts)))
    pts = [path.point_at(v) for v in S]
    ns = path.normals(pts)

    def g_at(v):
        g = 0.0
        for s0, s1 in mouths:
            if s0 - 1e-6 <= v <= s1 + 1e-6:
                return 1.0
            if s0 - wing < v < s0:
                g = max(g, (v - (s0 - wing)) / wing)
            if s1 < v < s1 + wing:
                g = max(g, ((s1 + wing) - v) / wing)
        return g
    gs = [g_at(v) for v in S]
    mid = lip + (walk_top - lip) * curb_w / ramp
    curb_cols = [(0.0, curb_top, lip), (curb_w, curb_top, mid)]
    walk_cols = [(curb_w, walk_top, mid), (ramp, walk_top, walk_top), (curb_w + walk_w, walk_top, walk_top)]
    # piece boundaries
    bounds = [0]
    run = 0.0
    bend = 0.0
    for i in range(1, len(S)):
        run += S[i] - S[i - 1]
        if 0 < i < len(S) - 1:
            a = math.degrees(math.atan2(ns[i][1], ns[i][0]) - math.atan2(ns[i - 1][1], ns[i - 1][0]))
            bend += abs((a + 180.0) % 360.0 - 180.0)
        if i == len(S) - 1 or S[i] in cuts or run >= chunk or bend >= turn:
            bounds.append(i)
            run = 0.0
            bend = 0.0
    for k in range(len(bounds) - 1):
        i0, i1 = bounds[k], bounds[k + 1]
        sl = slice(i0, i1 + 1)
        _strip(f"{prefix}_Curb_{k}", pts[sl], ns[sl], gs[sl], curb_cols, base, curb_col)
        _strip(f"{prefix}_Walk_{k}", pts[sl], ns[sl], gs[sl], walk_cols, base, walk_col)
    return curb_w + walk_w


def make_slab_between(name, front, back, top, base, color, top_back=None):
    """A slab whose plan runs between two polylines of equal length
    (front[i] faces back[i]): a driveway from the walk's back edge to the
    garage, a lawn from the walk to the house."""
    tb = top if top_back is None else top_back
    n = len(front)
    verts = []
    for i in range(n):
        verts += [(front[i][0], front[i][1], top), (back[i][0], back[i][1], tb),
                  (front[i][0], front[i][1], base), (back[i][0], back[i][1], base)]
    TF = lambda i: 4 * i
    TB = lambda i: 4 * i + 1
    BF = lambda i: 4 * i + 2
    BB = lambda i: 4 * i + 3
    faces = []
    for i in range(n - 1):
        d = (front[i][0] - back[i][0], front[i][1] - back[i][1])
        faces.append(_orient([TF(i), TF(i + 1), TB(i + 1), TB(i)], verts, (0.0, 0.0, 1.0)))
        faces.append(_orient([BF(i), BF(i + 1), BB(i + 1), BB(i)], verts, (0.0, 0.0, -1.0)))
        faces.append(_orient([BF(i), BF(i + 1), TF(i + 1), TF(i)], verts, (d[0], d[1], 0.0)))
        faces.append(_orient([BB(i), BB(i + 1), TB(i + 1), TB(i)], verts, (-d[0], -d[1], 0.0)))
    s0 = (front[1][0] - front[0][0], front[1][1] - front[0][1])
    s1 = (front[-1][0] - front[-2][0], front[-1][1] - front[-2][1])
    faces.append(_orient([BF(0), TF(0), TB(0), BB(0)], verts, (-s0[0], -s0[1], 0.0)))
    faces.append(_orient([BF(n - 1), TF(n - 1), TB(n - 1), BB(n - 1)], verts, (s1[0], s1[1], 0.0)))
    return _finalize_mesh(name, verts, faces, color)


def make_flat_polygon(name, poly, top, base, color):
    """A slab with any plan (counter-clockwise or not; concave is fine):
    a cul-de-sac's asphalt, a lot pad."""
    pts = [(float(x), float(y)) for x, y in poly]
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    if area < 0.0:
        pts.reverse()
    n = len(pts)
    verts = [(x, y, top) for x, y in pts] + [(x, y, base) for x, y in pts]
    faces = [_orient(list(range(n)), verts, (0.0, 0.0, 1.0)),
             _orient(list(range(n, 2 * n)), verts, (0.0, 0.0, -1.0))]
    for i in range(n):
        j = (i + 1) % n
        dx, dy = pts[j][0] - pts[i][0], pts[j][1] - pts[i][1]
        faces.append(_orient([i, j, n + j, n + i], verts, (dy, -dx, 0.0)))   # CCW: outward is right
    return _finalize_mesh(name, verts, faces, color)


def drive_lines(path, x0, x1, back_y, near_y, n=9, d=CURB_W + WALK_W):
    """The front (the walk's back edge) and back (the garage slab) lines
    of a driveway running across the street edge between x0 and x1."""
    front, back = [], []
    for k in range(n):
        x = x0 + (x1 - x0) * k / (n - 1)
        y = path.y_at_x(x, d, near_y)
        front.append((x, y))
        back.append((x, back_y))
    return front, back


# ── straight box curbs (the sets that lay a curb as one long box) ─────

def cut_pieces(a0, a1, gaps, wing=WING):
    """Split a straight curb run [a0, a1] at curb cuts. gaps: [(g0, g1)]
    along the run (the mouth, flare included). Returns [(kind, s, e)]:
    'full' the curb at height; 'down' it falls toward +a into a cut;
    'up' it climbs back out of one; 'lip' across the mouth."""
    marks = []
    for g0, g1 in sorted(gaps):
        g0, g1 = max(a0, g0), min(a1, g1)
        if g1 <= g0:
            continue
        marks.append((g0 - wing, g0, "down"))
        marks.append((g0, g1, "lip"))
        marks.append((g1, g1 + wing, "up"))
    out = []
    cur = a0
    for s, e, kind in marks:
        s, e = max(s, a0), min(e, a1)
        if e <= s:
            continue
        if s > cur + 1e-6:
            out.append(("full", cur, s))
        s = max(s, cur)
        if e > s + 1e-6:
            out.append((kind, s, e))
        cur = max(cur, e)
    if a1 > cur + 1e-6:
        out.append(("full", cur, a1))
    return out


def make_cut_curb(name, a0, a1, b0, b1, z0, top, gaps, *, axis="X", lip=None, wing=WING, color=CURB_COL):
    """A straight curb box along `axis` (a0..a1 along it, b0..b1 across,
    z0..top) with a curb cut at each (g0, g1) of `gaps`: over the mouth it
    is a lip 2 cm above its base, and it ramps down to it over `wing`
    either side. Pieces: <name>, <name>_<k> (the old single box's name is
    kept by the first full piece)."""
    lip = (z0 + LIP + 0.005) if lip is None else lip
    pieces = cut_pieces(a0, a1, gaps, wing)

    def P(a, b, z):
        return (a, b, z) if axis == "X" else (b, a, z)

    def SZ(da, db, dz):
        return (da, db, dz) if axis == "X" else (db, da, dz)
    bm, bw = (b0 + b1) / 2.0, abs(b1 - b0)
    named = False
    for k, (kind, s, e) in enumerate(pieces):
        nm = name if (kind == "full" and not named) else f"{name}_{k}"
        named = named or kind == "full"
        am, aw = (s + e) / 2.0, e - s
        if kind == "full":
            make_box(nm, P(am, bm, (z0 + top) / 2.0), SZ(aw, bw, top - z0), color)
        elif kind == "lip":
            make_box(nm, P(am, bm, (z0 + lip) / 2.0), SZ(aw, bw, lip - z0), color)
        else:
            make_box(nm + "_Base", P(am, bm, (z0 + lip) / 2.0), SZ(aw, bw, lip - z0), color)
            hi = ("-" if kind == "down" else "+") + axis      # the high end is away from the mouth
            make_wedge(nm, P(am, bm, (lip + top) / 2.0), SZ(aw, bw, top - lip), color, high_end=hi)
    return pieces


def make_v_ditch(name, x_road, x_out, y0, y1, bottom, road_z, out_z, color):
    """A bar ditch along Y between the road's shoulder edge (x_road) and
    the field (x_out): down from the road to `bottom` at its middle and
    back up to the field's level (pass 421: the ditches were one wedge,
    falling 34-40 cm to an outer edge that met nothing, so the void under
    the field showed as a black band the length of the road)."""
    xc = (x_road + x_out) / 2.0
    ym, yl = (y0 + y1) / 2.0, abs(y1 - y0)
    toward_road = "+X" if x_road > x_out else "-X"
    toward_out = "-X" if x_road > x_out else "+X"
    make_wedge(name, ((xc + x_road) / 2.0, ym, (bottom + road_z) / 2.0), (abs(x_road - xc), yl, road_z - bottom),
               color, high_end=toward_road)
    make_wedge(name + "_Out", ((xc + x_out) / 2.0, ym, (bottom + out_z) / 2.0), (abs(x_out - xc), yl, out_z - bottom),
               color, high_end=toward_out)
