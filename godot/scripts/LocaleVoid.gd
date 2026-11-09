## LocaleVoid — the substrate's holes are holes (2026-11-08).
##
## Vol 7: "The patch was a hole in the wall that opened onto nothing", and
## "The patch had, at its edges, a small shimmer". The builders laid the
## patch as a box painted near-black, lit like the wall around it — it read
## as a black sticker. The user: "isn't the patch supposed to be a black
## void, maybe have a starfield shimmer to it."
##
## Every mesh named `Mural_Patch*` or `Void_*` becomes a void here, when a
## set loads (Background3D, after the glass and hero-art passes):
##   · unshaded pure black, so no light in the room ever lands on it
##   · a far starfield INSIDE it — a few dozen pin-points set behind the
##     opening's face, twinkling slowly, so the black has depth
##   · a shimmer AT ITS EDGES — a ring of short emissive dashes along the
##     opening's border, their brightness running round it
## The face that shows is the box's thinnest side toward the set's origin
## (the room the cameras stand in). Standard materials only — no per-mesh
## shader (the locale rule); the motion is a small _process on a helper.
class_name LocaleVoid
extends RefCounted

const STARS_PER_M2 := 46.0
const STAR_DEPTH := 0.6          # how far behind the opening the stars hang
const EDGE_DASH := 0.07          # length of one shimmer dash (m)


static func is_void(nm: String) -> bool:
	return nm.begins_with("Mural_Patch") or nm.begins_with("Void_")


## Returns how many voids were made.
static func apply(root: Node) -> int:
	var n: int = 0
	var stack: Array[Node] = [root]
	var found: Array[MeshInstance3D] = []
	while not stack.is_empty():
		var node: Node = stack.pop_back()
		for c in node.get_children():
			stack.append(c)
		var mi := node as MeshInstance3D
		if mi != null and mi.mesh != null and is_void(String(mi.name)):
			found.append(mi)
	for mi in found:
		_make_void(root, mi)
		n += 1
	return n


static func _black() -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.albedo_color = Color(0.0, 0.0, 0.0, 1.0)
	return m


