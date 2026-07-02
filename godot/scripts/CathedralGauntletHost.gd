# CathedralGauntletHost.gd
# ════════════════════════════════════════════════════════════════
# Host script that wires the Tarot Gauntlet for the MAGICIAN
# (Frasier scenarios) into cathedral.tscn. Sister to
# DinerGauntletHost.gd — same shape, different map.
#
# The cathedral is "the whole tarot built into the floor": all 22
# arcana have a physical station marker (see build_gauntlet_stations
# in build_cathedral_interior.py). This file is the bridge between
# the abstract board-space IDs in resources/games/locations/
# cathedral.json and the actual Blender coordinates of the 22 floor
# zones.
#
# Coordinate frame: Blender Y-forward → Godot -Z. Positions stored
# in Blender frame; converted at the call site (helper _b2g()).
# ════════════════════════════════════════════════════════════════
extends Node3D

@export var player_path: NodePath = NodePath("../Player")
@export var auto_position_on_ready: bool = true
@export var launch_scene_path: String = "res://scenes/games/TarotGauntletGame.tscn"

# Eye height above the floor (matches FirstPersonController.eye_height)
const EYE_HEIGHT: float = 1.65

# Board-space ID → (Blender X, Blender Y, facing-yaw-degrees).
# Facing-yaw 0 = +X east, 90 = +Y north, 180 = -X west, 270 = -Y south.
#
# Positions pulled directly from build_cathedral_interior.py
# _zone_marker() calls. The facing-yaw is the direction the player
# naturally LOOKS while standing at the station — usually toward the
# zone's central prop (workbench, corkboard, pool, etc.).
const SPACE_MAP := {
	# Threshold stations (cathedral.json kind:"threshold")
	"warehouse_bay":  [+0.0,  +9.0, 270.0],   # bay door, facing south into the room
	"river_window":   [-11.5, +0.0,   0.0],   # west wall picture window, facing east
	"roof_hatch":     [+0.0,  +0.0,  90.0],   # central, facing up (yaw arbitrary)
	# 22 Major Arcana stations (cathedral.json kind:"named")
	"magician":       [+0.0,  -3.0,  90.0],   # WORKBENCH — Magician scenario START
	"fool":           [-4.0,  +5.5, 270.0],   # diner mini, facing south to read trim
	"priestess":      [-7.0,  +5.5, 270.0],   # cassette cabinet on N wall, facing S
	"empress":        [-6.0,  +7.5, 270.0],   # corkboard on N wall, facing S
	"emperor":        [-3.0,  +7.0, 270.0],   # Dante's chair
	"hierophant":     [-10.5, +3.0,   0.0],   # west wall altar, facing east
	"lovers":         [+4.0,  +5.5, 270.0],   # Briar Falls WIP
	"chariot":        [+5.0,  +2.0, 180.0],   # truck cab plinth
	"strength":       [-4.0,  +4.0,  90.0],   # press, facing north
	"hermit":         [+0.6,  -3.4,  90.0],   # BBS terminal at workbench corner
	"wheel":          [-6.0,  -2.0,  90.0],   # Harmony Creek WIP
	"justice":        [-8.5,  -1.5,   0.0],   # ledger, facing east
	"hanged_man":     [-3.0,  -2.0,  90.0],   # Montreal WIP
	"death":          [-7.5,  -7.0,  90.0],   # mask shelf, facing north
	"temperance":     [+5.0,  -3.0, 180.0],   # copper still
	"devil":          [+8.0,  -5.0, 180.0],   # the empty bar stool — DEMON spawn
	"tower":          [+6.0,  -2.0,  90.0],   # Sharp's Club WIP
	"star":           [-5.0,  -3.0,  90.0],   # cold LED rig
	"moon":           [-4.0,  -6.0,  90.0],   # reflecting pool, facing north
	"sun":            [+2.0,  -7.0,  90.0],   # sodium-vapor lamp + chair
	"judgement":      [-1.5,  -7.0,  90.0],   # blank stage
	"world":          [+10.0, +0.0, 180.0],   # wireframe globe armature
}

var _player: CharacterBody3D = null
var _game: Node = null


func _ready() -> void:
	_player = get_node_or_null(player_path) as CharacterBody3D
	if _player == null or not is_instance_valid(_player):
		push_warning("[CathedralGauntletHost] Player path '%s' not found" % player_path)
	if auto_position_on_ready:
		# Magician scenarios open at the WORKBENCH (the central object
		# of the location — Frasier's everyday vantage). Walking the
		# board moves us around the warehouse via sync_player_to_space.
		position_player_at("magician")


