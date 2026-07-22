extends Control
class_name SalmonberryYear
## SALMONBERRY · the year loop · the v1 core.
##
## Ten months, September 1963 to June 1964. Each month: a card (season,
## and for November and March the beat the town remembers), then a
## choice from the season's activities that spends the month — moving
## aptitudes, a bond, money, the book of the coast. No combat. The
## register at the end is who the town knows in June.
##
## March is special: the night the water comes, and what you built is
## what you can save.
##
## Emits (host contract): quit · month_complete(state) · year_over(result)
## F4-compliant via add_to_group("ui").

signal quit
signal month_complete(state: Dictionary)
signal year_over(result: Dictionary)

const ACTS_PATH := "res://resources/games/vol7/salmonberry/activities.json"
const NPCS_PATH := "res://resources/games/vol7/salmonberry/npcs.json"

const MONTHS := ["September", "October", "November", "December", "January",
	"February", "March", "April", "May", "June"]
const SEASON_LINE := [
	"The fog does not lift until noon. The whole town smells of fish and cut cedar. You are the new kid.",
	"The fall run is on. The cannery runs day and night and the gulls never sleep.",
	"On the twenty-second the radio said the President was shot. The line stopped for the afternoon. Nobody knew what to do with their hands.",
	"Rain like the sky forgot how to stop. The town pulls in close. Vovo bakes.",
	"The lowest tides of the year come at first light, in the cold. The flats belong to whoever will get up.",
	"Gray on gray. The storms line up off the point and come in one after another.",
	"",
	"The first green. The alders leaf out. The town is quieter than it was; the water took some of it.",
	"The salmonberry blooms pink along every draw. The days get long.",
	"School lets out. A little travelling show sets up on the cannery lot — a Ferris wheel, a fortune tent. The last month, and you know the town now.",
]

const C_SEA  := Color("3b5a6b")
const C_SAND := Color("b8a882")
const C_FOG  := Color("c8cec4")
const C_FIR  := Color("33452f")
const C_RUST := Color("9c5a3a")
const C_GOLD := Color("d8b048")
const C_INK  := Color("23282a")
const C_PANEL := Color(0.10, 0.11, 0.10, 0.90)

var _s: Dictionary = {}
var _acts: Array = []
var _journal_total: int = 12
var _npcs: Dictionary = {}     # id -> npc dict


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	_load_data()


func boot(state: Dictionary) -> void:
	_s = state
	# defensive defaults for older saves
	if not _s.has("apts"): _s["apts"] = {"hands": 0, "sea": 0, "word": 0, "heart": 0, "wild": 0, "grit": 0}
	if not _s.has("bonds"): _s["bonds"] = {}
	if not _s.has("journal"): _s["journal"] = []
	if not _s.has("thread_clues"): _s["thread_clues"] = []
	_render()


func _load_data() -> void:
	var a: Dictionary = _read_json(ACTS_PATH)
	_acts = a.get("activities", [])
	_journal_total = int(a.get("journal_total", 12))
	var n: Dictionary = _read_json(NPCS_PATH)
	for npc_v in n.get("npcs", []):
		var npc: Dictionary = npc_v
		_npcs[String(npc.get("id", ""))] = npc


func _read_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var f := FileAccess.open(path, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	return parsed if parsed is Dictionary else {}


# ─── render dispatch ─────────────────────────────────────────────

func _render() -> void:
	_clear_ui()
	_paint_backdrop()
	var month: int = int(_s.get("month", 0))
	if month >= MONTHS.size():
		_end_year()
	elif month == 6:
		_render_wave()
	else:
		_render_month()


func _clear_ui() -> void:
	for c in get_children():
		c.queue_free()


func _paint_backdrop() -> void:
	var sky := ColorRect.new()
	sky.color = C_FOG
	sky.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(sky)
	var sea := ColorRect.new()
	sea.color = C_SEA
	sea.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	sea.offset_top = -180
	add_child(sea)


func _panel() -> VBoxContainer:
	var pc := PanelContainer.new()
	pc.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	pc.offset_left = 80
	pc.offset_right = -80
	pc.offset_top = 40
	pc.offset_bottom = -40
	var sb := StyleBoxFlat.new()
	sb.bg_color = C_PANEL
	sb.set_corner_radius_all(4)
	sb.set_content_margin_all(20)
	pc.add_theme_stylebox_override("panel", sb)
	add_child(pc)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 10)
	pc.add_child(v)
	return v


# ─── the month ───────────────────────────────────────────────────

