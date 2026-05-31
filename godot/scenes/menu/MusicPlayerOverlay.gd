extends Control
## Music player overlay — full catalog list, heard/unheard, transport + seek,
## shuffle toggle, per-volume filtering, and a live now-playing bar driven by
## the global AudioMgr. Works from the main menu and the in-game HUD menu.

signal closed

const C_GOLD   := Color(0.78, 0.66, 0.29)
const C_BG     := Color(0.024, 0.020, 0.014, 0.97)
const C_BORDER := Color(0.70, 0.55, 0.24, 0.35)
const C_TXT    := Color(0.83, 0.79, 0.69)
const C_DIM    := Color(0.45, 0.43, 0.36, 0.6)

# Per-volume accent colors. Volumes not listed fall back to gold.
const VOL_COLORS := {
	3: Color(0.0, 0.78, 1.0),   # Vol 3 — The Earthman Chronicles (cyan)
	4: Color(1.0, 0.18, 0.0),   # Vol 4 — #/Sharp (red)
}

var _track_buttons: Dictionary = {}
var _now_lbl:    Label   = null
var _now_meta:   Label   = null
var _play_btn:   Button  = null
var _shuffle_btn: Button = null
var _seek:       HSlider = null
var _cur_time:   Label   = null
var _tot_time:   Label   = null
var _track_vbox: VBoxContainer = null
var _filter_row: HBoxContainer = null
var _heard_lbl:  Label   = null
var _catalog:    Array   = []
var _vol_filter: int     = 0      # 0 == all volumes
var _seeking:    bool    = false
var _built:      bool    = false


func _ready() -> void:
	set_process(false)


func open() -> void:
	if not _built:
		_build()
		_built = true
	_rebuild_tracks()
	_refresh()
	visible = true
	set_process(true)


func _close() -> void:
	visible = false
	set_process(false)
	closed.emit()


func _input(event: InputEvent) -> void:
	if not visible:
		return
	if event.is_action_pressed("menu_back"):
		_close()
		get_viewport().set_input_as_handled()


