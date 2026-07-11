extends Control
## NORTHWIND HARBOR · run controller · Oneironautics Inc., 1988.
##
## The studio's first stick · the founding text of "slow."  Seven
## consecutive mornings, 5:47 to the horns.  The manual's last
## line: "a game you cannot be good at, only present for."
##
## This cart is the Camp Sweetgum cart · Olaf bought the console
## lot at auction in 2011.  Sam's 1988 save of Chapter One is
## still on it, mid-pocket, holding the glove.  It is displayed on
## the title screen and never overwritten.
##
## Save file: user://northwind_harbor.save.json  (slot 2 · yours)
##
## Signals · uniform slowstock host contract:
##   quit_to_shelf · finished(canon_vars, lore_tokens)
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/northwind_harbor/manifest.json"
const CHAP_PATH     := "res://resources/games/vol7/northwind_harbor/chapters.json"
const SAVE_PATH     := "user://northwind_harbor.save.json"
const MORNING_SCENE := "res://scenes/games/northwind_harbor/NorthwindMorning.tscn"
const HERO_DIR      := "res://resources/games/vol7/northwind_harbor/hero_images/"

const C_DARK := Color("16202e")
const C_FOG  := Color("7a8894")
const C_PILE := Color("4a5a52")
const C_WOOD := Color("30281e")
const C_LAMP := Color("d88a30")
const C_GULL := Color("c8ccd4")

var _manifest: Dictionary = {}
var _chapters: Array = []
var _run_state: Dictionary = {}
var _title_root: Node = null
var _card_root: Node = null
var _child_scene: Node = null
var _ending_root: Node = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	SlowstickLook.apply(self, "oneironautics")
	# Studio control chrome (mirrors the look preset) — cascades
	# to every child scene; see StickTheme.gd.
	theme = preload("res://scenes/games/StickTheme.gd").make("oneironautics")
	_run_state = _fresh_state([])
	_load_manifest()
	_load_save_if_present()
	_build_title_screen()


func _fresh_state(weeks_walked: Array) -> Dictionary:
	return {
		"chapter_n":  1,
		"steps_done": [],
		"pockets":    [],
		"heard":      [],
		"poster_seen": false,
		"weeks_walked": weeks_walked,
		"canon_vars": {},
		"lore_tokens_pending": []
	}


