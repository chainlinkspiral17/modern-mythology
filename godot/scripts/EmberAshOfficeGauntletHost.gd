# EmberAshOfficeGauntletHost.gd
# ════════════════════════════════════════════════════════════════
# Host script wiring the Tarot Gauntlet for THE CHARIOT into
# Antonio's office above the Lacombe garage · three scenarios:
# hot_office / option_four / two_horses_one_wreck.
#
# Board-space positions match build_ember_ash_office.py geometry.
# ════════════════════════════════════════════════════════════════
extends Node3D

@export var player_path: NodePath = NodePath("../Player")
@export var auto_position_on_ready: bool = true
@export var launch_scene_path: String = "res://scenes/games/TarotGauntletGame.tscn"
@export var default_scenario_id: String = "hot_office"

const EYE_HEIGHT_CAMERA: float = 1.65

# Board-space ID → (Blender X, Blender Y, facing-yaw-degrees).
const SPACE_MAP := {
	"desk":            [-0.50, 3.20, 270.0],   # at the desk, facing south
	"chair":           [-0.50, 3.95,  90.0],   # in Antonio's chair, facing the desk
	"bourbon":         [-0.20, 3.30, 270.0],   # at the bottle on the desk
	"rotary_phone":    [-1.05, 3.10, 270.0],   # at the phone on the desk
	"voicemail":       [-0.80, 3.02, 270.0],   # at the voicemail counter
	"ac_window":       [+0.00, 0.40,  90.0],   # at the south wall AC
	"corner_across":   [+2.40, 2.40, 180.0],   # at the east window
	"back_stair":      [-2.40, 1.00,   0.0],   # at the back stair opening
	"crew_photo":      [-0.50, 4.90, 270.0],   # at the wall photo
	"door":            [+0.00, 4.80,  90.0],   # office door (north)
	"cypress_beam":    [+0.00, 2.60,  90.0],   # under the cypress beam
}

var _player: CharacterBody3D = null
var _game: Node = null


func _ready() -> void:
	_player = get_node_or_null(player_path) as CharacterBody3D
	if _player == null or not is_instance_valid(_player):
		push_warning("[EmberAshOfficeGauntletHost] Player path '%s' not found" % player_path)
	if auto_position_on_ready:
		position_player_at("desk")


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var k := event as InputEventKey
		if k.keycode == KEY_F12 and k.ctrl_pressed:
			launch_chariot_scenario()


func position_player_at(space_id: String) -> void:
	if _player == null or not is_instance_valid(_player):
		return
	var entry: Variant = SPACE_MAP.get(space_id, null)
	if entry == null:
		push_warning("[EmberAshOfficeGauntletHost] Unknown space: %s" % space_id)
		return
	var b_x: float = entry[0]
	var b_y: float = entry[1]
	var yaw_deg: float = entry[2]
	var t := _player.global_transform
	t.origin = Vector3(b_x, 0.0, -b_y)
	_player.global_transform = t
	var godot_yaw_deg: float = 90.0 - yaw_deg
	_player.rotation = Vector3(0.0, deg_to_rad(godot_yaw_deg), 0.0)


func sync_player_to_space(space_id: String) -> void:
	position_player_at(space_id)


func get_fp_camera_for_space(space_id: String) -> Dictionary:
	var entry: Variant = SPACE_MAP.get(space_id, null)
	if entry == null:
		return {}
	var b_x: float = entry[0]
	var b_y: float = entry[1]
	var yaw_deg: float = entry[2]
	var godot_yaw_deg: float = yaw_deg - 90.0
	return {
		"origin":   Vector3(b_x, EYE_HEIGHT_CAMERA, -b_y),
		"rotation": Vector3(-0.05, deg_to_rad(godot_yaw_deg), 0.0),
		"fov":      62.0,
	}


func launch_chariot_scenario() -> void:
	if _game != null and is_instance_valid(_game):
		print("[EmberAshOfficeGauntletHost] Gauntlet already running.")
		return
	var ps: PackedScene = load(launch_scene_path) as PackedScene
	if ps == null:
		push_warning("[EmberAshOfficeGauntletHost] Could not load %s" % launch_scene_path)
		return
	_game = ps.instantiate()
	get_tree().root.add_child(_game)
	if _game.has_method("start_scenario"):
		_game.start_scenario("chariot", "ember_ash_office", "tbd_chariot",
		                     default_scenario_id, true)
	if _game.has_signal("game_ended"):
		_game.connect("game_ended",
		              Callable(self, "_on_gauntlet_ended"))


func _on_gauntlet_ended(outcome: String, summary: Dictionary) -> void:
	print("[%s] gauntlet ended · outcome=%s · summary=%s" % [get_script().resource_path.get_file().get_basename(), outcome, summary])
	if _game != null and is_instance_valid(_game):
		_game.queue_free()
	_game = null
	position_player_at("desk")