func _build() -> void:
	var backdrop := ColorRect.new()
	backdrop.color = Color(0, 0, 0, 0.7)
	backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(backdrop)

	var card := Panel.new()
	card.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	card.offset_left   = -500
	card.offset_right  = 500
	card.offset_top    = -300
	card.offset_bottom = 300
	var st := StyleBoxFlat.new()
	st.bg_color     = C_BG
	st.border_color = C_BORDER
	st.set_border_width_all(1)
	card.add_theme_stylebox_override("panel", st)
	add_child(card)

	var outer := VBoxContainer.new()
	outer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	outer.offset_left   = 28
	outer.offset_right  = -28
	outer.offset_top    = 20
	outer.offset_bottom = -20
	outer.add_theme_constant_override("separation", 10)
	card.add_child(outer)

	# Header row
	var header_row := HBoxContainer.new()
	outer.add_child(header_row)
	var title_lbl := Label.new()
	title_lbl.text = "MUSIC PLAYER"
	_apply_font(title_lbl, SkinDB.F_CINZEL, 13, C_GOLD)
	title_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header_row.add_child(title_lbl)
	_heard_lbl = Label.new()
	_apply_font(_heard_lbl, SkinDB.F_CINZEL, 9, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.55))
	_heard_lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	header_row.add_child(_heard_lbl)
	var close_btn := Button.new()
	close_btn.text = "✕"
	close_btn.custom_minimum_size = Vector2(32, 32)
	close_btn.pressed.connect(_close)
	header_row.add_child(close_btn)

	outer.add_child(_rule())

	# Now Playing block
	_now_lbl = Label.new()
	_now_lbl.text = "—"
	_apply_font(_now_lbl, SkinDB.F_IMFELL_I if ResourceLoader.exists(SkinDB.F_IMFELL_I) else SkinDB.F_IMFELL_R, 17, C_TXT)
	_now_lbl.clip_text = true
	outer.add_child(_now_lbl)

	_now_meta = Label.new()
	_now_meta.text = ""
	_apply_font(_now_meta, SkinDB.F_SPACEMONO if ResourceLoader.exists(SkinDB.F_SPACEMONO) else SkinDB.F_IMFELL_R, 9, C_DIM)
	_now_meta.clip_text = true
	outer.add_child(_now_meta)

	# Seek / progress row
	var seek_row := HBoxContainer.new()
	seek_row.add_theme_constant_override("separation", 10)
	outer.add_child(seek_row)
	_cur_time = _time_lbl("0:00")
	seek_row.add_child(_cur_time)
	_seek = HSlider.new()
	_seek.min_value = 0.0
	_seek.max_value = 1.0
	_seek.step = 0.0001
	_seek.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_seek.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	_seek.custom_minimum_size.y = 18
	_seek.drag_started.connect(func() -> void: _seeking = true)
	_seek.drag_ended.connect(func(_changed: bool) -> void:
		_apply_seek()
		_seeking = false)
	# Clicking the track (no drag) also seeks.
	_seek.value_changed.connect(func(_v: float) -> void:
		if not _seeking:
			_apply_seek())
	seek_row.add_child(_seek)
	_tot_time = _time_lbl("0:00")
	seek_row.add_child(_tot_time)

	# Transport controls
	var ctrl_row := HBoxContainer.new()
	ctrl_row.add_theme_constant_override("separation", 8)
	ctrl_row.alignment = BoxContainer.ALIGNMENT_CENTER
	outer.add_child(ctrl_row)

	var prev_btn := _ctrl_btn("◀◀")
	prev_btn.pressed.connect(func() -> void: AudioMgr.play_prev(); _refresh())
	ctrl_row.add_child(prev_btn)

	_play_btn = _ctrl_btn("▶")
	_play_btn.custom_minimum_size.x = 60
	_play_btn.pressed.connect(_on_play_pause)
	ctrl_row.add_child(_play_btn)

	var stop_btn := _ctrl_btn("■")
	stop_btn.pressed.connect(func() -> void: AudioMgr.stop_bgm(); _refresh())
	ctrl_row.add_child(stop_btn)

	var next_btn := _ctrl_btn("▶▶")
	next_btn.pressed.connect(func() -> void: AudioMgr.play_next(); _refresh())
	ctrl_row.add_child(next_btn)

	# Spacer + shuffle toggle
	var spacer := Control.new()
	spacer.custom_minimum_size.x = 16
	ctrl_row.add_child(spacer)
	_shuffle_btn = _ctrl_btn("⤮ SHUFFLE")
	_shuffle_btn.custom_minimum_size.x = 96
	_shuffle_btn.toggle_mode = true
	_shuffle_btn.button_pressed = AudioMgr.is_shuffle()
	_shuffle_btn.toggled.connect(func(on: bool) -> void:
		AudioMgr.set_shuffle(on)
		_style_shuffle())
	ctrl_row.add_child(_shuffle_btn)
	_style_shuffle()

	outer.add_child(_rule())

	# Volume filter row
	_filter_row = HBoxContainer.new()
	_filter_row.add_theme_constant_override("separation", 4)
	outer.add_child(_filter_row)

	# Track list
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	outer.add_child(scroll)

	_track_vbox = VBoxContainer.new()
	_track_vbox.add_theme_constant_override("separation", 2)
	_track_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_track_vbox)

	_catalog = SceneDataDB.get_music_catalog()
	_build_filter_row()

	# React to track changes from anywhere (in-game scene music, auto-advance).
	AudioMgr.track_changed.connect(_on_track_changed)


func _build_filter_row() -> void:
	for ch in _filter_row.get_children():
		ch.queue_free()
	var vols: Array = []
	for entry: Dictionary in _catalog:
		var v: int = int(entry.get("vol", 0))
		if v not in vols:
			vols.append(v)
	vols.sort()
	var entries: Array = [{"v": 0, "lbl": "ALL"}]
	for v: int in vols:
		entries.append({"v": v, "lbl": ("MENU" if v == 0 else "%02d" % v)})
	for e: Dictionary in entries:
		var v: int = e["v"]
		var btn := Button.new()
		btn.text = str(e["lbl"])
		btn.toggle_mode = true
		btn.button_pressed = (v == _vol_filter)
		btn.custom_minimum_size = Vector2(0, 24)
		_style_filter_btn(btn, v == _vol_filter, v)
		btn.pressed.connect(func() -> void:
			_vol_filter = v
			_rebuild_tracks()
			_refresh())
		_filter_row.add_child(btn)


