## LocaleGlass — vertex alpha becomes real transparency (2026-10-02).
##
## The builders write glass with an alpha below 1 (the Houston office's
## glass wall 0.30, its partitions 0.50, the riverboat's cabinet glass,
## a water-cooler jug 0.55 …) and the GLB carries it in COLOR_0 — but
## the importer's default material is opaque, so every pane rendered as
## a painted slab: the "glass-walled office" was a box, the helm's
## leaded window a wall. This walks a freshly instanced locale and gives
## every surface whose vertex alpha is below ALPHA_MAX a duplicate of
## its material with alpha transparency on (vertex colour as albedo, so
## the alpha the builder asked for is the alpha drawn). No GLB rebuild;
## the Deck needs no Blender for this.
class_name LocaleGlass
extends RefCounted

const ALPHA_MAX := 0.98


## Returns the number of surfaces made transparent.
static func apply(root: Node) -> int:
	var n: int = 0
	var stack: Array[Node] = [root]
	while not stack.is_empty():
		var node: Node = stack.pop_back()
		for c in node.get_children():
			stack.append(c)
		var mi := node as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		var mesh: Mesh = mi.mesh
		for s in range(mesh.get_surface_count()):
			var arrays: Array = mesh.surface_get_arrays(s)
			if arrays.size() <= Mesh.ARRAY_COLOR:
				continue
			var v: Variant = arrays[Mesh.ARRAY_COLOR]
			if not (v is PackedColorArray):
				continue
			var cols: PackedColorArray = v
			if cols.is_empty() or cols[0].a > ALPHA_MAX:
				continue
			var m: StandardMaterial3D
			var sm := mi.get_active_material(s) as StandardMaterial3D
			if sm != null:
				m = sm.duplicate() as StandardMaterial3D
			else:
				m = StandardMaterial3D.new()
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			m.vertex_color_use_as_albedo = true
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
			mi.set_surface_override_material(s, m)
			n += 1
	return n
