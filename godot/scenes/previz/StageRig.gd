extends Node3D
## Three escalating professional truss rigs. Each level BUILDS ON the previous:
## level 2 = level 1 + more, level 3 = level 2 + more. This is the structural
## truss/skeleton only — the animated fixtures live in LightingRig (which also
## escalates per level). Local space; the Previz scene positions it at the stage.

const W := 24.0   # truss span across the stage (Z)

func build(level: int) -> void:
	for c in get_children():
		c.queue_free()
	_rig_one()
	if level >= 2:
		_rig_two()
	if level >= 3:
		_rig_three()


func _m() -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(0.13, 0.13, 0.15)
	m.roughness = 0.5
	m.metallic = 0.7
	return m


func _box(size: Vector3, pos: Vector3) -> void:
	var mi := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = size
	mi.mesh = bm
	mi.material_override = _m()
	mi.position = pos
	add_child(mi)


func _tower(z: float, h: float, x := 0.0) -> void:
	_box(Vector3(0.5, h, 0.5), Vector3(x, h * 0.5, z))


func _cross(y: float, x := 0.0, span := W) -> void:
	_box(Vector3(0.5, 0.5, span), Vector3(x, y, 0.0))


# ── Level 1 — intimate: a single front truss on two towers ───────────────────
func _rig_one() -> void:
	_tower(-W * 0.5 + 1.0, 8.0)
	_tower(W * 0.5 - 1.0, 8.0)
	_cross(8.0)


# ── Level 2 — adds an upstage truss, side booms and a backdrop frame ─────────
func _rig_two() -> void:
	_tower(-W * 0.5 + 1.0, 8.0, -6.0)
	_tower(W * 0.5 - 1.0, 8.0, -6.0)
	_cross(8.0, -6.0)
	# downstage→upstage ties to make it read as a frame
	_box(Vector3(6.0, 0.4, 0.4), Vector3(-3.0, 8.0, -W * 0.5 + 1.0))
	_box(Vector3(6.0, 0.4, 0.4), Vector3(-3.0, 8.0, W * 0.5 - 1.0))
	# side booms
	_box(Vector3(0.4, 7.0, 0.4), Vector3(1.0, 3.5, -W * 0.5 - 1.0))
	_box(Vector3(0.4, 7.0, 0.4), Vector3(1.0, 3.5, W * 0.5 + 1.0))
	# backdrop frame upstage
	_box(Vector3(0.4, 6.5, W), Vector3(-7.0, 4.25, 0.0))


# ── Level 3 — adds an overhead grid, PA/LED towers, floor truss + thrust ─────
func _rig_three() -> void:
	_cross(8.0, -3.0)
	_cross(8.0, 3.0)
	# PA / LED stacks flanking the stage
	_box(Vector3(1.2, 9.0, 1.2), Vector3(0.0, 4.5, -W * 0.5 - 2.0))
	_box(Vector3(1.2, 9.0, 1.2), Vector3(0.0, 4.5, W * 0.5 + 2.0))
	# downstage floor truss
	_box(Vector3(0.5, 0.5, W), Vector3(2.5, 0.4, 0.0))
	# (removed the thrust/runway slab — it read as a waist-high block in front of the band)
