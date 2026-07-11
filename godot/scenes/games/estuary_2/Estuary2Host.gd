extends Control
## ESTUARY 2 · run controller · Oneironautics Inc., 2002.
##
## Marc Ostrom's only lead credit.  Twelve walks, June to
## September.  E1 was responsibility; E2 is WITNESS · you change
## nothing directly and it matters anyway, because standing at
## the hearing is made of looking.
##
## The hearing (after walk 10): one statement, assembled from
## illuminated journal pages · the game quietly requires that you
## WITNESSED to have standing.  Three endings; THE COMPROMISE is
## canonically Estuary 3's status quo.
##
## Save file: user://estuary_2.save.json
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/estuary_2/manifest.json"
const WALKS_PATH    := "res://resources/games/vol7/estuary_2/walks.json"
const SAVE_PATH     := "user://estuary_2.save.json"
const WALK_SCENE    := "res://scenes/games/estuary_2/MudflatWalk.tscn"
const HERO_DIR      := "res://resources/games/vol7/estuary_2/hero_images/"

const C_MUD   := Color("5a6058")
const C_DRY   := Color("8a8878")
const C_CHAN  := Color("3a4a52")
const C_PLANK := Color("a8a290")
const C_STAKE := Color("d87838")
const C_DARK  := Color("2a3038")

var _manifest: Dictionary = {}
var _hearing_def: Dictionary = {}
var _run_state: Dictionary = {}
var _title_root: Node = null
var _child_scene: Node = null
var _beat_root: Node = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	SlowstickLook.apply(self, "oneironautics")
	# Studio control chrome (mirrors the look preset) — cascades
	# to every child scene; see StickTheme.gd.
	theme = preload("res://scenes/games/StickTheme.gd").make("oneironautics")
	_run_state = _fresh_state([])
	_load_data()
	_load_save_if_present()
	_build_title_screen()


func _fresh_state(summers: Array) -> Dictionary:
	return {
		"walk_n":       1,
		"observations": {},
		"illuminated":  [],
		"petition":     [],
		"hearing_result": "",
		"summers":      summers,
		"canon_vars":   {},
		"lore_tokens_pending": []
	}


func _load_data() -> void:
	for pair in [[MANIFEST_PATH, "m"], [WALKS_PATH, "w"]]:
		if not FileAccess.file_exists(String(pair[0])): continue
		var f := FileAccess.open(String(pair[0]), FileAccess.READ)
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			if String(pair[1]) == "m": _manifest = parsed
			else: _hearing_def = (parsed as Dictionary).get("hearing", {})


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
	_run_state = _fresh_state(_run_state.get("summers", []))
	_open_walk()


func _clear_current_scene() -> void:
	for n in [_title_root, _child_scene, _beat_root]:
		if n != null and is_instance_valid(n):
			n.queue_free()
	_title_root = null
	_child_scene = null
	_beat_root = null


func _play_bgm(path: String) -> void:
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("play_bgm"):
		am.play_bgm(path)


# ─── Title ───────────────────────────────────────────────────────

func _build_title_screen() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/e2/walk_01.wav")   # the theme, stated plainly

	_title_root = Control.new()
	_title_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_title_root)

	var bg := ColorRect.new()
	bg.color = C_DRY
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.add_child(bg)

	var hero := HeroImage.new()
	if hero.load_from(HERO_DIR + "stakes_at_dawn.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(800, 450))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -400
		tex_rect.offset_right = 400
		tex_rect.offset_top = -310
		tex_rect.offset_bottom = 140
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_title_root.add_child(tex_rect)

	# Title motion — studio character (menu motion playbook).
	preload("res://scenes/games/TitleMotion.gd").attach(_title_root, "oneironautics")

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -340
	v.offset_right = 340
	v.offset_top = 120
	v.offset_bottom = 350
	v.add_theme_constant_override("separation", 10)
	_title_root.add_child(v)

	var title := Label.new()
	title.text = "ESTUARY 2"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 38)
	title.add_theme_color_override("font_color", C_DARK)
	v.add_child(title)

	var subtitle := Label.new()
	subtitle.text = "the summer at the mudflats · Oneironautics Inc. · 2002"
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 13)
	subtitle.add_theme_color_override("font_color", C_CHAN)
	v.add_child(subtitle)

	var new_btn := Button.new()
	new_btn.text = "  JUNE · THE FIRST WALK  "
	new_btn.add_theme_font_size_override("font_size", 14)
	new_btn.pressed.connect(func() -> void: start_new_run(false))
	v.add_child(new_btn)

	if _has_save():
		var cont_btn := Button.new()
		cont_btn.text = "  CONTINUE · WALK " + str(int(_run_state.get("walk_n", 1))) + "  "
		cont_btn.add_theme_font_size_override("font_size", 14)
		cont_btn.pressed.connect(_open_walk)
		v.add_child(cont_btn)

	var back_btn := Button.new()
	back_btn.text = "  ← back to shelf  "
	back_btn.add_theme_font_size_override("font_size", 13)
	back_btn.pressed.connect(_on_back_to_shelf)
	v.add_child(back_btn)

	var summers: Array = _run_state.get("summers", [])
	if summers.size() > 0:
		var status := Label.new()
		status.text = "· summers witnessed: %d (%s) ·" % [summers.size(), ", ".join(summers)]
		status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		status.add_theme_font_size_override("font_size", 12)
		status.add_theme_color_override("font_color", C_MUD)
		v.add_child(status)


func _has_save() -> bool:
	var n: int = int(_run_state.get("walk_n", 1))
	return FileAccess.file_exists(SAVE_PATH) and n > 1 and n <= 12


func _on_back_to_shelf() -> void:
	quit_to_shelf.emit()


