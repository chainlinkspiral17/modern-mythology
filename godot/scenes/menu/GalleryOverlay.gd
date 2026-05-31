extends Control
## Gallery overlay — tabbed archive of unlockable content.
##   STILLS      CG images recorded as seen in scene data.
##   SUBSTRATES  ASCII/composition art from substrates/gallery/_index.json.
##   VIDEO       Cinematics under assets/video/.
## Each tab has a contextual filter row, a tiled grid with locked/seen states,
## and a fullscreen lightbox with ← / → / ESC navigation.

signal closed

const C_GOLD   := Color(0.78, 0.66, 0.29)
const C_BG     := Color(0.024, 0.020, 0.014, 0.97)
const C_BORDER := Color(0.70, 0.55, 0.24, 0.35)
const C_TXT    := Color(0.83, 0.79, 0.69)
const C_DIM    := Color(0.30, 0.28, 0.24, 0.6)
const THUMB_W  := 200
const THUMB_H  := 132

# Per-volume accent colors. Volumes not listed fall back to gold.
const VOL_COLORS := {
	3: Color(0.0, 0.78, 1.0),
	4: Color(1.0, 0.18, 0.0),
}

const SUBSTRATE_INDEX := "res://resources/substrates/gallery/_index.json"
const VIDEO_DIR := "res://assets/video/"
const SUBSTRATE_RASTER_SCRIPT := preload("res://scenes/game/AsciiSubstrateRaster.gd")
const COMPOSITION_SCRIPT := preload("res://scenes/game/AsciiComposition.gd")
const DEBUG_OVERLAY_SCRIPT := preload("res://scenes/menu/SubstrateDebugOverlay.gd")

var _active_tab: String = "substrates"
var _filters: Dictionary = {"stills": 0, "substrates": "", "video": 0}

var _count_lbl:    Label = null
var _tab_row:      HBoxContainer = null
var _filter_row:   HBoxContainer = null
var _content_host: Control = null
var _built: bool = false
# Cached per-open snapshot of all tab items (scanning 298 scenes is expensive).
var _data_cache: Dictionary = {}

# Lightbox state.
var _viewer:        Control = null
var _viewer_body:   Control = null
var _viewer_items:  Array = []
var _viewer_index:  int = 0


func open() -> void:
	if not _built:
		_build_chrome()
		_built = true
	_data_cache = {}  # refresh seen-state snapshot each time the gallery opens
	_select_tab(_active_tab)
	visible = true


func _close() -> void:
	if _viewer != null:
		_close_viewer()
		return
	visible = false
	closed.emit()


func _input(event: InputEvent) -> void:
	if not visible:
		return
	if event.is_action_pressed("menu_back"):
		_close()
		get_viewport().set_input_as_handled()
		return
	if _viewer != null and event is InputEventKey and (event as InputEventKey).pressed:
		var kc := (event as InputEventKey).keycode
		if kc == KEY_LEFT:
			_viewer_step(-1)
			get_viewport().set_input_as_handled()
		elif kc == KEY_RIGHT:
			_viewer_step(1)
			get_viewport().set_input_as_handled()


# ── Persistent chrome ──────────────────────────────────────────────────────────

func _build_chrome() -> void:
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

	# Header
	var header_row := HBoxContainer.new()
	vbox.add_child(header_row)
	var title_lbl := Label.new()
	title_lbl.text = "GALLERY"
	_apply_font(title_lbl, SkinDB.F_CINZEL, 13, C_GOLD)
	title_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header_row.add_child(title_lbl)
	_count_lbl = Label.new()
	_apply_font(_count_lbl, SkinDB.F_CINZEL, 10, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.6))
	_count_lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	header_row.add_child(_count_lbl)
	var close_btn := Button.new()
	close_btn.text = "✕"
	close_btn.custom_minimum_size = Vector2(32, 32)
	close_btn.pressed.connect(_close)
	header_row.add_child(close_btn)

	# Tab bar
	_tab_row = HBoxContainer.new()
	_tab_row.add_theme_constant_override("separation", 2)
	vbox.add_child(_tab_row)

	vbox.add_child(_rule())

	# Filter row
	_filter_row = HBoxContainer.new()
	_filter_row.add_theme_constant_override("separation", 4)
	vbox.add_child(_filter_row)

	# Content host fills remaining space.
	_content_host = Control.new()
	_content_host.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_content_host.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vbox.add_child(_content_host)


