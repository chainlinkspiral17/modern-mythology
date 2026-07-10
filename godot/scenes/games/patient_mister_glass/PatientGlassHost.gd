extends Control
## THE PATIENT MISTER GLASS · run controller · RANCH, 2004.
##
## Fourteen evenings, one suspect, one kitchen.  The drive-home
## theme plays ONLY over the cards between evenings — until
## evening 14, when it finally plays in the kitchen, very
## quietly, and resolves.
##
## Save file: user://patient_mister_glass.save.json
##
## Signals · uniform slowstock host contract:
##   quit_to_shelf · finished(canon_vars, lore_tokens)
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/patient_mister_glass/manifest.json"
const DECK_PATH     := "res://resources/games/vol7/patient_mister_glass/question_deck.json"
const SAVE_PATH     := "user://patient_mister_glass.save.json"
const KITCHEN_SCENE := "res://scenes/games/patient_mister_glass/GlassKitchen.tscn"
const HERO_DIR      := "res://resources/games/vol7/patient_mister_glass/hero_images/"

const C_DARK    := Color("100c0a")
const C_AMBER   := Color("e8a038")
const C_BROWN   := Color("6a4a30")
const C_OCTOBER := Color("8a98a8")
const C_RED     := Color("c8442c")
const C_CREAM   := Color("d8ccb8")

var _manifest: Dictionary = {}
var _deck: Dictionary = {}
var _run_state: Dictionary = {}
var _title_root: Node = null
var _card_root: Node = null
var _child_scene: Node = null
var _verdict_root: Node = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	SlowstickLook.apply(self, "ranch")
	# Studio control chrome (mirrors the look preset) — cascades
	# to every child scene; see StickTheme.gd.
	theme = preload("res://scenes/games/StickTheme.gd").make("ranch")
	_run_state = _fresh_state([])
	_load_data()
	_load_save_if_present()
	_build_title_screen()


func _fresh_state(verdicts_seen: Array) -> Dictionary:
	# Rain evenings roll once per case and save with it.
	var rains: Array = []
	for e in range(1, 14):
		if randf() < 0.35:
			rains.append(e)
	return {
		"evening_n":     1,
		"trust":         5,
		"answers_heard": [],
		"findings":      [],
		"unlocked_questions": [],
		"rain_evenings": rains,
		"verdicts_seen": verdicts_seen,
		"canon_vars":    {},
		"lore_tokens_pending": []
	}


func _load_data() -> void:
	for pair in [[MANIFEST_PATH, "m"], [DECK_PATH, "d"]]:
		var path := String(pair[0])
		if not FileAccess.file_exists(path): continue
		var f := FileAccess.open(path, FileAccess.READ)
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			if String(pair[1]) == "m": _manifest = parsed
			else: _deck = parsed


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
	_run_state = _fresh_state(_run_state.get("verdicts_seen", []))
	_show_drive_card(1)


func _clear_current_scene() -> void:
	for n in [_title_root, _card_root, _child_scene, _verdict_root]:
		if n != null and is_instance_valid(n):
			n.queue_free()
	_title_root = null
	_card_root = null
	_child_scene = null
	_verdict_root = null


func _play_bgm(path: String) -> void:
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("play_bgm"):
		am.play_bgm(path)


# ─── Title ───────────────────────────────────────────────────────

