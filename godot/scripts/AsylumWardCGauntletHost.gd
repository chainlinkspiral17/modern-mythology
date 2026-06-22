# AsylumWardCGauntletHost.gd
# ════════════════════════════════════════════════════════════════
# Host script that wires the Tarot Gauntlet for DEATH
# (Ward C — Walpurgisnacht — Walpurgisnacht) into
# asylum_ward_c.tscn. Sister to DinerGauntletHost +
# CathedralGauntletHost + BungalowGauntletHost +
# RiverboatGauntletHost.
#
# Board-space positions match build_asylum_ward_c.py geometry.
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
	"nurses_station": [+0.00, +7.00,  90.0],
	"ward_1":         [-2.40, +1.40,   0.0],
	"ward_2":         [-2.40, +3.80,   0.0],
	"ward_3":         [-2.40, +6.20,   0.0],
	"ward_4":         [-2.40, +8.60,   0.0],
	"ward_5":         [-2.40, +11.00,   0.0],
	"gurney":         [+0.40, +11.00, 180.0],
	"wheelchair":     [-1.20, +1.50,  90.0],
	"cupola_below":   [+0.00, +13.20,  90.0],
	"corridor_s":     [+0.00, +0.40,  90.0],
}

var _player: CharacterBody3D = null
var _game: Node = null


func _ready() -> void:
	_player = get_node_or_null(player_path) as CharacterBody3D
	if _player == null or not is_instance_valid(_player):
		push_warning("[AsylumWardCGauntletHost] Player path '%s' not found" % player_path)
	if auto_position_on_ready:
		position_player_at("nurses_station")


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var k := event as InputEventKey
		if k.keycode == KEY_F12 and k.ctrl_pressed:
			launch_walpurgisnacht()


# ── Public API ───────────────────────────────────────────────────
func position_player_at(space_id: String) -> void:
	if _player == null or not is_instance_valid(_player):
		return
	var entry: Variant = SPACE_MAP.get(space_id, null)
	if entry == null:
		push_warning("[AsylumWardCGauntletHost] Unknown space: %s" % space_id)
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


func launch_walpurgisnacht() -> void:
	if _game != null and is_instance_valid(_game):
		print("[AsylumWardCGauntletHost] Gauntlet already running.")
		return
	var ps: PackedScene = load(launch_scene_path) as PackedScene
	if ps == null:
		push_warning("[AsylumWardCGauntletHost] Could not load %s" % launch_scene_path)
		return
	_game = ps.instantiate()
	get_tree().root.add_child(_game)
	if _game.has_method("start_scenario"):
		_game.start_scenario("death", "asylum_ward_c", "tbd_death",
		                     "walpurgisnacht", true)
	if _game.has_signal("game_ended"):
		_game.connect("game_ended",
		              Callable(self, "_on_gauntlet_ended"))


func _on_gauntlet_ended(_outcome: String, _summary: Dictionary) -> void:
	if _game != null and is_instance_valid(_game):
		_game.queue_free()
	_game = null
	position_player_at("nurses_station")