func _build_tab_bar() -> void:
	for ch in _tab_row.get_children():
		ch.queue_free()
	var data := _gather_all()
	var tabs := [
		{"id": "stills",     "label": "STILLS",     "items": data["stills"]},
		{"id": "substrates", "label": "SUBSTRATES", "items": data["substrates"]},
		{"id": "video",      "label": "VIDEO",      "items": data["video"]},
	]
	for t: Dictionary in tabs:
		var items: Array = t["items"]
		var seen := 0
		for it: Dictionary in items:
			if it.get("seen", false):
				seen += 1
		var btn := Button.new()
		btn.text = "%s (%d/%d)" % [t["label"], seen, items.size()]
		btn.toggle_mode = true
		btn.button_pressed = (t["id"] == _active_tab)
		btn.focus_mode = Control.FOCUS_NONE
		_style_tab_btn(btn, t["id"] == _active_tab)
		var tid: String = t["id"]
		btn.pressed.connect(func() -> void: _select_tab(tid))
		_tab_row.add_child(btn)


# ── Tab / filter selection ─────────────────────────────────────────────────────

func _select_tab(tab: String) -> void:
	_active_tab = tab
	_build_tab_bar()
	_rebuild_filter()
	_rebuild_content()
	_update_header_count()


func _rebuild_filter() -> void:
	for ch in _filter_row.get_children():
		ch.queue_free()
	var chips: Array = [] # each: {key, label, accent}
	var data := _gather_all()
	if _active_tab == "substrates":
		var sets: Array = []
		for it: Dictionary in data["substrates"]:
			var s: String = str(it.get("set", ""))
			if s != "" and s not in sets:
				sets.append(s)
		chips.append({"key": "", "label": "ALL", "accent": C_GOLD})
		for s: String in sets:
			chips.append({"key": s, "label": s.to_upper(), "accent": C_GOLD})
	else:
		var vols: Array = []
		for it: Dictionary in data[_active_tab]:
			var v: int = int(it.get("vol", 0))
			if v not in vols:
				vols.append(v)
		vols.sort()
		chips.append({"key": 0, "label": "ALL", "accent": C_GOLD})
		for v: int in vols:
			var lbl := "MENU" if v == 0 else "%02d" % v
			chips.append({"key": v, "label": lbl, "accent": _vol_color(v)})

	# Hide the filter row entirely when there's nothing to filter by.
	_filter_row.visible = chips.size() > 1
	var cur = _filters[_active_tab]
	for c: Dictionary in chips:
		var key = c["key"]
		var btn := Button.new()
		btn.text = str(c["label"])
		btn.toggle_mode = true
		btn.focus_mode = Control.FOCUS_NONE
		btn.button_pressed = (key == cur)
		btn.custom_minimum_size = Vector2(0, 24)
		_style_filter_btn(btn, key == cur, c["accent"])
		btn.pressed.connect(func() -> void:
			_filters[_active_tab] = key
			_rebuild_filter()
			_rebuild_content())
		_filter_row.add_child(btn)


func _rebuild_content() -> void:
	for ch in _content_host.get_children():
		ch.queue_free()

	var scroll := ScrollContainer.new()
	scroll.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	_content_host.add_child(scroll)

	var flow := FlowContainer.new()
	flow.alignment = FlowContainer.ALIGNMENT_BEGIN
	flow.add_theme_constant_override("h_separation", 12)
	flow.add_theme_constant_override("v_separation", 12)
	flow.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(flow)

	var items := _visible_items()
	# Lightbox navigation cycles through the seen items of the active tab.
	_viewer_items = items.filter(func(it: Dictionary) -> bool: return it.get("seen", false))

	if items.is_empty():
		var empty_lbl := Label.new()
		empty_lbl.text = _empty_text()
		_apply_font(empty_lbl, SkinDB.F_IMFELL_I if ResourceLoader.exists(SkinDB.F_IMFELL_I) else SkinDB.F_IMFELL_R, 15, C_DIM)
		empty_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		empty_lbl.custom_minimum_size = Vector2(THUMB_W * 3, THUMB_H)
		flow.add_child(empty_lbl)
		return

	for it: Dictionary in items:
		flow.add_child(_make_tile(it))


