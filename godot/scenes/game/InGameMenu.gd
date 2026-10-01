extends Control
## In-game pause/menu overlay.
## Emits signals for actions that GameEngine or Main.gd handles.

signal resume_requested
signal save_requested(slot: int)
signal main_menu_requested
signal settings_opened
signal music_opened

const C_GOLD   := Color(0.78, 0.66, 0.29)
const C_BG     := Color(0.039, 0.031, 0.020, 0.97)
const C_BORDER := Color(0.70, 0.55, 0.24, 0.35)
const C_TXT    := Color(0.83, 0.79, 0.69)

var _active_slot: int = -1
var _save_status: Label = null
var _slot_overlay: Node = null


func open(active_slot: int) -> void:
	_active_slot = active_slot
	_rebuild()
	visible = true


func _input(event: InputEvent) -> void:
	if not visible:
		return
	# ESC / pad-back resumes play — mirrors the RESUME button exactly.
	# When the SAVE AS… slot picker is up, ESC closes that first.
	# set_input_as_handled() stops the event before GameEngine._input
	# (parent runs after children) so the same press can't re-open us.
	if event.is_action_pressed("ui_cancel") or event.is_action_pressed("menu_back"):
		get_viewport().set_input_as_handled()
		if _slot_overlay != null and is_instance_valid(_slot_overlay):
			_slot_overlay.queue_free()
			_slot_overlay = null
			return
		visible = false
		resume_requested.emit()


func _rebuild() -> void:
	for ch in get_children():
		ch.queue_free()

	var backdrop := ColorRect.new()
	backdrop.color = Color(0, 0, 0, 0.65)
	backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(backdrop)

	# Two columns (2026-10-01): the menu, and the save's picture + notes.
	var card := Panel.new()
	card.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	card.offset_left   = -430
	card.offset_right  = 430
	card.offset_top    = -250
	card.offset_bottom = 250
	var st := StyleBoxFlat.new()
	st.bg_color     = C_BG
	st.border_color = C_BORDER
	st.set_border_width_all(1)
	card.add_theme_stylebox_override("panel", st)
	add_child(card)

	var cols := HBoxContainer.new()
	cols.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	cols.offset_left   = 28
	cols.offset_right  = -28
	cols.offset_top    = 24
	cols.offset_bottom = -24
	cols.add_theme_constant_override("separation", 24)
	card.add_child(cols)

	var vbox := VBoxContainer.new()
	vbox.custom_minimum_size.x = 340
	vbox.add_theme_constant_override("separation", 10)
	cols.add_child(vbox)
	var notes_col := VBoxContainer.new()
	notes_col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	notes_col.add_theme_constant_override("separation", 8)

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
		_rebuild()          # the new picture
		_show_status("Saved to slot %d." % _active_slot)
	)
	vbox.add_child(save_btn)

	var saveas_btn := _nav_btn("SAVE AS…")
	saveas_btn.pressed.connect(_open_save_as)
	vbox.add_child(saveas_btn)

	_save_status = Label.new()
	_save_status.text = ""
	_save_status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		_save_status.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	_save_status.add_theme_font_size_override("font_size", 12)
	_save_status.add_theme_color_override("font_color", Color(0.6, 0.85, 0.5))
	vbox.add_child(_save_status)

	vbox.add_child(_rule())

	var settings_btn := _nav_btn("SETTINGS")
	settings_btn.pressed.connect(func() -> void: settings_opened.emit())
	vbox.add_child(settings_btn)

	var music_btn := _nav_btn("MUSIC PLAYER")
	music_btn.pressed.connect(func() -> void: music_opened.emit())
	vbox.add_child(music_btn)

	vbox.add_child(_rule())

	var resume_btn := _nav_btn("RESUME GAME")
	resume_btn.pressed.connect(func() -> void: visible = false; resume_requested.emit())
	vbox.add_child(resume_btn)

	var menu_btn := _nav_btn("MAIN MENU")
	menu_btn.add_theme_color_override("font_color", Color(0.7, 0.5, 0.3))
	menu_btn.pressed.connect(func() -> void: main_menu_requested.emit())
	vbox.add_child(menu_btn)

	cols.add_child(_vrule())
	cols.add_child(notes_col)
	_build_notes(notes_col)


