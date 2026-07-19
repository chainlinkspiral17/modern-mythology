extends Control
## KWIK STOP MANAGER · one week · summer 1998, Highway 101.
##
## Estuary 1 with the score attached · that is the whole schism
## in one sentence, and this scene is the sentence.  Where
## Oneironautics hides every number, KSM posts them: cash, stock,
## morale, landlord, and THE SCORE, big, top-right, recalculated
## while you watch.
##
## A week: read the note · set the crew (three slots) · order
## stock · run it.  Rent falls on 4/8/12.  Staff events pull
## people's lives across the counter.  Week 8 is week 8, and it
## cannot be prevented; the design is what you do after.

signal quit
signal week_over(state: Dictionary)
signal summer_over(state: Dictionary)

const STAFF_PATH := "res://resources/games/vol7/kwik_stop_manager/staff.json"
const WEEKS_PATH := "res://resources/games/vol7/kwik_stop_manager/weeks.json"

const C_CREAM := Color("f4f0e8")
const C_RED   := Color("c8442c")
const C_DARK  := Color("2a3038")
const C_GOLD  := Color("f0c040")
const C_SAGE  := Color("6a7a72")
const C_SKY   := Color("8898a8")

const STOCK_UNIT_COST := 30
const STOCK_UNIT_REVENUE := 55

var _staff: Array = []
var _weeks: Dictionary = {}
var _state: Dictionary = {}
var _week: Dictionary = {}
var _n: int = 1
var _phase: String = "plan"     # plan · event · report · robbery
var _picked: Array = []          # staff ids on this week's crew

var _hdr: Label = null
var _score_lbl: Label = null
var _note_lbl: Label = null
var _body: RichTextLabel = null
var _crew_col: VBoxContainer = null
var _stock_row: HBoxContainer = null
var _go_btn: Button = null
var _stock_order: int = 0
var _stock_lbl: Label = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_load_data()
	_build_ui()


func boot(state: Dictionary) -> void:
	_state = state
	_n = clampi(int(_state.get("week_n", 1)), 1, 12)
	_week = (_weeks.get("weeks", []))[_n - 1]
	# One repave week per summer · rolled once, weeks 3-7, never
	# colliding with week 8.  Persists through the save like
	# everything else in _state.
	if not _state.has("repave_week"):
		_state["repave_week"] = 3 + int(randi() % 5)
	_phase = "plan"
	_picked = (_state.get("last_crew", []) as Array).duplicate()
	_stock_order = 0
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("request_scene_bgm"):
		am.request_scene_bgm("res://assets/audio/bgm/ksm/%s.wav" % ("week_after" if _n == 9 else "highway_summer"))
	_render_plan()


func _load_data() -> void:
	for pair in [[STAFF_PATH, "s"], [WEEKS_PATH, "w"]]:
		var f := FileAccess.open(String(pair[0]), FileAccess.READ)
		if f == null: continue
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			if String(pair[1]) == "s": _staff = (parsed as Dictionary).get("staff", [])
			else: _weeks = parsed


func _find_staff(sid: String) -> Dictionary:
	for s in _staff:
		if String((s as Dictionary)["id"]) == sid:
			return s
	return {}


# ─── UI ──────────────────────────────────────────────────────────

