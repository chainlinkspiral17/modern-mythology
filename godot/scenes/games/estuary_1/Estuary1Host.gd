extends Control
## ESTUARY (1) · run controller · Oneironautics Inc., 2001.
##
## The very small first one.  Team of three: Ines Rocha (tide-gate
## math, her first job), Marc Ostrom (score), Sarah Delahaye (every
## sprite).  One fixed screen, one lever, twelve weeks.  The report
## card grades the ESTUARY, not the player.  Gate touched at most
## twice: Week 13, the hidden thirteenth screen.
##
## Save file: user://estuary_1.save.json
##
## Signals · uniform slowstock host contract:
##   quit_to_shelf · caller (SlowstockBoot) reopens shelf
##   finished(canon_vars, lore_tokens)
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/estuary_1/manifest.json"
const SAVE_PATH     := "user://estuary_1.save.json"
const LOOP_SCENE    := "res://scenes/games/estuary_1/EstuaryOneLoop.tscn"
const HERO_DIR      := "res://resources/games/vol7/estuary_1/hero_images/"

# The six colors · total · everywhere
const C_WATER := Color("2a3038")
const C_FLAT  := Color("6a7a72")
const C_SKY   := Color("a8b4a0")
const C_REED  := Color("4a5a3a")
const C_HERON := Color("b8c0c0")
const C_GOLD  := Color("d8b048")

var _manifest: Dictionary = {}
var _run_state: Dictionary = {}
var _title_root: Node = null
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


func _fresh_state(cards_signed: Array) -> Dictionary:
	return {
		"week":          1,
		"gate":          "closed",
		"last_gate":     "closed",
		"touches":       0,
		"fry_remaining": 9.0,
		"fry_out":       0.0,
		"shrimp":        5.0,
		"channel":       6.0,
		"closed_streak": 0,
		"gate_history":  [],
		"heron_absent_used": false,
		"heron_absent_week": -1,
		"heron_calls":   0,
		"cards_signed":  cards_signed,
		"week_13_seen":  false,
		"canon_vars":    {},
		"lore_tokens_pending": []
	}


