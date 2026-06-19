extends Node
## VnDebugState — process-lifetime registry of VN debug overrides
## ════════════════════════════════════════════════════════════════
## Persists user-driven debug tweaks (portrait shader knobs,
## backdrop kinds, per-portrait Environment grading, bg-3D mood /
## lighting / style / blend) across VN navigation:
##   · forward — `_advance()` re-instantiates portraits and may
##     reload the bg locale; without this registry, every dial-in
##     would reset on the next beat
##   · backward — scene rewind / replay flows hit the same
##     construction paths; same problem
##
## STATE SHAPES (all keyed by char_key() or Background3D preset_id)
##
## portrait_state[char_key] = {
##     "shader":   { uniform_name: value, ... },
##     "backdrop": String ("static" / "warm_glow" / ...),
##     "lights":   { "_rest_key_color": Color, ..., "_rest_back_energy": float },
##     "mood":     String (overrides scene-driven expression),
##     "demon":    bool,
##     "env":      { "brightness": float, "contrast": float,
##                   "saturation": float, "glow": float },
##     "cam":      { "fov": float, "pos": Vector3, "rot": Vector3 },
## }
##
## locale_state[preset_id] = {
##     "mood_index":       int,   // MoodCycler.mood_index
##     "lighting_index":   int,
##     "style_pack_index": int,
##     "blend_mode":       int,
##     "blend_amt_index":  int,
## }
##
## Apply hooks:
##   · CharLayer.show_character() calls apply_portrait_state() after
##     spawning a portrait (and after any same-slot re-expression).
##   · Background3D.load_location() calls apply_locale_state() after
##     the locale's PostProcess / MoodCycler is in the tree.
##
## Debug-overlay writers:
##   · VnPortraitDebugOverlay's _bump_shader / _set_backdrop /
##     _bump_env / _bump_cam_* / _shift_temp / etc. all call the
##     stamp_* methods below so any user action is captured.
##
## Autoload via project.godot as "VnDebugState" — registered
## globally so any node can read/write without a NodePath.
## ════════════════════════════════════════════════════════════════

# ── Process-lifetime state ────────────────────────────────────────
var portrait_state: Dictionary = {}
var locale_state:   Dictionary = {}


# ── Portrait stamps ───────────────────────────────────────────────
func stamp_portrait_shader(char_key: String, uniform: String, value) -> void:
	var entry: Dictionary = portrait_state.get(char_key, {})
	var shader: Dictionary = entry.get("shader", {})
	shader[uniform] = value
	entry["shader"] = shader
	portrait_state[char_key] = entry


func stamp_portrait_backdrop(char_key: String, kind: String) -> void:
	var entry: Dictionary = portrait_state.get(char_key, {})
	entry["backdrop"] = kind
	portrait_state[char_key] = entry


func stamp_portrait_light(char_key: String, prop: String, value) -> void:
	var entry: Dictionary = portrait_state.get(char_key, {})
	var lights: Dictionary = entry.get("lights", {})
	lights[prop] = value
	entry["lights"] = lights
	portrait_state[char_key] = entry


func stamp_portrait_env(char_key: String, knob: String, value: float) -> void:
	var entry: Dictionary = portrait_state.get(char_key, {})
	var env: Dictionary = entry.get("env", {})
	env[knob] = value
	entry["env"] = env
	portrait_state[char_key] = entry


func stamp_portrait_cam(char_key: String, key: String, value) -> void:
	var entry: Dictionary = portrait_state.get(char_key, {})
	var cam: Dictionary = entry.get("cam", {})
	cam[key] = value
	entry["cam"] = cam
	portrait_state[char_key] = entry


func stamp_portrait_mood(char_key: String, mood_id: String) -> void:
	var entry: Dictionary = portrait_state.get(char_key, {})
	entry["mood"] = mood_id
	portrait_state[char_key] = entry


func stamp_portrait_demon(char_key: String, on: bool) -> void:
	var entry: Dictionary = portrait_state.get(char_key, {})
	entry["demon"] = on
	portrait_state[char_key] = entry


func clear_portrait(char_key: String) -> void:
	portrait_state.erase(char_key)


# ── Locale stamps ─────────────────────────────────────────────────
func stamp_locale_mood(preset_id: String, idx: int) -> void:
	_locale_set(preset_id, "mood_index", idx)


func stamp_locale_lighting(preset_id: String, idx: int) -> void:
	_locale_set(preset_id, "lighting_index", idx)


func stamp_locale_style_pack(preset_id: String, idx: int) -> void:
	_locale_set(preset_id, "style_pack_index", idx)


func stamp_locale_blend_mode(preset_id: String, mode: int) -> void:
	_locale_set(preset_id, "blend_mode", mode)


func stamp_locale_blend_amt(preset_id: String, idx: int) -> void:
	_locale_set(preset_id, "blend_amt_index", idx)


func _locale_set(preset_id: String, key: String, value) -> void:
	var entry: Dictionary = locale_state.get(preset_id, {})
	entry[key] = value
	locale_state[preset_id] = entry


