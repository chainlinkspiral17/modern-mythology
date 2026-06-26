extends Node3D
## Venue: a large corrugated barrel-vault (Quonset) hangar whose OPEN end frames
## the stage, with the crowd gathered OUTSIDE the mouth on the festival apron —
## matching the reference photo. Loads the real model "barn hanger.glb" if it's
## been imported; otherwise builds a procedural barrel-vault blockout at roughly
## the reference scale (large to a human).
##
## Convention: the barrel runs along X. Open mouth at +X (stage + crowd outside);
## closed end at -X. +Y up, +Z = width. Apex ≈ WALL_H + RADIUS.

const LENGTH := 55.0
const RADIUS := 9.0    # half-span (≈18 m wide); arch apex ≈ 11.5 m
const WALL_H := 2.5    # straight kerb wall the arch springs from
const STAGE_X := 24.0  # stage sits just inside the +X open mouth

# The .glb is authored in Drive (one model nation finale/3D model/). Drop it at
# one of these res:// paths and it loads instead of the blockout.
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
	var apex := WALL_H + RADIUS
	var half := LENGTH * 0.5
	# straight kerb walls the arch springs from
	_box(Vector3(LENGTH, WALL_H, 0.4), Vector3(0.0, WALL_H * 0.5, RADIUS), kerb)
	_box(Vector3(LENGTH, WALL_H, 0.4), Vector3(0.0, WALL_H * 0.5, -RADIUS), kerb)
	# barrel-vault roof: tangent panels around a semicircle, extruded along X
	var n := 16
	var seg := PI / float(n)
	for i in n:
		var phi := seg * (float(i) + 0.5)
		var z := RADIUS * cos(phi)
		var y := WALL_H + RADIUS * sin(phi)
		var panel := _box(Vector3(LENGTH, 0.3, RADIUS * seg * 1.08), Vector3(0.0, y, z), metal)
		panel.rotation_degrees = Vector3(rad_to_deg(phi) - 90.0, 0.0, 0.0)
	# closed back end (-X)
	_box(Vector3(0.4, apex, RADIUS * 2.0), Vector3(-half, apex * 0.5, 0.0), metal)
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
	_box(Vector3(8.0, 1.5, RADIUS * 1.6), Vector3(STAGE_X - 2.0, 0.75, 0.0), _mat(Color(0.1, 0.1, 0.11)))
