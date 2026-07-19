extends Control
## THE PATIENT MISTER GLASS · one evening in the kitchen.
##
## One location, fourteen sessions.  The room is drawn once and
## lit fourteen ways — amber and steam early, colder and bluer as
## October leans in, evening 13 lit only by the stove.  Glass is
## always cooking; the menu is the calendar and it modulates
## candor.  Rain modulates memory.  Trust — built by which
## questions you DON'T press — modulates length.
##
## THE QUESTION DECK: twelve standing questions, any evening, and
## the same question returns rotations, not contradictions ·
## until it doesn't.
##
## THE LEDGER: pin any two heard answers against each other.  A
## true contradiction becomes a FINDING (there are nine).  A
## false pin costs trust · he saw you take the bait.
##
## Three questions cannot be asked cold.

signal quit
signal evening_over(state: Dictionary)

const DECK_PATH := "res://resources/games/vol7/patient_mister_glass/question_deck.json"
const HERO_DIR  := "res://resources/games/vol7/patient_mister_glass/hero_images/"

const C_DARK    := Color("100c0a")
const C_AMBER   := Color("e8a038")
const C_BROWN   := Color("6a4a30")
const C_OCTOBER := Color("8a98a8")
const C_RED     := Color("c8442c")
const C_CREAM   := Color("d8ccb8")
const C_WOOL    := Color("3a4438")

const QUESTIONS_PER_EVENING := 3

var _deck: Dictionary = {}
var _state: Dictionary = {}
var _evening: int = 1
var _asked_tonight: int = 0
var _rain_tonight: bool = false
var _evening_done: bool = false

var _tableau: TextureRect = null
var _glass_lbl: Label = null
var _answer_lbl: Label = null
var _status_lbl: Label = null
var _deck_col: VBoxContainer = null
var _ledger_btn: Button = null
var _end_btn: Button = null
var _ledger_overlay: Control = null
var _pin_first: Dictionary = {}


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_load_deck()
	_build_ui()


func boot(state: Dictionary) -> void:
	_state = state
	_evening = clampi(int(_state.get("evening_n", 1)), 1, 13)
	_asked_tonight = 0
	_evening_done = false
	var rains: Array = _state.get("rain_evenings", [])
	_rain_tonight = rains.has(_evening)
	_render_kitchen()
	_render_deck()
	_sfx("kettle_hiss", 0.5)
	if _rain_tonight:
		var am := get_node_or_null("/root/AudioMgr")
		if am != null and am.has_method("request_scene_bgm"):
			am.request_scene_bgm("res://assets/audio/bgm/pmg/rain_bed.wav")
	_set_answer(_arrival_line())
	# Evening 9, raining, and the player once stood the Sweetgum
	# watch: he volunteers one sentence, unprompted.
	if _evening == 9 and _rain_tonight and OneironauticsTokens.has("sweetgum_watch_stood"):
		_set_answer(String(_deck.get("evening_9_rain_watch_line", "")))


func _arrival_line() -> String:
	var cooking := _cooking()
	match cooking:
		"chowder": return "he lets you in without a word and goes back to the pot. chowder week. the chair by the table is yours now, apparently."
		"bread":   return "flour on the counter, the oven ticking. bread days. he nods at your chair. the timing of everything tonight belongs to the oven."
		_:         return "the kitchen smells of blackberries and pectin. jam. late october. he looks older in this light, or the light looks older on him."


func _cooking() -> String:
	return String(_deck.get("menu_by_evening", {}).get(str(_evening), "chowder"))


