# SprinklerFX.gd — lawn sprinklers as PARTICLES (2026-09-07)
# ════════════════════════════════════════════════════════════════
# Meadowlark Circle's opening: "The sprinklers activate in sequence,
# lot by lot, traveling east down the block." Draft 1 drew each fan
# as a tinted slab (this pipeline has no alpha — they rendered as
# opaque blue rectangles: "what are these blue rectangles in front of
# the home?"); draft 2 drew five thin tubes ("still look ridiculous,
# consider particles or transparent images"). Draft 3: water is
# particles.
#
# Draft 4 (2026-09-24, the user: "sprinklers should do the rotational
# chug-chug-chug thing and there should be more in a single yard and
# they should have wider arcs"): IMPACT sprinklers. Each head throws one
# narrow jet (plus a short break-up spray at the nozzle) and steps it
# across its arc in ticks — STEP_DEG every TICK_SECONDS, the arm kicking
# back each time — then swings fast back to the start and goes again,
# spraying throughout, the way a Rain Bird does. Three heads per lawn;
# the arc is read from the head's name, Sprinkler_Head_<lot>_<k>_a<from>_<to>
# (degrees counter-clockwise from +X in the BUILDER's frame). The lots
# come on in sequence, west to east, and stay on.
#
# Miller_Cracked_Head keeps its fixed thin arc to the sidewalk (the
# cracked housing is jammed — it does not turn).
#
# Attach to a Node3D in the locale .tscn. On _ready it walks the scene
# for MeshInstance3Ds named Sprinkler_Head_* / Miller_Cracked_Head and
# parents the emitters at each. CPU particles so the Compatibility
# renderer never has a say. World geometry, not HUD: F4 leaves it alone.
# ════════════════════════════════════════════════════════════════
extends Node3D

const TICK_SECONDS: float = 0.16       # one "chug"
const STEP_DEG: float = 6.0            # how far the arm advances per chug
const RETURN_DEG_PER_S: float = 140.0  # the fast swing back
const JET_SPEED: float = 7.0           # m/s · ~3.7 m throw at 24° up
const JET_ELEV_DEG: float = 24.0
const ARC_SPEED: float = 4.2           # the cracked head's thin arc
const LOT_STAGGER: float = 1.4         # s between lots coming on
const WATER: Color = Color(0.86, 0.92, 0.98, 0.55)
# the sound of it: three impact heads out of phase over the spray's hiss,
# rendered by tools/audio/sprinkler_chug.py as a seamless 8 s loop
const CHUG_PATH: String = "res://assets/audio/sfx/env/sprinkler_chug_loop.wav"
const CHUG_DB: float = -13.0

class Head:
	var jet: CPUParticles3D
	var mist: CPUParticles3D
	var arm: MeshInstance3D
	var a0: float = 0.0
	var a1: float = 0.0
	var angle: float = 0.0
	var returning: bool = false
	var tick_t: float = 0.0
	var start_at: float = 0.0
	var started: bool = false

var _heads: Array[Head] = []
var _t: float = 0.0
var _chug: AudioStreamPlayer = null


func _ready() -> void:
	# The glb's meshes arrive with the parent; wait one frame so the
	# instance tree is complete before walking it.
	await get_tree().process_frame
	var root: Node = get_parent()
	if root == null:
		return
	var found: Array[MeshInstance3D] = []
	_collect(root, found)
	# lots west → east for the sequence (godot x ascending)
	found.sort_custom(func(a: MeshInstance3D, b: MeshInstance3D) -> bool:
		return a.global_position.x < b.global_position.x)
	var lot_order: Dictionary = {}
	for mi in found:
		var centre: Vector3 = mi.global_transform * mi.get_aabb().get_center()
		var nm: String = String(mi.name)
		if nm.begins_with("Miller_Cracked"):
			var arc: CPUParticles3D = _make_jet(true)
			add_child(arc)
			arc.global_position = centre + Vector3(0.0, 0.04, 0.0)
			arc.emitting = true
			continue
		var h: Head = Head.new()
		var parts: PackedStringArray = nm.split("_")
		# Sprinkler_Head_<lot>_<k>_a<from>_<to>
		var lot: String = parts[2] if parts.size() > 2 else "0"
		if not lot_order.has(lot):
			lot_order[lot] = lot_order.size()
		var lot_i: int = int(lot_order[lot])
		h.a0 = 0.0
		h.a1 = 90.0
		for i in range(parts.size()):
			if parts[i].begins_with("a") and parts[i].substr(1).is_valid_int() and i + 1 < parts.size():
				h.a0 = float(parts[i].substr(1).to_int())
				h.a1 = float(parts[i + 1].to_int())
		h.angle = h.a0
		h.start_at = float(lot_i) * LOT_STAGGER
		h.jet = _make_jet(false)
		h.mist = _make_mist()
		h.arm = _make_arm()
		add_child(h.jet)
		add_child(h.mist)
		add_child(h.arm)
		var nozzle: Vector3 = centre + Vector3(0.0, 0.06, 0.0)
		h.jet.global_position = nozzle
		h.mist.global_position = nozzle
		h.arm.global_position = nozzle
		h.jet.emitting = false
		h.mist.emitting = false
		_aim(h)
		_heads.append(h)
	if not _heads.is_empty() and ResourceLoader.exists(CHUG_PATH):
		var st: AudioStreamWAV = load(CHUG_PATH) as AudioStreamWAV
		if st != null:
			st.loop_mode = AudioStreamWAV.LOOP_FORWARD
			st.loop_begin = 0
			st.loop_end = int(st.get_length() * float(st.mix_rate))
			_chug = AudioStreamPlayer.new()
			_chug.name = "Sprinkler_Chug"
			_chug.stream = st
			_chug.volume_db = CHUG_DB
			if AudioServer.get_bus_index("SFX") >= 0:
				_chug.bus = "SFX"
			add_child(_chug)