func _rebuild_tracks() -> void:
	if _track_vbox == null:
		return
	for ch in _track_vbox.get_children():
		ch.queue_free()
	_track_buttons.clear()
	# Refresh filter-button highlight state.
	for child in _filter_row.get_children():
		if child is Button:
			(child as Button).button_pressed = false
	_build_filter_row()

	var cur_vol := -2
	for entry: Dictionary in _catalog:
		# Skip key-locked tracks that haven't been unlocked yet.
		var unlock: Dictionary = entry.get("unlock", {})
		if unlock.get("type", "") == "key":
			if not SaveSystem.is_unlocked(unlock.get("key", "")):
				continue

		var vol: int = int(entry.get("vol", 0))
		if _vol_filter != 0 and vol != _vol_filter:
			continue

		if vol != cur_vol:
			cur_vol = vol
			var vol_lbl := Label.new()
			vol_lbl.text = "  MENU" if vol == 0 else "  VOL. %d" % vol
			_apply_font(vol_lbl, SkinDB.F_CINZEL, 9, Color(_vol_color(vol).r, _vol_color(vol).g, _vol_color(vol).b, 0.6))
			vol_lbl.custom_minimum_size.y = 22
			_track_vbox.add_child(vol_lbl)

		_track_vbox.add_child(_make_track_row(entry))


func _make_track_row(entry: Dictionary) -> Button:
	var src: String = entry.get("src", "")
	var track_title: String = entry.get("title", src)
	var vol: int = int(entry.get("vol", 0))
	var accent := _vol_color(vol)

	var t_btn := Button.new()
	t_btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	t_btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
	t_btn.custom_minimum_size.y = 44
	_style_track_btn(t_btn, false, accent)

	var s: String = src
	t_btn.pressed.connect(func() -> void:
		AudioMgr.play_bgm(s)
		_refresh())

	var t_hbox := HBoxContainer.new()
	t_hbox.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	t_hbox.mouse_filter = Control.MOUSE_FILTER_IGNORE
	t_hbox.add_theme_constant_override("separation", 8)

	var dot_lbl := Label.new()
	dot_lbl.text = "●" if AudioMgr.is_heard(src) else "○"
	dot_lbl.add_theme_font_size_override("font_size", 10)
	dot_lbl.add_theme_color_override("font_color",
		Color(accent.r, accent.g, accent.b, 0.8) if AudioMgr.is_heard(src) else C_DIM)
	dot_lbl.custom_minimum_size.x = 16
	dot_lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	t_hbox.add_child(dot_lbl)

	var text_vbox := VBoxContainer.new()
	text_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	text_vbox.size_flags_vertical = Control.SIZE_EXPAND_FILL
	text_vbox.add_theme_constant_override("separation", 0)
	text_vbox.alignment = BoxContainer.ALIGNMENT_CENTER

	var name_lbl := Label.new()
	name_lbl.text = track_title
	_apply_font(name_lbl, SkinDB.F_IMFELL_R, 13, C_TXT)
	name_lbl.clip_text = true
	text_vbox.add_child(name_lbl)

	var desc: String = str(entry.get("desc", ""))
	var desc_lbl: Label = null
	if desc != "":
		desc_lbl = Label.new()
		desc_lbl.text = desc
		_apply_font(desc_lbl, SkinDB.F_SPACEMONO if ResourceLoader.exists(SkinDB.F_SPACEMONO) else SkinDB.F_IMFELL_R, 9, Color(C_TXT.r, C_TXT.g, C_TXT.b, 0.4))
		desc_lbl.clip_text = true
		text_vbox.add_child(desc_lbl)
	t_hbox.add_child(text_vbox)

	t_btn.add_child(t_hbox)
	_track_buttons[src] = {"btn": t_btn, "dot": dot_lbl, "name": name_lbl, "desc": desc_lbl, "accent": accent}
	return t_btn


func _refresh() -> void:
	var cur: String = AudioMgr.get_current_track()
	var entry := SceneDataDB.get_music_entry(cur)
	if cur != "":
		_now_lbl.text = entry.get("title", cur)
		var meta_parts: Array = []
		var composer: String = str(entry.get("composer", ""))
		if composer != "" and composer != "—":
			meta_parts.append(composer)
		var desc: String = str(entry.get("desc", ""))
		if desc != "":
			meta_parts.append(desc)
		_now_meta.text = "  ·  ".join(PackedStringArray(meta_parts))
	else:
		_now_lbl.text = "—"
		_now_meta.text = ""
	_play_btn.text = "⏸" if AudioMgr.is_playing() else "▶"

	# Heard count across full catalog.
	var heard_n := 0
	for e: Dictionary in _catalog:
		if AudioMgr.is_heard(e.get("src", "")):
			heard_n += 1
	_heard_lbl.text = "%d / %d HEARD" % [heard_n, _catalog.size()]

	for src in _track_buttons:
		var d: Dictionary = _track_buttons[src]
		var is_current: bool = (src == cur)
		var accent: Color = d["accent"]
		_style_track_btn(d["btn"] as Button, is_current, accent)
		(d["dot"] as Label).text = "▶" if (is_current and AudioMgr.is_playing()) else ("●" if AudioMgr.is_heard(src) else "○")
		(d["dot"] as Label).add_theme_color_override("font_color",
			accent if is_current else (Color(accent.r, accent.g, accent.b, 0.6) if AudioMgr.is_heard(src) else C_DIM))
		(d["name"] as Label).add_theme_color_override("font_color",
			accent if is_current else C_TXT)
	_update_seek()


