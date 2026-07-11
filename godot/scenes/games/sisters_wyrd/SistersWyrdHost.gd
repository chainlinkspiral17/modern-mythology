extends Control
## THE SISTERS WYRD · run controller · Sagebrush Engineworks, 1983.
##
## The oldest playable cart on the shelf.  A drifter, a home hex,
## seven scales of woven territory, and four witches on a compass
## that lies.  Dorothy by way of the Gunslinger.
##
## Save file: user://sisters_wyrd.save.json
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/sisters_wyrd/manifest.json"
const WITCHES_PATH  := "res://resources/games/vol7/sisters_wyrd/witches.json"
const SAVE_PATH     := "user://sisters_wyrd.save.json"
const CRAWL_SCENE   := "res://scenes/games/sisters_wyrd/WyrdHexcrawl.tscn"
const HERO_DIR      := "res://resources/games/vol7/sisters_wyrd/hero_images/"

const C_DUST   := Color("c8a878")
const C_INK    := Color("201410")
const C_BONE   := Color("e8dcc0")
const C_BLOOD  := Color("7a3020")
const C_SILVER := Color("b8bcc8")
const C_WYRD   := Color("8a58a8")

# Preload by path — new class_names miss the first editor scan
# after a pull (sprite playbook rule).
const FIGURE_ART := preload("res://scenes/games/sisters_wyrd/WyrdFigureArt.gd")

var _manifest: Dictionary = {}
var _witches: Dictionary = {}
var _run_state: Dictionary = {}
var _title_root: Node = null
var _child_scene: Node = null
var _beat_root: Node = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	SlowstickLook.apply(self, "sagebrush")
	# Studio control chrome (mirrors the look preset) — cascades
	# to every child scene; see StickTheme.gd.
	theme = preload("res://scenes/games/StickTheme.gd").make("sagebrush")
	_run_state = _fresh_state([])
	_load_data()
	_load_save_if_present()
	_build_title_screen()


func _fresh_state(rides: Array) -> Dictionary:
	return {
		"addr":  [0, 0, 0, 0, 0, 0],
		"grit":  6,
		"silver": 3,
		"lore":  0,
		"witches_dealt": {},
		"encounters_seen": [],
		"no_southwest": false,
		"rides": rides,
		"canon_vars": {},
		"lore_tokens_pending": []
	}


