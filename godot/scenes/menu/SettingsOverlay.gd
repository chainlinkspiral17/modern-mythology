extends Control
## Settings overlay — text speed, font size, screen resolution, audio, misc.

signal closed

const C_GOLD   := Color(0.78, 0.66, 0.29)
const C_BG     := Color(0.039, 0.031, 0.020, 0.97)
const C_BORDER := Color(0.70, 0.55, 0.24, 0.35)
const C_TXT    := Color(0.83, 0.79, 0.69)
const C_DIM    := Color(0.50, 0.47, 0.38, 0.7)


func open() -> void:
	_rebuild()
	visible = true


func _rebuild() -> void:
	for ch in get_children():
		ch.queue_free()

	var backdrop := ColorRect.new()
	backdrop.color = Color(0, 0, 0, 0.65)
	backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(backdrop)

	var card := Panel.new()
	card.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	card.offset_left   = -310
	card.offset_right  = 310
	card.offset_top    = -360
	card.offset_bottom = 360
	var st := StyleBoxFlat.new()
	st.bg_color     = C_BG
	st.border_color = C_BORDER
	st.set_border_width_all(1)
	card.add_theme_stylebox_override("panel", st)
	add_child(card)

	# Scrollable content inside the card
	var scroll := ScrollContainer.new()
	scroll.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scroll.offset_left   = 0
	scroll.offset_right  = 0
	scroll.offset_top    = 0
	scroll.offset_bottom = 0
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	card.add_child(scroll)

	var vbox := VBoxContainer.new()
	vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vbox.offset_left   = 32
	vbox.offset_right  = -32
	vbox.add_theme_constant_override("separation", 14)
	scroll.add_child(vbox)

	# Top padding
	var top_pad := Control.new()
	top_pad.custom_minimum_size.y = 24
	vbox.add_child(top_pad)

	# Header row with close button
	var header_row := HBoxContainer.new()
	vbox.add_child(header_row)
	var heading_lbl := _heading("SETTINGS")
	heading_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header_row.add_child(heading_lbl)
	var close_btn_top := Button.new()
	close_btn_top.text = "✕"
	close_btn_top.custom_minimum_size = Vector2(32, 32)
	close_btn_top.pressed.connect(func() -> void: visible = false; closed.emit())
	header_row.add_child(close_btn_top)

	vbox.add_child(_rule())

	# ── TEXT SPEED ────────────────────────────────────────────────────────────
	vbox.add_child(_row_label("TEXT SPEED"))
	vbox.add_child(_button_row(
		["SLOW", "NORMAL", "FAST"],
		Settings.text_speed.to_upper(),
		func(v: String) -> void: Settings.text_speed = v.to_lower()
	))

	vbox.add_child(_rule())

	# ── FONT SIZE ─────────────────────────────────────────────────────────────
	vbox.add_child(_font_size_section())

	vbox.add_child(_rule())

	# ── SCREEN SIZE ───────────────────────────────────────────────────────────
	vbox.add_child(_screen_size_section())

	vbox.add_child(_rule())

	# ── AUDIO ─────────────────────────────────────────────────────────────────
	vbox.add_child(_slider_row("MUSIC VOLUME", Settings.bgm_vol,
		func(v: float) -> void:
			Settings.bgm_vol = v
			AudioMgr.set_bus_volume("BGM", v)
	))
	vbox.add_child(_slider_row("SFX VOLUME", Settings.sfx_vol,
		func(v: float) -> void:
			Settings.sfx_vol = v
			AudioMgr.set_bus_volume("SFX", v)
	))

	vbox.add_child(_rule())

	# ── MISC ──────────────────────────────────────────────────────────────────
	vbox.add_child(_toggle_row("SKIP UNREAD TEXT", Settings.skip_unread,
		func(v: bool) -> void: Settings.skip_unread = v
	))

	vbox.add_child(_row_label("AUTO ADVANCE"))
	var aa_options := ["OFF", "1 SEC", "3 SEC", "5 SEC"]
	var aa_values  := [0, 1000, 3000, 5000]
	var aa_current := "OFF"
	for i in aa_values.size():
		if aa_values[i] == Settings.auto_advance_ms:
			aa_current = aa_options[i]
	vbox.add_child(_button_row(aa_options, aa_current,
		func(v: String) -> void:
			var idx := aa_options.find(v)
			Settings.auto_advance_ms = aa_values[idx] if idx >= 0 else 0
	))

	# Bottom padding
	var bot_pad := Control.new()
	bot_pad.custom_minimum_size.y = 24
	vbox.add_child(bot_pad)