func _render_month() -> void:
	var month: int = int(_s.get("month", 0))
	var v := _panel()

	var hdr := Label.new()
	hdr.text = "%s %d" % [MONTHS[month], (1963 if month <= 3 else 1964)]
	hdr.add_theme_font_size_override("font_size", 26)
	hdr.add_theme_color_override("font_color", C_RUST)
	v.add_child(hdr)

	var season := Label.new()
	season.text = SEASON_LINE[month]
	season.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	season.add_theme_font_size_override("font_size", 15)
	season.add_theme_color_override("font_color", C_INK if month != 2 else C_RUST)
	v.add_child(season)

	v.add_child(_rule())
	v.add_child(_status_strip())
	v.add_child(_rule())

	var prompt := Label.new()
	prompt.text = "The month is yours. What do you do with it?"
	prompt.add_theme_font_size_override("font_size", 14)
	prompt.add_theme_color_override("font_color", C_GOLD)
	v.add_child(prompt)

	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	v.add_child(scroll)
	var list := VBoxContainer.new()
	list.add_theme_constant_override("separation", 6)
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(list)

	for act_v in _acts:
		var act: Dictionary = act_v
		if not _eligible(act, month):
			continue
		var b := Button.new()
		b.text = "  " + String(act.get("label", "?")) + _effect_hint(act)
		b.add_theme_font_size_override("font_size", 14)
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.pressed.connect(_on_activity.bind(act))
		list.add_child(b)

	var book := Button.new()
	book.text = "  · open the book of the coast ·  "
	book.add_theme_font_size_override("font_size", 12)
	book.add_theme_color_override("font_color", C_GOLD)
	book.pressed.connect(_show_book)
	v.add_child(book)

	var back := Button.new()
	back.text = "  · put it down for now (save & quit) ·  "
	back.add_theme_font_size_override("font_size", 12)
	back.pressed.connect(func() -> void: quit.emit())
	v.add_child(back)

	GamepadMgr.focus_first.call_deferred(scroll)


# ── the book of the coast · the collectible, read back ──
func _show_book() -> void:
	_sfx("page_turn")
	_clear_ui()
	_paint_backdrop()
	var v := _panel()
	var hdr := Label.new()
	hdr.text = "The Book of the Coast"
	hdr.add_theme_font_size_override("font_size", 24)
	hdr.add_theme_color_override("font_color", C_RUST)
	v.add_child(hdr)

	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	v.add_child(scroll)
	var list := VBoxContainer.new()
	list.add_theme_constant_override("separation", 8)
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(list)

	var journal: Array = _s.get("journal", [])
	var jh := Label.new()
	jh.text = "· what you noticed (%d of %d) ·" % [journal.size(), _journal_total]
	jh.add_theme_font_size_override("font_size", 14)
	jh.add_theme_color_override("font_color", C_GOLD)
	list.add_child(jh)
	if journal.is_empty():
		list.add_child(_book_line("The pages are still blank. Go and look at something.", C_FIR))
	for e in journal:
		list.add_child(_book_line("— " + String(e), C_INK))

	var clues: Array = _s.get("thread_clues", [])
	if not clues.is_empty():
		var ch := Label.new()
		ch.text = "· what you know ·"
		ch.add_theme_font_size_override("font_size", 14)
		ch.add_theme_color_override("font_color", C_GOLD)
		list.add_child(ch)
		for cid in clues:
			list.add_child(_book_line("— " + String(CLUE_TEXT.get(String(cid), "")), C_INK))

	var back := Button.new()
	back.text = "  · close the book ·  "
	back.add_theme_font_size_override("font_size", 14)
	back.pressed.connect(_render)
	v.add_child(back)
	GamepadMgr.focus_first.call_deferred(scroll)


func _book_line(text: String, col: Color) -> Label:
	var l := Label.new()
	l.text = text
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.add_theme_font_size_override("font_size", 14)
	l.add_theme_color_override("font_color", col)
	return l


func _eligible(act: Dictionary, month: int) -> bool:
	if act.has("months"):
		var ms: Array = act["months"]
		if not ms.has(month):
			return false
	# require: ALL of the listed conditions. require_any: at least ONE.
	if act.has("require") and not _req_met(act["require"]):
		return false
	if act.has("require_any"):
		var ok: bool = false
		for r_v in act["require_any"]:
			if _req_met(r_v):
				ok = true
				break
		if not ok:
			return false
	return true


