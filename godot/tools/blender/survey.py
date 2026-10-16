#!/usr/bin/env python3
"""survey.py <build_script.py> [--band lo,hi] [--find substr] [--map]
Executes a Blender locale build script with a stubbed bpy, capturing
every mesh object's AABB (Blender coords). Prints object bboxes
(--find filters by name) and/or an ASCII top-down occupancy map of
geometry intersecting the vertical band (default 0.4..2.2 = what a
standing camera sees). Map legend: # solid, . floor-level only.
Godot conversion reminder: gx=bx, gy=bz, gz=-by.
"""
import sys, types, math, os

REG = []  # (name, min3, max3)

class Mesh:
    def __init__(s, name): s.name=name; s.verts=[]; s.polygons=[]; s.loops=[]; s._vc=VCols()
    def from_pydata(s, v, e, f, **k): s.verts=list(v)
    def update(s, *a, **k): pass
    @property
    def vertex_colors(s): return s._vc
class VCols:
    def __init__(s): s.d={}
    def __bool__(s): return bool(s.d)
    def new(s, name="Col"): s.d[name]=types.SimpleNamespace(data=[]); return s.d[name]
    def __getitem__(s, k): return s.d.setdefault(k, types.SimpleNamespace(data=[]))
class Obj:
    def __init__(s, name, mesh):
        s.name=name; s.data=mesh
        s.location=(0,0,0); s.rotation_euler=(0,0,0); s.scale=(1,1,1)
OBJS=[]
class Coll:
    def __init__(s): s.objects=types.SimpleNamespace(link=s._link)
    def _link(s, obj):
        OBJS.append(obj)
        if obj.data.verts:
            xs,ys,zs = zip(*obj.data.verts)
            REG.append((obj.name,(min(xs),min(ys),min(zs)),(max(xs),max(ys),max(zs))))
class OpTree:
    def __getattr__(s, k): return s
    def __call__(s, *a, **k): return {'FINISHED'}
class DataColl(list):
    def new(s, name, *a, **k):
        m = Mesh(name); return m
    def remove(s, item): pass

bpy = types.ModuleType("bpy")
bpy.ops = OpTree()
meshes = DataColl(); mats = DataColl(); imgs = DataColl(); curves = DataColl(); fonts=DataColl()
def _obj_new(name, mesh): return Obj(name, mesh if isinstance(mesh, Mesh) else Mesh(name))
class ObjColl(list):
    def new(s, name, mesh): return _obj_new(name, mesh)
    def remove(s, item, **k):
        if item in s: list.remove(s, item)
bpy.data = types.SimpleNamespace(meshes=meshes, materials=mats, images=imgs,
    curves=curves, fonts=fonts, objects=ObjColl())
bpy.context = types.SimpleNamespace(collection=Coll(),
    scene=types.SimpleNamespace(collection=Coll(), objects=OBJS),
    view_layer=types.SimpleNamespace(objects=types.SimpleNamespace(active=None)))
mathutils = types.ModuleType("mathutils")
class Vector(tuple):
    def __new__(cls, it=(0,0,0)): return super().__new__(cls, it)
mathutils.Vector = Vector
mathutils.Euler = lambda *a, **k: (0,0,0)
sys.modules['bpy']=bpy; sys.modules['mathutils']=mathutils
sys.modules['bmesh']=types.ModuleType("bmesh")

path = sys.argv[1]
args = sys.argv[2:]
band = (0.4, 2.2)
if '--band' in args:
    lo,hi = args[args.index('--band')+1].split(','); band=(float(lo),float(hi))
src = open(path).read()
g = {'__name__':'__survey__', '__file__':os.path.abspath(path)}
# Neuter the export/main tail: most scripts call main()/export at
# module level guarded or not — run and swallow the export error.
try:
    exec(compile(src, path, 'exec'), g)
except Exception as e:
    print('(script raised %s: %s — %d objects captured before that)' % (type(e).__name__, e, len(REG)))
# Some scripts only build inside main()
if not REG and 'main' in g and callable(g['main']):
    try: g['main']()
    except Exception as e: print('(main raised %s: %s)' % (type(e).__name__, e))

print('%d objects captured' % len(REG))
if '--find' in args:
    sub = args[args.index('--find')+1].lower()
    for n,mn,mx in REG:
        if sub in n.lower():
            print('  %-34s min(%6.2f,%6.2f,%5.2f) max(%6.2f,%6.2f,%5.2f)' % (n,*mn,*mx))
if '--box' in args:
    bx0,bx1,by0,by1 = [float(v) for v in args[args.index('--box')+1].split(',')]
    hits = [(n,mn,mx) for n,mn,mx in REG
            if mx[0]>bx0 and mn[0]<bx1 and mx[1]>by0 and mn[1]<by1
            and mx[2]>band[0] and mn[2]<band[1]]
    hits.sort(key=lambda t: -((t[2][0]-t[1][0])*(t[2][1]-t[1][1])))
    for n,mn,mx in hits[:40]:
        print('  %-34s min(%6.2f,%6.2f,%5.2f) max(%6.2f,%6.2f,%5.2f)' % (n,*mn,*mx))
if '--map' in args:
    xs=[v for _,mn,mx in REG for v in (mn[0],mx[0])]; ys=[v for _,mn,mx in REG for v in (mn[1],mx[1])]
    x0,x1,y0,y1 = min(xs),max(xs),min(ys),max(ys)
    if '--crop' in args:
        x0,x1,y0,y1 = [float(v) for v in args[args.index('--crop')+1].split(',')]
    res=0.5
    W=int((x1-x0)/res)+1; H=int((y1-y0)/res)+1
    grid=[[' ']*W for _ in range(H)]
    for n,mn,mx in REG:
        solid = mx[2] > band[0] and mn[2] < band[1]
        lowonly = not solid and mx[2] <= band[0]
        ch = '#' if solid else ('.' if lowonly else None)
        if ch is None: continue
        for gy in range(max(0,int((mn[1]-y0)/res)), min(H,int((mx[1]-y0)/res)+1)):
            for gx in range(max(0,int((mn[0]-x0)/res)), min(W,int((mx[0]-x0)/res)+1)):
                if grid[gy][gx] != '#': grid[gy][gx]=ch
    # y axis printed north(+y) at top
    print('   top-down (blender coords) · x %.1f..%.1f · y %.1f..%.1f · band z %s' % (x0,x1,y0,y1,band))
    for gy in range(H-1,-1,-1):
        print('%6.1f |%s' % (y0+gy*res, ''.join(grid[gy])))
    print('        ' + ''.join('%-10s' % ('^%.0f' % (x0+i*res)) for i in range(0,W,10)))
