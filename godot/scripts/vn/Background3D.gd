# Background3D.gd
# ════════════════════════════════════════════════════════════════
# Controller for Background3D.tscn — a SubViewport-backed VN bg
# that loads a location scene (diner.tscn, riverfront.tscn) into
# its own World3D and frames an establishing-shot Camera3D per a
# named preset.
#
# Public API:
#   load_location(location_id: String)
#       location_id is a key into CAMERA_PRESETS below. Loads the
#       matching scene into LocationAnchor and positions the
#       Background3D's own Camera3D for the establishing shot.
#       Drop-in: subsequent calls swap the location seamlessly.
#
#   get_viewport_texture() -> Texture2D
#       Convenience accessor used by GameEngine when wrapping this
#       node inside the bg TextureRect.
# ════════════════════════════════════════════════════════════════
extends SubViewportContainer

# Each preset specifies:
#   scene          : res:// path of the location to instantiate
#   camera_origin  : Vector3 in the location's world coords
#                    (Godot frame — X right, Y up, Z-forward = into
#                     the scene; remember Blender Y north = Godot -Z)
#   camera_rotation: Vector3 of euler radians (rotates the camera)
#   fov            : optional override (degrees)
#   suppress_input : if true, the location's interactable Player
#                    node is removed so it doesn't compete for
#                    input or move while the VN bg is on screen
const CAMERA_PRESETS := {
	"diner_interior": {
		"scene": "res://scenes/locales/diner.tscn",
		"requires_glb": "res://assets/3d/locales/diner.glb",
		# At the front door looking west into the dining floor.
		"camera_origin": Vector3(7.5, 1.95, 0.0),
		"camera_rotation": Vector3(-0.08, deg_to_rad(-90.0), 0.0),
		"fov": 60.0,
		"suppress_input": true,
	},
	"diner_exterior_porch": {
		"scene": "res://scenes/locales/diner.tscn",
		"requires_glb": "res://assets/3d/locales/diner.glb",
		# Standing on the new portside porch, looking south down the
		# riverboat hull.
		"camera_origin": Vector3(-16.5, 2.20, -2.0),
		"camera_rotation": Vector3(-0.05, deg_to_rad(160.0), 0.0),
		"fov": 65.0,
		"suppress_input": true,
	},
	"riverfront_exterior": {
		"scene": "res://scenes/locales/riverfront.tscn",
		"requires_glb": "res://assets/3d/locales/riverfront.glb",
		# Wide establishing shot from across the river.
		"camera_origin": Vector3(-30.0, 4.5, 6.0),
		"camera_rotation": Vector3(-0.10, deg_to_rad(75.0), 0.0),
		"fov": 42.0,
		"suppress_input": true,
	},
}

const BG_W: int = 1280
const BG_H: int = 720

@onready var _viewport: SubViewport = $SubViewport
@onready var _anchor: Node3D = $SubViewport/LocationAnchor
@onready var _camera: Camera3D = $SubViewport/Camera3D

var _loaded_preset: String = ""
var _location_instance: Node = null


func _ready() -> void:
	custom_minimum_size = Vector2(BG_W, BG_H)


# ── Public API ────────────────────────────────────────────────────
func load_location(preset_id: String) -> bool:
	if preset_id == _loaded_preset and _location_instance != null:
		return true
	if not CAMERA_PRESETS.has(preset_id):
		push_warning("[Background3D] Unknown preset: %s" % preset_id)
		return false
	var spec: Dictionary = CAMERA_PRESETS[preset_id]
	# Pre-check the required GLB BEFORE asking Godot to parse the
	# .tscn — locale .glb files are build artifacts (not committed),
	# so a fresh checkout that hasn't run the Blender builders yet
	# will hit a parse-error cascade if we let the .tscn load. The
	# explicit check turns it into a single actionable warning.
	var req_glb: String = spec.get("requires_glb", "")
	if req_glb != "" and not FileAccess.file_exists(req_glb):
		push_warning("[Background3D] GLB missing: %s — build it with `cd godot/tools/blender && ./run_cathedral.sh build_<name>.py`. Falling back to 2D bg." % req_glb)
		return false
	# Tear down the previously-loaded location
	if _location_instance != null and is_instance_valid(_location_instance):
		_location_instance.queue_free()
	_location_instance = null
	# Load + instantiate the new location
	var ps: PackedScene = load(spec.get("scene", "")) as PackedScene
	if ps == null:
		push_warning("[Background3D] Could not load scene %s" % spec.get("scene", ""))
		return false
	_location_instance = ps.instantiate()
	# CRITICAL: suppress interactive nodes BEFORE adding to tree.
	# Once added, every script in the locale's _ready cascade caches
	# references to the Player / HUD / etc — and the queue_free that
	# follows turns those caches into "previously freed" errors every
	# frame, eventually freezing the engine. Detaching pre-attach
	# means the doomed children's _ready never fires.
	if spec.get("suppress_input", false):
		_suppress_interactive_nodes(_location_instance)
	_anchor.add_child(_location_instance)
	# Position our SubViewport's own Camera3D + make it the current
	# camera for the World3D. The location's own Camera3D node (if
	# any) is overridden because make_current() pushes onto the
	# camera stack.
	_camera.position = spec.get("camera_origin", Vector3.ZERO)
	_camera.rotation = spec.get("camera_rotation", Vector3.ZERO)
	if spec.has("fov"):
		_camera.fov = float(spec["fov"])
	_camera.make_current()
	_loaded_preset = preset_id
	return true


func get_viewport_texture() -> Texture2D:
	return _viewport.get_texture()


# ── Internal ─────────────────────────────────────────────────────
func _suppress_interactive_nodes(root: Node) -> void:
	# Recursively kill any Player CharacterBody3D + any CanvasLayer
	# named HUD/PostProcess. We keep the world lights, the geometry,
	# and the WorldEnvironment — that's what we want to render.
	# Called BEFORE the locale instance is added to the SceneTree so
	# the removed nodes' scripts never get _ready'd and so other
	# scripts in the locale don't cache references to them.
	var to_remove: Array[Node] = []
	for n: Node in _walk_tree(root):
		if n is CharacterBody3D and n.is_in_group("player"):
			to_remove.append(n)
		elif n is CanvasLayer:
			to_remove.append(n)
	for n in to_remove:
		var parent: Node = n.get_parent()
		if parent != null:
			parent.remove_child(n)
		n.queue_free()


func _walk_tree(node: Node, out: Array[Node] = []) -> Array[Node]:
	out.append(node)
	for child in node.get_children():
		_walk_tree(child, out)
	return out
