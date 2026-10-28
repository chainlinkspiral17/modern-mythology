extends Node3D
## HERO PROP (2026-10-11): a Meshy / Hero Studio GLB placed in a locale
## by hand, fitted at runtime the way Portrait3D fits a hero.
##
## The GLBs live on the Drive (gitignored; `meshy_pipeline.py drive-pull`
## lands them in assets/3d/props/). Their frame and scale are Meshy's,
## not ours, so a .tscn cannot place one by transform alone. This node:
##   1. loads `glb_path` if the file exists — otherwise warns and leaves
##      the procedural stand-in visible, so a clone without the Drive's
##      files renders exactly as before;
##   2. measures the merged AABB, lays the longest extent along
##      `length_axis` (a boat, a radio, a book) or stands it up when
##      `upright` (a lamp, a figurine), scales the longest extent to
##      `size_m`, centres it on this node and drops its bottom onto y 0;
##   3. mattes the materials (roughness 1, no metal) so the textured
##      model sits in the flat-lit world without a plastic sheen;
##   4. hides the stand-in: every node whose name starts with one of
##      `hide_prefixes` under `stand_in_root` (the locale's GLB instance).
## It runs DEFERRED so it lands after the scene's setup pass
## (CathedralSetup overrides every MeshInstance3D material it finds on
## _ready — a textured prop added earlier would come out flat white).
##
## Place the node at the spot the prop stands (its y = the surface it
## rests on). No ext_resource to the GLB: a missing file must never
## break the scene.

@export_file("*.glb") var glb_path: String = ""
@export var size_m: float = 0.9            # the longest extent, in metres
@export var length_axis: String = "x"      # "x" or "z": where the longest extent lies
@export var upright: bool = false          # true: size_m is the height (the model stands as built, Y up)
## (2026-10-27) the widest a standing prop may be across its footprint, metres
## (0: no cap) — a collectible with a spread cape on a 0.84 m shelf of two
@export var fit_w: float = 0.0
## (2026-10-27, the Deck: "crow seems to just be hanging out or hovering") seat
## the model on the lowest point of its CENTRAL footprint (a bird's feet), not
## its lowest point overall (the perched crow's tail hangs 15 % of its height
## below its feet, and the crow sat on its tail tip, feet in the air)
@export var seat_center: bool = false
@export var lay_down: bool = false         # true: a model standing on end is laid along length_axis (a book, a rolled rug); a Meshy model is drawn upright and never is (2026-10-27)
@export var stand_in_root: NodePath        # the locale GLB instance holding the procedural stand-in
@export var hide_prefixes: PackedStringArray = PackedStringArray()
@export var matte: bool = true

var _model: Node3D = null


func _ready() -> void:
	call_deferred("_load")


func _load() -> void:
	if glb_path == "":
		return
	if not (FileAccess.file_exists(glb_path) or ResourceLoader.exists(glb_path)):
		push_warning("[HeroProp] %s: no GLB at %s (drive-pull it); the stand-in stays" % [name, glb_path])
		return
	var ps: PackedScene = load(glb_path) as PackedScene
	if ps == null:
		push_warning("[HeroProp] %s: could not load %s" % [name, glb_path])
		return
	var inst: Node = ps.instantiate()
	var root: Node3D = inst as Node3D
	if root == null:
		root = Node3D.new()
		add_child(root)
		inst.reparent(root)
	else:
		add_child(root)
	_model = root
	_fit(root)
	if matte:
		_matte_materials(root)
	_hide_stand_in()
	add_to_group("hero_prop")


