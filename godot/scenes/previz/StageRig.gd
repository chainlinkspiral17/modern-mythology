extends Node3D
## Three progressively more elaborate stage-show rigs, matching the story's
## escalation: 1) NoNo / intimate, 2) One Model Nation / mid, 3) Zonk / spectacle.
## build(level) rebuilds the rig from primitives + real SpotLight3D fixtures.
## The node is positioned at the stage by the Previz scene; geometry is local.

const STAGE_W := 24.0  # usable stage width (Z)

func build(level: int) -> void:
	for c in get_children():
		c.queue_free()
	match level:
		2:
			_rig_two()
		3:
			_rig_three()
		_:
			_rig_one()


func _mat(color: Color, rough := 0.7, metallic := 0.3) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = rough
	m.metallic = metallic
	return m


func _truss_mat() -> StandardMaterial3D:
	return _mat(Color(0.15, 0.15, 0.16), 0.5, 0.7)


func _box(size: Vector3, pos: Vector3, mat: StandardMaterial3D) -> void:
	var mi := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = size
	mi.mesh = bm
	mi.material_override = mat
	mi.position = pos
	add_child(mi)


## A vertical truss tower at z.
func _tower(z: float, height: float) -> void:
	_box(Vector3(0.4, height, 0.4), Vector3(0.0, height * 0.5, z), _truss_mat())


## A horizontal truss spanning the stage at height y, set back by x.
func _cross_truss(y: float, x := 0.0) -> void:
	_box(Vector3(0.5, 0.5, STAGE_W), Vector3(x, y, 0.0), _truss_mat())


## A spotlight fixture hung at (x,y,z), aimed at a stage target.
func _spot(pos: Vector3, color: Color, energy := 6.0, angle := 22.0) -> void:
	var body := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = Vector3(0.5, 0.5, 0.7)
	body.mesh = bm
	body.material_override = _mat(Color(0.05, 0.05, 0.05), 0.4, 0.6)
	body.position = pos
	add_child(body)
	var s := SpotLight3D.new()
	s.position = pos
	s.light_color = color
	s.light_energy = energy
	s.spot_range = 40.0
	s.spot_angle = angle
	s.shadow_enabled = false
	add_child(s)
	s.look_at(Vector3(pos.x + 6.0, 1.5, pos.z * 0.5), Vector3.UP)


# ── Level 1 — intimate (NoNo / dusk): single spot truss ──────────────────────
func _rig_one() -> void:
	_tower(-6.0, 8.0)
	_tower(6.0, 8.0)
	_cross_truss(8.0)
	_spot(Vector3(2.0, 7.5, -3.0), Color(1.0, 0.85, 0.7), 7.0, 18.0)
	_spot(Vector3(2.0, 7.5, 3.0), Color(1.0, 0.85, 0.7), 7.0, 18.0)


# ── Level 2 — mid (One Model Nation): front truss + washes + backdrop ─────────
func _rig_two() -> void:
	for z in [-10.0, -3.0, 3.0, 10.0]:
		_tower(z, 9.0)
	_cross_truss(9.0)
	_cross_truss(8.0, -6.0)
	# backdrop panel
	_box(Vector3(0.4, 7.0, STAGE_W), Vector3(-7.0, 4.5, 0.0), _mat(Color(0.1, 0.1, 0.14)))
	var cols := [Color(0.9, 0.5, 0.3), Color(0.4, 0.6, 1.0), Color(1.0, 0.85, 0.7), Color(0.6, 0.3, 0.8)]
	var i := 0
	for z in [-8.0, -3.0, 3.0, 8.0]:
		_spot(Vector3(1.0, 8.5, z), cols[i], 8.0, 20.0)
		i += 1


# ── Level 3 — spectacle (Zonk / night): full festival rig + LED towers + pyro ─
func _rig_three() -> void:
	for z in [-11.0, -6.0, 0.0, 6.0, 11.0]:
		_tower(z, 11.0)
	_cross_truss(11.0)
	_cross_truss(10.0, -4.0)
	_cross_truss(10.0, 4.0)
	# LED screen towers flanking the stage
	_box(Vector3(0.6, 8.0, 5.0), Vector3(-2.0, 5.0, -13.0), _mat(Color(0.05, 0.06, 0.1), 0.3))
	_box(Vector3(0.6, 8.0, 5.0), Vector3(-2.0, 5.0, 13.0), _mat(Color(0.05, 0.06, 0.1), 0.3))
	# runway extension toward the crowd
	_box(Vector3(10.0, 1.4, 4.0), Vector3(6.0, 0.7, 0.0), _mat(Color(0.12, 0.12, 0.13)))
	# pyro markers (emissive nubs along the stage front)
	for z in [-10.0, -5.0, 0.0, 5.0, 10.0]:
		var p := _mat(Color(1.0, 0.6, 0.2))
		p.emission_enabled = true
		p.emission = Color(1.0, 0.5, 0.1)
		_box(Vector3(0.4, 0.6, 0.4), Vector3(1.5, 0.3, z), p)
	var cols := [Color(1.0, 0.3, 0.6), Color(1.0, 0.8, 0.3), Color(0.4, 0.7, 1.0), Color(0.7, 0.3, 1.0), Color(1.0, 0.5, 0.2)]
	var i := 0
	for z in [-10.0, -5.0, 0.0, 5.0, 10.0]:
		_spot(Vector3(0.0, 10.5, z), cols[i], 10.0, 22.0)
		i += 1
