extends Control
## Main menu — literary dark aesthetic, left nav + right volumes panel + overlays.

signal play_requested(vol: int, scene_id: String, start_node: int)
signal load_requested(slot: int)

const C_GOLD    := Color(0.78, 0.66, 0.29)
const C_GOLD_DIM := Color(0.78, 0.66, 0.29, 0.5)
const C_BG      := Color(0.024, 0.018, 0.012)
const C_PANEL   := Color(0.031, 0.024, 0.016, 0.92)
const C_BORDER  := Color(0.70, 0.55, 0.24, 0.30)
const C_TXT     := Color(0.83, 0.79, 0.69)
const C_DIM     := Color(0.45, 0.43, 0.36, 0.6)
const C_LOCKED  := Color(0.35, 0.33, 0.29, 0.5)
const LEFT_W    := 310

const VOLUME_META: Array = [
	{"vol": 1,  "title": "Modern Mythology",          "skin": "literary",  "locked": false},
	{"vol": 2,  "title": "Small Wood Volumes",         "skin": "literary",  "locked": false},
	{"vol": 3,  "title": "The Earthman Chronicles",    "skin": "signal",    "locked": false},
	{"vol": 4,  "title": "#/Sharp",                    "skin": "zine",      "locked": false},
	{"vol": 5,  "title": "Major Arcana",               "skin": "arcana",    "locked": false},
	{"vol": 6,  "title": "Planned Community",          "skin": "suburban",  "locked": false},
	{"vol": 7,  "title": "Land of Milk & Honey",       "skin": "pastoral",  "locked": false},
	{"vol": 8,  "title": "SCUMM",                      "skin": "scumm",     "locked": true},
	{"vol": 9,  "title": "Por Puesto",                 "skin": "caliente",  "locked": true},
	{"vol": 10, "title": "ROFLcopter",                 "skin": "glitch",    "locked": true},
]

var _sel_vol:         int     = 1
var _chapter_vbox:    VBoxContainer = null
var _vol_buttons:     Dictionary   = {}
var _continue_btn:    Button       = null

# Overlay instances (created once, shown/hidden)
var _save_overlay:     Control = null
var _settings_overlay: Control = null
var _gallery_overlay:  Control = null
var _music_overlay:    Control = null
var _editor_overlay:   Control = null
var _unlock_overlay:   Control = null


func _ready() -> void:
	_build_ui()
	_build_overlays()
	_select_vol(1)
	_play_title_music()
	# Pad support · give the d-pad somewhere to start.
	GamepadMgr.focus_first.call_deferred(self)
	# Fade in from black — the book opens.
	modulate = Color(1, 1, 1, 0)
	var tw := create_tween()
	tw.tween_property(self, "modulate:a", 1.0, 0.7)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)


