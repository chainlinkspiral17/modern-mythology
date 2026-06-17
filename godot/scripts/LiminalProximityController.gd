# LiminalProximityController.gd
# ════════════════════════════════════════════════════════════════
# Drives the liminal_proximity.gdshader based on the player's
# distance to the nearest liminal-tagged station in the current
# location's gauntlet JSON.
#
# SINGLE SOURCE OF TRUTH — drift detection:
#   The location JSON (resources/games/locations/<id>.json) is the
#   authoritative source for which stations are liminal. Each
#   station may carry an optional "liminal_type" field with one of:
#       "show"        — part of someone's broadcast/blog/art
#                       (card_wall, the_studio, the_editing_desk,
#                       the_storage_closet)
#       "imagination" — imagined-but-not-visited place
#                       (cathedral WIPs)
#       "threshold"   — wall-thin between realities
#                       (precipice_door, the_back_room, table_17,
#                       the_bookshelf [mirror shard])
#   Additionally, stations with kind=="wip" are auto-inferred as
#   "imagination" (so future WIPs need no extra tagging).
#
#   The GauntletHost's SPACE_MAP is the authoritative source for
#   WORLD POSITIONS. This controller joins the two: for each space
#   that's liminal per JSON, look up its position in SPACE_MAP and
#   drive the shader.
#
#   At _ready() we run a drift check: every station_id that appears
#   in the JSON must also appear in the host's SPACE_MAP (and vice
#   versa). Mismatches are push_warning'd loudly so the next person
#   who runs the scene sees the drift.
#
#   To add a new liminal space:
#     1. Tag it in the location JSON.
#     2. Make sure it's in the host's SPACE_MAP (with a position).
#     That's all — no edits here.
# ════════════════════════════════════════════════════════════════
extends Node3D

@export var host_path:           NodePath
@export var player_path:         NodePath
@export var post_process_path:   NodePath
@export var location_json:       String = ""
# Distance (in metres) at which proximity strength = 1.0; falls off
# to 0 by `falloff_metres` past that. Tweak per locale if needed
# (bungalow is tight; riverboat sprawls).
@export var inner_metres:        float = 1.5
@export var falloff_metres:      float = 6.0
# How aggressively shader strength tracks distance. 1.0 = linear.
@export var strength_gamma:      float = 1.2
# Smoothing — strength doesn't snap, it lerps toward target so
# walking past a station doesn't pop the cue.
@export var smoothing:           float = 4.0

# Liminal-type → shader tint colour. The "show" tint is warm
# sodium (broadcast burnt-in feel), "imagination" is cool desat
# (unfinished), "threshold" is wrong-room cold blue.
const TINT_BY_TYPE := {
	"show":        Color(0.96, 0.78, 0.42, 1.0),
	"imagination": Color(0.62, 0.66, 0.74, 1.0),
	"threshold":   Color(0.32, 0.52, 0.74, 1.0),
}

# Built at _ready() from JSON + host SPACE_MAP:
#   [{pos: Vector3, type: String, id: String}, ...]
var _liminal_world: Array = []
var _strength: float = 0.0
var _target_type: String = "threshold"  # the type of the nearest active station
var _shader_mat: ShaderMaterial = null
var _player: CharacterBody3D = null


func _ready() -> void:
	_player = get_node_or_null(player_path) as CharacterBody3D
	if _player == null:
		push_warning("[LiminalProximity] Player path '%s' not found" % player_path)
		return
	var pp: CanvasLayer = get_node_or_null(post_process_path) as CanvasLayer
	if pp == null:
		push_warning("[LiminalProximity] PostProcess path '%s' not found" % post_process_path)
		return
	var quad: ColorRect = pp.get_node_or_null("LiminalQuad") as ColorRect
	if quad == null:
		push_warning("[LiminalProximity] LiminalQuad not found under PostProcess")
		return
	_shader_mat = quad.material as ShaderMaterial
	if _shader_mat == null:
		push_warning("[LiminalProximity] LiminalQuad has no ShaderMaterial")
		return

	_build_liminal_world()
	set_process(true)