func _load_deck() -> void:
	if not FileAccess.file_exists(DECK_PATH): return
	var f := FileAccess.open(DECK_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_deck = parsed


# ─── UI ──────────────────────────────────────────────────────────

func _build_ui() -> void:
	var bg := ColorRect.new()
	bg.color = C_DARK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	_tableau = TextureRect.new()
	_tableau.stretch_mode = TextureRect.STRETCH_KEEP
	_tableau.position = Vector2(40, 16)
	_tableau.size = Vector2(768, 432)
	add_child(_tableau)

	_glass_lbl = Label.new()
	_glass_lbl.position = Vector2(52, 24)
	_glass_lbl.add_theme_font_size_override("font_size", 14)
	_glass_lbl.add_theme_color_override("font_color", C_OCTOBER)
	add_child(_glass_lbl)

	_answer_lbl = Label.new()
	_answer_lbl.position = Vector2(48, 462)
	_answer_lbl.size = Vector2(760, 210)
	_answer_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_answer_lbl.add_theme_font_size_override("font_size", 16)
	_answer_lbl.add_theme_color_override("font_color", C_CREAM)
	add_child(_answer_lbl)

	_status_lbl = Label.new()
	_status_lbl.position = Vector2(48, 686)
	_status_lbl.size = Vector2(760, 24)
	_status_lbl.add_theme_font_size_override("font_size", 13)
	_status_lbl.add_theme_color_override("font_color", C_BROWN)
	add_child(_status_lbl)

	# The question deck · right column
	var panel := ColorRect.new()
	panel.color = Color(C_DARK.r + 0.03, C_DARK.g + 0.02, C_DARK.b + 0.02)
	panel.position = Vector2(830, 16)
	panel.size = Vector2(430, 688)
	add_child(panel)

	var hdr := Label.new()
	hdr.text = "· THE QUESTION DECK ·"
	hdr.position = Vector2(850, 28)
	hdr.add_theme_font_size_override("font_size", 14)
	hdr.add_theme_color_override("font_color", C_AMBER)
	add_child(hdr)

	var scroll := ScrollContainer.new()
	scroll.position = Vector2(842, 56)
	scroll.size = Vector2(410, 560)
	add_child(scroll)

	_deck_col = VBoxContainer.new()
	_deck_col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_deck_col.add_theme_constant_override("separation", 6)
	scroll.add_child(_deck_col)

	_ledger_btn = Button.new()
	_ledger_btn.text = "  · OPEN THE LEDGER ·  "
	_ledger_btn.position = Vector2(842, 624)
	_ledger_btn.add_theme_font_size_override("font_size", 14)
	_ledger_btn.pressed.connect(_toggle_ledger)
	add_child(_ledger_btn)

	_end_btn = Button.new()
	_end_btn.text = "  · let him get back to his kitchen ·  "
	_end_btn.position = Vector2(842, 664)
	_end_btn.add_theme_font_size_override("font_size", 13)
	_end_btn.pressed.connect(_end_evening)
	add_child(_end_btn)


func _render_kitchen() -> void:
	var hero := HeroImage.new()
	var img := "kitchen_evening_13" if _evening >= 12 else "kitchen_evening_1"
	if hero.load_from(HERO_DIR + img + ".json"):
		_tableau.texture = hero.texture(Vector2i(768, 432))
	# October leans in · amber (1.0) → colder blue by evening 11
	var cold: float = clampf(float(_evening - 1) / 12.0, 0.0, 1.0)
	_tableau.modulate = Color(1.0 - cold * 0.18, 1.0 - cold * 0.10, 1.0 + cold * 0.08)
	var micro := ""
	if _evening > 6:
		micro = " · the cardigan buttons differently now"
	elif _evening > 3:
		micro = " · the reading glasses have migrated"
	_glass_lbl.text = "EVENING %d OF 14 · %s%s%s" % [
		_evening, _cooking().to_upper(),
		" · RAIN" if _rain_tonight else "", micro]


func _render_deck() -> void:
	for c in _deck_col.get_children():
		c.queue_free()
	var unlocked: Array = _state.get("unlocked_questions", [])
	for q_v in _deck.get("questions", []):
		var q: Dictionary = q_v
		var qid := String(q["id"])
		if bool(q.get("locked", false)) and not unlocked.has(qid):
			continue
		var b := Button.new()
		b.text = String(q.get("label", qid)) + ("  ⚷" if bool(q.get("locked", false)) else "")
		b.flat = true
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.add_theme_font_size_override("font_size", 14)
		b.add_theme_color_override("font_color", C_CREAM)
		b.add_theme_color_override("font_hover_color", C_AMBER)
		b.disabled = _asked_tonight >= QUESTIONS_PER_EVENING or _evening_done
		b.pressed.connect(_ask.bind(qid))
		_deck_col.add_child(b)
	_status_lbl.text = "questions tonight · %d of %d · trust · %s · findings · %d of 9" % [
		_asked_tonight, QUESTIONS_PER_EVENING, _trust_word(),
		(_state.get("findings", []) as Array).size()]


func _trust_word() -> String:
	var t: int = int(_state.get("trust", 5))
	if t >= 8: return "he leaves the pot to talk"
	if t >= 6: return "he talks while he cooks"
	if t >= 4: return "he answers"
	if t >= 2: return "he answers, shorter"
	return "he answers the door, at least"


# ─── Asking ──────────────────────────────────────────────────────

func _ask(qid: String) -> void:
	if _asked_tonight >= QUESTIONS_PER_EVENING or _evening_done:
		return
	var q := _find_question(qid)
	if q.is_empty():
		return
	_asked_tonight += 1
	_sfx("knife_board", 0.4)
	var heard: Array = _state.get("answers_heard", [])
	var heard_ids: Array = []
	for h in heard:
		heard_ids.append(String((h as Dictionary).get("variant", "")))
	var trust: int = int(_state.get("trust", 5))
	var picked: Dictionary = {}
	for v_v in q.get("variants", []):
		var v: Dictionary = v_v
		if heard_ids.has(String(v["id"])):
			continue
		if _variant_ok(v):
			picked = v
			break
	if picked.is_empty():
		# All heard · he repeats himself, softer.
		_set_answer("he gives you the answer he has already given, softer, watching to see if you noticed it was the same. you noticed.")
		_render_deck()
		return
	_set_answer(String(picked["text"]))
	heard.append({"variant": String(picked["id"]), "question": qid,
		"label": String(q.get("label", qid)), "evening": _evening,
		"text": String(picked["text"])})
	_state["answers_heard"] = heard
	# Hearing the envelopes answer IS seeing the second ledger.
	if String(picked["id"]) == "envelopes_1":
		OneironauticsTokens.add("glass_second_ledger_seen")
	_render_deck()


func _variant_ok(v: Dictionary) -> bool:
	var cond: Dictionary = v.get("cond", {})
	if cond.has("evening_min") and _evening < int(cond["evening_min"]): return false
	if cond.has("evening_max") and _evening > int(cond["evening_max"]): return false
	if cond.has("cooking") and String(cond["cooking"]) != _cooking(): return false
	if cond.has("rain") and bool(cond["rain"]) != _rain_tonight: return false
	if cond.has("trust_min") and int(_state.get("trust", 5)) < int(cond["trust_min"]): return false
	return true


func _find_question(qid: String) -> Dictionary:
	for q in _deck.get("questions", []):
		if String((q as Dictionary)["id"]) == qid:
			return q
	return {}


func _set_answer(text: String) -> void:
	_answer_lbl.text = text


# ─── The ledger · pin two answers ────────────────────────────────

func _toggle_ledger() -> void:
	if _ledger_overlay != null and is_instance_valid(_ledger_overlay):
		_ledger_overlay.queue_free()
		_ledger_overlay = null
		_pin_first = {}
		return
	_pin_first = {}
	_ledger_overlay = Panel.new()
	_ledger_overlay.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_ledger_overlay.offset_left = -480
	_ledger_overlay.offset_right = 480
	_ledger_overlay.offset_top = -300
	_ledger_overlay.offset_bottom = 300
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(C_DARK.r, C_DARK.g, C_DARK.b, 0.97)
	sb.border_color = C_RED
	sb.set_border_width_all(1)
	_ledger_overlay.add_theme_stylebox_override("panel", sb)
	add_child(_ledger_overlay)
	_rebuild_ledger()


func _rebuild_ledger() -> void:
	for c in _ledger_overlay.get_children():
		c.queue_free()
	var scroll := ScrollContainer.new()
	scroll.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scroll.offset_left = 16
	scroll.offset_right = -16
	scroll.offset_top = 16
	scroll.offset_bottom = -16
	_ledger_overlay.add_child(scroll)
	var col := VBoxContainer.new()
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col.add_theme_constant_override("separation", 8)
	scroll.add_child(col)

	var hdr := Label.new()
	hdr.text = "· THE LEDGER · pin two answers against each other ·" \
			+ ("   [first pin: %s, evening %d]" % [String(_pin_first.get("label", "")), int(_pin_first.get("evening", 0))] if not _pin_first.is_empty() else "")
	hdr.add_theme_font_size_override("font_size", 14)
	hdr.add_theme_color_override("font_color", C_RED)
	col.add_child(hdr)

	# Findings so far
	for fid in _state.get("findings", []):
		var f := _find_finding(String(fid))
		if f.is_empty(): continue
		var fl := Label.new()
		fl.text = "★ FINDING · %s — %s" % [String(f.get("title", "")), String(f.get("text", ""))]
		fl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		fl.custom_minimum_size = Vector2(900, 0)
		fl.add_theme_font_size_override("font_size", 13)
		fl.add_theme_color_override("font_color", C_AMBER)
		col.add_child(fl)

	for h_v in _state.get("answers_heard", []):
		var h: Dictionary = h_v
		var b := Button.new()
		b.text = "ev%d · %s · %s" % [int(h.get("evening", 0)), String(h.get("label", "")),
			String(h.get("text", "")).left(90) + "…"]
		b.flat = true
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.clip_text = true
		b.custom_minimum_size = Vector2(900, 0)
		b.add_theme_font_size_override("font_size", 13)
		b.add_theme_color_override("font_color", C_CREAM)
		b.add_theme_color_override("font_hover_color", C_RED)
		b.pressed.connect(_pin.bind(h))
		col.add_child(b)


func _pin(answer: Dictionary) -> void:
	if _pin_first.is_empty():
		_pin_first = answer
		_rebuild_ledger()
		return
	if String(_pin_first.get("variant", "")) == String(answer.get("variant", "")):
		_pin_first = {}
		_rebuild_ledger()
		return
	var pair := [String(_pin_first.get("variant", "")), String(answer.get("variant", ""))]
	pair.sort()
	var found: Dictionary = {}
	for f_v in _deck.get("findings", []):
		var f: Dictionary = f_v
		var fp: Array = (f.get("pair", []) as Array).duplicate()
		fp.sort()
		if fp == pair:
			found = f
			break
	_pin_first = {}
	if not found.is_empty():
		var fids: Array = _state.get("findings", [])
		if not fids.has(String(found["id"])):
			fids.append(String(found["id"]))
			_state["findings"] = fids
			var unlocks := String(found.get("unlocks", ""))
			if unlocks != "":
				var uq: Array = _state.get("unlocked_questions", [])
				if not uq.has(unlocks):
					uq.append(unlocks)
					_state["unlocked_questions"] = uq
			_sfx("page_turn", 0.7)
			_set_answer("FINDING · %s.  %s" % [String(found.get("title", "")), String(found.get("text", ""))])
		else:
			_set_answer("you have this finding already. the ledger doesn't mind being reread.")
	else:
		var t: int = int(_state.get("trust", 5))
		_state["trust"] = maxi(0, t - 1)
		_set_answer("you lay the two answers side by side and they are the same story wearing different weather. across the kitchen, without turning around: 'find it?' he saw you take the bait.")
	_toggle_ledger()
	_render_deck()


func _find_finding(fid: String) -> Dictionary:
	for f in _deck.get("findings", []):
		if String((f as Dictionary)["id"]) == fid:
			return f
	return {}


# ─── Evening's end ───────────────────────────────────────────────

func _end_evening() -> void:
	if _evening_done:
		return
	_evening_done = true
	# Restraint builds trust · two questions or fewer.
	if _asked_tonight <= 2:
		_state["trust"] = mini(10, int(_state.get("trust", 5)) + 1)
	# The silent evening · sit the whole evening and ask NOTHING.
	# Once, ever. The candor mechanic taken to its logical end:
	# the question you never ask is the one he answers.
	if _asked_tonight == 0 and not bool(_state.get("silent_evening_done", false)):
		_state["silent_evening_done"] = true
		_state["trust"] = mini(10, int(_state.get("trust", 5)) + 1)
		_set_answer("he cooks the whole evening without a word between you, and it is not uncomfortable, and that is the strange part. at the door, with your coat in your hand: 'my wife used to do that. sit there while i cooked. not asking.' he turns back to the stove. 'come again.'")
		OneironauticsTokens.add("pmg_silent_evening")
	evening_over.emit(_state)


func _sfx(preset: String, vol: float = 1.0) -> void:
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null and sb.has_method("play"):
		sb.play(preset, vol)


func _input(event: InputEvent) -> void:
	if not is_visible_in_tree():
		return
	if event is InputEventKey and event.pressed and not event.echo:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			if _ledger_overlay != null and is_instance_valid(_ledger_overlay):
				_toggle_ledger()
			else:
				quit.emit()
			get_viewport().set_input_as_handled()
		elif kev.keycode == KEY_L or kev.keycode == KEY_J:
			# J rides the pad's Y button (GamepadMgr) · same panel.
			_toggle_ledger()