func _build_ui() -> void:
	# ── Background ───────────────────────────────────────────────────────────
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Procedural frontispiece over the flat fill: lamplight from the
	# upper left, paper-tooth grain, a dim compass ring behind the
	# volumes panel. Drawn once at boot, deterministic.
	var backdrop := TextureRect.new()
	backdrop.texture = _make_backdrop_tex()
	backdrop.stretch_mode = TextureRect.STRETCH_SCALE
	backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	backdrop.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(backdrop)
	# Frontispiece motion — grain drifting in the lamplight
	# (menu motion playbook).
	preload("res://scenes/games/TitleMotion.gd").attach(self, "shelf")

	# Gradient rule at top
	var rule_stops: Array = [
		[0.00, Color(0.706, 0.549, 0.235, 0.0)],
		[0.05, Color(0.706, 0.549, 0.235, 0.25)],
		[0.50, Color(0.863, 0.769, 0.314, 0.5)],
		[0.95, Color(0.706, 0.549, 0.235, 0.25)],
		[1.00, Color(0.706, 0.549, 0.235, 0.0)],
	]
	var rule_tex := SkinDB.make_rule_tex(rule_stops)
	var rule := TextureRect.new()
	rule.texture      = rule_tex
	rule.stretch_mode = TextureRect.STRETCH_SCALE
	rule.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	rule.custom_minimum_size.y = 2
	rule.size.y = 2
	add_child(rule)

	# ── Left panel ────────────────────────────────────────────────────────────
	var left := Control.new()
	left.anchor_left   = 0.0
	left.anchor_top    = 0.0
	left.anchor_right  = 0.0
	left.anchor_bottom = 1.0
	left.offset_right  = LEFT_W
	add_child(left)

	# Left background
	var left_bg := ColorRect.new()
	left_bg.color = C_PANEL
	left_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	left.add_child(left_bg)

	# Left border (right edge)
	var left_border := ColorRect.new()
	left_border.color = C_BORDER
	left_border.anchor_left   = 1.0
	left_border.anchor_top    = 0.0
	left_border.anchor_right  = 1.0
	left_border.anchor_bottom = 1.0
	left_border.offset_left   = -1
	left_border.offset_right  = 0
	left.add_child(left_border)

	var left_inner := VBoxContainer.new()
	left_inner.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	left_inner.offset_left   = 28
	left_inner.offset_right  = -20
	left_inner.offset_top    = 52
	left_inner.offset_bottom = -24
	left_inner.add_theme_constant_override("separation", 0)
	left.add_child(left_inner)

	# Title
	var title := Label.new()
	title.text = "MODERN\nMYTHOLOGY"
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		title.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	title.add_theme_font_size_override("font_size", 34)
	title.add_theme_color_override("font_color", C_GOLD)
	title.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.85))
	title.add_theme_constant_override("shadow_offset_x", 2)
	title.add_theme_constant_override("shadow_offset_y", 2)
	title.custom_minimum_size.y = 100
	left_inner.add_child(title)

	# Edition label
	var edition := Label.new()
	edition.text = "A Literary Visual Novel"
	edition.add_theme_font_size_override("font_size", 13)
	edition.add_theme_color_override("font_color", C_DIM)
	edition.custom_minimum_size.y = 32
	left_inner.add_child(edition)

	# Ornament rule — rule · diamond · rule, a book plate's divider.
	var orn_row := HBoxContainer.new()
	orn_row.add_theme_constant_override("separation", 8)
	var orn_r1 := _make_rule_rect()
	orn_r1.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	orn_r1.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	orn_row.add_child(orn_r1)
	var orn := Label.new()
	orn.text = "◆"
	orn.add_theme_font_size_override("font_size", 12)
	orn.add_theme_color_override("font_color", C_GOLD_DIM)
	orn_row.add_child(orn)
	var orn_r2 := _make_rule_rect()
	orn_r2.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	orn_r2.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	orn_row.add_child(orn_r2)
	left_inner.add_child(orn_row)

	var spacer0 := Control.new()
	spacer0.custom_minimum_size.y = 12
	left_inner.add_child(spacer0)

	# Primary buttons
	var new_btn := _nav_btn("NEW GAME")
	new_btn.pressed.connect(_on_new_game)
	left_inner.add_child(new_btn)

	_continue_btn = _nav_btn("CONTINUE")
	_continue_btn.pressed.connect(_on_continue)
	_continue_btn.disabled = not SaveSystem.has_any_save()
	left_inner.add_child(_continue_btn)

	var spacer1 := Control.new()
	spacer1.custom_minimum_size.y = 8
	left_inner.add_child(spacer1)

	left_inner.add_child(_make_rule_rect())

	var spacer2 := Control.new()
	spacer2.custom_minimum_size.y = 8
	left_inner.add_child(spacer2)

	# Secondary buttons
	for btn_data: Array in [
		["THE ALMANAC",       _on_almanac],
		["GALLERY",           _on_gallery],
		["MUSIC PLAYER",      _on_music],
		["ACHIEVEMENTS",      _on_achievements],
		["SCRAPBOOK",         _on_scrapbook],
		["PROFILE",           _on_profile],
		["SLOWSTOCK LIBRARY", _on_slowstock_library],
		["SETTINGS",          _on_settings],
		["SCENE EDITOR",      _on_editor],
	]:
		var btn := _nav_btn_small(btn_data[0] as String)
		btn.pressed.connect(btn_data[1] as Callable)
		left_inner.add_child(btn)

	var spacer3 := Control.new()
	spacer3.size_flags_vertical = Control.SIZE_EXPAND_FILL
	left_inner.add_child(spacer3)

	left_inner.add_child(_make_rule_rect())

	var spacer4 := Control.new()
	spacer4.custom_minimum_size.y = 8
	left_inner.add_child(spacer4)

	var quit_btn := _nav_btn_small("QUIT")
	quit_btn.pressed.connect(func() -> void: get_tree().quit())
	left_inner.add_child(quit_btn)

	# ── Right panel ───────────────────────────────────────────────────────────
	var right := Control.new()
	right.anchor_left   = 0.0
	right.anchor_top    = 0.0
	right.anchor_right  = 1.0
	right.anchor_bottom = 1.0
	right.offset_left   = LEFT_W + 1
	add_child(right)

	var right_inner := VBoxContainer.new()
	right_inner.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	right_inner.offset_left   = 40
	right_inner.offset_right  = -40
	right_inner.offset_top    = 44
	right_inner.offset_bottom = -24
	right_inner.add_theme_constant_override("separation", 14)
	right.add_child(right_inner)

	# Volumes header
	var vol_header_row := HBoxContainer.new()
	right_inner.add_child(vol_header_row)
	var vol_header := Label.new()
	vol_header.text = "VOLUMES"
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		vol_header.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	vol_header.add_theme_font_size_override("font_size", 13)
	vol_header.add_theme_color_override("font_color", C_GOLD_DIM)
	vol_header.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vol_header_row.add_child(vol_header)

	right_inner.add_child(_make_rule_rect())

	# Content area: volume list (left) + chapter list (right)
	var content_row := HBoxContainer.new()
	content_row.size_flags_vertical = Control.SIZE_EXPAND_FILL
	content_row.add_theme_constant_override("separation", 24)
	right_inner.add_child(content_row)

	# Volume list
	var vol_scroll := ScrollContainer.new()
	vol_scroll.custom_minimum_size.x = 340
	vol_scroll.vertical_scroll_mode  = ScrollContainer.SCROLL_MODE_AUTO
	vol_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	content_row.add_child(vol_scroll)

	var vol_vbox := VBoxContainer.new()
	vol_vbox.add_theme_constant_override("separation", 4)
	vol_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vol_scroll.add_child(vol_vbox)

	for meta: Dictionary in VOLUME_META:
		var vol: int       = meta.get("vol", 0)
		var vol_title: String = meta.get("title", "")
		var locked: bool   = meta.get("locked", false)

		var vbtn := Button.new()
		vbtn.text = "%02d  %s" % [vol, vol_title.to_upper()]
		if locked:
			vbtn.text += "    🔒"
		vbtn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		vbtn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		vbtn.custom_minimum_size.y = 40
		vbtn.disabled = locked
		_style_vol_btn(vbtn, false, locked)
		if not locked:
			var v: int = vol
			vbtn.pressed.connect(func() -> void: _select_vol(v))
		vol_vbox.add_child(vbtn)
		if not locked:
			_vol_buttons[vol] = vbtn

	# Vertical divider
	var vdiv := ColorRect.new()
	vdiv.color = C_BORDER
	vdiv.custom_minimum_size.x = 1
	content_row.add_child(vdiv)

	# Chapter panel (right side of content)
	var chap_col := VBoxContainer.new()
	chap_col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	chap_col.add_theme_constant_override("separation", 8)
	content_row.add_child(chap_col)

	var chap_header := Label.new()
	chap_header.text = "CHAPTERS"
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		chap_header.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	chap_header.add_theme_font_size_override("font_size", 13)
	chap_header.add_theme_color_override("font_color", C_GOLD_DIM)
	chap_col.add_child(chap_header)

	chap_col.add_child(_make_rule_rect())

	var chap_scroll := ScrollContainer.new()
	chap_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	chap_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	chap_col.add_child(chap_scroll)

	_chapter_vbox = VBoxContainer.new()
	_chapter_vbox.add_theme_constant_override("separation", 4)
	_chapter_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	chap_scroll.add_child(_chapter_vbox)