func _req_met(req: Dictionary) -> bool:
	if req.has("apt") and _apt(String(req["apt"])) < int(req.get("min", 0)):
		return false
	if req.has("bond") and _bond(String(req["bond"])) < int(req.get("min", 0)):
		return false
	if req.has("money") and int(_s.get("money", 0)) < int(req.get("min", 0)):
		return false
	return true


func _effect_hint(act: Dictionary) -> String:
	var parts: PackedStringArray = PackedStringArray()
	var apts_d: Dictionary = act.get("apts", {})
	for k in apts_d.keys():
		parts.append("+%d %s" % [int(apts_d[k]), String(k)])
	if act.has("bond"):
		parts.append("+ " + _npc_name(String(act["bond"])))
	if int(act.get("money", 0)) > 0:
		parts.append("+$%d" % int(act["money"]))
	if act.has("journal"):
		parts.append("book")
	if bool(act.get("song", false)):
		parts.append("a song")
	if parts.is_empty():
		return ""
	return "   (" + ", ".join(parts) + ")"


# ─── resolve an activity ─────────────────────────────────────────

func _on_activity(act: Dictionary) -> void:
	_sfx(String(ACT_SFX.get(String(act.get("id", "")), "tile_enter")))
	var lines: Array = []
	# aptitudes
	var apts_d: Dictionary = act.get("apts", {})
	var apts: Dictionary = _s["apts"]
	for k in apts_d.keys():
		apts[String(k)] = int(apts.get(String(k), 0)) + int(apts_d[k])
	# money
	_s["money"] = int(_s.get("money", 0)) + int(act.get("money", 0))
	# bonds (up to two)
	if act.has("bond"):
		lines.append_array(_raise_bond(String(act["bond"]), int(act.get("bond_amt", 1))))
	if act.has("bond2"):
		lines.append_array(_raise_bond(String(act["bond2"]), int(act.get("bond2_amt", 1))))
	# song
	if bool(act.get("song", false)):
		_s["songs"] = int(_s.get("songs", 0)) + 1
	# a clue toward the boat that didn't come back
	if act.has("clue"):
		lines.append_array(_grant_clue(String(act["clue"])))
	# journal
	if act.has("journal"):
		var j: Array = _s["journal"]
		var entry: String = String(act["journal"])
		if not j.has(entry):
			j.append(entry)
			lines.append("· your book of the coast: \"%s\"" % entry)
			_sfx("page_turn")
	var outcome: String = String(act.get("outcome", ""))
	_advance_after(outcome, lines)


func _raise_bond(id: String, amt: int) -> Array:
	var bonds: Dictionary = _s["bonds"]
	var before: int = int(bonds.get(id, 0))
	var after: int = before + amt
	bonds[id] = after
	var out: Array = []
	var npc: Dictionary = _npcs.get(id, {})
	# crossing a threshold (2/4/6) surfaces the next bond line
	for i in range(3):
		var thresh: int = 2 + i * 2
		if before < thresh and after >= thresh:
			var bl: Array = npc.get("bond_lines", [])
			if i < bl.size():
				out.append("%s — %s" % [_npc_name(id), String(bl[i])])
	# a deep enough bond can turn up a clue about the boat
	for c_v in npc.get("clues", []):
		var c: Dictionary = c_v
		var at: int = int(c.get("at", 99))
		if before < at and after >= at:
			out.append_array(_grant_clue(String(c.get("id", ""))))
	return out


# ── the boat that didn't come back · the year's quiet thread ──
const CLUE_TEXT := {
	"estelle_light": "the boat · Estelle keeps a light in the window that faces the bar. Someone she loved went out on it, and did not come back.",
	"del_saw": "the boat · Del told you what he saw the morning it did not come in. He has never told anyone else.",
	"iris_record": "the boat · the county register has the crew, and a date, and after the date nothing at all.",
	"estelle_name": "the boat · Estelle said his name to you. Once. You are the only one she has told.",
}


func _grant_clue(id: String) -> Array:
	if id == "":
		return []
	var clues: Array = _s.get("thread_clues", [])
	if clues.has(id):
		return []
	clues.append(id)
	_s["thread_clues"] = clues
	_sfx("page_turn")
	return ["· " + String(CLUE_TEXT.get(id, "you learn something the town does not say."))]


func _thread_depth() -> int:
	return (_s.get("thread_clues", []) as Array).size()


