# ParishCemeteryGauntletHost.gd
# ════════════════════════════════════════════════════════════════
# Host script that wires the Tarot Gauntlet for JUDGEMENT
# (Ensemble — dust notes — Everyone Stays) into
# parish_cemetery.tscn. Sister to DinerGauntletHost +
# CathedralGauntletHost + BungalowGauntletHost +
# RiverboatGauntletHost.
#
# Board-space positions match build_parish_cemetery.py geometry.
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
	"central_mausoleum": [+0.00, +0.00, 270.0],
	"path_spine_n":      [+0.00, +5.00, 270.0],
	"path_spine_s":      [+0.00, -5.00,  90.0],
	"vault_row_w":       [-7.00, +0.00,   0.0],
	"vault_row_e":       [+7.00, +0.00, 180.0],
	"vault_row_n":       [+0.00, +7.00, 270.0],
	"lamp_central":      [+1.20, +0.00, 180.0],
	"oak_sw":            [-8.50, -8.00,   0.0],
	"gate":              [+0.00, -9.00,  90.0],
}

var _player: CharacterBody3D = null
var _game: Node = null


func _ready() -> void:
	_player = get_node_or_null(player_path) as CharacterBody3D
	if _player == null or not is_instance_valid(_player):
		push_warning("[ParishCemeteryGauntletHost] Player path '%s' not found" % player_path)
	if auto_position_on_ready:
		position_player_at("central_mausoleum")


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var k := event as InputEventKey
		if k.ctrl_pressed:
			if k.keycode == KEY_F9:
				launch_the_quiet_committal()
			elif k.keycode == KEY_F10:
				launch_the_family_plot_visit()
			elif k.keycode == KEY_F11:
				launch_the_reading_of_the_hard_names()
			elif k.keycode == KEY_F12:
				launch_everyone_stays()


# ── Public API ───────────────────────────────────────────────────
func position_player_at(space_id: String) -> void:
	if _player == null or not is_instance_valid(_player):
		return
	var entry: Variant = SPACE_MAP.get(space_id, null)
	if entry == null:
		push_warning("[ParishCemeteryGauntletHost] Unknown space: %s" % space_id)
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


func launch_everyone_stays() -> void:
	_launch_scenario("judgement", "parish_cemetery", "tbd_judgement",
	                 "everyone_stays", true)


func launch_the_family_plot_visit() -> void:
	_launch_scenario("judgement", "parish_cemetery", "tbd_judgement",
	                 "the_family_plot_visit", false)


func launch_the_reading_of_the_hard_names() -> void:
	_launch_scenario("judgement", "parish_cemetery", "tbd_judgement",
	                 "the_reading_of_the_hard_names", true)


func launch_the_quiet_committal() -> void:
	# Different arcana at this same location · death.the_quiet_committal
	# is a Death scenario that takes place here at parish_cemetery.
	_launch_scenario("death", "parish_cemetery", "tbd_death",
	                 "the_quiet_committal", true)


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
	position_player_at("central_mausoleum")
