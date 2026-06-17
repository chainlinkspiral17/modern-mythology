# ExpertModePanel.gd
# ════════════════════════════════════════════════════════════════
# Autoloaded singleton. Shift+F12 toggles a side-panel with live
# sliders + color-pickers for every screen-space shader's key
# uniforms in the current scene's PostProcess stack. Edits write
# directly to the ShaderMaterials — no preset commit; the changes
# are wiped the next time F3/F11/F12 re-applies a mood/lighting/
# pack.
#
# Includes:
#   · Live readout: current mood + lighting + style + blend %
#   · Per-shader sections: strength slider + key params per shader
#   · World env controls: glow_intensity, glow_bloom, env_brightness
#   · Buttons: Refresh from materials, Reset to current mood preset,
#     Close
#
# The panel honours F4 HUD-toggle (added to the "ui" group), so
# screenshots taken via Shift+F1 won't have the panel in them.
#
# QA tip: after dialing a look, hit Shift+F1 to snapshot — the
# JSON's shader_strengths section will record the exact tuning,
# and you can paste a recipe to Claude as direction for a new
# preset.
# ════════════════════════════════════════════════════════════════
extends Node

const PANEL_LAYER := 150

# Per-shader uniform exposure. Each shader gets the params worth
# tweaking; the rest stay at preset defaults. Type: "float" | "color".
const SHADER_PARAMS := {
	"NeonQuad": [
		{"name": "strength",        "type": "float", "min": 0.0,   "max": 1.0,   "step": 0.01},
		{"name": "edge_threshold",  "type": "float", "min": 0.001, "max": 0.5,   "step": 0.001},
		{"name": "edge_thickness",  "type": "float", "min": 0.5,   "max": 4.0,   "step": 0.05},
		{"name": "edge_glow",       "type": "float", "min": 0.0,   "max": 1.5,   "step": 0.01},
		{"name": "edge_color",      "type": "color"},
		{"name": "fill_low",        "type": "color"},
		{"name": "fill_high",       "type": "color"},
	],
	"AsciiQuad": [
		{"name": "strength",  "type": "float", "min": 0.0, "max": 1.0,  "step": 0.01},
		{"name": "cell_size", "type": "float", "min": 4.0, "max": 32.0, "step": 0.5},
		{"name": "gamma",     "type": "float", "min": 0.2, "max": 3.0,  "step": 0.01},
		{"name": "fg_color",  "type": "color"},
		{"name": "bg_color",  "type": "color"},
	],
	"DirAsciiQuad": [
		{"name": "strength",       "type": "float", "min": 0.0,   "max": 1.0,  "step": 0.01},
		{"name": "cell_size",      "type": "float", "min": 4.0,   "max": 32.0, "step": 0.5},
		{"name": "edge_threshold", "type": "float", "min": 0.001, "max": 0.5,  "step": 0.001},
		{"name": "line_color",     "type": "color"},
		{"name": "fill_color",     "type": "color"},
	],
	"StarscapeQuad": [
		{"name": "strength",        "type": "float", "min": 0.0, "max": 1.0,  "step": 0.01},
		{"name": "time_scale",      "type": "float", "min": 0.0, "max": 2.0,  "step": 0.01},
		{"name": "galaxy_strength", "type": "float", "min": 0.0, "max": 1.5,  "step": 0.01},
		{"name": "star_strength",   "type": "float", "min": 0.0, "max": 1.5,  "step": 0.01},
		{"name": "chip_strength",   "type": "float", "min": 0.0, "max": 1.5,  "step": 0.01},
	],
	"MotionQuad": [
		{"name": "strength",        "type": "float", "min": 0.0, "max": 1.0,  "step": 0.01},
		{"name": "motion_speed",    "type": "float", "min": 0.0, "max": 4.0,  "step": 0.02},
		{"name": "trail_strength",  "type": "float", "min": 0.0, "max": 1.0,  "step": 0.01},
		{"name": "line_density",    "type": "float", "min": 0.0, "max": 1.5,  "step": 0.01},
		{"name": "line_color",      "type": "color"},
	],
	"BlurQuad": [
		{"name": "strength",  "type": "float", "min": 0.0, "max": 1.0,  "step": 0.01},
		{"name": "radius",    "type": "float", "min": 0.5, "max": 16.0, "step": 0.1},
	],
	"Quad": [   # demoscene_post
		{"name": "palette_size",          "type": "float", "min": 2.0,  "max": 32.0,    "step": 0.5},
		{"name": "dither_strength",       "type": "float", "min": 0.0,  "max": 1.0,     "step": 0.01},
		{"name": "scanline_strength",     "type": "float", "min": 0.0,  "max": 1.0,     "step": 0.01},
		{"name": "chromatic_aberration",  "type": "float", "min": 0.0,  "max": 0.005,   "step": 0.0001},
	],
	"OldFilmQuad": [
		{"name": "strength",          "type": "float", "min": 0.0,  "max": 1.0,   "step": 0.01},
		{"name": "sim_fps",           "type": "float", "min": 12.0, "max": 60.0,  "step": 1.0},
		{"name": "tint_amount",       "type": "float", "min": 0.0,  "max": 1.0,   "step": 0.01},
		{"name": "grain_strength",    "type": "float", "min": 0.0,  "max": 1.0,   "step": 0.01},
		{"name": "flicker_strength",  "type": "float", "min": 0.0,  "max": 1.0,   "step": 0.01},
		{"name": "vignette_strength", "type": "float", "min": 0.0,  "max": 1.0,   "step": 0.01},
		{"name": "scratch_strength",  "type": "float", "min": 0.0,  "max": 1.0,   "step": 0.01},
		{"name": "judder_strength",   "type": "float", "min": 0.0,  "max": 0.04,  "step": 0.001},
		{"name": "tint_color",        "type": "color"},
	],
	"LiminalQuad": [
		{"name": "strength",     "type": "float", "min": 0.0, "max": 1.0,   "step": 0.01},
		{"name": "edge_ca",      "type": "float", "min": 0.0, "max": 0.04,  "step": 0.001},
		{"name": "wobble_amp",   "type": "float", "min": 0.0, "max": 0.008, "step": 0.0001},
		{"name": "wobble_freq",  "type": "float", "min": 0.1, "max": 6.0,   "step": 0.05},
		{"name": "tint_amount",  "type": "float", "min": 0.0, "max": 0.6,   "step": 0.01},
		{"name": "tint_color",   "type": "color"},
	],
}