func _build_ui() -> void:
	var bg := ColorRect.new()
	bg.color = C_CREAM
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	var band := ColorRect.new()
	band.color = C_RED
	band.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	band.offset_bottom = 44
	add_child(band)

	_hdr = Label.new()
	_hdr.position = Vector2(20, 10)
	_hdr.add_theme_font_size_override("font_size", 16)
	_hdr.add_theme_color_override("font_color", C_CREAM)
	add_child(_hdr)

	# THE SCORE · big · top right · the whole argument
	_score_lbl = Label.new()
	_score_lbl.position = Vector2(980, 4)
	_score_lbl.add_theme_font_size_override("font_size", 26)
	_score_lbl.add_theme_color_override("font_color", C_GOLD)
	add_child(_score_lbl)

	_note_lbl = Label.new()
	_note_lbl.position = Vector2(20, 58)
	_note_lbl.size = Vector2(1240, 44)
	_note_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_note_lbl.add_theme_font_size_override("font_size", 14)
	_note_lbl.add_theme_color_override("font_color", C_DARK)
	add_child(_note_lbl)

	_crew_col = VBoxContainer.new()
	_crew_col.position = Vector2(20, 120)
	_crew_col.size = Vector2(560, 520)
	_crew_col.add_theme_constant_override("separation", 4)
	add_child(_crew_col)

	_body = RichTextLabel.new()
	_body.bbcode_enabled = true
	_body.position = Vector2(610, 120)
	_body.size = Vector2(650, 480)
	_body.add_theme_font_size_override("normal_font_size", 14)
	_body.add_theme_color_override("default_color", C_DARK)
	add_child(_body)

	_stock_row = HBoxContainer.new()
	_stock_row.position = Vector2(20, 648)
	_stock_row.size = Vector2(700, 34)
	_stock_row.add_theme_constant_override("separation", 10)
	add_child(_stock_row)

	var minus := Button.new()
	minus.text = " − "
	minus.pressed.connect(func() -> void:
		_stock_order = maxi(0, _stock_order - 1)
		_refresh_numbers())
	_stock_row.add_child(minus)

	_stock_lbl = Label.new()
	_stock_lbl.add_theme_font_size_override("font_size", 14)
	_stock_lbl.add_theme_color_override("font_color", C_DARK)
	_stock_row.add_child(_stock_lbl)

	var plus := Button.new()
	plus.text = " + "
	plus.pressed.connect(func() -> void:
		if _cash() >= (_stock_order + 1) * STOCK_UNIT_COST:
			_stock_order += 1
			_refresh_numbers())
	_stock_row.add_child(plus)

	_go_btn = Button.new()
	_go_btn.text = "  RUN THE WEEK  "
	_go_btn.position = Vector2(1040, 644)
	_go_btn.add_theme_font_size_override("font_size", 15)
	_go_btn.pressed.connect(_advance)
	add_child(_go_btn)


func _cash() -> int:
	return int(_state.get("cash", 300))


func _score() -> int:
	# The score is loud and simple on purpose · RANCH's kind of honest.
	return _cash() + int(_state.get("morale", 5)) * 40 \
			+ int(_state.get("landlord", 5)) * 25 + int(_state.get("stock", 5)) * 10


func _refresh_numbers() -> void:
	_hdr.text = "KWIK STOP · HWY 101 · WEEK %d OF 12 · SUMMER 1998      CASH $%d · STOCK %d · MORALE %d · LANDLORD %d" % [
		_n, _cash(), int(_state.get("stock", 5)), int(_state.get("morale", 5)), int(_state.get("landlord", 5))]
	_score_lbl.text = "SCORE %d" % _score()
	_stock_lbl.text = "order stock · %d units · $%d   (sell @ $%d · shelf max 12)" % [
		_stock_order, _stock_order * STOCK_UNIT_COST, STOCK_UNIT_REVENUE]


# ─── Plan phase ──────────────────────────────────────────────────

func _render_plan() -> void:
	_phase = "plan"
	_refresh_numbers()
	_note_lbl.text = "· %s" % String(_week.get("note", ""))
	_body.clear()
	_body.append_text("[b]THE WEEK AHEAD[/b]\n\ntraffic forecast · ×%.1f\n%s\n\npick a crew of three. skill runs the register. wages come out saturday. the score watches everything, because this is the game where the score is allowed to.\n" % [
		float(_week.get("traffic", 1.0)),
		"[color=#c8442c]RENT DUE THIS WEEK · $" + str(int(_weeks.get("rent", 220))) + "[/color]" if _n in _weeks.get("rent_weeks", []) else "rent is not due this week."])
	if _n == int(_state.get("repave_week", -1)):
		_body.append_text("\n[color=#c8442c]· COUNTY REPAVE THIS WEEK · flaggers either side of the lot, traffic thinned to a crawl · but a road crew eats where it works. guaranteed lunch-counter money.[/color]\n")
	_render_crew_picker()
	_go_btn.visible = true
	_stock_row.visible = true


