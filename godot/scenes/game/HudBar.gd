extends Control
## Top HUD bar — volume title, skill dots, menu button.

signal menu_pressed

const SKILL_NAMES := ["empathy", "logic", "composure", "rhetoric", "signal"]
const VOL_TITLES: Dictionary = {
	1: "Modern Mythology",
	2: "Small Wood Volumes",
	3: "The Earthman Chronicles",
	4: "#/Sharp",
	5: "Major Arcana",
	6: "Planned Community",
	7: "Land of Milk & Honey",
}

var _dot_rects: Dictionary = {}


func setup(skin: Dictionary, vol: int, skills: Dictionary, _unused: Variant = null) -> void:
	for ch in get_children():
		ch.queue_free()
	_dot_rects = {}
	_build(skin, vol, skills)


func update_skills(skills: Dictionary) -> void:
	for sk in SKILL_NAMES:
		if not _dot_rects.has(sk):
			continue
		var dots: Array = _dot_rects[sk]
		var val: int = int(skills.get(sk, 0))
		for d in dots.size():
			(dots[d] as ColorRect).modulate.a = 1.0 if d < val else 0.18


func _build(skin: Dictionary, vol: int, skills: Dictionary) -> void:
	var hud_col:  Color  = skin.get("hud_color",  Color(0.78, 0.66, 0.29, 0.75))
	var hud_bg:   Color  = skin.get("hud_bg",     Color(0.05, 0.04, 0.03, 0.88))
	var hud_bdr:  Color  = skin.get("hud_border", Color(0.70, 0.55, 0.24, 0.35))
	var hud_font: String = skin.get("hud_font",   SkinDB.F_CINZEL)

	var bg := ColorRect.new()
	bg.color = hud_bg
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	var sep := ColorRect.new()
	sep.color = hud_bdr
	sep.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	sep.custom_minimum_size.y = 1
	sep.offset_top = -1
	add_child(sep)

	var row := HBoxContainer.new()
	row.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	row.offset_left  = 12
	row.offset_right = -12
	row.add_theme_constant_override("separation", 8)
	add_child(row)

	var title_lbl := Label.new()
	title_lbl.text               = (VOL_TITLES.get(vol, "") as String).to_upper()
	title_lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	title_lbl.add_theme_font_size_override("font_size", 12)
	title_lbl.add_theme_color_override("font_color", hud_col)
	if ResourceLoader.exists(hud_font):
		title_lbl.add_theme_font_override("font", load(hud_font) as Font)
	row.add_child(title_lbl)

	var sp1 := Control.new()
	sp1.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(sp1)

	var dots_row := HBoxContainer.new()
	dots_row.add_theme_constant_override("separation", 10)
	dots_row.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(dots_row)

	for sk: String in SKILL_NAMES:
		var sk_col := VBoxContainer.new()
		sk_col.add_theme_constant_override("separation", 2)
		dots_row.add_child(sk_col)

		var lbl := Label.new()
		lbl.text = sk.substr(0, 3).to_upper()
		lbl.add_theme_font_size_override("font_size", 12)
		lbl.add_theme_color_override("font_color",
				Color(hud_col.r, hud_col.g, hud_col.b, 0.45))
		lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		sk_col.add_child(lbl)

		var dot_h := HBoxContainer.new()
		dot_h.add_theme_constant_override("separation", 2)
		sk_col.add_child(dot_h)

		var val: int = int(skills.get(sk, 0))
		var this_dots: Array = []
		for d in 5:
			var dot := ColorRect.new()
			dot.custom_minimum_size = Vector2(5, 5)
			dot.color      = hud_col
			dot.modulate.a = 1.0 if d < val else 0.18
			dot_h.add_child(dot)
			this_dots.append(dot)
		_dot_rects[sk] = this_dots

	var sp2 := Control.new()
	sp2.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(sp2)

	# Styled to match the literary chrome — the default gray Godot
	# button was the one stock control left on the reading screen.
	var menu_btn := Button.new()
	menu_btn.text = "MENU"
	menu_btn.custom_minimum_size = Vector2(74, 30)
	menu_btn.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	var mst := StyleBoxFlat.new()
	mst.bg_color = Color(0, 0, 0, 0)
	mst.border_color = hud_bdr
	mst.set_border_width_all(1)
	mst.set_corner_radius_all(2)
	menu_btn.add_theme_stylebox_override("normal", mst)
	var mst_h: StyleBoxFlat = mst.duplicate() as StyleBoxFlat
	mst_h.bg_color = Color(hud_col.r, hud_col.g, hud_col.b, 0.08)
	mst_h.border_color = Color(hud_col.r, hud_col.g, hud_col.b, 0.7)
	menu_btn.add_theme_stylebox_override("hover", mst_h)
	menu_btn.add_theme_stylebox_override("focus", mst_h)
	menu_btn.add_theme_stylebox_override("pressed", mst_h)
	if ResourceLoader.exists(hud_font):
		menu_btn.add_theme_font_override("font", load(hud_font) as Font)
	menu_btn.add_theme_font_size_override("font_size", 12)
	menu_btn.add_theme_color_override("font_color", hud_col)
	menu_btn.add_theme_color_override("font_hover_color",
			Color(minf(hud_col.r + 0.1, 1.0), minf(hud_col.g + 0.1, 1.0), hud_col.b, 1.0))
	menu_btn.pressed.connect(func() -> void: menu_pressed.emit())
	row.add_child(menu_btn)
