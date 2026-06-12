extends Control
## Music player overlay — full catalog list, heard/unheard, play controls.
## Works from main menu and in-game HUD menu.
##
## Skinnable: SKINS holds N palette+font definitions. Each skin has an
## `unlock` clause (key/heard/none). The active skin is read from
## Settings.music_skin at open(); a `[SKIN ▾]` dropdown in the header
## lets the user switch among unlocked skins. Visualizer plug-in slot
## is reserved next to the transport row but not yet populated.

signal closed

# When TRUE, every catalog track + every skin is visible regardless of
# unlock state — useful for studio testing. In ship mode this is FALSE.
const UNLOCK_ALL_TRACKS := false
const UNLOCK_ALL_SKINS  := false

# ── Skin definitions ─────────────────────────────────────────────────
# Each skin is a palette + font swap for the music overlay. The first
# entry is the default and is always unlocked. `unlock` is one of:
#   {}                                — always unlocked
#   {type: "key",   key: "..."}        — SaveSystem.is_unlocked(key)
#   {type: "heard", src: "..."}        — AudioMgr.is_heard(src)
const SKINS := [
	{
		"id": "diner_booth",
		"name": "Diner Booth",
		"unlock": {},
		"bg":     Color(0.024, 0.020, 0.014, 0.97),
		"border": Color(0.70, 0.55, 0.24, 0.35),
		"accent": Color(0.78, 0.66, 0.29),
		"txt":    Color(0.83, 0.79, 0.69),
		"dim":    Color(0.45, 0.43, 0.36, 0.6),
		"title_font": "res://resources/fonts/Cinzel-Regular.ttf",
		"title_size": 13,
		"label_font": "res://resources/fonts/Cinzel-Regular.ttf",
		"label_size": 9,
		"track_font": "res://resources/fonts/IMFellEnglish-Regular.ttf",
		"track_size": 13,
	},
	{
		"id": "cathedral",
		"name": "Cathedral of Rust",
		"unlock": {"type": "key", "key": "milestone:gauntlet_win"},
		"bg":     Color(0.043, 0.027, 0.020, 0.97),
		"border": Color(0.62, 0.38, 0.22, 0.40),
		"accent": Color(0.85, 0.45, 0.22),
		"txt":    Color(0.82, 0.72, 0.60),
		"dim":    Color(0.45, 0.36, 0.27, 0.6),
		"title_font": "res://resources/fonts/Cinzel-Regular.ttf",
		"title_size": 13,
		"label_font": "res://resources/fonts/SpaceMono-Regular.ttf",
		"label_size": 9,
		"track_font": "res://resources/fonts/IMFellEnglish-Regular.ttf",
		"track_size": 13,
	},
	{
		"id": "tape_reel",
		"name": "Tape Reel",
		"unlock": {"type": "heard", "src": "assets/audio/bgm/vol5_elicia_theme_solo.ogg"},
		"bg":     Color(0.087, 0.067, 0.043, 0.97),
		"border": Color(0.65, 0.52, 0.31, 0.40),
		"accent": Color(0.92, 0.83, 0.55),
		"txt":    Color(0.92, 0.87, 0.74),
		"dim":    Color(0.62, 0.55, 0.38, 0.6),
		"title_font": "res://resources/fonts/SpecialElite-Regular.ttf",
		"title_size": 13,
		"label_font": "res://resources/fonts/SpecialElite-Regular.ttf",
		"label_size": 9,
		"track_font": "res://resources/fonts/SpecialElite-Regular.ttf",
		"track_size": 13,
	},
	{
		"id": "riverboat",
		"name": "Riverboat",
		"unlock": {"type": "heard", "src": "assets/audio/bgm/vol5_riverboat_drone.ogg"},
		"bg":     Color(0.012, 0.043, 0.027, 0.97),
		"border": Color(0.40, 0.62, 0.30, 0.40),
		"accent": Color(0.85, 0.71, 0.27),
		"txt":    Color(0.78, 0.85, 0.71),
		"dim":    Color(0.40, 0.45, 0.36, 0.6),
		"title_font": "res://resources/fonts/Cinzel-Regular.ttf",
		"title_size": 13,
		"label_font": "res://resources/fonts/Cinzel-Regular.ttf",
		"label_size": 9,
		"track_font": "res://resources/fonts/IMFellEnglish-Regular.ttf",
		"track_size": 13,
	},
	{
		"id": "twenty_four_hour_diner",
		"name": "24-Hour Diner",
		"unlock": {"type": "key", "key": "milestone:gauntlet_loss"},
		"bg":     Color(0.020, 0.020, 0.024, 0.97),
		"border": Color(0.92, 0.38, 0.55, 0.45),
		"accent": Color(0.20, 0.95, 0.85),
		"txt":    Color(0.85, 0.88, 0.92),
		"dim":    Color(0.45, 0.48, 0.52, 0.6),
		"title_font": "res://resources/fonts/BebasNeue-Regular.ttf",
		"title_size": 14,
		"label_font": "res://resources/fonts/BebasNeue-Regular.ttf",
		"label_size": 10,
		"track_font": "res://resources/fonts/CourierPrime-Regular.ttf",
		"track_size": 13,
	},
	{
		"id": "full_moon",
		"name": "Full Moon",
		"unlock": {"type": "key", "key": "milestone:candles_lit"},
		"bg":     Color(0.027, 0.024, 0.043, 0.97),
		"border": Color(0.62, 0.55, 0.85, 0.40),
		"accent": Color(0.85, 0.82, 0.92),
		"txt":    Color(0.85, 0.82, 0.92),
		"dim":    Color(0.50, 0.48, 0.60, 0.6),
		"title_font": "res://resources/fonts/Cinzel-Regular.ttf",
		"title_size": 13,
		"label_font": "res://resources/fonts/Cinzel-Regular.ttf",
		"label_size": 9,
		"track_font": "res://resources/fonts/IMFellEnglish-Regular.ttf",
		"track_size": 13,
	},
]

