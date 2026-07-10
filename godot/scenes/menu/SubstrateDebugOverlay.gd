extends Control
## SubstrateDebugOverlay — live tweak of an AsciiComposition's windows.
##
## Spawn inside a composition viewer and call `bind(composition)` to attach.
## Sliders/spinboxes mutate live window properties (position, z, alpha,
## visualizer params); the "Export" button writes the current state as a
## composition manifest JSON to the clipboard, also dropping a copy to
## user://exports/<composition_id>_<timestamp>.json.

signal closed

const C_BG     := Color(0.03, 0.04, 0.06, 0.94)
const C_BORDER := Color(0.61, 0.76, 1.0, 0.30)
const C_TXT    := Color(0.91, 0.93, 0.97)
const C_DIM    := Color(0.50, 0.55, 0.68)
const C_GOLD   := Color(1.00, 0.82, 0.48)

const PANEL_WIDTH := 440.0

var _composition: Node = null
var _scroll_vbox: VBoxContainer = null
var _status_lbl: Label = null


func _ready() -> void:
	# F4 sweep compliance per CLAUDE.md hard rule.
	add_to_group("ui")
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP


func bind(composition: Node) -> void:
	_composition = composition
	for ch in get_children():
		ch.queue_free()
	_rebuild()


func _rebuild() -> void:
	# Right-anchored panel
	var panel := Panel.new()
	panel.set_anchors_preset(Control.PRESET_RIGHT_WIDE)
	panel.anchor_left = 1.0
	panel.anchor_right = 1.0
	panel.offset_left = -PANEL_WIDTH
	panel.offset_right = 0
	panel.offset_top = 0
	panel.offset_bottom = 0
	var st := StyleBoxFlat.new()
	st.bg_color = C_BG
	st.border_color = C_BORDER
	st.set_border_width_all(1)
	st.content_margin_top    = 16
	st.content_margin_right  = 16
	st.content_margin_bottom = 16
	st.content_margin_left   = 16
	panel.add_theme_stylebox_override("panel", st)
	add_child(panel)

	var vbox := VBoxContainer.new()
	vbox.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	vbox.offset_left = 16
	vbox.offset_right = -16
	vbox.offset_top = 16
	vbox.offset_bottom = -16
	vbox.add_theme_constant_override("separation", 10)
	panel.add_child(vbox)

	# Header
	var header := HBoxContainer.new()
	vbox.add_child(header)
	var title := Label.new()
	var comp_id: String = "(none)"
	if _composition != null:
		comp_id = str(_composition.composition_id())
	title.text = "SUBSTRATE DEBUG  —  " + comp_id
	title.add_theme_color_override("font_color", C_GOLD)
	title.add_theme_font_size_override("font_size", 12)
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(title)
	var close_btn := Button.new()
	close_btn.text = "✕"
	close_btn.custom_minimum_size = Vector2(28, 24)
	close_btn.pressed.connect(func() -> void: visible = false; closed.emit())
	header.add_child(close_btn)

	_add_rule(vbox)

	# Window editors
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	vbox.add_child(scroll)
	_scroll_vbox = VBoxContainer.new()
	_scroll_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_scroll_vbox.add_theme_constant_override("separation", 14)
	scroll.add_child(_scroll_vbox)

	if _composition == null:
		var nope := Label.new()
		nope.text = "No composition bound."
		nope.add_theme_color_override("font_color", C_DIM)
		_scroll_vbox.add_child(nope)
	else:
		for entry_v in _composition.get_windows():
			var entry: Dictionary = entry_v
			_scroll_vbox.add_child(_make_window_editor(entry["node"], entry["manifest"]))

	_add_rule(vbox)

	# Footer
	var footer := HBoxContainer.new()
	footer.add_theme_constant_override("separation", 8)
	vbox.add_child(footer)
	var export_btn := Button.new()
	export_btn.text = "Export to clipboard"
	export_btn.pressed.connect(_on_export_pressed)
	footer.add_child(export_btn)
	var save_btn := Button.new()
	save_btn.text = "Save to user://"
	save_btn.pressed.connect(_on_save_pressed)
	footer.add_child(save_btn)
	_status_lbl = Label.new()
	_status_lbl.add_theme_color_override("font_color", C_DIM)
	_status_lbl.add_theme_font_size_override("font_size", 12)
	_status_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_status_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	footer.add_child(_status_lbl)


func _add_rule(parent: Node) -> void:
	var r := ColorRect.new()
	r.color = C_BORDER
	r.custom_minimum_size.y = 1
	parent.add_child(r)


