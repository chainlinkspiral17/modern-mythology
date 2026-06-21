# DinerGauntletHost.gd
# ════════════════════════════════════════════════════════════════
# Host script that wires the Tarot Gauntlet for the FOOL (THE LEAP)
# into the diner.tscn 3D scene. Owns:
#
#  · A 24-space board → 3D position map (each game-board space ID
#    from godot/resources/games/locations/dambrosios.json mapped
#    to actual Blender coordinates in the diner.glb world).
#  · A scenario-opener placement: when the scene loads, positions
#    the Player at the canonical opening vantage (the counter at
#    3:47 AM, holding a rag, looking north into the dining floor).
#  · A debug key (F12) to launch TarotGauntletGame.tscn with the
#    "the_leap" scenario inside the diner overlay. The existing
#    GalleryOverlay launch path is the proven harness; we mirror
#    its boot sequence here.
#  · A sync hook (call sync_player_to_space() from outside) so
#    the gauntlet's planning-phase walk action can teleport the
#    FPC body to match the new board space.
#
# Coordinate frame: Blender Y-forward → Godot -Z. We store positions
# in Blender frame and convert at the call site (helper _b2g()).
# ════════════════════════════════════════════════════════════════
extends Node3D

@export var player_path: NodePath = NodePath("../Player")
@export var auto_position_on_ready: bool = true
@export var launch_scene_path: String = "res://scenes/games/TarotGauntletGame.tscn"

# Eye height above the floor (matches FirstPersonController.eye_height)
const EYE_HEIGHT: float = 1.65

# Board-space ID → (Blender X, Blender Y, facing-yaw-degrees).
# Facing-yaw 0 = +X east, 90 = +Y north, 180 = -X west, 270 = -Y south.
# Positions chosen by reading dambrosios.json space adjacency + the
# actual 3D geometry in build_diner.py (counter at Y=-3.5, alcove
# booths at X=-7.95 etc.). When in doubt the camera faces the room's
# OPEN side so the player can see the gauntlet's relevant geometry.
const SPACE_MAP := {
	"parking_lot":    [+12.0,  +0.0, 180.0],   # outside east, facing west
	"hostess_stand":  [+7.6,   -0.5, 180.0],   # vestibule, facing west
	"back_door":      [-7.5,   -5.5,  90.0],   # south kitchen exit, facing north
	"bar":            [-12.0,  +4.5, 270.0],   # west-ext bar, facing south
	"booth_1":        [-7.95,  +3.75, 0.0],    # north alcove booth, facing east
	"kitchen_alcove": [-6.0,   -5.0,  90.0],
	"grill":          [-4.75,  -5.55, 90.0],   # galley grill, facing north
	"dish_station":   [+4.0,   -5.55, 90.0],   # galley sink, facing north
	"order_window":   [-5.5,   -3.95, 90.0],   # counter pass-through
	"booth_4":        [-7.95,  +0.75,  0.0],
	"booth_6":        [-7.95,  -2.25,  0.0],   # river-window booth — the Stranger spawn
	"counter":        [+0.0,   -2.65, 90.0],   # canonical THE LEAP start
	"bar_stools":     [-10.5,  +3.5, 270.0],
	"under_counter":  [+0.0,   -3.5,  90.0],
	"jukebox":        [-10.5,  +5.0,  90.0],
	"bell":           [-4.5,   -3.5,  90.0],
	"pay_phone":      [+2.32,  +7.27, 180.0],
	"cig_machine":    [+2.32,  +7.5,  180.0],
	"register":       [-3.6,   -3.5,  90.0],
	"bathroom":       [+7.0,   -4.7,  90.0],
	"card_wall":      [+0.0,   +8.28, 270.0],  # facing south, reading the cards
	"river_window":   [-15.0,  +0.0,   0.0],   # at the new port-side picture window
	"precipice_door": [+1.20,  +8.4,  90.0],   # hidden door at back of hallway
}

var _player: CharacterBody3D = null
var _game: Node = null


func _ready() -> void:
	_player = get_node_or_null(player_path) as CharacterBody3D
	if _player == null or not is_instance_valid(_player):
		push_warning("[DinerGauntletHost] Player path '%s' not found" % player_path)
	if auto_position_on_ready:
		# Scene opens on the canonical THE LEAP vantage. If a real
		# gauntlet game is launched later it will reposition us; until
		# then, the diner feels lived-in from the moment of entry.
		position_player_at("counter")


func _input(event: InputEvent) -> void:
	# F12 launches THE LEAP from inside the diner (handy during
	# development). Avoid clobbering MoodCycler's F12 (style pack)
	# by guarding on Ctrl: Ctrl+F12 launches.
	if event is InputEventKey and event.pressed and not event.echo:
		var k := event as InputEventKey
		if k.keycode == KEY_F12 and k.ctrl_pressed:
			launch_the_leap()