var _skin:          Dictionary = {}
var _track_buttons: Dictionary = {}
var _now_lbl:       Label  = null
var _play_btn:      Button = null
var _skin_menu_btn: MenuButton = null
var _viz_menu_btn:  MenuButton = null
var _viz_host:      Control = null
var _viz:           Control = null
var _catalog:       Array  = []
var _built:         bool   = false


const _VizScene := preload("res://scenes/menu/MusicVisualizer.gd")


func open() -> void:
	# Always rebuild — cheap and avoids stale-cache bugs after
	# unlock changes or hot-reload of the catalog.
	for ch in get_children():
		ch.queue_free()
	_track_buttons.clear()
	_built = false
	_skin = _resolve_active_skin()
	_build()
	_built = true
	_refresh()
	visible = true


# ── Skin resolution ──────────────────────────────────────────────────
# Pick the skin the user selected via Settings.music_skin, if it's
# unlocked. Otherwise fall back to the first unlocked skin (default
# diner_booth is always unlocked).
func _resolve_active_skin() -> Dictionary:
	var want: String = Settings.music_skin
	for s: Dictionary in SKINS:
		if s["id"] == want and _skin_unlocked(s):
			return s
	return SKINS[0]


func _skin_unlocked(s: Dictionary) -> bool:
	if UNLOCK_ALL_SKINS:
		return true
	var u: Dictionary = s.get("unlock", {})
	var t: String = String(u.get("type", ""))
	if t == "":
		return true
	if t == "key":
		return SaveSystem.is_unlocked(String(u.get("key", "")))
	if t == "heard":
		return AudioMgr.is_heard(String(u.get("src", "")))
	return false


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
	st.bg_color     = _skin["bg"]
	st.border_color = _skin["border"]
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
	title_lbl.text = "MUSIC PLAYER · " + String(_skin["name"]).to_upper()
	_apply_font(title_lbl, _skin["title_font"], _skin["title_size"], _skin["accent"])
	title_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header_row.add_child(title_lbl)

	# Skin dropdown — lists unlocked skins, lets the user switch live.
	_skin_menu_btn = MenuButton.new()
	_skin_menu_btn.text = "SKIN ▾"
	_skin_menu_btn.custom_minimum_size = Vector2(80, 32)
	_apply_font_btn(_skin_menu_btn, _skin["label_font"], _skin["label_size"], _skin["accent"])
	_populate_skin_menu()
	header_row.add_child(_skin_menu_btn)

	# Visualizer dropdown — same shape as skin, scoped to viz modes.
	_viz_menu_btn = MenuButton.new()
	_viz_menu_btn.text = "VIZ ▾"
	_viz_menu_btn.custom_minimum_size = Vector2(72, 32)
	_apply_font_btn(_viz_menu_btn, _skin["label_font"], _skin["label_size"], _skin["accent"])
	_populate_viz_menu()
	header_row.add_child(_viz_menu_btn)

	var close_btn := Button.new()
	close_btn.text = "✕"
	close_btn.custom_minimum_size = Vector2(32, 32)
	close_btn.pressed.connect(func() -> void: visible = false; closed.emit())
	header_row.add_child(close_btn)

	outer.add_child(_rule())

	# Visualizer host (above NOW PLAYING) — instantiate the visualizer
	# Control inline, drive its mode via Settings.music_viz (filtered
	# to unlocked viz modes).
	_viz_host = Control.new()
	_viz_host.custom_minimum_size = Vector2(0, 64)
	_viz_host.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	outer.add_child(_viz_host)
	_viz = _VizScene.new()
	_viz.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_viz.set_colors(_skin["accent"], _skin["dim"], _skin["txt"])
	_viz.set_mode(_resolve_active_viz_id())
	_viz_host.add_child(_viz)

	# Now Playing row
	var np_row := HBoxContainer.new()
	np_row.add_theme_constant_override("separation", 6)
	outer.add_child(np_row)
	var np_lbl := Label.new()
	np_lbl.text = "NOW PLAYING"
	_apply_font(np_lbl, _skin["label_font"], _skin["label_size"], _skin["dim"])
	np_row.add_child(np_lbl)
	_now_lbl = Label.new()
	_now_lbl.text = "—"
	_apply_font(_now_lbl, _skin["track_font"], 14, _skin["txt"])
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
		  " · UNLOCK_ALL_TRACKS=", UNLOCK_ALL_TRACKS,
		  " · skin=", _skin["id"])
	var cur_vol := -2
	var _added := 0
	for entry: Dictionary in _catalog:
		var unlock: Dictionary = entry.get("unlock", {})
		var unlock_type: String = String(unlock.get("type", ""))
		var src_for_gate: String = String(entry.get("src", ""))
		if not UNLOCK_ALL_TRACKS:
			if unlock_type == "key":
				if not SaveSystem.is_unlocked(String(unlock.get("key", ""))):
					continue
			elif unlock_type == "heard":
				if not AudioMgr.is_heard(src_for_gate):
					continue

		var vol: int = int(entry.get("vol", 0))
		if vol != cur_vol:
			cur_vol = vol
			var vol_lbl := Label.new()
			vol_lbl.text = "  MENU" if vol == 0 else "  VOL. %d" % vol
			var dimmed_accent: Color = Color(_skin["accent"].r, _skin["accent"].g, _skin["accent"].b, 0.55)
			_apply_font(vol_lbl, _skin["label_font"], _skin["label_size"], dimmed_accent)
			vol_lbl.custom_minimum_size.y = 22
			track_vbox.add_child(vol_lbl)

		var src: String = entry.get("src", "")
		var track_title: String = entry.get("title", src)

		var t_btn := Button.new()
		t_btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		t_btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		_style_track_btn(t_btn, false)
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
			Color(_skin["accent"].r, _skin["accent"].g, _skin["accent"].b, 0.8) if AudioMgr.is_heard(src) else _skin["dim"])
		dot_lbl.custom_minimum_size.x = 16
		t_hbox.add_child(dot_lbl)

		var name_lbl := Label.new()
		name_lbl.text = track_title
		_apply_font(name_lbl, _skin["track_font"], _skin["track_size"], _skin["txt"])
		name_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		name_lbl.clip_text = true
		t_hbox.add_child(name_lbl)

		t_btn.add_child(t_hbox)
		track_vbox.add_child(t_btn)
		_track_buttons[src] = {"btn": t_btn, "dot": dot_lbl, "name": name_lbl}
		_added += 1
	print("[MusicPlayer] added ", _added, " track buttons")

	AudioMgr.track_changed.connect(_on_track_changed)