func _fit(root: Node3D) -> void:
	var meshes: Array[Node] = _collect_mesh_instances(root)
	if meshes.is_empty():
		return
	var ext: Vector3 = _measure(root, meshes).size
	var longest: int = 0
	if ext.y >= ext.x and ext.y >= ext.z:
		longest = 1
	elif ext.z >= ext.x and ext.z >= ext.y:
		longest = 2
	# Orient: the longest extent goes where the prop wants it.
	if upright:
		# (2026-10-27, the Deck: "figures still poking out through glass case")
		# every GLB is Y-up, and a figure wider than it is tall (a cape, a
		# leap, a broad base) was tipped onto its side so its WIDTH stood as
		# the height — then scaled to the shelf. Upright means as built.
		pass
	else:
		var want: int = 2 if length_axis.to_lower() == "z" else 0
		if longest == 1 and lay_down:
			# Standing on end: lay it down along the wanted axis.
			root.rotation = Vector3(0.0, 0.0, -PI / 2.0) if want == 0 else Vector3(PI / 2.0, 0.0, 0.0)
		else:
			# (2026-10-27, the Deck: "sideways crow") a Meshy model comes out
			# standing as it was drawn, Y up — a perched crow is taller than it
			# is long, and the old rule laid every such model on its side. It
			# only turns about Y now: its longest HORIZONTAL extent goes along
			# length_axis, and that length is what size_m fits.
			var horiz: int = 2 if ext.z >= ext.x else 0
			if horiz != want:
				root.rotation = Vector3(0.0, PI / 2.0, 0.0)      # swap X and Z
	# Re-measure in the new orientation, then scale and seat.
	var box: AABB = _measure(root, meshes)
	ext = box.size
	var current: float = ext.y if upright else (ext.z if length_axis.to_lower() == "z" else ext.x)
	if current < 0.001:
		current = maxf(ext.x, maxf(ext.y, ext.z))
	var s: float = size_m / current
	if fit_w > 0.0:
		var across: float = maxf(ext.x, ext.z)
		if across * s > fit_w:
			s = fit_w / across
	root.scale = Vector3(s, s, s)
	var lo: Vector3 = box.position
	var hi: Vector3 = box.position + box.size
	var floor_y: float = lo.y
	if seat_center:
		floor_y = _central_floor(meshes, box, floor_y)
	root.position = Vector3(-((lo.x + hi.x) * 0.5) * s, -floor_y * s, -((lo.z + hi.z) * 0.5) * s)
	print("[HeroProp] %s: ext=(%.2f, %.2f, %.2f) scale=%.3f" % [name, ext.x, ext.y, ext.z, s])


# The lowest vertex inside the middle half of the footprint (x and z within
# 25 % of the box's half-size of its centre), in this node's space at unit
# scale — where a bird stands. Falls back to the box's floor.
func _central_floor(meshes: Array[Node], box: AABB, fallback: float) -> float:
	var c: Vector3 = box.get_center()
	var hx: float = box.size.x * 0.25
	var hz: float = box.size.z * 0.25
	var inv: Transform3D = global_transform.affine_inverse()
	var best: float = INF
	for n: Node in meshes:
		var mi: MeshInstance3D = n as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		var xf: Transform3D = inv * mi.global_transform
		for si in mi.mesh.get_surface_count():
			var arrays: Array = mi.mesh.surface_get_arrays(si)
			var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			for v: Vector3 in verts:
				var w: Vector3 = xf * v
				if absf(w.x - c.x) <= hx and absf(w.z - c.z) <= hz and w.y < best:
					best = w.y
	return best if best < INF else fallback


# The merged AABB of the model's meshes in THIS node's space (root's
# rotation included, its scale and position not yet applied).
func _measure(_root: Node3D, meshes: Array[Node]) -> AABB:
	var lo: Vector3 = Vector3.INF
	var hi: Vector3 = -Vector3.INF
	var inv: Transform3D = global_transform.affine_inverse()
	for n: Node in meshes:
		var mi: MeshInstance3D = n as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		var local: AABB = mi.mesh.get_aabb()
		var xf: Transform3D = inv * mi.global_transform
		var world: AABB = xf * local
		lo = lo.min(world.position)
		hi = hi.max(world.position + world.size)
	if lo == Vector3.INF:
		return AABB()
	# Both measurements happen before root is scaled or moved (rotation
	# only), so this box is the model as oriented, at unit scale.
	return AABB(lo, hi - lo)


func _matte_materials(root: Node3D) -> void:
	for n: Node in _collect_mesh_instances(root):
		var mi: MeshInstance3D = n as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		for si in mi.mesh.get_surface_count():
			var src: Material = mi.get_active_material(si)
			var bm: BaseMaterial3D = src as BaseMaterial3D
			if bm == null:
				continue
			var m: BaseMaterial3D = bm.duplicate() as BaseMaterial3D
			m.roughness = 1.0
			m.metallic = 0.0
			m.metallic_specular = 0.12
			m.clearcoat_enabled = false
			mi.set_surface_override_material(si, m)


func _hide_stand_in() -> void:
	if hide_prefixes.is_empty() or stand_in_root.is_empty():
		return
	var base: Node = get_node_or_null(stand_in_root)
	if base == null:
		return
	var hidden: int = 0
	for n: Node in _collect_all(base):
		var v: Node3D = n as Node3D
		if v == null:
			continue
		for p: String in hide_prefixes:
			if v.name.begins_with(p):
				v.visible = false
				hidden += 1
				break
	print("[HeroProp] %s: hid %d stand-in node(s)" % [name, hidden])


func _collect_mesh_instances(node: Node, out: Array[Node] = []) -> Array[Node]:
	if node is MeshInstance3D:
		out.append(node)
	for child in node.get_children():
		_collect_mesh_instances(child, out)
	return out


func _collect_all(node: Node, out: Array[Node] = []) -> Array[Node]:
	for child in node.get_children():
		out.append(child)
		_collect_all(child, out)
	return out
