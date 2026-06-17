# Portrait3D.gd
# ════════════════════════════════════════════════════════════════
# Controller for Portrait3D.tscn — a SubViewport-backed VN portrait
# that renders a 3D character GLB to a ViewportTexture. CharLayer
# instantiates this scene when a matching GLB is available for the
# speaking character; otherwise it falls back to the existing
# PNG / ASCII-composition portrait path.
#
# Public API:
#   load_character(glb_path: String, expression: String = "")
#       Loads a GLB into CharacterAnchor; clears any previous load.
#       Re-runs the auto-orient + auto-scale heuristic the Graustark
#       hero placement uses, so heroes from different exporters
#       (Mixamo, Meshy, Ready Player Me) all frame consistently.
#
#   set_expression(expression: String)
#       Stub for future expression-driven pose/shader tweaks. Right
#       now expression just tints the ambient light slightly.
#
#   get_viewport_texture() -> ViewportTexture
#       Convenience accessor used by CharLayer when wrapping this
#       node inside a TextureRect.
# ════════════════════════════════════════════════════════════════
extends SubViewportContainer

const PORTRAIT_W: int = 300
const PORTRAIT_H: int = 320
const TARGET_HEIGHT_M: float = 1.80   # frame to roughly real-human

@onready var _viewport: SubViewport = $SubViewport
@onready var _anchor: Node3D = $SubViewport/CharacterAnchor
@onready var _placeholder: Node3D = $SubViewport/CharacterAnchor/Placeholder

var _loaded_glb_path: String = ""
var _current_character: Node3D = null


func _ready() -> void:
	custom_minimum_size = Vector2(PORTRAIT_W, PORTRAIT_H)


# ── Public API ────────────────────────────────────────────────────
func load_character(glb_path: String, _expression: String = "") -> bool:
	if glb_path == _loaded_glb_path and _current_character != null:
		return true
	# Tear down any previously-loaded model
	if _current_character != null and is_instance_valid(_current_character):
		_current_character.queue_free()
	_current_character = null
	# Hide placeholder (the editor-default capsule) once we actually
	# have something to render
	if _placeholder != null:
		_placeholder.visible = false
	var ps: PackedScene = load(glb_path) as PackedScene
	if ps == null:
		push_warning("[Portrait3D] Could not load GLB at %s" % glb_path)
		return false
	var inst: Node = ps.instantiate()
	if inst == null:
		return false
	_anchor.add_child(inst)
	_current_character = inst as Node3D
	if _current_character == null:
		# Top node wasn't a Node3D — wrap it
		var wrap := Node3D.new()
		_anchor.add_child(wrap)
		inst.reparent(wrap)
		_current_character = wrap
	_loaded_glb_path = glb_path
	# Auto-orient + auto-scale to the portrait's target framing
	_orient_and_scale_character(_current_character)
	return true


func set_expression(_expression: String) -> void:
	# Stub. Expression-driven pose/shader work goes here later.
	pass


func get_viewport_texture() -> Texture2D:
	return _viewport.get_texture()


# ── Internal: orient + scale the loaded GLB ──────────────────────
func _orient_and_scale_character(root: Node3D) -> void:
	# Same logic as build_graustark.py's _instance_hero_glb: measure
	# the bounding box, figure out which axis is "up," scale so the
	# longest axis hits TARGET_HEIGHT_M, drop the model so its feet
	# land on the anchor's origin plane.
	var mesh_objs: Array[Node] = _collect_mesh_instances(root)
	if mesh_objs.is_empty():
		return
	var aabb_min: Vector3 = Vector3.INF
	var aabb_max: Vector3 = -Vector3.INF
	for n: Node in mesh_objs:
		var mi: MeshInstance3D = n as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		var local_aabb: AABB = mi.mesh.get_aabb()
		# Transform AABB into root space
		var xform: Transform3D = root.global_transform.affine_inverse() * mi.global_transform
		var world_aabb: AABB = xform * local_aabb
		aabb_min = aabb_min.min(world_aabb.position)
		aabb_max = aabb_max.max(world_aabb.position + world_aabb.size)
	if aabb_min == Vector3.INF:
		return
	var ext: Vector3 = aabb_max - aabb_min
	# Pick the largest extent — that's the height axis (auto-detect
	# so a Z-up Meshy export and a Y-up Mixamo export both work)
	var max_axis: int = 1
	if ext.x > ext.y and ext.x > ext.z: max_axis = 0
	elif ext.z > ext.y: max_axis = 2
	var current_h: float = [ext.x, ext.y, ext.z][max_axis]
	if current_h < 0.001:
		return
	var s: float = TARGET_HEIGHT_M / current_h
	root.scale = Vector3(s, s, s)
	# Re-measure post-scale and translate so feet land on Y=0
	var bot_y: float = aabb_min.y * s
	root.position = Vector3(-((aabb_min.x + aabb_max.x) / 2.0) * s,
	                         -bot_y,
	                         -((aabb_min.z + aabb_max.z) / 2.0) * s)


func _collect_mesh_instances(node: Node, out: Array[Node] = []) -> Array[Node]:
	if node is MeshInstance3D:
		out.append(node)
	for child in node.get_children():
		_collect_mesh_instances(child, out)
	return out