func _build_overlays() -> void:
	_save_overlay     = preload("res://scenes/menu/SaveSlotOverlay.tscn").instantiate()
	_settings_overlay = preload("res://scenes/menu/SettingsOverlay.tscn").instantiate()
	_gallery_overlay  = preload("res://scenes/menu/GalleryOverlay.tscn").instantiate()
	_music_overlay    = preload("res://scenes/menu/MusicPlayerOverlay.tscn").instantiate()
	_editor_overlay   = preload("res://scenes/menu/SceneEditorOverlay.tscn").instantiate()
	_unlock_overlay   = preload("res://scenes/menu/UnlockOverlay.tscn").instantiate()

	for ov: Control in [_save_overlay, _settings_overlay, _gallery_overlay,
						_music_overlay, _editor_overlay, _unlock_overlay]:
		ov.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		ov.visible = false
		add_child(ov)

	_editor_overlay.connect("playtest_requested", _on_playtest_requested)


# ── Volume / chapter selection ────────────────────────────────────────────────

func _select_vol(vol: int) -> void:
	_sel_vol = vol
	for v in _vol_buttons:
		_style_vol_btn(_vol_buttons[v] as Button, v == vol, false)
	_populate_chapters(vol)
	# Picking a volume unlocks every track tagged to that vol in
	# the music catalog. They're added to the Music Player's
	# unlocked list and queued so the playlist naturally pulls
	# them in once the current track finishes. The title theme is
	# already unlocked from app-start; opening Volume 1 introduces
	# Volume 1's music, etc.
	if AudioMgr.has_method("unlock_volume"):
		AudioMgr.unlock_volume(vol)


