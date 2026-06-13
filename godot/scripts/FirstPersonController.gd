# FirstPersonController.gd
# ════════════════════════════════════════════════════════════════
# COMMUNITY PLANNED · Frasier's eye-height walking controller.
#
# Attach to a CharacterBody3D node with a Camera3D child. The
# pacing is intentionally slow — Frasier is middle-aged and his
# warehouse is the warehouse, not a parkour course.
#
# Default controls:
#   WASD / arrow keys · move
#   mouse             · look
#   shift             · slower (careful) walk
#   space             · (reserved · for sitting at the workbench)
#   esc               · release mouse capture
# ════════════════════════════════════════════════════════════════

extends CharacterBody3D

@export var walk_speed: float = 2.2      # meters per second (slow)
@export var careful_speed: float = 1.0   # held-shift speed
@export var mouse_sensitivity: float = 0.0025
@export var eye_height: float = 1.65     # Frasier's eye-height above the floor

const GRAVITY: float = 9.8

var camera: Camera3D
var pitch: float = 0.0


func _ready() -> void:
    # Position the camera at eye height if not already set
    camera = get_node_or_null("Camera3D")
    if camera and camera.position.y < 0.01:
        camera.position.y = eye_height
    Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)


func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
        rotate_y(-event.relative.x * mouse_sensitivity)
        if camera:
            pitch -= event.relative.y * mouse_sensitivity
            pitch = clamp(pitch, -PI / 2.2, PI / 2.2)
            camera.rotation.x = pitch
    elif event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
        if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
            Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
        else:
            Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)


func _physics_process(delta: float) -> void:
    # Movement input
    var input_vec := Vector3.ZERO
    if Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP):
        input_vec.z -= 1.0
    if Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN):
        input_vec.z += 1.0
    if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT):
        input_vec.x -= 1.0
    if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT):
        input_vec.x += 1.0

    var speed: float = careful_speed if Input.is_key_pressed(KEY_SHIFT) else walk_speed
    var direction: Vector3 = (transform.basis * input_vec).normalized() * speed

    velocity.x = direction.x
    velocity.z = direction.z

    if not is_on_floor():
        velocity.y -= GRAVITY * delta

    move_and_slide()