# ─── Walks ───────────────────────────────────────────────────────

func _open_walk() -> void:
	_clear_current_scene()
	_child_scene = load(WALK_SCENE).instantiate()
	_child_scene.quit.connect(_on_walk_quit)
	_child_scene.walk_over.connect(_on_walk_over)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_walk_quit() -> void:
	_save_state()
	_build_title_screen()


func _on_walk_over(state: Dictionary) -> void:
	_run_state = state
	var n: int = int(_run_state.get("walk_n", 1))
	if n == 10:
		_run_state["walk_n"] = 11
		_save_state()
		_show_hearing()
		return
	if n >= 12:
		_save_state()
		_show_winter()
		return
	_run_state["walk_n"] = n + 1
	_save_state()
	_open_walk()


# ─── The hearing · week 10 · standing is made of looking ─────────

func _show_hearing() -> void:
	_clear_current_scene()
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("stop_bgm"):
		am.stop_bgm()

	_beat_root = Control.new()
	_beat_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_beat_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_beat_root)

	var bg := ColorRect.new()
	bg.color = C_DARK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_beat_root.add_child(bg)

	var hero := HeroImage.new()
	if hero.load_from(HERO_DIR + "hearing_room.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(640, 360))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -320
		tex_rect.offset_right = 320
		tex_rect.offset_top = -300
		tex_rect.offset_bottom = 60
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_beat_root.add_child(tex_rect)

	var illuminated: Array = _run_state.get("illuminated", [])
	var sigs: Array = _run_state.get("petition", [])
	var standing: bool = illuminated.size() >= 3
	var result := ""
	if not standing:
		result = "dredged"
	else:
		var score: int = mini(illuminated.size(), 6) + sigs.size()
		if score >= 8: result = "blocked"
		elif score >= 5: result = "compromise"
		else: result = "dredged"
	_run_state["hearing_result"] = result

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -400
	v.offset_right = 400
	v.offset_top = 80
	v.offset_bottom = 340
	v.add_theme_constant_override("separation", 12)
	_beat_root.add_child(v)

	var intro := Label.new()
	intro.text = String(_hearing_def.get("intro", ""))
	intro.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	intro.add_theme_font_size_override("font_size", 14)
	intro.add_theme_color_override("font_color", C_PLANK)
	v.add_child(intro)

	var body := Label.new()
	if not standing:
		body.text = String(_hearing_def.get("no_standing", ""))
	else:
		var pages := ", ".join(illuminated.slice(0, 6))
		body.text = "%s %s.  %d signature(s) enter with you." % [
			String(_hearing_def.get("statement_prefix", "")), pages, sigs.size()]
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.add_theme_font_size_override("font_size", 14)
	body.add_theme_color_override("font_color", C_DRY)
	v.add_child(body)

	var go := Button.new()
	go.text = "  · the county votes ·  "
	go.add_theme_font_size_override("font_size", 14)
	go.pressed.connect(func() -> void:
		_save_state()
		_open_walk())
	v.add_child(go)


# ─── Winter ──────────────────────────────────────────────────────

func _show_winter() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/e2/walk_12.wav")   # resolved

	_beat_root = Control.new()
	_beat_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_beat_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_beat_root)

	var bg := ColorRect.new()
	bg.color = C_DARK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_beat_root.add_child(bg)

	var result := String(_run_state.get("hearing_result", "compromise"))
	var results: Dictionary = _hearing_def.get("results", {})
	var rd: Dictionary = results.get(result, {})

	var hero := HeroImage.new()
	if hero.load_from(HERO_DIR + String(rd.get("card", "winter_compromise")) + ".json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(800, 450))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -400
		tex_rect.offset_right = 400
		tex_rect.offset_top = -300
		tex_rect.offset_bottom = 150
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_beat_root.add_child(tex_rect)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -380
	v.offset_right = 380
	v.offset_top = 160
	v.offset_bottom = 350
	v.add_theme_constant_override("separation", 12)
	_beat_root.add_child(v)

	var title := Label.new()
	title.text = "· WINTER · %s ·" % String(rd.get("title", result.to_upper()))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 18)
	title.add_theme_color_override("font_color", C_STAKE)
	v.add_child(title)

	var body := Label.new()
	body.text = String(rd.get("text", ""))
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_theme_font_size_override("font_size", 14)
	body.add_theme_color_override("font_color", C_DRY)
	v.add_child(body)

	var done := Button.new()
	done.text = "  · close the journal ·  "
	done.add_theme_font_size_override("font_size", 14)
	done.pressed.connect(func() -> void: _finish_run(result))
	v.add_child(done)


func _finish_run(result: String) -> void:
	var tokens: Array = _run_state.get("lore_tokens_pending", [])
	for t in ["estuary_2_finished", "estuary_2_hearing_" + result]:
		if not tokens.has(t):
			tokens.append(t)
	for sid in _run_state.get("illuminated", []):
		var tk := "e2_journal_" + String(sid)
		if not tokens.has(tk):
			tokens.append(tk)
	_run_state["lore_tokens_pending"] = tokens
	OneironauticsTokens.add_many(tokens)
	var canon: Dictionary = _run_state.get("canon_vars", {})
	canon["estuary_2_hearing"] = result
	canon["estuary_2_pages"] = (_run_state.get("illuminated", []) as Array).size()
	_run_state["canon_vars"] = canon
	var summers: Array = _run_state.get("summers", [])
	summers.append(result)
	_run_state["summers"] = summers
	_run_state["walk_n"] = 1
	_save_state()
	finished.emit(canon, tokens)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			if _title_root != null and _child_scene == null:
				_on_back_to_shelf()
				get_viewport().set_input_as_handled()