func _populate_chapters(vol: int) -> void:
	for ch in _chapter_vbox.get_children():
		ch.queue_free()

	var chapters := SceneDataDB.get_volume_chapters(vol)
	if chapters.is_empty():
		var lbl := Label.new()
		lbl.text = "No scenes loaded.\nRun tools/import_scenes.py first."
		lbl.add_theme_font_size_override("font_size", 14)
		lbl.add_theme_color_override("font_color", C_DIM)
		lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		_chapter_vbox.add_child(lbl)
		return

	for scene: Dictionary in chapters:
		var ch_raw = scene.get("chapter", "")
		var ch_str: String = str(ch_raw) if ch_raw != null else ""
		var scene_title: String = scene.get("title", "")
		if scene_title == "":
			scene_title = "Chapter %s" % ch_str if ch_str != "" else scene.get("id", "—")
		var scene_type: String = scene.get("type", "")
		var sid: String = scene.get("id", "")

		var btn := Button.new()
		btn.text = ""
		btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		btn.custom_minimum_size.y = 48

		var normal_st := StyleBoxFlat.new()
		normal_st.bg_color     = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.04)
		normal_st.border_color = C_BORDER
		normal_st.set_border_width_all(1)
		normal_st.content_margin_left   = 12.0
		normal_st.content_margin_right  = 12.0
		normal_st.content_margin_top    = 8.0
		normal_st.content_margin_bottom = 8.0
		btn.add_theme_stylebox_override("normal", normal_st)
		var hover_st: StyleBoxFlat = normal_st.duplicate() as StyleBoxFlat
		hover_st.bg_color     = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.10)
		hover_st.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.5)
		btn.add_theme_stylebox_override("hover",   hover_st)
		btn.add_theme_stylebox_override("focus",   hover_st)
		btn.add_theme_stylebox_override("pressed", hover_st)

		# Content row: title (left) + chapter badge (right)
		var row := HBoxContainer.new()
		row.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		row.offset_left  = 12
		row.offset_right = -12
		row.add_theme_constant_override("separation", 8)
		row.mouse_filter = Control.MOUSE_FILTER_IGNORE

		var title_lbl := Label.new()
		title_lbl.text = scene_title
		title_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		title_lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		title_lbl.clip_text = true
		title_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
		if ResourceLoader.exists(SkinDB.F_IMFELL_R):
			title_lbl.add_theme_font_override("font", load(SkinDB.F_IMFELL_R) as Font)
		title_lbl.add_theme_font_size_override("font_size", 15)
		title_lbl.add_theme_color_override("font_color", C_TXT)
		row.add_child(title_lbl)

		# Badge: "Ch N · TYPE" or just "Ch N"
		var badge_parts: Array = []
		if ch_str != "":
			badge_parts.append("Ch %s" % ch_str)
		if scene_type != "" and scene_type != "chapter":
			badge_parts.append(scene_type.to_upper())
		if not badge_parts.is_empty():
			var badge := Label.new()
			badge.text = "  ·  ".join(badge_parts)
			badge.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
			badge.mouse_filter = Control.MOUSE_FILTER_IGNORE
			if ResourceLoader.exists(SkinDB.F_CINZEL):
				badge.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
			badge.add_theme_font_size_override("font_size", 12)
			badge.add_theme_color_override("font_color", Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.45))
			row.add_child(badge)

		btn.add_child(row)
		btn.add_theme_color_override("font_color",       C_TXT)
		btn.add_theme_color_override("font_hover_color", C_GOLD)
		btn.add_theme_color_override("font_focus_color", C_GOLD)

		var v: int    = vol
		var s: String = sid
		btn.pressed.connect(func() -> void: _on_chapter_selected(v, s))
		_chapter_vbox.add_child(btn)


# ── Button handlers ───────────────────────────────────────────────────────────

