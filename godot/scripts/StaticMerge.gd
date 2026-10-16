# StaticMerge.gd
# ════════════════════════════════════════════════════════════════
# STATIC MERGE (2026-10-16 · perf draft 2): a locale's still parts drawn
# as a few chunks instead of thousands of objects.
#
# The user: "do a quick assessment how well game is handling graphical
# load … how much it can be optimized/expanded with new content", then
# "Go ahead". tools/PerfProbe.gd found every builder exports each part as
# its own mesh and the Compatibility renderer draws each one separately,
# again for every shadow pass: graustark 14,316 draw calls, pharmacy
# 12,464, the fueling station 12,302 — against a comfort line of ~2,000.
#
# attach(locale_root) — called once from MoodCycler._ready (every locale
# scene carries one, walkable and VN background alike) — adds this node,
# which two frames later (after HeroArt / HeroProp / the setup scripts have
# hidden their stand-ins) groups the eligible MeshInstance3Ds by
# (material, vertex format, shadow mode, 4 m cell) and builds each group
# of two or more into one mesh, a few groups a frame. NOTHING IS REMOVED:
# the originals keep their nodes, names, colliders and transforms; only
# their render instances are switched off (RenderingServer), so every
# script that finds a part by name still finds it. If anything later hides
# or frees a merged part, its chunk splits back into the originals.
#
# Left alone: anything under a node with a script (players, staged cast,
# HeroProp, gauntlet hosts) except the static setup scripts, anything an
# AnimationPlayer animates, transparent or shader materials, skinned /
# blend-shape meshes, visibility ranges, HeroProp hide_prefixes and the
# KEEP_PREFIXES runtime scripts look up, and any node in group "no_merge".
# A chunk never takes more lamps than the renderer lights per object
# (rendering/limits/opengl/max_lights_per_object, 8): a crowded cell
# splits to 2 m, then 1 m, and past that its parts stay separate.
#
# shadow_budget(): each shadowed sun drops from four splits to two, within
# 60 m (it runs at once, in attach, so no shadow pops in late).
#
# MM_STATIC_MERGE=0 in the environment turns both off; MM_MERGE=0 or
# MM_SHADOW_BUDGET=0 just the one (A/B in PerfProbe).
# Draft 3: merge at IMPORT (post-import script) so load does no work, and
# give chunks generated LODs for the big exteriors.
# ════════════════════════════════════════════════════════════════
extends Node3D

const CELL := 4.0           # a room's cells; a big exterior grows them (_cell_for)
const CELL_MAX := 12.0
const MIN_CELL := 1.0
const FRAME_BUDGET_USEC := 6000
const SUN_SHADOW_MAX_M := 60.0
const KEEP_PREFIXES: Array[String] = ["Sprinkler_Head", "Miller_Cracked", "HeroArt_"]
const SETUP_SCRIPTS: Array[String] = ["LocaleSetup.gd", "CathedralSetup.gd"]
const FORMAT_MASK: int = Mesh.ARRAY_FORMAT_NORMAL | Mesh.ARRAY_FORMAT_TANGENT \
		| Mesh.ARRAY_FORMAT_COLOR | Mesh.ARRAY_FORMAT_TEX_UV | Mesh.ARRAY_FORMAT_TEX_UV2

static var last_report: Dictionary = {}

var _root: Node3D = null
var _wait: int = 2
var _pending: Array = []          # groups still to build: Array of Array[Dictionary]
var _chunks: Array = []           # {mesh_node, members: Array[MeshInstance3D]}
var _lights: Array = []           # [{pos, r}] omni / spot in root space
var _light_cap: int = 8
var _shadow_mask: int = 0         # the lamps (not suns) that cast shadows
var _report: Dictionary = {}
var _t_build: int = 0


static func attach(locale_root: Node) -> void:
	var r: Node3D = locale_root as Node3D
	if r == null or OS.get_environment("MM_STATIC_MERGE") == "0":
		return
	for c in r.get_children():
		if c.name == "StaticMerge":
			return
	if OS.get_environment("MM_SHADOW_BUDGET") != "0":
		shadow_budget(r)
	if OS.get_environment("MM_MERGE") == "0":
		return
	var n := Node3D.new()
	n.set_script(load("res://scripts/StaticMerge.gd"))
	n.name = "StaticMerge"
	r.add_child.call_deferred(n)


