"""plan.py — move a builder's furniture groups when its room grows (2026-10-09).

THE BIGGER ROOM technique (lore/_SET_DETAIL_PLAYBOOK.md, 2026-10-09):
a hand-placed room's groups were authored against its old walls. To
enlarge the room without retyping hundreds of literal coordinates, each
group is built inside

    with shifted(globals(), dx, dy, ROOM_W=old_w, ROOM_D=old_d):
        build_kitchen()

which moves every part built in the block rigidly by (dx, dy) and hands
the block the OLD room constants, so `ROOM_W/2 - 0.1` pieces land on the
new wall. It wraps the builder's own geometry names (whatever of the
known ones it imported) and the helper modules that functions import
locally — call those as `module.fn` inside a shifted block (a name bound
by `from x import fn` before the block is not wrapped).

Verify by diff: record every part before the change and after; each part
must have moved by exactly one of the planned shifts.
"""
import contextlib

_CENTER = ("make_box", "make_cyl", "make_lathe", "make_chamfer_box", "make_rot_box", "make_taper_cyl",
           "make_prism", "make_blob", "make_wall", "make_window", "make_frame_ring", "make_floor_plant",
           "make_faded_poster", "make_smoke_detector", "make_calendar", "make_soft_box")
_XY = ("make_chair", "make_table", "make_bed", "make_stool", "make_bench", "make_lamp", "make_sofa")
_PATH = ("make_tube",)


@contextlib.contextmanager
def shifted(g, dx, dy, extra=(), extra_paths=(), prefix="", dz=0.0, **consts):
    """`extra` / `extra_paths`: more of the builder's own global names to
    move, centre-first (`fn(name, (x, y[, z]), ...)`) or path-first
    (`fn(name, [(x, y), ...], ...)`) — opt-in per builder, so a name a
    builder already compensates by hand is never moved twice.
    `prefix`: prepended to every wrapped part name — for building ANOTHER
    builder's area into this set (the Cosmic back office in the shop,
    2026-10-09) without its names colliding with this set's own.
    `dz`: lifts or drops every centre-first / path part too (only those:
    the x-y helpers take their own z0) — the Altima's cab is the truck's
    cab run 14 cm lower (vehicle_cab, 2026-10-09)."""
    import _props.creatures as _C
    import _props.detail as _D

    def c3(f):
        def w(name, center, *a, **k):
            return f(prefix + name, (center[0] + dx, center[1] + dy) + tuple(c + dz for c in center[2:3]), *a, **k)
        return w

    def xy(f):
        def w(name, x, y, *a, **k):
            return f(prefix + name, x + dx, y + dy, *a, **k)
        return w

    def path(f):
        def w(name, pts, *a, **k):
            return f(prefix + name, [(q[0] + dx, q[1] + dy) + tuple(c + dz for c in q[2:3]) for q in pts], *a, **k)
        return w

    def two(f):
        def w(name, a_, b_, *a, **k):
            return f(prefix + name, (a_[0] + dx, a_[1] + dy) + tuple(c + dz for c in a_[2:3]), (b_[0] + dx, b_[1] + dy) + tuple(c + dz for c in b_[2:3]), *a, **k)
        return w

    saved_g, saved_m = {}, []
    for names, wrap in ((_CENTER + tuple(extra), c3), (_XY, xy), (_PATH + tuple(extra_paths), path)):
        for n in names:
            if n in g and n not in saved_g:     # never wrap a name twice
                saved_g[n] = g[n]
                g[n] = wrap(g[n])
    for mod, n, wrap in ((_C, "make_crow", xy), (_D, "make_traffic_wear", path), (_D, "make_floor_stain", c3),
                         (_D, "make_scuff_band", c3), (_D, "make_wall_outlet", c3), (_D, "make_light_switch", c3),
                         (_D, "make_cord_run", two)):
        if hasattr(mod, n):
            saved_m.append((mod, n, getattr(mod, n)))
            setattr(mod, n, wrap(getattr(mod, n)))
    for k, v in consts.items():
        saved_g[k] = g[k]
        g[k] = v
    try:
        yield
    finally:
        g.update(saved_g)
        for mod, n, f in saved_m:
            setattr(mod, n, f)


@contextlib.contextmanager
def zoned(regions):
    """RE-PLAN BY REGION (2026-10-21, the Deck: "Certain interiors look poorly
    arranged and cramped"). `shifted` moves one group rigidly, which needs
    the group built in its own block; a room authored over many passes has
    each zone's things spread through a dozen functions. Inside

        with zoned([(x0, y0, x1, y1, dx, dy), ...]):
            build_everything_but_the_shell()

    every part whose PLAN CENTRE falls in a region (first match wins; x0 <=
    x < x1, y0 <= y < y1) moves by that region's (dx, dy) — kit pieces and
    all, because it moves what was BUILT, not the calls: in Blender the new
    objects (by their world bounding-box centre), under the audit recorder
    the boxes recorded inside the block (so every gate measures exactly the
    room Blender exports). Build the shell (floor, walls, ceiling) outside
    the block, sized to the new room. Parts outside every region stay put."""
    def delta(cx, cy):
        for (x0, y0, x1, y1, dx, dy) in regions:
            if x0 <= cx < x1 and y0 <= cy < y1:
                return dx, dy
        return 0.0, 0.0

    import sys
    bpy = sys.modules.get("bpy")
    real = bpy is not None and getattr(bpy, "app", None) is not None
    rec = None
    if not real:
        for m in list(sys.modules.values()):
            if getattr(m, "BOXES", None) is not None and hasattr(m, "install_stubs"):
                rec = m
                break
    spheres = None
    if not real:
        for m in list(sys.modules.values()):
            if isinstance(getattr(m, "SPHERES", None), dict) and hasattr(m, "record_builder"):
                spheres = m.SPHERES
                break
    if real:
        before = set(o.name for o in bpy.data.objects)
    n0 = len(rec.BOXES) if rec else 0
    s0 = set(spheres) if spheres is not None else set()
    try:
        yield
    finally:
        if real:
            from mathutils import Vector
            for o in bpy.data.objects:
                if o.name in before or o.parent is not None:
                    continue
                cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
                dx, dy = delta(sum(c.x for c in cs) / 8.0, sum(c.y for c in cs) / 8.0)
                if dx or dy:
                    o.location.x += dx
                    o.location.y += dy
        elif rec is not None:
            moved = {}
            for i in range(n0, len(rec.BOXES)):
                n, c, h = rec.BOXES[i]
                dx, dy = delta(c[0], c[1])
                if dx or dy:
                    rec.BOXES[i] = (n, (c[0] + dx, c[1] + dy, c[2]), h)
                    moved[n] = (dx, dy)
            if spheres is not None:
                for n in set(spheres) - s0:
                    if n in moved:
                        (cc, r), (dx, dy) = spheres[n], moved[n]
                        spheres[n] = ((cc[0] + dx, cc[1] + dy, cc[2]), r)