func _on_new_game() -> void:
	var chapters := SceneDataDB.get_volume_chapters(_sel_vol)
	var scene_id: String = ""
	for scene: Dictionary in chapters:
		if int(scene.get("chapter", -1)) == 1:
			scene_id = scene.get("id", "")
			break
	if scene_id == "" and not chapters.is_empty():
		scene_id = chapters[0].get("id", "")
	if scene_id == "":
		var all := SceneDataDB.get_volume_scenes(_sel_vol)
		if not all.is_empty():
			scene_id = (all[0] as Dictionary).get("id", "")
	if scene_id == "":
		return
	play_requested.emit(_sel_vol, scene_id, 0)


func _on_chapter_selected(vol: int, scene_id: String) -> void:
	play_requested.emit(vol, scene_id, 0)


func _on_continue() -> void:
	_save_overlay.call("open", "continue", func(slot: int, save_data: Dictionary) -> void:
		load_requested.emit(slot)
	)


func _on_settings() -> void:
	_settings_overlay.call("open")


func _on_gallery() -> void:
	_gallery_overlay.call("open")


func _on_music() -> void:
	_music_overlay.call("open")


func _on_achievements() -> void:
	# Build a fresh achievements panel each open — cheap and avoids
	# stale-cache bugs after a run that just unlocked something.
	var existing: Node = get_node_or_null("AchievementsPanel")
	if existing != null and is_instance_valid(existing):
		existing.queue_free()
	var panel := _build_achievements_panel()
	panel.name = "AchievementsPanel"
	add_child(panel)


func _on_profile() -> void:
	# The whole reading in one place — VN slots, gauntlet record,
	# sticks finished, tokens held. Same fresh-build pattern.
	var existing: Node = get_node_or_null("ProfilePanel")
	if existing != null and is_instance_valid(existing):
		existing.queue_free()
	var ProfilePanel := load("res://scenes/menu/ProfilePanel.gd")
	var panel: Control = ProfilePanel.build(self)
	add_child(panel)


func _on_almanac() -> void:
	# The cross-pillar compendium — chapters + threads that light up
	# as you play across VN / gauntlet / CP / slowsticks. Fresh build.
	var existing: Node = get_node_or_null("Almanac")
	if existing != null and is_instance_valid(existing):
		existing.queue_free()
	var Almanac := load("res://scenes/menu/Almanac.gd")
	var panel: Control = Almanac.build(self)
	add_child(panel)


func _on_scrapbook() -> void:
	# Same pattern as achievements — build fresh each open so lore
	# tokens revealed in the last run show up without a menu reload.
	var existing: Node = get_node_or_null("ScrapbookPanel")
	if existing != null and is_instance_valid(existing):
		existing.queue_free()
	var ScrapbookPanel := load("res://scenes/menu/ScrapbookPanel.gd")
	var panel: Control = ScrapbookPanel.build(self)
	add_child(panel)