func _collect(node: Node, acc: Array[MeshInstance3D]) -> void:
	if node is MeshInstance3D:
		var nm: String = node.name
		if nm.begins_with("Sprinkler_Head") or nm.begins_with("Miller_Cracked_Head"):
			acc.append(node as MeshInstance3D)
	for child in node.get_children():
		_collect(child, acc)


# builder heading (deg, CCW from +X in the builder's x/y) → godot direction
func _heading(deg: float, elev_deg: float) -> Vector3:
	var a: float = deg_to_rad(deg)
	var e: float = deg_to_rad(elev_deg)
	return Vector3(cos(a) * cos(e), sin(e), -sin(a) * cos(e))


func _aim(h: Head) -> void:
	h.jet.direction = _heading(h.angle, JET_ELEV_DEG)
	h.mist.direction = _heading(h.angle, 40.0)
	# the arm points along the jet (godot yaw: +X rotated by the heading)
	h.arm.rotation = Vector3(0.0, deg_to_rad(h.angle), 0.0)


func _water_mesh(size: float) -> QuadMesh:
	var quad: QuadMesh = QuadMesh.new()
	quad.size = Vector2(size, size)
	var mat: StandardMaterial3D = StandardMaterial3D.new()
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
	mat.vertex_color_use_as_albedo = true
	mat.albedo_color = Color(0.92, 0.96, 1.0, 0.6)
	quad.material = mat
	return quad


func _make_jet(is_cracked: bool) -> CPUParticles3D:
	var p: CPUParticles3D = CPUParticles3D.new()
	p.name = "Spray_Arc" if is_cracked else "Spray_Jet"
	p.amount = 90 if is_cracked else 170
	p.lifetime = 1.4 if is_cracked else 1.25
	p.local_coords = false
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_POINT
	# the cracked head's arc goes to the sidewalk (-Z godot), thin and fast
	p.direction = Vector3(0.0, 0.62, -0.78) if is_cracked else Vector3(1.0, 0.45, 0.0)
	p.spread = 4.0 if is_cracked else 2.5
	var v: float = ARC_SPEED if is_cracked else JET_SPEED
	p.initial_velocity_min = v * 0.94
	p.initial_velocity_max = v * 1.04
	p.gravity = Vector3(0.0, -9.8, 0.0)
	p.scale_amount_min = 0.018
	p.scale_amount_max = 0.034
	p.color = WATER
	p.mesh = _water_mesh(0.05)
	return p


func _make_mist() -> CPUParticles3D:
	# the break-up at the nozzle: the impact arm knocks the jet apart
	var p: CPUParticles3D = CPUParticles3D.new()
	p.name = "Spray_Mist"
	p.amount = 40
	p.lifetime = 0.6
	p.local_coords = false
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_POINT
	p.spread = 22.0
	p.initial_velocity_min = 1.6
	p.initial_velocity_max = 2.8
	p.gravity = Vector3(0.0, -9.8, 0.0)
	p.scale_amount_min = 0.014
	p.scale_amount_max = 0.026
	p.color = WATER
	p.mesh = _water_mesh(0.04)
	return p


func _make_arm() -> MeshInstance3D:
	# the swinging impact arm: a short dark bar along the jet's heading
	var mi: MeshInstance3D = MeshInstance3D.new()
	mi.name = "Impact_Arm"
	var box: BoxMesh = BoxMesh.new()
	box.size = Vector3(0.14, 0.014, 0.018)
	var mat: StandardMaterial3D = StandardMaterial3D.new()
	mat.albedo_color = Color(0.22, 0.24, 0.22, 1.0)
	box.material = mat
	mi.mesh = box
	return mi


func _process(delta: float) -> void:
	_t += delta
	for h in _heads:
		if not h.started:
			if _t < h.start_at:
				continue
			h.started = true
			h.jet.emitting = true
			h.mist.emitting = true
			if _chug != null and not _chug.playing:
				_chug.play()
		if h.returning:
			h.angle -= RETURN_DEG_PER_S * delta
			if h.angle <= h.a0:
				h.angle = h.a0
				h.returning = false
				h.tick_t = 0.0
			_aim(h)
			continue
		h.tick_t += delta
		if h.tick_t >= TICK_SECONDS:
			h.tick_t -= TICK_SECONDS
			h.angle += STEP_DEG
			if h.angle >= h.a1:
				h.angle = h.a1
				h.returning = true
			_aim(h)
			# the arm's kick: a quick sideways flick on each chug
			h.arm.rotation.y += deg_to_rad(9.0)
		elif h.tick_t > TICK_SECONDS * 0.35:
			h.arm.rotation.y = deg_to_rad(h.angle)