func _load_data() -> void:
	for pair in [[MANIFEST_PATH, "m"], [WITCHES_PATH, "w"]]:
		if not FileAccess.file_exists(String(pair[0])): continue
		var f := FileAccess.open(String(pair[0]), FileAccess.READ)
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			if String(pair[1]) == "m": _manifest = parsed
			else: _witches = parsed


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
	_run_state = _fresh_state(_run_state.get("rides", []))
	_open_crawl()


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
	_play_bgm("res://assets/audio/bgm/sw/territory.wav")

	_title_root = Control.new()
	_title_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_title_root)

	var bg := ColorRect.new()
	bg.color = C_DUST
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.add_child(bg)

	var hero := HeroImage.new()
	if hero.load_from(HERO_DIR + "title_territory.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(800, 450))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -400
		tex_rect.offset_right = 400
		tex_rect.offset_top = -310
		tex_rect.offset_bottom = 140
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_title_root.add_child(tex_rect)

	# the drifter, standing at the edge of the territory
	var drifter_rect := TextureRect.new()
	drifter_rect.texture = FIGURE_ART.drifter(Vector2i(54, 84))
	drifter_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	drifter_rect.offset_left = -378
	drifter_rect.offset_right = -324
	drifter_rect.offset_top = 52
	drifter_rect.offset_bottom = 136
	drifter_rect.stretch_mode = TextureRect.STRETCH_KEEP
	drifter_rect.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_title_root.add_child(drifter_rect)

	# Dust on the wind over the territory (menu motion playbook).
	preload("res://scenes/games/TitleMotion.gd").attach(_title_root, "sagebrush")

	# The living titleplate — the logo earns its marks as the ride
	# does. Each dealt sister sets a witch-sign at her compass point
	# over the hex; the eighth point burns at center once the loom
	# has been seen. (User idea: fill the logo in as a title plate.)
	var dealt_marks: Dictionary = _run_state.get("witches_dealt", {})
	var mark_pos: Dictionary = {
		"north": Vector2(-8, -260), "east": Vector2(180, -90),
		"south": Vector2(-8, 90), "west": Vector2(-196, -90)}
	for wid_v in dealt_marks.keys():
		var wid := String(wid_v)
		if not mark_pos.has(wid):
			continue
		var pip := ColorRect.new()
		pip.color = C_WYRD if String(dealt_marks[wid]) == "unweave" else C_BLOOD
		pip.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		var mp: Vector2 = mark_pos[wid]
		pip.offset_left = mp.x
		pip.offset_right = mp.x + 16
		pip.offset_top = mp.y
		pip.offset_bottom = mp.y + 16
		pip.pivot_offset = Vector2(8, 8)
		pip.rotation_degrees = 45.0
		_title_root.add_child(pip)
	if bool(_run_state.get("eighth_point_seen", false)):
		var eighth := ColorRect.new()
		eighth.color = C_WYRD
		eighth.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		eighth.offset_left = -10
		eighth.offset_right = 10
		eighth.offset_top = -95
		eighth.offset_bottom = -75
		eighth.pivot_offset = Vector2(10, 10)
		eighth.rotation_degrees = 45.0
		_title_root.add_child(eighth)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -340
	v.offset_right = 340
	v.offset_top = 130
	v.offset_bottom = 350
	v.add_theme_constant_override("separation", 10)
	_title_root.add_child(v)

	var title := Label.new()
	title.text = "THE SISTERS WYRD"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 36)
	title.add_theme_color_override("font_color", C_INK)
	v.add_child(title)

	var subtitle := Label.new()
	subtitle.text = "SAGEBRUSH ENGINEWORKS · AMARILLO TX · 1983 · seven scales · four sisters · one porch"
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 13)
	subtitle.add_theme_color_override("font_color", C_BLOOD)
	v.add_child(subtitle)

	var new_btn := Button.new()
	new_btn.text = "  SADDLE UP  "
	new_btn.add_theme_font_size_override("font_size", 14)
	new_btn.pressed.connect(func() -> void: start_new_run(false))
	v.add_child(new_btn)

	if _has_save():
		var cont_btn := Button.new()
		cont_btn.text = "  CONTINUE THE RIDE  "
		cont_btn.add_theme_font_size_override("font_size", 14)
		cont_btn.pressed.connect(_open_crawl)
		v.add_child(cont_btn)

	var back_btn := Button.new()
	back_btn.text = "  ← back to shelf  "
	back_btn.add_theme_font_size_override("font_size", 13)
	back_btn.pressed.connect(_on_back_to_shelf)
	v.add_child(back_btn)

	var rides: Array = _run_state.get("rides", [])
	if rides.size() > 0:
		var status := Label.new()
		status.text = "· rides finished: %d (%s) ·" % [rides.size(), ", ".join(rides)]
		status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		status.add_theme_font_size_override("font_size", 12)
		status.add_theme_color_override("font_color", C_BLOOD)
		v.add_child(status)


func _has_save() -> bool:
	return FileAccess.file_exists(SAVE_PATH) \
			and (_run_state.get("witches_dealt", {}) as Dictionary).size() > 0


func _on_back_to_shelf() -> void:
	quit_to_shelf.emit()


# ─── The crawl ───────────────────────────────────────────────────

func _open_crawl() -> void:
	_clear_current_scene()
	_child_scene = load(CRAWL_SCENE).instantiate()
	_child_scene.quit.connect(_on_crawl_quit)
	_child_scene.crawl_event.connect(_on_crawl_event)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_crawl_quit() -> void:
	if _child_scene != null and _child_scene.get("_state") != null:
		_run_state = _child_scene.get("_state")
		_run_state["addr"] = _child_scene.get("_addr")
	_save_state()
	_build_title_screen()


func _on_crawl_event(kind: String, state: Dictionary) -> void:
	_run_state = state
	_save_state()
	match kind:
		"witch":
			_show_witch(String(_run_state.get("_witch", "")))
		"home":
			_show_home()


# ─── The seats ───────────────────────────────────────────────────

func _find_witch(wid: String) -> Dictionary:
	for w in _witches.get("witches", []):
		if String((w as Dictionary)["id"]) == wid:
			return w
	return {}