func _build_achievements_panel() -> Control:
	const PATH := "res://resources/achievements.json"
	var achievements: Array = []
	if FileAccess.file_exists(PATH):
		var f := FileAccess.open(PATH, FileAccess.READ)
		if f != null:
			var parsed = JSON.parse_string(f.get_as_text())
			if parsed is Dictionary:
				achievements = (parsed as Dictionary).get("achievements", [])

	var root := Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_STOP

	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.78)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.add_child(dim)

	var card := Panel.new()
	card.set_anchors_preset(Control.PRESET_CENTER)
	card.offset_left = -360
	card.offset_right = 360
	card.offset_top = -300
	card.offset_bottom = 300
	var st := StyleBoxFlat.new()
	st.bg_color = Color(0.024, 0.020, 0.014, 0.97)
	st.border_color = Color(0.70, 0.55, 0.24, 0.45)
	st.set_border_width_all(1)
	card.add_theme_stylebox_override("panel", st)
	root.add_child(card)

	var vb := VBoxContainer.new()
	vb.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	vb.offset_left = 24
	vb.offset_right = -24
	vb.offset_top = 18
	vb.offset_bottom = -18
	vb.add_theme_constant_override("separation", 8)
	card.add_child(vb)

	# Header
	var hdr := HBoxContainer.new()
	vb.add_child(hdr)
	var ttl := Label.new()
	var earned: int = 0
	for a in achievements:
		if SaveSystem.is_unlocked(String((a as Dictionary).get("unlock_key", ""))):
			earned += 1
	ttl.text = "ACHIEVEMENTS · %d / %d" % [earned, achievements.size()]
	ttl.add_theme_font_size_override("font_size", 13)
	ttl.add_theme_color_override("font_color", Color(0.92, 0.78, 0.40))
	ttl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hdr.add_child(ttl)
	var close_btn := Button.new()
	close_btn.text = "✕"
	close_btn.custom_minimum_size = Vector2(28, 28)
	close_btn.pressed.connect(func() -> void: root.queue_free())
	hdr.add_child(close_btn)

	var rule := ColorRect.new()
	rule.color = Color(0.70, 0.55, 0.24, 0.25)
	rule.custom_minimum_size.y = 1
	vb.add_child(rule)

	# Scroll list
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vb.add_child(scroll)
	var list := VBoxContainer.new()
	list.add_theme_constant_override("separation", 4)
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(list)

	for a_v in achievements:
		var a: Dictionary = a_v
		var unlocked: bool = SaveSystem.is_unlocked(String(a.get("unlock_key", "")))
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 8)
		list.add_child(row)
		var dot := Label.new()
		dot.text = "●" if unlocked else "○"
		dot.add_theme_font_size_override("font_size", 14)
		dot.add_theme_color_override("font_color",
			Color(0.92, 0.78, 0.40) if unlocked else Color(0.45, 0.43, 0.36, 0.6))
		dot.custom_minimum_size.x = 18
		row.add_child(dot)
		var meta := VBoxContainer.new()
		meta.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(meta)
		var name_lbl := Label.new()
		name_lbl.text = String(a.get("title", a.get("id", "?")))
		name_lbl.add_theme_font_size_override("font_size", 12)
		name_lbl.add_theme_color_override("font_color",
			Color(0.83, 0.79, 0.69) if unlocked else Color(0.45, 0.43, 0.36, 0.85))
		meta.add_child(name_lbl)
		var desc_lbl := Label.new()
		desc_lbl.text = String(a.get("desc", ""))
		desc_lbl.add_theme_font_size_override("font_size", 12)
		desc_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		desc_lbl.custom_minimum_size = Vector2(620, 0)
		desc_lbl.add_theme_color_override("font_color",
			Color(0.65, 0.62, 0.55) if unlocked else Color(0.40, 0.38, 0.33, 0.75))
		meta.add_child(desc_lbl)
	return root


func _on_editor() -> void:
	_editor_overlay.call("open")


# Slowstock Library · opens the cabin shelf (Vol 7's Estuary 3 +
# the ten authored cartridge spines) as a full-screen overlay.
# Uses SlowstockBoot's flow directly · shelf → pick → host → back.
# When the boot flow's overlay closes (via BACK-TO-SHELF or the
# host's `finished` signal), we free it and land back on the
# main menu.
var _slowstock_root: Node = null