var _panel: CanvasLayer = null
var _container: VBoxContainer = null
var _header_label: Label = null


func _ready() -> void:
	set_process_unhandled_input(true)


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo):
		return
	var k := event as InputEventKey
	# Shift+F12 toggles the panel
	if k.keycode == KEY_F12 and k.shift_pressed and not k.ctrl_pressed and not k.alt_pressed:
		get_viewport().set_input_as_handled()
		toggle()


func toggle() -> void:
	if _panel != null:
		_close()
	else:
		_open()


# ── Open / close ────────────────────────────────────────────────
func _open() -> void:
	var scene: Node = get_tree().current_scene
	if scene == null:
		return
	var post: Node = scene.get_node_or_null("PostProcess")
	if post == null:
		push_warning("[ExpertMode] No PostProcess node in current scene.")
		return

	_panel = CanvasLayer.new()
	_panel.layer = PANEL_LAYER
	_panel.add_to_group("ui")   # honours F4 HUD toggle

	# Backdrop — semi-transparent dark on left half, opaque panel on right
	var root := PanelContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_RIGHT_WIDE)
	root.custom_minimum_size = Vector2(640, 0)
	root.offset_left = -640
	root.offset_right = 0
	root.offset_top = 0
	root.offset_bottom = 0
	_panel.add_child(root)

	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.08, 0.06, 0.10, 0.95)
	sb.border_color = Color(0.62, 0.46, 0.22, 1)
	sb.set_border_width_all(2)
	root.add_theme_stylebox_override("panel", sb)

	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 16)
	margin.add_theme_constant_override("margin_right", 16)
	margin.add_theme_constant_override("margin_top", 14)
	margin.add_theme_constant_override("margin_bottom", 14)
	root.add_child(margin)

	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 8)
	margin.add_child(col)

	# Header (mood / lighting / blend readout)
	_header_label = Label.new()
	_header_label.add_theme_font_size_override("font_size", 14)
	_header_label.add_theme_color_override("font_color", Color(0.96, 0.78, 0.36, 1))
	_header_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
	_header_label.add_theme_constant_override("outline_size", 3)
	_header_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	col.add_child(_header_label)

	# Action buttons row
	var btn_row := HBoxContainer.new()
	btn_row.add_theme_constant_override("separation", 8)
	col.add_child(btn_row)
	_make_button(btn_row, "↻ Refresh", _refresh)
	_make_button(btn_row, "Reset to mood", _reset_to_mood)
	_make_button(btn_row, "Close", _close)

	# Hint
	var hint := Label.new()
	hint.text = "Shift+F12 toggles · Shift+F1 captures · F4 hides HUD\nEdits live on the ShaderMaterials. F3/F11/F12 will overwrite."
	hint.add_theme_font_size_override("font_size", 10)
	hint.add_theme_color_override("font_color", Color(0.62, 0.58, 0.50, 1))
	col.add_child(hint)

	# Scrollable content
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col.add_child(scroll)

	_container = VBoxContainer.new()
	_container.add_theme_constant_override("separation", 6)
	_container.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_container)

	# Add the WorldEnvironment section first (above shaders)
	_add_world_env_section(scene)
	# Build per-shader controls
	_build_shader_controls(post)

	get_tree().root.add_child(_panel)
	_update_header(post)