# ── Public API ───────────────────────────────────────────────────
func position_player_at(space_id: String) -> void:
	# Move the FPC body + spin the camera to face the right direction
	# for the named board space. Idempotent.
	if _player == null or not is_instance_valid(_player):
		return
	var entry: Variant = SPACE_MAP.get(space_id, null)
	if entry == null:
		push_warning("[DinerGauntletHost] Unknown space: %s" % space_id)
		return
	var b_x: float = entry[0]
	var b_y: float = entry[1]
	var yaw_deg: float = entry[2]
	# Blender X → Godot X (preserved); Blender Y → Godot -Z (forward
	# axis flip from glTF Y-up conversion).
	var gx: float = b_x
	var gz: float = -b_y
	# Player origin is at floor level; capsule local is offset 0.85
	# so visible "feet" land on Z=0. The Camera3D inside is at
	# Y=eye_height. We just place the Player at floor level.
	var t := _player.global_transform
	t.origin = Vector3(gx, 0.0, gz)
	_player.global_transform = t
	# Yaw the FPC body. The Player's transform.basis (a Y rotation)
	# determines initial facing — FPC.rotate_y handles user input
	# afterward.
	#
	# Convention mapping:
	#   Blender yaw 0   (face +X / east)  → Godot rotation -π/2 (-90°)
	#   Blender yaw 90  (face +Y / north) → Godot rotation 0
	#   Blender yaw 180 (face -X / west)  → Godot rotation +π/2 (+90°)
	#   Blender yaw 270 (face -Y / south) → Godot rotation π    (180°)
	# Conversion:  godot_yaw_deg = 90 - blender_yaw_deg
	var godot_yaw_deg: float = 90.0 - yaw_deg
	_player.rotation = Vector3(0.0, deg_to_rad(godot_yaw_deg), 0.0)


func sync_player_to_space(space_id: String) -> void:
	# Called by gauntlet logic when the player completes a Walk
	# action and moves to a new board space. Same as
	# position_player_at(), but kept as a separate name so it's
	# clear in the caller that this is gameplay-driven, not a
	# scene-init placement.
	position_player_at(space_id)


# ── 3D FP camera vantage (for the gauntlet's per-space FP view) ──
# Returns a Dictionary the gauntlet uses to position a SubViewport
# camera that shares this host's World3D. Letting the gauntlet render
# the actual 3D diner geometry from each space's vantage replaces
# the painted-PNG fallback the FP mode used to rely on.
# Returns {} for unknown spaces (caller falls back to top-down map).
func get_fp_camera_for_space(space_id: String) -> Dictionary:
	var entry: Variant = SPACE_MAP.get(space_id, null)
	if entry == null:
		return {}
	var b_x: float = entry[0]
	var b_y: float = entry[1]
	var yaw_deg: float = entry[2]
	# Blender → Godot frame.
	# Camera convention NOTE: position_player_at uses
	# "godot_yaw_deg = 90 - blender_yaw" because the FPC body's
	# forward is +Z. Camera3D's default forward is -Z (Godot's
	# canonical camera-looks-down-negative-Z) — that's the
	# OPPOSITE direction, so the camera rotation is reversed:
	#   godot_camera_yaw_deg = blender_yaw_deg - 90
	# Yields:
	#   blender 0   (face east +X)  → -90°  → camera looks +X ✓
	#   blender 90  (face north +Y) →   0°  → camera looks -Z ✓
	#   blender 180 (face west -X)  → +90°  → camera looks -X ✓
	#   blender 270 (face south -Y) → +180° → camera looks +Z ✓
	var gx: float = b_x
	var gz: float = -b_y
	var godot_yaw_deg: float = yaw_deg - 90.0
	return {
		"origin":   Vector3(gx, EYE_HEIGHT, gz),
		"rotation": Vector3(-0.05, deg_to_rad(godot_yaw_deg), 0.0),
		"fov":      62.0,
	}


func launch_the_leap() -> void:
	# Spawn the gauntlet game on top of the diner scene. Reuses
	# the existing TarotGauntletGame.tscn boot path; the gauntlet
	# overlay renders on a CanvasLayer above the 3D, so the player
	# sees the gauntlet UI with the diner faint behind it.
	if _game != null and is_instance_valid(_game):
		print("[DinerGauntletHost] Gauntlet already running.")
		return
	var ps: PackedScene = load(launch_scene_path) as PackedScene
	if ps == null:
		push_warning("[DinerGauntletHost] Could not load %s" % launch_scene_path)
		return
	_game = ps.instantiate()
	get_tree().root.add_child(_game)
	if _game.has_method("start_scenario"):
		_game.start_scenario("0_fool", "dambrosios", "john_frank",
		                     "the_leap", true)
	# Mirrors the GalleryOverlay.gd launch pattern — signal is
	# `game_ended(outcome, summary)`.
	if _game.has_signal("game_ended"):
		_game.connect("game_ended",
		              Callable(self, "_on_gauntlet_ended"))


func _on_gauntlet_ended(_outcome: String, _summary: Dictionary) -> void:
	if _game != null and is_instance_valid(_game):
		_game.queue_free()
	_game = null
	# Reset the player to the canonical opening vantage when the
	# gauntlet ends.
	position_player_at("counter")
