class_name Helicopter
extends Node3D
## The helicopter that buzzes the hangar. Loads a real model if present
## (res://assets/models/helicopter.glb), otherwise a procedural blockout with a
## spinning main + tail rotor. fly(progress 0..1) flies an approach → buzz →
## depart path low over the hangar mouth.

const MODEL_CANDIDATES := [
	"res://assets/models/helicopter.glb",
	"res://assets/models/heli.glb",
]

const START := Vector3(120.0, 48.0, -75.0)
const BUZZ := Vector3(30.0, 17.0, 0.0)    # low pass over the stage mouth
const END := Vector3(-70.0, 26.0, 70.0)

var _rotor: Node3D


func _ready() -> void:
	visible = false
	if not _try_model():
		_build()


func _mat(c: Color, rough := 0.6, metallic := 0.5) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = c
	m.roughness = rough
	m.metallic = metallic
	return m


func _box(size: Vector3, pos: Vector3, mat: StandardMaterial3D, parent: Node = self) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = size
	mi.mesh = bm
	mi.material_override = mat
	mi.position = pos
	parent.add_child(mi)
	return mi


func _try_model() -> bool:
	for p in MODEL_CANDIDATES:
		if ResourceLoader.exists(p):
			var res: Resource = load(p)
			if res is PackedScene:
				add_child((res as PackedScene).instantiate())
				return true
	return false


func _build() -> void:
	var body := _mat(Color(0.18, 0.2, 0.22))
	var dark := _mat(Color(0.08, 0.08, 0.09), 0.4)
	_box(Vector3(5.0, 1.8, 1.9), Vector3.ZERO, body)              # fuselage
	_box(Vector3(1.8, 1.2, 1.7), Vector3(2.0, 0.2, 0.0), dark)    # cockpit
	_box(Vector3(4.5, 0.5, 0.5), Vector3(-4.2, 0.4, 0.0), body)   # tail boom
	_box(Vector3(0.4, 1.4, 0.4), Vector3(-6.2, 0.9, 0.0), body)   # tail fin
	_box(Vector3(4.6, 0.15, 0.25), Vector3(0.0, -1.0, 0.7), dark) # skids
	_box(Vector3(4.6, 0.15, 0.25), Vector3(0.0, -1.0, -0.7), dark)
	# main rotor
	_rotor = Node3D.new()
	_rotor.position = Vector3(0.0, 1.2, 0.0)
	add_child(_rotor)
	_box(Vector3(12.0, 0.1, 0.5), Vector3.ZERO, dark, _rotor)
	_box(Vector3(0.5, 0.1, 12.0), Vector3.ZERO, dark, _rotor)
	# tail rotor
	var tail := Node3D.new()
	tail.position = Vector3(-6.4, 0.9, 0.3)
	add_child(tail)
	_box(Vector3(0.1, 3.0, 0.3), Vector3.ZERO, dark, tail)
	_rotor.set_meta("tail", tail)


func _process(delta: float) -> void:
	if _rotor:
		_rotor.rotate_y(delta * 45.0)
		var tail: Node3D = _rotor.get_meta("tail")
		if tail:
			tail.rotate_x(delta * 60.0)


func fly(progress: float) -> void:
	var p := clampf(progress, 0.0, 1.0)
	var pos: Vector3
	var ahead: Vector3
	if p < 0.5:
		var u := p / 0.5
		pos = START.lerp(BUZZ, u)
		ahead = START.lerp(BUZZ, minf(u + 0.05, 1.0))
	else:
		var u := (p - 0.5) / 0.5
		pos = BUZZ.lerp(END, u)
		ahead = BUZZ.lerp(END, minf(u + 0.05, 1.0))
	global_position = pos
	if pos.distance_to(ahead) > 0.01:
		look_at(ahead, Vector3.UP)
