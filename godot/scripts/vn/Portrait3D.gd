# Portrait3D.gd
# ════════════════════════════════════════════════════════════════
# Controller for Portrait3D.tscn — a SubViewport-backed VN portrait
# that renders a 3D character GLB to a ViewportTexture. CharLayer
# instantiates this scene when a matching GLB is available for the
# speaking character; otherwise it falls back to the existing
# PNG / ASCII-composition portrait path.
#
# Public API:
#   load_character(glb_path: String, expression: String = "")
#       Loads a GLB into CharacterAnchor; clears any previous load.
#       Re-runs the auto-orient + auto-scale heuristic the Graustark
#       hero placement uses, so heroes from different exporters
#       (Mixamo, Meshy, Ready Player Me) all frame consistently.
#
#   set_expression(expression: String)
#       Drives a per-mood camera + lighting + motion override on
#       top of the resting framing. Each mood has:
#           · camera position offset (zoom, side, tilt)
#           · key/fill light color + energy
#           · continuous motion (shake amplitude/frequency, bob
#             amplitude/frequency, drift)
#       See MOOD_TABLE below. Subtle by design — the goal is
#       'angry' reads as a tightening + tremor + warm-red light,
#       not a screen-pounding shake.
#
#   get_viewport_texture() -> ViewportTexture
#       Convenience accessor used by CharLayer when wrapping this
#       node inside a TextureRect.
# ════════════════════════════════════════════════════════════════
extends SubViewportContainer

const PORTRAIT_W: int = 300
const PORTRAIT_H: int = 320
const TARGET_HEIGHT_M: float = 1.80   # frame to roughly real-human

@onready var _viewport: SubViewport = $SubViewport
@onready var _anchor: Node3D = $SubViewport/CharacterAnchor
@onready var _placeholder: Node3D = $SubViewport/CharacterAnchor/Placeholder
@onready var _camera: Camera3D = $SubViewport/Camera3D
@onready var _key: DirectionalLight3D = $SubViewport/Key
@onready var _fill: DirectionalLight3D = $SubViewport/Fill
@onready var _back: DirectionalLight3D = $SubViewport/BackRim

var _loaded_glb_path: String = ""
var _current_character: Node3D = null

# Resting camera transform (read once at _ready), so per-mood
# offsets compose on top instead of accumulating
var _rest_cam_pos: Vector3
var _rest_cam_fov: float
var _rest_key_color: Color
var _rest_key_energy: float
var _rest_fill_color: Color
var _rest_fill_energy: float
var _rest_back_color: Color
var _rest_back_energy: float

# Active mood state — _process() reads these to animate
var _mood_id: String = "neutral"
var _mood: Dictionary = {}
var _mood_t: float = 0.0     # time since the mood was set (drives motion)

# Demon mode — when true, set_expression() routes to "demon_chaos"
# regardless of the requested expression (a demon doesn't perform
# moods, it leaks signal corruption), and the SubViewportContainer's
# portrait_demon_static shader gets pushed to strength=1.
var _demon_mode: bool = false

