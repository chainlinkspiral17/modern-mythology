# RiverboatGauntletHost.gd
# ════════════════════════════════════════════════════════════════
# Host script for the Tarot Gauntlet inside the D'Ambrosio's
# riverboat interior. Canonically shared by THREE arcana scenarios
# (per riverboat_interior.json notes):
#
#   · The Empress (Nicola, maitre d' — "THE FLOOR HOLDS")
#   · The Emperor (Dante, helm — "THE LEDGER CLOSED")
#   · The Hierophant (Paul at Table 17, one scenario)
#
# Each reframes the same 13-station + 3-threshold board. The
# Ctrl+F12 launcher defaults to the EMPRESS scenario; future
# Emperor / Hierophant launches can override.
#
# Coordinate frame: Blender Y-forward → Godot -Z. SPACE_MAP holds
# (Blender X, Blender Y, Blender Z, facing-yaw-degrees). The Z
# component is needed because this is a multi-deck building —
# upper-deck stations sit at UPPER_FLOOR_Z, lower-deck stations
# at LOWER_FLOOR_Z, main-deck at MAIN_FLOOR_Z (per
# build_riverboat_interior.py).
# ════════════════════════════════════════════════════════════════
extends Node3D

@export var player_path: NodePath = NodePath("../Player")
@export var auto_position_on_ready: bool = true
@export var launch_scene_path: String = "res://scenes/games/TarotGauntletGame.tscn"

const EYE_HEIGHT: float = 1.65
# Deck floor heights (Blender Z, matches build_riverboat_interior.py)
const LOWER_FLOOR_Z: float = 0.00
const MAIN_FLOOR_Z:  float = 2.50
const UPPER_FLOOR_Z: float = 5.10

# Board-space ID → (Blender X, Blender Y, Blender floor-Z,
# facing-yaw-degrees). Facing-yaw 0=+X east, 90=+Y north,
# 180=-X west, 270=-Y south.
const SPACE_MAP := {
	# ─── UPPER DECK ─────────────────────────────────────────────
	"helm":               [0.0,   -2.4, UPPER_FLOOR_Z, 90.0],   # facing leaded window N
	"office_staircase":   [+3.0,  -3.0, UPPER_FLOOR_Z, 270.0],  # at top of stair
	# ─── MAIN DECK ──────────────────────────────────────────────
	"maitre_d_stand":     [0.0,   -8.5, MAIN_FLOOR_Z,  90.0],   # facing dining room N
	"main_dining_room":   [-1.0,  -3.0, MAIN_FLOOR_Z,  90.0],   # facing N
	"private_dining":     [-4.0,  +3.0, MAIN_FLOOR_Z,  90.0],   # facing the table
	"table_17":           [-4.5,  -0.7, MAIN_FLOOR_Z, 180.0],   # facing the deepest window W
	"sammys_bar":         [+3.5,  0.0,  MAIN_FLOOR_Z,  0.0],    # facing the back bar E
	"the_pass":           [+1.5,  +5.0, MAIN_FLOOR_Z,  90.0],   # facing the kitchen N
	"kitchen":            [0.0,   +8.0, MAIN_FLOOR_Z,  90.0],   # facing the line N
	# ─── LOWER DECK ─────────────────────────────────────────────
	"back_corridor":      [0.0,   +6.0, LOWER_FLOOR_Z, 270.0],  # facing the doors S
	"catering_office":    [-4.5,  -1.5, LOWER_FLOOR_Z,  0.0],   # facing the file cabinet E (actually -X for the cab)
	"the_card_room":      [-1.0,  -1.0, LOWER_FLOOR_Z,  90.0],  # facing the table center
	"the_back_room":      [+2.5,  -1.0, LOWER_FLOOR_Z,  90.0],  # facing the table center
	"staff_locker_room":  [+4.5,  -1.0, LOWER_FLOOR_Z,  0.0],   # facing the lockers E
	# ─── THRESHOLDS ─────────────────────────────────────────────
	"side_door":          [+5.6,  -3.0, MAIN_FLOOR_Z,  0.0],    # facing E to step out
	"staff_exit":         [+5.0,  -5.0, LOWER_FLOOR_Z, 270.0],  # facing S
	"gangway":            [0.0,   -11.0, MAIN_FLOOR_Z, 270.0],  # at the boat door, facing dock
}

var _player: CharacterBody3D = null
var _game: Node = null


