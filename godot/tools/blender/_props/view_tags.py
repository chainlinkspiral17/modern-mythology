"""view_tags.py — which VIEWS a part is in, for the builders (pass 375).

A set serves several views (Background3D.CAMERA_PRESETS), and a part can be
in some of them only. Its name says so: `<Name>__<view>`, or
`<Name>__<group>` where the group stands for a list of views
(Background3D.VIEW_GROUPS — a part of three views overran Blender's
63-character names). A builder gives each view one letter and each part the
letters of the views it is in:

    V = Views("fx", {"k": "foxhole_check", "s": "foxhole_show", "t": "foxhole_after"})
    make_box("Rail_Flyer" + V.tag("st"), ...)            # __fx_st
    with V.tagged("s", FIG):                             # every part FIG makes: __foxhole_show
        FIG.make_standing_figure("Fx_Kid", ...)
    V.check()                                            # at the end of the function

check() fails the build when a group it used is not in the engine's table:
a tag that names nothing is not a tag, and the part would be in EVERY view
of the set. The gates read the same table (tools/audit/view_tags.py).
"""
import os


class Views:
    def __init__(self, prefix, views):
        self.prefix, self.views, self.used = prefix, dict(views), set()

    def _norm(self, m):
        return "".join(ch for ch in self.views if ch in m)

    def tag(self, m):
        m = self._norm(m)
        assert m, "no view letters in %r" % (m,)
        self.used.add(m)
        return "__" + (self.views[m] if len(m) == 1 else "%s_%s" % (self.prefix, m))

    def tagged(self, m, *mods):
        """Within the block, every part the given _props modules make takes
        the tag of the views `m` names."""
        tag = self.tag(m)

        class _Ctx:
            def __enter__(ctx):
                ctx.saved = []
                for mod in mods:
                    for n in dir(mod):
                        fn = getattr(mod, n)
                        if n.startswith("make_") and callable(fn) and getattr(fn, "__module__", None) != mod.__name__:
                            ctx.saved.append((mod, n, fn))
                            setattr(mod, n, (lambda f: (lambda name, *a, **k: f(str(name) + tag, *a, **k)))(fn))
                return ctx

            def __exit__(ctx, *exc):
                for mod, n, fn in ctx.saved:
                    setattr(mod, n, fn)
                return False
        return _Ctx()

    def check(self):
        gd = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..",
                                           "scripts", "vn", "Background3D.gd"))
        src = open(gd, encoding="utf-8").read()
        for m in sorted(self.used):
            if len(m) > 1:
                want = '"%s_%s": [%s]' % (self.prefix, m, ", ".join('"%s"' % self.views[ch] for ch in m))
                assert want in src, "Background3D.VIEW_GROUPS lacks %s" % want
