# BungalowGauntletHost.gd
# ════════════════════════════════════════════════════════════════
# Host script that wires the Tarot Gauntlet for the PRIESTESS
# (Elicia Duchane scenarios — "The Choose-Your-Own Adventure
# Episode") into bungalow.tscn. Sister to DinerGauntletHost +
# CathedralGauntletHost.
#
# The bungalow's board has 10 STATION spaces (living room, studio,
# editing desk, bookshelf, kitchen, bedroom, bathroom, storage
# closet, porch, back yard) + 3 THRESHOLD spaces (front door,
# back gate, roof). Positions match build_bungalow.py geometry.
#
# Coordinate frame: Blender Y-forward → Godot -Z. SPACE_MAP is in
# Blender frame; we convert at the call site via position_player_at.
# ════════════════════════════════════════════════════════════════
extends Node3D

@export var player_path: NodePath = NodePath("../Player")
@export var auto_position_on_ready: bool = true
@export var launch_scene_path: String = "res://scenes/games/TarotGauntletGame.tscn"

const EYE_HEIGHT: float = 1.65

# Board-space ID → (Blender X, Blender Y, facing-yaw-degrees).
# Yaw: 0=+X east, 90=+Y north, 180=-X west, 270=-Y south.
const SPACE_MAP := {
	# 10 station spaces from elicia_bungalow.json
	"living_room":        [-0.5,  +1.6,  90.0],   # facing north into the room
	"the_studio":         [+2.8,  +2.4, 180.0],   # facing the mic boom
	"the_editing_desk":   [+3.7,  +1.3,  90.0],   # CHOOSE-YOUR-OWN ADVENTURE start
	"the_bookshelf":      [+0.6,  +2.6,   0.0],   # facing the shelves (east)
	"the_kitchen":        [+2.5,  +4.2,  90.0],   # facing the counter
	"the_bedroom":        [-3.0,  +4.0,  90.0],   # facing the bed
	"the_bathroom":       [-3.4,  +0.8, 180.0],   # facing the mirror (west)
	"the_storage_closet": [+0.4,  +1.6,  90.0],   # facing the PH boxes
	"the_porch":          [+0.0,  -1.2, 270.0],   # facing the street (south)
	"the_back_yard":      [+0.0,  +8.0,  90.0],   # facing the back fence (north)
	# 3 threshold spaces
	"front_door":         [+0.0,  -0.6,  90.0],   # just inside the front door
	"back_gate":          [-4.4,  +9.4,  90.0],   # at the back gate, facing north
	"roof":               [+1.0,  +2.0,  90.0],   # NOTE: roof is at Y=+3.2 in Godot
}

var _player: CharacterBody3D = null
var _game: Node = null


func _ready() -> void:
	_player = get_node_or_null(player_path) as CharacterBody3D
	if _player == null:
		push_warning("[BungalowGauntletHost] Player path '%s' not found" % player_path)
	if auto_position_on_ready:
		# Priestess scenario opens at the editing desk — Elicia at
		# the laptop, the timeline waiting for the first cut.
		position_player_at("the_editing_desk")


func _input(event: InputEvent) -> void:
	# Ctrl+F12 launches the Priestess scenario inside the bungalow.
	if event is InputEventKey and event.pressed and not event.echo:
		var k := event as InputEventKey
		if k.keycode == KEY_F12 and k.ctrl_pressed:
			launch_choose_your_own_adventure()


# ── Public API ───────────────────────────────────────────────────
func position_player_at(space_id: String) -> void:
	if _player == null:
		return
	var entry: Variant = SPACE_MAP.get(space_id, null)
	if entry == null:
		push_warning("[BungalowGauntletHost] Unknown space: %s" % space_id)
		return
	var b_x: float = entry[0]
	var b_y: float = entry[1]
	var yaw_deg: float = entry[2]
	# Blender X → Godot X; Blender Y → Godot -Z
	var gx: float = b_x
	var gz: float = -b_y
	# Roof is the only station with a non-floor Y — pin to roof Z
	# height so the player stands on the flat roof.
	var gy: float = 0.0
	if space_id == "roof":
		gy = 3.20  # matches build_bungalow.py ROOF_Z
	var t := _player.global_transform
	t.origin = Vector3(gx, gy, gz)
	_player.global_transform = t
	# godot_yaw_deg = 90 - blender_yaw_deg (see DinerGauntletHost
	# for the derivation).
	var godot_yaw_deg: float = 90.0 - yaw_deg
	_player.rotation = Vector3(0.0, deg_to_rad(godot_yaw_deg), 0.0)


func sync_player_to_space(space_id: String) -> void:
	position_player_at(space_id)


func launch_choose_your_own_adventure() -> void:
	if _game != null and is_instance_valid(_game):
		print("[BungalowGauntletHost] Gauntlet already running.")
		return
	var ps: PackedScene = load(launch_scene_path) as PackedScene
	if ps == null:
		push_warning("[BungalowGauntletHost] Could not load %s" % launch_scene_path)
		return
	_game = ps.instantiate()
	get_tree().root.add_child(_game)
	if _game.has_method("start_scenario"):
		_game.start_scenario("2_priestess", "elicia_bungalow", "elicia_temple",
		                     "choose_your_own_adventure", true)
	if _game.has_signal("game_ended"):
		_game.connect("game_ended",
		              Callable(self, "_on_gauntlet_ended"))


func _on_gauntlet_ended(_outcome: String, _summary: Dictionary) -> void:
	if _game != null and is_instance_valid(_game):
		_game.queue_free()
	_game = null
	position_player_at("the_editing_desk")
