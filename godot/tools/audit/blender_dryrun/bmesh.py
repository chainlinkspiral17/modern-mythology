"""A stand-in for Blender's bmesh — only what the export's winding step
(_props.geometry.turn_closed_meshes_outward) uses, so the dry run carries a
builder through that step on its real vertex lists (pass 379: it is the last
thing before the export, and an exception there leaves no GLB on the Deck)."""
import bpy


class _Face:
    def __init__(self, poly):
        self._p = poly

    def normal_flip(self):
        self._p.vertices = tuple(reversed(self._p.vertices))
        bpy.STATS["turned_faces"] = bpy.STATS.get("turned_faces", 0) + 1


class _Faces(list):
    def ensure_lookup_table(self):
        pass


class _BMesh:
    def __init__(self):
        self.faces = _Faces()

    def from_mesh(self, me):
        self.faces = _Faces(_Face(p) for p in me.polygons)

    def to_mesh(self, me):
        bpy.STATS["turned_meshes"] = bpy.STATS.get("turned_meshes", 0) + 1

    def free(self):
        pass


def new():
    return _BMesh()