# ── Skin dropdown ────────────────────────────────────────────────────
func _populate_skin_menu() -> void:
	var pop: PopupMenu = _skin_menu_btn.get_popup()
	pop.clear()
	# Filter to unlocked skins, with a count of locked ones rendered
	# as a disabled trailing entry so the player sees there's more.
	var locked: int = 0
	for i in SKINS.size():
		var s: Dictionary = SKINS[i]
		if _skin_unlocked(s):
			var marker: String = "• " if s["id"] == _skin["id"] else "  "
			pop.add_item(marker + String(s["name"]), i)
		else:
			locked += 1
	if locked > 0:
		pop.add_separator()
		var locked_idx: int = pop.item_count
		pop.add_item("(%d locked)" % locked, 9999)
		pop.set_item_disabled(locked_idx, true)
	if not pop.id_pressed.is_connected(_on_skin_picked):
		pop.id_pressed.connect(_on_skin_picked)


func _on_skin_picked(id: int) -> void:
	if id < 0 or id >= SKINS.size():
		return
	var picked: Dictionary = SKINS[id]
	if not _skin_unlocked(picked):
		return
	Settings.music_skin = String(picked["id"])
	open()  # rebuild with the new skin


# ── Visualizer dropdown + resolution ─────────────────────────────────
# The available visualizers and their unlock criteria live on the
# MusicVisualizer class itself, so the dropdown stays in sync with
# whatever modes the visualizer knows how to draw.
func _resolve_active_viz_id() -> String:
	var want: String = Settings.music_viz
	for v: Dictionary in _VizScene.VIZ:
		if v["id"] == want and _VizScene.viz_unlocked(v):
			return String(v["id"])
	return String((_VizScene.VIZ[0] as Dictionary)["id"])


