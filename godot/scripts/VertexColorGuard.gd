# VertexColorGuard.gd
# ════════════════════════════════════════════════════════════════
# Make every locale mesh that CARRIES vertex colours actually USE them.
#
# 2026-09-24 · the white rooms. After the Deck's Blender update (glTF
# exporter v5.2.39) every rebuilt locale rendered washed toward white
# while its GLB held the correct linear COLOR_0 values (read back with
# tools/audit/glb_diag.py). The diner — whose scene runs LocaleSetup.gd,
# which puts a vertex-colour-as-albedo material on every mesh — stayed
# in colour on the same exporter. The other scenes rely on the material
# Godot's glTF importer creates for a material-less primitive, and with
# the new files that default no longer reads the colours.
#
# apply(root) walks the locale and, for each surface whose mesh has a
# COLOR array and whose material is an untextured StandardMaterial3D
# without vertex_color_use_as_albedo (or no material at all), sets a
# copy of it with the flag on. Real materials — textured, shader, or
# already vertex-coloured — are left alone. Called once from
# MoodCycler._ready (every locale scene carries a MoodCycler).
# ════════════════════════════════════════════════════════════════
class_name VertexColorGuard
extends RefCounted


static func apply(root: Node) -> int:
	var fixed: int = 0
	var cache: Dictionary = {}
	var stack: Array[Node] = [root]
	while not stack.is_empty():
		var node: Node = stack.pop_back()
		for child in node.get_children():
			stack.append(child)
		var mi: MeshInstance3D = node as MeshInstance3D
		if mi == null or mi.mesh == null or mi.material_override != null:
			continue
		var mesh: Mesh = mi.mesh
		for i in range(mesh.get_surface_count()):
			if not _has_colors(mesh, i):
				continue
			if mi.get_surface_override_material(i) != null:
				continue
			var src: Material = mesh.surface_get_material(i)
			var fix: Material = _fixed_material(src, cache)
			if fix != null:
				mi.set_surface_override_material(i, fix)
				fixed += 1
	return fixed


static func _has_colors(mesh: Mesh, surface: int) -> bool:
	var am: ArrayMesh = mesh as ArrayMesh
	if am == null:
		return false
	return (am.surface_get_format(surface) & Mesh.ARRAY_FORMAT_COLOR) != 0


static func _fixed_material(src: Material, cache: Dictionary) -> Material:
	var key: int = src.get_instance_id() if src != null else 0
	if cache.has(key):
		var hit: Material = cache[key]
		return hit
	var out: StandardMaterial3D = null
	if src == null:
		out = StandardMaterial3D.new()
		out.vertex_color_use_as_albedo = true
	else:
		var sm: StandardMaterial3D = src as StandardMaterial3D
		if sm != null and not sm.vertex_color_use_as_albedo and sm.albedo_texture == null:
			out = sm.duplicate() as StandardMaterial3D
			out.vertex_color_use_as_albedo = true
	cache[key] = out
	return out
