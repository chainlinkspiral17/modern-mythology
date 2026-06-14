# FirstPersonController.gd
# ════════════════════════════════════════════════════════════════
# COMMUNITY PLANNED · Frasier's eye-height walking controller.
#
# Default controls:
#   WASD           · move forward / back / strafe
#   Q / E          · turn left / right (works in embedded play window)
#   R / F          · pitch up / down (works in embedded play window)
#   mouse          · look (when not embedded; may not work in embed)
#   space / ctrl   · up / down (noclip only)
#   shift          · slower (careful) walk
#   esc            · release mouse capture
#   F1             · TOGGLE NOCLIP (fly through walls — debug)
#   F2             · TELEPORT to (0, 3, 0) — debug recovery if stuck
# ════════════════════════════════════════════════════════════════

extends CharacterBody3D

@export var walk_speed: float = 2.2
@export var careful_speed: float = 1.0
@export var fly_speed: float = 6.0
@export var mouse_sensitivity: float = 0.0025
@export var keyboard_turn_speed: float = 2.2     # radians/sec for Q/E turn
@export var keyboard_pitch_speed: float = 1.6    # radians/sec for R/F pitch
@export var eye_height: float = 1.65

const GRAVITY: float = 9.8

var camera: Camera3D
var pitch: float = 0.0
# DEFAULT TO NOCLIP for testing. Once we confirm movement works
# in fly mode, we'll add collision back. Toggle with F1.
var noclip: bool = true
var _logged_input := false


func _ready() -> void:
	camera = get_node_or_null("Camera3D")
	if camera and camera.position.y < 0.01:
		camera.position.y = eye_height
	# CRITICAL: force the player's Camera3D to be the active one.
	# The cathedral_interior.glb (and others) ship with an embedded
	# camera from the Blender export (FrasierEye / cam_player_entry /
	# etc.) — Godot can pick that as the active camera, which means
	# the player moves but the view never updates because the
	# rendered camera is fixed elsewhere in the scene.
	if camera:
		camera.make_current()
	# Also defensively de-activate any other cameras in the scene
	var scene_root := get_tree().current_scene
	if scene_root:
		_deactivate_other_cameras(scene_root, camera)
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
	print("[FPC] _ready · mouse mode: %s · spawn at %s" % [Input.mouse_mode, global_position])
	print("[FPC] noclip=%s · WASD move · Q/E turn · R/F pitch · Space/Ctrl up/down · F1 collide · F2 teleport" % noclip)
	print("[FPC] active camera: %s" % camera)


func _deactivate_other_cameras(node: Node, keep: Camera3D) -> void:
	if node is Camera3D and node != keep:
		var other := node as Camera3D
		if other.current:
			other.current = false
			print("[FPC] de-activated stray camera: %s" % other.get_path())
	for child in node.get_children():
		_deactivate_other_cameras(child, keep)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		# While the right mouse button is held the MoodCycler is
		# consuming the horizontal motion to spin the strata wheel —
		# freeze player look so the camera doesn't slew at the same
		# time. Vertical pitch stays free so the cycler doesn't
		# eat all motion.
		if Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
			return
		rotate_y(-event.relative.x * mouse_sensitivity)
		if camera:
			pitch -= event.relative.y * mouse_sensitivity
			pitch = clamp(pitch, -PI / 2.2, PI / 2.2)
			camera.rotation.x = pitch
	elif event is InputEventKey and event.pressed:
		match event.keycode:
			KEY_ESCAPE:
				if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
					Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
					print("[FPC] mouse released")
				else:
					Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
					print("[FPC] mouse captured")
			KEY_F1:
				action_toggle_collide()
			KEY_F2:
				action_teleport_origin()
			KEY_F4:
				action_toggle_hud()


func action_toggle_collide() -> void:
	noclip = not noclip
	print("[FPC] noclip = %s" % noclip)


func action_teleport_origin() -> void:
	global_position = Vector3(0, 3, 0)
	velocity = Vector3.ZERO
	print("[FPC] teleport to (0, 3, 0) · current global_position now %s" % global_position)


func action_toggle_hud() -> void:
	# Clean HUD = ALL floating UI canvases off. Every script that
	# owns a HUD layer (scene HUD, PDPRiffmaster, InGameMusic track
	# label, DebugMenu, etc.) adds its CanvasLayer / Control to
	# the "ui" group. We walk the group and snap them all to the
	# same visibility state.
	#
	# NOTE — duck-typed access on .visible because CanvasLayer
	# does NOT extend CanvasItem in Godot 4 (separate base classes,
	# both have their own .visible property). Casting to CanvasItem
	# returns null for CanvasLayer → crash. Use `in` to check.
	var ui_nodes: Array = get_tree().get_nodes_in_group("ui")
	if ui_nodes.is_empty():
		return
	var first: Node = ui_nodes[0] as Node
	if first == null or not ("visible" in first):
		return
	var target_visible: bool = not first.visible
	var count: int = 0
	for n in ui_nodes:
		if "visible" in n:
			n.visible = target_visible
			count += 1
	print("[FPC] HUD visible = %s (%d ui nodes)" % [target_visible, count])


func action_mouse_release() -> void:
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	print("[FPC] mouse released (debug menu accessible)")


func action_mouse_capture() -> void:
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
	print("[FPC] mouse captured")


func _physics_process(delta: float) -> void:
	# Keyboard turning · works even if mouse-look doesn't (embedded
	# play window quirks). Q/E for yaw, R/F for pitch.
	var yaw_input: float = 0.0
	if Input.is_key_pressed(KEY_Q):
		yaw_input += 1.0
	if Input.is_key_pressed(KEY_E):
		yaw_input -= 1.0
	if abs(yaw_input) > 0.01:
		rotate_y(yaw_input * keyboard_turn_speed * delta)

	var pitch_input: float = 0.0
	if Input.is_key_pressed(KEY_R):
		pitch_input += 1.0
	if Input.is_key_pressed(KEY_F):
		pitch_input -= 1.0
	if abs(pitch_input) > 0.01 and camera:
		pitch += pitch_input * keyboard_pitch_speed * delta
		pitch = clamp(pitch, -PI / 2.2, PI / 2.2)
		camera.rotation.x = pitch

	var input_vec := Vector3.ZERO
	if Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP):
		input_vec.z -= 1.0
	if Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN):
		input_vec.z += 1.0
	if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT):
		input_vec.x -= 1.0
	if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT):
		input_vec.x += 1.0

	# Log the first input event so we can verify the script is running
	if input_vec.length() > 0.01 and not _logged_input:
		_logged_input = true
		print("[FPC] first WASD input detected · script is running")

	if noclip:
		# Fly mode: ignore gravity and collisions
		var fly_input := input_vec
		if Input.is_key_pressed(KEY_SPACE):
			fly_input.y += 1.0
		if Input.is_key_pressed(KEY_CTRL):
			fly_input.y -= 1.0
		var direction: Vector3 = (transform.basis * fly_input).normalized() * fly_speed
		global_position += direction * delta
		velocity = Vector3.ZERO
		return

	# Normal walk mode
	var speed: float = careful_speed if Input.is_key_pressed(KEY_SHIFT) else walk_speed
	var direction: Vector3 = (transform.basis * input_vec).normalized() * speed

	velocity.x = direction.x
	velocity.z = direction.z

	if not is_on_floor():
		velocity.y -= GRAVITY * delta

	move_and_slide()
