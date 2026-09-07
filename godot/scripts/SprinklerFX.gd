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
# Attach to a Node3D in the locale .tscn. On _ready it walks the
# scene for MeshInstance3Ds named Sprinkler_Head_* (a lawn fan aimed
# +Z godot / -Y blender — across the lawn away from the street) and
# Miller_Cracked_Head (the thin surgical arc toward the sidewalk,
# -Z godot) and parents a CPUParticles3D at each head. CPU particles
# so the Compatibility renderer never has a say.
#
# The heads fire in SEQUENCE east down the block (x ascending) —
# each runs SPRAY_SECONDS then hands off — the prelude's own image.
# World geometry, not HUD: no CanvasLayer, F4 leaves it alone.
# ════════════════════════════════════════════════════════════════
extends Node3D

const SPRAY_SECONDS: float = 7.0
const LAWN_SPEED: float = 5.2          # m/s · a fan head throws ~3 m
const ARC_SPEED: float = 4.2           # m/s · the cracked head's thin arc
const WATER: Color = Color(0.86, 0.92, 0.98, 0.55)

var _heads: Array[CPUParticles3D] = []
var _cycle_t: float = 0.0
var _active: int = 0


func _ready() -> void:
	# The glb's meshes arrive with the parent; wait one frame so the
	# instance tree is complete before walking it.
	await get_tree().process_frame
	var root: Node = get_parent()
	if root == null:
		return
	var found: Array[MeshInstance3D] = []
	_collect(root, found)
	# fan heads sorted west → east (godot x ascending) for the sequence
	found.sort_custom(func(a: MeshInstance3D, b: MeshInstance3D) -> bool:
		return a.global_position.x < b.global_position.x)
	for mi in found:
		var is_arc: bool = mi.name.begins_with("Miller_Cracked")
		var p: CPUParticles3D = _make_emitter(is_arc)
		var centre: Vector3 = mi.global_transform * mi.get_aabb().get_center()
		add_child(p)
		p.global_position = centre + Vector3(0.0, 0.04, 0.0)
		_heads.append(p)
	if _heads.is_empty():
		return
	for p in _heads:
		p.emitting = false
	_heads[0].emitting = true


func _collect(node: Node, acc: Array[MeshInstance3D]) -> void:
	if node is MeshInstance3D:
		var nm: String = node.name
		if nm.begins_with("Sprinkler_Head") or nm.begins_with("Miller_Cracked_Head"):
			acc.append(node as MeshInstance3D)
	for child in node.get_children():
		_collect(child, acc)


func _make_emitter(is_arc: bool) -> CPUParticles3D:
	var p: CPUParticles3D = CPUParticles3D.new()
	p.name = "Spray_Arc" if is_arc else "Spray_Fan"
	p.amount = 90 if is_arc else 220
	p.lifetime = 1.4
	p.local_coords = false
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_POINT
	# lawn fans throw away from the street (+Z godot); the cracked head's
	# arc goes the other way, to the sidewalk (-Z), thin and fast
	p.direction = Vector3(0.0, 0.62, -0.78) if is_arc else Vector3(0.0, 0.78, 0.62)
	p.spread = 4.0 if is_arc else 38.0
	p.initial_velocity_min = (ARC_SPEED if is_arc else LAWN_SPEED) * 0.92
	p.initial_velocity_max = (ARC_SPEED if is_arc else LAWN_SPEED) * 1.08
	p.gravity = Vector3(0.0, -9.8, 0.0)
	p.scale_amount_min = 0.018
	p.scale_amount_max = 0.034
	p.color = WATER
	var quad: QuadMesh = QuadMesh.new()
	quad.size = Vector2(0.05, 0.05)
	var mat: StandardMaterial3D = StandardMaterial3D.new()
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
	mat.vertex_color_use_as_albedo = true
	mat.albedo_color = Color(0.92, 0.96, 1.0, 0.6)
	quad.material = mat
	p.mesh = quad
	return p


func _process(delta: float) -> void:
	if _heads.size() < 2:
		return
	_cycle_t += delta
	if _cycle_t >= SPRAY_SECONDS:
		_cycle_t = 0.0
		_heads[_active].emitting = false
		_active = (_active + 1) % _heads.size()
		_heads[_active].emitting = true