func _advance_after(outcome: String, extra: Array) -> void:
	_clear_ui()
	_paint_backdrop()
	var v := _panel()
	var month: int = int(_s.get("month", 0))
	var h := Label.new()
	h.text = "%s %d" % [MONTHS[month], (1963 if month <= 3 else 1964)]
	h.add_theme_font_size_override("font_size", 20)
	h.add_theme_color_override("font_color", C_FIR)
	v.add_child(h)

	var o := Label.new()
	o.text = outcome
	o.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	o.add_theme_font_size_override("font_size", 16)
	o.add_theme_color_override("font_color", C_INK)
	v.add_child(o)

	for ln_v in extra:
		var ln := Label.new()
		ln.text = String(ln_v)
		ln.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		ln.add_theme_font_size_override("font_size", 14)
		ln.add_theme_color_override("font_color", C_GOLD)
		v.add_child(ln)

	v.add_child(_rule())
	v.add_child(_status_strip())

	# advance the month now (persist), then continue.
	_s["month"] = int(_s.get("month", 0)) + 1
	month_complete.emit(_s)
	_sfx("season_settle")

	var cont := Button.new()
	cont.text = "  the month passes  →  " if int(_s["month"]) < MONTHS.size() else "  the year ends  →  "
	cont.add_theme_font_size_override("font_size", 15)
	cont.pressed.connect(_render)
	v.add_child(cont)
	GamepadMgr.focus_first.call_deferred(v)


# ─── March · the water comes ─────────────────────────────────────

func _render_wave() -> void:
	_sfx("harbor_bell")
	var v := _panel()
	var hdr := Label.new()
	hdr.text = "March 1964 · Good Friday"
	hdr.add_theme_font_size_override("font_size", 26)
	hdr.add_theme_color_override("font_color", C_RUST)
	v.add_child(hdr)

	var body := Label.new()
	body.text = "At dinner the ground moves — a long slow roll, not a jolt — and does not stop. Del is out the door before it ends, yelling to bring the boats in. Then the harbormaster's bell, and the word goes house to house faster than the phone: the water has gone out. Too far out. It is coming back."
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.add_theme_font_size_override("font_size", 15)
	body.add_theme_color_override("font_color", C_INK)
	v.add_child(body)

	v.add_child(_rule())
	var prompt := Label.new()
	prompt.text = "You have a few minutes. What do you do with them?"
	prompt.add_theme_font_size_override("font_size", 14)
	prompt.add_theme_color_override("font_color", C_GOLD)
	v.add_child(prompt)

	# options gated by what you built
	if _apt("sea") >= 3 or _bond("del") >= 2:
		v.add_child(_wave_btn(
			"Run for the boats with Del",
			"You know the bar and Del knows you. You get lines cast off and the fleet stood off the bar in deep water, and it rides the surge instead of splintering on the pilings. Half the town's living, saved.",
			"del", 2, "sea", 2, true))
	if _bond("estelle") >= 2 or _apt("heart") >= 3:
		v.add_child(_wave_btn(
			"Get Estelle to high ground",
			"She will not leave the window that faces the bar. You take her hand and you say the thing only someone who has sat with her could say, and she comes. You are both on the hill when the water takes the gray house.",
			"estelle", 2, "heart", 2, true))
	# the thread pays off: if you have followed the boat, you know where
	# Estelle will be, and what she cannot be left alone with tonight.
	var clues: Array = _s.get("thread_clues", [])
	if _thread_depth() >= 2 and (clues.has("estelle_light") or clues.has("estelle_name")):
		var tb := Button.new()
		tb.text = "  Go straight to Estelle — you know now"
		tb.add_theme_font_size_override("font_size", 15)
		tb.alignment = HORIZONTAL_ALIGNMENT_LEFT
		tb.pressed.connect(func() -> void:
			_raise_bond("estelle", 3)
			var ap: Dictionary = _s["apts"]
			ap["heart"] = int(ap.get("heart", 0)) + 2
			_s["helped_wave"] = true
			_s["told_estelle"] = true
			_advance_after("You are already running before the bell finishes. She is at the window that faces the bar, the way she is every night, waiting the way she has waited a year. This time someone came for her. She lets you take her up the hill, and she does not look back at the water, she looks at you, and that is the thing the boat could not do and you could.", []))
		v.add_child(tb)

	v.add_child(_wave_btn(
		"Get yourself and Vovo up the hill",
		"You take Vovo's arm and you climb, and you watch from the top as the river walks up into the town and back out again, taking pieces. You are safe. That is also a choice, and not a small one.",
		"gran", 1, "grit", 1, false))

	GamepadMgr.focus_first.call_deferred(v)


