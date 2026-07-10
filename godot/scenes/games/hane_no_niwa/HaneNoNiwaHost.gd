extends Control
## HANE NO NIWA (羽の庭) · run controller · Yumemi Denshi, 1993.
##
## Four seasons × nine visits.  One letter per season, left on
## the shelf at the season's last visit · composed from a grammar
## over the player's own offering-lexicon: since real
## understanding can't be checked, the game builds meaning out of
## exactly what you gave it.
##
## The fourth letter contains, regardless of lexicon, one
## sentence in English, uncommented, with the doubled r.
##
## Save file: user://hane_no_niwa.save.json
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/hane_no_niwa/manifest.json"
const LETTERS_PATH  := "res://resources/games/vol7/hane_no_niwa/letters.json"
const SAVE_PATH     := "user://hane_no_niwa.save.json"
const VISIT_SCENE   := "res://scenes/games/hane_no_niwa/ShrineVisit.tscn"
const HERO_DIR      := "res://resources/games/vol7/hane_no_niwa/hero_images/"

const SEASONS := ["spring", "summer", "autumn", "winter"]
const FEATHER_COLORS := ["black", "grey", "white", "gold"]
const C_PAPER := Color("f4ece0")
const C_INK   := Color("38302a")
const C_BLOSSOM := Color("d88a98")

var _manifest: Dictionary = {}
var _letters: Dictionary = {}
var _run_state: Dictionary = {}
var _title_root: Node = null
var _child_scene: Node = null
var _letter_root: Node = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	SlowstickLook.apply(self, "yumemi")
	_run_state = _fresh_state(false, [])
	_load_data()
	_load_save_if_present()
	_build_title_screen()


func _fresh_state(ng_plus: bool, letters_kept: Array) -> Dictionary:
	return {
		"visit_total":  0,
		"swept":        0,
		"mended":       5,
		"satchel":      [],
		"lexicon":      [],
		"lexicon_items": [],
		"lexicon_prev": [],
		"season_offered": [],
		"feathers":     0,
		"ng_plus":      ng_plus,
		"letters_kept": letters_kept,
		"canon_vars":   {},
		"lore_tokens_pending": []
	}


func _load_data() -> void:
	for pair in [[MANIFEST_PATH, "m"], [LETTERS_PATH, "l"]]:
		if not FileAccess.file_exists(String(pair[0])): continue
		var f := FileAccess.open(String(pair[0]), FileAccess.READ)
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			if String(pair[1]) == "m": _manifest = parsed
			else: _letters = parsed


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
	_run_state = _fresh_state(bool(_run_state.get("ng_plus", false)),
			_run_state.get("letters_kept", []))
	_open_visit()


func _clear_current_scene() -> void:
	for n in [_title_root, _child_scene, _letter_root]:
		if n != null and is_instance_valid(n):
			n.queue_free()
	_title_root = null
	_child_scene = null
	_letter_root = null


func _play_bgm(path: String) -> void:
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("play_bgm"):
		am.play_bgm(path)


# ─── Title ───────────────────────────────────────────────────────

func _build_title_screen() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/hnn/spring.wav")

	_title_root = Control.new()
	_title_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_title_root)

	var bg := ColorRect.new()
	bg.color = C_PAPER
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.add_child(bg)

	var hero := HeroImage.new()
	if hero.load_from(HERO_DIR + "shrine_spring.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(800, 450))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -400
		tex_rect.offset_right = 400
		tex_rect.offset_top = -310
		tex_rect.offset_bottom = 140
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_title_root.add_child(tex_rect)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -340
	v.offset_right = 340
	v.offset_top = 130
	v.offset_bottom = 350
	v.add_theme_constant_override("separation", 10)
	_title_root.add_child(v)

	var title := Label.new()
	title.text = "羽の庭 · HANE NO NIWA"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 32)
	title.add_theme_color_override("font_color", C_INK)
	v.add_child(title)

	var subtitle := Label.new()
	subtitle.text = "the feather garden · Yumemi Denshi · 1993 · (grey import · fan translation included)"
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 13)
	subtitle.add_theme_color_override("font_color", C_INK)
	v.add_child(subtitle)

	var new_btn := Button.new()
	new_btn.text = "  CLIMB THE HILL  " if not bool(_run_state.get("ng_plus", false)) else "  CLIMB AGAIN · (the door is one pixel wider)  "
	new_btn.add_theme_font_size_override("font_size", 14)
	new_btn.pressed.connect(func() -> void: start_new_run(false))
	v.add_child(new_btn)

	if _has_save():
		var total: int = int(_run_state.get("visit_total", 0))
		var cont_btn := Button.new()
		cont_btn.text = "  CONTINUE · %s, VISIT %d  " % [SEASONS[total / 9].to_upper(), (total % 9) + 1]
		cont_btn.add_theme_font_size_override("font_size", 14)
		cont_btn.pressed.connect(_open_visit)
		v.add_child(cont_btn)

	var back_btn := Button.new()
	back_btn.text = "  ← back to shelf  "
	back_btn.add_theme_font_size_override("font_size", 13)
	back_btn.pressed.connect(_on_back_to_shelf)
	v.add_child(back_btn)

	var kept: Array = _run_state.get("letters_kept", [])
	if kept.size() > 0:
		var status := Label.new()
		status.text = "· letters kept: %d ·" % kept.size()
		status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		status.add_theme_font_size_override("font_size", 12)
		status.add_theme_color_override("font_color", C_INK)
		v.add_child(status)