func _screen_size_section() -> VBoxContainer:
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 8)
	col.add_child(_row_label("SCREEN SIZE"))

	# Track pending selection without immediately applying. Boxed in an
	# Array because GDScript lambdas capture locals by value — a bare
	# `pending = ...` inside the picker lambda would mutate its own
	# copy and APPLY would never see the new selection.
	var pending: Array = [Settings.window_mode]

	var btn_row := _button_row(
		["720p", "900p", "1080p", "FULLSCREEN"],
		Settings.window_mode.to_upper(),
		func(v: String) -> void: pending[0] = v.to_lower()
	)
	col.add_child(btn_row)

	var hint := Label.new()
	hint.text = "720p = 1280×720  ·  900p = 1600×900  ·  1080p = 1920×1080"
	hint.add_theme_font_size_override("font_size", 9)
	hint.add_theme_color_override("font_color", C_DIM)
	col.add_child(hint)

	var action_row := HBoxContainer.new()
	action_row.add_theme_constant_override("separation", 8)

	var apply_btn := Button.new()
	apply_btn.text = "APPLY"
	apply_btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	apply_btn.custom_minimum_size.y = 32
	_style_toggle_btn(apply_btn, true)
	apply_btn.pressed.connect(func() -> void:
		Settings.window_mode = pending[0]
	)
	action_row.add_child(apply_btn)

	var reset_btn := Button.new()
	reset_btn.text = "RESET TO 720p"
	reset_btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	reset_btn.custom_minimum_size.y = 32
	_style_toggle_btn(reset_btn, false)
	reset_btn.pressed.connect(func() -> void:
		Settings.window_mode = "720p"
		_rebuild()
	)
	action_row.add_child(reset_btn)
	col.add_child(action_row)

	return col


func _font_size_section() -> VBoxContainer:
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 6)

	# Label + live % display
	var hdr := HBoxContainer.new()
	var lbl := _row_label("FONT SIZE")
	lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hdr.add_child(lbl)
	var pct_lbl := Label.new()
	pct_lbl.text = "%d%%" % int(Settings.txt_scale * 100.0)
	pct_lbl.add_theme_font_size_override("font_size", 12)
	pct_lbl.add_theme_color_override("font_color", C_TXT)
	pct_lbl.custom_minimum_size.x = 52
	hdr.add_child(pct_lbl)
	col.add_child(hdr)

	# Slider — 50 % … 300 %
	var slider := HSlider.new()
	slider.min_value = 0.5
	slider.max_value = 3.0
	slider.step      = 0.05
	slider.value     = Settings.txt_scale
	slider.custom_minimum_size.y = 24
	slider.value_changed.connect(func(v: float) -> void:
		pct_lbl.text = "%d%%" % int(v * 100.0)
		Settings.txt_scale = v
	)
	col.add_child(slider)

	# Tick labels below slider
	var ticks := HBoxContainer.new()
	for pct: int in [50, 100, 150, 200, 250, 300]:
		var t := Label.new()
		t.text = "%d%%" % pct
		t.add_theme_font_size_override("font_size", 8)
		t.add_theme_color_override("font_color", C_DIM)
		t.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		ticks.add_child(t)
	col.add_child(ticks)

	# Reset to 100% shortcut
	var reset_btn := Button.new()
	reset_btn.text = "RESET TO 100%"
	reset_btn.custom_minimum_size.y = 28
	reset_btn.pressed.connect(func() -> void:
		slider.value = 1.0
		pct_lbl.text = "100%"
		Settings.txt_scale = 1.0
	)
	col.add_child(reset_btn)

	return col