## SHADOW BUDGET: a sun's shadow is drawn once per split. Godot's default
## is four splits out to 100 m — four extra passes over the whole room for a
## window's light. Two splits within 60 m keep the near shadows (sharper:
## each split gets more of the atlas). Runs at once, so nothing pops.
## Returns how many lights it trimmed.
static func shadow_budget(root: Node) -> int:
	var n: int = 0
	for l in root.find_children("*", "DirectionalLight3D", true, false):
		var d: DirectionalLight3D = l as DirectionalLight3D
		if not d.shadow_enabled:
			continue
		if d.directional_shadow_mode == DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS:
			d.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_2_SPLITS
			n += 1
		if d.directional_shadow_max_distance > SUN_SHADOW_MAX_M:
			d.directional_shadow_max_distance = SUN_SHADOW_MAX_M
	return n


func _ready() -> void:
	_root = get_parent() as Node3D
	transform = Transform3D.IDENTITY


func _process(_dt: float) -> void:
	if _root == null:
		set_process(false)
		return
	if _wait > 0:
		_wait -= 1
		if _wait == 0:
			_plan()
		return
	var t0: int = Time.get_ticks_usec()
	while not _pending.is_empty() and Time.get_ticks_usec() - t0 < FRAME_BUDGET_USEC:
		var g: Array = _pending.pop_back()
		_build(g)
	_t_build += Time.get_ticks_usec() - t0
	if _pending.is_empty():
		set_process(false)
		_report["chunks"] = _chunks.size()
		_report["build_ms"] = _t_build / 1000
		last_report = _report
		print("[StaticMerge] %s: %d parts → %d chunks (%d left separate) in %d ms" % [
			_root.name, int(_report.get("merged", 0)), _chunks.size(),
			int(_report.get("separate", 0)), _t_build / 1000])


# ── planning ─────────────────────────────────────────────────────

func _plan() -> void:
	var t0: int = Time.get_ticks_usec()
	_light_cap = int(ProjectSettings.get_setting("rendering/limits/opengl/max_lights_per_object", 8))
	var inv: Transform3D = _root.global_transform.affine_inverse()
	var keep: Array[String] = KEEP_PREFIXES.duplicate()
	var animated: Dictionary = {}
	_scan_rules(_root, keep, animated)
	var cands: Array = []
	var separate: int = 0
	var stack: Array[Node] = [_root]
	while not stack.is_empty():
		var node: Node = stack.pop_back()
		if node != _root and _blocks_subtree(node, animated):
			continue
		for c in node.get_children():
			if c != self:
				stack.append(c)
		var mi: MeshInstance3D = node as MeshInstance3D
		if mi == null:
			continue
		var info: Dictionary = _candidate(mi, keep, inv)
		if info.is_empty():
			separate += 1
		else:
			cands.append(info)
	for l in _root.find_children("*", "Light3D", true, false):
		if l is OmniLight3D or l is SpotLight3D:
			_add_light(l as Light3D, inv)
	# A lamp that casts shadows changes the picture once anything merges, in
	# the Compatibility renderer (2026-10-16: Faust's dark foreground shelf
	# went; pixel-identical with the lamps' shadows off, and still wrong
	# with only the parts those lamps reach left out). A scene with such a
	# lamp keeps every part separate — only Faust's apartment, so far.
	# Suns are fine. Draft 3: find the cause.
	if _shadow_mask != 0:
		separate += cands.size()
		cands = []
	var cell: float = _cell_for(cands)
	var groups: Dictionary = {}
	for info: Dictionary in cands:
		var k: String = "%s|%s" % [String(info["key"]), _cell_key(info["center"], cell)]
		if not groups.has(k):
			groups[k] = []
		(groups[k] as Array).append(info)
	for k: String in groups:
		separate += _split_for_lights(groups[k] as Array, cell)
	_report = {"cell_m": cell, "candidates": cands.size(), "separate": separate, "merged": 0,
			"plan_ms": (Time.get_ticks_usec() - t0) / 1000}


