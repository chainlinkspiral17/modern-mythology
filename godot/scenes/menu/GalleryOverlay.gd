extends Control
## Gallery overlay — shows all CG images found in scene data plus any
## ASCII substrate gallery items listed in
## res://resources/substrates/gallery/_index.json.
## Locked tiles for unseen, full-screen viewer on click.

signal closed

const C_GOLD   := Color(0.78, 0.66, 0.29)
const C_BG     := Color(0.024, 0.020, 0.014, 0.97)
const C_BORDER := Color(0.70, 0.55, 0.24, 0.35)
const C_TXT    := Color(0.83, 0.79, 0.69)
const C_DIM    := Color(0.30, 0.28, 0.24, 0.6)
const THUMB_W  := 180
const THUMB_H  := 120

const SUBSTRATE_INDEX := "res://resources/substrates/gallery/_index.json"
const SUBSTRATE_RASTER_SCRIPT := preload("res://scenes/game/AsciiSubstrateRaster.gd")
const COMPOSITION_SCRIPT := preload("res://scenes/game/AsciiComposition.gd")
const DEBUG_OVERLAY_SCRIPT := preload("res://scenes/menu/SubstrateDebugOverlay.gd")
const CARD_INTERACTIVE_SCRIPT := preload("res://scenes/menu/CardInteractiveLayer.gd")

# Mirrors MainMenu.VOLUME_META — used to label per-volume gallery sections.
const VOLUME_TITLES: Dictionary = {
	1:  "Modern Mythology",
	2:  "Small Wood Volumes",
	3:  "The Earthman Chronicles",
	4:  "#/Sharp",
	5:  "Major Arcana",
	6:  "Planned Community",
	7:  "Land of Milk & Honey",
	8:  "SCUMM",
	9:  "Por Puesto",
	10: "ROFLcopter",
}


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
	var subs     := _load_substrate_index()
	var count_lbl := Label.new()
	count_lbl.text = "%d / %d   +%d ascii" % [seen_cgs.size(), all_cgs.size(), subs.size()]
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

	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_child(scroll)

	var content := VBoxContainer.new()
	content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	content.add_theme_constant_override("separation", 14)
	scroll.add_child(content)

	# Substrate (ASCII) section, grouped per-volume.
	# Items without a `volume` (e.g. Player Surfaces) go into a leading
	# "Always Available" bucket. Items with a volume show as a section per
	# volume, headed with the volume title from VOLUME_TITLES.
	if not subs.is_empty():
		content.add_child(_section_label("ASCII SUBSTRATES"))
		var groups: Dictionary = {}  # key: int volume or -1 for "no volume"
		var order: Array = []        # preserve discovery order for unkeyed
		for item_v in subs:
			if typeof(item_v) != TYPE_DICTIONARY:
				continue
			var it: Dictionary = item_v
			var vol: int = int(it.get("volume", -1))
			if not groups.has(vol):
				groups[vol] = []
				order.append(vol)
			(groups[vol] as Array).append(it)

		var ordered_vols: Array = []
		if order.has(-1):
			ordered_vols.append(-1)
		var numbered: Array = []
		for v in order:
			if v != -1:
				numbered.append(v)
		numbered.sort()
		ordered_vols.append_array(numbered)

		for vol_v in ordered_vols:
			var vol: int = int(vol_v)
			var header: String = ""
			if vol == -1:
				header = "ALWAYS AVAILABLE"
			else:
				var title: String = str(VOLUME_TITLES.get(vol, ""))
				header = "VOLUME %d" % vol if title == "" else "VOLUME %d  —  %s" % [vol, title.to_upper()]
			content.add_child(_volume_label(header))
			var flow := FlowContainer.new()
			flow.alignment = FlowContainer.ALIGNMENT_BEGIN
			flow.add_theme_constant_override("h_separation", 10)
			flow.add_theme_constant_override("v_separation", 10)
			flow.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			content.add_child(flow)
			for it_v in groups[vol]:
				flow.add_child(_make_substrate_tile(it_v as Dictionary))

	# CG section
	content.add_child(_section_label("CG IMAGES"))
	if all_cgs.is_empty():
		var empty_lbl := Label.new()
		empty_lbl.text = "No CG images found in scene data."
		_apply_font(empty_lbl, SkinDB.F_IMFELL_R, 14, C_DIM)
		empty_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		content.add_child(empty_lbl)
	else:
		var flow := FlowContainer.new()
		flow.alignment = FlowContainer.ALIGNMENT_BEGIN
		flow.add_theme_constant_override("h_separation", 10)
		flow.add_theme_constant_override("v_separation", 10)
		flow.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		content.add_child(flow)

		for cg_src: String in all_cgs:
			var is_seen: bool = SaveSystem.is_cg_seen(cg_src)
			var tile := _make_tile(cg_src, is_seen)
			flow.add_child(tile)


func _section_label(text: String) -> Label:
	var lbl := Label.new()
	lbl.text = text
	_apply_font(lbl, SkinDB.F_CINZEL, 11, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.85))
	return lbl


func _volume_label(text: String) -> Label:
	# Subordinate label under the ASCII SUBSTRATES section — dimmer + smaller.
	var lbl := Label.new()
	lbl.text = text
	_apply_font(lbl, SkinDB.F_CINZEL, 10, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.55))
	return lbl


func _load_substrate_index() -> Array:
	if not FileAccess.file_exists(SUBSTRATE_INDEX):
		return []
	var f := FileAccess.open(SUBSTRATE_INDEX, FileAccess.READ)
	if f == null:
		return []
	var data: Variant = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY:
		return []
	var dd: Dictionary = data
	if not dd.has("items"):
		return []
	var items_v: Variant = dd["items"]
	if typeof(items_v) != TYPE_ARRAY:
		return []
	return items_v as Array