func _load_manifest() -> void:
	if not FileAccess.file_exists(MANIFEST_PATH): return
	var f := FileAccess.open(MANIFEST_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_manifest = parsed
	var f2 := FileAccess.open(CHAP_PATH, FileAccess.READ)
	if f2 != null:
		var p2: Variant = JSON.parse_string(f2.get_as_text())
		f2.close()
		if p2 is Dictionary:
			_chapters = (p2 as Dictionary).get("chapters", [])


func _load_save_if_present() -> void:
	if not FileAccess.file_exists(SAVE_PATH): return
	var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		var saved: Dictionary = parsed
		for k in saved.keys():
			_run_state[String(k)] = saved[k]


func _save_state() -> void:
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f == null: return
	f.store_string(JSON.stringify(_run_state, "  "))
	f.close()


func start_new_run(_manager_mode: bool = false) -> void:
	var weeks: Array = _run_state.get("weeks_walked", [])
	_run_state = _fresh_state(weeks)
	_show_chapter_card(1)


func _clear_current_scene() -> void:
	for n in [_title_root, _card_root, _child_scene, _ending_root]:
		if n != null and is_instance_valid(n):
			n.queue_free()
	_title_root = null
	_card_root = null
	_child_scene = null
	_ending_root = null


func _play_bgm(path: String) -> void:
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("play_bgm"):
		am.play_bgm(path)


# ─── Title · the harbor from the breakwater · Sam's save ─────────

func _build_title_screen() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/nh/title_pad.wav")

	_title_root = Control.new()
	_title_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_title_root)

	var bg := ColorRect.new()
	bg.color = C_DARK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.add_child(bg)

	var hero := HeroImage.new()
	if hero.load_from(HERO_DIR + "title_breakwater.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(960, 540))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -480
		tex_rect.offset_right = 480
		tex_rect.offset_top = -330
		tex_rect.offset_bottom = 210
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_title_root.add_child(tex_rect)

	# Title motion — studio character (menu motion playbook).
	preload("res://scenes/games/TitleMotion.gd").attach(_title_root, "oneironautics")

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -340
	v.offset_right = 340
	v.offset_top = -40
	v.offset_bottom = 320
	v.add_theme_constant_override("separation", 10)
	_title_root.add_child(v)

	var shelf: Dictionary = _manifest.get("shelf", {})

	var title := Label.new()
	title.text = String(shelf.get("label_title", "NORTHWIND HARBOR"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 40)
	title.add_theme_color_override("font_color", C_GULL)
	v.add_child(title)

	var subtitle := Label.new()
	subtitle.text = String(shelf.get("label_subtitle", "seven mornings · a boy, a dog, a harbor"))
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 14)
	subtitle.add_theme_color_override("font_color", C_FOG)
	v.add_child(subtitle)

	# Sam's 1988 save · the artifact · never overwritten
	var sam := Label.new()
	sam.text = "SAVE 1 · SAM · 1988 · MORNING ONE · mid-pocket, holding the glove   [do not overwrite]"
	sam.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sam.add_theme_font_size_override("font_size", 12)
	sam.add_theme_color_override("font_color", C_LAMP)
	v.add_child(sam)

	var sep := Control.new()
	sep.custom_minimum_size = Vector2(0, 10)
	v.add_child(sep)

	var new_btn := Button.new()
	new_btn.text = "  SAVE 2 · WALK THE WEEK  "
	new_btn.add_theme_font_size_override("font_size", 14)
	new_btn.pressed.connect(func() -> void: start_new_run(false))
	v.add_child(new_btn)

	if _has_save():
		var cont_btn := Button.new()
		cont_btn.text = "  CONTINUE · MORNING " + str(int(_run_state.get("chapter_n", 1))) + "  "
		cont_btn.add_theme_font_size_override("font_size", 14)
		cont_btn.pressed.connect(func() -> void: _show_chapter_card(int(_run_state.get("chapter_n", 1))))
		v.add_child(cont_btn)

	var back_btn := Button.new()
	back_btn.text = "  ← back to shelf  "
	back_btn.add_theme_font_size_override("font_size", 13)
	back_btn.pressed.connect(_on_back_to_shelf)
	v.add_child(back_btn)

	var motto := Label.new()
	motto.text = "'a game you cannot be good at, only present for.'"
	motto.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	motto.add_theme_font_size_override("font_size", 12)
	motto.add_theme_color_override("font_color", C_PILE)
	v.add_child(motto)

	var weeks: Array = _run_state.get("weeks_walked", [])
	if weeks.size() > 0:
		var status := Label.new()
		status.text = "· weeks walked: %d ·" % weeks.size()
		status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		status.add_theme_font_size_override("font_size", 12)
		status.add_theme_color_override("font_color", C_PILE)
		v.add_child(status)


func _has_save() -> bool:
	return FileAccess.file_exists(SAVE_PATH) and int(_run_state.get("chapter_n", 1)) > 1 \
			and int(_run_state.get("chapter_n", 1)) <= 7


func _on_back_to_shelf() -> void:
	quit_to_shelf.emit()


# ─── Chapter cards · the concertina's only stage ─────────────────

func _show_chapter_card(n: int) -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/nh/concertina_cards.wav")

	_card_root = Control.new()
	_card_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_card_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_card_root)

	var bg := ColorRect.new()
	bg.color = C_DARK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_card_root.add_child(bg)

	var ch: Dictionary = _chapters[n - 1] if n - 1 < _chapters.size() else {}

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -360
	v.offset_right = 360
	v.offset_top = -110
	v.offset_bottom = 110
	v.add_theme_constant_override("separation", 18)
	_card_root.add_child(v)

	var title := Label.new()
	title.text = String(ch.get("title", "MORNING %d" % n))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 26)
	title.add_theme_color_override("font_color", C_GULL)
	v.add_child(title)

	var card := Label.new()
	card.text = String(ch.get("card", ""))
	card.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	card.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	card.add_theme_font_size_override("font_size", 15)
	card.add_theme_color_override("font_color", C_FOG)
	v.add_child(card)

	var begin := Button.new()
	begin.text = "  · 5:47 ·  "
	begin.add_theme_font_size_override("font_size", 14)
	begin.pressed.connect(_open_morning)
	v.add_child(begin)


