extends Control
## Music player overlay — full catalog list, heard/unheard, play controls.
## Works from main menu and in-game HUD menu.

signal closed

const C_GOLD   := Color(0.78, 0.66, 0.29)
const C_BG     := Color(0.024, 0.020, 0.014, 0.97)
const C_BORDER := Color(0.70, 0.55, 0.24, 0.35)
const C_TXT    := Color(0.83, 0.79, 0.69)

# TESTING: every track in the catalog shows up + plays regardless of
# SaveSystem unlock state. Flip to false to restore lock-gating.
const UNLOCK_ALL_TRACKS := true
const C_DIM    := Color(0.45, 0.43, 0.36, 0.6)

var _track_buttons: Dictionary = {}
var _now_lbl:   Label = null
var _play_btn:  Button = null
var _catalog:   Array  = []
var _built:     bool   = false


func open() -> void:
	# Always rebuild — cheap and avoids stale-cache bugs after
	# unlock changes or hot-reload of the catalog.
	for ch in get_children():
		ch.queue_free()
	_track_buttons.clear()
	_built = false
	_build()
	_built = true
	_refresh()
	visible = true


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
	var close_btn := Button.new()
	close_btn.text = "✕"
	close_btn.custom_minimum_size = Vector2(32, 32)
	close_btn.pressed.connect(func() -> void: visible = false; closed.emit())
	header_row.add_child(close_btn)

	outer.add_child(_rule())

	# Now Playing row
	var np_row := HBoxContainer.new()
	np_row.add_theme_constant_override("separation", 6)
	outer.add_child(np_row)
	var np_lbl := Label.new()
	np_lbl.text = "NOW PLAYING"
	_apply_font(np_lbl, SkinDB.F_CINZEL, 9, C_DIM)
	np_row.add_child(np_lbl)
	_now_lbl = Label.new()
	_now_lbl.text = "—"
	_apply_font(_now_lbl, SkinDB.F_IMFELL_R, 14, C_TXT)
	_now_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_now_lbl.clip_text = true
	np_row.add_child(_now_lbl)

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

	outer.add_child(_rule())

	# Track list
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	outer.add_child(scroll)

	var track_vbox := VBoxContainer.new()
	track_vbox.add_theme_constant_override("separation", 2)
	track_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(track_vbox)

	_catalog = SceneDataDB.get_music_catalog()
	print("[MusicPlayer] catalog size: ", _catalog.size(),
	      " · UNLOCK_ALL_TRACKS=", UNLOCK_ALL_TRACKS)
	var cur_vol := -2
	var _added := 0
	for entry: Dictionary in _catalog:
		# TESTING: every track unlocked. To restore key-gated locks, flip
		# UNLOCK_ALL_TRACKS (declared at script scope above) to false.
		var unlock: Dictionary = entry.get("unlock", {})
		if not UNLOCK_ALL_TRACKS and unlock.get("type", "") == "key":
			if not SaveSystem.is_unlocked(unlock.get("key", "")):
				continue

		var vol: int = int(entry.get("vol", 0))
		if vol != cur_vol:
			cur_vol = vol
			var vol_lbl := Label.new()
			vol_lbl.text = "  MENU" if vol == 0 else "  VOL. %d" % vol
			_apply_font(vol_lbl, SkinDB.F_CINZEL, 9, Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.55))
			vol_lbl.custom_minimum_size.y = 22
			track_vbox.add_child(vol_lbl)

		var src: String = entry.get("src", "")
		var track_title: String = entry.get("title", src)

		var t_btn := Button.new()
		t_btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		t_btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		_style_track_btn(t_btn, false, false)
		t_btn.custom_minimum_size.y = 36

		var s: String = src
		t_btn.pressed.connect(func() -> void:
			AudioMgr.play_bgm(s)
			_refresh()
		)

		var t_hbox := HBoxContainer.new()
		t_hbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		t_hbox.mouse_filter = Control.MOUSE_FILTER_IGNORE
		t_hbox.add_theme_constant_override("separation", 8)

		var dot_lbl := Label.new()
		dot_lbl.text = "●" if AudioMgr.is_heard(src) else "○"
		dot_lbl.add_theme_font_size_override("font_size", 10)
		dot_lbl.add_theme_color_override("font_color",
			Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.8) if AudioMgr.is_heard(src) else C_DIM)
		dot_lbl.custom_minimum_size.x = 16
		t_hbox.add_child(dot_lbl)

		var name_lbl := Label.new()
		name_lbl.text = track_title
		_apply_font(name_lbl, SkinDB.F_IMFELL_R, 13, C_TXT)
		name_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		name_lbl.clip_text = true
		t_hbox.add_child(name_lbl)

		t_btn.add_child(t_hbox)
		track_vbox.add_child(t_btn)
		_track_buttons[src] = {"btn": t_btn, "dot": dot_lbl, "name": name_lbl}
		_added += 1
	print("[MusicPlayer] added ", _added, " track buttons")

	# Connect track change signal
	AudioMgr.track_changed.connect(_on_track_changed)


func _refresh() -> void:
	var cur: String = AudioMgr.get_current_track()
	var entry := SceneDataDB.get_music_entry(cur)
	_now_lbl.text = entry.get("title", cur) if cur != "" else "—"
	_play_btn.text = "⏸" if AudioMgr.is_playing() else "▶"
	for src in _track_buttons:
		var d: Dictionary = _track_buttons[src]
		var is_current: bool = (src == cur)
		_style_track_btn(d["btn"] as Button, is_current, AudioMgr.is_heard(src))
		(d["dot"] as Label).text = "●" if AudioMgr.is_heard(src) else "○"
		(d["dot"] as Label).add_theme_color_override("font_color",
			C_GOLD if is_current else (Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.6) if AudioMgr.is_heard(src) else C_DIM))
		(d["name"] as Label).add_theme_color_override("font_color",
			C_GOLD if is_current else C_TXT)


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


func _style_track_btn(btn: Button, active: bool, _heard: bool) -> void:
	var st := StyleBoxFlat.new()
	st.bg_color     = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.08) if active else Color(0, 0, 0, 0)
	st.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.4)  if active else Color(0, 0, 0, 0)
	st.set_border_width_all(1 if active else 0)
	st.content_margin_left   = 8.0
	st.content_margin_right  = 8.0
	st.content_margin_top    = 4.0
	st.content_margin_bottom = 4.0
	btn.add_theme_stylebox_override("normal",  st)
	var hover_st := st.duplicate() as StyleBoxFlat
	hover_st.bg_color     = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.12)
	hover_st.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.5)
	hover_st.set_border_width_all(1)
	btn.add_theme_stylebox_override("hover",  hover_st)
	btn.add_theme_stylebox_override("focus",  hover_st)
	btn.add_theme_stylebox_override("pressed", hover_st)


func _ctrl_btn(text: String) -> Button:
	var btn := Button.new()
	btn.text = text
	btn.custom_minimum_size = Vector2(44, 36)
	return btn


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
