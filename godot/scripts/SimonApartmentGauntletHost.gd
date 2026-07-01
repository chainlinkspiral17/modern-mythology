# SimonApartmentGauntletHost.gd
# ════════════════════════════════════════════════════════════════
# Host script that wires the Tarot Gauntlet for THE HANGED MAN
# (Natalie — at Simon's — After Simon) into
# simon_apartment.tscn. Sister to DinerGauntletHost +
# CathedralGauntletHost + BungalowGauntletHost +
# RiverboatGauntletHost.
#
# Board-space positions match build_simon_apartment.py geometry.
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
	"armchair":     [+0.50, +2.40, 180.0],
	"bed":          [+1.40, +5.70, 180.0],
	"kitchenette":  [-1.80, +2.40,   0.0],
	"tv":           [-0.50, +2.20,   0.0],
	"tipped_chair": [-1.20, +3.20,  90.0],
	"hanging_boot": [-2.30, +5.50,   0.0],
	"front_window": [+0.00, +0.80, 270.0],
	"front_door":   [+1.80, +0.40,  90.0],
}

var _player: CharacterBody3D = null
var _game: Node = null


func _ready() -> void:
	_player = get_node_or_null(player_path) as CharacterBody3D
	if _player == null or not is_instance_valid(_player):
		push_warning("[SimonApartmentGauntletHost] Player path '%s' not found" % player_path)
	if auto_position_on_ready:
		position_player_at("armchair")


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var k := event as InputEventKey
		if k.ctrl_pressed:
			if k.keycode == KEY_F8:
				open_scenario_picker()
				return
			if k.keycode == KEY_F10:
				launch_the_seventh_evening()
			elif k.keycode == KEY_F11:
				launch_the_first_night()
			elif k.keycode == KEY_F12:
				launch_after_simon()


# ── Public API ───────────────────────────────────────────────────
func position_player_at(space_id: String) -> void:
	if _player == null or not is_instance_valid(_player):
		return
	var entry: Variant = SPACE_MAP.get(space_id, null)
	if entry == null:
		push_warning("[SimonApartmentGauntletHost] Unknown space: %s" % space_id)
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


func launch_after_simon() -> void:
	_launch_scenario("hanged_man", "simon_apartment", "tbd_hanged_man",
	                 "after_simon", true)


func launch_the_seventh_evening() -> void:
	_launch_scenario("hanged_man", "simon_apartment", "tbd_hanged_man",
	                 "the_seventh_evening", false)


func launch_the_first_night() -> void:
	_launch_scenario("hanged_man", "simon_apartment", "tbd_hanged_man",
	                 "the_first_night", true)


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
		{"launch_fn": Callable(self, "launch_the_seventh_evening"), "title": "THE SEVENTH EVENING", "subtitle": "Simon's apartment · 7:14 PM · one week later · the lease is up in ten days", "difficulty": "easy"},
		{"launch_fn": Callable(self, "launch_after_simon"), "title": "AFTER SIMON", "subtitle": "Simon's apartment · 9:43 PM · the third evening", "difficulty": "medium"},
		{"launch_fn": Callable(self, "launch_the_first_night"), "title": "THE FIRST NIGHT", "subtitle": "Simon's apartment · 11:14 PM Sunday · seven hours after the call", "difficulty": "hard"},
	]
	picker.present(entries)


func _on_gauntlet_ended(outcome: String, summary: Dictionary) -> void:
	print("[%s] gauntlet ended · outcome=%s · summary=%s" % [get_script().resource_path.get_file().get_basename(), outcome, summary])
	if _game != null and is_instance_valid(_game):
		_game.queue_free()
	_game = null
	position_player_at("armchair")
