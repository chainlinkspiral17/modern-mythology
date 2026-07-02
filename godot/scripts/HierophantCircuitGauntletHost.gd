# HierophantCircuitGauntletHost.gd
# ════════════════════════════════════════════════════════════════
# Host script wiring the Tarot Gauntlet for THE HIEROPHANT into
# Paul's Sunday circuit · three scenarios spanning two physical
# stops in this GLB plus the riverboat (for Sunday brunch):
#   st_judes_morning      · church steps + long black car at curb
#   sunday_brunch         · Table 17 (riverboat — host swaps GLB)
#   the_bandstand_calls   · park bandstand + John Frank's bench
#
# Board-space positions match build_hierophant_circuit.py geometry.
# ════════════════════════════════════════════════════════════════
extends Node3D

@export var player_path: NodePath = NodePath("../Player")
@export var auto_position_on_ready: bool = true
@export var launch_scene_path: String = "res://scenes/games/TarotGauntletGame.tscn"
@export var default_scenario_id: String = "st_judes_morning"

const EYE_HEIGHT_CAMERA: float = 1.65

# Board-space ID → (Blender X, Blender Y, facing-yaw-degrees).
# The GLB contains two physical stops on a continuous ground plane:
# St. Jude's at the south end and the bandstand at the north end.
# Sunday brunch's Table 17 vantage lives in the riverboat GLB.
const SPACE_MAP := {
	# St. Jude's church + curb (south stop)
	"church_plaza":         [+0.00,  -4.00,  90.0],   # facing the steps
	"church_steps_top":     [+0.00,  -6.20,  90.0],
	"church_doors":         [+0.00,  -6.80,  90.0],
	"church_niche_W":       [-4.60,  -7.10,   0.0],
	"church_niche_E":       [+4.60,  -7.10, 180.0],
	"long_car_curb":        [-2.50,  -9.50,  90.0],   # at the car, facing the door
	"car_passenger_side":   [-1.00, -10.00,  90.0],
	"sidewalk_west":        [-6.00,  -8.30,   0.0],
	"sidewalk_east":        [+6.00,  -8.30, 180.0],
	# Connecting path
	"path_south":           [+0.00,  +2.00,  90.0],
	"path_mid":             [+0.00,  +8.00,  90.0],
	# Park bandstand (north stop)
	"bandstand_path":       [+0.00, +12.00,  90.0],
	"bandstand_steps":      [+0.00, +14.20,  90.0],
	"bandstand_stage":      [+0.00, +18.00,  90.0],
	"bandstand_west":       [-3.00, +18.00,   0.0],
	"bandstand_east":       [+3.00, +18.00, 180.0],
	"john_franks_bench":    [-2.40, +14.00,   0.0],   # facing east, John writing
	"bench_north":          [-2.40, +15.20, 180.0],   # near the bench
}

var _player: CharacterBody3D = null
var _game: Node = null


func _ready() -> void:
	_player = get_node_or_null(player_path) as CharacterBody3D
	if _player == null or not is_instance_valid(_player):
		push_warning("[HierophantCircuitGauntletHost] Player path '%s' not found" % player_path)
	if auto_position_on_ready:
		position_player_at("church_plaza")


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var k := event as InputEventKey
		if k.keycode == KEY_F12 and k.ctrl_pressed:
			launch_hierophant_scenario()


func position_player_at(space_id: String) -> void:
	if _player == null or not is_instance_valid(_player):
		return
	var entry: Variant = SPACE_MAP.get(space_id, null)
	if entry == null:
		push_warning("[HierophantCircuitGauntletHost] Unknown space: %s" % space_id)
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


func launch_hierophant_scenario() -> void:
	if _game != null and is_instance_valid(_game):
		print("[HierophantCircuitGauntletHost] Gauntlet already running.")
		return
	var ps: PackedScene = load(launch_scene_path) as PackedScene
	if ps == null:
		push_warning("[HierophantCircuitGauntletHost] Could not load %s" % launch_scene_path)
		return
	_game = ps.instantiate()
	get_tree().root.add_child(_game)
	if _game.has_method("start_scenario"):
		_game.start_scenario("hierophant", "the_hierophant_circuit", "tbd_hierophant",
		                     default_scenario_id, true)
	if _game.has_signal("game_ended"):
		_game.connect("game_ended",
		              Callable(self, "_on_gauntlet_ended"))


func _on_gauntlet_ended(outcome: String, summary: Dictionary) -> void:
	print("[%s] gauntlet ended · outcome=%s · summary=%s" % [get_script().resource_path.get_file().get_basename(), outcome, summary])
	if _game != null and is_instance_valid(_game):
		_game.queue_free()
	_game = null
	position_player_at("church_plaza")
