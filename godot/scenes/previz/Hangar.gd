extends Node3D
## Procedural blockout of the giant barn-hangar festival venue.
## This is a previz STAND-IN built from primitives so the scene runs with zero
## imported assets — replace with real modelled geometry when it's ready.
## Coordinate convention: +X runs from stage (-X, back) toward the audience and
## the open bay doors (+X, outdoor festival ground). +Y up, +Z = stage width.

const LENGTH := 60.0   # interior depth, X
const WIDTH := 30.0    # interior width, Z
const WALL_H := 12.0   # eave height
const RIDGE_H := 20.0  # roof apex
const STAGE_X := -22.0 # front edge of the stage riser

func _ready() -> void:
	_ground()
	_shell()
	_stage_riser()


func _mat(color: Color, rough := 0.9, metallic := 0.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = rough
	m.metallic = metallic
	return m


func _box(size: Vector3, pos: Vector3, mat: StandardMaterial3D, rot_x := 0.0) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = size
	mi.mesh = bm
	mi.material_override = mat
	mi.position = pos
	if rot_x != 0.0:
		mi.rotation_degrees = Vector3(rot_x, 0.0, 0.0)
	add_child(mi)
	return mi


func _ground() -> void:
	# large festival ground extending out past the bay doors
	var mi := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(400.0, 400.0)
	mi.mesh = pm
	mi.material_override = _mat(Color(0.08, 0.08, 0.09))
	mi.position = Vector3(60.0, 0.0, 0.0)
	add_child(mi)


func _shell() -> void:
	var concrete := _mat(Color(0.32, 0.31, 0.3))
	var metal := _mat(Color(0.4, 0.42, 0.45), 0.6, 0.5)
	var hl := LENGTH * 0.5
	var hw := WIDTH * 0.5
	# side walls
	_box(Vector3(LENGTH, WALL_H, 0.4), Vector3(0.0, WALL_H * 0.5, hw), concrete)
	_box(Vector3(LENGTH, WALL_H, 0.4), Vector3(0.0, WALL_H * 0.5, -hw), concrete)
	# back wall (behind the stage)
	_box(Vector3(0.4, WALL_H, WIDTH), Vector3(-hl, WALL_H * 0.5, 0.0), concrete)
	# front: corner posts + lintel beam framing the open bay doors
	_box(Vector3(1.0, WALL_H, 1.0), Vector3(hl, WALL_H * 0.5, hw - 0.5), concrete)
	_box(Vector3(1.0, WALL_H, 1.0), Vector3(hl, WALL_H * 0.5, -hw + 0.5), concrete)
	_box(Vector3(1.0, 2.0, WIDTH), Vector3(hl, WALL_H, 0.0), metal)
	# gable roof: two tilted slabs meeting at the ridge
	var rise := RIDGE_H - WALL_H
	var slope := sqrt(hw * hw + rise * rise)
	var ang := rad_to_deg(atan2(rise, hw))
	var y_mid := (WALL_H + RIDGE_H) * 0.5
	_box(Vector3(LENGTH, 0.4, slope), Vector3(0.0, y_mid, hw * 0.5), metal, ang)
	_box(Vector3(LENGTH, 0.4, slope), Vector3(0.0, y_mid, -hw * 0.5), metal, -ang)


func _stage_riser() -> void:
	var stage := _mat(Color(0.12, 0.12, 0.13))
	_box(Vector3(8.0, 1.5, WIDTH * 0.85), Vector3(STAGE_X - 4.0, 0.75, 0.0), stage)