static func _glow(col: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.vertex_color_use_as_albedo = true
	m.albedo_color = col
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	m.no_depth_test = false
	return m


static func _make_void(root: Node, mi: MeshInstance3D) -> void:
	var black: StandardMaterial3D = _black()
	for s in range(mi.mesh.get_surface_count()):
		mi.set_surface_override_material(s, black)
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	# the opening: the mesh's box in its own space, its thinnest axis the
	# normal, the face toward the set's origin the one that shows
	var aabb: AABB = mi.mesh.get_aabb()
	var sz: Vector3 = aabb.size
	var ax: int = 0
	if sz.y < sz[ax]:
		ax = 1
	if sz.z < sz[ax]:
		ax = 2
	var u_ax: int = (ax + 1) % 3
	var v_ax: int = (ax + 2) % 3
	var centre: Vector3 = aabb.get_center()
	var normal: Vector3 = Vector3.ZERO
	normal[ax] = 1.0
	# toward the room: the root's origin, in the mesh's space
	var to_origin: Vector3 = (mi.transform.affine_inverse() * _rel_inv(root, mi)) - centre
	if to_origin[ax] < 0.0:
		normal[ax] = -1.0
	var face: Vector3 = centre + normal * (sz[ax] * 0.5)
	var half_u: float = sz[u_ax] * 0.5
	var half_v: float = sz[v_ax] * 0.5
	var helper := VoidShimmer.new()
	helper.name = "VoidShimmer_%s" % String(mi.name)
	mi.add_child(helper)
	# stars: tiny quads behind the face (the black box is drawn over them
	# from outside its rim, so they read as seen THROUGH the opening)
	var area: float = sz[u_ax] * sz[v_ax]
	var count: int = clampi(int(area * STARS_PER_M2), 12, 160)
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(String(mi.name))
	var stars := MultiMesh.new()
	stars.transform_format = MultiMesh.TRANSFORM_3D
	stars.use_colors = true
	stars.instance_count = count
	var dot := QuadMesh.new()
	dot.size = Vector2(0.008, 0.008)
	stars.mesh = dot
	var basis: Basis = _face_basis(u_ax, v_ax, normal)
	for i in range(count):
		var p: Vector3 = face
		p[u_ax] += rng.randf_range(-half_u * 0.92, half_u * 0.92)
		p[v_ax] += rng.randf_range(-half_v * 0.92, half_v * 0.92)
		# just in front of the black face: unshaded black behind, the dots on it
		p += normal * 0.003
		var s: float = rng.randf_range(0.5, 1.6)
		stars.set_instance_transform(i, Transform3D(basis.scaled(Vector3(s, s, s)), p))
		stars.set_instance_color(i, Color(0.8, 0.85, 1.0, 0.0))
	var smi := MultiMeshInstance3D.new()
	smi.name = "Stars"
	smi.multimesh = stars
	smi.material_override = _glow(Color(1, 1, 1, 1))
	smi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	helper.add_child(smi)
	# the shimmer: dashes round the rim, a little outside the black
	var per: float = 2.0 * (sz[u_ax] + sz[v_ax])
	var dashes: int = clampi(int(per / EDGE_DASH), 16, 220)
	var rim := MultiMesh.new()
	rim.transform_format = MultiMesh.TRANSFORM_3D
	rim.use_colors = true
	rim.instance_count = dashes
	var dash := QuadMesh.new()
	dash.size = Vector2(EDGE_DASH * 0.9, 0.014)
	rim.mesh = dash
	for i in range(dashes):
		var t: float = float(i) / float(dashes) * per
		var p2: Vector3 = face + normal * 0.004
		var along_u: bool = true
		if t < sz[u_ax]:
			p2[u_ax] += -half_u + t
			p2[v_ax] += half_v
		elif t < sz[u_ax] + sz[v_ax]:
			p2[u_ax] += half_u
			p2[v_ax] += half_v - (t - sz[u_ax])
			along_u = false
		elif t < 2.0 * sz[u_ax] + sz[v_ax]:
			p2[u_ax] += half_u - (t - sz[u_ax] - sz[v_ax])
			p2[v_ax] += -half_v
		else:
			p2[u_ax] += -half_u
			p2[v_ax] += -half_v + (t - 2.0 * sz[u_ax] - sz[v_ax])
			along_u = false
		# not a dotted frame: each dash a little in or out of the seam, its
		# own length and thickness — the edge of a hole, not a border
		var jit: float = rng.randf_range(-0.012, 0.012)
		if along_u:
			p2[v_ax] += jit
		else:
			p2[u_ax] += jit
		var b2: Basis = basis
		if not along_u:
			b2 = basis * Basis(Vector3(0, 0, 1), PI * 0.5)
		b2 = b2.scaled(Vector3(rng.randf_range(0.45, 1.25), rng.randf_range(0.35, 1.0), 1.0))
		rim.set_instance_transform(i, Transform3D(b2, p2))
		rim.set_instance_color(i, Color(0.7, 0.8, 1.0, 0.0))
	var rmi := MultiMeshInstance3D.new()
	rmi.name = "Rim"
	rmi.multimesh = rim
	rmi.material_override = _glow(Color(1, 1, 1, 1))
	rmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	helper.add_child(rmi)
	helper.setup(stars, rim, rng.randi())


## The root's origin in `mi`'s parent space (works before the set is in the
## tree: walks the parents).
static func _rel_inv(root: Node, mi: Node3D) -> Vector3:
	var xf := Transform3D.IDENTITY
	var p: Node = mi.get_parent()
	while p != null and p != root:
		var p3: Node3D = p as Node3D
		if p3 != null:
			xf = p3.transform * xf
		p = p.get_parent()
	return xf.affine_inverse() * Vector3.ZERO


## A quad's basis laid on the face: its X along the face's u axis, Y along
## v, +Z (QuadMesh's normal) along `normal` (the materials draw both sides).
static func _face_basis(u_ax: int, v_ax: int, normal: Vector3) -> Basis:
	var x := Vector3.ZERO
	x[u_ax] = 1.0
	var y := Vector3.ZERO
	y[v_ax] = 1.0
	return Basis(x, y, normal)


## The motion: stars twinkle slowly, a brightness runs round the rim.
class VoidShimmer extends Node3D:
	var _stars: MultiMesh
	var _rim: MultiMesh
	var _phase: PackedFloat32Array = PackedFloat32Array()
	var _speed: PackedFloat32Array = PackedFloat32Array()
	var _t: float = 0.0
	var _acc: float = 0.0

	func setup(stars: MultiMesh, rim: MultiMesh, seed_v: int) -> void:
		_stars = stars
		_rim = rim
		var rng := RandomNumberGenerator.new()
		rng.seed = seed_v
		_phase.resize(stars.instance_count)
		_speed.resize(stars.instance_count)
		for i in range(stars.instance_count):
			_phase[i] = rng.randf() * TAU
			_speed[i] = rng.randf_range(0.25, 0.9)
		_paint()

	func _process(delta: float) -> void:
		_t += delta
		_acc += delta
		if _acc < 1.0 / 20.0:
			return
		_acc = 0.0
		_paint()

	func _paint() -> void:
		if _stars == null or _rim == null:
			return
		# (2026-11-09) the void breathes with the music: the beat brightens
		# its rim and wakes its stars (light only; nothing moves)
		var beat: float = 0.0
		var loud: float = 0.0
		var trip: Node = get_node_or_null("/root/TripSync")
		if trip != null:
			beat = clampf(float(trip.get("pulse")), 0.0, 1.0)
			loud = clampf(float(trip.get("energy")), 0.0, 1.0)
		for i in range(_stars.instance_count):
			var tw: float = 0.5 + 0.5 * sin(_t * _speed[i] + _phase[i])
			var a: float = clampf(0.15 + 0.85 * tw * tw + 0.35 * beat * tw, 0.0, 1.0)
			_stars.set_instance_color(i, Color(0.78, 0.84, 1.0, a))
		var n: int = _rim.instance_count
		for i in range(n):
			var f: float = float(i) / float(n)
			var run: float = 0.5 + 0.5 * sin(TAU * (f * 3.0 - _t * 0.12))
			var flick: float = 0.5 + 0.5 * sin(_t * 2.3 + float(i) * 1.7)
			var a2: float = 0.10 + 0.55 * run * run + 0.15 * flick + 0.30 * beat + 0.15 * loud
			# a faint hue drift, the substrate's colour at the seam
			var hue: float = fposmod(0.58 + 0.08 * sin(_t * 0.2 + f * TAU), 1.0)
			var col: Color = Color.from_hsv(hue, 0.35, 1.0, clampf(a2, 0.0, 1.0))
			_rim.set_instance_color(i, col)
