# DebugHUD.gd
# ════════════════════════════════════════════════════════════════
# Tiny on-screen overlay showing the player's position + velocity.
# Lets you SEE that movement is working even if visual feedback
# from the scene is ambiguous.
# Attach to a Label node inside a CanvasLayer in the scene.
# ════════════════════════════════════════════════════════════════

extends Label

@export var target: NodePath

var _target_node: Node3D


func _ready() -> void:
	if target.is_empty():
		_target_node = get_tree().get_first_node_in_group("player") as Node3D
	else:
		_target_node = get_node_or_null(target) as Node3D
	add_theme_font_size_override("font_size", 24)
	add_theme_color_override("font_color", Color(1.0, 0.92, 0.65))
	add_theme_color_override("font_outline_color", Color(0.0, 0.0, 0.0))
	add_theme_constant_override("outline_size", 4)


func _process(_delta: float) -> void:
	if _target_node == null:
		text = "[no target]"
		return
	var pos: Vector3 = _target_node.global_position
	var vel: Vector3 = Vector3.ZERO
	if _target_node is CharacterBody3D:
		vel = (_target_node as CharacterBody3D).velocity
	var noclip_str: String = "OFF"
	if _target_node.has_method("get") and "noclip" in _target_node:
		noclip_str = "ON · flying" if _target_node.get("noclip") else "OFF · walking"
	text = "POS  x=%6.2f  y=%6.2f  z=%6.2f\nVEL  x=%6.2f  y=%6.2f  z=%6.2f\nSPEED %6.2f m/s\nMOUSE %s\nMODE  %s" % [
		pos.x, pos.y, pos.z,
		vel.x, vel.y, vel.z,
		vel.length(),
		["VISIBLE", "HIDDEN", "CAPTURED", "CONFINED"][Input.mouse_mode],
		noclip_str
	]
