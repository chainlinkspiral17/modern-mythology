extends Control
## Save slot picker overlay.
## mode "new"      → all 8 slots shown; choosing writes a new save
## mode "continue" → only filled slots shown; choosing loads that save
## callback(slot: int, save_data: Dictionary)  save_data={} for new game

signal closed

const C_GOLD   := Color(0.78, 0.66, 0.29)
const C_DIM    := Color(0.50, 0.47, 0.38, 0.7)
const C_BG     := Color(0.039, 0.031, 0.020, 0.97)
const C_BORDER := Color(0.70, 0.55, 0.24, 0.35)
const C_TXT    := Color(0.83, 0.79, 0.69)

var _mode:     String   = "new"
var _callback: Callable
var _saves:    Array    = []


func open(mode: String, callback: Callable) -> void:
	_mode     = mode
	_callback = callback
	# The autosave (slot 0) is offered when loading, never as a manual
	# save target.
	_saves    = SaveSystem.list_saves(_mode == "continue")
	_rebuild()
	visible = true


func _rebuild() -> void:
	for ch in get_children():
		ch.queue_free()

	# Dim backdrop
	var backdrop := ColorRect.new()
	backdrop.color = Color(0, 0, 0, 0.65)
	backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	backdrop.gui_input.connect(func(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
			_close()
	)
	add_child(backdrop)

	# Card panel
	var card := Panel.new()
	card.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	card.offset_left   = -320
	card.offset_right  = 320
	card.offset_top    = -300
	card.offset_bottom = 300
	var st := StyleBoxFlat.new()
	st.bg_color     = C_BG
	st.border_color = C_BORDER
	st.set_border_width_all(1)
	st.content_margin_left   = 28.0
	st.content_margin_right  = 28.0
	st.content_margin_top    = 24.0
	st.content_margin_bottom = 24.0
	card.add_theme_stylebox_override("panel", st)
	add_child(card)

	var vbox := VBoxContainer.new()
	vbox.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	vbox.offset_left   = 28
	vbox.offset_right  = -28
	vbox.offset_top    = 24
	vbox.offset_bottom = -24
	vbox.add_theme_constant_override("separation", 10)
	card.add_child(vbox)

	var title_txt := "NEW GAME — SELECT SLOT" if _mode == "new" else "CONTINUE — SELECT SAVE"
	var title := _make_label(title_txt, SkinDB.F_CINZEL, 13, C_GOLD)
	title.custom_minimum_size.y = 28
	vbox.add_child(title)

	vbox.add_child(_make_rule())

	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_child(scroll)

	var slot_vbox := VBoxContainer.new()
	slot_vbox.add_theme_constant_override("separation", 6)
	slot_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(slot_vbox)

	for save_data: Dictionary in _saves:
		var slot: int = int(save_data.get("slot", 0))
		var is_empty: bool = save_data.get("empty", false)
		if _mode == "continue" and is_empty:
			continue

		var btn := Button.new()
		btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		btn.custom_minimum_size.y = 52

		var slot_style := StyleBoxFlat.new()
		slot_style.bg_color     = Color(C_BORDER.r, C_BORDER.g, C_BORDER.b, 0.06)
		slot_style.border_color = Color(C_BORDER.r, C_BORDER.g, C_BORDER.b, 0.25)
		slot_style.set_border_width_all(1)
		slot_style.content_margin_left   = 12.0
		slot_style.content_margin_right  = 12.0
		slot_style.content_margin_top    = 8.0
		slot_style.content_margin_bottom = 8.0
		btn.add_theme_stylebox_override("normal", slot_style)

		var hover_style: StyleBoxFlat = slot_style.duplicate() as StyleBoxFlat
		hover_style.bg_color     = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.08)
		hover_style.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.5)
		btn.add_theme_stylebox_override("hover",   hover_style)
		btn.add_theme_stylebox_override("focus",   hover_style)
		btn.add_theme_stylebox_override("pressed", hover_style)

		if ResourceLoader.exists(SkinDB.F_IMFELL_R):
			btn.add_theme_font_override("font", load(SkinDB.F_IMFELL_R) as Font)
		btn.add_theme_color_override("font_color",        C_TXT)
		btn.add_theme_color_override("font_hover_color",  C_GOLD)
		btn.add_theme_color_override("font_focus_color",  C_GOLD)
		btn.add_theme_font_size_override("font_size", 14)

		if is_empty:
			btn.text = "  SLOT %d    —    EMPTY" % slot
		else:
			var scene_id: String = save_data.get("scene", "")
			var vol: int = int(save_data.get("vol", 0))
			var ts: float = float(save_data.get("ts", 0))
			var dt := Time.get_datetime_dict_from_unix_time(int(ts))
			var slot_label := "AUTO  " if slot == SaveSystem.AUTOSAVE_SLOT else "SLOT %d" % slot
			btn.text = "  %s    Vol.%d  ·  %s\n  %02d/%02d/%d  %02d:%02d" % [
				slot_label, vol, scene_id,
				dt.get("month", 0), dt.get("day", 0), dt.get("year", 0),
				dt.get("hour", 0),  dt.get("minute", 0)
			]

		if _mode == "continue" and is_empty:
			btn.disabled = true
		else:
			var sd: Dictionary = save_data
			var sl: int = slot
			btn.pressed.connect(func() -> void: _pick(sl, sd if not sd.get("empty", false) else {}))

		if not is_empty and _mode == "new":
			var del_btn := Button.new()
			del_btn.text = "✕"
			del_btn.custom_minimum_size = Vector2(28, 28)
			del_btn.add_theme_color_override("font_color", Color(0.8, 0.3, 0.3))
			var sl: int = slot
			del_btn.pressed.connect(func() -> void: _delete_slot(sl))
			# wrap button + delete in hbox
			var hbox := HBoxContainer.new()
			hbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			hbox.add_child(btn)
			btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			hbox.add_child(del_btn)
			slot_vbox.add_child(hbox)
		else:
			slot_vbox.add_child(btn)

	vbox.add_child(_make_rule())

	var back_btn := Button.new()
	back_btn.text = "CANCEL"
	back_btn.custom_minimum_size.y = 36
	back_btn.pressed.connect(_close)
	vbox.add_child(back_btn)


func _pick(slot: int, save_data: Dictionary) -> void:
	visible = false
	if _callback.is_valid():
		_callback.call(slot, save_data)


func _delete_slot(slot: int) -> void:
	SaveSystem.delete_save(slot)
	_saves = SaveSystem.list_saves(_mode == "continue")
	_rebuild()


func _close() -> void:
	visible = false
	closed.emit()


func _make_label(text: String, font_path: String, size: int, col: Color) -> Label:
	var lbl := Label.new()
	lbl.text = text
	if ResourceLoader.exists(font_path):
		lbl.add_theme_font_override("font", load(font_path) as Font)
	lbl.add_theme_font_size_override("font_size", size)
	lbl.add_theme_color_override("font_color", col)
	return lbl


func _make_rule() -> ColorRect:
	var r := ColorRect.new()
	r.color = C_BORDER
	r.custom_minimum_size.y = 1
	return r