func _render_crew_picker() -> void:
	for c in _crew_col.get_children():
		c.queue_free()
	var hdr := Label.new()
	hdr.text = "· THE CREW · pick 3 · (everyone has a life · the schedule is where you find out)"
	hdr.add_theme_font_size_override("font_size", 13)
	hdr.add_theme_color_override("font_color", C_RED)
	_crew_col.add_child(hdr)
	for s_v in _staff:
		var s: Dictionary = s_v
		var sid := String(s["id"])
		var quit_staff: Array = _state.get("staff_gone", [])
		if quit_staff.has(sid):
			continue
		var b := CheckBox.new()
		b.text = "%s · $%d/wk · skill ×%.1f · %s" % [String(s["name"]), int(s["wage"]),
				float(s["skill"]), String(s["life"])]
		b.button_pressed = _picked.has(sid)
		b.add_theme_font_size_override("font_size", 13)
		b.toggled.connect(func(on: bool) -> void:
			if on and _picked.size() < 3 and not _picked.has(sid):
				_picked.append(sid)
			elif not on:
				_picked.erase(sid)
			_render_crew_picker())
		if not _picked.has(sid) and _picked.size() >= 3:
			b.disabled = true
		_crew_col.add_child(b)


# ─── Run the week ────────────────────────────────────────────────

func _advance() -> void:
	match _phase:
		"plan":
			if _picked.size() != 3:
				_note_lbl.text = "· three on the crew. the counter has three shifts' worth of summer in it."
				return
			_run_week()
		"event", "report":
			_finish_week()
		"robbery":
			pass


func _run_week() -> void:
	_phase = "report"
	_go_btn.text = "  NEXT WEEK  "
	_stock_row.visible = false
	for c in _crew_col.get_children():
		c.queue_free()
	_state["last_crew"] = _picked.duplicate()

	var cash: int = _cash()
	var stock: int = mini(12, int(_state.get("stock", 5)) + _stock_order)
	cash -= _stock_order * STOCK_UNIT_COST
	var traffic: float = float(_week.get("traffic", 1.0))
	var repave: bool = _n == int(_state.get("repave_week", -1))
	if repave:
		traffic *= 0.55
	var skill := 0.0
	var wages := 0
	for sid in _picked:
		var s := _find_staff(String(sid))
		skill += float(s.get("skill", 1.0))
		wages += int(s.get("wage", 50))
	var morale: int = int(_state.get("morale", 5))
	var demand := int(round(4.0 * traffic * (skill / 3.0) * (0.8 + 0.05 * morale)))
	var sold: int = mini(stock, demand)
	var revenue: int = sold * STOCK_UNIT_REVENUE
	stock -= sold
	cash += revenue - wages

	var lines: Array = []
	lines.append("[b]THE LEDGER · WEEK %d[/b]\n" % _n)
	lines.append("stock in · %d units (−$%d)" % [_stock_order, _stock_order * STOCK_UNIT_COST])
	lines.append("sold · %d of %d demanded · +$%d" % [sold, demand, revenue])
	lines.append("wages · −$%d (%s)" % [wages, ", ".join(_picked)])
	if repave:
		cash += 95
		lines.append("repave crew lunches · +$95 · eight men, five days, the same order by wednesday")
	if sold < demand:
		lines.append("[color=#c8442c]· empty shelves turned away $%d. the score saw.[/color]" % ((demand - sold) * STOCK_UNIT_REVENUE))
	var landlord: int = int(_state.get("landlord", 5))
	if _n in _weeks.get("rent_weeks", []):
		var rent: int = int(_weeks.get("rent", 220))
		cash -= rent
		lines.append("rent · −$%d · mr. aldous counts the lot before he comes in." % rent)
		landlord += 1 if cash > 0 else -2

	_state["cash"] = cash
	_state["stock"] = stock
	_state["landlord"] = clampi(landlord, 0, 9)

	# a staff life crosses the counter
	var event_text := ""
	for sid in _picked:
		var s := _find_staff(String(sid))
		if int(s.get("event_week", -1)) == _n and not (_state.get("events_done", []) as Array).has(String(sid)):
			var done: Array = _state.get("events_done", [])
			done.append(String(sid))
			_state["events_done"] = done
			event_text = String(s.get("event", ""))
			_show_staff_event(s, lines, event_text)
			return

	# week 8 · it cannot be prevented
	if bool(_week.get("robbery", false)):
		_show_robbery(lines)
		return

	if bool(_week.get("heron", false)):
		var heron := String(_weeks.get("heron_line", ""))
		if OneironauticsTokens.has("estuary_1_finished"):
			heron += String(_weeks.get("heron_line_e1", ""))
		lines.append("\n[color=#6a7a72][i]%s[/i][/color]" % heron)

	_finish_report(lines)