func _has_save() -> bool:
	var t: int = int(_run_state.get("visit_total", 0))
	return FileAccess.file_exists(SAVE_PATH) and t > 0 and t < 36


func _on_back_to_shelf() -> void:
	quit_to_shelf.emit()


# ─── Visits ──────────────────────────────────────────────────────

func _open_visit() -> void:
	_clear_current_scene()
	_child_scene = load(VISIT_SCENE).instantiate()
	_child_scene.quit.connect(_on_visit_quit)
	_child_scene.visit_over.connect(_on_visit_over)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_visit_quit() -> void:
	_save_state()
	_build_title_screen()


func _on_visit_over(state: Dictionary) -> void:
	_run_state = state
	var total: int = int(_run_state.get("visit_total", 0))
	if total % 9 == 0:
		# The season's last visit · a letter waits on the shelf.
		_show_letter(total / 9)   # 1..4
		return
	_save_state()
	_open_visit()


# ─── The letters ─────────────────────────────────────────────────

func _compose_letter(season_n: int) -> Dictionary:
	# season_n · 1..4.  Returns {title, lines: [..], blank: bool}
	var season := SEASONS[season_n - 1]
	var lexicon: Array = _run_state.get("lexicon", [])
	var prev: Array = _run_state.get("lexicon_prev", [])
	var new_tags: Array = []
	for t in lexicon:
		if not prev.has(t):
			new_tags.append(String(t))
	_run_state["lexicon_prev"] = lexicon.duplicate()

	var lines: Array = []
	lines.append(String(_letters.get("openings", {}).get(season, "")))
	var offered_this_season: bool = (_run_state.get("season_offered", []) as Array).has(season)
	if not offered_this_season and season_n < 4:
		lines.append(String(_letters.get("empty_season", "")))
	else:
		var count := 0
		for clause_v in _letters.get("clauses", []):
			var clause: Dictionary = clause_v
			if new_tags.has(String(clause.get("tag", ""))) and count < 5:
				lines.append(String(clause.get("text", "")))
				count += 1
		if count == 0 and season_n < 4:
			lines.append("nothing new was given this season. the old gifts are re-read instead. they hold up.")
	var upkeep := (int(_run_state.get("swept", 0)) + int(_run_state.get("mended", 5))) / 2
	lines.append(String(_letters.get("upkeep_high" if upkeep >= 5 else "upkeep_low", "")))
	# summer · the roses across the sea
	if season == "summer" and OneironauticsTokens.has("fey_faire_titania_blessing_keepsake"):
		lines.append(String(_letters.get("titania_clause", "")))

	if season_n < 4:
		return {"title": "THE %s LETTER" % season.to_upper(), "lines": lines, "blank": false}

	# ── the fourth letter ──
	var ending := _determine_ending()
	if ending == "true":
		return {"title": String(_letters.get("endings", {}).get("true", {}).get("title", "")),
			"lines": [String(_letters.get("endings", {}).get("true", {}).get("text", "")),
				String(_letters.get("carrnival_sentence", ""))],
			"blank": true}
	var e: Dictionary = _letters.get("endings", {}).get(ending, {})
	lines.append(String(e.get("text", "")))
	lines.append(String(_letters.get("carrnival_sentence", "")))
	return {"title": String(e.get("title", "")), "lines": lines, "blank": false}