func _show_witch(wid: String) -> void:
	var w := _find_witch(wid)
	if w.is_empty():
		_open_crawl()
		return
	var dealt: Dictionary = _run_state.get("witches_dealt", {})
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/sw/sister_%s.wav" % wid)

	_beat_root = Control.new()
	_beat_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_beat_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_beat_root)

	var bg := ColorRect.new()
	bg.color = C_INK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_beat_root.add_child(bg)

	# The seat itself — paperback cover art above the dealing.
	var seat_hero := HeroImage.new()
	if seat_hero.load_from(HERO_DIR + "seat_%s.json" % wid):
		var seat_rect := TextureRect.new()
		seat_rect.texture = seat_hero.texture(Vector2i(480, 216))
		seat_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		seat_rect.offset_left = -240
		seat_rect.offset_right = 240
		seat_rect.offset_top = -330
		seat_rect.offset_bottom = -114
		seat_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_beat_root.add_child(seat_rect)

	# The sister herself, standing beside the dealing.
	var sister_rect := TextureRect.new()
	sister_rect.texture = FIGURE_ART.sister(wid, Vector2i(84, 132))
	sister_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	sister_rect.offset_left = -560
	sister_rect.offset_right = -476
	sister_rect.offset_top = -110
	sister_rect.offset_bottom = 22
	sister_rect.stretch_mode = TextureRect.STRETCH_KEEP
	sister_rect.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_beat_root.add_child(sister_rect)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -420
	v.offset_right = 420
	v.offset_top = -100
	v.offset_bottom = 280
	v.add_theme_constant_override("separation", 14)
	_beat_root.add_child(v)

	var hdr := Label.new()
	hdr.text = "· %s ·" % String(w.get("name", ""))
	hdr.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hdr.add_theme_font_size_override("font_size", 20)
	hdr.add_theme_color_override("font_color", C_WYRD)
	v.add_child(hdr)

	if dealt.has(wid):
		var quiet := Label.new()
		quiet.text = "her seat is quiet. the weather here is just weather now. you dealt this thread · %s." % String(dealt[wid])
		quiet.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		quiet.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		quiet.add_theme_font_size_override("font_size", 15)
		quiet.add_theme_color_override("font_color", C_BONE)
		v.add_child(quiet)
		var back := Button.new()
		back.text = "  · ride on ·  "
		back.add_theme_font_size_override("font_size", 14)
		back.pressed.connect(_open_crawl)
		v.add_child(back)
		return

	var body := Label.new()
	body.text = String(w.get("arrival", ""))
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.add_theme_font_size_override("font_size", 15)
	body.add_theme_color_override("font_color", C_BONE)
	v.add_child(body)

	var lore: int = int(_run_state.get("lore", 0))
	var silver: int = int(_run_state.get("silver", 0))
	var need: int = int(w.get("unweave_lore", 4))

	var parley := Button.new()
	parley.text = "  PARLEY · she asks: %s  " % String(w.get("parley_price", ""))
	parley.add_theme_font_size_override("font_size", 14)
	parley.pressed.connect(_deal.bind(wid, "parley"))
	v.add_child(parley)

	var draw_b := Button.new()
	draw_b.text = "  DRAW · iron and silver (needs 2 SILVER · costs GRIT either way)  "
	draw_b.add_theme_font_size_override("font_size", 14)
	draw_b.disabled = silver < 2
	draw_b.pressed.connect(_deal.bind(wid, "draw"))
	v.add_child(draw_b)

	var unweave := Button.new()
	unweave.text = "  UNWEAVE · (needs %d LORE · you carry %d)  " % [need, lore]
	unweave.add_theme_font_size_override("font_size", 14)
	unweave.disabled = lore < need
	unweave.pressed.connect(_deal.bind(wid, "unweave"))
	v.add_child(unweave)

	var leave := Button.new()
	leave.text = "  · not yet · ride out ·  "
	leave.flat = true
	leave.add_theme_font_size_override("font_size", 13)
	leave.add_theme_color_override("font_color", C_SILVER)
	leave.pressed.connect(func() -> void:
		_show_beat_text(String(w.get("refuse_text", "")), _open_crawl))
	v.add_child(leave)


func _deal(wid: String, how: String) -> void:
	var w := _find_witch(wid)
	var dealt: Dictionary = _run_state.get("witches_dealt", {})
	var text := ""
	match how:
		"parley":
			text = String(w.get("parley_text", ""))
			if wid == "south":
				_run_state["no_southwest"] = true
		"draw":
			text = String(w.get("draw_text", ""))
			_run_state["silver"] = maxi(0, int(_run_state.get("silver", 0)) - 2)
			_run_state["grit"] = maxi(1, int(_run_state.get("grit", 6)) - 2)
		"unweave":
			text = String(w.get("unweave_text", ""))
	dealt[wid] = how
	_run_state["witches_dealt"] = dealt
	_save_state()
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null:
		sb.play("win_chord" if how == "unweave" else ("hurt" if how == "draw" else "coin"), 0.6)
	_show_beat_text(text, _open_crawl)


