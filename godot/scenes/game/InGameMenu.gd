extends Control
## In-game pause/menu overlay.
## Emits signals for actions that GameEngine or Main.gd handles.

signal resume_requested
signal save_requested(slot: int)
signal load_requested(slot: int)
signal main_menu_requested
signal settings_opened
signal music_opened
signal backlog_opened

const C_GOLD   := Color(0.78, 0.66, 0.29)
const C_BG     := Color(0.039, 0.031, 0.020, 0.97)
const C_BORDER := Color(0.70, 0.55, 0.24, 0.35)
const C_TXT    := Color(0.83, 0.79, 0.69)

var _active_slot: int = -1
var _save_status: Label = null


func open(active_slot: int) -> void:
	_active_slot = active_slot
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
	card.offset_left   = -200
	card.offset_right  = 200
	card.offset_top    = -240
	card.offset_bottom = 240
	var st := StyleBoxFlat.new()
	st.bg_color     = C_BG
	st.border_color = C_BORDER
	st.set_border_width_all(1)
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

	var title := Label.new()
	title.text = "GAME MENU"
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		title.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	title.add_theme_font_size_override("font_size", 13)
	title.add_theme_color_override("font_color", C_GOLD)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vbox.add_child(title)

	vbox.add_child(_rule())

	# Quick save
	var save_btn := _nav_btn("QUICK SAVE  (Slot %d)" % _active_slot if _active_slot > 0 else "QUICK SAVE  (no slot)")
	save_btn.disabled = _active_slot < 1
	save_btn.pressed.connect(func() -> void:
		save_requested.emit(_active_slot)
		_show_status("Saved to slot %d." % _active_slot)
	)
	vbox.add_child(save_btn)

	var saveas_btn := _nav_btn("SAVE AS…")
	saveas_btn.pressed.connect(_open_save_as)
	vbox.add_child(saveas_btn)

	var load_btn := _nav_btn("LOAD GAME…")
	load_btn.pressed.connect(_open_load)
	vbox.add_child(load_btn)

	_save_status = Label.new()
	_save_status.text = ""
	_save_status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		_save_status.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	_save_status.add_theme_font_size_override("font_size", 10)
	_save_status.add_theme_color_override("font_color", Color(0.6, 0.85, 0.5))
	vbox.add_child(_save_status)

	vbox.add_child(_rule())

	var settings_btn := _nav_btn("SETTINGS")
	settings_btn.pressed.connect(func() -> void: settings_opened.emit())
	vbox.add_child(settings_btn)

	var music_btn := _nav_btn("MUSIC PLAYER")
	music_btn.pressed.connect(func() -> void: music_opened.emit())
	vbox.add_child(music_btn)

	var backlog_btn := _nav_btn("BACKLOG")
	backlog_btn.pressed.connect(func() -> void: backlog_opened.emit())
	vbox.add_child(backlog_btn)

	vbox.add_child(_rule())

	var resume_btn := _nav_btn("RESUME GAME")
	resume_btn.pressed.connect(func() -> void: visible = false; resume_requested.emit())
	vbox.add_child(resume_btn)

	var menu_btn := _nav_btn("MAIN MENU")
	menu_btn.add_theme_color_override("font_color", Color(0.7, 0.5, 0.3))
	menu_btn.pressed.connect(func() -> void: main_menu_requested.emit())
	vbox.add_child(menu_btn)


func _open_save_as() -> void:
	var slot_overlay := preload("res://scenes/menu/SaveSlotOverlay.tscn").instantiate()
	add_child(slot_overlay)
	slot_overlay.open("new", func(slot: int, _sd: Dictionary) -> void:
		slot_overlay.queue_free()
		save_requested.emit(slot)
		_active_slot = slot
		_show_status("Saved to slot %d." % slot)
		_rebuild()
	)


func _open_load() -> void:
	var slot_overlay := preload("res://scenes/menu/SaveSlotOverlay.tscn").instantiate()
	add_child(slot_overlay)
	slot_overlay.open("continue", func(slot: int, _sd: Dictionary) -> void:
		slot_overlay.queue_free()
		load_requested.emit(slot)
	)


func _show_status(msg: String) -> void:
	if _save_status:
		_save_status.text = msg


func _nav_btn(text: String) -> Button:
	var btn := Button.new()
	btn.text = text
	btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	btn.custom_minimum_size.y = 36
	btn.alignment = HORIZONTAL_ALIGNMENT_CENTER
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		btn.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	btn.add_theme_font_size_override("font_size", 11)
	btn.add_theme_color_override("font_color", C_TXT)
	btn.add_theme_color_override("font_hover_color", C_GOLD)
	btn.add_theme_color_override("font_focus_color", C_GOLD)
	return btn


func _rule() -> ColorRect:
	var r := ColorRect.new()
	r.color = C_BORDER
	r.custom_minimum_size.y = 1
	return r
