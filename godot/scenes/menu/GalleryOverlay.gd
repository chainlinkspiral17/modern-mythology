extends Control
## Gallery overlay — shows all CG images found in scene data.
## Locked tiles for unseen, full-screen viewer on click.

signal closed

const C_GOLD   := Color(0.78, 0.66, 0.29)
const C_BG     := Color(0.024, 0.020, 0.014, 0.97)
const C_BORDER := Color(0.70, 0.55, 0.24, 0.35)
const C_TXT    := Color(0.83, 0.79, 0.69)
const C_DIM    := Color(0.30, 0.28, 0.24, 0.6)
const THUMB_W  := 180
const THUMB_H  := 120


func open() -> void:
	_rebuild()
	visible = true


func _rebuild() -> void:
	for ch in get_children():
		ch.queue_free()

	var backdrop := ColorRect.new()
	backdrop.color = Color(0, 0, 0, 0.7)
	backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(backdrop)

	var card := Panel.new()
	card.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	card.offset_left   = 60
	card.offset_right  = -60
	card.offset_top    = 40
	card.offset_bottom = -40
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
	vbox.offset_top    = 20
	vbox.offset_bottom = -20
	vbox.add_theme_constant_override("separation", 12)
	card.add_child(vbox)

	var header_row := HBoxContainer.new()
	vbox.add_child(header_row)
	var title_lbl := Label.new()
	title_lbl.text = "GALLERY"
	_apply_font(title_lbl, SkinDB.F_CINZEL, 13, C_GOLD)
	title_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header_row.add_child(title_lbl)
	var seen_cgs := SaveSystem.get_seen_cgs()
	var all_cgs  := SceneDataDB.get_all_cg_ids()
	var count_lbl := Label.new()
	count_lbl.text = "%d / %d" % [seen_cgs.size(), all_cgs.size()]
	_apply_font(count_lbl, SkinDB.F_CINZEL, 10, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.6))
	count_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	count_lbl.horizontal_alignment  = HORIZONTAL_ALIGNMENT_RIGHT
	header_row.add_child(count_lbl)
	var close_btn := Button.new()
	close_btn.text = "✕"
	close_btn.custom_minimum_size = Vector2(32, 32)
	close_btn.pressed.connect(func() -> void: visible = false; closed.emit())
	header_row.add_child(close_btn)

	vbox.add_child(_rule())

	if all_cgs.is_empty():
		var empty_lbl := Label.new()
		empty_lbl.text = "No CG images found in scene data."
		_apply_font(empty_lbl, SkinDB.F_IMFELL_R, 14, C_DIM)
		empty_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		vbox.add_child(empty_lbl)
	else:
		var scroll := ScrollContainer.new()
		scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
		vbox.add_child(scroll)

		var flow := FlowContainer.new()
		flow.alignment = FlowContainer.ALIGNMENT_BEGIN
		flow.add_theme_constant_override("h_separation", 10)
		flow.add_theme_constant_override("v_separation", 10)
		flow.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		scroll.add_child(flow)

		for cg_src: String in all_cgs:
			var is_seen: bool = SaveSystem.is_cg_seen(cg_src)
			var tile := _make_tile(cg_src, is_seen)
			flow.add_child(tile)


func _make_tile(src: String, is_seen: bool) -> Control:
	var tile := Button.new()
	tile.custom_minimum_size = Vector2(THUMB_W, THUMB_H)
	tile.clip_contents = true

	var tile_style := StyleBoxFlat.new()
	tile_style.bg_color     = C_DIM if not is_seen else Color(0, 0, 0, 0.2)
	tile_style.border_color = C_BORDER
	tile_style.set_border_width_all(1)
	tile.add_theme_stylebox_override("normal",  tile_style)
	var hover_style: StyleBoxFlat = tile_style.duplicate() as StyleBoxFlat
	hover_style.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.7)
	tile.add_theme_stylebox_override("hover",   hover_style)
	tile.add_theme_stylebox_override("focus",   hover_style)
	tile.add_theme_stylebox_override("pressed", hover_style)

	if is_seen:
		var img_path := "res://" + src
		if ResourceLoader.exists(img_path):
			var tex := ResourceLoader.load(img_path) as Texture2D
			if tex:
				var img_rect := TextureRect.new()
				img_rect.texture      = tex
				img_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
				img_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
				img_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
				tile.add_child(img_rect)
	else:
		var lock_lbl := Label.new()
		lock_lbl.text = "🔒"
		lock_lbl.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		lock_lbl.add_theme_font_size_override("font_size", 24)
		lock_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		lock_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tile.add_child(lock_lbl)

	if is_seen:
		var s: String = src
		tile.pressed.connect(func() -> void: _view_fullscreen(s))
	else:
		tile.disabled = true

	return tile


func _view_fullscreen(src: String) -> void:
	var viewer := ColorRect.new()
	viewer.color = Color(0, 0, 0, 0.92)
	viewer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	viewer.z_index = 10
	add_child(viewer)

	var path := "res://" + src
	if ResourceLoader.exists(path):
		var tex := ResourceLoader.load(path) as Texture2D
		if tex:
			var img := TextureRect.new()
			img.texture      = tex
			img.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
			img.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			img.mouse_filter = Control.MOUSE_FILTER_IGNORE
			viewer.add_child(img)

	var close_lbl := Label.new()
	close_lbl.text = "CLICK TO CLOSE"
	close_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	close_lbl.vertical_alignment   = VERTICAL_ALIGNMENT_BOTTOM
	close_lbl.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	close_lbl.offset_right  = -16
	close_lbl.offset_bottom = -16
	_apply_font(close_lbl, SkinDB.F_CINZEL, 9, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.5))
	close_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	viewer.add_child(close_lbl)

	viewer.gui_input.connect(func(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
			viewer.queue_free()
	)


func _rule() -> ColorRect:
	var r := ColorRect.new()
	r.color = C_BORDER
	r.custom_minimum_size.y = 1
	return r


func _apply_font(node: Label, path: String, size: int, col: Color) -> void:
	if ResourceLoader.exists(path):
		node.add_theme_font_override("font", load(path) as Font)
	node.add_theme_font_size_override("font_size", size)
	node.add_theme_color_override("font_color", col)