func _heading(text: String) -> Label:
	var lbl := Label.new()
	lbl.text = text
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		lbl.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	lbl.add_theme_font_size_override("font_size", 13)
	lbl.add_theme_color_override("font_color", C_GOLD)
	return lbl


func _rule() -> ColorRect:
	var r := ColorRect.new()
	r.color = C_BORDER
	r.custom_minimum_size.y = 1
	return r


func _row_label(text: String) -> Label:
	var lbl := Label.new()
	lbl.text = text
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		lbl.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	lbl.add_theme_font_size_override("font_size", 10)
	lbl.add_theme_color_override("font_color", Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.7))
	return lbl


func _button_row(options: Array, current: String, on_pick: Callable) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 6)
	for opt: String in options:
		var btn := Button.new()
		btn.text = opt
		btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		btn.custom_minimum_size.y = 32
		var is_active: bool = (opt.to_upper() == current.to_upper())
		_style_toggle_btn(btn, is_active)
		var v: String = opt
		var r: HBoxContainer = row
		var cb: Callable = on_pick
		btn.pressed.connect(func() -> void:
			cb.call(v)
			for child in r.get_children():
				if child is Button:
					_style_toggle_btn(child as Button,
						(child as Button).text.to_upper() == v.to_upper())
		)
		row.add_child(btn)
	return row


func _style_toggle_btn(btn: Button, active: bool) -> void:
	var st := StyleBoxFlat.new()
	st.bg_color     = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.15) if active else Color(0, 0, 0, 0.3)
	st.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.6)  if active else C_BORDER
	st.set_border_width_all(1)
	st.content_margin_top    = 6.0
	st.content_margin_bottom = 6.0
	st.content_margin_left   = 8.0
	st.content_margin_right  = 8.0
	btn.add_theme_stylebox_override("normal",  st)
	btn.add_theme_stylebox_override("hover",   st)
	btn.add_theme_stylebox_override("pressed", st)
	btn.add_theme_stylebox_override("focus",   st)
	btn.add_theme_color_override("font_color",         C_GOLD if active else C_DIM)
	btn.add_theme_color_override("font_hover_color",   C_GOLD)
	btn.add_theme_color_override("font_focus_color",   C_GOLD)
	btn.add_theme_color_override("font_pressed_color", C_GOLD)
	btn.add_theme_font_size_override("font_size", 11)
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		btn.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)


func _slider_row(label: String, init_val: float, on_change: Callable) -> VBoxContainer:
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 4)
	var header := HBoxContainer.new()
	var lbl := _row_label(label)
	lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(lbl)
	var val_lbl := Label.new()
	val_lbl.text = "%d%%" % int(init_val * 100)
	val_lbl.add_theme_font_size_override("font_size", 10)
	val_lbl.add_theme_color_override("font_color", C_TXT)
	header.add_child(val_lbl)
	col.add_child(header)
	var slider := HSlider.new()
	slider.min_value = 0.0
	slider.max_value = 1.0
	slider.step      = 0.01
	slider.value     = init_val
	slider.custom_minimum_size.y = 20
	slider.value_changed.connect(func(v: float) -> void:
		val_lbl.text = "%d%%" % int(v * 100)
		on_change.call(v)
	)
	col.add_child(slider)
	return col


func _toggle_row(label: String, init_val: bool, on_change: Callable) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	var lbl := _row_label(label)
	lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(lbl)
	var chk := CheckButton.new()
	chk.button_pressed = init_val
	chk.toggled.connect(func(v: bool) -> void: on_change.call(v))
	row.add_child(chk)
	return row