# ── Mood table ───────────────────────────────────────────────────
# Each mood entry is OPTIONAL — leaves missing keys mean "use rest
# value." Camera offsets are added to the resting transform; light
# tweaks REPLACE the resting color/energy when present.
#
#   pos_off      Vector3 added to resting camera position
#                (negative Z = closer to character / zoom in)
#   pitch_off    radians added to camera pitch
#   yaw_off      radians added to camera yaw
#   fov_off      degrees added to resting FOV (negative = zoom in)
#   key_color    Color to override key-light color
#   key_energy   float to override key-light energy
#   fill_color   ...
#   shake_amp    Vector3 amplitude in radians (camera rotational
#                jitter — small)
#   shake_freq   Hz; how fast the shake oscillates
#   bob_amp      meters; vertical positional sway amplitude
#   bob_freq     Hz; vertical sway frequency
#   drift_yaw    rad/sec; slow continuous yaw drift
#   sway_amp     radians; horizontal yaw sway amplitude
#   sway_freq    Hz
const MOOD_TABLE := {
	"neutral": {
		"pos_off":  Vector3(0, 0, -0.15),     # subtle zoom-in
		"fov_off":  -1.0,
		"key_color":  Color(0.74, 0.82, 0.96),
		"key_energy": 1.05,
		"bob_amp":  0.005, "bob_freq": 0.30,  # gentle breathing
	},
	"happy": {
		"pos_off":  Vector3(0, 0.04, -0.08),
		"key_color":  Color(0.98, 0.92, 0.74),   # warm boost
		"key_energy": 1.35,
		"fill_color": Color(1.00, 0.85, 0.58),
		"fill_energy": 0.70,
		"bob_amp":  0.020, "bob_freq": 0.60,  # bouncy
		"sway_amp": 0.012, "sway_freq": 0.35, # CCW/CW lilt
	},
	"sad": {
		"pos_off":  Vector3(0, -0.06, -0.05),
		"pitch_off": -0.05,
		"key_color":  Color(0.66, 0.78, 0.96),   # cooler
		"key_energy": 0.85,
		"fill_color": Color(0.62, 0.74, 0.88),
		"fill_energy": 0.38,
		"bob_amp":  0.004, "bob_freq": 0.20,  # slow droop
		"drift_yaw": -0.02,
	},
	"surprised": {
		"pos_off":  Vector3(0, 0, -0.25),     # snap zoom-in
		"fov_off":  -3.0,
		"key_color":  Color(0.92, 0.95, 1.00),
		"key_energy": 1.30,
		"shake_amp": Vector3(0.004, 0.004, 0),
		"shake_freq": 14.0,                   # quick jitter
	},
	"angry": {
		"pos_off":  Vector3(0.02, 0, -0.20),  # tight on the face
		"fov_off":  -2.0,
		"key_color":  Color(1.00, 0.62, 0.46),  # warm red wash
		"key_energy": 1.25,
		"fill_color": Color(0.92, 0.42, 0.34),
		"fill_energy": 0.55,
		"shake_amp": Vector3(0.0065, 0.0065, 0),
		"shake_freq": 22.0,                   # subtle "angry tremor"
	},
	"tired": {
		"pos_off":  Vector3(0, -0.08, -0.05),
		"pitch_off": -0.04,
		"key_color":  Color(0.70, 0.78, 0.92),
		"key_energy": 0.75,
		"fill_color": Color(0.62, 0.70, 0.84),
		"fill_energy": 0.35,
		"bob_amp":  0.010, "bob_freq": 0.14,  # slow heavy drift
	},
	"nervous": {
		"pos_off":  Vector3(-0.04, 0.02, -0.06),
		"key_color":  Color(0.88, 0.92, 1.00),
		"key_energy": 0.95,
		"shake_amp": Vector3(0.003, 0.003, 0),
		"shake_freq": 8.0,                    # tremor
		"sway_amp": 0.010, "sway_freq": 0.7,  # uneasy sway
	},
	# ── Demon ────────────────────────────────────────────────────
	# Auto-selected by set_demon_mode(). Pairs with the digital-
	# static shader overlay (portrait_demon_static.gdshader) for
	# the "high-energy chaos" read — the camera does the spatial
	# unease, the shader does the signal corruption.
	"demon_chaos": {
		"pos_off":  Vector3(0.0, 0.0, -0.10),  # subtle zoom-in
		"fov_off":  -1.5,
		"key_color":  Color(0.62, 1.00, 0.66),  # sickly cathode green
		"key_energy": 1.45,
		"fill_color": Color(1.00, 0.36, 0.42),  # red signal-burn fill
		"fill_energy": 0.85,
		"back_color": Color(0.34, 0.92, 0.66),
		"back_energy": 0.70,
		"shake_amp": Vector3(0.014, 0.014, 0),
		"shake_freq": 28.0,                     # frantic jitter
		"bob_amp":  0.030, "bob_freq": 1.10,    # quick lurch
		"sway_amp": 0.025, "sway_freq": 1.30,
		"drift_yaw": 0.04,
	},
}

