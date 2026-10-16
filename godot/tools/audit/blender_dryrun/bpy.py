"""A minimal stand-in for Blender's bpy — enough for the _props kits, so
every builder can run its REAL kit code outside Blender and surface the
errors Blender would hit (bad kwargs, NameErrors, bad face indices)."""
import types, os

class _Any:
    """Permissive stand-in: any attribute, any call, empty iteration."""
    def __init__(self, *a, **k): pass
    def __getattr__(self, n):
        if n.startswith("__"): raise AttributeError(n)
        v = _Any(); object.__setattr__(self, n, v); return v
    def __call__(self, *a, **k): return _Any()
    def __iter__(self): return iter(())
    def __len__(self): return 0
    def __getitem__(self, k): return _Any()
    def __setitem__(self, k, v): pass
    def __bool__(self): return True
STATS = {"meshes": 0, "verts": 0, "faces": 0, "bad": []}

class _Layer:
    def __init__(self, n): self.data = [types.SimpleNamespace(color=None) for _ in range(n)]
class _VC(dict):
    def __init__(self, mesh): super().__init__(); self._m = mesh
    def new(self, name="Col"):
        self[name] = _Layer(self._m._loops); return self[name]
    def __getitem__(self, k):
        if isinstance(k, int): return list(self.values())[k]
        return dict.__getitem__(self, k)
    @property
    def active(self): return list(self.values())[0] if self else None
class _Poly:
    def __init__(self, start, n, verts=()):
        self.loop_indices = range(start, start + n); self.vertices = tuple(verts); self.material_index = 0
class Mesh(_Any):
    def __init__(self, name):
        object.__setattr__(self, "name", name); object.__setattr__(self, "_loops", 0)
        object.__setattr__(self, "polygons", []); object.__setattr__(self, "vertex_colors", _VC(self))
        object.__setattr__(self, "materials", []); object.__setattr__(self, "users", 0)
    def from_pydata(self, verts, edges, faces):
        nv = len(verts)
        for v in verts:
            if len(v) != 3 or any(c != c for c in v):
                STATS["bad"].append((self.name, "bad vertex %r" % (v,))); break
        start = 0
        for f in faces:
            if len(f) < 3 or len(set(f)) != len(f) or any((not isinstance(i, int)) or i < 0 or i >= nv for i in f):
                STATS["bad"].append((self.name, "bad face %r (nv=%d)" % (list(f)[:6], nv))); break
            self.polygons.append(_Poly(start, len(f), f)); start += len(f)
        self._loops = start
        STATS["meshes"] += 1; STATS["verts"] += nv; STATS["faces"] += len(faces)
    def update(self, *a, **k): pass

class _Obj(_Any):
    def __init__(self, name, data=None):
        object.__setattr__(self, "name", name); object.__setattr__(self, "data", data if data is not None else Mesh(name + "_mesh"))
        object.__setattr__(self, "users", 1)

class _Coll(list):
    def new(self, name, data=None, *a, **k):
        o = Mesh(name) if (data is None and self is data_meshes) else _Obj(name, data)
        self.append(o); return o
    def get(self, name, default=None):
        for o in self:
            if getattr(o, "name", None) == name: return o
        return default
    def remove(self, o, do_unlink=True):
        if o in self: list.remove(self, o)

data_meshes = _Coll()
data = _Any()
data.meshes = data_meshes; data.objects = _Coll(); data.materials = _Coll(); data.images = _Coll()
class _Ctx(_Any):
    @property
    def active_object(self):
        return data.objects[-1] if data.objects else _Obj("none")
    @property
    def object(self):
        return self.active_object
context = _Ctx()
context.collection = _Any(); context.collection.objects = _Any()
context.collection.objects.link = lambda o: None
context.scene = _Any(); context.scene.objects = data.objects
class _Gltf:
    def __call__(self, **kw):
        fp = kw.get("filepath"); STATS["export"] = fp; STATS["export_kw"] = kw
        if fp and not os.path.exists(fp):
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            open(fp, "wb").close(); STATS["touched"] = fp
    def get_rna_type(self):
        # a NEW exporter (2026-09-24): no `export_colors`; vertex colours
        # export only via export_vertex_color='ACTIVE' (default 'MATERIAL'
        # skips material-less meshes — the 09-24 sheet's white rooms)
        _ev = types.SimpleNamespace(enum_items=[types.SimpleNamespace(identifier=i)
                                                for i in ("MATERIAL", "ACTIVE", "NONE")])
        return types.SimpleNamespace(properties={"export_normals": 1, "export_vertex_color": _ev,
                                                 "export_active_vertex_color_when_no_material": 1})
def _prim(**k):
    data.objects.append(_Obj("prim"))
ops = _Any()
ops.export_scene = _Any(); ops.export_scene.gltf = _Gltf()
ops.mesh = _Any()
for _n in ("primitive_uv_sphere_add", "primitive_cube_add", "primitive_cylinder_add", "primitive_cone_add",
           "primitive_plane_add", "primitive_ico_sphere_add", "primitive_torus_add"):
    setattr(ops.mesh, _n, _prim)