func _load_manifest() -> void:
	if not FileAccess.file_exists(MANIFEST_PATH): return
	var f := FileAccess.open(MANIFEST_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_manifest = parsed


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
	var cards: Array = _run_state.get("cards_signed", [])
	var w13: bool = bool(_run_state.get("week_13_seen", false))
	_run_state = _fresh_state(cards)
	_run_state["week_13_seen"] = w13
	_open_loop()


func _clear_current_scene() -> void:
	for n in [_title_root, _child_scene, _ending_root]:
		if n != null and is_instance_valid(n):
			n.queue_free()
	_title_root = null
	_child_scene = null
	_ending_root = null


func _play_bgm(path: String) -> void:
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("play_bgm"):
		am.play_bgm(path)


func _sfx(preset: String) -> void:
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null and sb.has_method("play"):
		sb.play(preset)


# ─── Title screen · the estuary at rest · six colors ─────────────

func _build_title_screen() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/e1/mix_d.wav")   # the bare drone

	_title_root = Control.new()
	_title_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_title_root)

	# The screen the whole game happens on · flattened to a title
	var sky := ColorRect.new()
	sky.color = C_SKY
	sky.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.add_child(sky)

	var water := ColorRect.new()
	water.color = C_WATER
	water.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	water.offset_top = -420
	_title_root.add_child(water)

	var flat := ColorRect.new()
	flat.color = C_FLAT
	flat.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	flat.offset_top = -240
	_title_root.add_child(flat)

	var reeds := ColorRect.new()
	reeds.color = C_REED
	reeds.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	reeds.offset_top = -120
	reeds.offset_bottom = -80
	_title_root.add_child(reeds)

	# One line of tide-gold at the waterline · earned even here
	var gold := ColorRect.new()
	gold.color = C_GOLD
	gold.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	gold.offset_top = -422
	gold.offset_bottom = -420
	gold.offset_left = 500
	gold.offset_right = -500
	_title_root.add_child(gold)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -320
	v.offset_right = 320
	v.offset_top = -170
	v.offset_bottom = 230
	v.add_theme_constant_override("separation", 12)
	_title_root.add_child(v)

	var shelf: Dictionary = _manifest.get("shelf", {})

	var title := Label.new()
	title.text = String(shelf.get("label_title", "ESTUARY"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 44)
	title.add_theme_color_override("font_color", C_WATER)
	v.add_child(title)

	var subtitle := Label.new()
	subtitle.text = String(shelf.get("label_subtitle", "the very small first one"))
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 14)
	subtitle.add_theme_color_override("font_color", C_WATER)
	v.add_child(subtitle)

	var meta := Label.new()
	meta.text = "Oneironautics Inc. · Portland, OR · 2001"
	meta.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	meta.add_theme_font_size_override("font_size", 12)
	meta.add_theme_color_override("font_color", C_REED)
	v.add_child(meta)

	var sep := Control.new()
	sep.custom_minimum_size = Vector2(0, 14)
	v.add_child(sep)

	var new_btn := Button.new()
	new_btn.text = "  A NEW SEASON  "
	new_btn.add_theme_font_size_override("font_size", 14)
	new_btn.pressed.connect(func() -> void: start_new_run(false))
	v.add_child(new_btn)

	if _has_save():
		var cont_btn := Button.new()
		cont_btn.text = "  CONTINUE · WEEK " + str(int(_run_state.get("week", 1))) + "  "
		cont_btn.add_theme_font_size_override("font_size", 14)
		cont_btn.pressed.connect(_open_loop)
		v.add_child(cont_btn)

	var back_btn := Button.new()
	back_btn.text = "  ← back to shelf  "
	back_btn.add_theme_font_size_override("font_size", 13)
	back_btn.pressed.connect(_on_back_to_shelf)
	v.add_child(back_btn)

	var cards: Array = _run_state.get("cards_signed", [])
	if cards.size() > 0:
		var status := Label.new()
		status.text = "· report cards signed: %d ·" % cards.size()
		status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		status.add_theme_font_size_override("font_size", 12)
		status.add_theme_color_override("font_color", C_REED)
		v.add_child(status)


func _has_save() -> bool:
	return FileAccess.file_exists(SAVE_PATH) and int(_run_state.get("week", 1)) > 1 \
			and int(_run_state.get("week", 1)) <= 12


func _on_back_to_shelf() -> void:
	quit_to_shelf.emit()


# ─── The loop ────────────────────────────────────────────────────

func _open_loop() -> void:
	_clear_current_scene()
	_child_scene = load(LOOP_SCENE).instantiate()
	_child_scene.quit.connect(_on_loop_quit)
	_child_scene.week_complete.connect(_on_week_complete)
	_child_scene.season_over.connect(_on_season_over)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_loop_quit() -> void:
	_save_state()
	_build_title_screen()


func _on_week_complete(state: Dictionary) -> void:
	_run_state = state
	_save_state()


# ─── The report card · it grades the estuary, not you ────────────