func _empty_text() -> String:
	match _active_tab:
		"stills":     return "No stills recorded yet. Images you see in play collect here."
		"video":      return "No cinematics found."
		_:            return "Nothing here yet."


# ── Item gathering ─────────────────────────────────────────────────────────────

func _gather_all() -> Dictionary:
	if _data_cache.is_empty():
		_data_cache = {
			"stills":     _gather_stills(),
			"substrates": _gather_substrates(),
			"video":      _gather_video(),
		}
	return _data_cache


func _gather_stills() -> Array:
	var out: Array = []
	for src: String in SceneDataDB.get_all_cg_ids():
		out.append({
			"kind":  "image",
			"path":  src,
			"title": _titleize(src.get_file().get_basename()),
			"vol":   _vol_from_path(src),
			"seen":  SaveSystem.is_cg_seen(src),
		})
	return out


func _gather_substrates() -> Array:
	var out: Array = []
	for item_v in _load_substrate_index():
		if typeof(item_v) != TYPE_DICTIONARY:
			continue
		var item: Dictionary = item_v
		var always: bool = bool(item.get("always_unlocked", false))
		var seen: bool = always or SaveSystem.is_cg_seen("substrate:" + str(item.get("id", "")))
		out.append({
			"kind":  str(item.get("type", "substrate")),  # "composition" or "substrate"
			"path":  str(item.get("path", "")),
			"title": str(item.get("title", item.get("id", "?"))),
			"set":   str(item.get("set", "")),
			"seen":  seen,
		})
	return out


func _gather_video() -> Array:
	var out: Array = []
	var dir := DirAccess.open(VIDEO_DIR)
	if dir == null:
		return out
	dir.list_dir_begin()
	var fname := dir.get_next()
	var names: Array = []
	while fname != "":
		if not dir.current_is_dir() and fname.get_extension().to_lower() == "ogv":
			names.append(fname)
		fname = dir.get_next()
	dir.list_dir_end()
	names.sort()
	for n: String in names:
		var base := n.get_basename()
		out.append({
			"kind":  "video",
			"path":  VIDEO_DIR + n,
			"title": _titleize(base),
			"vol":   _vol_from_path(n),
			"seen":  true,  # cinematics are always viewable
		})
	return out


func _visible_items() -> Array:
	var data := _gather_all()
	var items: Array = data[_active_tab]
	var cur = _filters[_active_tab]
	if _active_tab == "substrates":
		if str(cur) == "":
			return items
		return items.filter(func(it: Dictionary) -> bool: return str(it.get("set", "")) == str(cur))
	else:
		if int(cur) == 0:
			return items
		return items.filter(func(it: Dictionary) -> bool: return int(it.get("vol", 0)) == int(cur))


# ── Tiles ──────────────────────────────────────────────────────────────────────

func _make_tile(item: Dictionary) -> Control:
	var seen: bool = item.get("seen", false)
	var accent: Color = _vol_color(int(item.get("vol", 0)))
	var tile := Button.new()
	tile.custom_minimum_size = Vector2(THUMB_W, THUMB_H)
	tile.clip_contents = true
	tile.focus_mode = Control.FOCUS_NONE

	var tile_style := StyleBoxFlat.new()
	tile_style.bg_color     = C_DIM if not seen else Color(0.02, 0.03, 0.05, 0.9)
	tile_style.border_color = C_BORDER
	tile_style.set_border_width_all(1)
	tile.add_theme_stylebox_override("normal",  tile_style)
	var hover_style: StyleBoxFlat = tile_style.duplicate() as StyleBoxFlat
	hover_style.border_color = Color(accent.r, accent.g, accent.b, 0.7)
	tile.add_theme_stylebox_override("hover",   hover_style)
	tile.add_theme_stylebox_override("focus",   hover_style)
	tile.add_theme_stylebox_override("pressed", hover_style)

	if not seen:
		var lock_lbl := Label.new()
		lock_lbl.text = "🔒"
		lock_lbl.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		lock_lbl.add_theme_font_size_override("font_size", 24)
		lock_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		lock_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tile.add_child(lock_lbl)
		tile.disabled = true
		return tile

	var kind: String = str(item.get("kind", "image"))
	if kind == "image" or kind == "video":
		_add_thumb_image(tile, item)
	else:
		_add_thumb_caption(tile, item, accent)

	if kind == "video":
		var play_badge := Label.new()
		play_badge.text = "▶"
		play_badge.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		play_badge.add_theme_font_size_override("font_size", 28)
		play_badge.add_theme_color_override("font_color", Color(accent.r, accent.g, accent.b, 0.85))
		play_badge.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		play_badge.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tile.add_child(play_badge)

	var the_item := item
	tile.pressed.connect(func() -> void: _open_viewer_for(the_item))
	return tile