func _build_liminal_world() -> void:
	# Load location JSON, find liminal-tagged spaces, look up their
	# world positions in the host's SPACE_MAP, and drift-check.
	var host: Node = get_node_or_null(host_path)
	if host == null:
		push_warning("[LiminalProximity] Host path '%s' not found"
			% host_path)
		return
	var space_map: Dictionary = host.get("SPACE_MAP") if "SPACE_MAP" in host \
		else {}
	if space_map.is_empty():
		push_warning("[LiminalProximity] Host has no SPACE_MAP")
		return

	if location_json == "" or not FileAccess.file_exists(location_json):
		push_warning("[LiminalProximity] location_json '%s' missing"
			% location_json)
		return
	var f := FileAccess.open(location_json, FileAccess.READ)
	var raw: String = f.get_as_text()
	f.close()
	var parsed: Variant = JSON.parse_string(raw)
	if typeof(parsed) != TYPE_DICTIONARY or not parsed.has("spaces"):
		push_warning("[LiminalProximity] '%s' is not a valid location JSON"
			% location_json)
		return

	var json_ids := {}
	for sp_v in parsed["spaces"]:
		var sp: Dictionary = sp_v as Dictionary
		var sid: String = sp.get("id", "")
		if sid == "":
			continue
		json_ids[sid] = true
		# Determine liminal type — explicit field overrides inference
		var ltype: String = sp.get("liminal_type", "")
		if ltype == "" and sp.get("kind", "") == "wip":
			ltype = "imagination"
		if ltype == "":
			continue
		if not space_map.has(sid):
			push_warning("[LiminalProximity] DRIFT — '%s' is liminal in %s but missing from host SPACE_MAP" % [sid, location_json])
			continue
		# SPACE_MAP entry is [bx, by, yaw] OR [bx, by, bz, yaw]
		var entry: Array = space_map[sid]
		var pos: Vector3 = _entry_to_world(entry)
		_liminal_world.append({"pos": pos, "type": ltype, "id": sid})

	# Reverse drift check — every SPACE_MAP key should be in JSON
	for sid in space_map.keys():
		if not json_ids.has(sid):
			push_warning("[LiminalProximity] DRIFT — host SPACE_MAP has '%s' but %s has no such space" % [sid, location_json])

	print("[LiminalProximity] %s · %d liminal spaces tracked"
		% [location_json.get_file(), _liminal_world.size()])


# Convert a SPACE_MAP entry to Godot world position.
# Bungalow/diner/cathedral entries are [bx, by, yaw]; riverboat is
# [bx, by, bz, yaw] (3-deck). Player y not relevant — we compare
# distance in xz plane only for the proximity calc, so the y here
# is approximate (used for visual debug if needed).
func _entry_to_world(entry: Array) -> Vector3:
	if entry.size() >= 4:
		# [bx, by, bz, yaw]
		return Vector3(entry[0], entry[2], -entry[1])
	# [bx, by, yaw]
	return Vector3(entry[0], 0.0, -entry[1])


func _process(delta: float) -> void:
	if _shader_mat == null:
		return
	# Find nearest liminal space in xz-plane
	var ppos: Vector3 = _player.global_transform.origin
	var nearest_d: float = INF
	var nearest_type: String = "threshold"
	for entry in _liminal_world:
		var dp: Vector3 = (entry["pos"] as Vector3) - ppos
		var d: float = sqrt(dp.x * dp.x + dp.z * dp.z)
		if d < nearest_d:
			nearest_d = d
			nearest_type = entry["type"]
	# Map distance → strength
	var target: float = 0.0
	if nearest_d < INF:
		if nearest_d <= inner_metres:
			target = 1.0
		elif nearest_d < inner_metres + falloff_metres:
			var t: float = (nearest_d - inner_metres) / falloff_metres
			target = pow(1.0 - t, strength_gamma)
	# Smooth the transition so it doesn't snap
	_strength = lerp(_strength, target, clamp(smoothing * delta, 0.0, 1.0))
	_target_type = nearest_type
	_shader_mat.set_shader_parameter("strength", _strength)
	# Tint follows the active type. We only swap the tint when the
	# strength is near zero so we don't flicker between colours
	# while crossing between two adjacent liminal stations.
	if _strength < 0.05:
		var tint: Color = TINT_BY_TYPE.get(
			_target_type, TINT_BY_TYPE["threshold"])
		_shader_mat.set_shader_parameter("tint_color", tint)