func _build_title_screen() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/pmg/drive_home.wav")

	_title_root = Control.new()
	_title_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_title_root)

	var bg := ColorRect.new()
	bg.color = C_DARK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.add_child(bg)

	# RANCH red band · dimmed to evening
	var band := ColorRect.new()
	band.color = C_RED
	band.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	band.offset_bottom = 40
	_title_root.add_child(band)

	var ranch_lbl := Label.new()
	ranch_lbl.text = "RANCH · SAN FRANCISCO CA · SLOWBOX REV 3"
	ranch_lbl.position = Vector2(16, 10)
	ranch_lbl.add_theme_font_size_override("font_size", 13)
	ranch_lbl.add_theme_color_override("font_color", C_DARK)
	_title_root.add_child(ranch_lbl)

	var hero := HeroImage.new()
	if hero.load_from(HERO_DIR + "kitchen_evening_1.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(800, 450))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -400
		tex_rect.offset_right = 400
		tex_rect.offset_top = -300
		tex_rect.offset_bottom = 150
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

	var shelf: Dictionary = _manifest.get("shelf", {})

	var title := Label.new()
	title.text = String(shelf.get("label_title", "THE PATIENT MISTER GLASS"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 30)
	title.add_theme_color_override("font_color", C_CREAM)
	v.add_child(title)

	var subtitle := Label.new()
	subtitle.text = "fourteen evenings · one suspect · one kitchen"
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 14)
	subtitle.add_theme_color_override("font_color", C_OCTOBER)
	v.add_child(subtitle)

	var new_btn := Button.new()
	new_btn.text = "  OPEN THE FILE  "
	new_btn.add_theme_font_size_override("font_size", 14)
	new_btn.pressed.connect(func() -> void: start_new_run(false))
	v.add_child(new_btn)

	if _has_save():
		var cont_btn := Button.new()
		cont_btn.text = "  CONTINUE · EVENING " + str(int(_run_state.get("evening_n", 1))) + "  "
		cont_btn.add_theme_font_size_override("font_size", 14)
		cont_btn.pressed.connect(func() -> void: _show_drive_card(int(_run_state.get("evening_n", 1))))
		v.add_child(cont_btn)

	var back_btn := Button.new()
	back_btn.text = "  ← back to shelf  "
	back_btn.add_theme_font_size_override("font_size", 13)
	back_btn.pressed.connect(_on_back_to_shelf)
	v.add_child(back_btn)

	var verdicts: Array = _run_state.get("verdicts_seen", [])
	if verdicts.size() > 0:
		var status := Label.new()
		status.text = "· the file has been closed before · " + ", ".join(verdicts) + " ·"
		status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		status.add_theme_font_size_override("font_size", 12)
		status.add_theme_color_override("font_color", C_BROWN)
		v.add_child(status)


func _has_save() -> bool:
	var n: int = int(_run_state.get("evening_n", 1))
	return FileAccess.file_exists(SAVE_PATH) and n > 1 and n <= 13


func _on_back_to_shelf() -> void:
	quit_to_shelf.emit()


# ─── Drive cards · the theme's only stage ────────────────────────

func _show_drive_card(evening: int) -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/pmg/drive_home.wav")

	_card_root = Control.new()
	_card_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_card_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_card_root)

	var bg := ColorRect.new()
	bg.color = C_DARK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_card_root.add_child(bg)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -340
	v.offset_right = 340
	v.offset_top = -90
	v.offset_bottom = 90
	v.add_theme_constant_override("separation", 16)
	_card_root.add_child(v)

	var title := Label.new()
	title.text = "· THE COAST ROAD · EVENING %d ·" % evening
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 18)
	title.add_theme_color_override("font_color", C_OCTOBER)
	v.add_child(title)

	var line := Label.new()
	line.text = _card_line(evening)
	line.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	line.add_theme_font_size_override("font_size", 14)
	line.add_theme_color_override("font_color", C_CREAM)
	v.add_child(line)

	var go := Button.new()
	go.text = "  · knock ·  " if evening < 14 else "  · knock, one last time ·  "
	go.add_theme_font_size_override("font_size", 14)
	go.pressed.connect(_open_kitchen if evening < 14 else _show_verdict)
	v.add_child(go)


func _card_line(evening: int) -> String:
	match evening:
		1:  return "the file is thirty years old and weighs nothing. $31,000, the ferry accounts, 1971 to 1974, clerk of record A. GLASS. he agreed to the interviews by return post. his handwriting is very steady."
		5:  return "the theme on the radio isn't on the radio. you've started hearing it on the drive whether you play anything or not."
		9:  return "october is leaning in. the kitchen will be colder tonight. he will pretend it isn't and so will you."
		13: return "his letter said, come around the back, the bulb's gone in the front hall. the stove will be the only light. you have twelve questions and none of them are the one that matters."
		14: return "the verdict is due. the county wants a box checked. the coast road is long and the theme will not leave you alone tonight."
		_:  return "the coast road, again. the case is not getting bigger. it is getting deeper, which is different, and slower, and his."


# ─── Evenings ────────────────────────────────────────────────────

func _open_kitchen() -> void:
	_clear_current_scene()
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("stop_bgm"):
		am.stop_bgm()   # no theme during interviews · ever
	_child_scene = load(KITCHEN_SCENE).instantiate()
	_child_scene.quit.connect(_on_kitchen_quit)
	_child_scene.evening_over.connect(_on_evening_over)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_kitchen_quit() -> void:
	_save_state()
	_build_title_screen()


func _on_evening_over(state: Dictionary) -> void:
	_run_state = state
	var n: int = int(_run_state.get("evening_n", 1))
	_run_state["evening_n"] = n + 1
	_save_state()
	_show_drive_card(n + 1)


# ─── Evening 14 · the verdict ────────────────────────────────────