func _open_morning() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/nh/harbor_quiet.wav")
	_child_scene = load(MORNING_SCENE).instantiate()
	_child_scene.quit.connect(_on_morning_quit)
	_child_scene.morning_over.connect(_on_morning_over)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_morning_quit() -> void:
	_save_state()
	_build_title_screen()


func _on_morning_over(state: Dictionary) -> void:
	_run_state = state
	var n: int = int(_run_state.get("chapter_n", 1))
	if n >= 7:
		_save_state()
		_show_ending()
		return
	_run_state["chapter_n"] = n + 1
	_save_state()
	_show_chapter_card(n + 1)


# ─── The end of the week ─────────────────────────────────────────

func _chains_closed() -> int:
	var closed := 0
	for ch in _chapters:
		if int(ch.get("n", 1)) >= 7:
			continue
		var all_done := true
		for step in ch.get("steps", []):
			var s: Dictionary = step
			if bool(s.get("optional", false)):
				continue
			if not (_run_state.get("steps_done", []) as Array).has(String(s["id"])):
				all_done = false
				break
		if all_done:
			closed += 1
	return closed


func _show_ending() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/nh/title_pad.wav")

	_ending_root = Control.new()
	_ending_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_ending_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_ending_root)

	var bg := ColorRect.new()
	bg.color = C_DARK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_ending_root.add_child(bg)

	var hero := HeroImage.new()
	if hero.load_from(HERO_DIR + "clara_b_going_out.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(960, 540))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -480
		tex_rect.offset_right = 480
		tex_rect.offset_top = -320
		tex_rect.offset_bottom = 220
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_ending_root.add_child(tex_rect)

	var closed := _chains_closed()
	var good_week := closed >= 6

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -340
	v.offset_right = 340
	v.offset_top = 120
	v.offset_bottom = 330
	v.add_theme_constant_override("separation", 12)
	_ending_root.add_child(v)

	var line := Label.new()
	line.text = "seven mornings. the town is the same town. you are slightly otherwise."
	line.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	line.add_theme_font_size_override("font_size", 15)
	line.add_theme_color_override("font_color", C_GULL)
	v.add_child(line)

	var tally := Label.new()
	tally.text = ("THE GOOD WEEK · every chain closed" if good_week
			else "chains closed · %d of 6 · the town remembers the rest kindly" % closed)
	tally.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	tally.add_theme_font_size_override("font_size", 13)
	tally.add_theme_color_override("font_color", C_LAMP if good_week else C_FOG)
	v.add_child(tally)

	var done := Button.new()
	done.text = "  · hang up the coat ·  "
	done.add_theme_font_size_override("font_size", 14)
	done.pressed.connect(func() -> void: _finish_run(good_week))
	v.add_child(done)


func _finish_run(good_week: bool) -> void:
	var tokens: Array = _run_state.get("lore_tokens_pending", [])
	for t in ["northwind_harbor_finished", "nh_poster_seen"]:
		if not tokens.has(t):
			tokens.append(t)
	if good_week and not tokens.has("nh_good_week"):
		tokens.append("nh_good_week")
	_run_state["lore_tokens_pending"] = tokens
	OneironauticsTokens.add_many(tokens)
	var canon: Dictionary = _run_state.get("canon_vars", {})
	canon["northwind_harbor_good_week"] = good_week
	_run_state["canon_vars"] = canon
	var weeks: Array = _run_state.get("weeks_walked", [])
	weeks.append("good" if good_week else "walked")
	_run_state["weeks_walked"] = weeks
	_run_state["chapter_n"] = 1
	_save_state()
	finished.emit(canon, tokens)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			if _title_root != null and _child_scene == null:
				_on_back_to_shelf()
				get_viewport().set_input_as_handled()