func _show_staff_event(s: Dictionary, lines: Array, event_text: String) -> void:
	_phase = "event"
	_go_btn.visible = false
	lines.append("\n[b]· %s ·[/b]\n%s" % [String(s.get("name", "")), event_text])
	_body.clear()
	_body.append_text("\n".join(lines))
	var sid := String(s["id"])
	var cover := Button.new()
	cover.text = "  COVER FOR THEM · morale +2 · −$%d  " % int(s.get("wage", 50))
	cover.position = Vector2(640, 620)
	cover.add_theme_font_size_override("font_size", 14)
	cover.pressed.connect(func() -> void:
		_state["cash"] = _cash() - int(s.get("wage", 50))
		_state["morale"] = clampi(int(_state.get("morale", 5)) + 2, 0, 9)
		cover.queue_free()
		_clear_insist()
		_finish_report(["you cover the shift yourself. the crew clocks it. the ledger clocks it differently. both are the job."]))
	add_child(cover)
	_insist_btn = Button.new()
	_insist_btn.text = "  THEY WORK · morale −2  "
	_insist_btn.position = Vector2(640, 664)
	_insist_btn.add_theme_font_size_override("font_size", 14)
	_insist_btn.pressed.connect(func() -> void:
		_state["morale"] = clampi(int(_state.get("morale", 5)) - 2, 0, 9)
		if is_instance_valid(cover): cover.queue_free()
		_clear_insist()
		_finish_report(["they work the shift. the work is fine. something else isn't, and it stays on the schedule for weeks."]))
	add_child(_insist_btn)

var _insist_btn: Button = null

func _clear_insist() -> void:
	if _insist_btn != null and is_instance_valid(_insist_btn):
		_insist_btn.queue_free()
	_insist_btn = null


func _show_robbery(lines: Array) -> void:
	_phase = "robbery"
	_go_btn.visible = false
	var rob: Dictionary = _weeks.get("robbery", {})
	var witness := String(_picked[0]) if _picked.size() > 0 else "the crew"
	var wname := String(_find_staff(witness).get("name", witness))
	lines.append("\n[color=#c8442c][b]WEEK EIGHT.[/b][/color]\n%s\n\n%s" % [
		String(rob.get("text", "")), String(rob.get("witness_line", "")) % wname])
	_body.clear()
	_body.append_text("\n".join(lines))
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("loss_thud", 0.7)
	_state["cash"] = maxi(0, _cash() - 180)   # the till
	var y := 560.0
	for ch_v in rob.get("after_choices", []):
		var ch: Dictionary = ch_v
		var b := Button.new()
		b.text = "  %s  " % String(ch.get("label", ""))
		b.position = Vector2(640, y)
		b.add_theme_font_size_override("font_size", 14)
		b.pressed.connect(_resolve_robbery.bind(ch))
		add_child(b)
		y += 44.0


func _resolve_robbery(ch: Dictionary) -> void:
	for c in get_children():
		if c is Button and c != _go_btn:
			c.queue_free()
	_state["cash"] = _cash() + int(ch.get("cash", 0))
	_state["morale"] = clampi(int(_state.get("morale", 5)) + int(ch.get("morale", 0)), 0, 9)
	_state["landlord"] = clampi(int(_state.get("landlord", 5)) + int(ch.get("landlord", 0)), 0, 9)
	_state["robbery_choice"] = String(ch.get("id", ""))
	_finish_report([String(ch.get("text", ""))])


func _finish_report(lines: Array) -> void:
	_phase = "report"
	_go_btn.visible = true
	_go_btn.text = "  NEXT WEEK  " if _n < 12 else "  THE FALL REOPENING  "
	_refresh_numbers()
	_body.clear()
	_body.append_text("\n".join(lines))
	_body.append_text("\n\n[b]SCORE · %d[/b]   (cash + morale×40 + landlord×25 + stock×10 · the formula is printed in the manual. of course it is.)" % _score())


func _finish_week() -> void:
	if _n >= 12:
		summer_over.emit(_state)
		return
	_state["week_n"] = _n + 1
	week_over.emit(_state)


func _input(event: InputEvent) -> void:
	if not is_visible_in_tree():
		return
	if event is InputEventKey and event.pressed and not event.echo:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE and _phase in ["plan", "report"]:
			quit.emit()
			get_viewport().set_input_as_handled()