# Aliases collapse the EXPR_TINTS expression vocabulary down to the
# canonical 7 moods above.
const MOOD_ALIASES := {
	"excited":    "happy",
	"pleased":    "happy",
	"warm":       "happy",
	"melancholy": "sad",
	"upset":      "sad",
	"shocked":    "surprised",
	"wide":       "surprised",
	"furious":    "angry",
	"frustrated": "angry",
	"scared":     "nervous",
	"uneasy":     "nervous",
}


func _ready() -> void:
	custom_minimum_size = Vector2(PORTRAIT_W, PORTRAIT_H)
	# Placeholder capsule lives in the .tscn so the scene is visible
	# in-editor when nothing's loaded. At runtime we always call
	# load_character() right after instancing, so hide the placeholder
	# from frame 0 — otherwise it flashes for one frame before the
	# deferred GLB load lands.
	if _placeholder != null:
		_placeholder.visible = false
	# Belt-and-suspenders: explicitly write the demon-static
	# strength to 0 on every fresh instance. The .tscn already
	# specifies this and the material is local-to-scene, but if
	# either of those guarantees breaks, this catches it before
	# the first frame renders — heroes never inherit a stale
	# strength from a sibling portrait.
	var mat: ShaderMaterial = material as ShaderMaterial
	if mat != null:
		mat.set_shader_parameter("strength", 0.0)
	# Snapshot resting state so per-mood offsets compose on top
	_rest_cam_pos = _camera.position
	_rest_cam_fov = _camera.fov
	_rest_key_color  = _key.light_color
	_rest_key_energy = _key.light_energy
	_rest_fill_color  = _fill.light_color
	_rest_fill_energy = _fill.light_energy
	_rest_back_color  = _back.light_color
	_rest_back_energy = _back.light_energy
	# Default mood
	set_expression("neutral")
	set_process(true)


func _process(delta: float) -> void:
	# Continuous mood motion. We rebuild the camera transform every
	# frame from rest + mood offset + time-driven animation, so the
	# state stays clean (no drift accumulation across mood changes).
	_mood_t += delta
	var pos: Vector3 = _rest_cam_pos
	if _mood.has("pos_off"):
		pos += _mood["pos_off"]
	# Bob (vertical sway)
	if _mood.has("bob_amp") and _mood.has("bob_freq"):
		var amp: float = _mood["bob_amp"]
		var freq: float = _mood["bob_freq"]
		pos.y += sin(_mood_t * freq * TAU) * amp
	_camera.position = pos
	# Pitch + yaw — start from defaults, layer offsets + animation
	var pitch: float = _mood.get("pitch_off", 0.0)
	var yaw: float = _mood.get("yaw_off", 0.0)
	# Sway (horizontal yaw)
	if _mood.has("sway_amp") and _mood.has("sway_freq"):
		yaw += sin(_mood_t * _mood["sway_freq"] * TAU) * _mood["sway_amp"]
	# Drift (continuous slow yaw)
	if _mood.has("drift_yaw"):
		yaw += sin(_mood_t * 0.4) * _mood["drift_yaw"] * 4.0
	# Shake (random tremor, higher frequency)
	if _mood.has("shake_amp") and _mood.has("shake_freq"):
		var sa: Vector3 = _mood["shake_amp"]
		var sf: float = _mood["shake_freq"]
		# Lissajous-ish jitter so the shake doesn't look periodic
		pitch += sin(_mood_t * sf * TAU * 1.07) * sa.x
		yaw   += sin(_mood_t * sf * TAU * 0.93) * sa.y
	_camera.rotation = Vector3(pitch, yaw, 0.0)
	# FOV
	var fov: float = _rest_cam_fov + _mood.get("fov_off", 0.0)
	if fov < 5.0:
		fov = 5.0
	_camera.fov = fov


