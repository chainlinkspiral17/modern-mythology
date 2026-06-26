class_name Disaster
extends Node3D
## The One Model Nation disaster beat: the helicopter buzzes the hangar mouth and,
## at the low pass, roof panels + glass panes break off and fall onto the
## stage-side crowd, with dust bursts. trigger() runs the sequence; reset() puts
## the pieces back. Designed to be fired from a key now and a timeline cue later.

const DURATION := 9.0
const RELEASE_AT := 0.45   # fraction of the flight where debris breaks off

var heli: Helicopter
var dust: GPUParticles3D
var active := false
var released := false
var t := 0.0

var _pieces: Array = []    # [{body:RigidBody3D, home:Transform3D}]


func setup(stage_x: float) -> void:
	_ground_collider()
	heli = Helicopter.new()
	add_child(heli)
	_build_debris(stage_x)
	_build_dust(stage_x)


func _ground_collider() -> void:
	var sb := StaticBody3D.new()
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(600.0, 1.0, 600.0)
	cs.shape = box
	sb.add_child(cs)
	sb.position = Vector3(40.0, -0.5, 0.0)   # top at y≈0
	add_child(sb)


func _piece(size: Vector3, pos: Vector3, mat: StandardMaterial3D) -> void:
	var rb := RigidBody3D.new()
	rb.position = pos
	rb.freeze = true            # held in the roof until release
	rb.gravity_scale = 1.0
	var mi := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = size
	mi.mesh = bm
	mi.material_override = mat
	rb.add_child(mi)
	var cs := CollisionShape3D.new()
	var shape := BoxShape3D.new()
	shape.size = size
	cs.shape = shape
	rb.add_child(cs)
	add_child(rb)
	_pieces.append({ "body": rb, "home": rb.transform })


func _build_debris(stage_x: float) -> void:
	var rust := StandardMaterial3D.new()
	rust.albedo_color = Color(0.45, 0.3, 0.22)
	rust.roughness = 0.85
	var glass := StandardMaterial3D.new()
	glass.albedo_color = Color(0.55, 0.75, 0.85, 0.35)
	glass.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	glass.roughness = 0.1
	glass.metallic = 0.2
	# along the front roof edge / mouth header, spread across the width
	for i in 7:
		var z := lerpf(-9.0, 9.0, float(i) / 6.0)
		_piece(Vector3(2.2, 0.2, 1.6), Vector3(stage_x + 3.0, 11.5, z), rust)
	for i in 5:
		var z := lerpf(-7.0, 7.0, float(i) / 4.0)
		_piece(Vector3(1.3, 0.15, 0.9), Vector3(stage_x + 5.0, 9.5, z), glass)


func _build_dust(stage_x: float) -> void:
	dust = GPUParticles3D.new()
	dust.amount = 96
	dust.lifetime = 2.6
	dust.one_shot = true
	dust.emitting = false
	dust.explosiveness = 0.6
	dust.position = Vector3(stage_x + 5.0, 1.0, 0.0)
	var pm := ParticleProcessMaterial.new()
	pm.direction = Vector3(1.0, 0.6, 0.0)
	pm.spread = 80.0
	pm.initial_velocity_min = 2.0
	pm.initial_velocity_max = 7.0
	pm.gravity = Vector3(0.0, -3.0, 0.0)
	pm.scale_min = 0.4
	pm.scale_max = 1.4
	dust.process_material = pm
	var quad := QuadMesh.new()
	quad.size = Vector2(0.8, 0.8)
	var dm := StandardMaterial3D.new()
	dm.albedo_color = Color(0.55, 0.5, 0.45, 0.5)
	dm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	dm.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	dm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	quad.material = dm
	dust.draw_pass_1 = quad
	add_child(dust)


func trigger() -> void:
	active = true
	released = false
	t = 0.0
	if heli:
		heli.visible = true
		heli.fly(0.0)


func reset() -> void:
	active = false
	released = false
	t = 0.0
	if heli:
		heli.visible = false
	if dust:
		dust.emitting = false
	for p in _pieces:
		var rb: RigidBody3D = p["body"]
		rb.freeze = true
		rb.linear_velocity = Vector3.ZERO
		rb.angular_velocity = Vector3.ZERO
		rb.transform = p["home"]


func _process(delta: float) -> void:
	if not active:
		return
	t += delta
	var p := t / DURATION
	if heli:
		heli.fly(p)
	if not released and p >= RELEASE_AT:
		_release()
	if t >= DURATION + 5.0:
		active = false
		if heli:
			heli.visible = false


func _release() -> void:
	released = true
	for p in _pieces:
		var rb: RigidBody3D = p["body"]
		rb.freeze = false
		rb.apply_central_impulse(Vector3(randf_range(3.0, 9.0), randf_range(-1.0, 1.0), randf_range(-3.0, 3.0)))
		rb.apply_torque_impulse(Vector3(randf_range(-4.0, 4.0), randf_range(-4.0, 4.0), randf_range(-4.0, 4.0)))
	if dust:
		dust.restart()
		dust.emitting = true
