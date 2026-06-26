extends Node3D
## Venue: a wide, shallow corrugated barrel-vault (Quonset) hangar matching the
## reference — a low segmental arch much wider than it is tall, a solid gable
## facade with a rectangular stage opening cut low-centre (+ a small hatch
## above), the stage in the mouth and the crowd OUTSIDE on the festival apron.
## Loads the real "barn hanger.glb" if imported; otherwise builds this blockout
## at roughly reference scale (large to a human).
##
## Convention: barrel runs along X. Open mouth/stage at +X; closed end at -X.
## +Y up, +Z width. Apex ≈ WALL_H + RISE.

const LENGTH := 55.0
const HALF_W := 15.0    # half-span → ~30 m wide
const WALL_H := 4.0     # side wall the arch springs from
const RISE := 8.0       # apex above the spring → apex ≈ 12 m (wide & shallow)
const OPEN_HW := 10.0   # stage-opening half-width (~20 m)
const OPEN_H := 9.0     # stage-opening height
const STAGE_X := 24.0   # stage just inside the +X mouth

const MODEL_CANDIDATES := [
	"res://assets/models/barn hanger.glb",
	"res://assets/models/barn_hanger.glb",
	"res://scenes/previz/models/barn hanger.glb",
]

func _ready() -> void:
	_ground()
	if not _try_model():
		_shell()
	_stage_riser()


func _mat(color: Color, rough := 0.85, metallic := 0.2) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = rough
	m.metallic = metallic
	return m


func _box(size: Vector3, pos: Vector3, mat: StandardMaterial3D) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = size
	mi.mesh = bm
	mi.material_override = mat
	mi.position = pos
	add_child(mi)
	return mi


func _try_model() -> bool:
	for p in MODEL_CANDIDATES:
		if ResourceLoader.exists(p):
			var res: Resource = load(p)
			if res is PackedScene:
				add_child((res as PackedScene).instantiate())
				return true
	return false


func _ground() -> void:
	var mi := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(600.0, 600.0)
	mi.mesh = pm
	mi.material_override = _mat(Color(0.09, 0.08, 0.07))
	mi.position = Vector3(40.0, 0.0, 0.0)
	add_child(mi)


func _shell() -> void:
	var metal := _mat(Color(0.46, 0.33, 0.26), 0.8, 0.35)   # rusty corrugated steel
	var kerb := _mat(Color(0.3, 0.29, 0.28))
	var apex := WALL_H + RISE
	var half := LENGTH * 0.5
	# segmental-arch geometry: arc of a circle whose centre sits below the spring
	var r := (HALF_W * HALF_W + RISE * RISE) / (2.0 * RISE)
	var cy := apex - r
	var theta := asin(clampf(HALF_W / r, -1.0, 1.0))
	# side kerb walls the arch springs from
	_box(Vector3(LENGTH, WALL_H, 0.4), Vector3(0.0, WALL_H * 0.5, HALF_W), kerb)
	_box(Vector3(LENGTH, WALL_H, 0.4), Vector3(0.0, WALL_H * 0.5, -HALF_W), kerb)
	# wide shallow barrel roof: tangent panels along the arc, extruded along X
	var n := 18
	for i in n:
		var f := -theta + (2.0 * theta) * (float(i) + 0.5) / float(n)
		var z := r * sin(f)
		var y := cy + r * cos(f)
		var seglen := r * (2.0 * theta / float(n)) * 1.06
		var panel := _box(Vector3(LENGTH, 0.3, seglen), Vector3(0.0, y, z), metal)
		panel.rotation_degrees = Vector3(rad_to_deg(f), 0.0, 0.0)
	# closed back end (-X)
	_box(Vector3(0.4, apex, HALF_W * 2.0), Vector3(-half, apex * 0.5, 0.0), metal)
	# front gable facade + rectangular stage opening (+X mouth)
	var fx := half
	# spandrels either side of the opening, up toward the roofline
	_box(Vector3(0.5, apex, HALF_W - OPEN_HW), Vector3(fx, apex * 0.5, (HALF_W + OPEN_HW) * 0.5), metal)
	_box(Vector3(0.5, apex, HALF_W - OPEN_HW), Vector3(fx, apex * 0.5, -(HALF_W + OPEN_HW) * 0.5), metal)
	# header above the opening
	_box(Vector3(0.5, apex - OPEN_H, OPEN_HW * 2.0), Vector3(fx, (OPEN_H + apex) * 0.5, 0.0), metal)
	# small square hatch/door high on the facade (reference detail)
	_box(Vector3(0.4, 2.6, 2.6), Vector3(fx + 0.1, OPEN_H + 2.0, 0.0), _mat(Color(0.2, 0.16, 0.14), 0.7, 0.3))
	# roof ventilators along the ridge
	for i in 5:
		var vx := lerpf(-half * 0.7, half * 0.55, float(i) / 4.0)
		var v := MeshInstance3D.new()
		var cm := CylinderMesh.new()
		cm.top_radius = 0.6
		cm.bottom_radius = 0.6
		cm.height = 1.4
		v.mesh = cm
		v.material_override = _mat(Color(0.3, 0.25, 0.22), 0.6, 0.4)
		v.position = Vector3(vx, apex + 0.4, 0.0)
		add_child(v)


func _stage_riser() -> void:
	_box(Vector3(8.0, 1.5, 22.0), Vector3(STAGE_X - 2.0, 0.75, 0.0), _mat(Color(0.1, 0.1, 0.11)))