## The save's picture and the player's notes (2026-10-01): "the save
## state should be a thumbnail with a notes section. Players can input
## these notes at any time." Saved as they type — to the active slot,
## or held for the first save when there is none yet.
func _build_notes(col: VBoxContainer) -> void:
	var head := Label.new()
	head.text = ("NOTES  ·  SLOT %d" % _active_slot) if _active_slot > 0 else "NOTES  ·  NOT SAVED YET"
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		head.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	head.add_theme_font_size_override("font_size", 12)
	head.add_theme_color_override("font_color", C_GOLD)
	col.add_child(head)

	var frame := PanelContainer.new()
	var fst := StyleBoxFlat.new()
	fst.bg_color = Color(0, 0, 0, 0.6)
	fst.border_color = C_BORDER
	fst.set_border_width_all(1)
	frame.add_theme_stylebox_override("panel", fst)
	frame.custom_minimum_size = Vector2(0, 216)
	col.add_child(frame)
	var thumb: Texture2D = SaveSystem.get_thumb(_active_slot) if _active_slot > 0 else null
	if thumb != null:
		var tr := TextureRect.new()
		tr.texture = thumb
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		tr.custom_minimum_size = Vector2(384, 216)
		frame.add_child(tr)
	else:
		var none := Label.new()
		none.text = "no picture yet — save to keep this moment"
		none.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		none.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		none.add_theme_color_override("font_color", Color(C_TXT.r, C_TXT.g, C_TXT.b, 0.5))
		none.add_theme_font_size_override("font_size", 12)
		frame.add_child(none)

	var te := TextEdit.new()
	te.size_flags_vertical = Control.SIZE_EXPAND_FILL
	te.custom_minimum_size.y = 110
	te.wrap_mode = TextEdit.LINE_WRAPPING_BOUNDARY
	te.placeholder_text = "Your notes for this save — who you suspect, what to try next, where you left off…"
	te.text = SaveSystem.get_notes(_active_slot)
	te.add_theme_font_size_override("font_size", 13)
	te.add_theme_color_override("font_color", C_TXT)
	var tst := StyleBoxFlat.new()
	tst.bg_color = Color(0.02, 0.016, 0.01, 0.95)
	tst.border_color = C_BORDER
	tst.set_border_width_all(1)
	tst.content_margin_left = 8.0
	tst.content_margin_right = 8.0
	tst.content_margin_top = 6.0
	tst.content_margin_bottom = 6.0
	te.add_theme_stylebox_override("normal", tst)
	te.add_theme_stylebox_override("focus", tst)
	te.text_changed.connect(func() -> void: SaveSystem.set_notes(_active_slot, te.text))
	col.add_child(te)

	var hint := Label.new()
	hint.text = "Saved as you type." + ("  On Steam Deck, STEAM + X opens the keyboard." if Input.get_connected_joypads().size() > 0 else "")
	hint.add_theme_font_size_override("font_size", 12)
	hint.add_theme_color_override("font_color", Color(C_TXT.r, C_TXT.g, C_TXT.b, 0.55))
	col.add_child(hint)


func _open_save_as() -> void:
	var slot_overlay := preload("res://scenes/menu/SaveSlotOverlay.tscn").instantiate()
	add_child(slot_overlay)
	_slot_overlay = slot_overlay
	slot_overlay.open("new", func(slot: int, _sd: Dictionary) -> void:
		slot_overlay.queue_free()
		_slot_overlay = null
		save_requested.emit(slot)
		_active_slot = slot
		_show_status("Saved to slot %d." % slot)
		_rebuild()
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
	btn.add_theme_font_size_override("font_size", 12)
	btn.add_theme_color_override("font_color", C_TXT)
	btn.add_theme_color_override("font_hover_color", C_GOLD)
	btn.add_theme_color_override("font_focus_color", C_GOLD)
	return btn


func _rule() -> ColorRect:
	var r := ColorRect.new()
	r.color = C_BORDER
	r.custom_minimum_size.y = 1
	return r


func _vrule() -> ColorRect:
	var r := ColorRect.new()
	r.color = C_BORDER
	r.custom_minimum_size.x = 1
	return r
