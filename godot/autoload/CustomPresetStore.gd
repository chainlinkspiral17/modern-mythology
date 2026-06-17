# CustomPresetStore.gd
# ════════════════════════════════════════════════════════════════
# Autoloaded singleton. Persists user-saved visual presets to
# user://custom_presets.json. Used by ExpertModePanel:
#   · "Save as new..." captures the current shader + environment
#     state and writes it under a chosen name
#   · "Apply" re-writes the captured state back onto the active
#     scene's materials/environment
#   · "Delete" removes a saved preset
#
# A preset is a snapshot of every uniform exposed in
# ExpertModePanel.SHADER_PARAMS for every shader present in the
# scene's PostProcess CanvasLayer, plus the WorldEnvironment
# adjustment knobs the panel exposes.
#
# Presets survive Godot restarts. The HTML QA console doesn't
# need to know about them — Shift+F1 snapshots still record the
# resulting shader_strengths regardless of whether the look came
# from a built-in pack or a custom preset.
# ════════════════════════════════════════════════════════════════
extends Node

const STORE_PATH := "user://custom_presets.json"
const VERSION := 1

# Same env property list the panel exposes (kept in sync manually
# — change here AND in ExpertModePanel._add_world_env_section).
const ENV_PROPS := [
	"ambient_light_energy", "glow_intensity", "glow_bloom",
	"adjustment_contrast", "adjustment_saturation", "fog_density",
]

var _presets: Array = []   # Array of Dictionary


func _ready() -> void:
	_load()


func _load() -> void:
	if not FileAccess.file_exists(STORE_PATH):
		_presets = []
		return
	var f := FileAccess.open(STORE_PATH, FileAccess.READ)
	if f == null:
		_presets = []
		return
	var text := f.get_as_text()
	f.close()
	var parsed: Variant = JSON.parse_string(text)
	if typeof(parsed) == TYPE_DICTIONARY and parsed.has("presets"):
		_presets = parsed["presets"]
	else:
		_presets = []
	print("[CustomPresets] loaded %d preset%s"
		% [_presets.size(), "" if _presets.size() == 1 else "s"])


func _save() -> void:
	var f := FileAccess.open(STORE_PATH, FileAccess.WRITE)
	if f == null:
		push_warning("[CustomPresets] could not write %s" % STORE_PATH)
		return
	f.store_string(JSON.stringify({
		"version": VERSION,
		"presets": _presets,
	}, "\t"))
	f.close()


# ── Public API ──────────────────────────────────────────────────
func list_preset_names() -> Array[String]:
	var out: Array[String] = []
	for p in _presets:
		if typeof(p) == TYPE_DICTIONARY and p.has("name"):
			out.append(String(p["name"]))
	return out


func has_preset(name: String) -> bool:
	for p in _presets:
		if String(p.get("name", "")) == name:
			return true
	return false


# Snapshot the current scene's shader uniforms + env properties.
# Caller passes the PostProcess CanvasLayer + WorldEnvironment so
# we don't have to traverse twice with different APIs.
func capture_current(post: Node, world_env: WorldEnvironment) -> Dictionary:
	var snap: Dictionary = {
		"version": VERSION,
		"created": Time.get_datetime_string_from_system(true),
		"based_on": "",
		"shaders": {},
		"environment": {},
	}
	# Tag what the player was on when they saved (for traceability)
	if post != null:
		if "current_index" in post and "MOODS" in post:
			var idx: int = post.current_index
			if idx >= 0 and idx < post.MOODS.size():
				snap["based_on"] = String(post.MOODS[idx]["name"])
		if "style_pack_index" in post and "STYLE_PACKS" in post:
			var si: int = post.style_pack_index
			if si >= 0 and si < post.STYLE_PACKS.size():
				snap["based_on"] = String(post.STYLE_PACKS[si]["name"])
	# Capture per-shader uniforms — only the params ExpertModePanel
	# knows about so apply_preset doesn't try to write unrecognised
	# uniforms.
	if post != null:
		var panel_params: Dictionary = ExpertMode.SHADER_PARAMS if Engine.has_singleton("ExpertMode") else {}
		# Fall back to a runtime fetch since autoload globals access
		# via Engine.has_singleton is finicky pre-_ready ordering
		if panel_params.is_empty() and "SHADER_PARAMS" in ExpertMode:
			panel_params = ExpertMode.SHADER_PARAMS
		for child in post.get_children():
			if not (child is ColorRect and child.material is ShaderMaterial):
				continue
			var params: Array = panel_params.get(child.name, [])
			if params.is_empty():
				continue
			var mat: ShaderMaterial = child.material as ShaderMaterial
			var per_shader: Dictionary = {}
			for p in params:
				var n: String = p["name"]
				var v: Variant = mat.get_shader_parameter(n)
				if v == null:
					continue
				if v is Color:
					per_shader[n] = [v.r, v.g, v.b, v.a]
				else:
					per_shader[n] = v
			snap["shaders"][child.name] = per_shader
	# Capture env props
	if world_env != null and world_env.environment != null:
		for prop in ENV_PROPS:
			snap["environment"][prop] = world_env.environment.get(prop)
	return snap


func save_preset(name: String, snap: Dictionary) -> bool:
	if name.strip_edges() == "":
		return false
	snap["name"] = name
	# Replace existing with the same name; otherwise append
	for i in range(_presets.size()):
		if String(_presets[i].get("name", "")) == name:
			_presets[i] = snap
			_save()
			print("[CustomPresets] updated '%s'" % name)
			return true
	_presets.append(snap)
	_save()
	print("[CustomPresets] saved '%s'" % name)
	return true


func delete_preset(name: String) -> bool:
	for i in range(_presets.size()):
		if String(_presets[i].get("name", "")) == name:
			_presets.remove_at(i)
			_save()
			print("[CustomPresets] deleted '%s'" % name)
			return true
	return false


# Apply a stored preset back onto the live materials + env. Missing
# shaders / env are silently skipped so a preset taken in one
# locale can be partially applied in another.
func apply_preset(name: String, post: Node, world_env: WorldEnvironment) -> bool:
	var preset: Dictionary = {}
	for p in _presets:
		if String(p.get("name", "")) == name:
			preset = p
			break
	if preset.is_empty():
		return false
	# Shaders
	var shaders: Dictionary = preset.get("shaders", {})
	if post != null:
		for child in post.get_children():
			if not (child is ColorRect and child.material is ShaderMaterial):
				continue
			var per: Dictionary = shaders.get(child.name, {})
			if per.is_empty():
				continue
			var mat: ShaderMaterial = child.material as ShaderMaterial
			for pname in per.keys():
				var v: Variant = per[pname]
				# Colors come back as 4-arrays
				if v is Array and v.size() == 4:
					mat.set_shader_parameter(pname, Color(v[0], v[1], v[2], v[3]))
				else:
					mat.set_shader_parameter(pname, v)
	# Environment
	if world_env != null and world_env.environment != null:
		var env_dict: Dictionary = preset.get("environment", {})
		for prop in env_dict.keys():
			world_env.environment.set(prop, env_dict[prop])
	print("[CustomPresets] applied '%s'" % name)
	return true
