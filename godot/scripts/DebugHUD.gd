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
    add_theme_font_size_override("font_size", 16)
    add_theme_color_override("font_color", Color(0.95, 0.85, 0.55))
    add_theme_color_override("font_outline_color", Color(0.05, 0.04, 0.02))
    add_theme_constant_override("outline_size", 2)


func _process(_delta: float) -> void:
    if _target_node == null:
        text = "[no target]"
        return
    var pos: Vector3 = _target_node.global_position
    var vel: Vector3 = Vector3.ZERO
    if _target_node is CharacterBody3D:
        vel = (_target_node as CharacterBody3D).velocity
    text = "pos: %5.2f, %5.2f, %5.2f\nvel: %5.2f, %5.2f, %5.2f\nspeed: %5.2f m/s\nmouse: %s" % [
        pos.x, pos.y, pos.z,
        vel.x, vel.y, vel.z,
        vel.length(),
        ["VISIBLE", "HIDDEN", "CAPTURED", "CONFINED"][Input.mouse_mode]
    ]
