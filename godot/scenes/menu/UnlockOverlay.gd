extends Control
## Reusable unlock notification card.
## Call show_unlock(data) where data has: type, title, desc (optional).
## Emits `dismissed` when the card is gone. Auto-dismisses after DURATION seconds.

signal dismissed

const DURATION    := 4.0
const C_GOLD      := Color(0.78, 0.66, 0.29)
const C_BG        := Color(0.039, 0.031, 0.020, 0.97)
const C_BORDER    := Color(0.70, 0.55, 0.24, 0.35)
const C_TXT       := Color(0.83, 0.79, 0.69)
const C_DIM       := Color(0.50, 0.47, 0.38, 0.7)

var _timer:    float = 0.0
var _running:  bool  = false
var _bar:      ColorRect = null


func show_unlock(data: Dictionary) -> void:
	_build(data)
	modulate.a = 0.0
	visible    = true
	_running   = false
	_timer     = 0.0
	var tween  := create_tween()
	tween.tween_property(self, "modulate:a", 1.0, 0.35)
	tween.tween_callback(func() -> void: _running = true)


func _process(delta: float) -> void:
	if not _running:
		return
	_timer += delta
	if _bar != null:
		_bar.size.x = _bar.get_parent().size.x * clampf(_timer / DURATION, 0.0, 1.0)
	if _timer >= DURATION:
		_dismiss()


func _dismiss() -> void:
	_running = false
	var tween := create_tween()
	tween.tween_property(self, "modulate:a", 0.0, 0.25)
	tween.tween_callback(func() -> void:
		visible = false
		dismissed.emit()
	)


func _build(data: Dictionary) -> void:
	for ch in get_children():
		ch.queue_free()
	_bar = null

	var backdrop := ColorRect.new()
	backdrop.color = Color(0, 0, 0, 0.45)
	backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	backdrop.gui_input.connect(func(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
			_dismiss()
	)
	add_child(backdrop)

	var card := Panel.new()
	card.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	card.offset_left   = -240
	card.offset_right  = 240
	card.offset_top    = -110
	card.offset_bottom = 110
	var st := StyleBoxFlat.new()
	st.bg_color     = C_BG
	st.border_color = C_BORDER
	st.set_border_width_all(1)
	card.add_theme_stylebox_override("panel", st)
	add_child(card)

	# Top gold rule
	var top_rule := ColorRect.new()
	top_rule.color = C_GOLD
	top_rule.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	top_rule.custom_minimum_size.y = 2
	top_rule.size.y = 2
	card.add_child(top_rule)

	var vbox := VBoxContainer.new()
	vbox.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	vbox.offset_left   = 32
	vbox.offset_right  = -32
	vbox.offset_top    = 28
	vbox.offset_bottom = -28
	vbox.add_theme_constant_override("separation", 8)
	card.add_child(vbox)

	# "✦ UNLOCKED ✦"
	var tag := Label.new()
	tag.text = "✦  UNLOCKED  ✦"
	tag.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		tag.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	tag.add_theme_font_size_override("font_size", 12)
	tag.add_theme_color_override("font_color", Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.7))
	vbox.add_child(tag)

	# Category (MUSIC TRACK, CG IMAGE, etc.)
	var cat_lbl := Label.new()
	cat_lbl.text = (data.get("type", "") as String).to_upper()
	cat_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		cat_lbl.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	cat_lbl.add_theme_font_size_override("font_size", 12)
	cat_lbl.add_theme_color_override("font_color", C_DIM)
	vbox.add_child(cat_lbl)

	# Title
	var title_lbl := Label.new()
	title_lbl.text = data.get("title", "")
	title_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	if ResourceLoader.exists(SkinDB.F_IMFELL_I):
		title_lbl.add_theme_font_override("font", load(SkinDB.F_IMFELL_I) as Font)
	title_lbl.add_theme_font_size_override("font_size", 26)
	title_lbl.add_theme_color_override("font_color", C_GOLD)
	vbox.add_child(title_lbl)

	# Description
	var desc: String = data.get("desc", "")
	if desc != "":
		var desc_lbl := Label.new()
		desc_lbl.text = desc
		desc_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		desc_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		if ResourceLoader.exists(SkinDB.F_IMFELL_R):
			desc_lbl.add_theme_font_override("font", load(SkinDB.F_IMFELL_R) as Font)
		desc_lbl.add_theme_font_size_override("font_size", 13)
		desc_lbl.add_theme_color_override("font_color", C_TXT)
		vbox.add_child(desc_lbl)

	# Progress bar track
	var bar_track := ColorRect.new()
	bar_track.color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.12)
	bar_track.custom_minimum_size.y = 3
	bar_track.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	bar_track.offset_top    = -3
	bar_track.offset_bottom = 0
	card.add_child(bar_track)

	_bar = ColorRect.new()
	_bar.color    = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.6)
	_bar.size     = Vector2(0, 3)
	_bar.position = Vector2(0, 0)
	bar_track.add_child(_bar)