func _make_substrate_tile(item: Dictionary) -> Control:
	var always_unlocked: bool = bool(item.get("always_unlocked", false))
	var is_seen: bool = always_unlocked or SaveSystem.is_cg_seen("substrate:" + str(item.get("id", "")))

	var tile := Button.new()
	tile.custom_minimum_size = Vector2(THUMB_W, THUMB_H)
	tile.clip_contents = true

	var tile_style := StyleBoxFlat.new()
	tile_style.bg_color     = C_DIM if not is_seen else Color(0.04, 0.05, 0.08, 0.9)
	tile_style.border_color = C_BORDER
	tile_style.set_border_width_all(1)
	tile.add_theme_stylebox_override("normal",  tile_style)
	var hover_style: StyleBoxFlat = tile_style.duplicate() as StyleBoxFlat
	hover_style.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.7)
	tile.add_theme_stylebox_override("hover",   hover_style)
	tile.add_theme_stylebox_override("focus",   hover_style)
	tile.add_theme_stylebox_override("pressed", hover_style)

	if is_seen:
		var v := VBoxContainer.new()
		v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		v.offset_left = 10
		v.offset_right = -10
		v.offset_top = 14
		v.offset_bottom = -10
		v.add_theme_constant_override("separation", 6)
		v.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tile.add_child(v)

		var kind := Label.new()
		kind.text = "// ASCII"
		_apply_font(kind, SkinDB.F_CINZEL, 9, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.55))
		v.add_child(kind)

		var title := Label.new()
		title.text = str(item.get("title", item.get("id", "?")))
		_apply_font(title, SkinDB.F_CINZEL, 14, C_TXT)
		title.autowrap_mode = TextServer.AUTOWRAP_WORD
		v.add_child(title)

		var set_lbl := Label.new()
		set_lbl.text = str(item.get("set", ""))
		_apply_font(set_lbl, SkinDB.F_IMFELL_R, 10, Color(C_TXT.r, C_TXT.g, C_TXT.b, 0.55))
		v.add_child(set_lbl)

		var path: String = str(item.get("path", ""))
		var title_str: String = str(item.get("title", item.get("id", "")))
		var item_kind: String = str(item.get("type", "substrate"))
		tile.pressed.connect(func() -> void: _view_substrate_fullscreen(path, title_str, item_kind))
	else:
		var lock_lbl := Label.new()
		lock_lbl.text = "🔒"
		lock_lbl.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		lock_lbl.add_theme_font_size_override("font_size", 24)
		lock_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		lock_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tile.add_child(lock_lbl)
		tile.disabled = true

	return tile


func _view_substrate_fullscreen(short_path: String, title: String, kind: String = "substrate") -> void:
	var viewer := ColorRect.new()
	viewer.color = Color(0, 0, 0, 0.96)
	viewer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	viewer.z_index = 10
	viewer.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(viewer)

	var sub := Control.new()
	if kind == "composition":
		sub.set_script(COMPOSITION_SCRIPT)
	else:
		sub.set_script(SUBSTRATE_RASTER_SCRIPT)
	sub.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	sub.mouse_filter = Control.MOUSE_FILTER_IGNORE
	viewer.add_child(sub)
	if kind == "composition":
		sub.call_deferred("load_composition", short_path)
	else:
		sub.call_deferred("load_substrate", short_path)

	# Debug overlay — composition-only. Hidden by default; toggled via DEBUG btn.
	var debug_overlay: Control = null
	if kind == "composition":
		debug_overlay = Control.new()
		debug_overlay.set_script(DEBUG_OVERLAY_SCRIPT)
		debug_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		debug_overlay.visible = false
		debug_overlay.z_index = 20
		viewer.add_child(debug_overlay)

		var debug_btn := Button.new()
		debug_btn.text = "DEBUG"
		debug_btn.custom_minimum_size = Vector2(80, 28)
		debug_btn.set_anchors_preset(Control.PRESET_TOP_LEFT)
		debug_btn.offset_left = 16
		debug_btn.offset_top  = 16
		debug_btn.offset_right = 96
		debug_btn.offset_bottom = 44
		debug_btn.z_index = 21
		debug_btn.pressed.connect(func() -> void:
			if not debug_overlay.visible:
				debug_overlay.call("bind", sub)
				debug_overlay.visible = true
			else:
				debug_overlay.visible = false)
		viewer.add_child(debug_btn)

	# Interactive layer — adds clickable hotspots + cipher reveals +
	# per-card synth note trigger if a puzzle_hooks entry exists for
	# this asset id. Sits above the composition, below the close hint.
	# Resolves both arcana ids and portrait ids via the layer's bind().
	var card_interactive := Control.new()
	card_interactive.set_script(CARD_INTERACTIVE_SCRIPT)
	card_interactive.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	card_interactive.z_index = 15
	card_interactive.mouse_filter = Control.MOUSE_FILTER_PASS
	viewer.add_child(card_interactive)
	# Defer bind so _ready has fired and audio is initialized
	card_interactive.call_deferred("bind", short_path)

	var close_lbl := Label.new()
	close_lbl.text = "CLICK TO CLOSE — %s" % title
	close_lbl.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	close_lbl.offset_right  = -16
	close_lbl.offset_bottom = -16
	close_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	close_lbl.vertical_alignment   = VERTICAL_ALIGNMENT_BOTTOM
	_apply_font(close_lbl, SkinDB.F_CINZEL, 9, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.5))
	close_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	viewer.add_child(close_lbl)

	viewer.gui_input.connect(func(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
			viewer.queue_free()
	)


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