func _add_thumb_image(tile: Button, item: Dictionary) -> void:
	if str(item.get("kind", "")) == "video":
		# No frame extraction; show a stylized placeholder backdrop instead.
		var bg := ColorRect.new()
		bg.color = Color(0.03, 0.04, 0.06, 1.0)
		bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tile.add_child(bg)
	else:
		var p: String = str(item.get("path", ""))
		var img_path := p if p.begins_with("res://") else "res://" + p
		if ResourceLoader.exists(img_path):
			var tex := ResourceLoader.load(img_path) as Texture2D
			if tex:
				var img_rect := TextureRect.new()
				img_rect.texture      = tex
				img_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
				img_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
				img_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
				tile.add_child(img_rect)
	# Title caption gradient at the bottom.
	var cap := Label.new()
	cap.text = str(item.get("title", ""))
	cap.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	cap.offset_top = -26
	cap.offset_left = 8
	cap.offset_right = -8
	cap.offset_bottom = -6
	cap.clip_text = true
	_apply_font(cap, SkinDB.F_IMFELL_I if ResourceLoader.exists(SkinDB.F_IMFELL_I) else SkinDB.F_IMFELL_R, 12, C_TXT)
	cap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tile.add_child(cap)


func _add_thumb_caption(tile: Button, item: Dictionary, accent: Color) -> void:
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
	_apply_font(kind, SkinDB.F_CINZEL, 9, Color(accent.r, accent.g, accent.b, 0.55))
	v.add_child(kind)

	var title := Label.new()
	title.text = str(item.get("title", "?"))
	_apply_font(title, SkinDB.F_CINZEL, 14, C_TXT)
	title.autowrap_mode = TextServer.AUTOWRAP_WORD
	v.add_child(title)

	var set_lbl := Label.new()
	set_lbl.text = str(item.get("set", ""))
	_apply_font(set_lbl, SkinDB.F_IMFELL_R, 10, Color(C_TXT.r, C_TXT.g, C_TXT.b, 0.55))
	v.add_child(set_lbl)


# ── Lightbox ───────────────────────────────────────────────────────────────────