# ── Public API ────────────────────────────────────────────────────
func load_character(glb_path: String, expression: String = "") -> bool:
	if glb_path == _loaded_glb_path and _current_character != null:
		if expression != "":
			set_expression(expression)
		return true
	# Tear down any previously-loaded model
	if _current_character != null and is_instance_valid(_current_character):
		_current_character.queue_free()
	_current_character = null
	# Hide placeholder (the editor-default capsule) once we actually
	# have something to render
	if _placeholder != null:
		_placeholder.visible = false
	var ps: PackedScene = load(glb_path) as PackedScene
	if ps == null:
		push_warning("[Portrait3D] Could not load GLB at %s" % glb_path)
		return false
	var inst: Node = ps.instantiate()
	if inst == null:
		return false
	_anchor.add_child(inst)
	_current_character = inst as Node3D
	if _current_character == null:
		# Top node wasn't a Node3D — wrap it
		var wrap := Node3D.new()
		_anchor.add_child(wrap)
		inst.reparent(wrap)
		_current_character = wrap
	_loaded_glb_path = glb_path
	# Auto-orient + auto-scale to the portrait's target framing
	_orient_and_scale_character(_current_character)
	return true


func set_expression(expression: String) -> void:
	# Drive a per-mood camera + lighting + motion override on top
	# of the resting framing. Normalizes via MOOD_ALIASES (so
	# "furious" / "frustrated" both map to "angry", etc.), then
	# applies lights immediately and stores motion state for
	# _process() to animate.
	var normalized: String = expression.strip_edges().to_lower()
	if normalized == "":
		normalized = "neutral"
	if MOOD_ALIASES.has(normalized):
		normalized = MOOD_ALIASES[normalized]
	# Demons don't perform moods — they leak. Any incoming expression
	# is collapsed to the chaos preset (the signal-corruption shader
	# does the actual emotional read).
	if _demon_mode:
		normalized = "demon_chaos"
	# Reset mood timer ONLY on actual change — same-mood updates
	# preserve the existing animation phase so a re-trigger doesn't
	# snap the camera
	if normalized != _mood_id:
		_mood_t = 0.0
	_mood_id = normalized
	_mood = MOOD_TABLE.get(normalized, {})
	# Apply light overrides immediately. Missing keys fall back to
	# the resting values (so e.g. surprised doesn't override fill).
	_key.light_color  = _mood.get("key_color",  _rest_key_color)
	_key.light_energy = _mood.get("key_energy", _rest_key_energy)
	_fill.light_color  = _mood.get("fill_color",  _rest_fill_color)
	_fill.light_energy = _mood.get("fill_energy", _rest_fill_energy)
	_back.light_color  = _mood.get("back_color",  _rest_back_color)
	_back.light_energy = _mood.get("back_energy", _rest_back_energy)


func set_demon_mode(enabled: bool) -> void:
	# Flip the SubViewportContainer's demon-static shader on/off and
	# pin the mood to demon_chaos. Heroes get strength=0 (pass-
	# through); demons get strength=1 (full digital-static + RGB
	# tear + scanline glitch + signal-drop bands).
	_demon_mode = enabled
	var mat: ShaderMaterial = material as ShaderMaterial
	if mat != null:
		mat.set_shader_parameter("strength", 1.0 if enabled else 0.0)
	# Re-apply expression so the demon_chaos route fires immediately
	set_expression(_mood_id)


func get_viewport_texture() -> Texture2D:
	return _viewport.get_texture()


