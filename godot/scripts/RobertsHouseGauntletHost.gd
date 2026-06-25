# RobertsHouseGauntletHost.gd
# ════════════════════════════════════════════════════════════════
# Host script wiring the Tarot Gauntlet for THE LOVERS into the
# Roberts house · the_faucet_wins / he_waved / today_the_drip_can_win.
#
# Board-space positions match build_roberts_house.py geometry.
# Camera-yaw convention: blender_yaw - 90 (Camera3D forward -Z,
# opposite of FPC body's +Z).
# ════════════════════════════════════════════════════════════════
extends Node3D

@export var player_path: NodePath = NodePath("../Player")
@export var auto_position_on_ready: bool = true
@export var launch_scene_path: String = "res://scenes/games/TarotGauntletGame.tscn"
@export var default_scenario_id: String = "the_faucet_wins"

const EYE_HEIGHT_CAMERA: float = 1.65

# Board-space ID → (Blender X, Blender Y, facing-yaw-degrees).
const SPACE_MAP := {
	"front_porch":     [+0.00,  -1.00, 270.0],   # on the porch facing the door
	"front_door":      [+1.50,   0.20,  90.0],   # just inside the front door
	"front_hallway":   [+1.50,   0.80,  90.0],
	"hall_table":      [+0.40,   0.60, 180.0],   # at the Polaroid
	"phone_niche":     [-0.50,   0.10,   0.0],   # at the wall phone
	"living_couch":    [-2.50,   2.40, 270.0],   # facing the picture window
	"coffee_table":    [-2.50,   1.50,  90.0],
	"side_chair":      [-0.60,   2.40, 180.0],
	"kitchen_table":   [+2.50,   2.20,   0.0],
	"kitchen_sink":    [+3.00,   5.60,  90.0],   # at the drip faucet
	"casserole":       [+2.50,   2.30, 270.0],   # over the kitchen table
	"back_porch":      [-2.00,   6.40,   0.0],
	"bedroom_door":    [-3.00,   4.00,  90.0],
	"front_yard":      [+0.00,  -3.50, 270.0],   # walkway between porch + sidewalk
	"curb":            [-1.00,  -6.50,   0.0],   # at Mrs. Theriot's parking spot
	"back_yard_fence": [+3.20,   8.40,  90.0],   # at the bird-on-the-wire
}

var _player: CharacterBody3D = null
var _game: Node = null


func _ready() -> void:
	_player = get_node_or_null(player_path) as CharacterBody3D
	if _player == null or not is_instance_valid(_player):
		push_warning("[RobertsHouseGauntletHost] Player path '%s' not found" % player_path)
	if auto_position_on_ready:
		position_player_at("kitchen_sink")


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var k := event as InputEventKey
		if k.keycode == KEY_F12 and k.ctrl_pressed:
			launch_lovers_scenario()


# ── Public API ───────────────────────────────────────────────────
func position_player_at(space_id: String) -> void:
	if _player == null or not is_instance_valid(_player):
		return
	var entry: Variant = SPACE_MAP.get(space_id, null)
	if entry == null:
		push_warning("[RobertsHouseGauntletHost] Unknown space: %s" % space_id)
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


func launch_lovers_scenario() -> void:
	if _game != null and is_instance_valid(_game):
		print("[RobertsHouseGauntletHost] Gauntlet already running.")
		return
	var ps: PackedScene = load(launch_scene_path) as PackedScene
	if ps == null:
		push_warning("[RobertsHouseGauntletHost] Could not load %s" % launch_scene_path)
		return
	_game = ps.instantiate()
	get_tree().root.add_child(_game)
	if _game.has_method("start_scenario"):
		_game.start_scenario("lovers", "roberts_house", "tbd_lovers",
		                     default_scenario_id, true)
	if _game.has_signal("game_ended"):
		_game.connect("game_ended",
		              Callable(self, "_on_gauntlet_ended"))


func _on_gauntlet_ended(outcome: String, summary: Dictionary) -> void:
	print("[%s] gauntlet ended · outcome=%s · summary=%s" % [get_script().resource_path.get_file().get_basename(), outcome, summary])
	if _game != null and is_instance_valid(_game):
		_game.queue_free()
	_game = null
	position_player_at("kitchen_sink")
