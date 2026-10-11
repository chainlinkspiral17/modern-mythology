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
@export var upright: bool = false          # true: the longest extent is the height
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
		if longest == 2:
			root.rotation = Vector3(-PI / 2.0, 0.0, 0.0)     # Z-up → Y-up
		elif longest == 0:
			root.rotation = Vector3(0.0, 0.0, PI / 2.0)      # X-up → Y-up
	else:
		var want: int = 2 if length_axis.to_lower() == "z" else 0
		if longest == 1:
			# Standing on end: lay it down along the wanted axis.
			root.rotation = Vector3(0.0, 0.0, -PI / 2.0) if want == 0 else Vector3(PI / 2.0, 0.0, 0.0)
		elif longest != want:
			root.rotation = Vector3(0.0, PI / 2.0, 0.0)      # swap X and Z
	# Re-measure in the new orientation, then scale and seat.
	var box: AABB = _measure(root, meshes)
	ext = box.size
	var current: float = ext.y if upright else (ext.z if length_axis.to_lower() == "z" else ext.x)
	if current < 0.001:
		current = maxf(ext.x, maxf(ext.y, ext.z))
	var s: float = size_m / current
	root.scale = Vector3(s, s, s)
	var lo: Vector3 = box.position
	var hi: Vector3 = box.position + box.size
	root.position = Vector3(-((lo.x + hi.x) * 0.5) * s, -lo.y * s, -((lo.z + hi.z) * 0.5) * s)
	print("[HeroProp] %s: ext=(%.2f, %.2f, %.2f) scale=%.3f" % [name, ext.x, ext.y, ext.z, s])


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