func _process(_delta: float) -> void:
	if not visible:
		return
	_update_seek()
	# Keep the play/pause glyph in sync with auto-advance / external changes.
	var want := "⏸" if AudioMgr.is_playing() else "▶"
	if _play_btn.text != want:
		_play_btn.text = want


func _update_seek() -> void:
	var length := AudioMgr.get_stream_length()
	var pos := AudioMgr.get_playback_position()
	_tot_time.text = _fmt_time(length)
	_cur_time.text = _fmt_time(pos)
	if not _seeking:
		var frac := 0.0
		if length > 0.0:
			frac = clampf(pos / length, 0.0, 1.0)
		# Avoid re-triggering value_changed -> seek while syncing.
		_seek.set_block_signals(true)
		_seek.value = frac
		_seek.set_block_signals(false)


func _apply_seek() -> void:
	var length := AudioMgr.get_stream_length()
	if length > 0.0:
		AudioMgr.seek(_seek.value * length)


func _on_play_pause() -> void:
	if AudioMgr.is_playing():
		AudioMgr.pause_bgm()
	elif AudioMgr.is_paused():
		AudioMgr.resume_bgm()
	elif AudioMgr.get_current_track() != "":
		AudioMgr.play_bgm(AudioMgr.get_current_track())
	_refresh()


func _on_track_changed(_src: String) -> void:
	if visible:
		_refresh()


# ── Styling helpers ────────────────────────────────────────────────────────────

func _vol_color(vol: int) -> Color:
	return VOL_COLORS.get(vol, C_GOLD)


func _style_track_btn(btn: Button, active: bool, accent: Color) -> void:
	var st := StyleBoxFlat.new()
	st.bg_color     = Color(accent.r, accent.g, accent.b, 0.08) if active else Color(0, 0, 0, 0)
	st.border_color = Color(accent.r, accent.g, accent.b, 0.4)  if active else Color(0, 0, 0, 0)
	st.set_border_width_all(1 if active else 0)
	st.border_width_left = 3 if active else 0
	st.content_margin_left   = 10.0
	st.content_margin_right  = 8.0
	st.content_margin_top    = 4.0
	st.content_margin_bottom = 4.0
	btn.add_theme_stylebox_override("normal",  st)
	var hover_st := st.duplicate() as StyleBoxFlat
	hover_st.bg_color     = Color(accent.r, accent.g, accent.b, 0.12)
	hover_st.border_color = Color(accent.r, accent.g, accent.b, 0.5)
	hover_st.border_width_left = 3
	hover_st.set_border_width_all(1)
	hover_st.border_width_left = 3
	btn.add_theme_stylebox_override("hover",  hover_st)
	btn.add_theme_stylebox_override("focus",  hover_st)
	btn.add_theme_stylebox_override("pressed", hover_st)


func _style_filter_btn(btn: Button, active: bool, vol: int) -> void:
	var accent := _vol_color(vol)
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


func _style_shuffle() -> void:
	if _shuffle_btn == null:
		return
	var on := _shuffle_btn.button_pressed
	var col := C_GOLD if on else Color(C_TXT.r, C_TXT.g, C_TXT.b, 0.4)
	_apply_button_font(_shuffle_btn, SkinDB.F_SPACEMONO if ResourceLoader.exists(SkinDB.F_SPACEMONO) else SkinDB.F_CINZEL, 9, col)


func _ctrl_btn(text: String) -> Button:
	var btn := Button.new()
	btn.text = text
	btn.custom_minimum_size = Vector2(44, 36)
	return btn


func _time_lbl(text: String) -> Label:
	var lbl := Label.new()
	lbl.text = text
	_apply_font(lbl, SkinDB.F_SPACEMONO if ResourceLoader.exists(SkinDB.F_SPACEMONO) else SkinDB.F_IMFELL_R, 9, Color(C_TXT.r, C_TXT.g, C_TXT.b, 0.5))
	lbl.custom_minimum_size.x = 36
	lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	return lbl


func _fmt_time(seconds: float) -> String:
	if seconds <= 0.0 or is_nan(seconds) or is_inf(seconds):
		return "0:00"
	var total := int(seconds)
	return "%d:%02d" % [total / 60, total % 60]


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
