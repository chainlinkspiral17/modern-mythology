extends Control
## Backlog / dialogue-history overlay. Shows the engine's _log — every
## narrate / say / think line so far — newest at the bottom. Opened from
## the in-game pause menu. Esc, ✕ or a backdrop click closes it.

signal closed

const C_GOLD   := Color(0.78, 0.66, 0.29)
const C_BG     := Color(0.039, 0.031, 0.020, 0.97)
const C_BORDER := Color(0.70, 0.55, 0.24, 0.35)
const C_TXT    := Color(0.83, 0.79, 0.69)
const C_DIM    := Color(0.55, 0.50, 0.42)

var _scroll: ScrollContainer = null


func open(log_entries: Array) -> void:
	_rebuild(log_entries)
	visible = true
	# Jump to the most recent line once the scrollbar knows its range.
	if _scroll != null:
		await get_tree().process_frame
		_scroll.scroll_vertical = int(_scroll.get_v_scroll_bar().max_value)


func _input(event: InputEvent) -> void:
	if not visible:
		return
	if event.is_action_pressed("menu_back"):
		get_viewport().set_input_as_handled()
		_close()


func _close() -> void:
	visible = false
	closed.emit()


func _rebuild(log_entries: Array) -> void:
	for ch in get_children():
		ch.queue_free()

	var backdrop := ColorRect.new()
	backdrop.color = Color(0, 0, 0, 0.72)
	backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	backdrop.gui_input.connect(func(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and ev.pressed:
			_close())
	add_child(backdrop)

	var card := Panel.new()
	card.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	card.offset_left   = -420
	card.offset_right  = 420
	card.offset_top    = -300
	card.offset_bottom = 300
	var st := StyleBoxFlat.new()
	st.bg_color     = C_BG
	st.border_color = C_BORDER
	st.set_border_width_all(1)
	card.add_theme_stylebox_override("panel", st)
	add_child(card)

	var vbox := VBoxContainer.new()
	vbox.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	vbox.offset_left   = 24
	vbox.offset_right  = -24
	vbox.offset_top    = 18
	vbox.offset_bottom = -18
	vbox.add_theme_constant_override("separation", 8)
	card.add_child(vbox)

	var header := HBoxContainer.new()
	vbox.add_child(header)
	var title := Label.new()
	title.text = "BACKLOG"
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		title.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	title.add_theme_font_size_override("font_size", 13)
	title.add_theme_color_override("font_color", C_GOLD)
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(title)
	var close_btn := Button.new()
	close_btn.text = "✕"
	close_btn.custom_minimum_size = Vector2(30, 30)
	close_btn.pressed.connect(_close)
	header.add_child(close_btn)

	var rule := ColorRect.new()
	rule.color = C_BORDER
	rule.custom_minimum_size.y = 1
	vbox.add_child(rule)

	_scroll = ScrollContainer.new()
	_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_child(_scroll)

	var lines := VBoxContainer.new()
	lines.add_theme_constant_override("separation", 10)
	lines.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_scroll.add_child(lines)

	if log_entries.is_empty():
		var empty := Label.new()
		empty.text = "Nothing yet."
		empty.add_theme_color_override("font_color", C_DIM)
		lines.add_child(empty)
		return

	for entry_v in log_entries:
		if typeof(entry_v) != TYPE_DICTIONARY:
			continue
		var entry: Dictionary = entry_v
		lines.add_child(_entry_row(entry))


func _entry_row(entry: Dictionary) -> VBoxContainer:
	var row := VBoxContainer.new()
	row.add_theme_constant_override("separation", 2)
	row.size_flags_horizontal = Control.SIZE_EXPAND_FILL

	var role: String = str(entry.get("role", "narrate"))
	var who: String  = str(entry.get("char", ""))
	if who != "" and role != "narrate":
		var name_lbl := Label.new()
		name_lbl.text = who.to_upper() if role == "say" else who.to_upper() + "  (thinking)"
		if ResourceLoader.exists(SkinDB.F_CINZEL):
			name_lbl.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
		name_lbl.add_theme_font_size_override("font_size", 10)
		name_lbl.add_theme_color_override("font_color", C_GOLD)
		row.add_child(name_lbl)

	var text_lbl := Label.new()
	text_lbl.text = str(entry.get("text", ""))
	text_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	text_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	if ResourceLoader.exists(SkinDB.F_IMFELL_R):
		text_lbl.add_theme_font_override("font", load(SkinDB.F_IMFELL_R) as Font)
	text_lbl.add_theme_font_size_override("font_size", 13)
	text_lbl.add_theme_color_override("font_color", C_DIM if role == "narrate" else C_TXT)
	row.add_child(text_lbl)
	return row