func _populate_viz_menu() -> void:
	var pop: PopupMenu = _viz_menu_btn.get_popup()
	pop.clear()
	var active: String = String(_viz.mode) if _viz != null else _resolve_active_viz_id()
	var locked: int = 0
	for i in _VizScene.VIZ.size():
		var v: Dictionary = _VizScene.VIZ[i]
		if _VizScene.viz_unlocked(v):
			var marker: String = "• " if v["id"] == active else "  "
			pop.add_item(marker + String(v["name"]), i)
		else:
			locked += 1
	if locked > 0:
		pop.add_separator()
		var locked_idx: int = pop.item_count
		pop.add_item("(%d locked)" % locked, 9999)
		pop.set_item_disabled(locked_idx, true)
	if not pop.id_pressed.is_connected(_on_viz_picked):
		pop.id_pressed.connect(_on_viz_picked)


func _on_viz_picked(id: int) -> void:
	if id < 0 or id >= _VizScene.VIZ.size():
		return
	var picked: Dictionary = _VizScene.VIZ[id]
	if not _VizScene.viz_unlocked(picked):
		return
	Settings.music_viz = String(picked["id"])
	if _viz != null:
		_viz.set_mode(String(picked["id"]))
	_populate_viz_menu()  # refresh the • marker


func _refresh() -> void:
	var cur: String = AudioMgr.get_current_track()
	var entry := SceneDataDB.get_music_entry(cur)
	_now_lbl.text = entry.get("title", cur) if cur != "" else "—"
	_play_btn.text = "⏸" if AudioMgr.is_playing() else "▶"
	for src in _track_buttons:
		var d: Dictionary = _track_buttons[src]
		var is_current: bool = (src == cur)
		_style_track_btn(d["btn"] as Button, is_current)
		(d["dot"] as Label).text = "●" if AudioMgr.is_heard(src) else "○"
		(d["dot"] as Label).add_theme_color_override("font_color",
			_skin["accent"] if is_current else (Color(_skin["accent"].r, _skin["accent"].g, _skin["accent"].b, 0.6) if AudioMgr.is_heard(src) else _skin["dim"]))
		(d["name"] as Label).add_theme_color_override("font_color",
			_skin["accent"] if is_current else _skin["txt"])


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


func _style_track_btn(btn: Button, active: bool) -> void:
	var accent: Color = _skin["accent"]
	var st := StyleBoxFlat.new()
	st.bg_color     = Color(accent.r, accent.g, accent.b, 0.08) if active else Color(0, 0, 0, 0)
	st.border_color = Color(accent.r, accent.g, accent.b, 0.4)  if active else Color(0, 0, 0, 0)
	st.set_border_width_all(1 if active else 0)
	st.content_margin_left   = 8.0
	st.content_margin_right  = 8.0
	st.content_margin_top    = 4.0
	st.content_margin_bottom = 4.0
	btn.add_theme_stylebox_override("normal",  st)
	var hover_st := st.duplicate() as StyleBoxFlat
	hover_st.bg_color     = Color(accent.r, accent.g, accent.b, 0.12)
	hover_st.border_color = Color(accent.r, accent.g, accent.b, 0.5)
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
	r.color = _skin["border"]
	r.custom_minimum_size.y = 1
	return r


func _apply_font(node: Label, path: String, size: int, col: Color) -> void:
	if ResourceLoader.exists(path):
		node.add_theme_font_override("font", load(path) as Font)
	node.add_theme_font_size_override("font_size", size)
	node.add_theme_color_override("font_color", col)


func _apply_font_btn(node: Button, path: String, size: int, col: Color) -> void:
	if ResourceLoader.exists(path):
		node.add_theme_font_override("font", load(path) as Font)
	node.add_theme_font_size_override("font_size", size)
	node.add_theme_color_override("font_color", col)