## 4 m cells suit a room; a town (graustark, the riverfront) at 4 m is
## still thousands of chunks. The cell grows with the set's footprint —
## a sixteenth of its longer side, 4 to 12 m — and culling stays useful.
func _cell_for(cands: Array) -> float:
	if cands.is_empty():
		return CELL
	var first: Dictionary = cands[0]
	var box: AABB = first["aabb"]
	for info: Dictionary in cands:
		var b: AABB = info["aabb"]
		box = box.merge(b)
	return clampf(maxf(box.size.x, box.size.z) / 16.0, CELL, CELL_MAX)


func _scan_rules(root: Node, keep: Array[String], animated: Dictionary) -> void:
	for n in root.find_children("*", "", true, false):
		var hp: Variant = n.get("hide_prefixes")
		if typeof(hp) == TYPE_ARRAY or typeof(hp) == TYPE_PACKED_STRING_ARRAY:
			for p: Variant in hp:
				if String(p) != "":
					keep.append(String(p))
		var ap: AnimationPlayer = n as AnimationPlayer
		if ap == null:
			continue
		var base: Node = ap.get_node_or_null(ap.root_node)
		if base == null:
			continue
		for lib_name: StringName in ap.get_animation_library_list():
			var lib: AnimationLibrary = ap.get_animation_library(lib_name)
			for an: StringName in lib.get_animation_list():
				var anim: Animation = lib.get_animation(an)
				for t in anim.get_track_count():
					var path: NodePath = anim.track_get_path(t)
					var target: Node = base.get_node_or_null(NodePath(String(path.get_concatenated_names())))
					if target != null:
						animated[target.get_instance_id()] = true


func _blocks_subtree(node: Node, animated: Dictionary) -> bool:
	if node is Viewport or node is CanvasLayer or node.is_in_group("no_merge"):
		return true
	if animated.has(node.get_instance_id()):
		return true
	var s: Script = node.get_script() as Script
	if s != null and not (s.resource_path.get_file() in SETUP_SCRIPTS):
		return true
	return false


func _candidate(mi: MeshInstance3D, keep: Array[String], inv: Transform3D) -> Dictionary:
	var am: ArrayMesh = mi.mesh as ArrayMesh
	if am == null or not mi.is_visible_in_tree() or am.get_surface_count() == 0:
		return {}
	if mi.skin != null or am.get_blend_shape_count() > 0 or mi.transparency > 0.0:
		return {}
	if mi.visibility_range_end > 0.0 or mi.visibility_range_begin > 0.0:
		return {}
	var nm: String = String(mi.name)
	for p: String in keep:
		if nm.begins_with(p):
			return {}
	var mats: Array = []
	var fmt: int = -1
	for s in am.get_surface_count():
		if am.surface_get_primitive_type(s) != Mesh.PRIMITIVE_TRIANGLES:
			return {}
		var f: int = am.surface_get_format(s) & FORMAT_MASK
		if fmt == -1:
			fmt = f
		elif f != fmt:
			return {}
		var m: Material = mi.material_override
		if m == null:
			m = mi.get_surface_override_material(s)
		if m == null:
			m = am.surface_get_material(s)
		if m != null and not _opaque(m):
			return {}
		mats.append(m)
	# one material for the whole part (the builders' parts have one surface)
	var mat: Material = mats[0]
	for m: Variant in mats:
		if m != mat:
			return {}
	var xf: Transform3D = inv * mi.global_transform
	if xf.basis.determinant() <= 0.0:
		return {}                # mirrored: its triangles would wind backwards
	var center: Vector3 = xf * am.get_aabb().get_center()
	var mid: String = _mat_key(mat)
	return {"mi": mi, "xf": xf, "center": center, "mat": mat,
			"aabb": xf * am.get_aabb(),
			"key": "%s|%d|%d|%d" % [mid, fmt, int(mi.cast_shadow), mi.layers]}