func _close() -> void:
	if _panel != null and is_instance_valid(_panel):
		_panel.queue_free()
	_panel = null
	_container = null
	_header_label = null


func _refresh() -> void:
	# Rebuild the panel with fresh values from the materials.
	# Cheap to do — same as close + open.
	var scene: Node = get_tree().current_scene
	if scene == null or _panel == null:
		return
	_close()
	_open()


func _reset_to_mood() -> void:
	# Tell MoodCycler to re-apply its current mood, wiping any
	# live edits. The MoodCycler script lives on PostProcess.
	var scene: Node = get_tree().current_scene
	if scene == null:
		return
	var post: Node = scene.get_node_or_null("PostProcess")
	if post == null or not post.has_method("_apply"):
		return
	if "current_index" in post and "MOODS" in post:
		post._apply(post.MOODS[post.current_index])
	_refresh()


# ── World env section ───────────────────────────────────────────
func _add_world_env_section(scene: Node) -> void:
	var we: WorldEnvironment = scene.get_node_or_null("WorldEnvironment") as WorldEnvironment
	if we == null or we.environment == null:
		return
	_add_section_header("WorldEnvironment")
	var env := we.environment
	_add_env_slider("ambient_light_energy",    env, "ambient_light_energy",      0.0, 3.0,  0.01)
	_add_env_slider("glow_intensity",           env, "glow_intensity",            0.0, 3.0,  0.01)
	_add_env_slider("glow_bloom",               env, "glow_bloom",                0.0, 1.0,  0.01)
	_add_env_slider("adjustment_contrast",      env, "adjustment_contrast",       0.5, 2.0,  0.01)
	_add_env_slider("adjustment_saturation",    env, "adjustment_saturation",     0.0, 2.0,  0.01)
	_add_env_slider("fog_density",              env, "fog_density",               0.0, 0.05, 0.0005)


func _add_env_slider(label_text: String, env: Environment, prop: String,
		min_val: float, max_val: float, step_val: float) -> void:
	var hb := HBoxContainer.new()
	var label := Label.new()
	label.text = label_text
	label.add_theme_font_size_override("font_size", 11)
	label.custom_minimum_size.x = 200
	label.add_theme_color_override("font_color", Color(0.86, 0.82, 0.74, 1))
	var slider := HSlider.new()
	slider.min_value = min_val
	slider.max_value = max_val
	slider.step = step_val
	slider.custom_minimum_size.x = 240
	slider.value = env.get(prop)
	var value_label := Label.new()
	value_label.custom_minimum_size.x = 80
	value_label.add_theme_font_size_override("font_size", 11)
	value_label.add_theme_color_override("font_color", Color(0.96, 0.78, 0.36, 1))
	value_label.text = _fmt(slider.value, step_val)
	slider.value_changed.connect(func(v: float):
		env.set(prop, v)
		value_label.text = _fmt(v, step_val))
	hb.add_child(label)
	hb.add_child(slider)
	hb.add_child(value_label)
	_container.add_child(hb)


# ── Shader controls ─────────────────────────────────────────────
func _build_shader_controls(post: Node) -> void:
	for child in post.get_children():
		if not (child is ColorRect and child.material is ShaderMaterial):
			continue
		var params: Array = SHADER_PARAMS.get(child.name, [])
		if params.is_empty():
			continue
		_add_section_header(child.name)
		var mat: ShaderMaterial = child.material as ShaderMaterial
		for p in params:
			if p["type"] == "float":
				_add_shader_slider(mat, p["name"], p["min"], p["max"], p.get("step", 0.01))
			elif p["type"] == "color":
				_add_shader_color(mat, p["name"])