func _determine_ending() -> String:
	var lexicon: Array = _run_state.get("lexicon", [])
	var upkeep := (int(_run_state.get("swept", 0)) + int(_run_state.get("mended", 5))) / 2
	if lexicon.size() >= 6 and upkeep >= 6 and int(_run_state.get("feathers", 0)) >= 3:
		return "true"
	var belongings := 0
	var comfort := 0
	var weather := 0
	for t in lexicon:
		var s := String(t)
		if s in ["belonging", "grief", "grandfather", "words"]: belongings += 1
		elif s in ["food", "comfort", "sweetness", "warmth"]: comfort += 1
		elif s in ["weather", "rain", "spring", "summer", "autumn", "winter", "leaving"]: weather += 1
	if belongings >= comfort and belongings >= weather and belongings > 0:
		return "grief"
	if comfort >= weather and comfort > 0:
		return "comfort"
	return "weather"


func _show_letter(season_n: int) -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/hnn/one_melody.wav" if season_n == 4
			else "res://assets/audio/bgm/hnn/%s.wav" % SEASONS[season_n - 1])

	var letter := _compose_letter(season_n)
	_run_state["feathers"] = mini(4, int(_run_state.get("feathers", 0)) + 1)
	var kept: Array = _run_state.get("letters_kept", [])
	kept.append(String(letter.get("title", "")))
	_run_state["letters_kept"] = kept

	_letter_root = Control.new()
	_letter_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_letter_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_letter_root)

	var bg := ColorRect.new()
	bg.color = C_PAPER
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_letter_root.add_child(bg)

	# the letter · a narrow column, read down the page
	var col := VBoxContainer.new()
	col.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	col.offset_left = -280
	col.offset_right = 280
	col.offset_top = -300
	col.offset_bottom = 300
	col.add_theme_constant_override("separation", 16)
	_letter_root.add_child(col)

	var hdr := Label.new()
	var feather_color := FEATHER_COLORS[clampi(season_n - 1, 0, 3)]
	hdr.text = "· a letter on the shelf · under a %s feather ·" % feather_color
	hdr.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hdr.add_theme_font_size_override("font_size", 14)
	hdr.add_theme_color_override("font_color", C_BLOSSOM)
	col.add_child(hdr)

	if bool(letter.get("blank", false)):
		var blank := Label.new()
		blank.text = "\n\n( the page is blank )\n\n"
		blank.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		blank.add_theme_font_size_override("font_size", 15)
		blank.add_theme_color_override("font_color", C_INK)
		col.add_child(blank)
	for line in letter.get("lines", []):
		var l := Label.new()
		l.text = String(line)
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		l.add_theme_font_size_override("font_size", 15)
		l.add_theme_color_override("font_color", C_INK)
		col.add_child(l)

	var title := Label.new()
	title.text = "— %s —" % String(letter.get("title", ""))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 13)
	title.add_theme_color_override("font_color", C_BLOSSOM)
	col.add_child(title)

	var go := Button.new()
	go.text = "  · fold it carefully ·  "
	go.add_theme_font_size_override("font_size", 14)
	if season_n < 4:
		go.pressed.connect(func() -> void:
			_save_state()
			_open_visit())
	else:
		go.pressed.connect(func() -> void: _finish_run(letter))
	col.add_child(go)


func _finish_run(letter: Dictionary) -> void:
	var tokens: Array = _run_state.get("lore_tokens_pending", [])
	if not tokens.has("hane_no_niwa_finished"):
		tokens.append("hane_no_niwa_finished")
	if bool(letter.get("blank", false)) and not tokens.has("hnn_gold_feather"):
		tokens.append("hnn_gold_feather")
	_run_state["lore_tokens_pending"] = tokens
	OneironauticsTokens.add_many(tokens)
	var canon: Dictionary = _run_state.get("canon_vars", {})
	canon["hnn_fourth_letter"] = String(letter.get("title", ""))
	_run_state["canon_vars"] = canon
	_run_state["ng_plus"] = true
	_run_state["visit_total"] = 0
	_save_state()
	finished.emit(canon, tokens)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			if _title_root != null and _child_scene == null:
				_on_back_to_shelf()
				get_viewport().set_input_as_handled()
