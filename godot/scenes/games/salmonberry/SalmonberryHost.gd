extends Control
## SALMONBERRY · run controller · Oneironautics Inc., 2006.
##
## A year in the fictional cannery town of Salmonberry, Oregon,
## 1963-64. Part adventure, part RPG: you grow by living (six
## aptitudes), you build a web of bonds, you keep a book of the coast.
## No combat. The year is framed by the November the radio went quiet
## and the Good Friday the water came up the river. The register at the
## end is who the town knows in June.
##
## Save: user://salmonberry.save.json (mid-year continue supported).
##
## Signals · uniform slowstock host contract:
##   quit_to_shelf · finished(canon_vars, lore_tokens)
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/salmonberry/manifest.json"
const SAVE_PATH     := "user://salmonberry.save.json"
const YEAR_SCENE    := "res://scenes/games/salmonberry/SalmonberryYear.tscn"
const HERO_DIR      := "res://resources/games/vol7/salmonberry/hero_images/"

# coastal 1960s gouache
const C_SEA  := Color("3b5a6b")
const C_SAND := Color("b8a882")
const C_FOG  := Color("c8cec4")
const C_FIR  := Color("33452f")
const C_RUST := Color("9c5a3a")
const C_GOLD := Color("d8b048")
const C_INK  := Color("23282a")

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
	theme = preload("res://scenes/games/StickTheme.gd").make("oneironautics")
	_run_state = _fresh_state()
	_load_manifest()
	_load_save_if_present()
	_build_title_screen()


func _fresh_state() -> Dictionary:
	return {
		"month":   0,
		"apts":    {"hands": 0, "sea": 0, "word": 0, "heart": 0, "wild": 0, "grit": 0},
		"bonds":   {},
		"money":   0,
		"journal": [],
		"songs":   0,
		"thread_clues": [],
		"told_estelle": false,
		"helped_wave": false,
		"years_done":  0,
		"canon_vars":  {},
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
	var years: int = int(_run_state.get("years_done", 0))
	_run_state = _fresh_state()
	_run_state["years_done"] = years
	_open_year()


func _clear_current_scene() -> void:
	for n in [_title_root, _child_scene, _ending_root]:
		if n != null and is_instance_valid(n):
			n.queue_free()
	_title_root = null
	_child_scene = null
	_ending_root = null


func _play_bgm(path: String) -> void:
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("request_scene_bgm"):
		am.request_scene_bgm(path)


func _sfx(preset: String) -> void:
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null and sb.has_method("play"):
		sb.play(preset)


# ─── Title ───────────────────────────────────────────────────────

func _build_title_screen() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/salmonberry/coast.wav")

	_title_root = Control.new()
	_title_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_title_root)

	var sky := ColorRect.new()
	sky.color = C_FOG
	sky.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.add_child(sky)

	var sea := ColorRect.new()
	sea.color = C_SEA
	sea.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	sea.offset_top = -300
	_title_root.add_child(sea)

	var sand := ColorRect.new()
	sand.color = C_SAND
	sand.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	sand.offset_top = -150
	_title_root.add_child(sand)

	var hero := HeroImage.new()
	if hero.load_from(HERO_DIR + "title.json"):
		var tr := TextureRect.new()
		tr.texture = hero.texture(Vector2i(1120, 630))
		tr.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tr.offset_left = -560
		tr.offset_right = 560
		tr.offset_top = -315
		tr.offset_bottom = 315
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		tr.modulate.a = 0.55
		_title_root.add_child(tr)

	preload("res://scenes/games/TitleMotion.gd").attach(_title_root, "oneironautics")

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -320
	v.offset_right = 320
	v.offset_top = -170
	v.offset_bottom = 240
	v.add_theme_constant_override("separation", 12)
	_title_root.add_child(v)

	var shelf: Dictionary = _manifest.get("shelf", {})

	var title := Label.new()
	title.text = String(shelf.get("label_title", "SALMONBERRY"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 44)
	title.add_theme_color_override("font_color", C_RUST)
	v.add_child(title)

	var subtitle := Label.new()
	subtitle.text = String(shelf.get("label_subtitle", "a year on the coast"))
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 15)
	subtitle.add_theme_color_override("font_color", C_INK)
	v.add_child(subtitle)

	var meta := Label.new()
	meta.text = "Oneironautics Inc. · Portland, OR · 1992 · Salmonberry, 1963"
	meta.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	meta.add_theme_font_size_override("font_size", 12)
	meta.add_theme_color_override("font_color", C_FIR)
	v.add_child(meta)

	var sep := Control.new()
	sep.custom_minimum_size = Vector2(0, 14)
	v.add_child(sep)

	var new_btn := Button.new()
	new_btn.text = "  COME TO LIVE ON THE COAST  "
	new_btn.add_theme_font_size_override("font_size", 14)
	new_btn.pressed.connect(func() -> void: start_new_run(false))
	v.add_child(new_btn)

	if _has_save():
		var cont := Button.new()
		cont.text = "  CONTINUE · %s  " % _month_name(int(_run_state.get("month", 0)))
		cont.add_theme_font_size_override("font_size", 14)
		cont.pressed.connect(_open_year)
		v.add_child(cont)

	var back := Button.new()
	back.text = "  ← back to shelf  "
	back.add_theme_font_size_override("font_size", 13)
	back.pressed.connect(_on_back_to_shelf)
	v.add_child(back)

	var years: int = int(_run_state.get("years_done", 0))
	if years > 0:
		var st := Label.new()
		st.text = "· years lived on the coast: %d ·" % years
		st.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		st.add_theme_font_size_override("font_size", 12)
		st.add_theme_color_override("font_color", C_FIR)
		v.add_child(st)

	GamepadMgr.focus_first.call_deferred(_title_root)