func _add_section_header(name: String) -> void:
	var sep := HSeparator.new()
	_container.add_child(sep)
	var lbl := Label.new()
	lbl.text = "── " + name + " ──"
	lbl.add_theme_font_size_override("font_size", 13)
	lbl.add_theme_color_override("font_color", Color(0.62, 0.92, 0.78, 1))
	_container.add_child(lbl)


func _add_shader_slider(mat: ShaderMaterial, param_name: String,
		min_val: float, max_val: float, step_val: float) -> void:
	var hb := HBoxContainer.new()
	var label := Label.new()
	label.text = param_name
	label.add_theme_font_size_override("font_size", 11)
	label.custom_minimum_size.x = 200
	label.add_theme_color_override("font_color", Color(0.86, 0.82, 0.74, 1))
	var slider := HSlider.new()
	slider.min_value = min_val
	slider.max_value = max_val
	slider.step = step_val
	slider.custom_minimum_size.x = 240
	var current = mat.get_shader_parameter(param_name)
	slider.value = float(current) if current != null else min_val
	var value_label := Label.new()
	value_label.custom_minimum_size.x = 80
	value_label.add_theme_font_size_override("font_size", 11)
	value_label.add_theme_color_override("font_color", Color(0.96, 0.78, 0.36, 1))
	value_label.text = _fmt(slider.value, step_val)
	slider.value_changed.connect(func(v: float):
		mat.set_shader_parameter(param_name, v)
		value_label.text = _fmt(v, step_val))
	hb.add_child(label)
	hb.add_child(slider)
	hb.add_child(value_label)
	_container.add_child(hb)


func _add_shader_color(mat: ShaderMaterial, param_name: String) -> void:
	var hb := HBoxContainer.new()
	var label := Label.new()
	label.text = param_name
	label.add_theme_font_size_override("font_size", 11)
	label.custom_minimum_size.x = 200
	label.add_theme_color_override("font_color", Color(0.86, 0.82, 0.74, 1))
	var picker := ColorPickerButton.new()
	picker.custom_minimum_size = Vector2(240, 28)
	var current = mat.get_shader_parameter(param_name)
	if current is Color:
		picker.color = current
	picker.color_changed.connect(func(c: Color):
		mat.set_shader_parameter(param_name, c))
	hb.add_child(label)
	hb.add_child(picker)
	_container.add_child(hb)


# ── Misc helpers ────────────────────────────────────────────────
func _make_button(parent: Control, label_text: String, cb: Callable) -> void:
	var b := Button.new()
	b.text = label_text
	b.custom_minimum_size = Vector2(110, 28)
	b.pressed.connect(cb)
	parent.add_child(b)


func _update_header(post: Node) -> void:
	if _header_label == null:
		return
	var lines: Array[String] = ["EXPERT MODE"]
	var parts: Array[String] = []
	if "current_index" in post and "MOODS" in post:
		var idx: int = post.current_index
		var moods: Array = post.MOODS
		if idx >= 0 and idx < moods.size():
			parts.append("mood = " + String(moods[idx]["name"]))
	if "lighting_index" in post and "LIGHTING_PRESETS" in post:
		var li: int = post.lighting_index
		var lp: Array = post.LIGHTING_PRESETS
		if li >= 0 and li < lp.size():
			parts.append("light = " + String(lp[li]["name"]))
	if "style_pack_index" in post and "STYLE_PACKS" in post:
		var si: int = post.style_pack_index
		var sp: Array = post.STYLE_PACKS
		if si >= 0 and si < sp.size():
			parts.append("pack = " + String(sp[si]["name"]))
	if "blend_amount_pct" in post:
		var p: int = post.blend_amount_pct
		if p >= 0:
			parts.append("blend = %d%%" % p)
	if parts.size() > 0:
		lines.append("  ·  ".join(parts))
	_header_label.text = "\n".join(lines)


func _fmt(v: float, step_val: float) -> String:
	if step_val < 0.001:
		return "%.4f" % v
	if step_val < 0.01:
		return "%.3f" % v
	if step_val < 0.1:
		return "%.2f" % v
	if step_val < 1.0:
		return "%.2f" % v
	return "%.1f" % v