func _open_viewer_for(item: Dictionary) -> void:
	var idx := 0
	for i in _viewer_items.size():
		if (_viewer_items[i] as Dictionary).get("path", "") == item.get("path", ""):
			idx = i
			break
	_viewer_index = idx
	if _viewer == null:
		_viewer = ColorRect.new()
		(_viewer as ColorRect).color = Color(0, 0, 0, 0.95)
		_viewer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		_viewer.z_index = 10
		_viewer.mouse_filter = Control.MOUSE_FILTER_STOP
		_viewer.gui_input.connect(func(ev: InputEvent) -> void:
			if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
				if (ev as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
					_close_viewer())
		add_child(_viewer)
	_show_viewer_item()


func _close_viewer() -> void:
	if _viewer != null:
		_viewer.queue_free()
		_viewer = null
		_viewer_body = null


func _viewer_step(dir: int) -> void:
	if _viewer == null or _viewer_items.is_empty():
		return
	_viewer_index = (_viewer_index + dir + _viewer_items.size()) % _viewer_items.size()
	_show_viewer_item()


func _show_viewer_item() -> void:
	if _viewer == null or _viewer_items.is_empty():
		return
	for ch in _viewer.get_children():
		ch.queue_free()
	var item: Dictionary = _viewer_items[_viewer_index]
	var kind: String = str(item.get("kind", "image"))

	_viewer_body = Control.new()
	_viewer_body.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_viewer_body.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_viewer.add_child(_viewer_body)

	match kind:
		"image":
			_build_image_view(item)
		"video":
			_build_video_view(item)
		"composition":
			_build_substrate_view(item, true)
		_:
			_build_substrate_view(item, false)

	_build_viewer_overlay(item)


func _build_image_view(item: Dictionary) -> void:
	var p: String = str(item.get("path", ""))
	var path := p if p.begins_with("res://") else "res://" + p
	if ResourceLoader.exists(path):
		var tex := ResourceLoader.load(path) as Texture2D
		if tex:
			var img := TextureRect.new()
			img.texture      = tex
			img.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
			img.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			img.offset_top = 40
			img.offset_bottom = -70
			img.mouse_filter = Control.MOUSE_FILTER_IGNORE
			_viewer_body.add_child(img)


func _build_video_view(item: Dictionary) -> void:
	var path: String = str(item.get("path", ""))
	var stream: VideoStream = null
	if ResourceLoader.exists(path):
		stream = ResourceLoader.load(path) as VideoStream
	if stream != null:
		var vp := VideoStreamPlayer.new()
		vp.stream = stream
		vp.expand = true
		vp.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		vp.offset_top = 40
		vp.offset_bottom = -70
		vp.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_viewer_body.add_child(vp)
		vp.play()
	else:
		var msg := Label.new()
		msg.text = "Cannot play: %s" % path
		msg.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		_apply_font(msg, SkinDB.F_SPACEMONO if ResourceLoader.exists(SkinDB.F_SPACEMONO) else SkinDB.F_IMFELL_R, 11, C_DIM)
		msg.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_viewer_body.add_child(msg)


func _build_substrate_view(item: Dictionary, is_composition: bool) -> void:
	var sub := Control.new()
	if is_composition:
		sub.set_script(COMPOSITION_SCRIPT)
	else:
		sub.set_script(SUBSTRATE_RASTER_SCRIPT)
	sub.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	sub.offset_top = 40
	sub.offset_bottom = -70
	sub.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_viewer_body.add_child(sub)
	var path: String = str(item.get("path", ""))
	if is_composition:
		sub.call_deferred("load_composition", path)
		# Composition-only debug toggle.
		var debug_overlay := Control.new()
		debug_overlay.set_script(DEBUG_OVERLAY_SCRIPT)
		debug_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		debug_overlay.visible = false
		debug_overlay.z_index = 20
		_viewer.add_child(debug_overlay)
		var debug_btn := Button.new()
		debug_btn.text = "DEBUG"
		debug_btn.custom_minimum_size = Vector2(80, 28)
		debug_btn.position = Vector2(16, 46)
		debug_btn.focus_mode = Control.FOCUS_NONE
		debug_btn.z_index = 21
		debug_btn.pressed.connect(func() -> void:
			if not debug_overlay.visible:
				debug_overlay.call("bind", sub)
				debug_overlay.visible = true
			else:
				debug_overlay.visible = false)
		_viewer.add_child(debug_btn)
	else:
		sub.call_deferred("load_substrate", path)


func _build_viewer_overlay(item: Dictionary) -> void:
	# Title + position counter (top center).
	var title_lbl := Label.new()
	title_lbl.text = str(item.get("title", ""))
	title_lbl.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	title_lbl.offset_top = 12
	title_lbl.offset_bottom = 36
	title_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_apply_font(title_lbl, SkinDB.F_IMFELL_I if ResourceLoader.exists(SkinDB.F_IMFELL_I) else SkinDB.F_CINZEL, 15, C_TXT)
	title_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_viewer.add_child(title_lbl)

	var multi := _viewer_items.size() > 1
	if multi:
		var prev_btn := _nav_btn("←")
		prev_btn.set_anchors_and_offsets_preset(Control.PRESET_CENTER_LEFT)
		prev_btn.offset_left = 18
		prev_btn.offset_top = -22
		prev_btn.offset_bottom = 22
		prev_btn.pressed.connect(func() -> void: _viewer_step(-1))
		_viewer.add_child(prev_btn)

		var next_btn := _nav_btn("→")
		next_btn.set_anchors_and_offsets_preset(Control.PRESET_CENTER_RIGHT)
		next_btn.offset_right = -18
		next_btn.offset_left = -62
		next_btn.offset_top = -22
		next_btn.offset_bottom = 22
		next_btn.pressed.connect(func() -> void: _viewer_step(1))
		_viewer.add_child(next_btn)

	var footer := Label.new()
	var pos_txt := "%d / %d" % [_viewer_index + 1, _viewer_items.size()] if multi else ""
	footer.text = "%s        CLICK / ESC TO CLOSE" % pos_txt
	footer.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	footer.offset_top = -40
	footer.offset_bottom = -16
	footer.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_apply_font(footer, SkinDB.F_CINZEL, 9, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.5))
	footer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_viewer.add_child(footer)


