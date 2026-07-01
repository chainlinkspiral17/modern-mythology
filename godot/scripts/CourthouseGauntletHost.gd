# CourthouseGauntletHost.gd
# ════════════════════════════════════════════════════════════════
# Host script that wires the Tarot Gauntlet for JUSTICE
# (Erica + Anna — Motion to Dismiss) into
# courthouse_chamber.tscn. Sister to DinerGauntletHost +
# CathedralGauntletHost + BungalowGauntletHost +
# RiverboatGauntletHost.
#
# Board-space positions match build_courthouse_chamber.py geometry.
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
	"judge_bench":     [+0.00, +9.80, 270.0],
	"witness_stand":   [+2.40, +9.60, 180.0],
	"jury_box":        [-3.70, +6.00,   0.0],
	"plaintiff_table": [-1.50, +5.50,  90.0],
	"defense_table":   [+1.50, +5.50,  90.0],
	"pew_front":       [+0.00, +1.50,  90.0],
	"bar_rail":        [+0.00, +4.20,  90.0],
	"flag_us":         [+3.20, +11.40, 180.0],
	"flag_state":      [-3.20, +11.40,   0.0],
	"rear_door":       [+0.00, +0.40,  90.0],
}

var _player: CharacterBody3D = null
var _game: Node = null


func _ready() -> void:
	_player = get_node_or_null(player_path) as CharacterBody3D
	if _player == null or not is_instance_valid(_player):
		push_warning("[CourthouseGauntletHost] Player path '%s' not found" % player_path)
	if auto_position_on_ready:
		position_player_at("plaintiff_table")


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var k := event as InputEventKey
		if k.ctrl_pressed:
			if k.keycode == KEY_F8:
				open_scenario_picker()
				return
			if k.keycode == KEY_F10:
				launch_chambers_at_nine()
			elif k.keycode == KEY_F11:
				launch_post_decision_review()
			elif k.keycode == KEY_F12:
				launch_motion_to_dismiss()


# ── Public API ───────────────────────────────────────────────────
func position_player_at(space_id: String) -> void:
	if _player == null or not is_instance_valid(_player):
		return
	var entry: Variant = SPACE_MAP.get(space_id, null)
	if entry == null:
		push_warning("[CourthouseGauntletHost] Unknown space: %s" % space_id)
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


func launch_motion_to_dismiss() -> void:
	_launch_scenario("justice", "courthouse_chamber", "tbd_justice",
	                 "motion_to_dismiss", true)


func launch_chambers_at_nine() -> void:
	_launch_scenario("justice", "courthouse_chamber", "tbd_justice",
	                 "chambers_at_nine", false)


func launch_post_decision_review() -> void:
	_launch_scenario("justice", "courthouse_chamber", "tbd_justice",
	                 "post_decision_review", true)


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



func open_scenario_picker() -> void:
	# Ctrl+F8 opens a UI picker so players who don't know the F10/F11
	# keybinds can discover the bookend scenarios. F10/F11/F12 remain
	# as direct-launch keybinds for the fast path.
	var existing: Node = get_node_or_null("ScenarioPicker")
	if existing != null and is_instance_valid(existing):
		return
	var picker_script := load("res://scenes/menu/ScenarioPicker.gd")
	if picker_script == null:
		return
	var picker: Control = picker_script.new()
	picker.name = "ScenarioPicker"
	add_child(picker)
	var entries: Array = [
		{"launch_fn": Callable(self, "launch_chambers_at_nine"), "title": "CHAMBERS AT NINE", "subtitle": "Graustark Parish Courthouse · 8:48 AM · Erica's chambers · the morning before the motion", "difficulty": "easy"},
		{"launch_fn": Callable(self, "launch_motion_to_dismiss"), "title": "MOTION TO DISMISS", "subtitle": "Graustark Parish Courthouse · 9:14 AM · Department 3", "difficulty": "medium"},
		{"launch_fn": Callable(self, "launch_post_decision_review"), "title": "POST-DECISION REVIEW", "subtitle": "Graustark Parish Courthouse · Department 3 · 11:18 AM · three weeks after the motion was denied", "difficulty": "hard"},
	]
	picker.present(entries)


func _on_gauntlet_ended(outcome: String, summary: Dictionary) -> void:
	print("[%s] gauntlet ended · outcome=%s · summary=%s" % [get_script().resource_path.get_file().get_basename(), outcome, summary])
	if _game != null and is_instance_valid(_game):
		_game.queue_free()
	_game = null
	position_player_at("plaintiff_table")