func _on_slowstock_library() -> void:
	if _slowstock_root != null and is_instance_valid(_slowstock_root):
		return   # already open
	_slowstock_root = load("res://scenes/games/estuary_3/SlowstockBoot.tscn").instantiate()
	# Full-screen OPAQUE container styled as the cabin's console TV —
	# a diegetic physical prop (Olaf's set, 2048), not a filter. The
	# menu can no longer bleed through, and every slowstick plays
	# inside the television it canonically plays on.
	# InputBlocker: a modal fence — swallows whatever the slowstick
	# UI doesn't consume, releases menu focus, and flags itself so
	# _input-level handlers (the VN's advance key) stand down.
	# Without it, keys leak through and navigate the menu and the
	# visual novel underneath the TV.
	var wrap: Control = preload("res://scripts/InputBlocker.gd").new()
	wrap.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	wrap.mouse_filter = Control.MOUSE_FILTER_STOP
	wrap.add_to_group("ui")   # F4 sweep catches this
	# The dark room behind the set.
	var room := ColorRect.new()
	room.color = Color(0.014, 0.011, 0.009, 1.0)
	room.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	room.mouse_filter = Control.MOUSE_FILTER_IGNORE
	wrap.add_child(room)
	# The set's plastic shell.
	var bezel := Panel.new()
	bezel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bezel.offset_left = 10
	bezel.offset_top = 8
	bezel.offset_right = -10
	bezel.offset_bottom = -8
	bezel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var bsb := StyleBoxFlat.new()
	bsb.bg_color = Color(0.095, 0.085, 0.080, 1.0)
	bsb.border_color = Color(0.030, 0.026, 0.024, 1.0)
	bsb.set_border_width_all(3)
	bsb.set_corner_radius_all(16)
	bezel.add_theme_stylebox_override("panel", bsb)
	wrap.add_child(bezel)
	# The screen — inset glass the whole library flow lives inside.
	var screen := Panel.new()
	screen.name = "TvScreen"
	screen.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	screen.offset_left = 30
	screen.offset_top = 26
	screen.offset_right = -30
	screen.offset_bottom = -46
	screen.clip_contents = true
	var ssb := StyleBoxFlat.new()
	ssb.bg_color = Color(0.008, 0.009, 0.012, 1.0)
	ssb.border_color = Color(0.020, 0.018, 0.016, 1.0)
	ssb.set_border_width_all(2)
	ssb.set_corner_radius_all(8)
	screen.add_theme_stylebox_override("panel", ssb)
	wrap.add_child(screen)
	screen.add_child(_slowstock_root)
	# Chin plate: brand + power LED.
	var brand := Label.new()
	brand.text = "S L O W S T O C K"
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		brand.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	brand.add_theme_font_size_override("font_size", 12)
	brand.add_theme_color_override("font_color", Color(0.44, 0.40, 0.34, 1.0))
	brand.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	brand.offset_top = -34
	brand.offset_bottom = -14
	brand.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	brand.mouse_filter = Control.MOUSE_FILTER_IGNORE
	wrap.add_child(brand)
	var led := ColorRect.new()
	led.color = Color(0.35, 0.85, 0.45, 0.9)
	led.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	led.offset_left = -52
	led.offset_right = -44
	led.offset_top = -28
	led.offset_bottom = -20
	led.mouse_filter = Control.MOUSE_FILTER_IGNORE
	wrap.add_child(led)
	add_child(wrap)
	# ESC on the shelf's dim-click / closed signal frees the wrap.
	# We poll for it by listening on the SlowstockBoot's tree exit.
	_slowstock_root.tree_exited.connect(func() -> void:
		if is_instance_valid(wrap): wrap.queue_free()
		_slowstock_root = null)
	# Also allow the wrap to intercept ESC as a global close.
	wrap.gui_input.connect(func(ev: InputEvent) -> void:
		if ev is InputEventKey and ev.pressed and (ev as InputEventKey).keycode == KEY_ESCAPE:
			if _slowstock_root != null and is_instance_valid(_slowstock_root):
				_slowstock_root.queue_free())


func _play_title_music() -> void:
	const SRC := "assets/audio/bgm/title_theme.ogg"
	AudioMgr.request_scene_bgm(SRC)
	var is_new := SaveSystem.mark_unlocked("music:title_theme")
	if is_new:
		_unlock_overlay.call("show_unlock", {
			"type": "Music Track",
			"title": "Modern Mythology",
			"desc":  "The theme that plays at the beginning of everything."
		})


func _on_playtest_requested(scene_id: String, node_idx: int) -> void:
	var scene_data := SceneDataDB.get_scene(scene_id)
	var vol: int = int(scene_data.get("vol", _sel_vol))
	play_requested.emit(vol, scene_id, node_idx)


# ── Helpers ───────────────────────────────────────────────────────────────────

func _nav_btn(text: String) -> Button:
	var btn := Button.new()
	btn.text = text
	btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
	btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	btn.custom_minimum_size.y = 44
	var st := StyleBoxFlat.new()
	st.bg_color     = Color(0, 0, 0, 0)
	st.border_color = Color(0, 0, 0, 0)
	st.set_border_width_all(0)
	st.content_margin_left = 0.0
	st.content_margin_right = 0.0
	btn.add_theme_stylebox_override("normal", st)
	var hover_st: StyleBoxFlat = st.duplicate() as StyleBoxFlat
	hover_st.bg_color     = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.06)
	hover_st.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.25)
	hover_st.set_border_width_all(1)
	hover_st.content_margin_left = 4.0
	btn.add_theme_stylebox_override("hover",   hover_st)
	btn.add_theme_stylebox_override("focus",   hover_st)
	btn.add_theme_stylebox_override("pressed", hover_st)
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		btn.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	btn.add_theme_font_size_override("font_size", 16)
	btn.add_theme_color_override("font_color",        C_TXT)
	btn.add_theme_color_override("font_hover_color",  C_GOLD)
	btn.add_theme_color_override("font_focus_color",  C_GOLD)
	btn.add_theme_color_override("font_pressed_color", C_GOLD)
	return btn


func _nav_btn_small(text: String) -> Button:
	var btn := _nav_btn(text)
	btn.custom_minimum_size.y = 34
	btn.add_theme_font_size_override("font_size", 13)
	btn.add_theme_color_override("font_color", C_DIM)
	return btn


