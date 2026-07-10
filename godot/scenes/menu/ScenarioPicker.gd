extends Control
## ScenarioPicker — a small overlay that pops up from a GauntletHost
## when there are multiple scenarios at that locale.
##
## Shows up to four card entries with title / difficulty / subtitle
## and hotkeys (1 / 2 / 3 / 4). Player clicks a card OR presses the
## number to launch. Escape or click-outside closes without launching.
##
## Called by a host script's `open_picker(entries)` helper. Each
## entry is a Dictionary:
##   { launch_fn: Callable, title, subtitle, difficulty, hotkey }
##
## F4-compliant via add_to_group("ui").

signal picked(entry_index: int)
signal dismissed

const C_GOLD      := Color(0.92, 0.78, 0.40)
const C_GOLD_DIM  := Color(0.70, 0.55, 0.24, 0.45)
const C_BG        := Color(0.024, 0.020, 0.014, 0.97)
const C_TXT       := Color(0.83, 0.79, 0.69)
const C_TXT_DIM   := Color(0.50, 0.47, 0.38)
const C_EASY      := Color(0.55, 0.85, 0.55)
const C_MED       := Color(0.85, 0.75, 0.35)
const C_HARD      := Color(0.85, 0.45, 0.45)

var _entries: Array = []


func present(entries: Array) -> void:
	_entries = entries
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	var bank := get_node_or_null("/root/SFXBank")
	if bank: bank.play("scenario_picker", 0.75)
	_build()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var k := event as InputEventKey
		if k.keycode == KEY_ESCAPE:
			get_viewport().set_input_as_handled()
			_dismiss()
			return
		# Hotkeys 1-4 launch by index
		var idx: int = -1
		match k.keycode:
			KEY_1: idx = 0
			KEY_2: idx = 1
			KEY_3: idx = 2
			KEY_4: idx = 3
		if idx >= 0 and idx < _entries.size():
			get_viewport().set_input_as_handled()
			_launch(idx)


func _build() -> void:
	# Backdrop dim
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.86)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.gui_input.connect(func(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
			_dismiss()
	)
	add_child(dim)

	var card_h := 110
	var card_w := 640
	var gap := 12
	var n := _entries.size()
	var total_h := card_h * n + gap * (n - 1) + 100

	var panel := Panel.new()
	panel.set_anchors_preset(Control.PRESET_CENTER)
	panel.offset_left = -card_w / 2 - 24
	panel.offset_right = card_w / 2 + 24
	panel.offset_top = -total_h / 2
	panel.offset_bottom = total_h / 2
	var st := StyleBoxFlat.new()
	st.bg_color = C_BG
	st.border_color = C_GOLD_DIM
	st.set_border_width_all(1)
	panel.add_theme_stylebox_override("panel", st)
	add_child(panel)

	var vb := VBoxContainer.new()
	vb.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	vb.offset_left = 20
	vb.offset_right = -20
	vb.offset_top = 16
	vb.offset_bottom = -16
	vb.add_theme_constant_override("separation", gap)
	panel.add_child(vb)

	var hdr := Label.new()
	hdr.text = "CHOOSE A SCENARIO"
	hdr.add_theme_color_override("font_color", C_GOLD)
	hdr.add_theme_font_size_override("font_size", 13)
	hdr.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(hdr)

	var rule := ColorRect.new()
	rule.color = Color(C_GOLD_DIM.r, C_GOLD_DIM.g, C_GOLD_DIM.b, 0.25)
	rule.custom_minimum_size.y = 1
	vb.add_child(rule)

	# One card per entry
	for i in range(_entries.size()):
		var entry: Dictionary = _entries[i]
		vb.add_child(_build_card(i, entry))

	# Footer hint
	var footer := Label.new()
	footer.text = "PRESS 1-%d  ·  CLICK A CARD  ·  ESCAPE TO CANCEL" % _entries.size()
	footer.add_theme_color_override("font_color", C_TXT_DIM)
	footer.add_theme_font_size_override("font_size", 12)
	footer.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(footer)


func _build_card(index: int, entry: Dictionary) -> Control:
	var btn := Button.new()
	btn.custom_minimum_size.y = 92
	btn.flat = false
	btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
	# Style the button as a card
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(C_GOLD.r * 0.08, C_GOLD.g * 0.06, C_GOLD.b * 0.04, 0.6)
	sb.border_color = C_GOLD_DIM
	sb.set_border_width_all(1)
	sb.content_margin_left = 16
	sb.content_margin_right = 16
	sb.content_margin_top = 12
	sb.content_margin_bottom = 12
	btn.add_theme_stylebox_override("normal", sb)
	var sb_hi := sb.duplicate() as StyleBoxFlat
	sb_hi.bg_color = Color(C_GOLD.r * 0.16, C_GOLD.g * 0.12, C_GOLD.b * 0.08, 0.8)
	sb_hi.border_color = C_GOLD
	btn.add_theme_stylebox_override("hover", sb_hi)
	btn.add_theme_stylebox_override("focus", sb_hi)
	btn.pressed.connect(func() -> void: _launch(index))

	# Build the card content inside the button
	var hbox := HBoxContainer.new()
	hbox.add_theme_constant_override("separation", 14)
	hbox.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hbox.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	btn.add_child(hbox)

	# Hotkey badge
	var hotkey := Label.new()
	hotkey.text = "%d" % (index + 1)
	hotkey.add_theme_color_override("font_color", C_GOLD)
	hotkey.add_theme_font_size_override("font_size", 26)
	hotkey.custom_minimum_size = Vector2(30, 0)
	hotkey.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	hbox.add_child(hotkey)

	# Text column
	var col := VBoxContainer.new()
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col.add_theme_constant_override("separation", 2)
	hbox.add_child(col)

	var title := Label.new()
	title.text = String(entry.get("title", "?"))
	title.add_theme_color_override("font_color", C_TXT)
	title.add_theme_font_size_override("font_size", 13)
	col.add_child(title)

	var sub := Label.new()
	sub.text = String(entry.get("subtitle", ""))
	sub.add_theme_color_override("font_color", C_TXT_DIM)
	sub.add_theme_font_size_override("font_size", 12)
	sub.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	sub.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col.add_child(sub)

	# Difficulty badge
	var diff := String(entry.get("difficulty", "medium")).to_lower()
	var diff_lbl := Label.new()
	diff_lbl.text = diff.to_upper()
	diff_lbl.add_theme_font_size_override("font_size", 12)
	diff_lbl.custom_minimum_size = Vector2(70, 0)
	diff_lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	diff_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	match diff:
		"easy":  diff_lbl.add_theme_color_override("font_color", C_EASY)
		"hard":  diff_lbl.add_theme_color_override("font_color", C_HARD)
		_:       diff_lbl.add_theme_color_override("font_color", C_MED)
	hbox.add_child(diff_lbl)

	return btn


func _launch(index: int) -> void:
	if index < 0 or index >= _entries.size():
		return
	var entry: Dictionary = _entries[index]
	var cb: Callable = entry.get("launch_fn", Callable())
	picked.emit(index)
	if cb.is_valid():
		cb.call()
	# The host now owns the game instance; close the picker.
	queue_free()


func _dismiss() -> void:
	dismissed.emit()
	queue_free()