## Parts group by what their material LOOKS like: the glTF importer gives
## every material-less primitive its own default material (and
## VertexColorGuard its own vertex-colour copy), so graustark's 14,303
## parts carried 14,303 identical materials and nothing could merge. An
## untextured StandardMaterial3D keys on its visible settings; anything
## textured keys on the material itself. (Nothing edits a part's material
## after load — LocaleGlass runs before; checked 2026-10-16.)
func _mat_key(m: Material) -> String:
	if m == null:
		return "none"
	var sm: StandardMaterial3D = m as StandardMaterial3D
	if sm == null:
		return "id%d" % m.get_instance_id()
	if sm.albedo_texture != null or sm.normal_texture != null or sm.emission_texture != null \
			or sm.roughness_texture != null or sm.metallic_texture != null:
		return "id%d" % m.get_instance_id()
	return "%s|%s%s|%.3f|%.3f|%.3f|%s|%s|%.3f|%d|%d|%d|%d|%s%s%s%s" % [
		sm.albedo_color.to_html(), sm.vertex_color_use_as_albedo, sm.vertex_color_is_srgb,
		sm.roughness, sm.metallic, sm.metallic_specular,
		sm.emission_enabled, sm.emission.to_html(), sm.emission_energy_multiplier,
		sm.cull_mode, sm.shading_mode, sm.diffuse_mode, sm.specular_mode,
		sm.rim_enabled, sm.clearcoat_enabled, sm.no_depth_test, sm.disable_receive_shadows]


func _opaque(m: Material) -> bool:
	var bm: BaseMaterial3D = m as BaseMaterial3D
	if bm == null:
		return false             # a ShaderMaterial may use VERTEX / ALPHA: leave it
	if bm.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED:
		return false
	if bm.normal_enabled or bm.normal_texture != null:
		return false             # the merged mesh carries no tangents
	if bm.billboard_mode != BaseMaterial3D.BILLBOARD_DISABLED:
		return false
	return bm.next_pass == null


func _cell_key(p: Vector3, cell: float) -> String:
	return "%d,%d,%d" % [floori(p.x / cell), floori(p.y / cell), floori(p.z / cell)]


func _add_light(l: Light3D, inv: Transform3D) -> void:
	# hidden lamps count too: a mood or the night may switch one on later
	var r: float = 0.0
	if l is OmniLight3D:
		r = (l as OmniLight3D).omni_range
	elif l is SpotLight3D:
		r = (l as SpotLight3D).spot_range
	if l.shadow_enabled:
		_shadow_mask |= 1 << _lights.size()
	_lights.append({"pos": inv * l.global_position, "r": r})


## The lamps whose range reaches `box`, as a bit mask (lamp i → bit i).
func _lights_touching(box: AABB) -> int:
	var mask: int = 0
	for i in _lights.size():
		var e: Dictionary = _lights[i]
		var p: Vector3 = e["pos"]
		var r: float = float(e["r"])
		var q: Vector3 = p.clamp(box.position, box.end)
		if q.distance_squared_to(p) <= r * r:
			mask |= 1 << i
	return mask


static func _bits(mask: int) -> int:
	var n: int = 0
	var m: int = mask
	while m != 0:
		m &= m - 1
		n += 1
	return n


func _box(g: Array) -> AABB:
	var first: Dictionary = g[0]
	var box: AABB = first["aabb"]
	for info: Dictionary in g:
		var b: AABB = info["aabb"]
		box = box.merge(b)
	return box


## Queue the group for building. The renderer lights each object with at
## most _light_cap lamps, so a chunk is safe only when no more lamps than
## that reach it: past the cap the renderer picks a subset PER OBJECT, and
## a chunk's pick differs from its parts' (2026-10-16: the diner's counter
## came out brighter when chunks reached by the same 12 lamps merged).
## Otherwise the cell splits in half, down to MIN_CELL. Returns how many
## parts stay separate.
func _split_for_lights(g: Array, cell: float) -> int:
	if g.size() < 2:
		return g.size()
	if _lights.size() > 62:
		return g.size()              # past a mask's width: stay conservative
	var reach: int = _lights_touching(_box(g))
	if _bits(reach) <= _light_cap:
		_pending.append(g)
		return 0
	var left: int = 0
	var rest: Array = g
	var half: float = cell * 0.5
	if half < MIN_CELL or rest.size() < 2:
		return rest.size()
	var sub: Dictionary = {}
	for info: Dictionary in rest:
		var ck: String = _cell_key(info["center"], half)
		if not sub.has(ck):
			sub[ck] = []
		(sub[ck] as Array).append(info)
	for ck: String in sub:
		left += _split_for_lights(sub[ck] as Array, half)
	return left