func _style_vol_btn(btn: Button, selected: bool, locked: bool) -> void:
	var st := StyleBoxFlat.new()
	st.bg_color     = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.08) if selected else Color(0, 0, 0, 0)
	st.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.4)  if selected else Color(0, 0, 0, 0)
	st.set_border_width_all(1 if selected else 0)
	st.content_margin_left   = 10.0
	st.content_margin_right  = 10.0
	st.content_margin_top    = 6.0
	st.content_margin_bottom = 6.0
	btn.add_theme_stylebox_override("normal", st)
	var hover_st: StyleBoxFlat = st.duplicate() as StyleBoxFlat
	hover_st.bg_color     = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.10)
	hover_st.border_color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.5)
	hover_st.set_border_width_all(1)
	btn.add_theme_stylebox_override("hover",   hover_st)
	btn.add_theme_stylebox_override("focus",   hover_st)
	btn.add_theme_stylebox_override("pressed", hover_st)
	if ResourceLoader.exists(SkinDB.F_CINZEL):
		btn.add_theme_font_override("font", load(SkinDB.F_CINZEL) as Font)
	btn.add_theme_font_size_override("font_size", 14)
	btn.add_theme_color_override("font_color",
		C_GOLD if selected else (C_LOCKED if locked else C_TXT))
	btn.add_theme_color_override("font_hover_color",  C_GOLD)
	btn.add_theme_color_override("font_focus_color",  C_GOLD)


func _make_rule_rect() -> ColorRect:
	var r := ColorRect.new()
	r.color = C_BORDER
	r.custom_minimum_size.y = 1
	return r


# ── Procedural frontispiece backdrop ─────────────────────────────

func _hash01_menu(x: int, y: int) -> float:
	var n: int = x * 374761393 + y * 668265263
	n = (n ^ (n >> 13)) * 1274126177
	n = n ^ (n >> 16)
	return float(n & 0xFFFF) / 65536.0


func _make_backdrop_tex() -> ImageTexture:
	# Half-res canvas, scaled to the viewport by the TextureRect.
	# ~230k pixels once at boot; deterministic, no RNG.
	var w := 640
	var h := 360
	var img := Image.create(w, h, false, Image.FORMAT_RGBA8)
	for y in range(h):
		for x in range(w):
			# Lamplight: soft radial falloff from behind the title.
			var dx: float = (float(x) - 150.0) / 460.0
			var dy: float = (float(y) - 80.0) / 330.0
			var glow: float = clampf(1.0 - sqrt(dx * dx + dy * dy), 0.0, 1.0)
			var c := Color(
				C_BG.r + glow * 0.034,
				C_BG.g + glow * 0.024,
				C_BG.b + glow * 0.010, 1.0)
			# Paper tooth — sparse up-flecks and down-flecks.
			var g: float = _hash01_menu(x, y)
			if g > 0.94:
				c = Color(c.r + 0.014, c.g + 0.012, c.b + 0.008, 1.0)
			elif g < 0.05:
				c = Color(maxf(0.0, c.r - 0.010), maxf(0.0, c.g - 0.009),
					maxf(0.0, c.b - 0.006), 1.0)
			img.set_pixel(x, y, c)
	# Compass ring watermark behind the volumes panel — a book
	# plate, barely there.
	var cx := 470
	var cy := 195
	for ri in [132, 126]:
		var r_f: float = float(ri)
		for i in range(1080):
			var ang: float = float(i) * TAU / 1080.0
			var px: int = cx + int(cos(ang) * r_f)
			var py: int = cy + int(sin(ang) * r_f)
			if px >= 0 and px < w and py >= 0 and py < h:
				img.set_pixel(px, py, img.get_pixel(px, py).lerp(C_GOLD, 0.055))
	# Eight radial ticks.
	for t in range(8):
		var ang2: float = float(t) * TAU / 8.0
		for rr in range(112, 122):
			var px2: int = cx + int(cos(ang2) * float(rr))
			var py2: int = cy + int(sin(ang2) * float(rr))
			if px2 >= 0 and px2 < w and py2 >= 0 and py2 < h:
				img.set_pixel(px2, py2, img.get_pixel(px2, py2).lerp(C_GOLD, 0.07))
	# Small diamond at the ring's heart.
	for yy in range(cy - 6, cy + 7):
		for xx in range(cx - 6, cx + 7):
			if absi(xx - cx) + absi(yy - cy) <= 6 and xx >= 0 and xx < w and yy >= 0 and yy < h:
				img.set_pixel(xx, yy, img.get_pixel(xx, yy).lerp(C_GOLD, 0.05))
	return ImageTexture.create_from_image(img)