func _show_verdict() -> void:
	_clear_current_scene()
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("stop_bgm"):
		am.stop_bgm()

	_verdict_root = Control.new()
	_verdict_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_verdict_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_verdict_root)

	var bg := ColorRect.new()
	bg.color = C_DARK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_verdict_root.add_child(bg)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -400
	v.offset_right = 400
	v.offset_top = -220
	v.offset_bottom = 220
	v.add_theme_constant_override("separation", 14)
	_verdict_root.add_child(v)

	var hdr := Label.new()
	hdr.text = "· EVENING FOURTEEN · THE VERDICT ·"
	hdr.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hdr.add_theme_font_size_override("font_size", 20)
	hdr.add_theme_color_override("font_color", C_RED)
	v.add_child(hdr)

	var findings: Array = _run_state.get("findings", [])
	var sub := Label.new()
	sub.text = "findings on file · %d of 9.  he has put the kettle on.  he is waiting." % findings.size()
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.add_theme_font_size_override("font_size", 14)
	sub.add_theme_color_override("font_color", C_CREAM)
	v.add_child(sub)

	var verdicts: Dictionary = _deck.get("verdicts", {})
	for vid in ["accuse", "clear", "close_ledger"]:
		var vd: Dictionary = verdicts.get(vid, {})
		if vd.is_empty(): continue
		if vd.has("requires_finding_id") and not findings.has(String(vd["requires_finding_id"])):
			continue
		if int(vd.get("requires_findings", 0)) > findings.size():
			continue
		var b := Button.new()
		b.text = "  %s  " % String(vd.get("label", vid))
		b.add_theme_font_size_override("font_size", 15)
		b.pressed.connect(_resolve_verdict.bind(vid, vd))
		v.add_child(b)

	var hint := Label.new()
	hint.text = "(what you can file is what you found. the game grades nothing.)"
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hint.add_theme_font_size_override("font_size", 12)
	hint.add_theme_color_override("font_color", C_BROWN)
	v.add_child(hint)


func _resolve_verdict(vid: String, vd: Dictionary) -> void:
	_clear_current_scene()
	# The theme, in the kitchen, for the only time.
	var resolved := vid == "close_ledger"
	_play_bgm("res://assets/audio/bgm/pmg/drive_home%s.wav" % ("_resolved" if resolved else ""))

	_verdict_root = Control.new()
	_verdict_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_verdict_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_verdict_root)

	var bg := ColorRect.new()
	bg.color = C_DARK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_verdict_root.add_child(bg)

	var hero := HeroImage.new()
	var img := "kitchen_evening_13" if vid == "accuse" else "kitchen_evening_1"
	if hero.load_from(HERO_DIR + img + ".json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(640, 360))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -320
		tex_rect.offset_right = 320
		tex_rect.offset_top = -300
		tex_rect.offset_bottom = 60
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_verdict_root.add_child(tex_rect)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -400
	v.offset_right = 400
	v.offset_top = 80
	v.offset_bottom = 340
	v.add_theme_constant_override("separation", 14)
	_verdict_root.add_child(v)

	var body := Label.new()
	body.text = String(vd.get("text", ""))
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.add_theme_font_size_override("font_size", 14)
	body.add_theme_color_override("font_color", C_CREAM)
	v.add_child(body)

	var card := Label.new()
	card.text = String(vd.get("card", ""))
	card.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	card.add_theme_font_size_override("font_size", 13)
	card.add_theme_color_override("font_color", C_OCTOBER)
	v.add_child(card)

	var done := Button.new()
	done.text = "  · close the file ·  "
	done.add_theme_font_size_override("font_size", 14)
	done.pressed.connect(func() -> void: _finish_run(vid))
	v.add_child(done)


func _finish_run(vid: String) -> void:
	var token_by_vid := {"accuse": "glass_verdict_accuse",
		"clear": "glass_verdict_clear", "close_ledger": "glass_verdict_closed"}
	var tokens: Array = _run_state.get("lore_tokens_pending", [])
	for t in ["patient_mister_glass_finished", String(token_by_vid.get(vid, ""))]:
		if t != "" and not tokens.has(t):
			tokens.append(t)
	_run_state["lore_tokens_pending"] = tokens
	OneironauticsTokens.add_many(tokens)
	var canon: Dictionary = _run_state.get("canon_vars", {})
	canon["glass_verdict"] = vid
	_run_state["canon_vars"] = canon
	var seen: Array = _run_state.get("verdicts_seen", [])
	if not seen.has(vid):
		seen.append(vid)
	_run_state["verdicts_seen"] = seen
	_run_state["evening_n"] = 1
	_save_state()
	finished.emit(canon, tokens)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			if _title_root != null and _child_scene == null:
				_on_back_to_shelf()
				get_viewport().set_input_as_handled()