# ── Apply hooks ────────────────────────────────────────────────────
# Called by CharLayer.show_character AFTER the portrait is in tree.
# Re-applies any saved overrides for this character.
func apply_portrait_state(char_key: String, p3d: Node) -> void:
	if not portrait_state.has(char_key):
		return
	if not is_instance_valid(p3d):
		return
	var entry: Dictionary = portrait_state[char_key]
	# Shader uniforms
	var mat: ShaderMaterial = p3d.material as ShaderMaterial
	if mat != null and entry.has("shader"):
		for u in entry["shader"]:
			mat.set_shader_parameter(u, entry["shader"][u])
	# Light overrides (rest values; mood deltas compose on top)
	if entry.has("lights"):
		for prop in entry["lights"]:
			if prop in p3d:
				p3d.set(prop, entry["lights"][prop])
	# Mood override — apply LAST so the live light nodes get the
	# combined rest + mood values
	if entry.has("mood") and p3d.has_method("set_expression"):
		p3d.set_expression(String(entry["mood"]))
	# Demon mode
	if entry.has("demon") and p3d.has_method("set_demon_mode"):
		p3d.set_demon_mode(bool(entry["demon"]))
	# Camera
	if entry.has("cam") and "_camera" in p3d:
		var cam = p3d.get("_camera")
		if cam != null and is_instance_valid(cam):
			var c: Dictionary = entry["cam"]
			if c.has("fov"): cam.fov = float(c["fov"])
			if c.has("pos"): cam.position = c["pos"]
			if c.has("rot"): cam.rotation = c["rot"]
	# Environment grading — apply via the same path as the debug
	# overlay's _bump_env (find/spawn WorldEnvironment in SubViewport).
	if entry.has("env"):
		_apply_env(p3d, entry["env"])


func _apply_env(p3d: Node, env_state: Dictionary) -> void:
	var vp = p3d.get_node_or_null("SubViewport")
	if vp == null:
		return
	var we: WorldEnvironment = null
	for child in vp.get_children():
		if child is WorldEnvironment:
			we = child
			break
	if we == null:
		we = WorldEnvironment.new()
		we.environment = Environment.new()
		we.environment.background_mode = Environment.BG_COLOR
		we.environment.background_color = Color(0, 0, 0, 0)
		vp.add_child(we)
	var env: Environment = we.environment
	if env == null:
		env = Environment.new()
		we.environment = env
	env.adjustment_enabled = true
	if env_state.has("brightness"):
		env.adjustment_brightness = float(env_state["brightness"])
	if env_state.has("contrast"):
		env.adjustment_contrast = float(env_state["contrast"])
	if env_state.has("saturation"):
		env.adjustment_saturation = float(env_state["saturation"])
	if env_state.has("glow"):
		env.glow_enabled = true
		env.glow_intensity = float(env_state["glow"])


# Returns the backdrop kind the debug overlay last set for this
# character, or "" if no override exists. CharLayer.show_character
# reads this on portrait construction so the kind survives respawn.
func get_portrait_backdrop(char_key: String) -> String:
	if not portrait_state.has(char_key):
		return ""
	return String(portrait_state[char_key].get("backdrop", ""))


# Called by Background3D.load_location AFTER the locale's
# PostProcess / MoodCycler is in tree. Re-applies any saved bg-3D
# overrides for this preset.
func apply_locale_state(preset_id: String, mood_cycler: Node) -> void:
	if not locale_state.has(preset_id):
		return
	if mood_cycler == null or not is_instance_valid(mood_cycler):
		return
	var entry: Dictionary = locale_state[preset_id]
	# MoodCycler's action_set_* methods are the cleanest entry points,
	# but several locales' MoodCyclers don't expose them. Walk the
	# common index/property names — defensive against drift.
	if entry.has("style_pack_index") and "style_pack_index" in mood_cycler:
		mood_cycler.style_pack_index = int(entry["style_pack_index"])
		if mood_cycler.has_method("apply_style_pack"):
			mood_cycler.apply_style_pack(int(entry["style_pack_index"]))
	if entry.has("mood_index") and "mood_index" in mood_cycler:
		mood_cycler.mood_index = int(entry["mood_index"])
		if mood_cycler.has_method("apply_mood"):
			mood_cycler.apply_mood(int(entry["mood_index"]))
	if entry.has("lighting_index") and "lighting_index" in mood_cycler:
		mood_cycler.lighting_index = int(entry["lighting_index"])
		if mood_cycler.has_method("apply_lighting"):
			mood_cycler.apply_lighting(int(entry["lighting_index"]))
	if entry.has("blend_mode") and "blend_mode" in mood_cycler:
		mood_cycler.blend_mode = int(entry["blend_mode"])
	if entry.has("blend_amt_index") and "blend_amt_index" in mood_cycler:
		mood_cycler.blend_amt_index = int(entry["blend_amt_index"])