# ── building + splitting back ─────────────────────────────────────

func _build(g: Array) -> void:
	var live: Array = []
	for info: Dictionary in g:
		var mi: MeshInstance3D = info["mi"]
		if is_instance_valid(mi) and mi.is_visible_in_tree():
			live.append(info)
	if live.size() < 2:
		_report["separate"] = int(_report.get("separate", 0)) + live.size()
		return
	# SurfaceTool.append_from places the vertices and offsets the indices (in
	# C++, fast) but turns NORMALS by the plain basis — wrong for a part both
	# scaled and rotated (2026-10-16: Faust's bookshelf lit as if it faced
	# elsewhere). So the normals are redone here with the inverse transpose,
	# a whole part at a time (Transform3D * PackedVector3Array is native),
	# and the tangents are dropped (only untextured materials merge).
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var members: Array[MeshInstance3D] = []
	var normals := PackedVector3Array()
	var n_verts: int = 0
	for info: Dictionary in live:
		var mi: MeshInstance3D = info["mi"]
		var xf: Transform3D = info["xf"]
		var nxf := Transform3D(xf.basis.inverse().transposed(), Vector3.ZERO)
		for s in mi.mesh.get_surface_count():
			var arr: Array = mi.mesh.surface_get_arrays(s)
			var v: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
			var nv: Variant = arr[Mesh.ARRAY_NORMAL]
			if typeof(nv) == TYPE_PACKED_VECTOR3_ARRAY and (nv as PackedVector3Array).size() == v.size():
				normals.append_array(nxf * (nv as PackedVector3Array))
			n_verts += v.size()
			st.append_from(mi.mesh, s, xf)
		members.append(mi)
	var arrays: Array = st.commit_to_arrays()
	var got: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	if got.size() != n_verts:
		_report["separate"] = int(_report.get("separate", 0)) + live.size()
		return                   # SurfaceTool reordered: leave these parts alone
	if normals.size() == n_verts:
		arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_TANGENT] = null
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	if mesh.get_surface_count() == 0:
		_report["separate"] = int(_report.get("separate", 0)) + live.size()
		return
	var first: Dictionary = live[0]
	var mat: Material = first["mat"]
	if mat != null:
		mesh.surface_set_material(0, mat)
	var chunk := MeshInstance3D.new()
	chunk.name = "Chunk_%d" % _chunks.size()
	chunk.mesh = mesh
	chunk.cast_shadow = members[0].cast_shadow
	chunk.layers = members[0].layers
	add_child(chunk)
	var entry: Dictionary = {"node": chunk, "members": members}
	_chunks.append(entry)
	for mi in members:
		RenderingServer.instance_set_visible(mi.get_instance(), false)
		mi.visibility_changed.connect(_split_back.bind(entry), CONNECT_ONE_SHOT)
		mi.tree_exiting.connect(_split_back.bind(entry), CONNECT_ONE_SHOT)
	_report["merged"] = int(_report.get("merged", 0)) + members.size()


## A merged part was hidden, shown or freed by someone: give the chunk's
## parts their own render instances back and drop the chunk.
func _split_back(entry: Dictionary) -> void:
	# the other members' one-shot connections still fire later: no-ops
	if bool(entry.get("split", false)):
		return
	entry["split"] = true
	if _root == null or _root.is_queued_for_deletion() or is_queued_for_deletion():
		return                   # the whole locale is going: nothing to restore
	var chunk: Node = entry["node"]
	if is_instance_valid(chunk):
		chunk.queue_free()
	for mi: MeshInstance3D in entry["members"]:
		if not is_instance_valid(mi):
			continue
		if mi.is_inside_tree():
			RenderingServer.instance_set_visible(mi.get_instance(), mi.is_visible_in_tree())
	_report["split_back"] = int(_report.get("split_back", 0)) + 1