# ── Internal: orient + scale the loaded GLB ──────────────────────
func _orient_and_scale_character(root: Node3D) -> void:
	# Measure the bounding box, figure out which axis is "up,"
	# ROTATE the model if it isn't Y-up already, then scale so the
	# height axis hits TARGET_HEIGHT_M, then drop so feet land at
	# the anchor's Y=0 plane.
	var mesh_objs: Array[Node] = _collect_mesh_instances(root)
	if mesh_objs.is_empty():
		return
	# First-pass AABB measurement in root-local space
	var aabb_min: Vector3 = Vector3.INF
	var aabb_max: Vector3 = -Vector3.INF
	for n: Node in mesh_objs:
		var mi: MeshInstance3D = n as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		var local_aabb: AABB = mi.mesh.get_aabb()
		var xform: Transform3D = root.global_transform.affine_inverse() * mi.global_transform
		var world_aabb: AABB = xform * local_aabb
		aabb_min = aabb_min.min(world_aabb.position)
		aabb_max = aabb_max.max(world_aabb.position + world_aabb.size)
	if aabb_min == Vector3.INF:
		return
	var ext: Vector3 = aabb_max - aabb_min
	# Pick the largest extent — that's the "height" axis. If it's
	# not already Y, rotate the model so it stands upright.
	var max_axis: int = 1
	if ext.x > ext.y and ext.x > ext.z: max_axis = 0
	elif ext.z > ext.y and ext.z > ext.x: max_axis = 2
	print("[Portrait3D] orient — initial AABB ext=(%.2f, %.2f, %.2f) " % [ext.x, ext.y, ext.z]
		+ "longest axis=%s" % ["X", "Y", "Z"][max_axis])
	# Rotate if needed. We rotate the root node, then re-measure
	# the AABB in the new orientation before scaling + translating.
	if max_axis == 2:
		# Z-up → Y-up: rotate -90° about X (tip the head from +Z to +Y)
		root.rotation = Vector3(-PI / 2.0, 0, 0)
		print("[Portrait3D] orient — Z-up detected, rotated -90° about X")
	elif max_axis == 0:
		# X-up (lying sideways on +X): rotate +90° about Z
		root.rotation = Vector3(0, 0, PI / 2.0)
		print("[Portrait3D] orient — X-up detected, rotated +90° about Z")
	# Re-measure post-rotation
	aabb_min = Vector3.INF
	aabb_max = -Vector3.INF
	for n in mesh_objs:
		var mi2: MeshInstance3D = n as MeshInstance3D
		if mi2 == null or mi2.mesh == null:
			continue
		var local_aabb2: AABB = mi2.mesh.get_aabb()
		var xform2: Transform3D = root.transform.affine_inverse() * (root.transform * mi2.transform)
		# Actually simpler: combine the rotation into the AABB transform
		var world_aabb2: AABB = (root.transform * mi2.transform) * local_aabb2
		# Re-root by undoing root.position (which is still zero at this point)
		aabb_min = aabb_min.min(world_aabb2.position)
		aabb_max = aabb_max.max(world_aabb2.position + world_aabb2.size)
	if aabb_min == Vector3.INF:
		return
	ext = aabb_max - aabb_min
	# After rotation, Y should be the long axis
	var current_h: float = ext.y
	if current_h < 0.001:
		# Fall back to longest if rotation didn't land cleanly
		current_h = max(ext.x, max(ext.y, ext.z))
	var s: float = TARGET_HEIGHT_M / current_h
	root.scale = Vector3(s, s, s)
	# Drop so feet land at anchor Y=0; centre horizontally on X/Z
	var bot_y: float = aabb_min.y * s
	root.position = Vector3(-((aabb_min.x + aabb_max.x) / 2.0) * s,
	                         -bot_y,
	                         -((aabb_min.z + aabb_max.z) / 2.0) * s)
	print("[Portrait3D] orient — scale=%.3f, position=(%.2f, %.2f, %.2f)"
		% [s, root.position.x, root.position.y, root.position.z])


func _collect_mesh_instances(node: Node, out: Array[Node] = []) -> Array[Node]:
	if node is MeshInstance3D:
		out.append(node)
	for child in node.get_children():
		_collect_mesh_instances(child, out)
	return out