func _ready() -> void:
	_player = get_node_or_null(player_path) as CharacterBody3D
	if _player == null or not is_instance_valid(_player):
		push_warning("[RiverboatGauntletHost] Player path '%s' not found" % player_path)
	if auto_position_on_ready:
		# Empress scenarios open at the MAÎTRE D' STAND — Nicola's
		# friday-night post.
		position_player_at("maitre_d_stand")


func _input(event: InputEvent) -> void:
	# Ctrl+F12 launches the Empress scenario.
	if event is InputEventKey and event.pressed and not event.echo:
		var k := event as InputEventKey
		if k.keycode == KEY_F12 and k.ctrl_pressed:
			launch_floor_holds()


# ── Public API ───────────────────────────────────────────────────
func position_player_at(space_id: String) -> void:
	if _player == null or not is_instance_valid(_player):
		return
	var entry: Variant = SPACE_MAP.get(space_id, null)
	if entry == null:
		push_warning("[RiverboatGauntletHost] Unknown space: %s" % space_id)
		return
	var b_x: float = entry[0]
	var b_y: float = entry[1]
	var b_z: float = entry[2]
	var yaw_deg: float = entry[3]
	# Blender X → Godot X; Blender Y → Godot -Z; Blender Z → Godot Y
	var gx: float = b_x
	var gz: float = -b_y
	var gy: float = b_z
	var t := _player.global_transform
	t.origin = Vector3(gx, gy, gz)
	_player.global_transform = t
	var godot_yaw_deg: float = 90.0 - yaw_deg
	_player.rotation = Vector3(0.0, deg_to_rad(godot_yaw_deg), 0.0)


func sync_player_to_space(space_id: String) -> void:
	position_player_at(space_id)


# Per-space 3D FP camera vantage. See DinerGauntletHost docstring.
# Riverboat is the ONLY 4-element host — entries are
#   [blender_x, blender_y, floor_z, yaw_deg]
# because the boat has three decks (upper / main / lower) at
# different Y heights in Godot frame. Camera Y in Godot frame =
# floor_z + EYE_HEIGHT_CAMERA so the vantage sits at standing
# eye-level above whatever deck the space belongs to.
func get_fp_camera_for_space(space_id: String) -> Dictionary:
	var entry: Variant = SPACE_MAP.get(space_id, null)
	if entry == null:
		return {}
	var b_x: float = entry[0]
	var b_y: float = entry[1]
	var floor_z: float = entry[2]   # deck height (UPPER/MAIN/LOWER_FLOOR_Z)
	var yaw_deg: float = entry[3]
	# Camera yaw = blender_yaw - 90 (Camera3D forward -Z, NOT body
	# +Z). See DinerGauntletHost for the full convention table.
	var godot_yaw_deg: float = yaw_deg - 90.0
	return {
		"origin":   Vector3(b_x, floor_z + 2.30, -b_y),
		"rotation": Vector3(-0.05, deg_to_rad(godot_yaw_deg), 0.0),
		"fov":      62.0,
	}


func launch_floor_holds() -> void:
	# Default launcher → the Empress beat at the maître d' stand.
	# Canonical authored scenario: empress/setup_static_bloom.json
	# (Friday dinner service, the "THE FLOOR HOLDS" beat from the
	# original launcher name).
	_launch_with_args("3_empress", "riverboat_interior",
	                  "nicola", "static_bloom")


func launch_ledger_closed() -> void:
	# Emperor scenario (Dante at the helm).
	# Canonical authored scenario: emperor/setup_the_friday_helm.json.
	_launch_with_args("4_emperor", "riverboat_interior",
	                  "dante_dambrosio", "the_friday_helm")


func _launch_with_args(arcana: String, location: String,
                       hero: String, scenario: String) -> void:
	if _game != null and is_instance_valid(_game):
		print("[RiverboatGauntletHost] Gauntlet already running.")
		return
	var ps: PackedScene = load(launch_scene_path) as PackedScene
	if ps == null:
		push_warning("[RiverboatGauntletHost] Could not load %s" % launch_scene_path)
		return
	_game = ps.instantiate()
	get_tree().root.add_child(_game)
	if _game.has_method("start_scenario"):
		_game.start_scenario(arcana, location, hero, scenario, true)
	if _game.has_signal("game_ended"):
		_game.connect("game_ended",
		              Callable(self, "_on_gauntlet_ended"))


func _on_gauntlet_ended(_outcome: String, _summary: Dictionary) -> void:
	if _game != null and is_instance_valid(_game):
		_game.queue_free()
	_game = null
	position_player_at("maitre_d_stand")