func _make_window_editor(win: Control, manifest: Dictionary) -> Control:
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 4)

	var kind: String = str(manifest.get("kind", "static"))
	var label := Label.new()
	var title := kind.to_upper()
	if kind == "visualizer":
		title += "  ·  " + str(manifest.get("min_freq", "?")) + "-" + str(manifest.get("max_freq", "?")) + " Hz"
	else:
		title += "  ·  " + str(manifest.get("path", ""))
	label.text = title
	label.add_theme_color_override("font_color", C_TXT)
	label.add_theme_font_size_override("font_size", 12)
	v.add_child(label)

	# Common controls: position, z, alpha
	_add_xy_row(v, "Position", int(win.position.x), int(win.position.y),
		func(x: int) -> void: win.position.x = float(x),
		func(y: int) -> void: win.position.y = float(y))
	_add_int_row(v, "Z-index", win.z_index, -10, 50,
		func(z: int) -> void: win.z_index = z)
	_add_float_row(v, "Alpha", win.modulate.a, 0.0, 1.0, 0.01,
		func(a: float) -> void: win.modulate = Color(win.modulate.r, win.modulate.g, win.modulate.b, a))

	# Visualizer-specific live params
	if kind == "visualizer":
		_add_float_row(v, "Smoothing", win.smoothing, 0.0, 0.95, 0.01,
			func(s: float) -> void: win.smoothing = s)
		_add_float_row(v, "Magnitude", win.magnitude_scale, 0.5, 40.0, 0.1,
			func(m: float) -> void: win.magnitude_scale = m)
		_add_float_row(v, "Peak decay", win.peak_decay, 0.80, 0.999, 0.001,
			func(d: float) -> void: win.peak_decay = d)
		_add_int_row(v, "Bar count", win.bar_count, 4, 200,
			func(c: int) -> void: win.bar_count = c)
		_add_int_row(v, "Bar height", win.bar_height, 4, 40,
			func(h: int) -> void: win.bar_height = h)

	_add_rule(v)
	return v


func _add_xy_row(parent: Node, label: String, x: int, y: int,
				on_x: Callable, on_y: Callable) -> void:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 6)
	var lbl := Label.new()
	lbl.text = label
	lbl.add_theme_color_override("font_color", C_DIM)
	lbl.custom_minimum_size.x = 96
	row.add_child(lbl)
	var x_sb := SpinBox.new()
	x_sb.min_value = -1000; x_sb.max_value = 4000; x_sb.step = 1
	x_sb.value = x; x_sb.custom_minimum_size.x = 80
	x_sb.value_changed.connect(func(v: float) -> void: on_x.call(int(v)))
	row.add_child(x_sb)
	var y_sb := SpinBox.new()
	y_sb.min_value = -1000; y_sb.max_value = 4000; y_sb.step = 1
	y_sb.value = y; y_sb.custom_minimum_size.x = 80
	y_sb.value_changed.connect(func(v: float) -> void: on_y.call(int(v)))
	row.add_child(y_sb)
	parent.add_child(row)


func _add_int_row(parent: Node, label: String, v_init: int, lo: int, hi: int,
				cb: Callable) -> void:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 6)
	var lbl := Label.new()
	lbl.text = label
	lbl.add_theme_color_override("font_color", C_DIM)
	lbl.custom_minimum_size.x = 96
	row.add_child(lbl)
	var sb := SpinBox.new()
	sb.min_value = lo; sb.max_value = hi; sb.step = 1
	sb.value = v_init; sb.custom_minimum_size.x = 100
	sb.value_changed.connect(func(v: float) -> void: cb.call(int(v)))
	row.add_child(sb)
	parent.add_child(row)


func _add_float_row(parent: Node, label: String, v_init: float, lo: float, hi: float, step: float,
					cb: Callable) -> void:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 6)
	var lbl := Label.new()
	lbl.text = label
	lbl.add_theme_color_override("font_color", C_DIM)
	lbl.custom_minimum_size.x = 96
	row.add_child(lbl)
	var sb := SpinBox.new()
	sb.min_value = lo; sb.max_value = hi; sb.step = step
	sb.value = v_init; sb.custom_minimum_size.x = 100
	sb.value_changed.connect(func(v: float) -> void: cb.call(float(v)))
	row.add_child(sb)
	var slider := HSlider.new()
	slider.min_value = lo; slider.max_value = hi; slider.step = step
	slider.value = v_init
	slider.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	slider.custom_minimum_size.x = 100
	# Two-way sync between spinbox and slider
	slider.value_changed.connect(func(v: float) -> void:
		if sb.value != v:
			sb.value = v
		cb.call(float(v)))
	sb.value_changed.connect(func(v: float) -> void:
		if slider.value != v:
			slider.value = v)
	row.add_child(slider)
	parent.add_child(row)


# ── Export ────────────────────────────────────────────────────────────────────

func _build_export_json() -> String:
	if _composition == null:
		return "{}"
	var data: Dictionary = _composition.export_manifest()
	return JSON.stringify(data, "  ")


func _on_export_pressed() -> void:
	var text := _build_export_json()
	DisplayServer.clipboard_set(text)
	_set_status("copied %d chars to clipboard" % text.length())


func _on_save_pressed() -> void:
	var text := _build_export_json()
	var dir := "user://exports"
	DirAccess.make_dir_recursive_absolute(dir)
	var stamp := Time.get_datetime_string_from_system().replace(":", "").replace("-", "").replace("T", "_")
	var id: String = "composition"
	if _composition != null:
		id = str(_composition.composition_id())
	var path := dir + "/" + id + "_" + stamp + ".json"
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		_set_status("save FAILED: " + path)
		return
	f.store_string(text)
	f.close()
	_set_status("saved → " + path)


func _set_status(s: String) -> void:
	if _status_lbl != null:
		_status_lbl.text = s