func _show_beat_text(text: String, then: Callable) -> void:
	_clear_current_scene()
	_beat_root = Control.new()
	_beat_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_beat_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_beat_root)
	var bg := ColorRect.new()
	bg.color = C_INK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_beat_root.add_child(bg)
	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -400
	v.offset_right = 400
	v.offset_top = -140
	v.offset_bottom = 160
	v.add_theme_constant_override("separation", 16)
	_beat_root.add_child(v)
	var body := Label.new()
	body.text = text
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.add_theme_font_size_override("font_size", 15)
	body.add_theme_color_override("font_color", C_BONE)
	v.add_child(body)
	var go := Button.new()
	go.text = "  · · ·  "
	go.add_theme_font_size_override("font_size", 14)
	go.pressed.connect(then)
	v.add_child(go)


# ─── Home · the loom or the iron ─────────────────────────────────

func _show_home() -> void:
	var dealt: Dictionary = _run_state.get("witches_dealt", {})
	var all_unwoven: bool = dealt.size() == 4
	for wid in dealt.keys():
		if String(dealt[wid]) != "unweave":
			all_unwoven = false
	_clear_current_scene()
	var loom: Dictionary = _witches.get("loom", {})

	if all_unwoven:
		_play_bgm("res://assets/audio/bgm/sw/loom.wav")
		_run_state["eighth_point_seen"] = true
		_show_ending(String(loom.get("gate_line", "")) + "\n\n" + String(loom.get("text", "")),
				"the_loom", true)
	else:
		_play_bgm("res://assets/audio/bgm/sw/territory.wav")
		var kept := "%d of 4 sisters dealt with · the rest keep their weather." % dealt.size()
		_show_ending(String(loom.get("hang_up_text", "")) + "\n\n" + kept, "home_hex", false)


func _show_ending(text: String, hero_name: String, true_end: bool) -> void:
	_beat_root = Control.new()
	_beat_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_beat_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_beat_root)

	var bg := ColorRect.new()
	bg.color = C_INK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_beat_root.add_child(bg)

	var hero := HeroImage.new()
	if hero.load_from(HERO_DIR + hero_name + ".json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(640, 360))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -320
		tex_rect.offset_right = 320
		tex_rect.offset_top = -310
		tex_rect.offset_bottom = 50
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_beat_root.add_child(tex_rect)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -400
	v.offset_right = 400
	v.offset_top = 70
	v.offset_bottom = 340
	v.add_theme_constant_override("separation", 14)
	_beat_root.add_child(v)

	var body := Label.new()
	body.text = text
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_theme_font_size_override("font_size", 14)
	body.add_theme_color_override("font_color", C_WYRD if true_end else C_BONE)
	v.add_child(body)

	var done := Button.new()
	done.text = "  · hang up the iron ·  "
	done.add_theme_font_size_override("font_size", 14)
	done.pressed.connect(func() -> void: _finish_run(true_end))
	v.add_child(done)

	# The porch is not a trap — with sisters still seated you can
	# always turn the horse around instead.
	if not true_end:
		var ride_on := Button.new()
		ride_on.text = "  · not yet · the territory keeps ·  "
		ride_on.flat = true
		ride_on.add_theme_font_size_override("font_size", 13)
		ride_on.add_theme_color_override("font_color", C_SILVER)
		ride_on.pressed.connect(_open_crawl)
		v.add_child(ride_on)


func _finish_run(true_end: bool) -> void:
	var dealt: Dictionary = _run_state.get("witches_dealt", {})
	var tokens: Array = _run_state.get("lore_tokens_pending", [])
	if not tokens.has("sisters_wyrd_finished"):
		tokens.append("sisters_wyrd_finished")
	if dealt.size() == 4 and not tokens.has("wyrd_all_four_unwoven") and true_end:
		tokens.append("wyrd_all_four_unwoven")
	if bool(_run_state.get("eighth_point_seen", false)) and not tokens.has("wyrd_eighth_point_seen"):
		tokens.append("wyrd_eighth_point_seen")
	_run_state["lore_tokens_pending"] = tokens
	OneironauticsTokens.add_many(tokens)
	var canon: Dictionary = _run_state.get("canon_vars", {})
	canon["wyrd_sisters_dealt"] = dealt.size()
	canon["wyrd_true_ending"] = true_end
	_run_state["canon_vars"] = canon
	var rides: Array = _run_state.get("rides", [])
	rides.append("the loom" if true_end else "%d/4" % dealt.size())
	_run_state["rides"] = rides
	_save_state()
	finished.emit(canon, tokens)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			if _title_root != null and _child_scene == null:
				_on_back_to_shelf()
				get_viewport().set_input_as_handled()