func _nav_btn(text: String) -> Button:
	var btn := Button.new()
	btn.text = text
	btn.custom_minimum_size = Vector2(44, 44)
	btn.focus_mode = Control.FOCUS_NONE
	var st := StyleBoxFlat.new()
	st.bg_color = Color(0.1, 0.09, 0.06, 0.6)
	st.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.25)
	st.set_border_width_all(1)
	btn.add_theme_stylebox_override("normal", st)
	var hov := st.duplicate() as StyleBoxFlat
	hov.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.7)
	btn.add_theme_stylebox_override("hover", hov)
	btn.add_theme_stylebox_override("pressed", hov)
	btn.add_theme_color_override("font_color", C_GOLD)
	return btn


# ── Header / misc ──────────────────────────────────────────────────────────────

func _update_header_count() -> void:
	var data := _gather_all()
	var seen := 0
	var total := 0
	for key in ["stills", "substrates", "video"]:
		for it: Dictionary in data[key]:
			total += 1
			if it.get("seen", false):
				seen += 1
	_count_lbl.text = "%d / %d UNLOCKED" % [seen, total]


func _vol_color(vol: int) -> Color:
	return VOL_COLORS.get(vol, C_GOLD)


func _vol_from_path(path: String) -> int:
	var f := path.get_file()
	var re := RegEx.new()
	re.compile("vol(\\d+)")
	var m := re.search(f)
	if m != null:
		return int(m.get_string(1))
	return 0


func _titleize(raw: String) -> String:
	var s := raw.replace("_", " ").strip_edges()
	var words := s.split(" ", false)
	var out: Array = []
	for w: String in words:
		if w.length() == 0:
			continue
		out.append(w.substr(0, 1).to_upper() + w.substr(1))
	return " ".join(PackedStringArray(out))


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


# ── Style helpers ──────────────────────────────────────────────────────────────

func _style_tab_btn(btn: Button, active: bool) -> void:
	var st := StyleBoxFlat.new()
	st.bg_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.06) if active else Color(0, 0, 0, 0)
	st.border_color = C_GOLD if active else Color(0, 0, 0, 0)
	st.border_width_bottom = 2 if active else 0
	st.content_margin_left = 18.0
	st.content_margin_right = 18.0
	st.content_margin_top = 8.0
	st.content_margin_bottom = 8.0
	btn.add_theme_stylebox_override("normal", st)
	btn.add_theme_stylebox_override("hover", st)
	btn.add_theme_stylebox_override("pressed", st)
	btn.add_theme_stylebox_override("focus", st)
	var col := C_GOLD if active else Color(C_TXT.r, C_TXT.g, C_TXT.b, 0.45)
	_apply_button_font(btn, SkinDB.F_CINZEL, 10, col)


func _style_filter_btn(btn: Button, active: bool, accent: Color) -> void:
	var st := StyleBoxFlat.new()
	st.bg_color     = Color(accent.r, accent.g, accent.b, 0.10) if active else Color(0, 0, 0, 0)
	st.border_color = Color(accent.r, accent.g, accent.b, 0.55) if active else Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.12)
	st.set_border_width_all(1)
	st.content_margin_left   = 10.0
	st.content_margin_right  = 10.0
	st.content_margin_top    = 3.0
	st.content_margin_bottom = 3.0
	btn.add_theme_stylebox_override("normal", st)
	btn.add_theme_stylebox_override("hover", st)
	btn.add_theme_stylebox_override("pressed", st)
	btn.add_theme_stylebox_override("focus", st)
	var col := accent if active else Color(C_TXT.r, C_TXT.g, C_TXT.b, 0.45)
	_apply_button_font(btn, SkinDB.F_SPACEMONO if ResourceLoader.exists(SkinDB.F_SPACEMONO) else SkinDB.F_CINZEL, 9, col)


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


func _apply_button_font(node: Button, path: String, size: int, col: Color) -> void:
	if ResourceLoader.exists(path):
		node.add_theme_font_override("font", load(path) as Font)
	node.add_theme_font_size_override("font_size", size)
	node.add_theme_color_override("font_color", col)
	node.add_theme_color_override("font_hover_color", col)
	node.add_theme_color_override("font_pressed_color", col)
	node.add_theme_color_override("font_focus_color", col)