func _on_season_over(state: Dictionary, grades: Dictionary) -> void:
	_run_state = state
	_clear_current_scene()
	_sfx("signing")

	_ending_root = Control.new()
	_ending_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_ending_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_ending_root)

	var bg := ColorRect.new()
	bg.color = C_WATER
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_ending_root.add_child(bg)

	# The card · HeroImage blank stock, grades overlaid live
	var hero := HeroImage.new()
	if hero.load_from(HERO_DIR + "report_card.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(640, 360))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -320
		tex_rect.offset_right = 320
		tex_rect.offset_top = -240
		tex_rect.offset_bottom = 120
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_ending_root.add_child(tex_rect)

		# Grades beside the row labels · pencil, in the gold
		var rows := {"water": 27, "passage": 41, "patience": 55}
		for key in rows.keys():
			var g := Label.new()
			g.text = String(grades.get(key, "C"))
			g.add_theme_font_size_override("font_size", 34)
			g.add_theme_color_override("font_color", C_GOLD)
			# Hero pixel (120, row_y) → screen · 4× scale from card center
			g.position = Vector2(640 - 320 + 120 * 4, 360 - 240 + int(rows[key]) * 4 - 20)
			_ending_root.add_child(g)

	var footer := Label.new()
	footer.text = "the season is graded for the estuary · not for you"
	footer.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	footer.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	footer.offset_top = 150
	footer.offset_bottom = 180
	footer.offset_left = -320
	footer.offset_right = 320
	footer.add_theme_font_size_override("font_size", 13)
	footer.add_theme_color_override("font_color", C_FLAT)
	_ending_root.add_child(footer)

	var done_btn := Button.new()
	done_btn.text = "  put the card in the log  "
	done_btn.add_theme_font_size_override("font_size", 14)
	done_btn.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	done_btn.offset_top = 200
	done_btn.offset_bottom = 240
	done_btn.offset_left = -130
	done_btn.offset_right = 130
	done_btn.pressed.connect(func() -> void: _after_report_card(grades))
	_ending_root.add_child(done_btn)


func _after_report_card(grades: Dictionary) -> void:
	var cards: Array = _run_state.get("cards_signed", [])
	cards.append("%s%s%s" % [grades.get("water", "C"), grades.get("passage", "C"), grades.get("patience", "C")])
	_run_state["cards_signed"] = cards

	if int(grades.get("touches", 99)) <= 2:
		_show_week_13(grades)
	else:
		_finish_run(grades)


# ─── Week 13 · hidden · night · no UI ────────────────────────────

func _show_week_13(grades: Dictionary) -> void:
	_clear_current_scene()
	_run_state["week_13_seen"] = true
	_play_bgm("res://assets/audio/bgm/e1/mix_dfsh.wav")   # the full chord

	_ending_root = Control.new()
	_ending_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_ending_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_ending_root)

	var bg := ColorRect.new()
	bg.color = Color("11151a")
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_ending_root.add_child(bg)

	var hero := HeroImage.new()
	if hero.load_from(HERO_DIR + "week_13_night.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(1120, 630))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -560
		tex_rect.offset_right = 560
		tex_rect.offset_top = -315
		tex_rect.offset_bottom = 315
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_ending_root.add_child(tex_rect)

	var line := Label.new()
	line.text = "it was doing this before you, too."
	line.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	line.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	line.offset_top = 250
	line.offset_bottom = 290
	line.offset_left = -320
	line.offset_right = 320
	line.add_theme_font_size_override("font_size", 15)
	line.add_theme_color_override("font_color", C_HERON)
	line.modulate.a = 0.0
	_ending_root.add_child(line)

	# The line arrives late, on its own clock · then a quiet exit
	var tw := create_tween()
	tw.tween_interval(4.0)
	tw.tween_property(line, "modulate:a", 1.0, 3.0)
	tw.tween_interval(5.0)
	tw.tween_callback(func() -> void: _finish_run(grades))


func _finish_run(grades: Dictionary) -> void:
	var tokens: Array = _run_state.get("lore_tokens_pending", [])
	for t in ["estuary_1_finished", "the_dna_of_the_series"]:
		if not tokens.has(t):
			tokens.append(t)
	if String(grades.get("patience", "")) == "A" and not tokens.has("estuary_1_patience_a"):
		tokens.append("estuary_1_patience_a")
	if bool(_run_state.get("week_13_seen", false)) and not tokens.has("estuary_1_week_13_seen"):
		tokens.append("estuary_1_week_13_seen")
	_run_state["lore_tokens_pending"] = tokens
	OneironauticsTokens.add_many(tokens)
	var canon: Dictionary = _run_state.get("canon_vars", {})
	canon["estuary_1_grades"] = "%s / %s / %s" % [grades.get("water", "C"), grades.get("passage", "C"), grades.get("patience", "C")]
	_run_state["canon_vars"] = canon
	# The season is over · a fresh title shows a week-1 state
	_run_state["week"] = 1
	_save_state()
	finished.emit(canon, tokens)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			if _title_root != null and _child_scene == null and _ending_root == null:
				_on_back_to_shelf()
				get_viewport().set_input_as_handled()
