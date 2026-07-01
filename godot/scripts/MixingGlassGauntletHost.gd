# MixingGlassGauntletHost.gd
# ════════════════════════════════════════════════════════════════
# Host script that wires the Tarot Gauntlet for TEMPERANCE
# (Frank — Tuesday observation — Tuesday Observation) into
# mixing_glass.tscn. Sister to DinerGauntletHost +
# CathedralGauntletHost + BungalowGauntletHost +
# RiverboatGauntletHost.
#
# Board-space positions match build_mixing_glass.py geometry.
# Camera-yaw convention: blender_yaw - 90 (Camera3D forward -Z,
# opposite of FPC body's +Z).
# ════════════════════════════════════════════════════════════════
extends Node3D

@export var player_path: NodePath = NodePath("../Player")
@export var auto_position_on_ready: bool = true
@export var launch_scene_path: String = "res://scenes/games/TarotGauntletGame.tscn"

const EYE_HEIGHT_CAMERA: float = 2.30

# Board-space ID → (Blender X, Blender Y, facing-yaw-degrees).
# Yaw: 0=+X east, 90=+Y north, 180=-X west, 270=-Y south.
const SPACE_MAP := {
	"bar_stool_mid": [+1.05, +5.60,   0.0],
	"bar_stool_w":   [-1.05, +5.60, 180.0],
	"backbar":       [+0.00, +8.40, 270.0],
	"booth_1":       [-1.60, +1.20,   0.0],
	"booth_2":       [-1.60, +3.00,   0.0],
	"booth_3":       [-1.60, +4.80,   0.0],
	"booth_4":       [-1.60, +6.60,   0.0],
	"neon_open":     [-1.40, +7.80, 270.0],
	"alley_door":    [+0.00, +0.40,  90.0],
}

var _player: CharacterBody3D = null
var _game: Node = null


func _ready() -> void:
	_player = get_node_or_null(player_path) as CharacterBody3D
	if _player == null or not is_instance_valid(_player):
		push_warning("[MixingGlassGauntletHost] Player path '%s' not found" % player_path)
	if auto_position_on_ready:
		position_player_at("bar_stool_mid")


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var k := event as InputEventKey
		if k.ctrl_pressed:
			if k.keycode == KEY_F10:
				launch_pre_shift_setup()
			elif k.keycode == KEY_F11:
				launch_last_call_friday()
			elif k.keycode == KEY_F12:
				launch_tuesday_observation()


# ── Public API ───────────────────────────────────────────────────
func position_player_at(space_id: String) -> void:
	if _player == null or not is_instance_valid(_player):
		return
	var entry: Variant = SPACE_MAP.get(space_id, null)
	if entry == null:
		push_warning("[MixingGlassGauntletHost] Unknown space: %s" % space_id)
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


# Per-space 3D FP camera vantage. See DinerGauntletHost docstring.
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


func launch_tuesday_observation() -> void:
	_launch_scenario("temperance", "mixing_glass", "tbd_temperance",
	                 "tuesday_observation", true)


func launch_pre_shift_setup() -> void:
	_launch_scenario("temperance", "mixing_glass", "tbd_temperance",
	                 "pre_shift_setup", false)


func launch_last_call_friday() -> void:
	_launch_scenario("temperance", "mixing_glass", "tbd_temperance",
	                 "last_call_friday", true)


func _launch_scenario(arcana_id: String, location_id: String,
                      hand_id: String, scenario_id: String,
                      reversed: bool) -> void:
	if _game != null and is_instance_valid(_game):
		print("[%s] Gauntlet already running." % get_script().resource_path.get_file().get_basename())
		return
	var ps: PackedScene = load(launch_scene_path) as PackedScene
	if ps == null:
		push_warning("[%s] Could not load %s" % [get_script().resource_path.get_file().get_basename(), launch_scene_path])
		return
	_game = ps.instantiate()
	get_tree().root.add_child(_game)
	if _game.has_method("start_scenario"):
		_game.start_scenario(arcana_id, location_id, hand_id,
		                     scenario_id, reversed)
	if _game.has_signal("game_ended"):
		_game.connect("game_ended",
		              Callable(self, "_on_gauntlet_ended"))


func _on_gauntlet_ended(outcome: String, summary: Dictionary) -> void:
	print("[%s] gauntlet ended · outcome=%s · summary=%s" % [get_script().resource_path.get_file().get_basename(), outcome, summary])
	if _game != null and is_instance_valid(_game):
		_game.queue_free()
	_game = null
	position_player_at("bar_stool_mid")