const MONTHS := ["September", "October", "November", "December", "January",
	"February", "March", "April", "May", "June"]


func _month_name(i: int) -> String:
	var idx: int = clampi(i, 0, MONTHS.size() - 1)
	var yr: int = 1963 if idx <= 3 else 1964
	return "%s %d" % [MONTHS[idx], yr]


func _has_save() -> bool:
	return FileAccess.file_exists(SAVE_PATH) and int(_run_state.get("month", 0)) > 0 \
			and int(_run_state.get("month", 0)) < MONTHS.size()


func _on_back_to_shelf() -> void:
	quit_to_shelf.emit()


# ─── The year ────────────────────────────────────────────────────

func _open_year() -> void:
	_clear_current_scene()
	_child_scene = load(YEAR_SCENE).instantiate()
	_child_scene.quit.connect(_on_year_quit)
	_child_scene.month_complete.connect(_on_month_complete)
	_child_scene.year_over.connect(_on_year_over)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_year_quit() -> void:
	_save_state()
	_build_title_screen()


func _on_month_complete(state: Dictionary) -> void:
	_run_state = state
	_save_state()


# ─── Ending register ─────────────────────────────────────────────

const REGISTER_TITLE := {
	"song":     "THE SONG",
	"keeper":   "THE KEEPER",
	"listener": "THE LISTENER",
	"hands":    "THE HANDS",
	"leaver":   "THE LEAVER",
}
const REGISTER_LINE := {
	"song":     "June. The bus is idling on Main and Vovo is singing the last verse to you through the window, the one for the boat that does not come back, and you have all of it now. You will carry these songs your whole life, and one day put them in things, and nobody will know where they came from. You know.",
	"keeper":   "June. Your book of the coast is nearly full — the birds, the tides, the weather signs, the town's own small lore. You noticed this place while it was still itself. Someone had to. It was you.",
	"listener": "June. You know the town by its stories now, the ones it does not tell at home. You are its memory, a little. That is a thing a person can be for a place.",
	"hands":    "June. Your hands know the knife and the net and the oar, and the town knows your name, and Del does not say well done, which means well done. You belong here now.",
	"leaver":   "June. You did your year. You are going home changed but apart — the coast stayed a place you visited. Not everyone puts down roots in the fog. That is all right too.",
}


func _on_year_over(result: Dictionary) -> void:
	_run_state = result.get("state", _run_state)
	_run_state["years_done"] = int(_run_state.get("years_done", 0)) + 1
	_clear_current_scene()
	_sfx("season_settle")
	var register: String = String(result.get("register", "leaver"))

	_ending_root = Control.new()
	_ending_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_ending_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_ending_root)

	var bg := ColorRect.new()
	bg.color = C_FOG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_ending_root.add_child(bg)

	var hero := HeroImage.new()
	if hero.load_from(HERO_DIR + "ending_%s.json" % register):
		var tr := TextureRect.new()
		tr.texture = hero.texture(Vector2i(1120, 630))
		tr.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		tr.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tr.modulate.a = 0.4
		_ending_root.add_child(tr)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -380
	v.offset_right = 380
	v.offset_top = -190
	v.offset_bottom = 230
	v.add_theme_constant_override("separation", 16)
	_ending_root.add_child(v)

	var title := Label.new()
	title.text = String(REGISTER_TITLE.get(register, "THE LEAVER"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 34)
	title.add_theme_color_override("font_color", C_RUST)
	v.add_child(title)

	var line := Label.new()
	line.text = String(REGISTER_LINE.get(register, ""))
	line.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	line.add_theme_font_size_override("font_size", 15)
	line.add_theme_color_override("font_color", C_INK)
	v.add_child(line)

	var coda := Label.new()
	coda.text = String(result.get("coda", ""))
	coda.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	coda.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	coda.add_theme_font_size_override("font_size", 13)
	coda.add_theme_color_override("font_color", C_FIR)
	v.add_child(coda)

	var sep := Control.new()
	sep.custom_minimum_size = Vector2(0, 8)
	v.add_child(sep)

	var done := Button.new()
	done.text = "  close the book  "
	done.add_theme_font_size_override("font_size", 14)
	done.pressed.connect(func() -> void: _finish_run(register))
	v.add_child(done)

	GamepadMgr.focus_first.call_deferred(_ending_root)


func _finish_run(register: String) -> void:
	var tokens: Array = _run_state.get("lore_tokens_pending", [])
	if not tokens.has("salmonberry_finished"):
		tokens.append("salmonberry_finished")
	var reg_token: String = "salmonberry_" + ("the_song" if register == "song" else register)
	if not tokens.has(reg_token):
		tokens.append(reg_token)
	if bool(_run_state.get("helped_wave", false)) and not tokens.has("salmonberry_the_wave"):
		tokens.append("salmonberry_the_wave")
	if not tokens.has("salmonberry_faire_seen"):
		tokens.append("salmonberry_faire_seen")
	_run_state["lore_tokens_pending"] = tokens
	OneironauticsTokens.add_many(tokens)

	var canon: Dictionary = _run_state.get("canon_vars", {})
	canon["salmonberry_result"] = register
	_run_state["canon_vars"] = canon
	_run_state["month"] = 0
	_save_state()
	finished.emit(canon, tokens)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			if _title_root != null and _child_scene == null and _ending_root == null:
				_on_back_to_shelf()
				get_viewport().set_input_as_handled()