func _wave_btn(label: String, result: String, bond_id: String, bond_amt: int,
		apt_name: String, apt_amt: int, helped: bool) -> Button:
	var b := Button.new()
	b.text = "  " + label
	b.add_theme_font_size_override("font_size", 15)
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.pressed.connect(func() -> void:
		_raise_bond(bond_id, bond_amt)
		var apts: Dictionary = _s["apts"]
		apts[apt_name] = int(apts.get(apt_name, 0)) + apt_amt
		if helped:
			_s["helped_wave"] = true
		_advance_after(result, []))
	return b


# ─── the year ends ───────────────────────────────────────────────

func _end_year() -> void:
	var register: String = _resolve_register()
	var coda: String = ""
	if bool(_s.get("helped_wave", false)):
		coda = "And the town remembers you were there the night the water came."
	else:
		coda = "The water came and went, and you were up the hill with Vovo, safe. That is a kind of choice too."
	# the boat thread pays off in the coda, by how far you followed it
	var depth: int = _thread_depth()
	if bool(_s.get("told_estelle", false)):
		coda += " You got to Estelle before the water did. Whatever the boat took from her, she did not have to face this one alone."
	elif depth >= 3:
		coda += " You know the whole of it now — the boat, the crew, the morning Del cannot forget. The town's quietest grief has one more keeper."
	elif depth >= 1:
		coda += " You know a little of what the town will not say aloud about the boat that did not come back."
	year_over.emit({"state": _s, "register": register, "coda": coda})


func _resolve_register() -> String:
	var a: Dictionary = _s["apts"]
	var gran: int = _bond("gran")
	var songs: int = int(_s.get("songs", 0))
	var journal_n: int = (_s["journal"] as Array).size()
	var deep: int = 0
	var town: int = 0
	for id in (_s["bonds"] as Dictionary).keys():
		if String(id) == "gran":
			continue
		var lvl: int = int((_s["bonds"] as Dictionary)[id])
		if lvl >= 2:
			deep += 1
		if lvl >= 4:
			town += 1
	var heart_word: int = int(a.get("heart", 0)) + int(a.get("word", 0))
	var body_sum: int = int(a.get("hands", 0)) + int(a.get("sea", 0)) + int(a.get("grit", 0))
	if gran >= 6 and songs >= 3:
		return "song"
	if journal_n >= 9:
		return "keeper"
	if heart_word >= 10 and deep >= 3:
		return "listener"
	if body_sum >= 12 and town >= 2:
		return "hands"
	return "leaver"


# ─── helpers ─────────────────────────────────────────────────────

func _apt(name: String) -> int:
	return int((_s["apts"] as Dictionary).get(name, 0))


func _bond(id: String) -> int:
	return int((_s["bonds"] as Dictionary).get(id, 0))


func _npc_name(id: String) -> String:
	var npc: Dictionary = _npcs.get(id, {})
	return String(npc.get("name", id.capitalize()))


func _rule() -> ColorRect:
	var r := ColorRect.new()
	r.color = Color(C_GOLD.r, C_GOLD.g, C_GOLD.b, 0.35)
	r.custom_minimum_size = Vector2(0, 1)
	return r


func _status_strip() -> Label:
	var a: Dictionary = _s["apts"]
	var l := Label.new()
	l.text = "hands %d · sea %d · word %d · heart %d · wild %d · grit %d      $%d · book %d/%d · month %d/10" % [
		int(a.get("hands", 0)), int(a.get("sea", 0)), int(a.get("word", 0)),
		int(a.get("heart", 0)), int(a.get("wild", 0)), int(a.get("grit", 0)),
		int(_s.get("money", 0)), (_s["journal"] as Array).size(), _journal_total,
		mini(int(_s.get("month", 0)) + 1, 10)]
	l.add_theme_font_size_override("font_size", 13)
	l.add_theme_color_override("font_color", C_FIR)
	return l


func _sfx(preset: String) -> void:
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null and sb.has_method("play"):
		sb.play(preset)


# Which ambient one-shot an activity earns, by id. Reuses the shared bank.
const ACT_SFX := {
	"walk_the_beach": "gull_cry",
	"clamming": "water_slap",
	"storm_watch": "wave_break",
	"row_the_bay": "water_slap",
	"cannery_line": "cooler_whoosh",
	"berry_picking": "gull_cry",
	"cafe_dishes": "customer_bell",
	"store_errand": "door_open",
}


func _input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		quit.emit()
		get_viewport().set_input_as_handled()