func _input(event: InputEvent) -> void:
	# Ctrl+F12 launches a Magician scenario from inside the cathedral
	# (handy during development). Avoid clobbering MoodCycler's F12
	# (style pack) by guarding on Ctrl.
	if event is InputEventKey and event.pressed and not event.echo:
		var k := event as InputEventKey
		if k.keycode == KEY_F12 and k.ctrl_pressed:
			launch_watch_party()


# ── Public API ───────────────────────────────────────────────────
func position_player_at(space_id: String) -> void:
	# Move the FPC body + spin the camera to face the right direction
	# for the named board space. Idempotent.
	if _player == null or not is_instance_valid(_player):
		return
	var entry: Variant = SPACE_MAP.get(space_id, null)
	if entry == null:
		push_warning("[CathedralGauntletHost] Unknown space: %s" % space_id)
		return
	var b_x: float = entry[0]
	var b_y: float = entry[1]
	var yaw_deg: float = entry[2]
	# Blender X → Godot X (preserved); Blender Y → Godot -Z.
	var gx: float = b_x
	var gz: float = -b_y
	var t := _player.global_transform
	t.origin = Vector3(gx, 0.0, gz)
	_player.global_transform = t
	# Yaw conversion: godot_yaw_deg = 90 - blender_yaw_deg (see
	# DinerGauntletHost for the derivation).
	var godot_yaw_deg: float = 90.0 - yaw_deg
	_player.rotation = Vector3(0.0, deg_to_rad(godot_yaw_deg), 0.0)


func sync_player_to_space(space_id: String) -> void:
	# Called by gauntlet logic when the player completes a Walk
	# action and moves to a new board space. Same as
	# position_player_at(), but kept as a separate name so callers
	# can tell scene-init placements apart from gameplay moves.
	position_player_at(space_id)


# Per-space 3D FP camera vantage. TarotGauntletGame queries this
# to render the cathedral's live geometry into the gauntlet panel
# via a shared-world SubViewport — first-person perspective for
# every Magician-scenario board space.
func get_fp_camera_for_space(space_id: String) -> Dictionary:
	var entry: Variant = SPACE_MAP.get(space_id, null)
	if entry == null:
		return {}
	var b_x: float = entry[0]
	var b_y: float = entry[1]
	var yaw_deg: float = entry[2]
	# Camera yaw formula = blender_yaw - 90 (NOT the FPC body's
	# 90 - blender_yaw — Camera3D's default forward is -Z, opposite
	# of the body's +Z forward). See DinerGauntletHost for the
	# full convention table.
	var gx: float = b_x
	var gz: float = -b_y
	var godot_yaw_deg: float = yaw_deg - 90.0
	return {
		"origin":   Vector3(gx, 2.30, gz),     # user-confirmed eye height
		"rotation": Vector3(-0.05, deg_to_rad(godot_yaw_deg), 0.0),
		"fov":      62.0,
	}


func launch_watch_party() -> void:
	# Spawn the gauntlet game on top of the cathedral scene. Uses
	# the same boot path as the diner's THE LEAP launch.
	# Default Magician scenario for ch1 is WATCH PARTY (the easy
	# entry point — the harder gravity decks come later).
	if _game != null and is_instance_valid(_game):
		print("[CathedralGauntletHost] Gauntlet already running.")
		return
	var ps: PackedScene = load(launch_scene_path) as PackedScene
	if ps == null:
		push_warning("[CathedralGauntletHost] Could not load %s" % launch_scene_path)
		return
	_game = ps.instantiate()
	get_tree().root.add_child(_game)
	if _game.has_method("start_scenario"):
		# hand_id "frasier" matches resources/games/hands/frasier.json
		# (not "frasier_temple" — that's the character GLB name).
		_game.start_scenario("1_magician", "cathedral", "frasier",
		                     "watch_party", true)
	if _game.has_signal("game_ended"):
		_game.connect("game_ended",
		              Callable(self, "_on_gauntlet_ended"))


func _on_gauntlet_ended(outcome: String, summary: Dictionary) -> void:
	print("[%s] gauntlet ended · outcome=%s · summary=%s" % [get_script().resource_path.get_file().get_basename(), outcome, summary])
	if _game != null and is_instance_valid(_game):
		_game.queue_free()
	_game = null
	# Reset to the canonical opening vantage when the gauntlet ends.
	position_player_at("magician")
